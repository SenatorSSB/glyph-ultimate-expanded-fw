# G12g-k UF2 Source And Delivery Rollup

Status: docs/source-only rollup. No hardware flashing, device write, uploader, updater, runtime default reachability, or gameplay-semantic change is included.

## Created Docs And Source Files

Docs added:

- `docs/sources/raw/glyph_firmware_uf2/1.0.7/README.md`
- `docs/sources/raw/glyph_firmware_uf2/1.0.7/manifest.json`
- `docs/project/G12G_OFFICIAL_UF2_SOURCE_CAPTURE.md`
- `docs/project/G12H_UF2_FORMAT_AND_FLASH_RANGE_ANALYSIS.md`
- `docs/project/G12I_CUSTOM_FIRMWARE_UPDATE_STYLE_PLAN.md`
- `docs/project/G12J_GLYPH_FUNCTION_PRESERVATION_RISK_AUDIT.md`
- `docs/project/G12K_SAFE_FIRST_CUSTOM_FLASH_DECISION_GATE.md`
- `docs/project/G12G_K_UF2_SOURCE_AND_DELIVERY_ROLLUP.md`

Raw source files added:

- `docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7.uf2`
- `docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7-Clean.uf2`

UF2 files were available to the agent and were added as user-provided official raw source artifacts.

## Hashes

| File | SHA-256 |
| --- | --- |
| `GlyphFirmware-1.0.7.uf2` | `2fe38be67b68b9f8b9cb8be2f338837785e63a3732e0c1c269380f6c48f70c6d` |
| `GlyphFirmware-1.0.7-Clean.uf2` | `22fd7f8f29fb33d9cb601187e9503411e5330e72c7297fbce0df710eec8ff200` |

## Main Insights

- The user-provided official update procedure uses `.uf2` firmware files.
- The user-provided official update procedure says the programming volume appears as `RPI-RP2`.
- `RPI-RP2` strongly suggests RP2040 UF2 programming mode.
- The inspected repo also has Pico/RP2040 build configuration and source paths that call `rp2040.rebootToBootloader()`.
- The official Update and Clean/Fresh Install files are valid UF2 images with family ID `0xe48bff56`.
- Update vs Clean differ by a Clean-only high-flash all-zero segment.
- The shared app segment is byte-identical in both official files.
- First custom firmware should be Update-style app-only.
- Clean/Fresh Install-style artifacts should be avoided unless profile/config wipe is intended and explicitly approved.

## Range Summary

| Artifact | Ranges | Notes |
| --- | --- | --- |
| Update UF2 | `0x10000000..0x1005df00` | App-only, 384,768 payload bytes. |
| Clean UF2 | `0x10000000..0x1005df00`; `0x1017f000..0x101ff000` | Same app segment plus 524,288 all-zero bytes in the Clean-only high-flash segment. |

## Boundaries Held

- No source/header/config/protobuf files changed.
- No runtime/default reachability changed.
- No Force Up-B behavior changed.
- No digital output behavior changed.
- No right-stick/C-stick behavior changed.
- No upload/flashing workflow was added.
- No hardware flashing was performed.
- No gameplay semantic claims were added.
- Official connect/update behavior is captured as user-provided evidence plus read-only UF2 inspection and repo-source context; RP2040 BOOTSEL behavior remains partly inferred unless corroborated by official docs or hardware verification.

## Recommended Next Branches

A. `G12L` generated custom UF2 artifact inspection after a local build.
B. `G12M` official update-mode recovery verification checklist.
C. `G12N` first spare-device custom flash protocol only after explicit user approval.
D. `G11p/G11q` runtime implementation only after explicit user approval.

## Follow-Up Research Added

Additional docs-only research was added on this branch after the initial source capture:

- `docs/project/G12L_DEEP_UF2_STRUCTURAL_AUDIT.md`
- `docs/project/G12M_OFFICIAL_SOURCE_CORROBORATION.md`
- `docs/project/G12N_REPO_TO_UF2_STORAGE_LAYOUT_MAPPING.md`
- `docs/project/G12O_OFFICIAL_FIRMWARE_PAYLOAD_STRING_AUDIT.md`
- `docs/project/G12P_GENERATED_ARTIFACT_COMPARISON.md`
- `docs/project/G12Q_RECOVERY_PATH_RESEARCH_CHECKLIST.md`

New high-signal confirmations:

- Official Limit Labs resources independently corroborate the update procedure, `RPI-RP2`, `.uf2`, Update/Fresh Install distinction, `v1.0.7 (9a78c7e)`, and April 19, 2026 release date.
- The Glyph manual provides additional official evidence for Manual FW Update mode and a physical BOOTSEL button, though hardware accessibility still needs human review.
- RP2040 official docs corroborate `RPI-RP2`, UF2 copy/eject/reboot behavior, ROM-resident BOOTSEL, family ID `0xe48bff56`, and invalid-UF2 risk.
- Official UF2 blocks are structurally consistent: valid magic, `flags=0x2000`, 256-byte payloads, no missing or duplicate block numbers.
- Clean’s `0x1017f000..0x101ff000` all-zero segment exactly matches the locally generated `glyph_mk6` LittleFS region.
- Official app payload embeds `9a78c7e`, `glyph_mk6`, and `HayBox`; `9a78c7e` resolves to tag `1.0.7` in this clone.
- A local read-only `glyph_mk6` build passed and generated an app-only RP2040 UF2 at `0x10000000..0x1005fb00`; it does not include the Clean high-flash wipe segment.

Updated current posture:

- The branch is stronger than initial source capture: it is now ready for read-only generated-artifact review discussions.
- It remains not approved for hardware flashing.
- Recovery trust level is `SOURCE_PLAUSIBLE`, not `SPARE_DEVICE_OBSERVED`.
- First custom firmware should still be Update-style app-only and spare-device-only after explicit approval.
