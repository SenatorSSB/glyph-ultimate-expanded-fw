# G8f7 - Transport Report Serialization Audit

Status: docs-only source audit
Date: 2026-05-24

## Scope

This document is docs-only and source-audit only. It does not implement runtime behavior, modify firmware source, alter headers, change config/protobuf/default activation, add export/push/upload/flashing workflows, flash hardware, change Senscope neutral profile schema, or make game interpretation claims.

Audit question:

> What do transport-specific report paths do with selected-mode `OutputState` values, and what can or cannot be claimed for GC-adapter-mode Senscope capability modeling?

Short answer: transport files can prove how selected-mode `OutputState` bytes are serialized, transformed, or reduced. They do not prove that any selected mode can produce arbitrary requested coordinates, and they do not prove generic backend realization.

## Shared Report Path

The shared path visible in current source is:

```text
Input scan
  -> CommunicationBackend output update
  -> selected InputMode/ControllerMode
  -> mode writes OutputState
  -> transport-specific SendReport serializes OutputState
```

Source-backed details:

- `CommunicationBackend` owns shared `_outputs` as an `OutputState` and exposes `SendReport()` as a transport-specific virtual function. Source: `include/core/CommunicationBackend.hpp:22-35`.
- `CommunicationBackend::ScanInputs` updates the shared `InputState` from each `InputSource`, with scan-speed overloads used by multiple transports. Source: `src/core/CommunicationBackend.cpp:28-42`.
- `CommunicationBackend::UpdateOutputs` delegates to the selected game mode when `_gamemode` is present. Source: `src/core/CommunicationBackend.cpp:49-54`.
- `ControllerMode::UpdateOutputs` runs remap, SOCD, digital output synthesis, and analog output synthesis. Source: `src/core/ControllerMode.cpp:8-15`.
- Each inspected transport `SendReport` then maps the resulting `_outputs` fields into a transport report or console report. Sources: `HAL/pico/src/comms/GamecubeBackend.cpp:26-70`, `HAL/pico/src/comms/NintendoSwitchBackend.cpp:114-152`, `HAL/pico/src/comms/DInputBackend.cpp:25-64`, `HAL/pico/src/comms/XInputBackend.cpp:27-74`, `HAL/pico/src/comms/N64Backend.cpp:25-67`, `HAL/pico/src/comms/NesBackend.cpp:21-37`, `HAL/pico/src/comms/SnesBackend.cpp:21-41`.

## OutputState Analog Surface

`OutputState` contains a digital `buttons` bitfield plus six analog byte fields. Source: `include/core/state.hpp:105-157`.

Analog fields and defaults:

| field | type | default | source |
| --- | --- | --- | --- |
| `leftStickX` | `uint8_t` | `128` | `include/core/state.hpp:143-149` |
| `leftStickY` | `uint8_t` | `128` | `include/core/state.hpp:143-150` |
| `rightStickX` | `uint8_t` | `128` | `include/core/state.hpp:143-151` |
| `rightStickY` | `uint8_t` | `128` | `include/core/state.hpp:143-152` |
| `triggerLAnalog` | `uint8_t` | `0` | `include/core/state.hpp:143-153` |
| `triggerRAnalog` | `uint8_t` | `0` | `include/core/state.hpp:143-154` |

The byte fields show the shape of data available to transports. They do not by themselves define how desired target coordinates are selected or realized.

## Transport Serialization Matrix

