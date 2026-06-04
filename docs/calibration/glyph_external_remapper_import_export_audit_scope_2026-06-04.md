# Glyph External Remapper Import/Export Audit Scope - 2026-06-04

## Purpose and scope

This records a docs/tools/fixtures-only source audit scope for a future external
remapper import/export review.

Scope status is `source_audit_scope_only`.

This packet does not audit external source code.

This packet does not promote external source to authority.

This packet does not copy external source code into this repository.

This packet does not add an external dependency.

This packet does not implement an adapter.

This packet does not generate external JSON.

This packet does not add transform code.

This packet does not implement runtime-loaded config.

This packet does not implement serial/device write behavior.

This packet does not implement WebSerial transport.

This packet does not implement protobuf binary generation.

This packet does not claim official configurator compatibility.

This packet does not claim hardware validation.

## Audit targets

The future source audit must inspect these targets if present in the external
remapper source or app surface:

- repository metadata
- license
- README/docs
- file inventory
- JSON import path
- JSON export path
- profile normalization logic
- buttonRemapping handling
- activates handling
- SOCD pair handling
- RGB config handling
- menu icon/default metadata handling
- protobuf encode/decode path
- WebSerial load/save path
- custom profile/modifier representation
- default config payload provenance
- browser storage/localStorage behavior

## Required source-audit outputs

A future audit result must separate:

- source-backed observations
- inferred observations
- unknown or absent behavior
- license and provenance notes
- implementation blockers
- compatibility claims that remain disallowed

Any observed external behavior remains non-authoritative for Glyph firmware until
reviewed and explicitly promoted by the project.

## Forbidden interpretations

- external source authority
- official configurator compatibility claim
- hardware validation claimed
- external source code copied into repo
- external dependency added
- adapter implemented
- external JSON generated
- transform code added
- runtime-loaded config implemented
- serial/device write behavior implemented
- WebSerial transport implemented
- protobuf binary generation implemented
- firmware runtime behavior changed
- active profile artifact changed
- exported experiment artifact changed

## Checker output

`tools/check_glyph_external_remapper_import_export_audit_scope.py` prints:

- `glyph_external_remapper_import_export_audit_scope`
- `status=PASS` or `status=FAIL`
- `audit_targets=<N>`
- `external_source_promoted_to_authority=false`
- `hardware_status=not_new_hardware_result`
