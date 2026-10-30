"""Wetter-Werkzeug für Temperatur-Wettmärkte (Kalshi „Highest temperature in … on …?“).

Quelle: Open-Meteo-Ensembles (GFS 31 + ECMWF IFS 51 Mitglieder, CC BY 4.0 – Quellenangabe auf der Seite), Tageshöchstwert in °F zur Ortszeit.
P(Bracket) = Mittel über die Mitglieder von P(gerundeter Wert im Bracket) mit normalverteiltem Modellfehler (σ wächst mit dem Vorlauf).
Abrechnung bei Kalshi über den NWS-Klimabericht (CLI) der genannten Station; für den laufenden Tag zeigt das Werkzeug zusätzlich das bisher
beobachtete Maximum der NWS-Station. Ergebnisse werden zwischengespeichert (geteiltes IP-Kontingent der Actions-Runner)."""
from __future__ import annotations

import time
from datetime import datetime, timezone
from statistics import NormalDist
from zoneinfo import ZoneInfo

from arena import store
from arena.data.http import HttpFehler, get

ENSEMBLE = "https://ensemble-api.open-meteo.com/v1/ensemble"
MODELLE = "gfs_seamless,ecmwf_ifs025"
CACHE = "wetter_cache.json"
CACHE_S = 3600

# Kalshi-Serie → Station (Koordinaten der CLI-Messstation, NWS-Stations-ID für Beobachtungen, Zeitzone)
STATIONEN = {
    "KXHIGHNY": ("New York (Central Park)", 40.7789, -73.9692, "KNYC", "America/New_York"),
    "KXHIGHCHI": ("Chicago (Midway)", 41.7861, -87.7522, "KMDW", "America/Chicago"),
    "KXHIGHMIA": ("Miami (Flughafen)", 25.7932, -80.2906, "KMIA", "America/New_York"),
    "KXHIGHAUS": ("Austin (Bergstrom)", 30.1831, -97.6799, "KAUS", "America/Chicago"),
    "KXHIGHLAX": ("Los Angeles (Flughafen)", 33.9382, -118.3866, "KLAX", "America/Los_Angeles"),
    "KXHIGHDEN": ("Denver (Flughafen)", 39.8466, -104.6562, "KDEN", "America/Denver"),
    "KXHIGHPHIL": ("Philadelphia (Flughafen)", 39.8721, -75.2407, "KPHL", "America/New_York"),
    "KXHIGHTBOS": ("Boston (Logan)", 42.3606, -71.0097, "KBOS", "America/New_York"),
    "KXHIGHTSEA": ("Seattle (Sea-Tac)", 47.4447, -122.3144, "KSEA", "America/Los_Angeles"),
    "KXHIGHTATL": ("Atlanta (Flughafen)", 33.6301, -84.4418, "KATL", "America/New_York"),
    "KXHIGHTDC": ("Washington (Reagan)", 38.8483, -77.0342, "KDCA", "America/New_York"),
    "KXHIGHTPHX": ("Phoenix (Sky Harbor)", 33.4277, -112.0038, "KPHX", "America/Phoenix"),
}
N01 = NormalDist()


def fehler_sigma(vorlauf_tage: float) -> float:
    """Modellfehler des Tageshöchstwerts (°F) zusätzlich zur Ensemble-Streuung; konservativ, später aus der Trefferbilanz kalibrieren."""
    return 1.5 + 0.4 * max(0.0, vorlauf_tage)


