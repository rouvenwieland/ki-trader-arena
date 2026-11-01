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
    return {"id": f"stock:{sym.upper()}", "art": "stock", "venue": "yahoo", "symbol": sym.upper()}


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


def fx_usd(waehrung: str | None) -> float | None:
    """USD je Einheit der Kurswährung (Yahoo-Devisenkurs, 10 min zwischengespeichert). GBp/ZAc = Pence/Cent."""
    w = (waehrung or "USD").strip()
    teiler = 100.0 if w in ("GBp", "GBX", "ZAc", "ILA") else 1.0
    w = {"GBp": "GBP", "GBX": "GBP", "ZAc": "ZAR", "ILA": "ILS"}.get(w, w).upper()
    if w == "USD":
        return 1.0 / teiler
    try:
        m = get(YAHOO + f"{w}USD=X", {"range": "1d", "interval": "1h"}, ttl=600, versuche=2)["chart"]["result"][0]["meta"]
        return float(m["regularMarketPrice"]) / teiler
    except (HttpFehler, KeyError, IndexError, TypeError, ValueError):
        return None


def _meta(sym: str) -> dict | None:
    try:
        return get(YAHOO + sym, {"range": "1d", "interval": "5m"}, ttl=120, versuche=2)["chart"]["result"][0]
    except (HttpFehler, KeyError, IndexError, TypeError):
        return None


def kurs(sym: str) -> dict | None:
    """Kurs in USD für JEDEN Yahoo-Ticker (US, Europa, Asien, OTC …). Offen = innerhalb der regulären Handelszeit dieser Börse
    (laut Yahoo) und letzter Kurs jünger als 20 min. Fremdwährungen werden zum aktuellen Devisenkurs in USD umgerechnet."""
    d = _meta(sym)
    if not d:
        return None
    meta = d["meta"]
    px, t = meta.get("regularMarketPrice"), meta.get("regularMarketTime")
    if px is None:
        return None
    w = meta.get("currency") or "USD"
    fx = fx_usd(w)
    if fx is None:
        return None
    reg = (meta.get("currentTradingPeriod") or {}).get("regular") or {}
    jetzt = time.time()
    in_zeit = reg.get("start", 0) <= jetzt < reg.get("end", 0) if reg else boerse_offen()
    vortag = meta.get("chartPreviousClose") or meta.get("previousClose")
    return {"preis": float(px) * fx, "zeit": t, "offen": bool(in_zeit and t and jetzt - t < 20 * 60),
            "vortag": vortag * fx if vortag else None, "aenderung_pct": round((float(px) / vortag - 1) * 100, 2) if vortag else None,
            "waehrung": w, "preis_lokal": float(px), "boerse": meta.get("exchangeName"), "zeitzone": meta.get("exchangeTimezoneName"),
            "handelszeit": reg, "typ": meta.get("instrumentType")}


def naechste_oeffnung_symbol(sym: str, ts: float | None = None) -> float:
    """Nächste reguläre Eröffnung der Börse dieses Tickers (US: NYSE-Kalender; sonst gleiche Uhrzeit am nächsten Werktag)."""
    ts = ts or time.time()
    k = kurs(sym) or {}
    reg = k.get("handelszeit") or {}
    if k.get("zeitzone", NY) == NY or not reg.get("start"):
        return naechste_oeffnung(ts)
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(k["zeitzone"])
    start = datetime.fromtimestamp(reg["start"], tz)
    for i in range(0, 10):
        kand = start + timedelta(days=i)
        if kand.timestamp() > ts and kand.weekday() < 5:
            return kand.timestamp()
    return ts + 86400


def schluss_nach(sym: str, ts: float) -> float:
    """Handelsschluss des Tages, an dem die Börse dieses Tickers nach `ts` öffnet."""
    k = kurs(sym) or {}
    reg = k.get("handelszeit") or {}
    oeff = naechste_oeffnung_symbol(sym, ts)
    dauer = (reg["end"] - reg["start"]) if reg.get("start") and reg.get("end") else 6.5 * 3600
    return max(oeff, ts) + dauer


