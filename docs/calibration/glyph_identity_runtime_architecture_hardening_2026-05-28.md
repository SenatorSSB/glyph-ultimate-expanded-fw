# Glyph Identity Runtime Architecture Hardening - 2026-05-28

## Scope

This document records behavior-preserving architecture hardening for the current native `MODE_ULTIMATE` identity-runtime Smash Box implementation.

No runtime behavior, raw coordinate table value, button role, profile artifact, schema/proto/configurator structure, priority order, or unrelated mode behavior is intentionally changed by this branch.

## Current Hardware-Verified Status

The current runtime behavior is documented as hardware-verified in `docs/calibration/glyph_identity_runtime_smashbox_latest_hardware_result_2026-05-28.md`.
The canonical declarative role-map artifact for this scope is `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`.
The representative source-backed behavior-case matrix for this scope is `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`; it is docs/fixture/checker-only and is not a new hardware result.
The bounded evaluator harness for the representative matrix is documented in `docs/calibration/glyph_identity_runtime_behavior_evaluator_harness_2026-05-28.md`; it is source-backed but not hardware validation.

The verified scope includes the explicit self-activated identity profile compatibility, current raw table values, Mode/default tables, X1/X2, Y1/MY1, Tilt1/Tilt2/Tilt3, Mode tilt tables, scratched Y2/MY2 runtime policy, Y1+Tilt1 composite, LT5/RF11 Z-airdodge low-magnitude override, LT4=X1, LT1=X2, LT3=L, RF9 null modifier, LT6 hard Down+A, RF12/RF15 hard Up+A, RF13 LS->DPad, RF7 hard Up+B, LF8/LF7 layer-left/layer-right, LF4 sub-mode, LF4+LT2 Y1 suppression, LF4 sub-mode RF2/RF3 behavior, RF2 suppression by C-stick in LF4 sub-mode, RF4 flipper, RF3 pure-layer B + normal-x behavior, RT4=C-right, RT5=C-up, no profile semantic remaps, and no SOCD changes for the custom layer behavior.

Nunchuk override behavior remains source-present but not hardware-validated in the latest result because nunchuk hardware was unavailable.

## Runtime Evaluator Phases

The runtime is represented as a primitive evaluator with named local state in `src/modes/Ultimate.cpp`.

Digital/effective direction phase:

1. Physical inputs are read from `InputState`.
2. LF8/LF7 layer direction contribution is resolved.
3. LF4 sub-mode activation is resolved.
4. Forced-Up sources are resolved.
5. B/X/Z/L/R/A/Y/menu digital output carriers are applied.
6. RF13 LS->DPad digital routing is applied.

Analog phase:

1. Base effective direction calculation.
2. Table selection.
3. Direction-plus-A hard override.
4. LT5/RF11 Z-airdodge low-magnitude override.
5. RF7 hard Up+B override.
6. RF9 null override.
7. Nunchuk override, if connected.

The source order is intended to match the hardware-tested expectations. If future source inspection finds a different effective order, that difference must be documented before behavior changes are attempted.

## Primitive Role Categories

Digital button output:

- RF1=A, RF5/LF4/RF7 and pure-layer RF3 contribute B as documented, RF2=X outside pure layer and in LF4 sub-mode unless C-stick suppressed, RF10=Y, RT1/LT5/RF11=Z carrier, LT3=L, RF16=R, MB4/MB5/MB6/MB7 menu outputs.

Direction contribution:

- LF3/LF1/LF2/LF5 are base left/right/up/down inputs.
- LF8 contributes layer-left and LF7 contributes layer-right.
- RF6, RF12, RF15, pure-layer RF2, and LF4-sub-mode RF3 contribute forced-Up sources.
- LT6 contributes hard Down+A and participates in effective down only when forced-Up is not active.

Table modifier:

- LT4=X1, LT1=X2, LT2=Y1 when LF4 is not held, RF3=Tilt1 outside layer/sub-mode, RF4=Tilt2 outside layer/sub-mode, RF3+RF4=Tilt3 outside layer/sub-mode.

Composite table modifier:

- Y1+Tilt1 is an explicit composite exception with dedicated non-Mode and Mode tables.
- Y1+layer RF3 normal-x and Y1+layer RF4 flipper are explicit layer composites with dedicated tables.

