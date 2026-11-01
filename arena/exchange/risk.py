"""Positionsgrenzen je Risikoprofil."""
from __future__ import annotations

from arena import config


def profil(name: str) -> dict:
    return config.load()["risiko"][name]


def _krypto_nominal(p: dict) -> float:
    """Brutto-Krypto-Risiko einer Position: Spot/Perp/Option zum Nominal (BTC/ETH/SOL korrelieren 0,89–0,91 → ein Cluster)."""
    return abs(p["einstand"] * p["menge"])


def cluster_stand(pf: dict, prof: dict, equity: float) -> dict:
    from arena import themen
    eq = max(equity, 1e-9)
    krypto = sum(_krypto_nominal(p) for p in pf["positionen"] if p["inst"]["art"] in ("spot", "perp", "option"))
    je_thema: dict[str, float] = {}
    for p in pf["positionen"]:
        if p["inst"]["art"] == "pm":
            t = themen.thema(p["inst"])
            je_thema[t] = je_thema.get(t, 0.0) + p["einstand"] * p["menge"]
    return {"krypto_pct": round(100 * krypto / eq, 1), "krypto_limit_pct": 100 * prof.get("max_krypto_cluster_pct", 99),
            "wetten_je_thema_pct": {t: round(100 * v / eq, 1) for t, v in je_thema.items()}, "thema_limit_pct": 100 * prof.get("max_thema_pct", 1)}


def pruefe_eroeffnung(pf: dict, prof: dict, inst: dict, nominal: float, hebel: float, equity: float, seite: str = "long") -> str | None:
    """Gibt None zurück, wenn erlaubt, sonst den Ablehnungsgrund (deutsch)."""
    if hebel > prof["max_hebel"] + 1e-9:
        return f"Hebel {hebel} über dem Limit {prof['max_hebel']} dieses Risikoprofils"
    if hebel < 1:
        return "Hebel muss mindestens 1 sein"
    if inst["art"] == "stock" and hebel > config.load()["boerse"]["aktien_marge"]["max_hebel"] + 1e-9:
        return f"Aktien: Wertpapierkredit höchstens {config.load()['boerse']['aktien_marge']['max_hebel']}× (Reg-T)"
    if inst["art"] not in ("perp", "stock") and hebel != 1:
        return "Hebel gibt es nur bei Perpetuals und Aktien (Wertpapierkredit)"
    eq = max(equity, 1e-9)
    gleiche = sum(p["einstand"] * p["menge"] for p in pf["positionen"] if p["inst"]["id"] == inst["id"])
    if (gleiche + nominal) / eq > prof["max_position_pct"] + 1e-9 and inst["art"] != "perp":
        return f"Einzelposition würde {100 * (gleiche + nominal) / eq:.1f} % des Vermögens übersteigen (Limit {100 * prof['max_position_pct']:.0f} %)"
    if inst["art"] == "perp":
        perp = sum(p["einstand"] * p["menge"] for p in pf["positionen"] if p["inst"]["art"] == "perp")
        if (perp + nominal) / eq > prof["max_perp_pct"] * prof["max_hebel"] + 1e-9:
            return "Perp-Nominal über dem Limit des Risikoprofils"
        marge = nominal / hebel + sum(p["marge"] for p in pf["positionen"] if p["inst"]["id"] == inst["id"])
        if marge / eq > prof["max_position_pct"] + 1e-9:
            return "Marge der Perp-Position über dem Einzelpositions-Limit"
    if inst["art"] == "option":
        opt = sum(p["einstand"] * p["menge"] for p in pf["positionen"] if p["inst"]["art"] == "option")
        if (opt + nominal) / eq > prof["max_optionen_pct"] + 1e-9:
            return f"Optionsprämien würden {100 * prof['max_optionen_pct']:.0f} % des Vermögens übersteigen"
    if inst["art"] in ("spot", "perp", "option") and "max_krypto_cluster_pct" in prof:
        krypto = sum(_krypto_nominal(p) for p in pf["positionen"] if p["inst"]["art"] in ("spot", "perp", "option"))
        if (krypto + nominal) / eq > prof["max_krypto_cluster_pct"] + 1e-9:
            return (f"Krypto-Cluster (BTC/ETH/SOL & Co. laufen fast gleich) würde {100 * (krypto + nominal) / eq:.0f} % Nominal erreichen "
                    f"(Limit {100 * prof['max_krypto_cluster_pct']:.0f} %)")
    if inst["art"] == "pm" and "max_thema_pct" in prof:
        from arena import themen
        t = themen.thema(inst)
        im_thema = sum(p["einstand"] * p["menge"] for p in pf["positionen"] if p["inst"]["art"] == "pm" and themen.thema(p["inst"]) == t)
        if (im_thema + nominal) / eq > prof["max_thema_pct"] + 1e-9:
            return f"Themen-Cluster „{t}“ würde {100 * (im_thema + nominal) / eq:.0f} % des Vermögens übersteigen (Limit {100 * prof['max_thema_pct']:.0f} %)"
    from arena.exchange import portfolio
    einsatz = nominal / hebel
    gebunden = sum(portfolio.gebunden(p) for p in pf["positionen"])
    if (gebunden + einsatz) / eq > prof["max_gesamt_exposure_pct"] + 1e-9:
        return f"Gesamt-Exposure würde {100 * prof['max_gesamt_exposure_pct']:.0f} % des Vermögens übersteigen"
    if (pf["cash"] - einsatz) / eq < prof["min_cash_pct"] - 1e-9:
        return f"Mindest-Cash {100 * prof['min_cash_pct']:.0f} % würde unterschritten"
    return None
