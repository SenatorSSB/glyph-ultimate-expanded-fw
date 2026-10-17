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
TASK_HOST=ROOT/'tools/fixtures/rt2_comprehensive_host'
SETUP_HOST=ROOT/'tools/fixtures/rt2_pre_setup_host'
HOST=ROOT/'tools/fixtures/rt2_dcd_host';LEGACY=ROOT/'tools/fixtures/profile_store_timeout_host'
USB=FRAMEWORK/'libraries/Adafruit_TinyUSB_Arduino/src';SDK=FRAMEWORK/'pico-sdk'
def run(args):return base.run(args)
def main():
 import argparse
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path);args=ap.parse_args()
 sources=[USB/'portable/raspberrypi/rp2040/dcd_rp2040.c',USB/'portable/raspberrypi/rp2040/rp2040_usb.c',USB/'portable/raspberrypi/rp2040/rp2040_usb.h',USB/'arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp',USB/'device/usbd.c',USB/'device/usbd_control.c',SDK/'src/rp2040/hardware_structs/include/hardware/structs/usb.h',SDK/'src/rp2040/hardware_regs/include/hardware/regs/usb.h',ROOT/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp',ROOT/'HAL/pico/src/core/RecoveryStartupDiagnostics.cpp',ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp',ROOT/'schema/haybox/config.proto',ROOT/'include/core/RecoveryTaskDiagnostics.hpp',ROOT/'config/glyph/common/src/config.cpp',FRAMEWORK/'cores/rp2040/main.cpp',ROOT/'.pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/src/Adafruit_USBD_XInput.cpp']
 sources += [USB/'osal/osal_pico.h',USB/'common/tusb_fifo.c',USB/'common/tusb_fifo.h',ROOT/'include/core/RecoveryStartupDiagnostics.hpp',ROOT/'include/core/RecoveryUsbDiagnostics.hpp',ROOT/'builder_scripts/rt2_dcd_observer.py',Path(__file__),ROOT/'include/core/RecoverySetupIrqDiagnostics.hpp',ROOT/'include/core/RecoveryPreSetupDiagnostics.hpp',USB/'device/dcd.h',*sorted(TASK_HOST.rglob('*')),*sorted(SETUP_HOST.rglob('*'))]
 # Hash all source dependencies used by generated translation units, including
 # reused retained fixtures/headers and checker helpers; caches are not inputs.
 for directory in [HOST,TASK_HOST,SETUP_HOST,LEGACY,ROOT/'tools/fixtures/rt2_usb_startup',ROOT/'tools/fixtures/profile_store_cdc_progress',ROOT/'include',ROOT/'HAL/pico/include',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',USB,SDK/'src/rp2040/hardware_regs/include',SDK/'src/rp2040/hardware_structs/include',NANOPB,ROOT/'.pio/libdeps/glyph_mk6/nanopb-arduino/src',ROOT/'.pio/libdeps/glyph_mk6/PacketIO/src']:
  sources += [p for p in directory.rglob('*') if p.suffix in ('.h','.hpp','.c','.cpp','.inc','.py')]
 sources += list((ROOT/'src/core').glob('config*validation.cpp'))+[ROOT/'HAL/pico/src/core/ProfileStore.cpp',ROOT/'config/glyph/common/src/glyph_config_validation.cpp']+list((ROOT/'tools').glob('*.py'))
 sources=list(dict.fromkeys(p for p in sources if p.is_file() and p.suffix!='.pyc'))
 source_start={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
 assert json.loads((FRAMEWORK/'package.json').read_text())['version']=='1.30603.0'
 class GateEnv:
  def __init__(self,d):self.d=d;self.calls=[]
  def get(self,*a):return []
  def ParseFlags(self,f):return {'CPPDEFINES':self.d}
  def Append(self,**kw):self.calls.append(kw)
 for definitions,n in [([],0),([('GLYPH_STRICT_HARDENING_CANDIDATE',0)],0),([('GLYPH_STRICT_HARDENING_CANDIDATE',1)],1)]:
  env=GateEnv(definitions);exec((ROOT/'builder_scripts/rt2_dcd_observer.py').read_text(),{'env':env,'Import':lambda *_:None});assert len(env.calls)==n
  if n:assert len(env.calls[0]['LINKFLAGS'])==18
 dcd=sources[0].read_text();common=sources[1].read_text();port=sources[3].read_text();extract={}
 signatures=['TU_ATTR_ALWAYS_INLINE static inline struct hw_endpoint *hw_endpoint_get_by_num','static struct hw_endpoint *hw_endpoint_get_by_addr','static void _hw_endpoint_alloc','static void hw_endpoint_init','static void hw_endpoint_xfer','static void __tusb_irq_path_func(hw_handle_buff_status)','TU_ATTR_ALWAYS_INLINE static inline void reset_ep0_pid','static void __tusb_irq_path_func(reset_non_control_endpoints)','static void __tusb_irq_path_func(dcd_rp2040_irq)','void dcd_init','void dcd_int_enable','void dcd_int_disable','void dcd_set_address','void dcd_connect','void dcd_disconnect','void dcd_edpt0_status_complete','bool dcd_edpt_open','void __tusb_irq_path_func(dcd_int_handler)']
 for sig in signatures:extract[sig]=base.function(dcd,sig)
 common_signatures=['void rp2040_usb_init','void __tusb_irq_path_func(hw_endpoint_reset_transfer)','TU_ATTR_ALWAYS_INLINE static inline bool is_host_mode','void __tusb_irq_path_func(_hw_endpoint_buffer_control_update32)','static uint32_t __tusb_irq_path_func(prepare_ep_buffer)','void __tusb_irq_path_func(hw_endpoint_start_next_buffer)','static uint16_t __tusb_irq_path_func(sync_ep_buffer)','static void __tusb_irq_path_func(_hw_endpoint_xfer_sync) (','bool __tusb_irq_path_func(hw_endpoint_xfer_continue)']
 for sig in common_signatures:extract[sig]=base.function(common,sig)
 with tempfile.TemporaryDirectory(prefix='glyph-dcd-') as name:
  temp=Path(name);sys.path.insert(0,str(SETUP_HOST));import panic_abi
  abi=panic_abi.check(ROOT,temp);print("panic_abi_actual_assembled_Thumb_48_trials_40_vararg_words=MODELED_PASS")
  overlay=temp/'overlay';shutil.copytree(LEGACY/'include',overlay);(overlay/'arduino').mkdir(exist_ok=True);gen=temp/'generated';gen.mkdir()
  stubs=(overlay/'host_stubs.hpp').read_text();stubs=stubs[:stubs.index('struct TinyUSBDeviceStub')]+stubs[stubs.index('inline void reboot_firmware()'):];(overlay/'host_stubs.hpp').write_text(stubs)
  (overlay/'Arduino.h').write_text('#include "host_stubs.hpp"\nvoid yield();\n');(overlay/'Stream.h').write_text('#include "host_stubs.hpp"\n');(overlay/'arduino/Adafruit_USBD_Device.h').write_text('#include '+json.dumps(str(USB/'arduino/Adafruit_USBD_Device.h'))+'\n')
  persistence=(overlay/'core/Persistence.hpp').read_text().replace('class Persistence {','extern void USBTestDuringInspection();\nclass Persistence {').replace(' public:',' public:\n bool SetValidator(ConfigSemanticValidator){return true;}\n bool IsAvailable(){return true;}').replace('    ++load_calls;','    ++load_calls; USBTestDuringInspection();');(overlay/'core/Persistence.hpp').write_text(persistence)
  # Retain exact SDK register layouts/bit definitions; substitute only address base.
  hardware=temp/'hardware/structs';hardware.mkdir(parents=True)
  (hardware/'usb.h').write_text('#pragma once\n#include "pico.h"\n#include '+json.dumps(str(sources[6]))+'\n#undef usb_hw\n#undef usb_dpram\ntypedef usb_hw_t UsbHw;\nextern usb_hw_t usb_registers;\nextern usb_device_dpram_t usb_dpram_registers;\n#define usb_hw (&usb_registers)\n#define usb_dpram (&usb_dpram_registers)\n')
  run([sys.executable,NANOPB/'generator/nanopb_generator.py','-I',ROOT/'schema/haybox','-f',ROOT/'schema/haybox/config.options','--error-on-unmatched','--no-timestamp','-D',gen,ROOT/'schema/haybox/config.proto'])
  pb,jf,_=transport.load_runtime_proto_modules(ROOT);_,data=transport.encode_artifact_payload(make_v3_artifact(),pb,jf);fixture=temp/'config.pb';fixture.write_bytes(data)
  libs=ROOT/'.pio/libdeps/glyph_mk6';includes=[temp,TASK_HOST/'include',HOST/'include',overlay,ROOT/'tools/fixtures/rt2_usb_startup/include',ROOT/'tools/fixtures/profile_store_cdc_progress/include',USB/'portable/raspberrypi/rp2040',USB/'arduino',USB/'class/cdc',USB/'class/msc',USB/'class/hid',USB/'class/midi',USB,SDK/'src/rp2040/hardware_regs/include',ROOT/'HAL/pico/include',ROOT/'include',gen,NANOPB,libs/'nanopb-arduino/src',libs/'PacketIO/src',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include'];inc=[x for p in includes for x in ('-I',p)]
  queue_size=int(re.search(r'#define CFG_TUD_TASK_QUEUE_SZ\s+(\d+)',(USB/'device/usbd.c').read_text())[1])
  defs=['-DGLYPH_HOST_QUEUE_SIZE='+str(queue_size),'-DCFG_TUSB_CONFIG_FILE="fixture_tusb_config.h"','-DARDUINO=1','-DUSE_TINYUSB=1','-DGLYPH_CDC_COORDINATION_TEST=1','-DGLYPH_STRICT_HARDENING_CANDIDATE=1','-DGLYPH_RECOVERY_DIAGNOSTICS_HOST=1','-DGLYPH_RT2_DCD_HOST=1','-DUSB_VID=0x2e8a','-DUSB_PID=0x000a','-fshort-enums'];san=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
  c_sources=[NANOPB/'pb_common.c',NANOPB/'pb_decode.c',NANOPB/'pb_encode.c',gen/'config.pb.c',USB/'device/usbd.c',USB/'device/usbd_control.c',USB/'common/tusb_fifo.c',USB/'tusb.c',USB/'class/cdc/cdc_device.c',USB/'class/hid/hid_device.c',USB/'class/msc/msc_device.c',USB/'class/midi/midi_device.c'];objects=[]
  for src in c_sources:
   flags=['-Dtud_task_ext=__wrap_tud_task_ext','-Dtud_control_xfer=__wrap_tud_control_xfer','-Dtu_fifo_write=__wrap_tu_fifo_write','-Dtu_fifo_read=__wrap_tu_fifo_read']
   if src.name=='usbd.c':flags=['-Dtud_task_ext=__real_tud_task_ext','-Dtud_control_xfer=__wrap_tud_control_xfer','-Ddcd_set_address=__wrap_dcd_set_address','-Dusbd_control_reset=__wrap_usbd_control_reset','-Dtu_fifo_write=__wrap_tu_fifo_write','-Dtu_fifo_read=__wrap_tu_fifo_read','-Dcdcd_reset=__wrap_cdcd_reset','-Dmscd_reset=__wrap_mscd_reset','-Dhidd_reset=__wrap_hidd_reset','-Dmidid_reset=__wrap_midid_reset','-Dusbd_control_set_complete_callback=__wrap_usbd_control_set_complete_callback','-Ddcd_event_handler=__real_dcd_event_handler']
   if src.name=='usbd_control.c':flags=['-Dtud_task_ext=__wrap_tud_task_ext','-Dtud_control_xfer=__real_tud_control_xfer','-Ddcd_edpt0_status_complete=__wrap_dcd_edpt0_status_complete','-Dusbd_control_reset=__real_usbd_control_reset','-Dusbd_control_set_complete_callback=__real_usbd_control_set_complete_callback']
   if src.name=='tusb_fifo.c':flags=[f for f in flags if not f.startswith(('-Dtu_fifo_write=','-Dtu_fifo_read='))]+['-Dtu_fifo_write=__real_tu_fifo_write','-Dtu_fifo_read=__real_tu_fifo_read']
   for stem,symbol in [('cdc_device.c','cdcd_reset'),('msc_device.c','mscd_reset'),('hid_device.c','hidd_reset'),('midi_device.c','midid_reset')]:
    if src.name==stem:flags.append('-D'+symbol+'=__real_'+symbol)
   if src.name!='usbd.c':flags.append('-Ddcd_event_handler=__wrap_dcd_event_handler')
   # Host-only scheduling/stall injection; production pinned files are untouched.
   if src.name=='usbd.c':
    body=src.read_text()
    body=body.replace('        queue_event(&event_resume, in_isr);','        GlyphSofQueueBoundary();\n        queue_event(&event_resume, in_isr);')
    body=body.replace('    if ( !osal_queue_receive', '    GlyphTaskBoundary("queue",0);\n    if ( !osal_queue_receive')
    body=body.replace('      case DCD_EVENT_SETUP_RECEIVED:', '      case DCD_EVENT_SETUP_RECEIVED:\n        GlyphTaskBoundary("setup-consumed",0);')
    body=body.replace('  usbd_control_set_complete_callback(NULL);','  usbd_control_set_complete_callback(NULL);\n  GlyphTaskBoundary("control-began",0);')
    body=body.replace('    if ( !osal_queue_receive(_usbd_q, &event, timeout_ms) ) return;', '    if ( !osal_queue_receive(_usbd_q, &event, timeout_ms) ) { GlyphTaskBoundary("empty-return",0);return; }')
    body=body.replace('    driver->reset(rhport);','    GlyphTaskBoundary("class-enter",i);\n    driver->reset(rhport);\n    GlyphTaskBoundary("class-return",i);')
    body=body.replace('  configuration_reset(rhport);\n  usbd_control_reset();','  GlyphTaskBoundary("configuration-enter",0);\n  configuration_reset(rhport);\n  GlyphTaskBoundary("configuration-return",0);\n  GlyphTaskBoundary("control-enter",0);\n  usbd_control_reset();\n  GlyphTaskBoundary("control-return",0);')
    src=temp/'usbd.c';src.write_text('extern void GlyphTaskBoundary(const char*,unsigned);\nextern void GlyphSofQueueBoundary(void);\n'+body)
   if src.name in ['cdc_device.c','msc_device.c','hid_device.c','midi_device.c']:
    body=src.read_text();symbol={'cdc_device.c':'cdcd_reset','msc_device.c':'mscd_reset','hid_device.c':'hidd_reset','midi_device.c':'midid_reset'}[src.name];index={'cdcd_reset':1,'mscd_reset':2,'hidd_reset':3,'midid_reset':4}[symbol]
    function=base.function(body,'void '+symbol+'(');injected=function.replace('{','{\n  GlyphTaskBoundary("class-body",'+str(index)+');',1)
    path=temp/src.name;path.write_text('extern void GlyphTaskBoundary(const char*,unsigned);\n'+body.replace(function,injected));src=path
   obj=temp/(src.stem+'.o');run(['cc','-std=c11',*san,*defs,*flags,*inc,'-c',src,'-o',obj]);objects.append(obj)
  obj=temp/'ProfileStore.o';run(['c++','-std=c++17',*san,*defs,*inc,'-Dprofile_store=production_profile_store','-c',ROOT/'HAL/pico/src/core/ProfileStore.cpp','-o',obj]);objects.append(obj)
  (temp/'retained_timeout_harness.inc').write_text((LEGACY/'timeout_harness.cpp').read_text())
  app=(ROOT/'config/glyph/common/src/config.cpp').read_text();(temp/'recovery_route.inc').write_text(base.function(app,'void enter_recovery_configurator()'))
  route=base.function(app,'void enter_recovery_configurator()')
  assert route.index('HandOffIndicator();')<route.index('publish_boot_state(BootOutcome::RecoveryConfigurator')
  setup1=base.function(app,'void setup1()');assert setup1.index('if (refused(snapshot.outcome))')<setup1.index('static RgbBrightnessMenu')
  main1=base.function((FRAMEWORK/'cores/rp2040/main.cpp').read_text(),'extern "C" void main1()')
  assert main1.index('setup1();')<main1.index('while (true)')<main1.index('loop1();')
  loop1=base.function(app,'void loop1()');observer=loop1[:loop1.index('    if (refused(snapshot.outcome))')]+"}"
  assert 'PublishIndependent();\n        return;' in observer
  (temp/'recovery_observer.inc').write_text(observer.replace('void loop1()', 'void recovery_observer_loop()'))
  loop=base.function(app,'void loop()');i=loop.index('    if (read_boot_state().outcome == BootOutcome::RecoveryConfigurator)');body=base.function(loop[i:],'    if (read_boot_state().outcome == BootOutcome::RecoveryConfigurator)');(temp/'recovery_loop.inc').write_text('void recovery_loop(){'+body+'}\n')
  # Source-faithful extraction. Alias-register assignments adapt to host W1C/SET.
  def mmio(s):
   return re.sub(r'usb_hw_(set|clear)->(\w+)\s*=\s*([^;]+);',lambda m:'GlyphHost'+('Set' if m[1]=='set' else 'Clear')+'(offsetof(usb_hw_t,'+m[2]+'),'+m[3]+');',s)
  parts=['static uint8_t *next_buffer_ptr;static hw_endpoint_t hw_endpoints[USB_MAX_ENDPOINTS][2];static bool _sof_enable=false;const char *ep_dir_string[]={\"out\",\"in\"};\n#define e15_is_critical_frame_period(ep) false']+[extract[sig] for sig in common_signatures]
  parts += [extract[sig] for sig in signatures]
  generated=mmio('\n'.join(parts)).replace('void dcd_set_address','void __real_dcd_set_address').replace('void dcd_edpt0_status_complete','void __real_dcd_edpt0_status_complete').replace('    hw_endpoint_init(desc_edpt->bEndpointAddress','    ++opened;hw_endpoint_init(desc_edpt->bEndpointAddress')
  generated=generated.replace('bool __tusb_irq_path_func(hw_endpoint_xfer_continue)', 'bool __tusb_irq_path_func(__real_hw_endpoint_xfer_continue)').replace('hw_endpoint_xfer_continue(ep)', '__wrap_hw_endpoint_xfer_continue(ep)')
  # Host omits only RP2040 busy-cycle assembly; all transfer decisions/panics stay exact.
  generated=re.sub(r'__asm volatile \(.*?: : : \"memory\"\);', '/* target-only twelve-cycle delay */', generated, flags=re.S)
  generated=generated.replace('  _hw_endpoint_xfer_sync(ep);', '  GlyphPreSetupBoundary(3);\n  _hw_endpoint_xfer_sync(ep);')
  generated=generated.replace('    hw_handle_buff_status();', '    GlyphPreSetupBoundary(1);\n    hw_handle_buff_status();')
  generated=generated.replace('    dcd_event_sof(0, usb_hw->sof_rd & USB_SOF_RD_BITS, true);', '    dcd_event_sof(0, usb_hw->sof_rd & USB_SOF_RD_BITS, true);\n    GlyphPreSetupBoundary(2);')
  generated=generated.replace('irq_add_shared_handler(', '__wrap_irq_add_shared_handler(')
  generated=generated.replace('dcd_event_setup_received(0, setup, true);','GlyphSetupEvent(setup);')
  generated=generated.replace('  uint32_t const status = usb_hw->ints;', '  GlyphTiming(0);\n  uint32_t const status = usb_hw->ints;\n  GlyphTiming(1);')
  generated=generated.replace('    reset_ep0_pid();', '    reset_ep0_pid();\n    GlyphTiming(2);')
  generated=generated.replace('    reset_non_control_endpoints();', '    GlyphTiming(3);\n    reset_non_control_endpoints();')
  generated=generated.replace('GlyphHostClear(offsetof(usb_hw_t,sie_status),USB_SIE_STATUS_BUS_RESET_BITS);', 'GlyphHostClear(offsetof(usb_hw_t,sie_status),USB_SIE_STATUS_BUS_RESET_BITS);\n    GlyphTiming(4);')
  irq_body=base.function(generated,'static void __tusb_irq_path_func(dcd_rp2040_irq)');generated=generated.replace(irq_body,irq_body[:-1]+'  GlyphTiming(5);\n}')
  (temp/'dcd_generated.inc').write_text('extern "C" {\n'+generated+'\n}\n')
  model=(HOST/'model.inc').read_text().replace('extern "C" void irq_add_shared_handler(', 'extern \"C\" void __real_irq_add_shared_handler(')
  model=model.replace('extern \"C\" void panic(const char*format,...){throw std::runtime_error(format);}', 'extern \"C\" void GlyphObserveUsbPanic(const char*);\nextern \"C\" void panic(const char*format,...){GlyphObserveUsbPanic(format);throw std::runtime_error(format);}')
  model=model.replace(' if(offset==offsetof(usb_hw_t,sie_status)){', ' if(offset==offsetof(usb_hw_t,buf_status)){if(usb_hw->buf_status)usb_hw->intr|=USB_INTR_BUFF_STATUS_BITS;else usb_hw->intr&=~USB_INTR_BUFF_STATUS_BITS;}\n if(offset==offsetof(usb_hw_t,sie_status)){')
  model=model.replace('usb_hw->intr&usb_hw->inte','(usb_hw->intr&usb_hw->inte)|usb_hw->intf')
  (temp/'model.inc').write_text(model)
  startup=(ROOT/'tools/fixtures/rt2_usb_startup/startup.cpp').read_text().replace('unsigned tasks=0,','std::vector<uint32_t> led_words;unsigned tasks=0,');startup=startup.replace('void HostBoundary(const char*);','void HostBoundary(const char*);\nvoid host_setup_packet(const tusb_control_request_t&);\nvoid host_tick();\nvoid physical_reset();')
  old=base.function(startup,'void control(');startup=startup.replace(old,'void control(const tusb_control_request_t &request){control_rx.clear();host_setup_packet(request);}')
  # Remove only DCD/API bodies now supplied by extracted pinned source/wrappers.
  for sig in ['void TinyUSB_Port_InitDevice','void dcd_init','void dcd_int_enable','void dcd_int_disable','void dcd_connect','void dcd_disconnect','void dcd_set_address','bool dcd_edpt_open','void dcd_edpt0_status_complete','void tud_event_hook_cb']:
   startup=startup.replace(base.function(startup,sig),'')
  task=base.function(port,'void TinyUSB_Device_Task(');task=task.replace('  // Since','  host_tick();\n  // Since');startup=startup.replace(base.function(startup,'void TinyUSB_Device_Task('),task)
  startup=startup.replace('bool dcd_edpt_xfer(uint8_t port,uint8_t ep,uint8_t*buffer,uint16_t n){', 'bool dcd_edpt_xfer(uint8_t port,uint8_t ep,uint8_t*buffer,uint16_t n){if(reset_on_xfer&&ep==0x80&&n){reset_on_xfer=false;physical_reset();}')
  startup=startup.replace('void HostBoundary(const char *point){', 'void HostBoundary(const char *point){if(selected_timing=="reset-during-inspection"&&std::string(point)=="during-inspection"){physical_reset();return;}')
  startup=startup.replace('if(ep&0x80){if(n)', 'if(ep==0x80&&n==0&&hold_address_ack){pending_address_ack=true;return true;}\n if(ep&0x80){if(n)')
  port_init=base.function(port,'void TinyUSB_Port_InitDevice(').replace('TinyUSB_Port_InitDevice','GlyphRealPortInit').replace('irq_add_shared_handler(', '__wrap_irq_add_shared_handler(')
  prefix='extern \"C\" bool __wrap_hw_endpoint_xfer_continue(struct hw_endpoint*);\n#include '+json.dumps(str(SETUP_HOST/'timing.inc'))+'\nextern "C" {\n#include "rp2040_usb.h"\n}\n#include '+json.dumps(str(temp/'model.inc'))+'\n#include "dcd_generated.inc"\nstatic unsigned USB_TASK_IRQ;\n'+base.function(port,'static void usb_task_irq(')+'\n'+base.function(port,'static void usb_task_trigger_irq(')+'\n'+port_init+'\n'
  startup=startup.replace('void TinyUSB_Port_EnterDFU()',prefix+'void TinyUSB_Port_EnterDFU()')
  startup=startup.replace('void pio_sm_put(PIO,int,uint32_t){', 'void pio_sm_put(PIO,int,uint32_t word){led_words.push_back(word);')
  startup=startup.replace('int main(int argc,char**argv){try{','#include '+json.dumps(str(SETUP_HOST/'cases.inc'))+'\n#define main unused_startup_main\nint main(int argc,char**argv){try{')
  startup+='\nextern "C" void hw_endpoint_xfer_start(struct hw_endpoint*ep,uint8_t*b,uint16_t n){dcd_edpt_xfer(0,ep->ep_addr,b,n);}\n'
  # Register actual target XInput init/reset bodies with inactive open callback.
  xinput=(libs/'Adafruit_TinyUSB_XInput/src/Adafruit_USBD_XInput.cpp').read_text()
  exact=base.function(xinput,'static void xinput_init(')+'\n'+base.function(xinput,'static void xinput_reset(').replace('{','{GlyphTaskBoundary("class-body",0);',1)
  old='const usbd_class_driver_t* usbd_app_driver_get_cb(uint8_t* count){*count=0;return nullptr;}'
  replacement=exact+'\nstatic uint16_t inactive_xinput_open(uint8_t,const tusb_desc_interface_t*,uint16_t){return 0;}\nconst usbd_class_driver_t* usbd_app_driver_get_cb(uint8_t* count){static usbd_class_driver_t d={};d.init=xinput_init;d.reset=xinput_reset;d.open=inactive_xinput_open;*count=1;return &d;}'
  assert old in startup;startup=startup.replace(old,replacement)
  startup=startup.replace('#include "recovery_loop.inc"','#include "recovery_loop.inc"\n#include "recovery_observer.inc"')
  startup='#include <thread>\nextern "C" void GlyphTaskBoundary(const char*,unsigned);\n#include "core/ResourceDiagnostics.hpp"\n'+startup
  startup=startup.replace('bool attached=false,', 'unsigned joined_fifo_depth=4;uint64_t host_clock_us=0;bool attached=false,')
  startup=startup.replace('void pio_sm_put(PIO,int,uint32_t word){led_words.push_back(word);require(!sm_enabled&&pio_words<4,"SM disabled throughout frame preload, USB IRQ may interleave");++pio_words;}', 'void pio_sm_put(PIO,int,uint32_t word){led_words.push_back(word);require(!sm_enabled&&pio_words<joined_fifo_depth,"entire bounded frame preloaded without overflow and USB IRQ may interleave");++pio_words;}')
  startup=startup.replace('require(n==200&&pio_words==4,"bounded LED protocol interval");','require(n==200&&(pio_words==4||pio_words==8),"bounded inherited LED protocol interval");')
  startup+='\nvoid sm_config_set_fifo_join(pio_sm_config*,unsigned join){require(join==PIO_FIFO_JOIN_TX,"only dedicated TX FIFO joins eight slots");joined_fifo_depth=8;}\nbool pio_sm_is_tx_fifo_full(PIO,int){return pio_words>=joined_fifo_depth;}\nuint32_t time_us_32(){return uint32_t(host_clock_us); }\nuint64_t time_us_64(){return host_clock_us;}\n'
  startup=startup.replace('#define main unused_startup_main', '#include '+json.dumps(str(SETUP_HOST/'focused.inc'))+'\n#define main unused_startup_main')
  (temp/'checks.inc').write_text((TASK_HOST/'checks.inc').read_text())
  (temp/'startup.cpp').write_text(startup)
  vendor=temp/'Adafruit_USBD_Device.cpp';vendor.write_text((USB/'arduino/Adafruit_USBD_Device.cpp').read_text().replace('(uint32_t)_desc_str_arr[STRID_LANGUAGE]','(uintptr_t)_desc_str_arr[STRID_LANGUAGE]').replace('TinyUSB_Port_InitDevice(rhport)','GlyphWrapPortInit(rhport)'))
  # Port API prototype uses C++ linkage, as in the pinned implementation.
  vendor.write_text('#include <cstdint>\nvoid GlyphWrapPortInit(uint8_t);\n'+vendor.read_text())
  backend_copy=temp/'ConfiguratorBackend.cpp';backend=(ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp').read_text()
  anchor='        const bool captured=RecoveryStartupDiagnostics::CapturedTaskInto(task);';assert anchor in backend
  backend_copy.write_text('extern void GlyphCaptureResponseBoundary();\n'+backend.replace(anchor,anchor+'\n        GlyphCaptureResponseBoundary();'))
  cpp=[temp/'startup.cpp',vendor,USB/'arduino/Adafruit_USBD_CDC.cpp',LEGACY/'checked_storage_unavailable.cpp',ROOT/'src/core/config_validation.cpp',ROOT/'src/core/config_button_validation.cpp',ROOT/'src/core/config_usb_default_validation.cpp',ROOT/'src/core/config_rgb_target_validation.cpp',ROOT/'config/glyph/common/src/glyph_config_validation.cpp',libs/'nanopb-arduino/src/pb_arduino.cpp',backend_copy,ROOT/'HAL/pico/src/core/RecoveryStartupDiagnostics.cpp',ROOT/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp']
  exe=temp/'dcd';run(['c++','-std=c++17',*san,*defs,'-DEXPECT_DIAGNOSTICS=1','-Dtud_task_ext=__wrap_tud_task_ext','-Ddcd_event_handler=__wrap_dcd_event_handler',*inc,*cpp,*objects,'-o',exe])
  results=[]
  cases=['pre-enable-reset','generic-unplug','capture-during-response','descriptor-dropped-reset','configured-reset','deconfigured','before-entry','pullup-off','later-recent','no-events','queue-empty','task-active-zero','later-active','task-multiple','pre-first-reset','one-reset','two-resets','continuous-reset','post-first-reset','queue-partial','queue-full','queue-failed','drop-reset','drop-setup','raw-only','dcd-setup','setup-consumed','control-began','descriptor','address-request','address-applied','configured','inspection','hardware-irq-locked','soft-irq-locked','core1-active','core1-irqs','stall-continued','stall-empty-return']
  cases += ['external-context','forced','nvic-off','global-mask','pending']+['timing-'+str(i) for i in range(7)]
  cases += ['stall-'+boundary for boundary in ['configuration-enter','configuration-return','control-enter','control-return']]
  cases += ['stall-class-'+str(i)+'-'+side for i in range(5) for side in ['enter','body','return']]
  cases += ['pre-'+x for x in ['never','empty','active','inactive','unhandled','other-panic','sof','active-stall','sof-stall','sof-queue-stall','later-irq','later-setup','no-false-inactive','queue-full','zeroed-ep','reset-only','unarmed','recent','restarted']]
  for case in cases:
   output=run([exe,fixture,case]);print(output,end='');results.append({'case':case,'output':output.strip()})
  negatives=[]
  for label,old,new,case in [
   ('irq-enter','pre_setup_observer.IrqEnter(usb_hw->ints);','/* removed */;','pre-empty'),
   ('irq-return','pre_setup_observer.IrqReturn(usb_hw->ints);','/* removed */;','pre-empty'),
   ('endpoint-enter','pre_setup_observer.EndpointEnter(ep->ep_addr,ep->active,usb_hw->buf_status,uint32_t(reinterpret_cast<uintptr_t>(ep)));','/* removed */;','pre-active'),
   ('endpoint-return','pre_setup_observer.EndpointReturn(result);','/* removed */;','pre-active'),
   ('panic','pre_setup_observer.PanicEntered(kind);','/* removed */;','pre-inactive'),
   ('sof-enter','pre_setup_observer.Event(sof,false);','/* removed */;','pre-sof'),
   ('sof-return','pre_setup_observer.Event(sof,true);','/* removed */;','pre-sof'),
   ('xfer-queue','pre_setup_observer.Queue(result);','/* removed */;','pre-active'),
   ('original-once','const bool result=__real_hw_endpoint_xfer_continue(ep);','const bool result=__real_hw_endpoint_xfer_continue(ep);__real_hw_endpoint_xfer_continue(ep);','pre-active')]:
   body=(ROOT/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp').read_text();assert old in body
   mutant=temp/(label+'.cpp');mutant.write_text(body.replace(old,new));negative=temp/(label+'-negative')
   run(['c++','-std=c++17',*san,*defs,'-DEXPECT_DIAGNOSTICS=1','-Dtud_task_ext=__wrap_tud_task_ext','-Ddcd_event_handler=__wrap_dcd_event_handler',*inc,*[mutant if p==ROOT/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp' else p for p in cpp],*objects,'-o',negative])
   out=base.run([negative,fixture,case],expected=1);assert 'FAIL:' in out;negatives.append(label);print(label+'=DETECTED')
  sampler=temp/'sampler';run(['c++','-std=c++17',*san,'-I',ROOT/'include',SETUP_HOST/'sampler.cpp','-o',sampler]);print(run([sampler]),end='')
  for label,old,new in [
   ('irq-active','active.store(entered.load());','active.store(0);'),
   ('irq-latest','latest.store(active.load());','latest.store(0);'),
   ('irq-pre','pre.store(ints);','pre.store(0);'),
   ('irq-post','post.store(ints);','post.store(0);'),
   ('ep-identity','ep_pointer.store(pointer);','ep_pointer.store(0);'),
   ('ep-address','ep_addr.store(addr);','ep_addr.store(0);'),
   ('ep-active','ep_active.store(is_active?1u:0u);','ep_active.store(0);'),
   ('ep-buffer','ep_buf.store(status);','ep_buf.store(0);'),
   ('ep-inactive','if(!is_active)bump(ep_inactive);','/* removed */;'),
   ('ep-result','ep_result.store(result?1u:0u);','ep_result.store(0);'),
   ('panic-id','panic_irq.store(active.load());','panic_irq.store(0);'),
   ('panic-class','panic_kind.store(kind);','panic_kind.store(2);'),
   ('active-sof','if(s.sof_entered>s.sof_returned)branch=Orange;','/* removed */;'),
   ('same-id-age','age>=1000000u','age>=1000001u')]:
   directory=temp/label;(directory/'core').mkdir(parents=True)
   body=(ROOT/'include/core/RecoveryPreSetupDiagnostics.hpp').read_text();assert old in body
   (directory/'core/RecoveryPreSetupDiagnostics.hpp').write_text(body.replace(old,new));negative=directory/'negative'
   run(['c++','-std=c++17',*san,'-I',directory,'-I',ROOT/'include',SETUP_HOST/'sampler.cpp','-o',negative]);out=base.run([negative],expected=1);assert 'FAIL:' in out;negatives.append(label);print(label+'=DETECTED')
  source_end={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources};assert source_end==source_start,'source changed during harness run; rerun frozen inputs'
  report={'status':'PASS','panic_abi':abi,'negative_controls':negatives,'timing_matrix':'T0..T6 extracted handler with sequential MMIO adapters; conditional SOF and BUFF_STATUS nonreturn before later SETUP','cases':results,'physical_macOS':'NOT_MODELED','source_hashes':source_end,'frozen_source_hashes_verified':True,'extracted_function_hashes':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in extract.items()},'model_boundary':'ASan/UBSan extracted pinned DCD plus actual endpoint continuation/sync/buffer functions. Host models BUFF_STATUS-derived INTR and alias-register writes; no claim BUS_RESET silicon behavior. Actual pinned USBD/CDC/HID/MSC/MIDI task/reset source and extracted XInput init/reset. Host-only event/replenishment/stall hooks; independent std::thread publisher while foreground paused. MMIO/NVIC/locks/host USB electrical completion remain models, not physical causal proof.'}
  if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=True);(args.output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:
  import traceback;traceback.print_exc();print('glyph_rt2_pre_setup: FAIL: '+str(e));raise SystemExit(1)
