# Diagnostic Source-View Candidate Published

status: HARDWARE_FAIL
overall_result: HARDWARE_FAIL

branch_under_test: `runtime-config-diagnostic-source-view-candidate-published`
result_branch: `runtime-config-diagnostic-source-view-candidate-published-hardware-failure`

baseline branch: `configurator`

operator_report: `tested, failed. same disconnects happen. I reflashed an older working version for use.`

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
- `runtime-config-diagnostic-source-view-candidate-published-hardware-failure`
  records `HARDWARE_FAIL`; publishing candidate-backed active runtime view/table
  pointers reproduces the disconnect class without parser payload parsing.

## Source Boundary

- Parser payload activation is disabled and absent.
- ParseUltimateRuntimeConfigPayload(...) is not called.
- Parsed payload bytes are not present or used.
- Source-owned parsed diagnostic payload bytes are not present or used.
- Candidate state is materialized from kSourceOwnedCurrentBaselineRuntimeConfig.
- Source-view candidate materialization/publication is namespace-scope
  initialized before active resolver use.
- Candidate state is validated with `ValidateRuntimeConfigCandidateState(...)`.
- Candidate points/tables are validated equivalent to
  `kSourceOwnedCurrentBaselineRuntimeConfig`.
- Candidate active publication is enabled only after materialization, validation, and source-owned equivalence pass.
- Published active view is candidate.view when the candidate is equivalent.
- Published active view falls back to kSourceOwnedCurrentBaselineRuntimeConfig when validation or equivalence fails.
- Active resolver chain does not first-trigger candidate materialization.
- ResolveActiveRuntimeConfig() dereferences only the stable published ActiveRuntimeConfigState.active_view.
- UpdateAnalogOutputs(...) binds runtime config through
  ResolveActiveRuntimeConfig() and does not read candidate, parser, decision,
  status, load, storage, write, or flash state.
- `UpdateDigitalOutputs(...)` remains unchanged relative to `configurator`.
- RF5/RF6/LT6 expressions remain preserved.

Expected active resolver chain:

```text
UpdateAnalogOutputs -> ResolveActiveRuntimeConfig -> GetActiveRuntimeConfigState -> gActiveRuntimeConfigState.active_view
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
- Candidate materialization presence alone is not sufficient to reproduce the
  disconnect based on the prior parsed-candidate-present/source-owned-published
  diagnostic hardware pass.
- The low-level failure mechanism is not proven.
- Nunchuk remains NOT_TESTED.

## Hardware Result

Hardware testing failed with the operator report:
`tested, failed. same disconnects happen. I reflashed an older working version for use.`

The result is recorded in
`docs/runtime_config/diagnostic_source_view_candidate_published_hardware_failure_2026-06-10.md`
and
`docs/calibration/diagnostic_source_view_candidate_published_hardware_plan_2026-06-10.md`.

## Conclusions

- `source_view_candidate_publication_safe_for_merge`: `false`
- `candidate_backed_active_runtime_view_safe`: `false`
- `candidate_view_active_publication_reproduces_disconnect`: `true`
- `parser_payload_required_to_reproduce_disconnect`: `false`
- `candidate_materialization_presence_alone_sufficient_to_reproduce_disconnect`: `false`
- `source_owned_active_state_preselection_remains_repair_baseline`: `true`
- `parsed_candidate_presence_source_owned_published_remains_hardware_pass`: `true`
- `low_level_failure_mechanism_proven`: `false`
- `implementation_branch_merge_allowed`: `false`
- `requires_new_publication_model`: `true`
