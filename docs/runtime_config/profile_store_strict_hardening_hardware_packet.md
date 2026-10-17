# Strict hardening: bounded owner hardware packet

Status: prepared acceptance procedure; **no device action or physical PASS is
reported by this packet**. Use only the exact committed candidate and primary
content-addressed UF2 named in the accompanying custody manifest. Earlier
f7ba82d4 hardware receipts do not accept this changed source. Do not merge
canonical on build or host results alone.

This candidate deliberately advertises `strict_hardening_candidate`, resource
diagnostics and bounded volatile fault controls. These markers must be true
for the injected rows below. Final production removal or explicit retention of
instrumentation requires a separately reviewed exact source/artifact decision.
No automatic flashing, reset, power interruption or test runner is authorized
by executing a host checker. The owner performs each device action separately.

## Preparation and preservation

1. Record candidate SHA/tree, UF2 byte count/SHA-256 from custody and hash the
   actual file selected for flashing. Record controller identity, date, host,
   USB path and tool versions. Do not use an old build-directory UF2.
2. While the old f7ba82d4 firmware is still available, enter Configurator through
   the already accepted ordinary route. Export Config and all three surviving
   profiles. Retain the original export bytes, decoded JSON, STATUS and paged
   LIST, not just screenshots. Baseline is incarnation as reported, generation
   8, ID1 rev2, ID3 rev1, ID4 rev1, deleted ID2, mode1→3 and mode2→4. Verify
   payloads against the retained prior acceptance exports. Stop on disagreement.
3. Obtain a full flash backup with an owner-operated RP2040 ROM/BOOTSEL backup
   tool if available, without erase or format. Store it separately from the
   candidate. Hash it twice after copying and retain the tool's address/length
   report. This is an emergency preservation image, not permission to roll back
   live identity history after new IDs are issued. If full flash readback is
   unavailable, retain complete logical exports and perform only the
   non-destructive injected matrix; do not perform physical corruption/deletion
   or uncontrolled power cuts.
4. Logical exports preserve useful Config/profile content, but importing them
   through CREATE cannot restore original IDs, revision history or incarnation.
   Therefore they are **not** a sufficient restore procedure for destructive
   root tests. This packet requires no destructive root deletion, factory reset
   or raw Config replacement. If unexpected state damage occurs, stop and
   preserve the device for diagnosis; do not improvise a reset or restore.
5. Owner flashes the exact candidate using the established manual procedure,
   without a filesystem image, erase-all or autoformat option. This run performs
   no flashing. On first boot verify upgrade rows below before creating data.

The candidate tool is `tools/glyph_profile_store_candidate_tool.py`. Inspect its
`--help` offline first. Set `PORT` yourself to the verified controller path.
These example commands are instructions for the later owner session; they were
not executed during preparation:

```sh
python3 tools/glyph_serial_config_tool.py --read --port "$PORT" --backup-out before-config.json
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" status
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" list --page 0
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" read --profile-id 1
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" read --profile-id 3
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" read --profile-id 4
```

For the old v1 firmware use the retained v1 inspection client/export transcript
if it refuses a version-2 request. Never try a write to determine compatibility.
After upgrade, repeat exports with the candidate client. Page until every
reported directory entry is captured. Preserve each request and response as
JSON with timestamps, token and exact source payload hash. For mutations use
explicit expected incarnation, generation and applicable revision/Config CRC.
Read the advertised token high water and choose a strictly greater uint64 token.
Every mutation requires `--request-out` naming a new receipt file; the client
exclusively creates and fsyncs its exact protobuf bytes, SHA-256 and decoded
fields before transmitting. Preserve that file for explicit replay. Do not
refresh expectations on a retry. For example, after assigning the actual
recorded values to these shell variables and exporting a bare profile/READ JSON:

```sh
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" create --token "$TOKEN" --incarnation "$INCARNATION" --store-generation "$GENERATION" --name ACCEPT-01 --rank 100 --profile-json baseline-id3.json --request-out create-01.request.json --output create-01.response.json
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" query --token "$TOKEN"
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" replay --replay-request create-01.request.json --output create-01.replay.json
```

The replay action sends the original bytes once, checks their saved hash and
store incarnation, and intentionally retains old generation/token fields. It
does not apply the new-mutation high-water preflight or retry automatically.
An accepted but uncommitted intent can resolve to TRANSACTION_ABORTED (wire11).
Its token is consumed: exact replay remains ABORTED and changed reuse conflicts;
a later deliberate attempt needs a new token. A proven pre-intent rejection can
remain NOT_FOUND. Never interpret COMMIT_UNKNOWN as either result.


## Upgrade and ordinary operation

