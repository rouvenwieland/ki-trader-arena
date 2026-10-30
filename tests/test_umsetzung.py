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


# ---------------------------------------------------------------- B5/B6 Preise und Modellnamen
def test_cache_lesen_je_modell():
    from arena.agent import budget as bmod
    opus = bmod.kosten_usd("claude-opus-5-5", {"cache_lesen": 1_000_000})
    sonnet = bmod.kosten_usd("claude-sonnet-5-5", {"cache_lesen": 1_000_000})
    assert opus == pytest.approx(0.20 * bmod.SICHERHEIT) and sonnet == pytest.approx(0.20 * bmod.SICHERHEIT)


def test_modellliste_bevorzugt_bekannten_namen(monkeypatch):
    s = llm.OpenAISitzung("https://x/v1/chat/completions", "k", "kimi-k3", "sys", [], alternativen=["kimi-latest", "kimi-k2.5"])

    class R:
        def json(self):
            return {"data": [{"id": "kimi-k2.5"}, {"id": "kimi-k9-vision"}, {"id": "moonshot-v1-8k"}]}
    monkeypatch.setattr(llm.requests, "get", lambda *a, **k: R())
    assert s._modell_suchen() == "kimi-k2.5"


# ---------------------------------------------------------------- Schnelle Gewinne 1/2: Denkschulen, Diät, Pflichtfelder
def test_gemeinsamer_systemteil_fuer_cache_und_denkschulen():
    from arena import funds
    from arena.agent import prompts
    c = funds.claude_fonds()
    teile = [prompts.system_teile(d, {}) for d in c]
    assert teile[0][0] == teile[1][0] == teile[2][0]  # identischer Präfix → Cache über Fonds geteilt
    assert not any(d["name"] in teile[0][0] for d in c)
    assert "Basisraten" in teile[0][1] and "Arbitrageur" in teile[1][1] and "Momentum" in teile[2][1]


def test_ereignisse_je_fonds_anders_sortiert():
    from arena import funds
    from arena.agent import prompts
    c = {d["id"]: d for d in funds.claude_fonds()}
    ev = [{"typ": "kurssprung", "titel": "a", "ts": 1, "fonds": None}, {"typ": "fehlbewertung", "titel": "b", "ts": 1, "fonds": None},
          {"typ": "markt_schliesst", "titel": "c", "ts": 1, "fonds": None}]
    assert prompts.ereignisse_sortiert(c["claude_aggressiv"], ev)[0]["typ"] == "kurssprung"
    assert prompts.ereignisse_sortiert(c["claude_mittel"], ev)[0]["typ"] == "fehlbewertung"
    assert prompts.ereignisse_sortiert(c["claude_vorsichtig"], ev)[0]["typ"] == "markt_schliesst"
    assert "RECHERCHEPLAN" in prompts.runde_prompt(c["claude_mittel"], "Ereignis", ev, "", JETZT, plan=["Regeln lesen"])


def _ctx():
    from arena import funds
    from arena.agent.tools import Kontext
    from arena.exchange import portfolio

    class MZ:
        def buch(self, inst):
            from arena.exchange.book import Book
            return Book([(0.39, 1000)], [(0.41, 1000)]), None

        def marke(self, inst):
            return {"bid": 0.39, "ask": 0.41, "mark": 0.4}
    snap = {"ts": JETZT, "wetten": [], "pm_index": {"pm:polymarket:9": {"mid": "pm:polymarket:9", "venue": "polymarket", "frage": "Will it rain in NYC?",
                                                                    "ja_bid": 0.39, "ja_ask": 0.41, "schliesst": JETZT + 86400, "ref": {}}}}
    pf = portfolio.neu("claude_mittel", 10000)
    return Kontext(funds.claude_fonds()[1], pf, snap, MZ(), "t", [], JETZT)


def test_wahrscheinlichkeit_pflichtfelder_und_kohaerenz():
    from arena import store
    ctx = _ctx()
    assert "Pflichtfelder fehlen" in ctx.t_wahrscheinlichkeit("pm:polymarket:9", p_ja=0.5)
    voll = dict(markt_id="pm:polymarket:9", p_blind=0.5, basisrate="Regen an ~30 % der Tage", abrechnung="NWS CLI 1.11.",
                status_quo="trocken", gegenargument="Front kommt früher", begruendung="Ensemble 45 %")
    assert "Inkohärent" in ctx.t_wahrscheinlichkeit(p_ja=0.7, p_nein=0.6, **voll)
    r = ctx.t_wahrscheinlichkeit(p_ja=0.45, p_nein=0.55, **voll)
    assert "gespeichert" in r and "+5 pp" in r
    e = store.lies_jsonl("funds/claude_mittel/prognosen.jsonl")[-1]
    assert e["p_blind"] == 0.5 and e["markt_ja_mitte"] == pytest.approx(0.40) and e["schliesst"] == JETZT + 86400


