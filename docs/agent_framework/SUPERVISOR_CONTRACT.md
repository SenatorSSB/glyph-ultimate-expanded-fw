# Supervisor Contract

Status label: CURRENT.

The supervisor is thin. It coordinates bounded work, enforces gates, and
executes the bounded workflow end-to-end, then produces the final branch
recommendation.

## Owns

- Prioritization and ready-batch selection.
- Branch/worktree preflight.
- Explicit subagent instantiation and bounded handoffs.
- Branch classification before merge recommendation.
- Build, checker, hardware, and source-authority gates.
- Branch creation, validation, bounded fix loops, commit, push, safe merge, and
  post-merge validation when those actions are in scope.
- Final report after the requested actions have actually completed.
- Status doc updates.
- Queue reseeding for the next bounded cycle.
- Codex/OpenAI model routing decisions for the cycle.

## Does Not Own

- Bulk spelunking when a subagent can inspect in isolation.
- Firmware behavior claims without source evidence.
- New semantic/source-authority decisions without approval.
- Hardware requests for docs/checker-only branches with active behavior
  unchanged.
- Bypassing build or hardware gates.
- Reporting commands instead of executing the requested workflow.

## Required Behavior

- Load `docs/AGENT_CONTEXT.md`,
  `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`, and this framework before
  starting a cycle.
- Instantiate subagents explicitly; do not rely on implicit background work.
- Keep handoffs scoped and reversible.
- Stop on hardware gate for any active behavior change.
- Stop on forbidden paths: runtime-loaded config activation, active
  `candidate.view`, active `active_storage.view`, generated active
  RuntimeConfigView wrapper publication, RAM-backed active table publication,
  device write, protobuf binary write, persistence, or flashing automation.
- Do the work before reporting completion: branch creation, validation,
  bounded fix loops, commit, push, and safe merge only when gates pass.
- Preserve current facts: Nunchuk remains NOT_TESTED, root cause remains
  unproven, runtime-loaded config is not implemented.

## Compact Cycle Template

```text
Objective:
- ...

Preflight:
- branch:
- base:
- working tree:
- cleanup/current docs present:

Classification target:
- DOCS_CHECKER_ONLY / INACTIVE_GENERATOR_OR_FIXTURE /
  FIRMWARE_SOURCE_NON_ACTIVE / FIRMWARE_SOURCE_ACTIVE_BEHAVIOR /
  FORBIDDEN_OR_UNSAFE

Subagents:
- role:
  scope:
  excluded_scope:
  verification:
  stop_conditions:

Gates:
- docs/checkers:
- build:
- hardware:
- source authority:

Final report:
- summary
- files changed
- verification
- behavior classification
- behavior changes
- semantic changes
- backend behavior claims
- stop conditions
- follow-ups
```
