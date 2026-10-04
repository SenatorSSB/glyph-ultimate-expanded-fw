# User Direction

Status label: CURRENT.

This file records only actual human direction or a faithful bounded summary of
it. Agents must not invent entries. Types are `Directive`, `Decision`,
`Priority`, `Preference`, `Observation`, and `Hypothesis`; statuses are
`Active`, `Resolved`, or `Superseded`.

## Active Entries

### GLYPH-UD-001

- Type: `Directive`
- Status: `Active`
- Source: user migration instruction supplied 2026-08-23
- Direction: Keep this repository limited to Glyph/HayBox firmware,
  configurator, and backend realization. Senscope owns game-semantic/profile
  intent. The control-plane migration must not include an opportunistic product
  or firmware behavior feature.

### GLYPH-UD-002

- Type: `Decision`
- Status: `Active`
- Source: user migration instruction supplied 2026-08-23
- Direction: `configurator` is the canonical development and comparison
  branch. The canonical build is `pio run -e glyph_mk6`, with the repository
  fallback wrapper allowed when the command is unavailable.

### GLYPH-UD-003

- Type: `Directive`
- Status: `Active`
- Source: user migration instruction supplied 2026-08-23
- Direction: Runtime-sensitive work requires a first-class manual physical
  controller acceptance lane. Hardware success must never be fabricated, and
  failed or hardware-invalidated active source must not enter `configurator`.

### GLYPH-UD-004

- Type: `Preference`
- Status: `Active`
- Source: user migration instruction supplied 2026-08-23
- Direction: Start with a Minimal Supervisor, durable Ready/Preauthorized
  authorization, and a hard hardware lane. Keep Planner and Curator available,
  initially manual or low-frequency, so stale candidate supply can recover
  without autonomous idea generation outrunning physical validation.

### GLYPH-UD-005

- Type: `Decision`
- Status: `Active`
- Source: current user-directed governance correction supplied 2026-08-23
- Direction: Authorized, source-grounded firmware behavior work may be
  implemented autonomously through the candidate stage when substantive
  behavior, product, domain, source-authority, architecture, scope, and
  validation decisions are already resolved. H2/H3 remains physically gated
  before merge. Unresolved behavior or product decisions still require
  user/domain input.

### GLYPH-UD-006

- Type: `Priority`
- Status: `Active`
- Source: user continuation direction supplied 2026-08-24
- Direction: Resolve or curate authorization for the unrelated generator
  validation failure before resuming `GP-PROV-002` publication. This priority
  does not itself broaden implementation scope or waive current validation,
  review, publication, or runtime/product boundaries.

### GLYPH-UD-007

- Type: `Decision`
- Status: `Active`
- Source: user supervisor task supplied 2026-08-27
- Direction: Official Glyph configurator interoperability is no longer a
  product requirement, development dependency, or progression dependency for
  the custom Glyph/Senscope firmware path. `GP-CONFIG-002` is invalidated; no
  official-configurator operator capture is required or awaited. Historical
  corpus, templates, procedures, and evidence remain provenance only. This
  lane may become active again only through a later explicit user decision.

### GLYPH-UD-008

- Type: `Decision`
- Status: `Active`
- Source: user supervisor task supplied 2026-08-27
- Direction: The first production source-authority pilot uses
  `overlay_preserve` and owns exactly the canonical X1 table symbol established
  mechanically from the current 28-table baseline. Its initial replacement is
  the exact existing ordered nine-point raw-byte X1 baseline content, so this
  pilot authorizes ownership while deliberately preserving active table bytes.
  The baseline supplied the bytes; this decision supplies production authority
  and does not claim that Senscope generated the values. All other 27 tables
  remain unowned and preserved.

### GLYPH-UD-009

- Type: `Directive`
- Status: `Active`
- Source: user supervisor task supplied 2026-08-27
- Direction: The X1 pilot authorizes no different X1 coordinate, second table,
  all-table replacement, active byte change, new modifier/gameplay semantic,
  runtime-loaded or persistent configuration, WebSerial/device write,
  protobuf write, flashing automation, alternate active publication path, or
  Nunchuk claim. Future active X1 changes and future ownership expansion each
  require separate explicit authority; behavior-changing candidates retain the
  exact-candidate build, artifact, and physical hardware gate.

