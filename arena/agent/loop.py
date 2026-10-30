"""Schlanke Agentenschleife mit Tool-Use (siehe DECISIONS.md: warum nicht Hermes Agent).
Hartes Budget: vor jedem Aufruf wird Worst-Case-Kosten geprüft, nach jedem Aufruf gebucht."""
from __future__ import annotations

import json
import time

from arena import funds, store
from arena.agent import budget as bmod
from arena.agent import llm, prompts
from arena.agent.tools import Kontext

# Limits je Rundenart: „tief“ = tägliche Tiefenrunde (Opus), „claude“ = feste/ereignisgesteuerte Sonnet-Runde, „liga“ = Liga-Modelle
MAX_SCHRITTE = {"tief": 26, "claude": 20, "liga": 12}
MAX_SEKUNDEN = {"tief": 900, "claude": 600, "liga": 480}  # Wanduhr-Limit je Runde (freie Modelle antworten teils minutenlang)
WEBSUCHEN = {"tief": 12, "claude": 8}
SCHLUSS_SCHRITTE = 3  # so viele Schritte bleiben nach dem Abschluss-Hinweis, um Orders/Tagebuch zu schreiben
ABSCHLUSS = ("HINWEIS DER ARENA: {grund}. Keine weitere Recherche mehr – triff jetzt deine Entscheidungen (Orders, Wahrscheinlichkeiten, "
             "Notizbuch) mit dem, was du weißt, und schließe mit dem Tagebucheintrag ab.")


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
        s = llm.AnthropicSitzung(modell, prompts.TRIAGE, [], websuche=0, effort="low", max_tokens=1500)  # Haiku 5.5 denkt mit; 300 schnitt die JSON-Antwort teils ab
        s.nutzer(f"Fonds: {defn['name']} ({defn.get('risiko')})\n{pf_info}\nEreignisse:\n{ev}")
        a = s.schritt()
        bud.buche(defn["id"], modell, a.nutzung, "triage")
        j = json.loads(a.text[a.text.index("{"): a.text.rindex("}") + 1])
        plan = j.get("plan") if isinstance(j.get("plan"), list) else []
        return bool(j.get("aufwecken")), str(j.get("grund", "")) + (" | PLAN: " + " ; ".join(map(str, plan[:4])) if plan else "")
    except Exception as e:  # Triage-Fehler dürfen nichts blockieren
        return True, f"Triage fehlgeschlagen ({type(e).__name__}) – Runde zur Sicherheit"


