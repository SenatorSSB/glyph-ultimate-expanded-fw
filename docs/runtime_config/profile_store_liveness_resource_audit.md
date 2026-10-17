# Fault campaign resource and target-safety audit

Status: source/evidence audit; physical liveness root cause **UNPROVEN**.

This audit concerns failed strict-hardening source
`594066d9bb65b9f93c14e0e24e9d2002c3f83924`, tree
`00cc52535267bbaefe28c2f80feec0b17c61bf98`, and its retained ELF SHA-256
`04d50ccee4468f0ef4d2bbb90f04ce0f2ed73fe53f1814d5d6096f2b494f85cf`.
The physical failure is permanent evidence for that exact candidate. These
checks do not overturn it. No device was opened, reset, flashed or otherwise
operated during this audit, and the failed firmware was not rebuilt.

## Retained hardware measurements

The entire retained campaign tree contains 573 files. Recursive extraction of
all JSON objects with `resource_diagnostics_enabled=true` found **159 samples**.
A search of non-JSON text found no additional numeric diagnostic captures.
The tracked reproducible CSV is
[profile_store_liveness_resource_samples.csv](profile_store_liveness_resource_samples.csv), with
one row per sample, relative evidence filename, phase, source SHA-256,
retained file modification time, both stack values, heap values and generation.
The machine-readable audit is retained in the final custody evidence under
`resource-safety/`; the CSV remains tracked alongside this document.
The timestamp is **file mtime in UTC**, not a firmware measurement clock. It
orders retained evidence but cannot establish when an unacknowledged command
ran or whether a firmware instruction executed.

Every sample reports core1 stack minimum **3716 bytes**, heap arena current
**9092 bytes**, peak **9092 bytes**, and capacity **74628 bytes**. Observed arena
headroom is 65536 bytes. Core0 minima range from **1336 to 1852 bytes**; none
is zero or below the existing 512-byte investigation threshold. The last
128 samples report 1472 bytes. The first sample is generation 8 at
2026-10-15 21:40:03 UTC; the final retained response is generation 160,
`fault-record-open-lost-status.json`, at 22:08:17 UTC.

Changes in the retained core0 watermark sequence are below. Reboot-labelled
captures explain increases between sampling lifetimes; this table does not
pretend that a minimum should monotonically decrease across reboots.

| UTC time on 2026-10-15 | Response phase | Generation | Core0 minimum bytes |
| --- | --- | ---: | ---: |
| 21:40:03 | first-status | 8 | 1852 |
| 21:44:47 | n1-pre-status | 9 | 1496 |
| 21:45:34 | n1-32-status | 12 | 1480 |
| 21:49:30 | n1-reboot-status | 14 | 1852 |
| 21:51:02 | capacity-status-10 | 15 | 1536 |
| 21:51:08 | capacity-status-15 | 20 | 1480 |
| 21:51:11 | capacity-status-17 | 22 | 1440 |
| 21:53:23 | capacity-20-reboot-status | 26 | 1852 |
| 21:55:54 | t1-create-loss-status | 27 | 1608 |
| 21:56:25 | t1-update-loss-status | 28 | 1568 |
| 21:57:10 | t1-delete-loss-status | 32 | 1336 |
| 21:59:18 | t1-reboot-status | 32 | 1784 |
| 22:00:55 | t1-reference-restored-status | 32 | 1512 |
| 22:02:20 | reserve-update-status-3 | 35 | 1472 |
| 22:08:17 | fault-record-open-lost-status, final sample | 160 | 1472 |

STATUS does not report a profile count. The CSV explicitly records
`NOT_REPORTED`; it does not derive a count from generation or the filename.
Separate complete LIST evidence proves counts 3 at generation 8, 4 at 9,
7 at 13, 8 at 14, and 20 at 26 (both pre- and post-reboot page sequences).
The retained generation-32 LIST has pages 0 and 8 with another page announced,
so those two files alone prove a lower bound of 16, not a complete count.
The owner-reported campaign history and transaction evidence are separate
sources for subsequent inventory reconstruction.

These measurements show no *arena growth* or observed touched-stack exhaustion
through the final successful STATUS. `_sbrk` measures reserved allocator arena,
not current live allocation bytes: a leak that consumes existing free space
inside that arena is not disproved by a flat arena value. Likewise stack
watermarks miss untouched reserved slots, matching-sentinel overwrites,
pre-setup startup use and unexercised interrupt/call combinations. There is no
sample from the failed request, so the last successful sample cannot exclude
an abrupt failure afterwards.

