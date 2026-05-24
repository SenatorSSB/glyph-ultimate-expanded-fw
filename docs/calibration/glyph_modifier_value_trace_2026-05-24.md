# Glyph Modifier Value Trace - 2026-05-24

## Scope

This document traces modifier-related schema, default examples, and runtime application paths relevant to future custom Ultimate `TILT`/`Tilt2` work. It is read-only/source-trace documentation. No firmware behavior is implemented here.

## Confirmed From Source/Proto

| File path | Symbol/function/message/field | Meaning | Kind | Why it matters for future `TILT`/`Tilt2` |
| --- | --- | --- | --- | --- |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` | `enum DigitalOutput` / `GP_A` through `GP_RSTICK_CLICK` | Custom mode digital outputs are gamepad output slots, not Glyph physical buttons. | Schema-only | Future custom mode definitions would bind physical buttons to these generic outputs rather than Ultimate-specific named actions. |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` | `enum StickDirectionButton` / `SD_LSTICK_*`, `SD_RSTICK_*` | Custom mode has ordered left-stick and right-stick direction slots. | Schema-only | Provides direction-button mapping surface, but not arbitrary coordinate tables. |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` | `enum AnalogAxis` / `AXIS_LSTICK_X`, `AXIS_LSTICK_Y`, `AXIS_RSTICK_X`, `AXIS_RSTICK_Y`, `AXIS_LTRIGGER`, `AXIS_RTRIGGER` | Modifier target axis names. | Schema-only | `TILT`/`Tilt2` storage can only target one axis per `AnalogModifier` in the current schema. |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` | `enum ModifierCombinationMode` | Defines `COMBINATION_MODE_COMPOUND` and `COMBINATION_MODE_OVERRIDE`; comments say unspecified currently defaults to compound. | Schema-only | Gives source-backed names for multi-modifier resolution, but exact runtime math still needs runtime source. |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` | `message AnalogTriggerMapping` / `button`, `trigger`, `value` | Maps a button to an analog trigger value. | Schema-only | Trigger values are separate from stick modifier storage. |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` | `message AnalogModifier` / `buttons`, `axis`, `multiplier`, `combination_mode` | A modifier is a held-button combo, one target axis, a float multiplier, and a combination mode. | Schema-only | This is the main current schema surface for custom analog modifiers. |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` | `message CustomModeConfig` / `digital_button_mappings`, `stick_direction_mappings`, `analog_trigger_mappings`, `modifiers`, `stick_range`, `button_combo_mappings` | Custom mode maps buttons to digital outputs, stick directions, analog triggers, modifiers, a base stick range, and combo outputs. | Schema-only | Future `TILT`/`Tilt2` work must fit this surface or require an explicitly approved schema/runtime change. |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.options` | `AnalogModifier.buttons max_count:3`, `CustomModeConfig.modifiers max_count:20`, `CustomModeConfig.stick_range int_size:IS_8` | Nanopb generated capacity and integer-width options. | Schema/generation options | Establishes local generated limits for current `glyph_mk6` build. |
| `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h` | `typedef struct _AnalogModifier` | Generated struct contains `buttons_count`, `buttons[3]`, `AnalogAxis axis`, `float multiplier`, `ModifierCombinationMode combination_mode`. | Generated build artifact | Confirms local generated C/C++ field names used by firmware source. |
| `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h` | `typedef struct _CustomModeConfig` | Generated struct contains count/value arrays for digital mappings, stick directions, analog trigger mappings, modifiers, stick range, and combo mappings. | Generated build artifact | Confirms local generated storage shape; not durable source authority. |
| `src/core/mode_selection.cpp` | `set_mode(..., GameModeConfig &mode_config, Config &config)` / `case MODE_CUSTOM` | Selects `CustomControllerMode` only when `custom_mode_config` is in range and indexes `config.custom_modes[custom_mode_config - 1]`. | Runtime behavior | Establishes how custom-mode config reaches runtime. This is a candidate path if future work uses `MODE_CUSTOM`. |
| `src/modes/CustomControllerMode.cpp` | `CustomControllerMode::SetConfig` | Stores a pointer to `CustomModeConfig` and precomputes masks for modifier buttons and combo mappings. | Runtime behavior | Modifier activation is based on all configured buttons held; empty button lists cannot activate because `all_buttons_held` requires a nonzero mask. |
| `src/modes/CustomControllerMode.cpp` | `CustomControllerMode::UpdateDigitalOutputs` | Applies button-combo mappings first, ignores buttons consumed by active combos, then maps ordered inputs to `DigitalOutput` slots. | Runtime behavior | Digital mappings and modifier/button-combo filtering interact before analog modifier application. |
| `src/modes/CustomControllerMode.cpp` | `CustomControllerMode::UpdateAnalogOutputs` | Uses `stick_direction_mappings` and `stick_range` to call `UpdateDirections`, then applies analog modifiers and analog trigger mappings. | Runtime behavior | This is the current source-backed runtime location where `CustomModeConfig.modifiers` are applied. |
| `HAL/pico/include/util/state_util.hpp` | `axis_pointer(AnalogAxis axis)` | Maps `AnalogAxis` values to `OutputState` fields: left stick, right stick, and analog triggers. | Runtime helper | Confirms modifier axes mutate `OutputState` byte fields. |
| `include/core/state.hpp` | `OutputState::analog_axes` / `leftStickX`, `leftStickY`, `rightStickX`, `rightStickY`, `triggerLAnalog`, `triggerRAnalog` | Analog outputs are `uint8_t` fields initialized to stick neutral `128,128,128,128` and triggers `0,0`. | Runtime data structure | Any modifier math is ultimately written into byte-valued output state fields. |
| `src/modes/Ultimate.cpp` | `Ultimate::UpdateAnalogOutputs` | Hard-coded Ultimate mode sets left/right stick coordinates from input and mode-specific modifier buttons. | Runtime behavior | Native Ultimate mode already contains hard-coded tilt-like values, but not config-backed custom `AnalogModifier` definitions. |
| `src/modes/Ultimate.cpp` | Comments `Horizontal Tilts = 36`, `Vertical Shield Tilt = 51`, `MY Horizontal Tilts`, `MY Vertical Tilts` | Existing source comments name tilt-related values in Ultimate mode. | Runtime behavior comments | Useful source evidence that tilt-like values exist in hard-coded Ultimate logic. This branch does not choose final `TILT`/`Tilt2` values. |

