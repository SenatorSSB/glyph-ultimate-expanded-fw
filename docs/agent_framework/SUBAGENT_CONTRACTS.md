# Subagent Contracts

Status label: CURRENT.

Subagents are bounded specialists. Each handoff must name role, scope,
excluded scope, allowed files, forbidden files, active behavior constraints,
verification, stop conditions, return format, and tool budget. Default
Codex/OpenAI model/effort recommendations live in `MODEL_ROUTING.md`.

Prompt labels such as `read-only`, `allowed_files`, and `forbidden_files` are
coordination contracts, not mechanically enforced filesystem isolation. Root
must inspect shared-worktree status/diffs and attribute unexpected mutations
before integration. When hard read-only enforcement is required, use an
actually isolated/read-only execution environment rather than relying on the
prompt label.

## Native Delegation Discovery And Accountability

Native internal subagent delegation means scoped child agents, sidecars, or
reviewers created by the current root run. They return results to that root;
the root retains integrated mutation, authoritative validation, Git,
publication, status, and final authority.

User-owned task, thread, conversation, or Automation creation starts a separate
user-visible job. It is distinct from and not equivalent to native internal
subagent delegation. A root must not present user-owned job creation as the
only delegation mechanism when a native internal facility exists, and must not
replace a required independent reviewer with a suggestion to create another
user task or thread.

Before substantive implementation or research, when repository guidance or
the selected role calls for subagent use, the root must perform this delegation
preflight:

1. Determine whether repository delegation guidance applies.
2. Inspect the complete available runtime capability/tool catalog, or use the
   runtime's supported capability-discovery mechanism, before declaring native
   delegation unavailable. Absence from the initial visible tool manifest or
   tool list is insufficient evidence of unavailability and the initial
   manifest must not be treated as exhaustive.
3. Determine whether a native internal subagent facility is available without
   hardcoding one runtime-specific tool name as the only valid backend.
4. Identify useful separable specialist tasks and required independent review.
5. Record every delegated role and objective. If no native subagent is used,
   record the exact reason.

Acceptable no-subagent reasons include a true no-op cycle; a trivial mechanical
task with no useful separable investigation, provided any independently
required review is still satisfied; complete capability discovery confirming
that no native facility exists; a runtime failure after attempted discovery or
child creation; or a concurrency/safety stop before substantive work. "No
tools were visible initially" is never an acceptable reason.

For a normal Implementation cycle that mutates repository state, a fresh
independent post-implementation reviewer is required when native capability is
available. The root may not self-review as a substitute. The reviewer receives
the exact work-order objective, scope, and exclusions; the exact diff or
changed-area description; relevant evidence and contracts; validation results;
and an instruction to look for material correctness, safety, authority, scope,
publication, and regression defects. The root repairs material findings and
obtains re-review of repaired areas.

Use at least one additional bounded specialist when a materially separable
investigation exists. Examples include source/upstream history, source
authority, schema/contract, build/test gaps, provenance/evidence, firmware
safety, and recovery/lineage. Do not create specialist work merely to satisfy a
quota; reviewer-only is acceptable for a small mechanical implementation with
no meaningful separable research.

For active firmware or H2/H3 work, normally use at least one bounded
source-authority or firmware-safety specialist and a separate fresh independent
reviewer. Use additional build/evidence help when warranted. This adds no new
user-approval gate: a complete `READY` H2/H3 contract remains executable to its
existing exact-snapshot hardware stop.

Planner should use parallel read-heavy specialists when a broad audit can be
cleanly partitioned, while avoiding arbitrary parallelism for a tiny candidate
surface. Planner and its helpers remain non-authoritative. Curator may use
bounded verification specialists for separable source, evidence, validation,
or hardware-risk checks, but Curator retains the final substantive
authorization judgment. Hardware Evidence Processor uses a fresh reviewer for
a result-bearing evidence mutation when native capability exists; that reviewer
may validate identity, correspondence, and schema but must not invent physical
observations.

