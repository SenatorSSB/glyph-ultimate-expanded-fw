# Independent READ-liveness repair review

Reviewed 2026-10-16, against failed parent
`d59684b9368be61183881bdfc82adc774ad5f0ba`, in the isolated
`codex/profile-store-read-liveness` worktree. The owner explicitly requested a
fresh reviewer. This reviewer did not implement the production changes, perform
Git mutations, or operate any device. The reviewed change is a source repair
candidate; hardware acceptance and canonical merge are not granted.

## Seven required answers

1. **Physical boundary:** `READ_REQUEST_TRANSMITTED_FINAL_RESPONSE_NONE`.
   The retained `d596-postcycle-read-1.trace.json` contains transmit attempt,
   completed host write, then timeout approximately ten seconds later.
   Protobuf request hex `080218032801` independently hashes to
   `7e71733f90dacaf476e8bc4271809e7aa70413f44b53d95b36ba8cf7b2d389d2`.
   No READ device-stage tracing was enabled. The old journal did not record
   RX byte counts or partial frames; zero bytes, partial bytes, delimiter
   absence and the exact device program counter are **unknown**. No new device
   observation is inferred from a completed OS write. The physical failure
   remains permanent; the source reproduction does not retrospectively prove
   its interrupt schedule.

2. **Reproduced failure:** transmission progress. Actual frozen record
   storage, checked I/O, CRC, Nanopb decode, validation and encoding pass the
   independently rerun real LittleFS test. The actual frozen writer fails with
   the actual CDC/FIFO and COBS implementations under a legal deferred-completion
   schedule. A transfer completion IRQ that encounters the held outer mutex
   leaves work pending; `delay(1)` only sleeps in this framework. The old
   foreground writer fills the remaining FIFO, then exhausts its two-second
   deadline without servicing that work. An all-nonzero body sweep first fails
   at 317 bytes (321 required wire bytes versus 64 endpoint + 256 FIFO bytes).
   This is schedule/payload dependent, not a universal physical size limit.

3. **Lock inversion remains repaired:** yes. Every adapter foreground direct CDC
   query/write/flush remains under the shared outer USB mutex. `serviceTx`
   calls `TinyUSB_Device_Task` with no foreground Guard alive; the pinned helper
   takes its own outer try-lock. The following flush obtains a separate Guard.
   No task servicing or sleep occurs while the foreground owns the mutex.
   Generic `yield()` is deliberately avoided because its framework FlushCDC
   helper does not take that outer mutex. The split space-query/write remains
   safe because the actual write rechecks available space and connection.

4. **Bounded multipacket progress:** yes, within the pinned nonblocking API
   and finite event-processing contract. Enqueue, wait-for-space and final FIFO
   submission all service pending completion work and share the original
   two-second packet deadline. The independent model passes both adversarial
   and ordinary completion schedules and slow draining. A stalled/disconnected
   host reaches bounded failure; the partial frame is delimited before a later
   packet. This is not a hard real-time proof against arbitrary unrelated ISR
   starvation or a malicious infinite USB control-event stream.

5. **Final tail/delimiter:** the repair explicitly submits the final FIFO tail
   after `COBSPrint::end`; a connected draining host receives and reconstructs
   it in the regression. `finish()` does **not** observe a host ACK. A dedicated
   test returns from the writer with FIFO empty while the last endpoint packet
   and delimiter are still pending; only a later host completion produces the
   accepted complete frame. Stage 23 means FIFO submitted, never host receipt.
   Host success requires both the reconstructed full READ and terminal stage 24.

6. **B1–B8:** the diff preserves their source mechanisms. No capacity/admission,
   GC, v2 record/directory encoding, identity/replay, root recovery, migration,
   stable-ID, reboot selection, recovery restriction or health policy is
   rewritten. Storage changes add an inactive-by-default scoped observer;
   checked open/read/close results retain their checks and a failed observer
   cannot skip closing an open file. The total receive deadline and inert
   ticketed fault controls remain. Source preservation does not grant new
   hardware PASS to any historical row.

