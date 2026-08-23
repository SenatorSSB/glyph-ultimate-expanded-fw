# Glyph Workflow

Status label: CURRENT.

This workflow applies to the Glyph/HayBox-side firmware, configurator, and
backend realization workstream. Keep Senscope browser app work separate unless
explicitly instructed.

## Branch Categories

- Planning: non-authoritative `planning/portfolio-*` candidate packets; never
  implementation recovery or direct publication to `configurator`.
- Curation/control plane: canonical queue, authorization, status, and narrowly
  coupled control-plane contract tests; no product/runtime implementation.
- Docs/tools: navigation, indexes, packets, read-only validators, and checker
  wiring.
- Corpus/evidence: captured official configurator artifacts, source-authority
  packets, fixtures, and correction records.
- Firmware behavior: source changes that can alter controller/backend runtime
  behavior.
- Hardware result: user-reported or operator-recorded test results with artifact
  provenance and scope caveats.
- Exporter/adapter: offline candidate generation, transform design, validator
  work, and adapter boundary records.
- Runtime-loaded config/device write: storage, interpreter, WebSerial,
  protobuf, device-write, or flashing workflow work.

## Inspection Policy

- Inspect feature branches before merge.
- Post-merge inspection is usually not needed for docs/tools after a clean
  merge and passing checkers.
- Post-merge inspection is required for firmware behavior, hardware result,
  device-write, runtime-loaded config, firmware flashing, and other
  behavior-affecting branches.
- Do not infer current roadmap from every calibration file. Prefer
  `docs/CURRENT_STATE.md`, `docs/ROADMAP.md`, and this workflow when old blocker
  packets conflict with current canonical docs.
- Avoid `blocked` for current status unless the task is actually waiting on a
  specific external item. Prefer precise labels such as ready for engineering
  design, ready for source research, waiting for user artifact, waiting for
  hardware test, future phase, product approval required, or forbidden by
  policy.

## Live Remote Verification

Separate local Git inspection from GitHub connectivity. Inspect the repository,
remote URL, refs, status, branches, and worktrees locally, then attempt the
ordinary/default minimal read-only live-remote operation. If the restricted
sandbox cannot resolve or reach GitHub because of environment-level DNS,
network, or sandbox policy, treat that attempt as inconclusive and retry the
same minimal read-only verification through the runtime's permitted
network-enabled/escalated path. The retry grants network access only and does
not expand filesystem, mutation, product, queue, evidence, or publication
authority.

A sandbox DNS/network failure is not authentication evidence and is not enough
for `BLOCKED_EXTERNAL`. Diagnose authentication only after connectivity is
established and GitHub actually rejects credentials or permissions. A failing
sandboxed `gh auth status` is not a reliable authentication oracle when GitHub
cannot be reached. Never automatically run `gh auth login`/`gh auth logout`,
rewrite tokens, delete Git credentials, change credential helpers, replace SSH
keys, switch accounts, or request re-login because of unverified connectivity.
Account-level mutation is user-owned.

If a network-enabled retry succeeds, use its live result as authoritative,
continue normally, and report the restricted failure plus successful retry
without calling it an authentication incident. If every permitted
network-capable retry fails or is unavailable, stop fail-closed with live
remote unverified because all permitted network-capable retries failed. Stale
local remote-tracking refs never substitute for successful live verification.

## Authorization Policy

- `docs/project/ACTIVE_AGENT_QUEUE.md` is the only executable queue.
- Only `READY` authorizes immediate new implementation.
- `PREAUTHORIZED` may activate only through already-authorized objective
  mechanical conditions. New judgment, semantic drift, missing evidence, or
  invalidation returns `CURATION_REQUIRED`.
- Planner packets, roadmap entries, remote branches, and chat recommendations
  are not authorization.
- One normal Implementation Supervisor invocation completes at most one new
  work order, with recovery first.

## Autonomy And Approval Policy

- Docs/tools, source research, and engineering design can proceed autonomously
  when branch scope is clear and source-authority caveats are preserved.
- User domain input is not required for routine engineering design.
- A complete `READY` work order may authorize source-grounded firmware/runtime
  behavior implementation without a fresh user approval solely because the
  work changes active firmware, when all required behavior, product, domain,
  source-authority, architecture, scope, and validation decisions are already
  durably resolved and evidenced.
- User/domain input is required before implementation when the proposed runtime
  behavior still contains an unresolved product, domain, source-authority, or
  unsupported behavior decision that Curator is not authorized to make.
  Curator may not infer user intent or invent undocumented Glyph behavior to
  create executable firmware work.
- Separate explicit approval remains required for runtime-loaded config,
  WebSerial/device write, protobuf binary write, firmware flashing automation,
  external adapter output, or Senscope neutral profile schema changes.
