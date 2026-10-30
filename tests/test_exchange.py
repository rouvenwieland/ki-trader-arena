import math

import pytest

from arena.exchange import engine, fees, portfolio, risk
from arena.exchange.book import Book, max_qty_fuer_budget, walk

MITTEL = risk.profil("mittel")
AGGR = risk.profil("aggressiv")
VORSICHT = risk.profil("vorsichtig")


def spot(sym="BTC-USD"):
    return {"id": f"spot:{sym}", "art": "spot", "venue": "coinbase"}


def pm(venue="polymarket", ergebnis="JA", id_="pm:x"):
    return {"id": id_, "art": "pm", "venue": venue, "ergebnis": ergebnis}


def perp():
    return {"id": "perp:BTC", "art": "perp", "venue": "deribit"}


def test_walk_vwap_und_teilfuellung():
    f = walk([(100, 1), (101, 1)], 1.5, 0, True)
    assert f.qty == 1.5 and f.vwap == pytest.approx((100 + 0.5 * 101) / 1.5) and f.voll
    f = walk([(100, 1)], 3, 0, True)
    assert f.qty == 1 and not f.voll


def test_slippage_gegen_haendler():
    assert walk([(100, 5)], 1, 10, True).vwap == pytest.approx(100.1)
    assert walk([(100, 5)], 1, 10, False).vwap == pytest.approx(99.9)


def test_budget_menge_respektiert_gebuehr():
    lv = [(100.0, 100)]
    q = max_qty_fuer_budget(lv, 1000, 0, lambda p, q: p * q * 0.01)
    assert q * 100 * 1.01 <= 1000 + 1e-6 and q == pytest.approx(1000 / 101, rel=1e-6)


def test_kalshi_gebuehr_aufgerundet():
    g = fees.gebuehr({"art": "pm", "venue": "kalshi"}, 0.5, 100)
    assert g == pytest.approx(1.75)  # 0,07*100*0,25 = 1,75 exakt, kein Aufrunden nötig
    assert fees.gebuehr({"art": "pm", "venue": "kalshi"}, 0.33, 10) == pytest.approx(math.ceil(0.07 * 10 * 0.33 * 0.67 * 100) / 100)


def test_option_gebuehr_deckel():
    # Teure Option: 0,03 % des Basiswerts greift. Billige Option: 12,5 % des Preises greift.
    inst = {"art": "option", "venue": "deribit"}
    assert fees.gebuehr(inst, 5000, 1, 80000) == pytest.approx(80000 * 0.0003)
    assert fees.gebuehr(inst, 50, 1, 80000) == pytest.approx(50 * 0.125)


def test_kauf_und_verkauf_spot_kosten():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(99.0, 100)], asks=[(101.0, 100)])
    r = engine.eroeffne(pf, MITTEL, spot(), book, usd=1500, ts=1)
    assert r["ok"]
    pos = pf["positionen"][0]
    erwartet_vwap = 101.0 * 1.0002
    assert r["preis"] == pytest.approx(erwartet_vwap)
    assert pf["cash"] == pytest.approx(10000 - r["menge"] * erwartet_vwap - r["gebuehr"])
    assert r["menge"] * erwartet_vwap + r["gebuehr"] <= 1500 + 1e-6
    # sofort wieder schließen: Verlust durch Spread + Gebühren + Slippage
    s = engine.schliesse(pf, pos, book, grund="test", ts=2)
    assert s["ok"] and not pf["positionen"]
    assert pf["cash"] < 10000 - 0.012 * 1500 * 0.9  # ≥ ~1,2 % Rundreise-Kosten


def test_risikolimit_einzelposition():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(1.0, 1e6)], asks=[(1.0, 1e6)])
    r = engine.eroeffne(pf, VORSICHT, spot(), book, usd=2000)
    assert not r["ok"] and "Einzelposition" in r["grund"]
    assert not pf["positionen"] and pf["cash"] == 10000


def test_hebel_limit_und_nur_perp():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(100, 1e6)], asks=[(100, 1e6)])
    assert "Hebel" in engine.eroeffne(pf, MITTEL, spot(), book, usd=500, hebel=2)["grund"]
    assert "Hebel" in engine.eroeffne(pf, MITTEL, perp(), book, usd=1000, hebel=5)["grund"]


def test_nicht_genug_tiefe_teilfuellung():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(1, 1)], asks=[(100, 2)])
    r = engine.eroeffne(pf, MITTEL, spot(), book, qty=10)
    assert r["ok"] and r["menge"] == 2 and r["teilfuellung"]


