#!/usr/bin/env python3
"""Pinned RP2040 init/IRQ extraction, real USBD/CDC and read-only observer.

MMIO/NVIC/packet electrical completion are explicit host models, never macOS proof.
"""
import hashlib,json,os,shlex,shutil,subprocess,sys,tempfile,re
from pathlib import Path
import check_glyph_rt2_usb_startup as base
from check_glyph_stage_b_ultimate_profiles import ROOT,NANOPB,make_v3_artifact
from check_glyph_profile_store_littlefs_host import FRAMEWORK
import glyph_serial_config_tool as transport
HOST=ROOT/'tools/fixtures/rt2_dcd_host';LEGACY=ROOT/'tools/fixtures/profile_store_timeout_host'
USB=FRAMEWORK/'libraries/Adafruit_TinyUSB_Arduino/src';SDK=FRAMEWORK/'pico-sdk'
def run(args):return base.run(args)
def main():
 import argparse
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path);args=ap.parse_args()
 sources=[USB/'portable/raspberrypi/rp2040/dcd_rp2040.c',USB/'portable/raspberrypi/rp2040/rp2040_usb.c',USB/'portable/raspberrypi/rp2040/rp2040_usb.h',USB/'arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp',USB/'device/usbd.c',USB/'device/usbd_control.c',SDK/'src/rp2040/hardware_structs/include/hardware/structs/usb.h',SDK/'src/rp2040/hardware_regs/include/hardware/regs/usb.h',ROOT/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp',ROOT/'HAL/pico/src/core/RecoveryStartupDiagnostics.cpp',ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp',ROOT/'schema/haybox/config.proto']
 assert json.loads((FRAMEWORK/'package.json').read_text())['version']=='1.30603.0'
 class GateEnv:
  def __init__(self,d):self.d=d;self.calls=[]
  def get(self,*a):return []
  def ParseFlags(self,f):return {'CPPDEFINES':self.d}
  def Append(self,**kw):self.calls.append(kw)
 for definitions,n in [([],0),([('GLYPH_STRICT_HARDENING_CANDIDATE',0)],0),([('GLYPH_STRICT_HARDENING_CANDIDATE',1)],1)]:
  env=GateEnv(definitions);exec((ROOT/'builder_scripts/rt2_dcd_observer.py').read_text(),{'env':env,'Import':lambda *_:None});assert len(env.calls)==n
  if n:assert len(env.calls[0]['LINKFLAGS'])==6
 dcd=sources[0].read_text();common=sources[1].read_text();port=sources[3].read_text();extract={}
 signatures=['TU_ATTR_ALWAYS_INLINE static inline struct hw_endpoint *hw_endpoint_get_by_num','static struct hw_endpoint *hw_endpoint_get_by_addr','static void _hw_endpoint_alloc','static void hw_endpoint_init','static void hw_endpoint_xfer','static void __tusb_irq_path_func(hw_handle_buff_status)','TU_ATTR_ALWAYS_INLINE static inline void reset_ep0_pid','static void __tusb_irq_path_func(reset_non_control_endpoints)','static void __tusb_irq_path_func(dcd_rp2040_irq)','void dcd_init','void dcd_int_enable','void dcd_int_disable','void dcd_set_address','void dcd_connect','void dcd_disconnect','void dcd_edpt0_status_complete','bool dcd_edpt_open','void __tusb_irq_path_func(dcd_int_handler)']
 for sig in signatures:extract[sig]=base.function(dcd,sig)
 for sig in ['void rp2040_usb_init','void __tusb_irq_path_func(hw_endpoint_reset_transfer)']:extract[sig]=base.function(common,sig)
 with tempfile.TemporaryDirectory(prefix='glyph-dcd-') as name:
  temp=Path(name);overlay=temp/'overlay';shutil.copytree(LEGACY/'include',overlay);(overlay/'arduino').mkdir(exist_ok=True);gen=temp/'generated';gen.mkdir()
  stubs=(overlay/'host_stubs.hpp').read_text();stubs=stubs[:stubs.index('struct TinyUSBDeviceStub')]+stubs[stubs.index('inline void reboot_firmware()'):];(overlay/'host_stubs.hpp').write_text(stubs)
  (overlay/'Arduino.h').write_text('#include "host_stubs.hpp"\nvoid yield();\n');(overlay/'Stream.h').write_text('#include "host_stubs.hpp"\n');(overlay/'arduino/Adafruit_USBD_Device.h').write_text('#include '+json.dumps(str(USB/'arduino/Adafruit_USBD_Device.h'))+'\n')
  persistence=(overlay/'core/Persistence.hpp').read_text().replace('class Persistence {','extern void USBTestDuringInspection();\nclass Persistence {').replace(' public:',' public:\n bool SetValidator(ConfigSemanticValidator){return true;}\n bool IsAvailable(){return true;}').replace('    ++load_calls;','    ++load_calls; USBTestDuringInspection();');(overlay/'core/Persistence.hpp').write_text(persistence)
  # Retain exact SDK register layouts/bit definitions; substitute only address base.
  hardware=temp/'hardware/structs';hardware.mkdir(parents=True)
  (hardware/'usb.h').write_text('#pragma once\n#include "pico.h"\n#include '+json.dumps(str(sources[6]))+'\n#undef usb_hw\n#undef usb_dpram\ntypedef usb_hw_t UsbHw;\nextern usb_hw_t usb_registers;\nextern usb_device_dpram_t usb_dpram_registers;\n#define usb_hw (&usb_registers)\n#define usb_dpram (&usb_dpram_registers)\n')
  run([sys.executable,NANOPB/'generator/nanopb_generator.py','-I',ROOT/'schema/haybox','-f',ROOT/'schema/haybox/config.options','--error-on-unmatched','--no-timestamp','-D',gen,ROOT/'schema/haybox/config.proto'])
  pb,jf,_=transport.load_runtime_proto_modules(ROOT);_,data=transport.encode_artifact_payload(make_v3_artifact(),pb,jf);fixture=temp/'config.pb';fixture.write_bytes(data)
  libs=ROOT/'.pio/libdeps/glyph_mk6';includes=[temp,HOST/'include',overlay,ROOT/'tools/fixtures/rt2_usb_startup/include',ROOT/'tools/fixtures/profile_store_cdc_progress/include',USB/'portable/raspberrypi/rp2040',USB/'arduino',USB,SDK/'src/rp2040/hardware_regs/include',ROOT/'HAL/pico/include',ROOT/'include',gen,NANOPB,libs/'nanopb-arduino/src',libs/'PacketIO/src',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include'];inc=[x for p in includes for x in ('-I',p)]
  defs=['-DCFG_TUSB_CONFIG_FILE="fixture_tusb_config.h"','-DARDUINO=1','-DUSE_TINYUSB=1','-DGLYPH_CDC_COORDINATION_TEST=1','-DGLYPH_STRICT_HARDENING_CANDIDATE=1','-DGLYPH_RECOVERY_DIAGNOSTICS_HOST=1','-DGLYPH_RT2_DCD_HOST=1','-DUSB_VID=0x2e8a','-DUSB_PID=0x000a','-fshort-enums'];san=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
  c_sources=[NANOPB/'pb_common.c',NANOPB/'pb_decode.c',NANOPB/'pb_encode.c',gen/'config.pb.c',USB/'device/usbd.c',USB/'device/usbd_control.c',USB/'common/tusb_fifo.c',USB/'tusb.c',USB/'class/cdc/cdc_device.c',USB/'class/hid/hid_device.c',USB/'class/msc/msc_device.c',USB/'class/midi/midi_device.c'];objects=[]
  for src in c_sources:
   flags=['-Dtud_task_ext=__wrap_tud_task_ext','-Dtud_control_xfer=__wrap_tud_control_xfer']
   if src.name=='usbd.c':flags=['-Dtud_task_ext=__real_tud_task_ext','-Dtud_control_xfer=__wrap_tud_control_xfer','-Ddcd_set_address=__wrap_dcd_set_address']
   if src.name=='usbd_control.c':flags=['-Dtud_task_ext=__wrap_tud_task_ext','-Dtud_control_xfer=__real_tud_control_xfer','-Ddcd_edpt0_status_complete=__wrap_dcd_edpt0_status_complete']
   obj=temp/(src.stem+'.o');run(['cc','-std=c11',*san,*defs,*flags,*inc,'-c',src,'-o',obj]);objects.append(obj)
  obj=temp/'ProfileStore.o';run(['c++','-std=c++17',*san,*defs,*inc,'-Dprofile_store=production_profile_store','-c',ROOT/'HAL/pico/src/core/ProfileStore.cpp','-o',obj]);objects.append(obj)
  (temp/'retained_timeout_harness.inc').write_text((LEGACY/'timeout_harness.cpp').read_text())
  app=(ROOT/'config/glyph/common/src/config.cpp').read_text();(temp/'recovery_route.inc').write_text(base.function(app,'void enter_recovery_configurator()'))
  loop=base.function(app,'void loop()');i=loop.index('    if (read_boot_state().outcome == BootOutcome::RecoveryConfigurator)');body=base.function(loop[i:],'    if (read_boot_state().outcome == BootOutcome::RecoveryConfigurator)');(temp/'recovery_loop.inc').write_text('void recovery_loop(){'+body+'}\n')
  # Source-faithful extraction. Alias-register assignments adapt to host W1C/SET.
  def mmio(s):
   return re.sub(r'usb_hw_(set|clear)->(\w+)\s*=\s*([^;]+);',lambda m:'GlyphHost'+('Set' if m[1]=='set' else 'Clear')+'(offsetof(usb_hw_t,'+m[2]+'),'+m[3]+');',s)
  parts=['static uint8_t *next_buffer_ptr;static hw_endpoint_t hw_endpoints[USB_MAX_ENDPOINTS][2];static bool _sof_enable=false;',extract['void rp2040_usb_init'],extract['void __tusb_irq_path_func(hw_endpoint_reset_transfer)']]
  parts += [extract[sig] for sig in signatures]
  generated=mmio('\n'.join(parts)).replace('void dcd_set_address','void __real_dcd_set_address').replace('void dcd_edpt0_status_complete','void __real_dcd_edpt0_status_complete').replace('    hw_endpoint_init(desc_edpt->bEndpointAddress','    ++opened;hw_endpoint_init(desc_edpt->bEndpointAddress')
  (temp/'dcd_generated.inc').write_text('extern "C" {\n'+generated+'\n}\n')
  startup=(ROOT/'tools/fixtures/rt2_usb_startup/startup.cpp').read_text().replace('unsigned tasks=0,','std::vector<uint32_t> led_words;unsigned tasks=0,');startup=startup.replace('void HostBoundary(const char*);','void HostBoundary(const char*);\nvoid host_setup_packet(const tusb_control_request_t&);\nvoid host_tick();')
  old=base.function(startup,'void control(');startup=startup.replace(old,'void control(const tusb_control_request_t &request){control_rx.clear();host_setup_packet(request);}')
  # Remove only DCD/API bodies now supplied by extracted pinned source/wrappers.
  for sig in ['void TinyUSB_Port_InitDevice','void dcd_init','void dcd_int_enable','void dcd_int_disable','void dcd_connect','void dcd_disconnect','void dcd_set_address','bool dcd_edpt_open','void dcd_edpt0_status_complete','void tud_event_hook_cb']:
   startup=startup.replace(base.function(startup,sig),'')
  task=base.function(port,'void TinyUSB_Device_Task(');task=task.replace('  // Since','  host_tick();\n  // Since');startup=startup.replace(base.function(startup,'void TinyUSB_Device_Task('),task)
  startup=startup.replace('if(ep&0x80){if(n)', 'if(ep==0x80&&n==0&&hold_address_ack){pending_address_ack=true;return true;}\n if(ep&0x80){if(n)')
  port_init=base.function(port,'void TinyUSB_Port_InitDevice(').replace('TinyUSB_Port_InitDevice','GlyphRealPortInit')
  prefix='extern "C" {\n#include "rp2040_usb.h"\n}\n#include '+json.dumps(str(HOST/'model.inc'))+'\n#include "dcd_generated.inc"\nstatic unsigned USB_TASK_IRQ;\n'+base.function(port,'static void usb_task_irq(')+'\n'+base.function(port,'static void usb_task_trigger_irq(')+'\n'+port_init+'\n'
  startup=startup.replace('void TinyUSB_Port_EnterDFU()',prefix+'void TinyUSB_Port_EnterDFU()')
  startup=startup.replace('void pio_sm_put(PIO,int,uint32_t){', 'void pio_sm_put(PIO,int,uint32_t word){led_words.push_back(word);')
  startup=startup.replace('int main(int argc,char**argv){try{','#include '+json.dumps(str(HOST/'cases.inc'))+'\n#define main unused_startup_main\nint main(int argc,char**argv){try{')
  startup+='\nextern "C" void hw_endpoint_xfer_start(struct hw_endpoint*ep,uint8_t*b,uint16_t n){dcd_edpt_xfer(0,ep->ep_addr,b,n);}\nextern "C" bool hw_endpoint_xfer_continue(struct hw_endpoint*){panic("DPRAM buffer continuation not modeled");return false;}\n'
  (temp/'startup.cpp').write_text(startup)
  vendor=temp/'Adafruit_USBD_Device.cpp';vendor.write_text((USB/'arduino/Adafruit_USBD_Device.cpp').read_text().replace('(uint32_t)_desc_str_arr[STRID_LANGUAGE]','(uintptr_t)_desc_str_arr[STRID_LANGUAGE]').replace('TinyUSB_Port_InitDevice(rhport)','GlyphWrapPortInit(rhport)'))
  # Port API prototype uses C++ linkage, as in the pinned implementation.
  vendor.write_text('#include <cstdint>\nvoid GlyphWrapPortInit(uint8_t);\n'+vendor.read_text())
  cpp=[temp/'startup.cpp',vendor,USB/'arduino/Adafruit_USBD_CDC.cpp',LEGACY/'checked_storage_unavailable.cpp',ROOT/'src/core/config_validation.cpp',ROOT/'src/core/config_button_validation.cpp',ROOT/'src/core/config_usb_default_validation.cpp',ROOT/'src/core/config_rgb_target_validation.cpp',ROOT/'config/glyph/common/src/glyph_config_validation.cpp',libs/'nanopb-arduino/src/pb_arduino.cpp',ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp',ROOT/'HAL/pico/src/core/RecoveryStartupDiagnostics.cpp',ROOT/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp']
  exe=temp/'dcd';run(['c++','-std=c++17',*san,*defs,'-DEXPECT_DIAGNOSTICS=1','-Dtud_task_ext=__wrap_tud_task_ext',*inc,*cpp,*objects,'-o',exe])
  results=[]
  for case in ['pullup-off','silent','reset','setup','address','address-pending','configured','irq-deferred','irq-disabled','global-mask','task-deferred','inspect','replug']:
   output=run([exe,fixture,case]);print(output,end='');results.append({'case':case,'output':output.strip()})
  negative_source=temp/'no_events.cpp';negative_source.write_text((ROOT/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp').read_text().replace('if(event==DCD_EVENT_BUS_RESET)reset_seen=true;', 'if(event==DCD_EVENT_BUS_RESET){}').replace('if(event==DCD_EVENT_SETUP_RECEIVED)setup_seen=true;', 'if(event==DCD_EVENT_SETUP_RECEIVED){}'))
  negative_exe=temp/'negative';run(['c++','-std=c++17',*san,*defs,'-DEXPECT_DIAGNOSTICS=1','-Dtud_task_ext=__wrap_tud_task_ext',*inc,*[negative_source if p==ROOT/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp' else p for p in cpp],*objects,'-o',negative_exe])
  rejected=base.run([negative_exe,fixture,'reset'],expected=1);assert 'magenta actual DCD bus reset' in rejected
  print('negative_removed_event_hook=DETECTED')
  report={'negative_removed_event_hook':'DETECTED','status':'PASS','cases':results,'physical_macOS':'NOT_MODELED','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'extracted_function_hashes':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in extract.items()},'model_boundary':'Real pinned init/IRQ/control/address/endpoint-open and USBD/CDC/backend. MMIO SET/CLEAR, NVIC scheduling, resets, electrical packets/DPRAM completion modeled; no full DMA continuation or physical host policy. Disabled RP2040 E5/E15 fixes match pin. Mach-O rename and 64-bit language pointer adaptations are host-only.'}
  if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=True);(args.output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:
  import traceback;traceback.print_exc();print('glyph_rt2_dcd_observer: FAIL: '+str(e));raise SystemExit(1)
