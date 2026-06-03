# Glyph Export Artifact Compatibility Index - 2026-06-03

## Purpose and scope

This document records a docs/tools-only compatibility index for the current
Glyph export-adjacent review artifacts.

It is not firmware source, not runtime-loaded config, not serial/device write
behavior, not hardware validation, and not nunchuk hardware validation.

## Artifact nodes

The compatibility index tracks these committed artifact nodes:

- `generated_config_prototype`
- `generated_config_contract`
- `runtime_config_candidate_sample`
- `runtime_config_candidate_validator_contract`
- `senscope_export_package_sample`
- `senscope_export_contract`
- `runtime_config_validation_report`
- `behavior_cases`
- `behavior_evaluator`
- `generated_cpp_review_artifact`

The index points only to committed docs/tools/fixtures artifacts already present
in this repository.

## Required invariants

The compatibility index requires these invariants to hold:

- generated-config tables equal runtime-candidate tables
- generated-config role bindings equal runtime-candidate role bindings
- generated-config hard overrides equal runtime-candidate hard overrides
- generated-config priority lists equal runtime-candidate priority references
- generated-config suppression rules equal runtime-candidate suppression rules
- Senscope export nested generated config equals committed generated-config prototype
- validation report summarizes the committed runtime-candidate sample
- runtime-candidate validation report table count equals generated-config table count
- generated-config-backed evaluator path still validates behavior cases
- all artifacts preserve hardware and nunchuk caveats

## Caveats

- not firmware source
- not runtime-loaded config
- not serial/device write behavior
- not hardware validation
- not nunchuk hardware validation

## Checker output

`tools/check_glyph_export_artifact_compatibility_index.py` prints:

- `glyph_export_artifact_compatibility_index`
- `status=PASS` or `status=FAIL`
- `artifact_nodes=<N>`
- `required_invariants=<N>`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms docs/tools artifact compatibility only. It does
not implement runtime-loaded config, generated firmware source, serial/device
write behavior, hardware validation, or nunchuk hardware validation.
