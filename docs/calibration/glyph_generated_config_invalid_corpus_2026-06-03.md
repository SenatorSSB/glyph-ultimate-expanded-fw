# Glyph Generated Config Invalid Corpus - 2026-06-03

## Scope

This document defines a negative test corpus for the offline generated-config validator.

It is a docs/tools-only corpus. It is not firmware, not runtime-loaded config, not serial/device write behavior, and not hardware validation.

## Source Authority

The corpus is derived from the current committed docs/tools prototype and validator source:

- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `tools/glyph_generated_config_validator.py`

The corpus does not introduce new firmware behavior and does not mutate the baseline generated-config fixture to make checks pass.

## Corpus Shape

The machine-readable fixture is:

- `docs/calibration/fixtures/glyph_generated_config_invalid_corpus_2026-06-03.json`

Required top-level fields:

- `schema_name = glyph_generated_config_invalid_corpus`
- `corpus_version = 1`
- `status = negative_validator_corpus`
- `hardware_status = not_new_hardware_result`

Each case records:

- `case_id`
- `mutation`
- `expected_error_codes`
- `payload`

The `payload` field stores explicit JSON patch-style mutation operations against the current valid baseline fixture. This keeps the corpus small and machine-readable without copying the full prototype payload into every case.

## Validation Intent

The corpus checks that the baseline generated-config fixture still passes the current offline validator, then applies each invalid mutation and confirms:

1. the mutated payload fails;
2. at least one expected validator issue code is produced;
3. unsafe or malformed payload content is rejected.

## Non-Goals

- No firmware source changes.
- No runtime-loaded config implementation.
- No hardware validation claim.
- No serial/device write behavior.
- No profile artifact mutation.
