# Exact ef22 finite LittleFS inner stack upper proof

This is a conservative finite **inner upper**, not a whole-resource PASS, device measurement, or proof that every upper branch is simultaneously feasible. It closes the fixed LittleFS/SDK descendant graph for the CheckedStorage operations below. The application visitor passed to Enumerate is an explicitly retained caller obligation, with its sole actual target identified below. No source/SDK/build/device/Git mutation or new image was performed.

Candidate `ef22f6107ec1fb26e8a25ab1f7345f301952b237`, tree `aea9a57e47d717eee9332aceda3cd6f50d44df92`; ELF 5,592,128 bytes, SHA256 `5d3f25e40b1b3765f891f3bc8f3fa16ff3c67483104c6f08f609a8569bede78f`. The ELF was independently rehashed. Exact own frames/calls come from symbol extents and instruction addresses, including literal-loaded negative SP allocations, not an angle-bracket function-name parser. All LFS/CheckedStorage direct external tail edges were checked: none exist. The source uses the pinned Arduino-Pico 3.6.3 global LittleFS configuration. Application source was read from Git ef22 rather than the writer's changing checkout. Final candidate must independently preserve these bodies, callbacks, compile-time configuration, frame envelopes and source predicates or be recomputed.

## How to apply the numbers

`U` is the maximum inner stack at a potentially interruptible instruction, without IRQ activation. It includes the 16-byte noInterrupts frame before CPSID where applicable. `M` is a separate maximum inside a known masked flash/allocator descendant. A dash means no masked descendant in that refined path.

**caller retained + max(U + applicable route IRQ allowance, M)**

Do not add another pre-mask16 to U. Do not add IRQ atop M or add M after U. Caller retained includes automatic File objects and any application wrappers/adapters still alive. IRQ allowance must match actual lifecycle/descriptor/backend installation: prior Configurator348, supported mode-save408, and appropriate boot/default bounds are separate source-scoped certificates. Their feasible lower witnesses are not interchangeable with conservative upper allowances.

The graph's historical-compatible E column is only a structural comparison envelope through the flash callback entry (and keeps conservative allocator alternatives). It is not a universal feasible witness. The U/M columns below are the applicable upper certificate.

## CheckedStorage inner bounds (bytes)

| Entry and phase | U | M | Predicate |
|---|---:|---:|---|
| Open (writable generic) | 1448 | 1560 | Includes initial forceconsistency, new-entry commit, generated repair and cleanup alternatives |
| Open new entry AFTER initial consistency returned | 1384 | 1496 | Excludes that initial force64; keeps entrycommit and any returned generated deorphan |
| Open read-only | 588 | 320 | O_RDONLY, default attrs0; excludes forceconsistency/create/truncate |
| Read generic handle | 692 | 600 | May flush a previous WRITING phase before reading |
| Read read-only handle | 292 | — | No previous write, so no WRITING flush |
| Write | 708 | 616 | Includes flush/outlining/CTZ extension/relocation/allocator alternatives |
| Seek generic handle | 700 | 608 | May flush WRITING; safe even where caller has a tighter read-only path |
| Sync generic DIRTY/WRITING | 1256 | 1368 | Data flush then metadata commit; returned generated repair included |
| Sync clean handle | 168 | — | Neither WRITING nor DIRTY; cache-drop-only flush |
| Close generic DIRTY/WRITING | 1264 | 1376 | Implicit Sync plus free; returned generated repair included |
| Close read-only handle | 176 | 200 | Default attrs0 and no writes |
| Close after successful Sync | 176 | 200 | No intervening write/dirtying event; successful Sync cleared DIRTY and WRITING |
| Close ERRED handle | 88 | 200 | rawsync exits before flush/commit; still releases cache |
| Stat | 532 | — | Lookup/fetch/find comparator only |
| Remove | 1384 | 1496 | Includes inlined forceconsistency and generated repair |
| Rename | 1464 | 1576 | Includes inlined forceconsistency and generated repair |
| Capacity | 404 | — | fs_size/rawtraverse, fixed callback; no metadata write |
| Enumerate internal filesystem work | 676 | — | Excludes the explicitly supplied application visitor budget |

Writable TRUNC of an existing file performs consistency first and marks the file DIRTY; it does not create the new entry in that Open. A later Sync/Close can commit. New-entry Open commits the creation only after its first consistency call has returned; successful initial Remove is therefore not a blanket later-compaction exclusion. Generic Open retains both alternatives using max, without adding the earlier consistency activation to the later entry commit. The post-consistency new-entry row still allows generated repair and does not assert that its deeper branch is a currently feasible application history.

Read-only and clean-close refinements are source flag predicates, not assumptions that the whole filesystem is pristine. Other pending global state does not make rawsync force consistency on a clean handle. A failed Sync can set ERRED; the ERRED row applies only if that flag is actually known. Otherwise use the generic row. Public Read on an arbitrary writable handle retains the flushing subtree; a read-only input File cannot acquire WRITING through these reads.

## Fixed source call graph and nesting

