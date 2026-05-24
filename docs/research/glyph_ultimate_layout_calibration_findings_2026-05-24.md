# Glyph Ultimate Everything Layout Calibration Findings

Date: 2026-05-24  
Project: Senscope / Glyph backend realization  
Sources:
- `GlyphUserProfilesUlt-filled.json`
- `GlyphUltFilled2.json`
- Visual calibration screenshots from the Glyph configurator:
  - first filled Ultimate layout
  - Melee default layout
  - GameCube default layout
  - second filled Ultimate layout

## 1. Purpose

This document records the inferred Glyph physical button model for the `LAYOUT_PLATE_EVERYTHING` layout, using two deliberately varied Ultimate calibration profiles and visual screenshots.

The goal is not to define gameplay semantics. The goal is to establish a reliable enough physical-button inventory and calibration fixture set for future Senscope/Glyph adapter work.

This document should be treated as a calibration/evidence note, not as firmware source authority.

## 2. Core distinction

Glyph JSON separates at least these concepts:

```text
physicalButton = physical location ID on the Glyph plate
activates      = logical button/output/action that physical button triggers
socdPairs      = physical opposite-direction pair configuration
```

Therefore, the same physical button can show a different visual icon between calibration profiles because its `activates` target changed.

Omitted `activates` fields must not be casually interpreted as disabled. In the observed JSON, entries such as `{ "physicalButton": "BTN_MB1" }` mean that the button exists in the profile's remap list but has no explicit remap target in that object. Firmware/configurator behavior for omitted `activates` should be verified before treating this as identity, default, or unset.

## 3. Cluster prefix interpretation

The observed IDs strongly support the following cluster interpretation:

| Prefix | Likely physical cluster | Confidence | Notes |
|---|---|---:|---|
| `LF` | Left finger cluster | High | Left-side/finger button family. |
| `LT` | Left thumb cluster | High | Lower-left/thumb button family. |
| `RF` | Right finger / right-side cluster | High | Large right/center-right non-thumb family. |
| `RT` | Right thumb cluster | High | Lower-right/thumb C-stick/right-stick family. |
| `MB` | Menu button family | High | Menu/system/start-style physical or logical family. |

`RF` should not be overinterpreted as only one visible right-hand cluster. In the Everything layout it covers a broad right/center physical bank.

## 4. Calibration profile 1 — Ultimate remaps

Source file: `GlyphUserProfilesUlt-filled.json`

Ultimate SOCD pairs:

```json
[
  { "buttonDir1": "BTN_LF3", "buttonDir2": "BTN_LF1", "socdType": "SOCD_2IP" },
  { "buttonDir1": "BTN_LF2", "buttonDir2": "BTN_RF4", "socdType": "SOCD_2IP" },
  { "buttonDir1": "BTN_RT3", "buttonDir2": "BTN_RT5", "socdType": "SOCD_2IP" },
  { "buttonDir1": "BTN_RT2", "buttonDir2": "BTN_RT4", "socdType": "SOCD_2IP" },
  { "buttonDir1": "BTN_LF8", "buttonDir2": "BTN_LF6" },
  { "buttonDir1": "BTN_RF7", "buttonDir2": "BTN_RF8" }
]
```

Ultimate physical remaps:

| Physical ID | Activates |
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

## 5. Calibration profile 2 — Ultimate remaps

Source file: `GlyphUltFilled2.json`

Ultimate SOCD pairs:

```json
[
  { "buttonDir1": "BTN_LF3", "buttonDir2": "BTN_LF1", "socdType": "SOCD_2IP" },
  { "buttonDir1": "BTN_RT3", "buttonDir2": "BTN_RT5", "socdType": "SOCD_2IP" },
  { "buttonDir1": "BTN_RT2", "buttonDir2": "BTN_RT4", "socdType": "SOCD_2IP" },
  { "buttonDir1": "BTN_LF8", "buttonDir2": "BTN_LF6" }
]
```

Ultimate physical remaps:

| Physical ID | Activates |
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

## 6. Calibration 1 → 2 delta

