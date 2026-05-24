# Glyph Native Ultimate Analog Baseline (2026-05-24)

## Scope

This document is a source-grounded baseline snapshot of current native `MODE_ULTIMATE` analog behavior.

It is documentation only. It does not change runtime firmware behavior, device behavior, SOCD behavior, remapping semantics, or add flashing/push-to-device behavior.

## 1) Source files involved

- `src/modes/Ultimate.cpp`
- `include/modes/Ultimate.hpp`
- `src/core/ControllerMode.cpp`
- `include/core/ControllerMode.hpp`
- `src/core/InputMode.cpp`
- `include/core/state.hpp`
- `config/glyph/common/include/glyph_overrides.hpp`

## 2) Functions involved

- `Ultimate::UpdateDigitalOutputs` (`src/modes/Ultimate.cpp`)
- `Ultimate::UpdateAnalogOutputs` (`src/modes/Ultimate.cpp`)
- `ControllerMode::UpdateOutputs` (`src/core/ControllerMode.cpp`)
- `ControllerMode::UpdateDirections` (`src/core/ControllerMode.cpp`)
- `InputMode::HandleRemap` (`src/core/InputMode.cpp`)
- `InputMode::HandleSocd` (`src/core/InputMode.cpp`)

## 3) Input state consumed

Directly consumed in `Ultimate.cpp`:

- Left/right face/direction clusters: `lf1`, `lf2`, `lf3`, `lf4`, `lf6`, `lf8`, `rf1`, `rf2`, `rf3`, `rf4`, `rf5`, `rf6`, `rf7`, `rf8`
- Left/right thumb clusters: `lt1`, `lt2`, `rt1`, `rt2`, `rt3`, `rt4`, `rt5`
- Menu buttons: `mb4`, `mb5`, `mb6`, `mb7`
- Nunchuk fields: `nunchuk_connected`, `nunchuk_c`, `nunchuk_x`, `nunchuk_y`

Pipeline consumed before Ultimate-specific logic:

- `ControllerMode::UpdateOutputs` applies `HandleRemap`, then `HandleSocd`, then calls Ultimate digital/analog update functions.
- `glyph_overrides.hpp` configures `MODE_ULTIMATE` SOCD pairs (`SOCD_2IP`) and button remapping defaults.

## 4) Output state fields written

Digital (`UpdateDigitalOutputs`):

- Face/buttons: `a`, `b`, `x`, `y`, `buttonR`
- Trigger digital: `triggerLDigital`, `triggerRDigital`
- System: `start`, `select`, `home`, `capture`
- D-pad: `dpadUp`, `dpadDown`, `dpadLeft`, `dpadRight`
- Stick digital directions: `leftStickLeft`, `leftStickRight`, `leftStickDown`, `leftStickUp`, `rightStickLeft`, `rightStickRight`, `rightStickDown`, `rightStickUp`
- Modifier flags: `modX`, `modY`

Analog (`UpdateDirections` + `UpdateAnalogOutputs`):

- `leftStickX`, `leftStickY`
- `rightStickX`, `rightStickY`
- `triggerLAnalog`, `triggerRAnalog`

## 5) Existing hard-coded left-stick values/constants

Global macros in `Ultimate.cpp`:

- `ANALOG_STICK_MIN = 28`
- `ANALOG_STICK_NEUTRAL = 128`
- `ANALOG_STICK_MAX = 228`

`UpdateDirections` baseline axis initialization and direct cardinal values:

- Left stick neutral uses `analogStickNeutral` (called with `128`).
- Left stick cardinal resolves to `analogStickMin` (`28`) or `analogStickMax` (`228`) before modifier overrides.

Ultimate modifier overrides in `UpdateAnalogOutputs` set left-stick components via `128 + direction * value`, with observed values:

- X-side values: `28`, `31`, `34`, `35`, `36`, `38`, `39`, `40`, `41`, `43`, `44`, `49`, `51`, `53`, `55`, `67`
- Y-side values: `26`, `28`, `30`, `31`, `35`, `36`, `38`, `39`, `43`, `44`, `49`, `51`, `53`, `55`, `67`, `68`, `70`

Special override:

- If `nunchuk_connected` is true, left stick is overwritten with raw `inputs.nunchuk_x` / `inputs.nunchuk_y`.

## 6) Existing hard-coded right-stick/C-stick values/constants

`UpdateDirections` baseline:

- Right stick neutral uses `analogStickNeutral` (`128`).
- Right stick cardinal resolves to `analogStickMin` (`28`) or `analogStickMax` (`228`) before modifier overrides.

Ultimate-specific overrides:

- Angled C-stick branch: `rightStickX = 128 + directions.cx * 127`, `rightStickY = 128 + directions.y * 59`
- ASDI slideoff diagonal branch: `rightStickX = 128 + directions.cx * 42`, `rightStickY = 128 + directions.cy * 68`
- D-pad layer branch (`lt1 && lt2` or `nunchuk_c`) forces right stick neutral (`128`, `128`)

## 7) Existing trigger values/constants

- `triggerLAnalog = 140` when `lf4` is pressed, else `0`
- `triggerRAnalog = 140` when `rf5` is pressed, else `0`

## 8) Existing modifier-button or layer interactions

- `lt1` behaves as Mod X branch enable for multiple left-stick and some right-stick angled overrides.
- `lt2` behaves as Mod Y branch enable for multiple left-stick overrides.
- `lf4 || rf5` creates `shield_button_pressed`, which changes several Mod X/Mod Y diagonal outputs.
- `rt1`..`rt5` select alternate angle values inside both Mod X and Mod Y diagonal branches.
- `rf1` enables "Extended Up B Angles" sub-branches.
- Combined `lt1 && lt2` (or `nunchuk_c`) enables D-pad layer and later forces C-stick analog output to neutral.
- `UpdateDigitalOutputs` writes `outputs.modX = inputs.lt1` and `outputs.modY = inputs.lt2`.

## 9) Existing nunchuk, d-pad, C-stick, shield, or special-case branches

- D-pad layer toggle:
  - condition: `(lt1 && lt2) || nunchuk_c`
  - behavior: D-pad digital outputs are driven from `rt2`/`rt3`/`rt4`/`rt5`
- C-stick shutdown during D-pad layer:
  - condition: `(lt1 && lt2) || nunchuk_c`
  - behavior: `rightStickX = 128`, `rightStickY = 128`
- Nunchuk override:
  - condition: `nunchuk_connected`
  - behavior: `leftStickX = nunchuk_x`, `leftStickY = nunchuk_y`
- Shield-aware analog shaping:
  - condition: `lf4 || rf5`
  - behavior: modifies several Mod X/Mod Y tilt angle selections
- C-stick diagonal ASDI slideoff override:
  - condition: `directions.cx != 0 && directions.cy != 0`
  - behavior: overrides other C-stick modifier outputs

## 10) Current known risks for adding Tilt/Tilt2 later

- Override order risk: `UpdateAnalogOutputs` has many sequential rewrites to the same stick fields; small branch insertions can silently change final values.
- Preprocessing dependency risk: inputs reaching Ultimate logic are post-remap and post-SOCD (`HandleRemap` then `HandleSocd`), so runtime patch behavior depends on that pipeline.
- Right-stick preservation risk: C-stick angle logic and ASDI slideoff override can conflict with new custom tilt behavior if output targets are not tightly scoped.
- D-pad/nunchuk branch risk: D-pad layer neutralizes C-stick and nunchuk can overwrite left stick late in the function.
- Numeric safety risk: analog outputs are `uint8_t` (`include/core/state.hpp`); overflow/clamp behavior should not be assumed without explicit proof.
- Scope risk: final Tilt1/Tilt2 values and activation mapping are not selected in-repo and must remain external owner decisions before runtime patching.
