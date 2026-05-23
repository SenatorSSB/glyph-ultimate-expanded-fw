# G12k Safe First Custom Flash Decision Gate

Status: decision gate only. This document is not approval to flash hardware.

## Agent Rule

An agent must not flash hardware, copy firmware to `RPI-RP2`, copy firmware to any mounted device, run PlatformIO upload commands, or add upload/flashing scripts unless a future task gives explicit approval and the repo stop conditions are satisfied.

## Required Gates

Before any human considers a first custom firmware flash, all gates must be reviewed:

1. Official Update UF2 archived.
2. Official Clean UF2 archived.
3. Official restore path documented.
4. Generated custom UF2 parsed and confirmed app-only.
5. Build passes.
6. Custom branch diff inspected.
7. No default reachability, config, or protobuf activation changes.
8. `SenscopePrototype` remains unreachable unless intentionally testing a debug build.
9. No Force Up-B, digital output, right-stick, or C-stick expansion unless explicitly approved.
10. Recovery path tested or accepted with known risk.
11. Spare device preferred.
12. No tournament/main controller first if avoidable.

## Approval Levels

| Level | Meaning |
| --- | --- |
| NOT_READY | Required source, artifact, recovery, or branch-diff evidence is missing. No custom flash should occur. |
| READY_FOR_READ_ONLY_ARTIFACT_INSPECTION | Source capture is complete enough to build and inspect a generated artifact locally without device writes. |
| READY_FOR_SPARE_DEVICE_FLASH | A generated artifact is app-only, build/diff checks passed, restore path is documented, and a human explicitly approves testing on a spare device. |
| READY_FOR_MAIN_DEVICE_FLASH | Spare-device testing and recovery have passed, risk is accepted, and a human explicitly approves use on a main device. |

## Current Status

Current expected status after this docs/source capture branch:

- `READY_FOR_READ_ONLY_ARTIFACT_INSPECTION`
- Not approved for actual custom flash
- Not approved for copy-to-device
- Not approved for PlatformIO upload
- Not approved for main-device use

This status depends on the branch remaining docs/source-only and the official UF2 files remaining archived with matching hashes.

## Evidence Required To Advance

To move beyond read-only artifact inspection, a future branch must document:

- exact generated artifact path;
- generated artifact size and SHA-256;
- UF2 magic validity;
- family ID or compatible metadata;
- target ranges;
- absence of the high-flash Clean/Fresh Install wipe segment;
- successful build command and result;
- branch diff summary against `configurator`;
- grep checks showing no default reachability/config/protobuf activation changes;
- explicit human approval for any hardware action.

## Stop Conditions

Remain at `NOT_READY` or stop if:

- official Update or Clean UF2 is missing;
- custom artifact format is unknown;
- custom artifact writes outside the expected app range;
- custom artifact writes the Clean-only high-flash region unintentionally;
- branch diff includes forbidden source/header/config/protobuf/default behavior changes;
- recovery path is unknown and risk is not explicitly accepted;
- a requested step would require an agent-run device write.
