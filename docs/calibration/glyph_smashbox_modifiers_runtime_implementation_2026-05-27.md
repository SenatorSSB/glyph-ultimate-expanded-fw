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
- `RF15 = Up+A` (RF12 alias)
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

- `RT4 = C-Right`
- `RT3 = C-Left`
- `RT5 = C-Up`
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

- `LF6`, `LF7`, `LF8`, `RF11`, `RF13`, `RF14`, `MB1`, `MB2`, and `MB3` output nothing in the native Ultimate runtime map.

## Custom Modifier Role Table

- `RF8 = Mode`
- `RF9 = null modifier`
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

`RF9` null modifier policy:

- `RF9` is not a game button output path.
- `RF9` is not an X/Y/Tilt/Mode table selector.
- `RF9` does not participate in modifier counting/composition.
- `RF9` applies a final analog left-stick override to `(128,128)` after table selection, direction-plus-A override, and LT1 low-magnitude override.
- Under LS->DPad, `RF9` still forces final analog left stick to `(128,128)` while preserving LS->DPad D-pad behavior.

Direction-plus-A runtime roles (not modifiers):

- `LT6 = Down+A`
- `RF12 = Up+A`
- `RF15 = Up+A` alias (same hard Up+A behavior as RF12)
- `RF16` remains `R` and is not replaced by `RF12`/`RF15`.

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
- `LT6`, `RF12`, and `RF15` are not used as modifier-table direction-index sources.
- `LT6` and `RF12`/`RF15` instead hard-override final left-stick output to direction `2`/`8` using Default or Mode-default base tables.

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
- Ordinary non-Mode Tilt1 y offset is `81` from neutral center `128`, yielding Tilt1 y values `47/128/209`.

Active effective non-mode modifiers counted:

- X1, X2, Y1, effective Tilt1/Tilt2/Tilt3
- RF9 is excluded from effective-modifier counting.
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

Y1+Tilt1 special composite exception:

- `Y1 + Tilt1` is an explicit runtime exception to ordinary multi-modifier deactivation.
- The exception is active only when effective `Y1` and effective `Tilt1` are active with no other X/Y/Tilt modifier.
- If Mode is inactive, runtime uses special non-Mode Y1+Tilt1 composite:
  - Y values come from Y1 table (`99/128/157`).
  - X values use flipper-style offset `41` from center `128`:
    - left `169`
    - neutral `128`
    - right `87`
  - Table:
    - `1 = (169, 99)`
    - `2 = (128, 99)`
    - `3 = (87, 99)`
    - `4 = (169, 128)`
    - `5 = (128, 128)`
    - `6 = (87, 128)`
    - `7 = (169, 157)`
    - `8 = (128, 157)`
    - `9 = (87, 157)`
- If Mode is active, runtime uses special Mode Y1+Tilt1 composite:
  - Y values come from MY1 table (`179/169/77`).
  - X values use same flipper-style offset `41` from center `128`.
  - Table:
    - `1 = (169, 179)`
    - `2 = (128, 179)`
    - `3 = (87, 179)`
    - `4 = (169, 169)`
    - `5 = (128, 169)`
    - `6 = (87, 169)`
    - `7 = (169, 77)`
    - `8 = (128, 77)`
    - `9 = (87, 77)`
- If any extra X/Y/Tilt modifier is present with Y1+Tilt1, runtime falls back to ordinary multi-modifier policy:
  - Mode inactive => Default
  - Mode active => Mode default
- `Y1+Tilt2` and `Y1+Tilt3` are not special exceptions.

Direction-plus-A hard final override policy:

- Runtime A output is `outputs.a = inputs.rf1 || inputs.lt6 || inputs.rf12 || inputs.rf15`.
- LT6/RF12/RF15 are hard direction+A outputs and are not modifier-table direction-index sources.
- LT6/RF12/RF15 do not count as modifiers in composition and do not alter `SelectStickTable` modifier selection.
- Mode is respected as base-table selection for hard override:
  - Mode inactive hard override uses `kDefaultTable`.
  - Mode active hard override uses `kModeDefaultTable`.
- Hard override directions:
  - direction `2` for Down+A,
  - direction `8` for Up+A (`RF12` or `RF15`).
- With converted Mode default values, hard Mode rows are:
  - Mode + LT6 => `(128,87)` + A
  - Mode + RF12/RF15 => `(128,169)` + A
- Up override precedence while direction-plus-A is active:
- `RF12 + LT6` resolves to Up+A,
- `RF15 + LT6` resolves to Up+A,
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
  - Up: `LF2` or forced-Up (`RF6`/`RF12`/`RF15`)
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

## RF9 Null Modifier Policy

- Runtime reads `RF9` as a dedicated null modifier (`null_modifier_active = inputs.rf9`).
- RF9 does not change game-button output ownership (`A/B/X/Y/Z/L/R`), right-stick/C-stick, or menu outputs.
- RF9 does not emit D-pad output by itself.
- RF9 does not enter X/Y/Tilt/Mode table selection or effective-modifier counting.
- RF9 final analog priority:
  - after ordinary table selection,
  - after direction-plus-A hard analog override,
  - after LT1 low-magnitude override,
  - set final analog left stick to `(128,128)`.
- Under LS->DPad:
  - D-pad behavior remains from LS->DPad effective directions,
  - final analog left stick is still forced to `(128,128)` when RF9 is active.

## LS->DPad Policy

