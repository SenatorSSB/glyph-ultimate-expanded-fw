# Finite mode-destination persistence IRQ upper, exact bcb9824b, 2026-10-21

**Use456 bytes as a conservative source-backed union IRQ allowance for core0 mode-destination persistence across the actual backend routes.** This includes two conservative exception-alignment pads. A layout may round it upward to512. It does not include the interrupted foreground or its pre-mask noInterrupts16. The existing Configurator/recovery348 remains a narrower route certificate; it is not silently transferred to the NES/other-backend persistence path. This result is stack accounting, not hardware acceptance or a USB/backend correctness/stability claim.

Exact linked ELF SHA-256 `3f43081cec177763abf9f1955f8a3686faa39fa4ca660a5de174a2d70ca62884`, candidate bcb9824bc00c6210babdf00675952deeda7f7c88. Source and exact symbol extents are those pinned by the adjacent core1 and initial IRQ/ROM reports. No source/SDK/build/device changes or additional fault images/tests occurred. All filesystem admission and fixed budgets remain as directed by the owner, including unrelated directories/positive orphans/PENDING_MOVE. Observed runtime model/effort UNKNOWN; requested gpt-6.1-sol/high.

## Actual persistence entry and producer/mutex scope

`config.cpp` loop invokes select_mode before its backend SendReport loop. The registered request_mode_destination calls persist_mode_destination, which loads/checks a candidate, changes the selected backend/default-mode fields and invokes SaveConfigIfGenerationMatches. ModeSelectionTransaction excludes Configurator and Unspecified, **not NES/SNES/Gamecube/N64**. Therefore a physical-console backend's active IRQs must remain allowed during those actual load/validation/save filesystem chains. The mode selector's persisted destination transaction and earlier USB report functions are synchronous core0 calls; no endpoint lock is held after return into this FS work.

The completed core1 graph has no CDC/HID report writer, TinyUSB task, __loop/yield, or endpoint claim/release caller. Its menu tud_disconnect is DCD-only. Source-owned SysTick/SIO/alarm/GPIO callbacks do not call endpoint claim/release. `_usbd_mutex` claim/release scopes unlock before transfer/return; the task's outer `__usb_mutex` is distinct. Equal-priority hardware USB cannot preempt deferred USB task. Consequently the same endpoint/FIFO uncontended-at-FS condition applies to this persistence entry: keep the32-byte mutex-enter frame, exclude its contended timeout-helper child44 here. This is specific to FS after returned producers; it does not certify arbitrary unguarded viewer/HID foreground API prefixes.

## Finite enabled handlers and priorities

SDK initialization sets every external NVIC priority0x80. Source installations affecting ordinary core0 are USBCTRL shared DCD+trigger, exclusive user USB task, exclusive SIO, default alarm IRQ3 and IO_BANK0 handlers. SysTick is enabled on core0 with reset priority0. Source's only external priority setter is NesConsole constructor, which sets IO_BANK0 to0. Its destructor does not restore priority. This upper deliberately permits IO_BANK0 at0 across the route union instead of deriving a new restrictive initializer-history assumption. GPIO shared-handler order controls sequential dispatch, not NVIC nesting.

Normal FastLED PIO DMA IRQ is installed on core1, not core0. The early MB1 bootloader FastLED route installs on core0 then reboots/enters bootloader before ordinary persistence; it does not coexist with mode-destination save. Wire uses master mode, which does not install I2C slave IRQs. The actual Gamecube/N64 joybus PIO drivers do not install a CPU IRQ. The active Mk6 input matrix polls GPIO; PCF8575 interrupt examples are not production callers. Active source/library searches locate only temporary console-detection attachInterrupt, NES/SNES raw handlers and FastLED's already-covered DMA installation. No additional arbitrary app callback is inferred from library APIs.

