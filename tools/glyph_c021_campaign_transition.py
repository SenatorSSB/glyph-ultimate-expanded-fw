"""Finite GP-VAL-038 exact C021 admission and hardware chronology.

Candidate source validation is never controller acceptance. Original predecessor
callables and observations remain at their immutable object roots.
"""
from __future__ import annotations
import hashlib
import json
import re
import stat
from glyph_tracked_worktree_integrity import IGNORED_ALLOWED_ROOTS
from pathlib import Path
from types import ModuleType
import glyph_c017_campaign_transition as previous
from glyph_hardware_correspondence import CorrespondenceError, classify_path, verify_correspondence

stateutil = previous.previous
original = stateutil.original
require = previous.require
_git = previous._git
_tree = previous._tree
raw_bytes = previous.raw_bytes
current_bytes = previous.current_bytes
critical_tree = previous.critical_tree
ancestor = previous.ancestor
item = previous.item
unique = previous.unique
sha = previous.sha
_stage_and_live = previous._stage_and_live
QUEUE = previous.QUEUE
C = 'a170bd40a51741582913324bfecbc14ce9b3211d'
B = 'c6887115f2e44f0803eb0956ebb574633cec53be'
TREE = '91ca6d86c2fa28b55ef5a6b3623b25748b167feb'
RAW = '09ac5a6ae8db4d0cba50731187057394a3a8819969abd769f331765b58d7878d'
HANDOFF = '80a22333fd783bcd89ac46bab10c219b3cbaf8f6'
READY = '80a22333fd783bcd89ac46bab10c219b3cbaf8f6'
MAPPING = 'docs/runtime_config/fixtures/gp_val038_c021_transition.json'
TRANSITIONS = 'docs/runtime_config/fixtures/gp_val038_accepted_transitions.json'
MAPPING_SHA256 = '9ee3b2ebed68dabe8d4a60312c8df2c5e84f128f22cdcd6e2f304af87dc1bfab'
PROTOCOL = 'docs/agent_framework/GP_CONFIG_021_HARDWARE_PROTOCOL.md'
EVIDENCE = 'docs/calibration/fixtures/gp_config_021_hardware_evidence.json'
RESULT = 'docs/calibration/gp_config_021_hardware_result.md'
CHECKER = 'tools/check_glyph_gp_config021_persisted_recovery.py'
CHECKER_BLOB = 'a3d3dd9186c7f885316adca16706d360e652dd90'
CHECKER_SHA256 = '2dc78d118dd2936ad9544a297ef00a66a140f90dc58152c87c2abbe423ef556d'
CRITICAL = frozenset(('HAL/pico/include/core/Persistence.hpp', 'HAL/pico/src/comms/ConfiguratorBackend.cpp', 'HAL/pico/src/core/Persistence.cpp', 'config/glyph/common/src/config.cpp', 'include/core/config_validation.hpp', 'src/core/config_validation.cpp'))
HOSTS = frozenset(('docs/runtime_config/fixtures/gp_config021_persisted_recovery.json', 'docs/runtime_config/gp_config021_persisted_recovery.md', 'tools/check_glyph_gp_config021_persisted_recovery.py', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/LICENSE.CRC32.md', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/NOTICE.nanopb-arduino.txt', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/GamecubeConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/LICENSE', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/N64Console.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/gamecube_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/joybus.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/library.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/n64_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/library.nanopb-arduino.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/LICENSE', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/NesConsole.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/NesConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/SnesConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/library.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/nes.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/nes_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/snes_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.c', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.h', 'tools/fixtures/gp_config021_persisted_recovery/host_observation.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_GFX.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_SSD1306.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_TinyUSB.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_USBD_XInput.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/Arduino.h', 'tools/fixtures/gp_config021_persisted_recovery/include/FastLED.h', 'tools/fixtures/gp_config021_persisted_recovery/include/LittleFS.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Print.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Stream.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Wire.h', 'tools/fixtures/gp_config021_persisted_recovery/include/arduino/Adafruit_USBD_Device.h', 'tools/fixtures/gp_config021_persisted_recovery/include/avr/pgmspace.h', 'tools/fixtures/gp_config021_persisted_recovery/include/cobs/Print.h', 'tools/fixtures/gp_config021_persisted_recovery/include/cobs/Stream.h', 'tools/fixtures/gp_config021_persisted_recovery/include/comms/backend_init.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/device/usbd_pvt.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/pio.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/structs/usb.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/sync.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/timer.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/lock_core.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/mutex.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/stdlib.h', 'tools/fixtures/gp_config021_persisted_recovery/persistence_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/platform_doubles.cpp', 'tools/fixtures/gp_config021_persisted_recovery/semantic_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/setconfig_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/startup_harness.cpp'))
METADATA = frozenset(('docs/runtime_config/fixtures/glyph_checker_census.json', 'docs/runtime_config/fixtures/runtime_config_validation_health.json', 'docs/runtime_config/fixtures/runtime_config_validation_manifest.json', 'docs/runtime_config/runtime_config_validation_health.md'))
NEW_PATHS = frozenset((MAPPING, TRANSITIONS, 'tools/glyph_c021_campaign_transition.py',
                       'tools/test_glyph_c021_campaign_transition.py'))
CONSUMER_PATHS = frozenset(('tools/check_glyph_c021_proof_replay.py',
                           'docs/runtime_config/fixtures/gp_val038_c021_consumer_replay.json'))
CONSUMER_PATHS |= frozenset(('tools/fixtures/gp_val038_c021_current_consumers/getconfig_harness.cpp',
                            'tools/fixtures/gp_val038_c021_current_consumers/current_consumer_harness.cpp'))
GOVERNANCE_PATHS = previous.GOVERNANCE_PATHS | HOSTS | METADATA | NEW_PATHS | CONSUMER_PATHS | frozenset((PROTOCOL, EVIDENCE, RESULT))
ROOTS = previous.ROOTS | frozenset((C, B, HANDOFF, READY))
# Existing current inputs may change only at these allocated control-plane seams.
# All prior KBD/019/014 host/replay/0028 inputs retain exact B modes/blobs/live.
SHARED_CURRENT_PATHS = frozenset((
    'docs/AGENT_CONTEXT.md', 'docs/CURRENT_STATE.md', 'docs/ROADMAP.md', QUEUE,
    'docs/agent_framework/HARDWARE_CORRESPONDENCE.md',
    'tools/glyph_campaign_transition.py', 'tools/glyph_checker_context.py',
    'tools/glyph_hardware_correspondence.py', 'tools/run_glyph_runtime_config_validation.py',
    'tools/check_glyph_runtime_config_validation_aggregate.py',
    'tools/check_glyph_docs_agent_surface.py',
    'tools/check_glyph_config_010_integration_semantic_correspondence.py')) | METADATA
REQUIRED_ROWS = ('valid_stored_boot', 'rejected_file', 'persistent_refusal',
                 'display_failure_refusal', 'no_gameplay_reports',
                 'rejected_file_reboot', 'recovery_restoration')


REPLAY_LANES = {'current_config_persistence_recovery_research': 'persistence', 'getconfig_raw_load_characterization': 'raw_get', 'configurator_setconfig_transaction': 'transaction005', 'setconfig_runtime_rebinding_characterization': 'rebind008', 'config_menu_invalid_state_characterization': 'menu009', 'gp_config_012_button_mask_characterization': 'button012', 'gp_config_013_usb_default_characterization': 'usb013', 'gp_config020_button_validation': 'button020', 'gp_kbd_001_keyboard_pipeline': 'kbd001', 'gp_config019_usb_name_selection': 'usb019', 'neopixel_null_sendreport_characterization': 'neopixel016_017', 'gp_config017_neopixel_repaired_current': 'neopixel016_017', 'custom_modifier_cache_characterization': 'modifier011', 'gp_config014_modifier_capacity': 'modifier014', 'gp_val035_c017_transition':'transition035'}