def suche(q: str, n: int = 10) -> list[dict]:
    """Ticker-Suche (Aktien, ETFs, weltweit) über die öffentliche Yahoo-Suche."""
    try:
        d = get("https://query1.finance.yahoo.com/v1/finance/search", {"q": q, "quotesCount": n, "newsCount": 0}, ttl=3600, versuche=2)
    except HttpFehler:
        return []
    return [{"instrument_id": f"stock:{x['symbol']}", "name": x.get("shortname") or x.get("longname"), "boerse": x.get("exchDisp") or x.get("exchange"),
             "typ": x.get("quoteType")} for x in d.get("quotes", []) if x.get("symbol") and x.get("quoteType") in ("EQUITY", "ETF", "MUTUALFUND", "INDEX")]


def tagesvolumen_sigma(sym: str) -> tuple[float | None, float | None]:
    """Mittleres Tagesvolumen in USD (20 Tage) und Tagesvolatilität der Schlusskurse – für Spread und Impact."""
    try:
        d = get(YAHOO + sym, {"range": "1mo", "interval": "1d"}, ttl=3600, versuche=1)["chart"]["result"][0]
        q = d["indicators"]["quote"][0]
        paare = [(c, v) for c, v in zip(q["close"], q["volume"]) if c and v]
        fx = fx_usd(d["meta"].get("currency")) or 1.0
    except (HttpFehler, KeyError, IndexError, TypeError):
        return None, None
    if len(paare) < 5:
        return None, None
    vol = sum(c * v for c, v in paare) / len(paare) * fx
    r = [math.log(b[0] / a[0]) for a, b in zip(paare, paare[1:])]
    m = sum(r) / len(r)
    return vol, math.sqrt(sum((x - m) ** 2 for x in r) / max(1, len(r) - 1))


def halb_spread(vol_tag_usd: float | None) -> float:
    """Halber Geld-Brief-Abstand nach Liquidität: Mega-Caps ≈ 1 bp, Nebenwerte/OTC deutlich mehr (gedeckelt bei 2,5 %)."""
    basis = config.load()["boerse"]["gebuehren"]["stock_spread_bps"] / 2e4
    if not vol_tag_usd:
        return max(basis, 0.0025)
    return min(0.025, max(basis, 5e-4 * math.sqrt(1e8 / vol_tag_usd)))


def buch(sym: str) -> Book | None:
    """Synthetisches Buch (Kurse in USD): liquiditätsabhängiger Halb-Spread plus Tiefe nach dem Square-Root-Gesetz."""
    k = kurs(sym)
    if not k:
        return None
    if not k["offen"]:
        return Book([], [], time.time(), mark=k["preis"])  # Börse geschlossen → kein Handel (Auftrag wird vorgemerkt)
    from arena.exchange import impact
    px = k["preis"]
    vol, sigma = tagesvolumen_sigma(sym)
    h = halb_spread(vol)
    stufen_usd = [25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000, 2_500_000, 5_000_000]
    asks, bids, vorher = [], [], 0.0
    for kum in stufen_usd:
        q = (kum - vorher) / px
        imp = impact.sqrt_impact(kum / px, px, vol, sigma) if vol else 1e-4 * kum / 50_000
        asks.append((px * (1 + h + imp), q))
        bids.append((px * (1 - h - imp), q))
        vorher = kum
    return Book(bids, asks, time.time(), mark=px)


def extreme(sym: str, seit: float) -> tuple[float, float] | None:
    """Tief/Hoch (USD) aus 5-Minuten-Kerzen seit `seit` – für Stops und Limit-Orders während des Handelstags."""
    try:
        d = get(YAHOO + sym, {"range": "5d", "interval": "5m"}, ttl=120, versuche=1)["chart"]["result"][0]
        q = d["indicators"]["quote"][0]
        fx = fx_usd(d["meta"].get("currency"))
        werte = [(lo, hi) for t, lo, hi in zip(d["timestamp"], q["low"], q["high"]) if t >= seit - 300 and lo and hi]
    except (HttpFehler, KeyError, IndexError, TypeError):
        return None
    if not werte or not fx:
        return None
    return min(w[0] for w in werte) * fx, max(w[1] for w in werte) * fx


def tagesschluesse(sym: str, bereich: str = "1y") -> list[tuple[float, float]]:
    try:
        d = get(YAHOO + sym, {"range": bereich, "interval": "1d"}, ttl=3600, versuche=1)["chart"]["result"][0]
        fx = fx_usd(d["meta"].get("currency")) or 1.0
        return [(t, c * fx) for t, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]) if c is not None]
    except (HttpFehler, KeyError, IndexError, TypeError):
        return []
