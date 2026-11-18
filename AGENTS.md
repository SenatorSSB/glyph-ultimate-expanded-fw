# Coding-agent instructions

## Scope

This repository is the Glyph/HayBox firmware workstream. Senscope is a separate
product and owns its game semantics, datasets and solver authority.

Do not invent Glyph/HayBox firmware behavior, undocumented backend capabilities,
or Super Smash Bros. Ultimate gameplay semantics. Use source, current technical
docs, tests, fixtures and explicit user/domain statements as authority. Label
inference as inference and unknown behavior as unknown. Historical observations
are not proof of a root cause or a broader capability.

## Read first

Start ordinary coding work with:

- [Development](docs/DEVELOPMENT.md): build, validation and contribution rules.
- [Architecture](docs/ARCHITECTURE.md): system relationships and source owners.
- [Current state](docs/CURRENT_STATE.md): present qualification and non-claims.
- [Capabilities](docs/CAPABILITIES.md): implementation and product limits.

For native profile work, also read the [profile system](docs/PROFILE_SYSTEM.md)
and [profile authoring contract](profiles/README.md).
For runtime-sensitive work, respect the hard
[implementation boundary](docs/runtime_config/IMPLEMENTATION_BOUNDARY.md).
The accepted native Ultimate/ProfileStore lane does not authorize arbitrary
generic runtime configuration or new device operations.

An explicitly assigned public coding task supplies its bounded work scope;
resolve missing product, source or compatibility decisions with the user.

## Git and branch hygiene

Live-verify the current `origin/configurator` before starting and refresh it
before publication. Create a feature branch from the verified base in a clean
worktree. Inspect `git status` and `git diff --stat`, keep the diff bounded, and
preserve unrelated edits in other worktrees. Use ordinary reviewed commits and
normal pushes; integrate only within the task's explicit publication scope.

Do not force-push or run destructive Git operations (`git reset`, `git clean`,
`git stash`, `git revert`) unless explicitly authorized. Do not use stale local
remote-tracking refs as live truth.

Use a known permitted network-enabled mechanism when restricted networking
cannot reach GitHub. If connectivity is unknown, try a minimal read-only probe
and retry through the permitted network-enabled path after a network failure.
Network permission grants no other authority. A network failure is not
authentication proof; diagnose credentials only after GitHub is reachable and
rejects authentication or permissions. Never automatically log in/out of GitHub,
change credentials, tokens, credential helpers, SSH keys or accounts, or request
re-login because of a network failure. If all permitted network paths fail,
report live remote verification as unavailable and stop dependent publication.

## Build and validation

Canonical Mk6 build, from the repository root:

```sh
pio run -e glyph_mk6
```

Fallback:

```sh
./scripts/build-glyph-mk6-quiet.sh
```

Run focused tests first, then affected current validation. For documentation
changes, inspect navigation, links and source-backed claims. For checker changes,
exercise positive and negative controls and regenerate the checker census using
the existing generator. Follow DEVELOPMENT's validation commands and CI model;
allow the CI classifier to request a build for checker/tooling changes.

Report PASS, FAIL, TIMEOUT and SKIPPED accurately, with scope and failed checks.
TIMEOUT is not PASS. SKIPPED is not PASS. An incomplete aggregate or unavailable
dependency supplies no successful coverage. Investigate current validation
failures; preserve evidenced historical failures without relabeling them PASS.

## Change and evidence boundary

Use the [DEVELOPMENT evidence matrix](docs/DEVELOPMENT.md#change-classification-and-required-evidence)
for the change class and required checks rather than inferring gates from file
extensions alone. Documentation/checker-only work normally needs no hardware
when active firmware behavior and build inputs are unchanged.

Firmware behavior changes require build proof from the exact committed candidate
and exact hardware acceptance before canonical integration when hardware gating
applies. Build PASS is not hardware acceptance. Source implementation is not
physical qualification. Acceptance belongs to the exact candidate Git SHA,
exact tested artifact SHA-256 and recorded human test scope; a later rebuild or
CI artifact does not inherit that acceptance. Preserve accepted artifact identity.
Nunchuk remains NOT_TESTED unless the user explicitly reports a test. Root cause
remains unproven without direct evidence.

Do not expand runtime-loaded configuration, schemas, protocols, persistent
formats, backend writes or export semantics without explicit task authority and
source support. Maintain compatibility and refusal/preservation guarantees.

## Stop conditions

Stop and return to the supervisor/user when:

- Firmware behavior changes are required outside the explicitly assigned scope.
- A schema, protocol or persistent-format change is required outside that scope.
- Source authority, a substantive product decision or compatibility is ambiguous.
- Game semantics would need invention.
- Required hardware testing needs human execution or its evidence is missing.
- Device write or flashing is needed without specific explicit authorization.
- A current validation failure is not understood.
- Required private evidence is unavailable.

## Device safety

No firmware flashing, serial/device write, hidden device mutation, destructive
recovery or controller operation unless the user explicitly authorizes that
specific device action. Documentation and general implementation permission do
not supply device-operation authorization.

Manual hardware testing requires exact candidate/artifact identity and explicit
human execution where applicable. Never fabricate a test result or substitute a
successful build for a human hardware report.

## Documentation ownership

Use [DEVELOPMENT's canonical ownership table](docs/DEVELOPMENT.md#documentation-maintenance-policy).
Update current state in its canonical owner; do not prepend another dated status
dump. Keep implementation, product exposure and physical qualification distinct.
Retain exact evidence and its limitations without broadening acceptance claims.

## Legacy/internal material

Historical/internal campaign machinery from the development fork is not part of
the supported public workflow. Curated [history](docs/history/HISTORY.md) and
[evidence](docs/evidence/README.md) contain the durable public facts. Retained
internal records and their consistency checks are not retired by this contract.
