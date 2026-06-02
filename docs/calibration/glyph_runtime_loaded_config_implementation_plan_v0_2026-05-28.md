# Glyph Runtime-Loaded Config Implementation Plan v0 - 2026-05-28

## Purpose and scope

This document defines a future implementation plan for runtime-loaded config.
The implementation remains blocked.

Scope boundaries:

- This is docs/tools-only.
- This does not implement runtime-loaded config.
- This does not implement storage.
- This does not implement serial/device write behavior.
- This does not change firmware behavior.
- This does not change profile artifacts.
- This does not change protobuf/config schema behavior.
- This does not validate hardware.
- This does not validate nunchuk hardware behavior.

## Plan status

This plan is blocked until explicit user approval and design resolution. It is
not approval to implement runtime-loaded config, storage, transport, schema
behavior, or device writing.

## Source authority

Primary source authority is limited to current repository sources:

- `src/modes/Ultimate.cpp`
- identity runtime role map docs/fixtures
- behavior-case docs/fixtures
- behavior evaluator
- generated-config prototype docs/tools/fixtures
- generated C++ review artifact docs/tools/fixtures
- generated-config contract docs/fixtures
- Senscope export draft docs/fixtures
- runtime-loaded config design docs/fixtures
- preimplementation go/no-go docs/fixtures
- current checkers in `tools/`

Unknown backend behavior remains unknown. Inferred behavior must be marked as
inferred before it can be used in any later implementation branch.

## Preconditions before implementation

- Explicit user approval.
- Storage location decision.
- Representation format decision.
- Boot-time validation design.
- Fallback behavior decision.
- Version migration policy.
- Maximum config size decision.
- Profile-bound vs global config decision.
- Update/transport path decision.
- Official configurator source authority.
- Hardware validation matrix.
- Nunchuk handling decision.

## Candidate implementation boundary

If later approved, the candidate implementation boundary is:

- Add a firmware-owned validator/interpreter for a bounded config format.
- Config may own only bounded data classes already documented.
- Firmware owns primitive evaluator and phase order semantics.
- Config must not mutate evaluator phase order.
- Config must not contain scripts, macros, turbo, timing automation, toggles, one-shot behavior, or history-dependent logic.
- Invalid config must fail safely to an approved fallback.
- Any storage/transport must be separately source-backed.

## Required architecture decisions

- Storage location.
- Representation format.
- Boot-time validation.
- Fallback behavior.
- Version migration.
- Maximum config size.
- Profile-bound vs global config.
- Update/transport path.
- Official configurator source authority.
- Hardware validation matrix.
- Nunchuk handling.

## Required validator architecture

A future validator/interpreter must be firmware-owned, bounded, source-backed,
and able to reject unsupported schema versions, unknown mode scope, missing
required tables, malformed table points, coordinates outside `[0,255]`, boolean
coordinates, unknown role classes, unknown priority classes, phase order
mutation, arbitrary scripts, macros, turbo, timing automation, one-shot or
toggle logic, missing source authority, hardware validation claims without a
hardware result source, device write instructions, serial transport payloads,
and embedded firmware patches.

## Required storage representation decisions

Future implementation planning must resolve storage location, representation
format, write/read lifecycle, validation timing, provenance, maximum config
size, profile-bound vs global scope, version migration, and rollback behavior.

## Required fallback and failure behavior

Future implementation planning must define invalid-config handling, missing
config behavior, version mismatch behavior, partial-write handling, safe
fallback behavior, and how the fallback is validated.

## Required transport policy

Any update or transport path must be separately source-backed and explicitly
approved. This plan does not implement serial/device write behavior or
push-to-device workflow.

## Required performance and latency evidence

Future implementation planning must define measurement scope, thresholds, and
runtime path evidence before latency or performance claims are made.

## Required hardware validation

Future implementation planning must include hardware test scope, artifact
provenance, operator steps, pass/fail criteria, post-failure rollback
expectations, and nunchuk scope before any hardware-validation claim.

## Required nunchuk decision

Future implementation planning must decide whether nunchuk behavior is excluded
from the claim or separately hardware-tested. This plan does not validate
nunchuk hardware behavior.

## Stop conditions

- Explicit approval is missing.
- Required architecture decisions are unresolved.
- Storage or transport behavior lacks source authority.
- Fallback behavior is ambiguous.
- Implementation would depend on inferred behavior.
- Config would mutate evaluator phase order.
- Config would include scripts, macros, turbo, timing automation, toggles, one-shot behavior, or history-dependent logic.
- Hardware validation or nunchuk validation would be claimed without hardware result evidence.

## Forbidden shortcuts

- Skip validator.
- Skip fallback policy.
- Accept unknown role classes.
- Allow scripts, macros, or turbo.
- Mutate phase order from config.
- Claim hardware validation without test.
- Implement device write or transport without source authority and approval.

## Approval requirement

Runtime-loaded config implementation requires explicit user approval before any
firmware source, storage, transport, profile artifact, or schema behavior edits.

## Open blockers

- Explicit user approval.
- Storage location decision.
- Representation format decision.
- Validator design.
- Failure/fallback policy.
- Version migration policy.
- Maximum config size.
- Profile-bound vs global config decision.
- Official configurator source authority.
- Update/transport path source authority.
- Performance/latency measurement plan.
- Hardware validation matrix.
- Nunchuk handling decision.
