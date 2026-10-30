"""Baut docs/data.json (für die Webseite) und docs/status.json (maschinenlesbar, für das Laptop-Widget).
Aufruf: python -m arena.site – reine Dateiarbeit, kein Netzwerk."""
from __future__ import annotations

import time

from arena import config, funds, metrics, store
from arena.agent import route

DOCS = config.ROOT / "docs"


def _runter(punkte: list[dict], n: int = 400) -> list[list]:
    if len(punkte) > n:
        schritt = len(punkte) / n
        punkte = [punkte[int(i * schritt)] for i in range(n)] + [punkte[-1]]
    return [[p["t"], p["usd"]] for p in punkte]


def _runter_punkte(punkte: list, n: int) -> list:
    if len(punkte) <= n:
        return punkte
    schritt = (len(punkte) - 1) / (n - 1)
    return [punkte[round(i * schritt)] for i in range(n)]


def fonds_datensatz(d: dict, fx: float) -> dict | None:
    pf = funds.lade_portfolio(d["id"])
    meta = funds.meta(d["id"])
    if not pf:
        return {"id": d["id"], "name": d["name"], "typ": d["typ"], "risiko": d.get("risiko"), "status": meta.get("status") or "wartet auf Schlüssel",
                "modell": d.get("modell"), "kennzahlen": {}, "verlauf": [], "positionen": [], "entscheidungen": [], "notizbuch": []}
    eq = store.lies_jsonl(f"funds/{d['id']}/equity.jsonl")
    k = metrics.kennzahlen(d["id"])

    dec = store.lies_jsonl(f"funds/{d['id']}/decisions.jsonl", 80)
    orders = [x for x in dec if x.get("typ") == "order"][-25:]
    led = {x.get("entscheidung_id"): x for x in store.lies_jsonl(f"funds/{d['id']}/ledger.jsonl", 400) if x.get("entscheidung_id")}
    for o in orders:
        r = led.get(o["id"])
        o["ergebnis"] = None if not r else {k2: r.get(k2) for k2 in ("ok", "grund", "preis", "menge", "gebuehr", "nominal", "netto_pnl") if k2 in r}
    runden = [x for x in dec if x.get("typ") == "runde"][-10:]
    from arena import notizbuch
    return {"id": d["id"], "name": d["name"], "typ": d["typ"], "risiko": d.get("risiko"), "modell": meta.get("modell_aktuell") or d.get("modell"),
            "status": meta.get("status") or ("läuft" if d["typ"] == "benchmark" else "wartet auf ersten Lauf"),
            "start": pf.get("erstellt"), "kennzahlen": k, "verlauf": _runter(eq),
            "positionen": [{"id": p["id"], "inst": p["inst"]["id"], "name": p["inst"].get("frage") or p["inst"].get("symbol"), "seite": p["seite"],
                            "menge": p["menge"], "einstand": p["einstand"], "kurs": p.get("kurs"), "wert": p.get("wert"), "hebel": p.get("hebel", 1),
                            "stop": p.get("stop_loss"), "ziel": p.get("take_profit"), "plan": p.get("ausstiegsplan"),
                            "schliesst": p["inst"].get("schliesst"), "liq": p.get("liq_preis")} for p in pf["positionen"]],
            "entscheidungen": orders, "runden": runden, "notizbuch": notizbuch.lies(d["id"], 12)}


def _wette(inst_id: str) -> str:
    """Worauf eine Position eigentlich setzt: Wettmarkt+Seite, bei Krypto der Basiswert samt Richtung (Spot/Perp long = gleiche Wette)."""
    teile = inst_id.split(":")
    if teile[0] == "pm":
        return inst_id
    if teile[0] in ("spot", "perp"):
        return "krypto:" + teile[1].split("-")[0].split("_")[0]
    return inst_id


def ueberlappung(fonds: list[dict]) -> dict:
    """Klumpenrisiko: Für jedes Fondspaar der Anteil des (kleineren) investierten Kapitals, der in denselben Wetten steckt.
    0 % = völlig verschiedene Wetten, 100 % = der kleinere Fonds ist eine Teilmenge des größeren."""
    def gewichte(f: dict) -> dict[str, float]:
        g: dict[str, float] = {}
        for p in f["positionen"]:
            key = _wette(p["inst"]) + (":short" if p["seite"] == "short" else "")
            g[key] = g.get(key, 0.0) + abs(p.get("wert") or 0.0)
        return g
    w = {f["id"]: gewichte(f) for f in fonds}
    paare = []
    for i, a in enumerate(fonds):
        for b in fonds[i + 1:]:
            ga, gb = w[a["id"]], w[b["id"]]
            if not ga or not gb:
                continue
            gemeinsam = sum(min(ga[k], gb[k]) for k in ga.keys() & gb.keys())
            basis = min(sum(ga.values()), sum(gb.values()))
            paare.append({"a": a["id"], "b": b["id"], "pct": round(100 * gemeinsam / basis, 1) if basis else 0.0,
                          "gemeinsam": sorted(ga.keys() & gb.keys())})
    mittel = round(sum(p["pct"] for p in paare) / len(paare), 1) if paare else None
    return {"mittel_pct": mittel, "paare": paare}


