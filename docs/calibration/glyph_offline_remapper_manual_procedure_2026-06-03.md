# Glyph Offline Remapper Manual Procedure - 2026-06-03

## Purpose and scope

This document records a procedure only checklist for a future no-device manual
import/export observation in the external remapper app. It is not executed in
this branch.

The procedure status is:

- `procedure_only_not_executed`

This is procedure only, not executed. It does not implement an adapter, does not
transform repo artifacts into an external-remapper-compatible JSON candidate,
does not change repo fixtures to fit the external app, does not implement
runtime-loaded config, and does not authorize device write behavior.

No live device is allowed. Do not click Connect. Do not click Save to Device.
Do not grant WebSerial device access. This procedure is not official
compatibility and not hardware validation.

## External app target

The external app URL to open for the future manual observation is:

- `https://lyseste.com/glyph-remapper/`

This URL is carried forward from the existing repo-documented external remapper
snapshot/boundary notes. It remains a non-authoritative external observation and
does not become firmware source authority or official configurator authority.

## Required operator checklist

If a later branch is explicitly approved to execute the no-device observation,
the operator must perform the following steps:

1. Open external app URL `https://lyseste.com/glyph-remapper/`.
2. Ensure no Glyph/live device is connected before interacting with the page.
3. Record browser/environment details.
4. Record external app URL/version/commit if visible.
5. Do not click Connect.
6. Do not grant WebSerial device access.
7. Do not click Save to Device.
8. Import the primary active profile artifact
   `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`.
9. Record whether import succeeds, fails, or blocks.
10. If import succeeds, export JSON from the app without device access.
11. Save exported JSON outside repo first.
12. Record that the exported artifact hash must be computed later in a separate
    result fixture.
13. Record that exported JSON comparison is deferred to a later result-recording
    branch.
14. Optionally record screenshots/notes.

The later operator must not compare the exported JSON in this procedure branch,
must not update repo fixtures to match the external app, and must not claim
official compatibility or hardware validation.

## Forbidden actions

The future manual procedure explicitly forbids all of the following:

- live device connected
- clicking Connect
- granting WebSerial device access
- clicking Save to Device
- serial/device write
- firmware flashing
- adapter implementation
- artifact transformation/generation
- protobuf binary generation
- runtime-loaded config implementation
- copying external source code
- changing repo fixtures to fit external app
- claiming official compatibility
- claiming hardware validation

## Required observations

A later result-recording branch must record all of the following, without
modifying this procedure to fit the observed result:

- no-device confirmation
- browser/environment
- external app URL/version/commit if visible
- primary active profile artifact path
- import succeeds/fails/blocks
- export JSON path outside repo if import succeeds
- exported artifact hash pending separate result fixture
- screenshots/notes optional
- not official compatibility
- not hardware validation

## Result output expectations

If this procedure is executed later, the result must be recorded in a separate
result doc/fixture pair. The result fixture must compute and record the exported
artifact hash after the exported JSON is saved outside repo first. The result
branch may compare exported JSON, but this procedure branch must not compare or
transform exported JSON.

Any later result must keep external observations separate from source authority.
It must not claim official compatibility, hardware validation, device write
behavior, WebSerial behavior, runtime-loaded config, protobuf binary generation,
or promotion of external observations into firmware/configurator authority.

## Source inputs

This procedure is bounded to already committed docs/tools/fixtures:

- `docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md`
- `docs/calibration/glyph_external_remapper_adapter_boundary_2026-06-03.md`
- `docs/calibration/glyph_offline_remapper_manual_experiment_packet_2026-06-03.md`
- `docs/calibration/glyph_offline_remapper_experiment_input_manifest_2026-06-03.md`
- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`

## Required fixture fields

The fixture for this procedure must preserve these top-level fields:

- `schema_name=glyph_offline_remapper_manual_procedure`
- `procedure_version=1`
- `status=procedure_only_not_executed`
- `hardware_status=not_new_hardware_result`
- `experiment_executed=false`
- `device_write_allowed=false`
- `webserial_access_allowed=false`
- `save_to_device_allowed=false`
- `adapter_implemented=false`

## Checker output

`tools/check_glyph_offline_remapper_manual_procedure.py` prints:

- `glyph_offline_remapper_manual_procedure`
- `status=PASS` or `status=FAIL`
- `steps=<N>`
- `experiment_executed=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that this remains procedure only, not
executed, no live device, do not click Connect, do not click Save to Device, do
not grant WebSerial, not official compatibility, and not hardware validation.
