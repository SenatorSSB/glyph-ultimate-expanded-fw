# Official Configurator Export Target Docs

This directory is reserved for offline-only, source-backed export-target
contract documentation and preview fixtures.

Rules:

- do not add production export output here;
- do not add device-write or WebSerial workflows here;
- do not add runtime-loaded config implementation here;
- do not add firmware flashing automation here;
- do not claim official configurator compatibility here;
- keep preview fixtures explicitly labeled offline-only and non-production.

Firmware flashing automation is not implemented or approved by this offline
export-target workflow.

## Files

- `official_configurator_export_source_authority.md`
- `official_configurator_export_target_contract.md`
- `official_configurator_export_validation_report.md`
- `official_configurator_export_candidate_diff_report.md`
- `official_configurator_manual_import_export_test_plan.md`
- `official_configurator_manual_import_export_result_TEMPLATE.md`
- `fixtures/official_configurator_export_candidate_preview.json`
- `fixtures/official_configurator_export_invalid_cases.json`
- `fixtures/official_configurator_export_mutation_cases.json`
- `fixtures/official_configurator_export_validation_report.json`
- `fixtures/generated_official_configurator_candidate_preview.json`
- `fixtures/generated_official_configurator_candidate_preview_report.json`
- `fixtures/official_configurator_export_candidate_diff_report.json`
- `fixtures/official_configurator_manual_import_export_test_plan.json`

## Offline Workflow Tools

- `tools/check_glyph_official_configurator_export_target_contract.py` validates
  the source-authority packet, target contract, preview fixture, and invalid
  corpus.
- `tools/check_glyph_official_configurator_export_validation_report.py`
  validates the offline validation report and mutation cases.
- `tools/glyph_official_configurator_export_candidate_dry_run.py` creates a
  deterministic offline dry-run preview metadata fixture; it does not create
  production export output.
- `tools/check_glyph_official_configurator_export_candidate_dry_run.py`
  validates the generated dry-run preview and report.
- `tools/glyph_official_configurator_export_candidate_diff.py` creates an
  offline diff/simulation report between official fixtures and the generated
  preview; it does not claim real official configurator round-trip success.
- `tools/check_glyph_official_configurator_export_candidate_diff.py` validates
  the diff/simulation report and non-claims.
- `tools/check_glyph_official_configurator_manual_import_export_test_plan.py`
  validates the manual import/export test plan remains plan-only and not a
  result.
