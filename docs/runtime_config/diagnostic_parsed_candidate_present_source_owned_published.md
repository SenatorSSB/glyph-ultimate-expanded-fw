# Diagnostic Parsed Candidate Present, Source-Owned Published

status: HARDWARE_PASS
overall_result: HARDWARE_PASS

branch_under_test: `runtime-config-diagnostic-parsed-candidate-present-source-owned-published`
result_branch: `runtime-config-diagnostic-parsed-candidate-present-source-owned-published-hardware-result`

baseline branch: `configurator`

## Purpose

This diagnostic branch isolates whether source-owned/static parsed-candidate
presence, parser bridge execution, candidate materialization, and candidate
equivalence validation are enough to trigger the disconnects reported on the
previous failed branch, or whether publishing the candidate `RuntimeConfigView`
as the active view caused the unsafe behavior.

The previous branch
`runtime-config-parsed-candidate-opt-in-diagnostic-batch` is recorded as
`HARDWARE_FAIL` by operator report: "tested, fails. disconnects happen". Parsed
candidate opt-in activation is unsafe for merge and must not be merged into
`configurator`.

The hardware result branch records `overall_result: HARDWARE_PASS` with
`operator_report: "tested, everything works"`.
Parsed candidate/parser/materialization presence is hardware-safe when
source-owned baseline remains the published active view. Active publication of
`candidate.view` remains the main suspect for the parsed-candidate opt-in
failure.

## Source Boundary

- Parsed candidate machinery is present in firmware source.
- A source-owned/static diagnostic parsed payload is present in firmware source.
- The candidate parser bridge calls `ParseUltimateRuntimeConfigPayload(...)`
  before active publication.
- Candidate materialization remains present and initialized.
- Candidate equivalence validation compares the materialized candidate view
  against `kSourceOwnedCurrentBaselineRuntimeConfig`.
- Candidate activation decision scaffolding may exist only before publication.
- The published active runtime view is forced to kSourceOwnedCurrentBaselineRuntimeConfig.
- candidate.view is not published as the active runtime view.
- ResolveActiveRuntimeConfig() returns only the stable published active view.
- UpdateAnalogOutputs(...) does not read parser, candidate, decision, source,
  status, load, storage, write, or flash state.
- RF5/RF6/LT6 expressions remain unchanged.
- `UpdateDigitalOutputs(...)` remains unchanged relative to `configurator`.

Expected runtime chain:

```text
UpdateAnalogOutputs -> ResolveActiveRuntimeConfig -> GetActiveRuntimeConfigState -> published source-owned active_view
```

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Candidate active publication is not implemented.
- No `kPhase7AD3GlobalParseResult.status` read is introduced.
- No parser status read is introduced in the resolver or analog hot path.
- Parsed candidate activation is not claimed safe.
- The low-level failure mechanism is not proven.
- Nunchuk remains NOT_TESTED.

## Hardware Result

Hardware result is recorded in
`docs/runtime_config/diagnostic_parsed_candidate_present_source_owned_published_hardware_result_2026-06-10.md`
and
`docs/calibration/diagnostic_parsed_candidate_present_source_owned_published_hardware_plan_2026-06-10.md`.

Recorded conclusions:

- `parsed_candidate_presence_safe_when_source_owned_published`: `true`
- `candidate_view_active_publication_remains_suspect`: `true`
- `parsed_candidate_opt_in_activation_safe_for_merge`: `false`
- `source_owned_active_state_preselection_remains_repair_baseline`: `true`
- `implementation_branch_merge_allowed`: `true` for this diagnostic branch only
- `failed_opt_in_activation_branch_merge_allowed`: `false`
- `low_level_failure_mechanism_proven`: `false`
