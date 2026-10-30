"""Prognose-Werkzeug. Feste Basislinie ist ein GARCH(1,1)-Band um den Random Walk (im Recherche-Test am besten kalibriert,
gleichauf mit dem Random Walk); dazu TimesFM/Kronos aus data/prognosen.json, wenn frisch vorhanden (Workflow „prognosen“),
und der Bootstrap der Renditen. Immer mit Unsicherheitsband, immer als Hinweis gekennzeichnet.

Kronos liefert nur noch eine Richtung (Median): sein Band aus wenigen Pfaden war viel zu eng (B3 der Recherche).
Die Trefferbilanz (Abdeckung des 10–90-Bands, Pinball-Verlust) wird aus data/prognosen_log.jsonl gegen echte Kurse gerechnet."""
from __future__ import annotations

import math
import random
import time
from datetime import datetime, timezone

from arena import store
from arena.data import crypto, stocks

Z90 = 1.2815515655446004  # Standardnormal-Quantil 0,9
LOG = "prognosen_log.jsonl"


def historie(iid: str, snap: dict | None = None) -> list[float]:
    """Stunden-Schlusskurse (älteste zuerst)."""
    if iid.startswith("spot:"):
        return [c[4] for c in crypto.spot_kerzen(iid.split(":", 1)[1], 3600, 300)]
    if iid.startswith("stock:"):
        return [c for _, c in stocks.tagesschluesse(iid.split(":", 1)[1], "1y")]
    serie = (snap or {}).get("verlauf", {}).get(iid)
    return [p for _, p in serie] if serie else []


def renditen(preise: list[float]) -> list[float]:
    return [math.log(b / a) for a, b in zip(preise, preise[1:]) if a > 0 and b > 0]


def statistisch(preise: list[float], horizont: int, n: int = 400) -> dict:
    rets = renditen(preise)
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


# ---------------------------------------------------------------- GARCH(1,1) (rein in Python, ohne Zusatzpakete)
def _nll(rets: list[float], var: float, a: float, b: float) -> float:
    omega = var * (1 - a - b)
    s2, nll = var, 0.0
    for r in rets:
        nll += math.log(s2) + r * r / s2
        s2 = omega + a * r * r + b * s2
    return nll


def garch_fit(rets: list[float]) -> dict:
    """GARCH(1,1) mit Varianz-Targeting (ω = σ²·(1−α−β)), α/β per Gittersuche mit Verfeinerung (Gauß-Likelihood).
    Liefert auch die bedingte Varianz für den nächsten Schritt."""
    mu = sum(rets) / len(rets)
    x = [r - mu for r in rets]
    var = sum(r * r for r in x) / len(x) or 1e-12
    best = (math.inf, 0.05, 0.9)
    for a in [i / 100 for i in range(1, 31, 2)]:
        for b in [j / 100 for j in range(50, 99, 2)]:
            if a + b < 0.995:
                best = min(best, (_nll(x, var, a, b), a, b))
    _, a0, b0 = best
    for a in [a0 + d / 1000 for d in range(-10, 11, 2)]:
        for b in [b0 + d / 1000 for d in range(-10, 11, 2)]:
            if a > 0 and b > 0 and a + b < 0.999:
                best = min(best, (_nll(x, var, a, b), a, b))
    _, a, b = best
    omega = var * (1 - a - b)
    s2 = var
    for r in x:
        s2 = omega + a * r * r + b * s2
    return {"alpha": a, "beta": b, "omega": omega, "var": var, "s2_naechster": s2}


def garch_band(preise: list[float], horizont: int) -> dict:
    """10–90-Band für den Kurs in `horizont` Schritten: Random Walk (Median = letzter Kurs), Streuung aus GARCH(1,1)."""
    rets = renditen(preise)
    if len(rets) < 30:
        return {"fehler": "zu wenig Daten"}
    g = garch_fit(rets[-500:])
    p = g["alpha"] + g["beta"]
    v = sum(g["var"] + p ** k * (g["s2_naechster"] - g["var"]) for k in range(max(1, int(horizont))))
    s = math.sqrt(max(v, 0.0))
    letzter = preise[-1]
    return {"modell": "GARCH(1,1)-Band um Random Walk (Basislinie)", "letzter": letzter, "median": letzter,
            "p10": letzter * math.exp(-Z90 * s), "p90": letzter * math.exp(Z90 * s), "p_hoeher": 0.5,
            "vola_horizont_pct": round(100 * s, 3), "alpha": round(g["alpha"], 3), "beta": round(g["beta"], 3)}


