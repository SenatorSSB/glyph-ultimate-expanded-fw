# ProfileStore fault-campaign liveness diagnosis

Disposition: **MULTI_PROFILE_STORE_FAULT_CAMPAIGN_DIAGNOSTIC_READY**, subject to
final exact committed build, custody and independent review recorded in HANDOFF.
Physical attribution remains **UNPROVEN**. No device action or canonical merge
is authorized by this result.

## Physical adjudication

`594066d9bb65b9f93c14e0e24e9d2002c3f83924` / UF2
`fb8f005995b6feef33a196f1c3d8dbc6985350ca3d4bc40d22a03cf1724c4413` is permanently
**HARDWARE_FAIL — CONFIGURATOR_LIVENESS_FAILURE_DURING_FAULT_CAMPAIGN**.
Earlier physical PASS rows remain valid within their observed scope. The
record/write failure injection did not execute: no disposable UPDATE followed.

**ARM_TRANSMISSION_UNPROVEN.** The exact command transcript records a 5100 ms
failed `arm` process; `/private/tmp/fwfa.log` contains the generic response
timeout used by both STATUS preflight and ARM. Either a preflight timeout or a
fast successful preflight followed by ARM timeout fits these observations.
There is no retained raw/per-request capture. The subsequent independent STATUS
process timed out after 10089 ms. The exact device-side timeout point is unknown.
[Retained adjudication and transcript](profile_store_liveness_physical_adjudication.json)
contains the evidence, without inferring execution from the command name.

The old volatile rule may be absent, or may be active if ARM reached its
handler. No UPDATE was sent, so its matching Record/Write boundary did not run.
A reboot would clear it; no reboot was performed in this source-diagnosis run.
The primary failure is Configurator liveness, not CheckedStorage::Write outcome.

## Source findings and repairs

A concrete **USB interrupt/main-code lock inversion** exists in the pinned
Arduino-Pico 3.6.3 TinyUSB path. `Adafruit_USBD_CDC` accesses FIFO and endpoint
mutexes without the global `__usb_mutex`. The deferred USB task IRQ takes that
global mutex, then may take the same internal locks during DTR/reset/endpoint
processing. If it interrupts main while main owns an internal nonrecursive
lock, it waits for the interrupted owner. Its `UINT32_MAX` millisecond timeout
is approximately 49.7 days; the outer 2-second writer deadline cannot interrupt
that call. A listed CDC device node does not prove core0 or Configurator can
progress. This mechanism explains how both host requests could time out while
the Mac still lists the device, but no captured PC/IRQ trace proves that this
specific physical failure took that path.

`CoordinatedCdcStream` now owns all three Configurator stream views (PacketIO
input, legacy output and bounded ProfileStore output). Production uses sole
CDC instance 0, as both normal and recovery constructors pass Serial. Short
direct CDC operations first **try** the same outer USB mutex. The deferred
IRQ defers work when it is held. No delay, yield, filesystem access, blocking
outer-lock acquisition, or `tud_task` call occurs inside the guard. Writes are
limited to FIFO-admitted bytes. ProfilePacketWriter uses a single-attempt adapter
method and owns one 2-second whole-packet retry deadline. Legacy writes retry
outside the guard for at most 2 seconds per call.
The frame reader now has a 5-second total deadline, preventing slow trickle
traffic from extending the old inactivity deadline indefinitely.

Candidate fault control version 2 makes ARM a **pending, inert rule**. A new
mutation must explicitly supply its returned `fault_ticket`; it is activated
only after durable replay and common admission checks. The rule is consumed
and uninstalled before response encoding, even when the requested operation
never hits it. Exact durable replay precedes ticket validation. Ordinary
mutations, STATUS, QUERY, legacy SET, and port reconnections cannot activate a
pending rule. CLEAR removes it; ordinary reset clears all RAM state. Tickets
are session-local, never an authorization to reuse a pre-reset fault receipt.
Fault fields remain part of the full semantic transaction digest.

No persistent layout, capacity accounting, checked publication, migration
receipt, stable-ID/high-water rule, recovery restriction, profile health,
selection or gameplay table changed. Normal binaries still reject candidate
faults and pulse requests. The USB coordination and total RX deadline apply to
Configurator transport in both candidate and ordinary builds.

## Narrow evidence for the next failure

Candidate operation14 `PROFILE_STORE_LIVENESS` / CLI `pulse` returns RAM state
without LittleFS access, Config encoding, or resource sampling. It is not a
capacity/health assertion. STATUS keeps its authoritative capacity and Config
reads; these are not replaced by stale cached values.

Opt-in `--trace` emits small token-matched stage responses before expensive
synchronous phases. `liveness_stage=0` is the final result; stages are:

