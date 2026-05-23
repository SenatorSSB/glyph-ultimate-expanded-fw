# G8h - Senscope App-Side Package Target Decision Inputs

Status: docs-only decision-input artifact
Date: 2026-05-23

## Scope note

This document is docs-only and not an app implementation.

It provides decision inputs for where evaluator code should eventually live in the Senscope repository.

## Candidate placement options

### Option 1: App-local prototype

- Pros:
  - fastest iteration with UI/request context nearby;
  - easiest to validate fail-closed behavior during early contract churn.
- Cons:
  - lower reuse and weaker separation from app feature code;
  - refactor cost when promoting to shared package.
- Dependency risks:
  - hidden coupling to app-local state helpers;
  - accidental dependency on unstable feature modules.
- Boundary risks:
  - backend capability and semantic logic can blur without strict review.
- When to choose it:
  - earliest phase when contracts/status/diagnostics are still moving quickly.

### Option 2: `packages/realization-evaluator`

- Pros:
  - clear ownership boundary for evaluator logic;
  - reusable by UI and test harnesses.
- Cons:
  - requires upfront package wiring and interface discipline;
  - can slow rapid exploratory changes.
- Dependency risks:
  - package may pull too many app/runtime dependencies too early.
- Boundary risks:
  - can become pseudo-semantic layer if boundaries are not enforced.
- When to choose it:
  - after fail-closed contract and diagnostics ordering stabilize.

### Option 3: `packages/backend-capabilities`

- Pros:
  - centralizes fixture ingestion and capability parsing;
  - keeps source-ref and claim-status handling cohesive.
- Cons:
  - evaluator decision logic may be awkward if deeply tied to request context.
- Dependency risks:
  - risk of circular dependency with evaluator package.
- Boundary risks:
  - capability ingestion concerns may be conflated with decision policy.
- When to choose it:
  - when primary instability is fixture/claim ingestion rather than evaluator status logic.

### Option 4: Dataset-adjacent package

- Pros:
  - same-effective dataset interface sits near dataset versioning concerns;
  - cleaner injection boundaries for equivalence evidence.
- Cons:
  - may over-center dataset concerns over core representability checks.
- Dependency risks:
  - evaluator could become tightly coupled to one dataset storage strategy.
- Boundary risks:
  - pressure to derive equivalence internally instead of consuming explicit dataset evidence.
- When to choose it:
  - when equivalence-dataset lifecycle and provenance are the primary design driver.

### Option 5: Adapter-specific package

- Pros:
  - keeps evaluator logic close to a specific backend adapter contract;
  - easier to encode adapter-specific constraints.
- Cons:
  - reduced reuse across backend families;
  - higher fragmentation risk.
- Dependency risks:
  - package lock-in to one adapter stack.
- Boundary risks:
  - adapter assumptions may leak into generic evaluator semantics.
- When to choose it:
  - only when multiple adapters diverge enough that a shared evaluator is impractical.

## Conservative recommended path

1. Start app-local or a small package prototype in Senscope repo only.
2. Keep mock fixtures synthetic.
3. Inject Senscope equivalence dataset rather than deriving same-effective.
4. Keep backend capability fixture ingestion separate from game semantics.
5. Promote to a package only after the test contract stabilizes.

## Firmware-repo boundary statement

This firmware repo should not host the TypeScript package unless that is separately decided and explicitly approved.