## Exact ELF and diagnostic safety

The audit reads the custodied ELF directly. It does not substitute an isolated
object or a new build for its memory placement and instruction evidence.
`tools/check_glyph_liveness_resource_safety.py` validates the ELF32 sections,
linker symbols, default core1-stack selector, diagnostic direct calls and
absence of out-of-line atomic helpers. The retained disassembly is
`/private/tmp/glyph-liveness-evidence/failed-candidate-disassembly.txt`.

* Core0 uses scratch Y `[0x20041000,0x20042000)`; core1 uses scratch X
  `[0x20040000,0x20041000)`. Both `.scratch_x` and `.scratch_y` have size zero
  in this ELF. No non-stack section overlaps either fill interval. The
  `.stack_dummy`/`.stack1_dummy` sections are linker COPY reservations, not
  unrelated live objects occupying the bottom of those banks.
* The linker records `end=0x2002dc7c`, `__StackLimit=0x20040000`,
  `__StackOneTop=0x20041000`, `__StackTop=0x20042000`. The exact
  `core1_separate_stack` symbol is zero-initialized BSS. Arduino-Pico 3.6.3
  `cores/rp2040/main.cpp:139–146` therefore chooses the SDK default core1
  launch. The 2048-byte SDK reservations are not a measured whole-runtime
  bound for the 4096-byte scratch envelopes.
* `ResourceDiagnostics.cpp:25–37` fills only the current core's bank up to
  aligned `SP-64`. The exact initialization routine at `0x1002735c` pushes
  12 bytes, validates SP, disables interrupts, executes a call-free bounded
  store loop, then restores the previous PRIMASK. It cannot overwrite its
  own live frames or the caller frames above the captured SP. An interrupt
  before PRIMASK capture returns before filling starts; no active interrupt
  frame is erased. This assumes the ordinary valid stack state checked by
  the function, not arbitrary pre-existing memory corruption.
* Sampling is bounded by the initialized bank interval: at most 1024 words
  per scan, with no allocation, lock, callback or I/O. The exact sample
  routine at `0x100273d0` has a 12-byte frame and no calls; snapshot at
  `0x10027428` has a 16-byte frame, with only a memset call. The snapshot
  may observe a newer core1 minimum on the next request; this does not
  require a cross-core lock or make the values atomic as a multi-field tuple.
* The exact instructions use aligned native 32-bit loads/stores; heap
  acquire/release accesses include DMB. There are no `__atomic_*` library
  calls, spinlocks, malloc calls or recursion introduced by diagnostics.
* The wrapper at `0x100274c8` has an 8-byte frame. Its only two calls target
  real `_sbrk` at `0x1003ccf4`; the second passes zero. The real function
  updates a bounded break pointer and makes no calls. The actual failed
  ELF uses failure on overflow, not the optional optimistic-clamp branch.
  No allocation, printing or additional mutex is acquired inside the wrapper.
  Newlib's actual `__malloc_lock`/`__malloc_unlock` retain the pinned recursive
  allocator lock; Arduino's malloc/calloc/realloc/free interrupt wrappers
  remain in place. Thus ordinary allocator callers serialize the peak update.
  A separate unsynchronized custom `_sbrk` caller would need fresh review;
  none was identified on the ProfileStore paths.

The diagnostic checker used previously also passes: enabled initialization
frame 12 bytes, BSS 24 bytes, disabled no-hook/no-state control. The new checker
runs the actual `StackWatermark.hpp` implementation under ASan/UBSan for
10000 initialization cycles and 50000 scans, covering every first-overwritten
word position and preserving both end guards. It rejects two synthetic
non-stack scratch-bank overlaps and a synthetic recursive wrapper binding.
These are adversarial safety controls, not an RP2040 cycle-time measurement
or a reproduction of the physical hang. The no-instrumentation control proves
its code/state absence; it is not evidence that an uninstrumented device would
survive this campaign.

Disposition: there is no source-proven reason to disable or enlarge this
instrumentation. Retaining it for the next diagnostic candidate is reasonable
provided the **new exact ELF** passes the same bank/call gates. A changed
linker layout or separate-stack mode invalidates this conclusion. Sampling
overhead is finite but remains part of the candidate timing behavior; target
hardware must still accept the exact instrumented image.

## STATUS, storage ownership and multicore flash boundary

