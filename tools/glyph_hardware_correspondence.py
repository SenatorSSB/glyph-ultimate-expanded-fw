"""Read-only, fail-closed correspondence for already accepted firmware inputs.

Identity, hardware authorization and normal metadata validators remain callers'
responsibility. See docs/agent_framework/HARDWARE_CORRESPONDENCE.md for the
dependency audit behind the deliberately finite metadata inventory.
"""
from __future__ import annotations

from pathlib import Path
from contextvars import ContextVar
import hashlib
import re
import stat
import subprocess

from glyph_tracked_worktree_integrity import (
    CRITICAL_FILES,
    CRITICAL_ROOTS,
    TrackedWorktreeIntegrityError,
    ignored_critical_worktree_paths,
)


class CorrespondenceError(ValueError):
    """An input is unknown, unsafe, or differs from the tested source snapshot."""


# Executable validation code changed by the candidate is held to critical-path
# correspondence even though it is not a firmware compiler input.
CORRESPONDENCE_CRITICAL_PATHS = frozenset({
    'tools/check_glyph_profile_adapter_prewrite.py',
})


# Exact, reviewed paths only. Membership never overrides a critical input.
NON_BEHAVIORAL_PATHS = frozenset({
    # GP-VAL-035 finite source-free literals; HAL retains critical precedence.
    'tools/glyph_c017_campaign_transition.py',
    'tools/test_glyph_c017_campaign_transition.py',
    'tools/check_glyph_neopixel_historical_replay.py',
    'docs/runtime_config/fixtures/gp_val035_c017_transition.json',
    'docs/runtime_config/fixtures/gp_val035_accepted_transitions.json',
    'docs/calibration/gp_config_017_hardware_result.md',
    'docs/calibration/fixtures/gp_config_017_hardware_evidence.json',
    'docs/agent_framework/PORTFOLIO_20261005_0028_CURATOR.md',
    'docs/agent_framework/GP_CONFIG_017_HARDWARE_PROTOCOL.md',
    'docs/runtime_config/fixtures/gp_config_017_neopixel_repaired_current.json',
    'docs/runtime_config/gp_config_017_neopixel_repaired_current.md',
    'tools/check_glyph_gp_config_017_neopixel_repaired_current.py',
    'tools/fixtures/gp_config017_neopixel_repaired_current/include/FastLED.h',
    'tools/fixtures/gp_config017_neopixel_repaired_current/neo_harness.cpp',
    # GP-VAL-041: finite original019 hosts, separate current proof and read-only authority.
    'docs/calibration/fixtures/gp_config_019_usb_name_selection_characterization.json',
    'docs/calibration/gp_config_019_usb_name_selection_characterization.md',
    'tools/check_glyph_gp_config019_usb_name_selection.py',
    'tools/fixtures/gp_config019_usb_name_selection/include/host_stubs.hpp',
    'tools/fixtures/gp_config019_usb_name_selection/main.cpp',
    'tools/fixtures/gp_config019_usb_name_selection/current_acceptance.cpp',
    'docs/runtime_config/fixtures/gp_val041_usb_name_current_acceptance.json',
    'docs/runtime_config/gp_val041_usb_name_current_acceptance.md',
    'docs/agent_framework/GP_VAL_041_FINITE_SCOPE_CURATOR_20261004.md',
    'docs/agent_framework/curation_receipts/gp_val041_finite_scope_20261004.json',

    # GP-VAL-034: exact host/governance literals; firmware remains critical.
    'tools/glyph_c014_campaign_transition.py',
    'tools/test_glyph_c014_campaign_transition.py',
    'docs/runtime_config/fixtures/gp_val034_c014_transition.json',
    'docs/runtime_config/fixtures/gp_val034_accepted_transitions.json',
    'tools/check_glyph_custom_modifier_cache_characterization.py',
    'tools/check_glyph_gp_config014_modifier_capacity.py',
    'tools/fixtures/gp_config014_modifier_capacity/modifier_capacity_harness.cpp',
    'docs/runtime_config/fixtures/gp_config014_modifier_capacity.json',
    'docs/runtime_config/gp_config014_modifier_capacity.md',
    'docs/agent_framework/GP_CONFIG_014_HARDWARE_PROTOCOL.md',
    'docs/calibration/gp_config_014_hardware_result.md',
    'docs/calibration/fixtures/gp_config_014_hardware_evidence.json',
    # Exact preserved KBD host overlay named by the adopted034 contract.
    'docs/calibration/fixtures/gp_kbd_001_keyboard_pipeline_characterization.json',
    'docs/calibration/gp_kbd_001_keyboard_pipeline_characterization.md',
    'tools/check_glyph_gp_kbd_001_keyboard_pipeline.py',
    'tools/fixtures/gp_kbd_001_keyboard_pipeline/include/TUKeyboard.hpp',
    'tools/fixtures/gp_kbd_001_keyboard_pipeline/main.cpp',
    # Owner-directed bounded Revision-3 control-plane contracts, not a prefix.
    'AGENTS.md',
    'docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md',
    'docs/agent_framework/SUPERVISOR_CONTRACT.md',
    'docs/agent_framework/SCHEDULED_TASKS.md',
    'docs/agent_framework/CYCLE_STATE_MACHINE.md',
    'docs/agent_framework/PROMPT_TEMPLATES.md',
    'docs/agent_framework/JUDGE_WATCHDOG_CONTRACT.md',
    'docs/agent_framework/RUNNER_BOUNDARY.md',
    'docs/agent_framework/WORK_ORDER_TEMPLATE.md',
    'tools/glyph_checker_context.py',
    'tools/check_glyph_config_menu_invalid_state_characterization.py',
    'tools/check_glyph_getconfig_raw_load_characterization.py',
    'tools/check_glyph_setconfig_runtime_rebinding_characterization.py',

    # GP-VAL-043: six exact source-free proof/governance paths.
    'tools/glyph_c020_abi_repair_transition.py',
    'docs/runtime_config/fixtures/gp_val043_c020_abi_repair.json',
    'docs/runtime_config/fixtures/gp_val043_accepted_transitions.json',
    'tools/fixtures/gp_config020_button_validation/abi_probe.cpp',
    'docs/runtime_config/gp_config020_abi_repair.md',
    'docs/runtime_config/fixtures/gp_config020_abi_repair.json',

    # GP-VAL-037: literal reviewed host roles; critical classification remains first.
    'tools/glyph_campaign_transition.py',
    'docs/runtime_config/fixtures/gp_val037_accepted_transitions.json',
    'tools/check_glyph_gp_config020_button_validation.py',
    'tools/fixtures/gp_config020_button_validation/decoder_harness.cpp',
    'tools/fixtures/gp_config020_button_validation/include/Adafruit_TinyUSB.h',
    'tools/fixtures/gp_config020_button_validation/setconfig_harness.cpp',
    'tools/fixtures/gp_config020_button_validation/validation_harness.cpp',
    'docs/agent_framework/GP_CONFIG_020_HARDWARE_PROTOCOL.md',
    'docs/calibration/gp_config_020_hardware_result.md',
    'docs/calibration/fixtures/gp_config_020_hardware_evidence.json',
    'docs/agent_framework/curation_receipts/gp_val040_finite_scope_20261003.json',
    'docs/agent_framework/curation_receipts/gp_val037_predecessor_20261003.json',
    'docs/agent_framework/curation_receipts/gp_val037_guard_applicability_20261003.json',
    'docs/agent_framework/curation_receipts/gp_val037_current_arguments_20261003.json',
    'tools/check_glyph_runtime_config_webserial_device_write_source_authority.py',
    'tools/check_glyph_checker_context.py',
    'tools/check_glyph_generated_source_owned_generator_contract.py',
    'tools/check_glyph_generated_source_owned_artifact_install.py',
    'tools/check_glyph_coordinate_native_runtime_profile_contract.py',
    'tools/check_glyph_generated_source_owned_baseline_artifact.py',

    'docs/AGENT_CONTEXT.md',
    'docs/CURRENT_STATE.md',
    'docs/ROADMAP.md',
    'docs/WORKFLOW.md',
    'docs/agent_framework/GP_CONFIG_005_HARDWARE_OPERATOR.md',
    'docs/agent_framework/GP_CONFIG_005_HARDWARE_PROTOCOL.md',
    'docs/agent_framework/GP_CONFIG_005_INTEGRATION_RESULT_20260919.md',
    'docs/agent_framework/GP_CONFIG_010_INTEGRATION_HARDWARE_PROTOCOL.md',
    'docs/agent_framework/GP_CONFIG_010_INTEGRATION_HARDWARE_RESULT_20260923.md',
    'docs/agent_framework/GP_X1_002_HARDWARE_PROTOCOL.md',
    'docs/agent_framework/HARDWARE_CORRESPONDENCE.md',
    'docs/agent_framework/HARDWARE_EVIDENCE.md',
    'docs/agent_framework/README.md',
    'docs/agent_framework/SUBAGENT_CONTRACTS.md',
    'docs/agent_framework/USER_DIRECTION.md',
    'docs/agent_framework/VALIDATION_AND_GATES.md',
    'docs/calibration/INDEX.md',
    'docs/calibration/fixtures/gp_x1_002_hardware_evidence_2026-09-21.json',
    'docs/calibration/fixtures/gp_config_005_hardware_evidence_2026-09-17.json',
    'docs/calibration/fixtures/gp_config_010_integration_hardware_evidence_2026-09-23.json',
    'docs/calibration/gp_config_005_hardware_result_2026-09-17.md',
    'docs/calibration/gp_config_005_prior_inconclusive_persistence_event_2026-09-17.md',
    'docs/project/ACTIVE_AGENT_QUEUE.md',
    'docs/project/DEFERRED_CONFIG_WORK_2026-09-21.md',
    'docs/runtime_config/README.md',
    'docs/runtime_config/current_config_persistence_recovery_research.md',
    'docs/runtime_config/fixtures/configurator_setconfig_transaction.json',
    'docs/runtime_config/fixtures/config_menu_invalid_state_characterization.json',
    'docs/runtime_config/fixtures/current_baseline_extracted_config_preview.json',
    'docs/runtime_config/fixtures/current_baseline_runtime_config_semantics_bridge.json',
    'docs/runtime_config/fixtures/current_config_persistence_recovery_research.json',
    'docs/runtime_config/fixtures/glyph_checker_census.json',
    'docs/runtime_config/fixtures/gp_config_010_integration_semantic_correspondence.json',
    'docs/runtime_config/fixtures/gp_config_010_mode_activation_capacity.json',
    'docs/runtime_config/fixtures/gp_config012_button_mask_characterization.json',
    'docs/runtime_config/fixtures/gp_config013_usb_default_characterization.json',
    'docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json',
    'docs/runtime_config/fixtures/neopixel_null_sendreport_characterization.json',
    'docs/runtime_config/fixtures/runtime_config_validation_health.json',
    'docs/runtime_config/fixtures/runtime_config_validation_manifest.json',
    'docs/runtime_config/fixtures/setconfig_runtime_rebinding_characterization.json',
    'docs/runtime_config/gp_config_010_mode_activation_capacity.md',
    'docs/runtime_config/gp_config_012_button_mask_characterization.md',
    'docs/runtime_config/gp_config013_usb_default_characterization.md',
    'docs/runtime_config/gp_prov_014_decoder_closure.md',
    'docs/runtime_config/neopixel_null_sendreport_characterization.md',
    'docs/runtime_config/intakes/x1_normal_restoration_overlay_hardware_candidate.intake.json',
    'docs/runtime_config/runtime_config_validation_health.md',
    'docs/runtime_config/source_authority_intake_workflow.md',
    'tools/check_glyph_agent_framework_docs.py',
    'tools/check_glyph_configurator_setconfig_transaction.py',
    'tools/check_glyph_config_010_integration_semantic_correspondence.py',
    'tools/check_glyph_config_010_mode_activation_capacity.py',
    'tools/check_glyph_gp_config012_button_mask_characterization.py',
    'tools/check_glyph_gp_config013_usb_default_characterization.py',
    'tools/check_glyph_neopixel_null_sendreport_characterization.py',
    'tools/check_glyph_prebuild_git_identity.py',
    'tools/check_glyph_runtime_config_validation_aggregate.py',
    'tools/run_glyph_runtime_config_validation.py',
    'tools/check_glyph_current_config_persistence_recovery_research.py',
    'tools/check_glyph_docs_agent_surface.py',
    'tools/check_glyph_docs_navigation.py',
    'tools/check_glyph_profile_config_semantics.py',
    'tools/check_glyph_gp_x1_002_candidate.py',
    'tools/check_glyph_gp_prov_014_decoder_closure.py',
    'tools/check_glyph_runtime_config_source_sync.py',
    'tools/check_glyph_runtime_config_validation_health.py',
    'tools/check_glyph_source_owned_source_authority_intake.py',
    'tools/fixtures/configurator_setconfig_host/handler_harness.cpp',
    'tools/fixtures/configurator_setconfig_host/include/arduino/Adafruit_USBD_Device.h',
    'tools/fixtures/configurator_setconfig_host/include/cobs/Print.h',
    'tools/fixtures/configurator_setconfig_host/include/cobs/Stream.h',
    'tools/fixtures/configurator_setconfig_host/include/config.pb.h',
    'tools/fixtures/configurator_setconfig_host/include/core/CommunicationBackend.hpp',
    'tools/fixtures/configurator_setconfig_host/include/core/InputSource.hpp',
    'tools/fixtures/configurator_setconfig_host/include/core/Persistence.hpp',
    'tools/fixtures/configurator_setconfig_host/include/host_stubs.hpp',
    'tools/fixtures/configurator_setconfig_host/include/pb_arduino.h',
    'tools/fixtures/configurator_setconfig_host/include/pb_decode.h',
    'tools/fixtures/configurator_setconfig_host/include/pb_encode.h',
    'tools/fixtures/configurator_setconfig_host/include/reboot.hpp',
    'tools/fixtures/gp_config012_button_host/LICENSE.nanopb.txt',
    'tools/fixtures/gp_config012_button_host/button_harness.cpp',
    'tools/fixtures/gp_config012_button_host/generated/config.pb.c',
    'tools/fixtures/gp_config012_button_host/generated/config.pb.h',
    'tools/fixtures/gp_config012_button_host/include/Arduino.h',
    'tools/fixtures/gp_config012_button_host/include/pico/stdlib.h',
    'tools/fixtures/gp_config012_button_host/nanopb/pb.h',
    'tools/fixtures/gp_config012_button_host/nanopb/pb_common.c',
    'tools/fixtures/gp_config012_button_host/nanopb/pb_common.h',
    'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c',
    'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.h',
    'tools/fixtures/gp_config012_button_host/schema/config.options',
    'tools/fixtures/gp_config012_button_host/schema/config.proto',
    'tools/fixtures/gp_config013_usb_host/usb_harness.cpp',
    'tools/fixtures/mode_selection_host/include/config.pb.h',
    'tools/fixtures/mode_selection_host/generated/LICENSE.nanopb.txt',
    'tools/fixtures/mode_selection_host/generated/README.md',
    'tools/fixtures/mode_selection_host/generated/config.pb.h',
    'tools/fixtures/mode_selection_host/generated/nanopb.library.json',
    'tools/fixtures/mode_selection_host/generated/provenance.json',
    'tools/fixtures/mode_selection_host/include/core/CommunicationBackend.hpp',
    'tools/fixtures/mode_selection_host/include/core/ControllerMode.hpp',
    'tools/fixtures/mode_selection_host/include/core/KeyboardMode.hpp',
    'tools/fixtures/mode_selection_host/include/core/mode_selection.hpp',
    'tools/fixtures/mode_selection_host/include/core/state.hpp',
    'tools/fixtures/mode_selection_host/include/modes/64.hpp',
    'tools/fixtures/mode_selection_host/include/modes/CustomControllerMode.hpp',
    'tools/fixtures/mode_selection_host/include/modes/CustomKeyboardMode.hpp',
    'tools/fixtures/mode_selection_host/include/modes/FgcMode.hpp',
    'tools/fixtures/mode_selection_host/include/modes/Melee20Button.hpp',
    'tools/fixtures/mode_selection_host/include/modes/ProjectM.hpp',
    'tools/fixtures/mode_selection_host/include/modes/Rivals2.hpp',
    'tools/fixtures/mode_selection_host/include/modes/RivalsOfAether.hpp',
    'tools/fixtures/mode_selection_host/include/modes/SenscopePrototype.hpp',
    'tools/fixtures/mode_selection_host/include/modes/Ultimate.hpp',
    'tools/fixtures/mode_selection_host/include/prototypes/senscope/SenscopePrototypeBuildFlags.hpp',
    'tools/fixtures/mode_selection_host/include/util/state_util.hpp',
    'tools/fixtures/mode_selection_host/mode_selection_harness.cpp',
    'tools/fixtures/neopixel_null_host/include/FastLED.h',
    'tools/fixtures/neopixel_null_host/include/config.pb.h',
    'tools/fixtures/neopixel_null_host/include/core/CommunicationBackend.hpp',
    'tools/fixtures/neopixel_null_host/neo_harness.cpp',
    'tools/glyph_hardware_correspondence.py',
    'tools/glyph_serial_config_tool.py',
    'tools/gp_config_005_hw_test.py',
    'tools/source_owned_source_authority_intake.py',
    'tools/test_glyph_docs_agent_surface_integration.py',
    'tools/test_glyph_hardware_correspondence.py',
    'tools/test_glyph_config_010_semantic_applicability.py',
    'tools/test_glyph_config_010_capacity_provenance.py',
    'tools/test_glyph_gp_prov_014_decoder_closure.py',
    'tools/test_gp_config_005_hw_test.py',
})


