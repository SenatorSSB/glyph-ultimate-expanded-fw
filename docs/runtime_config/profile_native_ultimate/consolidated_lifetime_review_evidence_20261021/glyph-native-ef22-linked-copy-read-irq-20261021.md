# Exact ef22 linked correspondence appendix: copy/read/CDC IRQ,2026-10-21

The affected caller/callee/IRQ frames and branch predicates in the historical mixed-object copy/read and queued-CDC reports correspond to the supplied **exact engineering ELF**. Their numeric findings remain unchanged: copy2308, existing-source read2168, published-source read2200 and CDC IRQ340. Historical reports were not rewritten. These are qualified source/linked-stack accounting findings, not observed physical overflow, device acceptance, implementation authority or a whole resource PASS. Whole P1 remains OPEN.

## Artifact and source verification

Candidate ef22f6107ec1fb26e8a25ab1f7345f301952b237, treeaea9a57e47d717eee9332aceda3cd6f50d44df92. Independently rehashed the custody firmware.elf:5592128 bytes, SHA256 `5d3f25e40b1b3765f891f3bc8f3fa16ff3c67483104c6f08f609a8569bede78f`. The exact custody path is pinned in the adjacent JSON. Independently verified disassembly/symbols/sections/ELF-header bytes against elf_inspection_pins.json. Source reads via gitshowef22 for all five frozen TUs match the9cff analysis-object source hashes. The earlier probe's stale head/FIRMWARE_VERSION metadata is not used to identify this linked artifact. Current literal-loaded frames and calls below are read from this ELF, resolving that earlier linkage qualification for these paths.

Selected LittleFS/SDK source hashes match both historical input pins and this build's dependency provenance inventory. The build dependency file records no compiler .d files and therefore a broad source/prebuilt-library inventory fallback; this appendix does not mislabel that inventory as precise dependency tracing. Build/custody records remain the root's build evidence. The affected branch/body sources are unchanged. No source/SDK/build/device/Git mutation or experiment was performed for this inspection; private/tmp analysis evidence only.

Exact nm symbol sizes define function extents, including template names. The extraction accounts for PUSH/immediate SUBSP and literal-loaded negative ADDSP. In hash_file, ADDSP at1001e412 uses literal−620 plus36 saved bytes=656; a push/immediate-only parser would incorrectly report36. Internal BL instructions into the same symbol are compiler local control flow, not recursive C entry; the read-open witness occurs before those later local cleanup branches. The adjacent frames JSON preserves exact calls/stack instructions. Wrapper __wrap_main at1001da44 uses no stack allocation and restores PRIMASK before tail BX to main; it contributes no retained frame under setup.

## Current addresses and frames

| Current function / route | Address | Retained own bytes |
|---|---|---:|
| main |1003ff08|48|
| setup |1002f2f4|136|
| CaptureLegacySource |1001fd34|16|
| PrepareCaptureSource |1001fc10|64|
| ExecuteCaptureSource |1001fc8c|96|
| LegacySourceIdentity |1001f594|280|
| copy_checked_file constprop |1001e104|504|
| hash_file |1001e400|656|
| CheckedStorage::Open |1001c5dc|88|
| lfs_file_open |100163c8|16|
| lfs_file_rawopencfg |1001544c|80|
| ordinary compaction/program subtree |10014dc8 entry|1008 total|
| read-open definite prefix |1001c5dc→100102c4|668 total|
| noInterrupts |100406a8|16|
| SysTick installed RP2040 handler |1003fe54|12|
| default-serial unique-ID helper |10043850|8|
| memcpy AEABI ROM wrapper |10043730|0 tail BX|
| memset ROM wrapper |10043724|0 tail BX|
| SDK flash_range_program / erase |20000ca0 /20000c28|40 each|

No affected own-frame change was found relative to the frozen/mixed calculations. Many SDK/LFS/USB function addresses are unchanged; application/helpers and some SDK wrappers shifted. Historical stop addresses must not be used as current addresses.

## Copy branch correspondence

setup calls Capture at1002f79c, before its initialize_backends call1002f5fa in the alternative later normal-initialization flow. Capture calls Prepare at1001fd4a; after it returns, the NeedsCopy branch calls Execute at1001fd6c. Execute's Remove call1001fc9e returns before copy call1001fcc2. Copy input Open is1001e170; output Open is1001e208, with full504 frame and input object retained. Its input/output closes remain later at1001e2ec/1001e30e, and other error cleanup paths do not alter that prefix.

The exact SDK new-entry create branch still calls orphaningcommit at10015604. Subsequent ordinary chain remains orphan160→reloc136→split192→compact136→traverse216→commit callback72→commitprog72→flashprog24=1008. commitprog's cfg.prog BLX remains10010e1e; there is no extra bd_flush frame. Source-installed callback/prog targets remain lfs_dir_commit_commit10013520 and LittleFS lfs_flash_prog1000eba8. Both source installation and linked call frames correspond. The historical healthy-state predicates remain necessary: absent temp Remove returns without a metadata commit after clean consistency; input is read-only; metadata append is full/insufficient and enough live metadata fills the256-byte program cache while traverse/callback frames remain; global reserve still passes. No initial positive orphan/MOVE is assumed. The appendix preserves the source-level state-feasibility qualification; it adds no mounted fault-image witness.