SysTick0 and IO_BANK0 when0 cannot preempt each other. Each may preempt a0x80 external handler where unmasked. Thus maximum ordinary maskable nesting is one0x80 activation plus one priority0 activation. Equal0x80 USB, alarm, SIO and default-priority GPIO activations execute/tail-chain sequentially. Do not add their full bodies to each other. A later priority0 GPIO may execute after SysTick returns but cannot retain SysTick's frame at its deepest body, or vice versa.

## Exact GPIO callback graph

Every shared IO_BANK0 activation retains the single SDK8-byte shared stub. Source raw NES/SNES callbacks and gpio_default_irq_handler are sequential children of that stub; even if a conservative route union keeps more than one, use their maximum, not their sum.

| Exact function | Address | Own bytes | Maximum retained child |
|---|---|---:|---:|
| LatchIrqHandler (NES) |200004fc|16|nes send32 + PIO init16 =48|
| SnesLatchIrqHandler |20000558|8|SNES send24 + PIO init16 =40|
| nes_device_send_packet |10005ee4|32|pio_sm_init16|
| snes_device_send_packet |10005f20|24|pio_sm_init16|
| pio_sm_init |10043a40|16|0, register-loop leaf|
| gpio_default_irq_handler |10041fbc|40|Arduino dispatcher subtree72|
| _gpioInterruptDispatcher |1004141c|32|CoreMutex constructor subtree40|
| CoreMutex constructor |10041938|24|max(veneer4+mutex_try_enter8, veneer4+mutex_enter_blocking12)=16|
| CoreMutex destructor |100419a4|16|veneer4+mutex_exit0 =4|

The constructor/destructor branches are sequential;40 dominates destructor20. CoreMutex follows the non-RTOS branch. It does not allocate or recurse there; hardware mutex wait is a fixed frame. We conservatively include the blocking branch even when actual sole-caller ownership would rule it out. The emitted GPIO dispatcher inlines map lookup; there is no recursive tree function or allocation child. Source console-detection callbacks `latch_irq_handler`/`clock_irq_handler` are leaf counters, and both are detached before backends run. The GPIO map is empty at ordinary mode-destination persistence, so its CBInfo callback BLX cannot call arbitrary user code. Even allowing those two known counter targets adds0. No production code registers another Arduino GPIO callback.

SDK gpio_default_irq_handler skips pins claimed in raw_irq_mask and dispatches the remaining events through the single registered callback. This report intentionally retains its full112-byte default/dispatcher/mutex subtree even where pin masking or detached callbacks could reduce it. Inherited priority and stale pending NVIC events therefore need not be excluded to use the bound.

NES C subtree64, SNES48, default112 -> GPIO C maximum112. Including shared stub8 and architectural exception32 gives **152 bytes**. First-entry alignment4 ->156 as a standalone priority0 activation. The tighter NES raw-only value is104 before alignment (108 with alignment), but456 uses the larger conservative default subtree, not the tighter raw-only assumption.

## USB descriptor/callback union

A physical backend may retain a descriptor initialized during console detection. This upper does **not** assume USB disappears when NES/SNES/Gamecube/N64 is selected, nor that an interface was removed by deleting a backend. It admits every source-registered class: CDC, composite HID from DInput/keyboard/Switch, and XInput/vendor. The only HID object is the static TUCompositeHID object; its get/set report callbacks stayNULL because the application has no setReportCallback caller. MSC/MIDI drivers are compiled and their reset callbacks execute sequentially, but no source registers those interfaces, so their transfer/control callbacks are not selected by local descriptor-to-driver binding. Host requests do not supply new local descriptors or function pointers.

The largest deferred-task C chain remains264:

`usb_task_irq8 -> tud_task_ext112 -> cdcd_xfer_cb40 -> tud_cdc_n_write_flush24 -> usbd_edpt_claim8 -> tu_edpt_claim16 -> mutex_enter_timeout_ms24 -> mutex_enter_block_until32`.

