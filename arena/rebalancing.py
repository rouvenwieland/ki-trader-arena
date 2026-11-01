"""Stehende Rebalancing-Regel je Fonds (Volatility Harvesting / „Shannons Dämon“): Zielgewichte für Long-Positionen in Krypto-Spot und
Aktien/ETFs; der Rest ist Cash. Der Wächter prüft alle 15 min und handelt die Differenz, sobald ein Gewicht mehr als `schwelle_pp`
Prozentpunkte vom Ziel abweicht – zu echten Kosten (Gebühr, Spread, Impact), mit den Limits des Fonds. Ob das nach Kosten etwas bringt,
misst der Kontrollfonds „Shannons Dämon“ (BTC/Cash 50/50)."""
from __future__ import annotations

from arena.exchange import engine, portfolio

ERLAUBT = ("spot", "stock")
MIN_HANDEL_USD = 50.0


def setze(pf: dict, ziele: list[dict], schwelle_pp: float, entscheidung_id: str | None, jetzt: float, aufloesen) -> str:
    if not ziele:
        pf.pop("rebalancing", None)
        return "Rebalancing-Regel entfernt."
    out = {}
    for z in ziele:
        inst = aufloesen(str(z.get("instrument_id", "")))
        try:
            anteil = float(z.get("anteil"))
        except (TypeError, ValueError):
            return f"Ungültiger Anteil bei {z.get('instrument_id')}."
        if not inst or inst["art"] not in ERLAUBT:
            return f"{z.get('instrument_id')}: Rebalancing nur für Krypto-Spot und Aktien/ETFs (long)."
        if not 0 <= anteil <= 1:
            return "Anteile zwischen 0 und 1 angeben."
        out[inst["id"]] = {"inst": inst, "anteil": anteil}
    if sum(v["anteil"] for v in out.values()) > 1 + 1e-9:
        return "Summe der Zielanteile darf 1 (100 % des Vermögens) nicht übersteigen; der Rest bleibt Cash."
    pf["rebalancing"] = {"ziele": out, "schwelle_pp": max(1.0, float(schwelle_pp)), "seit": jetzt, "entscheidung_id": entscheidung_id}
    return "Rebalancing-Regel gesetzt: " + ", ".join(f"{k} {100 * v['anteil']:.0f} %" for k, v in out.items()) + f" (Schwelle {pf['rebalancing']['schwelle_pp']:.0f} pp)."


def pruefe(pf: dict, prof: dict, mz, jetzt: float) -> list[dict]:
    r = pf.get("rebalancing")
    if not r:
        return []
    marks = {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]}
    eq = portfolio.equity(pf, marks)
    log = []
    for iid, z in r["ziele"].items():
        pos = next((p for p in pf["positionen"] if p["inst"]["id"] == iid and p["seite"] == "long" and not p.get("marginal")), None)
        m = marks.get(iid, {})
        wert = portfolio.pos_wert(pos, m.get("bid"), m.get("mark")) if pos else 0.0
        diff = z["anteil"] * eq - wert
        if abs(diff) / max(eq, 1e-9) * 100 < r["schwelle_pp"] or abs(diff) < MIN_HANDEL_USD:
            continue
        book, idx = mz.buch(z["inst"])
        if book is None or (not book.asks and not book.bids):
            continue  # Börse zu / kein Kurs
        if diff > 0:
            e = engine.eroeffne(pf, prof, z["inst"], book, usd=diff, equity=eq, ts=jetzt, entscheidung_id=r.get("entscheidung_id"),
                                ausstiegsplan="Rebalancing-Regel", index_preis=idx)
        else:
            px = book.bids[0][0] if book.bids else None
            if not pos or not px:
                continue
            e = engine.schliesse(pf, pos, book, qty=min(pos["menge"], -diff / px), grund="Rebalancing-Regel", ts=jetzt, index_preis=idx)
        log.append({**e, "rebalancing": True})
        marks = {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]}
        eq = portfolio.equity(pf, marks)
    return log
