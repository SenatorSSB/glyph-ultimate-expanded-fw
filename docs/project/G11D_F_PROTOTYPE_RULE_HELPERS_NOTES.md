# G11d-f Isolated Prototype Rule Helpers Notes

Status: implemented (isolated prototype helpers only)  
Branch: `proto/glyph-prototype-rule-helpers-g11d-f`  
Implementation boundary: prototype-scoped helper APIs and source only; no runtime wiring.

## 1. Scope

Files added:
- `include/prototypes/senscope/SenscopePrototypeDirection.hpp`
- `src/prototypes/senscope/SenscopePrototypeDirection.cpp`
- `include/prototypes/senscope/SenscopePrototypeDigital.hpp`
- `src/prototypes/senscope/SenscopePrototypeDigital.cpp`
- `include/prototypes/senscope/SenscopePrototypeForce.hpp`
- `src/prototypes/senscope/SenscopePrototypeForce.cpp`
- `docs/project/G11D_F_PROTOTYPE_RULE_HELPERS_NOTES.md`

Intentionally not wired:
- no mode-selection entry;
- no `GameModeId` addition;
- no activation binding;
- no default config change;
- no runtime calls from `SenscopePrototype` shell;
- no changes to `Ultimate`, `CustomControllerMode`, `InputMode`, or `ControllerMode` behavior;
- no output report behavior changes;
- no protobuf/config schema changes;
- no persistence/configurator/transport changes;
- no evaluator/export/push workflow changes;
- no game-semantic logic.

## 2. Source/Design Basis

Design/docs basis:
- `docs/project/G7_CUSTOM_MODE_CONTROLLER_LOGIC_ENGINE_DESIGN.md`
- `docs/project/G10_COMPILE_TIME_CONTROLLER_LOGIC_PROTOTYPE_DESIGN.md`
- `docs/project/G11A_COMPILE_TIME_SCAFFOLD_NOTES.md`
- `docs/project/G11B_SENSCOPE_PROTOTYPE_MODE_SHELL_NOTES.md`
- `docs/project/G11C_LEFT_STICK_RESOLVER_PROTOTYPE_NOTES.md`

Source files inspected:
- `include/prototypes/senscope/SenscopePrototypeTypes.hpp`
- `src/prototypes/senscope/SenscopePrototypeValidation.cpp`
- `include/prototypes/senscope/SenscopePrototypeResolver.hpp`
- `src/prototypes/senscope/SenscopePrototypeResolver.cpp`
- `include/core/socd.hpp`
- `src/core/socd.cpp`
- `include/core/InputMode.hpp`
- `src/core/InputMode.cpp`
- `include/core/state.hpp`
- `include/modes/SenscopePrototype.hpp`
- `src/modes/SenscopePrototype.cpp`
- `platformio.ini`

## 3. G11d Direction Helper

Added request/result/status API in `SenscopePrototypeDirection.*`.

Request includes:
- `pre_socd_direction_roles` (`SenscopePrototypeDirectionRoleMask`)
- `opposite_policy` (`NeutralOnOpposite`, `LeftPriority`, `RightPriority`, `DownPriority`, `UpPriority`)

Result includes:
- `status`
- `resolved_direction_key` (`SenscopePrototypeDirectionKey`)
- `post_socd_direction_roles`
- `diagnostic_code`

SOCD boundary:
- helper is prototype-only normalization over already OR-composed direction roles;
- helper comment explicitly states this does not replace source-backed core SOCD algorithms (`include/core/socd.hpp`, `src/core/socd.cpp`).

Direction-key mapping implemented:
- neutral -> D5
- left -> D4
- right -> D6
- down -> D2
- up -> D8
- left+down -> D1
- right+down -> D3
- left+up -> D7
- right+up -> D9

Policy behavior:
- `NeutralOnOpposite`: opposing axis clears to neutral.
- `LeftPriority` / `RightPriority`: resolve horizontal; vertical opposites still neutral-on-opposite.
- `DownPriority` / `UpPriority`: resolve vertical; horizontal opposites still neutral-on-opposite.

Non-goals:
- no SOCD algorithm edits;
- no 2IP memory behavior in this batch;
- no runtime integration.

## 4. G11e Digital OR Helper

Added request/result/status API in `SenscopePrototypeDigital.*`.

Request includes:
- `direct_digital_output_mask`
- `active_physical_button_mask`

Result includes:
- `status`
- `composed_digital_output_mask`
- `triggered_rule_count`
- `diagnostic_code`

Digital rule handling:
- helper takes `SenscopePrototypeDigitalMultiOutputRulesArray` (or profile wrapper);
- starts from direct digital output mask;
- for each enabled rule, if all condition bits are held, OR `rule.outputs` into final mask;
- composition is OR-only in this batch (no suppression/pass-through).

Known-output boundary:
- unknown output bits are checked against `kSenscopePrototypeKnownDigitalOutputsMask`;
- unknown direct bits or unknown rule bits return diagnostic status.

Non-goals:
- no output suppression policy;
- no gameplay semantics;
- no runtime mode wiring.

## 5. G11f Force Override Helper

Added request/result/status API in `SenscopePrototypeForce.*`.

Request includes:
- `active_physical_button_mask`
- `post_socd_direction_key`
- optional horizontal X choices (`use_custom_values` + left/neutral/right X values)

Result includes:
- `status`
- `matched`
- `selected_rule_index`
- `left_stick_raw_coordinate`
- `digital_output_contribution`
- `diagnostic_code`

Priority behavior:
- enabled rules with fully-held `trigger_mask` are considered matches;
- highest-priority match wins;
- equal-priority highest matches return ambiguity diagnostic.

Fixed exact form:
- returns `fixed_coordinate` directly.

Forced-upward + post-SOCD horizontal form:
- always uses `rule.forced_upward_y` for `y`;
- derives horizontal from post-SOCD direction key (left/neutral/right classes);
- `x` comes from prototype placeholder constants unless custom choices are supplied.

Prototype constants:
- `kSenscopePrototypeForceHorizontalPlaceholderLeftX = 96`
- `kSenscopePrototypeForceHorizontalPlaceholderNeutralX = 128`
- `kSenscopePrototypeForceHorizontalPlaceholderRightX = 160`

These are explicitly documented as placeholder helper constants, not gameplay claims.

Digital contribution behavior:
- helper returns the selected rule’s `digital_outputs` mask contribution;
- no implicit Y output is added;
- no output beyond the rule’s configured mask is added.

Non-goals:
- no left-stick table resolver logic here;
- no runtime integration;
- no gameplay semantics.

## 6. Runtime Behavior

Runtime behavior changes: none.

Explicitly:
- helpers are not called by `SenscopePrototype` shell;
- helpers are not in mode selection;
- existing modes and runtime output paths are unchanged.

## 7. Verification

Commands run:
- `git status`
- `git diff --stat`
- `test -x ./scripts/pio-local.sh`
- `test -x ./scripts/build-glyph-mk6-quiet.sh`
- `./scripts/build-glyph-mk6-quiet.sh`

Build result:
- helper files compile as isolated scaffold code with no runtime wiring changes.

## 8. Recommended Next Batches

1. G11d-fR human review.
2. G11g isolated helper integration into `SenscopePrototype` shell (still not mode-selected).
3. G11h compile/build audit and docs normalization.
4. G11i optional lightweight unit-test strategy, if selected later.
