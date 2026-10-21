# Frozen H1 source review and constrained resource-branch inventory

Frozen candidate **a288908de83e75997cd7459b4abe607ee968bb60**, tree `d0b92601a26ea1523ffb4fff4b1c2c663b719791`: **no material defect found in the H1 production delta**. The complete native resource gate remains **OPEN**. This is the finite first-phase review requested by root, not a final review of concurrently edited source or an H1 firmware build.

The source was independently archived to `/private/tmp/glyph-h1-source-review-20261021` using `git archive` of the exact commit. It has no Git checkout and no floating production reads. A dependency-only `.pio` symlink points to the writer's installed toolchain/library inputs for the focused host test. Canonical local readback was df5fbcd019dfd7e72b897b7d5a43e6c142ecd665; root owns supplied live verification and publication. Requested routing gpt-6.1-sol/high, runtime-observed routing UNKNOWN. No source/checker/SDK/Git/canonical/device/network mutation, broad test matrix or firmware build was performed.

## H1 findings and independent validation

The only production paths changed from bcb9824bc00c6210babdf00675952deeda7f7c88 are ProfileStore.cpp and its private header declaration. `Admit` preserves the exact original GC status check and Capacity formula/order, invoking `EvaluateAdmission` only after GC returns Ok. CollectGarbage's fixed Search is a constant-initialized POD owned by the existing synchronous core0 store lane: every iteration zeros the full object and reinstalls owner; the scope guard zeros it on every post-acquisition exit. Unready/recovery/uncertain/migration/protected-root failures precede acquisition. The production callback neither mutates nor reenters store; Enumerate closes its directory before remove. No pointer escapes the synchronous call. The change introduces no directory/history admission restriction, deletion-policy change, retry, callback or heap allocation.

I independently ran the actual pinned NOR/LittleFS GC fixture from the frozen snapshot with ASan/UBSan. It passed protected current/previous/active/migration bytes, unrelated/nested/matching-name physical directories, first-match order, repeated/new-call reset, all16 enumeration/remove before/after Fail/LostAck cases, handle closure, 128/129 removal budget, no Capacity after GC Full and same-token retry. Raw report/log are under `/private/tmp/glyph-native-h1-review-gc-20261021`. This finite run did not generate/replay additional orphan or power-loss images. Existing broader-state witness evidence remains attributed and is not target-stack evidence.

Source/header SHA-256 match the committed adopted O3 component manifest. The object facts are GC48, Admit16, EvaluateAdmission120, Capacity320 and static Search40. Capacity's returned object is absent during GC but remains charged during EvaluateAdmission. These are component facts, not final linked source/ELF correspondence. The preserved bcb ELF was rehashed to `3f43081cec177763abf9f1955f8a3686faa39fa4ca660a5de174a2d70ca62884`; it is **not** H1 firmware.

## Concrete source/resource findings

The final repair must account for **LoadConfigChecked PriorCompact restoration** separately from SaveConfig: after explicit close, `Rename(prior,current)` still runs inside its retained automatic function frame (existing production O3 .su456). The first mutation can occur here, under boot, recovery, Configurator preparation/query/SET or mode-destination callers. A Save-only phase repair does not retire that frame. This is a concrete uncovered branch obligation, not a newly proven overflow or authority to edit additional methods.

GC with no garbage is read-only and need not clear pending filesystem recovery; CREATE/UPDATE/duplicate first record can therefore still be the first mutator. Rename/Reorder/Delete first write is control phase3. Conversely a successful earlier mutating record/GC operation can clear prior pending state, so it cannot automatically be recharged at every later directory write. LFS forceconsistency orders demove then deorphan, but demove's dir_commit can itself enter deorphan on an orphaned result; deorphan's direct orphaningcommit and restart loop must be analyzed from actual retained code. Broad directories/orphans/MOVE cannot be excluded by a flat-history premise. Fixed-depth traverse state is already inside one function frame; do not invent a C-frame-per-directory recursion.

Preserve every other important branch: fresh/legacy/phase1/phase2/phase3 boot and recovery; legacy source capture/hash/copy and streamed import; compact Config save/completion; Config staging/reopen/rotation/uncertainty-readback/rollback; ordinary SetConfig's retained validation caller; two-domain reconciliation/query/replay; READ/health/reference; activation/decode/structure/body/context SHA; native frame; identity/parser/snapshot/TX; own-core masked scan/publication; setup1/display/RGB/metrics and actual backend interrupts.

