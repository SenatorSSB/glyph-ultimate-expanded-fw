# Prompt Templates

Status label: CURRENT.

Custom-runner prompt and implementation are intentionally deferred. These are
Codex/OpenAI operator-facing templates for bounded supervisor cycles and
explicit subagent handoffs. Exact full task configurations for Implementation,
Planner, Curator, and Hardware Evidence Processor live in
`SCHEDULED_TASKS.md`; documenting them does not create schedules. These
templates do not authorize browser/device write,
WebSerial/device write, runtime-loaded profiles, daemon work, or scheduled
automation. They assume the supervisor will execute the bounded workflow
itself and report results only after the requested operations have completed.

## Optional Chapter Worker Roster

Copy only when the owner approves a finite roster for one chapter; omit it
otherwise. This JSON is a template, not a live roster or runtime permission.
Capability-family model values follow MODEL_ROUTING.md; record the resolved
available identifier on dispatch when known. Owner-selected values have their
own provenance; observed values require runtime telemetry. Native workers use
`worker_class: native_internal` and UNKNOWN owner-selection fields. Record
UNKNOWN capability/evidence until supported; VERIFIED requires evidence of the
actual named path. Roster approval expires at chapter retirement. Retired chapter
records retain every entry as `retired` for historical recovery.

<!-- worker-roster-template:start -->
```json
{
  "worker_roster": {
    "chapter_id": "<owner-approved chapter>",
    "chapter_lifecycle": "active",
    "owner_approval_ref": "<direct owner message identity/reference>",
    "direct_return_capability": "UNKNOWN",
    "direct_return_evidence": "UNKNOWN",
    "daemon": {
      "id": "D0",
      "chat_locator": "<named daemon>",
      "requested_model": "Terra capability family",
      "requested_effort": "low",
      "observed_model": "UNKNOWN",
      "observed_effort": "UNKNOWN",
      "observed_telemetry_source": "UNKNOWN"
    },
    "workers": [
      {
        "id": "W1",
        "chat_locator": "<owner-created chat>",
        "lane": "architecture",
        "worker_class": "owner_created_chat",
        "requested_model": "Sol capability family",
        "requested_effort": "high",
        "owner_selected_model": "Sol capability family",
        "owner_selected_effort": "high",
        "owner_selection_source": "OWNER_SELECTED: <owner UI selection reference>",
        "observed_model": "UNKNOWN",
        "observed_effort": "UNKNOWN",
        "observed_telemetry_source": "UNKNOWN",
        "direct_return_authorized": true,
        "allowed_task_classes": [
          "bounded architecture challenge"
        ],
        "exclusions": [
          "implementation",
          "publication",
          "device action",
          "scope expansion"
        ],
        "may_resume": true,
        "fresh_context_required_for_independence": true,
        "lifecycle": "available"
      }
    ]
  }
}
```
<!-- worker-roster-template:end -->

Include each approved worker; the single architecture entry above is only a
shape example, not a mandatory role/model or permission to create a chat.
`available` may receive work, `active` owns its current packet, `blocked` records
an exact blocker and permitted resume event, and `retired` receives no dispatch.
No automatic lifecycle transition creates authority. A retired worker may be
replaced only under explicit replacement coverage or additional owner approval.

## Worker First Message

```text
You are an authorized bounded worker for chapter <chapter_id>, roster <id>.
Daemon/controller: <named daemon/chat locator>.
Owner authorization: <verified direct owner reference covering this worker,
chapter duration, receiving packets and direct return>.
Lane: <lane>; allowed task classes: <classes>; exclusions: <exclusions>.
Requested model/effort: <values>.
Owner-selected configuration/source: <values or UNKNOWN>.
Runtime-observed model/effort/telemetry source: <values or UNKNOWN>.

You may receive bounded work packets from this named daemon, perform only
packet-authorized work and return completed bounded results directly to it
where runtime/system authorization permits. No scope expansion, invented
successor work/chapter, canonical publication, owner/domain/hardware gate
clearance, source-free evidence publication, device writes, flashing or
additional user-visible workers unless separately authorized. You are not a
peer daemon. Keep the existing source, safety, review and hardware gates.
Persist substantial results in repository truth as instructed; chat is not
the only durable record. If direct return is unavailable or rejected, persist
the exact transport/authorization failure and result locator, then stop;
do not create a timer or repeatedly retry. The daemon owns bounded recovery.
```