### GLYPH-UD-010

- Type: `Decision`
- Status: `Active`
- Source: user Codex task supplied 2026-09-02
- Direction: For the single X1 offset-41 hardware-test candidate based on the
  then-current live `configurator`, the project owner explicitly supersedes
  the baseline-equivalent X1 no-op restriction and authorizes
  `generation_mode = overlay_preserve`, ownership of `kX1Table` only, and the
  exact ordered raw coordinates `(87,87)`, `(128,87)`, `(169,87)`,
  `(87,128)`, `(128,128)`, `(169,128)`, `(87,169)`, `(128,169)`, and
  `(169,169)`. The user supplies this coordinate intent; Glyph realizes the
  exact raw values without inferring gameplay meaning.

### GLYPH-UD-011

- Type: `Directive`
- Status: `Active`
- Source: user Codex task supplied 2026-09-02
- Direction: GLYPH-UD-010 is candidate-specific and does not authorize any
  other X1 value, any other source-owned table, routing or publication-path
  changes, modifier or game-semantic changes, runtime-loaded configuration,
  persistence, WebSerial/device write, protobuf write, flashing automation,
  release/upload, or merge. The exact committed candidate may be built to a
  local UF2 for manual exploratory hardware testing, but no hardware PASS or
  merge eligibility exists until the user reports physical results for the
  preserved candidate/artifact identity.

### GLYPH-UD-012

- Type: `Observation`
- Status: `Active`
- Source: direct user hardware reports supplied 2026-09-02
- Direction: For candidate
  `74ae24364b84520d4e0e39240beb9867653cc7b9` and the handed-off UF2 with
  SHA-256
  `5fadd3d7e82e629fbccd41fac868312b07b01e39d2ef0a0a98a06d649ae28254`,
  the project owner reported that all outputs were as expected and the
  controller did not disconnect at any point. After receiving the regenerated
  prior firmware, the project owner reported that it worked and directed the
  supervisor to proceed with the real results. This observation accepts only
  the recorded X1 test scope; Nunchuk remains NOT_TESTED and root cause remains
  unproven.

### GLYPH-UD-013

- Type: `Decision`
- Status: `Active`
- Source: one-time supervisor task supplied by the project owner 2026-09-07
- Direction: `GP-VAL-011` complete-proof isolation optimization is intentionally
  deferred and nonexecutable. Preserve its objective, research, failed
  candidates, measurements, adjudication, and historical reviewed completion,
  but do not treat the deliberately deprioritized repair as the primary current
  liveness blocker. Reopening requires fresh substantive authorization. This
  decision authorizes no concurrent fingerprint/proof work, cancellation or
  timeout-resource redesign, Git-object/ref-topology expansion, production
  deadline increase, mutation-proof or ignored-state weakening, isolated-clone
  weakening, or false DONE claim.

### GLYPH-UD-014

- Type: `Decision`
- Status: `Active`
- Source: one-time supervisor task supplied by the project owner 2026-09-07
- Direction: In the existing custom Glyph/HayBox backend, a rejected
  `SetConfig` operation must not leave rejected candidate values active in the
  live in-memory `Config`. Decode, validation/bounds, persistence/save, and any
  other rejection in the existing bounded transaction path preserve or restore
  the prior accepted live `Config`; only complete success may publish the
  candidate live. This is a live-RAM transaction invariant only. It does not
  claim or authorize atomic `config.bin` persistence, disk rollback/recovery,
  power-loss safety, a new persistence mechanism, a configurator redesign, or
  revived official-configurator interoperability. Source-derived Curator
  architecture may authorize an exact candidate, but behavior-changing source
  remains H2/H3 and cannot merge without exact-snapshot build and physical PASS.

### GLYPH-UD-015

