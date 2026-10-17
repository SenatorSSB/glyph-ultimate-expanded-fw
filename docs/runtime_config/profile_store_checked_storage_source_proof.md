# Checked same-mount persistence source proof

This records source and host-model evidence for strict hardening B2. It does
not claim target power-loss, flash timing, multicore, or controller acceptance.
A fresh exact target candidate and the separately required owner hardware
campaign remain necessary.

The inspected package is `framework-arduinopico` version `1.30603.0`, Arduino-
Pico `3.6.3`. The installed directory name is `framework-arduinopico`; the
version is established by its package manifest and `RP2040Version.h`.

## Why the old wrapper is insufficient

Pinned `LittleFS.h`, `LittleFSFileImpl::flush`, calls `lfs_file_sync` but exposes
no result. `LittleFSFileImpl::close` discards `lfs_file_close`'s return and then
marks the handle closed. `LittleFSImpl::open` also ignores an initial sync
return. Thus successful byte writes plus `File.close()` cannot prove every
named sync/close result. Reopened content is useful exact-byte verification,
but it does not retroactively turn a discarded error into an observed result.

## How the mount is shared

Pinned `LittleFS.cpp` constructs the global `fs::FS LittleFS` with a
`littlefs_impl::LittleFSImpl` implementation. `FS.h` declares protected `_impl`;
`LittleFS.h` declares protected `_lfs` and `_mounted`. The repository's
`CheckedStorage.cpp` uses derived access classes solely to obtain pointers to
those members with their **declaring base-class member-pointer types**. Those
pointers are applied to the existing base objects. No global FS is cast to an
invented derived object, no layout offset is guessed, and no second filesystem
is constructed or mounted. The known implementation pointer is cast to the
exact implementation type used by the pinned global constructor.

The shim refuses an unmounted object and has a compile-time Arduino-Pico
3.6.3 version gate. All checked `lfs_*` calls receive this existing `_lfs`.
Its `cfg` retains the original framework callbacks and context. Pinned
`lfs_flash_prog` and `lfs_flash_erase` disable interrupts, idle the other core,
perform the SDK flash operation, resume the other core, and re-enable
interrupts. The repository does not replace or call around these callbacks.
The pinned flash sync callback is a successful no-op; LittleFS file sync still
performs its own checked file/metadata flush. No API here mounts, formats,
flashes firmware, or activates a profile. Callers retain synchronous core0
ownership.

## Observable outcomes

`CheckedStorage` exposes checked open, read, write, seek, file sync, file close,
stat, remove, rename, geometry and bounded enumeration. Native errors remain
observable with the operation and error code. Stat distinguishes `NOENT` from
I/O failure; remove is idempotent for genuine absence. Metadata errors after
execution and injected lost acknowledgements are conservatively uncertain.
The record/root/Config fault hook names the operation, before/after phase,
publication kind and source path.

ProfileStore and Config retain independent exact-byte verification before
publication. Config compares a second deterministic protobuf encoding with the
reopened staged body. A lost final Config rename can be resolved by that same
exact comparison against the published file. Otherwise Config retains an
uncertain result and fences writers until checked authoritative reload.
ProfileStore owns its format-specific intent/checkpoint reconciliation.

Geometry comes from the mounted `lfs_config`: block count, erase/block size,
program/read granularity and cache size. Used blocks come from checked
`lfs_fs_size`, including allocated filesystem metadata; negative or impossible
usage fails closed. Free bytes are checked total minus allocated bytes. The
adapter does not confuse logical file-body length with allocated capacity.

## Retained host evidence

- `tools/check_glyph_checked_storage_host.py` compiles the current production
  primitive against the pinned LittleFS C engine with ASAN/UBSAN. It covers 54
  operation-specific fault cases across record, root and Config, checked
  enumeration/geometry/absence, rename/remove lost acknowledgements and
  remount. Four old unchecked negative controls expose discarded close/sync
  results, including an actual `lfs_config.sync` I/O error.
- `tools/check_glyph_profile_store_config_persistence.py`, with
  `GLYPH_PROFILE_STORE_SANITIZERS=1`, compiles current `Persistence.cpp` with
  real Nanopb/CRC. It retains old compact-save/generation tests and adds
  checked sync/close refusal, exact lost-ack resolution, unknown writer
  fencing/reconciliation and immutable source SHA/streaming tests.
- `tools/check_glyph_profile_store_strict_host.py` compiles current
  `ProfileStore.cpp` against bounded block-charged storage and also exercises
  its actual mounted adapter on the pinned LittleFS engine. Twenty
  representative v3 profiles use 110592 allocated bytes in the RAM NOR model:
  total 524288, free 413696, protected accounting 143360, staging 45056, and
  conservative representative admission 32. These are model observations,
  not target-device geometry observations. The checker separately compiles
  actual frozen `f7ba82d4` production source to demonstrate the former reserve,
  lone-generation1 ID reuse, changed-source retry and name-truncation defects.

## Inspected dependency hashes

| Pinned dependency file | SHA-256 |
| --- | --- |
| `package.json` | `0aa78013e54caef261f2fd38b12ac84ce16c8f1e5dcba5660be6846e888c8960` |
| `cores/rp2040/FS.h` | `c188a6b49d593855d839162dd112c6a81ef4142dd5da82d59dcb983916521763` |
| `cores/rp2040/RP2040Version.h` | `c6b3f327351891c9a2c4a922a9c655b231fdd101948732afa513eabfbcf79440` |
| `libraries/LittleFS/src/LittleFS.h` | `6036f92f824ee8257da051ed37fe01e7dfdedece33c772ae6321036dc0f412f9` |
| `libraries/LittleFS/src/LittleFS.cpp` | `dfc032cc49b5254abc204b67a2aa56156d28e39b5adbb3b70c2e291667c70e5d` |
| `libraries/LittleFS/lib/littlefs/lfs.h` | `bece5357a4721c826c3d25ffab83962986a92f929fcf2d06bc9d66b5be2a3f3a` |
| `libraries/LittleFS/lib/littlefs/lfs.c` | `8c28c80018293820d5400759f4918359b09d869c1a1240959b0647cc844783b5` |
