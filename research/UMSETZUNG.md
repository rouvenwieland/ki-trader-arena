# Umsetzung der Empfehlung (30./31.10.2026, Cloud-Session)

Grundlage: [EMPFEHLUNG.md](EMPFEHLUNG.md). Begründungen jeder Entscheidung: [DECISIONS.md](../DECISIONS.md), Abschnitt „Umsetzung der Recherche-Empfehlung“.
Alles nur Papierhandel. 104 Tests grün (vorher 73). Keine neuen Python-Abhängigkeiten (Statistik, GARCH, MCS rein in Python).

## 0. Fehler (alle behoben)
| # | Ergebnis |
|---|---|
| B1 | Polymarket-Taker-Gebühr `C·rate·(p(1−p))^exp` aus `feeSchedule` je Markt, Doku-Beispiel als Test (1,75 $). |
| B2 | Alle Anthropic-Aufrufe gestreamt; Review mit 32k, `max_tokens` = Fehler (kein Regel-Import, Nachholen). **W44 wurde live neu erzeugt – vollständig, mit Regeln.** Agentenrunden werten Abschneiden nicht mehr als Rundenende; Haiku-Vorsichter 1,5k statt 300 Tokens. |
| B3 | Kronos nur noch Richtung; GARCH(1,1)-Band als Basislinie (Rückblick-Abdeckung ≈ 81 %); jede Prognose wird protokolliert und gegen den echten Kurs bewertet. |
| B4 | Reddit nur Atom mit echten Zeiten, GDELT `seendate`. |
| B5 | Cache-Lesepreis je Modell; System-Prompt geteilt in gemeinsamen (gecachten) und Fonds-Teil. |
| B6 | Liga-Modellnamen über die echte Modellliste des Anbieters; Groq-Triage `gpt-oss-20b`; Cerebras als „kein Gratis-Kontingent“ markiert. |

## 1. Schnelle Gewinne (alle 10)
1. Denkschulen je Claude-Fonds, eigene Ereignis-Reihenfolge, Rechercheplan des Vorsichters.
2. Pflichtfelder (Abrechnung, Status quo, Basisrate, `p_blind`, `p_ja`/`p_nein` getrennt, Invalidierung, Gegenargument, `risiko_usd`, Zuversicht-Skala).
3. Marktrelative Prognose-Kennzahlen (Brier-Skill gg. Markt, marktbereinigt mit KI, Log-Score, Murphy, Kalibrierung, Gewinn/Kontrakt; Filter nach Ereignis).
4. Ehrliche Rangliste (Block-Bootstrap-KI, PSR, Deflated Sharpe, MinTRL, p-Wert gg. BTC).
5. Reflexion bei Abrechnung (Haiku-Lektion ins Notizbuch) + Kalibrier-Rückmeldung im Rundenprompt.
6. GARCH-Band im Prognose-Werkzeug.
7. Deribit DVOL, exaktes Funding je Zeitraum, Basis-Kurve (Werkzeug `derivate_lage`).
8. Orderfluss-Werkzeug (Polymarket Verlauf/Trades/Halter/OI, Kalshi Trades).
9. Fed-/EZB-/SEC-RSS, FOMC-Termine (FRED-Termine mit optionalem Schlüssel).
10. Kontrollfonds „Markt-Kopierer“ und „Immer NEIN“.

## 2. Große Hebel
| # | Stand |
|---|---|
| 1 Schwarm | **umgesetzt**: drei Meta-Fonds (alle/Claude/Liga), 0 Tokens, Mischung mit Markt, ¼-Kelly. |
| 2 Metaculus | vorbereitet/dokumentiert (Konto nötig) → [VORBEREITUNG-HEBEL-2-5-10.md](VORBEREITUNG-HEBEL-2-5-10.md) |
| 3 Wetter | **umgesetzt**: Werkzeug `wetter` (Open-Meteo GFS+ECMWF, 82 Mitglieder, NWS-Beobachtung) + Regelfonds „Wetter-Ensemble“. |
| 4 Größen/Risiko | **umgesetzt**: Werkzeug `positionsgroesse` (Kelly simultan inkl. Gebühr, Vol-Ziel), Krypto- und Themen-Cluster-Limits. |
| 5 Hyperliquid | vorbereitet/dokumentiert (ToS-Prüfung im Browser nötig). |
| 6 Notizbuch + Policy | **umgesetzt**: Wichtigkeit/Zerfall/Ablauf, Policy-Gate (≥ 5 Verlust-Trades → Sperre, nur Review lockert). |
| 7 Börsen-Realismus | **umgesetzt**: verbrauchte Buchtiefe je Lauf, Square-Root-Impact für Stops und Aktienbuch. |
| 8 Modellwahl | **umgesetzt**: Model Confidence Set, günstigstes unter den Besten, 7 Tage stabil. |
| 9 A/B + Risikomanager | **umgesetzt**: „Claude Mittel+RM (A/B)“ mit Haiku-Gegenprüfung großer Orders. |
| 10 Offizielle Quellen | teilweise vorbereitet (FRED-Schlüssel optional); Alpaca/Finnhub/EDGAR brauchen Konten bzw. Kontaktadresse. |

## 3. Seite
Neue Abschnitte „Prognosegüte – besser als der Marktpreis?“ (mit Kalibrierungsdiagramm und Konfidenzbalken) und „Schwarm & Kontrollen“; Rangliste mit
95-%-Spanne, „Können?“, „Messbar ab“, p gg. BTC; Kosten mit Gewinn je API-€, A/B-Kasten, Nachfolger-Vorschau; Gleichlauf. Headless geprüft
(1440 px / 390 px): keine Konsolenfehler, kein horizontales Scrollen.

## Was sich ab jetzt beobachten lässt
- Prognosen werden erst mit der Abrechnung bewertbar: Brier-Skill gegen den Markt und Kalibrierung füllen sich in den nächsten Tagen.
- Konfidenzintervalle erscheinen je Fonds ab 24 Stunden Verlauf; „messbar ab“ zeigt, wie lange es bei gleicher Güte bis zum Beleg dauert.
- Wetter-Regelfonds und Schwarm sind die ersten Kandidaten für einen *messbaren* Vorteil gegenüber dem Markt-Kopierer.
