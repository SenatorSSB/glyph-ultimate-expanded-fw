# Glyph Current State

Status label: CURRENT. <!-- current-runway:start -->{"ready_ids":[],"immediate_ready":0,"recorded_preauthorized":0,"mechanically_activatable_preauthorized":0,"invalidated_preauthorized":0,"hardware_pending":0,"effective_authorized_runway":0,"target_effective_authorized_runway":4,"primary_liveness":"PLANNING_REQUIRED","global_evidence_wait_supported":false}<!-- current-runway:end -->

This is the short current-state entrypoint. Agents should read
`docs/AGENT_CONTEXT.md` first for the operating snapshot, then
`docs/runtime_config/IMPLEMENTATION_BOUNDARY.md` before proposing runtime-config
implementation work. Detailed historical evidence remains indexed from
`docs/archive/README.md` and `docs/calibration/INDEX.md`.
<!-- current-runway-summary:start -->
Ready IDs: ; Immediate Ready: 0; Recorded Preauthorized: 0; Mechanically activatable Preauthorized: 0; Invalidated Preauthorized: 0; Hardware-pending: 0; Effective authorized runway: 0; Target effective authorized runway: 4; Primary liveness: PLANNING_REQUIRED
<!-- current-runway-summary:end -->
**Current Agentic Operating State:** `docs/project/ACTIVE_AGENT_QUEUE.md` is canonical; `GP-VAL-006` is the sole Ready H1 work order after exact branch-correspondence and standalone-temporary-repository safety curation, so effective authorized runway is one and `RUNWAY_LOW` is current; packet `glyph-portfolio-20260827-1210` is consumed for further executable supply and a fresh broad Planner audit is requested; `GP-VAL-008` remains evidence gated, and `GP-ART-001` plus `GP-X1-001` remain user-decision gated; current validation is manifest v4 with 32 entries and 27 load-bearing checks before GP-VAL-006 implementation; `CUSTOM_RUNNER_NOT_REQUIRED`; retired official-configurator historical evidence: `tools/check_glyph_official_configurator_validation.py`; `GP-CONFIG-002` is invalidated and no operator capture is required; `GP-AUTH-001` is resolved by the sole-X1 production-authorized no-op intake; older import/export compatibility chain is historical-only; external-remapper evidence remains quarantined; no hardware wait or product/runtime claim is implied.
## Current Known-Good State

`PLANNING_REQUIRED` is not the current liveness state because `GP-VAL-006` is
Ready; a Planner refresh is nevertheless requested to restore runway after its
consumed packet supplied no other executable survivor.

- `configurator` contains the latest Y2 layout source-owned port after the
  recorded source-owned Y2 layout HARDWARE_PASS.
- Evidence is preserved in
  `docs/calibration/latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md`
  and its fixture.
- Pre-Revision-2 reports remain historical acceptance only for already-merged source; missing candidate/artifact identity is `UNKNOWN` and cannot satisfy a new/rebuilt candidate's exact-snapshot gate.
- The implementation lineage is
  `runtime-config-latest-y2-layout-source-owned-port`, with the recorded result
  branch `runtime-config-latest-y2-layout-source-owned-port-hardware-result`;
  the port is merge-approved after hardware PASS.
- The accepted user report is "everything works, all usual tests pass,
  including Up+A and Down+A".
- Active RuntimeConfigView selection remains unchanged: source-owned
  table/routing source remains the approved active Glyph realization path,
  `GetActiveRuntimeConfigState()` publishes the source-owned current baseline
  view, and `ResolveActiveRuntimeConfig()` remains the active lookup path.
- RuntimeConfigView replacement is not used, generated active wrapper is not
  used, `candidate.view` is not active, and RAM-backed active table publication
  is not used.
- Source-owned table/routing source path passed hardware for this layout.
- Alternative B generated-table aliasing is now hardware-passed for candidate
  commit `ee5fd35c4ce00e31d9a00905c771699ad17517b9` when preserving the
  existing active `RuntimeConfigView` publication path through
  `&kSourceOwnedCurrentBaselineRuntimeConfig`,
  `GetActiveRuntimeConfigState()`, and `ResolveActiveRuntimeConfig()`;
  evidence is recorded in
  `docs/calibration/alt_b_generated_table_alias_candidate_hardware_result_2026-07-09.md`; its missing artifact SHA-256 prevents reuse as Revision-2 acceptance.
- Prior active-publication HARDWARE_FAIL evidence remains archived evidence,
  not current work.
