# Diagnostic Active Storage Published

status: HARDWARE_GATED_DIAGNOSTIC

branch: `runtime-config-diagnostic-active-storage-published`

baseline branch: `configurator`

hardware_test_required_before_merge: true

## Purpose

Test whether a source-owned-equivalent `RuntimeConfigView` stored in dedicated
active storage can safely be published as the active runtime config view while
candidate storage remains non-active.

This branch intentionally does not use the parser payload path. It does not call
`ParseUltimateRuntimeConfigPayload`, does not include
`UltimateRuntimeConfigParser`, and does not publish `candidate.view`.

Do not call ParseUltimateRuntimeConfigPayload. Do not include
UltimateRuntimeConfigParser.

## Current Evidence

| Case | Result |
| --- | --- |
| source-owned active-state preselection | HARDWARE_PASS |
| parsed/candidate machinery present, source-owned active view published | HARDWARE_PASS |
| parsed candidate.view published active | HARDWARE_FAIL |
| source-owned-materialized candidate.view published active | HARDWARE_FAIL |

## Diagnostic Chain

Expected active resolver chain:

```text
UpdateAnalogOutputs
  -> ResolveActiveRuntimeConfig
  -> GetActiveRuntimeConfigState
  -> gActiveRuntimeConfigState.active_view
```

`ResolveActiveRuntimeConfig()` only dereferences the stable selected
`active_view`. `UpdateAnalogOutputs(...)` does not read candidate, parser,
decision, status, load, storage, write, WebSerial, or flash state.

## Source Boundary

- Dedicated active storage is copied from
  `kSourceOwnedCurrentBaselineRuntimeConfig`.
- Dedicated active storage is validated with `ValidateRuntimeConfigActiveStorage`.
- Dedicated active storage point/table equivalence against
  `kSourceOwnedCurrentBaselineRuntimeConfig` is validated before publication.
- Dedicated active storage is published as the active view only after validation
  and equivalence success.
- If validation or equivalence fails, the active view falls back to
  `kSourceOwnedCurrentBaselineRuntimeConfig`.
- `candidate.view` is never active.
- Candidate-owned table pointers are never assigned to the active view.
- `UpdateDigitalOutputs(...)` remains unchanged relative to `configurator`.
- RF5, RF6, and LT6 expressions remain preserved.

## Diagnostic State

- `active_behavior_changed`: `true`
- `hardware_test_required_before_merge`: `true`
- `dedicated_active_storage_active`: `true`
- `candidate_view_published_active`: `false`
- `candidate_owned_table_pointer_published_active`: `false`
- `published_active_view_when_equivalent`: `dedicated active storage view`
- `fallback_active_view`: `kSourceOwnedCurrentBaselineRuntimeConfig`
- `runtime_loaded_config_implemented`: `false`
- `storage_implemented`: `false`
- `webserial_device_write_implemented`: `false`
- `backend_config_pb_write_path_implemented`: `false`
- `flashing_automation_implemented`: `false`
- `nunchuk_status`: `NOT_TESTED`

## Hardware

No hardware result is claimed by this diagnostic packet.

This branch must not merge until the diagnostic hardware plan is executed and a
hardware PASS result is recorded for the applicable non-nunchuk scope.

Nunchuk remains NOT_TESTED.

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Parser payload path is not implemented.
- Persistent storage is not implemented.
- Nunchuk validation is not claimed.
- The low-level failure mechanism from prior active-candidate failures is not
  proven.
