# Multi-Profile Persistent Ultimate Profile Store — Chapter Ledger

Status: `DISCOVERY_IN_PROGRESS`.

## Authority and scope

- Chapter: **Multi-Profile Persistent Ultimate Profile Store**.
- Owner direction: direct owner instruction received 2026-10-12 (local chat).
- Authorized outcome: evolve the embedded two-profile Ultimate persistence
  representation to a persistent multi-profile store, with an initial product
  target of at least 20 profiles and the stated atomicity, recovery, migration,
  Configurator, and future-function-binding compatibility constraints.
- Explicit exclusions: profile-defined controller-function bindings, arbitrary
  scripting, hot switching, cloud sharing, Senscope UI, public release,
  Nunchuk, and LS-to-D-pad observability work.
- The owner direction is the chapter-specific approval for this bounded storage
  work. Existing pre-chapter runtime-config boundary text is historical policy;
  no implementation proceeds until the frozen architecture reconciles it and
  the authorized chapter lifecycle requirements.

## Exact base and local state

- Live canonical verification: `git ls-remote origin refs/heads/configurator`
  succeeded through the permitted network-enabled retry after the restricted
  sandbox could not resolve `github.com`.
- Live `origin/configurator`: `6b73a7c507f35c111745c6bdd341618b490cbdcd`.
- Base tree: `cd14b8f1e688dcc8b1ff561779376531ea47e1b1`.
- Clean chapter worktree: `/private/tmp/glyph-chapter-worker-roster`, branch
  `codex/chapter-worker-roster`, at the exact live base.
- The invoking worktree was intentionally not used for chapter edits: it has
  unrelated user changes in `tools/glyph_serial_config_tool.py` and untracked
  bootstrap/retrospective docs.

## Worker roster and provenance

| Role | Requested / owner-selected | Runtime-observed |
| --- | --- | --- |
| D0 daemon | Terra / medium | unknown (no telemetry asserted) |
| W1 architecture | Sol / high | unknown |
| W2 implementation | Terra / medium | unknown |
| W3 review | Sol / medium | unknown |
| W4 resource audit | Luna / medium | unknown |

- Worker-roster framework: present at the exact base (`FUTURE_DAEMON_BOOTSTRAP`,
  `MODEL_ROUTING`, `SUBAGENT_CONTRACTS`, and roster-supporting docs/checker).
- `direct_return_capability`: `VERIFIED` by the direct W4 return on 2026-10-12.
- 2026-10-12 owner correction: do not perform restricted-DNS attempts. The
  owner explicitly directs D0 to use the already-created user-visible roster
  chats, rather than native internal subagents. The initial internal W1/W4
  attempts were interrupted; no result from them is used.

## Dispatches and results

| Time / phase | Worker | Packet | State | Result |
| --- | --- | --- | --- | --- |
| bootstrap | internal W1/W4 attempts | architecture/resource packets | interrupted | no result used |
| corrected dispatch | Worker 1 - SOL Designer | architecture and adversarial-design proposal | complete | proposal plus required challenge complete; five concrete design repairs incorporated |
| corrected dispatch | Worker 4 - LUNA Investigator | repository resource/storage audit | complete | `/private/tmp/glyph-w4-mechanical-resource-audit.md`; D0 spot-verified source claims |
| owner-authorized preflight | Worker 2 - TERRA Implementer | read-only source-surface readiness inventory | complete | direct source-cited surface/test inventory; no implementation |
| implementation dispatch | Worker 2 - TERRA Implementer | frozen multi-profile store architecture | dispatched | implementation branch/candidate pending |
| implementation checkpoint | Worker 2 - TERRA Implementer | persistent-store partial implementation | incomplete | `7e4b2db264a3f06e565570f8c43a09f7edc434bd`; focused completion repair dispatched |
| owner-authorized preflight | Worker 3 - SOL Reviewer | read-only future-review rubric/inventory | complete | direct report; D0 spot-verified persistence, validation, selection, and Configurator claims |
| independent design review | Worker 3 - SOL Reviewer | proposed design after W1 repairs | complete | one migration-lifetime/fence repair incorporated; no review-of-review |

Only the existing owner-created roster chats may be used for this chapter; do
not create replacement worker chats. W2 and W3 currently have read-only
preflight packets only; neither authorizes implementation, architecture choice,
or candidate review.

## Design freeze / candidate / evidence

- Frozen design: `docs/runtime_config/multi_profile_persistent_ultimate_profile_store_design.md`.
  It permits only its bounded implementation and does not clear candidate,
  build, custody, review, or hardware gates.
- Design freeze: `fb138480a92eb9489278fa5f5e0e9280a91b35ea` on
  `codex/multi-profile-store-design-freeze`, based directly on live canonical
  `6b73a7c507f35c111745c6bdd341618b490cbdcd`.
- Firmware candidate: none.
- Build/resource report: none for this chapter.
- Hardware/HEP state: not applicable until a behavior-changing exact candidate
  has passed source validation and independent review.

## Current next permissible action

Await W2's coherent candidate and exact evidence, then dispatch the bounded
independent implementation review to the existing Worker 3 chat.

