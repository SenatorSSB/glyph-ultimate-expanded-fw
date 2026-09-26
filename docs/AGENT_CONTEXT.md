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
{"ready_ids":["GP-CONFIG-012","GP-CONFIG-013"],"immediate_ready":2,"recorded_preauthorized":0,"mechanically_activatable_preauthorized":0,"invalidated_preauthorized":0,"hardware_pending":0,"effective_authorized_runway":2,"target_effective_authorized_runway":4,"primary_liveness":"RUNWAY_LOW","global_evidence_wait_supported":false}
<!-- current-runway:end -->

<!-- current-runway-summary:start -->
Ready IDs: GP-CONFIG-012, GP-CONFIG-013; Immediate Ready: 2; Recorded Preauthorized: 0; Mechanically activatable Preauthorized: 0; Invalidated Preauthorized: 0; Hardware-pending: 0; Effective authorized runway: 2; Target effective authorized runway: 4; Primary liveness: RUNWAY_LOW
<!-- current-runway-summary:end -->

- GP-CONFIG-010 is `DONE`. Exact tested integration candidate `1c0ff22646729d26d45eacb4b8322c5baea7de48`, based on `22c639c31ea7006c18a29ec2693c8b18ff688ed4`, entered canonical through merge `50a6357eddf0d9c83d31233666c451806fb1f424`; narrow completion-control commit `7ca129e218b292c0aa64b38577848dd8b63a4c66` added only the three exact source-free protocol/result/evidence paths to the finite correspondence inventory. The physically passed artifact remains the preserved 791552-byte UF2 `4312f6a64fd1009e231aab2015e3ce67f862abd88a8ea31cd545db0e91e27476`. Required 13-profile capacity/reconnect checks, exact owner Config restoration, all nine GP-X1-002 rows, ordinary sanity, and final reconnect passed with empty evidence gaps. The original candidate `f4771e17430fd1ea3f1e3e5339a83dfe648290a3`, UF2 `9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a`, and immutable PASS remain distinct historical evidence. GP-VAL-015/027 retain critical precedence and unknown-path fail-closed behavior. The prior frozen-logo event remains unexplained and did not recur. GP-CONFIG-012 and GP-CONFIG-013 are READY for H1 characterization only. GP-CONFIG-014 is USER_DECISION_GATED: successful SetConfig can replace the live custom-mode count while an active mode retains its modifier-mask cache, so valid in-place replacement behavior needs an owner decision before H3 repair authorization. GP-VAL-011 remains deferred and GP-HW-002 remains research gated. Nunchuk remains NOT_TESTED and root cause remains unproven.
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
