#!/usr/bin/env python3
"""Measure actual production translation units, not a surrogate callback.

Run pio run -e glyph_mk6 -t compiledb first. Extra compiler outputs go only to
--output-dir (or a temporary directory). The report distinguishes enumerated
C call chains from an UNKNOWN whole-target/IRQ/ROM bound.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, pathlib, re, shlex, subprocess, tempfile, os, sys
from check_glyph_stage_b_ultimate_profiles import NANOPB
ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERNS = ['UltimateNativeProfile.cpp', 'UltimateNativeEvaluator.cpp', '/Ultimate.cpp', 'ControllerMode.cpp', 'InputMode.cpp', 'CommunicationBackend.cpp', 'mode_selection.cpp', 'XInputBackend.cpp', 'SwitchBackend.cpp', 'GameCubeBackend.cpp', 'ConfiguratorBackend.cpp', 'ProfileStore.cpp', 'CheckedStorage.cpp', 'Persistence.cpp', '/FS.cpp', 'LittleFS/src/',
 'RP2040Support.cpp', '/main.cpp', '/pb_encode.c', '/pb_decode.c', '/pb_common.c',
 'nanopb-arduino/src/', 'config/glyph/common/src/config.cpp', 'Adafruit_USBD_CDC.cpp',
 '/usbd.c', '/cdc_device.c', '/tusb.c', '/tusb_fifo.c', '/dcd_rp2040.c',
 'config_validation.cpp', '/Print.cpp', '/Stream.cpp', 'Adafruit_TinyUSB_rp2040.cpp', 'Adafruit_USBD_Device.cpp', '/usbd_control.c']

def measure(out, compiledb=None):
 # Regenerate current schema into isolated evidence output: a source-side
 # frame check must not silently compile against a stale preliminary header.
 generated=out/'generated';generated.mkdir(exist_ok=True)
 nanopb=pathlib.Path(os.environ.get('GLYPH_PROFILE_STORE_NANOPB',str(NANOPB)))
 schema=ROOT/'schema/haybox'
 subprocess.run([sys.executable,str(nanopb/'generator/nanopb_generator.py'),'-I',str(schema),'-f',str(schema/'config.options'),'--error-on-unmatched','--no-timestamp','-D',str(generated),str(schema/'config.proto')],check=True,capture_output=True)
 entries=json.loads((compiledb or ROOT/'compile_commands.json').read_text())
 selected=[e for e in entries if any(p in e['file'] for p in PATTERNS)]
 def compile_one(e):
  name=e['file'].replace('/','_').replace('.','_'); target=out/(name+'.o')
  args=shlex.split(e['command']);args[args.index('-o')+1]=str(target)
  args[1:1]=['-I',str(generated)]
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
  'ProfileStore::Create(const UltimateProfile&, const char*, uint32_t, const TransactionIdentity&)':256,'ProfileStore::WriteProfile(':512,'ProfileStore::PublishDirectory(':256,
  'ProfileStore::Duplicate(uint32_t, uint32_t, const char*, uint32_t, const TransactionIdentity&)':128,':void setup()':512,
  'Persistence::LoadConfigChecked(':512,'Persistence::SaveConfigIfGenerationMatches(':512,
  'Persistence::SaveConfig(':512,'ProfileStore::Bootstrap(':512,
  'Persistence::CaptureLegacySource(':768,'CheckedStorage::Open(':128,
  'CheckedStorage::WriteFile(':256,'CheckedStorage::ReadFile(':256}
 # GCC may split a function into a public wrapper and a part.0 implementation
 # whose .su name is only "0(Config&)". Both retain the same source coordinate.
 # Include all such frames so a tiny wrapper cannot hide a large load body.
 measured={}
 for name,limit in limits.items():
  definitions={':'.join(r['function'].split(':',3)[:3]) for r in rows if name in r['function']}
  if not definitions:raise AssertionError('missing production stack row: '+name)
  measured[name]=sum(r['bytes'] for r in rows if ':'.join(r['function'].split(':',3)[:3]) in definitions)
  if measured[name]>limit:raise AssertionError(f'{name}: {measured[name]} > {limit}')
 prefix=size(':int main()')+size(':void loop()')+size('ConfiguratorBackend::SendReport()')+size('ConfiguratorBackend::HandleProfileStore()')
 # Direct calls verified by relocations in the pinned O3 object; the traverse
 # callback is lfs_dir_commit_commit. Inlined bd_prog/flush are NOT added again.
 leaf_names=[':lfs_file_open',':lfs_file_rawopencfg',':lfs_fs_forceconsistency',':lfs_fs_deorphan',
  ':lfs_dir_orphaningcommit',':lfs_dir_relocatingcommit',':lfs_dir_splittingcompact',
  ':lfs_dir_compact',':lfs_dir_traverse.constprop',':lfs_dir_commit_commit',':lfs_dir_commitprog']
 leaf=sum(size(x) for x in leaf_names)
 # Format-v2 production uses the repository-owned same-mount checked
 # primitive, preserving Arduino core/flash safety while bypassing unchecked
 # Arduino File handles. Publish is inlined into WriteProfile on this pin.
 root_open=prefix+size('ProfileStore::Create(const UltimateProfile&, const char*, uint32_t, const TransactionIdentity&)')+size('ProfileStore::WriteProfile(')+size('MountedStorage::CheckedWrite(')+size('CheckedStorage::WriteFile(')+size('CheckedStorage::Open(')+leaf+size('LittleFSImpl::lfs_flash_prog(')
 require_envelope=4096
 if root_open>require_envelope:raise AssertionError(f'enumerated checked record-open chain {root_open} exceeds scratch bank {require_envelope}')
 # Schema maximum depth is four (Request/Profile/OutputProgram/Effect or
 # Request/Profile/Table/Coords). Parent and child frames coexist; arrays
 # iterate, not recurse. This intentionally overcounts mutually exclusive
 # substream helpers to provide an enumerated decoder C envelope.
 decoder=prefix+4*sum(size(x) for x in [':pb_decode_inner',':decode_field',':decode_basic_field',':pb_close_string_substream',':pb_make_string_substream'])+sum(next(r['bytes'] for r in rows if r['function'].endswith(':'+name)) for name in ['pb_decode','pb_read','pb_decode_varint'])
 compiler=pathlib.Path(shlex.split(selected[0]['command'])[0])
 report={'compiler':str(compiler),'compiler_sha256':hashlib.sha256(compiler.read_bytes()).hexdigest(),
  'optimization':'production compiledb flags, O3 project/LittleFS; no LTO',
  'frames':rows,'critical_limits':limits,'critical_measured_bytes':measured,'prefix_bytes':prefix,
  'record_open_reachable_chain_bytes':root_open,'littlefs_open_chain_bytes':leaf,
  'record_open_scratch_bank_margin_before_unmodeled_paths':4096-root_open,
  'adapter':'repository-owned same-mounted CheckedStorage; Publish inlined into WriteProfile',
  'request_decode_enumerated_C_upper_bytes':decoder,
  'default_reservation_bytes':2048,'ordinary_scratch_bank_envelope_bytes':4096,
  'whole_target_upper_bound':'UNKNOWN: SDK/ROM, IRQ and unresolved indirect paths are not certified by this report',
  'source_sha256':{e['file']:hashlib.sha256((ROOT/e['file']).read_bytes()).hexdigest() for e in selected}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('glyph_profile_store_create_stack: PASS')
 print(json.dumps({k:v for k,v in report.items() if k not in ['frames','source_sha256','critical_limits']},indent=2))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=pathlib.Path);parser.add_argument('--compiledb',type=pathlib.Path);args=parser.parse_args()
 if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=True);measure(args.output_dir,args.compiledb)
 else:
  with tempfile.TemporaryDirectory(prefix='glyph-create-stack-') as d:measure(pathlib.Path(d),args.compiledb)
if __name__=='__main__':main()
