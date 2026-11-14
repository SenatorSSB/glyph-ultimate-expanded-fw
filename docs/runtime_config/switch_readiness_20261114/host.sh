#!/bin/bash
set -eu
repo=/private/tmp/glyph-switch-live-review
cd "$repo"
py='/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/.venv/bin/python'
corpus=/private/tmp/productization-20261113-senscope/contracts/glyph-package-v1
export PYTHONDONTWRITEBYTECODE=1
export PLATFORMIO_CORE_DIR=/private/tmp/productization-combined-pio
set -x
dir=tools/fixtures/glyph_package_v1/transaction
dest=/private/tmp/glyph-switch-checks/host
mkdir -p "$dest"
"$py" "$dir/build.py" --repo . --boot-probe --out "$dest/build"
binary="$dest/build/package-fault-harness"
"$py" "$dir/lifecycle_regressions.py" --corpus "$corpus" --binary "$binary" --out "$dest/lifecycle"
"$py" "$dir/managed_selection.py" --corpus "$corpus" --binary "$binary" --out "$dest/selection"
export PYTHONPATH=/private/tmp/glyph-startup-protobuf GLYPH_PACKAGE_REPO=/private/tmp/productization-20261113-senscope GLYPH_PACKAGE_CORPUS="$corpus"
"$py" "$dir/startup_work.py" --corpus "$corpus" --binary "$binary"
"$py" "$dir/boot_regressions.py" --corpus "$corpus" --binary "$binary" --require-visible --out "$dest/boot"
"$py" "$dir/regressions.py" --repo "$repo" --corpus "$corpus" --binary "$binary" --out "$dest/transactions"

for name in historical_config_regressions storage_fence_regressions; do
  "$py" "$dir/$name.py" --corpus "$corpus" --binary "$binary" --out "$dest/$name"
done
