# Runtime Config Flashing Automation Safety Boundary

Status label: FORBIDDEN_NOT_APPROVED.

## Purpose

This Step 17 packet sets the safety and source-authority boundary for any future
flashing safety work in the runtime-config roadmap.

firmware flashing automation is forbidden/not approved.

This branch does not implement firmware flashing automation, firmware update
automation, automatic UF2 upload, or hidden device write tooling.

## Inspected Files And Searches

- `scripts/build-glyph-mk6-quiet.sh`
- `platformio.ini`
- `docs/sources/raw/glyph_firmware_uf2/1.0.7/README.md`
- `docs/sources/raw/glyph_firmware_uf2/1.0.7/manifest.json`
- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/WORKFLOW.md`
- `docs/runtime_config/runtime_config_manual_load_path_plan.md`
- `docs/runtime_config/runtime_config_device_write_safety_plan.md`
- `docs/runtime_config/runtime_config_webserial_device_write_source_authority.md`
- `docs/runtime_config/runtime_config_firmware_binary_parser_source_authority.md`
- `docs/runtime_config/runtime_config_firmware_binary_parser_integration_plan.md`
- `docs/project/G12H_UF2_FORMAT_AND_FLASH_RANGE_ANALYSIS.md`
- `docs/project/G12K_SAFE_FIRST_CUSTOM_FLASH_DECISION_GATE.md`
- `HAL/pico/src/display/DefaultConfigMenu.cpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `HAL/pico/include/comms/ConfiguratorBackend.hpp`
- `HAL/pico/src/core/Persistence.cpp`
- `HAL/pico/include/core/Persistence.hpp`
- `config/glyph/common/src/config.cpp`
- `tools/glyph_serial_config_tool.py`
- `tools/inspect_glyph_mk6_build_artifact.py`
- `tools/uf2/inspect_uf2.py`
- `tools/check_glyph_runtime_config_firmware_binary_parser_plan.py`

The following repository search was run while preparing this packet:

```text
rg -n "firmware|bootloader|UF2|RPI-RP2|reboot_bootloader|CMD_REBOOT_BOOTLOADER|CMD_REBOOT_FIRMWARE|config.bin|LittleFS|upload|openocd|picotool|build|pio|scripts" scripts config HAL tools docs platformio.ini
```

## Source-Backed Safety Facts

- `scripts/build-glyph-mk6-quiet.sh` runs `./scripts/pio-local.sh run -e glyph_mk6`, so build scripts may compile firmware if present.
- `platformio.ini` defines build environments, including Pico build settings and
  dependencies, but does not provide source-backed firmware upload automation.
- `docs/sources/raw/glyph_firmware_uf2/1.0.7/README.md` stores user-provided official UF2 files as
  read-only references for analysis and recovery planning.
- `docs/sources/raw/glyph_firmware_uf2/1.0.7/README.md` preserves manual firmware update guidance as user-provided source text; this branch adds no automation.
- `docs/sources/raw/glyph_firmware_uf2/1.0.7/manifest.json` records official UF2 file metadata and notes that this repo does not authorize flashing or copy-to-device behavior from these artifacts.
- Manual firmware update guidance exists in the above source text with the RPI-RP2 drag-and-drop flow and explicit
  user confirmation.
- `docs/project/G12H_UF2_FORMAT_AND_FLASH_RANGE_ANALYSIS.md` records a read-only UF2 comparison, identifies the clean-only high-flash wipe segment as a strong inference, and warns against treating filename alone as a flash decision.
- `docs/project/G12K_SAFE_FIRST_CUSTOM_FLASH_DECISION_GATE.md` records a read-only decision gate and says an agent must not flash hardware, copy firmware to `RPI-RP2`, copy to any mounted device, or run PlatformIO upload commands without future approval.
- `HAL/pico/src/core/Persistence.cpp` and `HAL/pico/include/core/Persistence.hpp` persist only current protobuf `Config` in
  `config.bin`; no firmware blob persistence path is source-backed.
- `HAL/pico/src/display/DefaultConfigMenu.cpp` and `config/glyph/common/src/config.cpp`
  contain explicit user-driven bootloader entry paths; no automatic bootloader invocation path is source-backed.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp` has `CMD_REBOOT_BOOTLOADER` and `CMD_REBOOT_FIRMWARE`, but no source-backed firmware artifact upload command.
- `tools/glyph_serial_config_tool.py` is a guarded serial tool with current-config read/write support and a dry-run default; it explicitly never flashes firmware.
- `tools/inspect_glyph_mk6_build_artifact.py` and `tools/uf2/inspect_uf2.py` are
  read-only artifact-inspection utilities and do not write firmware.

## Forbidden Automation Classes

- UF2 copy automation.
- bootloader/RPI-RP2 automation.
- PlatformIO upload automation.
- picotool/openocd automation.
- WebSerial/device write automation.
- hidden device mutation.
- automatic recovery writes.
- Unattended or looped flashing automation without explicit operator control.
- Any tooling path that auto-selects artifact, target, or transport and proceeds without manual confirmation.

## Allowed Manual Guidance

The current Step 17 boundary allows manual/operator-run flashing instructions only:

- manual/operator-run flashing instructions may be referenced only as manual recovery/update guidance;
- manual paths must be visibly operator-run and do not turn manual instructions into automated tooling;
- operator confirms target, artifact, and intent before any host-initiated flash attempt;
- operator performs bootloader/RPI-RP2 hand-off manually;
- no automatic fallback or background recovery write path is allowed;
- this branch adds no automation for firmware update workflows.

## Required Future Gates Before Reconsideration

Step 17 remains `FORBIDDEN_NOT_APPROVED` until all of these are satisfied by
future branch scope:

- explicit product approval;
- source/legal/safety review;
- exact hardware target;
- recovery/rollback plan;
- hardware test matrix;
- user confirmation/consent model;
- no hidden write policy;
- source-backed packet transport and payload authority package.

## Non-Claims

- no flashing automation is implemented or approved by this branch
- no uf2 copy automation is implemented or approved by this branch
- no bootloader automation is implemented or approved by this branch
- no rpi-rp2 mass-storage automation is implemented or approved by this branch
- no WebSerial/device write is implemented or claimed
- no runtime-loaded config is implemented or claimed
- no hardware validation is claimed
- no nunchuk validation is claimed

## Stop Conditions Hit

- no source-backed host automation transport exists for firmware artifact upload;
- no explicit recovery/rollback plan and no hidden write policy package exists for automated flashing;
- no explicit hardware test matrix for automated flashing paths;
- no product-approved, source/legal/safety review for this branch scope;
- no user confirmation/consent model added for pre/post flash steps.