| Function (exact own frame) | U | M |
|---|---:|---:|
| `lfs_dir_commitprog` (72) at `0x10010d4c` | 112 | 224 |
| `lfs_dir_commit_commit` (72) at `0x10013520` | 184 | 296 |
| `lfs_dir_traverse.constprop.0` (216) at `0x10010a6c` | 400 | 512 |
| `lfs_dir_compact` (136) at `0x10013914` | 536 | 648 |
| `lfs_dir_splittingcompact.constprop.0` (192) at `0x10013bbc` | 728 | 840 |
| `lfs_dir_relocatingcommit` (136) at `0x1001443c` | 864 | 976 |
| `lfs_dir_orphaningcommit` (160) at `0x10014dc8` | 1024 | 1136 |
| `lfs_fs_deorphan` (176) at `0x100151cc` | 1200 | 1312 |
| `lfs_fs_forceconsistency` (64) at `0x100153cc` | 1264 | 1376 |
| `lfs_alloc` (120) at `0x100127ec` | 356 | — |
| `lfs_dir_alloc` (136) at `0x10012174` | 372 | — |
| `lfs_fs_rawtraverse.constprop.0` (96) at `0x100118e0` | 332 | — |
| `lfs_file_relocate` (80) at `0x10012ddc` | 436 | 344 |
| `lfs_file_flushedwrite` (104) at `0x10012f94` | 540 | 448 |
| `lfs_file_flush` (112) at `0x1001332c` | 652 | 560 |
| `lfs_mount` (120) at `0x10015940` | 356 | 264 |

The largest metadata spine is orphaningcommit160 → relocatingcommit136 → splittingcompact192 → compact136 → traverse216 → commit callback72 → commitprog72 → flash callback. Through callback own24 it is **1008**. The U branch adds pre-mask16 =1024; the M branch replaces callback24 with callback24 + SDK flash40 + official ROM88 =1136. This is the same ordinary fragment, now compared against every sibling/helper branch rather than assumed globally maximal.

Deorphan176 adds once: U1200/M1312. Forceconsistency64 adds once: U1264/M1376. For example generic Open adds CheckedOpen88 + public file_open16 + rawopencfg80, giving U1448/M1560. Rename already inlines forceconsistency/demove in its own240: CheckedRename24 + rename240 + deorphan176 + ordinary1024 =1464. **Do not append an extra force64 to Rename or Remove.** Their direct deorphan child is already present in the exact emitted functions.

`lfs_dir_commit` first calls orphaningcommit and returns from it, then may call deorphan(false). The two ordinary commit activations do not remain co-live. `lfs_fs_deorphan` calls orphaningcommit directly for full/half-orphan repair; it does not call the commit wrapper that would reenter deorphan. Its restart is a goto to the same activation. `lfs_dir_orphaningcommit` propagates relocation through a while-loop of relocatingcommit calls; it never calls deorphan. Dropped-parent handling, parent updates, predecessor updates and pending-move replacement similarly reuse that one frame. Therefore no orphaningcommit→deorphan→orphaningcommit recursive C cycle exists.

Forceconsistency's demove implementation may itself commit and run returned repair, then the subsequent deorphan(true) runs after it returns. There is one retained force64, not MOVE64 + another force64 or two live deorphan176 frames. The source-generated/partial-repair branches are conservatively included after earlier writes; successful consistency is not used as proof that every future recovery branch is unreachable.

`lfs_dir_traverse` source has a bounded explicit stack (`LFS_DIR_TRAVERSE_DEPTH-1`), contained within exact own216. MOVE/filter continuations push that explicit array; they do not create additional C traverse frames. Its actual callbacks are commit_commit72, commit_size0, and traverse_filter12. Directory depth, number of foreign entries, split attempts, retry/CRC loops, CTZ loops, allocator scans, mlist walks and deorphan restart affect work/time, not C nesting. No claim about timing or guaranteed termination under arbitrary corruption is made.

Allocator `lfs_alloc120` already contains the compiler-inlined rawtraverse scan. It directly calls fetchmatch(NULL); adding another rawtraverse96 there is incorrect. dir_alloc136 similarly contains its own scan. The separately emitted fs_rawtraverse96 is used by Capacity. CTZ traversal invokes only the inlined lookahead/count callbacks in these actual contexts. File relocation80 → alloc120 → fetchNULL152 → bd_read64 → callback/divider20 =436 dominates its unmasked program and direct erase siblings. file_flushedwrite104 and file_flush112 can retain it, giving540/652. Their flush/read/write, cache copy, allocate, erase, prog, verify and retry operations are represented by max over exact edges; separate stages are not summed.

The CRC/sync branch is also included: commitcrc104 → bd_flush72 → bd_read64 → read/divider20 =260 unmasked; masked104+72+152=328. Under compact136 both are below its traverse→commit path. `commitprog72` has already inlined its buffering/prog/flush parts and direct cfg.prog call; adding bd_prog40 + bd_flush72 again under that callback would double-count source helpers absent from the linked call edge.

## Callback/context closure

