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
- `CURRENT_BASELINE`: preserved current firmware/configurator baseline for
  comparison and non-claim tracking.
- `COMPLETE_USER_REPORTED_PASS_WITH_NUNCHUK_NOT_TESTED`: user-reported pass is
  recorded for all applicable non-nunchuk preservation rows, while nunchuk
  remains NOT_TESTED/unvalidated because the controller has no nunchuk port
  available out of the box.
- `READY_FOR_ENGINEERING_DESIGN`: scoped design/checker/contract work may
  proceed without user domain input.
- `READY_FOR_SOURCE_RESEARCH`: scoped source-authority or audit research may
  proceed without implementation.
- `READY_FOR_PROTOTYPE`: docs/tools or offline prototype work may proceed.
- `READY_FOR_USER_PRODUCT_DECISION`: implementation scope is ready to be chosen
  or prioritized, but source changes must wait for product approval.
- `WAITING_FOR_USER_ARTIFACT`: a specific user-provided artifact would improve
  or complete the item.
- `WAITING_FOR_HARDWARE_TEST`: a candidate/firmware artifact exists and a
  hardware result is required before the claim can advance.
- `FUTURE_PHASE`: not the current implementation phase; design/source research
  may still be allowed when scoped.
- `NOT_STARTED`: no current branch is active for the item.
- `FORBIDDEN_BY_POLICY`: disallowed by standing policy.
- `OFFICIAL_CORPUS_PRESENT_INITIAL`: official configurator export-shape corpus
  exists, but exact configurator metadata and write-behavior authority remain
  unresolved.
- `OUT_OF_SCOPE`: not part of this Glyph-side repository workstream.

Legacy `BLOCKED_*` labels in older calibration packets may mean user domain
input, product approval, source research, user artifact, hardware test,
implementation deferral, or policy restriction. Current entries keep status
separate from requirement booleans such as `requires_user_domain_input`,
`requires_user_product_approval`, `requires_source_research`,
`requires_hardware_test`, `requires_user_artifact`, `requires_firmware_change`,
`requires_safety_review`, `requires_schema_decision`, and
`requires_transport_authority`.

## Roadmap triage table