# GP-VAL-038: exact reviewed source-free literals; critical classification below
# retains precedence. No basename, prefix, caller-supplied set or source exemption.
NON_BEHAVIORAL_PATHS |= frozenset(('docs/agent_framework/GP_CONFIG_021_HARDWARE_PROTOCOL.md', 'docs/calibration/fixtures/gp_config_021_hardware_evidence.json', 'docs/calibration/gp_config_021_hardware_result.md', 'docs/runtime_config/fixtures/gp_config021_persisted_recovery.json', 'docs/runtime_config/fixtures/gp_val038_accepted_transitions.json', 'docs/runtime_config/fixtures/gp_val038_c021_consumer_replay.json', 'docs/runtime_config/fixtures/gp_val038_c021_transition.json', 'docs/runtime_config/gp_config021_persisted_recovery.md', 'tools/check_glyph_c021_proof_replay.py', 'tools/check_glyph_gp_config021_persisted_recovery.py', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/LICENSE.CRC32.md', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/NOTICE.nanopb-arduino.txt', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/GamecubeConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/LICENSE', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/N64Console.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/gamecube_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/joybus.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/library.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/n64_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/library.nanopb-arduino.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/LICENSE', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/NesConsole.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/NesConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/SnesConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/library.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/nes.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/nes_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/snes_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.c', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.h', 'tools/fixtures/gp_config021_persisted_recovery/host_observation.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_GFX.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_SSD1306.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_TinyUSB.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_USBD_XInput.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/Arduino.h', 'tools/fixtures/gp_config021_persisted_recovery/include/FastLED.h', 'tools/fixtures/gp_config021_persisted_recovery/include/LittleFS.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Print.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Stream.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Wire.h', 'tools/fixtures/gp_config021_persisted_recovery/include/arduino/Adafruit_USBD_Device.h', 'tools/fixtures/gp_config021_persisted_recovery/include/avr/pgmspace.h', 'tools/fixtures/gp_config021_persisted_recovery/include/cobs/Print.h', 'tools/fixtures/gp_config021_persisted_recovery/include/cobs/Stream.h', 'tools/fixtures/gp_config021_persisted_recovery/include/comms/backend_init.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/device/usbd_pvt.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/pio.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/structs/usb.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/sync.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/timer.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/lock_core.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/mutex.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/stdlib.h', 'tools/fixtures/gp_config021_persisted_recovery/persistence_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/platform_doubles.cpp', 'tools/fixtures/gp_config021_persisted_recovery/semantic_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/setconfig_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/startup_harness.cpp', 'tools/fixtures/gp_val038_c021_current_consumers/current_consumer_harness.cpp', 'tools/fixtures/gp_val038_c021_current_consumers/getconfig_harness.cpp', 'tools/glyph_c021_campaign_transition.py', 'tools/test_glyph_c021_campaign_transition.py'))


