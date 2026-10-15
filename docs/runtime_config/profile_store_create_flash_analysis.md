# ProfileStore CREATE flash, multicore and stack analysis

Status: source-backed diagnostic analysis; physical root cause UNPROVEN.
Date: 2026-10-15. Baseline candidate: `83f526b843fbcc61ee7dac6da9df0bc79351c2bf`.
This specialist inspected local source and existing compiler outputs only. No
build, firmware/device operation, filesystem-on-device inspection or physical
acceptance was performed. The parent owns the repair, validation and handoff.

## Evidence boundaries

`F/` below denotes the installed Arduino-Pico package
`/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico`.
Its package version is `1.30603.0`; repository `platformio.ini:108-109` requests
Arduino-Pico tag 3.6.3. `L/` denotes
`F/libraries/LittleFS/lib/littlefs/lfs.c`. The compiled wrapper
`F/libraries/LittleFS/src/lfs.c` includes that file and defines `LFS_NAME_MAX 32`.
Local bytes are pinned below; package metadata alone is not a remote provenance
verification. Repo source line references without a working-candidate qualifier
refer to the baseline commit. Current canonical docs preserve older accepted
chapters; they are not evidence of hardware acceptance for this candidate.

## Complete synchronous CREATE storage path

The baseline command dispatch in `HAL/pico/src/comms/ConfiguratorBackend.cpp:71-79`
passes the framed request to `HandleProfileStore`; request/response/frame storage
is static (`230-244`). CREATE dispatch is at `285-286`. `ProfileStore::Create`
(`HAL/pico/src/core/ProfileStore.cpp:295-297`) validates and selects the next ID,
writes the record, creates the next directory snapshot, then publishes that
snapshot. Config and active controller profile selection are not written by CREATE.

`WriteProfile:236-258` creates the record envelope and protobuf in static scratch.
`ProfileStoreAtomicCommit.hpp:19-50` performs temporary write, close through the
adapter, reopen/readback, validation, optional destination remove, and rename.
`PublishDirectory:218-228` repeats this publication sequence for the inactive
redundant directory root, then updates the live in-memory directory. There are
therefore two file publications, not a single flash write. File helpers are
`ProfileStore.cpp:111-145`. The temporary filenames fit the installed wrapper's
strict component bound (`ProfileStorePaths.hpp`; wrapper `LittleFS.h:308-320`).

The directory wire is **2,620 bytes**: 32 + 64 entries * 40 + 28. The maximum record
buffer is 4,128 bytes, including its 32-byte envelope. The adapter issues one
high-level write per file; that does not mean one low-level flash transaction.

## Actual LittleFS and flash work

`F/libraries/LittleFS/src/LittleFS.h:50-66` selects 256-byte read/program/cache
units, 4,096-byte blocks, and metadata block_cycles 16. The final FS instance is
constructed at `LittleFS.cpp:215`. Both a representative profile record larger
than 256 bytes and the directory exceed the inline-file threshold
(`L/:3328-3339`) and require outlined data storage.

The `w+` mode requests create/truncate, not append (`LittleFS.h:288-303`).
Existing temporary files become zero-length inline files marked dirty
(`L/:2905-2908`); new files commit a directory entry (`2878-2896`). The wrapper
calls `lfs_file_sync` immediately after a successful open (`LittleFS.cpp:90-97`).
An existing stale `.tmp` is therefore normally truncated. The wrapper ignores
that sync return and ignores `lfs_file_close`'s result (`LittleFS.h:449-468`),
so successful write counts alone are insufficient durability evidence.

Writes can allocate/erase/program outlined data (`L/:3323-3405`), and close/sync
flushes data and commits its metadata (`3191-3237`). Remove/rename also commit
metadata. Compaction, metadata-pair splitting, relocation/wear leveling and
orphan recovery depend on prior filesystem state (`1734-2380`, `4480-4620`).
Reads ordinarily use XIP memcpy (`LittleFS.cpp:173-178`); the wrapper's read-open
still enters its normal open/sync code. A read is not a license to assume that
all internal recovery-related code is excluded without examining its flags/state.

Every actual program or erase callback executes, in order:

1. `noInterrupts()` on the caller core.
2. `rp2040.idleOtherCore()` and acknowledgment wait.
3. SDK `flash_range_program` or `flash_range_erase`.
4. `rp2040.resumeOtherCore()`.
5. `interrupts()` restoring the saved caller state.

