# Current Official Configurator Validation Lane

Status: `OFFLINE_CURRENT_LANE_CLASSIFICATION_ONLY`

The current lane is a bounded offline aggregate over the committed
`primary_official_configurator_corpus`. It runs the export-corpus, corpus-diff,
export-target, candidate-diff, and validation-report checks.

`tools/check_glyph_import_export_compatibility.py` remains a historical-only
compatibility chain. Its generated-prototype/runtime anchor is not rewritten
to manufacture a current pass. External-remapper evidence remains quarantined
and is not promoted into the current lane.

This lane does not claim official configurator compatibility, universal
compatibility, production export, device write, runtime-loaded config, or
firmware flashing.

Run it offline with:

```text
python3 tools/check_glyph_official_configurator_validation.py
```

The classification fixture and its adversarial promotion check are at
`docs/export/fixtures/official_configurator_validation_lane.json`.