CDC IRQ TX FIFO read mutex and RX FIFO write mutex areNULL by cdcd_init; their read_n32/write_n48 paths add only ROM memcpy<=12, not the56-byte mutex child. Other FIFO lock sides/reset paths are uncontended here and smaller. All official B0/B1/B2 memory bounds and sequential timeout-helper distinctions from the initial report apply unchanged.

Additional actual class bounds below task's own120 bytes:

* XInput control/init/reset callbacks are stackless; transfer8 -> endpoint16 -> DCD8 -> hardware start24 -> ROM memcpy12 =68; open32 -> endpoint open16 -> DCD open24 =72. Vendor16 -> tud_control_xfer32 -> endpoint16 -> DCD8 -> hardware start24 -> ROM12 =108.
* HID transfer24 -> max(set-report callback16, endpoint16+DCD8+hardware24+ROM12) =84. HID control32 -> max(null get/set report callback16, tud_control_xfer32+endpoint16+DCD8+hardware24+ROM12)=124. Open32 -> endpoint-pair40+DCD open24 =96. Completion-wrapper16+control32+callback16=64. All <=CDC144 below task120.
* Configured serial path uses callback8+serial80+UTF16 helper48=136, belowCDC144; default serial callback8+serial80+ID8+unique-ID8+ROM12=116. The control-transfer child executes after the descriptor returns and is not added to it. Nintendo Switch's serial"1.0" is covered by the configured branch.
* Per-class reset/init dispatches are sequential; the compiled reset callbacks, weak/null lifecycle callbacks, and CDC DFU reset request remain below264. ROM reset8 -> watchdog8 is bounded16 acrossB0/B1/B2.

No USB ISR callback in this finite graph re-enters mode destination/FS. This bounds stack across the declared callback union; it does not assert USB descriptor lifetime or concurrent backend behavior beyond the source-backed call/ownership facts required for stack accounting.

## Feasible witness is separate from the conservative union

**456/512 is a safe union allowance, not a demonstrated source-feasible maximum and not a lower-bound witness for conditional layout repair.** In particular, do not infer a need for a mode-header change merely by adding456 to foreground storage use. The independent foreground review must pair a source-feasible interrupt prefix with its exact unmasked persistence prefix and candidate frame sizes.

For an ordinary detected NES route, Arduino dispatcher72 is excluded from actual latch events. The Mk6 pinout is data8/clock9/latch10. detect_console attaches only latch10 and clock9, then synchronously detaches both before backend installation. _detachInterruptInternal disables all four event bits and erases each map entry. No other production attachInterrupt/attachInterruptParam caller exists. The non-RTOS mutex has no competing core1 GPIO map writer. The SDK callback pointer/default shared handler remains installed; detach does **not** clear it. But NES then enables only rising latch10 and raw_irq_mask claims10. gpio_default_irq_handler explicitly skips events on raw-owned pins. Therefore its Arduino callback/constructor subtree is not entered from NES latch events. A stale pending NVIC activation without enabled non-raw events can scan the default handler but cannot call the dispatcher; it does not realize112. NES constructor sets IO_BANK0 priority0; detection already enabled the NVIC line. Raw LatchIrqHandler then has its concrete104-byte activation: shared8 + exception32 + Latch16 + send32 + PIO init16. Its RAM-to-flash veneer transient4 is popped before tail BX to send; it does not remain under send/PIO. The pio_sm_init leaf has no further BL or dynamic SP allocation.

A concrete interrupt witness requiring no CDC TX producer is **360 bytes**, before optional architectural alignment: USB task8 + tud_task_ext112 + string callback8 + getSerialDescriptor80 + TinyUSB_Port_GetSerialNumber8 + pico_get_unique_board_id8 =224 C bytes; first exception32; nested raw NES104. Exact stopped instruction can be pico_get_unique_board_id at1004491a after its push, before the memcpy call. All original caller frames are live there, with no new USB mutex/ROM child or GPIO mask. NES nesting reaches pio_sm_init after its push at10043a42. No SysTick is added at this priority0 NES peak. This witness deliberately does not use the ROM memcpy upper12 as if it were an observed/mandatory frame, or rely on a four-byte alignment pad.

