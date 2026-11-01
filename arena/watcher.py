"""Wächter: alle 15 Minuten, ohne KI. Daten holen, Portfolios bewerten, Stops/Funding/Liquidation/
Abrechnung ausführen, Ereignisse erzeugen. Aufruf: python -m arena.watcher"""
from __future__ import annotations

import os
import sys
import time

from arena import benchmarks, config, events, funds, store, verlauf
from arena.data import crypto, news, pm, stocks
from arena.exchange import engine, impact, portfolio
from arena.exchange.book import Book
from arena.registry import Marktzugriff, preis_fuer_ereignisse


def mitte(b: Book | None) -> float | None:
    return None if b is None else b.mid


def sammle_preise(cfg: dict, pm_markte: list[dict]) -> tuple[dict, dict]:
    """Preise (Mitte) aller beobachteten Instrumente + Funding je 8 h der Perps."""
    preise, funding = {}, {}
    for s in cfg["universum"]["krypto"]:
        t = crypto.spot_ticker(s)
        if t:
            preise[f"spot:{s}-USD"] = (t["bid"] + t["ask"]) / 2
    for p in cfg["universum"]["perps"]:
        t = crypto.perp_ticker(p)
        if t:
            preise[f"perp:{p}"] = t["mark"]
            funding[f"perp:{p}"] = t["funding_8h"]
    for s in cfg["universum"]["aktien"]:
        k = stocks.kurs(s)
        if k:
            preise[f"stock:{s}"] = k["preis"]
    for m in pm_markte:
        preise[f"{m['mid']}:JA"] = (m["ja_bid"] + m["ja_ask"]) / 2
    return preise, funding


def _stop_buch(auslöser: float, seite: str, aktuell: Book | None, menge: float = 0.0, inst: dict | None = None) -> Book:
    """Ein ausgelöster Stop füllt am Stop-Preis, verschlechtert um den Marktimpact (Square-Root-Gesetz aus Tagesvolumen und -vola;
    die normale Slippage übernimmt die Börse), außer der Markt liegt schon schlechter (Lücke) – dann gilt das aktuelle Buch."""
    if aktuell is not None:
        if seite == "long" and aktuell.bids and aktuell.bids[0][0] < auslöser:
            return aktuell
        if seite == "short" and aktuell.asks and aktuell.asks[0][0] > auslöser:
            return aktuell
    imp = impact.sqrt_impact(menge, auslöser, *impact.markt_kennzahlen(inst)) if inst and menge else 0.0
    px = auslöser * (1 - imp) if seite == "long" else auslöser * (1 + imp)
    return Book([(px, 1e9)], [(px, 1e9)], time.time())


_funding_cache: dict[tuple[str, int], float | None] = {}


