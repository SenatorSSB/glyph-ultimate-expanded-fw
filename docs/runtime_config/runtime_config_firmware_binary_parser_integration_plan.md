# Runtime Config Firmware Binary Parser Integration Plan

Status label: DESIGN_APPROVAL_GATE_ONLY.

## Purpose

This Step 13 plan defines the future implementation boundary for firmware
binary/protobuf runtime-config parser integration.

It is a design and approval gate only. It does not modify firmware source, does
not make firmware consume binary/runtime-loaded config, does not add storage,
does not add WebSerial/device write, does not add exporter output, and does not
add firmware flashing automation.

## Parser Input Boundary

A future parser may accept only an already-obtained bounded byte buffer or
decoded protobuf message candidate for the `MODE_ULTIMATE` runtime table corpus
after explicit approval.

The input boundary must be firmware-owned and must identify:

- byte source: storage, command payload, test fixture, or another approved
  source;
- payload format: raw binary preview, protobuf, or another approved format;
- maximum payload size;
- mode scope;
- schema/version;
- table count;
- point count per table;
- table-id order;
- checksum or CRC coverage;
- provenance or source-authority marker if the approved format includes one.

No byte source is approved by this branch.

## Offline Binary Preview Relation

The Step 12 offline binary preview is a useful candidate input shape for future
review because it is deterministic, table-bounded, and checker-backed.

The preview container currently records:

- magic `GCFG`;
- format version `1`;
- `MODE_ULTIMATE` scope hash;
- `27` tables;
- `9` points per table;
- canonical table-id order;
- raw `uint8` x/y point payload;
- CRC32 over header, table order, and payload.

## Why The Offline Container Is Not Yet Firmware Format

The offline container is not yet a firmware format because:

- it is explicitly documented as offline-only;
- no firmware parser consumes it;
- no firmware storage slot or boot-time read path is defined;
- no protobuf schema, command ID, or current `Config` extension is approved;
- no maximum-size or memory-budget decision exists for firmware;
- no migration, rollback, recovery, or diagnostics policy is approved;
- no hardware result validates firmware consumption;
- no official protobuf or official configurator compatibility claim exists.

Future firmware may reuse, revise, or reject the preview shape only after the
source-authority and product-approval gates are passed.

## Validation-Before-Use Sequence

A future implementation must validate all payload bytes before producing a
`RuntimeConfigView` used by `Ultimate.cpp`.

Minimum sequence:

1. Read candidate payload from an approved source into a temporary candidate.
2. Reject missing payload and use the known-good source-owned baseline.
3. Check payload length against the approved fixed length or maximum size.
4. Validate magic or message type if the selected format defines one.
5. Validate schema/version before parsing version-specific fields.
6. Validate mode scope is exactly `MODE_ULTIMATE`.
7. Validate checksum/CRC over the exact approved byte range before trusting
   table data.
8. Validate table count is exactly `27`.
9. Validate point count per table is exactly `9`.
10. Validate table-id order is complete, canonical, unique, and in range.
11. Validate a fallback table ID is present and valid if the format carries one.
12. Validate table payload length matches the declared table and point counts.
13. Validate each coordinate as an integer in `[0,255]` before narrowing to
    `uint8_t`.
14. Reject booleans, negative values, floats, strings, truncated entries,
    trailing bytes, duplicate tables, missing tables, and unsupported metadata.
15. Reject forbidden capabilities: macros, turbo, timing automation, arbitrary
    scripts, one-shot behavior, toggles, history-dependent logic, transport
    commands, device-write instructions, firmware patches, and unproven
    hardware claims.
16. Materialize only bounded table data into a firmware-owned representation.
17. Validate the resulting `RuntimeConfigView` with the source-owned boundary
    before use.
18. If any step fails, use `kKnownGoodRuntimeConfig`.

## Checksum And CRC Policy

The Step 12 preview uses CRC32 over header, table order, and payload. Integrity
checking is required before use in any future firmware parser, but the firmware
checksum/CRC algorithm, byte range, endianness, and failure behavior remain
undecided until separately approved.

The existing Pico `Config` persistence CRC proves a current `Config` integrity
pattern. It does not approve a runtime table CRC layout, a storage slot, or a
firmware parser.

Checksum or CRC failure must fail closed to the known-good baseline.

## Schema And Version Policy

The future parser must reject unknown or unsupported schema versions.

Version migration is not approved by this branch. Unsupported versions must use
the known-good source-owned baseline unless a separately approved migration path
exists and is hardware-tested where behavior can change.

## Mode Scope Policy

The future parser must reject payloads not explicitly scoped to
`MODE_ULTIMATE`.

