# RT2 pre-SETUP bounded source and ABI audit — 2026-10-17

Read-only specialist result for owner-authorized descendant of
`0f22b6d3b5d4a1a16fc7fd03866cfa44336de4ff`, tree
`4f5fb41553f98da3f11108685b2eaa0942583fc0`. No tracked source, vendor source,
Git state, controller state, queue or canonical publication was changed by this role.
Actual requested model/effort cannot be established from available telemetry;
this role does not claim an independently verified model identity.

## Finding and scope

The source hypothesis remains plausible and UNPROVEN. The registered DCD handler
reads `usb_hw->ints` once, then handles SOF, BUFF_STATUS, SETUP, bus reset,
suspend/resume and finally unknown bits. A call begun before a later SETUP latch
can remain active; a wrapper that promotes only SETUP-positive entry/return
samples misses that earlier invocation. Later sticky SIE/INTR/INTS positives do
not prove no IRQ entry, no panic, or that the handler's saved status included
SETUP. Current owner observations and root cause remain separate: normal0f22
PASS, one RT2 LF4WHITE/LF3YELLOW/LF5OFF/black/no USB/no Serial and then no actions.
Root cause UNPROVEN. Nunchuk NOT_TESTED.

External `hw_endpoint_xfer_continue` wrapping plus general invocation
active/returned/ID and panic-enter observation is feasible without private
vendor-handler instrumentation. Exactly one real call must remain on every
wrapped ordinary route. Panic must always tail-forward to the original exactly
once; observation cannot suppress, repair, retry or replace it.

## Pinned dependency and build basis

The saved compile database is
`/private/tmp/glyph-profile-store-rt2-setup-irq/local_backups/setup-irq/compile_commands.json`.
It selects Arduino-Pico package1.30603.0 (Arduino-Pico3.6.3), Adafruit TinyUSB2.3.0,
TinyUSB0.16.0 and SDK1.5.1 from the local package below. The active driver is the
Adafruit library's `portable/raspberrypi/rp2040` source, NOT the SDK vendored copy.
Actual compile flags include GNU17/O3, ARMv6-M/Cortex-M0+/Thumb, NDEBUG,
USE_TINYUSB, CFG_TUSB_CONFIG_FILE=tusb_config_pico.h and the strict diagnostic
candidate flag. Findings are grounded in saved source, active preprocessing,
object relocations and the saved exact base ELF, not generic SDK assumptions.

Preprocessing actual DCD/usbd/FIFO compile commands succeeded. E5 enumeration
and E15/uframe macros are undefined, so their #if bodies are false.
PICO_RP2040_USB_FAST_IRQ=0; CFG_TUSB_DEBUG=0; CFG_TUSB_OS=OPT_OS_PICO;
CFG_TUH_ENABLED evaluates0 (TUH_RHPORT_MODE=OPT_MODE_NONE); CFG_TUD_ENABLED=1;
CDC/MSC/HID/MIDI each1, AUDIO0; OSAL_MUTEX_REQUIRED=1;
CFG_TUD_TASK_QUEUE_SZ=16. The uframe timer/endpoint SOF scheduling branches are
absent in the active object. The endpoint lock helper is an empty inline function.

## SOF route

`dcd_rp2040.c:264-306`: the disabled E15 loop contributes no wait or lock. Remaining
SOF code conditionally clears SOF enable, reads SOF count and calls
`dcd_event_sof` -> `dcd_event_handler`.
`usbd.c:1134-1156`: if suspended, it clears suspended and enqueues one RESUME;
then loops the class drivers. Initialized expected count is1 application XInput
plus4 built-ins. The actual XInput table (`Adafruit_USBD_XInput.cpp:290-305`) and
CDC/MSC/HID/MIDI tables (`usbd.c:114-184`) all have `.sof=NULL`. No class SOF
callback or game callback runs in this valid state. The loop is bounded under
this initialized state; arbitrary memory corruption is outside that proof.

