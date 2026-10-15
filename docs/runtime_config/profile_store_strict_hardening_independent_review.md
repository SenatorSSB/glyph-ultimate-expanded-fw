# Fresh independent strict-hardening review

Date: 2026-10-16. Base: `04d7521fbdaeb313c1fe768a992a6c35847b68bf`.
Reviewed worktree: `/private/tmp/glyph-multi-profile-directory-stack-repair`,
branch `codex/multi-profile-store-strict-hardening`.

**Source-side review PASS, subject to exact committed source/build/resource
binding. B10 and actual physical resource acceptance remain STILL BLOCKED.**
This is readiness for the owner's bounded hardware handoff, not strict chapter
DONE, controller acceptance, canonical merge approval, or a final artifact
identity. The final committed build and external custody/resource receipt must
bind the reviewed source. No replacement hardware evidence is inferred from
`f7ba82d4` or the historical F1–F6 observations.

The reviewer is separate from implementation, read the direct owner request,
frozen design, original B1–B10 review, chapter ledger, production finalization,
and current hardening design/protocol/storage/resource supplements. The owner
explicitly requests a fresh independent reviewer. This reviewer modified only
this new review document; independent temporary harnesses lived outside the
repository. No Git mutation, device operation, flashing, reset, or merge was
performed by the reviewer. The requested review routing was Sol/high; no
unsupported runtime model telemetry claim is made.

## Disposition matrix

`CLOSED` below means the original source-side defect is closed with direct
source and independently executed evidence. It does not relabel the new
firmware as hardware-passed. Physical acceptance is collected under B10 and
the B9 measurements, with exact source SHA and UF2 SHA-256. The exact committed
build/resource/custody binding remains a mechanical integration prerequisite.

