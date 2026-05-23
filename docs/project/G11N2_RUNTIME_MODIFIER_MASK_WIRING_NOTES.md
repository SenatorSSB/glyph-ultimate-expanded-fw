# G11n-impl2 Runtime Modifier-Mask Wiring Notes

Status: implemented  
Branch: `proto/glyph-runtime-modifier-mask-g11n2`

## 1. Scope and files changed

This batch wires the isolated G11n1 modifier-mask helper into the already debug-gated `SenscopePrototype`
selected runtime path only.

Files changed:
- `src/modes/SenscopePrototype.cpp`
- `docs/project/G11N2_RUNTIME_MODIFIER_MASK_WIRING_NOTES.md`
- `docs/project/ACTIVE_AGENT_QUEUE.md` (minimal queue stop-point update)

## 2. Source-backed binding decision

Prototype modifier bindings wired in this batch:
- modifier bit 0 (X) = `inputs.rf2`
- modifier bit 1 (Z/R-style) = `inputs.rf3`
- modifier bit 2 (Left Stick Up) = `inputs.rf4`

Source basis from current Ultimate mode:
- `outputs.x = inputs.rf2`
- `outputs.buttonR = inputs.rf3`
- `outputs.leftStickUp = inputs.rf4`

Notes:
- `outputs.buttonL` is currently commented out in Ultimate source.
- `inputs.lf4` maps to `triggerLDigital`, not the intended Z binding, so `lf4` is intentionally not used.
- `rf3` is treated as Z/R-style in this prototype batch because the active Ultimate mapping uses `outputs.buttonR = inputs.rf3`.

## 3. Runtime behavior change

Selected `SenscopePrototype` runtime behavior now builds `active_modifier_mask` through
`BuildSenscopePrototypeActiveModifierMask(...)` with local compile-time bindings.

Previously:
- `active_modifier_mask` was fixed to `0`.

Now:
- `active_modifier_mask` is derived from `rf2`/`rf3`/`rf4` via the G11n1 helper and fed into
  the existing left-stick resolver request path.

If modifier helper status is invalid:
- selected runtime fails closed to neutral output (no table coordinate write).
- this is conservative fallback and is not expected in normal builds with compile-time local bindings.

## 4. Disabled behavior preserved

Unchanged by this batch:
- digital output behavior remains neutral-only (`outputs.buttons = 0`)
- Force Up-B remains disabled
- right-stick/C-stick runtime behavior remains neutral/centered
- triggers remain neutral (`0`)
- mode-selection debug gate/default reachability behavior unchanged
- default config unchanged

## 5. Safety checks

Boundary confirmations:
- no `kEnableSenscopePrototypeManualSelection` default change
- no `GameModeId` additions
- no activation binding or default config changes
- no `InputMode`/`ControllerMode` behavior changes
- no protobuf/config schema changes
- no output-report path expansion beyond selected runtime modifier-mask input

## 6. Verification commands and results

- `git status`: pass
- `git diff --stat`: pass
- `rg "active_modifier_mask|SenscopePrototypeModifier|rf2|rf3|rf4|lf4|kEnableSenscopePrototypeManualSelection" include src docs/project`: pass
- `rg "MODE_SENSCOPE|SENSCOPE|GameModeId|mode_id" include src config HAL`: pass
- `rg "activation_binding|default_mode_config" config/glyph/common/include/glyph_overrides.hpp HAL/pico/include/config_defaults.hpp`: pass
- `test -x ./scripts/pio-local.sh`: pass
- `test -x ./scripts/build-glyph-mk6-quiet.sh`: pass
- `./scripts/build-glyph-mk6-quiet.sh`: pass

## 7. Recommended next batches

1. Human review/inspection of G11n2 selected runtime behavior before any further runtime expansion.
2. G11p Force Up-B design/implementation only after explicit approval.
3. G11q digital output behavior only after explicit approval.
4. G11s real binding UX/config discussion later (separate approval and boundary review).
