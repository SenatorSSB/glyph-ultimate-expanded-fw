# Glyph Senscope-to-Glyph Export Contract Draft - 2026-05-28

## Purpose and scope

This document defines a source-grounded draft for how Senscope could eventually
export a Glyph-compatible artifact targeting the current generated-config
contract.

This is a draft, not an implementation. It does not depend on the official Limit
Labs configurator being open-source. It does not implement serial writing,
device writing, or runtime-loaded config.

## Draft status

`contract_version=1` records a docs/tools-only export planning target. The draft
exists to keep the Senscope app boundary and Glyph firmware repo boundary clear
before any implementation work.

The draft is not a firmware patch, not a browser-app patch, and not hardware
validation.

## Source authority

Primary source authority is limited to current repository sources:

- `src/modes/Ultimate.cpp`
- `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_generated_config_prototype_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json`
- existing generated-config, table, and behavior checkers in `tools/`

No external source is used for this draft.

## Boundary between Senscope app and Glyph firmware repo

Senscope app owns:

- app-owned neutral profile data
- raw-coordinate modifier profile semantics
- SSBU mapping datasets
- user-facing optimization/report UX
- export package generation

Glyph firmware repo owns:

- primitive evaluator
- priority model
- supported role classes
- source-backed firmware behavior
- checkers that validate generated artifacts against firmware source assumptions

The Glyph repo may validate a generated artifact against current
controller/backend assumptions. It must not become the source authority for
Senscope neutral profile semantics or SSBU game semantics.

## Export package concept

A future Senscope export should be a package containing:

- neutral Senscope-owned profile model
- Glyph generated-config prototype JSON
- table source/citation metadata
- role-binding metadata
- validation report
- optional generated C++ review text
- explicit hardware-status caveat
- explicit nunchuk-status caveat

The package target is the generated-config contract fixture, not firmware source
and not a device write path.

## Required export payloads

The draft fixture requires these payload names:

- `neutral_senscope_profile`
- `glyph_generated_config_prototype`
- `table_source_metadata`
- `role_binding_metadata`
- `validation_report`
- `hardware_status_caveat`
- `nunchuk_status_caveat`

## Validation report requirements

A future validation report should include:

- `source_authority`
- `table_count`
- `role_binding_summary`
- `priority_model_summary`
- `hard_override_summary`
- `behavior_case_coverage_summary`
- `no_forbidden_behavior_confirmation`
- `not_hardware_validation_caveat`
- `open_questions`

The report is a review artifact. It is not hardware validation and does not
claim the exported artifact has been written to a device.

## Table and coordinate semantics

Raw controller coordinates remain raw `[0,255]`. Origin/domain details should
remain app-owned if exported from Senscope.

Glyph-side generated config for the current runtime uses source-backed raw table
outputs from `src/modes/Ultimate.cpp`.

Do not collapse raw controller coordinates with SSBU effective output semantics.
Generated config is not a claim about game semantics.

## Role-binding semantics

Role-binding metadata may describe controller/backend role classes currently
modeled by the Glyph identity runtime:

- button carriers
- direction contributors
- C-stick bindings
- modifiers
- special functions
- layer/sub-mode metadata

This draft does not redesign the Senscope profile schema and does not redesign
the Glyph role-map fixture schema.

## Device/backend boundaries

This draft does not implement device writing.
This draft does not implement serial transport.
This draft does not implement runtime-loaded config.
This draft does not implement firmware behavior changes.
This draft does not implement profile schema changes.

Any future device/backend transport must be separately designed, source-backed,
reviewed, and validated.

## Explicit non-goals

This draft does not implement:

- device writing
- serial transport
- runtime-loaded config
- generated firmware inclusion
- firmware behavior changes
- profile schema changes
- macros/turbo/timing/history-dependent behavior
- hardware validation

It also does not alter game-semantic source authority and does not touch the
Senscope browser app code.

## Checker ownership

`tools/check_glyph_identity_runtime_config_contracts.py` owns the aggregate
fixture and caveat checks for this draft.

The checker validates required export payload names, validation-report section
names, forbidden scope names, target generated-config contract path, and required
doc caveat phrases.

## Migration path

1. Current generated-config prototype remains docs/tools-only.
2. Generated-config contract fixture makes the target review shape explicit.
3. Senscope export draft defines a possible package boundary.
4. Senscope app may later define its app-owned export schema.
5. Glyph repo may later add source-backed validators for generated artifacts.
6. Runtime-loaded config and device writing require separate approval and are
   not implemented by this draft.

## Open questions / deferred decisions

- Exact Senscope export schema is deferred to Senscope.
- Actual app-owned neutral profile fields are not defined in this Glyph repo.
- Device write/serial transport is not defined here.
- Runtime-loaded config is not defined here.
- Hardware and nunchuk validation remain out of scope for this draft.
