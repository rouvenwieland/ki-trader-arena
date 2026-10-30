"""Bewertet alle npz: Pinball (Mittel über 9 Quantile, in % vom letzten Preis), MAE Median (%), Abdeckung 10-90 bei h=24,
Richtungstreffer des Medians bei h=24. Plus Diebold-Mariano-artiger t-Wert ggü. rw-normal (Pinball h=1..24, je Ursprung)."""
import sys, glob, os, json
import numpy as np
QL = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
def pinball(q, y):  # q (N,H,9), y (N,H)
    d = y[..., None] - q
    return np.maximum(QL * d, (QL - 1) * d).mean(2)  # (N,H)
erg = {}
for f in sorted(glob.glob(os.path.join(sys.argv[1], "*.npz"))):
    z = np.load(f); n = os.path.basename(f)[:-4]
    L = z["letzter"][:, None]; q = z["q"] / L[..., None] * 100; y = z["ziel"] / L * 100
    pb = pinball(q, y); mae = np.abs(q[..., 4] - y)
    cov = ((y[:, -1] >= q[:, -1, 0]) & (y[:, -1] <= q[:, -1, 8])).mean()
    med = q[:, -1, 4] - 100
    richt = (np.sign(med) == np.sign(y[:, -1] - 100)) if np.abs(med).max() > 1e-9 else None
    from scipy.stats import spearmanr
    vol = spearmanr(q[:, -1, 8] - q[:, -1, 0], np.abs(y[:, -1] - 100)).correlation if (q[:, -1, 8] - q[:, -1, 0]).std() > 0 else float('nan')
    erg[n] = dict(pb=pb, mae=mae, cov=cov, richt=richt, vol=vol, breite=(q[:, -1, 8] - q[:, -1, 0]).mean(), laden=float(z["laden"]), inf=float(z["inferenz"]))
ref = erg["rw-normal"]["pb"].mean(1)
print("| Modell | Pinball h1-24 (% Preis) | Pinball h=24 | MAE Median h1-24 | Abdeckung 10-90 h=24 | Breite 10-90 h=24 | Richtung h=24 | t-Wert vs RW (neg=besser) | Spearman Breite~|Rendite| h=24 |")
print("|---|---|---|---|---|---|---|---|---|")
for n, e in erg.items():
    d = e["pb"].mean(1) - ref
    t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d))) if d.std() > 0 else 0.0
    print(f"| {n} | {e['pb'].mean():.4f} | {e['pb'][:, -1].mean():.4f} | {e['mae'].mean():.3f} | {e['cov']:.0%} | {e['breite']:.2f} | {('n/a' if e['richt'] is None else format(e['richt'].mean(), '.0%'))} | {t:+.2f} | {e['vol']:+.2f} |")
