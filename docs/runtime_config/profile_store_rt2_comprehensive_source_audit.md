# Comprehensive RT2 observer: bounded independent source-authority audit

Reviewed exact source candidate `3b5c92b2200753c795315a166dc7bd501a93a9f6`, tree `8637a3d0c1ae5be03c64628cca3fca56842803f9`, parent `88ab0029d464175865e1ce3e9a19b462579ffed4`, and its existing target objects/ELF. This is a specialist investigation, not the fresh post-implementation review or physical acceptance. No source, Git, vendor package or device mutation occurred; this local audit is the only write.

Pinned source prefix: `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/libraries/Adafruit_TinyUSB_Arduino/src/`. XInput prefix: `.pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/src/`. Existing 3b5c target artifacts under `.pio/build/glyph_mk6/` were inspected with the pinned ARM objdump/readelf/nm.

## Queue identity and exact acceptance

The active `OPT_OS_PICO` implementation uses TinyUSB FIFO plus Pico critical section; SDK `queue_try_add` / `queue_try_remove` are not the integration points. `HAL/pico/include/tusb_config_pico.h` selects OPT_OS_PICO; `osal/osal.h:60-61` selects `osal_pico.h`. `osal/osal_pico.h:103-109` defines `osal_queue_def_t` with `tu_fifo_t ff` as the first member. Its OSAL_QUEUE_DEF at112-117 declares externally visible queue storage. `device/usbd.c:68-70` defaults task capacity16; :291 creates `_usbd_qdef`, :292 stores the queue handle in a private pointer.

`osal/osal_pico.h:137-151` wraps exactly one `tu_fifo_read` in the queue's existing critical section; :153-168 wraps exactly one `tu_fifo_write`, unlocks, then TU_ASSERTs success. Both OSAL functions are always-inline, but their FIFO callees are out of line. Existing usbd.c.o proves GLOBAL/UND `tu_fifo_read` and `tu_fifo_write`, with R_ARM_THM_CALL relocations at tud_task_ext+0x4c and the DCD event path in `.time_critical.tinyusb` (+0xa0/+0x136); usbd_defer_func also calls write. `_usbd_qdef` is GLOBAL OBJECT size28 and its backing buffer size192 (16*12-byte dcd_event_t).

Safe narrow interposition: include the actual OSAL/FIFO type, declare `extern "C" osal_queue_def_t _usbd_qdef`, identify `f == &_usbd_qdef.ff`, and GNU-wrap `tu_fifo_read` / `tu_fifo_write`. All other FIFOs are transparent passthrough. Call each real function exactly once with identical pointers and preserve its bool result. Read the dcd_event_t only after successful read; inspect immutable supplied event on write without changing it. This obtains exact attempted/accepted/failed sends and exact consumed event kinds. It needs neither vendor edits nor queue draining changes.

`common/tusb_fifo.c:693-705` returns true after copying and advancing the FIFO read index. :794-819 returns false when full/non-overwriting, or copies and advances the write index before true. `tu_fifo_count` at584-587 only reads indices and clamps depth. Sampling it inside these wrappers (still under the existing OSAL critical section) gives exact instantaneous occupancy at that boundary and a maximum observed occupancy; it is not electrical traffic demand. The wrapper adds bounded execution to an existing IRQ-masked critical section, so keep it small and report this perturbation explicitly. Do not add another lock. Source queue FIFO mutex fields are zero from its static initializer; existing outer critical section provides serialization.

`device/usbd.c:302-305` invokes the existing event hook after osal_queue_send regardless of the returned bool. A DCD hook therefore remains emission evidence, not acceptance. At debug0 TU_ASSERT returns false; it neither retries nor repairs drops (`common/tusb_verify.h:120-129`). Queue-full RESET/SETUP failure is safely observable via FIFO return. Send counters should be split by writer context or use only the serialization already proved; core1 must only read atomic published banks. Do not let a shared generation-word protocol create nested-writer aliasing.

## Consume versus control entry

