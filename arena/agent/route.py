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


def kandidaten() -> list[dict]:
    out = []
    for d in funds.liga_fonds():
        if not funds.liga_hat_schluessel(d) or d["anbieter"] == "groq" or d.get("entfallen"):
            continue
        if funds.meta(d["id"]).get("pausiert_bis", 0) > time.time():  # ohne Guthaben nicht als Nachfolger wählen
            continue
        out.append(d)
    return out


def modellwahl(jetzt: float | None = None) -> dict:
    """Nachfolger der Claude-Fonds statistisch abgesichert (Recherche B8/Hebel 8): Model Confidence Set (α = 0,1) über die Stunden-Verluste
    (−Log-Rendite) der Liga-Fonds; unter den nicht unterscheidbaren Besten wird das günstigste Modell gewählt (bei Gleichstand höhere Rendite).
    Zu wenig gemeinsame Daten → Rückfall auf die beste Rendite (ausgewiesen). Ergebnis in data/modellwahl.json (für Seite und Nachvollzug)."""
    from arena import config, metrics
    from arena import statistik as st
    jetzt = jetzt or time.time()
    cfg = config.load()
    mw = cfg.get("modellwahl", {})
    kosten = cfg.get("liga_kosten_je_runde_usd", {})
    kand = kandidaten()
    if not kand:
        return {"ts": jetzt, "gewaehlt": None, "grund": "kein Liga-Modell verfügbar"}
    reihen = {d["id"]: dict(metrics.stundenrenditen(store.lies_jsonl(f"funds/{d['id']}/equity.jsonl"))) for d in kand}
    mit_daten = [d for d in kand if len(reihen[d["id"]]) >= 12 and funds.meta(d["id"]).get("letzte_runde")]
    if mit_daten:  # nur Modelle, die wirklich gehandelt/gerechnet haben (sonst gewänne ein nie gelaufener Fonds mit 0 %)
        kand = mit_daten
        reihen = {d["id"]: reihen[d["id"]] for d in kand}
    gemeinsam = set.intersection(*(set(r) for r in reihen.values())) if reihen else set()
    stunden = sorted(gemeinsam)
    renditen = {d["id"]: rendite(d["id"]) for d in kand}
    if len(kand) >= 2 and len(stunden) >= mw.get("min_stunden", 48):
        mcs = st.model_confidence_set({fid: [-reihen[fid][h] for h in stunden] for fid in reihen}, alpha=mw.get("alpha", 0.1))
        menge = [d for d in kand if d["id"] in mcs["menge"]]
        verfahren = f"Model Confidence Set (α={mw.get('alpha', 0.1)}, {len(stunden)} gemeinsame Stunden)"
    else:
        mcs = None
        best = max(kand, key=lambda d: (renditen[d["id"]] is not None, renditen[d["id"]] or -1))
        menge = [best]
        verfahren = f"Rückfall beste Rendite (nur {len(stunden)} gemeinsame Stunden, MCS braucht {mw.get('min_stunden', 48)})"
    gewaehlt = min(menge, key=lambda d: (kosten.get(d["anbieter"], 0.05), -(renditen[d["id"]] or -1)))
    return {"ts": jetzt, "gewaehlt": gewaehlt["id"], "name": gewaehlt["name"], "verfahren": verfahren,
            "menge": [d["id"] for d in menge], "p_werte": mcs["p_werte"] if mcs else None,
            "kosten_je_runde_usd": {d["id"]: kosten.get(d["anbieter"], 0.05) for d in kand},
            "rendite_pct": {k: (round(100 * v, 2) if v is not None else None) for k, v in renditen.items()},
            "grund": "günstigstes Modell unter den statistisch nicht unterscheidbaren Besten"}


def bestes_liga_modell(jetzt: float | None = None) -> dict | None:
    """Gewählter Nachfolger; die Wahl bleibt `stabil_tage` stehen (kein Hin und Her zwischen Runden), außer das Modell fällt aus."""
    from arena import config
    jetzt = jetzt or time.time()
    stabil = config.load().get("modellwahl", {}).get("stabil_tage", 7) * 86400
    z = store.lies("modellwahl.json", {})
    kand = {d["id"]: d for d in kandidaten()}
    if z.get("gewaehlt") in kand and jetzt - z.get("ts", 0) < stabil:
        return kand[z["gewaehlt"]]
    neu = modellwahl(jetzt)
    store.schreibe("modellwahl.json", neu)
    return kand.get(neu["gewaehlt"])


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
