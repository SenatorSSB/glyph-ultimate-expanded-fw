# Strict-hardening candidate resource evidence

This document describes temporary, explicit candidate instrumentation. It is not
hardware evidence, a whole-target mathematical stack bound, or production
acceptance. The exact candidate build, map/ELF, source hashes and owner samples
must accompany the final handoff. Historical 84.4% RAM use remains historical;
it must not be substituted for the new exact source measurement.

## Exact candidate marker and artifact

On this repair branch only, `[env:glyph_mk6]` explicitly defines
`GLYPH_STRICT_HARDENING_CANDIDATE=1`, `GLYPH_RESOURCE_DIAGNOSTICS=1` and
`-Wl,--wrap=_sbrk`. Thus the required `pio run -e glyph_mk6` produces the same
instrumented artifact that the owner's B9 packet will measure. Other board
configurations remain unaffected. The diagnostics header rejects an enabled
resource flag without the conspicuous candidate marker.

STATUS reports `strict_hardening_candidate` (tag33),
`resource_diagnostics_enabled` (tag30), and five uint32 measurements (tags25–29):
`core0_stack_min_free_bytes`, `core1_stack_min_free_bytes`,
`heap_arena_peak_bytes`, `heap_arena_current_bytes`,
`heap_arena_capacity_bytes`. Both booleans must be true for this candidate.
Removing the instrumentation, or explicitly accepting it as a final production
choice, requires a separate exact-source review/build/hardware acceptance gate.
It cannot disappear silently after the measured artifact is frozen.

With both feature macros zero, the public calls inline to no-ops and an empty
snapshot. The diagnostic implementation has no state or `_sbrk` hook in its
object. The host/pinned ARM checker proves this absence as well as the enabled
implementation's 24-byte BSS and 12-byte initialization frame. Those individual
measurements are source-side checks, not a final linked RAM result.

## Pinned source authority

The framework pin is Arduino-Pico 3.6.3 from `platformio.ini`. Relevant exact
framework files and SHA-256 values inspected during implementation:

| Framework-relative path | SHA-256 |
| --- | --- |
| `cores/rp2040/RP2040Support.h` | `f9aebd5a7e47ca82a6ff2f38f5bde74f048f8cac668e02df84752c29ccb01412` |
| `cores/rp2040/main.cpp` | `c715e100f362b7520ed11348b9e446d9f451432a2fabce07766b14dd9f5f0fe3` |
| `cores/rp2040/malloc-lock.cpp` | `532acda747dc6700283599e5a7ecee2a12335d164388cef55b9002205950fb98` |
| `cores/rp2040/lock.cpp` | `ea7cdc3df66c1cd83521fdfa544c2122eb950ceac1394a81fdc4b0bb2d70fe44` |
| `pico-sdk/src/rp2_common/pico_runtime/runtime.c` | `c6b63ea7bebb1a0dc6b108664d048ed53ad61e9b04a4fae2439b6ba93891bb19` |

`RP2040Support.h:232–260` defines heap used through `mallinfo().uordblks`,
heap capacity through `__StackLimit - __bss_end__`, and the default two-core
stack lower addresses. `main.cpp:141–146` uses the SDK default core1 stack when
`core1_separate_stack` is false; this repository does not enable that weak
separate-stack override. The linked candidate must independently confirm the
linker boundaries. The SDK 0x800-byte reservations are linker reservations,
not whole-runtime limits: the actual default core0/core1 scratch-bank envelopes
are each 4 KiB.

`malloc-lock.cpp:28–51` already wraps malloc/calloc/realloc/free with Arduino
interrupt management. `lock.cpp` supplies Newlib's recursive allocator mutex.
The new hook preserves these exact wrappers; it does not redefine them, add a
second allocator, or modify their interrupt/core safety. SDK `_sbrk` in
`runtime.c:192–218` advances the heap break bounded by `__StackLimit`, and may
optimistically clamp a request. The hook queries the real `_sbrk(0)` after each
successful call so the measurement reflects the resulting break, including
clamping, rather than merely adding the requested increment.

## Measured lifetime and interpretation

Each core initializes its own stack watermark at the first statement in its
`setup` function. It fills only `[bank bottom, captured SP - 64)` and preserves
its own current frames, caller frames and a checked guard. Interrupts are
disabled only for this bounded, call-free initialization loop. Core0 and core1
write disjoint scratch banks. The real ARM compilation gates the initialization
frame below the 64-byte guard. A separate-stack override or out-of-bank pointer
refuses initialization; a zero reported stack margin must therefore stop the
hardware packet, not be treated as a successful measurement.

Each ordinary/recovery loop scans the watermark. A transient deeper frame
leaves its writes behind after return; sampling at phase boundaries therefore
retains evidence of intervening stack use instead of recording only the
current SP. Core0 STATUS samples again before reporting. This measures touched
stack since the setup entry, including observed interrupt activity; it does
not certify untouched but reserved local stack slots, an accidental overwrite
matching the marker, unexercised paths, or pre-setup startup depth. Actual GCC
frame/call evidence complements it. No function-entry instrumentation or
per-report print traffic is installed.

The `_sbrk` hook records actual allocator arena current/peak size from linker
`end`, even for transient internal realloc demand. It performs no allocation,
printing, filesystem operation, `mallinfo`, or extra lock acquisition. Existing
allocator serialization remains in force. The peak is retained from first
heap growth, including global constructors before setup. This is complete
observed allocator arena demand and gives a conservative physical heap
headroom measure; it is not the peak number of live user allocation bytes.
The candidate ELF must verify the intended `_sbrk` wrapper is linked and no
alternative allocator bypasses it on the relevant paths.

