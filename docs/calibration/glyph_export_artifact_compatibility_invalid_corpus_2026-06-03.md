# Glyph Export Artifact Compatibility Invalid Corpus - 2026-06-03

## Scope

This document defines a negative compatibility corpus for the current
docs/tools-only Glyph export artifact bundle.

It is a docs/tools-only corpus. It is not firmware source, not runtime-loaded config, not serial/device write behavior, not hardware validation, and not nunchuk hardware validation.

## Source authority

The corpus derives from the currently committed export artifact bundle and its
existing docs/tools validators:

- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_runtime_config_validation_report_2026-06-03.json`
- `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt`
- `docs/calibration/fixtures/glyph_export_artifact_snapshots_2026-06-03.json`
- `tools/check_glyph_export_artifact_round_trip.py`
- `tools/check_glyph_export_artifact_snapshots.py`

The corpus does not change committed behavior fixtures or profile artifacts to
make checks pass. Every invalid case mutates an in-memory copy of the baseline
bundle only.

## Corpus shape

The machine-readable fixture is:

- `docs/calibration/fixtures/glyph_export_artifact_compatibility_invalid_corpus_2026-06-03.json`

Required top-level fields:

- `schema_name = glyph_export_artifact_compatibility_invalid_corpus`
- `corpus_version = 1`
- `status = negative_compatibility_corpus`
- `hardware_status = not_new_hardware_result`

Each case records:

- `case_id`
- `mutation`
- `target_artifact`
- `expected_error_codes`
- `payload`

The `payload` field stores declarative in-memory mutation operations against the
baseline bundle so the checker can exercise compatibility, round-trip, and
snapshot invariants without rewriting any committed artifacts.

## Invalid cases

The corpus covers these required negative scenarios:

- generated-config table drift against an unchanged runtime-candidate table
- runtime-candidate table drift against an unchanged generated-config table
- runtime-candidate role binding drift
- runtime-candidate hard override drift
- runtime-candidate priority reference drift
- runtime-candidate suppression rule drift
- Senscope export nested generated config drift
- validation report table count drift
- validation report missing caveat
- generated C++ table hash drift
- behavior cases count drift
- hardware-status validation claim
- nunchuk hardware-validated claim
- runtime-loaded config status claim
- serial/device write claim

## Validation intent

`tools/check_glyph_export_artifact_compatibility_invalid_corpus.py` loads the
baseline bundle, confirms the unmodified bundle passes its local compatibility
and round-trip invariants, applies each invalid mutation, and then confirms:

1. the mutated bundle fails;
2. the expected stable error code appears;
3. no invalid bundle passes as compatible.

The checker output is intentionally compact:

- `glyph_export_artifact_compatibility_invalid_corpus`
- `status=PASS` or `status=FAIL`
- `invalid_cases=<N>`
- `hardware_status=not_new_hardware_result`

## Non-goals

- No firmware source changes.
- No runtime-loaded config implementation.
- No serial/device write behavior.
- No hardware validation claim.
- No nunchuk hardware validation claim.
- No generated C++ integration into firmware.
- No behavior fixture or profile artifact mutation on disk.
