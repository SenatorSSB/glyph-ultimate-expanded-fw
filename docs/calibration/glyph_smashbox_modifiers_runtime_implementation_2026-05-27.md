# Glyph Smash Box Modifiers Runtime Implementation - 2026-05-27

## Implementation Status

Implementation is complete in this branch for native `MODE_ULTIMATE` runtime source scope.

- Runtime source updated: `src/modes/Ultimate.cpp`
- Marker block added:
  - `// Senscope Glyph Smash Box runtime begin`
  - `// Senscope Glyph Smash Box runtime end`
- Hardware validation is still required before claiming hardware pass.

## Identity Runtime Policy

- User-facing button IDs are physical-position IDs.
- Active identity baseline uses same-name physical/logical button IDs.
- Runtime consumes post-remap same-name logical fields directly.
- No semantic profile remapping for these custom modifier roles is used in this branch.

## Runtime Role Table

- `RF8 = Mode`
- `LT5 = X1`
- `LT4 = X2`
- `LT2 = Y1`
- `LT3 = Y2`
- `RF7 = LS->DPad`
- `LT1 = L`
- `RF3 = Tilt1`
- `RF4 = Tilt2`
- `RF3 + RF4 = Tilt3`

Historical replacement:

- Previous standalone `LT3 -> Tilt3` behavior is historical only.
- In this identity runtime profile, `LT3` is `Y2`.
- Tilt3 is now the `RF3+RF4` chord.

## Canonical Table Source

- `docs/calibration/glyph_smash_box_profile_output_tables_2026-05-27.md`

The runtime applies those exact absolute raw left-stick table values.

## Modifier Composition Policy

Tilt family compression:

- `RF3 && RF4` => effective Tilt3
- `RF3` alone => effective Tilt1
- `RF4` alone => effective Tilt2

Active effective non-mode modifiers counted:

- X1, X2, Y1, Y2, effective Tilt1/Tilt2/Tilt3

Selection logic:

- Mode inactive:
  - count `0` => Default table
  - count `1` => matching non-Mode table
  - count `>=2` => Default table
- Mode active:
  - count `0` => Mode default table
  - count `1` => matching `M*` table
  - count `>=2` => Mode default table

Therefore:

- X+Y together deactivate to Default/Mode default.
- X/Y + Tilt together deactivate to Default/Mode default.
- Mode + multiple modifiers gives Mode default.
- Mode + exactly one modifier gives the matching M-table.

## LS->DPad Policy

- `RF7` enables LS->DPad.
- While LS->DPad is active:
  - left-stick direction buttons drive D-pad directions,
  - left stick is forced to direction `5` center,
  - Mode inactive center is `(128,128)`,
  - Mode active center is `(128,172)`.
- LS->DPad is orthogonal to right-stick/C-stick and trigger paths.
- LS->DPad does not reintroduce the old prototype D-pad-layer side effects.
- Old nunchuk C D-pad behavior is preserved only when nunchuk C is active.

## L Button Behavior

- `LT1` now drives `outputs.buttonL` for native Ultimate backends (including Switch/GameCube mappings through existing backend output adapters).
- Existing trigger behavior remains on its prior trigger paths.

## Preservation Boundaries

Preserved:

- No schema/proto/configurator structure change.
- No firmware flashing automation.
- No macro/turbo/toggle/one-shot/timing automation.
- No unrelated mode changes.
- Nunchuk overwrite behavior remains after left-stick runtime logic.
- Right-stick/C-stick and trigger runtime paths remain intact outside the LS->DPad-specific left-stick redirection.

## Hardware Test Requirements

Manual hardware validation is required for:

- all Default/Mode/X/Y/Tilt/M-table direction outputs,
- `RF3+RF4 => Tilt3`,
- `LT3 => Y2` and no standalone LT3 Tilt3 claim,
- `LT1 => L`,
- LS->DPad behavior and orthogonality,
- nunchuk availability row handling.
