# G11p/q/s Sequenced Design Notes

Status: docs-only batch summary

## Created docs

1. `docs/project/G11P_FORCE_UPB_RUNTIME_DESIGN.md`
2. `docs/project/G11Q_DIGITAL_OUTPUT_BEHAVIOR_DESIGN.md`
3. `docs/project/G11S_BINDING_UX_CONFIG_BOUNDARY_DESIGN.md`
4. `docs/project/G11P_Q_S_SEQUENCED_DESIGN_NOTES.md`

## Batch decisions

- This batch is docs-only.
- No runtime/default reachability changed.
- Force Up-B remains disabled.
- Digital outputs remain neutral.
- Debug/source-backed modifier bits remain `rf2` / `rf3` / `rf4`.
- Real binding UX/config remains deferred.

## Explicit deferrals

- Force Up-B implementation is deferred and requires separate user approval.
- Digital output implementation is deferred and requires separate user approval.
- No config/protobuf/default activation work was introduced.
- No export/push workflows were introduced.
- No hardware flashing workflow was introduced.
- No gameplay semantic labeling/threshold/source-authority claims were introduced.

## Recommended next choices

A. `G11p-impl-readiness` audit only, no Force Up-B implementation  
B. `G11q-impl-readiness` audit only, no digital implementation  
C. `G11u` selected-runtime invariant tests/self-test expansion  
D. `G8` software-side realization evaluator prototype, separate from firmware runtime