This is exact in `LittleFS.cpp:181-203`. IRQ nesting is maintained by per-core
saved masks (`F/cores/rp2040/wiring_private.cpp:27-48`). Flash SDK functions are
RAM-resident and disable XIP only around boot-ROM work, flush cache and restore
XIP before returning (`F/pico-sdk/src/rp2_common/hardware_flash/flash.c:63-105`).
The LittleFS callback reports success after that return; it exposes no flash-chip
status or timeout to ProfileStore.

If a CREATE causes P program callbacks and E erase callbacks, it performs exactly
P+E corresponding idle/resume pairs, assuming each returns. P and E cannot be
fixed from the high-level operation alone: payload length, metadata free space,
existing temporary/destination files, allocation position, compaction/relocation,
and recovery state affect them. No physical count or timing was observed. The
two publications must not be described as merely two lockout cycles. Repeated
calls are sequential; file-open/write/close/rename have returned before their
following high-level stages execute.

Full allocation performs a filesystem scan and returns `LFS_ERR_NOSPC` when its
acknowledged block budget is exhausted (`L/:557-600`). Full storage by itself is
not a source-proven infinite loop. ProfileStore Update/Delete do not reclaim old
record paths (`ProfileStore.cpp:299-317`), so entry count/capacity arithmetic is
not a measurement of actual free filesystem space. Corruption, stale files and
physical flash failure on the owner device remain unknown.

## Multicore audit and hypotheses

`F/cores/rp2040/RP2040Support.h:92-145` establishes the actual non-FreeRTOS
handshake. Idle acquires `_idleMutex`, clears `__otherCoreIdled`, pushes the
sleep token and waits for acknowledgment. The other core's RAM-resident FIFO IRQ
disables its IRQs, acknowledges, and busy-waits until resume clears the flag.
Resume releases the mutex and clears that flag. There are no deadline checks in
these waits. A core unable to service FIFO IRQ, a lost handler, corrupted shared
state or nested idle acquisition could consequently block indefinitely. These
are possible failure mechanisms, not observations from this controller.

Core1 registers the FIFO handler before calling setup1 (`F/cores/rp2040/main.cpp:52-61`).
Glyph setup1 waits for the boot snapshot, then establishes display/RGB. In ordinary
Configurator mode it selects REMAPPER, paints once and returns
(`config/glyph/common/src/config.cpp:305-310,373-385`). loop1 returns early for
REMAPPER (`392-415`) while normal IRQ servicing remains available. Transport-only
recovery also leaves the registered core alive without initializing those backends.
No Configurator-path FIFO handler replacement, permanent IRQ mask or concurrent
LittleFS caller was identified. Repo idle calls in GameCube/N64 and the Oopsie
screen-off branch belong to other mode paths; their presence alone does not show
that they ran during CREATE.

**No source-proven CREATE-specific multicore fault was found.** The handshake
source alone does not prove a repeated-cycle race. Adding an outer idle around
LittleFS would introduce nested acquisition of the nonrecursive idle mutex and
must not be used as a fix. Changing framework sequencing or adding a blind delay
would be an unproved workaround without a captured blocked location.

## Comparison with the existing Config write

`HAL/pico/src/core/Persistence.cpp:112-183` uses the same LittleFS instance and
flash callbacks: remove temporary, open `w+`, header write, streaming protobuf,
seek/read CRC, header rewrite, close, reopen/validate, rotate old compact Config,
rename temporary, reopen/validate. It also produces multiple flash/lockout cycles.
`ConfiguratorBackend.cpp:218` calls it synchronously on core0. Existing successful
Config writes, if tied to owner evidence, demonstrate that the installed flash
path can work in that context. They do not prove that CREATE's larger call stack,
two-publication sequence, exact file allocation/metadata state, response path or
particular interrupted operation is safe. This specialist did not independently
observe a physical Config write and claims no new hardware result.

## Reachable stack chains and actual reserved regions

The supplied before-repair `.su` and object files are under
`/private/tmp/glyph-create-stack-before`. Existing object disassembly was inspected
with `arm-none-eabi-objdump -dr`; direct `R_ARM_THM_CALL` edges were combined with
the source-bound callback passed by compact to traverse (`L/:1797-1804`). No new
compilation was performed. These establish reachable, state-dependent chains;
they are not a measurement of the failed device's PC/SP or a complete WCET/stack
proof. The callback was not inferred from an unconstrained function pointer.

