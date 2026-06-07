# Public / Manual Workflow Release Candidate Plan

Status: PLAN_ONLY_NOT_RELEASED
Branch: `runtime-config-public-workflow-release-candidate-plan`

This plan is docs/tools only. It defines the manual/public workflow release-candidate boundary before the next hardware run. It does not declare a release, a pass, or an official compatibility claim.

## Purpose

Define what can be said publicly about the manual workflow release-candidate preparation without turning any blocked runtime-config or write-capable work into a release claim.

## Public / Manual RC Scope

- source-backed firmware baseline;
- generated-like constants path;
- source-owned runtime-config interpreter boundary;
- offline runtime-config/binary-preview tooling;
- manual/operator-run firmware update path;
- public documentation and checklist work;
- no hidden writes.

## Allowed Public Claims

- The current firmware baseline is source-backed for the stated scope.
- Offline runtime-config/binary-preview tooling is docs/tools only and read-only.
- The manual/public workflow release-candidate preparation is plan-only and not released.
- Hardware rows remain NOT_TESTED until a separate result branch records them.

## Explicit Non-Claims

- no runtime-loaded config;
- no runtime-config storage;
- no firmware binary/protobuf parser integration;
- no WebSerial/device write;
- no push-to-device;
- no flashing automation;
- no firmware flashing automation;
- no official configurator compatibility claim;
- no nunchuk validation unless actually tested and recorded later.

## Operator-Run Workflow Boundary

- manual/operator-run firmware update path only;
- no hidden writes;
- no automatic save, sync, upload, or background recovery write;
- no automatic bootloader handoff;
- operator confirmation is required before any manual firmware update or recovery action;
- this branch only documents the boundary and does not mutate devices.

## Offline Tooling Role

- validate docs and fixtures;
- validate source-backed offline preview artifacts;
- keep manual workflow guardrails explicit;
- keep result recording separate from plan writing;
- do not add device mutation behavior.

## Manual Firmware Update / Recovery Boundary

- manual firmware update and recovery remain operator-run only;
- no automatic flashing, UF2 copy, or bootloader automation;
- no runtime-loaded config consumption is implemented here;
- any later hardware result must be recorded in a separate result branch after the test;
- this plan stops before any public release claim.

## Required Pre-Hardware Checks

- `python3 tools/check_glyph_docs_navigation.py`
- `python3 tools/check_glyph_runtime_config_binary_offline_roundtrip.py`
- `python3 tools/check_glyph_runtime_config_storage_fallback.py`
- `python3 tools/check_glyph_runtime_config_firmware_binary_parser_plan.py`
- `python3 tools/check_glyph_runtime_config_webserial_device_write_source_authority.py`
- `python3 tools/check_glyph_runtime_config_manual_load_path_plan.py`
- `python3 tools/check_glyph_runtime_config_device_write_safety_plan.py`
- `python3 tools/check_glyph_runtime_config_flashing_automation_safety_boundary.py`
- `python3 tools/check_glyph_public_manual_workflow_release_candidate.py`

## Hardware Test Trigger

- Hardware testing becomes relevant only after an approved artifact exists for the test scope.
- The hardware run must be recorded in a separate result branch after the test.
- Nunchuk remains NOT_TESTED unless explicitly validated and recorded later.

## Post-Hardware Result Recording Requirement

- Record scope, artifact identity when available, row outcomes, caveats, and rollback notes in a separate result packet.
- Do not turn the plan into a hardware result.
- Do not claim release, validation, or official compatibility until the result packet exists.

## Stop Line Before Public Release Claims

- This plan is not a release.
- This plan does not claim public release.
- This plan does not claim official configurator compatibility.
- This plan does not claim hardware pass status.
- This plan does not claim nunchuk validation.
- This plan does not claim runtime-loaded config implementation.