## Source-side evidence collection

Run `python3 tools/check_glyph_resource_diagnostics.py` for the sanitizer-backed
watermark bounds model, actual diagnostic ARM TU frame/BSS, disabled-hook
absence, and candidate flag placement.

After integration has generated the current production compilation database,
run `python3 tools/measure_glyph_profile_store_resources.py --elf EXACT_ELF
--output-dir EVIDENCE_DIR`. It recompiles actual production commands into an
isolated evidence directory with GCC stack/call information, appends ABI size
probes only to an analysis copy of the real ProfileStore TU, and records source,
compiler, compilation-database and ELF hashes. It records Config,
active/candidate Ultimate profile, ProfileStore object, directory/entry,
protocol request/response and transaction identity sizes. It retains linked
static sections and size-sorted symbols so migration/recovery/Config scratch,
protocol frame and static BSS/data remain inspectable. The 8192-byte transport
frame is explicit. Shared Config write scratch is used by Configurator,
selection and migration; the retired extra migration Config object must not
reappear in the linked symbol report.

This collector does not invent a composed whole-target bound from individual
frames. The final report must explain critical actual call chains, callback
and IRQ gaps, both-core paths, ABI assumptions and the owner measurements.
The earlier checker hardcodes the old unchecked adapter chain and is not a
current checked-storage resource proof.

## Exact-candidate owner measurement rows

No device action has been performed. Use the same exact source SHA, UF2 hash
and owner-approved backup/restore packet as the other strict-hardening rows.
Record STATUS after initial boot/connection; ordinary controller operation;
selection/reset; manual and automatic headless recovery; bounded record
read/list/health; CREATE/UPDATE/DUPLICATE and checked publication/GC/fault
scenarios already authorized by that packet; and the exact supported legacy
migration/upgrade route. Do not introduce extra destructive mutations solely
to collect resource values. A fresh boot starts a fresh sample lifetime, so
retain each row before the next reboot.

For every row record both booleans and all five numeric fields. Zero stack
margin, invalid geometry, peak/current beyond heap capacity, missing markers,
or unexplained regressions stop the packet. Also stop and investigate a
measured stack margin below 512 bytes; this is a conservative engineering
investigation threshold, not a waiver or a claim that 512 bytes proves every
IRQ path. Compare the measured margins with the final actual GCC critical
frames and unresolved paths before deciding sufficiency. Record allocator
arena growth and retained headroom explicitly. Unexercised/physical-only rows
remain NOT_TESTED until the owner reports their exact observations.

## Preliminary uncommitted collection — 2026-10-15

The second preliminary integration build succeeded before final review, source
freeze or commit. Its working-tree source was dirty and subsequently formatted;
these values are preliminary engineering evidence only. They do not identify
the final candidate and must be refreshed after final convergence/freeze. The
preliminary ELF SHA-256 was
`a905711bee8512692d193cfa950db2aef737a29568b1f97f4d4d1bac7613d3de`.
The integration log recorded RAM187240/262144 (71.4%) and flash471900/1568768
(30.1%). Earlier accepted 84.4% usage remains preserved historical evidence.

The preliminary source/ELF collector report is retained outside the repository
at `/private/tmp/glyph-strict-resource-preliminary/report.json`, alongside
isolated compilation objects, GCC frame/call reports, linked symbols and
sections. Exact compiler SHA-256:
`ce911118c96964b17d1ba0f7607ca7ec78565981c9f7f5447a1831e1bb8d9a1c`.

| Measured target ABI object | Bytes |
| --- | ---: |
| Config | 31312 |
| UltimateProfile, each active/candidate | 2152 |
| ProfileStore object including both profiles | 4348 |
| Directory, each of three workspace objects | 3848 |
| Directory entry | 56 |
| ProfileStore request | 2264 |
| ProfileStore response | 2960 |
| Transaction identity | 40 |
| Protocol byte frame | 8192 |

The linked preliminary heap start was `0x2002dc2c` and `__StackLimit` was
`0x20040000`, giving74708 bytes of allocator arena capacity before dynamic
allocation. This is capacity, not measured remaining heap or a claim that all
74708 bytes are unused after boot. The hook's owner-observed current/peak rows
must supply actual allocation demand. The active and candidate profiles total
4304 bytes; the three directory workspaces total11544 bytes. Linked static
symbols/sections retain the separate Config, persistence-load candidate,
shared write/migration/recovery scratch and protocol allocations explicitly.

Largest preliminary individual GCC frames were hash_file656,
CaptureLegacySource600, profile semantic validation544, Bootstrap480,
HandleProfileStore464 and LoadConfigChecked456 bytes. The composed enumerated
checked record-open path was2800 bytes, leaving1296 bytes within the 4096-byte
scratch bank before unmodeled IRQ/ROM/other paths. This remains above the
2048-byte SDK reservation and does not convert that reservation into a runtime
limit. Target watermark rows and the final actual call report remain required.

The retained ARM decoder/stack regression independently measured actual full
v2 TU decoder32, ReadRoot80 and Begin/BeginRecovery24-byte frames. The legacy
decoder was inlined into the bounded Bootstrap path. Its exact historical F6
copy reconstruction still consumes2640 bytes, exceeding2048. A second negative
control restores `Directory{}` assignments in the current actual production TU;
it reproduces DecodeLegacy4032 and Begin3872-byte frames. The new in-place reset
must preserve these negative detections, not merely change a textual checker.
