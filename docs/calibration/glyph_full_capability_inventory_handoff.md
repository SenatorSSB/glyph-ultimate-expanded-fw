# Glyph Full Capability Inventory Handoff

Date: 2026-05-26

Branch: `glyph/full-capability-inventory`

## What Was Inspected

- Physical/logical input model:
  - `include/core/state.hpp`
  - `HAL/pico/include/util/state_util.hpp`
  - `config/glyph/glyph_mk6/include/matrix_definition.hpp`
  - `config/glyph/glyph_mk6/include/button_positions.hpp`
  - `include/input/SwitchMatrixInput.hpp`
  - `HAL/pico/include/input/DebouncedSwitchMatrixInput.hpp`
- Remap/SOCD/runtime flow:
  - `src/core/ControllerMode.cpp`
  - `src/core/InputMode.cpp`
  - `src/core/socd.cpp`
  - `src/modes/Ultimate.cpp`
  - `src/modes/CustomControllerMode.cpp`
  - `src/modes/SenscopePrototype.cpp`
  - `include/prototypes/senscope/SenscopePrototypeTypes.hpp`
- Profile/config/configurator/storage:
  - `config/glyph/common/include/glyph_overrides.hpp`
  - `config/glyph/common/src/config.cpp`
  - `HAL/pico/src/comms/ConfiguratorBackend.cpp`
  - `HAL/pico/src/core/Persistence.cpp`
  - `HAL/pico/src/comms/backend_init.cpp`
  - `HAL/pico/src/display/DefaultConfigMenu.cpp`
  - `HAL/pico/src/display/ConfigMenu.cpp`
  - `config/glyph/common/src/display/GlyphConfigMenu.cpp`
  - `docs/sources/raw/GlyphUserProfiles.json`
  - `tools/glyph_config_model.py`
- Display/menu behavior:
  - `HAL/pico/src/display/InputDisplay.cpp`
  - `HAL/pico/src/display/RemapMenu.cpp`
  - `config/glyph/common/src/config.cpp`
- Build/release/artifact/check flow:
  - `platformio.ini`
  - `config/glyph/env.ini`
  - `config/glyph/meta.yaml`
  - `tools/run_glyph_ultimate_tilt_prehardware_checks.py`
  - `tools/check_glyph_ultimate_tilt_hardware_result.py`
  - `tools/check_glyph_ultimate_tilt_rc_manifest.py`
  - `tools/inspect_glyph_mk6_build_artifact.py`
  - `tools/uf2/inspect_uf2.py`
- Hardware/result/calibration docs used as evidence:
  - `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`
  - `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`
  - `docs/calibration/glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md`
  - `docs/calibration/fixtures/glyph_ultimate_tilt_domain_spec.json`

## What Was Not Inspected

- External browser configurator app source, because it is not present in this repo as an npm/TypeScript app.
- External HayBox proto repository history beyond the PlatformIO dependency configuration and local generated/dependency artifacts.
- Full per-backend report serialization details for every backend; only enough was inspected to identify output surfaces and artifact/build boundaries.
- Exhaustive hardware behavior beyond the recorded hardware result file.
- Any Senscope app code or Senscope game-semantic source authority.

## Runtime Behavior Changed

None.

This batch only adds documentation. It does not change firmware runtime behavior, SOCD semantics, remap semantics, profile schema/proto/configurator behavior, or flashing/push workflows.

## Recommended Next Branches

1. `glyph/profile-config-source-authority`
   - Capture authoritative proto/configurator JSON behavior, especially omitted fields versus explicit disabled fields.
2. `glyph/profile-adapter-design-fixtures`
   - Add read-only fixtures/checkers for a future Senscope-to-Glyph adapter contract without runtime changes.
3. `glyph/ultimate-preservation-hardware-matrix`
   - Expand C-stick, trigger, SOCD, RF5 identity, profile preservation, and optional nunchuk hardware checklist coverage.
4. `glyph/native-ultimate-table-runtime-design`
   - Design only, pending review, for any additional exact-coordinate native Ultimate runtime table support.

## Verification Commands Run

- `.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py`: PASS (`overall_status=PASS`, `failed_steps=0`)
- `.venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py`: PASS (`final_disposition=PASS`)
- `.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py`: PASS
- `grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true`: PASS (no conflict markers)
- `git diff --check`: PASS
- `git status --short`: only these three new docs were present before staging

No new helper script was added, so there is no helper-script output to report.

## Exact Unresolved Questions Requiring User Domain Input

- What is the intended canonical treatment of omitted `activates` in Glyph JSON exports: identity, disabled, unset/default, or configurator-specific shorthand?
- Which physical Glyph layout labels should Senscope-facing docs use for `BTN_LF*`, `BTN_RF*`, `BTN_LT*`, `BTN_RT*`, and `BTN_MB*` beyond source-confirmed matrix/display positions?
- For future full profile realization, which exact controller outputs are required beyond current native Tilt1/Tilt2 left-stick tables?
- Should future Glyph-side work target native `MODE_ULTIMATE`, `MODE_CUSTOM`, the existing `SenscopePrototype` scaffold, or a new reviewed mode boundary?
- Which communication backends are in scope for future verification: Switch only, GameCube, XInput/DInput, or all available backends?
- Is Nunchuk behavior in scope for the desired full Glyph profile functionality?
- Should the next hardware batch retest RF5 physical identity, exhaustive C-stick/right-stick preservation, trigger preservation, SOCD matrix behavior, and profile readback/preservation?
- Who owns final approval for adapter behavior that cannot be proven from this repo alone: user domain statement, external configurator source, or a reviewed captured export corpus?
