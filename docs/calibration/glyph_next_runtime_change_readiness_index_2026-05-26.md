# Glyph Next Runtime Change Readiness Index - 2026-05-26

Scope: readiness index before the next real Glyph firmware/runtime patch. This is not approval to flash, push to device, or implement runtime behavior. The next runtime patch still requires explicit user approval.

## Current Readiness State

- `READY_FOR_DESIGN_ONLY`: current source/docs/checker work supports continued design and review.
- `BLOCKED_NEEDS_USER_INPUT`: final physical roles, full modifier tables, chord/conflict behavior, disabled-remap outbound policy, and adapter write policy remain unresolved.
- `BLOCKED_NEEDS_HARDWARE`: preservation hardware matrix must be completed before any new runtime behavior can be claimed safe.
- `BLOCKED_CHECK_FAILURE`: only if the aggregator reports a real checker failure.
- `READY_FOR_RUNTIME_PATCH_REVIEW`: only after required sibling branch checkers are merged, user/corpus inputs are resolved, and hardware blockers are cleared or explicitly accepted for review scope.

## Completed Prerequisites In This Workstream Sequence

These prerequisites are intended to exist across the sibling branches in this long-run sequence:

- adapter policy decisions documented;
- read-only prewrite validation designed;
- physical/logical layout mapping documented;
- Ultimate preservation hardware matrix drafted;
- native Ultimate table runtime design written;
- native Ultimate table fixture contract drafted;
- native Ultimate table source-shape checker designed;
- full layout requirements spec created;
- readiness aggregation added here.

Because every branch is based on `configurator`, this aggregator skips optional sibling-branch tools until those branches are merged together.

## Remaining Blockers Before Runtime Patch

- User/domain requirements for the final physical and logical layout.
- Explicit modifier-state coordinate tables and chord/conflict policy.
- Captured export corpus for write-capable adapter decisions.
- Outbound disabled-remap policy for omitted `activates` versus explicit `BTN_UNSPECIFIED`.
- RF5 physical identity resolution.
- Preservation hardware result for C-stick/right-stick, triggers, SOCD, both-held behavior, defaults, and profile/readback.
- Explicit user approval for any runtime patch.

## Non-Approval Statement

This index does not approve flashing, push-to-device automation, firmware runtime changes, profile schema changes, SOCD changes, remap changes, or game-semantic source changes.
