"""Welches Modell treibt welchen Fonds? Umschaltung der Claude-Fonds auf das beste Liga-Modell."""
from __future__ import annotations

import os
import time

from arena import funds, store
from arena.agent.budget import Budget


def rendite(fid: str) -> float | None:
    eq = store.lies_jsonl(f"funds/{fid}/equity.jsonl")
    pf = funds.lade_portfolio(fid)
    if not eq or not pf:
        return None
    return eq[-1]["usd"] / pf["start_kapital"] - 1


def bestes_liga_modell() -> dict | None:
    best, best_r = None, None
    for d in funds.liga_fonds():
        if not funds.liga_hat_schluessel(d) or d["anbieter"] == "groq" or d.get("entfallen"):
            continue
        if funds.meta(d["id"]).get("pausiert_bis", 0) > time.time():  # ohne Guthaben nicht als Nachfolger wählen
            continue
        r = rendite(d["id"])
        if r is not None and (best_r is None or r > best_r):
            best, best_r = d, r
    return best


PAUSE_KEIN_GUTHABEN = "pausiert (kein Guthaben)"


def route(defn: dict, bud: Budget, jetzt: float, tief: bool = False) -> dict:
    """Gibt {"art","modell",...} zurück oder {"status": "..."} wenn der Fonds nicht laufen kann.
    tief=True: tägliche Tiefenrunde (Claude-Fonds mit dem Tiefenrunden-Modell, z. B. Opus)."""
    if defn["typ"] == "liga":
        key = os.environ.get(defn["schluessel"], "").strip()
        if not key:
            return {"status": "wartet auf Schlüssel"}
        if defn.get("entfallen"):
            return {"status": "pausiert (Modell nicht mehr gratis)"}
        m = funds.meta(defn["id"])
        if m.get("pausiert_bis", 0) > jetzt:  # kein Guthaben: nur einmal täglich neu probieren
            return {"status": m.get("status") or PAUSE_KEIN_GUTHABEN}
        # ein früher automatisch aufgelöster Modellname (404 → Modellliste) bleibt erhalten
        modell = m.get("modell_aufgeloest") if m.get("modell_konfiguriert") == defn["modell"] and m.get("modell_aufgeloest") else defn["modell"]
        return {"art": "openai", "anbieter": defn["anbieter"], "modell": modell, "key": key,
                "alternativen": defn.get("alternativen", [])}
    # Claude-Fonds
    umschalten = bud.claude_zeit_vorbei() or bud.gesamt_erschoepft()
    if not umschalten:
        if not os.environ.get("ARENA_ANTHROPIC_KEY", "").strip():
            return {"status": "wartet auf Schlüssel"}
        ok, grund = bud.darf(defn["id"], 1, global_nur=True)
        if not ok:
            return {"status": grund}
        b = bud.cfg["budget"]
        return {"art": "anthropic", "modell": b.get("tiefenrunde_modell", "claude-opus-5-5") if tief else b.get("runden_modell", "claude-sonnet-5-5"),
                "triage": True, "tief": tief}
    best = bestes_liga_modell()
    if not best:
        return {"status": "pausiert: Claude-Phase beendet, kein Liga-Modell verfügbar"}
    key = os.environ.get(best["schluessel"], "").strip()
    r = {"art": "openai", "anbieter": best["anbieter"], "modell": best["modell"], "key": key, "umgeschaltet_auf": best["name"],
         "alternativen": best.get("alternativen", [])}
    m = funds.meta(defn["id"])
    if m.get("modell_aktuell") != best["modell"]:  # Wechsel im Verlauf markieren
        grund = "Budget erschöpft" if bud.gesamt_erschoepft() else "Claude-Phase beendet (14.11.)"
        store.anhaengen("model_switches.jsonl", {"ts": jetzt, "fonds": defn["id"], "von": m.get("modell_aktuell", "claude-sonnet-5-5"),
                                                  "auf": best["modell"], "name": best["name"], "grund": grund})
        m["modell_aktuell"] = best["modell"]
        funds.speichere_meta(defn["id"], m)
    return r
