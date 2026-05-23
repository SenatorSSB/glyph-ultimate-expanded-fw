# G11m2 Runtime Debug-Path Audit

Status: completed (docs-only audit)  
Branch: `proto/glyph-runtime-audit-modifier-design-g11m2-n-r`  
Boundary: no runtime expansion beyond existing G11l debug-gated selected left-stick table path.

## 1. Current G11l runtime path summary

- `kEnableSenscopePrototypeManualSelection` is `false` by default in `src/core/mode_selection.cpp`.
- Manual debug chord selection exists only under compile-time guarded path (`if constexpr` on that flag).
- No `GameModeId` / protobuf / default-config activation path for `SenscopePrototype` is added.
- When manually selected in a debug-enabled build, runtime output scope is left-stick table resolution only.

## 2. Safety properties

- Default runtime reachability remains off.
- Normal selected behavior for existing modes is unchanged.
- No digital output enablement is added in `SenscopePrototype`.
- No Force Up-B path is enabled in selected runtime behavior.
- No right-stick/C-stick runtime behavior is enabled.
- Failure paths preserve neutral fallback for left stick (`128,128`) with neutral right stick/triggers.

## 3. Flashing and hardware policy

- Automated agents must not flash hardware.
- Hardware flashing requires explicit user intent and approval per run.
- Builds with manual debug flag switched to `true` should be treated as experimental-only binaries.

## 4. Risks

- If the manual debug flag is manually enabled, `SenscopePrototype` becomes selectable via debug chord.
- Selected behavior currently uses `GetSenscopePrototypeExampleProfile()`, not user configuration.
- Direction mapping is tied to specific `InputState` fields (`lf3`, `lf1`, `lf2`, `rf4`) and should be reviewed before serious hardware use.

## 5. Recommended pre-flash checklist

1. Build from a clean tree and confirm expected branch.
2. `rg "kEnableSenscopePrototypeManualSelection" src/core/mode_selection.cpp` and confirm intended value.
3. Inspect `git diff -- src/core/mode_selection.cpp` and confirm no unintended mode-selection changes.
4. Confirm no default config activation changes in:
   - `config/glyph/common/include/glyph_overrides.hpp`
   - `HAL/pico/include/config_defaults.hpp`
5. Confirm explicit hardware intent and approval before any flashing action.

## 6. Verification commands

```bash
git status
git diff --stat
rg "kEnableSenscopePrototypeManualSelection" src/core/mode_selection.cpp docs/project
rg "SenscopePrototype" include src docs/project
rg "MODE_SENSCOPE|SENSCOPE|GameModeId|mode_id" include src config HAL
rg "activation_binding|default_mode_config" config/glyph/common/include/glyph_overrides.hpp HAL/pico/include/config_defaults.hpp
test -x ./scripts/pio-local.sh
test -x ./scripts/build-glyph-mk6-quiet.sh
./scripts/build-glyph-mk6-quiet.sh
```
