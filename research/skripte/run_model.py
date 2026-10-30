"""Rechnet für ein Modell Quantilprognosen an N rollenden Ursprüngen (BTC-USD Stundenkerzen).
Aufruf: python run_model.py MODELL daten.json out.npz
Ausgabe: q (N, H, 9) Quantile 0.1..0.9 als Preise; Zeiten für Laden/Inferenz."""
import json, sys, time, os
import numpy as np
name, datei, out = sys.argv[1:4]
H, CTX, N, STEP = 24, 512, 50, 24
QL = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
k = json.load(open(datei)); close = np.array([c[4] for c in k], dtype=np.float64)
T = len(close)
ursprung = [T - H - i * STEP for i in range(N)][::-1]   # Index des ersten Zielpunkts
ctxs = np.stack([close[u - CTX:u] for u in ursprung]).astype(np.float32)
t0 = time.time()
q = None
if name.startswith("chronos"):
    import torch
    from chronos import BaseChronosPipeline
    repo = {"chronos-bolt-tiny": "amazon/chronos-bolt-tiny", "chronos-bolt-small": "amazon/chronos-bolt-small",
            "chronos-2": "amazon/chronos-2"}[name]
    pipe = BaseChronosPipeline.from_pretrained(repo, device_map="cpu", torch_dtype=torch.float32)
    t1 = time.time()
    if name == "chronos-2":
        qq, _ = pipe.predict_quantiles([torch.tensor(c) for c in ctxs], prediction_length=H, quantile_levels=QL)
        q = np.stack([x[0].numpy() for x in qq])  # (N,H,9)
    else:
        qq, _ = pipe.predict_quantiles(torch.tensor(ctxs), prediction_length=H, quantile_levels=QL)
        q = qq.numpy()
elif name == "tirex":
    import torch
    from tirex import load_model
    m = load_model("NX-AI/TiRex", device="cpu")
    t1 = time.time()
    qq, mean = m.forecast(context=torch.tensor(ctxs), prediction_length=H)
    q = np.asarray(qq)  # (N,H,9) Quantile 0.1..0.9
elif name == "ttm-r2":
    import torch
    from tsfm_public.toolkit.get_model import get_model
    m = get_model("ibm-granite/granite-timeseries-ttm-r2", context_length=CTX, prediction_length=H)
    m.eval(); t1 = time.time()
    # TTM ist ein Punktprognose-Modell; eigene Normierung je Fenster zur Sicherheit
    mu = ctxs.mean(1, keepdims=True); sd = ctxs.std(1, keepdims=True)
    with torch.no_grad():
        ft = torch.full((len(ctxs),), 7, dtype=torch.long) if getattr(m.config, 'resolution_prefix_tuning', False) else None  # 7 = stündlich
        p = m(past_values=torch.tensor((ctxs - mu) / sd)[..., None], freq_token=ft).prediction_outputs[..., 0].numpy()
    p = p * sd + mu
    q = np.repeat(p[..., None], 9, axis=2)  # nur Punkt → alle Quantile = Punkt (Pinball dann = MAE-artig)
elif name == "garch":
    from arch import arch_model
    t1 = time.time(); q = np.zeros((N, H, 9))
    from scipy.stats import t as student
    for i, c in enumerate(ctxs.astype(np.float64)):
        r = 100 * np.diff(np.log(c))
        res = arch_model(r, mean="Zero", vol="GARCH", p=1, q=1, dist="t").fit(disp="off")
        var = res.forecast(horizon=H, reindex=False).variance.values[0]  # (H,) pro Schritt
        cumsd = np.sqrt(np.cumsum(var)) / 100
        nu = res.params["nu"]; z = student.ppf(QL, nu) * np.sqrt((nu - 2) / nu)
        q[i] = c[-1] * np.exp(cumsd[:, None] * z[None, :])
elif name in ("rw-normal", "bootstrap"):
    t1 = time.time(); q = np.zeros((N, H, 9)); rng = np.random.default_rng(0)
    from scipy.stats import norm
    for i, c in enumerate(ctxs.astype(np.float64)):
        r = np.diff(np.log(c))
        if name == "rw-normal":
            s = r.std() * np.sqrt(np.arange(1, H + 1))
            q[i] = c[-1] * np.exp(s[:, None] * norm.ppf(QL)[None, :])
        else:  # wie arena/forecast.py: 400 Bootstrap-Pfade aus Stundenrenditen
            pf = np.cumsum(rng.choice(r, size=(400, H)), axis=1)
            q[i] = c[-1] * np.exp(np.quantile(pf, QL, axis=0).T)
