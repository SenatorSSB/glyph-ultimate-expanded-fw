# G8f - Capability Known-Unknowns and Audit Backlog

Status: docs-only audit-planning artifact
Date: 2026-05-23

## Scope and guardrails

This document is docs-only and audit-planning only.

It does not implement runtime behavior, evaluator runtime code, export/push workflows, hardware flashing, or gameplay semantics.

No runtime behavior is changed and no backend capability is newly claimed by this document.

## Status vocabulary

Use the existing conservative vocabulary from G2/G3/G5/G8:

- `SOURCE_BACKED`
- `INFERRED`
- `UNKNOWN`
- `UNSUPPORTED_BY_CURRENT_SOURCE`
- `OUT_OF_SCOPE`

Interpretation reminders:

- `UNKNOWN` does not mean unsupported.
- `UNSUPPORTED_BY_CURRENT_SOURCE` does not mean impossible.
- `INFERRED` must not be promoted to `SOURCE_BACKED` without new source authority.

## Known-unknown categories and audit backlog

### 1) Generic exact raw left-stick output support

- Current conservative status: `INFERRED` (generic byte-level output surface exists; arbitrary generic exact-coordinate realization is not yet source-backed as a universal backend guarantee).
- Source docs to inspect next:
  - `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`
  - `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`
  - `docs/project/G5_NON_RUNTIME_CAPABILITY_MODEL_SCHEMA_DRAFT.md`
  - source deep-audit candidates referenced by G2/G3: `src/modes/Ultimate.cpp`, `src/modes/CustomControllerMode.cpp`, `src/core/ControllerMode.cpp`
- Evidence needed to upgrade status:
  - deterministic, source-backed evidence that generic backend pathways (not only mode-specific hardcoded paths) can realize requested raw targets under defined constraints;
  - source refs tied to concrete realization rules and failure modes.
- Stop conditions:
  - if analysis would require claiming undocumented universal raw-coordinate support;
  - if conclusions depend only on inferred structure without direct source evidence.

### 2) Full 9-way directional modifier table support

- Current conservative status: `UNSUPPORTED_BY_CURRENT_SOURCE` for generic first-class support.
- Source docs to inspect next:
  - `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`
  - `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`
  - `docs/project/G5_NON_RUNTIME_CAPABILITY_MODEL_SCHEMA_DRAFT.md`
- Evidence needed to upgrade status:
  - source-backed generic representation and realization path for all 9 directions as a first-class backend primitive;
  - explicit mapping behavior, scope, and constraints.
- Stop conditions:
  - if only mode-specific behavior exists and cannot be safely generalized;
  - if upgrade would require semantic inference beyond documented controller/backend behavior.

### 3) Neutral direction 5 support

- Current conservative status: `UNSUPPORTED_BY_CURRENT_SOURCE` for first-class generic backend direction-5 capability.
- Source docs to inspect next:
  - `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`
  - `docs/project/G5_NON_RUNTIME_CAPABILITY_MODEL_SCHEMA_DRAFT.md`
  - `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`
- Evidence needed to upgrade status:
  - source-backed first-class backend representation or deterministic rule set for neutral direction `5` handling beyond centered-default assumptions.
- Stop conditions:
  - if work would reinterpret gameplay semantics to fill backend gaps;
  - if neutrality behavior is inferred from indirect side effects only.

### 4) Non-center neutral support

- Current conservative status: `UNKNOWN`.
- Source docs to inspect next:
  - `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`
  - `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`
  - `docs/project/G5_NON_RUNTIME_CAPABILITY_MODEL_SCHEMA_DRAFT.md`
- Evidence needed to upgrade status:
  - source-backed mode/config/runtime path proving non-center neutral can be represented and realized with documented constraints.
- Stop conditions:
  - if the only evidence is reference-only material without runtime authority;
  - if claims require undocumented assumptions about neutral-intent semantics.

### 5) Mode-specific selected-runtime support vs generic backend support

- Current conservative status: `SOURCE_BACKED` for the boundary rule itself (mode-specific evidence must not auto-satisfy generic requirements).
- Source docs to inspect next:
  - `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`
  - `docs/project/G8_MOCK_EVALUATOR_CONTRACT.md`
  - `docs/project/G8_EVALUATION_STATUS_AND_DIAGNOSTICS.md`
- Evidence needed to upgrade status:
  - explicit source-backed generic capability claims independent of selected runtime/mode-specific behavior.
- Stop conditions:
  - if scope promotion from mode-specific to generic would be inferred without dedicated source refs;
  - if evaluator decisions would silently bypass scope mismatch diagnostics.

### 6) Export support

- Current conservative status: `UNSUPPORTED_BY_CURRENT_SOURCE` for stable, approved export workflow/format in current inspected scope.
- Source docs to inspect next:
  - `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`
  - `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`
  - `docs/project/G8D_SOURCE_REF_AND_DIAGNOSTIC_TRACE_DESIGN.md`
- Evidence needed to upgrade status:
  - explicit, source-backed export artifact format/workflow authority;
  - documented compatibility and scope boundaries.
- Stop conditions:
  - if audit would require inventing vendor/private formats;
  - if export support is inferred from unrelated config transport primitives.

### 7) Push-to-device support

- Current conservative status: `UNSUPPORTED_BY_CURRENT_SOURCE` for approved host-side workflow (while device-side primitives may exist as lower-confidence evidence).
- Source docs to inspect next:
  - `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`
  - `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`
  - `docs/project/G8E_SENSCOPE_HANDOFF_BOUNDARY_NOTES.md`
- Evidence needed to upgrade status:
  - explicit, approved, source-backed end-to-end host/device push workflow and constraints.
- Stop conditions:
  - if workflow claims rely only on inferred device-side command handlers;
  - if implementation planning would cross into unapproved push tooling.

### 8) Same-effective evaluation dependency

- Current conservative status: `SOURCE_BACKED` dependency rule: same-effective requires Senscope-supplied equivalence dataset; deriving same-effective without dataset is `OUT_OF_SCOPE`.
- Source docs to inspect next:
  - `docs/project/G8_MOCK_EVALUATOR_CONTRACT.md`
  - `docs/project/G8_EVALUATION_STATUS_AND_DIAGNOSTICS.md`
  - `docs/project/G8D_SOURCE_REF_AND_DIAGNOSTIC_TRACE_DESIGN.md`
- Evidence needed to upgrade status:
  - formal Senscope-side dataset contract and traceable dataset provenance for equivalence decisions.
- Stop conditions:
  - if evaluator logic would derive equivalence internally without supplied dataset evidence;
  - if gameplay semantics are introduced to justify equivalence.

### 9) App-side integration location

- Current conservative status: `UNKNOWN` for final package placement; implementation placement decision remains outside this firmware repo.
- Source docs to inspect next:
  - `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`
  - `docs/project/G5_NON_RUNTIME_CAPABILITY_MODEL_SCHEMA_DRAFT.md`
  - `docs/project/G8E_SENSCOPE_HANDOFF_BOUNDARY_NOTES.md`
- Evidence needed to upgrade status:
  - explicit Senscope-repo decision record tying package location to dependency boundaries and test contract maturity.
- Stop conditions:
  - if this repo attempts to hard-commit TypeScript package placement without Senscope-side approval;
  - if integration location decisions require runtime architecture commitments not yet approved.

## Audit backlog execution guidance

1. Audit one category at a time and keep each status change source-referenced.
2. Preserve fail-closed behavior when evidence is incomplete.
3. Keep backend capability evidence separate from gameplay semantic authority.
4. Route app-side package/location decisions to Senscope-side planning artifacts.
