# Glyph Offline Remapper Manual Experiment Packet - 2026-06-03

## Purpose and scope

This document records the exact future manual/no-device import/export
experiment packet for checking external-remapper adapter feasibility without
implementing an adapter and without touching live hardware.

The packet status is:

- `planned_not_executed`

This packet is planned not executed. Adapter not implemented. This is not
device write behavior, not WebSerial write behavior, not official
compatibility, and not hardware validation.

No live device is allowed for this packet. No Save to Device is allowed. No
WebSerial write is allowed. No firmware flashing is allowed. External source
observations remain non-authoritative comparison inputs only.

## Experiment scope

The future manual/no-device experiment is limited to the following scope:

- no-device import/export compatibility check
- external remapper app/repo version recording
- sample input artifact hashes
- import attempt
- export attempt
- JSON diff report
- accepted/rejected field list
- screenshots/notes optional

The packet defines what a future manual operator run must record. It does not
execute the experiment, generate a compatibility verdict, implement an
adapter, enable runtime-loaded config, or approve device-write behavior.

## Prerequisites

The experiment must not be attempted until all of the following are current or
recorded:

- source audit snapshot current
- gap matrix current
- license review status recorded
- no live device connected
- browser/environment noted
- input artifacts checksummed

## Candidate inputs

The future manual/no-device run is limited to these committed sample artifacts
and their current SHA-256 hashes:

| Input | Path | SHA-256 |
| --- | --- | --- |
| Senscope export package sample | `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json` | `c5f1a687315571ca1a7d634ba1c50d52f4d1a035d8c538d7920133173d622d27` |
| Runtime config candidate sample | `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json` | `e4e9b0e47b36f9f8585b37ac0e9f3cba2b6ae2833d79121e99af602c9d48543f` |
| Active profile artifact | `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json` | `0a9c70f6a0c1bb8c347a811df2ec327c176482dc9c35f433c45bd3454e704707` |

These candidate inputs are comparison-only artifacts. They do not authorize
device writing, WebSerial transport, runtime-loaded config, official
compatibility claims, or hardware validation.

## Planned operator actions

If the experiment is approved and executed later in a separate result packet,
the manual run should record:

- external remapper app URL/version/commit if available
- browser/environment notes
- import attempt notes
- export attempt notes
- JSON diff report
- accepted/rejected field list
- optional screenshots/notes

## Forbidden actions

The future experiment explicitly forbids all of the following:

- connecting live Glyph
- WebSerial write
- Save to Device
- firmware flashing
- claiming official compatibility
- claiming hardware validation
- copying external source code
- changing repo fixtures to fit external app

This means the packet stays no live device, no WebSerial write, no Save to
Device, adapter not implemented, not official compatibility, and not hardware
validation.

## Result recording requirements

If the experiment is ever executed later, results must be recorded in a
separate result doc/fixture pair and must include all of the following:

- separate result doc/fixture
- external app URL/version/commit if available
- browser/environment
- input artifact hash
- exported artifact hash
- pass/fail/blocked rows
- no-device confirmation
- no hardware validation caveat
- no source-authority promotion caveat

The future result artifact must keep compatibility observations separate from
source authority. It must not claim official compatibility, hardware
validation, device write behavior, WebSerial behavior, or promotion of
external observations into firmware/configurator authority.

## Source inputs

This packet is bounded to already committed docs/tools/fixtures:

- `docs/calibration/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_adapter_target_contract_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_adapter_target_contract_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_adapter_gap_matrix_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_adapter_gap_matrix_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_source_snapshot_index_2026-06-03.json`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`

## Required fixture fields

The fixture for this packet must preserve these top-level fields:

- `schema_name=glyph_offline_remapper_manual_experiment_packet`
- `packet_version=1`
- `status=planned_not_executed`
- `hardware_status=not_new_hardware_result`
- `experiment_executed=false`
- `adapter_implemented=false`
- `device_write_allowed=false`
- `webserial_write_allowed=false`
- `external_source_promoted_to_authority=false`

## Checker output

`tools/check_glyph_offline_remapper_manual_experiment_packet.py` prints:

- `glyph_offline_remapper_manual_experiment_packet`
- `status=PASS` or `status=FAIL`
- `experiment_executed=false`
- `adapter_implemented=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the docs/fixture remain planned not
executed, no live device, no WebSerial write, no Save to Device, adapter not
implemented, not official compatibility, and not hardware validation.
