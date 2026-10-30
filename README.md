# KI-Trader-Arena

Papierhandel-Experiment: KI-Agenten (vier Claude-Fonds inkl. A/B-Test + eine Modell-Liga, dazu ein Schwarm-Meta-Fonds und Kontrollfonds) handeln **simuliert** auf Wettmärkten, Krypto, Aktien/ETFs und Derivaten – auf einer streng realistischen Papier-Börse, gemessen gegen Vergleichsfonds ohne KI. **Nur Simulation, keine Anlageberatung, kein echtes Geld.**

Live-Seite: **https://rouvenwieland.github.io/ki-trader-arena/** · Maschinenlesbar: [`docs/status.json`](docs/status.json)

Plan und Entscheidungen: [PLAN.md](PLAN.md) · [DECISIONS.md](DECISIONS.md) · Stand/Grenzen: [STATUS.md](STATUS.md)

## Wie es funktioniert

| Baustein | Was | Wann |
|---|---|---|
| **Dauerlauf** (`dauerlauf.yml`, `scripts/dauerlauf.sh`, `arena/takt.py`) | Herzstück: ein sich selbst verkettender Job, der alle 15 min den Wächter laufen lässt und danach fällige Entscheider-Runden, das Wochen-Review und den Seiten-Deploy erledigt (GitHub-Cron ist für 15-min-Takte unzuverlässig). | ständig (Nachfolger startet automatisch) |
| **Wächter** (`arena/watcher.py`, Rückfall `waechter.yml`) | Daten holen, alle Portfolios zum Marktwert bewerten, Funding buchen, Stop-Loss/Take-Profit/Liquidation/Abrechnung ausführen, **Ereignisse** erzeugen (Kurssprung, Nachricht zu Position, Markt schließt < 24 h, große Wettmarkt-Bewegung, Volatilitätsausbruch, Fehlbewertung). Kein KI-Einsatz, kostenlos. | alle 15 min |
| **Entscheider** (`arena/entscheider.py`, Rückfall `entscheider.yml`) | Jeder Fonds-Agent bekommt Marktdaten + Werkzeuge und handelt mit Begründung, Zuversicht, Ausstiegsplan. Claude-Fonds mit eigenem Schwerpunkt und eigener Startliste (unabhängig). Feste Runden mit Sonnet, Tiefenrunde mit Opus, Ereignisrunden nach Haiku-Vorsichtung. | fest 0/3/6/9/15/18/21 UTC, Tiefenrunde 13 UTC, dazu bei weckendem Ereignis (≥ 45 min Abstand) |
| **Wochen-Review** (`arena/review.py`, `review.yml`) | Opus prüft die Strategien, schreibt `reports/JJJJ-Www.md` und gibt den Claude-Fonds Regeln ins Notizbuch. | sonntags |
| **Prognosen** (`scripts/prognosen.py`, `prognosen.yml`) | GARCH-Basislinie, TimesFM 2.5 (Apache-2.0) und Kronos (MIT, nur Richtung) auf CPU; jede Prognose wird protokolliert und gegen den echten Kurs bewertet (Trefferbilanz). | alle 6 h |
| **Webseite** (`docs/`, `arena/site.py`, `seite.yml`) | Dunkle Live-Seite: Verläufe, Rangliste mit Konfidenzintervallen, Prognosegüte gegen den Marktpreis (Kalibrierung), Schwarm & Kontrollen, Unabhängigkeit (Überlappung, Gleichlauf), Kosten je Fonds, Positionen, jede Entscheidung mit Begründung, Kennzahlen. `data.json` wird beim Deploy gebaut. | nach jedem Tick |

**Fonds:** `claude_vorsichtig`, `claude_mittel`, `claude_aggressiv` (je 10.000 €, eigene Denkschule, eigenes Notizbuch) und `claude_mittel_rm` (A/B-Zwilling von Mittel mit Risikomanager-Pass) · **Liga** (je ein Fonds, mittleres Risiko, gleiche Regeln/Daten) für jedes Modell mit vorhandenem Schlüssel: Gemini Flash, DeepSeek, Kimi/Moonshot, Cerebras, Mistral, OpenAI, plus automatisch gewählte OpenRouter-`:free`-Modelle · **Ohne LLM:** Schwarm (alle KI / nur Claude / nur Liga), Kontrollen „Markt-Kopierer“ und „Immer NEIN“, Regelfonds „Wetter-Ensemble“ · **Vergleich ohne KI:** Buy & Hold BTC, S&P-500-ETF, 60/40, Zufallsaffe.

**Börse (`arena/exchange/`):** Füllung gegen echte Orderbuchtiefe (Teilfüllung), Spread, Slippage, Gebühren je Plattform, Funding, Liquidation (Dochte zählen), Abrechnung der Wettmärkte, Positionsgrenzen je Risikoprofil. Alles Details in [DECISIONS.md](DECISIONS.md).

