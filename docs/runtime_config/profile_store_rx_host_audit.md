# Retained 895 inbound request and host writer audit

The exact failed UPDATE was **3,074 protobuf bytes / 3,089 COBS wire bytes**.
Its retained request receipt and transmit journal agree byte for byte. The host
recorded completed OS transmission, then received exactly one normal CMD_ERROR
frame 5.000585375 seconds later. That frame contains `Profile store frame timeout`.
No ProfileStore response bytes or device-stage frames precede it in the recorded
UPDATE receive stream. The narrow supported boundary is
`LARGE_UPDATE_WIRE_TRANSMITTED_DEVICE_FRAME_READER_TIMED_OUT`.

This retains the separate `MULTI_PROFILE_STORE_895_READ_GATE_HARDWARE_PASS`:
84 physical full-profile READs, 20 reconnect cycles and healthy resource margins.
The candidate is permanently full-campaign
`HARDWARE_FAIL — LARGE_PROFILESTORE_REQUEST_RX_TIMEOUT_DURING_TICKETED_UPDATE`.
Earlier 594 and d596 hardware failures, reset adjudications and uncertainty labels
remain historical evidence. This audit performed no controller operation.

## Exact evidence

The append-only physical record is summarized in
[profile_store_rx_physical_adjudication.json](profile_store_rx_physical_adjudication.json).
Standalone copies of the relevant receipt, raw journals, pending-state replies,
operator stop and READ gate result are in
[`tools/fixtures/profile_store_rx_host`](../../tools/fixtures/profile_store_rx_host/).
Its `manifest.json` identifies each original relative path, byte length and SHA-256.
The original files were only read; no source evidence was rewritten.

| Item | SHA-256 |
| --- | --- |
| UPDATE protobuf | `96c2d8ce408eb41c7e24230e106f2d1647c5cb8930a3f473ca7c9af2038d4063` |
| UPDATE COBS wire | `9ac14ee426193d4ba07dac9484165007705f86e48f55d756da28e26fa4c11b20` |
| Immutable request receipt | `fdb1a4d236231444839c3c4d0d7a0b93c2748680ddfb2a21c4be4b10be32fdde` |
| Mutation journal | `c83e9e468ff7e771f58c20dc7d072a45929f1b1e875947edda829d4c55b49757` |
| Received CMD_ERROR frame | `768fe84df935a969f7150eb8308aad2017b949a5cf621888cf6aeb531cf1971f` |

The protobuf requests operation UPDATE, profile ID 22, expected revision 130,
expected generation 160, incarnation 1, token `0xf000000000000100`, and fault
ticket 1. Its profile is schema 3. `liveness_trace` is false. The operator did not
supply `--trace`; 895's CLI would not set this field for UPDATE even if supplied.
Absence of stage 1 therefore is **not independently proof** of absent decode.

The received wire is:

```text
1d0550726f66696c652073746f7265206672616d652074696d656f757400
```

Production COBS decoding yields command 5 followed by the 26-byte ASCII timeout
message. The journal contains one 30-byte receive chunk, one delimiter, no partial
preceding frame, and no decoded ProfileStore response. The CLI stopped on the
unexpected command; the operator stopped because no decoded ProfileStore result
was available. OS write acceptance took 449,333 ns. The receive timestamp is
5,001,034,708 ns after transmit-attempt and 5,000,585,375 ns after transmitted.
These are host journal timestamps, not a measurement of USB bus acknowledgement.

## Source-supported boundary and fault state

The frozen 895 `ConfiguratorBackend::HandleProfileStore` calls `ReadPacket` first.
Its `_packet_timed_out` branch emits precisely this CMD_ERROR and returns before
creating the protobuf input stream and calling `pb_decode`. This unique source
branch, together with the received frame, establishes failure before successful
request decode. It does not establish how many incoming bytes firmware consumed
or the exact physical interrupt schedule.

`ReadPacket` only operates the PacketIO reader, time checks and delay. It calls
no CheckedStorage primitive or fault hook. After complete request decode, common
protocol/ticket eligibility checks and durable transaction admission, the
mutation branch calls `ProfileStoreFaultControls::BeginMutation(ticket)` before
dispatching UPDATE. The pending ARM response and subsequent STATUS both report
pending=true, ticket 1, armed=false and triggered=false (omitted protobuf booleans
decode to false).

The actual `ProfileStoreFaultControls.hpp` confirms that `Arm` sets pending and
explicitly uninstalls the CheckedStorage hook. `BeginMutation` alone turns that
pending ticket into armed and installs the hook. `Hook` also requires armed,
even if directly called. The host test compiles this actual header, attempts
10,000 matching hook calls while pending, proves all inert, rejects a mismatched
ticket, then proves the matching ticket activates exactly the intended boundary.
The row-A intended record/open-write injection is **UNTESTED**. The current
volatile and persistent post-row state remain **UNKNOWN** pending separately
authorized reset/read-only adjudication.

## Actual host write control

Both candidate and general serial tools use
`glyph_serial_config_tool.PosixSerialPort.write_all`. In frozen 895 it repeatedly
submits `data[total:]` through `os.write`, advances `total` by the returned positive
count, and returns only after all bytes have been accepted. It has no 64-byte,
256-byte or FIFO-sized truncation rule. `candidate.request` emits `transmitted`
only after this method returns. The receipt was fsynced before transmission;
reconstructed production COBS bytes match its journal wire length and SHA-256.

`tools/check_glyph_profile_store_rx_host.py` executes both the exact frozen 895
method and the current production method with forced successful OS writes of at
most 1/63/64/65/127/128/255/256/257/512/3089 bytes. Every case reconstructs all 3,089
bytes, then uses actual production COBS and runtime ProfileStore protobuf decoding
to assert the exact original request. It also executes the actual candidate
request orchestrator, verifying that `transmitted` is emitted only after complete
OS acceptance and that its ideal receiver returns the expected response.

Injected `InterruptedError` and `BlockingIOError` propagate from the 895 method;
they are not silently ignored or reported as transmission success. These cases
retain an exact 64-byte prefix in the offline OS sink and produce no transmitted
event. Write-unavailable, zero and negative progress also fail closed. No physical
row-A exception occurred: its transmitted event was recorded. Python/OS automatic
restart behavior is not needed for this conclusion. The test makes no claim that
OS acceptance proves delivery into the device's FIFO.

Validation command (offline; never opens a serial port):

```sh
python3 tools/check_glyph_profile_store_rx_host.py --output-dir /tmp/glyph-rx-host-results
```

The source-faithful pinned TinyUSB/PacketIO regression is a separate proof of
actual receiver progress. This host audit does not replace that test with an
unbounded receiver or claim it locates the failed physical controller's PC.
