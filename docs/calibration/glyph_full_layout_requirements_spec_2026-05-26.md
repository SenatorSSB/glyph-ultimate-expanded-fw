# Glyph Full Layout Requirements Spec - 2026-05-26

Scope: requirements capture document for future Glyph firmware/profile realization work. This is not the Senscope browser app repo, does not change runtime behavior, and does not invent missing user/domain requirements.

## Status Legend

- `CONFIRMED`: explicit user/domain requirement or already established branch requirement.
- `HARDWARE_OBSERVED`: recorded in repo-local hardware result evidence.
- `SOURCE_CONFIRMED`: directly visible in repo source/docs/tools/fixtures.
- `USER_INPUT_REQUIRED`: needs user/domain decision.
- `SOURCE_RESEARCH_REQUIRED`: needs more repo/source inspection.
- `CORPUS_REQUIRED`: needs captured exports/fixtures/corpus authority.
- `OUT_OF_SCOPE`: excluded by current workstream constraints.

## Physical Button Roles

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Current MVP Tilt1 physical role | `CONFIRMED` + `HARDWARE_OBSERVED` | `BTN_RF3` | `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`, `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` | Profile-specific; do not universalize from geometry. |
| Current MVP Tilt2 physical role | `CONFIRMED` + `HARDWARE_OBSERVED` | `BTN_RF4` | same as above | Profile-specific; do not universalize from geometry. |
| RF5 physical identity | `USER_INPUT_REQUIRED` + `HARDWARE_OBSERVED` | ambiguous | `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` | Hardware result explicitly says RF5 was not definitively identified. |
| Full target physical layout | `USER_INPUT_REQUIRED` | not specified | none | User/domain must provide final physical roles before full realization. |
| Ergonomic/user-facing names from geometry | `OUT_OF_SCOPE` | none | workstream constraint | Do not invent role names from matrix/display coordinates. |

## Logical Post-Remap Roles

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Tilt1 logical post-remap input | `SOURCE_CONFIRMED` + `HARDWARE_OBSERVED` | `BTN_LT1` / `inputs.lt1` | MVP fixture, `src/modes/Ultimate.cpp`, hardware result | Runtime consumes logical post-remap input. |
| Tilt2 logical post-remap input | `SOURCE_CONFIRMED` + `HARDWARE_OBSERVED` | `BTN_LT2` / `inputs.lt2` | MVP fixture, `src/modes/Ultimate.cpp`, hardware result | Runtime consumes logical post-remap input. |
| Full logical role map | `USER_INPUT_REQUIRED` | incomplete | none | Must be filled without changing remap semantics. |
| Many-to-one aliases | `SOURCE_CONFIRMED` | valid runtime behavior | `src/core/InputMode.cpp` | Do not reject as macros; this is runtime remap behavior. |
| Duplicate physical remap behavior | `SOURCE_CONFIRMED` | first-entry-wins | `src/core/InputMode.cpp` | Future adapter/checkers must preserve ordering. |

## Mode/Profile Requirements

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Native Ultimate mode identity for current Tilt/Tilt2 | `SOURCE_CONFIRMED` | `MODE_ULTIMATE` | `src/modes/Ultimate.cpp` | Current patch is native Ultimate. |
| Default profile behavior | `SOURCE_CONFIRMED` + `SOURCE_RESEARCH_REQUIRED` | one-based defaults where source-confirmed | `HAL/pico/src/comms/backend_init.cpp`, `src/core/config_utils.cpp` | Full desired default behavior still needs user requirement. |
| Profile preservation after flash | `HARDWARE_OBSERVED` partial | appeared preserved, not exhaustive | hardware result | Needs expanded hardware matrix before future runtime patch. |
| Runtime adapter implementation | `OUT_OF_SCOPE` | none | current prompt constraints | Do not implement until explicitly approved later. |

## Modifier Table Requirements

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Current Tilt1 table | `HARDWARE_OBSERVED` + `SOURCE_CONFIRMED` | 9-way formula using x magnitude 59 and y magnitude 41 | `src/modes/Ultimate.cpp`, hardware result | Native formula, not arbitrary profile table. |
| Current Tilt2 table | `HARDWARE_OBSERVED` + `SOURCE_CONFIRMED` | 9-way formula using x magnitude 40 and y magnitude 49 | same as above | Native formula, not arbitrary profile table. |
| Arbitrary native Ultimate table support | `SOURCE_RESEARCH_REQUIRED` + `USER_INPUT_REQUIRED` | not implemented | `src/modes/Ultimate.cpp` | Design/review required before runtime patch. |
| Production modifier state names | `USER_INPUT_REQUIRED` | not specified | none | Do not infer names or semantics. |
| Production coordinate tables | `USER_INPUT_REQUIRED` + `CORPUS_REQUIRED` | not specified | none | Need explicit raw coordinate sources/evidence. |

## Disabled Button Requirements

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Explicit `BTN_UNSPECIFIED` behavior | `SOURCE_CONFIRMED` | no-op target | `HAL/pico/include/util/state_util.hpp` | Source-confirmed explicit disabled target behavior. |
| Omitted `activates` outbound policy | `USER_INPUT_REQUIRED` + `CORPUS_REQUIRED` | unresolved | `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md` | Do not interpret omission as disabled for outbound writes without authority. |
| Omitted versus explicit disabled equivalence | `CORPUS_REQUIRED` | unproven | existing fixtures and semantics gap map | Must stay distinct in read-only tools. |

