"""Zustand im Repo (data/): JSON für Momentaufnahmen, JSONL append-only für Verläufe."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from arena import config


def pfad(*teile: str, anlegen: bool = True) -> Path:
    p = config.DATA.joinpath(*teile)
    if anlegen:
        p.parent.mkdir(parents=True, exist_ok=True)
    return p


def lies(rel: str | Path, default=None):
    p = Path(rel) if str(rel).startswith("/") else pfad(*str(rel).split("/"), anlegen=False)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def schreibe(rel: str, obj) -> None:
    """Atomar schreiben (tmp + rename)."""
    p = pfad(*rel.split("/"))
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False), encoding="utf-8")
    os.replace(tmp, p)


def anhaengen(rel: str, obj) -> None:
    """Append-only JSONL: bestehende Zeilen werden nie verändert."""
    p = pfad(*rel.split("/"))
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def lies_jsonl(rel: str, letzte: int | None = None) -> list[dict]:
    p = pfad(*rel.split("/"), anlegen=False)
    if not p.exists():
        return []
    zeilen = p.read_text(encoding="utf-8").splitlines()
    if letzte:
        zeilen = zeilen[-letzte:]
    out = []
    for z in zeilen:
        try:
            out.append(json.loads(z))
        except json.JSONDecodeError:
            pass
    return out


def jetzt() -> float:
    return time.time()
