# Strict hardening candidate design

Status: implementation candidate; new hardware acceptance is required. This is
an implementation supplement to the frozen multi-profile design, not a change
to its requirements. Owner authority is the 2026-10-15 strict-hardening request.
Base is `04d7521fbdaeb313c1fe768a992a6c35847b68bf`; the previously tested firmware
is `f7ba82d4cbe79d4353e8d87b7d1b24be3fc15113`. Its receipts and F1–F6 remain
historical evidence. Runtime-B physical output observation remains NOT_TESTED —
PHYSICAL_RUNTIME_OBSERVER_UNAVAILABLE, non-blocking observer debt.

## Shared persistent invariants

The implementation uses two explicit version-2 directory roots and one
format-owned control record. It retains the deployed version-1 record envelope
and the compact Config format marker 1. Persistent integers are little endian;
no native C++ object, pointer, alignment padding, or whole Config memory image
is persisted as an identity. CRC detects accidental corruption; SHA-256 binds
content. These are integrity checks, not signatures against a malicious writer
with arbitrary flash access.

A v2 root is 3,908 bytes: a 320-byte header, 64 entries of 56 bytes, and a
4-byte CRC. Each entry preserves ID, current/previous revisions, payload
version, rank and 32 name bytes plus NUL. The header carries incarnation,
generation, high-water ID, full 64-bit transaction token, firmware-computed
request SHA-256/result, and migration source/mapping/dependency/compact receipt
identities. The 3,924-byte control record contains a phase and a full validated
root checkpoint. Its checksum covers phase, length and root bytes.

Control phases are bootstrap, ready and pending intent. New initialization or
v1 upgrade publishes bootstrap control, both identical seed roots, then ready
control. A normal directory change publishes pending intent first, the next
root second, and ready control last. Success is returned only after all three
checked publications. Missing control with any v2 authority never enables v1
fallback. A firmware-owned Config field independently records accepted root
format 2 before ordinary mutations are serviced. Losing all v2 files cannot
resurrect retained v1 roots when that marker survives. Legacy empty Configs are
converted through checked compact publication before store mutations are enabled. Missing or incompatible roots never enable allocation.

A ready checkpoint must exactly match the selected root, including generation
and high-water history. Therefore replacing both roots with an older pair is
detected. A pending intent can reconcile to the committed new root, or—if both
healthy roots prove the preceding state—to an identity-only abort checkpoint
that reserves the intended high-water ID and retains the accepted token/digest
with an explicit ABORTED result without claiming the mutation succeeded. Exact
replay returns ABORTED; changed content under that token conflicts. Migration
maintenance without a new token preserves the previous successful receipt.
Validation rejection or a record failure before durable intent acceptance has
no accepted identity; checked ready-state reconciliation can prove NOT_FOUND. An unresolved case remains fenced. Orphan filenames never create
authority. No accepted recovery allocates an issued ID again in that incarnation.

These guarantees assume surviving format-owned evidence. Arbitrary restoration
of an entire older flash image, including Config, both roots and the control,
cannot be detected without an external monotonic authority. The hardware packet
must not use whole-image rollback after issuing new stable IDs as a normal
recovery procedure.

## Upgrade of the existing device

The explicit v1 reader validates both 2,620-byte old roots and all current,
previous and migration-dependent records before publishing v2 bootstrap intent.
The real logical fixture has generation 7 pending migration and generation 8
completed migration, incarnation unchanged, high-water 4, ID1 revision 2, ID3
revision 1, ID4 revision 1, deleted ID2, and mode references 1→3 and 2→4.
Both source roots are retained. The generation-8 state is copied without
renumbering, re-encoding record payloads, changing names/ranks or changing
references. An interruption resumes from bootstrap control; it never permits
writable downgrade. A lone v1 root or highest pending old migration is
inspection-only because safe identity/migration completion is not established.

Old completed migration is represented with provenance version 3: SHA-256 of
the accepted old root plus its retained imported record identities. This
preserves and validates existing state; it does not retroactively assert that
the old migration authenticated its original raw legacy Config. A missing
new owned receipt in the existing compact Config is added by checked save.
New legacy migrations use receipt version 2 and exact persisted-source hashing.

## Checked persistence

`CheckedStorage` accesses the existing Arduino-Pico 3.6.3 LittleFS implementation
and native `lfs_t` using a checked, source-pinned protected-member access shim.
It does not mount another filesystem. It retains that mount's existing block
callbacks, including flash interrupt/core1 pause protection. It calls and
checks native open/write/read/sync/close/stat/remove/rename results. The Stream
bridge exists only for the established streaming protobuf/CRC paths.

