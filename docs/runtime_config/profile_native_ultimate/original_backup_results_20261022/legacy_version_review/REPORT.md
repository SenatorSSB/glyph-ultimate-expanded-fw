# Finite legacy READ directory/body version adjudication

Disposition: **the exact-equality assertion was an unjustified private host
backup gate, not a source-grounded invalid/unsupported READ result.** The
retained response for ID4 is a supported legacy-class directory/body distinction:
directory `payload_version=1`, actual decoded profile `schema_version=3`.
Preserve both values; do not rewrite, normalize or diagnose their origin.

This finite offline review performs no device request, retry, source/queue change,
or private-backup mutation. Exact F334f/artifact/resource holds remain unchanged.
Only public source excerpts and hash/metadata evidence are written here. Original
profile bodies, received bytes, journals and directory data remain in the private
owner backup directory; do not publish or content-archive those private inputs.

## Source proof and supported-domain boundary

- Accepted `307d72347653c079ec8ec6e9b6ecae3c30ae536c`
  `ProfileStore::ReadProfile` verifies record bounds, incarnation, ID, revision,
  record length, header/payload CRC and supported record framing. It decodes the
  complete UltimateProfile, admits schemas1–3 and calls the existing semantic
  validator. It never receives or compares directory `payload_version`.
- `ProfileStore::Read(id,out,rev)` is byte-identical between accepted307d and
  F334f. It finds the directory entry, calls ReadProfile at that entry's revision,
  returns that revision and OK on success. It does not equate cached directory
  payload metadata with decoded schema. F is at
  `HAL/pico/src/core/ProfileStore.cpp:1096–1149`.
- Accepted307d activation likewise reads the current or retained previous record
  and publishes the validated decoded legacy profile; no metadata/schema equality
  is imposed. F adds its explicit native-versus-legacy class guard at1178–1182:
  `(decoded.schema_version==5)` must equal `(entry.payload_version==5)`.
  It deliberately does **not** add equality between individual legacy versions.
  For the observed1/3 pair, both sides of that class comparison are false.
- Directory structural validation checks identity/revision/name/uniqueness and
  migration dependencies, not individual payload/schema equality. LIST at
  `ConfiguratorBackend.cpp:852–868` copies entry metadata without reading payloads;
  its comment explicitly says enumeration never reads payloads. READ at701–715
  calls the validated store Read and marks a profile present on success.
- `schema/haybox/config.proto:530–548` defines the actual UltimateProfile schema
  and distinct legacy1/2/3 semantics, and581–589 defines separately transmitted
  directory metadata/health. Response comment638 states LIST never reads bodies.
  Neither establishes the private equality assertion. Record-format version1,
  directory payload_version1 and decoded profile schema3 are separate fields;
  they must not be conflated.
- F Update at1599 rejects crossing the native/legacy class. A successful ordinary
  Update sets new directory payload metadata from the new profile at1621.
  That does not establish how this existing historical1/3 pair arose. No UPDATE,
  metadata repair or inference of corruption is justified here.

The existing firmware/source validation must still apply to malformed, corrupt,
unsupported or cross-engine data. This finding resolves only the verified
legacy1–3 class distinction. It does not bless arbitrary directory metadata,
unknown schema versions, malformed fields, invalid CRC, wrong ID/revision or
uncertain response. Rejecting this already admitted legacy distinction merely
to simplify host custody would narrow the supported domain without authority.

## Exact retained evidence replay

The actual retained READ4 tool result reports returncode0, no timeout, and no
retry authorization. The private host assertion stopped later backup processing
after IDs1 and3, rather than the device returning an invalid/unsupported status.
The stop record remains unchanged and is preserved as evidence.

The offline replay reconstructs the single status-preflight and single READ from
their exact journal chunks. Every request/wire/frame/prefix SHA and byte count
matches the retained records. There is one complete READ COBS frame of3088 bytes,
one response, no partial frame, invalid-frame, device-error, EOF or timeout event,
and the complete received protobuf is consumed. It exactly matches the retained
response JSON after parsing with tracked F protobuf descriptors.

Observed READ metadata is PROFILE_STORE_OK/id4/revision1, protocol2 and mutation
protocol2, incarnation1, store generation172 and Config generation1156314366.
Those identity/fence values match both the normal STATUS preflight and the stable
complete22-entry directory. STATUS has no recovery flags and remains mutation
feasible. Schema3 contains no native payload; the existing host classifier
identifies legacy and explicitly delegates full legacy semantic admission to the
firmware. All28 table IDs and their nine-coordinate extents are present.

The latter checks are not relabeled a new independent execution of the C++
semantic validator. Full semantic admission here is supported by the returned
OK response plus the exact accepted/F source paths above. This review establishes
retained transport/JSON fidelity and the disputed version relationship, not
hardware acceptance or cryptographic identification of installed firmware.

The deterministic decoded UltimateProfile wrapper is3047 bytes, SHA256
`b8583459651f42bfbb108e4558627ce0a192be89bae229cbb5a74fb0e7dcd8d4`.
This is reconstructible canonical public-wrapper custody; it is not proof of the
original record's byte encoding or a raw filesystem/history backup. No original
payload bytes are emitted into this report directory.

## Corrected host backup validation and bounded continuation

1. Preserve the original directory entry, complete response JSON, journal, tool
   result and original assertion stop as separate immutable evidence. Require
   actual complete successful READ framing, requested ID, exact listed revision,
   expected protocol/status/token, matching incarnation/store generation/Config
   generation and complete decoded profile. Retain every existing uncertainty,
   recovery, unsupported/error and fence stop condition.
2. Record `directory_payload_version` and `decoded_schema_version` separately.
   For the disputed case, both values in1–3 are the existing legacy class; do
   not require equality between individual legacy versions. This corrects only
   the host equality condition. A schema5/native-versus-legacy disagreement is
   not covered by this correction and must still stop; unknown/unsupported
   versions or malformed content require source-grounded adjudication rather
   than automatic acceptance.
3. Complete ID4's **private offline** custody from the existing retained READ4
   message. Serialize the complete decoded wrapper deterministically, verify the
   hash/length above, roundtrip it, and record both observed versions along with
   source response/journal hashes and unchanged fences. The hash-only proposed
   custody record here supplies those facts. Do not replace directory metadata,
   strip Stage-C fields, re-encode it as schema1, update the device, or reread ID4.
4. The resolved host-only assertion does not consume another READ or require a
   new physical action. Root may continue only the untouched original IDs
   `5–22,24` (19 IDs) through their **first** already-approved READ attempts,
   with each tool's existing STATUS preflight and the unchanged overall
   approval/counter bounds. IDs1,3,4 must not be retried. This is continuation
   under existing owner authority, not a renewed read budget or a new approval.
5. If a later response changes fences, lacks its exact ID/revision/profile,
   refuses, times out, is partial/uncertain, crosses native/legacy class, or raises
   another genuine unsupported-content issue, stop that operation and preserve
   its evidence. This review supplies no fallback access path, retry, recovery,
   mutation, installation or acceptance waiver.

Historical origin remains UNKNOWN and root cause UNPROVEN. The broader owner
accepted filesystem support domain, legacy compatibility, all fixed resource
limits and exact source/artifact custody remain intact. No hardware PASS,
installation, profile/Config write or H1–H12 campaign is granted.