Source-created route predicates for that witness: a valid Config selects XInput as the USB default; initial backend choice is unspecified so initialize_backends registers that default before detect_console; USB is initially disconnected, allowing NES pulse detection; backend replacement installs NES while TinyUSBDevice's default serial descriptor remains NULL; a host can subsequently connect and issue standard GET_DESCRIPTOR STRING index3 during unmasked mode-destination persistence, while a NES latch edge occurs during that descriptor callback. XInput sets only VID/PID, not serial; the source serial override belongs only to the alternative Switch initializer. The descriptor dispatch uses the global TinyUSBDevice serial state, not a deleted XInput object's transfer callback. The task handles the standard descriptor even in steady operation. Host requests and console edges are possible external inputs; no likelihood/timing/highwater observation is claimed. No CDC/viewer TX is needed: NES has no secondary viewer, so the264-byte CDC completion/flush chain is **not claimed feasible on this NES route** without an actual queued-TX producer proof. The safe456 union still admits it for upper-bound accounting.

The360 witness alone makes a total exceed2048 only when the independently established, simultaneously unmasked foreground exceeds1688. It is not a universal IRQ lower bound, nor permission to sum masked flash/heap descendants with the IRQ. For direct-selected NES startup that skipped detection, IO_BANK0 enablement needs its own predicate; this witness specifically uses the detected NES path above. Other backend/descriptor histories may have different feasible maxima and do not strengthen this witness merely by belonging to the conservative union.

## Final nesting and alternative maxima

| Activation / nesting alternative | Conservative bytes including alignment |
|---|---:|
| Deferred USB plus priority0 GPIO |264 + first exception32 + GPIO152 + two pads8 = **456**|
| Deferred USB plus SysTick |264 +32 +44 +8 =348|
| Hardware USB plus priority0 GPIO |DCD/event/FIFO/ROM148 + shared8 + first32 + GPIO152 +8 =348|
| GPIO at0x80 plus SysTick |GPIO C112 + shared8 + first32 + SysTick44 +8 =204|
| Standalone priority0 GPIO |GPIO C112 + shared8 + first32 +4 =156|
| Alarm fixed16-node recursive heap (masked) |332 + first pad4 =336|
| Unmasked alarm/pool plus priority0 GPIO |hardware32+pool80+first32+GPIO152+8 =304|
| SIO pre-mask plus priority0 GPIO |handler16+noInterrupts16+first32+GPIO152+8 =224|

Therefore456 dominates the ordinary mode-destination persistence route union. No simultaneous SysTick44 is added on top of GPIO152, and no further0x80 IRQ nests in the deferred USB activation. A newer IRQ priority/handler/callback source change would invalidate this proof and is not authorized as a repair.

At a foreground prefix ending in LFS flash callback24, include the actual noInterrupts16 pre-mask child before adding456 if that prefix did not already contain it. Once masked, compare flash separately: SDK flash40 + largest ROM child88 =128 below the retained LFS callback. Neither a new priority0 GPIO nor USB is added to that masked flash/heap peak. This extension supplies an IRQ allowance; the independent reviewer must still establish actual foreground/FS repair co-liveness and the final exact candidate must satisfy2048. Existing violations in another retained foreground are neither repaired nor relabeled PASS by this accounting.

No target timing/highwater was measured. Nunchuk remains NOT_TESTED; root cause remains UNPROVEN; exact human hardware PASS, source review/build/custody and all original acceptance gates remain unchanged.

Official ROM ELF/source copies retain original copyright/licenses in `/private/tmp/glyph-bootrom-NOTICES-20261021.txt`, with exact URLs, source SHAs and file hashes in `/private/tmp/glyph-bootrom-license-provenance-20261021.json`. The prior already-hashed core1 and IRQ manifests remain unchanged.
