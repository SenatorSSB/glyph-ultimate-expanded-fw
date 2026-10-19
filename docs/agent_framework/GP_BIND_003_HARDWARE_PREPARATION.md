# GP-BIND-003 hardware preparation and recovery packet

Protocol: `GP_BIND_RUNTIME_ATTESTATION_HW_V1`  
Classification: `DOCS_CHECKER_ONLY`; source-free preparation.  
Status: `READ_ONLY_PREPARATION_READY`; no controller observations are recorded.

This packet binds read-only enumeration, preservation of the current Config
and ProfileStore state, and recovery materials to the exact GP-BIND-003
candidate. It does not amend the immutable
[`GP_BIND_003_HARDWARE_PROTOCOL.md`](GP_BIND_003_HARDWARE_PROTOCOL.md).
Neither document authorizes flashing, any Config/ProfileStore/profile write,
physical acceptance testing, or source integration/merge. A separate explicit
authorization is required before any of those operations.

## Exact subject and capability

| Field | Bound value |
| --- | --- |
| Work order | `GP-BIND-003` |
| Candidate ref | `codex/gp-bind-003-runtime-attestation` |
| Candidate Git SHA | `307d72347653c079ec8ec6e9b6ecae3c30ae536c` |
| Candidate tree | `56d9622d2e91174be1395a5234097ab6ef1739ac` |
| Canonical base | `bd548dacf453c932b1a88a0684e6e1155080a309` |
| Recorded direct parent | `9482219ffd575f63cf3c863d465afa134cbf0d28` |
| Protocol | `GP_BIND_RUNTIME_ATTESTATION_HW_V1` |
| Candidate UF2 | `local_backups/hardware-artifacts/307d72347653c079ec8ec6e9b6ecae3c30ae536c/83aa255a7843fbc96af37c679e92408808d9de0f004271315f968db73c37747b/firmware.uf2` |
| Candidate UF2 SHA-256 / size | `83aa255a7843fbc96af37c679e92408808d9de0f004271315f968db73c37747b` / `979456` bytes |
| Controller capability | `PARTIAL`: repository/tool access is available; no matching serial/filtered USB device was observed in the capability input. This does not establish all possible device capabilities. |
| Current evidence | No read-only device capture or physical observation is included in this packet. |

The candidate and artifact tuple above is a fixed subject identity, not proof
that the branch, local custody file, or controller currently matches it. Before
any later separately authorized update, freshly resolve the ref and verify
candidate SHA, tree, parent/base ancestry, regular non-symlink artifact path,
size, and SHA-256. Rehash the artifact immediately before use. Any mismatch,
unavailable custody, or ambiguous identity stops the operation; do not rebuild
or substitute an artifact.

## Physical connection boundary

The known capability gap is the absent matching serial/filtered USB endpoint.
If the controller is not already connected, the sole owner action needed to
enable this read-only preparation is: connect the controller to the host using
its ordinary data USB cable while leaving its current state intact. Do not
press buttons, enter a mode, reset, power-cycle, unplug/replug an already
enumerated device, or initiate bootloader/recovery mode. If the controller is
already connected, no owner action is needed.

After that connection, the terminal operator may perform only ordinary host
USB/serial inventory and the read operations below. Record the host, timestamp,
endpoint, USB identity as observed, controller model/revision only if supplied
or visibly read, and current backend/profile context only where observable.
Label unavailable fields `UNAVAILABLE`; do not infer firmware identity from a
port name, USB identity, stored Config, or historical capture. If no unique
ordinary endpoint is available, stop without probing via reset, 1200-baud
reconnect, bootloader, or any write-capable command.

## Read-only capture order

Use a new, unique, owner-held evidence directory outside Git for the session.
Keep original logs and prior captures immutable. Record the exact host-tool
version/revision and repository commit used. Use one request at a time, a
maximum 10-second response timeout, and stop at the first missing, malformed,
ambiguous, or unexpected response. Never retry an operation after an uncertain
response; retain the partial journal and report it.

1. Capture Configurator device information if the existing read path exposes
   it, then read persisted Config through the existing
   `tools/glyph_serial_config_tool.py --read --port <PORT> --backup-out
   <NEW_DIR>/config-backup.json` route. Do not pass `--write`.
