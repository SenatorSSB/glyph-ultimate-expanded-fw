# Glyph Identity Runtime Hardware Validation and Rollback Plan - 2026-05-28

## Purpose and scope

This document defines hardware-validation and rollback planning requirements for
any future identity-runtime firmware behavior change, generated constants
refactor, or runtime-loaded config implementation.

Scope boundaries:

- This does not execute hardware testing.
- This does not validate hardware.
- This is not a hardware result.
- This does not change firmware runtime behavior.
- This does not implement generated constants.
- This does not implement runtime-loaded config.
- This does not implement serial/device write behavior.

## Plan status

This is a planning document only. It records gates and evidence requirements for
future work; it does not approve firmware edits or hardware claims.

## Source authority

Primary source authority is limited to current repository sources:

- `src/modes/Ultimate.cpp`
- identity runtime role map docs/fixtures
- behavior-case docs/fixtures
- behavior evaluator
- table source sync docs/tools
- generated-config prototype docs/tools/fixtures
- generated C++ review artifact docs/tools/fixtures
- generated-config contract docs/fixtures
- runtime-loaded config design docs/fixtures
- preimplementation go/no-go docs/fixtures
- current checkers in `tools/`

Hardware behavior not recorded in current repository evidence remains unknown.

## When this plan is required

This plan is required before merging any future branch that claims preservation
or validation for:

- behavior-preserving source refactor;
- generated constants refactor;
- runtime behavior change;
- runtime-loaded config interpreter;
- storage/transport/device write behavior;
- nunchuk behavior.

## Hardware validation categories

- Behavior-preserving source refactor.
- Generated constants refactor.
- Runtime behavior change.
- Runtime-loaded config interpreter.
- Storage/transport/device write behavior.
- Nunchuk behavior.

## Minimum behavior-preserving refactor validation

- Prehardware checks pass.
- Build passes.
- Behavior evaluator passes.
- Source/table sync checks pass.
- Generated config checks pass.
- Limited hardware smoke test unless explicitly waived by user.
- No profile artifacts changed unless intentionally part of the branch.

## Minimum runtime behavior change validation

- Full hardware test plan.
- Explicit expected behavior matrix.
- Latest hardware result doc.
- Rollback commit/path.
- No unsupported hardware claims.
- Before merge, hardware result must be recorded.

## Minimum runtime-loaded config validation

- Valid config path test.
- Invalid config fallback test.
- Version mismatch test.
- Missing table rejection test.
- Forbidden role rejection test.
- Transport/storage failure test if transport/storage implemented.
- Latency/performance measurement if runtime path changes.

## Required evidence format

- Artifact provenance.
- Branch name and commit under test.
- Build artifact identity if a build artifact is produced.
- Hardware setup and operator notes.
- Test matrix with pass/fail rows.
- Failure notes and scope.
- Link or path to rollback branch or commit.

## Required rollback plan

- Rollback branch or commit.
- Restore previous firmware artifact if applicable.
- Restore previous profile artifact if applicable.
- Document failure and scope.

## Required no-regression areas

- Source-parsed table values.
- Current role bindings.
- Current evaluator phase order.
- Current hard override constants.
- Behavior-case evaluator results.
- Generated-config and generated C++ artifact checks.
- Profile artifacts unless intentionally in scope.
- Device transport and serial writer behavior unless separately approved.

## Nunchuk handling

Nunchuk behavior remains preserved in the source-backed model but is not
hardware-validated by this plan. Any future nunchuk claim must either exclude
nunchuk behavior from the validation scope or provide separate hardware evidence.

## Failure classification

- Checker failure.
- Build failure.
- Hardware setup failure.
- Hardware behavior mismatch.
- Unsupported hardware claim.
- Rollback failure.
- Scope violation.

## Merge gate policy

- Hardware result required before behavior change merge.
- No unsupported hardware claims.
- Rollback plan required.
- Checkers must pass.
- Explicit user approval required for firmware behavior changes.
- Source-backed plan required for generated constants refactor or runtime-loaded config implementation.

## Open blockers

- No new hardware result is produced by this planning branch.
- Future generated constants refactor requires explicit approval.
- Future runtime-loaded config implementation requires explicit approval and design resolution.
- Future storage/transport/device write behavior requires source authority and approval.
- Nunchuk hardware validation remains unexecuted.
