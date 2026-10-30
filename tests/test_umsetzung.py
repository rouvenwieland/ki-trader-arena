"""Umsetzung research/EMPFEHLUNG.md (31.10.): Abschnitt 0 (B1–B6) und Folgendes."""
import pytest

from arena import config, review, site, takt
from arena.agent import llm
from arena.exchange import fees

JETZT = 1_793_350_000  # 2026-10-30 08:46 UTC (Freitag)


@pytest.fixture(autouse=True)
def tmpdata(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA", tmp_path)
    monkeypatch.setattr(site, "DOCS", tmp_path / "docs")
    monkeypatch.setattr(config, "ROOT", tmp_path)
    for k in ["ARENA_ANTHROPIC_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY", "DEEPSEEK_API_KEY"]:
        monkeypatch.delenv(k, raising=False)


# ---------------------------------------------------------------- B1 Polymarket-Gebühr
def poly(rate, exp=1):
    return {"id": "pm:polymarket:1:JA", "art": "pm", "venue": "polymarket", "ergebnis": "JA",
            "ref": {"gebuehr_rate": rate, "gebuehr_exp": exp}}


def test_polymarket_gebuehr_doku_beispiel():
    # Doku: 100 Anteile zu 0,50 $ in Krypto (Rate 0,07) kosten 1,75 $
    assert fees.gebuehr(poly(0.07), 0.50, 100) == pytest.approx(1.75)
    assert fees.gebuehr(poly(0.0), 0.50, 100) == 0.0  # Geopolitik
    assert fees.gebuehr(poly(0.05), 0.9, 10) == pytest.approx(round(10 * 0.05 * 0.09, 5))
    alt = {"id": "pm:polymarket:2:JA", "art": "pm", "venue": "polymarket", "ergebnis": "JA", "ref": {}}
    assert fees.gebuehr(alt, 0.5, 100) == 0.0  # Altposition ohne feeSchedule: konfigurierter Standard (0)


def test_polymarket_markt_speichert_rate_und_exponent():
    from arena.data import pm
    m = pm._norm_poly({"id": "1", "question": "Q?", "clobTokenIds": '["a","b"]', "outcomes": '["Yes","No"]', "enableOrderBook": True,
                       "bestBid": "0.4", "bestAsk": "0.42", "feesEnabled": True,
                       "feeSchedule": {"rate": 0.05, "exponent": 1, "takerOnly": True}})
    assert m["ref"]["gebuehr_rate"] == 0.05 and m["ref"]["gebuehr_exp"] == 1
    m = pm._norm_poly({"id": "1", "question": "Q?", "clobTokenIds": '["a","b"]', "outcomes": '["Yes","No"]', "enableOrderBook": True,
                       "bestBid": "0.4", "bestAsk": "0.42", "feesEnabled": False, "feeSchedule": {"rate": 0.05}})
    assert m["ref"]["gebuehr_rate"] == 0.0


# ---------------------------------------------------------------- B2 Review abgeschnitten
class FakeSitzung:
    ende = "max_tokens"
    text = "Halber Satz (0"

    def __init__(self, *a, **k):
        FakeSitzung.max_tokens = k.get("max_tokens")

    def nutzer(self, t):
        pass

    def schritt(self):
        return llm.Antwort(text=self.text, nutzung={"ein": 100, "aus": 32000}, ende=self.ende)


def test_review_abgeschnitten_wird_nicht_verwendet(monkeypatch):
    monkeypatch.setenv("ARENA_ANTHROPIC_KEY", "x")
    monkeypatch.setattr(llm, "AnthropicSitzung", FakeSitzung)
    assert review.lauf(JETZT) is None
    assert FakeSitzung.max_tokens >= 32000
    berichte = config.ROOT / "reports"
    assert (berichte / "2026-W44-abgeschnitten.md").exists() and not (berichte / "2026-W44.md").exists()
    # der Taktgeber holt das Review dieser Woche einmal nach (auch werktags)
    assert "review" in takt.aufgaben(JETZT)
    assert "review" not in takt.aufgaben(JETZT + 900)


def test_review_vollstaendig_schreibt_regeln(monkeypatch):
    monkeypatch.setenv("ARENA_ANTHROPIC_KEY", "x")
    FakeSitzung.ende = "end_turn"
    FakeSitzung.text = 'Gut.\n```json\n{"regeln": {"claude_mittel": ["Nie mehr als 5 % je Wette"]}}\n```'
    monkeypatch.setattr(llm, "AnthropicSitzung", FakeSitzung)
    try:
        assert review.lauf(JETZT)
    finally:
        FakeSitzung.ende, FakeSitzung.text = "max_tokens", "Halber Satz (0"
    from arena import notizbuch
    assert any("5 %" in e["text"] for e in notizbuch.lies("claude_mittel"))


# ---------------------------------------------------------------- B3 / GARCH-Basislinie und Trefferbilanz
def test_garch_band_kalibriert_auf_simulation():
    import math
    import random

    from arena import forecast
    rng = random.Random(1)
    p, treffer, n = [100.0], 0, 0
    for _ in range(1200):
        p.append(p[-1] * math.exp(rng.gauss(0, 0.01)))
    for i in range(300, 1150, 10):
        b = forecast.garch_band(p[:i], 24)
        n += 1
        treffer += b["p10"] <= p[i + 23] <= b["p90"]
        assert b["median"] == p[i - 1]
    assert 0.65 <= treffer / n <= 0.95  # Soll ≈ 80 %


def test_trefferbilanz_aus_log(monkeypatch):
    from arena import forecast, store
    t0 = JETZT - 30 * 3600
    store.anhaengen(forecast.LOG, {"ts": t0, "iid": "spot:BTC-USD", "modell": "garch", "h": 24, "letzter": 100.0,
                                   "median": 100.0, "p10": 95.0, "p90": 105.0})
    store.anhaengen(forecast.LOG, {"ts": t0, "iid": "spot:BTC-USD", "modell": "kronos", "h": 24, "letzter": 100.0,
                                   "median": 101.0, "p10": None, "p90": None})
    from arena import verlauf
    verlauf.tick_anhaengen(t0 + 24 * 3600 + 60, {"spot:BTC-USD": 103.0})
    b = forecast.bilanz(JETZT)
    assert b["garch"]["n"] == 1 and b["garch"]["abdeckung_pct"] == 100.0
    assert b["kronos"]["abdeckung_pct"] is None and b["kronos"]["median_fehler_pct"] == pytest.approx(2.0)


# ---------------------------------------------------------------- B4 Zeitstempel
def test_zeitstempel_atom_und_gdelt():
    from arena.data import news
    assert news._iso("20261030T153000Z") == pytest.approx(1793374200.0)
    assert news._iso("2026-10-30T15:30:00+00:00") == pytest.approx(1793374200.0)
    assert news._iso("kaputt") == 0.0 and news._iso(None) == 0.0
    assert "Fed Presse" in news.RSS and "SEC Presse" in news.RSS
