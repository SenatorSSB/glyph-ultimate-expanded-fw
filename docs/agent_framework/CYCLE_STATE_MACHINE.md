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
   - Use current Revision 3 GLYPH-UD-027 and VALIDATION_AND_GATES.md: Tier 1
     always blocks, Tier 2 blocks when directly affected, Tier 3 is honest
     framework debt unless a concrete Tier-1/Tier-2 contradiction exists.
   - Run focused regressions, all directly affected actual consumers, relevant
     historical correspondence/negatives, review and frozen mutation/isolation.
     Never relabel FAIL/TIMEOUT/incomplete as PASS or require recursive global
     topology meta-proof. Future GP-VAL requires UNPROVEN_SAFETY_FACT and the
     WORK_ORDER_TEMPLATE.md successor limits, not scheduling-cost churn.
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
   - Preserve R -> E -> I: source-free E requires no I catalog; later accepted
     I still requires immutable E, exact tested source/catalog and review.
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
     reauthorization, or interpretation only while the canonical
     `curation_obligation.pending` flag is true.
   - A newly recorded invalidated Preauthorization or failed-hardware event
     opens that obligation with exact trigger and provenance. At zero runway
     the pending obligation takes precedence over absent/stale Planner supply
     and yields primary `CURATION_REQUIRED`; hardware failure also carries
     supporting `REPAIR_REQUIRED`.
   - After the Curator records an authenticated resolution, preserve the
     invalidated/failed item without deriving another Curator cycle from the
     same evidence. Zero runway then routes to `PLANNING_REQUIRED` unless an
     independently accepted global wait applies.
   - Treat candidate-local `HARDWARE_TEST_REQUIRED` and `REPAIR_REQUIRED` as
     supporting signals, not the exclusive portfolio liveness state.

11. Return compact final report
    - Follow GLYPH-UD-028 transport-only known-Glyph ACK/WORKER_RESULT delivery.
      CROSS_THREAD_MESSAGE_REJECTED falls back to durable canonical/pushed
      result and readback, no repeated retry or duplicate worker. Successful
      callbacks chain immediately; ten-minute polling is idle fallback.
      Canonical write/publication authority remains single-writer.
    - Delegation guidance, capability discovery, native availability,
      specialists, reviewer, and exact no-use reason.
    - Summary.
    - Files changed.
    - Verification.
    - Behavior classification.
    - Build and hardware requirements.
    - Backend behavior claims.
    - Stop conditions and follow-ups.
