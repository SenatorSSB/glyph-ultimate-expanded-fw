# Glyph MK6 Physical/Logical Layout Map (2026-05-26)

## Scope and Evidence Taxonomy

This document is a source-grounded layout map for Glyph MK6 that separates physical button identity from logical post-remap behavior.

Status taxonomy used in this file:

- `SOURCE_CONFIRMED`: directly supported by checked-in source/docs.
- `FIXTURE_OBSERVED`: directly observed in checked-in fixture/profile JSON.
- `HARDWARE_OBSERVED_USER_REPORTED`: user-reported hardware observation from manual testing context.
- `USER_LABEL_CONFIRMED`: user/domain label explicitly provided for the mapped role.
- `INFERRED_DO_NOT_USE_FOR_MAPPING`: inference only; not safe as mapping authority.
- `UNKNOWN`: not currently established by source/fixture/user transcription.

## Layer Separation (Do Not Collapse)

The same `BTN_*` symbol namespace appears in multiple layers, but each layer has distinct meaning:

1. Matrix scan position:
   - Electrical scan-cell location in `matrix[num_rows][num_cols]`.
   - Source: `config/glyph/glyph_mk6/include/matrix_definition.hpp`.

2. Display/input-viewer position:
   - Mini-screen draw coordinates (`center_x`, `center_y`) used by Input Viewer rendering.
   - Source: `config/glyph/glyph_mk6/include/button_positions.hpp`, `HAL/pico/src/display/InputDisplay.cpp`.

3. Physical `BTN_*` id:
   - Raw pressed button identity from matrix scan before remap.

4. Logical post-remap `BTN_*` target:
   - `ButtonRemap.activates` output after `HandleRemap`.
   - Source flow: `src/core/ControllerMode.cpp` -> `src/core/InputMode.cpp`.

5. Runtime `InputState` field:
   - Consumer code reads `inputs.<field>` from remapped `InputState`.
   - Source: `include/core/state.hpp`, `src/modes/Ultimate.cpp`.

6. User-facing role:
   - Role labels (for example Tilt1/TILT, Tilt2) are profile/user-context-specific unless source/user evidence confirms scope.

7. Printed faceplate/base marking:
   - Physical text printed on hardware base under plexi.
   - Must be recorded exactly as transcribed; do not infer missing values.

## Source-Confirmed Physical/Matrix/Display Map

Matrix scan cells (0-based index from `matrix_definition.hpp`):

- `BTN_RF5`: row 1, col 7
- `BTN_RF3`: row 2, col 9
- `BTN_RF4`: row 2, col 10
- `BTN_LT1`: row 3, col 2
- `BTN_LT2`: row 3, col 4

Input-viewer coordinates (platform-fighter and full-layout entries in `button_positions.hpp`):

- `BTN_RF3`: `(112, 24)`
- `BTN_RF4`: `(122, 29)`
- `BTN_RF5`: `(93, 17)`
- `BTN_LT1`: `(38, 52)`
- `BTN_LT2`: `(46, 58)`

Important: these display coordinates are rendering positions only; they are not physical matrix coordinates.

## Confirmed Current Ultimate MVP Tilt Mapping (Profile-Specific)

For the provided Ultimate MVP fixture/profile context:

- physical `BTN_RF3` -> logical `BTN_LT1` -> runtime `inputs.lt1` -> user role Tilt1/TILT
- physical `BTN_RF4` -> logical `BTN_LT2` -> runtime `inputs.lt2` -> user role Tilt2

Evidence:

- `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json` (`MODE_ULTIMATE` remaps)
- `docs/calibration/glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md`
- `src/core/InputMode.cpp` (remap behavior)
- `src/modes/Ultimate.cpp` (runtime `inputs.lt1` and `inputs.lt2` consumption)
- `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` (manual smoke observations for RF3/RF4 path)

Caveat: this is confirmed for current uploaded MVP profile evidence; it is not a universal/fixed Glyph mapping claim.

## Hardware-Observed Printed/Base Marking Transcription

Evidence status for this section: `HARDWARE_OBSERVED_USER_REPORTED`.

- The user supplied an annotated layout image in chat: `glyph_physical_ids_v3_centered.jpeg`.
- Unless that image is separately committed into this repo, it is treated as chat-provided evidence and not as a repo-local source file.
- The transcription below is the repo-recorded evidence.

