# Frozen ef22 startup conversion-state allocation addendum — 2026-10-21

**The two named btowc/wctob malloc-NULL assertion branches are infeasible during the examined ordinary startup prefix.** This closes that specific limitation using the explicitly allowed finite heap-census alternative; it is not a generic assertion/stdio proof or whole all31/P1 PASS. The completed early-startup report/JSON/pins are preserved byte-for-byte. Exact ef22 ELF5592128 rehash remains `5d3f25e40b1b3765f891f3bc8f3fa16ff3c67483104c6f08f609a8569bede78f`. Model/effort UNKNOWN; inherited execution without override. No source/SDK/cache/Git/network/build/device mutation occurred.

## Why the census is the smaller exact proof

Both guards test allocation of the same80-byte newlib conversion-state block (`_reent+232`): btowc branches at1005f45e, wctob at1006579e. Their exact `__assert_func` uses the immutable `%s`/`%d` format at10074a52 and `iprintf`; float formatting is not selected. The linked `_write`1006a420 is a stackless return0, not Arduino/TinyUSB output.

However, exact newlib `__sinit` must obtain FILE storage via `__sfp`→`__sfmoreglue`, requesting464 bytes. A further NULL allocation returns no FILE object before `std` initializes it. I do **not** assume that allocation succeeds, infer valid FILE callbacks after NULL, or expand into corrupted-object/ROM-null-address execution. The census below proves that the original80-byte request cannot return NULL in this ordinary startup, so that error path is not an outstanding startup stack route. This is an inference from emitted allocator arithmetic and an exhaustive source/linked request prefix, not a hardware observation.

## Exact request prefix

Application reset copies `.data` and clears `.bss` before registered constructors. This resets the allocator independently of the earlier unchanged OTA stage. `heap_end.0=0`, `__malloc_sbrk_base=0xffffffff`, top size0, top pointer20005bf8, `__malloc_top_pad=0`, and trim threshold131072 are exact initial words. Both `_impure_ptr` and `_global_impure_ptr` select20005994; its misc pointer20005a7c is0. `_sbrk` initializes its break at `end=20030508` and rejects only a positive resulting break above20040000: **64248 bytes existing capacity**. No limit is changed.

| Allocation purpose | Exact call | Request bytes | Maximum calls |
|---|---|---:|---:|
| LittleFS concrete object |100100f0|236|1|
| LittleFS shared-count object |10010196|16|1|
| Read/program/lookahead caches |10015b2c /10015b46 /10015b56|256 each|3|
| Classic char numpunct cache |10045350|104|1|
| Classic char moneypunct caches |10044bcc /10044b30|68 each|2|
| Classic char timepunct cache |1005efb0|200|1|
| Shared conversion-state block |10065796|80|1|

This is at most10 requests,1540 requested bytes and1608 normalized chunk bytes using the emitted `max(16,(request+11)&~7)` rule. Mount cleanup/freeing can reduce retained allocation, not add a request site. Autoformatfalse means one mount attempt; directory count/content, orphan/MOVE state and mount/read success do not alter the three fixed cache sites. No mounted fault-image restriction is introduced.

The ELF init-table order places this locale constructor before later mode/keyboard/PIO/freeres constructors. Prior constructors other than LittleFS/mount have no heap-allocation descendants in their linked initialized-object paths. C++ iostream setup reaches its first classic-locale construction at10043d06 before FILE I/O or later ostream initialization. `_S_initialize_once` uses the static Impl at2001faac, not a new Impl allocation.

Before the wchar ctype call, the Impl installs14 distinct facet-ID objects. The small constant-argument probe resolves all14 exact addresses, each reset word0, with global ID counter0; they acquire indices0–13 inside the initially cleared48-slot array. Thus its resize/new-array, existing-facet shim/replacement and cache-deletion branches are unavailable. `_M_init_extra` and wide/cache allocations occur later. The four char cache requests in the table are the only locale allocation descendants before wchar conversion. Their constants and call locations are emitted in the pinned linked evidence, rather than guessed from C++ type sizes.

## Why these requests cannot exhaust the allocator

Every request is<=256 and normalizes to<=264, so the linked overflow/negative-size NULL guards cannot trigger. The initial positive `_sbrk_r` increment is the normalized request plus16 (<4096), with at most one initial correction of0–4095 bytes. Later positive growth uses emitted `(need+0x100f)>>12<<12` with top-pad0: for these request sizes the requested increment is at most4096. `_sbrk` is the sole break provider, is contiguous, and has no platform/device failure mode besides its exact upper-address comparison. The fixed prefix has no external break writer. Frees coalesce existing valid chunks; the131072-byte trim threshold exceeds the entire conservative prefix bound, so no unexpected break relocation is admitted.

A deliberately loose induction permits one full4096-byte growth per allocation, plus one full initial correction: **(10+1)×4096=45056 bytes**, leaving **19192 bytes** below the existing64248-byte limit. This already assumes no useful free-chunk/top-chunk reuse. At every allocation, a matching existing chunk returns success, or the bounded extension is still admitted and supplies more than the required264 bytes. Thus the induction proves the small earlier requests and final80-byte request succeed; successful allocation is the result, not a premise. Actual arena growth is not measured or claimed to equal45056.

The first `std::ctype<wchar_t>::_M_initialize_ctype` call is `wctob(0)` at10049098. Its input is not WEOF, so it establishes that80-byte block and stores it in the common reent before returning. The subsequent0–127 wctob loop and0–255 btowc loop do not free/clear it. btowc starts at100490bc only after that first loop; therefore its own NULL-pointer allocation predicate is false as well. No separate btowc heap block is counted or assumed.

## Disposition and limits

The original report's specifically named startup malloc80→assertion limitation is closed for the exact ordinary reset prefix. Its stack bounds need no added assertion/stdio frame and no budget increase. Existing source-owned callback/object and valid allocator-state prerequisites remain; arbitrary corruption/direct entry and post-NULL-FILE execution are not newly certified. No broad later-startup/main/setup heap or generic all-panic/all-stdio certificate is claimed. Whole all31/P1, final repaired-source/ELF correspondence, review/build/custody and exact hardware gates remain separate and OPEN. No target timing/highwater or physical observation was made.
