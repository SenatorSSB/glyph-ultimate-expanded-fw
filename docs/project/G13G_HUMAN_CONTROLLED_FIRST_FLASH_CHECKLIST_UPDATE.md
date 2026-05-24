# G13g Human-Controlled First Flash Checklist Update

Status: future human checklist update only. This is not approval to flash hardware.

This document updates the first-flash decision checklist using the read-only artifact facts from `docs/project/G13F_PLAYTEST_BUILD_ARTIFACT_INSPECTION.md`, the decision gate from `docs/project/G12K_SAFE_FIRST_CUSTOM_FLASH_DECISION_GATE.md`, and the archived official Glyph 1.0.7 Update/Clean UF2 references under `docs/sources/raw/glyph_firmware_uf2/1.0.7/`.

## Agent Must Not Flash

An agent must not flash hardware, copy firmware to `RPI-RP2`, copy firmware to any mounted device, run PlatformIO upload commands, or add upload/flashing scripts unless a future task gives explicit approval and all repo stop conditions are satisfied.

## Preconditions Before First Spare-Device Flash Consideration

All preconditions must be reviewed by a human before any future spare-device flash is considered:

1. Normal `glyph_mk6` build passes.
2. Playtest `glyph_mk6_senscope_playtest` build passes.
3. Playtest UF2 is parsed.
4. Playtest UF2 is classified as an app-only Update-style candidate.
5. Official Update UF2 is archived.
6. Official Clean UF2 is archived.
7. Recovery path is known or risk is explicitly accepted.
8. Branch diff is reviewed.
9. No default reachability, config, or protobuf activation changes are present.
10. No Force/digital/right-stick/C-stick expansion is present.
11. No export/push/upload workflow is present.
12. Spare device is preferred.
13. No main/tournament controller first if avoidable.

## Current Evidence Snapshot

| Gate | Current evidence from this batch |
| --- | --- |
| Normal build | Passed in G13F. |
| Playtest build | Passed in G13F. |
| Playtest UF2 parsed | Parsed by existing read-only `tools/uf2/inspect_uf2.py`. |
| Playtest UF2 app-only candidate | Classified in G13F as `UPDATE_STYLE_APP_ONLY_CANDIDATE`. |
| Official Update archived | `GlyphFirmware-1.0.7.uf2`, manifest hash `2fe38be67b68b9f8b9cb8be2f338837785e63a3732e0c1c269380f6c48f70c6d`. |
| Official Clean archived | `GlyphFirmware-1.0.7-Clean.uf2`, manifest hash `22fd7f8f29fb33d9cb601187e9503411e5330e72c7297fbce0df710eec8ff200`. |
| Official Update range | `0x10000000..0x1005df00`. |
| Official Clean high-flash wipe range | `0x1017f000..0x101ff000`. |
| Generated playtest range | `0x10000000..0x1005fc00`; no Clean high-flash overlap. |

Even with this evidence, flashing still requires explicit future human approval.

## Observations To Record After A Future Human Flash

If a future human-approved spare-device flash is performed, record these observations exactly:

| Area | Observation to record |
| --- | --- |
| Boot | Device boots. |
| Menu | Menu works. |
| Display | Mini-screen/OLED works. |
| Normal mode | Normal controller mode works. |
| Configurator | Configurator still connects if tested. |
| Update mode | Menu/firmware update path still reaches `RPI-RP2` if tested. |
| Manual selection | `SenscopePrototype` manual chord selection behavior. |
| Left stick | Left-stick output sanity. |
| Digital neutral | Digital outputs remain neutral in `SenscopePrototype`. |
| Force | Force disabled. |
| Right-stick/C-stick | Right-stick/C-stick centered. |
| Triggers | Triggers zero. |

## Stop Conditions

Stop before any flash, or stop future testing immediately after a human flash, if any of these occur:

- artifact is not app-only;
- any high-flash wipe segment is present;
- no rollback path exists and risk has not been explicitly accepted;
- unexpected source/config/protobuf changes appear;
- unstable USB enumeration occurs;
- profiles are wiped unexpectedly;
- update mode is inaccessible;
- normal firmware functions fail;
- branch diff includes default reachability, config, protobuf, or activation changes;
- Force/digital/right-stick/C-stick behavior expanded unexpectedly;
- any step would require an agent to flash or write a mounted device.

## Future Approval Boundary

The next possible hardware-facing step is not automatic. It must be a separately approved human-controlled spare-device protocol, with the artifact path, hash, range classification, rollback path, and expected observations reviewed before the human acts.
