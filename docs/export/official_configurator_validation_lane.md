# Retired Official Configurator Evidence Lane

Status: `RETIRED_HISTORICAL_EVIDENCE_ONLY`

Official Glyph configurator interoperability is no longer a product,
development, validation, or progression dependency for the custom
Glyph/Senscope firmware path. `GP-CONFIG-002` is invalidated by
`GLYPH-UD-007`; no operator capture is required or awaited. Reopening the lane
requires a later explicit user decision.

The preserved `primary_official_configurator_corpus` and its export-corpus,
corpus-diff, export-target, candidate-diff, and validation-report checks remain
historical integrity evidence only. The retired aggregate verifies their
classification and presence but does not execute branch-scoped historical
checks. Running any preserved check separately does not reactivate the lane.

`tools/check_glyph_import_export_compatibility.py` remains a historical-only
compatibility chain. Its generated-prototype/runtime anchor is not rewritten
to manufacture a current pass. External-remapper evidence remains quarantined
and is not promoted into the current lane.

This historical evidence does not claim official configurator compatibility, universal
compatibility, production export, device write, runtime-loaded config, or
firmware flashing.

Validate preserved historical integrity offline with:

```text
python3 tools/check_glyph_official_configurator_validation.py
```

The retired classification fixture and its adversarial promotion/dependency
checks are at
`docs/export/fixtures/official_configurator_validation_lane.json`.
