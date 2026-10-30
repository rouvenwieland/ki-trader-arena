#!/usr/bin/env bash
# Rückfall-Workflows (Wächter/Entscheider/Review einzeln) arbeiten nur, wenn kein Dauerlauf aktiv ist –
# sonst schriebe zweimal jemand gleichzeitig in data/. Ausgabe: aktiv=true|false nach $GITHUB_OUTPUT.
set -u
n=$(gh run list --workflow dauerlauf.yml --status in_progress --json databaseId -q 'length' 2>/dev/null || echo 0)
aktiv=false; [ "${n:-0}" != "0" ] && aktiv=true
echo "aktiv=$aktiv" >> "${GITHUB_OUTPUT:-/dev/null}"
echo "Dauerlauf aktiv: $aktiv"