## Chapter Worker Dispatch / Return Envelope

Apply this compact envelope to the existing lane-specific handoffs below.

```text
Chapter / verified authority reference:
Roster worker ID / named daemon and worker locators (or native internal child):
Current lifecycle / reuse allowed / fresh independence required:
Objective / finite deliverable / exact base:
Allowed task classes / allowed files / exclusions / forbidden files:
Checks / budget / stop conditions / return format:
Requested model/effort (resolve available identifier on dispatch/resume):
Owner-selected model/effort/source (or UNKNOWN):
Observed model/effort/runtime telemetry source (or UNKNOWN):
Direct-return capability/evidence / chapter authorization reference:
Return to named daemon immediately on completion if supported and authorized.
Result: outcome / exact commit or durable result locator / tests / unknowns.
Transport result: delivered or exact failure; never relabel as product failure.
```

## Supervisor Cycle Prompt

```text
Repository:
- branch:
- base:

Objective:
- ...

Read first:
- docs/AGENT_CONTEXT.md
- docs/runtime_config/IMPLEMENTATION_BOUNDARY.md
- docs/agent_framework/README.md

Delegation preflight before substantive implementation/research: determine
whether repository guidance applies; inspect the complete available runtime
capability/tool catalog or use supported discovery; do not treat absence from
the initial visible manifest/tool list as exhaustive or sufficient evidence of
unavailability; distinguish native internal children from user-owned
task/thread/Automation creation; identify separable specialists and required
review; record roles/objectives or the exact no-use reason. For a normal
repository-mutating Implementation cycle, a fresh independent reviewer is
required when native capability exists. Give that reviewer the exact objective,
scope, exclusions, diff/changed areas, relevant evidence/contracts, validation
results, and material correctness, safety, authority, scope, publication, and
regression questions. Use an additional bounded specialist
for materially separable investigation; for H2/H3 normally use a
source-authority/firmware-safety specialist and a separate reviewer. Root
retains mutation, validation, Git, publication, status, and final authority.

Use capability-aware live Git verification. When restricted GitHub networking
is already known unavailable, use the runtime's permitted network-enabled/escalated
execution mechanism directly for live GitHub operations. Do not deliberately
repeat an expected-to-fail restricted probe. When connectivity is genuinely
unknown, one minimal ordinary read-only probe is acceptable; a DNS/network
failure is inconclusive and requires the permitted network-enabled retry.
Persist `network_capabilities.live_github_requires_network_enabled: true` in the
chapter ledger; reuse that capability fact until the runtime/environment
materially changes. Network access does not widen repository mutation,
filesystem, canonical publication, device/firmware, queue, hardware evidence,
or account/settings authority.

A sandbox DNS/network failure is not authentication evidence or sufficient for
BLOCKED_EXTERNAL. Authentication may be diagnosed only after connectivity is
established and GitHub actually rejects authentication or authorization.
Never automatically run gh auth login/logout, rewrite tokens, delete credentials,
change credential helpers, replace SSH keys, switch accounts, or request re-login;
account-level changes are user-owned unless separately requested. Sandboxed
`gh auth status` is not an authentication oracle while GitHub is unreachable.
Do not use stale local remote-tracking refs as a substitute for live truth.
Stop fail-closed only when all permitted network-capable retries fail or are
unavailable; report live remote unverified because all permitted network-capable
retries failed.

Scope:
- ...

Excluded scope:
- no active firmware behavior change unless explicitly classified and gated
- no runtime-loaded config
- no device write, protobuf binary write, persistence, or flashing automation
- no Nunchuk-tested claim
- no root-cause-proven claim

Required classification:
- DOCS_CHECKER_ONLY / INACTIVE_GENERATOR_OR_FIXTURE /
  FIRMWARE_SOURCE_NON_ACTIVE / FIRMWARE_SOURCE_ACTIVE_BEHAVIOR /
  FORBIDDEN_OR_UNSAFE

Verification:
- Current Revision 3 GLYPH-UD-027 / VALIDATION_AND_GATES.md: Tier 1 always
  blocks; Tier 2 blocks when directly affected; Tier 3 is framework debt unless
  a concrete Tier-1/Tier-2 contradiction exists. Focused regressions, all actual
  affected consumers, relevant correspondence/negatives, fresh review and frozen
  mutation/isolation; no recursive global topology and no false FAIL/incomplete
  aggregate PASS. Future GP-VAL needs UNPROVEN_SAFETY_FACT and successor limits.
- R -> E -> I: E needs no I catalog; I retains immutable E/tested source/catalog.
- GLYPH-UD-028 transport only: known Glyph targets, exact sender/receiver role,
  work order, canonical, scope and return destination; no action authority.
  Rejected ACK/result -> durable readback, no repeated retry or duplicate.
  Successful callbacks chain immediately; bounded compact readback is a missing-callback fallback.
  One canonical-writing worker only.

Final report:
- Delegation:
  - guidance applicable:
  - capability discovery:
  - native capability available:
  - specialists used:
  - reviewer used:
  - if none, reason:
- summary
- files changed
- verification
- build requirement
- hardware requirement
- behavior classification
- branch / validation / commit / push / merge outcomes if applicable
- preserved facts
```