2. Preserve `config-backup.json` byte-for-byte. Decode its
   `rawConfigPayloadBase64` field to `config.raw.bin`; record byte length and
   SHA-256 of those decoded raw protobuf `Config` message bytes (excluding
   command and COBS framing). Preserve the decoded JSON as a convenience copy,
   not as the authoritative restoration source. Re-encode the decoded Config
   with the tracked schema/tool and require byte-for-byte equality with
   `config.raw.bin`. Record the command output, tool/schema identity, hashes,
   and decode/re-encode comparison. `GET_CONFIG` is persisted Config evidence;
   it does not establish live RAM or the active Ultimate object.
3. Capture ProfileStore `STATUS` with the production tool. The concrete
   invocations below show the required distinct files; each file must be new
   and the tool refuses journal overwrite:

   ```sh
   python3 tools/glyph_profile_store_production_tool.py --port "$PORT" --timeout 10 --journal-out "$SESSION_DIR/profile-status.jsonl" status --output "$SESSION_DIR/profile-status.json"
   python3 tools/glyph_profile_store_production_tool.py --port "$PORT" --timeout 10 --journal-out "$SESSION_DIR/profile-list-000.jsonl" list --page 0 --page-size 8 --output "$SESSION_DIR/profile-list-000.json"
   ```

   Preserve the complete request/response journal and decoded response.
   Record protocol/status, store incarnation, generation, transaction-token
   high-water, and any recovery flags exactly as returned. Do not assume a
   baseline from another controller or session.
4. Capture every page of `LIST`, beginning at cursor 0 and following the
   returned cursor until the response says there are no further records. Use
   distinct, newly created output and journal files for every page (for
   example `profile-list-001.json[l]` for the next page). Preserve exact page
   responses and combine IDs only after checking pages do not overlap or omit
   an advertised continuation.
5. For every stable profile ID returned by LIST, issue one read-only `READ`
   with the production tool and separate new journal/output files, using this
   invocation shape:

   ```sh
   python3 tools/glyph_profile_store_production_tool.py --port "$PORT" --timeout 10 --journal-out "$SESSION_DIR/profile-<ID>-read.jsonl" read --profile-id <ID> --output "$SESSION_DIR/profile-<ID>-read.json"
   ```

   Replace `<ID>` with one decimal ID from the verified LIST; run one command
   per ID. Preserve
   the complete exact TX/RX journal, decoded response JSON, returned profile
   ID/revision/name/rank/payload, raw response-frame bytes and their hashes.
   Also record a canonical payload digest only by deterministic serialization
   of the returned `UltimateProfile` submessage with the tracked descriptor;
   never hash JSON as a substitute. Hash each saved file and record its size.
   Compare the READ identity/revision with the corresponding LIST entry and
   retain the original unmodified files. The approved READ surface returns a
   decoded profile response; it does not expose underlying LittleFS record
   bytes, so do not describe this capture as a raw flash/filesystem image.
6. Re-read STATUS and GET_CONFIG once after enumeration. Require unchanged
   Config raw bytes/hash, store incarnation/generation and profile ID/revision
   inventory. Record any allowed observational counters separately; do not
   interpret changes to volatile diagnostic counters as persistent data
   changes. A changed identity or persistent value stops preparation.

The approved ProfileStore production operator exposes only STATUS, LIST,
READ, and its separately gated CREATE/UPDATE actions. This packet uses only
STATUS/LIST/READ. Do not use the candidate/fault tool, QUERY, pulse, health,
fault controls, mutation actions, or any other operation for this preparation.
The Configurator route is read-only `GET_DEVICE_INFO`/`GET_CONFIG` only.

### Required capture manifest

Record a manifest containing at least:

- session ID, UTC timestamps, operator/tool identities, host and observed port;
- all exact candidate/protocol fields above, copied from the protocol without
  resolving unknown values by guess;
- controller model/revision and backend context with the observation source,
  or an explicit `UNAVAILABLE` value;
- Config raw payload path, byte length, SHA-256, base64-wrapper path/hash,
  decoded JSON path/hash, tracked schema identity, and deterministic
  decode/re-encode byte-equality result;
