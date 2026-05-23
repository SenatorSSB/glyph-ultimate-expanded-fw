# G11l First Output Behavior Design

Status: docs-only

## 1. Scope

This document designs the first selected-mode `SenscopePrototype` output behavior candidate.

This batch does not implement runtime behavior.

## 2. Current boundary

- `SenscopePrototype` is compile-visible and unreachable in normal mode selection.
- Constructor self-test is gated off by default.
- `SenscopePrototype` output methods are currently inert (neutral digital/analog output shell behavior).

## 3. Recommended first runtime behavior (future, approval-gated)

The first runtime behavior should be intentionally narrow:

- left-stick only;
- no right-stick behavior yet;
- no Force Up-B as the first runtime behavior;
- exact left-stick table resolver output only.

Direction source recommendation:

- prefer using the already-resolved post-SOCD direction signal from existing `ControllerMode`/`InputMode` flow only if that source path is explicitly source-safe and review-approved for this prototype;
- if not source-safe, start with the internal prototype direction helper and a controlled prototype input snapshot path.

Digital output recommendation:

- keep digital outputs neutral for the first selected runtime behavior unless explicit approval is given to enable digital composition.

## 4. Why not Force Up-B first

Force Up-B has a higher safety surface than plain table lookup because it can affect both:

- `B` digital output, and
- left-stick output.

It should remain deferred until the simpler left-stick table path is validated in isolation.

## 5. Why not mode activation/default config yet

Runtime reachability decisions should be reviewed separately from output behavior decisions.

Keeping activation/default config unchanged reduces blast radius while first output behavior is evaluated.

## 6. Proposed future G11l-impl stages

Stage A:

- make `SenscopePrototype` selectable only through an explicit manual/debug route after approval;
- keep outputs neutral.

Stage B:

- enable exact left-stick table output for a fixed test profile;
- keep digital outputs neutral;
- no Force Up-B.

Stage C:

- add digital OR and Force Up-B only after separate approval.

## 7. Stop conditions before implementation

- selected activation path is not explicitly approved;
- hardware safety review is not complete;
- direction source decision is unresolved;
- any change risks affecting existing selected modes.

## 8. Verification plan for future implementation

- run the standard build;
- grep-confirm no default-config edits;
- manual diff review of `src/core/mode_selection.cpp`;
- confirm runtime remains unreachable by default, or is only reachable through explicit manual gating.
