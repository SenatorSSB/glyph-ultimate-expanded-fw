# Profile-bearing READ: pinned USB progress audit

This source audit concerns failed candidate
`d59684b9368be61183881bdfc82adc774ad5f0ba`. It proves a deterministic
large-response progress defect and a regression control for the repair. It does
not identify an interrupt interleaving on the physical controller. The retained
hardware trace cannot retroactively supply missing device-stage or raw RX data.
The previous `594066d9` failure and `USB_RACE_PHYSICAL_CAUSALITY_UNPROVEN`
classification remain historical and unchanged.

## Exact dependency and progress contract

The installed framework package is `framework-arduinopico` version `1.30603.0`
(Arduino-Pico 3.6.3). Its bundled TinyUSB reports 0.16.0. The checker records
SHA-256 of the actual compiled CDC/FIFO sources, OSAL source, framework task
implementation, PacketIO COBS implementation, and current firmware source.
Paths below are relative to that framework's
`libraries/Adafruit_TinyUSB_Arduino/src`, except where stated otherwise.

* The selected project header `HAL/pico/include/tusb_config_pico.h`, chosen
  by `platformio.ini` through `CFG_TUSB_CONFIG_FILE`, sets TX FIFO capacity
  to 256 and selects `OPT_OS_PICO`.
  `class/cdc/cdc_device.h` defaults the full-speed endpoint buffer to 64 bytes.
* `class/cdc/cdc_device.c:178–227`: `tud_cdc_n_write_available` reports FIFO
  space. `tud_cdc_n_write` enqueues bytes and automatically flushes only when
  the FIFO reaches 64 bytes. `tud_cdc_n_write_flush` claims the endpoint,
  removes at most 64 bytes from the FIFO and submits a transfer. It does not
  wait for the host. A busy endpoint prevents another submission.
* `device/usbd.c:499–580`: deferred task processing consumes completion events,
  releases endpoint busy/claimed flags, and calls the CDC callback.
  `class/cdc/cdc_device.c:429–489` then flushes the next queued bytes, including
  a short tail; it also handles a USB zero-length packet when needed.
* `arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp:81–91`: the deferred USB IRQ
  tries the shared outer mutex and returns if it is held. Its comment expressly
  relies on the foreground caller running `tud_task` afterward. The hardware
  USB IRQ sets the deferred software IRQ; releasing the mutex does not itself
  process or re-pend that work.
* Framework `cores/rp2040/delay.cpp:34–53`: `delay(1)` only calls `sleep_ms`.
  `yield()` calls `TinyUSB_Device_Task` and `TinyUSB_Device_FlushCDC`.
  Framework `cores/rp2040/main.cpp:66` yields after a foreground loop returns.
* `arduino/Adafruit_USBD_CDC.cpp:217–233`: the normal Arduino CDC writer calls
  `yield()` when bytes remain. The d596 coordinated writer bypassed this and
  used only `delay(1)` when FIFO space was exhausted.
* `tusb.c:331–365` contains generic `tu_edpt_stream_write[_xfer]` helpers with
  similar submit/threshold semantics, but the pinned CDC implementation does
  **not** call them. This audit and harness use the actual CDC implementation.

The split `availableForWrite` / `writeAvailable` lock acquisition is safe for
this single foreground producer: completion processing can increase FIFO space;
`writeAvailable` rechecks the actual space and connection while holding its
own guard. The split is not a progress mechanism. A dropped deferred IRQ can
leave the endpoint busy until somebody services the event queue.

## Deterministic source failure

One legal schedule is: a full-speed IN transfer completes while foreground
code holds the outer mutex; the deferred USB IRQ runs, fails the try-lock, and
returns. No new event is required after that. The already-delivered 64-byte
endpoint transfer remains marked busy in software until task processing handles
its completion. Foreground output can enqueue another 256 bytes, then it waits
for FIFO room using `delay(1)` until the packet's two-second deadline expires.
The ordinary loop yield occurs too late to complete that abandoned COBS frame.
It drains the queued prefix, leaving the host without the final zero delimiter.

For an all-nonzero synthetic response body, a sweep of every length 1–600 has
its first failed body at **317 bytes**: command plus COBS overhead and delimiter
require 321 bytes, exceeding the 64-byte submitted transfer plus 256-byte FIFO.
This exact threshold is encoding-pattern and scheduling specific, not a claim
that every physical response over 316 bytes always fails.

Actual decoded hardware responses reconstructed as protobuf messages reproduce
the observed small/large split under the same schedule:

