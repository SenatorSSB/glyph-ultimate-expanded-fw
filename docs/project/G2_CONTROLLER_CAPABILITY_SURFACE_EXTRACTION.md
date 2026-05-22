# G2 — Controller Capability Surface Extraction

Status: complete (documentation/source extraction)  
Date: 2026-05-23  
Branch inspected: `docs/senscope-glyph-baseline`  
Authority scope: source-backed extraction only; this is not capability approval and not runtime adapter implementation.

## 1. Scope

Inspected source/doc paths (required set plus directly referenced support files):
- `platformio.ini`
- `include/core/state.hpp`
- `include/core/InputMode.hpp`
- `src/core/InputMode.cpp`
- `include/core/ControllerMode.hpp`
- `src/core/ControllerMode.cpp`
- `src/core/socd.cpp`
- `include/core/mode_selection.hpp`
- `src/core/mode_selection.cpp`
- `include/core/CommunicationBackend.hpp`
- `src/core/CommunicationBackend.cpp`
- `include/modes/Ultimate.hpp`
- `src/modes/Ultimate.cpp`
- `include/modes/CustomControllerMode.hpp`
- `src/modes/CustomControllerMode.cpp`
- `config/glyph/common/include/glyph_overrides.hpp`
- `config/glyph/common/src/config.cpp`
- `config/glyph/env.ini`
- `HAL/pico/include/config_defaults.hpp`
- `HAL/pico/src/core/Persistence.cpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `HAL/pico/src/comms/backend_init.cpp`
- `docs/sources/source-manifest.json`
- `docs/sources/raw/ESAM1.cpp`
- `docs/sources/raw/ESAM1.hpp`
- `docs/sources/raw/GlyphUserProfiles.json`
- Supporting refs used for extraction clarity:
  - `include/core/socd.hpp`
  - `HAL/pico/include/util/state_util.hpp`
  - `include/core/config_utils.hpp`
  - `src/core/config_utils.cpp`
  - `HAL/pico/include/core/Persistence.hpp`
  - `HAL/pico/include/comms/backend_init.hpp`
  - `HAL/pico/include/comms/ConfiguratorBackend.hpp`
  - `HAL/pico/include/core/KeyboardMode.hpp`
  - `include/modes/CustomKeyboardMode.hpp`
  - `src/modes/CustomKeyboardMode.cpp`
  - `HAL/pico/src/comms/{DInputBackend,XInputBackend,NintendoSwitchBackend,GamecubeBackend,N64Backend,NesBackend,SnesBackend}.cpp`

Intentionally not decided:
- No runtime backend adapter implementation.
- No firmware behavior change.
- No neutral profile schema change.
- No vendor export-format or push workflow product decision.
- No gameplay semantic interpretation or semantic-source changes.

Game semantics and Senscope semantic-source authority are out of scope for this document.

## 2. Capability claim classification

This document uses:
- `SOURCE_BACKED`: directly shown by inspected repo source/docs.
- `INFERRED`: reasonable interpretation from source structure, but not explicitly guaranteed.
- `UNKNOWN`: not proven by current inspected source.
- `UNSUPPORTED_BY_CURRENT_SOURCE`: inspected source does not show support for the capability as stated.
- `OUT_OF_SCOPE`: capability concerns game semantics or authority boundaries outside this extraction task.

## 3. Input button / physical input surface

- `SOURCE_BACKED`: `InputState` exposes a 64-bit `buttons` bitfield with named physical fields `lf1..lf16`, `rf1..rf16`, `lt1..lt8`, `rt1..rt8`, `mb1..mb12`.  
  Source: `include/core/state.hpp`
- `SOURCE_BACKED`: Nunchuk input surface includes `nunchuk_connected`, `nunchuk_c`, `nunchuk_z`, plus `int8_t nunchuk_x`, `int8_t nunchuk_y`.  
  Source: `include/core/state.hpp`
- `SOURCE_BACKED`: Button operations (`get_button`, `set_button`, masks) are enum-indexed bit operations, with `BTN_UNSPECIFIED` explicitly handled.  
  Source: `HAL/pico/include/util/state_util.hpp`
- `SOURCE_BACKED`: Input scan pipeline updates shared `InputState` from each `InputSource` and increments `counter`.  
  Source: `src/core/CommunicationBackend.cpp::ScanInputs`
- `INFERRED`: “modifier-like” physical buttons are mode-defined, not globally typed; e.g., `lt1/lt2` used as modifiers in `Ultimate`, and config-driven modifier masks in `CustomControllerMode`.  
  Source: `src/modes/Ultimate.cpp`, `src/modes/CustomControllerMode.cpp`

## 4. Digital output surface

- `SOURCE_BACKED`: `OutputState` digital bitfield includes `a,b,x,y,buttonL,buttonR,triggerLDigital,triggerRDigital,start,select,home,capture,dpad*,leftStickClick,rightStickClick,leftStick*/rightStick*,modX,modY`.  
  Source: `include/core/state.hpp`
- `SOURCE_BACKED`: `ControllerMode::UpdateOutputs` pipeline order is remap -> SOCD -> digital mapping -> analog mapping.  
  Source: `src/core/ControllerMode.cpp::UpdateOutputs`
- `SOURCE_BACKED`: `Ultimate::UpdateDigitalOutputs` is hardcoded per-field mapping from physical inputs to `OutputState` fields, including D-pad layer behavior.  
  Source: `src/modes/Ultimate.cpp::UpdateDigitalOutputs`
- `SOURCE_BACKED`: `CustomControllerMode::UpdateDigitalOutputs` supports:
  - button-combo -> single digital output mapping
  - digital output map by index (`digital_button_mappings`)
  - combo-pressed buttons excluded from normal mapping via `_buttons_to_ignore` / `_filtered_buttons`
  - nunchuk Z OR into `triggerLDigital`
  Source: `src/modes/CustomControllerMode.cpp::UpdateDigitalOutputs`
- `UNKNOWN`: Universal digital-output behavior across all controller modes is not proven from `Ultimate` and `CustomControllerMode` alone.

## 5. Analog output surface

- `SOURCE_BACKED`: `OutputState` analog fields are 6 bytes: `leftStickX/Y`, `rightStickX/Y`, `triggerLAnalog`, `triggerRAnalog`; default initializer is `{128,128,128,128,0,0}`.  
  Source: `include/core/state.hpp`
- `SOURCE_BACKED`: Base directional synthesis sets both sticks to neutral first, then sets min/max by directional booleans.  
  Source: `src/core/ControllerMode.cpp::UpdateDirections`
- `SOURCE_BACKED`: `Ultimate` defines `ANALOG_STICK_MIN=28`, `ANALOG_STICK_NEUTRAL=128`, `ANALOG_STICK_MAX=228` and applies many hardcoded coordinate offsets by modifier/context.  
  Source: `src/modes/Ultimate.cpp`
- `SOURCE_BACKED`: `Ultimate` sets analog triggers to `140` when digital trigger buttons are pressed; else `0`.  
  Source: `src/modes/Ultimate.cpp`
- `SOURCE_BACKED`: `CustomControllerMode` computes stick min/max from `stick_range` around neutral `128`, applies config-driven `AnalogModifier` operations on selected axes, supports analog trigger mappings, then forces analog trigger to `255` when digital trigger output is active.  
  Source: `src/modes/CustomControllerMode.cpp`, `HAL/pico/include/util/state_util.hpp::axis_pointer`
- `SOURCE_BACKED`: Both `Ultimate` and `CustomControllerMode` override left stick with nunchuk X/Y when connected.  
  Source: `src/modes/Ultimate.cpp`, `src/modes/CustomControllerMode.cpp`
- `UNKNOWN`: Generic exact realization of arbitrary raw coordinates across all modes/backends is not proven.

## 6. SOCD and direction-resolution surface

- `SOURCE_BACKED`: SOCD pair handling is config-driven via `GameModeConfig.socd_pairs`.  
  Source: `src/core/InputMode.cpp::HandleSocd`
- `SOURCE_BACKED`: Implemented SOCD types:
  - `SOCD_NEUTRAL`
  - `SOCD_2IP`
  - `SOCD_2IP_NO_REAC`
  - `SOCD_DIR1_PRIORITY`
  - `SOCD_DIR2_PRIORITY`
  Source: `src/core/InputMode.cpp`, `include/core/config_utils.hpp::socd_name`
- `SOURCE_BACKED`: SOCD algorithms are in `src/core/socd.cpp`; 2IP variants maintain memory via `socd::SocdState` fields (`was_dir1/was_dir2/lock_dir1/lock_dir2`).  
  Source: `include/core/socd.hpp`, `src/core/socd.cpp`
- `SOURCE_BACKED`: SOCD is applied before digital/analog output generation in controller mode pipeline.  
  Source: `src/core/ControllerMode.cpp::UpdateOutputs`
- `UNKNOWN`: Cross-mode semantic intent of SOCD settings (game-specific policy meaning) is not determined here.

## 7. Remapping surface

- `SOURCE_BACKED`: Remapping uses `GameModeConfig.button_remapping` in `InputMode::HandleRemap`.  
  Source: `src/core/InputMode.cpp::HandleRemap`
- `SOURCE_BACKED`: Anti-macro guard exists: if a physical button is already remapped once, later remaps for the same physical button are ignored.  
  Source: `src/core/InputMode.cpp::HandleRemap` (comment and logic via `physical_buttons_already_remapped`)
- `SOURCE_BACKED`: Remap supports many-to-one target activation (target remains pressed if another mapped physical input is active).  
  Source: `src/core/InputMode.cpp::HandleRemap`
- `SOURCE_BACKED`: Ordering relative to other stages is remap before SOCD and before output synthesis.  
  Source: `src/core/ControllerMode.cpp::UpdateOutputs`
- `UNKNOWN`: Any external UI/host constraints on remap authoring are not proven solely by this source set.

## 8. Mode system surface

- `SOURCE_BACKED`: Mode selection is based on activation button-hold masks built from `GameModeConfig.activation_binding`.  
  Source: `src/core/mode_selection.cpp::setup_mode_activation_bindings`, `select_mode`
- `SOURCE_BACKED`: Built-in controller mode instances in selection module include `Melee20Button`, `ProjectM`, `Ultimate`, `FgcMode`, `RivalsOfAether`, `Rivals2`, `Smash64`, and `CustomControllerMode`; `CustomKeyboardMode` is also present.  
  Source: `src/core/mode_selection.cpp`
- `SOURCE_BACKED`: `MODE_KEYBOARD` is gated to DInput backend and valid `keyboard_mode_config` index.  
  Source: `src/core/mode_selection.cpp::set_mode(GameModeConfig&, Config&)`
- `SOURCE_BACKED`: `MODE_CUSTOM` is gated to valid `custom_mode_config` index and uses `config.custom_modes[...]`.  
  Source: `src/core/mode_selection.cpp::set_mode(GameModeConfig&, Config&)`
- `SOURCE_BACKED`: `ConfiguratorBackend` validates `keyboard_mode_config` and `custom_mode_config` against mode IDs and count bounds during `CMD_SET_CONFIG`.  
  Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp::HandleSetConfig`
