"""Prognosen mit TimesFM 2.5 (Google, Apache-2.0 inkl. Gewichte) und Kronos (Kurskerzen-Modell, MIT) auf CPU.
Schreibt data/prognosen.json (Stundenkerzen BTC/ETH/SOL, Horizont 24 h, mit Unsicherheitsband).
Läuft im Workflow „Prognosen“; jede Modellgruppe einzeln abgesichert – fällt eine aus, bleibt die andere.
Hinweis: TimesFM 3.0 steht unter einer Nicht-kommerziell-Lizenz für die Gewichte und wird bewusst NICHT genutzt."""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arena import store  # noqa: E402
from arena.data import crypto  # noqa: E402

ZIELE = {"spot:BTC-USD": "BTC-USD", "spot:ETH-USD": "ETH-USD", "spot:SOL-USD": "SOL-USD"}
H = 24


def kerzen(sym: str):
    k = crypto.spot_kerzen(sym, 3600, 300)  # [zeit, tief, hoch, offen, schluss, vol]
    return k


def timesfm_lauf(daten: dict) -> dict:
    import timesfm
    import torch
    torch.set_float32_matmul_precision("high")
    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")
    model.compile(timesfm.ForecastConfig(max_context=512, max_horizon=H, normalize_inputs=True, use_continuous_quantile_head=True,
                                         force_flip_invariance=True, infer_is_positive=True, fix_quantile_crossing=True))
    eingaben = [np.array([c[4] for c in k], dtype=np.float32) for k in daten.values()]
    punkt, quant = model.forecast(horizon=H, inputs=eingaben)  # quant: (n, H, 10) = Mittel, q10..q90
    out = {}
    for i, iid in enumerate(daten):
        out[iid] = {"modell": "TimesFM 2.5 (200M, CPU)", "letzter": float(eingaben[i][-1]), "median": [float(x) for x in quant[i][:, 5]],
                    "p10": [float(x) for x in quant[i][:, 1]], "p90": [float(x) for x in quant[i][:, 9]]}
    return out


def kronos_lauf(daten: dict) -> dict:
    import pandas as pd
    sys.path.insert(0, "Kronos")
    from model import Kronos, KronosPredictor, KronosTokenizer
    tok = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
    mod = Kronos.from_pretrained("NeoQuasar/Kronos-small")
    pred = KronosPredictor(mod, tok, device="cpu", max_context=512)
    out = {}
    for iid, k in daten.items():
        df = pd.DataFrame(k[-400:], columns=["t", "low", "high", "open", "close", "volume"])
        x_ts = pd.to_datetime(df["t"], unit="s")
        y_ts = pd.Series(pd.date_range(x_ts.iloc[-1] + pd.Timedelta(hours=1), periods=H, freq="h"))
        pfade = []
        for _ in range(8):  # 8 Pfade → Unsicherheitsband
            p = pred.predict(df=df[["open", "high", "low", "close", "volume"]], x_timestamp=x_ts, y_timestamp=y_ts, pred_len=H,
                             T=1.0, top_p=0.9, sample_count=1, verbose=False)
            pfade.append(p["close"].to_numpy())
        a = np.array(pfade)
        out[iid] = {"modell": "Kronos-small (24.7M, CPU)", "letzter": float(df["close"].iloc[-1]), "median": [float(x) for x in np.median(a, 0)],
                    "p10": [float(x) for x in np.quantile(a, .1, 0)], "p90": [float(x) for x in np.quantile(a, .9, 0)]}
    return out


def main() -> int:
    daten = {iid: kerzen(sym) for iid, sym in ZIELE.items()}
    daten = {k: v for k, v in daten.items() if len(v) >= 200}
    if not daten:
        print("Keine Kerzen – Abbruch")
        return 0
    ergebnis = store.lies("prognosen.json", {})
    jetzt = time.time()
    for name, fn in (("timesfm", timesfm_lauf), ("kronos", kronos_lauf)):
        try:
            for iid, e in fn(daten).items():
                eintrag = ergebnis.setdefault(iid, {})
                eintrag.setdefault("modelle", {})[name] = e
                eintrag["ts"], eintrag["horizont_h"] = jetzt, H
            print(name, "ok")
        except Exception:
            print(name, "FEHLER:")
            traceback.print_exc()
    store.schreibe("prognosen.json", ergebnis)
    return 0


if __name__ == "__main__":
    sys.exit(main())
