# Agent Context

Status label: CURRENT.

Read this before using older calibration packets as roadmap input.

## Current Known-Good Branch State

- `GP-CONFIG-005` is `DONE`: exact candidate
  `437f87e8086a50f0dfbd834176b80d245c1ed307` entered `configurator` through
  `4e50be81716117022318d8dcdc7aa60c4390b605`, after reviewed GP-VAL-015
  correspondence repair and exact Revision-2 hardware PASS. Original UF2
  `650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44`
  remains the physically accepted artifact. The prior inconclusive persistence
  event remains separate; no disk-atomicity, recovery or rebuild-acceptance
  guarantee is added. Strict completion correspondence is published.
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
{"ready_ids":["GP-VAL-022","GP-CONFIG-009"],"immediate_ready":2,"recorded_preauthorized":1,"mechanically_activatable_preauthorized":1,"invalidated_preauthorized":0,"hardware_pending":0,"effective_authorized_runway":3,"target_effective_authorized_runway":4,"primary_liveness":"RUNWAY_LOW","global_evidence_wait_supported":false}
<!-- current-runway:end -->

<!-- current-runway-summary:start -->
Ready IDs: GP-VAL-022, GP-CONFIG-009; Immediate Ready: 2; Recorded Preauthorized: 1; Mechanically activatable Preauthorized: 1; Invalidated Preauthorized: 0; Hardware-pending: 0; Effective authorized runway: 3; Target effective authorized runway: 4; Primary liveness: RUNWAY_LOW
<!-- current-runway-summary:end -->

- The canonical executable queue is docs/project/ACTIVE_AGENT_QUEUE.md. Published packet glyph-portfolio-20260920-0227 has GP-VAL-021 DONE after exact reviewed integration; GP-VAL-022 and GP-CONFIG-009 remain READY; GP-VAL-023 is now mechanically ACTIVATABLE after the exact GP-VAL-021 integration. GP-PERSIST-003 remains RESEARCH_GATED on unresolved host fault semantics, target ABI correspondence, and dependency identity. The machine-derived markers above are authoritative. GP-VAL-011 remains REVIEW / OWNER_DEFERRED / NONEXECUTABLE. Existing DONE and hardware evidence remains unchanged. The next H2 realization still awaits owner/Senscope modifier/layout data and routing intent. Global evidence wait is unsupported.
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
