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
PATTERNS = ['NativeTargetMetrics.cpp', 'UltimateNativeProfile.cpp', 'UltimateNativeEvaluator.cpp', '/Ultimate.cpp', 'ControllerMode.cpp', 'InputMode.cpp', 'CommunicationBackend.cpp', 'mode_selection.cpp', 'XInputBackend.cpp', 'SwitchBackend.cpp', 'GameCubeBackend.cpp', 'ConfiguratorBackend.cpp', 'ProfileStore.cpp', 'CheckedStorage.cpp', 'Persistence.cpp', '/FS.cpp', 'LittleFS/src/',
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
 if not any(e['file'].endswith('NativeTargetMetrics.cpp') for e in selected):
  original=next(e for e in entries if e['file'].endswith('/ProfileStore.cpp'))
  selected.append({**original,'file':'HAL/pico/src/core/NativeTargetMetrics.cpp','command':original['command'].replace(original['file'],'HAL/pico/src/core/NativeTargetMetrics.cpp')})
 # Analysis objects use the same constant/layout/code path as the clean builder.
 # They are source-pinned object evidence, never an accepted firmware artifact.
 analysis_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 values=','.join('0x'+analysis_sha[i:i+2] for i in range(0,40,2))
 (generated/'native_target_source.hpp').write_text('#pragma once\n#include <cstdint>\nconstexpr uint8_t kNativeTargetSourceSha[20]={'+values+'};\nconstexpr uint16_t kNativeTargetSourceFlags=3;\n')
 def compile_one(e):
  name=e['file'].replace('/','_').replace('.','_'); target=out/(name+'.o')
  args=shlex.split(e['command']);args[args.index('-o')+1]=str(target)
  args[1:1]=['-I',str(generated),'-DGLYPH_NATIVE_TARGET_METRICS=1']
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
  'ProfileStore::Create(const UltimateProfile&, const char*, uint32_t, const TransactionIdentity&)':256,'ProfileStore::PrepareProfileWrite(':256,'ProfileStore::PublishPreparedProfile(':128,'ProfileStore::PublishDirectory(':256,
  'ProfileStore::Duplicate(uint32_t, uint32_t, const char*, uint32_t, const TransactionIdentity&)':128,':void setup()':512,
  'Persistence::LoadConfigChecked(':512,'Persistence::SaveConfigIfGenerationMatches(':512,
  'Persistence::SaveConfig(':512,'ProfileStore::Begin(':512,'ProfileStore::BeginRecovery(':512,
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
 prefix_names=[':int main()',':void loop()','ConfiguratorBackend::SendReport()',
               'ConfiguratorBackend::HandleProfileStore()','ConfiguratorBackend::DispatchProfileStore()']
 measured_main=size(':int main()')
 # Exact ea137 linked main retained48. Charge at least that until the
 # refreshed exact ELF confirms current main/loop/caller composition.
 main_charge=max(48,measured_main)
 prefix=sum(size(x) for x in prefix_names)+main_charge-measured_main
 # Actual ordinary file16 compaction witness: forceconsistency/deorphan are
 # separate conditional work, not frames retained in this ordinary branch.
 # Open is out-of-line in the new MountedStorage adapter; WriteFile is absent.
 leaf_names=[':lfs_file_open',':lfs_file_rawopencfg',':lfs_dir_orphaningcommit',
  ':lfs_dir_relocatingcommit',':lfs_dir_splittingcompact',':lfs_dir_compact',
  ':lfs_dir_traverse.constprop',':lfs_dir_commit_commit',':lfs_dir_commitprog',
  'LittleFSImpl::lfs_flash_prog(']
 leaf=sum(size(x) for x in leaf_names)
 adapter=size('MountedStorage::CheckedWrite(')+size('CheckedStorage::Open(')
 create=size('ProfileStore::Create(const UltimateProfile&, const char*, uint32_t, const TransactionIdentity&)')
 record=prefix+create+size('ProfileStore::PublishPreparedProfile(')+adapter+leaf
 directory=prefix+create+size('ProfileStore::FinalizePreparedCreate(')+size('ProfileStore::PublishDirectory(')+adapter+leaf
 boot=main_charge+size(':void setup()')+size('ProfileStore::Begin(')+adapter+leaf
 conditional=sum(size(x) for x in [':lfs_fs_forceconsistency',':lfs_fs_deorphan'])
 # Independently reviewed exactfc source/ELF feasible lower-bound IRQ paths.
 # These are NOT a whole-IRQ upper certificate. Native final ELF must recheck.
 irq_known={'default_serial_plus_nested_SysTick':300,'direct_CDC_claim_plus_nested_SysTick':316,
            'pending_TX_flush_plus_nested_SysTick':340}
 reserve=2048; pre_mask_helper=16; exception_alignment_allowance=8
 move=size(':lfs_fs_forceconsistency')
 duplicate=size('ProfileStore::Duplicate(uint32_t, uint32_t, const char*, uint32_t, const TransactionIdentity&)')
 update=size('ProfileStore::Update(uint32_t, const UltimateProfile&, uint32_t, const TransactionIdentity&)')
 branches={'record_new_entry_compaction':record,'directory_control_new_entry_compaction':directory,
           'duplicate_record_pending_MOVE':record+duplicate+move,
           'duplicate_directory_after_record_MOVE_cleared':directory+duplicate,
           'update_record_pending_MOVE':prefix+update+size('ProfileStore::PublishPreparedProfile(')+adapter+leaf+move,
           'startup_new_entry_compaction':boot}
 for name,signature in [('rename','ProfileStore::Rename(uint32_t, const char*, uint32_t, const TransactionIdentity&)'),
                         ('reorder','ProfileStore::Reorder(uint32_t, uint32_t, uint32_t, const TransactionIdentity&)'),
                         ('delete','ProfileStore::Delete(uint32_t, uint32_t, uint32_t, const TransactionIdentity&)')]:
  branches[name+'_directory_pending_MOVE']=prefix+size(signature)+size('ProfileStore::PublishDirectory(')+adapter+leaf+move
 known_composition={}
 for name,foreground in branches.items():
  irq=irq_known['default_serial_plus_nested_SysTick'] if name.startswith('startup') else max(irq_known.values())
  # Endpoint-mutex contention is a separate source-conditional branch. Retain
  # its44-byte allowance here unless final review proves it cannot coexist.
  contention=0 if name.startswith('startup') else 44
  known_composition[name]={'foreground_bytes':foreground,'known_irq_increment_bytes':irq,
   'conditional_endpoint_mutex_contention_bytes_charged':contention,
   'pre_mask_helper_bytes':pre_mask_helper,'exception_alignment_allowance_bytes':exception_alignment_allowance,
   'known_composed_bytes':foreground+irq+contention+pre_mask_helper+exception_alignment_allowance,
   'remaining_reserved_bytes_before_unknown_paths':reserve-foreground-irq-contention-pre_mask_helper-exception_alignment_allowance}
 known_fit=all(row['known_composed_bytes']<=reserve for row in known_composition.values())
 # Schema maximum depth is four (Request/Profile/OutputProgram/Effect or
 # Request/Profile/Table/Coords). Parent and child frames coexist; arrays
 # iterate, not recurse. This intentionally overcounts mutually exclusive
 # substream helpers to provide an enumerated decoder C envelope.
 decoder=prefix+4*sum(size(x) for x in [':pb_decode_inner',':decode_field',':decode_basic_field',':pb_close_string_substream',':pb_make_string_substream'])+sum(next(r['bytes'] for r in rows if r['function'].endswith(':'+name)) for name in ['pb_decode','pb_read','pb_decode_varint'])
 compiler=pathlib.Path(shlex.split(selected[0]['command'])[0])
 report={'analysis_only_source_label_head':analysis_sha,'compiler':str(compiler),'compiler_sha256':hashlib.sha256(compiler.read_bytes()).hexdigest(),
  'optimization':'production compiledb flags, O3 project/LittleFS; no LTO',
  'frames':rows,'critical_limits':limits,'critical_measured_bytes':measured,'prefix_bytes':prefix,'preliminary_main_frame_bytes':measured_main,'main_charged_bytes':main_charge,'main_charge_basis':'max(preliminary object, exact ea137 ELF48); refresh against new exact ELF',
  'known_foreground_branches_bytes':branches,'known_compositions':known_composition,
  'known_compositions_within_reserved2048':known_fit,
  'ordinary_compaction_retained_function_sequence':prefix_names+['ProfileStore::Create','ProfileStore::PublishPreparedProfile',
   'MountedStorage::CheckedWrite','CheckedStorage::Open']+leaf_names,
  'littlefs_ordinary_open_chain_bytes':leaf,
  'conditional_forceconsistency_deorphan_inventory_bytes':conditional,
  'conditional_inventory_classification':'MOVE64 charged in named feasible branches; deorphan176 remains CONDITIONAL_UNEXCLUDED for arbitrary accepted pre-existing FS; no whole-bound PASS',
  'unexcluded_deorphan_inventory_bytes':size(':lfs_fs_deorphan'),
  'unexcluded_deorphan_plus_worst_record_composition_bytes':known_composition['duplicate_record_pending_MOVE']['known_composed_bytes']+size(':lfs_fs_deorphan'),
  'physical_scratch_bank_bytes':4096,'physical_scratch_bank_is_stack_budget':False,
  'adapter':'fixed synchronous MountedStorage File; CheckedStorage::Open retained; WriteFile absent; Publish/control/Commit inlined as emitted',
  'request_decode_enumerated_C_upper_bytes':decoder,
  'default_reservation_bytes':2048,
  'whole_target_upper_bound':'UNKNOWN: SDK/ROM, IRQ and unresolved indirect paths are not certified by this report',
  'object_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.o')},
  'source_sha256':{e['file']:hashlib.sha256((ROOT/e['file']).read_bytes()).hexdigest() for e in selected}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('glyph_profile_store_create_stack: '+('KNOWN_PATHS_WITHIN_RESERVED_STACK_WHOLE_BOUND_UNKNOWN' if known_fit else 'FAIL_KNOWN_RESERVED_STACK_PATH'))
 print(json.dumps({k:v for k,v in report.items() if k not in ['frames','source_sha256','critical_limits']},indent=2))
 if not known_fit:raise AssertionError('concrete known composition exceeds reserved2048; no resource PASS')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=pathlib.Path);parser.add_argument('--compiledb',type=pathlib.Path);args=parser.parse_args()
 if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=True);measure(args.output_dir,args.compiledb)
 else:
  with tempfile.TemporaryDirectory(prefix='glyph-create-stack-') as d:measure(pathlib.Path(d),args.compiledb)
if __name__=='__main__':main()
