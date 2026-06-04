# Glyph Offline Remapper Adapter Gap Matrix - 2026-06-03

## Purpose and scope

This document records a blocked-field gap matrix for repo-owned artifacts that
could later inform a future external-remapper-compatible JSON candidate.

The matrix status is:

- `offline_adapter_gap_matrix_only`

This is a blocked-field gap matrix only. There is no adapter generation, no
external code reuse, no device write behavior, no WebSerial transport, and not
hardware validation.

Boundary reminder: not hardware validation.

This branch does not add an adapter implementation, does not generate the
future JSON candidate, does not promote external observations to authority, and
does not approve protobuf binary generation, runtime-loaded config, Save to
Device behavior, or firmware flashing.

## Source-backed inputs

The gap matrix is bounded to already committed repo artifacts:

- `docs/calibration/glyph_external_remapper_adapter_boundary_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_adapter_boundary_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_source_snapshot_index_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_config_shape_matrix_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_config_shape_matrix_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_adapter_feasibility_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_adapter_feasibility_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_adapter_target_contract_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_adapter_target_contract_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.json`
- `docs/calibration/glyph_protobuf_config_schema_research_packet_2026-06-03.md`
- `docs/calibration/fixtures/glyph_protobuf_config_schema_research_packet_2026-06-03.json`
- `docs/calibration/glyph_webserial_transport_blocker_packet_2026-06-03.md`
- `docs/calibration/fixtures/glyph_webserial_transport_blocker_packet_2026-06-03.json`
- `docs/calibration/glyph_config_json_compatibility_fixtures_2026-06-03.md`
- `docs/calibration/fixtures/glyph_config_json_compatibility_cases_2026-06-03.json`
- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`

These sources support blocker classification and future evidence requirements
only. They do not establish official protobuf/schema authority, official
configurator compatibility authority, WebSerial packet framing authority,
device-write authority, hardware validation, or license clearance for reuse.

## Gap status meanings

- `blocked_missing_source_authority`: required authority is still missing.
- `blocked_pending_manual_experiment`: a future offline/manual experiment is
  still required before the field or behavior can be treated as safe to map.
- `blocked_pending_license_review`: legal review is required before any reuse
  claim or code-copy assumption.
- `allowed_as_sidecar_only`: future evidence may be recorded only in a sidecar
  report and must not become an adapter-generated config field.
- `out_of_scope`: deliberately excluded from adapter generation in this branch.

## Gap summary

The machine-readable fixture is the detailed source of truth for `gap_id`,
`status`, `risk`, `required_evidence`, `must_not_generate`, and notes.

| Gap | Status | Notes |
| --- | --- | --- |
| external custom modifier representation | `blocked_missing_source_authority` | Mapping plan already keeps custom modifier representation blocked until source audit. |
| official protobuf schema | `blocked_missing_source_authority` | Protobuf/schema authority is still missing in the research packet. |
| external protobuf encode/decode assumptions | `blocked_missing_source_authority` | External encode/decode observations remain non-authoritative comparison notes only. |
| WebSerial packet framing | `blocked_missing_source_authority` | WebSerial blocker packet records missing official packet framing authority. |
| Save to Device behavior | `out_of_scope` | Save to Device stays outside adapter generation in this branch. |
| official configurator JSON edge cases | `blocked_missing_source_authority` | Repo fixtures are bounded compatibility checks, not official edge-case authority. |
| RGB shared-index behavior | `blocked_pending_manual_experiment` | Internal RGB references exist, but shared-index import/export behavior is not proven. |
| menu button display-vs-runtime behavior | `blocked_pending_manual_experiment` | Display metadata exists internally, but runtime equivalence in an external candidate is not proven. |
| keyboard scancode mapping | `blocked_pending_manual_experiment` | Keyboard keycode fields exist internally, but external import/export acceptance is not proven. |
| SOCD semantic equivalence | `blocked_pending_manual_experiment` | SOCD pair shape exists, but semantic equivalence across an external adapter is not proven. |
| profile count/limits | `blocked_pending_manual_experiment` | Future profile-count limits need offline/manual evidence or official source authority. |
| external default config provenance | `allowed_as_sidecar_only` | Provenance notes may be recorded later, but must not become adapter-generated config fields. |
| external license/code reuse | `blocked_pending_license_review` | No external code reuse is allowed without license review. |
| import/export no-device experiment evidence | `allowed_as_sidecar_only` | Later no-device experiment evidence belongs in a sidecar result only and is not adapter generation. |

## Blocked-field matrix conclusions

- custom modifier representation remains blocked until source authority exists.
- official protobuf schema and external protobuf encode/decode assumptions
  remain blocked until source authority exists.
- WebSerial packet framing remains blocked and Save to Device behavior remains
  out of scope.
- official configurator JSON edge cases remain blocked until source authority
  exists.
- RGB shared-index behavior, menu-button display-vs-runtime behavior, keyboard
  scancode mapping, SOCD semantic equivalence, and profile count/limits remain
  blocked until future offline/manual experiment evidence exists.
- external default config provenance is allowed as sidecar only and must not be
  adapter-generated as config.
- external license/code reuse remains blocked pending license review, and
  external code copy must not be generated.
- import/export no-device experiment evidence is allowed as sidecar only and
  must not be adapter-generated as config.

## Non-goals

- adapter implementation
- device write behavior
- WebSerial transport
- Save to Device behavior
- protobuf binary generation
- runtime-loaded config
- hardware validation
- external source promotion to authority
- external code reuse

## Checker output

`tools/check_glyph_offline_remapper_adapter_gap_matrix.py` prints:

- `glyph_offline_remapper_adapter_gap_matrix`
- `status=PASS` or `status=FAIL`
- `gaps=<N>`
- `adapter_implemented=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the fixture and document preserve the
blocked-field gap matrix boundary, keep no adapter generation, keep no external
code reuse, keep no device write behavior, keep no WebSerial transport, and do
not claim hardware validation.
