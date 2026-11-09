# Candidate-only exact retained config.bin extraction

This isolated software candidate implements the owner's bounded
`EXACT_RETAINED_CONFIG_BIN_READONLY_EXTRACTION` objective. Physical `/config.bin`
bytes and family remain **UNKNOWN**. No physical observation, installation,
hardware acceptance, compatibility repair, source promotion or canonical
publication follows from synthetic validation.

The isolated `glyph_mk6` environment explicitly sets
`GLYPH_CONFIG_BIN_READONLY_DIAGNOSTIC=1`; the source default is zero. This flag
forces the recovery transport before normal Config loading, store initialization,
migration and backend initialization. The candidate recovery entry skips
`initialize_recovery`, so it does not load/adopt Config or initialize ProfileStore.
Existing Runtime Identity and STATUS handlers and wire schemas are unchanged.
The initial hardware packet does not request STATUS.

Before the existing first LittleFS mount, the candidate replaces the actual
Arduino-Pico 3.6.3 mount configuration's program and erase callbacks with denial
callbacks. They remain denied throughout that boot. Automatic formatting remains
disabled. The read callback, context and geometry are unchanged. This is stronger
than `LittleFSConfig(false)`, which disables formatting but ordinarily retains
working flash callbacks. No second mount is created, no raw-flash reader is added,
and no fence is cleared.

The operation opens only the compile-time literal `/config.bin`, using
`lfs_file_opencfg`, `LFS_O_RDONLY` and a supplied 256-byte file cache. It requires
the denied callback configuration, no other open handles, and the pinned cache
size. It never calls the Arduino File wrapper, Config decoder, package API,
storage classifier or mutators. The new state borrows the existing 8192-byte
Configurator RX/TX frame through an aligned union; no second Config or complete
file buffer is added. Existing boot/library allocations are distinct from this
allocation-free extraction operation.

## Candidate wire

Outer framing is existing COBS with one command byte `0x7e`. No production
protobuf enum or schema is extended. All integer fields below are little endian.
The fixed request is exactly 16 bytes: `GCB1`, version byte 1, type byte 0,
reserved uint16 zero, nonzero uint64 nonce. Unknown/trailing/short requests drop
without storage access. A trusted request in recovery consumes a boot-local
one-shot latch before checking storage. Neither error nor lost delivery grants
a second operation.

Every response begins with the same 16-byte common header: `GCB1`, version 1,
type byte, status uint16, echoed nonce uint64.

| Type | Bytes after common header |
|---|---|
| 1 BEGIN | file size uint32; chunk maximum uint32 = 128 |
| 2 CHUNK | absolute raw-file offset uint32; count uint16; reserved uint16 zero; count raw bytes |
| 3 FINAL | layout below; exactly 116 total bytes |

FINAL offsets from its payload start:

| Offset | Field |
|---|---|
| 16 | file size uint32 |
| 20 | successfully sent bytes uint32 |
| 24 | raw header's declared body size uint32, or zero without a full header |
| 28 | raw header's stored CRC32 uint32, or zero without a full header |
| 32 | body bytes successfully read and sent uint32 |
| 36 | CRC32 over successfully read body bytes uint32 |
| 40 | available header byte count uint8, from 0 to 8 |
| 41 | factual flags uint8 |
| 42 | reserved uint16 zero |
| 44 | first eight raw file bytes, zero padded |
| 52 | complete raw-file SHA-256, 32 bytes |
| 84 | complete physical body SHA-256, 32 bytes |

Flags: bit0 complete eight-byte header; bit1 declared size equals physical body
size; bit2 stored CRC equals observed body CRC; bit3 complete read/EOF/size check;
bit4 successful close. Other bits are zero. Size/CRC match flags are not set
without a complete header. SHA fields are populated only after complete read
and successful close; failures leave them zero. Partial-result metadata is
diagnostic and cannot establish complete-file identity.

Statuses: 0 OK; 1 NOT_RECOVERY; 2 ALREADY_USED; 3 STORAGE_UNAVAILABLE;
4 NOT_FOUND; 5 OPEN_FAILED; 6 SIZE_LIMIT; 7 READ_FAILED; 8 CLOSE_FAILED;
9 DEADLINE; 10 INTERNAL (reserved).

The physical file limit is 524288 bytes, from the pinned filesystem extent,
not a guessed historical writer limit. The body is **every physical file byte
after the first eight**, regardless of header claims. Empty/short/malformed
wrappers can therefore extract successfully while their factual flags expose
the mismatch. No historical family or protobuf validity is inferred.

One request emits BEGIN, contiguous CHUNKs, then FINAL. Files missing or refused
before BEGIN receive only FINAL. A successful FINAL requires complete raw bytes,
EOF, unchanged file size and checked close. Any TX failure closes the handle and
stops without retrying, replaying, or adding a later FINAL. Candidate TX separately
enforces the remaining absolute 60-second operation budget and two seconds per
frame using coordinated nonblocking FIFO admission; existing production writer
behavior is unchanged. Filesystem calls are synchronous and source bounded;
no claim of interrupting a stalled flash read is made.

## Synthetic verification and remaining gates

`python3 tools/check_config_bin_readonly_diagnostic.py` compiles the actual
extraction module with pinned LittleFS and ASan/UBSan against a newly seeded
synthetic 512 KiB NOR. It checks exact raw bytes and independent Python
SHA-256/CRC32, absent/empty/short/header-only/70008-byte malformed fixtures,
read/size/close faults, deadline, partial TX, checked handle cleanup, no extraction
allocation, no real program/erase calls, and byte-identical NOR. Test function
interposition applies only to synthetic objects; production source remains linked
normally. The direct deny-callback negative check proves it cannot reach real
program/erase callbacks.

`python3 tools/check_config_bin_readonly_backend.py --libdeps <local-library-directory>`
also compiles the actual ConfiguratorBackend, PacketIO, Persistence and store
sources against synthetic NOR. It verifies COBS framing, one-shot and recovery
refusals, malformed-request recovery, subsequent Identity, Config/store/NOR
preservation, initial-mount denial and negative raw remove/rename/dirty-handle
controls. Source guards compare existing Identity and STATUS-related handler
bodies with the exact parent, and verify default-off/fixed-path/early-boot bounds.
No corpus is consumed by either diagnostic checker.

Fresh independent review, exact target build/custody and linked resource
adjudication remain separate required gates.
Existing ceilings remain 2048-byte foreground stack, retained caller 64 bytes,
199632-byte static RAM and 1568768-byte flash. Nothing in this document claims
those target checks have already passed.

Any later hardware action needs a separately approved exact artifact packet:
initially disconnected, one owner bootloader/manual copy, recovery, exact
Identity status3/backend8, one extraction, disconnect. No retries, restore,
adoption, cleanup, package/profile/Config writes or compatibility changes are
authorized. Exact extracted bytes belong only in the approved private evidence
location, never public logs or fixtures.
