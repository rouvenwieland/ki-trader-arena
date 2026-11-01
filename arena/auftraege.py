"""Bedingte Aufträge (Papierhandel): Markt-Auftrag zur Eröffnung, Limit und Stop – für alle Instrumente, mit Gültigkeit Tag/GTC/Datum.

Ausführung im Wächter (alle 15 min) gegen das dann gültige Buch und die Kursspanne seit der letzten Prüfung (Dochte):
* Limit-Kauf: Briefkurs ≤ Limit → Füllung gegen die Buchstufen bis zum Limit; oder das Tief lag mindestens 5 bp unter dem Limit
  (Kurs ist durchgehandelt) → Füllung genau zum Limit. Limit-Verkauf spiegelbildlich (Geldkurs ≥ Limit bzw. Hoch ≥ Limit + 5 bp).
  Ein bloßes Berühren reicht nicht (in der Warteschlange stünden andere vorn) – konservativ.
* Stop-Kauf: Briefkurs bzw. Hoch ≥ Stop → Kauf zum Stop-Preis plus Marktimpact, bei Kurslücke zum schlechteren aktuellen Buch.
  Stop-Verkauf spiegelbildlich.
Limits, Cash und Risiko werden erst bei der Ausführung geprüft (kein Kapital reserviert)."""
from __future__ import annotations

import math
import time
import uuid
from datetime import datetime, timezone

from arena.exchange import engine, portfolio
from arena.exchange.book import Book

TYPEN = ("eroeffnung", "limit", "stop")
MAX_OFFEN = 10
DURCHHANDEL = 5e-4  # 5 bp


def gueltig_bis(inst: dict, gueltigkeit: str | None, jetzt: float) -> float:
    g = (gueltigkeit or "tag").strip().lower()
    if g == "gtc":
        return jetzt + 30 * 86400
    if g != "tag":
        try:
            t = datetime.fromisoformat(gueltigkeit.replace("Z", "+00:00"))
            t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
            return min(max(t.timestamp(), jetzt + 900), jetzt + 30 * 86400)
        except (ValueError, AttributeError):
            pass
    if inst["art"] == "stock":
        from arena.data import stocks
        return stocks.schluss_nach(inst["symbol"], jetzt)
    return jetzt + 86400


def kaufseite(a: dict, pf: dict) -> bool:
    """True, wenn der Auftrag auf der Briefseite ausgeführt wird (Kauf long, Rückkauf eines Leerverkaufs)."""
    if a["aktion"] == "kaufen":
        return a.get("seite", "long") == "long"
    pos = next((p for p in pf["positionen"] if p["inst"]["id"] == a["inst"]["id"]), None)
    return bool(pos) and pos["seite"] == "short"


def neu(pf: dict, did: str, inst: dict, aktion: str, typ: str, *, seite: str = "long", betrag_usd=None, menge=None, hebel: float = 1.0,
        limit_preis=None, stop_preis=None, gueltigkeit: str | None = None, stop_loss=None, take_profit=None, ausstiegsplan: str = "",
        invalidierung: str = "", jetzt: float | None = None) -> dict:
    jetzt = jetzt or time.time()
    a = {"id": "a" + uuid.uuid4().hex[:6], "entscheidung_id": did, "inst": inst, "aktion": aktion, "typ": typ, "seite": seite,
         "betrag_usd": betrag_usd, "menge": menge, "hebel": hebel, "limit_preis": limit_preis, "stop_preis": stop_preis,
         "stop_loss": stop_loss, "take_profit": take_profit, "ausstiegsplan": ausstiegsplan, "invalidierung": (invalidierung or "")[:300],
         "erstellt": jetzt, "geprueft_bis": jetzt, "gueltig_bis": gueltig_bis(inst, gueltigkeit, jetzt)}
    pf.setdefault("auftraege", []).append(a)
    return a


def fuellbuch(a: dict, kauf: bool, book: Book | None, ex: tuple[float, float] | None) -> tuple[Book | None, float | None]:
    """Buch, gegen das der Auftrag jetzt ausgeführt wird (und Slippage-Vorgabe), oder (None, None), wenn er nicht auslöst."""
    if book is None or (not book.asks and not book.bids):
        return None, None  # Markt geschlossen / kein Kurs
    typ = a["typ"]
    if typ == "eroeffnung":
        return book, None
    if typ == "limit":
        L = a["limit_preis"]
        if kauf:
            lv = [(p, q) for p, q in book.asks if p <= L]
            if lv:
                return Book(book.bids, lv, book.ts, book.mark), 0.0
            if ex and ex[0] < L * (1 - DURCHHANDEL):
                return Book([(L, 1e9)], [(L, 1e9)], book.ts, book.mark), 0.0
        else:
            lv = [(p, q) for p, q in book.bids if p >= L]
            if lv:
                return Book(lv, book.asks, book.ts, book.mark), 0.0
            if ex and ex[1] > L * (1 + DURCHHANDEL):
                return Book([(L, 1e9)], [(L, 1e9)], book.ts, book.mark), 0.0
        return None, None
    if typ == "stop":
        S = a["stop_preis"]
        from arena.watcher import _stop_buch
        if kauf and ((book.asks and book.asks[0][0] >= S) or (ex and ex[1] >= S)):
            return _stop_buch(S, "short", book, a.get("menge") or 0.0, a["inst"]), None
        if not kauf and ((book.bids and book.bids[0][0] <= S) or (ex and ex[0] <= S)):
            return _stop_buch(S, "long", book, a.get("menge") or 0.0, a["inst"]), None
    return None, None


