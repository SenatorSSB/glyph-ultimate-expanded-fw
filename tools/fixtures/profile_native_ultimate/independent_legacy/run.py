import pathlib,subprocess,json,hashlib
R=pathlib.Path('/private/tmp/glyph-native-curation-20261020'); D=pathlib.Path('/private/tmp/glyph-native-independent-oracle'); N=pathlib.Path('/private/tmp/glyph-profile-native-20261020/.pio/libdeps/glyph_mk6/Nanopb'); G=R/'docs/runtime_config/profile_native_ultimate/production_abi_evidence/baseline/generated'
commands=[]
(D/"corpus").mkdir(exist_ok=True)
def run(c):
 commands.append([str(x) for x in c]);p=subprocess.run(c,cwd=D,capture_output=True,text=True);(D/'commands.json').write_text(json.dumps(commands,indent=2));
 if p.returncode:raise Exception(p.stdout+p.stderr)
 return p
inc=[]
for p in [R/'tools/fixtures/stage_c_ultimate_profiles_host/include',G,N,R/'include',R/'HAL/pico/include',R/'config/glyph/common/include',R/'config/glyph/glyph_mk6/include',R/'src']:inc+=['-I',str(p)]
common=['-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-non-c-typedef-for-linkage',*inc]
sources=[R/p for p in ['src/modes/Ultimate.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp','src/core/config_validation.cpp','src/core/config_button_validation.cpp','src/core/config_usb_default_validation.cpp','src/core/config_rgb_target_validation.cpp','config/glyph/common/src/glyph_config_validation.cpp']]
for abi,extra in [('short',['-fshort-enums']),('default',[])]:
 objects=[]
 for src in [N/'pb_common.c',N/'pb_decode.c',N/'pb_encode.c',G/'config.pb.c']:
  obj=D/(abi+'-'+src.stem+'.o');run(['cc','-std=c11',*common,*extra,'-c',str(src),'-o',str(obj)]);objects.append(obj)
 exe=D/('probe-'+abi);run(['c++','-std=c++17',*common,*extra,str(D/'probe.cpp'),*map(str,sources),*map(str,objects),'-o',str(exe)])
 p=run([str(exe),str(D/'base.bin')]);(D/(abi+'-expected.jsonl')).write_text(p.stdout);(D/(abi+'-status.txt')).write_text(p.stderr)
assert (D/'short-expected.jsonl').read_bytes()==(D/'default-expected.jsonl').read_bytes()
files=[R/'src/modes/Ultimate.cpp',R/'src/core/config_validation.cpp',R/'include/modes/UltimateProfileEvaluator.hpp',G/'config.pb.h',G/'config.pb.c',N/'pb.h',D/'base.bin']
(D/'input-hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
print(p.stderr.strip()+'; identical enum ABIs')
