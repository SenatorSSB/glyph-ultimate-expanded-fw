# Latest Y2 Layout Source-Owned Port Hardware Plan - 2026-06-29

Status: PLAN_ONLY.

Branch under test:
`runtime-config-latest-y2-layout-source-owned-port`

This plan gates the full required latest Y2 layout restored on the source-owned
active path. It is not a Tilt3-only plan and records no hardware result yet.

## Required Result Boundary

- `hardware_test_required_before_merge`: `true`
- `full_latest_layout_port`: `true`
- `partial_tilt3_only_port`: `false`
- `active_behavior_changed`: `true`
- `active_view_selection_changed`: `false`
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

## Evidence Basis

- Source-owned active-state preselection: `HARDWARE_PASS`.
- Source-owned table-content replacement boundary for RF5 forced A+Up and LT6
  forced A+Down: `HARDWARE_PASS`.
- RuntimeConfigView replacement paths: `HARDWARE_FAIL`.
- RAM-backed active table publication: `HARDWARE_FAIL`.
- Low-level root cause remains unproven.

## Rows

| Row | Status | Notes |
| --- | --- | --- |
| BOOT-001 | NOT_TESTED | Device boots and enumerates. |
| RF5-001 | NOT_TESTED | RF5 forced A+Up source path remains present. |
| LT6-001 | NOT_TESTED | LT6 forced A+Down source path remains present. |
| ORDINARY-DIR-001 | NOT_TESTED | Ordinary directions remain usable. |
| NEUTRAL-001 | NOT_TESTED | Neutral output remains usable. |
| TILT3-TABLE-001 | NOT_TESTED | Tilt3 table emits latest required values. |
| Y2-TABLE-001 | NOT_TESTED | Y2 table emits latest required values. |
| LT3-Y2-001 | NOT_TESTED | LT3 selects Y2. |
| NO-LR-BUTTON-001 | NOT_TESTED | LT3 emits no L/R digital. |
| Y2-RF1-001 | NOT_TESTED | Y2+RF1 cases match the required layout. |
| Y2-RF2-001 | NOT_TESTED | Y2+RF2 cases match the required layout. |
| Y2-RF3-001 | NOT_TESTED | Y2+RF3 cases match the required layout. |
| Y2-RF4-001 | NOT_TESTED | Y2+RF4 cases match the required layout. |
| Y2-RT1-001 | NOT_TESTED | Y2+RT1 selects Tilt2. |
| Y2-RT1-RF4-TILT3-001 | NOT_TESTED | Y2+RT1+RF4 selects Tilt3. |
| Y1-SUBLAYER-REMOVED-001 | NOT_TESTED | Y1 no longer owns the old RF sublayers. |
| ACTIVE-VIEW-SELECTION-UNCHANGED-001 | NOT_TESTED | Source-owned active view selection remains unchanged. |
| RUNTIMECONFIGVIEW-UNCHANGED-001 | NOT_TESTED | RuntimeConfigView replacement is not used. |
| NO-PARSER-001 | NOT_TESTED | No parser/runtime-loaded path is implemented. |
| NO-STORAGE-001 | NOT_TESTED | No persistent storage is implemented. |
| NO-WRITE-001 | NOT_TESTED | No WebSerial/device/backend write path is implemented. |
| NO-FLASH-001 | NOT_TESTED | No firmware flashing automation is implemented. |
| NUNCHUK-001 | NOT_TESTED | Nunchuk remains NOT_TESTED. |
| Y1-SIMPLE-001 | NOT_TESTED | Y1 is a simple modifier only. |
| Y1-RF-SUBLAYER-REMOVED-001 | NOT_TESTED | Y1 RF sublayers are removed. |
| Y2-SUBLAYER-MIGRATION-001 | NOT_TESTED | Former Y1 RF sublayers are migrated to Y2. |

## Merge Gate

Do not merge this active behavior change into `configurator` unless a later
result packet records a preserved `HARDWARE_PASS` for the applicable
non-nunchuk full-layout scope. Nunchuk remains NOT_TESTED unless explicitly
exercised and recorded.
