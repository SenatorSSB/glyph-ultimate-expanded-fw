# Independent P1/P2 committed delta review

Candidate `a2a5c94d0a0bef3638b1ead1071ff58faaa7528f`, tree `01005eeaf2a9c93abbf7bd47dcd861c4847cea9a`, compared with H1 `a288908de83e75997cd7459b4abe607ee968bb60`. **No material source, transaction or lifetime defect found in this P1/P2 delta.** The whole resource gate remains OPEN; no final source/ELF, build, hardware or integration acceptance is claimed. Requested gpt-6.1-sol/high, observed UNKNOWN.

The candidate was archived independently to `/private/tmp/glyph-a2a5-source-review-20261021`. Audit facts and test source came from that immutable archive and the hashed immutable author packet. One initial live header read was discarded as an audit input and re-read/verified from the snapshot. The production delta is exactly four ProfileStore/Persistence source/header paths; no conditional header/config.cpp/P4/Load/Capture delta is included. df5 layout proposals1/2 authorize these methods; later0a346975 scope is not treated as already implemented here.

**P1 lifetime.** PrepareBootstrap returns a byte action before ExecuteBootstrap. Its only continuation data is the existing owned _next seed and store fields, not borrowed automatic geometry/phase/legacy arrays. O3 relocations show separate Prepare then Execute calls in both Begin entries.

**P1 flags/results.** All original early refusal/readiness/root-invalid/read-only checks remain in their original order. Existing return _ready maps to Complete/Refused without changing flags. phase1 normal initializes and recovery refuses; phase3 recovery LoadDirectory stays read-only; ordinary phase3 reconciles after preceding checks return.

**P1 persistence order.** Fresh/v1 upgrade checks original geometry and reserve before first write, copies same _next, then control1, _v2=true, InitializeV2 own geometry at original point, root0/root1/control2/LoadDirectory. Existing current/previous/migration validation and hashing remain pre-write. No new read/write, admission reduction or backend semantics found.

**P2 constructor points.** Verify generation read file begins only after unchanged mutation/RAM/availability/file-selection checks; stage w+ begins only after size+temp Remove; verify read file begins only after stage scope ends; published readback read file exists only after Uncertain publication. Modes match original constructor tests.

**P2 file ownership.** One alignas(CheckedStorageFile) raw slot, placement-constructed unchanged class, exact qualified destructor and then full-slot zeroing on every scope exit. No live overlap: generation scope returns before Save, and stage/reopen/readback scopes never overlap. Stream/compare callbacks remain synchronous and cannot escape the file reference.

**P2 close/fallback.** All original explicit closes remain, including staging_failed close on failed constructor, unconditional staged close, generation checked close and readback short-circuit order. Open lost-ack cleanup and Close clearing opened are unchanged in CheckedStorage. Constructor-success/stat-failure in generation returns through destructor fallback; qualified destructor preserves it. Already-closed handles do not get a new close.

**P2 generation fence.** VerifyExpectedConfigGeneration returns before Save; same synchronous core0 no-yield/no-writer-callback invariant. Durable header CRC compared only after checked close; unchanged Conflict/StorageFailure/Uncertain and Save return mapping.

**P2 phase sequence.** Prepare(size), Remove, Stage/write/encode/CRC/header/seek/sync/close, independent reopen/check/reencode/close, Stat/prior removal/rotation, pending CRC+size then publication; ordinary error rollback and uncertain exact readback preserved. Short-circuit AND composition retires each helper before next.

**P2 metadata aliasing.** Original current Result is represented by bool save_phase.current before operation scratch is overwritten by remove/rotation; later rollback consumes that saved bool. Original uses of current needed only its truth value there. Header/encoded_size remain owned scalar metadata; uncertain readback keeps exact expected CRC/size and deterministic payload compare.

**P2 reset.** Save clears all phase bytes before prepare and on every normal/error exit through RAII; raw file slot clears after each file destructor. No heap, new format, payload/path/directory buffer or extra slot found. Existing load/migration methods unchanged at this checkpoint.

**Resource qualification.** Actual ARM slot176 plus SavePhase32 =208 bytes before final-link padding, both enum ABIs; old STATE168/200 estimates are superseded, not rewritten as proof. New later P4/boot scalar gross214 is outside this delta assessment. Component .su/relocations establish phase frames, not complete linked stack/static bounds.

## Verification

I independently rebuilt and ran the existing actual production Persistence/CheckedStorage/pinned NOR-LittleFS host fixture against frozen a2a5 source with ASan/UBSan: **1636 Fail/LostAck cases at818 operation boundary events PASS**, including reconcile/next-operation/reboot checks and actual native handle closure. Its1641 output rows match a288 baseline on every result/fence/generation/canonical file hash/full operation trace, excluding only the explicitly labeled raw NOR hash field. Independently parsed writer short/default ABI logs produce the same equality. Raw NOR hashes differ and are not relabeled equal: on64-bit host ConfigHeader includes4 unspecified padding bytes; file canonicalization excludes only those bytes, while target ARM header is8 without padding.

I independently ran affected strict host regression: **24 current cases and4 frozen production negatives PASS**. The first archive-only run reached24PASS then could not obtain frozen historical Git objects because the archive intentionally has no.git. That failure log remains; the same checker completed using read-only GIT_DIR solely for its immutable git-show lookups. No Git mutation occurred.

Two writer-run targeted mutants were independently inspected: staging before Remove fails normal publication, and omitting the raw slot's actual destructor fails native handle closure on a constructor failure. Their source diffs change only the named phase order/destructor and their failure assertions are meaningful. Existing37-case Persistence and migration logs were read as attributed author evidence, not fresh independent execution.

Committed historical pre_mode_header/STATE.md still says168-byte slot/200total. Exact both-ABI ARM nm and emitted clear176 correct this to176+32=208 before final-link padding. Preserve that erratum explicitly. Later gross214 including other metadata is separate. The new object recipes/source hashes match frozen checkpoint; Begin32/Prepare96/Execute80 and SaveIf16/Save16 are component facts. Helper grandchildren, destructor/error frames, outer callers/IRQs/ROM remain in the final all-path calculation.

No new broad native oracle rerun or firmware build was performed. Post-P4/Load/Capture clean-source review, actual final ELF/map/.su/source/generated/dependency/flags correspondence, every31-class resource obligation, original limits and custody still precede a candidate-specific hardware packet. No device approval/action or hardware PASS. Nunchuk NOT_TESTED; timing/highwater NOT_MEASURED; root cause UNPROVEN.
