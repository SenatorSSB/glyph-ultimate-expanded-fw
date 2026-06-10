# Parsed Candidate Opt-In Diagnostic Batch

status: HARDWARE_FAIL_RECORDED

branch: `runtime-config-parsed-candidate-opt-in-diagnostic-batch`

baseline branch: `configurator`

## Purpose

Implement a supervised runtime-config diagnostic batch where a source-owned,
compiled parser fixture is parsed and materialized into candidate state before
active-state publication. The diagnostic opt-in path is enabled in source and
may publish the parsed candidate as the active runtime config view.

This is not runtime-loaded config. The candidate fixture is source-owned static
diagnostic data, not transport input, storage input, WebSerial input, device
write input, or flashing automation input.

## Source Boundary

- `kParsedCandidateOptInDiagnosticPayload` is the source-owned compiled parser
  fixture.
- `MaterializeRuntimeConfigCandidateFromParsedPayload(...)` parses the payload
  and materializes bounded candidate tables before publication.
- `RuntimeConfigActivationDecision` records whether the candidate is accepted,
  rejected, unavailable, or whether the source-owned fallback path is selected.
- `PublishedRuntimeConfigState` is the explicit publication boundary.
- `gPublishedRuntimeConfigState` and `gActiveRuntimeConfigState` are
  namespace-scope initialized before output generation can call the active
  resolver.
- `ResolveActiveRuntimeConfig()` returns only `GetActiveRuntimeConfigState().active_view`.
- `UpdateAnalogOutputs(...)` binds `const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();`
  and does not read parser, candidate, decision, source, or activation state.
- The hot-path resolver chain after publication is
  `UpdateAnalogOutputs -> ResolveActiveRuntimeConfig -> GetActiveRuntimeConfigState -> gActiveRuntimeConfigState.active_view`.

## Equivalence Validation

The diagnostic candidate is intended to be equivalent to the source-owned
baseline. Firmware helper `RuntimeConfigViewsEquivalentEveryPoint(...)` checks:

- every runtime table count matches;
- every table id matches;
- every table point count matches;
- every 9-way point equals the source-owned baseline point;
- fallback table id matches.

If equivalence fails, the candidate is rejected and the source-owned baseline is
published instead. The branch checker also verifies the equivalence helper and
the compiled payload bridge are present.

## Opt-In Activation

The source-controlled diagnostic flag is enabled:

```cpp
constexpr bool kEnableParsedCandidateActivationDiagnostic = true;
```

Because the accepted candidate can become the published active view, this branch
required hardware testing before merge. Hardware testing failed on result branch
`runtime-config-parsed-candidate-opt-in-diagnostic-batch-hardware-failure`.

## Guardrails

- Parser/materialization/decision state is used only before active-state publication.
- Parser/materialization/decision/publication work is not first-triggered by the
  analog hot-path resolver chain.
- Output generation consumes only the already-selected `RuntimeConfigView`.
- `ResolveActiveRuntimeConfig()` does not inspect parser, candidate, activation,
  or decision state directly.
- `UpdateAnalogOutputs(...)` does not inspect parser status, CRC/load/storage/
  write state, source, activation status, candidate status, candidate state, or
  decision state.
- RF5, RF6, and LT6 expressions are unchanged.
- `UpdateDigitalOutputs(...)` is unchanged relative to `configurator`.
- No unbounded or dynamic allocation is introduced for candidate/runtime tables.

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- Backend/config.pb write behavior is not implemented.
- Firmware flashing automation is not implemented.
- Hardware testing failed on the result branch with operator report: "tested,
  fails. disconnects happen".
- The implementation branch must not be merged into `configurator`.
- The low-level failure mechanism is not proven.
- Nunchuk remains NOT_TESTED.

## Hardware

Hardware test failed because parsed candidate opt-in activation still triggered
the disconnect class after flashing branch firmware.

The correct conclusion is narrow: parsed candidate publication/activation still
triggers the disconnect class even when publication is namespace-scope and the
active output path consumes only published `active_view`.

Do not claim the root cause is parser status hot-path reads. The direct
parser-status hot-path read was avoided here, and the failure mechanism remains
unproven.

The hardware plan/result rows are recorded in
`docs/calibration/parsed_candidate_opt_in_diagnostic_batch_hardware_plan_2026-06-10.md`.
The dedicated failure packet is
`docs/runtime_config/parsed_candidate_opt_in_diagnostic_batch_hardware_failure_2026-06-10.md`.
