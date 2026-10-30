# Recherche Oktober 2026 – Was macht die KI-Trader-Arena stärker?

Stand: **30.10.2026**. Erstellt in einer automatischen Cloud-Session (Rouven nicht erreichbar). **Es wurde kein Code und kein Workflow der Arena geändert**; dieser Ordner enthält nur Recherche. Die priorisierte Umsetzungsliste steht in [EMPFEHLUNG.md](EMPFEHLUNG.md), alle verworfenen Kandidaten mit Grund in [ANHANG-verworfen.md](ANHANG-verworfen.md). Das Gegenstück für **kostenpflichtige oder anderweitig eingeschränkte** Ideen ist [IDEEN-TRESOR.md](IDEEN-TRESOR.md) (von der parallelen Session). Kleine Test- und Auswerteskripte, auf die sich „getestet“ bezieht, liegen in [skripte/](skripte/).

## 1. Ziel und Filter (Weitblick Schritt 1)

**Ziel:** Alles finden, was die Arena als Werkzeug, Datenquelle, Modell, Bibliothek, Methode oder Verbesserung stärker macht – mit dem Maßstab „misst die Arena danach ehrlicher, handeln die Agenten danach besser, oder wird es billiger?“.

**Harte Filter:**
- kostenlos oder sehr günstig im Betrieb;
- nur legale, öffentliche Quellen, kein Scraping hinter Logins, keine Umgehung von Sperren; Nutzungsbedingungen (auch Weiterverbreitung, da Repo und Seite öffentlich sind) beachten;
- lauffähig in GitHub Actions (Linux-CPU, ~7 GB RAM, 6 h) bzw. später Oracle-Gratis-Server (ARM, 24 GB);
- Lizenz MIT/Apache/BSD bevorzugt, alles andere gekennzeichnet (GPL/AGPL/LGPL, Nicht-kommerziell, „Commons Clause“, keine Lizenzdatei);
- nur Papierhandel; nichts, wofür Rouven belangt werden kann; keine Angriffs-/Recon-Werkzeuge.

## 2. Vorgehen (Weitblick Schritte 2–6)

1. **Breit aufspannen:** acht parallele Recherche-Agenten, je einer pro Kategorie (siehe Inhaltsverzeichnis). Jeder hat zuerst PLAN.md, STATUS.md, DECISIONS.md und die betroffenen Dateien unter `arena/` gelesen und dann GitHub-Suche, Awesome-Listen, arXiv/SSRN, Hugging Face, Papers with Code, Foren (r/algotrading, r/LocalLLaMA, Hacker News, LessWrong) und offizielle Dokus/ToS durchsucht.
2. **Grob bewerten:** Nutzen für die Arena, Aufwand, Kosten, Risiko, Lizenz, Pflegezustand (Sterne, letzter Commit).
3. **Ausdünnen:** Filterverletzer und klar Unterlegenes in den Anhang (mit Grund).
4. **Genau prüfen:** README/Code/ToS gelesen, und wo möglich **in der Sandbox getestet** – rund 120 öffentliche Endpunkte live per `curl` abgefragt (die Sandbox läuft wie GitHub Actions über US-Cloud-IPs, also ein guter Indikator), ~15 Zeitreihenmodelle auf CPU gemessen und gegen den Random Walk verglichen, Risiko-/Signal-Bibliotheken installiert und auf echten BTC/ETH/SOL-Kerzen ausprobiert, Kalibrier-/Bewertungsformeln nachgerechnet.
5. **Empfehlung mit Umstiegspunkten:** siehe [EMPFEHLUNG.md](EMPFEHLUNG.md).

**Statusbegriffe je Fund:**
- **getestet** – selbst ausgeführt (Endpunkt abgefragt, Paket installiert und benutzt, Modell gerechnet);
- **geprüft** – Primärquelle gelesen (README, Code, LICENSE, offizielle Doku/ToS);
- **nur gelesen** – nur Sekundärquelle (Blog, Zusammenfassung, Abstract);
- **ungeprüft** – Angabe nicht bestätigt; nicht darauf verlassen.

Sterne stammen aus der GitHub-Suche am 30.10.2026; bei einigen Einträgen ist „letzter Commit“ das `updated_at`/`pushed_at` des Repos (so im Eintrag vermerkt). Alles ohne Beleg ist als ungeprüft markiert. Pfade „‹Sandbox›/…“ bezeichnen Testdateien der Recherche-Sitzung, die nicht im Repo liegen (die wichtigsten Skripte sind nach `research/skripte/` kopiert).

## 3. Querschnitt: Befunde am bestehenden Code (vor allem anderen lesen)

Während der Recherche sind konkrete Fehler bzw. irreführende Stellen in der laufenden Arena aufgefallen. Ich habe jede davon selbst im Code gegengeprüft; **behoben ist nichts** (Auftrag: keinen Code ändern, und eine andere Session arbeitet parallel an `main`).

| # | Befund | Beleg im Code | Auswirkung | Quelle |
|---|---|---|---|---|
| B1 | **Polymarket-Taker-Gebühr wird nie gebucht.** `pm.py` speichert `feeSchedule.rate` als `ref.gebuehr_rate`, `fees.py` rechnet aber fest mit `polymarket_taker = 0`. | `arena/data/pm.py:60`, `arena/exchange/fees.py:30-31` | Laut Live-Abfrage (30.10.) haben 10 der Top-40-Märkte eine Gebühr (Sport 0,03/0,05, Krypto 0,07); Formel laut Doku `C·rate·p·(1−p)` → bis 3,5 % des Nominals. Die Börse ist dort zu optimistisch; DECISIONS.md behauptet das Gegenteil. | Kat. 5 |
| B2 | **Opus-Wochen-Review wird abgeschnitten.** `max_tokens=8000` inklusive Denken; `reports/2026-W44.md` endet mitten im Satz, der Regel-JSON fehlt → keine Regeln im Notizbuch. | `arena/review.py:58`, `reports/2026-W44.md` (Ende) | Review-Lernschleife wirkt nicht. Abhilfe: Streaming, ~32k Tokens, `stop_reason` prüfen. Ähnliches Risiko bei der neuen Opus-Tiefenrunde (`arena/agent/loop.py:55`, 12k je Schritt) – dort `stop_reason` mitprüfen. | Kat. 8 |
| B3 | **Kronos-Unsicherheitsband ist viel zu eng.** p10/p90 aus nur 8 Einzelpfaden. | `scripts/prognosen.py:56-63` | Im Nachbau exakt wie in der Arena: Bandbreite ~1 % statt ~4,5 % (Random Walk), Abdeckung 0 von 6 statt ~80 %; im 50-Ursprünge-Test Pinball-Loss +50 % gegenüber Random Walk. Agenten bekommen eine falsche Sicherheit gezeigt. | Kat. 3 |
| B4 | **Reddit-`.json` liefert 403**, Rückfall auf RSS funktioniert, setzt aber `zeit = time.time()` statt des echten Zeitstempels (GDELT ebenso). | `arena/data/news.py:49, 56-60, 69` | Nachrichtenalter falsch → „Nachricht zu Position“-Ereignisse und Altersfilter ungenau. | Kat. 7 |
| B5 | **Budget zählt Cache-Lesen zu teuer.** Config: 0,1×; laut offizieller Preisseite (vom Agenten gelesen) für Sonnet/Opus 5.5 0,05×. Außerdem steht der Fondsname früh im System-Prompt → kein Cache-Sharing zwischen den drei Fonds. | `arena/config.json` (`cache_lesen_faktor`), `arena/agent/prompts.py` (`SYSTEM` beginnt mit „DEIN FONDS“) | Budget ~23 % zu hoch gebucht; ~45 % der Sonnet-Kosten sind Cache-Schreiben. Vor Umsetzung Preis nochmals gegenprüfen. | Kat. 8 |
| B6 | **Liga-Konfiguration veraltet (ungeprüft, aber wahrscheinlich):** DeepSeek-Preisseite nennt nur noch `deepseek-flash`/`deepseek-v4-pro` (Config: `deepseek-chat`); Groq `llama-3.3-70b-versatile` nicht mehr in der Limit-Tabelle; Cerebras nur noch 30-Tage-Test; GitHub Models laut GitHub-Doku seit 30.07.2026 eingestellt. | `arena/config.json` (`liga`) | Liga-Fonds mit Fehlerstatus. | Kat. 8 |
| B7 | **Klumpenrisiko hat eine erklärbare Ursache:** gleiches Modell, gleicher Prompt (nur ein Persönlichkeitssatz), gleicher Schnappschuss, gleiche Ereignis-Reihenfolge, gleiche Suche. Literatur (Herding-Paper ICLR 2026, Metaculus FutureEval) zeigt: gleiche Information treibt gleichgerichtete Wetten stärker als die Persona. | `arena/config.json` (`fonds_claude`), `arena/agent/prompts.py` | Drei „unabhängige“ Fonds sind faktisch einer. **Nachtrag 30.10. mittags:** Die parallele Session hat inzwischen je Fonds Schwerpunkt, Recherchepfad, Startliste und die Kennzahl „Überlappung“ eingebaut (siehe STATUS.md, Tagschicht) – das deckt einen Teil von M1/M2 ab; offen bleiben gleiche Ereignis-Reihenfolge, Pflichtfelder und der Schwarm-Ansatz. | Kat. 1, 4 |
| B8 | **Statistik der Rangliste:** Mit 12+ Fonds und wenigen Wochen ist der Erstplatzierte fast sicher Glück (Simulation: bester von 12 Null-Fonds nach 60 Tagen Sharpe 1,15; Deflated-Sharpe-Wahrscheinlichkeit echten Könnens 19 %). | `arena/metrics.py` | Ohne Konfidenzintervalle/Mehrfachtest-Korrektur ist die Liga-Umschaltung am 14.11. ein Münzwurf. | Kat. 2 |

## 4. Wichtigste Erkenntnisse in fünf Sätzen

1. **Kein Zeitreihen-Foundation-Modell schlägt bei BTC-Stundenkursen den Random Walk** (eigener 50-Ursprünge-Test, deckungsgleich mit der Literatur 2025/26); nützlich sind sie höchstens für Volatilität/Risiko – und dort ist GARCH gleich gut und 40× billiger.
2. **Auf liquiden Wettmärkten ist der Marktpreis meist besser als ein LLM allein;** Vorteil entsteht laut AIA Forecaster/ForecastBench erst durch die *Mischung* aus Modell und Markt, durch Ensembles *verschiedener* Modelle und durch Spezialwissen (Wetter, Abrechnungsregeln).
3. **Die Arena braucht mehr unabhängige Stichproben und ehrlichere Kennzahlen,** bevor eine Rangliste etwas bedeutet – marktrelative Brier-Kennzahlen, Konfidenzintervalle und öffentliche Forecasting-Turniere (Metaculus) liefern das.
4. **Die größten billigen Hebel sind Prompt-/Schema-Änderungen** (Denkschulen statt Risikoadjektiv, getrennte Informationsdiät, Pflichtfelder Basisrate/Invalidierung/`p_blind`) und **ein geschlossener Lernkreis** (Reflexion bei Abrechnung, Kalibrier-Rückmeldung).
5. **Neue Gratis-Daten mit echtem Vorteil:** Open-Meteo-Ensembles + NWS-Klimaberichte für Wetter-Wettmärkte, Hyperliquid (Funding/OI/L2 für 225 Perps), Deribit DVOL, Polymarket-Orderfluss (Data-API), SEC EDGAR – alle live getestet.

## Inhaltsverzeichnis

1. LLM-Trading-Agenten, Multi-Agenten-Systeme und kreative Methoden
2. Benchmarks, Evaluation, Schutz vor Lookahead
3. Zeitreihen-Foundation-Modelle und Basislinien
4. Forecasting-Methoden und Wettmarkt-Daten
5. Backtesting/Ausführung, Risiko/Portfolio, Signale/Regime
6. Gratis-Marktdaten: Krypto, Aktien/ETF, Makro
7. Nachrichten/Stimmung, alternative Daten, MCP-Server
8. LLM-Kosten, Gratis-Modelle, Dashboards

Hinweis zum Lesen: Jede Kategorie wurde von einem eigenen Recherche-Agenten erarbeitet und von mir zusammengeführt; Formulierungen sind daher je Kapitel leicht unterschiedlich. Bewertungen 1–5 beziehen sich auf den Nutzen *für diese Arena*, nicht auf die allgemeine Qualität eines Projekts.

---

## 1. LLM-Trading-Agenten, Multi-Agenten-Systeme und kreative Methoden

### Kategorie: LLM-Trading-Agenten-Frameworks, Multi-Agenten-Systeme und kreative Methoden

Prüfdatum aller Angaben: **2026-10-30**. Sterne stammen aus der GitHub-Suche (MCP `search_repositories`) an diesem Tag, „letzter Commit“ und Lizenz aus einem flachen `git clone --depth 1` (Commit-Datum von HEAD auf dem Standardzweig, LICENSE-Datei gelesen). Wo etwas nur aus Papers oder Presseberichten stammt, steht „nur gelesen (Sekundärquelle)“. Alle Klone liegen unter `‹Sandbox›/test-agents/repos` (untrusted, nur gelesen). Zwei Bausteine habe ich isoliert getestet (Python mit `-I`, eigener venv, ohne API-Schlüssel), siehe „getestet“.

**Ausgangslage in der Arena** (gelesen: `arena/agent/prompts.py`, `loop.py`, `tools.py`, `arena/notizbuch.py`, `arena/review.py`, `arena/entscheider.py`, `arena/config.json`, `STATUS.md`, `DECISIONS.md`):
- Ein Agent je Fonds arbeitet in einer einzigen Tool-Use-Schleife („Weitblick“-Prompt: Thesen → Gegenargument → Kosten → Größe → Notizbuch). Es gibt keine getrennte Rolle für Gegenposition oder Risiko. Das Gegenargument prüft dasselbe Modell im selben Kontext.
- Die drei Claude-Fonds unterscheiden sich nur durch einen Satz Persönlichkeit und durch Limits. Sie bekommen dasselbe Modell, denselben Schnappschuss, dieselben Ereignisse in derselben Reihenfolge und dieselbe Websuche. Laut STATUS.md setzten alle drei auf dieselbe Wette (Iran-Waffenruhe).
- Das Gedächtnis (`notizbuch.als_text`) zeigt einfach die letzten 40 Einträge chronologisch. Es gibt kein Ranking, keinen Zerfall und keine Lektion, die automatisch aus abgerechneten Positionen entsteht.
- Der Brier-Score wird gemessen, fließt aber nicht als Korrektur zurück (keine Rekalibrierung, kein „Haircut“).
- Das Order-Schema hat `begruendung`, `zuversicht`, `ausstiegsplan` und `wahrscheinlichkeit_ja`. Felder für Invalidierungsbedingung, stärkstes Gegenargument oder Basisrate fehlen.
- Das Wochen-Review (Opus) schreibt bis zu 3 Regeln je Fonds ins Notizbuch. Das ist schon eine Form von „Conceptual Verbal Reinforcement“ im Sinn von FinCon.

---

#### TauricResearch/TradingAgents
- Link: https://github.com/TauricResearch/TradingAgents | Paper https://arxiv.org/abs/2412.20138 | Lizenz: Apache-2.0 (LICENSE gelesen) | Sterne/letzter Commit: 118.501 / 2026-10-27
- Was es kann: Ein LangGraph-Graph bildet eine Handelsfirma nach. Vier Analysten (Markt, Stimmung, News, Fundamentaldaten) liefern Berichte, dann folgt eine Bull/Bear-Debatte zwischen Researchern (`max_debate_rounds`, Standard 1). Ein Research Manager schreibt den Investmentplan, der Trader macht daraus einen Vorschlag. Danach debattiert ein Risiko-Trio (aggressiv/konservativ/neutral, `max_risk_discuss_rounds`, Standard 1), und am Ende entscheidet ein **Portfolio Manager** mit einer strukturierten Ausgabe (Rating Buy/Overweight/Hold/Underweight/Sell). Neu: `memory/reflection.py` und `memory/settlement.py`. Abgerechnete Entscheidungen werden gegen eine Benchmark (SPY) als Alpha bewertet, und ein schnelles LLM schreibt **2–4 Sätze Lektion**, die späteren Läufen wieder vorgelegt wird. Es gibt sogar einen Polymarket-Datenlieferanten (Gamma-API, nur lesend).
- Nutzen für die Arena (konkret):
  1. **Reflexion nach Abrechnung**: Der Reflector-Prompt lässt sich fast wörtlich übernehmen. Er nennt das Ergebnisfenster ausdrücklich („Fenster kann kürzer sein als der Horizont der These, dann sag das“), verlangt Bezug auf die Zahl, fragt, welcher Teil der These gestützt oder widerlegt wurde, und genau eine Lektion. In der Arena würde ihn ein neuer Hook auslösen, wenn `exchange` eine Position schließt oder ein Markt abgerechnet wird: Haiku schreibt dann `notizbuch.schreibe(fid, "lektion", …)` mit Rendite gegen BTC- oder SPY-Vergleichsfonds.
  2. **Portfolio-Manager-Regel gegen das „Hold aus Feigheit“**: „Konflikt allein ist kein Grund für Hold; entscheide dich für die stärkere Seite, Größe danach, wie deutlich sie gewinnt. Hold nur, wenn die Evidenz nach Abwägung ausgeglichen oder zu dünn ist.“ Das passt gut als Ergänzung zu Schritt 6 in `prompts.SYSTEM`.
  3. Die Prompts für das Risiko-Trio sind eine gute Vorlage für einen einzelnen **Risikomanager-Pass vor der Order** (siehe Muster).
- Aufwand: gering für die Reflexion (ein Haiku-Aufruf je abgerechneter Position, Hook in der Abrechnung). Das ganze Framework zu übernehmen wäre hoch (LangGraph, viele Aufrufe je Ticker, aktienzentriert) und widerspräche dem harten Budget.
- Bewertung: 5/5 als Musterquelle, 1/5 als einzubauendes Framework
- Status: geprüft (README/Code gelesen: `bull_researcher.py`, `conservative_debator.py`, `portfolio_manager.py`, `memory/reflection.py`, `memory/settlement.py`, `default_config.py`)

#### hsliuping/TradingAgents-CN
- Link: https://github.com/hsliuping/TradingAgents-CN | Lizenz: **gemischt**. Apache-2.0 für `tradingagents/`, `cli/`, `docs/`, `tests/`, `web/`, dazu **proprietäre „Source Available“-Teile** (LICENSE gelesen) | Sterne/letzter Commit: 32.717 / 2026-09-22
- Was es kann: Chinesische Erweiterung von TradingAgents (A-Aktien, Weboberfläche, mehr Datenquellen).
- Nutzen für die Arena: Keiner über das Original hinaus, die Muster sind dieselben.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (LICENSE gelesen) → verworfen

#### virattt/ai-hedge-fund
- Link: https://github.com/virattt/ai-hedge-fund | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 64.361 / 2026-10-27
- Was es kann: Inzwischen eine TUI-App (`aihf`) mit Papierhandel und Backtest. **Investoren-Personas** (Buffett, Munger, Graham, Lynch, Druckenmiller) sind jeweils *nur ein System-Prompt* auf einer gemeinsamen `LLMAgent`-Maschine, jede mit eigenem `horizon_days` und eigenem `investment_approach` (long_only/long_short). Signale werden je Strategie gewichtet gemischt, und `risk/limits.py` skaliert Zielgewichte nur proportional *herunter* (max. Position, Brutto-Exposure). Dazu kommt ein **Blind-Modus**: Ticker, Branche, Daten und Dollarwerte werden aus dem Prompt entfernt, damit das Modell im Backtest nicht auf Trainingswissen zurückgreift.
- Nutzen für die Arena:
  1. **Personas mit echter Denkschule statt Risikoadjektiv**: Der Druckenmiller-Prompt ist ein gutes Vorbild. Er beschreibt in 5 Punkten, *wie* gedacht wird (Wendepunkt, eingepreiste Erwartung, Asymmetrie, „wenn das Setup durchschnittlich ist, ist die richtige Position keine“), gibt eine Skala für die Zuversicht (90–100 / 70–89 / 40–69 / 10–39) und harte Regeln („keine Zahlen erfinden“). Die drei `persoenlichkeit`-Sätze in `config.json` sollten so zu echten Denkschulen ausgebaut werden. Das ist das stärkste Mittel gegen gleiche Wetten (siehe Muster).
  2. **Skala für Zuversicht**: Die Arena verlangt `zuversicht` 0..1 ohne Anker. Mit einer Ankerskala im Tool-Schema werden die Zahlen über die Modelle hinweg vergleichbarer, auch für die Liga.
  3. Blind-Modus: für die Arena (Vorwärtstest) nicht nötig. Er wäre aber nützlich für ein Opus-Review „ohne Namen“ (Fondsnamen und Modell ausblenden, damit das Urteil nicht vom Ruf abhängt).
- Aufwand: gering (nur Prompt und Konfiguration)
- Bewertung: 4/5
- Status: geprüft (README, `signals/druckenmiller.py`, `signals/llm_agent.py`, `risk/limits.py` gelesen)

#### FinMem (pipiku915/FinMem-LLM-StockTrading)
- Link: https://github.com/pipiku915/FinMem-LLM-StockTrading | Paper https://arxiv.org/abs/2311.13743 | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 968 / 2024-08-17 (inaktiv)
- Was es kann: **Geschichtetes Gedächtnis** (kurz/mittel/lang/reflexiv), jede Schicht mit eigenem Zerfall. In der Konfiguration z. B. `recency_factor` 3 / 90 / 365 Tage und `importance_factor` 0,92 / 0,967 / 0,988. Einträge mit hoher Wichtigkeit springen eine Schicht höher (`jump_threshold_upper`), Einträge unter einer Schwelle werden gelöscht (`clean_up_threshold`). Abgerufen wird nach Aktualität × Relevanz × Wichtigkeit. Dazu kommt ein **dynamischer Charakter**: Ist die kumulierte Rendite ≥ 0, ist der Agent risikofreudig, sonst risikoscheu (`puppy/prompts.py`).
- Nutzen für die Arena: Das Notizbuch ist bisher „letzte 40 Einträge“. Übernehmbar ohne Embeddings: Jeder Eintrag bekommt `wichtigkeit` (1–10, vom Agenten beim Schreiben gesetzt) und `schicht` (Typ `regel`/`lektion` = lang, `these` = mittel, `beobachtung` = kurz). `als_text` sortiert dann nach `wichtigkeit × exp(-alter/τ_schicht)` und zeigt z. B. 10 Regeln, 15 Lektionen, 10 Thesen und 5 Beobachtungen. Relevanz kann man billig über Stichwortüberlappung mit den Ereignistiteln oder offenen Instrument-IDs berechnen. Lektionen gehen so nicht mehr unter, wenn viele Beobachtungen geschrieben werden. Den Charakterwechsel nach Rendite würde ich *nicht* übernehmen, er verwischt die Risikoprofile, die die Arena vergleichen will.
- Aufwand: gering bis mittel (Änderung in `notizbuch.py` und am Tool-Schema `notizbuch_schreiben`)
- Bewertung: 4/5
- Status: geprüft (Konfiguration und `prompts.py` gelesen)

#### TradingGPT (Paper)
- Link: https://arxiv.org/abs/2309.03736 | Lizenz: Paper (kein Code geprüft) | Sterne/letzter Commit: ungeprüft
- Was es kann: Vorläufer von FinMem. Mehrere Agenten mit geschichtetem Gedächtnis und **unterschiedlichen Charakteren** (risikofreudig, neutral, risikoscheu), die vor der Entscheidung debattieren.
- Nutzen für die Arena: Bestätigt die Idee „verschiedene Charaktere statt Klone“. Konkretes steckt schon in FinMem.
- Aufwand: –
- Bewertung: 2/5
- Status: nur gelesen (Sekundärquelle: Abstract und Zusammenfassungen)

#### FinCon (The-FinAI/FinCon)
- Link: https://github.com/The-FinAI/FinCon | Paper https://arxiv.org/abs/2407.06567 (NeurIPS 2024) | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 70 / 2026-10-08
- Was es kann (laut Paper): Hierarchie aus Manager und Analysten. Ein Risikokontroll-Bestandteil startet **episodisch eine Selbstkritik** und destilliert aus GuV-Verläufen „Investment-Überzeugungen“ (Conceptual Verbal Reinforcement), die *gezielt nur an die Agenten weitergegeben werden, die sie brauchen*. **Der Code ist laut README nicht veröffentlicht** („release within the next 3–4 months“), das Repo enthält nur README und LICENSE.
- Nutzen für die Arena: Das Wochen-Review (`review.py`) setzt dieses Muster schon um (Regeln je Fonds ins Notizbuch). Daraus übernehmbar: Überzeugungen **mit Ablaufdatum und Beleg** (Fonds-ID, Zeitraum, GuV) speichern und beim nächsten Review prüfen lassen, ob die Regel gehalten oder geschadet hat. Sonst wachsen die Regeln nur an.
- Aufwand: gering (Prompt in `review.py` und Felder im Notizbuch)
- Bewertung: 3/5
- Status: geprüft (Repo gelesen, Code fehlt), Methode nur gelesen (Sekundärquelle)

#### FinAgent (Paper, Zhang et al.)
- Link: https://arxiv.org/abs/2402.18485 | Lizenz: Paper (Code ungeprüft) | Sterne/letzter Commit: ungeprüft
- Was es kann: Multimodaler Agent (Kurse, Chartbilder, News, Experten), **zweistufige Reflexion** (Low-Level: Was sagten die Preisbewegungen? High-Level: Waren frühere Entscheidungen richtig?) und diversifizierter Gedächtnisabruf, getrennt von der Handelsaufgabe.
- Nutzen für die Arena: Die zweistufige Reflexion ist ein gutes Prompt-Muster für das Ende einer Runde. Die Kursbilder (Vision) braucht man nicht. Die Prognosewerkzeuge (TimesFM, Kronos) decken das numerisch ab.
- Aufwand: gering (Prompt)
- Bewertung: 2/5
- Status: nur gelesen (Sekundärquelle)

#### AI4Finance-Foundation/FinRobot
- Link: https://github.com/AI4Finance-Foundation/FinRobot | Lizenz: Apache-2.0 (LICENSE gelesen) | Sterne/letzter Commit: 8.336 / 2026-10-24
- Was es kann: Drei Generationen: V0 AutoGen (Lernversion), V1 OpenAI Agents SDK (Aktienanalyse als Web-App), V2 PydanticAI-Desktop-Arbeitsplatz für Aktienresearch. Leitsatz: „**models reason, software computes, agents orchestrate, systems verify**“, d. h. alle Finanzzahlen (DCF, WACC …) rechnet reiner Python-Code, das LLM begründet nur.
- Nutzen für die Arena: Der Leitsatz bestätigt das Design der Arena (die Börse rechnet deterministisch). Konkret übernehmbar: Werkzeuge, die dem Agenten **Rechenarbeit abnehmen**, z. B. ein Tool `erwartungswert` (P(JA), Preis, Gebühr, Spread → EV nach Kosten, Kelly-Bruchteil). Sonst rechnet das LLM die Rundreisekosten im Kopf. Das Framework selbst ist auf Aktienresearch und Berichte ausgerichtet und für die Arena zu schwer.
- Aufwand: gering (ein Werkzeug), hoch (Framework)
- Bewertung: 2/5
- Status: geprüft (README gelesen)

#### AI4Finance-Foundation/FinGPT
- Link: https://github.com/AI4Finance-Foundation/FinGPT | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 21.489 / 2026-10-25
- Was es kann: Feinabgestimmte Finanz-LLMs (LoRA) für Sentiment, NER und Prognosen sowie Datensätze.
- Nutzen für die Arena: Gering. Allenfalls ein lokales Sentiment-Modell auf dem Oracle-ARM-Rechner. Für die Arena zählen aber die Entscheidungen der großen Modelle, nicht Klassifikationen. Ein Fine-Tuning braucht GPU.
- Aufwand: hoch
- Bewertung: 1/5
- Status: geprüft (Repo-Metadaten und LICENSE)

#### HKUDS/AI-Trader
- Link: https://github.com/HKUDS/AI-Trader | Lizenz: MIT laut README-Badge, **im Repo-Wurzelverzeichnis aber keine LICENSE-Datei** (geprüft) | Sterne/letzter Commit: 23.036 / 2026-06-11
- Was es kann: Hat sich von einem LLM-Benchmark zu einer **Plattform** (ai4trade.ai) entwickelt. Agenten registrieren sich über eine SKILL.md, veröffentlichen Signale, kopieren Trades und handeln Polymarket auf Papier mit automatischer Abrechnung. Im Ordner `research/` liegt eine Pipeline für eine Studie über Wettbewerb und Kooperation mit mehr als 4.000 Agenten.
- Nutzen für die Arena: Die Plattform ist ein externer Dienst (Daten gehen raus, Login und Registrierung) und damit unpassend. Brauchbar ist das Skill-Muster „Polymarket direkt über Gamma und CLOB lesen, Plattform nur zur Ausführung“. Das macht die Arena schon. Die Forschungs-Exporte (anonymisierte Agenten-Hashes, `--public-structure-only` ersetzt Freitext durch Hashes) sind eine gute Vorlage, falls die Arena ihre `decisions.jsonl` als Datensatz veröffentlicht.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (README, `skills/polymarket/SKILL.md`, `research/README.md` gelesen)

#### nof1 Alpha Arena (Methodik) + nof0 (Community-Rekonstruktion)
- Link: https://nof1.ai (Original-Blogbeitrag per WebFetch nicht erreichbar, 404; Kopie unter https://dyor.pages.dev/blog/TechPost1 ebenfalls 404) | Berichte: https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/ , https://www.thinkadvisor.com/amp/2026/05/06/why-ai-bots-arent-ready-to-replace-your-fund-manager/ | nof0: https://github.com/nof0-ai/nof0 (Lizenz: **keine LICENSE-Datei**, letzter Commit 2025-12-07, Sterne ungeprüft)
- Was es kann: Staffel 1 (17.10.–3.11.2025) gab 6 LLMs je 10.000 $ für Krypto-Perps auf Hyperliquid, mit gleichem Prompt, gleichen Daten und Standard-Sampling. Laut Berichten machten 4 von 6 Verlust, es wurde stark übertradet (ein Bericht nennt 1.418 Trades bei Qwen gegenüber 158 bei Grok), es gab Richtungs-Bias (einige Modelle shorteten bevorzugt, Claude Sonnet 4.5 kaum), und die Modelle hatten kein Gedächtnis früherer Aktionen. Der Gründer sagt, man brauche „a very sophisticated harness and scaffolding“. nof0 enthält einen **rekonstruierten** System-Prompt (ausdrücklich „inferred“, nicht offiziell) mit Pflichtfeldern je Trade: `invalidation_condition` („konkretes Marktsignal, das die These ungültig macht“), `confidence` mit Ankerskala, `risk_usd` und eine Prüfung „Check for invalidation conditions on existing trades“ zu Beginn jeder Runde.
- Nutzen für die Arena:
  1. Bestätigt die Methodik der Arena (gleicher Prompt und gleiche Werkzeuge für alle Modelle, öffentliche Entscheidungen) und das Thema Übertrading. Die Arena hat schon Triage und „Nichtstun ist gültig“. Eine **Kennzahl „Trades je Woche“ und „Kosten in % des Kapitals“** in Rangliste und Review wäre trotzdem sinnvoll.
  2. **Invalidierungsbedingung als Pflichtfeld** in `t_order` (zusätzlich zu `ausstiegsplan`): ein überprüfbarer Satz, der in `portfolio()` mit ausgegeben wird, damit Schritt 1 („passt die Position noch zur These?“) gegen etwas Konkretes prüft. `risk_usd` (Verlust bis zum Stop) als Pflichtangabe zwingt zum Rechnen.
  3. Der Richtungs-Bias je Modell ist auch in der Liga zu erwarten → Kennzahl „Anteil Long/Short/JA/NEIN“ je Fonds auf der Seite.
- Aufwand: gering
- Bewertung: 4/5 (Methodik und Lehren), nof0 selbst 1/5 (ohne Lizenz, nur Ideen)
- Status: nur gelesen (Sekundärquellen), nof0-Prompt-Dateien geprüft (`gitbook/prompt/system-prompt.md`)

#### HKUSTDial/DeepFund
- Link: https://github.com/HKUSTDial/DeepFund | Paper „Time Travel is Cheating“ https://arxiv.org/abs/2505.11065 (NeurIPS 2025) | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 303 / 2026-03-18
- Was es kann: Live-Benchmark mit nur Daten nach dem Trainings-Cutoff. Ein **Planner-Agent** wählt je Ticker aus, *welche* Analysten (Fundamental, Technik, Policy, News …) überhaupt laufen (`agents/planner.py`, strukturierte Ausgabe `analysts` + `justification`). Danach entscheidet ein Portfolio-Manager. Ergebnis im Paper: Auch Spitzenmodelle machten live netto Verlust.
- Nutzen für die Arena: Das Planner-Muster passt zur Haiku-Triage. Statt nur „wecken ja/nein“ könnte die Triage **einen Rechercheplan** liefern („prüfe: Kalshi-Regeln Markt X, Nachrichten Y, Orderbuch Z“). Das wird in `runde_prompt` eingefügt, spart Sonnet-Schritte und lenkt jeden Fonds in andere Richtungen (Diversität). Das Paper ist zudem ein Beleg für die Vorwärtstest-Haltung der Arena.
- Aufwand: gering (TRIAGE-Prompt und JSON-Feld erweitern)
- Bewertung: 3/5
- Status: geprüft (Repo-Struktur, `planner.py` gelesen), Paper nur gelesen (Sekundärquelle)

#### Agent Market Arena (Paper)
- Link: https://arxiv.org/abs/2510.11695 | Lizenz/Sterne: ungeprüft
- Was es kann: Dauerhafter Live-Benchmark über mehrere Märkte (Krypto, Aktien) mit vier Agent-Designs (InvestorAgent, TradeAgent, HedgeFundAgent, DeepFundAgent). Zentrale Aussage laut Abstract: **Das Agent-Design prägt die Ergebnisse stärker als das zugrunde liegende Modell.**
- Nutzen für die Arena: Wichtig für die Auswertung. Die Liga vergleicht Modelle bei gleichem Design. Ein zweiter Vergleich „gleiches Modell, anderes Design“ (z. B. Claude Mittel mit und ohne Risikomanager-Pass) wäre aussagekräftiger. Das spricht für einen A/B-Fonds.
- Aufwand: mittel (zusätzlicher Fonds, Budget)
- Bewertung: 3/5
- Status: nur gelesen (Sekundärquelle)

#### LiveTradeBench (ulab-uiuc/live-trade-bench)
- Link: https://github.com/ulab-uiuc/live-trade-bench | Paper https://arxiv.org/abs/2511.03628 | Lizenz: **PolyForm Noncommercial 1.0.0** (LICENSE gelesen; ältere PyPI-Version sagte MIT) | Sterne/letzter Commit: 167 / 2025-11-21
- Was es kann: Live-Bewertung von 21 LLMs über 50 Tage auf US-Aktien **und Polymarket**, als Portfolio-Allokation. Befund laut Abstract: Hohe LMArena-Werte bedeuten keine besseren Handelsergebnisse.
- Nutzen für die Arena: Nah verwandt (Polymarket plus Aktien plus Liga). Den Code wegen NC-Lizenz nicht übernehmen. Die Idee „Allokationsvektor statt Einzelorders“ ist eine denkbare zweite Liga-Variante, die billiger und robuster für schwache freie Modelle wäre.
- Aufwand: –
- Bewertung: 2/5 (Lizenz)
- Status: geprüft (LICENSE), Paper nur gelesen

#### Prophet Arena (Paper, UChicago SIGMA Lab)
- Link: https://arxiv.org/abs/2510.17638 (ICLR 2026) | Projektseite prophetarena.co | Lizenz/Sterne: ungeprüft (kein Repo gefunden)
- Was es kann: Live-Benchmark auf **Kalshi**-Ereignissen mit über 1.300 abgerechneten Ereignissen. Ablauf: Ereignisse filtern (Beliebtheit, Vielfalt, Wiederkehr) → Kontext bauen → Wahrscheinlichkeit. Befund laut Abstract: kleine Kalibrierungsfehler, aber **ungenaue Erinnerung an Ereignisse, Missverständnisse der Datenquellen (Abrechnungsquelle!) und langsamere Informationsverarbeitung als der Markt**.
- Nutzen für die Arena: Direkt relevant für die Wettmarkt-Fonds. Die genannten Schwächen rechtfertigen eine Pflicht im Prompt: „Nenne die **Abrechnungsquelle** und das **Abrechnungsdatum** aus `markt_details`, bevor du eine Wahrscheinlichkeit abgibst.“ Das ließe sich als Pflichtfeld im Tool `wahrscheinlichkeit` umsetzen.
- Aufwand: gering
- Bewertung: 3/5
- Status: nur gelesen (Sekundärquelle)

#### Y-Research-SBU/QuantAgent („QuantHarness“)
- Link: https://github.com/Y-Research-SBU/QuantAgent | Paper https://arxiv.org/abs/2509.09995 | Lizenz: MIT (LICENSE gelesen) | Sterne: ungeprüft | letzter Commit: 2026-08-18
- Was es kann: LangGraph mit vier Agenten (Indikator, Muster, Trend, Entscheidung) für Hochfrequenz-Kerzen. Muster und Trend werden über **Chartbilder** von einem Vision-LLM erkannt.
- Nutzen für die Arena: Gering. Die Arena hat 15-Minuten-Takt und Prognosemodelle. Vision-Aufrufe je Runde wären teuer und bringen wenig. Höchstens als Muster: ein Werkzeug `indikatoren` (RSI, MACD, Bollinger, deterministisch berechnet), damit Liga-Modelle nicht aus rohen Kursen schätzen.
- Aufwand: gering (Indikator-Tool), hoch (Vision)
- Bewertung: 1/5
- Status: geprüft (README gelesen)

#### FinStep-AI/ContestTrade
- Link: https://github.com/FinStep-AI/ContestTrade | Paper https://arxiv.org/abs/2508.00554 | Lizenz: Apache-2.0 (LICENSE gelesen) | Sterne/letzter Commit: 680 / 2025-12-22
- Was es kann: **Interner Wettbewerb**: Mehrere Daten-Agenten und mehrere Research-Agenten mit je einer eigenen „Trading-Überzeugung“ (`config/belief_list.json`, z. B. aggressive Event-Arbitrage gegen defensive Dividenden-Events) liefern parallel Signale. Ein Bewertungsteil (`research_signal_judger.py`) bewertet die Signale, `research_predictor.py` schätzt aus der Signalhistorie die erwartete Sharpe-Ratio je Agent, und `research_weight_optimizer.py` verteilt die Gewichte danach. Nur die besten Signale fließen ins Portfolio.
- Nutzen für die Arena: Das ist das Muster „**Meta-Agent gewichtet Modelle nach Leistung**“. In der Arena gibt es schon viele unabhängige Signalquellen (3 Claude-Fonds plus Liga, alle mit `wahrscheinlichkeit_ja` und Orders). Ein **Meta-Fonds ohne eigene Recherche** würde nach jedem Entscheiderlauf die festgehaltenen Wahrscheinlichkeiten aller Fonds zu einem Wettmarkt nehmen, nach dem bisherigen Brier-Score je Fonds gewichten (oder zuerst einfach den getrimmten Mittelwert bilden) und nur handeln, wenn die Abweichung vom Marktpreis die Rundreisekosten deutlich übersteigt. Das kostet kein LLM-Token und misst direkt, ob die „Weisheit der Arena“ den Einzelfonds schlägt. Das passt zum Ziel des Projekts.
- Aufwand: mittel (neuer Fondstyp in `funds.py`/`entscheider.py`, eine deterministische Funktion, Gewichte aus `metrics.py`)
- Bewertung: 5/5 (als Idee), 2/5 (Code: A-Aktien, AKShare)
- Status: geprüft (README, `belief_list.json`, Struktur von `contest/researcher/*` gelesen)

#### TradExpert (Paper)
- Link: https://arxiv.org/abs/2411.00782 | Lizenz/Sterne: ungeprüft
- Was es kann: Mixture of Experts aus 4 spezialisierten LLMs (News, Marktdaten, Alpha-Faktoren, Fundamentaldaten) und einem General Expert, der zusammenfasst. Laut Ablation tragen Markt- und News-Experte am meisten bei. Die berichteten Kennzahlen (Sharpe 5,01) sind Backtests und kaum glaubwürdig übertragbar.
- Nutzen für die Arena: Schwach. Bestätigt höchstens, dass News und Marktdaten die wichtigsten Quellen sind. Für fein abgestimmte Experten fehlt der Rahmen.
- Aufwand: hoch
- Bewertung: 1/5
- Status: nur gelesen (Sekundärquelle)

#### MarketSenseAI 2.0 (Paper)
- Link: https://arxiv.org/abs/2502.00415 | Lizenz/Sterne: ungeprüft (kein offizielles Repo gefunden)
- Was es kann: LLM-Agenten mit RAG über SEC-Filings, Earnings Calls und Makroberichten (HyDE-Abruf, semantisches Chunking). Backtest auf S&P 100 mit 125,9 % gegenüber 73,5 % (Angabe der Autoren, nicht repliziert).
- Nutzen für die Arena: Gering. Die Arena handelt Aktien nur am Rand. HyDE (erst eine hypothetische Antwort schreiben, dann damit suchen) ist allerdings als **Suchstrategie-Hinweis** im Prompt nützlich: „Formuliere vor der Websuche, wie eine Meldung aussähe, die deine These widerlegt, und suche genau danach.“
- Aufwand: gering (ein Satz im Prompt)
- Bewertung: 2/5
- Status: nur gelesen (Sekundärquelle)

#### Metaculus/forecasting-tools
- Link: https://github.com/Metaculus/forecasting-tools | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 87 / 2026-10-27
- Was es kann: Framework für KI-Prognose-Bots. Für die Arena besonders wichtig ist `calibration_adjustment/`: **Rekalibrierer** (konstante Verschiebung, Stufen, Entscheidungsbaum, K-Means und **logistische Platt-Rekalibrierung**). `LogisticRecalibrationAdjuster` schätzt aus vergangenen (p, Ausgang)-Paaren zwei verständliche Zahlen: **BIA** (systematische Überschätzung von JA) und **CON** (>1 heißt überkonfident) und korrigiert damit neue Prognosen. Dazu kommen `ai_congress_v2` (Mitglieder mit ausgearbeiteten Profilen, also Persona-Vielfalt) und `base_rates/` (Recherche von Basisraten).
- Nutzen für die Arena:
  1. Die **Brier-Daten der Arena** (Werkzeug `wahrscheinlichkeit`, Abrechnung) passen genau in diese Form. Nach ≥10–30 abgerechneten Schätzungen je Fonds BIA und CON berechnen und **dem Agenten als Feedback in den Rundenprompt geben** („Deine bisherigen JA-Schätzungen waren im Schnitt zu hoch, BIA +0,4; du bist überkonfident, CON 1,5“). Für den Meta-Fonds die Schätzungen vor dem Mitteln rekalibrieren.
  2. Den Code nicht übernehmen (sklearn als Abhängigkeit). Die Formel ist eine logistische Regression in 1 Variable und lässt sich in ~20 Zeilen ohne sklearn nachbauen, z. B. mit Newton-Verfahren.
- Aufwand: gering (Kennzahl in `metrics.py` plus eine Zeile im Rundenprompt)
- Bewertung: 5/5
- Status: **getestet**. `LogisticRecalibrationAdjuster` habe ich isoliert mit synthetischen Daten laufen lassen (400 Fragen, simulierter Agent überkonfident und JA-lastig). Ergebnis BIA=0,591, CON=1,538 (richtig als überkonfident und JA-lastig erkannt). Brier roh 0,1767 → rekalibriert 0,1660 (wahre Wahrscheinlichkeiten 0,1668). Achtung: das ist innerhalb der Stichprobe gemessen. Skript: `‹Sandbox›/test-agents/scripts/test_recal.py`

#### Metaculus/metac-bot-template
- Link: https://github.com/Metaculus/metac-bot-template | Lizenz: **keine LICENSE-Datei im Repo** (geprüft) → Text nicht kopieren, nur die Idee nutzen | Sterne/letzter Commit: 67 (392 Forks) / 2026-10-27
- Was es kann: Vorlage für Metaculus-Turnier-Bots. Je Frage erst Recherche, dann **5 unabhängige Prognosen je Recherchebericht** (`predictions_per_research_report=5`), die aggregiert werden. Vor der Zahl muss der Bot schreiben: (a) Zeit bis zur Auflösung, (b) **Status-quo-Ausgang, wenn sich nichts ändert**, (c) **ein Szenario für einen unerwarteten Ausgang**. Leitsätze: „Gute Prognostiker gewichten den Status quo stärker, weil die Welt sich meist langsam ändert“ und „lassen etwas Wahrscheinlichkeit für Unerwartetes“.
- Nutzen für die Arena: Ein bewährtes Prompt-Gerüst für Wettmärkte, das direkt in `prompts.SYSTEM` (Schritt 2/3) und in die Beschreibung des Werkzeugs `wahrscheinlichkeit` passt. Pflichtfelder: `zeit_bis_aufloesung`, `status_quo`, `ueberraschungsszenario`, `basisrate`. Diese Felder kosten fast nichts und erzwingen die Prüfung, die beim Iran-Waffenruhe-Klumpen vermutlich fehlte.
- Aufwand: gering
- Bewertung: 5/5 (Idee), Lizenz ungeklärt (eigene Formulierung verwenden)
- Status: geprüft (`main.py` gelesen)

#### Halawi et al. „Approaching Human-Level Forecasting with Language Models“ (Paper)
- Link: https://arxiv.org/abs/2402.18563 (NeurIPS 2024) | Lizenz: Paper CC BY 4.0 (laut arXiv-HTML-Seite) | Code ungeprüft
- Was es kann: Drei Stufen. (1) Abruf: Das LM schreibt Suchanfragen, bewertet die Relevanz der Artikel und fasst sie zusammen. (2) Begründung: mehrere Prognosen mit Begründung. (3) **Aggregation über getrimmten Mittelwert**. Das System kommt nahe an die menschliche Crowd heran (Crowd-Brier 0,149). Retrieval und Fine-Tuning bringen den größten Gewinn.
- Nutzen für die Arena: Der getrimmte Mittelwert ist die passende Aggregation für den Meta-Fonds und für ein Schwarm-Werkzeug (siehe Muster). „Relevanz bewerten, dann zusammenfassen“ ist ein Muster für das Werkzeug `nachrichten`. Bisher kommen ungefilterte Treffer an, die Kontext und Kosten verbrauchen.
- Aufwand: gering bis mittel
- Bewertung: 4/5
- Status: nur gelesen (Sekundärquelle)

#### „Wisdom of the Silicon Crowd“ (Paper, Schoenegger/Tetlock)
- Link: https://arxiv.org/abs/2402.19379 (Science Advances 2024) | Lizenz/Sterne: –
- Was es kann: Ein Ensemble aus 12 LLMs war bei 31 Binärfragen statistisch nicht von 925 Menschen zu unterscheiden. Einzelmodelle sind schwächer als das Aggregat. Die Modelle zeigen einen **Acquiescence-Bias** (Mittel über 50 %, obwohl weniger als die Hälfte mit JA endete). Den Median der Menschen zu zeigen verbessert GPT-4 und Claude 2 um 17–28 %, einfaches Mitteln von Mensch und Maschine war aber noch besser.
- Nutzen für die Arena: Die Arena *hat* einen Schwarm aus Gemini, DeepSeek, Kimi, Mistral, Cerebras, OpenRouter free und Claude. Das ist die Begründung für den Meta-Fonds und für ein Werkzeug „Schwarmschätzung“. Der JA-Bias spricht für die BIA-Korrektur (forecasting-tools). Daraus folgt auch: Den **Marktpreis** als „Crowd“ zeigen und dann *mitteln*, statt das Modell nur „anpassen“ zu lassen.
- Aufwand: gering bis mittel
- Bewertung: 4/5
- Status: nur gelesen (Sekundärquelle)

#### AIA Forecaster (Bridgewater AIA Labs, Technischer Bericht)
- Link: https://arxiv.org/abs/2511.07678 | Lizenz/Sterne: – (kein Code)
- Was es kann: Agentische Nachrichtensuche, **mehrere unabhängige Läufe**, ein **Supervisor-Agent**, der Abweichungen *mit zusätzlicher Recherche* auflöst (statt einfach zu mitteln), und statistische Kalibrierung (Platt). Erreicht auf ForecastBench Superforecaster-Niveau, liegt auf liquiden Wettmärkten aber *hinter dem Marktkonsens*. **Ein Mix aus System und Konsens schlägt den Konsens allein.** Kalibrierung hilft nur, wenn die Rohschätzung schon auf der richtigen Seite von 0,5 liegt.
- Nutzen für die Arena: Sehr wichtig für ehrliche Erwartungen. Liquide Polymarket- und Kalshi-Märkte schlägt ein LLM allein kaum. Ein Vorteil entsteht eher (a) in illiquiden oder neuen Märkten, (b) durch Mischen mit dem Marktpreis, (c) durch Kreuz-Plattform-Abweichungen (die Arena erzeugt schon Ereignisse „Fehlbewertung“). Daraus folgt eine Prompt-Regel: „Deine Handelswahrscheinlichkeit = Mischung aus deiner Schätzung und dem Marktpreis. Weiche nur deutlich ab, wenn du eine konkrete Informationsquelle nennst, die der Markt noch nicht verarbeitet hat.“ Der Supervisor entspricht dem Meta-Fonds mit einem einzigen „Schlichter“-Aufruf bei großer Uneinigkeit.
- Aufwand: gering (Prompt), mittel (Supervisor)
- Bewertung: 5/5
- Status: nur gelesen (Sekundärquelle)

#### ryanfrigo/kalshi-ai-trading-bot („honest edge layer“)
- Link: https://github.com/ryanfrigo/kalshi-ai-trading-bot | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 637 / 2026-10-02
- Was es kann: Hat sich vom Handelsbot zur **Ehrlichkeitsschicht** entwickelt. Laut README gibt es ausdrücklich *kein* 5-Modell-Ensemble (die Debatten-Agenten sind nicht eingebaut). `src/agent/edge.py` ist rein deterministisch: Brier, Log-Loss, Kalibrierungstabelle, **Edge-vs-Book** (realisierte Trefferquote minus mittlerer bezahlter Preis = implizite Wahrscheinlichkeit, je Kategorie und Seite), **forward_only** (nur Trades, die vor der Abrechnung geschlossen wurden) und ein Urteil mit Mindest-n. `learnings.py` plus Policy-Regeln: **Block** (Kategorie mit ≥5 abgerechneten Trades und negativer GuV wird gesperrt), **Seiten-Warnung**, **Haircut** (Wahrscheinlichkeitsband, in dem man ≥10 pp überkonfident ist, wird auf die echte Trefferquote gestutzt). Grundsatz: „Eine Gruppe mit <5 Trades bekommt keine Meinung“, die Policy wird nur verschärft.
- Nutzen für die Arena:
  1. **Edge-vs-Book** als Kennzahl je Fonds auf der Seite, zusätzlich zum Brier. Brier allein sagt nicht, ob man den *Markt* geschlagen hat. Edge-vs-Book sagt das direkt.
  2. Den **geschlossenen Kreislauf** „abrechnen → messen → Regel ableiten → nächste Order prüfen“ deterministisch nachbauen. `risk.py` könnte eine `policy.json` je Fonds lesen (z. B. „Kategorie Geopolitik gesperrt: 6 Trades, −8 %“). Der Agent sieht die Sperre in `portfolio()`. Das ist billiger und härter als jede Notizbuch-Lektion.
- Aufwand: gering bis mittel (Kennzahlen in `metrics.py`, Policy-Prüfung in `exchange/risk.py`)
- Bewertung: 5/5
- Status: **getestet**. `edge.edge_report` lief isoliert mit 60 synthetischen Trades eines Agenten, der +12 pp Vorteil *glaubt*, während das Buch recht hat. Ergebnis: Kalibrierungstabelle zeigt vorhergesagt 0,695 gegen tatsächlich 0,556 im Band [0,50; 0,85], Edge −4,8 pp, Urteil „NO MEASURED EDGE (n=60 …)“. Skript: `‹Sandbox›/test-agents/scripts/test_edge.py`

#### OctagonAI/kalshi-trading-bot-cli
- Link: https://github.com/OctagonAI/kalshi-trading-bot-cli | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 407 / 2026-10-01
- Was es kann: TypeScript-CLI. Edge = Modellwahrscheinlichkeit minus Orderbuch, fraktionaler Kelly, **5 Risiko-Gates (Kelly, Liquidität, Korrelation, Konzentration, Drawdown)**, Körbe mit Cluster- und Korrelationsgrenzen, Papier-Journal. Hinweis „edge provenance“: Das Modell ist am Markt verankert, ein „Edge“ aus `market_baseline` ist also nur mechanisch. Die Kernwahrscheinlichkeiten kommen aber aus der **kostenpflichtigen Octagon-API**.
- Nutzen für die Arena: Die Gates **Korrelation und Konzentration** fehlen in der Arena (Grenzen gibt es nur je Position). Übernehmbar ist eine **Themen-Cluster-Grenze** je Fonds (z. B. höchstens 25 % Kapital in Märkten mit gleichem Thema-Tag „Nahost“). Dazu bekommt jeder Wettmarkt beim Snapshot einen Tag (Kategorie von Polymarket/Kalshi oder billige Haiku-Verschlagwortung). Die Herkunfts-Warnung passt zur Fehlbewertungs-Erkennung der Arena.
- Aufwand: mittel
- Bewertung: 3/5 (Muster), Code nicht nutzbar (bezahlte API)
- Status: geprüft (README gelesen)

#### Polymarket/agents
- Link: https://github.com/Polymarket/agents | Lizenz: MIT (LICENSE.md gelesen) | Sterne/letzter Commit: 3.806 / 2024-11-05, **Repo archiviert**
- Was es kann: Offizielles Framework für Polymarket-Agenten (API-Anbindung, RAG, Prompt-Hilfen), für echten Handel gedacht.
- Nutzen für die Arena: Keiner (veraltet, archiviert, auf echte Orders ausgelegt, Nutzungsbedingungen beschränken US-Personen).
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (Metadaten, LICENSE) → verworfen

#### Reflexion (noahshinn/reflexion)
- Link: https://github.com/noahshinn/reflexion | Paper https://arxiv.org/abs/2303.11366 | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 3.372 / 2025-01-13
- Was es kann: Verbales Verstärkungslernen. Nach einem Fehlschlag schreibt der Agent eine Selbstreflexion in ein episodisches Gedächtnis, das im nächsten Versuch im Prompt steht.
- Nutzen für die Arena: Das Grundmuster hinter Notizbuch, Opus-Review und TradingAgents-Reflector. Neu daraus: Reflexion *ereignisgesteuert* bei Stop-Loss, Liquidation oder falsch abgerechneter Wette auslösen, nicht nur wöchentlich. Siehe TradingAgents.
- Aufwand: gering
- Bewertung: 3/5
- Status: geprüft (Metadaten, LICENSE), Methode bekannt aus dem Paper

#### Multi-Agent-Debatte: Du et al. + „Diversity of Thought“ + „Debate or Vote“
- Links: https://github.com/composable-models/llm_multiagent_debate (ICML 2024; **keine LICENSE-Datei**, 556 Sterne, letzter Commit 2025-04-24) | https://arxiv.org/abs/2410.12853 | https://arxiv.org/abs/2508.17536 (NeurIPS 2025)
- Was es kann: Du et al.: Mehrere Instanzen debattieren über Runden und werden dadurch faktentreuer. Hegazy: **Verschiedene Modelle** in der Debatte schlagen 3 Kopien desselben Modells (GSM-8K 91 % gegen 82 %, nur Mathematik, Einzelautor). Choi/Zhu/Li: **Mehrheitsabstimmung erklärt den Großteil des Debattengewinns**. Debatte allein ist ein Martingal und verbessert die erwartete Korrektheit nicht. Aus der Suche zusätzlich: Ein Paper zu Wettmarkt-Auflösung fand, dass deliberativer Konsens *unter* jedes Einzelmodell fällt (≈76 %; nur Sekundärquelle, https://arxivexplorer.arxivexplorer.workers.dev/paper/2605.30802).
- Nutzen für die Arena: Eine **wichtige Gegenposition zu TradingAgents**. Mehrere Debattenrunden kosten viele Tokens und bringen gegenüber *unabhängigen Stichproben plus Aggregation* wenig. Für die Arena heißt das: (1) keine langen Bull/Bear-Runden, sondern **höchstens ein gezielter Gegenpass** (Rote Mannschaft/Risikomanager), (2) Vielfalt über **verschiedene Modelle** (Liga) und unterschiedliche Informationen, nicht über Kopien, (3) Aggregation per (getrimmtem) Mittel oder Median.
- Aufwand: –
- Bewertung: 4/5 (als Entscheidungsgrundlage)
- Status: nur gelesen (Sekundärquelle), Debate-Repo Metadaten geprüft

#### „Information Homogenization Induces Herding in Retrieval-Augmented LLM Agent Markets“ (ICLR 2026)
- Link: https://www.iclr.cc/virtual/2026/10016534 | Lizenz/Sterne: –
- Was es kann: Zeigt im Experiment, dass die **Überlappung der abgerufenen Dokumente** die Korrelation der Handelsaktionen antreibt (mittlere paarweise Korrelation steigt von ≈0,04 auf ≈0,41, wenn die Überlappung von 0 auf 1 geht). Zahlen aus der Suchzusammenfassung, nicht im Volltext geprüft.
- Nutzen für die Arena: **Erklärt das Klumpenrisiko** wahrscheinlich besser als die Persönlichkeit. Alle drei Claude-Fonds sehen denselben Schnappschuss, dieselben 25 Ereignisse in gleicher Reihenfolge, denselben Notizbuch-Stil und dieselbe Websuche. Gegenmittel: **unterschiedliche Informationsdiäten** je Fonds, z. B. Vorsichtig bekommt Ereignisse nach Liquidität sortiert, Mittel nach Markt-Vielfalt (höchstens 3 je Thema), Aggressiv nach Bewegung/Volatilität. Dazu Pflicht-Startwerkzeuge je Fonds und verschiedene Suchschwerpunkte. Die Persona allein reicht vermutlich nicht.
- Aufwand: gering (Sortierung und Filter in `entscheider.relevante` bzw. `runde_prompt`)
- Bewertung: 5/5 (Diagnose plus Hebel)
- Status: nur gelesen (Sekundärquelle)

#### NousResearch/hermes-agent
- Link: https://github.com/NousResearch/hermes-agent | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 258.664 / 2026-10-30
- Was es kann: Allgemeiner Terminal- und Desktop-Agent mit eigenem Gedächtnis, eigenen Fähigkeiten und eigener Werkzeugwelt.
- Nutzen für die Arena: Laut DECISIONS.md schon geprüft und verworfen (kopfloser Betrieb, Budget im Code, identische Werkzeuge). Neue Gründe für eine Neubewertung habe ich nicht gefunden. Es gibt keine Trading-spezifischen Muster, die die eigene Schleife nicht schon hat.
- Aufwand: hoch
- Bewertung: 1/5
- Status: geprüft (Metadaten, LICENSE) → bleibt verworfen

#### CrewAI / LangGraph / AutoGen (Finanzbeispiele)
- Links: https://github.com/crewAIInc/crewAI (MIT, 60.286 Sterne, letzter Commit 2026-10-29) | https://github.com/crewAIInc/crewAI-examples (**keine LICENSE-Datei**, letzter Commit 2026-04-20, Sterne ungeprüft) | https://github.com/langchain-ai/langgraph (MIT, 44.145 Sterne, 2026-10-29) | https://github.com/microsoft/autogen (Code MIT laut `LICENSE-CODE`, Doku CC-BY-4.0; 61.628 Sterne, 2026-10-28)
- Was es kann: Orchestrierungs-Frameworks. Die Finanzbeispiele (Aktienanalyse-Crew, TradingAgents auf LangGraph, FinRobot V0 auf AutoGen) sind Rollen-Pipelines aus Analyst, Researcher und Entscheider.
- Nutzen für die Arena: Kein Mehrwert gegenüber der eigenen Schleife. Sie bringen Abhängigkeiten und verdeckte Token-Kosten und erschweren das harte Budget je Aufruf. Die *Rollen* lassen sich als zusätzliche `AnthropicSitzung`-Aufrufe abbilden (siehe Muster).
- Aufwand: hoch
- Bewertung: 1/5
- Status: geprüft (Metadaten und Lizenzen)

#### OpenBB-finance/agents-for-openbb
- Link: https://github.com/OpenBB-finance/agents-for-openbb | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 410 / 2026-07-01, **archiviert**
- Was es kann: Beispielagenten für die OpenBB Workspace (Widgets, Zitate, Diagramme).
- Nutzen für die Arena: Keiner (an die Workspace-Oberfläche gebunden, archiviert). Die OpenBB-*Datenplattform* gehört in die Daten-Kategorie, nicht hierher.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (README) → verworfen

#### SamuelSchmidgall/AgentLaboratory
- Link: https://github.com/SamuelSchmidgall/AgentLaboratory | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 5.914 / 2025-08-20
- Was es kann: Ein Agenten-Workflow für Forschung: Literatur → Plan → Experiment (Code) → Bericht, mit Rollen PhD, Postdoc, ML-Engineer und Reviewer.
- Nutzen für die Arena: Als **Opus-Wochenreview Stufe 2** denkbar. Das Review schlägt nicht nur Regeln vor, sondern formuliert **eine überprüfbare Hypothese je Woche** („Fonds X verliert bei Wettmärkten mit < 7 Tagen Restlaufzeit“), und ein deterministisches Skript wertet sie auf `decisions.jsonl` aus. Das Framework selbst nicht einbauen.
- Aufwand: mittel
- Bewertung: 2/5
- Status: geprüft (Metadaten, LICENSE)

#### INVESTOR-BENCH (felis33) und Open-Finance-Lab/AgenticTrading
- Links: https://github.com/felis33/INVESTOR-BENCH (MIT, 34 Sterne, letzter Commit 2025-09-12; ACL 2025) | https://github.com/Open-Finance-Lab/AgenticTrading (Lizenz **OpenMDW-1.0**, ungewöhnlich, 788 Sterne, letzter Commit 2026-10-30)
- Was es kann: InvestorBench vergleicht Einzelagenten-Designs (Nachfolger von FinMem) über Aktien, Krypto und ETFs. AgenticTrading ist ein Protokoll-orientiertes (MCP/A2A) Framework für Agenten-Pools.
- Nutzen für die Arena: Gering. InvestorBench bestätigt FinMem-Muster. AgenticTrading hat eine unklare Lizenz und ist schwer.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (Metadaten, LICENSE)

#### forecastingresearch/forecastbench
- Link: https://github.com/forecastingresearch/forecastbench | Lizenz: MIT (LICENSE gelesen) | Sterne/letzter Commit: 92 / 2026-10-29
- Was es kann: Dynamischer, kontaminationsfreier Prognose-Benchmark mit menschlichen Vergleichsgruppen (Fragen aus Märkten und Datensätzen).
- Nutzen für die Arena: Als **externe Eichung** der Liga-Modelle. Die öffentlichen Ranglisten zeigen, welche Modelle als Prognostiker gut kalibriert sind, und helfen bei der Wahl der Liga-Modelle und Startgewichte im Meta-Fonds. Der Fragenpool könnte auch eine zusätzliche reine Prognose-Liga ohne Geld speisen.
- Aufwand: gering (nur nachschlagen)
- Bewertung: 2/5
- Status: geprüft (Metadaten, LICENSE)

---

#### Übernehmbare Muster

Geordnet nach Verhältnis von Nutzen zu Aufwand. Alles passt in die eigene Schleife, ohne fremdes Framework.

**M1 – Echte Denkschulen statt Risikoadjektive (gegen Klumpenrisiko)** · Quelle: ai-hedge-fund, ContestTrade-„beliefs“, TradingGPT, forecasting-tools `ai_congress`
`persoenlichkeit` in `config.json` wird zu einem Block mit 4–6 Denkregeln, eigener Skala für die Zuversicht und eigenem Horizont. Vorschlag:
- *Vorsichtig = „Basisraten-Prognostiker“*: Status quo und Basisrate zuerst. Handelt fast nur Wettmärkte mit klarer Abrechnungsquelle. Ein Vorteil zählt erst ab ≥8 pp nach Kosten. Bevorzugt NEIN-Seiten bei Hype.
- *Mittel = „Arbitrageur/Mikrostruktur“*: sucht Kreuz-Plattform-Abweichungen, Funding und Regel-Feinheiten (Abrechnungsdetails). Meidet Richtungswetten auf Nachrichten.
- *Aggressiv = „Makro/Momentum, konträr bei Überreaktion“*: Krypto, Perps, Optionen. Wettmärkte nur, wenn der Marktpreis sich in < 24 h stark bewegt hat (Überreaktion).

Dazu eine Zeile im Rundenprompt: „Dein Fonds verfolgt *seine* Schule. Thesen außerhalb davon nur mit besonderem Grund.“ Aufwand: gering.

**M2 – Unterschiedliche Informationsdiäten** · Quelle: ICLR-2026-Herding-Paper, DeepFund-Planner
In `runde_prompt` erhält jeder Fonds die Ereignisse anders sortiert und gefiltert (siehe oben) und dazu einen „Rechercheplan“ von der Triage (Haiku liefert `{"aufwecken":…, "plan":["…","…"]}`). Optional: Websuche je Fonds mit anderen Quellenvorgaben (Vorsichtig: offizielle Quellen und Regeln; Aggressiv: Märkte, Funding, Social). Aufwand: gering.

**M3 – Pflichtfelder für Wettmarkt-Schätzungen (Superforecaster-Gerüst)** · Quelle: metac-bot-template, Prophet Arena, Wisdom of the Silicon Crowd
Das Werkzeug `wahrscheinlichkeit` und die Wettmarkt-Order verlangen: `abrechnungsquelle_und_datum`, `zeit_bis_aufloesung`, `status_quo_ausgang`, `basisrate` (mit Herkunft), `ueberraschungsszenario`, `p_eigene_schaetzung`, `p_markt`, `p_handel` (Mischung). Regel: „Weiche von `p_markt` nur stark ab, wenn du eine konkrete, neue Informationsquelle nennst.“ Gegen den JA-Bias: „Prüfe, ob du die JA-Seite nur wegen der Frageformulierung bevorzugst. Formuliere die Frage im Kopf als NEIN-Frage um.“ Aufwand: gering.

**M4 – Pflichtfelder in jeder Order** · Quelle: nof0-Rekonstruktion (nof1), TradingAgents-PM
Zusätzlich zu `ausstiegsplan`: `invalidierung` (konkretes, beobachtbares Signal), `staerkstes_gegenargument` (ein Satz) und `risiko_usd` (Verlust bis Stop oder bei Wetten bis 0). `portfolio()` gibt `invalidierung` je offener Position aus, und Schritt 1 des Weitblick-Prompts prüft explizit: „Ist eine Invalidierung eingetreten? Dann schließen oder begründen.“ Ankerskala für `zuversicht` (0,9+ unverkennbar / 0,7–0,89 solide / 0,4–0,69 gemischt / <0,4 kein Vorteil → nicht handeln). Aufwand: gering (`tools.py` Schema und Prüfung).

**M5 – Ein Risikomanager-Pass vor großen Orders (statt mehrstufiger Debatte)** · Quelle: TradingAgents-Risiko-Trio, „Debate or Vote“, AIA-Supervisor
In `Kontext.t_order` wird vor der Ausführung für Orders über einer Schwelle (z. B. >10 % Kapital, Hebel >2 oder neue Themen-Konzentration) **ein** Haiku-Aufruf gemacht. System: „Du bist Risikomanager. Du argumentierst nur gegen diese Order. Prüfe Kosten, Abrechnungsregel, Konzentration, Invalidierung, Gegenargument. Antworte JSON `{urteil: freigeben|verkleinern|ablehnen, faktor: 0..1, grund}`.“ Bei `verkleinern` wird die Order mit dem Faktor gekürzt, bei `ablehnen` bekommt der Agent den Grund als Tool-Ergebnis und darf *einmal* mit Gegenbegründung erneut ordern. Alles wird in `decisions.jsonl` protokolliert. Der Pass ist billig, begrenzt (eine Runde) und für die Liga identisch (gleiches Haiku-Urteil, damit der Vergleich fair bleibt). Aufwand: mittel.

**M6 – Grenze für Themen-Cluster je Fonds und Überlappungskennzahl der Arena** · Quelle: OctagonAI-Gates, ai-hedge-fund `risk/limits.py`
Jeder Markt bekommt einen Thema-Tag (Kategorie der Plattform, sonst Haiku-Verschlagwortung beim Snapshot, im Cache). `risk.py` begrenzt das Exposure je Tag (z. B. Vorsichtig 15 %, Mittel 25 %, Aggressiv 40 %). Auf der Seite: **Jaccard-Überlappung der Positionen** zwischen Fonds und Korrelation der Equity-Kurven als Klumpen-Warnung. Fonds untereinander *nicht* informieren, das würde die unabhängige Messung verfälschen. Aufwand: mittel.

**M7 – Reflexion bei Abrechnung (ereignisgesteuert)** · Quelle: TradingAgents `Reflector`, Reflexion, FinAgent
Hook beim Schließen oder Abrechnen einer Position: Haiku bekommt Begründung, Zuversicht, Ergebnis, Haltedauer und Vergleich (BTC Buy&Hold, SPY bzw. Marktpreis zum Einstieg) und schreibt 2–4 Sätze: (1) Was zeigt das Ergebnis (mit Zahl), Fenster zu kurz? (2) Welcher Teil der These wurde gestützt oder widerlegt? (3) Genau eine Lektion. Das Ergebnis geht als `lektion` mit Wichtigkeit ins Notizbuch. Aufwand: gering.

**M8 – Geschichtetes, gewichtetes Notizbuch** · Quelle: FinMem, TradingGPT
Felder `wichtigkeit` (1–10) und `gueltig_bis`. `als_text` wählt je Typ nach `wichtigkeit × exp(-alter/τ)` (τ: Beobachtung 3 d, These 14 d, Lektion 90 d, Regel 365 d) plus Bonus bei Stichwort-Treffer mit Ereignissen oder Positionen. Abgelaufene Regeln prüft das Opus-Review (Muster FinCon: Regel mit Beleg und Ablaufdatum). Aufwand: gering bis mittel.

**M9 – Kalibrierungs-Feedback und „Haircut“** · Quelle: forecasting-tools (Platt BIA/CON), ryanfrigo edge/learnings
`metrics.py` berechnet je Fonds ab n≥15 abgerechneten Schätzungen BIA und CON, Edge-vs-Book und eine Kalibrierungstabelle. Der Rundenprompt bekommt eine Zeile: „Deine Kalibrierung bisher (n=…): JA-Überschätzung … pp, Überkonfidenz-Faktor …; im Band 60–80 % lagst du bei … % Trefferquote.“ Optional wendet die Börse den Haircut *hart* an: Die festgehaltene `wahrscheinlichkeit_ja` wird für die Größenberechnung rekalibriert, für die Brier-Messung bleibt der Rohwert. Grundsatz: „<5 Fälle = keine Meinung“. Aufwand: gering.

**M10 – Policy-Gate aus eigener Bilanz** · Quelle: ryanfrigo „Edge Policy“
Deterministisch nach jeder Abrechnung: Kategorie oder Seite mit ≥5 abgerechneten Trades und negativer GuV → `policy.json` sperrt neue Käufe dort (Agent sieht die Sperre in `portfolio()`, das Override wird protokolliert). Nur verschärfen, nie automatisch lockern. Lockern darf nur das Opus-Review mit Begründung. Aufwand: gering bis mittel.

**M11 – Meta-Fonds „Schwarm der Arena“** · Quelle: ContestTrade, Wisdom of the Silicon Crowd, Halawi (getrimmter Mittelwert), AIA (Mischung mit Markt)
Neuer Fondstyp ohne LLM: Je Wettmarkt mit ≥3 frischen Schätzungen (≤48 h) aus verschiedenen Fonds wird erst rekalibriert (M9), dann der getrimmte Mittelwert gebildet, gewichtet mit `1/Brier` (Start gleichgewichtet), dann mit dem Marktpreis gemischt (z. B. 50/50, später fitten). Handel nur, wenn |p_mix − Preis| > Rundreisekosten + Puffer, Größe mit ¼-Kelly. Eine Variante „Schwarm nur Liga (freie Modelle)“ gegen „Schwarm nur Claude“ zeigt, ob Modellvielfalt hilft. Kosten 0 Tokens, großer Erkenntniswert. Aufwand: mittel.

**M12 – Werkzeug „schwarm_schaetzung“ (optional, kostet Liga-Tokens)** · Quelle: metac-Template (5 Stichproben), Halawi, Hegazy
Für einen Wettmarkt fragt das Werkzeug 3–5 freie Liga-Modelle *ohne Marktpreis* (gegen Anker) mit dem M3-Gerüst nach P(JA) und gibt Median und Streuung zurück. Große Streuung signalisiert Unsicherheit und spricht für weniger Größe. Nur auf dem Oracle-Server oder mit Tageslimit, weil Wanduhr und Ratenlimits der freien Modelle knapp sind. Aufwand: mittel.

**M13 – Kennzahlen gegen Übertrading** · Quelle: nof1-Lehren
Rangliste und Review zeigen Trades je Woche, Gebühren und Slippage in % des Kapitals, mittlere Haltedauer und den Anteil Long/Short/JA/NEIN. Prompt-Regel: „Jede neue Order muss erklären, warum sie mehr bringt als die Rundreisekosten *und* als Nichtstun.“ Aufwand: gering.

**M14 – Gezielte Gegen-Suche (HyDE umgedreht)** · Quelle: MarketSenseAI (HyDE), Weitblick Schritt 3
Ein Satz in Schritt 3: „Schreibe vor der Gegenrecherche die Schlagzeile, die deine These widerlegen würde, und suche nach genau dieser Meldung.“ Aufwand: minimal.

**M15 – A/B-Fonds für Designfragen** · Quelle: Agent Market Arena („Design > Modell“)
Ein vierter Claude-Fonds (z. B. „Mittel+RM“) mit identischer Persona wie Mittel, aber mit M5 (Risikomanager) oder M3 (Gerüst). Nur so lässt sich messen, ob die Muster helfen. Kosten ≈ +⅓ des Claude-Budgets. Alternativ wechselt ein Liga-Modell wöchentlich zwischen den Varianten. Aufwand: gering (Konfiguration), aber Budget.

---

_Verworfene Kandidaten dieser Kategorie: siehe [ANHANG-verworfen.md](ANHANG-verworfen.md), Abschnitt „1. LLM-Trading-Agenten, Multi-Agenten-Systeme und kreative Methoden“._

### Top-Empfehlungen dieser Kategorie

1. **Schneller Gewinn: Wettmarkt-Gerüst und Order-Pflichtfelder (M3 + M4).** Status quo, Basisrate, Überraschungsszenario, Abrechnungsquelle und -datum, `p_eigen`/`p_markt`/`p_handel`, Invalidierung, stärkstes Gegenargument, `risiko_usd`, Ankerskala für die Zuversicht. Nur `prompts.py` und das Schema in `tools.py`, 0 zusätzliche Tokens je Aufruf, wirkt sofort für Claude *und* Liga. (Quellen: metac-bot-template, Prophet Arena, nof1/nof0, ai-hedge-fund)

2. **Schneller Gewinn: Diversität über Denkschulen *und* Informationsdiät (M1 + M2).** Das ist das direkte Gegenmittel zum Iran-Waffenruhe-Klumpen. Nach der Herding-Evidenz ist die gleiche Information wahrscheinlich der Haupttreiber, nicht die Persona. Dazu Überlappung der Positionen als Kennzahl auf der Seite (Teil von M6). (Quellen: ICLR-2026-Herding, ai-hedge-fund, ContestTrade, DeepFund)

3. **Schneller Gewinn mit Dauerwirkung: geschlossener Lern- und Kalibrierkreis (M7 + M9 + M10).** Reflexion bei Abrechnung (TradingAgents-Reflector), BIA/CON- und Edge-vs-Book-Feedback im Rundenprompt (forecasting-tools, beide Teile *getestet*), deterministisches Policy-Gate nach eigener Bilanz (ryanfrigo, *getestet*). Wenige deterministische Zeilen in `metrics.py`/`risk.py` plus ein Haiku-Aufruf je abgerechneter Position.

4. **Großer Hebel: Meta-Fonds „Schwarm der Arena“ (M11), später das Werkzeug `schwarm_schaetzung` (M12).** Er braucht kein LLM, nutzt die vorhandenen Schätzungen aller Fonds, rekalibriert sie, bildet den getrimmten Mittelwert, mischt ihn mit dem Markt und handelt nur Abweichungen über den Kosten. Er beantwortet die Kernfrage des Projekts (hat *der Schwarm* einen Vorteil, auch wenn kein Einzelmodell einen hat?) und ist laut AIA und Silicon Crowd die aussichtsreichste Konstruktion. (Quellen: ContestTrade, Wisdom of the Silicon Crowd, Halawi, AIA Forecaster)

5. **Mittlerer Hebel: ein Risikomanager-Pass vor großen Orders (M5) plus Themen-Cluster-Grenze (M6), gemessen als A/B-Fonds (M15).** Ein gezielter Gegen-Aufruf statt mehrstufiger Bull/Bear-Debatte, denn die Evidenz sagt: Abstimmen und Aggregieren schlägt lange Debatten. Ob das hilft, zeigt erst ein Vergleichsfonds mit sonst gleichem Design. (Quellen: TradingAgents, „Debate or Vote“, Agent Market Arena, OctagonAI)


---

## 2. Benchmarks, Evaluation, Schutz vor Lookahead

### Kategorie: Benchmarks und Evaluation für LLM-Trader und LLM-Prognostiker

Stand der Prüfung: 2026-10-30. Sterne stammen aus der GitHub-Suche (MCP `search_repositories`) vom 30.10.2026; Lizenz und letzter Commit stammen aus einem flachen `git clone --depth 1` (LICENSE-Datei gelesen, `git log -1`) vom selben Tag. Alles, was nicht so geprüft wurde, ist als „ungeprüft“ markiert. Die Zahlen zu Papers stammen aus den arXiv-Abstracts bzw. aus Sekundärquellen (dann so gekennzeichnet).

**Ausgangslage in der Arena** (`arena/metrics.py`, `arena/agent/tools.py`): Rendite, Max-Drawdown, Sharpe (annualisiert mit 365, `pstdev`, ab 8 Tageswerten), Trefferquote, Brier je Fonds. Für den Brier zählt die *erste* Schätzung je Markt, und zu jeder Schätzung wird schon der Markt-Mittelkurs `markt_ja_mitte` mitgespeichert. Damit ist ein Vergleich gegen den Marktpreis (Brier-Skill gegen Markt) fast kostenlos zu haben. API-Kosten in € werden ebenfalls schon erfasst. Es fehlen: Unsicherheit (Konfidenzintervalle), eine Korrektur für Mehrfachvergleiche (12+ Fonds, „bestes Liga-Modell“ wird nach Rangliste gewählt), Kalibrierung/Zerlegung, ein marktrelativer Score, kostenbereinigte Kennzahlen und eine Aussage, ab wann ein Unterschied überhaupt signifikant sein *kann*.

**Kernaussage der Literatur:** Alle seriösen neueren LLM-Trading-Benchmarks (DeepFund, StockBench, LiveTradeBench, AI-Trader, Agent Market Arena, Prophet Arena, ForecastBench, FutureX, KalshiBench, PolyBench) sind aus demselben Grund auf **Live- bzw. Vorwärtstests** umgestiegen, den die Arena schon in DECISIONS/PLAN nennt: Rücktests mit LLMs sind durch Trainingswissen verfälscht (Profit Mirage, Lopez-Lira et al., Gao/Jiang/Yan). Die Arena liegt methodisch also richtig. Ihre Schwäche ist die **statistische Auswertung bei kleiner Stichprobe und vielen Fonds**.

**Funktionstest (getestet):** In `‹Sandbox›/test-bench/eval_test.py` (venv, `python -I`, synthetische Daten, keine Schlüssel, kein Repo-Code) wurden quantstats 0.0.86, empyrical-reloaded 0.7.1, scoringrules 0.10.0, arch 8.0.0 und properscoring 0.1 installiert. Damit wurden PSR, DSR, MinTRL, Block-Bootstrap-KI, Hansen-SPA, Murphy-Zerlegung, BSS gegen Markt, Log-Score, Diebold-Mariano, Fragen-Bootstrap und eine Fallzahlplanung nachgerechnet. Ergebnis bei 12 Fonds **ohne** echten Vorteil und 60 Tagen:
- Der „glücklichste“ Fonds hatte einen annualisierten Sharpe von 1,15.
- PSR = 0,68, DSR = 0,19.
- MinTRL = 746 Tage.
- 95-%-KI des Sharpe: [−5,6; 7,0].
- SPA-p-Wert: 0,95.

Das heißt: Eine Rangliste nach 2 Monaten ist Rauschen, und die Werkzeuge zeigen das korrekt an. quantstats' `sharpe(periods=365)` stimmt mit der Handrechnung überein (1,147).

---

#### StockBench (Tsinghua/BUPT)
- Link: https://github.com/ChenYXxxx/stockbench · Paper https://arxiv.org/abs/2510.02209 · Projekt https://stockbench.github.io/ | Lizenz: Apache-2.0 (geprüft) | Sterne/letzter Commit: 184 ★ / 2025-10-28 (geprüft)
- Was es kann: Mehrmonatiger Handels-Benchmark auf 20 Dow-Aktien (laut Sekundärquelle März–Juni 2025, ca. 82 Handelstage). Agenten sehen nur Daten bis zum Entscheidungstag (Preise, Fundamentaldaten, Schlagzeilen). Kennzahlen: Rendite, Max-Drawdown, Sortino. Befund: Gute Werte bei statischen Finanz-Fragen übertragen sich nicht auf den Handel.
- Nutzen für die Arena (konkret): Referenz für Kennzahlen-Set und Prompt-Format (täglicher Entscheidungszyklus, festes Aktien-Universum gegen Auswahlverzerrung). Seine Rücktestphase liegt vor dem Wissensstand heutiger Modelle, ist für aktuelle Modelle also verseucht. Darum nur als Vorlage verwenden, nicht als Messung. Ein Inspect-Port existiert (https://github.com/mahimn01/stockbench-inspect, 0 ★, ungeprüft).
- Aufwand: gering (nur Ideen übernehmen) / mittel (Nachbau des Dow-20-Universums als zusätzlicher Arena-Markt)
- Bewertung: 3/5
- Status: geprüft (Repo), Paper nur Abstract/Sekundärquelle gelesen

#### InvestorBench
- Link: https://github.com/felis33/INVESTOR-BENCH · Paper https://arxiv.org/abs/2412.18174 (ACL 2025) · https://suchow.io/investorbench/ | Lizenz: MIT (geprüft) | Sterne/letzter Commit: 34 ★ / 2025-09-12 (geprüft)
- Was es kann: Agenten-Benchmark für Aktien-, Krypto- und ETF-Entscheidungen mit 13 LLM-Backbones, schichtweisem Gedächtnis (FinMem-Linie) und historischen Umgebungen.
- Nutzen für die Arena: Gering als Messinstrument, weil es ein historischer Rücktest ist und damit lookahead-anfällig. Brauchbar ist die Aufteilung der Aufgaben (Aktie/Krypto/ETF getrennt auswerten), also eine Rangliste je Anlageklasse in der Arena.
- Aufwand: gering (Idee) – hoch (Integration; lohnt nicht)
- Bewertung: 2/5
- Status: geprüft (Repo), Paper nur gelesen

#### FinBen / PIXIU (The-FinAI)
- Link: https://github.com/The-FinAI/PIXIU · Paper https://arxiv.org/abs/2402.12659 | Lizenz: MIT für den Code (geprüft); die Datensätze haben eigene Lizenzen (MIT, CC BY 4.0, CC0, „Public“), und laut README sind Repo und Inhalt nur für akademische/Bildungszwecke gedacht | Sterne/letzter Commit: 896 ★ / 2026-10-08 (geprüft)
- Was es kann: Statischer Benchmark mit 35–36 Datensätzen und 23–24 Finanzaufgaben (Sentiment, NER, QA, Aktienbewegung, …), dazu das FinMA-Modell.
- Nutzen für die Arena: Kaum einer. Statische Finanz-QA sagt laut StockBench/LiveTradeBench wenig über Handelserfolg aus und ist durch Trainingsdaten verseucht. Höchstens als Vorab-Filter, um für die Liga ein Gratis-Modell auszuwählen, das Finanztexte grundsätzlich versteht.
- Aufwand: mittel (lm-eval-Harness, GPU wünschenswert)
- Bewertung: 1/5
- Status: geprüft (Repo)

#### Prophet Arena
- Link: https://www.prophetarena.co/ · Paper https://arxiv.org/abs/2510.17638 (ICLR 2026) | Lizenz: Code nicht gefunden (ungeprüft) | Sterne/letzter Commit: – (kein Repo gefunden)
- Was es kann: Live-Benchmark auf offenen Kalshi-Ereignissen, laut Sekundärquelle 81 % Sport. Die Pipeline zerlegt die Aufgabe in Stufen (Ereignis → Kontext aus News und Marktdaten → Wahrscheinlichkeit). Laut Abstract misst es Kalibrierungsfehler, Konsistenz der Zuversicht und „market returns“, also den ökonomischen Wert gegen den Marktpreis. Befund: Märkte verarbeiten Informationen kurz vor der Auflösung schneller, LLMs zeigen Stärken bei langen Horizonten.
- Nutzen für die Arena (konkret): (1) **Ökonomischen Wert gegen den Marktpreis** als zweite Prognose-Kennzahl neben dem Brier übernehmen. Dafür hypothetisch 1 $ setzen, wenn |p − p_markt| > Schwelle, zum Marktpreis; siehe „Übernehmbare Methoden“. (2) Brier nach **Horizont** aufschlüsseln (Restlaufzeit bei der Schätzung). Die Arena speichert `ts`; nötig ist zusätzlich die Schlusszeit des Markts.
- Aufwand: gering (Metrik) – Teilnahme ist offenbar nicht offen (ungeprüft)
- Bewertung: 4/5
- Status: nur gelesen

#### ForecastBench (Forecasting Research Institute)
- Link: https://github.com/forecastingresearch/forecastbench · https://www.forecastbench.org · Daten: https://huggingface.co/datasets/forecastingresearch/forecastbench-datasets · Paper https://arxiv.org/abs/2409.19839 | Lizenz: Code MIT (geprüft), Daten CC BY-SA 4.0 (geprüft, HF-Karte) | Sterne/letzter Commit: 92 ★ / 2026-10-29 (geprüft); Daten-Repo 43 ★, nächtlich aktualisiert
- Was es kann: Dynamischer, kontaminationsfreier Benchmark mit Markt-Fragen (Polymarket, Manifold, Metaculus, …) und Datensatz-Fragen (FRED, ACLED, …) sowie Vergleichsgruppen aus Superforecastern und Laien. **Im Code gelesen** (`src/leaderboard/main.py`):
  - Peer-Score: `question_avg_brier − brier_score`
  - Brier-Skill gegen ein Naiv-Modell je Frage
  - schwierigkeitsbereinigter Brier: Bei Markt-Fragen ist die Schwierigkeit gleich dem Markt-Brier, alternativ Two-Way-Fixed-Effects
  - Neu-Skalierung, sodass „immer 0,5“ = 0,25
  - **Brier-Index = 100·(1 − √Brier)** (100 = perfekt, 50 = immer 50 %)
  - **Fragen-Bootstrap mit 1999 Wiederholungen** für 95-%-KIs und p-Werte zwischen Modellen
- Nutzen für die Arena (konkret): (1) Den **Brier-Index** als verständliche 0–100-Skala auf der Webseite zeigen. (2) **Markt-bereinigter Brier**: Wer einfach den Marktpreis kopiert, bekommt 0. Genau das ist die ehrliche Frage, ob ein LLM den Markt schlägt; die Arena speichert `markt_ja_mitte` bereits. (3) Fragen-Bootstrap für KIs übernehmen (in eval_test.py nachgebaut). (4) **Trainingsfeld:** Die zweiwöchentlichen Fragensätze (HF, CC BY-SA) als zusätzliche, kostenlose Prognose-Aufgaben für Liga-Gratismodelle nutzen. Ob eine offizielle Einreichung von außen möglich ist, ist ungeprüft (die Website nennt ein Tournament-Leaderboard).
- Aufwand: gering (Formeln) / mittel (Fragensätze automatisch beantworten und selbst gegen Auflösungen scoren)
- Bewertung: 5/5
- Status: geprüft (Code gelesen, Formeln verifiziert)

#### FutureX (ByteDance Seed u. a.)
- Link: https://futurex-ai.github.io/ · Daten https://huggingface.co/datasets/futurex-ai/Futurex-Online · Paper https://arxiv.org/abs/2508.11987 (ICLR 2026) | Lizenz: auf der HF-Karte nicht angegeben (ungeprüft) | Sterne/letzter Commit: kein Code-Repo gefunden; HF-Datensatz aktualisiert 26.10.2026, 27,1 Tsd. Downloads (geprüft)
- Was es kann: Größter Live-Benchmark für Zukunftsprognosen, mit **wöchentlicher Challenge**. Laut HF-Karte umfasst die aktuelle Woche Ereignisse mit Ende zwischen 28.10. und 03.11.2026. Vier Schwierigkeitsstufen (Basic, Wide Search, Deep Search, Super Agent); 25 Modelle/Agenten wurden evaluiert. Befund: anfällig für gefälschte Webseiten und Probleme mit zeitlicher Gültigkeit.
- Nutzen für die Arena (konkret): **Trainingsfeld** für die Recherche-Fähigkeit der Agenten. Wöchentlich die Aufgaben laden, von einem günstigen Liga-Modell mit derselben Websuche beantworten lassen und laut Submission-Guidelines einreichen. Die Ergebnisse geben ein externes Maß, ob die Recherche-Schleife der Arena taugt. Die Befunde „gefälschte Webseiten / zeitliche Gültigkeit“ als Prüfpunkte in den Agenten-Prompt aufnehmen (Quelle und Datum jeder Nachricht prüfen).
- Aufwand: mittel (wöchentlicher Workflow, Einreichungsformat)
- Bewertung: 3/5
- Status: geprüft (HF-Karte), Paper nur gelesen

#### Metaculus FutureEval Bot-Turniere (früher „AI Benchmark“ / Q-Turniere, inkl. MiniBench)
- Link: https://www.metaculus.com/aib · Ankündigung Herbst 2026: https://forum.effectivealtruism.org/posts/hrJrsgMCwsdBuAqgQ/announcing-fall-2026-futureeval-bot-tournament · Scores-FAQ: https://www.metaculus.com/help/scores-faq/ | Lizenz: – (Plattform; Teilnahme kostenlos) | Sterne/letzter Commit: –
- Was es kann (Stand Ankündigung, gelesen):
  - Herbstturnier 2026 mit 50.000 $ Preisgeld und 300–400 Fragen; neue Fragen seit 28.09.2026. Es läuft, bis „a few weeks before January 1, 2027“ keine Fragen mehr eröffnet werden. **Einstieg jederzeit möglich** („start in the middle of the leaderboard with 0 points“).
  - **MiniBench**: zweiwöchentliche Turniere mit ca. 60 automatisch erzeugten Fragen und 1.000 $, ausdrücklich für schnelles Feedback gedacht.
  - Market-Pulse-Turnier (7.000 $), bei dem Bots preisberechtigt sind.
  - **Kostenlose LLM- und Such-Credits** (Spenden von Anthropic, Google, OpenAI; Partnerschaft mit AskNews), anfangs ca. 100 $ für einige Bot-Bauer, auf Antrag.
  - Pflicht: Teilnahmeformular. Kommentare, die die Begründung des Bots wiedergeben, sind für Preise erforderlich.
  - Wertung: Baseline- und Peer-Score auf Log-Score-Basis, zeitgemittelt (Zitate siehe „Übernehmbare Methoden“).
- Nutzen für die Arena (konkret): **Bestes Trainingsfeld.** Der Fonds-Agent (bzw. ein Liga-Gratismodell) prognostiziert in einer eigenen GitHub Action (Vorlage: metac-bot-template, siehe unten) auf echten Turnierfragen. Das bringt (a) Hunderte aufgelöste Fragen pro Saison, also genau die Stichprobe, die der Arena-Brier nie erreicht; (b) einen externen, unabhängigen Vergleich mit anderen Bots und Pros; (c) eventuell kostenlose Credits, die das API-Budget nach dem 14.11. entlasten. Die Begründungen der Arena-Agenten sind ohnehin schon vorhanden und passen zur Kommentarpflicht. Vor der Teilnahme die aktuellen Regeln lesen. Ältere Regeln verboten z. B., mit demselben Bot auf anderen Plattformen dieselben Fragen zu beantworten, und verlangten Code oder eine Beschreibung für Preise; für Herbst 2026 ist das ungeprüft.
- Aufwand: mittel (Konto, Token als Secret, Workflow, Formular)
- Bewertung: 5/5
- Status: nur gelesen (Ankündigung und FAQ per Scrape)

#### Metaculus forecasting-tools (+ metac-bot-template)
- Link: https://github.com/Metaculus/forecasting-tools · Vorlage https://github.com/Metaculus/metac-bot-template | Lizenz: MIT (geprüft) | Sterne/letzter Commit: 87 ★ / 2026-10-27 (geprüft); Template ungeprüft
- Was es kann: Python-Rahmen für Metaculus-Bots: `TemplateBot`/`ForecastBot`, `MetaculusClient` (API-Wrapper), `forecast_on_tournament(ID)`, Aggregation, Rechercheschnittstelle (Exa/Perplexity/AskNews), optional `stats` und Kalibrierungs-Adjuster. Läuft laut README **direkt in GitHub Actions** (nur `METACULUS_TOKEN` nötig, Suche optional).
- Nutzen für die Arena: Der schnellste Weg in die FutureEval-Turniere. Eine eigene Unterklasse überschreibt `run_research`/`_run_forecast_on_binary` und ruft darin die Arena-eigene Tool-Use-Schleife bzw. die Liga-Modelle auf. Die Kalibrierungs-Adjuster sind ggf. für die Arena-Prognosen selbst wiederverwendbar.
- Aufwand: gering–mittel (laut README „30 min“ für das Template)
- Bewertung: 5/5
- Status: geprüft (Repo/README)

#### KalshiBench
- Link: https://arxiv.org/abs/2512.16030 | Lizenz: Code/Daten ungeprüft | Sterne/letzter Commit: ungeprüft
- Was es kann: Benchmark für epistemische Kalibrierung mit Kalshi-Fragen nach den Trainings-Cutoffs (Abstract: 300 Fragen; HTML-Version: 1.531 Fragen, 16 Kategorien – widersprüchlich). Kennzahlen: ECE, Brier-Skill-Score gegen die Basisrate. Befund laut Abstract: Alle Modelle sind überzuversichtlich; Claude Opus 4.5 ist am besten kalibriert (ECE 0,120) und als einziges mit positivem BSS (0,057).
- Nutzen für die Arena (konkret): Bestätigt, dass **Überzuversicht** der Hauptfehler ist. Darum in der Arena (1) ECE und Kalibrierungskurve je Fonds zeigen, (2) die Positionsgröße von der *kalibrierten* statt der geäußerten Wahrscheinlichkeit abhängig machen: einfache Platt- bzw. Isotonic-Korrektur aus den eigenen aufgelösten Prognosen, ab ca. 50 Auflösungen.
- Aufwand: gering
- Bewertung: 4/5
- Status: nur gelesen

#### PolyBench
- Link: https://github.com/PolyBench/PolyBench · Paper https://arxiv.org/abs/2604.14199 | Lizenz: **keine LICENSE-Datei** im Repo (geprüft); Paper CC BY-NC-SA 4.0 | Sterne/letzter Commit: ungeprüft / 2026-03-10 (geprüft)
- Was es kann: Zeitpunktgenaue Schnappschüsse von 38.666 binären Polymarket-Märkten (4.997 Ereignisse) samt Orderbuch (CLOB) und Nachrichtenstrom. Sieben LLMs gaben 36.165 Prognosen ab, mit **Ausführungssimulation gegen das Orderbuch**. Kennzahlen: Richtungs-Trefferquote, Confidence-Weighted Return (CWR), APY, Sharpe. Befund: Nur 2 von 7 Modellen waren profitabel, trotz durchgehend hoher Zuversicht.
- Nutzen für die Arena: Kennzahl **CWR** (Rendite gewichtet mit der Zuversicht) als Ergänzung für Wettmärkte; die Orderbuch-Simulation entspricht dem, was die Arena schon tut. Wegen fehlender Lizenz **keinen Code übernehmen**, nur die Idee.
- Aufwand: gering (Metrik)
- Bewertung: 3/5
- Status: geprüft (Repo-Lizenz/Commit), Paper nur Abstract

#### nof1 Alpha Arena (Season 1 / 1.5)
- Link: https://nof1.ai (Leaderboard, nicht direkt geprüft) · Sekundärquellen: https://helloacm.com/alpha-arena-how-ai-performs-in-the-real-crypto-market/ , https://www.blockhead.co/2025/10/21/ai-models-battle-in-live-crypto-trading-competition , https://www.onedayadvisor.com/2025/12/nof1ai-alpha-arena-review-season-15.html | Lizenz: kein Code veröffentlicht (ungeprüft) | Sterne/letzter Commit: –
- Was es kann: Echtgeld-Wettbewerb.
  - Season 1 (18.10.–03./04.11.2025): 6 LLMs mit je 10.000 $ auf Hyperliquid-Perps (BTC, ETH, SOL, XRP, DOGE, BNB), gleicher Prompt, Zero-Shot. Laut Sekundärquellen: Qwen3-Max +22 %, DeepSeek +4,9 %, GPT-5 −62,7 %, Gemini 2.5 Pro −56,7 %.
  - Season 1.5 (ab 19.11.2025): US-Aktien bzw. tokenisierte Aktien (Quellen widersprüchlich), vier Modi; laut Sekundärquelle gewann Grok 4.20, und 7 von 8 Modellen verloren.
- Nutzen für die Arena: Mahnendes Beispiel. Zwei Wochen, kein Konfidenzintervall, keine Kontrolle für Glück: Die Ranglisten wurden breit als „Modell X kann traden“ berichtet, obwohl nof1 selbst von möglichem Glück spricht. Die Arena sollte ihre Rangliste **mit KI-Balken und einem „noch nicht unterscheidbar“-Hinweis** zeigen (siehe MinTRL/SPA). Gleicher Aufbau (gleicher Prompt, gleiche Daten, je ein Fonds pro Modell) = Arena-Liga; die Arena ist mit Gebühren/Slippage/Benchmarks bereits strenger.
- Aufwand: – (keine Übernahme von Code)
- Bewertung: 2/5 (als Lehrbeispiel wertvoll, als Werkzeug nicht)
- Status: nur gelesen (Sekundärquellen, nicht offiziell verifiziert)

#### LiveTradeBench (UIUC)
- Link: https://github.com/ulab-uiuc/live-trade-bench · Paper https://arxiv.org/abs/2511.03628 · PyPI `live-trade-bench` | Lizenz: **PolyForm Noncommercial 1.0.0** (geprüft; nicht MIT/Apache) | Sterne/letzter Commit: 167 ★ / 2025-11-21 (geprüft)
- Was es kann: Live-Umgebung mit Preis- und Newsstrom für US-Aktien **und Polymarket**; 21 LLMs, 50 Tage live. Befund: Hohe Werte in allgemeinen Benchmarks bedeuten keine bessere Handelsleistung.
- Nutzen für die Arena: Fast identisches Konzept, also gute Quelle für Vergleichszahlen und Design-Ideen (Portfolio-Allokation über Aktien plus Wettmärkte). Wegen der Nicht-kommerziell-Lizenz keinen Code übernehmen (privat/nicht-kommerziell wäre erlaubt, aber unnötig, weil die Arena weiter ist).
- Aufwand: gering (Paper lesen)
- Bewertung: 3/5
- Status: geprüft (Repo/Lizenz)

#### Agent Market Arena (AMA) – „When Agents Trade“
- Link: https://arxiv.org/abs/2510.11695 | Lizenz: Code ungeprüft | Sterne/letzter Commit: ungeprüft (kein Repo-Link im Abstract)
- Was es kann: Dauerhafter Live-Benchmark für Krypto und Aktien, mit Marktdaten-Strom, verifizierten Daten und von Experten geprüften News. Vier Agenten-Frameworks (InvestorAgent, TradeAgent, HedgeFundAgent, DeepFundAgent) × fünf Backbones (GPT-4o, GPT-4.1, Claude-3.5-Haiku, Claude-Sonnet-4, Gemini-2.0-Flash). Befund laut Abstract: **Die Agenten-Architektur erklärt mehr Varianz als das Basismodell.**
- Nutzen für die Arena (konkret): Versuchsdesign übernehmen, nämlich **Architektur und Modell faktoriell trennen**. Die Arena variiert heute Risiko-Persönlichkeit (3 Claude-Fonds) und Modell (Liga) gleichzeitig. Ein 2×k-Plan (gleiche Persönlichkeit über alle Modelle, gleiches Modell über alle Persönlichkeiten) erlaubt eine Zerlegung per Two-Way-Fixed-Effects wie bei ForecastBench.
- Aufwand: mittel (Fondszuschnitt ändern, mehr Fonds)
- Bewertung: 3/5
- Status: nur gelesen

#### FinSearchComp
- Link: https://randomtutu.github.io/FinSearchComp (Projektseite laut Suche, ungeprüft) · Paper https://arxiv.org/abs/2509.13160 (ICLR 2026) · HF-Kopien z. B. https://huggingface.co/datasets/ByteSeedXpert/FinSearchComp | Lizenz: ungeprüft | Sterne/letzter Commit: ungeprüft
- Was es kann: 635 von Experten annotierte Fragen zur Finanz-Websuche (zeitkritischer Datenabruf, einfache und komplexe historische Recherche; global und Greater China).
- Nutzen für die Arena: Einmaliger **Test der Recherche-Werkzeuge**: Liefern Websuche und Datenadapter der Agenten korrekte, aktuelle Zahlen? Die Teilaufgabe „Time-Sensitive Data Fetching“ ist nützlich, um zu prüfen, ob Liga-Modelle veraltete Kurse halluzinieren. Für die Handelsbewertung selbst irrelevant.
- Aufwand: mittel
- Bewertung: 2/5
- Status: nur gelesen

#### DeepFund („Time Travel is Cheating“, NeurIPS 2025)
- Link: https://github.com/HKUSTDial/DeepFund · Papers https://arxiv.org/abs/2503.18313 und https://arxiv.org/abs/2505.11065 | Lizenz: MIT (geprüft) | Sterne/letzter Commit: 303 ★ / 2026-03-18 (geprüft)
- Was es kann: Live-Fonds-Arena mit Multi-Agenten-Ablauf (Financial Planner → Analysten-Team → Portfolio-Manager), austauschbaren LLM-Backends und Live-Bewertung als Schutz vor Lookahead. Befund laut Abstract: Selbst DeepSeek-V3 und Claude-3.7-Sonnet machten live Verluste.
- Nutzen für die Arena: Argumentationsgrundlage für „nur Vorwärtstest“ (Titel und Befund passen genau zu DECISIONS.md). MIT-Code als Vorlage für eine Rollenteilung Analyst → Manager, falls die Arena Architektur-Varianten testen will (siehe AMA).
- Aufwand: gering (Zitat/Design) / mittel (Rollen-Variante als zusätzlicher Fonds)
- Bewertung: 3/5
- Status: geprüft (Repo)

#### AI-Trader (HKUDS)
- Link: https://github.com/HKUDS/AI-Trader · Paper https://arxiv.org/abs/2512.10971 · Dashboard https://ai4trade.ai | Lizenz: README-Badge „MIT“, aber **keine LICENSE-Datei** im Repo (geprüft) → rechtlich unklar | Sterne/letzter Commit: 23.036 ★ / 2026-06-11 (geprüft)
- Was es kann: Laut Paper ein vollautomatischer, kontaminationsfreier Live-Benchmark (NASDAQ-100, SSE-50, Krypto, mehrere Frequenzen). Das Repo hat sich inzwischen zu einer TypeScript-Plattform „Agent-Native Trading“ gewandelt (package.json/service/skills) und bietet seit 03.2026 Polymarket-Papierhandel mit Auto-Settlement.
- Nutzen für die Arena: Ideen für Polymarket-Settlement und Agenten-Skills; das Paper liefert Vergleichszahlen. Wegen fehlender Lizenzdatei und Sprachwechsel (TS) keine Code-Übernahme.
- Aufwand: gering (lesen)
- Bewertung: 2/5
- Status: geprüft (Repo-Struktur, Lizenz)

#### Bench to the Future (FutureSearch) – „Pastcasting“
- Link: https://arxiv.org/abs/2506.21558 · https://evals.futuresearch.ai/ · https://epoch.ai/benchmarks/btf-3 | Lizenz: Zugang auf Anfrage (hello@futuresearch.ai), ungeprüft | Sterne/letzter Commit: –
- Was es kann: Prognosen auf schon aufgelöste Fragen mit **eingefrorenem Web-Korpus** (BTF-2: ca. 1.417 Fragen und 15 Mio. Dokumente laut Sekundärquelle; BTF-3: 1.007 bzw. 1.907 Fragen, widersprüchlich). So lässt sich ohne Wartezeit testen, solange das Modell den Ausgang nicht schon kennt.
- Nutzen für die Arena: Methode „Recherche nur in einem zeitlich eingefrorenen Korpus“. Das ließe sich für schnelle A/B-Tests von Agenten-Prompts nachbauen, indem man das eigene `data/`-Archiv (News, Kurse) bis Zeitpunkt t verwendet. **Aber:** Für Fragen vor dem Trainings-Cutoff des Modells bleibt das Gedächtnis ein Leck; darum nur mit Fragen nach dem Cutoff des jeweils getesteten Modells.
- Aufwand: hoch (Korpus-Snapshots)
- Bewertung: 3/5
- Status: nur gelesen

#### prediction-market-agent-tooling (Gnosis)
- Link: https://github.com/gnosis/prediction-market-agent-tooling | Lizenz: **LGPL-3.0** (geprüft; als Bibliothek nutzbar, Änderungen an ihr selbst müssen offengelegt werden) | Sterne/letzter Commit: 65 ★ / 2026-04-22 (geprüft)
- Was es kann: Werkzeuge zum Benchmarken, Deployen und Überwachen von Wettmarkt-Agenten (Manifold, Polymarket, Omen).
- Nutzen für die Arena: Vergleichsvorlage für einen Benchmark-Lauf „Agent vs. Marktpreis auf Manifold/Polymarket“. Die Arena hat eigene Adapter; Nutzen eher gering.
- Aufwand: mittel
- Bewertung: 2/5
- Status: geprüft (Repo/Lizenz)

#### Profit Mirage / FinLake-Bench / FactFin
- Link: https://arxiv.org/abs/2510.07920 | Lizenz: Code ungeprüft | Sterne/letzter Commit: ungeprüft
- Was es kann: Zeigt, dass Rücktest-Gewinne von LLM-Agenten nach dem Wissens-Cutoff verschwinden. Laut Sekundärquelle fällt der Sharpe um 51–62 % (unbestätigt), und GPT-4o beantwortet historische Richtungsfragen zu > 85 % richtig, was auf Auswendiglernen hindeutet. Dazu FinLake-Bench (2.000 historische QA mit Gedächtnis-Proben und kontrafaktischen Labels) und FactFin (kontrafaktische Störungen).
- Nutzen für die Arena: Begründung für die Vorwärtstest-Regel und für eine **Gedächtnisprobe vor jedem Rücktest-Experiment**, falls die Arena je Rücktests macht (z. B. für TimesFM/Kronos-Baselines ohne LLM sind Rücktests unkritisch).
- Aufwand: gering
- Bewertung: 3/5
- Status: nur gelesen

#### „The Memorization Problem: Can We Trust LLMs' Economic Forecasts?“ (Lopez-Lira, Tang, Zhu)
- Link: https://arxiv.org/abs/2504.14765 · SSRN https://papers.ssrn.com/abstract=5217505 | Lizenz: – | Sterne: –
- Was es kann: Belegt, dass Prognosen vor dem Cutoff nicht von Erinnerung zu trennen sind. Die Anweisung „ignoriere Wissen nach Datum X“ wirkt nicht, und Maskieren hilft nicht, weil LLMs Firmen und Daten aus minimalem Kontext rekonstruieren.
- Nutzen für die Arena: Direkte Regel: **keine „So-tun-als-ob-Datum“-Prompts** und keine anonymisierten Rücktests als Ersatz für den Vorwärtstest. Gilt auch für das Opus-Wochen-Review: Wenn es Strategien anhand vergangener Wochen „rücktestet“, sind die Ergebnisse verdächtig, sofern die Woche vor dem Cutoff liegt. Für die laufende Arena (Okt. 2026) ist das nur relevant, wenn ältere Daten eingespielt werden.
- Aufwand: gering
- Bewertung: 4/5
- Status: nur gelesen (Suchzusammenfassung)

#### „Detecting Lookahead Bias in LLM Forecasts“ (Gao, Jiang, Yan) – Lookahead Propensity
- Link: https://arxiv.org/abs/2512.23847 | Lizenz: – | Sterne: –
- Was es kann: Statistischer Test. Je Firma und Datum wird eine reine Datums-Erinnerungsfrage gestellt; daraus wird die Wahrscheinlichkeit geschätzt, dass das Modell den Ausgang kennt (**LAP**). In der Genauigkeits-Regression zeigt ein positiver Interaktionsterm LAP × Prognose eine Verseuchung an. LAP fällt nach dem Cutoff auf ≈ 0.
- Nutzen für die Arena: Billiger Diagnose-Test, falls Liga-Modelle mit unbekanntem bzw. späterem Cutoff dazukommen (Gratis-Modelle mit unklarer Dokumentation). Stichprobenartig Fragen zu Ereignissen der letzten Wochen stellen, um zu sehen, ob das Modell sie „kennt“. Kennt ein Modell Ausgänge *vor* dem Entscheidungszeitpunkt, kann das im Vorwärtstest nicht passieren; wohl aber bei Märkten, deren Ereignis schon stattgefunden hat und die nur noch auf Auflösung warten. Das ist legitimes Wissen, verzerrt aber den Brier gegen den Markt (siehe Methoden: Filter `ts < ereignis_zeit`).
- Aufwand: gering–mittel
- Bewertung: 3/5
- Status: nur gelesen (Abstract)

#### Chronologically Consistent LLMs (ChronoBERT/ChronoGPT)
- Link: https://arxiv.org/abs/2502.21206 | Lizenz: Paper CC BY 4.0; Modelle/Code ungeprüft | Sterne: ungeprüft
- Was es kann: Modelle, die zu jedem Zeitpunkt nur bis dahin verfügbare Texte kennen. Für Rücktests sind sie damit lookahead-frei. Befund: Der Lookahead-Bias ist bei ihrer Aufgabe (News → Tagesrendite) moderat.
- Nutzen für die Arena: Option für einen **lookahead-freien Rücktest-Baseline-Fonds** (News-Sentiment → Signal) als ehrliche Nicht-LLM-Agent-Referenz. Für die Haupt-Arena unnötig.
- Aufwand: mittel–hoch (Modelle laden; CPU-tauglich ungeprüft)
- Bewertung: 2/5
- Status: nur gelesen

#### FINSABER („Can LLM-based Financial Investing Strategies Outperform the Market in Long Run?“)
- Link: https://github.com/waylonli/FINSABER · Paper https://arxiv.org/abs/2505.07078 | Lizenz: Apache-2.0 (geprüft) | Sterne/letzter Commit: ungeprüft / 2026-09-17 (geprüft)
- Was es kann: Rücktest-Rahmen über 20 Jahre und mehr als 100 Titel. Befund: Berichtete LLM-Vorteile schrumpfen bei breiterem Universum und längerem Zeitraum deutlich (Survivorship- und Data-Snooping-Bias). LLMs sind in Bullenmärkten zu vorsichtig und verlieren in Bärenmärkten überproportional.
- Nutzen für die Arena (konkret): (1) Auswertung **nach Marktregime** (Bulle/Bär/Seitwärts, z. B. nach BTC-200-Tage-Linie) auf der Seite zeigen. (2) Klassische, risikobewusste Regeln (z. B. Momentum/Volatilitäts-Targeting) als zusätzlichen **Vergleichsfonds ohne KI** aufnehmen; das ist laut FINSABER der härtere Gegner als der Zufallsaffe.
- Aufwand: gering (Regime) / mittel (Regel-Fonds)
- Bewertung: 4/5
- Status: geprüft (Repo/Lizenz), Paper nur gelesen

#### quantstats
- Link: https://github.com/ranaroussi/quantstats | Lizenz: Apache-2.0 (geprüft) | Sterne/letzter Commit: 7.767 ★ / 2026-09-27 (geprüft)
- Was es kann: Über 50 Kennzahlen (Sharpe, Sortino, Calmar, Omega, Ulcer, Tail-Ratio, VaR/CVaR, Probabilistic Sharpe, Smart-Sharpe mit Autokorrelations-Abschlag …) und HTML-Tearsheets gegen eine Benchmark.
- Nutzen für die Arena (konkret): Wöchentliche **HTML-Tearsheets je Fonds vs. BTC/SPY** für `reports/` bzw. die Pages-Seite; Sortino/Calmar/CVaR in `kennzahlen()`. Getestet: `qs.stats.sharpe(s, periods=365)` = Handrechnung. Zieht pandas, matplotlib und yfinance nach sich (in Actions unproblematisch).
- Aufwand: gering
- Bewertung: 4/5
- Status: getestet (v0.0.86)

#### empyrical-reloaded
- Link: https://github.com/stefan-jansen/empyrical-reloaded | Lizenz: Apache-2.0 (geprüft) | Sterne/letzter Commit: 131 ★ / 2026-10-26 (geprüft)
- Was es kann: Schlanke, getestete Kennzahlen-Funktionen (Sharpe, Sortino, Alpha/Beta, Max-DD, Capture-Ratios, Rolling-Varianten) auf numpy/pandas.
- Nutzen für die Arena: Leichtgewichtiger als quantstats für `metrics.py`: **Alpha/Beta gegen BTC- und SPY-Vergleichsfonds** (zeigt, ob ein Fonds nur gehebeltes Beta ist) sowie Up-/Down-Capture.
- Aufwand: gering
- Bewertung: 4/5
- Status: getestet (Installation, v0.7.1)

#### pyfolio-reloaded
- Link: https://github.com/stefan-jansen/pyfolio-reloaded | Lizenz: Apache-2.0 (geprüft) | Sterne/letzter Commit: 620 ★ / 2026-10-26 (geprüft)
- Was es kann: Tearsheets inkl. Positions-, Transaktions- und Round-Trip-Analyse sowie Bayes-Tearsheet (alt).
- Nutzen für die Arena: Round-Trip-Analyse, also Gewinn je Trade nach Haltedauer und Instrumentklasse, aus `ledger.jsonl`. Überschneidet sich mit quantstats; nur nehmen, wenn Round-Trip-Statistik gewünscht ist.
- Aufwand: mittel (Datenformat anpassen)
- Bewertung: 3/5
- Status: geprüft (Repo)

#### arch (Kevin Sheppard) – Bootstrap, SPA, Model Confidence Set
- Link: https://github.com/bashtage/arch | Lizenz: University of Illinois/NCSA (BSD-artig, permissiv; geprüft) | Sterne/letzter Commit: 1.654 ★ / 2026-10-30 (geprüft)
- Was es kann: `StationaryBootstrap`/`CircularBlockBootstrap` (Konfidenzintervalle für Zeitreihen mit Abhängigkeit), **Hansen-SPA**, StepM (Romano-Wolf), **Model Confidence Set (MCS)**, dazu GARCH.
- Nutzen für die Arena (konkret): (1) KIs für Sharpe/Rendite je Fonds per Block-Bootstrap. (2) **SPA-Test „schlägt irgendein KI-Fonds BTC Buy&Hold nach Korrektur für 12+ Fonds?“** (3) **MCS für die Umschaltung nach dem 14.11.:** statt „bestes Liga-Modell nach Rangliste“ die Menge der statistisch nicht unterscheidbaren Besten bestimmen und darin das billigste/schnellste wählen. Alles getestet.
- Aufwand: gering
- Bewertung: 5/5
- Status: getestet (v8.0.0, StationaryBootstrap + SPA)

#### scoringrules
- Link: https://github.com/frazane/scoringrules | Lizenz: Apache-2.0 (geprüft) | Sterne/letzter Commit: 107 ★ / 2026-06-20 (geprüft)
- Was es kann: Proper Scoring Rules (`brier_score`, `log_score`, CRPS, Energy-Score, viele `logs_*`/`crps_*` für Verteilungen), Backends numpy/JAX/torch.
- Nutzen für die Arena: Brier/Log-Score für Wettmärkte und **CRPS für die TimesFM-/Kronos-Prognosebänder** (Quantile → CRPS), also eine ehrliche Bewertung des Prognose-Werkzeugs, das die Agenten nutzen.
- Aufwand: gering
- Bewertung: 4/5
- Status: getestet (v0.10.0, `brier_score`/`log_score`)

#### properscoring
- Link: https://github.com/properscoring/properscoring | Lizenz: Apache-2.0 (geprüft) | Sterne/letzter Commit: 188 ★ / 2022-10-12, **archiviert** (geprüft)
- Was es kann: CRPS (Ensemble/Gauß), Brier, Threshold-Brier.
- Nutzen für die Arena: Funktioniert noch (installiert), ist aber archiviert → scoringrules vorziehen.
- Aufwand: gering
- Bewertung: 2/5
- Status: getestet (Installation)

#### net:cal (calibration-framework)
- Link: https://github.com/EFS-OpenSource/calibration-framework | Lizenz: Apache-2.0 (geprüft) | Sterne/letzter Commit: 381 ★ / 2026-04-16 (geprüft)
- Was es kann: ECE/MCE/ACE, Reliability-Diagramme, Kalibrierungsverfahren (Histogram Binning, Isotonic, Beta, Platt/Temperature …).
- Nutzen für die Arena: Kalibrierungskurve und ECE je Fonds sowie eine nachträgliche Kalibrierung der Agenten-Wahrscheinlichkeiten. **Achtung:** Die Installation zog im Test so schwere Abhängigkeiten (vermutlich torch), dass sie nach mehreren Minuten abgebrochen wurde. Für die Arena reicht eine Eigenimplementierung (ca. 20 Zeilen) oder `sklearn.calibration` bzw. model-diagnostics.
- Aufwand: mittel (Abhängigkeiten)
- Bewertung: 2/5
- Status: geprüft (Repo/Lizenz); Installation abgebrochen

#### model-diagnostics
- Link: https://github.com/lorentzenchr/model-diagnostics | Lizenz: MIT (geprüft) | Sterne/letzter Commit: 45 ★ / 2026-04-26 (geprüft)
- Was es kann: Reliability-Diagramme nach der **CORP-Methode** (Dimitriadis/Gneiting/Jordan, isotone Regression statt willkürlicher Bins), Score-Zerlegung in Miscalibration/Discrimination/Uncertainty, Bias-Diagnostik.
- Nutzen für die Arena: Bei kleinen n (Dutzende aufgelöste Märkte) ist die binfreie CORP-Zerlegung stabiler als die klassische Murphy-Zerlegung mit 10 Bins. Ideal für die Brier-Kachel der Webseite.
- Aufwand: gering
- Bewertung: 4/5
- Status: geprüft (Repo/Lizenz); Installation nicht getestet (im abgebrochenen Lauf enthalten)

#### pypbo
- Link: https://github.com/esvhd/pypbo | Lizenz: **AGPL-3.0** (geprüft; Copyleft, auch für Netzdienste) | Sterne/letzter Commit: 145 ★ / 2026-07-07 (geprüft)
- Was es kann: Probability of Backtest Overfitting (CSCV), PSR, DSR, MinTRL.
- Nutzen für die Arena: Referenzimplementierung zum Abgleich. Wegen AGPL besser nicht einbinden, sondern die Formeln (unten) selbst implementieren; das wurde in eval_test.py getan.
- Aufwand: gering (als Referenz)
- Bewertung: 2/5
- Status: geprüft (Repo/Lizenz)

---

#### Übernehmbare Methoden

Bezeichnungen: r_t = Tagesrendite, n = Anzahl Tage, SR = mean/sd (nicht annualisiert), γ₃ = Schiefe, γ₄ = Kurtosis (nicht Exzess), Φ = Normal-Verteilungsfunktion.

**1. Probabilistic Sharpe Ratio (PSR)** (Bailey & López de Prado 2012) – Wahrscheinlichkeit, dass der wahre Sharpe > SR* ist:
PSR(SR*) = Φ( (SR − SR*)·√(n−1) / √(1 − γ₃·SR + (γ₄−1)/4·SR²) )
→ Neben jeden Sharpe auf der Seite „PSR(0) = 68 %“ schreiben statt nur „Sharpe 1,15“.

**2. Deflated Sharpe Ratio (DSR)** (Bailey & López de Prado 2014, https://doi.org/10.3905/jpm.2014.40.5.094) – PSR mit SR* = erwarteter Maximal-Sharpe unter H0 bei N Versuchen:
SR*₀ = √V[SR_n] · ( (1−γ)·Φ⁻¹(1 − 1/N) + γ·Φ⁻¹(1 − 1/(N·e)) ), γ ≈ 0,5772 (Euler-Mascheroni)
N = Anzahl Fonds (Claude + Liga + ggf. frühere, abgeschaltete Varianten!), V[SR_n] = Varianz der Sharpes über die Fonds.
Weil die drei Claude-Fonds oft dieselbe Wette eingehen (STATUS: Iran-Waffenruhe), ist das *effektive* N kleiner. Es lässt sich über die Korrelationsmatrix der Tagesrenditen schätzen (z. B. N_eff = Anzahl Cluster oder (Σλ)²/Σλ² der Eigenwerte).
Test: Bester von 12 Null-Fonds nach 60 Tagen: PSR 0,68, **DSR 0,19**.

**3. Minimum Track Record Length (MinTRL)** – Tage, bis SR mit Konfidenz 1−α über SR* liegt:
MinTRL = 1 + (1 − γ₃·SR + (γ₄−1)/4·SR²) · (Φ⁻¹(1−α)/(SR − SR*))²
Für normalverteilte Tagesrenditen, α = 5 %, SR* = 0 und 365 Handelstage/Jahr: annualisierter Sharpe 0,5 → ca. 3.950 Tage; 1 → ca. 990 Tage; 2 → ca. 250 Tage; 3 → ca. 110 Tage (nachgerechnet). **Konsequenz:** Bis Mitte November (ca. 2–3 Wochen Laufzeit) ist *keine* Sharpe-Aussage möglich. Das sollte auf der Seite stehen („Messbar ab Tag X“).

**4. Probability of Backtest Overfitting (PBO, CSCV)** (Bailey, Borwein, López de Prado, Zhu 2015/2017, https://doi.org/10.21314/JCF.2016.322): Renditematrix T×N in S gleich große Zeitblöcke teilen. Für jede Kombination von S/2 Blöcken als „In-Sample“ den besten Fonds n* wählen, dessen relativen Rang ω im Rest bestimmen und λ = ln(ω/(1−ω)) berechnen; PBO = Anteil λ ≤ 0. Für die Arena bedeutet PBO die Wahrscheinlichkeit, dass „der Fonds, der bisher führt“, in der anderen Hälfte der Zeit unter dem Median liegt. Das passt direkt auf die **Modellauswahl nach dem 14.11.** Benötigt ca. 8 Wochen Daten (S = 8 Wochenblöcke → 70 Kombinationen).

**5. Bootstrap-Konfidenzintervalle**
- Renditen: stationärer Block-Bootstrap (Politis-Romano, `arch.bootstrap.StationaryBootstrap`, mittlere Blocklänge ca. 5 Tage), **gepaart**, d. h. dieselben Tagesindizes für alle Fonds, damit Korrelationen erhalten bleiben. Für Differenzen „Fonds − BTC Buy&Hold“ das KI der Differenz berechnen, nicht zwei Einzel-KIs vergleichen.
- Prognosen: Fragen-Bootstrap wie ForecastBench (1999 Wiederholungen, Fragen mit Zurücklegen; Paare Agent/Markt bleiben zusammen). Test: BSS-KI [−0,16; +0,06] bei 150 Fragen.

**6. Datenschnüffel-Korrektur über alle Fonds:** Hansen-SPA (H0: kein Fonds besser als Benchmark) und Model Confidence Set (Hansen, Lunde, Nason 2011). Beide sind in `arch` enthalten, sofort nutzbar und getestet.

**7. Brier, Murphy-Zerlegung, Kalibrierung**
- Brier B = (1/n)Σ(p_i − y_i)²
- Murphy: B = REL − RES + UNC, mit REL = (1/n)Σ_k n_k(p̄_k − ō_k)² (Kalibrierungsfehler, kleiner = besser), RES = (1/n)Σ_k n_k(ō_k − ō)² (Trennschärfe, größer = besser), UNC = ō(1−ō). Bei kleinem n die CORP-Variante (isotone Regression; `model-diagnostics`) statt 10 fester Bins verwenden.
- ECE = Σ_k (n_k/n)|p̄_k − ō_k|; Kalibrierungskurve (p̄_k gegen ō_k) mit Bootstrap-Band.
- Log-Score L = −(1/n)Σ[y·ln p + (1−y)·ln(1−p)]. p auf [0,01; 0,99] klemmen, sonst ruiniert ein einziges p = 0 alles. Der Log-Score bestraft Überzuversicht stärker als der Brier und ist damit der passende zweite Score (vgl. KalshiBench).

**8. Bewertung relativ zum Marktpreis (Kern für Wettmärkte).** Die Arena hat `markt_ja_mitte` je Schätzung.
- **Brier-Skill gegen Markt:** BSS_M = 1 − B_Agent / B_Markt (> 0 = besser als der Preis zum selben Zeitpunkt).
- **Markt-bereinigter Brier (ForecastBench):** Δ_i = B_Agent,i − B_Markt,i; der Mittelwert von Δ ist 0 für jemanden, der den Markt kopiert.
- **Log-Score-Vorteil (entspricht dem Metaculus-Peer-Score mit dem Markt als einzigem Gegner):** 100·(ln p_Agent(y) − ln p_Markt(y)), über Fragen gemittelt.
- **Ökonomischer Wert (Prophet Arena / PolyBench-CWR):** Hypothetischer Einsatz von 1 $ zum Mittelkurs, wenn |p − m| > τ (z. B. τ = 0,05). Gewinn je Frage = sign(p − m)·(y − m)/Preis der gekauften Seite. Variante „Confidence-weighted“: Einsatz ∝ |p − m|. Ein Kelly-Bruchteil wäre f* = (p − m)/(1 − m) für „Ja“. Das trennt Prognosegüte von der Ausführung (Spread/Gebühren), die die Papier-Börse ohnehin separat misst.
- **Wichtige Filter:** (a) nur Schätzungen mit `ts` < Ereigniszeit/Schließzeit; Märkte, deren Ereignis schon passiert ist und nur auf Auflösung wartet, getrennt ausweisen (sonst „Wissensvorsprung“ statt Prognose). (b) Märkte mit zu breitem Spread (z. B. > 10 Punkte) getrennt ausweisen, weil der Mittelkurs dort kein guter Marktkonsens ist. (c) Die erste Schätzung je Markt zählt (so bereits umgesetzt). Zusätzlich die **Selektionsverzerrung** beachten: Agenten wählen selbst, wozu sie schätzen; darum immer gepaart mit dem Markt auf denselben Fragen vergleichen (bereits möglich).

**9. Diebold-Mariano (gepaarter Verlustvergleich):** d_i = L(Agent_i) − L(Markt_i) bzw. L(Agent A) − L(Agent B); DM = d̄ / √(V̂(d̄)). Für unabhängige Fragen V̂ = s²/n; für Tageszeitreihen Newey-West-HAC (Lag ≈ n^{1/3}) bzw. die Harvey-Leybourne-Newbold-Korrektur für kleine n. Test: t = 0,88, p = 0,38 bei 150 Fragen. Ein echter, kleiner Unterschied ist bei dieser Fallzahl nicht nachweisbar.

**10. Minimale Stichprobe bis Signifikanz (Fallzahlplanung)**
- Prognosen: n ≈ ((z₀,₉₇₅ + z₀,₈)·sd(d)/δ)². Mit sd(d) ≈ 0,12 (synthetisch; mit Arena-Daten neu schätzen): δ = 0,02 → ca. 270 Fragen, δ = 0,01 → ca. 1.080, δ = 0,005 → ca. 4.300. Der Arena-Brier wird in den ersten Wochen also nur große Unterschiede zeigen. Das ist ein starkes Argument für die Metaculus-/ForecastBench-Teilnahme als Stichproben-Quelle.
- Renditen: MinTRL (siehe 3).

**11. Kosten-adjustierte Rendite pro API-€**
- Netto-PnL = PnL_USD − API-Kosten_EUR·FX (Fonds mit 10.000 € Start)
- Netto-Rendite = Netto-PnL / Start
- **Effizienz = PnL je API-€** sowie Brier-Verbesserung gegen Markt je 1.000 Prognose-Calls
- „Break-even-Edge“: Mindest-Überrendite pro Jahr, die die API-Kosten deckt = (API-€/Tag·365)/Kapital. Bei 0,73 €/Tagesrunde für 3 Fonds sind das ca. 0,9 % p. a. je 10.000-€-Fonds; bei 12 €/Tag Deckel ca. 15 % p. a. für alle drei zusammen. Gut sichtbar machen.

**12. Weitere sinnvolle Ergänzungen der Kennzahlen**
- Sharpe mit Stichproben-sd (ddof = 1) statt `pstdev`.
- Lo-(2002)-Korrektur bei autokorrelierten Tagesrenditen (quantstats „smart sharpe“).
- Sortino, Calmar, CVaR 95 %.
- Alpha/Beta gegen BTC und SPY (empyrical): Ist ein Fonds nur gehebeltes BTC-Beta?
- Auswertung nach Regime (FINSABER).
- Harvey-Liu-Haircut als Alternative zur DSR (Bonferroni/Holm/BHY auf die Sharpe-t-Werte, https://doi.org/10.3905/jpm.2015.42.1.013), Formel ungeprüft nachgelesen, Methode bekannt.
- Brier-Index 100·(1 − √B) für die Anzeige.

**13. Datenleck-Schutz im Vorwärtstest (Checkliste)**
- Die Arena nutzt append-only JSONL plus Zeitstempel. Als Beweis gegenüber Dritten dient die **GitHub-Push-Zeit** (serverseitig) des öffentlichen Repos; die Commit-Zeit ist vom Autor fälschbar. Optional einen täglichen SHA-256 über `prognosen.jsonl`/`ledger.jsonl` in den Commit-Text bzw. einen Tag schreiben.
- Keine Rücktests mit LLM-Entscheidungen, keine „Tu so, als wäre heute X“-Prompts (Lopez-Lira et al.).
- Vergleichsfonds und TimesFM/Kronos dürfen rückgetestet werden, weil kein LLM-Gedächtnis beteiligt ist. TimesFM/Kronos-Gewichte können aber selbst auf Kursen bis zu ihrem Trainings-Cutoff trainiert sein; Rücktests über diesen Zeitraum sind ebenfalls verdächtig.
- Kennzahlen nur aus Daten mit `ts` ≤ Auswertungszeit; Auflösungen erst nach dem offiziellen Settlement zählen (bereits umgesetzt).
- Den Modell-Cutoff je Liga-Modell in `config.json` dokumentieren; bei unbekanntem Cutoff einen LAP-Kurztest (Gao/Jiang/Yan) machen.

**14. Teilnahme an öffentlichen Turnieren als Trainingsfeld**
- Metaculus FutureEval (Herbst 2026 läuft, Einstieg jederzeit) plus MiniBench (zweiwöchentlich, schnelles Feedback), über `forecasting-tools`/`metac-bot-template` in einer eigenen Action.
- FutureX wöchentliche Challenge (HF).
- ForecastBench-Fragensätze (CC BY-SA) intern beantworten und scoren.
- Erkenntnisse (Kalibrierungsfehler, Überzuversicht) fließen per Kalibrierungs-Korrektur und Notizbuch-Lektionen zurück in die Handelsfonds. Die Credits von Metaculus können das Budget entlasten.

---

_Verworfene Kandidaten dieser Kategorie: siehe [ANHANG-verworfen.md](ANHANG-verworfen.md), Abschnitt „2. Benchmarks, Evaluation, Schutz vor Lookahead“._

### Top-Empfehlungen dieser Kategorie

1. **Schneller Gewinn – „Ehrliche Rangliste“ (ca. 1 Tag):** In `metrics.py` PSR, DSR (N = Anzahl Fonds, ggf. effektives N), MinTRL („messbar ab Tag X“) und Block-Bootstrap-KIs (arch, NCSA-Lizenz) ergänzen und auf der Seite als Fehlerbalken zeigen. Dazu ein Hansen-SPA-p-Wert „KI-Fonds vs. BTC Buy&Hold“. Ohne das ist jede Rangliste vor ca. 1.000 Tagen (bei Sharpe 1) Rauschen, wie bei nof1.
2. **Schneller Gewinn – Marktrelative Prognose-Kennzahlen (wenige Stunden):** Aus den vorhandenen Daten (`p_ja`, `markt_ja_mitte`) berechnen: BSS gegen Markt, markt-bereinigter Brier (ForecastBench-Logik: Kopierer = 0), Log-Score-Vorteil, ökonomischer Wert (Prophet Arena/CWR), Murphy/CORP-Zerlegung (model-diagnostics, MIT), ECE und Kalibrierungskurve, Brier-Index 100·(1 − √B). Filter: `ts` < Ereigniszeit, breite Spreads getrennt. Diebold-Mariano bzw. Fragen-Bootstrap für p-Werte.
3. **Großer Hebel – Metaculus-FutureEval/MiniBench als Trainingsfeld (2–3 Tage):** Eigener Workflow mit `forecasting-tools` (MIT). Ein Arena-Agent bzw. ein Liga-Gratismodell beantwortet Turnierfragen (Herbst 2026 läuft, Einstieg jederzeit). Das bringt Hunderte unabhängig gescorte Prognosen pro Saison (die Stichprobe, die der Arena fehlt), einen externen Vergleich und eventuell kostenlose LLM-Credits. Ergänzend: FutureX wöchentlich und ForecastBench-Fragensätze intern.
4. **Großer Hebel – Modellwahl nach dem 14.11. statistisch absichern:** Die Umschaltung „bestes Liga-Modell“ per Model Confidence Set bzw. PBO statt Rangplatz entscheiden. Unter den nicht unterscheidbaren Besten das kostengünstigste wählen, dazu Kosten-Effizienz (PnL je API-€, Break-even-Edge) anzeigen.
5. **Mittelfristig – Versuchsdesign (AMA/FINSABER):** Architektur (Persönlichkeit/Rollen) und Modell faktoriell trennen und per Fixed-Effects zerlegen. Einen regelbasierten, risikobewussten Vergleichsfonds (Momentum + Vol-Targeting) als härteren Gegner als den Zufallsaffen hinzufügen. Ergebnisse nach Marktregime ausweisen.


---

## 3. Zeitreihen-Foundation-Modelle und Basislinien

## Recherche Kategorie 3: Zeitreihen-Foundation-Modelle und klassische Basislinien

Stand: 2026-10-30. Lizenzen der Gewichte habe ich über die Hugging-Face-Metadaten bzw. die LICENSE-Dateien geprüft, Sterne über die GitHub-Suche.
Hinweis zu den Sternen: Das Feld „updated_at“ der GitHub-Suche ändert sich auch bei neuen Sternen und ist deshalb nur ein grober Hinweis auf Aktivität, kein exaktes Datum des letzten Commits.

### Kategorie: Zeitreihen-Foundation-Modelle (TSFM) und klassische starke Basislinien

**Ausgangslage im Projekt.** `scripts/prognosen.py` lässt TimesFM 2.5 (200M) und Kronos-small alle 6 h auf CPU laufen (Workflow `prognosen.yml`, timeout 25 min). Die Eingabe sind die BTC/ETH/SOL-Stundenschlusskurse, Kontext max. 512 bzw. 400. Ausgegeben werden Median, p10 und p90 für 24 h. `arena/forecast.py` ergänzt einen Bootstrap der Stundenrenditen und weist darauf hin, dass Foundation-Modelle im Vorwärtstest oft keinen Vorteil bringen.

**Kernaussage der Recherche und der eigenen Tests.**

1. **Rendite-Richtung:** Kein getestetes TSFM schlägt auf BTC-Stundenkerzen den Random Walk. Die Literatur von 2025/26 kommt zum gleichen Ergebnis: Skill gegenüber dem Random Walk ist bei Renditen „sparse and small“ (Größenordnung 10⁻³).
2. **Quantile und Unsicherheit:** Im eigenen Mini-Test sind die Bänder aller TSFMs bei 24 h zu schmal. Die 10–90-%-Bänder decken nur 66–76 % statt 80 % ab. Ein einfacher Random Walk mit Normalverteilung oder eine GARCH-Variante liegt beim Pinball-Loss gleichauf oder besser.
3. **Volatilität:** Am ehesten können TSFMs hier etwas beitragen. Laut Brini 2026 (50 Assets, realisierte Varianz) schlägt aber nur IBM TTM das Log-HAR-Modell, und das nur knapp (QLIKE −1,3 bis −1,8 %).
4. **Kronos in der aktuellen Arena-Konfiguration (Kronos-small, 8 Pfade → p10/p90):** Das Band ist viel zu schmal (~1 % statt ~4,5 %), die Abdeckung liegt bei 14 % statt 80 %. Dazu kommen große, falsche Median-Ausschläge (Pinball +50 % ggü. RW). Das ist der wichtigste konkrete Befund für das Projekt.

Fazit: Als „zweite Meinung“ für die Agenten sind TSFM-Bänder vertretbar. Sie sollten aber neben GARCH- bzw. Random-Walk-Bändern angezeigt und laufend nachkalibriert werden, z. B. mit Conformal-Skalierung auf Basis der eigenen Treffer-Historie.

---

#### TimesFM 2.5 (google, 200M) – bereits im Einsatz
- Link: https://huggingface.co/google/timesfm-2.5-200m-pytorch · https://github.com/google-research/timesfm | Lizenz (Code/Gewichte): Apache-2.0 / Apache-2.0 | Sterne/letzter Commit: ~34,8k / aktiv (GitHub-Suche: updated 2026-10-30)
- Was es kann: Univariate Prognose mit einem kontinuierlichen Quantilkopf, Kontext bis 16k. 231M Parameter laut HF. **Eigene Messung (CPU, 4 Kerne):** Laden 28,9 s, Inferenz für 50 Reihen × 24 h 11,1 s, Spitzen-RAM 2,1 GB. Download 883 MB (gemessen).
- Nutzen für die Arena: Bereits integriert. Im Mini-Test schlechter als der Random Walk (Pinball +6 %, Abdeckung 70 % statt 80 %).
- Aufwand: 0 (läuft). Das PyPI-Paket `timesfm` hat die Version 3.0.2 und enthält sowohl `TimesFM_2p5_200M_torch` als auch `TimesFM3Torch`. Die Gewichte entscheiden über die Lizenz.
- Bewertung: 3/5 (behalten, aber nachkalibrieren)
- Status: getestet

#### TimesFM 3.0 (google, ~331M)
- Link: https://huggingface.co/google/timesfm-3.0-pytorch | Lizenz (Code/Gewichte): Code Apache-2.0 (PyPI `timesfm` 3.0.2) / **Gewichte „TimesFM Non-Commercial License v1.0“ („non-commercial and non-production use“)** | Sterne: s. o.
- Was es kann: Laut fev-bench auf Platz 4 (Skill ggü. Seasonal Naive ca. 49 %). Laut t0-Paper führt es GIFT-Eval zero-shot an (CRPS 0,456, MASE 0,667).
- Nutzen für die Arena: Höchstens marginal. Die Lizenz schließt zudem ausdrücklich „production use“ aus.
- Aufwand: niedrig (gleiches Paket)
- Bewertung: 1/5 (Lizenz; die bisherige Entscheidung bestätigt sich)
- Status: geprüft (Lizenztext gelesen)

#### TimesFM 2.0 (500M)
- Link: https://huggingface.co/google/timesfm-2.0-500m-pytorch | Lizenz: Apache-2.0 / Apache-2.0
- Was es kann: Vorgänger von 2.5 mit 499M Parametern, also größer und langsamer.
- Nutzen für die Arena: keiner gegenüber 2.5
- Aufwand: niedrig
- Bewertung: 1/5
- Status: geprüft (nur Metadaten)

#### Chronos-Bolt (amazon; tiny 9M / mini 21M / small 48M / base 205M)
- Link: https://huggingface.co/amazon/chronos-bolt-tiny (sowie -mini, -small, -base) · https://github.com/amazon-science/chronos-forecasting | Lizenz: Apache-2.0 / Apache-2.0 | Sterne: ~6,2k / aktiv (updated 2026-10-30)
- Was es kann: Direkte Quantilausgabe (q0.1–q0.9), sehr schnell. Parameterzahlen für mini, small und base laut Modellkarten (ungeprüft); tiny laut HF 8,7M. **Messung tiny:** 34 MB Download, Laden 8,7 s, Inferenz 50×24 h 0,10 s, RAM 0,65 GB. **Messung small:** 183 MB, Laden 10,3 s, Inferenz 0,37 s, RAM 0,83 GB.
- Nutzen für die Arena: Billigster TSFM-Kandidat. Im Test bei Pinball und Abdeckung aber schlechter als der Random Walk (tiny +7 %, small +6 %).
- Aufwand: sehr niedrig (`pip install chronos-forecasting`, 5 Zeilen Code)
- Bewertung: 2/5
- Status: getestet

#### Chronos-2 (amazon, 120M)
- Link: https://huggingface.co/amazon/chronos-2 · arXiv 2510.15821 | Lizenz: Apache-2.0 / Apache-2.0
- Was es kann: Univariat und multivariat, mit Kovariaten (z. B. ETH und SOL als Ko-Reihen, Funding-Raten). Auf fev-bench etwa Platz 5 (Skill ca. 47 %). **Messung:** 456 MB, Laden 14,4 s, Inferenz 1,7 s, RAM 1,15 GB.
- Nutzen für die Arena: Im Test das schlechteste Quantilmodell (Pinball +12,5 % ggü. RW, t-Wert +3,1). Eine Stärke liegt in den Kovariaten, die univariat nicht genutzt wurden.
- Aufwand: niedrig
- Bewertung: 2/5
- Status: getestet (univariat)

#### Moirai 1.1 / Moirai-MoE / Moirai 2.0 (Salesforce)
- Link: https://huggingface.co/Salesforce/moirai-2.0-R-small · https://github.com/SalesforceAIResearch/uni2ts | Lizenz: Code Apache-2.0 (uni2ts, laut Repo, ungeprüft) / **Gewichte CC-BY-NC-4.0 (alle Varianten, auch moirai-agent)** | Sterne: ~1,6k
- Was es kann: Moirai 2.0-small hat 11,4M Parameter, Moirai-MoE-small 117M. Im Rendite-Benchmark von Noguer i Alonso & Franklin 2026 erreichte Moirai 2.0 zusammen mit TimesFM 2.5 den besten mittleren Rang, allerdings mit Skill von nur ca. 10⁻³.
- Nutzen für die Arena: Lizenz nicht kommerziell. Für ein öffentliches Hobby-Repo vermutlich zulässig, aber klar als NC zu kennzeichnen.
- Aufwand: mittel (uni2ts hat viele Abhängigkeiten)
- Bewertung: 1/5
- Status: geprüft (Lizenzen via HF)

#### Lag-Llama
- Link: https://huggingface.co/time-series-foundation-models/Lag-Llama · https://github.com/time-series-foundation-models/lag-llama | Lizenz: Apache-2.0 / Apache-2.0 | Sterne: ~1,6k / Gewichte seit 05/2024 nicht aktualisiert
- Was es kann: 2,4M Parameter, probabilistisch (Student-t). In der Volatilitätsstudie von Brini 2026 schlägt es Log-HAR nicht.
- Nutzen für die Arena: veraltet, auf Benchmarks deutlich überholt
- Aufwand: mittel (GluonTS-Abhängigkeit)
- Bewertung: 1/5
- Status: nur gelesen

#### IBM Granite TTM (TinyTimeMixer r2 / r3)
- Link: https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2 · https://huggingface.co/ibm-granite/granite-timeseries-ttm-r3 · https://github.com/ibm-granite/granite-tsfm | Lizenz: Apache-2.0 / Apache-2.0 | Sterne: ~0,9k / aktiv
- Was es kann: Winzig (r2 0,8M, r3 1,4M Parameter), liefert nur Punktprognosen. Feinabstimmung auf CPU in Minuten möglich. **Messung r2:** 3,1 MB Download, Laden 6,0 s, Inferenz 0,05 s, RAM 0,64 GB. Fallstrick: Die r2-Variante für Kontext 512 braucht `freq_token` (stündlich = 7), sonst bricht der Aufruf mit „Expecting freq_token“ ab.
- Nutzen für die Arena: Für Preisrichtung nutzlos (Punkt-MAE 1,09 % vs. 0,87 % beim RW). **Laut Literatur aber das beste TSFM für realisierte Volatilität:** Brini 2026 zeigt, dass es als einziges Log-HAR auf allen Horizonten schlägt. Sinnvoll wäre also TTM auf einer *Volatilitätsreihe* (z. B. tägliche realisierte Varianz aus 5-min- oder 1-h-Renditen), nicht auf dem Preis.
- Aufwand: niedrig (Paket `granite-tsfm`). Ein Volatilitätsaufbau kostet zusätzlich etwa einen halben Tag.
- Bewertung: 3/5 (für Volatilität)
- Status: getestet (auf Preisen; Volatilität nur gelesen)

#### IBM Granite FlowState r1
- Link: https://huggingface.co/ibm-granite/granite-timeseries-flowstate-r1 (arXiv 2508.05287) | Lizenz: Apache-2.0 / Apache-2.0
- Was es kann: State-Space-Modell mit 9,1M Parametern, frequenzinvariant. Im GIFT-Eval-Umfeld stark für seine Größe (laut IBM, ungeprüft).
- Nutzen für die Arena: wie TTM, eher für Volatilität; klein und CPU-tauglich
- Aufwand: niedrig bis mittel (granite-tsfm)
- Bewertung: 2/5
- Status: geprüft (Metadaten)

#### IBM Granite PatchTST-FM r2 und Granite-Ensemble r1
- Link: https://huggingface.co/ibm-granite/granite-timeseries-patchtst-fm-r2 · https://huggingface.co/ibm-granite/granite-timeseries-ensemble-r1 | Lizenz: PatchTST-FM **OpenMDW-1.0** (permissive Modell-Lizenz) / Ensemble Apache-2.0
- Was es kann: PatchTST-FM hat 385M Parameter. Das Ensemble steht im GIFT-Eval-Leaderboard oben (CRPS 0,423), ist dort aber als „agentic“ markiert und **mit Test-Leakage = Yes**.
- Nutzen für die Arena: zu groß bzw. zu komplex für den Nutzen
- Aufwand: mittel
- Bewertung: 1/5
- Status: geprüft (Metadaten, Leaderboard-Ausschnitt)

#### Kronos (NeoQuasar; mini 4,1M / small 24,7M / base 102M) – bereits im Einsatz (small)
- Link: https://github.com/shiyu-coder/Kronos · https://huggingface.co/NeoQuasar/Kronos-small · Paper arXiv 2508.02739 (AAAI) | Lizenz: MIT / MIT | Sterne: ~44k / aktiv
- Was es kann: Tokenisiert OHLCV-Kerzen und generiert sie autoregressiv; Pfade werden gesampelt. Laut Paper +93 % RankIC ggü. dem besten TSFM und 9 % niedrigerer MAE bei Volatilität (eigene Angaben der Autoren). **Messung Kronos-mini:** 400 Pfade (50 Ursprünge × 8) in 290 s, **RAM-Spitze 3,8 GB** im Batch. **Messung Kronos-small:** 111 MB Download. 400 Pfade im Batch brauchten 1642 s bei 5,9 GB RAM. Wie in der Arena (8 Einzelaufrufe) sind es 22 s pro Reihe bei 0,6 GB RAM.
- Nutzen für die Arena: **Befund:** p10/p90 aus 8 Pfaden ist systematisch zu eng. Kronos-mini deckte bei h=24 nur 36 % statt 80 % ab (Bandbreite 1,35 % vs. 4,5 % beim RW). **Kronos-small, das die Arena nutzt, schnitt am schlechtesten ab:** Abdeckung 14 %, Pinball +50 % ggü. RW (t = +2,9), Median-MAE 1,16 % vs. 0,87 %. Der Median weicht im Mittel 1,7 % vom letzten Preis ab (TimesFM 0,35 %, Toto 0,27 %). Kronos-small gibt also selbstsichere, aber falsche Richtungsaussagen. In der Gegenprobe exakt wie in der Arena: Bandbreite ~1 %, 0 von 6 Treffern im Band. Empfehlung: mindestens 32–64 Pfade, die Abdeckung beobachten und das Band nachskalieren, oder das Band ganz aus GARCH/RW nehmen und Kronos nur als Pfad-/Richtungsindikator zeigen.
- Aufwand: läuft bereits; Anpassung klein
- Bewertung: 2/5 (in der jetzigen Form irreführend; Band reparieren oder abschalten)
- Status: getestet (mini, small, plus Gegenprobe im Arena-Modus)

#### Datadog Toto 2.0 (4m / 22m / 313m / 1B / 2.5B) und Toto 1.0
- Link: https://huggingface.co/Datadog/Toto-2.0-22m · https://github.com/DataDog/toto · arXiv 2605.20119 | Lizenz: Apache-2.0 / Apache-2.0 (Paket `toto-models` bzw. `toto-2`) | Sterne: ~0,6k / aktiv
- Was es kann: Multivariat, liefert 9 Quantile. Die großen Varianten sind bei GIFT-Eval und TIME vorne. **Wichtig: `toto-models` braucht Python ≥ 3.12** (die Arena nutzt 3.11). **Messung 4m:** 16 MB, Laden 8,7 s, Inferenz 0,13 s, RAM 0,55 GB. **Messung 22m:** 84 MB, Laden 11,4 s, Inferenz 0,25 s, RAM 0,68 GB.
- Nutzen für die Arena: **Bestes TSFM im Mini-Test** (Pinball nur +2–2,5 % über RW, nicht signifikant, t ≈ +0,7 bis +1,0). Toto2-22m kam mit 76 % am nächsten an die Soll-Abdeckung von 80 %. Klein und schnell.
- Aufwand: niedrig, aber Python-Upgrade auf 3.12 im Workflow nötig
- Bewertung: 3/5
- Status: getestet (4m, 22m)

#### NX-AI TiRex (35M, xLSTM) und TiRex-2 (82M)
- Link: https://huggingface.co/NX-AI/TiRex · https://huggingface.co/NX-AI/TiRex-2 · https://github.com/NX-AI/tirex · https://github.com/NX-AI/tirex-2 | Lizenz: **TiRex (Code `tirex-ts` und Gewichte): NXAI Community License** (Llama-3-ähnlich; Pflichtvermerk „Built with technology from NXAI“, kommerzielle Lizenz erst ab 100 Mio. € Umsatz) / **TiRex-2 Gewichte: Apache-2.0** (Code-Lizenz von tirex-2 nicht geprüft) | Sterne: tirex ~0,3k, tirex-2 ~0,16k
- Was es kann: Starke Kurz- und Langfrist-Quantilprognosen. Auf fev-bench liegt TiRex-2 ungefähr auf Platz 8. TiRex-2 unterstützt Kovariaten und Streaming. **Messung TiRex (v1):** 135 MB, Laden 11 s, Inferenz 3,5 s, RAM 0,83 GB.
- Nutzen für die Arena: Im Test Pinball +5,6 % ggü. RW, Abdeckung 66 %. TiRex-2 habe ich nicht getestet; die Installation läuft laut README über Pixi bzw. git (ungeprüft per pip).
- Aufwand: niedrig (v1) / mittel (v2)
- Bewertung: 2/5
- Status: TiRex getestet; TiRex-2 geprüft

#### Sundial (THUML, 128M)
- Link: https://huggingface.co/thuml/sundial-base-128m · https://github.com/thuml/Sundial | Lizenz: Apache-2.0 (Gewichte); Code laut Repo, ungeprüft | Sterne: ~0,2k
- Was es kann: Generatives Modell (Flow-Matching), sampelt Pfade; läuft über transformers mit `trust_remote_code`. Laut Brini 2026 bei der Volatilität für h=1 etwa gleichauf mit Log-HAR (0,998).
- Nutzen für die Arena: gering; `trust_remote_code` ist ein Sicherheitsminus
- Aufwand: niedrig bis mittel
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### Time-MoE (50M aktiv / 113M gesamt)
- Link: https://huggingface.co/Maple728/TimeMoE-50M · https://github.com/Time-MoE/Time-MoE | Lizenz: Apache-2.0 / Apache-2.0 | Sterne: ~1k
- Was es kann: Mixture-of-Experts, nur Punktprognose; Gewichte seit 10/2024 nicht aktualisiert
- Nutzen für die Arena: keine Quantile, auf Benchmarks überholt
- Aufwand: niedrig (`trust_remote_code`)
- Bewertung: 1/5
- Status: geprüft

#### Timer / Timer-XL (THUML, 84M)
- Link: https://huggingface.co/thuml/timer-base-84m · https://github.com/thuml/Large-Time-Series-Model | Lizenz: Apache-2.0 | Sterne: ~1k
- Was es kann: Generatives Punktmodell; im GIFT-Eval-Changelog 2025 auf Rang 36
- Nutzen für die Arena: gering
- Aufwand: niedrig
- Bewertung: 1/5
- Status: geprüft

#### TabPFN-TS (Prior Labs)
- Link: https://github.com/PriorLabs/tabpfn-time-series · https://huggingface.co/Prior-Labs/TabPFN-v2-reg | Lizenz: Code Apache-2.0 (laut Repo, ungeprüft) / **TabPFN v2: „Prior Labs License“ (Apache-2.0 mit Attributionspflicht); TabPFN 2.5 und 3: Nicht-kommerziell („non-commercial and non-production use“)** | Sterne: ~0,5k
- Was es kann: Prognose als Tabellen-Regression mit beliebigen Merkmalen (Kalender, Funding, Orderbuch). TabPFN-TS-3 liegt auf fev-bench im Mittelfeld der Spitzengruppe.
- Nutzen für die Arena: Interessant, wenn man Merkmale einbringen will. Die aktuellen Gewichte sind aber NC, und ohne GPU ist es langsam (ungeprüft).
- Aufwand: mittel
- Bewertung: 1/5
- Status: geprüft (Lizenzen)

#### MOMENT (CMU AutonLab; small 38M / base / large)
- Link: https://huggingface.co/AutonLab/MOMENT-1-small · https://github.com/moment-timeseries-foundation-model/moment | Lizenz: MIT / MIT | Sterne: ~0,9k
- Was es kann: Mehrzweckmodell für Klassifikation, Anomalien und Imputation; Prognose nur mit Fine-Tuning-Kopf
- Nutzen für die Arena: Höchstens für Anomalie- oder Regime-Erkennung. Zero-shot-Prognose ist nicht vorgesehen.
- Aufwand: mittel
- Bewertung: 1/5
- Status: geprüft

#### YingLong (50M; laut HF 36M Parameter)
- Link: https://huggingface.co/qcw2333/YingLong_50m | Lizenz: Gewichte **CC-BY-4.0** (Attribution, kommerziell erlaubt); Code ungeprüft
- Was es kann: Nicht-kausales Modell mit verzögertem Chain-of-Thought; sehr wenige Downloads (617)
- Nutzen für die Arena: gering, kaum verbreitet
- Aufwand: mittel (`trust_remote_code`)
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### Timestral (Mistral AI; 5M / 28M / 123M / 209M) – neu (10/2026)
- Link: https://huggingface.co/mistralai/Timestral-28M · https://github.com/mistralai/timestral | Lizenz: **„Modified MIT“ für die Gewichte: keine Rechte bei mehr als 20 Mio. $ Monatsumsatz** (für ein Hobby-Repo unkritisch, aber nicht OSI) / Code ungeprüft | Sterne: ~1k (Repo seit 15.10.2026)
- Was es kann: 21 Quantile, Kontext bis 32k, Kovariaten. Laut Modellkarte GIFT-Eval CRPS 0,446 (209M) bzw. 0,461 (28M) und fev-bench SQL-Skill 48,4 (28M). Auf fev-bench liegt 209M auf Platz 2.
- Nutzen für die Arena: Spannend wegen 5M und 28M (CPU-tauglich). Finanz-Nutzen unbekannt. Installation nur über git, nicht von PyPI.
- Aufwand: niedrig bis mittel
- Bewertung: 2/5
- Status: geprüft (Lizenztext gelesen), nicht getestet

#### t0-beta (The Forecasting Company, 256M) – neu (09/2026)
- Link: https://huggingface.co/theforecastingcompany/t0-beta · arXiv 2609.24559 | Lizenz: Apache-2.0 (Gewichte laut HF) / Code ungeprüft
- Was es kann: Multivariat mit bekannten zukünftigen Kovariaten. Laut Paper Platz 3 auf GIFT-Eval (CRPS 0,474); auf fev-bench liegt t0-gamma auf Platz 3.
- Nutzen für die Arena: Zu groß, um für den erwartbar geringen Finanz-Nutzen auf CPU zu laufen. ONNX-int8-Varianten gibt es.
- Aufwand: mittel
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### statsforecast (Nixtla): AutoETS / AutoARIMA / Theta
- Link: https://github.com/Nixtla/statsforecast | Lizenz: Apache-2.0 | Sterne: ~5k / aktiv
- Was es kann: Schnelle klassische Modelle mit Prognoseintervallen. **Messung:** AutoETS (season 24) auf log-Preis für 50 Fenster 22,9 s, AutoARIMA 7,2 s, RAM ~0,26 GB, ohne Download.
- Nutzen für die Arena: **Im Test gleichauf mit dem RW** (Pinball −0,1 %, AutoETS-Abdeckung 78 %). Das ist im Grunde ein Random Walk mit gut geschätzter Varianz. Taugt als ehrliche Basislinie neben den TSFMs.
- Aufwand: sehr niedrig
- Bewertung: 4/5 (als Basislinie)
- Status: getestet (AutoETS, AutoARIMA; Theta nur gelesen)

#### arch (GARCH, Kevin Sheppard)
- Link: https://github.com/bashtage/arch | Lizenz: NCSA (BSD-artig) | Sterne: ~1,7k / aktiv
- Was es kann: GARCH, EGARCH, GJR, HAR-Mittelwert, Student-t, Bootstrap, Model Confidence Set. **Messung:** GARCH(1,1)-t für 50 Fenster 1,2 s, RAM 0,22 GB.
- Nutzen für die Arena: **Erste Wahl für Volatilität und VaR-Bänder.** Im 24-h-Test etwas zu breit (Abdeckung 84 %), beim Pinball gleichauf mit dem RW. Die Stärke liegt bei kurzen Horizonten und Regimewechseln; das bilden 50 Ursprünge kaum ab. Dazu kommt die Vergleichsinfrastruktur (`arch.bootstrap.MCS`, SPA-Test).
- Aufwand: sehr niedrig
- Bewertung: 5/5
- Status: getestet

#### darts (unit8)
- Link: https://github.com/unit8co/darts | Lizenz: Apache-2.0 | Sterne: ~9,6k
- Was es kann: Einheitliche API für Statistik-, ML- und TSFM-Modelle (u. a. Chronos und TimesFM als Wrapper), Backtesting
- Nutzen für die Arena: Bequem für Backtests, für 2–3 Modelle aber überdimensioniert
- Aufwand: mittel (große Abhängigkeiten)
- Bewertung: 2/5
- Status: nur gelesen

#### sktime
- Link: https://github.com/sktime/sktime | Lizenz: BSD-3-Clause (laut Repo, ungeprüft) | Sterne: ~10k
- Was es kann: Umfassendes Framework mit vielen Schätzern, darunter Wrapper für TSFMs
- Nutzen für die Arena: wie darts
- Aufwand: mittel
- Bewertung: 2/5
- Status: nur gelesen

#### neuralforecast (Nixtla)
- Link: https://github.com/Nixtla/neuralforecast | Lizenz: Apache-2.0 | Sterne: ~4,3k
- Was es kann: NHITS, NBEATS, PatchTST, TFT und weitere mit Quantilverlust; Training pro Datensatz nötig
- Nutzen für die Arena: Eigenes Training auf Krypto-Renditen wäre möglich. Die Literatur (Rahimikia et al. 2025) zeigt Gewinne vor allem beim Training auf großen Finanzdaten, was in GitHub Actions kaum machbar ist.
- Aufwand: hoch
- Bewertung: 1/5
- Status: nur gelesen

#### NeuralProphet
- Link: https://github.com/ourownstory/neural_prophet | Lizenz: MIT (laut Repo, ungeprüft) | Sterne: ~4,3k
- Was es kann: Trend, Saisonalität und AR-Terme
- Nutzen für die Arena: Kurse haben keine verlässliche Saisonalität; kaum Nutzen
- Aufwand: mittel
- Bewertung: 1/5
- Status: nur gelesen

#### Benchmarks: GIFT-Eval und fev-bench (Stand 30.10.2026)
- GIFT-Eval: https://huggingface.co/spaces/Salesforce/GIFT-Eval · https://github.com/SalesforceAIResearch/gift-eval (~0,3k Sterne). Das Live-Leaderboard ließ sich per Scraper nur bruchstückhaft lesen. Oben stehen agentische bzw. Ensemble-Einträge wie Granite-Ensemble (CRPS 0,423, **Test-Leakage Yes**) und STRIDE (Google, CRPS 0,423, kein Code). Bei den zero-shot-TSFMs laut Modellkarten und Papers: Timestral-209M 0,446, TimesFM-3 0,456, t0-beta 0,474, Toto-2.0-22m 0,496 (Selbstangaben, nicht unabhängig geprüft). Der Bereich Econ/Fin ist klein und enthält keine Krypto-Stundendaten (ungeprüft).
- fev-bench: https://huggingface.co/spaces/autogluon/fev-bench (100 Aufgaben, Metrik SQL). Reihenfolge laut Paarvergleich-Grafik (ausgelesen, Werte ≈ Skill ggü. Seasonal Naive): TimeH2O-v1 (~51 %, **nicht kommerziell, gated**), Timestral-209M (~50 %), t0-gamma (~49 %), TimesFM-3 (~49 %, NC), Chronos-2 (~47 %), iAmTime, t0-beta, TiRex-2, Toto-2.0-2.5B, TabPFN-TS-3, TS-ICL, Toto-2.0-22m, TiRex, TimesFM-2.5 (~43 %), CITRAS-FM, Chronos-Bolt (~39 %). **Wichtig:** Die Abstände zwischen den Spitzenmodellen sind klein (wenige Prozentpunkte), und kein Benchmark misst Finanzrenditen sinnvoll.

#### Literatur zu TSFM in Finance (Auswahl)
- Noguer i Alonso & Franklin (2026): „Pretrained Time-Series Foundation Models for Financial Return Forecasting“, https://arxiv.org/abs/2606.27100. Getestet: TimeGPT, TimesFM-2.5, Moirai-2.0, Chronos, Chronos-2 auf 5 US-Aktien, täglich, h=20. Ergebnis: Skill ggü. Random Walk nur ~10⁻³; DM-Test nur in 2 von 10 Fällen signifikant. „useful low-data priors, not reliable sources of alpha“. Nur MAE, keine Quantile.
- Brini (2026): „Forecasting Realized Volatility with Time Series Foundation Models“, https://arxiv.org/abs/2607.05291. 9 TSFMs gegen HAR-Familie, 50 Assets. Nur **TTM** schlägt Log-HAR stabil (QLIKE-Verhältnis 0,982–0,987). Gepoolte Mittelwerte täuschen, weil wenige volatile Assets sie treiben. Kombination TTM + Log-HAR ist am robustesten.
- Rahimikia, Ni & Wang (2025): „Re(Visiting) Time Series Foundation Models in Finance“, https://arxiv.org/abs/2511.18578. Zero-shot und Fine-Tuning schwach bei täglichen Überrenditen; nur Pretraining auf Finanzdaten bringt Gewinne.
- Goel et al. (2025), https://arxiv.org/abs/2505.11163: TimesFM für realisierte Volatilität ist zero-shot eine brauchbare Basis, inkrementelles Fine-Tuning ist aber nötig.
- Kronos-Paper (Shi et al., 2025, AAAI): https://arxiv.org/abs/2508.02739. Pretraining auf über 12 Mrd. Kerzen; laut Autoren deutlich bessere RankIC und 9 % niedrigere Volatilitäts-MAE. Selbstauskunft, Krypto ist enthalten.
- FinTSB (Tongji, 2025/26): https://arxiv.org/abs/2502.18834 · https://github.com/TongjiFinLab/FinTSB. Benchmark mit Transaktionskosten und Marktregimen. Die zentrale Warnung: Fehlende Kosten blähen Ergebnisse auf.
- Ein Paper mit dem exakten Titel „Are time series foundation models ready for financial forecasting“ habe ich nicht gefunden (ungeprüft, ob es existiert). Am nächsten kommen die Arbeiten oben.
- Blog (nicht begutachtet), Juni 2026: Chronos-2 und TimesFM 2.5 auf Bitcoin waren „worse than ARIMA on every metric“, https://jeromeetienne.github.io/blog/2026-06-15-post-06-pretrained.html. Das passt zum eigenen Test.

---

#### Testergebnisse

**Aufbau (Skripte in `‹Sandbox›/tests/`):**
- `run_model.py MODELL daten.json out.npz` rechnet die Prognosen, `mess.py` misst Wandzeit und Spitzen-RSS des Kindprozesses, `bewerte.py` wertet aus.
- Daten: 3001 öffentliche Coinbase-Stundenkerzen BTC-USD vom 27.06. bis 30.10.2026.
- 50 rollende, nicht überlappende Ursprünge im Abstand von 24 h (die letzten ~50 Tage). Kontext 512 h (Kronos 400 OHLCV-Kerzen wie im Arena-Skript), Horizont 24 h, Quantile 0,1–0,9.
- Metriken: Pinball-Loss in % vom letzten Preis (Mittel über 9 Quantile und h=1–24 ≈ CRPS-Näherung), MAE des Medians, Abdeckung des 10–90-%-Bands bei h=24 (Soll 80 %), Trefferquote der Richtung des Medians bei h=24, gepaarter t-Wert der Pinball-Differenz je Ursprung ggü. Random Walk (negativ = besser), Spearman-Korrelation zwischen Bandbreite und |realisierter 24-h-Rendite| als Volatilitäts-Skill.
- Hardware: Container mit 4 vCPU, 15 GB RAM, Python 3.11 (Toto: 3.12), torch 2.11/2.15 CPU.

**Basislinien:**
- rw-normal: Median = letzter Preis, σ = Standardabweichung der 512 Stundenrenditen × √h
- bootstrap: wie `arena/forecast.py`, 400 Pfade
- garch: GARCH(1,1), Student-t, Mittelwert 0
- autoets / autoarima: statsforecast auf log-Preis

**Leistung und Ressourcen:**

| Modell | Download | Laden (s) | Inferenz 50 Reihen × 24 h (s) | RAM-Spitze (MB) | Lizenz Gewichte |
|---|---|---|---|---|---|
| rw-normal | – | 0 | 0,7 | 107 | – |
| bootstrap (Arena) | – | 0 | 0,8 | 107 | – |
| GARCH(1,1)-t (arch) | – | 1,1 | 1,2 | 222 | NCSA |
| AutoETS (statsforecast) | – | 1,9 | 22,9 | 257 | Apache |
| AutoARIMA (statsforecast) | – | 1,5 | 7,2 | 258 | Apache |
| Chronos-Bolt-tiny | 34 MB | 8,7 | 0,10 | 647 | Apache |
| Chronos-Bolt-small | 183 MB | 10,3 | 0,37 | 827 | Apache |
| Chronos-2 | 456 MB | 14,4 | 1,74 | 1146 | Apache |
| TiRex (v1) | 135 MB | 11,0 | 3,5 | 833 | NXAI Community |
| IBM TTM-r2 | 3,1 MB | 6,0 | 0,05 | 643 | Apache |
| Toto-2.0-4m | 16 MB | 8,7 | 0,13 | 547 | Apache |
| Toto-2.0-22m | 84 MB | 11,4 | 0,25 | 678 | Apache |
| TimesFM 2.5 (wie Arena) | 883 MB | 28,9 | 11,1 | 2092 | Apache |
| Kronos-mini (8 Pfade/Ursprung = 400 Pfade) | 32 MB (16 + 16 Tokenizer-2k) | 2,6 | 289,6 | 3846 | MIT |
| Kronos-small (8 Pfade/Ursprung) | 111 MB (95 + 16 Tokenizer) | 2,8 | 1641,6 | 5908 | MIT |

**Prognosegüte (50 Ursprünge, BTC-USD 1 h, h=24):**

| Modell | Pinball h1-24 (% Preis) | Pinball h=24 | MAE Median h1-24 | Abdeckung 10-90 h=24 | Breite 10-90 h=24 | Richtung h=24 | t-Wert vs RW (neg=besser) | Spearman Breite~|Rendite| h=24 |
|---|---|---|---|---|---|---|---|---|
| autoarima | 0.3436 | 0.5332 | 0.855 | 76% | 4.63 | 46% | -0.12 | +0.01 |
| autoets | 0.3437 | 0.5335 | 0.865 | 78% | 4.50 | 58% | -0.57 | +0.02 |
| bootstrap | 0.3515 | 0.5534 | 0.882 | 76% | 4.42 | 50% | +1.22 | -0.22 |
| chronos-2 | 0.3870 | 0.6004 | 1.001 | 70% | 3.87 | 40% | +3.10 | +0.06 |
| chronos-bolt-small | 0.3651 | 0.5838 | 0.911 | 66% | 3.91 | 56% | +1.57 | -0.12 |
| chronos-bolt-tiny | 0.3691 | 0.5622 | 0.929 | 68% | 3.75 | 52% | +2.37 | +0.07 |
| garch | 0.3442 | 0.5424 | 0.866 | 84% | 5.31 | n/a | +0.11 | -0.13 |
| kronos-mini | 0.3840 | 0.6190 | 0.879 | 36% | 1.35 | 56% | +1.59 | -0.02 |
| kronos-small | 0.5178 | 0.9597 | 1.164 | 14% | 1.34 | 52% | +2.91 | +0.08 |
| rw-normal | 0.3440 | 0.5338 | 0.866 | 78% | 4.54 | n/a | +0.00 | +0.00 |
| timesfm-2.5 | 0.3652 | 0.5715 | 0.925 | 70% | 3.52 | 54% | +1.50 | -0.00 |
| tirex | 0.3633 | 0.5784 | 0.917 | 66% | 3.93 | 48% | +1.79 | +0.03 |
| toto2-22m | 0.3524 | 0.5473 | 0.891 | 76% | 3.97 | 52% | +1.01 | +0.08 |
| toto2-4m | 0.3507 | 0.5498 | 0.883 | 66% | 3.95 | 50% | +0.67 | +0.13 |
| ttm-r2 | 0.5436 | 0.8176 | 1.087 | 0% | 0.00 | 50% | +3.90 | +nan |

*TTM-r2 liefert nur Punktprognosen; seine „Pinball“-Werte sind daher nicht mit den Quantilmodellen vergleichbar. „n/a“ bei der Richtung: Der Median ist identisch mit dem letzten Preis.*

**Gegenprobe Kronos-small exakt wie `scripts/prognosen.py`** (8 einzelne `predict`-Aufrufe, 6 Ursprünge, Skript `tests/kronos_seq.py`): mittlere Bandbreite p10–p90 bei h=24 **0,99 %** (RW: ~4,5 %), Abdeckung **0 von 6**, 22 s pro Reihe (bei 3 Reihen also ~67 s), RAM 0,6 GB. Der Befund ist damit unabhängig vom Batch-Modus bestätigt.

**Interpretation (vorsichtig):**
- Mit n = 50 ist jeder Unterschied unter ~3–5 % Pinball statistisch nicht belastbar (|t| < 2). Belastbar ist nur, dass **Chronos-2 (t = +3,1) schlechter als der Random Walk** war. TTM (t = +3,9) ist nicht vergleichbar, weil es nur einen Punkt liefert.
- Die **Richtung ist Münzwurf**: Trefferquoten von 40–58 % bei n = 50 liegen alle im Zufallsbereich (95-%-Band ≈ 36–64 %).
- **Kalibrierung:** Alle TSFMs liefern zu enge Bänder (66–76 %), Kronos mit 8 Pfaden sehr deutlich. Klassische Varianzschätzer (RW, ETS, ARIMA) liegen bei 76–78 %, GARCH bei 84 %.
- **Volatilitäts-Skill** (Spearman Breite ~ |Rendite|): Bei allen Modellen nahe 0 (−0,22 bis +0,13), auf 50 Punkten also nicht messbar. Für eine echte Volatilitätsbewertung bräuchte es viele Ursprünge (z. B. 1-h-Horizont, Tausende Punkte) oder realisierte Varianz als Ziel.
- Der Zeitraum umfasst nur ~7 Wochen eines Regimes. Ein anderer Zeitraum kann die Reihenfolge ändern.

**Praktische Funde beim Test:**
1. `pip install chronos-forecasting tirex-ts granite-tsfm` zog trotz vorher installiertem CPU-torch ein **CUDA-torch (≈ 3,7 GB extra)** nach, weil eine Abhängigkeit eine andere torch-Version verlangte. Im Workflow sollte man torch pinnen (`pip install torch==X --index-url …/cpu` und danach `pip install … "torch==X"` oder `--extra-index-url` der CPU-Wheels nutzen).
2. Toto 2.0 (`toto-models`) läuft erst ab Python 3.12.
3. TTM-r2 verlangt bei Kontext 512 ein `freq_token`.
4. Kronos im Batch ist RAM-hungrig (3,8 GB für 400 Pfade). In GitHub Actions (7 GB) sollte man in kleineren Batches arbeiten.

_Verworfene Kandidaten dieser Kategorie: siehe [ANHANG-verworfen.md](ANHANG-verworfen.md), Abschnitt „3. Zeitreihen-Foundation-Modelle und Basislinien“._

### Top-Empfehlungen
1. **GARCH-Band (arch) als Pflicht-Basislinie** neben Bootstrap: ~1 s, 0,2 GB, NCSA-Lizenz. Liefert Volatilität und VaR, die die Agenten tatsächlich nutzen können (Positionsgröße, Stopps). Optional HAR auf realisierter Varianz aus 1-h-Renditen.
2. **Kronos-Band reparieren**: Statt 8 eher 32–64 Pfade (gebatcht, `predict_batch`) oder das Band per Conformal-Faktor aus der eigenen Treffer-Historie skalieren. Aktuell deckt das 10–90-Band nur 36 % (mini) bzw. 14 % (small, im Arena-Modus 0/6) ab. Bis zur Reparatur sollte das Kronos-Band den Agenten nicht als p10/p90 gezeigt werden.
3. **Selbst-Evaluation in der Arena einbauen**: Für jede gespeicherte Prognose nach 24 h Pinball und Abdeckung je Modell protokollieren (rollend). Den Agenten dann pro Modell „Trefferquote / Kalibrierung der letzten 30 Tage“ zeigen. So wird ehrlich sichtbar, dass die TSFMs aktuell nicht besser als der Random Walk sind.
4. **Wenn ein drittes TSFM dazukommen soll: Toto-2.0-22m** (Apache, 84 MB, 0,25 s, im Test bestes TSFM; Python 3.12 nötig) oder **Chronos-Bolt-small** (Apache, kein Python-Upgrade). Beide sind billig genug, um TimesFM 2.5 (2 GB RAM, ~40 s) mittelfristig zu ersetzen.
5. **Für Volatilität: IBM TTM-r2/r3** auf einer realisierten Varianz-Reihe testen (Literatur-Favorit, 3 MB, Apache). Nicht auf dem Preis einsetzen.
6. **Torch im Workflow pinnen** (CPU-Wheel), damit neue Pakete kein CUDA-torch nachladen.


---

## 4. Forecasting-Methoden und Wettmarkt-Daten

## Kategorie 4 – Forecasting-Methoden für LLMs & Gratis-Datenquellen für Wettmärkte

### Kategorie: A) Superforecaster-/LLM-Prognosemethoden, B) Wettmarkt-Datenquellen (gratis, legal, nur lesend)

Stand: 2026-10-30. Recherche für die KI-Trader-Arena (nur lesend im Repo, nichts geändert).

**Ausgangslage im Repo (gelesen):** `arena/data/pm.py` nutzt Polymarket Gamma (`/markets`, `/public-search`) + CLOB `/book`, Kalshi `trade-api/v2` (markets, orderbook), PredictIt `marketdata/all`, Manifold `v0/search-markets` + CPMM-Nachrechnung. `arena/agent/prompts.py` (Denkweise „Weitblick“) verlangt ≥3 Thesen, Gegenargument, Kosten, Werkzeug `wahrscheinlichkeit` (P(JA) + Begründung, Brier). Es fehlen: Preisverlauf, Trades/Holder, Basisraten, eine Trennung „eigene Schätzung vor Marktpreis“, Ensemble/Kalibrierung, Kelly-Größe, Diversifikationsregeln.

**Diagnose „alle drei Claude-Fonds setzen auf dieselbe Wette“** (Begründung aus den Funden unten): Gleiches Modell (Sonnet), gleicher System-Prompt (nur Risiko-Parameter unterscheiden sich), **gleicher Schnappschuss** (gleiche Top-Märkte in gleicher Reihenfolge), gleiche Websuche → hochkorrelierte Fehler. Die Forschung (FutureEval Spring 2026: Ensembles helfen nur bei *unterschiedlichen* Mitgliedern; nostreambot nimmt Grok bewusst als „low-correlation“-Mitglied; Panshul trennt Outside-/Inside-View-Agenten) legt nahe: Diversität muss *erzwungen* werden (Rollen, Marktausschnitte, Quellen), sonst ist es ein Fonds in dreifacher Ausführung. Dazu kommt der dokumentierte **Ja-Bias** von LLMs (Schoenegger: Mittel der Modellprognosen signifikant > 50 %, obwohl Ausgänge ~50/50).

**Teststatus:** Endpunkte mit curl aus der Cloud-Sandbox (US-IP, Ohio) getestet; Rohantworten liegen in `‹Sandbox›/test-pm/`. GitHub-Sterne via GitHub-MCP-Suche (30.10.2026); Lizenzen nur, wo eine Quelle sie nennt.

---

## Teil A – Methoden, Bots, Papiere

#### Metaculus forecasting-tools (Python-Paket)
- Link: https://github.com/Metaculus/forecasting-tools | Lizenz/Bedingungen: MIT (README-Badge) | Sterne/letzter Commit: ★87, aktualisiert 2026-10-27
- Was es kann: Rahmen für Prognose-Bots (TemplateBot, MainBot), LLM-Wrapper via litellm, Kostenmanager, `QuestionDecomposer` (Extra „agents“), Fermi-Beispiel mit Code-Ausführung, Metaculus-API-Wrapper. Recherche über Perplexity/Exa (Schlüssel nötig).
- Nutzen für die Arena (konkret): Nicht als Abhängigkeit (zieht Metaculus-Token, Perplexity/Exa, litellm), aber **Prompt-Vorlagen** der offiziellen Template-Bots (z. B. `q2_template_bot.py`) als Vorlage für einen Prompt-Baustein „Prognose“ übernehmen; Idee „Frage zerlegen“ als eigenes Werkzeug.
- Aufwand: gering (nur Prompts übernehmen), hoch (als Paket einbauen)
- Bewertung: 3/5
- Status: nur gelesen (README)

#### Metaculus metac-bot-template
- Link: https://github.com/Metaculus/metac-bot-template | Lizenz: ungeprüft | ★67, 392 Forks, aktualisiert 2026-10-27
- Was es kann: Minimal-Bot, läuft per **GitHub Actions** (Cron) – genau wie die Arena.
- Nutzen: Referenz für den Prompt-Aufbau „Zeitrahmen bis Auflösung → Status quo → Szenario JA → Szenario NEIN → Wahrscheinlichkeit“. Gute, kurze Struktur für `wahrscheinlichkeit`.
- Aufwand: gering
- Bewertung: 3/5
- Status: nur gelesen (Metadaten)

#### Panshul42 Forecasting_Bot_Q2 (Gewinner Metaculus AI Benchmark Q2 2025)
- Link: https://github.com/Panshul42/Forecasting_Bot_Q2 | Lizenz: **AGPL-3.0** (laut README) → Code nicht übernehmen, nur Ideen | Sterne: ungeprüft
- Was es kann: 7-Stufen-Pipeline (Frage analysieren → Suchanfragen → Abruf Google/News/AskNews/Perplexity → Synthese → 5 parallele Prognosen → gewichtetes Mittel). „Ausschuss“: 2× Claude 3.7 Sonnet, 2× o4-mini, 1× o3 (doppelt gewichtet). Einige Agenten werden auf **Outside View** (Referenzklasse), andere auf **Inside View** (Mechanismus) gepromptet.
- Nutzen: Direkt übertragbar auf die 3 Claude-Fonds: Fonds 1 = Outside-View-Spezialist (Basisraten), Fonds 2 = Inside-View (Nachrichten/Kausalität), Fonds 3 = Markt-/Orderfluss-Skeptiker. Erzwingt Diversität statt Gleichschritt.
- Aufwand: gering (Prompt-Rollen)
- Bewertung: 5/5 (als Idee)
- Status: nur gelesen (README; Q2-Bericht https://www.lesswrong.com/posts/Surnjh8A4WjgtQTkZ/)

#### Metaculus FutureEval Spring 2026 – Ergebnisse (GreeneiBot2, nostreambot)
- Link: https://www.lesswrong.com/posts/wZBbDqzfBjYG58CxK/futureeval-spring-results-pros-beat-bots-but-the-gap-is | Bedingungen: Blogpost | –
- Was es kann (Befunde): 7.1.–15.4.2026, 173 Bots, 297 gewertete Fragen. Pro-Team vs. Bot-Team −1,25 (95-%-KI −4,87…2,37, p = 0,247) – Lücke fast weg (Q2 2025 noch −20). Sieger GreeneiBot2: mehrere parallele Recherchen (AskNews, Perplexity, GPT-5-Suche, **Screenshots der Auflösungs-Links**), mehrere Läufe aggregiert. Bestes offenes: nostreambot (MIT): Ensemble über OpenRouter, **Grok als gering korreliertes Mitglied, Median**. Aggregation hilft nur bis ~2–10 Bots, danach schlechter. „Extremisierung/Nachkalibrierung umstritten.“ Stärkster Prädiktor: Modellwahl (GPT-5.4).
- Nutzen: (1) Median über *verschiedene* Modelle der Liga als eigener „Liga-Konsens“-Fonds/-Signal; (2) Werkzeug, das die Auflösungsquelle (resolution source) explizit abruft; (3) keine blinde Extremisierung.
- Aufwand: mittel
- Bewertung: 5/5
- Status: geprüft (Bericht gelesen per Firecrawl)

#### Q2-2025-Bot-Maker-Umfrage (Metaculus)
- Link: https://www.lesswrong.com/posts/Surnjh8A4WjgtQTkZ/q2-ai-benchmark-results-pros-maintain-clear-lead | –
- Was es kann: Befunde: Median/Mittel mehrerer Läufe gehört zu den wirksamsten Praktiken; AskNews/Perplexity häufigste Recherche; LLMs runden auf 5-/10-%-Schritte; ein Teilnehmer **kappt Prognosen** (z. B. 2–98 %) gegen seltene Überzuversicht; Einspeisen von Metaculus-Communityprognosen half einem Teilnehmer *nicht*.
- Nutzen: Clip auf [0,02; 0,98] im Werkzeug `wahrscheinlichkeit` (Brier-Schutz), mehrere Stichproben je Schätzung.
- Aufwand: gering
- Bewertung: 4/5
- Status: geprüft

#### Mantic (Metaculus Cup Sommer 2026)
- Link: https://www.thestar.com.my/tech/tech-news/2026/09/18/ai-startup-mantic-raises-25-million-for-superhuman-forecasting | Lizenz: proprietär
- Was es kann: Laut Presse Platz 8 (Sommer 2025), Platz 4 (Herbst 2025), Sommer 2026 vor allen Menschen (genauer Rang widersprüchlich, ggf. hinter Bot „laertes“). 25 Mio $ Seed.
- Nutzen: Nur Beleg, dass agentische LLM-Prognose inzwischen menschliches Niveau erreicht; keine Methode öffentlich.
- Aufwand: –
- Bewertung: 1/5
- Status: nur gelesen (Presse, Details ungeprüft)

#### Lightning Rod Labs – Foresight (Outcome-RL, Polymarket-Fragen)
- Link: https://huggingface.co/LightningRodLabs/foresight-32B , Papier https://arxiv.org/abs/2505.17989 | Lizenz: ungeprüft (Modellkarte nicht geprüft)
- Was es kann: Qwen3-32B per Outcome-RL auf 10.000 Polymarket-Fragen trainiert; laut Firma besser als Frontier-Modelle bei Brier/ECE/Profit, Top-5 ForecastBench (Jan 2026, selbstberichtet). Kommerzielle API.
- Nutzen: Kandidat für die Modell-Liga (falls Gratis-Zugang über OpenRouter o. Ä. – ungeprüft). 32B auf CPU in Actions unrealistisch.
- Aufwand: hoch
- Bewertung: 2/5
- Status: nur gelesen

#### Halawi et al. 2024 – „Approaching Human-Level Forecasting with Language Models“
- Link: https://arxiv.org/abs/2402.18563 | CC BY 4.0
- Was es kann: Retrieval (Suchanfragen generieren → Artikel bewerten/zusammenfassen) + Begründungs-Prompt + mehrere Stichproben, getrimmter Mittelwert. Brier 0,179 vs. Crowd 0,149 (914 Fragen); **wählt das System selbst aus, wo es prognostiziert (wenn Crowd unsicher), schlägt es die Crowd**; Mittel aus System und Crowd besser als Crowd allein. (Kritik zur Vergleichbarkeit der 0,179 im Alignment Forum.)
- Nutzen: Regel „handle nur, wo der Markt unsicher ist (Preis 0,15–0,85) und du frische Information hast“ – genau dort hatte das LLM Vorteil. Relevanz-Bewertung von Artikeln vor der Synthese.
- Aufwand: gering (Prompt)
- Bewertung: 4/5
- Status: nur gelesen (Abstract/Suchergebnisse)

#### Schoenegger et al. 2024 – „Wisdom of the Silicon Crowd“
- Link: https://arxiv.org/abs/2402.19379 (Science Advances, DOI 10.1126/sciadv.adp1528) | CC BY
- Was es kann: Median von 12 LLMs ≈ 925 Menschen (31 Fragen). **Ja-Bias (Acquiescence)**: Mittel der Prognosen signifikant > 50 %. Zeigt man GPT-4/Claude 2 den menschlichen Median, steigt die Genauigkeit um 17–28 %, aber **einfaches Mitteln** von Mensch und Maschine war noch besser.
- Nutzen: (1) Gegenmaßnahme Ja-Bias: Frage auch negiert stellen („P(NEIN)?“) und mitteln; (2) Marktpreis erst *nach* eigener Schätzung zeigen und dann mechanisch mischen statt das LLM „anpassen“ zu lassen.
- Aufwand: gering
- Bewertung: 5/5
- Status: nur gelesen

#### AIA Forecaster (Bridgewater AIA Labs, Tech-Report 2025)
- Link: https://arxiv.org/abs/2511.07678 | arXiv
- Was es kann: Agentische Suche, Supervisor-Agent versöhnt abweichende Prognosen, **statistische Kalibrierung** gegen LLM-Biases; ForecastBench ≈ Superforecaster. Auf **liquiden Polymarket-Märkten schlechter als der Markt**, aber Ensemble Markt+LLM besser als Markt allein (laut Suchergebnis LLM-Gewicht ≈ 1/3, Regression auf Simplex – Zahl nicht im Volltext geprüft).
- Nutzen: Kernrezept für die Arena: **p_final = Mischung aus Marktpreis und LLM**, LLM-Gewicht klein (~0,3), handeln nur bei Abweichung nach Kosten.
- Aufwand: gering
- Bewertung: 5/5
- Status: geprüft (Abstract), Gewicht ungeprüft

#### Market-Conditioned Prompting (arXiv 2602.21229, „Forecasting Future Language“)
- Link: https://arxiv.org/abs/2602.21229 | arXiv
- Was es kann: Marktwahrscheinlichkeit als Prior in den Prompt, LLM aktualisiert mit Textbelegen; Mischung „MixMCP“ schlägt Markt-Baseline (Mention-Märkte). 70/30-Gewicht nur aus Sekundärquelle.
- Nutzen: Zweistufiges Werkzeug: Schätzung blind → dann Prior zeigen → Update begründen; beide Werte speichern (zwei Brier-Reihen: „blind“ und „markt-konditioniert“) – misst, ob das LLM überhaupt Information beisteuert.
- Aufwand: gering
- Bewertung: 4/5
- Status: nur gelesen

#### ForecastBench (Forecasting Research Institute)
- Link: https://github.com/forecastingresearch/forecastbench , https://www.forecastbench.org | Lizenz: ungeprüft | ★92, aktualisiert 2026-10-29
- Was es kann: Dynamischer, kontaminationsfreier Benchmark (Markt- und Datensatzfragen). Befunde: Turnier-Board 2026 – mehrere Modelle statistisch ununterscheidbar von Superforecastern; Good Judgment kritisiert, dass bei **Marktfragen** die Lücke bleibt (≈0,039 vs. 0,059 bester KI-Wert).
- Nutzen: Realistische Erwartung setzen: auf Märkten mit Preis ist der Markt die harte Messlatte → Brier der Fonds immer **gegen Brier des Marktpreises zum selben Zeitpunkt** vergleichen (Brier-Skill-Score), nicht absolut.
- Aufwand: gering (Metrik)
- Bewertung: 4/5
- Status: nur gelesen

#### Squiggle / squigglepy
- Link: https://github.com/quantified-uncertainty/squiggle (★222), https://github.com/peterhurford/squigglepy (★84, Python) | Lizenz: ungeprüft
- Was es kann: Verteilungen kombinieren (Fermi-Schätzungen mit Unsicherheit, Monte Carlo).
- Nutzen: Ein Werkzeug „fermi“ (Faktoren als Verteilungen 5–95 %, Monte-Carlo → P(Schwelle überschritten)) für Zahl-/Schwellenmärkte (z. B. „Temperatur > X“, „Kurs > Y“). Leichter mit numpy selbst zu bauen als Abhängigkeit.
- Aufwand: mittel
- Bewertung: 3/5
- Status: nur gelesen

#### Polymarket/agents
- Link: https://github.com/Polymarket/agents | Lizenz: ungeprüft (vermutlich MIT) | ★3.806, **archiviert**
- Was es kann: LLM-Agent-Gerüst für Polymarket (Gamma-Client, RAG über Nachrichten, Handel per CLOB).
- Nutzen: Gamma-/Nachrichten-Prompts als Inspiration; archiviert, Handelsteil irrelevant.
- Aufwand: –
- Bewertung: 2/5
- Status: nur gelesen (Metadaten)

#### Gnosis prediction-market-agent(-tooling)
- Link: https://github.com/gnosis/prediction-market-agent (★90), https://github.com/gnosis/prediction-market-agent-tooling (★65, aktualisiert 2026-10-24) | Lizenz: ungeprüft
- Was es kann: Benchmark/Deploy/Monitoring für Wettmarkt-Agenten (Omen, Manifold, Polymarket), inkl. Vergleich von Agenten gegen Marktpreis, Kelly-Strategien.
- Nutzen: Benchmark-Idee „Agent vs. Markt-Referenz“ und Kelly-Implementierung als Vorlage (nicht als Abhängigkeit – Web3-lastig).
- Aufwand: mittel
- Bewertung: 3/5
- Status: nur gelesen (Metadaten)

#### Jon-Becker/prediction-market-analysis (Datensatz)
- Link: https://github.com/Jon-Becker/prediction-market-analysis | Lizenz: ungeprüft | ★3.918, aktualisiert 2026-10-29
- Was es kann: Laut Beschreibung größter öffentlicher Datensatz Polymarket+Kalshi Märkte/Trades.
- Nutzen: **Basisraten** offline berechnen: „Wie oft löst ein Markt mit Preis 0,9 eine Woche vor Schluss JA auf?“ (Favorite-Longshot-Bias je Kategorie) → als Werkzeug `basisrate(kategorie, preis, tage_bis_schluss)`. Einmal offline, Tabelle ins Repo.
- Aufwand: mittel
- Bewertung: 4/5
- Status: nur gelesen (Metadaten)

#### sterlingcrispin/nothing-ever-happens (Meme-Strategie)
- Link: https://github.com/sterlingcrispin/nothing-ever-happens | ★979 | Lizenz: ungeprüft
- Was es kann: Kauft „Nein“ auf allen Nicht-Sport-Märkten.
- Nutzen: **Vergleichsfonds ohne KI** („Immer-NEIN“) neben Zufallsaffe – zeigt, ob die Fonds mehr als den Status-quo-Bias ausnutzen. Spiegelt den Ja-Bias der LLMs.
- Aufwand: gering
- Bewertung: 4/5
- Status: nur gelesen

#### komako-workshop/digital-oracle
- Link: https://github.com/komako-workshop/digital-oracle | ★906 | Lizenz: ungeprüft
- Was es kann: Agent-Skill, der Wahrscheinlichkeiten aus 13 Finanzquellen (Polymarket, Kalshi, CFTC, SEC …) ableitet.
- Nutzen: Ideensammlung für Quellen (CFTC COT); Code ungeprüft.
- Aufwand: –
- Bewertung: 2/5
- Status: nur gelesen (Metadaten)

---

## Teil B – Datenquellen / APIs

#### Polymarket Data-API (Trades, Holder, Open Interest, Activity)
- Link: https://data-api.polymarket.com (Doku https://docs.polymarket.com) | Bedingungen: öffentlich, ohne Schlüssel; Rate-Limit lt. Doku ~1.000 Req/10 s allgemein, /trades 200/10 s (zweite Doku-Version nennt andere Werte; Cloudflare drosselt statt abzulehnen)
- Was es kann: `/trades?limit=` (getestet, 200), `/holders?market=<conditionId>` (getestet, 200 – Top-Halter mit Pseudonym und Menge), `/oi?market=` (getestet), `/activity?user=` (getestet).
- Nutzen: Werkzeug `orderfluss(markt)`: letzte große Trades, Konzentration der Top-Halter, OI-Änderung → beantwortet die Prompt-Frage „Wer bietet dir den Handel an?“. Wale-Signal.
- Aufwand: gering (3 GETs in pm.py)
- Bewertung: 5/5
- Status: getestet

#### Polymarket CLOB prices-history
- Link: https://clob.polymarket.com/prices-history?market=<token_id>&interval=1d&fidelity=60 | öffentlich
- Was es kann: Preisverlauf je Token (getestet: stündliche Punkte).
- Nutzen: `kurs_verlauf` für Wettmärkte auch für nicht gespeicherte Märkte; Momentum/Volatilität vor Ereignis; Kalibrierungsstudien.
- Aufwand: gering
- Bewertung: 5/5
- Status: getestet

#### Polymarket Geoblock-Hinweis
- Link: https://polymarket.com/api/geoblock | –
- Was es kann: Liefert für die Sandbox-IP `{"blocked":true,"country":"US"}`. GitHub-Actions-Runner stehen meist in den USA. Die Daten-Endpunkte antworteten trotzdem (Sperre betrifft laut Doku das Handeln).
- Nutzen: Bestätigt: Arena darf nur lesen; ToS-Abschnitt zu Datennutzung **ungeprüft** – vor Veröffentlichung von Rohdaten prüfen.
- Aufwand: –
- Bewertung: –
- Status: getestet

#### Polymarket WebSocket (CLOB market channel) / Goldsky-Subgraph
- Link: wss://ws-subscriptions-clob.polymarket.com/ws/market ; Goldsky-Subgraphen (Positionen/PnL) | Bedingungen ungeprüft
- Was es kann: Echtzeit-Buch; Subgraph für historische Onchain-Positionen.
- Nutzen: Für 15-Min-Actions kaum nötig (REST reicht). Subgraph erst für Wallet-Analysen.
- Aufwand: mittel/hoch
- Bewertung: 2/5
- Status: ungeprüft

#### Kalshi – Kerzen, Trades, Historie (öffentlich)
- Link: https://api.elections.kalshi.com/trade-api/v2 (Doku https://docs.kalshi.com) | Bedingungen: Marktdaten ohne Login erreichbar; Token-Budget (Basic 200 Lese-Token/s, meist 10 Token/Req – gilt laut Doku für authentifizierte Req.); **ohne Schlüssel sehr schnell 429** (bei 3 Req in ~1 s getestet)
- Was es kann: `/series/{s}/markets/{t}/candlesticks?period_interval=60` (getestet, OHLC + Bid/Ask + OI), `/markets/trades` (getestet), `/historical/cutoff` (getestet: Daten vor 2026-08-31 liegen in `/historical/*`; `/historical/markets` gab 429 → ungeprüft).
- Nutzen: Verlauf + Trades für Kalshi-Märkte; wichtig: **in pm.py Pausen/Backoff ≥1 s je Kalshi-Request**, Abrechnung alter Märkte über `/historical/markets`.
- Aufwand: gering
- Bewertung: 5/5
- Status: getestet (historical teilweise)

#### Manifold API (Bets, Märkte)
- Link: https://docs.manifold.markets/api | Bedingungen: Lesen ohne Auth; 500 Req/min/IP; Bots erlaubt; Scraping außerhalb der API verboten; **Training kommerzieller KI-Modelle mit API-Daten braucht Lizenz** (persönlich/akademisch/nicht kommerziell erlaubt)
- Was es kann: `/v0/bets?contractId=` (getestet), Märkte, Positionen, Kommentare.
- Nutzen: Orderfluss für Manifold-Märkte; Manifold oft als „Zweitmeinung“ zu Polymarket-/Kalshi-Fragen (Cross-Venue-Vergleich).
- Aufwand: gering
- Bewertung: 4/5
- Status: getestet

#### Metaculus API (Community-Prognosen)
- Link: https://www.metaculus.com/api/ (OpenAPI: https://raw.githubusercontent.com/Metaculus/metaculus/main/docs/openapi.yml) | Bedingungen: **Token Pflicht** (getestet: 403 ohne); Community-Prediction laut Spec nur für ~50 Fragen frei, Rest über Antrag/Research-Tier; Nutzungsbedingungen regeln Datenverwendung (KI-Nutzungsklausel nur aus Drittquelle, ungeprüft)
- Was es kann: Fragen, Auflösungen; CP eingeschränkt.
- Nutzen: Mit Gratis-Konto + Token Fragen-Texte/Auflösungskriterien als Basisraten-Quelle; CP als Signal nur eingeschränkt. Erst ToS lesen.
- Aufwand: mittel (Konto, Secret)
- Bewertung: 2/5
- Status: getestet (403), Bedingungen nur gelesen

#### PredictIt marketdata
- Link: https://www.predictit.org/api/marketdata/all/ | Bedingungen: Endpunkt antwortet (getestet, 524 kB). Laut rpredictit-Doku „nur nicht-kommerzielle Nutzung“; laut Drittquelle (Alphascope, 06.10.2026) verbieten die ToS Scraping/Datenextraktion und automatisierten Handel – **ungeprüft, Original-ToS lesen**
- Was es kann: Spitzenpreise aller Kontrakte.
- Nutzen: Bereits in pm.py. Empfehlung: ToS-Lage dokumentieren; Abfragehäufigkeit niedrig halten (TTL ≥ 60 s, ist so).
- Aufwand: –
- Bewertung: 3/5 (rechtlich unklar)
- Status: getestet (Endpunkt), ToS ungeprüft

#### Smarkets public API v3
- Link: https://api.smarkets.com/v3/events/ | Bedingungen: **ungeprüft** (keine Doku-Aussage gefunden)
- Was es kann: Ereignisse/Märkte ohne Login (getestet: Politik-Ereignisse); Preise über `/v3/markets/{id}/quotes/` (nicht getestet).
- Nutzen: Britische Börse mit Politik-/Sportmärkten als zusätzlicher Preis-Referenzpunkt (Cross-Venue-Konsens).
- Aufwand: mittel
- Bewertung: 3/5
- Status: getestet (Events), ToS ungeprüft

#### Betfair Exchange API (Delayed Key)
- Link: https://betfair-developer-docs.atlassian.net | Bedingungen: Delayed-Key gratis, aber **Betfair-Konto nötig**, Daten 1–180 s verzögert, „nur private Wettzwecke“, kommerzielle Nutzung genehmigungspflichtig; Konto in DE eingeschränkt
- Nutzen: Tiefste Sport-/Politik-Liquidität – aber öffentliche Darstellung im Repo wäre Grauzone.
- Aufwand: hoch
- Bewertung: 1/5
- Status: nur gelesen

#### Limitless Exchange API
- Link: https://api.limitless.exchange/markets/active | Bedingungen: ungeprüft
- Was es kann: Aktive Märkte ohne Login (getestet; viele Kurzfrist-Krypto-Märkte „Up/Down“, Chainlink-Auflösung).
- Nutzen: Gering – Märkte meist Krypto-Kurzfrist; ggf. als Arbitrage-Vergleich zu Polymarket-Kryptomärkten.
- Aufwand: mittel
- Bewertung: 2/5
- Status: getestet

#### Myriad Protocol API
- Link: https://api-v2.myriadprotocol.com/markets | Bedingungen: ungeprüft
- Was es kann: Märkte ohne Login (getestet; erste Antwort ein alter E-Sport-Markt).
- Nutzen: Gering (kleine Liquidität).
- Aufwand: mittel
- Bewertung: 1/5
- Status: getestet

#### Opinion (opinion.trade) OpenAPI
- Link: https://openapi.opinion.trade/openapi/market | Bedingungen: ungeprüft (Doku nennt evtl. API-Key)
- Was es kann: Antwortete ohne Schlüssel (getestet; BNB-Chain-Märkte, viel E-Sport).
- Nutzen: Gering bis mittel; erst Bedingungen prüfen.
- Aufwand: mittel
- Bewertung: 2/5
- Status: getestet

#### pmxt („CCXT für Wettmärkte“)
- Link: https://github.com/pmxt-dev/pmxt , https://pypi.org/project/pmxt/ | Lizenz: MIT (PyPI/Metadaten; LICENSE-Datei ungeprüft) | ★2.187, aktualisiert 2026-10-28, **1.454 offene Issues**
- Was es kann: Einheitliche API für Polymarket, Kalshi u. a.; überwiegend TypeScript mit Python-SDK.
- Nutzen: Könnte pm.py-Adapter ersetzen – aber die eigenen Adapter laufen schon und sind auf das Papier-Orderbuch zugeschnitten; viele offene Issues + TS-Kern = Risiko. Eher als Referenz für neue Venues (Endpunkte abschauen).
- Aufwand: mittel/hoch
- Bewertung: 2/5
- Status: nur gelesen

#### Dome API
- Link: (Quicknode-Listing) https://www.quicknode.com/builders-guide/tools/dome-api-by-dome-inc | Bedingungen: Gratis-Tier laut Listing, Schlüssel nötig, Details ungeprüft
- Nutzen: Normalisierte Historie Polymarket/Kalshi – überflüssig, da direkte APIs reichen.
- Bewertung: 1/5
- Status: ungeprüft

#### Wikipedia Pageviews (Wikimedia REST)
- Link: https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{Artikel}/daily/{von}/{bis} | Bedingungen: frei, **aussagekräftiger User-Agent mit Kontakt Pflicht** (getestet: generischer UA → 429, UA mit Repo-URL → 200)
- Was es kann: Tägliche Aufrufe je Artikel.
- Nutzen: Aufmerksamkeits-Signal (Kandidat, Film, Ereignis) für Märkte wie „Wird X …?“ / Mention-Märkte; günstig.
- Aufwand: gering
- Bewertung: 3/5
- Status: getestet

#### ESPN „site.api“ (inoffiziell)
- Link: https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard | Bedingungen: **inoffiziell, keine Doku/ToS-Freigabe** → rechtlich Grauzone
- Was es kann: Spielpläne/Ergebnisse (getestet, 250 kB).
- Nutzen: Auflösung/Status von Sportmärkten. Wegen fehlender Freigabe nur mit Vorsicht oder gar nicht.
- Bewertung: 2/5
- Status: getestet

#### openfootball/football.json
- Link: https://github.com/openfootball/football.json | Lizenz: laut Projekt Public Domain/CC0 (ungeprüft)
- Was es kann: Spielpläne/Ergebnisse großer Ligen als JSON (getestet EPL 2025/26).
- Nutzen: Basisraten für Fußballmärkte (Heimsieg-Quoten, Tore), legal und gratis; Aktualität per Community (Verzögerung möglich).
- Aufwand: gering
- Bewertung: 3/5
- Status: getestet

#### football-data.org (Free Tier)
- Link: https://www.football-data.org | Bedingungen: Gratis-Schlüssel, ~10 Calls/min, 12 Wettbewerbe, verzögert (Drittquelle), Quoten kostenpflichtig
- Nutzen: Tabellen/Ergebnisse für Fußballmärkte; Secret nötig.
- Aufwand: gering
- Bewertung: 3/5
- Status: nur gelesen

#### The Odds API (Free Tier)
- Link: https://the-odds-api.com | Bedingungen: 500 **Credits**/Monat (Credits je Markt×Region, Historie 10×) – laut Drittquelle (Konkurrent)
- Was es kann: Buchmacher-Quoten vieler Sportarten.
- Nutzen: **Beste Gratis-Referenz für Sport-Wettmärkte**: Buchmacher-Konsens (vig-bereinigt) vs. Polymarket/Kalshi-Preis. 500 Credits reichen nur für sparsame, ereignisgesteuerte Abfragen (z. B. nur gehaltene Sportmärkte).
- Aufwand: gering (Secret)
- Bewertung: 4/5
- Status: nur gelesen

#### Umfragedaten (538-Archiv, FiftyPlusOne, VoteHub, Silver Bulletin)
- Link: https://projects.fivethirtyeight.com/polls/data/ (getestet: 302 – 538 ist eingestellt), Archiv-Spiegel https://datahub.io/fivethirtyeight/congress-generic-ballot , https://fiftyplusone.news/readme | Bedingungen: je Quelle ungeprüft
- Nutzen: Für Wahl-/Zustimmungsmärkte (Approval-Märkte sind häufig). FiftyPlusOne-CSV zuerst prüfen (Aktualität/Lizenz). Silver Bulletin: keine offenen Downloads gefunden.
- Aufwand: mittel
- Bewertung: 2/5
- Status: getestet (538 tot), Rest ungeprüft

---

#### Übernehmbare Methoden

**M1 – Rollen-Diversität gegen Gleichschritt (Ursache „alle setzen dieselbe Wette“)**
Je Claude-Fonds eine *feste Prognose-Rolle* im System-Prompt (zusätzlich zu Risiko):
- Vorsichtig = „Outside View“: zuerst Referenzklasse + Basisrate nennen, Abweichung davon nur mit harter Evidenz (max. ±15 Pp ohne neue Fakten).
- Mittel = „Inside View“: Mechanismus, Akteure, Fristen, Auflösungsquelle direkt prüfen.
- Aggressiv = „Konträr/Orderfluss“: suche Märkte, wo Preis sich ohne Nachricht bewegt hat, prüfe Halter/Trades, Favorite-Longshot-Bias.
Plus **Schnappschuss je Fonds anders sortieren/teilen** (z. B. Fonds k bekommt die Märkte mit Index ≡ k mod 3 zuerst, oder je Fonds andere Kategorien als Startpunkt) und eine **Korrelationsregel**: „Hält ein anderer Arena-Fonds bereits diese Wette, brauchst du ein eigenständiges Argument“ (Info über andere Fonds nur als Anzahl, nicht als Begründung – sonst Herdeneffekt). Messbar: Anteil gemeinsamer Märkte zwischen Fonds je Woche.

**M2 – Blind zuerst, dann Markt (zwei Zahlen speichern)**
Werkzeug `wahrscheinlichkeit` erweitern: `p_blind` (vor Blick auf Preis; Werkzeug `markt_details` könnte optional ohne Preis aufrufbar sein) und `p_final`. Brier für beide sowie für den Marktpreis zum selben Zeitstempel loggen → Brier-Skill-Score `BSS = 1 − Brier_fonds / Brier_markt`. Nur so sieht man, ob die Fonds Information beitragen (ForecastBench/AIA: auf liquiden Märkten ist der Markt meist besser).

**M3 – Mechanische Mischung mit dem Markt (Log-Odds)**
`logit(p) = ln(p/(1−p))`. Kombination:
`p_handel = σ( w·logit(p_llm) + (1−w)·logit(p_markt) )`, w ≈ 0,3 für liquide Märkte (AIA: LLM ≈ 1/3 Gewicht – ungeprüft), w ≈ 0,5 für illiquide/Manifold. Gehandelt wird nur, wenn `p_handel` den **Kaufpreis inkl. Gebühren + Spread** um eine Mindestmarge übersteigt (z. B. 3 Pp). Das Rechnen gehört in Code, nicht ins LLM.

**M4 – Ja-Bias neutralisieren (Schoenegger)**
Im Prompt: „Schätze P(JA) und separat P(NEIN) (umformuliert). Wenn Summe ≠ 100 %, normiere: p = P(JA)/(P(JA)+P(NEIN)).“ Optional den Prompt so formulieren, dass das NEIN-Szenario zuerst ausgeschrieben wird. Zusätzlich Kontrollfonds „Immer-NEIN“ (nothing-ever-happens).

**M5 – Mehrfachstichprobe + Median, Clip**
Für Märkte, auf die ein Fonds handeln will: 3 günstige Haiku-Stichproben (oder Liga-Modelle verschiedener Hersteller) mit Rollen-Prompts → Median als Zweitmeinung; Ensemble nur aus *verschiedenen* Modellen (FutureEval: Gewinne flachen nach 2–10 Mitgliedern ab; gering korrelierte Mitglieder wertvoll). Endwert auf [0,02; 0,98] clippen.

**M6 – Extremisierung nur nach Daten**
Nicht pauschal (FutureEval: umstritten). Nach ≥50 aufgelösten Prognosen je Fonds **Platt-Kalibrierung** fitten: `logit(p_kal) = a·logit(p) + b` per logistischer Regression auf (p, Ausgang); a>1 heißt „zu vorsichtig → extremisieren“, a<1 „überzuversichtlich“. Isotonische Regression erst ab ~200 Punkten. Kalibrierungskurve (10 Bins) auf der Webseite zeigen und dem Fonds im Notizbuch als Lektion zurückspiegeln („Du warst bei 70–80 % nur zu 55 % richtig“).

**M7 – Basisraten-Abfrage**
Werkzeug `basisrate`: (a) eigene Arena-Historie aufgelöster Märkte nach Kategorie/Preisband/Tagen-bis-Schluss, (b) einmalig offline aus Jon-Becker-Datensatz oder Polymarket-`closed=true`-Märkten + prices-history eine Tabelle „Preis x Tage vor Schluss → Trefferquote“. Prompt-Pflicht: „Nenne die Basisrate, bevor du Nachrichten liest.“

**M8 – Fermi-Zerlegung für Schwellenmärkte**
Prompt-Rezept: „Zerlege in 2–4 unabhängige Faktoren, gib je 5 %/95 %-Grenzen; das Werkzeug `fermi` rechnet Monte Carlo (lognormal) und liefert P(Ergebnis > Schwelle).“ Für Kurs-Schwellen (BTC > X am Datum) stattdessen die vorhandenen Optionen-/TimesFM-Daten: risikoneutrale P aus Deribit-Optionen als Referenz.

**M9 – Kelly für binäre Kontrakte (im Code, nicht im LLM)**
Kauf JA zum effektiven Preis c (inkl. Gebühr/Slippage), Glaube p: `f* = (p − c)/(1 − c)`; Kauf NEIN zum Preis c_n: `f* = ((1−p) − c_n)/(1 − c_n)`. Bei Unsicherheit über p: **Bruchteil-Kelly** (Vorsichtig 0,1, Mittel 0,2, Aggressiv 0,35) und p vorher mit M3 Richtung Markt schrumpfen; Deckel durch bestehende Positionslimits. Kapitalbindung berücksichtigen: Rendite annualisieren `(1/c)^(365/Tage) − 1` gegen Alternativrendite – lange Märkte mit 2 % Edge lohnen nicht.

**M10 – Auflösungsquelle prüfen (GreeneiBot2)**
Prompt-Pflicht vor jedem Wettkauf: „Lies die Abrechnungsregel wörtlich, nenne Quelle, Stichtag, Zeitzone und Randfälle (Storno, ‚bis einschließlich‘). Viele Fehlbewertungen sind Regel-Missverständnisse.“

**M11 – Orderfluss-Frage beantworten**
Werkzeug `orderfluss` (Data-API `/trades`, `/holders`, `/oi`; Kalshi `/markets/trades`): „Wenn Top-Halter >40 % halten oder in den letzten 24 h große Gegen-Trades kamen: begründe, warum du mehr weißt.“

**M12 – Selektiv prognostizieren (Halawi)**
Handelsfokus auf Preise 0,15–0,85 mit frischer Information (< 48 h) und Schluss in < 30 Tagen; Extrembereiche (Longshots < 5 %) nur mit Basisraten-Beleg.

_Verworfene Kandidaten dieser Kategorie: siehe [ANHANG-verworfen.md](ANHANG-verworfen.md), Abschnitt „4. Forecasting-Methoden und Wettmarkt-Daten“._

### Top-Empfehlungen
1. **Rollen-Diversität + verschiedene Schnappschuss-Reihenfolge je Claude-Fonds (M1)** – direkte Antwort auf das Gleichschritt-Problem; nur Prompt/Snapshot-Änderung.
2. **Werkzeug `wahrscheinlichkeit` um `p_blind` erweitern und Brier-Skill gegen Marktpreis messen (M2)** – ohne das ist die Brier-Zahl nicht interpretierbar.
3. **Log-Odds-Mischung mit Markt + Bruchteil-Kelly im Code (M3, M9)** – verhindert Überzeugungswetten gegen liquide Märkte.
4. **Ja-Bias-Gegenmittel + Kontrollfonds „Immer-NEIN“ (M4)**.
5. **Neue Daten-Werkzeuge, alle getestet und gratis:** Polymarket `prices-history` + Data-API `/trades` `/holders` `/oi`; Kalshi `candlesticks` + `/markets/trades` (mit Backoff ≥1 s gegen 429; alte Märkte über `/historical/*`).
6. **Basisraten-Tabelle (M7)** aus eigener Historie bzw. Jon-Becker-Datensatz; Prompt-Pflicht „Basisrate zuerst“.
7. **Nach ≥50 aufgelösten Prognosen Platt-Kalibrierung je Fonds (M6)** und Rückmeldung ins Notizbuch.
8. Für Sportmärkte: The Odds API Free Tier (sparsam) + openfootball; für Aufmerksamkeit: Wikipedia-Pageviews (UA mit Kontakt).
9. ToS offen prüfen: PredictIt (möglicherweise Scraping-/Kommerzverbot), Polymarket-Datenklausel, Smarkets, Opinion.

Quellen (Auswahl): https://www.lesswrong.com/posts/wZBbDqzfBjYG58CxK/ · https://www.lesswrong.com/posts/Surnjh8A4WjgtQTkZ/ · https://arxiv.org/abs/2402.18563 · https://arxiv.org/abs/2402.19379 · https://arxiv.org/abs/2511.07678 · https://arxiv.org/abs/2602.21229 · https://arxiv.org/abs/2505.17989 · https://forecastingresearch.substack.com/p/ai-models-have-likely-reached-parity · https://goodjudgment.substack.com/p/what-forecastbench-doesnt-measure · https://docs.polymarket.com/api-reference/rate-limits · https://docs.kalshi.com/getting_started/rate_limits · https://docs.manifold.markets/api · https://raw.githubusercontent.com/Metaculus/metaculus/main/docs/openapi.yml · https://www.alphascope.app/blog/predictit-api · https://betfair-developer-docs.atlassian.net · https://oddspapi.io/blog/the-odds-api-free-tier-limits


---

## 5. Backtesting/Ausführung, Risiko/Portfolio, Signale/Regime

## Kategorie 5: Backtesting/Ausführung, Risikomanagement, Signale/Regime

Stand: 2026-10-30. Repo nur gelesen (arena/exchange/*.py, arena/config.json, arena/metrics.py, arena/watcher.py, arena/data/pm.py, arena/agent/tools.py, DECISIONS.md).
Sterne, Lizenz und letzter Push stammen aus der GitHub-Suche (MCP) vom 30.10.2026. Version und Datum stammen aus der PyPI-JSON-API.
Funktionstests liefen in `‹Sandbox›/test-risk`
(Python 3.11, venv, 350 Stunden-Kerzen BTC/ETH/SOL von Coinbase, 15.10. bis 30.10.2026). Die Skripte liegen unter `…/scratchpad/scripts/t1.py` und `t2.py`.

**Wichtigster Fund vorab (Fehler in der Börse, verifiziert):** Polymarket erhebt inzwischen in vielen Märkten Taker-Gebühren.
Die Arena speichert die Rate zwar (`arena/data/pm.py` Z. 60: `ref.gebuehr_rate` aus `feeSchedule`), `arena/exchange/fees.py` rechnet aber
mit `polymarket_taker = 0.0` aus `config.json`. Die Rate wird also ignoriert. Live-Abfrage der 40 umsatzstärksten Polymarket-Märkte am 30.10.2026:
22 mit rate 0, 8 ohne feeSchedule und **10 mit rate > 0**: Sport `sports_fees_v3` 0,05, `sports_fees_v2` 0,03, Krypto `crypto_fees_v2` 0,07.
Details stehen unten unter A.

---

### Kategorie: A) Backtesting- und Ausführungssimulatoren, Gebührenmodelle

#### Polymarket-Gebührenmodell (Stand Okt. 2026)
- Link: https://docs.polymarket.com/trading/fees, Gamma-API `feeSchedule` | Lizenz: – | Sterne/letzter Commit: –
- Was es kann: Die Docs geben wörtlich an: `fee = C × feeRate × p × (1 − p)`, berechnet in USDC und gerundet auf 5 Nachkommastellen. Laut Docs-Tabelle kosten
  100 Anteile zu 0,50 $ in Krypto 1,75 $, also **3,5 % des Nominals bei p = 0,5**. Taker-Raten nach Kategorie: Crypto 0,07, Sports 0,05, Finance/Politics/Mentions/Tech 0,04,
  Economics/Culture/Weather/Other 0,05, Combos 0,05, **Geopolitics 0**. Maker zahlen nichts und bekommen einen Rebate (15–25 %). Die API liefert je Markt
  `feeSchedule = {rate, exponent, takerOnly, rebateRate}`. Live war überall `exponent: 1`.
  Einige Sekundärquellen nennen Exponenten 0,5 (Economics/Weather) und eine Formel mit zusätzlichem Faktor p. Das ist **ungeprüft und widerspricht dem Docs-Beispiel**.
- Nutzen für die Arena: In `fees.py` den Zweig `venue == "polymarket"` ersetzen durch
  `fs = inst["ref"]; fee = round(qty * fs["gebuehr_rate"] * (preis*(1-preis))**fs.get("gebuehr_exp",1), 5)`.
  Dazu in `pm.py` auch `exponent` speichern. Ohne diese Korrektur sind Sport- und Krypto-Wetten auf Polymarket um bis zu 2,5–3,5 % des Nominals zu billig.
  Zusätzlich gilt: DECISIONS.md behauptet, die Gebühr werde berücksichtigt („nur wenn feeSchedule anderes sagt“). Der Code tut das nicht.
- Aufwand: klein (rund 10 Zeilen plus ein Test)
- Bewertung: 5/5
- Status: geprüft (Live-API und Docs)

#### Kalshi-Gebührenmodell
- Link: https://kalshi.com/docs/kalshi-fee-schedule.pdf (laut Suchergebnis „effective Feb 5, 2026“; ein Sekundärartikel nennt 07/07/2026) | Lizenz: – | –
- Was es kann: Taker `ceil(0,07 × C × P × (1−P))` auf volle Cent. Maker 0,0175 nur in bestimmten Serien. Für S&P-/Nasdaq-Indexmärkte nennen
  Sekundärquellen 0,035 (ungeprüft, das PDF lieferte 429).
- Nutzen für die Arena: `fees.py` ist korrekt für den Standardfall. Bei Indexmärkten ist die Arena eher zu teuer, also konservativ. Optional ließe sich der Koeffizient je Serie konfigurieren.
- Aufwand: sehr klein
- Bewertung: 3/5
- Status: geprüft (Formel), Indexsatz ungeprüft

#### NautilusTrader
- Link: https://github.com/nautechsystems/nautilus_trader | Lizenz: **LGPL-3.0** | ~31.000 Sterne, Push 30.10.2026, PyPI 1.231.0 (Aug. 2026, Python ≥3.12)
- Was es kann: Ereignisgetriebene Rust/Python-Engine mit L1/L2/L3-Büchern, FillModel (`prob_fill_on_limit`, `prob_slippage`), `liquidity_consumption`
  (verbrauchte Tiefe je Stufe bis zum nächsten Daten-Update), Queue-Position-Tracking mit Trade-Daten, Funding/Margin-Konten, Adapter u. a. für Polymarket und Deribit.
- Nutzen für die Arena: Als Abhängigkeit zu schwer. Als **Vorbild** dient vor allem `liquidity_consumption`: In der Arena läuft jede Order (auch mehrere Fonds im selben Tick
  oder mehrere Orders eines Fonds) gegen ein frisch geholtes, unverbrauchtes Buch. Siehe Verbesserungsidee 2.
- Aufwand: Konzept übernehmen ist klein. Integration ist groß und nicht empfohlen.
- Bewertung: 3/5 (als Referenz)
- Status: nur gelesen (Docs-Suche)

#### hftbacktest
- Link: https://github.com/nkaz001/hftbacktest | Lizenz: MIT | ~5.000 Sterne, Push 23.12.2025, PyPI 2.4.4 (Dez. 2025)
- Was es kann: Tick-/L2-/L3-Backtest mit Queue-Positions-Modellen (`power_prob_queue_model(2)`, `log_prob_queue_model2`, `power_prob_queue_model3`)
  und Latenzmodellen (`intp_order_latency` aus gemessenen Latenzen), Rust-Kern mit Numba-Python.
- Nutzen für die Arena: Erst relevant, wenn die Arena **Limit-Orders** einführt. Derzeit gibt es nur Market-Orders gegen das Buch. Dann wären die Queue-Modelle die Vorlage
  für die Füllwahrscheinlichkeit einer ruhenden Order (Anteil des Volumens vor mir, der durch Trades oder Stornos abgebaut wird).
- Aufwand: mittel (Modell nachbauen, kein Paket nötig)
- Bewertung: 2/5
- Status: nur gelesen

#### QuantConnect Lean
- Link: https://github.com/QuantConnect/Lean | Lizenz: Apache-2.0 | ~22.300 Sterne, Push 30.10.2026
- Was es kann: C#-Engine mit sehr sauber getrennten Modellen: FeeModel je Broker (Coinbase-Tier-Gebühren, Kraken usw.), SlippageModel
  (u. a. `VolumeShareSlippageModel` und `MarketImpactSlippageModel` nach Almgren et al.), FillModel und MarginModel.
- Nutzen für die Arena: Referenz für Gebührentabellen (Coinbase-Volumenstufen) und für das Marktimpact-Modell bei synthetischen Büchern (Aktien, PredictIt).
- Aufwand: nur lesen, Formeln übernehmen
- Bewertung: 3/5
- Status: nur gelesen (aus Vorwissen, Modellnamen nicht neu verifiziert)

#### Square-Root-Law / Almgren-Chriss (Marktimpact-Modelle)
- Link: Almgren/Chriss 2000 „Optimal execution of portfolio transactions“; Tóth et al. 2011 „Anomalous price impact and the critical nature of liquidity“ (arXiv:1105.1694) | Lizenz: – | –
- Was es kann: Impact ≈ Y·σ_Tag·√(Q/V_Tag) mit Y ≈ 0,5–1 (empirisch). Almgren-Chriss trennt temporären und permanenten Impact für das Aufteilen einer Order.
- Nutzen für die Arena: Drei Stellen füllen heute **ohne** Tiefe:
  (1) Aktien mit synthetischem Buch 1e6 Stück (`data/stocks.py`),
  (2) ausgelöste Stops und Take-Profits mit einem Buch der Tiefe 1e9 zum Auslösepreis (`watcher._stop_buch`),
  (3) die synthetische Tiefe bei PredictIt.
  Ein Zuschlag `max(slippage_bps, Y·σ·√(Q/V))` mit σ und V aus den vorhandenen Kerzen wäre realistischer. Bei Stops in Kaskaden (Dochte) ist er besonders wichtig.
- Aufwand: klein (rund 20 Zeilen in `book.py` oder `engine.py`)
- Bewertung: 4/5
- Status: nur gelesen (Formel aus Fachliteratur)

#### vectorbt (Open Source) / vectorbt PRO
- Link: https://github.com/polakowo/vectorbt | Lizenz: **Apache-2.0 mit Commons Clause** (keine echte OSS-Lizenz, Verkaufsverbot; die LICENSE.md wurde gelesen) | ~9.600 Sterne, Push 28.10.2026, PyPI 1.2.0 (19.10.2026)
- Was es kann: Vektorisierte Backtests mit Numba, `Portfolio.from_signals` / `from_orders`, Gebühren und Slippage als Prozentsätze.
  PRO ist kostenpflichtig (Abo, privates Repo, nicht auf PyPI) und fällt damit durch den Filter.
- Nutzen für die Arena: Schnelle Sanity-Backtests einfacher Regeln (z. B. „Was hätte ein 50/50-BTC-Halter gemacht?“) als Benchmark in `benchmarks.py`. Für die Orderbuch-Logik ohne Nutzen.
  Wegen der Commons Clause im öffentlichen Repo nur nutzen, nicht vendoren.
- Aufwand: klein, die Abhängigkeit ist aber schwer (Numba/llvmlite rund 170 MB, im Test gemessen über riskfolio)
- Bewertung: 2/5
- Status: geprüft (Lizenz, PyPI)

#### backtrader
- Link: https://github.com/mementum/backtrader | Lizenz: **GPL-3.0** | ~23.600 Sterne, **letzter Push 19.08.2024**
- Was es kann: Klassischer ereignisgetriebener Backtester mit Kommissions-Schemata und Volumen-Füllern (`FixedSize`, `FixedBarPerc`, `BarPointPerc`).
- Nutzen für die Arena: Nur die Idee „Füllung höchstens x % des Kerzenvolumens“ ist nützlich (als Deckel für synthetische Bücher).
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### zipline-reloaded
- Link: https://github.com/stefan-jansen/zipline-reloaded (in der GitHub-Suche heute **nicht auffindbar**, Ursache ungeprüft), PyPI 3.2.1 vom 25.10.2026 | Lizenz: Apache-2.0
- Was es kann: Aktien-Backtester (Quantopian-Erbe) mit `VolumeShareSlippage` (Impact = 0,1·(Anteil Volumen)²) und `PerShare`/`PerDollar`-Kommissionen.
- Nutzen für die Arena: Formelvorlage für den Aktien-Impact. Das Paket selbst ist zu schwer und aktienfixiert.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (PyPI)

#### bt
- Link: https://github.com/pmorissette/bt | Lizenz: MIT | ~3.000 Sterne, Push 25.10.2026, PyPI 1.4.1
- Was es kann: Baumartige Allokations-Backtests (Algo-Stacks: monatlich rebalancieren, Gewichte nach inverser Vola usw.).
- Nutzen für die Arena: Benchmark-Fonds wie „inverse Vola BTC/ETH/SOL monatlich“ als Vergleichslinie in `benchmarks.py`.
- Aufwand: klein
- Bewertung: 2/5
- Status: geprüft (Metadaten)

#### backtesting.py
- Link: https://github.com/kernc/backtesting.py | Lizenz: **AGPL-3.0** | ~9.200 Sterne, Push 05.08.2026, PyPI 0.6.6
- Was es kann: Minimalistischer Einzelinstrument-Backtester mit Bokeh-Plots.
- Nutzen für die Arena: Kaum Nutzen. Wegen AGPL im öffentlichen Repo meiden.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### Jesse
- Link: https://github.com/jesse-ai/jesse | Lizenz: MIT | ~8.700 Sterne, Push 29.10.2026, PyPI 3.5.3
- Was es kann: Krypto-Backtest- und Livetrading-Framework mit Futures, Hebel, Funding (vereinfacht) und Liquidationen.
- Nutzen für die Arena: Referenz, wie Liquidation und Gebühren bei Krypto-Perps modelliert werden. Für die Arena-Börse nicht nötig.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### freqtrade (nur Referenz)
- Link: https://github.com/freqtrade/freqtrade | Lizenz: **GPL-3.0** | ~56.200 Sterne, Push 30.10.2026
- Was es kann: Krypto-Bot mit Backtesting, Hyperopt, FreqAI, Protections (`StoplossGuard`, `MaxDrawdown`, `CooldownPeriod`, `LowProfitPairs`).
- Nutzen für die Arena: Die **Protections** sind gute Vorlagen für Drawdown-Bremsen (siehe Idee 6). Code wegen GPL nicht übernehmen, nur die Idee.
- Aufwand: –
- Bewertung: 2/5 (als Referenz)
- Status: nur gelesen (Vorwissen, Metadaten geprüft)

#### Microsoft qlib
- Link: https://github.com/microsoft/qlib | Lizenz: MIT | ~49.800 Sterne, Push 30.10.2026, PyPI `pyqlib` 0.9.7 (Aug. 2025)
- Was es kann: Quant-Forschungsplattform (Daten, Alpha158-Features, Modelle, Backtest mit Ausführungsstufen und Order-Execution-RL).
- Nutzen für die Arena: Das Alpha158-Feature-Set lässt sich als Ideenliste für Signale nutzen. Die Plattform ist für die Arena zu groß und auf Aktien-Tagesdaten ausgerichtet.
- Aufwand: groß
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### FinRL
- Link: https://github.com/AI4Finance-Foundation/FinRL | Lizenz: MIT | ~16.900 Sterne, Push 25.10.2026, PyPI 0.3.7 (2024)
- Was es kann: RL-Umgebungen für Portfolios (Gym) mit DRL-Agenten.
- Nutzen für die Arena: Kein direkter Nutzen, denn die Arena testet LLM-Agenten und nicht RL. Die PyPI-Version ist veraltet.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### ABIDES / abides-jpmc-public
- Link: https://github.com/jpmorganchase/abides-jpmc-public | Lizenz: in der Suche NOASSERTION (ungeprüft) | 175 Sterne, **archiviert**, letzter Push 22.07.2024
- Was es kann: Agentenbasierter Markt-Simulator (Börse mit Matching, Noise/Value/Momentum-Agenten, Latenz).
- Nutzen für die Arena: Ein Stresstest der Börse mit simulierten Gegenparteien wäre möglich, ist aber archiviert und für die Arena überdimensioniert.
- Aufwand: groß
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### mbt_gym
- Link: https://github.com/JJJerome/mbt_gym | Lizenz: BSD-3-Clause | 182 Sterne, letzter Push 08.01.2024, nicht auf PyPI
- Was es kann: Gym-Umgebungen für modellbasiertes Market-Making und Ausführung (Avellaneda-Stoikov, Almgren-Chriss-Dynamiken).
- Nutzen für die Arena: Saubere Referenz-Implementierung der Almgren-Chriss-Preisdynamik. Ansonsten gibt es keinen Nutzen.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### PyLimitOrderBook (danielktaylor)
- Link: https://github.com/danielktaylor/PyLimitOrderBook | Lizenz: ungeprüft | in der GitHub-Suche nicht gefunden
- Was es kann: Einfaches Price-Time-Matching-Buch in Python (laut Vorwissen).
- Nutzen für die Arena: Die Arena braucht kein Matching, weil sie nur gegen externe Bücher füllt.
- Aufwand: –
- Bewertung: 0/5
- Status: ungeprüft

#### Deribit-Funding-Historie (Datenmodell für Funding)
- Link: https://www.deribit.com/api/v2/public/get_funding_rate_history | Lizenz: öffentliche API | –
- Was es kann: Liefert stündlich `interest_1h`, `interest_8h`, `index_price` und `prev_index_price`. Test vom 30.10. für BTC_USDC-PERPETUAL: `interest_8h` 0,000255, `interest_1h` 1,3e-7.
- Nutzen für die Arena: `engine.funding_buchen` rechnet heute mit der *aktuellen* 8-h-Rate × Stunden × **Einstands**-Nominal, höchstens 6 h je Tick (DECISIONS: bekannte Vereinfachung).
  Exakter wäre es, die Summe der tatsächlichen `interest_1h` der vergangenen Stunden × aktuelles Mark-Nominal zu buchen. Deribit verrechnet Funding kontinuierlich.
- Aufwand: klein
- Bewertung: 4/5
- Status: getestet (API-Aufruf)

---

### Kategorie: B) Risikomanagement und Portfolio

#### Kelly-Varianten (fraktional, unter Parameterunsicherheit, simultane Binärwetten)
- Link: Thorp „The Kelly Criterion in Blackjack, Sports Betting and the Stock Market“; Baker/McHale 2013 „Optimal betting under parameter uncertainty“; Whitrow 2007 „Algorithms for optimal allocation of bets on many simultaneous events“ | Lizenz: – | –
- Was es kann:
  - Binärkontrakt zum Preis q bei eigener Wahrscheinlichkeit p: `f* = (p − q)/(1 − q)`, Gebühren werden in q eingerechnet.
  - **Simultan-Kelly** (Erwartungswert des Log-Vermögens über alle 2^n Ausgänge maximieren) ist kleiner als die Summe der Einzel-Kelly-Anteile.
    **Getestet** mit 4 Wetten (p = .60/.55/.70/.52 bei q = .50/.45/.60/.40): Einzel-Kelly ergibt in Summe 0,83, simultan 0,72 (je Wette 0,171/0,157/0,212/0,177).
  - Unter Unsicherheit über p (Beta-Verteilung) schrumpft Kelly grob mit dem Faktor `(p−q)²/((p−q)²+Var(p))`. Beispiel mit Vorteil 10 pp:
    bei effektiv 10 „Beobachtungen“ Faktor 0,31, bei 30 Faktor 0,56, bei 100 Faktor 0,81. Das ist eine Näherung, nicht exakt nach Baker/McHale.
- Nutzen für die Arena: Ein **Agenten-Werkzeug `positionsgroesse`** in `arena/agent/tools.py`. Eingabe: Markt, p_ja (schon vorhanden über `t_wahrscheinlichkeit`),
  Profil. Es rechnet Ask-Preis inklusive echter Gebühr aus `fees.py`, Einzel-Kelly, simultanes Kelly mit den offenen PM-Positionen und einen Bruchteil je Profil
  (vorsichtig 1/8, mittel 1/4, aggressiv 1/2) und gibt einen USD-Vorschlag zurück, der bereits auf `risk.pruefe_eroeffnung` gekappt ist. Die Kalibrierung
  (Brier aus `metrics.brier`) kann den Bruchteil automatisch senken, wenn ein Fonds schlechter kalibriert ist als der Markt (`brier > brier_markt`).
- Aufwand: klein bis mittel (rund 80 Zeilen, nur numpy/scipy, Simultan-Kelly per Enumeration bis etwa 12 Wetten, darüber Monte Carlo)
- Bewertung: 5/5
- Status: getestet (eigene Implementierung, `scripts/t2.py`)

#### skfolio
- Link: https://github.com/skfolio/skfolio | Lizenz: BSD-3-Clause | ~2.560 Sterne, Push 29.10.2026, PyPI 1.12.5 (29.10.2026)
- Was es kann: Portfolio-Optimierung im scikit-learn-Stil: MeanRisk mit über 20 Risikomaßen (CVaR, CDaR, MaxDD …), HRP/HERC/NCO, Ledoit-Wolf, Szenarien und Stresstests, Kreuzvalidierung.
- Nutzen für die Arena: Ein Werkzeug „Risikobericht“ für Fonds: CVaR des aktuellen Portfolios aus Kursverläufen sowie HRP-Gewichte als Diversifikationsvorschlag.
  Getestet: MinCVaR ergab 100 % BTC (die geringste Tail-Vola), HRP ergab BTC 0,446 / ETH 0,223 / SOL 0,331. Laufzeit 1,2 s.
- Aufwand: klein. Installation 7 s, rund 150 MB zusätzlich (cvxpy, clarabel u. a. auf scikit-learn/scipy).
- Bewertung: 4/5
- Status: getestet

#### Riskfolio-Lib
- Link: https://github.com/dcajasn/Riskfolio-Lib | Lizenz: BSD-3-Clause | ~4.580 Sterne, Push 29.10.2026, PyPI 7.4.0
- Was es kann: Sehr breite Auswahl an Risikomaßen (CVaR, EVaR, CDaR, UCI …), Risk Parity und HRP, Black-Litterman, Plots.
- Nutzen für die Arena: Funktional ähnlich zu skfolio. Getestet: MinCDaR ergab 100 % BTC in 1,3 s.
- Aufwand: **Installation 63 s, rund 670 MB** (u. a. astropy, plotly, scs, Numba/llvmlite). Für GitHub Actions bei jedem Lauf zu schwer.
- Bewertung: 2/5 (skfolio bevorzugen)
- Status: getestet

#### PyPortfolioOpt
- Link: https://github.com/PyPortfolio/PyPortfolioOpt (umgezogen von robertmartin8) | Lizenz: MIT | ~6.130 Sterne, Push 29.10.2026, PyPI 1.6.0 (Feb. 2026)
- Was es kann: Efficient Frontier, Black-Litterman, HRP, Ledoit-Wolf, diskrete Allokation.
- Nutzen für die Arena: Leichtgewichtig. HRP lieferte im Test dieselben Gewichte wie skfolio. Installation 3 s (auf vorhandenem cvxpy).
- Aufwand: klein
- Bewertung: 3/5
- Status: getestet

#### cvxportfolio
- Link: https://github.com/cvxgrp/cvxportfolio | Lizenz: **GPL-3.0** | ~1.320 Sterne, Push 27.04.2026, PyPI 1.5.1 (Juli 2025)
- Was es kann: Mehrperioden-Optimierung **mit Transaktionskosten- und Haltekostenmodellen** (Boyd et al.), Backtest-Simulator mit Spread und Impact (σ·(Q/V)^β).
- Nutzen für die Arena: Das Kostenmodell (`StocksTransactionCost`: a·|Δ| + b·σ·|Δ|^{3/2}/V^{1/2}) ist eine gute Vorlage für Idee 3. Code wegen GPL nicht übernehmen.
- Aufwand: –
- Bewertung: 2/5 (als Referenz)
- Status: nur gelesen

#### Volatilitäts-Targeting mit GARCH bzw. DVOL
- Link: Moreira/Muir 2017 „Volatility-Managed Portfolios“; arch (siehe C) | Lizenz: – | –
- Was es kann: Exposure = min(1, Ziel-Vola / prognostizierte Vola).
  Getestet: GARCH(1,1)-t auf BTC 1h prognostiziert 1,98 % Vola über 24 h, also rund 38 % p. a. Bei einem Ziel von 40 % ergibt das Faktor 1,0. Persistenz 0,82.
- Nutzen für die Arena: In `risk.pruefe_eroeffnung` das Perp-Nominal-Limit (`max_perp_pct × max_hebel`) mit dem Faktor `min(1, Ziel/σ_prognose)` skalieren.
  Ziel-Vola je Profil: vorsichtig 15 %, mittel 30 %, aggressiv 60 %. So erzwingt die Börse in Crash-Phasen automatisch weniger Hebel.
- Aufwand: klein (σ aus DVOL wäre ohne Abhängigkeit sofort verfügbar)
- Bewertung: 4/5
- Status: getestet

#### Drawdown-Bremse (CPPI-artig, freqtrade-Protections als Vorbild)
- Link: Grossman/Zhou 1993 (Drawdown-Constraint); freqtrade Protections | Lizenz: – | –
- Was es kann: Riskobudget ∝ (1 − DD/DD_max). Nach X Stop-Losses in Y Stunden gilt eine Pause.
- Nutzen für die Arena: `risk.py` kennt heute keine Fondshistorie. Vorschlag: Bei Fonds-Drawdown von mehr als 50 % des Profil-Maximums (z. B. vorsichtig −10 %) werden
  `max_position_pct` und `max_hebel` halbiert. Nach drei Stops in 24 h wird für 6 h nicht neu eröffnet. Die Daten dafür liegen schon in `equity.jsonl` und `ledger.jsonl`.
- Aufwand: klein
- Bewertung: 4/5
- Status: nur gelesen (Konzept)

#### Korrelations- und Klumpenrisiko-Kontrolle (innerhalb des Fonds und über Fonds hinweg)
- Link: – | Lizenz: – | –
- Was es kann: Gemessen wurde die Korrelation der 1-h-Renditen über 2 Wochen: **BTC–ETH 0,91, BTC–SOL 0,89, ETH–SOL 0,91**. Praktisch ist das eine Wette.
- Nutzen für die Arena:
  (a) Innerhalb eines Fonds rechnet `risk.py` Einzelpositionen getrennt. Ein Cluster-Limit „Krypto-Beta“ würde Spot + Perp + Optionsdelta
  von BTC/ETH/SOL/… zusammen als BTC-äquivalentes Nominal begrenzen, gewichtet über β zu BTC aus den Kerzen. Hinzu kommen PM-Märkte der Kategorie Krypto (Polymarket `crypto_fees`-Märkte!).
  (b) Über Fonds hinweg ist die Arena ein Wettbewerb, kein Gesamtportfolio. Ein hartes Limit über alle Fonds verfälscht ihn. Besser ist eine **Kennzahl „Gleichlauf“**
  in `metrics.py` (Korrelation der täglichen Fondsrenditen untereinander und Überlappung der Positionen) plus der Hinweis in der Webseite, dass das Ranking bei hohem Gleichlauf
  vor allem Hebel misst. Optional bekommt jeder Agent im Prompt die aggregierte Arena-Position („7 von 9 Fonds sind long BTC“), damit er Konsens bewusst bewerten kann.
- Aufwand: klein bis mittel
- Bewertung: 4/5
- Status: getestet (Korrelationsmessung), Rest Konzept

#### CVaR / Expected Shortfall als Kennzahl
- Link: Rockafellar/Uryasev 2000 | Lizenz: – | –
- Was es kann: Mittlerer Verlust der schlechtesten α % der Tage.
- Nutzen für die Arena: `metrics.kennzahlen` um CVaR95 (historisch, ab etwa 20 Tagen), Sortino und Calmar ergänzen. Das braucht nur numpy, keine Bibliothek.
- Aufwand: sehr klein
- Bewertung: 3/5
- Status: nur gelesen

---

### Kategorie: C) Feature-/Signal-Bibliotheken und Regimeerkennung

#### TA-Lib (ta-lib-python)
- Link: https://github.com/TA-Lib/ta-lib-python | Lizenz: BSD-2-Clause (C-Kern BSD-3) | ~12.300 Sterne, Push 29.10.2026, PyPI 0.8.3 (28.10.2026)
- Was es kann: Rund 150 Indikatoren und Candlestick-Muster in C.
- Nutzen für die Arena: Indikatoren (RSI, ATR, ADX, BBands) für `t_kurs_verlauf` und `t_lage`. ATR dient als Stop-Abstand für den Positionsgrößen-Rechner.
  **Der alte Installationshaken entfällt:** `pip install ta-lib` zog im Test ein Binär-Wheel mit eingebautem C-Kern (9 s, rund 35 MB, kein `apt` nötig). Getestet: RSI 36,0, ATR 640 $.
  Ob es für ARM64 (Oracle) Wheels gibt, ist ungeprüft.
- Aufwand: klein
- Bewertung: 4/5
- Status: getestet (x86_64)

#### pandas-ta (twopirllc)
- Link: https://github.com/twopirllc/pandas-ta | Lizenz: in den PyPI-Metadaten leer (früher MIT) | **in der GitHub-Suche heute nicht auffindbar**, die Seite liefert über den Proxy 403. PyPI 0.4.71b0 (14.09.2025, nur Beta, **Python ≥3.12**)
- Was es kann: Über 150 Indikatoren als pandas-Extension.
- Nutzen für die Arena: Der Pflegezustand ist unklar. Der Maintainer hatte Finanzierungsprobleme angekündigt (Vorwissen, ungeprüft). Seit 2025 gibt es keine stabile Version mehr.
  **Nicht als Abhängigkeit nehmen.**
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (PyPI, GitHub-Suche), Repo-Zustand ungeprüft

#### pandas-ta-classic (Fork)
- Link: https://github.com/xgboosted/pandas-ta-classic | Lizenz: MIT | 461 Sterne, Push 29.10.2026, PyPI 0.9.0 (28.10.2026, Python ≥3.11)
- Was es kann: Gepflegter Community-Fork von pandas-ta mit über 250 Indikatoren.
- Nutzen für die Arena: Ersatz, falls pandas-ta-Syntax gewünscht ist. TA-Lib oder eigene 20 Zeilen numpy reichen aber.
- Aufwand: klein
- Bewertung: 2/5
- Status: geprüft (Metadaten)

#### ta (bukosabino)
- Link: https://github.com/bukosabino/ta | Lizenz: MIT | ~5.250 Sterne, Push 18.03.2026, **letzte PyPI-Version 0.11.0 vom Nov. 2023**
- Was es kann: Reines pandas mit rund 40 Indikatoren.
- Nutzen für die Arena: Ohne C-Abhängigkeit, aber ohne neue Releases. Nur nehmen, wenn TA-Lib auf ARM scheitert.
- Aufwand: klein
- Bewertung: 2/5
- Status: geprüft (Metadaten)

#### finta
- Link: https://github.com/peerchemist/finta | Lizenz: **LGPL-3.0** | **archiviert**, letzter Push 2022
- Bewertung: 0/5 (siehe „Verworfen“)
- Status: geprüft

#### tulipy
- Link: https://github.com/cirla/tulipy | Lizenz: **LGPL-3.0** | PyPI 0.4.0 von **2019**
- Bewertung: 0/5 (siehe „Verworfen“)
- Status: geprüft (PyPI)

#### polars-talib / polars_ta
- Link: PyPI `polars-talib` 0.2.1 (18.10.2026, Lizenz in den Metadaten leer, ungeprüft); `polars-ta` 0.5.18 (20.10.2026, MIT, Repo laut Vorwissen wukan1986/polars_ta, nicht verifiziert)
- Was es kann: TA-Indikatoren als Polars-Ausdrücke.
- Nutzen für die Arena: Die Arena nutzt kein Polars, die Datenmengen sind klein (60 Instrumente, Stundenkerzen). Kein Mehrwert.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (PyPI)

#### tsfresh
- Link: https://github.com/blue-yonder/tsfresh | Lizenz: MIT | ~9.480 Sterne, Push 06.07.2026, PyPI 0.21.2 (Mai 2026)
- Was es kann: Automatische Extraktion von über 700 Zeitreihen-Features plus Relevanzfilter.
- Nutzen für die Arena: Für LLM-Agenten zu viele unbenannte Features. Allenfalls für eine spätere ML-Prognose (`forecast.py`).
- Aufwand: mittel
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### hmmlearn
- Link: https://github.com/hmmlearn/hmmlearn | Lizenz: BSD-3-Clause | ~3.450 Sterne, **letzter Push und Release 31.10.2024** (Wartungsmodus)
- Was es kann: Gaußsche und diskrete HMMs (Baum-Welch, Viterbi).
- Nutzen für die Arena: Regime „ruhig/turbulent“ aus Rendite und rollender Vola. Getestet mit 2 Zuständen auf BTC 1h: Vola je Regime 0,31 % bzw. 0,66 %, aktuell ruhig.
  Es kam eine **Konvergenzwarnung** und das Hoch-Vola-Regime war nur zu 1 % belegt. Das Ergebnis ist instabil bei nur 350 Kerzen.
- Aufwand: klein. Installation 11 s, rund 200 MB (scikit-learn + scipy).
- Bewertung: 2/5 (statsmodels-MS ist stabiler und kommt ohne Zusatzpaket)
- Status: getestet

#### statsmodels Markov-Switching (MarkovRegression / MarkovAutoregression)
- Link: https://github.com/statsmodels/statsmodels | Lizenz: BSD-3-Clause | ~11.700 Sterne, Push 29.10.2026, PyPI 0.15.0 (Aug. 2026)
- Was es kann: Regimewechsel mit wechselnder Varianz und geglätteten Regimewahrscheinlichkeiten.
- Nutzen für die Arena: Getestet: 2 Regime, σ² 0,04 vs. 0,41 (in %²), P(Hoch-Vola jetzt) = 0,14. Laufzeit **0,16 s**.
  Ein Wert wie „P(turbulent)“ wäre ein kompaktes, für LLMs verständliches Signal in `t_lage` bzw. `snapshot.py`.
- Aufwand: klein (statsmodels kommt ohnehin oft mit)
- Bewertung: 4/5
- Status: getestet

#### ruptures
- Link: https://github.com/deepcharles/ruptures | Lizenz: BSD-2-Clause | ~2.100 Sterne, Push 06.10.2026, PyPI 1.1.10 (Sept. 2025, **Python <3.14**)
- Was es kann: Offline-Change-Point-Erkennung (PELT, Binseg, Window, Kernel).
- Nutzen für die Arena: Getestet: PELT/rbf auf rollender Vola findet einen Bruch am 29.10.2026 01:00 UTC (2,3 s). Damit lässt sich „seit wann gilt das aktuelle Regime“ für den Wochen-Review (`review.py`) bestimmen.
  Für Echtzeit-Wecksignale (`events.py`) passt das nur bedingt, weil es offline arbeitet.
- Aufwand: klein (2 s Installation, wenige MB)
- Bewertung: 3/5
- Status: getestet

#### Bayesian Online Changepoint Detection (hildensia/bayesian_changepoint_detection)
- Link: https://github.com/hildensia/bayesian_changepoint_detection | Lizenz: MIT | 780 Sterne, Push 24.09.2026, **PyPI-Stand 0.2.dev1 von 2019**
- Was es kann: Adams/MacKay-BOCPD (online) und Fearnhead (offline).
- Nutzen für die Arena: BOCPD wäre das passende *Online*-Wecksignal für `events.py` („Lauflänge kollabiert“). Der Algorithmus ist rund 40 Zeilen numpy und lässt sich besser selbst schreiben als das veraltete PyPI-Paket zu nutzen.
- Aufwand: klein
- Bewertung: 3/5
- Status: geprüft (Metadaten)

#### arch (Kevin Sheppard)
- Link: https://github.com/bashtage/arch | Lizenz: NCSA (University of Illinois/NCSA, permissiv, BSD-ähnlich) | ~1.650 Sterne, Push 30.10.2026, PyPI 8.0.0 (Okt. 2025)
- Was es kann: GARCH/EGARCH/GJR mit t- und Skew-t-Verteilung, Vola-Prognosen, Bootstrap, Unit-Root-Tests.
- Nutzen für die Arena: Vola-Prognose für Vol-Targeting (siehe B), realistische Stop-Abstände und Liquidationswahrscheinlichkeit („P(Docht erreicht Liq-Preis in 24 h)“) als Warnhinweis im Order-Ergebnis.
  Getestet: 4 s Fit, 9 s Installation, rund 75 MB (statsmodels).
- Aufwand: klein
- Bewertung: 4/5
- Status: getestet

#### Hurst-Exponent (Mottl/hurst bzw. eigene Implementierung)
- Link: https://github.com/Mottl/hurst | Lizenz: MIT | 341 Sterne, Push 18.11.2025, **PyPI 0.0.5 von 2019**
- Was es kann: Hurst-Exponent per R/S-Analyse (H > 0,5 trendig, < 0,5 mean-reverting).
- Nutzen für die Arena: Getestet mit eigener R/S-Implementierung (15 Zeilen): H = 0,57 auf BTC 1h. R/S ist bei kleinen Stichproben nach oben verzerrt. Das Signal ist schwach und eignet sich nur als Kontext.
  Kein Paket nötig.
- Aufwand: sehr klein
- Bewertung: 2/5
- Status: getestet (eigene Implementierung)

#### Deribit DVOL (implizite Vola) und Optionsskew
- Link: https://www.deribit.com/api/v2/public/get_volatility_index_data (öffentlich, ohne Schlüssel) | –
- Was es kann: Der 30-Tage-IV-Index (DVOL) für BTC/ETH als OHLC je Auflösung. Test vom 30.10.: DVOL BTC = 38,3. Skew lässt sich aus `get_book_summary_by_currency`
  (mark_iv je Strike) als 25-Delta-Risk-Reversal berechnen. Die Arena holt Optionsdaten schon (`t_optionen`).
- Nutzen für die Arena: (1) DVOL als Vola-Prognose ohne Abhängigkeit, für Vol-Targeting und Stop-Abstände. (2) Erwartete Tagesbewegung ≈ DVOL/√365 (38,3 → ±2,0 %, passt zur GARCH-Prognose 1,98 %).
  (3) Risk-Reversal und Term-Structure als Stimmungssignal in `t_lage`. (4) Krypto-PM-Märkte bewerten („BTC über 85.000 $ im Oktober?“, Polymarket): Wahrscheinlichkeit aus dem
  Optionsmarkt als Vergleich zum PM-Preis. Das ist ein echter Edge-Kandidat und eine gute Kontrolle für Agenten-Prognosen.
- Aufwand: klein
- Bewertung: 5/5
- Status: getestet (DVOL-API); Skew und RND nur gelesen

#### Risk-Neutral Density (Breeden-Litzenberger)
- Link: Breeden/Litzenberger 1978; z. B. Malz 2014 (FRB NY Staff Report 677) | Lizenz: – | –
- Was es kann: Die zweite Ableitung der Call-Preise nach dem Strike ergibt die risikoneutrale Dichte. Daraus folgt P(S_T > K) = −∂C/∂K (digitaler Call).
- Nutzen für die Arena: Direkte Bepreisung der Polymarket- und Kalshi-Krypto-Schwellenmärkte („Wird BTC bis Datum X über K schließen?“). Einfacher als die volle Dichte ist
  P(S_T > K) ≈ N(d2) mit der IV des nächsten Strikes plus Skew-Korrektur (−∂σ/∂K · Vega). Achtung: „berührt bis Datum X“ (Barrier) unterscheidet sich von „liegt am Datum X über“.
  Für Touch-Märkte gilt grob P_touch ≈ 2·P(S_T > K) (Reflexionsprinzip, ohne Drift).
- Aufwand: mittel (Glättung der IV-Kurve, rund 100 Zeilen scipy)
- Bewertung: 4/5
- Status: nur gelesen

#### Funding-, Basis- und OI-Signale (Krypto)
- Link: Deribit `get_funding_rate_history`, `ticker` (`open_interest`, `funding_8h`, `index_price`, `mark_price`) | –
- Was es kann: Extremes Funding und hohe Basis zeigen überhebelte Longs (Contrarian-Signal). Steigendes OI bei fallendem Preis deutet auf neue Shorts hin.
- Nutzen für die Arena: `config.ereignisse.funding_extrem_8h` existiert bereits als Wecksignal. Ergänzen ließen sich die Basis (Mark/Index − 1) und die OI-Änderung über 24 h als Kontextzahlen in `t_lage`.
  OI gibt es nur von Deribit, weil Binance und Bybit US-IPs sperren (DECISIONS).
- Aufwand: klein
- Bewertung: 3/5
- Status: getestet (Funding-API), OI nur gelesen

---

#### Konkrete Verbesserungsideen für die Papier-Börse und das Risikomanagement

1. **Polymarket-Gebühr korrekt buchen (Fehler).** `fees.gebuehr` für `venue == "polymarket"`: `qty × rate × (p(1−p))^exponent`, gerundet auf 5 Nachkommastellen, mit `rate` und `exponent`
   aus `inst["ref"]` (`pm.py` speichert die Rate bereits, der Exponent muss ergänzt werden). Der Config-Wert `polymarket_taker` dient nur noch als Fallback.
   Ein Regressionstest gegen das Docs-Beispiel: 100 Anteile zu 0,50 bei rate 0,07 ergeben 1,75 $. DECISIONS.md korrigieren.
   Zusätzlich sollte `max_qty_fuer_budget` die neue Gebühr mitnehmen. Das geschieht automatisch, weil `gebuehr_fn` schon genutzt wird.
2. **Liquiditätsverbrauch über Orders und Fonds hinweg** (nach Nautilus `liquidity_consumption`). Ein Tick-Speicher `verbraucht[inst_id][preis] += menge`, zurückgesetzt bei neuem
   Buch-Zeitstempel bzw. nach N Minuten. `walk()` zieht die bereits verbrauchte Menge je Stufe ab. Ohne das kaufen neun Fonds im selben Lauf dieselbe dünne Polymarket-Stufe neunmal.
   Ein Fonds kann außerdem eine große Order in viele kleine zerlegen und jede bekommt den besten Preis.
   (Die Concurrency-Gruppe `arena-zustand` serialisiert schon. Eine JSON-Datei je Lauf genügt.)
3. **Impact-Zuschlag für synthetische Bücher und Stops.** Aktien (Tiefe 1e6), Stop/TP (`_stop_buch` mit Tiefe 1e9) und PredictIt: Preis zusätzlich um
   `Y·σ_tag·√(Q/V_tag)` verschlechtern (Square-Root-Law, Y = 0,7 konservativ, σ und V aus den Kerzen). Bei Stops zusätzlich gegen das echte aktuelle Buch walken statt unendliche Tiefe anzunehmen.
4. **Funding exakt.** `interest_1h` der tatsächlich vergangenen Stunden aus `get_funding_rate_history` summieren und auf das aktuelle Mark-Nominal buchen (statt aktueller 8-h-Rate × Einstand, gedeckelt auf 6 h).
5. **Ausstiegsgebühr in der Bewertung** (bekannte, leicht optimistische Vereinfachung): Die Equity in `portfolio.pos_wert` zusätzlich als „netto liquidierbar“ = Geldkurs-Wert − Gebühr(Exit) ausweisen.
   Bei Kalshi und Polymarket mit 1–3,5 % ist das relevant für das Ranking.
6. **Drawdown-Bremse und Stop-Serie-Pause** in `risk.pruefe_eroeffnung` (Daten aus `equity.jsonl`/`ledger.jsonl`): Limits halbieren ab dem halben Profil-Drawdown, Pause nach drei Stops in 24 h.
7. **Vol-Targeting für Perps:** Das Perp-Nominal-Limit mit `min(1, Ziel-Vola/σ)` skalieren, σ aus DVOL oder GARCH. Ziel je Profil in `config.json`.
8. **Cluster-Limit Krypto-Beta:** Spot, Perp und Optionsdelta auf BTC/ETH/SOL/… und Krypto-PM-Märkte als ein BTC-äquivalentes Exposure begrenzen (gemessene Korrelation 0,89–0,91).
   Hedges (Spot long / Perp short, JA/NEIN) dabei verrechnen. Das behebt auch die bekannte Vereinfachung „Hedges nicht verrechnet“.
9. **Werkzeug `positionsgroesse`** für Agenten: Kelly für Binärkontrakte inkl. Gebühr, simultan über offene Wetten, Bruchteil je Profil und gekürzt bei schlechtem Brier. Für Perps und Spot
   gilt `Risiko-USD / (k·ATR)`. Rückgabe ist ein USD-Betrag, der `risk.py` schon besteht.
10. **Kennzahlen:** CVaR95, Sortino, Calmar, „Gleichlauf“ (Korrelation der Fondsrenditen, Positions-Überlappung) in `metrics.py`. Zusätzlich eine Kennzahl „Kosten in % des Umsatzes“, um Überhandeln sichtbar zu machen.
11. **Signale in `t_lage`:** DVOL, 25-Δ-Risk-Reversal, P(turbulent) aus statsmodels-MS, GARCH-24h-Vola, Funding, Basis und OI-Delta. Für Krypto-PM-Märkte die
    optionsimplizite Wahrscheinlichkeit neben den PM-Preis stellen.
12. (Später, nur mit Limit-Orders) Queue-Position nach hftbacktest `power_prob_queue_model` sowie Maker-Rebates bei Polymarket und Kalshi.

---

_Verworfene Kandidaten dieser Kategorie: siehe [ANHANG-verworfen.md](ANHANG-verworfen.md), Abschnitt „5. Backtesting/Ausführung, Risiko/Portfolio, Signale/Regime“._

### Top-Empfehlungen

1. **Polymarket-Gebühr aus `feeSchedule` buchen** (Fehler, 5/5, rund 10 Zeilen). Ein Viertel der Top-40-Märkte hat derzeit Gebühren bis 3,5 % des Nominals.
2. **Werkzeug Positionsgrößen-Rechner** (Kelly binär, simultan, fraktional, Brier-gekoppelt; ATR-Sizing für Perps), nur numpy/scipy (5/5).
3. **Liquiditätsverbrauch je Tick** und **Square-Root-Impact** für Stops und synthetische Bücher (4/5): schließt die größten Realismuslücken in `book.py`/`watcher.py`.
4. **DVOL + optionsimplizite Wahrscheinlichkeit** als Signal und Bewertungshilfe für Krypto-PM-Märkte (5/5, keine Abhängigkeit).
5. **Risikoschicht:** Vol-Targeting (DVOL/arch), Drawdown-Bremse, Krypto-Beta-Cluster-Limit sowie die Kennzahlen „Gleichlauf“ und CVaR in `metrics.py` (4/5).
6. Bibliotheken, falls überhaupt: **skfolio** (BSD), **arch** (NCSA), **statsmodels** (BSD), **TA-Lib** (BSD, jetzt pip-Wheel), **ruptures** (BSD). Alle in Sekunden installierbar und unter 1 min im Test.
   hmmlearn ist nur zweite Wahl (Wartungsmodus, instabil auf kurzen Daten).

#### Quellen
- Polymarket Fees: https://docs.polymarket.com/trading/fees · Gamma-API https://gamma-api.polymarket.com/markets (live abgefragt) · Sekundär: https://pineanalytics.substack.com/p/polymarket-fee-rollout, https://www.predictionhunt.com/blog/polymarket-fees-complete-guide
- Kalshi: https://kalshi.com/docs/kalshi-fee-schedule.pdf · https://www.predictionhunt.com/blog/kalshi-fees-complete-guide-2026 · https://www.bettingusa.com/prediction-markets/reviews/kalshi/fees/
- Nautilus Fill Models: https://nautilustrader.io/docs/latest/concepts/backtesting/fill-models/
- hftbacktest Queue Models: https://hftbacktest.readthedocs.io/en/latest/tutorials/Probability%20Queue%20Models.html
- vectorbt-Lizenz: https://github.com/polakowo/vectorbt/blob/master/LICENSE.md
- pandas-ta-Status: https://repos.ecosyste.ms/hosts/GitHub/repositories/twopirllc%2Fpandas-ta, https://pypi.org/project/pandas-ta/
- Deribit: https://www.deribit.com/api/v2/public/get_volatility_index_data, …/get_funding_rate_history (live abgefragt)


---

## 6. Gratis-Marktdaten: Krypto, Aktien/ETF, Makro

## Kategorie 6: Gratis-Marktdaten (Krypto, Aktien/ETF, Makro)

Stand: 2026-10-30. Recherche für `rouvenwieland/ki-trader-arena`, nur lesend, im Repo wurde nichts geändert.
Die Live-Tests liefen mit curl aus der Claude-Sandbox über einen US-Cloud-Proxy, User-Agent `ki-trader-arena research kontakt@example.org`. Je Endpunkt gab es 1–2 kleine Anfragen, ohne Schlüssel.
Rohantworten liegen unter `‹Sandbox›/test-daten/out/`.

Was das Projekt schon nutzt (aus `arena/data/*.py`, `DECISIONS.md`, `STATUS.md`): Coinbase Exchange (Spot, Kerzen), Kraken (Fallback), Deribit public (Perps, Optionen, Funding), Yahoo v8 chart (Aktien, Drosselung möglich), FRED `fredgraph.csv` (ohne Schlüssel). Stooq ist wegen Anti-Bot verworfen, Binance und Bybit sind US-gesperrt.

Lesehilfe für das Feld „Status“:
- **getestet** = live aus der Sandbox abgerufen.
- **geprüft** = Doku oder ToS online nachgelesen.
- **nur gelesen** = aus Suchtreffern oder Sekundärquellen.
- **ungeprüft** = Vorwissen, nicht verifiziert.

Grundsätzlicher Hinweis zur Weiterverbreitung: Das Repo und die Webseite sind öffentlich. Sicher sind deshalb nur abgeleitete Kennzahlen und Agenten-Entscheidungen im Repo, keine Rohdaten-Spiegel. Wo die ToS das Wiederveröffentlichen verbieten oder unklar sind, ist das unten markiert.

---

### Kategorie: Gratis-Marktdaten – Krypto

#### Hyperliquid Info-API (public)
- Link (Doku/ToS): https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint · Rate-Limits: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits · ToS: https://hyperliquid.xyz/terms (Abruf per WebFetch: **403**, Inhalt nicht geprüft) | Kosten/Schlüssel: gratis, kein Schlüssel | Limits: 1200 Gewicht/min je IP (offizielle Doku; `l2Book`/`allMids` Gewicht 2, die meisten anderen 20; `fundingHistory`/`candleSnapshot` mit Zusatzgewicht)
- Was es liefert: alle Perps per POST `/info`.
  - `metaAndAssetCtxs`: 225 Märkte, je Markt Funding, Open Interest, Mark/Oracle/Mid, Premium, 24h-Volumen.
  - `l2Book`: volles Orderbuch.
  - `fundingHistory`, `candleSnapshot`.
  - `predictedFundings`: liefert **auch die Funding-Sätze von Binance- und Bybit-Perps**, die wir direkt nicht abrufen können.
- Nutzen für die Arena: sehr hoch.
  - Echte Orderbücher geben realistische Slippage für Perps.
  - Funding und OI für ~225 Coins in einem einzigen Aufruf.
  - Börsenübergreifendes Funding, ohne die US-Sperre von Binance/Bybit zu umgehen. Die Daten kommen von Hyperliquid selbst.
- Aufwand: gering (ein POST-Adapter, Zahlen als Strings).
- Bewertung: 5/5
- Status: **getestet**.
  - `metaAndAssetCtxs`: 200, 0,60 s, BTC `openInterest: "40448.3"`, `funding: "0.0000125"`.
  - `l2Book`: 200, 0,27 s.
  - `fundingHistory`: 200, 0,42 s.
  - `predictedFundings`: 200, 0,31 s, enthält `BinPerp`/`BybitPerp`.
  - Offen: ToS nicht lesbar. Hyperliquid schließt US-Personen nach allgemeiner Kenntnis von der *Nutzung des Handels* aus (ungeprüft). Reines Lesen öffentlicher Chain-Daten ist vermutlich unkritisch, das sollte vor der Integration aber per Browser geprüft werden.

#### dYdX v4 Indexer
- Link (Doku/ToS): https://docs.dydx.xyz/indexer-client/http · ToS: https://dydx.trade/terms (ungeprüft) | Kosten/Schlüssel: gratis, kein Schlüssel | Limits: nicht dokumentiert geprüft (ungeprüft)
- Was es liefert: `/v4/perpetualMarkets` mit Oracle-Preis, 24h-Volumen, `nextFundingRate` und OI. Dazu `/v4/historicalFunding/{ticker}`, `/v4/orderbooks/perpetualMarket/{ticker}` und `/v4/candles`.
- Nutzen für die Arena: zweite DEX-Perp-Quelle zum Gegenprüfen von Funding und Basis. Kleinere Liquidität als Hyperliquid.
- Aufwand: gering
- Bewertung: 3/5
- Status: **getestet**. `perpetualMarkets?ticker=BTC-USD`: 200, 0,74 s, `nextFundingRate`. `historicalFunding`: 200, 0,70 s.

#### OKX Public API (v5)
- Link (Doku/ToS): https://www.okx.com/docs-v5/en/ · ToS: https://www.okx.com/help/terms-of-service | Kosten/Schlüssel: gratis, kein Schlüssel für Marktdaten | Limits: je Endpunkt z. B. 20 Anfragen/2 s (Doku, ungeprüft)
- Was es liefert: Spot- und Swap-Ticker, Funding-Rate (`/public/funding-rate`), Open Interest, Orderbuch, Kerzen, Optionen-Summaries.
- Nutzen für die Arena: große CEX-Perp-Quelle mit Funding und OI.
- Aufwand: gering, CCXT unterstützt OKX.
- Bewertung: 3/5. Technisch erreichbar, rechtlich unklar: Die OKX-ToS schränken US-Personen für die internationale Plattform ein. Das Sperren *öffentlicher* Marktdaten-Endpunkte habe ich nicht explizit gefunden.
- Status: **getestet**. Funding: 200, 0,57 s, `fundingRate: "0.0000672"`. Spot-Ticker: 200, 0,32 s. ToS **nur gelesen** (Sekundärquellen widersprüchlich).

#### Kraken Futures (public)
- Link (Doku/ToS): https://docs.kraken.com/api/docs/futures-api/trading/get-tickers · ToS: https://www.kraken.com/legal | Kosten/Schlüssel: gratis | Limits: ungeprüft
- Was es liefert: Perp-Ticker `PF_XBTUSD` mit Mark, Bid/Ask, Funding-Rate und OI.
- Nutzen für die Arena: regulierte CEX-Perp-Referenz. Kraken ist bereits als Spot-Fallback im Projekt.
- Aufwand: gering
- Bewertung: 4/5
- Status: **getestet**, 200, 0,22 s, `markPrice: 77512.04`.

#### Bitstamp, Gemini, Bitfinex, KuCoin, Gate.io, Binance.US (Spot/Perp-Ticker)
- Link (Doku/ToS): https://www.bitstamp.net/api/ · https://docs.gemini.com/rest-api/ · https://docs.bitfinex.com/ · https://www.kucoin.com/docs · https://www.gate.io/docs/developers/apiv4 · https://docs.binance.us/ | Kosten/Schlüssel: gratis, ohne Schlüssel | Limits: je Börse (Bitstamp 400/s, Gemini 120/min laut Doku, ungeprüft)
- Was es liefert: Ticker, Orderbücher und Kerzen. Gate.io liefert zusätzlich Perp-Kontrakte mit Funding.
- Nutzen für die Arena: Preis-Konsens und Ausreißer-Erkennung über mehrere Börsen, als Redundanz zu Coinbase und Kraken. Am einfachsten über **CCXT** (MIT-Lizenz, https://github.com/ccxt/ccxt) mit `fetch_ticker`/`fetch_funding_rate`.
- Aufwand: gering mit CCXT. Abhängigkeit beachten: CCXT ist groß.
- Bewertung: 3/5
- Status: **getestet**, alle 200 aus US-IP:
  - Bitstamp 0,12 s
  - Gemini 0,16 s
  - Bitfinex 0,19 s
  - KuCoin 0,37 s
  - Gate.io 0,69 s
  - Binance.US 0,65 s
  - Zum Vergleich: Binance.com **451**, Bybit **403** (CloudFront-Länderblock), BitMEX **403**.
  - Bei KuCoin und Gate.io schließen die ToS US-Personen als Kunden aus (ungeprüft). Deshalb dort mit Vorsicht oder nicht nutzen.

#### Deribit DVOL und Book-Summary (Erweiterung der bestehenden Quelle)
- Link (Doku/ToS): https://docs.deribit.com/#public-get_volatility_index_data · https://www.deribit.com/pages/information/terms-of-service | Kosten/Schlüssel: gratis | Limits: Credit-System (ungeprüft)
- Was es liefert: DVOL (implizite 30-Tage-Volatilität BTC/ETH, OHLC) und `get_book_summary_by_currency` (OI, Mark, Basis aller Futures).
- Nutzen für die Arena: Krypto-"VIX" als Regime-Signal. Term-Struktur und Basis der Futures.
- Aufwand: minimal, der Adapter existiert schon.
- Bewertung: 5/5
- Status: **getestet**. DVOL: 200, 0,22 s, OHLC `[…, 42.65, 42.94, …]`. Book-Summary: 200, 0,21 s, `open_interest`.

#### CoinGecko (ohne Schlüssel / Demo-Schlüssel)
- Link (Doku/ToS): https://docs.coingecko.com/ · https://www.coingecko.com/en/api_terms | Kosten/Schlüssel: keyless möglich. Demo-Schlüssel per Gratis-Konto | Limits: Demo ~30/min, 10.000/Monat (offizielle Fehler-Doku nennt ~30/min; Monatszahl aus Sekundärquelle). Keyless ist niedriger und schwankend.
- Was es liefert: Preise und Marktkapitalisierung für über 10.000 Coins, `/global` (Dominanz, Gesamt-MC), `/derivatives/exchanges` (OI und Volumen je Derivatebörse, **inkl. Binance Futures**), Trending und Kategorien.
- Nutzen für die Arena: Marktbreite (Dominanz, Gesamt-MC), Long-Tail-Coins und aggregiertes Derivate-OI.
- Aufwand: gering
- Bewertung: 4/5. Attributionspflicht laut Sekundärquelle, im API-Terms-Dokument nicht selbst geprüft.
- Status: **getestet** (keyless): `simple/price` 200, 0,12 s. `/global` 200, 0,21 s. `/derivatives/exchanges` 200, 0,23 s, `open_interest_btc: 417946.2` (Binance Futures).

#### CoinPaprika
- Link (Doku/ToS): https://api.coinpaprika.com/ · https://coinpaprika.com/terms/ (ungeprüft) | Kosten/Schlüssel: Free-Tier ohne Schlüssel | Limits: laut Doku ca. 20.000 Aufrufe/Monat im Free-Plan (ungeprüft)
- Was es liefert: Ticker, Marktkapitalisierung, Beta-Wert und historische OHLCV (nur eingeschränkt gratis).
- Nutzen für die Arena: Fallback für CoinGecko.
- Aufwand: gering
- Bewertung: 3/5
- Status: **getestet**, 200, 0,15 s, `beta_value: 1.04895`.

#### CoinLore
- Link (Doku/ToS): https://www.coinlore.com/cryptocurrency-data-api | Kosten/Schlüssel: gratis, ohne Schlüssel | Limits: „1 Anfrage/s empfohlen“ (ungeprüft)
- Was es liefert: Globale Kennzahlen (BTC-Dominanz, MC-Änderung) und Ticker.
- Nutzen für die Arena: dritter Fallback für Marktbreite.
- Aufwand: gering
- Bewertung: 2/5
- Status: **getestet**, 200, 0,19 s, `btc_d: "59.06"`.

#### DefiLlama (öffentliche API)
- Link (Doku/ToS): https://api-docs.defillama.com/ · ToS: https://defillama.com/terms | Kosten/Schlüssel: gratis, ohne Schlüssel. Pro-API kostenpflichtig | Limits: nicht beziffert
- Was es liefert:
  - TVL je Chain und Protokoll (`/v2/historicalChainTvl`).
  - Stablecoin-Umlauf (`stablecoins.llama.fi`, z. B. USDT 180 Mrd.).
  - Yields (`yields.llama.fi/pools`, **10,8 MB!**).
  - Fees und Revenue (`/overview/fees`).
  - DEX-Volumen.
- Nutzen für die Arena: Liquiditäts- und Stablecoin-Zufluss als Makro-Krypto-Signal. Fees als Fundamentaldaten für Token.
- Aufwand: gering. Große Antworten nur cachen und nicht ins Repo legen.
- Bewertung: 3/5, wegen der ToS:
  - Klausel 7 gewährt nur eine Lizenz für „personal, non-commercial purposes“.
  - 8.7 verbietet „republish the data in any form without permission“.
  - 8.9 erlaubt programmatischen Zugriff nur auf die „official public API“.
  - Folgerung: Nutzen als Agenten-Input ist ok. **Keine Rohdaten im öffentlichen Repo oder auf der Webseite veröffentlichen.** Für die Anzeige um Erlaubnis bitten.
- Status: **getestet**. TVL 200, 0,26 s. Stablecoins 200, 0,30 s. Yields 200, 0,86 s. Fees 200, 0,62 s. ToS **geprüft**. `/etfs/overview` lieferte 404.

#### Coin Metrics Community API
- Link (Doku/ToS): https://docs.coinmetrics.io/ · https://coinmetrics.io/api/terms (ungeprüft) | Kosten/Schlüssel: gratis, ohne Schlüssel | Limits: 10 Anfragen / 6 s je IP (Doku), max. 10 parallel
- Was es liefert: On-chain-Kennzahlen für BTC, ETH u. a. (aktive Adressen, Marktkapitalisierung, je nach Community-Freigabe auch Hashrate, MVRV-Bausteine, Transfervolumen). Tagesauflösung, eingeschränkte Historie.
- Nutzen für die Arena: der beste Glassnode-Ersatz gratis. Fundamentale On-chain-Signale.
- Aufwand: gering
- Bewertung: 4/5. Lizenz laut Doku **CC BY-NC 4.0**: Attribution nötig, nicht-kommerziell. Das passt zu einem Forschungsprojekt, die Webseite darf aber nicht kommerziell werden.
- Status: **getestet**, 200, 0,24 s, `AdrActCnt: "644645"` (2026-10-29). Lizenz **nur gelesen** (Doku-Suchtreffer).

#### mempool.space API
- Link (Doku/ToS): https://mempool.space/docs/api/rest · ToS: https://mempool.space/terms-of-service (ungeprüft) | Kosten/Schlüssel: gratis | Limits: nicht veröffentlicht, Fair-Use (selbst hostbar, AGPL)
- Was es liefert: Gebühren-Empfehlung, Mempool-Größe, Hashrate und Difficulty (`/v1/mining/hashrate/3d`), Blöcke.
- Nutzen für die Arena: Netzwerkauslastung und Miner-Stress als Nebensignal.
- Aufwand: gering
- Bewertung: 3/5
- Status: **getestet**. `fees/recommended` 200, 0,14 s, `fastestFee: 1`. `hashrate/3d` 200, 0,41 s.

#### Blockchain.com Charts API
- Link (Doku/ToS): https://www.blockchain.com/explorer/api/charts_api · https://www.blockchain.com/legal/terms (ungeprüft) | Kosten/Schlüssel: gratis | Limits: ungeprüft
- Was es liefert: Zeitreihen wie Hashrate, Transaktionen, Mempool, Miner-Umsatz u. a.
- Nutzen für die Arena: lange On-chain-Historie für BTC.
- Aufwand: gering
- Bewertung: 3/5
- Status: **getestet**, 200, 0,55 s, `"unit":"Hash Rate TH/s"`.

#### Blockchair
- Link (Doku/ToS): https://blockchair.com/api/docs · https://blockchair.com/terms | Kosten/Schlüssel: ohne Schlüssel begrenzt nutzbar | Limits: laut Doku ca. 1.440 Anfragen/Tag ohne Schlüssel (ungeprüft). Kommerzielle Nutzung erfordert Plan (ungeprüft)
- Was es liefert: `/{chain}/stats` für viele Chains (Blöcke, 24h-Volumen, Mempool, Difficulty).
- Nutzen für die Arena: Multi-Chain-Snapshot in einem Aufruf.
- Aufwand: gering
- Bewertung: 3/5
- Status: **getestet**, 200, 0,59 s, `blocks_24h: 129`.

#### Etherscan API v2 (Free-Key)
- Link (Doku/ToS): https://docs.etherscan.io/ · https://etherscan.io/apiterms | Kosten/Schlüssel: Gratis-Schlüssel per Konto | Limits: ohne Schlüssel 1 Anfrage / 5 s (laut Antwort). Mit Free-Key laut Doku 5/s und 100.000/Tag (ungeprüft)
- Was es liefert: Gas-Oracle, ETH-Supply, Token-Transfers und Kontodaten für über 50 EVM-Chains.
- Nutzen für die Arena: Gas- und Aktivitätssignal, Stablecoin-Mint/Burn verfolgen.
- Aufwand: mittel
- Bewertung: 2/5
- Status: **getestet** (ohne Schlüssel): 200, 0,21 s, `"OK-Missing/Invalid API Key, rate limit of 1/5sec applied"`, `SafeGasPrice: "0.169"`.

#### Alternative.me Fear & Greed Index
- Link (Doku/ToS): https://alternative.me/crypto/fear-and-greed-index/ (API-Regeln auf derselben Seite) | Kosten/Schlüssel: gratis | Limits: ungeprüft (Fair-Use)
- Was es liefert: täglicher Sentiment-Index 0–100 mit Historie (`?limit=0`).
- Nutzen für die Arena: einfaches Stimmungssignal für Agenten.
- Aufwand: minimal
- Bewertung: 4/5. ToS: kommerziell erlaubt, wenn **die Quelle direkt neben den Daten genannt** wird. Man darf sich nicht als Alternative.me ausgeben.
- Status: **getestet**, 200, 0,19 s, `value: "30"`, `"Fear"`. ToS **geprüft**.

#### Coinglass API
- Link (Doku/ToS): https://docs.coinglass.com/ | Kosten/Schlüssel: nur mit Schlüssel. Ob es einen dauerhaften Gratis-Plan gibt, ist ungeprüft (bekannt sind bezahlte Hobbyist-Pläne) | Limits: –
- Was es liefert: aggregiertes Funding, OI, Liquidationen und ETF-Flows.
- Nutzen für die Arena: hoch, wenn gratis. Funding und OI decken Hyperliquid (`predictedFundings`) und CoinGecko (Derivate-OI) aber weitgehend ab.
- Aufwand: gering
- Bewertung: 2/5
- Status: **getestet**, 200 mit `{"code":"30001","msg":"API key missing."}`.

#### Binance-Daten indirekt (ohne Sperrumgehung)
- Link (Doku/ToS): siehe Hyperliquid `predictedFundings` und CoinGecko `/derivatives/exchanges`
- Was es liefert: Funding von Binance und Bybit sowie aggregiertes OI, über Dritte, die diese Daten selbst veröffentlichen.
- Nutzen für die Arena: Die größte Perp-Börse bleibt sichtbar, ohne die 451-Sperre zu umgehen.
- Aufwand: gering
- Bewertung: 4/5
- Status: **getestet** (siehe oben).

---

### Kategorie: Gratis-Marktdaten – Aktien/ETF

#### SEC EDGAR APIs (data.sec.gov)
- Link (Doku/ToS): https://www.sec.gov/search-filings/edgar-application-programming-interfaces · Fair Access: https://www.sec.gov/os/webmaster-faq#developers | Kosten/Schlüssel: gratis, kein Schlüssel. **User-Agent mit Kontakt Pflicht** | Limits: max. 10 Anfragen/s
- Was es liefert:
  - `submissions/CIK##########.json` (alle Filings inkl. Form 4, 8-K, 13F).
  - `api/xbrl/companyfacts`, `companyconcept`, `frames` (Querschnitt einer Kennzahl über alle Firmen).
  - `company_tickers.json` (Ticker→CIK).
  - Volltextsuche `efts.sec.gov/LATEST/search-index`.
  - Atom-Feed der neuesten Filings (`browse-edgar?action=getcurrent&type=4`, für Insider-Käufe).
- Nutzen für die Arena: Fundamentaldaten, Insider-Transaktionen, 8-K-Ereignisse und 13F-Positionen. US-Regierungsdaten, gemeinfrei, zeitgestempelt und damit lookahead-sicher.
- Aufwand: mittel (XBRL- und Form-4-XML parsen). Im Code einen echten Kontakt in den UA schreiben (Projekt-URL/E-Mail des Betreibers).
- Bewertung: 5/5
- Status: **getestet**, alle 200:
  - submissions 0,24 s, `"name":"Apple Inc."`
  - frames 0,35 s
  - companyconcept 0,28 s
  - Volltextsuche 0,96 s, 282 Treffer
  - company_tickers 0,34 s
  - Form-4-Atom 0,24 s

#### FINRA Query API und Reg-SHO-Tagesdateien
- Link (Doku/ToS): https://developer.finra.org/docs · Reg SHO: https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data · ToS: https://www.finra.org/terms-of-use (ungeprüft) | Kosten/Schlüssel: öffentliche Datensätze ohne Schlüssel. Gratis-Konto für mehr | Limits: ungeprüft
- Was es liefert: `consolidatedShortInterest` (zweimonatliches Short Interest je Titel) und die täglichen Short-Sale-Volumen-Dateien (`CNMSshvol{YYYYMMDD}.txt`).
- Nutzen für die Arena: Short Interest und täglicher Short-Anteil als Positionierungssignal.
- Aufwand: gering
- Bewertung: 4/5
- Status: **getestet**. Query API 200, 0,53 s, `currentShortPositionQuantity: 4851353`. Reg-SHO-Datei vom 29.10.2026: 200, 0,27 s.

#### CFTC Commitments of Traders (Socrata-API)
- Link (Doku/ToS): https://publicreporting.cftc.gov/ · https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm | Kosten/Schlüssel: gratis. Socrata-App-Token optional | Limits: ohne Token gedrosselt (Socrata, ungeprüft)
- Was es liefert: wöchentliche COT-Positionen (Legacy, Disaggregated, TFF), u. a. für S&P-, VIX-, Treasury-, Bitcoin-CME-, Öl- und Gold-Futures.
- Nutzen für die Arena: Positionierung von Spekulanten und Hedgern als Makro- und Regime-Signal.
- Aufwand: gering bis mittel (Dataset-IDs wählen)
- Bewertung: 4/5
- Status: **getestet**, `6dca-aqww.json` 200, 0,59 s, `report_date_as_yyyy_mm_dd: 2026-10-20`.

#### Cboe: VIX-Historie, Put/Call-Ratio, verzögerte Optionsketten
- Link (Doku/ToS): https://www.cboe.com/tradable_products/vix/vix_historical_data/ · Rechtliches: https://www.cboe.com/legal/ (Unterseiten /terms, /use-of-content nicht ausgewertet) | Kosten/Schlüssel: gratis, ohne Schlüssel | Limits: ungeprüft
- Was es liefert:
  - `cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv` (VIX ab 1990, analog VIX9D, VVIX u. a.).
  - `…/volume_and_call_put_ratios/totalpc.csv`.
  - `cdn.cboe.com/api/global/delayed_quotes/options/SPY.json`: komplette verzögerte Optionskette mit Bid/Ask, IV, Greeks und OI.
- Nutzen für die Arena: hoch. VIX und Put/Call als Regime-Signal. Die Optionskette erlaubt realistische Optionsbewertung für Aktien-Optionen.
- Aufwand: gering. **Redirect beachten**: 307 → `cdn-api.cboe.com`, also `allow_redirects` oder die neue Domain direkt nutzen.
- Bewertung: 4/5 für VIX-CSV, 3/5 für die Optionsketten (inoffizieller Website-Endpunkt).
  - Die ToS für automatisierten Abruf und Weiterverbreitung sind **nicht geprüft**.
  - Die Put/Call-CSV trägt einen Haftungsausschluss.
  - Rohdaten nicht spiegeln.
- Status: **getestet** (mit `-L`). Optionskette SPY 200, 0,73 s, `"bid": 215.42, "open_interest": 12.0`. VIX-CSV 200, 0,46 s. Put/Call-CSV 200, 0,18 s.

#### Yahoo Finance Chart-Endpunkt (bestehend)
- Link (Doku/ToS): inoffiziell. https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html | Kosten/Schlüssel: gratis | Limits: drosselt Cloud-IPs (429, laut Projekt-Status)
- Was es liefert: Kurse und Kerzen. Optionsketten über `/v7/finance/options` (ungeprüft, oft Crumb-pflichtig).
- Nutzen für die Arena: läuft bereits.
- Aufwand: –
- Bewertung: 3/5. Die ToS erlauben nach allgemeiner Kenntnis nur persönliche Nutzung (ungeprüft). Nur best effort.
- Status: **getestet**, aktuell 200, 0,19 s für SPY (in diesem Moment nicht gedrosselt).

#### Alpaca Market Data (Basic, Gratis-Konto)
- Link (Doku/ToS): https://docs.alpaca.markets/docs/about-market-data-api · https://alpaca.markets/disclosures | Kosten/Schlüssel: **Gratis-Konto, Schlüssel nötig** (Paper-Account reicht) | Limits: 200 Aufrufe/min (Doku). Echtzeit nur IEX, SIP 15 min verzögert
- Was es liefert: Aktien- und ETF-Bars, Trades, Quotes (IEX), Snapshots, News. Optionen indikativ. Krypto.
- Nutzen für die Arena: robuster Yahoo-Ersatz für Cloud-IPs mit offiziellem API-Vertrag. Schon in STATUS.md als Option genannt.
- Aufwand: gering (Secrets in GitHub Actions)
- Bewertung: 5/5. Die Bedingungen zum Anzeigen und Weiterverbreiten der Daten habe ich nicht gefunden. Vermutlich nur abgeleitete Werte veröffentlichen.
- Status: **getestet**: 401 ohne Schlüssel. Der Endpunkt ist also erreichbar. Plan **nur gelesen**.

#### Tiingo (Gratis-Konto)
- Link (Doku/ToS): https://www.tiingo.com/documentation/general/overview · https://www.tiingo.com/about/terms | Kosten/Schlüssel: Gratis-Schlüssel | Limits: laut Preisseite ca. 50 Anfragen/h, 1.000/Tag, 500 Symbole/Monat (ungeprüft). Free-Plan für persönliche Nutzung, intern (ungeprüft)
- Was es liefert: EOD-Kurse (bereinigt, sehr lange Historie), IEX-Intraday, Fundamentaldaten (eingeschränkt), Krypto.
- Nutzen für die Arena: gute bereinigte Tagesdaten als zweiter Aktien-Fallback.
- Aufwand: gering
- Bewertung: 3/5
- Status: **getestet**: 403 `"Please supply a token"`.

#### Finnhub (Gratis-Konto)
- Link (Doku/ToS): https://finnhub.io/docs/api · https://finnhub.io/terms-of-service | Kosten/Schlüssel: Gratis-Schlüssel | Limits: 60 Aufrufe/min (Doku, ungeprüft)
- Was es liefert: Quotes, **Earnings-Kalender**, IPO-Kalender, Empfehlungstrends, Insider-Sentiment, Basis-Fundamentaldaten. Wirtschaftskalender ist bezahlt (ungeprüft).
- Nutzen für die Arena: Earnings-Kalender gratis, das schließt eine Lücke.
- Aufwand: gering
- Bewertung: 4/5 (Weiterverbreitung laut ToS vermutlich verboten, ungeprüft)
- Status: **getestet**: 401 `"Please use an API key."`.

#### Alpha Vantage (Gratis-Schlüssel)
- Link (Doku/ToS): https://www.alphavantage.co/documentation/ · https://www.alphavantage.co/terms_of_service/ | Kosten/Schlüssel: Gratis-Schlüssel | Limits: **25 Anfragen/Tag** (ungeprüft, laut Auftrag)
- Was es liefert: Kurse, Fundamentaldaten, Earnings-Kalender (CSV), FX, Makro-Indikatoren, News-Sentiment.
- Nutzen für die Arena: nur für seltene Abrufe, z. B. den Earnings-Kalender einmal täglich.
- Aufwand: gering
- Bewertung: 2/5
- Status: **getestet**: 200 mit Demo-Hinweis („demo API key is for demo purposes only“).

#### Financial Modeling Prep (Gratis-Schlüssel)
- Link (Doku/ToS): https://site.financialmodelingprep.com/developer/docs · https://site.financialmodelingprep.com/terms-of-service | Kosten/Schlüssel: Gratis-Schlüssel | Limits: 250 Anfragen/Tag (ungeprüft). Free-Tier auf US-Titel und Teile der Endpunkte beschränkt (ungeprüft)
- Was es liefert: Bilanzen, Kennzahlen, Earnings- und Dividenden-Kalender.
- Nutzen für die Arena: mittel. EDGAR deckt Fundamentaldaten gratis und ohne ToS-Risiko ab.
- Aufwand: gering
- Bewertung: 2/5
- Status: **getestet**: 401 „Invalid API KEY“.

#### Massive (ehemals Polygon.io), Free-Plan
- Link (Doku/ToS): https://massive.com/docs · https://massive.com/terms (ungeprüft) | Kosten/Schlüssel: Gratis-Schlüssel | Limits: 5 Aufrufe/min, EOD und 2 Jahre Historie (ungeprüft)
- Was es liefert: Aggregates (Vortag, Historie), Referenzdaten, Dividenden und Splits.
- Nutzen für die Arena: EOD-Fallback.
- Aufwand: gering
- Bewertung: 2/5
- Status: **getestet**: `api.massive.com` und `api.polygon.io` liefern beide 401 „API Key was not provided“.

#### Twelve Data (Gratis-Schlüssel)
- Link (Doku/ToS): https://twelvedata.com/docs · https://twelvedata.com/terms | Kosten/Schlüssel: Gratis-Schlüssel | Limits: 8/min, 800/Tag (ungeprüft)
- Was es liefert: Kurse für Aktien, FX und Krypto sowie technische Indikatoren.
- Nutzen für die Arena: Fallback für Kurse, auch FX.
- Aufwand: gering
- Bewertung: 2/5
- Status: **getestet**: 401 mit Hinweis auf kostenlosen Schlüssel.

#### EODHD (Gratis-Schlüssel)
- Link (Doku/ToS): https://eodhd.com/financial-apis/ · https://eodhd.com/financial-apis/terms-conditions | Kosten/Schlüssel: Gratis-Schlüssel | Limits: 20 Aufrufe/Tag (ungeprüft)
- Was es liefert: EOD-Daten weltweit (auch XETRA), Fundamentaldaten (bezahlt).
- Nutzen für die Arena: gering wegen 20/Tag. Interessant nur für Nicht-US-Börsen.
- Aufwand: gering
- Bewertung: 1/5
- Status: **getestet**: Der Demo-Schlüssel gilt nur für bestimmte Ticker. AAPL.US 200, 0,49 s, `adjusted_close: 347.1`. SPY.US 403.

#### Tradier Sandbox
- Link (Doku/ToS): https://documentation.tradier.com/brokerage-api · https://tradier.com/terms (ungeprüft) | Kosten/Schlüssel: Gratis-Developer-Konto mit Sandbox-Token | Limits: 60/min Sandbox (ungeprüft)
- Was es liefert: verzögerte Quotes, **Optionsketten mit Greeks** (via ORATS), Kalender.
- Nutzen für die Arena: Alternative zur Cboe-Optionskette mit offiziellem API-Vertrag.
- Aufwand: gering
- Bewertung: 3/5. Ob die Sandbox ohne Brokerage-Konto noch vergeben wird: ungeprüft.
- Status: **getestet**: 401 „Invalid access token“, der Endpunkt ist erreichbar.

#### US Treasury: FiscalData-API und Zinskurve
- Link (Doku/ToS): https://fiscaldata.treasury.gov/api-documentation/ · Zinskurve: https://home.treasury.gov/resource-center/data-chart-center/interest-rates | Kosten/Schlüssel: gratis, gemeinfrei | Limits: keine genannt
- Was es liefert:
  - FiscalData: Durchschnittszinsen, Schuldenstand (Debt to the Penny), Daily Treasury Statement (TGA-Saldo, Liquiditätssignal!), Auktionsergebnisse.
  - Zinskurve als CSV, täglich 1 Monat bis 30 Jahre.
- Nutzen für die Arena: Zinskurve und TGA-Liquidität als Makro-Regime-Signal. Dient auch als Risk-free-Rate.
- Aufwand: gering. Bei curl `page[size]` URL-kodieren.
- Bewertung: 5/5
- Status: **getestet**. FiscalData 200, 0,54 s, `avg_interest_rate_amt: "3.870"`. Zinskurven-CSV 200, aber **19,4 s** langsam: `10/29/2026, 10 Yr 4.98`.

---

### Kategorie: Gratis-Marktdaten – Makro

#### FRED / ALFRED (Gratis-Schlüssel für API)
- Link (Doku/ToS): https://fred.stlouisfed.org/docs/api/fred/ · ALFRED-Vintages: https://fred.stlouisfed.org/docs/api/fred/realtime_period.html · ToS: https://fred.stlouisfed.org/docs/api/terms_of_use.html | Kosten/Schlüssel: `fredgraph.csv` ohne Schlüssel (bereits genutzt). **API mit Gratis-Schlüssel** | Limits: 120 Anfragen/min (ungeprüft)
- Was es liefert: über 800.000 Serien. Mit `realtime_start`/`realtime_end` auf `series/observations` bekommt man **die Werte, wie sie zu einem Stichtag bekannt waren**.
- Nutzen für die Arena: sehr hoch, gegen Lookahead-Bias bei Backtests. Revisionen von BIP, Arbeitsmarkt und CPI werden korrekt abgebildet.
- Aufwand: gering
- Bewertung: 5/5. ToS: Serien mit dem Vermerk „Copyright“ (Dritt-Eigentümer, z. B. ICE/BofA, S&P) **nicht weiterverbreiten**. Für API-Anwendungen gilt ein Hinweis „nutzt die FRED-API, nicht vom Fed St. Louis unterstützt“ (laut Sekundärquelle).
- Status: **getestet**. `fredgraph.csv?id=DGS10` 200, 0,42 s. API ohne Schlüssel 400 „Variable api_key is not set“, der Endpunkt ist also erreichbar. ToS **nur gelesen** (Suchtreffer auf die offizielle Seite).

#### DBnomics
- Link (Doku/ToS): https://api.db.nomics.world/v22/apidocs · https://db.nomics.world/ (Lizenz je Provider; Plattform-Code AGPL) | Kosten/Schlüssel: gratis, ohne Schlüssel | Limits: nicht beziffert
- Was es liefert: eine einheitliche API für über 80 Provider (ECB, Eurostat, IMF, OECD, BIS, BLS, INSEE, Bundesbank u. a.).
- Nutzen für die Arena: **ein** Adapter statt vieler. Ideal für europäische und globale Makrodaten.
- Aufwand: gering
- Bewertung: 5/5
- Status: **getestet**, `ECB/EXR/D.USD.EUR.SP00.A` 200, **2,7 s**. Etwas langsam, lieber cachen.

#### ECB Data Portal (SDMX)
- Link (Doku/ToS): https://data.ecb.europa.eu/help/api/overview · Wiederverwendung: https://www.ecb.europa.eu/home/disclaimer/html/index.en.html (frei mit Quellenangabe, ungeprüft) | Kosten/Schlüssel: gratis | Limits: keine genannt
- Was es liefert: Leitzinsen, €STR, Wechselkurse, Renditekurven, Geldmengen. CSV und JSON.
- Nutzen für die Arena: EUR-Seite für den EUR/USD-Umrechner, Euro-Zinsen.
- Aufwand: gering
- Bewertung: 4/5
- Status: **getestet**, 200, 0,63 s (CSV, `lastNObservations=2`).

#### Frankfurter (EZB-Referenzkurse)
- Link (Doku/ToS): https://frankfurter.dev/ (Open Source) | Kosten/Schlüssel: gratis, ohne Schlüssel | Limits: keine genannt
- Was es liefert: tägliche EZB-Referenzkurse als einfaches JSON.
- Nutzen für die Arena: Ersatz oder Prüfung für den Coinbase-EUR/USD-Kurs in `crypto.py`.
- Aufwand: minimal
- Bewertung: 3/5
- Status: **getestet**. `api.frankfurter.dev/v1/latest` 200, 0,33 s, `EUR: 0.89847`. Die alte Domain `api.frankfurter.app` antwortet mit 301.

#### Eurostat API
- Link (Doku/ToS): https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access · Wiederverwendung: CC BY 4.0 (ungeprüft) | Kosten/Schlüssel: gratis | Limits: keine genannt
- Was es liefert: HICP, BIP, Arbeitslosigkeit u. a. für EU-Länder.
- Nutzen für die Arena: Euro-Makro. Auch über DBnomics erreichbar.
- Aufwand: gering
- Bewertung: 3/5
- Status: **getestet**, `prc_hicp_manr` 200, 0,55 s, `value {"0":2.1,"1":2.0}`.

#### OECD SDMX API
- Link (Doku/ToS): https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html · https://www.oecd.org/en/about/terms-conditions.html (ungeprüft) | Kosten/Schlüssel: gratis | Limits: laut OECD ca. 20 Abfragen/min (ungeprüft)
- Was es liefert: Composite Leading Indicators (CLI), Konjunktur- und Zinsdaten.
- Nutzen für die Arena: CLI als Konjunkturzyklus-Signal.
- Aufwand: mittel (SDMX-Schlüssel finden)
- Bewertung: 3/5
- Status: **getestet**, CLI USA 200, 1,06 s.

#### World Bank API
- Link (Doku/ToS): https://datahelpdesk.worldbank.org/knowledgebase/topics/125589 · CC BY 4.0 | Kosten/Schlüssel: gratis | Limits: keine genannt
- Was es liefert: jährliche Entwicklungsindikatoren.
- Nutzen für die Arena: gering für tägliche Handelsentscheidungen.
- Aufwand: gering
- Bewertung: 1/5
- Status: **getestet**, 200, 0,32 s.

#### IMF DataMapper API
- Link (Doku/ToS): https://www.imf.org/external/datamapper/api/help · https://www.imf.org/en/About/copyright-and-terms (ungeprüft) | Kosten/Schlüssel: gratis | Limits: ungeprüft
- Was es liefert: WEO-Prognosen (BIP, Inflation) je Land und Jahr.
- Nutzen für die Arena: gering, eher Kontext.
- Aufwand: gering
- Bewertung: 1/5
- Status: **getestet**, 200, 2,6 s. Achtung: Der Länderfilter wurde ignoriert, es kamen alle Länder zurück.

#### BLS Public Data API v2
- Link (Doku/ToS): https://www.bls.gov/developers/ · https://www.bls.gov/bls/linksite.htm | Kosten/Schlüssel: v1 ohne Schlüssel (25 Abfragen/Tag je IP). **v2 mit Gratis-Registrierungsschlüssel** (500/Tag, ungeprüft) | Limits: siehe oben
- Was es liefert: CPI, Arbeitsmarktdaten (NFP), PPI und JOLTS direkt von der Quelle.
- Nutzen für die Arena: mittel, FRED spiegelt dieselben Daten.
- Aufwand: gering
- Bewertung: 2/5
- Status: **getestet**: 200 mit `REQUEST_NOT_PROCESSED … daily threshold … reached`. **Die geteilte Cloud-IP hat das schlüssellose Tageskontingent schon verbraucht.** Für GitHub Actions ist das ebenso zu erwarten, also nur mit Schlüssel nutzen.

#### BEA API (Gratis-Schlüssel)
- Link (Doku/ToS): https://apps.bea.gov/api/signup/ | Kosten/Schlüssel: Gratis-UserID | Limits: 100 Anfragen/min (ungeprüft)
- Was es liefert: BIP, PCE (Fed-Inflationsmaß), Einkommen.
- Nutzen für die Arena: gering bis mittel (auch in FRED).
- Aufwand: gering
- Bewertung: 2/5
- Status: **getestet**: Mit ungültiger UserID 200 und eine Fehlermeldung, der Endpunkt ist erreichbar.

#### Deutsche Bundesbank SDMX-API
- Link (Doku/ToS): https://www.bundesbank.de/de/statistiken/zeitreihen-datenbanken/hilfe-zur-zeitreihen-datenbank/web-service | Kosten/Schlüssel: gratis | Limits: keine genannt
- Was es liefert: deutsche Zinsen (Umlaufrenditen), Zahlungsbilanz, Bankstatistik.
- Nutzen für die Arena: gering bis mittel (Bund-Rendite).
- Aufwand: mittel (Serien-Schlüssel finden)
- Bewertung: 2/5
- Status: **getestet**, Serie `BBSIS/D.I.ZAR…R10XX…` 200, 0,47 s (CSV).

#### New York Fed Markets API (SOFR, EFFR)
- Link (Doku/ToS): https://markets.newyorkfed.org/static/docs/markets-api.html · https://www.newyorkfed.org/termsofuse (ungeprüft) | Kosten/Schlüssel: gratis | Limits: keine genannt
- Was es liefert: SOFR, EFFR, OBFR mit Perzentilen und Volumen, Repo/RRP-Operationen (RRP-Saldo = Liquiditätssignal).
- Nutzen für die Arena: Geldmarkt-Liquidität. Die RRP-Inanspruchnahme ist ein beliebtes Krypto- und Aktien-Liquiditätssignal.
- Aufwand: gering
- Bewertung: 4/5
- Status: **getestet**, `sofr/last/2.json` 200, 0,41 s, `percentRate: 3.94` (2026-10-28).

#### FOMC-Termine (Federal Reserve)
- Link (Doku/ToS): https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (gemeinfrei) | Kosten/Schlüssel: gratis | Limits: –
- Was es liefert: Sitzungstermine, Statement- und Protokoll-Daten. Nur HTML, keine API.
- Nutzen für die Arena: Ereigniskalender für Agenten („FOMC in 2 Tagen“).
- Aufwand: gering. Empfehlung: Termine einmal im Jahr als statische Liste ins Repo statt Scraping.
- Bewertung: 4/5
- Status: **getestet**, HTML 200, 0,23 s.

#### Wirtschaftskalender (allgemein)
- Link (Doku/ToS): Gratis-APIs mit klaren Bedingungen fehlen. Finnhub `economic calendar` ist bezahlt (ungeprüft), Investing.com und ForexFactory haben keine API, ihre ToS verbieten Scraping (ungeprüft). | Kosten/Schlüssel: – | Limits: –
- Was es liefert: –
- Nutzen für die Arena: Ersatz durch Bausteine: BLS-Release-Kalender (https://www.bls.gov/schedule/news_release/), FRED `releases/dates` (mit Schlüssel), FOMC-Liste, BEA-Release-Schedule. Das ist alles gemeinfrei.
- Aufwand: mittel
- Bewertung: 3/5 (Bausteinlösung)
- Status: FRED-Release-Dates **ungeprüft**. Die BLS-Seite wurde nicht getestet.

---

### Live-Testergebnisse aus der Sandbox

US-Cloud-Proxy, 2026-10-30 ~10:00 UTC. Die Antwortzeit ist die gesamte curl-Zeit.

| Quelle / Endpunkt | HTTP | Zeit (s) | Beispielfeld / Bemerkung |
|---|---|---|---|
| Hyperliquid `metaAndAssetCtxs` | 200 | 0,60 | 225 Perps; BTC OI 40448, funding 0.0000125 |
| Hyperliquid `l2Book` BTC | 200 | 0,27 | px 77654.0 sz 15.71 |
| Hyperliquid `fundingHistory` ETH | 200 | 0,42 | fundingRate 0.0000125 |
| Hyperliquid `predictedFundings` | 200 | 0,31 | enthält BinPerp/BybitPerp |
| dYdX `perpetualMarkets` | 200 | 0,74 | nextFundingRate |
| dYdX `historicalFunding` | 200 | 0,70 | rate −0.000000375 |
| OKX funding-rate / ticker | 200/200 | 0,57/0,32 | fundingRate 0.0000672 |
| Kraken Futures ticker | 200 | 0,22 | markPrice 77512 |
| Bitstamp / Gemini / Bitfinex | 200 | 0,12/0,16/0,19 | Ticker |
| KuCoin / Gate.io / Binance.US | 200 | 0,37/0,69/0,65 | Ticker / Perp-Kontrakt |
| Binance.com | **451** | 0,12 | „restricted location“ |
| Bybit | **403** | 0,26 | CloudFront-Länderblock |
| BitMEX | **403** | 0,37 | gesperrt |
| Coinbase International | 404 | 0,95 | falscher Pfad getestet, nicht weiter verfolgt |
| Deribit DVOL / book_summary | 200 | 0,22/0,21 | DVOL 42.65 |
| CoinGecko simple/global/derivatives (ohne Schlüssel) | 200 | 0,12/0,21/0,23 | btc 77571 |
| CoinPaprika | 200 | 0,15 | beta_value 1.049 |
| CoinLore global | 200 | 0,19 | btc_d 59.06 |
| CoinCap v2 | 502 (Proxy) | 0,14 | v2 nicht erreichbar |
| CoinCap v3 (`rest.coincap.io`) | 401 | 0,36 | Schlüssel nötig |
| CryptoCompare (CoinDesk) | 401 | 0,17 | „API key required“ |
| CoinMarketCap | 401 | 0,30 | Schlüssel nötig |
| DefiLlama TVL / Stablecoins / Yields / Fees | 200 | 0,26/0,30/0,86/0,62 | Yields 10,8 MB |
| Coin Metrics Community | 200 | 0,24 | AdrActCnt 644645 |
| mempool.space fees / hashrate | 200 | 0,14/0,41 | fastestFee 1 |
| blockchain.info charts | 200 | 0,55 | Hash Rate TH/s |
| Blockchair stats | 200 | 0,59 | blocks_24h 129 |
| Etherscan v2 (ohne Schlüssel) | 200 | 0,21 | 1 Anfrage/5 s |
| alternative.me F&G | 200 | 0,19 | 30 „Fear“ |
| Coinglass | 200 | 0,58 | „API key missing“ |
| Farside (ETF-Flows) | **403** | 0,37 | Cloudflare „Just a moment“ (Anti-Bot) |
| SEC submissions / frames / concept | 200 | 0,24/0,35/0,28 | Apple Inc. |
| SEC Volltextsuche | 200 | 0,96 | 282 Treffer |
| SEC company_tickers / Form-4-Atom | 200 | 0,34/0,24 | – |
| Cboe Optionskette SPY (mit Redirect) | 200 | 0,73 | bid 215.42, OI |
| Cboe VIX_History.csv / totalpc.csv | 200 | 0,46/0,18 | ab 1990 |
| FINRA consolidatedShortInterest | 200 | 0,53 | currentShortPositionQuantity |
| FINRA Reg-SHO-Tagesdatei | 200 | 0,27 | ShortVolume |
| CFTC COT (Socrata) | 200 | 0,59 | report 2026-10-20 |
| Treasury FiscalData | 200 | 0,54 | avg_interest_rate 3.870 |
| Treasury Zinskurven-CSV | 200 | **19,4** | 10 Yr 4.98 |
| Yahoo chart SPY | 200 | 0,19 | aktuell nicht gedrosselt |
| Stooq CSV | Reset | 10,2 | Verbindung zurückgesetzt |
| Nasdaq Earnings-API | Timeout / HTTP2-Fehler | 25 | blockiert |
| Alpaca / Tiingo / Finnhub / FMP / Massive / Polygon / Twelve / Tradier | 401/403 | 0,13–0,36 | erreichbar, Schlüssel nötig |
| Alpha Vantage (demo) | 200 | 0,16 | nur Demo-Hinweis |
| EODHD demo | 200 (AAPL) / 403 (SPY) | 0,49 | Demo nur für einzelne Ticker |
| FRED fredgraph.csv | 200 | 0,42 | DGS10 |
| FRED API (ohne Schlüssel) | 400 | 0,51 | „api_key is not set“ |
| DBnomics | 200 | 2,74 | ECB/EXR |
| ECB Data Portal | 200 | 0,63 | CSV |
| Eurostat | 200 | 0,55 | HICP 2.1 |
| OECD SDMX | 200 | 1,06 | CLI |
| World Bank / IMF | 200 | 0,32/2,62 | – |
| BLS v2 (ohne Schlüssel) | 200 | 0,36 | **Tageslimit der geteilten IP erreicht** |
| BEA | 200 | 0,43 | Fehler wegen ungültiger UserID |
| Bundesbank SDMX | 200 | 0,47 | CSV |
| NY Fed SOFR | 200 | 0,41 | 3.94 |
| Fed FOMC-Kalender (HTML) | 200 | 0,23 | – |
| Frankfurter (.dev / .app) | 200 / 301 | 0,33 | EUR 0.89847 |

---

_Verworfene Kandidaten dieser Kategorie: siehe [ANHANG-verworfen.md](ANHANG-verworfen.md), Abschnitt „6. Gratis-Marktdaten: Krypto, Aktien/ETF, Makro“._

### Top-Empfehlungen

1. **Hyperliquid Info-API** (gratis, ohne Schlüssel, getestet). Ein POST liefert Funding, OI, Mark und Volumen für ~225 Perps, dazu L2-Orderbücher. `predictedFundings` zeigt auch Binance- und Bybit-Funding. Das ist das größte Upgrade für Derivate-Realismus. Vorher die ToS im Browser prüfen (WebFetch-403).
2. **Deribit DVOL und Book-Summary**: Erweiterung des bestehenden Adapters ohne neues Risiko. Krypto-Volatilitätsregime und Futures-Basis.
3. **SEC EDGAR** (submissions, frames, companyfacts, Volltextsuche, Form-4-Feed): gemeinfrei, 10 Anfragen/s, User-Agent Pflicht. Fundamentaldaten, Insider-Käufe und 8-K-Ereignisse mit Zeitstempel.
4. **Alpaca Basic** (Gratis-Konto) als offizieller Yahoo-Ersatz für Aktien. **Cboe VIX-CSV** zusätzlich für die Regime-Erkennung.
5. **FRED-API mit Gratis-Schlüssel inkl. ALFRED-Vintages** (`realtime_start`) gegen Lookahead. Dazu **DBnomics** als ein einziger Adapter für ECB, Eurostat, OECD und IMF.
6. **US Treasury FiscalData und Zinskurve** sowie **NY Fed (SOFR/RRP)**: Liquidität und Zinsstruktur, gemeinfrei.
7. **FINRA Short Interest und Reg SHO** sowie **CFTC COT**: Positionierungsdaten gratis und ohne Schlüssel.
8. **Coin Metrics Community** (CC BY-NC, Attribution) und **alternative.me Fear & Greed** (Attribution direkt neben den Daten): On-chain- und Stimmungssignal.
9. **CoinGecko keyless** (später Demo-Schlüssel): Marktbreite und aggregiertes Derivate-OI.
10. **DefiLlama** nur als Agenten-Input: Die ToS verbieten Wiederveröffentlichen ohne Erlaubnis. Für die Webseite vorher anfragen.

Zur Umsetzung:
- In `http.py` ist für ein POST-JSON (Hyperliquid) eine `post()`-Variante nötig.
- Cboe verlangt Redirect-Folgen (307 → `cdn-api.cboe.com`).
- Den SEC-User-Agent mit echtem Betreiber-Kontakt setzen.
- BLS nur mit Schlüssel nutzen, das Kontingent der geteilten IP ist verbraucht.
- Große Antworten (DefiLlama Yields 10,8 MB) nicht ins Repo schreiben.

Quellen (ToS/Doku, online gelesen):
- https://alternative.me/crypto/fear-and-greed-index/
- https://defillama.com/terms
- https://docs.coinmetrics.io/packages/coin-metrics-community-data
- https://gitbook-docs.coinmetrics.io/cm-api-spec/rate-limits
- https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits
- https://docs.coingecko.com/docs/common-errors-rate-limit
- https://docs.alpaca.markets/docs/about-market-data-api
- https://fred.stlouisfed.org/docs/api/terms_of_use.html
- https://fred.stlouisfed.org/legal/
- https://www.okx.com/help/terms-of-service
- https://farside.co.uk/


---

## 7. Nachrichten/Stimmung, alternative Daten, MCP-Server

## Kategorie 7: Nachrichten/Stimmung, Alternative Daten/Lage, MCP-Server

Stand: 30.10.2026. Recherche nur lesend, im Repo nichts geändert. Gelesen: `arena/data/news.py`, `arena/data/lage.py`, `arena/agent/tools.py`, `PLAN.md`, `STATUS.md`.
Live-Tests mit curl aus der Cloud-Sandbox (US-Rechenzentrum hinter einem Agent-Proxy, also eine **geteilte IP**, ähnlich wie bei GitHub Actions). Es wurden keine Schlüssel verwendet. Rohantworten liegen unter `‹Sandbox›/test-news/`.

**Statuswerte:** *getestet* = Endpunkt selbst live abgerufen · *geprüft* = Doku/ToS selbst gelesen oder per Websuche bestätigt · *nur gelesen* = Angaben aus Drittquellen, nicht selbst verifiziert · *ungeprüft* = Annahme aus Vorwissen.
**Repo-Datum:** Das angegebene Datum ist `updated_at` aus der GitHub-Suche, also die letzte Änderung an den Metadaten. Das ist nur ungefähr der letzte Commit.

#### Wichtigste Befunde zum bestehenden Code

1. **Reddit `.json` liefert heute 403.** Die RSS-Variante (`/r/<sub>/.rss`) liefert noch 200. `news.reddit()` fällt richtig auf RSS zurück, verliert dabei aber Punkte und Zeitstempel (dort wird `zeit = time.time()` gesetzt). Laut Drittquellen hat Reddit im Mai 2026 den Zugriff auf `.json` ohne Anmeldung abgeschaltet.
2. **GDELT DOC 2.0 lieferte bei 4 von 6 Versuchen HTTP 429** („one every 5 seconds“), obwohl zwischen den Abrufen 6–8 s Pause lagen. Ursache ist wahrscheinlich die geteilte IP. Die GDELT **Context API** und die **Rohdateien** (`lastupdate.txt`) liefen problemlos. `news.gdelt()` mit `versuche=1` liefert deshalb aus GitHub Actions vermutlich oft leere Listen.
3. **Open-Meteo:** Die ersten Abrufe liefen (200). Danach kam *„Daily API request limit exceeded“* (429). Das Kontingent gilt pro IP, und auf geteilten Cloud-IPs teilen sich viele Nutzer das Tageskontingent. Für die Arena braucht es deshalb Zwischenspeicher, eine Rückfallquelle (NWS, ECMWF/NOMADS) und eventuell einen eigenen Server.
4. **Wikimedia:** Mit einem User-Agent **ohne** vollständige URL bzw. E-Mail kam 429. Mit `(...; https://github.com/...)` kam 200. Die Richtlinie verlangt Kontaktdaten im User-Agent (dann 200 statt 10 Anfragen pro Minute).

---

### Kategorie: Nachrichten, Stimmung, alternative Daten, MCP

#### A) Nachrichten / Stimmung

#### GDELT DOC 2.0 API
- Link (Doku/ToS): https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/ · Bedingungen: https://www.gdeltproject.org/about.html#termsofuse | Lizenz/Kosten: kostenlos; laut Sekundärquelle für jede Nutzung erlaubt, mit Zitat und Link (Originaltext nicht selbst gelesen) | –
- Was es liefert: Artikelsuche über die Weltpresse (65 Sprachen) der letzten 3 Monate. Modi u. a. `artlist`, `timelinevol`, `timelinetone` (Ton-Zeitreihe), `tonechart`.
- Nutzen für die Arena: Hoch als Stimmungs-Zeitreihe (Ton und Volumen zu „Fed“, „Bitcoin“, Kandidatennamen) und als Nachrichtensuche. Ist schon eingebaut.
- Aufwand: gering (vorhanden). Nötig sind aber eine Drossel von mindestens 5 s, Backoff und ein Zwischenspeicher. Weniger Abfragen bündeln (OR-Abfragen) statt vieler Einzelabfragen.
- Bewertung: 3/5 (Inhalt 5/5, Erreichbarkeit von geteilten IPs schlecht)
- Status: **getestet**. 429 bei 4 von 6 Abrufen. Ein `timelinetone`-Abruf brachte 200, aber mit leerem `{}`.

#### GDELT Context 2.0 API
- Link: https://blog.gdeltproject.org/announcing-the-gdelt-context-2-0-api/ | kostenlos | –
- Was es liefert: Treffer auf Satzebene mit Kontext-Ausschnitt (`snippet`), Zeit und Domain. Gut, um für das Modell zu zeigen, was genau gesagt wurde.
- Nutzen für die Arena: Ergänzt DOC, und das Werkzeug `nachrichten` liefert so echte Zitate statt nur Titel. Im Test war die Context API erreichbar, während DOC gedrosselt wurde.
- Aufwand: gering (Abfrage wie bei DOC).
- Bewertung: 4/5
- Status: **getestet**. 200, ca. 16 s Antwortzeit. Beispiel: „Crypto giant Binance hit by 6.3 billion dollar hack…“ (seendate 20261030T094705Z). Ein erster Versuch lief nach 25 s in eine Zeitüberschreitung, daher Timeout ≥ 40 s setzen.

#### GDELT 2.0 Rohdateien (Events, Mentions, GKG, alle 15 min)
- Link: http://data.gdeltproject.org/gdeltv2/lastupdate.txt · Doku: https://www.gdeltproject.org/data.html | kostenlos | –
- Was es liefert: Alle 15 min ZIP-CSV mit Ereignissen (CAMEO), Erwähnungen und GKG (Themen, Personen, Orte, **Ton/Tone**).
- Nutzen für die Arena: Ohne API-Limits und robust. Der Wächter (der ohnehin alle 15 min läuft) kann die GKG-Datei laden, nach Themen filtern (`ECON_*`, `WB_*`, Ticker/Firmennamen) und eine eigene Ton-Zeitreihe je Thema speichern.
- Aufwand: mittel. GKG ist ca. 4–15 MB gezippt pro 15 min, also nur streamend filtern und nicht ins Repo schreiben.
- Bewertung: 4/5
- Status: **getestet**. `lastupdate.txt` liefert 200 (über HTTPS, HTTP liefert 301), Dateien vom 20261030100000.

#### GDELT über Google BigQuery (Freikontingent)
- Link: https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/ · BigQuery-Freikontingent: https://cloud.google.com/bigquery/pricing | 1 TB Abfrage pro Monat gratis (ungeprüft für 2026) | –
- Was es liefert: Vollständige historische GDELT-Tabellen per SQL.
- Nutzen für die Arena: Nur für Auswertungen und Rücktests, nicht für den Livebetrieb. GKG-Abfragen scannen schnell mehrere TB, also besteht Kostenrisiko.
- Aufwand: mittel (GCP-Konto und Dienstkonto als Secret).
- Bewertung: 2/5
- Status: ungeprüft

#### Behörden- und Zentralbank-RSS (Fed, EZB, SEC; BLS)
- Link: Fed https://www.federalreserve.gov/feeds/feeds.htm · EZB https://www.ecb.europa.eu/home/html/rss.en.html · SEC https://www.sec.gov/about/rss-feeds (SEC verlangt einen deklarierten User-Agent mit E-Mail und max. 10 Anfragen/s: https://www.sec.gov/os/accessing-edgar-data) · BLS https://www.bls.gov/feed/ | gemeinfrei (US-Behörden) bzw. EZB-Nutzungsbedingungen | –
- Was es liefert: Pressemitteilungen, FOMC-Statements, Reden, EZB-Beschlüsse, SEC-Durchsetzungen, BLS-Veröffentlichungen (CPI, Arbeitsmarkt).
- Nutzen für die Arena: Sehr hoch für Kalshi-/Polymarket-Märkte zu Fed-Entscheid, CPI und Arbeitslosenquote. Sollte in `RSS` von `news.py` aufgenommen werden (das kostet nichts).
- Aufwand: sehr gering (Einträge im RSS-Wörterbuch).
- Bewertung: 5/5 (Fed, EZB, SEC), BLS 2/5 aus der Cloud
- Status: **getestet**. Fed 200, EZB 200, SEC 200, **BLS 403 (Akamai „Access Denied“)**. Den BLS-Veröffentlichungskalender stattdessen per Ersatz beziehen: FRED-Release-Kalender (`fred/releases/dates`, Schlüssel ist vorhanden). Ein ICS von BLS wurde nicht getestet.

#### Reddit (offizielle API / `.json` / RSS)
- Link: Data API Terms https://redditinc.com/policies/data-api-terms · Responsible Builder Policy https://support.reddithelp.com/hc/en-us/articles/42728983564564 (nur gelesen) · Wiki https://github.com/reddit-archive/reddit/wiki/API | OAuth: nichtkommerziell gratis, ca. 100 Anfragen/min (Drittquelle); seit Nov. 2025 laut Drittquellen nur mit Freigabe | –
- Was es liefert: Beiträge aus r/wallstreetbets, r/CryptoCurrency, r/Kalshi, r/Polymarket usw.
- Nutzen für die Arena: Mittel. Stimmung von Privatanlegern, oft verrauscht.
- Aufwand: RSS ist schon eingebaut. OAuth braucht ein Konto, einen Antrag und ein Secret.
- Bewertung: 2/5. Rechtlich grau: Die Data-API-Bedingungen verlangen für automatisierten Zugriff eigentlich eine registrierte App, und RSS ist dafür nicht ausdrücklich freigegeben. Empfehlung: höchstens die RSS-Fallbacks mit niedriger Frequenz (ttl 300 s ist ok) und mit ehrlichem User-Agent nutzen. Mittelfristig einen OAuth-App-Antrag stellen oder auf Reddit verzichten.
- Status: **getestet**. `hot.json` liefert **403** (HTML-Sperrseite), `.rss` liefert **200** (Atom, 50 kB). Die Abschaltung ohne Anmeldung (Mai 2026) ist nur aus Drittquellen gelesen, z. B. https://dev.to/tonywangca/why-reddit-blocked-unauthenticated-json-in-2026-and-how-to-still-get-reddit-data-58b9.

#### Hacker News (Algolia Search API + Firebase API)
- Link: https://hn.algolia.com/api · https://github.com/HackerNews/API (MIT) | kostenlos, ohne Schlüssel; Algolia ca. 10.000 Anfragen/h pro IP (Doku-Angabe, ungeprüft) | –
- Was es liefert: Volltextsuche nach Datum bzw. Relevanz sowie Top-, New- und Best-Stories.
- Nutzen für die Arena: Frühsignal bei Tech- und Krypto-Themen (Ausfälle, Hacks, KI-Releases). Nischig, aber sauber und stabil.
- Aufwand: sehr gering.
- Bewertung: 3/5
- Status: **getestet**. Algolia `search_by_date?query=bitcoin` liefert 200 (2 s), Firebase `topstories.json` liefert 200 (0,6 s).

#### Stocktwits (öffentliche Streams)
- Link: https://api.stocktwits.com/developers/docs (Registrierung neuer Apps laut Drittquellen eingeschränkt) · ToS https://stocktwits.com/terms | inoffiziell ohne Schlüssel erreichbar | –
- Was es liefert: Die letzten 30 Nachrichten je Ticker, inklusive **selbst deklarierter Stimmung `Bullish`/`Bearish`**.
- Nutzen für die Arena: Einfaches Stimmungsmaß je Ticker (Anteil bullish) für Aktien und Krypto (`BTC.X`).
- Aufwand: gering.
- Bewertung: 3/5. Die AGB untersagen nach meinem Kenntnisstand automatisierte Abrufe ohne Genehmigung (**ungeprüft**, nicht selbst gelesen). Vor Einbau die AGB lesen oder bei api@stocktwits.com nachfragen.
- Status: **getestet**. `streams/symbol/AAPL.json` liefert 200, 30 Nachrichten, die erste mit `{'basic':'Bearish'}`. Cloudflare-geschützt (cf-ray IAD), funktionierte aber ohne Challenge.

#### Bluesky AppView: `app.bsky.feed.searchPosts`
- Link: https://docs.bsky.app/docs/api/app-bsky-feed-search-posts · Rate-Limits: https://docs.bsky.app/docs/advanced-guides/rate-limits (leitet auf bsky.network um; nicht gelesen) · ToS https://bsky.social/about/support/tos | kostenlos; öffentliche Posts | –
- Was es liefert: Volltextsuche über alle öffentlichen Posts (Sortierung `latest`/`top`, `since`/`until`, `lang`), `hitsTotal`.
- Nutzen für die Arena: **Sehr interessant.** Es ist die einzige große offene Echtzeit-Social-Quelle mit Suche und damit Ersatz für X/Twitter bei Politik, Makro und Krypto. Agenten können „was sagt Social Media zu X“ abfragen.
- Aufwand: gering.
- Bewertung: 4/5
- Status: **getestet**. **`public.api.bsky.app` liefert 403** (Cloudflare-artige Sperrseite für Cloud-IPs). **`api.bsky.app` liefert 200** (3 Posts, `hitsTotal: 10000`). Drittquellen berichten von 403 auf Rechenzentrums-IPs und nach wenigen Abfragen. Eventuell braucht es einen App-Passwort-Login über einen eigenen Account (das ist **kein** Scraping hinter Login, sondern offizielle API). Laut ToS ist das wohl erlaubt (**nicht geprüft**).

#### Bluesky Trending Topics (`app.bsky.unspecced.getTrendingTopics`)
- Link: https://docs.bsky.app/docs/api/app-bsky-unspecced-get-trending-topics | kostenlos | –
- Was es liefert: Aktuelle Trendthemen mit Beschreibung.
- Nutzen für die Arena: Billiger Aufmerksamkeitsmonitor für den Wächter. Im Test enthielt er z. B. „Polymarket reportedly hacked“ und „Russian drones hit Ukrainian cities“, was direkt relevant für die Wettmärkte ist.
- Aufwand: sehr gering.
- Bewertung: 4/5 („unspecced“, also instabile Schnittstelle)
- Status: **getestet**. 200 auf beiden Hosts.

#### Bluesky Jetstream (Firehose als JSON-WebSocket)
- Link: https://github.com/bluesky-social/jetstream (★45 im neuen Repo, `updated_at` 2026-10-27; das alte Repo hat mehr Sterne) · Doku: https://docs.bsky.app/blog/jetstream | kostenlos, ohne Schlüssel | –
- Was es liefert: Echtzeitstrom aller Posts, filterbar nach Collection und DID.
- Nutzen für die Arena: Nur sinnvoll auf einem dauerhaften Server (Oracle-Phase): Stichwort-Zähler für Krypto/Ticker, Volumen-Spikes als Ereignis. In GitHub Actions höchstens als Stichprobe von 1–2 min.
- Aufwand: mittel (WebSocket-Client, Stichwortfilter).
- Bewertung: 3/5 (jetzt), 4/5 (mit Server)
- Status: **getestet** (nur Handshake). `jetstream2.us-east.bsky.network/subscribe` antwortet ohne Upgrade-Header mit 426, ist also erreichbar. Einen WebSocket-Stream habe ich nicht gelesen.

#### Mastodon (öffentliche Hashtag-Timelines)
- Link: https://docs.joinmastodon.org/methods/timelines/#tag | kostenlos; Regeln je Instanz (mastodon.social: https://mastodon.social/about) | –
- Was es liefert: Öffentliche Posts je Hashtag, z. B. `#bitcoin`.
- Nutzen für die Arena: Gering. Wenig Finanz-Publikum, und die Nutzerbasis ist kleiner als bei Bluesky.
- Aufwand: gering.
- Bewertung: 2/5
- Status: **getestet**. `mastodon.social/api/v1/timelines/tag/bitcoin` liefert 200.

#### Google Trends: „Trending now“-RSS
- Link: https://trends.google.com/trending/rss?geo=US | kostenlos; Google-ToS (automatisierte Abfragen generell untersagt, aber ein RSS-Feed ist zum Abonnieren gedacht; die Einschätzung ist grau) | –
- Was es liefert: Tägliche Top-Suchbegriffe je Land mit ungefährem Volumen und News-Links.
- Nutzen für die Arena: Aufmerksamkeitsindikator (z. B. Ereignis „Suchtrend zu gehaltener Position“).
- Aufwand: sehr gering.
- Bewertung: 3/5
- Status: **getestet**. 200. Beispiel-Titel: „gta delayed“, „playstation“.

#### Google Trends: pytrends / offizielle Trends-API (Alpha)
- Link: pytrends https://github.com/GeneralMills/pytrends (★3,7k, **archiviert**, letzte PyPI-Version 4.9.2 von 2023) · offizielle API: https://developers.google.com/search/blog/2025/07/trends-api | pytrends Apache-2.0; die API ist eine Alpha mit Bewerbung | –
- Was es liefert: Suchinteresse-Zeitreihen je Begriff und Region.
- Nutzen für die Arena: Mittel. pytrends liefert von Cloud-IPs bekanntlich oft 429.
- Aufwand: pytrends gering, aber unzuverlässig. Für die Alpha muss man sich bewerben.
- Bewertung: 2/5. Empfehlung: Bewerbung für die Alpha-API einreichen (kostet nichts). pytrends nicht als Abhängigkeit aufnehmen.
- Status: geprüft (Repo-Status per GitHub-Suche bestätigt: `archived: true`; API-Status aus dem Google-Blog vom Juli 2025, später nur Drittquellen).

#### Wikimedia Pageviews API
- Link: https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/ · Rate-Limits/User-Agent: https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits | kostenlos, Daten CC0 | –
- Was es liefert: Tägliche bzw. stündliche Aufrufe je Artikel sowie Top-1000-Artikel pro Tag.
- Nutzen für die Arena: Guter Aufmerksamkeitsproxy für Wahl- und Personenmärkte. Am 28.10. stand z. B. „2026_Israeli_legislative_election“ mit 925.801 Aufrufen auf Platz 2.
- Aufwand: gering. **User-Agent mit URL oder E-Mail ist Pflicht** (dann 200 statt 10 Anfragen/min).
- Bewertung: 4/5
- Status: **getestet**. `per-article/.../Bitcoin/daily` liefert mit vollständigem User-Agent 200 (z. B. 2.305 Aufrufe am 20.10.), ohne URL im User-Agent 429. `top/.../2026/10/28` liefert 200.

#### Wikipedia „Portal:Current events“
- Link: https://en.wikipedia.org/api/rest_v1/page/html/Portal%3ACurrent_events | CC BY-SA 4.0 | –
- Was es liefert: Kuratierte Tagesereignisse (Konflikte, Wahlen, Wirtschaft).
- Nutzen für die Arena: Kompakter, verlässlicher Überblick für den Tageskontext der Agenten.
- Aufwand: gering (HTML parsen, Abschnitt des aktuellen Tages).
- Bewertung: 3/5
- Status: **getestet**. REST-HTML liefert 200 (283 kB). Die Action-API `api.php?action=parse` lieferte mit kurzem User-Agent 429.

#### Finnhub (Market News, Company News)
- Link: https://finnhub.io/docs/api/market-news · ToS https://finnhub.io/terms-of-service | kostenloser Schlüssel; laut Drittquelle 60 Anfragen/min; kommerzielle Nutzung eingeschränkt | –
- Was es liefert: Allgemeine News und News je Ticker (inkl. Krypto/Forex), Earnings-Kalender, IPO-Kalender.
- Nutzen für die Arena: Mittel bis hoch für Aktien. Ticker-genaue News und der Earnings-Kalender (der laut PLAN noch fehlt).
- Aufwand: gering, ein Secret nötig.
- Bewertung: 4/5
- Status: **getestet** (ohne Schlüssel): 401 „Please use an API key.“ Der Endpunkt ist erreichbar.

#### Alpha Vantage NEWS_SENTIMENT
- Link: https://www.alphavantage.co/documentation/#news-sentiment · ToS https://www.alphavantage.co/terms_of_service/ | kostenloser Schlüssel; laut Drittquelle 25 Anfragen/Tag | –
- Was es liefert: News mit fertigen Stimmungswerten je Ticker und Thema.
- Nutzen für die Arena: Fertige Stimmung, aber das Kontingent ist sehr klein (25/Tag) und reicht nur für eine Tagesrunde.
- Aufwand: gering.
- Bewertung: 2/5
- Status: nur gelesen

#### Marketaux / newsdata.io / GNews / TheNewsAPI (Gratis-News-APIs)
- Link: https://www.marketaux.com/documentation · https://newsdata.io/documentation · https://gnews.io/docs · https://www.thenewsapi.com/documentation | Gratis-Pläne mit kleinen Tageslimits (Zahlen **nicht bestätigt**). Gratis-Pläne meist nur für Entwicklung bzw. nichtkommerziell. | –
- Was es liefert: Schlagzeilen-Suche. Marketaux zusätzlich Entitäten und Stimmung je Ticker.
- Nutzen für die Arena: Gering bis mittel. Gegenüber RSS, GDELT und der Websuche der Agenten bringen sie wenig Neues. Marketaux ist am interessantesten (Ticker-Zuordnung).
- Aufwand: gering, je ein Secret nötig.
- Bewertung: 2/5
- Status: GNews **getestet**: 400 „You did not provide an API key.“ (erreichbar). Die anderen sind nur gelesen bzw. ungeprüft.

#### Telegram-Kanäle (Vorschau `t.me/s/<kanal>`)
- Link: https://telegram.org/tos · Bot-API https://core.telegram.org/bots/api | Die Webvorschau ist öffentliches HTML ohne API; eine offizielle Lesemöglichkeit für fremde Kanäle gibt es nur per MTProto mit Nutzerkonto | –
- Was es liefert: Öffentliche Kanalposts (z. B. Krypto-News- und Konfliktkanäle).
- Nutzen für die Arena: Teils schneller als Medien bei Konflikten und Krypto-Hacks. Die Qualität schwankt aber stark, Desinformation ist häufig.
- Aufwand: HTML-Scraping; MTProto braucht ein Konto.
- Bewertung: 1/5. Die Webvorschau ist nicht als API gedacht, und die ToS für das automatisierte Auslesen fremder Kanäle sind unklar.
- Status: **getestet**. `t.me/s/durov` liefert 200 (HTML). Wird nicht empfohlen.

#### Sentiment-Modell: distilroberta-finetuned-financial-news-sentiment-analysis
- Link: https://hf.co/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis | **Apache-2.0**, 82 Mio. Parameter, 147 Mio. Downloads | –
- Was es liefert: negative/neutral/positive für englische Finanzschlagzeilen (trainiert auf Financial PhraseBank).
- Nutzen für die Arena: Billige, deterministische Stimmungszahl je Schlagzeile im Wächter (ohne LLM-Kosten), z. B. für das Ereignis „Stimmung zu gehaltener Position kippt“.
- Aufwand: gering. torch-CPU und transformers sind dank TimesFM ohnehin im Prognose-Workflow vorhanden.
- Bewertung: **4/5** (beste Lizenz und Geschwindigkeit)
- Status: **getestet** (CPU, 4 Kerne, torch 2.15 CPU): 100 Schlagzeilen in **0,61 s** (Batch 16), Laden ca. 9,5 s beim ersten Mal. Ausgabe: Binance-Hack → negative 1,00, Fed-Zinssenkung → neutral 0,92, Apple fällt → negative 1,00, „Oil steady“ → positive 0,98 (das letzte ist fragwürdig).

#### Sentiment-Modell: ProsusAI/finbert
- Link: https://hf.co/ProsusAI/finbert · https://github.com/ProsusAI/finBERT (★2,3k) | **CC BY-NC-SA 4.0** (nichtkommerziell, Share-Alike) | –
- Was es liefert: positive/negative/neutral für Finanztexte (BERT-base, 110 Mio. Parameter).
- Nutzen für die Arena: Der Klassiker. Für ein nichtkommerzielles Forschungsprojekt ist die Lizenz ok, aber bei einem späteren Echtgeld- oder kommerziellen Betrieb kritisch.
- Aufwand: gering.
- Bewertung: 3/5 (wegen der Lizenz)
- Status: **getestet**. Warm 100 Schlagzeilen in **1,3–1,5 s**. Der erste Lauf brauchte 10,7 s, also Download und Aufwärmen mitrechnen. Spitzen-RAM (RSS) ca. 750–890 MB. Ausgabe: Hack → negative 0,85, Fed → positive 0,51, Apple → negative 0,96, Öl → positive 0,61.

#### Sentiment-Modell: ElKulako/cryptobert
- Link: https://hf.co/ElKulako/cryptobert | **MIT**, 125 Mio. Parameter | –
- Was es liefert: Bearish/Neutral/Bullish, trainiert auf Krypto-Social-Media-Texten (u. a. ein Stocktwits-Krypto-Datensatz).
- Nutzen für die Arena: Passend für Bluesky-, Reddit- und Stocktwits-Texte zu Krypto.
- Aufwand: gering.
- Bewertung: 3/5
- Status: geprüft (Hub-Metadaten), nicht laufen gelassen.

#### Sentiment-Modell: cardiffnlp/twitter-roberta-base-sentiment-latest
- Link: https://hf.co/cardiffnlp/twitter-roberta-base-sentiment-latest | CC BY 4.0 | –
- Was es liefert: Allgemeine Stimmung für Social-Media-Text (nicht finanzspezifisch).
- Nutzen für die Arena: Für Bluesky und Mastodon allgemein geeignet.
- Aufwand: gering.
- Bewertung: 3/5
- Status: geprüft (Hub-Metadaten)

#### Sentiment-Modell: mrm8488/deberta-v3-ft-financial-news-sentiment-analysis
- Link: https://hf.co/mrm8488/deberta-v3-ft-financial-news-sentiment-analysis | MIT, 142 Mio. Parameter | –
- Was es liefert: Wie distilroberta, aber auf DeBERTa-v3-small. Laut Modellkarte etwas genauer (ungeprüft).
- Nutzen für die Arena: Alternative, falls distilroberta zu grob ist.
- Aufwand: gering. Braucht wohl zusätzlich `sentencepiece`/`tiktoken` (ungeprüft).
- Bewertung: 3/5
- Status: geprüft (Hub-Metadaten)

#### Sentiment-Modelle: FinancialBERT, finbert-tone, FinGPT-sentiment
- Link: https://hf.co/ahmedrachid/FinancialBERT-Sentiment-Analysis (keine Lizenzangabe) · https://hf.co/yiyanghkust/finbert-tone (keine Lizenzangabe) · https://hf.co/FinGPT/fingpt-sentiment_llama2-13b_lora (MIT-LoRA auf Llama-2-13B) | – | –
- Was es liefert: Finanzstimmung.
- Nutzen für die Arena: FinancialBERT und finbert-tone haben keine Lizenz im Hub, also rechtlich unklar. FinGPT braucht ein 13B-Modell, auf CPU in Actions nicht praktikabel. Das Liga-LLM kann Stimmung ohnehin selbst beurteilen.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (Hub-Metadaten)

#### YouTube-Transkripte / Podcasts
- Link: YouTube-ToS https://www.youtube.com/t/terms · Podcast-RSS (z. B. Odd Lots, Bankless) | – | –
- Was es liefert: Transkripte (YouTube nur inoffiziell, z. B. youtube-transcript-api) bzw. Audio, das man mit Whisper umwandeln müsste.
- Nutzen für die Arena: Gering im Verhältnis zum Aufwand. Die YouTube-ToS untersagen automatisierten Zugriff außerhalb der Data-API, und die Data-API liefert keine Transkripte fremder Videos. Podcast-RSS ist legal, aber Whisper auf CPU ist teuer.
- Aufwand: hoch.
- Bewertung: 1/5
- Status: ungeprüft (verworfen, s. u.)

#### B) Alternative Daten / Lage

#### Open-Meteo Forecast API
- Link: https://open-meteo.com/en/docs · ToS https://open-meteo.com/en/terms · Repo https://github.com/open-meteo/open-meteo (★6,6k, AGPL-3.0 für den Servercode) | **Daten CC BY 4.0**; kostenlose API nur **nichtkommerziell** und < 10.000 Abrufe/Tag, 5.000/h, 600/min | –
- Was es liefert: Stündliche und tägliche Vorhersagen aus vielen Modellen (GFS, ECMWF IFS, ICON, HRRR …) für beliebige Koordinaten.
- Nutzen für die Arena: **Sehr hoch für Kalshi-Wettermärkte** (KXHIGH*, Tageshöchsttemperatur in NYC, CHI, MIA, LAX, DEN, AUS …) und für Polymarket-Wetter. Die Agenten schätzen damit P(Tmax ∈ Bracket).
- Aufwand: gering. Pflicht: Zwischenspeicher und Quellenangabe „Weather data by Open-Meteo.com“ auf der Webseite.
- Bewertung: **5/5**
- Status: **getestet**. Forecast liefert 200 (NYC Tmax °F). **Später 429 „Daily API request limit exceeded“** auf der Sandbox-IP, weil sich viele Nutzer die IP teilen. Dasselbe Risiko besteht auf GitHub-Actions-Runnern.

#### Open-Meteo Ensemble API
- Link: https://open-meteo.com/en/docs/ensemble-api | wie oben | –
- Was es liefert: Alle Mitglieder von GFS-Ensemble (31), ECMWF IFS/AIFS ENS (51), ICON-EPS usw., also eine Verteilung statt eines Punktwerts.
- Nutzen für die Arena: **Der Kern für Wettermärkte.** Der Anteil der Mitglieder im Temperatur-Bracket ist direkt eine Wahrscheinlichkeit. Ein eigenes Werkzeug `wetter_wahrscheinlichkeit(station, datum, bracket)` wäre deterministisch und für alle Liga-Modelle gleich. Dabei auf Bias zur Abrechnungsstation (NWS CLI) korrigieren.
- Aufwand: gering bis mittel (Stationskoordinaten der Kalshi-Märkte, Umrechnung auf lokale Standardzeit wie im CLI).
- Bewertung: **5/5**
- Status: **getestet**. `models=gfs_seamless` liefert 200, **30 Mitglieder** plus Kontrolllauf (NYC 30.10. Kontrolle: 66,7 °F). Der zweite Abruf (`ecmwf_ifs025`) bekam bereits 429 (Tageslimit der geteilten IP).

#### NOAA NWS API (api.weather.gov) inklusive Daily Climate Report (CLI)
- Link: https://www.weather.gov/documentation/services-web-api | US-Behörde, gemeinfrei, ohne Schlüssel; User-Agent mit Kontakt verlangt | –
- Was es liefert: Punktvorhersagen, Stundenvorhersage, Stationsbeobachtungen (`stations/KNYC/observations`), Warnungen und **Textprodukte `CLI`**. Das CLI ist genau die Quelle, nach der Kalshi die Tagestemperatur-Märkte abrechnet (laut Kalshi-Hilfe und Kontraktbedingungen, z. B. https://kalshi-public-docs.s3.amazonaws.com/contract_terms/NHIGH.pdf).
- Nutzen für die Arena: **Sehr hoch.** (1) Abrechnung der Papier-Wetterwetten mit derselben Quelle wie Kalshi. (2) Beobachtetes Tagesmaximum bis jetzt, also gegen Tagesende fast sichere Wetten. (3) Rückfallquelle, wenn Open-Meteo drosselt. Warnungen werden schon genutzt (`lage.py`).
- Aufwand: gering (CLI ist Text und muss geparst werden).
- Bewertung: **5/5**
- Status: **getestet**. `points/40.78,-73.97` liefert 200, `stations/KNYC/observations/latest` liefert 200, `products/types/CLI/locations/NYC` liefert 200 (14 Produkte, das neueste um 2026-10-30T06:16Z).

#### NOAA NOMADS (GFS/HRRR GRIB2) und NOAA-Daten auf AWS Open Data
- Link: https://nomads.ncep.noaa.gov/ · https://registry.opendata.aws/noaa-gfs-bdp-pds/ | gemeinfrei; NOMADS drosselt bei mehr als ca. 120 Anfragen/min (ungeprüft) | –
- Was es liefert: Rohe Modellfelder (GRIB2), mit Filter-Skripten (`filter_gfs_0p25.pl`) auf Punkte und Variablen zuschneidbar.
- Nutzen für die Arena: Unabhängige Rückfallquelle für Ensemble-Daten (GEFS), falls Open-Meteo dicht ist.
- Aufwand: mittel bis hoch (GRIB2 braucht cfgrib/eccodes, Datenmengen).
- Bewertung: 3/5
- Status: **getestet** (nur Startseite): 200

#### ECMWF Open Data (IFS und AIFS, HRES und ENS)
- Link: https://www.ecmwf.int/en/forecasts/datasets/open-data · Client: https://pypi.org/project/ecmwf-opendata/ (Apache-2.0) | **seit 01.10.2025 ist der gesamte Echtzeit-Katalog CC BY 4.0, ohne Datenkosten** (ECMWF-Angabe) | –
- Was es liefert: Weltbestes Global-Ensemble (51 Mitglieder) als GRIB2, 4 Läufe pro Tag.
- Nutzen für die Arena: Zweite Ensemble-Quelle ohne Open-Meteo-Limit. Für Punktwerte ist Open-Meteo aber bequemer.
- Aufwand: mittel bis hoch (GRIB-Dateien von mehreren 100 MB, nur die nötigen Parameter laden).
- Bewertung: 3/5
- Status: **getestet**. `data.ecmwf.int/forecasts/` liefert 200 (Verzeichnisliste). Die Lizenz ist geprüft (Websuche mit ECMWF-Quellen).

#### Copernicus Climate Data Store (ERA5)
- Link: https://cds.climate.copernicus.eu/ | kostenlos mit Konto und Schlüssel, Copernicus-Lizenz | –
- Was es liefert: Reanalyse und historische Klimadaten.
- Nutzen für die Arena: Nur für die Kalibrierung der Wettermodelle (Bias je Station). Für den Livebetrieb ungeeignet, weil die Warteschlangen lang sind.
- Aufwand: mittel.
- Bewertung: 2/5. Open-Meteo `archive-api` liefert ERA5-Punktwerte einfacher (dort wurde allerdings 429 wegen des Tageslimits getestet).
- Status: ungeprüft

#### OpenSky Network REST API
- Link: https://openskynetwork.github.io/opensky-api/rest.html · ToS https://opensky-network.org/about/terms-of-use | anonym 400 Credits/Tag, angemeldet 4.000 (Doku). Laut Drittquelle ist **jede operative Nutzung in einem automatisierten System nur mit schriftlicher Vereinbarung** erlaubt (nicht selbst gelesen) | –
- Was es liefert: Live-Flugzeugpositionen (ADS-B).
- Nutzen für die Arena: Gering bis mittel (z. B. Flugaktivität über Konfliktgebieten, Regierungsjets). Das ist eher OSIRIS-Stil und nahe an Personenüberwachung.
- Aufwand: gering.
- Bewertung: 1/5. Lizenzrisiko, und Tracking von Personen-Jets fällt unter Personenüberwachung, also verwerfen bzw. nur Aggregate.
- Status: **getestet**. `states/all` (Schweiz-Box) liefert anonym 200 (17 kB).

#### ADS-B Exchange
- Link: https://www.adsbexchange.com/data/ | API kostenpflichtig (über RapidAPI bzw. Enterprise), ungeprüft | –
- Bewertung: 1/5 (kostenpflichtig, s. Verworfen)
- Status: ungeprüft

#### aisstream.io (AIS-Schiffsdaten per WebSocket)
- Link: https://aisstream.io/documentation · ToS: nicht gefunden | kostenloser Schlüssel (Konto über GitHub-Login), Drosselung je Schlüssel ohne Zahlen | –
- Was es liefert: Echtzeit-Schiffspositionen in Bounding-Boxen (Straße von Hormus, Bab el-Mandeb, Schwarzes Meer, Panamakanal).
- Nutzen für die Arena: Mittel. Tankerverkehr durch Hormus und das Rote Meer ist ein Signal für Öl- und Konfliktmärkte. Nur auf dem Server als Dauerverbindung sinnvoll; in Actions höchstens als 2–3-min-Stichprobe.
- Aufwand: mittel (WebSocket, Abo-Nachricht innerhalb von 3 s senden).
- Bewertung: 3/5 (ToS vor Einbau klären)
- Status: geprüft (Doku-Seite liefert 200). Keine Verbindung getestet, da ein Schlüssel nötig ist.

#### Global Fishing Watch API
- Link: https://globalfishingwatch.org/our-apis/documentation · Bedingungen: https://globalfishingwatch.org/our-apis/terms-of-use (nicht gelesen) | kostenloser Token, nach meinem Kenntnisstand nur nichtkommerziell (ungeprüft) | –
- Was es liefert: Schiffsaktivität, Häfen, Fischerei- und Transit-Ereignisse (mit Verzögerung).
- Nutzen für die Arena: Gering (Verzögerung, Fischerei-Fokus).
- Aufwand: mittel.
- Bewertung: 1/5
- Status: **getestet**. `v3/datasets` liefert 401 „invalid token“ (erreichbar).

#### NASA FIRMS (aktive Feuer)
- Link: https://firms.modaps.eosdis.nasa.gov/api/ | kostenloser MAP_KEY | –
- Nutzen für die Arena: Ist schon optional eingebaut (`lage.py`). Waldbrände sind für Versorger-Aktien und Konfliktindizien relevant.
- Bewertung: 3/5
- Status: nur gelesen (Code)

#### Sentinel Hub / Copernicus Data Space
- Link: https://dataspace.copernicus.eu/ | kostenloses Kontingent mit Konto | –
- Nutzen für die Arena: Satellitenbilder brauchen Bildanalyse und sind für die Arena überdimensioniert.
- Bewertung: 1/5
- Status: ungeprüft

#### EIA Open Data API v2 (Energie USA)
- Link: https://www.eia.gov/opendata/ | gemeinfrei, kostenloser Schlüssel (`DEMO_KEY` funktioniert für Tests) | –
- Was es liefert: Wöchentliche Rohöl- und Benzinvorräte (WPSR, mittwochs), Strom, Erdgas, Preise.
- Nutzen für die Arena: Hoch für Öl, Energie-ETFs und Kalshi-Benzinpreis-Märkte. Termine und Daten der Lagerbestandsberichte.
- Aufwand: gering (Secret `EIA_KEY`).
- Bewertung: 4/5
- Status: **getestet**. `api.eia.gov/v2/?api_key=DEMO_KEY` liefert 200 (Routen-Liste).

#### ENTSO-E Transparency Platform (Strom Europa)
- Link: https://transparency.entsoe.eu/ · API-Doku: https://documenter.getpostman.com/view/7009892/2s93JtP3F6 | kostenlos, Token per E-Mail-Antrag | –
- Was es liefert: Day-Ahead-Preise, Last, Erzeugung je Land.
- Nutzen für die Arena: Gering, solange keine europäischen Strom- oder Energiemärkte gehandelt werden.
- Bewertung: 2/5
- Status: **getestet**. 401 ohne Token (Antwortzeit 25 s).

#### GridStatus API (US-Netzbetreiber)
- Link: https://www.gridstatus.io/api | Gratis-Plan mit Schlüssel (Umfang ungeprüft); Open-Source-Bibliothek `gridstatus` (BSD-3, ungeprüft) | –
- Nutzen für die Arena: Gering bis mittel (ERCOT/PJM-Last bei Hitzewellen, Kalshi-Strommärkte, falls vorhanden).
- Bewertung: 2/5
- Status: **getestet**. 401 „Missing API Key.“

#### USDA NASS Quick Stats / WASDE
- Link: https://quickstats.nass.usda.gov/api · WASDE: https://www.usda.gov/oce/commodity/wasde | gemeinfrei, kostenloser Schlüssel | –
- Nutzen für die Arena: Gering (keine Agrar-Futures in der Arena).
- Bewertung: 1/5
- Status: **getestet**. 401 ohne Schlüssel.

#### TSA-Passagierzahlen
- Link: https://www.tsa.gov/travel/passenger-volumes | gemeinfrei | –
- Nutzen für die Arena: Kalshi hat (bzw. hatte) TSA-Märkte, außerdem ist es ein Reiseindikator für Airline-Aktien.
- Bewertung: 2/5. Aus der Cloud gesperrt (Akamai), und das Umgehen der Sperre ist nicht erlaubt.
- Status: **getestet**. 403 „Access Denied“.

#### ESPN Site API (Sportergebnisse, inoffiziell)
- Link: z. B. https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard | inoffiziell, keine dokumentierten Bedingungen; ESPN-ToS untersagen eigentlich automatisierten Zugriff (ungeprüft) | –
- Was es liefert: Spielpläne, Live-Spielstände und Quoten für NFL, NBA, MLB usw.
- Nutzen für die Arena: Mittel für Sport-Wettmärkte (Kalshi/Polymarket haben viele). Live-Stand als Ereignis.
- Aufwand: gering.
- Bewertung: 2/5 (rechtlich grau). Alternativen: Abrechnungsdaten direkt aus Kalshi- und Polymarket-Regeln, TheSportsDB (Gratis-Schlüssel, ungeprüft).
- Status: **getestet**. 200 (NFL-Scoreboard, Saison 2026).

#### ACLED (Konfliktereignisse)
- Link: https://acleddata.com/ · ToS (Version 2023): kommerzielle Nutzung verboten, Registrierung Pflicht, kein Scraping, keine abgeleiteten Ersatzprodukte | kostenlos für Registrierte, aber eingeschränkt | –
- Nutzen für die Arena: Hoch für Konflikt-Wettmärkte. Die Bedingungen (keine „secondary products“, Veröffentlichung in einem öffentlichen Repo bzw. auf einer öffentlichen Webseite) passen aber schlecht.
- Bewertung: 1/5 (Bedingungen, s. Verworfen)
- Status: nur gelesen (Sekundärquellen zu den ToS 2023)

#### ReliefWeb API (UN OCHA)
- Link: https://apidoc.reliefweb.int/ | kostenlos; **seit 2025 ist ein genehmigter `appname` Pflicht** (Antrag) | –
- Was es liefert: Lageberichte, Katastrophen, Krisen (UN und NGOs).
- Nutzen für die Arena: Mittel als Ergänzung zu GDACS.
- Aufwand: gering nach Genehmigung.
- Bewertung: 3/5
- Status: **getestet**. 403 „You are not using an approved appname“. Ein Antrag ist nötig.

#### CoinGecko Public API (Trending, Kategorien)
- Link: https://docs.coingecko.com/ · ToS https://www.coingecko.com/en/api_terms | Demo-Plan gratis (Schlüssel optional), Quellenangabe Pflicht | –
- Was es liefert: Trending Coins (Suchinteresse), Kategorien, Marktkapitalisierungen.
- Nutzen für die Arena: Krypto-Aufmerksamkeit („HYPE trendet“).
- Aufwand: gering.
- Bewertung: 3/5
- Status: **getestet**. `search/trending` liefert 200 ohne Schlüssel (Platz 1: Hyperliquid).

#### GitHub-Aktivität von Krypto-Projekten
- Link: https://docs.github.com/en/rest/metrics/statistics | in Actions mit `GITHUB_TOKEN` 1.000 Anfragen/h je Repo bzw. 5.000 mit PAT | –
- Was es liefert: Commit-Aktivität und Releases von Protokoll-Repos.
- Nutzen für die Arena: Gering. Kurzfristig kaum kursrelevant, außer bei Releases bzw. Hardforks (dann besser Release-RSS `github.com/<org>/<repo>/releases.atom`).
- Bewertung: 2/5
- Status: ungeprüft. In der Sandbox sperrt der Proxy fremde Repos (403), der Grund liegt also bei der Sandbox, nicht bei GitHub.

#### Umfragedaten (538 / Aggregatoren)
- Link: früher https://projects.fivethirtyeight.com/polls/ | – | –
- Was es liefert: 538 wurde 2025 geschlossen. Die CSV-URL leitet heute auf `abcnews.go.com/politics` um.
- Nutzen für die Arena: Für Wahlmärkte sind Umfragen wertvoll. Mögliche Alternativen (ungeprüft): Wikipedia-Umfragetabellen (CC BY-SA, Parsing), RealClearPolling (ToS prüfen), Silver Bulletin (Abo).
- Bewertung: 2/5
- Status: **getestet**. 302, Umleitung auf ABC News.

#### Box-Office, App-Ranglisten, Spotify-Charts
- Link: Box Office Mojo (IMDb-ToS untersagen Scraping), Apple Marketing Tools RSS https://rss.marketingtools.apple.com/ (öffentlich, Nutzungsbedingungen ungeprüft), Spotify Charts (Login, keine API) | – | –
- Nutzen für die Arena: Polymarket und Kalshi haben solche Märkte (Box Office, „#1 App“, Spotify-Charts). Apple-RSS wäre die sauberste Quelle für App-Ranglisten.
- Bewertung: 2/5 (Apple-RSS), Rest 1/5
- Status: ungeprüft

#### C) MCP-Server für Finanzdaten und Trading

**Vorbemerkung zum MCP-Connector der Messages API** (Doku: https://platform.claude.com/docs/en/agents-and-tools/mcp-connector, nur gelesen):
- Server werden über den Parameter `mcp_servers` mit Typ `url` eingebunden, nur als **Remote-Server über HTTPS**.
- Beta-Header: laut aktueller Seite `mcp-client-2025-11-20`; `2025-04-04` ist veraltet.
- Laut FastMCP-Doku werden **nur Tools** unterstützt (keine Resources oder Prompts).
- Nicht verfügbar auf Bedrock/Vertex. OAuth-Token muss der Aufrufer selbst besorgen.
- **Lokale stdio-Server (uvx/npx) gehen damit nicht direkt.** Man müsste sie selbst als HTTPS-Dienst hosten oder per MCP-Client-Bibliothek im eigenen Code ansprechen.
- **Die Liga-Modelle (Gemini, DeepSeek, Kimi …) haben diesen Connector nicht.**

#### Alpaca MCP Server (offiziell)
- Link: https://github.com/alpacahq/alpaca-mcp-server | ★1.051, `updated_at` 2026-10-30, Lizenz laut Repo MIT (ungeprüft) | kostenloses Paper-Konto
- Was es liefert: Kurse, Bars, Optionsketten, Konto, Orders (Paper und Live) für Aktien, ETFs, Krypto und Optionen.
- Nutzen für die Arena: Nur als Vorlage. Die Arena hat eine eigene Papier-Börse. Ein MCP mit echtem Order-Werkzeug darf den Agenten **nicht** gegeben werden (Echtgeld nur nach Rouvens Ja). Für Daten besser direkt `alpaca-py` nutzen.
- Aufwand: gering (lokal, `uvx`), Remote-Hosting nötig für den Connector.
- Bewertung: 2/5
- Status: geprüft (GitHub-Metadaten)

#### Massive (vormals Polygon.io) MCP
- Link: https://github.com/massive-com/mcp_massive | ★399, `updated_at` 2026-10-29 | Massive-Gratis-Plan (5 Anfragen/min, Daten vom Vortag; ungeprüft für 2026)
- Was es liefert: Aktien-, Options-, Forex- und Krypto-Marktdaten, Referenzdaten, News.
- Nutzen für die Arena: Mit dem Gratis-Plan kaum nützlich (verzögert, 5/min).
- Bewertung: 2/5
- Status: geprüft (GitHub-Metadaten)

#### Financial Datasets MCP
- Link: https://github.com/financial-datasets/mcp-server | ★2.315, `updated_at` 2026-10-29 | API kostenpflichtig (Pay-per-use; Gratis-Umfang ungeprüft)
- Was es liefert: Bilanzen, Kurse, News, SEC-Filings, Krypto.
- Nutzen für die Arena: Gut gemacht, aber kostenpflichtig.
- Bewertung: 2/5
- Status: geprüft (Metadaten)

#### Alpha Vantage MCP (offiziell)
- Link: https://github.com/alphavantage/alpha_vantage_mcp · Remote: https://mcp.alphavantage.co/ (ungeprüft) | ★224, `updated_at` 2026-10-30 | kostenloser Schlüssel, 25 Anfragen/Tag
- Was es liefert: Alle Alpha-Vantage-Endpunkte (Kurse, Fundamentaldaten, NEWS_SENTIMENT, Indikatoren) als Tools.
- Nutzen für die Arena: Es gibt eine Remote-Variante, die mit dem Connector direkt nutzbar wäre. Das Gratis-Kontingent ist aber winzig.
- Bewertung: 2/5
- Status: geprüft (Metadaten); Remote-URL ungeprüft

#### CoinGecko MCP (offiziell, Remote, ohne Schlüssel)
- Link: https://docs.coingecko.com/ai-integration/mcp-server · Endpunkt `https://mcp.api.coingecko.com/mcp` (Streamable HTTP) bzw. `/sse` | gratis mit geteiltem Rate-Limit, ohne Schlüssel | SDK-Repo coingecko/coingecko-typescript ★59
- Was es liefert: Preise, Märkte, Trending, Kategorien, On-Chain (GeckoTerminal) als Tools.
- Nutzen für die Arena: **Der einzige Kandidat, der ohne Schlüssel sofort per Connector in die Claude-Fonds passt.** Allerdings gilt dann: Nur die Claude-Fonds bekommen ihn, die Ausgaben sind nicht deterministisch, es kostet zusätzliche Tokens und das Rate-Limit ist geteilt.
- Aufwand: sehr gering (ein Eintrag in `mcp_servers`).
- Bewertung: 3/5
- Status: geprüft (CoinGecko-Doku per Websuche). Den Endpunkt selbst habe ich nicht aufgerufen.

#### CCXT-MCP (Community)
- Link: https://github.com/doggybee/mcp-server-ccxt | ★145, `updated_at` 2026-09-16 | MIT (ungeprüft)
- Was es liefert: Kurse, Orderbücher und OHLCV von über 100 Börsen über CCXT.
- Nutzen für die Arena: Die Arena hat eigene Adapter (Coinbase, Kraken, Deribit). CCXT als **Python-Bibliothek** (MIT) wäre eher eine Erweiterung der Adapter als ein MCP.
- Bewertung: 2/5
- Status: geprüft (Metadaten)

#### Prediction-Market-MCP (Polymarket, PredictIt, Kalshi)
- Link: https://github.com/JamesANZ/prediction-market-mcp | ★38, `updated_at` 2026-10-23, MIT | gratis
- Was es liefert: Lesende Wettmarktdaten.
- Nutzen für die Arena: Keiner, weil die Arena das bereits besser hat (`markt_suche`, `markt_details`, `orderbuch`).
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### prediction-mcp (Kalshi + Polymarket)
- Link: https://github.com/shaanmajid/prediction-mcp | ★11, **archiviert** | –
- Bewertung: 0/5 (archiviert)
- Status: geprüft

#### Yahoo-Finance-MCP / MaverickMCP
- Link: https://github.com/Alex2Yang97/yahoo-finance-mcp (★364) · https://github.com/wshobson/maverick-mcp (★714, Yahoo-Daten, technische Analyse, Backtests) | gratis, aber Yahoo-ToS (inoffiziell, s. STATUS: Yahoo drosselt Cloud-IPs) | –
- Nutzen für die Arena: Dieselbe Yahoo-Schwäche wie der vorhandene Adapter.
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### OpenBB (Platform mit MCP-Server)
- Link: https://github.com/OpenBB-finance/OpenBB · MCP: `openbb-mcp-server` (ungeprüft) | Lizenz AGPL-3.0 (ungeprüft) | –
- Was es liefert: Einheitliche Schnittstelle zu vielen Datenanbietern (viele davon brauchen Schlüssel).
- Nutzen für die Arena: Mittel als Bibliothek. Die AGPL ist für ein öffentliches Repo kein Problem, aber nicht MIT/Apache.
- Bewertung: 2/5
- Status: ungeprüft (in der GitHub-Suche nicht gefunden, Repo-Name eventuell anders)

#### SEC-EDGAR-MCP
- Link: https://github.com/stefanoamorelli/sec-edgar-mcp | ★382, `updated_at` 2026-10-30, Lizenz laut README AGPL (ungeprüft) | gratis (SEC-Daten)
- Was es liefert: Filings, XBRL-Finanzdaten, Insider-Transaktionen (Form 4).
- Nutzen für die Arena: Insider-Käufe und 8-K-Meldungen sind wertvoll. Direkt über `data.sec.gov` (JSON, ohne Schlüssel) ist es aber einfacher und deterministischer als eigenes Werkzeug.
- Bewertung: 2/5 (als MCP), 4/5 (EDGAR direkt als eigenes Werkzeug)
- Status: geprüft (Metadaten)

#### FRED-MCP-Server
- Link: https://github.com/stefanoamorelli/fred-mcp-server | ★130, `updated_at` 2026-10-30 | FRED-Schlüssel gratis
- Nutzen für die Arena: FRED ist schon als `makro` eingebaut.
- Bewertung: 1/5
- Status: geprüft (Metadaten)

#### Twelve Data MCP
- Link: https://github.com/twelvedata/mcp | ★85, `updated_at` 2026-10-28 | Gratis-Plan 800 Anfragen/Tag (ungeprüft)
- Nutzen für die Arena: Möglicher Ersatz für Yahoo bei Aktienkursen. Dann aber besser die REST-API direkt im Adapter nutzen.
- Bewertung: 2/5 (als MCP), 3/5 (REST als Yahoo-Ersatz)
- Status: geprüft (Metadaten)

#### Octagon MCP / GDELT-MCP
- Link: Octagon (https://github.com/OctagonAI/octagon-mcp-server, ungeprüft; kommerzielle Research-Agenten); GDELT-MCPs: nur kleine Community-Projekte (ungeprüft) | – | –
- Bewertung: 1/5
- Status: ungeprüft (per Suche nicht bestätigt)

#### awesome-mcp-servers (Liste, Abschnitt Finance & Fintech)
- Link: https://github.com/punkpeye/awesome-mcp-servers | ★97k, `updated_at` 2026-10-30 | –
- Nutzen für die Arena: Sammelstelle. Die Qualität der Einträge schwankt stark, und es gibt viele Krypto-Wallet- bzw. Trading-Server mit Schlüsselzugriff. Vorsicht wegen Lieferkette (Supply Chain).
- Bewertung: –
- Status: geprüft (Metadaten)

#### Fazit zu MCP gegenüber eigenen Werkzeugen
**Eigene Werkzeuge sind für die Arena besser. MCP lohnt sich (fast) nicht.** Die Gründe:

1. **Gleiche Werkzeuge für alle Liga-Modelle.** Der MCP-Connector existiert nur in der Anthropic-API. Gemini, DeepSeek, Kimi, OpenRouter usw. hätten andere oder keine Werkzeuge, und der Ligavergleich wäre verfälscht. Eigene Funktionen in `tools.py` gelten für alle gleich.
2. **Determinismus und Reproduzierbarkeit.** Eigene Werkzeuge lesen den **gemeinsamen Daten-Schnappschuss** des Wächters, sodass jeder Fonds dieselben Zahlen sieht und sich das im Log nachvollziehen lässt. MCP-Abrufe liefern zu leicht unterschiedlichen Zeitpunkten andere Daten.
3. **Kosten.** MCP-Server liefern oft lange JSON-Antworten (Token-Kosten). Eigene Werkzeuge kürzen das gezielt (`_kurz`, `MAX_AUSGABE`). Viele Finanz-MCPs brauchen außerdem kostenpflichtige Schlüssel.
4. **Sicherheit.** Trading-MCPs (Alpaca, CCXT) haben Order-Tools. Ein Agent mit Order-Rechten am echten Broker widerspricht der Regel „Echtgeld nur nach Ja“. Community-MCPs sind zudem ein Lieferkettenrisiko.
5. **Technik.** Der Connector kann nur Remote-HTTPS-Server einbinden. Die meisten Finanz-MCPs laufen lokal über stdio und müssten erst gehostet werden.

**Ausnahme bzw. Option:** Der CoinGecko-Remote-MCP (ohne Schlüssel) wäre ein billiges Experiment, z. B. als *zusätzliches* Werkzeug nur für einen Claude-Fonds. Er sollte dann als „Abweichung“ markiert werden. Sinnvoller ist es, MCP-Server als **Ideenquelle** zu nutzen: Welche Tools bieten sie an, und welche davon lohnen sich nachgebaut?

---

### Live-Testergebnisse

Sandbox-IP, 30.10.2026 ca. 10:00 UTC, User-Agent `ki-trader-arena-research/0.1 (https://github.com/rouvenwieland/ki-trader-arena)`.

| Quelle | Endpunkt | HTTP | Zeit | Ergebnis / Hinweis |
|---|---|---|---|---|
| GDELT DOC 2.0 | `api/v2/doc/doc?mode=artlist` | **429** (4 von 6) | 7–18 s | „limit requests to one every 5 seconds“, trotz Pausen. Ein `timelinetone` brachte 200, aber leeres `{}` |
| GDELT Context 2.0 | `api/v2/context/context` | 200 | 16 s | Artikel mit Snippet (Binance-Hack). Erster Versuch: Zeitüberschreitung nach 25 s |
| GDELT Rohdateien | `data.gdeltproject.org/gdeltv2/lastupdate.txt` | 200 | 0,2 s | über HTTPS; HTTP liefert 301 |
| HN Algolia | `search_by_date?query=bitcoin` | 200 | 2,0 s | ok |
| HN Firebase | `v0/topstories.json` | 200 | 0,6 s | ok |
| Bluesky Suche | `public.api.bsky.app/...searchPosts` | **403** | 0,5 s | Sperrseite für Cloud-IP |
| Bluesky Suche | `api.bsky.app/...searchPosts` | 200 | 0,4 s | 3 Posts, hitsTotal 10000 |
| Bluesky Trends | `app.bsky.unspecced.getTrendingTopics` | 200 | 0,3 s | u. a. „Polymarket reportedly hacked“ |
| Bluesky Jetstream | `jetstream2.us-east…/subscribe` | 426 | 0,3 s | erreichbar (Upgrade nötig) |
| Mastodon | `mastodon.social/api/v1/timelines/tag/bitcoin` | 200 | 0,5 s | ok |
| Wikimedia Pageviews | `per-article/.../Bitcoin/daily` | 429, dann **200** | 0,4 s | 429 ohne URL im User-Agent, 200 mit vollständigem User-Agent |
| Wikimedia Top | `top/en.wikipedia/.../2026/10/28` | 200 | 0,5 s | Platz 2: 2026 Israeli legislative election |
| Wikipedia Current events | REST `page/html/Portal:Current_events` | 200 | 0,8 s | api.php lieferte vorher 429 |
| Google Trends RSS | `trends.google.com/trending/rss?geo=US` | 200 | 0,2 s | ok |
| Reddit JSON | `/r/wallstreetbets/hot.json` | **403** | 0,4 s | gesperrt |
| Reddit RSS | `/r/wallstreetbets/.rss` | 200 | 0,6 s | Atom 50 kB |
| Stocktwits | `api/2/streams/symbol/AAPL.json` | 200 | 0,5 s | 30 Nachrichten mit Bullish/Bearish |
| Telegram-Vorschau | `t.me/s/durov` | 200 | 0,7 s | HTML (nicht empfohlen) |
| Fed RSS | `federalreserve.gov/feeds/press_all.xml` | 200 | 0,1 s | ok |
| EZB RSS | `ecb.europa.eu/rss/press.html` | 200 | 0,5 s | ok |
| SEC RSS | `sec.gov/news/pressreleases.rss` | 200 | 0,3 s | ok |
| BLS RSS | `bls.gov/feed/bls_latest.rss` | **403** | 0,2 s | Akamai-Sperre |
| Finnhub | `api/v1/news` | 401 | 0,3 s | Schlüssel nötig |
| GNews | `api/v4/top-headlines` | 400 | 0,2 s | Schlüssel nötig |
| Open-Meteo Forecast | `api.open-meteo.com/v1/forecast` | 200 | 0,6 s | NYC Tmax °F |
| Open-Meteo Ensemble | `ensemble-api…?models=gfs_seamless` | 200 | 0,7 s | 30 Mitglieder plus Kontrolllauf |
| Open-Meteo Ensemble/Archiv | `models=ecmwf_ifs025`, `archive-api` | **429** | 0,5 s | „Daily API request limit exceeded“ (geteilte IP) |
| NWS Punkt | `api.weather.gov/points/40.78,-73.97` | 200 | 0,5 s | ok |
| NWS Beobachtung | `stations/KNYC/observations/latest` | 200 | 0,3 s | ok |
| NWS CLI (Kalshi-Abrechnung) | `products/types/CLI/locations/NYC` | 200 | 0,4 s | 14 Produkte, neuestes 06:16Z |
| NOMADS | Startseite | 200 | 0,4 s | ok |
| ECMWF Open Data | `data.ecmwf.int/forecasts/` | 200 | 1,8 s | Verzeichnis |
| OpenSky | `api/states/all` (Box CH) | 200 | 0,9 s | anonym ok, ToS problematisch |
| aisstream | Doku-Seite | 200 | 0,8 s | Stream nicht getestet (Schlüssel) |
| Global Fishing Watch | `v3/datasets` | 401 | 0,3 s | Token nötig |
| EIA | `api.eia.gov/v2/?api_key=DEMO_KEY` | 200 | 0,5 s | ok |
| ENTSO-E | `web-api.tp.entsoe.eu/api` | 401 | 25 s | Token nötig |
| GridStatus | `api.gridstatus.io/v1/datasets` | 401 | 0,5 s | Schlüssel nötig |
| USDA NASS | `quickstats…/get_counts` | 401 | 0,3 s | Schlüssel nötig |
| TSA | `tsa.gov/travel/passenger-volumes` | **403** | 0,5 s | Akamai-Sperre |
| ReliefWeb | `api.reliefweb.int/v2/reports` | **403** | 0,2 s | genehmigter `appname` nötig |
| ESPN | `site.api.espn.com/.../nfl/scoreboard` | 200 | 0,2 s | inoffiziell |
| CoinGecko | `api/v3/search/trending` | 200 | 0,2 s | ohne Schlüssel ok |
| 538-Umfragen | `projects.fivethirtyeight.com/polls/data/...csv` | 302 | 0,3 s | Umleitung auf abcnews.go.com (eingestellt) |
| FinBERT (CPU) | ProsusAI/finbert, 100 Schlagzeilen | – | 1,3–1,5 s warm (10,7 s kalt) | RSS ca. 750–890 MB, CC BY-NC-SA |
| DistilRoBERTa-fin (CPU) | mrm8488/distilroberta-…, 100 Schlagzeilen | – | 0,61 s | Apache-2.0, Laden ca. 9,5 s beim ersten Mal |

Die venv für den FinBERT-Test (1,2 GB plus 0,7 GB Modelle) wurde danach gelöscht.

---

_Verworfene Kandidaten dieser Kategorie: siehe [ANHANG-verworfen.md](ANHANG-verworfen.md), Abschnitt „7. Nachrichten/Stimmung, alternative Daten, MCP-Server“._

### Top-Empfehlungen

1. **Wetter-Werkzeug für Kalshi- und Polymarket-Wettermärkte (größter neuer Vorteil).** Open-Meteo Ensemble (GFS 31 plus ECMWF 51 Mitglieder) liefert P(Tmax im Bracket) deterministisch für alle Liga-Modelle. Abgerechnet wird mit **NWS CLI**, derselben Quelle wie bei Kalshi. Das beobachtete Tagesmaximum kommt aus `stations/<ICAO>/observations`. Nötig sind ein Zwischenspeicher (z. B. 1 Abruf je Stadt und Modelllauf) und als Rückfall NWS-Punktvorhersage bzw. ECMWF Open Data, weil das Open-Meteo-Tageslimit auf geteilten IPs schnell erreicht ist. Quellenangabe auf der Webseite nicht vergessen (CC BY 4.0).
2. **Behörden-RSS sofort ergänzen:** Fed (`press_all.xml`), EZB, SEC-Presse. Das sind Einzeiler im `RSS`-Wörterbuch, und sie sind direkt relevant für Fed-, Zins- und Regulierungsmärkte. Den BLS-Kalender über FRED-`releases/dates` beziehen.
3. **Bluesky als Social-Quelle:** `getTrendingTopics` im Wächter (Aufmerksamkeitsereignis) und `searchPosts` über **`api.bsky.app`** (nicht `public.api…`, das liefert 403) im Werkzeug `nachrichten`. Bei Sperren einen App-Passwort-Login mit eigenem Account nutzen. Später Jetstream auf dem Oracle-Server.
4. **GDELT robuster machen:** Für die Ton- und Volumen-Zeitreihe die 15-min-**GKG-Rohdateien** im Wächter streamend filtern (keine Rate-Limits). Die **Context API** statt DOC für Zitate verwenden. DOC nur mit mindestens 6 s Abstand, Backoff und Zwischenspeicher.
5. **Aufmerksamkeitsindikatoren:** Wikimedia-Pageviews (Top-Liste plus je Artikel; User-Agent mit Repo-URL!) und Google-Trends-RSS. Beide sind gratis, legal und stabil. Die Bewerbung für die offizielle Google-Trends-API (Alpha) lohnt sich.
6. **Lokales Sentiment im Wächter:** `mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis` (Apache-2.0, 0,6 s pro 100 Schlagzeilen auf CPU) statt FinBERT (NC-Lizenz, ca. 2× langsamer). Für Krypto-Social optional CryptoBERT (MIT). Die Zahl ergänzt das LLM-Urteil, sie ersetzt es nicht.
7. **Reddit-Pfad bereinigen:** `.json` entfernen (liefert 403), nur RSS mit geringer Frequenz behalten oder eine OAuth-App beantragen. Bei RSS den echten Zeitstempel aus `<updated>` lesen statt `time.time()`.
8. **Mit Gratis-Schlüssel als Secret:** Finnhub (Ticker-News plus **Earnings-Kalender**, der laut PLAN fehlt) und EIA (Öl-Lagerbestände). Optional ReliefWeb (`appname` beantragen) als GDACS-Ergänzung.
9. **MCP: nicht als Datenquelle für die Liga.** Eigene Werkzeuge bleiben, denn sie gelten für alle Modelle gleich, liefern Schnappschuss-Determinismus, kosten weniger Tokens und sind sicherer. Höchstens den CoinGecko-Remote-MCP (ohne Schlüssel) als markiertes Experiment in *einem* Claude-Fonds testen.


---

## 8. LLM-Kosten, Gratis-Modelle, Dashboards

## Kategorie 8: Kosten-Effizienz, Gratis-/Billig-Modelle, Dashboards

Stand: 2026-10-30. Repo nur gelesen (llm.py, loop.py, budget.py, route.py, review.py, prompts.py, config.json, site.py, index.html, DECISIONS.md, STATUS.md, data/budget_log.jsonl).
Quellen für Anthropic-Preise und -Funktionen: Skill `claude-api` (Stand 2026-10-06) und die offiziellen Seiten unter platform.claude.com, am 30.10. live abgerufen (Pricing, Batch Processing, Web Search Tool, Prompt Caching, Token Counting, Memory Tool).
Testdateien liegen unter `‹Sandbox›/test-llm/dl/`.
Statuswerte: **getestet** = selbst per curl/Skript geprüft · **geprüft** = in offizieller Doku nachgelesen · **nur gelesen** = nur Sekundärquellen · **ungeprüft** = Schätzung/Annahme.

---

### Kategorie: A – Kosten-Effizienz für die Claude-Fonds

#### A1 Prompt-Caching: Präfix so umbauen, dass alle drei Fonds ihn teilen
- Link: https://platform.claude.com/docs/en/build-with-claude/prompt-caching | Lizenz/Kosten: Teil der API. Sonnet 5.5: Schreiben (5 min) 2,50 $/MTok, Schreiben (1 h) 4 $/MTok, Lesen **0,10 $/MTok** (0,05×)
- Was es kann: Cache-Treffer sind reine Präfix-Übereinstimmungen in der Reihenfolge tools → system → messages, mit höchstens 4 Breakpoints. Für Agentenschleifen empfiehlt die Doku einen expliziten Breakpoint am Ende des statischen Präfixes und zusätzlich automatisches Caching (top-level `cache_control`) für den wachsenden Verlauf.
- Nutzen für die Arena: Heute steht in `prompts.SYSTEM` schon in der zweiten Zeile „DEIN FONDS: {name} … Persönlichkeit“. Damit unterscheidet sich der Präfix je Fonds, und jeder der drei Fonds schreibt pro Lauf rund 10–11 k Token neu in den Cache (im Log: erster Schritt jeder Runde `cache_schreiben` ≈ 10 070–11 699). Besser wäre diese Reihenfolge: Werkzeuge → gemeinsamer SYSTEM-Text → Schnappschuss (innerhalb eines Laufs für alle Fonds gleich) → **expliziter Breakpoint** → Fondsname, Persönlichkeit, Limits, Notizbuch und Portfolio als User-Text. Die drei Fonds starten im Abstand von Sekunden, deshalb reicht die 5-Minuten-TTL. Ersparnis: etwa 2 × ~9 k Token × (2,50 − 0,10) $/MTok ≈ **0,04 $ pro Lauf** (≈ 5–6 % der Rundenkosten).
- Aufwand: klein (Prompt-Aufteilung, ein `cache_control` am Systemblock). Mit `usage.cache_read_input_tokens` beim 2. und 3. Fonds prüfen.
- Bewertung: 4/5
- Status: geprüft (Doku), Ersparnis gerechnet aus dem eigenen Log

#### A2 1-Stunden-TTL – für die Arena eher nicht
- Link: wie A1, Abschnitt „Choosing the TTL“ | Kosten: Schreiben 2× statt 1,25×
- Was es kann: Hält Einträge 1 h. Laut Doku lohnt sich das erst ab drei Requests und nur bei Abständen zwischen 5 und 60 Minuten.
- Nutzen für die Arena: Ereignisläufe liegen mindestens 45 Minuten auseinander, die tägliche Runde einmal am Tag. Ein geteilter Präfix aus A1 (ohne Schnappschuss, ~4–5 k Token) würde nur dann lohnen, wenn mehrere Läufe in eine Stunde fallen. Erst nach A1 messen.
- Aufwand: eine Zeile (`"ttl": "1h"`). Wichtig: Einträge mit 1-h-TTL müssen vor 5-min-Einträgen stehen.
- Bewertung: 2/5
- Status: geprüft (Doku)

#### A3 Preisfaktoren in config.json korrigieren (Budget-Genauigkeit)
- Link: https://platform.claude.com/docs/en/about-claude/pricing | Kosten: –
- Was es kann: Laut offizieller Preisseite kosten Cache-Treffer auf **Sonnet 5.5 und Opus 5.5 0,05×** des Eingabepreises (0,10 $ bzw. 0,20 $/MTok), auf Haiku 5.5 0,1×. In `config.json` steht pauschal `cache_lesen_faktor: 0.1`. Zusätzlich gilt: Bei Haiku 5.5 steigen die Preise für Prompts über 100 k Token auf 0,50/2,50 $.
- Nutzen für die Arena: Das Budget überschätzt die Kosten heute um etwa 23 % (Faktor 0,1 plus 15 % Aufschlag). Das ist sicher, verschenkt aber Spielraum. Der Faktor sollte je Modell in der Konfiguration stehen.
- Aufwand: sehr klein
- Bewertung: 3/5
- Status: geprüft (Doku), gegen das Log nachgerechnet

#### A4 Opus-Wochen-Review: Antwort wird abgeschnitten (Fehler) → Streaming + größeres max_tokens + Batch
- Link: https://platform.claude.com/docs/en/build-with-claude/batch-processing | Kosten: Batch −50 % auf Ein- und Ausgabe (Opus 5.5: 2/10 $ statt 4/20 $). Lässt sich mit Caching kombinieren.
- Was es kann: Asynchron. Die meisten Batches sind laut Doku in unter 1 h fertig, spätestens nach 24 h. Ergebnisse bleiben 29 Tage abrufbar.
- Nutzen für die Arena: **Fund im Log:** Der Review-Aufruf hat `aus: 8000` = `max_tokens` erreicht. `reports/2026-W44.md` endet mitten im Satz („…(0“). Der abschließende JSON-Block mit den Regeln fehlt deshalb, und `review.py` schreibt keine Regeln ins Notizbuch. Ursache: Opus 5.5 denkt immer (adaptive Thinking, lässt sich nicht abschalten), und die Denk-Tokens zählen zu `max_tokens`. Abhilfe: `max_tokens` ≈ 32 000 mit Streaming (`.stream()` + `get_final_message()`), `stop_reason == "max_tokens"` prüfen. Das Review ist ein Einzelaufruf ohne Werkzeuge und nicht zeitkritisch, passt also ideal in die Batch-API: etwa 0,10–0,20 $ Ersparnis pro Woche. Das ist wenig Geld, aber der Umbau ist ohnehin fällig. Ein Cache-Write ist beim Einzelaufruf unnötig: Er kostet 1,25×, und es folgt kein Lesezugriff.
- Aufwand: klein (Streaming) bzw. mittel (Batch: einreichen, im nächsten Workflow-Lauf abholen)
- Bewertung: 5/5 (Fehlerbehebung), Batch-Anteil 3/5
- Status: getestet (Log und Report geprüft), Batch geprüft (Doku)

#### A5 Batch-API für die tägliche Runde – nein
- Link: wie A4 | Kosten: −50 %
- Was es kann: Batch-Requests sind Einzelschüsse und erlauben keine Werkzeugschleife innerhalb des Batches (Skill `cost-optimization.md` §2.5).
- Nutzen für die Arena: Die Fondsrunde braucht Tool-Use mit Orderbuch und Order. Eine Runde ließe sich nur „flach“ machen (alle Daten vorher holen, ein einziger Aufruf liefert die Orders als strukturierte Ausgabe). Das ändert das Denken der Agenten und die Vergleichbarkeit mit der Liga, außerdem kann ein Ergebnis bis zu 24 h dauern. Für ereignisgesteuerte Runden ungeeignet. Höchstens für eine „Nachtanalyse“ ohne Orders (z. B. Kalibrierungsbericht) sinnvoll.
- Aufwand: groß
- Bewertung: 1/5
- Status: geprüft (Doku)

#### A6 Websuche: `web_search_20260209` (dynamische Filterung) statt `web_search_20250305`
- Link: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool | Kosten: 10 $/1000 Suchen plus Tokens der Ergebnisse. Die Code-Ausführung ist laut Preisseite **kostenlos**, wenn sie zusammen mit `web_search_20260209` läuft.
- Was es kann: Claude filtert die Suchergebnisse per Code, bevor sie in den Kontext kommen. Laut Skill steht die Variante auf Sonnet 5.5 zur Verfügung. Es gibt laut Doku auch schon `web_search_20260318`.
- Nutzen für die Arena: Im Log erzeugt jede Suche 7–17 k Token Cache-Write (Ergebnisse), die in allen folgenden Schritten erneut gelesen werden. Websuche macht damit ≈ 35 % der Sonnet-Kosten aus (siehe Kostenanalyse). In DECISIONS.md wurde die neue Variante wegen „Code-Ausführung“ verworfen, doch die Code-Ausführung kostet nichts extra. Ob die Ergebnisse wirklich kleiner werden, ist für die Arena **ungeprüft** und braucht einen A/B-Lauf. Hinweis: Die dynamische Filterung ist nicht ZDR-fähig (hier unwichtig).
- Aufwand: eine Zeile, danach messen
- Bewertung: 4/5
- Status: geprüft (Doku), Effekt ungeprüft

#### A7 Eigene Billig-/Gratis-Suche als Arena-Werkzeug (auch für die Liga)
- Links: DeepSeek Search/Fetch API https://api-docs.deepseek.com/quick_start/pricing · Tavily https://tavily.com/pricing · Brave https://brave.com/search/api | Kosten: DeepSeek **0,75 $ je 1000** erfolgreiche Suchen bzw. Fetches (geprüft, offizielle Preisseite). Tavily 1000 Credits/Monat gratis (nur gelesen). Brave seit 2026 angeblich 5 $ Monatsguthaben statt Gratiskontingent (nur gelesen, widersprüchlich).
- Was es kann: Websuche als normales Funktionswerkzeug. Die Ausgabe kürzt der eigene Code (z. B. Titel + 300 Zeichen je Treffer).
- Nutzen für die Arena: (1) Fairness: Heute hat nur Claude Websuche, die Liga-Modelle nicht. Ein gemeinsames Werkzeug `websuche` gäbe allen Modellen dieselben Daten, wie es der Anspruch „identische Werkzeuge“ aus DECISIONS.md verlangt. (2) Kosten: Die Gebühr sinkt von 10 $ auf 0,75 $/1000, und die Ergebnislänge steuert man selbst. Nachteil: Claudes zitierfähige Server-Suche fällt weg, und der Vergleich mit den bisherigen Claude-Runden bricht. Vorschlag: nach dem 14.11. bzw. für die Liga sofort.
- Aufwand: mittel (Adapter + Werkzeug + Gebührenbuchung)
- Bewertung: 4/5
- Status: DeepSeek-Preis geprüft, Tavily/Brave nur gelesen

#### A8 effort-Parameter je Rolle
- Link: https://platform.claude.com/docs/en/build-with-claude/effort | Kosten: –
- Was es kann: `output_config.effort` mit low…max. Standard ist auf Sonnet 5.5 `high` (Stufen neu kalibriert), auf Haiku 5.5 und Opus 5.5 `medium`. Thinking lässt sich auf Opus 5.5 und Sonnet 5.5 nicht mit `disabled` ausschalten (400). Eine Effort-Änderung mitten im Verlauf invalidiert den Messages-Cache. Die Beta „per-message effort“ (`mid-conversation-output-config-2026-07-01`) umgeht das.
- Nutzen für die Arena: Die Arena nutzt high (Runde), low (Triage) und high (Review), das ist passend. Der Skill rät bei agentischem Tool-Use auf Sonnet 5.5, bei `medium` zu starten. Der eigene Test mit medium zeigte aber zu wenig Recherche, high bleibt also richtig. Der Effort sollte pro Route fest bleiben (Cache).
- Aufwand: –
- Bewertung: 2/5 (schon gut gelöst)
- Status: geprüft (Skill/Doku)

#### A9 Strukturierte Ausgaben für Triage und Review
- Link: https://platform.claude.com/docs/en/build-with-claude/structured-outputs | Kosten: –
- Was es kann: `output_config: {format: {...}}` (JSON-Schema) oder `strict: true` an Werkzeugen. Wichtig: Erzwungenes `tool_choice` (`any`/`tool`) gibt auf Sonnet 5.5 und Opus 5.5 einen 400-Fehler zurück.
- Nutzen für die Arena: `triage()` sucht heute per `text.index("{")`, und `review.py` holt den Regel-Block per Regex. Beides ist zerbrechlich (siehe A4). Ein Schema `{aufwecken: bool, grund: str}` liefert garantiert gültiges JSON. Ob `max_tokens: 300` mit Denken auf Haiku reicht, sollte man prüfen.
- Aufwand: klein
- Bewertung: 4/5
- Status: geprüft (Skill), ungetestet in der Arena

#### A10 Token-Zählung (`/v1/messages/count_tokens`)
- Link: https://platform.claude.com/docs/en/build-with-claude/token-counting | Kosten: **kostenlos**, eigenes RPM-Limit
- Was es kann: Exakte Eingabe-Tokens vor dem Aufruf. Fehler bei Requests mit Server-Werkzeugen außer dem Advisor (also auch mit `web_search`).
- Nutzen für die Arena: `schaetze_naechsten_aufruf` rechnet mit „Zeichen/3 + 2000“, dazu fehlt die Länge der Werkzeugschemas. Für den harten Budget-Stopp reicht die Schätzung, sie ist konservativ. Genauer ginge es mit count_tokens ohne das Websuche-Werkzeug plus Puffer. Das kostet allerdings einen zusätzlichen Roundtrip pro Schritt.
- Aufwand: klein
- Bewertung: 2/5
- Status: geprüft (Doku)

#### A11 Kleinere Modelle als Zusammenfasser (Haiku 5.5)
- Link: Preise s. A3 | Kosten: Haiku 5.5 0,10/0,50 $ (20× billiger als Sonnet)
- Was es kann: Lange Werkzeugausgaben (Nachrichten, `markt_details`, Suchtreffer) vorher von Haiku auf das Wesentliche kürzen lassen. Alternativ ein Recherche-Unteragent auf Haiku.
- Nutzen für die Arena: Spart Sonnet-Kontext, aber Modellwechsel bedeuten getrennte Caches, und Zusammenfassungen können für die Entscheidung wichtige Details verlieren. Erst lohnend, wenn A6/A7 nicht reichen.
- Aufwand: mittel
- Bewertung: 2/5
- Status: geprüft (Preise), Nutzen ungeprüft

#### A12 Schnappschuss-Text verkleinern / Daten auf Abruf
- Link: Code `arena/snapshot.py::text` | Kosten: –
- Was es kann: Der Schnappschuss (laut Docstring ~3–5 k Token, 30 Wettmärkte + bald schließende + Optionen) steckt in jedem Rundenprompt. Verkleinern ließe er sich, indem man die Wettmärkte auf ~15 begrenzt und den Rest über `markt_suche` holen lässt, Zahlen rundet und Spalten wie `24h-Umsatz` als k/M schreibt.
- Nutzen für die Arena: Mit A1 wird der Schnappschuss ohnehin gecacht (Lesezugriff ≈ 0,1 $/MTok). Der Spareffekt ist daher klein, er hilft aber vor allem den Liga- und Gratismodellen (Groq-TPM 8 k! Cerebras 30 k TPM).
- Aufwand: klein
- Bewertung: 3/5 (wegen Liga)
- Status: ungeprüft (Tokenzahl nicht gemessen)

#### A13 Kontext-Editing (`clear_tool_uses_20250919`) / Kompaktierung (`compact_20260112`)
- Link: https://platform.claude.com/docs/en/build-with-claude/context-editing | Kosten: –
- Was es kann: Löscht alte Werkzeugergebnisse bzw. fasst den Verlauf serverseitig zusammen (Beta).
- Nutzen für die Arena: Laut Skill „ein Kontextfenster-Werkzeug, kein Sparhebel“: Jedes Löschen schreibt den Cache neu, und in der Doku-Messung kostete es mehr, als es sparte. Arena-Runden bleiben unter 50 k Token bei 1 M Kontext. → nicht einsetzen.
- Aufwand: –
- Bewertung: 1/5
- Status: geprüft (Skill)

#### A14 Memory-Tool (`memory_20250818`)
- Link: https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool | Kosten: keine Zusatzkosten, Speicher liegt clientseitig
- Was es kann: Claude liest und schreibt Dateien unter `/memories`, die eigene Anwendung führt die Operationen aus (Pfadprüfung nötig). Die API fügt automatisch eine Systemanweisung hinzu („ALWAYS VIEW YOUR MEMORY DIRECTORY…“).
- Nutzen für die Arena: Das Notizbuch leistet das schon und ist modellunabhängig (gleich für die Liga). Das Memory-Tool würde Claude einen Sonderweg geben und kostet zusätzliche Schritte („view“ zu Beginn). → nicht nötig.
- Aufwand: mittel
- Bewertung: 1/5
- Status: geprüft (Doku)

#### A15 LLMLingua-2 (Prompt-Kompression)
- Link: https://github.com/microsoft/LLMLingua | Lizenz: MIT | ★ 6 784, aktiv (updated 2026-10-30)
- Was es kann: Kürzt Prompts per kleinem Klassifikator (bis „20×“ laut README) um unwichtige Tokens.
- Nutzen für die Arena: Der Schnappschuss besteht fast nur aus Zahlen, IDs und Preisen. Token-Dropping kann genau die entscheidenden Ziffern treffen, und komprimierter, wechselnder Text verträgt sich schlecht mit Caching. Zusätzlich braucht es torch und das Modell im Workflow (Minuten Startzeit). Höchstens für lange Nachrichtentexte denkbar.
- Aufwand: mittel
- Bewertung: 1/5
- Status: nur gelesen

#### A16 Cache-Diagnose (Beta)
- Link: https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics.md | Kosten: –
- Was es kann: `diagnostics: {previous_message_id: …}` zeigt, an welcher Stelle zwei Requests auseinanderlaufen.
- Nutzen für die Arena: Zum Überprüfen von A1, damit man sieht, ob der Präfix wirklich über die Fonds geteilt wird.
- Aufwand: klein
- Bewertung: 2/5
- Status: geprüft (Skill)

---

### Kategorie: B – Gratis-/Billig-Modelle (Liga und Zeit nach dem 14.11.)

#### B1 OpenRouter `:free`
- Link: https://openrouter.ai/docs/api-reference/limits | Kosten: gratis. 20 RPM. **50 Anfragen/Tag** bei < 10 $ gekauftem Guthaben, **1000/Tag** ab 10 $ (einmalig, all time)
- Was es kann: **Test 30.10. (curl /api/v1/models): 456 Modelle, davon 16 `:free`, 15 mit `tools`.** Nach Kontext sortiert: thinkingmachines/inkling-small, inkling, nvidia/nemotron-3.5-super-vl, nemotron-3.5-lightning, nemotron-3-ultra-550b-a55b, dots-3-note-preview, recursive/flint-v1.0, xingchen xing4.0-29b-a4b, poolside laguna-s/xs-2.1, google/gemma-4-26b-a4b-it, gemma-4-31b-it, cohere/north-mini-code, nemotron-3-nano-omni-30b, liquid/lfm-2.5-2.6b.
- Nutzen für die Arena: `openrouter_gratis()` wählt nach **Kontextlänge** und nimmt je Hersteller eines. Das bevorzugt kleine Modelle (inkling-small vor inkling) und Code-Modelle. Besser wäre eine kleine feste Bevorzugungsliste (z. B. nemotron-3-ultra-550b, gemma-4-31b, inkling) mit Kontext nur als Nebenkriterium. **10 $ einmalig aufladen** hebt das Limit auf 1000/Tag, das ist für 3 Liga-Fonds mit je ≤ 8 Schritten × ≤ 12 Läufen nötig (≈ 288 Anfragen/Tag > 50). Datenschutz: Gratis-Anbieter können Prompts loggen bzw. trainieren (Einstellung im Konto, ungeprüft).
- Aufwand: klein
- Bewertung: 4/5
- Status: getestet (Liste), Limits geprüft (Doku)

#### B2 Gemini API Free Tier
- Link: https://ai.google.dev/gemini-api/docs/rate-limits · Bedingungen https://ai.google.dev/gemini-api/terms | Kosten: gratis (Free Tier), Limits je Projekt und nur in AI Studio sichtbar. Sekundärquellen nennen für Flash ~15 RPM/~1500 RPD (nur gelesen)
- Was es kann: OpenAI-kompatibler Endpunkt mit Tool-Calling (in der Arena schon genutzt, `gemini-flash-latest`).
- Nutzen für die Arena: **Datennutzung geprüft:** In den Unpaid Services nutzt Google Ein- und Ausgaben zur Produktverbesserung, menschliche Prüfer können sie lesen. Für Entwickler im EWR, UK und CH gelten laut Bedingungen jedoch die Paid-Datenregeln auch für das Gratiskontingent („apply to all Services, including … unpaid quota“). Zudem: „You may use only Paid Services when making API Clients available to users in the EEA …“. Die Arena stellt keinen API-Client für Nutzer bereit, sie ruft nur aus Actions auf. Das ist vermutlich unkritisch, aber **juristisch ungeprüft**. Die Arena verarbeitet ohnehin nur öffentliche Marktdaten. Gemini 1.5 Flash und 2.0 Flash-Lite sind abgeschaltet (nur gelesen). Der Alias `-latest` ist robust.
- Aufwand: –
- Bewertung: 4/5
- Status: Bedingungen geprüft, Limits nur gelesen

#### B3 GitHub Models (gratis mit GITHUB_TOKEN) – **eingestellt**
- Link: https://docs.github.com/en/github-models/use-github-models/prototyping-with-ai-models | Kosten: –
- Was es kann: Nichts mehr. Laut GitHub-Doku: „As of July 30, 2026, GitHub Models has been fully retired … inference API … no longer available“. Der Katalog-Endpunkt `models.github.ai/catalog/models` antwortete im Test mit `200 "OK"` (4 Byte) statt JSON.
- Nutzen für die Arena: keiner. Nicht einplanen.
- Aufwand: –
- Bewertung: 0/5
- Status: getestet + geprüft

#### B4 Groq (nur Triage)
- Link: https://console.groq.com/docs/rate-limits | Kosten: gratis (Free/Developer-Basislimits)
- Was es kann: Laut Doku-Tabelle (Basislimits): openai/gpt-oss-120b, gpt-oss-20b, qwen/qwen3.8-27b je 30 RPM, 1 000 RPD, **8 000 TPM**, 200 000 TPD.
- Nutzen für die Arena: **`llama-3.3-70b-versatile` (in `loop.triage_groq`) steht nicht mehr in der Tabelle** und ist womöglich abgeschaltet. Der automatische 404-Ersatz (`_modell_suchen`) würde per Präfix ein „llama…“-Modell suchen. Empfehlung: auf `openai/gpt-oss-20b` (Triage) umstellen. 8 k TPM schließen volle Runden aus (Entscheidung wie gehabt).
- Aufwand: sehr klein
- Bewertung: 3/5
- Status: geprüft (Doku), Modellstatus ungeprüft (Liste braucht Schlüssel)

#### B5 Cerebras
- Link: https://inference-docs.cerebras.ai/support/rate-limits | Kosten: **nur noch Free Trial: 5 $ Guthaben, verfällt nach 30 Tagen, kein dauerhaftes Gratis-Tier** (laut Doku)
- Was es kann: gpt-oss-120b und qwen-3.8-27b, 5 RPM, 30 k TPM ungecacht, 1 M Token/Tag.
- Nutzen für die Arena: Der Liga-Fonds „Cerebras gpt-oss“ (Schlüssel fehlt noch) wäre nach 30 Tagen kostenpflichtig. 5 RPM bremst die Schleife (8 Schritte ≥ 1,6 min). Entweder bewusst als „30-Tage-Gast“ oder gpt-oss-120b über OpenRouter/HF/SambaNova laufen lassen.
- Aufwand: –
- Bewertung: 2/5
- Status: geprüft (Doku)

#### B6 Mistral La Plateforme (Experiment/Free)
- Link: https://docs.mistral.ai (Tier-Seite 404). Admin-Konsole „Limits“ | Kosten: gratis
- Was es kann: Sekundärquelle (cheahjs/free-llm-api-resources): 1 RPS, 500 k TPM, 1 Mrd. Token/Monat, **Opt-in in Datentraining nötig**. Offiziell sind keine Zahlen veröffentlicht.
- Nutzen für die Arena: `mistral-small-latest` passt (Tool-Use). 1 RPS ist für die Schleife unkritisch. Das Training-Opt-in ist bei öffentlichen Marktdaten vertretbar.
- Aufwand: Schlüssel setzen (fehlt laut STATUS)
- Bewertung: 3/5
- Status: nur gelesen

#### B7 DeepSeek (billig, empfohlener Nachfolger nach dem 14.11.)
- Link: https://api-docs.deepseek.com/quick_start/pricing | Kosten: `deepseek-flash` (V4.1-Flash-1017, 1 M Kontext, Tool-Calls ✓): Eingabe (Cache-Treffer) 0,003/0,006 $, Cache-Fehlschuss 0,15/0,30 $, Ausgabe 0,60/1,20 $ je MTok (Off-Peak/Peak, Off-Peak = halber Preis). `deepseek-v4-pro`: 0,66/1,32 $ ein, 1,98/3,96 $ aus. Automatisches Caching.
- Was es kann: OpenAI- **und Anthropic-kompatibler** Endpunkt, Thinking an (Standard) oder aus, Search/Fetch-API (s. A7).
- Nutzen für die Arena: (1) **`config.json` nutzt `deepseek-chat`**. Die Preisseite nennt nur noch `deepseek-flash` und `deepseek-v4-pro`, als Legacy-Namen nur `deepseek-v4-flash*`. Ob `deepseek-chat` noch angenommen wird, ist **ungeprüft** (ohne Schlüssel nicht testbar) → auf `deepseek-flash` umstellen. (2) Eine Arena-Runde mit ~300 k Eingabe (überwiegend Cache) + 5 k Ausgabe kostet auf Flash ungefähr **0,01 $**. Nach dem 14.11. könnten die drei Claude-Fonds also für wenige Euro im Monat auf DeepSeek weiterlaufen, wenn der „beste Liga-Fonds“ nicht taugt. (3) Mögliche Falle (ungeprüft): Im Thinking-Modus mit Tool-Calls verlangt DeepSeek eventuell, dass `reasoning_content` zurückgegeben wird. `OpenAISitzung` übernimmt nur role/content/tool_calls.
- Aufwand: klein
- Bewertung: 5/5
- Status: Preise geprüft (offizielle Seite), Modellname ungeprüft

#### B8 Kimi / Moonshot
- Link: https://platform.moonshot.ai (Preise nur aus Sekundärquellen) | Kosten: Kimi K3 ≈ 3/15 $ je MTok (nur gelesen). Für `kimi-latest` keine offizielle Aussage gefunden
- Was es kann: Starkes Agentikmodell. K3 ist auch bei HF-Providern und Chutes gelistet (getestet).
- Nutzen für die Arena: `kimi-latest` ist ein Alias mit unklarer Zukunft. Prüfen, ob die Läufe 404 liefern (der Auto-Ersatz greift dann). Im Vergleich zu DeepSeek teuer.
- Aufwand: –
- Bewertung: 2/5
- Status: nur gelesen

#### B9 Hugging Face Inference Providers
- Link: https://huggingface.co/docs/inference-providers/pricing | Kosten: **Free-Nutzer: keine Monatsguthaben mehr**, PRO 2 $/Monat inklusive. Pay-as-you-go ohne Aufschlag
- Was es kann: **Test: `router.huggingface.co/v1/models` (ohne Schlüssel) listet 137 Modelle, 114 mit Tool-fähigem Anbieter, 0 mit `is_free`.** Günstigste Tool-Modelle: Qwen3-4B (nscale 0,01/0,03 $), Llama-3.1-8B (0,02/0,05), gpt-oss-20b (deepinfra 0,03/0,14), gpt-oss-120b (deepinfra 0,037/0,17), DeepSeek-V4-Flash-0731 (0,06/0,18). Daneben u. a. Kimi-K3, GLM-5.3, Qwen3.8-27B, MiniMax-M3.
- Nutzen für die Arena: Ein Schlüssel öffnet viele offene Modelle über einen OpenAI-kompatiblen Endpunkt. Für eine „Open-Weights-Liga“ sehr praktisch, die Kosten liegen im Cent-Bereich.
- Aufwand: klein (neuer Anbieter in config)
- Bewertung: 4/5
- Status: getestet (Liste), Preise geprüft (Doku)

#### B10 NVIDIA NIM (build.nvidia.com)
- Link: https://build.nvidia.com | Kosten: gratis für Entwickler. ~40 RPM (Sekundärquellen, teils 30). Nutzung angeblich nur für Entwicklung, nicht Produktion (Forum, ungeprüft)
- Was es kann: **Test: `integrate.api.nvidia.com/v1/models` öffentlich, 85 Modelle**, u. a. deepseek-v4.1-flash, kimi-k2.6, mistral-large-4, nemotron-3-ultra-550b, gemma-4-31b, minimax-m3.1-flash.
- Nutzen für die Arena: Gratis-Zugang zu großen Modellen. Ein öffentliches Forschungsexperiment ist kaum „Produktion“, die AGB sollten aber geprüft werden.
- Aufwand: klein
- Bewertung: 3/5
- Status: getestet (Liste), Limits/AGB nur gelesen

#### B11 Cloudflare Workers AI
- Link: https://developers.cloudflare.com/workers-ai/platform/pricing/ | Kosten: **10 000 Neurons/Tag gratis**, danach 0,011 $/1000 Neurons. Preise: gpt-oss-120b 0,35/0,75 $, llama-4-scout 0,27/0,85, qwen3-30b-a3b-fp8 0,051/0,335, Kimi K2.6/K2.7 nur mit Paid
- Was es kann: OpenAI-kompatibler Endpunkt, Function-Calling je Modell (nicht auf der Preisseite vermerkt).
- Nutzen für die Arena: 10 k Neurons/Tag reichen grob für wenige zehntausend Token (Umrechnung je Modell, ungeprüft). Eher Reserve als Haupt-Liga.
- Aufwand: klein (Account-ID + Token)
- Bewertung: 2/5
- Status: geprüft (Doku)

#### B12 SambaNova Cloud
- Link: https://cloud.sambanova.ai | Kosten: Gratis-Tier ungeprüft
- Was es kann: **Test: `api.sambanova.ai/v1/models` öffentlich, 6 Modelle:** DeepSeek-V3.1, V3.2, Llama-3.3-70B, MiniMax-M3.1-Flash, gemma-4-31B-it, gpt-oss-120b.
- Nutzen für die Arena: Ersatzquelle für gpt-oss-120b (falls Cerebras ausläuft).
- Aufwand: klein
- Bewertung: 2/5
- Status: getestet (Liste), Konditionen ungeprüft

#### B13 Chutes
- Link: https://chutes.ai | Kosten: kostenpflichtig, aber sehr billig (Test: Qwen3.8-27B-TEE 0,039 $ ein / 1,25 $ aus, Cache-Lesen 0,0039 $). Gratis-Tier: nicht gefunden
- Was es kann: **Test: `llm.chutes.ai/v1/models` öffentlich, 17 Modelle** (DeepSeek V3.2/V4-Pro/V4.1-Flash, GLM-5.1–5.3, Kimi-K2.6/K3, Qwen3.5-397B, Qwen3.8-Max, …), teils in TEEs (vertrauliche Ausführung).
- Nutzen für die Arena: Günstige Quelle für Kimi-K3 und GLM-5.3.
- Aufwand: klein
- Bewertung: 2/5
- Status: getestet (Liste)

#### B14 Together AI
- Link: https://api.together.xyz | Kosten: kein Gratis-Tier bekannt (Modellliste verlangt Schlüssel, 401)
- Bewertung: 1/5 · Status: getestet (401), Rest ungeprüft

#### B15 Zhipu / Z.ai GLM-Flash (gratis?)
- Link: https://open.bigmodel.cn / https://z.ai | Kosten: laut Sekundärquellen GLM-4.7-Flash/GLM-4.5-Flash gratis, 128 k Kontext, Function-Calling
- Was es kann: OpenAI-kompatibel (`open.bigmodel.cn/api/paas/v4`, Modelllisten-Test → 401).
- Nutzen für die Arena: Ein potenziell dauerhaft gratis nutzbares Tool-Use-Modell. Der China-Endpunkt hat eigene Datenschutzfragen. Die neueren GLM-5.x sind über HF/Chutes erreichbar.
- Aufwand: klein
- Bewertung: 3/5
- Status: nur gelesen

#### B16 Qwen / Alibaba Model Studio (DashScope intl.)
- Link: https://www.alibabacloud.com/help/en/model-studio/new-free-quota | Kosten: Neukunden-Gratiskontingent **je Modell**, nur Region Singapur, befristet (früher 90 Tage). Die Höhe (oft „1 M Token“) ist nur aus Sekundärquellen bekannt
- Nutzen für die Arena: Für einen zeitlich begrenzten Qwen-Fonds. Achtung: Nach Ablauf wird ohne „stop on exhaustion“ abgerechnet.
- Bewertung: 2/5 · Status: nur gelesen

#### B17 Lokal auf Oracle ARM (4 OCPU A1, 24 GB) mit llama.cpp / Ollama
- Links: https://github.com/ggml-org/llama.cpp (MIT, ★ 132 819, aktiv) · https://github.com/ollama/ollama (MIT, ★ 185 312, aktiv) | Kosten: 0 € (Always-Free-Instanz)
- Was es kann: OpenAI-kompatibler Server (`llama-server`, Ollama) mit Tool-Calling (Jinja-Templates).
- Nutzen für die Arena: Einzige Messung gefunden: Qwen2.5-3B Q4_K_M auf genau dieser Form mit **≈ 10,6 Token/s** Generierung (13,4 mit Ampere-optimiertem Build). Daraus geschätzt (**ungeprüft**): Qwen3-8B Q4 ≈ 4–5 tok/s, 14B Q4 ≈ 2–3 tok/s, gpt-oss-20b (MoE, ~3,6 B aktiv, ~13 GB) ≈ 6–10 tok/s. Das eigentliche Problem ist die **Prompt-Verarbeitung** auf 4 CPU-Kernen: ein 10 k-Token-Rundenprompt dauert grob mehrere Minuten pro Schritt (Prefix-Cache von llama.cpp hilft bei Folgeschritten). Realistisch ist das nur für Triage/Zusammenfassen oder einen „langsamen“ lokalen Liga-Fonds mit verkleinertem Schnappschuss (A12), gpt-oss-20b ist der beste Kandidat.
- Aufwand: mittel (Server, Tunnel/Port, Schlüssel)
- Bewertung: 3/5
- Status: nur gelesen (ein Benchmark), Rest Schätzung

#### B18 Leaderboards zur Auswahl: BFCL v4 und τ²-bench
- Links: https://gorilla.cs.berkeley.edu/leaderboard.html (Repo ShishirPatil/gorilla, Apache-2.0, ★ 13 063) · https://github.com/sierra-research/tau2-bench (MIT, ★ 2 360, aktiv)
- Was es kann: BFCL misst Funktionsaufrufe (inkl. Multi-Turn/Agentik), τ²-bench Werkzeug-Agent-Nutzer-Interaktion.
- Nutzen für die Arena: Laut Aggregatoren (widersprüchlich, nur gelesen) liegen bei BFCL v4 unter den offenen Modellen Qwen3.5-397B-A17B (~73 %), Qwen3.5-122B und GLM-5 vorn. Eine bessere Grundlage für die OpenRouter/HF-Auswahl als die Kontextlänge.
- Aufwand: –
- Bewertung: 3/5
- Status: nur gelesen

#### B19 OpenAI gpt-5-mini (bestehender Liga-Fonds)
- Laut STATUS „no credits“. Ohne Guthaben gibt es kein Gratis-Tier → bis zur Aufladung „pausiert“ zeigen oder aus der Liga nehmen. Bewertung: 1/5 · Status: aus STATUS.md

---

### Kategorie: C – Dashboards und Visualisierung (statische Seite)

Ausgangslage: `docs/index.html` (24,8 kB) zeichnet die Verlaufskurve selbst (`<canvas id="chart">`, eigene `chart()`/`niceStep()`), ohne Abhängigkeiten. `data.json` hat 40 kB (Fonds 37 kB). Die Equity-Verläufe sind auf 400 Punkte heruntergerechnet. Bibliotheken sollten **ins Repo kopiert** werden (z. B. `docs/vendor/`), damit die Seite „ohne externe Abhängigkeiten“ bleibt. Größen wurden **gemessen** (jsDelivr, minifiziert / gzip -9).

#### C1 uPlot
- Link: https://github.com/leeoniya/uPlot | Lizenz: MIT | ★ 10 601, aktiv · v1.6.32
- Was es kann: Sehr schnelle Zeitreihen (Linien, Flächen, Bänder, OHLC), Canvas, Zoom/Cursor-Sync.
- Nutzen für die Arena: Ersetzt die Eigenbau-Kurve. Mehrere Fonds, synchronisierte Cursor, **Konfidenzband** (Bands-Plugin) für Equity und Prognosen (TimesFM-Quantile). Mit **51 kB min / 22 kB gzip** am kleinsten.
- Aufwand: klein
- Bewertung: 5/5
- Status: getestet (Größe), Funktionen nur gelesen

#### C2 TradingView Lightweight Charts
- Link: https://github.com/tradingview/lightweight-charts | Lizenz: Apache-2.0 | ★ 17 726, aktiv · v5.2.1
- Was es kann: Finanz-Charts (Kerzen, Linien, Marker für Orders, Preisskala), 198 kB min / 62 kB gzip.
- Nutzen für die Arena: Ideal für **Instrument-Ansichten**: BTC-Kerzen mit Kauf-/Verkauf-Markern, Stop/Take-Profit-Linien. **Attribution:** Die NOTICE-Datei enthält „Copyright (c) 2025 TradingView, Inc.“ und den Produktnamen „TradingView Lightweight Charts™“. Im Code ist `attributionLogo: true` Standard (getestet: `attributionLogo:!0` im Bundle). Das Logo also anlassen oder einen sichtbaren Hinweis mit Link auf tradingview.com setzen.
- Aufwand: klein–mittel
- Bewertung: 4/5
- Status: getestet (Größe, Default), Lizenzpflichten geprüft (NOTICE)

#### C3 Apache ECharts
- Link: https://github.com/apache/echarts | Lizenz: Apache-2.0 | ★ 67 636, aktiv · v6.1.0
- Was es kann: Alles (Heatmaps, Sankey, Kalender, Zeitstrahl), aber **1,12 MB min / 368 kB gzip** (Teilbuild möglich).
- Nutzen für die Arena: Nur sinnvoll, wenn viele Diagrammtypen gebraucht werden (z. B. Kalender-Heatmap der Entscheidungen). Für das Kerndashboard zu schwer.
- Bewertung: 3/5 · Status: getestet (Größe)

#### C4 Observable Plot
- Link: https://github.com/observablehq/plot | Lizenz: ISC | ★ 5 417, aktiv · v0.6.17
- Was es kann: Grammar-of-Graphics, sehr kompakt für statistische Grafiken (Kalibrierung, Streuung, Facetten). UMD-Bundle 209 kB, **braucht zusätzlich d3** (280 kB) → zusammen ~160 kB gzip.
- Nutzen für die Arena: Bestes Werkzeug für das **Kalibrierungsdiagramm** (vorhergesagte vs. eingetretene Häufigkeit, Brier je Fonds) und Bandbreiten.
- Bewertung: 3/5 · Status: getestet (Größe, d3-Abhängigkeit im Bundle gesehen)

#### C5 Chart.js
- Link: https://github.com/chartjs/Chart.js | Lizenz: MIT | ★ 67 766, aktiv · v4.6.1, 210 kB min / 71 kB gzip
- Nutzen für die Arena: Solide Allzweck-Lösung (Balken für Kosten je Fonds, Doughnut für Allokation). Gegenüber uPlot keine Vorteile bei Zeitreihen.
- Bewertung: 3/5 · Status: getestet (Größe)

#### C6 Plotly.js
- Link: https://github.com/plotly/plotly.js | Lizenz: MIT | ★ 18 372 · v4.2.0
- Was es kann: Sehr mächtig, aber **4,8 MB min / 1,48 MB gzip**.
- Nutzen für die Arena: zu schwer für die Seite und das Widget.
- Bewertung: 1/5 · Status: getestet (Größe)

#### C7 D3
- Link: https://github.com/d3/d3 | Lizenz: ISC | ★ 113 826 · v7.9.0, 280 kB min / 92 kB gzip
- Nutzen für die Arena: Für eine individuelle **Entscheidungs-Zeitleiste** (Swimlanes je Fonds, Punkte = Orders, Farbe = Ergebnis) oder die **Debatten-Ansicht**. Höchste Freiheit, höchster Aufwand. Einzelmodule (d3-scale, d3-shape) sind kleiner.
- Bewertung: 3/5 · Status: getestet (Größe)

#### C8 Frappe Charts
- Link: https://github.com/frappe/charts | Lizenz: MIT | ★ 15 091 · v1.6.2, 69 kB min / 18 kB gzip
- Nutzen für die Arena: Kleine SVG-Charts mit Heatmap (GitHub-Stil), geeignet für die Aktivität „Entscheidungen pro Tag“. Weniger aktiv gepflegt (letzte Version älter, ungeprüft).
- Bewertung: 2/5 · Status: getestet (Größe)

#### C9 Vega-Lite
- Link: https://github.com/vega/vega-lite | Lizenz: BSD-3-Clause · v6.5.0 (npm)
- Nutzen für die Arena: Deklarative Spezifikationen als JSON, die sich aus Python (`arena/site.py`) mit erzeugen lassen. Laufzeit (vega + vega-lite + vega-embed) jedoch mehrere 100 kB (ungeprüft).
- Bewertung: 2/5 · Status: nur gelesen (npm-Metadaten)

#### C10 Datenwachstum: JSON → Parquet (hyparquet) / DuckDB-WASM
- Links: https://github.com/hyparam/hyparquet (MIT, ★ 967, aktiv, v1.32.0) · https://github.com/duckdb/duckdb-wasm (MIT, ★ 2 157, v1.33.1-dev; npm-Paket 149 MB entpackt)
- Was es kann: hyparquet liest Parquet im Browser ohne Abhängigkeiten. DuckDB-WASM bietet SQL im Browser (WASM-Dateien mehrere MB).
- Nutzen für die Arena: Heute **nicht nötig**: `data.json` 40 kB, `data/` 384 kB, `.git` 516 kB. Wachstum laut DECISIONS ~100–200 kB/Tag, also ~50 MB/Jahr. GitHub-Pages-Grenzen (geprüft): Website ≤ 1 GB, Repo empfohlen ≤ 1 GB, 100 GB/Monat Bandbreite (soft), 10 Builds/h (soft), Deploy-Timeout 10 min. Vorschlag: `data.json` schlank halten (wie heute), Detail-Historie je Fonds/Monat in getrennte Dateien (`docs/hist/<fonds>-2026-11.json`), die erst beim Aufklappen nachgeladen werden. Parquet + hyparquet erst ab einigen MB. Die 10 Builds/h betreffen Actions-Deployments bei 4 Wächterläufen/h nicht kritisch (Soft-Limit, ungeprüft ob es für den Workflow-Pfad gilt).
- Aufwand: klein (Aufteilung) bzw. mittel (Parquet)
- Bewertung: 3/5
- Status: Pages-Limits geprüft (Doku), Größen getestet

#### C11 Inhaltsideen für das Dashboard
- **Kalibrierungsdiagramm** je Fonds: Wahrscheinlichkeiten aus dem Werkzeug `wahrscheinlichkeit` in 10 Klassen, beobachtete Trefferquote mit Wilson-Intervall, Diagonale als Ideal, Brier-Score und dessen Zerlegung (Reliabilität/Auflösung). (Plot oder uPlot)
- **Equity mit Konfidenzband**: Bootstrap-Band der Tagesrenditen bzw. Band gegen den Zufallsaffen-Benchmark (viele Zufallspfade → 5–95 %-Band). So wird Rauschen sichtbar, wie es STATUS ausdrücklich verlangt.
- **Entscheidungs-Zeitleiste**: Swimlanes je Fonds, Marker je Order (Größe = Nominal, Farbe = realisierter PnL), Klick öffnet die Begründung.
- **Debatten-Ansicht**: dasselbe Instrument, Thesen/Wahrscheinlichkeiten aller Fonds nebeneinander. Macht das Klumpenrisiko sichtbar (alle setzten auf die Iran-Waffenruhe).
- **Kosten pro Entscheidung**: € je Runde, je Order, je Brier-Punkt aus `nutzung.jsonl`, Aufteilung Ausgabe / Cache-Write / Cache-Read / Websuche.
- **Modellwechsel-Marker** am 14.11. in allen Kurven.
- Bewertung: 4/5 · Status: Idee (ungeprüft)

#### C12 Widget für Windows
- Optionen (alle lesen `status.json`): (a) **Mini-Seite `docs/widget.html`** (≤ 10 kB) als „App“ über Edge/Chrome installiert (PWA, immer im Vordergrund mit PowerToys „Always on Top“) – null Installation, MIT-frei. (b) **Rainmeter**-Skin (Rainmeter GPL-2.0, Skin selbst frei lizenzierbar; WebParser liest JSON per Regex). (c) Python-Tray-Icon mit `pystray` (LGPL-3.0) + Tooltip/Benachrichtigung. (d) Windows-11-Widgets-Board erfordert eine gepackte App mit Adaptive Cards → zu aufwendig.
- Nutzen für die Arena: (a) ist am einfachsten und plattformunabhängig. `status.json` liegt mit 4,6 kB in passender Größe vor. Hinweis: `raw.githubusercontent.com` cached ~5 min.
- Aufwand: klein (a) / mittel (b, c)
- Bewertung: 4/5 für (a)
- Status: Lizenzen von Rainmeter/pystray aus dem Gedächtnis → ungeprüft

---

#### Kostenanalyse der Arena (aus `data/budget_log.jsonl`, 37 Buchungen, 30.10.)

Gebucht: **1,108 $** (inkl. +15 % Aufschlag) = 0,99 €. Nachgerechnet ohne Aufschlag mit Config-Faktoren: 0,963 $. Mit **echten Preisen** (Cache-Lesen 0,05× auf Sonnet/Opus 5.5): **≈ 0,90 $**. Das Budget zählt also ~23 % zu hoch (A3).

| Posten | Tokens | Kosten (echt) | Anteil |
|---|---|---|---|
| Sonnet: Cache-Schreiben (2,50 $/MTok) | 163 229 | 0,408 $ | 45 % |
| – davon erster Schritt je Runde (7 Runden) | ~74 500 | ~0,186 $ | 21 % |
| – davon nach Websuchen (Suchergebnisse) | ~66 900 | ~0,167 $ | 19 % |
| Sonnet: Ausgabe (inkl. Denken) | 14 868 | 0,149 $ | 17 % |
| Sonnet: Websuche-Gebühr (8 Suchen) | – | 0,080 $ | 9 % |
| Sonnet: Cache-Lesen (0,10 $/MTok) | 648 622 | 0,065 $ | 7 % |
| Sonnet: ungecachte Eingabe | 86 | ~0 $ | 0 % |
| Opus-Review (Ausgabe 8 000 = **abgeschnitten**, Cache-Write 7 263) | | 0,196 $ | 22 % |
| Haiku-Triage | 536 | 0,0001 $ | 0 % |

Befunde:
- Caching funktioniert gut (Lesezugriffe ≫ ungecachte Eingabe). Teuer sind die **Schreibvorgänge**: Präfix je Fonds (A1) und Suchergebnisse (A6/A7). **Websuche insgesamt ≈ 0,25 $ + Folgelesungen ≈ 35 % der Sonnet-Kosten.**
- Eine volle Runde (7–8 Schritte, 1–2 Suchen) kostet ≈ 0,15–0,20 $ (≈ 0,14–0,19 €). Die STATUS-Angabe „Tagesrunde aller drei ≈ 0,73 €“ deckt sich damit.
- **Hochrechnung bis 14.11. (15 Tage, ungeprüft):** 1 Tageslauf + ~4 Ereignisläufe/Tag × 3 Fonds × 0,18 $ ≈ 2,7 $/Tag ≈ **37 €**. Bei 12 Läufen/Tag ≈ 6,5 $/Tag ≈ **90 €**. Der Tagesdeckel von 12 € und der Gesamtdeckel von 190 € werden voraussichtlich **nicht** ausgeschöpft. **Das Budget ist nicht der Engpass, die Qualität der Entscheidungen schon.** Ein Teil des Spielraums ließe sich bewusst nutzen, z. B. für einen Fonds auf Opus 5.5 (4/20 $, doppelter Sonnet-Preis) oder mehr Recherche. Das entscheidet Rouven.
- Einsparpotenzial: A1 ≈ 5 %, A6 ≈ unbekannt (bis ~20 %, ungeprüft), Batch für das Review ≈ 0,1 $/Woche, A3 ändert nur die Buchhaltung. Wichtiger als Sparen: **den Review-Fehler (A4) beheben.**

---

_Verworfene Kandidaten dieser Kategorie: siehe [ANHANG-verworfen.md](ANHANG-verworfen.md), Abschnitt „8. LLM-Kosten, Gratis-Modelle, Dashboards“._

### Top-Empfehlungen

1. **Review-Fehler beheben (A4):** `max_tokens` 8000 schneidet das Opus-Review ab (Denken zählt mit), der Regel-JSON fehlt. Streaming + ~32 k + `stop_reason`-Prüfung, optional über die Batch-API (−50 %).
2. **DeepSeek-Modellnamen auf `deepseek-flash` umstellen (B7)** und DeepSeek als günstigen Nachfolger für die Claude-Fonds ab 14.11. einplanen (~0,01 $/Runde). Groq-Triage auf `openai/gpt-oss-20b` (B4).
3. **Präfix-Umbau für Cache-Sharing (A1)** + Cache-Lesepreis je Modell korrigieren (A3).
4. **Websuche: `web_search_20260209` A/B-testen (A6)**; mittelfristig ein gemeinsames billiges Suchwerkzeug für alle Modelle (DeepSeek Search 0,75 $/1000, A7). Das stellt die Fairness zur Liga her.
5. **OpenRouter: 10 $ einmalig aufladen (1000 statt 50 Anfragen/Tag)** und die `:free`-Auswahl nach Qualität (BFCL) statt nach Kontextlänge treffen (B1, B18). HF-Router oder NVIDIA NIM als Open-Weights-Quellen ergänzen (B9, B10).
6. **Dashboard: uPlot (22 kB gzip, MIT) ins Repo kopieren** für Equity mit Konfidenzband und Kalibrierung. Lightweight Charts (Apache-2.0, Logo/Hinweis lassen) für Instrumente mit Order-Markern. Dazu eine 10-kB-`widget.html` als PWA für Windows (C1, C2, C11, C12).
7. Strukturierte Ausgaben für Triage/Review statt Text-Parsing (A9).
