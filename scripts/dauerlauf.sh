#!/usr/bin/env bash
# Dauerlauf: ein Job erledigt alles nacheinander – Wächter-Tick alle 15 min, Entscheider (fest/Ereignis/Tiefenrunde),
# Wochen-Review, Seiten-Deploy, Prognosen anstoßen. Nacheinander heißt: keine zwei Schreiber auf data/, keine Konflikte.
# Der Nachfolger wird gleich zu Beginn in dieselbe Concurrency-Gruppe eingereiht und startet, sobald dieser Lauf endet
# (normal oder durch Zeitlimit). GitHub-Jobs dürfen höchstens 6 h laufen.
set -u
LAUFZEIT="${LAUFZEIT:-18900}"     # 5 h 15 min
TAKT="${TAKT:-900}"               # 15 min
start=$(date +%s); ende=$((start + LAUFZEIT))
rest() { echo $((ende - $(date +%s))); }
seite() { gh workflow run seite.yml >/dev/null 2>&1 || echo "Seiten-Deploy nicht anstoßbar"; }
holen() { git pull -q --rebase origin main || { git rebase --abort 2>/dev/null; echo "WARNUNG: pull fehlgeschlagen"; }; }

while [ "$(rest)" -gt 300 ]; do
  tick=$(date +%s)
  holen
  export GITHUB_OUTPUT; GITHUB_OUTPUT=$(mktemp)
  timeout 600 uv run python -m arena.watcher || echo "WARNUNG: Wächter-Tick abgebrochen"
  ausloesen=$(grep -q '^ausloesen=true' "$GITHUB_OUTPUT" && echo ausloesen || true)
  timeout 120 uv run python -m arena.site || echo "Seitenbau fehlgeschlagen (nicht kritisch)"
  bash scripts/speichern.sh "Wächter $(date -u +%Y-%m-%dT%H:%MZ)"
  seite
  for aufgabe in $(uv run python -m arena.takt $ausloesen); do
    case "$aufgabe" in
      taeglich|takt|ereignis)
        if [ "$(rest)" -lt 2400 ]; then echo "Zu wenig Restzeit für $aufgabe – der Nachfolger holt es nach"; continue; fi
        echo "::group::Entscheider ($aufgabe)"
        timeout 2100 uv run python -m arena.entscheider "$aufgabe" || echo "WARNUNG: Entscheider abgebrochen"
        timeout 120 uv run python -m arena.site || true
        bash scripts/speichern.sh "Entscheider ($aufgabe) $(date -u +%Y-%m-%dT%H:%MZ)"
        seite
        echo "::endgroup::";;
      review)
        timeout 1200 uv run python -m arena.review || echo "WARNUNG: Review abgebrochen"
        bash scripts/speichern.sh "Wochen-Review $(date -u +%Y-%m-%d)"
        seite;;
      prognosen)
        gh workflow run prognosen.yml >/dev/null 2>&1 || echo "Prognosen nicht anstoßbar";;
    esac
  done
  bash scripts/speichern.sh "Takt $(date -u +%Y-%m-%dT%H:%MZ)"   # takt_zustand.json
  warten=$((TAKT - ($(date +%s) - tick)))
  [ "$warten" -gt "$(( $(rest) - 300 ))" ] && break
  [ "$warten" -gt 0 ] && sleep "$warten"
done
echo "Dauerlauf endet planmäßig; der eingereihte Nachfolger übernimmt."
