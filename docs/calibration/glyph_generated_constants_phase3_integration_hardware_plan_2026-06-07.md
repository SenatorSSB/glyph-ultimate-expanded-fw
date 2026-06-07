# Glyph Generated Constants Phase 3 Integration Hardware Plan

Status: TEMPLATE_ONLY
Branch: `phase3-generated-constants-firmware-integration`

This is the required hardware test template for this branch. It is **not** a
hardware result and does not claim any unexecuted behavior.

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

- Intended change: behavior-preserving firmware-source refactor only.
- Scope: consumed constants moved into generated-like source include, no runtime-loaded config,
  no profile artifact changes, no device write behavior.
- Non-claims: this plan does not assert nunchuk validation.

## 3) Planned Checks (all rows start as `NOT_TESTED`)

| Row ID | Category | Planned check | Result |
| --- | --- | --- | --- |
| BOOT-001 | boot | Build + flash path reaches normal boot state | NOT_TESTED |
| PROFILE-001 | identity_profile | Current identity profile remains usable | NOT_TESTED |
| DEFAULT-001 | default_table | Default/neutral points match prior source-backed behavior | NOT_TESTED |
| MODES-001 | mode_default | mode default/center behavior preserved | NOT_TESTED |
| MODS-001 | modifier_tables | Representative X/Y/Tilt/Layer tables preserved | NOT_TESTED |
| RT1RF4-001 | custom_modifier_table | RT1+RF4 custom raw points match prior hardware observations | NOT_TESTED |
| LT5-001 | low_magnitude | LT5 RF11 low-magnitude override preserved | NOT_TESTED |
| NULL-001 | null_override | RF9 null behavior preserved | NOT_TESTED |
| PROFILE-REG-001 | profile_regression | No profile artifact behavior regression observed | NOT_TESTED |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED |

Allowed result statuses:
- `PASS`
- `FAIL`
- `NOT_TESTED`
- `BLOCKED`
- `USER_ACCEPTED_RISK`

## 4) Nunchuk Scope

- Nunchuk scope for this branch: `NOT_TESTED`.
- Do not upgrade this row to PASS/FAIL unless a separate documented nunchuk hardware
  run is performed.

## 5) Rollback

- On any `FAIL`, roll back via normal Git history on this branch to the prior commit
  containing hardcoded tables in `src/modes/Ultimate.cpp`.
- Do not merge this branch until a separately recorded hardware result document confirms
  preservation and rollback path is still available.

## 6) Caveats

- `no_runtime_loaded_config` remains in force.
- `no_webserial_or_device_write` remains in force.
- This plan is only a test template and does not replace a hardware result document.