| Physical ID | Calibration 1 activates | Calibration 2 activates |
|---|---|---|
| `BTN_LF1` | omitted | `BTN_LF3` |
| `BTN_LF2` | `BTN_RF4` | `BTN_LF8` |
| `BTN_LF3` | omitted | `BTN_LF1` |
| `BTN_LF4` | `BTN_RF1` | `BTN_RT1` |
| `BTN_LF5` | `BTN_LF2` | `BTN_LF3` |
| `BTN_LF6` | `BTN_RT2` | `BTN_RT1` |
| `BTN_LF7` | `BTN_RT5` | `BTN_RF5` |
| `BTN_LF8` | `BTN_RT3` | `BTN_LF4` |
| `BTN_LT3` | `BTN_LF8` | omitted |
| `BTN_LT4` | `BTN_LF6` | omitted |
| `BTN_LT5` | `BTN_RT3` | `BTN_RT5` |
| `BTN_LT6` | `BTN_MB7` | `BTN_RF3` |
| `BTN_RF3` | `BTN_LT1` | `BTN_RT5` |
| `BTN_RF4` | `BTN_LT2` | `BTN_RT3` |
| `BTN_RF5` | omitted | `BTN_RF6` |
| `BTN_RF6` | `BTN_RF4` | `BTN_LF2` |
| `BTN_RF7` | omitted | `BTN_LF6` |
| `BTN_RF8` | omitted | `BTN_RF3` |
| `BTN_RF9` | `BTN_RF1` | omitted |
| `BTN_RF10` | `BTN_RT4` | `BTN_RF1` |
| `BTN_RF11` | omitted | `BTN_MB7` |
| `BTN_RF12` | omitted | `BTN_RT4` |
| `BTN_RF13` | `BTN_RF7` | `BTN_LT1` |
| `BTN_RF14` | `BTN_RF3` | `BTN_LT2` |
| `BTN_RF15` | `BTN_RF6` | `BTN_RT1` |

Unchanged between the two calibrations:

| Physical ID | Activates |
|---|---|
| `BTN_RF1` | `BTN_RT1` |
| `BTN_RT1` | `BTN_RF3` |
| `BTN_RF16` | `BTN_RF8` |
| `BTN_MB1` | omitted |
| `BTN_MB2` | omitted |
| `BTN_MB3` | omitted |

## 7. Physical button universe

The combined calibration evidence implies this physical button universe for the Everything layout:

```ts
export type GlyphPhysicalButtonId =
  | "BTN_LF1" | "BTN_LF2" | "BTN_LF3" | "BTN_LF4"
  | "BTN_LF5" | "BTN_LF6" | "BTN_LF7" | "BTN_LF8"
  | "BTN_LT1" | "BTN_LT2" | "BTN_LT3" | "BTN_LT4" | "BTN_LT5" | "BTN_LT6"
  | "BTN_RF1" | "BTN_RF2" | "BTN_RF3" | "BTN_RF4"
  | "BTN_RF5" | "BTN_RF6" | "BTN_RF7" | "BTN_RF8"
  | "BTN_RF9" | "BTN_RF10" | "BTN_RF11" | "BTN_RF12"
  | "BTN_RF13" | "BTN_RF14" | "BTN_RF15" | "BTN_RF16"
  | "BTN_RT1" | "BTN_RT2" | "BTN_RT3" | "BTN_RT4" | "BTN_RT5"
  | "BTN_MB1" | "BTN_MB2" | "BTN_MB3" | "BTN_MB7";
```

Note: `BTN_MB7` appears as an `activates` target for start-style behavior. It is not confirmed as a visible physical button in the same way as `BTN_MB1..BTN_MB3`.

## 8. Profile-dependent SOCD behavior

SOCD pairs must be modeled as profile/config data, not fixed universal layout metadata.

