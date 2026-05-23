# G11n Modifier-Mask Enablement Design

Status: design-only (not implemented)  
Branch: `proto/glyph-runtime-audit-modifier-design-g11m2-n-r`  
Boundary: no runtime modifier enablement in this batch.

## 1. Scope and non-goals

Scope:
- document a future path for active modifier-mask selection in `SenscopePrototype`;
- keep current selected runtime output behavior unchanged in this batch.

Non-goals:
- no runtime wiring in this batch;
- no default reachability changes;
- no `GameModeId` / protobuf / config-default activation;
- no gameplay semantics.

## 2. Current G11l behavior

- Current selected resolver request sets `active_modifier_mask = 0`.
- Left-stick coordinate resolution runs through existing G11c resolver path with that fixed mask.

## 3. Desired future behavior

- Build `active_modifier_mask` from selected physical/logical modifier inputs (three modifier bits).
- Feed computed `active_modifier_mask` into existing left-stick resolver request.
- Keep direction resolution in the same post-direction stage (no game-semantic interpretation).
- Preserve existing fallback behavior (`AllowHighestPrioritySubset` vs `RequireExactComboProfile` policy choice per request path).

## 4. Candidate modifier source mappings (examples only)

These are placeholders for discussion only, not approved bindings:

- Candidate A: map three dedicated left-hand physical inputs to modifier bits 0/1/2.
- Candidate B: map two physical inputs plus one logical role-derived bit to modifier bits 0/1/2.
- Candidate C: map three logical role outputs if physical bindings are unavailable.

Human/domain review is required before selecting real modifier sources.

## 5. Safety constraints

- Do not enable digital output behavior as part of modifier-mask wiring.
- Do not enable Force Up-B in the same batch.
- Do not enable right-stick/C-stick behavior.
- Do not introduce gameplay semantic mapping/thresholds.
- Do not alter default config or mode reachability.

## 6. Validation implications

- Exact duplicate combo masks are already rejected by validation diagnostics.
- Undefined combo handling should continue to surface no-match/subset fallback diagnostics.
- Any new modifier-mask helper should keep invalid/unknown mask handling explicit and source-backed.

## 7. Recommended future implementation stages

1. `G11n-impl1`: add helper to build active modifier mask (isolated, not wired to runtime output path).
2. `G11n-impl2`: wire active modifier mask into `SenscopePrototype` selected runtime resolver path after review/approval.
3. `G11p`: address Force Up-B path in a later separately approved batch.