Layer override:

- Pure LF8/LF7 layer changes RF2 to forced Up, RF3 to B + normal-x, and RF4 to flipper.

Sub-mode override:

- LF4 sub-mode activates when LF4 is held with LT2 or LF8/LF7.
- In sub-mode, LF4 keeps B asserted, LT2/Y1 is suppressed, RF2 is X unless C-stick suppressed, RF3 is forced Up, and RF4 is flipper.

Hard analog override:

- LT6, RF12, and RF15 apply direction-plus-A hard analog override.
- LT5/RF11 apply the low-magnitude Z-airdodge table when LS->DPad is inactive.
- RF7 applies hard Up+B analog output when LS->DPad is inactive.

Null analog override:

- RF9 forces final left-stick analog output to `(128,128)` after table selection, direction-plus-A, LT5/RF11, and RF7.

LS->DPad:

- RF13 routes effective left-stick directions to D-pad output and centers analog left stick before RF9 final null can apply.

## Layer/Sub-Mode Model

Pure LF8/LF7 layer:

- LF8 contributes left.
- LF7 contributes right.
- RF2 becomes forced Up and does not output X.
- RF3 becomes B + normal-x.
- RF4 becomes flipper.
- RF4 flipper wins over RF3 normal-x for table selection when both are held.
- Pure-layer RF2 remains forced Up even with C-stick if LF4 is not held.

LF4 sub-mode:

- Active when `LF4 && (LT2 || LF8 || LF7)`.
- LF4 always outputs B.
- LT2/Y1 is suppressed.
- RF2 outputs X unless any RT2/RT3/RT4/RT5 C-stick button is active.
- RF3 becomes forced Up.
- RF4 becomes flipper.
- Any RT2/RT3/RT4/RT5 suppresses RF2 completely in LF4 sub-mode.

Inactive layer/sub-mode:

- RF2=X.
- RF3=Tilt1.
- RF4=Tilt2.
- RF3+RF4=Tilt3.

## Profile/Config Future Direction

Firmware should own the primitive evaluator and priority model.

Profiles should eventually own role bindings, raw coordinate tables, layer definitions, and hard override constants.

Profiles should not become arbitrary scripting. The migration target is declarative data feeding the same bounded evaluator categories and priority rules.

## Migration Target

Stage 1: current hardcoded runtime.

Stage 2: generated C++ config from a declarative role map.

Stage 3: runtime-loaded config.

Stage 4: Senscope export.

The docs/tools-only generated-config contract and Senscope export draft are recorded in `docs/calibration/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.md` and `docs/calibration/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.md`; they do not implement runtime-loaded config or device writing.

The docs/tools-only runtime-loaded config design and validation contract are recorded in `docs/calibration/glyph_runtime_loaded_config_design_v0_2026-05-28.md` and `docs/calibration/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.md`; they remain design-only and do not implement runtime-loaded config, serial/device write behavior, firmware runtime changes, or hardware validation.

Preimplementation gates for generated constants, runtime-loaded config, device write/transport, and hardware-validation boundaries are explicitly tracked in `docs/calibration/glyph_preimplementation_go_nogo_index_2026-05-28.md`.

Docs/tools-only implementation planning packets for generated constants, runtime-loaded config, and hardware validation/rollback are recorded in `docs/calibration/glyph_generated_constants_refactor_implementation_plan_v0_2026-05-28.md`, `docs/calibration/glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.md`, and `docs/calibration/glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.md`; they are design-only gates and do not approve firmware source edits.

The generated constants refactor remains blocked until explicit approval, but the docs/tools-only execution packet, future prompt template, and hardware matrix now record the bounded future scope in `docs/calibration/glyph_generated_constants_refactor_execution_packet_2026-05-28.md`.

Each stage must preserve source-backed controller/backend behavior and must not promote game-semantic claims into firmware without separate source authority.

## Behavior Preservation

This branch is behavior-preserving by intent. The hardening work extracts named helper structs/functions and documents priority order. It does not intentionally change raw tables, role bindings, profile artifacts, schema/proto/configurator structure, SOCD behavior, or hardware-result documentation.

If behavior-preservation checks or build verification detect a runtime output change, the latest hardware PASS is not automatically applicable and fresh hardware validation is required.
