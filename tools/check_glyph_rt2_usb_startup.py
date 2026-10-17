#!/usr/bin/env python3
"""Pinned Adafruit descriptor/CDC + TinyUSB control events + actual recovery backend.

DCD bus and GPIO/PIO are explicit host models; never macOS/hardware acceptance.
Frozen2e0 is a positive falsification control for the late-CDC hypothesis.
"""
import argparse,hashlib,json,os,subprocess,sys,tempfile,shutil
from pathlib import Path
from check_glyph_stage_b_ultimate_profiles import ROOT,NANOPB,make_v3_artifact
from check_glyph_profile_store_littlefs_host import FRAMEWORK
import glyph_serial_config_tool as transport
HOST=ROOT/'tools/fixtures/rt2_usb_startup'
LEGACY=ROOT/'tools/fixtures/profile_store_timeout_host'
FROZEN='2e0a608622e8363ec7e2ef2aacc224e0810020ed'
def run(args,expected=0):
 p=subprocess.run(list(map(str,args)),cwd=ROOT,text=True,capture_output=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
 if (p.returncode==0)!=(expected==0):raise RuntimeError(' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
 return p.stdout+p.stderr

def function(text,signature):
 start=text.index(signature);end=text.index('{',start);depth=1;end+=1
 while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[start:end]

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path);ap.add_argument('--identity-matrix',action='store_true');a=ap.parse_args()
 frozen_ref='466f91ed867884640375627734d3473e9fb22c32' if a.identity_matrix else FROZEN
 try:
  usb=FRAMEWORK/'libraries/Adafruit_TinyUSB_Arduino/src';assert json.loads((FRAMEWORK/'package.json').read_text())['version']=='1.30603.0'
  device=(usb/'arduino/Adafruit_USBD_Device.cpp').read_text();begin=function(device[device.index('// Add interface descriptor'):],'bool Adafruit_USBD_Device::begin(uint8_t rhport)');assert begin.index('SerialTinyUSB.begin')<begin.index('TinyUSB_Port_InitDevice')
  results=[];sources=[usb/'arduino/Adafruit_USBD_Device.cpp',usb/'arduino/Adafruit_USBD_CDC.cpp',usb/'device/usbd.c',usb/'device/usbd_control.c',usb/'class/cdc/cdc_device.c',usb/'common/tusb_fifo.c',usb/'osal/osal_pico.h',FRAMEWORK/'cores/rp2040/main.cpp',usb/'arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp',ROOT/'config/glyph/common/src/config.cpp',ROOT/'HAL/pico/src/core/RecoveryStartupDiagnostics.cpp',ROOT/'include/core/RecoveryStartupDiagnostics.hpp']
  sources += [ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp',ROOT/'HAL/pico/include/comms/ConfiguratorBackend.hpp',ROOT/'tools/fixtures/rt2_usb_startup/startup.cpp',ROOT/'tools/fixtures/rt2_usb_startup/identity_matrix.inc',usb/'tusb_option.h',usb/'device/usbd.h',usb/'portable/raspberrypi/rp2040/dcd_rp2040.c',usb.parent/'library.properties',FRAMEWORK/'cores/rp2040/delay.cpp',ROOT/'platformio.ini',ROOT/'HAL/pico/include/tusb_config_pico.h',ROOT/'HAL/pico/src/comms/backend_init.cpp',ROOT/'HAL/pico/src/comms/XInputBackend.cpp',ROOT/'include/core/RecoveryInitialization.hpp',ROOT/'HAL/pico/src/core/Persistence.cpp',ROOT/'.pio/libdeps/glyph_mk6/FastLED/src/platforms/arm/rp2040/pio_gen.h']
  config=(ROOT/'HAL/pico/include/tusb_config_pico.h').read_text()
  import re
  for key,value in {'CDC':1,'MSC':1,'HID':1,'MIDI':1,'VENDOR':0,'CDC_RX_BUFSIZE':256,'CDC_TX_BUFSIZE':256,'MSC_EP_BUFSIZE':512,'HID_EP_BUFSIZE':64,'MIDI_RX_BUFSIZE':128,'MIDI_TX_BUFSIZE':128}.items():assert re.search(r'^#define CFG_TUD_'+key+r' '+str(value)+r'$',config,re.M)
  with tempfile.TemporaryDirectory(prefix='glyph-rt2-usb-') as directory:
   temp=Path(directory);gen=temp/'generated';gen.mkdir();overlay=temp/'overlay';(overlay/'core').mkdir(parents=True);(overlay/'arduino').mkdir();shutil.copytree(LEGACY/'include',overlay,dirs_exist_ok=True)
   stubs=(LEGACY/'include/host_stubs.hpp').read_text();stubs=stubs[0:stubs.index('struct TinyUSBDeviceStub')]+stubs[stubs.index('inline void reboot_firmware()'):];(overlay/'host_stubs.hpp').write_text(stubs)
   (overlay/'Arduino.h').write_text('#include "host_stubs.hpp"\nvoid yield();\n');(overlay/'Stream.h').write_text('#include "host_stubs.hpp"\n')
   (overlay/'arduino/Adafruit_USBD_Device.h').write_text('#include '+json.dumps(str(usb/'arduino/Adafruit_USBD_Device.h'))+'\n')
   persistence=(LEGACY/'include/core/Persistence.hpp').read_text().replace('class Persistence {','extern void USBTestDuringInspection();\nclass Persistence {').replace(' public:',' public:\n  bool SetValidator(ConfigSemanticValidator){return true;}\n  bool IsAvailable(){return true;}')
   persistence=persistence.replace('    ++load_calls;','    ++load_calls; USBTestDuringInspection();')
   (overlay/'core/Persistence.hpp').write_text(persistence)
   run([sys.executable,NANOPB/'generator/nanopb_generator.py','-I',ROOT/'schema/haybox','-f',ROOT/'schema/haybox/config.options','--error-on-unmatched','--no-timestamp','-D',gen,ROOT/'schema/haybox/config.proto'])
   pb,jf,_=transport.load_runtime_proto_modules(ROOT);_,data=transport.encode_artifact_payload(make_v3_artifact(),pb,jf);fixture=temp/'config.pb';fixture.write_bytes(data)
   libs=ROOT/'.pio/libdeps/glyph_mk6'
   includes=[overlay,HOST/'include',ROOT/'tools/fixtures/profile_store_cdc_progress/include',LEGACY/'include',usb/'arduino',usb,ROOT/'HAL/pico/include',ROOT/'include',gen,NANOPB,libs/'nanopb-arduino/src',libs/'PacketIO/src',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',temp]
   inc=[item for p in includes for item in ['-I',p]];san=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'];defs=['-DCFG_TUSB_CONFIG_FILE="fixture_tusb_config.h"','-DARDUINO=1','-DUSE_TINYUSB=1','-DGLYPH_CDC_COORDINATION_TEST=1','-DGLYPH_STRICT_HARDENING_CANDIDATE=1','-fshort-enums','-DUSB_VID=0x2e8a','-DUSB_PID=0x000a']
   if a.identity_matrix:defs+=['-DGLYPH_IDENTITY_MATRIX=1']
   objects=[]
   for src in [NANOPB/'pb_common.c',NANOPB/'pb_decode.c',NANOPB/'pb_encode.c',gen/'config.pb.c',usb/'device/usbd.c',usb/'device/usbd_control.c',usb/'common/tusb_fifo.c',usb/'tusb.c',usb/'class/cdc/cdc_device.c',usb/'class/hid/hid_device.c',usb/'class/msc/msc_device.c',usb/'class/midi/midi_device.c']:
    if a.identity_matrix and src.name=='usbd.c':
     probe=temp/'usbd.c';probe.write_text(src.read_text()+'\nbool glyph_host_addressed(void){return _usbd_dev.addressed;}\nuint8_t glyph_host_configuration(void){return _usbd_dev.cfg_num;}\n');src=probe
    obj=temp/(src.stem+'.o');run(['cc','-std=c11',*san,*defs,*inc,'-c',src,'-o',obj]);objects.append(obj)
   profile=temp/'ProfileStore.o';run(['c++','-std=c++17',*san,*defs,*inc,'-Dprofile_store=production_profile_store','-c',ROOT/'HAL/pico/src/core/ProfileStore.cpp','-o',profile]);objects.append(profile)
   (temp/'retained_timeout_harness.inc').write_text((LEGACY/'timeout_harness.cpp').read_text())
   portable_device=temp/'Adafruit_USBD_Device.cpp';portable_device.write_text('extern void USBTestCoreBeforeCDC();\nextern bool USBTestAllowAutoCDC();\n'+device.replace('(uint32_t)_desc_str_arr[STRID_LANGUAGE]','(uintptr_t)_desc_str_arr[STRID_LANGUAGE]').replace('SerialTinyUSB.begin(115200);','USBTestCoreBeforeCDC();\n  if(USBTestAllowAutoCDC()) SerialTinyUSB.begin(115200);'))
   common=[HOST/'startup.cpp',portable_device,usb/'arduino/Adafruit_USBD_CDC.cpp',LEGACY/'checked_storage_unavailable.cpp',ROOT/'src/core/config_validation.cpp',ROOT/'src/core/config_button_validation.cpp',ROOT/'src/core/config_usb_default_validation.cpp',ROOT/'src/core/config_rgb_target_validation.cpp',ROOT/'config/glyph/common/src/glyph_config_validation.cpp',libs/'nanopb-arduino/src/pb_arduino.cpp']
   for frozen in (True,False):
    app=subprocess.check_output(['git','show',frozen_ref+':config/glyph/common/src/config.cpp'],cwd=ROOT).decode() if frozen else (ROOT/'config/glyph/common/src/config.cpp').read_text()
    rec=function(app,'void enter_recovery_configurator()');loop=function(app,'void loop()');start=loop.index('    if (read_boot_state().outcome == BootOutcome::RecoveryConfigurator)')
    i=loop.index('{',start);end=i+1;depth=1
    while depth:depth+=(loop[end]=='{')-(loop[end]=='}');end+=1
    rec=rec.replace('    const RecoveryInitialization recovery = initialize_recovery(', '    HostBoundary("before-inspection");\n    const RecoveryInitialization recovery = initialize_recovery(').replace('    Serial.begin(115200);','    HostBoundary("before-serial");\n    Serial.begin(115200);\n    HostBoundary("after-serial");')
    (temp/'recovery_route.inc').write_text(rec);(temp/'recovery_loop.inc').write_text('void recovery_loop(){'+loop[start:end]+'}\n')
    backend=ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp';extra=[]
    if frozen:backend=temp/'frozen_backend.cpp';backend.write_bytes(subprocess.check_output(['git','show',frozen_ref+':HAL/pico/src/comms/ConfiguratorBackend.cpp'],cwd=ROOT))
    else:extra=['-DGLYPH_RECOVERY_DIAGNOSTICS_HOST=1'];common_diag=[ROOT/'HAL/pico/src/core/RecoveryStartupDiagnostics.cpp']
    if frozen and a.identity_matrix:
     extra=['-DGLYPH_RECOVERY_DIAGNOSTICS_HOST=1'];old_diag=temp/'frozen_diagnostics.cpp';old_diag.write_bytes(subprocess.check_output(['git','show',frozen_ref+':HAL/pico/src/core/RecoveryStartupDiagnostics.cpp'],cwd=ROOT));common_diag=[old_diag]
    exe=temp/('frozen' if frozen else 'candidate');run(['c++','-std=c++17',*san,*defs,*extra,'-DEXPECT_DIAGNOSTICS='+str(int(not frozen)),*inc,*common,*(common_diag if not frozen or a.identity_matrix else []),backend,*objects,'-o',exe])
    if a.identity_matrix:
     for initial in ('bootstrap','configurator'):
      for first_length in (8,18):
       for boundary in 'ABCDEFGH':
        result=json.loads(run([exe,fixture,boundary,initial,str(first_length)]));results.append(result)
     continue
    negative=run([exe,fixture,'no-auto-cdc'],expected=1);assert 'CDC installed BEFORE tud_init/attach' in negative;results.append({'frozen':frozen,'negative':'removed-auto-CDC','detected':True})
    if not frozen and not a.identity_matrix:
     guard=temp/'production-guard';prod_defs=[d for d in defs if d!='-DGLYPH_STRICT_HARDENING_CANDIDATE=1']+['-DGLYPH_STRICT_HARDENING_CANDIDATE=0']
     run(['c++','-std=c++17',*san,*prod_defs,'-DGLYPH_RECOVERY_DIAGNOSTICS_HOST=1','-DEXPECT_DIAGNOSTICS=0',*inc,*common,ROOT/'HAL/pico/src/core/RecoveryStartupDiagnostics.cpp',ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp',*objects,'-o',guard])
     print(run([guard,fixture,'production-retain-policy']),end='')
    for timing in ['before-inspection','during-inspection','before-serial','after-serial','after-publication','core-before-cdc','pio-unavailable','pio-no-sm','pio1-fallback','pio-fifo-busy','normal-configurator']:
     output=run([exe,fixture,timing]);print(output,end='');results.append({'frozen':frozen,'timing':timing,'output':output.strip()})
  if a.identity_matrix:
   assert len(results)==64
   assert any(x['mixed_identity'] for x in results if x['frozen'])
   assert not any(x['mixed_identity'] for x in results if not x['frozen'])
   print('identity_matrix: PASS frozen32 candidate32; mixed identities reproduced in frozen; candidate identity stable; physical failure not modeled')
  report={'result':'PASS','cases':results,'identity_matrix':a.identity_matrix,'late_cdc_hypothesis':'REJECTED_BY_PINNED_SOURCE_AND_FROZEN_POSITIVE_CONTROL','physical_failure_reproduced':False,'physical_macOS':'NOT_MODELED','host_portability_adaptation':'Device language descriptor pointer cast uses uintptr_t instead of uint32_t on 64-bit host; final uint16_t language ID unchanged; one observation hook before auto-CDC; Mach-O optional weak callbacks explicitly model null/no-op defaults','frozen':frozen_ref,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'model_boundary':'Real descriptor builder, CDC C++/C driver, USBD/control/event/Pico OSAL, backend/store. DCD packets/IRQ scheduling/PIO/Config physical I/O are explicit models; target XInput app-driver/BOS/vendor overrides omitted; not physical enumeration acceptance.'}
  if a.output_dir:a.output_dir.mkdir(parents=True,exist_ok=True);(a.output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
  print('glyph_rt2_usb_startup: PASS');return 0
 except Exception as e:print('glyph_rt2_usb_startup: FAIL: '+str(e));return 1
if __name__=='__main__':raise SystemExit(main())
