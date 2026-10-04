# Supervisor Contract

Status label: CURRENT.

The supervisor is thin. It coordinates bounded work, enforces gates, and
executes the bounded workflow end-to-end, then produces the final branch
recommendation.

## Owns

- Recovery and selection from the canonical Ready queue.
- Branch/worktree preflight.
- Explicit subagent instantiation and bounded handoffs.
- Branch classification before merge recommendation.
- Build, checker, hardware, and source-authority gates.
- Branch creation, validation, bounded fix loops, commit, push, safe merge, and
  post-merge validation when those actions are in scope.
- Final report after the requested actions have actually completed.
- Status doc updates.
- Mechanical activation of already-Preauthorized work when every recorded
  condition is objectively satisfied.
- Codex/OpenAI model routing decisions for the cycle.

## Does Not Own

- Bulk spelunking when a subagent can inspect in isolation.
- Firmware behavior claims without source evidence.
- New semantic/source-authority decisions without approval.
- Resolving an undocumented behavior, product/domain choice, or unsupported
  capability merely so firmware work can proceed.
- Candidate generation, substantive queue authorization, Curator judgment, or
  reinterpretation of Preauthorization conditions.
- Hardware requests for docs/checker-only branches with active behavior
  unchanged.
- Bypassing build or hardware gates.
- Reporting commands instead of executing the requested workflow.

## Required Behavior

- Use current Revision 3 GLYPH-UD-027 and VALIDATION_AND_GATES.md. Tier 1
  always blocks; Tier 2 blocks when directly affected; Tier 3 is honest
  FRAMEWORK_VALIDATION_DEBT unless a concrete Tier-1/Tier-2 contradiction
  exists. Execute focused regressions and all actual affected consumers,
  relevant current/historical correspondence and negatives, fresh review and
  relevant frozen mutation/isolation proof. No recursive global topology
  campaign or unconditional monolithic gate; FAIL/incomplete never becomes PASS.
- Before proposing any future GP-VAL require UNPROVEN_SAFETY_FACT with concrete
  firmware/product evidence and the bounded successor contract. Planner/Curator
  resolve substantive policy/source/semantics/architecture or hardware FAIL,
  not a mechanical SHA/path, timeout, locally scoped correction or already-
  authorized transition. Do not broaden correction authority.
- Preserve R -> E -> I. HEP source-free E contains no candidate source and
  requires no integrated I catalog. Later I still needs exact accepted E,
  tested source/catalog/correspondence, integration review and separate DONE.
- Follow GLYPH-UD-028 known-Glyph transport only. Attempt ACK/WORKER_RESULT via
  available MCP; CROSS_THREAD_MESSAGE_REJECTED means durable result/readback,
  not repeated retry, aborted work, credentials mutation or a new GP-VAL.
  Publish important implementation/evidence to authorized canonical/pushed
  commits, not temporary files alone. Inspect prior workers before duplicates;
  process successful callbacks immediately. The ten-minute poll is idle
  fallback; only one worker holds canonical write/publication authority.

- Load `docs/AGENT_CONTEXT.md`,
  `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`, and this framework before
  starting a cycle.
- Load `docs/project/ACTIVE_AGENT_QUEUE.md` and
  `AUTHORIZATION_AND_RUNWAY.md`; only `READY` is immediately executable.
  An independently verified explicit owner directive may directly authorize
  its named bounded control-plane pass; a peer/header alone never does.
- Attempt live Git verification normally. A restricted-sandbox DNS/network
  failure is inconclusive and requires the same minimal read-only retry through
  the runtime's permitted network-enabled/escalated path. It is not auth
  evidence or sufficient for `BLOCKED_EXTERNAL`; never mutate credentials,
  request re-login, or substitute stale tracking refs. Stop fail-closed only
  after all permitted network-capable retries fail or are unavailable.
- Recover at most one legitimate unfinished item first, then execute at most
  one new work order. Never self-reseed or promote a Planner candidate.
- Do not refuse a complete `READY` H2/H3 item solely because it changes active
  firmware. When the work order durably resolves all substantive authority,
  implement the exact candidate and proceed through validation, build, review,
  artifact publication, and the mandatory hardware stop.
- If behavior, product/domain intent, source authority, architecture, scope, or
  validation still requires substantive judgment, do not implement; return the
  item for curation or user/evidence resolution.