The separate exact-bcb IRQ/ROM/core1 worker supplied: Configurator/recovery FS348 including padding; all-backend mode-save conservative IRQ union456 (optional rounding512); core1 upper1152; flash SDK40+ROM88=128 below the LFS callback while masked, memory ROM memcpy12/memset8 across official B0/B1/B2. These are attributed exact-bcb certificates with final correspondence required. Their source invariants are consistent with inspected call ownership. They are not universal simultaneously feasible maxima. The concrete detected-NES/default-XInput-serial IRQ witness is360 before padding; it needs simultaneously unmasked foreground>1688 to establish overflow. The456 union alone must not activate conditional header permission. New maskable IRQs cannot be added after CPSID; noInterrupts16 pre-mask can coexist. Alarm, SIO, hardware/deferred USB, SysTick and priority0 GPIO are constrained alternatives.

## Independently reconstructed concrete over-budget compositions

These are exact-bcb retained source-feasible foreground chains for unchanged H1 Persistence/SDK inputs, not target highwater measurements or a new whole-firmware certificate. Common LFS chain: deorphan176 -> orphaningcommit160 -> relocatingcommit136 -> splittingcompact192 -> compact136 -> traverse216 -> commit callback72 -> commitprog72 -> LFS program callback24. The required admitted-state predicates are a valid mountable Config/source namespace, positive directory-orphan repair, a populated affected metadata pair forcing compaction and a cache-full traversal program callback. Existing host evidence observes repair/compact/program but does not realize/observe this entire target chain. Broad support cannot exclude those source predicates using an unapproved pristine-history requirement.

| Unchanged applicable route | Actual retained prefix | Foreground before noInterrupts | At pre-mask16 | Budget |
|---|---|---:|---:|---:|
| Boot prior Config restore | main48 + setup136 + LoadConfigChecked456 + CheckedRename24 + lfs_rename240 |**2088**|2104|2048|
| Boot source-capture first temp Remove | main48 + setup136 + CaptureLegacySource608 + CheckedRemove48 + lfs_remove136 |**2160**|2176|2048|

No IRQ allowance, alignment padding, ROM child or hypothetical concurrent producer is needed for these compositions to exceed2048. They do not establish that a particular controller experienced overflow. `lfs_rename` and `lfs_remove` inline their consistency calls: adding the standalone forceconsistency64 would double-count. `lfs_dir_commitprog` inlines the relevant bd_prog/flush work and directly BLXes the configured program callback; bd_prog40 and bd_flush72 are not added here. `setup` is136 in the exact linked ELF; an older .su entry272 must not override it. Capture's exact prologue uses36 push + register-adjusted572, verified by literal0xfffffdc4, giving608.

This materially extends the existing31-class inventory: both methods are outside the current Save/generation-only Persistence scope. A bounded source-preserving Load hypothesis is a checked-load preparation helper that owns the existing automatic File/Error through their original close/destructor points and RETURNS before the same prior Rename, then same candidate/config_generation publication. Return only owned scalar source/CRC/result metadata; retain the existing static candidate; **no load File workspace conversion** is required or authorized. For Capture, a bounded hypothesis retires unchanged source-check/hash/capacity preparation before the same initial temp Remove, and isolates the existing copy_checked_file automatic two-file lifetime from later hash/publication. Those are named synchronous lifetime boundaries, not new persistence semantics or automatic edit authority. Exact engineering/source/ELF/fault proof and bounded Curator adoption are still required before either currently excluded method changes.

## Complete constrained inventory

The JSON contains31 branch classes with exact source entrypoints, protected ordering/state predicate, final proof obligation and truth classification. Each must receive a final actual caller+callee/indirect/IRQ/ROM/PRIMASK bound or a source-proven reachability exclusion. This is complete at the constrained production branch-class level, not a claim every final machine path is already closed.

### STARTUP: reset, C++ constructors and ordinary SDK main

Sources: `config/glyph/common/src/config.cpp:170`, `HAL/pico/src/core/Persistence.cpp:120`, `HAL/pico/src/core/NativeTargetMetricsEntry.S`.

Persistence mounts with LittleFSConfig(false); no automatic formatting is inferred. External main paint and core1 adapter do not observe earlier startup. Bootloader MB1/DMA route terminates before ordinary persistence.

