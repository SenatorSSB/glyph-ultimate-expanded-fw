# Agent Operating Contract

This document defines how semi-autonomous coding agents should work in the Glyph-side controller implementation / backend realization repository.

## Purpose

This repo has source-authority requirements around controller/backend behavior. Agents may inspect, document, model, and implement bounded engineering work, but they must not invent firmware behavior or gameplay semantics.

The intended workflow is:

```text
User/domain expert
  -> ChatGPT architecture/control plane
  -> Codex orchestrator or implementation agent
  -> current repo branch
  -> pushed changes
  -> inspection/review
```

## Roles

### User/domain expert

Owns:

- final controller/backend interpretation;
- source-authority decisions;
- integration priorities;
- permission approval;
- decisions about push/export support;
- decisions that affect Senscope neutral profile compatibility.

### ChatGPT control plane

Owns:

- architecture planning;
- issue sequencing;
- prompt generation;
- pushed-branch inspection;
- identifying stop points;
- turning user decisions into implementation contracts.

### Codex orchestrator agent

Owns:

- reading the active queue;
- decomposing the batch into safe execution steps;
- enforcing stop conditions;
- avoiding destructive overlap if multi-agent work is used;
- running verification;
- producing a final report.

### Codex implementation agent

Owns:

- implementing one bounded issue or subtask;
- running targeted checks;
- committing/pushing only under the branch policy;
- reporting verification evidence.

### Reviewer / audit agent

Optional.

Owns:

- comparing implementation against issue contract;
- checking whether behavior claims are source-backed;
- checking tests;
- identifying drift;
- not making broad rewrites unless separately instructed.

## Default autonomy

Default autonomy is Tier 2:

```text
Autonomous with explicit stop conditions.
```

Agents may proceed through mechanical implementation, but must stop when source authority, backend behavior, export behavior, or Senscope integration semantics become ambiguous.

## Branch policy

Work on the current checked-out branch unless instructed otherwise.

If branch/remote policy is unclear:

```text
stop and report
```

Do not merge into protected/default branches unless explicitly instructed.

## Environment command policy

Command usage must support local and cloud environments.

- Do not assume `rtk` exists.
- Do not assume `.venv` exists.
- Do not assume `semble` exists.
- Use repo-native commands after inspecting package files.
- Prefer safe direct commands if wrappers are unavailable.
- Report fallback when using direct equivalents.

Safe baseline commands:

```bash
git status
git diff --stat
git diff -- <file>
rg "<pattern>" <paths>
git grep "<pattern>"
find . -maxdepth 3 -type f
sed -n '1,260p' <file>
```

Python policy:

- Use `python3` only when needed and available.
- If Python dependencies are missing, stop and report.
- Do not invent environment setup.

Package/build policy:

- Inspect package files before choosing commands.
- Run targeted tests where possible.
- Do not run broad expensive test suites unless requested or required for confidence.

## Source-authority policy

Sources are not equal.

### Backend/controller authority

Promotable evidence may include:

- firmware source;
- configuration schema;
- official docs;
- repository tests;
- fixtures;
- user-confirmed behavior;
- inspected implementation paths.

### Not authority by itself

- guesses;
- analogous behavior from another controller;
- undocumented community assumptions;
- manual interpretation without source;
- Senscope game-semantic data.

## Relationship to Senscope

This repo may produce findings for Senscope integration, but it must not mutate Senscope semantic source authority.

Valid integration targets:

- neutral profile compatibility;
- backend capability model;
- realization evaluator;
- manual-entry guide;
- diagnostics for unsupported/unknown backend outputs;
- adapter contracts.

Invalid without explicit approval:

- direct changes to Senscope game semantics;
- new no-smash/no-strong-input behavior;
- gameplay threshold interpretation;
- push-to-device workflows;
- vendor export file generation without source support.

## Stop-before-domain rule

Stop before implementing anything that requires answering:

```text
What Smash gameplay semantic should this coordinate satisfy?
```

That belongs to Senscope game-domain work, not this repo.
