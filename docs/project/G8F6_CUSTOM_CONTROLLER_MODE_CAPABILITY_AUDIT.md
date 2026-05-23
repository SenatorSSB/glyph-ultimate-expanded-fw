# G8f6 - CustomControllerMode Capability Audit

Status: docs-only source audit
Date: 2026-05-24

## Scope

This document is docs-only and source-audit only. It does not implement runtime behavior, modify firmware source/header files, alter config/protobuf/default activation, enable any prototype path, add export or push workflows, flash hardware, change the Senscope neutral profile schema, or make gameplay semantic claims.

Audit question:

> What can active `CustomControllerMode` source back today for Senscope-style neutral profile realization, especially exact raw left-stick coordinates, analog modifiers, neutral/non-center behavior, and full 9-way directional tables?

Short answer: `CustomControllerMode` source-backs a selected-mode, config-driven directional stick mapping with one global `stick_range`, plus per-axis analog multipliers selected by button masks. It does not source-back arbitrary two-axis raw coordinate assignment, non-center neutral, or a first-class full 9-way table of raw `(x,y)` pairs.

## Runtime Behavior

`CustomControllerMode::SetConfig` stores a `CustomModeConfig` pointer, delegates generic mode config to `InputMode::SetConfig`, and precomputes button masks for analog modifiers and button combo mappings. Source: `src/modes/CustomControllerMode.cpp:10-28`.

`ControllerMode::UpdateOutputs` runs remap, SOCD, digital output synthesis, and analog output synthesis in that order. Source: `src/core/ControllerMode.cpp:8-15`. This means CustomControllerMode analog behavior sees remapped and SOCD-cleaned inputs.

`CustomControllerMode::UpdateDigitalOutputs` may suppress normal mappings for buttons used in active combo mappings. It stores `_filtered_buttons`, then analog behavior reads direction and modifier buttons from `_filtered_buttons`. Source: `src/modes/CustomControllerMode.cpp:35-56` and `src/modes/CustomControllerMode.cpp:69-79`.

`CustomControllerMode::UpdateAnalogOutputs` reads eight configured stick direction button slots and passes booleans into `UpdateDirections`. Source: `src/modes/CustomControllerMode.cpp:69-84`.

`ControllerMode::UpdateDirections` sets both sticks to neutral, then assigns min/max per axis when directional booleans are active. Source: `src/core/ControllerMode.cpp:30-90`.

## Direction Inputs To Stick Axes

The config schema has eight ordered stick direction slots: left-stick up, down, left, right, then right-stick up, down, left, right. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:270-284`.

The runtime calls `GetDirectionButton(direction_buttons, SD_LSTICK_LEFT)`, `SD_LSTICK_RIGHT`, `SD_LSTICK_DOWN`, `SD_LSTICK_UP`, and the four right-stick equivalents, then passes the resulting held state to `UpdateDirections`. Source: `src/modes/CustomControllerMode.cpp:69-84` and `src/modes/CustomControllerMode.cpp:147-155`.

Capability claim: direction buttons are source-backed as button-to-direction mappings for both left and right stick. They are not source-backed as per-direction arbitrary raw coordinate entries.

## Stick Range

`stick_range` is read as `uint8_t` from `CustomModeConfig` and supplied to `UpdateDirections` as:

```text
min = 128 - stick_range
neutral = 128
max = 128 + stick_range
```

Source: `src/modes/CustomControllerMode.cpp:69-84`.

`UpdateDirections` then sets left-stick and right-stick axes to neutral by default, min when left/down is active, and max when right/up is active. Source: `src/core/ControllerMode.cpp:46-90`.

Capability claim: `stick_range` source-backs a symmetric scalar range around center for direction-button mapping. It is not a raw coordinate table, not axis-specific by itself, and not direction-combination-specific by itself.

## Analog Modifiers

`AnalogModifier` has a list of required buttons, one target axis, a float multiplier, and a combination mode. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:376-391`.

The generated header stores up to three buttons per modifier, one `AnalogAxis`, one `float multiplier`, and one `ModifierCombinationMode`. Source: `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h:369-384` and `.pio/libdeps/glyph_mk6/HayBox-proto/config.options:12-15`.