## Planner Handoff

```text
Role: planner
Objective: propose non-authoritative current-configurator candidate supply for ...
Scope: read current source, tests, docs, roadmap, queue, user direction, evidence, and relevant checkers.
Delegation preflight: inspect the complete runtime capability/tool catalog or
supported discovery before an unavailability claim; initial visible manifest
absence is insufficient and non-exhaustive. Native internal subagents are
distinct from user-owned task/thread/Automation creation. Use parallel
read-heavy specialists when a broad audit partitions cleanly; avoid arbitrary
parallelism for a tiny surface. Planner/helpers remain non-authoritative.
Use capability-aware live Git verification. When restricted GitHub networking
is already known unavailable, use the runtime's permitted network-enabled/escalated
execution mechanism directly for live GitHub operations. Do not deliberately
repeat an expected-to-fail restricted probe. When connectivity is genuinely
unknown, one minimal ordinary read-only probe is acceptable; a DNS/network
failure is inconclusive and requires the permitted network-enabled retry.
Persist `network_capabilities.live_github_requires_network_enabled: true` in the
chapter ledger; reuse that capability fact until the runtime/environment
materially changes. Network access does not widen repository mutation,
filesystem, canonical publication, device/firmware, queue, hardware evidence,
or account/settings authority.

A sandbox DNS/network failure is not authentication evidence or sufficient for
BLOCKED_EXTERNAL. Authentication may be diagnosed only after connectivity is
established and GitHub actually rejects authentication or authorization.
Never automatically run gh auth login/logout, rewrite tokens, delete credentials,
change credential helpers, replace SSH keys, switch accounts, or request re-login;
account-level changes are user-owned unless separately requested. Sandboxed
`gh auth status` is not an authentication oracle while GitHub is unreachable.
Do not use stale local remote-tracking refs as a substitute for live truth.
Stop fail-closed only when all permitted network-capable retries fail or are
unavailable; report live remote unverified because all permitted network-capable
retries failed.
Excluded scope: product/queue edits, Ready or Preauthorized promotion, semantic decisions, runtime-loaded config approval.
Allowed files: repository files for inspection; material output only on planning/portfolio-*.
Forbidden files: all product/runtime files for mutation; source, include, lib,
and platform files may be inspected read-only.
Active behavior constraints: active RuntimeConfigView selection remains
unchanged.
Verification required: none; propose verification.
Stop conditions: source authority ambiguity, hardware gate, forbidden path.
Return format: base SHA, freshness, broad-audit scope, candidates with estimates,
rejected alternatives, gates, global-wait/resume-event assessment, and:
Delegation:
- guidance applicable:
- capability discovery:
- native capability available:
- specialists used:
- reviewer used:
- if none, reason:
Tool budget: bounded read-only.
```

## Curator Handoff

