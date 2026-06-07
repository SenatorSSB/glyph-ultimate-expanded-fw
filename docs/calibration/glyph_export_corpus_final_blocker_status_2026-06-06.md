# Glyph Export Corpus Final Blocker Status - 2026-06-06

## Purpose and scope

This packet consolidates the current export-corpus blocker state for the Glyph
profile/config export workstream after the official configurator corpus source
correction.

It is docs/tools-only. It ingests the two user-provided official Glyph
configurator JSON exports into the export corpus, but it does not implement
adapter output and does not change firmware, profile artifacts, or transport
behavior.

Current status:

- `official_configurator_corpus_present_initial`
- Corpus present: true
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
- Official configurator corpus manifest:
  `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`
- Official configurator corpus notes:
  `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/notes.md`
- Official configurator corpus checker:
  `tools/check_glyph_official_configurator_export_corpus.py`
- Official configurator structural diff:
  `docs/calibration/glyph_official_configurator_corpus_diff_2026-06-06.md`
- Official configurator structural diff fixture:
  `docs/calibration/fixtures/glyph_official_configurator_corpus_diff_2026-06-06.json`
- External-remapper misattribution correction:
  `docs/calibration/glyph_external_remapper_misattribution_correction_2026-06-06.md`

The export-corpus directory now contains a real official configurator corpus
manifest and two user-provided official configurator JSON fixture files.

## What counts as real corpus

Real corpus means export captures written to
`docs/calibration/export_corpus/<corpus_id>/` with a filled `manifest.json` and
listed fixture files that actually exist on disk.

Template files, README guidance, repo examples, generated candidate payloads,
and external observations do not count as captured corpus.

The official configurator corpus exists with two user-provided fixture files:

- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json`

## What is still missing

The current repository state is no longer missing real export corpus artifacts.
The remaining missing or unresolved metadata/blockers are:

- `configurator_source_reference`
- `configurator_version_label`
- exact capture timestamp
- exact push/download route details
- write-behavior source authority
- explicit implementation approval

## Required future artifacts

Future work should provide or confirm:

- explicit configurator source reference and version label;
- exact capture timestamp and push/download route details if needed;
- explicit source authority for any write-capable behavior;
- explicit user approval before adapter implementation.

## Required hashes and provenance

The current official configurator corpus records:

- SHA-256 for every captured export fixture;
- the manifest path and every listed fixture path;
- `glyph_repo_commit`;
- `firmware_source_commit`;
- `device_model`;
- whether hardware was required for capture;
- unresolved unknowns instead of behavior inferences.

The corpus still records `configurator_source_reference` and
`configurator_version_label` as `UNKNOWN_NOT_PROVIDED`.

## Explicit non-claims

- The official configurator corpus is source-backed as user-provided official
  configurator export-shape evidence.
- No device write or WebSerial claim is made here.
- No runtime-loaded config is implemented here.
- No adapter implementation is made here.
- No external remapper adapter output is generated here.
- No hardware validation claim is made here.
- No external source authority promotion is made here.
- No firmware behavior changes are made here.
- No active profile artifact changes are made here.

## Future branch policy

Future export-corpus expansion may proceed when additional real corpus artifacts
or missing metadata are available and the protocol can be followed without
inventing provenance.

If artifact source, version provenance, or capture interpretation is unclear,
stop and ask for the missing corpus input instead of recording completion.
