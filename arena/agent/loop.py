"""Schlanke Agentenschleife mit Tool-Use (siehe DECISIONS.md: warum nicht Hermes Agent).
Hartes Budget: vor jedem Aufruf wird Worst-Case-Kosten geprüft, nach jedem Aufruf gebucht."""
from __future__ import annotations

import json
import time

from arena import funds, store
from arena.agent import budget as bmod
from arena.agent import llm, prompts
from arena.agent.tools import Kontext

MAX_SCHRITTE = {"claude": 14, "liga": 8}
MAX_SEKUNDEN = {"claude": 600, "liga": 420}  # Wanduhr-Limit je Runde (freie Modelle antworten teils minutenlang)


def _verlauf_zeichen(s) -> int:
    return len(json.dumps(s.nachrichten, default=str))


def triage(defn: dict, ereignisse: list[dict], pf_info: str, bud: bmod.Budget, n_fonds: int) -> tuple[bool, str]:
    """Haiku sichtet vor (billig). Bei Fehlern/Budgetmangel: lieber nicht wecken."""
    modell = "claude-haiku-5-5"
    ok, grund = bud.darf(defn["id"], n_fonds, bmod.schaetze_naechsten_aufruf(modell, 6000, 300))
    if not ok:
        return False, grund
    ev = "\n".join(f"- [{e['typ']}] {e['titel']}" for e in ereignisse[:25])
    try:
        s = llm.AnthropicSitzung(modell, prompts.TRIAGE, [], websuche=0, effort="low", max_tokens=300)
        s.nutzer(f"Fonds: {defn['name']} ({defn.get('risiko')})\n{pf_info}\nEreignisse:\n{ev}")
        a = s.schritt()
        bud.buche(defn["id"], modell, a.nutzung, "triage")
        j = json.loads(a.text[a.text.index("{"): a.text.rindex("}") + 1])
        return bool(j.get("aufwecken")), str(j.get("grund", ""))
    except Exception as e:  # Triage-Fehler dürfen nichts blockieren
        return True, f"Triage fehlgeschlagen ({type(e).__name__}) – Runde zur Sicherheit"


def laufe_runde(defn: dict, route: dict, pf: dict, snap: dict, mz, grund: str, ereignisse: list[dict],
                bud: bmod.Budget | None, n_fonds: int, jetzt: float | None = None,
                sitzung_fabrik=None) -> dict:
    """Eine komplette Agentenrunde. Liefert Ergebnis-Dict (auch bei Abbruch)."""
    jetzt = jetzt or time.time()
    from arena import snapshot as snapmod
    ctx = Kontext(defn, pf, snap, mz, grund, ereignisse, jetzt)
    tools = ctx.definitionen()
    sys_prompt = prompts.system_prompt(defn, ctx.prof)
    if sitzung_fabrik:
        s = sitzung_fabrik(sys_prompt, tools)
    elif route["art"] == "anthropic":
        s = llm.AnthropicSitzung(route["modell"], sys_prompt, tools, websuche=6, effort="high", max_tokens=8000)
    else:
        s = llm.openai_sitzung(route["anbieter"], route["modell"], sys_prompt, tools, route["key"])
    s.nutzer(prompts.runde_prompt(defn, grund, ereignisse, snapmod.text(snap), jetzt))
    modell = route["modell"]
    ist_claude = route["art"] == "anthropic"
    kosten, schritte, text, abbruch = 0.0, 0, "", ""
    gesamt_nutzung = {"ein": 0, "aus": 0, "cache_lesen": 0, "cache_schreiben": 0, "websuchen": 0}
    try:
        typ = defn["typ"] if defn["typ"] in MAX_SCHRITTE else "liga"
        start = time.time()
        while schritte < MAX_SCHRITTE[typ]:
            if time.time() - start > MAX_SEKUNDEN[typ]:
                abbruch = "Zeitlimit der Runde erreicht"
                break
            if ist_claude and bud:
                ok, warum = bud.darf(defn["id"], n_fonds, bmod.schaetze_naechsten_aufruf(modell, _verlauf_zeichen(s), 8000))
                if not ok:
                    abbruch = f"Budget-Stopp: {warum}"
                    break
            a = s.schritt()
            schritte += 1
            for k in gesamt_nutzung:
                gesamt_nutzung[k] += a.nutzung.get(k, 0)
            if ist_claude and bud:
                kosten += bud.buche(defn["id"], modell, a.nutzung, "runde")
            if a.text:
                text = a.text
            if a.aufrufe:
                erg = []
                for c in a.aufrufe:
                    out, fehler = ctx.fuehre_aus(c["name"], c["input"])
                    erg.append((c["id"], out, fehler))
                s.tool_ergebnisse(erg)
                continue
            if a.ende == "pause_turn":
                continue
            break
        else:
            abbruch = "Schrittlimit erreicht"
    except llm.LLMFehler as e:
        abbruch = f"Modellfehler: {e}"
        if "401" in str(e) or "403" in str(e):
            import arena
            abbruch += f" [Schlüssel abgelehnt – {arena.schluessel_info('ARENA_ANTHROPIC_KEY') if route['art'] == 'anthropic' else 'Fremdanbieter'}]"
    except Exception as e:
        abbruch = f"Fehler: {type(e).__name__}: {e}"
    ergebnis = {"typ": "runde", "ts": jetzt, "fonds_id": defn["id"], "grund": grund, "modell": modell, "schritte": schritte,
                "orders": ctx.orders, "text": text[:4000], "abbruch": abbruch, "kosten_usd": round(kosten, 4), "nutzung": gesamt_nutzung}
    store.anhaengen(f"funds/{defn['id']}/decisions.jsonl", ergebnis)
    store.anhaengen(f"funds/{defn['id']}/nutzung.jsonl", {"ts": jetzt, "modell": modell, **gesamt_nutzung, "usd": round(kosten, 4)})
    funds.speichere_portfolio(pf)
    return ergebnis
