# Glyph Runtime-Loaded Config Implementation Readiness Packet - 2026-05-28

## Purpose and scope

This packet defines what must be true before a future runtime-loaded config
implementation can be considered.

Scope boundaries:

- This is docs/tools-only.
- This does not implement runtime-loaded config.
- This does not implement storage.
- This does not implement serial/device write behavior.
- This does not change firmware behavior.
- This does not validate hardware.

## Status

This is a blocker/readiness packet. It is not approval to implement
runtime-loaded config, storage, transport, or device writing.

## Source authority

Primary source authority is limited to `src/modes/Ultimate.cpp`, the current
identity runtime role-map docs/fixtures, behavior-case docs/fixtures,
generated-config prototype docs/fixtures, generated-config contract
docs/fixtures, Senscope export draft docs/fixtures, runtime-loaded config design
docs/fixtures, runtime-loaded config validation contract docs/fixtures, and
current checkers in `tools/`.

## Why this is blocked

The runtime-loaded config design and validation contract are design-only. They
do not prove storage behavior, transport behavior, official configurator
integration, latency, fallback behavior, version migration, or hardware
validation.

## Required design decisions

- storage location;
- binary/JSON/protobuf/on-device representation;
- boot-time validation;
- fallback behavior if config invalid;
- version migration;
- maximum config size;
- profile-bound vs global config;
- official configurator integration source authority;
- transport policy;
- hardware validation plan.

## Required validator guarantees

A future validator must reject unsupported schema versions, unknown mode scope,
missing required tables, malformed table points, coordinates outside `[0,255]`,
boolean coordinates, unknown role classes, unknown priority classes, phase order
mutation, arbitrary script text, macros, turbo, timing automation, one-shot or
toggle logic, missing source authority, hardware validation claims without
hardware result source, device write instructions, serial transport payloads,
and embedded firmware patches.

## Required storage/transport decisions

Future implementation planning must resolve storage location, representation,
write/read lifecycle, transport policy, official configurator authority,
provenance, validation timing, and rollback behavior before code changes.

## Required failure/fallback policy

Future implementation planning must define invalid-config handling, missing
config behavior, version mismatch behavior, partial-write handling, and safe
fallback behavior before code changes.

## Required performance/latency evidence

Future implementation planning must define measurement scope and thresholds
before latency or performance claims are made.

## Required hardware validation plan

Future implementation planning must include hardware test scope, artifact
provenance, operator steps, pass/fail criteria, and post-failure rollback
expectations before claiming runtime-loaded config behavior is validated.

## Required nunchuk validation decision

Future implementation planning must decide whether nunchuk behavior is excluded
from the claim or separately hardware-tested. This packet does not validate
nunchuk hardware behavior.

## Forbidden implementation shortcuts

- skip validator;
- skip fallback policy;
- accept unknown role classes;
- allow scripts, macros, or turbo;
- mutate phase order from config;
- claim hardware validation without test;
- implement device write or transport without source authority and approval.

## Approval requirement

Runtime-loaded config implementation requires explicit user approval before any
firmware source, storage, or transport edits.

## Open blockers

- Explicit user approval.
- Storage location decision.
- Representation decision.
- Validator design.
- Failure/fallback policy.
- Version migration policy.
- Maximum config size.
- Profile-bound vs global config decision.
- Official configurator integration source authority.
- Transport policy.
- Performance/latency measurement plan.
- Hardware validation plan.
- Nunchuk validation decision.
