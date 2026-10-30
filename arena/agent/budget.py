"""Anthropic-Budget mit hartem Stopp im Code: gezählte Tokens × Preis. Tagesdeckel, Gesamtdeckel, je Fonds ein Tagesanteil.

Alle Beträge intern in USD; Deckel in Euro (config) werden mit dem aktuellen Kurs umgerechnet.
Sicherheitsaufschlag auf alle Kosten, damit Rundungen/Preisstufen das Budget nicht überraschen."""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone

from arena import config, store

SICHERHEIT = 1.15


def kosten_usd(modell: str, nutzung: dict, cfg: dict | None = None) -> float:
    b = (cfg or config.load())["budget"]
    p = b["preise_usd_je_mio"].get(modell)
    if not p:
        raise KeyError(f"Kein Preis für Modell {modell} in config.json – Aufruf verweigert")
    ein, aus = nutzung.get("ein", 0), nutzung.get("aus", 0)
    c_l, c_s = nutzung.get("cache_lesen", 0), nutzung.get("cache_schreiben", 0)
    c_l_faktor = p.get("cache_lesen", b["cache_lesen_faktor"])  # je Modell (Opus 5.5: 0,05×), sonst pauschal
    usd = (ein * p["ein"] + aus * p["aus"] + c_l * p["ein"] * c_l_faktor + c_s * p["ein"] * b["cache_schreiben_faktor"]) / 1e6
    usd += nutzung.get("websuchen", 0) * b["websuche_usd_je_1000"] / 1000
    return usd * SICHERHEIT


