# Glyph Identity Runtime Role Map - 2026-05-28

## Purpose and status

Source-backed canonical documentation for the current hardware-verified Smash Box identity runtime in native `MODE_ULTIMATE`.

- Status: docs-only canonicalization of existing behavior in `src/modes/Ultimate.cpp`.
- Scope: runtime role map, layer/sub-mode logic, table-selection policy, and priority ordering.
- Non-goal: runtime behavior change, table value change, profile/profile-schema change, or Senscope app logic claims.

## Source authority and hardware-validation status

Source files used:

- `src/modes/Ultimate.cpp`
- `docs/calibration/glyph_smashbox_modifiers_runtime_implementation_2026-05-27.md`
- `docs/calibration/glyph_identity_runtime_smashbox_latest_hardware_result_2026-05-28.md`
- `docs/calibration/glyph_identity_runtime_architecture_hardening_2026-05-28.md`
- `docs/calibration/glyph_ultimate_identity_profile_baseline_2026-05-27.md`
- `docs/calibration/glyph_smash_box_profile_output_tables_2026-05-27.md`

Hardware validation status:

- Current identity runtime scope is hardware-tested in `docs/calibration/glyph_identity_runtime_smashbox_latest_hardware_result_2026-05-28.md`.
- Nunchuk behavior remains preserved in source but not hardware-validated.

## Physical input ids

- Active physical/logical IDs in explicit self-activates identity profile path:
  - `BTN_LF2`, `BTN_LF3`, `BTN_LF1`, `BTN_LF4`, `BTN_LF5`, `BTN_LF6`, `BTN_LF7`, `BTN_LF8`
  - `BTN_LT1`, `BTN_LT2`, `BTN_LT3`, `BTN_LT4`, `BTN_LT5`, `BTN_LT6`
  - `BTN_RT1`, `BTN_RT2`, `BTN_RT3`, `BTN_RT4`, `BTN_RT5`
  - `BTN_RF1`, `BTN_RF2`, `BTN_RF3`, `BTN_RF4`, `BTN_RF5`, `BTN_RF6`, `BTN_RF7`, `BTN_RF8`, `BTN_RF9`, `BTN_RF10`, `BTN_RF11`, `BTN_RF12`, `BTN_RF13`, `BTN_RF14`, `BTN_RF15`, `BTN_RF16`
  - `BTN_MB4`, `BTN_MB5`, `BTN_MB6`, `BTN_MB7`

- Explicitly no-output physical IDs in this runtime scope:
  - `BTN_LF6`, `BTN_RT?` not used as game outputs by source
  - `BTN_RF14`
  - `BTN_MB1`, `BTN_MB2`, `BTN_MB3`

## Normal game button bindings

- `RF1 = A`
- `RF5 = B`
- `RF10 = Y`
- `LT3 = L`
- `RF16 = R`
- `RT1 = Z`
- `LT5 = Z`
- `RF11 = Z (airdodge-safe alias)`
- `RF2 = X` (except layer/sub-mode suppression)
- `RF6` does not map to Y; it is a forced-up directional source.
- `RF12/RF15 = Up+A` (hard analog override role below)
- Menu:
  - `MB4 = Capture`
  - `MB5 = Home`
  - `MB6 = Select/Minus`
  - `MB7 = Start/Plus`

## Main directional bindings

- Base directional inputs:
  - `LF3 = Left`
  - `LF1 = Right`
  - `LF2 = Up`
  - `LF5 = Down`

- Hard directional sources:
  - `RF6 = Forced Up`
  - `RF12 = Up+A`
  - `RF15 = Up+A`
  - `RF3 = Forced Up` in LF4 sub-mode
  - `RF2 = Forced Up` in pure LF7/LF8 layer when not `LF4`

- Down direction source:
  - `LT6 = Down` contribution to base direction plus `LT6` role alias in Direction+`A`

## C-stick bindings

- `RT3 = C-Left`
- `RT4 = C-Right`
- `RT2 = C-Down`
- `RT5 = C-Up`

## Modifier role bindings

- `LT4 = X1`
- `LT1 = X2`
- `LT2 = Y1` when `LF4` is not held
- `RF3 = Tilt1` when layer/sub-mode modifiers are inactive
- `RF4 = Tilt2` when layer/sub-mode modifiers are inactive
- `RF3 + RF4 = Tilt3` only when layer/sub-mode modifiers are inactive

Layer variants:

- `RF3` in pure LF7/LF8 layer (without `LF4`) = `B + Layer-RF3 normal-x` and no standalone Tilt1/Tilt2.
- `RF4` in pure LF7/LF8 layer (without `LF4`) = flipper x-only modifier.
- LF4 layer sub-mode: `RF2` may become X and `RF3` becomes forced-up, independent of tilt roles.

## Hard/special function bindings

- `RF8 = Mode`
- `RF9 = null modifier`
- `RF13 = LS->DPad`
- `RF7 = hard Up+B` (analog override role):
  - `RF7` applies the resolved effective horizontal direction after base left/right and LF8/LF7 layer contributions:
    - `resolved left => x = 77`
    - `resolved neutral => x = 128`
    - `resolved right => x = 179`
  - `y = 172`
  - does not select mode/modifier tables
- `LF4 = B` always, and activates LF4 sub-mode under rules below.

## Layer definitions

- `LF8` and `LF7` are directional layers, independent of profile remap:
  - `LF8 = layer-left`
  - `LF7 = layer-right`

