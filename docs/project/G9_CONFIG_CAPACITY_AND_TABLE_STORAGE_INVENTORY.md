# G9 - Config Capacity and Table Storage Inventory

Status: complete (docs/source-inventory only)  
Date: 2026-05-23  
Branch: `docs/glyph-config-capacity-g9`  
Implementation status: no firmware, protobuf schema, runtime adapter, evaluator, or platform build changes were made.

## 1. Title and status

This is the G9 config capacity and table storage inventory for future G7-style controller logic engine data.

This document is inventory and feasibility-boundary analysis only. It is not an implementation plan or schema-change approval.

## 2. Scope

Reviewed:
- Required project contracts and prior docs: `AGENTS.md`, queue/contract/stop-boundary docs, and G1-G7 milestone docs.
- Required source/config files listed in the batch instructions.
- Protobuf/nanopb sources and generated artifacts discovered in this repo workspace:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.options`
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.c`

Assessed:
- Whether existing source-backed config structures plausibly fit G7-style logic table storage needs.
- Current visible count/capacity limits.
- Persistence and configurator validation boundaries.
- What is source-backed vs inferred vs unknown.

Not implemented or decided:
- No firmware code changes.
- No protobuf/config schema changes.
- No runtime adapter or evaluator code.
- No export/push workflow additions.
- No Senscope game-semantic source changes.

Explicitly: no config/schema/source/runtime implementation was performed.

## 3. Why G9 exists

G7 described a future custom logic engine that may need explicit directional tables, modifier-combination profiles, and rule-driven output selection.

G7 also allowed a conservative path: compile-time prototype first, then config-backed storage later only if source capacity and constraints are clear.

G9 exists to inspect current source and answer: is there clear existing config capacity for G7-like data, or should early prototypes stay compile-time until storage constraints are better proven?

G9 preserves G7 safety constraints: no macros, no timing automation, no toggles, and current-frame logic only.

## 4. Source basis

Inspected files (required set and directly relevant neighbors):
- `platformio.ini`
- `config/glyph/common/include/glyph_overrides.hpp`
- `config/glyph/common/src/config.cpp`
- `config/glyph/env.ini`
- `HAL/pico/include/config_defaults.hpp`
- `HAL/pico/include/core/Persistence.hpp`
- `HAL/pico/src/core/Persistence.cpp`
- `HAL/pico/include/comms/ConfiguratorBackend.hpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `include/modes/CustomControllerMode.hpp`
- `src/modes/CustomControllerMode.cpp`
- `include/core/InputMode.hpp`
- `src/core/InputMode.cpp`
- `include/core/state.hpp`
- `docs/sources/source-manifest.json`
- `docs/sources/raw/GlyphUserProfiles.json`
- `src/core/mode_selection.cpp` (custom-mode and count use path)
- `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
- `.pio/libdeps/glyph_mk6/HayBox-proto/config.options`
- `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
- `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.c`

Where defaults live:
- Baseline Pico defaults: `HAL/pico/include/config_defaults.hpp` (`default_config`).
- Glyph overrides/defaults: `config/glyph/common/include/glyph_overrides.hpp` (`default_config`, `glyph_default_config()`).
- Runtime global config init: `config/glyph/common/src/config.cpp` (`Config config = glyph_default_config();`).

Where persistence lives:
- `HAL/pico/include/core/Persistence.hpp`
- `HAL/pico/src/core/Persistence.cpp`

Where configurator get/set lives:
- `HAL/pico/include/comms/ConfiguratorBackend.hpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`

Where CustomControllerMode consumes config:
- `include/modes/CustomControllerMode.hpp`
- `src/modes/CustomControllerMode.cpp`
- Mode dispatch/index resolution: `src/core/mode_selection.cpp`

## 5. Current config object inventory

Source-backed config object/field inventory relevant to G9:

1. `Config`
- Source symbols: `Config` message/struct with:
  - `game_mode_configs[]`, `communication_backend_configs[]`, `custom_modes[]`, `keyboard_modes[]`, `rgb_configs[]`
  - `default_backend_config`, `default_usb_backend_config`, `rgb_brightness`
- Source paths:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` (`message Config`)
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h` (`typedef struct _Config`)

2. `GameModeConfig`
- Source symbols:
  - `mode_id`, `name`, `socd_pairs[]`, `button_remapping[]`, `activation_binding[]`
  - `custom_mode_config`, `keyboard_mode_config`, `rgb_config`
  - `layout_plate`, `applicable_backends[]`, `menu_button_icon[]`
- Source paths:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`

