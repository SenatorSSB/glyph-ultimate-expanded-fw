# ProfileStore additive protocol hardening

Protocol version 2 is required for mutations. Versions 1 and 2 retain read-only
STATUS/LIST/READ/health/query; v1 mutations return explicit UNSUPPORTED. This
necessary version boundary makes the monotonic full-token rule explicit rather
than silently changing an old client's token allocation contract. Operations
1 through 11 retain their wire numbers and meanings. Operation 12,
`PROFILE_STORE_INSPECT_HEALTH`, adds explicit lazy inspection of `profile_id`.
Existing request tags are unchanged; response additions expose capacity,
recovery, resources, and mutation protocol/token capabilities. Old v1 STATUS
bytes remain a checked compatibility fixture. A whole-Config writer cannot
erase or forge firmware-owned reference/migration receipts, and compact-format
legacy-client rejection remains mandatory.

## Request identity and replay

The firmware hashes the ASCII domain `Glyph.ProfileStore.Request.v1` INCLUDING
its terminating NUL, followed by deterministic nanopb encoding of the complete
decoded `ProfileStoreRequest` with `request_token` temporarily zero. SHA-256 is
streamed without a second profile/frame buffer. The full original unsigned
64-bit token is persisted independently alongside all 32 digest bytes.

This is a semantic identity: known fields, scalar defaults, submessage presence,
repeated-field ordering, names, all expectations, operation, ID, rank, mode and
profile payload are bound. Unknown protobuf fields have no firmware semantics
and are discarded during decoding. Different wire ordering or equivalent
protobuf default representations yield the same semantic identity. The caller
cannot provide a digest. Token zero is invalid for a mutation/query.

Protocol-2 clients read `transaction_token_high_water` and allocate a nonzero
unsigned 64-bit token strictly greater than that durable high water (the maximum
of store and Config-reference receipts). Exact retained receipts replay first;
all other tokens at or below the high water conflict before admission. This
prevents a completed token executing again after a later receipt replaces its
bounded detail, including interposed mutations or changed expectations.
A durably accepted intent that is proved not committed records its complete
identity as TRANSACTION_ABORTED (status 11), consumes its token and reserves its
issued ID high water. Exact aborted replay returns ABORTED; changed replay
conflicts. Use a fresh higher token and fresh explicit expectations for a new
attempt. A proved pre-acceptance validation/staged-record failure, before any
intent was published, may report NOT_FOUND: no accepted identity exists.

QUERY of an evicted token at/below the high water returns additive
TRANSACTION_EXPIRED (status 10). A token above high water with no receipt is
NOT_FOUND. UINT64_MAX exhausts mutation tokens and fails closed thereafter.

Store and durable Config-reference receipts are checked before generation
fences. Exact completed requests return their previous result without executing
again, including stale expected generations. Reusing a retained token for a
changed request returns CONFLICT. `QUERY_TRANSACTION` uses the full token and
ignores request generation fields: it checks both the store receipt and durable
Config-reference receipt. Reference receipts are stored inside the same atomic
Config publication as the selected reference. Their result is profile ID,
store generation and mode index; the checked current Config CRC supplies the
response Config generation. The CRC is not a monotonic Config generation.

An uncertain store or Config publication fences all further mutations. Before a
mutation/query, the backend requests authoritative reconciliation. An unreadable
or unresolved publication keeps COMMIT_UNKNOWN and the fence; an unsuccessful
read of Config cannot become a false reference NOT_FOUND. Replay of an already
proved receipt performs no new mutation. The client remains stop-and-wait;
QUERY should resolve a lost response before issuing another mutation.

## Capacity and health fields

STATUS returns measured filesystem total/used/free bytes, erase and program
sizes, configured reserve, protected bytes, staging bytes, derived admitted
profile count and whether a mutation is presently feasible. These are actual
adapter measurements/calculations, not a target-hardware measurement receipt.
The final hardware packet must record the target values independently.