def test_order_kaufen_braucht_pflichtfelder_und_zuversicht():
    ctx = _ctx()
    basis = dict(instrument_id="pm:polymarket:9:JA", aktion="kaufen", begruendung="x" * 60, betrag_usd=100, ausstiegsplan="bis Abrechnung halten")
    assert "Pflichtfelder beim Kaufen" in ctx.t_order(zuversicht=0.7, **basis)
    voll = basis | dict(invalidierung="Ensemble fällt unter 30 %", staerkstes_gegenargument="Markt hat Lokalwissen", risiko_usd=100)
    assert "kein Vorteil" in ctx.t_order(zuversicht=0.3, **voll)
    assert "wahrscheinlichkeit_ja" in ctx.t_order(zuversicht=0.7, **voll)


# ---------------------------------------------------------------- Policy-Gate, Risikoschicht
def test_policy_gate_sperrt_nach_fuenf_verlusten_und_nur_review_lockert():
    from arena import policy, store
    for i in range(5):
        store.anhaengen("funds/claude_mittel/ledger.jsonl", {"aktion": "geschlossen", "netto_pnl": -10.0, "kategorie": "wette:sport:JA"})
    store.anhaengen("funds/claude_mittel/ledger.jsonl", {"aktion": "geschlossen", "netto_pnl": 30.0, "kategorie": "wette:wetter:JA"})
    assert policy.aktualisiere("claude_mittel", JETZT) == ["wette:sport:JA"]
    inst = {"id": "pm:polymarket:1:JA", "art": "pm", "ergebnis": "JA", "frage": "NBA: Lakers vs Celtics"}
    assert policy.gesperrt("claude_mittel", inst) == "wette:sport:JA"
    assert policy.aktualisiere("claude_mittel", JETZT) == []  # bleibt gesperrt, keine Doppelung
    assert policy.freigeben("claude_mittel", "wette:sport:JA", "Regelauslegung korrigiert")
    assert policy.gesperrt("claude_mittel", inst) is None and policy.aktualisiere("claude_mittel", JETZT) == []


def test_kelly_einzeln_und_simultan():
    from arena import risikoschicht as rs
    assert rs.kelly_binaer(0.6, 0.5) == pytest.approx(0.2)
    assert rs.kelly_binaer(0.4, 0.5) == 0.0
    einzel = rs.kelly_binaer(0.6, 0.5)
    sim = rs.kelly_simultan((0.6, 0.5), [(0.6, 0.5, 0.2), (0.6, 0.5, 0.2)])
    assert 0 < sim < einzel  # mit offenen Wetten weniger als Einzel-Kelly


def test_themen_und_krypto_cluster_limit():
    from arena import themen
    from arena.exchange import risk
    assert themen.thema({"art": "pm", "frage": "Will the highest temperature in NYC be 60°F or higher?"}) == "wetter"
    assert themen.thema({"art": "pm", "frage": "Will Bitcoin reach $100k?"}) == "krypto"
    prof = dict(risk.profil("vorsichtig"))
    pf = {"cash": 10000, "positionen": [{"inst": {"id": "spot:BTC-USD", "art": "spot"}, "einstand": 100.0, "menge": 20.0, "marge": 0}]}
    grund = risk.pruefe_eroeffnung(pf, prof, {"id": "spot:ETH-USD", "art": "spot"}, 900, 1, 10000)
    assert grund and "Krypto-Cluster" in grund


# ---------------------------------------------------------------- Statistik und marktrelative Kennzahlen
def test_statistik_grundfunktionen():
    import random

    from arena import statistik as st
    rng = random.Random(7)
    r = [rng.gauss(0.002, 0.01) for _ in range(400)]
    assert st.psr(r) > 0.9 and st.min_trl(r) is not None
    lo, hi = st.bootstrap_ki(r, st.mittel)
    assert lo < st.mittel(r) < hi
    assert st.p_wert_mehr(r) < 0.05 and st.p_wert_mehr([-x for x in r]) > 0.5
    assert st.sr0_erwartet_max(0.01, 12) > 0


