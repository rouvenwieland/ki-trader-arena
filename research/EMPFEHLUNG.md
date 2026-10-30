# Empfehlung – priorisierte Umsetzungsliste (Stand 30.10.2026)

Grundlage: [RECHERCHE-2026-10.md](RECHERCHE-2026-10.md) (8 Kategorien, rund 300 Kandidaten, ~120 Endpunkte live getestet). Verworfenes: [ANHANG-verworfen.md](ANHANG-verworfen.md). Kostenpflichtiges/Eingeschränktes: [IDEEN-TRESOR.md](IDEEN-TRESOR.md).
Es wurde **nichts am Code geändert**. Die Kennungen (B1, M3 …) verweisen auf die Recherche-Datei. „Aufwand“ ist grob geschätzt: S = unter 2 h, M = halber bis ganzer Tag, L = mehrere Tage.

## 0. Zuerst: Fehler beheben (vor jeder neuen Funktion)

| # | Was | Wo | Aufwand |
|---|---|---|---|
| B1 | Polymarket-Taker-Gebühr aus `ref.gebuehr_rate` buchen: `C·rate·p·(1−p)` laut Doku, gerundet auf 5 Stellen. Regressionstest mit dem Doku-Beispiel (100 Anteile zu 0,50, Rate 0,07 → 1,75 $). DECISIONS.md korrigieren. | `arena/exchange/fees.py` | S |
| B2 | Opus-Review: Streaming, `max_tokens` ~32k, `stop_reason == "max_tokens"` als Fehler behandeln, `reports/2026-W44.md` neu erzeugen. | `arena/review.py:58` | S |
| B3 | Kronos-Band nicht mehr als p10/p90 zeigen, solange es so eng ist: entweder 32–64 Pfade (gebatcht) plus Nachskalierung aus der Trefferhistorie, oder Band aus GARCH bzw. Random Walk nehmen und Kronos nur als Richtungshinweis. | `scripts/prognosen.py`, `arena/forecast.py` | S–M |
| B4 | Reddit `.json` entfernen (403), nur RSS; echte Zeitstempel aus `<updated>` bzw. `seendate` (GDELT) lesen. | `arena/data/news.py` | S |
| B5/B6 | Cache-Lesepreis je Modell (vorher auf der Preisseite gegenprüfen), Liga-Modellnamen aktualisieren (DeepSeek, Groq-Triage `gpt-oss-20b`), Cerebras/GitHub Models als „kein Gratis-Kontingent“ markieren. | `arena/config.json` | S |

## 1. Top 10 schnelle Gewinne (hoher Nutzen, Aufwand S–M)