- Runtime-config activation design must keep parser result status, parser
  result fields, payload validation state, CRC state, storage load state, and
  activation decision state out of `UpdateAnalogOutputs` and any resolver used
  by the analog output hot path. Activation/selection may validate and select
  stable state outside the hot path; output generation may consume only that
  stable selected view.
- Runtime-config publication must keep candidate buffer != active buffer. The
  `active_storage_publication_model` packet records that candidate state may
  validate proposed values before publication, but candidate.view and
  candidate-owned runtime table pointers must not become the active runtime
  view. Accepted values must be copied into dedicated active storage before any
  future dedicated-active-storage publication diagnostic.
- Activation/selection may validate parser/materialization/load status before
  active-state publication. After publication, analog output generation may
  consume only `ActiveRuntimeConfigState.active_view` and must not branch on
  `ActiveRuntimeConfigState.source` or `ActiveRuntimeConfigState.status`.
- Parser/materialization/load work belongs before active-state publication;
  output generation may consume only the already-selected `RuntimeConfigView`.
- A future phase may be ready for design or source research while still
  requiring a substantive decision before implementation. Firmware risk alone
  is not that decision: implementation autonomy is not merge autonomy, and
  H2/H3 remains physically gated before merge.
- Safety/policy-forbidden work remains forbidden even if adjacent design or
  source research is allowed.

## Hardware Test Policy

- Hardware validation must be recorded in a result packet with scope,
  artifact/build identity when available, operator/user report, pass/fail rows,
  caveats, and rollback notes if needed.
- H2/H3 acceptance requires the full candidate Git SHA and SHA-256 of the exact
  tested firmware artifact. A new build or relevant source change invalidates
  affected evidence.
- Preserve the exact UF2 at an immutable candidate-SHA/artifact-SHA-addressed
  locator outside mutable `.pio` output and re-hash the retrieved bytes
  immediately before device update. Never substitute a rebuild; without a
  durable artifact locator, stop before hardware handoff.
- Prefer at most one dependent H2/H3 candidate awaiting controller testing at
  once. Independent H0/H1 work may continue when it cannot contaminate the
  candidate.
- A failed candidate and failed active source must not enter `configurator`.
  A result/evidence branch is not source authority; source changes on it require
  renewed review, build, and hardware testing.
- Publish canonical pending and every result queue state on a
  docs/control-plane branch from fresh `configurator`, referencing the pinned
  candidate Git SHA, preserved artifact locator, artifact SHA-256, and evidence
  record without carrying candidate source into the canonical branch.
- Hardware tests are required only after a firmware/candidate artifact exists
  for the stated test scope.
- Nunchuk validation must not be claimed unless nunchuk rows are actually
  executed and recorded.
- User-reported results are allowed when clearly labeled as user-reported and
  bounded to the stated scope.

## Result Recording Policy

- Record result packets close to the evidence they summarize.
- Preserve exact known values and mark unknowns as unknown.
- Do not promote design docs, offline validators, or corpus fixtures into
  hardware evidence.
- Update `docs/CURRENT_STATE.md` and `docs/ROADMAP.md` when the current
  operating state changes.

## Source Authority Policy

- Backend behavior claims must reference repo source, repo docs, repo tests or
  fixtures, user-provided research notes, or explicit user/domain statements.
- Mark inferred behavior as inferred.
- Mark unknown behavior as unknown.
- External-remapper docs are quarantined unless independently source-backed.
- Official Glyph configurator corpus is the primary corpus when the correction
  packet and official corpus manifest are present.

## Merge And Check Expectations

- Start from the intended branch and ensure the worktree is clean.
- For docs-only tasks, run `git status` and `git diff --stat`.
- For firmware/build-affecting tasks, use `pio run -e glyph_mk6`; use
  `./scripts/build-glyph-mk6-quiet.sh` only when the canonical command is
  unavailable and report the fallback.
- Use repo-native checkers touched by the branch.
- Do not run destructive Git commands: `git reset`, `git clean`, `git stash`,
  `git revert`, or `git push --force`.
- Push and verify the exact live remote feature ref, refresh live
  `configurator` immediately before publication, reconcile drift and rerun
  invalidated gates, then verify the exact live remote canonical commit.
- Avoid editor-dependent merge instructions in user-facing command sequences.

## Final Report Format

Use this concise structure for implementation tasks:

```text
Summary:
- ...

Files changed:
- ...

Verification:
- command: result

Behavior changes:
- none / described

Semantic changes:
- none / described

Backend behavior claims:
- none / source-backed / inferred / unknown

Stop conditions hit:
- none / described

Follow-ups:
- ...
```
