# Glyph Roadmap

Status label: CURRENT.

Read this as the current forward plan, not as a full history. Historical
diagnostics and failed branches are preserved through `docs/archive/README.md`
and `docs/calibration/INDEX.md`.

## Current Baseline

The current known-good firmware state is the latest Y2 layout source-owned port
merged into `configurator` after HARDWARE_PASS. The implementation lineage is
`runtime-config-latest-y2-layout-source-owned-port`, and the preserved hardware
result branch is
`runtime-config-latest-y2-layout-source-owned-port-hardware-result`.

The result is merge-approved after hardware PASS. The accepted user report is
"everything works, all usual tests pass, including Up+A and Down+A". Active
RuntimeConfigView selection remains unchanged, RuntimeConfigView replacement is
not used, generated active wrapper is not used, `candidate.view` is not active,
RAM-backed active table publication is not used, root cause remains unproven,
and Nunchuk remains NOT_TESTED.

Alternative B generated-table aliasing is now hardware-passed for candidate
commit `ee5fd35c4ce00e31d9a00905c771699ad17517b9` when it preserves the
existing active `RuntimeConfigView` publication path through
`&kSourceOwnedCurrentBaselineRuntimeConfig`, `GetActiveRuntimeConfigState()`,
and `ResolveActiveRuntimeConfig()`. This does not validate runtime-loaded
profiles, device-write flows, C/D/E active-publication paths, Nunchuk, or root
cause.

## Phase 0 - Preserve Current Source-Owned Firmware Baseline

Status: `CURRENT_BASELINE`.

Goal: preserve the known-good source-owned table/routing path and keep current
checkers aligned with the latest Y2 layout HARDWARE_PASS.

Next concrete action: keep `docs/AGENT_CONTEXT.md`,
`docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`, and the latest Y2 layout
checker current when evidence changes.

Stop conditions: unclear hardware scope, any new nunchuk claim, any root-cause
claim, or any behavior-changing firmware edit without hardware gate.

## Phase 1 - Source-Owned Realization Generator

Status: `READY_FOR_ENGINEERING_DESIGN`.

Goal: turn neutral/profile intent into generated source-owned tables/routing
source that can be reviewed, built, and hardware-tested through the existing
source-owned active path.

Next concrete action: harden the source-owned realization generator and its
fixtures/checkers while keeping output as reviewable source artifacts.
Current safe queue after the generator/checker hardening:
- keep the offline `--emit-from-layout-spec` smoke command documented;
- preserve branch-independent checker coverage for the generated-source-owned
  lane;
- keep the offline coordinate-native-to-source-owned layout-spec bridge
  converter checked and explicitly offline-only;
- keep the offline coordinate-native pipeline packaging commands
  (`--check-offline-pipeline`, `--check-offline-artifact-bundle-manifest`, and
  `--check-offline-export-package`) aligned with their fixtures;
- add an inert generated-source-owned artifact index only if future generator
  outputs need a stable catalog.
- keep the offline candidate-prep wrapper and checker aligned with the dry-run
  plan, refusal cases, and approved inert Alternative B source path.
The candidate-generation diff diagnosis for the inert layout-spec fixture is
`TABLE_CONTENT_EQUIVALENT` on this branch, because the materialized artifact
matches the generated candidate output fixture and all 28 tables now align
with the approved inert alias path.

Current generated-source-owned packets in scope:
`generated_source_owned_realization_design.md`,
`fixtures/generated_source_owned_realization_design.json`,
`generated_source_owned_schema_scaffold.md`,
`generated_source_owned_generator_contract.md`,
`generated_source_owned_layout_spec.md`,
`generated_source_owned_artifact_install.md`, and
`generated_source_owned_baseline_artifact.md`.
Current docs/checker addendum:
`docs/runtime_config/runtime_config_activation_alternatives_a_f.md` and
`tools/check_glyph_runtime_config_activation_alternatives.py` harden claim
language across A-F activation comparisons without approving any runtime path.
The same addendum keeps the current lane blocked before active behavior until a
selected activation strategy is implemented and hardware-gated.
- Next docs/tools detail: `docs/runtime_config/source_owned_table_symbol_map.md`
  plus `tools/check_glyph_source_owned_table_symbol_map.py` for the Alternative
  B alias/replacement boundary.
Generator lane references in scope:
`generated_source_owned_generator_input.example.json`,
`fixtures/generated_source_owned_layout_spec.example.json`,
`fixtures/generated_source_owned_layout_spec.json`,
`--emit-current-source-owned-baseline`,
the explicit `--emit-from-layout-spec` packet-input mode,
`generated_outputs/generated_source_owned_runtime_config.example.hpp`, and
`tools/generate_source_owned_runtime_config.py`.
The offline install wrapper `tools/install_generated_source_owned_runtime_config.py` uses `--from-layout-spec`, `--from-generated-output`, and `--dry-run` to preview or write the inert alias path without changing active behavior.
The candidate-prep wrapper `tools/prepare_source_owned_candidate_branch.py`
adds a dry-run plan for
`runtime-config-install-workflow-candidate-generation`, keeping the approved
inert Alternative B source path explicit and refusing direct writes on
`configurator`.
The normal generator input now requires `layout_spec`, so spec-less JSON is
rejected.
Related fixtures in scope:
`fixtures/generated_source_owned_schema_scaffold.json`,
`fixtures/generated_source_owned_generator_contract.json`,
`fixtures/generated_source_owned_layout_spec.json`,
`fixtures/generated_source_owned_artifact_install.json`, and
`fixtures/generated_source_owned_baseline_artifact.json`.

