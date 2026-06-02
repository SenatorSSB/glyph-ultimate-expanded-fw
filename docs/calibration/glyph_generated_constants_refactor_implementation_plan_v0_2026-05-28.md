# Glyph Generated Constants Refactor Implementation Plan v0 - 2026-05-28

## Purpose and scope

This document defines a future implementation plan for replacing hardcoded
identity-runtime table constants with generated or generated-like constants.

Scope boundaries:

- This is docs/tools-only.
- This does not edit firmware source.
- This does not implement generated constants.
- This does not change table values.
- This does not change runtime behavior.
- This does not change profile artifacts.
- This does not implement runtime-loaded config.
- This does not implement serial/device write behavior.
- This does not validate hardware.

## Plan status

This plan is blocked until explicit user approval. It is not approval to edit
firmware source, move constants, introduce generated files, or change runtime
behavior.

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

Unknown backend behavior remains unknown. Inferred behavior must be marked as
inferred before it can be used in any later implementation branch.

## Preconditions before implementation

- Explicit user approval for firmware source edits.
- Source-backed implementation plan reviewed for exact file boundary.
- Current checker sequence passing before edits.
- No forbidden artifacts present.
- Hardware test plan prepared before merge of any later firmware source branch.
- Rollback plan prepared before firmware source edits.
- No unsupported behavior or hardware claims.

## Candidate implementation boundary

If later approved, the candidate implementation boundary is:

- Move or replace current table constants with generated or generated-like constants.
- Preserve exact 25 source-parsed table values.
- Preserve current evaluator phase order.
- Preserve current role bindings.
- Preserve current hard override constants.
- Preserve behavior-case evaluator results.
- Preserve current generated-config and generated C++ artifact checks.
- No runtime-loaded config.
- No device write path.
- No profile schema changes.

## Files that may be touched if later approved

- `src/modes/Ultimate.cpp`
- Possibly one generated constants header/source file, only if approved and placed deliberately.
- Relevant tools, docs, and checkers.

## Files that must not be touched

Without separate approval, a later implementation must not touch:

- profile artifacts;
- protobuf/config schema files;
- serial writer behavior;
- HAL/device transport paths;
- build artifacts;
- `.pio`;
- `.uf2`, `.bin`, `.elf`, or `.map` artifacts.

## Required invariant preservation

- All 25 tables match current source-parsed values.
- Behavior evaluator passes current cases.
- Generated-config prototype checker passes.
- Generated C++ diff artifact checker passes.
- Runtime source checker passes.
- No forbidden artifacts checker passes.
- Build passes only if source changes are actually approved in a later branch.
- Hardware test plan exists before merge of any later firmware source branch.

## Required checker sequence

- `tools/check_glyph_identity_runtime_table_source_sync.py`
- `tools/check_glyph_identity_runtime_generated_config_prototype.py`
- `tools/check_glyph_identity_runtime_generated_config_evaluator_input.py`
- `tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py`
- `tools/check_glyph_identity_runtime_config_contracts.py`
- `tools/check_glyph_runtime_loaded_config_design.py`
- `tools/check_glyph_preimplementation_go_nogo_index.py`
- `tools/check_glyph_implementation_planning_packets.py`
- `tools/check_glyph_identity_runtime_behavior_evaluator.py`

## Required hardware validation

A later firmware source branch must include a hardware test plan before merge.
This planning packet does not execute hardware testing and is not a hardware
result.

## Rollback plan

- Identify the rollback branch or commit before firmware source edits.
- Preserve a path back to current hardcoded constants through normal Git history.
- Restore previous firmware artifact only if an artifact is intentionally produced later.
- Restore previous profile artifact only if a profile artifact is intentionally changed later.
- Document any checker or hardware failure and the exact affected scope.

## Stop conditions

- Explicit approval is missing.
- Source authority for a claimed behavior is missing or ambiguous.
- Implementation would depend on inferred behavior.
- Any table value would change.
- Any runtime behavior would change.
- Any profile artifact or schema change is required.
- Device write or serial transport behavior becomes part of the branch.
- Hardware validation would be claimed without a hardware result.

## Forbidden changes

- Behavior change.
- Table value change.
- Profile artifact change.
- Runtime-loaded config.
- Serial/device write behavior.
- Hardware validation claim.
- Macros, turbo, timing automation, one-shot behavior, toggles, or scripting.

## Approval requirement

Generated constants firmware refactor work requires explicit user approval before
firmware source edits.

## Open blockers

- Explicit user approval.
- Reviewed source-backed implementation boundary.
- Current checker sequence passing.
- Hardware test plan.
- Rollback plan.
- No unsupported behavior claims.
