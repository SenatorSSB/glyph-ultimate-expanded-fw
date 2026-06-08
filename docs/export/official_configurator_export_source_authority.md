# Official Configurator Export Target Source Authority

Status label: `OFFLINE_SOURCE_AUTHORITY_RECORDED`.

## Purpose

This packet records the source authority for a future offline official
configurator export target contract.

It is source authority for the observed official configurator JSON shape only.
It is not production export output, not device write, not WebSerial, not
runtime-loaded config, not firmware flashing automation, and not an official
compatibility claim.

## Inspected Source And Search Scope

Inspected files:

- `README.md`
- `AGENTS.md`
- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/WORKFLOW.md`
- `docs/calibration/README.md`
- `docs/calibration/INDEX.md`
- `docs/calibration/archive_policy.md`
- `docs/release/public_manual_workflow_release_candidate_plan.md`
- `docs/release/public_manual_workflow_release_candidate_checklist.md`
- `docs/calibration/glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.md`
- `docs/calibration/export_corpus/README.md`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/notes.md`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json`
- `docs/calibration/glyph_external_remapper_misattribution_correction_2026-06-06.md`
- `docs/calibration/glyph_official_configurator_corpus_diff_2026-06-06.md`
- `docs/runtime_config/runtime_config_webserial_device_write_source_authority.md`
- `docs/runtime_config/runtime_config_manual_load_path_plan.md`
- `docs/runtime_config/runtime_config_device_write_safety_plan.md`
- `docs/runtime_config/runtime_config_firmware_binary_parser_source_authority.md`
- `docs/runtime_config/runtime_config_firmware_binary_parser_integration_plan.md`
- `tools/check_glyph_official_configurator_export_corpus.py`
- `tools/check_glyph_official_configurator_corpus_diff.py`
- `tools/glyph_official_configurator_corpus.py`

Searches run:

```text
rg -n "official glyph configurator|official configurator|GlyphUserProfilesDefault|GlyphUserProfilesBackAndForth|back-and-forth|export corpus|external remapper|lyseste|configurator compatibility|import export|profile json|profile|json compatibility|adapter|export target|candidate validator" README.md AGENTS.md docs tools config src HAL platformio.ini
find docs/calibration/export_corpus docs/release docs/runtime_config tools -maxdepth 6 -type f
```

## Manifest Status

The official corpus manifest is present at
`docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`.

It records:

- `corpus_id`: `official_glyph_configurator_2026-06-06`
- `source_kind`: `official_glyph_configurator_user_provided_export`
- `source_classification`: `primary_official_configurator_corpus`
- `captured_by`: `Rasmus / user-provided`
- `device_model`: `Glyph MK6`
- `hardware_required`: `true`
- known unknowns for exact app version, exact capture timestamp, and exact
  push/download route details

## Exact Fixture Files Identified

- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json`

Fixture hashes from the manifest:

- default profiles:
  `2d24324928f9c0292e3fce74f02083a740272eeb7a271437be10b7b4f6bf025e`
- back-and-forth custom profile:
  `0a782564bd454c50e3fbeccc754acaec6c6ffdc6e0dcff145eef9121b7a3b39b`

## Source Classification

- official Glyph configurator corpus: the manifest, notes, and the two
  user-provided JSON fixtures above;
- user-provided official configurator artifacts: the two JSON fixtures above;
- fixture-observed: the stable top-level keys, counts, and nested key sets
  observed in the fixtures;
- external-remapper quarantined: any `external_remapper`, `offline_remapper`,
  or `clean_room_adapter` record remains historical/non-authoritative unless
  independently source-backed;
- external-remapper records remain quarantined unless independently
  source-backed;
- inferred: that this observed JSON shape can inform an offline target contract
  for comparison work;
- unknown: any production export or official compatibility claim beyond the
  observed fixture shapes.

## Source-Backed Fields And Shapes

The following shapes are directly observed from the two official fixtures:

- top-level keys:
  `gameModeConfigs`, `communicationBackendConfigs`, `keyboardModes`,
  `rgbConfigs`, `defaultBackendConfig`, `defaultUsbBackendConfig`,
  `rgbBrightness`, `defaultDashboardOption`
- `gameModeConfigs`: 13 objects in each fixture
  - 12 entries share the key set
    `applicableBackends`, `buttonRemapping`, `layoutPlate`, `menuButtonIcon`,
    `modeId`, `name`, `rgbConfig`, `socdPairs`
  - 1 entry (`Keyboard` / `MODE_KEYBOARD`) uses
    `applicableBackends`, `keyboardModeConfig`, `layoutPlate`, `modeId`,
    `name`, `rgbConfig`, `socdPairs`
- `communicationBackendConfigs`: 8 objects in each fixture
  - 7 entries share `backendId`, `defaultModeConfig`
  - 1 entry uses `activationBinding`, `backendId`
- `keyboardModes`: 1 object with `buttonsToKeycodes`
- `rgbConfigs`: 13 objects with `animation`, `buttonColors`
- scalar defaults observed in both fixtures:
  - `defaultBackendConfig = 1`
  - `defaultUsbBackendConfig = 1`
  - `rgbBrightness = 255`
  - `defaultDashboardOption = DASHBOARD_MENU_BUTTON_HINTS`

The official corpus diff packet records the stable top-level key set and the
structural changes under `gameModeConfigs` and `rgbConfigs` between the two
fixtures. That is structural JSON evidence, not gameplay semantics.

## Unknowns

- exact official configurator app version;
- exact capture timestamp beyond the manifest date;
- exact push/download route details;
- any claim that the observed shape is universally supported by official
  configurator versions beyond the captured corpus;
- whether any future export target should be profile-scoped, global, or mixed
  beyond the observable top-level JSON shape.

## What Cannot Be Claimed

- no official configurator compatibility claim;
- no universal official configurator compatibility claim;
- no production export claim;
- no device write claim;
- no WebSerial claim;
- no runtime-loaded config claim;
- no firmware flashing automation claim;
- no nunchuk validation claim;
- no Senscope neutral profile schema change;
- no game-semantic change.

## Explicit Non-Claims

- this packet does not promote external-remapper evidence to primary authority;
- this packet does not claim the two fixtures are a production export target;
- this packet does not claim the observed shapes can be written directly to a
  device;
- this packet does not claim that the official configurator accepts any
  generated output without separate proof.
- this packet is not production export output.
- this packet is not device write.
- this packet is not WebSerial.
- this packet is not runtime-loaded config.
- this packet is not firmware flashing automation.
