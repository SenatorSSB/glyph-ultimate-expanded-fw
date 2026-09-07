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


## Reviewed completion — 2026-09-07

The final four-file repair `9d80cc5fe6324ba301ab1e05b06e4d4532360055`
from rebound base `0b851b969560c3bcb13339afc770d5ff5ec8713a` received a
fresh independent PASS and entered live configurator through
`0381a0150c6f2d590072bedb2c4e61ad810e80e3` before separate DONE publication.
The full current aggregate passed 30/30, with canonical fingerprint MATCH and
MATCH after every isolated checker. All focused, adversarial, checker-context,
census, manifest, health, framework, sequence, navigation, surface, syntax and
diff gates passed. Twenty repetitions of the original stalled-setup timeout
reproducer passed. The operational budget is 300 seconds, with bounded
TERM-to-KILL grace and reaping; this is not an exact 302-second wall guarantee.

The original `ab8e68ede84468c89365b7f5144889c5728e0583` and
`34f430886fb808ce70df81e21d926aef05ed7169` were retained locally on
`codex/gp-val-011-recovery-evidence`; their permitted implementation delta was
reused and repaired, while their failed commits were superseded and never
entered canonical ancestry. Intermediate failed candidate `95efad7bb49b3eb0e9b02a004fa05144cde2167b`
is also superseded local evidence, not unfinished authorized work. No failed
experimental commit was published as canonical implementation. No firmware,
runtime, workflow, build input, device, artifact or hardware behavior changed.


## Original ignored-directory defect — independent reopening 2026-09-07

Final clean main-checkout aggregate at live 31bdbbc83f3129ecb9cbf5bc4ad20e073bdd60a4 failed before checker execution: canonical_fingerprint rejected ignored nested Git directory .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/. Independent source Curator classifies this as an original ignored-path fingerprint implementation bug, not a new checker Git-topology requirement. GP-VAL-011 is reopened READY for the exact bounded directory traversal repair. Previous reviewed implementation/completion evidence remains historical; GP-PERSIST-001 stays DONE. Prior global wait is revoked and Planner packet STALE pending completed repair and fresh material review.

Current narrow repair: canonical_fingerprint must handle directory entries emitted by git ls-files --others --ignored --exclude-standard for caller-local ignored nested Git repositories. Recursively enumerate only physical descendants of such IGNORED directory entries in deterministic sorted order and fingerprint each relative path, file type/mode, directory membership (including empty directories), regular-file bytes and symlink target text. Treat nested .git content as opaque caller-local filesystem bytes; never use its refs/objects/config as validation inputs, execute Git there, copy it to the clone, or add it to required-ref/object catalogs. Use lstat and do not follow symlink directories or external targets. Preserve unambiguous length-framed hashing, existing whole-command budget checks during enumeration and byte reads, final proof rules, and fail-closed handling of unsupported special entries, unreadable state, detectable traversal races or unavailable proof. No timestamps are added as mutation semantics. This is support for the already permitted complete ignored-path set, not dirty-state support or new Git topology. Existing original snapshot, exact ref/object catalog, environment, checker commands/applicability, independent object storage and timeouts remain unchanged. The three implementation consequences are runner, aggregate adversarial tests and deterministic census; README may change only to explain this existing ignored-state contract.

This is an original implementation defect, not a third substantive topology expansion. No caller ignored state was deleted, moved, copied or modified to bypass failure. The failed preflight truthfully returned SETUP_FAILURE with canonical proof UNAVAILABLE and no checker results. Prior temporary-clone PASS remains truthful historical evidence but cannot establish present work-order completion.

### Historical prior DONE correspondence

The prior reviewed feature/integration/completion remains preserved; this record is not current DONE authority. Separate completion was published at `3171837fcfe8fa8b9f6ab1d1a8891478c98c76a3`.

```json
{
  "schema_name": "glyph_done_completion_evidence",
  "schema_version": 1,
  "mode": "DIRECT_ANCESTRY",
  "implementation_base_sha": "0b851b969560c3bcb13339afc770d5ff5ec8713a",
  "reviewed_implementation_sha": "9d80cc5fe6324ba301ab1e05b06e4d4532360055",
  "prior_canonical_integration_sha": "0381a0150c6f2d590072bedb2c4e61ad810e80e3",
  "reviewed_changed_paths": [
    "docs/runtime_config/README.md",
    "docs/runtime_config/fixtures/glyph_checker_census.json",
    "tools/check_glyph_runtime_config_validation_aggregate.py",
    "tools/run_glyph_runtime_config_validation.py"
  ],
  "independent_review_provenance": "Fresh independent reviewer PASS on exact 9d80cc5: scope, complete topology catalog, dirty index flags, exact branch identity, child ownership and bounded cleanup verified; no material findings.",
  "validation_provenance": "Exact 9d80cc5: full aggregate 30/30 PASS with canonical and every isolated fingerprint MATCH; 35 adversarial groups; 20/20 stalled-setup timeout repetitions; context18, census196, manifest34, health, framework, sequence, navigation, surface, compile and diff PASS. Integration 0381a01 live-verified before this separate completion record."
}
```
