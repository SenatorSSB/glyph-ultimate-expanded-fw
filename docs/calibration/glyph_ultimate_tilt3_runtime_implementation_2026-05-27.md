# Glyph Ultimate Tilt3 Runtime Implementation (2026-05-27)

## Scope

This branch implements native Ultimate Tilt3 behavior in `src/modes/Ultimate.cpp`.

- Native `MODE_ULTIMATE` only.
- Left-stick output only.
- Localized to the existing `// Senscope Glyph Ultimate Tilt patch begin` / `end` block.
- No schema, proto, configurator, profile serialization, export, flashing, or push-to-device behavior is added.
- No macros, turbo, toggles, one-shots, or timing automation are added.

## User-Approved Behavior

User-approved behavior for this branch:

- Dedicated Tilt3 is logical `LT3`.
- Tilt3 also activates from `LT1+LT2`.
- Tilt3 X offset: `53`.
- Tilt3 Y offset: `42`.
- Nothing more special.

## Source-Traced Dedicated Left-Thumb Logical Input Path

Dedicated Tilt3 uses the existing logical input field `inputs.lt3`.

Source trace:

- `include/core/state.hpp` defines `InputState::lt3` in the shared rectangle button bitfield.
- `src/core/ControllerMode.cpp` copies physical inputs into `remapped_inputs`, calls `HandleRemap`, then `HandleSocd`, then passes the remapped/SOCD-resolved inputs to `Ultimate::UpdateDigitalOutputs` and `Ultimate::UpdateAnalogOutputs`.
- `src/core/InputMode.cpp` implements `HandleRemap` using `ButtonRemap.physical_button` and `ButtonRemap.activates`, so logical fields such as `inputs.lt3` are consumed after remap.
- `HAL/pico/include/util/state_util.hpp` provides the `BTN_LT3` bit helper path through the shared button bitfield.

No raw physical left-thumb or RF button path is used for Tilt3 in this implementation.

## Tilt3 Active Condition

Runtime active condition:

```text
tilt3_active = inputs.lt3 || (inputs.lt1 && inputs.lt2)
```

Runtime priority inside the Tilt block:

1. If `tilt3_active`, apply Tilt3.
2. Else if `inputs.lt1`, apply existing Tilt1.
3. Else if `inputs.lt2`, apply existing Tilt2.
4. Else no Tilt override.

This means `LT1+LT2` now resolves to Tilt3 in this branch.

## Tilt3 Formula And Table

Formula for `directions.x` / `directions.y` in `-1, 0, 1`:

```text
leftStickX = 128 + directions.x * 53
leftStickY = 128 + directions.y * 42
```

| Direction | Left-stick output | Offset |
| --- | --- | --- |
| 1 | `(75, 86)` | `(-53, -42)` |
| 2 | `(128, 86)` | `(0, -42)` |
| 3 | `(181, 86)` | `(53, -42)` |
| 4 | `(75, 128)` | `(-53, 0)` |
| 5 | `(128, 128)` | `(0, 0)` |
| 6 | `(181, 128)` | `(53, 0)` |
| 7 | `(75, 170)` | `(-53, 42)` |
| 8 | `(128, 170)` | `(0, 42)` |
| 9 | `(181, 170)` | `(53, 42)` |

All values remain within `[0,255]` and do not rely on unsigned overflow or wrap behavior.

## Preservation Boundaries

Intentional runtime change:

- `MODE_ULTIMATE` left-stick Tilt behavior now includes Tilt3.
- `LT1+LT2` both-held no longer falls through to old combined behavior inside the Tilt override path; it resolves to Tilt3.

Preserved by implementation scope:

- SOCD handling remains in the existing pre-output path.
- Remap handling remains in the existing pre-output path.
- C-stick/right-stick assignments are not changed by the Tilt3 block.
- Trigger assignments are not changed by the Tilt3 block.
- Nunchuk left-stick overwrite remains after the Tilt block and remains authoritative when connected.
- Other modes are untouched.
- Profile/schema/proto/configurator behavior is untouched.

## Hardware-Test Requirements

Hardware testing is required before final acceptance.

Required hardware checks include:

- Dedicated logical `LT3` directions 1..9 produce the Tilt3 table.
- `LT1+LT2` directions 1..9 produce the Tilt3 table.
- `LT1` alone directions 1..9 still produce the existing Tilt1 table.
- `LT2` alone directions 1..9 still produce the existing Tilt2 table.
- Baseline no-modifier directions 1..9 remain unchanged.
- C-stick/right-stick, triggers, SOCD, remap, and nunchuk preservation smoke checks are completed.

## Caveat

No broad preservation claim exists until hardware testing is complete. This branch is source-checked and build-checked only until the Tilt3-specific hardware test run is performed.