Required proof: Retain reset/linker/main/constructor stack proof separately from post-main scan; account mount/allocation and display startup, actual 2048 regions and wrapper ABI. No startup or stack change is allowed.

### BOOT-PREFLIGHT: normal/recovery Begin common checks

Sources: `HAL/pico/src/core/ProfileStore.cpp:521`, `HAL/pico/src/core/ProfileStore.cpp:547`, `HAL/pico/src/core/ProfileStore.cpp:641`.

Reset owned directory/active state; required format, geometry/control presence/load, expected incarnation and legacy authority checks precede writes.

Required proof: Measure both Begin entries and actual preparation/execution siblings after repair. Preparation must return before mutation; scalar plan must not borrow an expired automatic. Include geometry lfs_fs_size traversal and decode/hash alternatives.

### BOOT-PHASE1: control phase1 resume

Sources: `HAL/pico/src/core/ProfileStore.cpp:611`, `HAL/pico/src/core/ProfileStore.cpp:662`.

Normal resume calls InitializeV2 directly. Recovery refuses without root/control writes. InitializeV2 repeats its original geometry check at the original reached point.

Required proof: Separate root0/root1/control2 publication and readback/failure maxima, with first mutating operation allowed pending consistency. Preserve all operation order/flags/early returns.

### BOOT-PHASE2: healthy or degraded phase2

Sources: `HAL/pico/src/core/ProfileStore.cpp:684`, `HAL/pico/src/core/ProfileStore.cpp:801`.

Load roots, generation/high-water/incarnation and SameDirectory checks are read-only. One invalid root causes read-only recovery. A healthy Begin does not inherently clear LittleFS move/orphan state.

Required proof: Bound root reads/decode and SameDirectory SHA independently; retain pending state at first later mutation. Do not add subsequent write recovery merely because boot was read-only.

### BOOT-PHASE3: uncertain control phase3

Sources: `HAL/pico/src/core/ProfileStore.cpp:674`, `HAL/pico/src/core/ProfileStore.cpp:937`.

Recovery calls LoadDirectory then remains read-only; ordinary Begin calls ReconcileTransaction. Reconcile may write control2 or publish an aborted identity/high-water checkpoint.

Required proof: Include successful-already-published, aborted-next-generation, unmatched/failure branches. Phase3 reconciliation must remain after original prior checks and may be the first mutation.

### BOOT-FRESH-UPGRADE: no v2 control / fresh / v1 legacy upgrade

Sources: `HAL/pico/src/core/ProfileStore.cpp:701`, `HAL/pico/src/core/ProfileStore.cpp:728`, `HAL/pico/src/core/ProfileStore.cpp:747`, `HAL/pico/src/core/ProfileStore.cpp:784`.

Missing control plus any v2 root, required-format>=2, invalid v1 pairs, expected-incarnation mismatch or recovery/fenced migration must retain original refusal/read-only behavior. Accepted upgrade validates all retained dependencies before write.

Required proof: Bound legacy DecodeLegacy, ReadProfile/current+previous, HashMessage and Receipt as separate pre-write paths; preserve initial admission then control1, _v2, root0/root1/control2/LoadDirectory.

### CONFIG-LOAD: Config current/prior/legacy load, decode and validation

Sources: `HAL/pico/src/core/Persistence.cpp:370`, `HAL/pico/src/core/Persistence.cpp:497`, `include/core/RecoveryInitialization.hpp:19`.

Config candidate is static; CheckedStorageFile and ConfigValidationError are automatic. Ordinary read/validation/close paths precede publication to caller.

Required proof: Include every boot/recovery/Configurator/query/mode caller prefix and protobuf Stream callbacks, validator/error, close/destructor error paths. Existing .su LoadConfigChecked456 is not a whole-route bound.

### CONFIG-PRIOR-RESTORE: LoadConfigChecked PriorCompact Rename