LIST reads directory metadata only. Its entry health is 0 (uninspected), so one
bad payload cannot poison enumeration. Explicit operation 12 returns
`profile_health`: 1 healthy, 2 current damaged with valid retained previous
revision, 3 missing, 4 corrupt, or 5 unsupported. It does not activate a profile
or change persistent state.

`recovery_flags` is a bitset: 0x1 filesystem unavailable, 0x2 root invalid,
0x4 migration fenced, 0x8 store transaction uncertain, 0x10 store read-only,
0x20 legacy upgrade required, 0x10000 Config invalid, 0x20000 filesystem
unavailable at the Configurator layer, 0x40000 Config transaction uncertain,
0x80000 minimal recovery service, and 0x100000 pending durable root-format
marker upgrade. The firmware-owned Config root-format marker 2 prevents
falling back to writable v1 when all v2 metadata is lost. A minimal recovery service permits
STATUS/LIST/READ/health/query and valid Config export only; all mutation paths
and whole-Config SET are refused. Filesystem-unavailable service limits storage
commands to diagnostic STATUS and retains device-info/reboot service.

Names occupy at most 32 UTF-8 bytes plus NUL; bytes are not Unicode character
counts. The store rejects malformed UTF-8 and excessive length before writing.

## Evidence

STATUS also exposes optional resource fields (tags 25–30): core0/core1 minimum
unused stack watermark and heap arena current/peak/capacity. The explicitly marked strict-hardening candidate sets
`resource_diagnostics_enabled` and `strict_hardening_candidate` (tag 33);
compiling without the diagnostic/candidate flags returns false/zero.
Diagnostics cannot compile without the conspicuous candidate flag. Heap arena is the SDK `_sbrk` break bound, not live malloc
occupancy. Host observations do not establish target physical peaks.

`tools/check_glyph_profile_store_request_identity.py` compiles the generated
schema and production helpers, verifies three independent standard SHA-256
vectors, request-field sensitivity, full-token separation, the old caller-digest
negative control, UTF-8 and byte bounds, and a frozen v1 STATUS wire fixture.
`tools/check_glyph_profile_store_strict_protocol.py` compiles the actual backend,
PacketIO, nanopb and ProfileStore with the functional storage/Persistence seams.
Its strict stream scenario covers create replay before/after reload, changed
requests, full names, capabilities, reference replay/query after reconnect,
unknown Config acknowledgement/reconciliation and recovery restrictions.
These are host tests; no device action or physical acceptance is implied.

## Candidate-only bounded storage faults

Operation 13 arms/clears a volatile single-shot hook only when the compiled
strict-hardening marker is true. Ordinary builds return UNSUPPORTED and never
install the hook. STATUS exposes capability, armed, triggered and operation
fields. Arming is limited to a typed kind/operation/phase/path class, with at
most eight matching boundaries skipped. No arbitrary path, persistent arming,
flashing, reset, filesystem deletion command or root removal hook exists.
Before-failure and after-lost-acknowledgement are separate controls. A fired
hook immediately disarms; its triggered bit remains until explicit clear/new
arm. Recovery service refuses arming. The actual callback is installed through
`CheckedStorage::SetFaultHook`, so target faults exercise the production checked
operation boundary rather than a second persistence implementation.

Request fields 14–20 describe kind (1 record, 2 root/control, 3 Config), checked
operation (OpenRead 1, OpenWrite 2, Read 3, Write 4, Seek 5, Sync 6, Close 7,
Stat 8, Remove 9, Rename 10), phase/result (1/1 fail before, 2/2 acknowledgement
loss after), path class (1 immutable profile, 2 alternating v2 root, 3 control
record, 4 compact Config), bounded skip, and explicit clear. Remove faults are
limited to unreferenced-record GC boundaries, never roots/Config. These hooks
are boundary-injection evidence; they do not constitute physical power-cut or
mount/flash corruption evidence. In particular, a read fault is temporary
unavailability and must not be relabelled actual persisted root loss.