```ts
export const glyphSocdPairsByCalibration = {
  ultimateCalibration1: [
    ["BTN_LF3", "BTN_LF1"],
    ["BTN_LF2", "BTN_RF4"],
    ["BTN_RT3", "BTN_RT5"],
    ["BTN_RT2", "BTN_RT4"],
    ["BTN_LF8", "BTN_LF6"],
    ["BTN_RF7", "BTN_RF8"],
  ],
  ultimateCalibration2: [
    ["BTN_LF3", "BTN_LF1"],
    ["BTN_RT3", "BTN_RT5"],
    ["BTN_RT2", "BTN_RT4"],
    ["BTN_LF8", "BTN_LF6"],
  ],
} as const;
```

This supersedes the earlier assumption that `BTN_LF2` + `BTN_RF4` is always present in the current Ultimate profile.

## 9. Stable directional groups

### 9.1 Left-stick / left-axis evidence

High-confidence recurrent pair:

```ts
leftAxisPair = ["BTN_LF3", "BTN_LF1"] as const;
```

Profile-dependent/default pair:

```ts
legacyOrDefaultLeftAxisPair = ["BTN_LF2", "BTN_RF4"] as const;
```

The second pair is present in default and calibration 1 style profiles but absent from calibration 2 Ultimate.

### 9.2 Right-stick / C-stick primary evidence

High-confidence primary C-stick/right-stick direction pairs:

```ts
rightStickPrimary = {
  pairA: ["BTN_RT3", "BTN_RT5"],
  pairB: ["BTN_RT2", "BTN_RT4"],
} as const;
```

### 9.3 Secondary opposite-pair evidence

High-confidence in calibration 2:

```ts
secondaryLeftFingerAxis = ["BTN_LF8", "BTN_LF6"] as const;
```

Profile/mode-dependent:

```ts
secondaryRightFingerAxis = ["BTN_RF7", "BTN_RF8"] as const;
```

## 10. Physical ID → visual-region inference

This is sufficient for backend work. Exact pixel coordinates should remain an optional later calibration task.

| Physical ID | Visual-region inference | Confidence |
|---|---|---:|
| `BTN_LF1` | Left-finger axis pair with `BTN_LF3` | High for pair, medium for exact circle |
| `BTN_LF2` | Large left-side lower/finger button; changed from `B` to `A` between calibrations | High |
| `BTN_LF3` | Left-finger axis pair with `BTN_LF1` | High for pair, medium for exact circle |
| `BTN_LF4` | Upper-left/central left-finger button; visible icon changed between calibrations | Medium-high |
| `BTN_LF5` | Left-finger auxiliary button; visible left-side stick/action target changed between calibrations | Medium-high |
| `BTN_LF6` | Secondary left-finger axis pair with `BTN_LF8` | High for pair, medium for exact circle |
| `BTN_LF7` | Lower/left-finger auxiliary near `LF6/LF8` group | Medium |
| `BTN_LF8` | Secondary left-finger axis pair with `BTN_LF6` | High for pair, medium for exact circle |
| `BTN_LT3` | Lower-left thumb `MX` position in calibration 1; omitted in calibration 2 | Medium-high |
| `BTN_LT4` | Lower-left thumb `MY` position in calibration 1; omitted in calibration 2 | Medium-high |
| `BTN_LT5` | Lower-left/right-stick direction auxiliary; changed from `RT3` to `RT5` | High |
| `BTN_LT6` | Lower-left start/Z-style auxiliary; changed from `MB7` to `RF3` | High |
| `BTN_RT1` | Right-thumb auxiliary near C-stick cluster; activates `BTN_RF3` in both calibrations | High |
| `BTN_RT2` | Primary right-stick/C-stick direction, paired with `BTN_RT4` | High |
| `BTN_RT3` | Primary right-stick/C-stick direction, paired with `BTN_RT5` | High |
| `BTN_RT4` | Primary right-stick/C-stick direction, paired with `BTN_RT2` | High |
| `BTN_RT5` | Primary right-stick/C-stick direction, paired with `BTN_RT3` | High |
| `BTN_RF1` | Right-side/central action position; activates `BTN_RT1` in both calibrations | Medium-high |
| `BTN_RF3` | Right/central auxiliary; changed from `LT1` to `RT5` | Medium |
| `BTN_RF4` | Right/central direction/auxiliary; also appears in legacy/default left-axis SOCD pair | Medium-high |
| `BTN_RF5` | Right-side control position, first explicitly activated in calibration 2 | Medium |
| `BTN_RF6` | Right-side large face/control button; changed from `B` to left-axis/A-style target | High |
| `BTN_RF7` | Right-side secondary axis/control; active in calibration 2 and paired with `RF8` in calibration 1/modes | Medium-high |
| `BTN_RF8` | Right-side secondary axis/control; active in calibration 2 and paired with `RF7` in calibration 1/modes | Medium-high |
| `BTN_RF9` | Right-side auxiliary; active in calibration 1, omitted in calibration 2 | Medium |
| `BTN_RF10` | Right-side auxiliary; changed from `RT4` to `RF1` | High |
| `BTN_RF11` | Right/central auxiliary; activates `MB7` in calibration 2 | High |
| `BTN_RF12` | Right/central auxiliary; activates `RT4` in calibration 2 | High |
| `BTN_RF13` | Right-side upper/action bank; changed from `RF7` to `LT1` | High |
| `BTN_RF14` | Right-side upper/action bank; changed from `RF3` to `LT2` | High |
| `BTN_RF15` | Right-side upper/action bank; changed from `RF6` to `RT1` | High |
| `BTN_RF16` | Far-right/right-side auxiliary; activates `RF8` in both calibrations | High |
| `BTN_MB1` | Menu button entry with omitted activate target | Medium |
| `BTN_MB2` | Menu button entry with omitted activate target | Medium |
| `BTN_MB3` | Menu button entry with omitted activate target | Medium |

