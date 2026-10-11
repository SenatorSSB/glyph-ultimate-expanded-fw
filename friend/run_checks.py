#!/usr/bin/env python3
"""Private actual-source host checks. No device access, firmware writes or flashing."""
import concurrent.futures, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT.parent / 'storage-recovery-v2' / 'verification'
OUT.mkdir(parents=True, exist_ok=True)
FIX = 'tools/fixtures/gp_config021_persisted_recovery'
GEN = '.pio/build/glyph_mk6/nanopb/generated-src'
NP = '.pio/libdeps/glyph_mk6/Nanopb'
INCLUDES = ['friend/tests/include', FIX, FIX+'/include', GEN, NP, FIX+'/dependencies',
            FIX+'/dependencies/joybus', FIX+'/dependencies/nes', 'include', 'HAL/pico/include',
            'config/glyph/common/include', 'config/glyph/glyph_mk6/include', 'lib/TUCompositeHID/include', 'src', '.']
CPP = ['friend/tests/harness.cpp', 'HAL/pico/src/core/Persistence.cpp',
       'src/core/config_validation.cpp', 'src/core/config_button_validation.cpp',
       'src/core/config_usb_default_validation.cpp', 'src/core/config_rgb_target_validation.cpp',
       'config/glyph/common/src/glyph_config_validation.cpp', 'src/core/InputMode.cpp',
       'src/core/ControllerMode.cpp', 'src/core/socd.cpp', 'src/modes/Ultimate.cpp',
       FIX+'/dependencies/CRC32.cpp', FIX+'/dependencies/pb_arduino.cpp']
C = [NP+'/pb_common.c', NP+'/pb_encode.c', NP+'/pb_decode.c', GEN+'/config.pb.c']
def run(command):
    r = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode: raise RuntimeError(' '.join(map(str,command))+'\n'+r.stdout)
    return r.stdout
for abi in ['short', 'ordinary']:
    directory = OUT / ('host-'+abi); directory.mkdir(exist_ok=True)
    flags = ['-O1', '-g', '-DNDEBUG', '-DGLYPH_PRIVATE_FRIEND_STORAGE_RECOVERY=1', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer', '-ffunction-sections', '-fdata-sections']
    if abi == 'short': flags += ['-fshort-enums']
    flags += ['-I'+str(ROOT/p) for p in INCLUDES]
    specs = [(p, directory/(str(i)+'.o')) for i,p in enumerate(CPP+C)]
    def compile_one(spec):
        p,obj = spec
        command = [('clang' if p in C else 'clang++'), ('-std=c99' if p in C else '-std=gnu++17'), *flags, '-c', str(ROOT/p), '-o', str(obj)]
        output = run(command)
        (directory/(obj.stem+'.log')).write_text(json.dumps(command)+'\n'+output)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(compile_one,specs))
    exe = directory/'friend-tests'
    run(['clang++', '-fsanitize=address,undefined', '-Wl,-dead_strip', *[str(o) for p,o in specs], '-o', str(exe)])
    output = run([str(exe), str(OUT/('baked-'+abi+'.pb'))])
    (OUT/('focused-'+abi+'.log')).write_text(output)
    print('ABI='+abi+'\n'+output, flush=True)
    off_flags=[f for f in flags if f!='-DGLYPH_PRIVATE_FRIEND_STORAGE_RECOVERY=1']
    off_objects=[]
    for i,path in enumerate(['friend/tests/no_recovery_harness.cpp','HAL/pico/src/core/Persistence.cpp']):
        obj=directory/('macro-off-'+str(i)+'.o');off_objects.append(str(obj))
        run(['clang++','-std=gnu++17',*off_flags,'-c',str(ROOT/path),'-o',str(obj)])
    control=directory/'macro-off-control'
    run(['clang++','-fsanitize=address,undefined','-Wl,-dead_strip',*off_objects,*[str(o) for p,o in specs if p not in ['friend/tests/harness.cpp','HAL/pico/src/core/Persistence.cpp']],'-o',str(control)])
    output=run([str(control)]);(OUT/('macro-off-'+abi+'.log')).write_text(output);print(output,flush=True)
