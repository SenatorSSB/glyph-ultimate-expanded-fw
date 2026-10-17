# ProfileStore READ liveness repair

Disposition: source repair and diagnostic candidate, **HARDWARE_TEST_REQUIRED**.
No device action, reset, flash, campaign continuation or canonical merge occurred
in this investigation. The exact committed build/custody tuple is supplied by
its content-addressed HANDOFF after this source snapshot is frozen.

## Physical evidence remains bounded

[Retained adjudication](profile_store_read_physical_adjudication.json) establishes
`READ_REQUEST_TRANSMITTED_FINAL_RESPONSE_NONE`: host write completed, then the
first ID1 READ timed out after10seconds. The exact reconstructed request is
`080218032801`, matching the retained SHA. There were no recorded READ stages,
raw RX bytes or delimiter counts. Partial output, zero output, device decode,
and the blocked physical PC remain unknown. The adjacent `set -e` terminal
sequence ended there; ID3/4/22 and GET_CONFIG were not attempted. No pending or
armed fault existed, no mutation followed, and no fresh device inspection was
performed during diagnosis.

d596 remains permanent `HARDWARE_FAIL —
PROFILESTORE_READ_LIVENESS_FAILURE_AFTER_CDC_COORDINATION`. Earlier594 remains
permanent `HARDWARE_FAIL — CONFIGURATOR_LIVENESS_FAILURE_DURING_FAULT_CAMPAIGN`;
its reset adjudication PASS, `ARM_TRANSMISSION_UNPROVEN`, and
`USB_RACE_PHYSICAL_CAUSALITY_UNPROVEN` remain unchanged. Previous source controls
passing are historical test results, not physical acceptance.

## Proven source mechanism and repair

The [pinned USB audit](profile_store_read_usb_audit.md) proves a second defect:
the coordinated writer can defer the USB completion task while holding the
outer mutex, fill the256-byte FIFO, then wait with `delay(1)`, which does not
service USB on Arduino-Pico3.6.3. Its two-second deadline expires before the
COBS delimiter is queued. Later ordinary-loop progress sends only a prefix.
The earlier ideal-stream test did not model finite FIFO/deferred completion;
its passing result did not establish multi-packet progress. Any earlier claim
that this pinned `delay(1)` itself yields USB is superseded by the pinned source.

The repair explicitly runs the pinned USB task outside the foreground Guard,
then flushes under the outer mutex. Enqueue and full-FIFO waits service progress;
final COBS completion drains the FIFO within the same original2second deadline.
No blocking wait holds the outer mutex. Generic `yield()` is avoided here because
its separate FlushCDC call is unguarded. The existing failed-prefix delimiter,
receive total deadline, inert ticketed faults and persistent-format behavior
remain intact. An empty FIFO means endpoint submission, not observed host ACK.

Frozen d596 fails the source-faithful negative control. For one legal dropped
completion schedule, nonzero body317 is the first failure in a1..600 sweep:
321 framed bytes exceed64 endpoint+256 FIFO. This is a schedule/pattern-specific
boundary. Actual STATUS104/LIST276 complete while READ1989/3071/3076/3072/4038
leave320-byte prefixes. The repaired path reconstructs all exact complete frames,
including the final short tail/delimiter, when the modeled host drains.
This locates the reproducible source defect in transmission, not record loading
or response encoding; it does not retroactively prove the failed physical PC.

## Independent controls

The CDC regression uses actual extracted old/new writer and packet routine,
actual PacketIO COBS, Nanopb, pinned CDC/FIFO/OSAL code and an explicit endpoint/
IRQ/task/host model. Coverage includes thresholds1/63/64/65/255/256/257/512,
actual messages,8191-byte zero/nonzero/mixed bodies,1,024 rotating full READs,
147 mixed rounds,20 DTR close/open cycles, dropped responses, slow/no-drain,
partial response recovery, exact delimiter receipt and stable host allocation.
It separately models host receipt after endpoint submission. The physical OS,
USB silicon and full scheduler are not simulated.

