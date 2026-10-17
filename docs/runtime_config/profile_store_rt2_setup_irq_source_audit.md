# Bounded pinned-source audit: raw SETUP → IRQ → DCD

Audit role: source-authority specialist delegated by root; read-only except this ignored evidence file. No controller operation, build, vendor edit, tracked edit, Git mutation, or publication. Requested model/effort was Sol/high; actual model/effort UNKNOWN absent runtime telemetry. This is source analysis, not physical acceptance.

Pinned repository: `3761b702ea09f50b9c98a55bea91caa337a3f62e`, tree `43f26381fd2b7b1f701c18aadc839d8f5143eedb`. Worktree is `/private/tmp/glyph-profile-store-rt2-setup-irq`. Concurrent implementer edits can appear in that worktree after audit began; original observer statements below refer to 3761, not moving uncommitted files. Existing exact3761 ELF/object and compile database were read from `/private/tmp/glyph-profile-store-rt2-comprehensive`, whose HEAD also verified 3761. Canonical named owner base remains 6b73a7c507f35c111745c6bdd341618b490cbdcd; no fresh remote assertion made by this specialist.

## Source names and exact target selection

Framework root F = `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico`.
TinyUSB root U = `F/libraries/Adafruit_TinyUSB_Arduino/src`.
SDK root S = `F/pico-sdk/src`.

Repo platformio.ini pins Arduino-Pico3.6.3; framework Adafruit library.properties is2.3.0; U/tusb_option.h:32–34 is TinyUSB0.16.0; F/pico-sdk/pico_sdk_version.cmake is1.5.1. Exact3761 compile database `local_backups/comprehensive/compile_commands.json` was used to repeat DCD preprocessing to stdout, without emitting a file. Result0:

- `CFG_TUSB_CONFIG_FILE="tusb_config_pico.h"`; repo HAL/pico/include/tusb_config_pico.h:49 selects `CFG_TUSB_OS OPT_OS_PICO`; numeric OPT_OS_PICO5.
- `F_CPU=130000000L`, `CFG_TUD_RPI_PIO_USB=0`, `CFG_TUH_RPI_PIO_USB=0`.
- `TUH_RHPORT_MODE OPT_MODE_NONE`, no TUH_OPT_RHPORT: hardware host path inactive.
- `PICO_DISABLE_SHARED_IRQ_HANDLERS=0`, `PICO_NO_RAM_VECTOR_TABLE=0`, shared priorities highest0xff and lowest0.
- PICO_RP2040_USB_DEVICE_ENUMERATION_FIX and PICO_RP2040_USB_DEVICE_UFRAME_FIX undefined; absent corresponding TUD options evaluate false. Existing observer has compile-time error if enumeration fix active.

Source SHA256:

| File relative F | SHA256 |
| --- | --- |
| libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040/dcd_rp2040.c | 92a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12 |
| libraries/Adafruit_TinyUSB_Arduino/src/device/dcd.h | 429bc790ad37e864ae0e0567e19f252edfe301988ac614239501d3569fdd050d |
| libraries/Adafruit_TinyUSB_Arduino/src/device/usbd.c | c39f68050719aaa803b193206baf117cfe6e763e47065ed1ffbab745ada173a4 |
| libraries/Adafruit_TinyUSB_Arduino/src/osal/osal_pico.h | fae15a1c7f4fc2911e04243c5506ca44cd470ed202343498fb30993e8df02192 |
| pico-sdk/src/rp2_common/hardware_irq/irq.c | a8ce7f79e707f3c41f8a2a062a6f7b8954bdef6cd834973a0b779f9f7a21bf36 |

## Exact linkage, registration, and minimal recommended interposition

U/portable/raspberrypi/rp2040/dcd_rp2040.c:246 defines `static dcd_rp2040_irq(void)`; :248 takes exactly one `usb_hw->ints` snapshot. :405 passes that private function address to external `irq_add_shared_handler(USBCTRL_IRQ, ..., 0xff)`. Public dcd_int_handler at:572–575 calls it but is NOT registered. Exact3761 ELF has lowercase local `t dcd_rp2040_irq` at1000a1bc; public dcd_int_handler is GC-absent. Wrapping dcd_int_handler will not observe normal USB dispatch.

Exact3761 DCD object relocation proof:

