import sys, json
sys.path.insert(0, sys.argv[1])
import numpy as np, pandas as pd
from forecasting_tools.calibration_adjustment.logistic_recalibration_adjuster import LogisticRecalibrationAdjuster as L
rng = np.random.default_rng(0)
true_p = rng.uniform(0.05, 0.95, 400)
y = rng.random(400) < true_p
# simulierter überkonfidenter, ja-lastiger Agent
from scipy.special import logit, expit
pred = expit(1.8*logit(true_p) + 0.4)
cols = None
df = pd.DataFrame({"type": "binary", "probability_yes": pred, "resolution": np.where(y, "yes", "no")})
a = L()
try:
    a.train(df)
except Exception as e:
    print("train error", type(e).__name__, e); raise
adj = np.array([a.adjust_binary_forecast(p) for p in pred])
brier = lambda p: float(np.mean((p - y)**2))
print("BIA=%.3f CON=%.3f" % (a.bias, a.confidence), "Brier roh=%.4f nach Rekalibrierung=%.4f wahr=%.4f" % (brier(pred), brier(adj), brier(true_p)))
