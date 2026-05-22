# Active Agent Queue

This file is the current queue for Codex agents in the Glyph-side repository.

## Branch

Use the current checked-out branch unless instructed otherwise.

If branch/remote policy is unclear, stop and report.

## Current mode

```text
Tier 2 — autonomous with stop conditions
```

## Current objective

Prepare Glyph/HayBox-style controller-backend realization architecture without changing Senscope game semantic source authority.

## Current boundaries

Read:

- `AGENTS.md`
- `docs/project/AGENT_OPERATING_CONTRACT.md`
- `docs/project/AGENT_STOP_CONDITIONS.md`
- `docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md`

Do not add gameplay semantics.

Do not change Senscope no-smash/no-strong-input behavior.

Do not add export/push workflows.

Do not claim undocumented firmware behavior.

## First implementation sequence

### G1 — Glyph repo inventory and architecture map

Inspect the repo structure, docs, source files, tests, and any existing backend/firmware/configuration modules.

Deliverable:

```text
docs/project/G1_GLYPH_REPO_INVENTORY_AND_ARCHITECTURE_MAP.md
```

The document should include:

- top-level repo structure;
- important source directories;
- important docs/tests;
- build/test commands discovered;
- likely firmware/backend modules;
- likely configuration/schema modules;
- likely integration-relevant files;
- unknowns and source-authority gaps;
- recommended next investigation targets.

### G2 — Controller capability surface extraction

Extract documented/source-backed controller capabilities.

Deliverable:

```text
docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md
```

The document should classify capabilities such as:

- input buttons;
- modifiers;
- layers/modes;
- analog coordinate/output representation;
- SOCD handling if sourced;
- priority/fusion behavior if sourced;
- profile/config format if sourced;
- transport/output behavior if sourced;
- unsupported/unknown areas.

Do not infer unsupported behavior.

### G3 — Neutral profile integration boundary design

Design how Senscope neutral profile concepts could integrate with this backend.

Deliverable:

```text
docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md
```

The document should cover:

- neutral profile assumptions;
- 9-way modifier-direction targets;
- raw coordinate realization;
- exact match / mismatch / unsupported / unknown statuses;
- adapter boundary;
- evaluator boundary;
- diagnostics;
- non-goals.

## Stop after G3

After G3, push if branch policy is clear and stop for inspection.

Do not implement runtime backend adapters until G1-G3 are reviewed.

## Verification

Docs/design only unless code is touched:

```bash
git status
git diff --stat
```

If code is touched, inspect package files and run targeted repo-native tests.

## Final report

Use:

```text
docs/project/AGENT_FINAL_REPORT_TEMPLATE.md
```

Semantic changes must be:

```text
none
```
