# Glyph Physical Logical Layout Map - 2026-05-26

Scope: source/user-evidence map between Glyph MK6 physical buttons, logical post-remap inputs, display positions, runtime input fields, and known profile roles for the current prehardware firmware/configurator workstream.

This is not a Smash/game-semantic document. It does not invent ergonomic names from geometry and does not claim that Senscope neutral Profile JSON maps directly to Glyph JSON.

## Evidence Layers

- Matrix position: electrical scan matrix from `config/glyph/glyph_mk6/include/matrix_definition.hpp`.
- Display position: mini-screen input viewer coordinates from `config/glyph/glyph_mk6/include/button_positions.hpp`.
- Physical `BTN_*` id: pre-remap button identifier in a profile fixture or source matrix.
- Logical post-remap id: `activates` target after `ControllerMode::HandleRemap` / `InputMode::HandleRemap`.
- Runtime input field: `InputState` field consumed by `src/modes/Ultimate.cpp` after remap.
- User-facing role: user/domain label only when specifically provided or already documented for the MVP layout.

## Layout Map

| physical_button | matrix_position_if_source_known | display_position_if_source_known | observed_profile_role | logical_activates | runtime_input_field | evidence_status | source_or_fixture | caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `BTN_RF3` | row 2, col 9 | full/platform/split display `(112,24)` | Tilt1 / TILT for uploaded MVP layout | `BTN_LT1` | `inputs.lt1` | `CONFIRMED_FOR_MVP_LAYOUT` | `matrix_definition.hpp`, `button_positions.hpp`, `GlyphUserProfilesUltimateMVP01.json`, `glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md`, `Ultimate.cpp` | Role is profile/user-evidence specific, not universal geometry meaning. |
| `BTN_RF4` | row 2, col 10 | full/platform/split display `(122,29)` | Tilt2 for uploaded MVP layout | `BTN_LT2` | `inputs.lt2` | `CONFIRMED_FOR_MVP_LAYOUT` | same as above | Role is profile/user-evidence specific, not universal geometry meaning. |
| `BTN_RF5` | row 1, col 7 | full/platform/split/fgc display `(93,17)` | Ambiguous/rejected as Tilt1/Tilt2 target for MVP; currently maps to `BTN_RF1` in MVP fixture | `BTN_RF1` in MVP fixture | `inputs.rf1` if activated post-remap | `AMBIGUOUS_FOR_HARDWARE_RESULT` | `GlyphUserProfilesUltimateMVP01.json`, `glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md`, `button_positions.hpp` | Do not infer user-facing role from display geometry. Hardware result left RF5 identity ambiguous beyond not being Tilt1/Tilt2. |
| `BTN_LT1` | row 3, col 2 | full/platform display `(38,52)` | Logical MX / existing firmware modifier target in current docs | self or target from remap | `inputs.lt1` | `SOURCE_CONFIRMED_LOGICAL_INPUT` | `Ultimate.cpp`, existing calibration docs | `BTN_LT1` can be a physical id or a logical post-remap id; docs must label which layer is meant. |
| `BTN_LT2` | row 3, col 4 | full/platform display `(46,58)` | Logical MY / existing firmware modifier target in current docs | self or target from remap | `inputs.lt2` | `SOURCE_CONFIRMED_LOGICAL_INPUT` | `Ultimate.cpp`, existing calibration docs | Same physical/logical caveat as `BTN_LT1`. |
| `BTN_LF3` | row 1, col 0 | full/platform/split display `(15,23)` | left-stick left logical direction in native Ultimate | varies by profile/remap | `inputs.lf3` | `SOURCE_CONFIRMED_RUNTIME_INPUT` | `Ultimate.cpp`, `button_positions.hpp`, `matrix_definition.hpp` | This is controller/backend behavior, not gameplay semantics. |
| `BTN_LF1` | row 2, col 2 | full/platform/split display `(35,27)` | left-stick right logical direction in native Ultimate | varies by profile/remap | `inputs.lf1` | `SOURCE_CONFIRMED_RUNTIME_INPUT` | same as above | This is controller/backend behavior, not gameplay semantics. |
| `BTN_LF2` | row 1, col 1 | full/platform/split display `(25,22)` | left-stick down logical direction in native Ultimate | varies by profile/remap | `inputs.lf2` | `SOURCE_CONFIRMED_RUNTIME_INPUT` | same as above | This is controller/backend behavior, not gameplay semantics. |
| `BTN_RF4` | row 2, col 10 | full/platform/split display `(122,29)` | left-stick up logical direction when used post-remap by native Ultimate | varies by profile/remap; `BTN_LT2` for MVP Tilt2 physical role | `inputs.rf4` for logical up, or `inputs.lt2` after MVP remap | `SOURCE_CONFIRMED_WITH_LAYER_CAVEAT` | `Ultimate.cpp`, MVP fixture | Same `BTN_RF4` symbol appears as a physical button in the MVP remap and as a logical Ultimate up input when not remapped away. Keep layer labels explicit. |
| `BTN_RT3` | row 3, col 7 | full/platform display `(82,46)` | right-stick/C-stick left logical direction | varies by profile/remap | `inputs.rt3` | `SOURCE_CONFIRMED_RUNTIME_INPUT` | `Ultimate.cpp`, `button_positions.hpp`, `matrix_definition.hpp` | Preservation tests still need hardware coverage. |
| `BTN_RT5` | row 3, col 10 | full/platform display `(98,46)` | right-stick/C-stick right logical direction | varies by profile/remap | `inputs.rt5` | `SOURCE_CONFIRMED_RUNTIME_INPUT` | same as above | Preservation tests still need hardware coverage. |
| `BTN_RT2` | row 3, col 6 | full/platform display `(82,58)` | right-stick/C-stick down logical direction | varies by profile/remap | `inputs.rt2` | `SOURCE_CONFIRMED_RUNTIME_INPUT` | same as above | Preservation tests still need hardware coverage. |
| `BTN_RT4` | row 3, col 9 | full/platform display `(90,40)` | right-stick/C-stick up logical direction | varies by profile/remap | `inputs.rt4` | `SOURCE_CONFIRMED_RUNTIME_INPUT` | same as above | Preservation tests still need hardware coverage. |
| `BTN_LF4` | row 2, col 0 | full display `(6,29)` | left trigger digital/analog source in native Ultimate | varies by profile/remap | `inputs.lf4` | `SOURCE_CONFIRMED_RUNTIME_INPUT` | `Ultimate.cpp` | Trigger preservation still needs expanded hardware checklist coverage. |
| `BTN_RF5` | row 1, col 7 | full/platform/split/fgc display `(93,17)` | right trigger digital/analog source in native Ultimate when logical `rf5` is active | varies by profile/remap | `inputs.rf5` | `SOURCE_CONFIRMED_RUNTIME_INPUT_WITH_MVP_AMBIGUITY` | `Ultimate.cpp`, MVP fixture | Do not collapse this with the separate MVP physical RF5 ambiguity row. |

## Confirmed MVP Tilt Routing

- Physical `BTN_RF3` maps to logical `BTN_LT1` in `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`.
- Physical `BTN_RF4` maps to logical `BTN_LT2` in that fixture.
- Native Ultimate runtime consumes logical `inputs.lt1` and `inputs.lt2` in the Tilt/Tilt2 patch.
- Runtime must not bypass remap by reading raw physical `inputs.rf3` or `inputs.rf4` for this behavior.

## Caveats

- RF5 remains ambiguous from the current hardware result and is not confirmed as a Tilt1/Tilt2 physical identity.
- Display coordinates are input-viewer positions, not gameplay or stick-output coordinates.
- Geometry does not prove ergonomic/user-facing names.
- User/domain labels are separated from source-confirmed IDs in the table.
- This document does not change runtime, remap, SOCD, profile schema, or configurator behavior.
