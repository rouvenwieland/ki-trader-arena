# Ideen-Tresor (Stand 30.10.2026)

**Was das ist:** Das Gegenstück zu `research/RECHERCHE-2026-10.md`. Dort steht, was kostenlos, legal und auf GitHub Actions/Oracle-Gratis-Server nutzbar ist. Hier steht, was **mindestens eine dieser Bedingungen verletzt**: Es kostet Geld, braucht andere Infrastruktur (GPU, VPS, Kolokation, Rechner rund um die Uhr), braucht Konten/KYC/Lizenzen oder ist rechtlich bzw. regulatorisch heikel (AGB, Geo-Sperren, Lizenzpflichten, Datenschutz).
**Nichts davon wird eingebaut.** Der Tresor dient nur dazu, das Potenzial zu kennen und später zu entscheiden.

**Spielregeln dieses Dokuments**
- Reine Recherche und Einordnung. **Keine Rechts- oder Steuerberatung**, keine Anleitungen zum Umgehen von Sperren, AGB oder Gesetzen.
- Potenzial 1–5 = realistischer Nutzen für *dieses* Projekt (Privatanleger, KI-Agenten mit Sekunden-Latenz, Vorwärtstest im Papierhandel), nicht für einen Hedgefonds. „5/5 als Vorsicht“ markiert Leitplanken, die nicht in der Rangliste stehen.
- Belege stehen als URLs direkt im Eintrag. **„(ungeprüft)“** heißt: nicht an einer Primärquelle bestätigt (oft Drittquelle oder Seite nicht abrufbar). Preise ändern sich häufig – vor jeder Entscheidung auf der Anbieterseite gegenprüfen.
- Recherche-Hinweis: Das Firecrawl-Kontingent war während der Recherche schnell erschöpft; danach lief die Suche über WebSearch/WebFetch. Deshalb stammen viele Preise aus Drittquellen und sind entsprechend markiert. Einige Primärquellen waren gesperrt (Kalshi Member Agreement 429, Smarkets-AGB 403, Metaculus/Good Judgment 403).
- Kürzel im Bereich „Kommerzielle KI-Dienste“/„GPU“: **B1** = nicht gratis (über das 200-€-Anthropic-Budget hinaus), **B2** = läuft nicht auf GitHub Actions (CPU, Laufzeitlimit), **B3** = braucht weitere Infrastruktur.

---

## Kurzübersicht: Top 10 nach Potenzial je Aufwand

Gewichtet: hohes Potenzial bei niedrigen Kosten und wenig Aufwand zuerst. Das heißt nicht „einbauen“ – nur „als Erstes anschauen, falls der Tresor geöffnet wird“.

| # | Idee | Pot. | Kosten (Stand) | verletzt | lohnt sich, wenn … |
|---:|---|---:|---|---|---|
| 1 | **Dauerhafter WebSocket-Sammler** (Polymarket-Markt-WS öffentlich; Kalshi-WS nur mit Konto; Deribit-WS) auf Oracle Free / Raspberry Pi / Hetzner | 4 | 0 € (Pi ≈ 13–18 €/Jahr Strom; Hetzner CX23 5,49 €/Monat seit 15.06.2026) | andere Infrastruktur (Dauerprozess) | der Wächter Ereignisse zwischen den 15-min-Läufen verpasst oder echte Orderbuch-Historie für die Papier-Börse gebraucht wird. Nutzen ist Vollständigkeit, **nicht** Latenz. |
| 2 | **Metaculus FutureEval** (KI-Prognose-Wettbewerb, Bot-Konto) | 4 | Teilnahme gratis + LLM-Kosten; Preispool 50.000 $ je Saison (Herbst 2026 unbestätigt) | Konto | die Arena-Agenten saubere Wahrscheinlichkeiten liefern – dann gibt es eine externe, kalibrierte Messlatte (Brier) ohne Echtgeld. |
| 3 | **The Odds API** (Buchmacher-Konsens als Benchmark für Kalshi/Polymarket-Sportmärkte) | 4 | 500 Credits/Monat gratis; 30 $ (20K), 59 $, 119 $, 249 $ | Konto/Key, Lizenz (Rohquoten nicht veröffentlichen) | Sportmärkte ein Schwerpunkt werden; Gratis-Tarif zuerst. Steht fast an der Grenze zu „machbar“. |
| 4 | **CoinGlass API** (börsenübergreifend Funding, OI, Liquidationen) | 4 | Hobbyist 29 $/Monat, Startup 79 $ (ungeprüft, Preissenkung 28.06.2026) | kostenpflichtig, Lizenz nur persönlich | Perps-Fonds dauerhaft laufen und Funding/OI-Signale im **Vorwärtstest** mehr als 29 $/Monat bringen. |
| 5 | **xAI Grok-API mit X-Suche** (einziger bezahlbarer, AGB-konformer X-Echtzeitzugang) | 4 | grok-4.3 1,25/2,50 $ pro Mio. Tokens, X Search 5 $/1.000 Posts; ≈ 50 $/Monat bei stündlichem Lauf (Schätzung) | kostenpflichtig, Konto | Wettmärkte zu Politik/Krypto/Promi-Themen dominieren und Nachrichten dort zuerst auf X auftauchen. Günstiger als die offizielle X-API (≈ 0,005 $/Post-Read, Basic/Pro 2026 abgeschafft). |
| 6 | **Interactive Brokers (Ireland)** – Paper-API = Live-API | 4 | Xetra Tiered 0,05 % (min. 1,25 €, max. 29 €); Marktdaten ≈ 10 $/Monat (bei genug Kommission erlassen) | Konto/KYC, Echtgeld | eine Aktien-/ETF-/Options-Strategie im Papierhandel nach Kosten positiv ist **und** Rouven ausdrücklich Ja sagt. Realistischster Echtgeld-Weg aus DE. |
| 7 | **Kraken** (Spot unter MiCA, Perps unter MiFID II über CySEC-Tochter) | 4 | 30 Tage gebührenfrei für neue EWR-Futures-Kunden; reguläre Sätze ungeprüft | Konto/KYC, Echtgeld, Angemessenheitstest | eine Perp-Strategie nach Gebühren/Funding positiv ist und mit ≤ 10x (realistisch 1–3x) funktioniert. |
| 8 | **Massive (ehem. Polygon.io) / Tiingo / FMP** als stabile Aktienquelle | 3 | Massive Starter 29 $, Tiingo Power 30 $ bzw. 300 $/Jahr, FMP ab 19 $ (jährl.) | kostenpflichtig, Lizenz „Individual/Internal use only“ | Yahoo die Cloud-IPs weiter drosselt (bekannte Grenze laut STATUS.md) und SPY/60-40-Fonds deshalb Läufe verlieren. Rohkurse dann nicht auf der öffentlichen Seite zeigen. |
| 9 | **Perplexity Sonar/Search, Exa oder Parallel.ai** als zweite Suchquelle | 3 | Perplexity Search 5 $/1.000; Exa 4–15 $/1.000; Parallel Search 1–5 $/1.000 | kostenpflichtig | die Anthropic-Websuche nach dem 14.11. wegfällt und die Gratis-Modelle eine eigene Suche brauchen. |
| 10 | **Outcome-basiertes RL für Prognosen** (eigenes 8B-Modell auf aufgelösten Wettmarkt-Fragen) | 3 | ≈ 40–200 $ GPU-Miete je Experiment (8B, Schätzung; A100 ≈ 1,19–1,79 $/h) | GPU, andere Infrastruktur | die Arena mehrere hundert aufgelöste Fragen mit Zeitstempel gesammelt hat – dann gibt es leckfreie Trainingsdaten. Einzige Feintuning-Richtung, die direkt auf Prognosequalität zielt. |

**Knapp dahinter:** Quiver Quantitative (300 $/Jahr, MCP inklusive), ORATS Delayed (99 $/Monat, implizite Volatilität), Betfair Historical Data (BASIC gratis), Opus-Klasse als Agent nach dem 14.11. (≈ 100 $/Monat je Agent bei stündlichem Lauf, Schätzung).

**Hoch bewertet, aber aus Deutschland faktisch blockiert:** Betfair-Exchange-API (4/5 als Benchmark, Live-Key einmalig 499 £) – laut Betfair-Support ist die Exchange für DE/AT nicht verfügbar. Polymarket (DE „close-only“), Kalshi (DE-Zulassung ungeprüft, nach GGL-Auffassung unerlaubtes Glücksspiel), Liquiditäts-Rewards beider Plattformen.

**Eigentlich „machbar“ (gratis, legal) – an die Haupt-Recherche weiterreichen:** Kenneth-French-Faktordaten (4/5), Polymarket-Wal-Tracking über öffentliche On-Chain-/API-Daten (3/5), Hyperliquid-Wal-Positionen über die öffentliche API (3/5, ungeprüft), 13F über EDGAR, Metaculus/INFER als Prior, ECMWF-Echtzeitdaten (seit 01.10.2025 CC-BY-4.0) und NWS-Klimaberichte für Kalshi-Wettermärkte.

## Querschnitts-Erkenntnisse

1. **Lizenz vs. öffentliches Repo.** Fast alle bezahlbaren Privatlizenzen („Individual“, „Internal use only“, „No redistribution or display“) verbieten die öffentliche Anzeige von Rohdaten – und das Repo, die GitHub-Pages-Seite **und die Actions-Logs** sind öffentlich. Bezahldaten wären nur flüchtig im Job nutzbar; veröffentlicht würden höchstens eigene abgeleitete Entscheidungen, und auch das nur, wenn die AGB es erlauben.
2. **Latenz ist für dieses Projekt fast wertlos.** Ein LLM-Agent braucht Sekunden pro Entscheidung, geplante Actions laufen frühestens alle 5 Minuten. Kolokation, AWS Tokio, Profi-Newsfeeds, Sportdaten-Feeds lohnen sich nicht. Polymarket bremst Latenz-Arbitrage seit 07.01.2026 zusätzlich mit dynamischen Taker-Gebühren; BLS-Medien-Lockups sind seit 2020 abgeschafft.
3. **Deutschland ist für Wettmärkte und Wettbörsen der Engpass**, nicht Geld oder Technik: Polymarket gesperrt (GGL-Warnung 05.09.2025, gemeinsames Statement von neun EU-Aufsichten 19.06.2026), Betfair-Exchange für DE nicht verfügbar, dazu 5,3 % Wettsteuer auf den Einsatz bei Sportwetten. Für Aktien/ETFs (IBKR, Trading 212) und Krypto (Kraken, Coinbase) gibt es dagegen regulierte Wege.
4. **Steuern (Einordnung):** Die Verlustverrechnungsgrenze für Termingeschäfte (§ 20 Abs. 6 EStG) wurde mit dem JStG 2024 gestrichen; Krypto nach § 23 EStG steuerfrei nach einem Jahr, Freigrenze unter 1.000 €; Steuerbehandlung von Prognosemarkt-Gewinnen unklar; DAC8 (KStTG) gilt seit 01.01.2026. Details im Abschnitt Echtgeld.
5. **Leitplanken (5/5 als Vorsicht):** Personenbezogene Social-Posts nicht roh im öffentlichen Repo speichern (DSGVO – betrifft schon heutige Reddit-RSS-Daten; besser nur Aggregate). Signale, Copy-Trading oder Fondsergebnisse **Dritten als Handlungsempfehlung anbieten** kann erlaubnispflichtig sein (§ 32 KWG; ohne Erlaubnis strafbar nach § 54 KWG). Eigenhandel auf eigene Rechnung über einen Broker gilt i. d. R. als erlaubnisfrei (BaFin-Merkblatt nicht im Wortlaut geprüft).
6. **Forschungsstand als Messlatte:** Bei ForecastBench liegen Superforecaster bei Brier ≈ 0,086, das beste LLM bei ≈ 0,103; Gleichstand wird für etwa Mai 2027 hochgerechnet (Details im KI-Abschnitt). Rücktests mit LLMs bleiben durch Trainingswissen verfälscht – jede Paper-Zahl (z. B. Trading-R1) ersetzt keinen Vorwärtstest.

Die Detailabschnitte unten sind nach dem höchsten Potenzial im Bereich sortiert, die Einträge innerhalb jedes Bereichs absteigend nach Potenzial; nicht bewertete Hintergrund-Einträge (z. B. Steuern, Wettsteuer, KWG, GPU-Marktüberblick) stehen am Ende des Bereichs.

---

## Gesamtliste nach Potenzial

Alle bewerteten Ideen, absteigend nach Potenzial (bei Gleichstand in Reihenfolge des Bereichs). „1–2/5“ zählt als 1,5. Details im jeweiligen Bereich weiter unten.