- `UNKNOWN`: Default Glyph config in `glyph_overrides.hpp` appears to define no active `MODE_CUSTOM` entries; runtime use of `CustomControllerMode` therefore depends on loaded/received config content.

## 9. Ultimate mode capability surface

- `SOURCE_BACKED`: Digital mapping is hardcoded (`rt1->a`, `rf1->b`, `rf2->x`, `rf6->y`, etc.).  
  Source: `src/modes/Ultimate.cpp::UpdateDigitalOutputs`
- `SOURCE_BACKED`: D-pad layer activates when `(lt1 && lt2) || nunchuk_c`; in that layer, `rt2/rt3/rt4/rt5` drive D-pad and C-stick analog is neutralized in analog stage.  
  Source: `src/modes/Ultimate.cpp`
- `SOURCE_BACKED`: Left-stick analog behavior is hardcoded for many modifier/chord contexts (`lt1`, `lt2`, shield buttons, `rt*`, `rf1`) with explicit byte offsets around 128.
  Source: `src/modes/Ultimate.cpp::UpdateAnalogOutputs`
- `SOURCE_BACKED`: Right-stick behavior includes diagonal override and specific angled behaviors tied to modifier contexts.  
  Source: `src/modes/Ultimate.cpp::UpdateAnalogOutputs`
