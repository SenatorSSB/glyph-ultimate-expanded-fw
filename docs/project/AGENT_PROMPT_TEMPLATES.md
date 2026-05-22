# Agent Prompt Templates

Use these templates when launching Codex agents in this repo.

## Command policy snippet

```text
Command policy:
  - Verify ./scripts/pio-local.sh and ./scripts/build-glyph-mk6-quiet.sh are executable before relying on them.
  - For docs-only tasks, use git status and git diff --stat.
  - For firmware/build-affecting tasks, use ./scripts/build-glyph-mk6-quiet.sh.
  - Use ./scripts/pio-local.sh run -e glyph_mk6 only when debugging full build output.
  - Do not paste full successful PlatformIO logs into final reports.
  - On build failure, report only the final 80 log lines unless the user asks for more.
  - Use repo-native commands after inspecting package files.
  - Do not assume rtk exists.
  - Do not assume .venv exists.
  - Do not assume semble exists.
  - Cloud environments may not have .venv; local environments may have .venv, but scripts must fall back safely.
  - If a prompt mentions unavailable tools, use safe direct equivalents and report fallback.
  - Use python3 only if needed and available.
  - If Python dependencies are missing, stop and report the missing dependency.
```

## Single-batch implementation prompt

```text
We are continuing the Glyph-side controller implementation / backend realization repo.

Read:
- AGENTS.md
- docs/project/ACTIVE_AGENT_QUEUE.md
- docs/project/AGENT_OPERATING_CONTRACT.md
- docs/project/AGENT_STOP_CONDITIONS.md
- docs/project/AGENT_FINAL_REPORT_TEMPLATE.md
- docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md

Execute the current queue exactly as written.

Autonomy:
  Use the tier specified in ACTIVE_AGENT_QUEUE.md.

Hard constraints:
  - Do not invent Glyph/HayBox firmware behavior.
  - Do not invent Smash gameplay semantics.
  - Do not change Senscope semantic-source authority.
  - Do not add export or push-to-device workflows.
  - Do not change neutral profile schema.
  - Do not reset/stash/clean/revert.
  - Do not force-push.

When done:
  - run required verification;
  - commit and push only if branch policy is clear;
  - report using docs/project/AGENT_FINAL_REPORT_TEMPLATE.md.
```

## Orchestrator prompt

```text
You are the Codex orchestrator for the Glyph-side controller implementation / backend realization repo.

Read:
- AGENTS.md
- docs/project/ACTIVE_AGENT_QUEUE.md
- docs/project/AGENT_OPERATING_CONTRACT.md
- docs/project/AGENT_AUTONOMY_TIERS.md
- docs/project/AGENT_STOP_CONDITIONS.md
- docs/project/AGENT_FINAL_REPORT_TEMPLATE.md
- docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md

Your job:
  - inspect the active queue;
  - decide whether tasks can be implemented sequentially or in parallel;
  - avoid overlapping file edits;
  - enforce stop conditions;
  - run required verification;
  - commit/push only if branch policy is clear.

Do not invent controller behavior.
Do not invent gameplay semantics.
Do not add export/push workflows.
Do not change Senscope semantic-source authority.

If a stop condition is hit:
  - stop;
  - do not commit partial risky behavior;
  - report the blocker and exact files/state.
```

## Reviewer/audit prompt

```text
You are reviewing the latest pushed branch for the Glyph-side repo.

Read:
- AGENTS.md
- docs/project/ACTIVE_AGENT_QUEUE.md
- docs/project/AGENT_STOP_CONDITIONS.md
- docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md

Audit only. Do not make code changes unless explicitly instructed.

Check:
  - issue contract was followed;
  - no unsupported controller behavior was claimed;
  - no gameplay semantics were added;
  - no Senscope semantic-source authority changed;
  - no export/push workflow was added;
  - tests reported by the implementing agent are relevant.

Return:
  - pass/fail assessment;
  - risks;
  - required fixes;
  - next recommended batch.
```

