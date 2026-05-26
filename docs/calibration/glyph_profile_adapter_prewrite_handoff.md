# Glyph Profile Adapter Prewrite Validation Handoff

Date: 2026-05-26

## What This Branch Adds

- `tools/check_glyph_profile_adapter_prewrite.py`, a stdlib-only read-only checker for explicit profile fixture paths.
- `docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md`, explaining checker scope and warning/error policy.
- This handoff document.

## Intended Use

Run the checker against candidate fixtures or future adapter candidate output before any write-capable adapter is reviewed:

```bash
.venv/bin/python tools/check_glyph_profile_adapter_prewrite.py docs/sources/raw/GlyphUserProfiles.json
```

## Important Boundaries

- No write-capable adapter exists here.
- The checker does not normalize omitted `activates` to `BTN_UNSPECIFIED`.
- The checker does not reorder remaps.
- Warnings are decision surfaces, not automatic failures.
- JSON fixtures remain examples/corpus candidates, not canonical wire format.

## Behavior Impact

- Runtime/source behavior changed: none.
- Configurator/profile schema behavior changed: none.
- Build artifacts or binaries committed: no.
