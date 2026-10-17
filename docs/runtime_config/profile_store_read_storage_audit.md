# ProfileStore READ storage and encoding control

This source-only control supports the owner-authorized investigation of the
first ID1 READ timeout on `d59684b9368be61183881bdfc82adc774ad5f0ba`.
It performs no device I/O. It does not adjudicate the USB transmission mechanism
or establish physical causality.

## Retained profile and physical boundary

The failed journal contains `transmit_attempt`, `transmitted`, and
`response_timeout` for operation 3. Its request SHA-256 is
`7e71733f90dacaf476e8bc4271809e7aa70413f44b53d95b36ba8cf7b2d389d2`.
The preceding candidate tool did not retain partial bytes or request READ device
stages. Those omissions cannot establish zero device output or a storage hang.

The exact earlier successful physical response is preserved byte-for-byte as
`tools/fixtures/profile_store_read_storage/physical_id1_response.json`, copied
from `responses/post-reset-adjudication-read-id1.json` in the retained October 16
hardware evidence. Its host request hash matches the failed request. The actual
ID1 profile is schema version 1, not a Stage-C profile. Re-encoding its decoded
profile yields 1,960 bytes; the whole retained response yields 1,989 bytes. This
is a reconstruction from retained decoded JSON, not custody of original raw USB
bytes. The report hashes the source evidence and generated binary.

## Real filesystem history and phases

Run:

```sh
python3 tools/check_glyph_profile_store_read_storage.py --output-dir /private/tmp/glyph-read-storage-results
```

The checker imports the existing pinned Arduino-Pico 3.6.3 LittleFS harness's
actual production setup, replacing only its later fault campaign with READs.
It builds both frozen d596 source and current source, with ASAN and UBSAN.
The fixture is a 512-KiB NOR model with 4-KiB erase blocks, 256-byte read/program
and cache units, block cycles 16, real v1-to-v2 upgrade, immutable migration
source, compact Config/current/prior files, and twenty live profiles. It runs
129 successful persisted updates, 43 discarded-result queries/exact replays,
real GC and metadata relocation before the generation-160 checkpoint. ID22 is
revision130; IDs1/3/4 remain immutable. ID1's body is the retained physical v1
profile, while ID3 and representative later records contain accepted Stage-C.
This reproduces the relevant geometry and logical history; it is not a byte
image of the physical controller's filesystem.

Each source control reads IDs1/3/4/22/5/20 one thousand times: 6,000 reads per
source. Checked-storage observers verify completion of both Stat operations,
OpenRead, Read and Close on each operation. Host-copy instrumentation marks
successful checked read/close, record integrity/CRC, Nanopb decode and semantic
validation. The original statements remain in order; the inserts only record
that execution passed their successful exit. Current production trace is also
checked for exact stages 10–18, independently of these host-only phase marks.
Failure of the trace callback is exercised at every stage, including while a
native file is open; all handles and allocations are released, later callbacks
stop, and the subsequent untraced READ succeeds after scope teardown.

Observed source controls: all reads complete, with at most 115 native block
reads per READ. The checkpoint has 955 erase operations and 280 enumeration
passes. No READ writes or erases storage. Native file handles return to zero;
LittleFS retains only its three mount allocations, 768 bytes total, with a
1,024-byte peak. Unmount releases all allocations. This is an allocation oracle
for actual LittleFS; it is not a claim about device-wide heap or IRQ timing.
Host milliseconds are recorded as workload measurements, not RP2040 deadlines.

## Profile-response encode bounds

Actual Nanopb `pb_get_encoded_size`, `pb_encode`, and full `pb_decode` are used,
with exact profile-byte roundtrip comparison and an 8,192-byte output buffer.
The 6,000 READ responses are encoded/decoded per source; each source also runs
1,000 encodes/decodes of each exact retained physical ID1/ID3/ID4/ID22 response
and 1,000 of a
maximal accepted Stage-C profile. The actual semantic validator admits that
maximal body. The ordinary Stage-C profile body is 3,042 bytes; the maximal
accepted Stage-C body is 4,025 bytes, and its minimal READ envelope is 4,038
bytes. The physical full envelope remains 1,989 bytes. Minimal stress envelopes
are explicitly distinguished from retained device envelopes, which include
additional metadata.