Sources: `HAL/pico/src/core/Persistence.cpp:429`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:534`, `include/core/ModeSelectionTransaction.hpp:41`.

Explicit close precedes Rename(prior,current), but the LoadConfigChecked automatic frame remains retained. This can be the first filesystem mutation before Save and is reachable even from the recovery load helper.

Required proof: Dedicated broad-FS forceconsistency/deorphan/MOVE + metadata-write and IRQ bound; do not assume Save lifetime repair removes this frame. Preserve existing uncertainty/generation/result behavior. No new edit scope is inferred.

### CONFIG-SAVE-GENERATION: SaveConfigIfGenerationMatches durable fence

Sources: `HAL/pico/src/core/Persistence.cpp:172`.

Fence, RAM generation, availability, file selection, CheckSavedConfig/seek/header/read/close then durable CRC comparison precede Save; all writers synchronous core0.

Required proof: Verify file lifetime actually ends before Save in new source/ELF; exact constructor failure, explicit-close and destructor-fallback equivalence; generation/fence conflicts and no interposed callback/yield.

### CONFIG-SAVE-STAGE: SaveConfig size, remove temp, open/write/encode/CRC/header/sync/close

Sources: `HAL/pico/src/core/Persistence.cpp:194`, `HAL/pico/include/core/CheckedStorageFile.hpp:9`.

Encoding-size precedes temp Remove. Temp remove/open can be the first mutation; even absent Remove enters LFS consistency before lookup. Staging has one checked file and exact error cleanup.

Required proof: Measure size, initial remove, constructor/open, body encoder, CRC read, sync/close separately under new raw-slot owner and phase siblings. Check all before/after fault/lost-ack branches, failed constructor and fallback closes; no second live raw slot.

### CONFIG-SAVE-VERIFY: independent reopen and deterministic reencode compare

Sources: `HAL/pico/src/core/Persistence.cpp:232`, `HAL/pico/src/core/Persistence.cpp:60`.

Read-open/check/seek/compare/checked-close is independent of staging, and its automatic file lifetime is nonoverlapping.

Required proof: Bound nanopb compare callback -> checked read with actual File slot and caller phase. Check every return resets slot/metadata and compares unchanged bytes; sequential stages are maxima, not additions.

### CONFIG-SAVE-PUBLISH: current stat/prior remove/rotation/publication/uncertainty/rollback

Sources: `HAL/pico/src/core/Persistence.cpp:240`.

Stat, remove prior, rename current to prior, set pending metadata, rename temp to current; exact authenticated readback may clear uncertainty; failed publication may rollback.

Required proof: Bound Remove, each Rename, readback/check/reencode, rollback and close/destructor alternatives. Preserve _config_generation/_mutation_fenced/_pending fields and statuses. Earlier successful mutation can clear boot pending state, but metadata relocation/repair generated later still needs source-specific treatment.

### MODE-DESTINATION: selected backend mode persistence

Sources: `config/glyph/common/src/config.cpp:141`, `include/core/ModeSelectionTransaction.hpp:41`, `src/core/mode_selection.cpp`.

Load candidate, locate backend, unchanged/refusal, capture generation, field edits, validate, Save then scratch/reboot. Configurator/Unspecified excluded; physical backends remain admitted.

Required proof: Use 456 safe all-backend IRQ union (512 rounding optional), or a proved tighter route. Conditional header permission requires exact post-Persistence feasible overflow with validation Error contributor; 456 alone is not a feasible lower witness. Existing NES+serial360 witness must be paired with simultaneously unmasked foreground>1688.

### MIGRATION-CAPTURE: legacy snapshot capture and source identity

Sources: `config/glyph/common/src/config.cpp:247`, `HAL/pico/src/core/Persistence.cpp:279`, `HAL/pico/src/core/Persistence.cpp:288`, `HAL/pico/src/core/Persistence.cpp:77`, `HAL/pico/src/core/Persistence.cpp:92`.

Read/check/hash existing config; if absent snapshot, capacity admission precedes temp Remove/copy/hash/Rename/identity check. Existing snapshot takes identity-only path.

Required proof: Include CaptureLegacySource608 and hash_file656 object frames only at their actual calls, copy input/output simultaneous handles, first-write consistency and all failure/uncertainty exits. No extra snapshot/format/erase is authorized.

### MIGRATION-IMPORT: ImportLegacyStream admission, two streamed records and directory

Sources: `HAL/pico/src/core/ProfileStore.cpp:1737`, `HAL/pico/src/core/Persistence.cpp:333`, `config/glyph/common/src/config.cpp:254`.

Hash source, replay/migration-state checks, Admit, per-profile reader/validate/record publication, receipt/compact digest then directory publication. Portable ImportLegacy is a separate API, not assumed a linked device caller.

Required proof: Account boot setup/lambda/ReadLegacyProfile stream and all profile publication paths; source SHA/hash/receipt maxima separate from FS maxima. Determine final linked reachability of portable compatibility entry before inclusion/exclusion.

### MIGRATION-COMPLETE: compact receipt/Config save/CompleteMigration

Sources: `config/glyph/common/src/config.cpp:231`, `config/glyph/common/src/config.cpp:274`, `config/glyph/common/src/config.cpp:289`, `HAL/pico/src/core/ProfileStore.cpp:1695`, `HAL/pico/src/core/ProfileStore.cpp:1720`, `HAL/pico/src/core/ProfileStore.cpp:1870`.

Boot may save compact config or acceptance marker, verify source/profile payloads, then publish migration state2; already-state2 returns without write.

Required proof: Separate compact hash/read validation, ordinary Save and CompleteMigration directory write prefixes; include receipt mismatch, migration fence, Config current/prior/recovery cases.

### DISPATCH-RX: Receive/identity/CAS/admission preparation

Sources: `HAL/pico/src/comms/ConfiguratorBackend.cpp:465`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:474`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:534`.

IncomingScope/RX lease remains owned across Receive, Dispatch and Respond; request/response/frame are separate static state. Preparation performs durable load/replay/CAS before mutation.

Required proof: Verify true returned siblings in final source/ELF rather than nested wrapper alone. RX decode/preparation/identity digest/load and operation execution cannot be blindly added; preserve FaultScope/tickets/trace/reset at effective original boundaries.

### STORE-GC: GC protected-root/no-garbage/enumerate/remove/budget

Sources: `HAL/pico/src/core/ProfileStore.cpp:1153`, `HAL/pico/src/core/ProfileStore.cpp:1299`, `HAL/pico/src/core/CheckedStorage.cpp:163`.

Early readiness/uncertainty/migration/protected-root checks precede Search acquisition. Directory scan closes before removal. First eligible unprotected root regular .bin/.tmp is removed; directories/skipped names retained. Each iteration and operation exit reset all Search bytes; 128 removals returns Full.

Required proof: Include enumeration callback sscanf/snprintf/libc and protected checks as separate read-only maximum; include remove/forceconsistency/deorphan/MOVE/compaction maximum with GC48. No Capacity frame during GC. No mutation after Full/failure. New independent host fixture PASS covers these invariants.

### STORE-CAPACITY: post-GC EvaluateAdmission and STATUS Capacity

Sources: `HAL/pico/src/core/ProfileStore.cpp:1185`, `HAL/pico/src/core/ProfileStore.cpp:1354`, `HAL/pico/src/core/ProfileStore.cpp:1361`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:452`.