| Item | Status | Allowed next action | Requirements / notes |
| --- | --- | --- | --- |
| Native Ultimate Tilt/Tilt2 runtime baseline | `CURRENT_BASELINE` / `COMPLETE` | Preserve with docs/checkers only. | Source and prior docs record current native `MODE_ULTIMATE` baseline. |
| Tilt/Tilt2 hardware smoke evidence | `COMPLETE` | Preserve evidence; do not expand claims. | Current smoke result is not nunchuk validation. |
| Preservation hardware matrix execution | `COMPLETE_USER_REPORTED_PASS_WITH_NUNCHUK_NOT_TESTED` | Preserve the recorded result scope only. | User-reported pass is recorded for all applicable non-nunchuk preservation rows in `docs/calibration/glyph_ultimate_preservation_hardware_result.md` and `docs/calibration/fixtures/glyph_ultimate_preservation_hardware_result.json`; nunchuk remains NOT_TESTED/unvalidated because the controller has no nunchuk port available out of the box. No runtime-loaded config, WebSerial/device write, external remapper adapter, or active profile artifact change is claimed. |
| Capability and source-authority mapping | `COMPLETE` | Maintain docs/checkers if source paths drift. | Do not promote unknown behavior to fact. |
| Identity runtime role/case canonicalization | `COMPLETE` | Maintain evaluator/table sync only. | Future firmware behavior changes still require their own gate. |
| Export corpus capture | `WAITING_FOR_USER_ARTIFACT` / `OFFICIAL_CORPUS_PRESENT_INITIAL` | Provide missing official configurator metadata if available. | Official configurator corpus exists with two user-provided fixture files under `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/`. Exact configurator version/source reference, exact capture timestamp, and exact push/download route details remain unknown. This is not a blocker for routine engineering design. |
| Export corpus final blocker/status consolidation | `COMPLETE` | Preserve the blocker packet and its checker only. | Final blocker packet records `official_configurator_corpus_present_initial`, `corpus_present=true`, and `completion_allowed=false`; write-capable implementation remains blocked. |
| Adapter policy and prewrite validation | `READY_FOR_SOURCE_RESEARCH` | Maintain the blocker matrix and read-only policy/checkers; perform source audit planning. | Write-capable implementation requires source authority, license/code-reuse review, transport/runtime decisions, and product approval. |
| Adapter prewrite implementation gate | `READY_FOR_USER_PRODUCT_DECISION` | `docs_tools_only_source_audit_or_official_corpus_metadata` | Write-capable adapter implementation is not approved unless all blockers are cleared. `implementation_allowed=false`. Current blockers are official corpus metadata still missing, missing official configurator/source authority for write behavior, quarantined non-authoritative external observations, unsafe active-profile round-trip, runtime-owned behavior not safely represented in external JSON, WebSerial/device write blocked, runtime-loaded config blocked, protobuf binary write blocked, external source code reuse blocked, adapter output generation blocked, and implementation approval missing. |
| Physical/logical mapping and RF5 transcription | `READY_FOR_SOURCE_RESEARCH` | Maintain the RF5 gap index only, without changing mappings. | Printed RF5 transcription exists; old RF5 smoke row remains `NOT_TESTED_AMBIGUOUS` and must not be retconned. Later GFW3 RF5 evidence is scope-limited and does not rewrite the historical row. Domain input is needed only if the historical ambiguity must be resolved by user/domain statement. |
| Next user action handoff | `READY_FOR_USER_PRODUCT_DECISION` | Use only for specific user artifacts, prioritization, and approval gates. | `glyph_next_user_action_handoff_2026-06-06` no longer means routine engineering/source research is user-domain-blocked. It records optional official configurator metadata, prioritization choices, product approval before risky implementation, and hardware results only after a test artifact exists. No firmware implementation should start from this handoff alone. |
| Identity runtime generated-config prototype | `COMPLETE` | Maintain generated review artifacts/checkers only. | Prototype is not firmware input and not runtime-loaded config. |
| Generated-config/evaluator bridge | `READY_FOR_PROTOTYPE` | Connect Senscope neutral profile outputs to generated-config/evaluator artifacts. | `requires_user_domain_input=false`; design/prototype work may proceed when scoped to docs/tools and source-backed artifacts. |
| Generated C++ constants / firmware build path | `READY_FOR_ENGINEERING_DESIGN` | Define generated constants target and source-diff checker. | `requires_user_domain_input=false`; `requires_user_product_approval=true` before firmware implementation. |
| Offline official configurator export candidate | `READY_FOR_ENGINEERING_DESIGN` | Define export target contract and candidate validator. | Requires Senscope neutral profile and source-authority review before exporter implementation. |
| Runtime config candidate validator | `COMPLETE` | Maintain offline validator/corpus only. | Candidate validator is not runtime-loaded config implementation. |
| Stable firmware + bounded config-owned modifier data | `FUTURE_PHASE` | Architecture/spec branch if prioritized. | `requires_user_domain_input=false`; `requires_user_product_approval=true` before implementation. |
| Runtime-loaded config design and validation contract | `READY_FOR_ENGINEERING_DESIGN` | Continue docs/tools design validation only. | Implementation requires product approval, source authority, storage/interpreter decisions, and hardware plan. This is not user-domain-blocked. |
| External remapper boundary/source snapshot/config-shape/feasibility/mapping/gap/experiment items | `READY_FOR_SOURCE_RESEARCH` | Perform non-authoritative source audit or repeat no-device experiment with provenance. | Adapter implementation and external JSON generation require source authority, license/code-reuse review, and product approval; external observations are not official source authority. |
| GFW3 runtime remap hardware result | `COMPLETE` | Preserve result scope and checker. | User-reported pass applies to GFW3 runtime remap behavior only; nunchuk hardware validation not claimed. |
| Post-GFW3 configurator baseline/readiness | `COMPLETE` | Use as current `configurator` baseline for docs/tools routing. | Future behavior-changing work still needs branch/spec/checker/build/artifact/hardware/result/rollback/merge gate. |
| Runtime patch implementation branch | `READY_FOR_USER_PRODUCT_DECISION` | Draft source-backed spec/checker plan only after approval scope is explicit. | Any firmware behavior change requires explicit product approval, deterministic checker/fixture, build, hardware plan, result recording, rollback, and merge gate. |
| Senscope browser-app implementation work | `OUT_OF_SCOPE` | None in this repo. | This branch must not mutate the Senscope browser app workflow. |
| Nunchuk hardware validation claim | `OUT_OF_SCOPE` for current hardware | Create test plan/result template only if future hardware supports it and scope requests it. | No nunchuk hardware result exists; validation must not be claimed. Not a general implementation blocker. |
| Runtime-loaded config implementation | `FUTURE_PHASE` | Storage/representation/fallback design branch if prioritized. | `requires_user_domain_input=false`; `requires_user_product_approval=true` before implementation; `requires_source_research=true`. Runtime-loaded config is not implemented and not user-domain-blocked. |
| WebSerial/device write | `FUTURE_PHASE` | Source-authority/transport research branch if prioritized. | `requires_user_domain_input=false`; `requires_user_product_approval=true` before implementation; `requires_transport_authority=true`. WebSerial/device write is not implemented and not user-domain-blocked. |
| Protobuf binary write | `FUTURE_PHASE` | Official schema/transport research if prioritized. | `requires_user_domain_input=false`; `requires_user_product_approval=true` before implementation; `requires_source_research=true`. |
| Firmware flashing automation | `FORBIDDEN_BY_POLICY` | None. | Unsafe flashing automation and hidden device write remain forbidden. |
| External remapper adapter output | `FUTURE_PHASE` | Source audit, license/code-reuse review, and clean-room target contract if prioritized. | `requires_user_domain_input=false`; `requires_user_product_approval=true` before implementation. |
| External source code reuse | `FORBIDDEN_BY_POLICY` | None. | License review and explicit user approval are required before any reuse/dependency. |

