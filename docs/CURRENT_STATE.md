# Glyph Current State

Status label: CURRENT.

This is the concise current-state entrypoint for the Glyph/HayBox-side
firmware, configurator, and backend realization workstream. Detailed evidence
packets remain under `docs/calibration/`.

## Firmware Baseline

- GFW3 runtime remap work is merged, user hardware-tested, and recorded in
  `docs/calibration/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md`.
- Preservation hardware pass is recorded for applicable non-nunchuk scope in
  `docs/calibration/glyph_ultimate_preservation_hardware_result.md`.
- Phase 3 generated-like C++ constants firmware integration is merged and
  behavior-preserving for the current 27-table `StickPoint[9]` baseline in
  `docs/calibration/glyph_generated_constants_phase3_integration_hardware_result_2026-06-07.md`.
  The user-reported hardware pass is recorded for applicable doable non-nunchuk
  scope.
- Step 14 manual firmware-consuming runtime-config load is blocked before implementation.
- Step 15 source-authority research complete.
- Step 16 WebSerial/device-write implementation is blocked before implementation.
- Step 17 flashing automation is forbidden/not approved; safety boundary complete.
- Phase 6 bounded config-owned modifier-data architecture is complete as
  docs/spec/tooling only in
  `docs/runtime_config/phase6_bounded_config_owned_data_architecture.md`;
  runtime-loaded config, storage, firmware parser integration, WebSerial/device
  write, and flashing remain not implemented.
- Phase 7A hot-path parse-status guardrail is accepted in
  `docs/runtime_config/hot_path_parse_status_guardrail.md`: parser result state
  must not be read from `UpdateAnalogOutputs` or any analog hot-path resolver.
  Do not read parser result state from UpdateAnalogOutputs or analog hot-path resolver.
  The low-level failure mechanism is not proven, parsed table materialization
  remains deferred, and runtime-loaded config/storage/write/flashing remain not
  implemented.
- Active runtime config state contract is accepted in
  `docs/runtime_config/active_runtime_config_state_contract.md` as docs/tools
  design only. Future activation/selection may validate
  parser/materialization/load status before publishing a stable selected
  `RuntimeConfigView`; analog output generation may consume only
  ActiveRuntimeConfigState.active_view. Analog output generation must not branch
  on ActiveRuntimeConfigState.source or ActiveRuntimeConfigState.status.
- Source-owned active runtime config preselection is implemented in
  `runtime-active-config-state-source-owned-preselection` through
  `GetActiveRuntimeConfigState()` and `ResolveActiveRuntimeConfig()`.
- Its hardware result is recorded on
  `runtime-active-config-state-source-owned-preselection-hardware-result` as a
  `HARDWARE_PASS`; RF5, RF6, LT6, baseline, ordinary-direction, neutral,
  unrelated-buttons, modifiers, active-state, hot-path, and no-parser/
  no-parsed-tables/no-storage/no-write/no-flash rows passed, while Nunchuk
  remains NOT_TESTED.
- The source-owned active-state indirection is safe enough to serve as the repair-architecture basis for this scope.
- `runtime-active-config-state-source-owned-preselection` routes analog config
  lookup through the active selected view and remains parser-result and
  parsed-table-materialization free in the hot path.
- Step 18 public/manual workflow release-candidate hardware result is recorded for
  applicable doable scope in
  `docs/calibration/glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.md`;
  the plan/checklist remain plan-only and no public release or official
  configurator compatibility claim is made.
- Nunchuk remains NOT_TESTED / unvalidated / unavailable because the controller
  has no nunchuk port available out of the box.
- Runtime-loaded config, runtime-config storage, firmware binary/protobuf
  parser integration, WebSerial/device write, protobuf binary write, and
  firmware flashing automation remain not implemented.

## Official Configurator Corpus

- Official Glyph configurator corpus is present when
  `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`
  exists.
- The manifest records two user-provided JSON fixtures: default profiles and a
  back-and-forth custom profile.
- The exact official configurator app version, exact capture timestamp, and
  exact push/download route details may remain unknown.
- Offline official configurator export target contract work is docs/tools only
  and preview-only; it is grounded in the manifest and fixtures and does not
  claim production export or official compatibility.
- External-remapper docs are quarantined unless independently source-backed.