- `RF7` enables LS->DPad.
- While LS->DPad is active:
  - left-stick direction buttons drive D-pad directions,
  - left stick is forced to direction `5` center,
  - Mode inactive center is `(128,128)`,
  - Mode active center is `(128,169)` when RF9 is not active.
- If RF9 is active during LS->DPad, final analog left-stick output is `(128,128)`.
- While LS->DPad is active, digital left-stick outputs are suppressed (`leftStickLeft/Right/Down/Up` forced off).
- LS->DPad is orthogonal to right-stick/C-stick and trigger paths.
- LS->DPad does not reintroduce the old prototype D-pad-layer side effects.
- Old nunchuk C D-pad behavior is preserved only when nunchuk C is active.
- Under LS->DPad, direction-plus-A still presses A while routing hard effective direction to D-pad.
- `RF7 + LT6` resolves to D-pad Down + A.
- `RF7 + RF12` resolves to D-pad Up + A.
- `RF7 + RF15` resolves to D-pad Up + A.
- `RF7 + RF12 + LT6` resolves to D-pad Up + A.
- `RF7 + RF15 + LT6` resolves to D-pad Up + A.
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
- converted Mode default table rows (`1..9` with Mode center `(128,169)` and Mode Down `(128,87)`),
- converted MX1/MX2, MY1, MTilt1/MTilt2/MTilt3 table rows,
- RF6 forced-Up direction resolution rows (`RF6` with no direction, Down, Left/Right, and Down+Left/Right),
- `RF3+RF4 => Tilt3`,
- `LT3 => L`,
- `LT1 => Z` plus low-magnitude table override behavior,
- `Y2/MY2` scratched (inactive/unreachable) in runtime selection,
- `RT1 => Z`,
- `RF16 => R`,
- `RF1 => A`, `RF5/LF4 => B`, `RF2 => X`, and `RF10 => Y`,
- `RF6` forced-Up path does not press game Y,
- Tilt1 non-Mode table rows use y-values `47/128/209` (81-pixel y offset from center),
- `RF4` behaves as Tilt2 and does not act as Up direction source,
- `RF3` Tilt1 path does not press R,
- `Y1+Tilt1` special composite rows (Mode and non-Mode),
- Mode Y1+Tilt1 special composite rows use updated MY1 values (`179/169/77`),
- `LT2` Y1 path does not emit prior LT2->modY behavior,
- `LT1` does not emit prior LT1->modX behavior,
- `LT6` Down+A path hard-overrides final left-stick output to direction `2` using Default/Mode-default base tables,
- `RF12` and `RF15` Up+A rows hard-override final left-stick output to direction `8` using Default/Mode-default base tables,
- LT6/RF12/RF15 hard-override rows ignore X/Y/Tilt final table outputs while preserving Mode base-table selection,
- `LT6/RF12/RF15` do not count as modifiers in X/Y/Tilt/Mode composition,
- LT1 low-table hard final override rows ignore X/Y/Tilt/Mode table outputs for final left-stick values,
- LT1 low-table hard final override rows supersede LT6/RF12/RF15 analog override output while preserving A press,
- LS->DPad behavior and orthogonality,
- LS->DPad + LT1 rows produce Z plus D-pad with analog left-stick centered,
- RF9 null modifier rows:
  - RF9 alone forces final analog to `(128,128)` with no extra game output from RF9 itself,
  - RF9 + A keeps A output while analog remains `(128,128)`,
  - RF9 + LT1 keeps Z output while analog remains `(128,128)`,
  - RF9 + LT6/RF12/RF15 keeps A output while analog remains `(128,128)`,
  - RF9 + LS->DPad preserves D-pad behavior while analog remains `(128,128)`,
  - RF9 does not participate in modifier-count composition and does not select tables,
- RT4/RT5 C-stick swap rows (`RT4=C-right`, `RT5=C-up`),
- no standalone D-pad outputs from empty buttons,
- empty/no-output buttons remain inert (excluding RF15 because RF15 is active as Up+A alias, and excluding RF9 because RF9 is now null-modifier analog override),
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
- `LT6 = Down+A` and `RF12/RF15 = Up+A` remain runtime-owned direction-plus-A additions.
- LT1 hard final analog override supersedes modifier-table and direction-plus-A analog outputs while preserving LT6/RF12/RF15 A press behavior.
- This reassignment requires a new hardware validation pass before claiming hardware PASS for these rows.

## 2026-05-28 Amendment: Pre-Hardware Runtime Tuning

- Ordinary non-Mode Tilt1 y offset is updated to 81 from neutral center (y=`47/128/209`).
- `RF15` now aliases `RF12` as hard Up+A across runtime paths.
- `Y1+Tilt1` now has explicit special composite tables for Mode and non-Mode runtime.
- `RT4/RT5` C-stick mapping is swapped (`RT4=C-right`, `RT5=C-up`) consistently in digital, analog, and nunchuk-C passthrough mapping.
- Mode/M-table values are converted to the latest Smash Box profile values:
  - Mode default center is `(128,169)` with Mode Down `(128,87)`,
  - MX1/MX2 and MY1 values are updated,
  - MTilt1/MTilt2/MTilt3 values are updated,
  - Mode Y1+Tilt1 composite uses MY1 y-values `179/169/77`.
- `RF9` is now a dedicated null modifier with final analog override to `(128,128)` and no game-button ownership.
- These adjustments require a new hardware validation pass before claiming PASS for updated rows.
