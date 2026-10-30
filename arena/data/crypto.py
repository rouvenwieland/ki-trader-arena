"""Krypto: Spot (Coinbase), Perps und Optionen (Deribit public), Fallbacks Kraken/CoinGecko.

Binance/Bybit sperren US-IPs (GitHub-Runner) → nicht verwendet."""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone

from arena import config
from arena.data.http import HttpFehler, get
from arena.exchange.book import Book

CB = "https://api.exchange.coinbase.com"
DERIBIT = "https://www.deribit.com/api/v2/public"
KRAKEN = "https://api.kraken.com/0/public"
KRAKEN_PAAR = {"BTC": "XBTUSD", "ETH": "ETHUSD", "SOL": "SOLUSD", "XRP": "XRPUSD", "DOGE": "DOGEUSD",
               "ADA": "ADAUSD", "LINK": "LINKUSD", "AVAX": "AVAXUSD"}


def spot_inst(sym: str) -> dict:
    return {"id": f"spot:{sym}-USD", "art": "spot", "venue": "coinbase", "symbol": f"{sym}-USD"}


def perp_inst(name: str) -> dict:
    return {"id": f"perp:{name}", "art": "perp", "venue": "deribit", "symbol": name}


# ------------------------------------------------------------------ Spot
def spot_ticker(sym: str) -> dict | None:
    try:
        t = get(f"{CB}/products/{sym}-USD/ticker")
        return {"bid": float(t["bid"]), "ask": float(t["ask"]), "last": float(t["price"]), "vol24": float(t["volume"])}
    except (HttpFehler, KeyError, ValueError):
        pass
    try:  # Fallback Kraken
        r = get(f"{KRAKEN}/Ticker", {"pair": KRAKEN_PAAR[sym]})["result"]
        t = next(iter(r.values()))
        return {"bid": float(t["b"][0]), "ask": float(t["a"][0]), "last": float(t["c"][0]), "vol24": float(t["v"][1])}
    except (HttpFehler, KeyError, ValueError, StopIteration):
        return None


def spot_buch(sym: str) -> Book:
    try:
        d = get(f"{CB}/products/{sym}/book", {"level": 2})
        return Book([(float(p), float(s)) for p, s, *_ in d["bids"]], [(float(p), float(s)) for p, s, *_ in d["asks"]], time.time())
    except HttpFehler:
        base = sym.split("-")[0]
        r = next(iter(get(f"{KRAKEN}/Depth", {"pair": KRAKEN_PAAR[base], "count": 50})["result"].values()))
        return Book([(float(p), float(s)) for p, s, _ in r["bids"]], [(float(p), float(s)) for p, s, _ in r["asks"]], time.time())


def spot_extreme(sym: str, seit: float) -> tuple[float, float] | None:
    """Tief/Hoch seit `seit` (Unix) aus 1-Minuten-Kerzen – damit Dochte Stops und Liquidationen auslösen."""
    ende = time.time()
    seit = max(seit, ende - 280 * 60)
    try:
        k = get(f"{CB}/products/{sym}/candles", {"granularity": 60,
                "start": datetime.fromtimestamp(seit, timezone.utc).isoformat(),
                "end": datetime.fromtimestamp(ende, timezone.utc).isoformat()})
    except HttpFehler:
        return None
    if not k:
        return None
    return min(c[1] for c in k), max(c[2] for c in k)


def spot_kerzen(sym: str, granularitaet: int = 3600, n: int = 300) -> list[list[float]]:
    """[[zeit, tief, hoch, offen, schluss, volumen], ...] aufsteigend nach Zeit."""
    try:
        k = get(f"{CB}/products/{sym}/candles", {"granularity": granularitaet}, ttl=300)
    except HttpFehler:
        return []
    return sorted(k)[-n:]


# ------------------------------------------------------------------ Deribit Perps
def perp_ticker(name: str) -> dict | None:
    try:
        t = get(f"{DERIBIT}/ticker", {"instrument_name": name})["result"]
        return {"mark": t["mark_price"], "index": t["index_price"], "bid": t.get("best_bid_price"),
                "ask": t.get("best_ask_price"), "funding_8h": t.get("funding_8h", 0.0), "oi": t.get("open_interest")}
    except (HttpFehler, KeyError):
        return None


