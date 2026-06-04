# Glyph Storage Transport Source Authority Registry - 2026-06-03

## Purpose and scope

This document records a docs/tools-only source-authority registry for every
known input category relevant to Glyph storage, transport, config JSON,
protobuf, WebSerial, device write, active profile artifacts, runtime-loaded
config, fallback policy, migration policy, latency/performance evidence, and
external remapper observations.

It is not device write behavior, not WebSerial implementation, not
runtime-loaded config, not official configurator compatibility, and not hardware
validation.

External observations non-authoritative. They are recorded only as comparison
inputs and are not promoted to firmware source authority, official configurator
compatibility authority, WebSerial packet-framing authority, device-write
authority, runtime-loaded config authority, protobuf authority, or hardware
validation.

## Authority classes

Allowed authority classes in the fixture are:

- `repo_source_authority`
- `repo_fixture_evidence`
- `external_non_authoritative_observation`
- `official_source_authority_missing`
- `user_hardware_result`
- `blocked_pending_approval`

These classes are classification labels for the registry. They do not approve
implementation work.

## Category registry

### config_json_shape

- Authority class: `repo_fixture_evidence`
- Current status: repo-committed profile/config JSON fixtures and compatibility
  checkers exist for offline docs/tools validation only.
- Known sources:
  - `docs/calibration/glyph_config_json_compatibility_fixtures_2026-06-03.md`
  - `docs/calibration/fixtures/glyph_config_json_compatibility_cases_2026-06-03.json`
  - `tools/check_glyph_config_json_compatibility_fixtures.py`
  - `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- Missing sources:
  - official source authority for exact configurator JSON compatibility
  - reviewed export corpus covering official configurator import/export
- Implementation allowed: `false`
- Required before implementation:
  - official source authority for the exact supported JSON shape
  - user approval for any adapter or schema-affecting work
- Notes: Repo fixtures are useful evidence for offline compatibility checks, but
  they are not official configurator compatibility.

### protobuf_schema

- Authority class: `official_source_authority_missing`
- Current status: no repo-authoritative official protobuf/schema source has been
  inspected for implementation.
- Known sources:
  - `docs/calibration/glyph_configurator_compatibility_source_registry_2026-06-03.md`
  - `docs/calibration/fixtures/glyph_configurator_compatibility_source_registry_2026-06-03.json`
- Missing sources:
  - official source authority for protobuf schema
  - legal/source-review approval for using any external schema observation
- Implementation allowed: `false`
- Required before implementation:
  - official protobuf/schema source authority
  - explicit user approval
- Notes: External protobuf observations remain non-authoritative.

### protobuf_encode_decode

- Authority class: `official_source_authority_missing`
- Current status: no repo-authoritative encode/decode implementation source is
  approved for implementation.
- Known sources:
  - `docs/calibration/glyph_configurator_compatibility_source_registry_2026-06-03.md`
  - `docs/calibration/glyph_external_remapper_config_shape_matrix_2026-06-03.md`
- Missing sources:
  - official source authority for protobuf encode/decode behavior
  - source-audited compatibility evidence
- Implementation allowed: `false`
- Required before implementation:
  - official encode/decode source authority
  - explicit user approval
- Notes: This registry does not generate protobuf binaries.

### webserial_packet_framing

- Authority class: `official_source_authority_missing`
- Current status: no repo-authoritative WebSerial packet-framing source has been
  inspected.
- Known sources:
  - `docs/calibration/glyph_configurator_compatibility_source_registry_2026-06-03.md`
  - `docs/calibration/glyph_external_remapper_adapter_boundary_2026-06-03.md`
  - `docs/calibration/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.md`
- Missing sources:
  - official source authority for WebSerial packet framing
  - device transport protocol source authority
- Implementation allowed: `false`
- Required before implementation:
  - official packet-framing source authority
  - explicit user approval for transport work
- Notes: This is not WebSerial implementation.

### device_write_path

- Authority class: `official_source_authority_missing`
- Current status: serial/device write remains outside approved implementation
  scope.
- Known sources:
  - `docs/calibration/glyph_import_export_compatibility_validator_2026-06-03.md`
  - `docs/calibration/glyph_serial_active_config_writer_trace_2026-05-27.md`
  - `tools/check_glyph_serial_config_writer.py`
- Missing sources:
  - official source authority for device-write transport
  - explicit approval for any write-capable path
  - hardware validation plan and result requirements
- Implementation allowed: `false`
- Required before implementation:
  - official device-write source authority
  - explicit user approval
  - hardware validation plan
- Notes: This registry does not add Save to Device, push-to-device, flashing, or
  any write behavior.

### active_profile_artifact_path

- Authority class: `repo_fixture_evidence`
- Current status: committed active profile artifact paths are fixture evidence
  for offline checks.
- Known sources:
  - `docs/calibration/glyph_active_ultimate_lt3_config_artifact_2026-05-27.md`
  - `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
  - `tools/check_glyph_active_ultimate_lt3_config_artifact.py`
- Missing sources:
  - official source authority for how active profile artifacts are selected,
    persisted, or loaded by an official configurator/device workflow
- Implementation allowed: `false`
- Required before implementation:
  - official source authority for active-profile artifact handling
  - explicit user approval for any adapter behavior
- Notes: The active profile artifact is not runtime-loaded config.

