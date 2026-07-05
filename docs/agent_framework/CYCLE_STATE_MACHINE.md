# Cycle State Machine

Status label: CURRENT.

A long run is many bounded cycles, not one unbounded monolithic conversation.
This document does not implement or define the runner prompt. Runner
implementation is deferred.

## States

1. Load canonical docs
   - Read `docs/AGENT_CONTEXT.md`.
   - Read `docs/CURRENT_STATE.md`.
   - Read `docs/ROADMAP.md`.
   - Read `docs/WORKFLOW.md`.
   - Read `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`.
   - Read `docs/agent_framework/README.md`.

2. Preflight repo
   - Confirm base branch, target branch, and working tree.
   - Confirm required cleanup/current docs exist.
   - Stop on dirty tree unless the task explicitly authorizes working with it.

3. Select ready batch
   - Choose a small objective with clear allowed files.
   - Assign initial branch classification.
   - Name verification and stop rules.

4. Spawn bounded subagents
   - Use explicit handoffs.
   - Keep tool budgets bounded.
   - Require compact returns with evidence and unknowns.

5. Validate
   - Run required checkers.
   - Run build only when source/build-affecting files require it.
   - Do not request hardware for docs/checker-only branches with active
     behavior unchanged.

6. Classify behavior
   - `DOCS_CHECKER_ONLY`
   - `INACTIVE_GENERATOR_OR_FIXTURE`
   - `FIRMWARE_SOURCE_NON_ACTIVE`
   - `FIRMWARE_SOURCE_ACTIVE_BEHAVIOR`
   - `FORBIDDEN_OR_UNSAFE`

7. Merge or stop
   - Merge recommendation is allowed only after validation and gate review.
   - Active behavior change requires build proof and hardware PASS before
     merge.
   - Forbidden or unsafe paths stop.

8. Update status docs
   - Keep `docs/AGENT_CONTEXT.md`, `docs/CURRENT_STATE.md`,
     `docs/ROADMAP.md`, runtime-config docs, and archive indexes aligned when
     facts change.
   - Do not convert status docs into run logs.

9. Reseed next queue
   - Name the next concrete ready item.
   - Preserve blocked items with explicit blockers.
   - Avoid process-only churn.

10. Return compact final report
    - Summary.
    - Files changed.
    - Verification.
    - Behavior classification.
    - Build and hardware requirements.
    - Backend behavior claims.
    - Stop conditions and follow-ups.
