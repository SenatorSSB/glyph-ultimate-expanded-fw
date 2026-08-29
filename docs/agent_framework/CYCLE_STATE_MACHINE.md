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
   - Read `docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md`.
   - Read `docs/project/ACTIVE_AGENT_QUEUE.md`.

2. Preflight repo
   - Confirm base branch, target branch, and working tree.
   - Confirm required cleanup/current docs exist.
   - Stop on dirty tree unless the task explicitly authorizes working with it.

3. Recover and select authorized work
   - Recover at most one legitimate contracted unfinished item first.
   - Select the highest-priority complete `READY` work order.
   - If none, mechanically activate at most one valid `PREAUTHORIZED` item.
   - Never reinterpret activation conditions, promote Planner candidates, or
     self-reseed.
   - Complete at most one new work order.

4. Perform delegation preflight
   - Determine whether repository delegation guidance applies.
   - Inspect the complete runtime capability/tool catalog or use the supported
     discovery mechanism; initial manifest absence is insufficient evidence of
     native unavailability.
   - Distinguish native internal children from user-owned tasks, threads, and
     Automations; record capability, separable tasks, delegation, reviewer, and
     any exact no-use reason.

5. Spawn bounded subagents
   - Use explicit handoffs.
   - Keep tool budgets bounded.
   - Require compact returns with evidence and unknowns.

6. Validate
   - Run required checkers.
   - Run build only when source/build-affecting files require it.
   - Do not request hardware for docs/checker-only branches with active
     behavior unchanged.

7. Classify behavior
   - `DOCS_CHECKER_ONLY`
   - `INACTIVE_GENERATOR_OR_FIXTURE`
   - `FIRMWARE_SOURCE_NON_ACTIVE`
   - `FIRMWARE_SOURCE_ACTIVE_BEHAVIOR`
   - `FORBIDDEN_OR_UNSAFE`

8. Publish candidate, merge, or stop
   - Merge recommendation is allowed only after validation and gate review.
   - Active behavior change requires build proof and hardware PASS before
     merge.
   - H2/H3 stops after exact candidate/artifact publication with
     `HARDWARE_TEST_REQUIRED`; record full Git SHA and artifact SHA-256.
   - A later `HARDWARE_VALIDATED` recovery cycle verifies the pinned candidate
     ref, preserved artifact hash/locator, exact PASS record, zero evidence
     gaps, and fresh-configurator drift before merging only that candidate
     tree and transitioning the queue item to `DONE`.
   - `HARDWARE_FAILED` never publishes candidate source. PARTIAL/INCONCLUSIVE
     remains `LOCAL_ACCEPTANCE_PENDING` with exact gaps.
   - Forbidden or unsafe paths stop.

9. Update status docs
   - Keep `docs/AGENT_CONTEXT.md`, `docs/CURRENT_STATE.md`,
     `docs/ROADMAP.md`, runtime-config docs, and archive indexes aligned when
     facts change.
   - Do not convert status docs into run logs.

10. Recompute runway and liveness
   - Report Ready, recorded/activatable/invalidated Preauthorized,
     hardware-pending, and effective runway separately.
   - Return `PLANNING_REQUIRED` for absent/stale/consumed candidate supply.
   - Return `CURATION_REQUIRED` for substantive authorization,
     reauthorization, or interpretation.
   - At zero runway, invalidated Preauthorization or failed hardware takes
     precedence over absent/stale Planner supply and yields primary
     `CURATION_REQUIRED`; hardware failure also carries supporting
     `REPAIR_REQUIRED`.
   - Treat candidate-local `HARDWARE_TEST_REQUIRED` and `REPAIR_REQUIRED` as
     supporting signals, not the exclusive portfolio liveness state.

11. Return compact final report
    - Delegation guidance, capability discovery, native availability,
      specialists, reviewer, and exact no-use reason.
    - Summary.
    - Files changed.
    - Verification.
    - Behavior classification.
    - Build and hardware requirements.
    - Backend behavior claims.
    - Stop conditions and follow-ups.
