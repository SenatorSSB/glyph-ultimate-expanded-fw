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

## Publishing Rules

New entries must identify the human source and date. If a direction is
superseded, retain it and identify the superseding entry. Observations and
hypotheses are evidence inputs, not automatic work authorization.
