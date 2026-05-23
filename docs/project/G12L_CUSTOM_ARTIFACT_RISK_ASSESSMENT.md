# G12l Custom Artifact Risk Assessment

Status: docs-only risk assessment based on read-only generated artifact inspection. No flashing, upload command, copy-to-device command, mounted-device write, or hardware write was performed.

## Scope

This assessment uses:

- the clean `glyph_mk6` inspection build recorded in `G12L_GENERATED_UF2_ARTIFACT_INSPECTION.md`;
- archived official Glyph 1.0.7 Update and Clean/Fresh Install UF2 files;
- read-only UF2 parsing by `tools/uf2/inspect_uf2.py`;
- branch diff and grep checks against firmware/source/config surfaces.

This assessment does not approve hardware flashing. An app-only generated UF2 is only a candidate for future human-controlled spare-device review after explicit approval.

## Risk Matrix

| Risk | Status | Evidence | Required mitigation |
| --- | --- | --- | --- |
| 1. Wrong artifact format | PASS | The generated candidate `.pio/build/glyph_mk6/firmware.uf2` parsed as valid UF2 with valid magic on 1,531 / 1,531 blocks; `file` reported "UF2 firmware image, family Raspberry Pi RP2040". | Keep parsing every generated candidate before any hardware decision; do not infer drag-and-drop compatibility from `.bin` or `.elf` side artifacts. |
| 2. Clean-style profile wipe segment | PASS | Generated UF2 target range is `0x10000000..0x1005fb00`; it does not overlap official Clean-only `0x1017f000..0x101ff000`; no all-zero segment was present. | Reject or require explicit wipe approval for any future artifact that writes `0x1017f000..0x101ff000` or any all-zero high-flash segment. |
| 3. Unexpected target ranges | PASS | Generated UF2 starts at `0x10000000`, ends at `0x1005fb00`, and remains below the local app/sketch limit `0x1017f000` documented in `G12N_REPO_TO_UF2_STORAGE_LAYOUT_MAPPING.md`. It extends 7,168 bytes beyond the archived official Update app end, but remains app-like. | Continue comparing generated ranges to both the exact official Update range and the local app/sketch window; stop on any filesystem/EEPROM overlap or unexplained target range. |
| 4. Dirty build tree | PASS for inspected artifact; UNKNOWN for later rebuilds until rechecked | The inspected artifact was built at commit `52d54d16e6a057f8373cdce8eb31129a29cf0453` with `git status --short` clean. The build system embeds Git hash and dirty state, so later docs/tooling edits can alter firmware bytes without firmware source changes. | Record branch, commit, dirty status, SHA-256, and parser output for each candidate. Rebuild and reparse after any future source-bearing commit chosen for review. |
| 5. Source diff touching preservation-critical files | PASS | This branch adds docs and a read-only local parser. It does not modify firmware source/header/config/protobuf/default activation files, `src/core/mode_selection.cpp`, or `src/modes/SenscopePrototype.cpp`. | Before any later hardware decision, compare against `configurator` and reject unapproved diffs touching preservation-critical firmware, config, protobuf, defaults, mode reachability, or behavior surfaces. |
| 6. Bootloader/update path uncertainty | UNKNOWN | Prior docs record source-backed bootloader-entry code paths and official update procedure evidence, but this batch performed no hardware or update-mode observation. | Add G12M official update-mode recovery verification checklist and perform only human-approved, non-agent hardware verification when appropriate. |
| 7. Official rollback not tested | UNKNOWN | Official Update and Clean UF2 files are archived and hashed, but no restore or rollback was tested in this batch. | Verify official recovery/rollback path on an explicitly approved device before relying on custom firmware recoverability. |
| 8. Generated artifact not equivalent to official release feature set | UNKNOWN | Generated UF2 app payload SHA-256 differs from official Update, range is larger by 7,168 bytes, and the repo may not exactly match official downstream release provenance. This is expected for a custom build, but equivalence is not proven. | Treat generated firmware as custom, not official-equivalent. Future review may compare strings, symbols, map/layout metadata, and feature surfaces before any hardware choice. |

## Decision Gate

Current decision-gate status remains:

```text
READY_FOR_READ_ONLY_ARTIFACT_INSPECTION
```

The generated UF2 is an `UPDATE_STYLE_APP_ONLY_CANDIDATE`, but this does not advance the gate to hardware approval. The candidate may be considered for future human-controlled spare-device review after explicit approval, recovery-path review, and any additional checklist items the reviewer requires.

## Explicit Non-Approvals

- No custom artifact is approved to flash.
- No copy to `RPI-RP2` is approved.
- No copy to any mounted device is approved.
- No PlatformIO upload command is approved.
- No upload/flashing workflow is added or approved.
- No main-device use is approved.
