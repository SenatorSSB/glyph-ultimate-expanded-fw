from pathlib import Path
import subprocess,hashlib,json,re,shutil
root=Path('/private/tmp/glyph-profile-native-20261020');out=Path('/private/tmp/glyph-native-production-abi');nb=root/'.pio/libdeps/glyph_mk6/Nanopb';tc=root/'.platformio-home/packages/toolchain-rp2040-earlephilhower/bin';py='/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/.venv/bin/python';out.mkdir(exist_ok=True)
assert hashlib.sha256((nb/'pb.h').read_bytes()).hexdigest()=='e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2'
assert hashlib.sha256((nb/'generator/nanopb_generator.py').read_bytes()).hexdigest()=='67d3c5e6de1e5dbd9f45bb4e5b7055d888d1afd6d6e1690791ab8607b6c6b738'
report={'dependency_version':'0.4.92','commands':[],'variants':{},'hashes':{},'size_macros':{}}
for variant in ['baseline','proposed']:
 d=out/variant;(d/'schema').mkdir(parents=True,exist_ok=True);(d/'generated').mkdir(exist_ok=True)
 origin=root/'schema/haybox' if variant=='baseline' else Path('/private/tmp/glyph-native-proposed-abi/schema')
 for name in ['config.proto','config.options']:shutil.copyfile(origin/name,d/'schema'/name)
 args=[py,str(nb/'generator/nanopb_generator.py'),'-I',str(d/'schema'),'-f',str(d/'schema/config.options'),'--error-on-unmatched','--no-timestamp','-D',str(d/'generated'),str(d/'schema/config.proto')];report['commands'].append(args);p=subprocess.run(args,text=True,capture_output=True);(d/'generation.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
 shutil.copyfile('/private/tmp/glyph-native-resource-probes/layout.cpp',d/'layout.cpp');report['variants'][variant]={}
 for abi,flag in [('short','-fshort-enums'),('no-short','-fno-short-enums')]:
  args=[str(tc/'arm-none-eabi-g++'),'-std=c++17','-mcpu=cortex-m0plus','-mthumb',flag,'-I'+str(d/'generated'),'-I'+str(nb),'-I'+str(root/'include'),'-I'+str(root/'HAL/pico/include'),'-c',str(d/'layout.cpp'),'-o',str(d/(abi+'.o'))];report['commands'].append(args);p=subprocess.run(args,text=True,capture_output=True);(d/(abi+'-compile.log')).write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr;s=subprocess.check_output([str(tc/'arm-none-eabi-nm'),'-S',str(d/(abi+'.o'))],text=True);(d/(abi+'-nm.txt')).write_text(s);report['variants'][variant][abi]={r.split()[-1][7:]:int(r.split()[1],16) for r in s.splitlines() if 'layout_' in r}
 # Compile actual generated descriptor TU too, no link or production build.
 args=[str(tc/'arm-none-eabi-gcc'),'-std=c11','-mcpu=cortex-m0plus','-mthumb','-fshort-enums','-I'+str(d/'generated'),'-I'+str(nb),'-c',str(d/'generated/config.pb.c'),'-o',str(d/'descriptor.o')];report['commands'].append(args);p=subprocess.run(args,text=True,capture_output=True);(d/'descriptor-compile.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
 for stem in ['Config','GameModeConfig','UltimateProfile','ProfileStoreRequest','ProfileStoreResponse','UltimateProfileCondition','UltimateProfileOutputEffect']:
  lines=[l for l in (d/'generated/config.pb.h').read_text().splitlines() if l.startswith('#define '+stem+'_size ') or l.startswith('/* '+stem+'_size ')];report['size_macros'].setdefault(stem,{})[variant]=lines
 report.setdefault('callback_fields',{})[variant]=[l for l in (d/'generated/config.pb.h').read_text().splitlines() if ('native_payload' in l or 'UltimateProfile_CALLBACK' in l or ('ultimate_profile_engine' in l and ('UINT32' in l or 'uint8_t' in l)))]
oldbase=json.loads(Path('/private/tmp/glyph-native-resource-probes/abi.json').read_text());oldpro=json.loads(Path('/private/tmp/glyph-native-proposed-abi/report.json').read_text())
report['drift_vs_0.4.91']={};report['proposed_deltas']={}
for abi in ['short','no-short']:
 report['drift_vs_0.4.91'][abi]={'baseline':{k:v-oldbase[abi][k] for k,v in report['variants']['baseline'][abi].items()},'proposed':{k:v-oldpro['abis'][abi]['sizes'][k] for k,v in report['variants']['proposed'][abi].items()}}
 report['proposed_deltas'][abi]={k:v-report['variants']['baseline'][abi][k] for k,v in report['variants']['proposed'][abi].items()}
# Recompile designer's concrete native byteowner/view/frame declarations against actual current production dependency.
d=out/'native-layout';d.mkdir(exist_ok=True);shutil.copyfile('/private/tmp/glyph-native-design-layout/layout.cpp',d/'layout.cpp');shutil.copyfile('/private/tmp/glyph-native-design-layout/stdlib.hpp',d/'stdlib.hpp');report['native_layout']={}
for abi,flag in [('short','-fshort-enums'),('no-short','-fno-short-enums')]:
 args=[str(tc/'arm-none-eabi-g++'),'-std=c++17','-mcpu=cortex-m0plus','-mthumb',flag,'-include',str(d/'stdlib.hpp'),'-I'+str(d),'-I'+str(out/'proposed/generated'),'-I'+str(nb),'-I'+str(root/'include'),'-c',str(d/'layout.cpp'),'-o',str(d/(abi+'.o'))];report['commands'].append(args);p=subprocess.run(args,text=True,capture_output=True);(d/(abi+'-compile.log')).write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr;s=subprocess.check_output([str(tc/'arm-none-eabi-nm'),'-S',str(d/(abi+'.o'))],text=True);(d/(abi+'-nm.txt')).write_text(s);report['native_layout'][abi]={r.split()[-1]:int(r.split()[1],16) for r in s.splitlines() if 'native_' in r}
for p in list(out.rglob('*.proto'))+list(out.rglob('*.options'))+list(out.rglob('*.h'))+list(out.rglob('*.c'))+[nb/'pb.h',nb/'generator/nanopb_generator.py',tc/'arm-none-eabi-g++']:
 report['hashes'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['variants','drift_vs_0.4.91','proposed_deltas','native_layout','size_macros','callback_fields']},indent=2))
