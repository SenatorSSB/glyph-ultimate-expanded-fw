# New RX-liveness candidate: hardware gate prepared only

Bind the exact committed candidate SHA/tree and preserved UF2 from the immutable
HANDOFF. Rehash those bytes before flashing; do not rebuild or substitute an
artifact. No hardware action is performed or scheduled by this packet. A
separate authorized human session must first assess the
[failed 895 one-reset adjudication](profile_store_rx_device_adjudication.md).

1. Flash the exact new candidate through the established manual route. Enter
   normal Configurator, collect pulse and STATUS with unique raw journals,
   verify identity, persistent-state expectations, no pending/armed fault and
   resource margins. A normal STATUS includes its existing capacity scan.
2. The current protocol has no safe mutation dry-run flag. Therefore use the
   explicitly requested alternative: the exact row-A record/open-write/
   fail-before ticketed UPDATE of disposable ID22, after its read-only preflight.
   Preserve IDs1/3/4. Derive token/generation/incarnation/revision from current
   authoritative readback; do not reuse failed token or blindly reuse ticket1.
   ARM once, verify its pending ticket and armed=false with STATUS, then send
   exactly one UPDATE using that ticket and the same retained profile payload.
   Save exact protobuf/wire receipt and `--trace --trace-out NEW.jsonl` evidence.
3. Require full reception evidence (stages30–38, decoded stage1), common
   admission39, accepted ticket40, operation-branch41, and the source-defined
   row-A result/trigger report. Follow the frozen row's QUERY/reconciliation
   rules only after this gate succeeds; a frame timeout or ambiguous response
   stops the session with no automatic retry, clear, QUERY or reset.
4. Recheck useful profiles/Config and collect resource samples. Preserve the
   prior 895 READ gate separately, and rerun affected new-candidate READ and
   reconnect checks. Only after receive/decode and intended mutation outcome are
   established may a separately authorized operator resume the remaining B9/B10
   matrix in the existing strict and liveness hardware packets. Do not mark any
   unattempted row PASS. Exact human hardware acceptance is required before merge.

## Diagnostics and interpretation

Mutation `--trace` is opt-in. Stages30–38 retrospectively report recognized
command, frame start, raw bytes consumed, decoded body bytes, RX task-helper
calls, EOP, elapsed ms, last-progress ms and decode entry. They are emitted only
after the entire frame decoded; absence alone cannot locate a hang. Stage1 is
successful decode;39 is after common admission but before ticket activation;
40 means the supplied ticket was accepted (zero means no fault ticket);
41 means the selected operation branch was entered, before its storage body.
It does not prove CheckedStorage ran or a fault triggered. Stages8/9 retain
response encoding meanings. A missing stage may reflect inability to send it.

Receive timeout emits a bounded CMD_ERROR with phase/raw/decoded/elapsed_ms/
tasks/last_ms/fetched/eop. RAM-only PULSE fields `rx_*` preserve the latest
non-PULSE snapshot. Flags:1 EOP,2 timeout,4 oversize,8 decode rejected. Raw and
fetched counters exclude command ingestion; fetched may include prefetched
following-frame bytes. Tasks counts helper calls, not successful completions.
No full profile is copied and no diagnostics are persisted to flash.

PULSE cannot bypass an abandoned unterminated COBS frame: PacketIO must first
resynchronize through that frame's delimiter. A reset erases the snapshot.
These limitations do not authorize recovery commands after a failed row; retain
the automatic CMD_ERROR and host journal first, then seek separate adjudication.
Use a ten-second host ceiling while firmware retains the five-second total RX
bound. Preserve exact candidate/UF2, request receipt, OS write completion, raw
chunks, stage values, response/error and last authoritative state on failure.
No SWD probe is available. Nunchuk remains NOT_TESTED. Canonical is unmerged.