| Blocker | Disposition | Direct repair and independently checked evidence |
| --- | --- | --- |
| B1 capacity/admission/GC | **CLOSED — source side** | `CheckedStorage::Capacity` uses the existing mounted `lfs_config` and checked `lfs_fs_size`. `ProfileStore::Capacity`, `Admit`, `Protected`, `LoadProtectedRoot`, and `CollectGarbage` charge both-root revision union, migration dependencies, exact active revision, control/roots, retained old roots, Config/source files, staging, metadata and 16,384-byte reserve. Real production mounted adapter on pinned LittleFS admits 20 representative profiles: total524288, used110592, free413696, protected143360, staging45056, representative admission32. Strict suite passes reserve refusal for CREATE/UPDATE/DUPLICATE, protected previous/deleted revision behavior and each of six GC removal boundaries before/after failure, plus retry. Frozen count-only implementation is detected by the actual-old-source negative control. Actual target geometry remains B10. |
| B2 checked persistence | **CLOSED — source side** | `HAL/pico/src/core/CheckedStorage.cpp` accesses the existing pinned LittleFS mount through declaring-base member pointers, checks native file/metadata operations, and preserves its flash/core callbacks. ProfileStore `Publish` independently verifies exact staged bytes; `Persistence::SaveConfig` checks sync/close and independently compares a second encode before publication. Mutating metadata uncertainty is explicit and fenced. Production primitive tests pass 54 faults against pinned LittleFS, including four old unchecked negative controls and real failing sync callback. Current production Persistence passes37 cases with ASAN/UBSAN, including lost-ack exact resolution, unresolved fence, interrupted rotation, immutable snapshot and reserve preflight. No physical power-loss claim is made. |
| B3 chord hot switching | **CLOSED — source side** | `select_mode` dispatches a latched destination request instead of calling `set_mode`. `persist_mode_destination` validates and generation-fences the durable destination before reset; `consume_committed_mode_destination` accepts only a matching checked durable destination and consumes scratch. Failure/uncertainty does not reset or alter active profile. Actual setup/backend/mode-selection tests pass same/different destination, failed/unknown save, non-Ultimate, held-chord and both recovery entry routes. Old immediate activation is a negative control. Target reset/held-chord rows remain required. |
| B4 request identity/replay/uncertainty | **CLOSED — source side after review repair** | Firmware SHA-256 covers the documented semantic request domain and full decoded fields with independent full uint64 token. Backend checks both durable store and Config-reference receipts before stale generation fences; monotonic protocol2 admission rejects retired tokens and v1 mutations fail closed. Config reference result is part of checked atomic Config publication. Store uncertainty rereads control/roots; Config uncertainty rereads actual persistent Config. Accepted pending intent now retains token/digest and `Aborted` result in its identity-only checkpoint. Independent strict engine24 cases and real stream protocol tests pass exact replay, changed request conflict, eviction, reset/query, every mutation and reference receipt behavior. See finding chronology below. |
| B5 root loss/ID reuse | **CLOSED — source side** | Bootstrap/ready/pending control phases and exact root checkpoint bind generation, incarnation and high water. Lost companion, invalid/conflicting roots and pair rollback fail read-only; accepted pending allocation reserves its ID through abort. Firmware-owned Config root-format2 prevents total v2 loss from reviving retained v1 roots. Strict tests reproduce the precise lost-gen2/lone-gen1 sequence, root absence/conflicts, older-pair rollback, repeated reboot and complete v2 erasure with compact marker. Actual f7 source exhibits the old ID reuse negative. Whole-image rollback including every authority is explicitly outside this local monotonic guarantee. |
| B6 authenticated/bounded migration | **CLOSED — source side** | `CaptureLegacySource` retains and hashes exact checked persisted input; `ReadLegacyProfile` streams individual bodies. `ImportLegacyStream` binds source/version/incarnation/import IDs/revisions/payload identities and compact successor digest; retry validates the same source and dependencies. `CompleteMigration` validates source, receipt, imported records, compact mapping/incarnation before releasing the fence. Count/high-water/admission preflight precedes array growth. Strict/Persistence/lifecycle tests pass exact A/B payloads, changed source, corrupt/missing dependency,63/64 entries, overflow, reserve, every record/root/completion publication fault, compact reset/retry and wrong successor. `ReadRange` now also checks exact read count. Old mismatched retry is detected. |
| B7 minimal recovery | **CLOSED — source side** | `initialize_recovery` installs validator, loads usable Config and calls inspection-only `BeginRecovery`; actual startup routes manualRT2 and automatic Config/storage rejection into bounded headless Configurator. MB1 retains priority. Backend reports layered storage/Config/root/migration/uncertainty/read-only flags and refuses unsafe mutation in recovery. Actual setup-route tests pass manual/automatic/unavailable/MB1 and old skipped-init/dead-refusal negatives. Physical automatic route remains honestly NOT_TESTED unless the hardware packet can exercise it safely. |
| B8 names/health | **CLOSED — source side** |33-byte storage retains32 UTF-8 bytes plus terminator. `ProfileStoreNameValid` rejects excess/malformed input. V2 explicit portable metadata encoding and protocol retain full names; LIST reads metadata only. Explicit `Health` distinguishes healthy/prior/missing/corrupt/unsupported without activation. Strict tests pass0/1/17/18/31/32 bytes, maximum rename/duplicate/reboot, unsupported/current/prior corruption and missing records. Old17-byte truncation is detected by actual-old-source control. |
| B9 resource sufficiency | **CLOSED — source prerequisites; physical measurements pending** | Actual ARM compilation, ABI/map/frame collector and candidate-only stack/heap instrumentation exist and pass independent checks. Current CREATE checked-open chain measured2792 bytes against the4096-byte scratch-bank envelope, with1304 bytes before unmodeled paths; SDK2048 reservation is not treated as a runtime maximum. Native Stage tests measure Config31432/Profile2152; preliminary ARM collection measures Config31312/Profile2152, directory3848, ProfileStore4348 and protocol objects/buffers explicitly. Preliminary link values are engineering evidence only. Exact committed ELF/map/ABI/frame report must replace preliminary identity in the external handoff, and owner watermark/allocator-peak rows must establish actual physical margins. No whole-target formal bound or physical peak is claimed. |
| B10 target geometry/interruption | **STILL BLOCKED — physical acceptance; packet ready** | `profile_store_strict_hardening_hardware_packet.md` specifies exact artifact/source, baseline preservation, upgrade, target geometry/reserve/20 profiles, bounded full/admission attempts, one-shot operation-specific injected boundaries, recovery, transaction replay and resource observations. Fault controls require conspicuous candidate capability and reject production-disabled arming. CLI transmits at most one requested operation and retains exact request custody for explicit replay. No physical tests were performed. Count FULL, host NOR faults and injected target faults must not be called physical power-cut evidence. |

## Aggressive persistent-format compatibility check

The explicit deployed v1 reader remains separate from v2. The exact logical
fixture uses old generation7 pending migration and generation8 completed
migration, incarnation7, high-water4, ID1 revision2 with retained revision1,
ID3/ID4 revision1, deletedID2, names/ranks and mode1→3/mode2→4. `Begin` chooses
generation8, validates records/dependencies and publishes bootstrap control,
both v2 roots, then ready checkpoint. It preserves all old root/record bytes;
no record payload re-encoding or ID/reference rewrite is needed for upgrade.
`PrepareCompact` adds root-format2/owned provenance metadata. Reboot preserves
generation8 and the next accepted allocation is ID5. Interruption before/after
each bootstrap/root rename resumes mechanically without writable downgrade.
A highest pending unauthenticated v1 migration or lone v1 root remains read-only.

