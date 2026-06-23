# Active Storage Publication Model

status: INACTIVE_SCAFFOLD

branch: `runtime-config-active-storage-publication-model`

baseline branch: `configurator`

## Purpose

Define the next safe runtime-config publication model after candidate-backed
active runtime views reproduced hardware disconnects.

This branch keeps active output behavior source-owned baseline. Dedicated active
storage is scaffolded but not activated. The active output path still consumes
the safe currently published source-owned view.

## Evidence Matrix

| Case | Result |
| --- | --- |
| source-owned active-state preselection | HARDWARE_PASS |
| prior diagnostic: parsed/candidate machinery present, source-owned active view | HARDWARE_PASS |
| parsed candidate.view active | HARDWARE_FAIL |
| source-owned-materialized candidate.view active | HARDWARE_FAIL |

Machine-readable summary:

- source-owned active-state preselection: HARDWARE_PASS
- prior diagnostic: parsed/candidate machinery present, source-owned active view: HARDWARE_PASS
- parsed candidate.view active: HARDWARE_FAIL
- source-owned-materialized candidate.view active: HARDWARE_FAIL

## Publication Rule

candidate buffer != active buffer

Required future publication chain:

```text
candidate validates proposed values
  -> accepted values are copied into dedicated active storage
  -> active RuntimeConfigView points to dedicated active storage
  -> candidate.view is never active
```

Candidate-backed active RuntimeConfigView publication is forbidden.
Candidate-owned runtime table pointers must not be published active.

## Source Boundary

- `RuntimeConfigActiveStorageStatus` and `RuntimeConfigActiveStorage` are
  compile-present in firmware source.
- `ResetRuntimeConfigActiveStorage(...)`,
  `ValidateRuntimeConfigActiveStorage(...)`, and
  `CopyRuntimeConfigViewIntoActiveStorage(...)` are source-local scaffolding.
- Dedicated active storage can copy a validated/equivalent source view into
  active-owned arrays.
- Candidate storage is not assigned to active publication state.
- Parser/payload machinery is not part of this branch.
- Do not include UltimateRuntimeConfigParser.hpp.
- Do not call ParseUltimateRuntimeConfigPayload.
- `GetActiveRuntimeConfigState()` continues publishing
  `kSourceOwnedCurrentBaselineRuntimeConfig`.
- `ResolveActiveRuntimeConfig()` dereferences only the active view.
- `UpdateAnalogOutputs(...)` binds runtime config through
  `ResolveActiveRuntimeConfig()`.
- `UpdateAnalogOutputs(...)` does not mention candidate, parser, decision,
  status, storage, write, WebSerial, flash, or load state.
- `UpdateDigitalOutputs(...)` remains unchanged relative to `configurator`.
- RF5/RF6/LT6 expressions remain present.
- Parser payload path is not implemented on this branch.

## Conclusions

- `candidate_backed_active_runtime_view_safe`: `false`
- `candidate_buffer_may_validate_values`: `true`
- `candidate_buffer_must_not_be_active`: `true`
- `dedicated_active_storage_required`: `true`
- `dedicated_active_storage_scaffolded`: `true`
- `dedicated_active_storage_active`: `false`
- `active_behavior_changed`: `false`
- `hardware_test_required_before_merge`: `false`
- `parser_payload_path_implemented`: `false`
- `low_level_failure_mechanism_proven`: `false`
- `runtime_loaded_config_implemented`: `false`
- `storage_implemented`: `false`
- `webserial_device_write_implemented`: `false`
- `flashing_automation_implemented`: `false`
- `nunchuk_status`: `NOT_TESTED`

## Hardware

hardware_test_required_before_merge: false

No hardware test is required before merge for this branch because active
behavior remains source-owned baseline and dedicated active storage is only
scaffolded.

If a later branch publishes dedicated active storage as the active view, that
later branch must set `hardware_test_required_before_merge: true` and record a
hardware diagnostic before merge.

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Parser payload path is not implemented.
- Candidate active publication is not implemented.
- Dedicated active storage active publication is not implemented.
- The low-level failure mechanism is not proven.
- Nunchuk remains NOT_TESTED.

## Next Diagnostic

The explicit next recommended diagnostic, if prioritized, is a hardware-gated
branch that publishes only source-owned-equivalent dedicated active storage as
the active view. Stop before enabling it on this branch.
