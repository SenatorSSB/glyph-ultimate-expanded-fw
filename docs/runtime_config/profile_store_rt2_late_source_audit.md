# Bounded late-SETUP source-authority audit

Disposition: SOURCE_GATE_PASS_WITH_LIMITS. A second INTS observation after the original unhandled check is meaningful and is not source-rejected. This is permission to continue the separately authorized observer design, not hardware readiness, implementation acceptance, or a repair recommendation.

Scope: exact supervisor-supplied base d30e5250ef2e5e425cc0f217fd37247b484ca988 / tree259a311fe5f2ea5bee3fff9bb74600edcd883399 in /private/tmp/glyph-profile-store-rt2-late-setup; canonical6b73a7c507f35c111745c6bdd341618b490cbdcd unchanged. No Git operation was performed, so commit/tree identity is supplied authority rather than independently verified here. Repository pristine DCD bytes independently hash to92a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12. No package/firmware/controller/build/queue/publication action. Only this ignored local report and JSON were written.

## What the two samples establish

S0 is the immutable handler-local status at pristine dcd_rp2040.c:248. Every original branch consumes that local variable. S1 is one new read at the source normal-return boundary, immediately after pristine:371-374. Thus S0.SETUP=0 and S1.SETUP=1 proves a sampled change in masked/forced SETUP status within this particular invocation. It does not identify the exact physical packet instant, persistence throughout the interval, or hardware cause. Force/mask state assumptions matter: INTS alone is not unconditional proof of a fresh packet; preserve the existing no-force/no-new-mask-writer audit.

For a first late invocation N, a later published entry count>N proves another private S0 observation was published after N. Equality means no later private S0 was published by frozen capture, subject to publication validity and saturation guards. Entries are counted after S0, so an entry that has read S0 but has not completed its diagnostic publication is not yet visible. State this observer limitation. A later S0.SETUP positive is a distinct fact; a total boot SETUP count alone must not silently conflate an earlier S0 positive with a later one unless the branch is explicitly restricted to S0-count-zero histories.

d30e CYAN/OFF/OFF remains the owner-provided exact-boot observation: private S0 snapshots occurred, no S0 contained SETUP, retained RAW was positive, no private local-SETUP/downstream event. It does not demonstrate failure inside the skipped SETUP branch. It does not by itself order RAW against private entry/return.

## Official RP2040 authority (hardware, separate from ARM)

[RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf), build2025-02-20/3184e62-clean, §4.1.2.8.1 p390: accepted SETUP ends by setting SETUP_REC and enabled status triggers an interrupt. §4.1.4, table404 p403 marks SETUP_REC bit17 WC/reset0; table421 p416 marks SETUP_REQ bit16 RO, sourced from SETUP_REC, with INTS described as “Interrupt status after masking & forcing.” AppendixA p625 defines RO reads as value-returning and WC writes1 as clear; reading INTS has no documented acknowledgement/clear side effect. §2.3.2 p60 maps USBCTRL_IRQ to5 and connects it to each core's NVIC. These facts plus the exact SDK hardware-IRQ contract support the level-source expectation below. They do not disclose cycle-level USB-to-NVIC synchronization or set/clear arbitration. Ordinary bus reset and whole USBCTRL block reset must not be conflated.

The register model S=SETUP_REC; R=INTR.SETUP_REQ; M=INTS.SETUP_REQ; E=INTE; F=INTF gives stable-state inference M=(S&E)|F, not a silicon timing theorem.

## Exact pinned software writers and non-SETUP branches

Repository pristine vendor/diagnostics/tinyusb-0.16.0/rp2040/dcd_rp2040.c:
- :246-249 one initial INTS read, handled=0.
- :251-288 SOF branch optionally clears DEV_SOF enable and reads SOF_RD; no SETUP_REC write.
- :292-295 buffer branch calls hw_handle_buff_status. Its :189-216 buffer/endpoints flow writes buffer controls/status and endpoint transfer state, not SIE_STATUS.SETUP_REC.
- :298-309 SETUP branch emits the event at:307, then is the sole direct SETUP_REC clear at:308.
- :314-328 connection branch clears CONNECTED only at:327 (compile-time FORCE_VBUS guard).
- :332-347 BUS_RESET branch writes address0, resets noncontrol endpoint RAM/state, emits reset, clears BUS_RESET only at:341; endpoint helper:230-244 does not touch SETUP_REC.
- :357-368 suspend/resume clear SUSPENDED/RESUME only. :371-375 checks the original status and returns; there is no rescan, pending-clear or hidden original epilogue acknowledgement.
- :393-425 init calls rp2040_usb_init, registers shared IRQ, initializes endpoints, enables controller and SETUP interrupt. :430-439 enable/disable is separate NVIC gating.

