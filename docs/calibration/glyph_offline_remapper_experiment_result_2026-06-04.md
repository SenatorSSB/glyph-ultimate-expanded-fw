# Glyph Offline Remapper Experiment Result - 2026-06-04

## CORRECTION / SOURCE MISATTRIBUTION

User clarification on 2026-06-06 supersedes the source attribution in this
historical packet. The user did not use or touch the custom external remapper
repo/app for `GlyphUserProfilesDefault.json` or
`GlyphUserProfilesBackAndForth.json`. Those files are official Glyph
configurator app artifacts and are now captured under
`docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/`.

This historical external/offline remapper packet is quarantined as
non-authoritative and pending correction unless independently source-backed. It
must not be used as primary corpus evidence or treated as user-executed external
remapper evidence for those files.

## Purpose and scope

This records a manual no-device external-remapper import/export experiment using the external app at `https://lyseste.com/glyph-remapper/`.

Scope is limited to docs, tools, and fixtures. This is not hardware validation, not official configurator compatibility, not firmware behavior validation, not adapter implementation, not WebSerial/device write behavior, not runtime-loaded config, and not protobuf binary generation.

## Experiment status

Status: manual no-device experiment completed with warnings.

The external remapper could import and export the active profile artifact. The resulting visual/function representation was not faithful to firmware-owned identity-runtime custom behavior.

## Source inputs

Primary input artifact:

- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- SHA-256: `0a9c70f6a0c1bb8c347a811df2ec327c176482dc9c35f433c45bd3454e704707`

Prior readiness chain:

- `docs/calibration/glyph_offline_remapper_experiment_readiness_index_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_experiment_readiness_index_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_result_template_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_result_TEMPLATE_2026-06-03.json`

## External app

- URL: `https://lyseste.com/glyph-remapper/`
- Visible version or commit: not reported.
- Browser/OS environment: not recorded in the chat report.
- Uploaded/exported JSON filename: `GlyphUserProfiles.json`

The screenshot observation is recorded textually only; no screenshot binary is committed.

## Safety boundary

No Glyph was connected. Connect/WebSerial access was not used. Save to Device was not clicked.

No WebSerial access was granted, no device write was attempted, and no firmware flashing was attempted.

## Result rows

| Row ID | Status | Result |
| --- | --- | --- |
| ENV-001 | PARTIAL | Browser/OS not recorded yet unless inferable from user report. |
| SRC-001 | PARTIAL | App URL recorded; visible version/commit not reported. |
| INPUT-001 | PASS | Active profile artifact used as primary candidate. |
| IMPORT-001 | PASS_WITH_WARNINGS | Import succeeded, but representation warning observed. |
| EXPORT-001 | PASS | Exported JSON received and committed as fixture. |
| DIFF-001 | PENDING | Structural/semantic diff to be expanded in future branch. |
| FIELDS-001 | PENDING | Accepted/rejected field list to be expanded in future branch. |
| DEVICE-001 | PASS | No live Glyph connected. |
| WS-001 | PASS | Connect/WebSerial access not used. |
| SAVE-001 | PASS | Save to Device not clicked. |
| AUTH-001 | PASS | No source-authority promotion and no official compatibility claim. |
| CLAIM-001 | PASS | No hardware validation claim. |

## Exported artifact

The user manually imported the active profile artifact into the external remapper, exported JSON, and saved the exported JSON locally as `GlyphUserProfiles.json`.

The exported JSON fixture is committed at:

- `docs/calibration/fixtures/glyph_offline_remapper_exported_GlyphUserProfiles_2026-06-04.json`
- SHA-256: `0a782564bd454c50e3fbeccc754acaec6c6ffdc6e0dcff145eef9121b7a3b39b`

The exported JSON fixture is a distinct artifact. It must not be treated as byte-identical to the input artifact unless a checker proves that. It must not replace the committed active profile artifact and must not be used as firmware input.

The exported file was copied into the repo without deterministic pretty-print normalization.

## Import/export interpretation

Import/export path: succeeded with warnings.

The active profile imported, and the external app exported JSON that parses as an object with `gameModeConfigs`, `communicationBackendConfigs`, `rgbConfigs`, and a `MODE_ULTIMATE` game mode entry.

This suggests profile-level import/export works for the manual no-device path, but it does not prove official configurator compatibility, firmware behavior validation, source authority, adapter correctness, runtime-loaded config support, WebSerial/device write behavior, or hardware validation.

## Functional representation warning

The app rendered a layout screenshot after import/export. The Ultimate profile showed a few D-pad buttons visible as a new thing. Otherwise, the representation was likely not functioning properly.

Interpretation: the visual/function representation was not faithful to firmware-owned identity-runtime custom behavior. The external remapper rendered/imported/exported the profile, but it did not faithfully represent firmware-owned identity-runtime custom behavior.

## Source-authority boundary

This result does not promote the external remapper to source authority.

The exported JSON is sidecar evidence for a manual no-device external-remapper import/export experiment only. It is not a firmware source, not a Senscope neutral-profile schema source, not a game-semantic source, and not an official configurator compatibility source.

## No-device/no-WebSerial/no-write confirmation

- No Glyph was connected.
- Connect was not clicked.
- WebSerial access was not granted.
- Save to Device was not clicked.
- No device write was attempted.
- No firmware flashing was attempted.

## Non-goals and forbidden interpretations

Do not interpret this result as:

- hardware validation;
- official configurator compatibility;
- firmware behavior validation;
- adapter implementation;
- WebSerial/device write behavior;
- runtime-loaded config;
- protobuf binary generation;
- source-authority promotion;
- permission to replace the active profile artifact;
- permission to use the exported JSON as firmware input.

No adapter implementation was added by this result packet.

## Follow-up recommendations

- Add a structural diff checker for exported JSON versus the committed active profile artifact.
- Record browser/OS and external app version/commit in any future repeated experiment.
- Expand accepted/rejected field lists in a future branch.
- Do not implement adapter generation from this result alone.
