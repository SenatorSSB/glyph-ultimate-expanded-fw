# G8f7 - Non-GC Transport Transform Boundaries

Status: docs-only source audit
Date: 2026-05-24

## Scope

This document is docs-only and source-audit only. It audits non-GameCube transport transforms visible in source and does not modify firmware, add runtime adapters, enable behavior, add export/push/upload/flashing workflows, flash hardware, alter Senscope neutral profile schema, or make game interpretation claims.

GC-adapter mode is the MVP-critical transport target for current Senscope backend capability modeling. Pro Controller / USB gamepad style mappings must not be assumed identical to GC raw-coordinate output.

## Summary

Non-GC transports consume the same selected-mode `OutputState`, but they do not preserve GC raw-coordinate semantics:

- Nintendo Switch scales stick bytes around 128 and inverts y axes.
- DInput inverts y axes, offsets triggers, and the local `TUGamepad` library expands byte values to 16-bit HID axis fields.
- XInput scales bytes into XInput report fields and treats digital trigger outputs as full analog trigger values.
- N64 converts left-stick bytes to centered signed offsets and maps right-stick direction booleans to C-buttons.
- NES/SNES reduce left-stick thresholds into digital D-pad booleans.

These transforms may be valid for their transports, but they require separate mapping datasets and evaluator rules if they ever become targets.

## Nintendo Switch

Source refs:
- report struct fields: `HAL/pico/include/comms/NintendoSwitchBackend.hpp:18-40`
- report descriptor 8-bit axes: `HAL/pico/src/comms/NintendoSwitchBackend.cpp:41-50`
- send path and transforms: `HAL/pico/src/comms/NintendoSwitchBackend.cpp:114-152`

Visible formulas:

```text
lx = (leftStickX - 128) * 1.25 + 128
ly = 255 - ((leftStickY - 128) * 1.25 + 128)
rx = (rightStickX - 128) * 1.25 + 128
ry = 255 - ((rightStickY - 128) * 1.25 + 128)
```

Classification:
- transformed, not pass-through;
- x axes are scaled around center;
- y axes are scaled around center and inverted;
- digital triggers are mapped to `zl` and `zr`, with no analog trigger fields in `switch_gamepad_report_t`.

Boundary:
- This source does not preserve GC raw coordinate bytes.
- It should not be used as evidence for GC-adapter exactness.
- It does not matter for the current Senscope MVP target except as a non-equivalence warning.

## DInput

Source refs:
- firmware send path: `HAL/pico/src/comms/DInputBackend.cpp:25-64`
- local gamepad report struct and setters: `lib/TUCompositeHID/include/TUGamepad.hpp:31-40`, `lib/TUCompositeHID/src/TUGamepad.cpp:131-153`

Visible firmware formulas:

```text
leftXAxis(leftStickX)
leftYAxis(255 - leftStickY)
rightXAxis(rightStickX)
rightYAxis(255 - rightStickY)
triggerLAnalog(triggerLAnalog + 1)
triggerRAnalog(triggerRAnalog + 1)
```

Visible local library setter formulas:

```text
report.x = value * 257
report.y = value * 257
report.rx = value * 257
report.ry = value * 257
report.z = value * 257
report.rz = value * 257
```

Classification:
- transformed, not GC raw pass-through;
- x bytes pass to the local setter, then expand to 16-bit values;
- y bytes are inverted first, then expand to 16-bit values;
- trigger bytes are offset by one before expansion.

Boundary:
- DInput report fields are not GC raw-coordinate bytes.
- DInput needs its own transport mapping rules if ever modeled as a target.
- It does not matter for the current Senscope MVP target except as a non-equivalence warning.

## XInput

Source refs:
- report holder: `HAL/pico/include/comms/XInputBackend.hpp:16-18`
- send path and transforms: `HAL/pico/src/comms/XInputBackend.cpp:27-74`

Visible formulas:

```text
lx = (leftStickX - 128) * 65535 / 255 + 128
ly = (leftStickY - 128) * 65535 / 255 + 128
rx = (rightStickX - 128) * 65535 / 255 + 128
ry = (rightStickY - 128) * 65535 / 255 + 128
lt = triggerLDigital ? 255 : triggerLAnalog
rt = triggerRDigital ? 255 : triggerRAnalog
```

Classification:
- transformed, not GC raw pass-through;
- stick bytes are scaled into XInput report fields;
- digital trigger outputs can override analog trigger bytes to 255.

Boundary:
- XInput report fields are not GC raw-coordinate bytes.
- XInput needs separate mapping datasets and evaluator rules if ever modeled as a target.
- It does not matter for the current Senscope MVP target except as a non-equivalence warning.

## N64

Source refs:
- report holder: `HAL/pico/include/comms/N64Backend.hpp:24-27`
- send path and transforms: `HAL/pico/src/comms/N64Backend.cpp:25-67`

Visible formulas:

```text
stick_x = leftStickX - 128
stick_y = leftStickY - 128
c_left = rightStickLeft
c_right = rightStickRight
c_down = rightStickDown
c_up = rightStickUp
```

Classification:
- transformed, not GC raw pass-through;
- left-stick bytes are converted from unsigned centered byte form to centered offset form;
- right-stick analog bytes are not copied as analog axes in this backend file; right-stick digital direction booleans map to C-button fields.

Boundary:
- N64 transport is not equivalent to GC raw-coordinate output.
- It is outside the current GC-adapter-mode Senscope MVP target.

## NES

Source refs:
- report holder: `HAL/pico/include/comms/NesBackend.hpp:25-28`
- send path and transforms: `HAL/pico/src/comms/NesBackend.cpp:21-37`

Visible formulas:

```text
dpad_left = dpadLeft || leftStickX < 128
dpad_right = dpadRight || leftStickX > 128
dpad_down = dpadDown || leftStickY < 128
dpad_up = dpadUp || leftStickY > 128
```

Classification:
- reduced to digital threshold decisions;
- no analog stick report fields visible in this backend file;
- no right-stick analog or analog trigger handling visible.

Boundary:
- NES transport is not equivalent to GC raw-coordinate output.
- It is outside the current GC-adapter-mode Senscope MVP target.

## SNES

Source refs:
- report holder: `HAL/pico/include/comms/SnesBackend.hpp:25-28`
- send path and transforms: `HAL/pico/src/comms/SnesBackend.cpp:21-41`

Visible formulas:

```text
dpad_left = dpadLeft || leftStickX < 128
dpad_right = dpadRight || leftStickX > 128
dpad_down = dpadDown || leftStickY < 128
dpad_up = dpadUp || leftStickY > 128
```

Classification:
- reduced to digital threshold decisions;
- no analog stick report fields visible in this backend file;
- no right-stick analog or analog trigger handling visible.

Boundary:
- SNES transport is not equivalent to GC raw-coordinate output.
- It is outside the current GC-adapter-mode Senscope MVP target.

## Capability Model Guidance

Do not promote non-GC transport evidence to GC raw-coordinate support.

Recommended evaluator boundaries:

- GC-adapter mode remains the MVP-critical target.
- Pro Controller / USB gamepad style mappings must not be assumed identical to GC raw-coordinate output.
- Nintendo Switch, DInput, XInput, N64, NES, and SNES need separate transport output IDs if modeled.
- Transformed transports need separate mapping datasets and evaluator rules.
- This audit does not add or infer Pro Controller mappings.
