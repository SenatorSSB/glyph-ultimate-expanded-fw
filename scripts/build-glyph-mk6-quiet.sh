#!/usr/bin/env bash
set -euo pipefail

LOG="${TMPDIR:-/tmp}/glyph_mk6_build.log"

if ! ./scripts/pio-local.sh run -e glyph_mk6 > "$LOG" 2>&1; then
  echo "glyph_mk6 build failed. Last 80 log lines:"
  tail -n 80 "$LOG"
  exit 1
fi

echo "glyph_mk6 build passed"
grep -E "SUCCESS|FAILED|RAM:|Flash:" "$LOG" | tail -n 20 || true
echo "Full log: $LOG"
