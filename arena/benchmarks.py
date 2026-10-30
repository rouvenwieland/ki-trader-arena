"""Vergleichsfonds ohne KI. Gehen durch dieselbe Börse (Gebühren, Spread, Slippage) wie die KI-Fonds."""
from __future__ import annotations

import random
from datetime import datetime, timezone

from arena import funds
from arena.data import crypto, stocks
from arena.exchange import engine, portfolio


def _kaufe(pf, inst, mz, anteil: float, jetzt: float, eq: float) -> dict | None:
    book, idx = mz.buch(inst)
    if book is None or not book.asks:
        return None
    r = engine.eroeffne(pf, funds.UNBEGRENZT, inst, book, usd=eq * anteil * 0.995, equity=eq, ts=jetzt, index_preis=idx)
    return r if r.get("ok") else None


def schritt(defn: dict, pf: dict, mz, marks: dict, jetzt: float) -> list[dict]:
    """Ein Wächter-Tick für einen Vergleichsfonds. Liefert Ledger-Einträge."""
    art = defn["art"]
    eq = portfolio.equity(pf, marks)
    out: list[dict] = []
    if art in ("btc", "sp500", "6040"):
        if pf["positionen"] or pf.get("gestartet"):
            return out
        ziele = {"btc": [(crypto.spot_inst("BTC"), 1.0)], "sp500": [(stocks.inst("SPY"), 1.0)],
                 "6040": [(stocks.inst("SPY"), 0.6), (stocks.inst("AGG"), 0.4)]}[art]
        ok = [_kaufe(pf, i, mz, a, jetzt, eq) for i, a in ziele]
        if all(ok):
            pf["gestartet"] = jetzt
        elif any(ok):  # unvollständig (z. B. Börse geschlossen): später ergänzen, Rest bleibt Cash
            pf["gestartet"] = jetzt
        out += [r for r in ok if r]
    elif art == "affe":
        tag = datetime.fromtimestamp(jetzt, timezone.utc).strftime("%Y-%m-%d")
        if pf.get("letzter_tag") == tag:
            return out
        rng = random.Random(f"{defn['id']}|{tag}")
        pf["letzter_tag"] = tag
        for pos in list(pf["positionen"]):  # täglich alles verkaufen
            book, idx = mz.buch(pos["inst"])
            if book and book.bids:
                r = engine.schliesse(pf, pos, book, grund="Zufallsaffe: Tageswechsel", ts=jetzt, index_preis=idx)
                if r.get("ok"):
                    out.append(r)
        eq = portfolio.equity(pf, {})
        kandidaten = [crypto.spot_inst(s) for s in ("BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "LINK", "AVAX")]
        for inst in rng.sample(kandidaten, k=rng.randint(1, 3)):
            r = _kaufe(pf, inst, mz, rng.uniform(0.1, 0.3), jetzt, eq)
            if r:
                out.append(r)
    return out