The suspended RESUME enqueue is the meaningful non-bounded route: the OSAL
queue enters its critical section -> spin_lock_blocking ->
spin_lock_unsafe_blocking, a busy wait with interrupts disabled until the lock
can be taken. The source contains no timeout. No WFE is used in that spin wait.
After lock acquisition, the actual queue FIFO has null mutex pointers from its
static TU_FIFO_INIT and no configuration adding FIFO mutexes. Its FIFO item copy
and index math are bounded with the valid positive depth16. General
`tu_fifo_write` can take a WAIT_FOREVER mutex for other FIFOs; this is conditional
code in the actual object, but the event queue does not populate that mutex.
Queue-full TU_ASSERT is not standard assert: it returnsfalse, and the breakpoint
macro is empty for Cortex-M0+. Queue send unlocks before TU_ASSERT. It does not
panic on full. Existing event hook is fixed bounded stores and returns for RESUME.

## BUFF_STATUS / transfer route

`dcd_rp2040.c:203-233`: one saved `buf_status` snapshot, maximum32 bits/iterations.
Each selected bit is cleared BEFORE `hw_endpoint_xfer_continue(ep)`. A hardware
change after that snapshot does not turn this loop into a polling loop.
On done=true, it emits XFER_COMPLETE then resets transfer state; on false it
continues the finite loop. There is no class xfer callback in this IRQ path:
`dcd_event_xfer_complete` -> `dcd_event_handler` default enqueues only. Class
callbacks run later in tud_task, separate software IRQ/foreground context.

`rp2040_usb.c:338-380`: hw_endpoint_lock_update is empty. Explicit !ep->active
panic is retained under NDEBUG. Sync reads buffer control once for each of at
most2 buffers, updates fixed state and performs finite memcpy for RX. Standard
FULL-bit asserts are removed by NDEBUG. The disabled #if0 abort_done polling
loop is not compiled. If remaining_len becomes0, returnstrue. Otherwise active
E15 check is constantfalse and start_next_buffer runs, then returnsfalse.

`hw_endpoint_start_next_buffer` prepares at most2 buffers, performs bounded
copies under valid endpoint sizes, updates endpoint and buffer control, and
returns. `_hw_endpoint_buffer_control_update32` has an explicit already-AVAIL
panic, else six forward unconditional branches as a fixed cycle delay, then
register write. There is no active hardware polling wait. Invalid/null/corrupted
pointers or lengths can fault or corrupt state; source boundedness does not
establish physical correctness or root cause.

Done transfer event enqueue shares the same critical-section/spinlock caveat
as the suspended SOF RESUME enqueue. `hw_endpoint_reset_transfer` is fixed stores.
The endpoint lock helper itself provides no actual mutual exclusion.

## Direct USB DCD panic formats and retained branches

All3 have actual external R_ARM_THM_CALL panic relocations in the active DCD or
rp2040_usb object; all survive NDEBUG:

| Scope | Literal format / bounded classification | Source |
| --- | --- | --- |
| xfer_continue !active | `Can't continue xfer on inactive ep %d %s` / INACTIVE | rp2040_usb.c:345 |
| buffer update already AVAIL | `ep %d %s was already available` / AVAILABLE | rp2040_usb.c:115 |
| saved status has unhandled bits | `Unhandled IRQ 0x%x\n` / UNHANDLED | dcd_rp2040.c:373 |

Use exact finite literal-prefix comparisons, fmt NULL guard, and generic OTHER
for any unmatched intercepted panic in the authorized USB context. Do not format
or dereference varargs or endpoint pointers in the panic observer. Record current
core/exception/invocation linkage and bounded read-only registers using fixed
stores; no logging, heap, locks or IO. An observer entry proves panic entry,
not completion of original panic/exit.

The full exact base ELF has16 direct panic callsites (listed below). The other13
are Wire SDA/SCL4, clock startup1, noInterrupts/attach/detach IRQ nesting3,
PIO program allocation2, hard_assertion_failure1 and hardware claim2. There is
no intended registered DCD/SOF/event-hook graph edge to those other13. Hard
assertion may be reachable in broader endpoint-open/init or software-task
contexts; all such intercepted unmatched panics must retain OTHER rather than
being silently dropped. Host-controller source has additional panic formats,
but CFG_TUH_ENABLED0 excludes that HCD code here. Source searches also find
unlinked SDK/platform/stdio/allocator panic routes; they are not inferred active
from source existence alone.

