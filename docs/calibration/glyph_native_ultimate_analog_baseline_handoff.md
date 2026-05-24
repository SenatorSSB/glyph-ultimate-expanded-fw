# Glyph Native Ultimate Analog Baseline Handoff

## Branch

- `glyph/ultimate-analog-baseline-snapshot`

## Files added/changed

- `docs/calibration/glyph_native_ultimate_analog_baseline_2026-05-24.md` (new)
- `docs/calibration/glyph_native_ultimate_tilt_patch_constraints_2026-05-24.md` (new)
- `docs/calibration/fixtures/native_ultimate_analog_static_snapshot.txt` (new generated fixture)
- `docs/calibration/glyph_native_ultimate_analog_baseline_handoff.md` (new)
- `tools/list_glyph_native_ultimate_analog_sources.py` (new read-only scanner)
- `tools/check_glyph_native_ultimate_snapshot.py` (new read-only snapshot checker)

## Behavior-change confirmations

- Runtime firmware behavior changed: **No**
- Device behavior changed: **No**
- Flashing/push-to-device behavior added: **No**
- SOCD behavior changed: **No**
- Remapping semantics changed: **No**
- Final Tilt1/Tilt2 values selected: **No**
- Tilt/Tilt2 runtime implementation added: **No**
- Scanner script added: **Yes**
- Static snapshot fixture added: **Yes**
- Snapshot check helper added/deferred: **Added** (`tools/check_glyph_native_ultimate_snapshot.py`)

## Tests/checks run

- `.venv/bin/python tools/check_glyph_calibration_fixtures.py` -> pass
- `.venv/bin/python tools/check_glyph_patch_script.py` -> pass
- `.venv/bin/python tools/list_glyph_modifier_symbols.py` -> pass
- `.venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py` -> pass
- `.venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py` -> pass
- `.venv/bin/python tools/check_glyph_native_ultimate_snapshot.py` -> pass
- `grep -R "<<<<<<<\|=======\|>>>>>>>" docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true` -> no conflicts found
- `find . -name .DS_Store -print` -> none found
- `./scripts/build-glyph-mk6-quiet.sh` -> pass (`glyph_mk6 SUCCESS`)

## Remaining blockers before runtime patch

- Final Tilt1/Tilt2 values are still not selected.
- Activation mapping/chord for Tilt/Tilt2 is not yet approved.
- Output target scope (left-stick only vs. other outputs) is not yet approved.
- C-stick/right-stick/trigger preservation constraints for runtime patch are not yet explicitly approved.
- Any overflow/clamp/flipper-dependent behavior remains blocked unless source-proven or explicitly avoided.
- Owner-reviewed hardware smoke-test protocol is still required before any manual flash.
