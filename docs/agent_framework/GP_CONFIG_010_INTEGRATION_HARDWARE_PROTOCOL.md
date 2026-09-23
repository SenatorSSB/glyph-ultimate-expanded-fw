# GP-CONFIG-010 current-canonical integration hardware protocol

Protocol version: `GP_CONFIG_010_INTEGRATION_HW_V1`

This protocol tests the exact fresh integration artifact that combines the
original GP-CONFIG-010 capacity repair with current canonical, including the
accepted GP-X1-002 table. It does not transfer acceptance from either
historical artifact. Give the owner one physical instruction at a time and
pause after every requested observation.

## Identity and preconditions

1. Record and verify the full integration candidate SHA, exact parent/tree,
   preserved UF2 locator, SHA-256, byte size, successful custody readback, and
   the committed-before-build provenance. A rebuild or mutable `.pio` output is
   not a substitute.
2. Require the reviewed machine-readable semantic comparison to contain no
   behaviorally relevant `DIFFERENT` result, and require current validation,
   build, and independent firmware-safety review to be complete.
3. Before firmware or persisted-Config mutation, capture the complete owner
   Config as raw bytes plus decoded form. Require deterministic byte-exact
   decode/re-encode. The expected unchanged identity is 4201 bytes with
   SHA-256
   `f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480`.
   If the live payload differs, stop for owner/Curator adjudication rather than
   overwriting it.
4. Manually update only from the verified preserved integration UF2. Record
   controller/host context and device-reported firmware identity. Flashing and
   device writes remain owner-controlled; no agent automation is authorized.

## Temporary 13-profile capacity regression

Use the already proven temporary thirteen-Ultimate Config technique. The
temporary payload must contain exactly `Ult01` through `Ult13` in order, retain
the established unique singleton activation bindings, be GameCube-only, and
differ from the owner Config only in the protocol-authorized profile content.
Require successful write plus immediate and post-reboot exact readback before
physical GameCube observations.

First ask the owner to connect normally once without retrying. The first
startup must pass the Glyph logo and reach a stable normal dashboard. Then ask
the owner to open the Profile menu and report the complete list. Exactly all
thirteen names must be visible in order with no missing or extra entry.

Exercise these required activation rows one at a time, pausing after every
observation:

| Profile | Index | Activation button | Physical location | Expected screen profile |
| --- | ---: | --- | --- | --- |
| Ult01 | 0 | LF6 | left-finger auxiliary in the LF6/LF8 axis group | Ult01 |
| Ult10 | 9 | RF15 | right-side upper/action bank | Ult10 |
| Ult11 | 10 | RF16 | far-right/right-side auxiliary | Ult11 |
| Ult12 | 11 | LT3 | lower-left thumb MX position | Ult12 |
| Ult13 | 12 | LT4 | lower-left thumb MY position | Ult13 |

If physical-label placement differs from the established owner controller,
use the exact previously recorded activation binding rather than guessing and
record the observed physical label. Exercise the other eight rows as well when
the incremental interaction cost is low, but their omission is not an evidence
gap for this bounded combined regression when the five required rows and exact
all-profile visibility pass.

After selecting `Ult13`, disconnect and reconnect normally. Require clean logo
passage, stable connection/miniscreen, exact thirteen-profile menu visibility,
then press and release `LT4` once and require `Ult13` again. Exercise one
horizontal direction, one vertical direction, and one representative face
button; require normal response and clean release. Any capacity, order,
binding, startup, reconnect, display, stuck-input, or disconnect discrepancy
stops the run.

## Exact owner Config restoration

Reconnect in Configurator mode and capture the complete temporary payload
before restoration. Restore the exact original owner payload captured at the
start. Require success, immediate byte-exact readback, one Configurator-mode
reboot, and post-reboot byte-exact readback with the original size and hash.
Restoration failure stops and becomes the recovery priority regardless of the
preceding result.

## GP-X1-002 combined regression

With the exact owner Config restored and Ultimate automatically selected,
press `LT5` with each direction below, one instruction at a time. Observe both
raw and miniscreen coordinates, then release and require neutral before the
next row.

| Dir | Raw | Miniscreen |
| ---: | ---: | ---: |
| 1 | (93,51) | (-35,-77) |
| 2 | (128,51) | (0,-77) |
| 3 | (163,51) | (+35,-77) |
| 4 | (93,128) | (-35,0) |
| 5 | (128,128) | (0,0) |
| 6 | (163,128) | (+35,0) |
| 7 | (93,205) | (-35,+77) |
| 8 | (128,205) | (0,+77) |
| 9 | (163,205) | (+35,+77) |

All nine rows are required for this protocol. Also exercise representative
ordinary buttons/directions, confirm normal miniscreen behavior, disconnect
and reconnect once, and require normal logo passage, stable connection,
Ultimate auto-selection, clean neutral return, and no stuck input or
disconnect. These are raw/display observations only; do not infer gameplay
angle or radius meaning.

## Result and processing

Record every required observation, all anomalies, exact backup/restoration
identities, and final controller state as `PASS`, `FAIL`, `PARTIAL`, or
`INCONCLUSIVE`. Nunchuk remains `NOT_TESTED` unless separately and explicitly
executed. Any repeated frozen-logo event is a failure for this protocol; the
historical isolated event remains preserved and no root cause is inferred.

Only a fresh Hardware Evidence Processor may publish `HARDWARE_VALIDATED` for
the exact integration candidate/artifact. `PASS` requires every required step,
exact owner Config restoration, both GP-CONFIG-010 and GP-X1-002 regression
results, and an empty evidence-gap list. The original GP-CONFIG-010 candidate,
artifact, and PASS record remain distinct historical evidence.