| Response | Protobuf bytes | d596 reconstructed result | Repaired host COBS frame bytes |
| --- | ---: | --- | ---: |
| STATUS | 104 | complete | 107 |
| LIST page 0 | 276 | complete | 280 |
| ID1 READ | 1989 | incomplete 320-byte prefix | 1999 |
| ID3 READ | 3071 | incomplete 320-byte prefix | 3086 |
| ID4 READ | 3076 | incomplete 320-byte prefix | 3091 |
| ID22 revision130 READ | 3072 | incomplete 320-byte prefix | 3087 |
| Maximum accepted Stage-C fixture READ | 4038 | incomplete 320-byte prefix | 4056 |

The `.pb` fixture bytes are reconstructions from retained decoded JSON or the
validated maximum fixture. They are **not** claimed to be retained raw USB
bytes from the failed READ. The harness decodes and reencodes each with the
actual generated Nanopb descriptor and requires byte-for-byte equality before
transmission. Fixture provenance and hashes are in
`tools/fixtures/profile_store_cdc_progress/payload_manifest.json`.

## Repair and tail semantics

`CoordinatedCdcStream::serviceTx` runs `TinyUSB_Device_Task()` with no foreground
Guard alive, then makes a nonblocking flush attempt under the shared outer
mutex. `ProfilePacketWriter` calls it after enqueueing bytes and while waiting
for FIFO space. `finish()` shares the same original two-second deadline and
services until the connected TX FIFO is empty. `WriteProfilePacket` calls it
after `COBSPrint::end`, so the final short tail and zero delimiter are submitted.
Failed output retains the existing prefix-delimiting resynchronization rule.

Do not replace this with unguarded `yield()` inside the writer: pinned
`arduino/Adafruit_TinyUSB_API.cpp:51–56` calls `tud_cdc_n_write_flush` directly
from `TinyUSB_Device_FlushCDC`, without the outer mutex. The new path preserves
the previous lock-order repair.

An empty FIFO means bytes have been submitted to an endpoint; it does **not**
mean the host acknowledged the final packet. The regression explicitly delays
that final endpoint: `finish()` can return with the FIFO empty and the delimiter
still absent from the host's received bytes. Only a later modeled host poll
makes the complete COBS frame observable. This distinction is intentional.
Host tooling must still require the complete response frame.

The old short-packet path can also leave the delimiter queued until the ordinary
loop yield; the harness proves this. That tail alone does not explain a lasting
physical timeout if the main loop continues yielding. The large-frame dropped
completion mechanism is the separately reproduced defect.

## Executable regression and limits

Run `python3 tools/check_glyph_profile_store_cdc_progress.py --output-dir DIR`.
It extracts the actual old/current `ProfilePacketWriter` and `WriteProfilePacket`
source, compiles the actual `CoordinatedCdcStream`, PacketIO COBS, pinned
`cdc_device.c`, `tusb_fifo.c`, generated protobuf descriptors and Nanopb under
ASAN/UBSAN. The pinned `osal_pico.h` implementation is used with modeled SDK
mutex primitives that assert FIFO locking occurs under the outer USB mutex.
A temporary initialization tail establishes an already-enumerated CDC interface
with DTR and non-overwriting FIFO; production driver code is otherwise unchanged.

The endpoint/task adapter models endpoint busy state, host polls, delayed
completion events and the IRQ try-lock failure. Endpoint submission copies into
a pending endpoint buffer; only a modeled host poll that drains the transfer
appends bytes to the received wire. Task processing releases busy state before
calling the actual CDC completion callback. The adapter is not RP2040 USB silicon,
full `usbd.c`, OS scheduling or a controller hardware test.

Coverage includes all requested endpoint/FIFO boundaries; exact COBS decoding
and delimiter checks; every nonzero payload length 1–600; 8191-byte synthetic
bodies including all-zero and alternating-zero patterns; all seven actual
protobuf fixtures; 1,024 repeated rotating full-profile READ frames; 147 mixed
rounds (1,029 additional frames); 20 process-style DTR close/open cycles through the actual pinned
`cdcd_control_xfer_cb` (FIFO/endpoint state retained); nine discarded
responses; eight stalled-host partial-frame recoveries; slow readers; disconnected
host failure at the same two-second deadline; and a delayed final delimiter.
No TX allocation occurs, and retained host allocation count stays unchanged
through the long sequence. This is not a physical heap-watermark measurement.

The bound is a foreground whole-packet deadline around the pinned nonblocking
CDC/task APIs, not preemption of arbitrary firmware or USB interrupt handlers.
Normal finite queued events are serviced; a host that stops draining causes
bounded failure and later framing recovery. Hardware acceptance remains required.
