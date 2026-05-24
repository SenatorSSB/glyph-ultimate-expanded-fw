# Glyph Config Parser and Firmware Trace Handoff

## Branch
- `glyph/ultimate-config-parser-and-firmware-trace`

## Files added/changed
- Added:
  - `docs/calibration/glyph_config_parser_and_firmware_trace_inventory.md`
  - `docs/calibration/glyph_firmware_enum_trace_2026-05-24.md`
  - `docs/calibration/glyph_initial_firmware_test_readiness_2026-05-24.md`
  - `docs/calibration/fixtures/example_ultimate_patch.json`
  - `tools/glyph_config_model.py`
  - `tools/patch_glyph_ultimate_profile.py`
  - `tools/check_glyph_patch_script.py`
  - `tools/list_glyph_button_symbols.py`
- Changed:
  - `tools/check_glyph_calibration_fixtures.py` (refactored to use parser model and expanded required checks)

## Parser/check scripts added
- `tools/glyph_config_model.py`
- `tools/patch_glyph_ultimate_profile.py`
- `tools/check_glyph_patch_script.py`
- `tools/list_glyph_button_symbols.py`
- Updated `tools/check_glyph_calibration_fixtures.py`

## Fixtures used
- `docs/calibration/fixtures/GlyphUserProfilesUlt-filled.json`
- `docs/calibration/fixtures/GlyphUltFilled2.json`
- `docs/calibration/fixtures/example_ultimate_patch.json`

## Source enum trace result
- Enum/schema definitions for buttons, modes, layout plates, SOCD types, and remap/socd config messages were found in:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
- Tracked source usages were confirmed in:
  - `config/glyph/common/include/glyph_overrides.hpp`
  - `include/core/config_utils.hpp`
  - `src/core/mode_selection.cpp`
- Detailed trace: `docs/calibration/glyph_firmware_enum_trace_2026-05-24.md`

## Firmware enum definitions found?
- Yes, in dependency proto source under `.pio/libdeps/...`.
- Note: canonical tracked enum definition source under repo-owned top-level source paths remains to be pinned/documented.

## Patch prototype added?
- Yes:
  - `tools/patch_glyph_ultimate_profile.py`
  - `docs/calibration/fixtures/example_ultimate_patch.json`
  - `tools/check_glyph_patch_script.py`
- Scope: config JSON patching only; no firmware runtime mutation.

## Firmware/device behavior changes
- Firmware behavior changed: **No**.
- Device behavior changed: **No**.
- Flashing / push-to-device behavior added: **No**.

## Boundary confirmations
- Omitted `activates` remain preserved/uninterpreted: **Yes**.
- SOCD pairs remain profile-specific config: **Yes**.
- Exact visual pixel mapping remains out of scope: **Yes**.

## Tests/checks run
- `.venv/bin/python tools/check_glyph_calibration_fixtures.py` (pass)
- `.venv/bin/python tools/check_glyph_patch_script.py` (pass)
- `.venv/bin/python tools/patch_glyph_ultimate_profile.py --input docs/calibration/fixtures/GlyphUltFilled2.json --patch docs/calibration/fixtures/example_ultimate_patch.json --output /tmp/GlyphUltPatched.json` (pass)
- `.venv/bin/python tools/list_glyph_button_symbols.py` (pass)
- `./scripts/build-glyph-mk6-quiet.sh` (pass)

## Remaining requirements before firmware behavior edits
- Pin and document canonical tracked enum/schema source authority.
- Confirm modifier-value behavior details for targeted firmware test scope.
- Finalize hardware smoke-test protocol for first firmware test run.
