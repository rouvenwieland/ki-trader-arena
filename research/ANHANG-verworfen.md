# Anhang: verworfene Kandidaten (Stand 30.10.2026)

Hier steht alles, was beim Ausdünnen (Weitblick Schritt 4) gestrichen wurde – entweder weil es einen harten Filter verletzt (Lizenz, Kosten, Login/ToS, US-Sperre, keine Lizenzdatei, archiviert) oder weil eine bessere Alternative existiert. Gliederung wie in [RECHERCHE-2026-10.md](RECHERCHE-2026-10.md). „Verworfen“ heißt nicht „schlecht“: Viele Projekte sind als Ideengeber genannt, nur der Code bzw. die Quelle ist für die Arena ungeeignet.

**Häufigste Gründe:**
- Lizenz: AGPL/GPL (z. B. backtesting.py, backtrader, freqtrade, TradingGoose, Panshul-Bot), Nicht-kommerziell (TimesFM 3.0, Moirai, TabPFN 2.5/3, LiveTradeBench, FinBERT CC BY-NC-SA), „Commons Clause“ (vectorbt), keine Lizenzdatei (metac-bot-template, nof0, AI-Trader).
- Zugang: Schlüssel/Bezahlung (Coinglass, Glassnode, CryptoQuant), Login/Kontopflicht mit Privatnutzungsklausel (Betfair), US-IP-Sperre (Binance 451, Bybit/BitMEX 403), Anti-Bot (Stooq, Farside, Nasdaq), abgeschaltet (Reddit `.json`, 538, IEX Cloud, CoinCap v2, GitHub Models, pytrends archiviert).
- Personenbezug/Überwachung bzw. heikle Bedingungen: OpenSky/ADS-B, Telegram-Scraping, YouTube-Transkripte, ACLED.
- Unterlegen: ganze Agenten-Frameworks (CrewAI, LangGraph, AutoGen, Hermes) gegenüber Mustern in der eigenen Schleife; schwere Bibliotheken (Riskfolio ~670 MB, ECharts/Plotly) gegenüber leichten Alternativen.

---

## 1. LLM-Trading-Agenten, Multi-Agenten-Systeme und kreative Methoden
| Name | Link | Grund |
|---|---|---|
| TradingAgents als Framework (nicht die Muster) | https://github.com/TauricResearch/TradingAgents | Unterlegen für diesen Zweck: LangGraph-Abhängigkeit, ~10+ LLM-Aufrufe je Ticker und Runde, aktienzentriert. Das harte Budget und gleiche Werkzeuge für die Liga wären schwer zu halten. Nur Muster übernehmen. |
| TradingAgents-CN | https://github.com/hsliuping/TradingAgents-CN | Mischlizenz mit proprietären Teilen, kein Mehrwert gegenüber dem Original |
| LiveTradeBench (Code) | https://github.com/ulab-uiuc/live-trade-bench | Lizenz PolyForm **Noncommercial** (Filter: MIT/Apache/BSD bevorzugt). Nur Ideen aus dem Paper. |
| TradingGoose | https://github.com/TradingGoose/TradingGoose.github.io | Lizenz **AGPL-3.0** (LICENSE gelesen, letzter Commit 2026-04-22), Web-App rund um eine TradingAgents-artige Pipeline, kein zusätzliches Muster |
| Hermes Agent | https://github.com/NousResearch/hermes-agent | Bereits in DECISIONS.md verworfen, keine neuen Gründe |
| CrewAI / LangGraph / AutoGen | siehe oben | Framework-Overhead ohne Mehrwert gegenüber der eigenen Schleife. crewAI-examples ohne LICENSE-Datei. |
| Polymarket/agents | https://github.com/Polymarket/agents | Archiviert, Stand 2024, für echten Handel gebaut |
| agents-for-openbb | https://github.com/OpenBB-finance/agents-for-openbb | Archiviert, an OpenBB Workspace gebunden |
| HKUDS/AI-Trader (Plattform) | https://github.com/HKUDS/AI-Trader | Externe Plattform mit Registrierung und Signal-Sharing (Daten verlassen die Arena), keine LICENSE-Datei im Root |
| FinGPT | https://github.com/AI4Finance-Foundation/FinGPT | Fine-Tuning und Modelle, GPU nötig, kein Entscheidungsmuster |
| QuantAgent / QuantHarness | https://github.com/Y-Research-SBU/QuantAgent | Vision-LLM auf Chartbildern für HFT: teuer, passt nicht zum 15-min-Takt |
| FinCon (Code) | https://github.com/The-FinAI/FinCon | Code nicht veröffentlicht (laut README). Methode nur als Muster. |
| OctagonAI kalshi-trading-bot-cli (Code) | https://github.com/OctagonAI/kalshi-trading-bot-cli | Kernfunktion braucht die kostenpflichtige Octagon-API. Nur Gate-Ideen übernommen. |
| metac-bot-template (Code/Text) | https://github.com/Metaculus/metac-bot-template | Keine LICENSE-Datei. Gerüst nur als Idee in eigener Formulierung. |
| nof0 (Prompt-Rekonstruktion) | https://github.com/nof0-ai/nof0 | Keine LICENSE-Datei, Inhalt ausdrücklich „abgeleitet“. Nur Feldideen. |
| llm_multiagent_debate (Code) | https://github.com/composable-models/llm_multiagent_debate | Keine LICENSE-Datei. Evidenz („Debate or Vote“) spricht ohnehin für Abstimmen statt langer Debatte. |
| AgenticTrading | https://github.com/Open-Finance-Lab/AgenticTrading | Ungewöhnliche Lizenz (OpenMDW-1.0), schweres Protokoll-Framework |
| TradExpert, MarketSenseAI 2.0 | https://arxiv.org/abs/2411.00782 , https://arxiv.org/abs/2502.00415 | Unterlegen: Fine-Tuning bzw. Aktien-RAG, nur Backtest-Zahlen. Höchstens ein Satz (HyDE) übernommen. |
| Dynamischer Charakter (FinMem: risikofreudig nach Gewinn) | https://github.com/pipiku915/FinMem-LLM-StockTrading | Würde die festen Risikoprofile verwischen, die die Arena vergleichen will |

