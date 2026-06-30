# Diagnostic Generated Source-Owned Baseline Active Hardware Failure - 2026-06-29

status: HARDWARE_FAIL
overall_result: HARDWARE_FAIL

branch_under_test: `runtime-config-diagnostic-generated-source-owned-baseline-active`
result_branch: `runtime-config-diagnostic-generated-source-owned-baseline-active-hardware-failure`
baseline_branch: `configurator`

## Observed Hardware Result

The generated source-owned baseline active diagnostic failed hardware testing.

Observed failure symptoms:

- Forced A + Up still disconnects.
- Forced A + Down still disconnects.
- Initial two Up+A presses did not immediately disconnect, but subsequent
  presses reproduced the same disconnect behavior.
- Across failed firmware diagnostics, after reconnect the controller has often
  been stuck with left stick fully down or fully up.

Nunchuk remains NOT_TESTED.

## Result Scope

This result applies only to the generated source-owned baseline active
diagnostic branch under test. It records that selecting the generated
source-owned baseline-equivalent `RuntimeConfigView` as active was not safe in
this diagnostic, even though generated table data was source-owned, immutable,
and baseline-equivalent.

The low-level mechanism remains unproven. This packet does not claim root cause
has been isolated, does not claim nunchuk validation, and does not claim any
runtime-loaded config, persistent storage, WebSerial/device write,
backend/config.pb write path, or flashing automation implementation.

Do not merge the failed implementation branch into `configurator`.

## Diagnostic State

- `active_behavior_changed`: `true`
- `hardware_test_required_before_merge`: `true`
- `merge_approved`: `false`
- `generated_source_owned_baseline_active`: `true`
- `generated_baseline_equivalent_to_source_owned_baseline`: `true`
- `ram_backed_active_table_publication`: `false`
- `candidate_view_published_active`: `false`
- `candidate_owned_table_pointer_published_active`: `false`
- `parser_payload_path_implemented`: `false`
- `runtime_loaded_config_implemented`: `false`
- `persistent_storage_implemented`: `false`
- `storage_implemented`: `false`
- `webserial_device_write_implemented`: `false`
- `backend_config_pb_write_path_implemented`: `false`
- `flashing_automation_implemented`: `false`
- `nunchuk_status`: `NOT_TESTED`
- `root_cause_proven`: `false`

## Failure Symptoms

| Symptom | Status |
| --- | --- |
| forced A + Up disconnect | OBSERVED |
| forced A + Down disconnect | OBSERVED |
| initial two Up+A presses did not immediately disconnect | OBSERVED |
| reconnect sometimes stuck left stick fully down or fully up across failed diagnostics | OBSERVED |

## Conclusions

- Generated source-owned baseline active diagnostic failed hardware testing.
- Generated/source-owned/baseline-equivalent table data was not sufficient for
  safe active publication.
- Failure is not isolated to RAM-backed active table storage.
- Changing active `RuntimeConfigView`/table publication path remains unsafe
  under this diagnostic.
- Source-owned active-state preselection remains the last known passing
  active-runtime boundary.
- The low-level mechanism remains unproven.
- The implementation branch must not merge into `configurator`.

## Future Realization Strategy

Future realization should avoid `RuntimeConfigView` replacement as the active
customization mechanism unless a narrower hardware-validated diagnostic proves
otherwise.

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- Persistent storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- No push-to-device behavior is implemented or claimed.
- No nunchuk validation is claimed.
- Nunchuk remains NOT_TESTED.
- Root cause is not proven.
