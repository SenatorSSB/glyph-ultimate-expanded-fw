# Current Config Persistence Recovery Research

Status: EVIDENCE_COMPLETE_IMPLEMENTATION_NOT_AUTHORIZED.

Research source was live-verified at configurator 2a80462ba2801192154e42ee4bebb9b1b43ca699; the exact reviewed source blobs remain unchanged at research implementation base 1a4b9311c8f7ae6d7cbf0a8680cd976499112f03. Changes are limited to this packet, its evidence fixture, offline checker and deterministic validation metadata. No firmware build, config.bin access, upstream execution, filesystem mount, device or hardware action.

## Immutable upstream authority

The configured selector is framework-arduinopico@https://github.com/earlephilhower/arduino-pico.git#3.6.3. Read-only live ls-remote resolved 3.6.3 to commit 32e74d024e5e3ee5e7ec9593f5a4101641c61897. GitHub Git commit API independently confirms commit identity. That commit's recursive tree binds libraries/LittleFS/lib/littlefs as mode 160000 commit 6a53d76e90af33f0656333c1db09bd337fa75d23; its .gitmodules binds https://github.com/littlefs-project/littlefs.git. The littlefs Git commit API confirms the gitlink identity. Exact trees, source bytes, per-file Git blob SHA-1 rehash, SHA-256, immutable raw URLs, and UTC lookup timestamps are frozen in the companion fixture with reviewed excerpts. Default restricted DNS failed; permitted read-only escalated retry succeeded. These are source-selector observations, not proof of an installed framework or built/device image.

## Immutable source locators

