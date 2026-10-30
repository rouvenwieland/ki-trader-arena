"""Makrodaten: FRED-CSV-Export (ohne Schlüssel) mit Ausfalltoleranz."""
from __future__ import annotations

import os
import re
import time
from datetime import datetime, timezone

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
    res: dict = {"termine": termine() or "keine Termine abrufbar"}
    for sid, name in SERIEN.items():
        s = serie(sid)
        if s:
            res[sid] = {"name": name, "letzte": s}
    if len(res) == 1:
        res["hinweis"] = "FRED derzeit nicht erreichbar."
    return res


MONATE = {m: i + 1 for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September",
                                          "October", "November", "December"])}


def fomc_termine() -> list[dict]:
    """FOMC-Sitzungen aus dem öffentlichen Kalender der Fed (HTML, gemeinfrei). Stern = mit Projektionen (SEP)."""
    try:
        t = get("https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm", text=True, ttl=86400, versuche=2)
    except HttpFehler:
        return []
    out = []
    for jahr in re.findall(r"(\d{4}) FOMC Meetings", t):
        i = t.find(f"{jahr} FOMC Meetings")
        seg = t[i:i + 25000]
        j = seg.find("FOMC Meetings", 30)
        seg = seg[:j] if j > 0 else seg
        for mon, tage in re.findall(r"fomc-meeting__month[^>]*>\s*<strong>([^<]+)</strong>.*?fomc-meeting__date[^>]*>([^<]+)<", seg, re.S):
            m = MONATE.get(mon.split("/")[-1].strip())
            letzter = re.findall(r"\d+", tage)
            if not m or not letzter:
                continue
            try:
                d = datetime(int(jahr), m, int(letzter[-1]), 18, 0, tzinfo=timezone.utc)  # Statement ~14:00 ET am letzten Tag
            except ValueError:
                continue
            out.append({"termin": "FOMC-Entscheid" + (" (mit Projektionen)" if "*" in tage else ""), "datum": d.strftime("%Y-%m-%d"), "ts": d.timestamp()})
    return out


def release_termine(tage: int = 14) -> list[dict]:
    """Veröffentlichungstermine wichtiger US-Daten über FRED `releases/dates` – nur mit Gratis-Schlüssel FRED_API_KEY (sonst leer)."""
    key = os.environ.get("FRED_API_KEY", "").strip()
    if not key:
        return []
    heute = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        d = get("https://api.stlouisfed.org/fred/releases/dates", {"api_key": key, "file_type": "json", "realtime_start": heute,
                "include_release_dates_with_no_data": "true", "limit": 400, "sort_order": "asc"}, ttl=21600, versuche=2)
    except HttpFehler:
        return []
    wichtig = ("Employment Situation", "Consumer Price Index", "Personal Income", "Gross Domestic Product", "Producer Price",
               "Retail Sales", "Unemployment Insurance", "Job Openings", "Industrial Production", "Housing Starts")
    grenze = time.time() + tage * 86400
    out = []
    for r in d.get("release_dates", []):
        try:
            ts = datetime.fromisoformat(r["date"]).replace(tzinfo=timezone.utc).timestamp()
        except (KeyError, ValueError):
            continue
        if ts <= grenze and any(w in r.get("release_name", "") for w in wichtig):
            out.append({"termin": r["release_name"], "datum": r["date"], "ts": ts})
    return out


def termine(tage: int = 21) -> list[dict]:
    """Kommende Termine (FOMC + FRED-Releases, falls Schlüssel) im Fenster der nächsten `tage` Tage."""
    jetzt = time.time()
    fomc = [x for x in fomc_termine() if x["ts"] > jetzt - 86400]
    alle = [x for x in fomc + release_termine(tage) if x["ts"] < jetzt + tage * 86400]
    if fomc and fomc[0] not in alle:  # die nächste Fed-Entscheidung immer zeigen
        alle.append(fomc[0])
    return sorted(alle, key=lambda x: x["ts"])
