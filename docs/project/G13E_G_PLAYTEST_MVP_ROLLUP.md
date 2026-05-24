# G13e-g Playtest MVP Rollup

Status: rollup for G13e through G13g. This is not approval to flash hardware.

## Created Docs

- `docs/project/G13E_LEFT_STICK_EXACT_TABLE_PLAYTEST_PROFILE.md`
- `docs/project/G13F_PLAYTEST_BUILD_ARTIFACT_INSPECTION.md`
- `docs/project/G13G_HUMAN_CONTROLLED_FIRST_FLASH_CHECKLIST_UPDATE.md`
- `docs/project/G13E_G_PLAYTEST_MVP_ROLLUP.md`

## Tooling

Optional UF2 parser tool was not added in this batch. Existing read-only tooling was reused:

```text
tools/uf2/inspect_uf2.py
```

## Build Results

| Build | Result |
| --- | --- |
| Normal `glyph_mk6` | Passed |
| Playtest `glyph_mk6_senscope_playtest` | Passed |

## Generated Playtest Artifact Classification

Generated playtest UF2 path inspected:

```text
.pio/build/glyph_mk6_senscope_playtest/firmware.uf2
```

Classification:

```text
UPDATE_STYLE_APP_ONLY_CANDIDATE
```

This is not approval to flash. It only supports future human review.

## Source And Runtime Boundaries

- No generated artifacts were committed.
- No source/header/config/protobuf files were changed in this batch.
- No runtime/default reachability changed for normal `glyph_mk6`.
- Experimental env remains opt-in through `glyph_mk6_senscope_playtest`.
- No Force/digital/right-stick/C-stick behavior changed.
- No export/push/upload/flashing workflow was added.
- No hardware flashing was performed.
- No `GameModeId`, `mode_id`, `activation_binding`, or `default_mode_config` behavior was added.
- No gameplay semantic labels, thresholds, or SSBU behavior claims were added.

## Artifact Summary

| Env | Generated UF2 | Range | Clean high-flash overlap | Classification |
| --- | --- | --- | ---: | --- |
| `glyph_mk6` | `.pio/build/glyph_mk6/firmware.uf2` | `0x10000000..0x1005fb00` | No | Normal generated app-only candidate for comparison |
| `glyph_mk6_senscope_playtest` | `.pio/build/glyph_mk6_senscope_playtest/firmware.uf2` | `0x10000000..0x1005fc00` | No | `UPDATE_STYLE_APP_ONLY_CANDIDATE` |

Official reference ranges:

| Official artifact | Range(s) |
| --- | --- |
| `GlyphFirmware-1.0.7.uf2` | `0x10000000..0x1005df00` |
| `GlyphFirmware-1.0.7-Clean.uf2` | `0x10000000..0x1005df00`; `0x1017f000..0x101ff000` |

## Recommended Next Options

A. G13h selected playtest profile refinement docs/code only after user supplies desired raw table.
B. G13i spare-device flash protocol only after explicit user approval.
C. G13j manual selection UX/checklist refinement.
D. Return to Senscope app-side evaluator implementation.
