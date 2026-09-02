# Agent Context

Status label: CURRENT.

Read this before using older calibration packets as roadmap input.

## Current Known-Good Branch State

- `configurator` now contains exact candidate
  `74ae24364b84520d4e0e39240beb9867653cc7b9` through integration commit
  `1597c01b416b6aa697d73efc7d2c2b3695dc3e5c`; UF2
  `5fadd3d7e82e629fbccd41fac868312b07b01e39d2ef0a0a98a06d649ae28254`
  is recorded as Revision-2 `HARDWARE_PASS` for the bounded
  sole/non-mode X1 offset-41 scope. The project owner reported all expected
  outputs and no disconnects, then confirmed the restored prior firmware
  worked. `GP-X1-001` is `DONE` with strict completion correspondence.
- `configurator` contains the full latest Y2 layout source-owned port after the
  recorded latest Y2 layout HARDWARE_PASS.
- The current approved Glyph realization path is source-owned table/routing
  source through the existing active RuntimeConfigView path.
- Active RuntimeConfigView selection is unchanged.
- `RuntimeConfigView` replacement is not used.
- Generated active wrappers are not used.
- `candidate.view` is not active.
- RAM-backed active table publication is not used.
- Source-owned table/routing source path passed hardware for the latest Y2
  layout.
- The Alternative B generated-table alias candidate at
  `ee5fd35c4ce00e31d9a00905c771699ad17517b9` is now recorded as
  HARDWARE_PASS when preserving the existing active RuntimeConfigView
  publication path.
- The current accepted baseline predates the Revision-2 exact artifact-identity
  contract. Missing legacy candidate/artifact identity is `UNKNOWN`; those
  reports cannot authorize any new or rebuilt candidate.
- The generated canonical-grid candidate at
  `e643017c1577c9ca2b94581fa6f18c0dfb1bac9b` is now recorded as
  HARDWARE_FAIL and must not merge. The failure concerns generated table
  content, not the already-proven Alternative B alias mechanism when
  source-aligned table content preserves the existing active publication path.
- The immediate mechanism supported by source/checker evidence is 26
  non-Y2/Tilt3 tables being canonical `0/128/255` grids instead of current
  source-owned contents; root cause remains unproven.
- Nunchuk remains NOT_TESTED.
- The low-level root cause remains unproven.

## Safe Implementation Boundary

Safe current work is docs/tools/checker work and source-owned realization
generator work that produces reviewable source-owned tables/routing source.
A complete `READY` H2/H3 work order inside the approved current path may be
implemented as a candidate when its substantive behavior and authority are
already resolved; behavior-changing firmware source deltas still require build
proof, source-backed review, and exact-snapshot hardware PASS before merge.
Unresolved behavior decisions and forbidden active-publication paths still stop
before implementation.

Do not implement runtime-loaded config, runtime-config storage, WebSerial/device
write, protobuf binary write, backend config write paths, or flashing
automation from this context document.

## Forbidden Active-Publication Paths

- `candidate.view` active publication.
- `active_storage.view` active publication.
- Generated active RuntimeConfigView wrappers.
- RuntimeConfigView replacement as the customization mechanism.
- RAM-backed active table publication.
- Runtime-loaded profile claims without separate design and hardware proof.
- Nunchuk validation claims.
- Root-cause claims.

## Forward Plan

<!-- current-runway:start -->
{"ready_ids":["GP-CTL-003","GP-PROV-008","GP-VAL-008"],"immediate_ready":3,"recorded_preauthorized":1,"mechanically_activatable_preauthorized":0,"invalidated_preauthorized":0,"hardware_pending":0,"effective_authorized_runway":3,"target_effective_authorized_runway":4,"primary_liveness":"RUNWAY_LOW","global_evidence_wait_supported":false}
<!-- current-runway:end -->

<!-- current-runway-summary:start -->
Ready IDs: GP-CTL-003, GP-PROV-008, GP-VAL-008; Immediate Ready: 3; Recorded Preauthorized: 1; Mechanically activatable Preauthorized: 0; Invalidated Preauthorized: 0; Hardware-pending: 0; Effective authorized runway: 3; Target effective authorized runway: 4; Primary liveness: RUNWAY_LOW
<!-- current-runway-summary:end -->

- The canonical executable queue is
  `docs/project/ACTIVE_AGENT_QUEUE.md`. Live-verified Planner packet
  `glyph-portfolio-20260901-0909` is partially consumed. Curator rebound both
  literally invalidated successors to the current snapshot, and `GP-VAL-012`
  and `GP-PROV-007` are completed with manifest sequencing preserved.
  Follow-up review corrected post-X1 survivor accounting, authorized
  `GP-CTL-003`, `GP-PROV-008`, and the bounded current `GP-VAL-008` X1
  regression lane, and Preauthorized `GP-BUILD-001` waiting on reviewed
  `GP-PROV-008` integration.
  The current-runway summary above is the authoritative executable order and
  liveness state. `GP-VAL-011`, `GP-CONFIG-005`, `GP-PERSIST-001`, and
  `GP-ART-001` retain substantive-dependency, research, or user-decision gates,
  but the packet does not support a portfolio-global evidence wait. Planner
  refresh is not requested while this partially consumed packet remains useful.
  Completed implementation history remains in the canonical queue. Bounded
  `glyph_nuker` research still leaves source lineage, purpose, byte
  transformation, build recipe, reproducibility, safety, artifact acceptance,
  and hardware UNKNOWN.
  The accepted X1 authority is the exact offset-41 `kX1Table` overlay recorded
  under `GLYPH-UD-010`, with hardware observation under `GLYPH-UD-012`; it
  owns no other table. `GP-CONFIG-002` is invalidated by `GLYPH-UD-007`; no
  official-configurator capture is required or awaited, and the retained
  corpus/templates are historical provenance.
  `GP-X1-001` is `DONE` for its exact Git/artifact pair after source-free PASS
  publication, exact-candidate integration, and accepted-baseline validation.
- Runtime-config validation now uses a full static checker census plus a
  curated runtime-config manifest. The census count is discovery-derived; the
  manifest, not a manual audit of every checker, owns current semantic gates.
- Maintain the source-owned Y2 layout baseline and current checkers.
- Harden the source-owned realization generator path for source-owned
  tables/routing source, starting with overlay/preserve candidate-generation
  semantics and checker enforcement. Candidate generation must use full
  replacement, overlay/preserve, or reject semantics and must not silently fill
  unspecified production tables with example/canonical defaults.
- The source-authority intake workflow is offline-only. The accepted canonical
  X1 record owns only `kX1Table` and preserves the immutable pre-change
  candidate baseline while validating its exact offset-41 points against the
  current accepted source. Any future X1 values or other table ownership
  remain separately gated.
- The former 27-table literal-body replacement generator contract is
  SUPERSEDED historical evidence; current authority is the 28-table baseline
  extraction, source-owned generator modes, and source-authority intake.
- Design coordinate-native runtime profile support separately.
- Treat browser/protobuf/persistence backend work as future infrastructure
  after the runtime model exists.
- Keep game semantics outside firmware.

## Evidence Map

- Current state: `docs/CURRENT_STATE.md`.
- Implementation boundary:
  `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`.
- Runtime-config surface: `docs/runtime_config/README.md`.
- Agent framework: `docs/agent_framework/README.md`.
- Authorization/runway: `docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md`.
- Executable queue: `docs/project/ACTIVE_AGENT_QUEUE.md`.
- Archive index: `docs/archive/README.md`.
- Calibration evidence index: `docs/calibration/INDEX.md`.