- Type: `Decision`
- Status: `Active`
- Source: one-time supervisor task supplied by the project owner 2026-09-07
- Direction: Revision-2 H2/H3 firmware candidates use owner-held local
  content-addressed custody rooted at
  `local_backups/hardware-artifacts/<full-candidate-git-sha>/<full-artifact-sha256>/firmware.uf2`.
  The custodian identity is `Glyph project owner / user authority`. Preserved
  bytes at an identity are write-once and retained while their hardware evidence
  remains accepted, current, or historical; tested artifacts are not
  automatically garbage-collected. Hash the produced bytes, preserve under the
  matching identity, read back and re-hash, and re-hash immediately before
  hardware handoff. A rebuild substitutes only when its bytes independently
  match the recorded SHA-256; otherwise it is a new artifact requiring new
  hardware evidence. Loss preserves the historical record but transfers no
  acceptance to a rebuild. Independent system/filesystem backup is recommended,
  not required; no cloud/external store, upload, release, credential, CI release
  policy, flashing automation, or device write is authorized.

### GLYPH-UD-016

- Type: `Decision`
- Status: `Active`
- Source: direct user governance correction supplied 2026-09-19
- Direction: A completed Work-Order Curator run must consume the current
  curation obligation and must never publish `CURATION_REQUIRED` as the next
  primary state. If it creates executable authorization, the next state is the
  derived runway state. If effective runway remains zero after every current
  candidate and invalidation has been adjudicated, the Curator must preserve
  exact user/evidence/research gates as supporting dispositions, mark supply
  that cannot proceed without new input as no longer pending Curator work, and
  route next to `PLANNING_REQUIRED` (or an independently accepted global wait).
  A later material packet, invalidation, failed-hardware event, or new external
  evidence may create a new curation obligation; it does not justify a
  self-loop at the end of the current Curator run. This decision authorizes no
  filler work, inferred product semantics, weakened evidence gate, or direct
  execution of gated candidates.

### GLYPH-UD-017

- Type: `Directive`
- Status: `Superseded`
- Source: owner campaign steering reported through the implementation supervisor
  on 2026-09-21; the owner said the warning did not show affected task names.
- Direction: park work associated with the reported cybersecurity warning as
  TODO/draft work and continue the remaining campaign. The supervisor applies
  this deferral to `GP-CONFIG-012`, `GP-CONFIG-013` and `GP-CONFIG-014` while
  preserving their prior source contracts and unfinished work. The exact
  warning source, cause and flagged item identities are `UNKNOWN`; this record
  does not assert an observed automatic approval rejection, exploitability,
  security classification, firmware defect severity or physical symptom.
  Independent Curator records these three items as `REVIEW / OWNER_DEFERRED /
  NONEXECUTABLE`. Do not continue their probes, implementation, firmware build
  or merge. Resumption requires explicit owner direction and fresh Curator
  reauthorization against live source, including every original validation and
  hardware gate. This does not defer other campaign work, change GP-VAL-011,
  or alter GP-CONFIG-010's exact preserved candidate/artifact or hardware gate.

### GLYPH-UD-018

- Type: `Decision`
- Status: `Active`
- Source: direct project-owner confirmation supplied 2026-09-21
- Direction: Restore the existing Ultimate sole/non-Mode `kX1Table` to the
  ordered direction rows `(93,51)`, `(128,51)`, `(163,51)`, `(93,128)`,
  `(128,128)`, `(163,128)`, `(93,205)`, `(128,205)`, and `(163,205)`. Preserve
  every other source-owned table, including `kMX1Table`, and preserve the
  current LT5/non-Mode selection route, Mode behavior, precedence, active
  publication mechanism, profile/configuration behavior, and GP-CONFIG-010
  identity. This decision creates no Senscope modifier or binding, makes no
  gameplay-angle or radius claim, and does not authorize runtime-loaded
  configuration, persistence, device write, protobuf write, WebSerial, or
  flashing automation. The restoration is H2 and requires an exact committed
  candidate, canonical build, preserved UF2 custody, independent review, and
  exact-snapshot physical PASS before merge.

### GLYPH-UD-019

