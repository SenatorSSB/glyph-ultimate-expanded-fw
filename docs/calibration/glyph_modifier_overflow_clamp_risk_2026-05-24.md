# Glyph Modifier Overflow/Clamp Risk (2026-05-24)

## Purpose

This document records what is known and unknown about modifier math that writes into `uint8_t` output fields. It is source-trace documentation only and does not implement tests or runtime behavior.

## Known Source Paths

### `include/core/state.hpp`

`OutputState` stores analog outputs as byte fields:

```cpp
uint8_t analog_axes[6] = { 128, 128, 128, 128, 0, 0 };
uint8_t leftStickX;
uint8_t leftStickY;
uint8_t rightStickX;
uint8_t rightStickY;
uint8_t triggerLAnalog;
uint8_t triggerRAnalog;
```

Known fact: modifier and mode math ultimately writes into `uint8_t` output fields.

### `HAL/pico/include/util/state_util.hpp::axis_pointer`

`axis_pointer(AnalogAxis axis)` returns a pointer-to-member for these `OutputState` fields:

- `AXIS_LSTICK_X` -> `OutputState::leftStickX`
- `AXIS_LSTICK_Y` -> `OutputState::leftStickY`
- `AXIS_RSTICK_X` -> `OutputState::rightStickX`
- `AXIS_RSTICK_Y` -> `OutputState::rightStickY`
- `AXIS_LTRIGGER` -> `OutputState::triggerLAnalog`
- `AXIS_RTRIGGER` -> `OutputState::triggerRAnalog`

Known fact: schema-backed modifiers can target one analog byte field at a time in `CustomControllerMode`.

### `src/core/ControllerMode.cpp::UpdateDirections`

`UpdateDirections` writes min/neutral/max values directly into `OutputState` stick fields using `uint8_t` parameters. It resets both sticks to neutral, then writes min or max when directional inputs are active.

Known fact: direction output values are already byte-shaped before assignment.

### `src/modes/CustomControllerMode.cpp::UpdateAnalogOutputs`

Custom mode reads `stick_range` as `uint8_t` and calls:

```cpp
UpdateDirections(..., 128 - stick_range, 128, 128 + stick_range, outputs);
```

It then applies modifiers:

```cpp
outputs.*axis = 128 + stick_range * modifier.multiplier * sign;
```

for `COMBINATION_MODE_OVERRIDE`, and:

```cpp
outputs.*axis = 128 + (outputs.*axis - 128) * modifier.multiplier;
```

for `COMBINATION_MODE_COMPOUND` and `COMBINATION_MODE_UNSPECIFIED`.

Known fact: these expressions are assigned to `uint8_t OutputState::*axis` without an explicit clamp or saturate call visible in this function.

### `src/modes/Ultimate.cpp::UpdateAnalogOutputs`

Native Ultimate computes hard-coded analog values such as:

```cpp
outputs.leftStickX = 128 + (directions.x * 53);
outputs.leftStickY = 128 + (directions.y * 44);
outputs.rightStickX = 128 + (directions.cx * 42);
outputs.rightStickY = 128 + (directions.cy * 68);
```

Known fact: current constants observed in native Ultimate source appear chosen to remain in normal byte range, but this document does not claim a complete numeric proof for every branch.

## Explicit Clamp/Saturate Status

No explicit clamp/saturate guard was found in the traced `CustomControllerMode` modifier math path.

This does not prove the compiler, target ABI, or generated code will behave in a desired way for out-of-range values. It only proves that no source-level clamp/saturate call is visible in the inspected modifier assignment path.

## Implicit `uint8_t` Conversion Risk

Because `outputs.*axis` is a `uint8_t` member, assigning a computed expression back into it can invoke implicit conversion to the byte field type.

The current repo docs and source traces do not define any intended overflow, wrapping, clamping, or saturation behavior for out-of-range modifier results. Depending on such behavior would be unsafe without source comments, tests, or explicit implementation.

## Why Overflow-Dependent Or Flipper-Like Behavior Is Unsafe

- No `flipper` field, symbol, fixture, or runtime implementation was found in active proto/runtime paths.
- No explicit clamp/saturate behavior was found for `CustomControllerMode` modifier writes.
- No tests in the current trace prove out-of-range multiplier results.
- Relying on implicit byte conversion would make an accident look like design.
- Future Senscope integration must not depend on undocumented backend behavior.

Conclusion: overflow-dependent and flipper-like behavior remains blocked until proven or replaced by explicit, reviewed logic.

## Future Host-Side Test Strategy

A later branch can add tests without hardware first if it stays source-backed and avoids changing runtime behavior:

1. Extract or wrap the existing modifier formula in a host-testable helper only after approval, or create a compile-time test fixture that invokes `CustomControllerMode::UpdateAnalogOutputs` with synthetic `InputState`, `OutputState`, and `CustomModeConfig`.
2. Test representative safe values, boundary values, and out-of-range multiplier results.
3. Assert exact output bytes and document whether behavior is clamp, wrap, or explicitly blocked.
4. Add cases for `COMBINATION_MODE_OVERRIDE`, `COMBINATION_MODE_COMPOUND`, unspecified mode, invalid axis, empty modifier button list, and trigger axes.
5. Keep tests independent from hardware flashing and device transport.

This branch does not implement those tests because the current task is documentation and read-only tooling only.

## Later Hardware Smoke-Test Observation Checklist

After a later runtime branch compiles and a human owner manually flashes it:

- Confirm board boots normally.
- Confirm left-stick neutral reports neutral when no directions/modifiers are held.
- Confirm baseline left/right/up/down and diagonals still report expected existing Ultimate behavior.
- Confirm new Tilt/Tilt2 inputs, if implemented later, produce only approved byte values.
- Confirm no axis jumps to unexpected extremes such as `0`, `255`, or mirrored/wrapped values unless explicitly designed and tested.
- Confirm C-stick/right-stick values are unaffected unless the later patch intentionally targets them.
- Confirm triggers still report expected analog/digital behavior.
- Stop immediately on stuck input, repeated uncontrolled input, unexpected SOCD behavior, menu/start breakage, or profile corruption.
