# Large inbound ProfileStore request liveness repair

Disposition: `MULTI_PROFILE_STORE_RX_LIVENESS_REPAIR_READY` after exact committed
build, independent review and custody binding. Hardware remains NOT_TESTED for
this new candidate. The immutable HANDOFF supplies final SHA/tree/parent/base,
UF2 identity and build/resource measurements; this source document does not
self-bind to a future commit hash.

## Physical boundary and preserved outcomes

Retained row-A evidence proves
`LARGE_UPDATE_WIRE_TRANSMITTED_DEVICE_FRAME_READER_TIMED_OUT`: the exact ticketed
ID22 UPDATE was 3074 protobuf bytes /3089 COBS wire bytes. Its receipt matches the
host transmission. The OS write completed; 5.000585375 seconds later the only
received chunk was a normal 30-byte CMD_ERROR containing `Profile store frame
timeout`. No ProfileStore response or stage preceded it. Tracing was not enabled;
absence of stage1 is not independent proof. The unique frozen895 error branch
returns before protobuf decoding and fault activation. Physical consumed-byte
counts and interrupt timing remain unknown.

895 remains permanently `HARDWARE_FAIL —
LARGE_PROFILESTORE_REQUEST_RX_TIMEOUT_DURING_TICKETED_UPDATE`. Intended row-A
storage injection is UNTESTED; current volatile and persistent state UNKNOWN.
No useful-profile mutation was confirmed. Separately preserve
`MULTI_PROFILE_STORE_895_READ_GATE_HARDWARE_PASS`: immediate ID1, IDs3/4/22,
20 reconnects,84/84 full READs, no partial COBS, healthy resources/stable state.
Earlier594/d596 failures and all custodied artifacts remain unchanged.

## Source defect and repair

The [pinned USB audit](profile_store_rx_usb_audit.md) establishes a reproducible
missing-progress defect. A USB OUT completion arriving under the outer mutex
can leave its task event pending. Frozen895 drains its FIFO then sleeps inside
ReadPacket without servicing that completion. It times out with the exact
physical request. The actual pinned CDC driver uses `tu_fifo_read_n` and
`_prep_out_transaction`, not the newer generic endpoint-stream API in the
initial hypothesis. This proves a matching source mechanism; it cannot recover
the physical controller's exact interrupt history.

The repair retains PacketIO and its delimiter ownership. A 64-byte cache reads a
bounded chunk under the outer guard, with explicit USB-task passes before and
after that guard. It never runs task processing or waits while owning the guard.
TX coordination and the accepted large-response repair are unchanged. The total
5000ms receive deadline remains; progress does not renew it. No storage, profile
schema, selection, migration, durability or B1–B8 semantics change.

## Regression and fault isolation

Frozen895 negative: first failing nonzero synthetic body253 /wire257 bytes for
the tested schedule; exact physical3074/3089 fails at5000ms, with256 raw bytes
consumed,64 endpoint bytes awaiting task processing,2769 upstream bytes. This
threshold is encoding/schedule-dependent. Normal completion scheduling accepts
the same bytes. The repaired source passes113 actual protobuf request shapes,
1/63/64/65/127/128/255/256/257/512 boundaries, StageA/B/C and max-profile shapes,
8191-byte valid-protobuf unknown-field control, zero-rich/254-block framing,
separate delimiters, adjacent cached frames and late-tail resynchronization.

1024 large mutation receptions retain the same parser/cache/FIFO across20 DTR
cycles, alternating payloads with mixed small requests and84 extra READ request
receptions. Complementary pinned TX tests reconstruct1024 full READ responses,
20 reconnects and bounded slow/drop/stall controls. These are source/model tests,
not new physical acceptance. One-byte/ms physical UPDATE completes; a longer
continuously progressing body still stops at the same5000ms total deadline.

The actual backend test proves a partial ticket-bearing body cannot mutate
MemoryStorage or activate the pending rule; post-resynchronization PULSE retains
the timeout; stale common admission leaves the rule inert; complete traced UPDATE
emits ordered receive/admission/activation/branch stages then reconciles by QUERY.
Trace failure after activation clears the hook without dispatching mutation.
MemoryStorage does not simulate the physical injected storage outcome. Separate
host/pending-hook and checked-storage suites cover those source boundaries.
The [host audit](profile_store_rx_host_audit.md) verifies exact receipt bytes,
short-write reconstruction and10000 pending-hook attempts remaining inert.

## Observability, resources, review and handoff

Candidate-only USB diagnostics use bounded metadata in the existing8192-byte
frame buffer and two32-byte RAM snapshots. No diagnostic traffic competes with
an arriving body. The [hardware packet](profile_store_rx_hardware_packet.md)
defines phases, limits, pulse resynchronization caveat and the next exact row-A
gate. No dry-run mutation capability is invented.

The [resource audit](profile_store_rx_resource_audit.md) accounts for both static
RAM and the heap-allocated backend's cache/snapshots, request stack and USB task
paths. Exact final reports are bound to the custodied ELF. Physical watermarks
1936 core0/3716 core1 and heap9048/74584 are historical895 measurements, not new
candidate observations. No whole-target IRQ/ROM stack bound is claimed.

The [fresh independent review](profile_store_rx_independent_review.md) answers
all eight required questions. Source, host, protocol, persistence/recovery,
large RX/TX and resource checks are retained with the exact candidate. The
separate [one-reset adjudication](profile_store_rx_device_adjudication.md) and
new hardware gate are prepared only. No controller action, reset, flash,
campaign continuation or canonical merge occurred. Nunchuk remains NOT_TESTED.