def test_perp_long_gewinn_und_funding():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(100, 1e6)], asks=[(100, 1e6)])
    r = engine.eroeffne(pf, AGGR, perp(), book, usd=3000, hebel=3, stop_loss=None, ts=1000)
    assert r["ok"]
    pos = pf["positionen"][0]
    assert pos["marge"] == pytest.approx(1000, rel=1e-3)
    assert pos["liq_preis"] == pytest.approx(100 * (1 - 1 / 3) / (1 - 0.005), rel=1e-3)
    f = engine.funding_buchen(pf, {"perp:BTC": 0.001}, 8, ts=1000 + 8 * 3600)
    assert f[0]["betrag"] == pytest.approx(-3.0, rel=1e-2)  # Long zahlt bei positiver Rate
    book2 = Book(bids=[(110, 1e6)], asks=[(110, 1e6)])
    s = engine.schliesse(pf, pos, book2, ts=5)
    assert s["brutto_pnl"] == pytest.approx(300, rel=1e-2)
    assert pf["cash"] > 10000 + 250


def test_perp_short_funding_erhaelt():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(100, 1e6)], asks=[(100, 1e6)])
    engine.eroeffne(pf, AGGR, perp(), book, usd=2000, hebel=2, seite="short", ts=1000)
    f = engine.funding_buchen(pf, {"perp:BTC": 0.001}, 8, ts=1000 + 8 * 3600)
    assert f[0]["betrag"] > 0


def test_liquidation_per_docht():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(100, 1e6)], asks=[(100, 1e6)])
    engine.eroeffne(pf, AGGR, perp(), book, usd=5000, hebel=5)
    cash_vorher = pf["cash"]
    # Docht auf 79: Verlust 21 % × 5 = 105 % der Marge → liquidiert, Markt schließt aber wieder bei 100
    ev = engine.pruefe_liquidation(pf, {"perp:BTC": (79.0, 101.0)}, {"perp:BTC": 100.0})
    assert len(ev) == 1 and ev[0]["aktion"] == "liquidiert"
    assert not pf["positionen"]
    assert pf["cash"] == pytest.approx(cash_vorher, abs=1e-6)  # Marge komplett weg, nichts zurück


def test_keine_liquidation_ueber_wartungsmarge():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(100, 1e6)], asks=[(100, 1e6)])
    engine.eroeffne(pf, AGGR, perp(), book, usd=3000, hebel=3)
    assert engine.pruefe_liquidation(pf, {"perp:BTC": (90.0, 101.0)}, {"perp:BTC": 100.0}) == []


def test_pm_abrechnung_ja_nein():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(0.39, 1000)], asks=[(0.40, 1000)])
    r = engine.eroeffne(pf, MITTEL, pm(), book, usd=1000)
    n = r["menge"]
    assert n == int(n)
    cash = pf["cash"]
    a = engine.rechne_pm_ab(pf, pf["positionen"][0], 1.0)
    assert pf["cash"] == pytest.approx(cash + n) and a["netto_pnl"] > 0
    # NO-Token verliert, wenn JA gewinnt
    pf2 = portfolio.neu("t", 10000)
    engine.eroeffne(pf2, MITTEL, pm(ergebnis="NEIN", id_="pm:y"), Book(bids=[(0.39, 1000)], asks=[(0.40, 1000)]), usd=1000)  # frisches Buch: Tiefe wird verbraucht
    cash2 = pf2["cash"]
    engine.rechne_pm_ab(pf2, pf2["positionen"][0], 1.0)
    assert pf2["cash"] == pytest.approx(cash2)


def test_predictit_gewinnsteuer():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(0.4, 1000)], asks=[(0.5, 1000)])
    inst = pm("predictit", id_="pm:pi")
    r = engine.eroeffne(pf, MITTEL, inst, book, qty=100)
    cash = pf["cash"]
    engine.rechne_pm_ab(pf, pf["positionen"][0], 1.0)
    gewinn = 100 - r["menge"] * r["preis"]
    assert pf["cash"] == pytest.approx(cash + 100 - 0.10 * gewinn)


def test_pm_storno_erstattet():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(0.4, 1000)], asks=[(0.5, 1000)])
    engine.eroeffne(pf, MITTEL, pm("manifold"), book, qty=100)
    cash = pf["cash"]
    engine.rechne_pm_storno(pf, pf["positionen"][0])
    assert pf["cash"] == pytest.approx(cash + 100 * 0.5 * 1.0)