- `.text.dcd_init+0x18 R_ARM_THM_CALL irq_add_shared_handler`.
- `.text.dcd_init+0xcc R_ARM_ABS32 dcd_rp2040_irq`.
- `.text.dcd_rp2040_irq+0x8a R_ARM_THM_CALL dcd_event_handler` for SETUP.

Recommended source-owned `--wrap=irq_add_shared_handler`: while inside core0 port initialization only, intercept exactly USBCTRL_IRQ + highest0xff registration, capture its passed immutable function pointer, and pass one trampoline in its place to the real registration function, preserving number, order_priority, shared registration count and original call order. Existing port wrapper offers a scope; a nested dcd_init wrapper is stricter if desired but not necessary given exact sole highest-priority registration. The port's second registration U/arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp:111–112 is the LOWEST0 software-task trigger and must be forwarded unchanged. Do not add a new shared slot or register core1 USB handling.

The trampoline records bounded read-only core0 pre-dispatch MMIO/gate observations, calls captured handler exactly once, then records post-return state. Capture pointer before the real registration and before dcd_int_enable. Unexpected/duplicate matching registration must be an explicit instrumentation-invalid result, forwarded unchanged without recursion/replacing the original pointer with the trampoline. No allocation, mutex acquisition, IRQ disable/clear, queue/task call, logging, LED, timing wait or hardware writes in observation. Added calls/register reads change IRQ latency; this is a diagnostic perturbation and needs exact build/review, not a claim of zero impact.

SDK S/rp2_common/hardware_irq/irq.c:206–278 stores one handler per shared slot; priority chain ordering compares slots at:238. Replacing a slot's passed handler pointer preserves shared-chain structure and order; inserting a second handler does not. Audit later removal if introduced: exact current DCD does not remove its handler. A remove by original pointer would not identify substituted trampoline, so future lifecycle change invalidates this design.

Pre-dispatch observation establishes the existing shared chain called the replacement immediately before invoking original handler. It is not the vendor function's first instruction or its own local `status`. The original read is separate and later. Source/ELF confirm this gap must remain an explicit residual. A handler pre-sample cannot truthfully be labeled `DCD_STATUS_SNAPSHOT_SETUP`.

## Earliest external SETUP boundary and attribution

DCD:298–308 tests local snapshot, computes setup pointer, resets PID with static always-inline helper:218–228, invokes static always-inline dcd_event_setup_received, then clears SETUP_REC. dcd.h:211–215 builds stack event and copies8bytes from DPRAM before the external dcd_event_handler call. Exact object disassembly shows direct PID stores and DPRAM eight-byte load/store followed by external relocation+0x8a; no external EP0 reset helper exists.

Therefore `--wrap=dcd_event_handler`, recording SETUP before forwarding exactly once, is earliest safe external SETUP boundary. It proves branch passed PID reset and event construction/copy, and emitted SETUP into stack boundary. It cannot distinguish initial branch entry from failure in those inline/local operations. Wrapping memcpy/memset globally is neither an exact branch boundary nor warranted; setup copy is inlined in exact object.

U/device/usbd.c:302–305 queues then invokes tud_event_hook_cb even after enqueue failure; dcd_event_handler:1161–1162 reaches queue_event for SETUP. Existing3761 hook restricts port0/core0/exception21 (HAL/pico/src/core/RecoveryUsbDiagnostics.cpp:157–174), and its reset-epoch fields clear SETUP when RESET is emitted later in a combined snapshot. RecoveryTaskDiagnostics::State::SetupEvent has a separate sticky event flag. New pre-event observation should retain both unrestricted diagnostic attribution (actual core/exception/in_isr, with bounded banks) and narrowly matched USBCTRL/core0 attribution; do not silently drop a real external SETUP because the legacy attribution filter rejects it. Maintain boot-lifetime SETUP emission separately from current reset epoch to expose combined SETUP-before-RESET chronology. Queue acceptance and event-hook evidence remain distinct. Do not reinterpret prior physical evidence beyond owner-supported classification.

## Register semantics and safe observations

S/rp2040/hardware_regs/include/hardware/regs/usb.h:1001–1007: SIE_STATUS.SETUP_REC is WC, bit17. :2924–2930: INTR.SETUP_REQ is read-only bit16 with direct source SIE_STATUS.SETUP_REC. :3069 describes enable, :3102–3108 SETUP enable; :3247 describes force; :3425–3429 describes INTS after masking/forcing. Authority specialist separately verifies official RP2040 source. Normal static model: R is derived from S, M inferred=(R&E)|F; INTF is not an independent host packet and must be read/audited.

