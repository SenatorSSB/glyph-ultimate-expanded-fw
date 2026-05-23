# G11a Minimal Compile-Time Scaffold Notes

Status: implemented (prototype scaffold only)  
Branch: `proto/glyph-compile-time-scaffold-g11a`  
Implementation boundary: compile-time data-structure scaffold and validation helper only. No runtime behavior wiring.

## 1. Scope

Files added:
- `include/prototypes/senscope/SenscopePrototypeTypes.hpp`
- `src/prototypes/senscope/SenscopePrototypeValidation.cpp`
- `docs/project/G11A_COMPILE_TIME_SCAFFOLD_NOTES.md`

Intentionally not wired:
- no mode-selection entry;
- no active mode instantiation;
- no changes to `Ultimate` or `CustomControllerMode` behavior;
- no changes to `InputMode` or `ControllerMode` behavior;
- no output report changes;
- no protobuf/config schema changes;
- no persistence/configurator transport changes;
- no export/push workflow.

## 2. User-Approved Prototype Parameters

This scaffold implements the approved G11a prototype constraints:
- left-stick only;
- prototype mode name `SenscopePrototype`;
- 3 modifier roles;
- explicit direction-table support with direction `5` entry support;
- both Force Up-B forms:
  - fixed exact coordinate;
  - forced upward Y with post-SOCD horizontal X;
- one digital multi-output rule shape (example includes `B+Y`);
- one held Layer/Mode role map shape;
- `static_assert` invariants plus a runtime/startup-usable validation helper.

## 3. Source/Design Basis

Design basis documents:
- `docs/project/G7_CUSTOM_MODE_CONTROLLER_LOGIC_ENGINE_DESIGN.md`
- `docs/project/G9_CONFIG_CAPACITY_AND_TABLE_STORAGE_INVENTORY.md`
- `docs/project/G10_COMPILE_TIME_CONTROLLER_LOGIC_PROTOTYPE_DESIGN.md`

Required source files inspected:
- `include/core/state.hpp`
- `include/core/InputMode.hpp`
- `src/core/InputMode.cpp`
- `include/core/ControllerMode.hpp`
- `src/core/ControllerMode.cpp`
- `include/core/socd.hpp`
- `src/core/socd.cpp`
- `include/modes/Ultimate.hpp`
- `src/modes/Ultimate.cpp`
- `include/modes/CustomControllerMode.hpp`
- `src/modes/CustomControllerMode.cpp`
- `platformio.ini`

## 4. Scaffold Structure

`include/prototypes/senscope/SenscopePrototypeTypes.hpp`:
- Defines prototype-scoped types only (`SenscopePrototype*` names).
- Defines G11a constants (direction count, modifier count, conservative max table sizes).
- Defines requested data-shape concepts:
  - `SenscopePrototypeRawCoord`
  - `SenscopePrototypeDirectionKey`
  - `SenscopePrototypeDigitalOutputMask`
  - `SenscopePrototypePhysicalButtonMask`
  - `SenscopePrototypeLogicalRoleMask`
  - `SenscopePrototypeDirectionRoleMask`
  - `SenscopePrototypeModifierId`
  - `SenscopePrototypeModifierCombinationMask`
  - `SenscopePrototypeComboProfile`
  - `SenscopePrototypeDirectionalStickTable9`
  - `SenscopePrototypeForceStickOverrideRule`
  - `SenscopePrototypeDigitalMultiOutputRule`
  - `SenscopePrototypeLayerRoleMap`
  - `SenscopePrototypeProfile`
  - validation diagnostic/result types
- Adds `static_assert` invariants:
  - direction count is 9;
  - modifier count is 3;
  - modifier mask width covers modifier count;
  - table array sizes match declared constants.

`src/prototypes/senscope/SenscopePrototypeValidation.cpp`:
- Implements an isolated, pure validation helper:
  - `ValidateSenscopePrototypeProfile(...)`
- Adds a compile-time-only example profile:
  - `GetSenscopePrototypeExampleProfile()`
  - mode name `SenscopePrototype`
  - left-stick tables with direction-5 entries
  - two Force Up-B rule forms
  - one `B+Y` digital multi-output rule
  - one held Layer/Mode role map
- No references from mode selection or runtime mode update paths.

## 5. Validation Boundaries

Validation currently checks:
- modifier-role count and left-stick-only guardrails for the prototype profile;
- modifier mask range against the selected modifier count;
- combo left-stick table index and table enabled-ness;
- direction table has explicit present/absent flags and at least one marked entry;
- equal-priority exact combo duplicates;
- equal-priority subset ambiguity for matching combo fallback;
- undefined combo fallback reported as TODO/UNKNOWN diagnostic where reachability cannot be proven from this scaffold alone;
- force-rule structural validity (non-empty trigger, non-empty digital outputs, required post-SOCD horizontal policy for the forced-upward form);
- equal-priority same-target force rule trigger conflict;
- digital multi-output structural validity (condition/output non-empty, known output bits only);
- layer-role map structural validity (held condition present, role output present).

Validation limitations intentionally preserved:
- Raw coordinate byte range is structurally enforced by `uint8_t`; no additional numeric range transform is needed in this scaffold.
- No runtime active-combo reachability proof is attempted because button-to-role expansion and mode wiring are intentionally out of scope for G11a.
- No resolver/output behavior or semantics are validated here.

## 6. Runtime Behavior

Runtime behavior changes: none.

Explicitly:
- not wired to mode selection;
- not wired to active output paths;
- not wired to persistence/configurator/protobuf flows.

## 7. Verification

Commands run:
- `git status`
- `git diff --stat`
- `test -x ./scripts/pio-local.sh`
- `test -x ./scripts/build-glyph-mk6-quiet.sh`
- `./scripts/build-glyph-mk6-quiet.sh`

Result:
- scaffold compiles with existing build flow (no runtime wiring introduced).

## 8. Recommended Next Batches

1. G11aR human review of scaffold naming, limits, and validation diagnostics.
2. G11b isolated custom mode shell (after explicit approval).
3. G11c left-stick resolver prototype (after explicit approval).
