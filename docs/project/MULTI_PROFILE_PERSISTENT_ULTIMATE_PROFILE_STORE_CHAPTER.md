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

## First CREATE diagnostic instrumentation (2026-10-15)

- The diagnostic candidate records an ephemeral `ProfileStoreIoStage` for the
  first failed record-publication operation and maps it only on
  `PROFILE_STORE_IO_FAILURE` to the existing response `diagnostic` field:
  `record.encode_size`, `record.encode`, `record.temp_open_write`,
  `record.temp_write`, `record.temp_read`, `record.temp_size`,
  `record.verify`, `record.dest_remove`, or `record.rename`.
  It neither persists the stage nor changes record/write ordering.
- Diagnostics reset at the start of every decoded ProfileStore request. The
  retained real-stream regression first injects `record.temp_write`, then
  makes the separate `SET_MODE_REFERENCE` persistence save fail and requires
  its `PROFILE_STORE_IO_FAILURE` response to have an empty diagnostic. This
  prevents stale record-stage labels from crossing transaction boundaries.
- Real COBS/PacketIO/Nanopb/Configurator/ProfileStore host coverage injects
  each reported record failure and requires its exact diagnostic, while the
  empty-store CREATE success path requires an empty diagnostic followed by
  LIST and READ persistence. Fresh independent review passed the request-bound
  reset and this regression at `36d5991f85373081940a0b474a845bc8d8fb06ed`.

## First CREATE physical root cause and filename-limit repair (2026-10-15)

- F2 and F3 remain **HARDWARE_FAIL — FIRST_PROFILESTORE_CREATE_IO_FAILURE**:
  their first CREATE failure stage was unknown at the time. F3's absent-record
  removal hardening remains valid host/storage-contract work, but did not clear
  the physical blocker.
- F4 (`3e093348f9f4d7584375d60b293bb4b4c809919f`) is permanently recorded as
  **HARDWARE_FAIL — FIRST_PROFILESTORE_CREATE_IO_FAILURE** with exact
  diagnostic `record.temp_open_write`. The physical root cause is
  **PROFILE_STORE_RECORD_TEMP_FILENAME_EXCEEDS_PINNED_LITTLEFS_COMPONENT_LIMIT**.
  This repository pins Arduino-Pico 3.6.3. Its `LittleFS.h` defines
  `LFS_NAME_MAX` as 32 and `LittleFSImpl::pathValid()` rejects a component with
  length `>= LFS_NAME_MAX`; the older dismissal based on current framework
  master did not apply to this deployed pin.
- The immutable record path `/ultimate-%08lx-%08lx.bin` has a 30-character
  basename. F4 constructed its temporary record by appending `.tmp`, producing
  a 34-character `.bin.tmp` basename that the pinned wrapper rejects before
  opening. The repair retains the destination and instead writes temporary
  records as `/ultimate-%08lx-%08lx.tmp`, also 30 characters.
- `ProfileStorePaths.hpp` now owns the deployed maximum component length (31),
  compile-time checks for record and directory/root filenames, and the sole
  production formatting functions. Real-stream host coverage models the
  Arduino-Pico 3.6.3 component rule, reconstructs F4's old suffix in a
  test-only mutation (requiring `record.temp_open_write`), and proves repaired
  CREATE/reboot plus `ImportLegacy`/compact migration/reload with strict path
  validation. IDs/revisions at `UINT32_MAX` and both directory slots are
  asserted within the project bound.

## Directory-root publication diagnostic follow-up (2026-10-15)

- F5 (`0a32eb7696cbc5b084332c442bbf5868f15b4173`) is recorded as
  **HARDWARE_FAIL — PROFILE_STORE_DIRECTORY_ROOT_PUBLICATION_FAILURE —
  EXACT_STAGE_UNRESOLVED**. Its one CREATE returned `COMMIT_UNKNOWN` with ID
  1/revision 1. After the single permitted reboot, STATUS was OK at generation
  0, LIST was empty, and the original transaction token returned NOT_FOUND.
  This physically clears immutable record publication and establishes that the
  new directory root was not authoritative; the possible ID1 record is a
  non-authoritative orphan and is not manually cleaned up.
- Directory publication now uses the same atomic primitive with an explicit
  publication kind. Low-level storage outcomes are generic and are mapped at
  the caller to either `record.*` or `directory.*`, preventing a directory
  failure from being mislabelled as a record failure. Directory diagnostics are
  ephemeral and include encode, temporary open/write/read/size, verification,
  inactive-root removal, rename, and decoded-generation mismatch. They are
  reported for both IO_FAILURE and COMMIT_UNKNOWN while retaining the original
  status vocabulary.
- The strict real-stream harness injects each filesystem directory stage after
  record publication succeeds. Every injected CREATE returns COMMIT_UNKNOWN
  with ID1/revision1 and its exact `directory.*` diagnostic; reboot leaves the
  authoritative store at generation 0 with empty LIST and no committed query.

## Directory callback stack repair qualification (2026-10-15)

- F6 (`da0618ef47242d049948187ea00e6fb961617ef5`) remains
  **HARDWARE_FAIL — DIRECTORY_PUBLICATION_RUNTIME_HANG**. Its CREATE produced
  no response, the endpoint remained enumerated but did not answer one bounded
  `GET_DEVICE_INFO`, and a subsequent power cycle recovered an authoritative
  generation-0 empty store. That is correlation evidence, not a claim of a
  hardware-proven stack-overflow root cause.