# GP-VAL-039 source/build-role reviewed literal metadata. Active helper, adapter,
# wrapper and approved default paths stay CRITICAL through the first predicate.
NON_BEHAVIORAL_PATHS |= frozenset((
    'docs/runtime_config/fixtures/gp_config022_rgb_target_validation.json',
    'docs/runtime_config/gp_config022_rgb_target_validation.md',
    'docs/runtime_config/gp_config022_owner_config_compatibility.md',
    'tools/check_glyph_gp_config022_rgb_target_validation.py',
    'tools/prepare_glyph_gp_config022_compatibility.py',
    'tools/fixtures/gp_config022_rgb_target_validation/consumer_harness.cpp',
    'tools/fixtures/gp_config022_rgb_target_validation/decoder_harness.cpp',
    'tools/fixtures/gp_config022_rgb_target_validation/persistence_harness.cpp',
    'tools/fixtures/gp_config022_rgb_target_validation/setconfig_harness.cpp',
    'tools/fixtures/gp_config022_rgb_target_validation/startup_harness.cpp',
    'tools/fixtures/gp_config022_rgb_target_validation/validation_harness.cpp',
    'tools/glyph_c022_campaign_transition.py',
    'tools/test_glyph_c022_campaign_transition.py',
    'tools/check_glyph_c022_proof_replay.py',
    'docs/runtime_config/fixtures/gp_val039_c022_transition.json',
    'docs/runtime_config/fixtures/gp_val039_accepted_transitions.json',
    'docs/runtime_config/fixtures/gp_val039_c022_consumer_replay.json',
    'docs/agent_framework/GP_CONFIG_022_HARDWARE_PROTOCOL.md',
    'docs/calibration/gp_config_022_hardware_result.md',
    'docs/calibration/fixtures/gp_config_022_hardware_evidence.json',
))


