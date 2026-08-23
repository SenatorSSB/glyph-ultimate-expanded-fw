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
- `docs/project/ACTIVE_AGENT_QUEUE.md` - the only executable Ready queue.
- `docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md` - Ready,
  Preauthorized, runway, Planner, and Curator authority.

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
- Only a complete `READY` work order authorizes immediate new implementation.
  `PREAUTHORIZED` work may activate only through its recorded objective
  mechanical conditions; judgment returns `CURATION_REQUIRED`.
- H2/H3 hardware acceptance requires the exact candidate Git SHA and exact
  tested artifact SHA-256. A successful build is not controller acceptance.
- Docs/checker-only changes with active firmware behavior unchanged do not
  require hardware.
- Nunchuk remains NOT_TESTED unless the user explicitly reports a test.
- Root cause remains unproven unless direct evidence is found.

## Source Authority

A backend behavior claim must reference source, docs, tests, fixtures,
user-provided research, or an explicit user/domain statement. If behavior is
inferred, mark it as inferred. If behavior is unknown, say unknown.

## Live Git Verification And Sandbox Networking

Every role that requires fresh GitHub truth must attempt the ordinary/default
minimal read-only verification first. If the restricted sandbox cannot resolve
or reach GitHub because of DNS, network, or sandbox policy, the result is
inconclusive: retry the same read-only verification through the runtime's
permitted network-enabled/escalated execution mechanism. That escalation grants
network access only, not broader filesystem, repository-mutation, firmware,
queue, evidence, or publication authority. A sandbox network failure is not
authentication evidence and is not sufficient for `BLOCKED_EXTERNAL`.

Diagnose authentication or authorization only after GitHub connectivity is
established and GitHub rejects credentials or permissions. Sandboxed
`gh auth status` is not an authentication oracle while GitHub is unreachable;
DNS/network failure takes precedence over apparent token messages from a tool
that could not contact the service. Never automatically run `gh auth login` or
`gh auth logout`, rewrite tokens, delete Git credentials, change credential
helpers, replace SSH keys, switch GitHub accounts, or request re-login because
of an unverified connectivity failure. Account-level mutation is user-owned.

Stale local remote-tracking refs never substitute for successful live
verification. Only after every permitted network-capable retry fails or is
unavailable may a role stop fail-closed with `BLOCKED_EXTERNAL`, explicitly
reporting that live remote is unverified because all permitted network-capable
retries failed.

## Stop Conditions

Stop before firmware-behavior implementation when no complete `READY` work
order authorizes it, when a required substantive product, domain,
source-authority, architecture, scope, or validation decision remains
unresolved, or when the work crosses a forbidden boundary. A complete `READY`
H2/H3 work order with resolved substantive authority may be implemented as an
exact candidate, but it must never merge before its required exact-snapshot
hardware PASS.

Stop before runtime-loaded config, device write, protobuf binary write,
persistence, flashing automation, neutral profile schema changes,
game-semantic decisions, vendor export format decisions, or any undocumented
backend capability claim unless their separate explicit approval and source
requirements are satisfied. Do not use H2/H3 authorization to bypass those
boundaries.