def ensemble(lat: float, lon: float, tz: str, tage: int = 4) -> dict[str, list[float]]:
    """Datum (Ortszeit) → Tageshöchstwerte aller Ensemble-Mitglieder in °F (zwischengespeichert)."""
    key = f"{lat:.3f},{lon:.3f}"
    c = store.lies(CACHE, {}) or {}
    e = c.get(key)
    if e and time.time() - e["ts"] < CACHE_S:
        return e["daten"]
    d = get(ENSEMBLE, {"latitude": lat, "longitude": lon, "daily": "temperature_2m_max", "models": MODELLE,
                       "temperature_unit": "fahrenheit", "timezone": tz, "forecast_days": tage}, ttl=CACHE_S, versuche=2, timeout=30)
    tage_ = d["daily"]["time"]
    daten: dict[str, list[float]] = {t: [] for t in tage_}
    for k, werte in d["daily"].items():
        if k.startswith("temperature_2m_max"):
            for t, v in zip(tage_, werte):
                if v is not None:
                    daten[t].append(float(v))
    c = {k: v for k, v in c.items() if time.time() - v["ts"] < 6 * 3600}
    c[key] = {"ts": time.time(), "daten": daten}
    store.schreibe(CACHE, c)
    return daten


def p_bracket(mitglieder: list[float], unten: float | None, oben: float | None, sigma: float, beobachtet: float | None = None) -> float:
    """P(Tageshöchstwert im Intervall [unten, oben)) – Grenzen bereits um die Rundung auf ganze Grad erweitert.
    Mit `beobachtet` (bisheriges Maximum heute) gilt X = max(Mitglied + Fehler, beobachtet): Masse darunter wird auf den Messwert gehoben."""
    if not mitglieder:
        return float("nan")
    s = 0.0
    for m in mitglieder:
        def cdf(x):
            return 0.0 if x is None else N01.cdf((x - m) / sigma)
        if beobachtet is None:
            s += max(0.0, (1.0 if oben is None else cdf(oben)) - cdf(unten))
        elif oben is not None and beobachtet >= oben:
            continue  # schon darüber gemessen → unmöglich
        elif unten is None or beobachtet >= unten:
            s += 1.0 if oben is None else cdf(oben)  # Messwert liegt im Bracket: alles bis zur Obergrenze landet hier
        else:
            s += max(0.0, (1.0 if oben is None else cdf(oben)) - cdf(unten))
    return s / len(mitglieder)


def grenzen(strike_type: str, floor: float | None, cap: float | None) -> tuple[float | None, float | None]:
    """Kalshi-Strikes → Intervall des (kontinuierlichen) Messwerts, der auf ganze °F gerundet wird.
    between 69/70 → 69 oder 70 → [68,5; 70,5); less 69 → ≤ 68 → (−∞; 68,5); greater 76 → ≥ 77 → [76,5; ∞)."""
    if strike_type == "between":
        return floor - 0.5, cap + 0.5
    if strike_type == "less":
        return None, cap - 0.5
    if strike_type == "greater":
        return floor + 0.5, None
    return None, None


def beobachtet_heute(station: str, tz: str) -> float | None:
    """Bisheriges Tagesmaximum (°F) der NWS-Station seit Mitternacht Ortszeit (für Märkte des laufenden Tages)."""
    mitternacht = datetime.now(ZoneInfo(tz)).replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        d = get(f"https://api.weather.gov/stations/{station}/observations", {"start": mitternacht.astimezone(timezone.utc).isoformat()},
                ttl=900, versuche=2)
    except HttpFehler:
        return None
    werte = [f["properties"]["temperature"]["value"] for f in d.get("features", []) if f["properties"].get("temperature", {}).get("value") is not None]
    return round(max(werte) * 9 / 5 + 32, 1) if werte else None


def event_daten(event_ticker: str) -> dict | None:
    """Kalshi-Event mit allen Brackets (ein Abruf)."""
    from arena.data.pm import KALSHI
    try:
        d = get(f"{KALSHI}/events/{event_ticker}", {"with_nested_markets": "true"}, ttl=300)
    except HttpFehler:
        return None
    return d


