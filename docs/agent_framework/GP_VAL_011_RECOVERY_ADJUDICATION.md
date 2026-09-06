# GP-VAL-011 independent recovery contract adjudication — 2026-09-06

Disposition: Path A — narrowly REAUTHORIZED / READY after publishing the rebound contract. This is contract authorization, not implementation PASS or merge approval.

Live canonical independently verified: `2a80462ba2801192154e42ee4bebb9b1b43ca699`. Ordinary GitHub DNS failed; permitted read-only network retry returned the same live canonical SHA. Local inspected `configurator` was clean at `34f430886fb808ce70df81e21d926aef05ed7169`, descending through `ab8e68ede84468c89365b7f5144889c5728e0583` from canonical. Source/control-plane inspection, no build/device/hardware action.

## A — checker_context

Contract omission with an implementation environment mismatch. `tools/glyph_checker_context.py:collect_checker_context` resolves inherited expected merge-base even with an explicit base argument. `tools/check_glyph_checker_context.py` creates unrelated synthetic repositories and intentionally requires absent comparison variables for its detached missing-base case. Neither helper nor test semantics should change. Omit only `GLYPH_CHECKER_BASE` and `GLYPH_CHECKER_EXPECTED_MERGE_BASE` for the exact existing checker_context self-test command. Apply the same exact exception to validation_aggregate_adversarial, whose synthetic Git repositories also cannot resolve outer immutable source SHAs. All other commands retain immutable outer context. No additional ambient variables are needed. `PYTHONHASHSEED=0` and `PYTHONNOUSERSITE=1` are explicit constructed deterministic Python controls within the already authorized deterministic-Python category; they are not inherited identity claims.

## B — census_freshness

The test expectation is valid: canonical aggregate reports census freshness after evaluating its load-bearing gate. The observed KeyError is downstream of outer GLYPH base injection causing synthetic immutable_source_context setup failure before checker results. Repair that environment defect and preserve truthful census_freshness in structured failure output whenever it has actually been evaluated. Never weaken the test or fabricate a PASS. Canonical setup failures formerly printed text; preserving an evaluated census object in the new structured setup report is an authorized runner reporting correction.

## C — required historical candidate ref

Contract omission, source-determined narrow resolution. `tools/check_glyph_current_x1_regression_subset.py:evidence_correspondence` executes git rev-parse on fixture candidate_branch and compares exact candidate SHA. The fixture binds local branch `runtime-config-x1-offset41-hardware-candidate` to `74ae24364b84520d4e0e39240beb9867653cc7b9`; the caller local ref currently matches, and candidate plus evidence objects are locally present. Require the caller exact local ref identity before recreation; recreate only `refs/heads/runtime-config-x1-offset41-hardware-candidate` at that immutable SHA inside the independent clone. Do not rewrite the checker to omit its ref check, copy arbitrary refs, trust remote branch state, or fetch. The checker independently binds evidence commit `6b0061489cb67d345f212f75268455c181ba271f`, evidence blob SHA-256, and candidate as parent of integration `1597c01b416b6aa697d73efc7d2c2b3695dc3e5c`; none changes. Missing/mismatched caller ref or required local object is fail-closed, not automatic repair. This exact ref requirement applies only when selected entry ID is current_x1_regression_subset and its command is unchanged [python3, tools/check_glyph_current_x1_regression_subset.py]. Category runs and synthetic tests not selecting that exact checker do not require its production fixture/ref; no broad classification-based bypass is authorized.

## Other defects and scope

Detached symbolic-ref return code 1 handling, honoring explicit expected merge-base instead of replacing it, setup clone process-group termination, whole-command deadline coverage, and fingerprints on every exit are implementation correctness defects inside the original objective. They authorize bounded repairs in the same two Python files and tests, not new architecture or checker semantics. Current clone retaining unrelated tags/refs must also be corrected to the closed ref set. Preserve origin comparison ref identity separately from an explicit base override.

Failed local commits are useful starting evidence and must not be merged as reviewed work. Their `SUBAGENT_CONTRACTS.md` delegation log is required by repository process but outside the work-order implementation file list; preserve/reconcile it in separate control-plane recovery publication rather than silently expanding implementation scope. No active source, workflow, manifest entry/schema/classification/dependency, helper, current-X1 checker, or hardware evidence edit is authorized.

## Required publication sequence

Publish this narrow contract from clean live canonical first. Implement and review on its descendant, reusing permitted local implementation content. Validate the full authorized safety contract, not merely the three reported failures; use a fresh postimplementation reviewer distinct from this Curator and implementation author. Full PASS precedes feature/integration publication, live ancestry proof precedes separate DONE status publication. If a new substantive scope/semantics requirement appears, return to curation instead of expanding scope.

## Deadline proof clarification

The 300-second operational deadline cannot promise a complete fingerprint after exhaustion or stalled filesystem access. Attempt final proof boundedly on every exit after initial capture; if proof is unavailable or unfinished at deadline, explicitly report final-proof-unavailable and FAIL. Never claim unchanged state or PASS without complete matching proof. The only deadline overrun allowance is the separately fixed two-second TERM-to-KILL process cleanup grace; no unbounded proof or cleanup is authorized. This is truthful implementation of the existing fail-closed requirement, not weakened mutation detection.