Top menu row:

- Top row button 1, far left: MB1
- Top row button 2: MB2
- Top row button 3: MB3
- Top row button 4: MB4
- Top row button 5: MB5
- Top row button 6: MB6
- Top row button 7, far right before screen: MB7

Left-finger cluster:

- Far-left lower isolated button: LF4
- Left-upper button: LF3
- Center-upper button: LF2
- Upper-right button: LF8
- Far-upper-right button: LF7
- Right-middle button below LF8: LF1
- Center-lower button below LF2: LF5
- Far-right isolated button near center: LF6

Left-thumb / lower-left cluster:

- Upper button: LT4
- Left button: LT5
- Right button: LT3
- Center/lower-left button: LT1
- Bottom button: LT2
- Large right button: LT6

Center-right / RF cluster:

- Upper-left button: RF14
- Upper-right button: RF15
- Far-right upper button: RF5
- Left-middle button: RF13
- Left-lower button: RF10
- Center-left middle button: RF11
- Center-right middle button: RF12
- Far-right middle/lower button: RF1
- Lower-center button: RF16

Far-right face cluster:

- Top-left button: RF6
- Top-right button: RF7
- Outer upper-right button: RF8
- Middle-left button: RF2
- Middle-right button: RF3
- Outer lower-right button: RF4
- Bottom-left button: RF9

Right-thumb / lower-right cluster:

- Top button: RT4
- Left button: RT3
- Center button: RT1
- Right button: RT5
- Bottom button: RT2

## RF5 Ambiguity and Forward Test Guidance

Per `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`:

- RF5 negative check result remains `NOT_TESTED_AMBIGUOUS`.
- At that test time, the tester was not sure which physical button corresponded to RF5.
- The printed/base-marking transcription identifies the center-right / RF cluster "Far-right upper button" as RF5.
- Do not retroactively convert the old RF5 negative check to PASS.
- Future RF5-specific checks should use this newly transcribed RF5 location.

## Physical/Logical Mapping Table