- Nunchuk remains NOT_TESTED; the low-level root cause remains unproven; the coordinate-native runtime profile contract now has a standalone repo-enforced profile validator, deterministic selection semantics, an offline dry-run evaluator, invalid/positive fixture corpora with expected results and failure reasons, and fixture-backed offline dry-run coverage for neutral, cardinal, diagonal, and Tilt3-aligned coordinate paths tied to current source-backed Y2/Tilt3 evidence.
- The current docs/checker queue also includes `docs/runtime_config/runtime_config_activation_alternatives_a_f.md` and `tools/check_glyph_runtime_config_activation_alternatives.py`, which classify A as currently hardware-passed, B as hardware-passed only for the source-owned generated-table alias candidate that preserves the active publication path, C-E as explicitly forbidden under current evidence, and F as future architecture only.
- The source-owned table symbol-map note and checker now document the current Alternative B alias/replacement boundary without changing the active publication path.
- Overlay/preserve generation is checker-enforced; unowned tables preserve the current source-owned baseline and production example provenance is rejected. The offline-only production-authorized X1 pilot owns exactly `kX1Table` and reproduces its exact current nine-point baseline, preserving all 28 active table contents and creating no hardware candidate.
- Generator modes are complete offline tooling with explicit modes, 28-row manifests, deterministic digests, stable exits, gates, and fixtures. The example remains `SOURCE_AUTHORITY_BLOCKER`; separately, the production-authorized X1 overlay owns only `kX1Table` with exact baseline-equivalent content. Its manifest is `NO_OP`, all 28 contents remain preserved, and no hardware candidate exists. The 27-table literal-body contract is SUPERSEDED; the 28-table baseline, generator modes, and intake are authoritative.

## Current Implementation Boundary

- Safe current path: source-owned realization generator work that produces source-owned tables/routing source for review, build, and hardware-gated firmware behavior changes.
- Safe offline source-owned layout-spec bridge path: `tools/convert_coordinate_native_profile_to_source_owned_spec.py` validates a supported coordinate-native profile fixture and emits the inert source-owned layout-spec packet consumed by `--emit-from-layout-spec`; the emitted layout spec stays offline-only and does not load into firmware.
- Safe offline coordinate-native pipeline packaging path: `tools/check_glyph_coordinate_native_runtime_profile_contract.py` now exposes `--check-offline-pipeline`, `--check-offline-artifact-bundle-manifest`, and `--check-offline-export-package` for the y2 fixture, offline bundle manifest, and offline export package. The fixtures stay provenance-only and do not imply runtime-loaded config, WebSerial/device write, persistent storage, or flashing automation.
- Current v0 production work remains source-owned firmware generation as v0: neutral/profile intent becomes generated source-owned tables/routing source, then a firmware build uses the existing active `RuntimeConfigView` path.
- Generated-source-owned packets and fixtures currently in scope include `generated_source_owned_realization_design.md`, `fixtures/generated_source_owned_realization_design.json`, `generated_source_owned_schema_scaffold.md`, `fixtures/generated_source_owned_schema_scaffold.json`, `generated_source_owned_generator_contract.md`, `fixtures/generated_source_owned_generator_contract.json`, `generated_source_owned_layout_spec.md`, `generated_source_owned_artifact_install.md`, `fixtures/generated_source_owned_artifact_install.json`, `generated_source_owned_baseline_artifact.md`, `fixtures/generated_source_owned_baseline_artifact.json`, and `GeneratedRuntimeConfigBaseline.current.hpp`.
- `generated_source_owned_generator_input.example.json`, `fixtures/generated_source_owned_layout_spec.example.json`, `generated_source_owned_layout_spec.json`, `--emit-current-source-owned-baseline`, the explicit `--emit-from-layout-spec` packet-input mode, `generated_outputs/generated_source_owned_runtime_config.example.hpp`, and `tools/generate_source_owned_runtime_config.py` remain the generator lane references.
- `tools/install_generated_source_owned_runtime_config.py` can preview or write only the inert `GeneratedRuntimeConfigArtifact.example.hpp` path through `--from-layout-spec` or `--from-generated-output`; it rejects `GeneratedRuntimeConfigBaseline.current.hpp`, which remains active compile-time table-content source through `UltimateIdentityRuntimeTables.hpp`. `GP-SRC-001` completed that fail-closed classification and write guardrail; `--dry-run` remains non-mutating.
- `tools/prepare_source_owned_candidate_branch.py` is non-mutating by default, and explicit `--write-source` is restricted to the inert example artifact path; it rejects the active table-content header and creates no current production authority.
- The candidate-generation diff diagnosis for `docs/runtime_config/fixtures/generated_source_owned_layout_spec.json` is currently classified `TABLE_CONTENT_DIFFERENT`: the candidate is not byte-for-byte equivalent to the source-owned baseline, `profile_name` drifts to `example_source_owned_runtime_config`, 26 tables collapse to the same canonical grid pattern, and `kY2Table` plus `kTilt3Table` remain source-aligned.
- The generated canonical-grid candidate at
  `e643017c1577c9ca2b94581fa6f18c0dfb1bac9b` is now recorded as
  HARDWARE_FAIL in
  `docs/calibration/generated_canonical_grid_candidate_hardware_result_2026-07-19.md`.
  The candidate branch must not merge. The failure concerns generated table
  content, not the already-proven Alternative B alias mechanism when
  source-aligned table content preserves the existing active publication path.
  The immediate mechanism supported by source/checker evidence is 26
  non-Y2/Tilt3 tables being canonical `0/128/255` grids instead of current
  source-owned contents; root cause remains unproven.