| Concurrent lfs_file_open chain | Per-frame bytes |
| --- | ---: |
| lfs_file_open | 16 |
| lfs_file_rawopencfg | 80 |
| lfs_fs_forceconsistency | 64 |
| lfs_fs_deorphan | 176 |
| lfs_dir_orphaningcommit | 160 |
| lfs_dir_relocatingcommit | 136 |
| lfs_dir_splittingcompact.constprop | 192 |
| lfs_dir_compact | 136 |
| lfs_dir_traverse.constprop | 216 |
| lfs_dir_commit_commit | 72 |
| lfs_dir_commitprog | 72 |
| Total before flash callback, SDK/ROM and callers | **1,320** |

The analogous no-deorphan open path is 1,080 bytes. A close path including
orphan handling totals 1,208, sync 1,200, and rename 1,400 bytes before its flash
callback and omitted outer/leaf frames. These are particular reachable chain
sums, not proven absolute maxima for all filesystem states. The emitted
`lfs_dir_commitprog` already inlines block-program/flush work; adding the separate
`lfs_bd_prog` and `lfs_bd_flush` `.su` values would double-count that path.
`LittleFS_cpp.su` separately records program and erase callbacks at 24 bytes.
SDK/ROM callees, library routines, exception entry and interrupt activity are not
fully bounded by these sums.

Baseline app measurements supplied by the parent and visible in the same evidence
set include HandleProfileStore 2,384 bytes, Create 192, WriteProfile 328,
PublishDirectory 152, and the LittleFS adapter write 64. Handle's full local
profile reservation exists even for CREATE's branch. These are concurrent with
the relevant storage chain, unlike response encoding after the store returns.
They show a reachable stack hazard; they do not establish which chain the
physical failure took. The working repair moves the unrelated full local
profile destinations to static scratch; final candidate stack proof belongs to
the parent's subsequent validation.

The retained baseline `.pio/build/glyph_mk6/firmware.elf` was read with `nm`:

| Symbol | Address |
| --- | --- |
| __StackBottom | 0x20041800 |
| __StackTop | 0x20042000 |
| __StackOneBottom | 0x20040800 |
| __StackOneTop | 0x20041000 |
| __scratch_x_start__, __scratch_x_end__ | 0x20040000 |
| __scratch_y_start__, __scratch_y_end__ | 0x20041000 |

The named linker reservations are **2 KiB per core**, while each otherwise-empty
scratch bank is **4 KiB** (`F/lib/memmap_default.ld:28-29,239-267`). Neither fact
must be substituted for the other: 2 KiB is the reserved size; 4 KiB describes
the bank envelope before crossing into the adjacent region. Empty scratch
sections do not constitute formal additional stack allocation or a runtime
high-water proof. Core1 default launch uses `__StackOneBottom` and the size of
its compiled stack array (`F/pico-sdk/src/rp2_common/pico_multicore/multicore.c:132-137`),
not the array's nominal C address; its launcher also places three startup words
on the stack (`117-129`). `core1_separate_stack` is false by default in main.cpp49.
No stack-size or alternate-core-launch repair is proposed by this report.

### Separate startup frame hazard

The supplied before-repair `config_glyph_common_src_config_cpp.su` records
`setup()` at **31,480 bytes**, with the same compiler warning in its log. This
number belongs to that diagnostic compilation; the parent's production-object
measurement may differ slightly and must retain its own attribution. The source
of the full automatic reservation is `Config compact = config` in the migration
branch (`config/glyph/common/src/config.cpp:225` at the baseline). A function-wide
frame is reserved on every setup entry, including boots that never take migration
and an early probe-recovery return. Arduino main launches core1 before setup
(`F/cores/rp2040/main.cpp:138-148`). The reservation exceeds both the 2 KiB core0
reservation and its 4 KiB scratch-bank envelope before additional calls occur.
This is a definite startup stack-budget defect, not proof of which bytes were
written, which live object was overwritten, or that it caused the reported freeze.

