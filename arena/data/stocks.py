"""Aktien/ETFs über Yahoo Finance (öffentlicher Chart-Endpunkt, ohne Login).
Kein Orderbuch verfügbar → synthetisches Buch aus Kurs ± Halb-Spread. Stooq verlangt einen
JavaScript-Nachweis (Anti-Bot) und wird deshalb nicht genutzt (keine Umgehung)."""
from __future__ import annotations

import time

from arena import config
from arena.data.http import HttpFehler, get
from arena.exchange.book import Book

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/"


def inst(sym: str) -> dict:
    return {"id": f"stock:{sym}", "art": "stock", "venue": "yahoo", "symbol": sym}


def kurs(sym: str) -> dict | None:
    try:
        d = get(YAHOO + sym, {"range": "1d", "interval": "5m"}, ttl=120)["chart"]["result"][0]
    except (HttpFehler, KeyError, IndexError, TypeError):
        return None
    meta = d["meta"]
    px, t = meta.get("regularMarketPrice"), meta.get("regularMarketTime")
    if px is None:
        return None
    return {"preis": float(px), "zeit": t, "offen": bool(t) and time.time() - t < 20 * 60,
            "vortag": meta.get("chartPreviousClose")}


def buch(sym: str) -> Book | None:
    k = kurs(sym)
    if not k:
        return None
    if not k["offen"]:
        return Book([], [], time.time(), mark=k["preis"])  # Börse geschlossen → kein Handel
    h = config.load()["boerse"]["gebuehren"]["stock_spread_bps"] / 2e4
    px = k["preis"]
    return Book([(px * (1 - h), 1e6)], [(px * (1 + h), 1e6)], time.time(), mark=px)


def tagesschluesse(sym: str, bereich: str = "1y") -> list[tuple[float, float]]:
    try:
        d = get(YAHOO + sym, {"range": bereich, "interval": "1d"}, ttl=3600)["chart"]["result"][0]
        return [(t, c) for t, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]) if c is not None]
    except (HttpFehler, KeyError, IndexError, TypeError):
        return []
