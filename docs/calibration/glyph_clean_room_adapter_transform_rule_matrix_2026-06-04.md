# Glyph Clean-Room Adapter Transform Rule Matrix - 2026-06-04

## Purpose and scope

This records a docs/tools/fixtures-only transform rule matrix for a possible
future clean-room adapter candidate.

Matrix status is `transform_rule_matrix_only`.

Transform implementation does not exist.

External JSON generation does not exist.

The rules are planning-only and do not implement transform code.

The matrix does not authorize active profile artifact changes or exported
experiment artifact changes.

Runtime-owned behavior remains sidecar-only.

No device write/WebSerial/protobuf/runtime-loaded config.

This packet is not official configurator compatibility and not hardware validation.

## Source artifacts

Matrix fixture:

- `docs/calibration/fixtures/glyph_clean_room_adapter_transform_rule_matrix_2026-06-04.json`

Checker:

- `tools/check_glyph_clean_room_adapter_transform_rule_matrix.py`

Required source checkers:

- `tools/check_glyph_offline_remapper_adapter_mapping_plan.py`
- `tools/check_glyph_offline_remapper_adapter_gap_matrix.py`
- `tools/check_glyph_clean_room_adapter_transform_design_contract.py`
- `tools/check_glyph_clean_room_adapter_sidecar_contract.py`
- `tools/check_glyph_storage_transport_source_authority_registry.py`
- `tools/check_glyph_protobuf_config_schema_research_packet.py`
- `tools/check_glyph_webserial_transport_blocker_packet.py`
- `tools/check_glyph_runtime_storage_interpreter_blocker_packet.py`

## Allowed dispositions

Allowed dispositions are exactly:

- `candidate_direct_profile_field`
- `sidecar_only`
- `blocked_requires_source_authority`
- `blocked_round_trip_unsafe`
- `out_of_scope`

## Rule matrix

| Category | Disposition | Planning note |
| --- | --- | --- |
| profile name/identity metadata | `blocked_requires_source_authority` | The mapping plan keeps top-level profile identity/name derivation under review because the active profile artifact does not provide a source-backed display-name authority for a future external candidate. |
| mode/backend metadata | `candidate_direct_profile_field` | The active profile artifact already carries mode IDs, mode names, applicable backends, and backend defaults as committed profile-level metadata. |
| profile-level button remapping | `candidate_direct_profile_field` | The active profile artifact already carries list-shaped `buttonRemapping` entries keyed by `physicalButton`. |
| activates-bearing bindings | `blocked_round_trip_unsafe` | The experiment result and binding-loss classification keep `activates`-bearing bindings blocked because exported profile JSON stripped those bindings and active profile round-trip remains unsafe. |
| disabled/visibility entries | `blocked_round_trip_unsafe` | Explicit disable serialization is still review-only and must not be treated as round-trip safe transform output. |
| SOCD policy | `sidecar_only` | The SOCD drift classification and clean-room transform design keep SOCD policy in warning/sidecar scope instead of a direct clean-room profile-field claim. |
| RGB metadata | `blocked_round_trip_unsafe` | The gap matrix keeps RGB shared-index behavior review-only, so RGB metadata stays blocked from round-trip-safe transform treatment. |
| menu icon metadata | `blocked_requires_source_authority` | Menu icon and display wiring are not source-audited as stable clean-room target authority. |
| keyboard mode metadata | `candidate_direct_profile_field` | The active profile artifact exposes keyboard mode references and button-to-keycode mappings directly, while this matrix still makes no compatibility claim. |
| runtime-owned behavior | `sidecar_only` | Runtime-owned behavior remains outside external profile JSON and must stay in sidecar/report scope. |
| validation report | `sidecar_only` | Validation report content belongs in sidecar/report scope, not a transformed profile payload. |
| source-authority caveats | `sidecar_only` | Source-authority caveats belong in sidecar/report scope so authority boundaries stay explicit without becoming profile fields. |
| loss warnings | `sidecar_only` | Binding-loss and SOCD-drift warnings belong in sidecar/report scope before any future review of transform output. |
| external JSON output path | `out_of_scope` | No generated external JSON path exists on this branch, and transform planning does not add one. |
| WebSerial/device write fields | `out_of_scope` | Transport/write fields remain out of scope for this planning-only matrix. |
| protobuf binary payload | `out_of_scope` | Protobuf binary generation is blocked and is not part of transform-rule planning. |
| runtime-loaded config payload | `out_of_scope` | Runtime-loaded config remains blocked and is not part of transform-rule planning. |

## Notes

- This matrix classifies planning rules only.
- This matrix does not implement a clean-room adapter.
- This matrix does not implement transform code.
- This matrix does not generate external JSON.
- This matrix does not add a generated external JSON output path.
- This matrix does not add device write fields, WebSerial transport, protobuf
  binary generation, or runtime-loaded config.
- This matrix does not claim official configurator compatibility.
- This matrix does not claim hardware validation.

## Checker output

`tools/check_glyph_clean_room_adapter_transform_rule_matrix.py` prints:

- `glyph_clean_room_adapter_transform_rule_matrix`
- `status=PASS` or `status=FAIL`
- `rules=17`
- `transform_implemented=false`
- `external_json_generated=false`
- `hardware_status=not_new_hardware_result`
