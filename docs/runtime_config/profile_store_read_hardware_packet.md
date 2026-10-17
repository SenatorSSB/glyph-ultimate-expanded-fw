# New exact READ-liveness candidate — prepared only

No device actions occurred during source diagnosis. A separate human hardware
session must bind the exact committed SHA/tree and content-addressed UF2 from
HANDOFF, rehash that file and flash those exact bytes without rebuilding. Never
reuse d596 or594 for acceptance. Canonical remains unmerged.

First complete and assess the separate
[one-reset read-only adjudication](profile_store_read_device_adjudication.md).
After exact new-candidate flash, use the existing normal Configurator entry.
Retain every journal under a new unique filename. Timeout10seconds maximum;
no automatic retries, no mutation on a failed read, no Clean/factory reset.

1. Capture pulse and traced STATUS, verifying candidate identity, unchanged
   authoritative generation/incarnation, no pending/armed fault and resource
   margins. The required STATUS itself includes its source-defined capacity
   scan; perform no separate capacity/fault campaign before the next step.
2. **Immediately run ID1 READ with `--trace --trace-out NEW.jsonl`**, before
   reconnect loops, capacity stress, fault ARM, mutations or cleanup. Require
   exact complete decoded profile/hash and stage24 terminal. Stage9/20 carry
   response bytes,21 accepted COBS bytes,22 flush requested,23 FIFO submitted.
   FIFO submission is not a device observation of host acknowledgement.
3. Run a bounded read-only regression:20 independent process/open-close cycles,
   each with pulse, STATUS, LIST pages0/8/16 and READ IDs1/3/4/22. Trace the first
   READ in each cycle and at least one READ per ID; record every response and
   raw receive journal. Compare generation/incarnation and payload hashes on
   every cycle. This is80 physical READs; the source harness separately supplies
   >=1000 full-response stress. No physical1000-read claim is implied.
4. Re-read STATUS/resource samples and GET_CONFIG; verify no persistent state
   change and no progressive heap/stack degradation. Preserve representative
   legacy Configurator GET_CONFIG/identity results because the transport is
   shared. Stop if any frame, terminal stage, state or resource check fails.
5. Only after these gates pass may the separately authorized hardware operator
   resume the remaining frozen B9/B10 rows using the ticketed pending-fault
   protocol in [the earlier campaign packet](profile_store_liveness_hardware_packet.md)
   and [the strict packet](profile_store_strict_hardening_hardware_packet.md).
   Never repeat a failed candidate's acceptance or infer unattempted rows passed.
   Preserve stable useful IDs; mutate only the existing authorized disposable ID.

Failure report: exact SHA/UF2, last host phase, OS write completion, all stage
numbers/values, received byte count/prefix SHA/raw chunks, last delimiter state,
full response if any, final stage if any, last authoritative state and physical
observation. Stage10 precedes probe;11 size known;12 before checked I/O;13 open
complete;14 data read complete;15 close complete (value1 means successful);
16 record/header CRC complete;17 protobuf decode complete;18 validation returned
(value1 valid);19 READ returned/profile populated;8 before response encode;
9 encode complete;20 before final COBS/TX;21–25 are trailing observations.

A missing stage cannot by itself distinguish a failed operation from failure
to transmit that stage. Partial RX plus exact previous stage narrows the next
investigation. If USB cannot deliver trailing diagnostics, the host still
retains raw prefix bytes and last successfully received stage. Nunchuk remains
NOT_TESTED. Exact human hardware PASS is required before any canonical merge.
