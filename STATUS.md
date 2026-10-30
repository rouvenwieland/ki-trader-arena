# STATUS (Stand 30.10.2026 abends – Umsetzung der Recherche-Empfehlung)

Live: **https://rouvenwieland.github.io/ki-trader-arena/** · `status.json` für die Laptop-Kachel · Entscheidungen mit Begründung in [DECISIONS.md](DECISIONS.md) ·
Kurzfassung der Umsetzung in [research/UMSETZUNG.md](research/UMSETZUNG.md)

## Erledigt (diese Session)

Umgesetzt wurde [research/EMPFEHLUNG.md](research/EMPFEHLUNG.md): Abschnitt 0, alle zehn schnellen Gewinne und die großen Hebel 1, 3, 4, 6, 7, 8 und 9.
Alles liegt in kleinen, getesteten Commits direkt auf `main`; 105 Tests sind grün (vorher 73), und der Test-Workflow auf GitHub war bei jedem Push grün.
Neue Python-Pakete gibt es nicht.

**Fehler (Abschnitt 0)**
- **Polymarket-Gebühr:** wird jetzt aus dem `feeSchedule` jedes Marktes gebucht (vorher immer 0).
- **Opus-Review:** gestreamt, 32k Ausgabe, Abschneiden gilt als Fehler. Das abgeschnittene **W44 wurde live vollständig neu erzeugt**, und die Regeln stehen jetzt in den Notizbüchern.
- **Kronos:** liefert nur noch eine Richtung. Neue Basislinie ist ein **GARCH-Band**, die Trefferbilanz aller Prognosemodelle wird laufend gemessen.
- **Nachrichten:** Reddit kommt per Atom-Feed mit echten Zeitstempeln, GDELT ebenso.
- **Kosten:** Cache-Preise je Modell; der Prompt-Cache wird zwischen den Fonds geteilt.
- **Liga:** Modellnamen werden über die echte Modellliste des Anbieters aufgelöst; Groq-Vorsichter ist jetzt `gpt-oss-20b`.

**Neue Agenten-Fähigkeiten (für Claude und Liga gleich)**
- **Denkschulen:** Vorsichtig = Basisraten, Mittel = Arbitrage und Regeln, Aggressiv = Momentum. Jeder Fonds sieht die Ereignisse in eigener Reihenfolge und bekommt einen Rechercheplan vom Vorsichter.
- **Pflichtfelder:** Superforecaster-Gerüst mit `p_blind` und getrennt geschätzten `p_ja`/`p_nein`. Orders brauchen Invalidierung, Gegenargument und `risiko_usd`; unter 0,4 Zuversicht wird nicht gekauft.
- **Neue Werkzeuge:** `positionsgroesse` (Kelly simultan inkl. Gebühr, Volatilitätsziel), `wetter` (82 Ensemble-Mitglieder gegen Kalshi-Temperaturmärkte), `derivate_lage` (DVOL, Funding exakt, Basis), `orderfluss`; dazu Fed-, EZB- und SEC-Presse und FOMC-Termine.
- **Lernschleife:** Haiku schreibt bei jeder Abrechnung eine Lektion. Das Notizbuch wählt Einträge nach Wichtigkeit und Alter aus. Das **Policy-Gate** sperrt Kategorien mit mindestens 5 Verlust-Trades; nur das Review darf sie wieder lockern. Ab 15 Auflösungen gibt es eine Kalibrier-Rückmeldung.
- **Risiko:** Krypto- und Themen-Cluster-Limits werden hart in der Börse geprüft.

**Neue Fonds (ohne LLM, außer dem A/B-Fonds)**
- **Schwarm:** alle KI-Fonds, nur Claude oder nur Liga. Mischt die Schätzungen mit dem Marktpreis und kauft mit ¼-Kelly.
- **Kontrollen:** „Markt-Kopierer“ (Null-Linie) und „Immer NEIN“ (misst den Ja-Hang).
- **Regelfonds Wetter-Ensemble.** Im Test hat er sofort zwei Käufe mit klarem Ensemble-Vorteil gemacht.
- **A/B-Fonds „Claude Mittel+RM“:** Zwilling von Mittel, aber mit Haiku-Risikomanager vor großen Orders.

**Börse und Statistik**
- **Buchtiefe:** Wer im selben Lauf später ordert, bekommt nur noch das, was frühere Orders im Buch übrig gelassen haben.
- **Marktimpact:** Ausgelöste Stops und das synthetische Aktienbuch tragen einen Aufschlag nach dem Square-Root-Gesetz.
- **Rangliste:** Bootstrap-Konfidenzintervalle, Deflated Sharpe, „messbar ab Tag X“, p-Wert gegen BTC.
- **Prognosen:** Brier-Skill gegen den Marktpreis.
- **Nachfolge am 14.11.:** Model Confidence Set statt Rangplatz; gewählt wird das günstigste Modell unter den nicht unterscheidbaren Besten, und die Wahl bleibt 7 Tage stabil.

