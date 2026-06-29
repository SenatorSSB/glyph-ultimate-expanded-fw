# Diagnostic Generated Source-Owned Baseline Active

Status: HARDWARE_GATED_DIAGNOSTIC.

Branch:
`runtime-config-diagnostic-generated-source-owned-baseline-active`

## Diagnostic Question

Can a generated source-owned baseline-equivalent artifact be selected active
safely while preserving source-owned/immutable pointer semantics and avoiding
RAM-backed active table publication?

The generated source-owned baseline-equivalent artifact is selected active by
this branch through a generated source-owned `RuntimeConfigView`.

## Source Boundary

- `src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`
  remains the generated source-owned baseline artifact.
- `src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaselineActiveView.current.hpp`
  adds a generated source-owned `RuntimeConfigView` wrapper.
- The generated baseline artifact is referenced only as source-owned immutable
  data.
- The wrapper contains immutable generated `StickPoint` table data and immutable
  `RuntimeTableView` metadata.
- Active `RuntimeTableView.table` pointers target generated source-owned
  immutable tables, not candidate storage and not RAM-backed active storage.
- `GetActiveRuntimeConfigState()` publishes
  `kGeneratedSourceOwnedBaselineRuntimeConfig`.
- `ResolveActiveRuntimeConfig()` only dereferences the stable active view.
- `UpdateAnalogOutputs(...)` still consumes only `ResolveActiveRuntimeConfig()`.
- `UpdateDigitalOutputs(...)` remains unchanged relative to `configurator`.

## Required Non-Implementations

- Do not call ParseUltimateRuntimeConfigPayload.
- This diagnostic does not include `UltimateRuntimeConfigParser`.
- It does not add parser payload bytes.
- It does not publish `candidate.view`.
- It does not assign candidate-owned table pointers to the active view.
- It does not copy generated tables into RAM for active publication.
- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Nunchuk remains NOT_TESTED.

## Diagnostic State

- `active_behavior_changed`: `true`
- `hardware_test_required_before_merge`: `true`
- `generated_source_owned_baseline_active`: `true`
- `generated_baseline_equivalent_to_source_owned_baseline`: `true`
- `ram_backed_active_table_publication`: `false`
- `candidate_view_published_active`: `false`
- `candidate_owned_table_pointer_published_active`: `false`
- `parser_payload_path_implemented`: `false`
- `runtime_loaded_config_implemented`: `false`
- `storage_implemented`: `false`
- `webserial_device_write_implemented`: `false`
- `backend_config_pb_write_path_implemented`: `false`
- `flashing_automation_implemented`: `false`
- `nunchuk_status`: `NOT_TESTED`

## Resolver Chain

```text
UpdateAnalogOutputs
  -> ResolveActiveRuntimeConfig
  -> GetActiveRuntimeConfigState
  -> active_view pointing to generated source-owned baseline RuntimeConfigView
```

## Evidence Basis

- Source-owned active-state preselection: `HARDWARE_PASS`.
- Parsed/candidate machinery present while source-owned active view remains
  published: `HARDWARE_PASS`.
- Parsed candidate view published active: `HARDWARE_FAIL`.
- Source-owned-materialized candidate view published active: `HARDWARE_FAIL`.
- Dedicated active storage published active: `HARDWARE_FAIL`.
- RAM-backed active table publication remains unsafe under current diagnostics.
- Generated source-owned artifacts are the intended path.
- Generated baseline artifact equivalence is checker-proven against
  `kSourceOwnedCurrentBaselineRuntimeConfig`.
- The low-level failure mechanism remains unproven.

## Merge Gate

This branch changes active firmware behavior and must not merge until the
hardware plan records a preserved non-nunchuk `HARDWARE_PASS`. Nunchuk remains
NOT_TESTED unless explicitly exercised and recorded.
