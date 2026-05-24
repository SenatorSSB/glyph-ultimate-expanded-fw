# Glyph Ultimate Tilt Runtime Patch Spec Template

## Purpose

Use this template before creating a behavior-changing runtime patch branch.
Only fill fields with source-backed, human-approved values.
If a field is unknown, write `unknown` and block implementation.

## 1) Branch Metadata

- Planned branch name: `<fill>`
- Base branch: `<fill>`
- Target commit SHA: `<fill>`
- Spec owner: `<fill>`
- Date: `<YYYY-MM-DD>`

## 2) Scope Approval

- Native `MODE_ULTIMATE` only: `[ ] yes  [ ] no`
- No schema/profile changes: `[ ] yes  [ ] no`
- No SOCD changes: `[ ] yes  [ ] no`
- No remap semantic changes: `[ ] yes  [ ] no`
- No macros/turbo/timing automation: `[ ] yes  [ ] no`

Notes:
- If any answer is `no`, explain and obtain explicit approval before implementation.

## 3) Tilt1/Tilt2 Values (Placeholder Only)

For each planned output value, fill one row from source-backed data.
Do not guess values.

| Field | Tilt1 | Tilt2 |
| --- | --- | --- |
| Name | `<fill>` | `<fill>` |
| Raw value representation | `<fill>` | `<fill>` |
| Effective value representation | `<fill>` | `<fill>` |
| Source value representation | `<fill>` | `<fill>` |
| Left-stick X output | `<fill>` | `<fill>` |
| Left-stick Y output | `<fill>` | `<fill>` |
| Value type (`absolute byte` or `neutral-relative offset`) | `<fill>` | `<fill>` |
| Source/provenance | `<file path / fixture / note>` | `<file path / fixture / note>` |

## 4) Activation Mapping

- Physical button(s): `<fill>`
- Logical input name(s): `<fill>`
- Post-remap runtime input(s): `<fill>`
- Chord requirement(s): `<fill>`
- Direction interaction: `<fill>`
- Priority/order relative to existing branches (`ModX` / `ModY` / native branches): `<fill>`
- Collision handling when multiple mappings are active: `<fill>`
- Source/provenance: `<file path / fixture / note>`

Reference for uploaded MVP layout:

- Tilt1 / TILT replaces MX: physical `BTN_RF3`, logical `BTN_LT1`, future native Ultimate runtime `inputs.lt1`.
- Tilt2 replaces MY: physical `BTN_RF4`, logical `BTN_LT2`, future native Ultimate runtime `inputs.lt2`.
- `BTN_RF5` is rejected for this layout's Tilt1/Tilt2 target.
- Runtime behavior should use post-remap logical inputs unless a later approved spec explicitly says otherwise.

## 5) Output Target Scope

- Left stick only: `[ ] yes  [ ] no`
- C-stick/right-stick behavior preserved: `[ ] yes  [ ] no`
- Trigger behavior preserved: `[ ] yes  [ ] no`
- Nunchuk behavior preserved: `[ ] yes  [ ] no`
- D-pad layer behavior preserved: `[ ] yes  [ ] no`
- Any approved exception(s): `<none / fill>`

## 6) Numeric Safety

- Explicitly no overflow/flipper dependency: `[ ] yes  [ ] no`
- Exact allowed byte range: `<fill, expected 0..255 unless explicitly approved otherwise>`
- Expected neutral/no-input behavior: `<fill>`
- Clamping/saturation expectation: `<fill>`
- Source/provenance for numeric assumptions: `<file path / fixture / note>`

## 7) Verification Plan

- Static scanner snapshot before patch: `<command + output artifact>`
- Static scanner snapshot after patch: `<command + output artifact>`
- Source diff review plan: `<fill>`
- Build command: `<fill>`
- Smoke-test protocol document: `<path>`
- Reviewer sign-off fields:
  - Diff scope approved: `[ ] yes  [ ] no`
  - Numeric safety approved: `[ ] yes  [ ] no`
  - Hardware-owner smoke-test approved: `[ ] yes  [ ] no`

## 8) Rollback Plan

- Rollback trigger(s): `<fill>`
- Rollback branch/commit target: `<fill>`
- Verification after rollback: `<fill>`
- Ownership for rollback execution: `<fill>`

## Sign-Off

- Firmware owner approval: `<name/date>`
- Hardware owner approval: `<name/date>`
- Reviewer approval: `<name/date>`
