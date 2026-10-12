# Multi-Profile Persistent Ultimate Profile Store

Status: `DESIGN_FROZEN` — implementation is authorized only within this
document's stated boundary and remains subject to candidate review, build,
artifact custody, and exact hardware acceptance.

Frozen against `origin/configurator` commit
`6b73a7c507f35c111745c6bdd341618b490cbdcd`, tree
`cd14b8f1e688dcc8b1ff561779376531ea47e1b1`, after W1's bounded adversarial
challenge and W3's bounded independent design review. The W3 migration-receipt
retention/fence repair is incorporated below; no review-of-review is implied.

## Purpose and constraints

This is the bounded storage evolution authorized for the post-C024 chapter. It
preserves the existing Ultimate v1/v2/v3 profile evaluator and its Stage A/B/C
behavior. It does not implement profile-defined controller-function bindings,
runtime hot switching, game semantics, arbitrary scripting, or a generic
`RuntimeConfigView` publication path.

The target is at least 20 separately stored Ultimate profiles. Twenty is an
admission target, not an architectural maximum. The implementation must measure
the real admitted limit using the final filesystem geometry, record size,
transaction reserve, and RAM/build data.

## Current evidence informing the design

- The current two embedded profiles scale each complete `Config`: documented
  `sizeof(UltimateProfile) = 2,152` and `sizeof(Config) = 31,224` bytes.
  Boot load and Configurator SET each also use a static `Config` candidate.
  (`docs/CURRENT_STATE.md`; `Persistence.cpp`; `ConfiguratorBackend.cpp`.)
- `board_build.filesystem_size = 0.5m` requests a nominal 512 KiB filesystem
  partition. Actual usable capacity remains to be measured on the target
  dependency/build. (`platformio.ini`.)
- Representative v3 fixture records encode to 3,042 and 3,047 bytes. W4's
  payload-only estimates are 60,840 / 97,344 / 194,688 bytes for 20 / 32 / 64
  profiles. These exclude all metadata, copy-on-write, reserve, and filesystem
  overhead and are not maxima.
- Existing `SaveConfig` overwrites `config.bin` through `w+`; it establishes no
  old-or-new power-loss guarantee. (`HAL/pico/src/core/Persistence.cpp`.)

## Frozen decisions proposed for review

### 1. Store boundary and RAM ownership

`ProfileStore` is the sole owner of Ultimate-profile persistence and shares the
existing mounted LittleFS instance with controller-Config persistence. It has
one long-lived materialized `UltimateProfile active_profile` and one bounded
`UltimateProfile candidate_profile`. It does not allocate or cache all stored
profile bodies in a runtime `Config`, by mode, or during enumeration.

`Ultimate` receives only a pointer to `active_profile` or the established
source-owned/null fallback. It never points into candidate/staging storage. All
load/decode/CRC/status logic occurs before boot publication; the output hot path
uses only stable materialized data.

### 2. Independent identity, metadata, and payloads

The store uses a nonzero monotonically allocated `uint32` `profile_id`; IDs are
never reused within a store incarnation. Identity is `(store_incarnation,
profile_id)`. Zero remains the source-owned Ultimate fallback, not a stored
profile. Names and display ranks are directory metadata; they never determine
identity, evaluator order, or a filesystem path. Rename/reorder changes only
directory metadata. Duplicate makes a new ID.

Each stored payload is a fully materialized existing `UltimateProfile` protobuf
with its accepted schema version. Its record envelope has magic, envelope
version, store incarnation, ID, revision, payload kind/version, explicit
length, and checksum over identity plus bytes. It uses portable fixed-width
fields/byte order—never native struct serialization. Unsupported executable
payload versions fail closed; a later function-binding payload is a different
payload kind/version, not a reinterpretation of current v3 bytes.

### 3. Directory and atomic publication

The store namespace contains two alternating checksummed directory snapshots
and immutable per-profile revisions. A directory records generation, store
incarnation, ID high-water mark, and bounded entries containing ID, current
revision, optional retained previous revision, payload version, name, and
display rank. Directory validation is structural and does not eagerly validate
every payload: a corrupt unselected record cannot poison enumeration or main
Config validity.

