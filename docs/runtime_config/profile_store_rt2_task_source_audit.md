# RT2 first-task source audit

Scope: exact88ab descendant, candidate diagnostics only. Root cause UNPROVEN.
No controller operation, task-drain policy change, persistence change or merge.
Pinned Arduino-Pico3.6.3 / Adafruit TinyUSB2.3.0 / TinyUSB0.16 / SDK1.5.1 remain
unchanged. Source hashes accompany the host report and final build evidence.

## Physical boundary

[Retained evidence](profile_store_rt2_task_physical_adjudication.json) establishes
normal88ab PASS and chip2/ROM3/B2. `E5_PHYSICALLY_INAPPLICABLE_ON_TEST_CONTROLLER`.
The one failed88ab RT2 ended RED/black/no endpoint. RED proves only repeated
recovery-loop observation was not established. It can have been latched before
first loop; it does not prove task entry, a reset, or a hang inside TinyUSB.
Historical b075 MAGENTA is a different boot; its reset/no-later-SETUP boundary and
pull-up caveat remain unchanged. Variability is observed; its cause is unknown.

## First-loop and queue path

Exact `SendReport` calls `ReadByte`; `_base_stream.available()` calls coordinated
`fillRx`. With an empty local cache it calls `serviceRx` before the guarded CDC
read and again afterward. Each service calls `TinyUSB_Device_Task`, whose
`mutex_try_enter(__usb_mutex)` either fails and returns or succeeds and calls
`tud_task_ext` before releasing the mutex. No serial connection or input byte
is required to enter this task. No wait for Serial/DTR appears in this path.
After the services and a zero-byte CDC read, ReadByte returns-1 and SendReport
returns. A nonempty cache bypasses this refill path.

`osal_queue_receive` under target OPT_OS_PICO ignores its timeout argument and
performs one FIFO read under a Pico critical section. An empty queue returns
immediately after lock acquisition. The enclosing `tud_task_ext` loop has no
event budget: it repeatedly receives/processes until the queue is empty.
Thus an individual receive is non-waiting for data, while one task invocation
can continue without a source bound if events keep replenishing it. This is
not proof that physical reset traffic can sustain that rate on this controller.
No physical event rate or time-per-reset upper bound has been measured.

The DCD hardware handler does not acquire `__usb_mutex`. It can preempt foreground
USB work and enqueue events except during short critical sections/IRQ masking.
The shared low-order trigger pends the software USB-task IRQ. That software
handler tries the outer mutex; if foreground owns it, it skips task processing.
This does not stop the independent hardware DCD from delivering more events.
The source therefore permits the requested mutex/queue-starvation interleaving.

Queue capacity is16 `dcd_event_t` entries, non-overwriting, with a distinct Pico
critical section. Full enqueue fails; the Pico OSAL `TU_ASSERT` returns false.
Target debug0 and Cortex-M0+ make its diagnostic print/breakpoint no-ops.
The caller does not retry or repair that lost event. The optional event hook
runs after the enqueue attempt even if it failed: emission is not acceptance.
A dropped RESET or SETUP can desynchronize software/progression and interfere
with enumeration in the model; this is a possible mechanism, not a physical
root-cause finding. No queue/drop behavior is changed by this candidate.

SUSPEND and RESUME are filtered before enqueue when `_usbd_dev.connected` is
false, and callbacks are also skipped in the task while disconnected. Repeated
suspend/resume alone therefore cannot refill a disconnected pre-SETUP task queue.
SETUP processing sets connected; reset processing clears the device state, so
SETUP/reset oscillation changes which suspend/resume events pass. SOF normally
bypasses the task queue, except a synthesized resume when suspended. BUS_RESET
is not subject to the disconnected suspend/resume filter.

The CDC FIFO read is not a host-data wait: it reads available bytes, then may
prepare an OUT transfer. However its FIFO and endpoint claim helpers have inner
locks; these are not unconditionally wait-free. The accepted outer-mutex
coordination prevents an ordinary USB task from concurrently entering those
same CDC sections. Hardware DCD queue operations use a different critical
section. No exact circular wait in the no-input recovery path was demonstrated.
Interrupt starvation, an unexpected held lock or corrupted state cannot be
ruled out by source-only analysis. Neither service pass is replaced or bounded.

## Every target reset callback

Target configuration compiles CDC1, MSC1, HID1, MIDI1 and VENDOR0. The additional
application-driver callback registers exactly one XInput driver, even in the
CDC-only recovery descriptor configuration. `configuration_reset` visits all
five drivers on every dequeued BUS_RESET/UNPLUGGED, not just opened interfaces.

| Driver | Exact reset work | Boundedness |
| --- | --- | --- |
| XInput | Empty `xinput_reset` | Returns directly |
| CDC | Clear interface prefix; clear RX/TX FIFOs; set TX overwritable | Fixed interface count, but FIFO helpers acquire initialized inner mutexes |
| MSC | Clear fixed interface structure | Fixed memory operation |
| HID | Clear fixed interface array | Fixed memory operation |
| MIDI | Clear interface prefix and RX/TX FIFOs | Fixed interface count, but FIFO helpers acquire inner mutexes |

