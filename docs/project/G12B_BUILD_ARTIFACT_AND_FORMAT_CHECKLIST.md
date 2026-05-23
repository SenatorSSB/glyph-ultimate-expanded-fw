# G12b Build Artifact And Format Checklist

Status: docs-only checklist. This document does not implement flashing, upload tooling, or artifact delivery.

## Purpose

Define the read-only checks required after a successful `glyph_mk6` build before anyone describes a custom firmware artifact as flash-ready or suitable for a drag-and-drop updater path.

## Safe Read-Only Command Sequence

Use only local repo/build-output inspection commands in this batch:

```bash
git status
git diff --stat
test -x ./scripts/build-glyph-mk6-quiet.sh
./scripts/build-glyph-mk6-quiet.sh
find .pio -maxdepth 5 -type f | sort
file <artifact>
ls -lh <artifact>
```

Notes:

- `<artifact>` is a placeholder for a file found under local build output, not a device path.
- Do not copy, move, or write artifacts to any mounted device in this batch.
- Do not run PlatformIO upload commands in this batch.
- Do not use a connected controller as a target from agent-run commands.

## What To Check After A Successful `glyph_mk6` Build

| Check | Required evidence | Status until checked |
| --- | --- | --- |
| Output artifact path or paths | Exact local path(s) under `.pio` or other local build output. | UNKNOWN |
| File extension or extensions | Extensions such as `.uf2`, `.bin`, `.elf`, `.hex`, `.map`, or other. | UNKNOWN |
| File size | `ls -lh <artifact>` output for each candidate firmware artifact. | UNKNOWN |
| File type | `file <artifact>` output for each candidate firmware artifact. | UNKNOWN |
| Firmware name metadata | Whether visible metadata identifies firmware name, currently source-backed as compiled from `FIRMWARE_NAME` in `platformio.ini` and `FIRMWARE_VERSION` in `builder_scripts/arduino_pico.py`; artifact-level visibility remains to be checked. | UNKNOWN |
| Device name metadata | Whether visible metadata identifies `DEVICE_NAME`, currently source-backed as `"${PIOENV}"`; artifact-level visibility remains to be checked. | UNKNOWN |
| Artifact format | Whether candidate artifact is UF2, BIN, ELF, HEX, or other. | UNKNOWN |
| Drag-and-drop updater suitability | Official evidence that the expected updater path accepts that exact artifact type and metadata. | UNKNOWN |

## Artifact Categories To Distinguish

| Artifact type | Interpretation rule |
| --- | --- |
| UF2 | Do not assume flash-ready. Confirm board/updater compatibility, metadata expectations, and official path acceptance. |
| BIN | Do not assume drag-and-drop compatible. Confirm whether the official updater or bootloader accepts raw binary and at which address/layout. |
| ELF | Treat primarily as build/debug output unless official tooling says otherwise. Do not drag-and-drop ELF to a device. |
| HEX | Treat as format-specific and unapproved unless official Glyph/RP2040 path expects it. |
| MAP/other | Treat as diagnostic/build metadata, not firmware delivery artifact, unless source-backed otherwise. |

## Evidence Needed Before Calling Any Artifact Flash-Ready

All of the following must be true before any custom artifact can be called flash-ready:

1. A successful `glyph_mk6` build was run from the intended branch/commit.
2. The working tree state was recorded, including dirty/clean status.
3. Exact candidate artifact path, name, extension, size, and hash were recorded.
4. `file <artifact>` output was recorded for the local artifact path.
5. The expected delivery path was identified from official docs, source-backed repo evidence, or explicit user-confirmed device behavior.
6. The expected artifact format for that delivery path was verified.
7. Official firmware rollback path was verified before first custom flash.
8. Config preservation/reset expectations were documented or marked unknown before first custom flash.
9. A human explicitly approved any hardware flashing step.
10. No agent-run command writes to a mounted device.

## Explicit Prohibitions For This Batch

- Do not copy artifacts to mounted devices.
- Do not drag-and-drop artifacts from an agent workflow.
- Do not run `pio run --target upload` or equivalent upload commands.
- Do not add upload scripts.
- Do not add updater code.
- Do not describe an artifact as UF2/BIN compatible until local build evidence and official updater expectations are both documented.

## Stop Conditions

Stop if:

- the build fails;
- no artifact path can be identified;
- artifact format is unknown;
- official updater/connect-mode expectations are unknown;
- official rollback path is unavailable or unverified;
- a requested command would write to a mounted device;
- source/header/config/protobuf/default runtime reachability changes appear in the working tree unexpectedly.
