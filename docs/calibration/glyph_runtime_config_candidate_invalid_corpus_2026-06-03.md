# Glyph Runtime Config Candidate Invalid Corpus - 2026-06-03

## Scope

This document defines a negative test corpus for the offline Glyph runtime config candidate validator.

It is a docs/tools-only corpus. It is not firmware, not runtime-loaded config, not serial/device write behavior, not hardware validation, and not nunchuk hardware validation.

## Source Authority

The corpus is derived from the current committed docs/tools sample candidate and validator source:

- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `tools/glyph_runtime_config_candidate_validator.py`

The corpus does not introduce new firmware behavior and does not mutate the baseline sample candidate to make checks pass.

## Corpus Shape

The machine-readable fixture is:

- `docs/calibration/fixtures/glyph_runtime_config_candidate_invalid_corpus_2026-06-03.json`

Required top-level fields:

- `schema_name = glyph_runtime_config_candidate_invalid_corpus`
- `corpus_version = 1`
- `status = negative_validator_corpus`
- `hardware_status = not_new_hardware_result`

Each case records:

- `case_id`
- `mutation`
- `expected_error_codes`
- `payload`

The `payload` field stores explicit JSON patch-style mutation operations against the current valid baseline sample candidate. This keeps the corpus small and machine-readable without copying the full candidate payload into every case.

## Validation Intent

The checker loads the baseline sample candidate from the existing validator package, confirms the baseline passes, applies each invalid mutation, and confirms:

1. the mutated payload fails;
2. at least one expected validator issue code is produced;
3. malformed or unsafe payload content is rejected without implying runtime-loaded config, serial/device write behavior, or hardware validation support.

The current validator does not expose a role-specific rejection code. The `unknown_role_class` case therefore uses a bounded `role_class` metadata field and expects the validator's existing `E_UNKNOWN_ACCEPTED_DATA_CLASS` rejection path.

## Non-Goals

- No firmware source changes.
- No runtime-loaded config implementation.
- No serial/device write behavior.
- No hardware validation claim.
- No nunchuk hardware validation claim.
- No profile artifact mutation.
