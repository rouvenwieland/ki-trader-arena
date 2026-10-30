"""Modell-Anbindung: Anthropic (offizielles SDK, Websuche als Server-Werkzeug) und OpenAI-kompatible Anbieter
(Gemini, OpenRouter, DeepSeek, Moonshot, Cerebras, Mistral, Groq, OpenAI) hinter einer gemeinsamen Sitzung.

Eine Sitzung hält den Gesprächsverlauf im jeweiligen Format. Der Verlauf wird nur angehängt, nie verändert."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field

import requests

from arena import config


class LLMFehler(Exception):
    pass


class KeinGuthaben(LLMFehler):
    """Anbieter meldet leeres Konto/Kontingent – Wiederholen ist zwecklos; der Fonds pausiert."""


# Bewusst eng: Geminis Minuten-Ratenlimit sagt auch „quota … billing“, ist aber nur vorübergehend.
_GUTHABEN_MUSTER = ("insufficient_quota", "no credits", "insufficient balance", "insufficient_balance", "credit balance",
                    "exceeded_current_quota", "account is suspended", "account_suspended")


def ist_kein_guthaben(status: int, text: str) -> bool:
    t = text.lower()
    return status == 402 or (status in (400, 403, 429) and any(m in t for m in _GUTHABEN_MUSTER))


def _warte(versuch: int, retry_after: str | None, basis: float = 5.0, maximal: float = 60.0) -> float:
    """Exponentielles Warten (5, 10, 20, 40 s …), Retry-After des Servers wird beachtet (gedeckelt)."""
    try:
        if retry_after:
            return min(float(retry_after), maximal)
    except ValueError:
        pass
    return min(basis * 2 ** versuch, maximal)


@dataclass
class Antwort:
    text: str = ""
    aufrufe: list[dict] = field(default_factory=list)  # [{"id","name","input"}]
    nutzung: dict = field(default_factory=dict)  # ein, aus, cache_lesen, cache_schreiben, websuchen
    ende: str = ""


def _tool_schema_anthropic(tools: list[dict]) -> list[dict]:
    return [{"name": t["name"], "description": t["beschreibung"], "input_schema": t["schema"]} for t in tools]


def _tool_schema_openai(tools: list[dict]) -> list[dict]:
    return [{"type": "function", "function": {"name": t["name"], "description": t["beschreibung"], "parameters": t["schema"]}}
            for t in tools]


class AnthropicSitzung:
    def __init__(self, modell: str, system: str | list[str], tools: list[dict], websuche: int = 0, effort: str | None = "medium",
                 max_tokens: int = 6000, key: str | None = None, timeout: float = 300):
        import anthropic
        self.client = anthropic.Anthropic(api_key=key or os.environ["ARENA_ANTHROPIC_KEY"], max_retries=4, timeout=timeout)
        if isinstance(system, list):  # [gemeinsamer Teil, Fondsteil]: Breakpoint nach dem gemeinsamen Teil → Cache über Fonds geteilt
            system = [{"type": "text", "text": t, **({"cache_control": {"type": "ephemeral"}} if i == 0 and len(system) > 1 else {})}
                      for i, t in enumerate(system) if t]
        self.modell, self.system, self.max_tokens, self.effort = modell, system, max_tokens, effort
        self.tools = _tool_schema_anthropic(tools)
        if websuche:
            self.tools.append({"type": "web_search_20250305", "name": "web_search", "max_uses": websuche})
        self.nachrichten: list[dict] = []

    def nutzer(self, text: str) -> None:
        self.nachrichten.append({"role": "user", "content": text})

    def tool_ergebnisse(self, ergebnisse: list[tuple[str, str, bool]]) -> None:
        self.nachrichten.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": i, "content": t, **({"is_error": True} if err else {})}
            for i, t, err in ergebnisse]})

    def hinweis(self, text: str) -> None:
        """Hinweis der Arena an die laufende Runde: an die letzte Nutzer-Nachricht anhängen (Verlauf bleibt append-only)."""
        letzte = self.nachrichten[-1] if self.nachrichten else None
        if letzte and letzte["role"] == "user" and isinstance(letzte["content"], list):
            letzte["content"].append({"type": "text", "text": text})
        else:
            self.nachrichten.append({"role": "user", "content": text})

    def schritt(self) -> Antwort:
        kw = dict(model=self.modell, max_tokens=self.max_tokens, system=self.system, messages=self.nachrichten,
                  cache_control={"type": "ephemeral"})
        if self.tools:
            kw["tools"] = self.tools
        if self.effort:
            kw["output_config"] = {"effort": self.effort}
        try:
            # Immer gestreamt: große max_tokens (Opus denkt immer mit) laufen sonst in HTTP-Zeitlimits.
            with self.client.messages.stream(**kw) as strom:
                r = strom.get_final_message()
        except Exception as e:
            raise LLMFehler(f"Anthropic: {e}") from e
        self.nachrichten.append({"role": "assistant", "content": r.content})  # unverändert zurückgeben
        u = r.usage
        st = getattr(u, "server_tool_use", None)
        a = Antwort(nutzung={"ein": u.input_tokens, "aus": u.output_tokens,
                             "cache_lesen": getattr(u, "cache_read_input_tokens", 0) or 0,
                             "cache_schreiben": getattr(u, "cache_creation_input_tokens", 0) or 0,
                             "websuchen": getattr(st, "web_search_requests", 0) or 0 if st else 0}, ende=r.stop_reason or "")
        for b in r.content:
            if b.type == "text":
                a.text += b.text
            elif b.type == "tool_use":
                a.aufrufe.append({"id": b.id, "name": b.name, "input": b.input})
        if r.stop_reason == "pause_turn":  # Server-Werkzeug (Websuche) wurde pausiert → einfach fortsetzen
            a.ende = "pause_turn"
        return a


class OpenAISitzung:
    VERSUCHE = 5
    SCHLAF = staticmethod(time.sleep)  # in Tests ersetzbar

    def __init__(self, url: str, key: str, modell: str, system: str, tools: list[dict], max_tokens: int = 4000,
                 alternativen: list[str] | None = None):
        self.url, self.key, self.modell, self.max_tokens = url, key, modell, max_tokens
        self.alternativen = [a for a in (alternativen or []) if a != modell]  # Ausweichmodelle bei Dauer-503/404
        self.versucht: set[str] = set()  # bei 404 schon probierte Namen (nicht erneut wählen)
        self.tools = _tool_schema_openai(tools)
        self.nachrichten: list[dict] = [{"role": "system", "content": system}]

    def nutzer(self, text: str) -> None:
        self.nachrichten.append({"role": "user", "content": text})

    def tool_ergebnisse(self, ergebnisse: list[tuple[str, str, bool]]) -> None:
        for i, t, _ in ergebnisse:
            self.nachrichten.append({"role": "tool", "tool_call_id": i, "content": t})

    def hinweis(self, text: str) -> None:
        self.nachrichten.append({"role": "user", "content": text})

    def schritt(self) -> Antwort:
        body = {"model": self.modell, "messages": self.nachrichten, "max_tokens": self.max_tokens}
        if self.tools:
            body["tools"] = self.tools
        d, letzter = None, ""
        aufloesungen = 0
        fehl_5xx = 0
        versuch = 0
        while versuch < self.VERSUCHE:
            body["model"] = self.modell
            try:
                r = requests.post(self.url, headers={"Authorization": f"Bearer {self.key}"}, json=body, timeout=150)
            except requests.RequestException as e:
                letzter = f"Netzwerk: {type(e).__name__}"
                self.SCHLAF(_warte(versuch, None, 3))
                versuch += 1
                continue
            if ist_kein_guthaben(r.status_code, r.text):
                raise KeinGuthaben(f"{self.modell}: HTTP {r.status_code} kein Guthaben/Kontingent ({r.text[:120]})")
            if r.status_code in (429, 500, 502, 503, 504, 529):
                letzter = f"HTTP {r.status_code} {r.text[:160]}"
                fehl_5xx += r.status_code != 429
                if fehl_5xx >= 2 and self.alternativen:  # Modell überlastet → auf Ausweichmodell desselben Anbieters
                    self.modell = self.alternativen.pop(0)
                    fehl_5xx = 0
                self.SCHLAF(_warte(versuch, r.headers.get("retry-after")))
                versuch += 1
                continue
            if r.status_code == 404 and aufloesungen < 4 and "model" in r.text.lower():
                aufloesungen += 1  # Modellname veraltet/gesperrt → Modellliste des Anbieters (bevorzugt Ausweichliste), bis zu 4 Kandidaten
                self.versucht.add(self.modell)
                neu = self._modell_suchen()
                if not neu:
                    neu = next((a for a in self.alternativen if a not in self.versucht), None)
                if neu and neu not in self.versucht:
                    self.modell = neu
                    continue
            if r.status_code >= 400:
                raise LLMFehler(f"{self.modell}: HTTP {r.status_code} {r.text[:200]}")
            try:
                d = r.json()
            except ValueError:
                letzter = "keine JSON-Antwort"
                versuch += 1
                continue
            break
        if not d or "choices" not in d:
            raise LLMFehler(f"{self.modell}: keine Antwort ({letzter or d})")
        msg = d["choices"][0]["message"]
        self.nachrichten.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")} | {"role": "assistant"})
        u = d.get("usage", {})
        a = Antwort(text=msg.get("content") or "", nutzung={"ein": u.get("prompt_tokens", 0), "aus": u.get("completion_tokens", 0),
                                                             "cache_lesen": 0, "cache_schreiben": 0, "websuchen": 0},
                    ende={"length": "max_tokens"}.get(d["choices"][0].get("finish_reason") or "", d["choices"][0].get("finish_reason") or ""))
        for tc in msg.get("tool_calls") or []:
            try:
                args = json.loads(tc["function"]["arguments"] or "{}")
            except json.JSONDecodeError:
                args = {}
            a.aufrufe.append({"id": tc["id"], "name": tc["function"]["name"], "input": args})
        return a


def _modell_suchen_impl(self) -> str | None:
    """Fragt die Modellliste des Anbieters (OpenAI-kompatibel) und wählt das Modell mit dem längsten gemeinsamen Präfix
    zum konfigurierten Namen, neuestes (alphabetisch größtes) zuerst; Bild-/Audio-/Embedding-Modelle ausgeschlossen."""
    try:
        d = requests.get(self.url.replace("/chat/completions", "/models"), headers={"Authorization": f"Bearer {self.key}"}, timeout=30).json()
        ids = [m["id"] for m in d.get("data", []) if not any(x in m["id"].lower() for x in ("embed", "vision", "audio", "image", "tts", "whisper", "moderation"))]
    except (requests.RequestException, ValueError, KeyError, AttributeError):
        return None
    if not ids:
        return None
    versucht = getattr(self, "versucht", set()) | {self.modell}
    for kandidat in self.alternativen:  # ein bekannter Name, den der Anbieter wirklich führt
        if kandidat in ids and kandidat not in versucht:
            return kandidat
    ids = [i for i in ids if i not in versucht]
    if not ids:
        return None

    def gemeinsam(a: str, b: str) -> int:
        n = 0
        for x, y in zip(a.lower(), b.lower()):
            if x != y:
                break
            n += 1
        return n
    ids.sort(reverse=True)
    return max(ids, key=lambda i: gemeinsam(i, self.modell))


OpenAISitzung._modell_suchen = _modell_suchen_impl


def openai_sitzung(anbieter: str, modell: str, system: str, tools: list[dict], key: str,
                   alternativen: list[str] | None = None) -> OpenAISitzung:
    url = config.load()["anbieter"][anbieter]["url"]
    return OpenAISitzung(url, key, modell, system, tools, alternativen=alternativen)


def modell_probe(anbieter: str, modell: str, key: str) -> bool:
    """Kurzer Probeaufruf mit Werkzeug: Manche Gratis-Modelle sind gelistet, aber gesperrt (403 „only available on …“)."""
    tool = [{"name": "ping", "beschreibung": "Antwortet mit pong.", "schema": {"type": "object", "properties": {}, "required": []}}]
    s = openai_sitzung(anbieter, modell, "Antworte knapp.", tool, key)
    s.VERSUCHE = 2
    s.SCHLAF = lambda x: time.sleep(min(x, 3))
    s.max_tokens = 50
    s.nutzer("Sag ok.")
    try:
        s.schritt()
        return True
    except LLMFehler:
        return False


def openrouter_gratis(n: int) -> list[str]:
    """Wählt aktuelle :free-Modelle mit Werkzeugunterstützung (öffentliche Modellliste, größter Kontext zuerst)."""
    try:
        d = requests.get("https://openrouter.ai/api/v1/models", timeout=30).json()["data"]
    except (requests.RequestException, KeyError, ValueError):
        return []
    kand = [m for m in d if m["id"].endswith(":free") and "tools" in (m.get("supported_parameters") or [])]
    # Qualität vor Kontextlänge: bevorzugte Familien (große Allzweck-Modelle mit gutem Tool-Use laut BFCL) zuerst, dann nach Kontext
    bevorzugt = config.load().get("openrouter_bevorzugt", [])
    rang = lambda m: next((i for i, b in enumerate(bevorzugt) if m["id"].startswith(b)), len(bevorzugt))  # noqa: E731
    kand.sort(key=lambda m: (rang(m), -(m.get("context_length") or 0)))
    gesehen, out = set(), []
    for m in kand:  # je Hersteller höchstens eins
        hersteller = m["id"].split("/")[0]
        if hersteller not in gesehen:
            gesehen.add(hersteller)
            out.append(m["id"])
    return out[:n]
