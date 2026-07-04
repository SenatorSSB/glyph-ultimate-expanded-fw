# Diagnostic Source-Owned Table Content Replacement Hardware Plan

Status label: PLAN / NOT_TESTED.

This plan covers the hardware-gated diagnostic branch
`runtime-config-diagnostic-source-owned-table-content-replacement`.

The branch changes one existing source-owned `StickPoint` table value while
preserving the current active `RuntimeConfigView`, active state,
`RuntimeTableView` array identity/path, and resolver chain.

## Required Conditions

- `active_behavior_changed`: `true`
- `hardware_test_required_before_merge`: `true`
- `active_view_selection_changed`: `false`
- `runtime_config_view_replacement`: `false`
- `source_owned_table_content_replacement_wired`: `true`
- Runtime-loaded config/storage/write/WebSerial/flashing/backend config.pb
  behavior remains not implemented.
- Nunchuk remains `NOT_TESTED`.

## Planned Rows

| Row | Status | Planned check |
| --- | --- | --- |
| BOOT-001 | NOT_TESTED | Device boots and enumerates normally. |
| BASELINE-001 | NOT_TESTED | Existing baseline behavior remains usable. |
| RF5-001 | NOT_TESTED | RF5 behavior remains preserved. |
| LT6-001 | NOT_TESTED | LT6 direction-plus-A behavior remains preserved. |
| ORDINARY-DIR-001 | NOT_TESTED | Ordinary directions remain preserved. |
| NEUTRAL-001 | NOT_TESTED | Neutral/center behavior remains controlled. |
| TABLE-CONTENT-REPLACEMENT-001 | NOT_TESTED | `kRT1RF4CustomTable[4]` content replacement does not trigger the prior disconnect class. |
| ACTIVE-VIEW-SELECTION-UNCHANGED-001 | NOT_TESTED | Active selection remains source-owned baseline path. |
| RUNTIMECONFIGVIEW-UNCHANGED-001 | NOT_TESTED | No generated/replaced `RuntimeConfigView` is active. |
| NO-PARSER-001 | NOT_TESTED | No parser/runtime-loaded config behavior is present. |
| NO-STORAGE-001 | NOT_TESTED | No persistent storage behavior is present. |
| NO-WRITE-001 | NOT_TESTED | No WebSerial/device/backend config.pb write behavior is present. |
| NO-FLASH-001 | NOT_TESTED | No flashing automation is present. |
| NUNCHUK-001 | NOT_TESTED | Nunchuk remains untested and no validation is claimed. |

## Merge Gate

Because active behavior changed, this diagnostic must preserve a recorded
`HARDWARE_PASS` result before the source content change can remain merged into
`configurator`.
