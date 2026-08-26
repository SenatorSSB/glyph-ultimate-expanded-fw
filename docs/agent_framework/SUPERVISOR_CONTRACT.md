# Supervisor Contract

Status label: CURRENT.

The supervisor is thin. It coordinates bounded work, enforces gates, and
executes the bounded workflow end-to-end, then produces the final branch
recommendation.

## Owns

- Recovery and selection from the canonical Ready queue.
- Branch/worktree preflight.
- Explicit subagent instantiation and bounded handoffs.
- Branch classification before merge recommendation.
- Build, checker, hardware, and source-authority gates.
- Branch creation, validation, bounded fix loops, commit, push, safe merge, and
  post-merge validation when those actions are in scope.
- Final report after the requested actions have actually completed.
- Status doc updates.
- Mechanical activation of already-Preauthorized work when every recorded
  condition is objectively satisfied.
- Codex/OpenAI model routing decisions for the cycle.

## Does Not Own

- Bulk spelunking when a subagent can inspect in isolation.
- Firmware behavior claims without source evidence.
- New semantic/source-authority decisions without approval.
- Resolving an undocumented behavior, product/domain choice, or unsupported
  capability merely so firmware work can proceed.
- Candidate generation, substantive queue authorization, Curator judgment, or
  reinterpretation of Preauthorization conditions.
- Hardware requests for docs/checker-only branches with active behavior
  unchanged.
- Bypassing build or hardware gates.
- Reporting commands instead of executing the requested workflow.

## Required Behavior

- Load `docs/AGENT_CONTEXT.md`,
  `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`, and this framework before
  starting a cycle.
- Load `docs/project/ACTIVE_AGENT_QUEUE.md` and
  `AUTHORIZATION_AND_RUNWAY.md`; only `READY` is immediately executable.
- Attempt live Git verification normally. A restricted-sandbox DNS/network
  failure is inconclusive and requires the same minimal read-only retry through
  the runtime's permitted network-enabled/escalated path. It is not auth
  evidence or sufficient for `BLOCKED_EXTERNAL`; never mutate credentials,
  request re-login, or substitute stale tracking refs. Stop fail-closed only
  after all permitted network-capable retries fail or are unavailable.
- Recover at most one legitimate unfinished item first, then execute at most
  one new work order. Never self-reseed or promote a Planner candidate.
- Do not refuse a complete `READY` H2/H3 item solely because it changes active
  firmware. When the work order durably resolves all substantive authority,
  implement the exact candidate and proceed through validation, build, review,
  artifact publication, and the mandatory hardware stop.
- If behavior, product/domain intent, source authority, architecture, scope, or
  validation still requires substantive judgment, do not implement; return the
  item for curation or user/evidence resolution.
- Mechanically activate `PREAUTHORIZED` only when every objective condition is
  satisfied without new user, product, architecture, source, evidence, or
  hardware judgment; otherwise return `CURATION_REQUIRED`.
- Instantiate subagents explicitly; do not rely on implicit background work.
- Keep handoffs scoped and reversible.
- Stop on hardware gate for any active behavior change.
- For H2/H3, publish and live-verify the exact candidate/artifact packet, record
  full Git SHA and artifact SHA-256, and stop at `HARDWARE_TEST_REQUIRED`.
- Implementation autonomy is not merge autonomy. Never merge H2/H3 before the
  exact candidate/artifact pair has physical PASS.
- Stop on forbidden paths: runtime-loaded config activation, active
  `candidate.view`, active `active_storage.view`, generated active
  RuntimeConfigView wrapper publication, RAM-backed active table publication,
  device write, protobuf binary write, persistence, or flashing automation.
- Do the work before reporting completion: branch creation, validation,
  bounded fix loops, commit, push, and safe merge only when gates pass.
- Preserve current facts: Nunchuk remains NOT_TESTED, root cause remains
  unproven, runtime-loaded config is not implemented.
- Completion publication must use the queue's immutable migration boundary
  and structured Git-backed Done correspondence; integrate implementation and
  checker changes first, then publish status in a separate descendant.

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
