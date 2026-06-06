# Glyph Export Corpus Readiness Status - 2026-06-06

## Purpose and scope

This packet records the current export-corpus state for future Glyph profile and
config JSON compatibility work. It is docs/tools-only and does not invent,
capture, or ingest corpus artifacts.

Current status:

- `blocked_missing_real_corpus_artifacts`
- Corpus present: false
- Completion allowed: false

## Current protocol and checker sources

Current source packets and checkers:

- Export corpus protocol:
  `docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md`
- Export corpus manifest template:
  `docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json`
- Export corpus checker:
  `tools/check_glyph_profile_config_export_corpus.py`
- Export corpus root:
  `docs/calibration/export_corpus/`
- Roadmap next-work index:
  `docs/calibration/glyph_roadmap_next_work_index_2026-06-06.md`

The corpus root currently contains only repository guidance and no real `manifest.json` corpus capture.

## Current missing artifacts

The required real matched-version corpus artifacts are missing:

- per-corpus directory under `docs/calibration/export_corpus/<corpus_id>/`;
- filled `manifest.json`;
- captured exported JSON files under `fixtures/`;
- hashes for captured files;
- configurator source/version provenance;
- firmware and repo commit provenance;
- semantic feature labels for captured files;
- known-unknowns recorded from the capture session.

## Required future corpus structure

A future completed corpus must use the protocol layout:

```text
docs/calibration/export_corpus/
  <corpus_id>/
    manifest.json
    fixtures/
      glyph_export__<configurator_version_label>__<device_model>__<case_id>__<captured_at_utc>.json
```

Each real corpus must include a filled manifest with:

- `corpus_id`
- `captured_at`
- `captured_by`
- `glyph_repo_commit`
- `firmware_source_commit`
- `configurator_source_reference`
- `configurator_version_label`
- `device_model`
- `hardware_required`
- `source_kind`
- `fixture_files`
- `expected_semantic_features`
- `known_unknowns`
- `notes`

## What counts as captured corpus

Captured corpus means real export files from a matched configurator/version
context, listed by a filled manifest, with each listed fixture present on disk.
Template files, README files, repo-local example fixtures, external remapper
observations, and generated candidate payloads do not count as captured corpus.

## Required hashes and records

Future corpus capture must record:

- SHA-256 for every captured export file;
- the manifest path and fixture paths;
- browser/tooling and configurator version or source reference;
- device model and firmware/source commit provenance;
- whether hardware was required for the capture;
- semantic-feature labels expected from the captured files;
- unresolved unknowns instead of inferred behavior claims.

## Explicit non-claims

- No official configurator authority claim is made here.
- No device write or WebSerial claim is made here.
- No hardware validation claim is made here.
- No adapter implementation is made here.
- No external remapper adapter output is generated here.
- No runtime-loaded config is implemented here.
- No firmware behavior changes are made here.
- No active profile artifact changes are made here.

## Future branch policy

Future corpus capture may proceed only when real corpus artifacts are available
and the protocol can be followed without user/domain choices. If artifact source,
version provenance, or capture interpretation is unclear, stop and ask for the
missing corpus input instead of recording completion.
