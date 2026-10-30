"""Routing/Umschaltung, Auslöselogik, Kennzahlen, Seitenbau, Benchmarks."""
import json

import pytest

from arena import config, entscheider, funds, metrics, site, store
from arena.agent import budget as bmod
from arena.agent import route as routemod
from arena.exchange import portfolio

T = 1_793_000_000  # 2026-10-26, vor dem Claude-Stichtag
KEYS = ["ARENA_ANTHROPIC_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "MOONSHOT_API_KEY", "GROQ_API_KEY",
        "OPENAI_API_KEY", "CEREBRAS_API_KEY", "MISTRAL_API_KEY"]


@pytest.fixture(autouse=True)
def tmpdata(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA", tmp_path)
    monkeypatch.setattr(site, "DOCS", tmp_path / "docs")
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)


CLAUDE = {"id": "claude_mittel", "name": "Claude Mittel", "typ": "claude", "risiko": "mittel"}


def test_ohne_schluessel_wartet_fonds(monkeypatch):
    bud = bmod.Budget(1.1, T)
    assert route_status(CLAUDE, bud) == "wartet auf Schlüssel"
    liga = funds.liga_fonds()[0]
    assert routemod.route(liga, bud, T)["status"] == "wartet auf Schlüssel"


def route_status(d, bud):
    return routemod.route(d, bud, T)["status"]


def test_claude_mit_schluessel_nutzt_sonnet(monkeypatch):
    monkeypatch.setenv("ARENA_ANTHROPIC_KEY", "x")
    r = routemod.route(CLAUDE, bmod.Budget(1.1, T), T)
    assert r["modell"] == "claude-sonnet-5-5" and r["triage"]


def test_tagesbudget_pausiert_nicht_umschalten(monkeypatch):
    monkeypatch.setenv("ARENA_ANTHROPIC_KEY", "x")
    bud = bmod.Budget(1.0, T)
    bud.buche("x", "claude-opus-5-5", {"aus": 700_000})
    assert "Tagesbudget" in routemod.route(CLAUDE, bud, T)["status"]


def _liga_fonds_mit_rendite(fid, rendite, start=10000.0):
    pf = portfolio.neu(fid, start)
    funds.speichere_portfolio(pf)
    store.anhaengen(f"funds/{fid}/equity.jsonl", {"t": T, "usd": start * (1 + rendite), "cash": 0, "n": 0, "gebuehren": 0})


def test_umschaltung_nach_stichtag_auf_bestes_liga_modell(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "d")
    monkeypatch.setenv("MISTRAL_API_KEY", "m")
    _liga_fonds_mit_rendite("liga_deepseek", 0.02)
    _liga_fonds_mit_rendite("liga_mistral", 0.07)
    nach_ende = 1_795_000_000  # 2026-11-18
    r = routemod.route(CLAUDE, bmod.Budget(1.1, nach_ende), nach_ende)
    assert r["anbieter"] == "mistral" and r["umgeschaltet_auf"]
    sw = store.lies_jsonl("model_switches.jsonl")
    assert len(sw) == 1 and sw[0]["fonds"] == "claude_mittel" and "14.11" in sw[0]["grund"]
    routemod.route(CLAUDE, bmod.Budget(1.1, nach_ende), nach_ende)  # kein zweiter Eintrag
    assert len(store.lies_jsonl("model_switches.jsonl")) == 1


def test_umschaltung_bei_erschoepftem_gesamtbudget(monkeypatch):
    monkeypatch.setenv("ARENA_ANTHROPIC_KEY", "x")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "d")
    _liga_fonds_mit_rendite("liga_deepseek", 0.01)
    bud = bmod.Budget(1.0, T)
    bud.z["gesamt_usd"] = 191
    r = routemod.route(CLAUDE, bud, T)
    assert r["anbieter"] == "deepseek"
    assert "Budget" in store.lies_jsonl("model_switches.jsonl")[0]["grund"]


def test_keine_umschaltung_ohne_liga_modell(monkeypatch):
    nach_ende = 1_795_000_000
    r = routemod.route(CLAUDE, bmod.Budget(1.1, nach_ende), nach_ende)
    assert "pausiert" in r["status"]


