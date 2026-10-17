# Independent RX liveness review

Reviewer: fresh `/root/rx_fresh_review`; this reviewer did not implement the RX
repair or review the preceding READ candidate. Scope is the explicit owner
request to repair the first large inbound request failure on
`895109eb662a8ad6b6c99889cb37a254dce49998`. No controller operation, firmware
rebuild, Git mutation, canonical integration or hardware acceptance is performed
by this reviewer. The owner request authorizes the bounded source candidate;
historical campaign authority is not reused as standing authorization.

## Eight required answers

1. **Did physical evidence establish failure before protobuf decode? Yes.**
   The retained response is a normal command 5 CMD_ERROR carrying exactly
   `Profile store frame timeout`. In frozen 895, that unique ProfileStore branch
   follows `ReadPacket` setting `_packet_timed_out` and returns before `pb_decode`.
   The receipt and transmitted journal agree on 3,074 protobuf bytes / 3,089 COBS
   wire bytes. The host received only the 30-byte error frame, 5.000585375 seconds
   after its OS-write-completed event. No stage trace was requested: absent stage
   1 is not independent evidence of failed decode. Consumed device bytes and the
   physical interrupt schedule remain unknown.
2. **Can frozen RX reproduce that timeout for the actual request? Yes.**
   The exact frozen adapter and `ReadPacket` body, actual pinned CDC/FIFO code,
   actual PacketIO COBS and nanopb are exercised by the new regression. Under its
   source-consistent deferred-completion schedule, the actual request times out
   at 5,000 ms after 256 raw wire bytes were consumed. The next 64-byte endpoint
   completion is pending; 2,769 wire bytes remain at the modeled host. The first
   failing all-nonzero synthetic body is 253 bytes / 257 framed bytes. Those are
   model observations, not reconstructed physical counters. The same old source
   accepts the same bytes when completion processing is serviced normally.
3. **What exact event was missing?** Processing the queued USB OUT completion
   through `tud_task`, which clears endpoint busy state, runs `cdcd_xfer_cb`,
   copies the completed endpoint bytes into the CDC RX FIFO, and prepares the
   next OUT transaction. The selected Arduino-Pico 3.6.3 source uses
   `tu_fifo_read_n` and `_prep_out_transaction`, not the newer
   `tu_edpt_stream_read` API named in the hypothesis. A task IRQ that finds the
   outer mutex held skips its task pass. `delay(1)` calls `sleep_ms`, not the USB
   task. The old framed reader therefore has no guaranteed foreground recovery
   for that schedule.
4. **Does repaired RX progress avoid lock inversion? Yes in the reviewed
   topology.** An empty 64-byte cache calls `TinyUSB_Device_Task` before acquiring
   the outer guard, performs only the bounded `tud_cdc_n_read` under the guard,
   releases it, then calls the task again. There is no delay, wait or task call
   inside that foreground guard. TinyUSB's helper acquires its own outer
   try-lock. Internal FIFO/endpoint locks remain underneath the same outer
   coordination used by the IRQ; no inverse acquisition is introduced.
5. **Is accepted large TX unchanged? Yes.** `ProfilePacketWriter`,
   `WriteProfilePacket`, `serviceTx`, `txSubmitted`, and the guarded TX primitives
   retain the READ-repaired implementation. The separate actual CDC TX
   regression still proves full COBS reconstruction, including 1,024 full READ
   replies, mixed responses, 20 DTR cycles, slow/stopped readers and partial-frame
   recovery. The preserved 84/84 physical READ PASS belongs to 895, not this new
   candidate. No new physical TX acceptance is inferred.
6. **Can a pending fault influence reception? No in this source path.** ARM
   leaves the rule pending and uninstalls its CheckedStorage hook. The frame
   reader calls no storage primitive. `BeginMutation` runs only after complete
   protobuf decode, protocol eligibility and common durable replay/admission
   checks. The operation-specific checks retain their preceding behavior.
   `FaultScope` clears an activated hook on early return and before response
   encoding. Independent host testing proves 10,000 matching hook calls remain
   inert while pending. The intended row-A storage fault remains UNTESTED.
7. **Is the bounded whole-frame deadline retained? Yes.** The same single start
   timestamp and unsigned elapsed comparison enforce 5,000 ms without resetting
   on progress. Repaired slow-fragment tests include successful 3,089-byte
   reception and a continuously progressing stream that still times out at the
   total bound. The deadline is checked between synchronous task/parser calls;
   this is not a claim of a hard real-time bound across arbitrary IRQ/ROM work.
