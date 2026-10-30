# STATUS (Stand 30.10.2026, nach der ersten Nachtschicht)

## Erledigt (läuft auf GitHub Actions, auf `main`)

**Phase 1 – Börse, Daten, Wächter**
- [x] Python-Projekt (uv, pytest), 50+ Tests (Börse, Gebühren, Füllung, Abrechnung, Liquidation, Budget-Stopp, Ereignisse, Routing, Agentenschleife).
- [x] Papier-Börse: Orderbuch-Füllung mit Teilfüllung, Slippage, Gebühren je Plattform, Funding, Liquidation per Docht, Stop-Loss/Take-Profit, Abrechnung der Wettmärkte (Ja/Nein/Teilwert/Storno, PredictIt-Gewinngebühr), Optionsverfall, Positionsgrenzen je Risikoprofil.
- [x] Datenadapter: Polymarket, Kalshi, PredictIt, Manifold (nur lesend); Coinbase/Kraken Spot, Deribit Perps (linear USDC) + Optionen + Funding; Yahoo (Aktien, s. u.); RSS/Reddit/GDELT; USGS/GDACS/NOAA; FRED.
- [x] Wächter-Workflow (alle 15 min, Concurrency-Gruppe, `contents: write`), speichert Zustand als JSON/JSONL in `data/` (append-only Verläufe, Entscheidung vor Ergebnis).
- [x] Ereignisse: Kurssprung, Nachricht zu Position, Markt schließt < 24 h, Wettmarkt-Bewegung, Volatilitätsausbruch, Fehlbewertung (Kreuz-Plattform, Funding).

**Phase 2 – Claude-Fonds**
- [x] Drei Claude-Fonds (Vorsichtig/Mittel/Aggressiv, je 10.000 €, eigene Persönlichkeit, Notizbuch).
- [x] Entscheider-Workflow (Ereignis per `workflow_dispatch` + täglich 13:17 UTC), Haiku-Triage → Sonnet-Runde mit Tool-Use und Websuche, Weitblick-Prompt, Mindestaufwand, Orders mit Begründung/Zuversicht/Ausstiegsplan.
- [x] Budget-Stopp im Code (Tages-/Fonds-/Gesamtdeckel, Worst-Case-Vorausschau), Umschaltung auf bestes Liga-Modell ab 14.11. oder bei erschöpftem Budget (inkl. Markierung).
- [x] Hermes Agent geprüft → eigene Schleife (Begründung in DECISIONS.md).
- [x] **Live-Test auf Actions bestanden:** Claude-Fonds liefen real (Sonnet 5.5, Caching, ~0,04 $/Runde in der ersten Fassung).

**Phase 3 – Liga**
- [x] Liga-Fonds je Modell mit Schlüssel (Gemini, DeepSeek, Moonshot/Kimi, Cerebras, Mistral, OpenAI, OpenRouter-`:free` dynamisch); Groq bewusst nicht als Fonds (Tokenlimit), Vergleichsfonds: BTC Buy&Hold, S&P-ETF, 60/40, Zufallsaffe; Rangliste in Seite und `status.json`.

**Phase 4**
- [x] Aktien/ETFs über Yahoo (best effort), Derivate (Perps long/short mit Hebel, Optionen long), Prognose-Werkzeug mit **TimesFM 2.5** (Apache-2.0) und **Kronos** (MIT) auf CPU im Workflow `prognosen.yml` (Live-Test auf Actions erfolgreich, Ergebnisse in `data/prognosen.json`), Nachrichten/Stimmung, Makro (FRED), Lagedaten (USGS, GDACS, NOAA).

**Phase 5**
- [x] Webseite `docs/index.html` (dunkel/cinematisch, ohne externe Abhängigkeiten): Verläufe, Rangliste, Positionen, Entscheidungen mit Begründung, Tagebuch, Notizbuch, Ereignisse, Kosten, Kennzahlen (Rendite, Max-Drawdown, Sharpe, Trefferquote, Brier).
- [x] `docs/status.json` (Schema v1) für das Laptop-Widget.
- [x] Wöchentliches Opus-Strategie-Review (`review.yml`, sonntags) → `reports/`.

## Offen / braucht Rouven

1. **GitHub Pages einschalten** (einmalig): *Settings → Pages → Source: GitHub Actions*. Aus der Cloud-Session war das nicht per API möglich (Proxy sperrt den Pages-Pfad). Bis dahin ist die Seite nur über `docs/` im Repo sichtbar; `status.json` ist auch roh über `raw.githubusercontent.com` abrufbar.
2. **Schlüssel prüfen:** Die per `secrets-setzen.cmd` gesetzten Secrets enthielten ein unsichtbares BOM (U+FEFF) – der Code bereinigt das jetzt automatisch, das Skript wurde korrigiert. Gesetzt waren zuletzt (nach Läufen erkennbar): Anthropic, DeepSeek, Gemini, Moonshot, OpenAI. Fehlen: Cerebras, Mistral, OpenRouter (und optional `NASA_FIRMS_KEY`) – die Fonds melden „wartet auf Schlüssel“.
3. Einige Liga-Schlüssel liefern Fehler (Quota/Modellname), siehe Fonds-Status auf der Seite; Modellnamen stehen in `arena/config.json` und lassen sich dort ändern.
4. Optional: Alpaca-Gratis-Konto für bessere Aktien-Daten.

## Bekannte Grenzen (ehrlich)

- **Aktien:** Yahoo drosselt Cloud-IPs teilweise; Stooq ist hinter einer Anti-Bot-Prüfung (nicht umgangen). Ohne Kurs starten SPY-/60-40-Vergleichsfonds erst, wenn die US-Börse offen ist und Yahoo antwortet – sie starten also später als die übrigen Fonds. Rangvergleiche dann bitte über „Rendite seit eigenem Start“ lesen.
- **PredictIt:** nur Top-of-Book bekannt → synthetische, konservative Tiefe; Ausgang schwer per API ablesbar (Position bleibt dann offen).
- **Manifold:** Spielgeld, als USD behandelt – nur Signalquelle.
- **Perps:** linear (USDC), isolierte Marge, Funding mit aktueller 8-h-Rate je Tick; Optionen nur gekauft.
- **Stichprobe:** In den ersten Wochen ist die Rangliste Rauschen. Der Wächter sieht nur alle 15 min; Intra-Tick-Dochte werden über 1-Minuten-Kerzen berücksichtigt, aber nicht jedes Ereignis.
- **GitHub-Cron** ist ungenau (Verzögerungen von Minuten sind normal); die Seite zeigt „Stand vor X min“.
- **Repo-Wachstum:** `data/` wächst um grob 100–200 kB/Tag (Kursverlauf + Equity). Später komprimieren/auslagern.
- Kein Punkt/Modell-roh-Fonds aus dem Wahrscheinlichkeits-Scanner (nicht in diesem Repo vorhanden).
- NASA FIRMS und OpenSanctions brauchen Schlüssel/Lizenz und sind nur optional (FIRMS) bzw. nicht eingebunden.
- Die „unabhängige Abnahme durch einen Prüfer-Agenten“ aus dem Plan steht noch aus.

## Nächste Schritte
1. Pages aktivieren, Secrets ergänzen.
2. Nach 1–2 Tagen: Fonds-Status auf der Seite prüfen (Fehler je Liga-Modell), Modellnamen anpassen.
3. Prüfer-Agent über Börse/Abrechnung laufen lassen (Abnahme).
4. Alpaca-Daten (Aktien), Oracle-Server für kürzere Takte.
