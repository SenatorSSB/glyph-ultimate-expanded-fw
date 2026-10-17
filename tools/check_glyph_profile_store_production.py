#!/usr/bin/env python3
"""Production composition/linked retirement gates; never opens a device."""
from pathlib import Path
import argparse,hashlib,json,re,shlex,subprocess
ROOT=Path(__file__).resolve().parents[1]
RETIRED=('RecoveryStartupDiagnostics','RecoveryUsbDiagnostics','RecoveryTaskDiagnostics','RecoveryPreSetupDiagnostics','RecoveryPrivateDcd','RecoverySetupIrq','GlyphColdRecovery','TinyUSB_Device_Init_cold','GlyphRecoveryUsbReinitialize','ProfileStoreFaultControls::','ProfileStoreReadTrace::Get','ProfileStoreReadTrace::Scope','ConfiguratorBackend::TraceProfileStage','ConfiguratorBackend::PrepareProfileMutation','CheckedStorage::SetFaultHook','CheckedStorage::(anonymous namespace)::faults','__wrap__sbrk','__wrap_panic','__wrap_hw_endpoint_xfer_continue','__wrap_dcd_event_handler')
def source_policy(env,config):
 section=env.split('[env:glyph_mk6]',1)[1].split('\n[',1)[0]
 assert not re.search(r'GLYPH_(STRICT_HARDENING_CANDIDATE|RESOURCE_DIAGNOSTICS|RT2_)\s*=\s*1|--wrap|rt2_.*\.py',section),'acceptance flag/wrapper/builder enabled'
 assert 'inputs.rt2 && !inputs.mb1' not in config and 'GlyphColdRecovery' not in config,'manual RT2 experiment compiled'
 assert 'initialize_recovery(' in config and 'if (inputs.mb1)' in config,'automatic recovery or MB1 removed'
def symbol_policy(symbols):
 assert not any(s in symbols for s in RETIRED),'retired implementation symbol linked'
def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path);p.add_argument('--compile-db',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 env=(ROOT/'config/glyph/env.ini').read_text();cfg=(ROOT/'config/glyph/common/src/config.cpp').read_text();source_policy(env,cfg)
 controls=0
 for badenv,badcfg in [(env.replace('extends = glyph_base','extends = glyph_base',1).replace('[env:glyph_mk6]\nextends = glyph_base','[env:glyph_mk6]\nextends = glyph_base\nbuild_flags = -D GLYPH_STRICT_HARDENING_CANDIDATE=1'),cfg),(env.replace('[env:glyph_mk6]\nextends = glyph_base','[env:glyph_mk6]\nextends = glyph_base\nextra_scripts = pre:builder_scripts/rt2_private_dcd.py'),cfg),(env,cfg+'\nif (inputs.rt2 && !inputs.mb1) {}')]:
  try:source_policy(badenv,badcfg)
  except AssertionError:controls+=1
  else:raise AssertionError('retirement source negative escaped')
 try:symbol_policy('void GlyphColdRecoveryStart()')
 except AssertionError:controls+=1
 else:raise AssertionError('linked symbol negative escaped')
 report={'status':'PASS_SOURCE_COMPOSITION','negative_controls':controls,'source_sha256':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in ['config/glyph/env.ini','config/glyph/common/src/config.cpp','HAL/pico/src/comms/ConfiguratorBackend.cpp','include/core/ProfileStoreFaultControls.hpp','include/core/ProfileStoreReadTrace.hpp','HAL/pico/src/core/CheckedStorage.cpp']},'hardware':'NOT_TESTED','underlying_RT2_cause':'UNRESOLVED'}
 if a.elf:
  nm=Path.home()/'.platformio/packages/toolchain-rp2040-earlephilhower/bin/arm-none-eabi-nm';symbols=subprocess.check_output([str(nm),'-C',str(a.elf)],text=True);symbol_policy(symbols)
  assert len(re.findall(r'^[0-9a-f]+ [TW] dcd_init$',symbols,re.M))==1,'not one ordinary DCD definition'
  assert len(re.findall(r'^[0-9a-f]+ W TinyUSB_Device_Init$',symbols,re.M))==1,'ordinary pinned weak TinyUSB init not selected'
  report.update(status='PASS_SOURCE_AND_ELF_COMPOSITION',elf_sha256=hashlib.sha256(a.elf.read_bytes()).hexdigest(),retired_symbols='ABSENT',ordinary_DCD='ONE',ordinary_TinyUSB_init='WEAK_ORIGINAL')
 if a.compile_db:
  entries=json.loads(a.compile_db.read_text());commands=[e.get('arguments') or shlex.split(e['command']) for e in entries]
  assert not any('GLYPH_STRICT_HARDENING_CANDIDATE=1' in x or 'GLYPH_RESOURCE_DIAGNOSTICS=1' in x or '--wrap' in x for cmd in commands for x in cmd),'acceptance flags in actual build'
  dcd=[e for e in entries if e['file'].endswith('/dcd_rp2040.c')];assert len(dcd)==1 and 'framework-arduinopico' in dcd[0]['file'],'private DCD replacement active'
  report['compile_database_sha256']=hashlib.sha256(a.compile_db.read_bytes()).hexdigest();report['dcd_source']=dcd[0]['file'];report['compiled_commands']=len(entries)
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
