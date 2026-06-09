# Parser Hot-Path Postmortem and Next Boundary

status: DESIGN_ACCEPTED
title: Parser Hot-Path Postmortem and Next Boundary

This branch is docs/tools-only and changes no firmware behavior.

## Purpose

This packet consolidates the Phase 7A parser/hot-path failure analysis, the
accepted hot-path guardrail, the active runtime config state contract, and the
hardware-passed source-owned preselection repair baseline.

The low-level failure mechanism remains unproven, but the safe architectural
boundary is established.

## Diagnostic Matrix

| Diagnostic | Result |
| --- | --- |
| D2B retained payload bytes only | PASS |
| D3 global/static parse result only | PASS |
| D4 resolver only | PASS |
| D5A parse-status-gated source-owned routing | FAIL |
| D5A-N1 direct source-owned view after parse-status gate | FAIL |
| D5A-N2 resolver without parse-status hot-path read | PASS |
| source-owned active runtime config state preselection | HARDWARE_PASS |

## Accepted Guardrail

Do not read parser result state from UpdateAnalogOutputs or analog hot-path resolver.

## Source-Owned Preselection Hardware Result

- HARDWARE_PASS
- RF5 did not disconnect
- RF6 did not disconnect
- LT6 did not disconnect
- baseline behavior remained intact
- nunchuk remains NOT_TESTED

## Repair Basis

Source-owned active-state preselection is the repair architecture baseline.

## Next Implementation Boundary

- parser/materialization/load may happen only before active-state publication
- output generation may consume only the already-selected RuntimeConfigView
- no parser status, CRC status, load status, storage status, write status,
  source, or activation status may be read by UpdateAnalogOutputs

## Next Allowed Implementation Family

- pre-hot-path active-state publication scaffold
- parsed-payload materialization only into a candidate state, not into hot path
- activation validation outside the analog hot path

## Deferred Work

- true parsed table materialization remains deferred until a separate approved branch
- runtime-loaded config remains deferred
- storage remains deferred
- WebSerial/device write remains deferred
- flashing automation remains deferred
- nunchuk validation remains deferred

## Forbidden Next-Step Shortcuts

- do not reintroduce kPhase7AD3GlobalParseResult.status into ResolveActiveRuntimeConfig
- do not branch on parser status from UpdateAnalogOutputs
- do not materialize parsed tables directly in the analog hot path
- do not add storage/write/flashing/WebSerial paths under parser/materialization work
- do not claim runtime-loaded config before storage/load/activation is implemented and tested

## Non-Claims

- Firmware behavior is unchanged by this docs/tools-only branch.
- Runtime-loaded config is not implemented.
- Parsed table materialization is not implemented.
- Storage is not implemented.
- WebSerial/device write is not implemented.
- Flashing automation is not implemented.
- Nunchuk is not tested or validated.
- Production release readiness is not claimed.
