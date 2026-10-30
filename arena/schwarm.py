"""Meta-Fonds „Schwarm der Arena“ (ohne LLM, 0 Tokens) und Kontrollfonds für Wettmärkte.

Schwarm (Recherche M11; AIA Forecaster, „Wisdom of the Silicon Crowd“, Halawi):
  je Wettmarkt mit ≥ 3 frischen Schätzungen (≤ 48 h) verschiedener Fonds der Gruppe → je Fonds rekalibrieren (erst ab 50 Auflösungen) →
  getrimmter Mittelwert, gewichtet mit 1/Brier (ab 10 Auflösungen, sonst gleich) → Log-Odds-Mischung mit dem Marktpreis (Gewicht der KI 0,3) →
  nur handeln, wenn der Abstand zum Kaufpreis Gebühr + Puffer übersteigt; Größe ¼-Kelly, höchstens 5 % je Markt. Varianten: alle KI-Fonds,
  nur Claude, nur Liga – zeigt, ob Modellvielfalt hilft.
Kontrollen: „Markt-Kopierer“ schätzt immer den Marktpreis (Null-Linie des marktbereinigten Brier, handelt nicht);
  „Immer NEIN“ kauft auf jeden von KI-Fonds geschätzten Echtgeld-Markt einen kleinen NEIN-Einsatz (misst den Ja-Hang)."""
from __future__ import annotations

import math
import statistics
import time

from arena import funds, metrics, store
from arena import statistik as st
from arena.data import pm
from arena.exchange import engine, fees, portfolio

FRISCH_S = 48 * 3600
MIN_STIMMEN = 3
LLM_GEWICHT = 0.3  # Startwert; ab 100 Schwarm-Auflösungen aus Daten fitten (Umstiegspunkt der Empfehlung)
PUFFER = 0.02
MAX_ANTEIL = 0.05
KELLY = 0.25
NEIN_EINSATZ = 0.015
ECHTGELD = ("polymarket", "kalshi")
MAX_KAEUFE_JE_TICK = 3



def ki_fonds(gruppe: str = "alle") -> list[str]:
    ids = []
    if gruppe in ("alle", "claude"):
        ids += [f["id"] for f in funds.claude_fonds()]
    if gruppe in ("alle", "liga"):
        ids += [f["id"] for f in funds.liga_fonds()]
    return ids


def logit(p: float) -> float:
    p = min(max(p, 0.01), 0.99)
    return math.log(p / (1 - p))


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def getrimmt(werte: list[tuple[float, float]]) -> float:
    """Gewichteter Mittelwert nach Trimmen der Extreme (ab 5 Stimmen je eine oben und unten)."""
    w = sorted(werte)
    if len(w) >= 5:
        w = w[1:-1]
    summe = sum(g for _, g in w)
    return sum(p * g for p, g in w) / summe if summe else statistics.mean(p for p, _ in w)


def fonds_gewicht(fid: str, cache: dict) -> tuple[float, tuple | None]:
    if fid not in cache:
        k = metrics.brier(fid)
        g = 1 / max(k["brier"], 0.02) if k.get("n", 0) >= 10 and k.get("brier") else 1.0
        kal = metrics.kalibrierung(fid)
        cache[fid] = (g, (kal["a"], kal["b"]) if kal and kal["n"] >= 50 else None)
    return cache[fid]


def schaetzung(liste: list[dict], cache: dict) -> float | None:
    if len({p["_fid"] for p in liste}) < MIN_STIMMEN:
        return None
    werte = []
    for p in liste:
        g, ab = fonds_gewicht(p["_fid"], cache)
        werte.append((st.rekalibriere(float(p["p_ja"]), ab), g))
    return getrimmt(werte)


def mische(p_llm: float, markt: float, w: float = LLM_GEWICHT) -> float:
    return sigmoid(w * logit(p_llm) + (1 - w) * logit(markt))


def _markt(mid: str, pm_index: dict) -> dict | None:
    if mid in pm_index:
        return pm_index[mid]
    try:
        _, venue, ident = mid.split(":", 2)
        m = pm.einzelmarkt(venue, ident)
    except ValueError:
        m = None
    if m:
        pm_index[mid] = m
    return m


