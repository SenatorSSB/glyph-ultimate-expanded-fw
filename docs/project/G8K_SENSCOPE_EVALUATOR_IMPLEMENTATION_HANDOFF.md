# G8K - Senscope Evaluator Implementation Handoff

Status: docs-only handoff artifact
Date: 2026-05-24

## Scope note

This document is docs-only and intended for implementation in the Senscope app repo, not in this Glyph firmware repo.

It packages the source-backed conclusions, recommended package shape, status taxonomy, diagnostics, deterministic evaluation order, test fixtures, and a copyable implementation prompt for a future Senscope-side realization evaluator.

It does not implement firmware code, app-side TypeScript, runtime push/export behavior, hardware flashing, or gameplay semantic logic.

## Source-backed Glyph-side conclusions

| conclusion | status | scope | source-backed basis |
| --- | --- | --- | --- |
| GC transport can carry selected-mode bytes | `SOURCE_BACKED` | `TRANSPORT_SPECIFIC` | `docs/project/G8F10_CAPABILITY_MODEL_STATUS_CONSOLIDATION.md`, `docs/project/G8F8_F11_FINAL_AUDIT_SEQUENCE_ROLLUP.md` |
| `SenscopePrototype` selected exact-table path exists but is selected-prototype-only and not default-reachable | `SOURCE_BACKED` | `SELECTED_PROTOTYPE_ONLY` | `docs/project/G8F10_CAPABILITY_MODEL_STATUS_CONSOLIDATION.md`, `docs/project/G8F11_IMPLEMENTATION_READINESS_DECISION.md` |
| `CustomControllerMode` arbitrary exact raw pair support is not proven by current source | `UNSUPPORTED_BY_CURRENT_SOURCE` | `MODE_SPECIFIC` | `docs/project/G8F10_CAPABILITY_MODEL_STATUS_CONSOLIDATION.md`, `docs/project/G8F11_IMPLEMENTATION_READINESS_DECISION.md` |
| non-GC transports are not GC-equivalent | `UNSUPPORTED_BY_CURRENT_SOURCE` | `TRANSPORT_SPECIFIC_NON_GC` | `docs/project/G8F10_CAPABILITY_MODEL_STATUS_CONSOLIDATION.md`, `docs/project/G8F8_F11_FINAL_AUDIT_SEQUENCE_ROLLUP.md` |
| export / push / flashing are out of scope for this approved handoff path | `OUT_OF_SCOPE` / `UNSUPPORTED_BY_CURRENT_SOURCE` | `HOST_WORKFLOW` / `FLASH_WORKFLOW` | `docs/project/G8F10_CAPABILITY_MODEL_STATUS_CONSOLIDATION.md`, `docs/project/G8F11_IMPLEMENTATION_READINESS_DECISION.md`, `docs/project/G8F8_F11_FINAL_AUDIT_SEQUENCE_ROLLUP.md` |

## Recommended Senscope-side implementation target

Use either:

1. an app-local prototype inside the Senscope repo, or
2. a shared `packages/realization-evaluator` package.

The implementation target should satisfy all of the following:

- no firmware dependency;
- no runtime push or export path;
- no upload / flashing workflow;
- no gameplay semantic computation;
- fail-closed behavior when evidence is missing or scope is mismatched;
- injected equivalence dataset support for same-effective proofs.

If package placement is still unclear, start app-local and promote to `packages/realization-evaluator` only after the contract and test surface stabilize.

## TypeScript concepts to implement

The following are the recommended Senscope-side concept names and responsibilities.

