"""Werkzeuge der Agenten: Marktdaten, Orderbuch, Nachrichten, Portfolio, Orders, Notizbuch.

Jede Order wird mit Zeitstempel in decisions.jsonl geschrieben, BEVOR sie ausgeführt wird (Vorwärtstest).
Alle Modelle (Claude und Liga) bekommen exakt dieselben Werkzeuge."""
from __future__ import annotations

import json
import time
import uuid

from arena import funds, notizbuch, store
from arena.data import crypto, news, pm, stocks
from arena.exchange import engine, portfolio, risk
from arena.registry import Marktzugriff

MAX_AUSGABE = 3500


def _kurz(obj, n: int = MAX_AUSGABE) -> str:
    t = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, default=str)
    return t if len(t) <= n else t[:n] + " …(gekürzt)"


class Kontext:
    def __init__(self, defn: dict, pf: dict, snap: dict, mz: Marktzugriff, grund: str, ereignisse: list[dict],
                 jetzt: float | None = None):
        self.defn, self.pf, self.snap, self.mz = defn, pf, snap, mz
        self.grund, self.ereignisse = grund, ereignisse
        self.jetzt = jetzt or time.time()
        self.prof = funds.risikoprofil(defn)
        self.fid = defn["id"]
        self.orders = 0
        self.prognosen = 0

    # ---------------------------------------------------------------- Auflösung
    def aufloesen(self, iid: str) -> dict | None:
        try:
            if iid.startswith("spot:"):
                sym = iid.split(":", 1)[1].removesuffix("-USD")
                return crypto.spot_inst(sym) if crypto.spot_ticker(sym) else None
            if iid.startswith("perp:"):
                name = iid.split(":", 1)[1]
                return crypto.perp_inst(name) if crypto.perp_ticker(name) else None
            if iid.startswith("opt:"):
                name = iid.split(":", 1)[1]
                return crypto.option_inst(name) if crypto.parse_option(name) else None
            if iid.startswith("stock:"):
                return stocks.inst(iid.split(":", 1)[1])
            if iid.startswith("pm:"):
                _, venue, rest = iid.split(":", 2)
                ident, erg = rest.rsplit(":", 1)
                if erg not in ("JA", "NEIN"):
                    return None
                mid = f"pm:{venue}:{ident}"
                m = self.snap["pm_index"].get(mid) or pm.einzelmarkt(venue, ident)
                if m:
                    self.snap["pm_index"][mid] = m
                    return pm.inst(m, erg)
        except Exception:
            return None
        return None

    # ---------------------------------------------------------------- Werkzeuge
    def t_portfolio(self, **_) -> str:
        marks = {p["inst"]["id"]: self.mz.marke(p["inst"]) for p in self.pf["positionen"]}
        eq = portfolio.equity(self.pf, marks)
        pos = []
        for p in self.pf["positionen"]:
            m = marks[p["inst"]["id"]]
            wert = portfolio.pos_wert(p, m.get("bid"), m.get("mark"))
            pos.append({"position_id": p["id"], "instrument": p["inst"]["id"], "beschreibung": p["inst"].get("frage") or p["inst"].get("symbol"),
                        "seite": p["seite"], "menge": round(p["menge"], 6), "einstand": round(p["einstand"], 5),
                        "hebel": p.get("hebel", 1), "liquidationspreis": p.get("liq_preis"),
                        "wert_liquidation_usd": round(wert, 2), "stop_loss": p.get("stop_loss"), "take_profit": p.get("take_profit"),
                        "ausstiegsplan": p.get("ausstiegsplan"), "schliesst": p["inst"].get("schliesst"),
                        "funding_gezahlt": round(p.get("funding", 0), 2)})
        return _kurz({"eigenkapital_usd": round(eq, 2), "cash_usd": round(self.pf["cash"], 2),
                      "start_usd": round(self.pf["start_kapital"], 2), "rendite_pct": round((eq / self.pf["start_kapital"] - 1) * 100, 2),
                      "gebuehren_gesamt_usd": round(self.pf["gebuehren"], 2), "limits": self.prof, "positionen": pos})

    def t_markt_suche(self, abfrage: str, plattform: str = "alle", **_) -> str:
        kw = news.stichworte(abfrage) or {abfrage.lower()}
        treffer = []
        for m in self.snap["wetten"]:
            if plattform not in ("alle", m["venue"]):
                continue
            if kw & news.stichworte(m["frage"]):
                treffer.append(m)
        if plattform in ("alle", "polymarket"):
            treffer += [m for m in _sicher(pm.polymarket_suche, abfrage) if m["mid"] not in {t["mid"] for t in treffer}]
        if plattform in ("alle", "manifold"):
            treffer += [m for m in _sicher(pm.manifold_suche, abfrage) if m["mid"] not in {t["mid"] for t in treffer}]
        for m in treffer:
            self.snap["pm_index"].setdefault(m["mid"], m)
        treffer.sort(key=lambda m: -m.get("volumen_24h", 0))
        return _kurz([{"id": m["mid"], "venue": m["venue"], "frage": m["frage"], "ja_bid": m["ja_bid"], "ja_ask": m["ja_ask"],
                       "schliesst_in_tagen": round((m["schliesst"] - self.jetzt) / 86400, 1) if m.get("schliesst") else None,
                       "umsatz_24h": m.get("volumen_24h")} for m in treffer[:12]]) if treffer else "Keine Treffer."

    def t_markt_details(self, markt_id: str, **_) -> str:
        m = self.snap["pm_index"].get(markt_id)
        if not m:
            _, venue, ident = markt_id.split(":", 2)
            m = pm.einzelmarkt(venue, ident)
        if not m:
            return "Markt nicht gefunden."
        return _kurz({k: m.get(k) for k in ("mid", "venue", "frage", "ja_bid", "ja_ask", "volumen_24h", "liquiditaet", "url", "beschreibung")}
                     | {"schliesst": m.get("schliesst")})

    def t_orderbuch(self, instrument_id: str, **_) -> str:
        inst = self.aufloesen(instrument_id)
        if not inst:
            return f"Unbekanntes Instrument {instrument_id}."
        b, idx = self.mz.buch(inst)
        if b is None or (not b.bids and not b.asks):
            return "Kein Orderbuch verfügbar (Markt geschlossen oder Quelle gestört)."
        return _kurz({"instrument": instrument_id, "bids": [(round(p, 6), round(s, 4)) for p, s in b.bids[:10]],
                      "asks": [(round(p, 6), round(s, 4)) for p, s in b.asks[:10]], "mark": b.mark, "indexpreis": idx})

    def t_kurs_verlauf(self, instrument_id: str, **_) -> str:
        serie = self.snap.get("verlauf", {}).get(instrument_id)
        if serie:
            pts = serie[:: max(1, len(serie) // 24)]
            return _kurz([(int(t), p) for t, p in pts])
        if instrument_id.startswith("spot:"):
            k = crypto.spot_kerzen(instrument_id.split(":", 1)[1], 3600, 72)
            return _kurz([(int(c[0]), c[4]) for c in k[::3]])
        return "Kein gespeicherter Verlauf."

    def t_optionen(self, basis: str = "BTC", **_) -> str:
        o = crypto.optionen_universum(basis.upper(), 12)
        return _kurz([{"id": x["inst"]["id"], "strike": x["inst"]["strike"], "typ": x["inst"]["typ"], "tage": x["tage"],
                       "bid_usd": round(x["bid"], 1), "ask_usd": round(x["ask"], 1), "iv": x["iv"], "oi": x["oi"], "index": x["index"]} for x in o])

    def t_nachrichten(self, abfrage: str, **_) -> str:
        res = news.suche(abfrage, self.snap.get("nachrichten", []), 8)
        extra = news.gdelt(abfrage, 6)
        return _kurz([{"quelle": n["quelle"], "titel": n["titel"], "url": n["url"]} for n in res + extra]) or "Keine Treffer."

    def t_lage(self, **_) -> str:
        from arena.data import lage
        return _kurz(lage.lagebild())

    def t_prognose(self, instrument_id: str, horizont_stunden: int = 24, **_) -> str:
        from arena import forecast
        return _kurz(forecast.prognose(instrument_id, int(horizont_stunden), self.snap))

    def t_makro(self, **_) -> str:
        from arena.data import makro
        return _kurz(makro.uebersicht())

    def t_notizbuch_schreiben(self, typ: str, text: str, **_) -> str:
        notizbuch.schreibe(self.fid, typ, text, ts=self.jetzt)
        return "Notiz gespeichert."

    def t_wahrscheinlichkeit(self, markt_id: str, p_ja: float, begruendung: str, **_) -> str:
        """Eigene Wahrscheinlichkeitsschätzung festhalten (Grundlage für den Brier-Score), auch ohne Handel."""
        if self.prognosen >= 25:
            return "Limit erreicht (25 Schätzungen je Runde)."
        if not 0.0 <= float(p_ja) <= 1.0:
            return "p_ja muss zwischen 0 und 1 liegen."
        m = self.snap["pm_index"].get(markt_id)
        self.prognosen += 1
        store.anhaengen(f"funds/{self.fid}/prognosen.jsonl", {
            "ts": self.jetzt, "markt_id": markt_id, "p_ja": float(p_ja), "markt_ja_mitte": ((m["ja_bid"] + m["ja_ask"]) / 2) if m else None,
            "begruendung": begruendung[:600]})
        return "Schätzung gespeichert."

    def t_order(self, instrument_id: str, aktion: str, begruendung: str, zuversicht: float, betrag_usd: float | None = None,
                menge: float | None = None, seite: str = "long", hebel: float = 1, stop_loss: float | None = None,
                take_profit: float | None = None, ausstiegsplan: str = "", wahrscheinlichkeit_ja: float | None = None,
                **_) -> str:
        if self.orders >= 8:
            return "Limit erreicht: höchstens 8 Orders je Runde."
        import math
        for n_, w_ in (("zuversicht", zuversicht), ("betrag_usd", betrag_usd), ("menge", menge), ("hebel", hebel), ("stop_loss", stop_loss), ("take_profit", take_profit)):
            if w_ is not None and (not isinstance(w_, (int, float)) or not math.isfinite(w_)):
                return f"{n_} muss eine endliche Zahl sein."
        if aktion not in ("kaufen", "verkaufen"):
            return "aktion muss 'kaufen' oder 'verkaufen' sein."
        if len(begruendung.strip()) < 40:
            return "Begründung zu kurz (mind. 40 Zeichen) – nenne These, Gegenargument und Kosten."
        if not 0 <= float(zuversicht) <= 1:
            return "zuversicht muss zwischen 0 und 1 liegen."
        if aktion == "kaufen" and (len(ausstiegsplan.strip()) < 10):
            return "Zum Kaufen ist ein Ausstiegsplan Pflicht (wann/warum raus, Stop-Loss/Take-Profit)."
        inst = self.aufloesen(instrument_id)
        if not inst:
            return f"Unbekanntes Instrument {instrument_id}."
        did = "d" + uuid.uuid4().hex[:8]
        # 1) Entscheidung mit Zeitstempel VOR dem Ergebnis festhalten
        entscheidung = {"typ": "order", "id": did, "ts": time.time(), "fonds_id": self.fid, "instrument": instrument_id,
                        "aktion": aktion, "seite": seite, "betrag_usd": betrag_usd, "menge": menge, "hebel": hebel,
                        "stop_loss": stop_loss, "take_profit": take_profit, "begruendung": begruendung,
                        "zuversicht": zuversicht, "ausstiegsplan": ausstiegsplan, "wahrscheinlichkeit_ja": wahrscheinlichkeit_ja,
                        "grund_der_runde": self.grund}
        store.anhaengen(f"funds/{self.fid}/decisions.jsonl", entscheidung)
        self.orders += 1
        book, idx = self.mz.buch(inst)
        if book is None:
            return self._ergebnis(did, {"ok": False, "grund": "Kein Orderbuch/Kurs verfügbar"})
        if inst["art"] == "stock" and not book.asks and not book.bids:
            return self._ergebnis(did, {"ok": False, "grund": "Börse geschlossen"})
        if aktion == "kaufen":
            marks = {p["inst"]["id"]: self.mz.marke(p["inst"]) for p in self.pf["positionen"]}
            eq = portfolio.equity(self.pf, marks)
            if (betrag_usd is None) == (menge is None):
                return self._ergebnis(did, {"ok": False, "grund": "Genau eines von betrag_usd oder menge angeben"})
            r = engine.eroeffne(self.pf, self.prof, inst, book, seite=seite, qty=menge, usd=betrag_usd, hebel=float(hebel), equity=eq,
                                stop_loss=stop_loss, take_profit=take_profit, ausstiegsplan=ausstiegsplan, entscheidung_id=did,
                                ts=time.time(), index_preis=idx)
            if r.get("ok") and wahrscheinlichkeit_ja is not None and inst["art"] == "pm":
                m = self.snap["pm_index"].get(inst["id"].rsplit(":", 1)[0])
                store.anhaengen(f"funds/{self.fid}/prognosen.jsonl", {
                    "ts": time.time(), "markt_id": inst["id"].rsplit(":", 1)[0], "p_ja": float(wahrscheinlichkeit_ja),
                    "markt_ja_mitte": ((m["ja_bid"] + m["ja_ask"]) / 2) if m else None, "begruendung": "mit Order " + did})
        else:
            pos = next((p for p in self.pf["positionen"] if p["inst"]["id"] == inst["id"]), None)
            if not pos:
                return self._ergebnis(did, {"ok": False, "grund": "Keine offene Position in diesem Instrument"})
            r = engine.schliesse(self.pf, pos, book, qty=menge, grund=f"Agent: {begruendung[:80]}", ts=time.time(), index_preis=idx)
        return self._ergebnis(did, r)

    def _ergebnis(self, did: str, r: dict) -> str:
        r = {**r, "entscheidung_id": did}
        store.anhaengen(f"funds/{self.fid}/ledger.jsonl", r)
        funds.speichere_portfolio(self.pf)
        return _kurz(r)

    # ---------------------------------------------------------------- Beschreibung für die Modelle
    def definitionen(self) -> list[dict]:
        def s(props: dict, req: list[str]) -> dict:
            return {"type": "object", "properties": props, "required": req}
        str_, num_ = {"type": "string"}, {"type": "number"}
        return [
            {"name": "portfolio", "beschreibung": "Dein Portfolio: Eigenkapital, Cash, offene Positionen mit Wert, Stops, Ausstiegsplänen und deine Limits.",
             "schema": s({}, []), "fn": self.t_portfolio},
            {"name": "markt_suche", "beschreibung": "Sucht Wettmärkte (Polymarket, Kalshi, PredictIt, Manifold) nach Stichworten. Liefert IDs wie pm:polymarket:123.",
             "schema": s({"abfrage": str_, "plattform": {"type": "string", "enum": ["alle", "polymarket", "kalshi", "predictit", "manifold"]}}, ["abfrage"]), "fn": self.t_markt_suche},
            {"name": "markt_details", "beschreibung": "Regeln/Beschreibung und Daten eines Wettmarkts (Abrechnungsbedingungen genau lesen!).",
             "schema": s({"markt_id": str_}, ["markt_id"]), "fn": self.t_markt_details},
            {"name": "orderbuch", "beschreibung": "Echte Orderbuchtiefe (10 Stufen). Instrument-IDs: spot:BTC-USD, perp:BTC_USDC-PERPETUAL, opt:BTC-27NOV26-73000-P, stock:SPY, pm:polymarket:123:JA (oder :NEIN).",
             "schema": s({"instrument_id": str_}, ["instrument_id"]), "fn": self.t_orderbuch},
            {"name": "kurs_verlauf", "beschreibung": "Gespeicherter Kursverlauf der letzten ~26 h (bzw. Stundenkerzen bei Spot).",
             "schema": s({"instrument_id": str_}, ["instrument_id"]), "fn": self.t_kurs_verlauf},
            {"name": "optionen", "beschreibung": "Liquide Deribit-Optionen (BTC/ETH) nahe am Geld. Nur Kaufen (Long) möglich.",
             "schema": s({"basis": {"type": "string", "enum": ["BTC", "ETH"]}}, []), "fn": self.t_optionen},
            {"name": "nachrichten", "beschreibung": "Sucht aktuelle Nachrichten/Reddit (RSS, GDELT) zu einem Thema.",
             "schema": s({"abfrage": str_}, ["abfrage"]), "fn": self.t_nachrichten},
            {"name": "lagebild", "beschreibung": "Lagedaten: Erdbeben (USGS), Katastrophenalarme (GDACS), Wetterwarnungen (NOAA).",
             "schema": s({}, []), "fn": self.t_lage},
            {"name": "makro", "beschreibung": "Makrodaten (Zinsen, VIX, Inflation u. a.) aus öffentlichen Quellen.",
             "schema": s({}, []), "fn": self.t_makro},
            {"name": "prognose", "beschreibung": "Zeitreihen-Prognose mit Unsicherheitsband für ein Krypto-/Aktien-Instrument (TimesFM/Kronos wenn verfügbar, sonst statistisches Verfahren). Nur ein Hinweis, kein Orakel.",
             "schema": s({"instrument_id": str_, "horizont_stunden": num_}, ["instrument_id"]), "fn": self.t_prognose},
            {"name": "wahrscheinlichkeit", "beschreibung": "Halte deine Wahrscheinlichkeit für JA eines Wettmarkts fest (auch ohne Handel). Wird später per Brier-Score gegen den Ausgang bewertet.",
             "schema": s({"markt_id": str_, "p_ja": num_, "begruendung": str_}, ["markt_id", "p_ja", "begruendung"]), "fn": self.t_wahrscheinlichkeit},
            {"name": "notizbuch_schreiben", "beschreibung": "Schreibe in dein Notizbuch (bleibt dir für künftige Runden erhalten): typ = these | lektion | beobachtung | regel.",
             "schema": s({"typ": {"type": "string", "enum": ["these", "lektion", "beobachtung", "regel"]}, "text": str_}, ["typ", "text"]), "fn": self.t_notizbuch_schreiben},
            {"name": "order", "beschreibung": "Order gegen das echte Orderbuch (Papierhandel). kaufen = Position eröffnen/aufstocken (bei Perps seite long|short, hebel), verkaufen = bestehende Position (ganz oder teilweise per menge) schließen. Gebühren, Spread, Tiefe und Slippage werden real abgezogen. Wettmärkte: kaufe JA- oder NEIN-Anteile (…:JA / …:NEIN).",
             "schema": s({"instrument_id": str_, "aktion": {"type": "string", "enum": ["kaufen", "verkaufen"]},
                          "begruendung": {"type": "string", "description": "These, stärkstes Gegenargument, Kostenrechnung"},
                          "zuversicht": {"type": "number", "description": "0..1"},
                          "betrag_usd": {"type": "number", "description": "Einsatz in USD (bei Perps: Nominal)"}, "menge": num_,
                          "seite": {"type": "string", "enum": ["long", "short"]}, "hebel": num_,
                          "stop_loss": {"type": "number", "description": "Preis des Instruments"}, "take_profit": num_,
                          "ausstiegsplan": str_, "wahrscheinlichkeit_ja": {"type": "number", "description": "Nur Wettmärkte: deine P(JA)"}},
                         ["instrument_id", "aktion", "begruendung", "zuversicht"]), "fn": self.t_order},
        ]

    def fuehre_aus(self, name: str, eingabe: dict) -> tuple[str, bool]:
        for d in self.definitionen():
            if d["name"] == name:
                try:
                    return d["fn"](**(eingabe or {})), False
                except TypeError as e:
                    return f"Ungültige Argumente: {e}", True
                except Exception as e:
                    return f"Fehler: {type(e).__name__}: {e}", True
        return f"Unbekanntes Werkzeug {name}", True


def _sicher(fn, *a):
    try:
        return fn(*a)
    except Exception:
        return []
