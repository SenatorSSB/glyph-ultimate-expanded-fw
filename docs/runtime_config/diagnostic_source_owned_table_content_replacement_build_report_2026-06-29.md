# Diagnostic Source-Owned Table Content Replacement Build Report

Status label: LOCAL BUILD REPORT.

Branch:
`runtime-config-diagnostic-source-owned-table-content-replacement`

Canonical command:

```bash
pio run -e glyph_mk6
```

Fallback used locally:

```bash
./scripts/build-glyph-mk6-quiet.sh
```

## Source Summary

- Changed source file:
  `src/modes/UltimateIdentityRuntimeTables.hpp`
- Changed table point:
  `kRT1RF4CustomTable[4]` from `(128, 128)` to `(129, 128)`
- Active view selection changed: `false`
- `RuntimeConfigView` path changed: `false`
- Runtime-loaded config/storage/write/WebSerial/flashing/backend config.pb
  behavior implemented: `false`
- Nunchuk status: `NOT_TESTED`

## Artifact Hashes

Artifact hashes are local observations only.

- `artifact_hashes_are_rebuild_stable`: `false`
- `artifact_hashes_are_checker_gate`: `false`
- build result: PASS via fallback command because `pio` was unavailable in PATH.

Observed local artifact hashes:

| Artifact | SHA-256 |
| --- | --- |
| `.pio/build/glyph_mk6/firmware.elf` | `e39397163c4c42f8097e3ee5236ecbf8f1cc5d45201b20808b17a5820d05b73f` |
| `.pio/build/glyph_mk6/firmware.uf2` | `94b4767097577c6e7ea6cb6fdcd8f94d6d2eda1eb7e940451cf1afca297a9d67` |
| `.pio/build/glyph_mk6/firmware.bin` | `f3d52b99e7feff20d42d562f42caca71d7bf976c20f2a1779dcb2d3b2287b7b9` |