This plan does not authorize cross-mode runtime-loaded config, global controller
config mutation, nunchuk validation, or Senscope/game-semantic schema changes.

## Table ID And Order Validation

The future parser must require exactly the source-owned current table corpus:

- `27` table IDs;
- canonical order matching `RuntimeTableId`;
- no missing IDs;
- no duplicate IDs;
- no IDs outside the approved enum range;
- known table symbols if the selected format carries symbols;
- valid fallback table ID if the selected format carries one;
- `9` points per table.

Any table drift must be reviewed against
`src/modes/UltimateRuntimeConfigInterpreter.hpp` and source-sync checkers before
firmware use.

## Coordinate Validation Before Narrowing

Firmware `StickPoint` coordinates are `uint8_t`. A future parser must validate
raw coordinates before narrowing:

- value is an integer;
- value is not a boolean masquerading as an integer;
- value is in `[0,255]`;
- table payload contains complete x/y pairs;
- no implicit clamp is used for invalid source data.

Invalid coordinates must reject the whole candidate payload and fall back to
the known-good baseline.

## Fallback-To-Known-Good Policy

Fallback source remains:

- `kKnownGoodRuntimeConfig`;
- `kSourceOwnedCurrentBaselineRuntimeConfig`;
- source-owned table constants included by `src/modes/Ultimate.cpp`;
- validation helpers in `src/modes/UltimateRuntimeConfigInterpreter.hpp`.

Future parser failure must not partially apply runtime table data. The accepted
unit is the whole validated runtime-config payload.

## Missing, Corrupt, Or Unsupported Payload Behavior

| Payload state | Required future behavior |
| --- | --- |
| Missing runtime config | Use source-owned known-good baseline |
| Truncated payload | Reject and use known-good baseline |
| Invalid magic/message type | Reject and use known-good baseline |
| Unsupported version | Reject and use known-good baseline unless approved migration exists |
| Wrong mode scope | Reject and use known-good baseline |
| Invalid checksum/CRC | Reject and use known-good baseline |
| Missing table | Reject and use known-good baseline |
| Duplicate or out-of-range table ID | Reject and use known-good baseline |
| Out-of-range coordinate | Reject and use known-good baseline |
| Forbidden capability marker | Reject and use known-good baseline |

No partial table use, guessed defaults from malformed payload, or hidden
recovery write is approved.

## Storage Dependency Status

Storage dependency status: unresolved and not implemented.

This plan does not choose:

- current `config.bin` reuse;
- a separate runtime-config file;
- flash address or filesystem path;
- profile-scoped versus global storage;
- atomic write strategy;
- staged known-good copy;
- storage cleanup or recovery mutation.

Current `Config` persistence is a source-backed precedent for the existing
protobuf `Config` object only.

## Boot-Time Read Dependency Status

Boot-time read dependency status: unresolved and not implemented.

This plan does not choose when a runtime-config payload would be read, how it
would interact with `persistence.LoadConfig(config)`, whether it is
mode-scoped, or how failures are surfaced to the user.

## Rollback And Recovery Requirements

A future implementation must define recovery before firmware consumption:

- how invalid stored payloads are ignored, preserved, deleted, or replaced;
- whether diagnostics are retained;
- whether a staged known-good runtime-config copy exists;
- how rollback is triggered;
- how recovery is tested without hidden device-write behavior;
- how users return to the source-owned baseline.

No recovery mutation is implemented by this branch.

## Hardware Test Requirements

Hardware testing is not required for this branch because no firmware source is
changed.

A future implementation branch that makes firmware consume a runtime-config
payload must include a build proof, hardware plan, and hardware result covering
at minimum:

- boot with no stored runtime config;
- boot with valid runtime config if implemented;
- invalid checksum fallback;
- unsupported version fallback;
- missing table fallback;
- out-of-range coordinate rejection;
- baseline output preservation;
- profile regression;
- recovery/rollback behavior if testable;
- nunchuk `NOT_TESTED` unless actually validated.

## Exact Stop Line Before Implementation

This document stops at architecture/design review for a future parser boundary
and does not implement firmware parsing, runtime-loaded config consumption,
storage/boot loading, protobuf/binary write, WebSerial/device write, exporter
output, firmware flashing automation, schema changes, firmware behavior
changes, or Super Smash Bros. Ultimate game-semantic changes.

Future work after this stop line requires explicit product approval and the
source-authority gates listed in
`docs/runtime_config/runtime_config_firmware_binary_parser_source_authority.md`.

## Non-Claims

- Firmware parser implementation is not implemented.
- Runtime-loaded config consumption is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- Firmware flashing automation is not implemented.
- Nunchuk validation is not claimed.
- Official protobuf compatibility is not claimed.
- Universal official configurator compatibility is not claimed.
