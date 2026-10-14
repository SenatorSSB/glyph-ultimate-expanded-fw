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

- `ed49c64ebdf9c4f13167126d726838b2de24fdd9` repairs a command-scoped
  Configurator lifecycle defect: ProfileStore's `ReadPacket()` owns the
  PacketIO advance after EOP, so `SendReport()` must return after that handler
  rather than advance a second time. The upgraded deterministic host proof
  compiles the real backend, production PacketIO COBS, generated Nanopb, and
  real injected-storage ProfileStore. It proves three consecutive LIST frames
  all receive valid two-entry responses, while a test-only reconstruction of
  the original duplicate advance drops the second request. It also proves the
  five-second partial-frame timeout, required delimiter resynchronization,
  stable later STATUS recovery, and behavioral 8192-byte cap rejection with
  no Config/ProfileStore mutation. This is host evidence, not hardware
  acceptance.
- The checked W5 head builds with `python3 -m platformio run -e glyph_mk6`;
  the observed build reported RAM `181636 / 262144` (69.3%) and flash
  `457340 / 1568768` (29.2%). These are continuation measurements, not final
  exact-candidate custody measurements.
- The earlier `40 02` field-8 observation remains unproven and is not evidence
  of a ProfileStore or Nanopb defect. The source-faithful full-stream proof
  supersedes it for this transport question; no protobuf repair was made on
  that observation.
- `3ca15f2f` corrects a separate v1 READ serialization defect discovered
  by the same real-stream harness: successful reads populated `response.profile`
  but omitted Nanopb's `has_profile`, so the encoded response lacked the
  profile payload. The current matrix drives STATUS, LIST, CREATE, READ,
  UPDATE, DUPLICATE, RENAME, REORDER, DELETE, SET_MODE_REFERENCE, and
  QUERY_TRANSACTION through one retained backend; it also checks malformed
  protocol rejection, missing-ID, stale-generation conflict, referenced-delete
  refusal, and subsequent STATUS continuity.
- The same W5 build's target ELF section report records `.data = 40260` and
  `.bss = 141376` bytes; PlatformIO reports total RAM `181636 / 262144` and
  program flash `457340 / 1568768`. The compiler warns of `2632` bytes stack
  use in `DecodeDirectoryCommit`, `2384` in `HandleProfileStore`, `2216` in
  `ProfileStore::Duplicate`, `1240` in the Senscope self-test, and a larger
  existing `31464` estimate in `setup`; target stack acceptance remains a
  review/hardware concern, not resolved by this measurement.
- Frozen filesystem accounting uses 4128-byte maximum record envelopes,
  2620-byte directory roots, and a 16384-byte reserve in the nominal 524288
  byte partition. The conservative accounting leaves 420104, 370568, and
  238472 bytes after 20, 32, and 64 records respectively; its uncapped
  arithmetic bound is 121 records, while the frozen directory maximum remains
  64. These calculations exclude target allocator geometry and are not a
  target-device capacity claim.

## Hardware handoff pending owner (2026-10-13)

- The immutable reviewed firmware candidate is
  `1a753e08f3c989a0743180183f18d6aa9e3859e0` (tree
  `ebeb1faab97666d05f93f851d036f41fbb2469df`, parent
  `e90b36e68c8156b6113220b3381ba0057e2e4144`) from canonical base and
  merge-base `6b73a7c507f35c111745c6bdd341618b490cbdcd`.
- Fresh independent review PASS found no blocking defect. The exact build used
  `python3 -m platformio run -e glyph_mk6`, measured RAM `181636 / 262144`
  (69.3%) and flash `457340 / 1568768` (29.2%), and produced a 939008-byte
  UF2 with SHA-256
  `536578e22de4be8652ff39d36c75bfd570bb55899f2a302b8c245c02e81672ff`.
- Reviewed bytes are readable in primary custody at
  `local_backups/hardware-artifacts/1a753e08f3c989a0743180183f18d6aa9e3859e0/536578e22de4be8652ff39d36c75bfd570bb55899f2a302b8c245c02e81672ff/firmware.uf2`.
  No hardware action has occurred and no canonical merge has occurred. This
  source-free handoff record does not redefine the tested firmware candidate.

