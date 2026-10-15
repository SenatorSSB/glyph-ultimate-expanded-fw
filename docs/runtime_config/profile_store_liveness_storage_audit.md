# Fault-campaign storage liveness audit

Status: **SOURCE/HOST PASS; PHYSICAL ROOT CAUSE UNPROVEN**. This audit does not
change the failed hardware adjudication for candidate
`594066d9bb65b9f93c14e0e24e9d2002c3f83924`. No device operation was performed.

## Finding

The retained source has no demonstrated storage-side explanation for a later
STATUS timeout after the acknowledged record-open fault rows. The actual
ProfileStore engine and pinned LittleFS implementation complete a realistic
long session and 2,048 repetitions of the preceding fault sequence under
ASAN/UBSAN. Both the failed candidate's frozen storage sources and the current
candidate pass. This result narrows hypotheses; it is not proof that target
flash, core synchronization, USB, stack instrumentation or scheduling is healthy.

There is a separate, reproduced fault-control defect: the old ARM command
activates a rule before its acknowledgement is received. A discarded ARM
response can therefore leave a rule that fires during an ordinary later write.
The new pending ticket requires explicit presentation by one mutation and
unconditionally ends the active scope when that request returns. The storage
harness demonstrates the old negative and the new inert-pending behavior.

## Exact preceding storage sequence

`CheckedStorage::Open` constructs a native `lfs_file_t`, calls `lfs_file_open`,
then applies the after-operation fault hook. When the synthetic acknowledgement
is lost, the native handle remains owned by this function. Its existing
`if (!r && f.opened)` branch calls `lfs_file_close` exactly once and clears
`opened` before returning. That direct cleanup bypasses fault injection, while
the caller still receives the original uncertain result. An error returned by
that cleanup cannot turn the original uncertain result into success. Pinned
`lfs_file_rawclose` removes the handle from `mlist` and frees its file cache even
when its initial sync returns an error.

`ProfileStore::Publish` returns this failed result immediately, before temporary
readback or rename. `WriteProfile` sets the uncertainty fence. The authoritative
v2 roots and Ready control were never changed. `QueryTransaction` subsequently
calls `ReconcileTransaction`; a matching Ready control reloads the roots and
clears the fence without a publication. The attempted token is absent and the
query returns NOT_FOUND. A zero-byte temporary can remain; it is not authority.
The next mutation's normal admission GC removes it. Neither STATUS nor ARM
needs to remove it first.

The long-session fixture retains that zero-byte temporary across the next
STATUS and ARM. It does **not** insert an extra cleanup between those commands.
A deliberate missing-close mutant is rejected immediately after the fault by
the native-handle oracle. That mutation is a sensitivity check, not a historical
production defect or an explanation of the physical hang.

## Reconstruction and measured workload

Run:

```sh
python3 tools/check_glyph_profile_store_liveness_host.py --output-dir /private/tmp/glyph-liveness-storage-results
```

The checker compiles the actual `ProfileStore.cpp`, `CheckedStorage.cpp`,
validators and Nanopb with Arduino-Pico 3.6.3's LittleFS C engine. The same
512-KiB NOR geometry uses 128 blocks of 4,096 bytes, 256-byte read/program/cache
sizes, 256-byte lookahead and block_cycles=16. Allocation accounting wraps the
pinned C source's actual `malloc/free` calls; it does not assume newer optional
LittleFS allocator macros exist. No alternative storage adapter handles the
mutations. The default production MountedStorage is used.

The portable v1 fixtures contain IDs 1/3/4, the older and completed roots, and
their exact record bytes. The production upgrade creates v2 authority and
promotes the compact Config receipt. Encoded Config current/prior, legacy and
migration-source files occupy real filesystem blocks. The fixture then creates
through high-water ID22, deletes ID21, and performs 129 successful updates on
ID22. The exact checkpoint has twenty live profiles, generation160 and ID22
revision130. Useful IDs1/3/4 retain their bytes. An older active revision remains
protected. The Config files are source-shaped, CRC-protected fixture bytes;
this checker does not execute Persistence's Config publication implementation,
which has its own dedicated checker.

Of those successful updates, 43 discard the initial result, query the durable
receipt, and replay the exact identity. Every replay performs zero flash block
programs. This models result loss at the storage API boundary; the separate
transport harness owns serial framing and port-reopen evidence.

