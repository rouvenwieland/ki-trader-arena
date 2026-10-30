"""Lagedaten aus öffentlichen Feeds (statt OSIRIS): USGS, GDACS, NOAA. NASA FIRMS nur mit freiem MAP_KEY
(Umgebungsvariable NASA_FIRMS_KEY), OpenSanctions wird nicht abgefragt (API verlangt Schlüssel/Lizenz)."""
from __future__ import annotations

import os
import time

from arena.data.http import HttpFehler, get


def usgs() -> list[dict]:
    try:
        d = get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson", ttl=600)
    except HttpFehler:
        return []
    return [{"quelle": "USGS", "typ": "erdbeben", "staerke": f["properties"]["mag"], "ort": f["properties"]["place"],
             "zeit": f["properties"]["time"] / 1000, "tsunami": bool(f["properties"].get("tsunami"))} for f in d["features"][:15]]


def gdacs() -> list[dict]:
    try:
        d = get("https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH", {"alertlevel": "Orange;Red"}, ttl=600)
    except HttpFehler:
        return []
    out = []
    for f in d.get("features", [])[:15]:
        p = f["properties"]
        out.append({"quelle": "GDACS", "typ": p.get("eventtype"), "alarm": p.get("alertlevel"), "ort": p.get("country") or p.get("name"),
                    "titel": p.get("name"), "zeit": p.get("fromdate")})
    return out


def noaa() -> list[dict]:
    try:
        d = get("https://api.weather.gov/alerts/active", {"severity": "Extreme"}, ttl=600)
    except HttpFehler:
        return []
    return [{"quelle": "NOAA", "typ": f["properties"]["event"], "ort": f["properties"]["areaDesc"][:80],
             "titel": f["properties"]["headline"]} for f in d.get("features", [])[:10]]


def firms() -> list[dict]:
    key = os.environ.get("NASA_FIRMS_KEY", "").strip()
    if not key:
        return []
    try:
        txt = get(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/VIIRS_SNPP_NRT/world/1", text=True, ttl=3600)
    except HttpFehler:
        return []
    return [{"quelle": "NASA FIRMS", "typ": "brandherde", "anzahl": max(0, len(txt.splitlines()) - 1)}]


def lagebild() -> dict:
    return {"ts": time.time(), "erdbeben": usgs(), "katastrophen": gdacs(), "wetterwarnungen": noaa(), "brandherde": firms(),
            "hinweis": "OpenSanctions und NASA FIRMS benötigen einen Schlüssel/Lizenz und sind ohne diese nicht abgefragt."}
