# Latest Y2 Layout Source-Owned Port Hardware Result - 2026-06-29

status: HARDWARE_PASS
overall_result: HARDWARE_PASS

branch_under_test: `runtime-config-latest-y2-layout-source-owned-port`
result_branch: `runtime-config-latest-y2-layout-source-owned-port-hardware-result`
baseline_branch: `configurator`

user_report: `everything works, all usual tests pass, including Up+A and Down+A`

## Observed Hardware Result

The full latest Y2 layout source-owned port passed hardware testing.

- RF5-001 / forced A + Up: PASS, no disconnect.
- LT6-001 / forced A + Down: PASS, no disconnect.
- Everything works and all usual tests pass.
- Full latest Y2 layout behavior is accepted by hardware testing.
- Y1 simple / Y2 sublayer migration is accepted by hardware testing.
- Nunchuk remains NOT_TESTED.

## Result Boundary

- `merge_approved`: `true`
- `active_behavior_changed`: `true`
- `hardware_test_required_before_merge`: `true`
- `full_latest_layout_port`: `true`
- `active_view_selection_changed`: `false`
- `runtime_config_view_replacement`: `false`
- `generated_active_wrapper_used`: `false`
- `candidate_view_published_active`: `false`
- `ram_backed_active_table_publication`: `false`
- `source_owned_table_content_replacement_wired`: `true`
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
| BOOT-001 | Boot and USB stability | PASS |
| RF5-001 | Forced A + Up | PASS |
| LT6-001 | Forced A + Down | PASS |
| ORDINARY-DIR-001 | Ordinary direction behavior | PASS |
| NEUTRAL-001 | Neutral behavior | PASS |
| TILT3-TABLE-001 | Tilt3 table emits latest required values | PASS |
| Y2-TABLE-001 | Y2 table emits latest required values | PASS |
| LT3-Y2-001 | LT3 selects Y2 | PASS |
| NO-LR-BUTTON-001 | LT3 emits no L/R digital | PASS |
| Y2-RF1-001 | Y2+RF1 cases match the required layout | PASS |
| Y2-RF2-001 | Y2+RF2 cases match the required layout | PASS |
| Y2-RF3-001 | Y2+RF3 cases match the required layout | PASS |
| Y2-RF4-001 | Y2+RF4 cases match the required layout | PASS |
| Y2-RT1-001 | Y2+RT1 selects Tilt2 | PASS |
| Y2-RT1-RF4-TILT3-001 | Y2+RT1+RF4 selects Tilt3 | PASS |
| Y1-SUBLAYER-REMOVED-001 | Y1 no longer owns the old RF sublayers | PASS |
| ACTIVE-VIEW-SELECTION-UNCHANGED-001 | Source-owned active view selection remains unchanged | PASS |
| RUNTIMECONFIGVIEW-UNCHANGED-001 | RuntimeConfigView replacement is not used | PASS |
| NO-PARSER-001 | No parser/runtime-loaded path is implemented | PASS |
| NO-STORAGE-001 | No persistent storage is implemented | PASS |
| NO-WRITE-001 | No WebSerial/device/backend write path is implemented | PASS |
| NO-FLASH-001 | No firmware flashing automation is implemented | PASS |
| NUNCHUK-001 | Nunchuk scope | NOT_TESTED |
| Y1-SIMPLE-001 | Y1 is a simple modifier only | PASS |
| Y1-RF-SUBLAYER-REMOVED-001 | Y1 RF sublayers are removed | PASS |
| Y2-SUBLAYER-MIGRATION-001 | Former Y1 RF sublayers are migrated to Y2 | PASS |

## Conclusions

- The full latest Y2 layout source-owned port is merge-approved after
  `HARDWARE_PASS`.
- Active RuntimeConfigView selection remains unchanged.
- RuntimeConfigView replacement is not used.
- Generated active wrapper is not used.
- `candidate.view` is not active.
- RAM-backed active table publication is not used.
- Source-owned table/routing source path passed hardware for this layout.
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
