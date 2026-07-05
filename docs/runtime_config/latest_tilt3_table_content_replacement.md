# Latest Tilt3 Table Content Replacement

Status: FIRMWARE_BEHAVIOR_PENDING_HARDWARE.

Branch:
`runtime-config-latest-tilt3-table-content-replacement`

This packet records the source-owned table-content replacement branch that
applies only the latest intended `kTilt3Table` x/y values from
`codex/update-custom-modifier-tables-y2` onto current `configurator`.

The source path follows
`docs/runtime_config/latest_layout_y2_port_plan.md`: direct merge of
`codex/update-custom-modifier-tables-y2` is forbidden, and only the existing
source-owned `kTilt3Table` is eligible for this table-content-only branch.

## Firmware Change

- Changed source file: `src/modes/UltimateIdentityRuntimeTables.hpp`.
- Changed table: `kTilt3Table`.
- Replacement input fixture:
  `docs/runtime_config/fixtures/latest_tilt3_table_content_replacement_input.json`.
- Replacement generator:
  `tools/generate_source_owned_table_replacement.py`.

The intended `kTilt3Table` values are:

| Direction | x | y |
| --- | ---: | ---: |
| 1 | 69 | 82 |
| 2 | 128 | 83 |
| 3 | 187 | 82 |
| 4 | 69 | 128 |
| 5 | 128 | 128 |
| 6 | 187 | 128 |
| 7 | 76 | 169 |
| 8 | 128 | 179 |
| 9 | 180 | 169 |

## Boundary

- `active_behavior_changed`: `true`
- `hardware_test_required_before_merge`: `true`
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
- `root_cause_proven`: `false`

## Explicit Non-Claims

This branch does not modify `src/modes/Ultimate.cpp`.

This branch does not modify
`src/modes/UltimateRuntimeConfigInterpreter.hpp`.

This branch does not implement Y2 routing, a Y2 table identity, or an LT3 Y2
role change.

This branch does not modify RuntimeConfigView symbols, active-state selection,
candidate view publication, active view selection, or generated active
wrappers.

This branch does not implement parser/runtime-loaded config, persistent
storage, storage write, WebSerial/device write, backend/config.pb write paths,
or flashing automation.

No nunchuk validation is claimed; Nunchuk remains `NOT_TESTED`.

## Merge Gate

Because this branch changes active output coordinates, hardware PASS is
required before the active behavior change may remain merged into
`configurator`. The hardware plan is recorded in
`docs/calibration/latest_tilt3_table_content_replacement_hardware_plan_2026-06-29.md`.