Each of 2,048 cycles runs record OpenWrite fail-before, OpenWrite lost-ack-after,
then Write fail-before, with Capacity/STATUS work before and after each fault,
ARM preparation, reconciliation, clear and rearm. Each row verifies both roots
and control byte-for-byte, unchanged generation/revision/count, no uncertainty
fence after NOT_FOUND, expected temporary residue, no native handle, and the
mount-only allocation baseline. Actual mutation admission performs GC.

The final validated run produced:

| Measurement | Frozen failed candidate storage | Current storage |
| --- | ---: | ---: |
| Full three-row cycles | 2,048 | 2,048 |
| Injected faults | 6,144 | 6,144 |
| Capacity samples | 20,610 | 20,610 |
| Largest Capacity block-read count | 1,900 | 1,900 |
| Largest Capacity checked-stat count | 29 | 29 |
| Largest observed host Capacity time | 1.064 ms | 7.212 ms |
| Native open handles after operations | 0 | 0 |
| Steady LittleFS allocations / bytes | 3 / 768 | 3 / 768 |
| Peak live LittleFS allocation bytes | 1,024 | 1,024 |
| Total LittleFS allocations | 50,555 | 50,555 |
| Actual directory enumerations | 10,521 | 10,521 |
| NOR erases, including setup/history | 1,868 | 1,868 |

Both unmounts release all LittleFS allocations. At generation160, used space is
147,456 bytes, free space 376,832, protected charge 188,416, staging charge
45,056 and reserve 16,384; conservative admissible count is29. These quantities
are fixture measurements, not readback from the failed controller. The full
report retains output and source hashes. Host timing is not a target deadline
or multicore timing bound.

## Capacity and hook boundedness

`ProfileStore::Capacity` calls actual `lfs_fs_size`, loads the opposite protected
root when necessary, then probes a deduplicated union of current/prior revisions,
migration dependencies, active revision and fixed Config/source paths. Its
entry loops are bounded by64 entries per root. There are at most263 record and
fixed-file probes before any required protected-root read. The pinned
`lfs_fs_rawtraverse` detects metadata-pair cycles at `block_count / 2` (64 for
this geometry). Open-file traversal assumes an uncorrupted native list; the
stress test checks that this list is empty at every operation boundary.

Every measured Capacity sample performs zero block programs and zero erases.
The host results do not justify claiming Capacity can never hang on corrupted
RAM or target flash callbacks. They also do not establish a need to weaken
admission accounting. Keeping inexpensive status diagnosis distinct from a
capacity scan can localize such a problem without replacing the full capacity
and reserve checks used for mutation admission.

The old fault hook remains installed after triggering, but checks `armed`
before accessing the configured operation/path and returns None while inactive.
The stress test retains that behavior when compiling the frozen old header.
Current EndMutation instead removes the hook. The only production installer is
the candidate Configurator fault control. Configurator requests, ProfileStore
storage calls and the fault state use synchronous core0 ownership. In
Configurator mode, core1's `loop1` returns at the Remapper display guard and
performs no profile-store call. No claim is made that arbitrary display/menu
callbacks in other modes were added to this fault campaign.

## Negative controls and limits

- Frozen ARM, lost acknowledgement, ordinary record write: **DETECTED**; the
  old rule fires. Current pending ARM leaves that ordinary write unaffected;
  wrong tickets fail, exact tickets start a scope, and consumed tickets fail.
- Deliberately deleting lost-open cleanup: **DETECTED** at the immediate native
  handle check. This is a synthetic source mutation, not an old-source failure.
- Frozen and current physical-sequence storage tests both pass. There is no
  reproduced old-source liveness failure to label repaired.

The harness does not execute RP2040 flash programming, `idleOtherCore`, IRQs,
TinyUSB, PacketIO, stack watermarks or firmware `_sbrk`. Its allocation numbers
cover LittleFS's owned allocations, not the entire target heap. Actual device
filesystem bytes are unavailable; the reconstruction matches the important
history/identity/resource shape and executes real GC, but is not a captured
image of the controller. A new candidate still requires exact-artifact human
hardware evidence. The current failed artifact remains hardware FAIL.
