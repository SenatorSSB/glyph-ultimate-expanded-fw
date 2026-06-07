# Glyph Runtime Config Interpreter Source Baseline Hardware Plan

Status: TEMPLATE_ONLY
Branch: `runtime-config-interpreter-source-baseline`

This is the required hardware test template for this branch. It is not a hardware result and does not claim any unexecuted behavior.

## 1) Build Artifact Identity

| Field | Value |
| --- | --- |
| Build command used | `./scripts/build-glyph-mk6-quiet.sh` |
| Firmware artifact path | _fill after local build (if emitted)_ |
| Firmware artifact SHA-256 | _fill after local build (if emitted)_ |
| Commit SHA under test | _fill before test_ |
| Tester | _fill_ |
| Test date | _fill_ |

## 2) Intent

- Intended change: behavior-preserving firmware-owned runtime-config interpreter boundary for the current source-owned baseline.
- Scope: source-owned config-shaped baseline only, validate-before-use, explicit fallback-to-known-good source-owned baseline, table lookup through interpreter path, no runtime-loaded storage.
- Non-claims: this plan does not assert nunchuk validation (`no_nunchuk_validation`).

## 3) Planned Checks (all rows start as `NOT_TESTED`)

| Row ID | Category | Planned check | Result |
| --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | NOT_TESTED |
| PROFILE-001 | identity_profile | Current identity/default profile remains usable | NOT_TESTED |
| DEFAULT-001 | default_table | Default table outputs preserved | NOT_TESTED |
| MODE-001 | mode_default | Mode default/center behavior preserved | NOT_TESTED |
| XY-001 | xy_modifiers | Representative X/Y modifier outputs preserved | NOT_TESTED |
| TILT-001 | tilt_tables | Tilt1/Tilt2/Tilt3 representative outputs preserved | NOT_TESTED |
| LAYER-001 | layer_tables | Layer Normal-X / Flipper representative outputs preserved | NOT_TESTED |
| SPECIAL-TABLE-001 | special_tables | Tilt1Minus41 / RT1RF4Custom / Lt1LowMagnitude preserved | NOT_TESTED |
| OVERRIDE-001 | override_paths | RF9 null / RF6 low magnitude / hard Up-B if applicable | NOT_TESTED |
| CSTICK-001 | cstick_interaction | Existing C-stick interaction not regressed where doable | NOT_TESTED |
| PROFILE-REG-001 | profile_regression | No profile regression observed | NOT_TESTED |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED |

Allowed result statuses:
- `PASS`
- `FAIL`
- `NOT_TESTED`
- `BLOCKED`
- `USER_ACCEPTED_RISK`

## 4) Nunchuk Scope

- Nunchuk scope for this branch: `NOT_TESTED`.
- Do not upgrade this row to PASS/FAIL unless a separate documented nunchuk hardware run is performed.

## 5) Rollback

- On any `FAIL`, roll back via normal Git history on this branch to the prior commit containing the source-owned baseline interpreter boundary.
- Do not merge this branch until a separately recorded hardware result document confirms preservation and rollback path is still available.

## 6) Caveats

- `no_runtime_loaded_storage` remains in force.
- `no_webserial_or_device_write` remains in force.
- `no_protobuf_binary_config_parser` remains in force.
- `no_firmware_flashing_automation` remains in force.
- This plan is only a test template and does not replace a hardware result document.
