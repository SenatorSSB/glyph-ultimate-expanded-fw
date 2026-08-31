# Agent Context

Status label: CURRENT.

Read this before using older calibration packets as roadmap input.

## Current Known-Good Branch State

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
{"ready_ids":["GP-VAL-003","GP-VAL-009","GP-CTL-001"],"immediate_ready":3,"recorded_preauthorized":0,"mechanically_activatable_preauthorized":0,"invalidated_preauthorized":0,"hardware_pending":0,"effective_authorized_runway":3,"target_effective_authorized_runway":4,"primary_liveness":"RUNWAY_LOW","global_evidence_wait_supported":false}
<!-- current-runway:end -->

<!-- current-runway-summary:start -->
Ready IDs: GP-VAL-003, GP-VAL-009, GP-CTL-001; Immediate Ready: 3; Recorded Preauthorized: 0; Mechanically activatable Preauthorized: 0; Invalidated Preauthorized: 0; Hardware-pending: 0; Effective authorized runway: 3; Target effective authorized runway: 4; Primary liveness: RUNWAY_LOW
<!-- current-runway-summary:end -->

- The canonical executable queue is
  `docs/project/ACTIVE_AGENT_QUEUE.md`. Fresh live-verified Planner packet
  `glyph-portfolio-20260831-1540` is partially consumed after independent
  curation. The current-runway summary above is the authoritative executable
  order and liveness state. The packet retains reviewed non-executable supply,
  including one dependency/design-gated aggregate-isolation successor, one
  evidence-gated runtime-regression research item, and two user-decision-gated
  survivors. It does not support a portfolio-global evidence wait.
  Completed implementation history remains in the canonical queue. Bounded
  `glyph_nuker` research still leaves source lineage, purpose, byte
  transformation, build recipe, reproducibility, safety, artifact acceptance,
  and hardware UNKNOWN.
  The `GP-AUTH-001` user-decision gate is satisfied by the production-authorized
  baseline-equivalent `kX1Table` overlay intake recorded under `GLYPH-UD-008`;
  it owns no other table, changes no active bytes, and creates no hardware
  candidate. `GP-CONFIG-002` is invalidated by `GLYPH-UD-007`; no
  official-configurator capture is required or awaited, and the retained
  corpus/templates are historical provenance.
- Runtime-config validation now uses a full static checker census plus a
  curated runtime-config manifest. The census count is discovery-derived; the
  manifest, not a manual audit of every checker, owns current semantic gates.
- Maintain the source-owned Y2 layout baseline and current checkers.
- Harden the source-owned realization generator path for source-owned
  tables/routing source, starting with overlay/preserve candidate-generation
  semantics and checker enforcement. Candidate generation must use full
  replacement, overlay/preserve, or reject semantics and must not silently fill
  unspecified production tables with example/canonical defaults.
- The source-authority intake workflow is offline-only. The canonical X1 pilot
  authorizes only `kX1Table`, with its exact matching baseline points, before
  deterministic v2 generation. This no-op authority record creates no active
  table-byte delta or hardware candidate; any future X1 values or other table
  ownership remain separately gated.
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
