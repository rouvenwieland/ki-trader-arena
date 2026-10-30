"""Papier-Börse: Eröffnen, Schließen, Funding, Liquidation, Abrechnung.

Alle Beträge in USD. Funktionen verändern das Portfolio-Dict in place und liefern
ein Handelsprotokoll (dict) zurück, das der Aufrufer append-only speichert."""
from __future__ import annotations

import math
import time

from arena import config, policy
from arena.exchange import fees, impact, portfolio, risk
from arena.exchange.book import Book, max_qty_fuer_budget, walk

ARTEN = ("spot", "perp", "option", "pm", "stock")


def _slip(art: str) -> float:
    return config.load()["boerse"]["slippage_bps"].get(art, 0)


def _ablehnung(grund: str, **kw) -> dict:
    return {"ok": False, "grund": grund, **kw}


def eroeffne(pf: dict, prof: dict, inst: dict, book: Book, *, seite: str = "long", qty: float | None = None,
             usd: float | None = None, hebel: float = 1.0, equity: float | None = None,
             stop_loss: float | None = None, take_profit: float | None = None,
             ausstiegsplan: str = "", entscheidung_id: str | None = None, ts: float | None = None,
             index_preis: float | None = None) -> dict:
    """Kauft (bzw. eröffnet Perp long/short) gegen das Orderbuch."""
    ts = ts or time.time()
    art = inst["art"]
    if art not in ARTEN:
        return _ablehnung(f"Unbekannte Instrumentenart {art}")
    if seite not in ("long", "short"):
        return _ablehnung("seite muss long oder short sein")
    if seite == "short" and art != "perp":
        return _ablehnung("Leerverkäufe gibt es nur bei Perpetuals")
    if (qty is None) == (usd is None):
        return _ablehnung("Genau eines von qty oder usd angeben")
    for name, wert in (("qty", qty), ("usd", usd), ("hebel", hebel), ("stop_loss", stop_loss), ("take_profit", take_profit)):
        if wert is not None and (not isinstance(wert, (int, float)) or not math.isfinite(wert) or (name in ("qty", "usd", "hebel") and wert <= 0)):
            return _ablehnung(f"Ungültiger Wert für {name}: {wert}")
    if stop_loss is not None and take_profit is not None and ((seite == "long") != (stop_loss < take_profit)):
        return _ablehnung("Stop-Loss/Take-Profit liegen auf der falschen Seite")
    kaufen = seite == "long"
    levels = book.asks if kaufen else book.bids
    if not levels:
        return _ablehnung("Kein Orderbuch auf dieser Seite (kein Handel möglich)")
    slip = _slip(art)
    gebuehr_fn = lambda p, q: fees.gebuehr(inst, p, q, index_preis)  # noqa: E731
    if usd is not None:
        if art == "perp":
            q = max_qty_fuer_budget(levels, usd, slip, lambda p, q: 0.0)
        else:
            q = max_qty_fuer_budget(levels, usd, slip, gebuehr_fn)
    else:
        q = qty
    if art == "pm":
        q = float(int(q))  # ganze Kontrakte
    if q <= 0:
        return _ablehnung("Menge null (Budget zu klein oder keine Tiefe)")
    f = walk(levels, q, slip, kaufen)
    if f.qty <= 0:
        return _ablehnung("Keine Füllung möglich")
    if art == "pm":
        f.qty = float(int(f.qty))
        if f.qty <= 0:
            return _ablehnung("Weniger als ein Kontrakt füllbar")
        f.kosten = f.vwap * f.qty
    if art == "pm" and not (0 < f.vwap < 1):
        return _ablehnung(f"Preis {f.vwap:.4f} außerhalb (0,1)")
    nominal = f.kosten
    fee = gebuehr_fn(f.vwap, f.qty)
    eq = equity if equity is not None else pf["cash"] + sum(p["marge"] if p["inst"]["art"] == "perp" else p["einstand"] * p["menge"] for p in pf["positionen"])
    for lvl, name in ((stop_loss, "Stop-Loss"), (take_profit, "Take-Profit")):
        if lvl is not None and ((name == "Stop-Loss") == (seite == "long")) == (lvl >= f.vwap):
            return _ablehnung(f"{name} {lvl} liegt auf der falschen Seite des Einstiegs {f.vwap:.4f}")
    grund = risk.pruefe_eroeffnung(pf, prof, inst, nominal, hebel, eq)
    if grund:
        return _ablehnung(grund)
    if inst.get("venue") == "predictit":
        cap = config.load()["boerse"]["gebuehren"]["predictit_max_position_usd"]
        bestand = sum(p["einstand"] * p["menge"] for p in pf["positionen"] if p["inst"]["id"] == inst["id"])
        if bestand + nominal > cap:
            return _ablehnung(f"PredictIt-Positionslimit {cap} USD je Vertrag")
    perp = art == "perp"
    marge = nominal / hebel if perp else 0.0
    braucht = (marge if perp else nominal) + fee
    if braucht > pf["cash"] + 1e-9:
        return _ablehnung(f"Nicht genug Cash: nötig {braucht:.2f}, vorhanden {pf['cash']:.2f}")
    vorhandene = next((p for p in pf["positionen"] if p["inst"]["id"] == inst["id"] and p["seite"] == seite), None)
    if vorhandene and perp and abs(vorhandene["hebel"] - hebel) > 1e-9:
        return _ablehnung("Es besteht bereits eine Position mit anderem Hebel")
    mm = config.load()["boerse"]["perp"]["wartungsmarge"]
    if vorhandene:
        neue_menge = vorhandene["menge"] + f.qty
        vorhandene["einstand"] = (vorhandene["einstand"] * vorhandene["menge"] + f.vwap * f.qty) / neue_menge
        vorhandene["menge"] = neue_menge
        vorhandene["marge"] += marge
        vorhandene["gebuehren"] += fee
        pos = vorhandene
    else:
        pos = {"id": portfolio.neue_id(), "inst": inst, "seite": seite, "menge": f.qty, "einstand": f.vwap,
               "hebel": hebel, "marge": marge, "eroeffnet": ts, "gebuehren": fee, "funding": 0.0}
        pf["positionen"].append(pos)
    if stop_loss is not None:
        pos["stop_loss"] = stop_loss
    if take_profit is not None:
        pos["take_profit"] = take_profit
    if ausstiegsplan:
        pos["ausstiegsplan"] = ausstiegsplan
    if entscheidung_id:
        pos["entscheidung_id"] = entscheidung_id
    if perp:
        pos["liq_preis"] = pos["einstand"] * (((1 - 1 / hebel) / (1 - mm)) if seite == "long" else ((1 + 1 / hebel) / (1 + mm)))
    pf["cash"] -= braucht
    pf["gebuehren"] += fee
    impact.verbrauche(book, kaufen, f.qty)  # weitere Orders im selben Lauf sehen das verbrauchte Buch
    return {"ok": True, "ts": ts, "aktion": "eroeffnet", "fonds_id": pf["fonds_id"], "position_id": pos["id"],
            "inst_id": inst["id"], "seite": seite, "menge": f.qty, "preis": f.vwap, "gebuehr": fee,
            "nominal": nominal, "hebel": hebel, "tiefe_stufen": f.stufen,
            "teilfuellung": (qty is not None and f.qty + 1e-9 < qty), "liq_preis": pos.get("liq_preis"),
            "entscheidung_id": entscheidung_id}


