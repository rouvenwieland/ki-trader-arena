"""Kennzahlen je Fonds: Rendite, max. Drawdown, Sharpe, Trefferquote, Brier-Score (Wettmärkte), Kosten."""
from __future__ import annotations

import math
import statistics
from datetime import datetime, timezone

from arena import store


def tageswerte(eq: list[dict]) -> list[tuple[str, float]]:
    tage: dict[str, float] = {}
    for p in eq:
        tage[datetime.fromtimestamp(p["t"], timezone.utc).strftime("%Y-%m-%d")] = p["usd"]
    return sorted(tage.items())


def max_drawdown(werte: list[float]) -> float:
    spitze, md = -math.inf, 0.0
    for w in werte:
        spitze = max(spitze, w)
        if spitze > 0:
            md = min(md, w / spitze - 1)
    return md * 100


def sharpe(werte_tag: list[float]) -> float | None:
    """Annualisiert (365 Tage, Krypto/Wetten laufen durch), erst ab 8 Tageswerten sinnvoll."""
    if len(werte_tag) < 8:
        return None
    r = [b / a - 1 for a, b in zip(werte_tag, werte_tag[1:]) if a > 0]
    sd = statistics.pstdev(r)
    return None if sd == 0 else statistics.mean(r) / sd * math.sqrt(365)


def brier(fid: str) -> dict:
    prog = store.lies_jsonl(f"funds/{fid}/prognosen.jsonl")
    res = store.lies("resolutions.json", {})
    neueste: dict[str, dict] = {}
    for p in prog:  # je Markt die erste Schätzung zählt (kein Nachbessern nach Kenntnis)
        neueste.setdefault(p["markt_id"], p)
    xs, ms = [], []
    for mid, p in neueste.items():
        r = res.get(mid)
        if r is None or r.get("wert") is None:
            continue
        xs.append((p["p_ja"] - r["wert"]) ** 2)
        if p.get("markt_ja_mitte") is not None:
            ms.append((p["markt_ja_mitte"] - r["wert"]) ** 2)
    return {"n": len(xs), "brier": statistics.mean(xs) if xs else None, "brier_markt": statistics.mean(ms) if ms else None,
            "offen": len(neueste) - len(xs)}


def kennzahlen(fid: str) -> dict:
    eq = store.lies_jsonl(f"funds/{fid}/equity.jsonl")
    pf = store.lies(f"funds/{fid}/portfolio.json")
    led = store.lies_jsonl(f"funds/{fid}/ledger.jsonl")
    if not eq or not pf:
        return {}
    start = pf["start_kapital"]
    tag = tageswerte(eq)
    geschl = [x for x in led if x.get("aktion") in ("geschlossen", "teilweise_geschlossen", "liquidiert") and "netto_pnl" in x]
    kosten_api = sum(x.get("usd", 0) for x in store.lies_jsonl(f"funds/{fid}/nutzung.jsonl"))
    fx = (store.lies("fx.json") or {}).get("usd_je_eur", 1.08)
    return {"equity_usd": eq[-1]["usd"], "start_usd": start, "rendite_pct": (eq[-1]["usd"] / start - 1) * 100,
            "max_drawdown_pct": max_drawdown([p["usd"] for p in eq]), "sharpe": sharpe([v for _, v in tag]),
            "trades": len(geschl), "trefferquote": (sum(1 for x in geschl if x["netto_pnl"] > 0) / len(geschl)) if geschl else None,
            "gebuehren_usd": pf["gebuehren"], "funding_usd": pf["funding"], "api_kosten_eur": kosten_api / fx,
            "brier": brier(fid), "positionen": len(pf["positionen"]), "cash_usd": pf["cash"]}
