# G8f6 - Custom Analog Modifier Limits

Status: docs-only source audit
Date: 2026-05-24

## Scope

This document is docs-only. It analyzes current `CustomControllerMode` analog modifier behavior and representability limits for evaluator/capability-model work. It does not change firmware, schemas, defaults, export/push workflows, hardware flashing paths, Senscope neutral profile schema, or gameplay semantic authority.

## Modifier Shape

Current analog modifiers are source-backed as button-gated, axis-specific scalar transforms.

Schema evidence:
- `AnalogModifier.buttons`: all listed buttons must be held for the modifier to apply. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:382-384`.
- `AnalogModifier.axis`: a single target axis. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:385-386`.
- `AnalogModifier.multiplier`: scalar multiplier. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:387-388`.
- `AnalogModifier.combination_mode`: compound or override behavior. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:310-324` and `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:389-390`.

Runtime evidence:
- masks are precomputed in `SetConfig`; all buttons must be held for the modifier to run. Source: `src/modes/CustomControllerMode.cpp:16-20` and `src/modes/CustomControllerMode.cpp:86-94`.
- target axis is mapped to one `OutputState` byte member. Source: `src/modes/CustomControllerMode.cpp:96-112` and `HAL/pico/include/util/state_util.hpp:53-70`.

## Multiplicative Vs Additive

`COMBINATION_MODE_COMPOUND` and unspecified mode are multiplicative around neutral:

```text
axis = 128 + (axis - 128) * multiplier
```

Source: `src/modes/CustomControllerMode.cpp:105-110`.

`COMBINATION_MODE_OVERRIDE` is still scalar/range-based rather than additive pair assignment:

```text
axis = 128 + stick_range * multiplier * SIGNUM(axis)
```

Source: `src/modes/CustomControllerMode.cpp:98-104`.

No active CustomControllerMode source shows an additive modifier of the form `axis += delta`, and no active source shows a modifier entry that assigns both X and Y from a stored coordinate pair.

Status:
- multiplicative/scalar support: `SOURCE_BACKED`;
- additive support: `UNSUPPORTED_BY_CURRENT_SOURCE`;
- arbitrary pair-coordinate support: `UNSUPPORTED_BY_CURRENT_SOURCE`.

## Axis-Specific And Stick-Specific

Modifiers are axis-specific: one modifier names one `AnalogAxis`. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:286-297` and `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:382-391`.

The axis enum includes left-stick X/Y, right-stick X/Y, and trigger axes. Source: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:286-297`.

The runtime helper maps each enum value to one output field. Source: `HAL/pico/include/util/state_util.hpp:53-70`.

Status:
- axis-specific: `SOURCE_BACKED`;
- stick-specific as a pair: `UNSUPPORTED_BY_CURRENT_SOURCE` for one modifier entry;
- left/right stick individual axis targets: `SOURCE_BACKED`.

## Layer-Specific And Direction-Combination-Specific

Modifiers are gated by button masks, not by a first-class layer object. Source: `src/modes/CustomControllerMode.cpp:16-20` and `src/modes/CustomControllerMode.cpp:86-94`.

Because the modifier sees the already-computed axis value, its output depends on the current axis state. Direction combinations can affect the starting axis values through `UpdateDirections`, but the modifier does not contain direction-specific table rows. Source: `src/core/ControllerMode.cpp:46-90` and `src/modes/CustomControllerMode.cpp:69-113`.

Status:
- button-mask-specific: `SOURCE_BACKED`;
- layer-specific as a named layer model: `UNKNOWN` from CustomControllerMode source alone;
- direction-combination-specific exact table rows: `UNSUPPORTED_BY_CURRENT_SOURCE`.

## Conceptual Source-Only Examples

These examples describe source formulas only and do not assign gameplay meaning.

Example 1 - global range:

```text
stick_range = 100
left direction held -> leftStickX starts at 28
right direction held -> leftStickX starts at 228
no horizontal direction -> leftStickX starts at 128
```

Source basis: `src/modes/CustomControllerMode.cpp:69-84` and `src/core/ControllerMode.cpp:46-90`.

Example 2 - compound scalar modifier:

```text
axis starts at 228
multiplier = 0.5
compound result = 128 + (228 - 128) * 0.5 = 178
```

Source basis: `src/modes/CustomControllerMode.cpp:105-110`.

Example 3 - no pair assignment:

```text
desired direction row: x = 163, y = 204
CustomControllerMode fields: direction buttons + stick_range + per-axis multipliers
missing field: one table row carrying x = 163 and y = 204 for that direction
```

Source basis: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:440-459` and `src/modes/CustomControllerMode.cpp:69-113`.

## Why Exact 9-Way Tables Are Not Encoded

A full 9-way raw table would need source-backed representation for at least:
- neutral direction as a first-class row;
- eight non-neutral directions as rows;
- raw X and Y per row;
- modifier or modifier-combination selection of table rows;
- deterministic conflict/priority behavior when multiple modifiers apply.

Current CustomControllerMode source instead has:
- eight direction button slots, not nine table rows;
- one global `stick_range` for min/max around center;
- independent scalar modifiers per axis;
- button masks for modifier activation;
- no raw pair table attached to directions or modifier combinations.

Therefore exact 9-way arbitrary raw coordinate tables are `UNSUPPORTED_BY_CURRENT_SOURCE` for CustomControllerMode.

## Evaluator Implications

Return `SOURCE_BACKED` when:
- the requested capability is scoped to CustomControllerMode;
- the requested output can be represented as direction buttons plus global range and source-backed per-axis scalar modifiers;
- source refs are preserved for `stick_range`, `AnalogModifier`, and runtime formulas.

Return `REPRESENTABILITY_UNKNOWN` when:
- a target coordinate might be achievable through a specific combination of range and multipliers, but no deterministic solver/proof has been approved;
- host/configurator authoring support is not proven;
- the request depends on exact numeric behavior after float-to-uint8 assignment, overflow, or rounding details not audited in tests.

Return `REPRESENTABILITY_UNSUPPORTED` when:
- the target requires a first-class raw `(x,y)` pair assignment;
- the target requires non-center neutral as a stored neutral row;
- the target requires a full 9-way table keyed by direction/modifier combination;
- the target requires additive deltas, pair-specific modifiers, macros, timing automation, or gameplay semantic labels.

Mode-specific support might be `SOURCE_BACKED` when a future evaluator capability explicitly models CustomControllerMode's range/scalar algorithm instead of claiming generic exact raw backend support.

## Constraints And Unknowns

Constraints:
- modifiers are limited to one axis per modifier entry;
- modifier button masks have local generated count limits;
- CustomModeConfig has local generated count limits for direction mappings, analog triggers, modifiers, and combos;
- neutral is center in the active direction helper call;
- nunchuk connected state overrides left-stick outputs after modifiers. Source: `src/modes/CustomControllerMode.cpp:140-144`.

Unknowns:
- exact host-side authoring surface for each field;
- whether external configurator tooling validates or transforms multiplier values;
- numeric edge behavior for unusual multipliers or ranges without dedicated tests;
- whether future approved schema/adapters should target CustomControllerMode or a different realization backend.
