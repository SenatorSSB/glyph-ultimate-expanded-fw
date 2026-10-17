# Independent fault-campaign liveness review

Verdict: **SOURCE REVIEW PASS for DIAGNOSTIC_READY**, conditional on the final
exact committed build, target resource gates and content-addressed custody.
This is not a physical root-cause finding, hardware PASS, chapter completion or
permission to merge. Candidate 594066d9 remains hardware FAIL. No device action,
firmware implementation or Git mutation was performed by this reviewer.

The fresh reviewer independently read the retained physical adjudication,
`/private/tmp/fwfa.log`, the full implementation diff against 594066d9, the new
adapter, CLI, schema, harnesses and audits, and the selected pinned TinyUSB
port/CDC/FIFO/OSAL sources. The separate future device-adjudication and resumed
hardware packets preserve the source-only boundary and do not erase old PASS
or FAIL observations.

## Required answers

1. **ARM_TRANSMISSION_UNPROVEN.** The old CLI first sends STATUS and uses the
   same generic timeout for that response and the subsequent ARM response.
   The retained 5100 ms failed process and generic log distinguish neither.
   The independent STATUS timeout is recorded at 10089 ms. No UPDATE followed;
   the intended Record/Write injected operation did not execute. The exact
   device-side blocked instruction is unknown. A new journal cannot supply
   missing historical evidence.

2. **A concrete source mechanism exists, but physical attribution is unproven.**
   The selected TinyUSB OSAL uses nonrecursive Pico mutexes. Old unguarded
   application CDC FIFO/endpoint operations can hold an internal mutex when
   the deferred USB task IRQ interrupts them. That IRQ takes the distinct
   global USB mutex and, through DTR/reset/endpoint handling, attempts the
   internal mutex held by its interrupted caller. The 49.7-day nominal wait
   prevents the outer writer deadline and later Configurator requests from
   progressing. Host device-node retention does not prove CPU/USB servicing.
   Independent source inspection confirms the relevant call topology, not
   that this interleaving occurred on the board.

3. **The identified transport waits are bounded; full STATUS has no proved
   wall-clock deadline.** All Configurator stream views use the adapter.
   Direct CDC calls occur only after nonblocking acquisition of the same
   outer mutex that the IRQ tries. No yield/delay occurs inside that guard.
   The sole CDC instance is 0 in both normal and recovery construction.
   Framework `__loop()` calls `yield()`, and explicit read/write waits also
   yield outside the guard, allowing deferred task work to resume. The new
   `writeAvailable` performs one attempt; ProfilePacketWriter owns a single
   2-second packet deadline. RX uses a total 5-second deadline. ARM itself
   does no storage I/O, but the CLI's STATUS preflight still does synchronous
   filesystem work. Full STATUS includes real capacity and durable Config
   reads and is not cancellable if arbitrary target code stalls. RAM-only
   pulse and opt-in phase frames provide narrower diagnosis without weakening
   accounting. Neither host timings nor finite application loops prove
   real-time completion under unrelated IRQ, RAM or flash failure.

4. **An unresolved ARM acknowledgement leaves an inert recoverable rule.**
   ARM records a pending ticket and installs no hook. Only an explicit
   ticket-bearing new mutation can activate it, after replay/common admission
   checks. Exact durable replay remains ahead of ticket activation, so consumed
   tickets do not invalidate a committed receipt. The active rule is removed
   at request completion, including an unused rule; ordinary mutations and
   legacy SET cannot activate pending state. STATUS/pulse expose pending/ticket
   state, CLEAR removes it, and reset clears volatile state. Tickets are
   session-local; the operator packet correctly forbids automatic reuse across
   reboot. Ticket fields remain bound by canonical request hashing.

5. **B1–B8 are retained within source-review scope.** Capacity/reserve/GC(B1),
   checked persistence(B2), reboot-bound selection(B3), root/high-water
   recovery(B5), authenticated migration(B6), recovery initialization(B7),
   names/health(B8) have no implementation edits in this delta. B4 replay,
   complete semantic hashing, monotonic token handling and durable reference
   results remain in place; the ticket branch follows durable replay and
   admission. Existing zero-valued added protobuf fields do not change the
   encoding of historical ordinary requests. Candidate-disabled protocol
   controls still reject candidate fault/pulse operations. Shared Configurator
   USB changes do require representative ordinary/recovery hardware coverage,
   as the packet explicitly records.

