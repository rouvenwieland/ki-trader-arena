# KI-Trader-Arena – Plan (30.10.2026)

Ziel: Herausfinden, ob KI-Agenten mit allen verfügbaren Daten und Werkzeugen im spekulativen Handel (Wettmärkte, Krypto, Aktien/ETFs, Derivate) einen Vorteil haben – ehrlich gemessen, nur Papierhandel. Bau als Cloud-Session (Cloud-Guthaben), Betrieb erst GitHub, später ggf. Server.

## Entscheidungen aus dem Interview
| Punkt | Entscheidung |
|---|---|
| Märkte | Wettmärkte, Krypto, Aktien/ETFs, Derivate (Optionen, Perpetuals) |
| Betrieb | erst GitHub Actions (öffentliches Repo), später Oracle-Gratis-Server, wenn es sich bewährt |
| Modell | Anthropic-API (200 €), „Gas geben“ bis ca. 14.11.; danach übernimmt automatisch das beste Gratis-Modell der Liga |
| Takt | ereignisgesteuert |
| Fonds | 3 unabhängige Claude-Agenten (Vorsichtig / Mittel / Aggressiv, je 10.000 €) + Modell-Liga: so viele weitere Modelle wie möglich, je ein Fonds |
| Anzeige | Live-Webseite (GitHub Pages), Laptop-Dashboard (Windows-Widget), Wochenbericht im Vault |
| Echtgeld | vorbereitet (Broker-Schnittstelle), aktiv nur nach ausdrücklichem Ja |
| Quellen | alles Kostenlose und rechtlich Unbedenkliche: Nachrichten, Reddit/Social, eigene Websuche, Lagedaten |

## Die zwei Reel-Tools
- **„Palantir-Nachbau“ = OSIRIS** (Reel 14.10., Lagedashboard mit 3D-Globus, Feeds: OpenSky, USGS, NASA FIRMS, NOAA, GDACS, OpenSanctions, MarineTraffic …). Repo nicht verifiziert; die README nennt zusätzlich ein Angriffs-Toolkit (Port-Scan, Schwachstellen-Scanner) → **nicht installieren**. Wir nutzen stattdessen dieselben öffentlichen Feeds direkt.
- **Google-Forecast-Modell: nicht in der Reel-Inbox gefunden** (weder Notion noch Vault). Gemeint ist sehr wahrscheinlich **TimesFM** (Google Research, Apache-2.0): Zeitreihe rein, Prognose mit Unsicherheitsband raus. Wird eingebaut.

## Architektur
1. **Wächter** (GitHub Action, alle 10–15 min, ohne KI, kostenlos): sammelt Daten, bewertet alle Portfolios zum Marktwert, führt Stop-Loss/Take-Profit aus und erzeugt **Ereignisse**: Kurssprung, Nachricht zu gehaltener Position, Markt schließt in < 24 h, neue Fehlbewertung/Arbitrage, Volatilitätsausbruch, große Wettmarkt-Bewegung.
2. **Entscheider** (Action, nur bei Ereignis + eine feste Runde täglich): jeder Fonds-Agent bekommt denselben Daten-Schnappschuss, recherchiert bei Bedarf selbst und gibt Orders mit Begründung, Zuversicht und Ausstiegsplan ab. Haiku sichtet vor, Sonnet entscheidet, Opus macht die wöchentliche Strategie-Überprüfung.
3. **Papier-Börse** (Kern, streng realistisch – Lehre aus den Arbitrage-Scannern): Gebühren je Plattform, Spread, Füllung gegen echte Orderbuchtiefe, Slippage, Finanzierungskosten, Optionen zu Deribit-Markpreisen, echte Abrechnungsregeln, Liquidation bei Hebel. Jede Entscheidung mit Zeitstempel **vor** dem Ergebnis gespeichert (nur Vorwärtstest; Rücktests mit LLMs sind durch deren Trainingswissen verfälscht).
4. **Broker-Schnittstelle**: heute PaperBroker; vorbereitet für Alpaca-Paper, Kalshi-Demo, später echt – echte Ausführung nur nach Rouvens Ja, mit harten Grenzen.
5. **Agenten-Rahmen**: Hermes Agent (Nous Research, Open Source) wie gewünscht – wird zuerst geprüft, ob er kopflos in GitHub Actions läuft; sonst schlanke eigene Schleife mit Anthropic-Tool-Use. Der Weitblick-Ablauf (mehrere Thesen, Gegenargument, Pareto) steckt in der Agenten-Anweisung.
6. **Speicher**: Zustand als JSON/Parquet im Repo (wie bei den Scannern), Gelerntes je Agent als „Notizbuch“ (Thesen, Fehler, Lektionen).

