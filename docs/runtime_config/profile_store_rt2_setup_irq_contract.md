# Narrow RT2 raw SETUP / IRQ observer contract

Owner scope: attachment88c6e055, direct source task from exact3761b702ea09f50b9c98a55bea91caa337a3f62e (tree43f26381fd2b7b1f701c18aadc839d8f5143eedb, parentb1a50079d1e2b8bca5dc2848c84b4a3cabbb181a). Canonical6b73a7c507f35c111745c6bdd341618b490cbdcd is unchanged. H3 candidate instrumentation, no USB repair, source-agent controller action, vendor edit or canonical merge. Exact final identities/build/resources/review are bound by the preserved handoff, not this prebuild source document.

## Physical authority and correction

The direct owner reports exact3761 normal PASS, version3761b702, /dev/cu.usbmodem101, incarnation1/store166, accepted useful authority and Config unchanged, min-free1856/3716, heap7868/capacity73404. Exactly one RT2 yielded LF4 BLUE+BLUE, LF3 BLUE+OFF, LF5 OFF+ORANGE, black display and no matching host USB/serial after10s. No follow-up controller action. See profile_store_rt2_setup_irq_physical_adjudication.json.

`MB1_PAIR_ROLE_DECODING = PHYSICALLY_UNRELIABLE`. GREEN+UNKNOWN on MB1 supplies no critical task/reset fact. Menu buttons must never require individual LED roles in this packet. Do not infer task return from the old MB1 observation.

Reliable3761 evidence: one after-enable DCD reset through frozen capture; class/control reset completed and next queue-read attempt reached; aggregate raw SETUP positive, no DCD SETUP event established, no queue-full/loss observed; no descriptor/address/configuration progression; pull-up control bit ON, not electrical proof. Classification RAW_SETUP_OBSERVED_NO_DCD_SETUP_EVENT. Every task returned is unknown. Reset storm, single reset-handler non-return and TinyUSB SETUP queue-drop explanations are not supported for that boot. Keep466/5913/b075/88ab separate; E5 physically inapplicable on chip2/ROM3/B2. Root cause UNPROVEN, selection/Nunchuk NOT_TESTED.

## Register semantics and exact sampling

Pinned Arduino-Pico3.6.3, Adafruit2.3.0, TinyUSB0.16.0, SDK1.5.1. RP2040 SIE_STATUS.SETUP_REC bit17 is W1C; INTR.SETUP_REQ bit16 is read-only and sourced from SETUP_REC. INTE/INTF enable/force bit16 are separate writable controls. INTS is read-only masked/forced status. Reads are non-destructive. No observer writes these registers.

Normal stable model inferred from official definitions: R=S, M=(R&E)|F. This is not a disclosed cross-domain timing/coherency guarantee. SIE→INTR→INTS must not be sold as three independently latched stages. S1/R0 and R1/E1/M0 are sample patterns that can arise when sequential loads straddle clears/changes; they do not establish stable hardware propagation or masking defects. No synthetic hardware test may hold such impossible stable states as ordinary device behavior. Sampler-skew robustness cases must be labeled separately.

A raw word carries SIE1 / INTR2 / INTE4 / INTS8 / INTF16. Each bank records sticky positive bits and a32-bit set of exact sequential raw-word tuples (bitN means a sample of wordN). INTE-ever and INTR-ever do not prove simultaneous enabling. Conditions are computed within one sequential read interval and remain sampling evidence, not atomic hardware instants: SIE-without-INTR1, INTR-with-INTE-off2, enabled-INTR/no-INTS4, INTS/NVIC-off8, INTS/PRIMASK-set16, INTS/NVIC-pending32, INTS/NVIC-on/PRIMASK-clear64.

Core1 samples USB MMIO only. Its local NVIC/PRIMASK/IPSR do not describe core0 and are never used as core0 evidence. Core0 foreground and USBCTRL trampoline banks record their own USB NVIC enabled/pending, PRIMASK, exception state, reset_done, port-init-returned and TinyUSB initialization publication. No TinyUSB call or shared USB lock on core1. Nonpositive samples never establish a historical absence or continuity.

## DCD handler and SETUP branch boundaries