**Ehrlichkeit:** Jede Entscheidung wird mit Zeitstempel **vor** dem Ergebnis in `data/funds/<id>/decisions.jsonl` gespeichert (append-only, durch die Git-Historie nachprüfbar). Nur Vorwärtstest.

## Einrichten (einmalig)

1. **Secrets setzen:** Doppelklick auf `secrets-setzen.cmd` (Windows). Das Skript fragt den Anthropic-Schlüssel verdeckt ab und überträgt die übrigen Schlüssel aus OpenCodes `auth.json` als GitHub-Secrets. **Schlüssel nie im Chat posten.**
   Erwartete Secret-Namen: `ARENA_ANTHROPIC_KEY` (Claude), optional `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `MOONSHOT_API_KEY`, `GROQ_API_KEY`, `OPENAI_API_KEY`, `CEREBRAS_API_KEY`, `MISTRAL_API_KEY`, `NASA_FIRMS_KEY`.
   Ohne Schlüssel überspringt der jeweilige Fonds sauber (Status „wartet auf Schlüssel“); die Workflows bleiben grün.
2. **GitHub Pages aktivieren:** Repo → *Settings → Pages → Build and deployment → Source: **GitHub Actions***. Erledigt (30.10.). Der Dauerlauf stößt `seite.yml` nach jedem Tick an.
3. **Dauerlauf starten** (nur falls die Kette einmal reißt; der stündliche Cron startet ihn sonst selbst): *Actions → Dauerlauf → Run workflow*.
4. **Workflow-Rechte:** *Settings → Actions → General → Workflow permissions* auf „Read and write“ lassen/stellen (die Workflows fordern `contents: write` selbst an).
5. Optional: Gratis-Konto bei Alpaca (Papierhandel) für bessere Aktien-Daten – derzeit nicht eingebunden.

## Lokal

```bash
uv sync
uv run pytest -q                    # Tests (Börse, Budget, Ereignisse, Routing, Agentenschleife mit Fake-Modell)
uv run python -m arena.watcher      # ein Wächter-Lauf (schreibt nach data/)
uv run python -m arena.site         # baut docs/data.json und docs/status.json
ARENA_NUR_FONDS=claude_mittel uv run python -m arena.entscheider takt       # einzelne Fonds testen (braucht Schlüssel); taeglich = Opus-Tiefenrunde
```

Konfiguration (Deckel, Limits, Gebühren, Fonds, Schwellen): [`arena/config.json`](arena/config.json).

## Budget

Anthropic: Ziel 8–11 €/Tag über Tagesanteile je Claude-Fonds (4 × 2,75 € + 0,8 € Reserve), harter Tagesdeckel 12 €, Gesamtdeckel 190 €, Stopp im Code anhand gezählter Tokens × Preis (+15 % Sicherheit, Worst-Case-Reservierung vor jedem Aufruf). Rundenbudget mit Abschluss-Hinweis; Tempo-Faktor streckt das Restbudget bis zum Stichtag. Opus für die tägliche Tiefenrunde und das Wochen-Review. Kosten je Fonds stehen auf der Seite und in `status.json`. Ab **14.11.2026** oder bei erschöpftem Gesamtbudget wechseln die Claude-Fonds automatisch auf ein Liga-Modell – gewählt per Model Confidence Set (das günstigste unter den statistisch nicht unterscheidbaren Besten, 7 Tage stabil, `data/modellwahl.json`) (Wechsel erscheint in der Seite und in `data/model_switches.jsonl`).

## Laptop-Widget

`docs/status.json` (Schema-Version 1): `rangliste[]` (Rang, Name, Typ, Rendite %, Wert €, Max-Drawdown, Status, Modell, `kosten_heute_eur`, `kosten_gesamt_eur`, `verlauf_pct[]`), `budget` (inkl. `ziel_tag_eur`, `tempo_faktor`), `ueberlappung_claude_pct`, `letzte_entscheidungen[]`, `ereignisse[]`, `wartend[]`. Kachel dafür: PR „KI-Trader-Arena“ im Repo `windows-dashboard`. Abrufbar unter `https://rouvenwieland.github.io/ki-trader-arena/status.json` oder roh über `raw.githubusercontent.com/rouvenwieland/ki-trader-arena/main/docs/status.json`.

## Daten & Recht

Nur kostenlose, öffentliche Quellen ohne Login, mit ehrlichem User-Agent, Zwischenspeicher, Abstand je Host und Schutzschalter bei Fehlern; Sperren (Binance 451, Reddit/Yahoo 403/429) werden **nicht** umgangen. Wettmärkte nur lesend. OSIRIS wird bewusst nicht eingebunden.
