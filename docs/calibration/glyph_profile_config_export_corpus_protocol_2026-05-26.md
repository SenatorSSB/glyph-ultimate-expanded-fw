# Glyph Profile/Config Export Corpus Protocol - 2026-05-26

## Scope

This document defines a **read-only export-corpus capture protocol** for Glyph profile/config JSON semantics.

This batch is limited to:

- documentation;
- fixture/corpus organization;
- manifest contracts;
- read-only validation checks.

This batch does **not** implement:

- write-capable profile adapters;
- firmware runtime changes;
- SOCD/remap semantic changes;
- push-to-device/flashing automation;
- vendor export format reverse engineering.

## Label legend

- `source-confirmed`: backed by inspected repo source/docs.
- `fixture-observed`: observed in repo-local JSON fixtures only.
- `corpus-required`: requires matched-version captured exports.
- `unknown`: not established by current source/fixtures.

## Why this corpus is needed

- `source-confirmed`: firmware persistence/transport authority is protobuf/binary (`config.bin` + CRC header, protobuf get/set config transport), not JSON export semantics.
- `fixture-observed`: repo JSON fixtures show useful patterns (for example frequent omitted `activates`) but cannot prove canonical configurator serializer/importer rules.
- `corpus-required`: future Senscope-to-Glyph adapter safety requires matched-version export evidence for omission/default/enum-zero behaviors before any write-capable implementation.

## Source authority this corpus is meant to capture

The corpus captures host-side behavior that is not proven by firmware source alone:

- `corpus-required`: matched configurator JSON export shape and field-presence policy.
- `corpus-required`: behavior of omitted fields vs explicit enum/string representations in exported JSON.
- `corpus-required`: observed profile ordering/default index serialization for a specific configurator/firmware pairing.
- `corpus-required`: backend/profile filtering effects visible in export outputs.

## What this corpus cannot prove

- `unknown`: canonical behavior for configurator versions not captured.
- `unknown`: equivalence between omitted `activates` and explicit `BTN_UNSPECIFIED` unless both are captured and source-linked for the same matched version.
- `unknown`: gameplay semantics, thresholds, or Smash-domain meaning.
- `unknown`: device write/apply behavior beyond documented transport/persistence source.

## Existing fixtures vs future matched-version captures

- Existing repo fixtures (`docs/sources/raw/...`, `docs/calibration/fixtures/...`) are `fixture-observed` inputs and must remain treated as examples.
- Future captured exports under `docs/calibration/export_corpus/...` are `corpus-required` evidence tied to explicit metadata (commit/version/model/capture context).
- Neither fixture class should be treated as universal truth across configurator revisions without version linkage.

## Recommended corpus directory layout

```text
docs/calibration/export_corpus/
  README.md
  <corpus_id>/
    manifest.json
    fixtures/
      glyph_export__<configurator_version_label>__<device_model>__<case_id>__<captured_at_utc>.json
```

Notes:

- one directory per `corpus_id`.
- one `manifest.json` per corpus directory.
- fixtures are immutable after capture; append new captures as new files/new corpus IDs.

## Fixture naming convention

Use:

```text
glyph_export__<configurator_version_label>__<device_model>__<case_id>__<YYYYMMDDTHHMMSSZ>.json
```

Token rules:

- lowercase ASCII, digits, `_` and `-` only;
- replace spaces with `-`;
- keep `case_id` stable and human-meaningful (example: `ultimate-omitted-activates`).

## Required manifest fields

Each corpus `manifest.json` must include:

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

Field intent:

- `glyph_repo_commit`: repo commit used during capture.
- `firmware_source_commit`: firmware source authority reference for the tested device/config.
- `configurator_source_reference`: URL/commit/tag/release identifier for host configurator source or build provenance.
- `source_kind`: expected values should distinguish fixture provenance (for example `matched-version-export-capture`).
- `fixture_files`: relative paths from manifest directory.
- `expected_semantic_features`: checklist labels expected for captured files (not inferred behavior claims).
- `known_unknowns`: unresolved gaps that still block write-policy decisions.

## Exact capture procedure (human tester)

1. Select target versions and record them before capture:
   - `glyph_repo_commit`;
   - firmware source commit running on target device;
   - configurator source reference + version label.
2. Create a new corpus directory at `docs/calibration/export_corpus/<corpus_id>/`.
3. Copy the template manifest and fill known metadata fields (leave unknowns explicit, do not invent).
4. In the matched configurator version, prepare each targeted test case manually.
5. Export JSON through the configurator UI (read-only capture; no flashing/push automation in this protocol).
6. Save each export into `fixtures/` using the naming convention.
7. Add each file path to `fixture_files` in `manifest.json`.
8. For each fixture, add expected semantic-feature labels in `expected_semantic_features`.
9. Record unresolved behavior as `known_unknowns` instead of assumptions.
10. Run read-only checkers:
    - `tools/check_glyph_profile_config_semantics.py` (repo fixture baseline);
    - `tools/check_glyph_profile_config_export_corpus.py` (template + corpus structure/feature reporting).
11. If checks fail structurally, fix manifest/file placement only; do not alter captured exports to force assumptions.
12. Commit corpus additions with capture metadata and checker results.

## Edge-case capture matrix (required targets)

Each item below is a capture target label, not a proven behavior claim.

- `omitted-activates`
  - `fixture-observed`: present in repo fixtures.
  - `corpus-required`: confirm whether matched configurator exports this form in target cases.
- `explicit-disabled-btn-unspecified`
  - `source-confirmed`: explicit `BTN_UNSPECIFIED` exists in firmware default config/runtime semantics.
  - `corpus-required`: capture whether configurator can emit explicit disabled/unmapped entries.
- `many-to-one-remap-aliases`
  - `source-confirmed`: runtime remap OR behavior supports many-to-one targets.
  - `corpus-required`: capture export representation.
- `duplicate-physical-remap-entries`
  - `source-confirmed`: runtime ignores later duplicates for same physical button.
  - `corpus-required`: capture whether configurator allows/exports duplicates.
- `omitted-defaultModeConfig`
  - `fixture-observed`: seen in repo fixtures for configurator backend.
  - `corpus-required`: confirm in matched exports.
- `defaultModeConfig-zero`
  - `source-confirmed`: firmware validation allows `default_mode_config == 0`.
  - `corpus-required`: capture if configurator can represent/export zero explicitly.
- `omitted-socdType`
  - `fixture-observed`: seen in repo fixtures.
  - `corpus-required`: confirm matched export behavior.
- `profile-count-and-default-ordering`
  - `source-confirmed`: one-based default index handling in runtime code.
  - `corpus-required`: capture export ordering/default fields for real profiles.
- `applicable-backend-filtering`
  - `source-confirmed`: used in menu visibility/filtering.
  - `corpus-required`: capture export manifestation and any omissions/restrictions.

## Checker policy for this batch

- read-only checks only;
- no mutation of captured files;
- no synthesis of missing export data;
- no write-policy decisions for omitted vs explicit disabled encodings.

## Explicit non-goals

- no firmware runtime behavior change;
- no configurator behavior change;
- no SOCD/remap logic change;
- no profile schema/proto mutation;
- no device flashing/push automation;
- no adapter write implementation.