def analyse_event(event_ticker: str) -> dict:
    """Modellwahrscheinlichkeit je Bracket gegen den Marktpreis (Kalshi-Temperatur-Event, z. B. KXHIGHNY-26OCT31)."""
    serie = event_ticker.split("-")[0]
    if serie not in STATIONEN:
        return {"fehler": f"Keine Station für Serie {serie} hinterlegt (bekannt: {', '.join(STATIONEN)})"}
    name, lat, lon, station, tz = STATIONEN[serie]
    ev = event_daten(event_ticker)
    if not ev:
        return {"fehler": "Event nicht abrufbar"}
    maerkte = ev.get("markets") or ev.get("event", {}).get("markets") or []
    if not maerkte:
        return {"fehler": "Event ohne Märkte"}
    try:
        datum = datetime.strptime(event_ticker.split("-")[1], "%y%b%d").date()
    except (IndexError, ValueError):
        return {"fehler": "Datum im Event-Ticker nicht lesbar"}
    try:
        ens = ensemble(lat, lon, tz)
    except (HttpFehler, KeyError, TypeError, ValueError) as e:
        return {"fehler": f"Open-Meteo nicht erreichbar ({e})"}
    mitglieder = ens.get(datum.isoformat(), [])
    heute = datetime.now(ZoneInfo(tz)).date()
    vorlauf = (datum - heute).days + 0.5
    sigma = fehler_sigma(vorlauf)
    beob = beobachtet_heute(station, tz) if datum == heute else None
    zeilen = []
    for m in maerkte:
        u, o = grenzen(m.get("strike_type", ""), m.get("floor_strike"), m.get("cap_strike"))
        if u is None and o is None:
            continue
        p = p_bracket(mitglieder, u, o, sigma, beob)  # Höchstwert kann nicht unter das bisher Gemessene fallen
        bid, ask = float(m.get("yes_bid_dollars") or 0), float(m.get("yes_ask_dollars") or 0)
        zeilen.append({"markt_id": f"pm:kalshi:{m['ticker']}", "bracket": m.get("yes_sub_title"), "p_modell": round(p, 3),
                       "ja_bid": bid, "ja_ask": ask, "vorteil_ja_pp": round(100 * (p - ask), 1) if ask else None,
                       "vorteil_nein_pp": round(100 * (bid - p), 1) if bid else None})
    srt = sorted(mitglieder)
    return {"event": event_ticker, "station": f"{name} – Abrechnung laut Kalshi-Regeln (NWS-Klimabericht/CLI)", "datum": datum.isoformat(),
            "mitglieder": len(mitglieder), "median_f": srt[len(srt) // 2] if srt else None,
            "spanne_10_90_f": [srt[int(0.1 * (len(srt) - 1))], srt[int(0.9 * (len(srt) - 1))]] if srt else None,
            "modellfehler_sigma_f": round(sigma, 2), "bisher_beobachtet_max_f": beob, "brackets": zeilen,
            "hinweis": ("Vorteil = Modell minus Kaufpreis (ohne Gebühr; Kalshi-Taker ≈ 0,07·p·(1−p) je Kontrakt). Ensembles sind gut, aber nicht perfekt: "
                        "Stationseffekte und Tagesgrenzen (CLI zählt Ortsstandardzeit) beachten. Daten: Open-Meteo (CC BY 4.0)."),
            "quelle": "Open-Meteo Ensemble API (GFS, ECMWF IFS), NWS"}


def offene_events(serien: list[str] | None = None, max_events: int = 12) -> list[str]:
    """Offene Temperatur-Events der bekannten Serien (je Serie ein Abruf, Kalshi-Mindestabstand beachtet)."""
    from arena.data.pm import KALSHI
    out = []
    for s in serien or list(STATIONEN)[:6]:
        try:
            d = get(f"{KALSHI}/events", {"series_ticker": s, "status": "open", "limit": 3}, ttl=900)
        except HttpFehler:
            continue
        out += [e["event_ticker"] for e in d.get("events", [])]
        if len(out) >= max_events:
            break
    return out[:max_events]
