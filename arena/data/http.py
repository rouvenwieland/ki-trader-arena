"""HTTP-Helfer: User-Agent, Mindestabstand je Host, Wiederholung bei 429/5xx, Prozess-Cache.

Wir respektieren Nutzungsbedingungen: ehrlicher User-Agent, keine Umgehung von Sperren
(bei 403/451 wird nicht erneut versucht), Rate-Limit-Abstand je Host."""
from __future__ import annotations

import time
from urllib.parse import urlparse

import requests

UA = "ki-trader-arena/0.1 (Papierhandel-Forschung; +https://github.com/rouvenwieland/ki-trader-arena)"
MIN_ABSTAND = {"default": 0.15, "gamma-api.polymarket.com": 0.25, "api.elections.kalshi.com": 1.0,
               "api.gdeltproject.org": 5.5, "www.reddit.com": 2.0, "query1.finance.yahoo.com": 1.0}
_letzter: dict[str, float] = {}
_cache: dict[str, tuple[float, object]] = {}
_fehlzaehler: dict[str, int] = {}
_session = requests.Session()
_session.headers["User-Agent"] = UA


class HttpFehler(Exception):
    pass


def get(url: str, params: dict | None = None, *, ttl: float = 0, timeout: float = 20, text: bool = False,
        versuche: int = 3, headers: dict | None = None):
    """GET mit JSON-Rückgabe (oder Text). ttl>0: Ergebnis im Prozess zwischenspeichern."""
    key = url + "?" + "&".join(f"{k}={v}" for k, v in sorted((params or {}).items()))
    if ttl and key in _cache and time.time() - _cache[key][0] < ttl:
        return _cache[key][1]
    host = urlparse(url).netloc
    if _fehlzaehler.get(host, 0) >= 3:  # Schutzschalter: Host in diesem Lauf wiederholt gescheitert → nicht weiter belasten
        raise HttpFehler(f"{host}: übersprungen (wiederholte Fehler in diesem Lauf)")
    abstand = MIN_ABSTAND.get(host, MIN_ABSTAND["default"])
    fehler = None
    for i in range(versuche):
        wait = _letzter.get(host, 0) + abstand - time.time()
        if wait > 0:
            time.sleep(wait)
        _letzter[host] = time.time()
        try:
            r = _session.get(url, params=params, timeout=timeout, headers=headers)
        except requests.RequestException as e:
            fehler = e
            time.sleep(1.5 * (i + 1))
            continue
        if r.status_code in (403, 451, 404, 401):
            if r.status_code in (403, 451, 401):
                _fehlzaehler[host] = _fehlzaehler.get(host, 0) + 2
            raise HttpFehler(f"{r.status_code} von {host} (kein Wiederholen, keine Umgehung)")
        if r.status_code == 429 or r.status_code >= 500:
            fehler = HttpFehler(f"{r.status_code} von {host}")
            time.sleep(2.0 * (i + 1))
            continue
        if r.status_code >= 400:
            raise HttpFehler(f"{r.status_code} von {host}: {r.text[:120]}")
        out = r.text if text else r.json()
        if ttl:
            _cache[key] = (time.time(), out)
        return out
    _fehlzaehler[host] = _fehlzaehler.get(host, 0) + 1
    raise HttpFehler(f"{url}: {fehler}")
