# Glyph Agent Framework

Status label: CURRENT.

This directory installs durable supervisor/subagent contracts for Glyph
firmware-backend work. It is documentation, schemas, examples, and checkers
only. It does not implement a runner, daemon, scheduled automation, browser or
device write path, runtime-loaded profile, or active firmware routing change.
Current operations are Codex/OpenAI-only, and the supervisor is expected to
execute the bounded workflow itself rather than merely report shell commands
for a human to run. The selected mode is one fresh chapter daemon with event-driven bounded
workers/gates and a hard manual H2/H3 hardware lane. Fresh daemons must read
[FUTURE_DAEMON_BOOTSTRAP.md](FUTURE_DAEMON_BOOTSTRAP.md) on their first turn.
No standing Implementation, Planner or Curator schedules are the default.

## Scope

Current progression is Revision 3 (GLYPH-UD-027), defined in
VALIDATION_AND_GATES.md: Tier 1 always blocks, Tier 2 blocks when directly
affected, Tier 3 is tracked framework debt unless a concrete Tier-1/Tier-2
contradiction exists. Preserve historical Revision-2 evidence and exact
hardware/source safety; no false aggregate PASS or recursive meta-campaign.
GLYPH-UD-028 authorizes known-campaign orchestration transport only, with
durable polling fallback; it creates no action authority or concurrent writer.

Repo-only scope:

- Glyph / HayBox firmware-backend behavior and realization boundaries.
- Docs, checkers, source-owned generator design, and reviewable source-owned
  firmware artifacts.
- Senscope boundary statements only: Senscope owns game semantics, datasets,
  and solver authority; Glyph realizes deterministic raw-coordinate output.

Out of scope:

- Custom-runner prompt or implementation.
- `scripts/agent_runner.py`.
- External schedule mutation without explicit owner authorization; repository
  task configurations alone do not change external schedules.
- Browser/device writes.
- WebSerial/device write.
- Protobuf binary write.
- Backend config.pb write.
- Persistent runtime-config storage.
- Flashing automation.
- Runtime-loaded profile/config activation.
- Non-Codex agent surfaces without a separate approved docs branch.

## Topology

Use separated generation, judgment, execution, and evidence roles as needed.

Role existence is not a quota. Instantiate Planner only for actual planning or
candidate-supply need, Curator only for real authority/adjudication, independent
reviewer only for a required mutation/evidence review, and HEP only after human
physical observations exist. Specialists and executors require a useful bounded
transition; do not create a role merely to report WAITING or restate known state.
One clean executor may carry an already-authorized coherent chain to the next
real hardware/domain/authority stop, within its recorded scope and successor
limits; it may not self-reseed. One independent review layer is normally
sufficient. Do not create reviewer-of-reviewer chains unless a concrete new
defect found by the first review needs repair and distinct independent review.

Available roles (not a permanent topology):

- Portfolio Planner proposes non-authoritative candidate supply.
- Work-Order Curator independently authorizes complete Ready or narrowly
  Preauthorized work and owns the canonical queue.
- The Implementation Supervisor recovers legitimate work, executes at most one
  new authorized item, owns integrated mutation and publication, and never
  self-reseeds.
- The Hardware Evidence Processor validates and records human-supplied results
  for one exact candidate/artifact pair and never fabricates testing.
- Subagents inspect or edit within explicit scope and return compact evidence.
- Independent review checks loop risk and merge readiness. No watchdog is
  created by default; a future watchdog needs evidence of missed completion
  events and may only detect missed callbacks, executable transitions or durable
  owner waits. It must not plan, curate, implement or invent work.
- Long work is many bounded cycles, not one unbounded monolithic conversation.

## Contracts

- `FUTURE_DAEMON_BOOTSTRAP.md` - mandatory first-turn chapter operating contract.
- `MODEL_ROUTING.md` - current recommended model/effort routing and provenance.
- `PROMPT_TEMPLATES.md#optional-chapter-worker-roster` - optional chapter-scoped
  owner roster, worker bootstrap and direct-return packets; runtime support is
  conditional and grants no product or publication authority.
- `AUTHORIZATION_AND_RUNWAY.md` - authority map, Ready/Preauthorized semantics,
  packet freshness, runway, liveness, and concurrency.
- `WORK_ORDER_TEMPLATE.md` - complete executable/Preauthorized contract shape.
- `HARDWARE_EVIDENCE.md` - H0-H3 risk and exact-snapshot acceptance lane.
- `HARDWARE_CORRESPONDENCE.md` - audited critical-input exactness and separate
  validation of non-behavioral repository metadata.
- `HARDWARE_ARTIFACT_CUSTODY.md` - approved owner-held local content-addressed
  preservation, readback, retention, rebuild, and loss contract.
- `GP_CONFIG_005_INTEGRATION_RESULT_20260919.md` - consolidated exact integration,
  correspondence model, validation and completion report.
- `GP_CONFIG_010_INTEGRATION_HARDWARE_RESULT_20260923.md` - exact combined
  candidate/artifact physical PASS summary and source-free publication boundary.
- `GP_CONFIG_005_HARDWARE_OPERATOR.md` - bounded project-owner CLI runbook for
  the exact GP-CONFIG-005 physical protocol; it is not hardware evidence.
- `GP_CONFIG_010_INTEGRATION_HARDWARE_PROTOCOL.md` - bounded exact-artifact
  combined regression for the current-canonical GP-CONFIG-010 integration.
- `USER_DIRECTION.md` - actual human direction only.
- `SCHEDULED_TASKS.md` - current event-driven defaults and legacy/manual role templates;
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

## Persistent campaign execution under GLYPH-UD-029

**Historical authority only:** GLYPH-UD-029 governed the completed C020–C024
campaign. It is not standing authority for future chapters. The preserved
campaign rules below do not renew that campaign. Future chapters require fresh
owner-approved chapter scope and chapter-specific authority, the current queue
and contracts, and `docs/agent_framework/FUTURE_DAEMON_BOOTSTRAP.md`.

The verified owner directive GLYPH-UD-029 supersedes default one-new-order and
return-after-mechanical-transition rules within its named H3 and H1 chains.
Reuse the existing campaign executor through objective PREAUTHORIZED activation,
the ordinary governance successor, product resume, focused Revision-3 validation,
fresh independent review, exact committed build/custody and hardware handoff.
No new full chat, Planner or Curator is required for these mechanical transitions.
Live queue scope and substantive decisions remain authoritative. Retain exact
candidates; never merge behavior-changing H2/H3 before exact human HEP PASS.
The canonical publication lock permits one writer; isolated dedicated branch
work/review may proceed without that lock when frozen inputs remain unchanged.
Retain the H3 lock through the logical chain and release at hardware wait or a
genuine substantive stop. Rejected transport uses durable readback. Preserve
chronology: a historical pause cannot override a newer verified owner resume.
Within each named product chain, allow at most one ordinary governance successor
and one exceptional validation repair for a concrete Tier-1 or Tier-2 defect.
Any further successor requires direct owner approval. This limit prospectively
supersedes broader Revision-3 exception wording within these named chains;
historical policy and evidence remain preserved.
Track full chats, canonical commit SHAs, internal transitions versus handoffs,
READY-to-hardware and hardware-report-to-DONE times, no-op/Curator/Planner calls.