Every affected root task prompt must require this final-report evidence:

```text
Delegation:
- guidance applicable:
- capability discovery:
- native capability available:
- specialists used:
- reviewer used:
- if none, reason:
```

This is per-run audit evidence, not canonical queue telemetry.

## Implementation Supervisor cycle — GP-VAL-006 (2026-08-31)

- guidance applicable: yes; GP-VAL-006 is a complete H1 READY work order and
  repository mutation requires bounded delegation plus fresh independent review.
- capability discovery: complete runtime tool catalog inspected; native
  internal subagent facility confirmed available.
- native capability available: yes.
- specialist: bounded read-only source/contract specialist; inspect the
  candidate writer/checker seams and required isolated-repository invariants;
  no edits, commits, pushes, or canonical-repository mutation.
- reviewer: fresh independent validator reviewer after implementation; inspect
  the exact diff and run the focused, manifest, aggregate, census, health,
  framework, navigation, agent-surface, syntax, and diff gates.
- allowed specialist files: GP-VAL-006 candidate writer/checker, fixture,
  runtime-config manifest/health/census, and directly relevant contracts.
- forbidden specialist actions: edits, commits, pushes, builds, dependency or
  network resolution, device/runtime claims, or canonical writes.
- stop conditions: canonical subprocess/write context, branch/target refusal
  bypass, incomplete repository isolation, scope drift, or active behavior.
- return format: findings first; exact contract matches/gaps; recommended
  bounded next action.

## Implementation Supervisor cycle — GP-CONFIG-012 (2026-09-29)

- guidance applicable: yes; the complete READY order requires exact decoder,
  source, and caller characterization, and repository mutation requires a
  bounded specialist plus fresh independent post-implementation review.
- capability discovery: inspected the complete runtime tool catalog (202
  capabilities); native internal child agents are available through the
  collaboration runtime.
- native capability available: yes.
- specialist used: `gp_config012_source`, read-only verification of the exact
  authorized source selector, four callers, GP-PROV-014 decoder closure, and
  invalidation conditions against live configurator `6b6424dc9f915530b4a3386cd3864671a236d4e6`.
- reviewer used: fresh independent post-implementation review is required
  before publication; review the exact GP-CONFIG-012 diff, source/closure
  evidence, focused and affected gates, and the work-order exclusions.
- separable investigation: the source/authority and accepted dependency
  closure were independently checked; exact GP-PROV-014 bytes were rehashed
  from the preserved GP-PROV-014 worktree after the root checkout's ignored
  cache was found to be the rejected 0.4.9.1 alternate.
- findings: current production source, selectors, and four callers remain
  aligned with the authorized source snapshot. All recorded accepted 0.4.9.2
  package, schema, generated C/header, decode/common closure, and license
  hashes match; upstream tag `0.4.9.2` resolves to pinned commit
  `160d4f09e5fabb2b66aa2dea32d4f38ace2c4b3f`. The local ignored cache is not
  an authorized test input.
- allowed specialist scope: source, schema, selector, dependency-provenance,
  and caller inspection only; no edits, tests, dependency installation,
  builds, hardware, or queue/status changes.
- stop conditions: any source/decoder drift, unavailable exact bytes, missing
  caller coverage, ambiguous sanitizer attribution, policy dependence, or
  prohibited behavior change.
- return format: exact evidence, source identities, invalidation result, and
  bounded next action.

## Planner

Current Revision 3 GLYPH-UD-027 and VALIDATION_AND_GATES.md supersede conflicting
progression only. Planner/Curator resolve substantive owner/product/source/
semantic/material-architecture questions and hardware-FAIL adjudication, not
mechanical identity/path/timeout/local-correction churn. Before future GP-VAL
supply require UNPROVEN_SAFETY_FACT and WORK_ORDER_TEMPLATE.md successor limits;
otherwise preserve framework debt. Do not create supply to meet a quota.
All roles use GLYPH-UD-028 transport only: known exact-campaign targets, bounded
role/work-order authority, single canonical writer and durable rejected-send
readback. A header confers no action permission. Tier 1 always blocks, Tier 2
blocks when affected, Tier 3 does not block absent concrete contradiction.