Independent sticky S/R/M/E observations are useful but not a temporal pipeline. Sequential SIE/INTR/INTE/INTS samples can straddle DCD clear, interrupt entry and hardware arrival. Separate ever-R and ever-E do not establish co-occurrence. A sample with S only or R+E without M is an observed skew/consistency tuple, not proof hardware stalled at a stage. Persistent coherent contradiction is not established by sequential reads. Include INTF and raw values in richer diagnostics when available. Do not make hardware-faithful tests assign RO INTR/INTS independently: derive from S/E/F, implement documented source clears, and mark deliberately inconsistent sampler tests synthetic.

NVIC and PRIMASK are per executing core. SDK irq.h:44–52 explicitly states one NVIC per core and APIs affect executing core. Core1 can sample shared USB registers and RESET_DONE, not core0 NVIC/PRIMASK/IPSR. Core0 must capture those into shared atomics at safe entry/foreground/existing wrapper points. Core1 then reads published banks. A stale core0 gate sample is not current core0 state. Pending may clear on entry; absence at wrapper entry does not mean IRQ was never pending. Entered exception21 itself proves dispatch occurred. The SDK enable routine clears pending before enable and documents asserted source immediately re-pending (irq.c:59–64). USBCTRL handling is level-source driven; pending-clear alone is not permanent SETUP loss while source remains asserted and gates later permit dispatch.

An arbitrary earlier reset IRQ does not establish IRQ delivery after later SETUP. Correlate raw-positive observation with handler sequence/epoch: e.g. core1 remembers entry counter at first raw-positive and later observes entry counter advance, or trampoline records pre/post SETUP-positive MMIO during a specific invocation. Clearly label same-read noncoherence. A first sample taken after emission/clear can miss all raw positives, so event proof supersedes negative sampling; never label negative sample as absence of packets.

## Relevant writer matrix