def schritt_schwarm(defn: dict, pf: dict, mz, jetzt: float, pm_index: dict) -> list[dict]:
    """Ein Wächter-Tick des Schwarm-Fonds: Schätzung festhalten, bei Vorteil nach Kosten kaufen (¼-Kelly)."""
    gruppe = defn["gruppe"]
    roh: dict[str, list[dict]] = {}
    for fid in ki_fonds(gruppe):
        for p in store.lies_jsonl(f"funds/{fid}/prognosen.jsonl", 600):
            if jetzt - p["ts"] <= FRISCH_S:
                roh.setdefault(p["markt_id"], {})[fid] = p | {"_fid": fid}
    bekannt = {p["markt_id"] for p in store.lies_jsonl(f"funds/{defn['id']}/prognosen.jsonl")}
    gehalten = {p["inst"]["id"].rsplit(":", 1)[0] for p in pf["positionen"]}
    cache: dict = {}
    log, kaeufe = [], 0
    eq = portfolio.equity(pf, {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]})
    for mid, je_fonds in sorted(roh.items(), key=lambda kv: -len(kv[1])):
        p_llm = schaetzung(list(je_fonds.values()), cache)
        if p_llm is None:
            continue
        m = _markt(mid, pm_index)
        if not m:
            continue
        mitte = (m["ja_bid"] + m["ja_ask"]) / 2
        p_mix = mische(p_llm, mitte)
        if mid not in bekannt:  # erste Schwarm-Schätzung je Markt zählt für den Brier-Vergleich mit dem Markt
            store.anhaengen(f"funds/{defn['id']}/prognosen.jsonl", {"ts": jetzt, "markt_id": mid, "p_ja": round(p_mix, 4), "p_llm": round(p_llm, 4),
                                                                   "markt_ja_mitte": mitte, "schliesst": m.get("schliesst"), "stimmen": len(je_fonds)})
            bekannt.add(mid)
        if mid in gehalten or kaeufe >= MAX_KAEUFE_JE_TICK or m["venue"] not in ECHTGELD:
            continue
        if m.get("schliesst") and m["schliesst"] - jetzt < 3600:
            continue
        for seite, p_seite in (("JA", p_mix), ("NEIN", 1 - p_mix)):
            inst = pm.inst(m, seite)
            book, _ = mz.buch(inst)
            if not book or not book.asks:
                continue
            k = book.asks[0][0] + fees.gebuehr(inst, book.asks[0][0], 100) / 100
            if p_seite - k <= PUFFER:
                continue
            from arena import risikoschicht
            anteil = min(KELLY * risikoschicht.kelly_binaer(p_seite, k), MAX_ANTEIL)
            if anteil * eq < 20:
                break
            r = engine.eroeffne(pf, funds.risikoprofil(defn), inst, book, usd=anteil * eq, equity=eq, ts=jetzt,
                                ausstiegsplan="Halten bis zur Abrechnung (Schwarm-Regel)")
            r["schwarm"] = {"p_llm": round(p_llm, 3), "p_mix": round(p_mix, 3), "kosten": round(k, 4), "stimmen": len(je_fonds)}
            log.append(r)
            if r.get("ok"):
                kaeufe += 1
            break
    return log


WETTER_PUFFER = 0.05
WETTER_MAX_ANTEIL = 0.03
WETTER_TAKT_S = 3600


def schritt_wetter(defn: dict, pf: dict, mz, jetzt: float) -> list[dict]:
    """Regelfonds ohne LLM: stündlich die offenen Kalshi-Temperatur-Events (≤ 2 Tage Vorlauf) analysieren, jede Bracket-Wahrscheinlichkeit
    als Schätzung festhalten (Brier gegen Markt messbar) und bei Vorteil > Gebühr + 5 pp mit ¼-Kelly (≤ 3 % je Bracket) kaufen."""
    from arena import risikoschicht
    from arena.data import wetter
    if jetzt - pf.get("wetter_letzter", 0) < WETTER_TAKT_S:
        return []
    pf["wetter_letzter"] = jetzt
    bekannt = {p["markt_id"] for p in store.lies_jsonl(f"funds/{defn['id']}/prognosen.jsonl")}
    gehalten = {p["inst"]["id"].rsplit(":", 1)[0] for p in pf["positionen"]}
    eq = portfolio.equity(pf, {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]})
    prof = funds.risikoprofil({"typ": "regel", "risiko": "mittel"})
    log, kaeufe = [], 0
    for ev in wetter.offene_events():
        a = wetter.analyse_event(ev)
        if "fehler" in a:
            continue
        vorlauf = (time.mktime(time.strptime(a["datum"], "%Y-%m-%d")) - jetzt) / 86400
        for b in a["brackets"]:
            mid, p = b["markt_id"], b["p_modell"]
            if p != p:  # NaN
                continue
            mitte = (b["ja_bid"] + b["ja_ask"]) / 2 if b["ja_ask"] else None
            if mid not in bekannt:
                store.anhaengen(f"funds/{defn['id']}/prognosen.jsonl", {"ts": jetzt, "markt_id": mid, "p_ja": p, "markt_ja_mitte": mitte,
                                                                       "schliesst": None, "quelle": "Open-Meteo-Ensemble"})
                bekannt.add(mid)
            if mid in gehalten or kaeufe >= 2 or vorlauf > 2:
                continue
            m = _markt(mid, {})
            if not m:
                continue
            for seite, ps in (("JA", p), ("NEIN", 1 - p)):
                inst = pm.inst(m, seite)
                book, _ = mz.buch(inst)
                if not book or not book.asks:
                    continue
                k = book.asks[0][0] + fees.gebuehr(inst, book.asks[0][0], 100) / 100
                if ps - k <= WETTER_PUFFER:
                    continue
                anteil = min(KELLY * risikoschicht.kelly_binaer(ps, k), WETTER_MAX_ANTEIL)
                if anteil * eq < 20:
                    break
                r = engine.eroeffne(pf, prof, inst, book, usd=anteil * eq, equity=eq, ts=jetzt, ausstiegsplan="Halten bis zur Abrechnung (Wetter-Regel)")
                r["wetter"] = {"p_modell": p, "kosten": round(k, 4), "event": ev}
                log.append(r)
                kaeufe += bool(r.get("ok"))
                break
    return log