- `SOURCE_BACKED`: Nunchuk connected state overrides left stick coordinates.  
  Source: `src/modes/Ultimate.cpp::UpdateAnalogOutputs`
- `UNKNOWN`: This does not prove generic backend-wide support for arbitrary 9-way modifier tables; behavior is mode-specific and hardcoded.

## 10. CustomControllerMode capability surface

- `SOURCE_BACKED`: Supports button-chord mappings (`button_combo_mappings`) that emit single digital outputs and suppress normal behavior for involved input buttons.  
  Source: `src/modes/CustomControllerMode.cpp::UpdateDigitalOutputs`
- `SOURCE_BACKED`: Supports direct digital-output mappings from configured physical buttons (`digital_button_mappings`).  
  Source: `src/modes/CustomControllerMode.cpp::UpdateDigitalOutputs`
- `SOURCE_BACKED`: Supports stick-direction mapping from configured buttons (`stick_direction_mappings`) and configurable stick range.  
  Source: `src/modes/CustomControllerMode.cpp::UpdateAnalogOutputs`
- `SOURCE_BACKED`: Supports analog modifiers with `COMBINATION_MODE_OVERRIDE` and `COMBINATION_MODE_COMPOUND` behavior paths.  
  Source: `src/modes/CustomControllerMode.cpp::UpdateAnalogOutputs`
