#!/usr/bin/env python3
"""C022 finite actual-source RGB host proof. No device interaction or hardware claim."""
from __future__ import annotations
import argparse, base64, concurrent.futures, hashlib, importlib.util, json, os, re, shutil, stat, subprocess, sys, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='14400b3ff75b5d017a9e7cf8e6d8be785c342187'
HOST='tools/fixtures/gp_config022_rgb_target_validation'
FIXTURE='docs/runtime_config/fixtures/gp_config022_rgb_target_validation.json'
CHECKER='tools/check_glyph_gp_config022_rgb_target_validation.py'
RGB_UNITS=['src/core/config_rgb_target_validation.cpp','config/glyph/common/src/glyph_config_validation.cpp']
SOURCE_PATHS=['include/core/config_rgb_target_validation.hpp',RGB_UNITS[0],'config/glyph/common/include/config_rgb_target_domain.hpp','config/glyph/common/include/glyph_config_validation.hpp',RGB_UNITS[1],'config/glyph/common/src/config.cpp','config/glyph/common/include/glyph_overrides.hpp']
class ContractError(AssertionError):pass
def require(v,m):
 if not v:raise ContractError(m)
def digest(b):return hashlib.sha256(b).hexdigest()
def regular(root,p):
 require(type(p) is str and p and not Path(p).is_absolute() and '..' not in Path(p).parts,'unsafe input path');root=Path(root).resolve();path=root/p
 for part in [path,*list(path.parents)[:len(Path(p).parts)-1]]:require(not part.is_symlink(),'symlink input '+p)
 require(path.is_file(),'nonregular input '+p);return path.read_bytes()
