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

Current generated-source-owned packets in scope:
`generated_source_owned_realization_design.md`,
`fixtures/generated_source_owned_realization_design.json`,
`generated_source_owned_schema_scaffold.md`,
`generated_source_owned_generator_contract.md`,
`generated_source_owned_layout_spec.md`,
`generated_source_owned_artifact_install.md`, and
`generated_source_owned_baseline_artifact.md`.
Generator lane references in scope:
`generated_source_owned_generator_input.example.json`,
`fixtures/generated_source_owned_layout_spec.example.json`,
`fixtures/generated_source_owned_layout_spec.json`,
`--emit-current-source-owned-baseline`,
the explicit `--emit-from-layout-spec` packet-input mode,
`generated_outputs/generated_source_owned_runtime_config.example.hpp`, and
`tools/generate_source_owned_runtime_config.py`.
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

The generated tables not wired active boundary remains intact, the source-owned
active-state preselection `HARDWARE_PASS` evidence and active-storage
`HARDWARE_FAIL` evidence remain distinct, and a future hardware gate is
required before generated source-owned tables are selected active.
future hardware gate required before generated source-owned tables are selected
active. source-owned active-state `HARDWARE_PASS` evidence and
`GeneratedRuntimeConfigBaseline.current.hpp` remain part of this lane.
future hardware gate required before generated source-owned baseline artifact
is selected active.
Nunchuk `NOT_TESTED`.

## Phase 2 - Coordinate-Native Runtime Profile Design

Status: `READY_FOR_ENGINEERING_DESIGN`, implementation deferred.

Goal: design coordinate-native runtime profile support around the primitive
`active role/modifier state + resolved direction key 1..9 -> exact raw
coordinate`, including neutral 5, full 9-way asymmetry, and explicit
routing/sublayers/priorities.

Current v0 production remains source-owned firmware generation as v0 until a
coordinate-native runtime profile has separate design, source authority, build
proof, and hardware proof.

The source-owned Y2 layout HARDWARE_PASS and prior active-publication
HARDWARE_FAIL evidence are the evidence base for this plan. The future target
is a coordinate-native runtime profile. Browser/protobuf/persistence as future
infrastructure is likely solvable, but the neutral app-owned profile remains
canonical and firmware-independent. Firmware should not own game semantics.

Stop conditions: runtime-loaded profile claims, active publication changes,
neutral profile schema changes, or game-semantic claims without explicit
approval and source authority.

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