## Real-predecessor compatibility repair (2026-10-14)

- Candidate `1a753e08f3c989a0743180183f18d6aa9e3859e0` and UF2
  `536578e22de4be8652ff39d36c75bfd570bb55899f2a302b8c245c02e81672ff`
  are permanently recorded as **HARDWARE_FAIL — REAL_PREDECESSOR_CONFIG_REJECTED
  BEFORE_MIGRATION**. The owner observed `Stored Config rejected`, `Recovery
  required`, and `Operation refused` immediately after flashing; no store
  command, Config write, migration, or reset followed that observation.
- The byte-exact physical predecessor fixture is
  `local_backups/hardware-tests/multi-profile-store-20261013/preflash-config-backup.json`:
  4201 bytes after base64 decoding, SHA-256
  `f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480`.
  The source-faithful host replay decodes it completely and passes extents and
  generic semantics. Its first failure on the frozen base validation route is
  Glyph RGB target validation: historical zero-color `BTN_UNSPECIFIED` entries
  are not physical targets.
- The repair admits only those exact zero-color legacy RGB no-op entries while
  `ultimate_profile_store_format == 0`; normal compact Configs remain strict.
  Color-bearing unspecified entries still reject, and the helper removes only
  the admitted no-ops when a legacy Config is actually converted to compact
  form. The captured Config contains zero embedded Ultimate profiles, so no
  ProfileStore import or compact successor is applicable to that exact input;
  the compatibility proof is normal legacy boot admission, not an invented
  migration transition.

## First ProfileStore CREATE repair (2026-10-14)

- Candidate `f76ece54478d7ce0364bd62cc8a0dc6406746e12` and UF2
  `c67dae5646c294ed400fa4f517271c415e06ff445d420980c2cf57933a537350`
  are permanently recorded as **HARDWARE_FAIL — FIRST_PROFILESTORE_CREATE_IO_FAILURE**.
  On the same accepted 4201-byte predecessor state, normal boot, Menu and RT2
  Configurator access, GET_DEVICE_INFO, GET_CONFIG, ProfileStore STATUS, and
  ProfileStore LIST passed. The first valid CREATE returned
  `PROFILE_STORE_IO_FAILURE`; no retry or later mutation occurred.
- The failure is reproduced by real `ProfileStore::Create()` when a storage
  double models LittleFS strict removal of the first, absent immutable-record
  destination. The old atomic publication path treated that false return as an
  I/O failure before directory publication. The adapter contract is now
  explicit: `Remove` ensures a path is absent, succeeds when it was already
  absent, and still reports an actual failure to remove an existing path.
- The repaired atomic layer checks destination existence before removal. Its
  tests cover a strict absent destination, successful replacement, real
  existing-destination remove failure, temporary write/read verification
  failures, and rename interruption. F2 is not reusable for another mutation
  attempt; its passing read-only observations remain valid evidence.

## First CREATE diagnostic follow-up (2026-10-15)

- Candidate `8e088b5d1c2629bb225f990128628bfa419e6c7d` and UF2
  `7e18bd1cff7dfb8ff267c0a2b5bdecc99b10c84b21c3ee2a3cc5c8910f9c1827`
  are permanently recorded as **HARDWARE_FAIL — FIRST_PROFILESTORE_CREATE_IO_FAILURE**.
  Exact flash, normal boot, Menu Configurator, and empty ProfileStore
  STATUS/LIST passed; the single first CREATE again returned
  `PROFILE_STORE_IO_FAILURE`, with no retry or later mutation.
- The absent-destination remove mismatch remains valid host-test fidelity and
  storage-contract hardening, but F3 proves it was not the complete physical
  root cause. The physical failure is now classified
  **FIRST_CREATE_PHYSICAL_IO_FAILURE — EXACT_STAGE_UNRESOLVED**.
- The next candidate is diagnostic-only: it reports an ephemeral exact record
  I/O stage through existing `ProfileStoreResponse.diagnostic` on an I/O
  failure. It changes neither persistent schema nor ProfileStore status
  vocabulary or publication ordering.
