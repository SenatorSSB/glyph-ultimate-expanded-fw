# Large ProfileStore request: pinned USB RX progress audit

This audit concerns the permanent full-campaign hardware failure of candidate
`895109eb662a8ad6b6c99889cb37a254dce49998`. Its separately observed
`MULTI_PROFILE_STORE_895_READ_GATE_HARDWARE_PASS` remains intact. The new regression
proves a source-level receive progress defect; it does not recover the physical
controller's missing interrupt history or program counter.

## Pinned implementation and correction to the initial hypothesis

The selected Arduino-Pico package is `1.30603.0` (Arduino-Pico 3.6.3), with the
bundled TinyUSB CDC source and repository-selected `OPT_OS_PICO`. The project's
`HAL/pico/include/tusb_config_pico.h` sets the RX FIFO to 256 bytes; the full-speed
CDC OUT endpoint buffer is 64 bytes.

The request's reference to `tu_edpt_stream_read` does **not** describe this pinned
CDC implementation. In the actual `class/cdc/cdc_device.c`:

- `tud_cdc_n_available` counts bytes already in `rx_ff`.
- `tud_cdc_n_read` calls `tu_fifo_read_n`, then `_prep_out_transaction`.
- `_prep_out_transaction` requires at least 64 free FIFO bytes before claiming
  and arming a 64-byte OUT transaction. It rechecks capacity after claiming.
- USB OUT completion is processed by `cdcd_xfer_cb`. Only that callback copies
  the completed endpoint buffer into `rx_ff`; afterward it attempts to arm the
  next OUT transaction.

`device/usbd.c::tud_task_ext` dequeues completion events, clears the endpoint's
busy/claimed state, and invokes the class callback. `osal/osal_pico.h` receives
queued events without waiting regardless of the requested timeout. The task
processes until its queue is empty. These facts support the ordinary finite-event
progress contract; the foreground deadline does not preempt an arbitrary IRQ
handler or an infinite unrelated event producer.

The framework's `arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp::usb_task_irq`
tries `__usb_mutex` and returns if foreground code owns it. Its comment relies
on the caller processing the task afterward. Releasing the mutex does not process
or re-pend the skipped software IRQ. `cores/rp2040/delay.cpp::delay` calls
`sleep_ms`; it does not call `TinyUSB_Device_Task`. The normal main-loop yield is
reached only after the blocked `ReadPacket` returns.

## Source-faithful negative control

Run:

```bash
python3 tools/check_glyph_profile_store_cdc_rx_progress.py --output-dir /tmp/rx-proof
```

The checker extracts the exact frozen 895 `ReadPacket` and
`CoordinatedCdcStream`, and then the current versions, without editing either
extracted method. It compiles the actual pinned `cdc_device.c`, `tusb_fifo.c`,
`osal_pico.h`, PacketIO 0.3.0 `COBSStream`/`COBSPrint`, generated Nanopb descriptors,
and Nanopb decode/encode sources under ASAN/UBSAN. A temporary appended observer
initializes an enumerated, DTR-on CDC interface and reports FIFO occupancy. The
production CDC driver is otherwise unchanged.

The endpoint/task adapter models a legal schedule:

1. Normal completion processing initially fills the RX FIFO, up to 256 bytes.
2. Foreground consumes enough bytes to make 64 bytes free. The real CDC reader
   arms another OUT transaction while holding the outer USB mutex.
3. The host completes that transaction during the guarded section. The task IRQ
   fails the same try-lock used by the framework and returns. The event remains
   pending; its bytes are still in the endpoint buffer, not the software FIFO.
4. Frozen 895 drains the original FIFO. It never services the pending completion
   while inside `ReadPacket`, and waits with `delay(1)` until 5,000 milliseconds.
5. The missing event processing would clear endpoint busy state, copy endpoint
   data into the FIFO, and arm subsequent OUT transfers. There is no arbitrary
   packet drop in this negative control.

For the all-nonzero synthetic body sweep from 1 through 600, the first failure is
**253 body bytes / 257 complete COBS wire bytes**, including command and delimiter.
This is a schedule- and encoding-dependent threshold, not a universal USB limit.
Separately arriving short packets or a delimiter can require an additional OUT
transaction earlier because `_prep_out_transaction` requires a full 64 bytes of
free capacity even for a host's short packet.

The exact physical UPDATE is 3,074 protobuf bytes / 3,089 COBS wire bytes. Frozen
895 reproducibly times out after consuming 256 raw wire bytes: FIFO occupancy is
zero, a completed 64-byte OUT transaction remains pending, the host has delivered
320 bytes to the modeled endpoint, and 2,769 wire bytes remain upstream. The
firmware has not consumed an EOP. The same exact bytes complete and decode under
a normal IRQ schedule, which controls for invalid request bytes and COBS encoding.

The adapter is not RP2040 silicon, OS serial scheduling, or the full `usbd.c` event
engine. It models the relevant busy-state/event/callback order directly and uses
the real CDC/FIFO/OSAL implementation. It cannot establish which interrupt
interleaving occurred in the physical test. Exact dependency and firmware hashes,
fixture sizes, and detailed negative/current outputs are retained in `report.json`.

