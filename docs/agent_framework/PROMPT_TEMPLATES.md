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

Live Git verification: attempt it normally; a restricted-sandbox GitHub/DNS/network failure is inconclusive, so retry the same minimal read-only check through the permitted network-enabled/escalated mechanism. It is not authentication evidence or sufficient for BLOCKED_EXTERNAL. Authentication may be diagnosed only after connectivity is established and GitHub rejects authentication. Never automatically mutate credentials or request re-login; account-level changes are user-owned unless separately requested. Do not substitute stale tracking refs. Stop fail-closed only after all permitted network-capable retries fail or are unavailable.

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
- ...

Final report:
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
Live Git verification: attempt it normally; a restricted-sandbox GitHub/DNS/network failure is inconclusive, so retry the same minimal read-only check through the permitted network-enabled/escalated mechanism. It is not authentication evidence or sufficient for BLOCKED_EXTERNAL. Authentication may be diagnosed only after connectivity is established and GitHub rejects authentication. Never automatically mutate credentials or request re-login; account-level changes are user-owned unless separately requested. Do not substitute stale tracking refs. Stop fail-closed only after all permitted network-capable retries fail or are unavailable.
Excluded scope: product/queue edits, Ready or Preauthorized promotion, semantic decisions, runtime-loaded config approval.
Allowed files: repository files for inspection; material output only on planning/portfolio-*.
Forbidden files: all product/runtime files for mutation; source, include, lib,
and platform files may be inspected read-only.
Active behavior constraints: active RuntimeConfigView selection remains
unchanged.
Verification required: none; propose verification.
Stop conditions: source authority ambiguity, hardware gate, forbidden path.
Return format: base SHA, freshness, broad-audit scope, candidates with estimates,
rejected alternatives, gates, and global-wait/resume-event assessment.
Tool budget: bounded read-only.
```

## Curator Handoff

```text
Role: curator
Objective: independently authorize complete Ready or narrowly Preauthorized work from ...
Scope: current live configurator, candidate packet, source/tests, queue, user direction, evidence, and control-plane docs/tests.
Live Git verification: attempt it normally; a restricted-sandbox GitHub/DNS/network failure is inconclusive, so retry the same minimal read-only check through the permitted network-enabled/escalated mechanism. It is not authentication evidence or sufficient for BLOCKED_EXTERNAL. Authentication may be diagnosed only after connectivity is established and GitHub rejects authentication. Never automatically mutate credentials or request re-login; account-level changes are user-owned unless separately requested. Do not substitute stale tracking refs. Stop fail-closed only after all permitted network-capable retries fail or are unavailable.
Excluded scope: firmware/configurator product code, runtime/product tests, implementation of newly authorized work.
Allowed files: canonical queue/status/portfolio/user-direction publication and narrowly coupled control-plane tests.
Forbidden files: src/**, include/**, config/**, firmware/runtime/configurator product tests.
Active behavior constraints: runtime product code changed: NO.
Verification required: agent-framework, navigation, queue/runway, and independent governance review.
Stop conditions: concurrent canonical writer, source authority ambiguity, new material idea requiring Planner, forbidden path.
Return format: base, packet/provenance, runway before/after, dispositions,
authorizations, refresh signal, validation, live publication.
Tool budget: bounded judgment and control-plane editing.
```

## Hardware Evidence Processor Handoff

```text
Role: hardware_evidence_processor
Objective: validate and record supplied controller observations for candidate ... and artifact SHA-256 ...
Scope: exact work order, protocol, candidate/ref, artifact identity, observations, evidence/status files.
Live Git verification: attempt it normally; a restricted-sandbox GitHub/DNS/network failure is inconclusive, so retry the same minimal read-only check through the permitted network-enabled/escalated mechanism. It is not authentication evidence or sufficient for BLOCKED_EXTERNAL. Authentication may be diagnosed only after connectivity is established and GitHub rejects authentication. Never automatically mutate credentials or request re-login; account-level changes are user-owned unless separately requested. Do not substitute stale tracking refs. Stop fail-closed only after all permitted network-capable retries fail or are unavailable.
Excluded scope: performing/fabricating tests, runtime source edits, source publication.
Allowed files: evidence record and directly coupled control-plane status.
Forbidden files: src/**, include/**, config/**, product/runtime tests.
Active behavior constraints: evidence branch is not source authority.
Verification required: identity, completeness, drift, framework/evidence checks, independent review.
Stop conditions: identity mismatch, incomplete protocol, source drift, concurrent writer.
Return format: match/mismatch, PASS/FAIL/PARTIAL/INCONCLUSIVE, disposition,
branch/SHA, retest/repair/publication action.
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
