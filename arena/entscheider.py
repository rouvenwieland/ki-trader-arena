"""Entscheider: läuft bei Ereignis (vom Wächter ausgelöst) und einmal täglich. Aufruf: python -m arena.entscheider [grund]
Jeder Fonds fehlerisoliert; fehlende Schlüssel/Budget → Status statt Fehler (Workflow bleibt grün)."""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone

from arena import config, funds, snapshot, store
from arena.agent import loop
from arena.agent.budget import Budget
from arena.agent.route import route
from arena.exchange import portfolio
from arena.registry import Marktzugriff

ZUSTAND = "entscheider_zustand.json"


def zustand() -> dict:
    return store.lies(ZUSTAND, {"letztes_ereignis_ts": 0, "laeufe": {}, "letzte_ausloesung": 0, "letzte_taegliche": 0})


def soll_ausloesen(neue_ereignisse: list[dict], jetzt: float) -> bool:
    """Wächter-Entscheidung: gibt es weckende Ereignisse, Abstand eingehalten, Tageslimit nicht erreicht, mindestens ein Schlüssel?"""
    cfg = config.load()["ereignisse"]
    z = zustand()
    if not any(e["weckt"] for e in neue_ereignisse):
        return False
    if jetzt - z["letzte_ausloesung"] < cfg["cooldown_min"] * 60:
        return False
    tag = datetime.fromtimestamp(jetzt, timezone.utc).strftime("%Y-%m-%d")
    if z["laeufe"].get(tag, 0) >= cfg["max_entscheider_pro_tag"]:
        return False
    if not any(funds.hat_schluessel(k) for k in ["ARENA_ANTHROPIC_KEY"] + [f["schluessel"] for f in config.load()["liga"]] + ["OPENROUTER_API_KEY"]):
        return False
    z["letzte_ausloesung"] = jetzt
    store.schreibe(ZUSTAND, z)
    return True


def relevante(ereignisse: list[dict], fid: str) -> list[dict]:
    return [e for e in ereignisse if e["fonds"] is None or fid in e["fonds"]]


def status_schreiben(fid: str, zustand_text: str, jetzt: float, extra: dict | None = None) -> None:
    m = funds.meta(fid)
    m["status"] = zustand_text
    m["status_ts"] = jetzt
    if extra:
        m.update(extra)
    funds.speichere_meta(fid, m)


