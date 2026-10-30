Du baust die KI-Trader-Arena in diesem Repo (rouvenwieland/ki-trader-arena, öffentlich, läuft auf GitHub Actions, Seite: https://rouvenwieland.github.io/ki-trader-arena/) in einem Zug weiter. Rouven ist nicht erreichbar und will nicht gefragt werden: arbeite selbstständig durch, entscheide begründet (DECISIONS.md), bis alles erledigt ist.

Lies zuerst: STATUS.md, DECISIONS.md, PLAN.md und vor allem research/EMPFEHLUNG.md (priorisierte Umsetzungsliste) mit den Details in research/RECHERCHE-2026-10.md. research/IDEEN-TRESOR.md NICHT umsetzen (nur zur Kenntnis).

Auftrag – setze research/EMPFEHLUNG.md um, in dieser Reihenfolge:
1. Abschnitt 0 komplett (B1 Polymarket-Gebühr, B2 Opus-Review Streaming/max_tokens, B3 Kronos-Band, B4 Reddit/Zeitstempel, B5/B6 Preise und Modellnamen).
2. Alle „Top 10 schnelle Gewinne“.
3. Aus „Top 10 große Hebel“ alles, was auf GitHub Actions ohne neue Konten geht: 1 (Schwarm-Meta-Fonds), 3 (Wetter-Werkzeug), 4 (Positionsgrößen/Risikoschicht), 6 (Notizbuch + Policy-Gate), 7 (Börsen-Realismus), 8 (Modellwahl nach dem 14.11. per Model Confidence Set), 9 (A/B-Fonds + Risikomanager-Pass). Hebel 2, 5, 10 nur vorbereiten/dokumentieren, wenn sie Konten oder einen Server brauchen.
4. Seite: neue Kennzahlen (Brier-Skill gegen Markt, Konfidenzintervalle, Kontrollfonds, Schwarm, Kosten je Fonds) hochwertig und verständlich darstellen, Desktop und Handy prüfen (headless Chromium).

Regeln:
- Nur Papierhandel, keine echten Orders, keine Konten anlegen, keine Anlageberatung.
- Niemals Schlüssel ausgeben oder committen (Secrets: ARENA_ANTHROPIC_KEY, GEMINI_API_KEY, DEEPSEEK_API_KEY, MOONSHOT_API_KEY, GROQ_API_KEY, OPENAI_API_KEY; fehlende sauber überspringen).
- Anthropic-API-Budget: Tagesdeckel 12 €, Ziel 8–11 €/Tag bis ca. 14.11., harter Stopp bleibt.
- Direkt auf main pushen ist erlaubt: kleine, getestete Commits auf Deutsch, vor jedem Push `git pull --rebase` (Actions committen laufend Daten), keine Force-Pushes. Tests mit `uv run pytest -q` müssen grün sein; Workflows nach Änderungen einmal per workflow_dispatch prüfen, falls möglich.
- Am Ende STATUS.md aktualisieren (erledigt / offen / was Rouven tun muss) und eine kurze Zusammenfassung in research/UMSETZUNG.md.