| Rang | Maßnahme | Warum (Beleg) | Wo | Aufwand |
|---|---|---|---|---|
| 1 | **Denkschulen + eigene Informationsdiät je Claude-Fonds** – *seit 30.10. mittags teilweise umgesetzt (Schwerpunkte, Startlisten, Überlappungs-Kennzahl); offen: Denkregeln je Schule, unterschiedliche Ereignis-Reihenfolge, Rechercheplan aus der Triage* (M1/M2 in Kat. 1, M1 in Kat. 4): Vorsichtig = Basisraten-Prognostiker, Mittel = Arbitrage/Mikrostruktur/Regeln, Aggressiv = Makro/Momentum. Ereignisse je Fonds unterschiedlich sortiert/gefiltert, Rechercheplan aus der Triage. | Direktes Gegenmittel zum beobachteten Klumpen (B7). Laut Herding-Literatur treibt die gleiche Information gleichgerichtete Wetten stärker als die Persona. | `config.json`, `prompts.py` | S |
| 2 | **Pflichtfelder für Wettmarkt-Schätzungen und Orders** (M3/M4): Abrechnungsquelle/-datum, Status quo, Basisrate, Überraschungsszenario, `p_blind` (vor Blick auf den Preis), `p_markt`, Invalidierung, stärkstes Gegenargument, `risiko_usd`, Ankerskala für Zuversicht. P(JA) und P(NEIN) getrennt abfragen gegen den Ja-Hang. | Superforecaster-Gerüst der Metaculus-Siegerbots; kostet kaum Tokens, wirkt für Claude *und* Liga. | `tools.py`, `prompts.py` | S |
| 3 | **Marktrelative Prognose-Kennzahlen:** Brier-Skill gegen Marktpreis, marktbereinigter Brier (ForecastBench: Markt kopieren = 0), Log-Score, Kalibrierungskurve, Murphy-Zerlegung, hypothetischer Gewinn gegen den Marktpreis. Schätzungen nach dem Ereignis ausfiltern. | Ohne Marktvergleich ist der Brier-Score nicht interpretierbar (Kat. 2, 4). Daten (`p_ja`, Markt-Mitte) sind schon gespeichert. | `metrics.py`, Seite | S–M |
| 4 | **Ehrliche Rangliste:** Block-Bootstrap-Konfidenzintervalle (Paket `arch`, NCSA-Lizenz), Probabilistic/Deflated Sharpe (N = Anzahl Fonds), „messbar ab Tag X“ (MinTRL), p-Wert gegen BTC Buy&Hold. | B8: Ohne das ist die Rangliste wochenlang Rauschen. Formeln in `research/skripte/eval_test.py` nachgerechnet. | `metrics.py`, `site.py` | M |
| 5 | **Reflexion bei Abrechnung + Kalibrier-Rückmeldung** (M7/M9): Haiku schreibt bei jeder geschlossenen/abgerechneten Position 2–4 Sätze Lektion (Muster: TradingAgents-Reflector); der Rundenprompt meldet JA-Überschätzung und Überkonfidenz (BIA/CON, ab n ≥ 15). | Schließt die Lernschleife, die heute nur wöchentlich (und wegen B2 gar nicht) wirkt. | `exchange`/`watcher`-Hook, `notizbuch.py`, `metrics.py` | M |
| 6 | **GARCH-Band als feste Basislinie** im Prognose-Werkzeug (Paket `arch`, ~1 s, 0,2 GB). | Im Test gleichauf mit dem Random Walk und am besten kalibriert (84 % Abdeckung) – ehrlicher als jedes Foundation-Modell. | `forecast.py` | S |
| 7 | **Deribit DVOL + Funding exakt (`interest_1h`) + Book-Summary (Basis)**. | Gleicher Adapter, ohne Schlüssel getestet; Volatilitätsregime für alle Agenten, korrekteres Funding in der Börse. | `arena/data/crypto.py`, `engine.py` | S |
| 8 | **Polymarket-/Kalshi-Orderfluss-Werkzeug:** `prices-history`, Data-API `/trades` `/holders` `/oi`; Kalshi `candlesticks` + `/markets/trades` (≥ 1 s Abstand gegen 429). | Alles ohne Schlüssel getestet; Agenten sehen, *wer* kauft und wie sich der Preis entwickelt hat. | `pm.py`, `tools.py` | M |
| 9 | **Behörden-RSS** (Fed `press_all.xml`, EZB, SEC-Presse) und Release-Termine über FRED `releases/dates`. | Einzeiler, live 200; direkt relevant für Zins-/Fed-Wettmärkte. | `news.py` | S |
| 10 | **Kontrollfonds „Immer NEIN“ und „Markt-Kopierer“** (kauft nichts, schätzt immer den Marktpreis) als Messlatten für Wettmärkte. | Bekannter Ja-Hang von LLMs; „Markt-Kopierer“ ist die Null-Linie des marktbereinigten Brier. | `benchmarks.py` | S |

## 2. Top 10 große Hebel (größerer Aufwand, potenziell großer Erkenntnis- oder Ertragsgewinn)

