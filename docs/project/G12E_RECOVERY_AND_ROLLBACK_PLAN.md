# G12e Recovery And Rollback Plan

Status: docs-only rollback planning. This document does not implement rollback tooling, firmware upload, flashing, or updater workflow.

## Purpose

Define recovery planning layers that must be understood before any future first custom firmware test on Glyph hardware.

## Rollback Planning Layers

| Layer | Status | Plan |
| --- | --- | --- |
| Git rollback | SOURCE_BACKED/POLICY | Use normal Git history and forward commits only. Do not use forbidden commands such as `git reset`, `git clean`, `git stash`, `git revert`, or force push under this repo task policy. |
| Firmware rollback to official firmware | UNKNOWN | Must use a verified, user-controlled path with an official firmware file available locally before any first custom flash. |
| Config preservation/restore | SOURCE_BACKED/UNKNOWN | Repo source shows runtime config stored via LittleFS `config.bin` with CRC. Whether official firmware update/rollback preserves or resets it is UNKNOWN. |
| Hardware bootloader fallback | SOURCE_BACKED/UNKNOWN | Repo source shows a configurator command path to reboot bootloader. Physical fallback procedure and expected artifact format are UNKNOWN until verified. |

## Evidence Needed Before First Custom Flash

1. Official firmware source/download location.
2. Official firmware file stored locally and identified by name/hash/size.
3. Official updater/connect-mode behavior documented from official docs/source or user-confirmed device evidence.
4. Bootloader fallback procedure documented from official resources or source-backed hardware guidance.
5. Accepted artifact format and expected delivery path documented.
6. Whether user config is preserved, reset, or must be backed up/ restored manually.
7. Known behavior when incompatible or corrupt firmware is supplied.
8. Criteria for confirming official firmware restore succeeded.

## Do Not Rely On Unverified Recovery

Do not rely on an unverified rollback path before first custom flash.

If official firmware restoration has not been documented and rehearsed by a human-controlled, verified path, stop before custom firmware flashing.

## Git-Side Recovery Policy

Allowed recovery approach for repository changes:

- add forward corrective commits;
- branch from known good refs;
- compare with `configurator`;
- preserve normal Git history.

Forbidden under this task policy:

- `git reset`;
- `git clean`;
- `git stash`;
- `git revert`;
- force push;
- broad unrelated rewrites.

## Firmware-Side Recovery Unknowns

These remain unknown until official evidence is captured:

- whether official connect mode accepts UF2, BIN, or another file format;
- whether official connect mode verifies firmware identity or board target;
- whether official firmware can be restored through the same connect mode;
- whether a physical bootloader fallback is always available;
- whether LittleFS config survives custom firmware, official rollback, or bootloader-level recovery.

## Stop Conditions

Stop if:

- official firmware file cannot be obtained;
- official restore path is unknown;
- artifact format is unknown;
- config preservation expectations matter but are unknown;
- any recovery step would require agent-run device writes;
- any rollback plan depends on undocumented behavior as fact.
