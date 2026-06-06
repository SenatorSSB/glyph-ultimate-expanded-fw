# Glyph Roadmap Next-Work Index - 2026-06-06

## Purpose and scope

This packet is a machine-checkable supervisor triage index for the Glyph /
HayBox-side firmware, configurator, and backend realization workstream after the
post-GFW3 `configurator` baseline.

Scope boundaries:

- This is docs/tools-only.
- This does not implement firmware behavior.
- This does not change firmware runtime behavior.
- This does not change active profile artifacts.
- This does not implement runtime-loaded config.
- This does not implement WebSerial/device write.
- This does not implement serial/device write behavior.
- This does not implement protobuf binary write.
- This does not implement firmware flashing automation.
- This does not implement an external remapper adapter or external-remapper-compatible JSON output.
- This does not copy external source code or add an external dependency.
- This does not claim nunchuk hardware validation.
- This does not touch Senscope browser app code.
- This does not change Super Smash Bros. Ultimate game semantics.

## Current baseline

- `configurator` has post-GFW3 baseline recorded.
- The GFW3 result is user-reported pass.
- The preservation hardware result is user-reported pass for applicable non-nunchuk scope.
- Nunchuk hardware validation not claimed.
- Runtime-loaded config not implemented.
- WebSerial/device write not implemented.
- External remapper adapter implementation not started.
- Active profile artifact change not required.

Primary baseline evidence:

- `docs/calibration/glyph_post_gfw3_configurator_baseline_2026-06-06.md`
- `docs/calibration/fixtures/glyph_post_gfw3_configurator_baseline_2026-06-06.json`
- `tools/check_glyph_post_gfw3_configurator_baseline.py`
- `docs/calibration/glyph_firmware_workstream_roadmap_2026-05-26.md`

## Status legend

- `COMPLETE`: current repo evidence records the docs/tools item or user-reported
  result as complete for its stated scope.
- `COMPLETE_USER_REPORTED_PASS_WITH_NUNCHUK_NOT_TESTED`: user-reported pass is
  recorded for all applicable non-nunchuk preservation rows, while nunchuk
  remains NOT_TESTED/unvalidated because the controller has no nunchuk port
  available out of the box.
- `READY_DOCS_TOOLS`: safe next work is limited to docs, fixtures, checkers,
  indexes, read-only validators, and source-auditable packets.
- `READY_CORPUS_CAPTURE`: protocol/checker exists; future work needs real
  captured corpus artifacts before completion claims.
- `BLOCKED_HARDWARE`: a hardware result is required before the claim can advance.
- `BLOCKED_USER_INPUT`: explicit user/domain input is required.
- `BLOCKED_SOURCE_AUTHORITY`: current source authority is insufficient.
- `BLOCKED_IMPLEMENTATION_APPROVAL`: implementation is not approved.
- `BLOCKED_EXTERNAL_AUDIT`: external source audit or license/code-reuse review is
  required before implementation can be proposed.
- `FORBIDDEN_WITHOUT_FUTURE_APPROVAL`: disallowed unless future source authority
  and explicit approval gates are satisfied.
- `OUT_OF_SCOPE`: not part of this Glyph-side repository workstream.

## Roadmap triage table

