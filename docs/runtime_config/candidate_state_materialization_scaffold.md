# Candidate State Materialization Scaffold

status: IMPLEMENTATION_SCAFFOLD

branch: `runtime-config-candidate-state-materialization-scaffold`

baseline branch: `configurator`

## Purpose

Add a source-level runtime-config candidate state scaffold after the accepted
source-owned active-state preselection baseline.

This branch is the next safe architecture step only. Candidate state is not
active. Candidate materialization does not change the active runtime config.
Output generation may consume only the already-selected RuntimeConfigView.

## Source Boundary

- `RuntimeConfigCandidateStatus` and `RuntimeConfigCandidateState` are compile-present in firmware source.
- Candidate state has bounded source-owned table storage.
- Candidate validation and materialization helpers are source-local scaffolding.
- Candidate materialization uses source-owned `RuntimeConfigView` data only.
- Candidate state is not used by `ResolveActiveRuntimeConfig()`.
- Candidate state is not used by `UpdateAnalogOutputs(...)`.
- ResolveActiveRuntimeConfig() remains stable active-view only.
- `UpdateAnalogOutputs(...)` continues binding runtime config through
  `ResolveActiveRuntimeConfig()`.

## Hot-Path Guardrail

UpdateAnalogOutputs(...) must not read candidate state, parser status, CRC
status, load status, storage status, write status, source, or activation status.

Parser/materialization/load state may be used only before active-state
publication. Output generation may consume only the already-selected
RuntimeConfigView.

## Non-Claims

- Runtime-loaded config is not implemented.
- Parsed runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- Firmware flashing automation is not implemented.
- No backend/config.pb write path is added.
- Nunchuk remains NOT_TESTED.

## Hardware

No hardware test is required for this branch because candidate state is not
active. The active output path does not consume candidate state, and
`ResolveActiveRuntimeConfig()` continues returning only the stable active view.

Source-owned active-state preselection remains the repair architecture baseline
for this scope. Its accepted hardware state remains `HARDWARE_PASS`; RF5, RF6,
and LT6 did not disconnect, baseline behavior remained intact, and Nunchuk
remains NOT_TESTED.