Actual registered dcd_rp2040_irq is static. Public dcd_int_handler is not the callback registered by this pin. Interpose external irq_add_shared_handler only inside actual core0 device-port initialization for USBCTRL; preserve irq/order and invoke the real registration once, replacing its one callback with a source-owned trampoline. Do not append a second handler or change shared IRQ priority. Trampoline calls the captured original exactly once, recording bounded read-only entry/pre/post/return evidence. Unexpected duplicate registration is forwarded unchanged and invalidates new diagnostic attribution.

The trampoline register sample is immediately around the real callback, **not its own local status=usb_hw->ints**. SETUP can change between these reads. No safe external helper exists for the static always-inline EP0 PID reset. The earliest safe external call is dcd_event_handler reached by inlined dcd_event_setup_received. A separate wrapper records SETUP entry before real queueing and return afterward, independent of the old hook's call and attribution filter. Unfiltered idempotent atomic flags record any port0 external SETUP entry/return and unexpected context (packed bits1/2/4), using store1 only and no multicontext counter/RMW. The strict USBCTRL counters retain their own single writer. A returned external call without old-hook attribution exposes an attribution gap; entry without return alone can instead be prequeue blocking. Existing FIFO wrapper records accepted/dropped SETUP separately; the hook records its own attribution independently. This distinguishes old-hook attribution failure from a missing prequeue event boundary.

IRQ entry counts alone include reset/other IRQs. A matching setup-positive pre-sample count and pre/post tuple history are separate; a prior reset IRQ cannot be presented as delivery of a later SETUP. Exact handler status snapshot and branch beginning before the external emission boundary remain DCD_HANDLER_STATUS_RESIDUAL / DCD_EARLY_SETUP_BRANCH_RESIDUAL. No DCD_IRQ_ENTERED_SETUP_NOT_IN_STATUS_SNAPSHOT or DCD_SETUP_BRANCH_ENTERED_NO_EVENT claim is permitted solely from a trampoline sample.

## Static human panel

Only three large main buttons are used critically. Source pixel map on GPIO11: MB1 pixels0/1, LF4 pixels2/3, LF3 pixels4/5, LF5 pixels6/7. MB1 is DARK in the final frame. Both pixels of each main button receive exactly the same color, so no orientation or within-button discrimination is required. Other LEDs are outside the panel.

Additional main pairs exist from pixel8 onward, but four main pairs plus leading menu pixels would need10 words; the existing joined FIFO admits8. Three main buttons preserve the established one-preloaded-frame implementation without a new streamed/CPU-refilled PIO path, DMA or altered LED timing. The source-proven button coordinates remain the same as the comprehensive contract. A still photo is optional, never video or transient sequence reading.

| Main button | One logical dimension | Settled color meaning |
|---|---|---|
| LF4 | Unordered ever-observed SIE/INTR/INTS bitset | OFF none; RED S; YELLOW I; ORANGE S+I; BLUE T; MAGENTA S+T; CYAN I+T; WHITE S+I+T |
| LF3 | IRQ-gate / dispatcher observation, priority applied over sticky positive evidence | OFF no raw; YELLOW raw with no stronger gate evidence; RED sampled INTR with INTE off; ORANGE sampled INTS/core0 NVIC off; MAGENTA sampled INTS/core0 PRIMASK set; BLUE sampled INTS/core0 pending; GREEN trampoline entry pre-sampled S/I/T; WHITE trampoline pre/post sampled INTS |
| LF5 | DCD emission / queue / downstream evidence | OFF none; ORANGE external SETUP event-handler entry; MAGENTA old SETUP hook observed; CYAN SETUP queue accepted; YELLOW task consumed SETUP; BLUE control began; GREEN descriptor/address milestone; WHITE configured-current or supported inspection; RED any SETUP drop overrides all |

S/I/T positives on LF4 need not be from one sample or packet. INTE and INTF remain exact telemetry, with mask evidence summarized on LF3. LF3 GREEN/WHITE are dispatcher-boundary evidence only; they do not prove the real handler snapshot or a given packet's delivery. LF5 GREEN groups descriptor/address, whose separate flags remain captured telemetry. Full counters and all gate conditions remain available if an endpoint exists. A later stronger color can conceal an earlier gate condition; no color claims that earlier masks never occurred. Snapshot/PIO unavailable is UNKNOWN, not proof of non-entry.

