# Diagnostic Source-View Candidate Published

status: WAITING_FOR_HARDWARE_TEST
overall_result: NOT_TESTED

branch_under_test: `runtime-config-diagnostic-source-view-candidate-published`

baseline branch: `configurator`

## Purpose

This diagnostic branch isolates whether a RAM-backed candidate
`RuntimeConfigView`, materialized from the already-safe source-owned baseline,
is unsafe when published as the active runtime config.

Prior evidence:

- `runtime-active-config-state-source-owned-preselection` recorded
  `HARDWARE_PASS`; source-owned active-state preselection remains the repair
  baseline.
- `runtime-config-diagnostic-parsed-candidate-present-source-owned-published`
  recorded `HARDWARE_PASS`; parser/materialization presence is safe when the
  source-owned baseline remains published active.
- `runtime-config-parsed-candidate-opt-in-diagnostic-batch` recorded
  `HARDWARE_FAIL`; active publication of `candidate.view` remains the main
  suspect.

## Source Boundary

- Parser payload activation is disabled and absent.
- ParseUltimateRuntimeConfigPayload(...) is not called.
- Parsed payload bytes are not present or used.
- Source-owned parsed diagnostic payload bytes are not present or used.
- Candidate state is materialized from kSourceOwnedCurrentBaselineRuntimeConfig.
- Candidate state is validated with `ValidateRuntimeConfigCandidateState(...)`.
- Candidate points/tables are validated equivalent to
  `kSourceOwnedCurrentBaselineRuntimeConfig`.
- Candidate active publication is enabled only after materialization, validation, and source-owned equivalence pass.
- Published active view is candidate.view when the candidate is equivalent.
- Published active view falls back to kSourceOwnedCurrentBaselineRuntimeConfig when validation or equivalence fails.
- ResolveActiveRuntimeConfig() dereferences only the stable published ActiveRuntimeConfigState.active_view.
- UpdateAnalogOutputs(...) binds runtime config through
  ResolveActiveRuntimeConfig() and does not read candidate, parser, decision,
  status, load, storage, write, or flash state.
- `UpdateDigitalOutputs(...)` remains unchanged relative to `configurator`.
- RF5/RF6/LT6 expressions remain preserved.

Expected runtime chain:

```text
source-owned baseline -> RAM candidate materialization -> validation/equivalence -> active_view publication -> UpdateAnalogOutputs
```

## Expected Diagnostic State

```text
candidate materialization source: kSourceOwnedCurrentBaselineRuntimeConfig
candidate active publication: enabled after validation/equivalence
parser payload path: disabled / absent
published active view: candidate.view if candidate is equivalent, otherwise source-owned fallback
```

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Parser payload activation is not implemented.
- No `kPhase7AD3GlobalParseResult.status` read is introduced.
- No D2B retained payload anchor symbols are introduced.
- No parser, candidate, status, decision, load, storage, write, or flash state
  is read by `UpdateAnalogOutputs(...)`.
- No hardware result is claimed by this packet.
- The low-level failure mechanism is not proven.
- Nunchuk remains NOT_TESTED.

## Hardware Test

Hardware testing is required before this diagnostic can be considered safe.
The hardware plan is recorded in
`docs/calibration/diagnostic_source_view_candidate_published_hardware_plan_2026-06-10.md`.