- The repaired callback passes the already-verified atomic-commit byte buffer
  directly to `DecodeDirectory`; it no longer makes the old 2620-byte automatic
  copy. The pinned Arduino-Pico 3.6.3 ARM compiler (`arm-none-eabi-g++`,
  Cortex-M0+, O3) reports 2640 bytes for a source-reconstructed F6 callback
  and 8 bytes for the direct-buffer callback. The checked target ELF contains
  the framework's two default 0x800-byte stack reservations; its source has
  `core1_separate_stack` weak-defaulted false and takes the ordinary multicore
  launch path. The 128-byte callback gate therefore leaves 1920 bytes against
  the observed 2048-byte reservation.
- `check_glyph_profile_store_directory_stack.py` binds the production callback
  shape to that compiler gate and fails if the F6-sized local copy returns.
  `check_glyph_profile_store_directory_decoder.py` runs the current direct
  decoder and a source-reconstructed old copy decoder through the same corpus:
  valid normal and 64-entry roots, bad magic/version/count/CRC/incarnation,
  high-water inconsistency, zero ID/revision, ID above high-water, and duplicate
  IDs. No directory wire format or atomic publication ordering changed.
- The real Configurator/ProfileStore harness additionally rejects delimiter
  overrun and raw-zero COBS chunks (including `02 00`), establishes the
  production 5000 ms inactivity boundary, asserts Config/storage/count/
  generation/save-count nonmutation, then proves delimiter resynchronization,
  STATUS recovery, the 8192-byte cap, and a 30-second external host timeout.

## Complete CREATE diagnosis and diagnostic qualification (2026-10-15)

The owner's direct complete-path repair request supersedes the narrow callback
investigation. Parent83f526b8's one CREATE timed out; no post-timeout probe,
reboot or mutation occurred, so its later state remains UNKNOWN. The direct
callback repair stays. Scope remains the existing store; canonical is not merged.

Branch `codex/multi-profile-store-create-path-repair` repairs cumulative handler,
DUPLICATE and startup automatic frames, exact temporary readback equality,
bounded ProfileStore TX/recovery framing, and direct CREATE cached-token replay.
The physical root cause remains UNPROVEN. The owner has no SWD probe; bounded
watchdog stage retention therefore provides the next diagnostic information.
After timeout reset, transport-only read-only recovery reports the stage before
filesystem access. No flash logging or framework/core1 lockout bypass is added.

See `docs/runtime_config/profile_store_create_path_diagnosis.md` and its linked
independent flash analysis for source tables, falsification, stack limits,
validation scope and the one-CREATE hardware packet. Source commit must receive
fresh independent review and exact committed build/custody before hardware
handoff. Final candidate SHA/build/UF2 receipt is stored beside the preserved UF2;
this ledger does not fabricate those future identities or physical acceptance.

Network capability: live GitHub requires permitted network-enabled execution;
ordinary DNS failed, permitted retry verified canonical6b73a7c and parent83f526b8.
Native internal specialists used; fresh review separate. No full user chats,
Planner or Curator calls, canonical commits, hardware operations or acceptance.
Nunchuk remains NOT_TESTED. Full global stack bound and physical cause UNKNOWN.

## Production finalization and accepted hardware lineage (2026-10-15)

The direct owner production-finalization request authorizes the bounded repair
of `SET_MODE_REFERENCE_PERSISTS_TRANSIENT_RUNTIME_SELECTION_STATE`, retirement
of CREATE-only diagnostics, affected regressions, fresh independent review and
exact committed production handoff. No canonical merge or strict DONE yet.

Owner reports exact4ac255eb first CREATE/persistence/payload PASS, non-reference
CRUD/reboot PASS, and migration/reference persistence PASS within the PARTIAL
lifecycle result. Final store generation8 contains ID1 rev2 `CRUD Primary` rank20,
ID3 rev1 `Migrated 1` rank0, ID4 rev1 `Migrated 2` rank1, and deleted ID2 absent.
The6248-byte fixture migrated generation6→8 without ID2 reuse; compact Config
format1 has zero embedded profiles, mode1→ID3 and mode2→ID4; payload equality,
no migration replay, reference3→4 persistence, referenced-delete refusal and
reference4→3 restore passed. Runtime-B physical discriminator remains
`NOT_TESTED — PHYSICAL_RUNTIME_OBSERVER_UNAVAILABLE`; source activation is not
physical-output evidence. PARTIAL does not mean migration failed.

Reference SET now uses a checked durable candidate and fresh durable-generation
fence, edits only target reference/legacy-index fields and leaves live Config
unchanged. DELETE protects live and next-boot references. Compact save retains
a sole prior recovery anchor and treats verified-file publication as success.
The CREATE-only watchdog/stage/recovery probe is retired; normal RT2 recovery
and all source-proven CREATE production fixes remain. Historical diagnostic
reports/artifacts are preserved. See
[production finalization](../runtime_config/profile_store_production_finalization.md)
for the complete mutation audit, accepted hardware rows, gate assessment, test
scope, failure boundaries and minimal new exact-candidate hardware packet.

Live canonical6b73a7c was verified through permitted network-enabled reads;
ordinary DNS remains unavailable. New source needs its own exact artifact
hardware acceptance. Frozen target geometry/interruption requirements are not
silently waived; no strict DONE or aggregate PASS is inferred. Nunchuk remains
NOT_TESTED. Native source/test workers and fresh independent reviewer are used;
no new user chats, Planner/Curator, device actions or canonical commits.

Fresh production review also found a concrete frozen root-recovery violation:
corrupting generation3 allowed writable generation2 fallback and ID3 reuse.
The bounded finalization now fences damaged/missing-companion fallback, invalid
roots and root conflicts, clears stale RAM on reload, and retains only safe
read-only inspection. Exact source counterexamples and regressions prevent ID
reuse; no automatic repair, orphan activation or format change. This is a
blocking identity-safety fix, not historical framework debt.
