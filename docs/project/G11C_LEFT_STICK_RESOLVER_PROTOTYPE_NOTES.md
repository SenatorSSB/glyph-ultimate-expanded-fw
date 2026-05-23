# G11c Left-Stick Resolver Prototype Notes

Status: implemented (isolated prototype helper only)  
Branch: `proto/glyph-left-stick-resolver-g11c`  
Implementation boundary: isolated resolver helper only; no runtime behavior wiring

## 1. Scope

Files added:
- `include/prototypes/senscope/SenscopePrototypeResolver.hpp`
- `src/prototypes/senscope/SenscopePrototypeResolver.cpp`
- `docs/project/G11C_LEFT_STICK_RESOLVER_PROTOTYPE_NOTES.md`

Intentionally not wired:
- no `mode_selection` changes;
- no `GameModeId` additions;
- no mode activation bindings;
- no default config changes;
- no `Ultimate` behavior changes;
- no `CustomControllerMode` behavior changes;
- no `InputMode` / `ControllerMode` behavior changes;
- no output report behavior changes;
- no protobuf/config schema changes;
- no persistence/configurator/transport path changes;
- no evaluator logic;
- no export/push workflow.

## 2. Source/Design Basis

Design/docs basis:
- `docs/project/G7_CUSTOM_MODE_CONTROLLER_LOGIC_ENGINE_DESIGN.md`
- `docs/project/G10_COMPILE_TIME_CONTROLLER_LOGIC_PROTOTYPE_DESIGN.md`
- `docs/project/G11A_COMPILE_TIME_SCAFFOLD_NOTES.md`
- `docs/project/G11B_SENSCOPE_PROTOTYPE_MODE_SHELL_NOTES.md`

Required source files inspected for this batch:
- `include/prototypes/senscope/SenscopePrototypeTypes.hpp`
- `src/prototypes/senscope/SenscopePrototypeValidation.cpp`
- `include/modes/SenscopePrototype.hpp`
- `src/modes/SenscopePrototype.cpp`
- `include/core/state.hpp`
- `include/core/ControllerMode.hpp`
- `src/core/ControllerMode.cpp`
- `platformio.ini`

## 3. Resolver Structure

Header:
- `include/prototypes/senscope/SenscopePrototypeResolver.hpp`
- defines prototype-scoped resolver API only (`senscope::prototype` + `SenscopePrototype*` names)
- defines:
  - request type (`SenscopePrototypeResolverRequest`)
  - result type (`SenscopePrototypeResolverResult`)
  - resolver status enum (`SenscopePrototypeResolverStatus`)
  - resolver diagnostic enum (`SenscopePrototypeResolverDiagnosticCode`)
  - fallback policy enum (`SenscopePrototypeResolverFallbackPolicy`)
  - profile-based and example-profile helper entry points

Source:
- `src/prototypes/senscope/SenscopePrototypeResolver.cpp`
- implements isolated left-stick raw-coordinate resolution
- no references from mode-selection or runtime mode update paths

## 4. Selection Algorithm

Resolver behavior for combo selection:
1. Validate the prototype profile using `ValidateSenscopePrototypeProfile(profile)`.
2. Check request direction key range `1..9`; map to table index `0..8`.
3. Try exact enabled combo profile match (`combo.modifiers == active_modifier_mask`).
4. If exact match is absent and fallback policy allows subset fallback, select the highest-priority enabled subset where:
   - `(combo.modifiers & active_modifier_mask) == combo.modifiers`
5. If multiple candidates share the best priority at the selected stage, return ambiguous status.
6. If no candidate exists, return no-matching-combo status.
7. Resolve `left_stick_table_index` and direction entry presence, then return raw coordinate.

## 5. Behavior Boundary

This resolver intentionally:
- receives a post-SOCD `DirectionKey` request input;
- does not implement SOCD;
- does not implement Force Up-B rule resolution;
- does not implement digital multi-output composition;
- does not implement right-stick/C-stick resolution;
- does not wire into runtime mode logic;
- does not add gameplay semantics.

## 6. Validation Relationship

Validation choice:
- resolver calls `ValidateSenscopePrototypeProfile(profile)` internally before lookup.

Defensive checks retained in resolver even with prior validation:
- direction-key range check (`1..9`);
- selected combo index defensive check;
- selected table-index range check;
- table enabled check;
- direction entry presence check.

## 7. Runtime Behavior

Runtime behavior changes: none.

Explicitly:
- resolver is not called by `SenscopePrototype` mode shell;
- resolver is not referenced in `mode_selection`;
- existing modes are unchanged.

## 8. Verification

Commands run:
- `git status`
- `git diff --stat`
- `test -x ./scripts/pio-local.sh`
- `test -x ./scripts/build-glyph-mk6-quiet.sh`
- `./scripts/build-glyph-mk6-quiet.sh`

Result:
- build compiles with isolated G11c resolver helper present and no runtime wiring changes.

## 9. Recommended Next Batches

1. G11cR human review of resolver API shape and ambiguity policy.
2. G11d direction/SOCD adapter boundary helper (still isolated).
3. G11e digital OR-composition helper.
4. G11f Force Up-B rule resolver.
5. G11g shell integration while still not mode-selected.