Completed old migration provenance version3 hashes the old root and retained
import dependencies. This validates preserved existing state; it does not
retroactively claim the old raw legacy migration was authenticated. New
migration version2 binds the exact source snapshot and canonical successor.
Control/Config format evidence survives the tested loss/rollback scenarios;
an arbitrary older restoration of Config, both roots and control together
needs external monotonic authority and is not a supported normal recovery.

## Findings discovered and repaired during this review

1. **Accepted abort identity was discarded.** An independent temporary
   ASAN/UBSAN harness seeded a store, injected fail-before next-root rename for
   token10/original request, observed COMMIT_UNKNOWN, reconciled QUERY to
   NOT_FOUND, then executed changed payload/name/rank with token10 as ID3.
   This violated the frozen accepted-token identity requirement. The repair
   keeps accepted token/digest/result with `Status::Aborted` in the durable
   identity-only checkpoint. Wire status11 is additive TRANSACTION_ABORTED.
   Current strict tests pass exact aborted replay without mutation, changed
   request conflict before/after reboot and after receipt eviction. An explicit
   discarded-receipt negative reconstruction reproduces the old defect.
   Migration maintenance retains its preceding successful receipt because it
   did not accept a new client token.
2. **Hardware replay procedure was locally blocked by the CLI.** Normal
   mutation preflight required token above current high water and matching
   current generation, so it could never transmit an exact old request. The
   explicit replay action now verifies retained original bytes/hash/decoded
   fields, same incarnation and candidate/protocol capability while preserving
   old token/expectations. Normal mutation custody is exclusively created and
   fsynced before first transmit. Independent offline checks prove exact byte
   replay with stale generation/high water and rejection of wrong incarnation,
   changed decoded fields and incorrect payload hash. No serial port was opened.
3. **Decoder fixture retained an obsolete invalid-status boundary.** After
   adding valid internal `Aborted = 12`, the final integration rerun exposed a
   fixture that still treated `Referenced + 1` (also12) as invalid. Production
   correctly accepted the supported status. The fixture now explicitly accepts
   `Aborted` and rejects `Aborted + 1` (13). The reviewer inspected the actual
   decoder's upper-bound check and independently reran both direct and F6-copy
   variants with ASAN/UBSAN: PASS. No production bytes/fingerprints changed.
   The final-suite failure was a stale expectation, not a decoder defect; this
   focused correction does not erase the initial failure chronology.
4. **Exact legacy range reads lacked a short-read check.** Production
   `ReadRange` now requires checked read byte count equal to the requested
   range, plus checked seek/close. This is defensive exact-input hardening;
   the reviewer did not claim an ordinary concurrent source-file race.

Durable transaction acceptance has a precise boundary. A persisted pending
intent is an accepted identity even if its mutation later aborts, hence the
mandatory retained aborted receipt. Malformed/validation-rejected requests and
proved failures before durable intent never acquired directory authority or
allocated a stable ID; their token remains unused and QUERY may return NOT_FOUND.
Likewise a Config-reference publication proved uncommitted has no committed
Config receipt. This does not relax successful/accepted token replay rules or
permit an uncertain publication to admit another mutation before reconciliation.

## Independently executed validation

All14 ProfileStore/checked-storage/resource checkers pass: atomic commit,
checked storage, Config persistence, CREATE stack, directory decoder, directory
stack, pinned LittleFS, migration lifecycle, request identity, selection/recovery,
strict host, strict protocol, retained timeout/resynchronization, and resource
diagnostics. Strict host and checked storage compile production translation
units with ASAN/UBSAN. Config persistence and retained backend were also rerun
with `GLYPH_PROFILE_STORE_SANITIZERS=1`. Strict protocol was rerun after the
aborted-identity repair with candidate fault controls enabled and disabled.

Unchanged Stage A, B and C suites and the exact real-predecessor compatibility
suite pass independently. Stage C compares1,222,420 final outputs against its
frozen legacy oracle. The accepted6248-byte A/B payload and4201-byte physical
predecessor remain distinct fixtures. The old aggregate SetConfig lineage scope
guard is retained as a documented scope failure, not an aggregate PASS.
No frozen oracle was regenerated from changed production semantics.

Scope inspection finds only the authorized persistence/capacity/transaction,
selection/recovery, metadata/health, protocol and temporary resource/fault
acceptance surfaces. No controller-function bindings, macros/turbo/scripts,
Senscope UI or game-semantic ownership, vendor-private storage dependency,
factory reset, automatic flash or unrelated firmware feature is introduced.
Diagnostics/fault controls are conspicuous in the candidate; their removal or
explicit final-production acceptance needs a separately reviewed exact
snapshot. Runtime-B remains NOT_TESTED — PHYSICAL_RUNTIME_OBSERVER_UNAVAILABLE,
non-blocking observer debt. Nunchuk remains NOT_TESTED; root cause of historical
physical hangs remains UNPROVEN.

## Remaining exact-candidate gates

