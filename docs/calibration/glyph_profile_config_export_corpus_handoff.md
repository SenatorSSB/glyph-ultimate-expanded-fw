# Glyph Profile/Config Export Corpus Handoff

Date: 2026-05-26

## What was added

- `docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md`
  - Defines corpus purpose, source authority boundaries, non-goals, manifest contract, directory layout, naming convention, and human capture procedure.
  - Includes required edge-case capture targets with labels: `source-confirmed`, `fixture-observed`, `corpus-required`, `unknown`.
- `docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json`
  - Valid JSON template with required manifest fields and placeholder values only.
- `tools/check_glyph_profile_config_export_corpus.py`
  - Read-only stdlib checker for template validity and real corpus manifest/file validation.
  - Integrates existing fixture semantics analyzer to report omission/alias/duplicate/default-field signals.
  - Passes in template-only state with explicit no-real-corpus message.
- `docs/calibration/export_corpus/README.md` (optional helper)
  - Documents where real matched-version export captures should live.

## What was not captured yet

- No real matched-version configurator export corpus files were added in this batch.
- No new `docs/calibration/export_corpus/<corpus_id>/manifest.json` entries were added.
- No captured export fixtures were added under `docs/calibration/export_corpus/*/fixtures/`.

## Runtime/source behavior changes

- Runtime behavior changed: none.
- Firmware source behavior changed: none.
- Configurator behavior changed: none.

## Exact next user actions to capture real exports

1. Choose and record one matched version tuple:
   - `glyph_repo_commit`
   - firmware source commit running on the device
   - configurator source reference + version label
2. Create `docs/calibration/export_corpus/<corpus_id>/`.
3. Copy `docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json` to `docs/calibration/export_corpus/<corpus_id>/manifest.json` and fill known metadata.
4. In the matched configurator, prepare and export JSON fixtures for each required edge case:
   - omitted `activates`
   - explicit disabled/unmapped (`BTN_UNSPECIFIED`) if emitter supports it
   - many-to-one remap aliases
   - duplicate physical remap entries
   - omitted `defaultModeConfig`
   - `defaultModeConfig = 0` if representable
   - omitted `socdType`
   - profile count/default profile ordering behavior
   - applicable backend filtering
5. Save each export under `docs/calibration/export_corpus/<corpus_id>/fixtures/` using the documented naming convention.
6. List each file in `fixture_files` and annotate `expected_semantic_features` + `known_unknowns` in the manifest.
7. Run:
   - `.venv/bin/python tools/check_glyph_profile_config_semantics.py`
   - `.venv/bin/python tools/check_glyph_profile_config_export_corpus.py`
8. Commit corpus additions once manifest + fixture checks pass.

## Next branch recommendation after real corpus exists

- Recommended next branch after at least one populated corpus: `glyph/profile-config-export-corpus-validation`.
- Intended focus for that branch:
  - strengthen corpus checks for cross-fixture consistency;
  - add corpus-backed regression assertions;
  - keep adapter writes deferred until corpus review sign-off.

## Verification commands run

- `.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py`: PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py`: PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py`: PASS
- `.venv/bin/python tools/check_glyph_profile_config_semantics.py`: PASS
- `.venv/bin/python tools/check_glyph_profile_config_export_corpus.py`: PASS (`no_real_corpus_present=true`, template-only state accepted)
- `grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true`: PASS (no conflict markers)
- `git diff --check`: PASS
- `git status --short`: PASS (expected new files only)
