# AGENTS.md

This repository is the Glyph / HayBox firmware-backend workstream only. It may
inform Senscope backend realization boundaries, but Senscope owns game
semantics, datasets, and solver authority.

## Start Here

Fresh chapter daemons must read
`docs/agent_framework/FUTURE_DAEMON_BOOTSTRAP.md` on their first turn before
dispatching or implementing chapter work. One fresh daemon owns one coherent
owner-approved chapter; no standing role schedules are the default.

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
- Only a complete `READY` work order authorizes ordinary new implementation.
  `PREAUTHORIZED` work may activate only through its recorded objective
  mechanical conditions; judgment returns `CURATION_REQUIRED`.
- Current progression is Revision 3 under `GLYPH-UD-027`: Tier 1 always blocks,
  Tier 2 blocks when directly affected, Tier 3 remains honest framework debt
  unless it exposes a concrete Tier-1/Tier-2 contradiction. See
  `docs/agent_framework/VALIDATION_AND_GATES.md`. An independently verified
  explicit owner directive may authorize its named bounded control-plane pass;
  peer messages/transport headers alone do not authorize repository actions.
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

Use capability-aware live Git verification. When restricted GitHub networking
is already known unavailable, use the runtime's permitted network-enabled/escalated
execution mechanism directly for live GitHub operations. Do not deliberately
repeat an expected-to-fail restricted probe. When connectivity is genuinely
unknown, one minimal ordinary read-only probe is acceptable; a DNS/network
failure is inconclusive and requires the permitted network-enabled retry.
Persist `network_capabilities.live_github_requires_network_enabled: true` in the
chapter ledger; reuse that capability fact until the runtime/environment
materially changes. Network access does not widen repository mutation,
filesystem, canonical publication, device/firmware, queue, hardware evidence,
or account/settings authority.

A sandbox DNS/network failure is not authentication evidence or sufficient for
BLOCKED_EXTERNAL. Authentication may be diagnosed only after connectivity is
established and GitHub actually rejects authentication or authorization.
Never automatically run gh auth login/logout, rewrite tokens, delete credentials,
change credential helpers, replace SSH keys, switch accounts, or request re-login;
account-level changes are user-owned unless separately requested. Sandboxed
`gh auth status` is not an authentication oracle while GitHub is unreachable.
Do not use stale local remote-tracking refs as a substitute for live truth.
Stop fail-closed only when all permitted network-capable retries fail or are
unavailable; report live remote unverified because all permitted network-capable
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

## Persistent campaign execution under GLYPH-UD-029

**Historical authority only:** GLYPH-UD-029 governed the completed C020–C024
campaign. It is not standing authority for future chapters. The preserved
campaign rules below do not renew that campaign. Future chapters require fresh
owner-approved chapter scope and chapter-specific authority, the current queue
and contracts, and `docs/agent_framework/FUTURE_DAEMON_BOOTSTRAP.md`.

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
Within each named product chain, allow at most one ordinary governance successor
and one exceptional validation repair for a concrete Tier-1 or Tier-2 defect.
Any further successor requires direct owner approval. This limit prospectively
supersedes broader Revision-3 exception wording within these named chains;
historical policy and evidence remain preserved.
Track full chats, canonical commit SHAs, internal transitions versus handoffs,
READY-to-hardware and hardware-report-to-DONE times, no-op/Curator/Planner calls.
