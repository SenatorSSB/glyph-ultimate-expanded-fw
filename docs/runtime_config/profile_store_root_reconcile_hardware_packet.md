# New candidate: single root-reconciliation fault hardware gate

Prepared, NOT_EXECUTED. No controller action or canonical merge in this task.
Use only the newly committed direct child of4ee and its preserved UF2, pinned
by the accompanying immutable SHA/tree/parent/base/branch/custody manifest.
Do not use4ee for this route. Human exact SHA/artifact PASS remains required.

First complete the separate [failed4ee adjudication](profile_store_root_reconcile_device_adjudication.md).
Only after those observations match expectations may the owner manually install
this new exact UF2, without filesystem image/format/erase. Preserve useful IDs,
Config, all exact original bytes and identity history. Missing custody or any
unexpected state is a stop; no reset/retry/repair is implied.

1. PULSE/STATUS once. Require strict candidate, mutation protocol2, fault-control2,
   `root_reconcile_fault_capable`, no pending/armed fault, healthy roots/Config.
   Export Config, paged LIST and full READs1/3/4/22; bind exact generation G,
   incarnation, actual ID22 revision R and useful-profile hashes. Record resource
   diagnostics. ID22 must be disposable and unreferenced; stop if it is not.
2. Select a fresh token above durable high water. Retain its exact UPDATE request
   and approved disposable payload; do not reuse `0xf000000000001c00`. ARM
   control/Rename/lost-ack-after/skip0 once, preserve returned ticket. UPDATE ID22
   once with that ticket and exact fresh expectations. Require COMMIT_UNKNOWN,
   `directory.rename`, uncertainty8, generation G. Preserve the exact receipt.
   Do not QUERY yet. No replay or ordinary mutation during uncertain state.
3. ARM root/OpenRead/fail-before/skip0 once; preserve returned ticket T. This
   prepares an inert rule. Ordinary QUERY cannot activate it. Do not substitute
   root Read, control path, lost-ack, nonzero skip or an arbitrary query fault.
4. Execute exactly the special command below. Its built-in STATUS is read-only
   and verifies the entire pending shape/uncertainty/capability before sending
   exactly one QUERY. The request and trace output paths must be new. On timeout
   or error, stop and inspect the trace; never retry automatically.

```sh
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" query \
  --token "$TOKEN" --reconcile-fault-ticket "$TICKET" \
  --request-out root-query.request.json --trace-out root-query.trace.jsonl \
  --output root-query.response.json
```

COMMIT_UNKNOWN intentionally gives the client exit1; inspect its complete
response, not only process status. Require stages42(T),43(1),44(1),45(1),46(0),
then8/9 and final COMMIT_UNKNOWN, exact ticket, operationOpenRead1,
pending=false/armed=false/triggered=true, uncertainty/read-only/root-invalid26.
There is exactly one store reconciliation attempt. No identity-only ABORTED
checkpoint may publish in this request. No generation advance or new profile
revision/ID/root deletion. The first actual root is `/ultimate-v2-0.bin`; control
loads must not consume path2. Depending on root parity, failed-read response
RAM generation can be G or G-1; require <=G, not equality, and do not treat the
older companion metadata as final healthy authority.

5. Preserve the entire first result before proceeding. With the one-shot scope
   ended, perform exactly one later ordinary manual reset (no CLEAR needed).
   PULSE/STATUS/LIST/READ22/READ1/3/4/GET_CONFIG and ordinary exact-token QUERY,
   each once. Require healthy both-root reconciliation, generation **G+1**,
   actual ID22 revision **R** and baseline payload; intended **R+1** appears only
   in the ABORTED receipt. Useful IDs, Config and selectors remain unchanged;
   token high water cannot fall, no pending/armed fault. Record resource values.
   No extra checkpoint should occur on resolved QUERY. Disagreement stops.

No physical root corruption/deletion, GC, selection, RT2, rollback, cleanup or
additional mutation is part of this row. The changed-request conflict and
reserved-ID proofs are host tests, not permission to send another hardware
mutation. This single row cannot imply full B1–B10 hardware acceptance. Any later
campaign continuation needs its already-authorized scope. Nunchuk NOT_TESTED.