`__assert_func` is a separate _exit path and is not observed by panic interposition.
The actual DCD ordinary assert sites are removed under NDEBUG. TU_ASSERT queue
failure is boundedreturn/noop breakpoint here, not __assert_func/panic.
GNU --wrap rewrites undefined references; same-TU runtime
hard_assertion_failure -> panic may bypass it. Final descendant ELF must verify
all3 DCD destinations and retain this wider generic coverage limitation.

## Original panic and physical implications

Saved base ELF panic0x10041f24 pushes varargs registers, calls puts(banner),
viprintf(fmt,va_list), puts(newline), then _exit(1). `_write`0x10068998 is
`movs r0,#0; bx lr`: this pinned build discards libc output and does not call
Serial/USB from panic output. The puts/viprintf path is still not bounded:
puts reaches __retarget_lock_acquire_recursive -> recursive_mutex_enter_blocking;
newlib initialization/formatting can use locks/heap. A panic can thus stall before
_exit. Do not add those operations to the observer.

`_exit`0x10041eb4 is `bkpt0; b _exit`, not WFE. Weak isr_hardfault0x100030c4 is
BKPT0. These exact instructions prove no normal return, but debugger presence
and architectural exception/lockup behavior determine what executes after BKPT.
The source/ELF does not establish that _exit or HardFault was reached on the
reported controller. Panic/exit code has no explicit USB peripheral reset,
pull-up disable, core1 reset, or halt-other-core operation. It does not prove
that core1 stops. Continued core1 LEDs or later peripheral sticky SETUP are
compatible with core0 non-return, but that is an inference to test, not evidence
that a specific panic fired. USB/peripheral effects belong to separate physical
adjudication; no device operation was performed here.

## Transparent variadic panic ABI recommendation

Do not forward a va_list as `__real_panic(fmt,args)`; the original is variadic,
not vpanic, and doing so changes all unnamed arguments.
A naked ARM Thumb veneer is feasible with ONLY basic asm and stable extern-C
observer/wrapper symbols. Save R0-R3,R4,LR (24bytes), keeping incoming8-byte SP
alignment across the bounded C observer call. Observer receives fmt from R0 and
must itself return normally. Then restore original LR from saved offset20;
load real panic's Thumb function address into R4 then IP; restore R0-R4; discard
saved LR slot; BX IP. Incoming stack arguments remain at their original SP and
are never rewritten. R4 and R5-R11 survive, R0-R3/LR/SP restored exactly. IP/r12
and condition flags are AAPCS scratch. This retains all argument register and
stack varargs, including aligned64-bit arguments.

A direct `b __real_panic` in Thumb1 has short-branch range and must not be assumed
to get a linker veneer. Literal load -> IP -> BX is robust for arbitrary distance;
final address must have Thumb bit1. GNU --wrap=panic binds __real_panic to original.
The wrapped C declaration can be noreturn/naked/used/noinline; no C body,
compiler locals, generated prologue or epilogue is allowed. Final disassembly
must establish the exact save/call/restore/tail sequence, alignment, original
symbol target, and interception of each active DCD call. Build success alone
is not that proof. No implementation was written by this read-only role.

## Evidence hashes

