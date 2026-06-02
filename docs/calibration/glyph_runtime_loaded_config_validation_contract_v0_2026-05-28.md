# Glyph Runtime-Loaded Config Validation Contract v0 - 2026-05-28

## Purpose and scope

This document defines what a future runtime-loaded config validator must reject
or require before any runtime-loaded config implementation exists.

The contract is design-only. It is not implemented as a firmware validator, not
runtime-loaded config, not serial/device write behavior, and not hardware
validation.

## Validation status

`contract_version=1` records a docs/tools-only validation contract. The paired
fixture is a checker target for boundaries and required rejection categories.

This document does not implement runtime-loaded config and does not authorize a
device write path.

## Source authority

Primary source authority is limited to current repository sources:

- `src/modes/Ultimate.cpp`
- `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_generated_config_prototype_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json`
- `docs/calibration/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.md`
- `docs/calibration/fixtures/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json`
- existing identity-runtime checkers in `tools/`

No external source is used.

## Required validation inputs

A future validator must receive or derive:

- generated-config contract version;
- mode scope;
- table set;
- role bindings;
- priority model references;
- hard overrides;
- source authority;
- hardware status caveat;
- nunchuk status caveat.

## Required accepted data classes

A future validator may accept only bounded data classes:

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

## Required rejection rules

A future validator must reject:

- unknown schema version;
- unknown mode scope;
- missing required tables;
- malformed table point;
- coordinate outside `[0,255]`;
- boolean coordinate values;
- unknown role class;
- unknown priority class;
- unsupported phase-order mutation;
- arbitrary script/code text;
- macro/turbo/timing automation;
- one-shot/toggle/history-dependent behavior;
- missing source authority;
- hardware validation claim without hardware-result source;
- nunchuk hardware validation claim without hardware-result source;
- device-write instructions;
- serial transport payloads;
- firmware source patches embedded in config.

## Table validation rules

Table validation must require:

- required tables present;
- exactly nine points per table;
- each point is two non-boolean integers;
- each coordinate is in `[0,255]`.

No raw coordinate is banned by this contract unless a validator explicitly
rejects it for a firmware-specific reason.

## Role-binding validation rules

Role-binding validation must require known bounded role classes and reject
unknown role classes.

Role bindings are controller/backend data. They are not Senscope game semantics
and do not promote Super Smash Bros. Ultimate action/function meanings into this
repo.

## Priority-reference validation rules

Priority references may name only approved firmware-owned priority classes.

Config must not mutate evaluator phase order. Priority model semantics remain
firmware-owned even if config can reference bounded priority classes.

## Override validation rules

Override validation must constrain hard analog overrides, low-magnitude table
references, and null analog overrides to bounded data.

Override coordinates must be non-boolean integers in `[0,255]`. Table
references must name present tables.

## Metadata and version validation

Metadata validation must require schema/version identity, mode scope, source
authority, hardware status caveat, and nunchuk status caveat.

Unknown schema versions and unknown mode scopes must be rejected.

## Runtime and hardware boundaries

This contract is not runtime-loaded config and is not a runtime-loaded config
implementation.

It is not serial/device write behavior. It is not hardware validation and does
not validate nunchuk hardware behavior. It does not change firmware runtime
behavior, table values, profile artifacts, or protobuf/config schema behavior.

## Relationship to generated-config contract

The generated-config contract remains the upstream review artifact for the
current docs/tools prototype. A future validator must be compatible with its
`MODE_ULTIMATE` scope, `not_new_hardware_result` caveat, table shape, hard
override shape, and source authority boundaries.

## Relationship to Senscope export draft

The Senscope export draft remains draft docs-only and not implemented.

A future validator may inspect a package that targets the generated-config
contract, but it must reject device write instructions, serial transport
payloads, runtime-loaded config implementation claims, firmware behavior change
claims, profile schema change claims, macro/turbo logic, timing/history logic,
and unsupported hardware validation claims.

## Checker ownership

`tools/check_glyph_runtime_loaded_config_design.py` owns the docs/tools-only
fixture and caveat checks for this design package.

The checker validates the two new fixtures, their relationship to the
generated-config contract fixture, the Senscope export draft boundary, and key
document caveat phrases.

## Migration path

1. Current hardcoded runtime.
2. Generated config as docs/tools review artifact.
3. Generated config can drive tools/evaluator.
4. Generated C++ review text can be diffed against source.
5. Firmware generated constants refactor may be proposed only after explicit
   approval.
6. Runtime-loaded config interpreter/storage design may be proposed only after
   separate approval.
7. Device write/transport workflow may be proposed only after separate source
   authority, policy, and validation.

## Open questions

- Exact runtime-loaded config storage location.
- Binary vs JSON/protobuf/on-device representation.
- Boot-time validation strategy.
- Failure fallback strategy.
- Version migration policy.
- Maximum table/config size.
- Whether configs are profile-bound or global.
- Whether official configurator/profile storage can be source-authoritatively
  integrated.
- Hardware validation plan.
- Nunchuk validation status.
