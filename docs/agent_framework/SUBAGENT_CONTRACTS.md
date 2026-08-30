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

## Native Delegation Discovery And Accountability

Native internal subagent delegation means scoped child agents, sidecars, or
reviewers created by the current root run. They return results to that root;
the root retains integrated mutation, authoritative validation, Git,
publication, status, and final authority.

User-owned task, thread, conversation, or Automation creation starts a separate
user-visible job. It is distinct from and not equivalent to native internal
subagent delegation. A root must not present user-owned job creation as the
only delegation mechanism when a native internal facility exists, and must not
replace a required independent reviewer with a suggestion to create another
user task or thread.

Before substantive implementation or research, when repository guidance or
the selected role calls for subagent use, the root must perform this delegation
preflight:

1. Determine whether repository delegation guidance applies.
2. Inspect the complete available runtime capability/tool catalog, or use the
   runtime's supported capability-discovery mechanism, before declaring native
   delegation unavailable. Absence from the initial visible tool manifest or
   tool list is insufficient evidence of unavailability and the initial
   manifest must not be treated as exhaustive.
3. Determine whether a native internal subagent facility is available without
   hardcoding one runtime-specific tool name as the only valid backend.
4. Identify useful separable specialist tasks and required independent review.
5. Record every delegated role and objective. If no native subagent is used,
   record the exact reason.

Acceptable no-subagent reasons include a true no-op cycle; a trivial mechanical
task with no useful separable investigation, provided any independently
required review is still satisfied; complete capability discovery confirming
that no native facility exists; a runtime failure after attempted discovery or
child creation; or a concurrency/safety stop before substantive work. "No
tools were visible initially" is never an acceptable reason.

For a normal Implementation cycle that mutates repository state, a fresh
independent post-implementation reviewer is required when native capability is
available. The root may not self-review as a substitute. The reviewer receives
the exact work-order objective, scope, and exclusions; the exact diff or
changed-area description; relevant evidence and contracts; validation results;
and an instruction to look for material correctness, safety, authority, scope,
publication, and regression defects. The root repairs material findings and
obtains re-review of repaired areas.

Use at least one additional bounded specialist when a materially separable
investigation exists. Examples include source/upstream history, source
authority, schema/contract, build/test gaps, provenance/evidence, firmware
safety, and recovery/lineage. Do not create specialist work merely to satisfy a
quota; reviewer-only is acceptable for a small mechanical implementation with
no meaningful separable research.

For active firmware or H2/H3 work, normally use at least one bounded
source-authority or firmware-safety specialist and a separate fresh independent
reviewer. Use additional build/evidence help when warranted. This adds no new
user-approval gate: a complete `READY` H2/H3 contract remains executable to its
existing exact-snapshot hardware stop.

Planner should use parallel read-heavy specialists when a broad audit can be
cleanly partitioned, while avoiding arbitrary parallelism for a tiny candidate
surface. Planner and its helpers remain non-authoritative. Curator may use
bounded verification specialists for separable source, evidence, validation,
or hardware-risk checks, but Curator retains the final substantive
authorization judgment. Hardware Evidence Processor uses a fresh reviewer for
a result-bearing evidence mutation when native capability exists; that reviewer
may validate identity, correspondence, and schema but must not invent physical
observations.

Every affected root task prompt must require this final-report evidence:

```text
Delegation:
- guidance applicable:
- capability discovery:
- native capability available:
- specialists used:
- reviewer used:
- if none, reason:
```

This is per-run audit evidence, not canonical queue telemetry.

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

## Implementation Supervisor cycle — GP-PROV-006 recovery (2026-08-30)

- guidance applicable: yes; GP-PROV-006 is a complete H0 READY work order and
  the supervisor requires bounded delegation plus fresh independent review for
  repository mutation.
- capability discovery: complete runtime tool catalog inspected; native
  internal subagent facility confirmed available.
- native capability available: yes.
- specialist: source/contract specialist; inspect the recovered GP-PROV-006
  partial state against the exact READY scope, source identities, finite INI
  chain, literal/reference correspondence, and excluded PlatformIO/compiler
  claims; read-only, no file edits.
- reviewer: fresh validator reviewer after implementation; inspect the exact
  diff and run the required offline gates for correctness, authority, scope,
  publication, and regression defects; no unrelated edits.
- allowed specialist files: current GP-PROV-006 docs/fixture/checker state and
  platformio.ini/config/glyph/env.ini plus relevant checker contracts.
- forbidden specialist actions: edits, PlatformIO/compiler/build execution,
  dependency/network access, runtime or firmware claims.
- stop conditions: source drift, missing exact correspondence, scope creep, or
  any need to interpret PlatformIO/compiler behavior.
- return format: findings first; exact contract matches/gaps; recommended
  bounded next action.

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
