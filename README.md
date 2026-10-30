# KI-Trader-Arena

Papierhandel-Experiment: KI-Agenten (drei Claude-Fonds + eine Modell-Liga) handeln **simuliert** auf Wettmärkten, Krypto, Aktien/ETFs und Derivaten – auf einer streng realistischen Papier-Börse, gemessen gegen Vergleichsfonds ohne KI. **Nur Simulation, keine Anlageberatung, kein echtes Geld.**

Live-Seite (nach Aktivierung von GitHub Pages): `https://rouvenwieland.github.io/ki-trader-arena/` · Maschinenlesbar: [`docs/status.json`](docs/status.json)

Plan und Entscheidungen: [PLAN.md](PLAN.md) · [DECISIONS.md](DECISIONS.md) · Stand/Grenzen: [STATUS.md](STATUS.md)

## Wie es funktioniert

| Baustein | Was | Wann |
|---|---|---|
| **Wächter** (`arena/watcher.py`, Workflow `waechter.yml`) | Daten holen, alle Portfolios zum Marktwert bewerten, Funding buchen, Stop-Loss/Take-Profit/Liquidation/Abrechnung ausführen, **Ereignisse** erzeugen (Kurssprung, Nachricht zu Position, Markt schließt < 24 h, große Wettmarkt-Bewegung, Volatilitätsausbruch, Fehlbewertung). Kein KI-Einsatz, kostenlos. | alle 15 min |
| **Entscheider** (`arena/entscheider.py`, `entscheider.yml`) | Jeder Fonds-Agent bekommt denselben Daten-Schnappschuss + Werkzeuge und handelt mit Begründung, Zuversicht, Ausstiegsplan. Haiku sichtet vor, Sonnet entscheidet. | bei weckendem Ereignis (Abstand ≥ 45 min, max. 12/Tag) + täglich 13:17 UTC |
| **Wochen-Review** (`arena/review.py`, `review.yml`) | Opus prüft die Strategien, schreibt `reports/JJJJ-Www.md` und gibt den Claude-Fonds Regeln ins Notizbuch. | sonntags |
| **Prognosen** (`scripts/prognosen.py`, `prognosen.yml`) | TimesFM 2.5 (Apache-2.0) und Kronos (MIT) auf CPU, Unsicherheitsband, als Werkzeug für die Agenten. | alle 6 h |
| **Webseite** (`docs/`, `arena/site.py`, `seite.yml`) | Dunkle Live-Seite: Verläufe, Rangliste, Positionen, jede Entscheidung mit Begründung, Kosten, Kennzahlen. | nach jedem Lauf |

**Fonds:** `claude_vorsichtig`, `claude_mittel`, `claude_aggressiv` (je 10.000 €, eigene Persönlichkeit, eigenes Notizbuch) · **Liga** (je ein Fonds, mittleres Risiko, gleiche Regeln/Daten) für jedes Modell mit vorhandenem Schlüssel: Gemini Flash, DeepSeek, Kimi/Moonshot, Cerebras, Mistral, OpenAI, plus automatisch gewählte OpenRouter-`:free`-Modelle · **Vergleich ohne KI:** Buy & Hold BTC, S&P-500-ETF, 60/40, Zufallsaffe.

**Börse (`arena/exchange/`):** Füllung gegen echte Orderbuchtiefe (Teilfüllung), Spread, Slippage, Gebühren je Plattform, Funding, Liquidation (Dochte zählen), Abrechnung der Wettmärkte, Positionsgrenzen je Risikoprofil. Alles Details in [DECISIONS.md](DECISIONS.md).

**Ehrlichkeit:** Jede Entscheidung wird mit Zeitstempel **vor** dem Ergebnis in `data/funds/<id>/decisions.jsonl` gespeichert (append-only, durch die Git-Historie nachprüfbar). Nur Vorwärtstest.

## Einrichten (einmalig)

1. **Secrets setzen:** Doppelklick auf `secrets-setzen.cmd` (Windows). Das Skript fragt den Anthropic-Schlüssel verdeckt ab und überträgt die übrigen Schlüssel aus OpenCodes `auth.json` als GitHub-Secrets. **Schlüssel nie im Chat posten.**
   Erwartete Secret-Namen: `ARENA_ANTHROPIC_KEY` (Claude), optional `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `MOONSHOT_API_KEY`, `GROQ_API_KEY`, `OPENAI_API_KEY`, `CEREBRAS_API_KEY`, `MISTRAL_API_KEY`, `NASA_FIRMS_KEY`.
   Ohne Schlüssel überspringt der jeweilige Fonds sauber (Status „wartet auf Schlüssel“); die Workflows bleiben grün.
2. **GitHub Pages aktivieren:** Repo → *Settings → Pages → Build and deployment → Source: **GitHub Actions***. (Per API aus der Bauumgebung nicht möglich.) Danach deployt `seite.yml` nach jedem Lauf.
3. **Workflow-Rechte:** *Settings → Actions → General → Workflow permissions* auf „Read and write“ lassen/stellen (die Workflows fordern `contents: write` selbst an).
4. Optional: Gratis-Konto bei Alpaca (Papierhandel) für bessere Aktien-Daten – derzeit nicht eingebunden.

## Lokal

```bash
uv sync
uv run pytest -q                    # Tests (Börse, Budget, Ereignisse, Routing, Agentenschleife mit Fake-Modell)
uv run python -m arena.watcher      # ein Wächter-Lauf (schreibt nach data/)
uv run python -m arena.site         # baut docs/data.json und docs/status.json
ARENA_NUR_FONDS=claude_mittel uv run python -m arena.entscheider taeglich   # einzelne Fonds testen (braucht Schlüssel)
```

Konfiguration (Deckel, Limits, Gebühren, Fonds, Schwellen): [`arena/config.json`](arena/config.json).

## Budget

Anthropic: Tagesdeckel 12 € (geteilt durch die drei Claude-Fonds), Gesamtdeckel 190 €, harter Stopp im Code anhand gezählter Tokens × Preis (+15 % Sicherheit); Opus nur für das Wochen-Review. Ab **14.11.2026** oder bei erschöpftem Gesamtbudget wechseln die Claude-Fonds automatisch auf das bis dahin renditebeste Liga-Modell (Wechsel erscheint in der Seite und in `data/model_switches.jsonl`).

## Laptop-Widget

`docs/status.json` (Schema-Version 1): `rangliste[]` (Rang, Name, Rendite %, Wert €, Max-Drawdown), `budget`, `letzte_entscheidungen[]`, `ereignisse[]`, `wartend[]`. Abrufbar unter `https://rouvenwieland.github.io/ki-trader-arena/status.json` oder roh über `raw.githubusercontent.com/rouvenwieland/ki-trader-arena/main/docs/status.json`.

## Daten & Recht

Nur kostenlose, öffentliche Quellen ohne Login, mit ehrlichem User-Agent, Zwischenspeicher, Abstand je Host und Schutzschalter bei Fehlern; Sperren (Binance 451, Reddit/Yahoo 403/429) werden **nicht** umgangen. Wettmärkte nur lesend. OSIRIS wird bewusst nicht eingebunden.
