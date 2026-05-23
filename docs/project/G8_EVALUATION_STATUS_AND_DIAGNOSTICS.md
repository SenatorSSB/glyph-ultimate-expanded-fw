# G8 - Evaluation Status and Diagnostics

Status: scaffold (docs-only taxonomy)
Date: 2026-05-23

## Status taxonomy

G8 uses conservative, contract-level statuses:

1. `EXACT_RAW_MATCH`: desired raw target and supported realized raw target are equal.
2. `SAME_EFFECTIVE_OUTPUT`: raw values differ, but supplied equivalence dataset proves same effective output.
3. `RAW_MISMATCH`: raw values differ and no accepted same-effective proof applies.
4. `REPRESENTABILITY_UNSUPPORTED`: request cannot be represented based on source-backed unsupported claim(s).
5. `REPRESENTABILITY_UNKNOWN`: representability cannot be proven from available evidence.
6. `SOURCE_EVIDENCE_MISSING`: required source evidence references are absent or insufficient.
7. `MODE_SCOPE_MISMATCH`: mode-specific support is presented where generic support is required.
8. `EXPORT_UNSUPPORTED`: export was requested but support is unsupported by current source evidence.
9. `PUSH_UNSUPPORTED`: push was requested but support is unsupported by current source evidence.
10. `OUT_OF_SCOPE`: request crosses scope boundary (for example game-semantic computation requests).

## Diagnostic code families

Recommended family prefixes:

1. Source evidence: `EVIDENCE_*`
2. Scope mismatch: `SCOPE_*`
3. Raw/effective matching: `MATCH_*`
4. Neutral direction 5: `NEUTRAL5_*`
5. Non-center neutral: `NONCENTER_*`
6. 9-way modifier table: `TABLE9_*`
7. Export: `EXPORT_*`
8. Push: `PUSH_*`
9. Game-semantic boundary: `SEMANTIC_BOUNDARY_*`

Example codes:

- `EVIDENCE_MISSING_REF`
- `SCOPE_MODE_SPECIFIC_ONLY`
- `MATCH_RAW_MISMATCH`
- `MATCH_SAME_EFFECTIVE_DATASET_REQUIRED`
- `NEUTRAL5_UNKNOWN`
- `NONCENTER_UNKNOWN`
- `TABLE9_UNSUPPORTED`
- `EXPORT_UNSUPPORTED`
- `PUSH_UNSUPPORTED`
- `SEMANTIC_BOUNDARY_OUT_OF_SCOPE`

## Deterministic evaluation ordering

Evaluation should proceed in a fail-closed sequence:

1. Reject out-of-scope and game-semantic requests.
2. Check source evidence presence and validity.
3. Check scope compatibility (generic vs mode-specific requirements).
4. Check representability (exact/raw support and known unsupported cases).
5. Check export/push support only when those intents are requested.
6. Check same-effective only when a supplied equivalence dataset is present.

## Fail-closed rules

1. `UNKNOWN` must not silently pass.
2. `INFERRED` must not be promoted to `SOURCE_BACKED`.
3. Mode-specific support must not be promoted to generic support.
4. Missing equivalence dataset must not produce `SAME_EFFECTIVE_OUTPUT`.
