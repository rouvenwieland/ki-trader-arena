"""Kennzahlen je Fonds: Rendite, max. Drawdown, Sharpe, Trefferquote, Brier-Score (Wettmärkte), Kosten."""
from __future__ import annotations

import math
import statistics
from datetime import datetime, timezone

from arena import store


def tageswerte(eq: list[dict]) -> list[tuple[str, float]]:
    tage: dict[str, float] = {}
    for p in eq:
        tage[datetime.fromtimestamp(p["t"], timezone.utc).strftime("%Y-%m-%d")] = p["usd"]
    return sorted(tage.items())


def max_drawdown(werte: list[float]) -> float:
    spitze, md = -math.inf, 0.0
    for w in werte:
        spitze = max(spitze, w)
        if spitze > 0:
            md = min(md, w / spitze - 1)
    return md * 100


def sharpe(werte_tag: list[float]) -> float | None:
    """Annualisiert (365 Tage, Krypto/Wetten laufen durch), erst ab 8 Tageswerten sinnvoll."""
    if len(werte_tag) < 8:
        return None
    r = [b / a - 1 for a, b in zip(werte_tag, werte_tag[1:]) if a > 0]
    sd = statistics.pstdev(r)
    return None if sd == 0 else statistics.mean(r) / sd * math.sqrt(365)


def prognose_paare(fid: str, res: dict | None = None) -> tuple[list[dict], int]:
    """Je Markt die ERSTE Schätzung (kein Nachbessern nach Kenntnis), nur wenn aufgelöst und VOR Schluss bzw. Auflösung abgegeben.
    Liefert ([{p, m, y, ts, markt_id}], Anzahl offener Märkte)."""
    res = store.lies("resolutions.json", {}) if res is None else res
    erste: dict[str, dict] = {}
    for p in store.lies_jsonl(f"funds/{fid}/prognosen.jsonl"):
        erste.setdefault(p["markt_id"], p)
    paare, offen = [], 0
    for mid, p in erste.items():
        r = res.get(mid)
        if r is None:
            offen += 1
            continue
        if r.get("wert") is None:  # storniert
            continue
        if p["ts"] >= r.get("ts", 9e18) or (p.get("schliesst") and p["ts"] >= p["schliesst"]):
            continue  # nach dem Ereignis abgegeben → zählt nicht
        paare.append({"p": float(p["p_ja"]), "m": p.get("markt_ja_mitte"), "y": float(r["wert"]), "ts": p["ts"], "markt_id": mid})
    return paare, offen


def prognose_kennzahlen(paare: list[dict], offen: int = 0) -> dict:
    """Marktrelative Kennzahlen: Brier, Brier des Marktpreises, Brier-Skill gegen den Markt (> 0 = besser als der Markt),
    marktbereinigter Brier (Markt kopieren = 0, kleiner = besser) mit 95-%-KI, Log-Score, Murphy-Zerlegung, Kalibrierungskurve,
    hypothetischer Gewinn je Kontrakt bei Handel zum Marktpreis (ohne Gebühren)."""
    from arena import statistik as st
    out: dict = {"n": len(paare), "offen": offen, "brier": None, "brier_markt": None}
    if not paare:
        return out
    p, y = [x["p"] for x in paare], [x["y"] for x in paare]
    out["brier"] = st.brier(p, y)
    out["log_score"] = st.log_score(p, y)
    mz = [x for x in paare if x["m"] is not None]
    if mz:
        bm = st.brier([x["m"] for x in mz], [x["y"] for x in mz])
        bf = st.brier([x["p"] for x in mz], [x["y"] for x in mz])
        diff = [(x["p"] - x["y"]) ** 2 - (x["m"] - x["y"]) ** 2 for x in mz]
        out |= {"n_markt": len(mz), "brier_markt": bm, "brier_eigen_markt": bf,
                "brier_skill_markt": (1 - bf / bm) if bm > 0 else None, "marktbereinigt": statistics.mean(diff),
                "marktbereinigt_ki": st.fragen_bootstrap_ki(diff), "log_score_markt": st.log_score([x["m"] for x in mz], [x["y"] for x in mz]),
                "gewinn_je_kontrakt": statistics.mean([(1 if x["p"] > x["m"] else -1) * (x["y"] - x["m"]) for x in mz if x["p"] != x["m"]] or [0.0])}
    out["murphy"] = st.murphy(p, y)
    return out


def brier(fid: str) -> dict:
    return prognose_kennzahlen(*prognose_paare(fid))


def kalibrierung(fid: str) -> dict | None:
    """Platt-Rekalibrierung (BIA/CON) ab 15 aufgelösten Schätzungen – darunter keine Meinung."""
    from arena import statistik as st
    paare, _ = prognose_paare(fid)
    if len(paare) < 15:
        return None
    p, y = [x["p"] for x in paare], [x["y"] for x in paare]
    ab = st.platt(p, y)
    if not ab:
        return None
    band = [x for x in paare if 0.6 <= x["p"] <= 0.8]
    return {"n": len(paare), "ja_ueberschaetzung_pp": round(100 * (statistics.mean(p) - statistics.mean(y)), 1),
            "a": round(ab[0], 3), "b": round(ab[1], 3), "band_60_80": (round(100 * statistics.mean([x["y"] for x in band]), 0), len(band)) if band else None}