| Row | Owner action and required evidence | Stop condition |
|---|---|---|
| U1 | Boot the candidate on the baseline compact store. Record STATUS, Config, all entries and payload bytes. Require same incarnation, generation8, ID1rev2/ID3rev1/ID4rev1, names/ranks/payloads and mode1→3/mode2→4. Config root-format marker becomes2; compact marker remains1 and embedded profile count remains0. | Any identity, payload or reference changes beyond owned marker/receipt metadata. |
| U2 | Ordinary reboot and repeat U1. No repeat migration/new IDs. Create a disposable profile using a saved baseline payload; require ID5 or a higher non-reused ID, never2. Record name, revision and token. | Reused ID, unexpected migration or unqueryable uncertainty. |
| S1 | Select the same persisted destination using its chord, then hold it through an ordinary boot. Observe no repeated reboot. | Reboot loop or active change without reset. |
| S2 | Select a different existing mode/profile destination. Capture Config before/after and observe one reset before the new destination is active. Repeat a non-Ultimate destination. Release the chord before another selection. Restore the original destination through the same checked path. | Hot activation, failed persistence followed by reset, or repeated reset while held. |
| N1 | On disposable IDs test empty/18-byte/32-byte UTF-8 names, maximum rename and duplicate; reboot and compare exact UTF-8 bytes/ranks/IDs. Duplicate must allocate a new ID. | Truncation, malformed-name acceptance, identity change on rename. |
| H1 | LIST plus explicit HEALTH of each useful profile must report healthy without changing active ID/Config/generation. Corrupt/missing/unsupported record cases are covered by host exact-byte fixtures; do not damage useful target records to repeat them. | LIST failure caused by unselected profile payload or inspection activating data. |
| T1 | For each store mutation and SET_MODE_REFERENCE, retain the exact request, deliberately discard its response at the host, QUERY the token, then replay before/after reboot. Require one durable change and stable result. Reuse token with changed payload/metadata/expectation; require conflict/expired refusal. Restore references afterward. | Duplicate execution, false NOT_FOUND, or accepting changed request under reused token. |

Runtime-B raw physical output observation remains NOT_TESTED —
PHYSICAL_RUNTIME_OBSERVER_UNAVAILABLE and non-blocking. These rows do not
substitute menu selection or Config readback for that observer. Nunchuk remains
NOT_TESTED unless the owner explicitly tests and reports it.

## Capacity, reserve and bounded cleanup

Record STATUS total/used/free, erase/program sizes, reserve, protected/staging
bytes, admitted count and feasibility on every capacity step. Expected pinned
partition geometry is 524,288 bytes and 4,096-byte erase blocks; the target
measurement is authoritative. Reserve must report16,384 bytes. Do not call
host geometry a physical measurement.

Using copies of the accepted representative A/B payloads, create disposable
profiles with a distinct `ACCEPT-` name prefix until **20 total live profiles**
are present. Never overwrite useful IDs1/3/4 or alter their references. After
each success capture token/result and STATUS, then READ and hash the new
payload. Reboot and verify all20; no ID reuse or payload loss is acceptable.

If sufficient session time and backup evidence exist, continue to at most64
entries. Count exhaustion must return FULL without publication. To exercise
actual disk admission rather than only the count ceiling, update only
unreferenced disposable IDs with alternating accepted A/B payloads, each with
a new token and current revision. Allow at most128 total successful disposable
updates. Stop at first FULL/reserve refusal. Capture the request and before/after
STATUS: no new revision, authoritative generation or reference may appear on a
definitely rejected operation; reserve must remain intact. If the bound ends
before actual reserve refusal, record that row NOT_TESTED; do not enlarge the
experiment or claim count FULL proved disk-reserve admission.

Cleanup uses DELETE only for the recorded disposable IDs, with fresh tokens
and current generation. Keep original IDs/references unchanged. Verify deleted
IDs are absent and cannot be reused. Retained previous-root garbage may remain
until subsequent bounded collection; this is not a live profile. If cleanup
itself refuses or becomes uncertain, stop and query; do not format. Export the
remaining state and retain the disposable ID/token ledger so later diagnosis
never mistakes test allocations for factory data.

## Candidate-only fault matrix

Fault arming is volatile, one-shot, bounded to an enumerated operation/path class
and at most8 matching calls skipped. It cannot specify arbitrary paths, persist
across reset or cause a reset. An armed rule clears when it fires. STATUS shows
capability, armed/triggered state and operation. `clear` removes an untriggered
rule. Disabled production builds reject the operation.

```sh
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" arm --path-class record --operation sync --result fail-before
# Owner now submits exactly one saved disposable CREATE or UPDATE request.
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" status
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" query --token 0xYOUR_TOKEN
python3 tools/glyph_profile_store_candidate_tool.py --port "$PORT" clear
```

Use actual recorded tokens, not the illustrative placeholder. A rule can fire
on an earlier matching read in admission; inspect its reported trigger and do
not assume it reached a later boundary. `--skip` is only for a source-reviewed
matching-call count, never trial-and-error on useful state.

