# G8d - Source Ref and Diagnostic Trace Design

Status: docs-only design draft
Date: 2026-05-23

## Scope note

This is a docs-only design artifact for evaluator source-reference discipline and diagnostic tracing.

No runtime evaluator code is implemented in this repository by this batch.

## Source-reference requirements

Evaluator claim handling should preserve conservative authority rules:

1. Every `SOURCE_BACKED` claim needs non-empty `source_refs`.
2. `INFERRED` claims remain inferential and must not pass as `SOURCE_BACKED`.
3. `UNKNOWN` claims should carry missing-evidence diagnostics.
4. `UNSUPPORTED_BY_CURRENT_SOURCE` should include inspected-basis refs or notes describing the basis for non-support.

Recommended source-ref minimum fields:

- `path`
- `symbol` (optional)
- `note` (optional)

## Diagnostic trace shape

Conceptual trace fields:

```ts
type DiagnosticTrace = {
  diagnostic_id: string;
  code: string;
  severity: "INFO" | "WARN" | "ERROR";
  message: string;
  claim_id?: string;
  source_refs?: Array<{
    path: string;
    symbol?: string;
    note?: string;
  }>;
  target_id?: string;
  status_contribution: string;
  next_action?: string;
};
```

Field intent:

- `diagnostic_id`: stable per-emission id for deterministic reporting.
- `code`: machine-readable diagnostic code.
- `severity`: severity band.
- `message`: human-readable summary.
- `claim_id`: capability claim that triggered the diagnostic.
- `source_refs`: supporting refs or inspected-basis refs.
- `target_id`: neutral target identifier when applicable.
- `status_contribution`: how this diagnostic contributed to final status.
- `next_action`: conservative follow-up guidance.

## Diagnostic trace examples

The examples below stay controller/backend-focused and avoid gameplay semantic claims.

### 1) Missing evidence

```json
{
  "diagnostic_id": "diag-001",
  "code": "EVIDENCE_MISSING_REF",
  "severity": "ERROR",
  "message": "SOURCE_BACKED claim cannot be accepted because source_refs are missing.",
  "claim_id": "exact_raw_left_stick_output",
  "source_refs": [],
  "target_id": "tgt-left-6",
  "status_contribution": "SOURCE_EVIDENCE_MISSING",
  "next_action": "Provide inspected source references or downgrade claim to UNKNOWN/INFERRED."
}
```

### 2) Mode-specific/generic mismatch

```json
{
  "diagnostic_id": "diag-002",
  "code": "SCOPE_MODE_SPECIFIC_ONLY",
  "severity": "ERROR",
  "message": "Mode-specific support cannot satisfy a generic backend requirement.",
  "claim_id": "selected_runtime_only_support",
  "source_refs": [
    {
      "path": "docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md",
      "note": "Mode-specific caveat baseline"
    }
  ],
  "target_id": "tgt-left-2",
  "status_contribution": "MODE_SCOPE_MISMATCH",
  "next_action": "Use a generic-source-backed claim or mark representability unknown/unsupported."
}
```

### 3) Neutral 5 unknown

```json
{
  "diagnostic_id": "diag-003",
  "code": "NEUTRAL5_UNKNOWN",
  "severity": "WARN",
  "message": "Neutral direction-5 support is unknown from current evidence.",
  "claim_id": "neutral_direction_5_support",
  "source_refs": [
    {
      "path": "docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md"
    }
  ],
  "target_id": "tgt-neutral-5",
  "status_contribution": "REPRESENTABILITY_UNKNOWN",
  "next_action": "Keep fail-closed status and require additional source audit before support claim."
}
```

### 4) Non-center neutral unknown

```json
{
  "diagnostic_id": "diag-004",
  "code": "NONCENTER_UNKNOWN",
  "severity": "WARN",
  "message": "Non-center neutral support is not proven by current source evidence.",
  "claim_id": "noncenter_neutral_support",
  "source_refs": [
    {
      "path": "docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md"
    }
  ],
  "target_id": "tgt-neutral-5-noncenter",
  "status_contribution": "REPRESENTABILITY_UNKNOWN",
  "next_action": "Do not assume non-center neutral capability without source-backed evidence."
}
```

### 5) Unsupported export

```json
{
  "diagnostic_id": "diag-005",
  "code": "EXPORT_UNSUPPORTED",
  "severity": "ERROR",
  "message": "Export intent requested, but export support is unsupported by current source evidence.",
  "claim_id": "export_support",
  "source_refs": [
    {
      "path": "docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md"
    }
  ],
  "target_id": "tgt-export-1",
  "status_contribution": "EXPORT_UNSUPPORTED",
  "next_action": "Keep export path disabled until explicit source-backed workflow exists."
}
```

### 6) Unsupported push

```json
{
  "diagnostic_id": "diag-006",
  "code": "PUSH_UNSUPPORTED",
  "severity": "ERROR",
  "message": "Push intent requested, but push support is unsupported by current source evidence.",
  "claim_id": "push_to_device_support",
  "source_refs": [
    {
      "path": "docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md"
    }
  ],
  "target_id": "tgt-push-1",
  "status_contribution": "PUSH_UNSUPPORTED",
  "next_action": "Keep push path out of scope until explicitly approved and source-backed."
}
```

### 7) Missing same-effective dataset

```json
{
  "diagnostic_id": "diag-007",
  "code": "MATCH_SAME_EFFECTIVE_DATASET_REQUIRED",
  "severity": "ERROR",
  "message": "Raw mismatch found and no Senscope equivalence dataset was supplied.",
  "claim_id": "same_effective_dataset_dependency",
  "source_refs": [
    {
      "path": "docs/project/G8_MOCK_EVALUATOR_CONTRACT.md"
    }
  ],
  "target_id": "tgt-left-3",
  "status_contribution": "RAW_MISMATCH",
  "next_action": "Return RAW_MISMATCH or UNKNOWN; do not emit SAME_EFFECTIVE_OUTPUT."
}
```

### 8) Semantic boundary out of scope

```json
{
  "diagnostic_id": "diag-008",
  "code": "SEMANTIC_BOUNDARY_OUT_OF_SCOPE",
  "severity": "ERROR",
  "message": "Request requires gameplay semantic interpretation, which is outside backend evaluator scope.",
  "claim_id": "semantic_boundary",
  "source_refs": [
    {
      "path": "docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md"
    }
  ],
  "target_id": "tgt-semantic-1",
  "status_contribution": "OUT_OF_SCOPE",
  "next_action": "Route to Senscope semantic authority layer, not backend capability evaluator."
}
```

## Deterministic diagnostic ordering

Emit and evaluate diagnostics in this fixed order:

1. Out-of-scope
2. Source evidence
3. Scope mismatch
4. Representability
5. Export/push
6. Same-effective dataset

This ordering supports deterministic, fail-closed triage and keeps controller/backend checks ahead of optional delivery workflows.

## Boundary reminders

1. Keep diagnostics focused on controller/backend capability evidence and evaluator scope.
2. Do not introduce gameplay semantic labels, thresholds, or behavior claims here.
3. Do not upgrade inferred or unknown claims to source-backed status without new source authority.