- `efc5468860150a802ab5cf557a09e03e3ed4e879120ef9341b8667bb5e63a9e4` `/private/tmp/glyph-profile-store-rt2-setup-irq/.pio/build/glyph_mk6/firmware.elf`
- `877f97a626184470b06b96e71d83512c8a5f4dd0203ff067c30f06297c6d0af5` `/private/tmp/glyph-profile-store-rt2-setup-irq/.pio/build/glyph_mk6/lib09f/Adafruit_TinyUSB_Arduino/portable/raspberrypi/rp2040/dcd_rp2040.c.o`
- `0c40d39b3e10adea913980fa70b1c4a4ff187d382bf123c59946b3160cd7c07e` `/private/tmp/glyph-profile-store-rt2-setup-irq/.pio/build/glyph_mk6/lib09f/Adafruit_TinyUSB_Arduino/portable/raspberrypi/rp2040/rp2040_usb.c.o`
- `276cb0a43743368a148d4f8c809b06192da2bec1177bcfcf4d60ecaf718ba062` `/private/tmp/glyph-profile-store-rt2-setup-irq/local_backups/setup-irq/compile_commands.json`
- `0aa78013e54caef261f2fd38b12ac84ce16c8f1e5dcba5660be6846e888c8960` `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/package.json`
- `5d2bb442f356ca002791a435be291be741ef5f1923c9c20dcec9a7a4371c45fe` `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/libraries/Adafruit_TinyUSB_Arduino/library.properties`
- `adb8bc6ccbe9a2f14225658a251c194ef65488757aaf2b05a6d2340506ad07da` `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/pico-sdk/pico_sdk_version.cmake`
- `92a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12` `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040/dcd_rp2040.c`
- `81c24999f3ec9918723d4494619a9abdb2733a21d4bf39573a7c60eb461c5de6` `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040/rp2040_usb.c`
- `5f215d092223581d9de4dd0542aa4cc587d280b7cc85978571621cfb54125524` `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040/rp2040_usb.h`
- `c39f68050719aaa803b193206baf117cfe6e763e47065ed1ffbab745ada173a4` `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/libraries/Adafruit_TinyUSB_Arduino/src/device/usbd.c`
- `fae15a1c7f4fc2911e04243c5506ca44cd470ed202343498fb30993e8df02192` `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/libraries/Adafruit_TinyUSB_Arduino/src/osal/osal_pico.h`
- `c6b63ea7bebb1a0dc6b108664d048ed53ad61e9b04a4fae2439b6ba93891bb19` `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/pico-sdk/src/rp2_common/pico_runtime/runtime.c`
- `a4fd1520d9b4700befe02edc7e6c8c41b70a13cb5f9867ce7d52c68bede2036f` `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/cores/rp2040/posix.cpp`

## All direct panic call sites in saved base ELF

```text
1000a1bc <dcd_rp2040_irq>: 1000a3ee:	f037 fd99 	bl	10041f24 <panic>
1000a760 <_hw_endpoint_buffer_control_update32.part.0.isra.0>: 1000a770:	f037 fbd8 	bl	10041f24 <panic>
1000aa84 <hw_endpoint_xfer_continue>: 1000ab34:	f037 f9f6 	bl	10041f24 <panic>
1000af68 <_ZN7TwoWire6setSDAEh>: 1000afa4:	f036 ffbe 	bl	10041f24 <panic>
1000af68 <_ZN7TwoWire6setSDAEh>: 1000afbc:	f036 ffb2 	bl	10041f24 <panic>
1000afe0 <_ZN7TwoWire6setSCLEh>: 1000b01a:	f036 ff83 	bl	10041f24 <panic>
1000afe0 <_ZN7TwoWire6setSCLEh>: 1000b032:	f036 ff77 	bl	10041f24 <panic>
1003e3ec <main>: 1003e408:	f003 fd8c 	bl	10041f24 <panic>
1003eb8c <noInterrupts>: 1003ebb8:	f003 f9b4 	bl	10041f24 <panic>
1003ebc8 <attachInterrupt>: 1003ec88:	f003 f94c 	bl	10041f24 <panic>
1003eca8 <detachInterrupt>: 1003ed28:	f003 f8fc 	bl	10041f24 <panic>
10040c64 <_pio_add_program_at_offset>: 10040c9a:	f001 f943 	bl	10041f24 <panic>
10040d94 <pio_add_program>: 10040db2:	f001 f8b7 	bl	10041f24 <panic>
10041f54 <hard_assertion_failure>: 10041f58:	f7ff ffe4 	bl	10041f24 <panic>
100420ba <hw_claim_or_assert>: 100420d8:	f7ff ff24 	bl	10041f24 <panic>
100420f4 <hw_claim_unused_from_range>: 1004213a:	f7ff fef3 	bl	10041f24 <panic>
```
