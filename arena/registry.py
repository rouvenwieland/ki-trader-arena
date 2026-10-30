"""Verbindet Instrumente mit den Datenadaptern: Orderbuch, Marken, Extreme, Abrechnung."""
from __future__ import annotations

import time

from arena.data import crypto, pm, stocks
from arena.exchange.book import Book


class Marktzugriff:
    """Kapselt Abrufe eines Laufs mit Zwischenspeicher je Instrument (ein Buch pro Tick)."""

    def __init__(self):
        self._buecher: dict[str, tuple[Book | None, float | None]] = {}
        self.fehler: list[str] = []

    def buch(self, inst: dict) -> tuple[Book | None, float | None]:
        """(Orderbuch, Indexpreis) – Indexpreis nur für Optionen relevant."""
        iid = inst["id"]
        if iid in self._buecher:
            return self._buecher[iid]
        try:
            art = inst["art"]
            if art == "spot":
                r = (crypto.spot_buch(inst["symbol"]), None)
            elif art == "perp":
                r = (crypto.perp_buch(inst["symbol"]), None)
            elif art == "option":
                r = crypto.option_buch(inst["symbol"])
            elif art == "pm":
                r = (pm.buch(inst), None)
            elif art == "stock":
                r = (stocks.buch(inst["symbol"]), None)
            else:
                r = (None, None)
        except Exception as e:  # Netzwerk-/Parse-Fehler dürfen den Lauf nie abbrechen
            self.fehler.append(f"{iid}: {e}")
            r = (None, None)
        self._buecher[iid] = r
        return r

    def marke(self, inst: dict) -> dict:
        """{"bid","ask","mark"} für Bewertung; leer, wenn kein Kurs."""
        b, _ = self.buch(inst)
        if b is None:
            return {}
        return {"bid": b.best_bid, "ask": b.best_ask, "mark": b.mark if b.mark is not None else b.mid}

    def extreme(self, inst: dict, seit: float) -> tuple[float, float] | None:
        try:
            if inst["art"] == "spot":
                return crypto.spot_extreme(inst["symbol"], seit)
            if inst["art"] == "perp":
                return crypto.perp_extreme(inst["symbol"], seit)
        except Exception as e:
            self.fehler.append(f"extreme {inst['id']}: {e}")
        return None

    def aufloesung(self, inst: dict):
        try:
            if inst["art"] == "pm":
                return pm.aufloesung(inst)
            if inst["art"] == "option" and time.time() > inst["verfall"] + 3600:
                return crypto.abrechnungspreis(inst["basis"], inst["verfall"])
        except Exception as e:
            self.fehler.append(f"aufloesung {inst['id']}: {e}")
        return None


def preis_fuer_ereignisse(inst_marke: dict) -> float | None:
    """Referenzpreis (Mitte) für Ereignislogik."""
    b, a, m = inst_marke.get("bid"), inst_marke.get("ask"), inst_marke.get("mark")
    if b is not None and a is not None:
        return (b + a) / 2
    return m