**Seite:** neue Abschnitte „Prognosegüte – besser als der Marktpreis?“ (mit Kalibrierungsdiagramm) und „Schwarm & Kontrollen“, die Rangliste mit
Konfidenzspannen, Gleichlauf, Gewinn je API-€, ein A/B-Kasten und eine Vorschau der Nachfolge. Headless geprüft (1440 px und 390 px): keine Konsolenfehler, kein horizontales Scrollen.

**Live geprüft:** Die feste Runde um 18 UTC lief mit dem neuen Code für alle vier Claude-Fonds fehlerfrei. Die Pflichtfelder stehen in den echten Entscheidungen, und Wetter-Regelfonds, Schwarm und Kontrollen handeln bereits.

**Budget:** Heute bis 16 UTC ≈ 5,4 €; hochgerechnet wären das mit drei Fonds ≈ 7,5 €/Tag. Der vierte (A/B-)Fonds bringt die Ausgaben ins Ziel von 8–11 €. Die Tagesanteile
betragen 4 × 2,75 € plus 0,8 € Reserve, der harte Deckel von 12 €/Tag bleibt.

## Was Rouven tun muss / kann

1. **Nichts Pflichtiges.** Der Dauerlauf zieht den neuen Code bei jedem Tick (`git pull`). Der A/B-Fonds und die Regelfonds legen sich beim nächsten Wächter-Lauf selbst an.
2. **Weiterhin offen von gestern:** Kachel-PR im Repo windows-dashboard mergen, OpenAI-Guthaben (optional) und die Secrets `CEREBRAS_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`.
3. **Optional, neu:** das Secret `FRED_API_KEY` (gratis); dann erscheinen die US-Veröffentlichungstermine (CPI, Arbeitsmarkt …) im Werkzeug `makro`. Die Workflow-Zeile ist schon da.
4. **Entscheidungen, die Konten oder eine ToS-Prüfung brauchen** (vorbereitet in [research/VORBEREITUNG-HEBEL-2-5-10.md](research/VORBEREITUNG-HEBEL-2-5-10.md)):
   - Metaculus-Bot-Konto (Hebel 2)
   - Hyperliquid-Nutzungsbedingungen im Browser prüfen (Hebel 5)
   - Alpaca/Finnhub (gratis) und für SEC EDGAR eine öffentliche Kontaktadresse (Hebel 10)
   - OpenRouter einmalig 10 $ aufladen (1000 statt 50 Gratis-Anfragen/Tag)
5. Falls „Stand vor …“ auf der Seite älter als 1 h ist: *Actions → Dauerlauf → Run workflow*.

## Offen / zu beobachten

- **Tageskosten** mit vier Claude-Fonds am 31.10. prüfen (Ziel 8–11 €). Liegen sie zu hoch, `fonds_tagesanteil_eur` senken; der Deckel greift ohnehin.
- **Prognose-Kennzahlen füllen sich erst mit Abrechnungen:** 175 Schätzungen warten derzeit. Ab etwa 5 bewerteten Schätzungen erscheinen Kalibrierung und Skill gegen den Markt, die Rangliste-KIs ab 24 h Verlauf.
- **Wetter-Regelfonds:** Der Modellfehler σ = 1,5 + 0,4·Vorlauf °F ist eine konservative Annahme. Nach etwa 50 abgerechneten Brackets aus der Trefferbilanz nachkalibrieren.
- **Kimi** wählte einen gelisteten, aber gesperrten Modellnamen. Jetzt werden bei 404 bis zu vier Kandidaten probiert – Status nach dem nächsten Liga-Lauf (21 UTC) prüfen. Bleibt es rot, hat der Schlüssel vermutlich keinen Zugriff auf Chat-Modelle (Moonshot-Konto prüfen).
- **Risikomanager-Schwelle** (5 % des Kapitals) beobachten: Zu viele Ablehnungen verfälschen den A/B-Vergleich nicht, machen ihn aber teurer.
- **Wächter-Laufzeit** liegt mit den neuen Fonds bei ≈ 110–130 s (Wetter stündlich +≈ 20 s), die Grenze ist 600 s.
- **Polymarket-Temperaturmärkte** sind bewusst nicht im Wetter-Werkzeug (andere Station, freie Formulierungen).
- `scripts/dauerlauf.sh` wurde nicht geändert (ein Lauf ist aktiv).

## Bekannte Grenzen (ehrlich)

- **Aktien:** Yahoo drosselt Cloud-IPs teilweise; Stooq ist nicht nutzbar. Das Aktienbuch ist synthetisch (jetzt mit Impact-Treppe).
- **PredictIt** nur Top-of-Book (synthetische Tiefe); **Manifold** ist Spielgeld.
- **Perps:** linear mit isolierter Marge; **Optionen** nur gekauft.
- **Kelly simultan** nimmt unabhängige Ausgänge an, ist also eine Obergrenze. Die Themen-Etiketten stammen aus einer Stichwortliste.
- **Stichprobe:** Die Konfidenzintervalle zeigen ehrlich, dass Rangplätze in den ersten Wochen Rauschen sind.
- **Repo-Wachstum:** Kursverlauf und Equity wachsen um ≈ 100–200 kB/Tag; dazu kommen die neuen Prognose- und Wetter-Protokolle (klein).