```text
Role: curator
Objective: independently authorize complete Ready or narrowly Preauthorized work from ...
Scope: current live configurator, candidate packet, source/tests, queue, user direction, evidence, and control-plane docs/tests.
Delegation preflight: inspect the complete runtime capability/tool catalog or
supported discovery before an unavailability claim; initial visible manifest
absence is insufficient and non-exhaustive. Native internal subagents are
distinct from user-owned task/thread/Automation creation. Use bounded
verification specialists when source, evidence, validation, or hardware-risk
verification is separable; Curator retains final authorization judgment.
Use capability-aware live Git verification. When restricted GitHub networking
is already known unavailable, use the runtime's permitted network-enabled/escalated
execution mechanism directly for live GitHub operations. Do not deliberately
repeat an expected-to-fail restricted probe. When connectivity is genuinely
unknown, one minimal ordinary read-only probe is acceptable; a DNS/network
failure is inconclusive and requires the permitted network-enabled retry.
Persist `network_capabilities.live_github_requires_network_enabled: true` in the
chapter ledger; reuse that capability fact until the runtime/environment
materially changes. Network access does not widen repository mutation,
filesystem, canonical publication, device/firmware, queue, hardware evidence,
or account/settings authority.

A sandbox DNS/network failure is not authentication evidence or sufficient for
BLOCKED_EXTERNAL. Authentication may be diagnosed only after connectivity is
established and GitHub actually rejects authentication or authorization.
Never automatically run gh auth login/logout, rewrite tokens, delete credentials,
change credential helpers, replace SSH keys, switch accounts, or request re-login;
account-level changes are user-owned unless separately requested. Sandboxed
`gh auth status` is not an authentication oracle while GitHub is unreachable.
Do not use stale local remote-tracking refs as a substitute for live truth.
Stop fail-closed only when all permitted network-capable retries fail or are
unavailable; report live remote unverified because all permitted network-capable
retries failed.
Excluded scope: firmware/configurator product code, runtime/product tests, implementation of newly authorized work.
Allowed files: canonical queue/status/portfolio/user-direction publication and narrowly coupled control-plane tests.
Forbidden files: src/**, include/**, config/**, firmware/runtime/configurator product tests.
Active behavior constraints: runtime product code changed: NO.
Verification required: agent-framework, navigation, queue/runway, and independent governance review.
Stop conditions: concurrent canonical writer, source authority ambiguity, new material idea requiring Planner, forbidden path.
Return format: base, packet/provenance, runway before/after, dispositions,
authorizations, refresh signal, validation, live publication, and:
Delegation:
- guidance applicable:
- capability discovery:
- native capability available:
- specialists used:
- reviewer used:
- if none, reason:
Tool budget: bounded judgment and control-plane editing.
```

## Hardware Evidence Processor Handoff

```text
Role: hardware_evidence_processor
Objective: validate and record supplied controller observations for candidate ... and artifact SHA-256 ...
Scope: exact work order, protocol, candidate/ref, artifact identity, observations, evidence/status files.
Delegation preflight: inspect the complete runtime capability/tool catalog or
supported discovery before an unavailability claim; initial visible manifest
absence is insufficient and non-exhaustive. Native internal subagents are
distinct from user-owned task/thread/Automation creation. Use a fresh reviewer
for a result-bearing evidence mutation when native capability exists; review
may validate identity/correspondence/schema but never invent physical
observations.
Use capability-aware live Git verification. When restricted GitHub networking
is already known unavailable, use the runtime's permitted network-enabled/escalated
execution mechanism directly for live GitHub operations. Do not deliberately
repeat an expected-to-fail restricted probe. When connectivity is genuinely
unknown, one minimal ordinary read-only probe is acceptable; a DNS/network
failure is inconclusive and requires the permitted network-enabled retry.
Persist `network_capabilities.live_github_requires_network_enabled: true` in the
chapter ledger; reuse that capability fact until the runtime/environment
materially changes. Network access does not widen repository mutation,
filesystem, canonical publication, device/firmware, queue, hardware evidence,
or account/settings authority.

A sandbox DNS/network failure is not authentication evidence or sufficient for
BLOCKED_EXTERNAL. Authentication may be diagnosed only after connectivity is
established and GitHub actually rejects authentication or authorization.
Never automatically run gh auth login/logout, rewrite tokens, delete credentials,
change credential helpers, replace SSH keys, switch accounts, or request re-login;
account-level changes are user-owned unless separately requested. Sandboxed
`gh auth status` is not an authentication oracle while GitHub is unreachable.
Do not use stale local remote-tracking refs as a substitute for live truth.
Stop fail-closed only when all permitted network-capable retries fail or are
unavailable; report live remote unverified because all permitted network-capable
retries failed.
Excluded scope: performing/fabricating tests, runtime source edits, source publication.
Allowed files: evidence record and directly coupled control-plane status.
Forbidden files: src/**, include/**, config/**, product/runtime tests.
Active behavior constraints: evidence branch is not source authority.
Verification required: identity, completeness, drift, framework/evidence checks, independent review.
Stop conditions: identity mismatch, incomplete protocol, source drift, concurrent writer.
Return format: match/mismatch, PASS/FAIL/PARTIAL/INCONCLUSIVE, disposition,
branch/SHA, retest/repair/publication action, and:
Delegation:
- guidance applicable:
- capability discovery:
- native capability available:
- specialists used:
- reviewer used:
- if none, reason:
Tool budget: bounded evidence verification.
```