EvaluateAdmission runs only after GC Ok, with unchanged formula/geometry/protected/fixed/reserve accounting. Capacity traverses actual FS then bounded union records; STATUS uses its own capacity wrapper.

Required proof: Account EvaluateAdmission120+Capacity320+actual child/caller, not GC+Evaluate frames together; all protected record Stat and filesystem/CTZ reads, uint64 helpers, LoadProtectedRoot and errors. Source pinning proves object correspondence only; final linked ELF required.

### STORE-FIRST-RECORD: CREATE/UPDATE/DUPLICATE and imported first record

Sources: `HAL/pico/src/core/ProfileStore.cpp:988`, `HAL/pico/src/core/ProfileStore.cpp:1020`, `HAL/pico/src/core/ProfileStore.cpp:1459`, `HAL/pico/src/core/ProfileStore.cpp:1488`, `HAL/pico/src/core/ProfileStore.cpp:1538`.

Preparation validation/encode ends before publication. CREATE/UPDATE first record may be first write after read-only GC/no garbage. DUPLICATE retains caller32 over Create and preserves candidate lease.

Required proof: Bound Open(create/truncate), Write, Sync, Close, readback and Rename separately, with pending MOVE/orphan at first actual mutator. GC success alone does not prove pending state cleared when no deletion occurred. Preserve unknown outcome and exact immutable payload owners.

### STORE-DIRECTORY: first directory and later directory publication

Sources: `HAL/pico/src/core/ProfileStore.cpp:838`, `HAL/pico/src/core/ProfileStore.cpp:1413`, `HAL/pico/src/core/ProfileStore.cpp:1446`, `HAL/pico/src/core/ProfileStore.cpp:1551`, `HAL/pico/src/core/ProfileStore.cpp:1575`, `HAL/pico/src/core/ProfileStore.cpp:1596`.

Rename/Reorder/Delete have no preceding record; control3 can be first write. Create/Update/Duplicate directory occurs after successful record. Sequence is control3 -> parity root -> RAM authority/protected invalidation -> control2.