def schliesse(pf: dict, pos: dict, book: Book, *, qty: float | None = None, grund: str = "manuell",
              ts: float | None = None, index_preis: float | None = None) -> dict:
    """Schließt (teilweise) gegen das Orderbuch. Bei dünner Tiefe bleibt ein Rest offen."""
    ts = ts or time.time()
    inst = pos["inst"]
    art = inst["art"]
    perp = art == "perp"
    verkaufen = pos["seite"] == "long"
    levels = book.bids if verkaufen else book.asks
    if not levels:
        return _ablehnung("Kein Orderbuch zum Schließen", position_id=pos["id"])
    if qty is not None and (not math.isfinite(qty) or qty <= 0):
        return _ablehnung("Ungültige Menge", position_id=pos["id"])
    q = pos["menge"] if qty is None else min(qty, pos["menge"])
    f = walk(levels, q, _slip(art), kaufen=not verkaufen)
    if f.qty <= 0:
        return _ablehnung("Keine Füllung beim Schließen", position_id=pos["id"])
    impact.verbrauche(book, not verkaufen, f.qty)
    return _abwickeln(pf, pos, f.qty, f.vwap, grund, ts, index_preis, perp, f.stufen)


def _abwickeln(pf: dict, pos: dict, q: float, preis: float, grund: str, ts: float,
               index_preis: float | None, perp: bool, stufen: int = 0, fee: float | None = None) -> dict:
    inst = pos["inst"]
    anteil = q / pos["menge"]
    if fee is None:
        fee = fees.gebuehr(inst, preis, q, index_preis)
    einstand_gesamt = pos["einstand"] * q
    if perp:
        vz = 1 if pos["seite"] == "long" else -1
        pnl = vz * (preis - pos["einstand"]) * q
        marge_teil = pos["marge"] * anteil
        pf["cash"] += marge_teil + pnl - fee
        erloes = marge_teil + pnl
        pos["marge"] -= marge_teil
        abschluss = 0.0
    else:
        erloes = preis * q
        abschluss = fees.abschluss_gebuehr(inst, einstand_gesamt, erloes)
        pnl = erloes - einstand_gesamt
        pf["cash"] += erloes - fee - abschluss
    einstiegs_fee = pos["gebuehren"] * anteil
    pos["gebuehren"] -= einstiegs_fee
    netto = pnl - fee - abschluss - einstiegs_fee
    pf["realisiert"] += pnl - fee - abschluss
    pf["gebuehren"] += fee + abschluss
    pos["menge"] -= q
    offen = pos["menge"] > 1e-9
    if not offen:
        pf["positionen"] = [p for p in pf["positionen"] if p["id"] != pos["id"]]
    return {"ok": True, "ts": ts, "aktion": "geschlossen" if not offen else "teilweise_geschlossen",
            "fonds_id": pf["fonds_id"], "position_id": pos["id"], "inst_id": inst["id"], "seite": pos["seite"],
            "menge": q, "preis": preis, "einstand": pos["einstand"], "gebuehr": fee + abschluss,
            "brutto_pnl": pnl, "netto_pnl": netto, "grund": grund, "tiefe_stufen": stufen,
            "kategorie": policy.kategorie_inst(inst, pos["seite"]), "eroeffnet": pos.get("eroeffnet")}


