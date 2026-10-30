# Entscheidungen (selbstständig getroffen, Nacht vom 29./30.10.2026)

Rouven schlief; Fragen wurden nicht gestellt. Jede Entscheidung mit Begründung – zum Überstimmen gern.

## Agenten-Rahmen: eigene Schleife statt Hermes Agent
Geprüft (Doku/Issues von NousResearch/hermes-agent): Hermes läuft nicht-interaktiv (`hermes chat -q …`), ist aber ein
Desktop-/Terminal-Agent mit eigener Installation per `curl | bash`, eigenem Zustand (`HERMES_HOME`), Einrichtungsassistent
(hängt laut Issue #905 in kopflosen Umgebungen) und eigener Werkzeug-/Speicherwelt. Anforderungen hier: **hartes Budget anhand
gezählter Tokens im Code**, identische Werkzeuge und Daten für alle Modelle, Entscheidung mit Zeitstempel **vor** dem Ergebnis,
deterministische Börse. Das ist mit einem Fremd-Agenten in 30 Minuten nicht sauber lösbar. → Schlanke eigene Schleife
(`arena/agent/loop.py`): Anthropic Messages API mit Tool-Use über das offizielle SDK, dieselben Werkzeuge für Liga-Modelle über
OpenAI-kompatible Endpunkte. Hermes bleibt als spätere Option (z. B. auf dem Oracle-Server), die Werkzeuge sind austauschbar.

## Währung
Das Hauptbuch läuft in **USD** (alle Plattformen rechnen in USD). Startkapital = 10.000 € zum Kurs bei Fondsstart
(Coinbase EUR→USD). Anzeige in € zum aktuellen Kurs; Renditen werden in USD gerechnet (kein Währungsrauschen im Ranking).

## Börse
* **Bewertung zum Geldkurs** (Long-Bestände) bzw. Markpreis (Perps): was man real bekäme, nicht die Mitte. Spread ist sofort sichtbar.
* **Perps:** Deribit **linear USDC-Perpetuals** (BTC/ETH/SOL), nicht die inversen BTC-Perps – lineare Auszahlung ist realistisch und einfacher korrekt abzubilden.
  Isolierte Marge, Wartungsmarge 0,5 %, Liquidationsgebühr 0,5 %, Funding je Tick mit der aktuellen 8-h-Rate.
* **Dochte:** Stop-Loss/Take-Profit/Liquidation werden gegen das Tief/Hoch der 1-Minuten-Kerzen seit dem letzten Tick geprüft
  (Coinbase bzw. Deribit), nicht nur gegen den 15-Minuten-Kurs. Ein ausgelöster Stop füllt zum Stop-Preis (mit Slippage), bei Kurslücke zum aktuellen Buch.
* **Optionen:** nur gekauft (Long), zu Deribit-Orderbuchpreisen in USD umgerechnet, Abrechnung zum Deribit-Lieferpreis (Innenwert). Verkauf/Short wegen unbegrenzten Risikos nicht erlaubt.
* **Wettmärkte:** Polymarket (CLOB-Buch je Token, Taker-Gebühr `C·rate·(p·(1−p))^exponent` aus dem `feeSchedule` des Marktes, gerundet auf 5 Stellen – *korrigiert 31.10., vorher wurde sie trotz dieser Zeile nie gebucht*), Kalshi (Gebühr 0,07·C·P·(1−P), Buch aus Orderbuch-Endpunkt),
  PredictIt (nur Spitze des Buchs bekannt → **konservative synthetische Tiefe**: 100 Kontrakte je Preisstufe, je 1 ct schlechter; 10 % Gewinngebühr, 850-$-Limit;
  die 5 % Auszahlungsgebühr bleibt unberücksichtigt), Manifold (Spielgeld-CPMM, Preiswirkung exakt aus dem Pool berechnet, wird wie USD behandelt – nur als Signalquelle ernst nehmen).
  Abrechnung über die Plattform-APIs (Ja/Nein/Teilwert/Storno). PredictIt-Ergebnisse sind per API schwer ablesbar → Position bleibt dann offen.
* **Aktien:** Yahoo-Chart-Endpunkt ohne Login, synthetisches Buch (±1 bp Halb-Spread), kein Handel bei geschlossener Börse. Stooq verlangt einen JavaScript-Nachweis (Anti-Bot) → **nicht umgangen**, nicht genutzt.
  Yahoo drosselt Cloud-IPs teilweise (429); dann fehlen Aktien-Fonds/-Preise vorübergehend, der Rest läuft weiter (Schutzschalter in `data/http.py`).
* **Binance/Bybit:** sperren US-IPs (Binance liefert 451) → nicht genutzt. Coinbase (Spot, Kerzen), Kraken (Fallback), Deribit public (Perps, Optionen, Funding), CoinGecko nicht nötig.

## Budget
Preise (USD je Mio. Token): Haiku 5.5 0,10/0,50, Sonnet 5.5 2/10, Opus 5.5 4/20; Websuche 10 $/1000; Cache-Lesen 0,1×, -Schreiben 1,25×; **+15 % Sicherheitsaufschlag**.
Vor jedem Aufruf wird der Worst-Case (gesamter Verlauf als frische Eingabe + volle Ausgabe) gegen Tages-, Fonds- und Gesamtdeckel geprüft, danach gebucht (`data/budget.json`, `budget_log.jsonl`).
Der Tagesdeckel (12 €) wird in drei gleiche Tagesanteile je Claude-Fonds geteilt, damit der aggressive Fonds nicht alles verbrennt; das Wochen-Review (Opus) nutzt nur den globalen Deckel.
Tagesdeckel erreicht → der Fonds pausiert bis morgen. **Gesamtdeckel (190 €) erschöpft oder ab 2026-11-14** → die Claude-Fonds wechseln auf das bis dahin renditebeste Liga-Modell
(`model_switches.jsonl`, sichtbar in der Webseite). Websuche: das Server-Werkzeug `web_search_20250305` (günstig, vorhersehbare Kosten) statt der neueren dynamischen Variante mit Code-Ausführung.
Sonnet 5.5 mit `effort: high` und Prompt-Caching (ein erster Live-Lauf mit „medium“ kostete nur ~0,04 $ je Runde, die Agenten recherchierten aber kaum → Mindestaufwand im Prompt + höherer Effort); Haiku 5.5 sichtet vor (Triage), bevor Sonnet geweckt wird.

## Takt
Wächter alle 15 Minuten (Cron ~:07/:22/:37/:52, GitHub verzögert Cron gern). Entscheider bei weckendem Ereignis (Abstand ≥ 45 Min, max. 12/Tag) plus fest täglich 13:17 UTC.
Gemeinsame Concurrency-Gruppe `arena-zustand` serialisiert alle Zustandsschreiber (kein Konflikt auf `data/`).

## Daten im Repo
`data/` wächst: pro Tick eine Zeile Kursverlauf (≈ 60 Instrumente) + Equity je Fonds. Das sind grob 100–200 kB/Tag. Bei Bedarf später komprimieren/auslagern.
Wetten-Schnappschüsse (Universum) werden **nicht** committet, nur Preise der Top-40 und gehaltener Märkte.

## Webseite
`docs/index.html` (statisch, ohne externe Abhängigkeiten) liest `docs/data.json`; `docs/status.json` ist die schlanke Fassung für das Laptop-Widget.
GitHub Pages: per API von hier nicht aktivierbar (Proxy sperrt den Pages-Pfad) → Workflow `seite.yml` versucht `configure-pages` mit `enablement`, sonst einmalig
**Settings → Pages → Source: GitHub Actions** setzen (siehe README).

## Prognose-Werkzeuge
Siehe STATUS.md (TimesFM/Kronos).

## Abnahme durch unabhängigen Prüfer-Agenten (30.10.)
Ein getrennter Agent prüfte die Börse nur lesend mit eigenen Reproduktionsskripten. Bestätigt und **behoben** (mit Regressionstests): NaN/ungültige Eingaben (Cash-Zerstörung),
Perp-Einzellimit per Mehrfach-Orders, Dochte vor Eröffnung lösten Stops/Liquidation aus, Funding für Zeit vor der Eröffnung, ungenauer Liquidationspreis, Funding-Doppelzählung in `realisiert`,
ungültige Orderbuch-Stufen (Preis ≤ 0), Stop/Take-Profit auf falscher Seite, Standard-Equity bei Perps.
Bekannte, bewusst belassene Annahmen: Equity bewertet zum Geldkurs **ohne** künftige Ausstiegsgebühr (leicht optimistisch); `realisiert` enthält Einstiegsgebühren nicht (stehen in `gebuehren`/`netto_pnl`);
Storno erstattet nur den Einsatz; PredictIt-10-%-Gebühr je Teilschließung ohne Verlustverrechnung und ohne 5 % Auszahlungsgebühr; Take-Profit verhält sich wie Stop (füllt zum schlechteren Buch);
Funding mit Einstandsnominal und höchstens 6 h je Tick; Mindest-Cash ignoriert Gebühren; JA/NEIN desselben Marktes und Spot/Perp werden getrennt gezählt (Hedges nicht verrechnet).

## Ausbau 30.10. (Tagschicht, Rouven nicht erreichbar)

### Betrieb: Dauerlauf statt 15-Minuten-Cron
Befund: Zwischen 00:53 und 10:00 UTC lief der Wächter genau **ein** Mal per Cron (06:10) statt ~36 Mal; die Seite stand 4 h still.
GitHub verzögert/verwirft Cron-Läufe bei hoher Frequenz (besonders in neuen Repos). → `dauerlauf.yml` + `scripts/dauerlauf.sh`:
ein Job (≤ 5 h 15 min) macht alle 15 min einen Wächter-Tick, danach – nacheinander im selben Job – fällige Entscheider-Runden,
Wochen-Review und Seiten-Deploy. Den Nachfolger reiht er **gleich zu Beginn** per `workflow_dispatch` in dieselbe Concurrency-Gruppe ein;
er startet, sobald der Vorgänger endet (auch bei Zeitlimit). Stündlicher Cron nur als Rückfallebene. Vorteile: keine parallelen
Schreiber auf `data/` (vorher konnten in der gemeinsamen Gruppe wartende Läufe von neueren verdrängt werden – ein Entscheider hätte
still verschwinden können), alle Zeitpläne im Code (`arena/takt.py`), unbegrenzte Actions-Minuten im öffentlichen Repo.
Die alten Workflows bleiben für Handstarts/Rückfall und tun nichts, solange ein Dauerlauf aktiv ist.

### Budget ausreizen (Ziel ≈ 10 €/Tag, Deckel 12 € bleibt)
Eine Tagesrunde kostete nur ≈ 0,73 €. Gewählt: **feste Runden alle ~3 h** (0, 3, 6, 9, 15, 18, 21 UTC, Sonnet 5.5, ohne Vorsichter; erster Live-Lauf mit 4-h-Takt hätte nur ≈ 4–5 €/Tag verbraucht, weil die Agenten nach 6–7 Schritten von selbst aufhörten → engerer Takt plus Rundenauftrag: je feste Runde mindestens fünf neue Kandidaten im Schwerpunkt und vier Recherchen, Handeln bleibt freiwillig) und
**13 UTC Tiefenrunde mit Opus 5.5** für *jeden* Claude-Fonds (statt eines gemeinsamen „Chefanalysten“ – ein gemeinsamer Analyst
würde allen drei Fonds dieselbe Sicht geben und das Klumpenrisiko verschärfen). Dazu Ereignisrunden mit Haiku-Vorsichter.
Tiefer: 20 Schritte/8 Websuchen (Sonnet), 26 Schritte/12 Websuchen/12k Ausgabe (Opus), Effort „high“ (bei Opus 5.5 explizit, da Standard „medium“).
Steuerung im Code: Tagesanteile je Fonds (3,3/3,4/3,5 € + 0,8 € Reserve für Vorsichter/Review), **Rundenbudget** = Rest des Tagesanteils
verteilt auf die noch kommenden festen Runden (Tiefenrunde doppelt, Ereignis halb, Deckel 1,30 $ bzw. 3,00 $). Wird es knapp, bekommt der
Agent einen **Abschluss-Hinweis** („jetzt entscheiden, Tagebuch schreiben“) und noch 3 Schritte – statt mitten in der Recherche abgeschnitten
zu werden (vorher endeten Runden ohne Orders/Tagebuch). Gleiches beim Schritt- und Zeitlimit. **Tempo-Faktor:** reicht das Restbudget bis
14.11. nicht für die vollen Tagesanteile, werden alle Anteile proportional gekürzt – das Geld reicht so sicher bis zum Stichtag.
Claude-Fonds laufen jetzt **parallel** (eine Runde dauert mit Opus länger); der globale Deckel bleibt hart, weil jeder Aufruf seinen
Worst-Case vorher atomar reserviert. Websuche bleibt `web_search_20250305` (vorhersehbare Kosten; die dynamische Variante führt Code aus).

### Unabhängigkeit der Claude-Fonds (Klumpenrisiko)
Alle drei hielten dieselbe Iran-Waffenruhe-Wette – sie sahen dieselbe Top-30-Liste nach Umsatz und starteten bei derselben Spitzenwette.
Ohne Verbot: je Fonds ein **Schwerpunkt** und **Recherchepfad** im Systemprompt (Vorsichtig: Makro/Zinsen/Wetter/Anleihen;
Mittel: Unternehmen/Tech/Sport/Wahlen außerhalb der USA/Einzelaktien; Aggressiv: Krypto, Perps, Optionen, Volatilität) und eine eigene
**Startliste** der Wettmärkte (Schwerpunkt-Treffer zuerst, Rest als je Fonds und Tag eigene Stichprobe). Handeln außerhalb ist erlaubt,
muss aber begründet werden. Die Fonds sehen einander nicht (geprüft: Prompt enthält keine anderen Fonds, Ereignisse sind je Fonds gefiltert).
Liga-Fonds bekommen weiter dieselbe Liste (fairer Modellvergleich). Kennzahl **Überlappung** je Paar: Anteil des investierten Kapitals des
kleineren Fonds in denselben Wetten (Spot und Perp desselben Coins long = gleiche Wette). Startwert: 100 %.

### Liga-Fehler
* OpenAI „no credits“ (429 insufficient_quota) → neue Ausnahme `KeinGuthaben`, Fonds **„pausiert (kein Guthaben)“**, Neuversuch nach 20 h.
  Bewusst eng erkannt: Geminis Minuten-Ratenlimit spricht auch von „quota … billing“, ist aber vorübergehend.
* Gemini 503 → bis zu 5 Versuche mit exponentiellem Warten (5–40 s, Retry-After beachtet); nach zwei 5xx Wechsel auf ein Ausweichmodell
  desselben Anbieters (`alternativen` in `config.json`). Status dann „vorübergehend gestört“ statt „Fehler“.
* Modellnamen: Ausweichliste je Anbieter; ein automatisch aufgelöster Name (404 → Modellliste) wird im Fonds gemerkt.
* OpenRouter: einmal gewählte `:free`-Modelle bleiben stabil (ein Fonds = ein Modell), tägliche Prüfung, ob sie noch gratis sind; vor der
  Auswahl ein **Probeaufruf** – live gefunden: manche gelisteten Gratis-Modelle sind gesperrt („only available on agentic harnesses“).
  Liga-Pfad live gegen ein OpenRouter-Gratismodell geprüft (5 Schritte, 1 Order, Tagebuch).
* Liga-Fonds laufen in festen Runden nur um 6 und 21 UTC (+ Tiefenrunde, + Ereignisse mit Groq-Vorsichter), damit DeepSeek/Kimi auf
  Rouvens eigenem Guthaben nicht 6× täglich Geld kosten.

### Daten
`docs/data.json` wird nicht mehr versioniert (wuchs als ~50–100-kB-Datei bei jedem Tick um ~2 MB/Tag im Git); der Seiten-Workflow baut sie
vor dem Deploy aus `data/`. `docs/status.json` (6 kB) bleibt im Git, weil die Laptop-Kachel sie als Rückfall roh aus dem Repo liest.

## Umsetzung der Recherche-Empfehlung (31.10., Cloud-Session, Rouven nicht erreichbar)

### Abschnitt 0 – Fehler
* **B1 Polymarket-Gebühr:** Formel und Rundung wörtlich aus der Doku; Rate/Exponent je Markt aus `feeSchedule` (bei `feesEnabled: false` → 0).
  Altpositionen ohne Rate bekommen den konfigurierten Standard (0). Regressionstest mit dem Doku-Beispiel (100 × 0,50 bei 0,07 → 1,75 $).
* **B2 Review/Opus:** Alle Anthropic-Aufrufe laufen jetzt **gestreamt** (`messages.stream` + `get_final_message`), damit große `max_tokens`
  keine HTTP-Zeitlimits reißen. Review mit 32k Ausgabe (Opus 5.5 denkt immer, Denk-Tokens zählen mit). `stop_reason == "max_tokens"` gilt als
  Fehler: das Review wird als `…-abgeschnitten.md` abgelegt, **keine** Regeln übernommen, und der Taktgeber holt das Review derselben Woche einmal nach.
  Das abgeschnittene W44 wurde deshalb nach `reports/2026-W44-abgeschnitten.md` verschoben → der nächste Takt erzeugt W44 neu.
  In Agentenrunden wird eine abgeschnittene Antwort nicht mehr als Rundenende gewertet: angefangene Werkzeugaufrufe werden als Fehler
  beantwortet (die API verlangt zu jedem `tool_use` ein `tool_result`), dazu ein Hinweis, kürzer weiterzuarbeiten (höchstens zweimal).
  Ausgabelimits: Sonnet 12k, Opus-Tiefenrunde 20k, Haiku-Vorsichter 1,5k (300 schnitt laut Log die JSON-Antwort ab → „Triage fehlgeschlagen“).
  Die serverseitigen `fallbacks` (Ausweichmodell bei Ablehnung) bleiben bewusst **aus**: Ein anderes Modell würde den Modellvergleich verfälschen,
  und eine abgelehnte Runde kostet im Papierhandel nichts.