The parent's working repair moves the unpublished migration candidate to static
BSS and assigns `config` only inside the original migration branch. That retains
its source-owned values and boot-only lifetime while removing the automatic full
Config frame. It adds one full Config-sized RAM allocation; its final BSS/heap
headroom and complete rebuilt target sizes require the parent's build evidence.
An earlier-return probe alone would not have fixed the function-wide automatic
reservation. The exact `.su` snapshot is pinned below.

## Diagnostic watchdog candidate inspection

The parent's working `ProfileStoreCreateProbe.hpp` and directly coupled caller
changes were inspected independently. This is a diagnostic candidate, not proof
that the freeze is fixed. Begin tags scratch2, stores stage in scratch3 and enables
a watchdog with an 8,000 ms deadline. Each Mark stores a stage then refreshes the
deadline; Finish disables it. Markers bracket record/directory storage stages and
response encoding/transport. The probe deliberately changes a prolonged stall's
outcome into a reset; it adds no flash logging or FIFO calls and does not change
the flash callback's IRQ/idle/program/resume ordering.

Scratch2/3 are MMIO and persist through soft reset (`F/pico-sdk/src/rp2040/hardware_regs/include/hardware/regs/watchdog.h:127-145`).
The repository uses scratch0/1 for selections. SDK watchdog_enable writes scratch4,
sets reset-selection/debug-pause bits and programs the watchdog counter
(`F/pico-sdk/src/rp2_common/hardware_watchdog/watchdog.c:36-74`); watchdog_reboot
owns scratch4-7 (`77-96`). Thus 'scratch4-7 remain owned elsewhere' means retained
SDK ownership, not that watchdog_enable leaves every register untouched.
8,000 ms fits the SDK's 24-bit counter with its twice-per-tick compensation;
it is a chosen diagnostic interval, not a source-established maximum FS latency.
Pause-on-debug is enabled. A stage denotes the last completed marker, not an
exact blocked instruction or proof the named operation succeeded.

`setup()` calls CaptureBoot before input/display/config/storage work and routes
recovery through the existing transport-only entry. That constructor creates
the Configurator transport; profile requests in recovery return the captured
stage before querying/mutating ProfileStore or persistence. The command filter
permits only device-info and profile-store requests; other commands are refused.
Consequently reporting the retained stage does not mount or rewrite the FS.
No concrete safety defect was found in this bounded diagnostic inspection.
The normal GetDeviceInfo writer still has its existing transport behavior; this
inspection does not establish a general bounded-recovery-transport claim.

Limits: reset may interrupt a flash operation, so completed atomic steps and
actual stored outcomes still need read-only reconciliation in the approved human
sequence. Power removal destroys scratch evidence. Invalid stage values are
reported as unknown, not accepted as a root cause. A completed response can mean
only that transport queued bytes; it is not a host-consumption acknowledgment.
The exact firmware SHA/UF2 digest, actual retained stage, post-reset availability
and store outcome require the parent's artifact custody and human hardware test.
No physical PASS, general stability, free-space value, or multicore root cause is
claimed. Nunchuk remains NOT_TESTED.

## Pinned local evidence

SHA-256 values below pin inspected local bytes. Baseline repository blobs use
`git show` at the candidate SHA; the diagnostic probe is a separately identified
working snapshot. Later parent edits require rechecking that snapshot before
using it as final-candidate review evidence.

