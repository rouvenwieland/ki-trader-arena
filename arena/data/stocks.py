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


# NYSE: Mo–Fr 9:30–16:00 New York; Feiertage 2026/27 (vollständige Schließtage; verkürzte Tage werden wie normale behandelt)
NY = "America/New_York"
FEIERTAGE = {"2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31", "2027-06-18",
             "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24"}


def boerse_offen(ts: float | None = None) -> bool:
    from datetime import datetime
    from zoneinfo import ZoneInfo
    d = datetime.fromtimestamp(ts or time.time(), ZoneInfo(NY))
    if d.weekday() >= 5 or d.strftime("%Y-%m-%d") in FEIERTAGE:
        return False
    m = d.hour * 60 + d.minute
    return 9 * 60 + 30 <= m < 16 * 60


def naechste_oeffnung(ts: float | None = None) -> float:
    """Unix-Zeit der nächsten regulären Eröffnung (bzw. jetzt, wenn offen)."""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    ts = ts or time.time()
    if boerse_offen(ts):
        return ts
    d = datetime.fromtimestamp(ts, ZoneInfo(NY))
    for i in range(10):
        tag = (d + timedelta(days=i)).replace(hour=9, minute=30, second=0, microsecond=0)
        if tag.timestamp() > ts and tag.weekday() < 5 and tag.strftime("%Y-%m-%d") not in FEIERTAGE:
            return tag.timestamp()
    return ts + 86400


def naechster_schluss(ts: float | None = None) -> float:
    from datetime import datetime
    from zoneinfo import ZoneInfo
    start = naechste_oeffnung(ts)
    d = datetime.fromtimestamp(start, ZoneInfo(NY))
    return d.replace(hour=16, minute=0, second=0, microsecond=0).timestamp()


def kurs(sym: str) -> dict | None:
    try:
        d = get(YAHOO + sym, {"range": "1d", "interval": "5m"}, ttl=120, versuche=1)["chart"]["result"][0]
    except (HttpFehler, KeyError, IndexError, TypeError):
        return None
    meta = d["meta"]
    px, t = meta.get("regularMarketPrice"), meta.get("regularMarketTime")
    if px is None:
        return None
    vortag = meta.get("chartPreviousClose") or meta.get("previousClose")
    return {"preis": float(px), "zeit": t, "offen": boerse_offen() and bool(t) and time.time() - t < 20 * 60,
            "vortag": vortag, "aenderung_pct": round((float(px) / vortag - 1) * 100, 2) if vortag else None}


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
