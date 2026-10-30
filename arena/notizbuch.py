"""Notizbuch je Fonds (append-only JSONL): Thesen, Lektionen, Beobachtungen, Regeln. Wird dem Agenten in jeder Runde vorgelegt.

Geschichtet (Recherche M8, FinMem/TradingGPT): jeder Eintrag hat eine Wichtigkeit (1–10) und optional ein Ablaufdatum. Vorgelegt werden
die Einträge mit dem höchsten Wert aus Wichtigkeit × Zerfall (Halbwertszeit je Typ) plus Bonus bei Stichwort-Treffern mit den aktuellen
Ereignissen/Positionen – statt nur der letzten 40 (dort gingen Lektionen unter)."""
from __future__ import annotations

import math
import re
import time
from datetime import datetime, timezone

from arena import store

TYPEN = ("these", "lektion", "beobachtung", "regel")
TAU_TAGE = {"beobachtung": 3, "these": 14, "lektion": 90, "regel": 365}
WICHTIG_STANDARD = {"beobachtung": 3, "these": 5, "lektion": 7, "regel": 8}


def schreibe(fid: str, typ: str, text: str, ts: float | None = None, wichtigkeit: float | None = None,
             gueltig_tage: float | None = None, **extra) -> dict:
    typ = typ if typ in TYPEN else "beobachtung"
    ts = ts or time.time()
    w = WICHTIG_STANDARD[typ] if wichtigkeit is None else max(1.0, min(10.0, float(wichtigkeit)))
    eintrag = {"ts": ts, "typ": typ, "text": text[:1200], "wichtigkeit": w, **extra}
    if gueltig_tage:
        eintrag["gueltig_bis"] = ts + float(gueltig_tage) * 86400
    store.anhaengen(f"funds/{fid}/notizbuch.jsonl", eintrag)
    return eintrag


def lies(fid: str, n: int = 40) -> list[dict]:
    return store.lies_jsonl(f"funds/{fid}/notizbuch.jsonl", n)


def _worte(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-zäöüß0-9]{4,}", (t or "").lower())}


def wert(e: dict, jetzt: float, kontext: set[str]) -> float:
    if e.get("gueltig_bis") and e["gueltig_bis"] < jetzt:
        return -1.0
    typ = e.get("typ", "beobachtung")
    w = e.get("wichtigkeit", WICHTIG_STANDARD.get(typ, 3))
    alter = max(0.0, (jetzt - e["ts"]) / 86400)
    bonus = 3.0 if kontext and len(_worte(e["text"]) & kontext) >= 2 else 0.0
    return w * math.exp(-alter / TAU_TAGE.get(typ, 14)) + bonus


def auswahl(fid: str, n: int = 40, kontext_text: str = "", jetzt: float | None = None) -> list[dict]:
    jetzt = jetzt or time.time()
    alle = store.lies_jsonl(f"funds/{fid}/notizbuch.jsonl", 2000)
    kontext = _worte(kontext_text)
    bewertet = sorted(((wert(e, jetzt, kontext), i, e) for i, e in enumerate(alle)), key=lambda t: (-t[0], -t[1]))
    gewaehlt = [(i, e) for s, i, e in bewertet if s > 0][:n]
    return [e for _, e in sorted(gewaehlt, key=lambda t: t[0])]  # chronologisch vorlegen


def als_text(fid: str, n: int = 40, kontext_text: str = "") -> str:
    eintraege = auswahl(fid, n, kontext_text)
    if not eintraege:
        return "(leer – du beginnst ohne Vorwissen. Halte Thesen und Lektionen fest.)"
    return "\n".join(f"- [{datetime.fromtimestamp(e['ts'], timezone.utc):%d.%m %H:%M}] ({e['typ']}, W{e.get('wichtigkeit', WICHTIG_STANDARD.get(e['typ'], 3)):.0f}) {e['text']}"
                     for e in eintraege)
