#!/usr/bin/env python3
"""Recompile actual committed-build commands for RAM ABI and per-function frames.

This is evidence collection, not a final firmware build or whole-target proof.
Run only after the calling integration role has generated a current compiledb.
The ELF must be the exact candidate artifact supplied by that role.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
ROOT=Path(__file__).resolve().parents[1]
PATTERNS=('ProfileStore.cpp','CheckedStorage.cpp','Persistence.cpp','ConfiguratorBackend.cpp',
 'ResourceDiagnostics.cpp','RecoveryStartupDiagnostics.cpp','RecoveryUsbDiagnostics.cpp','mode_selection.cpp','config/glyph/common/src/config.cpp',
 '/display/','/comms/','/main.cpp','/FS.cpp','LittleFS/src/','RP2040Support.cpp',
 'malloc-lock.cpp','/runtime.c','pb_encode.c','pb_decode.c','pb_common.c',
 'config_validation.cpp','/Print.cpp','/Stream.cpp','/usbd.c','/cdc_device.c',
 '/tusb.c','/tusb_fifo.c','/dcd_rp2040.c','/Adafruit_TinyUSB_API.cpp',
 '/Adafruit_TinyUSB_rp2040.cpp','/Adafruit_USBD_CDC.cpp','/Adafruit_USBD_Device.cpp','/delay.cpp','/rp2040_usb.c','/usbd_control.c')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args,cwd=ROOT):
 p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,timeout=120)
 if p.returncode:raise RuntimeError(' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
 return p.stdout

def measure(db:Path,elf:Path,out:Path,baseline_ref=None):
 entries=json.loads(db.read_text());selected=[e for e in entries if any(p in e['file'] for p in PATTERNS)]
 assert selected,'No resource-relevant compilation database entries'
 out.mkdir(parents=True,exist_ok=True)
 elf_hash=sha(elf)
 backend_headers={str(path):sha(path) for path in (ROOT/'HAL/pico/include/comms/ConfiguratorBackend.hpp',ROOT/'HAL/pico/include/comms/CoordinatedCdcStream.hpp',ROOT/'include/core/ProfileStoreRxDiagnostics.hpp',ROOT/'include/core/CommunicationBackend.hpp')}
 def compile_one(pair):
  index,e=pair;source=Path(e['file']);source=source if source.is_absolute() else Path(e.get('directory',ROOT))/source
  source_hash=sha(source)
  args=e.get('arguments') or shlex.split(e['command']);args=list(args)
  target=out/(str(index)+'-'+source.name+'.o');args[args.index('-o')+1]=str(target)
  args.extend(['-fstack-usage','-fdump-ipa-cgraph'])
  # The appended probes are compiled only into this isolated analysis object;
  # they never enter a candidate binary or alter repository source.
  if source.name=='ProfileStore.cpp':
   copy=out/'ProfileStore.layout.cpp'
   copy.write_text(source.read_text()+'''\nextern "C" {
char glyph_layout_Config[sizeof(Config)];
char glyph_layout_UltimateProfile[sizeof(UltimateProfile)];
char glyph_layout_ProfileStore[sizeof(ProfileStore)];
char glyph_layout_Directory[sizeof(ProfileStore::Directory)];
char glyph_layout_Entry[sizeof(ProfileStore::Entry)];
char glyph_layout_ProfileStoreRequest[sizeof(ProfileStoreRequest)];
char glyph_layout_ProfileStoreResponse[sizeof(ProfileStoreResponse)];
char glyph_layout_TransactionIdentity[sizeof(ProfileStore::TransactionIdentity)];
}\n''')
   source_arg=next(i for i,a in enumerate(args) if a==e['file'] or Path(a)==source)
   args[source_arg]=str(copy)
  elif source.name=='ConfiguratorBackend.cpp':
   copy=out/'ConfiguratorBackend.layout.cpp'
   copy.write_text(source.read_text()+'''\nextern "C" {
char glyph_layout_CoordinatedCdcStream[sizeof(CoordinatedCdcStream)];
char glyph_layout_ConfiguratorBackend[sizeof(ConfiguratorBackend)];
char glyph_layout_ProfileStoreRxDiagnostics[sizeof(ProfileStoreRxDiagnostics)];
}\n''')
   source_arg=next(i for i,a in enumerate(args) if a==e['file'] or Path(a)==source)
   args[source_arg]=str(copy)
  result=subprocess.run(args,cwd=e.get('directory',ROOT),text=True,capture_output=True,timeout=120)
  (target.with_suffix('.log')).write_text(result.stdout+result.stderr)
  if result.returncode:raise RuntimeError(source.name+' resource compile failed\n'+result.stderr)
  assert sha(source)==source_hash,'Source changed during resource compile: '+str(source)
  return {'file':str(source),'sha256':source_hash,'object':str(target),'compiler':args[0]}
 with ThreadPoolExecutor(max_workers=4) as pool:compiled=list(pool.map(compile_one,enumerate(selected)))
 compiler=Path(compiled[0]['compiler']);nm=compiler.with_name('arm-none-eabi-nm');size=compiler.with_name('arm-none-eabi-size')
 layouts={}
 for obj in compiled:
  if Path(obj['file']).name in ('ProfileStore.cpp','ConfiguratorBackend.cpp'):
   for line in run([str(nm),'-S',obj['object']]).splitlines():
    m=re.match(r'\w+ (\w+) \w glyph_layout_(\w+)$',line)
    if m:layouts[m[2]]=int(m[1],16)
 baseline=None
 if baseline_ref:
  baseline_dir=out/'baseline-backend-abi';overlay=baseline_dir/'include/comms';overlay.mkdir(parents=True,exist_ok=True)
  frozen={}
  for relative in ('HAL/pico/include/comms/ConfiguratorBackend.hpp','HAL/pico/include/comms/CoordinatedCdcStream.hpp','HAL/pico/src/comms/ConfiguratorBackend.cpp'):
   text=run(['git','show',baseline_ref+':'+relative]);frozen[relative]=hashlib.sha256(text.encode()).hexdigest()
   destination=(overlay/Path(relative).name) if relative.endswith('.hpp') else baseline_dir/'ConfiguratorBackend.layout.cpp'
   destination.write_text(text)
  source=baseline_dir/'ConfiguratorBackend.layout.cpp'
  source.write_text(source.read_text()+'''\nextern "C" {
char glyph_layout_CoordinatedCdcStream[sizeof(CoordinatedCdcStream)];
char glyph_layout_ConfiguratorBackend[sizeof(ConfiguratorBackend)];
}\n''')
  entry=next(e for e in selected if Path(e['file']).name=='ConfiguratorBackend.cpp')
  args=list(entry.get('arguments') or shlex.split(entry['command']))
  original=Path(entry['file']);original=original if original.is_absolute() else Path(entry.get('directory',ROOT))/original
  index=next(i for i,value in enumerate(args) if value==entry['file'] or Path(value)==original)
  args[index]=str(source);obj=baseline_dir/'backend.o';args[args.index('-o')+1]=str(obj)
  args[1:1]=['-I'+str(baseline_dir/'include')]
  result=subprocess.run(args,cwd=entry.get('directory',ROOT),text=True,capture_output=True,timeout=120)
  (baseline_dir/'compile.log').write_text(result.stdout+result.stderr)
  if result.returncode:raise RuntimeError('Frozen backend ABI compile failed\n'+result.stderr)
  old_layouts={}
  for line in run([str(nm),'-S',str(obj)]).splitlines():
   match=re.match(r'\w+ (\w+) \w glyph_layout_(\w+)$',line)
   if match:old_layouts[match[2]]=int(match[1],16)
  assert set(old_layouts)=={'CoordinatedCdcStream','ConfiguratorBackend'}
  baseline={'ref':baseline_ref,'frozen_sources':frozen,'abi_sizes':old_layouts,
   'delta_current_bytes':{name:layouts[name]-amount for name,amount in old_layouts.items()},
   'object':str(obj),'compile_command':args,
   'scope':'Frozen backend/stream headers and TU; same target compiler and current common dependencies. Backend does not embed protocol response/request structs. Not a frozen firmware rebuild or frozen stack measurement.'}
 frames=[]
 for file in out.glob('*.su'):
  for line in file.read_text().splitlines():
   function,amount,kind=line.rsplit('\t',2);frames.append({'function':function,'bytes':int(amount),'kind':kind})
 symbols=run([str(nm),'-S','--size-sort','-C',str(elf)]);(out/'candidate-symbols.txt').write_text(symbols)
 sections=run([str(size),'-A',str(elf)]);(out/'candidate-sections.txt').write_text(sections)
 bounds={}
 for line in run([str(nm),str(elf)]).splitlines():
  m=re.match(r'(\w+) \w (__Stack(?:Limit|Top|Bottom|OneTop|OneBottom)|__bss_end__|__end__)$',line)
  if m:bounds[m[2]]=int(m[1],16)
 assert sha(elf)==elf_hash,'Candidate ELF changed during collection'
 assert all(sha(Path(path))==digest for path,digest in backend_headers.items()),'Backend ABI header changed during collection'
 report={'candidate_elf':str(elf),'candidate_elf_sha256':elf_hash,'compile_database_sha256':sha(db),
  'compiler':str(compiler),'compiler_sha256':sha(compiler),'sources':compiled,
  'abi_sizes':layouts,'backend_layout_headers':backend_headers,'baseline_backend_abi':baseline,'stack_heap_linker_symbols':bounds,'frames':sorted(frames,key=lambda r:r['bytes'],reverse=True),
  'static_sections':sections,'protocol_frame_bytes':8192,
  'active_profile_bytes':layouts.get('UltimateProfile'),'candidate_profile_bytes':layouts.get('UltimateProfile'),
  'whole_target_stack_bound':'NOT CLAIMED: per-function frames omit composed IRQ/ROM/indirect/runtime paths',
  'runtime_measurements':'Required exact diagnostic artifact STATUS samples: percore watermark min free and complete heap arena peak/current/capacity',
  'heap_peak_interpretation':'SDK sbrk arena highwater bounds reserved allocator memory, including transient demand; not live malloc occupancy',
  'startup_stack_limitation':'Watermarks start at each setup entry; pre-setup startup frames require static evidence and remain outside sampled lifetime'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('sources','frames','static_sections')},indent=2))
 print('glyph_profile_store_resources=COLLECTED; candidate identity and hardware sufficiency remain integration/owner gates')
def main():
 p=argparse.ArgumentParser();p.add_argument('--compile-db',type=Path,default=ROOT/'compile_commands.json');p.add_argument('--elf',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--baseline-ref',help='Optional Git revision for isolated frozen backend/stream target ABI probes');a=p.parse_args();measure(a.compile_db.resolve(),a.elf.resolve(),a.output_dir.resolve(),a.baseline_ref)
if __name__=='__main__':main()
