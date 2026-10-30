"""Agentenschleife mit gefälschtem Modell: Entscheidungs-Zeitstempel vor Ergebnis, Budget-Stopp, Orders, Limits."""
import pytest

from arena import config, funds, store
from arena.agent import budget as bmod
from arena.agent import llm, loop
from arena.agent.tools import Kontext
from arena.exchange import portfolio
from arena.exchange.book import Book

DEFN = {"id": "claude_mittel", "name": "Claude Mittel", "typ": "claude", "risiko": "mittel", "persoenlichkeit": "x"}


@pytest.fixture(autouse=True)
def tmpdata(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA", tmp_path)


class FakeMZ:
    def __init__(self):
        self.fehler = []

    def buch(self, inst):
        return Book([(99.0, 1e6)], [(100.0, 1e6)], 0, mark=99.5), None

    def marke(self, inst):
        return {"bid": 99.0, "ask": 100.0, "mark": 99.5}


class FakeSitzung:
    """Skript: Liste von Antworten."""
    def __init__(self, antworten):
        self.antworten = list(antworten)
        self.nachrichten = []

    def nutzer(self, t):
        self.nachrichten.append(t)

    def tool_ergebnisse(self, e):
        self.nachrichten.append(e)

    def schritt(self):
        return self.antworten.pop(0)


def snap():
    return {"ts": 1.0, "fx": 1.1, "krypto": {}, "perps": {}, "aktien": {}, "optionen": [], "wetten": [], "pm_index": {}, "nachrichten": [], "verlauf": {}}


def A(text="", aufrufe=None, ende="end_turn", aus=100):
    return llm.Antwort(text=text, aufrufe=aufrufe or [], nutzung={"ein": 1000, "aus": aus, "cache_lesen": 0, "cache_schreiben": 0, "websuchen": 0}, ende=ende)


def test_runde_mit_order_speichert_entscheidung_vor_ergebnis(monkeypatch):
    pf = portfolio.neu("claude_mittel", 10000)
    funds.speichere_portfolio(pf)
    monkeypatch.setattr(Kontext, "aufloesen", lambda self, iid: {"id": iid, "art": "spot", "venue": "coinbase", "symbol": "BTC-USD"})
    order = {"instrument_id": "spot:BTC-USD", "aktion": "kaufen", "betrag_usd": 1000, "zuversicht": 0.6,
             "begruendung": "These: Momentum. Gegenargument: Funding hoch. Kosten 1,2 % Rundreise, Edge größer.",
             "ausstiegsplan": "Stop 95, Ziel 110 oder in 7 Tagen raus"}
    fabrik = lambda sp, tools: FakeSitzung([A("", [{"id": "1", "name": "portfolio", "input": {}}], "tool_use"),
                                            A("", [{"id": "2", "name": "order", "input": order}], "tool_use"),
                                            A("Tagebuch: gekauft.")])
    bud = bmod.Budget(1.1, jetzt=1_800_000_000)
    res = loop.laufe_runde(DEFN, {"art": "anthropic", "modell": "claude-sonnet-5-5"}, pf, snap(), FakeMZ(), "Test", [], bud, 3,
                           jetzt=1_800_000_000, sitzung_fabrik=fabrik)
    assert res["orders"] == 1 and res["text"].startswith("Tagebuch") and res["kosten_usd"] > 0
    dec = store.lies_jsonl("funds/claude_mittel/decisions.jsonl")
    led = store.lies_jsonl("funds/claude_mittel/ledger.jsonl")
    o = next(d for d in dec if d["typ"] == "order")
    assert o["ts"] <= led[0]["ts"] and led[0]["entscheidung_id"] == o["id"] and led[0]["ok"]
    assert len(pf["positionen"]) == 1 and pf["positionen"][0]["ausstiegsplan"].startswith("Stop")


def test_order_ohne_begruendung_oder_ausstieg_abgelehnt():
    pf = portfolio.neu("claude_mittel", 10000)
    ctx = Kontext(DEFN, pf, snap(), FakeMZ(), "t", [])
    assert "Begründung zu kurz" in ctx.t_order("spot:BTC-USD", "kaufen", "kurz", 0.5, betrag_usd=100)
    assert "Ausstiegsplan" in ctx.t_order("spot:BTC-USD", "kaufen", "x" * 60, 0.5, betrag_usd=100)
    assert not pf["positionen"]


def test_budget_stopp_beendet_runde():
    pf = portfolio.neu("claude_mittel", 10000)
    bud = bmod.Budget(1.0, jetzt=1_800_000_000)
    bud.buche("claude_mittel", "claude-opus-5-5", {"aus": 600_000})  # Tagesdeckel (12) überschritten
    fabrik = lambda sp, tools: FakeSitzung([A("sollte nie laufen")])
    res = loop.laufe_runde(DEFN, {"art": "anthropic", "modell": "claude-sonnet-5-5"}, pf, snap(), FakeMZ(), "Test", [], bud, 3,
                           jetzt=1_800_000_000, sitzung_fabrik=fabrik)
    assert res["schritte"] == 0 and "Budget-Stopp" in res["abbruch"]


def test_limit_wird_von_der_boerse_durchgesetzt(monkeypatch):
    pf = portfolio.neu("claude_mittel", 10000)
    funds.speichere_portfolio(pf)
    monkeypatch.setattr(Kontext, "aufloesen", lambda self, iid: {"id": iid, "art": "spot", "venue": "coinbase", "symbol": "BTC-USD"})
    ctx = Kontext(DEFN, pf, snap(), FakeMZ(), "t", [])
    r = ctx.t_order("spot:BTC-USD", "kaufen", "x" * 60, 0.9, betrag_usd=5000, ausstiegsplan="Stop bei 90, Ziel 120")
    assert '"ok": false' in r and "Einzelposition" in r and not pf["positionen"]


def test_unbekanntes_werkzeug_und_fehler_brechen_nicht():
    pf = portfolio.neu("claude_mittel", 10000)
    ctx = Kontext(DEFN, pf, snap(), FakeMZ(), "t", [])
    out, err = ctx.fuehre_aus("gibtsnicht", {})
    assert err
    out, err = ctx.fuehre_aus("order", {"nur": "unsinn"})
    assert err


def test_modellfehler_wird_aufgefangen():
    pf = portfolio.neu("claude_mittel", 10000)

    class Kaputt(FakeSitzung):
        def schritt(self):
            raise llm.LLMFehler("boom")
    res = loop.laufe_runde(DEFN, {"art": "openai", "modell": "x"}, pf, snap(), FakeMZ(), "Test", [], None, 3,
                           jetzt=1_800_000_000, sitzung_fabrik=lambda s, t: Kaputt([]))
    assert "Modellfehler" in res["abbruch"]