REQUIRED_NEW_DEPENDENCIES = {'gp_config021_persisted_recovery': ('HAL/pico/include/comms/ConfiguratorBackend.hpp', 'HAL/pico/include/comms/DInputBackend.hpp', 'HAL/pico/include/comms/GamecubeBackend.hpp', 'HAL/pico/include/comms/N64Backend.hpp', 'HAL/pico/include/comms/NeoPixelBackend.hpp', 'HAL/pico/include/comms/NesBackend.hpp', 'HAL/pico/include/comms/NintendoSwitchBackend.hpp', 'HAL/pico/include/comms/SnesBackend.hpp', 'HAL/pico/include/comms/XInputBackend.hpp', 'HAL/pico/include/core/KeyboardMode.hpp', 'HAL/pico/include/core/Persistence.hpp', 'HAL/pico/include/display/ConfigMenu.hpp', 'HAL/pico/include/display/ConfigMenuAssets/GlyphMenuBitmaps.h', 'HAL/pico/include/display/DefaultConfigMenu.hpp', 'HAL/pico/include/display/DisplayMode.hpp', 'HAL/pico/include/display/InputDisplay.hpp', 'HAL/pico/include/display/RemapMenu.hpp', 'HAL/pico/include/display/RgbBrightnessMenu.hpp', 'HAL/pico/include/gpio.hpp', 'HAL/pico/include/input/DebouncedSwitchMatrixInput.hpp', 'HAL/pico/include/input/debounce.hpp', 'HAL/pico/include/rgb/ButtonLocations.hpp', 'HAL/pico/include/serial.hpp', 'HAL/pico/include/stdlib.hpp', 'HAL/pico/include/util/state_util.hpp', 'HAL/pico/src/comms/ConfiguratorBackend.cpp', 'HAL/pico/src/comms/DInputBackend.cpp', 'HAL/pico/src/comms/GamecubeBackend.cpp', 'HAL/pico/src/comms/N64Backend.cpp', 'HAL/pico/src/comms/NesBackend.cpp', 'HAL/pico/src/comms/NintendoSwitchBackend.cpp', 'HAL/pico/src/comms/SnesBackend.cpp', 'HAL/pico/src/comms/XInputBackend.cpp', 'HAL/pico/src/comms/backend_init.cpp', 'HAL/pico/src/comms/console_detection.cpp', 'HAL/pico/src/core/KeyboardMode.cpp', 'HAL/pico/src/core/Persistence.cpp', 'HAL/pico/src/display/ConfigMenu.cpp', 'HAL/pico/src/display/DefaultConfigMenu.cpp', 'HAL/pico/src/display/InputDisplay.cpp', 'HAL/pico/src/display/RemapMenu.cpp', 'HAL/pico/src/display/RgbBrightnessMenu.cpp', 'HAL/pico/src/gpio.cpp', 'HAL/pico/src/reboot.cpp', 'HAL/pico/src/rgb/ButtonLocations.cpp', 'HAL/pico/src/serial.cpp', 'builder_scripts/arduino_pico.py', 'config/glyph/common/include/LEDTemplates.hpp', 'config/glyph/common/include/display/AboutMenu.hpp', 'config/glyph/common/include/display/Font4x7Fixed.h', 'config/glyph/common/include/display/GlyphConfigMenu.hpp', 'config/glyph/common/include/display/MenuButtonHints.hpp', 'config/glyph/common/include/display/OopsieMenu.hpp', 'config/glyph/common/include/display/Picopixel.h', 'config/glyph/common/include/glyph_overrides.hpp', 'config/glyph/common/include/icons/12x12bitmaps.hpp', 'config/glyph/common/include/icons/16x16bitmaps.hpp', 'config/glyph/common/include/icons/menubases.hpp', 'config/glyph/common/include/icons/splashscreen.hpp', 'config/glyph/common/src/LEDTemplates.cpp', 'config/glyph/common/src/config.cpp', 'config/glyph/common/src/display/AboutMenu.cpp', 'config/glyph/common/src/display/GlyphConfigMenu.cpp', 'config/glyph/common/src/display/MenuButtonHints.cpp', 'config/glyph/common/src/display/OopsieMenu.cpp', 'config/glyph/env.ini', 'config/glyph/glyph_mk6/include/button_positions.hpp', 'config/glyph/glyph_mk6/include/glyph_pinout.hpp', 'config/glyph/glyph_mk6/include/matrix_definition.hpp', 'config/glyph/glyph_mk6/include/neopixel_definitions.hpp', 'docs/runtime_config/fixtures/gp_config021_persisted_recovery.json', 'docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json', 'docs/runtime_config/fixtures/gp_val038_accepted_transitions.json', 'docs/runtime_config/fixtures/gp_val038_c021_consumer_replay.json', 'docs/runtime_config/fixtures/gp_val038_c021_transition.json', 'docs/runtime_config/gp_config021_persisted_recovery.md', 'docs/runtime_config/gp_prov_014_decoder_closure.md', 'include/comms/B0XXInputViewer.hpp', 'include/comms/IntegratedDisplay.hpp', 'include/comms/console_detection.hpp', 'include/core/CommunicationBackend.hpp', 'include/core/ControllerMode.hpp', 'include/core/InputMode.hpp', 'include/core/InputSource.hpp', 'include/core/config_button_validation.hpp', 'include/core/config_utils.hpp', 'include/core/mode_selection.hpp', 'include/core/pinout.hpp', 'include/core/socd.hpp', 'include/core/state.hpp', 'include/img/remap.hpp', 'include/img/update.hpp', 'include/input/SwitchMatrixInput.hpp', 'include/modes/64.hpp', 'include/modes/CustomControllerMode.hpp', 'include/modes/CustomKeyboardMode.hpp', 'include/modes/FgcMode.hpp', 'include/modes/Melee20Button.hpp', 'include/modes/ProjectM.hpp', 'include/modes/Rivals2.hpp', 'include/modes/RivalsOfAether.hpp', 'include/modes/SenscopePrototype.hpp', 'include/modes/Ultimate.hpp', 'include/prototypes/senscope/SenscopePrototypeBuildFlags.hpp', 'include/prototypes/senscope/SenscopePrototypeDigital.hpp', 'include/prototypes/senscope/SenscopePrototypeDirection.hpp', 'include/prototypes/senscope/SenscopePrototypeForce.hpp', 'include/prototypes/senscope/SenscopePrototypeModifier.hpp', 'include/prototypes/senscope/SenscopePrototypeOutput.hpp', 'include/prototypes/senscope/SenscopePrototypeResolver.hpp', 'include/prototypes/senscope/SenscopePrototypeSelfTest.hpp', 'include/prototypes/senscope/SenscopePrototypeTypes.hpp', 'include/reboot.hpp', 'lib/TUCompositeHID/include/TUCompositeHID.hpp', 'lib/TUCompositeHID/include/TUGamepad.hpp', 'lib/TUCompositeHID/include/TUKeyboard.hpp', 'lib/TUCompositeHID/src/TUCompositeHID.cpp', 'lib/TUCompositeHID/src/TUGamepad.cpp', 'lib/TUCompositeHID/src/TUKeyboard.cpp', 'platformio.ini', 'src/comms/B0XXInputViewer.cpp', 'src/comms/IntegratedDisplay.cpp', 'src/core/CommunicationBackend.cpp', 'src/core/ControllerMode.cpp', 'src/core/InputMode.cpp', 'src/core/InputSource.cpp', 'src/core/config_button_validation.cpp', 'src/core/config_utils.cpp', 'src/core/mode_selection.cpp', 'src/core/socd.cpp', 'src/modes/64.cpp', 'src/modes/CustomControllerMode.cpp', 'src/modes/CustomKeyboardMode.cpp', 'src/modes/FgcMode.cpp', 'src/modes/Melee20Button.cpp', 'src/modes/ProjectM.cpp', 'src/modes/Rivals2.cpp', 'src/modes/RivalsOfAether.cpp', 'src/modes/SenscopePrototype.cpp', 'src/modes/Ultimate.cpp', 'src/modes/UltimateIdentityRuntimeTables.hpp', 'src/modes/UltimateRuntimeConfigInterpreter.hpp', 'src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp', 'src/prototypes/senscope/SenscopePrototypeDigital.cpp', 'src/prototypes/senscope/SenscopePrototypeDirection.cpp', 'src/prototypes/senscope/SenscopePrototypeForce.cpp', 'src/prototypes/senscope/SenscopePrototypeModifier.cpp', 'src/prototypes/senscope/SenscopePrototypeOutput.cpp', 'src/prototypes/senscope/SenscopePrototypeResolver.cpp', 'src/prototypes/senscope/SenscopePrototypeSelfTest.cpp', 'src/prototypes/senscope/SenscopePrototypeValidation.cpp', 'tools/check_glyph_gp_config021_persisted_recovery.py', 'tools/fixtures/gp_config012_button_host/LICENSE.nanopb.txt', 'tools/fixtures/gp_config012_button_host/generated/config.pb.c', 'tools/fixtures/gp_config012_button_host/generated/config.pb.h', 'tools/fixtures/gp_config012_button_host/nanopb/pb.h', 'tools/fixtures/gp_config012_button_host/nanopb/pb_common.c', 'tools/fixtures/gp_config012_button_host/nanopb/pb_common.h', 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c', 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.h', 'tools/fixtures/gp_config012_button_host/schema/config.options', 'tools/fixtures/gp_config012_button_host/schema/config.proto', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/LICENSE.CRC32.md', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/NOTICE.nanopb-arduino.txt', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/GamecubeConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/LICENSE', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/N64Console.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/gamecube_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/joybus.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/library.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/n64_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/library.nanopb-arduino.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/LICENSE', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/NesConsole.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/NesConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/SnesConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/library.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/nes.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/nes_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/snes_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.c', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.h', 'tools/fixtures/gp_config021_persisted_recovery/host_observation.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_GFX.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_SSD1306.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_TinyUSB.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_USBD_XInput.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/Arduino.h', 'tools/fixtures/gp_config021_persisted_recovery/include/FastLED.h', 'tools/fixtures/gp_config021_persisted_recovery/include/LittleFS.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Print.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Stream.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Wire.h', 'tools/fixtures/gp_config021_persisted_recovery/include/arduino/Adafruit_USBD_Device.h', 'tools/fixtures/gp_config021_persisted_recovery/include/avr/pgmspace.h', 'tools/fixtures/gp_config021_persisted_recovery/include/cobs/Print.h', 'tools/fixtures/gp_config021_persisted_recovery/include/cobs/Stream.h', 'tools/fixtures/gp_config021_persisted_recovery/include/comms/backend_init.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/device/usbd_pvt.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/pio.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/structs/usb.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/sync.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/timer.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/lock_core.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/mutex.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/stdlib.h', 'tools/fixtures/gp_config021_persisted_recovery/persistence_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/platform_doubles.cpp', 'tools/fixtures/gp_config021_persisted_recovery/semantic_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/setconfig_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/startup_harness.cpp', 'tools/fixtures/gp_val038_c021_current_consumers/current_consumer_harness.cpp', 'tools/fixtures/gp_val038_c021_current_consumers/getconfig_harness.cpp', 'tools/glyph_c021_campaign_transition.py', 'tools/glyph_campaign_transition.py', 'tools/glyph_hardware_correspondence.py', 'tools/glyph_tracked_worktree_integrity.py', 'tools/test_glyph_c021_campaign_transition.py'), 'gp_val038_c021_transition': ('docs/runtime_config/fixtures/gp_config021_persisted_recovery.json', 'docs/runtime_config/fixtures/gp_val038_accepted_transitions.json', 'docs/runtime_config/fixtures/gp_val038_c021_consumer_replay.json', 'docs/runtime_config/fixtures/gp_val038_c021_transition.json', 'docs/runtime_config/gp_config021_persisted_recovery.md', 'tools/check_glyph_c021_proof_replay.py', 'tools/check_glyph_gp_config021_persisted_recovery.py', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/LICENSE.CRC32.md', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/NOTICE.nanopb-arduino.txt', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/GamecubeConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/LICENSE', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/N64Console.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/gamecube_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/joybus.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/library.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/n64_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/library.nanopb-arduino.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/LICENSE', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/NesConsole.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/NesConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/SnesConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/library.json', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/nes.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/nes_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/snes_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.c', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.h', 'tools/fixtures/gp_config021_persisted_recovery/host_observation.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_GFX.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_SSD1306.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_TinyUSB.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_USBD_XInput.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/Arduino.h', 'tools/fixtures/gp_config021_persisted_recovery/include/FastLED.h', 'tools/fixtures/gp_config021_persisted_recovery/include/LittleFS.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Print.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Stream.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Wire.h', 'tools/fixtures/gp_config021_persisted_recovery/include/arduino/Adafruit_USBD_Device.h', 'tools/fixtures/gp_config021_persisted_recovery/include/avr/pgmspace.h', 'tools/fixtures/gp_config021_persisted_recovery/include/cobs/Print.h', 'tools/fixtures/gp_config021_persisted_recovery/include/cobs/Stream.h', 'tools/fixtures/gp_config021_persisted_recovery/include/comms/backend_init.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/device/usbd_pvt.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/pio.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/structs/usb.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/sync.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/timer.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/lock_core.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/mutex.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/stdlib.h', 'tools/fixtures/gp_config021_persisted_recovery/persistence_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/platform_doubles.cpp', 'tools/fixtures/gp_config021_persisted_recovery/semantic_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/setconfig_harness.cpp', 'tools/fixtures/gp_config021_persisted_recovery/startup_harness.cpp', 'tools/fixtures/gp_val038_c021_current_consumers/current_consumer_harness.cpp', 'tools/fixtures/gp_val038_c021_current_consumers/getconfig_harness.cpp', 'tools/glyph_c021_campaign_transition.py', 'tools/glyph_campaign_transition.py', 'tools/glyph_hardware_correspondence.py', 'tools/glyph_tracked_worktree_integrity.py')}

def present(root: Path) -> bool:
    root = Path(root).resolve()
    tree = _tree(root, _git(root, 'rev-parse', 'HEAD').decode().strip())
    return any(path in tree or (root / path).exists() or (root / path).is_symlink()
               for path in (MAPPING, TRANSITIONS, 'tools/glyph_c021_campaign_transition.py'))


def _handoff(root: Path) -> dict:
    text = raw_bytes(root, HANDOFF, QUEUE).decode()
    start = '<!-- gp-config021-handoff-val038-activation:start -->'
    end = '<!-- gp-config021-handoff-val038-activation:end -->'
    require(text.count(start) == text.count(end) == 1, '021 handoff marker substitution')
    block = text.split(start)[1].split(end)[0].strip()
    require(block.startswith('```json') and block.endswith('```'), '021 handoff fence substitution')
    value = json.loads(block[7:-3], object_pairs_hook=unique)
    require(value['schema_name'] == 'glyph_gp_config021_candidate_handoff_val038_activation'
            and type(value['schema_version']) is int and value['schema_version'] == 1
            and (value['candidate'], value['canonical_base'], value['candidate_tree'],
                 value['candidate_direct_parent']) == (C, B, TREE, B)
            and value['source_free_canonical'] is True and value['gate_waivers'] is False,
            '021 handoff identity/scope substitution')
    for key, field, expected in (
        ('independent_review', 'review_sha256', '6d90b29bf0c8de5a03057abd2dc304b46e9b16745ccafd245778aff76f61d134'),
        ('source_proof', 'source_proof_sha256', 'f1a3a90beb9e953374302e2537351ee6a08c63b6d289b2120ca8dc554a3724c1'),
        ('conformance', 'conformance_sha256', '2c38eb6a389fa33d0f22648cbc49797fbe81402ecebf8638152b432d7c0a4c51')):
        require(value[field] == expected and sha((json.dumps(value[key], indent=2) + '\n').encode()) == expected,
                '021 handoff report substitution: ' + key)
    review = value['independent_review']
    require(review['reviewed_sha'] == C and review['reviewed_tree'] == TREE
            and review['verdict'] == 'APPROVED' and review['blocking_findings'] == []
            and value['conformance']['raw_inventory_sha256'] == RAW
            and value['conformance']['complete_inventory_count'] == 66,
            '021 independent conformance receipt substitution')
    return value


def _candidate_module(root: Path):
    raw = raw_bytes(root, C, CHECKER)
    require(_tree(root, C)[CHECKER] == ('100644', 'blob', CHECKER_BLOB)
            and sha(raw) == CHECKER_SHA256, '021 immutable engine substitution')
    module = ModuleType('glyph_c021_immutable_engine')
    module.__file__ = str(root / CHECKER)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    require(module.BASE == B and frozenset(module.SOURCES) == CRITICAL
            and len(module.PINS) == 214, '021 engine literal closure substitution')
    return module


@original._proof_invocation
def source_contract(root: Path):
    root = Path(root).resolve()
    require(_git(root, 'rev-list', '--parents', '-n', '1', C).decode().split() == [C, B]
            and _git(root, 'rev-parse', C + '^{tree}').decode().strip() == TREE
            and sha(_git(root, 'diff-tree', '-r', '--no-renames', '--raw', '-z', B, C)) == RAW,
            '021 candidate parent/tree/raw inventory substitution')
    head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    require(ancestor(root, READY, head) and ancestor(root, B, HANDOFF)
            and not ancestor(root, C, HANDOFF), '021 source-free READY chronology')
    require(item(root, READY, 'GP-VAL-038')['status'] == 'READY'
            and item(root, READY, 'GP-CONFIG-021')['status'] == 'REVIEW'
            and item(root, READY, 'GP-VAL-035')['status'] == 'DONE', '021 READY/predecessor state')
    mapping_raw = current_bytes(root, MAPPING)
    require(sha(mapping_raw) == MAPPING_SHA256, '021 mapping substitution')
    mapping = json.loads(mapping_raw, object_pairs_hook=unique)
    handoff = _handoff(root)
    require(set(mapping) == {'schema_name', 'schema_version', 'work_order', 'candidate',
            'base', 'tree', 'raw_inventory_sha256', 'entries', 'handoff', 'ready',
            'review_sha256', 'source_proof_sha256', 'conformance_sha256'}
            and mapping['schema_name'] == 'glyph_gp_val038_c021_transition'
            and type(mapping['schema_version']) is int and mapping['schema_version'] == 1
            and mapping['work_order'] == 'GP-VAL-038'
            and tuple(mapping[k] for k in ('candidate', 'base', 'tree', 'raw_inventory_sha256',
                                           'handoff', 'ready')) == (C, B, TREE, RAW, HANDOFF, READY)
            and all(mapping[k] == handoff[k] for k in
                    ('review_sha256', 'source_proof_sha256', 'conformance_sha256'))
            and mapping['entries'] == handoff['conformance']['inventory'],
            '021 mapping identity/review substitution')
    bt, ct = _tree(root, B), _tree(root, C)
    delta = {p for p in bt.keys() | ct.keys() if bt.get(p) != ct.get(p)}
    rows = {row['path']: row for row in mapping['entries']}
    require(delta == CRITICAL | HOSTS | METADATA and len(delta) == len(rows) == len(mapping['entries']) == 66,
            '021 finite inventory duplicate/omission/extension')
    for path in sorted(delta):
        row = rows[path]; old = bt.get(path); new = ct.get(path)
        require(set(row) == {'path', 'old_mode', 'new_mode', 'old_blob', 'new_blob', 'status', 'new_sha256', 'bytes'}
                and new[:2] == ('100644', 'blob') and row['new_mode'] == new[0]
                and row['new_blob'] == new[2] and row['new_sha256'] == sha(raw_bytes(root, C, path))
                and row['bytes'] == len(raw_bytes(root, C, path))
                and (row['old_mode'], row['old_blob'], row['status']) ==
                    ((old[0], old[2], 'M') if old else ('000000', '0' * 40, 'A')),
                '021 inventory mode/blob/bytes substitution: ' + path)
        require(classify_path(path) == ('CRITICAL' if path in CRITICAL else 'NON_BEHAVIORAL'),
                '021 input role classification substitution: ' + path)
    before, after = critical_tree(root, B), critical_tree(root, C)
    require(len(before) == 236 and len(after) == 238
            and {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)} == CRITICAL
            and sum(after[p] == before.get(p) for p in after) == 232,
            '021 critical tree outside exact six-source contract')
    engine = _candidate_module(root)
    for path, pin in engine.PINS.items():
        raw = raw_bytes(root, C, path)
        require(_tree(root, C)[path] == (pin['mode'], 'blob', pin['blob'])
                and pin['mode'] == '100644' and sha(raw) == pin['sha256'],
                '021 immutable dependency closure substitution: ' + path)
    fixture = raw_bytes(root, C, engine.FIXTURE)
    require(sha(fixture) == engine.FIXTURE_SHA256
            and json.loads(fixture, object_pairs_hook=unique) == engine.fixture_contract(),
            '021 immutable fixture contract substitution')
    engine._source_contract({p: raw_bytes(root, C, p).decode() for p in engine.SOURCES})
    old = raw_bytes(root, B, 'HAL/pico/include/comms/backend_init.hpp')
    adapter = raw_bytes(root, C, engine.HOST + '/include/comms/backend_init.hpp')
    parameter = b'detect_console_t detect_console = &detect_console,'
    require(old.count(parameter) == 1 and old.replace(parameter,
        b'detect_console_t detect_console_fn = &detect_console,', 1) == adapter,
        '021 adapter changed beyond declaration parameter')
    p = 'HAL/pico/src/core/Persistence.cpp'
    old_save = engine._function(raw_bytes(root, B, p).decode(), 'bool Persistence::SaveConfig(', 'bool Persistence::LoadConfig(')
    new_save = engine._function(raw_bytes(root, C, p).decode(), 'bool Persistence::SaveConfig(', 'bool Persistence::LoadConfig(')
    guard = '    if (!IsAvailable()) {\n        return false;\n    }\n'
    require(new_save.count(guard) == 1 and new_save.replace(guard, '', 1) == old_save,
            '021 successful SaveConfig body changed beyond mount guard')
    require(critical_tree(root, HANDOFF) == before and critical_tree(root, READY) == before,
            '021 source entered activation snapshot')
    return before, after


@original._proof_invocation
def predecessor_contract(root: Path):
    """Use native immutable017 source/build/processor/catalog APIs at B021."""
    old_before, old_after = previous.source_contract(root)
    prior, accepted014 = previous.predecessor_contract(root)
    require(critical_tree(root, B) == old_after, '021 base lost accepted017 source')
    records = previous._catalog(raw_bytes(root, B, previous.TRANSITIONS))
    require(len(records) == 1, '021 lacks exact accepted017 catalog')
    record = records[0]
    E = record['evidence_commit']
    processor = previous._processor(root, E, item(root, E, 'GP-CONFIG-017'), old_before, old_after)
    previous._accepted(root, B, record, processor, old_after)
    state = item(root, B, 'GP-CONFIG-017')
    require(state['status'] == 'DONE' and state['hardware_result'] == 'PASS'
            and state['hardware_evidence_gaps'] == [] and stateutil.same_acceptance(state, processor['native'])
            and item(root, B, 'GP-VAL-035')['status'] == 'DONE', '021 lacks strict017/035 predecessor')
    from check_glyph_agent_framework_docs import validate_completion_evidence
    for identity in ('GP-CONFIG-017', 'GP-VAL-035'):
        row = item(root, B, identity)
        payload = original.queue(root, B)
        validate_completion_evidence(row, row['done_evidence'], policy=payload['completion_correspondence'],
                                     publication_sha=B, repo_root=root)
    roots = set(previous.ROOTS) | set(prior['c020_object_roots']) | {record['integration']}
    roots |= {processor[k] for k in ('build', 'parent', 'review_commit', 'evidence_commit', 'evidence_root')}
    roots |= {prior[k] for k in ('build', 'parent', 'review_commit', 'evidence_commit', 'evidence_root')}
    return dict(processor, object_roots=frozenset(roots)), record


def _preserve_accepted_predecessors(root: Path, head: str):
    orders = ('GP-CONFIG-020', 'GP-CONFIG-014', 'GP-CONFIG-017')
    paths = tuple(p for helper in (stateutil.predecessor, stateutil, previous)
                  for p in (helper.PROTOCOL, helper.EVIDENCE, helper.RESULT, helper.TRANSITIONS))
    revisions = [B] + _git(root, 'rev-list', '--reverse', '--topo-order', B + '..' + head).decode().split()
    for revision in revisions:
        for order in orders:
            accepted = item(root, B, order); row = item(root, revision, order)
            require(row['status'] == 'DONE' and row['hardware_result'] == 'PASS'
                    and row['hardware_evidence_gaps'] == [] and stateutil.same_acceptance(row, accepted),
                    '021 predecessor acceptance erased/replaced: ' + order)
        for path in paths:
            require(_tree(root, revision).get(path) == _tree(root, B).get(path)
                    and raw_bytes(root, revision, path) == raw_bytes(root, B, path),
                    '021 predecessor evidence/catalog mode/blob substitution: ' + path)
    for path in paths:
        require(current_bytes(root, path) == raw_bytes(root, B, path)
                and _git(root, 'show', ':' + path) == raw_bytes(root, B, path),
                '021 live/index predecessor metadata substitution: ' + path)
        _stage_and_live(root, head, path, _tree(root, head)[path])
    _stage_and_live(root, head, QUEUE, _tree(root, head)[QUEUE])
    for raw in (current_bytes(root, QUEUE), _git(root, 'show', ':' + QUEUE)):
        for order in orders:
            row = stateutil.state_from(raw, order)
            require(row['status'] == 'DONE' and row['hardware_result'] == 'PASS'
                    and row['hardware_evidence_gaps'] == []
                    and stateutil.same_acceptance(row, item(root, B, order)),
                    '021 live/index predecessor acceptance substitution: ' + order)


def _current_integrity(root: Path, head: str, expected: dict):
    """Check every critical byte and finite dirty host, including ignored inputs."""
    require(critical_tree(root, head) == expected, '021 current critical tree substitution')
    index = {}
    for record in filter(None, _git(root, 'ls-files', '--stage', '-z').decode().split('\0')):
        meta, path = record.split('\t'); mode, blob, stage = meta.split()
        if path in expected:
            require(stage == '0', '021 unmerged critical input: ' + path)
            index[path] = (mode, 'blob', blob)
    require(index == expected, '021 critical index differs from committed tree')
    tags = {r[2:]: r[0] for r in filter(None, _git(root, 'ls-files', '-v', '-z').decode().split('\0'))}
    for path, entry in expected.items():
        require(path in tags and not tags[path].islower() and tags[path] != 'S',
                '021 critical index flag trap: ' + path)
        file = root / path
        require(file.is_file() and not file.is_symlink()
                and all(not p.is_symlink() for p in file.parents if p != root.parent),
                '021 critical missing/symlink input: ' + path)
        mode = '100755' if file.stat().st_mode & 0o111 else '100644'
        data = file.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require((mode, 'blob', blob) == entry, '021 critical live mode/bytes substitution: ' + path)
    ignored = set(filter(None, _git(root, 'ls-files', '--others', '--ignored',
                                    '--exclude-standard', '-z').decode().split('\0')))
    dirty = set()
    for args in (('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z'),
                 ('ls-files', '--others', '--exclude-standard', '-z'),
                 ('ls-files', '--others', '--ignored', '--exclude-standard', '-z')):
        dirty.update(filter(None, _git(root, *args).decode().split('\0')))
    permitted_cache = set()
    for path in dirty:
        try: category = classify_path(path)
        except CorrespondenceError: category = 'UNKNOWN'
        require(category != 'CRITICAL', '021 dirty critical input: ' + path)
        cache = (any(path == prefix or path.startswith(prefix + '/') for prefix in IGNORED_ALLOWED_ROOTS)
                 or (path.startswith('tools/__pycache__/') and path.endswith('.pyc')))
        if path in ignored and cache:
            permitted_cache.add(path)
        else:
            require(path in GOVERNANCE_PATHS, '021 dirty path outside finite governance: ' + path)
            if (root / path).exists():
                current_bytes(root, path)
    return dirty - permitted_cache


def _catalog(raw: bytes):
    value = json.loads(raw, object_pairs_hook=unique)
    require(set(value) == {'schema_version', 'accepted_transitions'} and
            type(value['schema_version']) is int and value['schema_version'] == 1 and
            type(value['accepted_transitions']) is list and
            len(value['accepted_transitions']) <= 1, '021 catalog fields/count substitution')
    fields = {'work_order', 'candidate', 'build', 'parent', 'tree',
              'review_commit', 'evidence_commit', 'integration'}
    for record in value['accepted_transitions']:
        require(type(record) is dict and set(record) == fields and record['work_order'] == 'GP-CONFIG-021'
                and record['candidate'] == C and
                all(re.fullmatch('[0-9a-f]{40}', record[k]) for k in fields - {'work_order'}),
                '021 catalog record substitution')
    return value['accepted_transitions']


def _reviewed_build(root: Path, state: dict, before: dict, after: dict,
                    protocol: bytes):
    F = state['candidate_git_sha']; parent = state['candidate_base_configurator_sha']
    require(isinstance(parent, str) and re.fullmatch('[0-9a-f]{40}', parent),
            '021 build parent identity invalid')
    composition = _git(root, 'rev-list', '--parents', '-n', '1', parent).decode().split()
    require(len(composition) == 3 and composition[0] == parent and composition[2] == C,
            '021 build parent is not exact [038 DONE,C021] composition merge')
    governance = composition[1]
    require(ancestor(root, READY, governance), '021 composition omitted 038 READY ancestry')
    from check_glyph_agent_framework_docs import validate_completion_evidence
    done_seen = False
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', READY + '..' + governance).decode().split():
        row = item(root, revision, 'GP-VAL-038')
        if row['status'] == 'DONE':
            payload = stateutil.parsed_queue(raw_bytes(root, revision, QUEUE))
            validate_completion_evidence(row, row['done_evidence'],
                policy=payload['completion_correspondence'],
                publication_sha=revision, repo_root=root)
            require(row['hardware_result'] is None
                    and row['canonical_build'] == 'NOT_REQUIRED: source-free H1 governance/characterization; stop on firmware/build change.'
                    and critical_tree(root, revision) == before,
                    '021 038 DONE lacks source-free completion correspondence')
            done_seen = True
        elif done_seen:
            require(False, '021 038 DONE downgraded before build')
        require(critical_tree(root, revision) == before,
                '021 candidate source entered canonical before reviewed F')
    require(done_seen and item(root, governance, 'GP-VAL-038')['status'] == 'DONE'
            and _catalog(raw_bytes(root, governance, TRANSITIONS)) == []
            and critical_tree(root, governance) == before,
            '021 build parent lacks latched strict038 DONE snapshot')
    dt, mt = _tree(root, governance), _tree(root, parent)
    require({path for path in dt.keys() | mt.keys() if dt.get(path) != mt.get(path)} == CRITICAL
            and all(mt[p] == after[p] for p in CRITICAL)
            and _git(root, 'rev-parse', parent + '^{tree}').decode().strip() ==
                _git(root, 'rev-parse', F + '^{tree}').decode().strip(),
            '021 composition changed input outside sole HAL source or F rebuilt tree')
    require(all(isinstance(x, str) and re.fullmatch('[0-9a-f]{40}', x) for x in (F, parent))
            and _git(root, 'rev-list', '--parents', '-n', '1', F).decode().split() == [F, parent]
            and ancestor(root, C, F) and ancestor(root, READY, F)
            and critical_tree(root, parent) == after
            and critical_tree(root, F) == after,
            '021 build F lacks candidate/strict038 DONE/source-free parent')
    verify_correspondence(root, C, B, target=F, integrated=True, check_worktree=False)
    digest = state['firmware_artifact_sha256']
    tree = _git(root, 'rev-parse', F + '^{tree}').decode().strip()
    locator = f'local_backups/hardware-artifacts/{F}/{digest}/firmware.uf2'
    require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest)
            and state['preserved_firmware_artifact_locator'] == locator
            and state['firmware_artifact_build_path'] == '.pio/build/glyph_mk6/firmware.uf2'
            and state['manual_acceptance_protocol_reference'] == PROTOCOL
            and state['manual_acceptance_protocol_version'] == 'GP_CONFIG_021_HW_V1',
            '021 artifact/protocol identity mismatch')
    original.validate_build_review(protocol.decode(),
        {'build': F, 'parent': parent, 'tree': tree}, digest, locator)
    return F, parent, tree



