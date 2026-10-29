"""Positionsgrenzen je Risikoprofil."""
from __future__ import annotations

from arena import config


def profil(name: str) -> dict:
    return config.load()["risiko"][name]


def pruefe_eroeffnung(pf: dict, prof: dict, inst: dict, nominal: float, hebel: float, equity: float) -> str | None:
    """Gibt None zurück, wenn erlaubt, sonst den Ablehnungsgrund (deutsch)."""
    if hebel > prof["max_hebel"] + 1e-9:
        return f"Hebel {hebel} über dem Limit {prof['max_hebel']} dieses Risikoprofils"
    if hebel < 1:
        return "Hebel muss mindestens 1 sein"
    if inst["art"] != "perp" and hebel != 1:
        return "Hebel gibt es nur bei Perpetuals"
    eq = max(equity, 1e-9)
    gleiche = sum(p["einstand"] * p["menge"] for p in pf["positionen"] if p["inst"]["id"] == inst["id"])
    if (gleiche + nominal) / eq > prof["max_position_pct"] + 1e-9 and inst["art"] != "perp":
        return f"Einzelposition würde {100 * (gleiche + nominal) / eq:.1f} % des Vermögens übersteigen (Limit {100 * prof['max_position_pct']:.0f} %)"
    if inst["art"] == "perp":
        perp = sum(p["einstand"] * p["menge"] for p in pf["positionen"] if p["inst"]["art"] == "perp")
        if (perp + nominal) / eq > prof["max_perp_pct"] * prof["max_hebel"] + 1e-9:
            return "Perp-Nominal über dem Limit des Risikoprofils"
        marge = nominal / hebel
        if marge / eq > prof["max_position_pct"] + 1e-9:
            return "Marge der Perp-Position über dem Einzelpositions-Limit"
    if inst["art"] == "option":
        opt = sum(p["einstand"] * p["menge"] for p in pf["positionen"] if p["inst"]["art"] == "option")
        if (opt + nominal) / eq > prof["max_optionen_pct"] + 1e-9:
            return f"Optionsprämien würden {100 * prof['max_optionen_pct']:.0f} % des Vermögens übersteigen"
    einsatz = nominal / hebel
    if inst["art"] == "perp":
        gebunden = sum(p["marge"] for p in pf["positionen"] if p["inst"]["art"] == "perp") + sum(
            p["einstand"] * p["menge"] for p in pf["positionen"] if p["inst"]["art"] != "perp")
    else:
        gebunden = sum(p["einstand"] * p["menge"] if p["inst"]["art"] != "perp" else p["marge"] for p in pf["positionen"])
    if (gebunden + einsatz) / eq > prof["max_gesamt_exposure_pct"] + 1e-9:
        return f"Gesamt-Exposure würde {100 * prof['max_gesamt_exposure_pct']:.0f} % des Vermögens übersteigen"
    if (pf["cash"] - einsatz) / eq < prof["min_cash_pct"] - 1e-9:
        return f"Mindest-Cash {100 * prof['min_cash_pct']:.0f} % würde unterschritten"
    return None
