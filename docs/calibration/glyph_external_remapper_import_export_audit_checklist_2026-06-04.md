# Glyph External Remapper Import/Export Audit Checklist - 2026-06-04

## Purpose and scope

This document records a docs/tools/fixtures-only checklist for a future
external remapper import/export source audit.

Checklist status is `planned_not_executed`.

This checklist does not execute the audit. `audit_executed=false`.
`hardware_status=not_new_hardware_result`.

This checklist does not promote external source to authority.

This checklist does not copy external source code into this repository.

This checklist does not claim official configurator compatibility.

This checklist does not claim hardware validation.

## Required item fields

Every checklist item must preserve:

- `status=planned_not_executed`
- `must_not_copy_code=true`
- `must_not_promote_authority=true`

## Checklist items

| item_id | category | requires_source_file | result_placeholder |
| --- | --- | --- | --- |
| `locate_import_handler` | locate import handler | `true` | Record the exact import entrypoint file(s), function(s), and unresolved gaps after source inspection. |
| `locate_export_handler` | locate export handler | `true` | Record the exact export entrypoint file(s), function(s), and unresolved gaps after source inspection. |
| `identify_json_parse_serialize_behavior` | identify JSON parse/serialize behavior | `true` | Record parse/serialize library usage, strictness, defaults, and unknowns from inspected source. |
| `identify_normalization_sanitization_behavior` | identify normalization/sanitization behavior | `true` | Record normalization, sanitization, coercion, and validation behavior from inspected source. |
| `trace_button_remapping_import_export` | trace buttonRemapping import/export | `true` | Record how `buttonRemapping` is parsed, normalized, serialized, preserved, or dropped. |
| `trace_activates_preservation_or_stripping` | trace activates preservation or stripping | `true` | Record whether `activates` data is preserved, transformed, stripped, or unsupported. |
| `trace_socd_pair_import_export` | trace SOCD pair import/export | `true` | Record how SOCD pair structures are parsed, normalized, serialized, and whether drift occurs. |
| `trace_rgb_config_import_export` | trace RGB config import/export | `true` | Record how RGB config data is parsed, normalized, serialized, preserved, or stripped. |
| `trace_menu_icon_default_metadata_handling` | trace menu icon/default metadata handling | `true` | Record how menu icon and default metadata are imported, serialized, preserved, or stripped. |
| `trace_protobuf_encode_decode_boundaries` | trace protobuf encode/decode boundaries | `true` | Record protobuf-related source boundaries, message names, and unknowns without copying code. |
| `trace_webserial_load_save_boundaries` | trace WebSerial load/save boundaries | `true` | Record WebSerial load/save entrypoints, transport boundaries, and unresolved gaps. |
| `trace_custom_profile_modifier_representation` | trace custom profile/modifier representation | `true` | Record how custom profile or modifier structures are represented and where fidelity limits appear. |
| `identify_tests_if_any` | identify tests, if any | `true` | Record exact test files, test scopes, or note that no relevant tests were found. |
| `record_exact_commit_audited` | record exact commit audited | `false` | Record the exact external commit, tag, or immutable revision audited, or state unknown. |
| `record_files_inspected` | record files inspected | `true` | Record the exact file paths, URLs, or UI surfaces inspected during the audit. |
| `record_non_authority_caveat` | record non-authority caveat | `false` | Record that external observations remain non-authoritative unless explicitly promoted later. |
| `record_no_code_copy_caveat` | record no-code-copy caveat | `false` | Record that no external source code is copied into this repository as audit evidence. |

## Source inputs

This checklist is bounded to already committed docs/tools/fixtures:

- `docs/calibration/glyph_external_remapper_import_export_audit_scope_2026-06-04.md`
- `docs/calibration/fixtures/glyph_external_remapper_import_export_audit_scope_2026-06-04.json`
- `docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_source_snapshot_index_2026-06-03.json`
- `docs/calibration/glyph_storage_transport_source_authority_registry_2026-06-03.md`
- `docs/calibration/fixtures/glyph_storage_transport_source_authority_registry_2026-06-03.json`
- `docs/calibration/glyph_protobuf_config_schema_research_packet_2026-06-03.md`
- `docs/calibration/fixtures/glyph_protobuf_config_schema_research_packet_2026-06-03.json`
- `docs/calibration/glyph_webserial_transport_blocker_packet_2026-06-03.md`
- `docs/calibration/fixtures/glyph_webserial_transport_blocker_packet_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.json`

## Required fixture fields

The fixture for this checklist must preserve these top-level fields:

- `schema_name=glyph_external_remapper_import_export_audit_checklist`
- `checklist_version=1`
- `status=planned_not_executed`
- `audit_executed=false`
- `hardware_status=not_new_hardware_result`
- `external_source_promoted_to_authority=false`
- `code_copied_into_repo=false`

## Checker output

`tools/check_glyph_external_remapper_import_export_audit_checklist.py` prints:

- `glyph_external_remapper_import_export_audit_checklist`
- `status=PASS` or `status=FAIL`
- `checklist_items=<N>`
- `audit_executed=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the docs/fixture remain
`planned_not_executed`, `audit_executed=false`,
`hardware_status=not_new_hardware_result`, the stable checklist item set is
present, external source is not promoted to authority, and no external source
code is copied into this repository.