elif name in ("autoets", "autoarima"):
    from statsforecast.models import AutoETS, AutoARIMA
    t1 = time.time(); q = np.zeros((N, H, 9))
    for i, c in enumerate(ctxs.astype(np.float64)):
        mdl = (AutoETS(season_length=24) if name == "autoets" else AutoARIMA(season_length=1)).fit(np.log(c))
        f = mdl.predict(h=H, level=[20, 40, 60, 80])
        cols = [f["lo-80"], f["lo-60"], f["lo-40"], f["lo-20"], f["mean"], f["hi-20"], f["hi-40"], f["hi-60"], f["hi-80"]]
        q[i] = np.exp(np.stack(cols, 1))
elif name == "timesfm-2.5":
    import timesfm, torch
    torch.set_float32_matmul_precision("high")
    m = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")
    m.compile(timesfm.ForecastConfig(max_context=512, max_horizon=H, normalize_inputs=True, use_continuous_quantile_head=True,
              force_flip_invariance=True, infer_is_positive=True, fix_quantile_crossing=True))
    t1 = time.time()
    _, qq = m.forecast(horizon=H, inputs=[c for c in ctxs])
    q = np.asarray(qq)[:, :H, 1:10]
elif name.startswith("kronos"):
    import pandas as pd
    sys.path.insert(0, os.environ["KRONOS_DIR"])
    from model import Kronos, KronosPredictor, KronosTokenizer
    tok = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base" if name != "kronos-mini" else "NeoQuasar/Kronos-Tokenizer-2k")
    mod = Kronos.from_pretrained({"kronos-small": "NeoQuasar/Kronos-small", "kronos-mini": "NeoQuasar/Kronos-mini"}[name])
    pred = KronosPredictor(mod, tok, device="cpu", max_context=512)
    t1 = time.time(); P = 8
    kk = np.array(k, dtype=np.float64); dfs, xs, ys = [], [], []
    for u in ursprung:
        df = pd.DataFrame(kk[u - 400:u], columns=["t", "low", "high", "open", "close", "volume"])
        xt = pd.Series(pd.to_datetime(df["t"], unit="s")); yt = pd.Series(pd.date_range(xt.iloc[-1] + pd.Timedelta(hours=1), periods=H, freq="h"))
        for _ in range(P):
            dfs.append(df[["open", "high", "low", "close", "volume"]]); xs.append(xt); ys.append(yt)
    ergeb = pred.predict_batch(dfs, xs, ys, pred_len=H, T=1.0, top_p=0.9, sample_count=1, verbose=False)
    pf = np.array([o["close"].to_numpy() for o in ergeb]).reshape(N, P, H)
    q = np.quantile(pf, QL, axis=1).transpose(1, 2, 0)
elif name.startswith("toto2"):
    import torch
    from toto2 import Toto2Model
    m = Toto2Model.from_pretrained({"toto2-4m": "Datadog/Toto-2.0-4m", "toto2-22m": "Datadog/Toto-2.0-22m"}[name]).eval()
    t1 = time.time()
    tg = torch.tensor(ctxs)[:, None, :]
    with torch.no_grad():
        qq = m.forecast({"target": tg, "target_mask": torch.ones_like(tg, dtype=torch.bool),
                         "series_ids": torch.zeros(len(ctxs), 1, dtype=torch.long)}, horizon=H, decode_block_size=768, has_missing_values=False)
    q = qq[:, :, 0, :].permute(1, 2, 0).numpy()  # (9,N,1,H) -> (N,H,9)
else:
    raise SystemExit("unbekannt")
t2 = time.time()
q = np.sort(np.asarray(q, dtype=np.float64), axis=2)  # Quantil-Kreuzungen glätten
np.savez(out, q=q, ziel=np.stack([close[u:u + H] for u in ursprung]), letzter=ctxs[:, -1].astype(np.float64),
         laden=t1 - t0, inferenz=t2 - t1)
print(json.dumps({"modell": name, "laden_s": round(t1 - t0, 2), "inferenz_s_50": round(t2 - t1, 2)}))
