from arena import events

CFG = {"kurssprung_pct": 3.0, "kurssprung_1h_pct": 5.0, "wettmarkt_bewegung_pp": 8.0, "markt_schliesst_stunden": 24,
       "volatilitaet_faktor": 3.0, "fehlbewertung_pp": 12.0, "funding_extrem_8h": 0.0008}
T = 1_800_000_000


def serie(preis, n=20, schritt=900, jitter=0.0005):
    return [(T - (n - i) * schritt, preis * (1 + (jitter if i % 2 else -jitter))) for i in range(n)]


def test_kurssprung_loest_aus_und_dedupliziert():
    verlauf = {"spot:BTC-USD": serie(100)}
    bekannt: set = set()
    e = events.erkenne(T, {"spot:BTC-USD": 104.0}, verlauf, {}, [], [], [], {}, bekannt, CFG)
    assert any(x["typ"] == "kurssprung" and x["weckt"] for x in e)
    e2 = events.erkenne(T + 60, {"spot:BTC-USD": 104.0}, verlauf, {}, [], [], [], {}, bekannt, CFG)
    assert not e2


def test_kein_ereignis_bei_ruhe():
    verlauf = {"spot:BTC-USD": serie(100)}
    assert events.erkenne(T, {"spot:BTC-USD": 100.2}, verlauf, {}, [], [], [], {}, set(), CFG) == []


def test_wettmarkt_bewegung_gehalten_niedrigere_schwelle():
    m = {"mid": "pm:polymarket:1", "venue": "polymarket", "frage": "Wird X passieren", "ja_bid": 0.5, "ja_ask": 0.52, "volumen_24h": 50000}
    verlauf = {"pm:polymarket:1:JA": [(T - 3600, 0.46), (T - 900, 0.5)]}
    preise = {"pm:polymarket:1:JA": 0.51}
    e = events.erkenne(T, preise, verlauf, {"pm:polymarket:1:JA": ["claude_mittel"]}, [m], [], [], {}, set(), CFG)
    assert e and e[0]["typ"] == "wettmarkt_bewegung" and e[0]["fonds"] == ["claude_mittel"]
    e = events.erkenne(T, preise, verlauf, {}, [m], [], [], {}, set(), CFG)
    assert e == []  # 5 pp < 8 pp ohne Position


def test_markt_schliesst():
    p = [{"fonds": "f", "position_id": "p1", "inst_id": "pm:x:1:JA", "schliesst": T + 5 * 3600}]
    e = events.erkenne(T, {}, {}, {}, [], p, [], {}, set(), CFG)
    assert e[0]["typ"] == "markt_schliesst" and e[0]["fonds"] == ["f"]
    p[0]["schliesst"] = T + 30 * 3600
    assert events.erkenne(T, {}, {}, {}, [], p, [], {}, set(), CFG) == []


def test_nachricht_zu_position():
    m = {"mid": "pm:polymarket:2", "venue": "polymarket", "frage": "Will Netanyahu remain Prime Minister of Israel", "ja_bid": .4, "ja_ask": .42}
    n = [{"titel": "Netanyahu coalition crisis threatens Israel government", "quelle": "BBC", "url": "u1", "zeit": T, "text": ""}]
    e = events.erkenne(T, {}, {}, {"pm:polymarket:2:JA": ["f"]}, [m], [], n, {}, set(), CFG)
    assert any(x["typ"] == "nachricht_position" for x in e)


def test_fehlbewertung_kreuz_plattform():
    a = {"mid": "pm:polymarket:1", "venue": "polymarket", "frage": "Will Republicans win the House in 2026", "ja_bid": .60, "ja_ask": .61}
    b = {"mid": "pm:kalshi:K", "venue": "kalshi", "frage": "Will Republicans win the House in 2026", "ja_bid": .78, "ja_ask": .79}
    e = events.erkenne(T, {}, {}, {}, [a, b], [], [], {}, set(), CFG)
    assert any(x["typ"] == "fehlbewertung" for x in e)


def test_volatilitaetsausbruch():
    s = serie(100, n=40, jitter=0.0004)
    s[-1] = (T - 900, 100.0)
    s.append((T - 3600 + 0, 100.0))
    s.sort()
    e = events.erkenne(T, {"perp:X": 102.0}, {"perp:X": s}, {"perp:X": ["f"]}, [], [], [], {}, set(), {**CFG, "kurssprung_pct": 10, "kurssprung_1h_pct": 10})
    assert any(x["typ"] == "volatilitaet" for x in e)


def test_extremes_funding():
    e = events.erkenne(T, {}, {}, {"perp:BTC": ["f"]}, [], [], [], {"perp:BTC": 0.002}, set(), CFG)
    assert e and e[0]["typ"] == "fehlbewertung" and e[0]["weckt"]


def test_keine_fehlbewertung_bei_aehnlichen_aber_verschiedenen_fragen():
    a = {"mid": "pm:polymarket:1", "venue": "polymarket", "frage": "2026 Balance of Power: R Senate, R House", "ja_bid": .06, "ja_ask": .07}
    b = {"mid": "pm:predictit:2", "venue": "predictit", "frage": "Balance of Power 2026: D Senate, R House", "ja_bid": .68, "ja_ask": .69}
    assert not [x for x in events.erkenne(T, {}, {}, {}, [a, b], [], [], {}, set(), CFG) if x["typ"] == "fehlbewertung"]
