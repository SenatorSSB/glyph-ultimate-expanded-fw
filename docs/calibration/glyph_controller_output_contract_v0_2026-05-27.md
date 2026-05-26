# Glyph Controller Output Contract v0 - 2026-05-27

Scope: Glyph/HayBox-side firmware/configurator/backend workstream only.

This contract packet is pre-implementation planning only. It does not change runtime behavior, does not mutate schema/proto/configurator behavior, and does not make Smash/game-semantic claims.

## Explicit Non-Goals

- no runtime firmware behavior change
- no profile/schema/proto/configurator change
- no SOCD/remap semantic change
- no flashing/push automation
- no Smash/game semantic claims

## Output Domains

### Left-stick raw byte outputs

- Contracted output surface for this planning packet is left-stick raw coordinate bytes.
- Coordinates are represented as explicit byte values, not inferred display offsets.
- Current native Ultimate Tilt1/Tilt2 baseline behavior remains source-confirmed and smoke-tested (`src/modes/Ultimate.cpp`, `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`, `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`).

### Right-stick/C-stick preservation boundary

- Future native Ultimate table runtime work must preserve right-stick/C-stick behavior unless explicitly approved otherwise.
- No right-stick/C-stick behavioral changes are approved in this contract packet.

### Trigger preservation boundary

- Future native Ultimate table runtime work must preserve trigger behavior unless explicitly approved otherwise.
- No trigger behavioral changes are approved in this contract packet.

### Nunchuk overwrite boundary

- Existing nunchuk overwrite precedence remains a preservation boundary for any future runtime patch scope.
- This contract packet does not approve any nunchuk overwrite behavior change.

### Post-remap logical input boundary

- Runtime modifier evaluation remains bounded to post-remap logical inputs.
- This packet does not approve bypassing remap with raw physical inputs.

## Invariants

- raw stick coordinates are bytes in `[0,255]`
- neutral is explicit
- 9-way direction tables use keys `1..9`
- `offset_x`/`offset_y` are display/debug values, not storage truth
- future runtime table work must not rely on unsigned overflow/wrap behavior
- omitted `activates` and explicit `BTN_UNSPECIFIED` must remain distinct until policy is resolved

## Evidence Classifications

- `SOURCE_CONFIRMED`
- `HARDWARE_SMOKE_VERIFIED`
- `HARDWARE_REQUIRED`
- `OBSERVED_ONLY_NON_CONTRACTUAL`
- `USER_INPUT_REQUIRED`
- `BLOCKED_CORPUS`

## Current-State Statements

- Current Tilt1/Tilt2 behavior is source-confirmed and smoke-tested for the current native Ultimate MVP scope (`src/modes/Ultimate.cpp`, `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`, `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`).
- Arbitrary native Ultimate table runtime remains unimplemented and unapproved in this repository state (`docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md`, `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md`).
- Both-held LT1+LT2 current behavior remains observed-only/non-contractual unless a future reviewed design explicitly promotes it (`docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`, `docs/calibration/fixtures/glyph_native_ultimate_current_tilt_tables_2026-05-26.json`).

## Boundaries With Requirements/Adapter Work

- Disabled-remap outbound policy remains unresolved (`docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`, `docs/calibration/glyph_profile_config_source_authority_2026-05-26.md`).
- This contract packet does not approve write-capable adapter behavior.