ROOTS |= frozenset(('0da68bdab9bf0fed4ed595538bea9aba7d2f49f3', '1a4b9311c8f7ae6d7cbf0a8680cd976499112f03', '328c6a1bfb09eb035c2065d0de080283307f34d6', '3dac79dac4eefcf832510817e8cb5ecd6a27f219', '478f438804275f3e0c23e6f36bfd26e34aa343bf', '5994f1657e45e0883c6c75468a19be7e3b49a72c', '7a2dba85332c90fa2bcc6c06e1205c4745facb92', '7db4f447d5e796367071b7143fa6c9274c70ae5e', '8b8e45b17a5670bbf983360faf87bdf9d6b50ce2', 'a170bd40a51741582913324bfecbc14ce9b3211d', 'a3664be5354ec4253122eb2e738e70e5dfdb9ccc', 'a6b7750e271324972c51915563fe0dc22f941f95', 'c6887115f2e44f0803eb0956ebb574633cec53be', 'd2f78cd3a3fa38c60d04dab54236ee630ead379e', 'd9ad6132ca0912398839673cc0da24e54a924210', 'e5c455637056ac535347c1176dd41c9a9d84d85a', 'fe84db39f2fcdd369d0ae26c1cbb80fd5a15d15d'))

CONSUMER_FIXTURE = 'docs/runtime_config/fixtures/gp_val038_c021_consumer_replay.json'
CONSUMER_FIXTURE_SHA256 = '6724b99d5bb66f086a91fc7676fc08aa6488015783bbc134deaf8a8776a6cf31'
CONSUMER_WRAPPER = 'tools/check_glyph_c021_proof_replay.py'
CONSUMER_WRAPPER_SHA256 = '45c1fe911100b73b1fb4dd91b1bb28bad5547d2139c25606cc4aee768990ca53'


