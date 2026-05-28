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
- `RF6 = forced Up`
- `LT1 = L`
- `RF3 = Tilt1`
- `RF4 = Tilt2`
- `RF3 + RF4 = Tilt3`

Historical replacement:

- Previous standalone `LT3 -> Tilt3` behavior is historical only.
- In this identity runtime profile, `LT3` is `Y2`.
- Tilt3 is now the `RF3+RF4` chord.

Direction mapping used by identity runtime:

- `LF3 = Left`
- `LF1 = Right`
- `LF2 = Down`
- `RF6 = forced Up`

`RF4` is Tilt2-only and is no longer consumed as Up direction input in the Smash Box runtime path.
`RF6` is forced-Up only and no longer drives game Y output in this runtime branch.

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

RF6 forced-Up policy for table direction:

- `RF6` forces effective Up regardless of simultaneous Down.
- `RF6` alone resolves to direction `8`.
- `RF6 + Down` resolves to direction `8`.
- `RF6 + Left` resolves to direction `7`.
- `RF6 + Right` resolves to direction `9`.
- `RF6 + Left + Down` resolves to direction `7`.
- `RF6 + Right + Down` resolves to direction `9`.

## LS->DPad Policy

- `RF7` enables LS->DPad.
- While LS->DPad is active:
  - left-stick direction buttons drive D-pad directions,
  - left stick is forced to direction `5` center,
  - Mode inactive center is `(128,128)`,
  - Mode active center is `(128,172)`.
- While LS->DPad is active, digital left-stick outputs are suppressed (`leftStickLeft/Right/Down/Up` forced off).
- LS->DPad is orthogonal to right-stick/C-stick and trigger paths.
- LS->DPad does not reintroduce the old prototype D-pad-layer side effects.
- Old nunchuk C D-pad behavior is preserved only when nunchuk C is active.
- Under LS->DPad, RF6 still acts as forced Up and overrides Down.

## L Button Behavior

- `LT1` now drives `outputs.buttonL` for native Ultimate backends (including Switch/GameCube mappings through existing backend output adapters).
- `outputs.modX = inputs.lt1` is removed/neutralized for this identity runtime path (`modX` no longer follows LT1).
- Existing trigger behavior remains on its prior trigger paths.

## Y Button and modY Behavior

- `RF6` is reserved for forced-Up direction behavior and is not used as game Y in this branch (`outputs.y = false`).
- Game Y is intentionally left unassigned until a user-approved/source-backed physical binding is provided.
- `LT2` remains the `Y1` modifier role only.
- `outputs.modY = inputs.lt2` is removed/neutralized for this identity runtime path (`outputs.modY = false`).
- `modY` remains neutralized unless later source-confirmed harmless/internal-only evidence is explicitly documented.

## R Button Behavior

- `outputs.buttonR = inputs.rf3` is removed in this branch because RF3 is reserved for Tilt1.
- No replacement R physical assignment is introduced in this identity runtime branch.
- R is intentionally left unassigned until a user-approved/source-backed replacement is specified.

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
- RF6 forced-Up direction resolution rows (`RF6` with no direction, Down, Left/Right, and Down+Left/Right),
- `RF3+RF4 => Tilt3`,
- `LT3 => Y2` and no standalone LT3 Tilt3 claim,
- `LT1 => L`,
- `RF6` forced-Up path does not press game Y,
- `RF4` behaves as Tilt2 and does not act as Up direction source,
- `RF3` Tilt1 path does not press R,
- `LT2` Y1 path does not emit prior LT2->modY behavior,
- `LT1` does not emit prior LT1->modX behavior,
- LS->DPad behavior and orthogonality,
- nunchuk availability row handling.
