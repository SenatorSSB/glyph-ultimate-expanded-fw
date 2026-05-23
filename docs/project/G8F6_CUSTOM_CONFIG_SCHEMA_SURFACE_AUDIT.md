# G8f6 - Custom Config Schema Surface Audit

Status: docs-only source audit
Date: 2026-05-24

## Scope

This document is docs-only and source-audit only. It inspects config/protobuf/schema surfaces available in this repository for `CustomControllerMode` capability modeling. It does not modify schemas, generated files, defaults, firmware source, host tooling, export workflows, push workflows, flashing paths, or Senscope-owned neutral profile schema.

This audit distinguishes four separate claims:

| claim type | meaning |
| --- | --- |
| runtime can read a field | active firmware source reads and uses the field |
| host/configurator can author a field | host-side UX or tool source proves the field can be edited by users |
| Senscope can safely generate a field | an approved adapter/export contract exists for Senscope to produce it |
| export/push is approved | an explicit approved workflow exists to move generated data to a device |

Device-side parser evidence alone does not prove host configurator UX, Senscope export authority, or push-to-device approval.

## Source Surfaces Inspected

| surface | path | finding | confidence |
| --- | --- | --- | --- |
| active CustomControllerMode runtime | `src/modes/CustomControllerMode.cpp` | reads `CustomModeConfig` direction mappings, `stick_range`, analog modifiers, analog triggers, and button combos | High |
| runtime declaration | `include/modes/CustomControllerMode.hpp` | stores a `CustomModeConfig` pointer and fixed mask arrays | High |
| active proto source from PlatformIO dependency | `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` | defines `CustomModeConfig`, `AnalogModifier`, direction enums, axis enums, config container, and custom mode reference path | High |
| nanopb options | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | sets max counts and integer widths for generated structs | High |
| generated nanopb header | `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h` | generated structs are present for current local build output | High for local build artifact, not source-of-truth schema |
| config transport | `HAL/pico/src/comms/ConfiguratorBackend.cpp` | decodes full `Config`, validates custom-mode references, saves accepted config | High |
| persistence | `HAL/pico/src/core/Persistence.cpp` | saves/loads protobuf config with size and CRC header | High |
| Glyph defaults | `config/glyph/common/include/glyph_overrides.hpp` | default Glyph config defines many built-in profiles and backend defaults; no `custom_modes_count` entry was found in this file by audit grep | High |
| base Pico defaults | `HAL/pico/include/config_defaults.hpp` | base defaults similarly define built-in profiles/backend defaults; no custom mode definitions found by audit grep | High |
| build config | `platformio.ini`, `config/glyph/env.ini` | Glyph env uses HayBox-proto dependency and generated config header path through PlatformIO/nanopb | High |

## CustomControllerMode Objects And Fields

### Direction Mappings

Schema: `StickDirectionButton` enumerates eight stick direction specifiers: four left-stick directions and four right-stick directions. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:270-284`.

`CustomModeConfig.stick_direction_mappings` is an ordered repeated button list, following the order of `StickDirectionButton`. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:447-450`.

Generated/local limits: `stick_direction_mappings` has max count 8 and stores button enum values as 8-bit generated fields. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.options:37-45` and `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h:437-441`.

Runtime read: `CustomControllerMode::UpdateAnalogOutputs` reads this array and maps each direction slot to booleans passed to `UpdateDirections`. Source: `src/modes/CustomControllerMode.cpp:69-84`.

Claim classification:
- runtime can read: `SOURCE_BACKED`;
- host/configurator can author: `UNKNOWN` from this repo alone;
- Senscope can safely generate: `OUT_OF_SCOPE` without explicit adapter approval;
- export/push approved: `UNSUPPORTED_BY_CURRENT_SOURCE` for this batch.

### Analog Modifiers

Schema: `AnalogModifier` contains `buttons`, one `axis`, a `multiplier`, and `combination_mode`. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:376-391`.

Schema: `AnalogAxis` includes left-stick X/Y, right-stick X/Y, and both trigger axes. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:286-297`.

Generated/local limits: up to 20 modifiers, with up to three buttons per modifier. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.options:12-15` and `.pio/libdeps/glyph_mk6/HayBox-proto/config.options:37-45`.

Runtime read: `SetConfig` precomputes modifier button masks; `UpdateAnalogOutputs` applies only held modifiers. Source: `src/modes/CustomControllerMode.cpp:16-20` and `src/modes/CustomControllerMode.cpp:86-113`.

Claim classification:
- runtime can read: `SOURCE_BACKED`;
- host/configurator can author: `UNKNOWN` from this repo alone;
- Senscope can safely generate: `OUT_OF_SCOPE` without explicit adapter approval;
- export/push approved: `UNSUPPORTED_BY_CURRENT_SOURCE` for this batch.

### Stick Range

