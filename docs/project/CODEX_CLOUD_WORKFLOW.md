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

## Command-policy check

Before depending on the build wrappers, verify they are present and executable:

```bash
test -x ./scripts/pio-local.sh
test -x ./scripts/build-glyph-mk6-quiet.sh
```

Cloud environments may not have `.venv`; local environments may have `.venv`, but scripts must fall back safely. Do not assume `rtk` or `semble` exists in cloud environments.

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
