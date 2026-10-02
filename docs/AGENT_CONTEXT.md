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
{"ready_ids":["GP-CONFIG-020","GP-VAL-036","GP-KBD-001","GP-CONFIG-019"],"immediate_ready":4,"recorded_preauthorized":11,"mechanically_activatable_preauthorized":0,"invalidated_preauthorized":0,"hardware_pending":0,"effective_authorized_runway":4,"target_effective_authorized_runway":4,"primary_liveness":"RUNWAY_OK","global_evidence_wait_supported":false}
<!-- current-runway:end -->

<!-- current-runway-summary:start -->
Ready IDs: GP-CONFIG-020, GP-VAL-036, GP-KBD-001, GP-CONFIG-019; Immediate Ready: 4; Recorded Preauthorized: 11; Mechanically activatable Preauthorized: 0; Invalidated Preauthorized: 0; Hardware-pending: 0; Effective authorized runway: 4; Target effective authorized runway: 4; Primary liveness: RUNWAY_OK
<!-- current-runway-summary:end -->

GP-CONFIG-012 and GP-VAL-033 retain exact completed H1 evidence. The 2026-10-02 Curator adoption supersedes the prior correspondence/protected-path REVIEW stops for candidate creation and establishes the serialized safety campaign plus independent Keyboard and USB-menu characterization. The machine-derived marker defines executability. Governance successors authenticate future candidate identities finitely; historical evidence and every build/hardware gate remain intact. GP-CONFIG-021 is narrowed to operation refusal on stored rejection or ambiguous storage failure, preserving the file and bypassing normal reports and save-capable construction. The OLED warning is supplementary and never treated as physical acknowledgment. GP-REL-001 retains substantive dependencies, GP-VAL-011 remains owner-deferred, Nunchuk remains NOT_TESTED and root cause remains unproven.

GP-VAL-032 is DONE: the exact current GP-CONFIG-010 semantic checker now has
the locally required historical commit in the isolated aggregate's closed
object catalog. The reviewed H1 repair passed 41 of 41 aggregate checks,
current and historical semantic proofs, adversarial omission/substitution and
closure tests, and independent review. GP-PROV-014 retains its
preserved candidate and separate full-aggregate DONE gate. All other
GP-VAL-011 work remains deferred under GLYPH-UD-013.

GP-PROV-014 is DONE: the preserved candidate was reconciled with canonical
after GP-VAL-032, then passed its snapshot-bound source/dependency closure
checks, 33 adversarial cases, independent review, and the required clean
42-of-42 aggregate with canonical proof MATCH. The observed Nanopb 0.4.92
closure does not pin future resolution or itself authorize GP-CONFIG-012/013 decoder
acceptance; the separate Curator receipt authorizes bounded H1 characterization. Independent replay in a reduced-object local clone passed 41 of 42:
GP-CONFIG-010's historical proof hashes `git diff` text whose `index` SHA
abbreviation changed with the object database; the patch body was identical.
The 42-of-42 result is specific to the recorded candidate checkout, not a
clean-clone portability guarantee. All other GP-VAL-011 work remains deferred.

GP-VAL-029 is DONE: the current semantic checker now proves accepted mode-selection and 28-table bytes on reviewed descendants; its historical candidate proof remains separate. At GP-VAL-029 publication, the full aggregate still had independent capacity, config-menu source drift, prebuild identity, and semantics bridge failures.

GP-VAL-030 is DONE: the prebuild self-test now sets Git identity only in its temporary repositories and passes with system and global Git config disabled. The aggregate still fails capacity, config-menu source drift, and semantics bridge checks; production builder behavior is unchanged.

GP-VAL-031 is DONE: the current semantics bridge fixtures bind the exact current extractor digest after bounded old/current equivalence proof.

GP-VAL-028 is DONE: an authenticated tracked Nanopb 0.4.9.2 generated header makes the GP-CONFIG-010 capacity checker run from a clean checkout. GP-CONFIG-016 subsequently completed a clean 41-of-41 aggregate with canonical proof MATCH and independent review; its NeoPixel null result is bounded host evidence with physical reachability UNKNOWN. The historical tested-artifact package identity remains UNKNOWN.

- GP-CONFIG-010 is `DONE`. Exact tested integration candidate `1c0ff22646729d26d45eacb4b8322c5baea7de48`, based on `22c639c31ea7006c18a29ec2693c8b18ff688ed4`, entered canonical through merge `50a6357eddf0d9c83d31233666c451806fb1f424`; narrow completion-control commit `7ca129e218b292c0aa64b38577848dd8b63a4c66` added only the three exact source-free protocol/result/evidence paths to the finite correspondence inventory. The physically passed artifact remains the preserved 791552-byte UF2 `4312f6a64fd1009e231aab2015e3ce67f862abd88a8ea31cd545db0e91e27476`. Required 13-profile capacity/reconnect checks, exact owner Config restoration, all nine GP-X1-002 rows, ordinary sanity, and final reconnect passed with empty evidence gaps. The original candidate `f4771e17430fd1ea3f1e3e5339a83dfe648290a3`, UF2 `9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a`, and immutable PASS remain distinct historical evidence. GP-VAL-015/027 retain critical precedence and unknown-path fail-closed behavior. The prior frozen-logo event remains unexplained and did not recur. The 2026-09-29 Curator receipt independently replaced the obsolete GP-CONFIG-012/013 evidence gates with exact 0.4.9.2-bound H1 orders, authorized the narrow GP-CONFIG-014 capacity repair and GP-CONFIG-017 RGB ordering repair, and kept valid same-session custom-mode replacement semantics separately USER_DECISION_GATED as GP-CONFIG-018. GP-CONFIG-015 remains RESEARCH_GATED. GP-VAL-011 remains deferred and GP-HW-002 remains research gated. Nunchuk remains NOT_TESTED and root cause remains unproven.
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