- Objective: produce broad, non-authoritative current-`configurator` candidate
  supply and assess packet freshness/consumption.
- Allowed actions: read source/docs/checkers/tests/fixtures/evidence, identify
  bottlenecks and dependencies, create a live-verified `planning/portfolio-*`
  packet when material.
- Forbidden actions: edit product code or canonical queue, mark Ready or
  Preauthorized, decide game semantics, fabricate user direction, infer global
  evidence scarcity from candidate-local gates, approve runtime-loaded config,
  or merge planning output to `configurator`.
- Required return format: base SHA, packet freshness, broad-audit scope,
  candidates with non-authoritative readiness estimates, rejected
  alternatives, exact gates, and whether `GLOBAL_EVIDENCE_WAIT_SUPPORTED` is
  proposed with a resume event.

## Work-Order Curator

- Objective: independently judge Planner candidates and own the canonical
  Ready/Preauthorized queue.
- Allowed actions: verify current gaps, authorize zero or more complete work
  orders, narrowly Preauthorize mechanical successors, disposition enough
  supply for the throughput-aware target, handle invalidation, and edit only
  directly coupled control-plane contract tests under the anti-cheating rule.
- Forbidden actions: implement firmware/configurator product code, edit
  runtime/product tests, rubber-stamp Planner scores, invent and authorize a
  materially new idea in one step, or weaken governance invariants.
- Required return format: live base, packet/provenance, runway before/after,
  candidate dispositions, authorizations, Planner refresh signal, validation,
  and runtime product code changed: NO.

## Hardware Evidence Processor

- Objective: validate and record human-supplied controller results for one
  exact candidate Git SHA and firmware artifact SHA-256.
- Allowed actions: verify protocol/result completeness and source drift, record
  PASS/FAIL/PARTIAL/INCONCLUSIVE, and update evidence/control-plane state.
- Forbidden actions: perform or fabricate the physical test, edit runtime
  source, reinterpret incomplete evidence as PASS, or publish source to
  `configurator`.
- Required return format: identity match, protocol completeness, result,
  evidence branch/SHA, queue disposition, and exact repair/retest/publication
  next action.

## Architecture Specialist

- Objective: inspect source-backed architecture boundaries and unknowns.
- Allowed actions: read source/docs/tests/fixtures, map evidence, mark
  inferred or unknown behavior.
- Forbidden actions: claim undocumented backend behavior, implement active
  firmware changes, create semantic authority.
- Allowed file categories: read any relevant repo file; edit only if explicitly
  assigned and scoped.
- Stop conditions: active behavior ambiguity, runtime publication uncertainty,
  source evidence missing.
- Required return format: evidence map, claims, inferred items, unknowns,
  recommendation.

## Implementer

- Objective: make the bounded edit requested by the supervisor.
- Allowed actions: edit allowed files, run scoped checks, report changed files.
- Forbidden actions: touch forbidden paths, broaden scope, use destructive Git,
  add device write/persistence/flashing/runtime-loaded activation.
- Allowed file categories: exactly those named in the handoff.
- Stop conditions: scope creep, failing checks that imply behavior ambiguity,
  firmware source touched unexpectedly.
- Required return format: patch summary, files changed, verification, behavior
  classification, blockers.

## Validator Reviewer

- Objective: review the diff and run required validation.
- Allowed actions: inspect diff, run checkers/builds as required, classify
  behavior, produce findings.
- Forbidden actions: silently fix unrelated changes, ignore hardware gate,
  approve forbidden paths.