Required proof: Cover each retained metadata caller, WriteControl/PublishDirectory/Publish final executor; preserve Start/name/CAS/refused semantics. Pending state cleared by a successful earlier mutation is not added again merely from boot; include relocation-created recovery separately.

### STORE-RECONCILE: uncertainty/query/replay/abort reconciliation

Sources: `HAL/pico/src/core/ProfileStore.cpp:937`, `HAL/pico/src/core/ProfileStore.cpp:1372`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:681`.

Query/mutation may reconcile both store and Config before admission. Already-published control2 repair and aborted checkpoint publication differ. Exact replay/conflict can return without new operation.

Required proof: Bound pre-dispatch ReconcileTransaction/LoadDirectory/SameDirectory/control write and ReconcileConfig->LoadConfigChecked; retain normal/recovery differences, token/high-water/receipt/fence order and error statuses.

### STORE-READ-REFERENCE: READ/health/status dependency/reference SET

Sources: `HAL/pico/src/core/ProfileStore.cpp:1030`, `HAL/pico/src/core/ProfileStore.cpp:1132`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:586`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:628`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:737`.

READ record wire lease stays through response encode; Health uses candidate scratch. Reference SET validates chosen profile and Config then SaveConfigIfGenerationMatches with existing static validation error.

Required proof: Bound record Stat/open/read/close, native scan/decode/validation and legacy alternatives, fallback prior revision, checked-reference Save and Config status load. Read/response encode does not carry FS write frames.

### LEGACY-CONFIGURATOR: legacy GET/SET/device-info/unknown/reboot responses

