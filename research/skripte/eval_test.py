"""Funktionstest: ehrliche Kennzahlen fuer die Arena auf synthetischen Daten (kein Repo-Code, keine Schluessel)."""
import math
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(42)
N_TAGE = 60          # ~2 Monate Vorwaertstest
N_FONDS = 12         # 3 Claude + Liga + Vergleichsfonds -> Anzahl "Versuche"

# --- 1) Renditen: alle Fonds ohne echten Vorteil (mu=0), einer zufaellig "gluecklich"
R = rng.normal(0.0, 0.02, size=(N_TAGE, N_FONDS))
sr_tag = R.mean(0) / R.std(0, ddof=1)
best = int(np.argmax(sr_tag))
r = R[:, best]


def psr(r, sr_ref=0.0):
    """Probabilistic Sharpe Ratio (Bailey & Lopez de Prado 2012), nicht annualisiert."""
    n = len(r); sr = r.mean() / r.std(ddof=1)
    g3 = stats.skew(r); g4 = stats.kurtosis(r, fisher=False)
    z = (sr - sr_ref) * math.sqrt(n - 1) / math.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr**2)
    return stats.norm.cdf(z)


def sr0_erwartet_max(var_sr, n_versuche):
    """Erwarteter maximaler Sharpe unter H0 bei N unabhaengigen Versuchen (DSR-Schwelle)."""
    em = 0.5772156649
    return math.sqrt(var_sr) * ((1 - em) * stats.norm.ppf(1 - 1 / n_versuche) + em * stats.norm.ppf(1 - 1 / (n_versuche * math.e)))


def min_trl(r, sr_ref=0.0, alpha=0.05):
    sr = r.mean() / r.std(ddof=1)
    g3 = stats.skew(r); g4 = stats.kurtosis(r, fisher=False)
    if sr <= sr_ref:
        return math.inf
    return 1 + (1 - g3 * sr + (g4 - 1) / 4 * sr**2) * (stats.norm.ppf(1 - alpha) / (sr - sr_ref)) ** 2


sr0 = sr0_erwartet_max(np.var(sr_tag, ddof=1), N_FONDS)
print(f"Bester Fonds #{best}: SR/Tag={sr_tag[best]:.3f}, annualisiert={sr_tag[best]*math.sqrt(365):.2f}")
print(f"PSR(SR*=0)={psr(r):.3f}  |  DSR (SR*=E[max]={sr0:.3f}/Tag)={psr(r, sr0):.3f}")
print(f"MinTRL fuer 95% (gg. SR*=0): {min_trl(r):.0f} Tage")

import quantstats as qs
s = pd.Series(r, index=pd.date_range("2026-11-01", periods=N_TAGE, freq="D"))
print(f"quantstats sharpe(periods=365)={qs.stats.sharpe(s, periods=365):.3f}  (Kontrolle: {sr_tag[best]*math.sqrt(365):.3f})")

# --- 2) Bootstrap-KI (stationaerer Block-Bootstrap, arch) fuer den Sharpe
from arch.bootstrap import StationaryBootstrap, SPA
bs = StationaryBootstrap(5, r, seed=1)
ci = bs.conf_int(lambda x: np.array([x.mean() / x.std(ddof=1) * math.sqrt(365)]), reps=2000, method="percentile")
print(f"95%-KI Sharpe annualisiert (Block-Bootstrap): [{ci[0,0]:.2f}, {ci[1,0]:.2f}]")

# --- 3) Hansen-SPA: schlaegt irgendein Fonds den Benchmark (BTC Buy&Hold) nach Datenschnueffel-Korrektur?
bench = rng.normal(0.0, 0.025, N_TAGE)
verlust_bench = -bench; verlust_fonds = -R
spa = SPA(verlust_bench, verlust_fonds, reps=1000, block_size=5, seed=1)
spa.compute()
print("SPA p-Werte (lower, consistent, upper):", np.round(spa.pvalues.values, 3))