- Allowed file categories: read all relevant files; edit only small checker/doc
  corrections if assigned.
- Stop conditions: active behavior changed without hardware plan, unexpected
  firmware source diff, failed required checker.
- Required return format: findings first, validation commands, classification,
  residual risk.

## Docs Status Clerk

- Objective: keep current status/navigation docs aligned with validated state.
- Allowed actions: update docs/status/navigation files and docs-only examples.
- Forbidden actions: edit source, build scripts, protobuf schemas, device write
  paths, or firmware routing.
- Allowed file categories: docs, docs checkers, schemas/examples when assigned.
- Stop conditions: requested wording would claim unproved root cause, Nunchuk
  validation, runtime-loaded config, or active publication support.
- Required return format: status deltas, docs touched, consistency checks.

## Judge Watchdog

- Objective: decide whether the cycle is done, should continue, is blocked,
  needs hardware, is unsafe, or is looping.
- Allowed actions: read summaries, diff stats, validation output, and status
  docs.
- Forbidden actions: edit files, broaden scope, override hardware/source gates.
- Allowed file categories: read-only access to relevant repo files.
- Stop conditions: unsafe path, loop criteria met, missing concrete delta.
- Required return format: one verdict from `JUDGE_WATCHDOG_CONTRACT.md`,
  reasons, required next action.

## Generic Handoff Template

## Implementation Supervisor cycle — GP-VAL-003 (2026-08-31)

- guidance applicable: yes; GP-VAL-003 is a complete H0 READY work order and
  repository mutation requires bounded delegation plus fresh independent review.
- capability discovery: complete available runtime tool catalog inspected;
  native internal subagent facility confirmed available.
- native capability available: yes.
- specialist: bounded read-only source/contract specialist; inspect tracked
  workflow discovery, route extraction, fixture correspondence, health prose,
  manifest dependencies, and exact scope/exclusions; no edits or canonical
  mutation.
- reviewer: fresh independent validator reviewer after implementation; inspect
  the exact diff and run focused route-census, aggregate, census, health,
  framework, navigation, agent-surface, syntax, and diff gates.
- allowed specialist files: publication workflow checker, workflow-census
  fixture, runtime-config health/manifest/census metadata, and directly
  relevant contracts.
- forbidden specialist actions: edits, commits, pushes, workflow execution,
  build/artifact/device actions, dependency or network resolution, or authority
  inference about external callers/owners.
- stop conditions: workflow bytes or classifications drift, external authority
  is inferred, manifest applicability changes, scope expands, or firmware/
  runtime behavior is implicated.
- return format: findings first; exact contract matches/gaps; recommended
  bounded next action.

## Implementation Supervisor cycle — GP-PROV-006 recovery (2026-08-30)

- guidance applicable: yes; GP-PROV-006 is a complete H0 READY work order and
  the supervisor requires bounded delegation plus fresh independent review for
  repository mutation.
- capability discovery: complete runtime tool catalog inspected; native
  internal subagent facility confirmed available.
- native capability available: yes.
- specialist: source/contract specialist; inspect the recovered GP-PROV-006
  partial state against the exact READY scope, source identities, finite INI
  chain, literal/reference correspondence, and excluded PlatformIO/compiler
  claims; read-only, no file edits.
- reviewer: fresh validator reviewer after implementation; inspect the exact
  diff and run the required offline gates for correctness, authority, scope,
  publication, and regression defects; no unrelated edits.
- allowed specialist files: current GP-PROV-006 docs/fixture/checker state and
  platformio.ini/config/glyph/env.ini plus relevant checker contracts.
- forbidden specialist actions: edits, PlatformIO/compiler/build execution,
  dependency/network access, runtime or firmware claims.
- stop conditions: source drift, missing exact correspondence, scope creep, or
  any need to interpret PlatformIO/compiler behavior.
- return format: findings first; exact contract matches/gaps; recommended
  bounded next action.