def classify_path(path: str) -> str:
    """Classify canonical Git paths; never normalize an ambiguous alias."""
    if (not isinstance(path, str) or not path or path.startswith("/")
            or "\\" in path or ":" in path
            or any(ord(char) < 32 or ord(char) == 127 for char in path)
            or any(part in {"", ".", ".."} for part in path.split("/"))):
        raise CorrespondenceError(f"unsafe correspondence path: {path!r}")
    folded = path.casefold()
    if (path in CORRESPONDENCE_CRITICAL_PATHS
            or folded.split("/", 1)[0] in CRITICAL_ROOTS
            or folded in CRITICAL_FILES
            or folded.startswith(".github/workflows/")
            or "/.github/workflows/" in folded):
        return "CRITICAL"
    if path in NON_BEHAVIORAL_PATHS:
        return "NON_BEHAVIORAL"
    raise CorrespondenceError(f"unclassified correspondence path: {path}")


# Enabled only by a bounded campaign proof invocation. The cache contains raw
# outputs of a closed set of full-SHA immutable reads, never successful proofs.
_immutable_query_cache = ContextVar("correspondence_immutable_queries", default=None)


def _immutable_query(args: tuple[str, ...]) -> bool:
    def sha(value: str) -> bool:
        return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None
    if len(args) == 4 and args[:3] == ("ls-tree", "-r", "-z"):
        return sha(args[3])
    if len(args) == 5 and args[:4] == ("rev-list", "--parents", "-n", "1"):
        return sha(args[4])
    if len(args) == 2 and args[0] == "rev-parse":
        return args[1].endswith("^{tree}") and sha(args[1][:-7])
    if len(args) == 4 and args[:3] == ("rev-parse", "--verify", "--end-of-options"):
        return args[3].endswith("^{commit}") and sha(args[3][:-9])
    if len(args) == 3 and args[0] == "merge-base":
        return sha(args[1]) and sha(args[2])
    if len(args) in (6, 7) and args[:4] == ("diff", "--no-renames", "--name-only", "-z"):
        return sha(args[4]) and sha(args[5]) and (len(args) == 6 or args[6] == "--")
    if len(args) == 7 and args[:5] == ("diff-tree", "-r", "--no-renames", "--raw", "-z"):
        return sha(args[5]) and sha(args[6])
    if len(args) == 4 and args[:3] == ("rev-list", "--reverse", "--topo-order"):
        pair = args[3].split("..")
        return len(pair) == 2 and all(sha(value) for value in pair)
    return False