## Local immutable object transfer clarification

The original contract requires every needed immutable object to be locally available and exact comparison semantics, but a normal clone may omit objects held only by caller remote-tracking refs. Supplying those exact objects through a local independent pack is a mechanical implementation of the already selected independent snapshot architecture, not a new checker or topology authority. The permitted transfer roots are source HEAD, selected comparison base, supplied expected merge-base, actual merge-base, original origin/configurator identity, and the conditionally required X1 candidate/evidence/integration IDs. Deduplicate and resolve them before transfer. Use local `git pack-objects --revs --stdout` with only those full IDs and destination `git index-pack --stdin`; no `--all`, reflogs, arbitrary refs, thin/shared packs, alternates, hardlinks, fetch, or network/lazy retrieval. Transfer includes necessary reachable object closure, not unrelated refs. Require local completeness and verify imported identities; missing local objects or errors fail closed. Both processes remain setup-budget/process-group bounded and caller fingerprint remains unchanged.


# GP-VAL-011 second independent recovery curation

Disposition: source-determined Path A, pending separately published contract. Candidate 95efad7 remains failed, nonauthoritative evidence. Full aggregate reported 27/30 PASS and outer canonical MATCH; this is not merge authority. No final portfolio wait is accepted.

## Scope of independent source audit

Reviewed all 30 selected current manifest command vectors, 42 manifest/direct-import Python surfaces, and a conservative 85-file surface including named subprocess/historical references. Inspected actual main/call paths to exclude dormant branch functions and historical checkers from current topology requirements. This is a bounded current source audit, not a claim of general dynamic dependency closure.

## Closed ref set

Retain prior source HEAD branch/detached and original origin/configurator comparison identity plus exact conditional X1 candidate ref. Add only caller refs/heads/configurator at its own pinned commit when exact generated_baseline_artifact command is selected. Its main calls validate_branch unconditionally and diffs configurator...HEAD; origin/base substitution would change scope semantics. Missing source local ref fails closed. Supervisor temporary source clone was itself missing this ref at inspection and needs explicit legitimate source preparation before validation; the runner may not silently create it from origin. Preserve detached failure of this unchanged checker.

## Closed additional object roots

- build_input_resolution_observations: 8c04262c66613d46b933b1b739c01c575cb0c580 and ffc007552abc848051841362b0b0ac4c1a7d087b.
- nuker_source_lineage: a747dd54b02b207483142331d8b5be1113fc951e and d5050847d3f850951b3f47865dc8a91aedea0834. These are current HEAD ancestors; no new ref or weakening of rev-list --all reachability is allowed.
- agent_framework, from committed regular HEAD queue blob: non-ABSENT planner_packet.base_configurator_sha/planning_commit/curation_commit; completion_correspondence.migration_base_configurator_sha; nonlegacy DONE items' done_evidence.implementation_base_sha/reviewed_implementation_sha/prior_canonical_integration_sha; and git-json hardware_evidence_record SHA only for HARDWARE_VALIDATED, HARDWARE_FAILED, or result-bearing LOCAL_ACCEPTANCE_PENDING states actually read by current evidence validation. repo-json uses HEAD. No arbitrary recursive metadata or SHA scanning.
- Existing exact X1 candidate/evidence/integration roots and runner HEAD/base/expected/merge-base/origin roots remain.

Select each row only for its exact current checker ID and unchanged command. Verify field types, duplicate-free committed JSON, full commit IDs, local object completeness; transfer exact deduplicated root closure using the already authorized local pack mechanism into independent objects. Do not infer authority, add arbitrary refs, load checkers in caller, read ignored state, or fetch. Malformed current metadata fails, and the unchanged checker still judges its semantics in the clone. Runtime-generated temporary Git repositories belong to self-tests and add no caller source dependencies. Fixed Git-blob identities need no separate roots because their owning commit closure supplies them.

## Nested timeout failure

The report records PermissionError during snapshot setup and final proof unavailable after the 0.5-second injected budget. Source evidence does not identify the exact failing syscall. Treat this as an execution/test failure needing operation-level diagnosis within the already authorized runner/adversarial files. Do not weaken the fixture to accept SETUP_FAILURE as evidence of a timeout or suppress unexpected signal errors. No new environment/product architecture is authorized by it.

## Authorization and stopping

This correction is deterministic from current source, not an owner product decision. Publish the explicit rebound before repair. Preserve exact failed candidate evidence and run the complete focused/aggregate/current-checker corpus again with fresh independent implementation review. This is the final substantive topology expansion permitted in this recovery; any further required checker semantic/topology expansion stops as non-executable REPAIR_REQUIRED while independent safe phases continue. No firmware, build, artifact, device, physical result or gameplay change is authorized.

Supervisor preparation: the temporary integration repository now has local
`configurator` explicitly bound to freshly live-verified canonical
`1a4b9311c8f7ae6d7cbf0a8680cd976499112f03`. This is source-repository
preparation outside validation, not inferred clone state. Subsequent repeated
timeout diagnostics reproduced the alarm interrupting TERM cleanup. Repair
must preserve the fixed bounded cleanup grace and demonstrate both deadline
and process-group termination; no failed result has been accepted.
