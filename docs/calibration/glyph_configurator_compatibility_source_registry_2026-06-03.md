# Glyph Configurator Compatibility Source Registry - 2026-06-03

## Purpose and scope

This document records a docs/tools-only source registry for configurator
compatibility work around the current Glyph export-adjacent artifacts.

It is not firmware source, not runtime-loaded config, not serial/device write
behavior, not hardware validation, and not nunchuk hardware validation.

This registry separates current repo-committed authority from repo-committed
compatibility fixtures, external observations, and deferred source authority.
External observations are non-authoritative. They are not promoted to firmware
source authority, generated-config authority, runtime-loaded config authority,
serial/device write behavior, WebSerial packet framing authority, or hardware
validation.

## Source classes

### repo_committed_source_authority

This class lists current repo-committed sources and validators that can be used
as authority for docs/tools compatibility checks:

- current firmware source references, including
  `src/modes/UltimateIdentityRuntimeTables.hpp`
- current generated-config contracts
- current runtime candidate fixtures and validator/checker sources
- current export package fixtures and validator/checker sources
- current export artifact compatibility, round-trip, canonical snapshot, invalid
  corpus, and agentic-sequence checkers

### repo_committed_compatibility_fixtures

This class lists repo-committed compatibility fixtures used as examples or
snapshots only:

- active profile artifact
- generated config prototype
- runtime config candidate sample
- Senscope export package sample
- canonical export artifact snapshots

These fixtures do not implement runtime-loaded config, serial/device write
behavior, firmware source, or hardware validation.

### external_observed_non_authoritative

This class records external observations supplied for compatibility awareness
only:

- public repository: `https://github.com/lyseste/glyph-remapper`
- public app: `https://lyseste.com/glyph-remapper/`
- observed scope: browser-based Glyph configurator, JSON import/export,
  WebSerial load/save, protobuf encode/decode, RGB/profile/SOCD/profile
  management UI, and a custom profile/modifier claim from a public post

These external observations are non-authoritative. They are not promoted to
firmware/source authority and do not authorize repo claims about official Glyph
firmware behavior, official configurator behavior, official protobuf/schema
source, official WebSerial packet framing, device-write transport, runtime-loaded
config storage, or hardware validation.

### deferred_source_authority

This class records sources that remain deferred until official source authority
is inspected or explicitly provided:

- official Limit Labs configurator behavior
- official protobuf/schema source
- official WebSerial packet framing
- device-write transport
- runtime-loaded config storage

The deferred list is not an implementation plan. It marks the boundary where the
repo must stop before claiming or implementing configurator/device behavior.

## Required fixture fields

The fixture for this registry must preserve these top-level fields:

- `schema_name=glyph_configurator_compatibility_source_registry`
- `registry_version=1`
- `status=docs_tools_source_registry`
- `hardware_status=not_new_hardware_result`
- `external_sources_promoted_to_authority=false`
- `device_write_implemented=false`
- `runtime_loaded_config_implemented=false`

## Caveats

- external observations are non-authoritative
- not firmware source
- not runtime-loaded config
- not serial/device write behavior
- not hardware validation
- not nunchuk hardware validation

## Checker output

`tools/check_glyph_configurator_compatibility_source_registry.py` prints:

- `glyph_configurator_compatibility_source_registry`
- `status=PASS` or `status=FAIL`
- `source_classes=<N>`
- `external_sources_promoted_to_authority=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the docs/fixture registry preserves the
required source-class boundaries. It does not implement runtime-loaded config,
serial/device write behavior, WebSerial packet framing, generated firmware
source, hardware validation, or nunchuk hardware validation.
