# Glyph Config JSON Compatibility Fixtures - 2026-06-03

## Purpose and scope

This document records repo-committed fixture compatibility only for the current
Glyph profile/config JSON artifacts already checked into this repository.

It is not official configurator source authority, not firmware source, not
runtime-loaded config, not serial/device write behavior, and not hardware
validation.

The goal is limited: capture compatibility properties observable from committed
artifacts, committed docs, and committed checker/tool behavior without claiming
official JSON compatibility.

## Compatibility boundaries

These fixtures and checks are bounded to repo-committed observations only:

- active profile artifact exists and parses as JSON
- `MODE_ULTIMATE` exists in the active profile artifact
- fixture profile artifact exists and parses as JSON
- explicit self-activated identity profile bindings remain present where current
  repo checkers require them
- explicit disables, when present in committed profile JSON, appear as remap
  entries with `physicalButton` and no `activates`
- `gameModeConfigs`, when present, is a list
- `buttonRemapping` in `MODE_ULTIMATE` is a list
- `socdPairs` in `MODE_ULTIMATE` is a list
- the committed active artifact and fixture artifact are accepted by the current
  serial dry-run tooling
- this branch does not change the committed active profile artifact or the
  committed fixture profile artifact relative to `origin/configurator`

## Required fixture fields

The fixture for this document must preserve these top-level fields:

- `schema_name=glyph_config_json_compatibility_cases`
- `case_version=1`
- `status=repo_committed_fixture_compatibility_only`
- `hardware_status=not_new_hardware_result`
- `official_configurator_compatibility_claimed=false`
- `device_write_implemented=false`

## Non-goals

- not official configurator source authority
- not firmware source
- not runtime-loaded config
- not serial/device write behavior
- not hardware validation

## Checker inputs

`tools/check_glyph_config_json_compatibility_fixtures.py` loads and validates:

- `docs/calibration/fixtures/glyph_config_json_compatibility_cases_2026-06-03.json`
- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`
- `tools/check_glyph_smashbox_identity_runtime_bindings.py`
- `tools/check_glyph_ultimate_identity_profile_baseline.py`
- `tools/check_glyph_serial_config_writer.py`
- `tools/check_glyph_active_profile_binding_path.py`

Passing this checker confirms repo-committed fixture compatibility only. It
does not claim official configurator compatibility, firmware source authority,
runtime-loaded config support, serial/device write behavior, or hardware
validation.

## Checker output

`tools/check_glyph_config_json_compatibility_fixtures.py` prints:

- `glyph_config_json_compatibility_fixtures`
- `status=PASS` or `status=FAIL`
- `cases=<N>`
- `official_configurator_compatibility_claimed=false`
- `hardware_status=not_new_hardware_result`
