"""Entscheider: läuft bei Ereignis (vom Wächter ausgelöst), fest alle ~4 h (takt) und täglich als Tiefenrunde.
Aufruf: python -m arena.entscheider [ereignis|takt|taeglich]
Jeder Fonds fehlerisoliert; fehlende Schlüssel/Budget → Status statt Fehler (Workflow bleibt grün)."""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone

from arena import config, funds, snapshot, store
from arena.agent import loop
from arena.agent.budget import Budget
from arena.agent.route import PAUSE_KEIN_GUTHABEN, route
from arena.exchange import portfolio
from arena.registry import Marktzugriff

ZUSTAND = "entscheider_zustand.json"
MIN_RUNDE_USD = 0.06  # darunter lohnt keine Runde (Rest des Tagesanteils)
PAUSE_SEKUNDEN = 20 * 3600  # Fonds ohne Guthaben: einmal am Tag neu probieren


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


def rundenart(grund: str, z: dict, jetzt: float) -> str:
    """tief = tägliche Tiefenrunde (Opus), takt = feste Runde alle ~4 h (Sonnet), ereignis = vom Wächter geweckt (mit Vorsichter).
    Fiel die Tiefenrunde aus (> 23 h her), wird die nächste feste Runde zur Tiefenrunde."""
    if grund == "taeglich":
        return "tief"
    if grund == "ereignis":
        return "ereignis"
    return "tief" if jetzt - z.get("letzte_taegliche", 0) > 23 * 3600 else "takt"


