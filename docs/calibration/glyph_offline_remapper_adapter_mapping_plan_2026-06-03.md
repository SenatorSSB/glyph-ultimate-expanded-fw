# Glyph Offline Remapper Adapter Mapping Plan - 2026-06-03

## Purpose and scope

This document records a mapping plan only for repo-owned artifacts that could
later feed a future external-remapper-compatible JSON candidate.

The plan status is:

- `offline_adapter_plan_only`

This is mapping plan only. The adapter not implemented, external source not
authority, not official configurator compatibility, no device write fields, no
WebSerial transport, not protobuf binary generation, not runtime-loaded
config, and not hardware validation.

Boundary reminder: no WebSerial transport.

No external source code was copied into this repo. No external dependency was
added. This branch does not generate the future JSON candidate, does not add an
adapter implementation, and does not approve any transport or hardware work.

## Source-backed inputs

The mapping plan is bounded to already committed repo artifacts:

- `docs/calibration/glyph_offline_remapper_adapter_target_contract_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_adapter_target_contract_2026-06-03.json`
- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_runtime_config_validation_report_2026-06-03.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_config_json_compatibility_cases_2026-06-03.json`
- `docs/calibration/fixtures/glyph_protobuf_config_schema_research_packet_2026-06-03.json`
- `docs/calibration/fixtures/glyph_webserial_transport_blocker_packet_2026-06-03.json`

Non-authoritative external comparison notes may inform future target-field
names, but they do not become firmware source authority, official configurator
compatibility authority, device-write authority, WebSerial authority, or
protobuf/schema authority.

## Mapping status meanings

- `direct_candidate`: repo-owned source field can map directly into a future
  candidate field without adding transport/runtime claims.
- `derived_candidate`: repo-owned source field can inform a future candidate
  field or sidecar after a bounded transform.
- `manual_review_required`: repo-owned source field exists, but the future
  target field needs explicit review before being treated as a stable mapping.
- `blocked_missing_source_authority`: a future target field is blocked because
  required source authority is still missing.
- `out_of_scope`: the target field is deliberately excluded from this plan.

## Mapping summary

The machine-readable fixture is the detailed source of truth for
`source_artifact`, `source_path_or_field`, `future_target_field`,
`mapping_status`, `authority_class`, and notes. Summary:

| Category | Future target field | Status | Notes |
| --- | --- | --- | --- |
| profile identity/name metadata | `profiles[].profileIdentity` | `manual_review_required` | Placeholder profile ID exists, but a committed top-level profile display name is not source-backed in the active profile artifact. |
| mode/backend metadata | `profiles[].modes[]` | `direct_candidate` | Mode IDs, mode names, applicable backends, and backend defaults exist in the active profile artifact. |
| button remapping entries | `profiles[].modes[].buttonRemapping[]` | `direct_candidate` | `physicalButton` and `activates` are already list-shaped in committed profile JSON. |
| explicit disabled button entries | `profiles[].modes[].disabledButtons[]` | `derived_candidate` | Repo checker guards physical-button-only disable-entry shape when present, but committed disable serialization still needs review. |
| SOCD pairs | `profiles[].modes[].socdPairs[]` | `direct_candidate` | Pair/button/type triples are source-backed in the active profile artifact. |
| RGB config references | `profiles[].modes[].rgbConfigRef` | `derived_candidate` | Internal `rgbConfig` references and brightness are source-backed, but future target index semantics still need review. |
| RGB button colors | `profiles[].rgbConfigs[]` | `direct_candidate` | Per-button colors and animation values are source-backed in committed profile JSON. |
| menu button icon/display metadata | `profiles[].modes[].displayMetadata` | `manual_review_required` | `menuButtonIcon` and `defaultDashboardOption` exist internally, but future target wiring is not source-audited. |
| keyboard mode metadata | `profiles[].keyboardModes[]` | `direct_candidate` | Keyboard mode references and button-to-keycode mappings are source-backed. |
| custom modifier metadata | `profiles[].modes[].customModifiers[]` | `blocked_missing_source_authority` | custom modifier representation requires source audit before any future target shape can be treated as stable. |
| generated config tables | `profiles[].modes[].generatedConfigTables` | `manual_review_required` | Generated config tables are not direct to an external remapper candidate until custom modifier representation is source-audited. |
| validation report | `sidecar.validationReport` | `derived_candidate` | Validation status belongs in a sidecar/report, not a device config field. |
| source authority / caveats | `sidecar.sourceAuthority` | `derived_candidate` | Authority boundaries and caveats belong in a sidecar/report, not a device config field. |
| non-goals | `sidecar.nonGoals` | `derived_candidate` | Non-goals belong in a sidecar/report, not a device config field. |
| protobuf binary payload | `transport.protobufBinary` | `blocked_missing_source_authority` | Official protobuf/schema authority is still missing. |
| WebSerial/device write fields | `transport.webserialDeviceWrite` | `out_of_scope` | Transport, Save to Device, and device write fields stay out of scope in this plan. |

## Sidecar outputs

Allowed future sidecar/report outputs in this plan:

- `sidecar.validationReport`
- `sidecar.sourceAuthority`
- `sidecar.nonGoals`

These stay offline plan artifacts only. They do not imply device config fields,
runtime-loaded config support, device write behavior, or hardware validation.

## Blocked and out-of-scope targets

- custom modifier representation requires source audit.
- Generated config tables are not direct to the future external-remapper
  candidate until custom modifier representation is source-audited.
- Protobuf binary payload mapping remains
  `blocked_missing_source_authority`.
- WebSerial/device write fields remain `out_of_scope`.

## Non-goals

- adapter implementation
- official configurator compatibility claim
- device write behavior
- WebSerial transport
- protobuf binary generation
- runtime-loaded config
- hardware validation
- external source promotion to authority

## Checker output

`tools/check_glyph_offline_remapper_adapter_mapping_plan.py` prints:

- `glyph_offline_remapper_adapter_mapping_plan`
- `status=PASS` or `status=FAIL`
- `mappings=<N>`
- `adapter_implemented=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the fixture and document preserve the
mapping-plan-only boundary, keep the adapter not implemented, keep external
source non-authoritative, keep no device write fields and no WebSerial
transport in scope, keep protobuf binary generation blocked, keep custom
modifier representation source-audit dependent, and do not claim hardware
validation.