## Architecture Specialist Handoff

```text
Role: architecture_specialist
Objective: map source-backed boundary for ...
Scope: inspect source/docs/tests/fixtures needed for the question.
Excluded scope: implementation, active publication changes, game semantics.
Allowed files: read relevant repo files.
Forbidden files: edits unless separately assigned.
Active behavior constraints: no candidate.view, active_storage.view, generated
active wrapper, or RAM-backed active publication claim.
Verification required: evidence references.
Stop conditions: undocumented behavior, missing source evidence.
Return format: evidence map, inferred items, unknowns, recommendation.
Tool budget: bounded read-only.
```

## Implementer Handoff

```text
Role: implementer
Objective: implement the bounded docs/checker change ...
Scope: named files only.
Excluded scope: firmware source, runtime-loaded config, device write,
persistence, flashing automation.
Allowed files: ...
Forbidden files: src/**, include/**, lib/**, platformio.ini, protobuf schemas,
device-write paths.
Active behavior constraints: active firmware behavior unchanged.
Verification required: named checkers and py_compile when Python is touched.
Stop conditions: source touched unexpectedly, checker failure, scope creep.
Return format: patch summary, files changed, verification, blockers.
Tool budget: bounded editing.
```

## Validator Reviewer Handoff

```text
Role: validator_reviewer
Objective: review the branch and run required validation.
Scope: inspect diff, run checkers, classify behavior.
Excluded scope: unrelated fixes, gate bypass.
Allowed files: read relevant files; edit only assigned docs/checker fixes.
Forbidden files: forbidden branch paths and destructive Git operations.
Active behavior constraints: active firmware behavior unchanged unless
explicitly classified.
Verification required: repo checkers listed by supervisor.
Stop conditions: firmware source diff, active behavior uncertainty, failed
required checker.
Return format: findings first, commands run, classification, residual risk.
Tool budget: bounded check/review.
```

## Docs Clerk Handoff

```text
Role: docs_status_clerk
Objective: align status/navigation docs with validated state.
Scope: docs/status/navigation files only.
Excluded scope: source, build scripts, protobuf schemas, device write paths.
Allowed files: docs/AGENT_CONTEXT.md, docs/CURRENT_STATE.md, docs/ROADMAP.md,
docs/runtime_config/README.md, docs/archive/README.md when assigned.
Forbidden files: src/**, include/**, lib/**, platformio.ini.
Active behavior constraints: no behavior change or new behavior claim.
Verification required: docs navigation checker.
Stop conditions: wording would claim Nunchuk tested, root cause proven, or
runtime-loaded config implemented.
Return format: status deltas, docs touched, consistency checks.
Tool budget: bounded docs-only.
```

## Judge Watchdog Handoff

```text
Role: judge_watchdog
Objective: decide cycle verdict.
Scope: read supervisor summary, diff stat, validation output, and gate notes.
Excluded scope: edits and gate overrides.
Allowed files: read-only.
Forbidden files: all edits.
Active behavior constraints: classify any active behavior uncertainty as
NEEDS_HARDWARE or UNSAFE.
Verification required: none; evaluate provided evidence.
Stop conditions: loop criteria, forbidden path, missing concrete delta.
Return format: verdict, reasons, required next action, gate notes.
Tool budget: small read-only.
```

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