8. **Are B1–B8 unchanged? Yes at source scope.** Storage records/directories,
   checked persistence, admission/GC, mode selection, durable token identity,
   recovery, migration and metadata/health implementations are unchanged. The
   common byte stream's RX implementation changes and therefore requires the
   focused protocol, recovery and persistence regressions. Additive candidate
   diagnostic fields do not alter stored profile schemas or storage semantics.
   Existing hardware evidence is retained within its original exact-candidate
   scope; this answer does not grant a new full-campaign PASS.

## Packet ownership and diagnostics

PacketIO 0.3.0 `available()` may consume a COBS code byte through `_update_count`;
`read()` emits a decoded zero or consumes an underlying byte; `next()` resets
after EOP and otherwise enters delimiter-skipping mode. The new cache preserves
unconsumed bytes, including following-frame bytes, across `next()`. The
ProfileStore handler remains the sole owner that consumes and advances its
packet; `SendReport` does not perform a second advance. Actual tests cover
254-byte COBS blocks, zero-rich payloads, separate delimiters, truncated input and
resynchronization into a subsequent exact request.

Receive diagnostics use two fixed eight-word snapshots and the existing static
frame for bounded timeout formatting; no profile copy, flash record or dynamic
trace allocation is added. Mutation stages 30–38 are emitted retrospectively
after complete EOP and successful decode. They do not compete with an arriving
body. Timeout CMD_ERROR includes bounded counts, total elapsed time and last
progress. PULSE exposes the last non-PULSE snapshot without replacing it with the
successful PULSE itself. Task-pass counts mean helper calls, not proof that an
IRQ ran or a callback was processed. Raw/fetched counts start after command
ingestion; fetched counts can include bytes prefetched beyond the current frame.
They are not a complete physical wire byte count. The dispatch trace marks entry
to the backend operation branch, not successful completion of a storage call.

Two review clarifications were raised before freeze: describe dispatch-stage
semantics precisely, and include backend object growth on the heap as well as
linker static RAM in resource reporting. Neither is a reason to reinterpret the
physical failure as an injected storage outcome.

## Evidence and limits

Independent executions of `check_glyph_profile_store_cdc_rx_progress.py` and
`check_glyph_profile_store_rx_host.py` passed, with ASan/UBSan in the receiver
harness. The reviewer inspected the actual pinned framework task/IRQ, CDC/FIFO,
OSAL and PacketIO source. These tests establish a reproducible source defect and
its repair under an explicit schedule. They do not identify the failed
controller's exact program counter or interrupt timing.

The final receiver report's source hashes match the reviewed source. The
production backend's sanitizer tests pass for partial ticketed-frame timeout,
inert pending state, post-delimiter PULSE snapshot retention, retrospective trace
ordering, common admission before ticket activation, QUERY reconciliation, and
failed trace cleanup before dispatch. The CLI tests preserve exact replay bytes,
exercise all seven mutation trace opt-ins, and retain six fragmented CMD_ERROR
cases without relabeling them as success or host timeout. All 21 focused existing
checks pass, including the real LittleFS liveness/fault suite. Complementary RX
and TX tests remain distinct, with neither presented as physical evidence.

Target development measurements were independently reviewed against the ABI
probe sources and output: static RAM grows by 32 bytes; the persistent backend
heap-object payload grows from 376 to 520 bytes, including the stream's growth
from 20 to 100 bytes and two 32-byte snapshots. There is no per-request cache
allocation. The enumerated receive/task C inventories are 808, 1,016 and 1,264
bytes; their stated SDK/ROM/libc/IRQ and timeout-formatting exclusions are real
limits. Historical physical stack/heap watermarks are not transferred to this
candidate. The resource audit correctly requires final exact-ELF regeneration.

**Source verdict: PASS.** No material correctness, lock-order, storage-scope,
authority or regression finding remains. Dispatch semantics were clarified and
the backend heap growth is explicitly accounted for. The prepared one-reset
adjudication and next-candidate hardware packet retain all stop conditions and
do not invent a mutation dry-run command. This approves the reviewed source
candidate for exact committed build/custody preparation, not controller
acceptance or merge. Final commit/tree/build/UF2 identity is bound by a separate
independent artifact receipt after custody; that receipt must not claim a new
hardware PASS. No hardware action is authorized by this review.