```ts
type CapabilityScope =
  | "GENERIC_BACKEND"
  | "MODE_SPECIFIC"
  | "TRANSPORT_SPECIFIC_GC"
  | "TRANSPORT_SPECIFIC_NON_GC"
  | "SELECTED_PROTOTYPE_ONLY"
  | "HOST_WORKFLOW"
  | "OUT_OF_SCOPE";

type EvidenceStrength =
  | "SOURCE_BACKED"
  | "SELECTED_PROTOTYPE_ONLY"
  | "TRANSPORT_SPECIFIC"
  | "INFERRED"
  | "UNKNOWN"
  | "UNSUPPORTED_BY_CURRENT_SOURCE";

type CapabilityClaim = {
  capabilityId: string;
  status: EvidenceStrength;
  scope: CapabilityScope;
  sourceRefs: Array<{
    path: string;
    symbol?: string;
    note?: string;
  }>;
  notes?: string[];
};

type RealizationEvaluationRequest = {
  intent: "REPRESENTABILITY" | "EXPORT" | "PUSH";
  requirementScope: CapabilityScope;
  targetId: string;
  capabilityClaims: CapabilityClaim[];
  desiredRaw?: { x: number; y: number };
  realizedRaw?: { x: number; y: number };
  sameEffectiveRequested?: boolean;
  equivalenceDatasetId?: string;
};

type Diagnostic = {
  diagnosticId: string;
  code: string;
  severity: "INFO" | "WARN" | "ERROR";
  message: string;
  claimId?: string;
  targetId?: string;
  sourceRefs?: Array<{
    path: string;
    symbol?: string;
    note?: string;
  }>;
  statusContribution: string;
  nextAction?: string;
};

type RealizationEvaluationResult = {
  status:
    | "EXACT_RAW_MATCH"
    | "SAME_EFFECTIVE_OUTPUT"
    | "RAW_MISMATCH"
    | "REPRESENTABILITY_UNSUPPORTED"
    | "REPRESENTABILITY_UNKNOWN"
    | "SOURCE_EVIDENCE_MISSING"
    | "MODE_SCOPE_MISMATCH"
    | "EXPORT_UNSUPPORTED"
    | "PUSH_UNSUPPORTED"
    | "OUT_OF_SCOPE";
  diagnostics: Diagnostic[];
};

interface EquivalenceDatasetProvider {
  getDataset(datasetId: string): Promise<{
    datasetId: string;
    mappings: Array<{
      desiredRaw: { x: number; y: number };
      realizedRaw: { x: number; y: number };
      effectiveOutputId: string;
    }>;
  } | null>;
}
```

Implementation notes:

- `CapabilityClaim` is the source-backed fact record.
- `CapabilityScope` is the compatibility fence, not a semantic label.
- `EvidenceStrength` preserves the distinction between direct source backing, selected-prototype-only lineage, transport-specific evidence, inference, and unsupported claims.
- `RealizationEvaluationRequest` carries only capability-evaluator inputs, not game semantics.
- `RealizationEvaluationResult` is deterministic and fail-closed.
- `EquivalenceDatasetProvider` is injected from Senscope and is the only approved source for same-effective proof.

## Status definitions

The evaluator should emit only the following statuses:

- `EXACT_RAW_MATCH`: desired raw equals realized raw under a supported claim.
- `SAME_EFFECTIVE_OUTPUT`: raw values differ, but injected dataset proof shows equal effective output.
- `RAW_MISMATCH`: raw values differ and no accepted same-effective proof applies.
- `REPRESENTABILITY_UNSUPPORTED`: current source-backed claims do not support the request.
- `REPRESENTABILITY_UNKNOWN`: evidence is incomplete or inconclusive.
- `SOURCE_EVIDENCE_MISSING`: source refs are absent or insufficient for a source-backed claim.
- `MODE_SCOPE_MISMATCH`: a mode-specific claim was used where generic support was required.
- `EXPORT_UNSUPPORTED`: export was requested, but source-backed support is not available.
- `PUSH_UNSUPPORTED`: push was requested, but source-backed support is not available.
- `OUT_OF_SCOPE`: request crosses the evaluator boundary, including gameplay semantic requests.

## Deterministic evaluation order

Use this fixed order:

1. Reject out-of-scope or gameplay-semantic requests.
2. Validate source evidence.
3. Validate scope compatibility.
4. Evaluate representability.
5. Evaluate export / push only when requested.
6. Evaluate same-effective only when an injected dataset proof is present.

The ordering must be stable and fail-closed. Later steps must not override earlier boundary failures.

## Diagnostic guidance

Recommended diagnostic families:

- `EVIDENCE_*` for source-ref and evidence-strength problems;
- `SCOPE_*` for generic vs mode-specific mismatches;
- `MATCH_*` for raw and same-effective comparison outcomes;
- `EXPORT_*` for export requests;
- `PUSH_*` for push requests;
- `SEMANTIC_BOUNDARY_*` for gameplay-semantic or other out-of-scope requests;
- `TRANSPORT_*` for transport-specific capability claims.

Example diagnostics:

- missing refs on a `SOURCE_BACKED` claim should produce `EVIDENCE_MISSING_REF`;
- mode-specific support used for a generic requirement should produce `SCOPE_MODE_SPECIFIC_ONLY` or `MODE_SCOPE_MISMATCH`;
- no dataset for same-effective should produce `MATCH_SAME_EFFECTIVE_DATASET_REQUIRED` and remain `RAW_MISMATCH` or `REPRESENTABILITY_UNKNOWN`;
- export requests should produce `EXPORT_UNSUPPORTED` when no approved source-backed workflow exists;
- push requests should produce `PUSH_UNSUPPORTED` when no approved source-backed workflow exists;
- gameplay semantic requests should produce `SEMANTIC_BOUNDARY_OUT_OF_SCOPE`.

## Test fixtures to implement

Use synthetic fixtures only. These are evaluator contract tests, not firmware claims.

1. source-backed exact raw synthetic mock
   - expected status: `EXACT_RAW_MATCH`
2. unknown generic exact raw support
   - expected status: `REPRESENTABILITY_UNKNOWN`
3. mode-specific support with generic request
   - expected status: `MODE_SCOPE_MISMATCH`
4. `CustomControllerMode` arbitrary exact raw unsupported
   - expected status: `REPRESENTABILITY_UNSUPPORTED`
5. GC transport carrying selected-mode bytes but no selected-mode realization
   - expected status: `REPRESENTABILITY_UNKNOWN`
   - note: transport bytes are evidence for transport-specific carriage, not proof of selected-mode realization by themselves
6. same-effective with dataset
   - expected status: `SAME_EFFECTIVE_OUTPUT`
7. same-effective without dataset
   - expected status: `RAW_MISMATCH`
8. export unsupported
   - expected status: `EXPORT_UNSUPPORTED`
9. push unsupported
   - expected status: `PUSH_UNSUPPORTED`
10. gameplay semantic request out of scope
    - expected status: `OUT_OF_SCOPE`

Fixture guidance:

- keep source refs explicit;
- keep unsupported claims conservative;
- do not promote inferred evidence to source-backed;
- do not derive same-effective without injected proof;
- do not encode gameplay semantics in any fixture.

## Clean implementation prompt for the Senscope repo

```text
Build a Senscope-side realization evaluator as either an app-local prototype or a shared package named packages/realization-evaluator.

Requirements:
- Keep it entirely in the Senscope repo.
- Do not add any firmware dependency.
- Do not add runtime push, export, upload, or flashing behavior.
- Do not add gameplay semantic computation.
- Preserve fail-closed behavior.
- Make evidence handling source-ref aware.
- Support synthetic contract tests and injected same-effective dataset proofs.

Implement these concepts:
- CapabilityClaim
- CapabilityScope
- EvidenceStrength
- RealizationEvaluationRequest
- RealizationEvaluationResult
- Diagnostic
- EquivalenceDatasetProvider

Use this status vocabulary only:
- EXACT_RAW_MATCH
- SAME_EFFECTIVE_OUTPUT
- RAW_MISMATCH
- REPRESENTABILITY_UNSUPPORTED
- REPRESENTABILITY_UNKNOWN
- SOURCE_EVIDENCE_MISSING
- MODE_SCOPE_MISMATCH
- EXPORT_UNSUPPORTED
- PUSH_UNSUPPORTED
- OUT_OF_SCOPE

Evaluation order must be deterministic:
1. reject out-of-scope / gameplay-semantic requests
2. validate source evidence
3. validate scope compatibility
4. evaluate representability
5. evaluate export/push only when requested
6. evaluate same-effective only with injected dataset proof

Add tests for:
- source-backed exact raw synthetic mock
- unknown generic exact raw support
- mode-specific support with generic request
- CustomControllerMode arbitrary exact raw unsupported
- GC transport carrying selected-mode bytes but no selected-mode realization
- same-effective with dataset
- same-effective without dataset
- export unsupported
- push unsupported
- gameplay semantic request out of scope

Keep the evaluator free of firmware assumptions and free of SSBU gameplay semantics.
```

## Model recommendation for the future Senscope implementation

- Use `5.3-Codex High` for implementation.
- Use `5.5 High` for package-boundary decisions if app-local versus shared-package placement is still unclear.

## Rollup

- No firmware source changed.
- No runtime/default reachability changed.
- No export / push / upload / flashing workflow was added.
- This completes the Glyph-side evaluator handoff for Senscope implementation intake.

## Boundary reminder

This document is a handoff package, not a runtime capability guarantee.