def laufe_runde(defn: dict, route: dict, pf: dict, snap: dict, mz, grund: str, ereignisse: list[dict],
                bud: bmod.Budget | None, n_fonds: int, jetzt: float | None = None,
                sitzung_fabrik=None, runden_budget_usd: float | None = None, plan: list[str] | None = None) -> dict:
    """Eine komplette Agentenrunde. Liefert Ergebnis-Dict (auch bei Abbruch)."""
    jetzt = jetzt or time.time()
    from arena import snapshot as snapmod
    ctx = Kontext(defn, pf, snap, mz, grund, ereignisse, jetzt)
    ctx.bud = bud
    tools = ctx.definitionen()
    sys_prompt = prompts.system_prompt(defn, ctx.prof)
    ist_claude = route["art"] == "anthropic"
    typ = ("tief" if route.get("tief") else "claude") if ist_claude else "liga"
    max_aus = 20000 if typ == "tief" else 12000  # inkl. Denk-Tokens; gestreamt, daher ohne HTTP-Zeitlimit
    if sitzung_fabrik:
        s = sitzung_fabrik(sys_prompt, tools)
    elif ist_claude:
        s = llm.AnthropicSitzung(route["modell"], prompts.system_teile(defn, ctx.prof), tools, websuche=WEBSUCHEN[typ], effort="high", max_tokens=max_aus,
                                 timeout=420 if typ == "tief" else 300)
    else:
        s = llm.openai_sitzung(route["anbieter"], route["modell"], sys_prompt, tools, route["key"], route.get("alternativen"))
    s.nutzer(prompts.runde_prompt(defn, grund, ereignisse, snapmod.text(snap, defn=defn), jetzt, plan=plan))
    modell = route["modell"]
    kosten, schritte, text, abbruch = 0.0, 0, "", ""
    abschluss_ab = None  # Schritt, an dem der Abschluss-Hinweis kam
    abgeschnitten = 0
    gesamt_nutzung = {"ein": 0, "aus": 0, "cache_lesen": 0, "cache_schreiben": 0, "websuchen": 0}
    try:
        start = time.time()
        while True:
            if schritte >= MAX_SCHRITTE[typ]:
                abbruch = "Schrittlimit erreicht"
                break
            if time.time() - start > MAX_SEKUNDEN[typ]:
                abbruch = "Zeitlimit der Runde erreicht"
                break
            schaetzung = bmod.schaetze_naechsten_aufruf(modell, _verlauf_zeichen(s), max_aus) if ist_claude and bud else 0.0
            if abschluss_ab is None and schritte:
                warum = ("Schrittlimit naht" if schritte >= MAX_SCHRITTE[typ] - SCHLUSS_SCHRITTE else
                         "Zeit der Runde fast um" if time.time() - start > 0.75 * MAX_SEKUNDEN[typ] else
                         "Rundenbudget fast aufgebraucht" if runden_budget_usd is not None and kosten + kosten / schritte > runden_budget_usd else "")
                if warum:
                    abschluss_ab = schritte
                    if hasattr(s, "hinweis"):
                        s.hinweis(ABSCHLUSS.format(grund=warum))
            elif abschluss_ab is not None and schritte - abschluss_ab >= SCHLUSS_SCHRITTE:
                abbruch = "Abschluss nach Hinweis (Limit der Runde)"
                break
            if ist_claude and bud:
                ok, warum = bud.reserviere(defn["id"], n_fonds, schaetzung)
                if not ok:
                    abbruch = f"Budget-Stopp: {warum}"
                    break
            try:
                a = s.schritt()
            finally:
                if ist_claude and bud:
                    bud.freigeben()
            schritte += 1
            for k in gesamt_nutzung:
                gesamt_nutzung[k] += a.nutzung.get(k, 0)
            if ist_claude and bud:
                kosten += bud.buche(defn["id"], modell, a.nutzung, "tiefenrunde" if typ == "tief" else "runde")
            if a.text:
                text = a.text
            if a.ende == "max_tokens" and abgeschnitten < 2:  # abgeschnitten: nicht stillschweigend als Rundenende werten
                abgeschnitten += 1
                if a.aufrufe:  # angefangene Aufrufe sind evtl. unvollständig → nicht ausführen, aber beantworten (API verlangt tool_result)
                    s.tool_ergebnisse([(c["id"], "Nicht ausgeführt: Antwort wurde abgeschnitten.", True) for c in a.aufrufe])
                if hasattr(s, "hinweis"):
                    s.hinweis("HINWEIS DER ARENA: Deine letzte Antwort wurde abgeschnitten (Ausgabelimit). Angefangene Werkzeugaufrufe "
                              "wurden nicht ausgeführt. Arbeite in kleineren Schritten weiter und fasse dich kürzer.")
                continue
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
    except llm.KeinGuthaben as e:
        abbruch = f"Kein Guthaben: {e}"
    except llm.LLMFehler as e:
        abbruch = f"Modellfehler: {e}"
        if "401" in str(e) or "403" in str(e):
            import arena
            abbruch += f" [Schlüssel abgelehnt – {arena.schluessel_info('ARENA_ANTHROPIC_KEY') if route['art'] == 'anthropic' else 'Fremdanbieter'}]"
    except Exception as e:
        abbruch = f"Fehler: {type(e).__name__}: {e}"
    modell = getattr(s, "modell", modell)  # evtl. automatisch aufgelöster/ausgewichener Name
    ergebnis = {"typ": "runde", "ts": jetzt, "fonds_id": defn["id"], "grund": grund, "modell": modell, "schritte": schritte,
                "orders": ctx.orders, "text": text[:4000], "abbruch": abbruch, "kosten_usd": round(kosten, 4), "nutzung": gesamt_nutzung}
    store.anhaengen(f"funds/{defn['id']}/decisions.jsonl", ergebnis)
    store.anhaengen(f"funds/{defn['id']}/nutzung.jsonl", {"ts": jetzt, "modell": modell, **gesamt_nutzung, "usd": round(kosten, 4)})
    funds.speichere_portfolio(pf)
    return ergebnis


def triage_groq(defn: dict, ereignisse: list[dict], pf_info: str) -> tuple[bool, str]:
    """Groq (schnell, kleines Tokenlimit) sichtet nur vor – für Liga-Fonds, damit freie Modelle nicht bei jedem Ereignis laufen."""
    import os
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        return True, "kein Groq-Schlüssel – Runde ohne Vorsichter"
    try:
        from arena import config
        s = llm.openai_sitzung("groq", config.load().get("triage_groq_modell", "openai/gpt-oss-20b"), prompts.TRIAGE, [], key)
        ev = "\n".join(f"- [{e['typ']}] {e['titel'][:140]}" for e in ereignisse[:12])
        s.nutzer(f"Fonds: {defn['name']}\n{pf_info}\nEreignisse:\n{ev}")
        a = s.schritt()
        j = json.loads(a.text[a.text.index("{"): a.text.rindex("}") + 1])
        return bool(j.get("aufwecken")), str(j.get("grund", ""))
    except Exception as e:
        return True, f"Groq-Triage fehlgeschlagen ({type(e).__name__})"