---


## 2. Benchmarks, Evaluation, Schutz vor Lookahead
| Name | Link | Grund |
|---|---|---|
| mlfinlab (Hudson & Thames) | https://github.com/hudson-and-thames/mlfinlab | Proprietäre/kostenpflichtige Lizenz (ungeprüft); PBO/DSR lassen sich frei selbst implementieren |
| LiveTradeBench als Abhängigkeit | https://github.com/ulab-uiuc/live-trade-bench | PolyForm Noncommercial; die Arena ist funktional weiter → nur als Paper/Referenz |
| AI-Trader-Code | https://github.com/HKUDS/AI-Trader | Keine LICENSE-Datei (nur Badge), inzwischen TypeScript-Plattform → nur Ideen |
| PolyBench-Code | https://github.com/PolyBench/PolyBench | Keine LICENSE-Datei → nur Metrik-Idee (CWR) |
| pypbo als Abhängigkeit | https://github.com/esvhd/pypbo | AGPL-3.0; Formeln selbst implementiert |
| net:cal | https://github.com/EFS-OpenSource/calibration-framework | Schwere Abhängigkeiten (Installation im Test abgebrochen); ECE/Reliability selbst oder per model-diagnostics |
| properscoring | https://github.com/properscoring/properscoring | Archiviert seit 2022; scoringrules ersetzt es |
| FinBen/PIXIU als Messgröße | https://github.com/The-FinAI/PIXIU | Statische, wahrscheinlich verseuchte Finanz-QA; sagt nichts über Handelserfolg |
| InvestorBench/StockBench-Rücktests als Messung | siehe oben | Historische Zeiträume vor dem Cutoff aktueller Modelle → Lookahead (Profit Mirage) |
| nof1 Alpha Arena als Werkzeug | https://nof1.ai | Kein Code; Methodik ohne Statistik → nur Lehrbeispiel |
| Original quantopian/pyfolio & empyrical | https://github.com/quantopian/pyfolio | Durch die „-reloaded“-Forks ersetzt (Archivstatus ungeprüft) |
| Bench to the Future (direkt) | https://evals.futuresearch.ai/ | Zugang nur auf Anfrage; Idee eingefrorener Korpus übernehmbar, Daten nicht |

