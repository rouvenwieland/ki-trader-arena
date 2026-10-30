"""Gegenprobe: Kronos-small genau wie scripts/prognosen.py (8 einzelne predict-Aufrufe) für 6 Ursprünge."""
import json, os, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, os.environ["KRONOS_DIR"])
from model import Kronos, KronosPredictor, KronosTokenizer
k = np.array(json.load(open(sys.argv[1])), dtype=np.float64); H = 24
pred = KronosPredictor(Kronos.from_pretrained("NeoQuasar/Kronos-small"), KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base"), device="cpu", max_context=512)
T = len(k); bw, cov, t0 = [], [], time.time()
for u in [T - H - i * 24 for i in range(6)]:
    df = pd.DataFrame(k[u - 400:u], columns=["t", "low", "high", "open", "close", "volume"])
    xt = pd.to_datetime(df["t"], unit="s"); yt = pd.Series(pd.date_range(xt.iloc[-1] + pd.Timedelta(hours=1), periods=H, freq="h"))
    pf = np.array([pred.predict(df=df[["open", "high", "low", "close", "volume"]], x_timestamp=xt, y_timestamp=yt, pred_len=H, T=1.0, top_p=0.9, sample_count=1, verbose=False)["close"].to_numpy() for _ in range(8)])
    L = df["close"].iloc[-1]; p10, p90 = np.quantile(pf[:, -1], [.1, .9]); y = k[u + H - 1, 4]
    bw.append((p90 - p10) / L * 100); cov.append(p10 <= y <= p90)
print(json.dumps({"breite_mittel_%": round(float(np.mean(bw)), 2), "abdeckung": float(np.mean(cov)), "s_pro_ursprung": round((time.time() - t0) / 6, 1)}))