## Current Readiness Categories

- Complete/current baseline: GFW3 runtime remap, applicable non-nunchuk
  preservation evidence, and the Phase 3 generated-like C++ constants current
  baseline are recorded for their stated scopes.
- Ready for engineering design: generated-config/evaluator bridge work and
  offline export target contract design may proceed when scoped to docs/tools
  and source-backed artifacts.
- Ready for source research: transport/source-authority research, official
  configurator metadata capture, and external source audit planning may proceed
  when scoped and non-authoritative caveats remain intact.
- Waiting for user artifact: exact official configurator app version/source
  reference, exact capture timestamp, and exact push/download route metadata may
  be supplied if available, but the user is not currently blocking routine
  engineering design.
- Waiting for hardware artifacts: hardware tests are required only after a
  candidate or firmware artifact exists for that test scope. Nunchuk remains
  unvalidated for current hardware.
- Future phase requiring product approval before implementation:
  runtime-loaded config, runtime-config storage, firmware binary/protobuf
  parser integration, WebSerial/device write, protobuf binary write,
  firmware flashing automation, future generated constants source deltas,
  external adapter output, and Senscope neutral profile schema changes.
- Forbidden by policy: macros, turbo, timing automation, hidden device write,
  unsafe flashing automation, and external source reuse without license/source
  review.

The user is not currently blocking runtime-loaded config, WebSerial/device
write, protobuf binary write, or exporter work as a domain input matter. Those items are not implemented because they are future engineering, source-research, or product phases. The Phase 3 generated-like constants current baseline is merged and recorded; future generated constants deltas remain source-backed and gated.

Engineering design and source-research branches may proceed when prioritized
and scoped. Firmware behavior implementation, future generated constants
deltas, device-write implementation, runtime-loaded config implementation,
protobuf binary write, firmware flashing automation, external adapter output,
and schema changes still require explicit product approval before source
changes.

User domain input is required only for product/domain choices, not for routine
engineering decisions.

## Implementation State

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- Firmware binary/protobuf parser integration is not implemented.
- Phase 6 bounded config-owned modifier-data docs, fixtures, and checkers are
  complete for design review only.
- Phase 7A runtime hot-path parse-status guardrail is accepted as docs/tools
  guidance only; it implements no runtime-loaded config and changes no firmware
  behavior.
- Active runtime config state contract is accepted as docs/tools guidance only;
  it implements no runtime-loaded config, no parsed table materialization, no
  storage, no WebSerial/device write, and no flashing automation, and changes
  no firmware behavior.
- Source-owned active runtime config state preselection scaffold is now implemented
  in firmware source in `runtime-active-config-state-source-owned-preselection`;
  it does not alter RF5/RF6/LT6 expressions and keeps `UpdateDigitalOutputs`
  unchanged.
- WebSerial/device write is not implemented.
- Protobuf binary write is not implemented.
- Firmware flashing automation is not implemented.
- External adapter output is not implemented.

## Non-Claims

- No nunchuk validation is claimed.
- No universal official configurator compatibility claim is made.
- No direct device write is implemented or claimed.
- No runtime-loaded config, WebSerial/device write, protobuf binary write,
  firmware flashing automation, or external-remapper adapter output is
  implemented.
- No public release claim is made.
- Nunchuk remains NOT_TESTED unless explicitly validated.
- No Super Smash Bros. Ultimate game semantics are changed here.

## Practical Next Steps

- Continue Senscope neutral profile work outside this Glyph repo when that
  workflow is explicitly requested.
- Continue the generated-config/evaluator bridge inside this repo using
  source-backed firmware/controller evidence only.
- Maintain the generated constants/source-sync checkers and keep future
  generated constants deltas behind source-backed review, build, hardware
  plan/result, and approval gates.
- Consider an offline official-configurator export candidate only after the
  profile format exists and the source-authority gates are satisfied.
- Prepare `docs/release/public_manual_workflow_release_candidate_plan.md`,
  `docs/release/public_manual_workflow_release_candidate_checklist.md`, and the
  calibration hardware template before the next hardware run.
- Keep any later hardware result in a separate result branch and do not claim
  public release, official compatibility, or nunchuk validation until that
  result exists.
- Continue runtime-loaded config/transport research only as design/source
  research when explicitly prioritized.
