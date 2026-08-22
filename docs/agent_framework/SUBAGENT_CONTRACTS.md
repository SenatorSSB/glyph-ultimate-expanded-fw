# Subagent Contracts

Status label: CURRENT.

Subagents are bounded specialists. Each handoff must name role, scope,
excluded scope, allowed files, forbidden files, active behavior constraints,
verification, stop conditions, return format, and tool budget. Default
Codex/OpenAI model/effort recommendations live in `MODEL_ROUTING.md`.

Prompt labels such as `read-only`, `allowed_files`, and `forbidden_files` are
coordination contracts, not mechanically enforced filesystem isolation. Root
must inspect shared-worktree status/diffs and attribute unexpected mutations
before integration. When hard read-only enforcement is required, use an
actually isolated/read-only execution environment rather than relying on the
prompt label.

## Planner

- Objective: produce broad, non-authoritative current-`configurator` candidate
  supply and assess packet freshness/consumption.
- Allowed actions: read source/docs/checkers/tests/fixtures/evidence, identify
  bottlenecks and dependencies, create a live-verified `planning/portfolio-*`
  packet when material.
- Forbidden actions: edit product code or canonical queue, mark Ready or
  Preauthorized, decide game semantics, fabricate user direction, infer global
  evidence scarcity from candidate-local gates, approve runtime-loaded config,
  or merge planning output to `configurator`.
- Required return format: base SHA, packet freshness, broad-audit scope,
  candidates with non-authoritative readiness estimates, rejected
  alternatives, exact gates, and whether `GLOBAL_EVIDENCE_WAIT_SUPPORTED` is
  proposed with a resume event.

## Work-Order Curator

- Objective: independently judge Planner candidates and own the canonical
  Ready/Preauthorized queue.
- Allowed actions: verify current gaps, authorize zero or more complete work
  orders, narrowly Preauthorize mechanical successors, disposition enough
  supply for the throughput-aware target, handle invalidation, and edit only
  directly coupled control-plane contract tests under the anti-cheating rule.
- Forbidden actions: implement firmware/configurator product code, edit
  runtime/product tests, rubber-stamp Planner scores, invent and authorize a
  materially new idea in one step, or weaken governance invariants.
- Required return format: live base, packet/provenance, runway before/after,
  candidate dispositions, authorizations, Planner refresh signal, validation,
  and runtime product code changed: NO.

## Hardware Evidence Processor

- Objective: validate and record human-supplied controller results for one
  exact candidate Git SHA and firmware artifact SHA-256.
- Allowed actions: verify protocol/result completeness and source drift, record
  PASS/FAIL/PARTIAL/INCONCLUSIVE, and update evidence/control-plane state.
- Forbidden actions: perform or fabricate the physical test, edit runtime
  source, reinterpret incomplete evidence as PASS, or publish source to
  `configurator`.
- Required return format: identity match, protocol completeness, result,
  evidence branch/SHA, queue disposition, and exact repair/retest/publication
  next action.

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