Source references in this section describe the failed SHA, not subsequent
repairs in the shared diagnosis branch.

`HAL/pico/src/comms/ConfiguratorBackend.cpp:362–412` reconciles uncertain
publications only for a mutation or transaction query. Ordinary STATUS does
not enter that reconciliation writer. It performs `ProfileStore::Capacity`,
protected-root reads/probes as needed, and `Persistence::LoadConfigChecked`
for durable reference high-water/root-format checks before sampling resources.
The latter is also filesystem work; an audit of Capacity alone is incomplete.
These are synchronous operations and have no elapsed-time cancellation budget.

`CheckedStorage.cpp:137–150` invokes real `lfs_fs_size`. Pinned LittleFS
`lib/littlefs/lfs.c:4243` traverses metadata/CTZ blocks; metadata-pair cycle
count is bounded by `block_count/2`. It also traverses the native open-file
list. The outer application loops are bounded by 64 entries per directory,
but filesystem cost depends on real directory/history state. A bounded static
loop count alone is not proof of a ten-second wall-clock bound. The separate
long-session reconstruction must measure real pinned LittleFS work and native
handle-list integrity, rather than an empty map fixture.

The checked adapter uses the mounted filesystem's original block callbacks.
Pinned `LittleFS.cpp:171–178` implements reads with XIP `memcpy`, without
pausing core1. Only its program/erase callbacks at lines 180–207 call
`noInterrupts`, `rp2040.idleOtherCore`, flash program/erase,
`rp2040.resumeOtherCore`, then `interrupts`. Sync is a no-op. STATUS opens
read-only files; LittleFS close calls rawsync, but no write/dirty flags are set
by these ordinary reads. The direct STATUS storage path therefore has no
source-supported reason to enter the flash pause handshake. No second-core
ProfileStore/filesystem caller was found in the `setup1`/`loop1` display/RGB
path. This conclusion does not cover arbitrary corrupted flags or memory.

The preceding lost-ack OpenWrite is different: `CheckedStorage.cpp:77–80`
closes the successfully opened native handle even when the acknowledgement
is injected as uncertain. Native `lfs_file_rawclose` at `lfs.c:3006` first
syncs, then unlinks the handle and frees its cache even when sync returns an
error. The new empty temporary file may therefore cause a real metadata
program/erase during that cleanup. That is a legitimate flash synchronization
path; it must be exercised in the preceding-sequence stress test. Its
successful later STATUS/query evidence establishes progress after that
particular prior request, not a live read of the currently failed controller.

`RP2040Support.h:92–110` contains an unbounded other-core acknowledgement wait
inside the program/erase handshake. This is a real target liveness boundary,
not a proven cause here. The retained failure has no program-counter/core-state
sample, and a direct new STATUS has no demonstrated write route. Changing the
handshake on conjecture would discard established flash safety without causal
evidence and is not recommended by this audit.

## Source-proven USB mutex re-entry hazard

A material liveness defect was found in the pinned USB integration after the
resource audit. Its occurrence during this physical failure remains unproven.
The exact retained compilation database selects the framework's
`Adafruit_TinyUSB_Arduino` sources and repository
`HAL/pico/include/tusb_config_pico.h:49`, which sets `CFG_TUSB_OS=OPT_OS_PICO`.
It is not sufficient to assume mutex-free TinyUSB from `OPT_OS_NONE` defaults
or inspect the separately listed XInput dependency instead of the compiled path.

The following interleaving is source-supported:

1. Application core0 enters a CDC FIFO or endpoint operation. In the failed
   source, `ProfilePacketWriter` calls `availableForWrite()` and `write()`
   without acquiring the port's global `__usb_mutex`. PacketIO reads also
   use the unguarded Adafruit stream.
2. TX `tu_fifo_write_n` acquires `tx_ff.mutex_wr`. RX reads similarly acquire
   the reader mutex; `cdc_device.c:261–262` assigns those mutexes explicitly.
   Endpoint claim/release acquire `_usbd_mutex` through `tu_edpt_claim` /
   `tu_edpt_release` (`tusb.c:115–147`, `usbd.c:1231–1242`).
3. A deferred USB interrupt preempts the application while one of those
   internal nonrecursive mutexes remains held. `usb_task_irq()` successfully
   takes the *different* global `__usb_mutex`, then executes `tud_task()`.