- Type: `Directive`
- Status: `Resolved`
- Source: direct project-owner recovery instruction supplied 2026-09-22
- Direction: Complete GP-CONFIG-010 physical acceptance using only unchanged
  candidate `f4771e17430fd1ea3f1e3e5339a83dfe648290a3` and preserved UF2 SHA-256
  `9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a`.
  Before mutation, capture and verify the owner's exact current protobuf Config
  payload bytes. Temporarily write an owner-Ultimate-derived configuration with
  exactly thirteen GameCube-applicable Ultimate clones, names `Ult01` through
  `Ult13`, and unique safe source-backed activation bindings so indices 0..12
  can be exercised. Preserve unrelated configuration and restore the exact
  original captured payload bytes immediately and after reboot whether the run
  passes or fails. Then manually restore only the physically accepted
  GP-X1-002 artifact for candidate
  `f657715b26d26587a931074ce7dd12c698785290`, SHA-256
  `00dc75b65a080830131c3c260558d4daeff45bb528e43d196b8ad94fcd06f451`,
  and perform bounded normal Ultimate/X1 sanity. This is one bounded recovery
  authorization through existing source-supported commands; it does not
  authorize firmware/source/schema/default changes, persistence architecture,
  generalized runtime-loaded configuration or device-write capability,
  flashing automation, candidate rebuild/substitution, Nunchuk claims,
  gameplay-semantic inference, evidence overwrite, or merge before a fresh
  independent Hardware Evidence Processor accepts complete observations.

Resolution: the one bounded recovery run was consumed. It established all
thirteen activation rows and exact restoration/rollback, but remained
INCONCLUSIVE after the first final reconnect froze at the Glyph logo and the
required post-reconnect visibility and LT4-to-Ult13 checks were not completed.

### GLYPH-UD-020

- Type: `Directive`
- Status: `Active`
- Source: direct project-owner reconnect-completion instruction supplied 2026-09-22
- Direction: Authorize through normal Planner/Curator governance one bounded
  GP-CONFIG-010 reconnect-completion retest using only unchanged candidate
  `f4771e17430fd1ea3f1e3e5339a83dfe648290a3` and preserved 791040-byte UF2
  SHA-256
  `9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a`.
  Preserve the prior exact 13/13 activation evidence, including indices 10,
  11, and 12, and do not repeat the full matrix absent a new discrepancy.
  Recreate the exact prior temporary thirteen-Ultimate Config only after a
  fresh exact owner-original backup, then require first-attempt normal
  GameCube startup, exact Ult01-through-Ult13 menu visibility, LT4-to-Ult13
  post-reconnect selection, representative normal operation, and exactly three
  additional reconnect cycles. Any controlled frozen-logo recurrence stops
  the run and is expected to classify FAIL unless evidence clearly proves an
  unrelated external cause. Restore the exact owner Config and the exact
  accepted GP-X1-002 firmware/artifact regardless of result. This directive
  authorizes no build, firmware patch, full-matrix repetition without
  discrepancy, product/runtime capability, GP-VAL-011 work, or merge before a
  fresh independent Hardware Evidence Processor publishes exact PASS.

### GLYPH-UD-021

- Type: `Directive`
- Status: `Active`
- Source: direct project-owner instruction in the Codex task "Resume config safety planning" (task `01a0dee7-fbe3-7202-b91c-fc0b49ebe74c`), supplied 2026-09-26
- Direction: Resume GP-CONFIG-012, GP-CONFIG-013 and GP-CONFIG-014 for normal Planner-to-Curator consideration. GLYPH-UD-017 no longer parks these three items by itself. This is planning/curation permission only; each item still needs fresh live-source Curator authorization before probes or implementation. No firmware candidate, build, device action, hardware result or merge is authorized by this direction. No invalid-button, USB-default or in-place custom-mode update policy is selected. GP-VAL-011 remains independently OWNER_DEFERRED / NONEXECUTABLE. The earlier warning source, cause and affected identities remain UNKNOWN.

### GLYPH-UD-022

- Type: `Decision`
- Status: `Active`
- Source: direct project-owner Curator campaign request supplied 2026-10-02.
- Direction: For populated Config fields/list elements representing actual button bindings, accept only supported source-defined named nonzero Button IDs; reject BTN_UNSPECIFIED/0, unnamed IDs and out-of-domain values. Absence/no binding is structural absence/count zero. Rejected candidates never become live; preserve GP-CONFIG-005 transaction semantics. The source-defined remap disable sentinel is a distinct operation, not a populated actual binding. This selects no RGB, USB fallback or valid live-rebind policy.