- Generated `RuntimeConfigView` wrappers, `candidate.view`, and RAM-backed active storage remain not wired active; `GeneratedRuntimeConfigBaseline.current.hpp` already supplies the 28 active compile-time table bodies through the source-owned include chain. Changing those bytes is H2 active firmware behavior work requiring source authority, build proof, an exact candidate/artifact pair, and hardware PASS before merge. Source-owned active-state preselection `HARDWARE_PASS` evidence, source-owned active-state `HARDWARE_PASS` evidence, and active-storage `HARDWARE_FAIL` evidence remain distinct. The phrase "generated tables not wired active" remains only as a checker navigation marker for inert/example lanes; future hardware gate required before generated source-owned tables are selected active for a behavior-changing candidate. `GP-SRC-001` completed the quarantine, and this does not describe the included current table-content header.
- Nunchuk `NOT_TESTED`.
- Forbidden current active-publication paths are documented in
  `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`.
- Runtime-loaded config is not implemented; runtime-config storage is not implemented; firmware binary/protobuf parser integration is not implemented; WebSerial/device write is not implemented; Protobuf binary write is not implemented; Firmware flashing automation is not implemented; external adapter output is not implemented.

## Forward Direction

- Next docs/tools direction: source-owned realization generator hardening.
- Current docs/checker queue includes activation-alternatives and
  source-owned table symbol-map claim-invariant hardening.
- Next safe queue: keep coordinate-native offline pipeline, bundle manifest,
  and export-package checks aligned with their fixtures.
- Future X1 values or other table ownership require separate explicit authority; a behavior-changing candidate must also pass the exact-candidate hardware lifecycle.
- Next design direction: coordinate-native runtime profile contract scaffolding, with separate design and hardware proof before any runtime-active implementation.
- Current contract scaffold packet: `docs/runtime_config/coordinate_native_runtime_profile_contract.md` with `docs/runtime_config/fixtures/coordinate_native_runtime_profile_contract.json`.
- Offline dry-run evaluator: `tools/dry_run_coordinate_native_runtime_profile.py` with fixture-backed positive and negative cases under `docs/runtime_config/fixtures/`.
- Browser/protobuf/persistence as future infrastructure is likely solvable, but it follows the runtime model and does not define the canonical profile.
- The neutral app-owned profile remains canonical; firmware remains a
  deterministic coordinate-output backend and must not own game semantics.

## Readiness

- Ready for docs/tools and checker work: yes.
- Ready for coordinate-native negative-corpus, positive-corpus, and validator follow-up work: yes,
  including deterministic selection semantics and offline dry-run fixtures.
- Ready for source-owned generator/evaluator design: yes, when source-backed and
  scoped outside active firmware behavior.
- Candidate-generation diff diagnosis is documented and executable; the current
  classification is `TABLE_CONTENT_DIFFERENT`, so this remains hardware-candidate
  material rather than a canonicalization-only branch.
- Current lane before active behavior: blocked until a selected activation
  strategy is implemented and hardware-gated.
- Hardware test required for this docs/checker cleanup: no.
- Hardware test required for future behavior-changing firmware source deltas:
  yes, before merge.
- Product approval required before runtime-loaded config, storage, device write, protobuf binary write, flashing automation, external adapter output, or neutral profile schema changes.

## Non-Claims

- No push-to-device behavior is implemented or claimed.
- No universal official configurator compatibility claim is made.
- No nunchuk validation is claimed.
- No root-cause claim is made.
- Older failed diagnostics are archived evidence, not current work.