## 11. Modeling recommendation

Add a calibrated fixture layer rather than hardcoding these as universal firmware truth.

```ts
export type GlyphCalibrationConfidence =
  | "confirmed"
  | "inferred"
  | "unknown";

export type GlyphButtonCluster = "LF" | "LT" | "RF" | "RT" | "MB";

export type GlyphPhysicalButtonCalibration = {
  physicalButton: GlyphPhysicalButtonId;
  cluster: GlyphButtonCluster;
  visualRegion: string;
  evidence: readonly string[];
  confidence: GlyphCalibrationConfidence;
};

export type GlyphSocdPairCalibration = {
  first: GlyphPhysicalButtonId;
  second: GlyphPhysicalButtonId;
  socdType?: string;
  sourceProfile: string;
  confidence: GlyphCalibrationConfidence;
};
```

Store the two calibration JSON files as fixtures, not as authoritative source truth:

```text
GlyphUserProfilesUlt-filled.json
GlyphUltFilled2.json
```

Use them to test parser behavior and to document observed configurator behavior.

## 12. Backend implications

For Senscope/Glyph adapter work, these findings are enough to proceed with:

1. Parsing Glyph profile JSON.
2. Extracting the active `MODE_ULTIMATE` config.
3. Listing physical remap entries.
4. Preserving omitted `activates` fields.
5. Extracting SOCD pairs as profile-specific data.
6. Building a typed physical button ID model.
7. Adding calibration fixture tests.
8. Keeping visual placement as calibrated/inferred metadata, not universal truth.

Do not yet claim:

```text
- exact pixel-perfect visual coordinates for every button
- universal SOCD direction groups independent of mode/profile
- omitted activates means disabled
- `MB7` is necessarily a physical menu button
```

## 13. Recommended next implementation slice

A safe first implementation slice is:

```text
Glyph config parser and calibration fixture support
```

This should be a pure parser/docs/test slice, not a firmware behavior change.

Deliverables:

```text
- Glyph JSON fixture storage
- TypeScript types for Glyph config fragments
- parser for mode configs, button remaps, SOCD pairs
- Ultimate mode lookup
- calibration fixture tests
- docs handoff
```

Out of scope:

```text
- device flashing / push-to-device
- vendor-private binary serialization
- final Senscope profile-to-Glyph exporter
- gameplay semantic changes
```