3. `CustomModeConfig`
- Source symbols:
  - `digital_button_mappings[]`
  - `stick_direction_mappings[]`
  - `analog_trigger_mappings[]`
  - `modifiers[]`
  - `stick_range`
  - `button_combo_mappings[]`
- Source paths:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`

4. Button remapping
- Source symbols:
  - `GameModeConfig.button_remapping[]`
  - runtime application in `InputMode::HandleRemap(...)`
- Source paths:
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `src/core/InputMode.cpp`

5. SOCD pairs
- Source symbols:
  - `GameModeConfig.socd_pairs[]`
  - runtime application in `InputMode::HandleSocd(...)`
- Source paths:
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `src/core/InputMode.cpp`

6. Custom modes
- Source symbols:
  - `Config.custom_modes[]`, `Config.custom_modes_count`
  - `GameModeConfig.custom_mode_config` (1-based index semantics)
  - `MODE_CUSTOM` gate and index checks
- Source paths:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `src/core/mode_selection.cpp`
  - `HAL/pico/src/comms/ConfiguratorBackend.cpp`

7. Button combo mappings
- Source symbols:
  - `CustomModeConfig.button_combo_mappings[]`
  - runtime consumption in `CustomControllerMode::UpdateDigitalOutputs(...)`
- Source paths:
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `src/modes/CustomControllerMode.cpp`

8. Digital button mappings
- Source symbols:
  - `CustomModeConfig.digital_button_mappings[]`
  - runtime consumption in `CustomControllerMode::UpdateDigitalOutputs(...)`
- Source paths:
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `src/modes/CustomControllerMode.cpp`

9. Stick direction mappings
- Source symbols:
  - `CustomModeConfig.stick_direction_mappings[]`
  - runtime consumption in `CustomControllerMode::UpdateAnalogOutputs(...)`
- Source paths:
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `src/modes/CustomControllerMode.cpp`

10. Analog modifiers
- Source symbols:
  - `CustomModeConfig.modifiers[]`
  - `AnalogModifier.buttons[]`, `axis`, `multiplier`, `combination_mode`
  - runtime consumption in `CustomControllerMode::UpdateAnalogOutputs(...)`
- Source paths:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `src/modes/CustomControllerMode.cpp`

11. Analog trigger mappings
- Source symbols:
  - `CustomModeConfig.analog_trigger_mappings[]`
  - runtime consumption in `CustomControllerMode::UpdateAnalogOutputs(...)`
- Source paths:
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `src/modes/CustomControllerMode.cpp`

12. Backend configs
- Source symbols:
  - `CommunicationBackendConfig.backend_id`, `default_mode_config`, `activation_binding[]`
  - `Config.communication_backend_configs[]`
- Source paths:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `HAL/pico/src/comms/ConfiguratorBackend.cpp`
  - `HAL/pico/src/comms/backend_init.cpp`

13. Keyboard modes
- Source symbols:
  - `Config.keyboard_modes[]`, `KeyboardModeConfig.buttons_to_keycodes[]`
  - `GameModeConfig.keyboard_mode_config`
- Source paths:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `src/core/mode_selection.cpp`
  - `HAL/pico/src/comms/ConfiguratorBackend.cpp`

14. RGB configs
- Source symbols:
  - `Config.rgb_configs[]`, `RgbConfig.button_colors[]`, `animation`, `speed`
  - `GameModeConfig.rgb_config`
- Source paths:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
  - `config/glyph/common/include/glyph_overrides.hpp`

## 6. Existing capacity / count limits

Source-backed discovered limits:

| Item | Source-backed limit/value | Source path | Notes |
|---|---:|---|---|
| `Config.game_mode_configs` | `max_count: 30` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| Glyph default `game_mode_configs_count` | `13` | `config/glyph/common/include/glyph_overrides.hpp` | Active Glyph default value. |
| Mode activation masks array | `10` slots | `src/core/mode_selection.cpp` (`mode_activation_masks[10]`) | Potential mismatch vs default count 13 and proto max 30. |
| `Config.communication_backend_configs` | `max_count: 15` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| Glyph default `communication_backend_configs_count` | `8` | `config/glyph/common/include/glyph_overrides.hpp` | Active Glyph default value. |
| `Config.custom_modes` | `max_count: 10` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| Glyph explicit `custom_modes_count` | not explicitly set | `config/glyph/common/include/glyph_overrides.hpp` | Inferred zero-init unless loaded config overrides. |
| `Config.keyboard_modes` | `max_count: 10` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| Glyph default `keyboard_modes_count` | `1` | `config/glyph/common/include/glyph_overrides.hpp` | Active Glyph default value. |
| `Config.rgb_configs` | `max_count: 30` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| Glyph default `rgb_configs_count` | `13` | `config/glyph/common/include/glyph_overrides.hpp` | Active Glyph default value. |
| `GameModeConfig.socd_pairs` | `max_count: 10` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| SOCD state array | `10` slots | `include/core/InputMode.hpp` (`_socd_states[10]`) | Matches proto SOCD pair limit. |
| `GameModeConfig.button_remapping` | `max_count: 60` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| `GameModeConfig.activation_binding` | `max_count: 4` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| `GameModeConfig.applicable_backends` | `max_count: 15` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| `GameModeConfig.menu_button_icon` | `max_count: 7` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Fixed length set true in options. |
| `CustomModeConfig.digital_button_mappings` | `max_count: 18` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | One input per digital output slot order. |
| `CustomModeConfig.stick_direction_mappings` | `max_count: 8` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | LS/RS directional slot list. |
| `CustomModeConfig.analog_trigger_mappings` | `max_count: 4` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| `CustomModeConfig.button_combo_mappings` | `max_count: 5` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| Combo mask cache array | `5` slots | `include/modes/CustomControllerMode.hpp` (`_button_combo_mappings_masks[5]`) | Matches proto combo count limit. |
| `CustomModeConfig.modifiers` | `max_count: 20` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| Modifier mask cache array | `10` slots | `include/modes/CustomControllerMode.hpp` (`_modifier_button_masks[10]`) | Potential mismatch vs proto max 20. |
| `AnalogModifier.buttons` | `max_count: 3` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Per-modifier combo depth. |
| `ButtonComboMapping.buttons` | `max_count: 3` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Per-combo button count. |
| `KeyboardModeConfig.buttons_to_keycodes` | `max_count: 60` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| `RgbConfig.button_colors` | `max_count: 60` | `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | Proto/nanopb limit. |
| LittleFS partition size (board setting) | `0.5m` | `platformio.ini` (`board_build.filesystem_size = 0.5m`) | Shared FS budget; not config-only budget. |
| Encoded `Config` max size | `UNKNOWN` | `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h` (`Config_size depends on runtime parameters`) | No fixed compile-time max in inspected header. |

