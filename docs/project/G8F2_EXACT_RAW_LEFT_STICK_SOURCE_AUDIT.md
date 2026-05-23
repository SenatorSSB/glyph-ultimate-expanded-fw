# G8f2 - Exact Raw Left-Stick Source Audit

Status: docs-only source audit
Date: 2026-05-23

## Scope

This document is docs-only and source-audit only. It does not implement runtime behavior, enable SenscopePrototype, modify firmware source, alter config/protobuf defaults, add export/push workflows, flash hardware, or make gameplay semantic claims.

Audit question:

> Does active firmware source prove generic exact raw left-stick coordinate realization capability, or only mode-specific/prototype-specific paths?

Short answer: active source proves byte-shaped left-stick output fields and several selected mode paths that assign byte coordinate values. It does not prove a generic backend realization primitive that can accept arbitrary Senscope neutral targets and realize them across modes/backends.

## Source Findings

`OutputState` represents analog outputs as six `uint8_t` fields, with `leftStickX` and `leftStickY` sharing storage with `analog_axes[6]`. The initializer centers the two stick pairs at `128` and initializes triggers to `0`. Source: `include/core/state.hpp:143-154`.

`ControllerMode::UpdateOutputs` delegates output synthesis to the selected mode after remap and SOCD handling. Source: `src/core/ControllerMode.cpp:8-15`.

`ControllerMode::UpdateDirections` can set left-stick axes to caller-supplied min, neutral, or max byte values. This is a shared helper, not a generic arbitrary-coordinate target resolver. Source: `src/core/ControllerMode.cpp:30-70`.

`Ultimate::UpdateAnalogOutputs` calls `UpdateDirections` with fixed min/neutral/max values and then overwrites left-stick axes with hardcoded coordinate formulas in selected input contexts. Source: `src/modes/Ultimate.cpp:61-265`.

`CustomControllerMode::UpdateAnalogOutputs` derives min/max from configured `stick_range`, applies configured direction buttons, and then applies analog modifiers to selected axes using a multiplier. Source: `src/modes/CustomControllerMode.cpp:64-113`. This is config-driven mode behavior, but the inspected source does not prove full arbitrary pair assignment for every Senscope neutral target.

`SenscopePrototype` has a selected-only runtime path that resolves an example profile coordinate and writes `resolved_coordinate.x/y` into `outputs.leftStickX/Y`. Source: `src/modes/SenscopePrototype.cpp:94-130` and `src/modes/SenscopePrototype.cpp:156-190`. Manual prototype selection is guarded by a compile-time false flag. Source: `src/core/mode_selection.cpp:35` and `src/core/mode_selection.cpp:170-174`.