def test_brier_skill_gegen_markt_und_filter_nach_ereignis():
    from arena import metrics, store
    store.schreibe("resolutions.json", {"pm:a": {"wert": 1.0, "ts": JETZT}, "pm:b": {"wert": 0.0, "ts": JETZT}, "pm:c": {"wert": 1.0, "ts": JETZT}})
    for mid, p, m, ts in (("pm:a", 0.9, 0.7, JETZT - 100), ("pm:b", 0.2, 0.3, JETZT - 100), ("pm:c", 0.99, 0.5, JETZT + 10)):
        store.anhaengen("funds/claude_mittel/prognosen.jsonl", {"ts": ts, "markt_id": mid, "p_ja": p, "markt_ja_mitte": m})
    k = metrics.brier("claude_mittel")
    assert k["n"] == 2  # pm:c nach der Auflösung abgegeben → zählt nicht
    assert k["brier"] == pytest.approx((0.01 + 0.04) / 2) and k["brier_markt"] == pytest.approx((0.09 + 0.09) / 2)
    assert k["brier_skill_markt"] > 0 and k["marktbereinigt"] < 0 and k["gewinn_je_kontrakt"] == pytest.approx(0.3)


# ---------------------------------------------------------------- Schwarm und Kontrollfonds
class BuchMZ:
    def __init__(self, ja_ask=0.40, nein_ask=0.62):
        self.ja_ask, self.nein_ask = ja_ask, nein_ask

    def buch(self, inst):
        from arena.exchange.book import Book
        a = self.ja_ask if inst["ergebnis"] == "JA" else self.nein_ask
        return Book([(a - 0.02, 5000)], [(a, 5000)]), None

    def marke(self, inst):
        return {"bid": 0.38, "ask": 0.40, "mark": 0.39}


def _stimmen(werte, mid="pm:kalshi:WETTER-1", ts=JETZT - 600):
    from arena import store
    for fid, p in zip(["claude_vorsichtig", "claude_mittel", "claude_aggressiv", "liga_gemini"], werte):
        store.anhaengen(f"funds/{fid}/prognosen.jsonl", {"ts": ts, "markt_id": mid, "p_ja": p, "markt_ja_mitte": 0.39})


def test_schwarm_mischung_und_kauf():
    from arena import funds, schwarm, store
    from arena.exchange import portfolio
    assert schwarm.mische(0.8, 0.5) == pytest.approx(schwarm.sigmoid(0.3 * schwarm.logit(0.8)))
    assert schwarm.getrimmt([(0.1, 1), (0.5, 1), (0.6, 1), (0.7, 1), (0.99, 1)]) == pytest.approx(0.6)
    _stimmen([0.9, 0.85, 0.95, 0.9])
    m = {"mid": "pm:kalshi:WETTER-1", "venue": "kalshi", "frage": "NYC high above 60°F?", "ja_bid": 0.38, "ja_ask": 0.40,
         "schliesst": JETZT + 86400, "ref": {"ticker": "WETTER-1"}}
    d = funds.SCHWARM[1]
    pf = portfolio.neu(d["id"], 10000)
    log = schwarm.schritt_schwarm(d, pf, BuchMZ(), JETZT, {m["mid"]: m})
    p = store.lies_jsonl(f"funds/{d['id']}/prognosen.jsonl")[0]
    assert 0.39 < p["p_ja"] < p["p_llm"] and p["stimmen"] == 3  # nur Claude-Stimmen, zum Markt hin gemischt
    assert log and log[0]["ok"] and log[0]["inst_id"].endswith(":JA") and log[0]["nominal"] <= 0.05 * 10000 + 1
    assert not schwarm.schritt_schwarm(d, pf, BuchMZ(), JETZT + 900, {m["mid"]: m})  # schon gehalten → kein zweiter Kauf


def test_schwarm_handelt_nicht_ohne_vorteil_nach_kosten():
    from arena import funds, schwarm
    from arena.exchange import portfolio
    _stimmen([0.45, 0.42, 0.44])
    m = {"mid": "pm:kalshi:WETTER-1", "venue": "kalshi", "frage": "x", "ja_bid": 0.38, "ja_ask": 0.40, "schliesst": JETZT + 86400, "ref": {}}
    pf = portfolio.neu("schwarm_alle", 10000)
    assert not schwarm.schritt_schwarm(funds.SCHWARM[0], pf, BuchMZ(), JETZT, {m["mid"]: m})