Root selection chooses only the highest fully valid, supported committed
generation for the expected store incarnation. Equal generations with different
content, generation ambiguity, unsupported roots, or an incarnation mismatch
are conflicts, not an empty/older writable store. If the newest root is damaged,
the preceding valid root is diagnostic/read-only: mutation and ID allocation
remain disabled until an explicit repair establishes a safe high-water mark or
creates a new incarnation with explicit reference remapping. Both-invalid roots
never autoactivate scanned orphans. This prevents recovery rollback from
reusing an ID already referenced by a compact Config.

For a profile mutation, the store validates the candidate, writes a new
immutable revision, verifies it after checked persistence operations, then
publishes a complete next directory only by replacing the older directory root.
The verified directory-root replacement is the commit point. Old/current roots,
each referenced previous revision, and migration dependencies are GC-protected.
Interrupted precommit records are orphans and never activate merely by existing.
Post-commit uncertainty returns an explicit unknown-outcome result identified by
operation/revision; clients query before retrying.

Each directory commit also records one bounded last-operation token, request
digest, and result identity. Strict stop-and-wait forbids a subsequent mutation
until that outcome is resolved; token reuse with a different request fails.
`QUERY_TRANSACTION` reports the committed ID/revision/generation or an explicit
not-found/expired/unknown status without allocating. A Config-reference commit
has an equivalent result identity.

The implementation must use a checked adapter for the same mounted LittleFS
instance or prove an equivalent primitive whose write, sync, close, rename and
readback outcomes are visible. The present Arduino `File` wrapper is not
sufficient evidence by itself. Every Config writer must use the corresponding
checked Config-replacement primitive; this is required for selected-reference
and main-Config survival, not a generic persistence redesign.

### 4. Compact Config and per-mode references

The new compact Config stores no full Ultimate-profile array. It stores a
format marker, the store incarnation, and a full-width stable profile reference
for each Ultimate `GameModeConfig`. Existing per-mode selection behavior is
preserved; there is no competing global active-profile setting. Profile
selection updates one mode reference, commits it atomically, and takes effect
at the existing reboot/reset boundary. A mode chord that would require a
different effective profile identity (including zero/baseline) first validates
and persists its destination mode/backend through that same checked Config
transaction, then takes that boundary; it never reloads the active object
mid-report. A failed persistence attempt never resets. The one-shot reboot
target is consumed on boot and cannot loop while a chord remains held.

The legacy array/index fields retain their legacy meaning only in a dedicated
streaming migration decoder. New fields use new wire tags and do not reinterpret
the one-based legacy index. A legacy client must receive explicit unsupported
protocol for mutations rather than silently dropping store fields through an
old whole-Config SET.

### 5. Boot, fallback, and recovery

Boot validates the compact controller Config privately, determines the selected
mode, then resolves the selected record into `candidate_profile`, fully validates
it, and copies it into `active_profile` before normal gameplay. It does not scan
or materialize every record.

A missing, corrupt, unsupported, or invalid selected profile preserves the
requested reference and reports its diagnostic. Boot may use only that record's
explicit retained prior revision; otherwise it uses the source-owned Ultimate
fallback. It never silently chooses a neighbor or first valid profile. One bad
record or directory must not invalidate unrelated records or the main Config.

Recovery/Configurator access is a trusted minimal route independent of a
selected stored profile, display success, or ordinary gameplay initialization.
It is an explicit recovery state with a bounded Configurator service loop and
no gameplay output, entered on compact-Config/mount rejection or through an
early source-owned manual hold before persisted selection. Configurator
selection bypasses profile resolution; the recovery route does not depend on
the display/core1/menu loop. Filesystem failure limits commands to diagnostic
and non-storage recovery operations; a record-only failure permits bounded
store inspection/repair. It does not autoformat, delete, reset, or save
defaults after a failure.

### 6. Migration

Legacy `config.bin` is treated as immutable input. A bounded streaming legacy
decoder imports each legacy embedded profile through the one candidate buffer,
retains at most two old-index-to-new-ID mappings, and preserves all accepted
v1/v2/v3 body semantics. The first directory transaction exposing imported
records contains the legacy payload digest, input identity, migration version,
and complete old-index-to-new-ID mapping; this is the sole authoritative,
idempotent receipt. It then writes and validates a new compact Config under a
distinct name; publication of that new Config is migration's commit point. On
retry, the receipt and referenced immutable records are revalidated and the
same IDs are reused. The legacy file remains byte-exact for explicit
rollback/export; imported-profile correspondence is semantic, not a claim that
protobuf re-encoding preserves raw field ordering or unknown fields.

