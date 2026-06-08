# Phase 6 Bounded Config-Owned Data Architecture

Status: PHASE6_DESIGN_COMPLETE_NOT_IMPLEMENTED.

## Purpose

Phase 6 defines the design boundary for Stable Firmware + Bounded
Config-Owned Modifier Data. It keeps the current source-owned
`MODE_ULTIMATE` runtime behavior stable while documenting how a future approved
runtime-config implementation may allow config to own bounded modifier table
data.

This is docs/spec/tooling work only. It does not implement runtime-loaded
config, runtime-config storage, firmware parser integration, boot/load changes,
WebSerial/device write, firmware flashing automation, or production export.

## Initial Scope

- PROPOSED_DECISION_NOT_IMPLEMENTED: the first future runtime-config scope is
  `MODE_ULTIMATE` only.
- PROPOSED_DECISION_NOT_IMPLEMENTED: no cross-mode runtime config is accepted in
  the first implementation slice.
- PROPOSED_DECISION_NOT_IMPLEMENTED: mode scope must be validated before any
  candidate data can replace the source-owned baseline.

## Firmware-Owned Semantics

Firmware owns the behavior that makes a runtime-config candidate safe and
bounded:

- evaluator phase order;
- priority logic;
- role resolution;
- table selection;
- validation-before-use;
- fallback;
- migration policy;
- storage policy;
- device-write policy;
- transport behavior;
- firmware parser acceptance rules.

These are implementation semantics, not config data. A config artifact may
describe desired bounded table data, but it must not redefine how firmware
evaluates, orders, prioritizes, stores, migrates, transports, or recovers from
that data.

## Config-Owned Bounded Data

PROPOSED_DECISION_NOT_IMPLEMENTED: future config-owned data may be limited to a
bounded `MODE_ULTIMATE` modifier-data payload:

- table values;
- table IDs;
- table order;
- fixed point count;
- coordinate bounds;
- metadata;
- provenance;
- checksums.

The candidate schema fixture in
`docs/runtime_config/fixtures/phase6_bounded_config_owned_modifier_data_schema_candidate.json`
is schema/metadata only. It is not a runtime-loaded config, is not consumed by
firmware, and is not a production export format.

## Forbidden Config-Owned Behavior

Config must never own or introduce:

- macros;
- turbo;
- timing automation;
- arbitrary scripting;
- hidden device write;
- transport commands;
- firmware patches;
- evaluator phase order;
- priority logic;
- role-resolution semantics;
- storage write policy;
- device-write authority;
- WebSerial authority;
- history-dependent logic.

Any future checker or firmware implementation must reject candidate data that
claims these powers.

## Source-Owned Baseline Relationship

The current baseline remains source-owned:

- `src/modes/UltimateRuntimeConfigInterpreter.hpp` defines the current
  `RuntimeConfigView` shape and known-good source-owned fallback.
- `src/modes/UltimateIdentityRuntimeTables.hpp` contains source-owned table
  data.
- `src/modes/Ultimate.cpp` uses source-owned runtime-config references.
- `tools/extract_glyph_identity_runtime_tables.py` and Step 12 binary tooling
  can inspect and serialize offline preview data, but firmware does not consume
  those artifacts.

Phase 6 does not replace this baseline. It documents the boundary a later
approved implementation must preserve when introducing config-owned bounded
data.

## Current RuntimeConfigView Relationship

`RuntimeConfigView` is treated as the source-backed firmware-side shape for the
current baseline. Phase 6 proposes that any future runtime-loaded candidate must
adapt into the firmware-owned view only after whole-payload validation passes.

PROPOSED_DECISION_NOT_IMPLEMENTED: failed candidate validation must leave the
active `RuntimeConfigView` at the source-owned known-good baseline.

## Schema Candidate Relationship

The Phase 6 schema candidate fixture is intentionally descriptive:

- it records the proposed ownership split;
- it names bounded candidate-data fields;
- it records forbidden config semantics;
- it records proposed storage, format, and boot/load decisions;
- it states `consumed_by_firmware=false`;
- it states `runtime_loaded_config=false`.

It is not a firmware ABI, not a protobuf extension, not a `config.bin` layout,
not a WebSerial payload, and not an official configurator export.

## Validation-Before-Use Invariant

PROPOSED_DECISION_NOT_IMPLEMENTED: future firmware must validate the complete
candidate before activation. Minimum validation includes:

- schema/version accepted by firmware;
- mode scope equals `MODE_ULTIMATE`;
- table count and table IDs match the allowed set;
- table order is complete and duplicate-free;
- point count is exact;
- coordinates are within bounded raw-coordinate limits before narrowing;
- checksum/integrity data matches the firmware-owned parser policy;
- no forbidden config-owned behavior is present.

Partial activation is not allowed.

## Fallback Invariant

PROPOSED_DECISION_NOT_IMPLEMENTED: first implementation must fail closed by
ignoring invalid runtime-config candidates and preserving the source-owned
baseline. It must not auto-delete, auto-rewrite, or perform hidden recovery
writes.

Diagnostics may be designed later only when source-backed and approved. This
branch does not implement diagnostics, recovery mutation, storage mutation, or
rollback behavior.

## Implementation Stop Line

This branch stops before:

- firmware source edits;
- runtime-loaded config implementation;
- runtime-config storage implementation;
- firmware parser implementation or integration;
- boot/load source changes;
- WebSerial/device write;
- direct device mutation workflow;
- firmware flashing automation;
- UF2 copy automation;
- bootloader automation;
- production vendor-specific export output.

## Hardware Gates

Hardware testing is not required for Phase 6 because this branch is
docs/tools/fixtures/checkers only.

Any future branch that changes firmware behavior, parser behavior, storage
loading, boot/load sequencing, device-write behavior, or flashing behavior must
include a build requirement, hardware test plan, and recorded hardware result
before claiming validation.

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- Firmware binary/protobuf parser integration is not implemented.
- Boot/load runtime-config consumption is not implemented.
- WebSerial/device write is not implemented.
- Direct device mutation workflow is not implemented.
- Firmware flashing automation is not implemented.
- Public release is not claimed.
- Official configurator compatibility is not claimed.
- Universal compatibility is not claimed.
- Nunchuk validation is not claimed.
- Senscope neutral profile schema is not changed.
- Super Smash Bros. Ultimate game semantics are not changed.
