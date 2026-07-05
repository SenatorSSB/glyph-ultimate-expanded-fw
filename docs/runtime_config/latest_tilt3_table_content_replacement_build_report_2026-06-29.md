# Latest Tilt3 Table Content Replacement Build Report - 2026-06-29

Status: LOCAL_BUILD_REPORT.

Branch:
`runtime-config-latest-tilt3-table-content-replacement`

Canonical command: pio run -e glyph_mk6

Fallback command used: ./scripts/build-glyph-mk6-quiet.sh

Result: PASS.

The canonical command was unavailable locally because `pio` was not on PATH.
The repository wrapper was executable and completed the `glyph_mk6` build.

Active behavior changed: `true`.

Latest layout partial port: `true`.

Changed source file: `src/modes/UltimateIdentityRuntimeTables.hpp`.

Changed table: `kTilt3Table`.

Y2 routing implemented: `false`.

Y2 table identity implemented: `false`.

LT3 Y2 role implemented: `false`.

Active view selection changed: `false`.

RuntimeConfigView replacement: `false`.

Source-owned table-content replacement wired: `true`.

Runtime-loaded config, persistent storage, WebSerial/device write,
backend/config.pb write path, and firmware flashing automation are not
implemented.

No hardware result is claimed.

hardware_test_required_before_merge: true.

Nunchuk remains NOT_TESTED.

## Artifact Hashes

Artifact hashes are local observations only, not checker gates.

- `.pio/build/glyph_mk6/firmware.elf`:
  `d8c22dfd9f8b9a2b49d8dad3015c5366ebbee9b17281fcc7fc721f7e81530278`
- `.pio/build/glyph_mk6/firmware.uf2`:
  `b038ec22f3fac84014703fce5fb83241e9566b31f8cbbb1a0fad0a6845d40f83`
- `.pio/build/glyph_mk6/firmware.bin`:
  `67921688e1fee1564e8208318dcf763394f195d2e3b2f76857e31afd02509490`

`artifact_hashes_are_rebuild_stable`: `false`

`artifact_hashes_are_checker_gate`: `false`
