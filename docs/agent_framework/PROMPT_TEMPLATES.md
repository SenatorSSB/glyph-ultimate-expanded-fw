# Prompt Templates

Status label: CURRENT.

Runner prompt and runner implementation are intentionally deferred. These are
operator-facing templates for bounded supervisor cycles and explicit subagent
handoffs. They do not authorize browser/device write, WebSerial/device write,
runtime-loaded profiles, daemon work, or scheduled automation.

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
- preserved facts
```

## Planner Handoff

```text
Role: planner
Objective: identify a ready bounded batch for ...
Scope: read current docs, roadmap, workflow, and relevant checkers.
Excluded scope: edits, semantic decisions, runtime-loaded config approval.
Allowed files: docs/**, tools/check_*.py for inspection.
Forbidden files: src/**, include/**, lib/**, platformio.ini.
Active behavior constraints: active RuntimeConfigView selection remains
unchanged.
Verification required: none; propose verification.
Stop conditions: source authority ambiguity, hardware gate, forbidden path.
Return format: ready batch, dependencies, classification, stop rules.
Tool budget: bounded read-only.
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
