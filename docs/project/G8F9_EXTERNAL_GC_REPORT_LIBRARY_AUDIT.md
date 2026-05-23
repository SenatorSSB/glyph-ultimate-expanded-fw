# G8f9 - External GC Report Library Audit

Status: docs-only source audit
Date: 2026-05-24

## Scope

This document is docs-only and source-audit only. It does not run hardware tests, alter transport code, alter firmware behavior, implement host tooling, or claim protocol-level exactness beyond inspected local source.

Audit question:

> Does the local external GameCube/Joybus library source support the GC report byte-carrying claims made by the local `GamecubeBackend` audit?

Short answer: local dependency source is present under `.pio/libdeps/glyph_mk6/joybus-pio`. It defines `gc_report_t` as a packed report struct with byte stick and trigger fields, defines `default_gc_report` with stick/c-stick center values at 128 and analog triggers at 0, and sends `sizeof(gc_report_t)` bytes by casting the report pointer to `uint8_t *`. No clamp, scale, or transform after `GamecubeBackend` assignment is visible in the inspected `GamecubeConsole::SendReport` source, though a TODO notes reading-mode translation is not implemented.

## Inspected Local Library Source

Source was available and inspected:

- `.pio/libdeps/glyph_mk6/joybus-pio/include/gamecube_definitions.h`
- `.pio/libdeps/glyph_mk6/joybus-pio/include/GamecubeConsole.hpp`
- `.pio/libdeps/glyph_mk6/joybus-pio/src/GamecubeConsole.cpp`
- `.pio/libdeps/glyph_mk6/joybus-pio/include/joybus.h`

PlatformIO pins the Pico dependency as `https://github.com/GregTurbo/joybus-pio#f2f59c0`. Source: `platformio.ini:111-114`. The inspected local checkout resolves to commit `f2f59c0aee07aea58cdd03616439bc3c6a8cbd8a`.

## Source Reference Table

| file/path | symbol/function | observed behavior | capability claim | confidence |
| --- | --- | --- | --- | --- |
| `.pio/libdeps/glyph_mk6/joybus-pio/include/gamecube_definitions.h:14-38` | `gc_report_t` | Packed struct with two digital bitfield bytes followed by `uint8_t stick_x`, `stick_y`, `cstick_x`, `cstick_y`, `l_analog`, `r_analog` | Report field byte sizes are source-backed for inspected local library | High |
| `.pio/libdeps/glyph_mk6/joybus-pio/include/gamecube_definitions.h:51-73` | `default_gc_report` | Defaults digital fields off, `reserved1 = 1`, sticks/c-sticks `128`, analog triggers `0` | Default neutral values are source-backed for inspected local library | High |
| `.pio/libdeps/glyph_mk6/joybus-pio/include/GamecubeConsole.hpp:46-70` | `WaitForPollStart`, `WaitForPollEnd`, `SendReport` declarations | Library exposes poll-start, poll-end, and report-send API used by local backend | Poll/send API availability is source-backed | High |
| `.pio/libdeps/glyph_mk6/joybus-pio/src/GamecubeConsole.cpp:71-100` | `WaitForPollStart` | Responds to probe/reset/origin/recalibrate commands and returns false on poll command | Poll-start behavior is source-backed at source level | Medium |
| `.pio/libdeps/glyph_mk6/joybus-pio/src/GamecubeConsole.cpp:102-125` | `WaitForPollEnd` | Reads remaining poll bytes, rejects timeout/invalid reading mode, records reading mode, returns rumble/error status | Poll-end status behavior is source-backed at source level | Medium |
| `.pio/libdeps/glyph_mk6/joybus-pio/src/GamecubeConsole.cpp:127-134` | `SendReport` | Waits until reply delay, then sends `sizeof(gc_report_t)` bytes from the report pointer; TODO says reading-mode translation | Direct report serialization of struct bytes is source-backed in inspected source | High |
| `.pio/libdeps/glyph_mk6/joybus-pio/include/joybus.h:61-75` | `joybus_send_bytes` | Sends caller-provided byte pointer and length over Joybus port | Byte-send API shape is source-backed | Medium |
| `HAL/pico/src/comms/GamecubeBackend.cpp:59-69` | `GamecubeBackend::SendReport` | Assigns `OutputState` bytes to report fields, then calls `_gamecube.SendReport(&_report)` if poll end is not error | Local backend assignment plus external send call is source-backed | High |

## Capability Determinations

Report field byte sizes:

- `SOURCE_BACKED` for inspected local library. `gc_report_t` uses `uint8_t` for stick, c-stick, and analog trigger fields. Source: `.pio/libdeps/glyph_mk6/joybus-pio/include/gamecube_definitions.h:14-38`.

Direct report serialization of stick bytes:

- `SOURCE_BACKED` for inspected local library source. `GamecubeConsole::SendReport` casts the report pointer to `uint8_t *` and sends `sizeof(gc_report_t)` bytes. Source: `.pio/libdeps/glyph_mk6/joybus-pio/src/GamecubeConsole.cpp:127-134`.

Default neutral values:

- `SOURCE_BACKED` for inspected local library. `default_gc_report` sets stick and c-stick axes to `128` and analog triggers to `0`. Source: `.pio/libdeps/glyph_mk6/joybus-pio/include/gamecube_definitions.h:51-73`.

Clamps/transforms after `GamecubeBackend` assignment:

- No clamp, scale, inversion, or field transform is visible in inspected `GamecubeConsole::SendReport`. A TODO says "Translate report according to reading mode", so reading-mode-specific translation remains not implemented in source and should not be claimed.

Poll/send behavior:

- `WaitForPollStart` and `WaitForPollEnd` behavior is source-backed at code level. Physical/electrical protocol timing and hardware-observed behavior remain outside this audit.

## Distinctions

Local backend assignment:

- `GamecubeBackend` copies selected-mode `OutputState` bytes into `gc_report_t` fields. Source: `HAL/pico/src/comms/GamecubeBackend.cpp:59-65`.

External library report serialization:

- `GamecubeConsole::SendReport` sends the report struct bytes using `joybus_send_bytes`. Source: `.pio/libdeps/glyph_mk6/joybus-pio/src/GamecubeConsole.cpp:127-134`.

Physical/electrical protocol timing:

- The library has PIO/Joybus send/receive functions and timing constants, but this audit does not validate electrical timing or console behavior.

Hardware-observed behavior:

- Not tested. Remains `UNKNOWN`.

## Conclusion

The external local GC library source strengthens the narrow transport claim: selected-mode bytes assigned into `gc_report_t` by `GamecubeBackend` are represented as byte report fields and sent as report bytes by the local Joybus library source. This still does not prove arbitrary Senscope target realization, hardware-observed exactness, or protocol-level correctness beyond inspected source.