4. A DTR control-line ACK calls `tu_fifo_set_overwritable` on TX
   (`cdc_device.c:389–403`). That function takes the TX writer mutex again
   (`tusb_fifo.c:892–902`). A reset/FIFO-clear can similarly take an RX reader
   mutex (`tusb_fifo.c:869–879`), and endpoint processing can contend with an
   application endpoint claim. These are actual interrupt-reachable callers.
5. OSAL uses `mutex_enter_timeout_ms(mutex, UINT32_MAX)`
   (`osal_pico.h:87–90`, `osal.h:41`). SDK `mutex.c:111–112,127–148` waits
   for an invalid owner; it does not grant recursive entry or reject the
   same-core owner on this path. The interrupted application cannot release
   its mutex until the IRQ returns. The nominal wait is approximately
   49.7 days, far beyond both the two-second application TX deadline and
   ten-second host deadline. The external application deadline cannot execute
   while preempted inside this wait.

Exact failed ELF evidence corroborates that these locks were compiled in:
`usb_task_irq` is at `0x10007770`, `tu_fifo_write_n` at `0x10009218`,
`tu_fifo_clear` at `0x10009390`, `tu_fifo_set_overwritable` at `0x100093d0`,
and `tu_edpt_claim` at `0x1000ab1c`. The FIFO clear/set-overwritable and endpoint
claim disassemblies load `UINT32_MAX` and call the mutex timeout routine.
This is a concrete repairable interrupt/main mutex re-entry defect, not
merely an expensive filesystem hypothesis. Port reopen/DTR churn supplies a
relevant trigger class, but retained host files do not prove that this exact
interleaving occurred on the failed board.

Recommended repair: use a bounded stream adapter for **all** Configurator CDC
reads, peek, FIFO inspection, writes and flushes. Acquire the same global
`__usb_mutex` using `mutex_try_enter`, perform one bounded direct CDC FIFO
operation, release with `mutex_exit`, and return no progress if the lock was
unavailable. The port's deferred IRQ already uses `mutex_try_enter` on that
same mutex and skips processing while application code owns it. Retry/delay
belongs outside the guard. Cap each write to available FIFO space and avoid
Adafruit `Serial.write`'s retry loop, `available`'s implicit yield, or any
other delay/yield while holding the guard. The actual single CDC instance and
initialization must remain source-verified. This repair requires neither flash
core pause changes nor globally disabling interrupts.

The existing framework `SerialUSB.cpp:68–126` demonstrates the same global
USB mutex ownership convention, but it is not the selected Adafruit stream.
Its `CoreMutex` helper can block for another core (`CoreMutex.cpp:45–55`), so
plain nonblocking `mutex_try_enter` is preferable for the bounded candidate
adapter. Exact-source adversarial regression should inject deferred DTR/reset
and endpoint processing while the application FIFO/endpoint lock is held:
old integration must exhibit denied progress, repaired integration must defer
the IRQ and complete after guard release. Physical root-cause attribution
still requires evidence from the failed state or the subsequent controlled
hardware campaign; source race repair alone does not supply it.

## Why enumerated USB does not establish application progress

The pinned TinyUSB RP2040 port runs `tud_task()` from a deferred USB interrupt
(`Adafruit_TinyUSB_rp2040.cpp:81–112`) when its USB mutex is available. A blocked
application loop with interrupts running can coexist with USB servicing.
Moreover, a device node remaining present on the host is not proof of even
that servicing: the host may retain an enumerated node until disconnect.
Consequently the observed CDC nodes do not distinguish a decoder wait,
filesystem traversal, transmit wait, core lockup or host-side response loss.
They cannot identify a root cause or justify continuing the fault campaign.

The next exact candidate needs independent, bounded liveness evidence outside
the expensive STATUS sequence, exposing last entered/completed stages and
explicit transport/request state. Resource numbers alone are insufficient.
The root executor owns the resulting protocol/instrumentation repair and the
independent review. No physical root-cause claim follows from this audit.

## Reproduction

Run the new checker with `--elf EXACT_CUSTODIED_ELF --output-dir EVIDENCE_DIR`
and optionally `--hardware-evidence RETAINED_CAMPAIGN_DIR`. It performs only
local reads and temporary host compilation; it never opens serial devices or
builds firmware. Preserve `resource-safety.json` and its generated CSV alongside
the final candidate's resource evidence. Run the ordinary
`tools/check_glyph_resource_diagnostics.py` as the complementary ARM isolated-TU
and disabled-control check. The root executor must rerun both when diagnostic
source or target/linker placement changes.