Installed framework base /Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico:
- libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040/rp2040_usb.c:65-80 explicitly resets/unresets USBCTRL then zeroes register/DPRAM ranges at initialization. A whole-block reset can reinitialize latch state; it is not the ordinary DCD bus-reset branch.
- cores/rp2040/SerialUSB.cpp:23 excludes its USB hardware reset path under USE_TINYUSB; :182-196 contains the inactive1200-baud reset route. platformio.ini:96 defines USE_TINYUSB.
- pico-sdk/src/rp2_common/pico_runtime/runtime.c:67-90 excludes USBCTRL from initial generic reset mask; do not misclassify a symbol mention as an active runtime reset.
- installed rp2040 hcd_rp2040.c writes different host flags, not SETUP_REC; host DCD is outside this device path. No new host behavior claim.
- pico-sdk E5 enumeration file only changes PHY/GPIO-related routing, not SETUP_REC. Candidate E5 remains disabled/inapplicable by existing authority.
- installed device/usbd.c:467-470,519-523 ordinary task reset resets class/control state rather than reinitializing the hardware block.
- recursive source scan of repository C/C++/headers (including HAL) and relevant installed TinyUSB/SDK/Arduino sources found no other named SETUP_REC clear or arbitrary SIE_STATUS writer in the active candidate sources. Raw observers in HAL/pico/src/core/RecoveryUsbDiagnostics.cpp:67-92,133-173 only read these registers. This is a bounded source audit, not proof against corruption, ROM/debugger actions, arbitrary unexpected stores, or undisclosed hardware behavior.

Therefore no original non-SETUP software branch supplies a supported explanation for clearing a newly asserted SETUP_REC when S0 lacked SETUP. If S0 contains SETUP, normal branch execution can legitimately yield S1 clear. If another packet arrives before the original SETUP clear, indications may coalesce; this audit does not assign same-cycle priority.

Unknown: whether an electrical USB bus reset autonomously clears/reinitializes SETUP_REC in every phase, whether reset and SETUP race, and precise asynchronous/internal latch behavior. The inspected official register descriptions do not settle these. A test must retain BUS_RESET near late SETUP as context and must not assert hardware preservation solely because C clears disjoint flags.

## Cortex-M0+ architectural expectation

