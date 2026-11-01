"""Krypto: Spot (Coinbase), Perps und Optionen (Deribit public), Fallbacks Kraken/CoinGecko.

Binance/Bybit sperren US-IPs (GitHub-Runner) → nicht verwendet."""
from __future__ import annotations

import math
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


# ------------------------------------------------------------------ Deribit: Volatilitätsregime, exaktes Funding, Basis
def funding_wert(name: str, seit: float, bis: float) -> float | None:
    """Tatsächlich angefallenes Funding (Anteil des Nominals) zwischen seit und bis – exakt statt 8-h-Mittel × Zeit."""
    try:
        return float(get(f"{DERIBIT}/get_funding_rate_value", {"instrument_name": name, "start_timestamp": int(seit * 1000),
                                                               "end_timestamp": int(bis * 1000)})["result"])
    except (HttpFehler, KeyError, TypeError, ValueError):
        return None


def dvol(basis: str = "BTC") -> dict | None:
    """Deribit-Volatilitätsindex (implizite 30-Tage-Vola in %): aktuell, vor 24 h, Spanne der letzten 7 Tage."""
    ende = int(time.time() * 1000)
    try:
        d = get(f"{DERIBIT}/get_volatility_index_data", {"currency": basis, "resolution": 3600, "start_timestamp": ende - 7 * 86400 * 1000,
                                                          "end_timestamp": ende}, ttl=600)["result"]["data"]
    except (HttpFehler, KeyError, TypeError):
        return None
    if not d:
        return None
    schluss = [x[4] for x in d]
    vor24 = schluss[-25] if len(schluss) >= 25 else schluss[0]
    return {"dvol": schluss[-1], "vor_24h": vor24, "min_7t": min(x[3] for x in d), "max_7t": max(x[2] for x in d),
            "tagesbewegung_1sigma_pct": round(schluss[-1] / math.sqrt(365), 2)}


def basis_kurve(basis: str = "BTC") -> list[dict]:
    """Annualisierte Basis der Deribit-Terminkontrakte gegen den Index (Contango/Backwardation = Hebelnachfrage)."""
    try:
        r = get(f"{DERIBIT}/get_book_summary_by_currency", {"currency": basis, "kind": "future"}, ttl=300)["result"]
    except (HttpFehler, KeyError):
        return []
    out = []
    for x in r:
        m = re.fullmatch(r"[A-Z]+-(\d{1,2})([A-Z]{3})(\d{2})", x.get("instrument_name", ""))
        if not m or not x.get("mark_price") or not x.get("estimated_delivery_price"):
            continue
        verfall = datetime(2000 + int(m.group(3)), _MON[m.group(2)], int(m.group(1)), 8, tzinfo=timezone.utc).timestamp()
        tage = (verfall - time.time()) / 86400
        if tage < 3:
            continue
        b = x["mark_price"] / x["estimated_delivery_price"] - 1
        out.append({"kontrakt": x["instrument_name"], "tage": round(tage), "basis_pct": round(100 * b, 3),
                    "annualisiert_pct": round(100 * b * 365 / tage, 2), "oi_usd": x.get("open_interest")})
    return sorted(out, key=lambda y: y["tage"])


# ------------------------------------------------------------------ Optionskette mit Griechen
def _bs(S: float, K: float, T: float, iv: float, typ: str) -> dict:
    """Black-Scholes (r = 0) für Delta, Gamma, Vega (USD je 1 Vola-Punkt), Theta (USD je Tag)."""
    from statistics import NormalDist
    N = NormalDist()
    if T <= 0 or iv <= 0 or S <= 0 or K <= 0:
        return {}
    s = iv * math.sqrt(T)
    d1 = (math.log(S / K) + 0.5 * s * s) / s
    pdf = math.exp(-0.5 * d1 * d1) / math.sqrt(2 * math.pi)
    delta = N.cdf(d1) if typ == "C" else N.cdf(d1) - 1
    return {"delta": round(delta, 3), "gamma": S * pdf / (S * s) / S, "vega_usd": round(S * pdf * math.sqrt(T) / 100, 2),
            "theta_usd_tag": round(-S * pdf * iv / (2 * math.sqrt(T)) / 365, 2)}


def optionskette(basis: str = "BTC", verfall: str | None = None, spanne: float = 0.3) -> dict:
    """Alle Deribit-Optionen eines Basiswerts: ohne `verfall` die Liste der Laufzeiten, mit `verfall` (z. B. 27NOV26) alle Strikes
    innerhalb ±spanne um den Kurs mit Geld/Brief/Mark in USD, IV, Griechen und Open Interest."""
    try:
        r = get(f"{DERIBIT}/get_book_summary_by_currency", {"currency": basis, "kind": "option"}, ttl=120)["result"]
    except (HttpFehler, KeyError):
        return {"fehler": "Deribit nicht erreichbar"}
    jetzt = time.time()
    laufzeiten: dict[str, int] = {}
    zeilen = []
    for o in r:
        p = parse_option(o["instrument_name"])
        if not p or not o.get("underlying_price"):
            continue
        tag = o["instrument_name"].split("-")[1]
        laufzeiten[tag] = laufzeiten.get(tag, 0) + 1
        if verfall and tag != verfall.upper():
            continue
        S = o["underlying_price"]
        if not verfall or abs(p["strike"] / S - 1) > spanne:
            continue
        T = (p["verfall"] - jetzt) / (365 * 86400)
        iv = (o.get("mark_iv") or 0) / 100
        z = {"id": f"opt:{o['instrument_name']}", "typ": p["typ"], "strike": p["strike"], "tage": round(T * 365, 1),
             "bid_usd": round(o["bid_price"] * S, 2) if o.get("bid_price") else None, "ask_usd": round(o["ask_price"] * S, 2) if o.get("ask_price") else None,
             "mark_usd": round(o["mark_price"] * S, 2) if o.get("mark_price") is not None else None, "iv_pct": o.get("mark_iv"),
             "oi": o.get("open_interest"), "basis_usd": round(S, 2)}
        zeilen.append(z | _bs(S, p["strike"], T, iv, p["typ"]))
    if not verfall:
        return {"basis": basis, "laufzeiten": dict(sorted(laufzeiten.items(), key=lambda kv: parse_option(f"{basis}-{kv[0]}-1-C")["verfall"])),
                "hinweis": "Mit verfall=… (z. B. 27NOV26) die Strikes mit Griechen abrufen."}
    zeilen.sort(key=lambda z: (z["strike"], z["typ"]))
    for z in zeilen:
        z.pop("gamma", None)
    return {"basis": basis, "verfall": verfall.upper(), "optionen": zeilen,
            "marge_verkauf": "Schreiben: Anfangsmarge je Kontrakt ≈ Mark + max(15 % · Basis − Aus-dem-Geld-Betrag, 10 % · Basis); Wartung 7,5 % · Basis."}
