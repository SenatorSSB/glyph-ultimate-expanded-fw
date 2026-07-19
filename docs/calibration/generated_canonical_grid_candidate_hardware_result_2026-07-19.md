# Generated Canonical Grid Candidate Hardware Result - 2026-07-19

status: HARDWARE_FAIL
overall_result: HARDWARE_FAIL

branch_under_test: `runtime-config-generated-canonical-grid-candidate`
commit_under_test: `e643017c1577c9ca2b94581fa6f18c0dfb1bac9b`
baseline_branch: `configurator`
result_branch: `runtime-config-generated-canonical-grid-candidate-hardware-result`

user_reported_result: “The forced Up/Down + A and Up + B function normally. But none of the modifiers seems to affect the left stick anymore, except specifically Tilt3 function. All other input magnitude affecting buttons (including Z and Y2 sublayer) failed. Y2 did still change the button functions seemingly normally, just not the left stick modifying parts.”

## Observed Hardware Result

The generated canonical-grid candidate failed user-reported hardware testing.

- Boots/connects: PASS, inferred from the report because the controller
  accepted and produced multiple tested inputs without a disconnect report.
- Forced Up + A: PASS.
- Forced Down + A: PASS.
- Up + B: PASS.
- Y2 button-function/routing changes: PASS.
- Tilt3 left-stick modification: PASS.
- Modifier-driven left-stick magnitude changes generally: FAIL.
- Z magnitude modification: FAIL.
- Y2 sublayer left-stick modification: FAIL.
- Nunchuk remains NOT_TESTED.

## Result Boundary

- `merge_approved`: `false`
- `candidate_must_not_merge`: `true`
- `result_branch_evidence_only`: `true`
- `active_behavior_changed`: `true`
- `hardware_test_required_before_merge`: `true`
- `runtime_loaded_config_implemented`: `false`
- `persistent_storage_implemented`: `false`
- `webserial_device_write_implemented`: `false`
- `backend_config_pb_write_path_implemented`: `false`
- `protobuf_binary_write_implemented`: `false`
- `flashing_automation_implemented`: `false`
- `nunchuk_status`: `NOT_TESTED`
- `root_cause_proven`: `false`

## Hardware Result Rows

| Row ID | Scope | Status |
| --- | --- | --- |
| BOOT-CONNECT-001 | Boots/connects, inferred from continued input testing | PASS |
| FORCED-UP-A-001 | Forced Up + A | PASS |
| FORCED-DOWN-A-001 | Forced Down + A | PASS |
| UP-B-001 | Up + B | PASS |
| Y2-ROUTING-001 | Y2 button-function/routing changes | PASS |
| TILT3-LS-001 | Tilt3 left-stick modification | PASS |
| MOD-LS-001 | Modifier-driven left-stick magnitude changes generally | FAIL |
| Z-LS-001 | Z magnitude modification | FAIL |
| Y2-LS-001 | Y2 sublayer left-stick modification | FAIL |
| NO-RUNTIME-LOADED-CONFIG-001 | Runtime-loaded profile/config is not implemented | PASS |
| NO-WEBSERIAL-WRITE-001 | WebSerial/device write is not implemented | PASS |
| NUNCHUK-001 | Nunchuk scope | NOT_TESTED |
| ROOT-CAUSE-001 | Root cause | UNPROVEN |

## Notes

- This result is direct hardware evidence for the branch and commit named
  above.
- The result is consistent with Y2/Tilt3 remaining source-aligned while the
  other 26 generated table records were replaced by canonical 0/128/255 grid
  contents.
- Routing and digital-side-effect behavior appears to remain functional in the
  tested Y2 scope.
- Most modifier-driven left-stick table behavior failed.
- The low-level firmware root cause remains unproven.
- This result branch descends from failed active source and is evidence only.

## Conclusions

- The generated canonical-grid candidate is rejected after `HARDWARE_FAIL`.
- The candidate branch must not be merged into `configurator`.
- This evidence branch must not be merged into `configurator` because it
  descends from the failed active source.
- Runtime-loaded profile/config remains not implemented.
- WebSerial/device write remains not implemented.
- Low-level root cause remains unproven.
- Nunchuk remains NOT_TESTED.

## Non-Claims

- Runtime-loaded config is not implemented.
- Persistent storage is not implemented.
- WebSerial/device write is not implemented.
- Protobuf binary write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- No push-to-device behavior is implemented or claimed.
- Root cause is not proven.
- No nunchuk PASS claim is made.