def ev(weckt=True):
    return {"weckt": weckt, "ts": T}


def test_ausloesen_regeln(monkeypatch):
    assert not entscheider.soll_ausloesen([ev()], T)  # kein Schlüssel
    monkeypatch.setenv("ARENA_ANTHROPIC_KEY", "x")
    assert not entscheider.soll_ausloesen([ev(False)], T)  # nichts Weckendes
    assert entscheider.soll_ausloesen([ev()], T)
    assert not entscheider.soll_ausloesen([ev()], T + 60)  # Abstand
    assert entscheider.soll_ausloesen([ev()], T + 3600)
    z = entscheider.zustand()
    from datetime import datetime, timezone
    z["laeufe"] = {datetime.fromtimestamp(T + 7200, timezone.utc).strftime("%Y-%m-%d"): 99}
    store.schreibe(entscheider.ZUSTAND, z)
    assert not entscheider.soll_ausloesen([ev()], T + 7200)  # Tageslimit


def test_kennzahlen_drawdown_sharpe_brier():
    assert metrics.max_drawdown([100, 120, 90, 110]) == pytest.approx(-25.0)
    assert metrics.sharpe([100, 101, 102]) is None
    assert metrics.sharpe([100 + i + (i % 2) for i in range(12)]) > 0
    pf = portfolio.neu("claude_mittel", 10000)
    funds.speichere_portfolio(pf)
    store.anhaengen("funds/claude_mittel/prognosen.jsonl", {"ts": 1, "markt_id": "pm:a:1", "p_ja": 0.9, "markt_ja_mitte": 0.6, "begruendung": ""})
    store.anhaengen("funds/claude_mittel/prognosen.jsonl", {"ts": 2, "markt_id": "pm:a:1", "p_ja": 0.1, "markt_ja_mitte": 0.6, "begruendung": ""})
    store.anhaengen("funds/claude_mittel/prognosen.jsonl", {"ts": 3, "markt_id": "pm:a:2", "p_ja": 0.5, "markt_ja_mitte": 0.5, "begruendung": ""})
    store.schreibe("resolutions.json", {"pm:a:1": {"wert": 1.0, "ts": 5}})
    b = metrics.brier("claude_mittel")
    assert b["n"] == 1 and b["brier"] == pytest.approx(0.01) and b["brier_markt"] == pytest.approx(0.16) and b["offen"] == 1


def test_seitenbau_und_status_json(monkeypatch):
    pf = portfolio.neu("claude_mittel", 11000)
    pf["start_fx"] = 1.1
    funds.speichere_portfolio(pf)
    for i in range(5):
        store.anhaengen("funds/claude_mittel/equity.jsonl", {"t": T + i * 900, "usd": 11000 + i * 10, "cash": 11000, "n": 0, "gebuehren": 0})
    store.anhaengen("events.jsonl", {"id": "e1", "ts": T, "typ": "kurssprung", "titel": "t", "weckt": True, "fonds": None})
    g = site.bauen(T + 4000)
    status = json.loads((site.DOCS / "status.json").read_text())
    assert status["rangliste"][0]["id"] == "claude_mittel" and status["rangliste"][0]["rendite_pct"] == pytest.approx(0.36, abs=0.01)
    assert status["version"] == 1 and "wartend" in status and (site.DOCS / "data.json").exists()
    assert any(f["id"] == "liga_deepseek" and f["status"] == "wartet auf Schlüssel" for f in g["fonds"])


def test_schluessel_werden_von_bom_und_umbruch_bereinigt(monkeypatch):
    import importlib

    import arena
    monkeypatch.setenv("GEMINI_API_KEY", "﻿abc123\r\n")
    importlib.reload(arena)
    import os
    assert os.environ["GEMINI_API_KEY"] == "abc123"
    assert "abc123" not in arena.schluessel_info("GEMINI_API_KEY")
    monkeypatch.setenv("ARENA_ANTHROPIC_KEY", "﻿sk-ant-api03-GEHEIMGEHEIMGEHEIM\n")
    importlib.reload(arena)
    info = arena.schluessel_info("ARENA_ANTHROPIC_KEY")
    assert "sk-ant-api03" in info and "GEHEIM" not in info
