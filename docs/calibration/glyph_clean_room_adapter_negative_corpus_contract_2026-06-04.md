# Glyph Clean-Room Adapter Negative Corpus Contract - 2026-06-04

## Purpose and scope

This records a docs/tools/fixtures-only negative corpus contract for the future clean-room adapter candidate schema.

Contract status is `negative_corpus_contract_only`.

Target: future clean-room adapter candidate schema.

The corpus rejects unsafe candidate payloads.

No adapter output exists.

No external JSON generation exists.

Active profile round-trip remains unsafe.

Sidecar is required.

Runtime-owned behavior must not be represented directly by external profile JSON.

This is not an adapter implementation.

This is not external-remapper-compatible JSON generation.

This is not official compatibility.

This is not hardware validation.

No device write, WebSerial, protobuf binary generation, or runtime-loaded config is implemented.

## Source artifacts

Contract fixture:

- `docs/calibration/fixtures/glyph_clean_room_adapter_negative_corpus_contract_2026-06-04.json`

Checker:

- `tools/check_glyph_clean_room_adapter_negative_corpus_contract.py`

Upstream contract inputs:

- `tools/check_glyph_clean_room_adapter_candidate_schema_contract.py`
- `tools/check_glyph_clean_room_adapter_candidate_schema_validator.py`
- `tools/check_glyph_clean_room_adapter_sidecar_contract.py`
- `tools/check_glyph_clean_room_adapter_schema_readiness_gate.py`
- `tools/check_glyph_offline_remapper_export_loss_gate.py`

## Required flags

- `adapter_implemented=false`
- `external_json_generated=false`
- `hardware_status=not_new_hardware_result`

## Invalid case categories

The negative corpus contract requires future candidate-schema validation to reject these unsafe candidate payload categories:

- missing sidecar
- missing runtime-owned behavior warning
- missing non-round-trip warning
- claims round-trip safe
- claims active profile round-trip safe
- claims runtime-owned behavior represented by external profile JSON
- adapter implemented
- external JSON generated
- generated external JSON output path present
- device write allowed
- WebSerial allowed
- protobuf binary generation allowed
- runtime-loaded config allowed
- official compatibility claimed
- hardware validation claimed
- external source promoted to authority
- copied external source code
- external dependency added
- missing source-authority classification
- missing validation report
- missing loss warnings
- binding loss warning suppressed
- SOCD drift warning suppressed

## Required rejection basis

- Sidecar is required for future candidate review.
- Runtime-owned behavior warning is required because external profile JSON cannot directly represent runtime-owned behavior.
- Non-round-trip warning is required because active profile round-trip remains unsafe.
- Loss warnings are required, including binding-loss and SOCD-drift warnings.
- Source-authority classification is required for every future candidate payload.
- Validation report is required for every future candidate payload.

## Forbidden claims and capabilities

- no adapter implementation
- no adapter output exists
- no external JSON generation exists
- no generated external JSON output path
- no active profile artifact change
- no exported experiment artifact change
- no runtime firmware source change
- no source-authority promotion
- no external code reuse
- no external dependency
- no device write
- no serial/device write behavior
- no WebSerial transport
- no protobuf binary generation
- no runtime-loaded config
- not official compatibility
- not hardware validation

## Source-authority classification

- Repo docs, fixtures, and checker outputs are the only authority for this negative corpus contract.
- External remapper export is non-authoritative.
- External source was not promoted to authority.
- No external source code was copied.
- No external dependency was added.

## Validation report

The checker validates that:

- The committed fixture exactly matches regenerated canonical JSON.
- The Markdown includes the required negative corpus phrases.
- Upstream clean-room and export-loss checkers still pass.
- Invalid case category count remains stable.
- Adapter implementation remains false.
- External JSON generation remains false.
- Hardware status remains `not_new_hardware_result`.
