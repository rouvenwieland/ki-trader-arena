"""Fonds: Definitionen, Zustandsdateien, Statuslogik (Schlüssel vorhanden? Modell? Budget?)."""
from __future__ import annotations

import os
import time

from arena import config, store
from arena.exchange import portfolio

UNBEGRENZT = {"max_hebel": 1, "max_position_pct": 1.0, "max_perp_pct": 0.0, "max_optionen_pct": 0.0,
              "min_cash_pct": 0.0, "max_gesamt_exposure_pct": 1.0}

BENCHMARKS = [
    {"id": "bm_btc", "name": "Buy & Hold BTC", "typ": "benchmark", "art": "btc"},
    {"id": "bm_sp500", "name": "S&P-500-ETF (SPY)", "typ": "benchmark", "art": "sp500"},
    {"id": "bm_6040", "name": "60/40 (SPY/AGG)", "typ": "benchmark", "art": "6040"},
    {"id": "bm_affe", "name": "Zufallsaffe", "typ": "benchmark", "art": "affe"},
]
# Kontrollfonds für Wettmärkte und Meta-Fonds ohne LLM (Logik in arena/schwarm.py)
KONTROLLEN = [
    {"id": "ko_markt", "name": "Kontrolle: Markt-Kopierer", "typ": "benchmark", "art": "markt", "kontrolle": True},
    {"id": "ko_nein", "name": "Kontrolle: Immer NEIN", "typ": "benchmark", "art": "nein", "kontrolle": True},
    {"id": "ko_wetter", "name": "Regelfonds: Wetter-Ensemble", "typ": "benchmark", "art": "wetter", "kontrolle": True},
    {"id": "ko_shannon", "name": "Kontrolle: Shannons Dämon (BTC/Cash 50/50)", "typ": "benchmark", "art": "shannon", "kontrolle": True},
]
SCHWARM = [
    {"id": "schwarm_alle", "name": "Schwarm (alle KI)", "typ": "schwarm", "risiko": "mittel", "gruppe": "alle"},
    {"id": "schwarm_claude", "name": "Schwarm (nur Claude)", "typ": "schwarm", "risiko": "mittel", "gruppe": "claude"},
    {"id": "schwarm_liga", "name": "Schwarm (nur Liga)", "typ": "schwarm", "risiko": "mittel", "gruppe": "liga"},
]


def hat_schluessel(env: str) -> bool:
    return bool(os.environ.get(env, "").strip())


def claude_fonds() -> list[dict]:
    return [{**f, "typ": "claude"} for f in config.load()["fonds_claude"]]


def liga_fonds() -> list[dict]:
    """Liga-Fonds aus der Konfiguration + dynamische OpenRouter-Gratismodelle (falls Schlüssel)."""
    out = [{**f, "typ": "liga", "risiko": "mittel",
            "persoenlichkeit": "Sachlich, mittleres Risiko, gleiche Regeln wie alle anderen."} for f in config.load()["liga"]]
    gespeichert = store.lies("openrouter_modelle.json", {}).get("modelle", [])
    if hat_schluessel("OPENROUTER_API_KEY") or gespeichert:  # ohne Schlüssel: bekannte Fonds weiter anzeigen („wartet auf Schlüssel“)
        for m in (openrouter_modelle() if hat_schluessel("OPENROUTER_API_KEY") else gespeichert):
            slug = "".join(c if c.isalnum() else "_" for c in m["id"].split(":")[0])
            out.append({"id": f"liga_or_{slug}", "name": f"OpenRouter {m['id'].removesuffix(':free')}", "anbieter": "openrouter",
                        "modell": m["id"], "schluessel": "OPENROUTER_API_KEY", "typ": "liga", "risiko": "mittel",
                        "entfallen": bool(m.get("entfallen")),
                        "persoenlichkeit": "Sachlich, mittleres Risiko, gleiche Regeln wie alle anderen."})
    return out


def openrouter_modelle(jetzt: float | None = None) -> list[dict]:
    """Einmal gewählte OpenRouter-:free-Modelle bleiben stabil (ein Fonds = ein Modell über die ganze Laufzeit).
    Höchstens täglich wird geprüft, ob sie noch gratis angeboten werden; entfallene werden markiert und durch neue ergänzt."""
    from arena.agent import llm
    jetzt = jetzt or time.time()
    z = store.lies("openrouter_modelle.json", {"modelle": [], "geprueft": 0})
    if z["modelle"] and jetzt - z.get("geprueft", 0) < 86400:
        return z["modelle"]
    n = config.load()["openrouter_gratis_anzahl"]
    aktuell = llm.openrouter_gratis(n * 4)
    if not aktuell:  # Liste nicht erreichbar → beim Bekannten bleiben
        return z["modelle"]
    for m in z["modelle"]:
        m["entfallen"] = m["id"] not in aktuell
    aktiv = [m for m in z["modelle"] if not m["entfallen"]]
    bekannt = {m["id"] for m in z["modelle"]}
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    for mid in aktuell:
        if len(aktiv) >= n:
            break
        if mid not in bekannt and llm.modell_probe("openrouter", mid, key):  # gelistet heißt nicht nutzbar
            neu = {"id": mid, "seit": jetzt, "entfallen": False}
            z["modelle"].append(neu)
            aktiv.append(neu)
    z["geprueft"] = jetzt
    store.schreibe("openrouter_modelle.json", z)
    return z["modelle"]


def alle_definitionen() -> list[dict]:
    return claude_fonds() + liga_fonds() + SCHWARM + BENCHMARKS + KONTROLLEN


def liga_hat_schluessel(f: dict) -> bool:
    return f["typ"] != "liga" or hat_schluessel(f["schluessel"])


# ---- Zustand
def lade_portfolio(fid: str) -> dict | None:
    return store.lies(f"funds/{fid}/portfolio.json")


def speichere_portfolio(pf: dict) -> None:
    store.schreibe(f"funds/{pf['fonds_id']}/portfolio.json", pf)


def meta(fid: str) -> dict:
    return store.lies(f"funds/{fid}/meta.json", {})


def speichere_meta(fid: str, m: dict) -> None:
    store.schreibe(f"funds/{fid}/meta.json", m)


def erzeuge_falls_noetig(defn: dict, fx_usd_je_eur: float, jetzt: float | None = None) -> dict | None:
    """Legt Portfolio+Meta beim ersten Mal an (Startkapital 10.000 € in USD zum aktuellen Kurs)."""
    pf = lade_portfolio(defn["id"])
    if pf:
        return pf
    if not liga_hat_schluessel(defn):
        return None
    jetzt = jetzt or time.time()
    start_usd = config.load()["start_kapital_eur"] * fx_usd_je_eur
    pf = portfolio.neu(defn["id"], start_usd, jetzt)
    pf["start_fx"] = fx_usd_je_eur
    speichere_portfolio(pf)
    speichere_meta(defn["id"], {k: v for k, v in defn.items()} | {"start": jetzt})
    return pf


def risikoprofil(defn: dict) -> dict:
    if defn["typ"] == "benchmark":
        return UNBEGRENZT
    return config.load()["risiko"][defn["risiko"]]