| State | Exact writer/caller | Target/relevance and limit |
| --- | --- | --- |
| USBCTRL reset, all MMIO/DPRAM zero including INTE/INTF/SIE | rp2040_usb.c:65–86 reset_block, unreset_block_wait, memset(hw), memset(DPRAM) | Called dcd_init:398 at startup. No application recovery reinit call found. ExactELF sole rp2040_usb_init caller dcd_init. Not bus-reset processing. |
| USBCTRL main/SIE/INTE initialization | dcd_rp2040.c:417–425 | main controller enabled, EP0 one-buffer control, full INTE assignment includes SETUP. |
| SETUP enable after init | dcd_rp2040.c:423; no other SETUP-specific INTE writer | Source continuously enabled barring whole-block reset/reinit, corruption or unknown hardware. No active app recovery path clears it. |
| Other INTE updates | dcd:285,458,484,490; rp2040_usb.c:236 | SOF bit only; :236 E15 compile branch inactive. No SETUP disable. |
| INTF | rp2040_usb_init memset only | No later active app/core/DCD INTF writer found. Read it nonetheless to avoid unwarranted assumed-zero interpretation. |
| SETUP latch clear | dcd:308 | Only active explicit SETUP_REC clear, after external setup event call returns. |
| RESET latch clear | dcd:341 | Clears BUS_RESET only, after DCD bus-reset event. Does not clear SETUP. |
| Other SIE clears | dcd:327,361,368 | CONNECTED (FORCE_VBUS_DETECT0 excluded), SUSPENDED, RESUME. Disjoint bits. |
| Device-address and EP state on BUS_RESET | dcd:338–340; reset_non_control_endpoints:230–244 | Address0, disable/zero NON-control endpoint state/reclaim data buffers, emit reset. Does not zero EP0, INTE or SETUP latch. |
| EP0 startup/PID/stall/transfers | dcd:408–410,218–228,499–508,533–560; rp2040_usb.c endpoint transfer helpers | Startup initializes EP0, SETUP resets local PID; transfer routines/EP0 stall affect DPRAM/endpoint state. None clears SETUP latch except :308. |
| USBCTRL NVIC enable/disable APIs | dcd:430–440→irq_set_enabled | enable called tud_init:448. disable exists in object but exact3761 linked ELF GC-removes dcd_int_disable and usbd_int_set. No linked ordinary USBCTRL disable path found. |
| Generic OSAL_NONE usbd_int_set(false) | osal_none.h:129–164→usbd.c:1170–1178 | INACTIVE for exact OPT_OS_PICO. Must not attribute its queue NVIC toggles to target. |
| Target PicoOSAL queue lock | osal_pico.h:119–127,146–148,161–163 | critical_section_enter/exit; sends and receives, including ISR producer, save/disable and restore local PRIMASK. Does not disable USBCTRL NVIC. |
| PRIMASK primitive | SDK hardware_sync sync.h:214–229,287–290,314–316; critical_section.h:61–71 | Inline save+disable; blocking spin until lock acquired; unlock restores saved mask. GNU symbol wrapping cannot observe every inline operation. Normal source balanced, duration not proven; lock never released/non-return/corruption remain residuals. |
| Arduino nested global masks | cores/rp2040/wiring_private.cpp:27–48 | Per-core15-deep saved stack; interrupts restores prior mask. Paired calls do not force masks on if prior state masked. |
| LittleFS program/erase | libraries/LittleFS/src/LittleFS.cpp:181–203 | noInterrupts→idleOtherCore→flash→resumeOtherCore→interrupts, paired on normal return. Read:173–178 is memcpy only. No source proof of leaked mask on normal return, no runtime-duration proof or universal hang exclusion. |
| Allocation masks | cores/rp2040/malloc-lock.cpp:28–52 | malloc/calloc/realloc/free wrappers pair noInterrupts/interrupts. Allocation not permitted in new IRQ observer. |
| Other-core lockout | cores/rp2040/RP2040Support.h:92–117,133–144 | FIFO recipient masks its own core while waiting for resume; if recipient core0 it affects USB delivery. Diagnostic core1 does no flash/USB/config operations. No proof this occurred in3761. |
| Resource watermark mask | repo ResourceDiagnostics.cpp:25–37 | Local initialization saves mask, fills bounded own-stack interval, restores. No USB NVIC write. |
| LED masks | pinned FastLED clockless_arm_rp2040.h:319–321 | M0 blocking fallback behind FASTLED_RP2040_CLOCKLESS_M0_FALLBACK; target explicitly0. PIO/DMA handler uses DMA11, no USBCTRL. Candidate static panel only dedicated PIO/FIFO, no global mask. |
| Arduino SerialUSB1200baud disable/reset | cores/rp2040/SerialUSB.cpp:189–192 | Entire file guarded !USE_TINYUSB at:23, INACTIVE target. Adafruit DFU route reset_usb_boot is explicit boot transition, not ordinary RT2 startup. |
| Hardware-host INTE/reset/NVIC writers | hcd_rp2040.c:393–403,490–498 | INACTIVE target; TUH_RHPORT_MODE NONE and exactELF no hcd symbols. PIO USB inactive too. |
| Core1 observer | original RecoveryUsbDiagnostics.cpp:75–80; RecoveryStartupDiagnostics.cpp:124–145 | Read-only USB samples + bounded atomic state reads, own PIO output; no USB MMIO/USB NVIC write, no read of core0 PPB state. |

Exact3761 ELF full irq_set_enabled/irq_remove_handler call-site scan: only dcd_int_enable passes USBCTRL5, called from tud_init. Other linked call sites select GPIO13 (Snes/GPIO SDK), I2C IRQs (Wire), DMA11 (FastLED), SIO15/16, hardware alarms, dynamic user IRQ26–31. Port's software IRQ enable is not USBCTRL hardware IRQ enable. SDK shared add/remove manipulate executing core's vector and briefly mask local IRQ via spinlock; current DCD never removes/replaces itself after startup. This is source/object audit, not protection against memory corruption/ROM/debugger/arbitrary unexpected writes.

TinyUSB task BUS_RESET processing usbd.c:519–523→usbd_reset:467–470→class resets/control reset does not call dcd_init/dcd_int_disable or modify INTE/SIE setup. Existing exact3761 physical reset completion/continued evidence remains valid. Current source does not support ordinary reset-drain NVIC disable claim.

## T0..T6 source-faithful timing matrix

Assumptions: inject an accepted SETUP packet/latch assertion (not arbitrary writes to RO registers); SETUP enable1, force0, controller remains running; distinguish controller BUS_RESET latch from whole-block reset; no unsupported erratum/hardware corruption; original IRQ eventually returns and local gates allow subsequent dispatch. BUS_RESET may remain latched after electrical reset ends, so setup arriving while its *pending bit* remains is not setup during a physical SE0 bus reset.

