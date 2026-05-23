# G8i - Fixture-to-Evaluator Test Plan

Status: docs-only test-planning artifact
Date: 2026-05-23

## Scope note

This document is docs-only test planning, not implementation.

It defines synthetic test groups for a future Senscope-side evaluator that consumes capability fixtures and emits deterministic statuses/diagnostics.

## Test groups and synthetic cases

| Group | Synthetic fixture input | Request input | Expected status | Expected diagnostic code family |
| --- | --- | --- | --- | --- |
| 1. Source evidence validation | Claim marked `SOURCE_BACKED` with empty `source_refs` | Representability check for affected capability | `SOURCE_EVIDENCE_MISSING` | `EVIDENCE_*` |
| 2. Status propagation | Fixture has `UNKNOWN` exact-raw claim | Representability check requiring generic exact raw | `REPRESENTABILITY_UNKNOWN` | `EVIDENCE_*` or `GENERIC_*` |
| 3. Scope mismatch | Mode-scoped fixture claim only | Request requires `GENERIC_BACKEND` | `MODE_SCOPE_MISMATCH` | `SCOPE_*` |
| 4. Neutral direction 5 | Fixture marks `neutral_direction_5_support = UNKNOWN` | Target direction `5` | `REPRESENTABILITY_UNKNOWN` | `NEUTRAL5_*` |
| 5. Non-center neutral | Fixture marks `noncenter_neutral_support = UNKNOWN` | Direction `5` with non-center desired raw | `REPRESENTABILITY_UNKNOWN` | `NONCENTER_*` |
| 6. 9-way table support | Fixture marks full 9-way as `UNSUPPORTED_BY_CURRENT_SOURCE` | Request requiring full 9-way table realization | `REPRESENTABILITY_UNSUPPORTED` | `TABLE9_*` |
| 7. Exact raw match | Fixture allows exact raw path in scoped synthetic case | Desired raw equals realized raw | `EXACT_RAW_MATCH` | `MATCH_*` |
| 8. Raw mismatch | Same fixture but desired/raw differ | No equivalence dataset supplied | `RAW_MISMATCH` | `MATCH_*` |
| 9. Same-effective with dataset | Raw mismatch + supplied dataset mapping proof | Same-effective requested/allowed by policy | `SAME_EFFECTIVE_OUTPUT` | `MATCH_*` |
| 10. Same-effective without dataset | Raw mismatch and no dataset object | Same-effective fallback evaluated | `RAW_MISMATCH` or `REPRESENTABILITY_UNKNOWN` | `MATCH_*` |
| 11. Export unsupported | Fixture marks `export_support = UNSUPPORTED_BY_CURRENT_SOURCE` | Intent `EXPORT` | `EXPORT_UNSUPPORTED` | `EXPORT_*` |
| 12. Push unsupported | Fixture marks push workflow unsupported/unknown | Intent `PUSH` | `PUSH_UNSUPPORTED` | `PUSH_*` |
| 13. Semantic boundary rejection | Fixture may be otherwise valid | Request asks for gameplay-semantic interpretation | `OUT_OF_SCOPE` | `SEMANTIC_BOUNDARY_*` |

## Non-goals

1. No firmware tests.
2. No hardware tests.
3. No gameplay semantic tests.
4. No vendor export tests.
5. No push-to-device tests.

## Traceability notes

- Group-to-fixture mapping baseline: `docs/project/G8C_BACKEND_CAPABILITY_FIXTURE_DRAFT.md`.
- Group-to-diagnostic mapping baseline: `docs/project/G8D_SOURCE_REF_AND_DIAGNOSTIC_TRACE_DESIGN.md`.
- Group-to-decision-order/status baseline: `docs/project/G8G_REALIZATION_EVALUATOR_DECISION_MATRIX.md`.