### GLYPH-UD-023

- Type: `Decision`
- Status: `Active`
- Source: direct project-owner Curator campaign request supplied 2026-10-02.
- Direction: If persisted Config fails decode or semantic validation, preserve the rejected stored file byte-for-byte; do not publish or consume partial/invalid state. Use independently validated source defaults for that boot, do not automatically overwrite the rejected file, and present a conspicuous persistent user-visible indication that stored Config was rejected, defaults are active and recovery is required. Do not present normal successful-profile-load UI/state. If reliable persistent fail-loud indication cannot be implemented and validated, refuse normal controller operation pending manual recovery. No general persistence/power-loss architecture is selected. The Curator's narrower current refusal authorization is an application of this fallback, not a new owner preference for all future recovery.

### GLYPH-UD-024

- Type: `Decision`
- Status: `Active`
- Source: direct project-owner Curator campaign request supplied 2026-10-02.
- Direction: Populated RGB button-color mapping targets must be supported physical RGB-targetable named nonzero buttons. Reject zero, unnamed and out-of-domain IDs; structural absence means no mapping. RGB eligibility is independent of gameplay binding state; a disabled/unassigned physical button may have lighting. No palette, animation, brightness, pin map or fallback color is chosen.

### GLYPH-UD-025

- Type: `Decision`
- Status: `Active`
- Source: direct project-owner Curator campaign request supplied 2026-10-02.
- Direction: The beta supports normal gameplay through GameCube-controller transport via GC adapter and ordinary source-verified default Glyph USB gameplay on Nintendo Switch and computers, including existing normal mode selection required for those paths. Configuration change -> reboot -> gameplay is an acceptable required workflow; same-session active custom-mode hot replacement remains deferred. This claims no official Glyph Configurator compatibility, generalized live reconfiguration, runtime-loaded profiles, WebSerial/device write, automated flashing or Nunchuk support. Common startup/persistence/GC/supported USB defects remain release-relevant. USB-default fallback remains undecided until GP-CONFIG-013 completes.

### GLYPH-UD-026

- Type: `Decision`
- Status: `Active`
- Source: direct project-owner message “Owner decision — USB default validation”, supplied 2026-10-02; daemon chat `01a0fcbd-2b4c-7d31-9088-42a22e260b57`, turn `01a0fcc9-98f0-7b41-9183-04f6d313685e`, userMessage `01a0fcc9-9965-7372-afbf-8e15a5dc88cc`, independently read by Curator.
- Direction: `default_usb_backend_config` is required one-based configuration. Reject Config before publication/acceptance when omitted and decoded zero, explicitly zero, or greater than `communication_backend_configs_count`. Zero has no no-USB meaning. Do not silently fall back to index 1 or another backend. Apply at all beta-relevant Config acceptance seams including external and persisted loading. Rejected candidates preserve existing accepted/live state and follow separately approved persisted recovery. This selects index validity only; no further referenced backend-type eligibility rule. Additional type constraints require separate source evidence and authority.
- Effect: resolves the USB-default policy left undecided by GLYPH-UD-025 and completed GP-CONFIG-013 characterization; other GLYPH-UD-025 support/reboot/non-claims remain active. Firmware repair still follows the complete gated GP-CONFIG-023 order.

### GLYPH-UD-027

- Type: `Directive`
- Status: `Active`
- Source: direct project-owner message "OWNER DIRECTIVE — FORCE GOVERNANCE
  REVISION NOW", supplied 2026-10-04 in daemon task
  `01a0fcbd-2b4c-7d31-9088-42a22e260b57`, userMessage
  `01a106b6-5a49-7812-b18d-3188826d23b7`; independently retrieved in full by
  the GP-VAL-044 Implementation Supervisor, not inferred from a peer summary.
