"""Themen-Etiketten für Instrumente (deterministisch, ohne LLM): Grundlage für Cluster-Limits, Policy-Gate und Gleichlauf-Kennzahlen."""
from __future__ import annotations

import re

THEMEN = {
    "krypto": {"bitcoin", "btc", "ethereum", "eth", "solana", "sol", "crypto", "xrp", "doge", "dogecoin", "stablecoin", "coinbase",
               "binance", "microstrategy", "token", "halving", "altcoin", "memecoin"},
    "zinsen_makro": {"fed", "fomc", "rate", "rates", "interest", "inflation", "cpi", "pce", "gdp", "unemployment", "jobs", "payrolls",
                     "recession", "ecb", "treasury", "yield", "tariff", "tariffs", "economy", "powell", "bps"},
    "wetter": {"temperature", "weather", "hurricane", "rain", "snow", "storm", "degrees", "°f", "highest", "lowest", "tmax", "heat"},
    "wahlen_politik": {"election", "elections", "president", "presidential", "senate", "house", "governor", "prime", "minister",
                       "democrat", "democrats", "republican", "republicans", "party", "vote", "poll", "midterm", "midterms", "mayor",
                       "parliament", "trump", "vance", "nominee", "congress"},
    "geopolitik": {"war", "ceasefire", "iran", "israel", "russia", "ukraine", "china", "taiwan", "nato", "strike", "invasion",
                   "regime", "sanctions", "military", "gaza", "netanyahu", "putin", "missile"},
    "sport": {"nba", "nfl", "mlb", "nhl", "soccer", "football", "premier", "champions", "league", "cup", "match", "game", "vs",
              "tennis", "open", "worlds", "counter-strike", "dota", "lol", "esports", "ufc", "f1", "grand", "prix", "bo3", "bo5"},
    "tech_unternehmen": {"nvidia", "apple", "microsoft", "tesla", "openai", "google", "meta", "amazon", "earnings", "ai", "spacex",
                         "launch", "ipo", "stock", "shares", "market cap", "gpt", "anthropic", "chip"},
    "kultur": {"oscar", "box", "album", "movie", "film", "grammy", "song", "spotify", "billboard", "netflix", "award"},
}
REIHENFOLGE = ["wetter", "krypto", "zinsen_makro", "sport", "wahlen_politik", "geopolitik", "tech_unternehmen", "kultur"]


def aus_text(text: str) -> str:
    w = set(re.findall(r"[a-z0-9°\-]+", (text or "").lower()))
    best, best_n = "sonstige", 0
    for t in REIHENFOLGE:  # Reihenfolge entscheidet bei Gleichstand (spezifischer zuerst)
        n = len(w & THEMEN[t])
        if n > best_n:
            best, best_n = t, n
    return best


def thema(inst: dict) -> str:
    """Thema einer Position: Wettmärkte nach Frage, Krypto/Perps/Optionen = krypto, Aktien = aktien bzw. anleihen_gold."""
    art = inst.get("art")
    if art == "pm":
        return aus_text(inst.get("frage", ""))
    if art in ("spot", "perp", "option"):
        return "krypto"
    if art == "stock":
        return "anleihen_gold" if inst.get("symbol") in ("TLT", "AGG", "GLD") else "aktien"
    return "sonstige"


def wette_kategorie(inst: dict) -> str:
    """Kategorie fürs Policy-Gate: Art + Thema, bei Wetten auch die Seite (JA/NEIN), bei Perps die Richtung."""
    art = inst.get("art", "?")
    if art == "pm":
        return f"wette:{thema(inst)}:{inst.get('ergebnis', 'JA')}"
    return f"{art}:{thema(inst)}"