## PacketIO ownership and repair

PacketIO's `COBSStream::available()` is not a passive FIFO count: it can read COBS
code bytes through `_update_count`. `read()` also consumes code bytes and may
return a synthetic decoded zero. EOP is returned when the raw zero delimiter is
consumed. `next()` resets after EOP; before EOP it sets `_skip_to_end`, so later
reads discard the remainder through its delimiter before decoding another frame.

The repaired `CoordinatedCdcStream` retains that byte/peek interface and owns one
64-byte cache. An empty cache is refilled by servicing the device task outside
any foreground guard, reading up to 64 bytes under the guard, releasing it, and
servicing the task again. The second task pass handles a completion that was
triggered by the read's OUT rearm. Cached bytes are never discarded by COBS
`next()` or DTR transitions. PacketIO alone consumes delimiters and owns framing.

The regression checks adjacent frames sharing the cache, a partial frame timeout
followed by its late remainder/delimiter and a valid next frame, 254-byte COBS
block boundaries, zero-rich data, and a separately arriving delimiter. Success
requires byte-for-byte complete body reconstruction and actual Nanopb decode for
protobuf cases; host writes or CDC FIFO enqueues alone are not success.

`ReadPacket` retains its original total 5,000-millisecond deadline. Slow receipt
of the physical UPDATE at one byte per millisecond completes. An 8,191-byte body
making continuous one-byte-per-millisecond progress still times out at the same
whole-frame deadline; progress never resets that deadline.

## Request matrix and sustained coverage

| Request | Protobuf bytes | Complete COBS wire bytes |
| --- | ---: | ---: |
| Exact physical ticketed ID22 UPDATE | 3,074 | 3,089 |
| Exact physical ARM | 20 | 23 |
| Exact physical STATUS | 7 | 10 |
| Metadata-only RENAME control | 41 | 44 |
| Stage-A fixture UPDATE | 1,992 | 2,002 |
| Stage-B fixture UPDATE | 2,709 | 2,722 |
| Stage-C fixture UPDATE | 3,074 | 3,089 |
| Maximum accepted Stage-C fixture wrapped as UPDATE | 4,057 | 4,075 |
| Near-ceiling protobuf with a skippable unknown field | 8,191 | 8,194 |

There are 113 protobuf cases, including all path/operation/phase combinations of
candidate fault-control requests, every ticket-bearing mutation operation shape,
physical profile variants, pulse, READ, QUERY, and STATUS. Every repaired case
receives its complete frame and decodes. The harness tests admission to protobuf
decode, not successful storage mutation or semantic acceptance of every control
combination. The near-ceiling request is valid protobuf using an unknown
length-delimited field; it is not a claim that a semantically valid full profile
requires that size. Exact protobuf body sizes 63/64/65/127/128/255/256/257/512 are
covered using such a field. A one-byte synthetic body is a framing test only;
there is no valid nonempty one-byte protobuf field encoding.

The synthetic sweep and explicit matrix also cover 1/63/64/65/127/128/253/254/
255/256/257/512/8191-byte bodies. COBS encoders and decoders are the production
PacketIO implementations. Zero-filled, alternating-zero, and 254-byte-spaced
patterns exercise framing overhead separately from the protobuf cases.

The sustained repaired sequence retains the same backend, cache, CDC FIFO, and
endpoint state for 1,024 large profile-bearing CREATE/UPDATE receptions, rotating
actual profile sizes. It interleaves small ARM/STATUS/pulse/READ/QUERY/RENAME
requests, 84 additional READ request receptions, and 20 real CDC DTR close/open
transitions. Twenty additional DTR controls exercise the exact physical UPDATE.
Slow/fragmented host transfers use 1/3/63/64-byte packets. No frame-reader heap
allocation or retained host allocation growth occurs. These are modeled host
allocation observations, not physical heap-watermark measurements.

This RX harness does not produce READ responses or execute actual ARM state,
fault injection, or persistent storage. Those remain covered by the existing
production backend/ticket and real LittleFS suites. The complementary pinned
TX regression exercises at least 1,024 full READ responses and must still pass
against the repaired combined source.

## Lock ordering and remaining hardware gate

The modeled SDK mutex primitives assert that every real FIFO mutex acquisition
occurs under the outer USB mutex. The endpoint adapter also asserts the outer
mutex at claims/submissions. Both task service and delay assert that no foreground
outer guard is alive. The RX cache therefore reduces lock acquisition frequency
while preserving the previous outer-lock coordination.

The TX methods, bounded packet writer, and `serviceTx` are unchanged by this RX
repair. Do not substitute generic `yield()` for these service points: the pinned
`TinyUSB_Device_FlushCDC` called by `yield()` flushes without the outer mutex.

The physical journal's normal Configurator frame-timeout error locates the
observed failure before full request protobuf decode. Pending fault ticket state
is not consulted by the frame reader or CDC methods. The source repair and
negative control therefore explain a matching pre-decode receive failure
mechanism, while the intended record/open-write injected outcome remains untested
and the failed controller's current state remains unknown. No controller action
is performed by this audit or checker. Exact new candidate hardware acceptance
is still required.
