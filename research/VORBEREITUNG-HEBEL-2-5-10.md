# Vorbereitung: große Hebel 2, 5 und 10 (brauchen Konten, Schlüssel oder einen Server)

Stand 31.10.2026. Diese drei Hebel aus [EMPFEHLUNG.md](EMPFEHLUNG.md) sind **nicht eingebaut**, weil sie ein Konto, eine Prüfung der Nutzungsbedingungen
im Browser oder einen eigenen Server brauchen – das ist Rouvens Entscheidung. Hier steht, was nötig ist und wo der Code andocken würde.

## Hebel 2 – Metaculus-Botturniere (FutureEval/MiniBench)

**Warum:** Hunderte unabhängig bewertete Prognosen je Saison – genau die Stichprobe, die der Arena für belastbare Kalibrierung fehlt; externer Vergleich.

**Was Rouven tun müsste:**
1. Metaculus-Konto anlegen, Bot-Konto/Token beantragen (Turnierregeln und ToS lesen).
2. Secret `METACULUS_TOKEN` setzen; optional LLM-Credits bei Metaculus beantragen (laut Ankündigung möglich).

**Wie es andocken würde (ohne neue Abhängigkeit im Dauerlauf):**
- Eigener Workflow `metaculus.yml` (täglich), getrennt vom Dauerlauf, mit `forecasting-tools` (MIT) nur in diesem Workflow installiert.
- Fragen holen → für jede Frage das vorhandene Superforecaster-Gerüst (`arena/agent/prompts.py`, Abschnitt „WAHRSCHEINLICHKEITEN“) mit einem
  günstigen Modell (nach dem 14.11. der per Model Confidence Set gewählte Nachfolger) → Prognose senden → in `data/metaculus/` protokollieren.
- Auswertung mit denselben Funktionen wie für Wettmärkte (`metrics.prognose_kennzahlen`, `statistik.murphy`, Kalibrierungskurve auf der Seite).
- Budget: eigener Tagesanteil in `config.json` (z. B. 0,5 €/Tag), damit der 12-€-Deckel hält.

## Hebel 5 – Hyperliquid als zweite Perp-Quelle

**Warum:** Funding/OI/Mark für ~225 Perps, L2-Buch, `predictedFundings` mit Binance-/Bybit-Raten – größtes Daten-Upgrade für Derivate.

**Was Rouven tun müsste:**
1. Die Nutzungsbedingungen von Hyperliquid im Browser prüfen (der automatische Abruf lieferte 403; eine Sperre wird **nicht** umgangen).
2. Bei Freigabe: nichts weiter – die Info-API ist öffentlich (POST `https://api.hyperliquid.xyz/info`).

**Wie es andocken würde:**
- `arena/data/http.py` bräuchte ein `post()` mit denselben Regeln (User-Agent, Mindestabstand, kein Wiederholen bei 403/451).
- `arena/data/crypto.py`: `hl_meta_and_ctxs()` (Typ `metaAndAssetCtxs`) und `hl_predicted_fundings()`; im Werkzeug `derivate_lage` als zweite Quelle,
  in der Marktlage als Funding-Vergleich Deribit vs. Hyperliquid vs. Binance/Bybit (Funding-Spread als Signal).
- Handel weiter nur auf Deribit-Büchern (eine Börse je Instrument, keine Vermischung der Abrechnung).
- WebSocket-Stream (L2 in Echtzeit) erst auf einem Server (siehe unten).

## Hebel 10 – Aktien/Makro auf offizielle Quellen

**Warum:** Yahoo drosselt Cloud-IPs; Vintages (ALFRED) schützen vor Lookahead.

**Was Rouven tun müsste (alles Gratis-Konten/-Schlüssel):**
| Quelle | Secret | Nutzen |
|---|---|---|
| FRED/ALFRED | `FRED_API_KEY` | **schon vorbereitet:** Veröffentlichungstermine (`makro.release_termine`) laufen, sobald das Secret existiert; Workflow-Zeile ist schon ergänzt |
| Alpaca Basic (Paper) | `ALPACA_KEY_ID`, `ALPACA_SECRET` | echte Quotes/Bars statt Yahoo, Grundlage für ein echtes Buch-Modell bei Aktien |
| Finnhub | `FINNHUB_KEY` | Earnings-Kalender, Unternehmensnachrichten |
| SEC EDGAR | – (kein Konto, aber User-Agent mit **Kontakt-E-Mail** Pflicht) | Form 4, 8-K, XBRL-Fundamentaldaten; braucht eine Kontaktadresse, die öffentlich im Code stünde → Rouvens Entscheidung |

**Wie es andocken würde:**
- `arena/data/stocks.py`: `kurs()`/`buch()` zuerst Alpaca, Rückfall Yahoo; das Impact-Modell (`exchange/impact.py`) nutzt dann echte Tagesvolumina.
- `arena/data/makro.py`: `serie()` über die FRED-API mit `realtime_start` (Vintage zum Entscheidungszeitpunkt) statt CSV-Export.
- Workflow `dauerlauf.yml`: im Schritt „Ticks, Entscheidungen, Review“ je Secret eine `env`-Zeile ergänzen
  (`FRED_API_KEY: ${{ secrets.FRED_API_KEY }}` usw.). Bewusst noch nicht geändert, damit der laufende Dauerlauf nicht berührt wird; fehlende Secrets
  wären ohnehin leer und würden sauber übersprungen. (`FRED_API_KEY` steht bereits im Dauerlauf-Workflow.)

## Server (Oracle-Gratis-ARM oder Hetzner) – Voraussetzung für 5 (WebSocket) und für dichtere Takte

Umstiegspunkte stehen in [EMPFEHLUNG.md](EMPFEHLUNG.md), Abschnitt 5 (Wächter > 10 min, Wetter-/Sportmärkte am Abrechnungstag, 429 bei Open-Meteo/GDELT).
Der Code ist serverfähig: `python -m arena.watcher` / `arena.entscheider` / `arena.takt` laufen unverändert per systemd-Timer; `scripts/dauerlauf.sh`
ist das Vorbild für die Schleife. Rouven müsste den Server anlegen (Konto) und die Secrets dort als Umgebungsvariablen setzen.
