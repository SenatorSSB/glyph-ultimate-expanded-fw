# G8f3 - Mode-Specific Vs Generic Capability Audit

Status: docs-only source audit
Date: 2026-05-23

## Scope

This document is docs-only. It clarifies why selected-mode support cannot automatically satisfy a generic backend capability claim.

Generic backend support requires evidence that a capability is available as a backend-level primitive independent of one selected mode's hardcoded behavior, debug-only prototype path, or transport serialization. The current source primarily shows selected mode classes producing `OutputState` values, then transports encoding those values.

## Comparison

| surface | exact raw left-stick output appears possible? | user-configurable? | hardcoded? | selected-runtime-only? | generic backend primitive or mode behavior? |
| --- | --- | --- | --- | --- | --- |
| Ultimate | Yes, for specific hardcoded byte coordinates assigned by the Ultimate mode | No generic arbitrary coordinate entry found in this mode | Yes: coordinate formulas and constants in `src/modes/Ultimate.cpp:61-265` | Yes | Mode behavior |
| CustomControllerMode | Partially source-backed: selected axes can be driven by `stick_range` and analog modifiers | Partially: direction mappings, range, and modifiers come from `CustomModeConfig` | Mixed: algorithm is fixed, data is config-driven | Yes | Mode behavior |
| SenscopePrototype | Yes, for exact example-profile table entries when the prototype mode is selected | No active generic user surface proven | Yes: local bindings and example profile path are prototype-scoped | Yes, and current manual debug selection is disabled | Selected prototype behavior |
| transport/report layer | Transports can carry or transform values supplied by `OutputState` | No, transport does not choose target coordinates | Transport encoding is fixed per backend | N/A | Transport-specific serialization |

## Surface Notes

Ultimate:
- `Ultimate::UpdateAnalogOutputs` calls `UpdateDirections` with fixed constants, then assigns `outputs.leftStickX/Y` using hardcoded formulas. Source: `src/modes/Ultimate.cpp:61-265`.
- This proves mode-specific byte-coordinate assignment only.

CustomControllerMode:
- Direction buttons and `stick_range` feed `UpdateDirections`; analog modifiers select an axis and multiply values around neutral. Source: `src/modes/CustomControllerMode.cpp:69-113`.
- This supports a config-driven selected mode, but not a proven first-class 9-way table of arbitrary x/y pairs.

SenscopePrototype:
- The prototype builds a local direction/modifier request, resolves an example profile coordinate, and writes it to `outputs.leftStickX/Y`. Source: `src/modes/SenscopePrototype.cpp:24-130` and `src/modes/SenscopePrototype.cpp:181-190`.
- The active manual debug selector is behind `constexpr false`. Source: `src/core/mode_selection.cpp:35` and `src/core/mode_selection.cpp:170-174`.

Transport/report layer:
- GameCube copies `OutputState` left-stick bytes into `stick_x/stick_y`. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:59-65`.
- Nintendo Switch, DInput, and XInput each encode the same fields differently. Sources: `HAL/pico/src/comms/NintendoSwitchBackend.cpp:142-146`, `HAL/pico/src/comms/DInputBackend.cpp:52-58`, `HAL/pico/src/comms/XInputBackend.cpp:67-70`.
- This is value transport, not target realization.

## Promotion Rule

To promote a claim from `MODE_SPECIFIC` to `GENERIC_BACKEND`, evidence must show all of the following:

1. A generic source path, outside one mode's selected implementation, that accepts or represents desired left-stick x/y targets.
2. Deterministic source-backed rules mapping target coordinates to output fields, including failure modes.
3. Evidence that the capability applies across the claimed backend scope, not only Ultimate, CustomControllerMode, SenscopePrototype, or one transport.
4. Source refs for limits, clamping, transforms, neutral handling, and unsupported cases.

Without that evidence, evaluator claims must stay mode-scoped or unknown.

## Do Not Promote

Do not promote these to generic backend capability:

- Prototype static/example tables.
- Debug-only or compile-time disabled selected paths.
- One official mode assigning `OutputState` fields.
- CustomControllerMode behavior without proof of complete target representability.
- Transport layer serializing whatever `OutputState` it receives.
- A byte field existing in `OutputState` without a generic realization rule.

## Evaluator Status Handling

Recommended diagnostics/status behavior:

- `MODE_SCOPE_MISMATCH`: use when a neutral profile asks for generic backend support but the only evidence is Ultimate, CustomControllerMode, or SenscopePrototype behavior.
- `REPRESENTABILITY_UNKNOWN`: use when fields or selected-mode formulas exist, but arbitrary target representation is not proven.
- `SOURCE_BACKED`: use only when the claim is scoped correctly and has direct source refs.

Conservative examples:

| requested claim | available evidence | recommended evaluator result |
| --- | --- | --- |
| generic exact raw left-stick realization | byte fields plus selected-mode assignments | `REPRESENTABILITY_UNKNOWN` or `MODE_SCOPE_MISMATCH` depending on request scope |
| Ultimate can assign specific byte coordinates | `Ultimate::UpdateAnalogOutputs` direct assignments | `SOURCE_BACKED`, `MODE_SPECIFIC` |
| SenscopePrototype exact example table path | prototype resolver and output write | `SOURCE_BACKED`, `SELECTED_PROTOTYPE_ONLY` |
| GC report can carry mode-produced stick bytes | GC backend copies fields | `SOURCE_BACKED`, `TRANSPORT_SPECIFIC` |

## Conclusion

Mode-specific support is real source evidence, but it is not generic backend support. The evaluator should fail closed unless the requested scope matches the source-backed scope.
