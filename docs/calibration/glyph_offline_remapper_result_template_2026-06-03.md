# Glyph Offline Remapper Result Template - 2026-06-03

## Purpose and scope

This document records the result template only for any later no-device offline
remapper import/export observation packet. It does not execute the experiment.

The template status is:

- `template_not_executed`

This is a result template only. It is not executed. No device connected. No
WebSerial access. No Save to Device. No device write attempted. This is not
official compatibility and not hardware validation.

## Required top-level fields

Any template or later result fixture using this shape must preserve these
fields:

- `schema_name=glyph_offline_remapper_result_template`
- `template_version=1`
- `status=template_not_executed`
- `hardware_status=not_new_hardware_result`
- `experiment_executed=false`
- `device_connected=false`
- `webserial_access_granted=false`
- `save_to_device_clicked=false`
- `device_write_attempted=false`
- `firmware_flashing_attempted=false`
- `adapter_implemented=false`
- `official_compatibility_claimed=false`
- `hardware_validation_claimed=false`
- `external_source_promoted_to_authority=false`

These bounds keep the template strictly no-device and no-write. They do not
authorize adapter implementation, external-remapper-compatible JSON
generation, runtime-loaded config, device transport, or source-authority
promotion.

## Required result fields

The fixture must keep the following result-recording categories:

- browser/environment
- external app URL/version/commit if available
- input artifact hash
- import attempt result
- export attempt result
- JSON diff result
- accepted/rejected field list
- no-device confirmation
- no WebSerial access confirmation
- no Save to Device confirmation
- no source-authority promotion confirmation
- no official/hardware compatibility claims confirmation

## Result rows template

The template must contain these ordered result row IDs:

| Row ID | Required prompt |
| --- | --- |
| `ENV-001` | browser/environment recorded |
| `SRC-001` | external app URL/version/commit recorded if available |
| `INPUT-001` | active profile artifact hash confirmed |
| `IMPORT-001` | active profile import attempt |
| `EXPORT-001` | export attempt if import succeeds |
| `DIFF-001` | JSON diff result |
| `FIELDS-001` | accepted/rejected field list |
| `DEVICE-001` | no live device confirmation |
| `WS-001` | no WebSerial access confirmation |
| `SAVE-001` | no Save to Device confirmation |
| `AUTH-001` | no source authority promotion |
| `CLAIM-001` | no official/hardware compatibility claims |

The row template exists only so any future manual result stays structured and
bounded. The row template does not mark the experiment executed.

## Required caveats

Any later filled result must preserve all of the following caveats:

- result template only
- not executed
- no device connected
- no WebSerial access
- no Save to Device
- no device write attempted
- not official compatibility
- not hardware validation

These caveats must stay explicit even if a future operator records screenshots,
import notes, export notes, or diff notes.

## Source inputs

This result template is bounded to already committed docs/tools/fixtures:

- `docs/calibration/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_manual_experiment_packet_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_manual_experiment_packet_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_experiment_input_manifest_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_experiment_input_manifest_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_manual_procedure_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_manual_procedure_2026-06-03.json`

## Checker output

`tools/check_glyph_offline_remapper_result_template.py` prints:

- `glyph_offline_remapper_result_template`
- `status=PASS` or `status=FAIL`
- `template_status=template_not_executed`
- `experiment_executed=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the result template remains result
template only, not executed, no device connected, no WebSerial access, no Save
to Device, no device write attempted, not official compatibility, and not
hardware validation.