## Implementation Supervisor cycle — GP-VAL-007 (2026-08-30)

- guidance applicable: yes; GP-VAL-007 is a complete H0 READY work order and
  repository mutation requires bounded delegation plus fresh independent review.
- capability discovery: complete available runtime catalog inspected; native
  internal subagent facility confirmed available.
- native capability available: yes.
- specialist: read-only source/contract specialist; inspect the manifest,
  runner, aggregate adversarial checker, checker census, direct helper-import
  shapes, and exact GP-VAL-007 exclusions; no edits or repository mutation.
- reviewer: fresh independent validator reviewer after implementation; inspect
  the exact diff and run the required metadata, adversarial, census, health,
  aggregate, framework, navigation, and agent-surface gates.
- allowed specialist files: relevant GP-VAL-007 docs, manifest/health fixtures,
  runner/checkers, and tracked tools imports.
- forbidden specialist actions: edits, commits, pushes, builds, dependency or
  network resolution, code execution/import of discovered checkers, and any
  runtime/firmware claim.
- stop conditions: source/manifest drift, dynamic or transitive discovery,
  branch-semantic enforcement, scope creep, or any active behavior delta.
- return format: findings first; exact contract matches/gaps; recommended
  bounded next action.

```yaml
role:
branch/worktree:
objective:
scope:
excluded_scope:
allowed_files:
forbidden_files:
active_behavior_constraints:
verification_required:
stop_conditions:
return_format:
tool_budget:
```

## Implementation Supervisor cycle — GP-VAL-009 (2026-08-31)

- guidance applicable: yes; GP-VAL-009 is a complete H0 READY work order and
  repository mutation requires bounded delegation plus fresh independent review.
- capability discovery: complete available runtime capability catalog inspected;
  native internal subagent facility confirmed available.
- native capability available: yes.
- specialist: bounded read-only schema/contract specialist; inspect the health
  fixture, checker, manifest/census correspondence, exact schema-v3 invariants,
  and focused validation; no edits, commits, pushes, builds, or network.
- reviewer: fresh independent validator reviewer after implementation; inspect
  the exact diff and run focused health, census, manifest, aggregate, full
  current-lane, framework, navigation, agent-surface, compile, and diff gates.
- allowed specialist files: GP-VAL-009 health checker, health fixture/docs,
  manifest/census fixtures, aggregate checker, and directly relevant contracts.
- forbidden specialist actions: repository mutation, discovered-checker
  execution outside authorized validation, dependency/network resolution,
  firmware/runtime/product claims, build, hardware, or publication.
- stop conditions: duplicate exclusion authority accepted, incomplete exact
  schema/correspondence, manifest/census drift, scope expansion, or any active
  behavior change.
- return format: findings first; exact contract matches/gaps; validation
  results; residual risks and bounded next action.

## Bounded recovery supervisor — 2026-09-06

Guidance applies. The native collaboration capability is available; independent
contract Curator, bounded implementation and persistence specialists, fresh
postimplementation reviewers, and separate Planner/portfolio Curator passes
are used. Root owns Git, authoritative validation and publication. Specialists
use separate temporary repositories or read-only source inspection; no device,
build, firmware, or hardware work is delegated. The failed local implementation
log at ab8e68e remains historical evidence and is superseded by this recovery
record, not evidence of a passing review.

## Implementation Supervisor cycle — GP-PERSIST-002 (2026-09-19)

- guidance applicable: yes; GP-PERSIST-002 is a complete H1 READY work order
  and repository mutation requires bounded delegation plus fresh independent
  review.
- capability discovery: complete available runtime tool catalog inspected;
  native internal subagent facility confirmed available.
- native capability available: yes.
- specialist: Euclid, bounded read-only source-authority specialist; inspect
  exact HandleGetConfig and LoadConfigRaw control flow, existing persistence
  research/harness seams, adversarial cases, and invalidation conditions.
