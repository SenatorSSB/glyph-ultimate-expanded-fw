# G11m2-n-r Audit and Design Notes

Status: completed  
Branch: `proto/glyph-runtime-audit-modifier-design-g11m2-n-r`

## 1. Files changed

- `docs/project/G11M2_RUNTIME_DEBUG_PATH_AUDIT.md`
- `docs/project/G11N_MODIFIER_MASK_ENABLEMENT_DESIGN.md`
- `docs/project/G11R_SELECTED_PATH_READINESS_CHECKS.md`
- `docs/project/G11M2_N_R_AUDIT_AND_DESIGN_NOTES.md`
- `include/prototypes/senscope/SenscopePrototypeSelfTest.hpp` (isolated self-test only)
- `src/prototypes/senscope/SenscopePrototypeSelfTest.cpp` (isolated self-test only)
- `docs/project/ACTIVE_AGENT_QUEUE.md` (minimal queue update)

## 2. Runtime behavior boundary

- No new selected runtime behavior is enabled.
- No mode reachability/default activation behavior is changed.
- No `GameModeId`, protobuf/config schema, output report, digital output, Force Up-B, right-stick/C-stick, or gameplay-semantic behavior is changed.

## 3. Docs created

- Runtime debug-path audit: `G11M2_RUNTIME_DEBUG_PATH_AUDIT.md`
- Modifier-mask future design (docs-only): `G11N_MODIFIER_MASK_ENABLEMENT_DESIGN.md`
- Selected-path readiness checks: `G11R_SELECTED_PATH_READINESS_CHECKS.md`

## 4. Self-test additions

Added isolated resolver assumptions for current selected-path profile use:

- active modifier `0` + direction `D5` resolves neutral coordinate (`128,128`) from base table
- active modifier `0` + direction `D6` resolves base table right coordinate (`228,128`)
- active modifier `0` + direction `D4` resolves base table left coordinate (`28,128`)

These are helper-level checks only (no runtime `SenscopePrototype` output-path wiring changes).

## 5. Verification actual results

- `git status`: passed; only in-scope doc and isolated self-test edits present.
- `git diff --stat`: passed; current stat reflects scoped edits only.
- `rg "kEnableSenscopePrototypeManualSelection" src/core/mode_selection.cpp docs/project`: passed; mode-selection flag remains present as `false` and docs reference that boundary.
- `rg "SenscopePrototype" include src docs/project`: passed; expected existing and new references only.
- `rg "MODE_SENSCOPE|SENSCOPE|GameModeId|mode_id" include src config HAL`: passed; no new `MODE_SENSCOPE`/`GameModeId` activation path introduced in this batch.
- `rg "activation_binding|default_mode_config" config/glyph/common/include/glyph_overrides.hpp HAL/pico/include/config_defaults.hpp`: passed; no changes made to default activation/default mode config paths.
- `find . -maxdepth 4 -type f | rg '/(test|tests|spec)/|(_test\\.|\\.test\\.|\\.spec\\.)|package.json|pytest|CMakeLists|platformio.ini' || true`: passed; returned expected inventory entries including `platformio.ini` and package manifests.
- `test -x ./scripts/pio-local.sh`: passed.
- `test -x ./scripts/build-glyph-mk6-quiet.sh`: passed.
- `./scripts/build-glyph-mk6-quiet.sh`: passed (`glyph_mk6 build passed`).

## 6. Recommended next batches

1. Human inspection of G11m2-n-r audit/design outputs before any runtime expansion.
2. If explicitly approved, `G11n-impl1` helper-only modifier mask construction (still unwired).
3. Keep Force Up-B, digital outputs, right-stick/C-stick, and flashing out-of-scope until separately approved.
