#!/usr/bin/env bash
set -euo pipefail
export PLATFORMIO_CORE_DIR="$PWD/.platformio-home"
python -m platformio "$@"
