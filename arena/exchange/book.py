"""Orderbuch: Füllung gegen echte Tiefe (VWAP, Teilfüllung, Slippage)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Book:
    """Orderbuch-Schnappschuss. bids absteigend, asks aufsteigend: Liste von (Preis, Menge)."""
    bids: list[tuple[float, float]] = field(default_factory=list)
    asks: list[tuple[float, float]] = field(default_factory=list)
    ts: float = 0.0
    mark: float | None = None  # Markpreis (Perps/Optionen), falls vorhanden

    @property
    def best_bid(self) -> float | None:
        return self.bids[0][0] if self.bids else None

    @property
    def best_ask(self) -> float | None:
        return self.asks[0][0] if self.asks else None

    @property
    def mid(self) -> float | None:
        if self.bids and self.asks:
            return (self.bids[0][0] + self.asks[0][0]) / 2
        return self.mark

    def to_dict(self, tiefe: int = 5) -> dict:
        return {"bids": self.bids[:tiefe], "asks": self.asks[:tiefe], "mark": self.mark, "ts": self.ts}


@dataclass
class Fill:
    qty: float
    vwap: float
    kosten: float  # Preis * Menge (ohne Gebühr)
    stufen: int
    voll: bool


def walk(levels: list[tuple[float, float]], qty: float, slippage_bps: float = 0.0, kaufen: bool = True) -> Fill:
    """Läuft die Orderbuchseite ab und liefert VWAP. Teilfüllung, wenn die Tiefe nicht reicht.

    Slippage (Verzögerung zwischen Schnappschuss und Ausführung) verschlechtert den Preis
    zusätzlich um slippage_bps gegen den Händler."""
    rest, kosten, got, n = qty, 0.0, 0.0, 0
    for preis, groesse in levels:
        if rest <= 1e-12:
            break
        nimm = min(rest, groesse)
        kosten += nimm * preis
        got += nimm
        rest -= nimm
        n += 1
    if got <= 0:
        return Fill(0.0, 0.0, 0.0, 0, False)
    vwap = kosten / got
    adj = 1 + slippage_bps / 1e4 if kaufen else 1 - slippage_bps / 1e4
    vwap *= adj
    return Fill(got, vwap, vwap * got, n, rest <= 1e-9)


def max_qty_fuer_budget(levels: list[tuple[float, float]], budget: float, slippage_bps: float, gebuehr_fn) -> float:
    """Größte Menge, deren Kosten + Gebühr das Budget nicht überschreiten (Bisektion)."""
    gesamt = sum(g for _, g in levels)
    lo, hi = 0.0, gesamt
    for _ in range(60):
        mid = (lo + hi) / 2
        f = walk(levels, mid, slippage_bps, True)
        if f.qty + 1e-12 < mid:  # Tiefe reicht nicht
            hi = mid
            continue
        if f.kosten + gebuehr_fn(f.vwap, f.qty) <= budget:
            lo = mid
        else:
            hi = mid
    return lo