The integration role must bind the reviewed production bytes to the committed
candidate, verify live canonical/remote identity, build exact committed
`pio run -e glyph_mk6`, collect current exact ELF/map/ABI/frame evidence and
retain content-addressed UF2 custody with independent reread/hash. Preliminary
builds/resources are not that final receipt. Source changes after this review
require focused re-review; a build alone does not close physical requirements.

The owner then supplies exact-SHA/exact-UF2 B9/B10 evidence under the bounded
packet. Preserve useful IDs1/3/4 and monotonic identity history; logical exports
cannot restore original IDs, and an emergency whole-image backup is not an
ordinary rollback authorization after new IDs are issued. Stop on unexpected
identity/payload/reference change, unresolved outcome, invalid geometry,
implausible/zero stack margin or exhausted heap, and report each unperformed
row NOT_TESTED. Canonical integration and strict DONE remain prohibited before
the required exact physical acceptance and its review.

## Reviewed production-byte fingerprint

These SHA-256 values identify the source-side review point, not a Git commit or
hardware artifact. The final integration receipt must check equality or obtain
focused review for a changed path. This document is excluded from its own
fingerprint.

| Path | SHA-256 |
| --- | --- |
| `HAL/pico/src/core/ProfileStore.cpp` | `55afd509856d2f68d96cfc4d292d2623696209ce9f7df5cf27853860541c69db` |
| `HAL/pico/src/core/Persistence.cpp` | `94b442b830f4a7a44c6bb0b56d50d3898d472b7ef94357b0a261f1c9e71871d0` |
| `HAL/pico/src/core/CheckedStorage.cpp` | `8e60e1ae9acbb47dfa332aafa47c8433392c933ca8d92ee2de581912fb3b2420` |
| `HAL/pico/src/core/ResourceDiagnostics.cpp` | `99628d38b1adbc44aa2084ccded843e050e453341291de29c0c34ef03df418da` |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp` | `35446cf8a35593f7198c13248d8569aa5e162064b13ad3af4a03a8c63258726d` |
| `HAL/pico/src/comms/backend_init.cpp` | `057e4eb529fd9d9fbe94872ee73f0a64799ce77cdfc7f32c367775c9293c27d0` |
| `config/glyph/common/src/config.cpp` | `adbeb24949bee4025c1abaa884814c4f3cde35c1bfea03fb1fbe144c9a900ee3` |
| `src/core/mode_selection.cpp` | `857d2a147ae45908a13cdf7dc7f3892dfdfc9322f23d692156a1508b70bcb872` |
| `include/core/ProfileStore.hpp` | `2fc0638819d5f3ae07b9c0e87ab1e2215479622058576c86f8b5afebbbda93d4` |
| `include/core/ProfileStoreStorage.hpp` | `c68040e69214eb13404f6945caa6d35f4069809797ebf77c0ff7186169050efc` |
| `include/core/ProfileStoreRequestIdentity.hpp` | `a0ee0e8d0d6d2c9f40404af3643a671ed405fd640a00b681b0664f8f663c3bd9` |
| `include/core/ProfileStoreTransaction.hpp` | `af647f116534fac3f10c473d11c8c93347d25b541efa8924c13454e34686f5ab` |
| `include/core/ModeSelectionTransaction.hpp` | `5ee7a5f854743127bb0344fefea938f477156405adae71abcce0c11aaf128ca1` |
| `include/core/RecoveryInitialization.hpp` | `af91a4af2a5c4acbcac37a905af4a4038f11b6300bbc9476b2fa362995f1710a` |
| `include/core/ProfileStoreFaultControls.hpp` | `d463a4a56d1e1e8a2599fbe699e4d565557a1bae6e8b44465b4af113c5118b8b` |
| `include/core/ResourceDiagnostics.hpp` | `00cddf0ce9bd9a34c0f3daa54fd3f909946ce9c17f0a9ce9dbe3dfa28e8715ad` |
| `include/core/StackWatermark.hpp` | `7b87846fa11a0910ec0c4fc6c5fd5520c78dffd6bce1015c335983ab9845f236` |
| `HAL/pico/include/core/CheckedStorageFile.hpp` | `7cab2070e1e0b3d3f4a9d98b2aad97e7b31aa4a808f38aa6ce00658e1e4e6e0c` |
| `schema/haybox/config.proto` | `59d5122318d8f8567874984a7f1c472c3c4f9384e1751996550868cd6c1b6772` |
| `schema/haybox/config.options` | `612d23b268742d0cc8e4b871d33b3ccba7c6f912ca3352364e329b3fef0096c0` |
| `config/glyph/env.ini` | `00c4d5a9f1d888cf40bc6919daa51d254bd79f9a96db07a8aafc022910154094` |
| `tools/glyph_profile_store_candidate_tool.py` | `9682a567671e1ebf132d1debd56066f273c06a17a28801b32b84869818d9873e` |