def lauf(grund: str = "ereignis", jetzt: float | None = None) -> dict:
    jetzt = jetzt or time.time()
    z = zustand()
    fx = (store.lies("fx.json") or {}).get("usd_je_eur") or config.load()["fallback_usd_je_eur"]
    bud = Budget(fx, jetzt)
    tag = datetime.fromtimestamp(jetzt, timezone.utc).strftime("%Y-%m-%d")
    taeglich = grund == "taeglich" or (jetzt - z["letzte_taegliche"] > 23 * 3600 and grund != "ereignis")
    alle_ev = [e for e in store.lies_jsonl("events.jsonl", 500) if e["ts"] > z["letztes_ereignis_ts"] and e["weckt"]]
    defs = [d for d in funds.claude_fonds() + funds.liga_fonds()]
    if os.environ.get("ARENA_NUR_FONDS"):  # Debug: einzelne Fonds testen
        defs = [d for d in defs if d["id"] in os.environ["ARENA_NUR_FONDS"].split(",")]
    kandidaten = []
    for d in defs:
        pf = funds.lade_portfolio(d["id"])
        if pf is None:
            status_schreiben(d["id"], "wartet auf Schlüssel" if not funds.liga_hat_schluessel(d) else "wartet auf ersten Wächter-Lauf", jetzt) \
                if funds.meta(d["id"]) or not funds.liga_hat_schluessel(d) else None
            continue
        kandidaten.append((d, pf))
    if not kandidaten:
        print("Keine Fonds mit Portfolio.")
        return {"gelaufen": 0}
    snap = snapshot.baue(jetzt)
    mz = Marktzugriff()
    ergebnisse = {}

    def bearbeite(d: dict, pf: dict) -> None:
        fid = d["id"]
        try:
            r = route(d, bud, jetzt)
            if "status" in r:
                status_schreiben(fid, r["status"], jetzt)
                ergebnisse[fid] = r["status"]
                return
            ev = relevante(alle_ev, fid)
            if not taeglich and not ev:
                return
            if not taeglich and d["typ"] == "liga":
                info = f"{len(pf['positionen'])} Positionen: " + ", ".join(p["inst"]["id"] for p in pf["positionen"])
                wecken, warum = loop.triage_groq(d, ev, info)
                store.anhaengen(f"funds/{fid}/decisions.jsonl", {"typ": "triage", "ts": jetzt, "aufwecken": wecken, "grund": warum, "vorsichter": "groq"})
                if not wecken:
                    ergebnisse[fid] = f"Vorsichter (Groq): nicht wecken ({warum})"
                    return
            if not taeglich and r.get("triage"):
                marks = {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]}
                info = f"Eigenkapital {portfolio.equity(pf, marks):.0f} USD, {len(pf['positionen'])} Positionen: " + \
                       ", ".join(p["inst"]["id"] for p in pf["positionen"])
                wecken, warum = loop.triage(d, ev, info, bud, len(defs))
                store.anhaengen(f"funds/{fid}/decisions.jsonl", {"typ": "triage", "ts": jetzt, "aufwecken": wecken, "grund": warum})
                if not wecken:
                    ergebnisse[fid] = f"Vorsichter: nicht wecken ({warum})"
                    return
            res = loop.laufe_runde(d, r, pf, snap, mz, "tägliche Runde" if taeglich else "Ereignis", ev, bud, 3, jetzt)
            fehler = res["abbruch"].startswith(("Modellfehler", "Fehler"))
            status_schreiben(fid, ("Fehler: " + res["abbruch"][:140]) if fehler else
                             "aktiv" + (f" (Modell: {r['umgeschaltet_auf']})" if r.get("umgeschaltet_auf") else ""), jetzt,
                             {"modell_aktuell": r["modell"], "letzte_runde": jetzt, "letzte_runde_abbruch": res["abbruch"]})
            ergebnisse[fid] = f"Runde: {res['orders']} Orders, {res['schritte']} Schritte, {res['kosten_usd']} USD {res['abbruch']}"
        except Exception as e:  # ein Fonds darf nie die anderen blockieren
            import traceback
            traceback.print_exc()
            status_schreiben(fid, f"Fehler: {type(e).__name__}", jetzt)
            ergebnisse[fid] = f"FEHLER {e}"

    # Claude-Fonds nacheinander (gemeinsames Budget), Liga-Fonds parallel dazu (eigene Zustände, langsame Antworten)
    from concurrent.futures import ThreadPoolExecutor
    claude = [k for k in kandidaten if k[0]["typ"] == "claude"]
    liga = [k for k in kandidaten if k[0]["typ"] != "claude"]

    def claude_serie() -> None:
        for d, pf in claude:
            bearbeite(d, pf)

    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(claude_serie)] + [ex.submit(bearbeite, d, pf) for d, pf in liga]
        for f in futs:
            f.result()
    z["letztes_ereignis_ts"] = max([e["ts"] for e in alle_ev] + [z["letztes_ereignis_ts"]])
    z["laeufe"][tag] = z["laeufe"].get(tag, 0) + 1
    if taeglich:
        z["letzte_taegliche"] = jetzt
    store.schreibe(ZUSTAND, z)
    store.schreibe("budget_status.json", bud.bericht() | {"ts": jetzt})
    for k, v in ergebnisse.items():
        print(k, "->", v)
    return {"gelaufen": len(ergebnisse), "ergebnisse": ergebnisse}


def main() -> int:
    grund = sys.argv[1] if len(sys.argv) > 1 else "ereignis"
    try:
        lauf(grund)
    except Exception:
        import traceback
        traceback.print_exc()
    return 0


if __name__ == "__main__":
    sys.exit(main())