7. **Next instrumentation:** sufficient to separate the requested phases.
   The opt-in READ observer covers probe/size, checked open/read/close,
   integrity, profile decode, validation and response population, followed by
   exact protobuf length and TX observations. Post-TX trailers are separate
   COBS frames and report accepted bytes, flush request, FIFO submission and
   terminal success/failure. They cannot corrupt the interior of the response.
   The host records raw chunks, cumulative byte count/SHA, full-frame hashes,
   partial frame bytes, delimiter state, stages and timeout. A timeout after a
   complete response but before its trailer is distinct. If USB itself stops,
   the last received stage narrows the synchronous boundary; it does not reveal
   an exact PC without a debugger. Journals retain exclusive creation.

## Independently executed evidence

- `check_glyph_configurator_usb_coordination.py`: PASS, 10,000 schedules,
  original inversion negative control, bounded full-FIFO failure.
- `check_glyph_profile_store_candidate_tool.py`: PASS, including real retained
  1989-byte READ parsing, partial timeout, missing trailer, malformed partial
  frame/failure trailer and refusal to overwrite/alias evidence.
- `check_glyph_profile_store_read_storage.py`: PASS on frozen and repaired
  sources, 6,000 READs each across IDs 1/3/4/22/5/20 at the generation 160 history.
  All phases complete; no READ flash programs/erases; no leaked file handles;
  LittleFS steady 768/peak 1024 allocated bytes. Every observer-stage failure
  preserves close/allocation cleanup. ASAN/UBSAN enabled.
- `check_glyph_profile_store_cdc_progress.py`: PASS with actual source-extracted
  writers, packet function, pinned CDC/FIFO, PacketIO COBS and Nanopb. Frozen
  actual profile responses fail with 320-byte incomplete prefixes; repaired
  actual responses 1989/3071/3076/3072/4038 bytes reconstruct exactly. Requested
  endpoint/FIFO thresholds, COBS blocks/zeros and 8191-byte bodies pass. Stress
  covers 1,024 full READs, 147 mixed rounds, 20 actual pinned DTR close/reopen
  cycles, dropped responses, stalled-host recovery and slow drains. No TX
  allocations or retained host allocation growth; this is not physical heap
  sampling. Reports are retained under `/private/tmp/glyph-read-review/`.

## Review findings resolved

The initial CDC endpoint model counted submitted bytes as received. It now
keeps endpoint payload pending until an explicit modeled host completion and
separately tests final delimiter receipt. The initial reconnect reset model was
replaced with actual pinned control-line callbacks preserving FIFO/endpoint
state. Actual ID 3/4/22 payloads were added. The host parser test now uses the
full retained ID 1 response, and stage 19 reports the actual has-profile result.
These were evidence/diagnostic gaps, not additional production storage defects.

## Resource and integration boundary

The measured ARM ABI keeps ProfileStoreResponse 2992, UltimateProfile 2152 and
static frame 8192 bytes. Generated finite schema bounds remain below 8192;
no callback/repeated-field allocation is introduced. Traced storage calls add
live stack while checked ReadFile remains active: resource review must include
its observer callback, the 88-byte split TraceProfileStage body, 344-byte packet
function and TinyUSB task/dispatch path, not merely the 8-byte trace wrapper.
The independently checked enumerated C-frame report gives 1912 bytes for traced
checked READ with CDC completion, 2160 for its conservative control/descriptor
inventory, and 2824 for the four-level response encode inventory. Each is below
the 4096-byte scratch-bank envelope, with at least 1272 bytes before excluded
paths. The split trace body is correctly included. These are enumerated paths
and conservative inventories, not a complete callgraph bound: ROM/SDK helpers,
IRQ nesting, arbitrary indirect callbacks and pre-setup startup remain excluded.
Development ABI RAM increases 12 bytes; flash increases 1768 bytes. Root
reported 21 focused regression checks all PASS; the reviewer inspected that
report, including strict protocol, persistence, migration, recovery, identity,
health/metadata and real LittleFS liveness coverage. Exact committed build
identity and artifact custody remain final integration prerequisites. No
whole-target stack bound or physical margin is asserted by host sanitizers,
individual frames or the inventory sum.

Source/transport/resource review is PASS with the above exact-artifact integration
prerequisites.
`594066d9` and `d59684b9` remain permanently HARDWARE_FAIL; the earlier reset
adjudication PASS and `ARM_TRANSMISSION_UNPROVEN` /
`USB_RACE_PHYSICAL_CAUSALITY_UNPROVEN` remain unchanged. The next action is a
separately authorized hardware packet, beginning with read-only failed-state
adjudication and then exact new-candidate pulse/STATUS/immediate traced ID 1 READ.
No device action or canonical merge occurred in this review.
