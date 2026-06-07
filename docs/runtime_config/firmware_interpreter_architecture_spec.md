# Firmware Interpreter Architecture Spec

## Purpose

This document describes the architecture boundary for a future firmware-owned
runtime config interpreter.

It is a spec-only artifact. It does not implement an interpreter, storage,
transport, or any runtime-loaded config behavior.

## Firmware-Owned Semantics

The interpreter must not take ownership of semantics that the firmware already
owns.

Firmware-owned semantics include:

- evaluator phase order;
- priority model semantics;
- role resolution;
- table selection logic;
- override ordering;
- fallback behavior;
- validation policy;
- safety constraints.

Config data may reference these semantics, but it must not rewrite them.

## Allowed Config-Owned Data

The future interpreter may only consume bounded data that has been approved as
config-owned, such as:

- table values;
- table names;
- source-backed role metadata;
- provenance and version metadata;
- checksums and hashes;
- bounded constants that are explicitly source-backed.

Anything outside those classes remains firmware-owned or out of scope.

## Interpreter Phase Order

The phase order in this spec is design-only and is not a firmware
implementation.

A future interpreter should, at minimum, validate before use, resolve
firmware-owned semantics, apply bounded config-owned data, and only then
produce controller outputs.

The order itself must remain firmware-owned, and the config must not mutate it.

## Validation-Before-Use Requirement

The firmware must validate any future runtime-loaded config before it is used.

Validation must reject unsupported schema versions, unknown mode scope, missing
tables, malformed points, out-of-range coordinates, boolean coordinates,
unknown role classes, unknown priority classes, scripts, macros, turbo,
timing automation, one-shot or toggle behavior, missing source authority,
hardware validation claims without evidence, nunchuk validation claims without
evidence, device-write instructions, serial transport payloads, and embedded
firmware patches.

## Fallback-To-Known-Good Requirement

If validation fails, the firmware must fall back to a known-good baseline.

That fallback must be deterministic, source-backed, and validated before use.
Invalid or corrupt input must not become controller output.

## Corrupt or Invalid Config Behavior

Corrupt or invalid runtime-loaded config must fail closed.

The firmware should preserve safe baseline behavior rather than guessing at
partial data. No hidden recovery path, no implicit transport write, and no
silent semantic promotion are allowed here.

## Version Migration Policy

Version migration is deferred. The architecture must support explicit version
checks, but it does not choose a migration algorithm in this branch.

Unsupported versions must either:

- fail closed to the known-good baseline; or
- be migrated by a separately approved, source-backed migration path.

## Storage Assumptions Deferred

Storage location, persistence model, rollback medium, and recovery medium are
all deferred.

This spec does not choose EEPROM, flash, file-backed storage, or any other
storage layout.

## Binary and Protobuf Deferred

Binary serialization, protobuf layout, parser implementation, and any wire
encoding are deferred.

This spec is not a serializer contract and is not a binary format claim.

## WebSerial and Device-Write Deferred

WebSerial transport, device-write behavior, save-to-device flow, and related
upload/write tooling are deferred.

This spec does not authorize hidden device write, push-to-device workflow, or
firmware flashing automation.

## Build and Hardware Gates

Future implementation must be gated by:

- a build that proves the firmware path compiles;
- a hardware plan that states the scope clearly;
- a hardware result packet that records the actual result;
- rollback and recovery notes when needed.

## No Implementation in This Branch

This branch does not implement the interpreter.

It does not change firmware source, does not change table values, does not add
runtime-loaded config consumption, and does not claim hardware validation.
