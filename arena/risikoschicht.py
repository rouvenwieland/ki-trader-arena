"""Positionsgrößen und Risikoschicht (Recherche: größter Verlusttreiber bei LLM-Tradern ist Größe/Übertrading).

* Kelly für binäre Kontrakte inkl. Gebühr, einzeln und simultan über die offenen Wetten des Fonds (gemeinsames log-Optimum).
* Bruchteil je Risikoprofil, gekürzt bei schlechter Kalibrierung (schlechter als der Markt); Rekalibrierung erst ab 50 Auflösungen.
* Volatilitäts-Targeting (GARCH) für Krypto/Perps/Aktien mit Stop-Vorschlag.
Die Werte sind Empfehlungen für den Agenten; hart durchgesetzt werden nur die Limits in exchange/risk.py."""
from __future__ import annotations

import itertools
import math

from arena import config, metrics, store
from arena import statistik as st
from arena.exchange import fees, portfolio

KELLY_BRUCHTEIL = {"vorsichtig": 0.15, "mittel": 0.25, "aggressiv": 0.4}
VOL_ZIEL_TAG = {"vorsichtig": 0.005, "mittel": 0.01, "aggressiv": 0.02}  # erlaubter 1-σ-Tagesverlust in % des Kapitals
MAX_SIMULTAN = 10


def kelly_binaer(p: float, kosten: float) -> float:
    """Kelly-Anteil des Kapitals für einen Kontrakt, der `kosten` (Preis + Gebühr) kostet und 1 auszahlt: (p − k)/(1 − k)."""
    if not 0 < kosten < 1:
        return 0.0
    return max(0.0, (p - kosten) / (1 - kosten))


def kelly_simultan(neu: tuple[float, float], offen: list[tuple[float, float, float]], schritte: int = 60) -> float:
    """Optimaler Anteil für die neue Wette (p, kosten), wenn offene Wetten (p, kosten, anteil_des_kapitals) bestehen bleiben.
    Ausgänge als unabhängig angenommen (konservativ wäre positive Korrelation; dann ist der Wert eine Obergrenze)."""
    p_n, k_n = neu
    if not 0 < k_n < 1 or p_n <= k_n:
        return 0.0
    offen = offen[:MAX_SIMULTAN]
    rest = 1 - sum(a for _, _, a in offen)
    best_f, best_u = 0.0, -math.inf
    obergrenze = min(kelly_binaer(p_n, k_n), max(rest, 0.0))
    for i in range(schritte + 1):
        f = obergrenze * i / schritte
        u = 0.0
        for ausg in itertools.product((0, 1), repeat=len(offen) + 1):
            w_p, w = 1.0, rest - f
            for (p, k, a), y in zip(offen + [(p_n, k_n, f)], ausg):
                w_p *= p if y else 1 - p
                w += (a / k) * y if a > 0 else 0.0
            if w <= 0:
                u = -math.inf
                break
            u += w_p * math.log(w)
        if u > best_u:
            best_f, best_u = f, u
    return best_f


def bruchteil(defn: dict) -> tuple[float, str]:
    """Kelly-Bruchteil des Profils; halbiert, wenn der Fonds marktbereinigt schlechter als der Markt schätzt (n ≥ 10)."""
    b = KELLY_BRUCHTEIL.get(defn.get("risiko", "mittel"), 0.25)
    k = metrics.brier(defn["id"])
    if k.get("n_markt", 0) >= 10 and (k.get("marktbereinigt") or 0) > 0:
        return b / 2, f"halbiert: deine Schätzungen waren bisher schlechter als der Marktpreis (n={k['n_markt']})"
    return b, "Profil-Bruchteil"


def eigene_schaetzung(fid: str, markt_id: str) -> float | None:
    for p in reversed(store.lies_jsonl(f"funds/{fid}/prognosen.jsonl", 400)):
        if p["markt_id"] == markt_id:
            return float(p["p_ja"])
    return None


