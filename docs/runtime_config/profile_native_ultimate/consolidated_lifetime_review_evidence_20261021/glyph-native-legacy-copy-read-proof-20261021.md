# Frozen9cff legacy copy/read retained-path evidence,2026-10-21

The new-entry output Open can reach the ordinary compaction/program stack after a successful absent-temp Remove. The frozen copy path yields a **2308-byte source-accounting composition** including a concrete boot interrupt prefix. Separately, the existing-snapshot LegacySourceIdentity→hash read-open path yields **2168 bytes** using a668-byte lookup prefix before any cache/ROM branch. These are source/compiled-frame accounting results under explicit predicates, not device observations, physical-overflow measurements, a final linked candidate bound or a whole resource PASS.

## Frozen inputs and exactness

Checkpoint9cff6df7dac544f8d88237f37cd62c26276c690b, tree9a18bd179820c47bdc1a38f1a1afed7b28005f6f. Independently read gitshow9cff for all five supplied TUs; every source hash matches `/private/tmp/glyph-native-frozen-boot-capture-20261021/manifest.json`, and every object hash matches its .o. The manifest's embedded head750297 and FIRMWARE_VERSION3b792fd7-DIRTY describe prior probe metadata, not a final9cff firmware ELF. The exact compile argv is retained; these are preliminary production-O3 analysis objects. FIRMWARE_VERSION occurs in ConfiguratorBackend device-info handling, not Persistence/config/setup/mode_selection bodies examined here. Final actual build defines, linked call reachability and generated frames still require exact candidate verification.

The SDK/LittleFS/CheckedStorage frames and IRQ instructions come from the pinned bcb ELF SHA256 `3f43081cec177763abf9f1955f8a3686faa39fa4ca660a5de174a2d70ca62884`. New caller frames come from the frozen9cff O3 objects. This is explicitly a mixed source-corresponding analysis composition, not a newly linked ELF. The three helper bodies copy_checked_file, hash_file and LegacySourceIdentity are byte-identical between bcb and9cff when comparing their brace-delimited bodies; only the permitted noinline annotations outside those bodies differ. Exact body hashes and input pins are adjacent. No source, SDK, Git, build cache, firmware or device mutation occurred; only private/tmp evidence was written. No new fault image or firmware build was made.

## Copy output creation: absent Remove does not normalize metadata

ExecuteCaptureSource first removes `/ultimate-migration.tmp`, then calls copy_checked_file. CheckedStorage::Remove converts LFS_ERR_NOENT to Outcome::Ok. lfs_rawremove invokes forceconsistency, then a missing-name lfs_dir_find returns before any delete/commit. Choose a healthy, consistent filesystem with no pending move/positive orphan, absent temp, a valid source Config and the required global free reserve. The consistency call returns without mutation. This witness needs neither a positive orphan nor a MOVE branch. Other admitted repair histories remain part of the broader gate; this is a sufficient ordinary-state path.

copy_checked_file constructs input(from,r) before output(to,w+). The input open is read-only and does not consume directory log space. Output CheckedStorage::Open sets O_CREAT|O_TRUNC|O_RDWR. In lfs_file_rawopencfg, forceconsistency is a completed sibling before lookup; an absent name with a usable id takes the create branch at lfs.c2884 and commits CREATE, REG-name and INLINESTRUCT attributes. That ordinary commit calls orphaningcommit regardless of initial orphan count. A valid metadata pair with insufficient append space or dir.erased=false enters splittingcompact/compact. An absent temp Remove provided no prior commit that would guarantee append room. Global free bytes/reserve do not imply remaining append bytes in a specific metadata pair.

The relevant healthy metadata-state predicates are: root directory log near/full so create must compact; enough live metadata (>one256-byte program cache) so a traverse callback fills the cache and invokes cfg.prog while its callback frames remain; enough global space to pass AdmitCaptureSource and the fixed reserve. A root with ordinary unrelated live entries and ordinary old metadata commits can satisfy these predicates without corruption. Compacted live metadata may remain comfortably below block capacity while the append log is full. ProfileStore Begin can take its valid phase2 control/root read-only Complete branch before Capture, so no earlier bootstrap write is mandatory to normalize that pair. This is a source-level feasibility argument, not a newly constructed/mounted image witness or an assertion that every admitted image takes the branch.

Exact retained ordinary program chain:

| Body | Bytes | Exact bcb address / callback |
|---|---:|---|
| lfs_dir_orphaningcommit |160|10014dc8|
| lfs_dir_relocatingcommit |136|1001443c|
| lfs_dir_splittingcompact |192|10013bbc|
| lfs_dir_compact |136|10013914|
| lfs_dir_traverse |216|10010a6c|
| lfs_dir_commit_commit |72|10013520|
| lfs_dir_commitprog |72|10010d4c|
| LittleFS lfs_flash_prog |24|1000eba8|
| Total |**1008**|before noInterrupts child|

The traverse callback is source-installed lfs_dir_commit_commit; cfg.prog is the exact LittleFS lfs_flash_prog installed in the global mount. commitprog already inlines the relevant bd_prog/flush body and invokes cfg.prog directly at10010e1e. Do not append a separate bd_flush72 or bd_prog40. Traverse uses its explicit bounded internal stack, not an added recursive C frame. No forceconsistency/deorphan/MOVE frame remains under this ordinary create commit.

Frozen retained prefix: main48 + setup136 =boot184; CaptureLegacySource16; ExecuteCaptureSource96; copy504; CheckedStorage::Open88; lfs_file_open16; lfs_file_rawopencfg80; ordinary program1008 =**1992**. Copy's constructor is inlined into504; do not append CheckedStorageFile constructor56. Its input/output objects both remain live at output Open; their explicit closes are later. Preparation64, CheckCaptureInput280, initial Remove and its lookup/consistency, later hash/Rename/Identity are returned siblings and are not added here.

At noInterrupts1004177c the16-byte prologue is allocated, with PRIMASK still clear until CPSID10041786. The boot interrupt witness below can preempt there:1992+16+300=**2308**, without ROM/padding assumptions. Conservative boot IRQ348 instead gives2356. After CPSID, new maskable IRQs cannot be appended; compare masked SDK flash40+ROM<=88 as a separate alternative. This result is a static source-path finding subject to final linked correspondence, not a measured physical overflow.

## Read-open:668 definite prefix,688 retained upper

For read mode, rawopencfg skips forceconsistency and does not create/truncate. Existing nonempty `/ultimate-migration.src` NAME entries are compared by lfs_dir_find_match during lfs_dir_fetchmatch. The local callback is source-bound by lfs_dir_find. The match helper invokes its inlined bd_cmp loop with diff=min(nonempty requested name,nonempty entry name)>0, so lfs_bd_read is reached even if cache hits. At the64-byte bd_read prologue, before the cache choice or ROM call, these frames are live:

CheckedStorage::Open88 + lfs_file_open16 + rawopencfg80 + dir_find96 + fetchmatch152 + find_match72 + bd_read64 =**668**.

Relevant exact functions are1001c558,100163c8,1001544c,10011a3c,10010e64,100106dc and100102c4 respectively. lfs_file_rawopen is inlined in public open; no additional rawopen wrapper is added. The path has no outer foreground mask, no write consistency prefix, and no arbitrary virtual/callback target. Constructor's subsequent Stat is a sibling after Open returns, not retained here.

The earlier688 inventory is a read-open upper:668+LittleFS read callback8+ROM memcpy<=12. Reaching its additional callback requires a cache miss; actual memcpy stack also depends on length/alignment/ROM revision. A source-valid name crossing a256-byte cache boundary can make find_match re-read an earlier page after fetchmatch's CRC scan leaves the later page cached; the configured read fills aligned256-byte buffers. However neither that construction nor ROM12 is needed for the definite668 witness, and this report does not present688 as an unconditional/observed lower bound. Allocation/get-structure/numeric-helper alternatives are separate smaller read-open siblings under the existing finite SDK/helper bounds.

## Closed automatic File remains live under Identity's hash

LegacySourceIdentity constructs a local CheckedStorageFile, CheckSavedConfig returns, and source.close() returns before `return hash_file(...)`. Explicit close releases its native handle; the C++ object's lifetime still extends to scope exit after the hash call. The frozen Identity prologue is280 bytes (36 saved registers+244 locals). Its hash call relocation is section LegacySourceIdentity+0x11a, while SP remains lowered; only afterward does the destructor/check/epilogue run. hash_file's prologue allocates656 (including register-loaded620-byte SP adjustment). Its read Open call is section hash_file+0xa4 while the full656 remains allocated. Do not use a parser that counts only immediate SUBSP: that would misread hash as36.

