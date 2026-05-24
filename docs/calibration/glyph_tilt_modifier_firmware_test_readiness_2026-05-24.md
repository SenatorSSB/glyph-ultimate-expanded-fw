# Glyph Tilt Modifier Firmware Test Readiness - 2026-05-24

## Purpose

Document the minimum evidence required before implementing custom Ultimate modifiers named `TILT` and `Tilt2`. This branch is readiness assessment only. It does not add runtime firmware behavior and does not push anything to hardware.

## Known Now

- Read-only config parser tooling exists in `tools/glyph_config_model.py`.
- Firmware enum trace documentation exists in `docs/calibration/glyph_firmware_enum_trace_2026-05-24.md`.
- Calibration fixtures exist under `docs/calibration/fixtures/`.
- Profile patch prototype tooling exists in `tools/patch_glyph_ultimate_profile.py`.
- Patch/check tooling exists in `tools/check_glyph_calibration_fixtures.py` and `tools/check_glyph_patch_script.py`.
- The prior merged baseline reported a successful local `glyph_mk6` build with `./scripts/build-glyph-mk6-quiet.sh`.

## Source-Grounded Modifier Facts From This Branch

- Active Glyph proto source is dependency-provided through PlatformIO, with Glyph env override `https://github.com/GregTurbo/HayBox-proto#db4e2f6`.
- Active local proto cache includes `AnalogModifier`, `AnalogTriggerMapping`, `CustomModeConfig`, `AnalogAxis`, `StickDirectionButton`, and `ModifierCombinationMode`.
- `AnalogModifier` contains `buttons`, one `axis`, `multiplier`, and `combination_mode`.
- `CustomModeConfig` contains `digital_button_mappings`, `stick_direction_mappings`, `analog_trigger_mappings`, `modifiers`, `stick_range`, and `button_combo_mappings`.
- Runtime application path for schema-backed custom modifiers was found in `src/modes/CustomControllerMode.cpp`.
- `axis_pointer` in `HAL/pico/include/util/state_util.hpp` maps modifier axes to `OutputState` left-stick, right-stick, and trigger analog fields.
- Native Ultimate hard-coded analog logic was found in `src/modes/Ultimate.cpp`, including source comments for tilt-like values.
- Explicit clamp behavior for `CustomControllerMode` modifier math was not found.
- Explicit overflow/wrap behavior for modifier math was not found.
- Flipper behavior or a `flipper` field was not found.
- Candidate implementation files are known only as candidates:
  - `src/modes/CustomControllerMode.cpp` for schema-backed custom mode modifiers.
  - `src/modes/Ultimate.cpp` for native Ultimate hard-coded behavior.

## Not Ready / Blockers

- Final Tilt1/Tilt2 values are not selected in this branch.
- Overflow behavior must be source-confirmed before any flipper or overflow-dependent modifier implementation.
- Flipper behavior must be source-confirmed or explicitly designed before implementation.
- Hardware smoke-test procedure must exist before flashing.
- Proto/source authority should be pinned and documented before runtime changes because active schema is dependency/cache-based rather than repo-tracked.
- No tracked JSON fixtures currently contain custom modifier/custom-mode arrays, so parser extension for raw modifier sections is deferred.
- Interaction with SOCD and remaps must remain explicitly bounded before any runtime patch.

## Minimum Safe Runtime Patch Scope Later

- One reviewed branch.
- One or two custom Ultimate modifier definitions only.
- No broad refactor.
- No SOCD changes unless explicitly requested.
- No button remapping semantic changes unless explicitly requested.
- No macros, turbo behavior, or timing automation.
- Compile before hardware test.
- Manual smoke test before any broader use.
- Hardware flashing only through an explicit human-controlled procedure.

## Stop Conditions Before Runtime Patch

- Unknown modifier value schema.
- Unknown clamp/overflow behavior.
- Unclear flipper behavior.
- Unclear interaction with SOCD/remaps.
- Any requirement for timing automation.
- Any requirement to choose final Tilt1/Tilt2 values without explicit source/domain confirmation.
- Any requirement to add push-to-device/flashing behavior in code.

