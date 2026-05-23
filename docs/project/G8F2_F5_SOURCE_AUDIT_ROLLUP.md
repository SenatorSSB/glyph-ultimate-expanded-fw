# G8f2-f5 Source Audit Rollup

Status: docs-only rollup
Date: 2026-05-23

## Created Docs

- `docs/project/G8F2_EXACT_RAW_LEFT_STICK_SOURCE_AUDIT.md`
- `docs/project/G8F3_MODE_SPECIFIC_VS_GENERIC_CAPABILITY_AUDIT.md`
- `docs/project/G8F4_OUTPUT_REPORT_PATH_AUDIT.md`
- `docs/project/G8F5_CAPABILITY_STATUS_UPDATE_RECOMMENDATIONS.md`
- `docs/project/G8F2_F5_SOURCE_AUDIT_ROLLUP.md`

## Guardrail Confirmation

This batch is docs-only.

No source/header/config/protobuf files changed.

No runtime/default reachability changed.

No Force Up-B behavior changed.

No digital output behavior changed.

No right-stick/C-stick behavior changed.

No export/push/flashing workflows were added.

No gameplay semantic claims were added.

No Senscope neutral profile schema changed.

## Main Conclusions

Source-backed:
- `OutputState` stores left-stick x/y as byte-shaped fields.
- Selected modes assign left-stick coordinate values.
- Ultimate and other official modes use mode-local formulas/constants for stick outputs.
- CustomControllerMode has config-driven selected-mode direction/range/modifier behavior.
- SenscopePrototype has a selected-only exact example-profile coordinate path.
- GameCube transport forwards selected mode left-stick bytes into GC report fields.

Remains inferred:
- Generic exact raw left-stick output support as a backend-level capability. The byte field and transport path exist, but source does not prove generic arbitrary target realization.

Remains unknown:
- Full CustomControllerMode representability for Senscope-style exact target sets.
- Non-center neutral support in active generic backend scope.
- Practical exactness after non-GC transport transforms beyond the formulas inspected here.
- Stable host/configurator exposure for exact arbitrary coordinate entry.

Unsupported by current source:
- Full 9-way generic directional modifier table support.
- Generic first-class neutral direction 5 support outside prototype-scoped structures.
- Approved export workflow.
- Approved push-to-device workflow.

Out of scope:
- Gameplay semantic equivalence.
- Senscope neutral profile schema changes.
- Runtime adapter implementation.

## Recommended Next Batches

A. G8f6 deeper audit of CustomControllerMode capability.

B. G8f7 deeper audit of transport-specific report serialization.

C. Senscope-side evaluator package decision.

D. G11p/G11q runtime implementation only after explicit user approval.

## Reviewer Merge Command

For reviewer use only after inspection approval:

```bash
git checkout configurator
git pull origin configurator
git merge --no-ff docs/g8f2-exact-raw-capability-source-audit --no-edit
git push origin configurator
```
