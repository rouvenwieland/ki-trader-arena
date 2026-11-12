"""Woechentliche Brier-Auswertung je Agent (Fonds): schreibt reports/brier-<Jahr>-W<nn>.md und .json.
Aufruf: python -m arena.auswertung. Nutzt metrics.brier (erste Schaetzung je Markt, nur aufgeloeste Maerkte)."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from arena import config, funds, metrics


def brier_score(p: list[float], y: list[float]) -> float | None:
    """Mittlere quadratische Abweichung (0 = perfekt, 0,25 = Muenzwurf)."""
    return sum((a - b) ** 2 for a, b in zip(p, y)) / len(p) if p else None


def tabelle(jetzt: float | None = None) -> list[dict]:
    zeilen = []
    for d in funds.alle_definitionen():
        k = metrics.brier(d["id"])
        if not k.get("n") and not k.get("offen"):
            continue
        zeilen.append({"fonds": d["id"], "name": d["name"], "n": k["n"], "offen": k.get("offen", 0), "brier": k["brier"],
                       "brier_markt": k.get("brier_markt"), "skill_gegen_markt": k.get("brier_skill_markt")})
    return sorted(zeilen, key=lambda z: (z["brier"] is None, z["brier"] if z["brier"] is not None else 0))


def lauf(jetzt: float | None = None) -> str:
    jetzt = jetzt or time.time()
    t = datetime.fromtimestamp(jetzt, timezone.utc)
    j, w, _ = t.isocalendar()
    zeilen = tabelle(jetzt)
    f = lambda x: "-" if x is None else f"{x:.3f}"  # noqa: E731
    md = [f"# Brier je Agent, {j}-W{w:02d}", "", "Kleiner ist besser (0,25 = Muenzwurf). Nur aufgeloeste Maerkte, erste Schaetzung je Markt.", "",
          "| Agent | n | offen | Brier | Brier Markt | Skill gegen Markt |", "|---|---|---|---|---|---|"]
    md += [f"| {z['name']} | {z['n']} | {z['offen']} | {f(z['brier'])} | {f(z['brier_markt'])} | {f(z['skill_gegen_markt'])} |" for z in zeilen]
    out = config.ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / f"brier-{j}-W{w:02d}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out / f"brier-{j}-W{w:02d}.json").write_text(json.dumps(zeilen, ensure_ascii=False, indent=1), encoding="utf-8")
    return f"{j}-W{w:02d}"


if __name__ == "__main__":
    print("Brier-Auswertung:", lauf())
