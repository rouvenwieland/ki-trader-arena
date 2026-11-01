"""Portfolio-Zustand (reines JSON) und Bewertung zum Marktwert."""
from __future__ import annotations

import time
import uuid


def neu(fonds_id: str, start_kapital_usd: float, ts: float | None = None) -> dict:
    return {
        "fonds_id": fonds_id, "waehrung": "USD", "start_kapital": start_kapital_usd,
        "cash": start_kapital_usd, "positionen": [], "realisiert": 0.0,
        "gebuehren": 0.0, "funding": 0.0, "erstellt": ts or time.time(),
    }


def neue_id() -> str:
    return "p" + uuid.uuid4().hex[:8]


def marginal(art: str, seite: str = "long", hebel: float = 1.0) -> bool:
    """Positionen auf Marge: Perps immer, Aktien bei Leerverkauf oder Wertpapierkredit (Hebel > 1, Reg-T), geschriebene Optionen."""
    return art == "perp" or (art == "stock" and (seite == "short" or hebel > 1 + 1e-9)) or (art == "option" and seite == "short")


def ist_marginal(pos: dict) -> bool:
    return pos["inst"]["art"] == "perp" or bool(pos.get("marginal"))


def gebunden(pos: dict) -> float:
    """Gebundenes Kapital: Marge bei Margin-Positionen, sonst Einstand × Menge."""
    return pos["marge"] if ist_marginal(pos) else pos["einstand"] * pos["menge"]


def pos_wert(pos: dict, bid: float | None, mark: float | None = None) -> float:
    """Liquidationswert einer Position: Long-Bestände zum Geldkurs (was man real bekäme);
    Perps: Marge + unrealisierter Gewinn zum Markpreis."""
    inst = pos["inst"]
    if ist_marginal(pos):
        px = mark if mark is not None else bid
        if px is None:
            return pos["marge"]
        vz = 1 if pos["seite"] == "long" else -1
        return pos["marge"] + vz * (px - pos["einstand"]) * pos["menge"]
    px = bid if bid is not None else mark
    if px is None:
        px = pos["einstand"]
    return px * pos["menge"]


def equity(pf: dict, marks: dict[str, dict]) -> float:
    """marks: inst_id -> {"bid": .., "mark": ..}. Fehlt ein Kurs, gilt der Einstand (konservativ-neutral)."""
    summe = pf["cash"]
    for p in pf["positionen"]:
        m = marks.get(p["inst"]["id"], {})
        summe += pos_wert(p, m.get("bid"), m.get("mark"))
    return summe


def exposure(pf: dict) -> float:
    """Summe der Positionsgrößen zum Einstand (Nominal)."""
    return sum(p["einstand"] * p["menge"] for p in pf["positionen"])