The receipt establishes a durable migration phase keyed by the exact legacy
identity/digest. Every successor directory root retains that receipt and its
imported immutable dependencies; the new compact Config records the matching
receipt identity before it is usable. Until compact-Config publication and its
referenced records are verified, unrelated CRUD, directory repair/rotation, and
GC are fenced. Recovery may only inspect, complete the authenticated migration,
or stop without allocating/re-importing. If the receipt cannot be authenticated,
the system remains in recovery with no fresh ID allocation. The receipt remains
reachable for the compact Config's lifetime while the retained legacy input can
be used for retry/rollback; a later explicit archival policy is outside this
chapter.

If a new-format Config is unreadable, it is not presumed absent and must not
cause a legacy overwrite. Conflicting versions, incarnation mismatch, full
storage, or an incomplete/invalid migration stop in recovery without deletion.

### 7. CRUD and protocol

Keep command-byte/COBS transport but add negotiated, versioned profile-store
operations: capability/status; paged enumeration; read/export; create/import;
update; duplicate; rename; delete; reorder; per-mode reference update; and
validation/health inspection. Each mutation is stop-and-wait and checks expected
directory/profile/Config generation as applicable. It returns explicit
validation, conflict, reference, full, I/O, and unknown-commit outcomes.

One bounded profile is transferred into candidate storage per operation. Device
and host enforce finite length/time limits before persistence. If measured link
limits demand chunking, an explicit begin/chunk/commit/abort protocol is
required before implementation; no second full receive buffer is introduced.
`GET_CONFIG` alone is not a complete store backup.

Delete refuses a referenced ID, including the selected one. The client must
first explicitly select another valid ID or zero, commit/reboot, and then delete.
No delete retargets references silently.

## Required resource and correctness evidence

Before an implementation candidate can proceed, it must prove:

- at least 20 representative complete v3 records can coexist with the required
  directory roots, the full GC-protected union of revisions referenced by both
  roots, a temporary write, compact Config/migration backups, and filesystem
  reserve;
- active plus candidate profile RAM, directory metadata, protocol buffers, boot
  peak, and both-target ABI/map resource data remain within measured limits;
- interrupted-write/fault tests cover record write/sync/close/rename, directory
  publication/readback, Config publication, migration, and GC;
- one corrupt unselected record, corrupt/missing selected record, invalid roots,
  full storage, unknown commit result, and Configurator recovery all preserve
  defined known-good states;
- migration is idempotent, preserves the legacy file byte-exactly, preserves
  decoded v1/v2/v3 semantics and mode mapping, and
- migration fault/interleaving tests cover receipt publication, compact-Config
  failure, attempted root rotation/CRUD/GC, reboot retry, and identical mapping
  with no duplicate IDs; and
- actual decoded stored/migrated profile behavior corresponds to the existing
  frozen Stage A/B/C oracles without regenerating those oracles from changed
  production code.

## Deferred by this design

Profile-defined controller-function bindings; generic runtime-profile
publication; hot profile switching; macros/timing/turbo/scripts; cloud
identity; Senscope UI; public release; Nunchuk; and LS-to-D-pad observability.
Game semantics remain Senscope-owned.

## Frozen Amendment A — recovery, protocol, and deterministic test seams

This amendment resolves the implementation choices identified after the first
W2 checkpoint. It is part of the frozen architecture.

### Recovery entry

At the first existing startup matrix sample, after the existing MB1 bootloader
priority check and before any persisted-Config load, a held `BTN_RT2` enters
the minimal Recovery Configurator state. This reuses the current source-owned
Configurator activation binding and introduces no new physical control, timing
window, debounce policy, or gameplay mapping. A compact-Config mount/load
failure also enters this state. It initializes only the USB Configurator
transport/service loop and source-owned diagnostics: it neither initializes a
gameplay backend nor depends on display/core1/menu initialization. The loop
serves device info, recovery status, store inspection/repair when the filesystem
is usable, and the negotiated profile-store protocol. MB1 remains the first and
exclusive bootloader path.

