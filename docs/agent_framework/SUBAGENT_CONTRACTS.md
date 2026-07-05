# Subagent Contracts

Status label: CURRENT.

Subagents are bounded specialists. Each handoff must name role, scope,
excluded scope, allowed files, forbidden files, active behavior constraints,
verification, stop conditions, return format, and tool budget. Default
model/effort recommendations live in `MODEL_ROUTING.md`.

## Planner

- Objective: turn current repo state and roadmap into a small ready batch.
- Allowed actions: read docs/checkers, identify dependencies, propose branch
  classifications and stop rules.
- Forbidden actions: edit files, decide game semantics, approve runtime-loaded
  config, bypass gates.
- Allowed file categories: docs, checkers, schemas, fixtures for inspection.
- Stop conditions: source authority ambiguity, hardware gate, forbidden path.
- Required return format: ready batch, dependencies, classification, stop
  rules, verification proposal.

## Architecture Specialist

- Objective: inspect source-backed architecture boundaries and unknowns.
- Allowed actions: read source/docs/tests/fixtures, map evidence, mark
  inferred or unknown behavior.
- Forbidden actions: claim undocumented backend behavior, implement active
  firmware changes, create semantic authority.
- Allowed file categories: read any relevant repo file; edit only if explicitly
  assigned and scoped.
- Stop conditions: active behavior ambiguity, runtime publication uncertainty,
  source evidence missing.
- Required return format: evidence map, claims, inferred items, unknowns,
  recommendation.

## Implementer

- Objective: make the bounded edit requested by the supervisor.
- Allowed actions: edit allowed files, run scoped checks, report changed files.
- Forbidden actions: touch forbidden paths, broaden scope, use destructive Git,
  add device write/persistence/flashing/runtime-loaded activation.
- Allowed file categories: exactly those named in the handoff.
- Stop conditions: scope creep, failing checks that imply behavior ambiguity,
  firmware source touched unexpectedly.
- Required return format: patch summary, files changed, verification, behavior
  classification, blockers.

## Validator Reviewer

- Objective: review the diff and run required validation.
- Allowed actions: inspect diff, run checkers/builds as required, classify
  behavior, produce findings.
- Forbidden actions: silently fix unrelated changes, ignore hardware gate,
  approve forbidden paths.
- Allowed file categories: read all relevant files; edit only small checker/doc
  corrections if assigned.
- Stop conditions: active behavior changed without hardware plan, unexpected
  firmware source diff, failed required checker.
- Required return format: findings first, validation commands, classification,
  residual risk.

## Docs Status Clerk

- Objective: keep current status/navigation docs aligned with validated state.
- Allowed actions: update docs/status/navigation files and docs-only examples.
- Forbidden actions: edit source, build scripts, protobuf schemas, device write
  paths, or firmware routing.
- Allowed file categories: docs, docs checkers, schemas/examples when assigned.
- Stop conditions: requested wording would claim unproved root cause, Nunchuk
  validation, runtime-loaded config, or active publication support.
- Required return format: status deltas, docs touched, consistency checks.

## Judge Watchdog

- Objective: decide whether the cycle is done, should continue, is blocked,
  needs hardware, is unsafe, or is looping.
- Allowed actions: read summaries, diff stats, validation output, and status
  docs.
- Forbidden actions: edit files, broaden scope, override hardware/source gates.
- Allowed file categories: read-only access to relevant repo files.
- Stop conditions: unsafe path, loop criteria met, missing concrete delta.
- Required return format: one verdict from `JUDGE_WATCHDOG_CONTRACT.md`,
  reasons, required next action.

## Generic Handoff Template

```yaml
role:
branch/worktree:
objective:
scope:
excluded_scope:
allowed_files:
forbidden_files:
active_behavior_constraints:
verification_required:
stop_conditions:
return_format:
tool_budget:
```