## Confirmed From Tracked Repo Examples

| File path | Symbol/example | Meaning | Kind | Why it matters |
| --- | --- | --- | --- | --- |
| `config/glyph/common/include/glyph_overrides.hpp` | `default_config.game_mode_configs` entry with `.mode_id = MODE_ULTIMATE`, `.name = "Ultimate"` | Default Glyph Ultimate profile exists as firmware default config. | Default-config | Confirms default Ultimate is native `MODE_ULTIMATE`, not custom mode. |
| `config/glyph/common/include/glyph_overrides.hpp` | Ultimate `.socd_pairs_count = 4` with `BTN_LF3/BTN_LF1`, `BTN_LF2/BTN_RF4`, `BTN_RT3/BTN_RT5`, `BTN_RT2/BTN_RT4`, all `SOCD_2IP` | Default Ultimate SOCD pairs are present. | Default-config | Must not be changed for this branch; future runtime patch must avoid SOCD changes unless explicitly requested. |
| `config/glyph/common/include/glyph_overrides.hpp` | Ultimate `.button_remapping_count = 5` with `BTN_MB1`, `BTN_LF8`, `BTN_LF7`, `BTN_LF6`, `BTN_LT6` remapped to `BTN_UNSPECIFIED` | Default Ultimate unmaps specific physical/menu buttons. | Default-config | Examples are remap evidence only; omitted/unspecified activation semantics are not changed here. |
| `config/glyph/common/include/glyph_overrides.hpp` | Ultimate `.menu_button_icon` includes `OUT_HOME`, `OUT_XB_BACK`, `OUT_START` | Output icon names appear in default menu display metadata. | Default-config | `OUT_*` names are UI/output option metadata, not custom analog modifier definitions. |
| `docs/calibration/fixtures/GlyphUserProfilesUlt-filled.json` | Ultimate `gameModeConfigs` entry with `modeId: MODE_ULTIMATE` | Calibration fixture contains native Ultimate profile. | Tracked JSON fixture | Fixture supports parser/remap checks; it has no custom modifier arrays. |
| `docs/calibration/fixtures/GlyphUltFilled2.json` | Ultimate `gameModeConfigs` entry with `modeId: MODE_ULTIMATE` | Second calibration fixture contains native Ultimate profile. | Tracked JSON fixture | Fixture supports parser/remap checks; it has no custom modifier arrays. |
| `docs/sources/raw/GlyphUserProfiles.json` | Top-level keys: `gameModeConfigs`, `communicationBackendConfigs`, `keyboardModes`, `rgbConfigs`, defaults, brightness/dashboard | Captured profile JSON lacks `customModes`/`customModeConfigs` in this repo snapshot. | Tracked JSON example | Parser modifier/custom-mode accessors are deferred because no fixture structure is present to regression-check. |

No tracked default/fixture examples found in this branch define `CustomModeConfig.modifiers`, `AnalogModifier`, `analog_trigger_mappings`, `stick_direction_mappings`, or `stick_range` in JSON. No tracked example names `TILT`, `Tilt2`, `flipper`, or an overflow modifier definition.

## Inferred From Naming Only

- `AnalogModifier.multiplier` likely scales the named axis because the proto comment says "multiplier" and runtime multiplies axis deltas by it. The exact numeric safety envelope is not established by schema alone.
- `COMBINATION_MODE_OVERRIDE` appears to replace an axis result using the current output sign and `stick_range * multiplier`; this is source-backed for `CustomControllerMode`, but whether that behavior is desirable for future `TILT`/`Tilt2` is not inferred here.
- `OUT_*` names in `OutputOption`/menu icon metadata look like display/output labels, not custom modifier names. They are not evidence of a `TILT`/`Tilt2` implementation.
- Existing hard-coded Ultimate comments such as "Horizontal Tilts" and "MY Vertical Tilts" indicate current mode-specific values, but this branch does not infer final Senscope or user layout semantics from them.

