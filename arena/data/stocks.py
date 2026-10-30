"""Aktien/ETFs über Yahoo Finance (öffentlicher Chart-Endpunkt, ohne Login).
Kein Orderbuch verfügbar → synthetisches Buch aus Kurs ± Halb-Spread. Stooq verlangt einen
JavaScript-Nachweis (Anti-Bot) und wird deshalb nicht genutzt (keine Umgehung)."""
from __future__ import annotations

import math
import time

from arena import config
from arena.data.http import HttpFehler, get
from arena.exchange.book import Book

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/"


def inst(sym: str) -> dict:
    return {"id": f"stock:{sym}", "art": "stock", "venue": "yahoo", "symbol": sym}


def kurs(sym: str) -> dict | None:
    try:
        d = get(YAHOO + sym, {"range": "1d", "interval": "5m"}, ttl=120, versuche=1)["chart"]["result"][0]
    except (HttpFehler, KeyError, IndexError, TypeError):
        return None
    meta = d["meta"]
    px, t = meta.get("regularMarketPrice"), meta.get("regularMarketTime")
    if px is None:
        return None
    return {"preis": float(px), "zeit": t, "offen": bool(t) and time.time() - t < 20 * 60,
            "vortag": meta.get("chartPreviousClose")}


def tagesvolumen_sigma(sym: str) -> tuple[float | None, float | None]:
    """Mittleres Tagesvolumen in USD (20 Tage) und Tagesvolatilität der Schlusskurse – für das Impact-Modell."""
    try:
        d = get(YAHOO + sym, {"range": "1mo", "interval": "1d"}, ttl=3600, versuche=1)["chart"]["result"][0]
        q = d["indicators"]["quote"][0]
        paare = [(c, v) for c, v in zip(q["close"], q["volume"]) if c and v]
    except (HttpFehler, KeyError, IndexError, TypeError):
        return None, None
    if len(paare) < 5:
        return None, None
    vol = sum(c * v for c, v in paare) / len(paare)
    r = [math.log(b[0] / a[0]) for a, b in zip(paare, paare[1:])]
    m = sum(r) / len(r)
    return vol, math.sqrt(sum((x - m) ** 2 for x in r) / max(1, len(r) - 1))


def buch(sym: str) -> Book | None:
    """Synthetisches Buch: Halb-Spread plus Tiefe nach dem Square-Root-Gesetz (große Orders werden teurer); ohne Volumendaten
    eine konservative Treppe (+1 bp je 50.000 USD)."""
    k = kurs(sym)
    if not k:
        return None
    if not k["offen"]:
        return Book([], [], time.time(), mark=k["preis"])  # Börse geschlossen → kein Handel
    from arena.exchange import impact
    h = config.load()["boerse"]["gebuehren"]["stock_spread_bps"] / 2e4
    px = k["preis"]
    vol, sigma = tagesvolumen_sigma(sym)
    stufen_usd = [25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000, 2_500_000, 5_000_000]
    asks, bids, vorher = [], [], 0.0
    for i, kum in enumerate(stufen_usd):
        q = (kum - vorher) / px
        imp = impact.sqrt_impact(kum / px, px, vol, sigma) if vol else 1e-4 * kum / 50_000
        asks.append((px * (1 + h + imp), q))
        bids.append((px * (1 - h - imp), q))
        vorher = kum
    return Book(bids, asks, time.time(), mark=px)


def tagesschluesse(sym: str, bereich: str = "1y") -> list[tuple[float, float]]:
    try:
        d = get(YAHOO + sym, {"range": bereich, "interval": "1d"}, ttl=3600, versuche=1)["chart"]["result"][0]
        return [(t, c) for t, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]) if c is not None]
    except (HttpFehler, KeyError, IndexError, TypeError):
        return []