fetchmatch has three separately resolved contexts: NULL under mount/alloc/pred/plain fetch/rawtraverse; find_match72 under dir_find96; parent_match40 only at orphaningcommit call10014f74 and deorphan call100152a2. The larger find matcher is not inserted beneath every NULL fetch. Source directory traversal uses a single fetch activation for each loop iteration.

Pinned global cfg callbacks are exact linked read1000eae8 own8 → ROM memcpy<=12, prog1000eba8 own24, erase1000ef24 own24, sync1000e644 leaf0. Read/sync/program/erase return0 as installed. Program and erase reach noInterrupts before the actual flash helper and hold masking through the SDK/ROM window. The subsequent reenable/mutex-exit branch is included in U40 for the whole callback and is smaller than the masked152. Mutex waits and multicore FIFO loops have fixed C depth; no arbitrary callback enters LittleFS there. SDK aligned-address assertions are excluded by the fixed 256-byte program /4096-byte erase geometry, rather than by assumed luck. NoInterrupts nesting15 panic is outside this graph's bounded ordinary nesting.

Global LittleFS's shared_ptr remains a live owner while CheckedStorage copies its implementation pointer. Thus the copy destruction is not a last-owner virtual destructor/dispose call. mount16 and the inlined Capacity variant include their emitted own frames; their unselected shared_ptr dispose callbacks are source-excluded. Actual CheckedStorage fault-hook calls are absent from this engineering ELF. A final build that includes an armed callback must add its precise target/phase budget; synthetic host failures are not evidence of target transient reachability.

All actual LFS integer divisions have positive denominators: read/prog/cache256, block_count128, CTZ block_size−8=4088, wear divisor((16+1)|1)=17, and constant powers of two. lfs_aligndown/up only receive those fixed alignments. No on-disk value is used as the divisor. The exact hardware-divider wrapper selects its save20 branch on SIO divider DIRTY, even in foreground, and that20 is counted. Its extra divide-by-zero8 branch is source-excluded by these denominators. The four-byte cross-region veneer temporary is popped before the tail target; max(4,20)=20 rather than24. Linked lmul4 and string leaves strlen/strchr0, strspn/strcspn/strncpy/memcmp<=12 are included. ROM CLZ/CTZ/popcount are stackless in the independently pinned official B0/B1/B2 release assets, including their internal branch labels; wrappers use BX with no frame. memcpy<=12, memset<=8, flash<=88 are reused from the prior pinned ROM proof, with licenses/provenance retained. This is a compatibility envelope for those published ROM revisions, not a target observation.

## Read/enum/mount phase details

Read-only lookup is CheckedOpen88 + public16 + raw80 + dir_find96 + fetch152 + findmatch72 + bd_read64 =568 before the leaf; callback/divider20 gives **588**. Stat72 + public56 + find96 + fetch152 + matcher72 + bdread64 +20 =532. These sums explicitly correct the earlier100-byte arithmetic excess; see the separate preserved read-sum erratum. Generic Read692 is a different WRITING-handle path and must not be substituted for the pure read292 path or for Open588.

Enumerate internal upper676 is own216 + dir_open56 + find96 + fetch152 + find_match72 + bdread64 +20. Each dir_read and visitor returns before the next iteration. The API permits a supplied visitor, so the complete formula is **U=max(676,216+V_U)** and **M=216+V_M** if the actual visitor has a masked child. No generic arbitrary-function V bound is claimed.

The only actual mounted-store visitor is CollectGarbage's lambda at100260a0 own40. It parses the fixed format `ultimate-%8x-%8x.%3s%n` using siscanf144→__ssvfiscanf_r680, calls strlen/strcmp, Protected (no filesystem call), then sniprintf with fixed `/%s`. The format excludes floating conversion. The application libc subtree is expressly handed to the final caller inventory, **not silently bounded by676**. No visitor reenters storage: CheckedRemove is invoked only after Enumerate has returned. Therefore there is no LFS→visitor→LFS C recursion or retained Enumerate216 on the later Remove branch.

Mount has own120, fetchNULL152, bdread64, leaf20 =356; its masked allocation/free alternatives264 are smaller. LittleFSImpl::begin48 with autoformat=false adds48 =404. Mount loads global state but does not perform deorphan/demove recovery. Startup launcher/constructor retained prefixes and interrupt installation are owned by the separate startup proof. Autoformat=true is a different branch and is not certified by the begin404 row.

## Scope and residual obligations

The machine-readable DAG solves96 contextual/fixed nodes with zero C call cycles. Broad valid admitted FS histories are bounded without requiring pristine initial state or proving every later generated repair history impossible. This does not reinstate the withdrawn direct Configurator initial-orphan witnesses: lifecycle35e8/543 erratum remains authoritative; upper reachability is intentionally overapproximated. It also does not establish any new physical overflow witness from a test-only fault, invalid current root that later magically succeeds, arbitrary corruption or unsupported callback.

All caller totals, actual Enumerate visitor libc target closure, phase-specific IRQ predicates and final candidate source/ELF correspondence remain final-inventory duties. Resource limits, original compatibility, NOT_TESTED hardware status and whole-resource OPEN status are unchanged. No source/architecture/workspace conversion is requested by this proof.