The [storage/encode audit](profile_store_read_storage_audit.md) independently
passes6,000 READs on each frozen/current source using actual pinned LittleFS and
generation160 history, including ID22rev130, after129updates and43query/replays.
Stat/open/read/close/CRC/decode/validation complete, with no READ writes/erases,
open-handle leaks or LittleFS allocation growth. Trace observer failure at every
storage stage still closes handles. Actual retained ID1/3/4/22 and maximum
accepted Stage-C payloads undergo1,000 Nanopb roundtrips each per source.
The complete static response schema bound6700 is below8192; profile/response/
frame are static and no unbounded protobuf callbacks are present.

The focused existing checked-I/O, strict protocol, identity, selection, Config
persistence, resynchronization, lifecycle, atomicity, LittleFS, decoder, stack,
resource, StageA/B/C and predecessor controls are retained in handoff evidence.
They support preserving B1–B8; they do not substitute for new hardware acceptance.
[Fresh independent review](profile_store_read_liveness_review.md) records the
seven requested judgments and resolved test-fidelity findings.

## READ trace contract

`read --trace --trace-out NEW.jsonl` opts into candidate-only RAM/USB diagnostics.
No flash log, watchdog, core1 pause or recovery behavior is added. Stages:

| Stage | Meaning/value |
| --- | --- |
|1,2|Request decoded; Config CRC complete|
|10,11|Before record probe; record size known (bytes)|
|12,13|Before checked I/O; native open returned successfully|
|14,15|Read returned (bytes); close returned (1=success)|
|16,17,18|Record/header CRC complete; profile decoded; validation returned (1=valid)|
|19|READ returned and profile population flag set (1=has_profile)|
|8,9|Before response encode; encoded response bytes|
|20|Before final COBS/TX, protobuf byte count|
|21|Exact wire bytes accepted by writer for final response attempt|
|22|Final flush requested (1=yes, only after complete COBS encoding)|
|23|FIFO submission completed within deadline (1=yes)|
|24,25|Final response attempt submitted successfully / failed|

Stages21–25 follow the final response attempt, never interrupt its COBS body.
A failed prefix is delimited before any later stage packet. If USB cannot carry
trailing stages, the last stage plus raw partial prefix still survives on host.
Tracing failure suppresses later callbacks and file close always runs; the
scope restores ordinary behavior. Non-READ tracing keeps its previous contract.

The host records exact request bytes/hash and OS write completion, raw bounded
chunks, running received-prefix SHA/count, COBS frame hashes, each stage/value,
timeout partial frame and delimiter state. It requires a reconstructed response
plus stage24 for traced READ success. Stage25 is a failure. Trace files use
exclusive creation and fsync; existing traces are never overwritten. Offline
parser controls cover actual1989-byte READ chunks, delimiter/trailer separation,
partial prefix timeout, complete-response/missing-trailer and corrupt-prefix
failure recovery. Raw malformed prefixes are retained, not counted as success.

## Resources and next gate

Target layout remains Config31312, ProfileStore4352, Directory3848,
UltimateProfile2152, Request2304, Response2992 and static frame8192 bytes.
The observer adds12 bytes of static RAM; source contains no new dynamic allocation.
The target resource report includes the new live ReadFile→observer→trace→writer→
USB-task stack composition, split compiler clones and pinned task/endpoint code.
The measured traced checked-READ CDC path is1912bytes; adding the enumerated
control/descriptor inventory gives2160bytes. A conservative four-level response
encode inventory is2824bytes. The existing checked-record CREATE chain remains
2640bytes. These fit the4096-byte scratch-bank envelope, excluding unmodeled
paths. Per-function/enumerated C evidence does not certify whole-target IRQ/ROM paths;
exact hardware stack/heap samples remain required.

Use the separate [d596 one-reset adjudication](profile_store_read_device_adjudication.md),
then [new-candidate hardware packet](profile_store_read_hardware_packet.md).
After exact new flash and pulse/STATUS, perform **immediate traced ID1 READ before
fault/capacity campaign work**, then bounded repeated read-only regression. Only
that gate passing permits the separately authorized operator to resume remaining
B9/B10. No automatic retry or mutation follows a READ failure. Both failed
candidates remain failed, and canonical merge requires exact human hardware PASS.
