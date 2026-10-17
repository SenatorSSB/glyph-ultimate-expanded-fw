# RT2 raw SETUP / IRQ diagnostic contract

Candidate only. No new controller action or accepted hardware outcome is recorded here. Root cause UNPROVEN; E5 remains unresolved and disabled. See [source audit](profile_store_rt2_e5_source_audit.md), [device adjudication](profile_store_rt2_e5_device_adjudication.md), and [hardware packet](profile_store_rt2_e5_hardware_packet.md).

## MB1 without serial or video

Only the existing MB1 pair is driven. No continuous refresh or new startup delay is added. The inherited PIO emission takes a bounded 200us per changed displayed state with IRQs enabled; this is observer perturbation, not a USB timing repair. No display/core1/gameplay initialization is added to recovery.

| Stable MB1 | Meaning in the latest processed DCD BUS_RESET epoch |
|---|---|
| Red | Repeated recovery loop not yet established; see startup phase |
| Orange | Repeated loop, no sampled pull-up and no later milestone |
| Yellow | Repeated loop and pull-up sampled, no later milestone |
| Magenta | DCD BUS_RESET, no raw SETUP indication observed in this epoch |
| Blue | Raw SIE SETUP_REC or INTR/INTS SETUP_REQ sampled; no DCD SETUP emission observed |
| Cyan | DCD SETUP event emitted; no eligible task control progress observed |
| Green | Successful device-descriptor submission or address control progress in the current attributable task epoch |
| White | Configuration completion or supported recovery inspection decoded in the current attributable task epoch |

All progression is sticky within an epoch. A newly processed DCD BUS_RESET starts a new epoch and may reduce the color; previously successful enumeration cannot mask the latest reset failure. A reset arriving during register sampling invalidates that mixed sample, and the next stable loop read supplies progress. Before a raw pending reset has been processed by the DCD, the observer conservatively suppresses advancement. If IRQ/task/foreground execution stops entirely, the last displayed state cannot prove continued observer liveness. No color proves host intent or bus electrical content.

Case A is MAGENTA: no SETUP raw state observed; this cannot distinguish host absence from hardware failure to latch. Case B is BLUE: a hardware setup latch was observed but DCD emission was not. Case C is CYAN: DCD emitted setup but attributable task control progress was not observed. Queue failure, task starvation and unsupported/stalled requests can all remain CYAN. GREEN is submission/progression, not proof of host acknowledgement. WHITE is configuration/decoded inspection, not ProfileStore mutation or a persistence PASS.

The baseline b075 color interpretation is different: BLUE combined SETUP/descriptor, CYAN address, GREEN configuration and WHITE inspection. Its MAGENTA independently overrides pull-up state, so MAGENTA does not prove pull-up was sampled ON. Version4 uses scratch namespace `0x52570000`; version3 `0x52560000` and legacy `0x52540000` remain recognized only as previous diagnostic values.

## Read-only normal Configurator fields

`recovery_startup_diagnostics_version=4`. The additive `ProfileStoreResponse` fields do not alter `Config`, `UltimateProfile`, storage records, selector semantics, persisted files, or write commands. Existing generic protobuf JSON output exposes the fields without changing the user's dirty local transport tool.

All names below have prefix `recovery_usb_`:

- `chip_version`, `rom_version`: exact SDK queries, current physical values (UNKNOWN until hardware).
- `e5_flags`: bit0 compile-enabled, bit1 chip version equals1, bit2 enabled AND eligible. This artifact enforces bit0=0 and bit2=0. B0/B1 produces2; B2 produces0. Unexpected values must be reported, not guessed from product age.
- `sie_status`, `sie_ctrl`, `intr`, `ints`, `inte`, `dev_addr`, `main_ctrl`, `ep0_in`, `ep0_out`: current sequential MMIO/DPRAM reads. SIE_STATUS includes raw SETUP_REC, BUS_RESET, CONNECTED and line-state bits; EP0 buffer-control words are read only, never acknowledged or modified.
- `seen_sie_status`, `seen_intr`, `seen_ints`, `seen_inte`, `seen_ep0_in`, `seen_ep0_out`: bitwise OR of samples in the latest observed DCD reset epoch. They are cumulative observations, not simultaneous snapshots. Hardware may change between reads.
- `seen_irq`: bit0 USBCTRL NVIC enabled observed, bit1 disabled observed; bit2 pending observed, bit3 not-pending observed; bit4 PRIMASK masked observed, bit5 unmasked observed; bit6 USBCTRL reset_done observed, bit7 not-done observed. Opposing bits can both be set at different times. The existing `irq_state` retains current USBCTRL/software-IRQ enable/pending, PRIMASK/reset_done, init/connection and dynamic software-IRQ identity encoding.
- `bus_reset_count`: boot-lifetime DCD reset epoch count. `setup_event_count`: DCD SETUP emissions in this epoch. `raw_setup_observations`: positive samples, not unique packets; each bank saturates, and their returned sum saturates.
- `task_entered`, `task_returned`: boot-lifetime core0 task entry/return counts, including IRQ and foreground calls. Entry/return count difference alone is not a deadlock diagnosis.
- `task_reset_count`: actual USB task control-reset calls completed. Only equality with DCD reset count permits task milestone attribution. A dropped reset queue event or unexpected UNPLUGGED prevents false task progress; it may conservatively withhold progress even if a later request executes.
- `reset_order`: boot-lifetime OR mask of source boundary at each DCD reset. bit0 before setup; bit1 setup entered before matrix start; bit2 first matrix sampling active; bit3 first matrix sample returned before recovery route; bit4 recovery route entered before publication; bit5 recovery publication marker passed. These are instruction-order markers, not microsecond timestamps. A reset between a real action and its following marker belongs to the prior marker. Route markers apply to the shared recovery function, including automatic entry; bit4 alone does not prove RT2 was held.
- `observation_valid`:1 only when no DCD reset changed epoch during this read. Even valid sequential register reads are not an atomic electrical snapshot. A mixed read is0 and does not advance LED progress.

`milestones` preserves existing bit positions and adds RawSetup bit4096. RepeatedLoop=1, sampled post-loop pull-up=2, BusReset=4, DCD Setup=8, descriptor=16, address requested=32/applied=64, config complete=128, current attributable mounted=256, inspection=512, IRQ task entered=1024/returned=2048. Task milestones are eligible only in the matching task/reset epoch; loop and IRQ-task counters remain boot-wide.

Raw IRQ sampling occurs from the pinned callback only on core0 USBCTRL IRQ and BUS_RESET/SETUP events, before DCD clears the corresponding status. Foreground sampling reads a separate single-writer observation bank. No lock, new interrupt masking, register writes, queue changes, device reset or timer callback is introduced. The observer does not snapshot the eight DPRAM request bytes because raw latch/event discrimination and real descriptor submission already establish the required boundaries without retaining a racing packet image.

The seven wrappers preserve original calls/arguments: `tud_control_xfer`, `dcd_set_address`, `dcd_edpt0_status_complete`, `tud_task_ext`, `usbd_control_reset`, `user_irq_claim_unused`, and C++ `TinyUSB_Port_InitDevice(uint8_t)`. Control milestones carry their captured reset epoch; task reset count must match, so pre-reset queued setup and reset-in-wrapper cases cannot falsely become GREEN. Counters are32-bit and intended for a bounded one-attempt boot; no claim is made across 2^32 reset/task calls.

## Validation boundaries

The host suite compiles pinned DCD init/reset/SETUP/control/address functions, actual USBD/CDC, and the real backend with sanitizers. MMIO alias semantics, NVIC scheduling, DPRAM/electrical packet completion and host traffic are explicit models. It cannot prove the physical chip revision, bus line state, host policy, restoration after E5, normal candidate enumeration or RT2 success. Those remain hardware NOT_TESTED. The normal read-only control is mandatory before the single candidate RT2 attempt.
