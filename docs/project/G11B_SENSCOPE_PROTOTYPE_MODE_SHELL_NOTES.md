# G11b Isolated SenscopePrototype Mode Shell Notes

Status: implemented (isolated shell only)  
Branch: `proto/glyph-senscope-mode-shell-g11b`  
Implementation boundary: build-visible class shell only; no runtime wiring.

## 1. Scope

Files added:
- `include/modes/SenscopePrototype.hpp`
- `src/modes/SenscopePrototype.cpp`
- `docs/project/G11B_SENSCOPE_PROTOTYPE_MODE_SHELL_NOTES.md`

Intentionally not wired:
- no `mode_selection` entry;
- no new `GameModeId`;
- no activation binding;
- no default-config changes;
- no changes to `Ultimate`, `CustomControllerMode`, `InputMode`, or `ControllerMode` behavior;
- no output report changes;
- no protobuf/config schema changes;
- no persistence/configurator path changes;
- no export/push workflow;
- no evaluator logic.

## 2. Source and Design Basis

Design references:
- `docs/project/G7_CUSTOM_MODE_CONTROLLER_LOGIC_ENGINE_DESIGN.md`
- `docs/project/G10_COMPILE_TIME_CONTROLLER_LOGIC_PROTOTYPE_DESIGN.md`
- `docs/project/G11A_COMPILE_TIME_SCAFFOLD_NOTES.md`

Supporting inventory:
- `docs/project/G9_CONFIG_CAPACITY_AND_TABLE_STORAGE_INVENTORY.md`

Source files inspected for this batch:
- `include/core/state.hpp`
- `include/core/InputMode.hpp`
- `src/core/InputMode.cpp`
- `include/core/ControllerMode.hpp`
- `src/core/ControllerMode.cpp`
- `include/modes/Ultimate.hpp`
- `src/modes/Ultimate.cpp`
- `include/modes/CustomControllerMode.hpp`
- `src/modes/CustomControllerMode.cpp`
- `include/prototypes/senscope/SenscopePrototypeTypes.hpp`
- `src/prototypes/senscope/SenscopePrototypeValidation.cpp`
- `src/core/mode_selection.cpp`
- `platformio.ini`

## 3. Shell Structure

`include/modes/SenscopePrototype.hpp`:
- declares `SenscopePrototype` as a `ControllerMode` subclass, matching the existing controller-mode pattern;
- documents boundary comments: experimental shell only, not mode-selected, no runtime behavior unless explicitly instantiated later, and no game semantics;
- declares only the minimal override surface required by `ControllerMode` (`UpdateDigitalOutputs`, `UpdateAnalogOutputs`);
- declares a private helper that references the G11a validation API shape.

`src/modes/SenscopePrototype.cpp`:
- includes G11a prototype types/validation declarations via `prototypes/senscope/SenscopePrototypeTypes.hpp`;
- keeps digital behavior inert by writing neutral digital outputs (`outputs.buttons = 0`);
- keeps analog behavior inert by centering sticks and zeroing analog triggers;
- references G11a validation through a private helper:
  - `ValidateSenscopePrototypeProfile(GetSenscopePrototypeExampleProfile())`
  - called from the mode constructor, with no external side effects.

## 4. Runtime Behavior

Runtime behavior changes: none.

Explicitly:
- `SenscopePrototype` is not instantiated by default;
- `SenscopePrototype` is not registered in `src/core/mode_selection.cpp`;
- no activation binding was added;
- no default config was changed;
- no output report behavior changed.

## 5. Validation / Scaffold Relation

This G11b shell is intentionally tied only to the G11a compile-time scaffold surface:
- it references the prototype data shape and validation declarations in `SenscopePrototypeTypes.hpp`;
- it reuses the G11a validation helper path in a local class helper;
- it does not add runtime resolver behavior, gameplay semantics, or evaluator behavior.

## 6. Verification

Commands run:
- `git status`
- `git diff --stat`
- `test -x ./scripts/pio-local.sh`
- `test -x ./scripts/build-glyph-mk6-quiet.sh`
- `./scripts/build-glyph-mk6-quiet.sh`

Result:
- build compiles with the isolated shell present and no mode-selection wiring.

## 7. Recommended Next Batches

1. G11bR human review of shell boundaries and naming.
2. G11c isolated left-stick table resolver prototype after explicit approval.
3. G11d isolated mode-selection wiring behind explicit approval, if needed later.
