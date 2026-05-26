# Glyph Ultimate Preservation Hardware Matrix - 2026-05-26

Scope: manual hardware checklist for preserving existing native Ultimate behavior before any future runtime patch. This is a template/protocol document only. It does not record new results, change firmware behavior, add flashing automation, or claim hardware verification.

## Required Disposition Values

A real completed result file must end with one of:

- `PASS`
- `FAIL_ROLLBACK`
- `BLOCKED_NOT_TESTED`
- `NEEDS_FIRMWARE_FIX`

Until a real result file exists, the checker must report `status=NO_RESULT_FILE`.

## Test Matrix

| id | area | manual observation target | required evidence | optional | caveats |
| --- | --- | --- | --- | --- | --- |
| `UPRES-001` | C-stick/right-stick preservation | Existing C-stick/right-stick directions still produce expected Switch visualization or mini-screen movement. | Record each direction and whether Switch visualization and mini-screen agree. | no | Do not infer game actions from visualization alone. |
| `UPRES-002` | C-stick ASDI/slideoff branch preservation | Diagonal right-stick/C-stick behavior remains observable and not overwritten unexpectedly by future left-stick work. | Record diagonal cases separately from cardinal cases. | no | Source branch exists in `src/modes/Ultimate.cpp`; hardware outcome must be observed later. |
| `UPRES-003` | Trigger preservation | Logical `lf4` and `rf5` still produce expected digital/analog trigger behavior. | Record Switch visualization and mini-screen if visible. | no | RF5 identity remains an explicit check surface. |
| `UPRES-004` | SOCD/opposite direction behavior | Opposite directions resolve according to existing configured SOCD behavior. | Record left/right, up/down, and C-stick opposing pairs if applicable. | no | Do not change SOCD semantics in this workstream. |
| `UPRES-005` | RF5 physical identity | Press the physical RF5 candidate and record what input/output is observed. | Record raw physical description, display highlight, Switch output, and profile mapping if known. | no | RF5 is currently ambiguous from prior hardware result. |
| `UPRES-006` | Profile preservation/readback | Existing profile remains selected and readable after any future candidate build/test if readback is possible. | Record profile name/default mode and whether configurator/readback was used. | no | No push-to-device automation is allowed. |
| `UPRES-007` | Both-held modifier behavior | Holding LT1+LT2 through the current MVP physical routing remains stable. | Record all 9 directions or note why each was blocked. | no | Current both-held behavior is observed/source-defined, not a new desired semantic. |
| `UPRES-008` | Default profile selection | Device boots/selects the expected default profile/backend mode. | Record backend, selected profile, and any screen/menu evidence. | no | Default indices are one-based where source-confirmed. |
| `UPRES-009` | Optional nunchuk | If nunchuk hardware is available, record whether nunchuk connection overwrites left stick as source suggests. | Record connected/not connected and observed behavior. | yes | Optional; absence must not fail preservation testing. |
| `UPRES-010` | Switch visualization vs mini-screen | Compare Switch controller visualization with Glyph mini-screen for each core preservation case. | Record mismatches explicitly. | no | Mini-screen coordinates are display observations, not proof of game semantics. |
| `UPRES-011` | Ultimate Training Mode smoke | Run a basic Ultimate Training Mode smoke if hardware/game access is available. | Record pass/fail/blocker with exact setup. | no | Do not make Smash semantic claims beyond smoke observation. |
| `UPRES-012` | Current Tilt1/Tilt2 preservation | Confirm native Ultimate Tilt/Tilt2 still matches the previously hardware-smoke-tested behavior. | Record 9-way Tilt1 and Tilt2 observations. | no | Existing pass is in prior result; future runtime patches need fresh evidence. |

## No Fake Results

This matrix intentionally contains no observed results. Use `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md` for future manual capture and commit a real result file only after hardware testing.
