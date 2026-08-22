# Glyph Current State

Status label: CURRENT.

This is the short current-state entrypoint. Agents should read
`docs/AGENT_CONTEXT.md` first for the operating snapshot, then
`docs/runtime_config/IMPLEMENTATION_BOUNDARY.md` before proposing runtime-config
implementation work. Detailed historical evidence remains indexed from
`docs/archive/README.md` and `docs/calibration/INDEX.md`.
**Current Agentic Operating State:** `docs/project/ACTIVE_AGENT_QUEUE.md` is canonical; Ready, Preauthorized, effective runway, and current hardware-pending counts are all zero; no trustworthy Planner packet exists; liveness is `PLANNING_REQUIRED`, not a global hardware wait; `CUSTOM_RUNNER_NOT_REQUIRED`; exact role configurations are in `docs/agent_framework/SCHEDULED_TASKS.md`.
## Current Known-Good State

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
- Overlay/preserve generation is checker-enforced; unowned tables preserve the current source-owned baseline and production example provenance is rejected; source-authority intake remains offline-only and records no real production approval.
- Generator modes are complete as offline tooling: `full_replacement`,
  `overlay_preserve`, and `reject_partial` have explicit semantics, complete
  28-row manifests, deterministic semantic digests, stable CLI exit codes,
  preparation/install gates, and fixture-backed regression coverage. No
  production profile has been authorized; the current example remains
  `SOURCE_AUTHORITY_BLOCKER`, and no hardware candidate was created; the old 27-table literal-body replacement contract is SUPERSEDED historical evidence, while the 28-table baseline extraction, generator modes, and source-authority intake are authoritative and this cleanup approves no production table ownership.

## Current Implementation Boundary

- Safe current path: source-owned realization generator work that produces source-owned tables/routing source for review, build, and hardware-gated firmware behavior changes.
- Safe offline source-owned layout-spec bridge path: `tools/convert_coordinate_native_profile_to_source_owned_spec.py` validates a supported coordinate-native profile fixture and emits the inert source-owned layout-spec packet consumed by `--emit-from-layout-spec`; the emitted layout spec stays offline-only and does not load into firmware.
- Safe offline coordinate-native pipeline packaging path: `tools/check_glyph_coordinate_native_runtime_profile_contract.py` now exposes `--check-offline-pipeline`, `--check-offline-artifact-bundle-manifest`, and `--check-offline-export-package` for the y2 fixture, offline bundle manifest, and offline export package. The fixtures stay provenance-only and do not imply runtime-loaded config, WebSerial/device write, persistent storage, or flashing automation.
- Current v0 production work remains source-owned firmware generation as v0: neutral/profile intent becomes generated source-owned tables/routing source, then a firmware build uses the existing active `RuntimeConfigView` path.
- Generated-source-owned packets and fixtures currently in scope include `generated_source_owned_realization_design.md`, `fixtures/generated_source_owned_realization_design.json`, `generated_source_owned_schema_scaffold.md`, `fixtures/generated_source_owned_schema_scaffold.json`, `generated_source_owned_generator_contract.md`, `fixtures/generated_source_owned_generator_contract.json`, `generated_source_owned_layout_spec.md`, `generated_source_owned_artifact_install.md`, `fixtures/generated_source_owned_artifact_install.json`, `generated_source_owned_baseline_artifact.md`, `fixtures/generated_source_owned_baseline_artifact.json`, and `GeneratedRuntimeConfigBaseline.current.hpp`.
- `generated_source_owned_generator_input.example.json`, `fixtures/generated_source_owned_layout_spec.example.json`, `generated_source_owned_layout_spec.json`, `--emit-current-source-owned-baseline`, the explicit `--emit-from-layout-spec` packet-input mode, `generated_outputs/generated_source_owned_runtime_config.example.hpp`, and `tools/generate_source_owned_runtime_config.py` remain the generator lane references.
- The offline install wrapper `tools/install_generated_source_owned_runtime_config.py` now covers the inert alias path with `--from-layout-spec`, `--from-generated-output`, and `--dry-run`; it stays offline-only and non-active.
- The offline candidate-prep wrapper `tools/prepare_source_owned_candidate_branch.py` now adds a dry-run plan for `runtime-config-install-workflow-candidate-generation` and keeps the approved inert Alternative B source path explicit without activating device-write or runtime-loaded behavior.
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
- The generated tables not wired active boundary remains intact; source-owned active-state preselection `HARDWARE_PASS` evidence, source-owned active-state `HARDWARE_PASS` evidence, and active-storage `HARDWARE_FAIL` evidence remain distinct. Future implementation must be hardware-gated if active source selection behavior changes; future hardware gate required before generated source-owned tables are selected active; future hardware gate required before generated source-owned baseline artifact is selected active.
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
- Next safe queue: obtain an explicit source-authorized owned-table set and
  replacement content. The completed offline generator must not be promoted to
  a production or hardware candidate without that authority.
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