| Boundary | Bounded action | Required classification/recovery |
|---|---|---|
| Record open/write/sync/close | For each operation arm fail-before, perform one disposable CREATE/UPDATE, query/inspect; then repeat with lost-ack-after. | Definite refusal or explicit uncertainty; no ordinary mutation while unresolved. Query/reboot resolves authoritative state; no duplicate result or changed useful profile. |
| Record rename | Fail-before and lost-ack-after on one disposable record mutation. | Readback/query determines whether root authority exists; orphan record never becomes authority by filename. |
| Control rename | Fail-before and lost-ack-after with skip0 on one disposable mutation. | No acknowledged success until root+ready checkpoint; pending intent fences. After reconciliation an aborted allocation may leave an ID gap, never reuse. |
| Root rename | Fail-before and lost-ack-after on one disposable mutation. | Old-or-new authority with durable high-water reservation; query/replay/reboot never execute twice. |
| Ready checkpoint | Arm control rename with skip1, then one disposable mutation. | Lost final acknowledgement still reconciles the published root/result; no false NOT_FOUND. |
| Config sync/close/rename | Use a reference change between already backed-up IDs3/4, never arbitrary whole Config. Inject before failure and after lost acknowledgement. | No live hot switch. Unresolved Config blocks later mutations. Query reports durable receipt when committed; clear/reboot and restore original reference through a new checked transaction. |
| Root unreadability | First leave a pending control intent through control-rename lost acknowledgement. On the new route-capable candidate only, ARM root/OpenRead/fail-before/skip0, then the explicit `query --reconcile-fault-ticket` route with exact token and exclusive receipt/trace custody. Ordinary QUERY cannot activate a v2 pending rule; see [corrected exact packet](profile_store_root_reconcile_hardware_packet.md). | Explicit unknown/read-only invalid-root state, no allocation. After preserving the one-shot result, ordinary manual reboot with no fault reconciles healthy roots without deleting any root; no CLEAR needed. This models the production read-failure boundary, not physical bit corruption. |
| GC remove | Create/update/delete only disposable data to make unprotected garbage, arm record remove fail-before then after lost acknowledgement on a later disposable mutation. | No protected useful/current/previous revision disappears. Retry resumes bounded collection. Record any no-trigger case honestly. |

Physical power-cut behavior remains a separate physical acceptance row if not
established by these faithful production-boundary injections. This packet
requires no uncontrolled power removal. Host LittleFS fault/reset tests and
these target injected failures must not be relabelled as real power-cut evidence.
Any additional destructive scenario needs an owner-reviewed preservation plan
that maintains monotonic identity; a logical export alone is insufficient.

## Recovery service and resource observations

Manual route: enter RT2 recovery with the normal held-button procedure; MB1
must still take update/bootloader priority. With the display disconnected or
unavailable, record device-info, STATUS, LIST, READ and HEALTH. The store must
be initialized for inspection, not reported empty merely because normal setup
was skipped. All mutations and whole Config SET must be refused in recovery.

Automatic route is source-tested for Config rejection and filesystem failure.
Do not corrupt useful Config to create that state. A physical automatic-route
exercise needs a separately preserved disposable device/image or a bounded
candidate route that does not destroy Config. If unavailable, record automatic
physical entry NOT_TESTED; preserve the source/host PASS separately. Filesystem
unavailable must be distinguishable from Config invalid/root invalid.

Record resource diagnostics after first upgrade boot, ordinary boot and steady
runtime, manual recovery, Config export, each CRUD/reference path,20-profile
LIST/READ, migration if separately available, and fault/reconciliation peaks.
Record core0/core1 minimum unused stack, heap current/peak/capacity, feature
flags and exact artifact identity. The watermark covers each 4 KiB scratch
bank from initialization onward; it cannot prove an earlier boot phase or every
possible IRQ interleaving. `_sbrk` peak measures allocator arena high water, not
live allocation occupancy. Do not replace a missing measurement with a static
linker reservation or with `build fits`.

Stop immediately on zero/implausible stack margin, heap peak at capacity,
reboot/hang/transport loss that cannot be reconciled, filesystem errors, any
useful-profile change, unexpected incarnation/generation rollback, or remaining
armed fault at the end of a row. Clear and re-inspect when safe; otherwise retain
the exact transcript and stop. Do not continue to try to obtain a PASS.

The result receipt must list each row PASS/FAIL/NOT_TESTED with actual evidence,
not an aggregate inferred PASS. B10 and physical resource margins remain open
until that exact-SHA/exact-UF2 receipt is reviewed. This packet itself grants no
canonical merge and contains no newly claimed hardware evidence.

## Root row correction — 2026-10-16

The former instruction “ARM root/open-read fail-before, then ordinary QUERY”
was impossible under fault-control v2. Preserve the failed4ee attempt as
`ROOT_UNREADABILITY_TEST_ROUTE_INVALID_UNDER_FAULT_CONTROL_V2`. Its ordinary
healthy reconciliation to ABORTED is valid behavior, not a product failure.
Ticket8 remained pending/inert, generation164→165, intended receipt revision133;
actual ID22 authority is not inferred from that receipt. Use the separate
[failed-device adjudication](profile_store_root_reconcile_device_adjudication.md)
and [new single-attempt candidate packet](profile_store_root_reconcile_hardware_packet.md).
Older strict procedures remain historical; they do not accept the new candidate.