## 7. Persistence and configurator path

Save/load path (source-backed):
- `Persistence::SaveConfig(Config&)`:
  - `pb_get_encoded_size(...)`
  - writes LittleFS `config.bin`
  - writes header (`config_size`, `config_crc`)
  - protobuf body via `pb_encode(...)`
  - CRC calculated over protobuf body and header rewritten
  - Source: `HAL/pico/src/core/Persistence.cpp`, `HAL/pico/include/core/Persistence.hpp`
- `Persistence::LoadConfig(Config&)`:
  - open `config.bin`
  - `CheckSavedConfig(...)` validates length + CRC
  - `config = Config_init_default`
  - `pb_decode(...)` into config
  - Source: `HAL/pico/src/core/Persistence.cpp`
- `Persistence::LoadConfigRaw(...)`:
  - streams stored protobuf payload after header offset
  - Source: `HAL/pico/src/core/Persistence.cpp`

Configurator path (source-backed):
- `ConfiguratorBackend::SendReport()` dispatches commands.
- `CMD_GET_CONFIG` -> `HandleGetConfig()`:
  - requires `persistence.CheckSavedConfig()`
  - writes `CMD_SET_CONFIG` + raw protobuf bytes via `LoadConfigRaw(...)`
- `CMD_SET_CONFIG` -> `HandleSetConfig()`:
  - resets runtime config to `Config_init_default`
  - decodes incoming protobuf with `pb_decode(...)`
  - validates index relationships:
    - `default_backend_config <= communication_backend_configs_count`
    - each backend `default_mode_config <= game_mode_configs_count`
    - keyboard/custom mode index allowed only with correct `mode_id`
    - keyboard/custom indexes must be within `keyboard_modes_count` and `custom_modes_count`
  - saves via `persistence.SaveConfig(...)`
  - returns `CMD_SUCCESS` or `CMD_ERROR`
- Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp`

What this proves:
- Device-side binary config persistence exists.
- Device-side config get/set transport exists.
- There is basic structural validation for top-level index relationships.

What this does not prove:
- Stable public host export/import contract.
- Full schema/version migration strategy.
- Capacity-safe validation for all nested custom-mode payload shapes.
- Approved vendor export format or push workflow.

## 8. CustomControllerMode config consumption

`CustomControllerMode` currently consumes:

1. Combo mappings
- `button_combo_mappings[]` are converted to masks and checked with `all_buttons_held(...)`.
- Matching combo sets one `digital_output` and ignores combo buttons for normal mapping in that frame.
- Source: `src/modes/CustomControllerMode.cpp`

2. Digital mappings
- `digital_button_mappings[]` maps ordered outputs `(DigitalOutput)(output + 1)` from configured buttons.
- Source: `src/modes/CustomControllerMode.cpp`

3. Stick direction mappings
- `stick_direction_mappings[]` feeds directional button lookup for LS/RS directions.
- `UpdateDirections(...)` computes analog min/neutral/max output using configured `stick_range`.
- Source: `src/modes/CustomControllerMode.cpp`, `src/core/ControllerMode.cpp`

4. Analog modifiers
- `modifiers[]` are active when all modifier buttons are held.
- `COMBINATION_MODE_OVERRIDE`: sets axis using sign and `stick_range * multiplier`.
- `COMBINATION_MODE_COMPOUND` (and default): compounds from current axis deviation.
- Source: `src/modes/CustomControllerMode.cpp`

5. Analog trigger mappings
- `analog_trigger_mappings[]` map buttons to `TRIGGER_LT`/`TRIGGER_RT` values.
- Digital trigger bits force analog trigger to `255`.
- Source: `src/modes/CustomControllerMode.cpp`

6. Nunchuk override
- If connected: `triggerLDigital |= nunchuk_z`.
- If connected: `leftStickX/Y` are overridden by nunchuk axes.
- Source: `src/modes/CustomControllerMode.cpp`

7. Combination limits / unknowns
- Combo mask cache array is fixed at 5 (`_button_combo_mappings_masks[5]`) and aligns with proto `max_count:5`.
- Modifier mask cache array is fixed at 10 (`_modifier_button_masks[10]`) while proto options allow `modifiers max_count:20`.
- No source-backed per-direction exact coordinate table field is consumed in this mode.
- Source: `include/modes/CustomControllerMode.hpp`, `src/modes/CustomControllerMode.cpp`, `.pio/libdeps/glyph_mk6/HayBox-proto/config.options`

## 9. G7 storage requirement matrix

| G7 design need | Existing source-backed field/path | Fit | Gaps | Recommendation |
|---|---|---|---|---|
| exact 9-way left-stick table per modifier combination | `CustomModeConfig.stick_direction_mappings`, `stick_range`, `modifiers` | NOT_SUPPORTED_BY_CURRENT_CONFIG | No explicit per-direction coordinate table keyed by modifier-combination + direction. | Use compile-time table prototype first; treat schema-backed tables as future option. |
| direction 5 table entry | Implicit neutral path in `ControllerMode::UpdateDirections(...)` | NOT_SUPPORTED_BY_CURRENT_CONFIG | No first-class direction-5 table field in current custom config model. | Keep as compile-time rule/table concept until schema decision. |
| multiple modifier-combination profiles | `CustomModeConfig.modifiers[]` with button sets | PARTIAL_FIT | Supports held-button modifier conditions, but not profile tables with explicit priority/fallback semantics. | Prototype profile selection in compile-time logic first. |
| highest-priority defined subset fallback | no direct field | NOT_SUPPORTED_BY_CURRENT_CONFIG | No explicit fallback-priority model for undefined full combinations. | Keep fallback semantics outside current config model in early prototype. |
| table-defined flipper/off-direction profiles | no direct field | NOT_SUPPORTED_BY_CURRENT_CONFIG | No source-backed table primitives for off-direction coordinate profiles. | Treat as future schema extension candidate only. |
| Force Up-B fixed exact coordinate rule | no direct field | NOT_SUPPORTED_BY_CURRENT_CONFIG | No explicit fixed-coordinate override rule entity. | Compile-time prototype rule first; schema later only with approval. |
| Force Up-B upward-Y plus post-SOCD horizontal rule | no direct field | NOT_SUPPORTED_BY_CURRENT_CONFIG | No explicit rule model for this two-part transform. | Keep in compile-time engine prototype first. |
| digital multi-output button/chord | `digital_button_mappings[]`, `button_combo_mappings[]` | PARTIAL_FIT | Combo mapping object emits one digital output per entry; multi-output needs repeated entries / duplicated mapping patterns. | Plausible with caveats; validate authoring semantics before relying on it. |
| one physical input emits multiple direction roles before SOCD | `stick_direction_mappings[]` (same button can be reused across slots), SOCD in `InputMode::HandleSocd` | DIRECT_FIT | None for basic role fan-out behavior in current model. | Reusable for prototype with caution on mode-specific assumptions. |
| right-stick/C-stick exact output table | `stick_direction_mappings[]`, `stick_range`, `modifiers` | PARTIAL_FIT | Right stick is directional/min-max driven; no explicit exact coordinate table per direction/profile. | Compile-time exact tables first if needed. |
| layer/Mode held-condition role map | `GameModeConfig.activation_binding[]`; custom combo mappings | PARTIAL_FIT | Has mode activation and per-frame combos, but no explicit generic layer-role map structure. | Treat as partial primitive, not full G7 layer model. |
| analog output priority categories | pipeline order + modifier combination modes | PARTIAL_FIT | No explicit global priority category schema. | Keep priority policy in prototype logic before schema changes. |
| validation diagnostics | `ConfiguratorBackend::HandleSetConfig()` index checks + error messages | PARTIAL_FIT | Validation covers top-level index relations, not deep semantic table validity. | Add design-level validation spec before schema extension. |
| transport-neutral logical outputs | `DigitalOutput` enum + internal `OutputState` mapping path | DIRECT_FIT | Transport-neutral at logic layer exists, but backend-specific packing still separate. | Reuse existing logical output concept in prototype docs. |

## 10. Compile-time prototype vs config-backed path

| Path | Pros | Cons |
|---|---|---|
| Compile-time constants prototype | Lowest schema risk, fastest way to validate logic semantics, avoids premature host/config coupling, easier to keep source authority explicit while behavior is unstable. | Low configurability, not user-editable via current config flow, not a long-term storage solution. |
| Existing config-backed extension (without schema changes) | Reuses existing persistence/get-set path and existing custom-mode fields. | Current fields do not cleanly model core G7 table needs; multiple fit gaps; internal fixed-array mismatches suggest capacity safety concerns. |
| Future protobuf/schema extension (docs first) | Could model G7 tables directly and explicitly, with clear validation contracts. | Highest migration/compat/tooling risk; requires explicit approval; requires nanopb generation, storage budget, validation, and compatibility planning first. |

Conservative readout:
- Implementation risk: lowest with compile-time prototype.
- Configurability: highest with schema extension, but highest risk.
- Source authority clarity: highest when prototype behavior is clearly separated from unsupported current config assumptions.
- Memory/storage risk: unknown for table-heavy schema without explicit size budgeting.
- Validation complexity: significantly higher for config-backed table model.
- Migration path: safer to prove logic shape first, then design schema against proven constraints.

## 11. Recommended near-term path

Recommended: **compile-time prototype first** (design/prototype path), then re-evaluate config-backed storage after capacity and validation constraints are reviewed.

Reason:
- Current source does not clearly prove direct config fit for the core G7 table model.
- There are source-backed count-constraint mismatches (`mode_activation_masks[10]` vs default `game_mode_configs_count = 13`; `_modifier_button_masks[10]` vs proto `modifiers max_count:20`) that argue for caution before config-backed expansion.

## 12. Source-authority gaps

- Exact config capacity unknowns:
  - Effective safe runtime maxima are unclear where code-side helper arrays are smaller than proto limits.
- Nanopb/protobuf generation workflow unknowns:
  - Proto/options are visible, generated files are visible, but full reproducible generation workflow contract was not fully traced in this batch.
- Configurator UI/tooling compatibility unknowns:
  - Device protocol exists, but host-side compatibility guarantees are not established here.
- Stable export/import format unknowns:
  - No approved public format contract established by inspected files.
- Storage/memory limits unknown:
  - No fixed encoded `Config_size`; no explicit table-budget guardrails for future large custom tables.
- Validation location unknown:
  - Top-level index validation exists; deep custom-table semantic validation location is not defined.
- Host-side push/export still unsupported:
  - Device-side get/set does not by itself establish approved push/export workflow.

## 13. Risks

- Overfitting G7 design to current `CustomControllerMode` behavior.
- Assuming `GlyphUserProfiles.json` is complete schema authority (it is copied reference evidence only).
- Changing protobuf/schema too early before logic shape and constraints are proven.
- Adding config-backed complexity before logic behavior is validated.
- Accidentally implying export/push workflow support from device-side handlers alone.
- Exceeding flash/RAM/storage or unsafe buffer assumptions with large combo/table payloads.

## 14. Recommended next batches

1. G9R: human review of these capacity and mismatch findings.
2. G10: compile-time prototype design refinement (still docs-only, no firmware code).
3. G10b: protobuf/config extension design (docs-only) only if config-backed path still appears plausible after G9R.
4. G11: minimal firmware prototype only after explicit approval.
5. G8: evaluator prototype remains separate and should wait until backend target shape is stable.

Do not proceed automatically to G8/G10/G10b/G11 without explicit approval.

## 15. Verification

Commands run (representative):
- `git checkout configurator`
- `git pull origin configurator`
- `git status --short --branch`
- `git branch --show-current`
- `git branch --list docs/glyph-config-capacity-g9`
- `git checkout -b docs/glyph-config-capacity-g9`
- `rg --files docs/project | sort`
- `sed -n '1,260p' ...` / targeted `sed` continuations for required docs and source files
- `find . -maxdepth 8 -type f | rg 'config\\.pb\\.(h|c)$|config\\.proto$|config\\.options$'`
- `rg -n '...'` targeted searches for config fields, counts, persistence/configurator paths, and custom mode mappings

Build/test status:
- Firmware build was not run because this is a docs-only inventory task and must not be build-affecting.
