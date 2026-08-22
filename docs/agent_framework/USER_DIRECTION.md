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

## Publishing Rules

New entries must identify the human source and date. If a direction is
superseded, retain it and identify the superseding entry. Observations and
hypotheses are evidence inputs, not automatic work authorization.
