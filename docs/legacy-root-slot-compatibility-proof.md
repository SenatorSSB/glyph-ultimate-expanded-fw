# Legacy source-kind-3 root slot compatibility proof

Owner authority: `owner-chat/2026-11-12/legacy-source-kind-3-root-slot-compatibility-proof`.
No hardware action; previous diagnostic episode is terminal. Phase B is disabled.

Historical writer `f7ba82d4cbe79d4353e8d87b7d1b24be3fc15113`,
`HAL/pico/src/core/ProfileStore.cpp`:
- Directory51–63: migration state 0 none, 1 receipt/fenced, 2 compact Config published.
- EncodeDirectory67–87: extent2620, generation+8, incarnation+12, state+24,
  migration IDs+2608/+2612, CRC+2616 covering first2616 bytes.
- ImportLegacy339: copies directory, writes payloads/IDs, state1, ++generation.
- CompleteMigration340: copies directory, changes ONLY state2 and ++generation.
- PublishDirectory235–246: destination `(generation+1)&1`; verified temporary
  write/read, remove only destination, rename only destination. Opposite root untouched.
- LoadDirectory207–232: newer generation selected; roots expected after generation1.
- AtomicCommit header46–58 preserves opposite active root during publication.
- config/glyph/common/src/config.cpp218–249 saves compact Config before completion.

Sixteen historical writer revisions from7e4b2db264a3f06e565570f8c43a09f7edc434bd
to08296b0e72f440e6536cff45246c57bb17bc9868 preserve identical normalized
ImportLegacy/CompleteMigration/EncodeDirectory. Six PublishDirectory variants keep
single-slot parity publication. The independent source specialist verified these facts.

The reachable immediate completion shape is olderstate1 generationN plus newerstate2
N+1, both surviving, with older bytes retained verbatim. State0 ->1 ->2 requires
two publications and overwrites the state0 slot, so adjacent older0/newer2 is NOT
source-proven and remains rejected. An ordinary Reorder after completion produces
two state2 roots, also retained by the source-native replay.

At diagnostic d082739b, ProfileStore::PrepareBootstrap914–918 selects newer;
DecodeLegacy604–616 hashes its entire original2620 bytes into migration_source,
sets kind3, copies ordered nonzero trailer IDs and revision1. The older root never
becomes proof authority. No root is chosen merely because its marker is2.

Conditional physical deduction: Scan's LegacyRoot(path,false) checks the same full
structure as LegacyRoot(path,true) except the latter additionally requires+24==2.
The generic path bounds+24<=2. Given stable checked reads, tested-source correspondence
and no I/O failure, `migration: legacy root` therefore implies at least one survivor
has state0 or1. The physical slot, raw bytes and exact state are UNKNOWN. Normal boot
is unvalidated. Receipt and Config correspondence are closed prior physical boundaries.

Defect: every survivor was required completed before newest/source-hash selection,
rejecting a successful historical writer output. Repair retains full generic validation,
incarnation/generation bounds, slot gap/equal-hash fences, source hash selection,
completed-source revalidation and exact migrated IDs/revisions/payload proof.
Only an older state1 dependency can be newly recognized: adjacent generation,
correct historical parity, and its complete2620-byte encoding must equal the
hash-bound selected root after normalizing only generation/state/derived CRC in
existing RAM scratch. This is a comparison; no storage operation writes these bytes.
State0 and state1 source roots stay fenced. No migration continuation or completion.
Both-state2 behavior is preserved. Absent historical dependencies remain permitted
exactly as before; the single survivor still must hash-bind and prove completion.

Executable witness tools/replay_legacy_root_writer.py compiles exact historical
Directory/encoder/decoder/import/completion/reorder and atomic publication code from
Git. Synthetic Config/profile types, successful payload validation/writes and known
initial ready directory are explicit test boundaries. This proves root-publication
semantics, not payload validity or a complete historical/physical boot. Differential
namespace fixtures pair those exact raw roots with independently valid synthetic
payloads/current Config. Raw witness bytes/hashes/source blocks are retained.

No protected gameplay/source/dataset/Profile JSON/solver/export/UI changes.
Candidate firmware is isolated and must not merge before separate hardware PASS.
