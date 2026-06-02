# Glyph Runtime-Loaded Config Design v0 - 2026-05-28

## Purpose and scope

This document defines a design-only future architecture boundary for a possible
runtime-loaded config for the Glyph Smash Box identity runtime in
`MODE_ULTIMATE`.

The upstream review artifact is the current generated-config contract. This
document describes ownership and rejection boundaries before any implementation
work exists.

Scope boundaries:

- This does not implement runtime-loaded config.
- This does not implement serial writing.
- This does not implement device writing.
- This does not alter firmware runtime behavior.
- This does not alter table values.
- This does not alter profile artifacts.
- This does not alter protobuf/config schema behavior.
- This does not validate hardware.
- This does not validate nunchuk hardware behavior.
- This does not touch Senscope browser app code.

## Design status

`design_version=1` is a docs/tools-only design package. It is not firmware
source, not a runtime input, not a serial/device write path, and not hardware
validation.

The paired fixture is a machine-readable checker target for design boundaries.
It is not a runtime config.

## Source authority

Primary source authority for this design is limited to current repository
sources:

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

No external source is used. Unknown future backend behavior remains unknown.

## Current pipeline state

The current source-backed chain is:

1. Hardcoded identity runtime in `src/modes/Ultimate.cpp`.
2. Canonical role map.
3. Behavior-case matrix.
4. Behavior evaluator.
5. Source-parsed table sync.
6. Generated-config prototype.
7. Generated-config evaluator-input validation.
8. Generated C++ review artifact.
9. Generated-config contract v0.
10. Senscope-to-Glyph export contract draft.

The generated-config prototype and contract are docs/tools review artifacts.
They do not prove that firmware can load configs at runtime.

## Firmware-owned responsibilities

Firmware must own:

- primitive evaluator;
- priority model semantics;
- allowed role classes;
- validation assumptions;
- deterministic current-input-to-output resolver;
- bounds checks for raw coordinates;
- rejection of unsupported role classes;
- rejection of arbitrary scripting or history-dependent behavior;
- source-backed implementation of any loaded-config interpreter if one is ever
  implemented.

Firmware ownership means these semantics must not be supplied by arbitrary
config data.

## Config-owned responsibilities

A future config may own only bounded data, such as:

- physical button role bindings;
- table IDs and table data;
- layer definitions;
- sub-mode definitions;
- hard override constants;
- low-magnitude override table reference;
- null override coordinate;
- limited priority-class references that map to firmware-owned semantics;
- metadata and source authority.

These fields are potential data ownership areas only. This design does not
approve an on-device representation or loader.

## Forbidden config capabilities

A future config must not provide:

- arbitrary scripting;
- macros;
- turbo;
- timing automation;
- one-shot behavior;
- toggles;
- history-dependent input logic;
- unbounded user-defined predicates;
- dynamic code execution;
- runtime changes to evaluator phase order;
- hidden device write behavior;
- claims of hardware validation.

## Determinism and evaluator constraints

Config must resolve deterministically from current input state only.

No frame history or temporal state should be required for the current
identity-runtime model. Priority order must be firmware-owned, even if config
can reference approved priority classes.

Raw coordinates must remain integer `[0,255]`. No raw coordinate is banned by
this design unless a validator explicitly rejects it for a firmware-specific
reason.

The current design does not prove latency properties and must not make latency
claims without measurement.

## Storage and transport boundaries

This design defines no storage implementation.

It implements no EEPROM, flash, or persistent storage layout. It implements no
serial write protocol. It implements no USB/configurator transport. It assumes
no Limit Labs configurator dependency. It approves no device push path.

## Validation model

The paired validation contract describes what a future validator must require
or reject before runtime-loaded config implementation work exists.

Validation must remain bounded to documented data classes, source authority,
mode scope, table shape, role classes, priority references, overrides, metadata,
and explicit non-goals.

Validation must reject any payload that attempts to become firmware source,
serial/device transport, arbitrary logic, macros, turbo, timing automation, or
hardware validation evidence.

## Hardware-status caveat

This design is not a new hardware result. It does not validate hardware and
must not be cited as hardware evidence.

Any future firmware runtime change or runtime-loaded config interpreter would
need separate hardware validation policy and execution.

## Nunchuk-status caveat

Nunchuk behavior remains preserved in the source-backed model but is not
hardware-validated here.

This design does not validate nunchuk hardware behavior and must not be cited
as nunchuk hardware evidence.

## Relationship to Senscope export draft

The Senscope export draft remains docs-only and not implemented. It may target
the generated-config contract as a future package boundary, but it does not
implement runtime-loaded config, serial transport, device writing, firmware
behavior changes, profile schema changes, or hardware validation.

This Glyph repo may define controller/backend validation boundaries. It must not
become the source authority for Senscope neutral profile semantics or Super
Smash Bros. Ultimate game semantics.

## Relationship to generated-config prototype

The generated-config prototype is the current source-backed docs/tools review
artifact for tables, role metadata, priority metadata, hard overrides,
suppression rules, and coverage metadata.

This design treats that artifact as an upstream review target. It does not
convert it into firmware input and does not alter the generated-config contract.

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

## Open questions / blocked decisions

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
