# Glyph Identity Runtime Generated-Config Contract v0 - 2026-05-28

## Purpose and scope

This document defines a reviewable contract for the current generated-config
prototype used by the Glyph Smash Box identity runtime in native
`MODE_ULTIMATE`.

This is a contract for tooling and review. It is app-independent and describes
the current generated-config prototype as a declarative intermediate artifact.

Scope boundaries:

- This is not firmware source.
- This is not included by firmware.
- This is not runtime-loaded config.
- This is not serial/device write behavior.
- This is not hardware validation.
- This does not change runtime behavior, table values, profile artifacts, or
  protobuf/config schema behavior.

## Contract status

`contract_version=1` describes the current
`glyph_identity_runtime_generated_config_prototype` fixture. The fixture is a
docs/tools-only contract target and is not a runtime input.

Required status values:

- `schema_name=glyph_identity_runtime_generated_config_prototype`
- `contract_version=1`
- `mode_scope=MODE_ULTIMATE`
- `source_status=source_backed_prototype_not_runtime_loaded`
- `hardware_status=not_new_hardware_result`
- `nunchuk_status=preserved_but_not_hardware_validated`
- `direction_convention=numpad`

## Source authority

Primary source authority for this contract is limited to:

- `src/modes/Ultimate.cpp`
- `tools/extract_glyph_identity_runtime_tables.py`
- `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_generated_config_prototype_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_generated_config_evaluator_input_2026-05-28.md`
- `docs/calibration/glyph_identity_runtime_generated_cpp_diff_artifact_2026-05-28.md`
- existing generated-config and identity-runtime checkers in `tools/`

The table truth is source-parsed from `src/modes/Ultimate.cpp`. Role metadata is
preserved from the role-map fixture. Behavior-case metadata is coverage metadata
only and is not table truth.

## Top-level fields

The generated-config prototype must provide these top-level fields:

- `schema_name`
- `contract_version`
- `mode_scope`
- `source_status`
- `hardware_status`
- `nunchuk_status`
- `direction_convention`
- `source_authority`
- `tables`
- `table_source_symbols`
- `role_bindings`
- `priority_model`
- `hard_overrides`
- `suppression_rules`
- `coverage_metadata`
- `non_goals`

The contract checker owns the required field list and must keep it aligned with
the committed generated-config prototype fixture.

## Table contract

The generated-config prototype must contain exactly the 25 required table names
defined by `tools/extract_glyph_identity_runtime_tables.py`:

- `Default`
- `ModeDefault`
- `X1`
- `X2`
- `MX1`
- `MX2`
- `Y1`
- `MY1`
- `LayerNormalX`
- `MLayerNormalX`
- `LayerFlipper`
- `MLayerFlipper`
- `Y1Tilt1`
- `MY1Tilt1`
- `Y1LayerFlipper`
- `MY1LayerFlipper`
- `Y1LayerNormalX`
- `MY1LayerNormalX`
- `Tilt1`
- `Tilt2`
- `Tilt3`
- `MTilt1`
- `MTilt2`
- `MTilt3`
- `Lt1LowMagnitude`

Each table has exactly 9 points. Each point is `[int, int]`. Booleans are
invalid coordinates. Every coordinate must be in `[0,255]`.

The table values are not authored by this contract. They are source-parsed from
the current `constexpr StickPoint` tables in `src/modes/Ultimate.cpp`.

## Role-binding contract

The generated-config prototype preserves existing role-map fixture field names
where possible. This branch does not redesign role schemas.

The role-binding data must explicitly distinguish:

- button carriers
- direction contributors
- C-stick bindings
- modifiers
- special functions
- layer/sub-mode metadata

Role bindings remain controller/backend metadata. They are not Senscope game
semantic mappings and are not user-facing SSBU action source authority.

## Priority-model contract

The generated-config prototype must carry these priority-model keys:

- digital effective direction priority list
- analog priority list
- physical input metadata
- layer left/right metadata
- LF4 sub-mode metadata
- forced-up resolution metadata
- button carrier metadata
- LS->DPad routing metadata
- table output metadata
- Direction+A metadata
- LT5/RF11 low-magnitude metadata
- RF7 hard Up+B metadata
- RF9 null metadata
- nunchuk override metadata

The priority model documents the current source-backed evaluator shape for
review. It is not a runtime-loaded evaluator definition.

## Hard-overrides contract

The generated-config prototype must include these source-backed hard overrides:

- RF7 hard Up+B:
  - left `[77,172]`
  - center `[128,172]`
  - right `[179,172]`
- RF9 null:
  - `[128,128]`
- LT5/RF11 low magnitude:
  - table reference `Lt1LowMagnitude`

The contract checker compares these values against the committed
generated-config prototype fixture.

## Suppression-rules contract

`suppression_rules` preserves the existing role-map fixture descriptions for the
current identity runtime. The field is descriptive controller/backend metadata
for review and checker coverage. It does not authorize new runtime behavior or
new game-semantic interpretation.

## Coverage-metadata contract

`coverage_metadata` records the behavior-case fixture, case count, category
count, category names, and hardware caveat from the current behavior-case
fixture. It is coverage metadata only.

Coverage metadata does not convert behavior cases into table truth and does not
make a new hardware validation claim.

## Non-goals and forbidden interpretations

This contract must not be interpreted as:

- firmware source
- runtime-loaded config
- serial/device write behavior
- hardware validation
- Senscope game semantics
- macro or turbo logic

It also does not alter table values, role bindings, profile artifacts,
protobuf/config schema behavior, or firmware runtime behavior.

## Validation and checker ownership

`tools/check_glyph_identity_runtime_config_contracts.py` owns the aggregate
contract validation for this document's fixture and the Senscope export draft
fixture.

The checker must validate:

- contract fixture structure and required caveats
- required top-level fields against the generated-config prototype
- required tables against the generated-config prototype
- hard override constants against the generated-config prototype
- boundary phrases in this document
- export draft fixture boundaries

## Migration path

1. Current docs/tools generated-config prototype.
2. Generated-config contract fixture for review and aggregate checking.
3. Senscope export package draft targeting the contract.
4. Generated C++ review text remains a review artifact only.
5. Firmware generated constants or runtime-loaded config require separate
   approval and source-backed implementation work.
6. Device write behavior requires separate source authority, policy approval,
   and validation.

## Open questions / deferred decisions

- Actual Senscope export package schema is deferred to the Senscope app.
- Runtime-loaded config is not designed or implemented here.
- Serial/device write behavior is not designed or implemented here.
- Nunchuk behavior remains preserved but not hardware-validated.
- Hardware validation is not claimed by this docs/tools-only contract.
