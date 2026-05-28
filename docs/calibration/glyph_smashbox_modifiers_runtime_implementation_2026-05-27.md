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

## Identity Artifact Caveat (2026-05-28)

- Runtime now requires an explicit self-activated identity profile artifact (`physicalButton == activates` in `MODE_ULTIMATE.buttonRemapping`).
- Hardware testing showed omitted-`activates` identity caused missing logical inputs, so omitted-`activates` is not treated as a reliable active baseline representation.

## Game Output Role Table

Main game buttons:

- `RF1 = A`
- `LT6 = Down+A`
- `RF12 = Up+A`
- `RF5 = B`
- `LF4 = B`
- `RF2 = X`
- `RF10 = Y`
- `LT1 = Z` (plus low-magnitude directional override when LS->DPad is inactive)
- `RT1 = Z`

Shoulders / triggers:

- `LT3 = L`
- `RF16 = R`

Source-backed carrier note:

- `OutputState` has no literal `z` member.
- The inspected GameCube/N64 backends serialize `outputs.buttonR` as report `z`.
- The inspected GameCube/N64 backends serialize `outputs.triggerRDigital` as report `r`.
- Runtime therefore assigns `RT1` and `LT1` to `outputs.buttonR` for source-confirmed Z and assigns `RF16` to `outputs.triggerRDigital` for source-confirmed R on those backends.
- `LT3` drives `outputs.buttonL` and `outputs.triggerLDigital`; the analog L trigger follows the digital carrier at value `140`.
- `LT1` contributes to the source-confirmed Z carrier and also applies a low-magnitude left-stick override when LS->DPad is inactive.
- `RF16` drives `outputs.triggerRDigital`; the analog R trigger follows the digital carrier at value `140`.

Left-stick directions:

- `LF3 = Left`
- `LF1 = Right`
- `LF2 = Up`
- `LF5 = Down`
- `LT6 = hard Down+A`
- `RF6 = forced Up`
- `RF12 = hard Up+A`
- Normal table-direction resolution still uses LF direction inputs plus RF6 forced-Up.
- LT6/RF12 direction-plus-A is applied afterward as a hard final left-stick override.

Right stick / C-stick:

- `RT4 = C-Up`
- `RT3 = C-Left`
- `RT5 = C-Right`
- `RT2 = C-Down`

Menu:

- `MB4 = Capture`
- `MB5 = Home`
- `MB6 = Select/Minus`
- `MB7 = Start/Plus`
- `MB1`, `MB2`, and `MB3` produce no game output in this runtime map.

Standalone D-pad:

- There are no standalone D-pad buttons in this runtime map.
- D-pad output is produced only by preserved nunchuk C behavior or by `RF7` LS->DPad using effective left-stick directions.

Empty/no-output physical IDs:

- `LF6`, `LF7`, `LF8`, `RF9`, `RF11`, `RF13`, `RF14`, `RF15`, `MB1`, `MB2`, and `MB3` output nothing in the native Ultimate runtime map.

## Custom Modifier Role Table

- `RF8 = Mode`
- `LT5 = X1`
- `LT4 = X2`
- `LT2 = Y1`
- `LT3 = L` (game output role; no longer a modifier role)
- `RF7 = LS->DPad`
- `RF6 = forced Up`
- `RF3 = Tilt1`
- `RF4 = Tilt2`
- `RF3 + RF4 = Tilt3`
- `Y2/MY2` are scratched/inactive in runtime selection.

Direction-plus-A runtime roles (not modifiers):

- `LT6 = Down+A`
- `RF12 = Up+A`
- `RF16` remains `R` and is not replaced by `RF12`.

Historical replacement:

- Previous standalone `LT3 -> Tilt3` behavior is historical only.
- Previous `LT3 -> Y2` behavior is historical only for this runtime path.
- `Y2/MY2` values remain documented in table docs for historical/source completeness.
- Tilt3 is now the `RF3+RF4` chord.

Direction mapping used by identity runtime:

- `LF3 = Left`
- `LF1 = Right`
- `LF2 = Up`
- `LF5 = Down`
- `RF6 = forced Up`
- `LT6/RF12` are not used as modifier-table direction-index sources.
- `LT6` and `RF12` instead hard-override final left-stick output to direction `2`/`8` using Default or Mode-default base tables.

