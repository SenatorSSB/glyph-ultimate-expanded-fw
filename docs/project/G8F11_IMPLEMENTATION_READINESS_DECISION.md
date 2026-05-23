# G8f11 - Implementation Readiness Decision

Status: docs-only decision input
Date: 2026-05-24

## Scope

This document is docs-only decision input, not implementation approval. It does not implement firmware behavior, app-side TypeScript, export/push/upload/flashing workflows, hardware flashing, default activation, config/protobuf changes, or gameplay semantic claims.

## Decision Options

| option | readiness | benefits | risks | blockers | required approvals | recommended model/tier |
| --- | --- | --- | --- | --- | --- | --- |
| A. Continue only app-side Senscope evaluator implementation | Ready to proceed separately | Uses handoff docs, can fail closed, avoids firmware behavior changes | Must preserve source-ref scope and avoid claiming runtime support | Senscope repo package target and fixture integration decisions | Senscope-side implementation approval only | Tier 2 for app evaluator with fail-closed tests |
| B. Implement a selected custom SenscopePrototype-style exact raw table mode in firmware | Conceptually plausible, not approved | Best fit for arbitrary exact raw table realization; aligns with source-backed prototype lineage and GC byte-carrying transport | Firmware behavior change, reachability/default/config hazards, profile authority questions | Explicit design approval; no reachability/default activation until reviewed; table/profile authority review | User/domain approval for firmware implementation and exact selected scope | Tier 3 ask-first for runtime implementation |
| C. Try to target existing CustomControllerMode | Not suitable for arbitrary exact raw profiles | Avoids new mode if limited scalar/range profiles are acceptable | Does not support arbitrary raw pair tables; numeric edge behavior needs tests; may create misleading evaluator claims | Need prove each profile fits range/scalar formulas; no generic exact table | Approval only for limited evaluator modeling, not generic exact support | Tier 2 for limited docs/evaluator analysis; Tier 3 for firmware/config changes |
| D. Investigate export/push/config generation first | Not ready as implementation path | Could eventually support user workflows after source-backed safety review | High risk of conflating device set command with approved push/export; hardware write and recovery issues | Export format, host transport, backup/restore, safety UX, schema authority, hardware evidence | Explicit export/push/user safety approval | Tier 3 ask-first |

## Recommended Conclusion

The conservative decision is:

- CustomControllerMode is not suitable for arbitrary exact raw neutral profiles.
- The GameCube transport path supports byte carrying once selected-mode outputs exist.
- Exact firmware realization likely requires a selected custom mode in the `SenscopePrototype` lineage or equivalent selected exact-table mode.
- Actual runtime firmware implementation requires explicit user approval.
- App-side evaluator implementation can proceed separately using the handoff docs and consolidated status table, with fail-closed behavior.

## Stop-Before Items For Any Implementation

Stop before:

- reachability/config/protobuf/default activation changes;
- adding `GameModeId`, `mode_id`, activation binding, or default mode config for Senscope runtime reachability;
- enabling Force Up-B;
- enabling digital output behavior;
- enabling right-stick/C-stick behavior;
- export/push/upload/flashing workflows;
- hardware flashing;
- gameplay semantic claims, labels, thresholds, or SSBU behavior claims;
- Senscope neutral profile schema changes.

## Next Possible Branches

1. Senscope app-side evaluator implementation.
2. Glyph-side selected custom mode implementation-readiness prompt, no reachability.
3. Glyph-side G11 selected runtime exact-table refinement, only if explicitly approved.
4. G12 hardware-delivery continuation only when artifact/recovery work resumes.

## Decision Notes

Option A is the lowest-risk next implementation direction because it consumes source-backed audits without changing firmware. It can classify exact raw realization as unsupported/unknown where source evidence is insufficient and can preserve the same-effective dataset dependency outside firmware semantics.

Option B is the likely firmware path if exact raw profile realization is approved. It should stay selected/custom and not become default-reachable until config, activation, safety, and recovery have their own review.

Option C should not be used to claim arbitrary exact support. It may support a limited scalar/range representability evaluator later, but only with precise caveats.

Option D should wait. Device-side set-config support is real, but export/push is a product/safety workflow, not a conclusion from command handlers alone.