---


## 3. Zeitreihen-Foundation-Modelle und Basislinien
- **TimesFM 3.0**: Gewichte unter Non-Commercial- und „non-production“-Lizenz
- **Moirai 1.x / MoE / 2.0 / moirai-agent**: CC-BY-NC-4.0
- **TimeH2O-v1 (h2o.ai)**: Platz 1 auf fev-bench, aber „h2o-model-non-commercial-licence“ und gated
- **TabPFN 2.5 / 3 (für TabPFN-TS)**: nicht-kommerzielle Lizenz. Nur v2 ist Apache plus Attribution.
- **TimeGPT (Nixtla)**: geschlossene API, kostenpflichtig, Schlüssel nötig
- **Lag-Llama, Time-MoE, Timer/Timer-XL, TimesFM 2.0**: veraltet bzw. auf Benchmarks klar überholt; teils ohne Quantile
- **MOMENT, YingLong**: nicht für zero-shot-Prognose gedacht bzw. kaum verbreitet; kein erwartbarer Mehrwert
- **Toto 2.0 ab 313M, t0, PatchTST-FM, Granite-Ensemble, Timestral-209M**: für CPU in 10 min zu groß bzw. zu langsam, ohne Aussicht auf Finanz-Mehrwert. Das Ensemble hat dazu Test-Leakage.
- **neuralforecast / NeuralProphet**: brauchen Training pro Reihe; Literatur zeigt keinen Zero-shot-Nutzen bei Renditen
- **Kronos-base**: laut Benchmark-Logik kaum Vorteil; CPU-Zeit ×4 ggü. small (ungeprüft)


## 4. Forecasting-Methoden und Wettmarkt-Daten
- **Good Judgment Open / INFER**: keine öffentliche API (GJOpen antwortete 406 auf JSON-Abruf); Scraping widerspräche den Bedingungen.
- **Metaforecast (QURI) API**: TLS-Verbindung aus der Sandbox scheiterte; Projekt-Status unklar → ungeprüft, nicht empfohlen.
- **Betfair**: Konto nötig, nur private Wettzwecke, kommerzielle/öffentliche Nutzung genehmigungspflichtig.
- **Hedgehog Markets**: nicht getestet, Aktivität unklar → ungeprüft, keine Priorität.
- **Dome API**: Schlüssel nötig, Mehrwert gegenüber direkten APIs gering, Doku ungeprüft.
- **pmxt als Ersatz der Adapter**: zu großer Umbau, 1.454 offene Issues, TS-Kern; nur als Referenz.
- **Panshul-Code**: AGPL-3.0 – Ideen ja, Code nein (würde Lizenz auf das Repo ausdehnen).
- **Polymarket/agents, py-clob-client**: archiviert; Handelsfunktionen werden nicht gebraucht.
- **Lightning Rod Foresight lokal**: 32B-Modell auf Actions-CPU nicht lauffähig; nur über (ggf. kostenpflichtige) API.
- **ESPN site.api**: inoffiziell ohne Nutzungsfreigabe → nicht ohne Klärung einbauen.
- **Metaculus-Communityprognosen als Signal**: Token nötig, CP nur für ~50 Fragen frei, Bedingungen restriktiv; Q2-Teilnehmer fand keinen Nutzen.
- **Pauschale Extremisierung** (Faktor 1,5–2,5 wie bei menschlichen Ensembles): für LLM-Ensembles umstritten; erst nach eigener Kalibrierung (M6).