Transport backends consume `OutputState` after the active mode updates it. GameCube forwards left-stick bytes directly into the GC report fields. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:42-65`. Nintendo Switch, DInput, and XInput encode or transform the same fields in transport-specific ways. Sources: `HAL/pico/src/comms/NintendoSwitchBackend.cpp:142-146`, `HAL/pico/src/comms/DInputBackend.cpp:52-58`, `HAL/pico/src/comms/XInputBackend.cpp:67-70`.

## Evidence Table

| file/path | symbol/function | observed behavior | source-backed claim | scope | confidence |
| --- | --- | --- | --- | --- | --- |
| `include/core/state.hpp:143-154` | `OutputState` analog union | left-stick x/y are `uint8_t` fields initialized through `analog_axes` defaults | Firmware output state has byte-shaped left-stick coordinate fields | GENERIC_BACKEND | High |
| `src/core/ControllerMode.cpp:8-15` | `ControllerMode::UpdateOutputs` | active mode owns digital/analog output synthesis after remap and SOCD | Coordinate realization is selected-mode behavior in the current pipeline | GENERIC_BACKEND | High |
| `src/core/ControllerMode.cpp:30-70` | `ControllerMode::UpdateDirections` | helper writes neutral/min/max byte values from caller-provided constants | Shared helper supports centered/cardinal/diagonal mode outputs, not arbitrary target resolution by itself | MODE_SPECIFIC | High |
| `src/modes/Ultimate.cpp:61-265` | `Ultimate::UpdateAnalogOutputs` | hardcoded formulas assign left-stick x/y for modifier and direction contexts | Ultimate contains mode-specific byte-coordinate assignment | MODE_SPECIFIC | High |
| `src/modes/CustomControllerMode.cpp:64-113` | `CustomControllerMode::UpdateAnalogOutputs` | configured direction buttons, `stick_range`, and analog modifiers affect selected axes | CustomControllerMode has config-driven selected-mode analog behavior; full arbitrary coordinate coverage remains unproven | MODE_SPECIFIC | Medium |
| `src/modes/SenscopePrototype.cpp:94-130` | `TryResolveSenscopePrototypeLeftStickCoordinate` | resolves an example profile coordinate for selected prototype input state | Prototype has a source-backed selected path for exact example-profile coordinate lookup | SELECTED_PROTOTYPE_ONLY | High |
| `src/modes/SenscopePrototype.cpp:156-190` | `SenscopePrototype::UpdateAnalogOutputs` | writes resolved coordinate bytes into `outputs.leftStickX/Y` | Prototype can write resolved raw bytes when this mode is selected | SELECTED_PROTOTYPE_ONLY | High |
| `src/core/mode_selection.cpp:35,170-174` | prototype manual selection gate | manual selection branch is behind `constexpr false` | Prototype selected path is not reachable through current active manual selection gate | SELECTED_PROTOTYPE_ONLY | High |
| `HAL/pico/src/comms/GamecubeBackend.cpp:42-65` | `GamecubeBackend::SendReport` | copies `OutputState` left-stick bytes to GC report `stick_x/stick_y` | GC transport can carry mode-produced left-stick bytes | TRANSPORT_SPECIFIC | High |
| `HAL/pico/src/comms/NintendoSwitchBackend.cpp:142-146` | `NintendoSwitchBackend::SendReport` | scales and flips axes for Switch report | Switch transport does not pass left-stick fields through unchanged | TRANSPORT_SPECIFIC | High |
| `HAL/pico/src/comms/DInputBackend.cpp:52-58` | `DInputBackend::SendReport` | forwards x and flips y; triggers add 1 | DInput transport can carry values with transport-specific y inversion | TRANSPORT_SPECIFIC | High |
| `HAL/pico/src/comms/XInputBackend.cpp:67-70` | `XInputBackend::SendReport` | scales axes into XInput report fields | XInput transport transforms left-stick bytes into report-space values | TRANSPORT_SPECIFIC | High |
| current inspected source set | generic arbitrary coordinate resolver | no generic source path found that accepts arbitrary Senscope neutral x/y targets independent of selected mode | Generic exact raw realization remains not source-backed | UNKNOWN | High |

## Distinctions

Existing official modes:
- Official controller modes assign stick outputs inside their own mode classes. Ultimate has explicit hardcoded byte assignments; Melee/Rivals/FGC/64 paths show the same selected-mode pattern through `UpdateDirections` and hardcoded mode formulas. Examples: `src/modes/Melee20Button.cpp:79-125`, `src/modes/RivalsOfAether.cpp:69-115`, `src/modes/FgcMode.cpp:49-67`, `src/modes/64.cpp:52-70`.
- This evidence supports selected-mode coordinate assignment, not generic backend realization of arbitrary Senscope targets.

CustomControllerMode:
- CustomControllerMode is more config-driven than Ultimate, using configured direction buttons, `stick_range`, and analog modifiers. Source: `src/modes/CustomControllerMode.cpp:64-113`.
- The inspected source does not prove full arbitrary two-axis coordinate assignment for every modifier/direction entry. Treat exact raw coverage as mode/config-specific until deeper source-backed analysis proves otherwise.

SenscopePrototype:
- SenscopePrototype has a prototype-only exact coordinate lookup path for an example profile and writes resolved x/y bytes into left-stick output fields. Source: `src/modes/SenscopePrototype.cpp:94-130` and `src/modes/SenscopePrototype.cpp:181-190`.
- Current active selection keeps the manual debug path disabled. Source: `src/core/mode_selection.cpp:35` and `src/core/mode_selection.cpp:170-174`.
- This must not be promoted to generic backend support.

Transport backend reporting:
- Transport layers serialize or transform whatever `OutputState` they receive from the selected mode.
- Transport evidence can prove carrying/encoding behavior. It does not prove the backend can realize arbitrary Senscope neutral targets.

## Conservative Conclusion

Source-backed:
- Left-stick output fields are byte-shaped in `OutputState`.
- Mode code can assign byte-like left-stick coordinate values.
- GameCube transport copies mode-produced left-stick bytes into report fields.
- SenscopePrototype selected path can write resolved example-profile coordinates into `OutputState` when selected.

Not source-backed:
- Generic exact raw left-stick realization for arbitrary Senscope neutral coordinates.
- Generic full 9-way directional modifier table support in active official modes.
- Generic non-center neutral support.

## Unknowns And Stop Conditions

Unknowns:
- Whether CustomControllerMode can represent every required Senscope neutral target under concrete config constraints.
- Whether a stable host/configurator surface exposes enough controls for exact arbitrary coordinate entry.
- Whether any transport-specific host expectations would alter practical exactness outside the GC report path.

Stop conditions:
- Do not upgrade generic exact raw support without direct generic-scope source evidence.
- Do not treat prototype static tables as generic backend capability.
- Do not infer gameplay meaning from coordinate constants.
- Do not implement runtime adapters, firmware changes, export, push, or flashing workflows from this audit.