def _consumer_contract(root: Path, head: str):
    """Require actual new replay inputs and all immutable original bodies."""
    raw = current_bytes(root, CONSUMER_FIXTURE)
    require(sha(raw) == CONSUMER_FIXTURE_SHA256
            and sha(current_bytes(root, CONSUMER_WRAPPER)) == CONSUMER_WRAPPER_SHA256,
            '021 consumer replay fixture/wrapper substitution')
    for path in CONSUMER_PATHS:
        _stage_and_live(root, head, path, _tree(root, head)[path])
    from check_glyph_c021_proof_replay import verify_fixture
    return verify_fixture(root)


def _preserve_original_current_inputs(root: Path, head: str):
    baseline = _tree(root, B)
    actual = _tree(root, head)
    frozen = (previous.GOVERNANCE_PATHS | stateutil.KBD_HOSTS |
              stateutil.CONFIG019_HOSTS | frozenset((previous.HISTORICAL_WRAPPER,
              'docs/agent_framework/PORTFOLIO_20261005_0028_CURATOR.md'))) - SHARED_CURRENT_PATHS
    baseline_manifest = json.loads(raw_bytes(root, B,
        'docs/runtime_config/fixtures/runtime_config_validation_manifest.json'), object_pairs_hook=unique)
    baseline_critical = critical_tree(root, B)
    for row in baseline_manifest['entries']:
        if row['id'] in REPLAY_LANES:
            frozen |= frozenset(p for p in (row['path'], *row['source_dependencies'])
                                if p not in SHARED_CURRENT_PATHS and p not in baseline_critical)
    for path in sorted(frozen):
        if path not in baseline:
            require(path not in actual and not (root / path).exists(),
                    '021 adds unreviewed historical host literal: ' + path)
            continue
        require(actual.get(path) == baseline[path], '021 original current host mode/blob substitution: ' + path)
        _stage_and_live(root, head, path, baseline[path])


