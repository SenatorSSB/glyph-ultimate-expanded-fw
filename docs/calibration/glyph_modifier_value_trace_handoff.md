# Glyph Modifier Value Trace Handoff

## Branch

- `glyph/ultimate-modifier-value-trace`

## Files Added/Changed

- Added `docs/calibration/glyph_proto_source_authority_2026-05-24.md`
- Added `docs/calibration/glyph_modifier_value_trace_2026-05-24.md`
- Added `docs/calibration/glyph_tilt_modifier_firmware_test_readiness_2026-05-24.md`
- Added `docs/calibration/glyph_modifier_value_trace_handoff.md`
- Added `tools/list_glyph_modifier_symbols.py`

## Findings

- Proto source authority: dependency-pinned for Glyph env through `config/glyph/env.ini` to `https://github.com/GregTurbo/HayBox-proto#db4e2f6`; not repo-tracked as a first-party `config.proto`; local `.pio` cache confirms full commit `db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8`.
- Modifier schema definitions found: yes, in `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` and generated local `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`.
- Runtime modifier application path found: yes, for `MODE_CUSTOM` / `CustomControllerMode` in `src/core/mode_selection.cpp`, `src/modes/CustomControllerMode.cpp`, and `HAL/pico/include/util/state_util.hpp`.
- Native Ultimate analog implementation path found: yes, in `src/modes/Ultimate.cpp`.
- Overflow behavior found: no explicit clamp/overflow behavior was source-confirmed for `CustomControllerMode` modifier math.
- Flipper behavior found: no.
- Tilt/Tilt2 implementation location known: candidate locations are known, but final implementation location is not approved or selected.
- Parser/helper script added: yes, `tools/list_glyph_modifier_symbols.py`.
- Parser extension added: no; tracked JSON fixtures do not contain custom modifier/custom-mode arrays to model or regression-check.
- Firmware behavior changed: no.
- Device behavior changed: no.
- Flashing/push-to-device behavior added: no.
- SOCD behavior changed: no.
- Button remapping semantics changed: no.
- Tilt/Tilt2 runtime implementation added: no.

## Tests/Checks Run

- `.venv/bin/python tools/check_glyph_calibration_fixtures.py`: passed.
- `.venv/bin/python tools/check_glyph_patch_script.py`: passed.
- `.venv/bin/python tools/list_glyph_modifier_symbols.py`: passed; `scanned_files=15`.
- Requested broad conflict/artifact grep was run and produced false positives from local PlatformIO cache separator lines under `.`. A targeted conflict marker scan over tracked source/doc/tool paths produced no merge markers.
- `find . -name .DS_Store -print`: no output.
- `find . -path "*/.venv/*" -print | head`: confirmed local `.venv` exists; `.venv` is not staged/committed.
- `./scripts/build-glyph-mk6-quiet.sh`: passed; `glyph_mk6 SUCCESS`.

## Remaining Blockers Before Firmware Runtime Patch

- Pin/review proto source authority before runtime/schema-sensitive changes.
- Confirm or design clamp/overflow behavior with source/test evidence.
- Confirm or design flipper behavior with source/test evidence.
- Select final Tilt1/Tilt2 values only with explicit source/domain confirmation.
- Decide whether implementation belongs in native `MODE_ULTIMATE`, `MODE_CUSTOM`, or another reviewed path.
- Define human-controlled compile and hardware smoke-test procedure before flashing.
