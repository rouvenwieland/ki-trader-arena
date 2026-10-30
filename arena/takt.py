"""Taktgeber des Dauerlaufs: entscheidet nach jedem Wächter-Tick, welche Agentenarbeit fällig ist.
Aufruf: python -m arena.takt [ausloesen]  → druckt eine Aufgabe je Zeile: taeglich | takt | ereignis | review | prognosen

Hintergrund (siehe DECISIONS.md): GitHub-Cron feuerte in den ersten Tagen kaum (1 von ~36 Wächter-Läufen in 9 h).
Deshalb läuft alles in einem selbst verkettenden Dauerlauf-Job; die Zeitpläne leben hier im Code."""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone

from arena import config, store

ZUSTAND = "takt_zustand.json"
SLOT_GUELTIG_STUNDEN = 3  # eine verpasste feste Runde wird höchstens 3 h später nachgeholt
PROGNOSE_ABSTAND = 6 * 3600


def aufgaben(jetzt: float | None = None, ereignis: bool = False) -> list[str]:
    jetzt = jetzt or time.time()
    cfg = config.load()["budget"]
    z = store.lies(ZUSTAND, {"slots": [], "review": "", "prognosen": 0})
    d = datetime.fromtimestamp(jetzt, timezone.utc)
    out: list[str] = []
    stunden = [h for h in cfg.get("takt_stunden_utc", []) if h <= d.hour and d.hour - h < SLOT_GUELTIG_STUNDEN]
    if stunden:
        h = max(stunden)
        slot = f"{d:%Y-%m-%d}T{h:02d}"
        if slot not in z["slots"]:
            z["slots"] = (z["slots"] + [slot])[-40:]
            out.append("taeglich" if h == cfg.get("tiefenrunde_stunde_utc") else "takt")
    if ereignis and not out:
        out.append("ereignis")
    iso = d.isocalendar()
    woche = f"{iso[0]}-W{iso[1]:02d}"
    berichte = config.ROOT / "reports"
    nachholen = (berichte / f"{woche}-abgeschnitten.md").exists()  # abgeschnittenes Review dieser Woche einmal neu erzeugen
    if (d.weekday() == 6 and d.hour >= 18 or nachholen) and z.get("review") != woche and not (berichte / f"{woche}.md").exists():
        z["review"] = woche
        out.append("review")
    prog = store.lies("prognosen.json", {}) or {}
    letzte = max(z.get("prognosen", 0), prog.get("ts", 0) if isinstance(prog, dict) else 0)
    if jetzt - letzte > PROGNOSE_ABSTAND:
        z["prognosen"] = jetzt
        out.append("prognosen")
    store.schreibe(ZUSTAND, z)
    return out


if __name__ == "__main__":
    for a in aufgaben(ereignis="ausloesen" in sys.argv[1:]):
        print(a)
