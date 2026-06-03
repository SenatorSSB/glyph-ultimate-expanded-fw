# Glyph Senscope Export Package Validator Draft - 2026-06-03

## Scope

This document defines a draft validator only for a sample future Senscope-to-Glyph export package shape.

The validator is not Senscope app implementation, not firmware, not runtime-loaded config, not serial/device write behavior, and not hardware validation.

It does not implement device writing, serial transport, runtime-loaded config, firmware behavior changes, profile schema changes, macros, turbo behavior, timing automation, or nunchuk hardware validation.

## Files

- `tools/check_glyph_senscope_export_package_validator.py`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_senscope_export_package_invalid_corpus_2026-06-03.json`

## Source Authority

The validator is bounded by existing committed docs/tools contracts:

- `docs/calibration/fixtures/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json`
- `tools/glyph_generated_config_validator.py`

The nested `glyph_generated_config_prototype` payload is validated by the offline generated-config validator from Branch 1. This package validator adds package-level shape, caveat, validation-report, forbidden-scope, and negative-corpus checks.

## Sample Package Shape

The sample package is docs/tools-only and uses:

- `schema_name = glyph_senscope_export_package`
- `package_version = 1`
- `status = sample_docs_only_not_implemented`
- `hardware_status = not_new_hardware_result`
- `nunchuk_status = preserved_but_not_hardware_validated`

Required payload sections are inherited from the existing export contract draft:

- `neutral_senscope_profile`
- `glyph_generated_config_prototype`
- `table_source_metadata`
- `role_binding_metadata`
- `validation_report`
- `hardware_status_caveat`
- `nunchuk_status_caveat`

The `neutral_senscope_profile` section is a minimal placeholder. It explicitly states that the actual Senscope schema is deferred to Senscope and is not defined by this Glyph repository.

The package does not claim to be device-writeable.

## Validation Report

The validator requires the validation report sections listed by `glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json`:

- `source_authority`
- `table_count`
- `role_binding_summary`
- `priority_model_summary`
- `hard_override_summary`
- `behavior_case_coverage_summary`
- `no_forbidden_behavior_confirmation`
- `not_hardware_validation_caveat`
- `open_questions`

The report is a review artifact. It is not firmware, not runtime-loaded config, not serial/device write behavior, and not hardware validation.

## Forbidden Scope

The validator rejects package content that adds or claims:

- device write instructions
- serial transport payloads
- runtime-loaded config implementation
- firmware behavior changes
- profile schema changes
- macro/turbo/timing/history-dependent logic
- hardware validation without a hardware result
- nunchuk hardware validation

These rejections are package-level guardrails only. They do not implement firmware behavior or transport behavior.

## Invalid Corpus

The invalid corpus mutates the valid sample package and confirms the validator rejects:

- missing generated config
- generated config invalid
- missing validation report
- device write instruction included
- serial transport payload included
- runtime-loaded config implementation claim
- firmware behavior change claim
- profile schema change claim
- macro/turbo logic
- hardware validation claim without hardware result
- nunchuk hardware validation claim

## Checker Output

`tools/check_glyph_senscope_export_package_validator.py` prints:

- `glyph_senscope_export_package_validator`
- `status=PASS` or `status=FAIL`
- `sample_validated=true` or `sample_validated=false`
- `invalid_cases=<N>`
- `hardware_status=not_new_hardware_result`

## Non-Goals

- No Senscope browser app changes.
- No firmware runtime source changes.
- No generated C++ placed in firmware paths.
- No runtime-loaded config implementation.
- No serial/device write behavior.
- No push-to-device behavior.
- No hardware validation claim.
- No nunchuk hardware validation claim.
- No Senscope neutral profile schema definition or mutation.
