#!/usr/bin/env python3
"""Compile actual candidate source with the pinned LittleFS NOR test mount."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,sys

def build(repo,out,framework=None,nanopb=None,sanitize=True):
 repo=Path(repo).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 here=Path(__file__).resolve().parent
 home=Path(os.environ.get('PLATFORMIO_CORE_DIR',Path.home()/'.platformio'))
 framework=Path(framework or home/'packages/framework-arduinopico').resolve()
 nanopb=Path(nanopb or repo/'.pio/libdeps/glyph_mk6/Nanopb').resolve()
 version_header=framework/'cores/rp2040/RP2040Version.h'
 version=version_header.read_text()
 if tuple(int(re.search(r'#define ARDUINO_PICO_'+name+r'\s+(\d+)',version).group(1)) for name in ['MAJOR','MINOR','REVISION'])!=(3,6,3):raise ValueError('exact Arduino-Pico3.6.3 framework required')
 fw=framework/'libraries/LittleFS';deps=repo/'tools/fixtures/gp_config021_persisted_recovery/dependencies';gen=out/'generated';gen.mkdir(exist_ok=True)
 logs=[]
 def run(args):
  p=subprocess.run(list(map(str,args)),cwd=repo,capture_output=True,text=True);logs.append({'argv':list(map(str,args)),'stdout':p.stdout,'stderr':p.stderr,'exit':p.returncode})
  (out/'build-log.json').write_text(json.dumps(logs,indent=2)+'\n')
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 schema=repo/'schema/haybox'
 for name in ['config','package']:
  run([sys.executable,'-m','grpc_tools.protoc','-I'+str(schema),'--descriptor_set_out='+str(gen/(name+'.pb')),schema/(name+'.proto')])
 run([sys.executable,nanopb/'generator/nanopb_generator.py','-I'+str(schema),'-D'+str(gen),gen/'config.pb',gen/'package.pb'])
 inc=[repo/'tools/fixtures/profile_store_config_persistence_host/include',repo/'tools/fixtures/gp_config021_persisted_recovery/include',gen,nanopb,repo/'include',repo/'HAL/pico/include',repo/'HAL/pico/src/core',repo/'config/glyph/common/include',repo/'config/glyph/glyph_mk6/include',fw/'lib/littlefs',deps]
 args=[x for p in inc for x in ['-I',str(p)]]
 flags=['-O1','-fshort-enums','-DGLYPH_PACKAGE_V1=1','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1','-DLFS_NAME_MAX=32','-fno-omit-frame-pointer','-g']
 if sanitize:flags+=['-fsanitize=address,undefined']
 cc=os.environ.get('CC','cc');cxx=os.environ.get('CXX','c++');objects=[]
 cs=[nanopb/'pb_common.c',nanopb/'pb_decode.c',nanopb/'pb_encode.c',gen/'config.pb.c',gen/'package.pb.c',fw/'src/lfs.c',fw/'src/lfs_util.c']
 for i,src in enumerate(cs):
  obj=out/(str(i)+'-'+src.stem+'.o');run([cc,'-std=c11',*flags,*args,'-c',src,'-o',obj]);objects.append(obj)
 cpp=[here/'harness.cpp',repo/'HAL/pico/src/core/Persistence.cpp',repo/'HAL/pico/src/core/GlyphPackageSourceReader.cpp',repo/'src/core/PackageNamespaceClassifier.cpp',repo/'src/core/PackageStorageFormat.cpp',repo/'HAL/pico/src/core/CheckedStorage.cpp',repo/'src/core/PackageStorageFence.cpp',deps/'pb_arduino.cpp',deps/'CRC32.cpp',repo/'src/modes/UltimateNativeProfile.cpp',repo/'src/core/ConfigWireValidator.cpp',repo/'src/core/config_validation.cpp',repo/'src/core/config_button_validation.cpp',repo/'src/core/config_usb_default_validation.cpp',repo/'src/core/config_rgb_target_validation.cpp',repo/'config/glyph/common/src/glyph_config_validation.cpp']
 for p in cpp+cs:
  if not p.exists():raise FileNotFoundError(p)
 binary=out/'package-fault-harness';run([cxx,'-std=c++17',*flags,*args,*cpp,*objects,'-o',binary])
 files=set(cpp+cs+[version_header,repo/'HAL/pico/src/core/ProfileStore.cpp',repo/'HAL/pico/src/core/ProfileStorePackage.inc'])
 files.update(here.glob('*.py'))
 for base in [repo/'include/core',repo/'HAL/pico/include/core',schema,gen,nanopb,fw/'lib/littlefs']:
  files.update(p for p in base.glob('*') if p.is_file() and p.suffix in {'.h','.hpp','.proto','.options','.inc'})
 manifest={str(p.relative_to(repo)) if p.is_relative_to(repo) else str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
 fingerprint=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
 (out/'source-manifest.json').write_text(json.dumps({'fingerprint':fingerprint,'files':manifest,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'sanitizers':sanitize,'python_version':sys.version,'compiler':subprocess.check_output([cxx,'--version'],text=True),'framework':str(framework),'nanopb':str(nanopb)},indent=2)+'\n')
 return binary
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--framework',type=Path);ap.add_argument('--nanopb',type=Path);ap.add_argument('--no-sanitize',action='store_true');a=ap.parse_args()
 print(build(a.repo,a.out,a.framework,a.nanopb,not a.no_sanitize))