| Rang | Maßnahme | Warum | Aufwand |
|---|---|---|---|
| 1 | **Meta-Fonds „Schwarm der Arena“ ohne LLM** (M11): Schätzungen aller Fonds rekalibrieren → getrimmter Mittelwert → Log-Odds-Mischung mit dem Marktpreis (LLM-Gewicht anfangs ~0,3) → nur handeln, wenn Abweichung > Rundreisekosten, Größe mit ¼-Kelly. Varianten „nur Liga“ vs. „nur Claude“. | Beantwortet die Kernfrage des Projekts (hat der *Schwarm* einen Vorteil?); laut AIA Forecaster und „Wisdom of the Silicon Crowd“ die aussichtsreichste Konstruktion. 0 Tokens. | M–L |
| 2 | **Metaculus-Botturniere (FutureEval/MiniBench) als Trainings- und Messfeld** mit `Metaculus/forecasting-tools` (MIT) in einem eigenen Workflow; ergänzend FutureX. | Hunderte unabhängig bewertete Prognosen je Saison – genau die Stichprobe, die der Arena fehlt; externer Vergleich; laut Ankündigung LLM-Credits auf Antrag. Braucht ein Metaculus-Konto (Bot-Token) – Rouvens Entscheidung. | M–L |
| 3 | **Wetter-Werkzeug für Kalshi/Polymarket-Temperaturmärkte:** Open-Meteo-Ensembles (GFS/ECMWF-Mitglieder) → P(Tmax im Bracket); Abrechnung über NWS-Klimabericht (CLI) – dieselbe Quelle wie Kalshi; Rückfall NWS-Punktprognose/ECMWF Open Data (CC BY 4.0). Zwischenspeicher wegen geteiltem IP-Kontingent. | Einziger Bereich mit echtem, messbarem Informationsvorsprung gegenüber dem Markt-Durchschnittsteilnehmer; deterministisch für alle Modelle. | M |
| 4 | **Positionsgrößen-Werkzeug + Risikoschicht:** Kelly binär inkl. Gebühr, simultan über offene Wetten (Test: Summe Einzel-Kelly 0,83 vs. gemeinsam 0,72), Bruchteil je Profil, gekürzt bei schlechtem Brier; ATR/Vol-Targeting für Perps; Krypto-Beta-Cluster-Limit (BTC/ETH/SOL korrelieren 0,89–0,91); Themen-Cluster-Limit (M6); Kennzahl „Gleichlauf“ zwischen Fonds. | Größte Einzelursache für Verluste bei LLM-Tradern ist Größe/Übertrading (nof1-Lehren). | M |
| 5 | **Hyperliquid als zweite Perp-Quelle** (POST `info`: Funding/OI/Mark für ~225 Perps, L2-Buch, `predictedFundings` inkl. Binance/Bybit-Raten). Vorher ToS im Browser prüfen (Abruf war 403). `http.py` braucht `post()`. | Größtes Daten-Upgrade für Derivate; deckt die US-gesperrten Börsen legal mit ab. | M |
| 6 | **Geschichtetes Notizbuch + Policy-Gate** (M8/M10): Wichtigkeit und Zerfall je Eintragstyp; Kategorien mit ≥ 5 Verlust-Trades werden deterministisch gesperrt (nur Opus-Review darf lockern). | Lektionen gehen heute unter den letzten 40 Einträgen verloren. | M |
| 7 | **Börsen-Realismus:** verbrauchte Buchtiefe je Tick über Orders/Fonds merken (Idee aus Nautilus), Square-Root-Impact für Stops und synthetische Bücher (Aktien, PredictIt). | Schließt die größten verbliebenen Realismuslücken in `book.py`/`watcher.py`. | M |
| 8 | **Modellwahl nach dem 14.11. statistisch absichern:** Model Confidence Set statt Rangplatz; unter den nicht unterscheidbaren Besten das günstigste wählen; „Gewinn je API-€“ anzeigen. Kandidat: DeepSeek (`deepseek-flash`, laut Preisseite ~0,01 $/Runde); OpenRouter einmalig 10 $ aufladen (1000 statt 50 Anfragen/Tag) und `:free`-Modelle nach Tool-Use-Qualität (BFCL) statt Kontextlänge wählen. | Verhindert, dass ein Glückstreffer die Claude-Fonds übernimmt. | M |
| 9 | **A/B-Fonds für Designfragen** (M15) + **ein Risikomanager-Pass vor großen Orders** (M5, ein Haiku-Gegenaufruf statt langer Debatte). | Nur so lässt sich messen, ob Muster wirklich helfen („Design > Modell“, Agent Market Arena; „Debate or Vote“). Budget reicht laut Kostenanalyse (Hochrechnung 37–90 € bis 14.11.). | M |
| 10 | **Aktien/Makro auf offizielle Quellen:** Alpaca Basic (Gratis-Konto) statt Yahoo, SEC EDGAR (Form 4, 8-K, XBRL-Fundamentaldaten), FRED mit Schlüssel inkl. ALFRED-Vintages, DBnomics (EZB/Eurostat/OECD/IMF), Cboe-VIX, Finnhub-Earnings-Kalender. | Behebt die bekannte Yahoo-Drosselung; Vintages schützen vor Lookahead. Braucht Gratis-Schlüssel als Secrets. | M–L |