# --- 4) Wettmarkt-Prognosen: Brier, Murphy-Zerlegung, BSS gegen Markt, Log-Score, Diebold-Mariano
M = 150
wahr_p = rng.uniform(0.05, 0.95, M)
y = (rng.uniform(size=M) < wahr_p).astype(float)
markt = np.clip(wahr_p + rng.normal(0, 0.05, M), 0.01, 0.99)     # Markt gut informiert
llm = np.clip(wahr_p + rng.normal(0, 0.12, M), 0.01, 0.99)       # LLM verrauschter


def brier(p, y):
    return np.mean((p - y) ** 2)


def murphy(p, y, bins=10):
    """Brier = REL - RES + UNC (Murphy 1973), binned."""
    kl = np.minimum((p * bins).astype(int), bins - 1)
    ybar = y.mean(); rel = res = 0.0
    for k in range(bins):
        m = kl == k
        if m.any():
            nk = m.sum(); pk = p[m].mean(); ok = y[m].mean()
            rel += nk * (pk - ok) ** 2; res += nk * (ok - ybar) ** 2
    return rel / len(p), res / len(p), ybar * (1 - ybar)


for name, p in (("LLM", llm), ("Markt", markt)):
    rel, res, unc = murphy(p, y)
    print(f"{name}: Brier={brier(p,y):.4f}  REL={rel:.4f} RES={res:.4f} UNC={unc:.4f} (REL-RES+UNC={rel-res+unc:.4f})")
bss = 1 - brier(llm, y) / brier(markt, y)
print(f"Brier-Skill-Score LLM gg. Markt: {bss:+.3f} (>0 = besser als Marktpreis)")

import scoringrules as sr_
ls_llm = sr_.log_score(y, llm) if hasattr(sr_, "log_score") else None
bs_llm = sr_.brier_score(y, llm)
print("scoringrules brier_score mean:", round(float(np.mean(bs_llm)), 4), "| log_score vorhanden:", ls_llm is not None)
logloss = lambda p: -(y * np.log(p) + (1 - y) * np.log(1 - p))
print(f"Log-Score LLM={logloss(llm).mean():.4f}  Markt={logloss(markt).mean():.4f}")

d = (llm - y) ** 2 - (markt - y) ** 2          # Verlustdifferenz je Frage
dm = d.mean() / (d.std(ddof=1) / math.sqrt(M))  # unabhaengige Fragen -> h=1, kein HAC noetig
print(f"Diebold-Mariano (Brier) t={dm:.2f}, p={2*(1-stats.norm.cdf(abs(dm))):.4f}")
# Fragen-Bootstrap wie ForecastBench
idx = rng.integers(0, M, size=(1999, M))
bss_bs = 1 - ((llm[idx] - y[idx]) ** 2).mean(1) / ((markt[idx] - y[idx]) ** 2).mean(1)
print(f"BSS-95%-KI (Fragen-Bootstrap, 1999x): [{np.percentile(bss_bs,2.5):+.3f}, {np.percentile(bss_bs,97.5):+.3f}]")

# --- 5) Mindest-Stichprobe: wie viele aufgeloeste Fragen braucht man, um Brier-Diff delta zu sehen?
sd_d = d.std(ddof=1)
for delta in (0.005, 0.01, 0.02):
    n_req = ((stats.norm.ppf(0.975) + stats.norm.ppf(0.8)) * sd_d / delta) ** 2
    print(f"Fragen fuer Brier-Diff {delta}: ~{n_req:.0f} (alpha 5%, Power 80%, sd(d)={sd_d:.3f})")

# --- 6) Kosten-adjustiert
pnl_usd, api_eur, fx = 180.0, 35.0, 1.08
print(f"Netto nach API: {pnl_usd - api_eur*fx:.1f} USD; PnL je API-EUR: {pnl_usd/api_eur:.2f} USD/EUR")
