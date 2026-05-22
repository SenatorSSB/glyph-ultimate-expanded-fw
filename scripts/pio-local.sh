#!/usr/bin/env bash
set -euo pipefail
export PLATFORMIO_CORE_DIR="$PWD/.platformio-home"
if [ -x .venv/bin/python ]; then
  exec .venv/bin/python -m platformio "$@"
fi
if command -v python >/dev/null 2>&1; then
  exec python -m platformio "$@"
fi
exec python3 -m platformio "$@"
