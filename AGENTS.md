# AGENTS.md

This repository is the Glyph-side controller implementation / backend realization workstream.

Agents must treat this file as the standing operating contract for this repository. Keep changes scoped, test-backed when code is touched, and reversible by normal Git history.

## Repository purpose

This repo is used to inspect, model, document, and potentially implement Glyph / HayBox-style controller-backend behavior relevant to Senscope integration.

The repo may contain firmware, configuration, controller-backend logic, documentation, or research material. Agents must not assume behavior beyond what the repo source/docs prove.

## Relationship to Senscope

Senscope is the separate browser-first Super Smash Bros. Ultimate Rectangle Modifier Designer app.

This Glyph repo may inform future Senscope backend adapters, realization evaluators, manual-entry guides, or export workflows.

This repo must not directly mutate Senscope game-semantic source authority.

## Core boundaries

Always keep these layers separate:

1. Controller/backend behavior
   - firmware fields
   - input processing
   - modifiers
   - layers/modes
   - SOCD/priority/fusion behavior
   - output/report/export behavior

2. Senscope neutral profile concepts
   - app-owned profile JSON
   - modifier directional maps
   - raw coordinate targets
   - dataset IDs
   - controller-family metadata

3. Game semantics
   - Super Smash Bros. Ultimate action/function meanings
   - thresholds
   - semantic maps
   - no-smash/no-strong-input
   - source-authority promotion

This repo may reason about layer 1 and integration boundaries to layer 2. It must not invent layer 3.

## Non-negotiable rules

- Do not invent Glyph/HayBox firmware behavior.
- Do not invent Super Smash Bros. Ultimate gameplay semantics.
- Do not claim undocumented backend behavior as fact.
- Do not assume a backend can realize every Senscope neutral profile.
- Do not add push-to-device behavior unless source support is explicit.
- Do not generate vendor-specific export files unless the file format/source support is explicit.
- Do not reverse-engineer private/encrypted formats unless explicitly authorized and legally safe.
- Do not change neutral profile schema without explicit user approval.
- Do not couple backend realization constraints into game-semantic solver logic.
- Do not add macros, turbo behavior, or timing automation.

## Source authority

A backend behavior claim must cite or reference one of:

- source file inspected in this repo;
- documentation file inspected in this repo;
- tests or fixtures in this repo;
- user-provided external research notes;
- explicit user/domain statement.

If behavior is inferred, mark it as inferred.

If behavior is unknown, say unknown.

## Branch workflow

Default branch policy:

- work on the current checked-out branch unless instructed otherwise;
- commit only when branch/remote are clear;
- push only to the intended remote branch;
- do not create a new branch unless instructed;
- do not merge into the default/protected branch unless instructed.

If branch policy is unclear, stop and report.

## Command policy

Support both local and cloud environments.

- Use plain/direct commands when tool wrappers are unavailable.
- Use repo-native package/test/build commands after inspecting package files.
- Do not assume `rtk` exists in this repo.
- Do not assume `.venv` exists.
- Do not assume `semble` exists.
- If a prompt mentions a tool that is unavailable, use a safe direct equivalent and report the fallback.
- If Python dependencies are missing, stop and report the missing dependency instead of inventing environment setup.

Common safe commands:

```bash
git status
git diff --stat
git diff -- <file>
rg "<pattern>" <paths>
git grep "<pattern>"
find . -maxdepth 3 -type f
sed -n '1,260p' <file>
```

Use package manager commands only after inspecting the repo:

```bash
npm test
npm run test
npm run typecheck
pnpm test
cargo test
python3 -m pytest
```

Do not run broad or destructive commands unless explicitly instructed.

## Forbidden commands / actions

Do not run:

```bash
git reset
git clean
git stash
git revert
git push --force
```

Do not delete source files, rewrite history, or perform broad formatting rewrites unrelated to the task.

## Stop conditions

Stop and ask the user if any of the following occur:

- repo branch/remote policy is unclear;
- source behavior is ambiguous;
- backend capability appears undocumented;
- tests reveal unexpected firmware/controller behavior;
- task requires deciding a vendor export format;
- task requires push-to-device workflow;
- task requires interpreting Smash gameplay semantics;
- task requires changing Senscope neutral profile schema;
- task requires coupling controller constraints into game semantic solving;
- task requires unsafe or destructive Git commands;
- implementation would depend on inferred behavior rather than source-backed behavior.

## Autonomy tiers

Use the tier specified by the active task or queue.

### Tier 1 — autonomous

Proceed through implementation, tests, commit, and push when branch policy is clear. Stop only for forbidden actions, failing verification, or explicit stop conditions.

Good for:

- docs;
- inventory;
- small refactors;
- tests;
- helper extraction;
- source-map generation.

### Tier 2 — autonomous with stop conditions

Proceed unless a listed stop condition is hit.

Good for:

- capability-model scaffolding;
- evaluator prototypes;
- diagnostics;
- adapter boundary code;
- behavior-preserving migrations.

### Tier 3 — ask first

Do not implement without explicit user/domain approval.

Required for:

- claiming undocumented controller behavior;
- export/push workflows;
- neutral profile schema changes;
- firmware behavior changes;
- hard architecture commitments;
- gameplay/domain semantics.

## Final report format

Every implementation task must end with a concise report:

```text
Summary:
- ...

Files changed:
- ...

Verification:
- command: result

Behavior changes:
- none / described

Semantic changes:
- none / described

Backend behavior claims:
- none / source-backed / inferred / unknown

Stop conditions hit:
- none / described

Follow-ups:
- ...
```

If verification was not run, state why.

## Current project emphasis

The current near-term direction is to inspect and model Glyph/HayBox-style backend behavior for possible Senscope integration.

Do not implement runtime backend adapters until the inventory/design has been reviewed.

Do not choose or alter Senscope game-semantic sources.
