"""Wettmärkte (nur lesend): Polymarket, Kalshi, PredictIt, Manifold.

Normalisierter Markt: {mid, venue, frage, schliesst, ja_bid, ja_ask, volumen_24h, liquiditaet, url, ref}
mid z. B. "pm:polymarket:562803". Instrument-IDs hängen :JA bzw. :NEIN an."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from arena import config
from arena.data.http import HttpFehler, get
from arena.exchange.book import Book


def _ts(s: str | None) -> float | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _f(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def inst(markt: dict, ergebnis: str) -> dict:
    return {"id": f"{markt['mid']}:{ergebnis}", "art": "pm", "venue": markt["venue"], "ergebnis": ergebnis,
            "frage": markt["frage"], "schliesst": markt.get("schliesst"), "ref": markt["ref"], "url": markt.get("url")}


def inst_aus_id(inst_id: str, ref: dict | None = None) -> dict:
    """Minimal-Instrument aus ID (für Bewertung von Altpositionen); ref nötig fürs Orderbuch."""
    _, venue, rest = inst_id.split(":", 2)
    mid, erg = rest.rsplit(":", 1)
    return {"id": inst_id, "art": "pm", "venue": venue, "ergebnis": erg, "ref": ref or {}, "mid": f"pm:{venue}:{mid}"}


# ---------------------------------------------------------------- Polymarket
def _norm_poly(m: dict) -> dict | None:
    try:
        toks = json.loads(m.get("clobTokenIds") or "[]")
        outs = json.loads(m.get("outcomes") or "[]")
        if len(toks) != 2 or [o.lower() for o in outs] != ["yes", "no"] or not m.get("enableOrderBook"):
            return None
        bid, ask = _f(m.get("bestBid")), _f(m.get("bestAsk"))
        if bid is None or ask is None:
            return None
        return {"mid": f"pm:polymarket:{m['id']}", "venue": "polymarket", "frage": m["question"],
                "schliesst": _ts(m.get("endDate")), "ja_bid": bid, "ja_ask": ask,
                "volumen_24h": _f(m.get("volume24hr"), 0), "liquiditaet": _f(m.get("liquidityNum"), 0),
                "beschreibung": (m.get("description") or "")[:1500],
                "url": f"https://polymarket.com/event/{(m.get('events') or [{}])[0].get('slug', m.get('slug'))}",
                "ref": {"id": m["id"], "token_ja": toks[0], "token_nein": toks[1], "tick": m.get("orderPriceMinTickSize", 0.01),
                        "gebuehr_rate": _f((m.get("feeSchedule") or {}).get("rate"), 0)}}
    except (KeyError, ValueError):
        return None


def polymarket(n: int) -> list[dict]:
    daten = get("https://gamma-api.polymarket.com/markets",
                {"limit": n * 2, "active": "true", "closed": "false", "order": "volume24hr", "ascending": "false"}, ttl=60)
    return [x for x in (_norm_poly(m) for m in daten) if x]


def polymarket_suche(q: str, n: int = 8) -> list[dict]:
    d = get("https://gamma-api.polymarket.com/public-search", {"q": q, "limit_per_type": n, "events_status": "active"}, ttl=120)
    out = []
    for ev in d.get("events", []):
        for m in ev.get("markets", []):
            if m.get("closed") or not m.get("enableOrderBook"):
                continue
            x = _norm_poly(m)
            if x:
                out.append(x)
    return out[:n]


def polymarket_buch(ref: dict, ergebnis: str) -> Book:
    tok = ref["token_ja"] if ergebnis == "JA" else ref["token_nein"]
    d = get("https://clob.polymarket.com/book", {"token_id": tok})
    bids = sorted(((float(x["price"]), float(x["size"])) for x in d["bids"]), reverse=True)
    asks = sorted((float(x["price"]), float(x["size"])) for x in d["asks"])
    return Book(bids, asks, time.time())


def polymarket_aufloesung(ref: dict) -> float | None:
    m = get("https://gamma-api.polymarket.com/markets/" + str(ref["id"]))
    if not m.get("closed"):
        return None
    try:
        p = [float(x) for x in json.loads(m["outcomePrices"])]
    except (KeyError, ValueError, TypeError):
        return None
    return p[0] if abs(p[0] + p[1] - 1) < 1e-6 and (p[0] in (0.0, 1.0) or m.get("umaResolutionStatus") == "resolved") else None


# ---------------------------------------------------------------- Kalshi
KALSHI = "https://api.elections.kalshi.com/trade-api/v2"


def _norm_kalshi(m: dict) -> dict | None:
    bid, ask = _f(m.get("yes_bid_dollars")), _f(m.get("yes_ask_dollars"))
    if m.get("market_type") != "binary" or not bid or not ask:
        return None
    return {"mid": f"pm:kalshi:{m['ticker']}", "venue": "kalshi",
            "frage": f"{m.get('title', '')} [{m.get('yes_sub_title', '')}]".strip(),
            "schliesst": _ts(m.get("close_time")), "ja_bid": bid, "ja_ask": ask,
            "volumen_24h": _f(m.get("volume_24h_fp"), 0), "liquiditaet": _f(m.get("open_interest_fp"), 0),
            "beschreibung": (m.get("rules_primary") or "")[:1500],
            "url": f"https://kalshi.com/markets/{m['event_ticker']}", "ref": {"ticker": m["ticker"]}}


def kalshi(n: int) -> list[dict]:
    d = get(KALSHI + "/markets", {"limit": 1000, "status": "open", "mve_filter": "exclude"}, ttl=60)
    ms = d.get("markets", [])
    ms.sort(key=lambda m: -(_f(m.get("volume_24h_fp"), 0)))
    out = [x for x in (_norm_kalshi(m) for m in ms) if x]
    return out[:n]


def kalshi_einzel(ticker: str) -> dict | None:
    return _norm_kalshi(get(f"{KALSHI}/markets/{ticker}")["market"])


def kalshi_buch(ref: dict, ergebnis: str) -> Book:
    d = get(f"{KALSHI}/markets/{ref['ticker']}/orderbook")["orderbook_fp"]
    yes_b = sorted(((float(p), float(s)) for p, s in d.get("yes_dollars") or []), reverse=True)
    no_b = sorted(((float(p), float(s)) for p, s in d.get("no_dollars") or []), reverse=True)
    ja_asks = sorted((round(1 - p, 4), s) for p, s in no_b)
    nein_asks = sorted((round(1 - p, 4), s) for p, s in yes_b)
    if ergebnis == "JA":
        return Book(yes_b, ja_asks, time.time())
    return Book(no_b, nein_asks, time.time())


def kalshi_aufloesung(ref: dict) -> float | None:
    m = get(f"{KALSHI}/markets/{ref['ticker']}")["market"]
    if m.get("status") in ("finalized", "settled") or m.get("result"):
        r = m.get("result")
        return {"yes": 1.0, "no": 0.0}.get(r)
    return None


# ---------------------------------------------------------------- PredictIt
def predictit(n: int) -> list[dict]:
    d = get("https://www.predictit.org/api/marketdata/all/", ttl=60)
    out = []
    for mk in d.get("markets", []):
        for c in mk.get("contracts", []):
            if c.get("status") != "Open":
                continue
            ask, bid = _f(c.get("bestBuyYesCost")), _f(c.get("bestSellYesCost"))
            if ask is None or bid is None or ask - bid > 0.10:
                continue
            name = mk["name"] if len(mk["contracts"]) == 1 else f"{mk['name']} — {c['name']}"
            out.append({"mid": f"pm:predictit:{c['id']}", "venue": "predictit", "frage": name,
                        "schliesst": _ts(c["dateEnd"]) if c.get("dateEnd") not in (None, "NA") else None,
                        "ja_bid": bid, "ja_ask": ask, "volumen_24h": 0.0, "liquiditaet": 0.0, "url": mk["url"],
                        "ref": {"vertrag": c["id"], "markt": mk["id"], "ja_kauf": ask, "ja_verkauf": bid,
                                "nein_kauf": _f(c.get("bestBuyNoCost")), "nein_verkauf": _f(c.get("bestSellNoCost"))}})
    # Nach Nähe zur Mitte (viel Unsicherheit = viel Handel) sortieren, begrenzen
    out.sort(key=lambda m: abs((m["ja_bid"] + m["ja_ask"]) / 2 - 0.5))
    return out[:n]


def predictit_buch(ref: dict, ergebnis: str) -> Book:
    """PredictIt liefert nur die Spitze des Buchs → konservative synthetische Tiefe:
    erste N Kontrakte zum besten Preis, danach je N weiteren 1 Cent schlechter."""
    tiefe = config.load()["boerse"]["predictit_tiefe_vertraege"]
    if ergebnis == "JA":
        ask, bid = ref["ja_kauf"], ref["ja_verkauf"]
    else:
        ask, bid = ref["nein_kauf"], ref["nein_verkauf"]
    asks = [(round(ask + 0.01 * k, 2), tiefe) for k in range(0, 10) if ask + 0.01 * k < 1]
    bids = [(round(bid - 0.01 * k, 2), tiefe) for k in range(0, 10) if bid - 0.01 * k > 0]
    return Book(bids, asks, time.time())


def predictit_aufloesung(ref: dict) -> float | None:
    try:
        m = get(f"https://www.predictit.org/api/marketdata/markets/{ref['markt']}")
    except HttpFehler:
        return None
    for c in m.get("contracts", []):
        if c["id"] == ref["vertrag"] and c.get("status") != "Open":
            lp = _f(c.get("lastClosePrice"))
            if lp is not None and (lp <= 0.01 or lp >= 0.99):
                return 1.0 if lp >= 0.99 else 0.0
    return None


# ---------------------------------------------------------------- Manifold (CPMM)
def _norm_mani(m: dict) -> dict | None:
    if m.get("mechanism") != "cpmm-1" or m.get("outcomeType") != "BINARY" or m.get("isResolved"):
        return None
    p = _f(m.get("probability"))
    if p is None:
        return None
    return {"mid": f"pm:manifold:{m['id']}", "venue": "manifold", "frage": m["question"],
            "schliesst": (m.get("closeTime") or 0) / 1000 or None, "ja_bid": p, "ja_ask": p,
            "volumen_24h": _f(m.get("volume24Hours"), 0), "liquiditaet": _f(m.get("totalLiquidity"), 0),
            "beschreibung": str(m.get("textDescription") or "")[:1500], "url": m.get("url"), "ref": {"id": m["id"]}}


def manifold(n: int) -> list[dict]:
    d = get("https://api.manifold.markets/v0/search-markets",
            {"term": "", "sort": "24-hour-vol", "filter": "open", "contractType": "BINARY", "limit": n}, ttl=60)
    return [x for x in (_norm_mani(m) for m in d) if x]


def manifold_suche(q: str, n: int = 8) -> list[dict]:
    d = get("https://api.manifold.markets/v0/search-markets",
            {"term": q, "sort": "score", "filter": "open", "contractType": "BINARY", "limit": n}, ttl=120)
    return [x for x in (_norm_mani(m) for m in d) if x]


def manifold_einzel(mid: str) -> dict | None:
    return _norm_mani(get(f"https://api.manifold.markets/v0/market/{mid}"))


def _cpmm_k(y: float, n: float, p: float) -> float:
    return y ** p * n ** (1 - p)


def cpmm_kauf_aktien(y: float, n: float, p: float, betrag: float) -> float:
    """Aktien (JA), die man für `betrag` bekommt (Manifold-CPMM-Formel)."""
    k = _cpmm_k(y, n, p)
    return (y + betrag) - (k / (n + betrag) ** (1 - p)) ** (1 / p)


def cpmm_verkauf_erloes(y: float, n: float, p: float, aktien: float) -> float:
    """Erlös für den Verkauf von `aktien` JA-Aktien (Bisektion auf die Invariante)."""
    k = _cpmm_k(y, n, p)
    lo, hi = 0.0, min(n, aktien)
    for _ in range(80):
        a = (lo + hi) / 2
        if (y + aktien - a) ** p * (n - a) ** (1 - p) >= k:
            lo = a
        else:
            hi = a
    return lo


def manifold_buch(ref: dict, ergebnis: str) -> Book:
    m = get(f"https://api.manifold.markets/v0/market/{ref['id']}")
    pool, p = m["pool"], m.get("p", 0.5)
    y, n = pool["YES"], pool["NO"]
    if ergebnis == "NEIN":  # Spiegelung: NEIN-Aktien = JA-Aktien mit vertauschten Töpfen und p' = 1-p
        y, n, p = n, y, 1 - p
    asks, bids = [], []
    vor_b, vor_s = 0.0, 0.0
    for betrag in (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000):
        s = cpmm_kauf_aktien(y, n, p, betrag)
        if s - vor_s > 1e-9:
            asks.append(((betrag - vor_b) / (s - vor_s), s - vor_s))
        vor_b, vor_s = betrag, s
    vor_e, vor_a = 0.0, 0.0
    for aktien in (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000):
        e = cpmm_verkauf_erloes(y, n, p, aktien)
        if aktien - vor_a > 1e-9:
            bids.append(((e - vor_e) / (aktien - vor_a), aktien - vor_a))
        vor_e, vor_a = e, aktien
    return Book(bids, asks, time.time())


def manifold_aufloesung(ref: dict) -> float | str | None:
    m = get(f"https://api.manifold.markets/v0/market/{ref['id']}")
    if not m.get("isResolved"):
        return None
    r = m.get("resolution")
    if r == "YES":
        return 1.0
    if r == "NO":
        return 0.0
    if r == "MKT":
        return float(m.get("resolutionProbability", 0.5))
    return "STORNO"


def einzelmarkt(venue: str, ident: str) -> dict | None:
    """Einen Markt per ID nachladen (auch wenn er nicht im Standard-Universum ist)."""
    try:
        if venue == "polymarket":
            return _norm_poly(get(f"https://gamma-api.polymarket.com/markets/{ident}"))
        if venue == "kalshi":
            return kalshi_einzel(ident)
        if venue == "manifold":
            return manifold_einzel(ident)
        if venue == "predictit":
            return next((m for m in predictit(100000) if m["mid"] == f"pm:predictit:{ident}"), None)
    except (HttpFehler, KeyError, ValueError):
        return None
    return None


# ---------------------------------------------------------------- Dispatcher
BUCH = {"polymarket": polymarket_buch, "kalshi": kalshi_buch, "predictit": predictit_buch, "manifold": manifold_buch}
AUFLOESUNG = {"polymarket": polymarket_aufloesung, "kalshi": kalshi_aufloesung,
              "predictit": predictit_aufloesung, "manifold": manifold_aufloesung}


def buch(i: dict) -> Book:
    return BUCH[i["venue"]](i["ref"], i["ergebnis"])


def aufloesung(i: dict):
    return AUFLOESUNG[i["venue"]](i["ref"])


def universum(n: int | None = None) -> list[dict]:
    n = n or config.load()["universum"]["pm_je_plattform"]
    out = []
    for fn in (polymarket, kalshi, predictit, manifold):
        try:
            out += fn(n)
        except (HttpFehler, KeyError, ValueError) as e:  # eine Quelle darf ausfallen
            print(f"WARNUNG {fn.__name__}: {e}")
    return out
