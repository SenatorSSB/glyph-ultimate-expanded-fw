# Glyph External Remapper Source Snapshot Index - 2026-06-03

## Purpose and scope

This document records a docs/tools-only, non-authoritative snapshot index for
the external Open Glyph Remapper public repo and hosted app.

It is a source-discovery index only. It is not firmware source authority, not
official configurator authority, not device write behavior, not runtime-loaded
config, and not hardware validation.

No external source copied into this repo. No external dependency was added. This
branch does not implement WebSerial, serial/device write behavior,
runtime-loaded config, generated firmware source, protobuf/config/schema
behavior changes, profile artifact changes, or hardware validation.

## External references

- External repo URL: `https://github.com/lyseste/glyph-remapper`
- External app URL: `https://lyseste.com/glyph-remapper/`
- Snapshot date: `2026-06-03`
- Inspected date: `2026-06-03`
- Access method:
  - GitHub contents API root inventory
  - public README raw fetch
  - hosted app HTML fetch
  - bounded raw `app.js` excerpt fetch

These observations are non-authoritative snapshot notes. They must not be used
as firmware source authority, official configurator authority, external source
dependency approval, device write behavior evidence, runtime-loaded config
evidence, or hardware validation evidence.

Required caveat phrases:

- non-authoritative snapshot
- no external source copied
- not firmware source authority
- not official configurator authority
- not device write behavior
- not runtime-loaded config
- not hardware validation

## Observed file inventory

| File | Kind | Provenance | Notes |
| --- | --- | --- | --- |
| `README.md` | README/docs | observed_from_external_repo_docs | README describes project layout, data model, WebSerial flow, protobuf, mode system, keyboard mode, custom mode, and JSON import/export. |
| `app.js` | app/script JS | observed_from_external_code_excerpt | Root inventory lists the file; a bounded excerpt showed inline `PROTO_DEF` and button layout constants. No external source copied. |
| `index.html` | index HTML | observed_from_external_code_excerpt | Hosted HTML showed toolbar, profile sidebar, controller SVG, settings panel, SOCD, RGB, remap, custom mode, import/export, and `app.js` include labels. |
| `styles.css` | CSS | not_verified | Root inventory lists the CSS file, but CSS contents were not audited for this snapshot. |
| `glyph-config.json` | default config payload | observed_from_external_repo_docs | Root inventory lists a default config payload; README describes `DEFAULT_CONFIG_JSON` with an embedded Load Defaults payload. Payload contents were not imported. |
| `app.js::PROTO_DEF` | inline protobuf/schema | observed_from_external_code_excerpt | A bounded `app.js` excerpt showed an inline `PROTO_DEF` string; no separate `.proto` file was observed in the root inventory. |
| `LICENSE` | license | not_verified | Root inventory lists the file, but license terms were not audited in this snapshot. |

## Observed feature categories

| Feature category | Provenance | Observation |
| --- | --- | --- |
| browser configurator | observed_from_external_repo_docs | README describes a browser-based configurator and hosted app URL. |
| visual layout | observed_from_external_code_excerpt | Hosted HTML includes a controller SVG area and platform display tabs; bounded `app.js` excerpt showed button layout constants. |
| per-button remap | observed_from_external_repo_docs | README describes popup remap behavior and physical-to-physical remapping. |
| profile management | observed_from_external_code_excerpt | Hosted HTML includes profile list, profile count, new profile, rename, and duplicate UI labels. |
| RGB/color palette | observed_from_external_code_excerpt | Hosted HTML includes Button Lighting, RGB animation, color swatch, hex input, saved color, and clear/apply labels. |
| SOCD | observed_from_external_code_excerpt | Hosted HTML includes SOCD Pairs and add SOCD pair UI labels; README data model describes `socdPairs`. |
| keyboard capture | observed_from_external_repo_docs | README describes keyboard mode capture and HID keycode behavior. |
| JSON import/export | observed_from_external_repo_docs | README describes offline JSON export/import; hosted HTML includes Config File import/export controls. |
| protobuf encode/decode | observed_from_external_repo_docs | README describes `configToBinary`, `binaryToConfig`, protobuf.js, and an inline `PROTO_DEF` schema. |
| WebSerial load/save | observed_from_external_repo_docs | README describes Connect, Load Config, Save to Device, and WebSerial load/save flow. This repo does not implement device write behavior. |
| custom profile/modifier support claim | observed_from_external_repo_docs | README describes `MODE_CUSTOM`, `CustomModeConfig`, modifier groups, analog trigger mappings, and custom-mode UI sections. |

## Access gaps

- No full source audit was performed.
- No external repo source was copied into this repository.
- No external repo dependency was added.
- No external license review was completed.
- No Glyph device, WebSerial session, serial write, or hardware validation was
  performed.
- No separate public-post URL was supplied for this snapshot; custom mode and
  modifier support were observed from external repo README docs only.
- External compatibility claims were not promoted to firmware source authority
  or official configurator authority.

## Forbidden interpretations

The snapshot fixture must keep these forbidden interpretations explicit:

- `firmware_source_authority`
- `official_configurator_authority`
- `copied_source`
- `imported_dependency`
- `device_write_implementation`
- `runtime_loaded_config_implementation`
- `hardware_validation`

## Required fixture fields

The fixture for this report must preserve these top-level fields:

- `schema_name=glyph_external_remapper_source_snapshot_index`
- `snapshot_version=1`
- `status=external_non_authoritative_snapshot_index`
- `hardware_status=not_new_hardware_result`
- `external_source_promoted_to_authority=false`
- `code_copied_into_repo=false`
- `device_write_implemented=false`
- `runtime_loaded_config_implemented=false`

## Checker output

`tools/check_glyph_external_remapper_source_snapshot_index.py` prints:

- `glyph_external_remapper_source_snapshot_index`
- `status=PASS` or `status=FAIL`
- `observed_features=<N>`
- `external_source_promoted_to_authority=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that this docs/tools-only snapshot index
preserves the required non-authority, no-copy, no-device-write,
no-runtime-loaded-config, and no-hardware-validation constraints. It does not
require live external network access and does not promote any external source to
authority.
