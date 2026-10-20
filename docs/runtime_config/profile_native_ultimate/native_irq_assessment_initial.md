# Finite IRQ assessment for native P1 repair

**P1 cannot close using a 1,752-byte ordinary C chain and a single 296-byte USB allowance.** Actual pinned source and clean linked ELF show a feasible default-serial USB task plus higher-priority SysTick requiring at least **300 bytes**, and a source-feasible CDC completion/endpoint-claim path requiring **340 bytes**, before unmeasured ROM/helper costs. These are critical feasible lower bounds, not complete IRQ upper bounds. No firmware/source edit, build, target instrumentation, controller operation or broad test was performed here.

Evidence: exact source-identical fc563760 ELF SHA256 `51dad8fed79c8e5726827d7702c86db2e578cff3b4663e8a7d808e23b9343b5d`, independently hashed in the prior review and disassembled at `/private/tmp/glyph-native-review-final-elf.txt`. Source/hash manifest for this assessment is `/private/tmp/glyph-native-irq-sourcepins.json`. Original reviewed source remains9e16e1c; the anticipated repaired1,752 total is writer evidence, not an independently frozen/build-verified peak.

## USB task, hardware IRQ and priorities

Pinned `Adafruit_TinyUSB_rp2040.cpp:81–112` installs `usb_task_irq` as an **exclusive** dynamically claimed user IRQ, and a shared USBCTRL trigger. USBCTRL also has the DCD hardware handler (`dcd_rp2040.c:405`). Both external IRQs retain SDK default hardware priority0x80: actual linked `irq_init_priorities` at100405dc writes0x80808080 only to external NVIC registers, and neither installation changes that priority. Thus hardware USB and the deferred task do not ordinarily preempt one another at equal priority. They execute/tail-chain as separate activations; do not add their entire bodies together. Shared handler ordering255 versus0 determines order within one IRQ and is not NVIC nesting priority.

The hardware USB chain uses `irq_handler_chain_first_slot` at2000571c, which pushes8 bytes once and branches through handlers. The soft USB task uses an exclusive vector: **no shared8-byte stub** belongs on its path. Example hardware setup-event known frames are exception32 + shared8 + dcd_rp2040_irq72 + dcd_event_handler40 + FIFO write24 =176 before memcpy/other library work; callbacks are sequential where source and branches say so.

`RP2040Support.h:174` enables SysTick before application setup on core0. Its exception priority field is not set by that registration: `exception_set_exclusive_handler` changes the vector only, and the pinned M0PLUS_SHPR3.PRI_15 architectural reset is0 (`m0plus.h:906–921`). No linked ordinary source setter changing SysTick priority was found; FreeRTOS is not active on this build. SysTick therefore has source-established higher priority than default0x80 external IRQs and must be allowed to preempt their unmasked bodies. Its linked handler at1003f004 pushes12 bytes; with a nested architectural exception frame32 the increment is44. Exception stack alignment is8-byte (`m0plus.h:868`); up to4 extra padding per exception entry must be considered where the interrupted SP is only4-aligned. The critical complete-frame sums below are8-aligned before SysTick, so44 establishes their lower bound without adding padding speculatively.

## Feasible descriptor paths, without helper aggregation

Actual linked frames (ordinary BL calls, no frame-releasing tailcall):

| Default serial descriptor path | Bytes |
| --- | ---: |
| Architectural USB exception |32|
| usb_task_irq at10007770 |8|
| tud_task_ext at10009534 |112|
| tud_descriptor_string_cb at100072cc |8|
| getSerialDescriptor at10007214 |80|
| TinyUSB_Port_GetSerialNumber at100077f0 |8|
| pico_get_unique_board_id at10042a00 |8|
| **Known total before ROM memcpy** |**256**|
| Higher-priority nested SysTick |44|
| **Known nested lower bound** |**300**|

GET_STRING_DESCRIPTOR can be processed while the controller is configured; it is not restricted to first enumeration by the inspected control dispatcher. Configurator stream Guard scopes have ended before filesystem work, so its outer USB mutex does not suppress this task during CREATE. The task's own mutex_try_enter succeeds and later task processing runs with interrupts enabled. SysTick can arrive after pico_get_unique_board_id's push and before its ROM call.