## Gate keywords

- `adapter_implementation_blocked`
- `implementation_allowed=false`
- `docs_tools_only_source_audit_or_official_corpus_metadata`
- `write-capable adapter implementation is not approved unless all blockers are cleared`
- `explicit user approval after source authority exists`

## Recommended next queues

### Queue 1 - Safe docs/tools-only next work

- Roadmap/index/checker hardening.
- Official configurator corpus metadata packet if app version/source reference
  or exact capture route details become available.
- Preservation hardware packet refinement if no hardware result is claimed.
- Adapter prewrite blocker matrix maintenance if upstream blocker packets drift.
- Source-authority blocker packets.
- External remapper source-audit result packet that records non-authoritative
  findings without copying source or adding dependencies.

### Queue 2 - User artifact, prioritization, or approval gates

- Provide exact official configurator app version/source reference and capture
  route metadata if available.
- Choose/prioritize whether to start generated C++ constants path, export target
  contract, runtime-loaded config design, or transport source research.
- Approve before firmware behavior implementation, runtime-loaded config
  implementation, WebSerial/device write, protobuf binary write, external
  adapter output, or schema changes.
- Provide hardware test results only after a test artifact exists.
- Any nunchuk validation if future hardware/scope explicitly needs it.
- Any physical/logical role or chord-priority decision that depends on
  user/domain intent.

### Queue 3 - Future phase or forbidden by policy

- Future phase requiring product approval before implementation:
  runtime-loaded config, WebSerial/device write, protobuf binary write, and
  external-remapper adapter output.
- Forbidden by policy: macros, turbo, timing automation, hidden device write,
  unsafe firmware flashing automation, and external source reuse without
  license/source review.

## Future behavior-changing workflow gate

Any next behavior-changing firmware work still needs its own branch, spec,
deterministic checker or fixture, firmware build, build artifact inspection,
hardware test plan, user hardware result recording, post-result inspection,
rollback plan, and merge gate before merging back to `configurator`.

Runtime-loaded config, WebSerial/device write, protobuf binary write, and
external-remapper adapter output are future phases, not user-domain blockers.
They remain unimplemented and require future source authority plus explicit
product approval before implementation. Firmware flashing automation remains
forbidden by policy unless a future safety policy explicitly supersedes this
roadmap.