## 5. Backtesting/Ausführung, Risiko/Portfolio, Signale/Regime
- **vectorbt PRO**: kostenpflichtig, privat. Fällt durch den Filter.
- **backtrader**: GPL-3.0, seit 08/2024 ohne Push. Keine Teile nötig.
- **backtesting.py**: AGPL-3.0, für ein öffentliches Repo ungünstig, und ohne Mehrwert für Orderbuch-Füllung.
- **freqtrade / cvxportfolio**: GPL-3.0. Nur Ideen übernehmen, keinen Code.
- **NautilusTrader als Abhängigkeit**: LGPL-3.0 (Nutzung als Bibliothek wäre zulässig), aber sehr groß (Rust-Wheels, Python ≥3.12) und eine komplett andere Architektur. Nur das Konzept übernehmen.
- **finta**: LGPL, archiviert seit 2022.
- **tulipy**: LGPL, letzte Version 2019.
- **pandas-ta (twopirllc)**: nur Beta 0.4.71b0 von 09/2025, Repo in der GitHub-Suche nicht auffindbar, Lizenz in den PyPI-Metadaten fehlt. Bei Bedarf pandas-ta-classic (MIT) nehmen.
- **Riskfolio-Lib** (für GitHub Actions): 63 s und rund 670 MB Installation je Lauf. skfolio deckt dasselbe mit rund 150 MB ab.
- **qlib, FinRL, ABIDES, mbt_gym, zipline-reloaded, Jesse**: andere Zielsetzung (RL, Aktien-Tagesdaten, Agentensimulation) oder archiviert bzw. veraltet. Kein Nutzen für eine Börse, die gegen echte Bücher füllt.
- **tsfresh, polars-talib/polars_ta**: hunderte unbenannte Features bzw. Polars ohne Bedarf. Für LLM-Agenten nicht lesbar.
- **PyLimitOrderBook**: ungeprüft, die Arena braucht kein eigenes Matching.
- **hurst / bayesian-changepoint-detection als PyPI-Pakete**: Releases von 2019. Die Algorithmen besser in wenigen Zeilen selbst schreiben.


## 6. Gratis-Marktdaten: Krypto, Aktien/ETF, Makro
| Quelle | Grund |
|---|---|
| Binance.com (Spot/Futures) | 451 von US-IP, die ToS schließen US aus. Daten indirekt über Hyperliquid `predictedFundings` und CoinGecko Derivate. |
| Bybit | 403 (CloudFront-Länderblock) |
| BitMEX | 403 von US-IP |
| Farside Investors (ETF-Flows) | Cloudflare-Anti-Bot (403), keine API. „All rights reserved“, Weiterverbreitung ungeklärt. **Nicht umgehen.** |
| Stooq | Anti-Bot und Verbindungsreset (bereits so entschieden) |
| Nasdaq-API (`api.nasdaq.com` Earnings-Kalender) | Blockiert Cloud-Clients (HTTP/2-Fehler, Timeout). Inoffiziell, ToS verbieten automatisierten Zugriff nach allgemeiner Kenntnis (ungeprüft). |
| CoinCap v2 | nicht mehr erreichbar (502). v3 nur mit Schlüssel und ohne Mehrwert gegenüber CoinGecko/CoinPaprika. |
| CryptoCompare / CoinDesk Data | jetzt schlüsselpflichtig (401), die Free-Bedingungen nicht geprüft. Kein Mehrwert. |
| CoinMarketCap | Schlüssel nötig, die ToS des Basic-Plans erlauben nach allgemeiner Kenntnis keine Weiterverbreitung (ungeprüft). Kein Mehrwert gegenüber CoinGecko. |
| Coinglass | Schlüssel nötig, ein dauerhafter Gratis-Plan ist nicht nachgewiesen |
| Glassnode, CryptoQuant, Laevitas, Velo Data | Kerndaten nur bezahlt oder hinter Login. Nicht getestet, laut Vorwissen ungeprüft. Ersatz: Coin Metrics Community, blockchain.info, mempool.space. |
| Dune Analytics | API schlüsselpflichtig, Credits-Modell. Abfragen ohne Konto nicht möglich (ungeprüft). Aufwand höher als Nutzen. |
| bitinfocharts | keine API, nur Scraping von HTML. Nicht genutzt. |
| IEX Cloud | 2024 eingestellt (laut Vorwissen, ungeprüft) |
| Nasdaq Data Link (Quandl) | die meisten freien Datensätze (WIKI u. a.) eingestellt. Für Marktdaten heute kaum gratis (ungeprüft). |
| Marketstack | Free-Tier nach Vorwissen 100 Aufrufe/Monat und EOD only (ungeprüft), zu wenig |
| Investing.com / ForexFactory Wirtschaftskalender | keine API. Scraping laut ToS untersagt (ungeprüft). |
| World Bank / IMF (als Kernquelle) | erreichbar, aber jährliche Daten ohne Handelsrelevanz. Nur Kontext. |