- Direction: separate product/firmware validation from framework self-validation.
  This Revision-3 decision supersedes conflicting Revision-2 progression rules
  while retaining their historical records and the exact-candidate safety model.
  Tier 1 candidate-critical proof always blocks; Tier 2 directly affected
  regression proof blocks where affected. Tier 3 framework health is tracked
  debt, not an automatic candidate blocker, unless a concrete Tier-1/Tier-2
  safety contradiction is identified. A timeout means incomplete execution,
  never PASS and not by itself a firmware-safety finding.
- Mandatory safety: exact committed candidate SHA/tree and build inputs,
  canonical Mk6 build where required, exact UF2 SHA-256/size and owner-held
  content-addressed custody, focused changed-behavior tests, every directly
  affected consumer, relevant current/historical correspondence and negative
  controls, exact critical source correspondence, relevant snapshot/mutation/
  isolation proof, fresh independent implementation and integration review,
  required Config backup/restoration, and exact H2/H3 human physical PASS before
  behavior-changing source integration. Independent HEP must validate candidate,
  artifact, protocol, required rows and gaps and classify the result; human
  observations remain distinct from inference. No unsupported behavior or root
  cause claims; Nunchuk remains NOT_TESTED. No expanded firmware/device/flashing
  automation or automatic public release.
- Immediate finite execution: independently review exact source-free GP-VAL-044
  candidate `d6fbbbf083c385d7cdfa82627ea2184bb9ded19e` and its focused/affected
  evidence. If no concrete safety contradiction exists, integrate it source-free
  and publish separate strict GP-VAL-044 DONE on that proof basis, preserving
  incomplete/failed aggregates as debt. No new Planner/Curator interpretation
  cycle or new GP-VAL is required for this existing framework failure. Then
  resume HEP using the already-complete preserved physical observations with
  no physical retest. Exact C020 F remains
  `7db4f447d5e796367071b7143fa6c9274c70ae5e`, artifact SHA-256
  `7743fcbe3d71ec4159e6da5026a1b4560cbbef4d1654cb80b8907fcce344b500`.
  Preserve `R -> E -> I`: source-free processor evidence E must not require the
  integrated source catalog at I. Only independently accepted HEP PASS permits
  later exact tested C020 source integration, focused integration proof, fresh
  independent integration review and strict C020 DONE. This decision is not HEP
  acceptance and confers no physical PASS itself.
- Framework debt, nonblocking absent a concrete safety contradiction:
  unexplained nested-preflight failure; aggregate runtime over 300 seconds;
  recursive validation cost; duplicated synthetic topology work; validator/
  governance coupling; expensive repeated Git-object proof construction.
  Preserve the original FAIL/incomplete reports and unknown root cause. In
  particular GP-VAL-044's nested-preflight FAIL and bounded 300-second timeout
  remain failures/incomplete, not PASS; the later diagnostic 307.80-second
  45/46 run with all 46 isolated proofs and canonical MATCH also remains FAIL.
  Its nested 0.7-second setup PermissionError has UNPROVEN cause. None is
  asserted to establish a contradictory firmware-safety fact.
- Deferred scope: production 300-second aggregate and 120-second checker limits
  are unchanged. GP-VAL-011 remains otherwise OWNER_DEFERRED / NONEXECUTABLE;
  do not reopen it broadly to complete C020. After C020 DONE, perform one bounded
  Revision-3 control-plane simplification of authorization/runway, supervisor,
  scheduled-runner, Planner/Curator boundaries, hardware lifecycle and validation
  tiers. Before a future GP-VAL, require `UNPROVEN_SAFETY_FACT` naming a concrete
  firmware/product safety property; otherwise record framework debt. Per logical
  product order, permit at most one ordinary candidate-governance successor and
  one exceptional validation-repair successor; a third needs owner approval
  unless hardware FAIL, a new firmware/source defect or a new product/domain
  decision justifies it. Timeouts, runner mechanics, topology and proof
  performance do not qualify. Planner/Curator remain for substantive unresolved
  authority, not mechanical identities, already-authorized transitions or
  timeout churn. The later broad documentation simplification is not performed
  by this finite GP-VAL-044 completion.

### GLYPH-UD-028