def lauf(grund: str = "ereignis", jetzt: float | None = None) -> dict:
    jetzt = jetzt or time.time()
    z = zustand()
    cfg = config.load()
    fx = (store.lies("fx.json") or {}).get("usd_je_eur") or cfg["fallback_usd_je_eur"]
    bud = Budget(fx, jetzt)
    tag = datetime.fromtimestamp(jetzt, timezone.utc).strftime("%Y-%m-%d")
    stunde = datetime.fromtimestamp(jetzt, timezone.utc).hour
    art = rundenart(grund, z, jetzt)
    fest = art in ("tief", "takt")
    liga_dabei = art == "tief" or art == "ereignis" or stunde in cfg.get("liga_takt_stunden_utc", [])
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
    try:  # Lernschleife: Reflexion zu frisch abgeschlossenen Positionen + Policy-Gate, bevor die Fonds entscheiden
        from arena import reflexion
        print("Reflexionen:", reflexion.lauf(bud, jetzt))
    except Exception as e:
        print("WARNUNG Reflexion:", e)
    snap = snapshot.baue(jetzt)
    mz = Marktzugriff()
    ergebnisse = {}
    anlass = {"tief": "tägliche Tiefenrunde", "takt": "feste Runde", "ereignis": "Ereignis"}[art]

    def bearbeite(d: dict, pf: dict) -> None:
        fid = d["id"]
        try:
            if d["typ"] == "liga" and not liga_dabei:
                return
            r = route(d, bud, jetzt, tief=art == "tief")
            if "status" in r:
                status_schreiben(fid, r["status"], jetzt)
                ergebnisse[fid] = r["status"]
                return
            ev = relevante(alle_ev, fid)
            warum = ""
            if not fest and not ev:
                return
            if not fest and d["typ"] == "liga":
                info = f"{len(pf['positionen'])} Positionen: " + ", ".join(p["inst"]["id"] for p in pf["positionen"])
                wecken, warum = loop.triage_groq(d, ev, info)
                store.anhaengen(f"funds/{fid}/decisions.jsonl", {"typ": "triage", "ts": jetzt, "aufwecken": wecken, "grund": warum, "vorsichter": "groq"})
                if not wecken:
                    ergebnisse[fid] = f"Vorsichter (Groq): nicht wecken ({warum})"
                    return
            if not fest and r.get("triage"):
                marks = {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]}
                info = f"Eigenkapital {portfolio.equity(pf, marks):.0f} USD, {len(pf['positionen'])} Positionen: " + \
                       ", ".join(p["inst"]["id"] for p in pf["positionen"])
                wecken, warum = loop.triage(d, ev, info, bud, len(defs))
                store.anhaengen(f"funds/{fid}/decisions.jsonl", {"typ": "triage", "ts": jetzt, "aufwecken": wecken, "grund": warum})
                if not wecken:
                    ergebnisse[fid] = f"Vorsichter: nicht wecken ({warum})"
                    return
            plan = warum.split(" | PLAN: ", 1)[1].split(" ; ") if " | PLAN: " in warum else None  # Rechercheplan des Vorsichters
            rb = None
            if r["art"] == "anthropic":
                rb = bud.runden_budget_usd(fid, r["modell"], art, stunde)
                if rb < MIN_RUNDE_USD:
                    status_schreiben(fid, "Tagesanteil aufgebraucht – nächste Runde morgen", jetzt)
                    ergebnisse[fid] = f"übersprungen (Rundenbudget {rb:.3f} USD)"
                    return
            res = loop.laufe_runde(d, r, pf, snap, mz, anlass, ev, bud, 3, jetzt, runden_budget_usd=rb, plan=plan)
            ergebnisse[fid] = f"Runde ({r['modell']}): {res['orders']} Orders, {res['schritte']} Schritte, {res['kosten_usd']} USD {res['abbruch']}"
            extra = {"modell_aktuell": res["modell"], "letzte_runde": jetzt, "letzte_runde_abbruch": res["abbruch"]}
            if d["typ"] == "liga" and res["modell"] != d["modell"]:
                extra |= {"modell_aufgeloest": res["modell"], "modell_konfiguriert": d["modell"]}
            if res["abbruch"].startswith("Kein Guthaben"):
                status_schreiben(fid, PAUSE_KEIN_GUTHABEN, jetzt, extra | {"pausiert_bis": jetzt + PAUSE_SEKUNDEN})
                return
            fehler = res["abbruch"].startswith(("Modellfehler", "Fehler"))
            text = ("Fehler: " + res["abbruch"][:140]) if fehler else \
                "aktiv" + (f" (Modell: {r['umgeschaltet_auf']})" if r.get("umgeschaltet_auf") else "")
            if fehler and "HTTP 404" in res["abbruch"] and d["typ"] == "liga":  # gemerkter Modellname taugt nicht mehr → beim nächsten Mal neu auflösen
                extra |= {"modell_aufgeloest": None}
            if fehler and any(c in res["abbruch"] for c in ("HTTP 503", "HTTP 502", "HTTP 529", "HTTP 500", "overloaded")):
                text = "vorübergehend gestört (Anbieter überlastet) – nächster Versuch beim nächsten Lauf"
            status_schreiben(fid, text, jetzt, extra | {"pausiert_bis": 0})
        except Exception as e:  # ein Fonds darf nie die anderen blockieren
            import traceback
            traceback.print_exc()
            status_schreiben(fid, f"Fehler: {type(e).__name__}", jetzt)
            ergebnisse[fid] = f"FEHLER {e}"

    # Alle Fonds parallel: Budget ist threadsicher (Reservierung des Worst-Case je Aufruf), Zustände sind je Fonds getrennt.
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as ex:
        for f in [ex.submit(bearbeite, d, pf) for d, pf in kandidaten]:
            f.result()
    z["letztes_ereignis_ts"] = max([e["ts"] for e in alle_ev] + [z["letztes_ereignis_ts"]])
    z["laeufe"][tag] = z["laeufe"].get(tag, 0) + 1
    z["laeufe"] = dict(sorted(z["laeufe"].items())[-30:])  # Zustand klein halten
    if art == "tief":
        z["letzte_taegliche"] = jetzt
    store.schreibe(ZUSTAND, z)
    store.schreibe("budget_status.json", bud.bericht() | {"ts": jetzt, "letzte_runde": art})
    for k, v in ergebnisse.items():
        print(k, "->", v)
    return {"gelaufen": len(ergebnisse), "ergebnisse": ergebnisse, "art": art}


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
