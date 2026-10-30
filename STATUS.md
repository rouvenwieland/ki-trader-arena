# STATUS (Stand 30.10.2026, Tagschicht)

Live: **https://rouvenwieland.github.io/ki-trader-arena/** · `status.json` für die Laptop-Kachel · Entscheidungen mit Begründung in [DECISIONS.md](DECISIONS.md)

## Heute erledigt

**Betrieb (wichtigster Fund):** GitHub-Cron hat den 15-Minuten-Wächter zwischen 00:53 und 10:00 UTC nur **einmal** gestartet; die Arena stand also praktisch still. Neu ist der **Dauerlauf** (`dauerlauf.yml` + `scripts/dauerlauf.sh` + `arena/takt.py`). Ein Job läuft 5¼ h. In dieser Zeit macht er alle 15 min einen Wächter-Tick, erledigt danach im selben Job die fälligen Entscheider-Runden, das Wochen-Review und den Seiten-Deploy und stößt alle 6 h die Prognosen an. Seinen Nachfolger reiht er gleich zu Beginn ein; als Rückfallebene gibt es einen stündlichen Cron. Die alten Workflows bleiben für Handstarts und tun nichts, solange der Dauerlauf läuft. Live geprüft: Tick 10:08, feste Runde 10:09, Prognosen 10:12 und Seiten-Deploy liefen, der Nachfolger steht in der Warteschlange.

**1. Budget ausreizen.** Feste Sonnet-Runden um 0, 3, 6, 9, 15, 18 und 21 UTC, dazu um 13 UTC (14 Uhr) eine **Opus-5.5-Tiefenrunde** für jeden Claude-Fonds sowie Ereignisrunden nach einer Vorsichtung durch Haiku. Die Runden sind tiefer: 20 bzw. 26 Schritte, 8 bzw. 12 Websuchen und ein Rundenauftrag (mindestens fünf neue Kandidaten im eigenen Schwerpunkt und vier Recherchen; ob gehandelt wird, entscheidet der Fonds weiterhin selbst).
- Tagesanteile 3,3/3,4/3,5 € plus 0,8 € Reserve ergeben ein Ziel von ≈ 10 €/Tag; der **harte Deckel von 12 €/Tag** bleibt.
- Das Rundenbudget verteilt den Rest des Tagesanteils. Wird es knapp, bekommt der Agent einen Hinweis, jetzt zu entscheiden, statt hart abgebrochen zu werden.
- Ein Tempo-Faktor sorgt dafür, dass die 190 € sicher bis zum 14.11. reichen.
- Kosten je Fonds und je Modell stehen auf der Seite, in `status.json` und in `budget_status.json`.
- Erster Live-Lauf (Sonnet, 4-h-Takt): 0,14–0,26 $ je Fonds und Runde. Deshalb gilt jetzt der 3-h-Takt mit Rundenauftrag.

**2. Klumpenrisiko.** Jeder Claude-Fonds hat jetzt einen eigenen **Schwerpunkt** mit eigenem **Recherchepfad** und eine eigene **Startliste** der Wettmärkte; die Fonds sehen einander nicht (per Test abgesichert):
- Vorsichtig: Makro, Zinsen, Wetter, Anleihen
- Mittel: Unternehmen, Tech, Sport, Wahlen, Einzelaktien
- Aggressiv: Krypto, Perps, Optionen

Neue Kennzahl **Überlappung** (auf der Seite und in `status.json`); Startwert 100 %. Schon in der ersten Runde danach hat *Mittel* die gemeinsame Iran-Wette verkauft und *Aggressiv* eine BTC-Schwellenwette gekauft.

**3. Liga-Fehler.**
- OpenAI: „no credits“ wird erkannt; der Fonds steht dann auf **„pausiert (kein Guthaben)“** und wird täglich neu probiert.
- Gemini 503: Wiederholung mit Backoff, danach Ausweichmodell `gemini-2.5-flash`.
- Modellnamen: Ausweichlisten je Anbieter; ein automatisch aufgelöster Name wird gemerkt.
- OpenRouter: die gewählten Gratismodelle bleiben stabil, und vor der Auswahl gibt es einen Probeaufruf. Live gefunden: Manche gelisteten `:free`-Modelle sind gesperrt.
- Der Liga-Pfad wurde live gegen ein OpenRouter-Gratismodell getestet: Runde mit Order und Tagebuch.
- Cerebras, Mistral und OpenRouter starten automatisch, sobald ihr Secret existiert.

Hinweis: Die angezeigten Liga-Status (OpenAI-Fehlertext, Gemini „Zeitlimit“) stammen noch von 06:11. Die Liga läuft im neuen Takt erst wieder um 13, 21 und 6 UTC und bei Ereignissen; ab dann gelten die neuen Status.

