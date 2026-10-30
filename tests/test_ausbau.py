"""Ausbau 30.10.: Budget-Takt, Rundenbudget, Liga-Fehlerbehandlung, Unabhängigkeit der Fonds, Überlappung, Taktgeber."""
import json

import pytest

from arena import config, entscheider, funds, site, snapshot, store, takt
from arena.agent import budget as bmod
from arena.agent import llm, loop
from arena.agent import route as routemod
from arena.exchange import portfolio

T = 1_793_000_000  # 2026-10-26 07:33 UTC
JETZT = 1_793_350_000  # 2026-10-30 08:46 UTC


@pytest.fixture(autouse=True)
def tmpdata(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA", tmp_path)
    monkeypatch.setattr(site, "DOCS", tmp_path / "docs")
    monkeypatch.setattr(config, "ROOT", tmp_path)
    for k in ["ARENA_ANTHROPIC_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY"]:
        monkeypatch.delenv(k, raising=False)


# ---------------------------------------------------------------- Budget
def test_fonds_tagesanteil_aus_config_und_tempo():
    b = bmod.Budget(1.0, JETZT)  # 190 € für ~15 Tage reichen für die vollen Anteile
    anteil = config.load()["budget"]["fonds_tagesanteil_eur"]["claude_aggressiv"]
    assert b.tempo_faktor() == 1.0
    assert b.fonds_anteil_usd(3, "claude_aggressiv") == pytest.approx(anteil)
    assert bmod.Budget(1.0, T).tempo_faktor() < 1.0  # 19 Tage vor Stichtag: 10 €/Tag < Summe der Anteile
    b.z["gesamt_usd"] = 185.0  # kaum Rest bis zum Stichtag → Anteile werden gestreckt
    assert b.tempo_faktor() < 0.1 and b.fonds_anteil_usd(3, "claude_aggressiv") < anteil * 0.1


def test_rundenbudget_verteilt_rest_auf_kommende_runden():
    b = bmod.Budget(1.0, JETZT)
    frueh = b.runden_budget_usd("claude_mittel", "claude-sonnet-5-5", "takt", 1)
    spaet = b.runden_budget_usd("claude_mittel", "claude-sonnet-5-5", "takt", 21)
    tief = b.runden_budget_usd("claude_mittel", "claude-opus-5-5", "tief", 13)
    assert 0 < frueh < spaet <= config.load()["budget"]["runden_deckel_usd"]["claude-sonnet-5-5"]
    assert tief > frueh
    b.buche("claude_mittel", "claude-sonnet-5-5", {"aus": 1_000_000})  # Anteil verbraucht
    assert b.runden_budget_usd("claude_mittel", "claude-sonnet-5-5", "takt", 21) == 0


def test_reservierung_haelt_globalen_deckel_bei_parallelen_fonds():
    b = bmod.Budget(1.0, T)
    b.z["tage"][b.tag] = 11.0
    assert b.reserviere("claude_mittel", 3, 0.6)[0]
    import threading
    erg = []
    t = threading.Thread(target=lambda: erg.append(b.reserviere("claude_vorsichtig", 3, 0.6)))
    t.start(); t.join()
    assert erg[0] == (False, "Tagesbudget erschöpft")  # 11 + 0,6 reserviert + 0,6 > 12
    b.freigeben()
    assert b.darf("claude_vorsichtig", 3, 0.6)[0]


# ---------------------------------------------------------------- Liga-Fehler
class R:
    def __init__(self, code, text="", headers=None, js=None):
        self.status_code, self.text, self.headers, self._js = code, text, headers or {}, js

    def json(self):
        return self._js


def ok_antwort():
    return R(200, "{}", js={"choices": [{"message": {"role": "assistant", "content": "fertig"}, "finish_reason": "stop"}],
                            "usage": {"prompt_tokens": 5, "completion_tokens": 2}})


def test_kein_guthaben_wird_erkannt_und_nicht_wiederholt(monkeypatch):
    aufrufe = []
    monkeypatch.setattr(llm.requests, "post", lambda *a, **k: aufrufe.append(1) or R(429, '{"error":{"message":"You have no credits remaining.","code":"insufficient_quota"}}'))
    s = llm.OpenAISitzung("u", "k", "gpt-5-mini", "sys", [])
    s.SCHLAF = lambda x: None
    s.nutzer("hi")
    with pytest.raises(llm.KeinGuthaben):
        s.schritt()
    assert len(aufrufe) == 1
    assert not llm.ist_kein_guthaben(429, "You exceeded your current quota, please check your plan and billing details")  # Gemini-Ratenlimit


def test_503_wiederholt_und_weicht_auf_alternative_aus(monkeypatch):
    modelle = []

    def post(url, headers, json, timeout):
        modelle.append(json["model"])
        return ok_antwort() if json["model"] == "gemini-2.5-flash" else R(503, "overloaded")
    monkeypatch.setattr(llm.requests, "post", post)
    s = llm.OpenAISitzung("u", "k", "gemini-flash-latest", "sys", [], alternativen=["gemini-2.5-flash"])
    s.SCHLAF = lambda x: None
    s.nutzer("hi")
    assert s.schritt().text == "fertig"
    assert modelle == ["gemini-flash-latest", "gemini-flash-latest", "gemini-2.5-flash"] and s.modell == "gemini-2.5-flash"


def test_liga_pausiert_ohne_guthaben_und_merkt_modellnamen(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    d = next(f for f in funds.liga_fonds() if f["id"] == "liga_openai")
    funds.speichere_meta(d["id"], {"pausiert_bis": T + 3600, "status": routemod.PAUSE_KEIN_GUTHABEN})
    assert routemod.route(d, bmod.Budget(1.0, T), T)["status"] == routemod.PAUSE_KEIN_GUTHABEN
    funds.speichere_meta(d["id"], {"pausiert_bis": 0, "modell_aufgeloest": "gpt-5-nano", "modell_konfiguriert": d["modell"]})
    assert routemod.route(d, bmod.Budget(1.0, T + 7200), T + 7200)["modell"] == "gpt-5-nano"


def test_tiefenrunde_nutzt_opus(monkeypatch):
    monkeypatch.setenv("ARENA_ANTHROPIC_KEY", "x")
    c = funds.claude_fonds()[0]
    assert routemod.route(c, bmod.Budget(1.0, T), T, tief=True)["modell"] == "claude-opus-5-5"
    assert routemod.route(c, bmod.Budget(1.0, T), T)["modell"] == "claude-sonnet-5-5"


# ---------------------------------------------------------------- Agentenschleife: Abschluss-Hinweis
class Sitzung:
    def __init__(self):
        self.nachrichten, self.hinweise, self.n = [], [], 0

    def nutzer(self, t):
        self.nachrichten.append(t)

    def tool_ergebnisse(self, e):
        self.nachrichten.append(e)

    def hinweis(self, t):
        self.hinweise.append(t)

    def schritt(self):
        self.n += 1
        return llm.Antwort(aufrufe=[{"id": str(self.n), "name": "portfolio", "input": {}}],
                           nutzung={"ein": 1000, "aus": 20000, "cache_lesen": 0, "cache_schreiben": 0, "websuchen": 0}, ende="tool_use")


def test_rundenbudget_gibt_abschluss_hinweis_statt_hartem_abbruch():
    pf = portfolio.neu("claude_mittel", 10000)
    funds.speichere_portfolio(pf)
    s = Sitzung()
    defn = funds.claude_fonds()[1]
    snap = {"ts": 1.0, "fx": 1.1, "krypto": {}, "perps": {}, "aktien": {}, "optionen": [], "wetten": [], "pm_index": {}, "nachrichten": [], "verlauf": {}}

    class MZ:
        fehler = []

        def marke(self, i):
            return {}
    res = loop.laufe_runde(defn, {"art": "anthropic", "modell": "claude-sonnet-5-5"}, pf, snap, MZ(), "Test", [], bmod.Budget(1.0, T), 3,
                           T, sitzung_fabrik=lambda sp, t: s, runden_budget_usd=0.5)
    assert len(s.hinweise) == 1 and "Rundenbudget" in s.hinweise[0]
    assert res["abbruch"].startswith("Abschluss") and res["schritte"] == 2 + loop.SCHLUSS_SCHRITTE


# ---------------------------------------------------------------- Unabhängigkeit & Überlappung
def _markt(i, frage, vol):
    return {"mid": f"pm:polymarket:{i}", "venue": "polymarket", "frage": frage, "ja_bid": 0.4, "ja_ask": 0.42, "volumen_24h": vol, "schliesst": None}


def test_startlisten_je_fonds_verschieden_und_schwerpunkt_zuerst():
    w = [_markt(1, "Iran ceasefire by November?", 9e6), _markt(2, "Fed cuts rates in December?", 1e5),
         _markt(3, "Bitcoin above 150k in 2026?", 2e5), _markt(4, "Nvidia earnings beat?", 3e5)] + \
        [_markt(10 + i, f"Random question {i}", 1e4 * i) for i in range(60)]
    s = {"ts": T, "wetten": w, "pm_index": {m["mid"]: m for m in w}}
    cf = {f["id"]: f for f in funds.claude_fonds()}
    l = {k: snapshot.startliste(s, d, 12) for k, d in cf.items()}
    assert l["claude_vorsichtig"][0] == "pm:polymarket:2" and l["claude_aggressiv"][0] == "pm:polymarket:3" and l["claude_mittel"][0] == "pm:polymarket:4"
    assert len(set(l["claude_vorsichtig"]) & set(l["claude_mittel"])) < 6  # nicht dieselbe Liste
    assert snapshot.startliste(s, None, 12)[0] == "pm:polymarket:1"  # Liga: gleiche Liste nach Umsatz


def test_system_prompt_enthaelt_schwerpunkt_aber_keine_anderen_fonds():
    from arena.agent import prompts
    c = funds.claude_fonds()
    sp = prompts.system_prompt(c[2], {})
    assert "SCHWERPUNKT" in sp and "Krypto" in sp
    assert not any(o["name"] in sp for o in c if o["id"] != c[2]["id"])


def test_ueberlappung():
    def f(fid, pos):
        return {"id": fid, "positionen": [{"inst": i, "seite": "long", "wert": w} for i, w in pos]}
    u = site.ueberlappung([f("a", [("pm:x:1:JA", 100), ("spot:BTC-USD", 100)]), f("b", [("pm:x:1:JA", 50), ("perp:BTC_USDC-PERPETUAL", 50)]),
                           f("c", [("pm:x:2:JA", 10)])])
    ab = next(p for p in u["paare"] if p["a"] == "a" and p["b"] == "b")
    assert ab["pct"] == 100.0  # b ist vollständig in a enthalten (BTC spot/perp = gleiche Wette)
    assert next(p for p in u["paare"] if p["b"] == "c")["pct"] == 0.0


# ---------------------------------------------------------------- Taktgeber
def test_takt_slots_tiefenrunde_review_und_prognosen():
    t13 = 1_793_318_400 + 13 * 3600 + 600  # 2026-10-30 13:10 UTC (Freitag)
    a = takt.aufgaben(t13)
    assert "taeglich" in a and "prognosen" in a
    assert takt.aufgaben(t13 + 900) == []  # gleicher Slot, Prognosen erst in 6 h
    assert takt.aufgaben(t13 + 900, ereignis=True) == ["ereignis"]
    assert takt.aufgaben(t13 + 4 * 3600) == ["takt"]  # 17 UTC
    sonntag = t13 + 2 * 86400 + 6 * 3600  # So 19:10
    assert "review" in takt.aufgaben(sonntag)


def test_rundenart():
    z = {"letzte_taegliche": T}
    assert entscheider.rundenart("taeglich", z, T) == "tief"
    assert entscheider.rundenart("takt", z, T + 3600) == "takt"
    assert entscheider.rundenart("takt", z, T + 24 * 3600) == "tief"  # Tiefenrunde verpasst → nachholen
    assert entscheider.rundenart("ereignis", z, T + 24 * 3600) == "ereignis"


def test_status_json_hat_kosten_und_ueberlappung():
    pf = portfolio.neu("claude_mittel", 11000)
    funds.speichere_portfolio(pf)
    store.anhaengen("funds/claude_mittel/equity.jsonl", {"t": T, "usd": 11000, "cash": 11000, "n": 0, "gebuehren": 0})
    store.anhaengen("budget_log.jsonl", {"ts": T, "fonds": "claude_mittel", "modell": "claude-sonnet-5-5", "usd": 1.1})
    site.bauen(T + 60)
    st = json.loads((site.DOCS / "status.json").read_text())
    r = st["rangliste"][0]
    assert r["kosten_gesamt_eur"] > 0 and "ueberlappung_claude_pct" in st and st["budget"]["ziel_tag_eur"] > 8