- Pure-layer state (LF7 or LF8 active, and no LF4):
  - Horizontal from LF8/LF7 overlays into base directional resolution.
  - `RF2 = forced-up` and no X.
  - `RF3 = B + LayerNormalX`.
  - `RF4 = LayerFlipper`.
  - RF4 flipper wins over RF3 normal-x for table selection when both are held.

## LF4 sub-mode definition

Activation:

- `LF4 sub-mode` is active when `LF4 && (LT2 || LF8 || LF7)`.

Sub-mode behaviors:

- `LF4` always contributes `B`.
- `LT2`/`Y1` is suppressed while `LF4` is held.
- `RF2 = X`, except when C-stick is active.
- `RF3 = forced Up`.
- `RF4 = LayerFlipper`.
- `RF7` remains hard Up+B.

## Suppression rules

- `LT2`/`Y1` suppressed by `LF4` (`Y1` role disabled when `LF4` active).
- In LF4 sub-mode, any C-stick (`RT2`, `RT3`, `RT4`, `RT5`) suppresses RF2 fully:
  - no `X`
  - no forced-up contribution
  - no directional LS phase contribution
  - no modifier contribution
- In pure-layer mode, RF2 forced-up remains even when C-stick active if `LF4` is not active.
- `RF4` and `RF3` flipper/normal-x composition applies only in layer contexts; RF3/RF4 become `Tilt3` only when not in layer or sub-mode.

## Forced-direction rules

Forced up sources, in runtime order:

1. `RF6`
2. `RF12`
3. `RF15`
4. Pure layer active `RF2`
5. LF4 sub-mode `RF3`

Down source:

1. `LT6` and `LF5` contribute down before forced-up suppression logic.
2. Forced-up cancels down (`if up is asserted`, `down = false`).

## LS->DPad routing rule

- `RF13` enables D-pad routing and suppresses source-derived analog left-stick direction output.
- D-pad outputs preserve normal Nunchuk C-cluster directions; RF13 then ORs effective left-stick up/down/left/right into D-pad.

## Analog priority order

1. Table output from active direction table
2. `Direction+ A` override
3. `LT5/RF11` low-magnitude neutral-airdodge override
4. `RF7` hard Up+B override
5. `RF9` null override
6. Pre-existing nunchuk override (if connected)

## Table ids and table selection rules

- Direction convention is numpad-style (`1` left-down, `2` down, `3` right-down, ..., `8` up, `9` right-up).
- Table constants in code:
  - `Default`
  - `Mode default`
  - `X1`, `X2`, `MX1`, `MX2`
  - `Y1`, `Y2`, `MY1`, `MY2`
  - `Tilt1`, `Tilt2`, `Tilt3`
  - `MTilt1`, `MTilt2`, `MTilt3`
  - Layer tables: `LayerNormalX`, `LayerFlipper`, `MLayerNormalX`, `MLayerFlipper`
  - Layer composites: `Y1+LayerNormalX`, `Y1+LayerFlipper`
  - `Y1+Tilt1`

- Y2/MY2 are source-supplied constants in `src/modes/Ultimate.cpp` but not runtime-selected; status is `historical`/inactive.
- Runtime table selection:
  1. Resolve one-of modifier/effective-mode state.
  2. If exactly one modifier is effective (including mode +1), apply that table.
  3. If zero or multiple effective modifiers are active, use base table (`Default` or `Mode default` when in mode).
  4. Special composites override normal table counting:
     - `Y1` + `Tilt1` (without x2/x1/layer flipper/layer normal-x/tilt2/tilt3) => Y1+Tilt1 table
     - `Y1` + layer normal-x => Y1+LayerNormalX table
     - `Y1` + layer flipper => Y1+LayerFlipper table

## Hard analog override

- `LT6`, `RF12`, `RF15` force final analog direction to index `2` or `8` (depending on forced-up state) from base/default table (`hard Down+A` / `hard Up+A`).
- `LT5`/`RF11` low-magnitude override uses `kLt1LowMagnitudeTable`:
  - `1=(89,89), 2=(128,79), 3=(167,89), 4=(79,128), 5=(128,128), 6=(177,128), 7=(89,167), 8=(128,177), 9=(167,167)`
- `RF7` hard Up+B override:
  - horizontal = `77` when effective left
  - horizontal = `128` when centered
  - horizontal = `179` when effective right
  - vertical = `172`
- Null role uses explicit analog override regardless of previous analog phase:
  - `RF9 => (128,128)`

## Null override

- `RF9` applies final analog override to `(128,128)` and is not a game button.
- `RF9` does not suppress B/X/Z/menu outputs.
- Under `RF13` LS->DPad, `RF9` still forces the analog left-stick neutral point.

## Nunchuk status: preserved but not hardware-tested

- Source behavior for Nunchuk is preserved in `src/modes/Ultimate.cpp`:
  - C-cluster D-pad can route C-stick into D-pad when active.
  - Nunchuk C-side left-stick analog override is applied after all software modifiers.
- Status in this branch: preserved in-source, no new hardware validation result.

## Future migration path

1. Current hardcoded runtime map (this branch) as canonical documentation.
2. Generate C++ constants from this declarative role-map document.
3. Load runtime role map at runtime from config-like input.
4. Export to Senscope canonical model after runtime/input/output behavior is review-cleared.

## Current behavior preservation statements

- No table values are changed by this file.
- No game-button bindings or profile semantics are changed by this file.
- No runtime source changes are included in this artifact.
- Nunchuk behavior and trigger semantics remain preserved source-present, unchanged.
