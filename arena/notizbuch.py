"""Notizbuch je Fonds (append-only JSONL): Thesen, Lektionen, Beobachtungen. Wird dem Agenten in jeder Runde vorgelegt."""
from __future__ import annotations

import time

from arena import store

TYPEN = ("these", "lektion", "beobachtung", "regel")


def schreibe(fid: str, typ: str, text: str, ts: float | None = None, **extra) -> dict:
    eintrag = {"ts": ts or time.time(), "typ": typ if typ in TYPEN else "beobachtung", "text": text[:1200], **extra}
    store.anhaengen(f"funds/{fid}/notizbuch.jsonl", eintrag)
    return eintrag


def lies(fid: str, n: int = 40) -> list[dict]:
    return store.lies_jsonl(f"funds/{fid}/notizbuch.jsonl", n)


def als_text(fid: str, n: int = 40) -> str:
    eintraege = lies(fid, n)
    if not eintraege:
        return "(leer – du beginnst ohne Vorwissen. Halte Thesen und Lektionen fest.)"
    from datetime import datetime, timezone
    return "\n".join(f"- [{datetime.fromtimestamp(e['ts'], timezone.utc):%d.%m %H:%M}] ({e['typ']}) {e['text']}" for e in eintraege)
