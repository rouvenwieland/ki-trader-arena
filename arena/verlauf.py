"""Kursverlauf der beobachteten Instrumente (append-only, ein File je Tag)."""
from __future__ import annotations

import time
from datetime import datetime, timezone

from arena import store


def _datei(t: float) -> str:
    return "history/preise-" + datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") + ".jsonl"


def tick_anhaengen(t: float, preise: dict[str, float]) -> None:
    runde = {k: (round(v, 6) if v < 10 else round(v, 3)) for k, v in preise.items() if v is not None}
    store.anhaengen(_datei(t), {"t": int(t), "p": runde})


def lade(stunden: float = 50, jetzt: float | None = None) -> dict[str, list[tuple[float, float]]]:
    jetzt = jetzt or time.time()
    out: dict[str, list[tuple[float, float]]] = {}
    tage = {_datei(jetzt - i * 86400) for i in range(int(stunden // 24) + 2)}
    for d in sorted(tage):
        for z in store.lies_jsonl(d):
            if z["t"] < jetzt - stunden * 3600:
                continue
            for k, v in z["p"].items():
                out.setdefault(k, []).append((z["t"], v))
    return out


def vor(serie: list[tuple[float, float]], jetzt: float, stunden: float) -> float | None:
    """Preis in der Serie, der am nächsten an `jetzt - stunden` liegt (innerhalb ±40 % Toleranz)."""
    ziel = jetzt - stunden * 3600
    best = min(serie, key=lambda x: abs(x[0] - ziel), default=None)
    if best and abs(best[0] - ziel) <= stunden * 3600 * 0.4:
        return best[1]
    return None
