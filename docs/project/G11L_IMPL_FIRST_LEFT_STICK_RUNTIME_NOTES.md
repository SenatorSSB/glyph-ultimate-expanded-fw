# G11l-impl First Selected Left-Stick Runtime Behavior Notes

Status: implemented (minimal selected runtime behavior)
Branch: `proto/glyph-first-left-stick-runtime-g11l`
Runtime boundary: crossed with explicit user approval after G11o readiness gate

## 1. Scope

Files changed:
- `src/core/mode_selection.cpp`
- `src/modes/SenscopePrototype.cpp`
- `docs/project/G11L_IMPL_FIRST_LEFT_STICK_RUNTIME_NOTES.md`

Behavior enabled:
- compile-time gated manual/debug reachability path for `SenscopePrototype` selection
- selected-mode left-stick raw coordinate output from prototype table resolver

Behavior intentionally still disabled:
- default config activation
- `GameModeId`/protobuf path for `SenscopePrototype`
- digital output composition
- Force Up-B path
- right-stick/C-stick runtime behavior
- runtime modifier-mask complexity beyond `active_modifier_mask = 0`

## 2. User Approval

This batch crosses the runtime boundary only because explicit approval was provided for G11l-impl after G11o.

## 3. Reachability Path

`src/core/mode_selection.cpp` now includes:
- `constexpr bool kEnableSenscopePrototypeManualSelection = false;`
- debug-only manual chord helper using `LT1 + LT2 + MB1 + MB2`
- guarded call in `select_mode(...)` via `if constexpr (kEnableSenscopePrototypeManualSelection)`

Default behavior impact:
- when the flag is `false` (default), no runtime selection path can reach `SenscopePrototype`
- normal mode-selection by config activation bindings is unchanged

Boundary confirmation:
- no default config changes
- no `GameModeId` additions
- no protobuf/config schema edits
- no default activation binding wiring

## 4. Left-Stick Behavior

`src/modes/SenscopePrototype.cpp` selected behavior:
- `UpdateDigitalOutputs(...)` keeps `outputs.buttons = 0`
- `UpdateAnalogOutputs(...)` centers both sticks and zeroes triggers first
- direction roles are mapped from `InputState` directional fields:
  - left: `lf3`
  - right: `lf1`
  - down: `lf2`
  - up: `rf4`
- direction resolution uses `ResolveSenscopePrototypeDirection(...)`
- left-stick coordinate resolution uses `ResolveSenscopePrototypeExampleLeftStickRawCoordinate(...)`
- profile source is `GetSenscopePrototypeExampleProfile()`
- active modifier mask policy is fixed to `active_modifier_mask = 0`

SOCD/source note:
- `SenscopePrototype` receives post-remap/post-SOCD `InputState` from `ControllerMode::UpdateOutputs(...)` (`HandleRemap` then `HandleSocd` before mode output hooks)

Failure fallback:
- if direction or resolver status is not resolved, output stays neutral (`leftStickX = 128`, `leftStickY = 128`)
- right stick remains centered
- triggers remain zero
- digital remains zero

## 5. Disabled Behavior

Still disabled in G11l-impl:
- digital outputs beyond neutral
- Force Up-B contribution
- right-stick/C-stick non-neutral behavior
- analog trigger non-neutral behavior
- gameplay semantic labels/threshold logic

## 6. Runtime Safety Review

- existing Ultimate/CustomControllerMode selection behavior unchanged
- default selected behavior unchanged
- `SenscopePrototype` remains unreachable unless compile-time debug flag is manually enabled
- no hardware flashing or push-to-device workflow added

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
- status/diff: only in-scope files changed
- grep checks: no `MODE_SENSCOPE`/new `GameModeId`/default activation wiring was introduced
- wrapper checks: passed
- build: passed (`glyph_mk6 build passed`)

## 8. Recommended Next Batches

1. G11lR human/hardware review of selected-mode safety before any flashing.
2. G11m output behavior tests/diagnostics expansion.
3. G11n modifier-mask enablement (separate approval).
4. G11p Force Up-B only after separate explicit approval.
5. G11q digital outputs only after separate explicit approval.