| transcribed_physical_id | transcribed_location | source_button_symbol_if_known | matrix_position_if_source_known | display_position_if_source_known | fixture_profile_role | logical_activates | runtime_input_field | user_facing_role | printed_base_marking | evidence_status | source_or_fixture | caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MB1 | Top row button 1, far left | unknown | unknown | unknown | unknown | unknown | unknown | unknown | MB1 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| MB2 | Top row button 2 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | MB2 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| MB3 | Top row button 3 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | MB3 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| MB4 | Top row button 4 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | MB4 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| MB5 | Top row button 5 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | MB5 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| MB6 | Top row button 6 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | MB6 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| MB7 | Top row button 7, far right before screen | unknown | unknown | unknown | unknown | unknown | unknown | unknown | MB7 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LF1 | Right-middle button below LF8 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LF1 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LF2 | Center-upper button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LF2 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LF3 | Left-upper button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LF3 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LF4 | Far-left lower isolated button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LF4 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LF5 | Center-lower button below LF2 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LF5 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LF6 | Far-right isolated button near center | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LF6 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LF7 | Far-upper-right button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LF7 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LF8 | Upper-right button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LF8 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LT1 | Center/lower-left button | `BTN_LT1` | row=3,col=2 | `(38,52)` | `MODE_ULTIMATE` remap entry present | `BTN_RF5` | `inputs.rf5` | unknown | LT1 | `HARDWARE_OBSERVED_USER_REPORTED` + `SOURCE_CONFIRMED` + `FIXTURE_OBSERVED` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`); `config/glyph/glyph_mk6/include/matrix_definition.hpp`; `config/glyph/glyph_mk6/include/button_positions.hpp`; `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`; `src/modes/Ultimate.cpp` | Physical LT1 row here is fixture remap evidence only; do not infer ergonomic or gameplay role. |
| LT2 | Bottom button | `BTN_LT2` | row=3,col=4 | `(46,58)` | `MODE_ULTIMATE` remap entry present (no `activates`) | omitted/unspecified in fixture row | `inputs.lt2` (field exists; consumed when active logically) | unknown | LT2 | `HARDWARE_OBSERVED_USER_REPORTED` + `SOURCE_CONFIRMED` + `FIXTURE_OBSERVED` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`); `config/glyph/glyph_mk6/include/matrix_definition.hpp`; `config/glyph/glyph_mk6/include/button_positions.hpp`; `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`; `include/core/state.hpp`; `src/modes/Ultimate.cpp` | Omitted `activates` behavior is profile/remap-data dependent; do not infer semantic role. |
| LT3 | Right button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LT3 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LT4 | Upper button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LT4 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LT5 | Left button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LT5 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| LT6 | Large right button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | LT6 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF1 | Far-right middle/lower button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF1 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF2 | Middle-left button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF2 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF3 | Middle-right button | `BTN_RF3` | row=2,col=9 | `(112,24)` | `MODE_ULTIMATE` remap entry present | `BTN_LT1` | `inputs.lt1` | Tilt1/TILT | RF3 | `HARDWARE_OBSERVED_USER_REPORTED` + `SOURCE_CONFIRMED` + `FIXTURE_OBSERVED` + `USER_LABEL_CONFIRMED` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`); `config/glyph/glyph_mk6/include/matrix_definition.hpp`; `config/glyph/glyph_mk6/include/button_positions.hpp`; `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`; `src/modes/Ultimate.cpp`; `docs/calibration/glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md` | Profile-specific confirmation for current MVP evidence; not universal mapping authority. |
| RF4 | Outer lower-right button | `BTN_RF4` | row=2,col=10 | `(122,29)` | `MODE_ULTIMATE` remap entry present | `BTN_LT2` | `inputs.lt2` | Tilt2 | RF4 | `HARDWARE_OBSERVED_USER_REPORTED` + `SOURCE_CONFIRMED` + `FIXTURE_OBSERVED` + `USER_LABEL_CONFIRMED` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`); `config/glyph/glyph_mk6/include/matrix_definition.hpp`; `config/glyph/glyph_mk6/include/button_positions.hpp`; `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`; `src/modes/Ultimate.cpp`; `docs/calibration/glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md` | Profile-specific confirmation for current MVP evidence; not universal mapping authority. |
| RF5 | Far-right upper button | `BTN_RF5` | row=1,col=7 | `(93,17)` | `MODE_ULTIMATE` remap entry present | `BTN_RF1` | `inputs.rf1` | unknown | RF5 | `HARDWARE_OBSERVED_USER_REPORTED` + `SOURCE_CONFIRMED` + `FIXTURE_OBSERVED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`); `config/glyph/glyph_mk6/include/matrix_definition.hpp`; `config/glyph/glyph_mk6/include/button_positions.hpp`; `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`; `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` | Old hardware smoke check for RF5 remains `NOT_TESTED_AMBIGUOUS`; do not retroactively mark PASS. Future RF5 checks should use this location. |
| RF6 | Top-left button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF6 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF7 | Top-right button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF7 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF8 | Outer upper-right button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF8 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF9 | Bottom-left button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF9 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF10 | Left-lower button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF10 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF11 | Center-left middle button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF11 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF12 | Center-right middle button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF12 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF13 | Left-middle button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF13 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF14 | Upper-left button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF14 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF15 | Upper-right button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF15 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RF16 | Lower-center button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RF16 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RT1 | Center button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RT1 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RT2 | Bottom button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RT2 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RT3 | Left button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RT3 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RT4 | Top button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RT4 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |
| RT5 | Right button | unknown | unknown | unknown | unknown | unknown | unknown | unknown | RT5 | `HARDWARE_OBSERVED_USER_REPORTED` + `UNKNOWN` | user chat transcription (`glyph_physical_ids_v3_centered.jpeg`) | Printed ID/location recorded; no source-confirmed matrix/display/runtime mapping yet. |

## Adapter Implications

- Any adapter/evaluator must preserve the physical-vs-logical distinction (`physicalButton` vs post-remap logical input).
- User-facing role labels must not be mapped directly to runtime fields without passing through remap evidence.
- Printed-base transcription improves confidence for physical ID identification, but source-verified matrix/display/runtime mapping still requires explicit source/fixture evidence.
- Write-capable adapter/push workflow remains deferred; this map is documentation + read-only evidence alignment only.

## Evidence Notes

- `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md` is present and is now part of the in-repo policy context for this map.
- `docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md` remains relevant for RF5 ambiguity handling and test-result interpretation.