def schaetze_naechsten_aufruf(modell: str, verlauf_zeichen: int, max_tokens: int, cfg: dict | None = None) -> float:
    """Worst-Case für den nächsten Aufruf: gesamter Verlauf als frische Eingabe (≈ 3 Zeichen/Token) + volle Ausgabe."""
    return kosten_usd(modell, {"ein": verlauf_zeichen // 3 + 2000, "aus": max_tokens, "websuchen": 0}, cfg)


class Budget:
    def __init__(self, usd_je_eur: float, jetzt: float | None = None, cfg: dict | None = None):
        self.cfg = cfg or config.load()
        self.fx = usd_je_eur
        self.jetzt = jetzt or time.time()
        self.tag = datetime.fromtimestamp(self.jetzt, timezone.utc).strftime("%Y-%m-%d")
        self.z = store.lies("budget.json", {"gesamt_usd": 0.0, "tage": {}, "fonds_tage": {}})
        self._lock = threading.RLock()  # Claude-Fonds laufen parallel in Threads
        self._reserviert: dict[int, float] = {}  # laufende Aufrufe (Worst-Case), damit parallele Fonds den Deckel nicht reißen

    # ---- Grenzen
    @property
    def tagesdeckel_usd(self) -> float:
        return self.cfg["budget"]["tagesdeckel_eur"] * self.fx

    @property
    def gesamtdeckel_usd(self) -> float:
        return self.cfg["budget"]["gesamtdeckel_eur"] * self.fx

    def heute_usd(self) -> float:
        return self.z["tage"].get(self.tag, 0.0)

    def fonds_heute_usd(self, fid: str) -> float:
        return self.z["fonds_tage"].get(self.tag, {}).get(fid, 0.0)

    def tempo_faktor(self) -> float:
        """Streckt das Restbudget bis zum Claude-Stichtag: Wenn Rest/Tage < Summe der Tagesanteile, werden alle Anteile gekürzt."""
        b = self.cfg["budget"]
        summe = sum(b.get("fonds_tagesanteil_eur", {}).values()) + b.get("reserve_tag_eur", 0.0)
        if not summe:
            return 1.0
        ende = datetime.fromisoformat(b["claude_ende"]).replace(tzinfo=timezone.utc).timestamp()
        tage = max(1.0, (ende - self.jetzt) / 86400)
        rest_eur = max(0.0, (self.gesamtdeckel_usd - self.z["gesamt_usd"] + self.heute_usd()) / self.fx)
        return max(0.0, min(1.0, rest_eur / tage / summe))

    def fonds_anteil_usd(self, n_fonds: int, fid: str | None = None) -> float:
        anteile = self.cfg["budget"].get("fonds_tagesanteil_eur", {})
        if fid in anteile:
            return anteile[fid] * self.fx * self.tempo_faktor()
        return self.tagesdeckel_usd / max(n_fonds, 1)

    def runden_budget_usd(self, fid: str, modell: str, art: str, stunde_utc: int) -> float:
        """Weiches Budget einer Runde: Rest des Tagesanteils, verteilt auf die noch kommenden festen Runden
        (Tiefenrunde zählt doppelt, Ereignisrunden halb), gedeckelt je Modell. Die harten Deckel prüft darf()."""
        b = self.cfg["budget"]
        rest = max(0.0, self.fonds_anteil_usd(3, fid) - self.fonds_heute_usd(fid))
        takt = b.get("takt_stunden_utc", [])
        tief = b.get("tiefenrunde_stunde_utc")
        kommend = sum(2.0 if h == tief else 1.0 for h in takt if h >= stunde_utc)
        gewicht = {"tief": 2.0, "takt": 1.0}.get(art, 0.5)
        if art in ("tief", "takt"):  # die laufende Runde ist in „kommend“ schon enthalten
            anteil = rest * gewicht / max(kommend + 0.5, gewicht)
        else:
            anteil = rest * gewicht / (kommend + gewicht)
        return min(anteil, b.get("runden_deckel_usd", {}).get(modell, anteil))

    def gesamt_erschoepft(self) -> bool:
        return self.z["gesamt_usd"] >= self.gesamtdeckel_usd

    def claude_zeit_vorbei(self) -> bool:
        ende = datetime.fromisoformat(self.cfg["budget"]["claude_ende"]).replace(tzinfo=timezone.utc).timestamp()
        return self.jetzt >= ende

    def darf(self, fid: str, n_fonds: int, geschaetzt_usd: float = 0.0, global_nur: bool = False) -> tuple[bool, str]:
        """Prüft Tages-, Fonds- und Gesamtdeckel inkl. geschätzter Kosten des nächsten Aufrufs."""
        with self._lock:
            unterwegs = sum(self._reserviert.values())
            if self.gesamt_erschoepft() or self.z["gesamt_usd"] + unterwegs + geschaetzt_usd > self.gesamtdeckel_usd:
                return False, "Gesamtbudget erschöpft"
            if self.heute_usd() + unterwegs + geschaetzt_usd > self.tagesdeckel_usd:
                return False, "Tagesbudget erschöpft"
            if not global_nur and self.fonds_heute_usd(fid) + geschaetzt_usd > self.fonds_anteil_usd(n_fonds, fid):
                return False, "Tagesanteil dieses Fonds erschöpft"
            return True, ""

    def reserviere(self, fid: str, n_fonds: int, geschaetzt_usd: float) -> tuple[bool, str]:
        """Wie darf(), hält den Worst-Case aber bis zur Buchung fest (atomar über parallele Fonds-Threads)."""
        with self._lock:
            ok, grund = self.darf(fid, n_fonds, geschaetzt_usd)
            if ok:
                self._reserviert[threading.get_ident()] = geschaetzt_usd
            return ok, grund

    def freigeben(self) -> None:
        with self._lock:
            self._reserviert.pop(threading.get_ident(), None)

    # ---- Buchung
    def buche(self, fid: str, modell: str, nutzung: dict, zweck: str = "") -> float:
        usd = kosten_usd(modell, nutzung, self.cfg)
        with self._lock:
            self._reserviert.pop(threading.get_ident(), None)
            self.z["gesamt_usd"] += usd
            self.z["tage"][self.tag] = self.heute_usd() + usd
            ft = self.z["fonds_tage"].setdefault(self.tag, {})
            ft[fid] = ft.get(fid, 0.0) + usd
            store.schreibe("budget.json", self.z)
            store.anhaengen("budget_log.jsonl", {"ts": time.time(), "fonds": fid, "modell": modell, "zweck": zweck,
                                                  "nutzung": nutzung, "usd": round(usd, 6)})
        return usd

    def bericht(self) -> dict:
        return {"heute_eur": round(self.heute_usd() / self.fx, 3), "gesamt_eur": round(self.z["gesamt_usd"] / self.fx, 3),
                "tagesdeckel_eur": self.cfg["budget"]["tagesdeckel_eur"], "gesamtdeckel_eur": self.cfg["budget"]["gesamtdeckel_eur"],
                "tempo_faktor": round(self.tempo_faktor(), 3),
                "fonds_heute_eur": {k: round(v / self.fx, 3) for k, v in self.z["fonds_tage"].get(self.tag, {}).items()}}