| Item | Status | Allowed next action | Blocked by / notes |
| --- | --- | --- | --- |
| Native Ultimate Tilt/Tilt2 runtime baseline | `COMPLETE` | Preserve with docs/checkers only. | Source and prior docs record current native `MODE_ULTIMATE` baseline. |
| Tilt/Tilt2 hardware smoke evidence | `COMPLETE` | Preserve evidence; do not expand claims. | Current smoke result is not nunchuk validation. |
| Preservation hardware matrix execution | `COMPLETE_USER_REPORTED_PASS_WITH_NUNCHUK_NOT_TESTED` | Preserve the recorded result scope only. | User-reported pass is recorded for all applicable non-nunchuk preservation rows in `docs/calibration/glyph_ultimate_preservation_hardware_result.md` and `docs/calibration/fixtures/glyph_ultimate_preservation_hardware_result.json`; nunchuk remains NOT_TESTED/unvalidated because the controller has no nunchuk port available out of the box. No runtime-loaded config, WebSerial/device write, external remapper adapter, or active profile artifact change is claimed. |
| Capability and source-authority mapping | `COMPLETE` | Maintain docs/checkers if source paths drift. | Do not promote unknown behavior to fact. |
| Identity runtime role/case canonicalization | `COMPLETE` | Maintain evaluator/table sync only. | Future firmware behavior changes still require their own gate. |
| Export corpus capture | `READY_CORPUS_CAPTURE` | Capture real matched-version corpus artifacts if available. | No real corpus manifest or fixture set is present under `docs/calibration/export_corpus/`. Export corpus readiness status records `blocked_missing_real_corpus_artifacts`, `corpus_present=false`, and `completion_allowed=false`. |
| Export corpus final blocker/status consolidation | `COMPLETE` | Preserve the blocker packet and its checker only. | Final blocker packet records that export corpus capture remains blocked by missing real corpus artifacts; the corpus root still contains only README guidance and no real manifest or fixture set. |
| Adapter policy and prewrite validation | `READY_DOCS_TOOLS` | Maintain the blocker matrix and read-only policy/checkers. | Write-capable adapter remains blocked by missing corpus, missing official configurator source authority, non-authoritative external observations, unsafe active-profile round-trip, WebSerial/device write blockers, runtime-loaded config blockers, protobuf binary write blockers, license/code-reuse blockers, and implementation approval. |
| Adapter prewrite implementation gate | `BLOCKED_IMPLEMENTATION_APPROVAL` | `docs_tools_only_source_audit_or_corpus_provision` | Write-capable adapter implementation is not approved unless all blockers are cleared. `implementation_allowed=false`. Current blockers are missing export corpus, missing official configurator source authority, non-authoritative external observations, unsafe active-profile round-trip, runtime-owned behavior not safely represented in external JSON, WebSerial/device write blocked, runtime-loaded config blocked, protobuf binary write blocked, external source code reuse blocked, adapter output generation blocked, and implementation approval missing. |
| Physical/logical mapping and RF5 transcription | `READY_DOCS_TOOLS` | Maintain the RF5 gap index only, without changing mappings. | Printed RF5 transcription exists; old RF5 smoke row remains `NOT_TESTED_AMBIGUOUS` and must not be retconned. Later GFW3 RF5 evidence is scope-limited and does not rewrite the historical row. |
| Next user action handoff | `BLOCKED_USER_INPUT` | Stop autonomous docs/tools sequence and wait for user action. | `glyph/gfw4-next-user-action-handoff` records `next_user_action_required`: provide real export corpus artifacts, provide source-authority approval or domain input as needed, and provide explicit implementation approval before behavior-changing work. The preservation hardware result is already recorded for applicable non-nunchuk scope; nunchuk remains NOT_TESTED/unvalidated. No firmware implementation should start from this handoff alone. |
| Identity runtime generated-config prototype | `COMPLETE` | Maintain generated review artifacts/checkers only. | Prototype is not firmware input and not runtime-loaded config. |
| Runtime config candidate validator | `COMPLETE` | Maintain offline validator/corpus only. | Candidate validator is not runtime-loaded config implementation. |
| Runtime-loaded config design and validation contract | `READY_DOCS_TOOLS` | Continue docs/tools design validation only. | Implementation remains blocked by user approval, source authority, storage/interpreter decisions, and hardware plan. |
| External remapper boundary/source snapshot/config-shape/feasibility/mapping/gap/experiment items | `BLOCKED_EXTERNAL_AUDIT` | Perform non-authoritative source audit or repeat no-device experiment with provenance. | Adapter implementation and external JSON generation remain blocked; external observations are not official source authority. |
| GFW3 runtime remap hardware result | `COMPLETE` | Preserve result scope and checker. | User-reported pass applies to GFW3 runtime remap behavior only; nunchuk hardware validation not claimed. |
| Post-GFW3 configurator baseline/readiness | `COMPLETE` | Use as current `configurator` baseline for docs/tools routing. | Future behavior-changing work still needs branch/spec/checker/build/artifact/hardware/result/rollback/merge gate. |
| Runtime patch implementation branch | `BLOCKED_IMPLEMENTATION_APPROVAL` | Draft source-backed spec/checker plan only after approval scope is explicit. | Any firmware behavior change requires explicit approval, deterministic checker/fixture, build, hardware plan, result recording, rollback, and merge gate. |
| Senscope browser-app implementation work | `OUT_OF_SCOPE` | None in this repo. | This branch must not mutate the Senscope browser app workflow. |
| Nunchuk hardware validation claim | `BLOCKED_HARDWARE` | Create test plan/result template only if requested. | No nunchuk hardware result exists; validation must not be claimed. |
| Runtime-loaded config implementation | `FORBIDDEN_WITHOUT_FUTURE_APPROVAL` | None in this branch. | Requires future source authority, explicit approval, deterministic checker/fixture, firmware build, hardware plan/result, rollback, and merge gate. |
| WebSerial/device write | `FORBIDDEN_WITHOUT_FUTURE_APPROVAL` | None in this branch. | Requires future source authority and explicit approval; not implemented. |
| Protobuf binary write | `FORBIDDEN_WITHOUT_FUTURE_APPROVAL` | None in this branch. | Requires official schema/transport authority and explicit approval; not implemented. |
| Firmware flashing automation | `FORBIDDEN_WITHOUT_FUTURE_APPROVAL` | None in this branch. | Push/flashing automation remains disallowed without future approval. |
| External remapper adapter output | `FORBIDDEN_WITHOUT_FUTURE_APPROVAL` | None in this branch. | Source audit, license/code-reuse review, clean-room implementation approval, and non-round-trip caveats are required first. |
| External source code reuse | `FORBIDDEN_WITHOUT_FUTURE_APPROVAL` | None in this branch. | License review and explicit user approval are required before any reuse/dependency. |