### Profile-store protocol v1

`CMD_PROFILE_STORE = 9` is a single COBS-delimited request/response command.
For a syntactically decodable request, both response and error use command 9
with `ProfileStoreResponse`; malformed framing or protobuf is the existing
`CMD_ERROR` path. `protocol_version` must equal 1.

The tracked schema adds these exact v1 message fields; fields not listed are
reserved and must not acquire alternative meanings in this chapter:

```
enum ProfileStoreOperation {
  PROFILE_STORE_STATUS = 1;
  PROFILE_STORE_LIST = 2;
  PROFILE_STORE_READ = 3;
  PROFILE_STORE_CREATE = 4;
  PROFILE_STORE_UPDATE = 5;
  PROFILE_STORE_DUPLICATE = 6;
  PROFILE_STORE_RENAME = 7;
  PROFILE_STORE_REORDER = 8;
  PROFILE_STORE_DELETE = 9;
  PROFILE_STORE_SET_MODE_REFERENCE = 10;
  PROFILE_STORE_QUERY_TRANSACTION = 11;
}
message ProfileStoreRequest {
  uint32 protocol_version = 1;
  uint64 request_token = 2;
  ProfileStoreOperation operation = 3;
  uint64 expected_store_generation = 4;
  uint32 profile_id = 5;
  uint64 expected_profile_revision = 6;
  uint32 page_cursor = 7;
  uint32 page_size = 8;
  string name = 9;
  uint32 display_rank = 10;
  UltimateProfile profile = 11;
  uint32 mode_config_index = 12;
  uint64 expected_config_generation = 13;
}
message ProfileStoreResponse {
  uint32 protocol_version = 1;
  uint64 request_token = 2;
  ProfileStoreStatus status = 3;
  uint64 store_generation = 4;
  uint32 profile_id = 5;
  uint64 profile_revision = 6;
  uint32 next_page_cursor = 7;
  repeated ProfileStoreEntry entries = 8;
  UltimateProfile profile = 9;
  uint64 config_generation = 10;
  string diagnostic = 11;
}
```

`ProfileStoreStatus` covers `OK`, `INVALID`, `UNSUPPORTED`, `NOT_FOUND`,
`REFERENCED`, `CONFLICT`, `FULL`, `IO_FAILURE`, and `COMMIT_UNKNOWN`.
`ProfileStoreEntry` contains only identity/revision/name/rank/payload-version
and health; it never embeds a profile body. Nanopb bounds: name at 32 UTF-8
bytes plus terminator, diagnostic at 96 bytes plus terminator, and list response
at 8 entries. A request body, response body, and decoded COBS frame are each
bounded at 8192 bytes; the device aborts an incomplete frame after five seconds
of no input. One whole profile fits in this v1 protocol. Chunking is expressly
not implemented: a profile that cannot fit is rejected as `FULL`/`INVALID`
without persistent mutation, and a later protocol version must define explicit
begin/chunk/commit/abort semantics before supporting it. The host uses the same
limits and stop-and-wait token/query semantics.

### Persistence fault seam and admission evidence

`ProfileStore` receives a narrow storage adapter with production operations
`write`, `sync`, `close`, `rename`, `remove`, `open/read`, capacity query, and
free-space query. Its Pico implementation wraps the same mounted LittleFS
instance and returns every observable operation outcome; it creates no second
mount. Host tests use a deterministic in-memory adapter that can fail exactly
before or after each named operation, including a committed rename followed by
lost acknowledgement. This is a test seam, not an alternate production storage
format or runtime fallback.

The capacity query reports total and free filesystem bytes from the mounted
filesystem. Admission reserves the full GC-protected union, staged record,
directory root, compact Config/migration state, and a fixed 16 KiB filesystem
reserve; it rejects a mutation before deleting any known-good data. The test
adapter is configured to the requested nominal 512 KiB partition and must prove
admission, enumeration, and switching of 20 representative v3 profiles with
that reserve. Firmware capabilities report measured total/free/reserved bytes
and the derived admission count. Target-device filesystem geometry and
interruption behavior remain required candidate/hardware evidence; the test
adapter does not claim them.