def wette(defn: dict, pf: dict, inst: dict, book, p_ja: float | None, equity: float) -> dict:
    """Größenempfehlung für den Kauf eines Wettmarkt-Kontrakts (JA oder NEIN)."""
    fid = defn["id"]
    mid = inst["id"].rsplit(":", 1)[0]
    p = p_ja if p_ja is not None else eigene_schaetzung(fid, mid)
    if p is None:
        return {"fehler": "Keine eigene Wahrscheinlichkeit – erst mit „wahrscheinlichkeit“ schätzen oder p_ja angeben."}
    roh = p
    kal = metrics.kalibrierung(fid)
    hinweis = []
    if kal and kal["n"] >= 50:  # Umstiegspunkt der Empfehlung: Rekalibrierung erst ab 50 Auflösungen anwenden
        p = st.rekalibriere(p, (kal["a"], kal["b"]))
        hinweis.append(f"p rekalibriert {roh:.2f}→{p:.2f} (Platt, n={kal['n']})")
    p_seite = p if inst.get("ergebnis", "JA") == "JA" else 1 - p
    if not book or not book.asks:
        return {"fehler": "Kein Orderbuch auf der Kaufseite."}
    preis = book.asks[0][0]
    gebuehr = fees.gebuehr(inst, preis, 100) / 100
    k = preis + gebuehr
    einzel = kelly_binaer(p_seite, k)
    offen = []
    for pos in pf["positionen"]:
        if pos["inst"]["art"] != "pm" or pos["inst"]["id"] == inst["id"]:
            continue
        pe = eigene_schaetzung(fid, pos["inst"]["id"].rsplit(":", 1)[0])
        if pe is None:
            continue
        pe = pe if pos["inst"].get("ergebnis", "JA") == "JA" else 1 - pe
        offen.append((pe, pos["einstand"], pos["einstand"] * pos["menge"] / max(equity, 1e-9)))
    sim = kelly_simultan((p_seite, k), offen) if offen else einzel
    b, warum = bruchteil(defn)
    empf = b * sim * equity
    return {"preis_ask": round(preis, 4), "gebuehr_je_kontrakt": round(gebuehr, 5), "kosten_je_kontrakt": round(k, 4),
            "deine_p_seite": round(p_seite, 3), "vorteil_pp": round(100 * (p_seite - k), 1),
            "kelly_einzeln_pct": round(100 * einzel, 2), "kelly_simultan_pct": round(100 * sim, 2), "offene_wetten_beruecksichtigt": len(offen),
            "bruchteil": b, "bruchteil_grund": warum, "empfehlung_usd": round(empf, 2),
            "hinweis": "; ".join(hinweis + ["Kein Vorteil nach Kosten → nicht kaufen." if p_seite <= k else
                                            "Kelly ist eine Obergrenze; bei unsicherer Schätzung kleiner. Grenzen der Börse gelten zusätzlich."])}


def vol_ziel(defn: dict, inst: dict, equity: float, preise: list[float]) -> dict:
    """Nominal, bei dem der 1-σ-Tagesverlust dem Profilziel entspricht (GARCH auf Stundenkursen), plus Stop-Vorschlag (2 σ)."""
    from arena import forecast
    if len(preise) < 40:
        return {"fehler": "zu wenig Kursdaten für das Volatilitätsziel"}
    h = 1 if inst.get("art") == "stock" else 24  # Aktien: Tagesschlüsse
    g = forecast.garch_band(preise, h)
    if "fehler" in g:
        return g
    sigma = g["vola_horizont_pct"] / 100
    ziel = VOL_ZIEL_TAG.get(defn.get("risiko", "mittel"), 0.01)
    nominal = equity * ziel / max(sigma, 1e-6)
    px = preise[-1]
    return {"vola_tag_pct": round(100 * sigma, 2), "ziel_verlust_1sigma_pct": 100 * ziel, "empfohlenes_nominal_usd": round(nominal, 2),
            "stop_vorschlag_long": round(px * math.exp(-2 * sigma), 6), "stop_vorschlag_short": round(px * math.exp(2 * sigma), 6),
            "hinweis": "Stop 2 σ außerhalb des normalen Tagesrauschens; bei Hebel zählt das Nominal, nicht die Marge."}


def cluster_auslastung(pf: dict, prof: dict, equity: float) -> dict:
    """Aktuelle Auslastung der Cluster-Limits (für das Portfolio-Werkzeug)."""
    from arena.exchange import risk
    return risk.cluster_stand(pf, prof, equity)


def _equity(pf: dict, mz) -> float:
    marks = {p["inst"]["id"]: mz.marke(p["inst"]) for p in pf["positionen"]}
    return portfolio.equity(pf, marks)


def cfg_limits(risiko: str) -> dict:
    return config.load()["risiko"][risiko]
