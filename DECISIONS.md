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
* **Wettmärkte:** Polymarket (CLOB-Buch je Token, Gebühr 0 – nur wenn `feeSchedule` anderes sagt, siehe ref), Kalshi (Gebühr 0,07·C·P·(1−P), Buch aus Orderbuch-Endpunkt),
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
Sonnet 5.5 mit `effort: medium` (Standard wäre high) und Prompt-Caching, damit die Runden bezahlbar bleiben; Haiku 5.5 sichtet vor (Triage), bevor Sonnet geweckt wird.

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
