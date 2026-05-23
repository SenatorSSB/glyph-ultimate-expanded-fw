# G8f4 - Output Report Path Audit

Status: docs-only source audit
Date: 2026-05-23

## Scope

This document is docs-only. It traces the output path from mode-level `OutputState` fields to transport report emission as far as current source permits.

It distinguishes:

- "transport can carry a value"
- from "backend can realize arbitrary Senscope neutral target"

No gameplay or Switch interpretation claims are made.

## Shared Output Path

The shared pipeline is:

```text
Input scan
  -> CommunicationBackend::UpdateOutputs()
  -> selected InputMode/ControllerMode
  -> mode writes OutputState
  -> transport-specific SendReport encodes OutputState
```

Source refs:
- `CommunicationBackend::_outputs` stores an `OutputState`: `include/core/CommunicationBackend.hpp:20-31`.
- `CommunicationBackend::UpdateOutputs` delegates to the current mode when present: `src/core/CommunicationBackend.cpp:42-47`.
- `ControllerMode::UpdateOutputs` runs remap, SOCD, digital output synthesis, then analog output synthesis: `src/core/ControllerMode.cpp:8-15`.
- `OutputState` left-stick fields are `uint8_t leftStickX` and `uint8_t leftStickY`: `include/core/state.hpp:143-154`.

## Transport Audit

| transport | left-stick x/y encoding or forwarding | clamp/transform/center behavior visible in source | relevance to GC-adapter target | source-backed claim |
| --- | --- | --- | --- | --- |
| GameCube | `_report.stick_x = _outputs.leftStickX`; `_report.stick_y = _outputs.leftStickY` | no explicit clamp or scale in this file; constructor starts from `default_gc_report` | Directly relevant to GC report path | GC backend forwards mode-produced left-stick bytes into report fields |
| Nintendo Switch | `_report.lx = (_outputs.leftStickX - 128) * 1.25 + 128`; y is also inverted after scale | explicit scale around 128 and y inversion; report defaults center at 128 | Not a GC-adapter path | Switch transport can encode mode-produced values, but not raw GC pass-through |
| DInput | left x forwarded; left y set to `255 - _outputs.leftStickY` | y inversion; triggers add 1 | Not a GC-adapter path | DInput transport can encode mode-produced values with y inversion |
| XInput | axes scaled with `(_outputs.leftStickX - 128) * 65535 / 255 + 128` and equivalent y formula | explicit scaling into XInput report fields | Not a GC-adapter path | XInput transport transforms mode-produced values into report-space values |
| Configurator | command/packet handler for device info/config/reboot; no gamepad report path in inspected file | not applicable | Not a GC report transport | ConfiguratorBackend is config transport, not left-stick report emission |

## GameCube Backend

`GamecubeBackend::SendReport` scans inputs, calls `UpdateOutputs`, copies digital fields, copies analog fields, then sends the GC report unless the poll command is invalid. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:26-70`.

Left-stick x/y are copied directly:

- `HAL/pico/src/comms/GamecubeBackend.cpp:59-61`

No source in this file shows scaling or clamping of `leftStickX/Y` before assignment to `_report.stick_x/stick_y`. This supports `TRANSPORT_SPECIFIC` evidence that the GC transport can carry the selected mode's byte values.

It does not prove generic arbitrary target realization, because the selected mode still chooses `_outputs.leftStickX/Y`.

## Nintendo Switch Backend

Nintendo Switch HID descriptor declares four 8-bit analog stick axes with 0-255 logical/physical max. Source: `HAL/pico/src/comms/NintendoSwitchBackend.cpp:41-50`.

`SendReport` transforms mode-produced axes with scale and y inversion before report emission. Source: `HAL/pico/src/comms/NintendoSwitchBackend.cpp:142-146`.

This is transport-specific behavior and should not be used to claim raw GC-coordinate exactness.

## DInput Backend

`DInputBackend::SendReport` forwards left x to `_gamepad.leftXAxis`, inverts left y, forwards right x, inverts right y, adjusts trigger analog values, and sends state. Source: `HAL/pico/src/comms/DInputBackend.cpp:52-64`.

This shows a transport can encode mode-produced values. It does not prove a target realization primitive.

## XInput Backend

`XInputBackend::SendReport` writes digital fields, uses trigger digital fields to select trigger values, scales left/right stick axes into XInput report fields, then sends the report if the timeout path did not fire. Source: `HAL/pico/src/comms/XInputBackend.cpp:48-74`.

This path is transport-specific and transformed. It is not evidence of raw GC pass-through.

## Configurator Backend And Persistence

`ConfiguratorBackend` handles device info, raw config get/set, persistence, and reboot commands. Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:44-226`.

`Persistence` saves and loads protobuf config data with a header and CRC. Source: `HAL/pico/src/core/Persistence.cpp:24-143`.

These files support a device-side config path, but they do not emit controller output reports and do not prove exact raw left-stick realization or export/push workflows.

## Unknowns

- Host-library behavior inside external report senders is not fully characterized here.
- GC report struct details come from included external library headers, not inspected in this audit.
- Practical exactness after non-GC transport transforms is transport-specific and not audited beyond current source formulas.
- No inspected transport chooses arbitrary neutral targets; transports consume mode-produced values.

## Conclusion

The report path is source-backed for carrying or transforming selected mode output fields. It is not source-backed evidence that the backend can realize arbitrary Senscope neutral targets. For GC-adapter-oriented evaluation, the strongest transport evidence is GameCube pass-through of `OutputState` left-stick bytes, scoped strictly to transport serialization.