Schema: `CustomModeConfig.stick_range` is the base stick range. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:455-457`.

Generated/local storage: `stick_range` is generated as `uint8_t`. Source: `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h:448-450`.

Runtime read: CustomControllerMode computes min, neutral, and max as `128 - stick_range`, `128`, and `128 + stick_range`. Source: `src/modes/CustomControllerMode.cpp:69-84`.

Claim classification:
- runtime can read: `SOURCE_BACKED`;
- host/configurator can author: `UNKNOWN` from this repo alone;
- Senscope can safely generate: `OUT_OF_SCOPE` without explicit adapter approval;
- export/push approved: `UNSUPPORTED_BY_CURRENT_SOURCE` for this batch.

### Modes And Layers

Schema: a general `GameModeConfig` can refer to a `CustomModeConfig` by a 1-based index into `Config.custom_modes`, valid only when the game mode selects the custom mode implementation. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:477-515`.

Generated config container: `Config` contains up to 30 game mode configs and up to 10 custom mode configs. Source: `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h:573-582` and `.pio/libdeps/glyph_mk6/HayBox-proto/config.options:58-61`.

Runtime selection: when a game mode config selects custom mode and the custom index is in range, mode selection calls `custom_mode.SetConfig(...)` with the referenced `config.custom_modes[...]`. Source: `src/core/mode_selection.cpp:129-137`.

Layer note: CustomControllerMode has button combo mappings and generic remap/SOCD pipeline support. This audit found no explicit CustomControllerMode field for Senscope-style named layers or a full modifier-role layer table. Treat layers beyond button masks/combos/remaps as `UNKNOWN` unless a later audit finds source.

### Button Combos And Digital Mappings

Schema: `CustomModeConfig.digital_button_mappings` maps ordered physical inputs to digital output slots. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:440-446`.

Schema: `ButtonComboMapping` maps a held button list to one digital output. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:393-400`.

Generated/local limits: digital mappings max 18; combo mappings max 5; combo buttons max 3. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.options:17-19` and `.pio/libdeps/glyph_mk6/HayBox-proto/config.options:37-45`.

Runtime read: combos can set one output and suppress normal behavior of involved buttons; digital mapping iterates output slots in order. Source: `src/modes/CustomControllerMode.cpp:35-56`.

### Analog Trigger Mappings

Schema: `AnalogTriggerMapping` maps one button to one trigger value. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:365-374`.

Runtime read: CustomControllerMode writes `outputs.triggerLAnalog` or `outputs.triggerRAnalog`, then digital trigger outputs promote analog triggers to `255`. Source: `src/modes/CustomControllerMode.cpp:115-138`.

This is source-backed for trigger values, not for left-stick exact raw pair realization.

## Persistence And Device-Side Config Transport

`ConfiguratorBackend::HandleSetConfig` resets config defaults, decodes protobuf `Config`, validates default backend and mode/custom references, then saves the accepted config. Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:161-272`.

`ConfiguratorBackend::HandleGetConfig` can return raw saved config bytes after validation. Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:148-158`.

`Persistence::SaveConfig` writes a header and protobuf-encoded config body to LittleFS, then stores size and CRC. Source: `HAL/pico/src/core/Persistence.cpp:36-77`.

`Persistence::LoadConfig` validates saved config, resets to generated defaults, then decodes protobuf config into the global config object. Source: `HAL/pico/src/core/Persistence.cpp:80-110`.

Classification:
- device-side config get/set/persist path: `SOURCE_BACKED`;
- host/configurator UX for editing every CustomModeConfig field: `UNKNOWN` from this repo alone;
- Senscope export/push workflow: `OUT_OF_SCOPE` and `UNSUPPORTED_BY_CURRENT_SOURCE` for approval in this batch.

## Generated Proto/Header Refs And Unknowns

Generated/local header refs exist under `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`. They reflect the local build artifact and are useful for current struct layout and counts, but the source schema comes from `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` and options from `.pio/libdeps/glyph_mk6/HayBox-proto/config.options`.

Unknowns:
- whether an external host configurator UI exposes all CustomModeConfig fields;
- whether authoring constraints exist outside this repo;
- whether multiple local `config.proto` copies with names like `config 2.proto` are stale artifacts or duplicate dependency files;
- whether a stable public export format exists outside this repo;
- whether Senscope should generate protobuf directly, generate a manual-entry guide, or not target this surface at all.

## Schema Fit For Senscope-Style Neutral Profiles

Source-backed fit:
- button-to-direction mapping;
- global range around center;
- per-axis analog scalar modifiers;
- button-mask gating for modifiers;
- custom mode selection by config reference;
- device-side config decode/persist path.

Not source-backed:
- arbitrary raw left-stick `(x,y)` pair per direction;
- non-center neutral raw pair as a first-class field;
- full 9-way table keyed by direction and modifier combination;
- host configurator UX support for authoring exact neutral profile targets;
- approved Senscope export/push workflow.

Conservative conclusion: the schema surface can support range/scalar CustomControllerMode modeling. It cannot currently be treated as a complete exact Senscope neutral profile realization schema.
