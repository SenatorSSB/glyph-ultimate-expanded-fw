# Glyph Phase 7A Runtime Config Compiled Payload Activation Hardware Plan

Status: `PLAN_ONLY_NOT_TESTED`

This is a hardware test plan for the Phase 7A source-owned compiled/test
runtime-config payload activation branch. It is not a hardware result. All rows
start as `NOT_TESTED`.

Branch:
`phase7a-runtime-config-compiled-payload-activation`

Scope:

- Validate normal operation after compiled/test payload activation.
- Confirm current source-equivalent baseline behavior remains preserved.
- Confirm no storage, device write, WebSerial, or flashing automation is used.
- Confirm no firmware flashing automation is used.
- Keep nunchuk as `NOT_TESTED` unless separately validated and recorded.

| ID | Area | Status | Procedure | Expected |
| --- | --- | --- | --- | --- |
| BOOT-001 | normal boot | NOT_TESTED | Build artifact is manually installed by the operator-approved route, then the controller is power-cycled normally. | Controller boots normally with no special runtime-config load path. |
| BASELINE-001 | current baseline preserved | NOT_TESTED | Exercise representative current baseline directions and neutral output. | Source-equivalent baseline output is preserved. |
| PARSER-001 | compiled valid payload accepted | NOT_TESTED | Run firmware with the committed compiled/test payload. | Normal runtime behavior is available after parser validation. |
| FALLBACK-001 | invalid/failure path | NOT_TESTED | Checker-only unless a separate intentionally invalid firmware artifact is prepared for operator review. | Invalid compiled payload falls back deterministically to known-good source-owned baseline. |
| MODIFIERS-001 | representative modifiers | NOT_TESTED | Exercise representative X/Y/tilt/layer modifier cases from the existing baseline matrix. | Modifier outputs match the current baseline. |
| SPECIAL-001 | special tables | NOT_TESTED | Exercise special table cases such as Y1 tilt/layer combinations and RT1/RF4 custom where practical. | Special-table outputs match the current baseline. |
| OVERRIDE-001 | override paths | NOT_TESTED | Exercise direction-plus-A, RF6 low magnitude, RF7 hard Up+B, and RF9 null where practical. | Override outputs match the current baseline. |
| CSTICK-001 | c-stick interaction | NOT_TESTED | Exercise c-stick ASDI/diagonal and RF3 vertical c-stick interaction where doable. | C-stick interactions are not regressed. |
| NO-STORAGE-001 | no storage read/write | NOT_TESTED | Inspect source/build branch and observe normal runtime operation. | No runtime-config storage read/write is used. |
| NO-WRITE-001 | no device write/WebSerial | NOT_TESTED | Inspect source/build branch and test without configurator write transport. | No device write or WebSerial runtime-config path is used. |
| NO-FLASH-001 | no flashing automation | NOT_TESTED | Confirm operator performs any install manually outside agent automation. | No flashing automation, UF2 copy automation, or bootloader automation is used by this branch. |
| PROFILE-REG-001 | profile regression | NOT_TESTED | Exercise current profile behavior covered by prior non-nunchuk baseline checks. | No profile regression is observed. |
| NUNCHUK-001 | nunchuk | NOT_TESTED | Not run unless nunchuk hardware is available and explicitly included. | Nunchuk remains NOT_TESTED; no validation claim is made. |

Merge gate:

- This branch must not merge until an operator/user hardware result is recorded
  on a separate hardware-result branch.