None of these reset bodies waits for a USB packet, invokes an application data
callback or allocates memory. CDC/MIDI `_ff_lock` calls
`osal_mutex_lock(..., OSAL_TIMEOUT_WAIT_FOREVER)`; the Pico backend uses
`mutex_enter_timeout_ms`. It is therefore wrong to call every callback
unconditionally bounded/no-lock. In recovery, the outer USB mutex excludes
ordinary competing USB task/guard activity and core1 does no USB work. This
supports ordinary completion but is not proof against an unexpected lock owner.
The harness injects non-return at each class boundary rather than claiming a
real lock fault occurred.

After the driver loop, `configuration_reset` clears device/interface/endpoint
maps; `usbd_reset` then calls `usbd_control_reset`, a fixed control-state clear.
The pinned external `usbd_control_reset` callsite is only this static reset
routine. It is invoked for both BUS_RESET and UNPLUGGED. An after-real wrapper
marker establishes that this reset path's preceding callbacks and control clear
returned (under the valid initialized driver table); it cannot identify which
queued reset emission caused it. SET_CONFIGURATION's configuration reset path
does not call this control-reset helper. Queue loss and prequeued events remain
explicit attribution limits.

## Independent observer and lineage

Arduino-Pico launches core1 before application setup. Its `main1` calls setup1
once then loop1 forever. Recovery setup1 returns through `refused()` before
menu/RGB/display allocation. The existing boot mutex is released before the
first SendReport. A new recovery branch in loop1 can therefore run independently
of foreground USB task completion, under the same scheduling assumptions as
ordinary core1 execution. Existing stack-watermark sampling remains in place.

Core0 initializes/completes the dedicated PIO indicator, then release-publishes
ownership before publishing recovery boot state. After handoff core0 Mark no
longer reads legacy USB state or drives the indicator; it can still arm first
foreground capture on LoopEntered. Core1 alone reads the atomic observer and
writes the PIO/scratch3. It never takes the USB mutex, calls TinyUSB/Configurator,
changes input/config/store state, or initializes recovery display/gameplay.

Observer banks use aligned32-bit atomic loads/stores, no atomic RMW, allocation
or lock. Foreground/task/IRQ writers are serialized by their source contexts.
A bounded sequence check rejects mixed foreground/reset snapshots without a
spin loop; core1 retries on its next normal loop1 pass. Target probes show inline
loads/stores and DMB, not libatomic/spinlock helpers; final ELF verification is a
separate gate. These atomics and changed LED timing are diagnostic perturbation,
not proof of timing-neutral hardware behavior.

The first foreground task is armed only by recovery LoopEntered. Before-loop,
IRQ and core1 task calls cannot consume its identity. Entry/return publication
has small instruction windows around the real call, documented in the
[contract](profile_store_rt2_task_diagnostic_contract.md). First-call GREEN stays
latched; later-call stalls are outside that LED's scope and require serial
current-ID evidence if transport works. First-task reset counts and progress
use separate pixels to avoid a later marker hiding repeated-reset evidence.

The PIO path checks FIFO empty, disables only its own SM, puts exactly four
words into the four-word FIFO and reenables it. It never blocks on a FIFO put.
The inherited200us protocol interval runs on core1 after handoff, with IRQs
available; no startup delay is introduced.96bits take120us at800kHz and the
remaining low interval supplies the latch. The program stalls low on an empty
FIFO, so the pixel retains its state without refresh. Unchanged successful
states are not rewritten. Unavailable PIO or halted core1 remains UNKNOWN.

No functional USB change in88ab has been proven to cause its RED observation.
The new candidate remains a direct descendant. The retained d596/895/4ee
coordination, TX/RX, root reconciliation and persistence semantics are unchanged.

## Validation and non-models

The new sanitizer harness executes pinned task/reset code for all five target
classes, extracted actual DCD/port functions and the actual recovery loop1 branch
in an independent host thread. It covers no events; one/two/replenished/full-queue
resets; reset/SETUP; SETUP while active; locked soft task vs delivering hardware
IRQ; pre-first reset and foreground call; later active calls; unplug/filtering;
configuration/control and every class before/after stall boundary. Four mutants
remove the independent publisher, whole reset hook, first-invocation anchor or completion mark and
must fail. Publication hooks exercise reset-before-entry, during-entry and
post-return boundaries. Independent state stress checks100,000 transitions.

MMIO, NVIC, queue/inner-lock scheduling, electrical packet completion, macOS host
policy, real multicore fairness and physical reset/lock cause remain NOT_MODELED.
Host stall hooks are artificial test boundaries. ASan/UBSan does not itself
prove data-race freedom; the atomic design/source and target codegen are separate
proofs. Full results and exact build/resources/custody belong to final HANDOFF.
