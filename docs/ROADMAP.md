# Glyph Roadmap

Status label: CURRENT.

Read this as the current forward plan, not as a full history. Historical
diagnostics and failed branches are preserved through `docs/archive/README.md`
and `docs/calibration/INDEX.md`.

## Current Baseline

<!-- current-runway:start -->
{"ready_ids":[],"immediate_ready":0,"recorded_preauthorized":1,"mechanically_activatable_preauthorized":0,"invalidated_preauthorized":0,"hardware_pending":0,"effective_authorized_runway":0,"target_effective_authorized_runway":4,"primary_liveness":"CURATION_REQUIRED","global_evidence_wait_supported":false}
<!-- current-runway:end -->

The executable work runway is owned separately by
`docs/project/ACTIVE_AGENT_QUEUE.md`; roadmap status does not authorize
implementation. Reviewed Planner packet `glyph-portfolio-20260823-2349` is
partially consumed after fresh curation. `GP-SRC-003`, `GP-SRC-004`, and
`GP-CONFIG-004`, and `GP-VAL-003` are DONE on validated implementation branches;
`GP-SRC-005` is recorded
Preauthorized but WAITING. Pushed recovery tip
`2b734b26439e9028717becf0010e345cb5efce6c` failed independent review and is
not mergeable; `GP-SRC-003` now requires prepared schema v2 with carried
normalized input and deterministic artifact/manifest regeneration. Effective
runway is zero against target four (`CURATION_REQUIRED`). The current-runway marker above is
authoritative; user/source-authority and external-evidence gates do not
establish a portfolio-wide wait.

Runtime-config validation stabilization uses a deterministic repository-wide
checker census together with a curated runtime-config validation manifest. The
census detects checker-set drift mechanically; the curated manifest retains
the detailed current validation dependency graph and explicit evidence/unsafe
exclusions. This creates no production authority or hardware claim.

The official-configurator direction currently has one bounded offline lane at
`tools/check_glyph_official_configurator_validation.py`. It uses the primary
official corpus only; the older compatibility chain is historical-only and
external-remapper evidence remains quarantined.

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

These pre-Revision-2 hardware reports are preserved operational evidence for
the already-merged baseline. Any unrecorded candidate Git SHA or artifact
SHA-256 is `UNKNOWN`; legacy acceptance cannot satisfy, transfer to, or be
reused for a new/rebuilt candidate under the exact-snapshot gate.

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
- keep the candidate-prep wrapper and checker aligned with non-mutating dry-run
  plans and fail-closed refusal of unauthorized writes to the active
  Alternative B table-content header.
The candidate-generation diff diagnosis for the inert layout-spec fixture is
`TABLE_CONTENT_DIFFERENT`, with the candidate profile name and 26 table
records drifting from the current source-owned baseline while `kY2Table` and
`kTilt3Table` remain source-aligned.
The generated canonical-grid candidate at
`e643017c1577c9ca2b94581fa6f18c0dfb1bac9b` is now HARDWARE_FAIL and must not
merge. The failure concerns generated table content, not the already
hardware-passed Alternative B alias mechanism when source-aligned table
content preserves the existing active publication path.

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
- The source-authority intake workflow may record explicit human ownership and
  approval before generator v2 emission, but remains offline-only and cannot
  create a production candidate or hardware claim.
Generator lane references in scope:
`generated_source_owned_generator_input.example.json`,
`fixtures/generated_source_owned_layout_spec.example.json`,
`fixtures/generated_source_owned_layout_spec.json`,
`--emit-current-source-owned-baseline`,
the explicit `--emit-from-layout-spec` packet-input mode,
`generated_outputs/generated_source_owned_runtime_config.example.hpp`, and
`tools/generate_source_owned_runtime_config.py`.
The install wrapper `tools/install_generated_source_owned_runtime_config.py`
uses `--from-layout-spec`, `--from-generated-output`, and `--dry-run` to preview
or write only the inert `GeneratedRuntimeConfigArtifact.example.hpp` path. It
rejects `GeneratedRuntimeConfigBaseline.current.hpp`, which remains active
compile-time table-content source through `UltimateIdentityRuntimeTables.hpp`.
`GP-SRC-001` completed that fail-closed classification and write guardrail.
The candidate-prep wrapper `tools/prepare_source_owned_candidate_branch.py`
adds a dry-run plan for
`runtime-config-install-workflow-candidate-generation`. Its default plan is
non-mutating, while explicit `--write-source` is restricted to the inert
example artifact path and rejects the active table-content header; that route
creates no current production authority.
Next safe implementation branch should focus on overlay/preserve
candidate-generation semantics and checker enforcement: full replacement must
specify every active table, overlay/preserve must copy unspecified tables from
the current source-owned baseline, and partial input without that policy must
be rejected.
That contract is now implemented by the standalone overlay generator,
semantic comparator, and negative-corpus checker. The current example/layout-
spec input still has no explicit ownership declaration and is therefore a
`SOURCE_AUTHORITY_BLOCKER`, not a hardware candidate.

The complete generator-mode cycle is now complete as offline tooling in
`tools/source_owned_generator_modes.py` and its CLI/checker. The three modes,
explicit provenance, source-derived baseline identity, deterministic artifact
and manifest digests, preparation/install gates, stable exit codes, migration
refusal for ambiguous legacy input, and fixture-backed regression matrix are
implemented. This does not authorize a production profile, create a hardware
candidate, or change active source. The next blocker is an explicit
source-authorized owned-table set and replacement content. The former 27-table
literal-body replacement contract is SUPERSEDED historical evidence; current
28-table baseline extraction, generator modes, and source-authority intake are
authoritative. This cleanup creates no candidate and approves no production
table ownership.
The inert proof report is
`docs/runtime_config/generated_source_owned_overlay_preserve_proof_2026-07-19.md`.
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

Generated `RuntimeConfigView` wrappers, `candidate.view`, and RAM-backed active
storage remain not wired active. The generated baseline header is different:
it already supplies the active compile-time table bodies through the
source-owned include chain while preserving the existing source-owned active
publication path. The source-aligned Alternative B alias shape has historical
hardware PASS, but any new table-byte content needs its own source authority,
canonical build, exact candidate/artifact identity, and hardware PASS. The
source-owned active-state preselection `HARDWARE_PASS` evidence, source-owned
active-state `HARDWARE_PASS` evidence, and active-storage `HARDWARE_FAIL`
evidence remain distinct. The phrases "generated tables not wired active",
	"future hardware gate required before generated source-owned tables are
	selected active for a behavior-changing candidate" remains the current
	behavior-change gate; `GP-SRC-001` completed the inert/example quarantine,
	and it is not a claim that the included current table-content header is
	inert.
Nunchuk `NOT_TESTED`.
The candidate-generation diff diagnosis remains hardware-candidate material
because table contents differ rather than formatting alone.

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