---


## 7. Nachrichten/Stimmung, alternative Daten, MCP-Server
| Kandidat | Grund |
|---|---|
| Reddit `.json` ohne OAuth | Liefert 403 (seit Mai 2026 laut Drittquellen abgeschaltet). Laut Data-API-Bedingungen ohnehin nur mit registrierter App erlaubt. Der Code-Pfad in `news.reddit()` ist toter Code. |
| pytrends | Repo archiviert (2025), inoffiziell, häufig 429 von Cloud-IPs |
| Telegram `t.me/s`-Scraping | Keine offizielle Lese-API ohne Nutzerkonto. Webvorschau-Scraping ist ToS-grau. Hohe Desinformationsquote. |
| YouTube-Transkripte | ToS untersagen automatisierten Zugriff außerhalb der Data-API, und die Data-API liefert keine fremden Transkripte |
| Podcasts plus Whisper | Legal, aber CPU-Transkription in Actions ist zu teuer bei geringem Mehrwert |
| ADS-B Exchange | API kostenpflichtig; Personen- bzw. Jet-Tracking ist Überwachung |
| OpenSky (für den Livebetrieb) | Laut Drittquelle braucht operative oder automatisierte Nutzung eine schriftliche Vereinbarung. Flugverfolgung von Personen widerspricht dem Filter. Höchstens Aggregate nach Rückfrage bei OpenSky. |
| ACLED | Registrierung, kein Scraping, keine abgeleiteten Produkte, keine kommerzielle Nutzung. Die Veröffentlichung auf einer öffentlichen Webseite bzw. in einem öffentlichen Repo ist problematisch. |
| TSA-Durchsatz, BLS-RSS | Aus Cloud-IPs per Akamai gesperrt (403). Umgehen ist ausgeschlossen. |
| Sentinel Hub / Copernicus-Bilder | Bildanalyse ist für den Nutzen zu aufwendig |
| USDA, ENTSO-E, GridStatus | Kein passender Markt in der Arena (vorerst) |
| FinancialBERT, finbert-tone | Keine Lizenzangabe im Hub |
| FinGPT-sentiment (Llama-2-13B-LoRA) | Auf CPU in Actions nicht praktikabel; das LLM der Fonds kann das selbst |
| Prediction-Market-MCPs, FRED-MCP, Yahoo-MCPs | Doppeln vorhandene, bessere eigene Adapter (prediction-mcp ist zudem archiviert) |
| Alpaca- und CCXT-MCP als Agenten-Werkzeug | Order-Tools am echten Broker widersprechen der Echtgeld-Regel; nur der Liga-Teil mit Anthropic könnte sie nutzen |
| Box Office Mojo, Spotify Charts | Scraping-Verbot (IMDb) bzw. Login nötig |
| 538-Umfrage-CSV | Dienst eingestellt (302 auf ABC News) |

---


## 8. LLM-Kosten, Gratis-Modelle, Dashboards
- **GitHub Models**: seit 30.07.2026 eingestellt (Doku + Test).
- **Batch-API für Fondsrunden**: keine Werkzeugschleife, bis zu 24 h Latenz (A5).
- **Kontext-Editing / Kompaktierung**: kein Sparhebel, Runden zu kurz (A13).
- **Memory-Tool**: Notizbuch existiert und ist modellneutral (A14).
- **LLMLingua-2**: zahlenlastiger Schnappschuss, kollidiert mit Caching, torch im Workflow (A15).
- **1-h-TTL** ohne vorherigen Präfix-Umbau: Abstände passen nicht (A2).
- **Plotly.js**: 1,5 MB gzip (C6).
- **DuckDB-WASM**: bei < 1 MB Daten überdimensioniert (C10).
- **Cerebras als Dauer-Gratisquelle**: nur 30-Tage-Trial mit 5 $ (B5).
- **HF Inference als Gratisquelle**: Free-Nutzer ohne Guthaben (B9, bleibt aber als billige Quelle).
- **Together AI**: kein Gratis-Tier gefunden.
- **Windows-11-Widgets-Board**: Paketierung zu aufwendig (C12d).