- Type: `Directive`
- Status: `Active`
- Source: direct project-owner message "ADDENDUM — CROSS-THREAD MCP
  AUTHORIZATION", supplied 2026-10-04 in daemon task
  `01a0fcbd-2b4c-7d31-9088-42a22e260b57`, userMessage
  `01a106eb-f269-7df2-86a8-ad68eae156a6`; independently retrieved in full by
  the post-C020 Control-plane Implementation Supervisor together with the
  complete GLYPH-UD-027 source directive. Not inferred from a worker summary.
- Direction: expressly authorize available cross-thread MCP orchestration
  transport between the known Glyph daemon, Planner, Curator, Implementation
  Supervisor, Hardware Evidence Processor and role-specific workers created
  or reused for this exact campaign. Purposes include dispatch, ACK/status,
  WORKER_RESULT, role results, completion/blockers, requesting the next
  authorized worker, write-lock release and exact identity handoff. Restrict
  targets to known existing Glyph workers, exact-campaign workers, the parent
  daemon and daemon-selected successors; no broadcast or unrelated chats.
- Identity: where practical prefix daemon messages with
  `OWNER_AUTHORIZED_GLYPH_ORCHESTRATION`; include sender/receiver role,
  project, exact work order, current canonical SHA, scope and expected return
  destination. The receiving worker still requires valid independent
  role/work-order authority. Transport grants no repository permission,
  firmware/Config/hardware/flashing/public-release/product semantics, role
  authority expansion or bypass of substantive Planner/Curator requirements.
- Rejection handling: accepted sends continue normally without unnecessary
  duplicate delivery. A rejected send is only
  `CROSS_THREAD_MESSAGE_REJECTED`, not assignment failure. Do not repeatedly
  retry or bypass rejection. Continue locally authorized work when receipt is
  not a dependency, persist the same logical result durably, and rely on
  daemon readback/polling. A rejected ACK is not an implementation stop and
  creates neither a GP-VAL nor a Curator obligation. Messaging friction is
  framework/orchestration debt unless it prevents a concrete safety fact.
- Durability: prefer canonical/authorized commits, then pushed worker branches,
  then authorized repository handoff files, stable reported local handoffs,
  and accessible transcripts. Important implementation/evidence must not rely
  exclusively on temporary storage. Attempt WORKER_RESULT through available
  MCP first; after rejection report
  `WORKER_RESULT_PERSISTED_FOR_DAEMON_READBACK` with work order, result, branch,
  implementation/candidate SHA, canonical, handoff path and next action.
- Chaining: process successful callbacks immediately, refresh canonical and
  dispatch the next deterministic authorized transition without a heartbeat
  delay. The existing ten-minute poll is idle fallback: inspect active/recent
  workers and missing callbacks, refs/commits and durable results, reconstruct
  and independently verify identities, then route the next transition.
  Inspect the prior worker/thread, branch and handoff before replacement;
  replace only when definitively failed, abandoned or unable to continue.
- Serialization: only one canonical-writing worker may hold the daemon's
  write/publication lock. Concurrent communication does not permit concurrent
  publication. No account/settings change or transport test is authorized by
  this addendum. It applies under GLYPH-UD-027 Revision 3.

## Publishing Rules

New entries must identify the human source and date. If a direction is
superseded, retain it and identify the superseding entry. Observations and
hypotheses are evidence inputs, not automatic work authorization.

## Persistent batch execution

### GLYPH-UD-029

- Type: `Directive`
- Status: `Active`
- Source: direct project-owner message "OWNER DIRECTIVE — SWITCH TO PERSISTENT
  BATCH EXECUTION NOW", supplied 2026-10-04 in daemon task
  `01a0fcbd-2b4c-7d31-9088-42a22e260b57`, actual userMessage
  `01a1078b-f2a9-77c2-b3bd-c0f0aaba5d74`; independently retrieved in full by
  the existing H3 Implementation Supervisor. The complete verified local
  readback has SHA-256
  `058f99066e4a2a1dd8d7daa5af8a0767ebfd840264bf9dd1d60d3f10adf309e8`.
  This is owner direction, not authority inferred from a peer transport header.
