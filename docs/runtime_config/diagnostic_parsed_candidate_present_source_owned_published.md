# Diagnostic Parsed Candidate Present, Source-Owned Published

status: HARDWARE_TEST_DIAGNOSTIC_BUILD

branch: `runtime-config-diagnostic-parsed-candidate-present-source-owned-published`

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
- No hardware result is claimed by this packet.
- Nunchuk remains NOT_TESTED.

## Hardware Requirement

Hardware testing is required before this diagnostic branch can answer the
disconnect question. The plan is recorded in
`docs/calibration/diagnostic_parsed_candidate_present_source_owned_published_hardware_plan_2026-06-10.md`.