- ProfileStore STATUS request/response journal and decoded-output paths/hashes,
  incarnation, generation, and token high-water;
- all LIST page journals/output paths/hashes, advertised cursors, and complete
  stable-ID inventory;
- one READ journal/output path/hash per listed profile, exact response
  framing bytes/hash, returned ID/revision, deterministic `UltimateProfile`
  payload size/hash, and the LIST-to-READ identity comparison; explicitly
  mark raw LittleFS record bytes unavailable through this surface;
- final STATUS/GET_CONFIG paths and hashes, pre/post equality results, and all
  anomalies or unavailable observations.

The evidence directory is not Git source, candidate input, or hardware PASS
evidence. It must not contain serial credentials or unrelated personal device
identifiers.

## Recovery and restoration materials

The primary restoration materials are the exact pre-session
`config.raw.bin`, its base64 backup wrapper, decoded Config display copy,
ProfileStore STATUS/LIST snapshots, and the complete per-profile READ capture
set. Preserve all files read-only after hashing; store a second independent
copy under the owner-held backup location and read it back, comparing each
file's size and SHA-256 to the session copy. If a second copy cannot be
verified, record that fact and stop before any later state-changing handoff.

The applicable known-good firmware rollback identity recorded by the current
GP-CONFIG-021/022/023 handoffs is accepted GP-CONFIG-017:

- Candidate F: `5994f1657e45e0883c6c75468a19be7e3b49a72c`
- UF2 SHA-256: `e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5`
- Size: `796672` bytes
- Locator: `local_backups/hardware-artifacts/5994f1657e45e0883c6c75468a19be7e3b49a72c/e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5/firmware.uf2`

This is a documented rollback identity only. Its current custody availability
and integrity have not been verified by this packet. If a future operation is
separately approved, verify this exact rollback artifact as a regular
non-symlink file, rehash it, and verify size immediately before any use. If
unavailable or mismatched, stop; do not substitute another firmware.

No Config or ProfileStore restoration request is created or sent here. A
future Config restore requires separate explicit authorization, a fresh
current-state GET_CONFIG comparison, and a guarded existing raw-payload
Configurator restoration path (for example,
`tools/gp_config_010_recovery_operator.py` only when its exact-target guards
admit the operation) that sends the exact captured `config.raw.bin` bytes and
verifies CMD_SUCCESS plus immediate and post-reboot byte-exact GET_CONFIG
readback. JSON reconstruction is not acceptable. A future
ProfileStore restore/update requires its own explicit authorization and
reviewed request plan bound to the then-current store incarnation, generation,
profile revision, and a new token above the observed high-water. Never roll
transaction metadata backwards. Since an UPDATE changes revision/generation,
semantic restoration is not byte-for-byte restoration of the prior store
history. If an operation response is uncertain, do not retry or issue a
restoration write; preserve journals and seek an independently authorized
recovery decision.

## Write-ready and action guards

This packet makes the following conditions prerequisites for any future
separately authorized state-changing work. Passing them does not itself grant
that authorization:

- exact candidate/ref/tree/parent/base and candidate UF2 custody all match the
  frozen protocol; candidate and rollback artifacts are rehashed immediately
  before any manual update;
- a unique ordinary endpoint and current controller/session context are
  observed; backups and independent readback copies are complete and verified;
- raw Config deterministic roundtrip is byte-exact; STATUS/LIST/READ snapshots
  are complete and internally consistent; persistent state is stable across
  the final read-only reread;
- the operator has a separately approved action-specific packet that names
  the exact allowed operation and recovery route; no write is inferred from
  this read-only preparation;
- one action is issued at a time with durable request/response/journal
  evidence; uncertain completion stops without retry, fallback write, reset,
  or cleanup.

For the current GP-BIND-003 acceptance protocol, the eventual query tests
remain read-only, but flashing the candidate itself is explicitly outside this
packet and needs the separately approved manual update step required by the
protocol. No GP-BIND-003 physical row is run or classified here. No candidate
source is integrated or merged. Historical GP-BIND-001/002 results remain
unchanged; H4 runtime identity and X1 root cause remain `UNKNOWN`/`UNPROVEN`;
Nunchuk remains `NOT_TESTED`.