The collector's16-byte descriptor callback is conservative here: the actual linked callback pushes8. For a **configured** serial string, the serial80 frame instead calls strcpy_utf16 with48; total software256 + first exception32 + nested SysTick44 =332. NintendoSwitch sets serial"1.0", but that branch is not independently established to coexist with Configurator CREATE on current initialization routes; do not use it as the necessary storage-overflow counterexample. The default serial300 path already suffices at the anticipated C total.

`tud_control_xfer`32 executes **after the descriptor callback returns**, so do not add it to either descriptor chain. Likewise the serial-ID and configured-string branches are alternatives, not simultaneous helpers. The default path ultimately calls the ROM memcpy trampoline, whose stack is not certified by the available source/ELF; its unknown cost is not needed for the lower bound.

## CDC completion/endpoint claim is another critical path

The actual linked ordinary-call chain for a TX completion with pending software TX data and a free endpoint is:

`usb_task_irq8 → tud_task_ext112 → cdcd_xfer_cb40 → tud_cdc_n_write_flush24 → usbd_edpt_claim8 → tu_edpt_claim16 → mutex_enter_timeout_ms24 → mutex_enter_block_until32`.

This is264 C bytes + architectural exception32 =296; higher-priority SysTick adds44 =**340**, before padding or any ROM/timeout helper cost. The32-byte mutex frame is retained even on the uncontended path; SysTick can preempt after its push and before cpsid. Endpoint `_usbd_mutex` is distinct from the task's outer `__usb_mutex`. `OSAL_MUTEX_REQUIRED` is enabled in the actual Pico OS configuration, and the exact ELF calls it. A direct OUT-preparation or ZLP endpoint claim omits the sequential flush frame24, yielding **316** nested bytes.

This is a conditional feasible branch, not a sum of every USB helper: valid CDC IN completion, nonempty FIFO and free endpoint are explicit source predicates (`cdc_device.c` TX-complete branch). Ordinary legacy Configurator response paths do not all wait for txSubmitted, so prior response bytes can remain pending when a following profile transaction starts; no script, malformed traffic or foreign producer is required. The current native ProfilePacketWriter's own successful finish normally drains its software FIFO, which must be respected when describing a particular preceding transaction. If a stronger invariant is used to exclude pending TX for a concrete phase, prove it across **all** current accepted Configurator response paths; do not assume it from ProfileStore replies alone.

## Flash mask window, SIO and timer context

LittleFS flash_prog at1000eba8 holds24 bytes and calls noInterrupts before ROM programming. noInterrupts at1003f858 pushes **16 bytes before cpsid**; that short pre-mask window can be interrupted. After interrupts() restores PRIMASK it also briefly holds8 bytes before return. Consequently a C-chain total that includes flash_prog24 but omits the pre-mask helper16 understates a feasible interruptible foreground prefix. ROM flash execution after masking must not be summed with a fresh maskable USB IRQ; inspect exact boundaries. SIO idle-other-core handling is a separate default-priority external IRQ, not another automatic nest inside USB; its own noInterrupts/restore windows and SysTick require separate bounds.

The default alarm hardware handler32 and alarm_pool callback80 are likewise separate external IRQ activations, with callback-specific indirect costs. No certificate for every callback, high-priority NES GPIO route, startup/recovery path, NMI/fault handler, ROM routine or whole core1 stack is claimed. NES explicitly raises IO_IRQ_BANK0 to0, but its backend is not silently assumed active concurrently with Configurator; console-detection temporary latch/clock handlers are detached. Enumerate actual enabled route-specific handlers when closing the final gate.

## Implication for the bounded repair

At the anticipated ordinary total1,752, default descriptor/SysTick gives **2,052** before padding/ROM, and CDC/SysTick gives **2,092**. If that1,752 includes flash24 but not noInterrupts16, feasible pre-mask totals rise another16. Therefore do not freeze/pass at1,752 using an exact-bound arithmetic fit or a4-KiB scratch-bank envelope. Continue only the authorized bounded stack-lifetime/static-workspace correction. This assessment does not authorize IRQ priority changes, SDK changes, masking whole transactions or resource limit increases.

Repaired final ELF must establish both the foreground prefixes and these unchanged library frames/call relationships, mask windows, actual enabled/nesting priorities, and a sufficient allowance for remaining relevant callbacks/ROM/interrupt paths under2,048. Separately bound native Poll→Observe/context/SHA and activation/validation. Actual target highwater/timing remains NOT_MEASURED. Keep this as resource evidence within the existing P1 review; no fresh architecture or reviewer-of-review cycle is needed.
