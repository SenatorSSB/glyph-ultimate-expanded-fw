# Glyph Physical/Logical Layout Map Handoff

## Changed files

- `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`
- `docs/calibration/glyph_physical_logical_layout_map_handoff.md`
- `tools/list_glyph_physical_logical_layout_sources.py`

## What was inspected

- `config/glyph/glyph_mk6/include/matrix_definition.hpp`
- `config/glyph/glyph_mk6/include/button_positions.hpp`
- `HAL/pico/src/display/InputDisplay.cpp`
- `config/glyph/common/src/config.cpp`
- `include/core/state.hpp`
- `HAL/pico/include/util/state_util.hpp`
- `src/core/InputMode.cpp`
- `src/core/ControllerMode.cpp`
- `src/modes/Ultimate.cpp`
- `docs/calibration/glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md`
- `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`
- `docs/calibration/fixtures/glyph_ultimate_tilt_domain_spec.json`
- `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`
- `docs/calibration/glyph_full_capability_inventory_2026-05-26.md`
- `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`
- user chat-provided evidence image reference: `glyph_physical_ids_v3_centered.jpeg` (not treated as repo-local source unless committed separately)

## What was not inspected

- Any non-listed firmware/game-mode files outside the source set above.
- Any flashing/push-to-device workflow implementation artifacts.

## Behavior/config impact

- Runtime behavior changed: none.
- Firmware source behavior changed: none.
- Configurator behavior changed: none.
- SOCD semantics changed: none.
- Remap semantics changed: none.
- Profile schema/proto changed: none.

## Artifact hygiene

- Build artifacts or firmware binaries committed: no.
- `.venv`, `.pio`, `__pycache__`, `.pyc` committed: no.

## Exact unresolved questions

1. Source-confirmed matrix/display/runtime mappings are still unknown for most transcribed printed IDs and remain pending explicit source/fixture evidence.
2. RF5 physical location is now transcribed (center-right cluster, far-right upper button), but the old RF5 negative smoke test remains `NOT_TESTED_AMBIGUOUS` and is not retroactively resolved.

## Next recommended branch

- `glyph/ultimate-preservation-test-matrix`