Current noInterrupts allocates16 at100406b4 and leaves PRIMASK clear until CPSID100406be. Thus the same pre-mask source witness is retained: main48+setup136+Capture16+Execute96+copy504+Open88+fileopen16+raw80+ordinary1008=1992, plus noInterrupts16 plus boot descriptor/SysTick300=**2308**. Once masked, flash is a separate alternative; SDK40+official ROM<=88 remains128 below the retained flash callback, not an extra IRQ peak.

## Read/closed-object correspondence and direct hash contexts

Identity closes its source via CheckedStorage::Close at1001f67c and calls hash at1001f6ae while SP still includes its full280 frame. Its epilogue/destructor checks remain after hash returns. The hash read Open at1001e4a4 retains656. The exact read prefix remains Open88+fileopen16+raw80+find96+fetchmatch152+find_match72+bd_read64=668, stopped after the100102c4 prologue. The existing nonempty NAME comparison reaches it before cache/ROM choice. Its associated upper688 adds read callback8+ROM<=12; that is still an upper, not the unconditional prefix. ROM wrappers remain stackless and the original all-B0/B1/B2 memory bound applies; target ROM revision was not observed.

Prepare calls Identity at1001fc68; Execute calls it at1001fd08. No CheckSavedConfig/close/Prepare sibling is added beneath Execute's hash. With boot184/Capture16 and the same300 feasible boot IRQ: Prepare64+Identity280+hash656+lookup668 gives**2168**; Execute96+Identity280+hash656+lookup668 gives**2200**, with the original existing/published-source branch predicates. Source-available stale but valid snapshot still reaches the first lookup before digest comparison, so equal hashes are not a prerequisite for the existing-source prefix.

All actual direct entries to this static hash_file are exactly:

| Linked caller | Call address | Current conservative total with read-open688 and boot IRQ348 |
|---|---|---:|
| PrepareCaptureSource, first source hash |1001fc38|1956|
| ExecuteCaptureSource, copied-temp hash |1001fcd6|1988|
| LegacySourceIdentity |1001f6ae|2236 under Prepare /2268 under Execute|

There is no address-taking/indirect source use of the static helper or additional linked external direct caller. Its other source I/O siblings remain smaller: constructor Stat uses72+56+the same directory lookup=632; read uses CheckedRead16+public read24+flushedread96+CTZfind64+bdread64+read8+ROM12=284 (inline getslice alternative292); read-only close has returned flush/free alternatives below688. Default cfg attrs are empty and hash's handle is read-only, so no writing/dirty commit or consistency path is acquired by read/close. Inlined SHA working arrays are already within656; its memcpy branches add at most12 and are separate from Open. Thus the two direct non-Identity contexts fit the current conservative boot allowance without a hash-body phase change. This does not prove a whole class/candidate PASS.

This favors checking the smaller Identity-only returned-validation phase before contemplating a separate hash-body phase. If its actual emitted wrapper were8 and the280-byte check/File/destructor phase fully returned before the unchanged hash, the largest current hash context's upper would be2268−280+8=1996. That is a conditional compiler target with52 bytes margin, not an implemented or approved result. The validation helper's own frames/failure/destructor/explicit-close order, workspace lifetime and all31 paths still require their actual proposed source/object proof. No simultaneous speculative adoption of both alternatives is justified by this exact helper inventory.

## Current interrupt and transport correspondence

Boot still initializes TinyUSB before setup: main's TinyUSB_Device_Init call is1003ffc6. The non-RTOS path installs the SysTick handler through10040012 with handler pointer1003fe55 and writes CSR7. setup's Capture precedes all backend installation/serial overrides. Default serial remains global initialized NULL. Its linked path is task8+tud_task112+stringCB8+serial80+portID8+uniqueID8=224. New stop10043852 is after unique-ID push and before memcpy10043856. Outer exception32 plus current SysTick12+exception32 gives the same **300** witness, without ROM/pads. SysTick priority/source rules are unchanged; no larger GPIO source is installed at these pre-backend boot phases.

The queued-legacy-response CDC transport source body matches ef22, and all linked C frames remain task8+tud_task112+cdcd40+flush24+edpt_claim8+tu_edpt_claim16+mutex_timeout24+mutex_block32=264. Current USB functions retain addresses10007770,10009534,10007c60,10007928,10009e80,1000ab1c,20000b20,20000aca. Deepest pre-mask point20000acc and CPSID20000ade are unchanged. Current SysTick12 at1003fe54 gives **264+exception32+44=340**. No timeout-contention44 or FIFO read mutex is added. The legacy GET_CONFIG COBS end/serviceTx/queued-delimiter, independent RX OUT and liveness_tracefalse predicates from the separate source-witness report remain unchanged by the exact build. Those predicates distinguish the feasible340 from safe348.

The independent31-path reviewer owns Update/Duplicate/Reconcile/legacySET foreground totals. Its current linked loop is32 (1002e2a4), replacing the preliminary object40 for that separate class; reviewer reports updated Update/Duplicate1696+premask16+340=2052. This appendix independently confirms loop32 and IRQ340 but does not duplicate the reviewer's full filesystem co-liveness proof. Phase3 Reconcile uses the confirmed boot300 before backend installation. No hardware timing/highwater or physical-overflow claim is introduced.

All current source/ELF correspondences above apply only to this exact ef22 artifact. A subsequent authorized lifetime repair needs new affected source/object/linked accounting and the ordinary exact candidate gates. Static-RAM build results are not a substitute for whole-stack closure or hardware acceptance.