def ausfuehren(pf: dict, prof: dict, a: dict, book: Book, slip: float | None, mz, jetzt: float) -> dict:
    marks = {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]}
    eq = portfolio.equity(pf, marks)
    if a["aktion"] == "kaufen":
        r = engine.eroeffne(pf, prof, a["inst"], book, seite=a.get("seite", "long"), qty=a.get("menge"), usd=a.get("betrag_usd"),
                            hebel=float(a.get("hebel") or 1), equity=eq, stop_loss=a.get("stop_loss"), take_profit=a.get("take_profit"),
                            ausstiegsplan=a.get("ausstiegsplan", ""), entscheidung_id=a["entscheidung_id"], ts=jetzt, slippage_bps=slip)
        if r.get("ok") and a.get("invalidierung"):
            pos = next((p for p in pf["positionen"] if p["id"] == r["position_id"]), None)
            if pos is not None:
                pos["invalidierung"] = a["invalidierung"]
    else:
        pos = next((p for p in pf["positionen"] if p["inst"]["id"] == a["inst"]["id"]), None)
        r = engine.schliesse(pf, pos, book, qty=a.get("menge"), grund=f"{a['typ'].capitalize()}-Auftrag", ts=jetzt, slippage_bps=slip) if pos else \
            {"ok": False, "grund": "Position nicht mehr vorhanden"}
    return {**r, "ts": jetzt, "fonds_id": pf["fonds_id"], "entscheidung_id": a["entscheidung_id"], "auftrag": a["id"], "auftragstyp": a["typ"]}


def pruefe(pf: dict, prof: dict, mz, jetzt: float) -> list[dict]:
    """Ein Wächter-Tick: offene Aufträge auslösen, verfallene entfernen."""
    log, rest = [], []
    for a in pf.get("auftraege", []):
        a.setdefault("typ", "eroeffnung")
        if jetzt > a["gueltig_bis"]:
            log.append({"ok": False, "ts": jetzt, "aktion": "auftrag_verfallen", "fonds_id": pf["fonds_id"], "inst_id": a["inst"]["id"],
                        "entscheidung_id": a["entscheidung_id"], "auftrag": a["id"], "grund": f"{a['typ'].capitalize()}-Auftrag verfallen"})
            continue
        book, _ = mz.buch(a["inst"])
        ex = mz.extreme(a["inst"], max(a.get("geprueft_bis", a["erstellt"]), a["erstellt"])) if a["typ"] != "eroeffnung" else None
        fb, slip = fuellbuch(a, kaufseite(a, pf), book, ex)
        if fb is not None and (book.asks or book.bids):
            a["geprueft_bis"] = jetzt
            r = ausfuehren(pf, prof, a, fb, slip, mz, jetzt)
            log.append(r)
            if r.get("ok") or a["typ"] == "eroeffnung":
                continue  # ausgeführt (oder Eröffnungsauftrag abgelehnt → erledigt)
        elif book is not None and (book.asks or book.bids):
            a["geprueft_bis"] = jetzt  # nur offene Handelszeit zählt für Dochte
        rest.append(a)
    pf["auftraege"] = rest
    return log


def sofort_ausfuehrbar(a: dict, kauf: bool, book: Book | None) -> bool:
    """Limit sofort ausführbar (Gegenseite kreuzt) bzw. Stop schon ausgelöst – ohne Dochte, nur das aktuelle Buch."""
    if book is None or (not book.asks and not book.bids):
        return False
    if a["typ"] == "limit":
        return bool(book.asks and book.asks[0][0] <= a["limit_preis"]) if kauf else bool(book.bids and book.bids[0][0] >= a["limit_preis"])
    if a["typ"] == "stop":
        return bool(book.asks and book.asks[0][0] >= a["stop_preis"]) if kauf else bool(book.bids and book.bids[0][0] <= a["stop_preis"])
    return False


def gueltiger_preis(x) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x) and x > 0