- reviewer: fresh independent validator reviewer after implementation; inspect
  exact GP-PERSIST-002 diff, source correspondence, host-only harness cases,
  non-claims, manifest/census/health wiring, and required focused gates.
- allowed specialist files: the two production source bodies, current
  persistence research, related fixtures/checkers, and host harness seams.
- forbidden specialist actions: edits, commits, pushes, builds, device/config.bin
  access, protocol or firmware decisions, persistence/recovery/hardware claims,
  and network dependency resolution.
- stop conditions: production source drift, copied rather than literal bodies,
  invented filesystem/device semantics, missing adversarial cases, scope creep,
  or any firmware/protocol/persistence/recovery/hardware behavior change.
- return format: findings first; exact control-flow correspondence; harness
  seams; risks; invalidation conditions.

## Implementation Supervisor cycle — GP-SRC-007 (2026-09-19)

- guidance applicable: yes; GP-SRC-007 is a complete H1 READY work order and
  repository mutation requires bounded delegation plus fresh independent review.
- capability discovery: complete available runtime tool catalog inspected;
  native internal subagent facility confirmed available.
- native capability available: yes.
- specialist: Darwin, bounded read-only source-authority specialist; inspect
  the coordinate-native converter, bridge fixtures/checker, direct generator
  path, and the exact fail-closed scope.
- reviewer: fresh independent validator reviewer after implementation; inspect
  the exact GP-SRC-007 diff, fail-closed corpus, direct generator regression,
  non-claims, manifest/census/health wiring, and required focused gates.
- allowed specialist files: the converter, coordinate-native contract checker,
  bridge fixtures/docs, generated source-owned layout-spec generator path, and
  directly relevant contracts.
- forbidden specialist actions: edits, commits, pushes, builds, device/config
  access, runtime/protocol/persistence/hardware decisions, and network
  dependency resolution.
- stop conditions: accepted profile still emits the fixed packet, direct
  layout-spec generation changes, a positive mapping or ownership claim is
  inferred, scope expands into active source/runtime/device behavior, or a
  required checker fails.
- return format: findings first; exact source correspondence; focused checks;
  risks; invalidation conditions.

## Implementation Supervisor cycle — GP-PROV-011 (2026-09-20)

- guidance applicable: yes; GP-PROV-011 is a complete H1 READY work order and
  repository mutation requires bounded delegation plus fresh independent review.
- capability discovery: complete available runtime capability catalog inspected;
  native internal subagent facility confirmed available.
- native capability available: yes.
- specialist: Noether, bounded read-only source-authority specialist; inspect
  the finite hardware-correspondence critical inventory, shared tracked-worktree
  seam, builder identity, artifact custody, and GP-PROV-009 coverage.
- reviewer: Kant, fresh independent post-implementation reviewer; inspect the
  exact GP-PROV-011 diff, ignored source/build/workflow inventory, exclusions,
  regressions, and focused validation.
- allowed specialist/reviewer files: tools/glyph_tracked_worktree_integrity.py,
  tools/glyph_hardware_correspondence.py, builder_scripts/arduino_pico.py,
  tools/glyph_hardware_artifact_custody.py, their focused checkers/tests, and
  directly coupled contracts.
- forbidden specialist/reviewer actions: edits, commits, pushes, firmware or
  device actions, artifact creation/custody mutation, GP-VAL-011 isolation or
  timeout redesign, dependency/network resolution, and authority inference.
- stop conditions: critical inventory drift, cache/custody scanning, ignored
  tree or nested-repository redesign, active firmware/runtime behavior beyond
  the expected embedded Git identity consequence, or focused/reviewer failure.
- return format: findings first; exact scope/authority correspondence;
  validation results; residual risks; bounded next action.

## Implementation Supervisor cycle — GP-X1-002 (2026-09-21)