def _manifest_contract(root: Path, head: str):
    path = 'docs/runtime_config/fixtures/runtime_config_validation_manifest.json'
    _stage_and_live(root, head, path, _tree(root, head)[path])
    current = json.loads(current_bytes(root, path), object_pairs_hook=unique)
    baseline = json.loads(raw_bytes(root, B, path), object_pairs_hook=unique)
    old = {e['id']: e for e in baseline['entries']}
    rows = {e['id']: e for e in current['entries']}
    lanes = REPLAY_LANES
    require(len(rows) == len(current['entries']) and set(rows) == set(old) |
            {'gp_config021_persisted_recovery', 'gp_val038_c021_transition'},
            '021 manifest deletion/duplicate/unknown lane')
    original_paths = frozenset(old[key]['path'] for key in REPLAY_LANES)
    permitted_deps = HOSTS | NEW_PATHS | CONSUMER_PATHS | original_paths | frozenset((
        'tools/glyph_campaign_transition.py', 'tools/glyph_tracked_worktree_integrity.py',
        'tools/glyph_hardware_correspondence.py'))
    for identity, prior in old.items():
        row = rows[identity]
        old_deps = frozenset(prior['source_dependencies'])
        expected = dict(prior, source_dependencies=row['source_dependencies'])
        require(old_deps <= frozenset(row['source_dependencies']) <= old_deps | permitted_deps,
                '021 manifest dependency removal/unknown addition: ' + identity)
        if identity in lanes:
            expected.update(path=CONSUMER_WRAPPER,
                command=['python3', CONSUMER_WRAPPER, '--consumer', lanes[identity]],
                required_arguments=['--consumer', lanes[identity]], mutation_risk='temporary_file_only',
                reason=row['reason'])
            require(row['load_bearing'] is True and row['historical'] is False
                    and row['applicability'] == 'current', '021 original proof demoted: ' + identity)
        require(row == expected, '021 original manifest lane changed outside replay admission: ' + identity)
    for identity, command in (
        ('gp_config021_persisted_recovery', ['python3', CONSUMER_WRAPPER]),
        ('gp_val038_c021_transition', ['python3', 'tools/test_glyph_c021_campaign_transition.py'])):
        row = rows[identity]
        require(row['command'] == command and row['path'] == command[1]
                and row['required_arguments'] == [] and row['load_bearing'] is True
                and row['historical'] is False and row['applicability'] == 'current'
                and row['category'] == 'candidate_safety'
                and row['branch_policy'] == 'content_and_scope'
                and row['mutation_risk'] == 'temporary_file_only'
                and type(row['load_bearing']) is bool and type(row['historical']) is bool
                and len(row['source_dependencies']) == len(set(row['source_dependencies']))
                and frozenset(row['source_dependencies']) == frozenset(REQUIRED_NEW_DEPENDENCIES[identity]),
                '021 required current proof omitted/substituted: ' + identity)
    require(current['strong_signal_exclusions'] == baseline['strong_signal_exclusions'], '021 excludes existing load-bearing proof')


