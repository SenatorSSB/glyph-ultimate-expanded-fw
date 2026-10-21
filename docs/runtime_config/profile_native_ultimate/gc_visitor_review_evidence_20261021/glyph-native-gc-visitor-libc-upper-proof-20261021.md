# Exactef22 GC visitor libc upper bound

Candidate `ef22f6107ec1fb26e8a25ab1f7345f301952b237` tree `aea9a57e47d717eee9332aceda3cd6f50d44df92`; rehashed ELF `5d3f25e40b1b3765f891f3bc8f3fa16ff3c67483104c6f08f609a8569bede78f`. Frozen Git ProfileStore source matches immutable9cff archive. Scope: the sole CollectGarbage Enumerate visitor, fixed formats and bounded NUL names.

**Conservative visitor U=996 bytes; M is absent. Actual CheckedStorage Enumerate U=max(676,216+996)=1212 bytes, M absent.** The676 value is the separate internal filesystem maximum; it does not include the visitor. Outer MountedEnumerate24, GC48 and application/IRQ prefixes remain outside this result.

Dominant conservative chain:40+144+680+64+8+40+20=996 (visitor→siscanf→ssvfiscanf→scanf_i→strtoul_r→strtoul→nonzero hardwaredivider). Programmatic DAG arithmetic verifies each parent=max-of-alternatives, including temporary tail veneers. This is an upper, not a demonstrated lower witness.

| Alternative | Bytes from visitor |
|---|---:|
| Integer scanner |996|
| Fixed /%s output |488|
| Protected leaf |72|
| strlen/strcmp |40|

## Exact constraints

- Fixed scanner format ultimate-%8x-%8x.%3s%n. Names are untrusted data arguments, never formats. x/x use width8/base16; s width3 writes ext[4] includingNUL; n stores count only. No float, wide, allocation extension, or arbitrary format branch.
- Checked Enumerate zero-initializes Entry and strncpy at most sizeof(name)-1; mount name_max31 gives NUL-terminated at most31 bytes. Visitor may drop one initial slash. After scan it requires used==strlen(name)==30; output /%s therefore at most31+NUL into path34.
- siscanf initializes string FILE buffer/base from input, remaining strlen, flags0x204 and UB base null (sp60=FILE+52), no ordinary device read function. __ssrefill is fixed string EOF/refill; no __srefill_r or FILE device callback union.
- scanf_i pushback is at most a single rollback of consumed sign/prefix byte on failed conversion (10068d88). For non-EOF matching-byte rewind, original input pointer/base and equal prior byte take10068432; after EOF resets pointer, fallback uses the embedded3-byte UB exactly once and conversion stops. Valid earlier conversions use no UB. Thus __submore cannot run; __ssrefill UB is null or embedded(FILE+68), excluding free_r. This covers invalid/short/empty names too, not only the eventual30-byte accepted name.
- sniprintf initializes flags0x208 and non-null outputbuffer with bounded33 remaining. svfiprintf initial malloc needs bit0x80 (clear); ssputs expansion test mask0x480 is also clear, even under truncation. malloc/realloc/free paths are unreachable. No __sfvwrite_r/stdio callbacks are installed in this string output route.
- Only printf s occurs: no floating, integer formatting/division, positional/dynamic format or locale conversion. printf_common+ssputs children are conservatively retained even if zero width eliminates particular padding callsites. memchr sees bounded NUL string; memmove copies bounded requested/remaining count.
- Protected32 walks already loaded current/other directories and active IDs; exact emitted function has no BL/BLX or stack recursion. ReadRoot/LoadProtectedRoot happens before Enumerate in GC, and Remove happens only after Enumerate returns. No visitor filesystem reentry.
- No reachable visitor instruction masks IRQs or calls flash/ROM. divider is linked hardware-divider RAM helper, memchr/memmove and switch helper are linked RAM functions. ROMB0/B1/B2 has no additional visitor leaf on the selected routes; ordinary route IRQ upper must still be added by caller ownership.
- All loop/restart iterations reuse one activation; conversions are sequential maxima. IRQ preemption is accounted externally. Temporary tail veneers are max, not cumulative4+target. Division denominator16 excludes div0 callback.

## Indirect targets

- 10068500, 10068616, 10068702, 10068728, 10068cda, 10068d68, 10068bbe → __ssrefill_r 10068450. ssvfiscanf initializes scan-data refill slot384 to literal10068451; all sites load this slot, not FILE device callback.
- 10068d88 → _sungetc_r 100683d8. ssvfiscanf initializes scan-data ungetc slot380 to literal100683d9; scanf_i loads that slot.
- 10068da8 → _strtoul_r 1006424c. scanf_i default conversion pointer1006424d; signed type3 alone replaces with strtol1006410d. Fixed x sets unsigned type4/base16; no signed format.
- 10061612, 1006163a, 10061282, 100612ce, 10061300 → __ssputs_r 10067fe0. svfiprintf passes literal10067fe1 at100683d4; printf_i stores callback and forwards SAME callback to printf_common.
- 1006a4e0, 1006a640 → divmod_u32u32 20000f20. linked veneer literals20000f21; nonzero denominator16. Temporary veneer4 returns before tail BX; hardware saved-state branch20 dominates.
- 1006a530 → memchr 20001390. linked veneer literal20001391; emitted RAM function has no stack/calls.
- 1006a680 → memmove 200013c2. linked veneer literal200013c3; emitted RAM function push8 and no calls.
- 1006a5d0 → __gnu_thumb1_case_shi 200013fc. literal200013fd; emitted helper push8/pop8 and BX adjusted return; bounded format dispatch table, no arbitrary callback.

## Remaining facts

- This closes V for ef22 under pinned callbacks, string initialization and fixed formats. The next coherent source/ELF must preserve these predicates and callframes or be remeasured.
- The independent LFS internal676 and retained216 are attributed to pinned96-root resource packet; this finite task does not repeat that graph.
- Actual new candidate outer PrepareCreate/Update/GC/Admit/Mounted frames and route IRQ composition remain separate final31/application graph work.
- No wholeP1/resource/hardware PASS. No source/SDK/Git/canonical/device changes, new fault images, firmware build or target measurements.
- Prior read arithmetic and lifecycle errata remain authoritative; this report does not modify historical reports.

Adjacent `-functions.json` contains exact emitted excerpts; `-graph.json` contains the recomputable contextual DAG; `-pins.json` records frozen source/build/ELF and dependency inputs. Runtime model/effort observed UNKNOWN.