## Gate keywords

- `adapter_implementation_blocked`
- `implementation_allowed=false`
- `docs_tools_only_source_audit_or_corpus_provision`
- `write-capable adapter implementation is not approved unless all blockers are cleared`
- `explicit user approval after source authority exists`

## Recommended next queues

### Queue 1 - Safe docs/tools-only next work

- Roadmap/index/checker hardening.
- Export corpus readiness/capture packet if corpus files are available.
- Preservation hardware packet refinement if no hardware result is claimed.
- Adapter prewrite blocker matrix maintenance if upstream blocker packets drift.
- Source-authority blocker packets.
- External remapper source-audit result packet that records non-authoritative
  findings without copying source or adding dependencies.

### Queue 2 - Requires user/corpus/hardware

- Export corpus capture if source artifacts are not present.
- Next user action handoff follow-up: provide real export corpus artifacts,
  provide source-authority approval or domain input where needed, and provide
  explicit implementation approval before any behavior-changing branch. The
  preservation hardware result is already recorded for applicable non-nunchuk
  scope.
- Any behavior-changing runtime branch.
- Any nunchuk validation if a future scope explicitly needs it.
- Any physical/logical role or chord-priority decision that depends on
  user/domain intent.

### Queue 3 - Forbidden until future source authority and explicit approval

- Runtime-loaded config implementation.
- WebSerial/device write.
- Protobuf binary write.
- Firmware flashing automation.
- External-remapper adapter output.
- External source code reuse.

## Future behavior-changing workflow gate

Any next behavior-changing firmware work still needs its own branch, spec,
deterministic checker or fixture, firmware build, build artifact inspection,
hardware test plan, user hardware result recording, post-result inspection,
rollback plan, and merge gate before merging back to `configurator`.

Runtime-loaded config, WebSerial/device write, protobuf binary write, firmware flashing automation, and external-remapper adapter output remain blocked unless future source authority and explicit approval exist.