Ebenfalls lohnend, aber nachrangig: Bluesky (`api.bsky.app` searchPosts/Trending) und Wikimedia-Pageviews als Aufmerksamkeitssignal; lokales Sentiment mit `distilroberta-financial-news` (Apache-2.0, 0,6 s/100 Schlagzeilen – FinBERT ist CC BY-NC-SA); Dashboard mit uPlot (MIT, 22 kB) für Kalibrierungsdiagramm und Konfidenzbänder, Lightweight Charts (Apache-2.0, Logo lassen) für Kurse mit Order-Markern; `widget.html` als PWA fürs Laptop; DVOL-/optionsimplizite Wahrscheinlichkeit zur Bewertung von Krypto-Wettmärkten; Prognosemodelle billiger machen (Toto-2.0-22m oder Chronos-Bolt-small statt TimesFM 2.5 – gleiche Güte, ein Bruchteil der Zeit).

## 3. Pareto-Begründung

Die Arena will **ehrlich messen**, ob KI-Agenten einen Vorteil haben. Drei Dinge entscheiden darüber, und auf sie zielen rund 80 % des Nutzens bei rund 20 % des Aufwands:

1. **Stimmt die Messung?** (B1, B3, Kennzahlen #3/#4, Kontrollfonds #10) – Eine Börse, die Gebühren vergisst, und eine Rangliste ohne Unsicherheit machen jedes Ergebnis wertlos. Das sind fast alles S-Aufgaben.
2. **Sind die Fonds wirklich unabhängig und lernen sie?** (#1, #2, #5, B2) – Drei Klone mit derselben Wette liefern eine Stichprobe statt drei; ein Lernkreis, der nicht schließt, verschenkt das Notizbuch. Reine Prompt-/Schema-Arbeit.
3. **Wo kann ein Vorteil überhaupt entstehen?** (großer Hebel #1, #3, #4) – Die Literatur und die eigenen Tests sagen klar: nicht in Kursprognosen (TSFM ≈ Random Walk), kaum im Alleingang gegen liquide Wettmärkte; sondern in Aggregation (Schwarm + Markt), Spezialdaten (Wetter, Abrechnungsregeln) und Disziplin bei der Größe.

Bewusst **nicht** priorisiert: fremde Agenten-Frameworks (TradingAgents, CrewAI, LangGraph, Hermes) – sie kosten Budget und Gleichheit zwischen den Modellen, ihre guten Ideen sind als Muster übernehmbar; MCP-Server – eigene Werkzeuge bleiben für alle Modelle gleich und billiger; größere Prognosemodelle – kein messbarer Vorteil.

## 4. Vorgeschlagene Reihenfolge

1. **Sofort (1 Tag):** Abschnitt 0 komplett, dann schnelle Gewinne 1, 2, 6, 9, 10.
2. **Bis 14.11. (solange Claude-Budget läuft):** schnelle Gewinne 3, 4, 5, 7, 8; großer Hebel 8 (Modellwahl) muss **vor** dem 14.11. stehen; großer Hebel 9 (A/B-Fonds) ist nur sinnvoll, solange Budget da ist.
3. **November/Dezember:** große Hebel 1 (Schwarm), 3 (Wetter), 4 (Größen/Risiko), 6 (Notizbuch).
4. **Mit Oracle-Server:** große Hebel 2 (Metaculus, mehr Laufzeit/Modelle), 5 (Hyperliquid-WebSocket), 7, 10; kürzerer Wächter-Takt; lokale Modelle.

## 5. Umstiegspunkte (wann etwas Neues lohnt oder etwas aufgegeben werden sollte)

| Auslöser | Dann |
|---|---|
| ≥ 50 aufgelöste Prognosen je Fonds | Platt-Rekalibrierung je Fonds einschalten; vorher nur anzeigen, nicht anwenden. Pauschales „Extremisieren“ ist umstritten – nur, wenn die Kalibrierungskurve Unterkonfidenz zeigt. |
| Kalibrierungsdaten des Schwarms ≥ 100 Fragen | LLM-Gewicht in der Markt-Mischung aus Daten fitten statt fest 0,3. |
| Ein Fonds/Muster liegt im Konfidenzintervall nach ≥ 60 Tagen nicht über „Markt-Kopierer“ bzw. Buy&Hold | Als „kein messbarer Vorteil“ markieren, Ressourcen umschichten – nicht weiter tunen (Überanpassung). |
| Prognose-Werkzeug: rollende Abdeckung des 10–90-Bands < 70 % oder Pinball schlechter als GARCH über 4 Wochen | Modell aus dem Werkzeug nehmen (gilt sofort für Kronos, B3). |
| Open-Meteo/GDELT liefern auf Actions regelmäßig 429 | Zwischenspeicher/Rohdateien (GDELT-GKG, ECMWF Open Data) bzw. Umzug dieser Abrufe auf den Oracle-Server. |
| Claude-Budget erschöpft oder 14.11. | Nachfolger per Model Confidence Set (großer Hebel 8), nicht nach Rangplatz; DeepSeek als günstiger Kandidat. |
| Wächter-Laufzeit > 10 min oder 15-min-Takt zu grob (z. B. Wetter-/Sportmärkte am Abrechnungstag) | Umstieg auf Oracle-ARM-Server (24 GB): WebSockets (Polymarket, Hyperliquid, Bluesky-Jetstream), kürzerer Takt, lokale Modelle (laut Schätzung 8–14B Q4 machbar, Prompt-Verarbeitung ist der Engpass – ungeprüft). |
| `data/` > ~200 MB | Verläufe als Parquet auslagern (Release-Assets oder separater Zweig); vorher nicht nötig (Pages-Grenzen unkritisch). |
| Rouven will echte Teilnahme an Turnieren | Metaculus-Bot-Konto anlegen (Rouvens Entscheidung, Konto/ToS) – einziger Punkt, der ein externes Konto braucht. |

## 6. Was Rouven entscheiden oder tun müsste

- Gratis-Schlüssel als Secrets, falls gewünscht: FRED, Alpaca (Paper), Finnhub, EIA, Metaculus-Bot-Token; optional OpenRouter 10 $ einmalig.
- ToS selbst im Browser prüfen, bevor eingebaut wird: Hyperliquid (für Bots 403), PredictIt (möglicherweise Scraping-/Kommerzverbot – betrifft den **bestehenden** Adapter), Polymarket-Datenklausel, Smarkets, Cboe-CDN.
- Hinweis zu Lizenzen beim Anzeigen auf der Seite: DefiLlama (keine Wiederveröffentlichung ohne Erlaubnis), Coin Metrics Community (CC BY-NC), alternative.me (Quelle neben den Daten), Open-Meteo/ECMWF (CC BY 4.0, Quellenangabe), FRED-Serien mit Copyright-Vermerk.