| Pot. | Idee | Bereich | verletzt |
|---:|---|---|---|
| 4/5 | CoinGlass (API) | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz (Hobbyist und Startup nur für den persönlichen Gebrauch). |
| 4/5 | xAI Grok-API mit X-Suche (x_search) | Kommerzielle KI-Dienste | B1. |
| 4/5 | ForecastBench, Metaculus FutureEval, Prophet Arena: was LLMs als Prognostiker können | Kommerzielle KI-Dienste |  |
| 4/5 | Interactive Brokers (IBKR, Ireland Limited) | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC (Angemessenheitstest für Derivate) und laufende Kosten (Marktdaten). Rechtlich gibt es kein … |
| 4/5 | Kraken (Spot + MiFID-Derivate EU) | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC, Echtgeld (siehe Eintrag) |
| 4/5 | Betfair Exchange API (Live-Key) | Wettbörsen-Daten | Betfair-Konto mit KYC. Live-Key gegen Gebühr. Betfair ist in Deutschland nur eingeschränkt verfügbar … |
| 4/5 | The Odds API | Wettbörsen-Daten | Konto und API-Key nötig. Historische Quoten nur bezahlt. |
| 4/5 | Kenneth-French-Datenbibliothek (gratis, zum Vergleich) | Akademische Datensätze | Keine. Eine Quellenangabe ist üblich. |
| 4/5 | Dauerhafte WebSocket-Feeds statt 15-min-Polling (Polymarket, Kalshi, Deribit) | Echtzeit- und Niedriglatenz-Infrastruktur | andere Infrastruktur (dauerhaft laufender Prozess, GitHub Actions taugt dafür nicht). Bei Kalshi … |
| 4/5 | Agentic-Forecasting-Wettbewerb: Metaculus FutureEval (ehem. AI Benchmark / Q-Cups) | Kreative Hebel | Konto (Metaculus-Bot-Account). Läuft aber auch auf GitHub Actions (Metaculus stellt dafür ein Template … |
| 3/5 | Massive (ehem. Polygon.io) | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz („Individual use only“). |
| 3/5 | Tiingo | Kostenpflichtige Marktdaten | Konto (der Free-Plan braucht schon einen Key), Lizenz, bei „Power“ zusätzlich kostenpflichtig. |
| 3/5 | EODHD (EOD Historical Data) | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 3/5 | Financial Modeling Prep (FMP) | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 3/5 | Amberdata / Laevitas (Krypto-Derivate, Deribit-Optionen) | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 3/5 | ORATS | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz (Individual). |
| 3/5 | Quiver Quantitative | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz (nicht kommerziell). |
| 3/5 | Benzinga Pro | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 3/5 | Perplexity Sonar API / Search API | Kommerzielle KI-Dienste | B1. |
| 3/5 | Exa | Kommerzielle KI-Dienste | B1. |
| 3/5 | Parallel.ai (Search, Task, Monitor, FindAll) | Kommerzielle KI-Dienste | B1. |
| 3/5 | Kosten für Opus-Klasse-Modelle als Agent (Anthropic) | Kommerzielle KI-Dienste | B1, sobald das 200-€-Budget weg ist. |
| 3/5 | Lightning Rod Labs (Foresight-Modelle, Outcome-RL) | Kommerzielle KI-Dienste | B1/B2/B3 (eigenes Hosting eines 14B–32B-Modells braucht eine GPU, kommerzieller Zugang kostet). |
| 3/5 | Outcome-basiertes RL für Prognosen (selbst trainieren) | GPU-Training und eigene Modelle | B2/B3. |
| 3/5 | Was der Oracle-Gratis-Server leisten kann und was nicht | GPU-Training und eigene Modelle |  |
| 3/5 | Trading 212 (API) | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC, Echtgeld (siehe Eintrag) |
| 3/5 | Coinbase | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC, Echtgeld (siehe Eintrag) |
| 3/5 | X/Twitter API (offiziell, Pay-per-use) | Social-Daten hinter Logins | Kostenpflichtig, Developer-Konto und Guthaben nötig. |
| 3/5 | Grok (xAI-API) als indirekter X-Zugang | Social-Daten hinter Logins | Kostenpflichtig, xAI-Konto nötig. |
| 3/5 | Truth Social | Social-Daten hinter Logins | Es gibt keine offizielle API. Suche, Hashtags und die meisten Profile sind nur mit Login erreichbar. … |
| 3/5 | Polymarket-Wal-Tracking auf Polygon (On-Chain) | MEV und On-Chain | Eigentlich keine. Bezahlt sind nur Komfort-Tools (siehe Copy-Trading). |
| 3/5 | Hyperliquid: Positionen öffentlicher Wale | MEV und On-Chain | Rohdaten öffentlich. Coinglass-API-Tarife sind kostenpflichtig (Preise ungeprüft). HyperDash konnte nicht … |
| 3/5 | Betfair Historical Data | Wettbörsen-Daten | Betfair-Konto nötig, ADVANCED und PRO kostenpflichtig. |
| 3/5 | Pinnacle als "scharfe Linie" | Wettbörsen-Daten | **Bestätigt:** Die API ist seit 23.7.2025 für die Öffentlichkeit geschlossen. Zugang gibt es nur noch für … |
| 3/5 | Hetzner Cloud VPS (nach den Preiserhöhungen 2026) | Echtzeit- und Niedriglatenz-Infrastruktur | kostenpflichtig, andere Infrastruktur. |
| 3/5 | Oracle Cloud Always Free (Kontrast / geplanter Umstieg) | Echtzeit- und Niedriglatenz-Infrastruktur | andere Infrastruktur, Konto (Kreditkarte zur Verifizierung). |
| 3/5 | Heimserver / Raspberry Pi 24/7 (Stromkosten DE) | Echtzeit- und Niedriglatenz-Infrastruktur | andere Infrastruktur (eigene Hardware, Heimnetz). |
| 3/5 | Wetterdaten für Kalshi-Wettermärkte (gratis vs. kommerziell) | Kreative Hebel | Bezahldaten sind kostenpflichtig. Gratis-Daten verletzen nichts (außer Rechenaufwand für … |
| 3/5 | Metaculus / INFER Gemeinschaftsprognosen (gratis, Kontrast) | Kreative Hebel | keine (allenfalls Konto/API-Token). Gehört eigentlich nicht in den Tresor, steht hier als Kontrast. |
| 2/5 | Koyfin | Kostenpflichtige Marktdaten | kostenpflichtig, Konto. |
| 2/5 | Finnhub (Premium) | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 2/5 | Intrinio | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 2/5 | Databento | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz (Börsenlizenzen, Personal vs. Commercial). |
| 2/5 | Glassnode (Advanced / Professional) | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 2/5 | CryptoQuant | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 2/5 | Nansen | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 2/5 | Arkham Intelligence | Kostenpflichtige Marktdaten | kostenpflichtig (bzw. Wallet mit USDC), API nur auf Antrag. |
| 2/5 | Dune (Plus) | Kostenpflichtige Marktdaten | kostenpflichtig (Plus), Konto. |
| 2/5 | Unusual Whales | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 2/5 | Stimmungs- und News-Analytics: RavenPack / Bigdata.com | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 2/5 | Santiment | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 2/5 | LunarCrush | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 2/5 | PolymarketAnalytics | Kostenpflichtige Marktdaten | kostenpflichtig (Premium), Konto. |
| 2/5 | Oddpool | Kostenpflichtige Marktdaten | kostenpflichtig, Konto. |
| 2/5 | Nixtla TimeGPT (TimeGPT-2.1) | Kommerzielle KI-Dienste | B1 (nach der Testphase kostenpflichtig). |
| 2/5 | Tavily | Kommerzielle KI-Dienste | B1 nur oberhalb des Gratis-Kontingents. 1.000 Credits pro Monat sind gratis, ohne Kreditkarte; eine … |
| 2/5 | Firecrawl | Kommerzielle KI-Dienste | B1 oberhalb von 1.000 Gratis-Credits pro Monat (1 Credit pro Seite, Suche 2 Credits pro 10 Treffer). |
| 2/5 | Brave Search API | Kommerzielle KI-Dienste | B1 nur oberhalb des Freibetrags. Der frühere Gratis-Plan ist entfallen; stattdessen gibt es 5 $ … |
| 2/5 | OpenAI Deep Research API (o3-deep-research / o4-mini-deep-research) | Kommerzielle KI-Dienste | B1. |
| 2/5 | Gemini Deep Research (Interactions API) | Kommerzielle KI-Dienste | B1. Das Gratis-Kontingent der Gemini-API gilt hier nicht (ungeprüft). |
| 2/5 | LoRA/QLoRA-Feintuning eines Finanz- oder Trading-LLM (Qwen3 / Llama) | GPU-Training und eigene Modelle | B2/B3 fürs Training. Die Inferenz eines 4–8B-Modells im GGUF-Format geht auf CPU (Actions: langsam, aber … |
| 2/5 | Fin-R1 (SUFE, 7B) | GPU-Training und eigene Modelle | B2 ist bei der Inferenz grenzwertig (7B auf Actions-CPU: langsam, Q4 etwa 4–5 GB RAM; ungeprüft). Ein … |
| 2/5 | Trading-R1 | GPU-Training und eigene Modelle | B2/B3 (RL-Training braucht eine GPU). |
| 2/5 | Zeitreihen-Basismodelle feintunen (TimesFM 2.5, Chronos-2, Moirai, Kronos) | GPU-Training und eigene Modelle | B2/B3 fürs Training. Die Inferenz der feingetunten Gewichte läuft weiter auf Actions-CPU. |
| 2/5 | Alpaca | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC. |
| 2/5 | Bitpanda (und One Trading) | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC, Echtgeld (siehe Eintrag) |
| 2/5 | Bybit (Bybit EU) | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC, Echtgeld (siehe Eintrag) |
| 2/5 | Deribit (Krypto-Optionen) | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC, Echtgeld (siehe Eintrag) |
| 2/5 | twitterapi.io und ähnliche Drittanbieter | Social-Daten hinter Logins | Kostenpflichtig. Vor allem holt der Anbieter die Daten nach eigener Darstellung nicht über die offizielle … |
| 2/5 | Telegram: Bot-API vs. MTProto-Client-API | Social-Daten hinter Logins | Login und Konto nötig. Die **Bot-API** liest einen Kanal nur, wenn der Bot dort Mitglied ist, praktisch … |
| 2/5 | Reddit Data API (OAuth) | Social-Daten hinter Logins | OAuth-Login nötig. Seit der **Responsible Builder Policy** (Ende 2025) braucht jeder neue OAuth-Token eine … |
| 2/5 | StockTwits | Social-Daten hinter Logins | Der API-Zugang ist eingeschränkt oder nur nach Freigabe zu haben. Die AGB erlauben, Konten mit nicht … |
| 2/5 | eToro CopyTrader | Copy-Trading und Signale | Konto mit KYC. Automatisches Auslesen ohne API widerspricht den AGB (ungeprüft). |
| 2/5 | Polymarket-Wal-Folgen: Polywhaler, PolyTrack und Co. | Copy-Trading und Signale | Kostenpflichtig im Premium-Tarif. |
| 2/5 | Kongress-Trades: Unusual Whales, Quiver Quantitative, Autopilot, NANC/KRUZ | Copy-Trading und Signale | Komfort-Daten kostenpflichtig, Autopilot braucht ein Brokerkonto (US-fokussiert). |
| 2/5 | 13F-Folgen (Hedgefonds-Positionen) | Copy-Trading und Signale | Nur die Komfort-Tools kosten Geld, die Rohdaten nicht. |
| 2/5 | OddsJam | Wettbörsen-Daten | Kostenpflichtig, Konto nötig. |
| 2/5 | WRDS (Wharton Research Data Services) als Zugangsplattform | Akademische Datensätze | Nur für Angehörige lizenzierter Institutionen. Nutzung "for academic and non-commercial research only". … |
| 2/5 | CRSP (Aktienrenditen, survivorship-frei) | Akademische Datensätze | Lizenz nötig, akademisch über WRDS, kommerziell direkt über CRSP per Anfrageformular. |
| 2/5 | OptionMetrics IvyDB | Akademische Datensätze | Lizenz. |
| 2/5 | I/B/E/S (Analystenschätzungen, LSEG) | Akademische Datensätze | Lizenz. |
| 2/5 | Eigene Polygon-Node vs. bezahlte RPCs (Alchemy, QuickNode, Helius) | Echtzeit- und Niedriglatenz-Infrastruktur | kostenpflichtig ab höherem Volumen. Eigene Node bedeutet andere Infrastruktur. |
| 2/5 | Tick-Datenarchiv: Tardis.dev | Echtzeit- und Niedriglatenz-Infrastruktur | kostenpflichtig. |
| 2/5 | Zeitreihen-Datenbank: TimescaleDB / ClickHouse Cloud | Echtzeit- und Niedriglatenz-Infrastruktur | kostenpflichtig (Cloud), andere Infrastruktur. |
| 2/5 | Polymarket Liquidity Rewards & Maker Rebates | Kreative Hebel | Echtgeld, Konto, **rechtlich: DE ist auf Polymarkets Sperrliste** ( VPN-Umgehung verstößt gegen die ToS. |
| 2/5 | Kalshi Liquidity Incentive Program (LIP) | Kreative Hebel | Echtgeld, Konto (US-KYC), rechtlich. |
| 2/5 | Ereignis-Auflösungs-Rennen (Wirtschaftsdaten, Wahlen) | Kreative Hebel | andere Infrastruktur (sekundengenauer Poller), für echten Vorteil Echtgeld/Konto. |
| 2/5 | Superforecaster-Dienst: Good Judgment Inc. FutureFirst | Kreative Hebel | kostenpflichtig, Konto/Vertrag. |
| 2/5 | Builder-Programme: Polymarket Builders / Kalshi Builders | Kreative Hebel | Konto. Rechtlich: Nutzer aus DE dürften nicht handeln (Polymarket-Geoblock). Ein Builder muss den Geoblock … |
| 1,5/5 | Kalshi aus Deutschland | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC, Echtgeld (siehe Eintrag) |
| 1,5/5 | Hyperliquid / dYdX (DEX-Perps) | Echtgeld-Zugang, Broker und Regulierung (DE) | rechtlich unklar (kein EU-Register), Echtgeld |
| 1/5 | Bloomberg Terminal / LSEG Workspace (ehem. Refinitiv Eikon) | Kostenpflichtige Marktdaten | kostenpflichtig, Vertrag/Konto, Lizenz (Einzelplatz, keine Weitergabe), andere Infrastruktur … |
| 1/5 | Kaiko | Kostenpflichtige Marktdaten | kostenpflichtig, Vertrag, Lizenz. |
| 1/5 | Token Terminal | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 1/5 | Cheddar Flow / Tradytics | Kostenpflichtige Marktdaten | kostenpflichtig, Konto. |
| 1/5 | Cboe DataShop | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 1/5 | Satellitenbilder (Planet, Privateer/Orbital Insight, SpaceKnow) | Kostenpflichtige Marktdaten | kostenpflichtig, Vertrag, Lizenz, andere Infrastruktur (Bildverarbeitung). |
| 1/5 | Kreditkarten-/Transaktionsdaten (Bloomberg Second Measure, Consumer Edge, YipitData) | Kostenpflichtige Marktdaten | kostenpflichtig, Vertrag, Lizenz. |
| 1/5 | Geodaten/Fußverkehr (Placer.ai, SafeGraph/Advan) | Kostenpflichtige Marktdaten | kostenpflichtig, Vertrag, Lizenz. |
| 1/5 | Jobdaten (Thinknum, LinkUp, Revelio Labs) | Kostenpflichtige Marktdaten | kostenpflichtig, Vertrag, Lizenz. |
| 1/5 | Alexandria Technology | Kostenpflichtige Marktdaten | kostenpflichtig, Vertrag, Lizenz. |
| 1/5 | StockTwits API | Kostenpflichtige Marktdaten | Konto/Freigabe, ggf. kostenpflichtig, Lizenz. |
| 1/5 | The TIE | Kostenpflichtige Marktdaten | kostenpflichtig, Vertrag, Lizenz. |
| 1/5 | Newsquawk | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, Lizenz. |
| 1/5 | Dow Jones Newswires | Kostenpflichtige Marktdaten | kostenpflichtig, Vertrag, Lizenz. |
| 1/5 | Tree of Alpha / Tree News | Kostenpflichtige Marktdaten | kostenpflichtig, Konto, andere Infrastruktur (dauerhaft laufender Websocket-Client). |
| 1/5 | BloombergGPT (nur als Referenz) | GPU-Training und eigene Modelle | alles. |
| 1/5 | Polymarket (international) aus Deutschland | Echtgeld-Zugang, Broker und Regulierung (DE) | rechtlich/Geo (hart). |
| 1/5 | Polymarket US (QCX LLC, ehem. QCEX) | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC und Geo. Das Angebot richtet sich an US-Nutzer. |
| 1/5 | Betfair Exchange | Echtgeld-Zugang, Broker und Regulierung (DE) | Geo. Laut Betfair-Support steht die Wettbörse Kunden in Deutschland bzw. Österreich „bedauerlicherweise … |
| 1/5 | Smarkets | Echtgeld-Zugang, Broker und Regulierung (DE) | voraussichtlich Geo/rechtlich. Eine primäre Länderliste habe ich nicht gefunden (ungeprüft). Ohne deutsche … |
| 1/5 | Matchbook | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC, Echtgeld (siehe Eintrag) |
| 1/5 | Binance | Echtgeld-Zugang, Broker und Regulierung (DE) | Konto/KYC, Echtgeld (siehe Eintrag) |
| 1/5 | Discord | Social-Daten hinter Logins | Ein Bot-Konto funktioniert nur auf Servern, deren Admin den Bot hinzufügt. **Self-Bots**, also … |
| 1/5 | DEX-Arbitrage (atomar, zwischen Pools/DEXs) | MEV und On-Chain | Echtes Kapital, Wallet und Gas nötig. Mit Gratis-Daten oder Papierhandel nicht abbildbar. |
| 1/5 | Liquidations-Bots (Aave/Compound) | MEV und On-Chain | Echtes Kapital (oder Flash-Loans), Wallet, private Order-Flow-Kanäle. |
| 1/5 | Backrunning über Flashbots MEV-Share | MEV und On-Chain | Echtes Kapital, Wallet, Bundle-Infrastruktur. |
| 1/5 | Solana / Jito-Bundles | MEV und On-Chain | Echtes Kapital und Wallet, Infrastruktur. |
| 1/5 | MEV-Infrastruktur (eigene Nodes, Latenz) | MEV und On-Chain | Kostenpflichtig. Läuft nicht auf GitHub Actions, das mit Minuten-Takt und ohne dauerhafte Prozesse dafür … |
| 1/5 | Bitget / Bybit Copy-Trading | Copy-Trading und Signale | Konto und KYC. **Bitget:** laut Tracker keine MiCA-Lizenz, Deutschland seit 16.1.2026 für Neuanmeldungen … |
| 1/5 | Compustat (Fundamentaldaten) | Akademische Datensätze | Lizenz, Uni über WRDS oder kommerziell über S&P. |
| 1/5 | TAQ (NYSE Trade and Quote) | Akademische Datensätze | Lizenz. |
| 1/5 | Polymarket-Nähe: AWS eu-west-2 (London) / eu-west-1 (Dublin) | Echtzeit- und Niedriglatenz-Infrastruktur | kostenpflichtig, andere Infrastruktur. Echter Handel wäre aus DE ohnehin geo-gesperrt (Help-Center listet DE: |
| 1/5 | AWS Tokyo (ap-northeast-1) nahe Binance / Singapur nahe Bybit | Echtzeit- und Niedriglatenz-Infrastruktur | kostenpflichtig, andere Infrastruktur. Binance/Bybit-Konto mit DE-Regulierung (MiCA) ist ein eigenes Thema … |
| 1/5 | Equinix NY4 / LD4 Kolokation inkl. Deribit-Kolokation | Echtzeit- und Niedriglatenz-Infrastruktur | kostenpflichtig, andere Infrastruktur, Konto/Vertrag, oft institutioneller Status. |
| 1/5 | Lizenzierte Echtzeit-Wirtschaftsdaten (Bloomberg ECO, MNI, Need to Know News) | Kreative Hebel | kostenpflichtig, Vertrag/Konto, meist kolokierte Infrastruktur. |
| 1/5 | Sportdaten-Feeds (Sportradar, Genius Sports) | Kreative Hebel | kostenpflichtig, Vertrag/Konto. |
| 1/5 | Experten-Netzwerke (GLG & Co.) | Kreative Hebel | kostenpflichtig, Konto (institutionelle Kunden), rechtlich heikel. |
| 0,5/5 | Telegram-Signalgruppen (Betrugsrisiko) | Copy-Trading und Signale |  |
| 0/5 | Dome API | Kostenpflichtige Marktdaten | entfällt. |
| 0/5 | Sandwich-Angriffe (Einordnung, nicht verfolgen) | MEV und On-Chain |  |

---

## Wettbörsen-Daten

### Betfair Exchange API (Live-Key)
- **Links:** https://developer.betfair.com/, https://support.developer.betfair.com/hc/en-us/articles/115003864531-Are-there-any-costs-associated-with-API-access
- **Was es bringt:** Echte Wettbörsen-Quoten mit Volumen. Für Sport- und Politikmärkte ein exzellenter Benchmark für Kalshi und Polymarket.
- **Potenzial: 4/5.** Ein liquider Exchange-Preis ist die beste "Wahrheit" für Wahrscheinlichkeiten. Der Delayed-Key reicht für Benchmarks oft schon.
- **Verletzte Bedingung:** Betfair-Konto mit KYC. Live-Key gegen Gebühr. Betfair ist in Deutschland nur eingeschränkt verfügbar (Status 2026 ungeprüft).
- **Kosten:** Ein **Delayed App Key** ist kostenlos (verzögerte Preise). Der **Live App Key** kostet einmalig **499 £**, abgebucht vom Betfair-Konto (Stand der Betfair-Hilfeseite, abgerufen 10/2026). Kommerzielle Datennutzung ist separat gebührenpflichtig.
- **Aufwand:** Mittel.
- **Rechtslage/Risiko:** Mit Konto im erlaubten Land gering. Die Nutzung von Betfair-Daten in einem öffentlichen Repo ist durch die Lizenz eingeschränkt (Details ungeprüft), daher nur aggregierte Vergleiche veröffentlichen.
- **Lohnt sich, wenn …** Sportmärkte auf Kalshi oder Polymarket ein Schwerpunkt werden und man ein Betfair-Konto legal führen kann. Erst mit Delayed-Key testen.

### The Odds API
- **Link:** https://the-odds-api.com/
- **Was es bringt:** Quoten von über 100 Buchmachern, darunter laut Liste Pinnacle in der EU-Region und Betfair. Historische Snapshots ab 2020 gibt es in den Bezahltarifen. Vergleichsseiten melden 2026 allerdings "No Pinnacle" (widersprüchlich, ungeprüft).
- **Potenzial: 4/5.** Ein günstiger, legaler und gut dokumentierter Konsens-Benchmark für Sportmärkte auf Kalshi und Polymarket. Der Gratis-Tarif passt zu GitHub Actions.
- **Verletzte Bedingung:** Konto und API-Key nötig. Historische Quoten nur bezahlt.
- **Kosten (10/2026):** Gratis 500 Credits pro Monat. **20K: 30 $/Monat**, 100K: 59 $, 5M: 119 $, 15M: 249 $. Ein Abruf kostet Märkte × Regionen Credits, historische Abrufe kosten das Zehnfache.
- **Aufwand:** Gering.
- **Rechtslage/Risiko:** Gering. Die Weiterveröffentlichung von Rohquoten im Repo regeln die AGB (ungeprüft).
- **Lohnt sich, wenn …** der Gratis-Tarif bereits genug für einen täglichen Vergleich "Sportbuch-Konsens vs. Kalshi-Preis" liefert. Das ist der beste Kandidat dieser Kategorie und steht fast an der Grenze zu "machbar".

### Betfair Historical Data
- **Link:** https://historicdata.betfair.com/
- **Was es bringt:** Historische Exchange-Preise zum Backtesten von Sport-Agenten.
- **Potenzial: 3/5.** Der Gratis-Tarif BASIC (1-Minuten-Intervalle, letzter gehandelter Preis, kein Volumen) reicht für Kalibrierungs-Checks.
- **Verletzte Bedingung:** Betfair-Konto nötig, ADVANCED und PRO kostenpflichtig.
- **Kosten:** BASIC gratis. Laut Preisübersicht ca. **69 £ (ADVANCED)** bzw. **230 £ (PRO, 50-ms-Takt)** pro Sport und Monat Datenzeitraum. Mai 2015 bis April 2016 ist kostenlos (Preisstand ungeprüft für 2026). Quelle: https://betfair-datascientists.github.io/data/usingHistoricDataSite/
- **Aufwand:** Mittel.
- **Rechtslage/Risiko:** Gering. Weiterveröffentlichung der Rohdaten ist verboten (ungeprüft im Detail).
- **Lohnt sich, wenn …** man Sportmarkt-Agenten historisch kalibrieren will. Mit BASIC anfangen.

### Pinnacle als "scharfe Linie"
- **Links:** https://github.com/pinnacleapi/pinnacleapi-documentation, https://arbusers.com/access-to-pinnacle-api-closed-since-july-23rd-2025-t10682/
- **Was es bringt:** Pinnacle gilt als der Buchmacher mit der effizientesten Linie und ist der klassische Benchmark für faire Wahrscheinlichkeiten.
- **Potenzial: 3/5.** Als Benchmark ideal, aber nicht mehr direkt zugänglich.
- **Verletzte Bedingung:** **Bestätigt:** Die API ist seit 23.7.2025 für die Öffentlichkeit geschlossen. Zugang gibt es nur noch für ausgewählte High-Value-Bettor, kommerzielle Partner sowie akademische und Pregame-Handicapping-Projekte auf Antrag per E-Mail an api@pinnacle.com. Drittanbieter wie pinnapi, pinnodds oder TheRundown verkaufen Pinnacle-Feeds. Woher die Daten stammen, ist ungeprüft.
- **Kosten:** Direkt nur auf Antrag. TheRundown mit Echtzeit ab 399 $/Monat (2026), Pinnacle-Spezial-Feeds ungeprüft.
- **Aufwand:** Gering bis mittel.
- **Rechtslage/Risiko:** Ein akademischer Antrag ist legal. Drittanbieter-Feeds haben eine unklare Herkunft (Scraping?), also Graumarkt-Risiko wie bei X.
- **Lohnt sich, wenn …** das Projekt als Hobby- oder Forschungsprojekt einen akademischen Antrag stellen kann. Einen Versuch per E-Mail wäre es wert.

### OddsJam
- **Link:** https://oddsjam.com/subscribe
- **Was es bringt:** +EV- und Arbitrage-Tools, die inzwischen ausdrücklich auch Kalshi und Polymarket abdecken. Dazu "Tail the world's top traders" und eine Odds-API für Firmen.
- **Potenzial: 2/5.** Für Privatleute teuer. Nutzer auf Reddit berichten gemischt, teils von Verlusten (anekdotisch).
- **Verletzte Bedingung:** Kostenpflichtig, Konto nötig.
- **Kosten (10/2026):** **199,99 $/Monat** (Pregame), **499,99 $/Monat** (In-Game), 449,99 $/Monat (Top-Trader folgen). Der erste Monat ist rabattiert. API-Preise auf Anfrage.
- **Aufwand:** Gering.
- **Rechtslage/Risiko:** Gering. Ein Bonus-/Arbitrage-Fokus kann zu Kontolimits bei Buchmachern führen (allgemein bekannt).
- **Lohnt sich, wenn …** nicht für die Arena. The Odds API liefert die Rohdaten für einen Bruchteil.

---

## Kommerzielle KI-Dienste

Stand der Recherche: 30.10.2026. Die Preise stehen in USD, so wie die Anbieter sie angeben. Für die Umrechnung in Euro gilt grob 1 $ ≈ 0,85–0,95 € (ungeprüft, Kurs schwankt).
Hier steht nur, was man kennen sollte. Eingebaut wird davon nichts.
Wichtiger Grundsatz für alle Punkte: Rücktests mit LLMs sind durch Trainingswissen verfälscht. Ein Nutzen zeigt sich nur im Vorwärtstest der Arena, und eine Paper-Behauptung ersetzt keine eigene Vorwärtsmessung.
Projektbedingungen, an denen jede Idee gemessen wird:
(B1) gratis bzw. aus dem 200-€-Anthropic-Budget bis 14.11., danach Gratis-Modelle;
(B2) läuft auf GitHub Actions (CPU, kein GPU, Laufzeitlimit pro Job);
(B3) keine weitere Infrastruktur.

### xAI Grok-API mit X-Suche (x_search)
- **Link:** https://docs.x.ai/developers/pricing
- **Was es bringt:** Modelle mit eingebauten Werkzeugen für Websuche **und X-Suche** über Posts, Profile und Threads. Gerade bei Polymarket-Themen wie Politik, Krypto oder Promi-Ereignissen bewegen sich die Kurse oft zuerst wegen X-Posts. Bei ForecastBench lag die externe Einreichung von Grok 4.20 (Preview) auf Platz 2 hinter den Superforecastern (https://forecastingresearch.substack.com/p/llms-are-closing-the-gap-on-human).
- **Potenzial: 4/5.** Die X-Echtzeitsuche ist eine Quelle, die keiner der anderen Dienste hat, und sie passt genau zu Wettmärkten. Das ist der Kandidat mit dem höchsten „Informationsvorsprung“. Einschränkungen: Profis an Polymarket lesen X ebenfalls, und auf X kursieren viele Falschinformationen.
- **Verletzt:** B1.
- **Kosten (Preisseite docs.x.ai, abgerufen Okt. 2026):**
  - grok-4.7/4.6: 2 $/6 $ pro Mio. Tokens (unter 200k Prompt-Tokens).
  - grok-4.3 und grok-4.20: 1,25 $/2,50 $.
  - Batch 20 % günstiger.
  - Werkzeuge: Web Search 5 $/1.000 Aufrufe, **X Search 5 $/1.000 Posts bzw. 10 $/1.000 Profile**.
  - Beispiel: 1 Lauf pro Stunde mit 3 X-Suchen und 20k Tokens bei grok-4.3 kostet etwa 0,015 $ + 0,05 $ ≈ 0,07 $ (eigene Rechnung, Annahmen ungeprüft). Das sind etwa 50 $ pro Monat.
- **Aufwand:** gering (OpenAI-kompatibel, Tools in der Responses-API).
- **Recht/Risiko:** Bei X-Inhalten auf die xAI-/X-AGB achten, also nicht massenhaft speichern oder weiterveröffentlichen. Für Agenten, die automatisch auf Gerüchte reagieren, besteht Manipulationsrisiko.
- **Lohnt sich, wenn:** die Vorwärtsdaten zeigen, dass die Arena bei schnell drehenden Polymarket-Märkten (Politik, Krypto) zu spät kommt. Dann zuerst einen Agenten mit X-Suche gegen einen ohne laufen lassen.

### ForecastBench, Metaculus FutureEval, Prophet Arena: was LLMs als Prognostiker können
- **Links:** https://forecastingresearch.substack.com/p/llms-are-closing-the-gap-on-human · https://forecastingresearch.substack.com/introducing-the-brier-index · https://www.lesswrong.com/posts/wZBbDqzfBjYG58CxK/futureeval-spring-results-pros-beat-bots-but-the-gap-is · https://arxiv.org/abs/2510.17638
- **Erkenntnisse:**
  - **ForecastBench:** Superforecaster liegen bei Brier 0,086, das beste LLM bei 0,103 (Abstand ca. 0,017). Grok 4.20 und das Cassi-Ensemble liegen gleichauf auf Platz 2. Die Hochrechnung auf Parität ergibt Mai 2027 (95 %-KI: April 2026 bis Mai 2028). In der Ausgabe von 2025 standen GPT-4.5 bei 0,101 und Superforecaster bei 0,081.
  - **Metaculus FutureEval (Jan.–Apr. 2026):** 173 Bots auf 297 Fragen. Die Profis liegen weiter vorn, aber der Abstand ist „nahezu weg“; zwei Bots schlugen knapp einen der Profis.
  - **Prophet Arena (ICLR 2026):** Kalshi-Live-Fragen, frei von Kontamination. 81 % davon sind Sport. Frühe Ergebnisse zeigen LLMs etwa auf Marktniveau, die Autoren warnen aber selbst vor „Raten“.
- **Bedeutung fürs Projekt:** Ein Modell, das nur „so gut wie der Markt“ ist, verdient nach Gebühren und Spread nichts. Edge entsteht eher bei schlecht gehandelten Nischenmärkten oder durch schnellere Information. Benchmarks wie Prophet Arena messen bereits „economic value“; diese Metrik sollte die Arena übernehmen.
- **Potenzial: 4/5** als Messlatte und Methodenquelle, nicht als Werkzeug.
- **Kosten:** Lesen ist gratis. Eine eigene Bot-Teilnahme bei Metaculus FutureEval ist möglich, es gibt Preisgelder; dann zahlt man aber die eigenen API-Kosten.
- **Lohnt sich, wenn:** die Arena-Agenten stabil laufen. Dann einen Agenten zusätzlich bei Metaculus einreichen, das ist ein kostenloser externer Vorwärtstest.

### Perplexity Sonar API / Search API
- **Link:** https://docs.perplexity.ai/docs/getting-started/pricing
- **Was es bringt:** Antworten mit Quellenangaben aus der Websuche (Sonar, Sonar Pro, Sonar Reasoning Pro, Sonar Deep Research). Daneben gibt es eine reine Search API, die Rohtreffer mit Seitentext für das eigene Modell liefert.
- **Potenzial: 3/5.** Aktuelle Nachrichten sind für Wettmärkte der wichtigste Eingang. Allerdings hat das Projekt schon die Anthropic-Websuche, der Mehrwert wäre also vor allem der Preis und eine zweite Quelle.
- **Verletzt:** B1.
- **Kosten (Doku, Okt. 2026):**
  - Search API: 5 $/1.000 Anfragen, „fast“ 1 $/1.000; bis zu 5 Queries pro Anfrage zählen als eine Einheit.
  - Sonar: 1 $/1 $ pro Mio. Tokens plus Gebühr pro Anfrage.
  - Sonar Pro: 3 $/15 $ plus 5–14 $/1.000 Anfragen, je nach Kontextgröße.
  - Deep Research: 2 $/8 $ plus Citation-, Reasoning- und Suchgebühren; ein Drittanbieter nennt etwa 0,41 $ pro Abfrage.
  - Quellen: https://www.activepieces.com/blog/perplexity-sonar-api-cost-per-search-2026-guide · https://openrouter.ai/perplexity/sonar-pro-search
- **Aufwand:** gering (OpenAI-kompatible API).
- **Recht/Risiko:** Die Abo-Guthaben der Consumer-App gelten nicht für die API. Daten fließen in die USA.
- **Lohnt sich, wenn:** die Arena die Anthropic-Websuche (10 $/1.000) nicht mehr bezahlen kann und billige Rohtreffer an ein Gratis-Modell gehen sollen. „Fast“ für 1 $/1.000 ist eine der günstigsten Optionen.

### Exa
- **Link:** https://exa.ai/pricing · https://exa.ai/docs/admin/pricing
- **Was es bringt:** eine neuronale Suche über einen eigenen Index mit Highlights, Volltext und einem Modus „Deep“ für mehrstufige Recherche. Sie eignet sich gut für „finde Artikel ähnlich zu …“ und für Nischenquellen.
- **Potenzial: 3/5.** Das ist eine gute Quelle für Agenten. Ob sie für Prognosen besser ist als die Anthropic-Suche, ist unbelegt.
- **Verletzt:** B1.
- **Kosten (Preisseite, Stand Okt. 2026):** Lite 4 $/1.000, Auto 7 $/1.000, Deep 12–15 $/1.000, Inhalte 1 $/1.000 Seiten, zusätzliche Treffer über 10 kosten 1 $/1.000 (https://www.activepieces.com/blog/exa-30-search-api-pricing-and-rate-limits-2026). Ein Gratis-Kontingent für den Einstieg gibt es (Höhe ungeprüft).
- **Aufwand:** gering.
- **Recht/Risiko:** Standard-SaaS-AGB. Die Treffer enthalten Textauszüge Dritter, deshalb die Inhalte nicht weiterveröffentlichen.
- **Lohnt sich, wenn:** die Suchkosten pro Agent-Lauf der größte Posten werden. Exa Lite ist etwa 2,5-mal billiger als die eingebaute Suche bei Anthropic/OpenAI (10 $/1.000).

### Parallel.ai (Search, Task, Monitor, FindAll)
- **Link:** https://parallel.ai/pricing · https://docs.parallel.ai/getting-started/pricing
- **Was es bringt:** Search für Agenten; eine Task-API für tiefe Web-Recherche mit Zitaten, Begründung und **Konfidenz** pro Feld; eine Monitor-API, die bei neuen Ereignissen zu einer Abfrage anstößt. Für Wettmärkte interessant ist eine „Monitor“-Abfrage pro offenem Markt.
- **Potenzial: 3/5.** Monitor und strukturierte Recherche passen gut zu Polymarket/Kalshi-Fragen. Die Preise steigen aber bei den tiefen Stufen schnell.
- **Verletzt:** B1.
- **Kosten (Preisseite, Okt. 2026):**
  - Search: Turbo/Fast 1 $/1.000, Basic/Advanced 5 $/1.000.
  - Task: Lite 5 $, Base 10 $, Core 25 $, Pro 100 $, Ultra 300 $ … bis Ultra8x 2.400 $ pro 1.000 Anfragen; das sind 0,005–2,40 $ pro Anfrage.
  - Monitor: 0,003–0,01 $ pro Anfrage.
- **Aufwand:** mittel (asynchrone Tasks, Webhooks; passt schlecht zu kurzen Actions-Jobs, geht aber per Polling).
- **Recht/Risiko:** SOC2, US-Dienst.
- **Lohnt sich, wenn:** man pro Markt eine laufende Nachrichtenüberwachung will, statt bei jedem Lauf neu zu suchen. Dann ist Monitor billiger als wiederholte Suchen.

### Kosten für Opus-Klasse-Modelle als Agent (Anthropic)
- **Link:** https://platform.claude.com/docs/en/about-claude/pricing
- **Was es bringt:** Die stärksten Claude-Modelle versprechen bessere Begründungen und eine sauberere Kalibrierung.
- **Potenzial: 3/5.** Bei ForecastBench schrumpft der Abstand zwischen Modellgenerationen, aber gerade die besten Systeme sind Agenten mit Suche und Ensembles, keine einzelnen Großmodelle. Ein Opus-Agent pro Markt wird schnell teuer.
- **Verletzt:** B1, sobald das 200-€-Budget weg ist.
- **Kosten (Preisseite, abgerufen 30.10.2026, pro Mio. Tokens Input/Output):**
  - Opus 5.5: 4 $/20 $, Cache-Treffer 0,20 $, Batch 2 $/10 $.
  - Opus 5/4.x: 5 $/25 $.
  - Sonnet 5.5: 2 $/10 $.
  - Haiku 5.5: 0,10 $/0,50 $ (bis 100k Prompt).
  - Fable 5.1: 10 $/50 $.
  - Batch-API halbiert die Preise. Neuere Modelle zählen etwa 30 % mehr Tokens für denselben Text (neuer Tokenizer). Die Websuche kostet laut Exa-Vergleich 10 $/1.000 Suchen (https://exa.ai/blog/best-web-search-tools-for-ai-agents).
  - Beispielrechnung (eigene, ungeprüfte Annahmen): Ein Agent-Lauf mit 30k Input (davon 20k gecacht) und 3k Output bei Opus 5.5 kostet etwa 0,04 $ + 0,004 $ + 0,06 $ ≈ 0,11 $, mit 3 Suchen etwa 0,14 $. Bei 24 Läufen pro Tag sind das 3,40 $ pro Tag, also rund 100 $ pro Monat für einen Agenten.
- **Aufwand:** keiner (läuft schon).
- **Recht/Risiko:** Budgetrisiko. Ein Ausgabelimit in der Console setzen.
- **Lohnt sich, wenn:** ein Opus-Agent im Vorwärtstest den Sonnet- oder Haiku-Agenten über mindestens 100 aufgelöste Märkte im Brier klar schlägt. Sonst lieber Haiku 5.5 mit Batch und Ensembles einsetzen.

### Lightning Rod Labs (Foresight-Modelle, Outcome-RL)
- **Link:** https://huggingface.co/LightningRodLabs · Paper https://arxiv.org/abs/2505.17989
- **Was es bringt:** eine Firma, die LLMs mit RL auf echten Ausgängen zu Prognostikern trainiert. Laut eigenen Angaben landet Foresight-32B in ForecastBench und ProphetArena weit vorne; Foresight-v3 soll im März 2026 Platz 1 bei ProphetArena (Brier) belegt haben. Im Paper erreicht ein 14B-Modell mit RL eine Genauigkeit auf Frontier-Niveau und eine bessere Kalibrierung, zum Teil trainiert mit Polymarket-Daten.
- **Potenzial: 3/5.** Das ist methodisch das spannendste Feld für Wettmärkte. Die Benchmark-Behauptungen stammen aber vom Hersteller (unabhängig ungeprüft). Ob es eine öffentliche, bezahlte API gibt, ist offen (ungeprüft).
- **Verletzt:** B1/B2/B3 (eigenes Hosting eines 14B–32B-Modells braucht eine GPU, kommerzieller Zugang kostet).
- **Kosten:** ungeprüft. Die Gewichte auf HF prüfen (Lizenz, Größe). Selbst hosten kostet etwa 0,34–1,99 $/h GPU (siehe unten).
- **Aufwand:** hoch.
- **Recht/Risiko:** Lizenz der Gewichte vor jeder Nutzung auf der HF-Modellkarte prüfen.
- **Lohnt sich, wenn:** eine bezahlbare API oder ein Modell mit offener Lizenz unter 15B erscheint, das auf CPU per llama.cpp läuft.

### Nixtla TimeGPT (TimeGPT-2.1)
- **Link:** https://www.nixtla.io/docs/introduction/timegpt_subscription_plans · https://github.com/Nixtla/nixtla
- **Was es bringt:** ein gehostetes Zeitreihen-Basismodell mit Prognoseintervallen und Anomalie-Erkennung, per Python-SDK in drei Zeilen nutzbar. Es wäre ein Gegenstück zu TimesFM/Kronos, ohne dass man selbst rechnen muss.
- **Potenzial: 2/5.** Für Kerzen-Daten ist kein Vorsprung gegenüber TimesFM 2.5/Chronos-2 belegt, die man gratis auf CPU betreibt. Finanzzeitreihen liegen nahe am Random Walk, deshalb bringt ein weiteres Basismodell wenig Zusatzinformation.
- **Verletzt:** B1 (nach der Testphase kostenpflichtig).
- **Kosten:** 30 Tage gratis, ohne Kreditkarte. Danach gibt es nur „Enterprise“-Pläne auf Anfrage, öffentliche Preise fehlen (Doku-Seite, abgerufen Okt. 2026; /pricing liefert 404).
- **Aufwand:** gering (SDK, API-Key als GitHub-Secret).
- **Recht/Risiko:** Die Daten gehen an einen US-Dienst; für Kursdaten ist das unkritisch. Die AGB für die Testphase habe ich nicht gelesen (ungeprüft).
- **Lohnt sich, wenn:** ein 30-Tage-Vorwärtsvergleich gegen TimesFM auf denselben Kerzen einen klar besseren CRPS/Brier zeigt. Das wäre ein Gratis-Experiment innerhalb der Testphase.

### Tavily
- **Link:** https://docs.tavily.com/documentation/api-credits
- **Was es bringt:** eine Such- und Extract-API speziell für LLM-Agenten, mit einem Research-Endpunkt.
- **Potenzial: 2/5.** Das Gratis-Kontingent ist nett, aber der Dienst bringt nichts Neues gegenüber der vorhandenen Websuche.
- **Verletzt:** B1 nur oberhalb des Gratis-Kontingents. 1.000 Credits pro Monat sind gratis, ohne Kreditkarte; eine Basic-Suche kostet 1 Credit. Das reicht für etwa 30 Suchen pro Tag.
- **Kosten (Doku, 2026):** Pay-as-you-go 0,008 $/Credit (Basic-Suche 0,008 $, Advanced 0,016 $). Project 30 $/Monat für 4.000 Credits, Bootstrap 100 $ für 15.000. Research kostet 4–250 Credits pro Anfrage.
- **Aufwand:** gering.
- **Recht/Risiko:** ohne Kreditkarte keine Kostenfalle; ist das Kontingent leer, stoppen die Anfragen.
- **Lohnt sich, wenn:** nach dem 14.11. ein Gratis-Modell eine Suchquelle braucht. Dann gehört Tavily eher in den Gratis-Bereich des Tresors.

### Firecrawl
- **Link:** https://www.firecrawl.dev/pricing · https://docs.firecrawl.dev/billing
- **Was es bringt:** Webseiten als Markdown oder JSON scrapen, crawlen und durchsuchen. Über den Katalog „Alexandria“ liefert es zusätzlich typisierte Datenquellen.
- **Potenzial: 2/5.** Nützlich, um Quellen wie Regelseiten oder Resolution-Kriterien sauber zu lesen. Für Prognosequalität ist kein direkter Nutzen belegt.
- **Verletzt:** B1 oberhalb von 1.000 Gratis-Credits pro Monat (1 Credit pro Seite, Suche 2 Credits pro 10 Treffer).
- **Kosten (Preisseite, Okt. 2026):** Hobby 19 $/Monat (5.000 Credits), Standard 99 $ (100.000), Growth 399 $, Scale 749 $. Nachkauf erfolgt in 5-$-Schritten.
- **Aufwand:** gering.
- **Recht/Risiko:** Das Scrapen fremder Seiten kann deren AGB verletzen (z. B. robots.txt oder Paywalls); das liegt beim Nutzer.
- **Lohnt sich, wenn:** regelmäßig viele Seiten strukturiert gelesen werden müssen, mehr als die Gratis-Credits hergeben.
- **Hinweis:** Das Gratis-Kontingent des hier genutzten Firecrawl-Kontos war während dieser Recherche aufgebraucht. Bei Agenten-Nutzung ist es also schnell weg.

### Brave Search API
- **Link:** https://api-dashboard.search.brave.com/documentation/pricing · https://brave.com/search/api/
- **Was es bringt:** ein unabhängiger Web-Index, nicht Google/Bing. Dazu kommen eine „LLM Context“- bzw. Answers-API.
- **Potenzial: 2/5.** Als zweite Suchquelle solide, aber ohne Prognosevorteil.
- **Verletzt:** B1 nur oberhalb des Freibetrags. Der frühere Gratis-Plan ist entfallen; stattdessen gibt es 5 $ Gratis-Guthaben pro Monat, also etwa 1.000 Suchen. Dafür ist eine Kreditkarte nötig (ungeprüft).
- **Kosten (2026):** 5 $/1.000 Anfragen für Search, Answers separat. Quelle: https://scrapegraphai.com/blog/brave-search-api
- **Aufwand:** gering (REST).
- **Recht/Risiko:** Laut AGB dürfen Ergebnisse nicht dauerhaft gespeichert werden (ungeprüft, Brave-ToS lesen).
- **Lohnt sich, wenn:** ein Gratis-Modell nach dem 14.11. eine Suche braucht und 1.000 Anfragen pro Monat reichen.

### OpenAI Deep Research API (o3-deep-research / o4-mini-deep-research)
- **Link:** https://developers.openai.com/api/docs/pricing · https://community.openai.com/t/deep-research-in-the-api-webhooks-and-web-search-with-o3/1299919
- **Was es bringt:** einen autonomen Rechercheagenten, der Dutzende Suchen ausführt und dann einen Bericht mit Quellen liefert.
- **Potenzial: 2/5.** Pro Markt zu teuer und zu langsam (Minuten). Es gibt keinen Beleg, dass ein langer Bericht die Wahrscheinlichkeitsschätzung verbessert. ForecastBench und Metaculus zeigen, dass gute Agenten mit normaler Suche schon nahe an Profis liegen.
- **Verletzt:** B1.
- **Kosten:**
  - o3-deep-research: 10 $/40 $ pro Mio. Tokens.
  - o4-mini-deep-research: 2 $/8 $ pro Mio. Tokens.
  - Dazu kommt die Websuche mit 10 $/1.000 Aufrufen (Preisseite 2026).
  - Beispiel eines einzelnen o4-mini-Laufs: etwa 1,10 $ (https://til.simonwillison.net/llms/o4-mini-deep-research, Okt. 2025). Bei o3 grob das 5-Fache (ungeprüft).
- **Aufwand:** mittel (Background-Modus, Polling).
- **Recht/Risiko:** Laut OpenAI-AGB werden API-Daten standardmäßig nicht zum Training genutzt (ungeprüft für 2026).
- **Lohnt sich, wenn:** man pro Woche wenige, hoch dotierte Langfrist-Märkte gezielt vertieft und im Vorwärtstest einen Brier-Gewinn messen kann.

### Gemini Deep Research (Interactions API)
- **Link:** https://ai.google.dev/gemini-api/docs/interactions-overview · https://ai.google.dev/gemini-api/docs/pricing
- **Was es bringt:** wie oben, ein Recherche-Agent (Agent „deep-research-pro-preview…“) mit Google-Suche.
- **Potenzial: 2/5.** Gleiche Gründe wie bei OpenAI Deep Research. Ein Vorteil ist, dass die Google-Suche die Ereignislage gut abdeckt.
- **Verletzt:** B1. Das Gratis-Kontingent der Gemini-API gilt hier nicht (ungeprüft).
- **Kosten:** Abgerechnet wird nach Tokens zu Gemini-3.x-Pro-Preisen, eine feste Gebühr pro Aufgabe gibt es nicht. Drittquellen nennen etwa 1–3 $ pro Aufgabe (Standard ca. 2 $, Max ca. 5 $), Forennutzer berichten von knapp 3 $ pro Lauf (https://discuss.ai.google.dev/t/google-gemini-deep-research-costs/112804; https://tokencost.app/blog/gemini-deep-research-agent-cost). Die Grounding-Suche kostet nach 5.000 Gratis-Anfragen pro Monat 14 $/1.000 (Preisseite, Okt. 2026).
- **Aufwand:** mittel.
- **Recht/Risiko:** Im Free-Tier verwendet Google die Daten zur Produktverbesserung, im Paid-Tier nicht (Preisseite).
- **Lohnt sich, wenn:** wie bei OpenAI Deep Research. Zusätzlich gilt: Die 5.000 Gratis-Grounding-Suchen pro Monat sind für normale Gemini-Aufrufe interessant, aber nur im Paid-Tier.

---

## Echtzeit- und Niedriglatenz-Infrastruktur

Stand der Recherche: 30.10.2026. Preise ohne MwSt., sofern nicht anders angegeben. „(ungeprüft)“ = nicht an Primärquelle verifiziert bzw. Schätzung.
**Grundsätzliche Einordnung vorweg:** Die Arena handelt auf Papier und entscheidet per LLM-Agent im 15-min-Takt. Ein LLM-Aufruf allein dauert Sekunden. Latenz-Vorteile im Millisekunden-Bereich sind deshalb für dieses Projekt strukturell unerreichbar und auch unnötig. Profi-Market-Maker sitzen kolokiert (Mikrosekunden bis niedrige Millisekunden), ein Privatanleger mit VPS sitzt bei Millisekunden bis Zehntel-Sekunden und mit KI-Agent bei Sekunden. Was ein dauerhafter Prozess realistisch bringt: **keine verpassten Ereignisse zwischen zwei Abfragen**, sauberere Papier-Fills (echte Orderbuch-Historie statt Momentaufnahme) und eigene Tick-Daten fürs Backtesting. Das ist der eigentliche Wert, nicht die Geschwindigkeit.

### Dauerhafte WebSocket-Feeds statt 15-min-Polling (Polymarket, Kalshi, Deribit)
- **Links:** Polymarket WS-Übersicht https://docs.polymarket.com/market-data/websocket/overview.md · Market-Channel https://docs.polymarket.com/api-reference/wss/market.md · Kalshi https://docs.kalshi.com/getting_started/quick_start_websockets · https://docs.kalshi.com/getting_started/websocket_connection
- **Was es bringt:** Orderbuch-Snapshots plus Deltas, Trades und Markt-Lifecycle-Ereignisse (Polymarket) bzw. `orderbook_snapshot` + `orderbook_delta` (Kalshi), alles in Echtzeit. Der Wächter könnte auf Ereignisse reagieren (Kurssprung, neuer Markt, Auflösung), statt sie bis zu 15 min später zu sehen. Papier-Fills würden realistischer, weil die Markttiefe zum Zeitpunkt der Entscheidung bekannt ist.
- **Wichtiges Detail:** Polymarkets Market-Channel (`wss://ws-subscriptions-clob.polymarket.com/ws/market`) ist **öffentlich, ohne Auth**. Lesen geht also ohne Konto, auch aus DE (der Geoblock betrifft Orders). Kalshi-WS braucht dagegen **immer einen authentifizierten API-Key**, also ein Konto, auch für öffentliche Marktdaten. Deribit bietet öffentliche WS-Kanäle (ungeprüft im Detail).
- **Potenzial: 4/5.** Das ist der größte echte Hebel dieser Liste: Ereignistreue und Datenqualität statt Speed. Er passt zur Papier-Arena.
- **Verletzte Bedingung:** andere Infrastruktur (dauerhaft laufender Prozess, GitHub Actions taugt dafür nicht). Bei Kalshi zusätzlich ein Konto.
- **Kosten:** 0 € für die Feeds. Der Host kostet je nach Variante 0 € (Oracle Free) bis etwa 5–6 €/Monat (Hetzner, s. u.).
- **Aufwand:** mittel. Nötig sind Reconnect-Logik, Heartbeats, lokaler Orderbuch-Zustand (Delta auf Snapshot anwenden), Persistenz und ein Weg, GitHub-Workflows per `repository_dispatch` anzustoßen.
- **Rechtslage/Risiko:** Lesen öffentlicher Daten ist unkritisch. API-ToS beachten (Rate-Limits, Weiterverbreitung).
- **Lohnt sich, wenn …** die Arena auf Ereignisse reagieren soll, die schneller als 15 min kommen und gehen (Live-Sport, Krypto-15-min-Märkte, Datenveröffentlichungen), oder wenn eigene Orderbuch-Historie fürs Backtesting gebraucht wird.

### Hetzner Cloud VPS (nach den Preiserhöhungen 2026)
- **Link:** https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/
- **Was es bringt:** ein günstiger, verlässlicher 24/7-Host in DE/FI für WS-Sammler, Datenbank und Wächter-Dienst.
- **Potenzial: 3/5.** Solide Basis. Für dieses Projekt ist aber Oracle Free oder ein Raspberry Pi oft genug.
- **Verletzte Bedingung:** kostenpflichtig, andere Infrastruktur.
- **Kosten (Hetzner-Doku, Anpassung zum 15.06.2026, 8 Uhr CEST, gilt für Neubestellungen und Rescales; Preise ohne IPv4):**
  - CX23: 3,99 € auf **5,49 €/Monat**
  - CX33: 6,49 € auf 8,49 €
  - CAX11 (ARM): 4,49 € auf **5,99 €**
  - CAX21: 7,99 € auf 10,49 €
  - CPX22: 7,99 € auf **19,49 €** (+144 %)
  - Davor gab es bereits zum 01.04.2026 eine Runde, laut Drittquelle CX22/CAX11 von 3,29 € auf 4,49 € (https://agentdeals.dev/hetzner-pricing-2026, https://www.igorslab.de/hetzner-erhoeht-preise-ab-april-2026-deutlich-fuer-cloud-und-dedicated-server/, https://heise.de/-11333037). In Summe ist CAX11 also von 3,29 € auf 5,99 € gestiegen, rund +82 %. Begründet wurde das mit Energie- und Hardwarekosten (RAM/SSD durch KI-Nachfrage).
- **Aufwand:** gering (Linux-Grundkenntnisse, systemd, Backups).
- **Rechtslage/Risiko:** unkritisch. Risiko weiterer Preisrunden: 2026 gab es mehrere (https://webhosting.today/2026/05/29/hetzner-has-now-raised-prices-three-times-in-2026-this-one-is-different/).
- **Lohnt sich, wenn …** Oracle Free wegen Kapazität, Idle-Reclaim oder Kürzung nicht zuverlässig läuft und man einen Dienst mit SLA-ähnlicher Verlässlichkeit für etwa 6 €/Monat will.

### Oracle Cloud Always Free (Kontrast / geplanter Umstieg)
- **Links:** https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm · https://infoq.com/news/2026/07/oracle-cloud-free-tier-limits/
- **Was es bringt:** ein 0-€-Host für WS-Sammler und Wächter.
- **Achtung, Stand 2026:** Mehrere Quellen berichten, dass das Ampere-A1-Kontingent von 4 OCPU/24 GB auf **2 OCPU/12 GB halbiert** wurde. Das Datum ist widersprüchlich (26.06. bzw. 18.08.2026). Oracle hat es laut InfoQ nicht öffentlich angekündigt. Idle-Instanzen können zurückgefordert werden: ungefähr 7 Tage mit CPU/Netz/RAM unter 15–20 % (Schwellen ungeprüft; https://oracommit.blogspot.com/2026/02/understanding-oci-always-free-compute.html).
- **Potenzial: 3/5.** Kostenlos, aber mit Plattformrisiko.
- **Verletzte Bedingung:** andere Infrastruktur, Konto (Kreditkarte zur Verifizierung).
- **Kosten:** 0 €.
- **Lohnt sich, wenn …** der WS-Sammler leichtgewichtig ist und ein Ausfall von Tagen verkraftbar ist.

### Heimserver / Raspberry Pi 24/7 (Stromkosten DE)
- **Links:** Strompreise https://www.stromauskunft.de/strompreise/dashboard/ · https://www.finanztip.de/strompreis/
- **Was es bringt:** volle Kontrolle, keine Cloud-Kündigungsrisiken, lokale Datenbank für Tick-Archive.
- **Kosten:**
  - Strompreis Neukunde, günstigster Tarif: ca. **30,5 ct/kWh** (StromAuskunft, 17.10.2026, Modellhaushalt 3.500 kWh). Grundversorgung ca. 40,4 ct/kWh. Finanztip nennt 32,95 ct (Stand 08/2026).
  - Pi 5 mit ca. 5 W Dauerlast (ungeprüft, Schätzung) braucht etwa 44 kWh/Jahr, also **rund 13–18 €/Jahr**.
  - Mini-PC mit ca. 10–15 W (ungeprüft) kostet etwa 27–55 €/Jahr.
  - Hardware einmalig: Pi 5 plus NVMe etwa 100–150 € (ungeprüft).
- **Potenzial: 3/5.** Günstigster dauerhafter Host. Für Latenz irrelevant, denn die Heimleitung ist schlechter als ein Rechenzentrum, für die Arena aber egal.
- **Verletzte Bedingung:** andere Infrastruktur (eigene Hardware, Heimnetz).
- **Aufwand:** mittel (USV/Stromausfall, SD-Karten-Verschleiß, Router-Neustarts, Zwangstrennung, Monitoring).
- **Rechtslage/Risiko:** unkritisch. Keine Ports nach außen öffnen, nur ausgehende WS-Verbindungen.
- **Lohnt sich, wenn …** ohnehin ein Pi oder Mini-PC herumliegt und Daten lokal liegen sollen (Tick-Archiv mit Hunderten GB).

### Eigene Polygon-Node vs. bezahlte RPCs (Alchemy, QuickNode, Helius)
- **Links:** Polygon-Doku https://docs.polygon.technology/pos/how-to/prerequisites.md · Helius https://www.helius.dev/docs/billing/plans.md · Vergleich https://costbench.com/compare/alchemy-vs-quicknode/
- **Was es bringt:** On-Chain-Sicht auf Polymarket (Settlement, Wallet-Bewegungen großer Trader, „Whale-Tracking“), ohne Rate-Limits öffentlicher RPCs. Helius ist Solana und nur relevant für Kalshi-tokenisierte Märkte via DFlow/Jupiter.
- **Status Polymarket-Chain:** Polymarket hat im Dez. 2025 eine eigene Ethereum-L2 („POLY“) angekündigt und im April 2026 einen Infrastruktur-Umbau (Chain, Orderbuch, Contracts, API) bestätigt. **Ob die Migration bis heute live ist, ist unbestätigt** (https://www.kucoin.com/news/flash/polymarket-to-migrate-from-polygon-launches-ethereum-l2-network). Eine eigene Polygon-Node könnte also bald entwertet sein.
- **Eigene Polygon-Full-Node:** laut 2026er Guide 16 Kerne, 64 GB RAM, **8 TB NVMe**, Snapshots referenzieren 9 TB (https://www.cherryservers.com/blog/polygon-node-requirements). Das bedeutet einen Dedicated Server für etwa 100–200 €/Monat (ungeprüft) und ist für einen Hobby-Rahmen unverhältnismäßig.
- **Bezahlte RPCs (Stand 2026):**
  - **Helius** (offiziell, gültig ab 07.04.2026): Free 0 $, Developer 49 $ (10 Mio. Credits, 50 req/s), Business 499 $, Professional 999 $/Monat.
  - **QuickNode** (Drittquellen): Free 0 $ (50 Mio. API-Credits), Build 49 $, Scale 299 $, Enterprise ab 999 $. Flat-Rate-RPS ab 799 $/Monat für 75 RPS (seit März 2026, ungeprüft an Primärquelle).
  - **Alchemy:** Free-Tier mit Compute Units, Pay-as-you-go. Drittquellen widersprechen sich (30 Mio. vs. 300 Mio. CU/Monat frei; „ab 104 $/Monat“ vs. „5 $ pro 11 Mio. CU“), deshalb **ungeprüft**, offizielle Seite https://www.alchemy.com/pricing prüfen.
- **Potenzial: 2/5.** Die Free-Tiers reichen für gelegentliche On-Chain-Abfragen. Die Polymarket-API (Gamma/Data-API) liefert das meiste ohnehin.
- **Verletzte Bedingung:** kostenpflichtig ab höherem Volumen. Eigene Node bedeutet andere Infrastruktur.
- **Lohnt sich, wenn …** ein Agent systematisch On-Chain-Flows (Smart-Money-Wallets) in Echtzeit auswerten soll und Free-Tier-Limits regelmäßig reißen.

### Tick-Datenarchiv: Tardis.dev
- **Link:** https://tardis.dev/#pricing
- **Was es bringt:** historische Tick-Level-Daten (L2-Orderbuch-Updates, Snapshots, Trades, Optionsketten, Liquidationen) für Deribit, Coinbase, Kraken, Binance u. v. m. Ermöglicht realistisches Backtesting der Krypto-Agenten und Replays („Tardis Machine“).
- **Potenzial: 2/5.** Für ein Hobby-Projekt zu teuer. Kostenlose Beispieldaten (Download-Samples) reichen zum Kennenlernen.
- **Verletzte Bedingung:** kostenpflichtig.
- **Kosten (Preisseite, abgerufen 30.10.2026, pro Monat):**
  - Academic: Perps/Optionen 350 $, Spot/Derivate 450 $, alle Börsen 650 $ (nur Quartals- oder Jahresabrechnung)
  - **Solo: 700 $ / 900 $ / 1.200 $**
  - Professional: 1.000 $ / 1.350 $ / 2.200 $
  - Business: 3.000 $ / 3.500 $ / 6.000 $
  - Mindestbestellung 300 $. 4 Jahre Historie (Business: alles). 20 TB Transfer/Monat.
- **Aufwand:** gering bis mittel (CSV-Downloads, Python-Client).
- **Rechtslage/Risiko:** Lizenz verbietet Weiterverbreitung (übliche Klausel, ungeprüft im Wortlaut).
- **Lohnt sich, wenn …** man eine konkrete Krypto-Strategie mit Orderbuch-Abhängigkeit (z. B. Deribit-Optionen-Skew) über Jahre backtesten will. Alternative: Gratis-Daten selbst per WS sammeln (s. o.), dann fehlt nur die Vergangenheit.

### Zeitreihen-Datenbank: TimescaleDB / ClickHouse Cloud
- **Links:** ClickHouse Billing https://clickhouse.com/docs/products/cloud/reference/billing/billing-overview.md · Timescale (jetzt „Tiger Data“) https://www.tigerdata.com/pricing (ungeprüft)
- **Was es bringt:** schnelle Abfragen über Millionen Ticks und Orderbuch-Deltas. Grundlage für Agent-Features wie „Volatilität der letzten 6 h“ oder „Orderbuch-Imbalance“.
- **Potenzial: 2/5.** Für Arena-Mengen reicht selbst gehostetes **TimescaleDB oder ClickHouse (Open Source)** auf Pi/VPS, oder schlicht DuckDB/Parquet. Managed Cloud ist Luxus.
- **Verletzte Bedingung:** kostenpflichtig (Cloud), andere Infrastruktur.
- **Kosten:** ClickHouse Cloud Basic ab **66,52 $/Monat** (Teilzeitbetrieb, 1 Replica, 8 GiB RAM, 2 vCPU). 24/7 sind es ca. 186 $/Monat. Kein dauerhafter Free-Tier, 300-$-Testguthaben für 30 Tage (Drittquellen, Stand Mitte 2026: https://dev.to/beton/clickhouse-pricing-teardown-2026-209h). Tiger-Data-Preise wurden nicht recherchiert (ungeprüft). Self-hosted kostet 0 € plus Host.
- **Lohnt sich, wenn …** Tick-Daten über mehrere Märkte im Bereich von Dutzenden GB anfallen und Abfragen auf SQLite/Parquet zu langsam werden. Dann zuerst self-hosted, Cloud erst bei Teamnutzung.

### Polymarket-Nähe: AWS eu-west-2 (London) / eu-west-1 (Dublin)
- **Links:** https://docs.polymarket.com/trading/overview · https://hyperlatency.glassnode.com/prediction-markets/about
- **Was es bringt:** Laut Polymarket-Doku stehen die primären CLOB-Server in **AWS eu-west-2 (London)**. Die nächstgelegene nicht geo-gesperrte Region ist **eu-west-1 (Dublin)**, denn UK ist gesperrt. Die API läuft hinter Cloudflare. Ein Entwickler-Benchmark misst etwa 1,2 ms ab Amsterdam und etwa 88 ms ab US-East (https://dev.to/bluewhale-quant-lab/i-measured-polymarkets-api-latency-from-5-regions-heres-the-script-and-the-results-3mjm). Ein Hetzner-Server in Nürnberg/Falkenstein liegt also ohnehin nur wenige Millisekunden entfernt (ungeprüft).
- **Potenzial: 1/5** für dieses Projekt. Der Abstand DE–London ist gegenüber der LLM-Latenz vernachlässigbar.
- **Realitäts-Check:** Polymarket hat am 07.01.2026 **dynamische Taker-Fees** (bis ca. 3,15 % bei 50 ct) in den 15-min-Kryptomärkten eingeführt, gezielt **gegen Latenz-Arbitrage** zwischen Spotbörsen und Polymarket (https://www.financemagnates.com/cryptocurrency/polymarket-introduces-dynamic-fees-to-curb-latency-arbitrage-in-short-term-crypto-markets/). Die Plattform schließt diese Nische also aktiv.
- **Verletzte Bedingung:** kostenpflichtig, andere Infrastruktur. Echter Handel wäre aus DE ohnehin geo-gesperrt (Help-Center listet DE: https://help.polymarket.com/en/articles/13364163-geographic-restrictions).
- **Lohnt sich, wenn …** nie, für dieses Projekt.

### AWS Tokyo (ap-northeast-1) nahe Binance / Singapur nahe Bybit
- **Links:** https://aws.amazon.com/blogs/industries/ultra-low-latency-cross-region-crypto-trading-with-avelacom-and-aws/ · https://docs.ccxt.com/blog/how-far-is-your-exchange
- **Was es bringt:** Tokyo gilt als Haupt-Hub für Binance (AWS-Blog). Die CCXT-Messung zeigt etwa 8 ms für Binance-Spot ab Tokyo und etwa 10 ms für Bybit-Spot ab Singapur. Der genaue Ort der Matching-Engines ist **nicht offiziell bestätigt**, Quellen widersprechen sich, teils wird us-east-1 genannt.
- **Potenzial: 1/5.** Die Arena handelt Coinbase/Kraken/Deribit, nicht Binance/Bybit. Cross-Exchange-Arbitrage ist ein Profi-Geschäft (HFT-Firmen mit dedizierten Leitungen wie Avelacom).
- **Verletzte Bedingung:** kostenpflichtig, andere Infrastruktur. Binance/Bybit-Konto mit DE-Regulierung (MiCA) ist ein eigenes Thema (ungeprüft).
- **Kosten:** kleine EC2-Instanz in Tokyo etwa 10–20 $/Monat plus Traffic (ungeprüft, AWS-Preisrechner prüfen). Dedizierte Low-Latency-Leitungen gibt es nur auf Anfrage.
- **Lohnt sich, wenn …** man echte Cross-Exchange-Arbitrage mit eigenem Kapital betreiben würde. Das passt nicht zu dieser Arena.

### Equinix NY4 / LD4 Kolokation inkl. Deribit-Kolokation
- **Links:** Deribit https://support.deribit.com/hc/en-us/articles/25944617582877 · Cross-Connect-Equalization https://support.deribit.com/hc/en-us/articles/36164403025181-Cross-Connect-Equalization-at-Deribit · Equinix-Billing https://docs.equinix.com/cross-connect/xc-pricing-billing-terms
- **Was es bringt:** Deribit-Server stehen in **Equinix LD4 (Slough)**. Anbindung über bis zu 2U im Deribit-Client-Rack oder per Cross-Connect (nur 10G Singlemode LR). Cross-Connects sind seitens Deribit derzeit **kostenlos**, Equinix berechnet aber Einrichtung und Monatsmiete. Seit 15.06.2026 gibt es „Cross Connect Equalization“ (gleich lange Leitungen für alle). NY4 (Secaucus) ist der Standard-Standort für US-Aktien und -Optionen.
- **Potenzial: 1/5.** Reines Profi-Terrain. Ein LLM-Agent hat Sekunden Latenz, Kolokation spart Mikrosekunden.
- **Verletzte Bedingung:** kostenpflichtig, andere Infrastruktur, Konto/Vertrag, oft institutioneller Status.
- **Kosten:** keine öffentliche Equinix-LD4-Preisliste. Vergleichswert: Cboe UK verlangt 2026 für 10G-Anbindung in LD4 **4.400 £/Monat** inkl. Cross-Connect (https://res-certification.cboe.com/resources/participant_resources/CboeUK_PhysicalConnectivityPricing_effective_2026.pdf). Dazu kommen Rack/Strom/Hardware im Bereich niedriger vierstelliger €/Monat (ungeprüft).
- **Lohnt sich, wenn …** man ein Market-Making-Unternehmen mit sechs- bis siebenstelligem Kapital betreibt.

---

## Kreative Hebel

### Agentic-Forecasting-Wettbewerb: Metaculus FutureEval (ehem. AI Benchmark / Q-Cups)
- **Links:** https://metaculus.com/aib · Frühjahr 2026 https://www.metaculus.com/aib/2026/spring/ · Ankündigung https://forum.effectivealtruism.org/posts/5EX9dz7nKthcxECTe/announcing-spring-2026-ai-forecasting-benchmark · Sommer 2026 https://www.lesswrong.com/posts/E7wxQnBvYxgB3rTTk/announcing-metaculus-summer-2026-futureeval-bot-tournament
- **Was es bringt:** Die KI-Agenten der Arena könnten **echte Preisgelder ohne Handelsrisiko** gewinnen und sich extern benchmarken lassen. Das Format läuft dreimal jährlich, je **50.000 $ Preispool**, 300–500 Fragen. Im Frühjahr 2026 traten 173 Bots an (111 ohne Metaculus-eigene). Für Preisgeld muss Code oder eine Bot-Beschreibung eingereicht werden (Regel aus Q4 2024; ob das weiter gilt, ist ungeprüft). Ein Herbst-2026-Turnier ist plausibel, aber **Datum und Pool nicht bestätigt** (Seite gab 403).
- **Potenzial: 4/5.** Bester „kreativer Hebel“ der Liste: passt exakt zum Projekt (LLM-Agenten, die Ereignis-Wahrscheinlichkeiten schätzen), kein Echtgeld-Risiko, legal aus DE, Preisgeld möglich. Teilnehmen kostet nur LLM-Tokens. Metaculus hat in früheren Runden teils LLM-Credits gestellt (ungeprüft für 2026).
- **Verletzte Bedingung:** Konto (Metaculus-Bot-Account). Läuft aber auch auf GitHub Actions (Metaculus stellt dafür ein Template bereit, ungeprüft für 2026).
- **Kosten:** 0 € Teilnahme plus LLM-API-Kosten (je nach Modell und Fragenzahl etwa 10–100 €/Saison, ungeprüft Schätzung).
- **Aufwand:** mittel. Adapter vom Arena-Agenten auf das Metaculus-Fragenformat (binär, numerisch, Multiple Choice), Abgabe-Workflow.
- **Rechtslage/Risiko:** unkritisch. Preisgeld ist ggf. steuerpflichtig (ungeprüft). Preisgeld-Berechtigung je nach Land in den Turnierregeln prüfen.
- **Lohnt sich, wenn …** die Arena-Agenten stabil laufen und man wissen will, wie gut sie gegen über 100 andere Bots und Pro-Forecaster kalibriert sind.

### Wetterdaten für Kalshi-Wettermärkte (gratis vs. kommerziell)
- **Links:** Kalshi Weather https://help.kalshi.com/markets/popular-markets/weather-markets · Kontraktbeispiel NYC https://kalshi-public-docs.s3.amazonaws.com/contract_terms/NHIGH.pdf · ECMWF Open Data https://ecmwf.int/en/forecasts/datasets/open-data · ECMWF-Ankündigung https://sciencebusiness.net/network-updates/ecmwf-makes-its-entire-real-time-catalogue-open-all · Tomorrow.io https://support.tomorrow.io/hc/en-us/articles/23554984091156-Tomorrow-io-Pricing-Overview
- **Was es bringt:**
  - **Settlement-Quelle:** Kalshi-Tageshöchst-Temperaturmärkte settlen **ausschließlich auf dem NWS Daily Climate Report** der im Kontrakt genannten Station (z. B. Central Park), am Morgen danach. Stündliche Märkte settlen auf The Weather Company.
  - **Gratis-Edge:** NWS-METAR-Stationsdaten (laufende Ist-Temperatur am Tag selbst), NWS-Prognosen, **ECMWF Open Data**. Seit **01.10.2025** ist der komplette Echtzeit-Katalog unter CC-BY-4.0 ohne Datengebühr. Für Vollvolumen-Lieferung und Sonderservices fallen Servicegebühren an. Das frei zugängliche Portal ist eine Teilmenge (0,25°, IFS und AIFS). AIFS erscheint sofort nach Berechnung, IFS erst am Ende des Dissemination-Plans.
  - **Kommerziell:** Tomorrow.io (Free etwa 500 Calls/Tag laut Drittquellen, bezahlte Developer/Team/Business-Stufen; Preise ungeprüft). DTN, Weather Company Enterprise und ECMWF-Dissemination-Vertrag für höhere Auflösung und frühere Lieferung gibt es nur auf Anfrage.
- **Potenzial: 3/5.** Wettermärkte sind einer der wenigen Bereiche, in denen **freie, hochwertige Daten** (Ensemble-Prognosen, METAR-Live-Werte) einem KI-Agenten echten Informationsvorsprung gegenüber Bauchgefühl-Tradern geben können. Bezahldaten bringen gegenüber ECMWF/NWS-Gratis nur noch marginal mehr.
- **Verletzte Bedingung:** Bezahldaten sind kostenpflichtig. Gratis-Daten verletzen nichts (außer Rechenaufwand für GRIB-Verarbeitung, ggf. VPS).
- **Kosten:** 0 € (ECMWF Open/NWS/Open-Meteo). Kommerziell auf Anfrage, mindestens dreistellig im Monat (ungeprüft).
- **Rechtslage/Risiko:** CC-BY-4.0 verlangt **Namensnennung** ECMWF. Kalshi-Konto aus DE ist unklar (s. o.), Papierhandel ist unproblematisch.
- **Lohnt sich, wenn …** (gratis) sofort einsetzbar als Ideenbaustein. Bezahlt nur, wenn ein Agent nachweislich durch Prognosequalität limitiert ist und nicht durch Kalibrierung.

### Metaculus / INFER Gemeinschaftsprognosen (gratis, Kontrast)
- **Links:** https://www.metaculus.com/questions/ · API-Doku über Metaculus-Website (ungeprüft) · INFER (RAND Forecasting Initiative) https://www.randforecastinginitiative.org/ (ungeprüft)
- **Was es bringt:** kostenlose Community-Prognosen (Metaculus Community Prediction) als Vergleichs-Prior zu Polymarket/Kalshi-Preisen. Divergenzen zwischen Markt und Community können Agenten als Signal nutzen.
- **Potenzial: 3/5.** Gratis, per API abrufbar, gut kalibriert. Ideale Ergänzung zur Arena, aber kein Bezahl-Hebel.
- **Verletzte Bedingung:** keine (allenfalls Konto/API-Token). Gehört eigentlich nicht in den Tresor, steht hier als Kontrast.
- **Kosten:** 0 €.
- **Lohnt sich, wenn …** sofort, als Feature-Quelle.

### Polymarket Liquidity Rewards & Maker Rebates
- **Links:** https://docs.polymarket.com/programs/liquidity-rewards · https://docs.polymarket.com/developers/market-makers/maker-rebates-program · Taker-Rebates https://docs.polymarket.com/trading/taker-rebates
- **Was es bringt:**
  - **Liquidity Rewards:** tägliche USDC-Auszahlung (Mitternacht UTC) für ruhende Limit-Orders nahe am Mittelkurs, je nach Markt. Es gibt Sonderkampagnen, z. B. WM 2026 (11.06.–19.07.2026).
  - **Maker Rebates:** aus Taker-Gebühren finanziert, anteilig zur ausgeführten Maker-Liquidität. Gestartet in den 15-min-Kryptomärkten, laut Berichten ab 30.03.2026 auf Finanzen/Politik/Kultur ausgeweitet (Geopolitik gebührenfrei; https://www.kucoin.com/news/flash/polymarket-to-earn-1m-daily-after-fee-structure-update-on-march-30-2026).
  - **Taker-Rebate-Programm** seit 28.05.2026.
- **Potenzial: 2/5.** Theoretisch ein „Gehalt fürs Quoten“. Praktisch konkurrieren Profi-MMs mit Inventar-Management und WS-Infrastruktur. Adverse Selektion frisst die Rewards schnell auf. Als Papier-Simulation („was hätte unser Agent an Rewards verdient?“) wäre es interessant, aber die Reward-Formel ist komplex.
- **Verletzte Bedingung:** Echtgeld, Konto, **rechtlich: DE ist auf Polymarkets Sperrliste** (https://help.polymarket.com/en/articles/13364163-geographic-restrictions). VPN-Umgehung verstößt gegen die ToS.
- **Kosten:** Kapital fürs Quoten (USDC), Infrastruktur (24/7-WS-Bot).
- **Rechtslage/Risiko:** aus DE nicht zulässig nutzbar. Glücksspielrechtlich ist Polymarket in DE nicht lizenziert (ungeprüft im Detail). Kontosperre und Verlust bei Umgehung.
- **Lohnt sich, wenn …** man in einer zugelassenen Jurisdiktion lebt, Kapital riskieren will und einen robusten MM-Bot mit Inventar-Limits hat.

### Kalshi Liquidity Incentive Program (LIP)
- **Links:** https://help.kalshi.com/incentive-programs/liquidity-incentive-program · CFTC-Filing https://www.cftc.gov/filings/orgrules/rules10142633803.pdf · Ende Volume-Rewards https://sbcamericas.com/2026/10/02/kalshi-end-volume-rewards-scrutiny/
- **Was es bringt:** Belohnung für ruhende Orders, die das Buch verbessern, **auch ohne Fill**. Laut Help-Center 10–1.000 $ pro Tag und Markt, Mindestauszahlung 1 $. Ein Substack-Artikel nennt das die „Dawn of the garage-band market maker“ (https://fiftycentdollars.substack.com/p/kalshis-new-liquidity-incentives). Laut CFTC-Filing tritt die geänderte Fassung am **28.10.2026** in Kraft. Das **Volume Incentive Program** endet nach CFTC-Prüfung und Wash-Trading-Vorwürfen vorzeitig.
- **Potenzial: 2/5** (für Privat-MM in den USA eher 3/5). Für einen deutschen Nutzer ist es faktisch irrelevant: Das Filing schließt laut Recherche **Nicht-US-Nutzer aus**.
- **Verletzte Bedingung:** Echtgeld, Konto (US-KYC), rechtlich.
- **Kosten:** Kapital plus 24/7-Bot.
- **Rechtslage/Risiko:** Kalshi ist CFTC-reguliert. Ob internationale Konten aus DE möglich sind, ist widersprüchlich belegt (ungeprüft; https://help.kalshi.com/account/signing-up/is-kalshi-us-only). Missbrauchsüberwachung und mögliche Statusentziehung.
- **Lohnt sich, wenn …** man US-Person ist. Für die Arena reicht es, das Programm als **Papier-Benchmark** zu kennen: Wie viel LIP hätte eine simulierte Quote-Strategie verdient?

### Ereignis-Auflösungs-Rennen (Wirtschaftsdaten, Wahlen)
- **Links:** BLS-Kalender 2026 https://www.bls.gov/schedule/2026/home.htm · BLS-Lockup-Abschaffung https://www.bls.gov/bls/discontinuing-department-of-labor-media-lockup-effective-june-3.pdf
- **Was es bringt:** Kalshi/Polymarket haben Märkte auf CPI, Arbeitsmarkt (NFP), Fed-Zins und Wahlergebnisse. Wer die Zahl Sekunden nach Veröffentlichung kennt, kann noch nicht nachgezogene Orders abgreifen.
- **Wichtiger Fakt:** Das US-Arbeitsministerium hat **Medien-Lockups zum 03.06.2020 dauerhaft abgeschafft**. BLS-Daten gehen um **8:30 ET gleichzeitig an alle über das Web**. Damit gibt es für BLS keinen legalen Presse-Vorsprung mehr, nur noch Netzwerk-Latenz zum BLS-Server/CDN. Fed-Entscheidungen erscheinen um 14:00 ET auf federalreserve.gov. Dort gibt es weiter einen Presse-Lockup (ungeprüft).
- **Potenzial: 2/5.** Ein Gratis-Poller auf bls.gov ist technisch leicht machbar. Profis sind aber mit Sub-Millisekunden-Feeds dran (s. nächste Idee), und Market-Maker ziehen Quotes vor Veröffentlichungen meist zurück. Für die Papier-Arena interessant als **„Event-Day-Modus“**: Der Wächter läuft zum Veröffentlichungszeitpunkt minütlich statt alle 15 min (geht sogar mit GitHub-Actions-Cron plus Zeitplan).
- **Verletzte Bedingung:** andere Infrastruktur (sekundengenauer Poller), für echten Vorteil Echtgeld/Konto.
- **Kosten:** 0 € (eigener Poller) bis 5-stellig/Jahr (Profi-Feeds).
- **Rechtslage/Risiko:** Öffentlich veröffentlichte Daten schnell zu nutzen ist legal. **Illegal** ist der Handel auf embargoed/geleakte Daten (Insiderhandel bzw. Missbrauch nach CEA/CFTC-Regeln). Kalshi verbietet zudem Insider-Handel in seinen Regeln (ungeprüft im Wortlaut).
- **Lohnt sich, wenn …** die Arena explizit „Event-Trading“ testen will. Dann reicht der Gratis-Weg völlig.

### Superforecaster-Dienst: Good Judgment Inc. FutureFirst
- **Links:** https://goodjudgment.com/services/ · Rückblick https://goodjudgment.com/2023-review/
- **Was es bringt:** abonnierbare Superforecaster-Prognosen zu geopolitischen und ökonomischen Fragen mit täglichen Updates und **API-Zugang**. Seit 2023 auch Direktabos und spezialisierte Kanäle. Könnte als externer „Prior“ für Agenten dienen (Agent gegen Superforecaster gegen Marktpreis).
- **Potenzial: 2/5.** Gute Kalibrierung, aber Fragen überlappen nur teilweise mit handelbaren Märkten. Die Prognosen fließen ohnehin schnell in die Marktpreise ein.
- **Verletzte Bedingung:** kostenpflichtig, Konto/Vertrag.
- **Kosten:** **kein öffentlicher Preis gefunden** (Beratungsgespräch/Angebot). Die Seite war für den Abruf gesperrt (403). Preis ungeprüft.
- **Rechtslage/Risiko:** Lizenz verbietet vermutlich Weiterverbreitung (ungeprüft).
- **Lohnt sich, wenn …** die Arena einen „externen Experten-Prior“ systematisch gegen eigene Agenten benchmarken will und ein Budget im (vermutlich) vierstelligen Bereich da ist (ungeprüft).

### Builder-Programme: Polymarket Builders / Kalshi Builders
- **Links:** Polymarket Builder-Fees https://docs.polymarket.com/builders/fees · pm.wiki-Übersicht https://pm.wiki/uk/projects/polymarket-builders-program · Kalshi-Builders (Solana/DFlow) https://blockworks.co/news/kalshi-ecosystem-hub-solana-base · https://decrypt.co/350534/kalshi-solana-on-chain-predictions-aims-increase-liquidity-pool
- **Was es bringt:**
  - **Polymarket:** Builder-Profil (Settings → Builders) mit eigenem Taker- und Maker-Fee-Aufschlag auf Orders, die über die eigene App geroutet werden. Grants und Rankings laufen über builders.polymarket.com. Die genannten Obergrenzen (1 % Taker / 0,5 % Maker) sowie wöchentliche USDC-Rewards für „Verified Builders“ sind ungeprüft.
  - **Kalshi:** 2-Mio.-$-Grant-Programm (Ende 2025) für Frontends und Apps auf tokenisierten Kalshi-Märkten via Solana/DFlow, mit Builder-Codes und Volumenbeteiligung.
- **Potenzial: 2/5.** Nur relevant, wenn aus der Arena ein **öffentliches Produkt** würde (z. B. ein „KI-Signal-Dashboard“ mit Handelslink). Für ein privates Papier-Projekt passt es nicht. Einen Grant für ein Open-Source-Forschungsprojekt (Agent-Benchmark auf Prognosemärkten) zu beantragen wäre denkbar (ungeprüft, ob das gefördert wird).
- **Verletzte Bedingung:** Konto. Rechtlich: Nutzer aus DE dürften nicht handeln (Polymarket-Geoblock). Ein Builder muss den Geoblock seiner Nutzer prüfen (https://docs.polymarket.com/api-reference/geoblock).
- **Kosten:** 0 € Einstieg, der Aufwand liegt im Produktbau.
- **Rechtslage/Risiko:** Als Betreiber einer Handelsoberfläche drohen regulatorische Fragen (Vermittlung von Wetten/Derivaten in DE, ungeprüft). Hohes Risiko.
- **Lohnt sich, wenn …** man ein öffentliches Tool baut, das Nutzer aus zugelassenen Ländern hat, und rechtlich beraten ist.

### Lizenzierte Echtzeit-Wirtschaftsdaten (Bloomberg ECO, MNI, Need to Know News)
- **Links:** MNI High-Speed-Kalender https://marketnews.com/st/newCalendarpage · Need to Know News (Deutsche Börse) https://mondovisione.com/media-and-resources/news/rts-realtime-systems-group-offers-need-to-know-news-ultralow-latency-economic-da-2011124/ · Bloomberg ECO (Terminal-Funktion, kein separater Link)
- **Was es bringt:** maschinenlesbare Makrodaten mit **Sub-Millisekunden-Latenz** (Need to Know News, MNI High-Speed-Kalender: über 500 Datenpunkte, Zentralbank-Entscheide, Anleiheauktionen). Need to Know News gehört seit 2009 zur Deutschen Börse, MNI ebenfalls seit 2009. Bloomberg ECO ist der Wirtschaftskalender im Terminal.
- **Potenzial: 1/5.** Die Geschwindigkeit verpufft hinter einem LLM-Agenten. Kosten und Nutzen stehen in keinem Verhältnis.
- **Verletzte Bedingung:** kostenpflichtig, Vertrag/Konto, meist kolokierte Infrastruktur.
- **Kosten:** keine öffentlichen Preise (auf Anfrage). Bloomberg Terminal laut Branchenangaben etwa 30.000 $/Jahr pro Arbeitsplatz (ungeprüft). Ultra-Low-Latency-Feeds kosten vermutlich mehr plus Kolokation (ungeprüft).
- **Rechtslage/Risiko:** lizenziert und legal. Weiterverbreitung ist verboten.
- **Lohnt sich, wenn …** man ein professioneller Makro-HFT-Desk ist.

### Sportdaten-Feeds (Sportradar, Genius Sports)
- **Links:** https://developer.sportradar.com/getting-started/docs/your-account · Preisvergleich (Wettbewerberquelle) https://oddspapi.io/blog/?p=3926 · Genius https://www.trustradius.com/products/genius-sports/pricing
- **Was es bringt:** offizielle Live-Daten (Tore, Ballbesitz, Spielereignisse) mit Sekunden-Latenz, schneller als TV-Streams. Relevant für Live-Sportmärkte auf Polymarket/Kalshi.
- **Potenzial: 1/5.** Sehr teuer. „Courtsiding“-artige Latenzvorteile sind genau das, wogegen Plattformen und Ligen vorgehen. Der LLM-Agent ist zu langsam.
- **Verletzte Bedingung:** kostenpflichtig, Vertrag/Konto.
- **Kosten:** Preise nicht öffentlich. Drittquellen schätzen Sportradar auf etwa 1.300–4.990+ €/Monat mit Jahresvertrag bis über 10.000 $/Monat (Wettbewerber-Aussage, ungeprüft). Es gibt einen Sportradar-Trial (30 Tage laut Doku, andernorts 90 Tage). Genius Sports nur auf Anfrage.
- **Rechtslage/Risiko:** Lizenzbedingungen sind streng. Nutzung für Wett-Arbitrage ist oft vertraglich ausgeschlossen (ungeprüft).
- **Lohnt sich, wenn …** nie, für eine Hobby-Arena. Gratis-Alternativen (öffentliche Live-Score-APIs, Quoten-Aggregatoren) reichen zum Experimentieren.

### Experten-Netzwerke (GLG & Co.)
- **Links:** https://en.wikipedia.org/wiki/Gerson_Lehrman_Group · https://unanswered.io/guide/expert-network-call-costs
- **Was es bringt:** einstündige Telefonate mit Branchen-, Politik- oder Regulierungsexperten. Hedgefonds nutzen das zur Due-Diligence.
- **Potenzial: 1/5.** Teuer, nicht automatisierbar, und kein KI-Agent kann es skalieren.
- **Verletzte Bedingung:** kostenpflichtig, Konto (institutionelle Kunden), rechtlich heikel.
- **Kosten:** typisch **ca. 1.000–1.350 $ pro Stunde** für Kunden. Experten erhalten 100–500 $ (Sekundärquellen, Bloomberg 2018 via Wikipedia: ca. 1.300 $/h).
- **Rechtslage/Risiko:** **hohes Compliance-Risiko** (Weitergabe wesentlicher nichtöffentlicher Informationen, MNPI). Es gab bereits Insider-Skandale in der Branche, z. B. Primary Global Research (ungeprüft im Detail).
- **Lohnt sich, wenn …** nie, für dieses Projekt.

---

## Akademische Datensätze

### Kenneth-French-Datenbibliothek (gratis, zum Vergleich)
- **Link:** https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- **Was es bringt:** Faktorrenditen (Markt, SMB, HML, Momentum usw.), aus CRSP und Compustat abgeleitet, **kostenlos und öffentlich**.
- **Potenzial: 4/5.** Damit lassen sich Arena-Renditen gegen Standardfaktoren prüfen ("Ist der Agent nur ein Momentum-Fonds?").
- **Verletzte Bedingung:** Keine. Eine Quellenangabe ist üblich.
- **Kosten:** 0 €.
- **Aufwand:** Gering (CSV/ZIP).
- **Rechtslage/Risiko:** Gering.
- **Lohnt sich, wenn …** sofort. Gehört eigentlich in den "machbar"-Teil des Tresors.

### WRDS (Wharton Research Data Services) als Zugangsplattform
- **Link:** https://wrds-www.wharton.upenn.edu/
- **Was es bringt:** Die zentrale Plattform, über die Universitäten CRSP, Compustat, TAQ, OptionMetrics, I/B/E/S usw. beziehen.
- **Potenzial: 2/5.** Die Daten sind Goldstandard, aber unerreichbar und für Papierhandel nicht nötig.
- **Verletzte Bedingung:** Nur für Angehörige lizenzierter Institutionen. Nutzung "for academic and non-commercial research only". Veröffentlichung und Weitergabe der Daten sind verboten.
- **Kosten:** Für Institutionen; 2016 wurde für eine mittelgroße Universität "über 60.000 $/Jahr" genannt. Einen Privattarif gibt es nicht (nicht gefunden, Stand 2026). Quelle: https://edesiderata.crl.edu/resources/wharton-research-data-services-wrds
- **Aufwand:** Hoch (Uni-Anbindung nötig).
- **Rechtslage/Risiko:** Den Zugang eines Uni-Freundes zu nutzen wäre Kontenmissbrauch und ein Lizenzbruch, das ist tabu. Daten oder abgeleitete Rohreihen in ein öffentliches Repo zu stellen ist ein Lizenzbruch.
- **Lohnt sich, wenn …** Rouven selbst an einer Hochschule eingeschrieben oder angestellt ist (z. B. Gasthörer- oder Fernstudium; ob das reicht, regelt die jeweilige Uni-Lizenz, ungeprüft). Ergebnisse dann nur aggregiert veröffentlichen.

### CRSP (Aktienrenditen, survivorship-frei)
- **Link:** https://www.crsp.org/
- **Was es bringt:** Saubere US-Aktienhistorie inkl. delisteter Titel, also ohne Survivorship-Bias.
- **Potenzial: 2/5.** Für langfristige Aktien-Backtests relevant, für die Arena kaum.
- **Verletzte Bedingung:** Lizenz nötig, akademisch über WRDS, kommerziell direkt über CRSP per Anfrageformular.
- **Kosten:** Nicht öffentlich. Anfrage an subscriptions@crsp.org (Stand 2026).
- **Aufwand:** Hoch.
- **Rechtslage/Risiko:** Veröffentlichung verboten.
- **Lohnt sich, wenn …** man ernsthaft Faktor-Backtests auf US-Aktien rechnen will. Sonst reicht Kenneth French (unten).

### OptionMetrics IvyDB
- **Link:** https://optionmetrics.com/
- **Was es bringt:** Historische Optionspreise, implizite Volatilität, Griechen.
- **Potenzial: 2/5.** Implizite Volatilität wäre als Risiko-Signal für Aktien- und Krypto-Agenten interessant. Krypto-IV (z. B. Deribit-DVOL) ist teils gratis (ungeprüft).
- **Verletzte Bedingung:** Lizenz.
- **Kosten:** Nicht öffentlich (ungeprüft).
- **Aufwand:** Hoch.
- **Rechtslage/Risiko:** Veröffentlichung verboten.
- **Lohnt sich, wenn …** ein Options-Agent ernsthaft geplant wäre. Derzeit nein.

### I/B/E/S (Analystenschätzungen, LSEG)
- **Link:** https://www.lseg.com/en/data-analytics/financial-data/company-data/ibes-estimates (ungeprüft)
- **Was es bringt:** Konsens-Schätzungen und Revisionen. Earnings-Surprise-Strategien bauen darauf auf.
- **Potenzial: 2/5.** Ein relevantes Signal, aber nur lizenziert. Gratis-Alternativen sind Yahoo-Earnings-Schätzungen, deren Nutzungsbedingungen ebenfalls zu beachten sind.
- **Verletzte Bedingung:** Lizenz.
- **Kosten:** Nicht öffentlich (ungeprüft).
- **Aufwand:** Hoch.
- **Rechtslage/Risiko:** Veröffentlichung verboten.
- **Lohnt sich, wenn …** nie für dieses Projekt.

### Compustat (Fundamentaldaten)
- **Link:** https://www.spglobal.com/marketintelligence/ (S&P Global)
- **Was es bringt:** Standardisierte Bilanzdaten, auch historisch "point in time".
- **Potenzial: 1/5.** Für die kurzfristige Arena kaum relevant. SEC-XBRL-Daten (EDGAR) gibt es gratis.
- **Verletzte Bedingung:** Lizenz, Uni über WRDS oder kommerziell über S&P.
- **Kosten:** Kommerziell im fünfstelligen Bereich (ungeprüft).
- **Aufwand:** Hoch.
- **Rechtslage/Risiko:** Veröffentlichung verboten.
- **Lohnt sich, wenn …** nie für dieses Projekt.

### TAQ (NYSE Trade and Quote)
- **Link:** https://www.nyse.com/market-data/historical (ungeprüft)
- **Was es bringt:** Tick-genaue US-Trades und Quotes für Mikrostruktur-Forschung.
- **Potenzial: 1/5.** Riesige Datenmengen, passt nicht zu GitHub Actions.
- **Verletzte Bedingung:** Lizenz.
- **Kosten:** Kommerziell hoch (ungeprüft), akademisch über WRDS.
- **Aufwand:** Sehr hoch.
- **Rechtslage/Risiko:** Veröffentlichung verboten.
- **Lohnt sich, wenn …** nie für dieses Projekt.

---

## Echtgeld-Zugang, Broker und Regulierung (DE)

> Stand der Recherche: 30.10.2026. **Keine Rechts- oder Steuerberatung**, nur eine sachliche Einordnung für das Hobby-Projekt. Es gibt hier keine Hinweise zum Umgehen von Geo-Sperren (VPN o. Ä.): Wer eine Sperre umgeht, verstößt gegen die AGB und riskiert eingefrorene Guthaben und rechtliche Folgen. Angaben ohne Primärbeleg sind mit „(ungeprüft)“ markiert. Gebühren ändern sich oft, deshalb vor jedem Echtgeld-Ja auf der Anbieterseite gegenprüfen.
>
> Ausgangslage im Projekt: Echtgeld ist „vorbereitet, aktiv nur nach ausdrücklichem Ja“. Papierhandel bleibt die Grundeinstellung.

Bewertungsschema „Potenzial 1–5“: Wie viel bringt der echte Zugang dem Projekt (realistische Fills, Lerneffekt, Daten) gegenüber dem Papierhandel, unter Berücksichtigung der Hürden für einen Privatanleger mit Wohnsitz in Deutschland?

### Interactive Brokers (IBKR, Ireland Limited)

- **Links:** https://www.interactivebrokers.ie · TWS API: https://www.interactivebrokers.com/docs/tws-api/ · Marktdaten: https://www.interactivebrokers.com/en/pricing/market-data-pricing.php
- **Was es bringt:**
  - einen vollwertigen Broker mit API (TWS/IB Gateway, Client Portal Web API) für Aktien, ETFs, Optionen und Futures (inkl. Eurex und CME-Krypto-Futures).
  - eine Paper-Trading-Umgebung mit identischer API. Damit wird der Umstieg vom Papier- auf den Echtbetrieb zur reinen Konfigurationsfrage.
- **Potenzial: 4/5.** Für Aktien, ETFs und Derivate der realistischste Weg zu Echtgeld aus Deutschland.
- **Verletzte Bedingung:** Konto/KYC (Angemessenheitstest für Derivate) und laufende Kosten (Marktdaten). Rechtlich gibt es kein Problem, EU-Kunden werden über die IBKR Ireland Limited (Aufsicht durch die Central Bank of Ireland) betreut (ungeprüft im Detail).
- **Kosten (Sekundärquellen, ungeprüft gegen die offizielle Preisliste):**
  - IBKR Pro Tiered auf Xetra: 0,05 % des Ordervolumens, mindestens 1,25 €, höchstens 29 €. Fixed: mindestens 3 €.
  - Keine Depot- oder Inaktivitätsgebühr. FX-Konvertierung 0,002 %, mindestens 2 USD.
  - IBKR Lite gibt es in der EU nicht.
  - Quelle: https://freenance.io/products/interactive-brokers-review-european-investors-2026
- **Marktdaten:**
  - Kostenlos: US-Echtzeitdaten von Cboe One und IEX (nicht konsolidiert, ohne NBBO) sowie bis zu 100 Snapshots pro Monat.
  - „US Securities Snapshot and Futures Value Bundle“: etwa 10 USD/Monat für Non-Professionals, bei ausreichendem Kommissionsvolumen wird die Gebühr erlassen.
  - Die API nutzt dieselben Abos wie die TWS.
  - Quelle: https://www.interactivebrokers.com/en/pricing/market-data-pricing.php
- **Aufwand:** mittel. Das Gateway muss laufen (täglicher Re-Login bzw. 2FA), die API hat Pacing-Limits.
- **Umstiegspunkt:** lohnt sich, wenn eine Aktien- oder ETF-Strategie im Papierhandel über mindestens 3–6 Monate stabil besser als der Benchmark abschneidet und die erwarteten Erträge die Marktdatenkosten von etwa 10–30 USD/Monat deutlich übersteigen.

### Kraken (Spot + MiFID-Derivate EU)

- **Links:** https://www.kraken.com · EU-Derivate: https://www.businesswire.com/news/home/20250520169459/en/ · Gebührenaktion: https://blog.kraken.com/product/kraken-derivatives/eea-futures-30-days-no-trading-fees
- **Was es bringt:**
  - Spot unter MiCA.
  - Perpetuals und Futures im EWR unter MiFID II über Payward Europe Digital Solutions (CY), CySEC-lizenziert, seit Mai 2025.
  - Eine ausgereifte REST- und WebSocket-API. Damit kommt Kraken den Perp-Strategien des Projekts am nächsten.
- **Potenzial: 4/5** für den Krypto-Teil (Spot und Perps).
- **Einschränkungen:**
  - Für EWR-Retail ist der Hebel auf etwa 10x begrenzt. 100x gibt es nur für „Rest of World“ (Sekundärquelle).
  - Funding wird in der EU stündlich abgerechnet.
  - Vor dem Derivatehandel steht ein Angemessenheitstest.
- **Kosten:** Für neue EWR-Futures-Kunden fallen 30 Tage lang 0 Maker- und Taker-Gebühren an (bis 10 Mio. USD Volumen). Die regulären Sätze für EU-Perps habe ich nicht belegt (ungeprüft, etwa 0,02 % Maker und 0,05 % Taker).
- **Rechtslage:** Kraken ist in der EU lizenziert. Es gibt die übliche Risikowarnung für Derivate. In Sekundärquellen wird diskutiert, dass ESMA Perps als CFDs einordnen könnte; das würde für Retail einen noch niedrigeren Hebel bedeuten (ungeprüft): https://cryptoticker.io/en/perpetuals-mifid-classification-leverage-cap/
- **Umstiegspunkt:** lohnt sich, wenn eine Perp-Strategie im Papierhandel nach Gebühren und Funding positiv ist **und** mit maximal 10x (realistisch 1–3x) funktioniert.

### Trading 212 (API)

- **Links:** https://docs.trading212.com · https://www.trading212.com
- **Was es bringt:** kommissionsfreien Aktien- und ETF-Handel mit offizieller API, die eine Demo- und eine Live-Umgebung hat.
- **Potenzial: 3/5** für einfache Aktien- und ETF-Strategien mit niedriger Frequenz.
- **Einschränkungen laut Doku:**
  - Beta-Status, nur für Invest- und Stocks-ISA-Konten.
  - Live sind nur **Market Orders** möglich.
  - Order-Endpunkte sind **nicht idempotent**: Wiederholte Requests können doppelte Orders erzeugen.
  - Rate-Limits gelten pro Konto. Optional lassen sich API-Keys auf bestimmte IP-Adressen beschränken.
- **Kosten:** keine Kommission. FX-Gebühr etwa 0,15 % (ungeprüft).
- **Rechtslage:** EU-regulierter Broker (Trading 212 Markets Ltd., Zypern, CySEC (ungeprüft)). Konten für deutsche Kunden sind möglich (ungeprüft).
- **Umstiegspunkt:** lohnt sich für kleine, langsame Aktien- und ETF-Strategien mit wenigen Orders am Tag, wenn Market Orders ausreichen. Wer Limit-Orders und Derivate braucht, ist bei IBKR besser aufgehoben.

### Coinbase

- **Links:** https://www.coinbase.com · MiCA: https://www.financemagnates.com/cryptocurrency/coinbase-announces-eu-mica-license-from-luxembourg-regulator/
- **Fakten:**
  - MiCA-Lizenz über die luxemburgische CSSF (Coinbase Luxembourg S.A., Juni 2025).
  - Zuvor gab es eine BaFin-Lizenz für Kryptoverwahrung und -handel (Coinbase Germany GmbH).
  - Die Advanced Trade API ist verfügbar.
  - Den Derivatestatus für EU-Retail habe ich nicht belegt (ungeprüft).
- **Potenzial: 3/5** für Krypto-Spot (seriös, gute API), offen für Derivate.
- **Kosten:** Maker/Taker im Advanced Trade nach Volumenstufen (ungeprüft für 2026).
- **Umstiegspunkt:** lohnt sich als Alternative oder Zweitbörse zu Kraken für Spot-Strategien.

### Alpaca

- **Links:** https://alpaca.markets · Eignung: https://alpaca.markets/learn/account-eligibility/
- **Was es bringt:** eine sehr einfache REST-API und eine kostenlose Paper-Trading-API, auch für Nicht-Kunden nutzbar.
- **Potenzial: 2/5.** Als Papier- und Datenquelle top, für Echtgeld aus Deutschland kaum zugänglich.
- **Verletzte Bedingung:** Konto/KYC.
  - Retail-Konten richten sich primär an US-Residenten.
  - Für Nicht-US-Personen gab es ein Invite-only-Programm (laut Hilfe-Seite, undatiert, u. a. 30.000 USD Mindesteinlage) (ungeprüft, ob es noch besteht).
  - Die Übernahme von WealthKernel im April 2026 („Alpaca Europe“, Lizenzen in UK und Spanien) und der Xetra-Handel ab Juli 2026 sind B2B-Angebote für Broker-Partner, kein Direktzugang für Privatkunden: https://www.businesswire.com/news/home/20260421441080/en/ · https://alpaca.markets/blog/alpaca-launches-german-equities-trading-via-deutsche-borse-xetra-for-broker-partners/
- **Umstiegspunkt:** lohnt sich, wenn Alpaca Europe ein Retail-Angebot für EU-Privatkunden startet. Bis dahin nur als Paper- und Daten-API nutzen.

### Bitpanda (und One Trading)

- **Links:** https://www.bitpanda.com · MiCA-Meldung: https://www.coindesk.com/policy/2025/01/27/bitpanda-secures-mica-license-from-german-regulator · One Trading: https://blog.bitpanda.com/en/bitpanda-pro-becomes-one-trading-after-completing-successful-series
- **Was es bringt:** Krypto-Spot unter MiCA-Lizenz, einen Anbieter aus dem DACH-Raum mit deutschsprachigem Support.
- **Potenzial: 2/5.** Rechtlich sauber, aber eine Handels-API ist für Privatkunden unklar.
- **Fakten:**
  - MiCA-Lizenz von der BaFin (Januar 2025), dazu eine weitere Lizenz in Österreich.
  - Die frühere Bitpanda Pro wurde als One Trading ausgegliedert (MiFID-Handelsplatz geplant).
  - Eine API für automatisierten Handel bei Bitpanda bzw. One Trading habe ich nicht verifiziert (ungeprüft).
- **Kosten:** Spreads bzw. Gebühren im Broker-Modell (ungeprüft).
- **Umstiegspunkt:** lohnt sich, wenn eine dokumentierte Trading-API für Privatkunden verfügbar ist und nur Krypto-Spot gehandelt werden soll.

### Bybit (Bybit EU)

- **Links:** https://www.bybit.eu · https://cointelegraph.com/news/bybit-secures-mica-license-establishes-eu-hq-in-vienna
- **Fakten:**
  - MiCA-Lizenz der österreichischen FMA für die Bybit EU GmbH (Mai 2025).
  - Bybit EU ist nach Sekundärquellen nur Spot. Für Derivate wäre eine zusätzliche MiFID-Erlaubnis nötig (ungeprüft).
  - Die globale Plattform (inkl. Perps) hat den Zugang für EWR-Nutzer vor dem Ende der MiCA-Übergangsfrist am 01.07.2026 eingeschränkt: https://www.mexc.com/news/1183665 (Sekundärquelle).
- **Potenzial: 2/5.** Spot ist möglich, die Perps (der eigentliche Mehrwert von Bybit) sind für EU-Retail nicht verfügbar.
- **Umstiegspunkt:** lohnt sich, wenn Bybit EU eine MiFID-Lizenz für Derivate erhält.

### Deribit (Krypto-Optionen)

- **Links:** https://www.deribit.com · Restricted Jurisdictions: https://support.deribit.com/hc/en-us/articles/25944487427741-Restricted-Jurisdictions · Übernahme: https://blockworks.co/news/coinbase-to-acquire-deribit-in-2-9b-deal
- **Was es bringt:** den liquidesten Markt für BTC- und ETH-Optionen mit einer sehr guten API und einem Testnet. Das passt exakt zum Papier-Modul des Projekts.
- **Potenzial: 2/5.**
- **Fakten:**
  - Coinbase hat im Mai 2025 angekündigt, Deribit für etwa 2,9 Mrd. USD zu übernehmen (Abschluss erwartet Ende 2025; der Vollzug ist laut Sekundärquelle erfolgt (ungeprüft)).
  - Deutschland bzw. der EWR steht nicht auf der offiziellen Restricted-Liste. Eingeschränkt sind u. a. die USA und das UK (dort kein Retail).
  - Die Deribit FZE (Dubai, VARA) richtet sich primär an professionelle Kunden. Welche Gesellschaft EWR-Retail-Kunden bedient und ob sie das darf, ist ungeklärt (ungeprüft).
- **Rechtslage/Risiko:** Ein Nicht-EU-Anbieter von Derivaten ohne MiFID-Erlaubnis für die EU bewegt sich gegenüber deutschen Privatkunden in einer regulatorischen Grauzone. Für den Kunden selbst ist die Nutzung nicht verboten, er hat aber keinen EU-Anlegerschutz (Einordnung (ungeprüft)).
- **Umstiegspunkt:** lohnt sich, wenn Coinbase Deribit-Optionen über eine EU-lizenzierte Gesellschaft für EWR-Retail anbietet. Bis dahin Testnet und Papierhandel nutzen.

### Kalshi aus Deutschland

- **Links:** https://kalshi.com · https://help.kalshi.com/en/articles/14026044-can-i-trade-on-kalshi-from-outside-the-united-states · Member Agreement: https://kalshi.com/docs/kalshi-member-agreement.pdf
- **Was es bringt:** eine CFTC-regulierte Eventbörse (DCM) mit einer guten REST- und WebSocket-API.
- **Potenzial: 1–2/5.** Kalshi ist technisch für Nicht-US-Nutzer geöffnet, für Deutschland ist das aber rechtlich heikel.
- **Fakten:**
  - Laut Help Center ist Handel „from many countries“ möglich, die Länderliste steht im Member Agreement. Einzahlung per Debitkarte (Visa/Mastercard), per Wire (mindestens 1.000 USD) oder in Krypto. Keine App außerhalb der USA, nur Web.
  - Ankündigung im Oktober 2025: Kalshi sei in mehr als 140 Ländern verfügbar (Sportico: https://www.sportico.com/business/sports-betting/2025/kalshi-international-countries-access-1234874388/). Seit März 2026 gibt es eine Kooperation mit XP in Brasilien (Bloomberg).
  - Laut Wikipedia haben bis Juni 2026 55 Jurisdiktionen den Zugang eingeschränkt: https://en.wikipedia.org/wiki/Kalshi
  - Der Status für Deutschland ist widersprüchlich. Sekundärquellen nennen Deutschland mal als „unterstützt“, mal als „close-only“. Primär nicht verifiziert, weil das Member Agreement nicht abrufbar war (HTTP 429): **(ungeprüft)**.
- **Kosten:**
  - Taker-Gebühr = 0,07 × C × P × (1−P), aufgerundet auf den Cent. Maximal etwa 1,75 ¢ je Kontrakt bei 50 ¢.
  - Maker-Koeffizient 0,0175, in manchen Märkten 0.
  - Quellen: https://kalshi.com/docs/kalshi-fee-schedule.pdf und die CFTC-Regeleinreichung https://cftc.gov/filings/orgrules/rule091222kexdcm003.pdf
- **Rechtslage/Risiko:** Selbst wenn die AGB Deutschland zulassen, gilt nach Auffassung der GGL jedes Angebot, das Personen in Deutschland die Teilnahme ermöglicht, als unerlaubtes Glücksspiel nach dem GlüStV 2021 (vgl. GGL-Warnung und Statement vom 19.06.2026). Was nach den Kalshi-AGB erlaubt ist, ist damit nicht automatisch auch nach deutschem Recht erlaubt.
- **Aufwand:** technisch mittel (KYC, Einzahlung in USD).
- **Umstiegspunkt:** lohnt sich, wenn das Member Agreement Deutschland eindeutig zulässt **und** die GGL bzw. der Gesetzgeber Event-Kontrakte klar einordnet, etwa als Finanzinstrument unter BaFin-Aufsicht statt als Glücksspiel. Bis dahin bleibt es beim Papierhandel.

### Hyperliquid / dYdX (DEX-Perps)

- **Links:** https://hyperliquid.xyz · https://dydx.exchange
- **Was es bringt:** On-Chain-Perps ohne KYC mit offener API. Technisch ist das attraktiv.
- **Potenzial: 1–2/5.** Die rechtlichen und technischen Risiken überwiegen.
- **Rechtslage/Risiko:**
  - Hyperliquid ist in keinem EU-Register für Kryptodienstleister (CASP) eingetragen: https://cryptoticker.io/de/hyperliquid-ohne-mica-zulassung/
  - Die britische FCA hat Hyperliquid auf ihre Warnliste gesetzt (21.05.2026): https://fintelegram.com/hyperliquid-after-the-fca-warning-defi-branding-meets-regulated-derivatives-reality/
  - Die Hyperliquid Policy Center wirbt in der EU dafür, Perps unter MiFID II einzuordnen: https://theblock.co/news/regulation/2026-10-01-hyperliquid-circle-mica-review-417452
  - Eine ESMA-Maßnahme speziell gegen Hyperliquid habe ich nicht gefunden.
  - Dazu kommen Smart-Contract-, Oracle- und Liquidationsrisiken, und es gibt keinen Anlegerschutz.
  - Die Frontends können Geo-Sperren haben. Diese werden hier bewusst nicht weiter behandelt.
  - dYdX: Status für die EU nicht separat recherchiert (ungeprüft).
- **Umstiegspunkt:** lohnt sich erst, wenn die EU Perps klar einordnet (MiFID/MiCA) und ein regulierter Zugang existiert. Bis dahin höchstens Marktdaten lesen.

### Polymarket (international) aus Deutschland

- **Link:** https://polymarket.com · Geo-Regeln: https://docs.polymarket.com/api-reference/geoblock · Hilfe: https://help.polymarket.com/en/articles/13364163-geographic-restrictions · AGB: https://polymarket.com/tos
- **Was es bringt:** den größten Prognosemarkt mit echtem Orderbuch (CLOB) und echten Fills statt simulierter Fills.
- **Potenzial: 1/5.** Deutschland ist gesperrt. Lesen geht weiterhin, Handeln nicht.
- **Verletzte Bedingung:** rechtlich/Geo (hart).
  - Die Polymarket-Doku führt Deutschland (DE) unter „Regulatory-Restricted Jurisdictions (Close-Only on Frontend and API)“.
  - Die Hilfe-Seite sagt dazu: „Germany: Trading is prohibited. Existing positions must be held until market resolution … Market data and commenting features are available.“
  - Nach den AGB dürfen Nutzer in einer Restricted Jurisdiction nur die „Content Features“ nutzen.
- **Kosten (Stand 2026, Sekundärquellen):**
  - Seit 2026 gibt es Taker-Gebühren: ab 05.01.2026 auf Crypto-Märkten, ab 18.02.2026 auf Sport, ab 30.03.2026 global („Fee Structure V2“).
  - Formel: Kontrakte × Kategoriesatz × p × (1−p). Kategoriesätze etwa Crypto 0,07, Sport 0,03, Politik/Finanzen 0,04. Maker zahlen 0 (ungeprüft gegen die aktuelle Doku).
  - Quellen: https://www.financemagnates.com/cryptocurrency/polymarket-introduces-dynamic-fees-to-curb-latency-arbitrage-in-short-term-crypto-markets/ · https://docs.polymarket.com/trading/fees
- **Aufwand:** technisch gering, weil der CLOB-Client vorhanden ist. Rechtlich ist es nicht machbar.
- **Rechtslage/Risiko:**
  - Die GGL hat am 05.09.2025 öffentlich vor „illegalen Gesellschaftswetten“ gewarnt und Polymarket dabei namentlich genannt: https://www.gluecksspiel-behoerde.de/de/news/ggl-warnt-vor-teilnahme-an-illegalen-gesellschaftswetten
  - Nach Darstellung der GGL sind solche Plattformen nach dem GlüStV 2021 nicht erlaubnisfähig und nicht lizenziert. Eine Teilnahme aus Deutschland sei unzulässig.
  - Am 19.06.2026 hat sich die GGL dem gemeinsamen Statement von neun europäischen Glücksspielaufsichten zu Prediction Markets angeschlossen: https://www.gluecksspiel-behoerde.de/de/news/ggl-schliesst-sich-gemeinsamem-statement-europaeischer-gluecksspielaufsichtsbehoerden-zu-herausforderungen-durch-prognosemaerkte-prediction-markets-an (PDF: https://www.gluecksspiel-behoerde.de/images/pdf/20260617_Joint_Statement_by_gambling_regulators.pdf)
  - Laut DW sagt die GGL, dass sie Hinweise auf illegales Glücksspiel an die Strafverfolgung weitergibt: https://www.dw.com/en/germany-betting-on-elections-is-illegal-but-possible/a-76712766
  - Einordnung: Auch für Spieler ist die Teilnahme an unerlaubtem Glücksspiel nach § 285 StGB grundsätzlich strafbewehrt (allgemeine Rechtslage; die Anwendung auf Prognosemärkte ist nicht gerichtlich geklärt (ungeprüft)).
  - Eine förmliche Untersagungsverfügung der GGL gegen Polymarket habe ich nicht gefunden (ungeprüft). Belegt sind nur die Warnungen und das gemeinsame Statement.
- **Umstiegspunkt:** lohnt sich erst, wenn Deutschland aus der Restricted-Liste entfernt wird **und** es eine deutsche Erlaubnis oder eine klare EU-Regelung gibt. Bis dahin bleibt es bei Read-only-Marktdaten und Papierhandel. Das ist bereits der heutige Stand.

### Polymarket US (QCX LLC, ehem. QCEX)

- **Links:**
  - https://www.prnewswire.com/news-releases/polymarket-acquires-cftc-licensed-exchange-and-clearinghouse-qcex-for-112-million-302509626.html
  - https://www.reuters.com/sustainability/boards-policy-regulation/polymarket-receives-green-signal-cftc-us-return-2025-09-03/
  - CFTC-DCM-Eintrag: https://www.cftc.gov/IndustryOversight/IndustryFilings/TradingOrganizations/49571
- **Was es bringt:** eine CFTC-regulierte Börse (DCM) mit eigener Clearingstelle (DCO) für US-Personen.
- **Potenzial: 1/5** für einen Betreiber mit Wohnsitz in Deutschland.
- **Verletzte Bedingung:** Konto/KYC und Geo. Das Angebot richtet sich an US-Nutzer.
- **Fakten:**
  - Übernahme von QCEX (Börse plus Clearinghouse) für 112 Mio. USD, gemeldet am 21.07.2025.
  - Grünes Licht der CFTC für die US-Rückkehr im September 2025 (Reuters).
  - Laut Sekundärquelle ein Antrag vom 28.04.2026, US-Nutzer an die Offshore-Börse anzubinden (ungeprüft).
  - Eigener Gebührenplan ab 01.07.2026 (ungeprüft): https://www.rivermarkets.com/insights/polymarket-us-fees.html
- **Umstiegspunkt:** nur relevant, wenn der Betreiber in die USA zieht oder Polymarket US Nicht-US-Personen zulässt. Das ist nicht absehbar.

### Betfair Exchange

- **Links:** https://www.betfair.com/exchange · Support (DE): https://support.betfair.com/de/app/answers/detail/5939-wettborse-kann-ich-in-deutschland-oder-osterreich-die-wettborse-exchange-nutzen · Developer: https://developer.betfair.com/
- **Was es bringt:** die liquideste Wettbörse für Sport und Politik mit einer ausgereiften API (Betting API und Stream API).
- **Potenzial: 1/5** aus Deutschland.
- **Verletzte Bedingung:** Geo. Laut Betfair-Support steht die Wettbörse Kunden in Deutschland bzw. Österreich „bedauerlicherweise nicht zur Verfügung“.
- **Kosten:**
  - Für einen Live App Key fällt eine einmalige Aktivierungsgebühr von **£499** an, die vom Betfair-Konto abgebucht wird: https://support.developer.betfair.com/hc/en-us/articles/115003864531-Are-there-any-costs-associated-with-API-access
  - Der Delayed Key (Entwicklung) ist kostenlos.
  - Dazu kommt die Marktkommission (UK-Standard etwa 5 % auf Nettogewinne je Markt (ungeprüft für 2026)).
- **Rechtslage:** Betfair International plc ist von der irischen GRAI lizenziert. Auf der GGL-Whitelist (https://www.gluecksspiel-behoerde.de/de/fuer-spielende/uebersicht-erlaubter-anbieter-whitelist) habe ich keine Wettbörse gefunden (ungeprüft, da die Whitelist dynamisch ist).
- **Umstiegspunkt:** nur bei einem Wohnsitz in einem Land, in dem die Exchange zugelassen ist (z. B. UK/IE), oder wenn Deutschland Börsenwetten erlaubt.

### Smarkets

- **Links:** https://smarkets.com · AGB: https://help.smarkets.com/hc/en-gb/articles/213469085-Smarkets-Terms-and-Conditions (Abruf mit HTTP 403 blockiert)
- **Was es bringt:** eine Wettbörse und ein Prognosemarkt mit niedriger Kommission und API.
- **Potenzial: 1/5.**
- **Verletzte Bedingung:** voraussichtlich Geo/rechtlich. Eine primäre Länderliste habe ich nicht gefunden (ungeprüft). Ohne deutsche Erlaubnis gilt die oben beschriebene Einordnung durch die GGL.
- **Kosten:** etwa 2 % Kommission (ungeprüft).
- **Umstiegspunkt:** wie bei Betfair.

### Matchbook

- **Link:** https://www.matchbook.com
- **Fakten:** Matchbook hat Betdaq übernommen. Betdaq wurde zum 4. November geschlossen und in Matchbook integriert: https://www.thelines.com/uk/legal-betting/matchbook-acquires-betdaq-amid-prediction-market-interest/
  - Laut einem deutschen Forenbeitrag (undatiert) sind Neuanmeldungen aus Deutschland ausgesetzt: https://ninjabetgermany.nodebb.com/post/10173 (ungeprüft).
- **Potenzial: 1/5.**
- **Umstiegspunkt:** wie bei Betfair.

### Binance

- **Fakten:**
  - Bis zum 01.07.2026 hatte Binance keine MiCA-Lizenz. Der Antrag lief in Griechenland (HCMC), Berichten zufolge drohte die Ablehnung: https://paymentexpert.com/2026/06/17/binance-mica-licence-denied-europe/ · https://www.financemagnates.com/cryptocurrency/binance-says-it-remains-fully-committed-to-securing-our-mica-license-as-eu-exit-risk-looms/
  - Laut ESMA gibt es keine Verlängerung der Übergangsfrist.
  - Den aktuellen Stand nach dem 01.07.2026 habe ich nicht verifiziert (ungeprüft). Abzugleichen im ESMA-Register: https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica
- **Potenzial: 1/5.** Der Regulierungsstatus in der EU ist unsicher, Echtgeld ist dort nicht empfehlenswert.
- **Umstiegspunkt:** lohnt sich, wenn Binance im ESMA-Register als CASP mit Passporting nach Deutschland eingetragen ist.

### PredictIt / Manifold (Kurznotiz)

- **PredictIt** richtet sich an US-Personen; für Deutschland ist kein Echtgeld-Zugang zu erwarten (ungeprüft, nicht separat recherchiert).
- **Manifold** ist ein Spielgeld-Markt ohne Echtgeld-Auszahlung, also faktisch schon Papierhandel (ungeprüft für den Stand 2026).

### Wettsteuer (Kontext Wettbörsen)

- Für online abgeschlossene Sportwetten fallen nach dem RennwLottG **5,3 % des Wetteinsatzes** an. Das ist eine Steuer auf den Einsatz, nicht auf den Gewinn, und wird meist an die Kunden weitergegeben: https://www.fimportal.de/api/v0/leistung-stammtexte/L100027/123527948/pvog/de/pdf
- Der BFH hat am 07.09.2021 (IX R 5/19) zur Rechtslage von 2012 entschieden, dass für den bloßen Betrieb einer Wettbörse keine Sportwettensteuer anfällt: https://rewis.io/urteile/urteil/8xv-07-09-2021-ix-r-519/ Ob das nach der Änderung des RennwLottG 2021 noch so gilt, ist ungeprüft.
- Folge für das Projekt: Eine Wettsteuer von 5,3 % auf den Einsatz würde Edge-Strategien mit dünnen Margen praktisch zerstören.

### KWG/BaFin: Brauche ich eine Erlaubnis?

- **Eigener automatisierter Handel mit eigenem Geld:**
  - Erlaubnispflichtig sind Finanzdienstleistungen für andere sowie bestimmte Formen des Eigenhandels nach § 1 Abs. 1a KWG und § 32 KWG.
  - Wer als Privatperson ausschließlich auf eigene Rechnung über einen zugelassenen Broker handelt, erbringt nach allgemeinem Verständnis keine Dienstleistung für andere und braucht keine Erlaubnis. Das gilt auch, wenn der Handel per API oder Bot läuft.
  - Belege: § 32 KWG https://www.gesetze-im-internet.de/kredwg/__32.html und das BaFin-Merkblatt zu Eigenhandel und Eigengeschäft (Fassung 2018). Eine Aussage dort speziell zu natürlichen Personen habe ich nicht primär geprüft (ungeprüft).
  - Die Regeln für algorithmischen Handel und Hochfrequenzhandel (MiFID II, § 80 WpHG) richten sich an Wertpapierfirmen bzw. HFT-Firmen mit direktem Marktzugang, nicht an Privatkunden eines Brokers (Einordnung (ungeprüft)).
- **Signale, Copy-Trading oder das Verwalten fremden Geldes:**
  - Wer anderen konkrete Handelsempfehlungen oder Signale gibt, kann eine Anlageberatung oder Anlageempfehlung erbringen. Wer fremde Depots automatisch handelt, betreibt Finanzportfolioverwaltung.
  - Beides ist grundsätzlich erlaubnispflichtig (KWG/WpIG) bzw. anzeigepflichtig (Art. 20 MAR für Anlageempfehlungen).
  - Präzedenzfall: ayondo hat Social Trading unter einer BaFin-Erlaubnis für Finanzportfolioverwaltung angeboten.
  - Quelle (Kanzlei): https://fin-law.de/wp-content/uploads/2026/05/Social-Trading-and-Signal-Following-Welche-aufsichtsrechtlichen-Aspekte-mussen-Anbieter-bedenken_PR.pdf
  - **Konsequenz für die Arena:** Ergebnisse privat halten. Eine öffentliche „Folgt meinem Bot“-Funktion, zahlende Abonnenten oder Fremdgeld nur nach Fachberatung.
- **MiCA aus Sicht von Privatanlegern:**
  - Seit 01.07.2026 ist die Übergangsfrist abgelaufen. In der EU dürfen nur noch zugelassene CASPs Kryptodienstleistungen erbringen.
  - Für Anleger heißt das: Mindeststandards für Verwahrung, Trennung von Kundenvermögen, Beschwerdeverfahren und Marketing.
  - Es gibt **keine** Einlagensicherung und keine Haftung für Kursverluste.
  - Derivate auf Krypto fallen in der Regel **nicht** unter MiCA, sondern unter MiFID II.
  - Vor jeder Börse prüfen: Steht der Anbieter im ESMA-Register?

### Steuern-Kurzüberblick

- **Kapitalerträge (Aktien, ETFs, Optionen und Futures bei Brokern):**
  - Abgeltungsteuer 25 % zzgl. Solidaritätszuschlag (ggf. Kirchensteuer), Sparer-Pauschbetrag 1.000 € (Einzelperson).
  - Ausländische Broker wie IBKR Ireland führen keine deutsche Abgeltungsteuer ab. Erträge müssen dann über die Anlage KAP erklärt werden (ungeprüft für die IBKR-Praxis 2026).
- **Verluste aus Termingeschäften:**
  - Die Beschränkung nach § 20 Abs. 6 Satz 5 und 6 EStG (Verrechnung nur mit Termingeschäften, Grenze 20.000 €) wurde durch das **JStG 2024** (BGBl. 05.12.2024) **ersatzlos gestrichen**. Sie gilt nicht mehr für alle offenen Fälle (§ 52 Abs. 28 EStG).
  - Quellen: https://cms.law/de/deu/legal-updates/verlustverrechnungsbeschraenkung-bei-termingeschaeften-gesetzgeber-schafft-vorschrift-ab · https://www.forvismazars.com/de/en/who-we-are/news/press-media/newsletters/newsletter-steuern/newsletter-steuern-1-2025/verlustverrechnung-bei-termingeschaeften
  - **Weiterhin gilt** der eigene Verrechnungstopf für Verluste aus Aktienverkäufen (§ 20 Abs. 6 Satz 4 EStG).
- **Krypto (private Veräußerungsgeschäfte, § 23 EStG):**
  - Steuerfrei nach mehr als 1 Jahr Haltedauer.
  - Darunter gilt der persönliche Steuersatz, mit einer Freigrenze von **unter 1.000 €** pro Jahr für alle privaten Veräußerungsgeschäfte zusammen (seit VZ 2024). Es ist eine Freigrenze, kein Freibetrag: Ab 1.000 € ist der gesamte Gewinn steuerpflichtig.
  - Quellen: https://www.gesetze-im-internet.de/estg/__23.html · https://stock3.com/news/kryptowaehrungen-versteuern-haltefristen-freigrenzen-und-steuerfallen-im-ueberblick-17282471
  - **Krypto-Derivate** (Perps, Futures, Optionen): Die Einordnung als Termingeschäft (§ 20 EStG, Abgeltungsteuer) oder als sonstige Einkünfte ist umstritten und hängt vom Produkt ab (ungeprüft, mit Steuerberater klären).
- **Wett- und Prognosemarkt-Gewinne:**
  - Gewinne aus Sportwetten und Glücksspiel sind bei Privatpersonen grundsätzlich **nicht einkommensteuerbar**. Ausnahme: gewerbliches bzw. „Berufsspieler“-Niveau, vgl. BFH X R 43/12 zu Poker: https://www.lto.de/recht/nachrichten/n/bfh-x-r-43-12-poker-gewinne-gewerbe-einkommensteuer/print.html
  - Bei Prognosemärkten ist die Einordnung **unklar**. Möglich sind Glücksspiel bzw. Wette (steuerfrei), Termingeschäft bzw. Finanzinstrument (§ 20 EStG) oder bei Krypto-Abwicklung ein Bezug zu § 23 EStG (USDC). Ein **systematischer, botgesteuerter Handel** spricht eher gegen eine reine Spiel-Einordnung. **Unklar, keine Belege gefunden.**
  - Angesichts der Sperre für Deutschland ist die Frage für das Projekt derzeit theoretisch.
- **DAC8 / KStTG:**
  - Das Kryptowerte-Steuertransparenzgesetz (BGBl. 2025 I Nr. 352) gilt seit **01.01.2026**.
  - Kryptodienstleister melden Transaktionen ihrer EU-Kunden an das BZSt. Erster Meldezeitraum ist 2026, Meldefrist 31.07.2027.
  - Quelle: https://www.forvismazars.com/de/en/who-we-are/news/press-media/newsletters/newsletter-steuern/newsletter-steuern-1-2026/dac8-meldepflicht-fuer-kryptotransaktionen-ab-2026
  - Folge für das Projekt: Jeder Bot-Trade bei einer Börse wird dem Finanzamt bekannt. Daher sollte das Projekt von Anfang an ein sauberes, exportierbares Trade-Journal führen (FIFO, Gebühren, Funding).

---

## Kostenpflichtige Marktdaten

> Stand der Recherche: 30.10.2026. Preise in USD pro Monat, falls nicht anders angegeben. Sie stammen von offiziellen Preisseiten, sofern verlinkt, sonst aus Drittquellen (Aggregatoren, Reviews) und sind dann so gekennzeichnet. „(ungeprüft)“ heißt: nicht an offizieller Stelle bestätigt.
>
> **Zwei Querschnitts-Punkte für alle Einträge:**
> 1. **Öffentlichkeit:** Fast alle Privatkunden-Lizenzen („Individual“, „Personal“, „Internal use only“, „No redistribution or display“) verbieten es, Rohdaten öffentlich anzuzeigen oder weiterzugeben. Das Repo, die Webseite **und die Logs von GitHub Actions in einem öffentlichen Repo** sind öffentlich. Zulässig wäre höchstens: Rohdaten nur flüchtig im Job verarbeiten und nur abgeleitete Entscheidungen bzw. eigene Kennzahlen veröffentlichen, und das auch nur, wenn die AGB das im Einzelfall erlauben (vorher lesen!). API-Keys gehören in die Secrets und dürfen nie in Logs oder Artefakten auftauchen.
> 2. **Latenz:** Geplante GitHub-Actions-Läufe laufen frühestens alle 5 Minuten und starten oft mit Verzögerung. Bezahlte Daten mit *niedriger Latenz* (Echtzeit-News, Websockets, Tick-Daten) verlieren damit fast ihren ganzen Wert. Sie lohnen sich erst auf eigener, dauerhaft laufender Infrastruktur (VPS).

### CoinGlass (API)
- **Link:** https://www.coinglass.com/pricing
- **Nutzen:** Börsenübergreifende Perp-Daten: Funding, Open Interest, Liquidationen, Long/Short-Ratios, ETF-Flows. Für Perps-Agenten sehr relevant.
- **Potenzial: 4/5.** Günstig, genau auf das Krypto-Perps-Segment zugeschnitten, und Aggregation über viele Börsen ist selbst mühsam. Bester Kandidat in dieser Liste.
- **Verletzt:** kostenpflichtig, Konto, Lizenz (Hobbyist und Startup nur für den persönlichen Gebrauch).
- **Kosten:** Hobbyist 29 $ (30 Requests/Min.), Startup 79 $ (80/Min.), Standard 299 $ (ab hier kommerziell), Professional 699 $. Laut Tracker am 28.06.2026 gesenkt von 35 bzw. 95 $ (Drittquellen 2026, offizielle Seite nicht ladbar, ungeprüft: https://dev.to/great-time-flies/coinglass-api-review-2026-is-it-worth-it-for-crypto-quant-traders-2bcf).
- **Aufwand:** gering.
- **Recht/Risiko:** Ohne Standard-Plan (299 $) keine kommerzielle Nutzung. Ob die Anzeige abgeleiteter Werte auf einer öffentlichen Hobbyseite erlaubt ist, steht in den AGB (ungeprüft). Rohdaten nicht veröffentlichen.
- **Lohnt sich, wenn …** Perps-Agenten dauerhaft laufen und Funding-, OI- oder Liquidations-Signale im Backtest einen Vorteil zeigen, der mehr als 29 $/Monat wert ist.

### Massive (ehem. Polygon.io)
- **Link:** https://massive.com/pricing · Umbenennung bestätigt: https://massive.com/blog/polygon-is-now-massive (30.10.2025)
- **Nutzen:** Saubere US-Aktien-API (REST und Websocket), lange Historie, Splits und Dividenden, dazu Finanzkennzahlen und Partner-Datensätze (Benzinga-News, ETF Global). Laut Startseite gibt es Zugang für KI-Agenten über x402 (Bezahlung pro Abfrage).
- **Potenzial: 3/5.** Deutlich zuverlässiger als kostenlose Scraper-Quellen, und das Benzinga-News-Add-on per API ist für LLM-Agenten interessant. Für Papierhandel auf Tages- oder Stundenbasis reichen aber auch kostenlose EOD-Daten.
- **Verletzt:** kostenpflichtig, Konto, Lizenz („Individual use only“).
- **Kosten (offizielle Seite, abgerufen 30.10.2026):** Stocks Basic 0 $; Starter 29 $; Developer 79 $; Advanced 199 $ (nur Non-Pro); Financials & Ratios 29 $; Benzinga, TMX und ETF Global je 99 $ pro Datensatz; jährliche Zahlung spart 20 %. Preise für Optionen und Krypto standen nicht auf der abgerufenen Seite (ungeprüft).
- **Aufwand:** gering (gut dokumentiertes REST-API, Python-Client).
- **Recht/Risiko:** Die Individual-Pläne gelten nur für den Eigengebrauch. Rohkurse auf der öffentlichen Seite anzuzeigen ist wahrscheinlich nicht erlaubt; dafür gibt es Business-Pläne. AGB prüfen.
- **Lohnt sich, wenn …** die kostenlosen Kursquellen (z. B. yfinance oder Stooq) regelmäßig ausfallen bzw. sperren und die Arena dadurch Läufe verliert, oder wenn die Agenten News-Volltexte per API bekommen sollen (Benzinga-Add-on).

### Tiingo
- **Link:** https://www.tiingo.com/about/pricing
- **Nutzen:** Sehr günstige EOD- und IEX-Intraday-Kurse, Fundamentaldaten, News-API und Krypto.
- **Potenzial: 3/5.** Bestes Preis-Leistungs-Verhältnis für Aktien und ETFs. Der Haken ist die Lizenz (siehe unten).
- **Verletzt:** Konto (der Free-Plan braucht schon einen Key), Lizenz, bei „Power“ zusätzlich kostenpflichtig.
- **Kosten (offiziell, abgerufen 30.10.2026):** Starter 0 $ (50 Requests/Std., 1.000/Tag, 500 Symbole/Monat); Power 30 $/Monat bzw. 300 $/Jahr (10.000 Requests/Std., 100.000/Tag); Business 50 $/Monat bzw. 499 $/Jahr für interne kommerzielle Nutzung; Redistribution kostet extra.
- **Aufwand:** gering.
- **Recht/Risiko:** **Ausdrücklich „Internal Use Only – you may not display or share the data with another person or organization“.** Das kollidiert direkt mit der öffentlichen Webseite. Nur abgeleitete Signale veröffentlichen, oder eine Redistribution-Lizenz kaufen.
- **Lohnt sich, wenn …** du einen stabilen Kurs-Feed brauchst und die Seite nur Portfolio-Werte und Trades zeigt, keine Kurstabellen. Vorher bei Tiingo nachfragen, ob abgeleitete Werte erlaubt sind.

### EODHD (EOD Historical Data)
- **Link:** https://eodhd.com/pricing · kommerziell: https://eodhd.com/commercial-pricing
- **Nutzen:** Weltweite EOD- und Intraday-Kurse (70+ Börsen, z. B. XETRA), Fundamentaldaten, Dividenden, ETFs. Interessant, falls die Arena auch europäische ETFs handeln soll.
- **Potenzial: 3/5.** Günstig und breit aufgestellt, für deutsche bzw. europäische Werte eine der wenigen bezahlbaren Quellen.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten (offizielle Seite, Snippet 2026):** EOD All World 19,99 $ (jährlich ca. 16,58 $); EOD+Intraday 29,99 $; Fundamentals ca. 59,99 $ (ungeprüft); All-In-One 99,99 $. Kommerziell ab 399 $/Monat.
- **Aufwand:** gering.
- **Recht/Risiko:** Private Pläne gelten nur für die persönliche Nutzung. Für eine öffentliche Anzeige braucht es den kommerziellen Plan ab 399 $.
- **Lohnt sich, wenn …** das Universum um EU- oder DE-Titel wächst und die kostenlosen Quellen dort lückenhaft sind.

### Financial Modeling Prep (FMP)
- **Link:** https://site.financialmodelingprep.com/pricing-plans
- **Nutzen:** Fundamentaldaten, Earnings-Kalender, Transkripte, Insider- und Kongress-Trades, Kurse. Sehr agentenfreundlich (einfache JSON-Endpunkte).
- **Potenzial: 3/5.** Viele „Story“-Daten für LLM-Agenten zu einem kleinen Preis.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten (offizielle Seite, Snippet 2026):** Starter 19 $ (statt 29 $), Premium 49 $ (statt 69 $), Ultimate 99 $ (statt 139 $), jeweils bei jährlicher Zahlung. Bandbreitenlimit über 30 Tage: Free 500 MB, Starter 20 GB, Premium 50 GB, Ultimate 150 GB. Eine Drittquelle nennt abweichend 22/59/149 $ (https://multiples.vc/compare/fmp-api-alternatives, ungeprüft).
- **Aufwand:** gering.
- **Recht/Risiko:** Die privaten Pläne erlauben keine Weitergabe. Für Anzeige und Weitergabe gibt es separate Build- bzw. Enterprise-Pläne (ungeprüft).
- **Lohnt sich, wenn …** die Agenten mit Earnings-, Insider- oder Transkript-Kontext messbar besser handeln als ohne (vorher mit dem Free-Tier testen).

### Amberdata / Laevitas (Krypto-Derivate, Deribit-Optionen)
- **Link:** https://www.amberdata.io/pricing (Inhalt nicht abrufbar) · https://www.laevitas.ch
- **Nutzen:** Kennzahlen zu Deribit-Optionen: IV-Oberflächen, Skew, Term Structure, GEX, Flow, Funding und Basis. Genau die Sicht, die Deribit-Optionsagenten bräuchten. Amberdata hat 2022 Genesis Volatility übernommen (https://www.coindesk.com/business/2022/10/05/digital-asset-data-provider-amberdata-acquires-crypto-analytics-company-genesis-volatility/). Eine Übernahme von Laevitas durch Amberdata ist **nicht** belegt.
- **Potenzial: 3/5 (Laevitas) bzw. 1/5 (Amberdata).** Laevitas ist für Privatnutzer bezahlbar, aber ein API gibt es laut Drittquelle erst im Enterprise-Plan. Vieles lässt sich aus dem kostenlosen Deribit-API selbst berechnen.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten:** Laevitas Free / Premium 50 $ / Enterprise 500 $ / Enterprise CME 600 $ (Drittquellen, ungeprüft: https://www.quicknode.com/builders-guide/tools/laevitas-by-laevitas, https://nexusfi.com/d/data-providers/laevitas/). Amberdata: Startup, On-Demand und Enterprise, Preise überwiegend auf Anfrage (ungeprüft).
- **Aufwand:** mittel.
- **Recht/Risiko:** Enterprise-Lizenzen mit Weitergabeverbot; Charts nicht öffentlich spiegeln.
- **Lohnt sich, wenn …** die Deribit-Optionsagenten nachweislich an fehlenden Vol-Kennzahlen scheitern und die Eigenberechnung aus Deribit-Rohdaten zu aufwendig wird.

### ORATS
- **Link:** https://orats.com/ai-agents · Doku: https://orats.com/docs
- **Nutzen:** Kennzahlen für US-Optionen: IV-Rang, Skew, Earnings-Moves, Greeks, historische EOD-Daten seit 2007. Wirbt ausdrücklich mit Nutzung durch KI-Agenten.
- **Potenzial: 3/5.** Der verzögerte Tarif passt gut zu Papierhandel und Cron-Takt. IV-Daten können Aktien- und ETF-Agenten helfen (z. B. Erwartung von Earnings-Bewegungen).
- **Verletzt:** kostenpflichtig, Konto, Lizenz (Individual).
- **Kosten (offiziell 2026):** Delayed 99 $ (20.000 Requests/Monat, ca. 15 Min. Verzug); Live 199 $ (100.000 Requests); Live Intraday 399 $ (1 Mio. Requests). Institutionelle Preise separat.
- **Aufwand:** gering bis mittel.
- **Recht/Risiko:** Individual-Lizenz, keine öffentliche Anzeige der Rohdaten.
- **Lohnt sich, wenn …** die Arena US-Optionen handeln soll oder Aktien-Agenten IV und Earnings-Erwartung als Feature bekommen.

### Quiver Quantitative
- **Link:** https://api.quiverquant.com/pricing/
- **Nutzen:** Kongress-Trades, Lobbying, Regierungsaufträge, Insider, WallStreetBets-Erwähnungen. Ein MCP-Server ist enthalten, also direkt für Claude-Agenten nutzbar.
- **Potenzial: 3/5.** Passt gut zum „KI-Agent mit Story-Daten“-Ansatz. Der MCP-Zugang spart Integrationsaufwand. Kongressdaten haben allerdings 30–45 Tage Meldeverzug, und rohe Offenlegungen gibt es auch kostenlos.
- **Verletzt:** kostenpflichtig, Konto, Lizenz (nicht kommerziell).
- **Kosten (offiziell, 2026):** Hobbyist 300 $/Jahr (ca. 25 $/Monat) bzw. 360 $ bei monatlicher Zahlung; Trader 750 $/Jahr bzw. 900 $. Kommerziell nur auf Anfrage.
- **Aufwand:** gering (Python-Paket `quiverquant`, MCP).
- **Recht/Risiko:** Nur nicht kommerziell. Ob eine öffentliche Hobbyseite mit abgeleiteten Trades erlaubt ist, steht in den AGB (ungeprüft).
- **Lohnt sich, wenn …** ein „Politiker-Trades/Lobbying“-Agent in der Arena gegen die anderen antreten soll und die kostenlosen Rohquellen zu aufwendig zu parsen sind.

### Benzinga Pro
- **Link:** https://www.benzinga.com/pro/pricing/
- **Nutzen:** Schnelle US-Aktien-News, Squawk, Kalender. Für Agenten interessanter: der Benzinga-Datensatz per API über Massive (99 $/Monat).
- **Potenzial: 3/5 (über das Massive-Add-on) bzw. 1/5 (Pro-Terminal).** Das Terminal bringt Agenten nichts. Ein News-Feed per API mit Ticker-Tags dagegen schon, auch mit Verzögerung.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten (offiziell 2026):** Basic 37 $ (jährlich 30,58 $), Streamlined 147 $, Essential 197 $ (jährlich 1.997 $). Benzinga-Datensatz bei Massive 99 $/Monat.
- **Aufwand:** gering (über die Massive-API).
- **Recht/Risiko:** News-Texte sind urheberrechtlich geschützt. Nicht auf der öffentlichen Seite wiedergeben, nur die eigene Entscheidung der Agenten.
- **Lohnt sich, wenn …** Agenten nachweislich an fehlendem, ticker-genauem News-Kontext scheitern.

### Koyfin
- **Link:** https://www.koyfin.com/pricing/
- **Nutzen:** Günstige „Bloomberg-Light“-Oberfläche mit Charts, Screenern, Schätzungen, Transkripten und ETF-Holdings. Gut für menschliche Recherche zu Aktien und ETFs.
- **Potenzial: 2/5.** Es gibt kein öffentliches Daten-API für Agenten. Der Nutzen beschränkt sich auf manuelle Recherche, etwa um Ideen der Agenten gegenzuprüfen.
- **Verletzt:** kostenpflichtig, Konto.
- **Kosten:** Free; Plus 39 $; Premium 79 $; Advisor Core 209 $; Advisor Pro 299 $ (offizielle Seite, 2026: https://www.koyfin.com/pricing/plans-comparison/).
- **Aufwand:** gering (nur Browser).
- **Recht/Risiko:** Die Inhalte gelten für den persönlichen Gebrauch. Screenshots oder Daten auf der öffentlichen Seite wären problematisch.
- **Lohnt sich, wenn …** du selbst regelmäßig Aktien- und ETF-Thesen der Agenten manuell prüfen willst.

### Finnhub (Premium)
- **Link:** https://finnhub.io/pricing · https://finnhub.io/pricing-stock-api-market-data
- **Nutzen:** Kurse, Fundamentaldaten, Alternativdaten (Sentiment, Insider, Lobbying, Kongress), News.
- **Potenzial: 2/5.** Das Free-Tier deckt bereits viel ab. Premium wird schnell teuer, und die Pakete sind nach Datenart gesplittet.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten (offiziell, Snippet 2026):** Market Data Basic 49,99 $, Standard 129,99 $, Professional 199,99 $; All-In-One 3.500 $/Monat.
- **Aufwand:** gering.
- **Recht/Risiko:** Für die Anzeige sind wahrscheinlich kommerzielle Bedingungen nötig (ungeprüft).
- **Lohnt sich, wenn …** ein bestimmter Premium-Endpunkt (z. B. Alternativdaten) in Tests klar Mehrwert bringt. Ansonsten das Free-Tier ausreizen.

### Intrinio
- **Link:** https://intrinio.com/pricing · https://account.intrinio.com/pricing/individual
- **Nutzen:** Echtzeitkurse für Aktien und Optionen (EquitiesEdge, OptionsEdge) ohne Börsen-Papierkram.
- **Potenzial: 2/5.** Relativ teuer für einen Privatnutzer. Echtzeit bringt unter GitHub Actions wenig.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten (offiziell 2026):** Individual-Plan 150 $/Monat mit Testphase.
- **Aufwand:** mittel.
- **Recht/Risiko:** Der Individual-Plan sagt ausdrücklich **„No redistribution or display“** und gilt für 1 Platz. Eine öffentliche Seite ist damit unvereinbar.
- **Lohnt sich, wenn …** nie im aktuellen Aufbau.

### Databento
- **Link:** https://databento.com/pricing · Lizenzgebühren: https://databento.com/docs/portal/live-data
- **Nutzen:** Börsennahe Tick- und Orderbuchdaten (CME, US-Aktien, Optionen), nutzungsbasiert bzw. als Abo.
- **Potenzial: 2/5.** Technisch top, aber das Projekt handelt keine Futures, und Tick-Daten sind überdimensioniert. Interessant höchstens für gelegentliche historische Backtests (nutzungsbasiert, Startguthaben, ungeprüft).
- **Verletzt:** kostenpflichtig, Konto, Lizenz (Börsenlizenzen, Personal vs. Commercial).
- **Kosten (offiziell 2026):** Standard 199 $/Monat; der CME-Standard-Plan kostete früher 179 $ (https://databento.com/blog/updates-to-subscription-pricing). ICE-Daten zusätzlich ca. 740–795 $ pro Standort.
- **Aufwand:** mittel bis hoch (große Datenmengen).
- **Recht/Risiko:** Börsendaten mit „Personal“-Lizenz dürfen nicht öffentlich angezeigt werden.
- **Lohnt sich, wenn …** die Arena Futures oder Mikrostruktur-Strategien bekommt und auf einem eigenen Server läuft.

### Glassnode (Advanced / Professional)
- **Link:** https://studio.glassnode.com/pricing
- **Nutzen:** On-Chain-Kennzahlen für BTC und ETH (MVRV, SOPR, Exchange-Flows, Holder-Kohorten).
- **Potenzial: 2/5.** On-Chain-Daten wirken eher über Wochen und Monate. Advanced enthält kein richtiges API, und Professional ist teuer.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten (offiziell, abgerufen 30.10.2026):** Advanced 49 $/Monat bei jährlicher Zahlung, kein API (nur „API Light“: 14 Tage Historie, Tagesauflösung). Professional ab 584 $/Monat bei jährlicher Zahlung, API als kostenpflichtiges Add-on. Alle Preise zzgl. MwSt.
- **Aufwand:** gering bis mittel.
- **Recht/Risiko:** Glassnode-Charts und -Daten dürfen nicht ohne Lizenz öffentlich weiterverbreitet werden (ungeprüft, AGB prüfen).
- **Lohnt sich, wenn …** ein Krypto-Agent mit langem Zeithorizont (Wochen) eingeführt wird.

### CryptoQuant
- **Link:** https://cryptoquant.com/pricing
- **Nutzen:** On-Chain-Daten und Börsenflüsse, Miner-Daten, Funding. Etwas günstiger als Glassnode.
- **Potenzial: 2/5.** Ähnlicher Fall wie Glassnode. Der Professional-Plan mit Minutenauflösung ist bezahlbar.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten:** Advanced ca. 39 $ (jährlich 29 $), Professional ca. 109 $ (jährlich 99 $), Premium ca. 799 $ (Drittquellen Okt. 2026, ungeprüft: https://cryptobriefing.com/cryptoquant-api-upgrade-rate-limits/, https://costbench.com/software/onchain-analytics/cryptoquant/).
- **Aufwand:** gering.
- **Recht/Risiko:** wie Glassnode.
- **Lohnt sich, wenn …** Börsenzuflüsse (Exchange-Inflows) als Signal getestet werden sollen.

### Nansen
- **Link:** https://academy.nansen.ai/articles/1287744-plans-and-pricing · https://docs.nansen.ai/getting-started/credits
- **Nutzen:** Gelabelte Wallets („Smart Money“), Token-Flows, DEX-Aktivität. Ein API mit Backtesting-Daten gibt es.
- **Potenzial: 2/5.** Stark für Altcoins und DeFi. Die Arena handelt aber eher die großen Werte (Spot/Perps).
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten (offizielle Doku 2026):** Pro 49 $ (jährlich) bzw. 69 $ (monatlich), API inklusive. Zusätzliche API-Credits kosten 10 $ pro 1.000. Wie viele Start-Credits enthalten sind, ist unklar: 1.000 oder 2.000 (ungeprüft).
- **Aufwand:** mittel (Kosten pro Credit planen).
- **Recht/Risiko:** Labels und Daten sind proprietär, keine Weitergabe.
- **Lohnt sich, wenn …** ein Altcoin- bzw. Memecoin-Agent dazukommt.

### Arkham Intelligence
- **Link:** https://intel.arkm.com/docs · x402: https://arkm.com/llms/guides/x402-pay-per-request-for-agents.md
- **Nutzen:** Entitäts-Labels (Fonds, Börsen, Regierungen), Wallet-Tracking, Warnungen. Interessant: Zahlung pro Abfrage via x402 in USDC, ohne Konto.
- **Potenzial: 2/5.** Mit x402 gibt es einen agentenfreundlichen Bezahlweg. Der Nutzen für Spot und Perps bleibt aber indirekt.
- **Verletzt:** kostenpflichtig (bzw. Wallet mit USDC), API nur auf Antrag.
- **Kosten:** API-Zugang auf Antrag, Preise nicht öffentlich. Drittquellen nennen 199 $/Monat, ab 900 $/Monat oder 0,20 $ pro Credit via x402 (alles ungeprüft: https://apis.io/plans/arkham/arkham-plans/).
- **Aufwand:** mittel (Antrag; bei x402 eine Krypto-Wallet im CI, was ein Sicherheitsrisiko ist).
- **Recht/Risiko:** Ein Wallet-Key in einem öffentlichen Repo bzw. CI ist riskant. Labels sind proprietär.
- **Lohnt sich, wenn …** ein Agent gezielt auf große Wallet-Bewegungen (z. B. ETF- oder Regierungs-Wallets) reagieren soll.

### Dune (Plus)
- **Link:** https://dune.com/pricing · Credits: https://docs.dune.com/learning/how-tos/pricing-faqs
- **Nutzen:** SQL auf dekodierten Blockchain-Daten, eigene Abfragen per API. Es gibt auch Polymarket-Tabellen auf Polygon (ungeprüft).
- **Potenzial: 2/5.** Das Free-Tier inklusive API reicht für wenige geplante Abfragen. Plus lohnt sich nur bei viel Volumen.
- **Verletzt:** kostenpflichtig (Plus), Konto.
- **Kosten:** Plus ca. 399 $/Monat (auch 349 $ genannt), ca. 25.000 Credits; Overage ca. 0,014 $ pro Credit (Drittquellen 2026, ungeprüft: https://comparedge.com/tools/dune-analytics/pricing).
- **Aufwand:** mittel (SQL-Abfragen pflegen).
- **Recht/Risiko:** Ergebnisse öffentlicher Dune-Abfragen sind meist öffentlich. Bei privaten Abfragen und Exporten die AGB beachten.
- **Lohnt sich, wenn …** On-Chain-Abfragen (z. B. Polymarket-Flows) im Free-Tier an die Credit-Grenze stoßen.

### Unusual Whales
- **Link:** https://unusualwhales.com/pricing?product=api
- **Nutzen:** US-Optionsfluss, Dark Pool, Kongress- und Insider-Trades, 13F. Es gibt ein API (REST, Websocket, Kafka).
- **Potenzial: 2/5.** Optionsfluss als Signal für Aktien und ETFs ist umstritten. Kongress-Trades gibt es auch aus kostenlosen Quellen, mit Verzug.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten:** Endkunden-Abo ca. 48–50 $/Monat (Drittquellen, ungeprüft). API-Preise nicht öffentlich gefunden; die Preise wurden am 28.05.2025 erhöht (https://unusualwhales.substack.com/p/unusual-whales-api-prices-increasing). Kostenloser Account mit verzögerten Daten (Flow 2 Handelstage später).
- **Aufwand:** gering bis mittel.
- **Recht/Risiko:** Daten nicht öffentlich anzeigen. Business-Nutzung läuft über einen eigenen Enterprise-Tarif.
- **Lohnt sich, wenn …** ein „Smart-Money-Flow“-Agent für US-Aktien getestet werden soll.

### Stimmungs- und News-Analytics: RavenPack / Bigdata.com
- **Link:** https://bigdata.com/pricing
- **Nutzen:** Strukturierte News-Ereignisse und Sentiment. Bigdata.com ist RavenPacks Plattform für Suche und Retrieval, gedacht für LLM-Agenten.
- **Potenzial: 2/5.** Die nutzungsbasierte Abrechnung mit kostenloser Testphase macht es erstmals für Einzelne erreichbar. Die Kosten lassen sich aber schwer planen.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten:** tokenbasiert, ohne Sitzplätze, mit Option auf eine Flatrate pro Content-Set; konkrete Beträge nicht öffentlich gefunden (ungeprüft). Testphase ohne Kreditkarte.
- **Aufwand:** mittel.
- **Recht/Risiko:** News-Inhalte sind urheberrechtlich geschützt. Keine Zitate oder Volltexte auf der öffentlichen Seite.
- **Lohnt sich, wenn …** die Agenten News-Retrieval mit Quellenangaben brauchen und kostenlose RSS-Feeds nicht reichen.

### Santiment
- **Link:** https://app.santiment.net/pricing · https://academy.santiment.net/products-and-plans/sanapi-plans
- **Nutzen:** Krypto-Social-Volume und -Sentiment, On-Chain- und Entwickleraktivität. Per GraphQL-API.
- **Potenzial: 2/5.** Social-Sentiment-Spitzen als Kontra-Indikator sind für Krypto-Agenten interessant. Das Free-Tier hat aber Verzögerungen und Lücken.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten:** Sanbase Pro ca. 49 $, Max ca. 249 $ (Drittquellen 2026, ungeprüft). SanAPI Pro mit 5.000 Calls/Monat, Max mit 80.000 Calls/Monat (offizielle Academy, Preis dort nicht genannt). Im Juni 2026 umfangreiche Planänderungen (ungeprüft).
- **Aufwand:** gering bis mittel.
- **Recht/Risiko:** Keine Weitergabe der Metriken.
- **Lohnt sich, wenn …** ein Krypto-Sentiment-Agent im Free-Tier vielversprechend aussieht.

### LunarCrush
- **Link:** https://lunarcrush.com/support/how-much-does-lunarcrush-cost
- **Nutzen:** Social-Metriken für Krypto und Aktien (Galaxy Score, Social Dominance). API, MCP und CLI vorhanden.
- **Potenzial: 2/5.** Ein MCP-Server ist praktisch für Claude, aber die Preise sind deutlich gestiegen.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten (offiziell 2026):** Discover kostenlos; Individual 90 $; Builder 300 $ (alle API-Endpunkte); Scale 900 $; Enterprise auf Anfrage. Ältere Angaben (24 $ bzw. 240 $) sind veraltet.
- **Aufwand:** gering.
- **Recht/Risiko:** Keine Weitergabe.
- **Lohnt sich, wenn …** Social-Signale als eigener Agent getestet werden sollen und Santiment nicht reicht.

### PolymarketAnalytics
- **Link:** https://polymarketanalytics.com
- **Nutzen:** Dashboards für Polymarket-Trader und -Wallets, Ranglisten, Portfolio-Tracking.
- **Potenzial: 2/5.** Praktisch, um „smarte“ Wallets zu finden. Die Rohdaten (Polymarket Data-API, On-Chain) sind aber ohnehin kostenlos.
- **Verletzt:** kostenpflichtig (Premium), Konto.
- **Kosten:** Free; Premium ca. 20 $/Monat (eine Drittquelle, ungeprüft: https://www.bonus.com/prediction-markets/tools/polymarket-analytics/).
- **Aufwand:** gering (Weboberfläche). Ein offizielles API wurde nicht gefunden (ungeprüft).
- **Recht/Risiko:** gering, solange nur manuell genutzt.
- **Lohnt sich, wenn …** ein Copy-Trading-Agent für Wallets auf Polymarket gebaut werden soll und die eigene Auswertung zu aufwendig ist.

### Oddpool
- **Link:** https://www.oddpool.com/pricing
- **Nutzen:** Normalisierte Daten über Kalshi und Polymarket hinweg: Suche, Arbitrage- und Spread-API, Whale-Tracking, Websockets, Historie.
- **Potenzial: 2/5.** Venue-übergreifende Arbitrage und Spreads passen genau zur Arena. **Neue Abos werden laut offizieller Seite derzeit aber nicht angenommen**; nur der kostenlose Account bleibt. Laut Berichten ist Oddpool zu Kalshi gewechselt bzw. wurde übernommen (https://dealroom.co/news/151169-kalshi-acquires-data-startup-oddpool-months-after-its-3m-seed/, ungeprüft).
- **Verletzt:** kostenpflichtig, Konto.
- **Kosten (offiziell, abgerufen 30.10.2026):** Free 0 $ (1 Request/s, 1.000 Calls/Monat, Historien-API); Pro 30 $ (1 Mio. Calls, Whale-API); Premium 100 $ (5 Mio. Calls, Arbitrage- und Spread-API); Enterprise auf Anfrage. Für neue Kunden geschlossen.
- **Aufwand:** gering.
- **Recht/Risiko:** Die AGB zur Weitergabe sind nicht auf der Preisseite genannt (ungeprüft).
- **Lohnt sich, wenn …** Oddpool wieder Abos verkauft (oder Kalshi es als offizielles Produkt anbietet) und die Arena Arbitrage zwischen Kalshi und Polymarket handeln will. Bis dahin das kostenlose Tier testen.

---

**Kurzfazit:** Für das Projekt realistisch interessant sind vor allem **CoinGlass Hobbyist (29 $)** für Perps, **Quiver Hobbyist (ca. 25 $)** wegen MCP und Kongressdaten, **ORATS Delayed (99 $)** für IV-Features, **Laevitas Premium (50 $, ungeprüft)** für Deribit-Optionen sowie **Massive/Tiingo/EODHD/FMP (20–30 $)** als stabilere Kursquellen. Bei allen gilt: Die Lizenz erlaubt in der Regel **keine öffentliche Anzeige von Rohdaten**, und das ist bei öffentlichem Repo, öffentlicher Seite und öffentlichen Actions-Logs der eigentliche Knackpunkt.

### Bloomberg Terminal / LSEG Workspace (ehem. Refinitiv Eikon)
- **Link:** https://www.bloomberg.com/professional/ · https://www.lseg.com/en/data-analytics/products/workspace
- **Nutzen fürs Projekt:** Der Goldstandard: Kurse, News, Fundamentaldaten und Alternativdaten (z. B. Second Measure über ALTD) an einem Ort. Für das Projekt nur als Referenz dafür, was „Profi-Daten“ sind.
- **Potenzial: 1/5.** Der Preis steht in keinem Verhältnis zu einem Hobbyprojekt. Außerdem gibt es kein freies API für Automatisierung in der Cloud: Die Terminal-API ist an die lokale Installation gebunden.
- **Verletzt:** kostenpflichtig, Vertrag/Konto, Lizenz (Einzelplatz, keine Weitergabe), andere Infrastruktur (Desktop-Terminal).
- **Kosten:** Bloomberg ca. 31.980 $/Jahr pro Platz, 2-Jahres-Vertrag (Drittquelle 2026, ungeprüft). LSEG Workspace ca. 12.000–24.000 $/Jahr, kein Listenpreis (Drittquellen 2026, ungeprüft). Quellen: https://eulerpool.com/blog/bloomberg-terminal-cost · https://multiples.vc/compare/pricing
- **Aufwand:** hoch (Vertrag, Desktop, keine Cloud-Automatisierung).
- **Recht/Risiko:** Die Lizenz verbietet die Weitergabe an Dritte strikt. Eine öffentliche Anzeige ist ausgeschlossen.
- **Lohnt sich, wenn …** nie für dieses Projekt. Allenfalls über einen Zugang an Uni oder Arbeitsplatz, um einzelne Hypothesen manuell zu prüfen.

### Kaiko
- **Link:** https://www.kaiko.com/contact
- **Nutzen:** Institutionelle Krypto-Marktdaten (Tick, Orderbuch, Referenzpreise, Derivate).
- **Potenzial: 1/5.** Nur Preise auf Anfrage, ausgerichtet auf Institutionen. Die kostenlosen Börsen-APIs (Binance, Deribit usw.) liefern für Papierhandel fast dasselbe.
- **Verletzt:** kostenpflichtig, Vertrag, Lizenz.
- **Kosten:** kein öffentlicher Preis, nur Angebot (https://datarade.ai/data-providers/kaiko-data). Unbestätigte Meldung: Kaiko soll Amberdata übernommen haben (https://solanacompass.com/projects/amberdata, ungeprüft).
- **Aufwand:** hoch (Sales-Prozess).
- **Recht/Risiko:** Lizenz mit Weitergabeverbot.
- **Lohnt sich, wenn …** nie für ein Hobbyprojekt.

### Token Terminal
- **Link:** https://tokenterminal.com/pricing
- **Nutzen:** „Fundamentaldaten“ für Krypto-Protokolle (Umsatz, Gebühren, aktive Nutzer).
- **Potenzial: 1/5.** Teuer, und die Daten bewegen sich langsam. Das kostenlose DefiLlama deckt viel davon ab.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten:** Pro ca. 350 $ pro Nutzer und Monat (Drittquellen, ungeprüft). API (250.000 Requests/Tag) nur auf Anfrage (offizielle Seite).
- **Aufwand:** mittel.
- **Recht/Risiko:** Lizenz mit Weitergabeverbot.
- **Lohnt sich, wenn …** kaum. DefiLlama ist kostenlos.

### Cheddar Flow / Tradytics
- **Link:** https://www.cheddarflow.com · https://tradytics.com
- **Nutzen:** Dashboards für Optionsfluss und KI-Signale.
- **Potenzial: 1/5.** In erster Linie Web- und Discord-Oberflächen, kein offenes Daten-API für Agenten (ungeprüft).
- **Verletzt:** kostenpflichtig, Konto.
- **Kosten:** Cheddar Flow Standard ca. 85 $ (https://www.luxalgo.com/blog/cheddarflow-order-flow-tool-review/, ungeprüft). Tradytics ca. 50–69 $, höhere Stufen 119 und 199 $ (https://www.softwaresuggest.com/tradytics/pricing, ungeprüft).
- **Aufwand:** nicht automatisierbar (Scraping verstößt wahrscheinlich gegen die AGB).
- **Recht/Risiko:** Scraping und Weitergabe sind nicht erlaubt.
- **Lohnt sich, wenn …** nie für die Arena.

### Cboe DataShop
- **Link:** https://datashop.cboe.com
- **Nutzen:** Offizielle historische Optionsdaten (Open-Close, Intraday-Snapshots, Tiefe).
- **Potenzial: 1/5.** Preise auf institutionellem Niveau.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten:** laut SEC-Gebührenordnungen z. B. C2 Ten-Minute Intraday 1.000 $/Monat, One-Minute 5.000 $/Monat (2026). Historische Tiefendaten 1.500 $ pro Datenmonat (2025). Quellen: https://www.sec.gov/files/rules/sro/c2/2026/34-106149-ex5.pdf, https://www.sec.gov/files/rules/sro/c2/2026/34-105559-ex5.pdf (Zuordnung der einzelnen Werte ungeprüft).
- **Aufwand:** hoch.
- **Recht/Risiko:** Börsenlizenz, Weitergabe verboten.
- **Lohnt sich, wenn …** nie für ein Hobbyprojekt.

### Satellitenbilder (Planet, Privateer/Orbital Insight, SpaceKnow)
- **Link:** https://www.planet.com/pricing · https://www.privateer.com/blog/reuters-exclusive-privateer-buys-orbital-insight
- **Nutzen:** Parkplatzbelegung, Öltanks, Industrieaktivität als Frühindikatoren.
- **Potenzial: 1/5.** Preise und Verarbeitung (Computer Vision) liegen klar auf Hedgefonds-Niveau. Für einen Privatanleger ist das Signal-Rausch-Verhältnis schlecht.
- **Verletzt:** kostenpflichtig, Vertrag, Lizenz, andere Infrastruktur (Bildverarbeitung).
- **Kosten:** Planet nur auf Anfrage. Zugang über Sentinel Hub, Basic laut Forum ca. 30 €/Monat (ungeprüft: https://forum.sentinel-hub.com/t/about-planet-monitoring-and-processing-plans/8982). Orbital Insight wurde im Mai 2024 von Privateer übernommen (Preis unbekannt). Für SpaceKnow keine Preise gefunden. Kostenlos verfügbar: Sentinel-2 (10 m Auflösung).
- **Aufwand:** sehr hoch.
- **Recht/Risiko:** Bildlizenzen beschränken die Weitergabe.
- **Lohnt sich, wenn …** nie im Rahmen der Arena.

### Kreditkarten-/Transaktionsdaten (Bloomberg Second Measure, Consumer Edge, YipitData)
- **Link:** https://secondmeasure.com · https://www.consumer-edge.com · https://www.yipitdata.com
- **Nutzen:** Umsatzschätzungen von Unternehmen vor den Quartalszahlen.
- **Potenzial: 1/5.** Nur für Enterprise-Kunden, Preise auf Anfrage. Second Measure gibt es nur über Bloomberg Data License oder das Terminal (ALTD, 7 Tage Verzug). Einzige bezahlbare Annäherung: Massive „European Consumer Spending by Merchant“ für 99 $/Monat (Individual, 30 Tage Embargo; https://massive.com/pricing).
- **Verletzt:** kostenpflichtig, Vertrag, Lizenz.
- **Kosten:** nicht öffentlich (https://datarade.ai/data-providers/second-measure/profile).
- **Aufwand:** hoch.
- **Recht/Risiko:** strenge Lizenzen, Weitergabe verboten.
- **Lohnt sich, wenn …** nie. Allenfalls das Massive-Add-on zum Experimentieren.

### Geodaten/Fußverkehr (Placer.ai, SafeGraph/Advan)
- **Link:** https://www.placer.ai · https://advanresearch.com
- **Nutzen:** Besucherzahlen in Filialen als Umsatz-Frühindikator für Einzelhandelsaktien. Advan hat 2022 das Patterns-Geschäft von SafeGraph übernommen (https://advanresearch.com/insights/advan-acquires-safegraphs-patterns-business-expanding-leadership-in-location-intelligence-and-foot-traffic-analytics).
- **Potenzial: 1/5.** Nur Enterprise, Preise auf Anfrage.
- **Verletzt:** kostenpflichtig, Vertrag, Lizenz.
- **Kosten:** nicht öffentlich (https://www.growthfactor.ai/resources/blog/placer-ai-pricing). Placer.ai hat einen kostenlosen Zugang mit eingeschränkten Inhalten (ungeprüft).
- **Aufwand:** hoch.
- **Recht/Risiko:** Lizenz mit Weitergabeverbot; Bewegungsdaten sind datenschutzrechtlich heikel (DSGVO).
- **Lohnt sich, wenn …** nie.

### Jobdaten (Thinknum, LinkUp, Revelio Labs)
- **Link:** https://www.thinknum.com · https://www.linkup.com · https://www.reveliolabs.com
- **Nutzen:** Stellenanzeigen und Personalbewegungen als Wachstumsindikatoren.
- **Potenzial: 1/5.** Enterprise-Preise; das Signal wirkt nur langsam (über Quartale).
- **Verletzt:** kostenpflichtig, Vertrag, Lizenz.
- **Kosten:** Thinknum laut Capterra ab 16.800 $/Jahr (ungeprüft: https://www.capterra.com/p/204405/Thinknum/). Revelio ohne öffentliche Preise, akademischer Zugang über WRDS. Für LinkUp nichts gefunden.
- **Aufwand:** hoch.
- **Recht/Risiko:** Lizenz mit Weitergabeverbot.
- **Lohnt sich, wenn …** nie.

### Alexandria Technology
- **Link:** https://www.alexandriatechnology.com
- **Nutzen:** KI-gestütztes News-Sentiment (Dow Jones und andere) für Institutionen.
- **Potenzial: 1/5.** Keine öffentlichen Preise gefunden; ausgerichtet auf Institutionen (ungeprüft).
- **Verletzt:** kostenpflichtig, Vertrag, Lizenz.
- **Kosten:** unbekannt, nichts gefunden (ungeprüft).
- **Aufwand:** hoch.
- **Recht/Risiko:** Lizenz mit Weitergabeverbot.
- **Lohnt sich, wenn …** nie. Ein LLM kann Sentiment selbst aus Schlagzeilen ableiten.

### StockTwits API
- **Link:** https://api.stocktwits.com/developers
- **Nutzen:** Kleinanleger-Stimmung pro Ticker.
- **Potenzial: 1/5.** Das offizielle API ist eingeschränkt, teils mit Freigabepflicht. Enterprise-Daten gibt es nur nach individueller Verhandlung (ungeprüft). Scraper von Drittanbietern verstoßen wahrscheinlich gegen die AGB.
- **Verletzt:** Konto/Freigabe, ggf. kostenpflichtig, Lizenz.
- **Kosten:** keine offiziellen Preise gefunden. Drittanbieter-Wrapper ab 30 $ (https://parse.bot/marketplace/f2e46dc1-171b-470d-9a07-9cfb5a0879bb/stocktwits-com-api, inoffiziell).
- **Aufwand:** mittel.
- **Recht/Risiko:** Scraping bzw. inoffizielle Wrapper sind ein AGB-Risiko.
- **Lohnt sich, wenn …** StockTwits wieder einen offenen, bezahlbaren Entwicklerzugang anbietet.

### The TIE
- **Link:** https://www.thetie.io
- **Nutzen:** Institutionelles Krypto-Sentiment, News und Terminal.
- **Potenzial: 1/5.** Sales-geführte Pakete, keine verlässlichen öffentlichen Preise.
- **Verletzt:** kostenpflichtig, Vertrag, Lizenz.
- **Kosten:** nicht öffentlich gefunden (https://www.rfp.wiki/crypto/digital-assets-nfts/crypto-data-analytics-market-risk/the-tie/coinmarketcap, geringe Zuverlässigkeit).
- **Aufwand:** hoch.
- **Recht/Risiko:** Lizenz mit Weitergabeverbot.
- **Lohnt sich, wenn …** nie.

### Newsquawk
- **Link:** https://newsquawk.com/pricing
- **Nutzen:** Audio-Squawk und Schlagzeilen zu Makro, FX und Aktien in Echtzeit.
- **Potenzial: 1/5.** Auf Echtzeit-Audio für menschliche Trader ausgelegt. Unter GitHub Actions ohne Wert; das API wird separat lizenziert.
- **Verletzt:** kostenpflichtig, Konto, Lizenz.
- **Kosten (offiziell 2026):** Basic 199 $ (1 Kanal), Pro 399 $ (6 Kanäle und Equities Suite), jeweils zzgl. MwSt. Testphase 29,99 $. API und Firmenlizenzen auf Anfrage.
- **Aufwand:** hoch (für Automatisierung).
- **Recht/Risiko:** Keine Weitergabe.
- **Lohnt sich, wenn …** nie im aktuellen Aufbau.

### Dow Jones Newswires
- **Link:** https://developer.dowjones.com
- **Nutzen:** Die Mutter der Finanz-Newsfeeds mit sehr niedriger Latenz.
- **Potenzial: 1/5.** Institutionelle Preise; die Latenz ist unter Cron nutzlos.
- **Verletzt:** kostenpflichtig, Vertrag, Lizenz.
- **Kosten:** über den Reseller QuoteMedia 110 $ pro Nutzer und Monat (für Profi-Nutzer, ungeprüft: https://api.quotemedia.com/supplement/docs/fees/pro/premium-news-services.php). API direkt nur auf Anfrage.
- **Aufwand:** hoch.
- **Recht/Risiko:** strenge Lizenz, keine Wiedergabe.
- **Lohnt sich, wenn …** nie.

### Tree of Alpha / Tree News
- **Link:** https://news.treeofalpha.com (ungeprüft)
- **Nutzen:** Krypto-Schlagzeilen mit sehr niedriger Latenz (Börsen-Listings, Tweets) per Websocket, beliebt bei Krypto-Daytradern.
- **Potenzial: 1/5.** Der ganze Wert liegt in Millisekunden, und die gibt es unter GitHub Actions nicht.
- **Verletzt:** kostenpflichtig, Konto, andere Infrastruktur (dauerhaft laufender Websocket-Client).
- **Kosten:** SPROUT ca. 500 $/Monat, SAPLING ca. 2.500 $/Monat (inoffizielle Spiegelseite, ungeprüft: https://web-5gv.pages.dev/resources/tree-of-alpha). Ein TREE-Token zum Bezahlen von Abos existiert (https://tokeninsight.com/en/coins/tree-capital/overview).
- **Aufwand:** hoch (Dauerprozess auf einem VPS).
- **Recht/Risiko:** Keine Weitergabe.
- **Lohnt sich, wenn …** die Arena auf einen VPS mit Dauerprozessen umzieht und eine Strategie für News-Reaktionen auf Listings gebaut wird.

### Dome API
- **Link:** https://docs.domeapi.io
- **Nutzen:** War ein vereinheitlichtes API für Polymarket und Kalshi (Märkte, Orderbücher, Trades).
- **Potenzial: 0/5 (eingestellt).** Laut eigener Doku **von Polymarket übernommen; alle Dome-APIs end of life am 28.04.2026**. Verwiesen wird auf die offiziellen Polymarket-APIs.
- **Verletzt:** entfällt.
- **Kosten:** früher Starter 39 $ / Pro 129 $ / Orderbook 249 $ (ungeprüft, die Zuordnung zu Dome ist unklar: https://pm.wiki/pt/compare/dome-vs-probalytics).
- **Aufwand/Recht:** entfällt.
- **Lohnt sich, wenn …** nie, der Dienst ist eingestellt. Stattdessen die kostenlosen offiziellen APIs von Polymarket und Kalshi nutzen.

---

## Social-Daten hinter Logins

> Stand der Recherche: 30.10.2026. Diese Ideen sind **nur zum Kennen**, nicht zum Einbauen. Die Arena läuft weiter mit kostenlosen, öffentlichen Quellen (Reddit-RSS, GDELT, RSS). Die Rechtshinweise sind eine grobe Einordnung und **keine Rechtsberatung**. Angaben mit "(ungeprüft)" ließen sich nicht mit einer Primärquelle belegen. Preise stammen oft von Drittseiten; vor jeder Entscheidung auf der Herstellerseite nachsehen.
Potenzial-Skala (für einen Privatanleger mit Hobby-Projekt): 1 = kaum Nutzen, 5 = deutlicher, realistischer Mehrwert.

### X/Twitter API (offiziell, Pay-per-use)
- **Link:** https://docs.x.com/x-api/getting-started/pricing
- **Was es bringt:** Echtzeit-Posts von Krypto-, Politik- und Finanzkonten. Für Wettmärkte (Wahlen, Politik-Events) ist X oft die schnellste Quelle.
- **Potenzial: 3/5.** Das Signal ist schnell, aber stark verrauscht, und Lesezugriffe werden schnell teuer. Für ein paar gezielte Konten könnte es reichen.
- **Verletzte Bedingung:** Kostenpflichtig, Developer-Konto und Guthaben nötig.
- **Kosten (2026):** Seit 6.2.2026 ist Pay-per-use der Standard, ein Free-Tier gibt es nicht mehr. Ein gelesener Post kostet rund **0,005 $**, 100.000 Reads also ca. 500 $ pro Monat. Einen Post zu schreiben kostet seit April 2026 0,015 $, mit Link 0,20 $. Basic (200 $/Monat) wurde nach dem 1.6.2026 abgeschaltet, Pro (5.000 $/Monat) nach dem 1.9.2026. Übrig bleibt Enterprise mit Preis auf Anfrage. Pay-per-use ist bei 3 Mio. Post-Reads pro Monat gedeckelt. Neue Konten bekommen einmalig Startguthaben, laut Drittquelle bis 70 $, das nach 3 Monaten verfällt. Quellen: https://postproxy.dev/blog/x-api-pricing-2026/, https://opentweet.io/x-api-pricing, https://www.blotato.com/blog/twitter-api-pricing
- **Aufwand:** Mittel. Die API ist sauber, man braucht aber ein Budget-Limit und Secrets in GitHub Actions.
- **Rechtslage/Risiko:** Über die offizielle API gering. Laut Berichten untersagen die X-AGB das Crawlen und Scrapen ohne schriftliche Zustimmung. Sie enthalten eine Vertragsstrafe von **15.000 $ pro 1 Mio. Posts**, die jemand unter AGB-Bruch in 24 Stunden abruft. Datum und Fassung der Klausel weichen zwischen den Quellen ab (ungeprüft gegen den AGB-Originaltext). Ob die Klausel durchsetzbar ist, besonders unter EU-Recht zu missbräuchlichen Klauseln, ist offen. Quellen: https://conductatlas.com/platform/x/x-terms-of-service/liquidated-damages-for-bulk-post-access/, https://knightcolumbia.org/content/knight-institute-says-xs-new-terms-of-service-will-stifle-independent-research
- **Lohnt sich, wenn …** ein Agent nachweislich Edge aus wenigen (unter 50) beobachteten Konten zieht und das Budget unter etwa 20 $ pro Monat bleibt.

### Grok (xAI-API) als indirekter X-Zugang
- **Link:** https://docs.x.ai/ (Preisseite, ungeprüft direkt)
- **Was es bringt:** Das serverseitige Tool "X Search" durchsucht X und liefert eine Zusammenfassung mit Belegen. Man bekommt also keinen Rohdatenstrom, sondern ein Recherche-Ergebnis. Für LLM-Agenten passt das gut.
- **Potenzial: 3/5.** Bequem für die Frage "Was sagt X gerade zu Markt Y?". Nicht vollständig und nicht reproduzierbar.
- **Verletzte Bedingung:** Kostenpflichtig, xAI-Konto nötig.
- **Kosten (2026, Drittquellen):** Meist genannt werden **5 $ pro 1.000 X-Search-Aufrufe** plus Token-Kosten. Eine Quelle nennt 10 $ pro 1.000 Aufrufe (ungeprüft). Quelle: https://www.eesel.ai/en/blog/xai-pricing. Hinweis: Die X-API-Preisseite verweist inzwischen auf xAI-Gutschriften für API-Ausgaben.
- **Aufwand:** Gering.
- **Rechtslage/Risiko:** Gering. Es ist ein offizielles Produkt aus demselben Konzern, und Lizenzfragen trägt der Anbieter.
- **Lohnt sich, wenn …** ein Agent ein paar Mal pro Tag eine qualitative Stimmungsabfrage braucht, also bei unter 5 $ pro Monat.

### Truth Social
- **Link:** https://truthsocial.com (keine offizielle API-Doku gefunden)
- **Was es bringt:** Posts von Donald Trump bewegen Märkte, z. B. Zölle, Krypto, Polymarket-Politikmärkte.
- **Potenzial: 3/5.** Wenige Konten mit großer Marktwirkung. Einzelne prominente Konten sind laut Drittquellen seit August 2025 ohne Login sichtbar.
- **Verletzte Bedingung:** Es gibt keine offizielle API. Suche, Hashtags und die meisten Profile sind nur mit Login erreichbar. Technisch basiert die Plattform auf Mastodon. Die Truth-Social-AGB zum Scraping wurden nicht geprüft (ungeprüft). Quelle: https://apify.com/thirdwatch/truth-social-scraper
- **Kosten:** Drittanbieter-Scraper rechnen nach Nutzung ab (Preise ungeprüft).
- **Aufwand:** Mittel.
- **Rechtslage/Risiko:** Unklar. Bewusst nicht hinter dem Login automatisieren. Legal und kostenlos ist der Umweg über Nachrichten-RSS und GDELT, die solche Posts binnen Minuten aufgreifen.
- **Lohnt sich, wenn …** sich zeigt, dass die Minuten Vorsprung gegenüber der GDELT- oder RSS-Meldung wirklich Geld wert sind. Bei Papierhandel eher nicht.

### twitterapi.io und ähnliche Drittanbieter
- **Link:** https://twitterapi.io/blog/twitter-api-pricing
- **Was es bringt:** X-Daten deutlich billiger als über die offizielle API.
- **Potenzial: 2/5.** Billig, aber auf unsicherem Fundament.
- **Verletzte Bedingung:** Kostenpflichtig. Vor allem holt der Anbieter die Daten nach eigener Darstellung nicht über die offizielle Lizenz. Damit steht er im Konflikt mit dem Scraping-Verbot der X-AGB (ungeprüft, wie genau der Anbieter die Daten bezieht).
- **Kosten:** Laut Anbieter und Vergleichsseiten ca. **0,15 $ pro 1.000 Tweets**, ohne Monatsminimum. Das Startguthaben wird uneinheitlich mit 0,10 $ bis 1 $ angegeben (Stand 2025/26, Eigenangaben). Quelle: https://www.getxapi.com/blogs/cheapest-twitter-api-2026-8-providers-ranked-by-real-per-1000-tweet-cost
- **Aufwand:** Gering.
- **Rechtslage/Risiko:** Hoch bis unklar. Den AGB-Bruch begeht zunächst der Anbieter, als Kunde nutzt man aber wissentlich ein Produkt, das darauf beruht. Dazu kommt das Ausfallrisiko, falls X den Dienst sperrt oder verklagt. Für ein öffentliches Repo nicht empfehlenswert.
- **Lohnt sich, wenn …** praktisch nie für dieses Projekt. Allenfalls als Wissen, dass es den Graumarkt gibt.

### Telegram: Bot-API vs. MTProto-Client-API
- **Links:** https://core.telegram.org/api/terms, https://core.telegram.org/api/obtaining_api_id
- **Was es bringt:** Viele Krypto-Alpha-, Pump- und Signalkanäle laufen über Telegram. Als Frühindikator für Hypes könnte das helfen, ebenso als Warnsignal für Pump-and-Dump.
- **Potenzial: 2/5.** Die Kanäle sind voller Betrug und Pump-Gruppen, und der Signalwert für seriöse Strategien ist zweifelhaft.
- **Verletzte Bedingung:** Login und Konto nötig. Die **Bot-API** liest einen Kanal nur, wenn der Bot dort Mitglied ist, praktisch als Admin. Das setzt eine Einladung durch den Kanalbetreiber voraus, und ältere Nachrichten sind nicht abrufbar. Fremde Kanäle lesen geht nur über die **MTProto-Client-API** mit echtem Nutzerkonto und eigener api_id. Quelle: https://dev.to/starnikov/the-telegram-bot-api-cannot-read-a-channel-your-bot-is-not-in-4jme
- **Kosten:** Die API ist kostenlos (Stand 2026). Kosten entstehen nur durch eine Telefonnummer für das Konto.
- **Aufwand:** Mittel bis hoch. Session-Handling ist nötig, in GitHub Actions ein heikler Secret-Umgang.
- **Rechtslage/Risiko:** Mittel. Die API-AGB verlangen eine eigene api_id. Flooding, Spam und das Fälschen von Zählern führen zum dauerhaften Bann. Bei Verstößen gibt es eine 10-Tage-Frist, dann wird der API-Zugang beendet. Telegram verweist zusätzlich auf eine eigene Policy zu Content-Lizenzierung und KI-Scraping (Inhalt ungeprüft). Inoffizielle Clients werden laut Community stärker beobachtet. Inhalte aus Kanälen enthalten personenbezogene Daten, siehe DSGVO unten.
- **Lohnt sich, wenn …** man einen eigenen oder einen ausdrücklich kooperierenden Kanal auswerten will. Dann reicht die Bot-API.

### Reddit Data API (OAuth)
- **Links:** https://redditinc.com/policies/data-api-terms, https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki, https://www.reddit.com/r/redditdev/comments/1oug31u/introducing_the_responsible_builder_policy_new/
- **Was es bringt:** Mehr als die RSS-Feeds, die das Projekt schon nutzt: Kommentare, Scores, Suche, höheres Volumen.
- **Potenzial: 2/5.** RSS deckt den Kern bereits ab, der Zusatznutzen ist gering.
- **Verletzte Bedingung:** OAuth-Login nötig. Seit der **Responsible Builder Policy** (Ende 2025) braucht jeder neue OAuth-Token eine manuelle Freigabe per Ticket. Nutzer berichten von langen Wartezeiten und stillen Ablehnungen.
- **Kosten (2026):** Für freigegebene, **nicht-kommerzielle** Nutzung kostenlos, mit 100 Anfragen pro Minute pro Client-ID im 10-Minuten-Mittel. Kommerzielle Preise sind nicht öffentlich. Historisch wurden rund 12.000 $ pro 50 Mio. Anfragen genannt, also ca. 0,24 $ pro 1.000 (2023, The Verge). Die Data-API-Terms wurden zuletzt am 20.7.2026 geändert. Quelle: https://snitchfeed.com/blog/reddit-api-pricing
- **Aufwand:** Gering technisch, hoch bürokratisch.
- **Rechtslage/Risiko:** Gering bei Freigabe. Die Terms schränken ML-Training mit Reddit-Inhalten ein (genaue Klausel ungeprüft). Drittanbieter, die "ohne Reddit-Freigabe" Daten liefern, haben dasselbe Graumarkt-Problem wie twitterapi.io.
- **Lohnt sich, wenn …** RSS nachweislich zu wenig Kontext liefert, z. B. Kommentar-Stimmung zu einem Ticker, und die Freigabe als Hobby-Forschungsprojekt klappt.

### StockTwits
- **Link:** https://api.stocktwits.com/developers (Status ungeprüft), AGB: https://www.stocktwits.com/about/legal/terms
- **Was es bringt:** Ticker-bezogene Retail-Stimmung mit Bullish/Bearish-Labels, als Kontra-Indikator für Aktien und Krypto.
- **Potenzial: 2/5.** Ein Retail-Sentiment-Signal, dessen Edge in der Literatur umstritten ist (ungeprüft).
- **Verletzte Bedingung:** Der API-Zugang ist eingeschränkt oder nur nach Freigabe zu haben. Die AGB erlauben, Konten mit nicht autorisiertem automatisiertem Zugriff zu sperren. Die Daten werden kommerziell über Partner wie Alpaca vertrieben.
- **Kosten:** Keine offiziellen Preise gefunden (2026). Über Partner/Broker wie Alpaca ungeprüft.
- **Aufwand:** Mittel.
- **Rechtslage/Risiko:** Scraper ohne Key verstoßen gegen die AGB, daher tabu. Über den offiziellen Partnerzugang gering.
- **Lohnt sich, wenn …** die Arena auf Aktien-Retail-Sentiment setzt und ein Broker-Partnerzugang ohnehin besteht.

### Discord
- **Link:** https://support.discord.com/hc/articles/115002192352
- **Was es bringt:** Trading- und Krypto-Communitys, Alpha-Server.
- **Potenzial: 1/5.** Man kommt nur auf Server, auf die man eingeladen wird. Der Signalwert ist ähnlich zweifelhaft wie bei Telegram.
- **Verletzte Bedingung:** Ein Bot-Konto funktioniert nur auf Servern, deren Admin den Bot hinzufügt. **Self-Bots**, also automatisierte Nutzerkonten, verbietet Discord ausdrücklich ("violation of our API Terms of Use").
- **Kosten:** Kostenlos.
- **Aufwand:** Mittel.
- **Rechtslage/Risiko:** Mit offiziellem Bot auf einem eigenen oder einladenden Server gering. Ein Self-Bot bedeutet Kontosperre und ist tabu.
- **Lohnt sich, wenn …** Rouven selbst einen Server betreibt, etwa als Arena-Community, und dort Feedback auswerten will.

### DSGVO beim Speichern personenbezogener Posts im öffentlichen Repo
- **Links:** https://www.dr-datenschutz.de/social-media-darf-man-die-oeffentlich-zugaenglichen-daten-nutzen/, https://www.dr-datenschutz.de/webseiten-scraping-was-die-edsa-guidelines-fordern/
- **Worum es geht:** Auch öffentliche Posts sind personenbezogene Daten. Wer sie speichert, braucht eine Rechtsgrundlage, meist das berechtigte Interesse nach Art. 6 Abs. 1 lit. f DSGVO mit Abwägung. Entscheidend sind die vernünftigen Erwartungen der Betroffenen. Bei sensiblen Daten nach Art. 9 (politische Meinung!) wird es schwierig. Ein **öffentliches GitHub-Repo** ist eine Veröffentlichung, keine bloße Speicherung. Damit greifen Informationspflichten (Art. 14), Löschpflichten und Speicherbegrenzung.
- **Potenzial/Relevanz: 5/5 als Vorsicht.** Das betrifft schon die heutigen Reddit-RSS-Daten.
- **Kosten:** 0 €, wenn man es von Anfang an richtig macht.
- **Aufwand:** Gering. Nur aggregierte Werte committen (Scores, Zählungen, Themen), keine Nutzernamen und keine Volltexte. Rohdaten kurzlebig halten, z. B. nur im Actions-Lauf oder als Artefakt mit kurzer Aufbewahrung.
- **Rechtslage/Risiko:** Hobbyprojekte fallen nicht automatisch unter die Haushaltsausnahme, wenn die Ergebnisse öffentlich sind (Einordnung, ungeprüft für diesen konkreten Fall). Das EDSA-Papier zu Scraping wird von Drittquellen zitiert, das Original ist ungeprüft.
- **Lohnt sich, wenn …** immer. Das ist eine Leitplanke, keine Option.

---

## GPU-Training und eigene Modelle

### Outcome-basiertes RL für Prognosen (selbst trainieren)
- **Links:** https://arxiv.org/abs/2505.17989 (Lightning Rod, TMLR) · Foresight Learning / Future-as-Label https://arxiv.org/pdf/2601.06336
- **Was es bringt:** Ein LLM wird mit RL auf **echten Auflösungen** trainiert: Belohnung ist der Brier- bzw. Log-Score, verwendet werden modifiziertes GRPO ohne Normalisierung pro Frage oder ReMax. Fragen werden synthetisch aus chronologischen Nachrichten erzeugt. Berichtet wird: Qwen3-32B verbessert den Brier um 27 %, halbiert den Kalibrierungsfehler und schlägt Qwen3-235B. Ein 14B-Modell erreicht Frontier-Niveau.
- **Potenzial: 3/5.** Das ist die einzige Feintuning-Richtung, die direkt auf die Prognosequalität zielt. Wichtig ist eine strikte zeitliche Trennung: Der Wissensstand des Basismodells muss vor den Trainingsfragen liegen, sonst lernt es nur Erinnern. Die eigene Arena würde selbst gelabelte Daten liefern (Polymarket/Kalshi-Auflösungen).
- **Verletzt:** B2/B3.
- **Kosten (eigene Schätzung, ungeprüft):**
  - 8B, QLoRA-GRPO, ~5k Fragen, 8 Rollouts: 1× A100/H100 für 20–60 h, also **ca. 40–200 $** pro Lauf.
  - 32B: 2–4× H100 über mehrere Tage, also **mehrere hundert bis über 1.000 $**.
  - Dazu kommen Datenkosten für Nachrichten-Snapshots mit Zeitstempel (z. B. Exa/Parallel).
- **Aufwand:** sehr hoch (Datensatz mit Zeitstempeln, Kontaminationskontrolle, RL-Infrastruktur, z. B. Unsloth/TRL/verl).
- **Recht/Risiko:** Nachrichtentexte zum Training sind urheberrechtlich heikel, Lizenz der Basisgewichte beachten. Polymarket-Daten sind öffentlich, die AGB zur Nutzung der API-Daten sollte man prüfen (ungeprüft).
- **Lohnt sich, wenn:** die Arena über 2.000 eigene aufgelöste Fragen mit Zeitstempel-Kontext gesammelt hat, die Gratis-Modelle im Vorwärtstest klar schlechter kalibriert sind als der Markt **und** jemand bereit ist, 100–200 $ für ein Experiment auszugeben.

### Was der Oracle-Gratis-Server leisten kann und was nicht
- **Link:** https://blogs.oracle.com/ai-and-datascience/post/smaller-llama-llm-models-cost-efficient-ampere-cpus · https://dev.to/kas_storksoft/5-ways-to-run-ai-agents-on-oracle-cloud-free-tier-4-arm-cores-24gb-ram-29d5
- **Fakten:** Always Free Ampere A1 bietet 4 OCPU und 24 GB RAM (ARM) **ohne GPU**. Für Inferenz kleiner Modelle unter ~15B per llama.cpp oder Ollama reicht das, z. B. Llama-3-8B Q4 oder Fin-R1-7B Q4. Die von Oracle genannten bis zu 115 tok/s stammen von größeren Shapes; im Free-Tier ist es deutlich langsamer (ungeprüft). Die aktuellen Bedingungen für 2026 sind nicht geprüft.
- **Für Training reicht es nicht:** Es gibt kein CUDA. Ein LoRA eines 7B-Modells auf 4 ARM-Kernen bräuchte Tage bis Wochen (ungeprüft), und GRPO ist praktisch unmöglich. Nur Kronos-mini/-small (4–25M Parameter) wären auf CPU feintunbar (ungeprüft).
- **Was man bräuchte (aufsteigend):**
  1. Kronos-small/TimesFM-LoRA: 1× GPU mit 8–24 GB (RTX 4090/L4), 1–4 h, **unter 2 $**.
  2. 7–8B-QLoRA-SFT: 1× 24 GB (4090), 2–6 h, **1–3 $**.
  3. 14B-QLoRA-SFT oder 8B-GRPO: 1× A100/H100 80 GB, 10–60 h, **12–200 $**.
  4. 32B-GRPO: 2–4× H100, mehrere Tage, **mehrere hundert bis über 1.000 $**.
  5. Dauerbetrieb eines 14B–32B-Modells für die Inferenz: eine dauerhaft gemietete GPU (L4 ~0,70–0,80 $/h ≈ 500–580 $/Monat), oder ein serverloser Dienst (Modal), der pro Sekunde abrechnet. Das passt nicht zu einem Gratis-Projekt.
- **Potenzial: 3/5** für Oracle als Inferenz-Host eines 7–8B-Gratis-Modells nach dem 14.11. (das wäre allerdings B3: weitere Infrastruktur). Für Training: 0/5.
- **Lohnt sich, wenn:** die GitHub-Actions-Laufzeit für CPU-Inferenz eines lokalen 7B-Modells nicht reicht.

### LoRA/QLoRA-Feintuning eines Finanz- oder Trading-LLM (Qwen3 / Llama)
- **Links:** Unsloth-VRAM-Tabelle https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements · FinGPT https://github.com/ai4finance-foundation/fingpt · FinLoRA-Kosten https://finlora-docs.readthedocs.io/en/latest/benchmark_results/resources.html
- **Was es bringt:** ein kleines Gratis-Modell, das nach dem 14.11. statt Claude die Marktanalyse übernimmt, mit festem Ausgabeformat (Wahrscheinlichkeit plus Begründung) und finanzspezifischem Wortschatz.
- **Potenzial: 2/5.** Ein LoRA lehrt vor allem Format und Stil, kein Wissen über die Zukunft. Trainingsdaten aus Vergangenheitskursen bergen ein Leck-Risiko (Look-ahead), und Rücktests sind verfälscht. Ohne RL auf echten Ausgängen ist kaum ein Prognosegewinn zu erwarten.
- **Verletzt:** B2/B3 fürs Training. Die Inferenz eines 4–8B-Modells im GGUF-Format geht auf CPU (Actions: langsam, aber möglich; ungeprüft für das Laufzeitlimit).
- **Kosten:**
  - VRAM-Minimum laut Unsloth: 8B QLoRA ~6 GB, 14B ~8,5 GB, 32B ~26 GB; LoRA 16-bit 22/33/76 GB.
  - FinGPT v3.3: 17,25 h auf 1× RTX 3090 (QLoRA 4,15 h).
  - FinLoRA: 56–64 GPU-Stunden auf A5000, ca. 15 $ pro Lauf.
  - **Realistisch pro Experiment:** 8B-QLoRA auf einer RunPod 4090 für 2–6 h, also **ca. 1–3 $**. 32B auf A100 für ~5 h, also **ca. 6–10 $** (eigene Schätzung).
- **Aufwand:** mittel bis hoch (Datensatz bauen ist die eigentliche Arbeit).
- **Recht/Risiko:**
  - Qwen3 steht unter Apache-2.0 (ungeprüft für jede Variante).
  - Für Llama gilt die Meta-Community-Lizenz (Auflagen, AUP).
  - Destillation aus Claude- oder OpenAI-Ausgaben kann die AGB verletzen: Anthropic untersagt in den AGB, Ausgaben zum Training konkurrierender Modelle zu nutzen (ungeprüft, im Detail lesen).
- **Lohnt sich, wenn:** die Arena mindestens 500 eigene, aufgelöste Vorhersagen mit Begründung hat. Damit trainiert man ein kleines Modell auf den eigenen Stil und vergleicht es vorwärts mit dem Gratis-Basismodell.

### Fin-R1 (SUFE, 7B)
- **Link:** https://huggingface.co/SUFE-AIFLM-Lab/Fin-R1 · https://arxiv.org/abs/2503.16252
- **Was es bringt:** Qwen2.5-7B-Instruct mit SFT und GRPO, trainiert auf ca. 60k aus DeepSeek-R1 destillierten Finanz-Begründungsketten. Es ist stark bei FinQA (76) und ConvFinQA (85).
- **Potenzial: 2/5.** Es ist auf Finanz-Rechenaufgaben und Textverständnis trainiert, nicht auf Prognosen. Als Gratis-Modell nach dem 14.11. (CPU, GGUF, 7B) könnte es eine Analysefunktion übernehmen.
- **Verletzt:** B2 ist bei der Inferenz grenzwertig (7B auf Actions-CPU: langsam, Q4 etwa 4–5 GB RAM; ungeprüft). Ein eigenes Nachtrainieren braucht eine GPU.
- **Kosten:** Die Gewichte sind gratis. Ein GPU-Nachtraining kostet wie beim LoRA-Feintuning oben ca. 1–5 $ pro Experiment.
- **Recht/Risiko:** Laut Drittquelle gilt Apache-2.0 (https://www.sourcepulse.org/projects/2178953, ungeprüft); dazu kommen die Qwen2.5-Lizenzbedingungen.
- **Lohnt sich, wenn:** ein Gratis-Modell für die Auswertung von Bilanzen oder SEC-Dokumenten im Aktien-Teil gebraucht wird.

### Trading-R1
- **Link:** https://arxiv.org/abs/2509.11420
- **Was es bringt:** Qwen3-4B mit SFT und Curriculum-RL (GRPO) auf über 100k Begründungen, die aus proprietären Modellen „rückwärts destilliert“ wurden. Als Belohnung dient eine volatilitätsbereinigte 5-Stufen-Bewertung. Laut Paper erreicht es auf NVDA einen Sharpe von 2,72 im Rücktest.
- **Potenzial: 2/5.** Die Zahlen sind **Rücktests** auf sechs großen US-Titeln mit einem kurzen Zeitfenster und unterliegen damit genau dem Trainingswissens-Problem. Die Details stammen teils aus Drittzusammenfassungen. Methodisch ist es interessant (Belohnung = volatilitätsbereinigte Rendite).
- **Verletzt:** B2/B3 (RL-Training braucht eine GPU).
- **Kosten:** GRPO auf 4B braucht wegen mehrerer Rollouts pro Prompt mehr VRAM als SFT. Eine A100 80 GB für 10–30 h kostet **ca. 12–55 $** auf RunPod (eigene Schätzung, ungeprüft).
- **Recht/Risiko:** Die Destillation aus OpenAI-Ausgaben kann gegen deren AGB verstoßen. Ob Gewichte veröffentlicht sind, ist ungeprüft.
- **Lohnt sich, wenn:** eine öffentliche Version erscheint, die man auf CPU vorwärts testen kann. Nachbauen lohnt sich nicht.

### Zeitreihen-Basismodelle feintunen (TimesFM 2.5, Chronos-2, Moirai, Kronos)
- **Links:** TimesFM https://github.com/google-research/timesfm (LoRA-Beispiel unter `timesfm-forecasting/examples/finetuning/`) · Kronos https://github.com/shiyu-coder/Kronos · Lizenzvergleich https://www.beri.net/article/timesfm-vs-chronos-vs-moirai-time-series-foundation-model-licence-bigquery-sagemaker-cost-2026
- **Was es bringt:** Die Basismodelle werden auf die eigenen Kerzen (Krypto-, Aktien-Intervalle) angepasst, mit dem Ziel besserer Verteilungsprognosen statt Zero-Shot.
  - **TimesFM 2.5:** offizielles LoRA-Beispiel (HF Transformers + PEFT); empfohlen ist eine GPU mit mindestens 8 GB (https://www.mql5.com/en/articles/22096).
  - **Chronos-2:** Apache-2.0, Feintuning wird unterstützt.
  - **Kronos (4,1M/24,7M/102,3M Parameter, NeurIPS 2025):** Die offiziellen Finetune-Skripte für Tokenizer und Predictor sind für Multi-GPU per torchrun ausgelegt; das Beispiel nutzt 4 GPUs für Kronos-base. Kronos-mini/-small sind so klein, dass ein Feintuning auf einer 4090 oder sogar auf CPU denkbar ist (ungeprüft).
- **Potenzial: 2/5.** Bei Finanzkursen ist der Gewinn durch Feintuning meist klein, und die Gefahr der Überanpassung ist groß. Ein Rücktest auf eigenen Kerzen ist zwar nicht vom LLM-Trainingswissen betroffen, aber die Basismodelle haben öffentliche Kursdaten womöglich schon gesehen. Deshalb nur vorwärts bewerten.
- **Verletzt:** B2/B3 fürs Training. Die Inferenz der feingetunten Gewichte läuft weiter auf Actions-CPU.
- **Kosten:** Kronos-small/TimesFM-LoRA auf einer RTX 4090 (0,34 $/h) für 1–4 h kostet **unter 2 $** pro Experiment. Kronos-base auf 4× A100 für einige Stunden kostet **ca. 15–30 $** (eigene Schätzung). Modal mit 30 $ Gratis-Guthaben würde dafür reichen.
- **Aufwand:** mittel (Datenaufbereitung OHLCV, Validierung über eine Zeitspalte).
- **Recht/Risiko:**
  - TimesFM: Apache-2.0.
  - Chronos-2: Apache-2.0.
  - **Moirai 2.0: CC BY-NC 4.0** (nicht kommerziell, laut Drittquelle; ungeprüft). Für ein Hobby-Papierhandelsprojekt ist das unkritisch, für spätere Echtgeld-Nutzung problematisch.
  - Kronos: MIT (ungeprüft, Repo prüfen).
- **Lohnt sich, wenn:** die Arena zeigt, dass Kronos oder TimesFM zero-shot auf einem bestimmten Markt systematisch falsch kalibriert sind (z. B. Intervalle zu eng). Dann ein Kronos-small-Feintuning für unter 2 $ testen und es 4 Wochen vorwärts gegen das Original laufen lassen.

### BloombergGPT (nur als Referenz)
- **Link:** https://arxiv.org/abs/2303.17564
- **Was es zeigt:** Ein eigenes Finanz-LLM von Grund auf zu trainieren kostete Bloomberg etwa 0,65–1 Mio. GPU-Stunden auf 512 A100, grob 2,7–3 Mio. $ (Schätzungen aus https://finlora-docs.readthedocs.io/en/latest/intro/overview.html und FinGPT-Material). Spätere allgemeine Modelle haben es in Finanz-Benchmarks eingeholt (ungeprüft im Detail).
- **Potenzial: 1/5.** Das ist für ein Hobbyprojekt ausgeschlossen. Die Lehre daraus: Feintuning schlägt Vortraining.
- **Verletzt:** alles.

### GPU-Miete 2026: Marktüberblick
- **Links:** https://www.runpod.io/gpu-cloud/pricing · https://modal.com/pricing · https://huggingface.co/docs/hub/jobs-pricing · https://huggingface.co/docs/inference-endpoints/en/pricing · https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison
- **Preise (Drittquellen-Schnappschüsse Juni–Okt. 2026, vor Nutzung auf der Anbieterseite prüfen):**

| Anbieter | GPU | $/h | Hinweis |
|---|---|---|---|
| RunPod Community | RTX 4090 24 GB | ~0,34 | Fremd-Hosts, können ausfallen |
| RunPod Secure | RTX 4090 | ~0,89 (seit Okt. 2026) | |
| RunPod Community / Secure | A100 80 GB | ~1,19 / ~1,79 | |
| RunPod Community / Secure | H100 | ~1,99 / 2,89–3,99 | |
| Vast.ai (Marktplatz) | H100 SXM | ~1,38–1,87 | schwankende Verfügbarkeit, kein SLA |
| Lambda | H100 PCIe / SXM | 3,29 / 4,29 (19.10.2026) | |
| Modal | H100 / A100-80 | ~3,95 / ~2,50 (0,001097 $/s; 0,000694 $/s) | **Starter: 30 $/Monat gratis** |
| HF Inference Endpoints | L4 / A10G / H100 | 0,80 / 1,00 / 4,50–10 | minutengenau |
| HF Jobs | CPU bis 8× RTX PRO 6000 | 0,01–22,00 | PRO 9 $/Monat mit kleinem Guthaben (Höhe ungeprüft) |

- **Wichtig:** Abgerechnet wird pro Sekunde bzw. Minute; eine 4090 für 0,34 $/h reicht für alle LoRA-Experimente bis 14B (4-bit).
- **Bester Einstieg:** **Modal Starter mit 30 $ Gratis-Guthaben pro Monat** (etwa 7,5 h H100 oder etwa 27 h T4, laut Drittrechner https://usagepricing.com/tools/pricing-calculator/modal). Das ist praktisch ein Gratis-Kontingent; eine Kreditkarte ist eventuell nötig (ungeprüft).
- **Verletzt:** B2/B3 (eigene Infrastruktur, außerhalb von GitHub Actions).

### Fazit für die Reihenfolge (falls man irgendwann Geld ausgibt)
1. **xAI X-Suche:** einzigartige Echtzeitquelle für Polymarket, billig pro Aufruf.
2. **Modal-Starter-Guthaben (30 $/Monat):** praktisch gratis GPU für Kronos- oder TimesFM-Feintuning.
3. **Billigsuche (Exa Lite, Perplexity Fast, Parallel Turbo; 1–4 $/1.000)** als Ersatz für die Anthropic-Suche nach dem 14.11.
4. **Outcome-RL:** erst, wenn genug eigene aufgelöste Fragen vorliegen.
5. **Deep-Research-APIs und Opus-Dauerbetrieb:** zu teuer pro Markt, ohne belegten Prognosegewinn.

---

## MEV und On-Chain

### Polymarket-Wal-Tracking auf Polygon (On-Chain)
- **Links:** https://docs.polymarket.com/ (Data-API, ungeprüft im Detail), https://dune.com/ (Polymarket-Dashboards, ungeprüft)
- **Was es bringt:** Polymarket-Trades sind on-chain (Polygon) und über öffentliche Polymarket-Endpunkte einsehbar. Große Wallets ("Wale") lassen sich nach Trefferquote und PnL profilieren.
- **Potenzial: 3/5.** Die Daten sind **öffentlich und gratis**, eine Login-Hürde gibt es kaum. Allerdings sind Wal-Signale oft spät, und manche Wale handeln absichtlich als Köder. Seit 2026 gelten auffällige Wal-Trades zudem oft als Insider-Verdacht (siehe Tabu).
- **Verletzte Bedingung:** Eigentlich keine. Bezahlt sind nur Komfort-Tools (siehe Copy-Trading).
- **Kosten:** 0 € mit eigenem Code. Dune hat einen Gratis-Tarif (Grenzen 2026 ungeprüft).
- **Aufwand:** Mittel.
- **Rechtslage/Risiko:** Öffentliche Blockchain-Daten zu lesen ist unproblematisch. Wallet-Adressen können personenbeziehbar sein, also im Repo nur pseudonymisiert oder aggregiert ablegen.
- **Lohnt sich, wenn …** sofort als Gratis-Idee prüfbar. Gehört eher in den "machbar"-Teil des Tresors.

### Hyperliquid: Positionen öffentlicher Wale
- **Links:** https://hyperliquid.gitbook.io/hyperliquid-docs (Info-API, ungeprüft im Detail), https://www.coinglass.com/ (Hyperliquid-Whale-Tracker)
- **Was es bringt:** Hyperliquid legt Perp-Positionen on-chain offen. Coinglass aggregiert die Wal-Positionen, Medien zitieren laufend Long/Short-Verhältnisse, z. B. 4,5 Mrd. $ Wal-Positionen im Mai 2026. Quelle: https://crypto.news/hyperliquid-whales-park-3-66b-as-long-short-ratio-hovers-near-neutral/
- **Potenzial: 3/5.** Echte Positionsdaten großer Trader sind selten. Liquidationspreise großer Positionen zeigen Kaskaden-Risiken. Vorsicht: Medienzahlen sind teils um den Faktor 10 widersprüchlich.
- **Verletzte Bedingung:** Rohdaten öffentlich. Coinglass-API-Tarife sind kostenpflichtig (Preise ungeprüft). HyperDash konnte nicht verifiziert werden.
- **Kosten:** 0 € über die öffentliche Info-API (ungeprüft), Coinglass-API kostenpflichtig (ungeprüft).
- **Aufwand:** Mittel.
- **Rechtslage/Risiko:** Lesen gering. Wer gezielt auf die Liquidation großer Positionen hinhandelt, also ein "Hunt", bewegt sich Richtung Marktmanipulation, das ist tabu.
- **Lohnt sich, wenn …** als Gratis-Datenquelle für einen Krypto-Agenten getestet. Ebenfalls eher "machbar".

### DEX-Arbitrage (atomar, zwischen Pools/DEXs)
- **Link:** https://docs.flashbots.net/
- **Was es bringt:** Preisunterschiede zwischen Uniswap, Curve, Sushi usw. werden in einer Transaktion ausgeglichen.
- **Potenzial: 1/5.** Der Wettbewerb wird von professionellen Searchern mit Builder-Beziehungen und optimierter Infrastruktur dominiert. Als Papierhandel kann man das nicht sinnvoll simulieren, weil der Gewinn von Latenz und Inklusion abhängt.
- **Verletzte Bedingung:** Echtes Kapital, Wallet und Gas nötig. Mit Gratis-Daten oder Papierhandel nicht abbildbar.
- **Kosten:** Gas plus Builder-Bids, die meist den Großteil des Gewinns auffressen. Infrastruktur siehe unten.
- **Aufwand:** Sehr hoch: Solidity, Simulation, Bundles.
- **Rechtslage/Risiko:** Reine Arbitrage gilt allgemein als legitimes Marktverhalten (Einordnung). Das Risiko ist finanziell: Smart-Contract-Bugs, gefälschte Token als Köder ("Salmonella"-Token, ungeprüft als aktueller Begriff).
- **Lohnt sich, wenn …** man das Thema als Lernprojekt betrachtet, nicht als Ertragsquelle.

### Liquidations-Bots (Aave/Compound)
- **Links:** https://aave.com/docs/developers/liquidations, https://www.spark.money/glossary/liquidation-bot
- **Was es bringt:** Unterbesicherte Kredite werden gegen einen Liquidationsbonus von typisch 5–15 % je nach Asset abgelöst.
- **Potenzial: 1/5.** Laut einer Auswertung haben seit Anfang 2025 wenige Bots rund 207,6 Mio. $ aus 28.037 Liquidationen verdient, die fünf aktivsten davon etwa 87 %. Ein Open-Source-Bot-Repo schreibt selbst "unlikely to be profitable nowadays". Protokolle holen sich den MEV zunehmend selbst zurück (Aave SVR, Status ungeprüft). Quelle: https://ambcrypto.com/defi-stops-the-liquidation-leak-protocols-reclaim-billions-lost-to-mev-bots/
- **Verletzte Bedingung:** Echtes Kapital (oder Flash-Loans), Wallet, private Order-Flow-Kanäle.
- **Kosten:** Gas plus Bids, eigener RPC/Node.
- **Aufwand:** Hoch.
- **Rechtslage/Risiko:** Liquidieren ist eine vom Protokoll vorgesehene Funktion und damit legal (Einordnung).
- **Lohnt sich, wenn …** als **Datenquelle** statt als Bot: Liquidationsschwellen großer Positionen sind öffentlich und zeigen mögliche Kaskaden an. Das geht kostenlos per Lesezugriff und wäre eine eigene, legale Tresor-Idee.

### Backrunning über Flashbots MEV-Share
- **Link:** https://docs.flashbots.net/flashbots-mev-share/overview
- **Was es bringt:** Searcher sehen Hinweise auf private Nutzer-Transaktionen und dürfen nur **dahinter** handeln, also backrunnen. Einen Teil des Gewinns zahlen sie an den Nutzer zurück. Den Standard nennt eine Drittquelle mit 90 % (ungeprüft).
- **Potenzial: 1/5.** Starker Wettbewerb, für Hobbyisten kaum profitabel.
- **Verletzte Bedingung:** Echtes Kapital, Wallet, Bundle-Infrastruktur.
- **Kosten:** Rückzahlung an Nutzer plus Validator-Anteil. Der Event-Stream (SSE) ist kostenlos.
- **Aufwand:** Hoch.
- **Rechtslage/Risiko:** Gilt als "gutes" MEV, weil Nutzer zustimmen und mitverdienen. Wichtig ist der Unterschied zum Sandwich: Backrunning schadet dem Nutzer nicht direkt.
- **Lohnt sich, wenn …** man verstehen will, wie Order-Flow-Auktionen funktionieren. Der MEV-Share-Event-Stream ist auch als **kostenloser Datenstrom** interessant.

### Solana / Jito-Bundles
- **Links:** https://quicknode.com/guides/solana-development/transactions/jito-bundles, https://www.coindesk.com/business/2024/03/08/solana-client-developer-jito-announces-end-of-mempool-function
- **Was es bringt:** Atomare Bundles mit bis zu 5 Transaktionen und einem Tip-Gebot (Minimum laut Drittquellen 1.000 Lamports). Jito hat im März 2024 seinen öffentlichen Mempool wegen Sandwich-Angriffen abgeschaltet.
- **Potenzial: 1/5.** Wie bei Ethereum ein professionalisierter Latenz-Wettbewerb.
- **Verletzte Bedingung:** Echtes Kapital und Wallet, Infrastruktur.
- **Kosten:** Tips plus RPC. Gute Solana-RPCs sind kostenpflichtig (Preise ungeprüft).
- **Aufwand:** Hoch.
- **Rechtslage/Risiko:** Arbitrage und Backrun legitim, Sandwich tabu.
- **Lohnt sich, wenn …** nur als Lernprojekt.

### MEV-Infrastruktur (eigene Nodes, Latenz)
- **Was es bringt:** Ohne eigenen Node bzw. Premium-RPC, Colocation und Builder-Kontakte ist man im MEV-Wettbewerb chancenlos.
- **Potenzial: 1/5.**
- **Verletzte Bedingung:** Kostenpflichtig. Läuft nicht auf GitHub Actions, das mit Minuten-Takt und ohne dauerhafte Prozesse dafür ungeeignet ist.
- **Kosten:** Ein eigener Ethereum-Full-Node braucht mehrere TB SSD und einen Dauer-Server (grob 50–300 €/Monat, ungeprüft). Premium-RPC- und Mempool-Dienste kosten meist dreistellige Dollarbeträge pro Monat (ungeprüft).
- **Aufwand:** Sehr hoch.
- **Rechtslage/Risiko:** Unbedenklich, aber teuer.
- **Lohnt sich, wenn …** das Projekt den Papierhandel verlässt und MEV der Kern wird. Für die Arena: nein.

### Sandwich-Angriffe (Einordnung, nicht verfolgen)
- **Was es ist:** Eine Order vor und eine nach der Nutzer-Transaktion platzieren, um am Preisrutsch des Opfers zu verdienen.
- **Potenzial: 0/5.** Ethisch schädlich und rechtlich riskant.
- **Rechtlicher Kontext (kurz):**
  - **Peraire-Bueno-Brüder (USA):** Vorwurf, rund 25 Mio. $ über eine ausgenutzte MEV-Boost-Schwachstelle von Sandwich-Bots erbeutet zu haben. Der erste Prozess endete am 7.11.2025 mit einem Mistrial. Die Staatsanwaltschaft beantragte eine Wiederaufnahme für Frühjahr 2026, frühestens 20.4.2026. Ausgang 2026 **ungeprüft**. Quellen: https://www.theblock.co/news/regulation/2025-11-11-prosecutors-seek-new-trial-mit-brothers-25-million-ethereum-fraud-case-ends-mistrial-378414, https://www.law360.com/cases/6645249291f3b8076188bc47/articles
  - **Eisenberg/Mango Markets:** Orakel- bzw. Preismanipulation. Die Verurteilung wurde am 23.5.2025 von einem SDNY-Richter aufgehoben (Rule 29: fehlender Nachweis von Täuschung und Gerichtsstand). Das ist **kein Freibrief**: Zivil- und EU-Recht bleiben (MiCA-Marktmissbrauchsregeln, Einordnung). Quellen: https://nysd.uscourts.gov/sites/default/files/2025-05/23cr10%20Opinion%20and%20Order.pdf, https://www.wilmerhale.com/en/insights/client-alerts/20250804-reversals-of-fraud-charges-highlight-difficulties-in-bringing-market-manipulation-cases
- **Lohnt sich, wenn …** nie. Gehört zu den Tabus unten.

---

## Copy-Trading und Signale

### eToro CopyTrader
- **Link:** https://www.etoro.com/copytrader/
- **Was es bringt:** Echte Portfolios von "Popular Investors" mit Historie und Risikoscore. Für die Arena als **Benchmark** interessant: Schlagen die KI-Agenten die Top-Kopierquellen?
- **Potenzial: 2/5.** Als Benchmark nett, aber ohne API für Privatleute nur manuell nutzbar (ungeprüft).
- **Verletzte Bedingung:** Konto mit KYC. Automatisches Auslesen ohne API widerspricht den AGB (ungeprüft).
- **Kosten (2026, Drittquellen):** Mindestbetrag pro kopiertem Trader ca. 200 $, keine Managementgebühr, 5 $ pro Auszahlung, 10 $/Monat Inaktivität nach 12 Monaten. Krypto-Spread ca. 1 %–1,5 %. Popular Investors erhalten bis 1,5 % p. a. auf das kopierte Vermögen, bezahlt von eToro. Quelle: https://investormint.com/software-tools/etoro-review-2026-copy-trading-fees-risks
- **Aufwand:** Gering (manuell).
- **Rechtslage/Risiko:** eToro ist in der EU über CySEC reguliert. Für Kopierer gering, finanzielles Risiko normal.
- **Lohnt sich, wenn …** man einen menschlichen Vergleichsmaßstab will. Dann einmal im Monat manuell 2–3 Top-Trader-Renditen notieren.

### Polymarket-Wal-Folgen: Polywhaler, PolyTrack und Co.
- **Links:** https://pm.wiki/th/compare/polywhaler-vs-traderwin-fun, https://dappradar.com/dapp/polytrack, https://oddsjam.com/subscribe
- **Was es bringt:** Fertige Feeds für große Polymarket-Trades (Polywhaler: ab 10.000 $, Schwelle einstellbar). Dazu Wallet-Profile mit PnL, Trefferquote und Kategorien. PolyTrack bewertet große Trades als hohe Schwere ab 250.000 $ und mittlere bei 100–250.000 $. Copy-Trading ist bei PolyTrack angekündigt, aber noch nicht da.
- **Potenzial: 2/5.** Alles, was diese Tools zeigen, kommt aus öffentlichen Daten und lässt sich selbst bauen. Nutzer berichten, dass reines Wal-Folgen nach Kosten oft nicht profitabel ist (ungeprüft, anekdotisch).
- **Verletzte Bedingung:** Kostenpflichtig im Premium-Tarif.
- **Kosten:** Polywhaler "Freemium", Paid-Preis ungeprüft (Stand Juni 2026). PolyTrack mit Gratis-Tarif (Closed Source). OddsJam bietet "Tail the world's top traders" für **449,99 $/Monat** an (Stand 10/2026). Apify-Scraper ab ca. 5 $ pro 1.000 Wal-Trades.
- **Aufwand:** Gering (Tool) bzw. mittel (selbst bauen).
- **Rechtslage/Risiko:** Gering. Aber wer erkennbaren Insidern folgt, kann sich nach US-Sicht selbst in Insider-Fragen verstricken (Einordnung, ungeprüft). Polymarket ist für Personen in Deutschland je nach Produkt eingeschränkt (Stand 2026 ungeprüft).
- **Lohnt sich, wenn …** man es nicht selbst bauen will. Für die Arena: selbst bauen mit Gratis-Daten.

### Kongress-Trades: Unusual Whales, Quiver Quantitative, Autopilot, NANC/KRUZ
- **Links:** https://unusualwhales.com/, https://www.quiverquant.com/, https://www.etfcentral.com/fund/NANC, https://www.etf.com/sections/etf-basics/nanc-vs-kruz-battle-congress-stock-trackers
- **Was es bringt:** Aufbereitete STOCK-Act-Meldungen von US-Abgeordneten. Die Rohdaten sind öffentlich, kommen aber bis zu 45 Tage verzögert.
- **Potenzial: 2/5.** Durch die Melde-Verzögerung ist der Vorteil gering. Der ETF NANC macht das einfach passiv.
- **Verletzte Bedingung:** Komfort-Daten kostenpflichtig, Autopilot braucht ein Brokerkonto (US-fokussiert).
- **Kosten:** Quiver Premium ca. 25 $/Monat, API-Tarife 10–75 $ (Drittquellen, ungeprüft). Unusual Whales ab ca. 30 $/Monat (widersprüchlich, ungeprüft). Autopilot: 1 Portfolio gratis, sonst ca. 99–100 $/Jahr (Stand 2025). **NANC** TER 0,74 %, ca. 263 Mio. $ Volumen (April 2026). **KRUZ** TER 0,75–0,83 % je nach Quelle, ETFdb führt KRUZ als "no longer active" (ungeprüft). Quelle Autopilot: https://www.salon.com/2025/03/17/pelosi-tracker-shows-us-how-to-trade-stocks-like-politicians/
- **Aufwand:** Gering.
- **Rechtslage/Risiko:** Öffentliche Meldungen nachzuhandeln ist legal (Einordnung). US-ETFs sind für EU-Privatanleger wegen PRIIPs/KID meist nicht kaufbar (Einordnung).
- **Lohnt sich, wenn …** man NANC als Vergleichs-Benchmark in die Arena aufnimmt. Kursdaten gibt es gratis.

### 13F-Folgen (Hedgefonds-Positionen)
- **Link:** https://www.sec.gov/edgar/search/ (öffentlich, gratis). Kostenpflichtig aufbereitet z. B. WhaleWisdom oder Quiver (Preise ungeprüft).
- **Was es bringt:** Quartalsweise Long-Positionen großer US-Fonds.
- **Potenzial: 2/5.** Bis zu 45 Tage nach Quartalsende verzögert, keine Shorts, keine Derivate-Details.
- **Verletzte Bedingung:** Nur die Komfort-Tools kosten Geld, die Rohdaten nicht.
- **Kosten:** 0 € über EDGAR.
- **Aufwand:** Mittel (XML parsen).
- **Rechtslage/Risiko:** Unbedenklich. Die SEC verlangt für automatischen Zugriff einen User-Agent mit Kontakt und begrenzt die Anfragerate (Fair-Access-Regel, ungeprüft für 2026).
- **Lohnt sich, wenn …** man gratis einen langsamen Aktien-Agenten testen will. Gehört eher in den "machbar"-Teil.

### Bitget / Bybit Copy-Trading
- **Links:** https://casptracker.eu/exchange/bitget/, https://defillama.com/mica/germany
- **Was es bringt:** Krypto-Futures-Copy-Trading mit öffentlichen Ranglisten.
- **Potenzial: 1/5.** Ranglisten sind vom Survivorship-Bias geprägt, oft gehebelt und manipulierbar.
- **Verletzte Bedingung:** Konto und KYC. **Bitget:** laut Tracker keine MiCA-Lizenz, Deutschland seit 16.1.2026 für Neuanmeldungen gesperrt und in den AGB als "Prohibited Country" geführt (Stand 14.10.2026). **Bybit:** seit Mai 2025 MiCA-Lizenz aus Österreich (bybit.eu). Laut einer Quelle umfasst sie nur Spot, keine Futures. Ob Copy-Trading für deutsche Kunden verfügbar ist, ist ungeprüft.
- **Kosten:** Gewinnbeteiligung an den Signalgeber (meist 8–20 %, ungeprüft) plus Handelsgebühren.
- **Aufwand:** Gering.
- **Rechtslage/Risiko:** Hoch bei Bitget, weil Umgehung der Länder-Sperre ein AGB-Bruch und regulatorisch heikel ist. Bei Bybit EU nur im lizenzierten Umfang.
- **Lohnt sich, wenn …** praktisch nicht. Allenfalls die öffentlichen Ranglisten als Kontra-Indikator betrachten.

### Telegram-Signalgruppen (Betrugsrisiko)
- **Links:** https://bafin.de/SharedDocs/Veroeffentlichungen/EN/Verbrauchermitteilung/unerlaubte/2023/meldung_2023_12_13_fx_flatforex_en.html, https://mondovisione.com/news/justtrade-bafin-warns-against-identity-fraud-in-whatsapp-groups-and-against-web-20251210
- **Was es bringt:** Angebliche Kauf- und Verkaufssignale.
- **Potenzial: 0–1/5.** Die BaFin warnt wiederholt vor Telegram- und WhatsApp-Kanälen ohne Erlaubnis und vor Identitätsbetrug (z. B. "FXflatforex signals", gefälschte Broker-Gruppen 2025). Häufige Muster: Pump-and-Dump, Vorab-Kauf durch die Betreiber, Abo-Abzocke.
- **Kosten:** Meist 30–300 € pro Monat Abo (ungeprüft, typisch).
- **Rechtslage/Risiko:** Hoch. Als Konsument verliert man Geld, und wer in Pump-Gruppen mitmacht, rutscht in die Marktmanipulation.
- **Lohnt sich, wenn …** nie als Signal. Höchstens als **Anti-Signal**: Ein Ticker, der in Pump-Kanälen auftaucht, ist ein Warnzeichen.

### Rechtsfrage: Signale der Arena an Dritte weitergeben
- **Links:** https://www.gvw.com/aktuelles/blog/detail/aktualisiertes-merkblatt-der-bafin-zur-anlageberatung-und-einordnung-von-finfluencern, https://www.frankfurt-main.ihk.de/standortpolitik/finanzplatz-frankfurt/finanzdienstleister-am-finanzplatz-frankfurt/brancheninformationen/hinweise-erlaubnispflicht-32-kwg-finanzdienstleistungsinstitute-5248146
- **Worum es geht:** Wer gewerbsmäßig Anlageberatung erbringt, braucht eine BaFin-Erlaubnis (§ 32 KWG bzw. WpIG). Unerlaubtes Betreiben ist strafbar (§ 54 KWG, § 82 WpIG). Laut BaFin-Merkblatt (2025) sind allgemeine Tipps von Finfluencern **meist keine** Anlageberatung im Sinne des KWG. Personalisierte Empfehlungen, ein bezahlter Signaldienst, Finanzportfolioverwaltung oder automatische Ausführung für Dritte (Copy-Trading-Anbieter!) können dagegen erlaubnispflichtig werden. Dazu kommen Pflichten nach Art. 20 MAR für Anlageempfehlungen: Offenlegung von Interessenkonflikten (Einordnung, ungeprüft im Detail).
- **Potenzial/Relevanz: 5/5 als Vorsicht.**
- **Kosten:** Erlaubnis und Compliance wären für ein Hobby unverhältnismäßig.
- **Lohnt sich, wenn …** die Arena öffentlich bleibt als **Papierhandels-Experiment mit Disclaimer** ("keine Anlageberatung, keine Empfehlung"). Kein Abo, kein Telegram-Signalkanal, keine automatische Weitergabe an fremde Konten.

---

## Kurzfazit Infrastruktur und kreative Hebel

1. **Echter Mehrwert ohne Bezahlung:** dauerhafter Polymarket-WS-Sammler (öffentlich, kein Konto) auf Oracle Free oder einem Raspberry Pi, ECMWF/NWS-Wetterdaten, Metaculus als Prior, Metaculus-FutureEval-Teilnahme.
2. **Latenz-Investitionen** (Kolokation, Tokyo, Profi-Newsfeeds, Sportradar) sind für LLM-Agenten im Sekundentakt wirkungslos und ein Profi-Spielfeld. Polymarket bekämpft Latenz-Arbitrage inzwischen aktiv per Gebühr.
3. **Liquiditäts-Rewards** sind für einen Nutzer aus DE faktisch nicht zugänglich: Polymarket geo-sperrt DE, Kalshi-LIP schließt Nicht-US-Nutzer aus. Sie taugen höchstens als Papier-Benchmark.

---

## Tabu – strafbar, nicht verfolgen

> Kurz gefasst, ohne Details. Einordnung, keine Rechtsberatung.

- **Insiderhandel (Börse):** Wer auf Basis nicht öffentlicher, kursrelevanter Informationen handelt, verstößt in der EU gegen Art. 14 MAR. Das ist strafbar (§ 119 WpHG).
- **Wettmarkt-Insiderhandel:** Die CFTC hat 2026 Insiderhandel auf Prognosemärkten zur Top-Priorität erklärt. Im Mai 2026 folgte die erste Klage samt Strafverfahren (ein Google-Mitarbeiter, der mit vertraulichen Daten auf Polymarket gewettet haben soll). Polymarket und Kalshi verbieten das seit März 2026 in eigenen Regeln. Quellen: https://www.sidley.com/en/insights/publications/2026/05/sidley-discusses-the-first-prediction-market-insider-trading-case, https://cointelegraph.com/news/cftc-enforcement-chief-warns-insider-traders-on-prediction-markets-will-be-prosecuted
- **Marktmanipulation:** Wer Preise durch Scheingeschäfte, Falschinformationen oder Pump-Kampagnen beeinflusst, verstößt gegen Art. 12/15 MAR bzw. die Marktmissbrauchsregeln für Kryptowerte in MiCA (Einordnung). Das ist strafbar.
- **Front-Running fremder Orders:** Wer Kenntnis von Kunden- oder fremden Aufträgen nutzt, um davor zu handeln, betreibt Insiderhandel bzw. Untreue gegenüber den Betroffenen.
- **Wash-Trading:** Handel mit sich selbst täuscht über Volumen und Preis. Das ist Manipulation und auf Polymarket ein ausdrücklich verfolgtes Thema.
- **Sandwich-Angriffe und Orakel-Manipulation:** Das schädigt gezielt andere Nutzer oder Protokolle durch künstliche Preise. US-Strafverfahren laufen bzw. liefen (Peraire-Bueno, Eisenberg). Auch ein Freispruch aus Verfahrensgründen macht es nicht legal.
- **Hacking und Datenklau:** Unbefugter Zugriff auf Systeme oder Daten ist strafbar (§§ 202a ff., 303a StGB). Auch das Umgehen von Login-, Paywall- und Zugangssperren gehört dazu, je nach Fall.
- **Kontenmissbrauch:** Fremde oder geliehene Zugänge (Uni-WRDS eines Freundes, geteilte API-Keys), gekaufte Konten oder Fake-KYC zur Umgehung von Ländersperren bedeuten Lizenz- und AGB-Bruch, teils Betrug.
- **Unerlaubte Finanzdienstleistungen:** Ein bezahlter Signaldienst, Vermögensverwaltung oder Copy-Trading-Angebot für Dritte ohne BaFin-Erlaubnis ist strafbar (§ 54 KWG, § 82 WpIG).

