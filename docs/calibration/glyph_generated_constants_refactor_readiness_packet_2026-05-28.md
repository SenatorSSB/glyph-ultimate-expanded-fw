# Glyph Generated Constants Refactor Readiness Packet - 2026-05-28

## Purpose and scope

This packet defines what must be true before a future firmware-source refactor
can replace hardcoded table constants with generated constants.

Scope boundaries:

- This is docs/tools-only.
- This does not edit firmware source.
- This does not implement generated constants.
- This does not change table values.
- This does not change behavior.
- This does not validate hardware.

## Status

This is a blocker/readiness packet. It is not approval to refactor firmware
source and it is not a generated constants implementation.

## Source authority

Primary source authority is limited to `src/modes/Ultimate.cpp`, the current
identity runtime role-map docs/fixtures, behavior-case docs/fixtures,
generated-config prototype docs/fixtures, generated-config contract
docs/fixtures, generated C++ review artifact docs/fixtures, and current
checkers in `tools/`.

## Why this is blocked

The current generated-config and generated C++ artifacts are docs/tools review
artifacts. Moving constants into firmware source would be a firmware source
change and requires explicit user approval, source-backed implementation
planning, checker coverage, a hardware test plan, and rollback planning.

## Candidate refactor boundary

If later approved, the only candidate implementation scope would be:

- move current table constants into generated or generated-like constants;
- preserve exact table values;
- preserve exact evaluator behavior;
- preserve current priority order;
- preserve current role bindings;
- no behavior changes;
- no profile changes;
- no runtime-loaded config.

## Required source files if later approved

The implementation plan must identify the exact source files before edits are
made. Current source authority proves table constants in `src/modes/Ultimate.cpp`
only; it does not by itself approve moving those constants into another path.

## Required invariant preservation

- 25 tables exactly match source-parsed current values.
- Behavior evaluator still passes 118 cases.
- Generated-config checker passes.
- Generated C++ diff artifact checker passes.
- No forbidden artifacts.
- No source-shape guardrails fail.

## Required checker coverage

Checker coverage must include the table source-sync checker, generated-config
prototype checker, generated-config evaluator-input checker, generated C++ diff
artifact checker, generated-config contract checker, runtime-loaded config
design checker, preimplementation go/no-go checker, and behavior evaluator.

## Required hardware test plan

A future refactor plan must include hardware test scope, artifact provenance,
operator steps, and pass/fail criteria before claiming preservation after any
firmware source change.

## Required rollback plan

A future refactor plan must document how to return to the current hardcoded
table implementation through normal Git history if checker or hardware evidence
fails.

## Forbidden changes

- behavior change;
- table value change;
- profile artifact change;
- runtime-loaded config;
- serial/device write behavior;
- hardware validation claim;
- macros, turbo, timing automation, one-shot behavior, toggles, or scripting.

## Approval requirement

Generated constants firmware refactor work requires explicit user approval
before firmware source edits.

## Open blockers

- Explicit user approval.
- Source-backed implementation plan.
- Current checkers passing.
- Hardware test plan.
- Rollback plan.
- No unsupported behavior claims.
