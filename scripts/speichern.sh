#!/usr/bin/env bash
# Committet Zustand (data/, docs/, reports/) und pusht auf main. Wiederholt bei Konflikten (Rebase), nie Force-Push.
set -u
nachricht="${1:-Zustand aktualisiert}"
git config user.name "arena-bot"
git config user.email "arena-bot@users.noreply.github.com"
git add data docs reports 2>/dev/null || true
if git diff --cached --quiet; then
  echo "Nichts zu speichern."
  exit 0
fi
git commit -q -m "$nachricht"
for i in 1 2 3 4 5; do
  if git pull -q --rebase origin main && git push -q origin HEAD:main; then
    echo "Gespeichert."
    exit 0
  fi
  echo "Push fehlgeschlagen (Versuch $i), neuer Versuch …"
  git rebase --abort 2>/dev/null || true
  sleep $((i * 3))
done
echo "WARNUNG: Speichern fehlgeschlagen (wird beim nächsten Lauf nachgeholt)."
exit 0
