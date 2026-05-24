# Glyph Ultimate Layout Calibration Handoff

Date: 2026-05-24  
Branch: `docs/glyph-ultimate-layout-calibration`

## Scope of this branch

This branch adds calibration documentation, fixture files, and a lightweight validation check script only.

Added:

- calibration findings doc
- two JSON fixtures copied into repo
- stdlib-only Python validation script
- optional machine-readable summary JSON

## Explicit non-goals and unchanged areas

- No firmware behavior changed.
- No device behavior changed.
- No configurator behavior changed.
- No build system changes.
- No remapping semantics changes.
- No flashing/push-to-device flow changes.

## Interpretation boundaries preserved

- Omitted `activates` remain uninterpreted omitted/unknown/default entries.
- Omitted `activates` are not interpreted as disabled.
- SOCD pairs are modeled as profile-specific configuration, not universal layout truth.
- Exact visual pixel coordinate mapping remains out of scope in this slice.

## Verification run in this branch

- `python3 tools/check_glyph_calibration_fixtures.py`
- `git status --short`
- `git diff --stat`
- conflict-marker scan command requested in task prompt

## Outcome

Calibration fixtures now have a repeatable guardrail check and documentation suitable for future backend/parser/export-planning work without changing firmware behavior.
