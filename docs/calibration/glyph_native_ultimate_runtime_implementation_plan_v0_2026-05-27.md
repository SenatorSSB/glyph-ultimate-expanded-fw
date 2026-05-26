# Glyph Native Ultimate Runtime Implementation Plan v0 - 2026-05-27

Scope: planning-only conversion of existing design/checker/fixture docs into a reviewable implementation sequence.

This file does not implement runtime behavior.

## Phase Plan

1. requirements packet completion
2. source authority confirmation
3. fixture contract update, if needed
4. runtime patch design diff review
5. local checker/build gate
6. manual UF2 hardware test packet
7. post-hardware result ingestion

## Explicit Stop Gates Before Any Runtime Branch

- user approves exact target behavior
- source definitions are clear enough
- preservation policy is explicit
- both-held/chord policy is explicit
- outbound disabled-remap policy is explicit if adapter work is involved
- hardware test owner is ready

## Runtime Patch Constraints

- native `MODE_ULTIMATE` only unless approved otherwise
- left-stick behavior only unless approved otherwise
- no C-stick/right-stick/trigger/nunchuk behavior change unless explicitly approved
- no SOCD/remap change
- no profile/schema/proto/configurator change
- no push-to-device/flashing automation
- no unsigned overflow/wrap dependence

## Verification Gates

- existing table fixture checker
- runtime scope checker
- next runtime readiness checker
- merged-state consistency checker
- PlatformIO `glyph_mk6` build
- artifact checksum only if building an RC artifact

## Hardware Evidence Rule

- runtime patch cannot be called preservation-verified until manual hardware result exists.

## Source Anchors

- `docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md`
- `docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md`
- `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md`
- `docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md`
- `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`
- `docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md`
- `tools/check_glyph_native_ultimate_table_fixture.py`
- `tools/check_glyph_native_ultimate_table_runtime_scope.py`
- `tools/run_glyph_next_runtime_change_readiness_checks.py`
- `tools/check_glyph_merged_state_consistency.py`

## Non-Goals

- no runtime implementation in this branch
- no firmware behavior promotion from observed-only rows
- no write-capable adapter implementation
- no game-semantic source claims