def prognose(iid: str, horizont: int, snap: dict | None = None) -> dict:
    """GARCH-Basislinie + Modellprognosen (TimesFM; Kronos nur Richtung) falls frisch vorhanden + Bootstrap."""
    out: dict = {}
    e = store.lies("prognosen.json", {}).get(iid)
    if e and time.time() - e["ts"] < 8 * 3600:
        h = max(1, min(int(horizont), e["horizont_h"])) - 1
        modelle = {}
        for n, m in e["modelle"].items():
            x = {"modell": m["modell"], "letzter": m["letzter"], "median": m["median"][h], "horizont_h": h + 1}
            if m.get("p10") and not m.get("nur_richtung"):
                x |= {"p10": m["p10"][h], "p90": m["p90"][h]}
            else:
                x["hinweis"] = "nur Richtungshinweis – kein verlässliches Unsicherheitsband"
            modelle[n] = x
        out["modelle"] = modelle
    p = historie(iid, snap)
    if p:
        hh = max(1, horizont // 24) if iid.startswith("stock:") else horizont
        out["basislinie_garch"] = garch_band(p, hh)
        out["statistik"] = statistisch(p, hh)
    if not out:
        return {"fehler": f"keine Historie für {iid}"}
    b = bilanz()
    if b:
        out["trefferbilanz_24h"] = b
    out["hinweis"] = ("Hinweise mit Unsicherheitsband, kein Orakel. Kein Zeitreihenmodell schlug im Test bei Krypto-Stundenkursen den Random Walk; "
                      "nutze das GARCH-Band für Risiko/Größe, nicht als Richtungssignal.")
    return out


# ---------------------------------------------------------------- Trefferbilanz (ehrliche Messung der Prognosemodelle)
def _kurs_um(iid: str, ziel: float, toleranz: float = 1800) -> float | None:
    tag = datetime.fromtimestamp(ziel, timezone.utc).strftime("%Y-%m-%d")
    best = None
    for z in store.lies_jsonl(f"history/preise-{tag}.jsonl"):
        if iid in z["p"] and abs(z["t"] - ziel) <= toleranz and (best is None or abs(z["t"] - ziel) < abs(best[0] - ziel)):
            best = (z["t"], z["p"][iid])
    return best[1] if best else None


def _pinball(y: float, q: float, tau: float) -> float:
    return max(tau * (y - q), (tau - 1) * (y - q))


def bilanz(jetzt: float | None = None, tage: int = 28) -> dict:
    """Je Modell: Anzahl fälliger 24-h-Prognosen, Abdeckung des 10–90-Bands (Soll ≈ 80 %), mittlerer Pinball-Verlust in % des Kurses
    (Mittel über q10/q50/q90; nur Median → nur q50) und absoluter Medianfehler in %."""
    jetzt = jetzt or time.time()
    acc: dict[str, dict] = {}
    for e in store.lies_jsonl(LOG):
        ziel = e["ts"] + e.get("h", 24) * 3600
        if ziel > jetzt or e["ts"] < jetzt - tage * 86400:
            continue
        y = _kurs_um(e["iid"], ziel)
        if y is None or not e.get("letzter"):
            continue
        a = acc.setdefault(e["modell"], {"n": 0, "treffer": 0, "n_band": 0, "pinball": 0.0, "fehler": 0.0})
        a["n"] += 1
        a["fehler"] += abs(y - e["median"]) / e["letzter"]
        if e.get("p10") is not None and e.get("p90") is not None:
            a["n_band"] += 1
            a["treffer"] += e["p10"] <= y <= e["p90"]
            a["pinball"] += (_pinball(y, e["p10"], .1) + _pinball(y, e["median"], .5) + _pinball(y, e["p90"], .9)) / 3 / e["letzter"]
        else:
            a["pinball"] += _pinball(y, e["median"], .5) / e["letzter"]
    return {m: {"n": a["n"], "abdeckung_pct": round(100 * a["treffer"] / a["n_band"], 1) if a["n_band"] else None,
                "pinball_pct": round(100 * a["pinball"] / a["n"], 4), "median_fehler_pct": round(100 * a["fehler"] / a["n"], 3)}
            for m, a in acc.items() if a["n"]}