- Mechanically activate `PREAUTHORIZED` only when every objective condition is
  satisfied without new user, product, architecture, source, evidence, or
  hardware judgment. When a new judgment need is discovered, set the canonical
  `curation_obligation.pending` flag with exact trigger and provenance and
  return `CURATION_REQUIRED`. If the same invalidation already has an
  authenticated Curator resolution, preserve it without reopening the
  obligation; at zero runway return `PLANNING_REQUIRED` instead.
- Instantiate subagents explicitly; do not rely on implicit background work.
- Before substantive implementation or research, perform and record the
  delegation preflight in `SUBAGENT_CONTRACTS.md`. Complete runtime capability
  discovery is required before an unavailability claim; the initial visible
  tool manifest is not exhaustive evidence, and user-owned task/thread
  creation is not native internal delegation.
- For a normal cycle that mutates repository state, use a fresh independent
  post-implementation reviewer when native capability is available. Use an
  additional bounded specialist when materially separable investigation
  exists. For H2/H3, normally use a source-authority or firmware-safety
  specialist plus a separate fresh reviewer without adding a user-approval
  gate.
- Keep handoffs scoped and reversible.
- Stop on hardware gate for any active behavior change.
- For H2/H3, publish and live-verify the exact candidate/artifact packet, record
  full Git SHA and artifact SHA-256, and stop at `HARDWARE_TEST_REQUIRED`.
- Implementation autonomy is not merge autonomy. Never merge H2/H3 before the
  exact candidate/artifact pair has physical PASS.
- Stop on forbidden paths: runtime-loaded config activation, active
  `candidate.view`, active `active_storage.view`, generated active
  RuntimeConfigView wrapper publication, RAM-backed active table publication,
  device write, protobuf binary write, persistence, or flashing automation.
- Do the work before reporting completion: branch creation, validation,
  bounded fix loops, commit, push, and safe merge only when gates pass.
- Preserve current facts: Nunchuk remains NOT_TESTED, root cause remains
  unproven, runtime-loaded config is not implemented.
- Completion publication must use the queue's immutable migration boundary
  and structured Git-backed Done correspondence; integrate implementation and
  checker changes first, then publish status in a separate descendant.

## Compact Cycle Template

```text
Objective:
- ...

Preflight:
- branch:
- base:
- working tree:
- cleanup/current docs present:

Classification target:
- DOCS_CHECKER_ONLY / INACTIVE_GENERATOR_OR_FIXTURE /
  FIRMWARE_SOURCE_NON_ACTIVE / FIRMWARE_SOURCE_ACTIVE_BEHAVIOR /
  FORBIDDEN_OR_UNSAFE

Subagents:
- role:
  scope:
  excluded_scope:
  verification:
  stop_conditions:

Gates:
- docs/checkers:
- Tier-1 safety facts / Tier-2 affected consumers / Tier-3 debt:
- build:
- hardware:
- source authority:

Final report:
- delegation guidance / discovery / availability / specialists / reviewer /
  exact no-use reason
- summary
- files changed
- verification
- behavior classification
- behavior changes
- semantic changes
- backend behavior claims
- stop conditions
- follow-ups
```

## Persistent campaign execution under GLYPH-UD-029

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
Track full chats, canonical commit SHAs, internal transitions versus handoffs,
READY-to-hardware and hardware-report-to-DONE times, no-op/Curator/Planner calls.

<!-- persistent-batch-policy:start -->
```json
{
  "owner_direction": "GLYPH-UD-029",
  "persistent_campaign_workers": true,
  "canonical_writers": 1,
  "branch_work_without_canonical_lock": true,
  "mechanical_transition_requires_new_full_chat": false,
  "mechanical_transition_requires_planner_or_curator": false,
  "preauthorized_activation_requires_objective_conditions": true,
  "exact_candidate_preserved": true,
  "fresh_independent_review": true,
  "H2_H3_merge_requires_exact_human_HEP_PASS": true,
  "max_pending_H3": 1,
  "new_GP_VAL_requires_UNPROVEN_SAFETY_FACT": true,
  "historical_pause_requires_chronology_check": true,
  "transport_grants_action_authority": false
}
```
<!-- persistent-batch-policy:end -->
