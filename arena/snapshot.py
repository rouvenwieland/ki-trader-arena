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
    s["dvol"] = {b: v for b in ("BTC", "ETH") if (v := crypto.dvol(b))}
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


def startliste(s: dict, defn: dict | None, max_wetten: int = 30) -> list[str]:
    """Welche Wettmärkte ein Fonds in seiner Marktlage sieht.
    Ohne Schwerpunkt (Liga, Vergleichbarkeit der Modelle): die umsatzstärksten + bald schließende – für alle gleich.
    Mit Schwerpunkt (Claude-Fonds): zuerst Märkte zu den eigenen Stichworten, dann eine je Fonds und Tag eigene Stichprobe
    aus dem Rest – so starten die Fonds nicht alle bei derselben Spitzenwette (Klumpenrisiko), ohne dass etwas verboten wird."""
    top = sorted(s["wetten"], key=lambda m: -m.get("volumen_24h", 0))
    bald = sorted([m for m in s["wetten"] if m.get("schliesst") and 0 < m["schliesst"] - s["ts"] < 3 * 86400],
                  key=lambda m: m["schliesst"])
    if not defn or not defn.get("stichworte"):
        gezeigt: list[str] = []
        for m in top[:max_wetten] + bald[:8]:
            if m["mid"] not in gezeigt:
                gezeigt.append(m["mid"])
        return gezeigt
    import hashlib
    kw = {w.lower() for w in defn["stichworte"]}
    import re
    passend = [m for m in top if kw & set(re.findall(r"[a-zäöüß0-9]+", m["frage"].lower()))]
    tag = time.strftime("%Y-%m-%d", time.gmtime(s["ts"]))

    def los(m: dict) -> str:
        return hashlib.sha256(f"{defn.get('ab_von') or defn['id']}|{tag}|{m['mid']}".encode()).hexdigest()  # A/B-Zwilling: gleiche Liste
    rest = sorted([m for m in top[:150] if m not in passend], key=los)
    gezeigt = []
    for m in passend[: max_wetten * 2 // 3] + [m for m in bald if m in passend][:6] + rest:
        if m["mid"] not in gezeigt:
            gezeigt.append(m["mid"])
        if len(gezeigt) >= max_wetten:
            break
    return gezeigt


def text(s: dict, max_wetten: int = 30, defn: dict | None = None) -> str:
    """Kompakte Textfassung für den Prompt (~3–5k Tokens). defn: Fonds mit Schwerpunkt → eigene Startliste der Wettmärkte."""
    z = []
    z.append(f"EUR/USD {s['fx']:.4f}. Alle Beträge in USD.")
    z.append("KRYPTO (Spot, Coinbase): " + "; ".join(
        f"{k} {v['bid']:.6g}/{v['ask']:.6g}" + (f" ({aenderung(s, 'spot:' + k + '-USD', 24):+.1f}% 24h)"
                                                  if aenderung(s, 'spot:' + k + '-USD', 24) is not None else "")
        for k, v in s["krypto"].items()))
    z.append("PERPS (Deribit, linear USDC; Funding je 8h): " + "; ".join(
        f"{k} mark {v['mark']:.6g} funding {v['funding_8h'] * 100:.4f}%" for k, v in s["perps"].items()))
    if s.get("dvol"):
        z.append("VOLA-REGIME (Deribit DVOL, implizite 30-Tage-Vola p. a.): " + "; ".join(
            f"{b} {v['dvol']:.1f} (24h zuvor {v['vor_24h']:.1f}, 7-Tage-Spanne {v['min_7t']:.0f}–{v['max_7t']:.0f}, ≈ ±{v['tagesbewegung_1sigma_pct']:.1f} % je Tag)"
            for b, v in s["dvol"].items()) + ". Mehr im Werkzeug „derivate_lage“.")
    if s["aktien"]:
        z.append("AKTIEN/ETF (Yahoo): " + "; ".join(f"{k} {v['preis']:.2f}{'' if v['offen'] else ' (Börse zu)'}" for k, v in s["aktien"].items()))
    else:
        z.append("AKTIEN/ETF: derzeit keine Kursquelle erreichbar.")
    if s["optionen"]:
        z.append("OPTIONEN (liquideste nahe am Geld, USD je Einheit bid/ask, IV%, Tage): " + "; ".join(
            f"{o['inst']['symbol']} {o['bid']:.0f}/{o['ask']:.0f} IV{o['iv']:.0f} {o['tage']:.0f}d" for o in s["optionen"][:10]))
    gezeigt = startliste(s, defn, max_wetten)
    z.append("WETTMÄRKTE " + ("(deine Startliste: Schwerpunkt zuerst, dann eigene Stichprobe; weitere über markt_suche) " if defn and defn.get("stichworte") else "") +
             "(id | JA bid/ask | Schluss in Tagen | 24h-Umsatz | Frage):")
    for mid in gezeigt:
        m = s["pm_index"][mid]
        tage = f"{(m['schliesst'] - s['ts']) / 86400:.1f}d" if m.get("schliesst") else "?"
        z.append(f"  {m['mid']} | {m['ja_bid']:.2f}/{m['ja_ask']:.2f} | {tage} | {m.get('volumen_24h', 0):.0f} | {m['frage'][:110]}")
    return "\n".join(z)