The separate `tools/glyph_profile_store_candidate_tool.py` supports bounded
STATUS, paged LIST, READ/export, health, query, candidate-only arm/clear and
explicit owner-invoked CRUD/reference operations. New mutations require the
visible candidate, exact supplied incarnation/generation, a token above the
observed high water, applicable revision/Config CRC, and a new exclusive
`--request-out` receipt file. It writes and syncs exact request bytes, SHA-256
and decoded fields before sending the mutation. Profile-source JSON and
transmitted request hashes are reported. It never refreshes expectations,
retries, flashes, resets, or issues a whole-Config SET. No serial/device action
was run during implementation. Example owner actions, with the actual target
port and observed identities:

```
python3 tools/glyph_profile_store_candidate_tool.py --port PORT status
python3 tools/glyph_profile_store_candidate_tool.py --port PORT arm --path-class record --operation sync --result fail-before
python3 tools/glyph_profile_store_candidate_tool.py --port PORT status
python3 tools/glyph_profile_store_candidate_tool.py --port PORT query --token TOKEN
python3 tools/glyph_profile_store_candidate_tool.py --port PORT clear
```

For logical backup, export Config with the existing read-only tool, then page
LIST and READ every listed ID. Follow each response's `next_page_cursor` until
zero; record name/rank/IDs/revisions/incarnation with each profile body.

```
python3 tools/glyph_serial_config_tool.py --read --port PORT --backup-out controller-config.json
python3 tools/glyph_profile_store_candidate_tool.py --port PORT list --page 0 --output directory-page-0.json
python3 tools/glyph_profile_store_candidate_tool.py --port PORT list --page NEXT_CURSOR --output directory-page-next.json
python3 tools/glyph_profile_store_candidate_tool.py --port PORT read --profile-id ID --output profile-ID.json
```

A bounded new test CREATE from a backed-up READ export has this explicit shape:

```
python3 tools/glyph_profile_store_candidate_tool.py --port PORT create --token TOKEN --store-generation GENERATION --incarnation INCARNATION --name "Acceptance test" --rank RANK --profile-json profile-ID.json --profile-sha256 SOURCE_JSON_SHA256 --request-out create-TOKEN.request.json --output create-TOKEN.response.json
```

UPDATE and DUPLICATE additionally require `--profile-id ID --profile-revision
REVISION`; UPDATE requires the source JSON, DUPLICATE requires name/rank.
RENAME requires ID/name, REORDER ID/rank, DELETE ID, and `set-reference` requires
ID (zero permitted), mode index and Config generation. Every mutation still
requires explicit token/store generation/incarnation and its new request-out.
Each command sends exactly once. Save/inspect the response and stop on failure
before advancing a twenty-profile target-admission sequence.

For a lost response, QUERY first. Exact replay is a separate explicit action:

```
python3 tools/glyph_profile_store_candidate_tool.py --port PORT replay --replay-request create-TOKEN.request.json --output replay-TOKEN.response.json
```

Replay authenticates the receipt's byte hash and decoded fields and requires
the same candidate protocol/store incarnation. It deliberately sends the exact
old bytes without applying fresh-token/current-generation preflight, so stale
expectations can recover the retained result. It never rewrites the original
receipt. ABORTED/EXPIRED are explicit outcomes, not permission for automatic
retry; a new attempt uses a fresh token, fresh observed fences, and a new file.
`tools/check_glyph_profile_store_candidate_tool.py` proves this distinction
offline without opening a serial port.

An arm does not execute the mutation. The approved hardware packet must name
one exact ordinary protocol-2 mutation and expected safe state for each armed
fault. Use a separately exported/backed-up disposable test profile, never an
unbacked selected profile or deletion of useful state. Before/after each test,
record target geometry, reserve, flags, token high water, generations and exact
profile payload/reference metadata. After acknowledgement loss, query the same
token before retrying or issuing another mutation. Stop on unexpected identity,
reference, payload, reserve or unresolved health; preserve diagnostics and do
not format/delete/repair/reset as a workaround. Logical exports are not a claim
that stable IDs/high-water metadata can be recreated through ordinary CREATE.
If an exact raw restore is required, establish an independently source-supported
backup/restore route before running a destructive scenario. This tool provides
no filesystem-destructive scenario or raw restore route.
