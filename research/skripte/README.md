# Test- und Auswerteskripte der Recherche (30.10.2026)

Nur zur Nachvollziehbarkeit der Angaben „getestet“ in [../RECHERCHE-2026-10.md](../RECHERCHE-2026-10.md). **Kein Teil der Arena**, werden von keinem Workflow und nicht von pytest benutzt (pytest sammelt nur `tests/`). Jeweils in einer eigenen venv ausgeführt, ohne Schlüssel.

| Datei | Zweck |
|---|---|
| `run_model.py` | Quantilprognosen eines Zeitreihenmodells an 50 rollenden Ursprüngen (BTC-USD-Stundenkerzen von Coinbase, öffentlich). |
| `bewerte.py` | Pinball-Loss, MAE, Abdeckung 10–90 %, Richtungstreffer, t-Wert gegen Random Walk → `tabelle.md`. |
| `kronos_seq.py` | Gegenprobe Kronos-small exakt wie `scripts/prognosen.py` (8 Einzelpfade); erwartet `KRONOS_DIR` (Klon von shiyu-coder/Kronos). |
| `mess.py` | Misst Laufzeit und Spitzen-RAM eines Unterprozesses. |
| `tabelle.md` | Ergebnis des Modellvergleichs (n = 50, vorsichtig interpretieren; TTM-r2 liefert nur Punktprognosen, daher 0 % Abdeckung). |
| `eval_test.py` | Ehrliche Kennzahlen auf synthetischen Daten: PSR/DSR, MinTRL, Bootstrap-KI, Brier-Skill gegen Markt. |
| `test_recal.py` | Rekalibrierung (Platt) mit `Metaculus/forecasting-tools` an einem simulierten überkonfidenten Agenten; erwartet Pfad zum Klon als Argument. |
| `test_edge.py` | „Edge gegen Marktpreis“-Auswertung aus `ryanfrigo/kalshi-ai-trading-bot` (MIT) an einem simulierten Agenten; erwartet Pfad zum Klon als Argument. |