def kalibrier_text(fid: str) -> str:
    k = kalibrierung(fid)
    if not k:
        return ""
    t = f"n={k['n']} aufgelöste Schätzungen; JA-Überschätzung {k['ja_ueberschaetzung_pp']:+.1f} pp; "
    t += ("überkonfident (Faktor %.2f < 1: ziehe extreme Schätzungen zur Mitte)" % k["b"]) if k["b"] < 0.9 else \
         ("unterkonfident (Faktor %.2f > 1)" % k["b"]) if k["b"] > 1.1 else "Streuung etwa richtig"
    if k["band_60_80"] and k["band_60_80"][1] >= 5:
        t += f"; im Band 60–80 % trat JA in {k['band_60_80'][0]:.0f} % ein (n={k['band_60_80'][1]})"
    return t + "."


# ---------------------------------------------------------------- ehrliche Rangliste
def stundenrenditen(eq: list[dict]) -> list[tuple[int, float]]:
    """Log-Renditen je Stunde (letzter Wert je Stunde), mit Stundenstempel – Grundlage für Bootstrap, PSR und Paarvergleiche."""
    h: dict[int, float] = {}
    for p in eq:
        if p.get("usd", 0) > 0:
            h[int(p["t"] // 3600)] = p["usd"]
    k = sorted(h)
    return [(b, math.log(h[b] / h[a])) for a, b in zip(k, k[1:]) if b - a <= 3]


def rangliste_statistik(fonds_ids: list[str], btc_id: str = "bm_btc") -> dict:
    """Je Fonds: 95-%-KI der Rendite (stationärer Block-Bootstrap, Blocklänge 24 h), PSR (P[Sharpe > 0]),
    Deflated Sharpe (Schwelle = erwartetes Maximum von N Null-Fonds), MinTRL in Tagen, p-Wert gegen BTC Buy & Hold."""
    from arena import statistik as st
    reihen = {fid: stundenrenditen(store.lies_jsonl(f"funds/{fid}/equity.jsonl")) for fid in fonds_ids}
    srs = [st.sharpe_periode([r for _, r in v]) for v in reihen.values()]
    srs = [x for x in srs if x is not None]
    var_sr = statistics.variance(srs) if len(srs) >= 2 else 0.0
    sr0 = st.sr0_erwartet_max(var_sr, len(srs))
    btc = dict(reihen.get(btc_id) or [])
    out = {}
    for fid, v in reihen.items():
        r = [x for _, x in v]
        if len(r) < 24:
            out[fid] = {"stunden": len(r)}
            continue
        ki = st.bootstrap_ki(r, lambda x: math.exp(sum(x)) - 1)
        trl = st.min_trl(r)
        d = [x - btc[t] for t, x in v if t in btc] if fid != btc_id else []
        out[fid] = {"stunden": len(r), "rendite_ki_pct": [round(100 * ki[0], 2), round(100 * ki[1], 2)] if ki else None,
                    "psr": _r(st.psr(r)), "dsr": _r(st.psr(r, sr0)) if len(srs) >= 2 else None,
                    "messbar_ab_tagen": round(trl / 24, 1) if trl else None,
                    "p_gegen_btc": _r(st.p_wert_mehr(d)) if len(d) >= 24 else None}
    return {"fonds": out, "n_versuche": len(srs), "sr0_je_stunde": round(sr0, 4)}


def _r(x: float | None, n: int = 3) -> float | None:
    return None if x is None else round(x, n)


def kennzahlen(fid: str) -> dict:
    eq = store.lies_jsonl(f"funds/{fid}/equity.jsonl")
    pf = store.lies(f"funds/{fid}/portfolio.json")
    led = store.lies_jsonl(f"funds/{fid}/ledger.jsonl")
    if not eq or not pf:
        return {}
    start = pf["start_kapital"]
    tag = tageswerte(eq)
    geschl = [x for x in led if x.get("aktion") in ("geschlossen", "teilweise_geschlossen", "liquidiert") and "netto_pnl" in x]
    kosten_api = sum(x.get("usd", 0) for x in store.lies_jsonl("budget_log.jsonl") if x.get("fonds") == fid)  # inkl. Vorsichter
    fx = (store.lies("fx.json") or {}).get("usd_je_eur", 1.08)
    return {"equity_usd": eq[-1]["usd"], "start_usd": start, "rendite_pct": (eq[-1]["usd"] / start - 1) * 100,
            "max_drawdown_pct": max_drawdown([p["usd"] for p in eq]), "sharpe": sharpe([v for _, v in tag]),
            "trades": len(geschl), "trefferquote": (sum(1 for x in geschl if x["netto_pnl"] > 0) / len(geschl)) if geschl else None,
            "gebuehren_usd": pf["gebuehren"], "funding_usd": pf["funding"], "api_kosten_eur": kosten_api / fx,
            "brier": brier(fid), "positionen": len(pf["positionen"]), "cash_usd": pf["cash"],
            "trades_je_woche": round(len(geschl) / max(1.0, (eq[-1]["t"] - eq[0]["t"]) / 604800), 1),
            "gebuehren_pct": round(100 * pf["gebuehren"] / start, 3), "gewinn_je_api_eur": ((eq[-1]["usd"] - start) / fx) / (kosten_api / fx) if kosten_api > 0 else None}
