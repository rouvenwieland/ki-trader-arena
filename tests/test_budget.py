import pytest

from arena import config
from arena.agent import budget


@pytest.fixture(autouse=True)
def tmpdata(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA", tmp_path)


def test_kosten_sonnet():
    # 1 Mio ein + 1 Mio aus = 2 + 10 USD, mal Sicherheitsfaktor
    assert budget.kosten_usd("claude-sonnet-5-5", {"ein": 1_000_000, "aus": 1_000_000}) == pytest.approx(12 * budget.SICHERHEIT)


def test_cache_und_websuche():
    k = budget.kosten_usd("claude-sonnet-5-5", {"cache_lesen": 1_000_000, "websuchen": 10})
    assert k == pytest.approx((0.2 + 0.1) * budget.SICHERHEIT)


def test_unbekanntes_modell_wird_verweigert():
    with pytest.raises(KeyError):
        budget.kosten_usd("claude-unbekannt", {"ein": 1})


def test_tagesdeckel_hart():
    b = budget.Budget(1.0, jetzt=1_800_000_000)
    ok, _ = b.darf("f", 3)
    assert ok
    b.buche("f", "claude-opus-5-5", {"ein": 0, "aus": 600_000})  # 12 USD * 1.15 = 13.8 > 12
    ok, grund = b.darf("g", 3, global_nur=True)
    assert not ok and "Tagesbudget" in grund


def test_fondsanteil():
    b = budget.Budget(1.0, jetzt=1_800_000_000)
    b.buche("f", "claude-sonnet-5-5", {"aus": 400_000})  # 4 USD * 1.15 = 4.6 > Anteil 4
    assert not b.darf("f", 3)[0]
    assert b.darf("g", 3)[0]


def test_vorausschau_verhindert_ueberschreitung():
    b = budget.Budget(1.0, jetzt=1_800_000_000)
    b.buche("f", "claude-sonnet-5-5", {"aus": 1_040_000})  # ≈ 11,96 USD
    schaetz = budget.schaetze_naechsten_aufruf("claude-sonnet-5-5", 30000, 6000)
    assert schaetz > 0.05
    assert not b.darf("f", 1, schaetz, global_nur=True)[0]


def test_gesamtdeckel_und_persistenz(tmp_path):
    b = budget.Budget(1.0, jetzt=1_800_000_000)
    b.buche("f", "claude-opus-5-5", {"aus": 100})
    b2 = budget.Budget(1.0, jetzt=1_800_000_000)
    assert b2.z["gesamt_usd"] == pytest.approx(b.z["gesamt_usd"])
    b2.z["gesamt_usd"] = 190.0
    assert b2.gesamt_erschoepft() and b2.darf("f", 1)[1] == "Gesamtbudget erschöpft"


def test_claude_ende():
    assert not budget.Budget(1.0, jetzt=1_793_000_000).claude_zeit_vorbei()  # 2026-10-26
    assert budget.Budget(1.0, jetzt=1_795_000_000).claude_zeit_vorbei()  # 2026-11-18