`RF4` is Tilt2-only and is no longer consumed as Up direction input in the Smash Box runtime path.
`RF6` is forced-Up only and no longer drives game Y output in this runtime branch.
`RF10` is the game Y binding in this runtime branch.

## Canonical Table Source

- `docs/calibration/glyph_smash_box_profile_output_tables_2026-05-27.md`

The runtime applies those exact absolute raw left-stick table values.

## Modifier Composition Policy

Tilt family compression:

- `RF3 && RF4` => effective Tilt3
- `RF3` alone => effective Tilt1
- `RF4` alone => effective Tilt2

Active effective non-mode modifiers counted:

- X1, X2, Y1, effective Tilt1/Tilt2/Tilt3
- Direction-plus-A buttons `LT6` and `RF12` are not modifiers and do not participate in modifier-count composition.
- Scratched/inactive tables `Y2/MY2` do not participate in modifier-count composition.

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

Direction-plus-A hard final override policy:

- Runtime A output is `outputs.a = inputs.rf1 || inputs.lt6 || inputs.rf12`.
- LT6/RF12 are hard direction+A outputs and are not modifier-table direction-index sources.
- LT6/RF12 do not count as modifiers in composition and do not alter `SelectStickTable` modifier selection.
- Mode is respected as base-table selection for hard override:
  - Mode inactive hard override uses `kDefaultTable`.
  - Mode active hard override uses `kModeDefaultTable`.
- Hard override directions:
  - direction `2` for Down+A,
  - direction `8` for Up+A.
- Up override precedence while direction-plus-A is active:
- `RF12 + LT6` resolves to Up+A,
- `RF6 + LT6` resolves to Up+A.
- X/Y/Tilt modifier tables are ignored for final left-stick output when direction-plus-A is active.

LT1 Z-airdodge low-magnitude hard final override policy:

- `LT1` contributes to Z (`outputs.buttonR = inputs.rt1 || inputs.lt1`).
- When LS->DPad is inactive and `LT1` is held, final left-stick output is hard-overridden by a dedicated low-magnitude table, after modifier-table selection and after direction-plus-A hard override.
- This LT1 override ignores X/Y/Tilt modifier-table output for final left-stick values.
- This LT1 override ignores Mode default table output for final left-stick values.
- This LT1 override also overrides the LT6/RF12 direction-plus-A analog table output, while LT6/RF12 still press A through `outputs.a`.
- Effective direction source for LT1 low table uses:
  - Left: `LF3`
  - Right: `LF1`
  - Up: `LF2` or forced-Up (`RF6`/`RF12`)
  - Down: `LF5` or `LT6`, suppressed by forced-Up
- LT1 low-magnitude absolute raw coordinate table:
  - `1 = (89, 89)`
  - `2 = (128, 79)`
  - `3 = (167, 89)`
  - `4 = (79, 128)`
  - `5 = (128, 128)`
  - `6 = (177, 128)`
  - `7 = (89, 167)`
  - `8 = (128, 177)`
  - `9 = (167, 167)`
- These low-magnitude values are selected to stay below the neutral-airdodge directional threshold target:
  - cardinal effective radius `78.000`
  - diagonal effective radius `77.782`
  - all below `79.2`

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
- Under LS->DPad, direction-plus-A still presses A while routing hard effective direction to D-pad.
- `RF7 + LT6` resolves to D-pad Down + A.
- `RF7 + RF12` resolves to D-pad Up + A.
- `RF7 + RF12 + LT6` resolves to D-pad Up + A.
- `RF7 + RF6 + LT6` resolves to D-pad Up + A.
- Under LS->DPad, `LT1` still presses Z through the shared Z carrier, while analog left stick remains centered by LS->DPad behavior.
- `RF7 + LT1 + direction` resolves to `Z + D-pad direction` with analog left-stick centered.
- There are no direct standalone D-pad inputs from `LF6`, `LF8`, or the old D-pad cluster.

## L/R/Z Button Behavior

