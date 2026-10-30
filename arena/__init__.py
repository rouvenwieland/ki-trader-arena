"""KI-Trader-Arena: Papierhandel-Experiment (nur Simulation)."""
import os

# Schlüssel aus GitHub-Secrets können ein BOM (U+FEFF) und Zeilenumbrüche enthalten, wenn sie unter Windows/PowerShell
# gesetzt wurden. Beim Import einmal bereinigen – so sehen alle Module saubere Werte.
_SCHLUESSEL = ["ARENA_ANTHROPIC_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "MOONSHOT_API_KEY",
               "GROQ_API_KEY", "OPENAI_API_KEY", "CEREBRAS_API_KEY", "MISTRAL_API_KEY", "NASA_FIRMS_KEY", "FRED_API_KEY"]
for _k in _SCHLUESSEL:
    _v = os.environ.get(_k)
    if _v:
        _c = "".join(ch for ch in _v if ch.isprintable() and ch not in "﻿​").strip()
        if _c != _v:
            os.environ[_k] = _c


def schluessel_info(name: str) -> str:
    """Unkritische Diagnose zu einem Schlüssel (nie der Wert): Format-Präfix und Länge."""
    v = os.environ.get(name, "")
    if not v:
        return "nicht gesetzt"
    prefix = v[:12] if v.startswith("sk-ant-") else v[:3] + "…"
    return f"Präfix {prefix}, Länge {len(v)}"
