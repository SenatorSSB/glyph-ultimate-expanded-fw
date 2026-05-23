# G8f7 - GameCube Report Path Capability Audit

Status: docs-only source audit
Date: 2026-05-24

## Scope

This document is docs-only and source-audit only. It focuses on `HAL/pico/src/comms/GamecubeBackend.cpp` and does not modify firmware, enable runtime behavior, add export/push/upload/flashing workflows, flash hardware, alter Senscope neutral profile schema, or make game interpretation claims.

Audit question:

> What does the GameCube transport path copy from `OutputState`, when does it send, and what capability claim does that support for GC-adapter-mode Senscope modeling?

Short answer: `GamecubeBackend::SendReport` directly assigns selected-mode `OutputState` stick and analog trigger bytes into GC report fields. That supports a transport-specific byte-carrying claim. It does not prove selected-mode arbitrary target realization.

## SendReport Flow

`GamecubeBackend` initializes `_report` from `default_gc_report` in its constructor. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:8-20`.

`SendReport` flow:

1. Scans slow and medium inputs before waiting for a poll. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:26-30`.
2. Scans fast inputs while waiting for poll start. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:31-36`.
3. Idles the other core. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:38`.
4. Runs selected-mode output logic through `UpdateOutputs()`. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:42-43`.
5. Copies digital outputs into `_report`. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:45-57`.
6. Copies analog outputs into `_report`. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:59-65`.
7. Sends the report only when `WaitForPollEnd()` does not return `PollStatus::ERROR`. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:67-70`.
8. Resumes the other core. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:71`.

## Field Findings

Left-stick bytes:
- `_report.stick_x = _outputs.leftStickX`
- `_report.stick_y = _outputs.leftStickY`
- Source: `HAL/pico/src/comms/GamecubeBackend.cpp:59-61`
- No clamp, scale, or inversion is visible in this file between `OutputState` and those assignments.

C-stick/right-stick bytes:
- `_report.cstick_x = _outputs.rightStickX`
- `_report.cstick_y = _outputs.rightStickY`
- Source: `HAL/pico/src/comms/GamecubeBackend.cpp:62-63`
- No clamp, scale, or inversion is visible in this file between `OutputState` and those assignments.

Analog triggers:
- `_report.l_analog = _outputs.triggerLAnalog`
- `_report.r_analog = _outputs.triggerRAnalog`
- Source: `HAL/pico/src/comms/GamecubeBackend.cpp:64-65`
- No clamp, scale, or inversion is visible in this file between `OutputState` and those assignments.

Digital outputs:
- `a`, `b`, `x`, `y`, `start`, and D-pad fields copy or map from matching `OutputState` fields. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:45-57`.
- `_report.z` maps from `_outputs.buttonR`. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:50`.
- `_report.l` maps from `_outputs.triggerLDigital`; `_report.r` maps from `_outputs.triggerRDigital`. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:51-52`.

Invalid command / poll behavior:
- `WaitForPollStart()` is used while polling, and `WaitForPollEnd()` gates report send. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:31-36` and `HAL/pico/src/comms/GamecubeBackend.cpp:67-70`.
- If `WaitForPollEnd()` returns `PollStatus::ERROR`, the backend does not call `_gamecube.SendReport(&_report)`. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:67-70`.

## Source Reference Table

| file/path | symbol/function | observed behavior | transport capability claim | confidence |
| --- | --- | --- | --- | --- |
| `HAL/pico/src/comms/GamecubeBackend.cpp:8-20` | `GamecubeBackend::GamecubeBackend` | initializes `_report` from `default_gc_report` | GC transport has a report object seeded from external default report data | High for local assignment; external default contents not audited here |
| `HAL/pico/src/comms/GamecubeBackend.cpp:26-43` | `GamecubeBackend::SendReport` | scans inputs and runs `UpdateOutputs()` before report field assignment | report values are selected-mode outputs at send time | High |
| `HAL/pico/src/comms/GamecubeBackend.cpp:45-57` | `GamecubeBackend::SendReport` digital block | maps selected digital output booleans into GC report fields | GC transport carries/mapping selected digital outputs into GC report fields | High |
| `HAL/pico/src/comms/GamecubeBackend.cpp:59-61` | `GamecubeBackend::SendReport` left-stick assignments | copies `leftStickX/Y` to `stick_x/stick_y` | GC transport can carry selected-mode left-stick bytes | High |
| `HAL/pico/src/comms/GamecubeBackend.cpp:62-63` | `GamecubeBackend::SendReport` C-stick assignments | copies `rightStickX/Y` to `cstick_x/cstick_y` | GC transport can carry selected-mode C-stick bytes | High |
| `HAL/pico/src/comms/GamecubeBackend.cpp:64-65` | `GamecubeBackend::SendReport` analog trigger assignments | copies `triggerLAnalog/RAnalog` to `l_analog/r_analog` | GC transport can carry selected-mode analog trigger bytes | High |
| `HAL/pico/src/comms/GamecubeBackend.cpp:67-70` | poll-end send gate | sends only when poll end is not `PollStatus::ERROR` | GC report send is poll-gated, with invalid/error poll path suppressing send | High for local branch behavior |
| `include/core/CommunicationBackend.hpp:22-35`, `src/core/CommunicationBackend.cpp:49-54` | shared backend output path | selected mode writes `_outputs` through `UpdateOutputs()` | transport consumes selected-mode `OutputState`, not a target request | High |

## Evaluator Implications

Recommended capability-model handling:

- Mark `GameCube transport carrying selected-mode left-stick bytes` as `SOURCE_BACKED`, scoped `TRANSPORT_SPECIFIC`.
- Mark `GameCube transport carrying selected-mode C-stick bytes` as `SOURCE_BACKED`, scoped `TRANSPORT_SPECIFIC`.
- Mark `GameCube transport carrying selected-mode analog trigger bytes` as `SOURCE_BACKED`, scoped `TRANSPORT_SPECIFIC`.
- Keep `selected-mode exact target realization` separate. This file does not prove that a selected mode can produce every requested target.
- Keep `generic backend arbitrary coordinate realization` separate. This file has no generic target resolver.

This is the key modeling rule:

```text
GC transport can carry bytes selected by the active mode.
GC transport source does not prove the active mode can select arbitrary target bytes.
```

## Caveats

- `gc_report_t`, `default_gc_report`, `PollStatus`, and low-level send behavior come from external GameCube/Joybus library headers and sources. This audit cites local backend assignments and does not fully audit that external report struct or electrical/protocol implementation.
- Exact electrical/protocol timing is outside this docs audit.
- This is not hardware testing.
- No claim is made that transport serialization proves arbitrary coordinate realization.
- No claim is made that this path defines game semantics.
