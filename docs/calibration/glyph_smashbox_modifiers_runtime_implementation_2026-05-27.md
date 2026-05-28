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
- `RT1 = Z`

Shoulders / triggers:

- `LT1 = L`
- `RF16 = R`

Source-backed carrier note:

- `OutputState` has no literal `z` member.
- The inspected GameCube/N64 backends serialize `outputs.buttonR` as report `z`.
- The inspected GameCube/N64 backends serialize `outputs.triggerRDigital` as report `r`.
- Runtime therefore assigns `RT1` to `outputs.buttonR` for source-confirmed Z and assigns `RF16` to `outputs.triggerRDigital` for source-confirmed R on those backends.
- `LT1` drives `outputs.buttonL` and `outputs.triggerLDigital`; the analog L trigger follows the digital carrier at value `140`.
- `RF16` drives `outputs.triggerRDigital`; the analog R trigger follows the digital carrier at value `140`.

Left-stick directions:

- `LF3 = Left`
- `LF1 = Right`
- `LF2 = Up`
- `LF5 = Down`
- `LT6 = forced Down+A`
- `RF6 = forced Up`
- `RF12 = forced Up+A`
- Forced-Up sources `RF6` and `RF12` suppress Down sources `LF5` and `LT6` for runtime table direction.

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
- `LT3 = Y2`
- `RF7 = LS->DPad`
- `RF6 = forced Up`
- `RF3 = Tilt1`
- `RF4 = Tilt2`
- `RF3 + RF4 = Tilt3`

Direction-plus-A runtime roles (not modifiers):

- `LT6 = Down+A`
- `RF12 = Up+A`
- `RF16` remains `R` and is not replaced by `RF12`.

Historical replacement:

- Previous standalone `LT3 -> Tilt3` behavior is historical only.
- In this identity runtime profile, `LT3` is `Y2`.
- Tilt3 is now the `RF3+RF4` chord.

Direction mapping used by identity runtime:

- `LF3 = Left`
- `LF1 = Right`
- `LF2 = Up`
- `LF5 = Down`
- `LT6 = forced Down+A`
- `RF6 = forced Up`
- `RF12 = forced Up+A`

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

- X1, X2, Y1, Y2, effective Tilt1/Tilt2/Tilt3
- Direction-plus-A buttons `LT6` and `RF12` are not modifiers and do not participate in modifier-count composition.

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

Direction-plus-A and forced-Up policy for table direction:

- Runtime A output is `outputs.a = inputs.rf1 || inputs.lt6 || inputs.rf12`.
- `RF12` provides forced Up plus A and overrides simultaneous Down sources.
- `LT6` provides Down plus A unless forced-Up (`RF6` or `RF12`) is active.
- `RF12` alone resolves to direction `8` and presses A.
- `RF12 + Down` resolves to direction `8` and presses A.
- `RF12 + LT6` resolves to direction `8` and presses A.
- `RF12 + Left` resolves to direction `7` and presses A.
- `RF12 + Right` resolves to direction `9` and presses A.
- `LT6` alone resolves to direction `2` and presses A.
- `LT6 + RF6` resolves to direction `8` and presses A.
- Existing `RF6` forced-Up rows remain valid (`RF6` keeps Up override semantics).

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
- Under LS->DPad, RF6/RF12 forced Up still override Down.
- Under LS->DPad, direction-plus-A still presses A while routing direction to D-pad.
- `RF7 + LT6` resolves to D-pad Down + A.
- `RF7 + RF12` resolves to D-pad Up + A.
- `RF7 + RF12 + Down` resolves to D-pad Up + A.
- There are no direct standalone D-pad inputs from `LF6`, `LF8`, or the old D-pad cluster.

## L/R/Z Button Behavior

- `LT1` now drives `outputs.buttonL` and the GameCube/N64 L carrier `outputs.triggerLDigital` in native Ultimate.
- `outputs.modX = inputs.lt1` is removed/neutralized for this identity runtime path (`modX` no longer follows LT1).
- `LT1` also drives `outputs.triggerLDigital`; `outputs.triggerLAnalog` follows that digital carrier at `140`.
- `RT1` drives `outputs.buttonR`, which the inspected GameCube/N64 backends serialize as report `z`.
- `RF16` drives `outputs.triggerRDigital`, which the inspected GameCube/N64 backends serialize as report `r`.
- `outputs.triggerRAnalog` follows `RF16` through `outputs.triggerRDigital` at `140`.
- `LF4` and `RF5` are no longer trigger carriers; they are duplicate B bindings in this runtime map.

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
- `LT3 => Y2` and no standalone LT3 Tilt3 claim,
- `LT1 => L`,
- `RT1 => Z`,
- `RF16 => R`,
- `RF1 => A`, `RF5/LF4 => B`, `RF2 => X`, and `RF10 => Y`,
- `RF6` forced-Up path does not press game Y,
- `RF4` behaves as Tilt2 and does not act as Up direction source,
- `RF3` Tilt1 path does not press R,
- `LT2` Y1 path does not emit prior LT2->modY behavior,
- `LT1` does not emit prior LT1->modX behavior,
- `LT6` Down+A path presses A and selects direction `2` table rows when no forced-Up is active,
- `RF12` Up+A path presses A and selects direction `8` table rows while overriding Down,
- `LT6/RF12` do not count as modifiers in X/Y/Tilt/Mode composition,
- LS->DPad behavior and orthogonality,
- no standalone D-pad outputs from empty buttons,
- empty/no-output buttons remain inert,
- nunchuk availability row handling.

## 2026-05-28 Amendment: Identity Runtime Hardware Confirmation

- Identity-runtime Smash Box firmware plus explicit self-activated identity profile was hardware-confirmed by user report.
- Final result doc: `docs/calibration/glyph_identity_runtime_smashbox_hardware_result_2026-05-28.md`.
- Hardware validation coverage reported by user includes all angles, functions, and combinations.

## 2026-05-28 Amendment: Direction-Plus-A Additions

- `LT6 = Down+A` and `RF12 = Up+A` are runtime-owned direction-plus-A additions in native Ultimate.
- `RF16` remains runtime-owned `R`; `RF12` does not replace `R`.
- Direction-plus-A additions require a new hardware validation pass for those rows.