def test_option_verfall_innenwert():
    pf = portfolio.neu("t", 10000)
    inst = {"id": "opt:x", "art": "option", "venue": "deribit", "strike": 70000, "typ": "P"}
    book = Book(bids=[(1500, 10)], asks=[(1600, 10)])
    r = engine.eroeffne(pf, AGGR, inst, book, qty=0.5, index_preis=78000)
    assert r["ok"]
    cash = pf["cash"]
    a = engine.rechne_option_ab(pf, pf["positionen"][0], 65000)
    assert pf["cash"] == pytest.approx(cash + 0.5 * 5000 - a["gebuehr"])
    pf2 = portfolio.neu("t", 10000)
    engine.eroeffne(pf2, AGGR, inst, book, qty=0.5, index_preis=78000)
    c2 = pf2["cash"]
    engine.rechne_option_ab(pf2, pf2["positionen"][0], 80000)
    assert pf2["cash"] == pytest.approx(c2)


def test_stop_loss_take_profit_mit_docht():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(100, 1e6)], asks=[(100, 1e6)])
    engine.eroeffne(pf, MITTEL, spot(), book, usd=1000, stop_loss=95, take_profit=110)
    assert engine.stop_ziele(pf, {"spot:BTC-USD": (96, 105)}, {"spot:BTC-USD": 100}) == []
    z = engine.stop_ziele(pf, {"spot:BTC-USD": (94, 105)}, {"spot:BTC-USD": 100})
    assert z[0][1] == "Stop-Loss"
    z = engine.stop_ziele(pf, {"spot:BTC-USD": (99, 111)}, {"spot:BTC-USD": 100})
    assert z[0][1] == "Take-Profit"


def test_equity_bewertet_zum_geldkurs():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(99, 1e6)], asks=[(101, 1e6)])
    engine.eroeffne(pf, MITTEL, spot(), book, usd=1000)
    eq = portfolio.equity(pf, {"spot:BTC-USD": {"bid": 99.0}})
    assert eq < 10000 - 10  # Spread + Gebühr sofort sichtbar


def test_nan_und_ungueltige_eingaben_werden_abgelehnt():
    nan = float("nan")
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(100, 1e6)], asks=[(100, 1e6)])
    assert not engine.eroeffne(pf, MITTEL, spot(), book, qty=nan)["ok"]
    assert not engine.eroeffne(pf, AGGR, perp(), book, usd=1000, hebel=nan)["ok"]
    assert not engine.eroeffne(pf, MITTEL, spot(), book, usd=500, stop_loss=nan)["ok"]
    assert pf["cash"] == 10000 and not pf["positionen"]
    engine.eroeffne(pf, MITTEL, spot(), book, usd=500)
    assert not engine.schliesse(pf, pf["positionen"][0], book, qty=nan)["ok"]
    assert pf["cash"] == pf["cash"] and pf["positionen"][0]["menge"] == pf["positionen"][0]["menge"]


def test_ungueltige_buchstufen_werden_ignoriert():
    assert walk([(0.0, 1e6), (-5, 10), (100, 2)], 5, 0, True).qty == 2


def test_stop_auf_falscher_seite_abgelehnt():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(100, 1e6)], asks=[(100, 1e6)])
    assert "falschen Seite" in engine.eroeffne(pf, MITTEL, spot(), book, usd=500, stop_loss=105)["grund"]
    assert "falschen Seite" in engine.eroeffne(pf, MITTEL, spot(), book, usd=500, take_profit=95)["grund"]


def test_perp_einzellimit_nicht_durch_mehrfachorders_umgehbar():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(100, 1e9)], asks=[(100, 1e9)])
    ok = 0
    for _ in range(30):
        ok += engine.eroeffne(pf, AGGR, perp(), book, usd=3000, hebel=10, ts=1)["ok"]
    assert sum(p["marge"] for p in pf["positionen"]) <= 0.35 * 10000 * 1.02


def test_funding_nur_fuer_haltedauer():
    pf = portfolio.neu("t", 10000)
    book = Book(bids=[(100, 1e6)], asks=[(100, 1e6)])
    engine.eroeffne(pf, AGGR, perp(), book, usd=1000, hebel=2, ts=1000)
    f = engine.funding_buchen(pf, {"perp:BTC": 0.001}, 6.0, ts=1000 + 360)  # Position existiert nur 0,1 h
    assert f[0]["betrag"] == pytest.approx(-0.001 * (0.1 / 8) * 1000, rel=0.02)
