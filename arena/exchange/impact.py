"""Börsen-Realismus (Recherche Kat. 5): Marktimpact nach dem Square-Root-Gesetz und verbrauchte Buchtiefe.

* Impact ≈ Y · σ_Tag · √(Q / V_Tag) (Tóth et al. 2011, Y ≈ 0,7) – für Füllungen ohne echte Tiefe: ausgelöste Stops/Take-Profits,
  Liquidationen und das synthetische Aktienbuch.
* Verbrauchte Tiefe (Idee „liquidity_consumption“ aus NautilusTrader): Innerhalb eines Laufs wird das zwischengespeicherte Orderbuch nach
  jeder Füllung um die genommene Menge verringert – mehrere Orders bzw. Fonds im selben Tick laufen nicht gegen dasselbe unverbrauchte Buch."""
from __future__ import annotations

import math
import threading

Y = 0.7
MAX_IMPACT = 0.10  # Deckel: mehr als 10 % Preiswirkung je Füllung wäre ohnehin unrealistisch modelliert
_lock = threading.RLock()


def sqrt_impact(qty: float, preis: float, vol_tag_usd: float | None, sigma_tag: float | None) -> float:
    """Relativer Preisaufschlag gegen den Händler (0,002 = 20 bp). Ohne Volumen/σ: 0 (nur die normale Slippage gilt)."""
    if not vol_tag_usd or not sigma_tag or vol_tag_usd <= 0 or qty <= 0:
        return 0.0
    return min(MAX_IMPACT, Y * sigma_tag * math.sqrt(qty * preis / vol_tag_usd))


def verbrauche(book, seite_kaufen: bool, qty: float) -> None:
    """Nimmt `qty` von der Buchseite (asks beim Kauf, bids beim Verkauf) – in place, threadsicher."""
    if book is None or qty <= 0:
        return
    with _lock:
        levels = book.asks if seite_kaufen else book.bids
        rest = qty
        neu = []
        for preis, menge in levels:
            if rest <= 1e-12:
                neu.append((preis, menge))
                continue
            nimm = min(rest, menge)
            rest -= nimm
            if menge - nimm > 1e-12:
                neu.append((preis, menge - nimm))
        levels[:] = neu


def markt_kennzahlen(inst: dict) -> tuple[float | None, float | None]:
    """(Tagesvolumen in USD, Tagesvolatilität) aus den vorhandenen Datenquellen; None, wenn unbekannt."""
    from arena.data import crypto, stocks
    try:
        if inst["art"] in ("spot", "perp"):
            basis = inst.get("symbol", "").split("-")[0].split("_")[0]
            t = crypto.spot_ticker(basis)
            sigma = None
            if basis in ("BTC", "ETH"):
                d = crypto.dvol(basis)
                sigma = d["dvol"] / 100 / math.sqrt(365) if d else None
            return ((t["vol24"] * t["last"]) if t else None), (sigma or 0.04)
        if inst["art"] == "stock":
            return stocks.tagesvolumen_sigma(inst["symbol"])
    except Exception:  # Kennzahlen sind ein Zuschlag, nie ein Grund, eine Füllung scheitern zu lassen
        return None, None
    return None, None
