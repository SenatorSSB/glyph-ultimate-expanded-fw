# Alternative B Generated Table Alias Candidate Hardware Result - 2026-07-09

status: HARDWARE_PASS
overall_result: HARDWARE_PASS

branch_under_test: `runtime-config-alt-b-generated-table-alias-candidate`
commit_under_test: `ee5fd35c4ce00e31d9a00905c771699ad17517b9`
baseline_branch: `configurator`

user_reported_result: “Tested everything, everything worked.”

## Observed Hardware Result

The Alternative B source-owned generated-table alias candidate passed
user-reported hardware testing.

- Boots/connects: PASS.
- Latest Y2 layout behavior: PASS.
- Usual layout tests: PASS.
- Up+A: PASS.
- Down+A: PASS.
- RF5 forced A + Up: PASS.
- LT6 forced A + Down: PASS.
- Nunchuk remains NOT_TESTED.

## Result Boundary

- `merge_approved`: `true`
- `active_behavior_changed`: `true`
- `hardware_test_required_before_merge`: `true`
- `alternative_b_generated_table_alias_candidate`: `true`
- `active_publication_path_preserved`: `true`
- `active_view_publication_symbol`: `&kSourceOwnedCurrentBaselineRuntimeConfig`
- `active_state_entrypoint`: `GetActiveRuntimeConfigState()`
- `active_resolution_entrypoint`: `ResolveActiveRuntimeConfig()`
- `runtime_config_view_replacement`: `false`
- `generated_active_wrapper_used`: `false`
- `candidate_view_published_active`: `false`
- `ram_backed_active_table_publication`: `false`
- `runtime_loaded_config_implemented`: `false`
- `persistent_storage_implemented`: `false`
- `webserial_device_write_implemented`: `false`
- `backend_config_pb_write_path_implemented`: `false`
- `flashing_automation_implemented`: `false`
- `nunchuk_status`: `NOT_TESTED`
- `root_cause_proven`: `false`

## Hardware Result Rows

| Row ID | Scope | Status |
| --- | --- | --- |
| BOOT-CONNECT-001 | Boots/connects | PASS |
| LATEST-Y2-001 | Latest Y2 layout behavior | PASS |
| USUAL-LAYOUT-001 | Usual layout tests | PASS |
| UP-A-001 | Up+A | PASS |
| DOWN-A-001 | Down+A | PASS |
| RF5-FORCED-A-UP-001 | RF5 forced A + Up | PASS |
| LT6-FORCED-A-DOWN-001 | LT6 forced A + Down | PASS |
| ACTIVE-PUBLICATION-001 | Active publication remains through `&kSourceOwnedCurrentBaselineRuntimeConfig` | PASS |
| ACTIVE-STATE-001 | `GetActiveRuntimeConfigState()` path remains active | PASS |
| ACTIVE-RESOLVE-001 | `ResolveActiveRuntimeConfig()` path remains active | PASS |
| NO-RUNTIME-LOADED-CONFIG-001 | Runtime-loaded profile/config is not implemented | PASS |
| NO-WEBSERIAL-WRITE-001 | WebSerial/device write is not implemented | PASS |
| NUNCHUK-001 | Nunchuk scope | NOT_TESTED |
| ROOT-CAUSE-001 | Root cause | UNPROVEN |

## Notes

- This validates the Alternative B source-owned generated-table alias
  candidate.
- Active publication remains through
  `&kSourceOwnedCurrentBaselineRuntimeConfig`.
- `GetActiveRuntimeConfigState()` / `ResolveActiveRuntimeConfig()` path remains
  the active publication path.
- This does not validate runtime-loaded profiles or device-write flows.

## Conclusions

- The Alternative B generated-table alias candidate is merge-approved after
  `HARDWARE_PASS`.
- Generated table aliasing is hardware-passed only when preserving the existing
  active `RuntimeConfigView` publication path.
- C/D/E forbidden active-publication paths remain forbidden.
- Runtime-loaded profile/config remains not implemented.
- WebSerial/device write remains not implemented.
- Low-level root cause remains unproven.
- Nunchuk remains NOT_TESTED.

## Non-Claims

- Runtime-loaded config is not implemented.
- Persistent storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- No push-to-device behavior is implemented or claimed.
- Root cause is not proven.
- No nunchuk PASS claim is made.
