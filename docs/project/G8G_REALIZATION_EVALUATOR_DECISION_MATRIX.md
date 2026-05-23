# G8g - Realization Evaluator Decision Matrix

Status: docs-only conceptual decision artifact
Date: 2026-05-23

## Scope note

This document is docs-only and conceptual.

It defines deterministic evaluator decision behavior for neutral-target evaluation against backend claims, without runtime implementation.

It does not include gameplay thresholds or SSBU semantic labels.

## Deterministic matrix

| Condition | Required evidence | Output status | Diagnostics | Allowed next action | Forbidden inference |
| --- | --- | --- | --- | --- | --- |
| 1. Out-of-scope or game-semantic request | Request classification plus boundary rules from G3/G8 | `OUT_OF_SCOPE` | `SEMANTIC_BOUNDARY_*` | Reject evaluator path and route to semantic authority layer | Do not reinterpret semantic requests as backend capability checks |
| 2. Missing source refs for `SOURCE_BACKED` claim | Claim marked `SOURCE_BACKED` but empty/insufficient refs | `SOURCE_EVIDENCE_MISSING` | `EVIDENCE_MISSING_REF` | Downgrade claim or request refs before proceeding | Do not accept source-backed claim without refs |
| 3. `INFERRED` claim where `SOURCE_BACKED` is required | Requirement policy + claim status metadata | `REPRESENTABILITY_UNKNOWN` | `EVIDENCE_INFERRED_ONLY` | Keep fail-closed and continue audit backlog | Do not promote inferred to source-backed |
| 4. Unknown exact raw support | Exact-raw capability status is `UNKNOWN`/insufficient | `REPRESENTABILITY_UNKNOWN` | `GENERIC_CAPABILITY_UNKNOWN` or `EVIDENCE_*` | Return unknown with source-audit next step | Do not assume exact realizability |
| 5. Unsupported full 9-way table | 9-way capability marked `UNSUPPORTED_BY_CURRENT_SOURCE` | `REPRESENTABILITY_UNSUPPORTED` | `TABLE9_UNSUPPORTED` | Stop representability path for that requirement | Do not synthesize implicit 9-way generic table |
| 6. Mode-specific support but generic requirement | Claim scope is mode-specific; request requires generic | `MODE_SCOPE_MISMATCH` (or conservative unknown policy) | `SCOPE_MODE_SPECIFIC_ONLY` | Request generic-scope evidence or narrow requirement scope | Do not auto-promote mode-specific support to generic |
| 7. Exact raw match | Deterministic desired/raw comparison and valid capability evidence | `EXACT_RAW_MATCH` | `MATCH_*` info (optional) | Record success with trace refs | Do not over-generalize one success to universal support |
| 8. Raw mismatch without equivalence dataset | Deterministic mismatch and no dataset proof | `RAW_MISMATCH` | `MATCH_RAW_MISMATCH`, `MATCH_SAME_EFFECTIVE_DATASET_REQUIRED` | Report mismatch and request dataset only if same-effective requested | Do not emit same-effective without dataset |
| 9. Raw mismatch with supplied same-effective proof | Supplied dataset includes traceable mapping proof | `SAME_EFFECTIVE_OUTPUT` | `MATCH_SAME_EFFECTIVE_DATASET_MATCH` | Accept same-effective status with dataset trace | Do not derive equivalence from internal assumptions |
| 10. Export requested but unsupported | Export intent + unsupported/unknown export evidence | `EXPORT_UNSUPPORTED` | `EXPORT_UNSUPPORTED` | Defer export path pending explicit source-backed workflow | Do not infer export support from unrelated config transport |
| 11. Push requested but unsupported | Push intent + unsupported/unknown push workflow evidence | `PUSH_UNSUPPORTED` | `PUSH_UNSUPPORTED` | Defer push workflow pending explicit source-backed approval | Do not infer host push workflow from device-side primitives alone |

## Evaluation ordering notes

1. Semantic/out-of-scope first.
2. Evidence and scope before representability.
3. Export/push checks only when those intents are requested.
4. Same-effective only after dataset evidence is present.

## Implementation-boundary reminders

1. Keep all decisions fail-closed when evidence is incomplete.
2. Keep backend capability evaluation separate from gameplay semantics.
3. Preserve explicit source-ref traceability for non-unknown claims.
