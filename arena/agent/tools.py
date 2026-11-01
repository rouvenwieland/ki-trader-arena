"""Werkzeuge der Agenten: Marktdaten, Orderbuch, Nachrichten, Portfolio, Orders, Notizbuch.

Jede Order wird mit Zeitstempel in decisions.jsonl geschrieben, BEVOR sie ausgeführt wird (Vorwärtstest).
Alle Modelle (Claude und Liga) bekommen exakt dieselben Werkzeuge."""
from __future__ import annotations

import json
import time
import uuid

from arena import funds, notizbuch, policy, store, themen
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
        self.rm_abgelehnt: set[str] = set()
        self.bud = None  # Budget (für den Risikomanager-Pass), setzt die Agentenschleife

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
                sym = iid.split(":", 1)[1]
                return stocks.inst(sym) if stocks.kurs(sym) else None  # jeder Ticker, den die Kursquelle kennt
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
                        "ausstiegsplan": p.get("ausstiegsplan"), "invalidierung": p.get("invalidierung"), "schliesst": p["inst"].get("schliesst"),
                        "funding_gezahlt": round(p.get("funding", 0), 2)})
        return _kurz({"eigenkapital_usd": round(eq, 2), "cash_usd": round(self.pf["cash"], 2),
                      "start_usd": round(self.pf["start_kapital"], 2), "rendite_pct": round((eq / self.pf["start_kapital"] - 1) * 100, 2),
                      "gebuehren_gesamt_usd": round(self.pf["gebuehren"], 2), "limits": self.prof,
                      "policy_sperren": policy.sperren(self.fid), "cluster": risk.cluster_stand(self.pf, self.prof, eq), "positionen": pos,
                      "offene_auftraege": [{"auftrag_id": a["id"], "instrument": a["inst"]["id"], "typ": a.get("typ", "eroeffnung"), "aktion": a["aktion"],
                                            "seite": a.get("seite"), "limit": a.get("limit_preis"), "stop": a.get("stop_preis"), "betrag_usd": a.get("betrag_usd"),
                                            "menge": a.get("menge"), "gueltig_bis": a["gueltig_bis"]} for a in self.pf.get("auftraege", [])],
                      "rebalancing_regel": {k: v["anteil"] for k, v in (self.pf.get("rebalancing") or {}).get("ziele", {}).items()} or None,
                      "us_boerse": "offen" if stocks.boerse_offen(self.jetzt) else "geschlossen"})

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

    def t_orderfluss(self, markt_id: str, **_) -> str:
        """Wer kauft was? Polymarket: Preisverlauf 1 Woche, letzte Trades nach Seite, große Orders, größte Halter, Open Interest.
        Kalshi: Taker-Volumen JA/NEIN und Preisweg. Sonst: gespeicherter Verlauf der Arena."""
        mid = markt_id.rsplit(":", 1)[0] if markt_id.endswith((":JA", ":NEIN")) else markt_id
        try:
            _, venue, ident = mid.split(":", 2)
        except ValueError:
            return "markt_id im Format pm:plattform:id angeben."
        m = self.snap["pm_index"].get(mid) or pm.einzelmarkt(venue, ident)
        if not m:
            return "Markt nicht gefunden."
        out = pm.polymarket_orderfluss(m["ref"]) if venue == "polymarket" else pm.kalshi_orderfluss(m["ref"]) if venue == "kalshi" else {}
        serie = self.snap.get("verlauf", {}).get(f"{mid}:JA")
        if serie:
            out["arena_verlauf_ja"] = [(int(t), p) for t, p in serie[:: max(1, len(serie) // 16)]]
        return _kurz(out or "Kein Orderfluss verfügbar.")

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
        if instrument_id.startswith("stock:"):
            t = stocks.tagesschluesse(instrument_id.split(":", 1)[1], "6mo")
            return _kurz({"tagesschluesse_usd": [(int(a), round(b, 4)) for a, b in t[-60:]]}) if t else "Kein Verlauf für diesen Ticker."
        return "Kein gespeicherter Verlauf."

    def t_optionen(self, basis: str = "BTC", **_) -> str:
        o = crypto.optionen_universum(basis.upper(), 12)
        return _kurz([{"id": x["inst"]["id"], "strike": x["inst"]["strike"], "typ": x["inst"]["typ"], "tage": x["tage"],
                       "bid_usd": round(x["bid"], 1), "ask_usd": round(x["ask"], 1), "iv": x["iv"], "oi": x["oi"], "index": x["index"]} for x in o])

    def t_wetter(self, markt_id: str = "", **_) -> str:
        """Temperatur-Wettmärkte (Kalshi): Ensemble-Wahrscheinlichkeit je Bracket gegen den Marktpreis. Ohne markt_id: offene Events auflisten."""
        from arena.data import wetter
        if not markt_id:
            return _kurz({"offene_events": wetter.offene_events(), "stationen": {k: v[0] for k, v in wetter.STATIONEN.items()},
                          "hinweis": "Mit markt_id (z. B. pm:kalshi:KXHIGHNY-26OCT31-B59.5 oder Event KXHIGHNY-26OCT31) die Analyse abrufen."})
        ticker = markt_id.split(":")[-1] if markt_id.startswith("pm:") else markt_id
        if ticker.endswith(("JA", "NEIN")) and markt_id.count(":") > 2:
            ticker = markt_id.split(":")[2]
        event = "-".join(ticker.split("-")[:2])
        return _kurz(wetter.analyse_event(event), 5000)

    def t_derivate_lage(self, basis: str = "BTC", **_) -> str:
        """Volatilitätsregime (DVOL), Funding (8-h-Mittel und letzte Stunden exakt), Basis-Kurve der Terminkontrakte, Open Interest."""
        b = basis.upper() if basis.upper() in ("BTC", "ETH", "SOL") else "BTC"
        perp = f"{b}_USDC-PERPETUAL"
        t = crypto.perp_ticker(perp) or {}
        jetzt = time.time()
        stunden = []
        for h in range(1, 7):
            w = crypto.funding_wert(perp, jetzt - h * 3600, jetzt - (h - 1) * 3600)
            if w is not None:
                stunden.append(round(w * 100, 5))
        return _kurz({"basis": b, "dvol": crypto.dvol(b) if b in ("BTC", "ETH") else "nur BTC/ETH",
                      "perp": {"mark": t.get("mark"), "index": t.get("index"), "funding_8h_pct": round(100 * t.get("funding_8h", 0), 5),
                               "funding_letzte_6h_pct_je_stunde": stunden, "open_interest": t.get("oi")},
                      "basis_kurve": crypto.basis_kurve(b) if b in ("BTC", "ETH") else [],
                      "hinweis": "Positive Basis/Funding = Long-Nachfrage (Hebel). Extreme sind Warnsignale für Gegenbewegungen, keine Garantie."})

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

    def t_positionsgroesse(self, instrument_id: str, p_ja: float | None = None, **_) -> str:
        """Größenempfehlung: Wetten per Kelly (inkl. Gebühr, simultan über offene Wetten, Profil-Bruchteil), sonst Volatilitätsziel (GARCH)."""
        from arena import forecast, risikoschicht
        inst = self.aufloesen(instrument_id)
        if not inst:
            return f"Unbekanntes Instrument {instrument_id}."
        marks = {p["inst"]["id"]: self.mz.marke(p["inst"]) for p in self.pf["positionen"]}
        eq = portfolio.equity(self.pf, marks)
        if inst["art"] == "pm":
            book, _ = self.mz.buch(inst)
            return _kurz(risikoschicht.wette(self.defn, self.pf, inst, book, None if p_ja is None else float(p_ja), eq))
        if inst["art"] == "option":
            return "Optionen: Prämie ist der Maximalverlust – Größe über risiko_usd und das Optionslimit des Profils wählen."
        basis = instrument_id if inst["art"] != "perp" else "spot:" + inst["symbol"].split("_")[0] + "-USD"
        return _kurz(risikoschicht.vol_ziel(self.defn, inst, eq, forecast.historie(basis, self.snap)) | {"limits": self.prof})

    def t_notizbuch_schreiben(self, typ: str, text: str, wichtigkeit: float | None = None, gueltig_tage: float | None = None, **_) -> str:
        try:
            notizbuch.schreibe(self.fid, typ, text, ts=self.jetzt, wichtigkeit=None if wichtigkeit is None else float(wichtigkeit),
                               gueltig_tage=None if not gueltig_tage else float(gueltig_tage))
        except (TypeError, ValueError):
            return "wichtigkeit (1–10) und gueltig_tage müssen Zahlen sein."
        return "Notiz gespeichert."

    def t_wahrscheinlichkeit(self, markt_id: str = "", p_ja: float | None = None, p_nein: float | None = None, p_blind: float | None = None,
                             basisrate: str = "", abrechnung: str = "", status_quo: str = "", gegenargument: str = "",
                             begruendung: str = "", ueberraschung: str = "", **_) -> str:
        """Eigene Wahrscheinlichkeitsschätzung mit Superforecaster-Gerüst festhalten (Grundlage für Brier-Score und Brier-Skill gegen den Markt)."""
        if self.prognosen >= 25:
            return "Limit erreicht (25 Schätzungen je Runde)."
        fehlt = [n for n, v in (("markt_id", markt_id), ("p_ja", p_ja), ("p_nein", p_nein), ("p_blind", p_blind), ("basisrate", basisrate),
                                ("abrechnung", abrechnung), ("status_quo", status_quo), ("gegenargument", gegenargument),
                                ("begruendung", begruendung)) if v in (None, "")]
        if fehlt:
            return "Pflichtfelder fehlen: " + ", ".join(fehlt) + ". Nutze das Gerüst: Abrechnung, Status quo, Basisrate, p_blind (ohne Marktpreis), dann p_ja und getrennt p_nein."
        try:
            pj, pn, pb = float(p_ja), float(p_nein), float(p_blind)
        except (TypeError, ValueError):
            return "p_ja, p_nein und p_blind müssen Zahlen zwischen 0 und 1 sein."
        if not all(0.0 <= x <= 1.0 for x in (pj, pn, pb)):
            return "p_ja, p_nein und p_blind müssen zwischen 0 und 1 liegen."
        if abs(pj + pn - 1) > 0.15:
            return (f"Inkohärent: p_ja {pj:.2f} + p_nein {pn:.2f} = {pj + pn:.2f}. Überdenke beide Seiten getrennt (Ja-Hang?) und gib sie neu an.")
        m = self.snap["pm_index"].get(markt_id)
        self.prognosen += 1
        store.anhaengen(f"funds/{self.fid}/prognosen.jsonl", {
            "ts": self.jetzt, "markt_id": markt_id, "p_ja": pj, "p_nein": pn, "p_blind": pb,
            "markt_ja_mitte": ((m["ja_bid"] + m["ja_ask"]) / 2) if m else None, "schliesst": m.get("schliesst") if m else None,
            "basisrate": str(basisrate)[:300], "abrechnung": str(abrechnung)[:300], "status_quo": str(status_quo)[:300],
            "gegenargument": str(gegenargument)[:300], "ueberraschung": str(ueberraschung)[:300], "begruendung": str(begruendung)[:600]})
        mitte = ((m["ja_bid"] + m["ja_ask"]) / 2) if m else None
        return "Schätzung gespeichert." + (f" Marktpreis JA ≈ {mitte:.2f}; deine Abweichung {100 * (pj - mitte):+.0f} pp." if mitte is not None else "")

    def t_order(self, instrument_id: str, aktion: str, begruendung: str, zuversicht: float, betrag_usd: float | None = None,
                menge: float | None = None, seite: str = "long", hebel: float = 1, stop_loss: float | None = None,
                take_profit: float | None = None, ausstiegsplan: str = "", wahrscheinlichkeit_ja: float | None = None,
                invalidierung: str = "", staerkstes_gegenargument: str = "", risiko_usd: float | None = None,
                gegenbegruendung: str = "", auftragsart: str = "markt", limit_preis: float | None = None, stop_preis: float | None = None,
                gueltigkeit: str = "tag", **_) -> str:
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
        if aktion == "kaufen":
            if len(ausstiegsplan.strip()) < 10:
                return "Zum Kaufen ist ein Ausstiegsplan Pflicht (wann/warum raus, Stop-Loss/Take-Profit)."
            fehlt = [n for n, v in (("invalidierung", invalidierung), ("staerkstes_gegenargument", staerkstes_gegenargument)) if len(str(v).strip()) < 10]
            if fehlt or risiko_usd is None or not isinstance(risiko_usd, (int, float)) or risiko_usd <= 0:
                return ("Pflichtfelder beim Kaufen: invalidierung (konkretes, beobachtbares Signal), staerkstes_gegenargument (ein Satz) und "
                        "risiko_usd (Verlust bis Stop bzw. bei Wetten bis 0, > 0). Fehlt/ungültig: " + ", ".join(fehlt + (["risiko_usd"] if not (isinstance(risiko_usd, (int, float)) and risiko_usd > 0) else [])))
            if float(zuversicht) < 0.4:
                return "Zuversicht unter 0,4 heißt laut Skala: kein Vorteil → nicht kaufen."
        inst = self.aufloesen(instrument_id)
        if not inst:
            return f"Unbekanntes Instrument {instrument_id}."
        if aktion == "kaufen" and inst["art"] == "pm" and (wahrscheinlichkeit_ja is None or not 0 <= float(wahrscheinlichkeit_ja) <= 1):
            return "Bei Wettmärkten ist wahrscheinlichkeit_ja (deine P(JA), 0..1) beim Kaufen Pflicht."
        if aktion == "kaufen":
            sperre = policy.gesperrt(self.fid, inst, seite)
            if sperre:
                return f"Policy-Sperre: Kategorie {sperre} ist nach deiner eigenen Bilanz für neue Käufe gesperrt (nur das Wochen-Review kann lockern)."
        did = "d" + uuid.uuid4().hex[:8]
        # 1) Entscheidung mit Zeitstempel VOR dem Ergebnis festhalten
        entscheidung = {"typ": "order", "id": did, "ts": time.time(), "fonds_id": self.fid, "instrument": instrument_id,
                        "aktion": aktion, "seite": seite, "betrag_usd": betrag_usd, "menge": menge, "hebel": hebel,
                        "stop_loss": stop_loss, "take_profit": take_profit, "begruendung": begruendung,
                        "zuversicht": zuversicht, "ausstiegsplan": ausstiegsplan, "wahrscheinlichkeit_ja": wahrscheinlichkeit_ja,
                        "invalidierung": invalidierung, "staerkstes_gegenargument": staerkstes_gegenargument, "risiko_usd": risiko_usd,
                        "thema": themen.thema(inst), "grund_der_runde": self.grund}
        store.anhaengen(f"funds/{self.fid}/decisions.jsonl", entscheidung)
        self.orders += 1
        book, idx = self.mz.buch(inst)
        if book is None:
            return self._ergebnis(did, {"ok": False, "grund": "Kein Orderbuch/Kurs verfügbar (Ticker prüfen – Suche mit aktien_suche)"})
        if aktion == "kaufen":
            marks = {p["inst"]["id"]: self.mz.marke(p["inst"]) for p in self.pf["positionen"]}
            eq = portfolio.equity(self.pf, marks)
            if (betrag_usd is None) == (menge is None):
                return self._ergebnis(did, {"ok": False, "grund": "Genau eines von betrag_usd oder menge angeben"})
            if self.defn.get("risikomanager"):
                betrag_usd, menge, abgelehnt = self._risikomanager(inst, book, eq, betrag_usd, menge, float(hebel), entscheidung, gegenbegruendung)
                if abgelehnt:
                    return self._ergebnis(did, {"ok": False, "grund": abgelehnt})
        art_auftrag = (auftragsart or "markt").lower()
        geschlossen = not book.asks and not book.bids
        if art_auftrag in ("limit", "stop") or (art_auftrag == "markt" and geschlossen and inst["art"] == "stock"):
            return self._bedingt(did, inst, aktion, "eroeffnung" if art_auftrag == "markt" else art_auftrag, book, seite=seite, betrag_usd=betrag_usd,
                                 menge=menge, hebel=float(hebel), limit_preis=limit_preis, stop_preis=stop_preis, gueltigkeit=gueltigkeit,
                                 stop_loss=stop_loss, take_profit=take_profit, ausstiegsplan=ausstiegsplan, invalidierung=invalidierung)
        if art_auftrag != "markt":
            return self._ergebnis(did, {"ok": False, "grund": "auftragsart muss markt, limit oder stop sein"})
        if aktion == "kaufen":
            r = engine.eroeffne(self.pf, self.prof, inst, book, seite=seite, qty=menge, usd=betrag_usd, hebel=float(hebel), equity=eq,
                                stop_loss=stop_loss, take_profit=take_profit, ausstiegsplan=ausstiegsplan, entscheidung_id=did,
                                ts=time.time(), index_preis=idx)
            if r.get("ok") and invalidierung:
                pos = next((p for p in self.pf["positionen"] if p["id"] == r["position_id"]), None)
                if pos is not None:
                    pos["invalidierung"] = invalidierung[:300]
            if r.get("ok") and wahrscheinlichkeit_ja is not None and inst["art"] == "pm":
                m = self.snap["pm_index"].get(inst["id"].rsplit(":", 1)[0])
                store.anhaengen(f"funds/{self.fid}/prognosen.jsonl", {
                    "ts": time.time(), "markt_id": inst["id"].rsplit(":", 1)[0], "p_ja": float(wahrscheinlichkeit_ja),
                    "markt_ja_mitte": ((m["ja_bid"] + m["ja_ask"]) / 2) if m else None, "schliesst": inst.get("schliesst"),
                    "begruendung": "mit Order " + did})
        else:
            pos = next((p for p in self.pf["positionen"] if p["inst"]["id"] == inst["id"]), None)
            if not pos:
                return self._ergebnis(did, {"ok": False, "grund": "Keine offene Position in diesem Instrument"})
            r = engine.schliesse(self.pf, pos, book, qty=menge, grund=f"Agent: {begruendung[:80]}", ts=time.time(), index_preis=idx)
        return self._ergebnis(did, r)

    def _risikomanager(self, inst, book, eq, betrag_usd, menge, hebel, entscheidung, gegenbegruendung):
        """A/B-Fonds: Haiku-Gegenprüfung großer Orders. Liefert (betrag, menge, Ablehnungsgrund oder None)."""
        from arena import risikomanager as rm
        preis = (book.asks[0][0] if book.asks else book.mark) or 0
        einsatz = (betrag_usd if betrag_usd is not None else (menge or 0) * preis) / (hebel if inst["art"] == "perp" else 1)
        if not rm.ist_gross(einsatz, eq, hebel, rm.thema_anteil_danach(self.pf, inst, einsatz, eq, self.prof)):
            return betrag_usd, menge, None
        if inst["id"] in self.rm_abgelehnt:
            if len(gegenbegruendung.strip()) >= 40:
                store.anhaengen(f"funds/{self.fid}/decisions.jsonl", {"typ": "risikomanager", "ts": time.time(), "instrument": inst["id"],
                                                                      "urteil": "übergangen", "grund": gegenbegruendung[:400]})
                return betrag_usd, menge, None
            return betrag_usd, menge, "Vom Risikomanager abgelehnt; erneut nur einmal mit gegenbegruendung (≥ 40 Zeichen) möglich."
        kontext = f"Eigenkapital {eq:.0f} USD, Cash {self.pf['cash']:.0f} USD, Positionen: " + ", ".join(
            f"{p['inst']['id']} {p['einstand'] * p['menge']:.0f} USD" for p in self.pf["positionen"]) + f"; Cluster: {risk.cluster_stand(self.pf, self.prof, eq)}"
        u = rm.pruefe(self.defn, {k: entscheidung.get(k) for k in ("instrument", "aktion", "seite", "betrag_usd", "menge", "hebel", "zuversicht",
                                                                   "wahrscheinlichkeit_ja", "begruendung", "invalidierung", "staerkstes_gegenargument", "risiko_usd")} |
                      {"einsatz_usd": round(einsatz, 2), "preis": preis}, kontext, getattr(self, "bud", None))
        if u["urteil"] == "ablehnen":
            self.rm_abgelehnt.add(inst["id"])
            return betrag_usd, menge, f"Risikomanager: abgelehnt – {u['grund']}"
        if u["urteil"] == "verkleinern":
            return (None if betrag_usd is None else betrag_usd * u["faktor"]), (None if menge is None else menge * u["faktor"]), None
        return betrag_usd, menge, None

    def _bedingt(self, did, inst, aktion, typ, book, **kw) -> str:
        """Limit-/Stop-Auftrag bzw. Markt-Auftrag zur Eröffnung (Börse zu) anlegen; ein sofort kreuzendes Limit wird gleich ausgeführt."""
        from arena import auftraege
        if typ == "limit" and not auftraege.gueltiger_preis(kw.get("limit_preis")):
            return self._ergebnis(did, {"ok": False, "grund": "Limit-Auftrag braucht limit_preis > 0 (Preis des Instruments in USD; Wetten 0..1)"})
        if typ == "stop" and not auftraege.gueltiger_preis(kw.get("stop_preis")):
            return self._ergebnis(did, {"ok": False, "grund": "Stop-Auftrag braucht stop_preis > 0"})
        if aktion == "verkaufen" and not any(p["inst"]["id"] == inst["id"] for p in self.pf["positionen"]):
            return self._ergebnis(did, {"ok": False, "grund": "Keine offene Position in diesem Instrument"})
        if len(self.pf.get("auftraege", [])) >= auftraege.MAX_OFFEN:
            return self._ergebnis(did, {"ok": False, "grund": f"Höchstens {auftraege.MAX_OFFEN} offene Aufträge – erst einen mit auftrag_loeschen entfernen"})
        vorlaeufig = {"typ": typ, "aktion": aktion, "seite": kw.get("seite", "long"), "inst": inst, "limit_preis": kw.get("limit_preis"),
                      "stop_preis": kw.get("stop_preis"), "menge": kw.get("menge")}
        kauf = auftraege.kaufseite(vorlaeufig, self.pf)
        if typ == "stop" and auftraege.sofort_ausfuehrbar(vorlaeufig, kauf, book):
            return self._ergebnis(did, {"ok": False, "grund": "Stop-Preis ist schon erreicht – nutze eine Marktorder"})
        a = auftraege.neu(self.pf, did, inst, aktion, typ, jetzt=time.time(), **kw)
        if typ == "limit" and auftraege.sofort_ausfuehrbar(a, kauf, book):
            fb, slip = auftraege.fuellbuch(a, kauf, book, None)
            self.pf["auftraege"] = [x for x in self.pf["auftraege"] if x["id"] != a["id"]]
            return self._ergebnis(did, {k: v for k, v in auftraege.ausfuehren(self.pf, self.prof, a, fb, slip, self.mz, time.time()).items()
                                        if k != "entscheidung_id"})
        from datetime import datetime, timezone
        bis = datetime.fromtimestamp(a["gueltig_bis"], timezone.utc).strftime("%d.%m. %H:%M UTC")
        text = {"eroeffnung": "Börse geschlossen – Auftrag zur Eröffnung vorgemerkt", "limit": f"Limit-Auftrag @ {a['limit_preis']} aktiv",
                "stop": f"Stop-Auftrag @ {a['stop_preis']} aktiv"}[typ]
        return self._ergebnis(did, {"ok": True, "aktion": "vorgemerkt", "auftrag_id": a["id"], "inst_id": inst["id"], "auftragstyp": typ,
                                    "grund": f"{text}, gültig bis {bis}; Ausführung im 15-min-Takt zum dann gültigen Kurs (Limits gelten dann)"})

    def t_technische_analyse(self, instrument_id: str, intervall: str = "tag", **_) -> str:
        """Indikatoren und Regime für Krypto, Perps (über den Spot-Basiswert), Aktien/ETFs weltweit und Wettmärkte (gespeicherter Verlauf)."""
        from arena import technik
        stunde = intervall == "stunde"
        if instrument_id.startswith(("spot:", "perp:", "opt:")):
            basis = instrument_id.split(":", 1)[1].split("-")[0].split("_")[0]
            k = crypto.spot_kerzen(f"{basis}-USD", 3600 if stunde else 86400, 300)
            kerzen = [(c[2], c[1], c[4], c[0]) for c in k]
            vgl = [c[4] for c in crypto.spot_kerzen("BTC-USD", 3600 if stunde else 86400, 300)] if basis != "BTC" else None
            pj = 8760 if stunde else 365
        elif instrument_id.startswith("stock:"):
            sym = instrument_id.split(":", 1)[1]
            kerzen = stocks.kerzen(sym, "1mo" if stunde else "2y", "60m" if stunde else "1d")
            vgl = [x[2] for x in stocks.kerzen("SPY", "1mo" if stunde else "2y", "60m" if stunde else "1d")] if sym.upper() != "SPY" else None
            pj = 252 * 6.5 if stunde else 252
        else:
            serie = self.snap.get("verlauf", {}).get(instrument_id) or []
            kerzen = [(p, p, p, t) for t, p in serie]
            vgl, pj = None, 4 * 24 * 365
        if vgl:
            vgl = vgl[-len(kerzen):]
        return _kurz(technik.analyse(kerzen, pj, vgl) | {"intervall": "Stunde" if stunde else "Tag",
                                                         "vergleich": "BTC" if instrument_id.startswith(("spot:", "perp:", "opt:")) else "SPY",
                                                         "hinweis": "Beschreibt die Vergangenheit; als Signal nur zusammen mit Kosten und Gegenargument nutzen."})

    def t_rebalancing_regel(self, ziele: list | None = None, schwelle_pp: float = 5.0, begruendung: str = "", **_) -> str:
        """Stehende Rebalancing-Regel setzen/ändern (leere Liste = entfernen); der Wächter handelt alle 15 min die Abweichung."""
        from arena import rebalancing
        did = "d" + uuid.uuid4().hex[:8]
        store.anhaengen(f"funds/{self.fid}/decisions.jsonl", {"typ": "rebalancing", "id": did, "ts": time.time(), "fonds_id": self.fid,
                                                             "ziele": ziele, "schwelle_pp": schwelle_pp, "begruendung": begruendung[:600]})
        try:
            t = rebalancing.setze(self.pf, list(ziele or []), schwelle_pp, did, self.jetzt, self.aufloesen)
        except (TypeError, ValueError, AttributeError) as e:
            return f"Ungültige Regel: {e}"
        funds.speichere_portfolio(self.pf)
        return t

    def t_optionskette(self, basis: str = "BTC", verfall: str = "", spanne_pct: float = 30, **_) -> str:
        """Komplette Deribit-Optionskette: ohne verfall die Laufzeiten, mit verfall alle Strikes mit Geld/Brief/Mark (USD), IV und Griechen."""
        return _kurz(crypto.optionskette(basis.upper() if basis.upper() in ("BTC", "ETH") else "BTC", verfall or None,
                                         max(0.02, min(1.0, float(spanne_pct) / 100))), 6000)

    def t_aktien_suche(self, abfrage: str, **_) -> str:
        """Ticker-Suche weltweit (Aktien, ETFs) – Ergebnis direkt als instrument_id nutzbar."""
        return _kurz(stocks.suche(abfrage, 10) or "Keine Treffer.")

    def t_aktie(self, instrument_id: str, **_) -> str:
        """Kurs (USD und Originalwährung), Börse, Handelszeit, Tagesveränderung, 1-Jahres-Spanne, Liquidität (Spread) eines Aktien-/ETF-Tickers."""
        sym = instrument_id.split(":", 1)[1] if instrument_id.startswith("stock:") else instrument_id
        k = stocks.kurs(sym)
        if not k:
            return f"Kein Kurs für {sym} (Ticker prüfen, z. B. mit aktien_suche)."
        tage = stocks.tagesschluesse(sym, "1y")
        vol, sigma = stocks.tagesvolumen_sigma(sym)
        z = [c for _, c in tage]
        return _kurz({"instrument_id": f"stock:{sym.upper()}", "kurs_usd": round(k["preis"], 4), "waehrung": k["waehrung"], "kurs_lokal": k["preis_lokal"],
                      "boerse": k["boerse"], "offen": k["offen"], "aenderung_pct": k["aenderung_pct"],
                      "spanne_1j_usd": [round(min(z), 2), round(max(z), 2)] if z else None,
                      "rendite_1j_pct": round((z[-1] / z[0] - 1) * 100, 1) if len(z) > 1 else None,
                      "tagesvolumen_usd": round(vol) if vol else None, "vola_tag_pct": round(100 * sigma, 2) if sigma else None,
                      "halber_spread_bp": round(stocks.halb_spread(vol) * 1e4, 1),
                      "naechste_eroeffnung": stocks.naechste_oeffnung_symbol(sym) if not k["offen"] else None})

    def t_auftrag_loeschen(self, auftrag_id: str, **_) -> str:
        vorher = len(self.pf.get("auftraege", []))
        self.pf["auftraege"] = [a for a in self.pf.get("auftraege", []) if a["id"] != auftrag_id]
        funds.speichere_portfolio(self.pf)
        return "Auftrag gelöscht." if len(self.pf["auftraege"]) < vorher else "Kein solcher Auftrag."

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
            {"name": "orderfluss", "beschreibung": "Orderfluss eines Wettmarkts: Preisverlauf, wer zuletzt JA/NEIN gekauft hat (Volumen, große Orders), größte Halter, Open Interest (Polymarket, Kalshi).",
             "schema": s({"markt_id": str_}, ["markt_id"]), "fn": self.t_orderfluss},
            {"name": "kurs_verlauf", "beschreibung": "Gespeicherter Kursverlauf der letzten ~26 h (bzw. Stundenkerzen bei Spot).",
             "schema": s({"instrument_id": str_}, ["instrument_id"]), "fn": self.t_kurs_verlauf},
            {"name": "optionen", "beschreibung": "Schnellüberblick: liquideste Deribit-Optionen (BTC/ETH) nahe am Geld. Volle Kette mit Griechen: „optionskette“. Kaufen (long) und Schreiben (order mit seite short und menge) möglich.",
             "schema": s({"basis": {"type": "string", "enum": ["BTC", "ETH"]}}, []), "fn": self.t_optionen},
            {"name": "wetter", "beschreibung": "Temperatur-Wettmärkte (Kalshi „Highest temperature in …“): Wahrscheinlichkeit je Bracket aus 82 Wetter-Ensemble-Mitgliedern (GFS+ECMWF, Open-Meteo) inkl. Modellfehler und bisher gemessenem Tagesmaximum, gegen den Marktpreis. Ohne markt_id: offene Events.",
             "schema": s({"markt_id": {"type": "string", "description": "Markt oder Event, z. B. pm:kalshi:KXHIGHNY-26OCT31-B59.5 oder KXHIGHNY-26OCT31"}}, []), "fn": self.t_wetter},
            {"name": "derivate_lage", "beschreibung": "Krypto-Derivate-Lage: Deribit-Volatilitätsindex DVOL (Regime), Funding (8-h-Mittel und exakt je Stunde), annualisierte Basis der Terminkontrakte, Open Interest.",
             "schema": s({"basis": {"type": "string", "enum": ["BTC", "ETH", "SOL"]}}, []), "fn": self.t_derivate_lage},
            {"name": "nachrichten", "beschreibung": "Sucht aktuelle Nachrichten/Reddit (RSS, GDELT) zu einem Thema.",
             "schema": s({"abfrage": str_}, ["abfrage"]), "fn": self.t_nachrichten},
            {"name": "lagebild", "beschreibung": "Lagedaten: Erdbeben (USGS), Katastrophenalarme (GDACS), Wetterwarnungen (NOAA).",
             "schema": s({}, []), "fn": self.t_lage},
            {"name": "makro", "beschreibung": "Makrodaten (Zinsen, VIX, Inflation u. a.) aus öffentlichen Quellen.",
             "schema": s({}, []), "fn": self.t_makro},
            {"name": "prognose", "beschreibung": "Zeitreihen-Prognose mit Unsicherheitsband für ein Krypto-/Aktien-Instrument (TimesFM/Kronos wenn verfügbar, sonst statistisches Verfahren). Nur ein Hinweis, kein Orakel.",
             "schema": s({"instrument_id": str_, "horizont_stunden": num_}, ["instrument_id"]), "fn": self.t_prognose},
            {"name": "wahrscheinlichkeit", "beschreibung": "Halte deine Wahrscheinlichkeit für einen Wettmarkt fest (auch ohne Handel), mit Superforecaster-Gerüst. Wird später per Brier-Score gegen den Ausgang UND gegen den damaligen Marktpreis bewertet.",
             "schema": s({"markt_id": str_, "abrechnung": {"type": "string", "description": "Abrechnungsquelle und -datum laut Regeln"},
                          "status_quo": {"type": "string", "description": "Ausgang, wenn sich nichts ändert"},
                          "basisrate": {"type": "string", "description": "Wie oft tritt so etwas grundsätzlich ein? Mit Herkunft"},
                          "ueberraschung": {"type": "string", "description": "Szenario, das dich widerlegen würde"},
                          "p_blind": {"type": "number", "description": "Deine P(JA) OHNE den Marktpreis zu berücksichtigen, 0..1"},
                          "p_ja": {"type": "number", "description": "Deine endgültige P(JA), 0..1"},
                          "p_nein": {"type": "number", "description": "Getrennt überlegt: P(NEIN), 0..1 (nicht einfach 1 − p_ja rechnen)"},
                          "gegenargument": {"type": "string", "description": "Stärkstes Argument gegen deine Schätzung"},
                          "begruendung": str_},
                         ["markt_id", "abrechnung", "status_quo", "basisrate", "p_blind", "p_ja", "p_nein", "gegenargument", "begruendung"]), "fn": self.t_wahrscheinlichkeit},
            {"name": "positionsgroesse", "beschreibung": "Größenempfehlung vor einer Order: Wettmärkte per Kelly inkl. Gebühr, gemeinsam mit deinen offenen Wetten optimiert, mal Bruchteil deines Profils (halbiert, wenn du bisher schlechter als der Markt geschätzt hast); Krypto/Perps/Aktien per Volatilitätsziel (GARCH) mit Stop-Vorschlag.",
             "schema": s({"instrument_id": str_, "p_ja": {"type": "number", "description": "Wettmärkte: deine P(JA); sonst deine letzte festgehaltene Schätzung"}}, ["instrument_id"]), "fn": self.t_positionsgroesse},
            {"name": "technische_analyse", "beschreibung": "Technische Analyse und Regime für jedes Instrument: SMA/EMA, RSI, MACD, Bollinger, ATR, realisierte Vola und Vola-Regime, Drawdown, Z-Score, Hurst-Exponent (Trend vs. Rückkehr zum Mittel), Autokorrelation, Beta/Korrelation zu BTC bzw. SPY.",
             "schema": s({"instrument_id": str_, "intervall": {"type": "string", "enum": ["tag", "stunde"]}}, ["instrument_id"]), "fn": self.t_technische_analyse},
            {"name": "rebalancing_regel", "beschreibung": "Stehende Rebalancing-Regel (z. B. Volatility Harvesting): Zielanteile am Vermögen für Krypto-Spot und Aktien/ETFs, Rest Cash. Der Wächter handelt alle 15 min die Abweichung, sobald sie die Schwelle übersteigt (echte Kosten). Leere Liste entfernt die Regel.",
             "schema": s({"ziele": {"type": "array", "items": {"type": "object", "properties": {"instrument_id": str_, "anteil": {"type": "number", "description": "0..1 des Vermögens"}},
                                                            "required": ["instrument_id", "anteil"]}},
                          "schwelle_pp": {"type": "number", "description": "Abweichung in Prozentpunkten, ab der gehandelt wird (min. 1, Standard 5)"},
                          "begruendung": str_}, ["ziele", "begruendung"]), "fn": self.t_rebalancing_regel},
            {"name": "optionskette", "beschreibung": "Komplette Deribit-Optionskette (BTC/ETH): ohne verfall alle Laufzeiten, mit verfall (z. B. 27NOV26) alle Strikes mit Geld/Brief/Mark in USD, IV, Delta, Vega, Theta, Open Interest – Grundlage für Spreads, Straddles, Covered Calls, Delta-Hedges.",
             "schema": s({"basis": {"type": "string", "enum": ["BTC", "ETH"]}, "verfall": str_, "spanne_pct": {"type": "number", "description": "Strikes ± so viel Prozent um den Kurs (Standard 30)"}}, []),
             "fn": self.t_optionskette},
            {"name": "aktien_suche", "beschreibung": "Sucht Aktien/ETFs weltweit nach Name oder Stichwort (Yahoo) und liefert handelbare IDs wie stock:RHM.DE.",
             "schema": s({"abfrage": str_}, ["abfrage"]), "fn": self.t_aktien_suche},
            {"name": "aktie", "beschreibung": "Details zu einem beliebigen Aktien-/ETF-Ticker: Kurs in USD und Originalwährung, Börse/Handelszeit, Tagesveränderung, 1-Jahres-Spanne, Volumen, Vola, Spread.",
             "schema": s({"instrument_id": str_}, ["instrument_id"]), "fn": self.t_aktie},
            {"name": "auftrag_loeschen", "beschreibung": "Löscht einen offenen Auftrag (Limit, Stop oder Eröffnung; IDs in „portfolio“).",
             "schema": s({"auftrag_id": str_}, ["auftrag_id"]), "fn": self.t_auftrag_loeschen},
            {"name": "notizbuch_schreiben", "beschreibung": "Schreibe in dein Notizbuch (bleibt dir für künftige Runden erhalten): typ = these | lektion | beobachtung | regel.",
             "schema": s({"typ": {"type": "string", "enum": ["these", "lektion", "beobachtung", "regel"]}, "text": str_,
                          "wichtigkeit": {"type": "number", "description": "1–10 (Standard: Beobachtung 3, These 5, Lektion 7, Regel 8); bestimmt, wie lange die Notiz vorgelegt wird"},
                          "gueltig_tage": {"type": "number", "description": "optional: nach so vielen Tagen nicht mehr vorlegen (z. B. These bis zur Abrechnung)"}},
                         ["typ", "text"]), "fn": self.t_notizbuch_schreiben},
            {"name": "order", "beschreibung": "Order gegen das echte Orderbuch (Papierhandel). kaufen = Position eröffnen/aufstocken (bei Perps seite long|short, hebel), verkaufen = bestehende Position (ganz oder teilweise per menge) schließen. Gebühren, Spread, Tiefe und Slippage werden real abgezogen. Wettmärkte: kaufe JA- oder NEIN-Anteile (…:JA / …:NEIN). Aktien/ETFs: stock:SYMBOL für JEDEN Yahoo-Ticker weltweit (z. B. stock:PLTR, stock:RHM.DE, stock:7203.T; Kurse in USD umgerechnet), long oder short (Leerverkauf), Wertpapierkredit bis hebel 2. Ordertypen: markt, limit, stop mit gueltigkeit tag/gtc/Datum; offene Aufträge stehen in portfolio und werden alle 15 min geprüft.",
             "schema": s({"instrument_id": str_, "aktion": {"type": "string", "enum": ["kaufen", "verkaufen"]},
                          "begruendung": {"type": "string", "description": "These, stärkstes Gegenargument, Kostenrechnung"},
                          "zuversicht": {"type": "number", "description": "0..1 – Skala: 0,9+ unverkennbar, 0,7–0,89 solide, 0,4–0,69 gemischt, < 0,4 kein Vorteil (dann nicht kaufen)"},
                          "betrag_usd": {"type": "number", "description": "Einsatz in USD (bei Perps: Nominal)"}, "menge": num_,
                          "seite": {"type": "string", "enum": ["long", "short"], "description": "short = Leerverkauf (Perps und Aktien/ETFs)"},
                          "hebel": {"type": "number", "description": "Perps bis Profil-Limit; Aktien bis 2 (Wertpapierkredit, Zinsen); sonst 1"},
                          "stop_loss": {"type": "number", "description": "Preis des Instruments"}, "take_profit": num_,
                          "ausstiegsplan": str_, "wahrscheinlichkeit_ja": {"type": "number", "description": "Wettmärkte (beim Kaufen Pflicht): deine P(JA)"},
                          "invalidierung": {"type": "string", "description": "Kaufen: konkretes, beobachtbares Signal, bei dem die These falsch ist"},
                          "staerkstes_gegenargument": {"type": "string", "description": "Kaufen: ein Satz"},
                          "risiko_usd": {"type": "number", "description": "Kaufen: Verlust bis Stop-Loss bzw. bei Wetten bis 0"},
                          "gegenbegruendung": {"type": "string", "description": "Nur nach Ablehnung durch den Risikomanager: warum die Order trotzdem richtig ist"},
                          "auftragsart": {"type": "string", "enum": ["markt", "limit", "stop"], "description": "markt = sofort (Aktie bei geschlossener Börse: zur Eröffnung); limit = nur zum limit_preis oder besser; stop = sobald stop_preis erreicht (Ausbruch/Absicherung)"},
                          "limit_preis": {"type": "number", "description": "Bei auftragsart limit: Kauf höchstens / Verkauf mindestens zu diesem Preis"},
                          "stop_preis": {"type": "number", "description": "Bei auftragsart stop: Auslösepreis (Kauf-Stop über, Verkauf-Stop unter dem Kurs)"},
                          "gueltigkeit": {"type": "string", "description": "tag (Standard: bis Handelsschluss bzw. 24 h), gtc (bis auf Widerruf, max. 30 Tage) oder Datum/Zeit ISO-8601"}},
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