The maximal Stage-C construction fills all bounded lists, byte coordinates and
admitted optional fields. Its profile wire budget is:

| Profile field | Bytes |
| --- | ---: |
| Schema version | 2 |
| 28 tables, nine coordinate pairs each | 2,126 |
| 22 roles, full 2/4/9-token conditions | 594 |
| 32 routing slots | 192 |
| Default table ID | 2 |
| 19 rules, full conditions and two-byte priorities | 570 |
| Enabled output program and twelve maximal valid effects | 539 |
| Total | 4,025 |

Each byte coordinate uses its maximal two-byte varint; valid table and token
IDs remain one-byte varints. Unique table IDs include zero once. Every condition
uses all fifteen allowed distinct routed tokens. All rule priorities are at
least128. Eight analogue effects and DPAD use eighteen maximal inline
coordinates; digital masks use two nonoverlapping two-byte masks; trigger bytes,
suppression, valid gates and gate inversion are populated. The fixed semantic
shapes prevent simultaneously adding the alternative coordinate modes.
Schema-v1/v2 omit extensions and cannot exceed this accepted Stage-C budget.
The store independently rejects record payloads above 4,096 bytes.

There is also a deliberately more conservative whole-schema proof:
Nanopb's generated `ProfileStoreResponse_size` bounds *all* statically allocated
fields, including maximum metadata, eight LIST entries and the schema's
unconstrained profile bound. The test uses a compile-time assertion that this
full bound remains below 8,192 bytes. Frozen d596 schema's bound was 6,693;
the additive READ `liveness_value` field makes the current bound 6,700. The
abstract profile bound is 5,740, deliberately above the semantic admission bound.
No response/profile field is a callback or an unbounded repeated field. Each
has a generated static descriptor and explicit bounded count/string extent.
Consequently encoding performs finite descriptor/list traversal into a bounded
buffer; it cannot await filesystem, USB or host progress.

The host response object is 2,992 bytes both before and after the additive
READ field under the test ABI (the new field uses existing layout padding). These are host layout measurements;
use the exact candidate ELF/resource report for RP2040 object sizes and stack
use. The production frame and response object are static. Host stack use in
this sanitizer fixture is not a device stack claim.

## Scope of conclusion

Frozen d596 and current storage/encoding controls pass. No deterministic
storage, record CRC/decode, semantic validation, or protobuf encoding failure
was reproduced on this history. This supports isolating the reproducible
transmission failure, but does not prove that those operations completed on the
failed physical request. The opt-in production READ stages are needed for that
next hardware observation. B1–B8 persistence and transaction code is not changed
by this checker or its fixture.


## Distinct retained READ bodies for the CDC regression

The checker also exports canonical protobuf reconstructions of exact retained
`post-reset-adjudication-read-id3.json`, `read-id4.json`, and `read-id22.json`.
Their byte-exact JSON copies are kept beside the ID1 fixture, with source and
binary hashes in the report. All four full responses pass actual Nanopb
encode/decode and semantic validation one thousand times per source build.
These are physical retained decoded responses, not the reconstructed history's
minimal envelopes. No original raw USB byte custody is claimed.

| Retained response | Profile bytes | Full response bytes | Generation | Revision |
| --- | ---: | ---: | ---: | ---: |
| ID1 | 1,960 | 1,989 | 160 | 2 |
| ID3 | 3,042 | 3,071 | 160 | 1 |
| ID4 | 3,047 | 3,076 | 160 | 1 |
| ID22 | 3,042 | 3,072 | 160 | 130 |

The CDC harness consumes these distinct retained bodies. The long-history
storage stress intentionally uses a simpler two-profile migration fixture:
its ID4 contains the same v1 body as ID1, while its ID3/ID22 and later records
contain the Stage-C A body. That storage model limitation does not apply to
the additional retained-response encoding and CDC controls.
