# Glyph Export Corpus Final Blocker Status - 2026-06-06

## Purpose and scope

This packet consolidates the current export-corpus blocker state for the Glyph
profile/config export workstream.

It is docs/tools-only. It does not invent corpus artifacts, does not ingest
exports, does not implement adapter output, and does not change firmware,
profile artifacts, or transport behavior.

Current status:

- `blocked_missing_real_corpus_artifacts`
- Corpus present: false
- Completion allowed: false

## Current source protocol inputs

This packet is grounded in the existing corpus protocol and read-only checker
boundary:

- Export corpus protocol:
  `docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md`
- Export corpus manifest template:
  `docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json`
- Export corpus checker:
  `tools/check_glyph_profile_config_export_corpus.py`
- Export corpus directory guide:
  `docs/calibration/export_corpus/README.md`
- Export corpus readiness packet:
  `docs/calibration/glyph_export_corpus_readiness_status_2026-06-06.md`
- Export corpus readiness fixture:
  `docs/calibration/fixtures/glyph_export_corpus_readiness_status_2026-06-06.json`
- Export corpus readiness checker:
  `tools/check_glyph_export_corpus_readiness_status.py`

The export-corpus directory currently contains only the README guidance and no
real `manifest.json` corpus capture.

## What counts as real corpus

Real corpus means matched-version export captures written to
`docs/calibration/export_corpus/<corpus_id>/` with a filled `manifest.json` and
listed fixture files that actually exist on disk.

Template files, README guidance, repo examples, generated candidate payloads,
and external observations do not count as captured corpus.
Template files, README guidance, repo examples, generated candidate payloads, and external observations do not count as captured corpus.

## What is still missing

The current repository state is missing these artifact classes:

- `filled_manifest_json`
- `captured_export_json_fixtures`
- `fixture_sha256_hashes`
- `glyph_repo_commit_reference`
- `firmware_source_commit_reference`
- `configurator_source_reference`
- `configurator_version_label`
- `device_model_or_capture_context`
- `expected_semantic_feature_labels`
- `known_unknowns`

## Required future artifacts

Future corpus capture must provide:

- one or more real corpus subdirectories under
  `docs/calibration/export_corpus/<corpus_id>/`;
- a filled `manifest.json` per corpus directory;
- captured export JSON fixtures under `fixtures/`;
- SHA-256 hashes for every captured export file;
- explicit `glyph_repo_commit` provenance;
- explicit firmware source commit provenance;
- explicit configurator source reference and version label;
- explicit device model or capture context;
- explicit expected semantic feature labels;
- explicit known unknowns instead of inferred behavior claims.

## Required hashes and provenance

Any future complete corpus must record:

- SHA-256 for every captured export fixture;
- the manifest path and every listed fixture path;
- `glyph_repo_commit`;
- `firmware_source_commit`;
- `configurator_source_reference`;
- `configurator_version_label`;
- `device_model`;
- whether hardware was required for capture;
- expected semantic feature labels;
- unresolved unknowns instead of behavior inferences.

## Explicit non-claims

- No official configurator authority claim is made here unless source-backed.
- No device write or WebSerial claim is made here.
- No runtime-loaded config is implemented here.
- No adapter implementation is made here.
- No external remapper adapter output is generated here.
- No hardware validation claim is made here.
- No external source authority promotion is made here.
- No firmware behavior changes are made here.
- No active profile artifact changes are made here.

## Future branch policy

Future export-corpus capture may proceed only when real corpus artifacts are
available and the protocol can be followed without inventing provenance.

If artifact source, version provenance, or capture interpretation is unclear,
stop and ask for the missing corpus input instead of recording completion.