def schritt_kontrolle(defn: dict, pf: dict, mz, jetzt: float, pm_index: dict) -> list[dict]:
    """Markt-Kopierer: übernimmt zu jeder KI-Schätzung den damaligen Marktpreis als eigene Schätzung (gleicher Zeitpunkt).
    Immer NEIN: kleiner NEIN-Kauf auf jeden von KI-Fonds geschätzten Echtgeld-Markt, gehalten bis zur Abrechnung."""
    eigene = {p["markt_id"] for p in store.lies_jsonl(f"funds/{defn['id']}/prognosen.jsonl")}
    seit = pf.get("kontrolle_bis", 0)
    neue: dict[str, dict] = {}
    for fid in ki_fonds("alle"):
        for p in store.lies_jsonl(f"funds/{fid}/prognosen.jsonl", 600):
            if p["ts"] > seit and p["markt_id"] not in eigene and p.get("markt_ja_mitte") is not None:
                if p["markt_id"] not in neue or p["ts"] < neue[p["markt_id"]]["ts"]:
                    neue[p["markt_id"]] = p
    log: list[dict] = []
    ts_max = max([seit] + [p["ts"] for p in neue.values()])
    if defn["art"] == "markt":
        for mid, p in sorted(neue.items(), key=lambda kv: kv[1]["ts"]):
            store.anhaengen(f"funds/{defn['id']}/prognosen.jsonl", {"ts": p["ts"], "markt_id": mid, "p_ja": p["markt_ja_mitte"],
                                                                   "markt_ja_mitte": p["markt_ja_mitte"], "schliesst": p.get("schliesst")})
        pf["kontrolle_bis"] = ts_max
        return log
    gehalten = {x["inst"]["id"] for x in pf["positionen"]}
    eq = portfolio.equity(pf, {x["inst"]["id"]: mz.marke(x["inst"]) for x in pf["positionen"]})
    kaeufe = 0
    for mid, p in sorted(neue.items(), key=lambda kv: kv[1]["ts"]):
        if kaeufe >= MAX_KAEUFE_JE_TICK:
            ts_max = p["ts"] - 1e-3  # Rest im nächsten Tick
            break
        store.anhaengen(f"funds/{defn['id']}/prognosen.jsonl", {"ts": p["ts"], "markt_id": mid, "p_ja": 0.0, "markt_ja_mitte": p["markt_ja_mitte"],
                                                               "schliesst": p.get("schliesst")})
        m = _markt(mid, pm_index)
        if not m or m["venue"] not in ECHTGELD or f"{mid}:NEIN" in gehalten or pf["cash"] < 0.1 * pf["start_kapital"]:
            continue
        inst = pm.inst(m, "NEIN")
        book, _ = mz.buch(inst)
        if not book or not book.asks:
            continue
        r = engine.eroeffne(pf, funds.UNBEGRENZT, inst, book, usd=NEIN_EINSATZ * pf["start_kapital"], equity=eq, ts=jetzt,
                            ausstiegsplan="Halten bis zur Abrechnung (Kontrollregel)")
        log.append(r)
        kaeufe += bool(r.get("ok"))
    pf["kontrolle_bis"] = ts_max
    return log
