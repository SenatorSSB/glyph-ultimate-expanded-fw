# Glyph Workflow

Status label: CURRENT.

This workflow applies to the Glyph/HayBox-side firmware, configurator, and
backend realization workstream. Keep Senscope browser app work separate unless
explicitly instructed.

## Branch Categories

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

## Autonomy And Approval Policy

- Docs/tools, source research, and engineering design can proceed autonomously
  when branch scope is clear and source-authority caveats are preserved.
- User domain input is not required for routine engineering design.
- User product approval is required before firmware behavior implementation,
  runtime-loaded config implementation, WebSerial/device write, protobuf binary
  write, firmware flashing automation, external adapter output, or Senscope
  neutral profile schema changes.
- Runtime-config activation design must keep parser result status, parser
  result fields, payload validation state, CRC state, storage load state, and
  activation decision state out of `UpdateAnalogOutputs` and any resolver used
  by the analog output hot path. Activation/selection may validate and select
  stable state outside the hot path; output generation may consume only that
  stable selected view.
- Activation/selection may validate parser/materialization/load status before
  active-state publication. After publication, analog output generation may
  consume only `ActiveRuntimeConfigState.active_view` and must not branch on
  `ActiveRuntimeConfigState.source` or `ActiveRuntimeConfigState.status`.
- Product approval gates are not the same as user-domain blockers. A future
  phase may be ready for design or source research while still requiring
  approval before implementation.
- Safety/policy-forbidden work remains forbidden even if adjacent design or
  source research is allowed.

## Hardware Test Policy

- Hardware validation must be recorded in a result packet with scope,
  artifact/build identity when available, operator/user report, pass/fail rows,
  caveats, and rollback notes if needed.
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
- For firmware/build-affecting tasks, prefer
  `./scripts/build-glyph-mk6-quiet.sh` when available.
- Use repo-native checkers touched by the branch.
- Do not run destructive Git commands: `git reset`, `git clean`, `git stash`,
  `git revert`, or `git push --force`.
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