Boundary: this phase may generate source text or docs fixtures, but it must not
replace the active RuntimeConfigView, publish `candidate.view`, publish
RAM-backed active table storage, introduce runtime-loaded config, or add
storage/write/flashing paths. The declarative layout spec mirror stays inert
and only validates the current source-owned baseline shape. Future
implementation must be hardware-gated if active source selection behavior
changes.

The generated tables not wired active boundary remains intact except for the
Alternative B generated-table alias candidate shape that preserves the existing
active publication path and is now hardware-passed. The source-owned
active-state preselection `HARDWARE_PASS` evidence and active-storage
`HARDWARE_FAIL` evidence remain distinct; any different future generated
source-owned table selection still needs its own source authority, build proof,
and hardware gate.
future hardware gate required before generated source-owned tables are selected
active. source-owned active-state `HARDWARE_PASS` evidence and
`GeneratedRuntimeConfigBaseline.current.hpp` remain part of this lane.
future hardware gate required before generated source-owned baseline artifact
is selected active.
Nunchuk `NOT_TESTED`.
The candidate-generation diff diagnosis now reflects the materialized inert
alias-path branch rather than a drift-only diagnostic packet.

## Phase 2 - Coordinate-Native Runtime Profile Contract Scaffolding

Status: `READY_FOR_ENGINEERING_DESIGN`, implementation deferred.

Goal: design coordinate-native runtime profile contract scaffolding around the
primitive `active role/modifier state + resolved direction key 1..9 -> exact
raw coordinate`, including neutral 5, full 9-way asymmetry, explicit
routing/sublayers/priorities, and deterministic selection semantics.

Current v0 production remains source-owned firmware generation as v0 until a
coordinate-native runtime profile has separate design, source authority, build
proof, and hardware proof.

Current contract scaffold packet:
`docs/runtime_config/coordinate_native_runtime_profile_contract.md` with
`docs/runtime_config/fixtures/coordinate_native_runtime_profile_contract.json`.
The packet now includes machine-readable input-state, tie, missing-table, side-
effect merge, and trace/explanation rules plus annotated future dry-run
examples.

Current repo-enforced tooling for this lane includes:

- `python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py`
- `python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py --validate-profile <path>`
- `python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py --check-negative-fixtures`

The source-owned Y2 layout HARDWARE_PASS and prior active-publication
HARDWARE_FAIL evidence are the evidence base for this plan. The future target
is a coordinate-native runtime profile. Browser/protobuf/persistence as future
infrastructure is likely solvable, but the neutral app-owned profile remains
canonical and firmware-independent. Firmware should not own game semantics.
The Y2-inspired sketch now has fixture-backed offline dry-run coverage for the
neutral, cardinal, diagonal, and Tilt3-aligned coordinate paths, tied to the
current source-backed Y2/Tilt3 evidence and still kept offline-only.

The offline dry-run evaluator for this lane is now implemented as tooling only:
`tools/dry_run_coordinate_native_runtime_profile.py` with fixture-backed
positive and negative cases under `docs/runtime_config/fixtures/`. The
generated result is not loaded by firmware, runtime-loaded config remains not
implemented, and there is no WebSerial/device write, no persistence/storage,
no flashing automation, and no active RuntimeConfigView publication.

Stop conditions: runtime-loaded profile claims, active publication changes,
neutral profile schema changes, or game-semantic claims without explicit
approval and source authority.

Next safe queue: keep the invalid corpus and standalone validator aligned with
the contract text; keep the deterministic selection semantics and
`future_dry_run_examples` annotations aligned; keep the offline dry-run
evaluator and checker-driven fixture corpus aligned. The offline resolver
runtime path remains a future implementation task, but its selection contract
is now documented and checker-enforced.

## Phase 3 - Future Browser/Protobuf/Persistence Backend

Status: `FUTURE_PHASE`.

Goal: after the runtime model exists, design browser/protobuf/persistence
backend infrastructure for moving a bounded runtime profile safely.

Next concrete action: none until the coordinate-native runtime profile design is
reviewed and a hardware-proof strategy exists.

Boundary: no WebSerial/device write, protobuf binary write, persistent
runtime-config storage, backend/config.pb write path, or firmware flashing
automation is implemented or approved by this roadmap.

## Archived Diagnostics

Archived failed implementation diagnostics remain important evidence, but they
are not current work. Start from `docs/archive/README.md` for the concise map,
then open the original packets only when needed.
