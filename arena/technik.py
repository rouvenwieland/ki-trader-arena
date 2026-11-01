"""Technische Analyse und Regime-Kennzahlen (reines Python, gleiche Ergebnisse für alle Modelle).

Ersetzt die in der Recherche gefundenen Bibliotheken (TA-Lib/pandas-ta, Hurst, Regime-Erkennung), ohne neue Abhängigkeiten:
SMA/EMA, RSI, MACD, Bollinger, ATR, realisierte Volatilität, Drawdown, Z-Score, Hurst-Exponent, Autokorrelation, Beta/Korrelation zu
einem Vergleichswert, Volatilitätsregime. Werte sind Beschreibungen der Vergangenheit, keine Prognosen."""
from __future__ import annotations

import math


def sma(x: list[float], n: int) -> float | None:
    return sum(x[-n:]) / n if len(x) >= n else None


def ema_reihe(x: list[float], n: int) -> list[float]:
    if not x:
        return []
    k, out = 2 / (n + 1), [x[0]]
    for v in x[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def rsi(x: list[float], n: int = 14) -> float | None:
    if len(x) <= n:
        return None
    g = [max(0.0, b - a) for a, b in zip(x, x[1:])]
    v = [max(0.0, a - b) for a, b in zip(x, x[1:])]
    ag, av = sum(g[:n]) / n, sum(v[:n]) / n
    for gi, vi in zip(g[n:], v[n:]):  # Wilder-Glättung
        ag, av = (ag * (n - 1) + gi) / n, (av * (n - 1) + vi) / n
    return 100.0 if av == 0 else 100 - 100 / (1 + ag / av)


def macd(x: list[float]) -> dict | None:
    if len(x) < 35:
        return None
    linie = [a - b for a, b in zip(ema_reihe(x, 12), ema_reihe(x, 26))]
    signal = ema_reihe(linie, 9)
    return {"macd": linie[-1], "signal": signal[-1], "histogramm": linie[-1] - signal[-1],
            "kreuzung": "aufwärts" if linie[-2] <= signal[-2] and linie[-1] > signal[-1] else
                        "abwärts" if linie[-2] >= signal[-2] and linie[-1] < signal[-1] else "keine"}


def bollinger(x: list[float], n: int = 20, k: float = 2.0) -> dict | None:
    if len(x) < n:
        return None
    w = x[-n:]
    m = sum(w) / n
    s = math.sqrt(sum((v - m) ** 2 for v in w) / n)
    return {"mitte": m, "oben": m + k * s, "unten": m - k * s, "prozent_b": (x[-1] - (m - k * s)) / (2 * k * s) if s else 0.5,
            "breite_pct": 200 * k * s / m if m else None}


def atr(hoch: list[float], tief: list[float], schluss: list[float], n: int = 14) -> float | None:
    if len(schluss) <= n:
        return None
    tr = [max(h - t, abs(h - c0), abs(t - c0)) for h, t, c0 in zip(hoch[1:], tief[1:], schluss[:-1])]
    return sum(tr[-n:]) / n


def renditen(x: list[float]) -> list[float]:
    return [math.log(b / a) for a, b in zip(x, x[1:]) if a > 0 and b > 0]


def real_vola(x: list[float], n: int, perioden_je_jahr: float) -> float | None:
    r = renditen(x)[-n:]
    if len(r) < max(5, n // 2):
        return None
    m = sum(r) / len(r)
    return math.sqrt(sum((v - m) ** 2 for v in r) / (len(r) - 1) * perioden_je_jahr) * 100


def hurst(x: list[float]) -> float | None:
    """Hurst-Exponent über die Varianz aggregierter Renditen: ≈ 0,5 Zufall, > 0,5 Trend, < 0,5 Rückkehr zum Mittel."""
    r = renditen(x)
    if len(r) < 64:
        return None
    lags, werte = [], []
    for lag in (1, 2, 4, 8, 16):
        summen = [sum(r[i:i + lag]) for i in range(0, len(r) - lag + 1, lag)]
        if len(summen) < 4:
            continue
        m = sum(summen) / len(summen)
        var = sum((s - m) ** 2 for s in summen) / (len(summen) - 1)
        if var > 0:
            lags.append(math.log(lag))
            werte.append(math.log(var))
    if len(lags) < 3:
        return None
    mx, my = sum(lags) / len(lags), sum(werte) / len(werte)
    steigung = sum((a - mx) * (b - my) for a, b in zip(lags, werte)) / sum((a - mx) ** 2 for a in lags)
    return steigung / 2


def autokorrelation(x: list[float], lag: int = 1) -> float | None:
    r = renditen(x)
    if len(r) < 30:
        return None
    m = sum(r) / len(r)
    nenner = sum((v - m) ** 2 for v in r)
    return sum((a - m) * (b - m) for a, b in zip(r, r[lag:])) / nenner if nenner else None


def beta_korrelation(x: list[float], y: list[float]) -> dict | None:
    """Beta und Korrelation der Renditen von x gegen y (gleiche Länge/Zeitpunkte vorausgesetzt)."""
    a, b = renditen(x), renditen(y)
    n = min(len(a), len(b))
    if n < 20:
        return None
    a, b = a[-n:], b[-n:]
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((u - ma) * (v - mb) for u, v in zip(a, b)) / (n - 1)
    va, vb = sum((u - ma) ** 2 for u in a) / (n - 1), sum((v - mb) ** 2 for v in b) / (n - 1)
    return {"beta": cov / vb if vb else None, "korrelation": cov / math.sqrt(va * vb) if va and vb else None, "n": n}


def analyse(kerzen: list[tuple[float, float, float, float]], perioden_je_jahr: float, vergleich: list[float] | None = None) -> dict:
    """kerzen: [(hoch, tief, schluss, zeit)] aufsteigend. Liefert eine kompakte Übersicht aller Kennzahlen."""
    h = [k[0] for k in kerzen]
    t = [k[1] for k in kerzen]
    c = [k[2] for k in kerzen]
    if len(c) < 20:
        return {"fehler": "zu wenig Kursdaten"}
    spitze = max(c)
    v_kurz, v_lang = real_vola(c, 20, perioden_je_jahr), real_vola(c, min(len(c) - 1, 120), perioden_je_jahr)
    m20 = sma(c, 20)
    s20 = math.sqrt(sum((v - m20) ** 2 for v in c[-20:]) / 20) if m20 else None
    out = {"letzter": c[-1], "sma20": sma(c, 20), "sma50": sma(c, 50), "sma200": sma(c, 200),
           "ema12": ema_reihe(c, 12)[-1], "ema26": ema_reihe(c, 26)[-1], "rsi14": rsi(c), "macd": macd(c), "bollinger20": bollinger(c),
           "atr14": atr(h, t, c), "vola_20_pa_pct": v_kurz, "vola_lang_pa_pct": v_lang,
           "vola_regime": None if not (v_kurz and v_lang) else "hoch" if v_kurz > 1.3 * v_lang else "niedrig" if v_kurz < 0.7 * v_lang else "normal",
           "drawdown_vom_hoch_pct": (c[-1] / spitze - 1) * 100, "zscore20": (c[-1] - m20) / s20 if s20 else None,
           "hurst": hurst(c), "autokorrelation_lag1": autokorrelation(c),
           "trend": "aufwärts" if sma(c, 50) and c[-1] > sma(c, 50) > (sma(c, 200) or 0) else "abwärts" if sma(c, 50) and c[-1] < sma(c, 50) else "seitwärts"}
    if vergleich:
        out["gegen_vergleich"] = beta_korrelation(c, vergleich)
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}
