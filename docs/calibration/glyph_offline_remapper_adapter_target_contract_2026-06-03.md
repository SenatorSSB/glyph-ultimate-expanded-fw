# Glyph Offline Remapper Adapter Target Contract - 2026-06-03

## Purpose and scope

This document records an offline adapter plan only target contract for a possible
future external-remapper-compatible JSON candidate.

The target status is:

- `offline_adapter_plan_only`

This is planning only. The adapter is not implemented, external source not
authority, this is not official configurator compatibility, not device write behavior, not WebSerial transport, not protobuf binary generation, not runtime-loaded config, and not hardware validation.

No external source code was copied into this repo. No external dependency was
added. This document does not generate an external-remapper-compatible JSON
candidate and does not approve a future adapter implementation.

## Target artifact

Future target artifact:

- external-remapper-compatible JSON candidate

The future target artifact is only a possible offline JSON candidate intended
for a no-device import/export experiment. It is not generated in this branch.
It is not a firmware input, not a runtime-loaded config, not a protobuf binary,
not an official configurator compatibility claim, and not device-writeable.

## Target authority

Target authority is limited to:

- non-authoritative external comparison
- repo fixtures

External observations may be used only as comparison notes. They do not become
firmware source authority, official configurator authority, device-write
authority, runtime-loaded config authority, WebSerial authority, protobuf
schema authority, or hardware validation evidence.

## Required future inputs

Any future adapter-target experiment must start from existing repo artifacts or
reviewed replacements for all of the following:

- Senscope export package sample:
  `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- runtime config candidate sample:
  `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- generated config prototype:
  `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- validation report:
  `docs/calibration/fixtures/glyph_runtime_config_validation_report_2026-06-03.json`
- active profile artifact:
  `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`

These are future comparison inputs only. They are not approval for adapter
implementation, external source authority, official configurator compatibility,
device write behavior, WebSerial transport, protobuf binary generation,
runtime-loaded config, or hardware validation.

## Future outputs

Allowed future outputs, if separately approved and produced later:

- JSON candidate intended for no-device import/export experiment only
- compatibility report

Both outputs are plan-only in this branch. No JSON candidate is generated here,
and no compatibility report from a real external-remapper import/export
experiment is claimed here.

## Required approvals

- user approval before generating an external-remapper-compatible JSON candidate
- user approval before running any no-device import/export experiment
- user approval before external dependency or source reuse
- user approval before adapter implementation
- user approval before device transport or WebSerial work
- user approval before protobuf/config/schema behavior changes
- user approval before runtime-loaded config implementation

## Forbidden interpretations

- adapter implemented
- official configurator compatibility claimed
- external source authority
- device write behavior
- WebSerial transport
- protobuf binary generation
- runtime-loaded config
- hardware validation
- firmware source change
- profile artifact change
- external source code copied
- external dependency added
- Senscope game-semantic source authority changed

## Checker output

`tools/check_glyph_offline_remapper_adapter_target_contract.py` prints:

- `glyph_offline_remapper_adapter_target_contract`
- `status=PASS` or `status=FAIL`
- `adapter_implemented=false`
- `external_source_promoted_to_authority=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the fixture and document preserve the
offline adapter plan only boundary, keep the adapter not implemented, keep
external source not authority, keep official configurator compatibility
unclaimed, keep device write behavior, WebSerial transport, protobuf binary
generation, and runtime-loaded config unimplemented, and do not claim hardware
validation.