Publication writes a temporary file, checks sync and close, independently reads
back and compares every byte, then atomically replaces the destination with
LittleFS rename. There is no remove-destination gap. Before-operation failures
can prove no operation occurred. A raw mutating error or lost acknowledgement
is classified uncertain. Uncertainty fences subsequent changes until durable
state is reconciled. Record/root and Config paths preserve separate context
and checked result classification. Host tests execute the production adapter
against the pinned LittleFS C implementation, including a real failing sync
callback as a negative control for the old ignored-close behavior.

## Capacity and collection

The production geometry comes from the same mounted `lfs_config` and
`lfs_fs_size`, including total blocks, allocated blocks, erase/program/read
sizes and cache/name bounds. Used/free reflect allocated blocks, not a sum of
logical file lengths. Reserve is 16,384 bytes.

Protected content is the deduplicated union of both roots' current and previous
record revisions, migration dependencies and the exact active revision. Fixed
charges include control/two v2 roots, retained old roots, existing Config
current/previous/legacy and immutable migration source. Conservative block
charges include CTZ pointer allowance and metadata pairs. Staging includes the
requested record(s), root/control copy-on-write, an 8,192-byte Config body plus
header, and metadata copy-on-write. Both actual free-space and protected-total
bounds must retain reserve before CREATE, UPDATE, DUPLICATE or migration writes.
STATUS reports the inputs, protected/staging/reserve amounts and admission.

Collection examines only precisely shaped immutable record/temp names. It never
removes a protected revision, root, Config, receipt or foreign file. It is
forbidden while migration/transaction authority is unresolved or recovery is
read-only. Up to 128 garbage removals occur per call; exhaustion refuses the
mutation and a retry resumes safely. A failed removal changes no logical
authority. Tests cover every destructive boundary and retry.

The host target-geometry test executes the real production storage adapter on
128 × 4,096-byte pinned LittleFS blocks. It creates 20 representative profiles
and checks block-accounted free space/reserve. The 64-entry limit is a metadata
ceiling, not a promise that 64 arbitrary payloads fit. Physical values and
allocator behavior still require the exact candidate hardware packet.

## Transactions, selection and recovery

See `profile_store_protocol_hardening.md` for canonical request digest domain,
full tokens, protocol-2 monotonic token admission, last-result replay,
expired-token refusal and durable Config-reference receipts. Read-only
protocol-1 operations remain available; old mutations fail closed.

Mode selection publishes the destination through checked Config persistence
before requesting reset. Failed or uncertain saves neither reset nor change
the active profile. Initialization consumes the committed destination and
activates the profile. Same destination is a no-op; a held chord is latched
until release. Non-Ultimate destinations use the same boundary.

Manual RT2 and automatic Config rejection both install the validator and
initialize inspection of usable storage before servicing the headless
Configurator. MB1 retains bootloader priority. No automatic formatting occurs.
Unavailable storage, invalid Config/root, migration fence, unknown transaction
and read-only recovery are distinct health information. Record health is an
explicit lazy operation, never LIST activation: healthy, recovered previous,
missing, corrupt and unsupported version are distinguishable.

## Bounded migration and resources

Persistence captures the exact validated persisted legacy input into one
immutable source file and hashes it. Individual profiles are streamed from
that source into the existing candidate profile, rather than a large automatic
Config object. Retry requires the same source identity. The receipt binds
version, incarnation, source, imported IDs/revisions and payload hashes. The
pending root also authenticates the canonical compact successor. Completion
rechecks source, dependencies, references/incarnation and receipt before
releasing the fence. Count/high-water/disk checks precede writes or array growth.

The shared unpublished Config candidate is reused by Configurator, selection
and migration. Active profile storage remains separate. Root resets occur in
place to avoid compiler-generated roughly 4 KiB aggregate temporaries.
Resource measurements and candidate-only heap/stack instrumentation are
specified in `profile_store_strict_resource_diagnostics.md`. The SDK 0x800
reservation is not presented as a whole-runtime stack bound; the two 4 KiB
scratch-bank envelopes remain explicit. Candidate diagnostics and fault hooks
must be removed or explicitly accepted in a separately reviewed final
production snapshot; this candidate is not a canonical merge authorization.