def _git(root: Path, *args: str) -> bytes:
    cache = _immutable_query_cache.get()
    key = (str(Path(root).resolve()), args) if cache is not None and _immutable_query(args) else None
    if key is not None and key in cache:
        return cache[key]
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    if result.returncode:
        raise CorrespondenceError(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}")
    if key is not None:
        cache[key] = result.stdout
    return result.stdout


def _paths(raw: bytes) -> set[str]:
    if raw and not raw.endswith(b"\0"):
        raise CorrespondenceError("unterminated Git path output")
    try:
        return {part.decode("utf-8") for part in raw.split(b"\0") if part}
    except UnicodeDecodeError as exc:
        raise CorrespondenceError("non-UTF-8 Git path") from exc


def _tree(root: Path, revision: str) -> dict[str, tuple[str, str, str]]:
    result = {}
    for record in _git(root, "ls-tree", "-r", "-z", revision).split(b"\0"):
        if record:
            try:
                header, raw_path = record.split(b"\t", 1)
                mode, kind, blob = header.decode("ascii").split()
                result[raw_path.decode("utf-8")] = (mode, kind, blob)
            except (ValueError, UnicodeDecodeError) as exc:
                raise CorrespondenceError("invalid Git tree entry") from exc
    return result


def _entries_safe(path: str, category: str, *entries: tuple[str, str, str] | None) -> None:
    modes = {"100644"} if category == "NON_BEHAVIORAL" else {"100644", "100755"}
    for entry in entries:
        if entry is not None and (entry[0] not in modes or entry[1] != "blob"):
            raise CorrespondenceError(f"unsupported correspondence entry: {path}: {entry[:2]}")


