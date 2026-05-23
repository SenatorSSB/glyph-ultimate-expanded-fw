# G11k Mode-Selection Wiring Implementation Plan

Status: docs/design only, no implementation  
Date: 2026-05-23  
Branch: `design/glyph-mode-selection-wiring-g11k`

## 1. Title and status

G11k mode-selection wiring implementation plan for `SenscopePrototype`.

- Branch: `design/glyph-mode-selection-wiring-g11k`
- Batch type: docs/design only
- Runtime wiring in this batch: not implemented

## 2. Scope

Reviewed:
- repo contracts and boundaries:
  - `AGENTS.md`
  - `docs/project/ACTIVE_AGENT_QUEUE.md`
  - `docs/project/AGENT_OPERATING_CONTRACT.md`
  - `docs/project/AGENT_STOP_CONDITIONS.md`
  - `docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md`
- prior design/notes docs:
  - `docs/project/G7_CUSTOM_MODE_CONTROLLER_LOGIC_ENGINE_DESIGN.md`
  - `docs/project/G10_COMPILE_TIME_CONTROLLER_LOGIC_PROTOTYPE_DESIGN.md`
  - `docs/project/G11A_COMPILE_TIME_SCAFFOLD_NOTES.md`
  - `docs/project/G11B_SENSCOPE_PROTOTYPE_MODE_SHELL_NOTES.md`
  - `docs/project/G11C_LEFT_STICK_RESOLVER_PROTOTYPE_NOTES.md`
  - `docs/project/G11D_F_PROTOTYPE_RULE_HELPERS_NOTES.md`
  - `docs/project/G11G_H_SHELL_HELPER_INTEGRATION_AND_AUDIT_NOTES.md`
  - `docs/project/G11J_MODE_SELECTION_WIRING_DESIGN.md`
  - `docs/project/G11I_J_SELFTEST_AND_WIRING_DESIGN_NOTES.md`
- required source files:
  - `src/core/mode_selection.cpp`
  - `include/core/mode_selection.hpp`
  - `include/core/InputMode.hpp`
  - `include/core/ControllerMode.hpp`
  - `include/core/state.hpp`
  - `include/modes/SenscopePrototype.hpp`
  - `src/modes/SenscopePrototype.cpp`
  - `include/modes/Ultimate.hpp`
  - `src/modes/Ultimate.cpp`
  - `include/modes/CustomControllerMode.hpp`
  - `src/modes/CustomControllerMode.cpp`
  - `config/glyph/common/include/glyph_overrides.hpp`
  - `HAL/pico/include/config_defaults.hpp`
  - `platformio.ini`

This plan designs:
- a conservative first implementation shape for future mode-selection wiring preparation;
- risk boundaries before any runtime reachability is introduced.

This plan intentionally does not implement:
- runtime mode wiring;
- any `GameModeId`, protobuf, or default-config changes;
- activation bindings;
- output behavior changes;
- gameplay semantic logic.

## 3. Current source inventory

Current static mode instances (`src/core/mode_selection.cpp`):
- `melee_mode`
- `projectm_mode`
- `ultimate_mode`
- `fgc_mode`
- `rivals_mode`
- `rivals2_mode`
- `keyboard_mode`
- `custom_mode`
- `s64_mode`

Current `set_mode` overload surface:
- `set_mode(CommunicationBackend*, ControllerMode*)`
- `set_mode(CommunicationBackend*, KeyboardMode*)`
- `set_mode(CommunicationBackend*, GameModeConfig&, Config&)`
- `set_mode(CommunicationBackend*, GameModeId, Config&)`

Current selection path:
- `select_mode(...)` iterates `config.game_mode_configs_count`;
- compares current inputs against `mode_activation_masks[i]`;
- when matched, dispatches `set_mode(...)` for each backend.

Current activation binding setup:
- `setup_mode_activation_bindings(...)` builds `mode_activation_masks` from each `GameModeConfig.activation_binding` via `make_button_mask(...)`.

Current config/default relationship:
- default game mode lists and bindings are in:
  - `config/glyph/common/include/glyph_overrides.hpp`
  - `HAL/pico/include/config_defaults.hpp`
- backend defaults (`default_mode_config`) are also configured there.

Where `SenscopePrototype` is currently absent:
- no include/static instance/case in `src/core/mode_selection.cpp`;
- no mode entry in inspected default config tables;
- no activation bindings or default backend selection path referencing it.

## 4. Wiring risk classification

