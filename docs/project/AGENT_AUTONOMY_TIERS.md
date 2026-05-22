# Agent Autonomy Tiers

This document defines how much freedom an agent has in the Glyph-side repository.

## Tier 1 — autonomous mechanical execution

Use Tier 1 for small, behavior-preserving tasks.

Allowed:

- docs;
- inventories;
- source maps;
- index updates;
- tests for existing behavior;
- helper extraction;
- naming cleanup;
- non-semantic refactors.

Agent may:

- implement;
- run targeted verification;
- commit;
- push if branch policy is clear.

Agent must stop if:

- tests fail unexpectedly;
- files outside scope need changes;
- behavior claims become ambiguous;
- branch/remote policy is unclear.

## Tier 2 — autonomous with stop conditions

Use Tier 2 for medium engineering tasks with clear source boundaries.

Allowed:

- capability-model scaffolding;
- evaluator prototypes from documented behavior;
- diagnostics;
- adapter boundary code;
- behavior-preserving migrations;
- source-backed documentation.

Agent may proceed unless a stop condition is hit.

Mandatory stop conditions:

- undocumented controller behavior required;
- export format assumptions required;
- push-to-device support required;
- neutral profile schema change required;
- gameplay semantics required;
- broad architecture decision required;
- tests indicate behavior differs from expectation.

## Tier 3 — domain approval required

Use Tier 3 for source-authority or product decisions.

Agent must not implement until user approves.

Examples:

- claiming firmware behavior not directly sourced;
- deciding whether backend behavior is universal;
- adding vendor export generation;
- adding push-to-device workflows;
- changing neutral profile compatibility assumptions;
- modeling SOCD/priority/fusion behavior without clear source;
- coupling backend constraints into game-semantic solver;
- selecting Smash gameplay semantics.

## Current default

Unless a task says otherwise:

```text
Tier 2
```

## Current allowed autonomous sequence

Initial safe sequence:

```text
G1 — Glyph repo inventory and architecture map
G2 — Controller capability surface extraction
G3 — Neutral profile integration boundary design
```

Stop after G3 for inspection.