| Injection boundary | Current local status and behavior | Latch/event outcome |
| --- | --- | --- |
| T0 before internal status read | New SETUP contributes M if stable by read. If RESET also sampled, SETUP branch runs before RESET branch. | SETUP external emission→clear S, then reset emission→clear R. One SETUP emitted even if current-epoch legacy summary retires it. If injection races read, either current or next dispatch. |
| T1 immediately after status read | Reset-only snapshot stays reset-only; new hardware M does not retroactively alter local status. | SETUP skipped this invocation; software RESET branch never clears S. M stays asserted until subsequent SETUP branch, so later dispatch expected when gates permit. |
| T2 during SETUP branch | Reachable only if status already had SETUP. First event proceeds. Another SETUP can change DPRAM before inline copy or coalesce into S before clear. | Before/after-copy and before-clear cases may overwrite/coalesce a SECOND indication; first external event already occurs before S clear. Arrival after S clear leaves new S for next IRQ. This does not explain ZERO first SETUP emission. |
| T3 during BUS_RESET branch | Setup check has already passed; if reset-only status no setup this call. | Address/noncontrol cleanup and clear R leave new S untouched; next dispatch expected. |
| T4 after BUS_RESET status clear | Any new S is unrelated to cleared R. | S→Rsetup→M with enable; pending/re-pending and next dispatch expected. |
| T5 just before IRQ return | Snapshot immutable; no rescan. | New S remains; level IRQ causes following entry (possibly tail-chain). No SETUP clear in epilogue. |
| T6 immediately after IRQ return | New S appears between invocations. | Normal fresh IRQ, assuming gates. No source-supported permanent loss caused solely by snapshot ordering. |

If a current status includes SOF or BUFF_STATUS, those branches execute before SETUP (dcd:251–296); non-return there can prevent setup branch even with SETUP in private snapshot. The external pre-handler sample cannot distinguish this from another internal pre-event failure. Do not label pre-entry M positive as setup-branch entry.

Combined snapshot S+R does not leave unhandled positive S solely because RESET clears it: code clears disjoint bits. Sequential observation can see S before its handler emits/clears; absence of later emission after10s still requires gate/dispatch/internal/residual diagnosis. Software pending clear at enable cannot permanently erase an asserted level source (SDK comment); model re-pending appropriately. Actual packet acceptance, physical latch set-vs-clear same-cycle priority, APB synchronization, faults, and silicon internals are below this source model; do not fabricate cycle precedence from C.

## Clock and errata boundary

Exact3761 compile DB F_CPU130MHz and main.cpp:82–83 set_sys_clock_khz before TinyUSB init:105. ExactELF main1003d58c calls check_sys_clock_khz and1003d5a2 set_sys_clock_pll with130000kHz literal at1003d7bc. SDK clocks.c:171–175 configures USB48MHz from PLL_USB. Source scan across app/HAL/glyph/compiled dependencies finds no later system/USB clock writer; joybus examples contain setters but are not compiled target. FullELF direct clock_configure calls occur only in clocks_init and set_sys_clock_pll; only direct set_sys_clock_pll caller is main. Source-configured130>48; actual clock hardware state unmeasured. Authority specialist owns official E16/E15/B2 conclusions; do not claim no B2 erratum exists. E16 B2 condition clk_sys<=clk_usb is not supported by this configured path. E5 eliminated physically and disabled; no new workaround recommended.

## Residual and handoff

This design can establish independent raw-positive layer samples, sample tuples/gate context, original-handler dispatch before/after, external SETUP emission before queue, queue/hook/consume/control boundaries. It cannot establish the exact vendor local status value or earliest static inline branch entry without invasive vendor change or instruction-level probes. Core1 cannot independently see core0's live NVIC/PRIMASK. No firmware-only observer proves absence between samples, electrical host recognition, register integrity, actual bus waveform, or silicon internal signal routing.

Recommend keep those residuals, implement sole-registration substitution + pre-event boundary, minimally instrument sticky sample tuples with INTF, and test the source-faithful matrix separately from synthetic sampler permutations. Freeze one whole-color pair per spatially separated main button. Preserve no controller action/no canonical merge; exact human hardware remains required.

Delegation: guidance applicable yes; native capability available and this role is the bounded source-authority specialist. No nested child: this is already the finite delegated read-only subtask and root separately owns implementation/review/official-authority specialist. Actual model/effort UNKNOWN.
