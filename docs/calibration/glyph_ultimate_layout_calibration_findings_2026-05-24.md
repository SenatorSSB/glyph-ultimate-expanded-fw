# Glyph Ultimate Everything-Layout Calibration Findings

Date: 2026-05-24  
Scope: Glyph/HayBox-side backend/configurator calibration evidence for Senscope integration planning  

## 1. Purpose

This document records physical-button calibration evidence for Glyph `Ultimate` mode using `LAYOUT_PLATE_EVERYTHING`.

This is documentation and calibration evidence only. It does not change firmware behavior.

## 2. Source files

- `docs/calibration/fixtures/GlyphUserProfilesUlt-filled.json`
- `docs/calibration/fixtures/GlyphUltFilled2.json`

## 3. Source distinction

- `physicalButton` = physical location ID on the Glyph plate
- `activates` = logical output/action triggered by that physical button
- `socdPairs` = profile-specific physical opposite-direction pair configuration

Important rule for integration work: omitted `activates` must be preserved as omitted/unknown/default. Omitted `activates` must not be treated as disabled unless configurator/firmware source explicitly proves that behavior.

## 4. Prefix interpretation

- `LF` = left finger cluster
- `LT` = left thumb cluster
- `RF` = right-side/right-finger cluster
- `RT` = right thumb cluster
- `MB` = menu button family

Cluster interpretation is high confidence from repeated remap/SOCD behavior. Exact per-button pixel mapping remains out of scope.

## 5. Calibration 1 (Ultimate) SOCD pairs

From `GlyphUserProfilesUlt-filled.json`:

1. `BTN_LF3` + `BTN_LF1`, `SOCD_2IP`
2. `BTN_LF2` + `BTN_RF4`, `SOCD_2IP`
3. `BTN_RT3` + `BTN_RT5`, `SOCD_2IP`
4. `BTN_RT2` + `BTN_RT4`, `SOCD_2IP`
5. `BTN_LF8` + `BTN_LF6`, omitted `socdType`
6. `BTN_RF7` + `BTN_RF8`, omitted `socdType`

## 6. Calibration 2 (Ultimate) SOCD pairs

From `GlyphUltFilled2.json`:

1. `BTN_LF3` + `BTN_LF1`, `SOCD_2IP`
2. `BTN_RT3` + `BTN_RT5`, `SOCD_2IP`
3. `BTN_RT2` + `BTN_RT4`, `SOCD_2IP`
4. `BTN_LF8` + `BTN_LF6`, omitted `socdType`

## 7. Important conclusion

- SOCD pairs are profile-specific configuration, not universal fixed layout metadata.
- `BTN_LF2` + `BTN_RF4` and `BTN_RF7` + `BTN_RF8` appear in some/default/calibration profiles but are absent in Ultimate calibration 2.
- `BTN_RT3` + `BTN_RT5` and `BTN_RT2` + `BTN_RT4` are strong primary right-stick/C-stick pair anchors.
- `BTN_LF3` + `BTN_LF1` is a strong recurring left-axis pair.
- `BTN_LF8` + `BTN_LF6` is a secondary left-finger axis pair in Ultimate calibration 2.

## 8. Calibration 1 remap table

| Physical | Activates |
|---|---|
| `BTN_LF2` | `BTN_RF4` |
| `BTN_LF4` | `BTN_RF1` |
| `BTN_RF1` | `BTN_RT1` |
| `BTN_RF3` | `BTN_LT1` |
| `BTN_RF4` | `BTN_LT2` |
| `BTN_RF6` | `BTN_RF4` |
| `BTN_RT1` | `BTN_RF3` |
| `BTN_LF5` | `BTN_LF2` |
| `BTN_RF9` | `BTN_RF1` |
| `BTN_LT3` | `BTN_LF8` |
| `BTN_LT4` | `BTN_LF6` |
| `BTN_LT5` | `BTN_RT3` |
| `BTN_LF8` | `BTN_RT3` |
| `BTN_LT6` | `BTN_MB7` |
| `BTN_LF7` | `BTN_RT5` |
| `BTN_LF6` | `BTN_RT2` |
| `BTN_RF10` | `BTN_RT4` |
| `BTN_RF16` | `BTN_RF8` |
| `BTN_RF13` | `BTN_RF7` |
| `BTN_RF14` | `BTN_RF3` |
| `BTN_RF15` | `BTN_RF6` |
| `BTN_MB1` | omitted |
| `BTN_MB2` | omitted |
| `BTN_MB3` | omitted |

## 9. Calibration 2 remap table

| Physical | Activates |
|---|---|
| `BTN_LF1` | `BTN_LF3` |
| `BTN_LF2` | `BTN_LF8` |
| `BTN_LF3` | `BTN_LF1` |
| `BTN_LF4` | `BTN_RT1` |
| `BTN_RF1` | `BTN_RT1` |
| `BTN_RF3` | `BTN_RT5` |
| `BTN_RF4` | `BTN_RT3` |
| `BTN_RF5` | `BTN_RF6` |
| `BTN_RF6` | `BTN_LF2` |
| `BTN_RF7` | `BTN_LF6` |
| `BTN_RF8` | `BTN_RF3` |
| `BTN_RT1` | `BTN_RF3` |
| `BTN_LF5` | `BTN_LF3` |
| `BTN_RF12` | `BTN_RT4` |
| `BTN_RF11` | `BTN_MB7` |
| `BTN_LT5` | `BTN_RT5` |
| `BTN_LF8` | `BTN_LF4` |
| `BTN_LT6` | `BTN_RF3` |
| `BTN_LF7` | `BTN_RF5` |
| `BTN_LF6` | `BTN_RT1` |
| `BTN_RF10` | `BTN_RF1` |
| `BTN_RF16` | `BTN_RF8` |
| `BTN_RF13` | `BTN_LT1` |
| `BTN_RF14` | `BTN_LT2` |
| `BTN_RF15` | `BTN_RT1` |
| `BTN_MB1` | omitted |
| `BTN_MB2` | omitted |
| `BTN_MB3` | omitted |

## 10. Physical button universe observed

- `BTN_LF1..BTN_LF8`
- `BTN_LT1..BTN_LT6` as logical/physical family, with `LT3..LT6` observed as physical remap entries in calibration 1 and `LT5/LT6` in calibration 2
- `BTN_RF1..BTN_RF16`
- `BTN_RT1..BTN_RT5`
- `BTN_MB1..BTN_MB3` as physical menu entries
- `BTN_MB7` as a logical Start-like target observed in remaps

## 11. Physical-location confidence notes

- Cluster-level interpretation is high confidence.
- SOCD directional groups are high confidence where profile pairs explicitly exist.
- Exact pixel-perfect visual coordinates for every `RF/LF/LT/RT` member are out of scope without configurator layout source.
- Static screenshots support visual-region inference but are not firmware truth.
