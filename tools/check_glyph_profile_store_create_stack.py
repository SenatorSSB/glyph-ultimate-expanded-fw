#!/usr/bin/env python3
"""Measure actual production translation units, not a surrogate callback.

Run pio run -e glyph_mk6 -t compiledb first. Extra compiler outputs go only to
--output-dir (or a temporary directory). The report distinguishes enumerated
C call chains from an UNKNOWN whole-target/IRQ/ROM bound.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, pathlib, re, shlex, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERNS = ['ConfiguratorBackend.cpp', 'ProfileStore.cpp', 'Persistence.cpp', '/FS.cpp', 'LittleFS/src/',
 'RP2040Support.cpp', '/main.cpp', '/pb_encode.c', '/pb_decode.c', '/pb_common.c',
 'nanopb-arduino/src/', 'config/glyph/common/src/config.cpp', 'Adafruit_USBD_CDC.cpp',
 '/usbd.c', '/cdc_device.c', '/tusb.c', '/tusb_fifo.c', '/dcd_rp2040.c',
 'config_validation.cpp', '/Print.cpp', '/Stream.cpp']

def measure(out):
 entries=json.loads((ROOT/'compile_commands.json').read_text())
 selected=[e for e in entries if any(p in e['file'] for p in PATTERNS)]
 def compile_one(e):
  name=e['file'].replace('/','_').replace('.','_'); target=out/(name+'.o')
  args=shlex.split(e['command']);args[args.index('-o')+1]=str(target)
  args+=['-fstack-usage','-fdump-ipa-cgraph']
  result=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,timeout=90)
  (out/(name+'.log')).write_text(result.stdout+result.stderr)
  if result.returncode: raise RuntimeError(result.stderr)
  return e['file']
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(compile_one,selected))
 rows=[]
 for f in sorted(out.glob('*.su')):
  for line in f.read_text().splitlines():
   location,amount,kind=line.rsplit('\t',2);rows.append({'function':location,'bytes':int(amount),'kind':kind})
 def size(needle):
  found=[r['bytes'] for r in rows if needle in r['function']]
  if not found:raise AssertionError('missing production stack row: '+needle)
  return max(found)
 limits={'ConfiguratorBackend::HandleProfileStore()':512,'ConfiguratorBackend::WriteProfilePacket(':512,
  'ProfileStore::Create(':256,'ProfileStore::WriteProfile(':512,'ProfileStore::PublishDirectory(':256,
  'ProfileStore::Duplicate(':128,':void setup()':512,
  'Persistence::LoadConfigChecked(':512,'Persistence::SaveConfigIfGenerationMatches(':512,
  'Persistence::SaveConfig(':512}
 for name,limit in limits.items():
  if size(name)>limit:raise AssertionError(f'{name}: {size(name)} > {limit}')
 prefix=size(':int main()')+size(':void loop()')+size('ConfiguratorBackend::SendReport()')+size('ConfiguratorBackend::HandleProfileStore()')
 # Direct calls verified by relocations in the pinned O3 object; the traverse
 # callback is lfs_dir_commit_commit. Inlined bd_prog/flush are NOT added again.
 leaf_names=[':lfs_file_open',':lfs_file_rawopencfg',':lfs_fs_forceconsistency',':lfs_fs_deorphan',
  ':lfs_dir_orphaningcommit',':lfs_dir_relocatingcommit',':lfs_dir_splittingcompact',
  ':lfs_dir_compact',':lfs_dir_traverse.constprop',':lfs_dir_commit_commit',':lfs_dir_commitprog']
 leaf=sum(size(x) for x in leaf_names)
 root_open=prefix+size('ProfileStore::Create(')+size('ProfileStore::WriteProfile(')+size('LittleFsDirectoryStorage::Write(')+size('fs::FS::open(const char*')+size('littlefs_impl::LittleFSImpl::open(')+leaf+size('LittleFSImpl::lfs_flash_prog(')
 # Schema maximum depth is four (Request/Profile/OutputProgram/Effect or
 # Request/Profile/Table/Coords). Parent and child frames coexist; arrays
 # iterate, not recurse. This intentionally overcounts mutually exclusive
 # substream helpers to provide an enumerated decoder C envelope.
 decoder=prefix+4*sum(size(x) for x in [':pb_decode_inner',':decode_field',':decode_basic_field',':pb_close_string_substream',':pb_make_string_substream'])+sum(next(r['bytes'] for r in rows if r['function'].endswith(':'+name)) for name in ['pb_decode','pb_read','pb_decode_varint'])
 compiler=pathlib.Path(shlex.split(selected[0]['command'])[0])
 report={'compiler':str(compiler),'compiler_sha256':hashlib.sha256(compiler.read_bytes()).hexdigest(),
  'optimization':'production compiledb flags, O3 project/LittleFS; no LTO',
  'frames':rows,'critical_limits':limits,'prefix_bytes':prefix,
  'record_open_reachable_chain_bytes':root_open,'littlefs_open_chain_bytes':leaf,
  'request_decode_enumerated_C_upper_bytes':decoder,
  'default_reservation_bytes':2048,'ordinary_scratch_bank_envelope_bytes':4096,
  'whole_target_upper_bound':'UNKNOWN: SDK/ROM, IRQ and unresolved indirect paths are not certified by this report',
  'source_sha256':{e['file']:hashlib.sha256((ROOT/e['file']).read_bytes()).hexdigest() for e in selected}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('glyph_profile_store_create_stack: PASS')
 print(json.dumps({k:v for k,v in report.items() if k not in ['frames','source_sha256','critical_limits']},indent=2))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=pathlib.Path);args=parser.parse_args()
 if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=True);measure(args.output_dir)
 else:
  with tempfile.TemporaryDirectory(prefix='glyph-create-stack-') as d:measure(pathlib.Path(d))
if __name__=='__main__':main()