| Input | SHA-256 |
| --- | --- |
| `83f526b8:HAL/pico/src/core/ProfileStore.cpp` | `6aa573b854cbbde14301dbf180325f238d0b8c1042bfb9d95f7ae1ea7c092007` |
| `83f526b8:include/core/ProfileStoreAtomicCommit.hpp` | `76342eca838d9666d0409ee5cc4b16fcb4ef959b54a1dea9534d47eee5a8e527` |
| `83f526b8:HAL/pico/src/comms/ConfiguratorBackend.cpp` | `8f9d736cd519896bf549bc14fd60ae45411ae5c819a2e9bb362b587d64d5a234` |
| `83f526b8:config/glyph/common/src/config.cpp` | `a5083f982cd97e4fefda596f22c37dc8f6ac40c44f5aea8702da6ae4fd3b02cd` |
| `83f526b8:HAL/pico/src/core/Persistence.cpp` | `9b6effc1a3b78ccaff08ae61804804441d0a47f02fd9f363efb2302dab3a353a` |
| `83f526b8:include/core/ProfileStorePaths.hpp` | `e2919e14fd17f820eb604a20117dc0fd33ee104aa53960607dd5f8eeb6c412e0` |
| `83f526b8:include/core/ProfileStore.hpp` | `05b1ed664d6f0bf670852ce3641660dff0248f3fe603f0d98634442403df3f73` |
| `F/package.json` | `0aa78013e54caef261f2fd38b12ac84ce16c8f1e5dcba5660be6846e888c8960` |
| `F/cores/rp2040/RP2040Support.h` | `f9aebd5a7e47ca82a6ff2f38f5bde74f048f8cac668e02df84752c29ccb01412` |
| `F/cores/rp2040/main.cpp` | `c715e100f362b7520ed11348b9e446d9f451432a2fabce07766b14dd9f5f0fe3` |
| `F/cores/rp2040/wiring_private.cpp` | `7486696cf7065981fdb9e405cac176b3fe5c713248e56d0270bc0a82a3ba44ec` |
| `F/libraries/LittleFS/src/LittleFS.cpp` | `dfc032cc49b5254abc204b67a2aa56156d28e39b5adbb3b70c2e291667c70e5d` |
| `F/libraries/LittleFS/src/LittleFS.h` | `6036f92f824ee8257da051ed37fe01e7dfdedece33c772ae6321036dc0f412f9` |
| `F/libraries/LittleFS/src/lfs.c` | `3ede3a5ee496159150b9f5a1bacac98d157eb1f761e19d7d58a9b0fa4528ca6e` |
| `F/libraries/LittleFS/lib/littlefs/lfs.c` | `8c28c80018293820d5400759f4918359b09d869c1a1240959b0647cc844783b5` |
| `F/lib/memmap_default.ld` | `b1ac28528b4353a94bc391ab2bc122e12f2992863e21f98b2915b87ac1ded2da` |
| `F/pico-sdk/src/rp2_common/pico_multicore/multicore.c` | `b6c1e838be570742412419af531d64cef2b53e5ecc247e3bb71bb0836deeae28` |
| `F/pico-sdk/src/rp2_common/hardware_flash/flash.c` | `ad7af777d6f600bc718ee455a82638a14bcb20ccef93440e4c85df2e571840ed` |
| `F/pico-sdk/src/rp2_common/hardware_watchdog/watchdog.c` | `199db806a6844a638ae505383083ce7942f8a7bfd746f218a7499e49999fd014` |
| `F/pico-sdk/src/rp2040/hardware_regs/include/hardware/regs/watchdog.h` | `d2020b6f62d175f3879151e7cafb39d8b5f40f83b67eec9bcad888c0b01b9900` |
| `before-stack/_Users_rasmus_pekkarinen__platformio_packages_framework-arduinopico_libraries_LittleFS_src_lfs_c.su` | `a6e15738e41917cfff9a922fa6eca8023657c9afd5b5afe7dbe27115c16cf5d6` |
| `before-stack/_Users_rasmus_pekkarinen__platformio_packages_framework-arduinopico_libraries_LittleFS_src_lfs_c.o` | `bc9680c1f9c10a49185b35fff05f44fe005715331387bbb2e0b3101df2eb9987` |
| `before-stack/_Users_rasmus_pekkarinen__platformio_packages_framework-arduinopico_libraries_LittleFS_src_LittleFS_cpp.su` | `2f8d98fc97f8f75991edb3d4c871a40a1b6a8ee47b447e2919f57daff8563c66` |
| `before-stack/HAL_pico_src_comms_ConfiguratorBackend_cpp.su` | `ee6081fdccc3fe87f57a0df9b6bdea0db0930ec692f87326958b6f69e4e6f51d` |
| `before-stack/HAL_pico_src_core_ProfileStore_cpp.su` | `f54a86b5e0c30039c18dd60032529f204da1d4536eaaa562cc4261a0cc8c9db9` |
| `inspected-local/.pio/build/glyph_mk6/firmware.elf` | `f38ea6fbae2f98af97afa8c65868c2da8bd469d0fc32d0b3d8c1d892797d568a` |
| `inspected-local/include/core/ProfileStoreCreateProbe.hpp` | `4f6daef0edeee17ecc07266e1da09eaf65f9da39fa76e1264c6ac34348869f87` |
| `before-stack/config_glyph_common_src_config_cpp.su` | `3558378fff71d1d28f56454e7757cda4e8916fe01b134afb66c77ecb4001f651` |