def funding_buchen(pf: dict, raten_8h: dict[str, float], stunden: float, ts: float | None = None) -> list[dict]:
    """Bucht Funding auf Perp-Positionen. raten_8h: inst_id -> Rate je 8 h (positiv: Long zahlt Short)."""
    out = []
    for pos in pf["positionen"]:
        if pos["inst"]["art"] != "perp":
            continue
        rate = raten_8h.get(pos["inst"]["id"])
        if rate is None:
            continue
        vz = 1 if pos["seite"] == "long" else -1
        h = min(stunden, max(0.0, ((ts or time.time()) - pos["eroeffnet"]) / 3600))  # nur für die Haltedauer
        betrag = -vz * rate * (h / 8.0) * pos["einstand"] * pos["menge"]  # <0: zahlt
        pos["marge"] += betrag
        pos["funding"] = pos.get("funding", 0.0) + betrag
        pf["funding"] += betrag
        out.append({"ts": ts or time.time(), "aktion": "funding", "fonds_id": pf["fonds_id"],
                    "position_id": pos["id"], "inst_id": pos["inst"]["id"], "betrag": betrag, "rate_8h": rate})
    return out


def pruefe_liquidation(pf: dict, extreme: dict[str, tuple[float, float]], marks: dict[str, float],
                       ts: float | None = None) -> list[dict]:
    """extreme: inst_id -> (Tief, Hoch) seit der letzten Prüfung (Dochte). Liquidiert, wenn
    Eigenkapital der Position unter die Wartungsmarge fällt (Funding gebucht in marge)."""
    ts = ts or time.time()
    cfg = config.load()["boerse"]["perp"]
    out = []
    for pos in list(pf["positionen"]):
        if pos["inst"]["art"] != "perp":
            continue
        tief, hoch = extreme.get(pos["inst"]["id"], (None, None))
        mk = marks.get(pos["inst"]["id"])
        schlimmster = (tief if pos["seite"] == "long" else hoch)
        if schlimmster is None:
            schlimmster = mk
        if schlimmster is None:
            continue
        vz = 1 if pos["seite"] == "long" else -1
        eq = pos["marge"] + vz * (schlimmster - pos["einstand"]) * pos["menge"]
        wartung = cfg["wartungsmarge"] * schlimmster * pos["menge"]
        if eq <= wartung:
            liqfee = cfg["liquidationsgebuehr"] * schlimmster * pos["menge"]
            rest = max(0.0, eq - liqfee)
            verlust_marge = pos["marge"]
            pf["cash"] += rest
            pf["realisiert"] += rest - verlust_marge - pos.get("funding", 0.0)  # Funding steht schon in pf["funding"]
            pf["gebuehren"] += min(liqfee, max(eq, 0.0))
            pf["positionen"] = [p for p in pf["positionen"] if p["id"] != pos["id"]]
            out.append({"ok": True, "ts": ts, "aktion": "liquidiert", "fonds_id": pf["fonds_id"],
                        "position_id": pos["id"], "inst_id": pos["inst"]["id"], "seite": pos["seite"],
                        "menge": pos["menge"], "preis": schlimmster, "einstand": pos["einstand"],
                        "rest_zurueck": rest, "netto_pnl": rest - verlust_marge, "gebuehr": liqfee,
                        "grund": "Liquidation (Marge unter Wartungsmarge)", "kategorie": policy.kategorie_inst(pos["inst"], pos["seite"]),
                        "eroeffnet": pos.get("eroeffnet")})
    return out


