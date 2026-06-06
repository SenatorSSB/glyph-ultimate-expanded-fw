# Glyph GFW3 Runtime Remap Rework Spec - 2026-06-04

## Purpose and status

This document is the docs/tools source-of-truth packet for the requested Glyph /
Smash Box `MODE_ULTIMATE` runtime remap rework.

Status:

- firmware behavior change requested;
- docs/fixture/checker specification only in this branch;
- firmware implementation not yet claimed by this document;
- hardware validation not claimed by this document;
- final merge to `configurator` blocked until user hardware testing passes and
  a hardware result document is recorded.

## Source authority

This packet is authorized by the user requirements for the
`glyph/gfw3-runtime-remap-rework` integration branch and bounded by repository
source inspection of:

- `src/modes/Ultimate.cpp`;
- `src/modes/UltimateIdentityRuntimeTables.hpp`;
- `tools/check_glyph_identity_runtime_behavior_evaluator.py`;
- `tools/check_glyph_identity_runtime_behavior_cases.py`;
- `docs/calibration/glyph_identity_runtime_architecture_hardening_2026-05-28.md`.

Where this document describes desired behavior, it is a requested behavior
specification, not a claim that the current firmware already implements it.

## Scope boundaries

This packet does not:

- alter active profile artifacts;
- alter physical ID mapping;
- alter nunchuk behavior;
- implement runtime-loaded config;
- implement WebSerial or device write;
- add macros, turbo, timing automation, one-shots, toggles, or history-dependent
  behavior;
- change Super Smash Bros. Ultimate game semantics;
- claim hardware validation.

## Base button roles

Required base-role changes:

- RF6 becomes Z plus the existing low-magnitude neutral-airdodge-safe analog
  override table.
- RF5 becomes forced Up plus A, inheriting the previous hard Up+A behavior.
- RF15 no longer carries hard Up+A.
- RF12 no longer carries hard Up+A.
- RF11 no longer carries Z-airdodge.
- RF3 + RF4 must not activate Tilt3.
- RF3 base role becomes X.
- RF2 base role becomes B.
- RF4 base role becomes the current Tilt1 table.
- RF4 + RF2 changes only the RF4 modifier X offset to -41 while preserving the
  rest of Tilt1.
- RF4 mirrored/flipper/modifier behavior is suppressed while any C-stick button
  `RT2`, `RT3`, `RT4`, or `RT5` is held.
- RT1 + RF4 custom table is exempt from RF4 C-stick suppression and remains
  active even with a C-stick button held.
- RT1 no longer carries Z.
- RT1 base role becomes the current Tilt2 table.
- Mode + RT1 uses MTilt2.
- RT1 + RF4 uses the custom table in this spec and has priority over RF4-alone
  and RT1-alone modifiers.
- RF9 full-null mode nulls both left stick and right stick inputs.
- RF9 + RF4 disables all RF9 nullification only while RF4 behavior is available
  and does not press any extra button.
- RF9 + RF4 + C-stick suppresses RF4 behavior, so RF9 nullification becomes
  active again and nulls both sticks.
- RF9 + RF3 enters a base-RF3-X suppression mode when RF3 would otherwise
  produce base X (`RF3`, not `LT2`, not `LF4`).
- RF9 base-RF3-X suppression mode suppresses base RF3 X while no C-stick button
  is held, but it does not full-null left stick or right stick/C-stick output.
- RF9 + RF3 + C-stick restores base RF3 X; this restoration applies only to the
  base RF3 X role, keeps C-stick output active, and does not convert LT2+RF3 or
  LF4+RF3 into X.
- RF4 behavior is suppressed/nullified while RF9 base-RF3-X suppression mode is
  active, including RT1+RF4 custom behavior.
- RF7 hard Up+B remains unchanged.
- RF13 LS->DPad remains unchanged.

## LT physical move cycle

Required final LT roles:

- LT1 = old LT3 = L.
- LT4 = old LT1 = X2 / MX2.
- LT5 = old LT4 = X1 / MX1.
- LT3 = new L + R role.

LT5 no longer owns Z-airdodge behavior. The old LT5/RF11 Z-airdodge behavior is
moved only to RF6.

## Mode behavior

Mode still exists. Mode + RT1 must use MTilt2.

MTilt1 can be scratched. Mode can win over RF4/Tilt1 for now. The RT1+RF4
custom table uses the same raw-coordinate table in Mode and non-Mode unless the
current architecture requires an explicit mode-specific table; this spec does
not define a separate mode table.

## RT1 + RF4 custom table

The RT1 + RF4 custom modifier table uses raw coordinates only:

