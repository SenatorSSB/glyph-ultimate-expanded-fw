# Glyph Ultimate LT3 Profile Binding (2026-05-27)

## Scope

- Current Ultimate MVP profile/remap binding only.
- No runtime logic change.
- No schema/proto/configurator structural change.
- No flashing automation.
- No push-to-device automation.

## Source-Traced Binding

- Source file changed: `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json` (`MODE_ULTIMATE` -> `buttonRemapping`).
- Old binding: `BTN_LT3 -> BTN_LF4`.
- New binding: `BTN_LT3 -> BTN_LT3`.
- Existing preserved bindings:
  - `BTN_RF3 -> BTN_LT1`
  - `BTN_RF4 -> BTN_LT2`

Relation to the existing Tilt mappings:
- `BTN_RF3 -> BTN_LT1` and `BTN_RF4 -> BTN_LT2` remain unchanged.
- This branch only repoints the physical left-thumb LT3 entry to logical LT3.

## Runtime Relation

- `inputs.lt3` activates Tilt3 through the already-merged native Ultimate runtime in `src/modes/Ultimate.cpp`.
- `LT1+LT2` remains an alternate Tilt3 trigger through the same runtime condition.

## Behavior Consequence

- In this Ultimate MVP profile, physical LT3 no longer activates logical `LF4` / `triggerLDigital` behavior.
- In this Ultimate MVP profile, physical LT3 now activates logical `LT3` for dedicated Tilt3.

## Caveats

- Standalone LT3 hardware testing is still required before accepting dedicated LT3 behavior.
- Prior hardware result verified `LT1+LT2 -> Tilt3` only, not standalone LT3.
- D-pad interaction remains unverified on the normal layout without D-pad buttons.
- Nunchuk remains `NOT_TESTED_UNAVAILABLE` unless tested later.

## Future Allocation Note

- This branch establishes a source-supported physical-to-logical reassignment pattern for later allocation updates.
- It does not automatically allocate all remaining desired buttons.
