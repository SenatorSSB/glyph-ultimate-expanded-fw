# Glyph Agent Framework

Status label: CURRENT.

This directory installs durable supervisor/subagent contracts for Glyph
firmware-backend work. It is documentation, schemas, examples, and checkers
only. It does not implement a runner, daemon, scheduled automation, browser or
device write path, runtime-loaded profile, or active firmware routing change.
Current operations are Codex/OpenAI-only, and the supervisor is expected to
execute the bounded workflow itself rather than merely report shell commands
for a human to run. The selected mode is a Minimal Supervisor with on-demand
consultative Planner/Curator roles and a hard manual H2/H3 hardware lane.

## Scope

Repo-only scope:

- Glyph / HayBox firmware-backend behavior and realization boundaries.
- Docs, checkers, source-owned generator design, and reviewable source-owned
  firmware artifacts.
- Senscope boundary statements only: Senscope owns game semantics, datasets,
  and solver authority; Glyph realizes deterministic raw-coordinate output.

Out of scope:

- Custom-runner prompt or implementation.
- `scripts/agent_runner.py`.
- External schedule mutation; repository task configurations are documentation
  only.
- Browser/device writes.
- WebSerial/device write.
- Protobuf binary write.
- Backend config.pb write.
- Persistent runtime-config storage.
- Flashing automation.
- Runtime-loaded profile/config activation.
- Non-Codex agent surfaces without a separate approved docs branch.

## Topology

Use separated generation, judgment, execution, and evidence roles:

- Portfolio Planner proposes non-authoritative candidate supply.
- Work-Order Curator independently authorizes complete Ready or narrowly
  Preauthorized work and owns the canonical queue.
- The Implementation Supervisor recovers legitimate work, executes at most one
  new authorized item, owns integrated mutation and publication, and never
  self-reseeds.
- The Hardware Evidence Processor validates and records human-supplied results
  for one exact candidate/artifact pair and never fabricates testing.
- Subagents inspect or edit within explicit scope and return compact evidence.
- The judge/watchdog reviews loop risk and merge readiness.
- Long work is many bounded cycles, not one unbounded monolithic conversation.

## Contracts

- `MODEL_ROUTING.md` - current recommended model and effort routing.
- `AUTHORIZATION_AND_RUNWAY.md` - authority map, Ready/Preauthorized semantics,
  packet freshness, runway, liveness, and concurrency.
- `WORK_ORDER_TEMPLATE.md` - complete executable/Preauthorized contract shape.
- `HARDWARE_EVIDENCE.md` - H0-H3 risk and exact-snapshot acceptance lane.
- `USER_DIRECTION.md` - actual human direction only.
- `SCHEDULED_TASKS.md` - exact copy-paste scheduled/manual role configurations;
  it does not create schedules.
- `SUPERVISOR_CONTRACT.md` - supervisor ownership and cycle contract.
- `SUBAGENT_CONTRACTS.md` - canonical native-delegation discovery,
  accountability, specialist, reviewer, and handoff contract.
- `CYCLE_STATE_MACHINE.md` - bounded cycle state machine.
- `JUDGE_WATCHDOG_CONTRACT.md` - verdicts and anti-looping rules.
- `VALIDATION_AND_GATES.md` - branch classifications and merge gates.
- `STATUS_DOC_CONTRACT.md` - current-state and status document ownership.
- `PROMPT_TEMPLATES.md` - supervisor and subagent prompt templates.
- `RUNNER_BOUNDARY.md` - explicit runner non-goals.
- `schemas/` - JSON schemas for handoffs, reports, branch contracts, and
  model routing.
- `examples/` - concise Glyph-context examples.

## Branch Classifications

Every branch must be classified before merge recommendation:

- `DOCS_CHECKER_ONLY`: Docs, examples, JSON schemas, or Python checkers only;
  active firmware behavior unchanged. Hardware is not required.
- `INACTIVE_GENERATOR_OR_FIXTURE`: Generator, fixture, or inactive artifact work
  that does not change active firmware behavior. Build/checker requirements
  depend on touched files; hardware is not required unless active behavior is
  changed.
- `FIRMWARE_SOURCE_NON_ACTIVE`: Firmware source touched, but evidence shows the
  active path is unchanged. Build proof is required; hardware may be required
  if uncertainty remains.
- `FIRMWARE_SOURCE_ACTIVE_BEHAVIOR`: Active firmware behavior or active
  RuntimeConfigView selection changes. Build proof and hardware PASS are
  required before merge.
- `FORBIDDEN_OR_UNSAFE`: Runtime-loaded config activation, active
  `candidate.view`, active `active_storage.view`, generated active
  RuntimeConfigView wrapper publication, RAM-backed active table publication,
  device write, protobuf binary write, persistence, flashing automation, or
  source-authority bypass. Stop.

Current evidence boundary: active publication remains source-owned through
`GetActiveRuntimeConfigState()`, `ResolveActiveRuntimeConfig()`, and
`&kSourceOwnedCurrentBaselineRuntimeConfig`. Runtime-loaded config is not
implemented. Nunchuk remains NOT_TESTED. Root cause remains unproven.

The canonical executable queue is
`docs/project/ACTIVE_AGENT_QUEUE.md`. Only `READY` is immediately executable;
Planner packets, roadmap prose, and branch names never authorize work.
