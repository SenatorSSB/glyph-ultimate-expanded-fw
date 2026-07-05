# AGENTS.md

This repository is the Glyph / HayBox firmware-backend workstream only. It may
inform Senscope backend realization boundaries, but Senscope owns game
semantics, datasets, and solver authority.

## Start Here

Read these files before using older calibration packets:

- `docs/AGENT_CONTEXT.md` - first-read current agent state.
- `docs/CURRENT_STATE.md` - factual current baseline and non-claims.
- `docs/ROADMAP.md` - current milestone and intent state.
- `docs/WORKFLOW.md` - branch, test, inspection, merge, and result procedure.
- `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md` - hard runtime-config
  implementation boundary.
- `docs/agent_framework/README.md` - supervisor/subagent contracts,
  classifications, gates, and templates.

Treat `docs/calibration/` as evidence and historical packets. Prefer canonical
current docs over old blocker packets when they conflict. Treat
external-remapper docs as quarantined unless independently source-backed.
Official Glyph configurator corpus is the primary corpus when the
misattribution correction packet and official corpus manifest are present.

## Commands

Canonical firmware build command:

```bash
pio run -e glyph_mk6
```

Fallback build command:

```bash
./scripts/build-glyph-mk6-quiet.sh
```

For docs-only work, use `git status` and `git diff --stat` first, then the
relevant repo checkers.

## Non-Negotiable Rules

- Do not invent Glyph/HayBox firmware behavior.
- Do not invent Super Smash Bros. Ultimate gameplay semantics.
- Do not claim undocumented backend behavior as fact.
- Do not add runtime-loaded profile/config, WebSerial/device write, protobuf
  binary write, backend config write, persistent runtime-config storage, or
  flashing automation without explicit approval and source support.
- Do not run destructive Git commands: no `git reset`, `git clean`,
  `git stash`, `git revert`, or force-push unless explicitly approved.
- Behavior-changing active firmware source requires build proof and hardware
  PASS before merge.
- Docs/checker-only changes with active firmware behavior unchanged do not
  require hardware.
- Nunchuk remains NOT_TESTED unless the user explicitly reports a test.
- Root cause remains unproven unless direct evidence is found.

## Source Authority

A backend behavior claim must reference source, docs, tests, fixtures,
user-provided research, or an explicit user/domain statement. If behavior is
inferred, mark it as inferred. If behavior is unknown, say unknown.

## Stop Conditions

Stop before implementing if the task requires firmware behavior changes,
runtime-loaded config, device write, protobuf binary write, persistence,
flashing automation, neutral profile schema changes, game-semantic decisions,
vendor export format decisions, or any undocumented backend capability claim.
