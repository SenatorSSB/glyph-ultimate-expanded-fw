# Glyph Offline Generated-Config Validator v0 - 2026-06-03

## Scope

This package adds an offline validator only for the current docs/tools generated-config prototype and generated-config contract.

The validator is not firmware source, not runtime-loaded config, not serial/device write behavior, not hardware validation, and not nunchuk hardware validation.

## Files

- `tools/glyph_generated_config_validator.py`
- `tools/check_glyph_generated_config_validator.py`
- `docs/calibration/fixtures/glyph_offline_generated_config_validator_contract_v0_2026-06-03.json`

## Source Authority

The validator is bounded by these existing committed fixtures:

- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json`

It does not create new table values and does not claim new backend behavior. The current table list, hard overrides, priority keys, role binding sections, source status, hardware status, nunchuk status, and non-goals are checked against those committed docs/tools contracts.

## Validation Boundary

The reusable module exposes:

- `load_json_object(path: Path) -> dict`
- `validate_generated_config(payload: dict) -> list[ValidationIssue]`
- `validate_generated_config_or_raise(payload: dict) -> None`

The validator rejects malformed generated-config payloads with explicit issue codes. It checks the schema name, contract version, mode scope, source status, hardware status, nunchuk status, direction convention, source authority, exactly 25 required tables, nine points per table, non-boolean integer coordinates in `[0,255]`, required hard overrides, required priority keys, priority-list entries, and bounded role binding metadata.

Priority lists must contain only the approved firmware-owned priority classes already represented by the committed generated-config prototype. Unknown priority classes are rejected with `E_UNKNOWN_PRIORITY_CLASS`. This is an offline tooling check only; it is not firmware source, not runtime-loaded config, not serial/device write behavior, and not hardware validation.

Forbidden payload content includes firmware source patches, serial transport payloads, device write instructions, macro or turbo logic, timing or history logic, arbitrary script/code strings, phase-order mutation claims, hardware validation claims without an explicit result source, and nunchuk hardware validation claims without an explicit result source.

## Checker Output

`tools/check_glyph_generated_config_validator.py` prints the required checker identity and summary lines:

- `glyph_generated_config_validator`
- `status=PASS` or `status=FAIL`
- `validated_schema=<schema>`
- `table_count=<N>`
- `hardware_status=not_new_hardware_result`

## Non-Goals

- No firmware runtime source changes.
- No generated C++ placed in firmware paths.
- No runtime-loaded config implementation.
- No serial/device write behavior.
- No push-to-device behavior.
- No hardware validation claim.
- No nunchuk hardware validation claim.
- No profile artifact changes.
