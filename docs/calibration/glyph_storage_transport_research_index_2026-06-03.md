# Glyph Storage Transport Research Index - 2026-06-03

## Purpose and scope

This document records a docs/tools research index that consolidates the current
Glyph storage/transport source-authority registry, protobuf/config schema
research packet, WebSerial transport blocker packet, and runtime
storage/interpreter blocker packet into one aggregate status view.

It is docs/tools research index only. It is not protobuf binary generation, not
device write behavior, not WebSerial implementation, not runtime-loaded
config, not official configurator compatibility claims, and not hardware
validation.

- not runtime-loaded config
- not hardware validation

External observations non-authoritative. They remain comparison inputs only and
are not promoted to firmware source authority, official configurator
compatibility authority, protobuf/schema authority, WebSerial transport
authority, device-write authority, runtime-loaded config authority, or hardware
validation.

## Consolidated status

The aggregate index conclusion is:

- source registry status: complete as a docs/tools-only source-authority
  registry with implementation still blocked
- protobuf/config schema research status: complete as a docs/tools-only
  research packet with official protobuf/schema authority still missing
- WebSerial/transport blocker status: complete as a docs/tools-only blocker
  packet with official packet framing and configurator behavior authority still
  missing
- runtime storage/interpreter blocker status: complete as a docs/tools-only
  blocker packet with design, source-authority, approval, and validation gates
  still unresolved
- all implementation classes blocked

## Required component packets

This index depends on these committed component packets and their checkers:

- source-authority registry
  - `docs/calibration/glyph_storage_transport_source_authority_registry_2026-06-03.md`
  - `docs/calibration/fixtures/glyph_storage_transport_source_authority_registry_2026-06-03.json`
  - `tools/check_glyph_storage_transport_source_authority_registry.py`
- protobuf/config schema research packet
  - `docs/calibration/glyph_protobuf_config_schema_research_packet_2026-06-03.md`
  - `docs/calibration/fixtures/glyph_protobuf_config_schema_research_packet_2026-06-03.json`
  - `tools/check_glyph_protobuf_config_schema_research_packet.py`
- WebSerial transport blocker packet
  - `docs/calibration/glyph_webserial_transport_blocker_packet_2026-06-03.md`
  - `docs/calibration/fixtures/glyph_webserial_transport_blocker_packet_2026-06-03.json`
  - `tools/check_glyph_webserial_transport_blocker_packet.py`
- runtime storage/interpreter blocker packet
  - `docs/calibration/glyph_runtime_storage_interpreter_blocker_packet_2026-06-03.md`
  - `docs/calibration/fixtures/glyph_runtime_storage_interpreter_blocker_packet_2026-06-03.json`
  - `tools/check_glyph_runtime_storage_interpreter_blocker_packet.py`

## Blocked implementation classes

All implementation classes remain blocked in this branch:

- protobuf binary generation
- WebSerial transport
- device write
- runtime-loaded storage
- runtime-loaded interpreter
- official configurator compatibility claims

These classes stay blocked until source-backed authority, explicit user
approval, and any required validation plans/results exist.

## Allowed next work

Allowed next work stays limited to:

- docs/tools validators
- offline JSON adapter planning
- manual no-device import/export experiment planning
- source audits

Those items are planning and validation only. They are not implementation work.

## Disallowed without approval

Disallowed without approval:

- firmware source changes
- device write
- WebSerial
- runtime-loaded config
- profile artifact changes
- hardware validation claims

This index does not authorize storage implementation, interpreter
implementation, live transport work, Save to Device behavior, firmware
flashing, profile artifact mutation, or hardware validation claims. It is not
runtime-loaded config.

## Checker ownership

`tools/check_glyph_storage_transport_research_index.py` validates the aggregate
fixture, required component packet references, required blocked implementation
classes, allowed/disallowed work lists, hard false implementation flags, and
required document caveat phrases. It also runs the component packet checkers.

Checker output lines:

- `glyph_storage_transport_research_index`
- `status=PASS` or `status=FAIL`
- `component_packets=<N>`
- `all_implementation_classes_blocked=true`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the aggregate docs/tools research index
and its component packets stay aligned. It is not protobuf binary generation,
not device write behavior, not WebSerial implementation, not runtime-loaded
config, not official configurator compatibility claims, and not hardware
validation.
