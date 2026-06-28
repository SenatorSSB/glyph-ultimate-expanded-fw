# Diagnostic Active Storage Published Hardware Failure - 2026-06-28

status: HARDWARE_FAIL
overall_result: HARDWARE_FAIL

branch_under_test: `runtime-config-diagnostic-active-storage-published`
result_branch: `runtime-config-diagnostic-active-storage-published-hardware-failure`
baseline_branch: `configurator`

## Observed Hardware Result

The dedicated active-storage publication diagnostic failed hardware testing.
The observed failure symptom is that controller disconnect still happens during
forced A + Up and forced A + Down.

Nunchuk remains NOT_TESTED.

## Result Scope

This result applies only to the dedicated active-storage publication diagnostic
branch under test. It records that publishing RAM-backed dedicated active
storage as the active `RuntimeConfigView` is not safe in this diagnostic.

The low-level mechanism remains unproven. This packet does not claim a cause
has been isolated, does not claim nunchuk validation, and does not claim any
runtime-loaded config, persistent storage, WebSerial/device write,
backend/config.pb write path, or flashing automation implementation.

Do not merge the failed implementation branch.

## Diagnostic State

- `active_behavior_changed`: `true`
- `hardware_test_required_before_merge`: `true`
- `merge_approved`: `false`
- `dedicated_active_storage_active`: `true`
- `dedicated_active_storage_published_active`: `true`
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

## Conclusions

- Dedicated active storage publication failed hardware testing.
- Dedicated active storage published active is unsafe under this diagnostic.
- Dedicated active storage published as the active `RuntimeConfigView` is not
  safe in this diagnostic.
- RAM-backed active table storage is unsafe as an active publication target
  under this test.
- RAM-backed active runtime table storage appears unsafe as an active
  publication target under this test, even when source-owned-equivalent,
  validated, equivalence-checked, parser-free, and not candidate-owned.
- The low-level mechanism remains unproven.
- Candidate-backed active view remains forbidden.
- Dedicated active storage may remain as archived diagnostic evidence only, not
  as an active firmware path.
- The implementation branch must not merge into `configurator`.

## Future Realization Strategy

Future realization work should pivot away from RAM-backed active table pointer
publication. Preferred next strategies to document are:

Future strategy should pivot away from RAM-backed active table pointer
publication.

1. compile-time/generated immutable source-owned tables;
2. source-owned table replacement / generated firmware artifacts;
3. no runtime-loaded publication until a safer active-storage model is proven.

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
