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

## Verification

Commands to run for this branch:

```bash
.venv/bin/python tools/check_glyph_profile_adapter_prewrite.py docs/sources/raw/GlyphUserProfiles.json
.venv/bin/python tools/check_glyph_profile_adapter_prewrite.py docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json
.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py
.venv/bin/python tools/check_glyph_profile_config_semantics.py
.venv/bin/python tools/check_glyph_profile_config_export_corpus.py
grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true
git diff --check
git status --short
```

Result on 2026-05-26: all commands above passed. The conflict-marker grep produced no output. `git status --short` showed only the three intended changed files before commit.

## Next Branch

Recommended next branch: `glyph/physical-logical-layout-map`.
