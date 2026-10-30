"""Daten-Schnappschuss für die Agenten: derselbe für alle Fonds eines Laufs (faire Bedingungen)."""
from __future__ import annotations

import time

from arena import config, verlauf
from arena.data import crypto, news, pm, stocks


def baue(jetzt: float | None = None, mit_nachrichten: bool = True) -> dict:
    jetzt = jetzt or time.time()
    cfg = config.load()
    s: dict = {"ts": jetzt, "fx": crypto.usd_je_eur(), "krypto": {}, "perps": {}, "aktien": {}, "optionen": []}
    for sym in cfg["universum"]["krypto"]:
        t = crypto.spot_ticker(sym)
        if t:
            s["krypto"][sym] = t
    for p in cfg["universum"]["perps"]:
        t = crypto.perp_ticker(p)
        if t:
            s["perps"][p] = t
    for sym in cfg["universum"]["aktien"]:
        k = stocks.kurs(sym)
        if k:
            s["aktien"][sym] = k
    s["wetten"] = pm.universum()
    s["pm_index"] = {m["mid"]: m for m in s["wetten"]}
    for basis in ("BTC", "ETH"):
        s["optionen"] += crypto.optionen_universum(basis, 8)
    s["nachrichten"] = news.alle_nachrichten() if mit_nachrichten else []
    s["verlauf"] = verlauf.lade(26, jetzt)
    return s


def aenderung(s: dict, iid: str, stunden: float) -> float | None:
    serie = s.get("verlauf", {}).get(iid)
    if not serie:
        return None
    alt = verlauf.vor(serie, s["ts"], stunden)
    neu = serie[-1][1]
    return None if not alt else (neu / alt - 1) * 100


def text(s: dict, max_wetten: int = 30) -> str:
    """Kompakte Textfassung für den Prompt (~3–5k Tokens)."""
    z = []
    z.append(f"EUR/USD {s['fx']:.4f}. Alle Beträge in USD.")
    z.append("KRYPTO (Spot, Coinbase): " + "; ".join(
        f"{k} {v['bid']:.6g}/{v['ask']:.6g}" + (f" ({aenderung(s, 'spot:' + k + '-USD', 24):+.1f}% 24h)"
                                                  if aenderung(s, 'spot:' + k + '-USD', 24) is not None else "")
        for k, v in s["krypto"].items()))
    z.append("PERPS (Deribit, linear USDC; Funding je 8h): " + "; ".join(
        f"{k} mark {v['mark']:.6g} funding {v['funding_8h'] * 100:.4f}%" for k, v in s["perps"].items()))
    if s["aktien"]:
        z.append("AKTIEN/ETF (Yahoo): " + "; ".join(f"{k} {v['preis']:.2f}{'' if v['offen'] else ' (Börse zu)'}" for k, v in s["aktien"].items()))
    else:
        z.append("AKTIEN/ETF: derzeit keine Kursquelle erreichbar.")
    if s["optionen"]:
        z.append("OPTIONEN (liquideste nahe am Geld, USD je Einheit bid/ask, IV%, Tage): " + "; ".join(
            f"{o['inst']['symbol']} {o['bid']:.0f}/{o['ask']:.0f} IV{o['iv']:.0f} {o['tage']:.0f}d" for o in s["optionen"][:10]))
    top = sorted(s["wetten"], key=lambda m: -m.get("volumen_24h", 0))
    bald = sorted([m for m in s["wetten"] if m.get("schliesst") and 0 < m["schliesst"] - s["ts"] < 3 * 86400],
                  key=lambda m: m["schliesst"])[:8]
    gezeigt = []
    for m in top[:max_wetten] + bald:
        if m["mid"] not in gezeigt:
            gezeigt.append(m["mid"])
    z.append("WETTMÄRKTE (id | JA bid/ask | Schluss in Tagen | 24h-Umsatz | Frage):")
    for mid in gezeigt:
        m = s["pm_index"][mid]
        tage = f"{(m['schliesst'] - s['ts']) / 86400:.1f}d" if m.get("schliesst") else "?"
        z.append(f"  {m['mid']} | {m['ja_bid']:.2f}/{m['ja_ask']:.2f} | {tage} | {m.get('volumen_24h', 0):.0f} | {m['frage'][:110]}")
    return "\n".join(z)