- `LT3` now drives `outputs.buttonL` and the GameCube/N64 L carrier `outputs.triggerLDigital` in native Ultimate.
- `outputs.modX = inputs.lt1` is removed/neutralized for this identity runtime path (`modX` no longer follows LT1).
- `LT3` drives `outputs.triggerLDigital`; `outputs.triggerLAnalog` follows that digital carrier at `140`.
- `RT1` remains a source-confirmed Z input and drives `outputs.buttonR`.
- `LT1` also contributes to `outputs.buttonR` so Z can be pressed from either RT1 or LT1.
- `outputs.buttonR` is `inputs.rt1 || inputs.lt1`.
- `RF16` drives `outputs.triggerRDigital`, which the inspected GameCube/N64 backends serialize as report `r`.
- `outputs.triggerRAnalog` follows `RF16` through `outputs.triggerRDigital` at `140`.
- `LF4` and `RF5` are no longer trigger carriers; they are duplicate B bindings in this runtime map.
- `RF16` remains runtime-owned `R`.

## Y Button and modY Behavior

- `RF6` is reserved for forced-Up direction behavior and is not used as game Y in this branch.
- `RF10` is the game Y binding in this branch (`outputs.y = inputs.rf10`).
- `LT2` remains the `Y1` modifier role only.
- `outputs.modY = inputs.lt2` is removed/neutralized for this identity runtime path (`outputs.modY = false`).
- `modY` remains neutralized unless later source-confirmed harmless/internal-only evidence is explicitly documented.

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
- `LT3 => L`,
- `LT1 => Z` plus low-magnitude table override behavior,
- `Y2/MY2` scratched (inactive/unreachable) in runtime selection,
- `RT1 => Z`,
- `RF16 => R`,
- `RF1 => A`, `RF5/LF4 => B`, `RF2 => X`, and `RF10 => Y`,
- `RF6` forced-Up path does not press game Y,
- `RF4` behaves as Tilt2 and does not act as Up direction source,
- `RF3` Tilt1 path does not press R,
- `LT2` Y1 path does not emit prior LT2->modY behavior,
- `LT1` does not emit prior LT1->modX behavior,
- `LT6` Down+A path hard-overrides final left-stick output to direction `2` using Default/Mode-default base tables,
- `RF12` Up+A path hard-overrides final left-stick output to direction `8` using Default/Mode-default base tables,
- LT6/RF12 hard-override rows ignore X/Y/Tilt final table outputs while preserving Mode base-table selection,
- `LT6/RF12` do not count as modifiers in X/Y/Tilt/Mode composition,
- LT1 low-table hard final override rows ignore X/Y/Tilt/Mode table outputs for final left-stick values,
- LT1 low-table hard final override rows supersede LT6/RF12 analog override output while preserving A press,
- LS->DPad behavior and orthogonality,
- LS->DPad + LT1 rows produce Z plus D-pad with analog left-stick centered,
- no standalone D-pad outputs from empty buttons,
- empty/no-output buttons remain inert,
- nunchuk availability row handling.

## 2026-05-28 Amendment: Identity Runtime Hardware Confirmation

- Identity-runtime Smash Box firmware plus explicit self-activated identity profile was hardware-confirmed by user report.
- Final result doc: `docs/calibration/glyph_identity_runtime_smashbox_hardware_result_2026-05-28.md`.
- Hardware validation coverage reported by user includes all angles, functions, and combinations.

## 2026-05-28 Amendment: LT1/LT3 Runtime Reassignment

- `LT3` is reassigned to runtime-owned `L`.
- `LT1` is reassigned to runtime-owned `Z` carrier plus low-magnitude directional override behavior.
- `Y2/MY2` are scratched/inactive in runtime selection and are no longer reachable modifier states.
- `RT1` remains runtime-owned `Z`.
- `RF16` remains runtime-owned `R`.
- `LT6 = Down+A` and `RF12 = Up+A` remain runtime-owned direction-plus-A additions.
- LT1 hard final analog override supersedes modifier-table and direction-plus-A analog outputs while preserving LT6/RF12 A press behavior.
- This reassignment requires a new hardware validation pass before claiming hardware PASS for these rows.