def _working_mode(root: Path, path: str) -> int:
    location = root / path
    for parent in location.parents:
        if parent == root:
            break
        if parent.is_symlink():
            raise CorrespondenceError(f"symlinked correspondence directory: {path}")
    return location.lstat().st_mode


def verify_correspondence(root: Path, candidate: str, tested_base: str,
                          target: str = "HEAD", *, integrated: bool,
                          check_worktree: bool = True) -> dict[str, object]:
    """Require exact critical inputs and audited metadata in both complete deltas.

This does not confer hardware acceptance or authorize metadata mutations.
    Callers must pin the actual candidate/artifact/PASS independently.
    """
    root = root.resolve()
    if not all(re.fullmatch(r"[0-9a-f]{40}", value) for value in (candidate, tested_base)):
        raise CorrespondenceError("candidate and tested base must be full immutable Git identities")
    # Resolve once; subsequent operations do not race against a moving target ref.
    target_sha = _git(root, "rev-parse", "--verify", "--end-of-options", f"{target}^{{commit}}").decode().strip()
    parents = _git(root, "rev-list", "--parents", "-n", "1", candidate).decode().split()
    if parents != [candidate, tested_base]:
        raise CorrespondenceError("candidate tested parent mismatch")
    baseline = candidate if integrated else tested_base
    merge_base = _git(root, "merge-base", candidate, target_sha).decode().strip()
    if merge_base != baseline:
        raise CorrespondenceError("candidate ancestry does not match correspondence phase")
    base_tree, candidate_tree, target_tree = (_tree(root, ref) for ref in (tested_base, candidate, target_sha))
    candidate_paths = _paths(_git(root, "diff", "--no-renames", "--name-only", "-z", tested_base, candidate, "--"))
    candidate_categories = {}
    for path in sorted(candidate_paths):
        category = candidate_categories[path] = classify_path(path)
        _entries_safe(path, category, base_tree.get(path), candidate_tree.get(path))
    target_paths = _paths(_git(root, "diff", "--no-renames", "--name-only", "-z", baseline, target_sha, "--"))
    baseline_tree = candidate_tree if integrated else base_tree
    target_categories = {}
    for path in sorted(target_paths):
        category = target_categories[path] = classify_path(path)
        _entries_safe(path, category, baseline_tree.get(path), target_tree.get(path))
        if category == "CRITICAL":
            raise CorrespondenceError(f"critical input differs from tested snapshot: {path}")
    dirty_categories = {}
    if check_worktree:
        dirty = _paths(_git(root, "diff", "--no-renames", "--name-only", "-z", "--"))
        dirty |= _paths(_git(root, "diff", "--cached", "--no-renames", "--name-only", "-z", "--"))
        dirty |= _paths(_git(root, "ls-files", "--others", "--exclude-standard", "-z"))
        # Git ignores do not exclude source from the firmware compiler. The
        # shared seam applies the exact audited inventory and excludes caches.
        try:
            dirty |= set(ignored_critical_worktree_paths(root))
        except TrackedWorktreeIntegrityError as exc:
            raise CorrespondenceError("unable to inspect ignored critical inputs") from exc
        index = {}
        for record in _git(root, "ls-files", "--stage", "-z").split(b"\0"):
            if record:
                header, name = record.split(b"\t", 1)
                mode, blob, stage = header.decode().split()
                path = name.decode("utf-8")
                if stage != "0":
                    raise CorrespondenceError(f"unmerged index: {path}")
                index[path] = (mode, "blob", blob)
        # Git diff can hide assume-unchanged/skip-worktree files and stat-cache
        # collisions. Inspect every indexed critical file's actual mode/bytes,
        # independently of those Git optimizations and without content filters.
        for path, entry in index.items():
            try:
                category = classify_path(path)
            except CorrespondenceError:
                continue  # Unchanged unknown paths are not new exemptions.
            if category != "CRITICAL":
                continue
            _entries_safe(path, category, entry)
            try:
                mode = _working_mode(root, path)
                if not stat.S_ISREG(mode):
                    raise CorrespondenceError(f"non-regular critical working input: {path}")
                raw = (root / path).read_bytes()
            except OSError as exc:
                raise CorrespondenceError(f"unreadable critical working input: {path}") from exc
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != entry[2] or bool(mode & 0o111) != (entry[0] == "100755"):
                raise CorrespondenceError(f"dirty critical working input: {path}")
        for path in sorted(dirty):
            category = dirty_categories[path] = classify_path(path)
            if category == "CRITICAL":
                raise CorrespondenceError(f"dirty critical input: {path}")
            _entries_safe(path, category, index.get(path))
            try:
                mode = _working_mode(root, path)
            except FileNotFoundError:
                continue  # A metadata deletion is left to its normal validator.
            if not stat.S_ISREG(mode) or mode & 0o111:
                raise CorrespondenceError(f"non-regular/non-100644 working metadata: {path}")
    return {"phase": "integrated" if integrated else "pre_integration",
            "candidate": candidate, "tested_base": tested_base, "target": target_sha,
            "candidate_paths": candidate_categories, "target_paths": target_categories,
            "dirty_paths": dirty_categories,
            "normal_metadata_validation_required": True}
