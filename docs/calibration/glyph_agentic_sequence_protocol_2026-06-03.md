# Glyph Agentic Sequence Protocol - 2026-06-03

## Purpose

This document records a workflow protocol only.

- It is not implementation.
- It is not hardware validation.
- It is not authorization to bypass user gates.

The protocol is for long deterministic branch sequences that must stay
docs/tools-only unless a stop condition requires user intervention.

## Scope

- Glyph / HayBox-side controller-backend workstream only.
- One branch per issue.
- Start from current `origin/configurator`.
- Stop if the target branch already exists locally or remotely.
- One conceptual change per branch.
- Merge after each successful branch.
- Run standard checks after each branch and merge.
- No continuation after failed checks.

## Supervisor Role

The supervisor:

- defines the branch objective and scope;
- confirms the branch starts from current `origin/configurator`;
- confirms the target branch does not already exist locally or remotely;
- reviews checker output before any continuation;
- requires user intervention when a stop gate is hit;
- keeps branch history separate and bounded.

## Subagent Role

The subagent:

- works exactly one branch at a time;
- makes one conceptual change per branch;
- stays within docs/tools/fixtures scope unless a stop gate is hit;
- runs the required checks after each branch and merge;
- stops immediately on failed checks;
- reports a final summary in the required format.

## Branch Lifecycle

1. Start from current `origin/configurator`.
2. Refuse to continue if the target branch already exists locally or remotely.
3. Take one conceptual change per branch.
4. Keep the branch docs/tools-only unless a later approved stop gate changes scope.
5. Merge after each successful branch.
6. Do not merge to `configurator` from the subagent.

## Verification Lifecycle

1. Run the standard checks after each branch and merge.
2. Stop on failed checks.
3. Do not continue past a failed check without a source-backed correction path.
4. Do not treat a failed checker/build as automatically correctable.

## User Intervention Gates

User intervention is required only for:

- source-authority ambiguity;
- firmware source approval;
- hardware testing;
- profile artifact approval;
- runtime-loaded config approval;
- serial/device write approval;
- unsupported behavior claims;
- checker or build failures that are not automatically correctable.

## Forbidden Autonomous Actions

The subagent must not autonomously:

- make firmware source changes without approval;
- claim hardware validation;
- implement serial/device write behavior;
- implement runtime-loaded config;
- change profile artifacts;
- make schema/protobuf changes;
- claim unsupported behavior.

## Final Summary Requirements

The final summary must report:

- branch name;
- commit SHA;
- files changed;
- checks run and pass/fail result;
- skipped checks and why;
- whether runtime source changed;
- whether profile artifacts changed;
- whether runtime-loaded config was implemented;
- whether serial/device write behavior was implemented;
- whether hardware validation was claimed;
- stop conditions hit, if any;
- whether the branch is ready for supervisor inspection.

## Notes

- This protocol is for workflow control only.
- It does not authorize a runtime implementation branch.
- It does not authorize hardware validation.
- It does not authorize bypassing user gates.