**4. Laptop-Kachel.** PR https://github.com/rouvenwieland/windows-dashboard/pull/1 (Branch `claude/arena-kachel`, nicht gemergt). Die Kachel zeigt Rangliste, Werte, Mini-Verläufe, API-Kosten, Budgetbalken, Überlappung und Stand. Getestet gegen die echte `status.json`; die Darstellung im Board ist nicht getestet (dafür braucht es Windows).

**5. Seite.** Headless geprüft (Desktop 1440 px, Mobil 390 px): keine Konsolenfehler, kein horizontales Scrollen, Ladezeit ≈ 0,6 s.
- Behoben: Die Fonds-Akte zeigte immer „Kein Fonds“ (JS-Fehler); ein langer Fehlerstatus sprengte die Tabelle; Achsenbeschriftungen überlappten auf dem Handy; die Rangliste war auf dem Handy nicht lesbar; die Daten waren 4 h alt (siehe Betrieb).
- Neu: Laufband mit Rangliste, Orders und Ereignissen im Kopf, Abschnitt „Unabhängigkeit“ (Überlappung je Paar mit gemeinsamen Wetten), Abschnitt „Was kostet das Denken?“ (Budgetbalken mit Ziel und Deckel, Kosten je Fonds und Modell), Status-Punkte und Einblenden beim Scrollen.

**6. Feinschliff.**
- `docs/data.json` liegt nicht mehr im Git (sie hätte ≈ 2 MB/Tag Wachstum bedeutet); die Seite baut sie beim Deploy.
- Zeitlimits je Schritt und Runde im Dauerlauf.
- Agentenschleife: Abschluss bei Schritt-, Zeit- und Budgetgrenze.
- 15 neue Tests (73 insgesamt); README und DECISIONS aktualisiert.

## Was Rouven tun muss / kann

1. **Kachel-PR ansehen und mergen** (windows-dashboard #1). Danach `pwsh werkzeuge\installieren.ps1`, weil `widgets.json` eine neue Widget-Definition bekommt, und im Board „KI-Trader-Arena“ anheften.
2. **OpenAI:** Guthaben aufladen *oder* nichts tun. Der Fonds bleibt dann pausiert und wird täglich neu probiert.
3. **Fehlende Secrets** (die Fonds starten danach von selbst): `CEREBRAS_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`. In der Cloud-Umgebung dieser Session ist ein OpenRouter-Schlüssel gesetzt; als GitHub-Secret fehlt er noch. Setzen per `secrets-setzen.cmd` oder unter *Settings → Secrets → Actions*.
4. Falls die Dauerlauf-Kette einmal reißt (auf der Seite ist „Stand vor …“ > 1 h): *Actions → Dauerlauf → Run workflow*. Der stündliche Cron sollte das aber selbst auffangen.
5. Optional: Alpaca-Gratis-Konto für bessere Aktien-Daten.

## Offen / zu beobachten

- **Tatsächliche Tageskosten** nach dem ersten vollen Tag prüfen (Ziel 8–11 €). Liegen sie darunter, `takt_stunden_utc` verdichten oder die `runden_deckel_usd` in `arena/config.json` anheben; liegen sie darüber, greift der Deckel automatisch.
- **Überlappung** in den nächsten Tagen beobachten: Sinkt sie unter ~30 %, wirken die Schwerpunkte.
- Kimi: `kimi-latest` lieferte einmal 404; die Ausweichliste (`kimi-k2-turbo-preview`, …) ist nicht live geprüft (kein Schlüssel hier).
- Eine zweite Claude-Session arbeitet parallel im Repo (`research/IDEEN-TRESOR.md`); bisher keine Überschneidung.
- `scripts/dauerlauf.sh` möglichst nicht ändern, während ein Lauf aktiv ist (Bash liest Skripte während der Ausführung nach). Neuer Code in `arena/` greift ab dem nächsten Tick, weil jeder Tick `git pull` macht.

## Bekannte Grenzen (ehrlich, unverändert)

- **Aktien:** Yahoo drosselt Cloud-IPs teilweise; Stooq ist nicht nutzbar (Anti-Bot). SPY- und 60/40-Vergleichsfonds starten erst, wenn ein Kurs kommt.
- **PredictIt** nur mit Top-of-Book (synthetische Tiefe); **Manifold** ist Spielgeld (nur Signal).
- **Perps** linear mit isolierter Marge; **Optionen** nur gekauft.
- **Stichprobe:** In den ersten Wochen ist die Rangliste Rauschen.
- **Equity-Kurve:** Neue Orders tauchen bis zum nächsten Tick mit dem Einstandswert auf.
- **Repo-Wachstum:** Kursverlauf und Equity wachsen um grob 100–200 kB/Tag (komprimiert deutlich weniger); `data.json` liegt nicht mehr im Git.
