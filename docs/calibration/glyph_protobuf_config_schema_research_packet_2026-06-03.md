# Glyph Protobuf Config Schema Research Packet - 2026-06-03

## Purpose and scope

This document records a docs/tools-only research packet for protobuf/config
schema compatibility questions around the current Glyph export-adjacent
artifacts.

It is based only on repo-internal fixtures/docs/tools evidence and
non-authoritative external observation packets already committed in this repo.
It is not firmware source, not runtime-loaded config, not protobuf binary
generation, not official configurator compatibility, not device write behavior,
and not hardware validation.

External observations non-authoritative. They are comparison inputs only and are
not promoted to firmware source authority, official configurator compatibility
authority, protobuf/schema authority, WebSerial authority, or device-write
authority.

The central packet conclusion is unchanged throughout this branch:

- official protobuf/schema source authority missing
- official configurator compatibility source authority missing
- protobuf binary generation not implemented
- official configurator compatibility not claimed
- device write not implemented

## Repo-internal shape packet

### active_profile_artifact_json_shape

Repo-committed profile/config JSON evidence exists in:

- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- `docs/calibration/glyph_config_json_compatibility_fixtures_2026-06-03.md`
- `tools/check_glyph_config_json_compatibility_fixtures.py`

Current repo evidence shows an active profile artifact JSON with top-level
`gameModeConfigs`, `communicationBackendConfigs`, `keyboardModes`,
`rgbConfigs`, `defaultBackendConfig`, `defaultUsbBackendConfig`,
`rgbBrightness`, and `defaultDashboardOption`.

This is repo fixture evidence for offline docs/tools validation only. It is not
official configurator compatibility.

### generated_config_runtime_candidate_shape

Current docs/tools-only generated config and runtime candidate evidence exists
in:

- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/glyph_runtime_config_candidate_validator_v0_2026-06-03.md`

The generated-config prototype carries review-oriented shape such as
`coverage_metadata`, `priority_model`, `hard_overrides`, `role_bindings`, and
table metadata. The runtime candidate sample adds `schema_name`,
`candidate_version`, `source_authority`, validator-contract references, and
candidate table payloads.

These are candidate/review artifacts only. They are not runtime-loaded config.

### senscope_export_package_shape

Current future-package boundary evidence exists in:

- `docs/calibration/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.md`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `tools/check_glyph_senscope_export_package_validator.py`

The sample export package shape includes:

- `schema_name`
- `package_version`
- `neutral_senscope_profile`
- `glyph_generated_config_prototype`
- `table_source_metadata`
- `role_binding_metadata`
- `validation_report`
- hardware/nunchuk caveats

This is a sample/docs-only package boundary. It is not official configurator
compatibility and not protobuf binary generation.

### serial_dry_run_behavior

Current repo-local serial tooling boundaries are documented in:

- `docs/calibration/glyph_serial_active_config_writer_trace_2026-05-27.md`
- `tools/check_glyph_serial_config_writer.py`
- `tools/glyph_serial_config_tool.py`

Current repo docs/tools evidence says:

- default mode is dry-run/read-only
- explicit `--write` is required for live write
- explicit `--read` is required for live read
- explicit `--port` is required for live device access
- explicit `--artifact` is required for dry-run encode/write
- JSON artifact is not the wire format
- no firmware flashing is allowed

This packet does not add device write behavior. It only records the existing
repo-local dry-run boundary and write gating language.

### repo_internal_protobuf_config_assumptions

Current repo-internal protobuf/config boundary notes exist in:

- `docs/calibration/glyph_storage_transport_source_authority_registry_2026-06-03.md`
- `docs/calibration/glyph_configurator_compatibility_source_registry_2026-06-03.md`
- `docs/calibration/glyph_serial_active_config_writer_trace_2026-05-27.md`

Those docs record only bounded internal assumptions:

- later config transfer work would need protobuf-shaped `Config` bytes
- serial/config transport authority is still separated from fixture evidence
- official protobuf/schema source authority missing
- official configurator compatibility source authority missing

These assumptions are docs/tools boundary notes only. They are not official
protobuf/schema authority and not protobuf binary generation.

## External non-authoritative observations

External comparison inputs already captured in this repo include:

- `docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md`
- `docs/calibration/glyph_external_remapper_adapter_boundary_2026-06-03.md`
- `docs/calibration/glyph_external_remapper_config_shape_matrix_2026-06-03.md`

Observed external claims include:

- README/docs describe `configToBinary`, `binaryToConfig`, protobuf.js, and an
  inline `PROTO_DEF`
- README/docs describe Connect, Load Config, Save to Device, and WebSerial
  load/save flow
- README/app claims compatibility scope beyond the repo's current internal
  fixtures

External observations non-authoritative. They do not establish official
protobuf/schema source authority, official configurator compatibility, device
write behavior, WebSerial packet framing, runtime-loaded config, or hardware
validation.

## Missing authority

Implementation authority remains missing for:

- official protobuf/schema source
- official configurator compatibility source
- official WebSerial packet-framing source
- official device-write transport source
- official runtime-loaded config storage/interpreter source

Without those sources, this repo must stop at docs/tools research packets and
explicit non-claims.

## Blocked implementation classes

This packet keeps these implementation classes blocked:

- protobuf binary generation
- device write
- WebSerial transport
- runtime-loaded config
- official configurator compatibility claims

## Checker ownership

`tools/check_glyph_protobuf_config_schema_research_packet.py` validates the
packet fixture, repo-path references, non-authoritative external observations,
required missing-authority entries, blocked implementation classes, and required
doc caveat phrases.

Checker output lines:

- `glyph_protobuf_config_schema_research_packet`
- `status=PASS` or `status=FAIL`
- `known_repo_internal_shapes=<N>`
- `official_protobuf_schema_authority_present=false`
- `hardware_status=not_new_hardware_result`

Passing the checker confirms only that this packet preserves the intended
docs/tools-only research boundary. It is not protobuf binary generation, not
official configurator compatibility, not device write behavior, and not
hardware validation.
