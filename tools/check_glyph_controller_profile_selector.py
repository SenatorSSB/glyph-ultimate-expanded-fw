#!/usr/bin/env python3
"""Source-faithful controller selector/menu checks; no device access."""
import os, subprocess, sys, tempfile
from pathlib import Path
from check_glyph_stage_b_ultimate_profiles import ROOT, NANOPB

def run(command):
    p=subprocess.run([str(x) for x in command],cwd=ROOT,text=True,capture_output=True,timeout=90,
        env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout

def main():
    with tempfile.TemporaryDirectory(prefix='glyph-selector-') as d:
        t=Path(d);g=t/'generated';g.mkdir();schema=ROOT/'schema/haybox'
        run([sys.executable,NANOPB/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',g,schema/'config.proto'])
        from check_glyph_profile_native_ultimate import program
        import glyph_serial_config_tool as writer
        pb,_,_=writer.load_runtime_proto_modules(ROOT)
        context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
        wrappers=[]
        for i in range(2):
            path=t/('native'+str(i)+'.pb');path.write_bytes(program(pb,context,[]).SerializeToString());wrappers.append(path)
        source=(ROOT/'config/glyph/common/src/config.cpp').read_text()
        start=source.index('__attribute__((noinline)) void service_profile_selection()')
        end=source.index('\n// Recovery deliberately reuses',start)
        (g/'selector_service.inc').write_text(source[start:end])
        # Existing UI doubles are retained; remove enum doubles now supplied
        # by the actual current generated ABI.
        ui=t/'include/comms';ui.mkdir(parents=True)
        s=(ROOT/'tools/fixtures/config_menu_host/include/comms/IntegratedDisplay.hpp').read_text()
        s='\n'.join(x for x in s.splitlines() if not x.startswith(('enum Button','enum DashboardOption')))+'\n'
        (ui/'IntegratedDisplay.hpp').write_text(s)
        resets=(ROOT/'tools/fixtures/config_menu_host/include/reboot.hpp').read_text()
        resets=resets.replace('struct WatchdogStub', 'inline unsigned firmware_reboots=0,bootloader_reboots=0,disconnects=0;\nstruct WatchdogStub')
        resets=resets.replace('inline void reboot_firmware() {}','inline void reboot_firmware() {++firmware_reboots;}')
        resets=resets.replace('inline void reboot_bootloader() {}','inline void reboot_bootloader() {++bootloader_reboots;}')
        resets=resets.replace('inline void tud_disconnect() {}','inline void tud_disconnect() {++disconnects;}')
        (t/'include/reboot.hpp').write_text(resets)
        includes=[g,t/'include',ROOT/'tools/fixtures/config_menu_host/include',ROOT/'HAL/pico/include',ROOT/'config/glyph/common/include',ROOT/'include',ROOT,NANOPB]
        for abi in ['-fshort-enums','-fno-short-enums']:
            exe=t/abi[2:]
            command=['c++','-std=c++17',abi,'-O1','-g','-Wall','-Wextra','-Wno-unused-parameter','-Wno-type-limits','-Wno-missing-field-initializers','-fsanitize=address,undefined','-fno-omit-frame-pointer']
            command += [x for p in includes for x in ['-I',p]]
            command += [ROOT/'tools/fixtures/controller_profile_selector/metadata_menu.cpp',ROOT/'src/core/profile_selection.cpp','-o',exe]
            run(command);print(abi,run([exe]),end='')
            deps=ROOT/'tools/fixtures/gp_config021_persisted_recovery'
            host=ROOT/'tools/fixtures/profile_store_config_persistence_host'
            inc=[host/'include',deps/'include',ROOT/'HAL/pico/include',ROOT/'include',g,NANOPB,deps/'dependencies']
            flags=[x for p in inc for x in ['-I',p]]
            objects=[]
            for source in [NANOPB/'pb_common.c',NANOPB/'pb_decode.c',NANOPB/'pb_encode.c',g/'config.pb.c']:
                obj=t/(abi+source.stem+'.o');run(['cc','-std=c11',abi,*flags,'-c',source,'-o',obj]);objects.append(obj)
            sources=[ROOT/'tools/fixtures/controller_profile_selector/selection_persistence.cpp',host/'checked_storage_double.cpp',ROOT/'HAL/pico/src/core/Persistence.cpp',deps/'dependencies/pb_arduino.cpp',deps/'dependencies/CRC32.cpp',ROOT/'src/modes/UltimateNativeProfile.cpp',ROOT/'src/core/profile_selection.cpp',ROOT/'src/core/config_validation.cpp',ROOT/'src/core/config_button_validation.cpp',ROOT/'src/core/config_usb_default_validation.cpp']
            exe=t/(abi+'-persistence')
            run(['c++','-std=c++17',abi,'-O1','-g','-DARDUINO=1','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1','-fsanitize=address,undefined','-fno-omit-frame-pointer',*flags,*sources,*objects,'-o',exe])
            print(abi,run([exe,*wrappers]),end='')
    return 0
if __name__=='__main__':raise SystemExit(main())