## Daten und Werkzeuge (alles gratis)
- Wettmärkte: Polymarket, Kalshi, PredictIt, Manifold (öffentliche APIs).
- Krypto/Derivate: Binance, Bybit, OKX, Deribit (Kurse, Orderbücher, Funding, Optionen, Open Interest).
- Aktien/ETFs: Yahoo/Stooq, Alpaca-Daten (Gratis-Konto), SEC-EDGAR-Meldungen, Earnings-Kalender.
- Makro: FRED, EZB, Wirtschaftskalender.
- Nachrichten/Stimmung: GDELT, RSS großer Medien, Reddit-Feeds (öffentlich), Google Trends; Websuche des Agenten (Anthropic Web Search, aus dem API-Guthaben).
- Lagedaten (OSIRIS-Feeds): GDACS, USGS, NASA FIRMS, NOAA, OpenSanctions, OpenSky.
- Prognose: **TimesFM** (Google) und **Kronos** (Open-Source-Modell speziell für Kurs-Kerzen) auf CPU in der Action; Ergebnisse mit Unsicherheitsband als Werkzeug für die Agenten.
- Recht: nur öffentliche, kostenlose Quellen, Nutzungsbedingungen und Abfragelimits einhalten, nichts hinter Logins, keine Umgehung von Sperren.

## Modell-Liga (je ein Fonds, mittleres Risiko, gleiche Regeln)
Claude Sonnet (3 Hauptfonds), Gemini Flash (gratis), OpenRouter-Gratismodelle (z. B. DeepSeek, Qwen, Llama, gpt-oss), Cerebras, Mistral (gratis), Kimi/Moonshot (falls Schlüssel), Groq nur zum Vorsichten (Tokenlimit zu klein). Dazu Vergleichsfonds ohne KI: Buy & Hold BTC, S&P 500, 60/40, Zufallsaffe, sowie punkt/modell_roh aus dem Wahrscheinlichkeits-Scanner.

## Messung (ehrlich)
Rendite, maximaler Rückgang, Sharpe/Sortino, Trefferquote, Brier-Score für Wettmarkt-Prognosen, Kosten je Fonds (API-€), Vergleich gegen Buy & Hold. Erwartung realistisch: Die meisten KI-Trader schlagen Buy & Hold nicht; aussagekräftig wird es nach mehreren Wochen.

## Budget
Anthropic-API bis ca. 14.11. ausreizen (Tagesdeckel im Code, z. B. 12 €/Tag, harter Stopp). Danach automatischer Wechsel der Claude-Fonds auf das beste Gratis-Modell der Liga (Wechsel wird markiert). GitHub Actions im öffentlichen Repo: unbegrenzte Gratis-Minuten.

## Anzeige
- Live-Webseite (GitHub Pages, cinematisch gestaltet): Fondsverläufe, Positionen, jede Entscheidung mit Begründung, Liga-Tabelle.
- Laptop-Dashboard: Kachel im Windows-Widget-Dashboard (liest das JSON der Webseite).
- Wochenbericht: sonntags im Vault (lokale Routine zieht die Daten).

## Was Rouven tun muss
1. API-Schlüssel als GitHub-Secrets hinterlegen (ich lege ein Skript bereit, das sie aus deinen Umgebungsvariablen überträgt – Schlüssel sehe ich nie).
2. Optional: Gratis-Konto bei Alpaca (Papierhandel) für Aktien-Daten.

## Bauphasen (Cloud-Session)
1. Repo, Papier-Börse mit Gebühren/Orderbuch, Wächter, Datenquellen Wettmärkte + Krypto → läuft.
2. Claude-Fonds (3 Agenten) + Ereignis-Logik + Budget-Wächter → läuft (Ziel: wenige Tage, damit das Guthaben bis 14.11. genutzt wird).
3. Modell-Liga + Vergleichsfonds.
4. Aktien/ETFs, Derivate, TimesFM/Kronos, Nachrichten/Reddit/Lagedaten.
5. Webseite, Laptop-Kachel, Wochenbericht, Opus-Strategie-Review.
Jede Phase mit Tests; Abnahme durch einen unabhängigen Prüfer-Agenten.