def perp_buch(name: str, tiefe: int = 20) -> Book:
    d = get(f"{DERIBIT}/get_order_book", {"instrument_name": name, "depth": tiefe})["result"]
    return Book([(float(p), float(s)) for p, s in d["bids"]], [(float(p), float(s)) for p, s in d["asks"]],
                time.time(), mark=d.get("mark_price"))


def perp_extreme(name: str, seit: float) -> tuple[float, float] | None:
    try:
        d = get(f"{DERIBIT}/get_tradingview_chart_data", {"instrument_name": name, "resolution": 1,
                "start_timestamp": int(seit * 1000), "end_timestamp": int(time.time() * 1000)})["result"]
        if d.get("low"):
            return min(d["low"]), max(d["high"])
    except (HttpFehler, KeyError):
        pass
    return None


# ------------------------------------------------------------------ Deribit Optionen (nur Long gekauft)
_MON = {m: i + 1 for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAI" if False else "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}


def parse_option(name: str) -> dict | None:
    m = re.fullmatch(r"([A-Z]+)-(\d{1,2})([A-Z]{3})(\d{2})-(\d+)-([CP])", name)
    if not m:
        return None
    basis, tag, mon, jahr, strike, typ = m.groups()
    verfall = datetime(2000 + int(jahr), _MON[mon], int(tag), 8, 0, tzinfo=timezone.utc).timestamp()
    return {"basis": basis, "verfall": verfall, "strike": float(strike), "typ": typ}


def option_inst(name: str) -> dict:
    p = parse_option(name)
    return {"id": f"opt:{name}", "art": "option", "venue": "deribit", "symbol": name, **p, "schliesst": p["verfall"]}


def optionen_universum(basis: str = "BTC", n: int = 12) -> list[dict]:
    """Liquide Optionen nahe am Geld mit 5–90 Tagen Restlaufzeit."""
    try:
        s = get(f"{DERIBIT}/get_book_summary_by_currency", {"currency": basis, "kind": "option"}, ttl=60)["result"]
    except (HttpFehler, KeyError):
        return []
    jetzt = time.time()
    out = []
    for o in s:
        p = parse_option(o["instrument_name"])
        if not p or not o.get("underlying_price") or o.get("mark_price") is None:
            continue
        tage = (p["verfall"] - jetzt) / 86400
        abst = abs(p["strike"] / o["underlying_price"] - 1)
        if not (5 <= tage <= 90) or abst > 0.15 or not o.get("bid_price") or not o.get("ask_price"):
            continue
        idx = o["underlying_price"]
        out.append({"inst": option_inst(o["instrument_name"]), "bid": o["bid_price"] * idx, "ask": o["ask_price"] * idx,
                    "mark": o["mark_price"] * idx, "iv": o.get("mark_iv"), "oi": o.get("open_interest", 0),
                    "index": idx, "tage": round(tage, 1)})
    out.sort(key=lambda x: -x["oi"])
    return out[:n]


def option_buch(name: str) -> tuple[Book, float]:
    """Orderbuch in USD je Einheit; zweiter Rückgabewert: Indexpreis."""
    d = get(f"{DERIBIT}/get_order_book", {"instrument_name": name, "depth": 10})["result"]
    idx = d["index_price"]
    return (Book([(p * idx, s) for p, s in d["bids"]], [(p * idx, s) for p, s in d["asks"]], time.time(),
                 mark=d["mark_price"] * idx), idx)


def abrechnungspreis(basis: str, verfall: float) -> float | None:
    """Deribit-Lieferpreis (Tagesindex um 08:00 UTC) nach Verfall."""
    try:
        d = get(f"{DERIBIT}/get_delivery_prices", {"index_name": f"{basis.lower()}_usd", "count": 30}, ttl=600)["result"]["data"]
    except (HttpFehler, KeyError):
        return None
    tag = datetime.fromtimestamp(verfall, timezone.utc).strftime("%Y-%m-%d")
    for x in d:
        if x["date"] == tag:
            return float(x["delivery_price"])
    return None


# ------------------------------------------------------------------ Fremdwährung
def usd_je_eur() -> float:
    try:
        return float(get("https://api.coinbase.com/v2/exchange-rates", {"currency": "EUR"}, ttl=600)["data"]["rates"]["USD"])
    except (HttpFehler, KeyError, ValueError):
        return config.load()["fallback_usd_je_eur"]
