"""Server-Faehigkeit (13.11.2026): schluessel(name), fehlender Schluessel -> uebersprungen, Brier je Agent."""
import json

import pytest

import arena
from arena import auswertung, config, funds, metrics, store


@pytest.fixture(autouse=True)
def tmpdata(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA", tmp_path / "data")
    monkeypatch.setattr(config, "ROOT", tmp_path)
    monkeypatch.delenv("CREDENTIALS_DIRECTORY", raising=False)
    for k in ["ARENA_ANTHROPIC_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY"]:
        monkeypatch.delenv(k, raising=False)


def test_schluessel_credential_datei_vor_env(tmp_path, monkeypatch):
    (tmp_path / "openrouter").write_text("﻿sk-test-platzhalter\n")
    monkeypatch.setenv("CREDENTIALS_DIRECTORY", str(tmp_path))
    monkeypatch.setenv("OPENROUTER_API_KEY", "aus-env")
    assert arena.schluessel("OPENROUTER_API_KEY") == "sk-test-platzhalter"
    assert arena.schluessel("ARENA_ANTHROPIC_KEY") == ""  # Datei fehlt, Env leer


def test_schluessel_env_und_fehlend(monkeypatch):
    assert arena.schluessel("OPENROUTER_API_KEY") == ""
    monkeypatch.setenv("OPENROUTER_API_KEY", " x \n")
    assert arena.schluessel("OPENROUTER_API_KEY") == "x"


def test_fehlender_schluessel_ueberspringt_liga_fonds_ohne_abbruch(monkeypatch):
    liga = [d for d in funds.alle_definitionen() if d["typ"] == "liga"]
    assert liga
    assert all(not funds.liga_hat_schluessel(d) for d in liga)  # ohne Schluessel: alle uebersprungen, keine Ausnahme
    d = liga[0]
    monkeypatch.setenv(d["schluessel"], "x")
    assert funds.liga_hat_schluessel(d)


def test_brier_von_hand_gerechnet():
    # (0.9-1)^2 = 0.01 ; (0.2-0)^2 = 0.04 ; (0.5-1)^2 = 0.25  -> Mittel 0.3/3 = 0.1
    assert auswertung.brier_score([0.9, 0.2, 0.5], [1, 0, 1]) == pytest.approx(0.1)
    assert auswertung.brier_score([], []) is None


def test_brier_je_agent_report(monkeypatch):
    fid = "claude_test"
    monkeypatch.setattr(funds, "alle_definitionen", lambda: [{"id": fid, "name": "Test-Agent", "typ": "claude"}])
    store.schreibe("resolutions.json", {"m1": {"wert": 1, "ts": 2e9}, "m2": {"wert": 0, "ts": 2e9}, "m3": {"wert": 1, "ts": 2e9}})
    for mid, p in [("m1", 0.9), ("m2", 0.2), ("m3", 0.5)]:
        store.anhaengen(f"funds/{fid}/prognosen.jsonl", {"markt_id": mid, "p_ja": p, "ts": 1e9, "markt_ja_mitte": None})
    z = auswertung.tabelle()
    assert z[0]["fonds"] == fid and z[0]["n"] == 3 and z[0]["brier"] == pytest.approx(0.1)
    name = auswertung.lauf(1_793_350_000)
    md = (config.ROOT / "reports" / f"brier-{name}.md").read_text(encoding="utf-8")
    assert "Test-Agent" in md and "0.100" in md
    assert json.loads((config.ROOT / "reports" / f"brier-{name}.json").read_text())[0]["n"] == 3