[ARM DUI0662A](https://documentation-service.arm.com/static/5f04aadfdbdee951c1cdc957?token=), §4.2.6 pp4-6/4-7, supports level and pulse inputs; entry removes pending, and a rising edge during active execution can pend again. For a level input still asserted at exception return, NVIC samples it and repends, permitting immediate re-entry. Quote: “the NVIC samples the interrupt signal.” Clearing pending cannot remove a still asserted level source. Disabled interrupts can still pend. §2.3.6 p2-19 describes eligible pending exceptions tail-chaining without unstacking. Same active IRQ cannot recursively preempt itself; enable/mask/priority eligibility still governs dispatch. Thus ISPR0 during an active ISR is not proof that a high peripheral source will fail to repend at return. ISPR1 is useful extra sampled evidence, not proof of completed return or a silicon cause.

This architecture describes the core, while the preceding RP2040 source/register authority binds the peripheral expectation. It does not independently prove physical USBCTRL signal integrity.

## Exact Pico SDK1.5.1 and shared return boundary

Official pinned source fetched read-only and compared byte-for-byte with installed files. Ordinary sandbox lookup failed DNS; permitted network-enabled retry succeeded. No authentication or Git state was changed.
- [irq.c](https://raw.githubusercontent.com/raspberrypi/pico-sdk/1.5.1/src/rp2_common/hardware_irq/irq.c):19500bytes SHA256a8ce7f79e707f3c41f8a2a062a6f7b8954bdef6cd834973a0b779f9f7a21bf36.
- [irq_handler_chain.S](https://raw.githubusercontent.com/raspberrypi/pico-sdk/1.5.1/src/rp2_common/hardware_irq/irq_handler_chain.S):2825bytes SHA256ac608575377af5dd9587559b647dfa646094e7366ef29a658bba37ab3aa1653e.
- [irq.h](https://raw.githubusercontent.com/raspberrypi/pico-sdk/1.5.1/src/rp2_common/hardware_irq/include/hardware/irq.h):15073bytes SHA2569e946d6f76b8178b3a0ad8c4f6368535e8deafceebffbad9454b75ac9a18bfaa.
- installed pico_sdk_version.cmake:3,6,9 =1.5.1.

irq.c:59-67 clears NVIC pending before enabling, then writes ISER; comment: “if IRQ is actually asserted, it will immediately re-pend”. Disabling writes ICER only. :70-73 force-pending writes ISPR. irq.h:277-287 documents clearing hardware IRQ state through peripheral registers; irq_clear writes ICPR and is intended for software IRQs. These are explicit API operations, not an automatic pending-clear in dispatcher return.

irq.c:206-277 builds a fixed executable shared chain: head enters first-slot stub; subsequent slots call callback and branch onwards; final slot pops return. irq_handler_chain.S:56-63 saves EXC_RETURN, puts slot continuation in LR and branches to callback; it neither reads INTS nor clears pending. :37-40 encodes later callback and final return. There is no automatic repeat/rescan loop within this chain.

Pinned installed Adafruit_TinyUSB_rp2040.cpp:95-112 registers LOWEST-order usb_task_trigger_irq after highest-order DCD; it pends USB_TASK_IRQ, a separate software interrupt. Therefore private function return is followed by shared slot continuation and at least this second callback in the normal chain before final EXC_RETURN. HAL/pico/src/core/RecoveryUsbDiagnostics.cpp:301-315 preserves original private callback/priority once and creates no per-invocation trampoline. Final candidate ELF must confirm actual routing/unique DCD and retained chain; this audit performed no build.

## Perturbation and wording requirements

Proceed with exactly one original S0 load and no intentional diagnostic operation/barrier ahead of it; minimal post-S0 entry accounting; original vendor body; original panic check; exactly one observational S1; bounded publication; normal return. No service/force/clear/rescan/loop based on S1. Remove obsolete per-branch marker calls. Existing SOF/transfer/event wrappers can still add latency when invoked; audit actual retained paths, not merely number of private hooks.

Post-S0 stores/barriers/calls extend the S0-to-S1 window and can create a newly sampled late transition which would have occurred after the pristine function returned. S1 publication/gate reads extend S1-to-machine-return latency. Compiler prologue/register allocation may shift even the original read. Exactly0 intentional pre-S0 diagnostics is not0 perturbation. Root/fresh review must answer whether final instruction/barrier deltas materially create the observed window; source cannot predetermine their magnitude. Reducing d30e's12 publications to two should be materially lighter only after final disassembly verifies it; no count or negligible-cost claim here.

Gate reads are sequential after S1, not simultaneous with it. Core0 aligned32 ISER/ISPR and MRS PRIMASK reads are observational, but their sampled values can change later. Core1 must not read them as core0 state.

Use source-return/late-read language. Case1 supports late SETUP sampled and no later private entry by frozen capture; it does not prove that exception return completed, that the signal stayed high, or that NVIC malfunctioned. Case2 supports a changed observation between late read and later S0, not a proven lost hardware latch/root cause. No-late result establishes only that S1 never caught SETUP; source permits events outside sampled windows or unseen transience. If no safe discriminator remains, software observability limit is honest; no escalating polling recommendation.

Required model boundaries: valid hardware source transitions rather than writing RO INTS, clear-on-WC behavior, no mandatory active-ISPR1, possible repend at actual exception return, optional gate masking, publication/saturation refusal, bus-reset hardware uncertainty and source-return/machine-return gap.

Delegation: already bounded read-only specialist; no nested specialist needed. Lane source/safety high bounded research; runtime observed model and effort UNKNOWN. Root retains implementation, source custody, build, fresh independent review and human exact-artifact gate. Root cause UNPROVEN; Nunchuk NOT_TESTED.
