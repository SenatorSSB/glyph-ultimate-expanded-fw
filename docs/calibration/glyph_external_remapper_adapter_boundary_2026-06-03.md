# Glyph External Remapper Adapter Boundary - 2026-06-03

## Purpose and scope

This document records a docs/tools-only boundary and gap report for possible
future comparison against the external Open Glyph Remapper project.

External observations are non-authoritative. They are not firmware authority,
not official configurator authority, not imported dependency evidence, not
device-write implementation evidence, not runtime-loaded config implementation
evidence, and not hardware validation.

This branch does not import external source, does not implement WebSerial,
does not implement serial/device write behavior, does not implement
runtime-loaded config, does not change protobuf/config/schema behavior, and
does not validate hardware.

## External references

- External repo URL: `https://github.com/lyseste/glyph-remapper`
- External app URL: `https://lyseste.com/glyph-remapper/`

The public repo was reachable through a non-copying Git ref probe and a
temporary shallow read-only clone outside this repo during supervisor
inspection. The hosted app URL is recorded as an external reference, but the
checker does not require live app access and this branch does not treat the
hosted app as source authority. These observations remain compatibility
research notes only.

Observed root file names from the temporary shallow read-only clone:

- `LICENSE`
- `README.md`
- `app.js`
- `glyph-config.json`
- `index.html`
- `styles.css`

## Observed scope

| Observation | Status | Notes |
| --- | --- | --- |
| browser configurator | observed_from_external_repo_docs | Public README describes a browser-based configurator. |
| profile editing | observed_from_external_repo_docs | Public README and repo static UI files expose profile editing labels. |
| JSON import/export | observed_from_external_repo_docs | Public README and repo static UI files expose JSON config file import/export. |
| RGB/color palette | observed_from_external_code | Repo static UI files expose button lighting, color swatch, saved color, and palette UI labels. |
| SOCD/profile management | observed_from_external_code | Repo static UI files expose profiles and SOCD pairs UI labels. |
| keyboard capture | observed_from_external_repo_docs | Public README describes keyboard capture behavior. |
| WebSerial load/save claim | observed_from_external_repo_docs | Public README claims device load/save over WebSerial. This repo does not implement that behavior. |
| custom profile/modifier support claim from public post | observed_from_public_post | User-provided task statement records the public-post claim; no public-post URL was supplied in this branch. |
| full external source audit | not_verified | Root files and public docs/UI labels were inspected only at a high level; no full code audit was performed. |
| official configurator compatibility | not_verified | External README/app claims compatibility, but this repo does not treat that claim as official authority. |

## Boundary statement

- The external repo and app are not source authority for this repository.
- The external repo and app are not firmware authority.
- The external repo and app are not official configurator authority.
- The external repo and app are not imported dependencies.
- No device-write implementation was added in this repo.
- No runtime-loaded config implementation was added in this repo.
- No WebSerial implementation was added in this repo.
- No hardware validation was performed or claimed.
- External observations must not be used to claim Glyph/HayBox firmware behavior.
- External observations must not be used to claim Super Smash Bros. Ultimate gameplay semantics.

## Gap report

Future adapter work needs all of the following before any dependency,
integration, or compatibility assumption:

- need full source audit before adapter assumptions
- need profile JSON compatibility comparison
- need protobuf schema comparison
- need WebSerial packet-framing comparison
- need custom modifier representation comparison
- need import/export package compatibility experiment
- need license review before code reuse
- need user approval before depending on or integrating

## Required fixture fields

The fixture for this report must preserve these top-level fields:

- `schema_name=glyph_external_remapper_adapter_boundary`
- `boundary_version=1`
- `status=external_non_authoritative_gap_report`
- `hardware_status=not_new_hardware_result`
- `external_source_promoted_to_authority=false`
- `device_write_implemented=false`
- `runtime_loaded_config_implemented=false`

## Checker output

`tools/check_glyph_external_remapper_adapter_boundary.py` prints:

- `glyph_external_remapper_adapter_boundary`
- `status=PASS` or `status=FAIL`
- `observations=<N>`
- `external_source_promoted_to_authority=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the docs/fixture boundary preserves the
required non-authority and gap-report constraints. It does not require live
external network access, does not import the external repo, does not implement
runtime-loaded config, does not implement device-write behavior, and is not
hardware validation.