@original._proof_invocation
def replay_covered_checker_paths(root: Path) -> frozenset[str]:
    """Only immutable originals actually served by the exact current replay lanes."""
    root = Path(root).resolve(); head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    source_contract(root)
    _preserve_original_current_inputs(root, head)
    fixture = _consumer_contract(root, head)
    _manifest_contract(root, head)
    paths = frozenset(row['original_path'] for row in fixture['consumer_lanes'].values())
    require(len(fixture['consumer_lanes']) == 14 and all(
            (path.startswith('tools/check_glyph_') and path.endswith('.py'))
            or path == 'tools/test_glyph_c017_campaign_transition.py' for path in paths), '021 replay coverage shape substitution')
    for path in paths:
        require(_tree(root, head).get(path) == _tree(root, B).get(path),
                '021 served original checker substitution: ' + path)
        _stage_and_live(root, head, path, _tree(root, B)[path])
    require(_tree(root, head).get(CHECKER) == _tree(root, C).get(CHECKER), '021 served original engine substitution')
    _stage_and_live(root, head, CHECKER, _tree(root, C)[CHECKER])
    return (paths - frozenset(('tools/test_glyph_c017_campaign_transition.py',))) | frozenset((CHECKER,))


@original._proof_invocation
def authenticate(root: Path):
    root = Path(root).resolve()
    head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    before, after = source_contract(root)
    predecessor, old_accepted = predecessor_contract(root)
    _preserve_accepted_predecessors(root, head)
    _preserve_original_current_inputs(root, head)
    current = critical_tree(root, head)
    require(current in (before, after), '021 current source outside B/C critical trees')
    dirty = _current_integrity(root, head, current)
    delta = set(filter(None, _git(root, 'diff', '--no-renames', '--name-only', '-z', B, head).decode().split('\0')))
    require(delta | dirty <= GOVERNANCE_PATHS | CRITICAL, '021 unknown governance/source delta')
    tree = _tree(root, head)
    for path in delta:
        require(tree.get(path, ())[:2] == ('100644', 'blob'), '021 deleted/nonregular changed path: ' + path)
        require(classify_path(path) != 'CRITICAL' or path in CRITICAL,
                '021 governance exemption attempted critical path: ' + path)
    for path in HOSTS:
        require(tree.get(path) == _tree(root, C)[path], '021 candidate host missing/substituted: ' + path)
        _stage_and_live(root, head, path, tree[path])
    for path in original.FROZEN:
        require(current_bytes(root, path) == raw_bytes(root, B, path), '021 historical fixture substitution: ' + path)
        _stage_and_live(root, head, path, tree[path])
    for path in (MAPPING, TRANSITIONS):
        _stage_and_live(root, head, path, tree[path])
    _consumer_contract(root, head)
    _manifest_contract(root, head)
    lifecycle = _lifecycle(root, head, before, after)
    lifecycle['changed_paths'] = frozenset(delta | dirty)
    lifecycle['object_roots'] |= predecessor['object_roots']
    return lifecycle


