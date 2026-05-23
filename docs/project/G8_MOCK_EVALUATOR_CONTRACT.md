# G8 - Mock Evaluator Contract

Status: scaffold (mock-only, docs-only)
Date: 2026-05-23

## Scope note

This document defines conceptual contract shapes for mock evaluation only.
It is not a final API and not a runtime implementation commitment.

## Conceptual input/result shapes

The following names build on G5/G6 concepts but remain non-final:

```ts
type BackendCapabilityClaim = {
  capability_id: string;
  status:
    | "SOURCE_BACKED"
    | "INFERRED"
    | "UNKNOWN"
    | "UNSUPPORTED_BY_CURRENT_SOURCE";
  scope: "GENERIC_BACKEND" | "MODE_SPECIFIC";
  source_refs: string[];
  notes?: string[];
};

type NeutralProfileTargetSlice = {
  target_id: string;
  modifier_id: string;
  direction: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;
  desired_raw: { x: number; y: number };
  dataset_id?: string;
};

type RealizationEvaluationRequest = {
  intent: "REPRESENTABILITY" | "EXPORT" | "PUSH";
  required_scope: "GENERIC_BACKEND" | "MODE_SPECIFIC_OK";
  target: NeutralProfileTargetSlice;
  claims: BackendCapabilityClaim[];
  realized_raw?: { x: number; y: number };
  equivalence_dataset?: {
    dataset_id: string;
    mappings: Array<{
      desired_raw: { x: number; y: number };
      realized_raw: { x: number; y: number };
      effective_output_id: string;
    }>;
  };
};

type Diagnostic = {
  code: string;
  severity: "INFO" | "WARN" | "ERROR";
  message: string;
  source_refs?: string[];
  target_id?: string;
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
```

## Mock-only example cases

These fixtures are synthetic contract examples.
They are not Glyph runtime behavior claims.

### 1. Exact raw match

- Input: exact-raw support claim is `SOURCE_BACKED`; `realized_raw == desired_raw`.
- Result: `EXACT_RAW_MATCH`.

### 2. Unknown exact raw support

- Input: exact-raw support claim is `UNKNOWN`.
- Result: `REPRESENTABILITY_UNKNOWN` or `SOURCE_EVIDENCE_MISSING` (implementation choice must be explicit).

### 3. Unsupported full 9-way table

- Input: full 9-way table claim is `UNSUPPORTED_BY_CURRENT_SOURCE`.
- Result: `REPRESENTABILITY_UNSUPPORTED`.

### 4. Mode-specific support cannot satisfy generic requirement

- Input: claim is `SOURCE_BACKED` but `scope = MODE_SPECIFIC`; request requires `GENERIC_BACKEND`.
- Result: `MODE_SCOPE_MISMATCH` or `REPRESENTABILITY_UNKNOWN` (explicit rule required).

### 5. Direction 5 / non-center neutral unknown

- Input: target direction is `5` with non-center raw target; neutral-5 and non-center claims are `UNKNOWN`.
- Result: `REPRESENTABILITY_UNKNOWN`.

### 6. Export unsupported

- Input: request intent is `EXPORT`; export claim is `UNSUPPORTED_BY_CURRENT_SOURCE`.
- Result: `EXPORT_UNSUPPORTED`.

### 7. Push unsupported

- Input: request intent is `PUSH`; push claim is `UNSUPPORTED_BY_CURRENT_SOURCE`.
- Result: `PUSH_UNSUPPORTED`.

### 8. Same-effective requires supplied equivalence dataset

- Input: raw mismatch and no equivalence dataset supplied.
- Result: not `SAME_EFFECTIVE_OUTPUT`; return `RAW_MISMATCH` or `REPRESENTABILITY_UNKNOWN` with diagnostic requiring dataset.

### 9. Same-effective accepted only with supplied dataset proof

- Input: raw mismatch, but supplied dataset includes proof mapping desired and realized raw to same effective output id.
- Result: `SAME_EFFECTIVE_OUTPUT`.

## Boundary assertions

1. Mock fixtures are synthetic and must not be treated as runtime firmware facts.
2. The evaluator does not compute game semantics.
3. Same-effective outcomes require a Senscope-supplied equivalence dataset and traceable evidence.
