# Glyph Native Ultimate Tilt Patch Constraints (2026-05-24)

## Purpose

Define guardrails for a later minimal native `MODE_ULTIMATE` Tilt/Tilt2 runtime branch.

This is a constraints document only. It does not add runtime behavior.

## 1) Allowed later runtime scope

- Exactly one implementation branch for runtime experimentation.
- Native `MODE_ULTIMATE` scope only, and only if explicitly approved.
- One or two custom modifier outputs only (narrowly scoped).
- No broad firmware refactor.

## 2) Required explicit inputs before runtime patch

- Final Tilt1/Tilt2 numeric values must be provided/approved.
- Activation button or chord mapping must be provided/approved.
  - Current uploaded MVP layout confirmation: Tilt1 / TILT is physical `BTN_RF3` -> logical `BTN_LT1` -> future runtime `inputs.lt1`.
  - Current uploaded MVP layout confirmation: Tilt2 is physical `BTN_RF4` -> logical `BTN_LT2` -> future runtime `inputs.lt2`.
  - Future runtime should use post-remap logical inputs, not raw physical `RF3`/`RF4` bypass semantics.
- Explicit decision whether Tilt/Tilt2 targets left stick only.
- Explicit decision whether behavior must preserve existing C-stick/right-stick/trigger behavior unchanged.

## 3) Required non-goals

- No macros.
- No turbo behavior.
- No timing automation.
- No SOCD behavior changes.
- No remap semantic changes.
- No profile/schema changes unless separately approved.
- No dependency on flipper or overflow behavior unless source-proven first.

## 4) Verification expectations

- Capture static scanner snapshot before and after runtime patch (`tools/list_glyph_native_ultimate_analog_sources.py`).
- Perform targeted source diff review for `MODE_ULTIMATE` runtime changes.
- Confirm build passes.
- Require owner-reviewed hardware smoke-test protocol before any manual flash.

## Source notes

- Current native Ultimate analog shaping and override order are in `src/modes/Ultimate.cpp`.
- Input pipeline order (`HandleRemap` -> `HandleSocd` -> analog update) is in `src/core/ControllerMode.cpp`.
- Ultimate default SOCD/remap config is in `config/glyph/common/include/glyph_overrides.hpp`.
- Output analog field types (`uint8_t`) are in `include/core/state.hpp`.
