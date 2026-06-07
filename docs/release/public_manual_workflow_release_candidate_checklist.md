# Public / Manual Workflow Release Candidate Checklist

Status: PLAN_ONLY_NOT_RELEASED

This checklist is for the manual/public workflow release-candidate preparation only. It is not a release approval, not a hardware result, and not a public compatibility claim.

## Repository Baseline

- [ ] Working branch is `runtime-config-public-workflow-release-candidate-plan`.
- [ ] `README.md`, `docs/CURRENT_STATE.md`, `docs/ROADMAP.md`, and `docs/WORKFLOW.md` were reviewed before changing status language.
- [ ] `docs/calibration/INDEX.md` was updated for navigation.
- [ ] No firmware source, build-script, or device-write implementation files were changed.

## Required Prior Evidence Packets

- [ ] Step 9 interpreter baseline hardware plan/result exist.
- [ ] Step 10 storage/fallback source-authority packet and checker exist.
- [ ] Step 11 binary representation design exists.
- [ ] Step 12 offline binary roundtrip tooling and checker exist.
- [ ] Step 13 firmware binary/parser integration plan and checker exist.
- [ ] Step 14 manual load path plan and checker exist.
- [ ] Step 15 WebSerial/device-write source-authority packet and checker exist.
- [ ] Step 16 device-write safety plan and checker exist.
- [ ] Step 17 flashing automation safety boundary and checker exist.

## Required Checkers

- [ ] `python3 tools/check_glyph_docs_navigation.py`
- [ ] `python3 tools/check_glyph_runtime_config_binary_offline_roundtrip.py`
- [ ] `python3 tools/check_glyph_runtime_config_storage_fallback.py`
- [ ] `python3 tools/check_glyph_runtime_config_firmware_binary_parser_plan.py`
- [ ] `python3 tools/check_glyph_runtime_config_webserial_device_write_source_authority.py`
- [ ] `python3 tools/check_glyph_runtime_config_manual_load_path_plan.py`
- [ ] `python3 tools/check_glyph_runtime_config_device_write_safety_plan.py`
- [ ] `python3 tools/check_glyph_runtime_config_flashing_automation_safety_boundary.py`
- [ ] `python3 tools/check_glyph_public_manual_workflow_release_candidate.py`

## Required Non-Claims

- [ ] No runtime-loaded config claim is made.
- [ ] No runtime-config storage claim is made.
- [ ] No firmware binary/protobuf parser integration claim is made.
- [ ] No WebSerial/device write claim is made.
- [ ] No push-to-device claim is made.
- [ ] No firmware flashing automation claim is made.
- [ ] No official configurator compatibility claim is made.
- [ ] No nunchuk validation claim is made unless separately tested and recorded.
- [ ] No public release claim is made.

## Manual Workflow Docs

- [ ] `docs/release/public_manual_workflow_release_candidate_plan.md` exists and states `PLAN_ONLY_NOT_RELEASED`.
- [ ] `docs/release/public_manual_workflow_release_candidate_checklist.md` exists and stays plan-only.
- [ ] Manual/operator-run firmware update and recovery boundaries are documented as manual only.
- [ ] No hidden writes are described or implied.
- [ ] No automated flashing, UF2 copy, or bootloader automation is described or implied.

## Pre-Hardware Local Verification

- [ ] Docs navigation checker passes.
- [ ] Offline binary roundtrip checker passes.
- [ ] Storage fallback checker passes.
- [ ] Firmware binary/parser plan checker passes.
- [ ] WebSerial/device-write source-authority checker passes.
- [ ] Manual load path checker passes.
- [ ] Device-write safety checker passes.
- [ ] Flashing automation safety boundary checker passes.
- [ ] Public/manual workflow release-candidate checker passes.

## Hardware Plan

- [ ] `docs/calibration/glyph_public_manual_workflow_release_candidate_hardware_plan_2026-06-07.md` exists.
- [ ] `docs/calibration/fixtures/glyph_public_manual_workflow_release_candidate_hardware_plan_2026-06-07.json` exists.
- [ ] All hardware-plan rows start as `NOT_TESTED`.
- [ ] `NUNCHUK-001` remains `NOT_TESTED` unless separately validated later.

## Result Recording

- [ ] Any future hardware result is recorded in a separate result branch.
- [ ] The result packet includes scope, artifact identity when available, row outcomes, caveats, and rollback notes.
- [ ] No hardware result is recorded in this branch.
- [ ] No pass or release claim is made before a result packet exists.

## Release Blockers

- [ ] Any changed file outside `README.md`, `docs/CURRENT_STATE.md`, `docs/ROADMAP.md`, `docs/release/`, `docs/calibration/`, `docs/runtime_config/`, or `tools/` is a blocker.
- [ ] Any firmware source or build-script path change is a blocker.
- [ ] Any hardware result file added in this branch is a blocker.
- [ ] Any positive release/pass language in plan or checklist docs is a blocker.
- [ ] Any nunchuk validation claim without a recorded nunchuk result is a blocker.