At runtime, a modifier applies only when all configured buttons are held in `_filtered_buttons`. Source: `src/modes/CustomControllerMode.cpp:86-94`.

The runtime maps the configured axis through `axis_pointer`. The helper supports left-stick X/Y, right-stick X/Y, and both analog triggers. Source: `HAL/pico/include/util/state_util.hpp:53-70`.

`COMBINATION_MODE_COMPOUND` and unspecified mode compute:

```text
axis = 128 + (axis - 128) * multiplier
```

Source: `src/modes/CustomControllerMode.cpp:105-110`.

`COMBINATION_MODE_OVERRIDE` computes:

```text
axis = 128 + stick_range * multiplier * SIGNUM(axis)
```

Source: `src/modes/CustomControllerMode.cpp:98-104`. The source uses `SIGNUM(outputs.*axis)` directly, not `SIGNUM(outputs.*axis - 128)`. This audit records that implementation shape without assigning intent beyond the code.

Capability claim: analog modifiers are source-backed as per-axis scalar transforms gated by button masks. They are not source-backed as pair-coordinate assignments.

## Left Stick, Right Stick, Or Both

The schema and `axis_pointer` support individual axes on left stick, right stick, and analog triggers. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:286-297` and `HAL/pico/include/util/state_util.hpp:53-70`.

A single `AnalogModifier` targets one axis. Multiple modifiers can target different axes, but the current runtime still applies scalar axis formulas independently. No inspected active source shows one modifier entry carrying a raw `(x,y)` pair for a stick.

Capability claim: modifiers can target left-stick axes, right-stick axes, and trigger axes. They are axis-specific, not stick-pair-specific.

## Exact Raw Coordinate Support

Source-backed:
- `OutputState` stores byte-shaped `leftStickX` and `leftStickY` fields. Source: `include/core/state.hpp:143-154`.
- CustomControllerMode direction mapping can produce min/neutral/max values derived from `stick_range`. Source: `src/modes/CustomControllerMode.cpp:69-84`.
- CustomControllerMode analog modifiers can transform selected axes with multipliers. Source: `src/modes/CustomControllerMode.cpp:86-113`.

Not source-backed:
- a `CustomModeConfig` field for arbitrary left-stick raw `(x,y)` target per direction;
- a runtime path in `CustomControllerMode` that reads raw pair targets for left-stick directions;
- a first-class full 9-way table keyed by neutral/profile direction;
- an explicit non-center neutral coordinate.

Conclusion: exact arbitrary raw pair support is `UNSUPPORTED_BY_CURRENT_SOURCE` for CustomControllerMode as currently audited. Some exact coordinate values may be representable by particular `stick_range` and multiplier combinations, but arbitrary exact pair realization is not source-backed as a general capability.

## Neutral Behavior

`UpdateDirections` sets both stick pairs to `analogStickNeutral`, and CustomControllerMode passes `128` as neutral. Source: `src/core/ControllerMode.cpp:46-49` and `src/modes/CustomControllerMode.cpp:80-82`.

No inspected `CustomModeConfig` field changes neutral away from center. `AnalogModifier` could run while no direction is active if its buttons are held, but the runtime formula remains axis-scalar and source does not identify that as a first-class neutral target. Treat non-center neutral support as `UNKNOWN` only for incidental scalar outcomes and `UNSUPPORTED_BY_CURRENT_SOURCE` for first-class neutral raw-pair representation.

## Full 9-Way Directional Tables

The active CustomControllerMode schema exposes eight stick direction button slots and a global range, not nine raw coordinate entries. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:270-284` and `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:440-459`.

Diagonal output can occur when horizontal and vertical direction buttons are both active because `UpdateDirections` sets axes independently. Source: `src/core/ControllerMode.cpp:51-73`. That yields combinations from min/neutral/max, not a table entry with its own arbitrary raw `(x,y)` pair.

Capability claim: full 9-way arbitrary raw table support is `UNSUPPORTED_BY_CURRENT_SOURCE` for CustomControllerMode.

## Source Reference Table