- Direction: reuse a small set of persistent full H3, H1, Curator/authority and
  Hardware Evidence Processor workers. The H3 worker executes the existing
  authorized sequence C014 -> C017 -> C021 -> C022 -> C023. Within each logical
  item, carry READY -> implementation -> its already PREAUTHORIZED ordinary
  governance successor -> product resume -> focused Revision-3 validation ->
  fresh independent review -> exact committed Mk6 build -> artifact custody ->
  HARDWARE_REQUIRED in the same worker. Objective activation and routine
  mechanical transitions do not require another full chat, daemon handoff,
  Planner or Curator. Preserve live prerequisites and exact candidate identity.
- Named chains: C014 -> VAL034 -> C014, C017 -> VAL035 -> C017,
  C021 -> VAL038 -> C021, C022 -> VAL039 -> C022, C023 -> VAL042 -> C023.
  The existing H1 worker carries VAL040 -> KBD001 and C019 -> VAL041 -> C019
  under live authority. The owner explicitly resumes this H1 lane; its earlier
  pause remains historical. H1 branch work may proceed concurrently when it
  cannot change frozen H3 source/build inputs; independent checkouts and stable
  validation intervals preserve proof fingerprints.
- Serialization: one canonical writer/publication lock at a time. The lock
  controls publication to `configurator`; other workers may inspect, implement
  dedicated branches, run tests, prepare commits, obtain review and prepare
  handoffs without that lock. Retain the H3 lock through its logical chain;
  release at genuine hardware wait or substantive stop. Do not mutate another
  worker's checkout or publish concurrently. The daemon grants later canonical
  publication authority and reassesses changed assumptions.
- Safety: GLYPH-UD-027 Revision 3 and GLYPH-UD-028 transport remain active.
  Tier 1 blocks; directly affected Tier 2 blocks; Tier 3 remains honest
  framework debt unless it exposes a concrete Tier-1/Tier-2 contradiction.
  Never merge behavior-changing H2/H3 before exact tested candidate/artifact
  human PASS validated by independent HEP. One pending H3 candidate at a time.
  No automatic flashing, device/Config write, public release, game-semantic
  decision, unsupported backend claim or Nunchuk acceptance is authorized.
- Successor limit: normal product -> one existing ordinary governance successor
  -> product resume. One exceptional repair successor requires a concrete
  Tier-1/Tier-2 defect; further recursion requires direct owner approval.
  Any proposed new validation order requires
  `UNPROVEN_SAFETY_FACT = <specific concrete safety fact>`; timeout or
  orchestration friction alone creates no order. Curator is for genuine
  source/owner/architecture decisions, hardware FAIL recovery or new safety
  facts; Planner is for genuinely exhausted runway or substantive decomposition.
- Hardware loop: freeze exact committed candidate and preserved artifact; send
  the owner the exact protocol one action at a time. H1 may progress safely
  during the wait. Actual observations go to persistent independent HEP.
  After HEP PASS the same H3 worker integrates/completes the exact accepted item
  and continues the next authorized H3 item immediately. Human publication
  remains the final release gate.
- Transport and throughput: send meaningful milestone, blocker, hardware or
  lock updates through authorized MCP when it succeeds. After rejection persist
  the same logical result and continue locally; daemon polling is fallback.
  No replacement worker or repeated ACK traffic solely for transport failure.
  New full chats are justified only by genuine independence/capability needs,
  a failed worker, or a separate long-running H1/H3 lane. Keep productive safe
  work moving through known transitions without waiting for a heartbeat.
- Metrics from this directive: full chats created per logical product order,
  canonical commits with SHAs, internal transitions versus daemon handoffs,
  READY -> HARDWARE_REQUIRED and hardware-report -> DONE timestamps, no-op
  calls, Curator calls and Planner calls. Reuse existing executors; mechanical
  execution targets zero Planner/Curator/no-op calls and immediate transitions.
- Supersession: within these named persistent chains this directive supersedes
  default one-new-order-per-invocation and return-after-mechanical-handoff
  instructions, including the earlier C014 candidate-only stop and H1 pause.
  Prior instructions/evidence stay preserved; substantive authority, live queue
  scope, independent review, exact source/build/custody and human hardware gates
  remain required. This directive creates no new product work order.