| Repository/source | Exact Git blob |
| --- | --- |
| [arduino_pico/.gitmodules](https://github.com/earlephilhower/arduino-pico/blob/32e74d024e5e3ee5e7ec9593f5a4101641c61897/.gitmodules) | `a754388fde16464d414423684b6dd71b86c728ee` |
| [arduino_pico/cores/rp2040/FS.cpp](https://github.com/earlephilhower/arduino-pico/blob/32e74d024e5e3ee5e7ec9593f5a4101641c61897/cores/rp2040/FS.cpp) | `8a25e225551473e2af889877b6d4e8d493d86441` |
| [arduino_pico/cores/rp2040/FS.h](https://github.com/earlephilhower/arduino-pico/blob/32e74d024e5e3ee5e7ec9593f5a4101641c61897/cores/rp2040/FS.h) | `0ea617aaa8ca548735df335ef4ac686655167617` |
| [arduino_pico/libraries/LittleFS/src/LittleFS.cpp](https://github.com/earlephilhower/arduino-pico/blob/32e74d024e5e3ee5e7ec9593f5a4101641c61897/libraries/LittleFS/src/LittleFS.cpp) | `a6299da36aa62fd0d628ce17d2a25e611e3b9a24` |
| [arduino_pico/libraries/LittleFS/src/LittleFS.h](https://github.com/earlephilhower/arduino-pico/blob/32e74d024e5e3ee5e7ec9593f5a4101641c61897/libraries/LittleFS/src/LittleFS.h) | `53e8637b3675a13ede044ddc513a79658ea3f373` |
| [arduino_pico/libraries/LittleFS/src/lfs.c](https://github.com/earlephilhower/arduino-pico/blob/32e74d024e5e3ee5e7ec9593f5a4101641c61897/libraries/LittleFS/src/lfs.c) | `63bebe1965d127bb220db7a520e06de3c107391b` |
| [littlefs/DESIGN.md](https://github.com/littlefs-project/littlefs/blob/6a53d76e90af33f0656333c1db09bd337fa75d23/DESIGN.md) | `1d02ba3bfcc37303fe3251acf3047fa2974fc498` |
| [littlefs/README.md](https://github.com/littlefs-project/littlefs/blob/6a53d76e90af33f0656333c1db09bd337fa75d23/README.md) | `32b3793f37360e2c467dd929f07c162ccf1ce6d4` |
| [littlefs/SPEC.md](https://github.com/littlefs-project/littlefs/blob/6a53d76e90af33f0656333c1db09bd337fa75d23/SPEC.md) | `3663ea54425f9054196dcd9b42ab205726078f5e` |
| [littlefs/bd/lfs_testbd.c](https://github.com/littlefs-project/littlefs/blob/6a53d76e90af33f0656333c1db09bd337fa75d23/bd/lfs_testbd.c) | `1f0877d43aa0c20d08ff94ccf090a79b5d1db7d5` |
| [littlefs/bd/lfs_testbd.h](https://github.com/littlefs-project/littlefs/blob/6a53d76e90af33f0656333c1db09bd337fa75d23/bd/lfs_testbd.h) | `61679e5e026aecfe2981efb918102e9a09b80b74` |
| [littlefs/lfs.c](https://github.com/littlefs-project/littlefs/blob/6a53d76e90af33f0656333c1db09bd337fa75d23/lfs.c) | `26280fa89509bb4f94ced008ac02cd60b5c2cff8` |
| [littlefs/lfs.h](https://github.com/littlefs-project/littlefs/blob/6a53d76e90af33f0656333c1db09bd337fa75d23/lfs.h) | `2bce17f5ccb91236341f30994c1b8ff42fc06872` |
| [littlefs/tests/test_files.toml](https://github.com/littlefs-project/littlefs/blob/6a53d76e90af33f0656333c1db09bd337fa75d23/tests/test_files.toml) | `565e665bc9f999554d12dfe29b43926b56d870aa` |
| [littlefs/tests/test_move.toml](https://github.com/littlefs-project/littlefs/blob/6a53d76e90af33f0656333c1db09bd337fa75d23/tests/test_move.toml) | `bb3b713f1013ac79e50c0f12aa1442477f21e3f0` |

## Current application path

Persistence constructor calls LittleFS.begin() and ignores its bool; destructor calls end(). ConfigHeader stores native size_t config_size and uint32_t config_crc, with payload offset sizeof(ConfigHeader); no portable serialized-header ABI claim is made.

SaveConfig order: pb_get_encoded_size checked before file access; open config.bin w+ checked; initialize zero header; header write count ignored; construct protobuf output stream; pb_encode checked (on failure close then false); seek payload offset ignored; read bytes until -1 while updating CRC (EOF/read error not distinguished); set header size from ostream.bytes_written and CRC from finalize; seek zero ignored; rewrite header count ignored; close provides no caller-visible result; return true. Preflight encoded_size is not used to reserve/check filesystem capacity or verify actual written size. There is no temporary, backup, rename, generation, or application rollback sequence.

LoadConfig order: read-only open checked; CheckSavedConfig checked (close/false on rejection); seek payload checked; assign Config_init_default; construct bounded input stream from available(); pb_decode checked (close/false on failure); close then true. CheckSavedConfig gets file size; requires a complete header; requires actual body length equal config_size; reads remaining bytes for CRC until -1; compares header CRC. CRC success does not establish protobuf decode success or controller/domain validity. Single-byte File::read() short/error reads collapse to -1 in the wrapper; buffered reads report counts or zero, so the application does not distinguish read failure from EOF.

Boot starts global Config from glyph_default_config(), calls LoadConfig, and if false calls SaveConfig(config) without checking its bool, before initialize_backends. Caveat: the comment's 'write default' is not universal behavior. If LoadConfig reaches reset/decode and then fails, setup saves the Config_init_default/partially decoded state left by that call; it does not restore glyph_default_config. The exact partial contents are UNKNOWN without a payload/nanopb analysis. This is source-backed flow plus labeled inference, not a proposed GP-CONFIG-005 transaction repair.

SetConfig now uses a function-static candidate: defaults and protobuf decode occur in candidate storage, all existing reference checks read candidate, and the existing SaveConfig(candidate) call runs while live _config remains unchanged. A successful save is followed by one `_config = candidate` publication; decode, reference, and save rejection paths send the existing CMD_ERROR and leave live RAM untouched. This is the bounded GP-CONFIG-005 RAM invariant only; it does not claim disk atomicity, persistence recovery, or successful-update runtime rebinding. SendReport does not use HandleSetConfig's return. An additional existing persistence caller is backend_init.cpp's selected boot-backend/mode update; SaveConfig result is ignored. It prevents claiming that the four requested files cover all save cadence or concurrency.

The companion [GP-CONFIG-005 transaction fixture](fixtures/configurator_setconfig_transaction.json) and [compiled production-path host harness](../../tools/check_glyph_configurator_setconfig_transaction.py) bind and compile the exact current handler source. Host doubles replace only nanopb decode/stream plumbing, persistence, packet transport, and platform-only symbols; the binary executes the production `HandleSetConfig()` body through all seven current validation families, save failure, and success without a runtime fault command, device access, or config.bin access. The immutable GP-PERSIST-001 source catalog remains pinned to its research base, while its explicit GP-CONFIG-005 overlay and current step table bind the renewed live handler.

## Dependency semantics and limits

FS.cpp interprets w+ as OM_CREATE | OM_TRUNCATE plus read/write access. LittleFS.h maps truncate to LFS_O_TRUNC. LittleFSImpl::open calls lfs_file_open then immediately lfs_file_sync after a successful open and discards that sync result. The pinned lfs.c marks an existing truncated file dirty with an empty inline structure. Inference: successful initial open sync can commit truncation before application header/body work, so a future interruption can leave an empty current file even if later writes were never closed. Exact observed power-loss outcome is UNKNOWN.

Pinned littlefs README documents atomic individual POSIX operations such as rename/remove and file-update commit at sync/close. This is a library contract under its block-device obligations, not whole SaveConfig atomicity and not evidence that this controller survives power loss. lfs.h exposes negative errors from sync/close, whereas wrapper close discards lfs_file_close's int and wrapper flush only DEBUGV-logs sync error. lfs.h allows an existing rename target of the same type (directory must be empty); that does not select a replacement/recovery policy.

LittleFSConfig defaults autoFormat=true. begin attempts mount, then when enabled calls format on mount failure and retries mount. The current Persistence constructor neither configures an alternative policy nor checks begin's result. Wrapper block read uses memory copying; prog/erase disable interrupts, idle the other core, call flash_range_program/erase, resume the other core, reenable interrupts, return zero. The sync callback is a no-op returning zero. These are exact wrapper source facts; underlying device persistence and cache guarantees remain UNKNOWN here.

Declared filesystem size is 0.5m. Wrapper global construction uses linker _FS_start/_FS_end, program/page 256 bytes, erase block 4096, max open FDs 16; cfg read/prog/cache/lookahead=256 and block_cycles=16. littlefs defines block_cycles as metadata relocation policy, not flash lifetime; its docs describe dynamic wear leveling. Actual filesystem capacity, free space/reserve, chip endurance, write amplification, save frequency, concurrency correctness, installed linker layout, and firmware-update preservation are UNKNOWN. No reserve/wear threshold selected.

## Failure windows

1. Preflight encode fails: SOURCE_BACKED false before application file open; physical prior storage unknown.
2. Mount/open fails or format branch occurs: SOURCE_BACKED code branches; actual old-data outcome UNKNOWN.
3. Successful truncate/open sync before first header: INFERRED committed-empty possibility from exact wrapper/lfs source; no application backup.
4. Placeholder-header short/error write: SOURCE_BACKED ignored count; INFERRED later encode/CRC/header can be inconsistent.
5. Body encode failure: SOURCE_BACKED close then false; INFERRED close may persist incomplete body with placeholder header; Load check can reject; hardware outcome UNKNOWN.
6. Payload seek/read/CRC pass failure: SOURCE_BACKED unchecked seek and -1 loop; INFERRED checksum may cover wrong/incomplete bytes while save later reports true.
7. Final seek/header rewrite short/error: SOURCE_BACKED unchecked; INFERRED stale/invalid header may survive reported success.
8. Close/sync error or interruption: SOURCE_BACKED status not propagated; INFERRED SaveConfig true is not persistence-success proof.
9. Load header/size/CRC failure: SOURCE_BACKED false, boot attempts save remaining config.
10. Decode failure after integrity pass: SOURCE_BACKED config reset before checked decode; INFERRED boot may save partially decoded/default-initialized object.
11. SetConfig decode/reference/save failure: SOURCE_BACKED staged-candidate rejection paths preserve the previously accepted live RAM config; persistence recovery and disk atomicity remain unclaimed.
12. Capacity/wear/concurrent save/update/power-loss effects: UNKNOWN device facts, bounded by source evidence and future gates.

## Options only; none selected

Temp-and-rename can describe staging complete content, validating it, then an individual namespace replacement; decisions include error propagation, replace semantics, fsync/close proof, stale file cleanup, old-or-new invariant, and compatibility. Temp-plus-backup additionally preserves a previous candidate at greater capacity and cleanup/recovery-precedence complexity; multiple namespace operations do not become one transaction. Two-slot/generation can describe separately validated candidates and ordering/selection metadata; generation rollover/ties, partial validity, boot precedence, migration, old-firmware compatibility, storage and wear all remain decisions. No filenames, format, mechanism, fallback, or acceptance policy chosen.

## Future testability and authority

Pinned bd/lfs_testbd.h and .c provide write-operation-count power-cycle exits at erase/program operation boundaries; tests/test_files.toml has reentrant file-writing with syncs and tests/test_move.toml reentrant move cases. They show source-level upstream harness feasibility only. They have not been run here, do not wrap Glyph Config/protobuf automatically, and are not controller evidence. They do not establish torn program/erase, brownout, or controller power-loss behavior. Existing Glyph runtime-config storage simulator explicitly excludes config.bin.

Potential future cut points: each application operation listed above; initial open sync; body and final-header writes; close; mount/format; any separately authorized publish/rename/recovery action. Error/short return injection and virtual block-device interruption are research options, not an implemented/selected harness.

Before future implementation: exact current-Config recovery invariant (old-or-new versus prior-good), boot/default/autoformat behavior, live-memory failure semantics boundary, diagnostics and readback policy, concurrency ownership, compatibility/migration/update preservation, reserve/wear/cadence, recovery precedence/cleanup, mechanism and fault-injection scope must be authorized in a complete H3 READY work order. Then independent source review, fault tests to exact expected invariants, canonical build with exact candidate SHA and artifact SHA-256 custody, and user physical tests under Revision-2 are required before merge. Nunchuk stays NOT_TESTED, root cause unproven. Research completion needs no user choice; H3 successor design does.

## Offline correspondence contract

The companion [fixture](fixtures/current_config_persistence_recovery_research.json) and [checker](../../tools/check_glyph_current_config_persistence_recovery_research.py) bind exact current blobs, closed ordered operations, immutable upstream identities/excerpts, classifications and non-authority gates. Offline validation checks frozen reviewed upstream provenance; it does not recontact upstream or rehash absent full upstream bodies. At research capture, each full body was hashed against its API tree Git blob. Individual record seals protect reviewed prose/classifications alongside structural and source checks, rather than treating one fixture digest as evidence. Changed source or facts require renewed source-authority review.

## Exact coverage and future decisions

<!-- persistence-coverage:start -->
| Step | Handling | Source |
| --- | --- | --- |
| `lifecycle.mount` | IGNORED | `HAL/pico/src/core/Persistence.cpp:29` |
| `lifecycle.unmount` | VOID | `HAL/pico/src/core/Persistence.cpp:33` |
| `save.size` | CHECKED | `HAL/pico/src/core/Persistence.cpp:39` |
| `save.open` | CHECKED | `HAL/pico/src/core/Persistence.cpp:44` |
| `save.placeholder` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:50` |
| `save.header_write` | IGNORED | `HAL/pico/src/core/Persistence.cpp:51` |
| `save.stream` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:54` |
| `save.encode` | CHECKED | `HAL/pico/src/core/Persistence.cpp:55` |
| `save.seek_body` | IGNORED | `HAL/pico/src/core/Persistence.cpp:61` |
| `save.crc_init` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:62` |
| `save.read_crc` | SENTINEL_ONLY | `HAL/pico/src/core/Persistence.cpp:64` |
| `save.length` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:69` |
| `save.crc_final` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:70` |
| `save.seek_header` | IGNORED | `HAL/pico/src/core/Persistence.cpp:71` |
| `save.header_rewrite` | IGNORED | `HAL/pico/src/core/Persistence.cpp:72` |
| `save.close` | VOID | `HAL/pico/src/core/Persistence.cpp:75` |
| `save.success` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:77` |
| `load.open` | CHECKED | `HAL/pico/src/core/Persistence.cpp:82` |
| `load.validate` | CHECKED | `HAL/pico/src/core/Persistence.cpp:87` |
| `load.seek` | CHECKED | `HAL/pico/src/core/Persistence.cpp:93` |
| `load.reset` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:100` |
| `load.stream` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:103` |
| `load.decode` | CHECKED | `HAL/pico/src/core/Persistence.cpp:104` |
| `load.close` | VOID | `HAL/pico/src/core/Persistence.cpp:109` |
| `load.success` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:110` |
| `check.size` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:155` |
| `check.header` | CHECKED | `HAL/pico/src/core/Persistence.cpp:159` |
| `check.length` | CHECKED | `HAL/pico/src/core/Persistence.cpp:165` |
| `check.read_crc` | SENTINEL_ONLY | `HAL/pico/src/core/Persistence.cpp:173` |
| `check.crc` | CHECKED | `HAL/pico/src/core/Persistence.cpp:176` |
| `check.success` | NOT_APPLICABLE | `HAL/pico/src/core/Persistence.cpp:180` |
| `boot.default` | NOT_APPLICABLE | `config/glyph/common/src/config.cpp:34` |
| `boot.load_save` | CHECKED_LOAD_IGNORED_SAVE | `config/glyph/common/src/config.cpp:91` |
| `boot.backends` | NOT_APPLICABLE | `config/glyph/common/src/config.cpp:96` |
| `setconfig.reset` | NOT_APPLICABLE | `HAL/pico/src/comms/ConfiguratorBackend.cpp:169` |
| `setconfig.stream` | NOT_APPLICABLE | `HAL/pico/src/comms/ConfiguratorBackend.cpp:171` |
| `setconfig.decode` | CHECKED | `HAL/pico/src/comms/ConfiguratorBackend.cpp:172` |
| `setconfig.decode_error` | IGNORED | `HAL/pico/src/comms/ConfiguratorBackend.cpp:176` |
| `setconfig.backend_bound` | CHECKED | `HAL/pico/src/comms/ConfiguratorBackend.cpp:181` |
| `setconfig.mode_bound` | CHECKED | `HAL/pico/src/comms/ConfiguratorBackend.cpp:196` |
| `setconfig.keyboard_type` | CHECKED | `HAL/pico/src/comms/ConfiguratorBackend.cpp:216` |
| `setconfig.custom_type` | CHECKED | `HAL/pico/src/comms/ConfiguratorBackend.cpp:228` |
| `setconfig.keyboard_bound` | CHECKED | `HAL/pico/src/comms/ConfiguratorBackend.cpp:240` |
| `setconfig.custom_bound` | CHECKED | `HAL/pico/src/comms/ConfiguratorBackend.cpp:254` |
| `setconfig.save` | CHECKED_SAVE_IGNORED_PACKET | `HAL/pico/src/comms/ConfiguratorBackend.cpp:269` |
| `setconfig.publish` | NOT_APPLICABLE | `HAL/pico/src/comms/ConfiguratorBackend.cpp:275` |
| `setconfig.success` | IGNORED_PACKET | `HAL/pico/src/comms/ConfiguratorBackend.cpp:277` |
| `additional_save.save` | IGNORED | `HAL/pico/src/comms/backend_init.cpp:117` |

| Failure window | Classification | Current consequence |
| --- | --- | --- |
| `encode_preflight` | SOURCE_BACKED | False returns before application open; no physical prior-storage claim. |
| `mount_open` | SOURCE_BACKED | Failed open returns false; enabled format may follow failed mount. Physical data outcome UNKNOWN. |
| `truncate_sync` | INFERRED | Successful initial sync can commit an empty file before header/body; no application backup exists. Exact interruption outcome UNKNOWN. |
| `placeholder_write` | INFERRED | Ignored short/error write can leave incomplete header; later flow continues. |
| `body_encode` | INFERRED | Encode failure closes then returns false; incomplete data may be persisted with placeholder header. |
| `seek_read_crc` | INFERRED | Ignored seek or read error can compute CRC over wrong/incomplete bytes while flow continues. |
| `header_rewrite` | INFERRED | Unchecked final positioning/write may leave invalid header despite subsequent true return. |
| `close_sync` | INFERRED | Close status is unavailable to caller; true SaveConfig is not proof of persistent success. |
| `load_integrity` | SOURCE_BACKED | Header/length/CRC rejection returns false and boot attempts save of remaining in-memory config. |
| `load_decode` | INFERRED | Decode failure after integrity pass can leave reset/partial config that boot then saves. |
| `setconfig_failure` | SOURCE_BACKED | Every decode, reference, or SaveConfig rejection leaves accepted live RAM unchanged; persistence disk recovery remains unclaimed. |
| `device_limits` | UNKNOWN | Capacity, wear, concurrency, update and physical interruption outcomes require future evidence and authority. |

| Future H3 decision | Exact question |
| --- | --- |
| `recovery_invariant` | Should a failed update preserve old-or-new valid data or a specifically identified prior-good configuration? |
| `stale_state_cleanup` | What recovery precedence and stale-state cleanup are required for incomplete candidates? |
| `boot_default` | What should boot do after integrity/decode failure and which default or retained state may it save? |
| `autoformat` | Should mount failure permit autoformat, retain data for recovery, or require an explicit recovery action? |
| `migration_compatibility` | What old-firmware and stored-layout compatibility/migration must be preserved? |
| `rename_replacement` | What replacement behavior and failure handling are required if a future mechanism uses rename? |
| `readback_diagnostics` | Which write/sync/readback failures must be exposed and through what approved diagnostic behavior? |
| `concurrency` | Who owns save serialization and concurrent access to current Config and storage? |
| `capacity_wear_save_cadence` | What reserve, capacity, wear bounds and save cadence must be measured and accepted? |
| `update_preservation` | What storage preservation is required across firmware updates and rollback? |
| `fault_injection` | Which separately authorized host or physical fault model and cut-point coverage establish the chosen invariant? |
| `physical_recovery_acceptance` | What operator recovery UX and exact Revision-2 physical acceptance rows must a future candidate satisfy? |
<!-- persistence-coverage:end -->