## Both-Held/Chord Behavior

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Current LT1+LT2 override exclusion | `SOURCE_CONFIRMED` | Tilt patch does not run when both are held | `src/modes/Ultimate.cpp` | Uses exclusive `lt1 && !lt2` and `lt2 && !lt1`. |
| Current both-held observed table | `HARDWARE_OBSERVED` | directions 1..9 offsets: `(-35,-53)`, `(0,-53)`, `(35,-53)`, `(-41,0)`, `(0,0)`, `(41,0)`, `(-35,53)`, `(0,53)`, `(35,53)` | hardware result | Recorded as stable existing behavior, not a new desired semantic. |
| Future chord/conflict policy | `USER_INPUT_REQUIRED` | not specified | none | Must be explicit before arbitrary table runtime. |

## C-Stick/Right-Stick Requirements

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Existing native Ultimate right-stick fields | `SOURCE_CONFIRMED` | logical `rt3`, `rt5`, `rt2`, `rt4`; later branches may override | `src/modes/Ultimate.cpp` | Hardware preservation not exhaustive. |
| Future preservation expectation | `USER_INPUT_REQUIRED` + `HARDWARE_OBSERVED` partial | preserve existing behavior | current workstream constraints and hardware result caveat | Needs preservation matrix before runtime changes. |
| New right-stick behavior | `OUT_OF_SCOPE` | none | prompt constraints | Do not add unsupported behavior. |

## Trigger Requirements

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Existing native Ultimate trigger fields | `SOURCE_CONFIRMED` | `inputs.lf4` and `inputs.rf5` set digital/analog trigger outputs | `src/modes/Ultimate.cpp` | RF5 identity still needs hardware clarity. |
| Trigger preservation | `USER_INPUT_REQUIRED` + `HARDWARE_OBSERVED` partial | preserve existing behavior | hardware result caveat | Needs expanded hardware test. |
| New trigger behavior | `OUT_OF_SCOPE` | none | prompt constraints | No unsupported hardware behavior. |

## SOCD Requirements

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Current SOCD pipeline | `SOURCE_CONFIRMED` | remap, then SOCD, then mode output generation | `src/core/ControllerMode.cpp`, `src/core/InputMode.cpp`, `src/core/socd.cpp` | Do not change SOCD semantics. |
| Future SOCD policy changes | `OUT_OF_SCOPE` | none | prompt constraints | Stop before coupling controller constraints into game-semantic solving. |
| Full SOCD hardware matrix | `HARDWARE_OBSERVED` partial + `USER_INPUT_REQUIRED` | not exhaustive | hardware result | Needs preservation matrix completion. |

## Profile/Default Behavior

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Default indices | `SOURCE_CONFIRMED` | one-based where source-confirmed | backend init/config utils docs | Do not assume zero-based. |
| `defaultModeConfig = 0` outbound use | `USER_INPUT_REQUIRED` | unresolved | semantics gap map | Firmware validation not rejecting zero is not an outbound policy. |
| Profile readback/preservation | `USER_INPUT_REQUIRED` + `HARDWARE_OBSERVED` partial | not exhaustively verified | hardware result | Needs explicit hardware checklist. |

## Corpus/Export Requirements

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| JSON fixtures as canonical wire format | `OUT_OF_SCOPE` | not claimed | `HAL/pico/src/comms/ConfiguratorBackend.cpp`, persistence docs | Firmware source confirms protobuf transport/storage, not JSON canonicality. |
| Export corpus for adapter writes | `CORPUS_REQUIRED` | absent | `tools/check_glyph_profile_config_export_corpus.py` | Needed before write-capable adapter. |
| Push-to-device automation | `OUT_OF_SCOPE` | none | prompt constraints | No push automation. |

## Hardware-Test Requirements

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| Current Tilt1/Tilt2 hardware pass | `HARDWARE_OBSERVED` | PASS | `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` | Current native behavior already smoke-tested. |
| Preservation matrix before future runtime patch | `USER_INPUT_REQUIRED` + `HARDWARE_OBSERVED` partial | needed | hardware result caveats | Stop before requiring real hardware evidence in this docs branch. |
| Nunchuk hardware behavior | `USER_INPUT_REQUIRED` | optional/not tested | hardware result | Optional, explicitly not required if hardware unavailable. |

## Adapter Policy Requirements

| requirement | status | current value | evidence | notes |
| --- | --- | --- | --- | --- |
| No write-capable adapter yet | `CONFIRMED` | none | prompt constraints and docs | Do not implement runtime adapters yet. |
| Preserve omission vs explicit disabled | `CONFIRMED` | required policy | existing semantics docs | Do not normalize omitted `activates` to `BTN_UNSPECIFIED`. |
| Preserve remap order | `SOURCE_CONFIRMED` | required for duplicate physical semantics | `src/core/InputMode.cpp` | Reordering can change first-entry-wins behavior. |
| Senscope neutral Profile JSON direct mapping | `OUT_OF_SCOPE` | not claimed | prompt constraints | Do not claim direct mapping to Glyph JSON. |

## Summary Of Known Facts Pre-Filled

- Current native Ultimate Tilt1/Tilt2 hardware smoke test passed.
- Current MVP layout uses physical `BTN_RF3 -> BTN_LT1` and `BTN_RF4 -> BTN_LT2`.
- RF5 physical identity remains ambiguous.
- Both-held LT1+LT2 observed table is recorded but is not a new desired semantic.
- No push automation is allowed or added.
- Omitted `activates` outbound policy remains unresolved.
- Explicit `BTN_UNSPECIFIED` no-op behavior is source-confirmed.