def stop_ziele(pf: dict, extreme: dict[str, tuple[float, float]], marks: dict[str, float]) -> list[tuple[dict, str, float]]:
    """Liefert (Position, Grund, Auslösepreis) für ausgelöste Stop-Loss/Take-Profit.
    Long: Tief <= SL bzw. Hoch >= TP. Short umgekehrt. Dochte zählen (konservativ: SL zuerst)."""
    out = []
    for pos in pf["positionen"]:
        iid = pos["inst"]["id"]
        tief, hoch = extreme.get(iid, (None, None))
        mk = marks.get(iid)
        tief = mk if tief is None else min(tief, mk) if mk is not None else tief
        hoch = mk if hoch is None else max(hoch, mk) if mk is not None else hoch
        if tief is None or hoch is None:
            continue
        sl, tp = pos.get("stop_loss"), pos.get("take_profit")
        long = pos["seite"] == "long"
        if sl is not None and ((long and tief <= sl) or (not long and hoch >= sl)):
            out.append((pos, "Stop-Loss", sl))
        elif tp is not None and ((long and hoch >= tp) or (not long and tief <= tp)):
            out.append((pos, "Take-Profit", tp))
    return out


def rechne_pm_ab(pf: dict, pos: dict, wert_ja: float, ts: float | None = None) -> dict:
    """Abrechnung eines Wettmarkt-Kontrakts. wert_ja ∈ [0,1] (1 = Ja, 0 = Nein, 0,5 = geteilt;
    Annullierung: Aufrufer übergibt den Einstandspreis über rechne_pm_storno)."""
    inst = pos["inst"]
    auszahlung = wert_ja if inst.get("ergebnis", "JA") == "JA" else 1 - wert_ja
    return _abwickeln(pf, pos, pos["menge"], auszahlung, "Abrechnung des Marktes", ts or time.time(), None, False, fee=0.0)


def rechne_pm_storno(pf: dict, pos: dict, ts: float | None = None) -> dict:
    return _abwickeln(pf, pos, pos["menge"], pos["einstand"], "Markt annulliert, Einsatz erstattet",
                      ts or time.time(), None, False, fee=0.0)


def rechne_option_ab(pf: dict, pos: dict, abrechnungspreis: float, ts: float | None = None) -> dict:
    """Verfall einer Deribit-Option zum Innenwert; Lieferungsgebühr 0,015 % des Basiswerts, max 12,5 % des Werts."""
    inst = pos["inst"]
    k = inst["strike"]
    innen = max(abrechnungspreis - k, 0.0) if inst["typ"] == "C" else max(k - abrechnungspreis, 0.0)
    fee = min(0.00015 * abrechnungspreis * pos["menge"], 0.125 * innen * pos["menge"]) if innen > 0 else 0.0
    return _abwickeln(pf, pos, pos["menge"], innen, "Verfall/Abrechnung", ts or time.time(), None, False, fee=fee)
