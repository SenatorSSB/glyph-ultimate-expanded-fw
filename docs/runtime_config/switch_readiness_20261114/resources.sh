#!/bin/bash
set -eu
set -x
repo=/private/tmp/glyph-switch-live-review
checks=/private/tmp/glyph-switch-checks
source_sha=$(git -C "$repo" rev-parse HEAD)
out="$checks/$source_sha"
elf="$repo/.pio/build/glyph_mk6/firmware.elf"
mkdir -p "$out"
cp "$elf" "$out/firmware.elf"
python3 "$checks/replay-display-stack.py" --glyph "$repo" --elf "$out/firmware.elf" --platformio /private/tmp/productization-combined-pio --out "$out/graph"
python3 /private/tmp/productization-hardware-handoff/docs/runtime_config/productization_20261113/resources/compose.py --resource "$out/graph" --baseline-archive /private/tmp/productization-20261113-senscope/docs/project/goal-runs/exact-legacy-migration-proof-diagnosis/evidence/target-and-resource-evidence.tar.gz --output "$out/core0.json"
python3 "$checks/compare.py" /private/tmp/productization-hardware-handoff/docs/runtime_config/productization_20261113/candidates/combined "$out/graph" "$out/compare.json"