Sources: `HAL/pico/src/comms/ConfiguratorBackend.cpp:296`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:317`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:334`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:924`, `HAL/pico/src/core/Persistence.cpp:462`.

Whole-Config SET has independent decode/error and automatic validation_error, profile engine checks then Save. GET config uses LoadConfigRaw/Stream; unknown formatting is separate helper. Retired fault requests remain inert in production.

Required proof: Include retained HandleSetConfig caller during new Save phases; PriorCompact load before SET and error formatting/TX need separate maxima. Include real transport/yield/USB guard scopes rather than transferring filesystem-specific mutex assumptions blindly.

### NATIVE-ACTIVATION: profile selection, native prepare/copy/bind/context digest

Sources: `src/core/mode_selection.cpp:130`, `HAL/pico/src/core/ProfileStore.cpp:1086`, `src/modes/Ultimate.cpp:782`, `src/modes/UltimateNativeProfile.cpp:182`.

Read current then previous fallback; copy candidate to dedicated active, BindOwned, then ContextMatches and latch selected engine. Hash scratch is synchronous core0 and not reentered by IRQ/core1; invalid/native-unavailable output is neutral.

Required proof: Retain exact source/ELF read/decode/PrepareStructure/BodyDigest/CopyProgram/ContextDigest/SetConfig and activation metric paths with their actual callers/IRQ routes. No FS frames remain during later native frame evaluation; unchanged native oracles apply only to unchanged sources.

### NATIVE-FRAME: real per-frame preprocess/evaluator

Sources: `src/core/ControllerMode.cpp:9`, `src/modes/Ultimate.cpp:795`, `src/modes/UltimateNativeEvaluator.cpp:41`.

One remap+ordered SOCD; consume owned published view; FrameState132+context12=144 source aggregate. Evaluator232 compiled frame is a different measurement. Table/rule/effect loops are finite.

Required proof: Bound actual backend SendReport/ControllerMode/Evaluate/direction/helper/IRQ prefix; separate sibling metrics RecordFrame. Preserve all18 frozen family/oracle semantics and no parser/load/status dependency in output hot path.

### IDENTITY-DIAGNOSTIC: XInput Poll, parser/digest/snapshot/TX

Sources: `include/core/RuntimeIdentityService.hpp:42`, `HAL/pico/src/core/NativeTargetMetrics.cpp:181`, `include/core/RuntimeIdentity.hpp`.

Poll is noinline after reports, XInput-only, one try-lock CDC pass, consume<=32, identity16/72 wins; diagnostic16/160 and one admitted write; no blocking Task/flush/retry in pass.

Required proof: Separate parser, Observe/body/context SHA, diagnostic mailbox/snapshot and write maxima; actual outer __usb_mutex suppresses deferred task here but does not mask all IRQs. Generic raw transport prefixes need actual lock/IRQ analysis. Preserve status/wire/parser counters and no new command.

### SCAN: post-main own-core stack-write scan/mailboxes

Sources: `HAL/pico/src/core/NativeTargetMetrics.cpp:155`, `HAL/pico/src/core/NativeTargetMetrics.cpp:93`, `config/glyph/common/src/config.cpp:338`, `config/glyph/common/src/config.cpp:438`.

Scan is per-core, bounded chunk, SaveIrq/restore exact state; mailbox word atomic stores/loads are bounded no-retry, no heap/FS. Scan then Publish are partially distinct masking windows.

Required proof: Account ServiceCore/Publish/Now/atomic helper presence and own entry prefix; preserve bottom32 exclusion and 2048 bounds. Watermark/timing remain NOT_MEASURED and cannot close structural gap.

### CORE1: setup1/display/control/RGB/metrics

Sources: `config/glyph/common/src/config.cpp:350`, `config/glyph/common/src/config.cpp:437`.

Concrete seven modes, SSD1306/Wire1, NEOPIXEL11 and callbacks; no core1 Config writer/ProfileStore/CDC endpoint producer in inspected source. setup and loop sequential.

Required proof: Reuse attributed exact-bcb graph1152 upper only after unchanged source/dependency and final emitted-code correspondence; linker movement alone is not a changed stack. Final stack regions/SIO/DMA/core1 entry must still match.

### LFS-INTERNAL: all admitted mutable/read filesystem branches

Sources: `HAL/pico/src/core/CheckedStorage.cpp:77`, `SDK LittleFS lfs.c:796`, `SDK LittleFS lfs.c:2174`, `SDK LittleFS lfs.c:4448`.

Checked storage is same mount. Writable Open/Remove/Rename force consistency before work; read-only Begin need not. forceconsistency demove and deorphan are ordered, but demove dir_commit can itself deorphan on orphaned return. deorphan directly invokes orphaningcommit; repair restart is a loop. Traverse uses explicit fixed depth3 state, not one C frame per directory.

Required proof: For every caller above bound append/compaction/split/relocation, allocator rawtraverse/CTZ, commit callback/prog/flush/CRC and read/erase alternatives at exact same prefix. Handle broad positive-orphan/PENDING_MOVE source predicates; do not add all alternatives or assume every guard simultaneously true. Existing witness proves nested repair compact/program, not deepest target callback/IRQ realization.

### IRQ-ROM: unmasked/pre-mask/masked and backend alternatives

Sources: `/private/tmp/glyph-native-irq-rom-upper-proof-20261021.md`, `/private/tmp/glyph-native-mode-destination-irq-upper-proof-20261021.md`.

Configurator/recovery FS upper348 incl pads; mode-destination union456 (round512) incl pads; core1 IRQ68. noInterrupts16 prologue can coexist before CPSID; after PRIMASK no new maskable IRQ. Flash SDK40+ROM88=128 below LFS callback is masked alternative.

Required proof: Carry exact source-selected priorities/handlers/class callbacks/endpoint-owner invariants and B0/B1/B2 ROM domain into final ELF. Alarm336, SIO116, hardwareUSB240 are alternatives; SysTick and priority0 GPIO do not mutually nest. Do not stack entire IRQ chains onto masked flash or blindly use a conservative union as feasible overflow witness.

## Final disposition

All original numeric caps remain unchanged, including usable2048 per core, layout-new-static512 together, diagnostic512 separately inside totals, added-static12288/whole-static199632, native7800/view560/frame144/validation256, filesystem524288/reserve16384 and20 complete profiles. Source aggregate frame caps and emitted whole-function frames are different quantities and must both be assessed honestly.

The earlier interrupted accounting numbers remain partial evidence; this report does not promote them to a complete review or assert their totals without an exact new chain derivation. New repair needs exact clean SHA/tree, final linked object/source/generated/dependency/flags correspondence, meaningful changed-path/fault/trace/lease regression, both-ABI layouts, complete structural bound, fresh independent final source/resource review and exact artifact custody. Then a concrete reviewed hardware packet still requires direct owner device approval and exact human HEP PASS before integration. Timing/highwater NOT_MEASURED; Nunchuk NOT_TESTED; root cause UNPROVEN. No handoff, controller acceptance, limit increase or support-domain reduction is approved. This finite review ends here.