| Stage | Last established boundary / next work |
| --- | --- |
| 1 | Request decoded; before Config CRC (pulse skips CRC) |
| 2 | CRC complete; before reconciliation/dispatch |
| 3 | Before capacity scan |
| 4 | Capacity complete |
| 5 | Before checked durable Config read |
| 6 | Config read complete; before resource diagnostics |
| 7 | Resource sampling complete |
| 8 | Before response protobuf encoding |
| 9 | Encoding complete; before final response transmission |

Progress transmission uses the same bounded coordinated writer; failure stops
that request before the next phase. It writes no flash, adds no watchdog/reset,
and touches no core1 pause behavior. A host seeing no stage can now distinguish
its own transmitted/preflight/ARM phases, but still cannot claim device receipt
or identify an arbitrary IRQ PC. The CLI's exclusive `--trace-out` JSONL journal
fsyncs attempt, completed write, device-stage, response and timeout events.
A completed host write proves transmission to the OS, not device execution.
Tracing can affect timing; retain traced and untraced controls in the bounded
hardware packet. No diagnostic claims total STATUS execution remains bounded
under arbitrary filesystem corruption or unrelated IRQ/CPU failure.

## Validation and retained limits

- [Real pinned LittleFS history](profile_store_liveness_storage_audit.md):
  v1→v2, 20 profiles, generation160, ID22 revision130, 129 updates, real GC,
  discarded results/QUERY/exact replay, and repeated preceding fault sequence.
  Frozen old storage and repaired storage both pass. This is evidence against
  a deterministic storage-history failure, not a reproduction of the hang.
- Actual Configurator/Nanopb/PacketIO retained harness: 20 profiles, 128 updates,
  1024 lost-ARM-response cycles, thousands of mixed frames, port-state flushing,
  ordered trace frames, ticket replay and slow-trickle deadline recovery.
  Backend uses injected storage; the separate pinned-LittleFS suite is the
  decisive filesystem control.
- Actual CDC adapter under 10000 deterministic IRQ/main lock schedules passes
  sanitizers. Omitting the outer guard reproduces internal-lock re-entry in
  the schedule model. This negative reconstructs the source race, not a physical
  interrupt trace or full USB-controller simulator.
- Old ARM immediately injects a later ordinary write after a lost response;
  current pending/ticket behavior rejects that negative. A synthetic missing
  native close is caught immediately by the LittleFS handle-list oracle.
- CLI offline orchestration separately proves preflight-timeout means ARM was
  not transmitted, while successful preflight/ARM-timeout records transmission.
- [Resource audit and chronology](profile_store_liveness_resource_audit.md): all
  159 retained samples, exact failed ELF, stack/heap/atomic controls. No observed
  arena growth or exhausted touched-stack margin. Instrumentation is retained;
  final candidate ELF must independently pass its bank/helper checks.

The [fresh independent review](profile_store_liveness_independent_review.md)
answers all six requested questions and approves DIAGNOSTIC_READY, with physical
attribution unproven. Twenty affected regression checks passed. Target source
measurement reports Config31312, ProfileStore4352, Directory3848, request2304,
response2992 bytes; the enumerated record-open call chain is2632 bytes with1464
bytes remaining in the 4096-byte scratch bank before unmodelled IRQ/ROM paths.
This is not a whole-target stack guarantee. The exact final committed build
must confirm these figures and the unchanged safe diagnostic bank placement.

Exact commands, exits, logs, source fingerprints, final memory sections and
UF2 identity belong to the content-addressed HANDOFF evidence, not a guessed
self-referential commit ID in this source file. Hardware is **NOT_TESTED** for
the new candidate; Nunchuk remains **NOT_TESTED**. No production acceptance or
canonical merge follows from host/static validation.

## Authority and delegation

Owner request: attachment `8a181997-61a9-48c3-a23e-08b5a229d2d4/Pasted text.txt`.
This explicitly authorizes the bounded repair, new branch/push/build/custody and
independent review, and prohibits all device actions in this run.
Canonical live ref remained `6b73a7c507f35c111745c6bdd341618b490cbdcd` at preflight.
The default read-only verification failed DNS; the permitted network-enabled
retry succeeded. Primary user edits were preserved in their checkout.

Repository delegation guidance applies. Native collaboration capability was
available. `liveness_resource_audit` independently audited target resources
and USB/source safety; `liveness_storage_stress` implemented the bounded real
filesystem regression; `fault_liveness_fresh_review` performs independent
post-implementation judgment. Root owns source integration, publication and
custody. No new user-owned chat, Planner, Curator or canonical writer was made.

Next: [separate device adjudication](profile_store_liveness_device_adjudication.md)
and [bounded resumed campaign](profile_store_liveness_hardware_packet.md).
