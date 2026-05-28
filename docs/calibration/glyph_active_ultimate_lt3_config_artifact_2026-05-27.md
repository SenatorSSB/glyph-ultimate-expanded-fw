# Glyph Active Ultimate LT3 Config Artifact - 2026-05-27

## Scope

- Active Ultimate profile/config application path only.
- No runtime Tilt logic change.
- No schema/proto/configurator structural change.
- No flashing automation.
- No push-to-device automation.

## Source-Backed Conclusion

- Implementation kind: `importable config/profile artifact`.
- Target artifact created: `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`.
- Checker created: `tools/check_glyph_active_ultimate_lt3_config_artifact.py`.
- Active write path remains source-backed through:
  - `HAL/pico/src/comms/ConfiguratorBackend.cpp` (`HandleSetConfig`, `CMD_SET_CONFIG`)
  - `HAL/pico/src/core/Persistence.cpp` (`SaveConfig`)
- This branch does not change firmware runtime Tilt logic or config schema.

## Binding Target

- Target replacement in Ultimate remap content:
  - old: `BTN_LT3 -> BTN_LF4`
  - new: `BTN_LT3 -> BTN_LT3`
- Preserved:
  - `BTN_RF3 -> BTN_LT1`
  - `BTN_RF4 -> BTN_LT2`

## Active vs Default Distinction

- Normal firmware update path keeps valid stored `config.bin`; it does not automatically apply this artifact to already-provisioned devices.
- Active profile change requires applying config through the existing configurator config-write path (`CMD_SET_CONFIG` -> `Persistence::SaveConfig`), or a default-restore/fresh-install path if defaults are changed in firmware source.
- This branch does not modify `config/glyph/common/include/glyph_overrides.hpp`.

## User Procedure (Manual)

1. Back up the current device profile/config first (export/get-config in your current configurator workflow, if available).
2. Use your existing configurator config import/edit flow with:
   - `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
3. Apply/write the config to device through the configurator path that sends `CMD_SET_CONFIG` (device-side source-backed write path).
4. Run standalone hardware validation after apply:
   - physical LT3 directions `1..9` should hit the Tilt3 table
   - LT1/LT2 and LT1+LT2 behavior should be rechecked

Warnings:
- This rebinding moves physical LT3 away from previous logical `LF4` / trigger L digital behavior in the active Ultimate profile.
- Do not claim dedicated LT3 hardware PASS before post-apply hardware test evidence is recorded.

## Caveats

- No claim that any active on-device profile changed until the user performs manual import/apply.
- No claim that dedicated LT3 hardware verification has passed in this branch.
- Repo source confirms device-side protobuf get/set transport and persistence, but does not include external configurator UI source semantics.

## 2026-05-27 Amendment: Webapp Path vs Path B

- Limit Labs configurator webapp is closed-source from this repository perspective and was observed not to preserve/action standalone LT3 after import/push in this test stream.
- This observation does not disprove the artifact content itself.
- It means the webapp import path is not treated here as a verified native config write path for this LT3 binding.
- Active direction is now Path B: direct source-backed serial/config write flow when protocol and payload handling are source-confirmed.

## 2026-05-27 Amendment: Serial Write Success and D-pad Profile Defect

- The serial config write path is now hardware-proven to activate standalone LT3 behavior.
- After apply, the active artifact/profile mapping was observed to produce duplicate D-pad Left behavior.
- This branch repairs the D-pad Down mapping in the active profile artifacts when source evidence supports the specific `BTN_RF10 -> BTN_RF7` correction.

## 2026-05-27 Amendment: Repaired Artifact Final Hardware Confirmation

- Repaired artifact apply was hardware-confirmed as working.
- Duplicate D-pad Left defect is fixed in the active profile mapping outcome.
- Standalone physical LT3 remains hardware-verified through the serial-config-applied active profile path.

## 2026-05-27 Amendment: Identity Baseline Supersession

- The prior LT3-active artifact path remains successful historical evidence for validating the LT3/D-pad remap path.
- The identity-baseline branch (`glyph/gfw2-ultimate-identity-profile-baseline`) supersedes this artifact as the active development baseline for future runtime-only custom behavior work.
- Do not confuse historical LT3/D-pad remap artifact behavior with identity-baseline behavior; the identity baseline intentionally removes semantic remap assumptions so follow-up runtime implementation can own those behaviors explicitly.

## 2026-05-28 Amendment: Runtime Supersession For Active Development

- The historical LT3/D-pad remap artifact path is superseded for active development by the identity-runtime implementation branch (`glyph/gfw2-identity-runtime-smashbox-modifiers`).
- Under the identity runtime policy, no claim is made that old standalone LT3 Tilt3 behavior remains active; LT3 is runtime-owned as Y2 and Tilt3 is runtime-owned as RF3+RF4 chord behavior.
