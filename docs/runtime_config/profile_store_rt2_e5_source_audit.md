# RT2 E5 / reset-to-SETUP source audit

Status: candidate-only diagnostics; E5 remains a high-priority hypothesis, root cause UNPROVEN. Actual controller silicon revision UNKNOWN. No controller action, E5 workaround, persistence semantic change, or canonical merge is part of this source pass.

## Decision and primary sources

`MULTI_PROFILE_STORE_RT2_DCD_DIAGNOSTIC_READY — E5_DEFERRED_GPIO15_TIMING_UNBOUNDED` is the truthful disposition once the separate build/review/custody gates pass. None of the user's three conditional labels fits an unresolved E5 hypothesis whose official fix cannot yet be bounded safely. This is not E5 rejection and not an E5 A/B artifact.

The exact installed Arduino-Pico 3.6.3 package is `framework-arduinopico` version `1.30603.0`, with Adafruit TinyUSB 2.3.0, TinyUSB 0.16.0, and Pico SDK 1.5.1. Source hashes and target definition evidence accompany the result. Official primary sources consulted online:

- [Pico SDK 1.5.1 platform header](https://github.com/raspberrypi/pico-sdk/blob/1.5.1/src/rp2_common/pico_platform/include/pico/platform.h), chip/ROM documentation.
- [Pico SDK 1.5.1 platform implementation](https://github.com/raspberrypi/pico-sdk/blob/1.5.1/src/rp2_common/pico_platform/platform.c), SYSINFO CHIP_ID revision extraction.
- [Exact SDK E5 implementation](https://github.com/raspberrypi/pico-sdk/blob/1.5.1/src/rp2_common/pico_fix/rp2040_usb_device_enumeration/rp2040_usb_device_enumeration.c) and its adjacent header, requiring entry from bus-reset IRQ.
- [Official RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf), revision build `3184e62-clean`, 2025-02-20; sections 4.1.2.8.5 and RP2040-E5 (printed pp. 631–632).

The exact header maps `rp2040_chip_version()` 1 to B0/B1 and 2 to B2. It extracts SYSINFO.CHIP_ID.REVISION, not the ROM version. `rp2040_rom_version()` reads byte address 0x13: 1=B0, 2=B1, 3=B2. The datasheet says E5 affects B0/B1 and is fixed in B2. An unexpected future chip number is reported numerically, not silently treated as a known revision. The SDK predicate is exactly chip version 1; the actual controller's eligibility must be read in the next normal control.

E5 requires a post-reset idle-J interval that other traffic can disrupt. Its described class is consistent with reset received/no observed SETUP, but this does not establish that the physical bus was busy, that the chip is affected, or that E5 caused the failure. Normal-mode enumeration does not by itself disprove E5.

## Official workaround and why it stays disabled

The DCD `rp2040_usb.h` macro chain copies `PICO_RP2040_USB_DEVICE_ENUMERATION_FIX` to `TUD_OPT_RP2040_USB_DEVICE_ENUMERATION_FIX` when the former is defined and the latter is not. The DCD's `#if` treats an absent option as zero. The diagnostic translation unit includes this same pinned header and rejects compilation if the option evaluates true. Reported enabled/would-execute bits are therefore zero by build invariant. The exact SDK fix is not compiled into a new source copy or linked as an enabled call. Existing SDK archive contents alone would not prove binding; final ELF symbol/call inspection is required and records absence of active fix binding.

The SDK function first checks B0/B1 support at compilation and `rp2040_chip_version()==1` at runtime. It waits for SE0 to end, then uses GPIO15's USB debug input mux to force J for approximately 1ms, waits for CONNECTED, and restores PHY mux and GPIO state. No approximation or altered workaround is implemented.

Default SDK alarm-pool configuration is enabled, hardware alarm 3, capacity 16. Runtime initializes the default pool before Arduino main; the final exact-target preprocessing receipt must confirm these defaults separately. `add_alarm_in_ms(..., true)` may return an alarm, may invoke an already-due callback synchronously, or return failure when no slot exists. Successful asynchronous scheduling returns from the USB IRQ before GPIO ownership ends. The timer callback runs on the pool's owning core (default startup core0); it does not reserve GPIO15 against foreground reads. `alarm_pool_add_alarm_at` releases its lock before invoking a due callback. That avoids a simplistic same-lock callback deadlock claim; it does not bound USB completion.

SE0 polling repeats every 1ms with no retry limit. The fallback spins while SE0 remains, with no timeout. The J hold fallback uses `busy_wait_us(1000)`, but the subsequent CONNECTED loop has no timeout. Timer lateness, interrupt masking, contention, or a missing hardware transition means no finite worst-case duration can be proven. The official implementation also uses one static saved GPIO-control/pad pair with no in-progress guard; another reset while asynchronous work is pending is not serialized by this function. USB shared-handler priority orders DCD before the task trigger within one IRQ; it is not NVIC preemption priority. Timer/USB default NVIC priority does not make foreground scanning safe while asynchronous ownership persists.

Disabling the default timer pool only to force synchronous busy waits would change execution timing and still leave unbounded waits; that is not adopted as a safety solution. A runtime gate set after RT2 sampling cannot cover a prior reset. A gate set globally before that sample cannot know the eventual RT2 versus MB1 decision. A GPIO lease/interlock, altered startup sequencing or modified timeout workaround would be additional behavior requiring its own supported design and review.

## GPIO15 matrix audit

Exact source: `config/glyph/common/src/config.cpp` constructs `matrix_input` with `DiodeDirection::COL2ROW`. `config/glyph/glyph_mk6/include/matrix_definition.hpp` defines columns `{15,14,13,12,16,17,21,20,19,18,22}` and rows `{26,25,24,23}`. GPIO15 is the input column for MB1, LF3, LF4 and LT5; RT2 is row3/column6 (GPIO21).

1. Scanning can overlap asynchronous workaround ownership. GPIO15 is read, not reconfigured, during COL2ROW scans; rows are driven in turn. There is no GPIO15 ownership interlock.
2. The first scan is in core0 `setup()`. Ordinary fast/all input updates are through core0 communication-backend report processing. Core1 handles display/RGB and waits for boot publication; it does not perform matrix updates. Recovery report processing skips normal input updates. This does not protect the initial core0 sample or later normal-mode scans.
3. USBCTRL IRQ is installed/enabled during TinyUSB initialization on core0 before setup. Foreground matrix scanning does not globally mask interrupts; USB IRQ can interrupt it. The workaround may then return before the timer path releases GPIO15.
4. The workaround sets GPIO15 INOVER_HIGH; `gpio_get()` reads the overridden input. Active-low matrix presses on that column can therefore read released. `DebouncedSwitchMatrixInput` accepts a changed sample immediately when its lockout has expired and then locks for 5ms; this is not a 5ms stability filter. A ~1ms disturbance can create a false release that persists through the lockout.
5. The first sample is after TinyUSB attach, core1 launch and the Arduino framework's existing startup work. A reset/workaround can precede or overlap it; no host scheduling guarantee excludes this.
6. MB1 can be falsely absent, bypassing its intended priority. RT2 uses another column and is not directly forced, but `inputs.rt2 && !inputs.mb1` can still select the wrong route when both are held. The first debounce state starts released, so a missing initial MB1 press is particularly consequential.
7. Later host resets can run during ordinary gameplay/report input scanning if the fix is globally enabled. Its global DCD placement is not limited to RT2 or boot.
8. The official code saves/restores the full GPIO15 CTRL and PAD words. It does not alter SIO output-enable/direction or output latch; GPIO15 remains a matrix input in this configuration. Restoration is exact for those saved registers only if the finish path returns and no overlapping invocation overwrites the static saved values. It restores USB muxing to PHY/SOFTCON and clears DP pull-up override, but does not restore every USB register to a saved prior word. GPIO16 must not select function8; Mk6 GPIO16 is another SIO input, satisfying that source precondition in ordinary matrix setup. Physical restoration has not been tested because this candidate does not run the fix.

## Reset timing and pinned DCD path

Arduino main calls TinyUSB_Device_Init before setup and before launching the second-core application. Thus reset receipt is possible (A) before setup, (B) between setup entry and the first sample, (during) that sample, (C) after shared recovery-route entry (manual RT2 or automatic recovery), and (D) after recovery publication. The b075 boot-wide sticky reset flag did not distinguish these. The candidate adds read-only source boundary markers; it does not delay or reschedule startup.

`dcd_rp2040_irq` snapshots masked INTS. It handles SETUP before BUS_RESET if both were in that snapshot. SETUP reads the DPRAM setup packet, resets both EP0 software PIDs to DATA1, emits `dcd_event_setup_received`, then clears SIE SETUP_REC. BUS_RESET sets address0, resets non-control endpoints, emits bus-reset, clears its SIE status, then conditionally calls E5. This branch remains disabled.

`dcd_init` resets USB hardware/DPRAM, selects PHY/SOFTCON, forces VBUS detect, initializes EP0 IN/OUT at64 bytes, resets non-control endpoints, enables MAIN_CTRL, sets SIE_CTRL EP0_INT_1BUF, enables SETUP_REQ/BUS_RESET/buffer/suspend/resume interrupts, then enables pull-up. EP0 SETUP delivery uses the dedicated setup packet/latch, not a pre-posted ordinary bulk receive. EP0 buffers and software state matter for subsequent control data/status progress; an unarmed bulk-style OUT buffer is not itself proof of missing SETUP.

For the path to proceed the line/PHY must leave reset, setup must be latched in DPRAM/SIE, INTR/INTE must permit masked INTS, USBCTRL NVIC/global interrupt state must permit the handler, DCD must emit an event, the bounded queue must retain it, and the software USB task must consume it and submit control progress. The task IRQ is dynamically claimed by the pinned port and triggered by the lower-order USB shared handler; task entry uses `__usb_mutex`. Its wrappers preserve all original arguments and calls.

The optional `tud_event_hook_cb` executes after `osal_queue_send` even if enqueue failed, before the DCD clears SIE. It proves DCD emission, not queue success. The seventh wrapper around external `usbd_control_reset` counts actual dequeued RESET/UNPLUGGED control resets. Matching DCD/task reset counts and epoch-stamped successful control submissions prevent an old queued setup or an IRQ-interrupted wrapper from falsely advancing the new reset epoch. Unexpected UNPLUGGED prevents task attribution; forced-VBUS RP2040 normally cannot emit it. Lost reset queue entries conservatively withhold task progress instead of inventing queue acceptance.

No exact reset-to-SETUP defect has been proven. The new observer narrows the next physical boundary; it does not repair or establish the root cause.