@original._proof_invocation
def _lifecycle(root: Path, head: str, before: dict, after: dict):
    """Native021 phase graph, after full admission in public authenticate.

    Tests reuse this actual bounded phase gate on private synthetic graphs.
    Production always verifies original predecessor/source/host custody first.
    """
    root = Path(root).resolve()
    require(_git(root, 'rev-parse', 'HEAD').decode().strip() == head,
            '021 phase graph HEAD substitution')
    current = critical_tree(root, head)
    require(current in (before, after), '021 phase source outside B/C critical trees')
    _current_integrity(root, head, current)
    tree = _tree(root, head)
    records = _catalog(current_bytes(root, TRANSITIONS))
    state = item(root, head, 'GP-CONFIG-021')
    pending_build = None
    if PROTOCOL in tree:
        require(state['status'] in {'REVIEW', 'HARDWARE_TEST_REQUIRED', 'HARDWARE_VALIDATED', 'DONE'},
                '021 protocol appears outside reviewed hardware phase')
        _stage_and_live(root, head, PROTOCOL, tree[PROTOCOL])
        pending_build = _reviewed_build(root, state, before, after, current_bytes(root, PROTOCOL))
    elif state['status'] in {'HARDWARE_TEST_REQUIRED', 'HARDWARE_VALIDATED', 'DONE'}:
        require(False, '021 hardware snapshot lacks exact reviewed protocol/build')
    _stage_and_live(root, head, QUEUE, tree[QUEUE])
    for raw in (current_bytes(root, QUEUE), _git(root, 'show', ':' + QUEUE)):
        require(stateutil.state_from(raw, 'GP-CONFIG-021') == state, '021 live/index queue substitution')
    require(state['status'] != 'HARDWARE_FAILED' and state['hardware_result'] != 'FAIL', 'failed021 cannot validate')
    phase = 'BASELINE'
    protected = stateutil.predecessor.CRITICAL | stateutil.CRITICAL | previous.CRITICAL
    source_candidates = {p: stateutil.predecessor.C_R for p in stateutil.predecessor.CRITICAL}
    source_candidates.update({p: stateutil.C for p in stateutil.CRITICAL})
    source_candidates.update({p: previous.C for p in previous.CRITICAL})
    if current == after:
        require(ancestor(root, C, head), '021 source replay without preserved C ancestry')
        phase = 'CANDIDATE_VALIDATION_ONLY'
        protected |= CRITICAL
        source_candidates.update({p: C for p in CRITICAL})
    elif ancestor(root, C, head):
        require(False, '021 candidate ancestry with original source')
    processor = None
    first_catalog = None
    done = False
    # Scan immutable queue history for the first real processor transition.
    # C, M and F are side-branch ancestors of the final integration but are not
    # descendants of E. Their pending rows must remain pending; only actual
    # descendants of E inherit its latched PASS, catalog and DONE obligations.
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', READY + '..' + head).decode().split():
        row = item(root, revision, 'GP-CONFIG-021')
        introduced = (_catalog(raw_bytes(root, revision, TRANSITIONS))
                      if TRANSITIONS in _tree(root, revision) else [])
        if processor is not None and not ancestor(root, processor['evidence_commit'], revision):
            require(row['hardware_result'] is None
                    and row['status'] not in {'HARDWARE_VALIDATED', 'DONE'}
                    and not introduced,
                    '021 competing PASS/catalog/DONE outside first E ancestry')
            continue
        if row['hardware_result'] == 'PASS' or row['status'] in {'HARDWARE_VALIDATED', 'DONE'}:
            require(row['hardware_result'] == 'PASS' and
                    row['status'] in {'HARDWARE_VALIDATED', 'DONE'} and
                    row['hardware_evidence_gaps'] == [] and
                    row['hardware_evidence_dependency_satisfied'] is True,
                    '021 PASS in invalid native status')
            if processor is None:
                require(row['status'] == 'HARDWARE_VALIDATED' and
                        critical_tree(root, revision) == before and
                        not ancestor(root, C, revision),
                        '021 first processor PASS must be source-free E')
                processor = _processor(root, revision, row, before, after)
            else:
                require(stateutil.same_acceptance(row, processor['native']),
                        '021 processor acceptance downgraded/replaced')
            require(not done or row['status'] == 'DONE',
                    '021 DONE status downgraded')
        elif processor is not None:
            require(False, '021 processor PASS erased/downgraded')
        if processor is not None:
            for path, key in ((PROTOCOL, 'protocol'), (EVIDENCE, 'payload'),
                              (RESULT, 'result')):
                require(_tree(root, revision).get(path, ())[:2] == ('100644', 'blob')
                        and raw_bytes(root, revision, path) == processor[key],
                        '021 accepted evidence/protocol/result erased/replaced: ' + path)
        if introduced:
            require(processor is not None and len(introduced) == 1,
                    '021 catalog precedes processor')
            if first_catalog is None:
                first_catalog = introduced[0]
            require(introduced == [first_catalog],
                    '021 accepted catalog replaced')
            _accepted(root, revision, first_catalog, processor, after)
        elif first_catalog is not None:
            require(False, '021 accepted catalog removed')
        if row['status'] == 'DONE':
            require(introduced, '021 DONE before accepted catalog')
            from check_glyph_agent_framework_docs import validate_completion_evidence
            queue_payload = stateutil.parsed_queue(raw_bytes(root, revision, QUEUE))
            validate_completion_evidence(row, row['done_evidence'],
                policy=queue_payload['completion_correspondence'],
                publication_sha=revision, repo_root=root)
            done = True
    require((state['hardware_result'] == 'PASS' or state['status'] in {'HARDWARE_VALIDATED', 'DONE'})
            == (processor is not None), '021 current processor status/history mismatch')
    if processor:
        require(stateutil.same_acceptance(state, processor['native']),
                '021 current acceptance tuple differs from first E')
        for path in (PROTOCOL, EVIDENCE, RESULT):
            require(current_bytes(root, path) == raw_bytes(root, head, path)
                    and _git(root, 'show', ':' + path) == current_bytes(root, path)
                    and raw_bytes(root, head, path) == processor[
                        {PROTOCOL: 'protocol', EVIDENCE: 'payload', RESULT: 'result'}[path]],
                    '021 accepted evidence/protocol/result live/index substitution: ' + path)
            _stage_and_live(root, head, path, tree[path])
        if current == before:
            require(not records and first_catalog is None,
                    'source-free021 processor has accepted catalog')
            phase = 'SOURCE_FREE_PROCESSOR'
        else:
            require(len(records) == 1 and records[0] == first_catalog,
                    'integrated021 PASS lacks first accepted catalog')
            _accepted(root, head, records[0], processor, after)
            phase = 'ACCEPTED_TRANSITION'
    else:
        require(not records, '021 accepted catalog without HEP PASS')
    metadata = frozenset(p for helper in (stateutil.predecessor, stateutil, previous)
                         for p in (helper.PROTOCOL, helper.EVIDENCE, helper.RESULT))
    if processor: metadata |= frozenset((PROTOCOL, EVIDENCE, RESULT))
    roots = set(ROOTS)
    if pending_build: roots.update(pending_build[:2])
    if processor: roots |= {processor[k] for k in ('build', 'parent', 'review_commit', 'evidence_commit', 'evidence_root')}
    if records: roots.add(records[0]['integration'])
    require(_git(root, 'rev-parse', 'HEAD').decode().strip() == head, '021 HEAD changed during authentication')
    return {'phase': phase, 'contract': 'c021_persisted_recovery', 'candidate': C, 'base': B,
            'predecessor_phase': 'ACCEPTED_TRANSITION', 'target': head,
            'critical_paths': protected, 'accepted_metadata_paths': metadata,
            'object_roots': frozenset(roots),
            'source_candidates': source_candidates, 'host_overlay_paths': CONSUMER_PATHS,
            'kbd_host_paths': stateutil.KBD_HOSTS, 'config019_host_paths': stateutil.CONFIG019_HOSTS,
            'evidence_commit': processor['evidence_commit'] if processor else None}