| Direction | Raw coordinate |
| --- | --- |
| 1 | `(69, 78)` |
| 2 | `(128, 78)` |
| 3 | `(187, 78)` |
| 4 | `(69, 128)` |
| 5 | unchanged / unset |
| 6 | `(187, 128)` |
| 7 | `(72, 172)` |
| 8 | `(128, 179)` |
| 9 | `(184, 172)` |

Firmware must not derive or store effective outputs for this table.

## LF8/LF7 removal

LF8 layer-left and LF7 layer-right are scratched from effective runtime
behavior. Their layer contingencies and pure-layer RF2/RF3/RF4 behavior are
scratched. LF8 and LF7 must not affect direction, layer, or submode behavior
unless unrelated normal runtime roles are separately source-backed.

## LT2 sublayer

LT2 remains primarily Y1/MY1 when no LT2 sublayer behavior is active.

While LT2 is held:

- RF4 = -41 flipper modifier.
- RF3 = B plus +41 normal-x modifier.
- RF3 + RF4 = B plus -41 flipper modifier, with RF4 winning over RF3.
- RF2 = forced Up.
- RF1 = X.
- RF1 X is suppressed if RT2, RT3, RT4, or RT5 is pressed.
- RT2/RT3/RT4/RT5 retain normal C-stick behavior.

The normal-x and flipper tables are the existing layer normal-x and layer
flipper tables:

- normal-x: `[(87,51), (128,51), (169,51), (87,128), (128,128), (169,128), (87,205), (128,205), (169,205)]`;
- flipper: `[(169,51), (128,51), (87,51), (169,128), (128,128), (87,128), (169,205), (128,205), (87,205)]`.

If any C-stick button is held, LT2+RF4 flipper behavior is suppressed. For
LT2+RF3+RF4 with C-stick held, RF4 no longer wins; the result falls back to
LT2+RF3 B plus normal-x behavior.

## LF4 submode

LF4 overrides LT2 behavior when both are held.

While LF4 is held:

- LF4 itself still outputs B.
- RF4 = Tilt1 table.
- RF3 = forced Up.
- RF2 = X.
- RF2 + RF4 deactivates RF4 modifier.
- If RT2, RT3, RT4, or RT5 is pressed, RF2's X is suppressed.
- RF2 still deactivates RF4 when RF2's X is suppressed by C-stick.
- RT2/RT3/RT4/RT5 retain normal C-stick behavior.
- LF4+RF4 Tilt1 behavior is suppressed while any C-stick button is held.

## RF3 vertical C-stick special

When physical RF3 is held and C-stick Up/Down is active, C-stick output becomes
a diagonal only if resolved digital left/right direction is nonzero.

The direction source is the resolved digital left/right state represented by
`EffectiveDirectionState.left/right`. It does not come from the selected
modifier table, final left-stick analog output, RF7, RF6, RF9, RT1+RF4, Tilt1,
Tilt2, or any analog modifier.

Coordinates:

- RF3 + RT5 + resolved left: right stick `(95,165)`.
- RF3 + RT5 + resolved right: right stick `(161,165)`.
- RF3 + RT2 + resolved left: right stick `(95,91)`.
- RF3 + RT2 + resolved right: right stick `(161,91)`.

If resolved left/right is neutral, normal C-stick vertical behavior is
preserved. If RT3 or RT4 is pressed, this RF3 vertical-special rule does not
apply and existing C-stick horizontal or two-axis diagonal/ASDI behavior is
preserved.

Existing C-stick horizontal or two-axis diagonal/ASDI behavior is preserved
outside this RF3 vertical-special case.

## Priority expectations

Expected high-level priority:

- LF4 submode overrides LT2 sublayer.
- RT1+RF4 custom table overrides RF4-alone Tilt1 and RT1-alone Tilt2.
- RT1+RF4 custom table remains active under C-stick.
- RF4 modifier behavior is suppressed by C-stick outside the RT1+RF4 custom
  exception.
- RF4+RF2 base interaction changes RF4's X offset to -41 unless LF4 or LT2
  sublayer overrides are active.
- Existing C-stick two-axis diagonal/ASDI behavior is preserved outside the RF3
  vertical-special case.
- RF9 full null remains last among analog overrides except RF9+RF4 disables RF9
  nulling while RF4 behavior is available, and except RF9 base-RF3-X suppression
  mode disables full left-stick/right-stick null.
- RF9 null also nulls right stick when active.
- Nunchuk behavior remains preserved and untested; do not alter it.

## Hardware and implementation caveats

This spec is not a hardware result. Hardware validation remains blocked until
the user tests firmware on hardware and records a result document.

This spec does not claim that firmware implementation exists. Firmware source
changes are expected in a later branch under the same integration branch.
