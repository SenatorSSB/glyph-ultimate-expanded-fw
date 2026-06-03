# Glyph External Remapper Compatibility Experiment Plan - 2026-06-03

## Purpose and scope

This document records a future offline/manual import-export compatibility
experiment plan for checking whether a committed export package or runtime
config candidate could be transformed into something the external remapper can
import.

The plan status is:

- `planned_not_executed`

This branch does not implement or execute the experiment. This is not device
write behavior, not runtime-loaded config, not official compatibility, and not
hardware validation.

No live device is allowed for this plan. No WebSerial write is allowed. No
firmware flashing is allowed. No external source code was copied into this
repo, and external observations are not promoted to firmware or configurator
authority.

## Experiment type

- `offline/manual import-export compatibility experiment`

## Prerequisites

The experiment must not be attempted until all of the following are complete:

- full source audit
- license review
- static JSON schema comparison
- safe sample config generation
- no live device connected
- no WebSerial write
- no firmware flashing

## Candidate inputs

The future manual comparison is limited to committed or generated sample
artifacts only:

- Senscope export package sample
- runtime config candidate sample
- active profile artifact

These are comparison inputs only. They are not approval for device writing,
runtime-loaded config, official compatibility, or hardware validation.

## Expected outputs

If the experiment is performed in a later approved branch or manual operator
run, the expected outputs are:

- external-remapper import test notes
- JSON diff report
- rejected/accepted field list
- no device write confirmation

## Forbidden actions

The experiment plan explicitly forbids all of the following:

- connecting live device
- Save to Device
- WebSerial write
- firmware flashing
- claiming official compatibility
- claiming hardware validation
- copying external source code

This means the plan stays offline/manual only, no live device, no WebSerial
write, not device write behavior, not official compatibility, and not hardware
validation.

## Result recording requirements

If the experiment is ever executed later, record results in a separate result
doc/fixture pair and include all of the following:

- separate result doc/fixture
- external app/repo version or commit
- browser/environment notes
- exact sample artifact hash
- pass/fail/blocked rows
- no hardware validation caveat

The future result artifact must keep the distinction between compatibility
notes and source authority. It must not promote external observations to
firmware authority, configurator authority, official compatibility, device
write behavior, or hardware validation.

## Source inputs

This plan is bounded to already committed docs/tools/fixtures:

- `docs/calibration/glyph_external_remapper_adapter_boundary_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_adapter_boundary_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_source_snapshot_index_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_config_shape_matrix_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_config_shape_matrix_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_adapter_feasibility_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_adapter_feasibility_2026-06-03.json`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`

## Required fixture fields

The fixture for this plan must preserve these top-level fields:

- `schema_name=glyph_external_remapper_compatibility_experiment_plan`
- `plan_version=1`
- `status=planned_not_executed`
- `hardware_status=not_new_hardware_result`
- `experiment_executed=false`
- `device_write_allowed=false`
- `webserial_write_allowed=false`
- `external_source_promoted_to_authority=false`

## Checker output

`tools/check_glyph_external_remapper_compatibility_experiment_plan.py` prints:

- `glyph_external_remapper_compatibility_experiment_plan`
- `status=PASS` or `status=FAIL`
- `experiment_executed=false`
- `device_write_allowed=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the docs/fixture remain
`planned_not_executed`, no live device, no WebSerial write, not device write
behavior, not official compatibility, and not hardware validation.
