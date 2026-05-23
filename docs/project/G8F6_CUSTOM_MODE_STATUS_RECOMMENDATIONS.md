# G8f6 - Custom Mode Status Recommendations

Status: docs-only recommendation artifact
Date: 2026-05-24

## Scope

This document is docs-only and recommendation-only. It recommends evaluator/capability-model statuses for `CustomControllerMode` based on the G8f6 source audits. It does not recommend firmware changes, schema changes, default activation changes, export/push workflows, flashing workflows, or gameplay semantic changes.

Allowed statuses:
- `SOURCE_BACKED`
- `INFERRED`
- `UNKNOWN`
- `UNSUPPORTED_BY_CURRENT_SOURCE`
- `OUT_OF_SCOPE`

## Recommendations

| capability | recommended status | scope | source refs | caveats | evidence needed to upgrade |
| --- | --- | --- | --- | --- | --- |
| 1. CustomControllerMode exact arbitrary raw pair support | `UNSUPPORTED_BY_CURRENT_SOURCE` | `MODE_SPECIFIC` | `src/modes/CustomControllerMode.cpp:69-113`, `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:440-459` | Source exposes range/scalar behavior, not raw pair rows | A CustomControllerMode source path and schema field that accept raw X/Y targets per requested condition |
| 2. CustomControllerMode axis/range scalar support | `SOURCE_BACKED` | `MODE_SPECIFIC` | `src/modes/CustomControllerMode.cpp:69-84`, `src/core/ControllerMode.cpp:46-90`, `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:455-457` | `stick_range` is global and symmetric around center | Tests or docs for numeric edge cases could improve confidence, but base support is source-backed |
| 3. CustomControllerMode analog modifier support | `SOURCE_BACKED` | `MODE_SPECIFIC` | `src/modes/CustomControllerMode.cpp:86-113`, `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:376-391`, `HAL/pico/include/util/state_util.hpp:53-70` | Modifier support is per-axis scalar, not pair-coordinate support | Dedicated evaluator model for compound/override formulas and numeric limits |
| 4. CustomControllerMode non-center neutral support | `UNSUPPORTED_BY_CURRENT_SOURCE` for first-class raw neutral pair; `UNKNOWN` for incidental scalar outcomes | `MODE_SPECIFIC` | `src/core/ControllerMode.cpp:46-49`, `src/modes/CustomControllerMode.cpp:80-82`, `src/modes/CustomControllerMode.cpp:86-113` | Neutral is passed as 128; modifier-held no-direction outcomes are not a neutral table | Source-backed field or rule for neutral raw X/Y, plus tests proving selected behavior |
| 5. CustomControllerMode full 9-way table support | `UNSUPPORTED_BY_CURRENT_SOURCE` | `MODE_SPECIFIC` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:270-284`, `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:440-459`, `src/modes/CustomControllerMode.cpp:69-113` | Eight direction slots plus range/scalar formulas do not equal nine raw rows | First-class table schema and runtime lookup keyed by direction/modifier combination |
| 6. CustomControllerMode export support | `OUT_OF_SCOPE`; `UNSUPPORTED_BY_CURRENT_SOURCE` for this batch | `WORKFLOW` | `HAL/pico/src/comms/ConfiguratorBackend.cpp:148-272`, `HAL/pico/src/core/Persistence.cpp:36-110` | Device-side config get/set exists; no approved export artifact workflow is shown | Explicit export format, host tooling, safety rules, and approval |
| 7. CustomControllerMode push support | `OUT_OF_SCOPE`; `UNSUPPORTED_BY_CURRENT_SOURCE` for this batch | `WORKFLOW` | `HAL/pico/src/comms/ConfiguratorBackend.cpp:161-272`, `HAL/pico/src/core/Persistence.cpp:36-110` | Device-side set/persist path exists; host push workflow is not approved here | End-to-end host/device workflow, constraints, rollback/safety procedure, and approval |
| 8. Senscope neutral profile realization through CustomControllerMode | `UNKNOWN` for limited scalar/range representability; `UNSUPPORTED_BY_CURRENT_SOURCE` for exact arbitrary neutral profiles | `INTEGRATION_BOUNDARY` | `docs/project/G8F2_EXACT_RAW_LEFT_STICK_SOURCE_AUDIT.md`, `docs/project/G8F3_MODE_SPECIFIC_VS_GENERIC_CAPABILITY_AUDIT.md`, `docs/project/G8F6_CUSTOM_CONTROLLER_MODE_CAPABILITY_AUDIT.md`, `docs/project/G8F6_CUSTOM_ANALOG_MODIFIER_LIMITS.md` | Some profiles may fit range/scalar behavior, but exact arbitrary raw profile realization is not source-backed | A reviewed evaluator model, profile-by-profile proof, and explicit adapter/export approval if output generation is desired |

## Status Notes

`SOURCE_BACKED` is appropriate for CustomControllerMode range/scalar primitives because active runtime source and config schema both represent them.

`UNSUPPORTED_BY_CURRENT_SOURCE` is appropriate for exact arbitrary pair support and full 9-way raw tables because the inspected CustomModeConfig fields and runtime formulas lack such representation.

`UNKNOWN` is appropriate for host configurator authoring and limited incidental representability until a deeper host/configurator audit or evaluator proof exists.

`OUT_OF_SCOPE` is appropriate for export, push-to-device, flashing, product workflow, and Senscope schema ownership decisions in this batch.

## Recommended Evaluator Treatment

For a future non-runtime evaluator:
- model CustomControllerMode as a `MODE_SPECIFIC` backend target, not a generic backend exact-coordinate primitive;
- expose `stick_range` and per-axis analog modifiers as `SOURCE_BACKED` scalar primitives;
- report exact raw pair requirements as unsupported unless a specific target is proven by a reviewed scalar/range model;
- report full neutral profile realization as unknown or unsupported unless the profile fits the source-backed primitive set;
- do not generate config, export artifacts, or push data from these recommendations alone.

## Caveats

This document does not audit external host UI source. It does not prove a user-facing configurator can author all fields present in the device-side protobuf schema.

This document does not interpret gameplay meanings of any coordinates, directions, or modifiers.

This document does not decide whether Senscope should target CustomControllerMode. It only classifies current evidence for evaluator/capability-model use.