- `SOURCE_BACKED`: Supports analog trigger mappings and digital-trigger-to-255 analog promotion.
  Source: `src/modes/CustomControllerMode.cpp::UpdateAnalogOutputs`
- `SOURCE_BACKED`: Nunchuk-connected state overrides left stick coordinates; nunchuk Z contributes to L digital trigger.  
  Source: `src/modes/CustomControllerMode.cpp`
- `UNKNOWN`: Whether `CustomModeConfig` can express full Senscope-style 9-way per-modifier directional tables is not proven from inspected default config artifacts.

## 11. Config / persistence / configurator surface

- `SOURCE_BACKED`: Config is protobuf-backed (`Config`, `GameModeConfig`, etc.) and used broadly across mode/backends.  
  Source: `include/core/state.hpp`, `src/core/InputMode.cpp`, `src/core/mode_selection.cpp`, `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `SOURCE_BACKED`: Pico default config baseline exists in `HAL/pico/include/config_defaults.hpp`; Glyph-specific default override exists in `config/glyph/common/include/glyph_overrides.hpp`, with `glyph_default_config()` used to initialize global `config`.  
  Source: `HAL/pico/include/config_defaults.hpp`, `config/glyph/common/include/glyph_overrides.hpp`, `config/glyph/common/src/config.cpp`
- `SOURCE_BACKED`: Persistence stores config to LittleFS `config.bin` with size+CRC header and protobuf body (`SaveConfig`, `LoadConfig`, `LoadConfigRaw`, validation checks).  
  Source: `HAL/pico/include/core/Persistence.hpp`, `HAL/pico/src/core/Persistence.cpp`
- `SOURCE_BACKED`: Configurator backend supports get/set config commands, decodes protobuf config stream, performs structural validation, and persists accepted config.  
  Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `INFERRED`: Firmware has a device-side config transport path suitable for external configurator tooling.
- `UNKNOWN`: Public/stable external configurator contract, UI/tooling compatibility, and vendor export compatibility are not proven by this source set alone.

## 12. Backend / transport surface

- `SOURCE_BACKED`: Communication backend abstraction separates input scan, mode update, and report send (`CommunicationBackend`, virtual `SendReport`).  
  Source: `include/core/CommunicationBackend.hpp`, `src/core/CommunicationBackend.cpp`
- `SOURCE_BACKED`: Backend selection/initialization includes configurable button-hold selection, USB fallback, console detection path, primary+secondary backend initialization, and default mode assignment.  
  Source: `HAL/pico/include/comms/backend_init.hpp`, `HAL/pico/src/comms/backend_init.cpp`
- `SOURCE_BACKED`: Backend implementations discovered and selected in init path include `DInput`, `XInput`, `NintendoSwitch`, `Gamecube`, `N64`, `NES`, `SNES`, `Configurator`.  
  Source: `HAL/pico/src/comms/backend_init.cpp`
- `SOURCE_BACKED`: Multiple backend report implementations consume `OutputState` stick/dpad/digital/trigger fields (with backend-specific scaling/packing).  
  Source: `HAL/pico/src/comms/{DInputBackend,XInputBackend,NintendoSwitchBackend,GamecubeBackend,N64Backend,NesBackend,SnesBackend}.cpp`
- `UNKNOWN`: Exact host-side behavior/compatibility for every transport stack and descriptor path is not fully characterized here.

## 13. Staged reference material surface

- `SOURCE_BACKED`: `docs/sources/source-manifest.json` marks `ESAM1.hpp`, `ESAM1.cpp`, `GlyphUserProfiles.json` as copied references.
- `SOURCE_BACKED`: `ESAM1` source expresses a controller-mode style with hardcoded analog/digital logic, modifier interactions, SOCD-oriented constructor pattern, and nunchuk override.
  Source: `docs/sources/raw/ESAM1.cpp`, `docs/sources/raw/ESAM1.hpp`
- `SOURCE_BACKED`: `GlyphUserProfiles.json` contains staged profile/config-like data (mode configs, backend configs, keyboard/rgb blocks).  
  Source: `docs/sources/raw/GlyphUserProfiles.json`
- `INFERRED`: `ESAM1` appears to be historical/alternate behavior evidence (API signatures diverge from current `ControllerMode`/`InputState` usage in active sources).
- `SOURCE_BACKED`: ESAM1 is treated here as behavior evidence/source material, not direct modern profile-format authority.

## 14. Senscope-relevant capability matrix

| Capability | Status | Source refs | Notes |
|---|---|---|---|
| exact raw left-stick coordinate output | INFERRED | `include/core/state.hpp`, `src/core/ControllerMode.cpp`, `src/modes/Ultimate.cpp`, `src/modes/CustomControllerMode.cpp` | Byte-level outputs are written directly, but generic arbitrary-coordinate realization coverage is not proven. |
| full 9-way directional modifier table | UNSUPPORTED_BY_CURRENT_SOURCE | `src/modes/Ultimate.cpp`, `src/modes/CustomControllerMode.cpp` | Mode-specific hardcoded logic and config modifiers exist; no proven first-class generic 9-way table model found. |
| first-class neutral direction 5 | UNSUPPORTED_BY_CURRENT_SOURCE | `src/core/ControllerMode.cpp`, `include/core/state.hpp` | Neutral exists as centered analog output, but no explicit backend-level “direction 5” field. |
| non-center neutral output | UNKNOWN | `src/modes/Ultimate.cpp`, `src/modes/CustomControllerMode.cpp`, `docs/sources/raw/ESAM1.cpp` | Current active modes center neutral at 128 by default; ESAM1 reference shows alternate neutral-like values, but not proven for current runtime. |
| flipper transform | UNKNOWN | `src/modes/Ultimate.cpp`, `src/modes/CustomControllerMode.cpp`, `include/core/ControllerMode.hpp` | No explicit named flipper transform mechanism identified in inspected active source paths. |
| pre-SOCD Force Up-B override | UNKNOWN | `src/core/ControllerMode.cpp`, `src/core/InputMode.cpp`, `src/modes/Ultimate.cpp` | Pipeline order is remap->SOCD->mode outputs; no explicit “pre-SOCD Force Up-B” primitive identified. |
| dynamic button layers | SOURCE_BACKED | `src/modes/Ultimate.cpp`, `src/modes/CustomControllerMode.cpp`, `src/core/mode_selection.cpp` | Ultimate D-pad layer and combo-based suppression are source-backed; layer model is mode/config specific. |
| button chord rules | SOURCE_BACKED | `src/modes/CustomControllerMode.cpp`, `src/core/mode_selection.cpp`, `HAL/pico/include/util/state_util.hpp` | Chord masks used for combo mappings and mode activation bindings. |
| SOCD handling | SOURCE_BACKED | `src/core/InputMode.cpp`, `src/core/socd.cpp`, `include/core/socd.hpp` | Multiple SOCD strategies with per-pair memory. |
| static remapping | SOURCE_BACKED | `src/core/InputMode.cpp` | Config-driven button remap with anti-macro duplicate-physical guard. |
| analog multipliers/modifiers | SOURCE_BACKED | `src/modes/CustomControllerMode.cpp` | Analog modifiers and combination modes are implemented in CustomControllerMode. |
| right-stick/C-stick output | SOURCE_BACKED | `include/core/state.hpp`, `src/core/ControllerMode.cpp`, `src/modes/Ultimate.cpp`, `HAL/pico/src/comms/GamecubeBackend.cpp` | Right-stick outputs are represented and used; advanced behavior is mode-specific. |
| analog triggers | SOURCE_BACKED | `include/core/state.hpp`, `src/modes/Ultimate.cpp`, `src/modes/CustomControllerMode.cpp`, `HAL/pico/src/comms/{DInputBackend,XInputBackend,GamecubeBackend}.cpp` | Analog trigger fields exist and are consumed by multiple backends. |
| manual-entry support | INFERRED | `config/glyph/common/src/config.cpp`, `HAL/pico/src/comms/ConfiguratorBackend.cpp` | Firmware includes configurator command path and on-device menu/remap code; end-user manual-entry workflow contract not fully proven here. |
| export support | UNSUPPORTED_BY_CURRENT_SOURCE | `HAL/pico/src/comms/ConfiguratorBackend.cpp`, `docs/sources/source-manifest.json` | Raw protobuf get/set path exists; no source-backed vendor-specific export artifact workflow in inspected scope. |
| push-to-device support | INFERRED | `HAL/pico/src/comms/ConfiguratorBackend.cpp`, `HAL/pico/src/core/Persistence.cpp` | Device-side config write command path exists; host-side push tooling/protocol guarantees are not proven here. |

## 15. Risks and source-authority gaps

- Risk: treating `Ultimate` hardcoded behavior as generic backend capability.
  - Mitigation: keep claims mode-specific unless independently shown in generic/config-driven layers.
- Risk: treating `CustomControllerMode` as sufficient proof of exact full 9-way directional modifier realization.
  - Mitigation: require explicit proof of representational completeness against Senscope target data model.
- Risk: treating `GlyphUserProfiles.json` as full schema authority.
  - Mitigation: treat it as copied reference material; rely on active protobuf-backed runtime paths for current authority.
- Risk: mixing controller/backend constraints into Smash game semantics.
  - Mitigation: keep semantics out-of-scope; only classify backend capability/unknowns.
- Risk: assuming export/push workflows from firmware-side configurator handlers.
  - Mitigation: separate “device-side handler exists” from “public/stable toolchain supported.”

## 16. Recommended G3 inputs

G3 should consume:
- this source-backed capability matrix (with mode-specific caveats preserved),
- explicit unknowns/unsupported areas,
- realization status categories needed for neutral-profile comparison,
- clear boundary between adapter surface (config/backend translation) and evaluator surface (match/mismatch/unknown),
- diagnostics to distinguish:
  - exact representation,
  - mode-limited representation,
  - unsupported-by-current-source,
  - unknown due to missing authority.

## 17. Verification

Commands run:
- `git status --short --branch`: branch is `docs/senscope-glyph-baseline` tracking `origin/docs/senscope-glyph-baseline`; working tree initially clean.
- `git branch --show-current`: `docs/senscope-glyph-baseline`.
- `git remote -v`: `origin` and `upstream` remotes present.
- `git diff --stat`: clean before edits.
- `find include src config HAL docs scripts -maxdepth 4 -type f`: source inventory reviewed.
- Multiple targeted `sed -n` and `rg -n` inspections across required files and directly referenced support files.

Build verification:
- Not run (docs/source-extraction-only task; no firmware/code behavior change).