6. **Resource diagnostics are reasonable to retain, subject to exact final
   ELF gates and physical acceptance.** All 159 retained samples have flat
   heap-arena current/peak 9092 bytes; final core0/core1 minima 1472/3716 bytes.
   These do not exclude an abrupt later failure or a leak within already
   reserved allocator space. Independent execution of the ELF checker on the
   preliminary repaired ELF confirmed empty non-stack scratch intervals,
   correct core bank/linker boundaries, no atomic helper, and direct
   nonrecursive `_sbrk` calls. Its 10000 fill/50000 scan sanitizer controls and
   three adversarial ELF/call negatives pass. The exact final ELF must pass
   again; the preliminary ELF is not custody. No enlarged memory limit or
   changed core1 flash-pause mechanism is required by the evidence.

## Independent validation and resolved findings

The reviewer independently reran the CDC coordination sanitizer checker,
offline candidate CLI checker, and actual Configurator/Nanopb/PacketIO strict
protocol checks with candidate disabled and enabled. All pass. The enabled
run covers 20 profiles, 128 updates, 1024 lost-ARM-response cycles, 7680 mixed frames,
ordered phase responses and slow-trickle timeout recovery. The deterministic
CDC schedule model covers 10000 iterations and detects the omitted-guard negative;
it is not a complete RP2040 USB simulator or physical reproduction.

The independently inspected real pinned-LittleFS report covers the exact
generation 160/count 20/ID22 revision 130 shape, 129 successful updates, real GC,
43 lost results with QUERY/replay and 2048 three-fault cycles. Both frozen and
current storage pass 6144 faults/20610 capacity samples, retain no native handle,
and return to the 768-byte mount allocation baseline. It detects the synthetic
missing-close mutant and the old active-on-ARM acknowledgement-loss behavior.
Current maximum observed host Capacity time 7.212 ms and 1900 block reads are
workload measurements, not target deadline proof. Config files are realistic
fixtures; the storage harness does not execute Persistence or USB, while the
backend harness uses injected storage. Their coverage is complementary.

Two review findings were repaired and rechecked before this verdict:

- The adapter's retrying write could nest its 2-second budget inside the
  packet writer's 2-second budget. `writeAvailable` now performs one guarded
  attempt and restores the packet writer's sole deadline ownership.
- `--trace-out` could alias `--output` and lose the completed journal when
  result output was written. Argument validation now rejects aliases with
  output, immutable request receipts, replay receipts and input profile files;
  offline negative checks pass.

No unresolved material source finding remains. The final build/custody and
hardware gates remain mandatory. A later physical failure must retain the
phase journal and last stage; no-stage receipt still does not identify a PC.

## Reviewed implementation fingerprints

These SHA-256 values bind the reviewed source before commit; final custody must
verify the committed files match them. This review document is excluded from
its own identity.

| Path | SHA-256 |
| --- | --- |
| `HAL/pico/include/comms/CoordinatedCdcStream.hpp` | `72b956f1f41dd309a7ad60c4642eb2193757a07f116911f5001258b562870848` |
| `HAL/pico/include/comms/ConfiguratorBackend.hpp` | `a534f5df233e8313a1fa881c5b226920b10e8ee7ca255e2aa0a8fce87bd2a274` |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp` | `7bf5b68700d38c3d14a433effd738b211927691b38069c162c96319777951a03` |
| `include/core/ProfileStoreFaultControls.hpp` | `d30fe5c4efd58c41d88e044a76c1d5ecc72c6d621bf6934927f405e538c13c67` |
| `schema/haybox/config.proto` | `4991387de47c8d56d5a1395e6ff7c9d064f89fe03f1e7191182e399e840979a1` |
| `tools/glyph_profile_store_candidate_tool.py` | `3ce9b7637afb3ecbac4331969434db7496b1037fceee1d7d94458309a66efa2f` |