## Capture, concurrency and response contract

Retain independent core1 sampling until a valid bounded snapshot at/after10s from recovery handoff. Freeze new raw/IRQ snapshot together with retained task/reset/queue snapshot and the whole-button panel before one release publication. Retry rejected mixed-bank samples only on the next ordinary loop. No spin, heap, atomic RMW, new mutex, input scan, gameplay, persistence or normal display initialization. Single-writer sequence banks use aligned32-bit atomic loads/stores; helpers inside existing IRQ-masked intervals add real observer cost. No negligible-perturbation claim.

The dedicated PIO path preloads all8 words with its SM disabled and emits one frame, no CPU refill, blocking put, DMA, clock change or unchanged refresh. Inherited IRQ-enabled200us interval remains;8pixels take240us and finish independently, then stall low. No added startup sleep or USB timing repair.

Scratch3 uses new namespace0x525a, while0x5259 and earlier namespaces remain historical-valid. Its upper two selected nibbles correspond to dark MB1 and are0; low nibbles retain LF3 gate/LF5 event. It is a partial summary, not the full raw panel. Full32-bit Dashboard includes all8 wire-order pixels. Selectors0–2 and SDK4–7 remain untouched.

Old task/reset queue counters remain telemetry, including total/pre/first/current/post reset attribution and reset completion/continued markers. They detect a different reset branch when readback is available. The photo prioritizes SETUP/IRQ and does not separately expose reset count; absent serial leaves PANEL_RESET_HISTORY_RESIDUAL.

Volatile response-only fields129–155 carry version1, valid, captured and the new25-word snapshot. Existing owner schema approval and this bounded request authorize diagnostic response reporting; Config/UltimateProfile/Request/storage and mutation semantics remain unchanged. Backend uses a100-byte static cache under its existing sole core0/nonreentrant ownership. One captured/live choice controls both task/new snapshot and dashboard/times, preventing a mixed live/frozen response at publication. Existing raw USB fields remain separate live samples. Invalid new snapshots are labeled valid0.

## Errata, host trace and stop

Official RP2040 datasheet2025-02-20 build3184e62 confirms E5 fixedB2. E16 affects B2 event synchronization including SETUP_REC, mitigated when clk_sys exceeds clk_usb by>=10%. Exact source configures130MHz/48MHz before USB init and no later active clock writer is found, so E16 is source-path mitigated; actual clock malfunction is not measured. E15 host/IN corruption conditions are unestablished; host-only E3/E4 and B2-fixed E2/E5 do not justify a workaround. No new erratum fix or root cause is claimed. See source and official-authority audits.

HOST_PACKET_TRACE=NOT_AUTHORITATIVE. Native ioreg shows registry objects; unified logs show emitted software messages with no documented complete on-wire SETUP guarantee. Optional read-only host log alongside the SAME attempt is corroboration only; a missing log is not a missing packet. No sudo, driver install, boot args, kernel tracing or logging configuration change.

If reset completes and SIE is positive without sampled INTR/INTS, and source finds no writer/mask mechanism, do not claim a stable silicon propagation defect from sequential polling. Retain HOST_PHY_SETUP_RESIDUAL / RAW_REGISTER_SAMPLING_RESIDUAL and stop increasingly invasive firmware work unless a new safe discriminator exists. External USB protocol analysis or a genuinely authoritative host packet trace is the next route for host transmission versus PHY/controller latch. Similar handler-local-status and early-branch limitations remain explicit even when dispatcher delivery is observed.

Prepared packets: profile_store_rt2_setup_irq_device_adjudication.md (one ordinary read-only normal boot of stopped3761; replacement blocked on any mismatch) and profile_store_rt2_setup_irq_hardware_packet.md (exact new normal control then exactly one RT2, static main-button observation and bounded read-only capture, stop in place without endpoint). No GC, selection, cleanup, mutation/refusal campaign or second attempt. Hardware NOT_TESTED until owner reports the exact new artifact.
