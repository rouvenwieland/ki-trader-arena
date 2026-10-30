"""Ereignislogik des Wächters. Reine Funktionen: Eingabe = Preise/Verlauf/Positionen, Ausgabe = Ereignisse."""
from __future__ import annotations

import hashlib
import statistics
import time

from arena import config
from arena.data import news as newsmod
from arena.verlauf import vor


def _ev(ts: float, typ: str, inst_id: str | None, titel: str, details: dict, fonds: list[str] | None,
        weckt: bool, schluessel: str) -> dict:
    h = hashlib.sha1(schluessel.encode()).hexdigest()[:10]
    return {"id": f"e{h}", "ts": ts, "typ": typ, "inst_id": inst_id, "titel": titel, "details": details,
            "fonds": fonds, "weckt": weckt, "schluessel": schluessel}


def erkenne(jetzt: float, preise: dict[str, float], verlauf: dict[str, list[tuple[float, float]]],
            gehalten: dict[str, list[str]], pm_markte: list[dict], pos_schluss: list[dict],
            nachrichten: list[dict], funding: dict[str, float], bekannt: set[str],
            cfg: dict | None = None) -> list[dict]:
    """gehalten: inst_id -> Fonds, die sie halten. pos_schluss: [{fonds, position_id, inst_id, schliesst}]."""
    cfg = cfg or config.load()["ereignisse"]
    out: list[dict] = []
    stunde = int(jetzt // 3600)

    def neu(e: dict):
        if e["schluessel"] not in bekannt:
            bekannt.add(e["schluessel"])
            out.append(e)

    # --- Kurssprünge & Volatilitätsausbruch (Krypto, Perps, Aktien, Optionen: Preise > 1) und Wetten (0..1)
    for iid, px in preise.items():
        serie = verlauf.get(iid, [])
        if px is None or not serie:
            continue
        halter = gehalten.get(iid)
        if iid.startswith("pm:"):
            continue
        letzter = serie[-1][1]
        if letzter:
            d = (px / letzter - 1) * 100
            if abs(d) >= cfg["kurssprung_pct"]:
                neu(_ev(jetzt, "kurssprung", iid, f"{iid} {d:+.1f} % seit letzter Messung",
                        {"von": letzter, "auf": px, "pct": d}, halter, bool(halter) or iid.startswith(("spot:BTC", "perp:BTC")),
                        f"kurssprung|{iid}|{stunde}"))
        h1 = vor(serie, jetzt, 1)
        if h1:
            d1 = (px / h1 - 1) * 100
            rets = [abs(b[1] / a[1] - 1) for a, b in zip(serie, serie[1:]) if a[1] and b[0] - a[0] < 3 * 3600]
            if len(rets) >= 12:
                # mittlere absolute Rendite je Messintervall, hochgerechnet auf eine Stunde (4 Messungen)
                norm = statistics.mean(rets) * 100 * 2  # √4 ≈ 2 als grobe Hochrechnung
                if abs(d1) >= max(cfg["volatilitaet_faktor"] * norm, 1.5):
                    neu(_ev(jetzt, "volatilitaet", iid, f"Volatilitätsausbruch {iid}: {d1:+.1f} % in 1 h (normal ≈ {norm:.2f} %)",
                            {"pct_1h": d1, "normal": norm}, halter, bool(halter), f"vola|{iid}|{stunde}"))
            if abs(d1) >= cfg["kurssprung_1h_pct"]:
                neu(_ev(jetzt, "kurssprung", iid, f"{iid} {d1:+.1f} % in 1 h", {"pct_1h": d1}, halter,
                        bool(halter), f"kurssprung1h|{iid}|{stunde}"))

    # --- Wettmarkt-Bewegung
    for m in pm_markte:
        key = f"{m['mid']}:JA"
        px = preise.get(key)
        serie = verlauf.get(key, [])
        h1 = vor(serie, jetzt, 1) if serie else None
        if px is None or h1 is None:
            continue
        halter = sorted(set(gehalten.get(key, []) + gehalten.get(f"{m['mid']}:NEIN", [])))
        pp = (px - h1) * 100
        schwelle = cfg["wettmarkt_bewegung_pp"] * (0.5 if halter else 1.0)
        if abs(pp) >= schwelle and (halter or m.get("volumen_24h", 0) >= 10000 or m["venue"] != "polymarket"):
            neu(_ev(jetzt, "wettmarkt_bewegung", key, f"Wette „{m['frage'][:90]}“ {pp:+.0f} Prozentpunkte in 1 h ({h1:.2f}→{px:.2f})",
                    {"von": h1, "auf": px, "pp": pp, "venue": m["venue"]}, halter or None, bool(halter) or abs(pp) >= 2 * cfg["wettmarkt_bewegung_pp"],
                    f"pm|{m['mid']}|{stunde // 3}"))

    # --- Markt schließt bald
    for p in pos_schluss:
        if p.get("schliesst") and 0 < p["schliesst"] - jetzt <= cfg["markt_schliesst_stunden"] * 3600:
            neu(_ev(jetzt, "markt_schliesst", p["inst_id"],
                    f"{p['inst_id']} läuft in {(p['schliesst'] - jetzt) / 3600:.1f} h ab ({p['fonds']})",
                    {"schliesst": p["schliesst"]}, [p["fonds"]], True, f"schliesst|{p['position_id']}"))

    # --- Nachricht zu gehaltener Position
    kw = {iid: _stichworte_fuer(iid, pm_markte) for iid in gehalten}
    for iid, treffer in newsmod.passende(nachrichten, {k: v for k, v in kw.items() if v}).items():
        for n in treffer[:2]:
            neu(_ev(jetzt, "nachricht_position", iid, f"Nachricht zu {iid}: {n['titel'][:120]} ({n['quelle']})",
                    {"url": n["url"], "quelle": n["quelle"]}, gehalten[iid], True, f"news|{iid}|{n['url']}"))

    # --- Fehlbewertung: gleiche Frage auf mehreren Plattformen
    out_fb = _kreuz_abweichung(pm_markte, preise, cfg["fehlbewertung_pp"])
    for a, b, diff in out_fb:
        neu(_ev(jetzt, "fehlbewertung", a["mid"],
                f"Fehlbewertung? „{a['frage'][:70]}“: {a['venue']} {_mitte(a):.2f} vs {b['venue']} {_mitte(b):.2f} ({diff * 100:.0f} pp)",
                {"a": a["mid"], "b": b["mid"], "diff_pp": diff * 100}, None, True, f"fb|{a['mid']}|{b['mid']}|{stunde // 6}"))
    # extremes Funding
    for iid, r in funding.items():
        if abs(r) >= cfg["funding_extrem_8h"]:
            neu(_ev(jetzt, "fehlbewertung", iid, f"Extremes Funding {iid}: {r * 100:.3f} % je 8 h", {"funding_8h": r},
                    gehalten.get(iid), bool(gehalten.get(iid)), f"funding|{iid}|{stunde // 6}"))
    return out


def _mitte(m: dict) -> float:
    return (m["ja_bid"] + m["ja_ask"]) / 2


def _stichworte_fuer(iid: str, pm_markte: list[dict]) -> set[str]:
    if iid.startswith("pm:"):
        mid = iid.rsplit(":", 1)[0]
        for m in pm_markte:
            if m["mid"] == mid:
                return newsmod.stichworte(m["frage"])
        return set()
    namen = {"BTC": {"bitcoin"}, "ETH": {"ethereum", "ether"}, "SOL": {"solana"}, "XRP": {"ripple"}, "DOGE": {"dogecoin"},
             "ADA": {"cardano"}, "LINK": {"chainlink"}, "AVAX": {"avalanche"}}
    for sym, kw in namen.items():
        if sym in iid.upper().replace("_", "-").split(":")[1].split("-")[0] or iid.upper().startswith(f"OPT:{sym}"):
            return kw
    return set()


def _kreuz_abweichung(markte: list[dict], preise: dict, schwelle_pp: float):
    """Gleiche Frage (Stichwort-Jaccard ≥ 0,6, Zahlen müssen übereinstimmen) auf verschiedenen Plattformen."""
    kw = [(m, _tokens(m["frage"])) for m in markte if m["venue"] != "manifold"]
    treffer = []
    for i, (a, ka) in enumerate(kw):
        for b, kb in kw[i + 1:]:
            if a["venue"] == b["venue"] or not ka or not kb:
                continue
            j = len(ka & kb) / len(ka | kb)
            krit = lambda t: {w for w in t if len(w) <= 2 or w.isdigit()}  # noqa: E731
            if j < 0.8 or krit(ka) != krit(kb):
                continue
            diff = abs(_mitte(a) - _mitte(b))
            if diff * 100 >= schwelle_pp and a["ja_ask"] - a["ja_bid"] < 0.08 and b["ja_ask"] - b["ja_bid"] < 0.08:
                treffer.append((a, b, diff))
    return treffer[:5]


def _tokens(text: str) -> set[str]:
    """Vergleichs-Tokens für „gleiche Frage“: auch kurze Tokens/Zahlen zählen (R/D, Jahreszahlen, Schwellen)."""
    import re
    return {w for w in re.findall(r"[a-zäöüß0-9]+", text.lower()) if w not in newsmod.STOP}
