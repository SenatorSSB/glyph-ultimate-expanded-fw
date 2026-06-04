# Glyph Clean-Room Adapter Invalid Corpus - 2026-06-04

## Purpose and scope

This records a docs/tools/fixtures-only invalid corpus for future clean-room adapter candidate schema validation.

Corpus status is `docs_tools_invalid_corpus`.

`schema_name = glyph_clean_room_adapter_invalid_corpus`

`corpus_version = 1`

This is planning fixture validation only.

There is no mutation application.

There is no adapter candidate generation.

The fixture covers every category from the clean-room adapter negative corpus contract.

This is not official compatibility.

This is not hardware validation.

## Source artifacts

Invalid corpus fixture:

- `docs/calibration/fixtures/glyph_clean_room_adapter_invalid_corpus_2026-06-04.json`

Checker:

- `tools/check_glyph_clean_room_adapter_invalid_corpus_fixture.py`
- `tools/check_glyph_clean_room_adapter_invalid_corpus.py`

Contract source:

- `tools/check_glyph_clean_room_adapter_negative_corpus_contract.py`
- `docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.json`

Candidate placeholder source:

- `tools/check_glyph_clean_room_adapter_candidate_schema_validator.py`
- `docs/calibration/fixtures/glyph_clean_room_adapter_candidate_SCHEMA_PLACEHOLDER_2026-06-04.json`

## Required top-level flags

- `adapter_implemented = false`
- `external_json_generated = false`
- `hardware_status = not_new_hardware_result`

## Per-case requirements

Every case in the fixture keeps these values:

- `must_fail = true`
- `must_not_generate_external_json = true`
- `must_not_claim_official_compatibility = true`
- `must_not_claim_hardware_validation = true`

## Coverage categories

Each metadata-only case maps directly to one committed contract category and required rejection basis:

- `missing_sidecar`: sidecar is required
- `missing_runtime_owned_behavior_warning`: runtime-owned behavior warning is required
- `missing_non_round_trip_warning`: non-round-trip warning is required
- `claims_round_trip_safe`: future candidate must not claim round-trip safe
- `claims_active_profile_round_trip_safe`: active profile round-trip remains unsafe
- `claims_runtime_owned_behavior_represented_by_external_profile_json`: runtime-owned behavior must not be represented directly by external profile JSON
- `adapter_implemented`: no adapter output exists
- `external_json_generated`: no external JSON generation exists
- `generated_external_json_output_path_present`: generated external JSON output path present
- `device_write_allowed`: device write allowed
- `webserial_allowed`: WebSerial allowed
- `protobuf_binary_generation_allowed`: protobuf binary generation allowed
- `runtime_loaded_config_allowed`: runtime-loaded config allowed
- `official_compatibility_claimed`: official compatibility claimed
- `hardware_validation_claimed`: hardware validation claimed
- `external_source_promoted_to_authority`: external source promoted to authority
- `copied_external_source_code`: copied external source code
- `external_dependency_added`: external dependency added
- `missing_source_authority_classification`: source-authority classification is required
- `missing_validation_report`: validation report is required
- `missing_loss_warnings`: loss warnings are required
- `binding_loss_warning_suppressed`: binding loss warning suppressed
- `socd_drift_warning_suppressed`: SOCD drift warning suppressed

## Non-goals and caveats

- no mutation application
- no adapter candidate generation
- does not execute an adapter
- no adapter implementation
- no external JSON generation
- no generated external JSON output path
- no external code reuse
- no external dependency
- no device write
- no WebSerial transport
- no protobuf binary generation
- no runtime-loaded config
- not official compatibility
- not hardware validation
- no active profile artifact change
- no exported experiment artifact change
- no runtime firmware source change
- no case can be interpreted as a valid adapter output

## Validation report

The checker validates that:

- The committed fixture exactly matches regenerated canonical JSON.
- The committed category list stays aligned with the negative corpus contract category set and order.
- Every case has the required metadata-only failure flags and expected error code list.
- Every case category is known and every required contract category is present.
- No case includes a generated external JSON path.
- No case can be interpreted as a valid adapter output relative to the committed placeholder/contract invariants.
- The corpus remains planning fixture validation only and does not execute an adapter.
- The corpus does not claim official compatibility or hardware validation.
- The Markdown includes the required invalid corpus phrases.
- The contract checker still passes before the invalid corpus fixture is accepted.
