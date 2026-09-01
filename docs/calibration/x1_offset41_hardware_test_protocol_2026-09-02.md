# X1 Offset-41 Manual Hardware Test Protocol

Status label: EXECUTED.

Protocol version: `GLYPH_X1_OFFSET41_MANUAL_PROTOCOL_V1`

This document formalizes the exact manual-test expectations supplied by the
project owner before candidate generation. It does not add a new behavior or
retroactively broaden the tested scope.

## Exact Candidate Identity

- Candidate branch: `runtime-config-x1-offset41-hardware-candidate`
- Candidate Git SHA: `74ae24364b84520d4e0e39240beb9867653cc7b9`
- Base `configurator` SHA: `045bca0d1450c261c3c60ccf5ef86f7302bd3dbc`
- Firmware artifact SHA-256:
  `5fadd3d7e82e629fbccd41fac868312b07b01e39d2ef0a0a98a06d649ae28254`

## Required Observations

Exercise the existing sole/non-mode X1 path and compare its raw X/Y output to
the following exact values:

| Direction | Expected X | Expected Y |
| --- | ---: | ---: |
| neutral | 128 | 128 |
| left | 87 | 128 |
| right | 169 | 128 |
| down | 128 | 87 |
| up | 128 | 169 |
| down-left | 87 | 87 |
| down-right | 169 | 87 |
| up-left | 87 | 169 |
| up-right | 169 | 169 |

The controller must remain connected throughout these observations. Record
only what the human tester actually reports. Do not infer mode+X1, X2, Y1/Y2,
Tilt, layer/flipper, routing, button-binding, gameplay, Nunchuk, persistence,
runtime-loaded configuration, device-write, or flashing-automation behavior.

## Acceptance

PASS requires the tester to report that all nine outputs match and that the
controller did not disconnect. A later restoration of the prior firmware may
be recorded as rollback evidence, but it does not expand the candidate test
scope.
