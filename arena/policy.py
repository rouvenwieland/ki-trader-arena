"""Policy-Gate aus der eigenen Bilanz (Muster „Edge Policy“, deterministisch, ohne LLM).

Nach jeder Abrechnung: Eine Kategorie (Art + Thema, bei Wetten + Seite, bei Perps + Richtung) mit mindestens MIN_TRADES
abgeschlossenen Trades und negativer Netto-Bilanz wird für neue Käufe gesperrt. Die Sperre wird nur verschärft, nie
automatisch gelockert; lockern darf nur das Opus-Wochen-Review (mit Begründung, protokolliert)."""
from __future__ import annotations

import time

from arena import store, themen

MIN_TRADES = 5
SCHLIESS = ("geschlossen", "teilweise_geschlossen", "liquidiert")


def kategorie_aus_eintrag(e: dict) -> str:
    if e.get("kategorie"):
        return e["kategorie"]
    iid = e.get("inst_id", "")
    teile = iid.split(":")
    if teile[0] == "pm":
        return f"wette:unbekannt:{teile[-1]}"
    art = {"opt": "option"}.get(teile[0], teile[0])
    k = f"{art}:{'krypto' if art in ('spot', 'perp', 'option') else 'aktien'}"
    return k + (f":{e.get('seite')}" if art == "perp" else "")


def kategorie_inst(inst: dict, seite: str = "long") -> str:
    k = themen.wette_kategorie(inst)
    return k + (f":{seite}" if inst.get("art") == "perp" or (inst.get("art") == "stock" and seite == "short") else "")


def bilanz(fid: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for e in store.lies_jsonl(f"funds/{fid}/ledger.jsonl"):
        if e.get("aktion") in SCHLIESS and "netto_pnl" in e:
            b = out.setdefault(kategorie_aus_eintrag(e), {"n": 0, "pnl": 0.0})
            b["n"] += 1
            b["pnl"] += e["netto_pnl"]
    return out


def aktualisiere(fid: str, jetzt: float | None = None) -> list[str]:
    """Neue Sperren eintragen (nur verschärfen). Liefert neu gesperrte Kategorien."""
    jetzt = jetzt or time.time()
    z = store.lies(f"funds/{fid}/policy.json", {"gesperrt": {}, "freigegeben": {}})
    neu = []
    for k, b in bilanz(fid).items():
        frei = z["freigegeben"].get(k)
        if b["n"] >= MIN_TRADES and b["pnl"] < 0 and k not in z["gesperrt"] and not (frei and b["n"] <= frei.get("bei_n", 0)):
            z["gesperrt"][k] = {"seit": jetzt, "grund": f"{b['n']} Trades, netto {b['pnl']:+.0f} USD"}
            neu.append(k)
    if neu:
        store.schreibe(f"funds/{fid}/policy.json", z)
        store.anhaengen(f"funds/{fid}/decisions.jsonl", {"typ": "policy", "ts": jetzt, "gesperrt": neu})
    return neu


def sperren(fid: str) -> list[dict]:
    z = store.lies(f"funds/{fid}/policy.json", {"gesperrt": {}})
    return [{"kategorie": k, **v} for k, v in z.get("gesperrt", {}).items()]


def gesperrt(fid: str, inst: dict, seite: str = "long") -> str | None:
    k = kategorie_inst(inst, seite)
    return k if k in store.lies(f"funds/{fid}/policy.json", {"gesperrt": {}}).get("gesperrt", {}) else None


def freigeben(fid: str, kategorie: str, grund: str, jetzt: float | None = None) -> bool:
    """Nur für das Opus-Review: hebt eine Sperre auf. Bis zum nächsten neuen Trade dieser Kategorie wird nicht erneut gesperrt."""
    z = store.lies(f"funds/{fid}/policy.json", {"gesperrt": {}, "freigegeben": {}})
    if kategorie not in z["gesperrt"]:
        return False
    z["gesperrt"].pop(kategorie)
    z["freigegeben"][kategorie] = {"ts": jetzt or time.time(), "grund": grund[:300], "bei_n": bilanz(fid).get(kategorie, {}).get("n", 0)}
    store.schreibe(f"funds/{fid}/policy.json", z)
    store.anhaengen(f"funds/{fid}/decisions.jsonl", {"typ": "policy", "ts": jetzt or time.time(), "freigegeben": kategorie, "grund": grund[:300]})
    return True