- guidance applicable: yes; GP-X1-002 is a complete H2 READY work order and
  repository mutation requires a bounded source-authority specialist plus a
  fresh independent post-implementation reviewer.
- capability discovery: native collaboration agents are available.
- specialist: bounded read-only source-authority/firmware-safety specialist;
  inspect the exact intake, sole-table source delta, route/publication
  preservation, protocol, checker consequences, and stop conditions.
- reviewer: fresh independent post-implementation reviewer; inspect the exact
  committed candidate diff, authority, source/table correspondence, exclusions,
  focused validation, canonical build, artifact custody, and handoff metadata.
- forbidden specialist/reviewer actions: edits, commits, pushes, merges,
  flashing/device actions, invented binding/gameplay semantics, GP-CONFIG-010
  mutation, Senscope mutation, persistence/runtime-loaded config, or hardware
  acceptance claims.
- stop conditions: any table other than kX1Table changes, routing/publication or
  Mode/MX1 behavior changes, authority/identity mismatch, failed validation,
  failed build/review/custody, or required physical mapping is invented.

## Implementation Supervisor cycle — GP-CONFIG-016 (2026-09-28)

- guidance applicable: yes; GP-CONFIG-016 is a complete H1 READY work order;
  repository mutation requires a bounded specialist for the exact production
  source/call-site seam and a fresh independent post-implementation reviewer.
- capability discovery: complete available runtime tool catalog inspected;
  191 runtime tools enumerated; native internal collaboration subagents
  confirmed available.
- native capability available: yes.
- specialist: bounded read-only source-authority investigation of the exact
  `NeoPixelBackend::SendReport` body, null-producing `SetGameMode` branches,
  Glyph loop1 call topology, and existing host-test seams/cases.
- reviewer: fresh independent post-implementation reviewer of the exact
  changed paths, literal production-source correspondence, case separation,
  sanitizer evidence, scope/non-claims, and required validation gates.
- allowed specialist/reviewer files: exact NeoPixel backend and Glyph call-site
  source, GP-CONFIG-016 order, directly related fixtures/checkers and existing
  characterization harnesses/contracts.
- forbidden specialist/reviewer actions: edits, commits, pushes, firmware
  builds, device/hardware actions, RGB fallback/product policy, firmware repair,
  physical reachability or crash claims, runtime config, persistence, or
  network/dependency resolution.
- stop conditions: material source/call-topology drift, inability to
  literal-include the exact method, host doubles replacing the target body,
  unseparated injected/source-supported states, active behavior scope, or any
  physical/root-cause claim.
- return format: findings first; exact source anchors; case and harness
  recommendations; validation gaps; residual risks and invalidation conditions.

Recovery continuation on live `configurator` `2fd9a827b90b2079f981d75e836833dc99ec7b10`:
the read-only specialist checked exact source/caller blobs and validation
manifest/census/health drift. A separate fresh read-only reviewer inspected
the recovered 13-path diff, focused PASS results, and full aggregate FAIL;
review found host RGB schema correspondence to repair and four pre-existing
aggregate blockers. Root owns the repair, re-review, final gates, and
publication decision.

Recovery continuation on live `configurator` `e30fd2435fac5986c6536ae876dd956d9431ef73`
(2026-09-29): repository delegation guidance applies; native internal
collaboration agents are available. Two bounded read-only specialists checked
the GP-CONFIG-010 generated-header capacity gate and the GP-CONFIG-009 menu
source-digest drift against that exact live commit. A third read-only specialist
investigated the generated-header materialization evidence gate. A fresh
independent read-only reviewer inspected recovered GP-CONFIG-016 candidate
`cea311d9c0174c0b0c13652157fc092dc699113e` against live, including merge
integrity, exact changed paths, focused results, aggregate failures, scope,
authority, and publication safety. Specialists and reviewer were excluded from
edits, Git publication, firmware build, device or hardware action, and new
backend-behavior claims. Root retains validation and publication authority;
the full aggregate gate remains failure-bearing.
## Implementation Supervisor cycle — GP-VAL-028 (2026-09-29)