`device/usbd.c:509-510` performs the read and returns immediately on empty. `:533-554` handles successfully consumed SETUP, sets connected, clears EP0 state and invokes `process_control_request`. The latter is static and target-inlined; GNU wrapping its name is not viable. Its FIRST operation (:644) is an external `usbd_control_set_complete_callback(NULL)` call. That symbol is GLOBAL/UND with R_ARM_THM_CALL relocations in the existing target object. A wrapper filtered by current successfully consumed event type SETUP, current USB-task context and NULL argument can latch control-processing-began before the real call. Other NULL calls (:811/:880) happen later inside the same control routine; latch once per consumed SETUP. This preserves consumed-versus-control distinction. `device/usbd_control.c:154-157` implements the real setter as a fixed pointer assignment.

Descriptor `tud_control_xfer` success means submission accepted by device-side code, not host receipt. Address request versus status-complete application remain separate. Configured/mounted device state is not proof the host created a serial node.

## Reset stages and function-pointer wrapping

`device/usbd.c:453-464` iterates application driver first, then builtin CDC, MSC, HID, MIDI, and clears device state. `:467-470` then calls usbd_control_reset. `:519-529` invokes that path for BUS_RESET and UNPLUGGED. `:724` also invokes configuration_reset while processing SET_CONFIGURATION; do not label those class callbacks as bus reset processing.

The existing target `.rodata._usbd_driver` contains GLOBAL/UND symbol R_ARM_ABS32 relocations:
- CDC reset at+0x04 -> cdcd_reset;
- MSC reset at+0x1c -> mscd_reset;
- HID reset at+0x34 -> hidd_reset;
- MIDI reset at+0x4c -> midid_reset.

GNU --wrap rewrites these unresolved function-pointer relocations, so source-owned wrappers before/after real CDC/MSC/HID/MIDI functions are viable. Qualify markers by the consumed RESET/UNPLUGGED event and task processing state. Verify final ELF table words equal wrapper addresses with Thumb bit; presence of wrapper symbols alone is insufficient.

Source reset bodies: CDC `class/cdc/cdc_device.c:266-280` clears fixed interface prefix, clears RX/TX FIFOs, resets TX overwritability. MIDI `class/midi/midi_device.c:400-412` clears interface prefix and both FIFOs. FIFO clear at `common/tusb_fifo.c:869-879` takes configured FIFO mutexes; those inner locks are plausible source-level wait boundaries, not physically proven causes. MSC `class/msc/msc_device.c:264-268` and HID `class/hid/hid_device.c:179-183` are fixed clears.

XInput reset at `Adafruit_USBD_XInput.cpp:213-215` is empty. It has LOCAL symbol `_ZL12xinput_reseth`, and the same object's local driver-table relocation binds it locally; ordinary GNU --wrap cannot replace that local pointer. Do not claim XInput before/after instrumentation. Narrow residual: `XINPUT_RESET_BOUNDARY_RESIDUAL`, bracketed by successful reset dequeue and first CDC wrapper entry; exact pinned body is empty. Shadowing/replacing application driver tables would add unnecessary integration semantics for an empty body.

After-real usbd_control_reset remains the correct complete-reset-path boundary: its source body `device/usbd_control.c:148-151` clears control state after all class resets and device clears returned. Next queue-read attempt after that marker proves the event loop continued beyond reset processing, even if that read returns empty. A consumed RESET marker by itself proves dequeue, not a completed reset callback.

## Raw SETUP and unavoidable residual

RP2040 DCD `portable/raspberrypi/rp2040/dcd_rp2040.c:307-308` emits SETUP then clears its SIE latch. `:340-341` emits reset then clears reset latch. SETUP handling precedes reset in a combined IRQ. Raw SIE/INTR/INTS samples are positive software observations, not a packet counter. Sampling cannot turn absence of a positive indication into proof no latch ever existed. Preserve 'no raw SETUP observed' wording. BUS_RESET plus no observed raw SETUP cannot distinguish host never sent it from electrical/PHY/controller failure to latch it: `HOST_PHY_SETUP_RESIDUAL`. If only periodically sampled raw registers are available, retain the temporal sampling limitation; do not infer packets that were never observed.

## Required follow-through

Final implementation needs source-faithful full/partial/empty queue and critical-event-drop tests, queue identity negatives, before/after class-stall markers, setup-consumed versus control-entry tests, transparent non-USBD FIFO passthrough checks, exact final wrapper call/table binding proof and independent fresh review. No claim of root cause, normal target control, physical RT2 acceptance or hardware noninterference is made by this audit.
