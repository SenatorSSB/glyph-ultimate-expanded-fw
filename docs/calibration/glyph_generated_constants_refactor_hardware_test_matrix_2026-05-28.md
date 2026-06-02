# Glyph Generated Constants Refactor Hardware Test Matrix - 2026-05-28

## Purpose and scope

This matrix defines the minimum hardware test scope for a future generated
constants firmware refactor. It is a template for later manual execution after
an approved implementation branch and firmware artifact exist.

Scope boundaries:

- This matrix is not executed.
- This is not a hardware result.
- This does not validate hardware.
- This does not approve firmware source edits.
- This does not implement generated constants.
- This does not change firmware runtime behavior.

## Status

Template only. Hardware status: not a new hardware result.

## Hardware caveat

Hardware test result must be recorded separately after a future implementation
branch exists and a future firmware artifact is built. No hardware validation is
claimed by this matrix.

## Source authority

Primary source authority is limited to current repository sources:

- `src/modes/Ultimate.cpp`
- generated-config prototype docs/fixtures
- generated C++ diff artifact docs/fixtures
- generated constants readiness packet
- generated constants implementation plan
- generated constants execution packet
- hardware validation and rollback plan
- preimplementation go/no-go index
- current identity-runtime checkers in `tools/`

## Test prerequisites

- Explicit user approval for the future generated constants firmware refactor.
- Future implementation branch exists.
- Future firmware artifact identity is recorded.
- Pre-edit and post-edit docs/tools checkers pass.
- Build verification passes for the future source branch.
- Rollback branch or commit is recorded.
- Operator has the required hardware available.

## Build/artifact identity

A future hardware result must record:

- repository and branch;
- commit SHA;
- build command;
- artifact filename and checksum if an artifact is produced;
- device identifier available to the operator;
- test date and tester;
- whether the artifact came from the future implementation branch.

## Test matrix

| Row ID | Category | Description | Expected result | Evidence required |
| --- | --- | --- | --- | --- |
| BOOT-001 | boot | Device boots with future firmware artifact. | Device reaches normal operating state. | Operator note with branch, commit, and artifact identity. |
| PROFILE-001 | identity_profile | Current identity profile remains active/compatible. | Existing identity runtime profile path remains usable. | Operator note showing current identity profile compatibility. |
| DEFAULT-001 | default_table | Default table neutral and cardinal sanity checks. | Neutral and cardinal outputs match current expected source-backed behavior. | Recorded neutral/cardinal observations. |
| MODE-001 | mode_default | Mode default center sanity check. | Mode/default center remains centered as expected. | Recorded mode/default observation. |
| XMOD-001 | x_modifiers | X1/X2 representative modifier checks. | Representative X1/X2 outputs match current expected behavior. | Recorded X1/X2 observations. |
| YMOD-001 | y_modifiers | Y1/MY1 representative modifier checks. | Representative Y1/MY1 outputs match current expected behavior. | Recorded Y1/MY1 observations. |
| TILT-001 | tilt_modifiers | Tilt1/Tilt2/Tilt3 representative modifier checks. | Representative Tilt1/Tilt2/Tilt3 outputs match current expected behavior. | Recorded Tilt observations. |
| ZAIR-001 | z_airdodge_low_magnitude | LT5/RF11 Z-airdodge low-magnitude representative checks. | Low-magnitude override remains source-backed and unchanged. | Recorded LT5/RF11 observations. |
| UPB-001 | hard_up_b | RF7 hard Up+B left/neutral/right checks. | RF7 hard Up+B outputs match current expected behavior. | Recorded left/neutral/right observations. |
| NULL-001 | null_override | RF9 null override check. | RF9 final null override centers left stick as expected. | Recorded RF9 observation. |
| DPA-001 | ls_to_dpad | RF13 LS->DPad representative checks. | Effective left-stick directions route to D-pad as expected. | Recorded RF13 observations. |
| LAYER-001 | pure_layer | LF8/LF7 pure layer representative checks. | Pure layer direction/table behavior matches current expected behavior. | Recorded LF8/LF7 observations. |
| LF4-001 | lf4_submode | LF4 sub-mode representative checks. | LF4 sub-mode behavior matches current expected behavior. | Recorded LF4 observations. |
| CSUP-001 | cstick_suppression | C-stick suppression representative checks. | C-stick suppression behavior in LF4 sub-mode matches current expected behavior. | Recorded suppression observations. |
| DA-001 | direction_plus_a | Direction+A representative checks. | Direction+A hard analog overrides match current expected behavior. | Recorded Direction+A observations. |
| RS-001 | right_stick | C-stick/right-stick representative checks. | Right-stick outputs remain representative and unchanged. | Recorded right-stick observations. |
| SYS-001 | system_buttons | Menu/system button smoke checks. | Menu/system button outputs remain usable. | Recorded menu/system observations. |
| PROFREG-001 | profile_regression | No profile artifact regression check. | No profile artifact regression is observed or introduced. | Git diff/status plus operator note. |
| NUNCHUK-001 | nunchuk_scope | Nunchuk remains not claimed unless separately tested. | No nunchuk hardware validation claim is made without separate test evidence. | Explicit nunchuk caveat in result. |

## Pass/fail criteria

Pass requires every applicable row to match current source-backed expected
behavior and the final result doc to avoid unsupported hardware claims.

Fail if any row changes table value behavior, runtime behavior, profile
compatibility, serial/device behavior, or unsupported nunchuk scope.

## Failure handling

On failure:

- stop merge preparation;
- record the failure row and observed output;
- preserve logs or notes needed for diagnosis;
- use the rollback plan;
- do not claim hardware validation.

## Rollback requirements

Rollback is required on failure. The future implementation branch must preserve
a normal Git-history path back to the pre-refactor hardcoded constants and must
not depend on generated build artifacts for rollback.

## Result recording requirements

The result must be recorded separately from this template. It must include
branch, commit, artifact identity, checker/build status, executed rows,
pass/fail status, caveats, and rollback decision.

## Nunchuk scope

Nunchuk behavior remains preserved by source intent but not hardware validated
unless separately tested with nunchuk hardware and recorded in a separate result
doc.
