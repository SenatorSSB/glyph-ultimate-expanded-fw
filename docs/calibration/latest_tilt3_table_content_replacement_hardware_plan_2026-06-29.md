# Latest Tilt3 Table Content Replacement Hardware Plan - 2026-06-29

Status: PLAN_ONLY.

Branch under test:
`runtime-config-latest-tilt3-table-content-replacement`

This plan gates the branch that replaces only the source-owned
`kTilt3Table` contents in
`src/modes/UltimateIdentityRuntimeTables.hpp`. It records no hardware result.

## Required Result Boundary

- `hardware_test_required_before_merge`: `true`
- `active_behavior_changed`: `true`
- `latest_layout_partial_port`: `true`
- `implements_y2_routing`: `false`
- `implements_y2_table_identity`: `false`
- `implements_lt3_y2_role`: `false`
- `active_view_selection_changed`: `false`
- `runtime_config_view_replacement`: `false`
- `source_owned_table_content_replacement_wired`: `true`
- `runtime_loaded_config_implemented`: `false`
- `persistent_storage_implemented`: `false`
- `webserial_device_write_implemented`: `false`
- `backend_config_pb_write_path_implemented`: `false`
- `flashing_automation_implemented`: `false`
- `nunchuk_status`: `NOT_TESTED`

## Rows

| Row | Status | Notes |
| --- | --- | --- |
| BOOT-001 | NOT_TESTED | Device boots and enumerates. |
| BASELINE-001 | NOT_TESTED | Baseline movement remains usable for applicable non-nunchuk scope. |
| RF5-001 | NOT_TESTED | Forced A+Up remains usable. |
| LT6-001 | NOT_TESTED | Forced A+Down remains usable. |
| ORDINARY-DIR-001 | NOT_TESTED | Ordinary directions remain usable. |
| NEUTRAL-001 | NOT_TESTED | Neutral output remains usable. |
| TILT3-TABLE-001 | NOT_TESTED | Latest intended Tilt3 table values are active. |
| ACTIVE-VIEW-SELECTION-UNCHANGED-001 | NOT_TESTED | Active view selection remains unchanged. |
| RUNTIMECONFIGVIEW-UNCHANGED-001 | NOT_TESTED | RuntimeConfigView symbols and replacement path remain unchanged. |
| Y2-ROUTING-NOT-IMPLEMENTED-001 | NOT_TESTED | Y2 routing, Y2 table identity, and LT3 Y2 role are not implemented. |
| NO-PARSER-001 | NOT_TESTED | No parser/runtime-loaded config path is implemented. |
| NO-STORAGE-001 | NOT_TESTED | No persistent storage path is implemented. |
| NO-WRITE-001 | NOT_TESTED | No storage write, WebSerial/device write, or backend/config.pb write path is implemented. |
| NO-FLASH-001 | NOT_TESTED | No firmware flashing automation is implemented. |
| NUNCHUK-001 | NOT_TESTED | Nunchuk remains NOT_TESTED. |

## Merge Gate

Do not let this active behavior change remain merged into `configurator`
unless a later result packet records a preserved `HARDWARE_PASS` for the
applicable non-nunchuk scope. Nunchuk remains NOT_TESTED unless explicitly
exercised.
