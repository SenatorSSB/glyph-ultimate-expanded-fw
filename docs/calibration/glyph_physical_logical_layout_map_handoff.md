# Glyph Physical Logical Layout Map Handoff

Date: 2026-05-26

## What This Branch Adds

- `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md` with a source/user-evidence layout map.
- `tools/list_glyph_physical_logical_layout_sources.py`, a stdlib-only read-only helper that prints matrix/display/runtime/fixture mapping signals.

## Key Source-Grounded Points

- Matrix positions come from `config/glyph/glyph_mk6/include/matrix_definition.hpp`.
- Display positions come from `config/glyph/glyph_mk6/include/button_positions.hpp`.
- Native Ultimate runtime input fields come from `src/modes/Ultimate.cpp`.
- MVP Tilt routing comes from `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json` and existing calibration docs.

## Confirmed MVP Routing

- `BTN_RF3 -> BTN_LT1 -> inputs.lt1` for Tilt1 / TILT in the uploaded MVP layout.
- `BTN_RF4 -> BTN_LT2 -> inputs.lt2` for Tilt2 in the uploaded MVP layout.
- RF5 remains ambiguous from hardware result and must not be promoted to a confirmed Tilt role.

## Behavior Impact

- Runtime/source behavior changed: none.
- Configurator/profile schema behavior changed: none.
- Build artifacts or binaries committed: no.