## Still Unknown / Not Safe Yet

- No source-backed custom modifier named `TILT` or `Tilt2` was found.
- No source-backed `flipper` field, message, function, or modifier definition was found in active proto or runtime paths.
- No explicit clamp/saturation guard was found around `CustomControllerMode` modifier writes to `uint8_t` output fields.
- Overflow/wrap behavior for assigning modifier math results back into `uint8_t OutputState` fields is not documented by a repo source comment or test. Treat as blocked for future flipper/overflow-dependent work.
- The exact final Tilt1/Tilt2 values are not selected in this branch.
- Whether future implementation should extend native `MODE_ULTIMATE`, use `MODE_CUSTOM`, or add a new reviewed profile mechanism remains a design decision requiring source/domain review.

## Runtime Modifier Application Trace

Candidate runtime path for schema-backed custom modifiers:

1. `src/core/mode_selection.cpp`
   - Consumes: `GameModeConfig.mode_id`, `GameModeConfig.custom_mode_config`, `Config.custom_modes_count`, `Config.custom_modes`.
   - Produces/mutates: selected backend game mode.
   - Behavior class: mode selection/config dispatch.
   - Source-backed fact: `MODE_CUSTOM` calls `custom_mode.SetConfig(mode_config, config.custom_modes[mode_config.custom_mode_config - 1])` when the one-based index is valid.

2. `src/modes/CustomControllerMode.cpp` / `SetConfig`
   - Consumes: `CustomModeConfig.modifiers`, `CustomModeConfig.button_combo_mappings`.
   - Produces/mutates: `_custom_mode_config`, `_modifier_button_masks`, `_button_combo_mappings_masks`.
   - Behavior class: generic custom controller config setup.
   - Source-backed fact: modifier button masks are made from each modifier's button list.

3. `src/modes/CustomControllerMode.cpp` / `UpdateDigitalOutputs`
   - Consumes: `InputState.buttons`, custom `button_combo_mappings`, `digital_button_mappings`.
   - Produces/mutates: `OutputState.buttons`, `_buttons_to_ignore`, `_filtered_buttons`.
   - Behavior class: button combos and digital output mapping.
   - Source-backed fact: active button combos set one `DigitalOutput` and remove combo buttons from later normal mapping and analog modifier input via `_filtered_buttons`.

4. `src/modes/CustomControllerMode.cpp` / `UpdateAnalogOutputs`
   - Consumes: `_filtered_buttons`, `stick_direction_mappings`, `stick_range`, `modifiers`, `analog_trigger_mappings`, nunchuk state.
   - Produces/mutates: `OutputState.leftStickX/Y`, `rightStickX/Y`, `triggerLAnalog/RAnalog`.
   - Behavior class: left-stick, C-stick/right-stick, trigger, and generic analog modifier path.
   - Source-backed fact: direction buttons establish base stick positions with `ANALOG_STICK_NEUTRAL +/- stick_range`; modifiers then mutate individual axes selected by `axis_pointer`.

5. `HAL/pico/include/util/state_util.hpp` / `axis_pointer`
   - Consumes: `AnalogAxis`.
   - Produces/mutates: returns pointer-to-member for one `OutputState` analog field.
   - Behavior class: generic analog axis mapping.
   - Source-backed fact: left stick, right stick, and analog triggers can be selected by schema axis.

Modifier combination behavior in `CustomControllerMode`:

- `COMBINATION_MODE_OVERRIDE`: computes `SIGNUM(outputs.*axis)` and assigns `ANALOG_STICK_NEUTRAL + stick_range * modifier.multiplier * sign`.
- `COMBINATION_MODE_COMPOUND` and `COMBINATION_MODE_UNSPECIFIED`: assign `ANALOG_STICK_NEUTRAL + (outputs.*axis - ANALOG_STICK_NEUTRAL) * modifier.multiplier`.
- `all_buttons_held` requires `button_mask != 0`, so an empty modifier button list does not activate in this runtime path.

Overflow/clamp status:

- Explicit clamp behavior: not found for `CustomControllerMode` modifier math.
- Explicit overflow/wrap behavior: not found as a documented behavior claim or test.
- Storage type: `OutputState` analog axes are `uint8_t`.
- Safety conclusion: future flipper or overflow-dependent modifier behavior is blocked until source/test evidence exists.

Flipper status:

- No `flipper` symbol or field was found in active proto, generated config header, tracked default config, calibration fixtures, or runtime modifier code.
- Any flipper behavior remains unknown and unsafe to implement from this branch.

Custom `TILT`/`Tilt2` implementation-location status:

- Known candidate for schema-backed custom-mode modifiers: `src/modes/CustomControllerMode.cpp`.
- Known native Ultimate hard-coded analog logic location: `src/modes/Ultimate.cpp`.
- Not yet safe/decided: final implementation location for custom Ultimate `TILT`/`Tilt2`. A runtime patch would require explicit design approval and source-authority pinning first.

