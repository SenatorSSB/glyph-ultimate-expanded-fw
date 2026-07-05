# Latest Y2 Layout Source-Owned Port Build Report - 2026-06-29

Status: LOCAL_BUILD_REPORT.

Branch:
`runtime-config-latest-y2-layout-source-owned-port`

Canonical command: pio run -e glyph_mk6

Fallback command used: ./scripts/build-glyph-mk6-quiet.sh

Result: PASS.

The canonical command was unavailable locally because `pio` was not on PATH.
The repository wrapper was executable and completed the `glyph_mk6` build.

Active behavior changed: `true`.

Full latest layout port: `true`.

Source-owned table content replacement wired: `true`.

Active view selection changed: `false`.

RuntimeConfigView replacement is not used.

Generated active wrapper used: `false`.

Candidate view published active: `false`.

RAM-backed active table publication: `false`.

Runtime-loaded config, persistent storage, WebSerial/device write,
backend/config.pb write path, and firmware flashing automation are not
implemented.

No hardware result is claimed.

hardware_test_required_before_merge: true.

Nunchuk remains NOT_TESTED.

Root cause remains unproven.

## Artifact Hashes

Artifact hashes are local observations only, not checker gates.

- `.pio/build/glyph_mk6/firmware.elf`:
  `4834caf79e043e8e00ba3b1c3234fe776b720c761945257b3fdc45ea25f6dee4`
- `.pio/build/glyph_mk6/firmware.uf2`:
  `23bf009264a9cfc00779e325ae534a50e5458d0c976116d115f7298e906937a1`
- `.pio/build/glyph_mk6/firmware.bin`:
  `ed8d66c4b954a1b3d4bf8e3c6d64579d810e05cd8bb515ce3830bfff56948c7b`

`artifact_hashes_are_rebuild_stable`: `false`

`artifact_hashes_are_checker_gate`: `false`
