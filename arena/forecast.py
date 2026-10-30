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
    gespeichert = store.lies("prognosen.json", {})
    e = gespeichert.get(iid)
    if e and time.time() - e["ts"] < 8 * 3600 and e.get("horizont_h") == horizont:
        return {**e, "hinweis": "Modellprognose – nur ein Hinweis, Unsicherheitsband beachten"}
    p = historie(iid, snap)
    if not p:
        return {"fehler": f"keine Historie für {iid}"}
    if iid.startswith("stock:"):
        horizont = max(1, horizont // 24)  # Tagesdaten
    return statistisch(p, horizont) | {"horizont": horizont, "hinweis": "Statistischer Hinweis – kein Orakel; TimesFM/Kronos-Ergebnis liegt nicht vor"}
