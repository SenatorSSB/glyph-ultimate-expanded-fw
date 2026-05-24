#!/usr/bin/env bash
set -euo pipefail

LOG="${TMPDIR:-/tmp}/glyph_mk6_senscope_playtest_build.log"

if ! ./scripts/pio-local.sh run -e glyph_mk6_senscope_playtest > "$LOG" 2>&1; then
  echo "glyph_mk6_senscope_playtest build failed. Last 80 log lines:"
  tail -n 80 "$LOG"
  exit 1
fi

echo "glyph_mk6_senscope_playtest build passed"
grep -E "SUCCESS|FAILED|RAM:|Flash:" "$LOG" | tail -n 20 || true
echo "Full log: $LOG"