| transport | source file | destination fields | left-stick assignment | right-stick assignment | trigger handling | digital handling | transform classification | GC-adapter relevance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GameCube | `HAL/pico/src/comms/GamecubeBackend.cpp` | `_report` fields including `stick_x`, `stick_y`, `cstick_x`, `cstick_y`, `l_analog`, `r_analog` | `_report.stick_x = _outputs.leftStickX`; `_report.stick_y = _outputs.leftStickY` | `_report.cstick_x = _outputs.rightStickX`; `_report.cstick_y = _outputs.rightStickY` | analog trigger bytes copied to `l_analog` and `r_analog`; digital trigger outputs mapped to `l` and `r` | `a/b/x/y`, `z`, `l/r`, `start`, D-pad copied/mapped field-by-field | pass-through for inspected analog bytes in this file; no visible clamp, scale, or inversion before assignment | MVP-critical for GC-adapter target |
| Nintendo Switch | `HAL/pico/src/comms/NintendoSwitchBackend.cpp` | `switch_gamepad_report_t` fields `lx`, `ly`, `rx`, `ry`, button bits, hat | `lx = (leftStickX - 128) * 1.25 + 128`; `ly = 255 - ((leftStickY - 128) * 1.25 + 128)` | same scale formula for `rx`; same scale plus y inversion for `ry` | no analog trigger fields in report struct; digital triggers map to `zl` and `zr` | digital outputs mapped to Switch-style button bits and hat | scaled around 128 and y-inverted for y axes; not raw GC pass-through | not equivalent to GC raw-coordinate output |
| DInput | `HAL/pico/src/comms/DInputBackend.cpp`, `lib/TUCompositeHID/src/TUGamepad.cpp` | `TUGamepad` setters ultimately write 16-bit HID report fields | firmware calls `leftXAxis(leftStickX)` and `leftYAxis(255 - leftStickY)`; library multiplies setter byte by `257` | firmware calls `rightXAxis(rightStickX)` and `rightYAxis(255 - rightStickY)`; library multiplies setter byte by `257` | firmware passes `triggerLAnalog + 1` and `triggerRAnalog + 1`; library multiplies setter byte by `257` | firmware maps digital outputs to numbered buttons and hat switch | x byte is expanded by library; y is inverted then expanded; triggers offset then expanded | not equivalent to GC raw-coordinate output |
| XInput | `HAL/pico/src/comms/XInputBackend.cpp` | `xinput_report_t` fields `lx`, `ly`, `rx`, `ry`, `lt`, `rt`, buttons | `lx = (leftStickX - 128) * 65535 / 255 + 128`; `ly` uses same formula | `rx` and `ry` use same formula | trigger digital outputs force `255`; otherwise analog trigger bytes are used | digital outputs mapped to XInput report bits | scaled into XInput report space; no GC raw byte pass-through | not equivalent to GC raw-coordinate output |
| N64 | `HAL/pico/src/comms/N64Backend.cpp` | `_report.stick_x`, `_report.stick_y`, C-button booleans, buttons | `stick_x = leftStickX - 128`; `stick_y = leftStickY - 128` | right-stick analog bytes are not copied as analog axes; right-stick digital direction booleans map to C-button fields | digital trigger outputs map to `l` and `r`; no analog trigger report fields visible in backend file | buttons and D-pad copied/mapped; right-stick direction booleans map to C-buttons | left stick transformed from unsigned centered byte to signed offset-like value | not equivalent to GC raw-coordinate output |
| NES | `HAL/pico/src/comms/NesBackend.cpp` | digital NES report fields | no analog axis field; left-stick x is thresholded around `128` into D-pad left/right | no right-stick handling visible | no trigger analog handling visible | `a`, `b`, `select`, `start`, and D-pad booleans; D-pad also ORs thresholded left-stick axes | analog bytes reduced to digital D-pad decisions | not relevant to GC raw-coordinate target |
| SNES | `HAL/pico/src/comms/SnesBackend.cpp` | digital SNES report fields | no analog axis field; left-stick x/y are thresholded around `128` into D-pad fields | no right-stick analog handling visible | digital shoulder outputs map to `l` and `r`; no analog trigger report fields visible | `a/b/x/y`, shoulders, select/start, D-pad; D-pad also ORs thresholded left-stick axes | analog bytes reduced to digital D-pad decisions | not relevant to GC raw-coordinate target |

## Distinctions For Capability Modeling

Transport serialization support:
- Source-backed transport evidence can say how existing `_outputs` fields are assigned into a report.
- For GameCube, current source backs the narrow claim that selected-mode left-stick, C-stick, and analog trigger bytes are copied into GC report fields in `GamecubeBackend::SendReport`. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:59-65`.

Selected-mode coordinate production:
- `CommunicationBackend::UpdateOutputs` delegates coordinate production to the selected mode. Source: `src/core/CommunicationBackend.cpp:49-54`.
- `ControllerMode::UpdateOutputs` calls selected-mode digital and analog synthesis after remap/SOCD processing. Source: `src/core/ControllerMode.cpp:8-15`.
- Transport files do not choose target coordinates.

Generic backend realization:
- No inspected transport file accepts a Senscope neutral target or resolves an arbitrary coordinate request.
- Transport serialization cannot be promoted to generic arbitrary coordinate realization without a source-backed selected-mode or generic resolver path.

## Conservative Conclusion

Source-backed for GC transport:
- selected-mode `OutputState.leftStickX/Y` bytes are copied into GC `stick_x/stick_y`;
- selected-mode `OutputState.rightStickX/Y` bytes are copied into GC `cstick_x/cstick_y`;
- selected-mode analog trigger bytes are copied into GC analog trigger fields;
- selected-mode digital outputs are mapped into GC digital report fields;
- no clamp, scale, or inversion is visible in `HAL/pico/src/comms/GamecubeBackend.cpp` before these assignments.

Not source-backed from transport serialization alone:
- arbitrary coordinate realization;
- selected-mode exact target coverage;
- equivalence between non-GC transport mappings and GC raw-coordinate output;
- hardware-level exactness.
