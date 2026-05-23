# G11k-impl Minimal Mode-Selection Preparation Notes

Status: implemented (minimal, boundary-safe)  
Date: 2026-05-23  
Branch: `proto/glyph-mode-selection-prep-g11k-impl`  
Implementation boundary: compile-visible preparation only; `SenscopePrototype` remains unreachable by normal runtime mode selection.

## 1. Title and status

This batch implements the approved G11k-impl minimal preparation.

No user-facing mode activation was added.

## 2. Scope

Files changed:
- `src/modes/SenscopePrototype.cpp`
- `src/core/mode_selection.cpp`
- `docs/project/G11K_IMPL_MODE_SELECTION_PREP_NOTES.md`
- `docs/project/ACTIVE_AGENT_QUEUE.md` (minimal queue status update)

Intentionally not wired:
- no `GameModeId` addition;
- no `set_mode` path for `SenscopePrototype`;
- no activation binding changes;
- no default config changes;
- no protobuf/config schema changes;
- no output report behavior changes;
- no persistence/configurator/export/push workflow changes;
- no evaluator code;
- no gameplay semantic changes.

## 3. Constructor self-test decision

Decision: gated (not removed).

`src/modes/SenscopePrototype.cpp` now defines:
- `constexpr bool kRunSenscopePrototypeConstructorSelfTest = false;`

The constructor now uses:
- `if constexpr (kRunSenscopePrototypeConstructorSelfTest) { (void)RunPrototypeStaticSmokeCheck(); }`

Default normal-build behavior is now no constructor self-test execution.

Why:
- avoids implicit constructor-time self-test execution before any approved runtime activation path;
- keeps `RunPrototypeStaticSmokeCheck()` available for explicit future debug/test bring-up paths.

## 4. Mode-selection preparation

Decision: added optional compile-visible static instance.

`src/core/mode_selection.cpp` now has:
- include: `#include "modes/SenscopePrototype.hpp"`
- static instance: `SenscopePrototype senscope_prototype_mode;`

Boundary confirmation:
- no new `set_mode(...)` case;
- no `GameModeId` additions;
- no activation/default wiring;
- no selection logic changes.

Result: compile-visible preparation only; mode remains unreachable/unselected by default.

## 5. Boundary verification

Verified in this batch:
- no `GameModeId` additions;
- no config/protobuf edits;
- no activation binding changes;
- no default config changes;
- no output behavior changes for selected modes;
- no `Ultimate`, `CustomControllerMode`, `InputMode`, or `ControllerMode` behavior changes.

## 6. Runtime behavior

Selected runtime behavior changes: none.

`SenscopePrototype` remains unreachable by normal mode selection because no mode-id/config/selection path was added.

## 7. Verification

Commands run:
- `git status`
- `git diff --stat`
- `rg "SenscopePrototype" include src docs/project`
- `rg "MODE_SENSCOPE|SENSCOPE|GameModeId|mode_id" include src config HAL`
- `rg "activation_binding|default_mode_config" config/glyph/common/include/glyph_overrides.hpp HAL/pico/include/config_defaults.hpp`
- `test -x ./scripts/pio-local.sh`
- `test -x ./scripts/build-glyph-mk6-quiet.sh`
- `./scripts/build-glyph-mk6-quiet.sh`

Results:
- wrapper checks passed;
- grep/diff checks confirm no mode reachability wiring path was added;
- build passed: `glyph_mk6 build passed`.

## 8. Recommended next batches

1. G11k-implR human review of boundary and reachability.
2. G11l-design first output behavior design (docs/design only).
3. G11l-impl first output behavior only after explicit approval.
