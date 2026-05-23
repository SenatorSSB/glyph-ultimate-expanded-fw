# G12i Custom Firmware Update-Style Plan

Status: future plan only. This is not authorization to flash hardware, copy firmware to a device, or call any custom artifact flash-ready.

## Target For First Custom Firmware

The first custom firmware candidate should be an Update-style app-only UF2:

- generated from the intended branch and commit;
- parsed read-only before hardware use;
- writes only an app range comparable to the official Update UF2;
- does not include the Clean/Fresh Install high-flash zero segment;
- does not intentionally wipe profile/config storage;
- keeps `SenscopePrototype` default-unreachable unless a human is intentionally testing a local debug build.

## Required Pre-Flash Artifact Checks

Before any human considers a custom flash, all of the following must be checked:

1. Generated UF2 exists under local build output.
2. Generated UF2 has valid UF2 magic and RP2040-compatible structure.
3. Generated UF2 has expected family ID or other source-backed RP2040-compatible metadata.
4. Generated UF2 writes only the expected app range.
5. Generated UF2 does not write the high-flash profile/config region.
6. Generated UF2 size and range are plausible compared to official `GlyphFirmware-1.0.7.uf2`.
7. Generated UF2 app payload hash is recorded.
8. Branch and commit are recorded, including dirty/clean build state.
9. Build passes from the intended branch.
10. Custom mode remains default-unreachable unless intentionally testing a debug build.

## Unacceptable First-Flash Artifacts

Do not use any first-flash artifact with any of these properties:

- Clean-style UF2 with a high-flash zero segment.
- Unknown or unparsed format.
- UF2 that writes outside the expected app range.
- Artifact whose target ranges overlap the official Clean-only high-flash segment.
- Build with config/protobuf/default activation changes not explicitly approved.
- Build with `GameModeId`, `mode_id`, `activation_binding`, or `default_mode_config` changes for `SenscopePrototype` not explicitly approved.
- Build with Force Up-B runtime behavior not explicitly approved.
- Build with digital output behavior not explicitly approved.
- Build with right-stick/C-stick behavior not explicitly approved.
- Artifact produced from a dirty tree whose differences were not inspected.

## Future Safe Read-Only Commands

These commands are appropriate for future read-only artifact inspection after a local build decision:

```bash
git status
git diff --stat
test -x ./scripts/build-glyph-mk6-quiet.sh
./scripts/build-glyph-mk6-quiet.sh
find .pio -maxdepth 5 -type f
shasum -a 256 <local-artifact.uf2>
python3 - <<'PY'
# Read-only UF2 parser over local artifact path only.
# Do not write device paths.
PY
```

The `./scripts/build-glyph-mk6-quiet.sh` wrapper runs `./scripts/pio-local.sh run -e glyph_mk6`; it does not call upload.

## Explicit Exclusions

This plan excludes:

- copy-to-device commands;
- drag-and-drop steps performed by an agent;
- PlatformIO upload commands;
- new upload or flashing scripts;
- firmware updater implementation;
- device-write commands;
- claims that custom firmware is safe to flash before artifact format, write ranges, recovery path, and rollback procedure are verified.

## Approval Boundary

A future custom flash requires explicit user approval after read-only artifact inspection. Approval for docs/source capture does not imply approval for hardware flashing.
