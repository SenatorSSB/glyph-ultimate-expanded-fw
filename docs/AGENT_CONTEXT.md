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
{"ready_ids":["GP-PROV-004","GP-PROV-005","GP-VAL-003","GP-CTL-001"],"immediate_ready":4,"recorded_preauthorized":0,"mechanically_activatable_preauthorized":0,"invalidated_preauthorized":0,"hardware_pending":0,"effective_authorized_runway":4,"target_effective_authorized_runway":4,"primary_liveness":"RUNWAY_OK","global_evidence_wait_supported":false}
<!-- current-runway:end -->

- The canonical executable queue is
  `docs/project/ACTIVE_AGENT_QUEUE.md`. Reviewed Planner packet
  `glyph-portfolio-20260827-1210` is partially consumed after independent
  curation.
  `GP-SRC-003` is DONE with prepared schema v2 carrying normalized
  input and deterministic artifact/manifest regeneration; earlier pushed tip
  `2b734b26439e9028717becf0010e345cb5efce6c` remains failed-review historical
  evidence and must not merge. `GP-SRC-004` is DONE; `GP-VAL-003` is reopened
  READY for its validation-health prose correspondence repair.
  `GP-SRC-005` is DONE after shared isolated-output and atomic-write hardening,
  and `GP-VAL-004` is DONE after its checker-only temporary-root repair.
  `GP-CONFIG-004` is DONE after its independently reviewed offline checker/docs
  correspondence repair; no real capture was performed.
  `GP-PROV-002` has a reviewed live feature tip at
  `9c94b5449b8065cb02aa0689ca0564720238b80c` and is DONE after exact
  integration into live configurator. `GP-CTL-002` is DONE after its exact
  implementation integration and separate completion publication.
  `GP-PROV-003` is DONE after its reviewed H0 implementation became a real
  canonical ancestor and received separate structured completion publication.
  `GP-PROV-004`, `GP-VAL-003`, and `GP-CTL-001` are reopened READY H0
  repair/revalidation work orders after direct current-source correspondence
  defects were confirmed. `GP-PROV-005` remains READY for `glyph_nuker`
  source-lineage research. The current-runway marker above is authoritative;
  recorded Preauthorization is zero and effective runway meets the target at
  four (`RUNWAY_OK`).
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