def kosten_je_fonds(fx: float, jetzt: float) -> dict:
    """API-Kosten je Fonds (€): heute, gesamt, je Modell und Zweck (Runde, Tiefenrunde, Vorsichter)."""
    tag = time.strftime("%Y-%m-%d", time.gmtime(jetzt))
    out: dict[str, dict] = {}
    for x in store.lies_jsonl("budget_log.jsonl"):
        f = out.setdefault(x.get("fonds", "?"), {"heute_eur": 0.0, "gesamt_eur": 0.0, "modelle": {}, "aufrufe": 0})
        eur = x.get("usd", 0) / fx
        f["gesamt_eur"] += eur
        f["aufrufe"] += 1
        if time.strftime("%Y-%m-%d", time.gmtime(x.get("ts", 0))) == tag:
            f["heute_eur"] += eur
        m = x.get("modell", "?")
        f["modelle"][m] = f["modelle"].get(m, 0.0) + eur
    for f in out.values():
        f["heute_eur"], f["gesamt_eur"] = round(f["heute_eur"], 3), round(f["gesamt_eur"], 3)
        f["modelle"] = {k: round(v, 3) for k, v in f["modelle"].items()}
    return out


def bauen(jetzt: float | None = None) -> dict:
    jetzt = jetzt or time.time()
    fx = (store.lies("fx.json") or {}).get("usd_je_eur", config.load()["fallback_usd_je_eur"])
    daten = [x for x in (fonds_datensatz(d, fx) for d in funds.alle_definitionen()) if x]
    bud = store.lies("budget_status.json", {})
    bz = store.lies("budget.json", {"gesamt_usd": 0, "tage": {}})
    ev = store.lies_jsonl("events.jsonl", 60)[-40:][::-1]
    switches = store.lies_jsonl("model_switches.jsonl")
    aktive = [f for f in daten if f["kennzahlen"]]
    rang = sorted(aktive, key=lambda f: -f["kennzahlen"]["rendite_pct"])
    kosten = kosten_je_fonds(fx, jetzt)
    for f in daten:
        f["kosten"] = kosten.get(f["id"])
    ki = [f for f in daten if f["typ"] != "benchmark" and f["kennzahlen"]]
    ueb = {"claude": ueberlappung([f for f in ki if f["typ"] == "claude"]), "ki": ueberlappung(ki)}
    bs = store.lies("budget_status.json", {})
    gesamt = {"ts": jetzt, "fx": fx, "fonds": daten, "ereignisse": ev, "modellwechsel": switches, "ueberlappung": ueb,
              "kosten_sonstige": {k: v for k, v in kosten.items() if not any(f["id"] == k for f in daten)},
              "budget": {"heute_eur": round(bz["tage"].get(time.strftime("%Y-%m-%d", time.gmtime(jetzt)), 0) / fx, 2),
                         "gesamt_eur": round(bz["gesamt_usd"] / fx, 2), "tagesdeckel_eur": config.load()["budget"]["tagesdeckel_eur"],
                         "gesamtdeckel_eur": config.load()["budget"]["gesamtdeckel_eur"], "claude_ende": config.load()["budget"]["claude_ende"],
                         "ziel_tag_eur": round(sum(config.load()["budget"].get("fonds_tagesanteil_eur", {}).values()), 2),
                         "tempo_faktor": bs.get("tempo_faktor")},
              "rangliste": [f["id"] for f in rang]}
    DOCS.mkdir(exist_ok=True)
    import json
    (DOCS / "data.json").write_text(json.dumps(gesamt, ensure_ascii=False, separators=(",", ":"), default=str), encoding="utf-8")
    status = {"version": 1, "stand": jetzt, "hinweis": "Papierhandel-Simulation, keine Anlageberatung",
              "seite": "https://rouvenwieland.github.io/ki-trader-arena/",
              "budget": gesamt["budget"], "ueberlappung_claude_pct": ueb["claude"]["mittel_pct"],
              "rangliste": [{"rang": i + 1, "id": f["id"], "name": f["name"], "typ": f["typ"], "rendite_pct": round(f["kennzahlen"]["rendite_pct"], 2),
                             "equity_eur": round(f["kennzahlen"]["equity_usd"] / fx, 2), "max_drawdown_pct": round(f["kennzahlen"]["max_drawdown_pct"], 2),
                             "status": f["status"], "modell": f.get("modell"),
                             "kosten_heute_eur": (f.get("kosten") or {}).get("heute_eur", 0.0),
                             "kosten_gesamt_eur": (f.get("kosten") or {}).get("gesamt_eur", 0.0),
                             "verlauf_pct": [round((p[1] / f["kennzahlen"]["start_usd"] - 1) * 100, 2) for p in _runter_punkte(f["verlauf"], 40)]}
                            for i, f in enumerate(rang)],
              "wartend": [{"id": f["id"], "name": f["name"], "status": f["status"]} for f in daten if not f["kennzahlen"]],
              "letzte_entscheidungen": sorted([{"ts": o["ts"], "fonds": f["name"], "instrument": o["instrument"], "aktion": o["aktion"],
                                                "zuversicht": o["zuversicht"]} for f in daten for o in f["entscheidungen"]], key=lambda x: -x["ts"])[:8],
              "ereignisse": [{"ts": e["ts"], "typ": e["typ"], "titel": e["titel"]} for e in ev[:8]]}
    (DOCS / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=1), encoding="utf-8")
    return gesamt


if __name__ == "__main__":
    g = bauen()
    print("docs/data.json:", len(g["fonds"]), "Fonds")
