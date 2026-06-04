# Glyph WebSerial Transport Blocker Packet - 2026-06-03

## Purpose and scope

This document records a docs/tools-only blocker packet for any future
WebSerial, serial/device write, Save to Device, or firmware flashing work.

It is not firmware source, not runtime-loaded config, not WebSerial
implementation, not device write behavior, not firmware flashing, not official
configurator compatibility, and not hardware validation.

The current serial dry-run exists but is not live device access. Existing
repo-local serial tooling is useful for checking gated dry-run boundaries, but
this packet does not approve or add a live device path.

## Current blocker status

The branch conclusion is:

- serial dry-run is not live device access
- WebSerial write not implemented
- device write not implemented
- firmware flashing not implemented
- official packet framing authority missing
- official configurator behavior source missing
- external WebSerial observations non-authoritative
- not hardware validation

External observations non-authoritative. Public external remapper observations
about WebSerial, Load Config, Save to Device, protobuf encode/decode, or
configurator compatibility are comparison inputs only. They are not promoted to
firmware source authority, official configurator behavior authority, packet
framing authority, device-write authority, firmware flashing authority, or
hardware validation.

## Source-backed inputs

Repo-local evidence currently includes only bounded docs/tools inputs:

- `docs/calibration/glyph_serial_active_config_writer_trace_2026-05-27.md`
- `tools/check_glyph_serial_config_writer.py`
- `tools/glyph_serial_config_tool.py`
- `docs/calibration/glyph_storage_transport_source_authority_registry_2026-06-03.md`
- `docs/calibration/glyph_protobuf_config_schema_research_packet_2026-06-03.md`
- `docs/calibration/glyph_external_remapper_adapter_boundary_2026-06-03.md`
- `docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md`
- `docs/calibration/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.md`

Those sources support a blocker record only. They do not establish official
packet framing, official configurator behavior, live WebSerial write behavior,
device write behavior, firmware flashing behavior, or hardware validation.

## Required missing authority

Future work remains blocked until source-backed authority exists for:

- official packet framing
- official configurator behavior source
- official device-write transport source
- official firmware flashing source, if flashing is ever proposed
- legal/source-review approval before relying on external source observations

If any of those authority sources remain unknown, implementation work must stop.

## Required future evidence

Any future implementation proposal must first provide:

- source-backed packet framing
- safe no-device dry-run
- readback strategy
- rollback plan
- hardware test plan
- user approval
- no accidental Save to Device path
- no firmware flashing path

These are prerequisites only. Recording them here does not approve transport,
device writes, runtime-loaded config, or flashing.

## Forbidden current claims

This branch must not claim:

- WebSerial transport is implemented
- WebSerial write is implemented
- serial dry-run is live device access
- device write is implemented
- Save to Device is implemented
- firmware flashing is implemented
- official packet framing authority is available
- official configurator behavior source is available
- external WebSerial observations are authoritative
- hardware validation has been performed

## Approval boundary

Required approval before future work:

- explicit user approval for any WebSerial, serial/device write, Save to Device,
  runtime-loaded config, or firmware flashing implementation path
- source-authority review approval for packet framing and official configurator
  behavior claims
- hardware-test-plan approval before any implementation branch can claim
  hardware results

## Checker ownership

`tools/check_glyph_webserial_transport_blocker_packet.py` validates the blocker
fixture, hard false implementation flags, required missing authority, required
future evidence, non-promoted external source status, and required document
caveat phrases.

Checker output lines:

- `glyph_webserial_transport_blocker_packet`
- `status=PASS` or `status=FAIL`
- `webserial_transport_implemented=false`
- `device_write_implemented=false`
- `hardware_status=not_new_hardware_result`

Passing the checker confirms only that this packet preserves the intended
docs/tools-only blocker boundary. It is not live device access, not WebSerial
implementation, not device write behavior, not firmware flashing, and not
hardware validation.
