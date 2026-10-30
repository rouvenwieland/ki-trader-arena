"""Ehrliche Statistik ohne Zusatzpakete (reines Python): Block-Bootstrap, Probabilistic/Deflated Sharpe, MinTRL,
Brier-Skill gegen den Markt, Murphy-Zerlegung, Kalibrierung (Platt: BIA/CON), Model Confidence Set.

Formeln wie in research/skripte/eval_test.py nachgerechnet (Bailey & López de Prado 2012/2014; Murphy 1973; Hansen, Lunde & Nason 2011).
Alle Zufallszahlen mit festem Startwert → gleiche Daten, gleiche Zahlen auf der Seite."""
from __future__ import annotations

import math
import random
from statistics import NormalDist

N01 = NormalDist()
EULER = 0.5772156649015329


def mittel(x: list[float]) -> float:
    return sum(x) / len(x) if x else 0.0


def sd(x: list[float]) -> float:
    if len(x) < 2:
        return 0.0
    m = mittel(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))


def schiefe_kurtosis(x: list[float]) -> tuple[float, float]:
    """Schiefe und (nicht-Exzess-)Kurtosis; bei Normalverteilung (0, 3)."""
    n = len(x)
    m = mittel(x)
    m2 = sum((v - m) ** 2 for v in x) / n
    if n < 3 or m2 <= 0:
        return 0.0, 3.0
    m3 = sum((v - m) ** 3 for v in x) / n
    m4 = sum((v - m) ** 4 for v in x) / n
    return m3 / m2 ** 1.5, m4 / m2 ** 2


def sharpe_periode(r: list[float]) -> float | None:
    s = sd(r)
    return None if len(r) < 3 or s == 0 else mittel(r) / s


def psr(r: list[float], sr_ref: float = 0.0) -> float | None:
    """Probabilistic Sharpe Ratio: Wahrscheinlichkeit, dass der wahre Sharpe (je Periode) über sr_ref liegt."""
    sr = sharpe_periode(r)
    if sr is None:
        return None
    g3, g4 = schiefe_kurtosis(r)
    nenner = 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2
    if nenner <= 0:
        return None
    return N01.cdf((sr - sr_ref) * math.sqrt(len(r) - 1) / math.sqrt(nenner))


def sr0_erwartet_max(var_sr: float, n_versuche: int) -> float:
    """Erwarteter maximaler Sharpe unter „kein Können“ bei N Versuchen (Schwelle des Deflated Sharpe)."""
    if n_versuche < 2 or var_sr <= 0:
        return 0.0
    return math.sqrt(var_sr) * ((1 - EULER) * N01.inv_cdf(1 - 1 / n_versuche) + EULER * N01.inv_cdf(1 - 1 / (n_versuche * math.e)))


def min_trl(r: list[float], sr_ref: float = 0.0, alpha: float = 0.05) -> float | None:
    """Minimum Track Record Length in Perioden: so lange muss die Reihe bei gleicher Güte laufen, bis SR > sr_ref mit 1−alpha belegt ist."""
    sr = sharpe_periode(r)
    if sr is None or sr <= sr_ref:
        return None
    g3, g4 = schiefe_kurtosis(r)
    return 1 + (1 - g3 * sr + (g4 - 1) / 4 * sr ** 2) * (N01.inv_cdf(1 - alpha) / (sr - sr_ref)) ** 2


def stationaer_indizes(n: int, block: float, rng: random.Random) -> list[int]:
    """Stationärer Bootstrap (Politis & Romano): Blöcke mit geometrischer Länge (Mittel `block`), zirkulär."""
    p = 1 / max(block, 1.0)
    out, i = [], rng.randrange(n)
    for _ in range(n):
        out.append(i)
        i = rng.randrange(n) if rng.random() < p else (i + 1) % n
    return out


def bootstrap_ki(r: list[float], stat, block: float = 24, reps: int = 1000, niveau: float = 0.95, seed: int = 1) -> tuple[float, float] | None:
    """Perzentil-KI einer Statistik stat(liste) per stationärem Block-Bootstrap."""
    if len(r) < 10:
        return None
    rng = random.Random(seed)
    werte = sorted(stat([r[i] for i in stationaer_indizes(len(r), block, rng)]) for _ in range(reps))
    a = (1 - niveau) / 2
    return werte[int(a * (reps - 1))], werte[int((1 - a) * (reps - 1))]


def p_wert_mehr(d: list[float], block: float = 24, reps: int = 1000, seed: int = 2) -> float | None:
    """Einseitiger p-Wert für „mittlere Differenz > 0“ (z. B. Fonds- minus BTC-Rendite je Stunde), Block-Bootstrap unter H0 (zentriert)."""
    if len(d) < 10:
        return None
    m = mittel(d)
    z = [x - m for x in d]
    rng = random.Random(seed)
    groesser = sum(1 for _ in range(reps) if mittel([z[i] for i in stationaer_indizes(len(z), block, rng)]) >= m)
    return (groesser + 1) / (reps + 1)


# ---------------------------------------------------------------- Prognosen (binär)
def brier(p: list[float], y: list[float]) -> float:
    return mittel([(a - b) ** 2 for a, b in zip(p, y)])


def log_score(p: list[float], y: list[float]) -> float:
    """Mittlerer Log-Verlust (kleiner = besser), p auf [0,01; 0,99] begrenzt."""
    return mittel([-math.log(min(max(a, 0.01), 0.99) if b >= 0.5 else 1 - min(max(a, 0.01), 0.99)) for a, b in zip(p, y)])