Therefore Identity280+hash656+lookup668 are actually co-live. CheckSavedConfig80, its CRC/read scratch and explicit close24 have returned, so none is appended to the hash prefix. Likewise hash.Final's inlined scratch belongs to the656 frame, not an extra sibling child during Open. CheckCaptureInput's separate280-byte source-check phase returns before Prepare's first hash and is not retained there.

Two frozen boot branches:

| Call branch | Foreground using668 | +boot feasible300 | +boot upper348 using688 |
|---|---:|---:|---:|
| Capture16→Prepare64→existing-src Identity280→hash656→lookup668, plusboot184 |1868|**2168**|2236|
| Capture16→Execute96→published-src Identity280→hash656→lookup668, plusboot184 |1900|**2200**|2268|

The first branch requires a valid current/legacy Config of allowed length, existing snapshot, available storage and valid snapshot CheckSavedConfig. Snapshot equality is checked only after Identity returns, so equality is not required to reach the lookup; a valid stale snapshot also executes it then refuses. The second branch additionally requires completed copy/hash/Rename publication and Identity validation; it is a separate conditional route. No Prepare64 is added under Execute96. The existing-snapshot branch alone provides the source-accounting finding without relying on newly published name/cache placement. Bare hash under Execute without Identity has1640 foreground using688; with boot upper348 it is1988. The extra retained closed Identity File is material.

## Boot interrupt predicate and scope

SDK main calls TinyUSB_Device_Init before setup. The initialized global TinyUSBDevice has STRID_SERIAL=NULL and iSerialNumber3. USB task IRQ is installed/enabled at external default0x80; rp2040.begin enables core0 SysTick at reset priority0. Capture/Begin/reconciliation occur before initialize_backends, so no Switch serial override, console GPIO IRQ installation or backend CDC/viewer TX producer is needed. Standard host GET_DESCRIPTOR STRING3 is handled by the global descriptor path, including before class/backend initialization. Its finite retained prefix is task8+tud_task112+stringCB8+getSerial80+portID8+uniqueID8=224, stopped at uniqueID1004491a after push before memcpy. Outer exception32 and nested SysTick(12 C+32 exception)=44 give **300**, no ROM child or alignment pad. SysTick calls no USB code. Hardware USB only queues task work then returns; equal0x80 IRQs do not nest. No foreground USB Guard or endpoint lock is held on these filesystem paths.

The same predicate applies to Begin→ReconcileTransaction phase3 control2/aborted-checkpoint writes before backend initialization: preceding read phases return, and the write's noInterrupts pre-mask prefix remains interruptible. Its foreground calculation belongs to the independent31-class reviewer. The348 boot allowance from the existing finite USB/ROM proof is a conservative upper;300 is the concrete before-ROM descriptor/SysTick prefix used above. No host/device timing or highwater observation is asserted.

## Materially different lifetime hypotheses, not authorized implementation

At the unchanged boot184/Capture16/Execute96 prefix, merely retiring/reusing copy's scratch64 or splitting transfer arithmetic cannot suffice. The two simultaneous automatic CheckedStorageFile objects occupy176 each. Even idealizing copy504 down to352 with no registers/other locals gives1992−504+352+16+300=**2156**. Their ordering/ownership cannot simply be reversed: input-open precedes output creation, both handles serve the transfer, and explicit close/uncertainty/destructor fallback order is observable. A different File owner/workspace lifetime for at least one object, or sufficient retirement of another retained caller, is a materially different scope decision. Current copy's conservative2356 accounting requires>=308 bytes reduction to reach2048; the definite2308 witness requires>=260. A shared workspace would need exact synchronous core0/non-reentrancy/ownership proof and the unchanged static budget. No workspace/body conversion is permitted by the current annotation-only authority and none was attempted.

Identity has a distinct returned-phase hypothesis: complete source open/check/explicit close/destructor in a separate bounded validation phase before calling hash from a small wrapper. Explicit close alone is insufficient; the object/frame lifetime must end and the compiler must demonstrate that retirement. With a hypothetical measured8-byte wrapper replacing280, Execute's conservative2268 would reduce by272 to1996 (52 margin). This is a quantitative target, not a compiled proposal or implementation proof. Hash656 itself includes File+scratch+inlined SHA working state; scope text alone does not guarantee a smaller allocated prologue. Final changes require the named scope/authority decision, actual recipe/object evidence, complete31-path accounting, static/candidate linkage/build/custody and exact hardware gates. This report authorizes none of those changes and claims no resource PASS.
