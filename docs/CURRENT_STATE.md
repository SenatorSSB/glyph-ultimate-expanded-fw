# Glyph Current State

Status label: CURRENT.

This is the short current-state entrypoint. Agents should read
`docs/AGENT_CONTEXT.md` first for the operating snapshot, then
`docs/runtime_config/IMPLEMENTATION_BOUNDARY.md` before proposing runtime-config
implementation work. Detailed historical evidence remains indexed from
`docs/archive/README.md` and `docs/calibration/INDEX.md`.

## Current Known-Good State

- `configurator` contains the latest Y2 layout source-owned port after the
  recorded source-owned Y2 layout HARDWARE_PASS.
- Evidence is preserved in
  `docs/calibration/latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md`
  and its fixture.
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
- Prior active-publication HARDWARE_FAIL evidence remains archived evidence,
  not current work.
- Nunchuk remains NOT_TESTED.
- The low-level root cause remains unproven.

## Current Implementation Boundary

- Safe current path: source-owned realization generator work that produces
  source-owned tables/routing source for review, build, and hardware-gated
  firmware behavior changes.
- Current v0 production work remains source-owned firmware generation as v0:
  neutral/profile intent becomes generated source-owned tables/routing source,
  then a firmware build uses the existing active `RuntimeConfigView` path.
- Generated-source-owned packets currently in scope:
  `generated_source_owned_realization_design.md`,
  `generated_source_owned_schema_scaffold.md`,
  `generated_source_owned_generator_contract.md`,
  `generated_source_owned_layout_spec.md`,
  `generated_source_owned_artifact_install.md`, and
  `generated_source_owned_baseline_artifact.md`,
  `GeneratedRuntimeConfigBaseline.current.hpp`.
- Related fixtures currently in scope:
  `fixtures/generated_source_owned_realization_design.json`,
  `fixtures/generated_source_owned_schema_scaffold.json`,
  `fixtures/generated_source_owned_generator_contract.json`,
  `fixtures/generated_source_owned_layout_spec.json`,
  `fixtures/generated_source_owned_artifact_install.json`, and
  `fixtures/generated_source_owned_baseline_artifact.json`.
- `generated_source_owned_generator_input.example.json`,
  `fixtures/generated_source_owned_layout_spec.example.json`,
  `generated_source_owned_layout_spec.json`,
  `--emit-current-source-owned-baseline`,
  the explicit `--emit-from-layout-spec` packet-input mode,
  `generated_outputs/generated_source_owned_runtime_config.example.hpp`, and
  `tools/generate_source_owned_runtime_config.py` remain the generator lane
  references.
- The generated tables not wired active boundary remains intact; source-owned
  active-state preselection `HARDWARE_PASS` evidence and active-storage
  `HARDWARE_FAIL` evidence remain distinct. source-owned active-state
  `HARDWARE_PASS` evidence and future hardware gate required before generated
  source-owned baseline artifact is selected active remain part of this lane.
  The declarative layout spec mirror stays inert and only validates the current
  source-owned baseline shape. The normal generator input now requires
  `layout_spec`, and the explicit `--emit-from-layout-spec` mode stays inert.
  Future implementation must be hardware-gated if active source selection
  behavior changes.
- future hardware gate required before generated source-owned tables are
  selected active.
- nunchuk `NOT_TESTED`.
- Forbidden current active-publication paths are documented in
  `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`.
- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- Firmware binary/protobuf parser integration is not implemented.
- WebSerial/device write is not implemented.
- Protobuf binary write is not implemented.
- Firmware flashing automation is not implemented.
- External adapter output is not implemented.

## Forward Direction

- Next docs/tools direction: source-owned realization generator hardening.
- Next safe queue: keep the offline generator smoke command documented and maintain branch-independent checker coverage; consider an inert generated-source-owned artifact index only if it helps future generator outputs.
- Next design direction: coordinate-native runtime profile contract scaffolding, with separate design and hardware proof before any runtime-active implementation.
- Current contract scaffold packet: `docs/runtime_config/coordinate_native_runtime_profile_contract.md` with `docs/runtime_config/fixtures/coordinate_native_runtime_profile_contract.json`.
- Browser/protobuf/persistence as future infrastructure is likely solvable, but it follows the runtime model and does not define the canonical profile.
- The neutral app-owned profile remains canonical; firmware remains a
  deterministic coordinate-output backend and must not own game semantics.

## Readiness

- Ready for docs/tools and checker work: yes.
- Ready for source-owned generator/evaluator design: yes, when source-backed and
  scoped outside active firmware behavior.
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
