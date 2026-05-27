# Glyph Smash Box Modifiers Hardware Test Plan - 2026-05-27

## Scope

- Native Ultimate only.
- Manual hardware validation plan for Smash Box-style modifier runtime after source-backed binding resolution.
- This plan is prepared while runtime implementation is blocked.

## Precondition Gate

Do not execute this matrix until all blocker codes below are cleared:

- `MODIFIER_ROLE_BINDING_SOURCE_GAP`
- `MODIFIER_COMPOSITION_POLICY_UNRESOLVED`
- `LS_DPAD_LEFT_STICK_NEUTRAL_POLICY_UNRESOLVED`

## Required Test Rows

| Row | Requirement | Status while blocked | Notes |
| --- | --- | --- | --- |
| T01 | Default `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact raw outputs from table doc. |
| T02 | Mode default `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact Mode table outputs. |
| T03 | `X1` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact raw outputs. |
| T04 | `X2` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact raw outputs. |
| T05 | `MX1` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact raw outputs. |
| T06 | `MX2` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact raw outputs. |
| T07 | `Y1` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact raw outputs. |
| T08 | `Y2` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact raw outputs. |
| T09 | `MY1` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Preserve intentional flipper outputs. |
| T10 | `MY2` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Preserve intentional flipper outputs. |
| T11 | `Tilt1` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Preserve existing Tilt behavior where required. |
| T12 | `Tilt2` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Preserve existing Tilt behavior where required. |
| T13 | `Tilt3` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Preserve existing LT3/Tilt3 behavior. |
| T14 | `MTilt1` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact raw outputs. |
| T15 | `MTilt2` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact raw outputs. |
| T16 | `MTilt3` `1..9` | `BLOCKED_PENDING_ROLE_BINDINGS` | Verify exact raw outputs. |
| T17 | Mode neutral `5 == (128,172)` | `BLOCKED_PENDING_ROLE_BINDINGS` | Must match exact coordinate. |
| T18 | `MY1/MY2` flipper behavior | `BLOCKED_PENDING_ROLE_BINDINGS` | Do not normalize or correct. |
| T19 | LS->DPad directional outputs | `BLOCKED_PENDING_LS_DPAD_POLICY` | Needs resolved function binding + expected path. |
| T20 | LS->DPad left-stick neutral/active policy | `BLOCKED_PENDING_LS_DPAD_POLICY` | Current source trace for this profile is unresolved. |
| T21 | D-pad repaired cluster regression | `READY_AFTER_RUNTIME_PATCH` | Preserve `RF13->RF8`, `RF10->RF7`, `LF6->LF8`, `RF11->LF6`. |
| T22 | Right-stick orthogonality smoke | `READY_AFTER_RUNTIME_PATCH` | Must remain unaffected except documented behavior. |
| T23 | Trigger smoke | `READY_AFTER_RUNTIME_PATCH` | Confirm no unintended trigger regressions. |
| T24 | SOCD/remap smoke | `READY_AFTER_RUNTIME_PATCH` | Confirm pre-remap/remap/SOCD path preserved. |
| T25 | Nunchuk check | `NOT_TESTED_UNAVAILABLE` | Keep explicit unless hardware path is available. |

## Execution Notes

- Use raw coordinate captures and direction `1..9` logs.
- Record pass/fail per row in a hardware result file after implementation.
- Do not claim preservation or completion while blocked rows remain unresolved.