def exakte_funding_raten(pf: dict, raten_8h: dict, seit: float, jetzt: float) -> dict:
    """Tatsächliches Deribit-Funding des Zeitraums (get_funding_rate_value), umgerechnet in eine 8-h-Rate, damit funding_buchen
    für den ganzen Zeitraum genau diesen Betrag bucht. Rückfall: aktuelles 8-h-Mittel des Tickers."""
    out = dict(raten_8h)
    stunden = (jetzt - seit) / 3600
    if stunden <= 0:
        return out
    for pos in pf["positionen"]:
        if pos["inst"]["art"] != "perp":
            continue
        key = (pos["inst"]["symbol"], int(seit // 60))
        if key not in _funding_cache:
            _funding_cache[key] = crypto.funding_wert(pos["inst"]["symbol"], seit, jetzt)
        w = _funding_cache[key]
        if w is not None:
            out[pos["inst"]["id"]] = w * 8 / stunden
    return out


def fuehre_auftraege_aus(pf: dict, prof: dict, mz: Marktzugriff, jetzt: float) -> list[dict]:
    """Bei geschlossener Börse vorgemerkte Aktien-/ETF-Aufträge: beim ersten Tick mit offenem Buch gegen das dann gültige Buch ausführen
    (Limits, Cash und Impact zum Ausführungszeitpunkt); nach Handelsschluss des Ziel-Tages verfallen sie."""
    log, rest = [], []
    for a in pf.get("auftraege", []):
        if jetzt > a["gueltig_bis"]:
            log.append({"ok": False, "ts": jetzt, "aktion": "auftrag_verfallen", "fonds_id": pf["fonds_id"], "inst_id": a["inst"]["id"],
                        "entscheidung_id": a["entscheidung_id"], "grund": "Auftrag zur Eröffnung verfallen"})
            continue
        book, _ = mz.buch(a["inst"])
        if book is None or (not book.asks and not book.bids):
            rest.append(a)
            continue
        marks = {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]}
        eq = portfolio.equity(pf, marks)
        if a["aktion"] == "kaufen":
            r = engine.eroeffne(pf, prof, a["inst"], book, qty=a.get("menge"), usd=a.get("betrag_usd"), equity=eq, stop_loss=a.get("stop_loss"),
                                take_profit=a.get("take_profit"), ausstiegsplan=a.get("ausstiegsplan", ""), entscheidung_id=a["entscheidung_id"], ts=jetzt)
            if r.get("ok") and a.get("invalidierung"):
                pos = next((p for p in pf["positionen"] if p["id"] == r["position_id"]), None)
                if pos is not None:
                    pos["invalidierung"] = a["invalidierung"]
        else:
            pos = next((p for p in pf["positionen"] if p["inst"]["id"] == a["inst"]["id"]), None)
            r = engine.schliesse(pf, pos, book, qty=a.get("menge"), grund="Auftrag zur Eröffnung", ts=jetzt) if pos else \
                {"ok": False, "grund": "Position nicht mehr vorhanden"}
        log.append({**r, "ts": jetzt, "fonds_id": pf["fonds_id"], "entscheidung_id": a["entscheidung_id"], "auftrag": a["id"]})
    pf["auftraege"] = rest
    return log


def verarbeite_portfolio(pf: dict, mz: Marktzugriff, funding_raten: dict, jetzt: float) -> list[dict]:
    """Funding → Liquidation → Stop-Loss/Take-Profit → Abrechnung. Liefert Ledger-Einträge."""
    log: list[dict] = []
    seit = pf.get("letzter_tick") or jetzt
    stunden = max(0.0, min((jetzt - seit) / 3600, 6.0))
    if stunden > 0:
        log += engine.funding_buchen(pf, exakte_funding_raten(pf, funding_raten, jetzt - stunden * 3600, jetzt), stunden, jetzt)
    extreme, marks = {}, {}
    for pos in pf["positionen"]:
        iid = pos["inst"]["id"]
        m = mz.marke(pos["inst"])
        marks[iid] = m.get("mark") if m.get("mark") is not None else m.get("bid")
        if pos["inst"]["art"] in ("spot", "perp"):
            ex = mz.extreme(pos["inst"], max(min(seit, jetzt), pos.get("eroeffnet", 0)))  # Dochte vor der Eröffnung zählen nicht
            if ex:
                extreme[iid] = ex
    marks = {k: v for k, v in marks.items() if v is not None}
    log += engine.pruefe_liquidation(pf, extreme, marks, jetzt)
    for pos, grund, preis in engine.stop_ziele(pf, extreme, marks):
        book, idx = mz.buch(pos["inst"])
        r = engine.schliesse(pf, pos, _stop_buch(preis, pos["seite"], book, pos["menge"], pos["inst"]), grund=grund, ts=jetzt, index_preis=idx)
        r["ausloeser_preis"] = preis
        log.append(r)
    for pos in list(pf["positionen"]):
        i = pos["inst"]
        if i["art"] == "pm" and (jetzt > (i.get("schliesst") or jetzt + 1) - 3600 * 24 * 365):
            res = mz.aufloesung(i)
            if res == "STORNO":
                log.append(engine.rechne_pm_storno(pf, pos, jetzt))
            elif res is not None:
                log.append(engine.rechne_pm_ab(pf, pos, float(res), jetzt))
        elif i["art"] == "option" and jetzt > i["verfall"]:
            px = mz.aufloesung(i)
            if px is not None:
                log.append(engine.rechne_option_ab(pf, pos, px, jetzt))
    pf["letzter_tick"] = jetzt
    return log


def loese_prognosen_auf(fonds_ids: list[str], jetzt: float, limit: int = 20) -> int:
    """Hält Ausgänge der Wettmärkte fest, zu denen Agenten Wahrscheinlichkeiten abgegeben haben (für den Brier-Score)."""
    res = store.lies("resolutions.json", {})
    offen = []
    for fid in fonds_ids:
        for p in store.lies_jsonl(f"funds/{fid}/prognosen.jsonl"):
            if p["markt_id"] not in res and p["markt_id"] not in offen:
                offen.append(p["markt_id"])
    neu = 0
    for mid in offen[:limit]:
        try:
            _, venue, ident = mid.split(":", 2)
            m = pm.einzelmarkt(venue, ident) or {"ref": {"id": ident, "ticker": ident, "vertrag": int(ident) if ident.isdigit() else 0}}
            i = {"venue": venue, "ref": m["ref"]}
            w = pm.aufloesung(i)
        except Exception:
            continue
        if w is not None:
            res[mid] = {"wert": None if w == "STORNO" else float(w), "ts": jetzt}
            neu += 1
    if neu:
        store.schreibe("resolutions.json", res)
    return neu


def lauf(jetzt: float | None = None) -> dict:
    jetzt = jetzt or time.time()
    cfg = config.load()
    mz = Marktzugriff()
    fx = crypto.usd_je_eur()
    pm_markte = pm.universum()
    preise, funding = sammle_preise(cfg, pm_markte)
    store.schreibe("fx.json", {"usd_je_eur": fx, "ts": jetzt})

    # Portfolios anlegen/laden
    defs = [d for d in funds.alle_definitionen()]
    pfs = {}
    for d in defs:
        pf = funds.erzeuge_falls_noetig(d, fx, jetzt)
        if pf:
            pfs[d["id"]] = (d, pf)
    # Verlauf VOR dem Anhängen des aktuellen Ticks laden (für Ereignisse)
    hist = verlauf.lade(50, jetzt)
    gehalten: dict[str, list[str]] = {}
    pos_schluss = []
    for fid, (d, pf) in pfs.items():
        for p in pf["positionen"]:
            gehalten.setdefault(p["inst"]["id"], []).append(fid)
            if p["inst"].get("schliesst"):
                pos_schluss.append({"fonds": fid, "position_id": p["id"], "inst_id": p["inst"]["id"],
                                    "schliesst": p["inst"]["schliesst"]})
            if p["inst"]["art"] == "option":
                pos_schluss.append({"fonds": fid, "position_id": p["id"], "inst_id": p["inst"]["id"],
                                    "schliesst": p["inst"]["verfall"]})

    ledger_gesamt = 0
    pm_index = {m["mid"]: m for m in pm_markte}
    for fid, (d, pf) in pfs.items():
        log = verarbeite_portfolio(pf, mz, funding, jetzt)
        if pf.get("auftraege"):
            log += fuehre_auftraege_aus(pf, funds.risikoprofil(d), mz, jetzt)
        if d["typ"] == "schwarm" or d.get("kontrolle"):
            from arena import schwarm
            try:
                if d.get("art") == "wetter":
                    log += schwarm.schritt_wetter(d, pf, mz, jetzt)
                else:
                    log += (schwarm.schritt_schwarm if d["typ"] == "schwarm" else schwarm.schritt_kontrolle)(d, pf, mz, jetzt, pm_index)
            except Exception as e:  # Meta-/Kontrollfonds dürfen den Tick nie abbrechen
                print("WARNUNG", fid, e)
        elif d["typ"] == "benchmark":
            marks_b = {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]}
            log += benchmarks.schritt(d, pf, mz, marks_b, jetzt)
        for r in log:
            store.anhaengen(f"funds/{fid}/ledger.jsonl", r)
        ledger_gesamt += len(log)
        marks = {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]}
        eq = portfolio.equity(pf, marks)
        for p in pf["positionen"]:  # letzte Bewertung festhalten (für Webseite/Status)
            m = marks.get(p["inst"]["id"], {})
            p["kurs"] = m.get("mark") if m.get("mark") is not None else m.get("bid")
            p["wert"] = round(portfolio.pos_wert(p, m.get("bid"), m.get("mark")), 2)
        store.anhaengen(f"funds/{fid}/equity.jsonl", {"t": int(jetzt), "usd": round(eq, 2), "cash": round(pf["cash"], 2),
                                                      "n": len(pf["positionen"]), "gebuehren": round(pf["gebuehren"], 2)})
        funds.speichere_portfolio(pf)

    if int(jetzt // 900) % 4 == 0:  # etwa stündlich
        try:
            loese_prognosen_auf(list(pfs), jetzt)
        except Exception as e:
            print("WARNUNG Auflösung:", e)

    # Ereignisse
    bekannt = {e["schluessel"] for e in store.lies_jsonl("events.jsonl", 3000)}
    try:
        nachrichten = news.alle_nachrichten()
    except Exception as e:  # Nachrichtenquellen dürfen ausfallen
        print("WARNUNG Nachrichten:", e)
        nachrichten = []
    neue = events.erkenne(jetzt, preise, hist, gehalten, pm_markte, pos_schluss, nachrichten, funding, bekannt, cfg["ereignisse"])
    for e in neue:
        store.anhaengen("events.jsonl", e)
    verlauf.tick_anhaengen(jetzt, _beobachtete(preise, gehalten, pm_markte))

    for f in mz.fehler[:10]:
        print("WARNUNG", f)
    from arena import entscheider
    ausloesen = entscheider.soll_ausloesen(neue, jetzt)
    zusammenfassung = {"ts": jetzt, "fonds": len(pfs), "ledger": ledger_gesamt, "ereignisse": len(neue),
                       "weckend": sum(1 for e in neue if e["weckt"]), "preise": len(preise), "ausloesen": ausloesen}
    print(zusammenfassung)
    return zusammenfassung


def _beobachtete(preise: dict, gehalten: dict, pm_markte: list[dict]) -> dict:
    """Verlauf speichern: alles außer Wetten + (gehaltene und die 40 umsatzstärksten Wetten)."""
    top = sorted(pm_markte, key=lambda m: -m.get("volumen_24h", 0))[:40]
    erlaubt = {f"{m['mid']}:JA" for m in top} | set(gehalten)
    return {k: v for k, v in preise.items() if not k.startswith("pm:") or k in erlaubt}


def main() -> int:
    try:
        z = lauf()
    except Exception as e:  # Der Workflow soll nie rot werden; der Fehler steht im Log und im Status
        import traceback
        traceback.print_exc()
        store.schreibe("watcher_fehler.json", {"ts": time.time(), "fehler": str(e)})
        z = {"weckend": 0}
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"weckend={z.get('weckend', 0)}\nausloesen={str(z.get('ausloesen', False)).lower()}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
