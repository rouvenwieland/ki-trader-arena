"""Prognose-Werkzeug. Bevorzugt Ergebnisse von TimesFM/Kronos (Workflow „prognosen“ schreibt data/prognosen.json);
sonst statistisches Verfahren (Bootstrap der Stundenrenditen). Immer mit Unsicherheitsband, immer als Hinweis gekennzeichnet."""
from __future__ import annotations

import math
import random
import time

from arena import store
from arena.data import crypto, stocks


def historie(iid: str, snap: dict | None = None) -> list[float]:
    """Stunden-Schlusskurse (älteste zuerst)."""
    if iid.startswith("spot:"):
        return [c[4] for c in crypto.spot_kerzen(iid.split(":", 1)[1], 3600, 300)]
    if iid.startswith("stock:"):
        return [c for _, c in stocks.tagesschluesse(iid.split(":", 1)[1], "1y")]
    serie = (snap or {}).get("verlauf", {}).get(iid)
    return [p for _, p in serie] if serie else []


def statistisch(preise: list[float], horizont: int, n: int = 400) -> dict:
    rets = [math.log(b / a) for a, b in zip(preise, preise[1:]) if a > 0 and b > 0]
    if len(rets) < 20:
        return {"fehler": "zu wenig Daten"}
    rng = random.Random(len(preise))
    ziel = []
    for _ in range(n):
        ziel.append(preise[-1] * math.exp(sum(rng.choice(rets) for _ in range(horizont))))
    ziel.sort()
    q = lambda p: ziel[int(p * (n - 1))]  # noqa: E731
    return {"modell": "Bootstrap der Renditen (Statistik)", "letzter": preise[-1], "median": q(0.5), "p10": q(0.1), "p90": q(0.9),
            "p_hoeher": sum(1 for z in ziel if z > preise[-1]) / n}


def prognose(iid: str, horizont: int, snap: dict | None = None) -> dict:
    """Modellprognosen (TimesFM/Kronos) falls frisch vorhanden, immer zusätzlich die statistische Basislinie."""
    out: dict = {}
    e = store.lies("prognosen.json", {}).get(iid)
    if e and time.time() - e["ts"] < 8 * 3600:
        h = max(1, min(int(horizont), e["horizont_h"])) - 1
        out["modelle"] = {n: {"modell": m["modell"], "letzter": m["letzter"], "median": m["median"][h], "p10": m["p10"][h], "p90": m["p90"][h],
                              "horizont_h": h + 1} for n, m in e["modelle"].items()}
    p = historie(iid, snap)
    if p:
        hh = max(1, horizont // 24) if iid.startswith("stock:") else horizont
        out["statistik"] = statistisch(p, hh)
    if not out:
        return {"fehler": f"keine Historie für {iid}"}
    out["hinweis"] = "Hinweise mit Unsicherheitsband, kein Orakel. Foundation-Modelle auf Kursen haben im Vorwärtstest oft keinen Vorteil nach Kosten."
    return out
