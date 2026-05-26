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

## RF5 Ambiguity (Do Not Resolve Yet)

Per `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`:

- RF5 negative check result is `NOT_TESTED_AMBIGUOUS`.
- Tester was not certain which physical button corresponded to RF5.
- A tested top-row right-most right-side button behaved identically with Tilt2/LT2.
- This does not resolve RF5 identity or provide definitive RF5-negative verification.

RF5 remains unresolved pending exact printed marking transcription.

## Faceplate/Base Marking Pending

User reports that printed physical ID markings are present on the controller base under plexi.

Current status:

- exact transcription is pending.
- no inferred spellings/capitalization are recorded here.
- once supplied, exact strings should be added as `HARDWARE_OBSERVED_USER_REPORTED` evidence in this map.

## Physical/Logical Mapping Table

| row_id | physical_button_id | matrix_position_if_source_known | display_position_if_source_known | fixture_profile_role | logical_activates | runtime_input_field | user_facing_role | printed_base_marking | evidence_status | source_or_fixture | caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| row_rf3_tilt1 | `BTN_RF3` | row=2,col=9 | `(112,24)` | `MODE_ULTIMATE` remap entry present | `BTN_LT1` | `inputs.lt1` | Tilt1/TILT | pending transcription | `SOURCE_CONFIRMED` + `FIXTURE_OBSERVED` + `USER_LABEL_CONFIRMED` | `config/glyph/glyph_mk6/include/matrix_definition.hpp`; `config/glyph/glyph_mk6/include/button_positions.hpp`; `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`; `src/modes/Ultimate.cpp`; `docs/calibration/glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md` | Profile-specific confirmation for current MVP evidence; not universal mapping authority. |
| row_rf4_tilt2 | `BTN_RF4` | row=2,col=10 | `(122,29)` | `MODE_ULTIMATE` remap entry present | `BTN_LT2` | `inputs.lt2` | Tilt2 | pending transcription | `SOURCE_CONFIRMED` + `FIXTURE_OBSERVED` + `USER_LABEL_CONFIRMED` | `config/glyph/glyph_mk6/include/matrix_definition.hpp`; `config/glyph/glyph_mk6/include/button_positions.hpp`; `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`; `src/modes/Ultimate.cpp`; `docs/calibration/glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md` | Profile-specific confirmation for current MVP evidence; not universal mapping authority. |
| row_rf5_ambiguous | `BTN_RF5` | row=1,col=7 | `(93,17)` | `MODE_ULTIMATE` remap entry present | `BTN_RF1` | `inputs.rf1` | unknown | pending transcription | `SOURCE_CONFIRMED` + `FIXTURE_OBSERVED` + `UNKNOWN` | `config/glyph/glyph_mk6/include/matrix_definition.hpp`; `config/glyph/glyph_mk6/include/button_positions.hpp`; `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`; `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` | Hardware test explicitly marks RF5 identity/negative check ambiguous; do not resolve from geometry. |
| row_lt1_physical | `BTN_LT1` | row=3,col=2 | `(38,52)` | `MODE_ULTIMATE` remap entry present | `BTN_RF5` | `inputs.rf5` | unknown | pending transcription | `SOURCE_CONFIRMED` + `FIXTURE_OBSERVED` | `config/glyph/glyph_mk6/include/matrix_definition.hpp`; `config/glyph/glyph_mk6/include/button_positions.hpp`; `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`; `src/modes/Ultimate.cpp` | Physical LT1 row here is fixture remap evidence only; not a claim about ergonomic naming. |
| row_lt2_physical | `BTN_LT2` | row=3,col=4 | `(46,58)` | `MODE_ULTIMATE` remap entry present (no `activates`) | omitted/unspecified in fixture row | `inputs.lt2` (field exists; consumed when active logically) | unknown | pending transcription | `SOURCE_CONFIRMED` + `FIXTURE_OBSERVED` | `config/glyph/glyph_mk6/include/matrix_definition.hpp`; `config/glyph/glyph_mk6/include/button_positions.hpp`; `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`; `include/core/state.hpp`; `src/modes/Ultimate.cpp` | Omitted `activates` behavior is profile/remap-data dependent; do not infer semantic role. |
| row_base_markings_pending | unknown | unknown | unknown | not yet provided | unknown | unknown | unknown | pending user transcription | `HARDWARE_OBSERVED_USER_REPORTED` | user report in task context (plexi removed, printed IDs observed) | Await exact spelling/capitalization before adding explicit per-button marking rows. |

## Adapter Implications

- Any adapter/evaluator must preserve the physical-vs-logical distinction (`physicalButton` vs post-remap logical input).
- User-facing role labels must not be mapped directly to runtime fields without passing through remap evidence.
- Future printed-base transcription can improve confidence for physical ID identification, but only as exact user-reported strings.
- Write-capable adapter/push workflow remains deferred; this map is documentation + read-only evidence alignment only.

## Evidence Notes

- `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md` was requested in task inputs but is not present in this repository at authoring time.
- Closest related checked-in policy doc discovered during this pass: `docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md`.
