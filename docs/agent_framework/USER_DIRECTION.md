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
- Status: `Active`
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

## Publishing Rules

New entries must identify the human source and date. If a direction is
superseded, retain it and identify the superseding entry. Observations and
hypotheses are evidence inputs, not automatic work authorization.
