# Glyph Runtime Config Candidate Validator v0 - 2026-06-03

## Purpose and scope

This document defines an offline validator only for a future
`glyph_runtime_config_candidate` payload shape.

The payload shape is a docs/tools review artifact. It is not firmware source,
not runtime-loaded config, not serial/device write behavior, not hardware
validation, and not nunchuk hardware validation.

Required caveat phrases: offline validator only; not firmware source; not runtime-loaded config; not serial/device write behavior; not hardware validation; not nunchuk hardware validation.

This package does not implement runtime-loaded config. It does not define a
serial transport payload, a push-to-device workflow, a firmware storage format,
or a device write path.

## Candidate status

The current candidate sample uses these required status values:

- `schema_name=glyph_runtime_config_candidate`
- `candidate_version=1`
- `status=candidate_docs_only_not_runtime_loaded`
- `mode_scope=MODE_ULTIMATE`
- `hardware_status=not_new_hardware_result`
- `nunchuk_status=preserved_but_not_hardware_validated`

The candidate sample derives table data, role-binding metadata, hard overrides,
priority references, suppression-rule metadata, and bounded metadata from the
committed generated-config prototype fixture:

- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`

The candidate also points to the existing generated-config contract and
runtime-loaded validation contract:

- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json`
- `docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json`

## Validator ownership

`tools/glyph_runtime_config_candidate_validator.py` owns reusable validation for
candidate payload shape. The public functions are:

- `load_json_object(path: Path) -> dict`
- `validate_runtime_config_candidate(payload: dict) -> list[ValidationIssue]`
- `validate_runtime_config_candidate_or_raise(payload: dict) -> None`

`tools/check_glyph_runtime_config_candidate_validator.py` validates the committed
sample fixture, this document, and the machine-readable validator contract.

## Required payload shape

The candidate payload must include:

- schema/version/status metadata;
- `MODE_ULTIMATE` scope;
- `not_new_hardware_result` caveat;
- `preserved_but_not_hardware_validated` nunchuk caveat;
- source-authority object;
- generated-config contract reference;
- runtime validation contract reference;
- exactly 25 required tables;
- bounded role-binding metadata;
- approved priority references;
- generated-config contract hard overrides;
- suppression rules as string-list metadata only;
- metadata object;
- required boundary non-goals.

## Table validation

The validator requires exactly the 25 table names documented by the
generated-config contract. Each table must contain exactly nine points. Each
point must be `[int, int]`; booleans are invalid coordinates; each coordinate
must be in `[0,255]`.

The checker verifies that the committed sample tables match the current
generated-config prototype fixture. The validator itself checks payload shape
and bounds; it does not make the sample firmware input.

## Role and priority validation

Role bindings are bounded metadata only. They are not Senscope game semantics
and do not promote Super Smash Bros. Ultimate action/function meanings into this
repo.

Accepted data classes are constrained to the runtime-loaded validation contract:

- `ButtonOutput`
- `DirectionContribution`
- `CStickContribution`
- `TableModifier`
- `CompositeModifier`
- `LayerOverride`
- `SubmodeOverride`
- `HardAnalogOverride`
- `LowMagnitudeOverride`
- `NullAnalogOverride`
- `LsToDpad`
- `SuppressionRule`
- `ForcedDirection`
- `RoleOverride`

Priority references may use only these approved firmware-owned classes:

- digital: `physical_inputs`, `layer_left_right`, `lf4_submode_active`,
  `forced_up_resolution`, `button_carriers`, `ls_to_dpad_routing`
- analog: `table_output`, `direction_plus_a`,
  `lt5_or_rf11_low_magnitude_za`, `rf7_hard_up_b`, `rf9_null`,
  `nunchuk_override`

The candidate validator rejects unknown priority classes and unsupported
phase-order mutation content. It does not define runtime evaluator semantics.

## Hard overrides

Hard overrides must match the generated-config contract:

- RF7 hard Up+B:
  - left `[77,172]`
  - center `[128,172]`
  - right `[179,172]`
- RF9 null:
  - `[128,128]`
- LT5/RF11 low magnitude:
  - table reference `Lt1LowMagnitude`

These are validated as docs/tools candidate data. They are not firmware source
and do not change table values or runtime behavior.

## Forbidden content

The validator rejects payload content that embeds or claims:

- firmware source patches;
- serial transport payloads;
- device write instructions;
- macros;
- turbo behavior;
- timing automation;
- one-shot, toggle, or history-dependent logic;
- runtime-loaded config implementation claims;
- phase-order mutation;
- hardware validation claims without a hardware result source;
- nunchuk hardware validation claims without a hardware result source;
- arbitrary script/code text.

The current candidate status intentionally uses `not_new_hardware_result`; this
package does not claim hardware validation.

## Checker output

The checker must print these summary fields:

- `glyph_runtime_config_candidate_validator`
- `status=PASS` or `status=FAIL`
- `validated_schema=<schema>`
- `table_count=<N>`
- `hardware_status=not_new_hardware_result`

## Non-goals

This validator package is not:

- firmware source;
- runtime-loaded config;
- serial/device write behavior;
- hardware validation;
- nunchuk hardware validation;
- Senscope game semantics;
- a table value or runtime behavior change.