| Change area | Risk level | Allowed in next implementation (G11k-impl) | Stop condition |
| --- | --- | --- | --- |
| Static instance only (`SenscopePrototype` object in mode-selection TU) | Medium | Yes, but only after constructor self-test is gated/removed and only if unreachable by default | Stop if static instance causes unapproved runtime side effects |
| Add `#include "modes/SenscopePrototype.hpp"` in `mode_selection.cpp` | Low | Yes (compile-visible only) | Stop if include path implies immediate reachability changes |
| Add `set_mode` case and/or new `GameModeId` path | High | No (defer) | Stop and require explicit approval |
| Add activation binding entry | High | No (defer) | Stop and require explicit approval |
| Add default config entry / default backend mode selection | High | No (defer) | Stop and require explicit approval |
| Protobuf/schema edits (`GameModeId` enum, config schema surfaces) | High | No (defer) | Stop and require explicit approval |
| Constructor self-test behavior in `SenscopePrototype` | High (for future wiring) | Must be addressed first | Stop if runtime wiring is attempted before gating/removal |

## 5. Recommended implementation strategy

Stage 1 (first implementation target, safest):
- gate or remove constructor self-test before any runtime reachability;
- optionally add compile-visible `SenscopePrototype` static instance only if it remains unreachable by default;
- do not add `GameModeId`;
- do not add activation binding;
- do not change defaults.

Stage 2 (after review/approval):
- choose an explicit manual/debug activation path;
- keep activation explicit and non-default.

Stage 3 (later, separately approved):
- consider `GameModeId`/protobuf/default-config wiring only after dedicated review;
- evaluate migration/config impacts separately.

## 6. Constructor self-test decision

Current source fact:
- `SenscopePrototype::SenscopePrototype()` calls `RunPrototypeStaticSmokeCheck()`;
- that helper calls `RunSenscopePrototypeSelfTest()`.

Before runtime wiring:
- constructor self-test should be gated behind a compile-time debug constant or removed from constructor flow.

Recommended implementation choice:
- preferred: compile-time debug guard that defaults off for normal builds;
- acceptable alternative: remove constructor call and invoke self-test only from explicit debug/test pathways.

Why:
- static instantiation in mode-selection would otherwise run self-test implicitly at construction time;
- this creates hidden runtime cost/side effects risk before explicit activation behavior is approved.

## 7. Proposed exact implementation diff for G11k-impl

This section describes future changes only. Do not apply in G11k-design.

Recommended:
1. `src/modes/SenscopePrototype.cpp`
- gate or remove constructor self-test call.
- keep default behavior unreachable and inert.

2. `src/core/mode_selection.cpp`
- optionally add `#include "modes/SenscopePrototype.hpp"`;
- optionally add a static `SenscopePrototype` instance only;
- do not add any `set_mode` switch case or selection path to make it reachable.

Optional:
3. `include/modes/SenscopePrototype.hpp`
- no change unless a constructor-gating declaration is needed.

4. docs updates
- add implementation notes/audit doc confirming no runtime reachability.

## 8. Non-goals for G11k-impl

- no `GameModeId` additions;
- no config/default activation path;
- no output behavior changes;
- no gameplay semantics;
- no export/push workflow;
- no hardware flashing.

## 9. Verification plan for future implementation

Planned checks:
- `git diff --stat`
- `rg "MODE_SENSCOPE|SenscopePrototype|mode_id = MODE_" include src config HAL` (confirm scope)
- `rg "activation_binding|default_mode_config" config/glyph/common/include/glyph_overrides.hpp HAL/pico/include/config_defaults.hpp` (confirm unchanged bindings/defaults)
- `rg "GameModeId|enum GameModeId|config.proto|\\.proto" include src config HAL` (confirm no schema/protobuf edits in scope)
- `./scripts/build-glyph-mk6-quiet.sh` (only when code is touched)
- manual inspection of `src/core/mode_selection.cpp` diff to confirm no reachability path, no activation binding wiring, no default config edits.

## 10. Rollback/containment plan

Because Stage 1 keeps mode unreachable by default:
- rollback is confined to removing static instance/include and constructor-gating edits;
- no config migration is involved;
- no `GameModeId`/protobuf/default-config rollback path is needed in Stage 1.

## 11. Open questions

- Which manual/debug activation path (if any) should be approved for Stage 2?
- Should `SenscopePrototype` ever receive a dedicated `GameModeId`?
- Should constructor self-test remain debug-only long-term or be moved fully out of constructor flow?
- When should first real runtime output behavior work begin?

## 12. Recommended next batches

1. G11k-impl:
- apply minimal constructor self-test gating/removal;
- optionally add unreachable static instance;
- require explicit approval before execution.

2. G11l-design:
- design first runtime output behavior path only.

3. G11l-impl:
- first runtime output behavior only after explicit approval.

4. G11m:
- test strategy expansion if needed.

## 13. Verification

Commands run for this docs/design batch:
- `git checkout configurator`
- `git pull origin configurator`
- `git status`
- `git branch --show-current`
- `git checkout -b design/glyph-mode-selection-wiring-g11k`
- `sed -n '1,260p' <required files>`
- `rg "<pattern>" <required paths>`

Result:
- docs-only planning completed;
- no runtime wiring implemented;
- no firmware code behavior changed in this batch.