def murphy(p: list[float], y: list[float], bins: int = 10) -> dict:
    """Brier ≈ Zuverlässigkeit − Auflösung + Unsicherheit (Murphy 1973), in 10 Klassen."""
    n = len(p)
    ybar = mittel(y)
    rel = res = 0.0
    kurve = []
    for k in range(bins):
        idx = [i for i in range(n) if min(int(p[i] * bins), bins - 1) == k]
        if not idx:
            continue
        pk = mittel([p[i] for i in idx])
        ok = mittel([y[i] for i in idx])
        rel += len(idx) * (pk - ok) ** 2
        res += len(idx) * (ok - ybar) ** 2
        kurve.append({"p": round(pk, 3), "anteil_ja": round(ok, 3), "n": len(idx)})
    return {"zuverlaessigkeit": rel / n, "aufloesung": res / n, "unsicherheit": ybar * (1 - ybar), "kurve": kurve}


def platt(p: list[float], y: list[float], iter_: int = 50) -> tuple[float, float] | None:
    """Logistische Rekalibrierung logit(q) = a + b·logit(p) (Newton). a > 0 heißt: JA wird unterschätzt; b < 1: überkonfident."""
    if len(p) < 5 or len(set(y)) < 2:
        return None
    xs = [math.log(min(max(v, 0.01), 0.99) / (1 - min(max(v, 0.01), 0.99))) for v in p]
    a, b = 0.0, 1.0
    for _ in range(iter_):
        ga = gb = haa = hab = hbb = 0.0
        for x, t in zip(xs, y):
            q = 1 / (1 + math.exp(-(a + b * x)))
            w = q * (1 - q)
            ga += t - q
            gb += (t - q) * x
            haa += w
            hab += w * x
            hbb += w * x * x
        det = haa * hbb - hab * hab
        if abs(det) < 1e-12:
            break
        da = (hbb * ga - hab * gb) / det
        db = (haa * gb - hab * ga) / det
        a, b = a + da, b + db
        a, b = max(-5.0, min(5.0, a)), max(0.05, min(5.0, b))
        if abs(da) + abs(db) < 1e-8:
            break
    return a, b


def rekalibriere(p: float, ab: tuple[float, float] | None) -> float:
    if not ab:
        return p
    x = math.log(min(max(p, 0.01), 0.99) / (1 - min(max(p, 0.01), 0.99)))
    return 1 / (1 + math.exp(-(ab[0] + ab[1] * x)))


def fragen_bootstrap_ki(werte: list[float], reps: int = 1000, seed: int = 3) -> tuple[float, float] | None:
    """KI des Mittelwerts unabhängiger Fragen (z. B. marktbereinigter Brier je Frage), wie bei ForecastBench."""
    if len(werte) < 5:
        return None
    rng = random.Random(seed)
    n = len(werte)
    m = sorted(mittel([werte[rng.randrange(n)] for _ in range(n)]) for _ in range(reps))
    return m[int(0.025 * (reps - 1))], m[int(0.975 * (reps - 1))]


# ---------------------------------------------------------------- Model Confidence Set
def model_confidence_set(verluste: dict[str, list[float]], alpha: float = 0.1, block: float = 24, reps: int = 500,
                         seed: int = 4) -> dict:
    """MCS nach Hansen/Lunde/Nason mit T_max-Statistik und stationärem Block-Bootstrap.
    verluste: Modell → Verlustreihe gleicher Länge (z. B. −Stundenrendite). Liefert die Menge der Modelle, die sich auf dem Niveau
    alpha nicht vom besten unterscheiden lassen, und je Modell den MCS-p-Wert (Eliminationsreihenfolge)."""
    namen = [k for k, v in verluste.items() if v]
    if len(namen) < 2:
        return {"menge": namen, "p_werte": {k: 1.0 for k in namen}, "n": len(verluste[namen[0]]) if namen else 0}
    n = min(len(verluste[k]) for k in namen)
    L = {k: verluste[k][-n:] for k in namen}
    rng = random.Random(seed)
    idx = [stationaer_indizes(n, block, rng) for _ in range(reps)]
    aktiv = list(namen)
    p_werte: dict[str, float] = {}
    p_max = 0.0
    while len(aktiv) > 1:
        lbar = {k: mittel(L[k]) for k in aktiv}
        gesamt = [mittel([L[k][t] for k in aktiv]) for t in range(n)]
        d = {k: [L[k][t] - gesamt[t] for t in range(n)] for k in aktiv}
        dbar = {k: lbar[k] - mittel(gesamt) for k in aktiv}
        boot = {k: [mittel([d[k][i] for i in ix]) - dbar[k] for ix in idx] for k in aktiv}
        var = {k: max(mittel([b * b for b in boot[k]]), 1e-18) for k in aktiv}
        t = {k: dbar[k] / math.sqrt(var[k]) for k in aktiv}
        tmax = max(t.values())
        tmax_boot = [max(boot[k][j] / math.sqrt(var[k]) for k in aktiv) for j in range(reps)]
        p_max = max(p_max, sum(1 for x in tmax_boot if x >= tmax) / reps)
        schlecht = max(aktiv, key=lambda k: t[k])  # bis zum Ende eliminieren → MCS-p-Wert je Modell
        p_werte[schlecht] = p_max
        aktiv.remove(schlecht)
    p_werte[aktiv[0]] = 1.0
    return {"menge": [k for k in namen if p_werte[k] >= alpha], "p_werte": {k: round(v, 3) for k, v in p_werte.items()}, "n": n}