### runtime_loaded_config_storage

- Authority class: `official_source_authority_missing`
- Current status: runtime-loaded config storage remains design-only and
  unimplemented.
- Known sources:
  - `docs/calibration/glyph_runtime_loaded_config_design_v0_2026-05-28.md`
  - `docs/calibration/fixtures/glyph_runtime_loaded_config_design_v0_2026-05-28.json`
  - `tools/check_glyph_runtime_loaded_config_design.py`
- Missing sources:
  - official source authority for runtime-loaded config storage
  - explicit implementation approval
  - fallback and migration policy authority
- Implementation allowed: `false`
- Required before implementation:
  - official storage source authority
  - approved design resolution
  - explicit user approval
- Notes: This is not runtime-loaded config.

### runtime_loaded_config_interpreter

- Authority class: `official_source_authority_missing`
- Current status: runtime-loaded config interpreter behavior remains unapproved
  and unimplemented.
- Known sources:
  - `docs/calibration/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.md`
  - `docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json`
  - `docs/calibration/glyph_runtime_config_candidate_validator_v0_2026-06-03.md`
- Missing sources:
  - official source authority for runtime-loaded config interpreter behavior
  - explicit implementation approval
  - hardware validation plan
- Implementation allowed: `false`
- Required before implementation:
  - official interpreter source authority
  - approved validator/interpreter design
  - explicit user approval
- Notes: Offline candidate validation is not firmware interpretation.

### fallback_policy

- Authority class: `blocked_pending_approval`
- Current status: fallback policy for invalid, missing, incompatible, or failed
  runtime-loaded config is unresolved.
- Known sources:
  - `docs/calibration/glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.md`
  - `docs/calibration/fixtures/glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.json`
  - `docs/calibration/glyph_preimplementation_go_nogo_index_2026-05-28.md`
- Missing sources:
  - official source authority for fallback behavior
  - user-approved fallback decision
  - test and hardware-validation plan
- Implementation allowed: `false`
- Required before implementation:
  - source-backed fallback policy
  - explicit user approval
  - validation and rollback plan
- Notes: This registry does not choose a fallback behavior.

### version_migration_policy

- Authority class: `official_source_authority_missing`
- Current status: version migration policy is unresolved for runtime-loaded
  config or transport payloads.
- Known sources:
  - `docs/calibration/glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.md`
  - `docs/calibration/fixtures/glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.json`
- Missing sources:
  - official source authority for version migration behavior
  - approved schema/version compatibility policy
  - rollback and rejection requirements
- Implementation allowed: `false`
- Required before implementation:
  - source-backed migration policy
  - explicit user approval
  - invalid-corpus coverage for migration/rejection cases
- Notes: This registry does not change any schema or migration behavior.

### latency_performance_evidence

- Authority class: `user_hardware_result`
- Current status: no new hardware result or latency/performance evidence is
  recorded by this branch.
- Known sources:
  - `docs/calibration/glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.md`
  - `docs/calibration/fixtures/glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.json`
- Missing sources:
  - official source authority for latency/performance requirements
  - user hardware result for any implementation branch
  - benchmark/test protocol for storage, transport, and runtime-loaded config
- Implementation allowed: `false`
- Required before implementation:
  - accepted performance requirements
  - approved measurement protocol
  - user hardware result after implementation
- Notes: This registry is not hardware validation and records no latency claim.

### external_remapper_observations

- Authority class: `external_non_authoritative_observation`
- Current status: external Open Glyph Remapper observations exist only as
  non-authoritative comparison inputs.
- Known sources:
  - `docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md`
  - `docs/calibration/fixtures/glyph_external_remapper_source_snapshot_index_2026-06-03.json`
  - `docs/calibration/glyph_external_remapper_config_shape_matrix_2026-06-03.md`
  - `docs/calibration/fixtures/glyph_external_remapper_config_shape_matrix_2026-06-03.json`
- Missing sources:
  - official source authority for configurator compatibility
  - approved source audit and license review before any adapter work
- Implementation allowed: `false`
- Required before implementation:
  - official source authority or explicit approved source-audit scope
  - user approval for any integration path
- Notes: External observations non-authoritative and not promoted to authority.

## Required fixture fields

The fixture for this registry must preserve these top-level fields:

- `schema_name=glyph_storage_transport_source_authority_registry`
- `registry_version=1`
- `status=docs_tools_source_authority_registry`
- `hardware_status=not_new_hardware_result`
- `device_write_implemented=false`
- `webserial_transport_implemented=false`
- `runtime_loaded_config_implemented=false`
- `external_source_promoted_to_authority=false`

## Caveats

- not device write behavior
- not WebSerial implementation
- not runtime-loaded config
- not official configurator compatibility
- external observations non-authoritative
- not hardware validation

## Checker output

`tools/check_glyph_storage_transport_source_authority_registry.py` prints:

- `glyph_storage_transport_source_authority_registry`
- `status=PASS` or `status=FAIL`
- `categories=<N>`
- `device_write_implemented=false`
- `runtime_loaded_config_implemented=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the docs/fixture registry preserves the
required source-authority boundaries. It does not implement storage, transport,
WebSerial, serial/device write behavior, protobuf binary generation,
runtime-loaded config, hardware validation, or official configurator
compatibility.