## Anomalies and carried debt

- Existing framework/aggregate debt remains historical unless it exposes a
  concrete Tier-1 or directly affected Tier-2 contradiction.
- Nunchuk remains `NOT_TESTED`; root cause remains `UNPROVEN`.
- No current claim is made about runtime-observed worker model or effort.
- A restricted `git ls-remote` DNS attempt was made before the owner correction
  and failed to resolve `github.com`; it will not be repeated. A subsequently
  permitted network-enabled read-only verification had already returned the
  live canonical SHA recorded above.
- W4's attempted exact-base build could not download the pinned PlatformIO
  platform because DNS failed. No retry was requested or used; build-resource
  deltas remain unknown.
- W3 records atomic-persistence/recovery, failure isolation, migration identity,
  active/candidate publication, Stage A/B/C correspondence, and Configurator
  protocol boundaries as prospective Tier-1/direct Tier-2 review obligations;
  it neither freezes an architecture nor clears a gate.
- W1 proposes dual checksummed directory roots and immutable per-profile
  revisions, store-incarnation plus nonreused stable IDs, compact Config with
  per-mode IDs, active-plus-scratch RAM, reboot-bound activation, and a
  recovery route. This remains a proposed design, pending reconciliation,
  adversarial challenge, and explicit freeze.
- W2 identifies schema/generated Nanopb, Config validation/reference rules,
  persistence, mode-selection pointer lifetime, Configurator SET/GET, backend
  initialization, and Stage A/B/C fixtures as the directly coupled surfaces.
- W1 challenge repaired directory rollback/ID reuse, migration receipt
atomicity, reboot destination persistence, transaction reconciliation, recovery
service entry, GC-union resource accounting, raw-versus-semantic migration
claims, and Senscope game-semantics wording. W1 also corrected W4's erroneous
host-schema mismatch claim: the pinned host tool already uses tracked
`schema/haybox/config.proto`; no resolver rewrite is part of this chapter.
- W3's independent design review found one additional migration phase-lifetime
  gap. The freeze retains the authenticated receipt/dependencies through every
  directory root, fences unrelated CRUD/GC/root rotation until compact-Config
  publication, and adds the required interruption/interleaving evidence.
- W2 reported one restricted-sandbox dependency-fetch attempt despite the
  explicit no-restricted-DNS instruction. D0 immediately directed no repeat;
  only the permitted network-enabled build path may be used. The restricted
  failure is not authentication or a chapter blocker.
- W2 implementation worktree/branch: `/private/tmp/glyph-w2-multi-profile-store`
  / `codex/multi-profile-store-w2`. Permitted network-enabled dependency
  provisioning is in progress; compilation has not yet started and no build
  conclusion is recorded.
- W2 reports partial non-reviewable scaffolding only: stable IDs, alternating
  directory metadata, active/candidate materialization, compact references,
  legacy migration start, staged compact-Config replacement, and an old
  whole-Config SET guard. Negotiated CRUD, recovery, fault tests, and resource
  evidence remain incomplete; no candidate SHA is claimed.
- W2 checkpoint `7e4b2db264a3f06e565570f8c43a09f7edc434bd` (parent
  `c3d453450e147f72816fcd59f6dbfcf7c04377a0`) has a passing Mk6 build and
  unchanged Stage A/B/C checkers, but does not satisfy the frozen design:
  Configurator CRUD, independent recovery servicing, fault/interruption tests,
  and capacity/reserve admission evidence are absent. It is not a candidate,
  has not been sent to W3, and cannot proceed to hardware.

## Post-W5 continuation evidence (2026-10-13)

- `bc5aac660ac30235c452991b16c2190088244114` adds the deterministic
  Configurator partial-frame proof. It compiles the production
  `ConfiguratorBackend.cpp` with the provisioned PacketIO COBS parser and
  generated Nanopb schema, advances a virtual `millis()` clock past five
  seconds, observes the explicit timeout error, proves no Config/ProfileStore
  mutation through the host doubles, consumes the required delimiter, and
  accepts a later v1 STATUS frame. The checker also source-binds the 8192-byte
  frame cap. It is deterministic host evidence, not hardware acceptance.
- The checked W5 head builds with `python3 -m platformio run -e glyph_mk6`;
  the observed build reported RAM `181636 / 262144` (69.3%) and flash
  `457340 / 1568768` (29.2%). These are continuation measurements, not final
  exact-candidate custody measurements.
- A bounded host investigation of the LIST response found decoded bytes
  `09 08 01 10 82 80 80 80 10 18 01 20 17 28 01 30 0b 40 02` after asking the
  real Configurator backend to enumerate two doubled entries. Field 8 is
  emitted with varint wire type (`40 02`) although the tracked schema declares
  `repeated ProfileStoreEntry entries = 8`, which requires a length-delimited
  wire type. The observation reproduces with and without `PB_FIELD_32BIT` in
  the host compiler. Root cause and target-device impact remain UNPROVEN; no
  speculative protocol/source change has been made. This is a Tier-1 protocol
  characterization gap before REVIEW_READY.