def _processor(root: Path, head: str, state: dict, before: dict, after: dict):
    """Validate actual future E; this path is unreachable from candidate fixtures."""
    F, parent, tree = _reviewed_build(root, state, before, after,
                                      raw_bytes(root, head, PROTOCOL))
    require(not ancestor(root, F, head) and critical_tree(root, head) == before,
            '021 processor E must be source-free')
    reference = state['hardware_evidence_record']
    if reference == 'repo-json:' + EVIDENCE:
        evidence_root = head
    else:
        match = re.fullmatch('git-json:([0-9a-f]{40}):' + re.escape(EVIDENCE), str(reference))
        require(match is not None, '021 evidence lacks immutable Git root')
        evidence_root = match.group(1)
    require(ancestor(root, evidence_root, head), '021 evidence root after E')
    payload = raw_bytes(root, evidence_root, EVIDENCE)
    from check_glyph_agent_framework_docs import validate_work_order, validate_evidence_record
    validated = dict(state, hardware_evidence_record=
        'git-json:' + evidence_root + ':' + EVIDENCE)
    validate_work_order(validated, evidence_repo_root=root)
    validate_evidence_record(validated, evidence_repo_root=root)
    evidence = json.loads(payload, object_pairs_hook=unique)
    rows = {row['id']: row for row in evidence['steps']}
    require(evidence['anomalies'] == evidence['evidence_gaps'] == []
            and len(rows) == len(evidence['steps'])
            and all(row in rows and rows[row]['observed'].strip().startswith('PASS')
                    for row in REQUIRED_ROWS),
            '021 required physical row missing/failing or evidence gaps')
    protocol = raw_bytes(root, head, PROTOCOL)
    require(all(token in protocol.decode() for token in
                REQUIRED_ROWS),
            '021 reviewed protocol omitted required physical row')
    review = None
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', READY + '..' + head).decode().split():
        row = item(root, revision, 'GP-CONFIG-021')
        if row['status'] in {'REVIEW', 'HARDWARE_TEST_REQUIRED'} and row['hardware_result'] is None:
            if all(row[k] == state[k] for k in stateutil.IDENTITIES) and PROTOCOL in _tree(root, revision):
                require(_tree(root, revision).get(PROTOCOL, ())[:2] == ('100644', 'blob'),
                        '021 earliest reviewed R protocol mode substitution')
                _reviewed_build(root, row, before, after, raw_bytes(root, revision, PROTOCOL))
                review = revision; break
    require(review is not None and ancestor(root, review, evidence_root)
            and ancestor(root, review, head) and not ancestor(root, F, review)
            and critical_tree(root, review) == before
            and raw_bytes(root, review, PROTOCOL) == raw_bytes(root, head, PROTOCOL),
            '021 missing reviewed source-free R/protocol')
    return {'build': F, 'parent': parent, 'tree': tree,
            'review_commit': review, 'evidence_commit': head, 'evidence_root': evidence_root,
            'payload': payload, 'protocol': raw_bytes(root, review, PROTOCOL),
            'result': raw_bytes(root, head, RESULT), 'native': state}


def _accepted(root: Path, head: str, record: dict, processor: dict, after: dict):
    require(all(record[k] == processor[k] for k in ('build', 'parent', 'tree',
                                                    'review_commit', 'evidence_commit'))
            and ancestor(root, processor['evidence_commit'], record['integration'])
            and ancestor(root, processor['build'], record['integration'])
            and ancestor(root, record['integration'], head)
            and critical_tree(root, record['integration']) == after,
            '021 accepted catalog chronology/source mismatch')
    verify_correspondence(root, processor['build'], processor['parent'],
                          target=head, integrated=True, check_worktree=False)



def verify_current_source(root: Path, path: str, historical_sha256: str | None = None):
    root = Path(root).resolve()
    old = raw_bytes(root, original.B, path)
    if historical_sha256 is not None:
        require(sha(old) == historical_sha256, '021 historical source identity mismatch: ' + path)
    current = current_bytes(root, path)
    if current != old:
        proof = authenticate(root)
        owner = proof['source_candidates'].get(path)
        require(owner is not None and current == raw_bytes(root, owner, path),
                'unadopted021 current source overlay: ' + path)
    return old