| file/path | symbol | behavior | capability claim | scope | confidence |
| --- | --- | --- | --- | --- | --- |
| `src/modes/CustomControllerMode.cpp:10-28` | `CustomControllerMode::SetConfig` | stores `CustomModeConfig` pointer and precomputes modifier/combo masks | CustomControllerMode runtime is config-driven when selected | MODE_SPECIFIC | High |
| `src/core/ControllerMode.cpp:8-15` | `ControllerMode::UpdateOutputs` | remap and SOCD run before digital/analog output synthesis | CustomControllerMode sees processed inputs | GENERIC_PIPELINE | High |
| `src/modes/CustomControllerMode.cpp:35-56` | `UpdateDigitalOutputs` | active combo mappings suppress normal buttons through `_filtered_buttons` | combo mappings can affect later direction/modifier input visibility | MODE_SPECIFIC | High |
| `src/modes/CustomControllerMode.cpp:69-84` | `UpdateAnalogOutputs` direction block | reads configured direction buttons and calls `UpdateDirections` with `128 +/- stick_range` | direction-button mapping and range scalar are source-backed | MODE_SPECIFIC | High |
| `src/core/ControllerMode.cpp:46-90` | `UpdateDirections` | centers sticks, then applies min/max per active axis | neutral is center; directions are axis min/max, including diagonals by axis combination | GENERIC_HELPER | High |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:270-284` | `StickDirectionButton` | enumerates eight stick direction slots | left/right stick direction mappings are schema-backed | CONFIG_SCHEMA | High |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:286-297` | `AnalogAxis` | enumerates left stick, right stick, and trigger axes | modifiers can target individual axes across sticks/triggers | CONFIG_SCHEMA | High |
| `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:376-391` | `AnalogModifier` | buttons, one axis, multiplier, combination mode | modifier output form is axis-scalar, not pair-coordinate | CONFIG_SCHEMA | High |
| `HAL/pico/include/util/state_util.hpp:53-70` | `axis_pointer` | maps `AnalogAxis` to one `OutputState` byte member | modifier target is one axis at a time | GENERIC_HELPER | High |
| `src/modes/CustomControllerMode.cpp:98-110` | analog modifier application | override and compound formulas assign one axis from scalar math | analog modifiers are multiplicative/scalar transforms | MODE_SPECIFIC | High |
| `src/modes/CustomControllerMode.cpp:115-138` | analog trigger block | maps buttons to trigger analog values and promotes digital triggers to 255 | trigger analog mapping is source-backed, separate from stick pair realization | MODE_SPECIFIC | High |
| `src/modes/CustomControllerMode.cpp:140-144` | nunchuk override | connected nunchuk overwrites left-stick output | nunchuk can override left stick; this is not Senscope exact-table support | MODE_SPECIFIC | High |
| `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h:429-454` | `CustomModeConfig` | generated struct has direction mappings, analog triggers, modifiers, range, combos | generated config surface matches schema and lacks raw stick table field | GENERATED_CONFIG | High |

## Capability Distinctions

| capability surface | CustomControllerMode status | source-backed basis | caveat |
| --- | --- | --- | --- |
| exact raw coordinate support | `UNSUPPORTED_BY_CURRENT_SOURCE` for arbitrary pair realization | no raw pair table or pair assignment field in `CustomModeConfig`; runtime uses range and scalar modifiers | particular coordinates may be representable incidentally, but arbitrary support is not proven |
| scalar/range modification | `SOURCE_BACKED` | `stick_range`, `AnalogModifier.multiplier`, runtime formulas | scoped to selected CustomControllerMode and individual axes |
| direction button mapping | `SOURCE_BACKED` | eight direction mapping slots and `UpdateDirections` | maps buttons to min/max axis states, not raw table rows |
| neutral behavior | `SOURCE_BACKED` as center; `UNSUPPORTED_BY_CURRENT_SOURCE` as first-class non-center raw pair | neutral constant `128` passed into helper | modifier-held no-direction outcomes are not a source-backed neutral table |
| backend generic support | `UNKNOWN` or `UNSUPPORTED_BY_CURRENT_SOURCE` depending claim | G8f2/G8f3 distinguish selected mode from generic backend | do not promote selected CustomControllerMode evidence to generic backend exact support |

## Conclusion

CustomControllerMode is a useful source-backed example of selected-mode, config-driven controller behavior. For Senscope-style exact neutral profile realization, the current active source supports range/scalar and direction-button primitives but not arbitrary exact raw pair tables, non-center neutral tables, or full 9-way directional tables.