- guidance applicable: yes; GP-VAL-028 is a complete H1 READY work order and
  repository mutation requires bounded delegation and fresh independent review.
- capability discovery: native internal collaboration agents are available.
- native capability available: yes.
- specialists: a read-only header-provenance specialist independently
  regenerated the exact `bdd72a22` Nanopb 0.4.9.2 header; a bounded
  implementation agent prepared host fixture, checker, provenance, and
  validation changes in an isolated worktree. Root retained Git, authoritative
  validation, and publication decisions.
- reviewer: a fresh independent post-implementation reviewer checked exact
  scope, generated-byte custody, fail-closed source and manifest correspondence,
  sanitizer coverage, adversarial negatives, history separation, and repaired
  findings before the final candidate gate.
- forbidden delegated actions: canonical queue or source publication, firmware
  build, active source/selector/schema edits, device or hardware action, and
  claims about the historical tested artifact's Nanopb package identity.
- stop conditions: generated-header or provenance mismatch, weaker exact-source
  proof, unreviewed active behavior, failed full aggregate, or publication drift.

## Implementation Supervisor cycle — GP-CONFIG-012 (2026-09-29)

- guidance applicable: yes; complete H1 READY order; exact decoder/source
  characterization only, with no firmware policy or behavior change.
- capability discovery: complete runtime tool catalog inspected (202 available
  tools); native internal collaboration capability confirmed.
- native capability available: yes.
- specialist: `/root/gp_config012_source`, read-only verification of exact
  source and Nanopb closure identities, production callers, default values,
  and compatible-range cache caveat.
- reviewer: `/root/gp_config012_review` found one attribution bug: the backend
  harness probe shifted before entering production on raw zero. Root fixed the
  probe to use a safe all-ones input mask. Fresh repaired-scope reviewer
  `/root/gp_config012_repaired_review` returned PASS on the changed harness,
  caller reachability, exact closure/source binding, manifest wiring, and
  non-claims.
- reviewer/specialist scope: read-only; no delegated edits, commits, pushes,
  firmware builds, device or hardware actions, policy selection, or physical
  behavior claims.
- stop conditions: any source or closure drift, caller probe that can fail
  before production, ambiguous sanitizer attribution, unavailable current
  aggregate proof, or requested scope crossing into invalid-button policy,
  firmware, build inputs, persistence, device writes, or physical acceptance.


## Implementation Supervisor cycle — GP-CONFIG-012 (2026-10-02)

- guidance applicable: yes; the current READY H1 order and supervisor contract
  require bounded specialist verification, a fresh independent post-implementation
  reviewer, and strict completion publication.
- capability discovery: inspected the complete runtime capability catalog (242
  tools); the native collaboration facility is available.
- native capability available: yes.
- specialist used: `gp_config012_source_audit`, read-only verification of all 22
  candidate paths/modes, thirteen source/build-selector hashes, GP-PROV-014
  decoder/schema/generated/license closure, source correspondence, and
  integration compatibility on current configurator `18a71ef`.
- reviewer used: fresh independent `gp_config012_independent_review` approved
  exact integration `0b792540f2f3887da1b2ccc8784c3e07b7316be6` against
  `18a71ef` with no material findings.
- exact changed scope: candidate integration remains the authorized 22 regular
  `100644` source-free paths; no firmware/build input, runtime behavior, or
  product policy changed.
- validation: candidate host proof, exact 22/22 correspondence, current and
  historical GP-CONFIG-010 proofs, 45 correspondence tests, full runtime-config
  aggregate, framework, sequence, navigation, agent-surface, and Python syntax
  passed. The exact upstream decoder/generated fixture bytes were retained;
  `git diff --check` identifies their preserved whitespace.
- stop conditions: none. No firmware build or hardware work was applicable.
