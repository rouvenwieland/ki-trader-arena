"""Makrodaten: FRED-CSV-Export (ohne Schlüssel) mit Ausfalltoleranz."""
from __future__ import annotations

from arena.data.http import HttpFehler, get

SERIEN = {"DFF": "Leitzins (Fed Funds, täglich)", "DGS10": "US-Rendite 10 Jahre", "DGS2": "US-Rendite 2 Jahre",
          "T10Y2Y": "Zinsstruktur 10J-2J", "VIXCLS": "VIX", "CPIAUCSL": "Verbraucherpreise (Index)", "UNRATE": "Arbeitslosenquote",
          "DEXUSEU": "USD je EUR", "SP500": "S&P 500 Index", "DCOILWTICO": "Ölpreis WTI"}


def serie(sid: str, n: int = 5) -> list[tuple[str, float]]:
    try:
        txt = get("https://fred.stlouisfed.org/graph/fredgraph.csv", {"id": sid}, text=True, ttl=3600, versuche=2, timeout=25)
    except HttpFehler:
        return []
    out = []
    for z in txt.strip().splitlines()[1:]:
        d, _, v = z.partition(",")
        try:
            out.append((d, float(v)))
        except ValueError:
            continue
    return out[-n:]


def uebersicht() -> dict:
    res = {}
    for sid, name in SERIEN.items():
        s = serie(sid)
        if s:
            res[sid] = {"name": name, "letzte": s}
    return res or {"hinweis": "FRED derzeit nicht erreichbar."}
