#!/usr/bin/env python3
"""Focused actual resolver/native activation checks on both enum ABIs; no device."""
import subprocess,sys,tempfile
from pathlib import Path
from check_glyph_profile_native_ultimate import ROOT,compile_runner,program

def main():
 import glyph_serial_config_tool as writer
 pb,_,_=writer.load_runtime_proto_modules(ROOT)
 for default in (False,True):
  with tempfile.TemporaryDirectory(prefix='glyph-display-') as d:
   t=Path(d)
   _,_,flags,objects=compile_runner(t,default=default)
   p=t/'native.pb';p.write_bytes(program(pb,pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE),[]).SerializeToString())
   exe=t/'labels'
   sources=['tools/fixtures/active_profile_display/labels.cpp','HAL/pico/src/display/CurrentProfileLabel.cpp','HAL/pico/src/display/InputDisplay.cpp','src/modes/Ultimate.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp','src/core/config_button_validation.cpp']
   subprocess.run(['c++','-std=c++17','-I',str(ROOT/'tools/fixtures/active_profile_display/include'),*flags,'-fsanitize=address,undefined','-fno-omit-frame-pointer',*[str(ROOT/s) for s in sources],*objects,'-o',str(exe)],check=True)
   subprocess.run([str(exe),str(p)],check=True)
   print('PASS actual resolver/native activation labels; ABI='+('default' if default else 'short'),flush=True)
 # Both current-identity surfaces must call the same resolver. Ordinary menu
 # config-row naming and viewer plate-to-button-layout dispatch remain separate.
 for relative in ['config/glyph/common/src/display/MenuButtonHints.cpp','HAL/pico/src/display/InputDisplay.cpp']:
  s=(ROOT/relative).read_text();assert 'current_profile_label(instance->CurrentGameMode(), _backend_id)' in s
  assert 'display.print(mode_config.name)' not in s
 assert 'dashboard_plate_label(mode_config.layout_plate)' in (ROOT/'config/glyph/common/src/display/MenuButtonHints.cpp').read_text()
 return 0
if __name__=='__main__':raise SystemExit(main())
