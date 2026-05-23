# G11g-h Shell Helper Integration and Audit Notes

Status: implemented (compile-visible shell helper integration only)  
Date: 2026-05-23  
Branch: `proto/glyph-shell-helper-integration-g11g-h`  
Implementation boundary: integrate isolated G11c/G11d-f prototype helpers into the inactive `SenscopePrototype` shell without runtime wiring.

## 1. Scope

Files changed:
- `include/modes/SenscopePrototype.hpp`
- `src/modes/SenscopePrototype.cpp`
- `docs/project/G11G_H_SHELL_HELPER_INTEGRATION_AND_AUDIT_NOTES.md`
- `docs/project/ACTIVE_AGENT_QUEUE.md` (queue normalization)

Intentionally not wired:
- no `mode_selection` changes;
- no `GameModeId` additions;
- no activation bindings;
- no default config changes;
- no runtime output integration for prototype helper results;
- no `Ultimate` behavior changes;
- no `CustomControllerMode` behavior changes;
- no `InputMode` / `ControllerMode` behavior changes;
- no output report behavior changes;
- no protobuf/config schema changes;
- no persistence/configurator path changes;
- no export/push workflows;
- no evaluator logic.

## 2. Source/Design Basis

Design notes used:
- `docs/project/G7_CUSTOM_MODE_CONTROLLER_LOGIC_ENGINE_DESIGN.md`
- `docs/project/G10_COMPILE_TIME_CONTROLLER_LOGIC_PROTOTYPE_DESIGN.md`
- `docs/project/G11A_COMPILE_TIME_SCAFFOLD_NOTES.md`
- `docs/project/G11B_SENSCOPE_PROTOTYPE_MODE_SHELL_NOTES.md`
- `docs/project/G11C_LEFT_STICK_RESOLVER_PROTOTYPE_NOTES.md`
- `docs/project/G11D_F_PROTOTYPE_RULE_HELPERS_NOTES.md`

Operating boundary docs reviewed:
- `AGENTS.md`
- `docs/project/ACTIVE_AGENT_QUEUE.md`
- `docs/project/AGENT_OPERATING_CONTRACT.md`
- `docs/project/AGENT_STOP_CONDITIONS.md`
- `docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md`

Source files inspected for this batch:
- `include/modes/SenscopePrototype.hpp`
- `src/modes/SenscopePrototype.cpp`
- `include/prototypes/senscope/SenscopePrototypeTypes.hpp`
- `src/prototypes/senscope/SenscopePrototypeValidation.cpp`
- `include/prototypes/senscope/SenscopePrototypeResolver.hpp`
- `src/prototypes/senscope/SenscopePrototypeResolver.cpp`
- `include/prototypes/senscope/SenscopePrototypeDirection.hpp`
- `src/prototypes/senscope/SenscopePrototypeDirection.cpp`
- `include/prototypes/senscope/SenscopePrototypeDigital.hpp`
- `src/prototypes/senscope/SenscopePrototypeDigital.cpp`
- `include/prototypes/senscope/SenscopePrototypeForce.hpp`
- `src/prototypes/senscope/SenscopePrototypeForce.cpp`
- `src/core/mode_selection.cpp`
- `platformio.ini`

## 3. Helper Integration Summary

Integrated compile-visible references in `SenscopePrototype` shell:
- validation helper: `ValidateSenscopePrototypeProfile(GetSenscopePrototypeExampleProfile())`
- direction helper: `ResolveSenscopePrototypeDirection(...)`
- left-stick resolver helper: `ResolveSenscopePrototypeLeftStickRawCoordinate(...)`
- digital OR helper: `ComposeSenscopePrototypeProfileDigitalOutputs(...)`
- force override helper: `ResolveSenscopePrototypeProfileForceOverride(...)`

Smoke/audit path shape:
1. validate example prototype profile;
2. resolve a sample pre-SOCD direction-role mask to a direction key;
3. resolve a sample left-stick table coordinate for a sample modifier mask;
4. compose sample direct+rule digital outputs;
5. resolve a sample Force Up-B rule contribution.

Constructor behavior:
- `SenscopePrototype` constructor now calls `RunPrototypeStaticSmokeCheck()`.
- The helper returns `bool` and has no external side effects.
- This remains isolated because `SenscopePrototype` is still not registered or selected in mode selection.

## 4. Runtime Behavior Boundary

Runtime behavior changes: none.

Explicitly:
- `SenscopePrototype` is not in `src/core/mode_selection.cpp`;
- `SenscopePrototype` is not selected by any existing mode activation path;
- existing mode behavior (`Ultimate`, `CustomControllerMode`, etc.) is unchanged;
- `UpdateDigitalOutputs` remains inert (`outputs.buttons = 0`);
- `UpdateAnalogOutputs` remains inert (left/right sticks centered, analog triggers neutral);
- no prototype helper output is written into active runtime `OutputState` paths for selected modes.

## 5. Build/Test Audit

Commands run:
- `git status`
- `git diff --stat`
- `find . -maxdepth 4 -type f | rg '/(test|tests|spec)/|(_test\.|\.test\.|\.spec\.)|package.json|pytest|CMakeLists|platformio.ini' || true`
- `test -x ./scripts/pio-local.sh`
- `test -x ./scripts/build-glyph-mk6-quiet.sh`
- `./scripts/build-glyph-mk6-quiet.sh`

Results:
- wrapper checks passed (`./scripts/pio-local.sh` and `./scripts/build-glyph-mk6-quiet.sh` executable);
- build passed (`glyph_mk6` success);
- no lightweight, repo-local prototype unit-test convention for these new isolated helpers was found from the required test-pattern scan in this batch.

## 6. Risk Review

- Compile-visible but inactive code risk: helper paths now compile-reference from shell code, but runtime activation remains blocked by absent mode-selection wiring.
- Constructor smoke call caveat: if a future batch wires mode selection, this smoke helper would execute on shell construction unless removed or gated then.
- No mode-selection wiring was introduced in this batch.
- No runtime output behavior wiring was introduced in this batch.

## 7. Recommended Next Batches

1. G11g-hR human review of shell integration boundaries and smoke helper expectations.
2. G11i optional lightweight prototype helper test strategy (if/when a safe convention is approved).
3. G11j isolated mode-selection wiring design docs only.
4. G11k mode-selection wiring implementation only after explicit approval.
5. G11l first runtime output behavior only after explicit approval.