def test_kontrollen_markt_kopierer_und_immer_nein():
    from arena import funds, metrics, schwarm, store
    from arena.exchange import portfolio
    _stimmen([0.9, 0.8, 0.7])
    m = {"mid": "pm:kalshi:WETTER-1", "venue": "kalshi", "frage": "x", "ja_bid": 0.38, "ja_ask": 0.40, "schliesst": JETZT + 86400, "ref": {}}
    ko_markt, ko_nein = funds.KONTROLLEN
    pf = portfolio.neu("ko_markt", 10000)
    assert schwarm.schritt_kontrolle(ko_markt, pf, BuchMZ(), JETZT, {m["mid"]: m}) == []
    e = store.lies_jsonl("funds/ko_markt/prognosen.jsonl")
    assert len(e) == 1 and e[0]["p_ja"] == 0.39 and e[0]["ts"] == JETZT - 600
    schwarm.schritt_kontrolle(ko_markt, pf, BuchMZ(), JETZT + 900, {m["mid"]: m})
    assert len(store.lies_jsonl("funds/ko_markt/prognosen.jsonl")) == 1  # nicht doppelt
    store.schreibe("resolutions.json", {m["mid"]: {"wert": 1.0, "ts": JETZT + 1000}})
    assert metrics.brier("ko_markt")["marktbereinigt"] == 0.0
    pf2 = portfolio.neu("ko_nein", 10000)
    log = schwarm.schritt_kontrolle(ko_nein, pf2, BuchMZ(), JETZT, {m["mid"]: m})
    assert log[0]["ok"] and log[0]["inst_id"].endswith(":NEIN")


# ---------------------------------------------------------------- Reflexion und geschichtetes Notizbuch
def test_notizbuch_waehlt_nach_wichtigkeit_und_zerfall():
    from arena import notizbuch
    alt = JETZT - 30 * 86400
    notizbuch.schreibe("claude_mittel", "beobachtung", "Alte Beobachtung zu Tennis", ts=alt)
    notizbuch.schreibe("claude_mittel", "lektion", "Lektion: Abrechnungsregeln wörtlich lesen", ts=alt)
    notizbuch.schreibe("claude_mittel", "these", "Abgelaufene These", ts=JETZT - 3600, gueltig_tage=0.01)
    for i in range(5):
        notizbuch.schreibe("claude_mittel", "beobachtung", f"Frische Beobachtung {i}", ts=JETZT - 60)
    gew = [e["text"] for e in notizbuch.auswahl("claude_mittel", 3, jetzt=JETZT)]
    assert "Lektion: Abrechnungsregeln wörtlich lesen" in gew and "Abgelaufene These" not in gew and "Alte Beobachtung zu Tennis" not in gew
    mit_bezug = [e["text"] for e in notizbuch.auswahl("claude_mittel", 2, kontext_text="Tennis Beobachtung Basel", jetzt=JETZT)]
    assert "Alte Beobachtung zu Tennis" in mit_bezug


def test_reflexion_schreibt_lektion_und_aktualisiert_policy(monkeypatch):
    from arena import notizbuch, reflexion, store
    reflexion.lauf(None, JETZT)  # erster Lauf: Stand merken
    for i in range(5):
        store.anhaengen("funds/claude_mittel/ledger.jsonl", {"aktion": "geschlossen", "ts": JETZT + i, "position_id": f"p{i}", "inst_id": "pm:kalshi:X:JA",
                                                            "netto_pnl": -5.0, "kategorie": "wette:sport:JA", "grund": "Abrechnung", "eroeffnet": JETZT - 3600})
    assert reflexion.lauf(None, JETZT + 10) == 5
    lekt = [e for e in notizbuch.lies("claude_mittel") if e.get("quelle") == "reflexion"]
    assert len(lekt) == 5 and lekt[0]["wichtigkeit"] == 7 and "Verlust" in lekt[0]["text"]
    assert store.lies("funds/claude_mittel/policy.json")["gesperrt"]["wette:sport:JA"]
    assert reflexion.lauf(None, JETZT + 20) == 0
