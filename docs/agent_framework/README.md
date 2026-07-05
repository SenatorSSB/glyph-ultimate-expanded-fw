# Glyph Agent Framework

Status label: CURRENT.

This directory installs durable supervisor/subagent contracts for Glyph
firmware-backend work. It is documentation, schemas, examples, and checkers
only. It does not implement a runner, daemon, scheduled automation, browser or
device write path, runtime-loaded profile, or active firmware routing change.
Current operations are Codex/OpenAI-only.

## Scope

Repo-only scope:

- Glyph / HayBox firmware-backend behavior and realization boundaries.
- Docs, checkers, source-owned generator design, and reviewable source-owned
  firmware artifacts.
- Senscope boundary statements only: Senscope owns game semantics, datasets,
  and solver authority; Glyph realizes deterministic raw-coordinate output.

Out of scope:

- Runner prompt.
- Runner implementation.
- `scripts/agent_runner.py`.
- Browser/device writes.
- WebSerial/device write.
- Protobuf binary write.
- Backend config.pb write.
- Persistent runtime-config storage.
- Flashing automation.
- Runtime-loaded profile/config activation.
- Non-Codex agent surfaces without a separate approved docs branch.

## Topology

Use a thin supervisor with bounded specialist subagents:

- The supervisor owns prioritization, branch classification, gates, handoffs,
  merge recommendation, status updates, and queue reseeding.
- Subagents inspect or edit within explicit scope and return compact evidence.
- The judge/watchdog reviews loop risk and merge readiness.
- Long work is many bounded cycles, not one unbounded monolithic conversation.

## Contracts

- `MODEL_ROUTING.md` - current recommended model and effort routing.
- `SUPERVISOR_CONTRACT.md` - supervisor ownership and cycle contract.
- `SUBAGENT_CONTRACTS.md` - specialist role contracts and handoff template.
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
