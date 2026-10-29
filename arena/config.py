"""Konfiguration laden (arena/config.json). Pfade des Repos."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


@lru_cache(maxsize=1)
def load() -> dict:
    return json.loads((Path(__file__).parent / "config.json").read_text(encoding="utf-8"))
