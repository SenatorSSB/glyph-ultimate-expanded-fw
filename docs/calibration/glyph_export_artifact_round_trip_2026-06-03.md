# Glyph Export Artifact Round Trip - 2026-06-03

## Purpose and scope

This document records an offline round-trip only checker for the current Glyph
generated-config prototype, runtime-candidate sample, Senscope export package
sample, and runtime validation report fixture.

It is not firmware source, not runtime-loaded config, not serial/device write
behavior, not hardware validation, and not nunchuk hardware validation.

## Checked artifacts

`tools/check_glyph_export_artifact_round_trip.py` checks these committed
artifacts:

- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_runtime_config_validation_report_2026-06-03.json`
- `tools/check_glyph_identity_runtime_generated_config_evaluator_input.py`
- `tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py`

The checker also imports the current generated-config, runtime-candidate, and
Senscope export package validators directly where that is simpler and still
deterministic.

## Round-trip invariants

The committed expectations fixture requires all of these invariants:

- generated-config prototype validates with `glyph_generated_config_validator`
- runtime-candidate sample validates with `glyph_runtime_config_candidate_validator`
- runtime-candidate tables equal generated-config tables
- runtime-candidate role bindings equal generated-config role bindings
- runtime-candidate hard overrides equal generated-config hard overrides
- runtime-candidate priority references equal generated-config priority lists
- runtime-candidate suppression rules equal generated-config suppression rules
- Senscope export package sample validates with the committed validator contract
- Senscope export package nested generated config equals the committed prototype
- runtime config validation report fixture exactly matches regenerated output
- runtime config validation report summarizes the committed runtime-candidate sample
- generated-config-backed evaluator input checker still passes
- generated C++ diff artifact checker still passes
- all artifacts preserve `hardware_status=not_new_hardware_result`
- all artifacts preserve the nunchuk non-validation caveat
- all artifacts preserve not runtime-loaded caveats
- all artifacts preserve not serial/device write behavior caveats

## Caveats

- offline round-trip only
- not firmware source
- not runtime-loaded config
- not serial/device write behavior
- not hardware validation
- not nunchuk hardware validation

## Checker output

`tools/check_glyph_export_artifact_round_trip.py` prints:

- `glyph_export_artifact_round_trip`
- `status=PASS` or `status=FAIL`
- `checked_artifacts=<N>`
- `round_trip_invariants=<N>`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms docs/tools artifact alignment only. It does not
implement runtime-loaded config, firmware source generation, serial/device write
behavior, hardware validation, or nunchuk hardware validation.