def load_base(root):
 s=importlib.util.spec_from_file_location('c022_c021_infrastructure',Path(root)/'tools/check_glyph_gp_config021_persisted_recovery.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b);return b

APP_UNITS=['config/glyph/common/src/config.cpp', 'HAL/pico/src/core/Persistence.cpp', 'src/core/config_validation.cpp', 'src/core/config_button_validation.cpp', 'src/core/CommunicationBackend.cpp', 'src/core/InputSource.cpp', 'src/core/mode_selection.cpp', 'HAL/pico/src/comms/backend_init.cpp', 'src/comms/IntegratedDisplay.cpp', 'config/glyph/common/src/display/AboutMenu.cpp', 'config/glyph/common/src/display/GlyphConfigMenu.cpp', 'config/glyph/common/src/display/MenuButtonHints.cpp', 'config/glyph/common/src/display/OopsieMenu.cpp', 'HAL/pico/src/display/RemapMenu.cpp', 'HAL/pico/src/display/InputDisplay.cpp', 'HAL/pico/src/display/RgbBrightnessMenu.cpp', 'HAL/pico/src/display/ConfigMenu.cpp', 'HAL/pico/src/display/DefaultConfigMenu.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.cpp', 'tools/fixtures/gp_config022_rgb_target_validation/startup_harness.cpp', 'src/core/InputMode.cpp', 'src/core/ControllerMode.cpp', 'src/core/config_utils.cpp', 'src/core/socd.cpp', 'HAL/pico/src/core/KeyboardMode.cpp', 'HAL/pico/src/gpio.cpp', 'HAL/pico/src/reboot.cpp', 'HAL/pico/src/serial.cpp', 'HAL/pico/src/comms/console_detection.cpp', 'HAL/pico/src/comms/ConfiguratorBackend.cpp', 'HAL/pico/src/comms/GamecubeBackend.cpp', 'HAL/pico/src/comms/N64Backend.cpp', 'HAL/pico/src/comms/NesBackend.cpp', 'HAL/pico/src/comms/SnesBackend.cpp', 'HAL/pico/src/comms/XInputBackend.cpp', 'HAL/pico/src/comms/DInputBackend.cpp', 'HAL/pico/src/comms/NintendoSwitchBackend.cpp', 'src/comms/B0XXInputViewer.cpp', 'lib/TUCompositeHID/src/TUCompositeHID.cpp', 'lib/TUCompositeHID/src/TUGamepad.cpp', 'lib/TUCompositeHID/src/TUKeyboard.cpp', 'config/glyph/common/src/LEDTemplates.cpp', 'HAL/pico/src/rgb/ButtonLocations.cpp', 'src/modes/Ultimate.cpp', 'src/modes/Melee20Button.cpp', 'src/modes/ProjectM.cpp', 'src/modes/RivalsOfAether.cpp', 'src/modes/Rivals2.cpp', 'src/modes/FgcMode.cpp', 'src/modes/64.cpp', 'src/modes/SenscopePrototype.cpp', 'src/modes/CustomKeyboardMode.cpp', 'src/modes/CustomControllerMode.cpp', 'tools/fixtures/gp_config021_persisted_recovery/platform_doubles.cpp', 'src/prototypes/senscope/SenscopePrototypeModifier.cpp', 'src/prototypes/senscope/SenscopePrototypeSelfTest.cpp', 'src/prototypes/senscope/SenscopePrototypeDigital.cpp', 'src/prototypes/senscope/SenscopePrototypeForce.cpp', 'src/prototypes/senscope/SenscopePrototypeResolver.cpp', 'src/prototypes/senscope/SenscopePrototypeValidation.cpp', 'src/prototypes/senscope/SenscopePrototypeOutput.cpp', 'src/prototypes/senscope/SenscopePrototypeDirection.cpp', 'src/core/config_rgb_target_validation.cpp', 'config/glyph/common/src/glyph_config_validation.cpp']

C_UNITS=['tools/fixtures/gp_config012_button_host/nanopb/pb_common.c', 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.c', 'tools/fixtures/gp_config012_button_host/generated/config.pb.c']
GENERAL_UNITS=['src/core/config_validation.cpp', 'src/core/config_button_validation.cpp', 'HAL/pico/src/core/Persistence.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.cpp', 'src/core/CommunicationBackend.cpp', 'HAL/pico/src/comms/ConfiguratorBackend.cpp', 'src/core/config_rgb_target_validation.cpp', 'config/glyph/common/src/glyph_config_validation.cpp', 'tools/fixtures/gp_config020_button_validation/abi_probe.cpp', 'src/core/InputMode.cpp', 'src/core/socd.cpp', 'HAL/pico/src/rgb/ButtonLocations.cpp']
INCLUDES=['tools/fixtures/gp_config021_persisted_recovery', 'tools/fixtures/gp_config021_persisted_recovery/include', 'tools/fixtures/gp_config021_persisted_recovery/dependencies', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes', 'tools/fixtures/gp_config012_button_host/generated', 'tools/fixtures/gp_config012_button_host/nanopb', 'include', 'HAL/pico/include', 'config/glyph/common/include', 'config/glyph/glyph_mk6/include', 'lib/TUCompositeHID/include', 'src', '.']

STARTUP_CASES=[(k,s,d)for k in ('normal','configurator','rejected','rgb_rejected','rgb_nonphysical','rgb_unnamed','rgb_legacy')for s in ('early','during','late')for d in ('display','failed')]+[(k,s,d)for k in ('missing','open','defaults','rgb_defaults','mount','config')for s in ('early','late')for d in ('display','failed')]+[('mb1','late','display'),('mb1','late','failed')]
SUITES=('validation','decoder','persistence','setconfig','consumer')
EXPECTED_CASES={'short': {'validation': 534, 'decoder': 538, 'persistence': 827, 'setconfig': 1139}, 'ordinary': {'validation': 539, 'decoder': 538, 'persistence': 827, 'setconfig': 1139}}
EXPLICIT_INPUTS=['tools/glyph_tracked_worktree_integrity.py', 'tools/check_glyph_gp_config022_rgb_target_validation.py', 'tools/check_glyph_gp_config021_persisted_recovery.py', 'docs/runtime_config/gp_config022_rgb_target_validation.md', 'docs/calibration/gp_config_021_hardware_result.md', 'tools/fixtures/gp_config012_button_host/schema/config.proto']
PIN_PATHS=['tools/glyph_tracked_worktree_integrity.py', 'HAL/pico/include/comms/ConfiguratorBackend.hpp', 'HAL/pico/include/comms/DInputBackend.hpp', 'HAL/pico/include/comms/GamecubeBackend.hpp', 'HAL/pico/include/comms/N64Backend.hpp', 'HAL/pico/include/comms/NeoPixelBackend.hpp', 'HAL/pico/include/comms/NesBackend.hpp', 'HAL/pico/include/comms/NintendoSwitchBackend.hpp', 'HAL/pico/include/comms/SnesBackend.hpp', 'HAL/pico/include/comms/XInputBackend.hpp', 'HAL/pico/include/core/KeyboardMode.hpp', 'HAL/pico/include/core/Persistence.hpp', 'HAL/pico/include/display/ConfigMenu.hpp', 'HAL/pico/include/display/ConfigMenuAssets/GlyphMenuBitmaps.h', 'HAL/pico/include/display/DefaultConfigMenu.hpp', 'HAL/pico/include/display/DisplayMode.hpp', 'HAL/pico/include/display/InputDisplay.hpp', 'HAL/pico/include/display/RemapMenu.hpp', 'HAL/pico/include/display/RgbBrightnessMenu.hpp', 'HAL/pico/include/gpio.hpp', 'HAL/pico/include/input/DebouncedSwitchMatrixInput.hpp', 'HAL/pico/include/input/debounce.hpp', 'HAL/pico/include/rgb/ButtonLocations.hpp', 'HAL/pico/include/serial.hpp', 'HAL/pico/include/stdlib.hpp', 'HAL/pico/include/util/state_util.hpp', 'HAL/pico/src/comms/ConfiguratorBackend.cpp', 'HAL/pico/src/comms/DInputBackend.cpp', 'HAL/pico/src/comms/GamecubeBackend.cpp', 'HAL/pico/src/comms/N64Backend.cpp', 'HAL/pico/src/comms/NesBackend.cpp', 'HAL/pico/src/comms/NintendoSwitchBackend.cpp', 'HAL/pico/src/comms/SnesBackend.cpp', 'HAL/pico/src/comms/XInputBackend.cpp', 'HAL/pico/src/comms/backend_init.cpp', 'HAL/pico/src/comms/console_detection.cpp', 'HAL/pico/src/core/KeyboardMode.cpp', 'HAL/pico/src/core/Persistence.cpp', 'HAL/pico/src/display/ConfigMenu.cpp', 'HAL/pico/src/display/DefaultConfigMenu.cpp', 'HAL/pico/src/display/InputDisplay.cpp', 'HAL/pico/src/display/RemapMenu.cpp', 'HAL/pico/src/display/RgbBrightnessMenu.cpp', 'HAL/pico/src/gpio.cpp', 'HAL/pico/src/reboot.cpp', 'HAL/pico/src/rgb/ButtonLocations.cpp', 'HAL/pico/src/serial.cpp', 'config/glyph/common/include/LEDTemplates.hpp', 'config/glyph/common/include/config_rgb_target_domain.hpp', 'config/glyph/common/include/display/AboutMenu.hpp', 'config/glyph/common/include/display/Font4x7Fixed.h', 'config/glyph/common/include/display/GlyphConfigMenu.hpp', 'config/glyph/common/include/display/MenuButtonHints.hpp', 'config/glyph/common/include/display/OopsieMenu.hpp', 'config/glyph/common/include/display/Picopixel.h', 'config/glyph/common/include/glyph_config_validation.hpp', 'config/glyph/common/include/glyph_overrides.hpp', 'config/glyph/common/include/icons/12x12bitmaps.hpp', 'config/glyph/common/include/icons/16x16bitmaps.hpp', 'config/glyph/common/include/icons/menubases.hpp', 'config/glyph/common/include/icons/splashscreen.hpp', 'config/glyph/common/src/LEDTemplates.cpp', 'config/glyph/common/src/config.cpp', 'config/glyph/common/src/display/AboutMenu.cpp', 'config/glyph/common/src/display/GlyphConfigMenu.cpp', 'config/glyph/common/src/display/MenuButtonHints.cpp', 'config/glyph/common/src/display/OopsieMenu.cpp', 'config/glyph/common/src/glyph_config_validation.cpp', 'config/glyph/glyph_mk6/include/button_positions.hpp', 'config/glyph/glyph_mk6/include/glyph_pinout.hpp', 'config/glyph/glyph_mk6/include/matrix_definition.hpp', 'config/glyph/glyph_mk6/include/neopixel_definitions.hpp', 'docs/calibration/gp_config_021_hardware_result.md', 'docs/runtime_config/gp_config022_rgb_target_validation.md', 'include/comms/B0XXInputViewer.hpp', 'include/comms/IntegratedDisplay.hpp', 'include/comms/console_detection.hpp', 'include/core/CommunicationBackend.hpp', 'include/core/ControllerMode.hpp', 'include/core/InputMode.hpp', 'include/core/InputSource.hpp', 'include/core/config_button_validation.hpp', 'include/core/config_rgb_target_validation.hpp', 'include/core/config_utils.hpp', 'include/core/config_validation.hpp', 'include/core/mode_selection.hpp', 'include/core/pinout.hpp', 'include/core/socd.hpp', 'include/core/state.hpp', 'include/img/remap.hpp', 'include/img/update.hpp', 'include/input/SwitchMatrixInput.hpp', 'include/modes/64.hpp', 'include/modes/CustomControllerMode.hpp', 'include/modes/CustomKeyboardMode.hpp', 'include/modes/FgcMode.hpp', 'include/modes/Melee20Button.hpp', 'include/modes/ProjectM.hpp', 'include/modes/Rivals2.hpp', 'include/modes/RivalsOfAether.hpp', 'include/modes/SenscopePrototype.hpp', 'include/modes/Ultimate.hpp', 'include/prototypes/senscope/SenscopePrototypeBuildFlags.hpp', 'include/prototypes/senscope/SenscopePrototypeDigital.hpp', 'include/prototypes/senscope/SenscopePrototypeDirection.hpp', 'include/prototypes/senscope/SenscopePrototypeForce.hpp', 'include/prototypes/senscope/SenscopePrototypeModifier.hpp', 'include/prototypes/senscope/SenscopePrototypeOutput.hpp', 'include/prototypes/senscope/SenscopePrototypeResolver.hpp', 'include/prototypes/senscope/SenscopePrototypeSelfTest.hpp', 'include/prototypes/senscope/SenscopePrototypeTypes.hpp', 'include/reboot.hpp', 'lib/TUCompositeHID/include/TUCompositeHID.hpp', 'lib/TUCompositeHID/include/TUGamepad.hpp', 'lib/TUCompositeHID/include/TUKeyboard.hpp', 'lib/TUCompositeHID/src/TUCompositeHID.cpp', 'lib/TUCompositeHID/src/TUGamepad.cpp', 'lib/TUCompositeHID/src/TUKeyboard.cpp', 'src/comms/B0XXInputViewer.cpp', 'src/comms/IntegratedDisplay.cpp', 'src/core/CommunicationBackend.cpp', 'src/core/ControllerMode.cpp', 'src/core/InputMode.cpp', 'src/core/InputSource.cpp', 'src/core/config_button_validation.cpp', 'src/core/config_rgb_target_validation.cpp', 'src/core/config_utils.cpp', 'src/core/config_validation.cpp', 'src/core/mode_selection.cpp', 'src/core/socd.cpp', 'src/modes/64.cpp', 'src/modes/CustomControllerMode.cpp', 'src/modes/CustomKeyboardMode.cpp', 'src/modes/FgcMode.cpp', 'src/modes/Melee20Button.cpp', 'src/modes/ProjectM.cpp', 'src/modes/Rivals2.cpp', 'src/modes/RivalsOfAether.cpp', 'src/modes/SenscopePrototype.cpp', 'src/modes/Ultimate.cpp', 'src/modes/UltimateIdentityRuntimeTables.hpp', 'src/modes/UltimateRuntimeConfigInterpreter.hpp', 'src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp', 'src/prototypes/senscope/SenscopePrototypeDigital.cpp', 'src/prototypes/senscope/SenscopePrototypeDirection.cpp', 'src/prototypes/senscope/SenscopePrototypeForce.cpp', 'src/prototypes/senscope/SenscopePrototypeModifier.cpp', 'src/prototypes/senscope/SenscopePrototypeOutput.cpp', 'src/prototypes/senscope/SenscopePrototypeResolver.cpp', 'src/prototypes/senscope/SenscopePrototypeSelfTest.cpp', 'src/prototypes/senscope/SenscopePrototypeValidation.cpp', 'tools/check_glyph_gp_config021_persisted_recovery.py', 'tools/check_glyph_gp_config022_rgb_target_validation.py', 'tools/fixtures/gp_config012_button_host/generated/config.pb.c', 'tools/fixtures/gp_config012_button_host/generated/config.pb.h', 'tools/fixtures/gp_config012_button_host/nanopb/pb.h', 'tools/fixtures/gp_config012_button_host/nanopb/pb_common.c', 'tools/fixtures/gp_config012_button_host/nanopb/pb_common.h', 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c', 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.h', 'tools/fixtures/gp_config012_button_host/schema/config.proto', 'tools/fixtures/gp_config017_neopixel_repaired_current/include/FastLED.h', 'tools/fixtures/gp_config020_button_validation/abi_probe.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/GamecubeConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/N64Console.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/gamecube_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/joybus.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/n64_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/NesConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/SnesConsole.hpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/nes.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/nes_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/snes_definitions.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.cpp', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_arduino.h', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.c', 'tools/fixtures/gp_config021_persisted_recovery/dependencies/pb_encode.h', 'tools/fixtures/gp_config021_persisted_recovery/host_observation.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_GFX.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_SSD1306.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_TinyUSB.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Adafruit_USBD_XInput.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/Arduino.h', 'tools/fixtures/gp_config021_persisted_recovery/include/FastLED.h', 'tools/fixtures/gp_config021_persisted_recovery/include/LittleFS.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Print.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Stream.h', 'tools/fixtures/gp_config021_persisted_recovery/include/Wire.h', 'tools/fixtures/gp_config021_persisted_recovery/include/arduino/Adafruit_USBD_Device.h', 'tools/fixtures/gp_config021_persisted_recovery/include/cobs/Print.h', 'tools/fixtures/gp_config021_persisted_recovery/include/cobs/Stream.h', 'tools/fixtures/gp_config021_persisted_recovery/include/comms/backend_init.hpp', 'tools/fixtures/gp_config021_persisted_recovery/include/device/usbd_pvt.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/pio.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/structs/usb.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/sync.h', 'tools/fixtures/gp_config021_persisted_recovery/include/hardware/timer.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/lock_core.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/mutex.h', 'tools/fixtures/gp_config021_persisted_recovery/include/pico/stdlib.h', 'tools/fixtures/gp_config021_persisted_recovery/platform_doubles.cpp', 'tools/fixtures/gp_config022_rgb_target_validation/consumer_harness.cpp', 'tools/fixtures/gp_config022_rgb_target_validation/decoder_harness.cpp', 'tools/fixtures/gp_config022_rgb_target_validation/persistence_harness.cpp', 'tools/fixtures/gp_config022_rgb_target_validation/setconfig_harness.cpp', 'tools/fixtures/gp_config022_rgb_target_validation/startup_harness.cpp', 'tools/fixtures/gp_config022_rgb_target_validation/validation_harness.cpp']
def check_default_delta(root):
 old=subprocess.run(['git','show',BASE+':config/glyph/common/include/glyph_overrides.hpp'],cwd=root,capture_output=True,check=True).stdout
 new=regular(root,'config/glyph/common/include/glyph_overrides.hpp')
 anchor=b'RgbConfig {\n          .button_colors_count = 20,\n          .button_colors = {\n                {\n                BTN_LF1,\n                2282478'
 positions=[m.start() for m in re.finditer(rb'RgbConfig\s*\{',old)]
 require(len(positions)==13,'exact13 source RGB blocks')
 begin,end=positions[10],positions[11]
 block=old[begin:end];require(block.startswith(anchor),'exact legacy ordinal block11 anchor')
 expected=old[:begin]+block.replace(anchor,anchor.replace(b'count = 20',b'count = 11').replace(b'2282478',b'0'),1)+old[end:]
 require(new==expected,'default delta must be exact approved count11 and LF1black only')
 return {'original_sha256':digest(old),'corrected_sha256':digest(new),'other12blocks_and_unrelated_source':'BYTE_EXACT','count_only_cyan':'REJECTED_BY_DEFAULT_APPEARANCE_ASSERTION'}
def authenticate_inputs(root,fixture=None):
 if fixture is None:fixture=json.loads(regular(root,FIXTURE))
 require(fixture.get('schema_name')=='glyph_gp_config022_rgb_target_validation' and fixture.get('schema_version')==1,'fixture schema')
 require(fixture.get('base')==BASE,'fixture base');pins=fixture.get('pins');require(isinstance(pins,dict)and pins,'finite closure not frozen')
 require(set(pins)==set(PIN_PATHS),'finite source/input closure omission or extra')
 for p,v in pins.items():
  require(type(v) is dict and set(v)=={'sha256','mode'},'pin record type '+p)
  require(v['mode']=='100644' and stat.S_IMODE((Path(root)/p).stat().st_mode)&0o111==0,'mode substitution '+p)
  require(digest(regular(root,p))==v['sha256'],'input substitution '+p)
 require(fixture.get('expected_cases')==EXPECTED_CASES,'case census substitution/type/count')
 return pins

def run_host(root,temporary,*,negative_controls=True,pins=None):
 """Preparatory proof on the root-controlled draft; CLI authenticates finite pins first."""
 root=Path(root).resolve();temporary=Path(temporary).resolve();temporary.mkdir(parents=True,exist_ok=True);require(not temporary.is_relative_to(root),'output outside repository')
 b=load_base(root);cc=shutil.which('cc');cxx=shutil.which('c++');require(cc and cxx,'compilers unavailable')
 evidence={'classification':'C022_ACTUAL_SOURCE_HOST_ONLY','abis':{},'commands':[],'dependencies':[],'negative_controls':[],'hardware':'NOT_CLAIMED','default_delta':check_default_delta(root)}
 evidence['toolchain']=[{'compiler':c,'stdout':b._run([c,'--version'],root).stdout}for c in (cc,cxx)]
 deps=set();dependency_sets={}
 for label,abi in [('short','-fshort-enums'),('ordinary','-fno-short-enums')]:
  directory=temporary/label;directory.mkdir(exist_ok=True)
  overlay=directory/'consumer-overlay';(overlay/'pico').mkdir(parents=True,exist_ok=True)
  timer=regular(root,'tools/fixtures/gp_config021_persisted_recovery/include/pico/stdlib.h').decode()
  timer=timer.replace('inline absolute_time_t get_absolute_time() { return absolute_time_t(0); }','inline size_t c022_clock_index=0,c022_timer_calls=0; inline int64_t c022_last_diff=0; inline absolute_time_t get_absolute_time() { const int64_t values[]={1000,101000,351000,851000,1876000}; if(c022_clock_index>=5)std::abort(); return absolute_time_t(values[c022_clock_index++]); }').replace('return to._private_us_since_boot - from._private_us_since_boot;','++c022_timer_calls; c022_last_diff=to._private_us_since_boot - from._private_us_since_boot; return c022_last_diff;')
  (overlay/'pico/stdlib.h').write_text(timer)
  evidence.setdefault('derived_timer_stubs',[]).append({'path':str(overlay/'pico/stdlib.h'),'sha256':digest(timer.encode()),'source':'tools/fixtures/gp_config021_persisted_recovery/include/pico/stdlib.h','scope':'only clock values and call instrumentation'})
  prot=['-fsanitize=address,undefined,enum,shift','-fno-sanitize-recover=all','-fno-omit-frame-pointer']
  common=['-O0','-g',abi,*prot,*['-I'+str(root/p)for p in INCLUDES]]
  cpp=['-std=gnu++17','-Wno-missing-field-initializers','-Wno-non-c-typedef-for-linkage','-DFIRMWARE_NAME="host"','-DFIRMWARE_VERSION="host"','-DDEVICE_NAME="host"',*common]
  startup=[*cpp,*(['-fPIE']if sys.platform!='darwin'else[]),'-DNDEBUG','-finstrument-functions','-ffunction-sections','-fdata-sections']
  consumer=['-DNDEBUG','-I'+str(overlay),'-I'+str(root/'tools/fixtures/gp_config017_neopixel_repaired_current/include'),*cpp]
  specs=[];objects={}
  for graph,units,compiler,flags in [('c',C_UNITS,cc,['-std=c99',*common]),('general',GENERAL_UNITS,cxx,cpp),('startup',APP_UNITS,cxx,startup)]:
   for i,p in enumerate(units):
    obj=directory/(graph+'-'+str(i)+'.o');dep=obj.with_suffix('.d');warning=(['-Wno-tautological-constant-out-of-range-compare']if p=='HAL/pico/src/comms/console_detection.cpp'else['-Wno-gnu-designator']if p=='HAL/pico/src/comms/NintendoSwitchBackend.cpp'else[])if sys.platform=='darwin'else[]
    specs.append((graph,p,obj,dep,[compiler,*flags,*warning,'-MMD','-MF',str(dep),'-c',str(root/p),'-o',str(obj)]))
  for suite in SUITES:
   p=HOST+'/'+suite+'_harness.cpp';obj=directory/(suite+'-harness.o');dep=obj.with_suffix('.d');specs.append(('harness',p,obj,dep,[cxx,*(consumer if suite=='consumer'else cpp),'-MMD','-MF',str(dep),'-c',str(root/p),'-o',str(obj)]))
  def compile_one(spec):
   graph,p,obj,dep,cmd=spec;result=b._run(cmd,root,timeout=60);(directory/(obj.stem+'.compile.log')).write_text(json.dumps(cmd)+'\n'+result.stdout+result.stderr);require(result.returncode==0 and not result.stderr,'compile '+p+'\n'+result.stdout+result.stderr)
   # The consumer's derived clock is the only explicitly allowed out-of-tree MMD input.
   text=dep.read_text().replace(str(overlay/'pico/stdlib.h'),str(root/'tools/fixtures/gp_config021_persisted_recovery/include/pico/stdlib.h'));normalized=dep.with_suffix('.normalized.d');normalized.write_text(text)
   actual=b._dependency_paths(normalized,root)
   if pins is not None:require(actual<=set(pins),'dependency omission '+str(sorted(actual-set(pins))))
   return graph,p,obj,actual,cmd
  with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
   for graph,p,obj,actual,cmd in pool.map(compile_one,specs):objects[(graph,p)]=obj;deps|=actual;dependency_sets[(graph,p)]=actual;evidence['commands'].append(cmd)
  c_objects=[objects[('c',p)]for p in C_UNITS]
  def link(suite,units,start=False):
   binary=directory/suite;objs=([objects[('startup',p)]for p in units]if start else[objects[('general',p)]for p in units])+c_objects+([]if start else[objects[('harness',HOST+'/'+suite+'_harness.cpp')]])
   cmd=[cxx,*prot,*((['-Wl,-dead_strip','-Wl,-export_dynamic']if sys.platform=='darwin'else['-pie','-Wl,--gc-sections','-Wl,--export-dynamic'])if start else[]),*map(str,objs),'-o',str(binary)];result=b._run(cmd,root,timeout=60);evidence['commands'].append(cmd);(directory/(suite+'.link.log')).write_text(json.dumps(cmd)+'\n'+result.stdout+result.stderr);require(result.returncode==0 and not result.stderr,'link '+suite+'\n'+result.stdout+result.stderr);return binary
  pure=GENERAL_UNITS[:2]+RGB_UNITS
  suites={'validation':pure,'decoder':pure+['tools/fixtures/gp_config020_button_validation/abi_probe.cpp'],'persistence':GENERAL_UNITS[:5]+RGB_UNITS,'setconfig':GENERAL_UNITS[:7]+RGB_UNITS,'consumer':pure+['src/core/CommunicationBackend.cpp','src/core/InputMode.cpp','src/core/socd.cpp','HAL/pico/src/rgb/ButtonLocations.cpp']}
  binaries={suite:link(suite,units)for suite,units in suites.items()};binaries['startup']=link('startup',APP_UNITS,True)
  rows={}
  for suite in ('validation','decoder','persistence','setconfig'):
   result=b._run([binaries[suite]],root,timeout=30);(directory/(suite+'.run.log')).write_text(result.stdout+result.stderr);require(result.returncode==0 and not result.stderr,suite+' failed\n'+result.stdout+result.stderr)
   count=sum(s.startswith(('set'if suite=='setconfig'else suite)+'_case=')for s in result.stdout.splitlines());require(count>0,'missing cases '+suite)
   rows[suite]={'cases':count,'stdout_sha256':digest(result.stdout.encode()),'summary':[s for s in result.stdout.splitlines()if '_matrix 'in s],'binary_sha256':digest(binaries[suite].read_bytes()),'binary_path':str(binaries[suite])}
  rawdeps=set().union(*[dependency_sets[('general',p)]for p in suites['decoder']],*[dependency_sets[('c',p)]for p in C_UNITS],dependency_sets[('harness',HOST+'/decoder_harness.cpp')])
  validator={'path':str(binaries['decoder']),'sha256':digest(binaries['decoder'].read_bytes()),'source_pins':{p:digest(regular(root,p))for p in sorted(rawdeps)},'abi':label,'interface':'--config-raw JSON accepted/decoded/error; exit0 accepted,1 semantic rejection,2 decode failure'}
  evidence.setdefault('raw_validators',{})[label]=validator
  if label=='short':evidence['raw_validator']=validator
  rows['archived_owner']=archive_characterization(root,directory,b,binaries['decoder'])
  result=b._run([binaries['setconfig'],'--missing-callback'],root);require(result.returncode==0 and not result.stderr,'fresh SET missing callback');(directory/'setconfig.missing.log').write_text(result.stdout);rows['setconfig']['missing_callback_cases']=1
  offsets=b._rgb_offsets(binaries['startup'],directory/'startup.nm.json',root)
  def startup_one(case):
   env=b._startup_environment(case[0],offsets);res=b._run([binaries['startup'],*case],root,env=env,timeout=10);return {'case':list(case),'exit':res.returncode,'stdout':res.stdout,'stderr':res.stderr}
  with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:startup_rows=list(pool.map(startup_one,STARTUP_CASES))
  (directory/'startup.actual.json').write_text(json.dumps(startup_rows,indent=2)+'\n')
  for row in startup_rows:require(row['exit']==0 and not row['stderr']and'case=whole_startup_'in row['stdout'],'startup '+str(row))
  rows['startup']={'cases':startup_rows,'binary_sha256':digest(binaries['startup'].read_bytes())}
  consumer_rows={}
  for name in ('static','shift','xwave','legacy','corrected','cyan'):
   for lane in (('baseline','validated')if name in ('static','shift','xwave','corrected','cyan')else('baseline',)):
    result=b._run([binaries['consumer'],name,lane],root);(directory/('consumer.'+name+'.'+lane+'.log')).write_text(result.stdout+result.stderr);require(result.returncode==0 and not result.stderr,'consumer '+name+' '+lane+'\n'+result.stdout+result.stderr);consumer_rows[name+'/'+lane]=result.stdout
  for name in ('static','shift','xwave','corrected','cyan'):require(consumer_rows[name+'/baseline']==consumer_rows[name+'/validated'],'validation changed consumer '+name)
  strip=lambda v:'\n'.join(x for x in v.splitlines()if not x.startswith('consumer_case='))
  require(strip(consumer_rows['legacy/baseline'])==strip(consumer_rows['corrected/validated']),'legacy/corrected all76 pixels/60 slots differ')
  require(strip(consumer_rows['cyan/validated'])!=strip(consumer_rows['corrected/validated']),'count-only cyan counterexample missing')
  rows['consumer']={'runs':len(consumer_rows),'unchanged_valid':'BYTE_EXACT','legacy_corrected_all76pixels_all60slots':'BYTE_EXACT','count_only_cyan':'DIFFERENT_AS_EXPECTED','hsv_conversion':'SYNTHETIC_HOST_STUB_NOT_PHYSICAL'}
  if negative_controls:evidence['negative_controls']+=runtime_negatives(root,directory,label,abi,objects,c_objects,cpp,startup,prot,cxx,b,binaries,offsets,suites)
  for suite in ('validation','decoder','persistence','setconfig'):require(rows[suite]['cases']==EXPECTED_CASES[label][suite],'executed case census '+label+'/'+suite)
  evidence['abis'][label]=rows
 deps|=set(EXPLICIT_INPUTS)
 evidence['dependencies']=sorted(deps);evidence['dependency_pins']={p:{'mode':'100644','sha256':digest(regular(root,p))}for p in sorted(deps)}
 if pins is not None:require(deps<=set(pins),'closure outside frozen pins')
 if negative_controls and pins is not None:evidence['negative_controls']+=identity_negatives(root)
 (temporary/'execution.json').write_text(json.dumps(evidence,indent=2)+'\n');return evidence

def runtime_negatives(root,directory,label,abi,objects,c_objects,cpp,startup,prot,cxx,b,binaries,offsets,suites):
 controls=[
  ('rgb_callback_omission','config/glyph/common/src/glyph_config_validation.cpp','if (!validate_glyph_rgb_targets(config)) {','if (false) {','validation',None),
  ('counted_zero_allowed','src/core/config_rgb_target_validation.cpp','        return false;\n    }\n    for (size_t i = 0; i < count; ++i) {','        return true;\n    }\n    for (size_t i = 0; i < count; ++i) {','validation',None),
  ('last_rgb_omission','src/core/config_rgb_target_validation.cpp','for (size_t j = 0; j < rgb.button_colors_count; ++j) {','for (size_t j = 0; j + 1 < rgb.button_colors_count; ++j) {','validation',None),
  ('nested_count_guard_omission','src/core/config_rgb_target_validation.cpp','if (static_cast<size_t>(rgb.button_colors_count) >','if (false && static_cast<size_t>(rgb.button_colors_count) >','validation',None),
  ('persistence_callback_bypass','HAL/pico/src/core/Persistence.cpp','return _validator(config, error);','return true;','persistence',None),
  ('SET_callback_bypass','HAL/pico/src/comms/ConfiguratorBackend.cpp','!persistence.ValidateConfig(candidate, validation_error)','false','setconfig',None),
  ('startup_base_callback','config/glyph/common/src/config.cpp','SetValidator(validate_glyph_config)','SetValidator(validate_config_semantics)','startup',('rgb_rejected','late','display')),
  ('startup_core0_refusal_omission','config/glyph/common/src/config.cpp','    if (read_boot_state().outcome != BootOutcome::Normal) return;','','startup',('rgb_rejected','late','display')),
 ]
 records=[]
 for name,path,old,new,suite,case in controls:
  v=directory/('negative-'+name);v.mkdir(exist_ok=True);raw=regular(root,path).decode();require(raw.count(old)==1,'mutation anchor '+name);changed=v/Path(path).name;changed.write_text(raw.replace(old,new,1));obj=v/'mutant.o';cmd=[cxx,*(startup if suite=='startup'else cpp),'-c',str(changed),'-o',str(obj)];res=b._run(cmd,root,timeout=60);require(res.returncode==0 and not res.stderr,'mutant compile '+name+'\n'+res.stderr)
  units=APP_UNITS if suite=='startup'else suites[suite];graph='startup'if suite=='startup'else'general';objs=[obj if p==path else objects[(graph,p)]for p in units]+c_objects+([]if suite=='startup'else[objects[('harness',HOST+'/'+suite+'_harness.cpp')]])
  binary=v/'mutant';link=[cxx,*prot,*((['-Wl,-dead_strip','-Wl,-export_dynamic']if sys.platform=='darwin'else['-pie','-Wl,--gc-sections','-Wl,--export-dynamic'])if suite=='startup'else[]),*map(str,objs),'-o',str(binary)];res=b._run(link,root,timeout=60);require(res.returncode==0 and not res.stderr,'mutant link '+name+'\n'+res.stderr)
  env=None;args=[]
  if case:env=b._startup_environment(case[0],b._rgb_offsets(binary,v/'nm.json',root));args=list(case)
  run=[binary,*args];res=b._run(run,root,timeout=30);(v/'run.log').write_text(res.stdout+res.stderr);require(res.returncode!=0,'negative unexpectedly passed '+name)
  records.append({'name':name,'abi':label,'compile_command':list(map(str,cmd)),'link_command':list(map(str,link)),'run_command':list(map(str,run)),'returncode':res.returncode,'stdout_sha256':digest(res.stdout.encode()),'stderr_sha256':digest(res.stderr.encode()),'rejected':True})
 return records

def archive_characterization(root,directory,b,binary):
 import copy
 doc=regular(root,'docs/calibration/gp_config_021_hardware_result.md').decode()
 match=re.search(r'<!-- c021-evidence-bundle:start -->\s*```json\s*(.*?)```',doc,re.S);require(match,'Git-preserved immutable HEP archive marker')
 bundle=json.loads(match.group(1));require(bundle['encoding']=='base64-zlib-json','archive encoding');data=zlib.decompress(base64.b64decode(bundle['payload'],validate=True));require(digest(data)==bundle['uncompressed_sha256'],'archive digest')
 files=json.loads(data)['files'];records={}
 for name in ('session/original-config.raw.bin','session/original-config.json'):
  record=files[name];raw=base64.b64decode(record['base64'],validate=True);require(len(raw)==record['size_bytes']and digest(raw)==record['sha256'],'archived original authenticity');records[name]=raw
 raw=records['session/original-config.raw.bin'];require(len(raw)==4201 and digest(raw)=='f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480','literal archived original identity')
 original=json.loads(records['session/original-config.json']);corrected=copy.deepcopy(original);colors=corrected['rgbConfigs'][10]['buttonColors'];require(len(colors)==20 and colors[11:]==[{}]*9,'archive9 structural empty objects')
 names=['BTN_LF1','BTN_LF2','BTN_LF3','BTN_LT1','BTN_RF1','BTN_RF2','BTN_RF5','BTN_RF6','BTN_RT1','BTN_MB1','BTN_LF5'];require(colors[:11]==[{'button':n,'color':2282478}for n in names],'archive exact retained11')
 del colors[11:];colors[0]['color']=0;undo=copy.deepcopy(corrected);undo['rgbConfigs'][10]['buttonColors'][0]['color']=2282478;undo['rgbConfigs'][10]['buttonColors'] += [{}]*9;require(undo==original,'unrelated archive semantic fields changed')
 archived=directory/'archived-original.raw.bin';archived.write_bytes(raw)
 command=[binary,'--archived-raw-check',archived];result=b._run(command,root);(directory/'archived-owner.run.log').write_text(result.stdout+result.stderr);require(result.returncode==0 and not result.stderr and'historical_not_fresh=YES PASS'in result.stdout,'archive actual decoder/wrapper proof '+result.stdout+result.stderr)
 return {'classification':'ARCHIVED_HISTORICAL_NOT_FRESH','raw_sha256':digest(raw),'raw_bytes':len(raw),'json_sha256':digest(records['session/original-config.json']),'all_unrelated_semantic_fields':'IDENTICAL','only_changes':['rgbConfigs[10].buttonColors[0].color:2282478->0','remove rgbConfigs[10].buttonColors[11:20] exactly9 empty objects'],'actual_validator_stdout':result.stdout,'command':list(map(str,command))}

def identity_negatives(root):
 import copy
 fixture=json.loads(regular(root,FIXTURE));names=[]
 def reject(name,changed):
  try:authenticate_inputs(root,changed)
  except (ContractError,TypeError,ValueError,AttributeError):names.append({'name':name,'rejected':True,'classification':'FINITE_INPUT_AUTHENTICATION_NEGATIVE'});return
  raise ContractError('identity control unexpectedly passed '+name)
 for path in PIN_PATHS:
  x=copy.deepcopy(fixture);del x['pins'][path];reject('omit/'+path,x)
 for name in ('hash','mode','pin_type','count','count_type','extra_path'):
  x=copy.deepcopy(fixture);p=SOURCE_PATHS[0]
  if name=='hash':x['pins'][p]['sha256']='0'*64
  elif name=='mode':x['pins'][p]['mode']='100755'
  elif name=='pin_type':x['pins'][p]=[]
  elif name=='count':x['expected_cases']['short']['decoder']-=1
  elif name=='count_type':x['expected_cases']['short']['decoder']=str(x['expected_cases']['short']['decoder'])
  elif name=='extra_path':x['pins']['unknown/helper.cpp']={'mode':'100644','sha256':'0'*64}
  reject(name,x)
 return names

def authenticate_repository(root):
 """CLI accepts committed, clean critical source and the exact seven-path delta."""
 spec=importlib.util.spec_from_file_location('c022_integrity',Path(root)/'tools/glyph_tracked_worktree_integrity.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 require(not m.tracked_worktree_divergence(Path(root)),'tracked HEAD/index/worktree divergence')
 require(not m.untracked_critical_worktree_paths(Path(root)),'untracked critical source')
 require(not m.ignored_critical_worktree_paths(Path(root)),'ignored critical source')
 def tree(ref):
  raw=subprocess.run(['git','ls-tree','-r','-z',ref],cwd=root,capture_output=True,check=True).stdout;out={}
  for item in raw.split(b'\0'):
   if not item:continue
   meta,path=item.split(b'\t',1);mode,kind,oid=meta.decode().split();path=path.decode()
   if m.is_critical_path(path):require(kind=='blob'and mode=='100644','critical object mode/type');out[path]=(mode,oid)
  return out
 old=tree(BASE);new=tree('HEAD');changed={p for p in set(old)|set(new)if old.get(p)!=new.get(p)};require(changed==set(SOURCE_PATHS),'critical candidate scope differs from exact seven paths')
 require(subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=root,capture_output=True).returncode==0,'candidate does not preserve exact BASE ancestry')
 return {'base':BASE,'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'critical_changed_paths':sorted(changed)}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 try:
  pins=authenticate_inputs(ROOT);repository=authenticate_repository(ROOT);e=run_host(ROOT,args.output,pins=pins);e['repository']=repository;(args.output/'execution.json').write_text(json.dumps(e,indent=2)+'\n');print(json.dumps({'result':'PASS','abis':{k:{s:v.get('cases',v.get('runs'))for s,v in rows.items()}for k,rows in e['abis'].items()},'dependencies':len(e['dependencies']),'negative_controls':len(e['negative_controls']),'report':str(args.output/'execution.json')}));return 0
 except (ContractError,subprocess.SubprocessError,OSError)as e:print('FAIL: '+str(e),file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