## Source-data / external docs staging prompt

```text
We need to stage source or documentation files in the Glyph-side repo.

Rules:
  - Pull latest intended branch.
  - Add/update source/docs files only as explicitly listed.
  - Do not change generated artifacts unless explicitly instructed.
  - Run minimal inventory or checksum commands if available.
  - Commit source/docs changes separately if branch policy is clear.
  - Report file paths and checksums if available.
```
```

## docs/project/ORCHESTRATION_MODEL.md

```md
# Orchestration Model

This repository supports either single-agent execution or orchestrated multi-agent execution.

## Default recommendation

Use one Codex agent for tightly coupled implementation batches.

Use an orchestrator agent when a batch contains independent subtracks.

## When to use one agent

Use one agent when tasks touch overlapping files, such as:

- capability model plus evaluator;
- adapter interface plus diagnostics;
- source inventory plus architecture doc;
- tests for the same behavior.

Reason: one agent reduces merge conflicts and context drift.

## When to use multiple agents

Use multiple agents only when file ownership is clearly separated.

Example safe split:

```text
Agent A:
  firmware/source inventory

Agent B:
  docs/test command discovery

Agent C:
  capability model design doc

Agent D:
  Senscope integration boundary doc
```

Example unsafe split:

```text
Multiple agents editing the same adapter/evaluator files.
Multiple agents changing capability model and tests independently.
Multiple agents making source-authority claims from different evidence.
```

## Orchestrator responsibilities

The orchestrator must:

1. read the active queue;
2. inspect branch/remote policy;
3. decide task/file partitioning;
4. assign non-overlapping work;
5. collect results;
6. run required verification;
7. stop on source-authority blockers;
8. produce one final report.

## Multi-agent stop conditions

Stop the whole batch if any agent reports:

- undocumented controller behavior required;
- source contradiction;
- test contradiction;
- export/push workflow needed;
- neutral profile schema change needed;
- gameplay semantics needed;
- branch/remote ambiguity.

## Commit policy

Preferred:

```text
one commit per completed batch
```

Acceptable:

```text
one commit per issue
```

Avoid:

```text
many tiny unreviewable commits
```

The final pushed branch must pass required verification.
```

## docs/project/CODEX_CLOUD_WORKFLOW.md

```md
# Codex Cloud Workflow

This repo may use Codex cloud or local Codex.

## Cloud by default when convenient

Cloud tasks can work in isolated repository environments and run commands/tests before returning results for review.

Cloud environments may not have local tools.

Do not assume:

- `rtk`;
- `.venv`;
- `semble`;
- local credentials;
- local hardware.

## Local repo role

Use local repo for:

- source file inspection;
- hardware-adjacent work;
- firmware flashing only if explicitly authorized;
- local toolchain checks;
- emergency Git repair;
- source-data commits.

## Default loop

```text
1. User asks ChatGPT control plane for next batch.
2. ChatGPT writes/updates queue or prompt.
3. Codex executes the batch.
4. Codex pushes if branch policy is clear.
5. User says: "pushed, inspect".
6. ChatGPT inspects and plans next step.
```

## Cloud task instructions

Every cloud task should include:

```text
Read AGENTS.md.
Read ACTIVE_AGENT_QUEUE.md.
Use repo-native commands.
Do not assume local wrappers.
Stop on source-authority blockers.
Do not invent controller behavior.
Do not add gameplay semantics.
```

## Approval policy

Approve:

- read/list/search commands;
- targeted tests;
- typecheck/build commands;
- normal commits/pushes to intended branch.

Do not approve:

- reset;
- clean;
- stash;
- revert;
- force push;
- broad source deletion;
- unexplained dependency installs;
- hardware/push-to-device commands unless explicitly intended.

## Branch protection discipline

Protected/default branches are integration-only.

Do not merge without human review.
