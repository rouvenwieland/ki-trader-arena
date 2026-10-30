"""Gebühren je Plattform (Taker, konservativ). Alles in USD."""
from __future__ import annotations

import math

from arena import config


def _g() -> dict:
    return config.load()["boerse"]["gebuehren"]


def gebuehr(inst: dict, preis: float, qty: float, index_preis: float | None = None) -> float:
    """Gebühr für einen Handel. inst["art"] ∈ spot|perp|option|pm|stock, inst["venue"] benennt die Plattform."""
    g = _g()
    art, venue = inst["art"], inst.get("venue", "")
    notional = preis * qty
    if art == "spot":
        return notional * g["coinbase_spot_taker"]
    if art == "perp":
        return notional * g["deribit_perp_taker"]
    if art == "option":
        # Deribit: min(0,03 % des Basiswerts, 12,5 % des Optionspreises) je Kontrakt; preis hier in USD
        basis = (index_preis or preis) * qty * g["deribit_option_taker_underlying"]
        return min(basis, notional * g["deribit_option_max_anteil"])
    if art == "pm":
        if venue == "kalshi":
            # Kalshi: aufgerundet auf volle Cent: 0,07 * C * P * (1-P)
            return math.ceil(g["kalshi_koeffizient"] * qty * preis * (1 - preis) * 100 - 1e-9) / 100
        if venue == "polymarket":
            # Laut Doku (docs.polymarket.com/trading/fees): C · rate · (p·(1−p))^exponent, gerundet auf 5 Stellen.
            # Rate/Exponent je Markt aus feeSchedule (pm.py → ref); Geopolitik u. a. haben Rate 0.
            ref = inst.get("ref") or {}
            rate = ref.get("gebuehr_rate")
            if rate is None:
                rate = g["polymarket_taker"]
            return round(qty * rate * (preis * (1 - preis)) ** ref.get("gebuehr_exp", 1), 5)
        return notional * g["manifold"] if venue == "manifold" else 0.0
    if art == "stock":
        return notional * 0.0 + g["stock_kommission"]
    return 0.0


def abschluss_gebuehr(inst: dict, einstand: float, erloes: float) -> float:
    """Gebühr, die beim Schließen/Abrechnen auf den Gewinn fällt (PredictIt: 10 % des Gewinns)."""
    if inst["art"] == "pm" and inst.get("venue") == "predictit":
        return max(0.0, erloes - einstand) * _g()["predictit_gewinn_gebuehr"]
    return 0.0
