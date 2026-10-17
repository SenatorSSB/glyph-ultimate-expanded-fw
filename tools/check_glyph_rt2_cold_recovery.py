#!/usr/bin/env python3
"""Execute cold boot policy, real USB descriptor/stack/backend and source mutations.

SDK/MMIO/NVIC and reset/electrical boundaries remain explicit host doubles.
"""
import argparse,hashlib,json,os,subprocess,sys,tempfile,shutil
from pathlib import Path
from check_glyph_stage_b_ultimate_profiles import ROOT,NANOPB,SPEC,STAGE_A,STAGE_C,make_v3_artifact
from check_glyph_profile_store_littlefs_host import FRAMEWORK
import glyph_serial_config_tool as transport
HOST=ROOT/'tools/fixtures/rt2_usb_startup'
COLD=ROOT/'tools/fixtures/rt2_cold_recovery_host'
LEGACY=ROOT/'tools/fixtures/profile_store_timeout_host'
def run(args,expected=0):
 p=subprocess.run(list(map(str,args)),cwd=ROOT,text=True,capture_output=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
 if (p.returncode==0)!=(expected==0):raise RuntimeError(' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
 return p.stdout+p.stderr

def function(text,signature):
 # Extract the current route without renaming or duplicating its policy.
 if signature == 'void enter_recovery_configurator()' and signature not in text:
  import re
  signature = re.search(r'void enter_recovery_configurator\([^)]*\)',text)[0]
 start=text.index(signature);end=text.index('{',start);depth=1;end+=1
 while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[start:end]


def boot_io_gate(source):
 import re
 if re.search(r'\b(?:LittleFS|Persistence|ProfileStore|profile_store|fopen|ofstream|SaveConfig|BeginRecovery)\b', source):
  raise AssertionError('boot intent must not depend on persistent storage')

def main():
 import re
 ap=argparse.ArgumentParser(description='Actual cold boot intent, strong init, descriptor builder, port/DCD init and bounded read-only CDC backend.');ap.add_argument('--output-dir',type=Path);a=ap.parse_args()
 out=a.output_dir or ROOT/'local_backups/cold/host';out.mkdir(parents=True,exist_ok=True)
 usb=FRAMEWORK/'libraries/Adafruit_TinyUSB_Arduino/src';device=(usb/'arduino/Adafruit_USBD_Device.cpp').read_text();app=(ROOT/'config/glyph/common/src/config.cpp').read_text();cold=ROOT/'HAL/pico/src/core/ColdRecoveryBoot.cpp';shim=ROOT/'HAL/pico/src/core/ColdRecoveryUsbInit.c'
 inputs=[p for parent in [COLD,HOST,LEGACY,usb,ROOT/'include',ROOT/'HAL/pico/include',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',ROOT/'schema/haybox',ROOT/'tools/fixtures/profile_store_cdc_progress/include',NANOPB,ROOT/'.pio/libdeps/glyph_mk6/nanopb-arduino/src',ROOT/'.pio/libdeps/glyph_mk6/PacketIO/src'] for p in parent.rglob('*') if p.is_file()]+[cold,shim,ROOT/'config/glyph/common/src/config.cpp',ROOT/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp',ROOT/'HAL/pico/src/core/RecoveryStartupDiagnostics.cpp',ROOT/'HAL/pico/src/core/ProfileStore.cpp',ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp',ROOT/'src/core/config_validation.cpp',ROOT/'src/core/config_button_validation.cpp',ROOT/'src/core/config_usb_default_validation.cpp',ROOT/'src/core/config_rgb_target_validation.cpp',ROOT/'config/glyph/common/src/glyph_config_validation.cpp',ROOT/'tools/check_glyph_rt2_usb_startup.py',ROOT/'tools/check_glyph_stage_b_ultimate_profiles.py',ROOT/'tools/check_glyph_profile_store_littlefs_host.py',ROOT/'tools/glyph_serial_config_tool.py',ROOT/'tools/fixtures/profile_store_selection_recovery_host/setup_routes.cpp',Path(__file__)]
 inputs += [SPEC,STAGE_A,STAGE_C]
 inputs=[p for p in inputs if "__pycache__" not in p.parts]
 before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
 boot_io_gate(cold.read_text()+(ROOT/'include/core/ColdRecoveryIntent.hpp').read_text())
 with tempfile.TemporaryDirectory(prefix='glyph-cold-') as directory:
  t=Path(directory);gen=t/'generated';gen.mkdir();overlay=t/'overlay';(overlay/'core').mkdir(parents=True);(overlay/'arduino').mkdir();(overlay/'hardware/structs').mkdir(parents=True);(overlay/'pico').mkdir();shutil.copytree(LEGACY/'include',overlay,dirs_exist_ok=True)
  stubs=(LEGACY/'include/host_stubs.hpp').read_text();stubs=stubs[:stubs.index('struct TinyUSBDeviceStub')]+stubs[stubs.index('inline void reboot_firmware()'):];(overlay/'host_stubs.hpp').write_text(stubs)
  (overlay/'Arduino.h').write_text('#include "host_stubs.hpp"\nvoid yield();\n');(overlay/'Stream.h').write_text('#include "host_stubs.hpp"\n')
  (overlay/'arduino/Adafruit_USBD_Device.h').write_text('#include '+json.dumps(str(usb/'arduino/Adafruit_USBD_Device.h'))+'\n')
  persistence=(LEGACY/'include/core/Persistence.hpp').read_text().replace('class Persistence {','extern void USBTestDuringInspection();\nclass Persistence {').replace(' public:',' public:\n  bool SetValidator(ConfigSemanticValidator){return true;}\n  bool IsAvailable(){return true;}').replace('    ++load_calls;','    ++load_calls; USBTestDuringInspection();');(overlay/'core/Persistence.hpp').write_text(persistence)
  (overlay/'hardware/watchdog.h').write_text('#pragma once\n#include <stdint.h>\nstruct WatchdogHw{uint32_t scratch[8]={};uint32_t reason=0;};extern WatchdogHw watchdog_registers;\n#define watchdog_hw (&watchdog_registers)\n')
  (overlay/'hardware/structs/usb.h').write_text('#pragma once\n#include <stdint.h>\nstruct UsbHw{uint32_t sie_ctrl=0,pwr=0,main_ctrl=0,inte=0;};extern UsbHw usb_registers;\n#define usb_hw (&usb_registers)\n#define USB_SIE_CTRL_PULLUP_EN_BITS 1u\n')
  (overlay/'pico/platform.h').write_text('#pragma once\ninline unsigned get_core_num(){return 0;}\ninline unsigned __get_current_exception(){return 0;}\n')
  (overlay/'pico/critical_section.h').write_text('#pragma once\n#ifdef __cplusplus\nextern "C" {\n#endif\nextern unsigned critical_initializations;\nstruct critical_section{unsigned held;};\nstatic inline void critical_section_init(struct critical_section*s){s->held=0;++critical_initializations;}\nstatic inline void critical_section_enter_blocking(struct critical_section*s){++s->held;}\nstatic inline void critical_section_exit(struct critical_section*s){--s->held;}\n#ifdef __cplusplus\n}\n#endif\n')
  run([sys.executable,NANOPB/'generator/nanopb_generator.py','-I',ROOT/'schema/haybox','-f',ROOT/'schema/haybox/config.options','--error-on-unmatched','--no-timestamp','-D',gen,ROOT/'schema/haybox/config.proto'])
  pb,jf,_=transport.load_runtime_proto_modules(ROOT);_,data=transport.encode_artifact_payload(make_v3_artifact(),pb,jf);fixture=t/'config.pb';fixture.write_bytes(data)
  libs=ROOT/'.pio/libdeps/glyph_mk6';includes=[overlay,HOST/'include',ROOT/'tools/fixtures/profile_store_cdc_progress/include',LEGACY/'include',usb/'arduino',usb,ROOT/'HAL/pico/include',ROOT/'include',gen,NANOPB,libs/'nanopb-arduino/src',libs/'PacketIO/src',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',COLD,t]
  inc=[item for p in includes for item in ['-I',p]];san=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'];defs=['-DCFG_TUSB_CONFIG_FILE="fixture_tusb_config.h"','-DARDUINO=1','-DUSE_TINYUSB=1','-DGLYPH_CDC_COORDINATION_TEST=1','-DGLYPH_STRICT_HARDENING_CANDIDATE=1','-DGLYPH_RT2_COLD_RECOVERY_CANDIDATE=1','-DGLYPH_RECOVERY_DIAGNOSTICS_HOST=1','-DEXPECT_DIAGNOSTICS=1','-fshort-enums']
  intent=t/'intent';run(['c++','-std=c++17',*san,'-I',ROOT/'include',COLD/'intent.cpp','-o',intent]);intent_result=run([intent]);(out/'intent-stdout.txt').write_text(intent_result)
  objects=[]
  for src in [NANOPB/'pb_common.c',NANOPB/'pb_decode.c',NANOPB/'pb_encode.c',gen/'config.pb.c',usb/'device/usbd.c',usb/'device/usbd_control.c',usb/'common/tusb_fifo.c',usb/'tusb.c',usb/'class/cdc/cdc_device.c',usb/'class/hid/hid_device.c',usb/'class/msc/msc_device.c',usb/'class/midi/midi_device.c',shim]:
   obj=t/(src.stem+'.o');run(['cc','-std=c11',*san,*defs,*inc,'-c',src,'-o',obj]);objects.append(obj)
  for src,extra in [(ROOT/'HAL/pico/src/core/ProfileStore.cpp',['-Dprofile_store=production_profile_store']), (cold,[]),(usb/'arduino/Adafruit_USBD_CDC.cpp',[]),(ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp',[]),(ROOT/'HAL/pico/src/core/RecoveryStartupDiagnostics.cpp',[]),(LEGACY/'checked_storage_unavailable.cpp',[]),(ROOT/'src/core/config_validation.cpp',[]),(ROOT/'src/core/config_button_validation.cpp',[]),(ROOT/'src/core/config_usb_default_validation.cpp',[]),(ROOT/'src/core/config_rgb_target_validation.cpp',[]),(ROOT/'config/glyph/common/src/glyph_config_validation.cpp',[]),(libs/'nanopb-arduino/src/pb_arduino.cpp',[])]:
   obj=t/(src.stem+'.o');run(['c++','-std=c++17',*san,*defs,*extra,*inc,'-c',src,'-o',obj]);objects.append(obj)
  portable=t/'Adafruit_USBD_Device.cpp';portable_text=device.replace('(uint32_t)_desc_str_arr[STRID_LANGUAGE]','(uintptr_t)_desc_str_arr[STRID_LANGUAGE]')
  for sig,hook in [('bool Adafruit_USBD_Device::begin(uint8_t rhport)','USBColdDeviceBegin'),('void Adafruit_USBD_Device::clearConfiguration(void)','USBColdDescriptorClear')]:
   fn=function(portable_text[portable_text.rfind(sig):],sig);portable_text=portable_text.replace(fn,fn.replace('{','{\n'+hook+'();',1))
  portable.write_text('extern void USBColdDeviceBegin();\nextern void USBColdDescriptorClear();\n'+portable_text)
  obj=t/'Adafruit_USBD_Device.o';run(['c++','-std=c++17',*san,*defs,*inc,'-c',portable,'-o',obj]);objects.append(obj)
  (t/'retained_timeout_harness.inc').write_text((LEGACY/'timeout_harness.cpp').read_text())
  rec=function(app,'void enter_recovery_configurator()');rec=rec.replace('recovery_configurator->SetRecoveryState(recovery.config_invalid, recovery.storage_available);','recovery_configurator->SetRecoveryState(recovery.config_invalid, recovery.storage_available); USBColdReadOnlyReady();');loop=function(app,'void loop()');start=loop.index('    if (read_boot_state().outcome == BootOutcome::RecoveryConfigurator)');i=loop.index('{',start);end=i+1;depth=1
  while depth:depth+=(loop[end]=='{')-(loop[end]=='}');end+=1
  (t/'recovery_route.inc').write_text(rec);(t/'recovery_loop.inc').write_text('void recovery_loop(){'+loop[start:end]+'}\n')
  retained=(HOST/'startup.cpp').read_text().replace('int main(int argc,char**argv)', 'int retained_usb_startup_main(int argc,char**argv)');retained=retained.replace('void TinyUSB_Port_InitDevice(uint8_t port)', 'void unused_legacy_port(uint8_t port)').replace('void TinyUSB_Device_Task()', 'void __real_TinyUSB_Device_Task()').replace('void TinyUSB_Device_FlushCDC()', 'void __real_TinyUSB_Device_FlushCDC()').replace('void dcd_init(uint8_t)', 'void unused_legacy_dcd_init(uint8_t)')
  retained=retained.replace('void mutex_init(mutex_t*m){m->held=false;}','void mutex_init(mutex_t*m){if(m==&__usb_mutex)++mutex_initializations;m->held=false;}')
  pre='void USBColdReadOnlyReady();\nextern bool cold_readonly_ready;\nbool GlyphRecoveryUsbReinitialize();\nextern unsigned mutex_initializations;\nextern "C" void __wrap_TinyUSB_Device_Task();\nextern "C" void __wrap_TinyUSB_Device_FlushCDC();\n'
  (t/'retained_startup.cpp').write_text(pre+retained)
  port=(usb/'arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp').read_text();dcd=(usb/'portable/raspberrypi/rp2040/dcd_rp2040.c').read_text();diag=(ROOT/'HAL/pico/src/core/RecoveryUsbDiagnostics.cpp').read_text()
  prefix='''#include <cassert>
#include "pico/platform.h"
unsigned descriptor_preparations=0,descriptor_clears=0;\nunsigned port_calls=0,mutex_initializations=0,critical_initializations=0,task_claims=0,task_registrations=0,trigger_registrations=0,dcd_registrations=0;
static unsigned USB_TASK_IRQ;
static constexpr unsigned USBCTRL_IRQ=5;
static bool in_port=false,port_complete=false;
#define PICO_SDK_VERSION_MAJOR 1
#define PICO_SDK_VERSION_MINOR 5
#define PICO_SHARED_IRQ_HANDLER_LOWEST_ORDER_PRIORITY 0
#define PICO_SHARED_IRQ_HANDLER_HIGHEST_ORDER_PRIORITY 255
#define FORCE_VBUS_DETECT 1
#define USB_USB_PWR_VBUS_DETECT_BITS 1u
#define USB_USB_PWR_VBUS_DETECT_OVERRIDE_EN_BITS 2u
#define USB_MAIN_CTRL_CONTROLLER_EN_BITS 1u
#define USB_SIE_CTRL_EP0_INT_1BUF_BITS 4u
#define USB_INTS_BUFF_STATUS_BITS 16u
#define USB_INTS_BUS_RESET_BITS 32u
#define USB_INTS_SETUP_REQ_BITS 64u
#define USB_INTS_DEV_SUSPEND_BITS 128u
#define USB_INTS_DEV_RESUME_FROM_HOST_BITS 256u
#define USB_INTS_DEV_CONN_DIS_BITS 512u
struct hw_endpoint_t {unsigned dummy;};static hw_endpoint_t hw_endpoints[16][2];
static void rp2040_usb_init() {require(!attached,"cold hardware init begins unattached");}
static void hw_endpoint_init(unsigned,unsigned,unsigned){}
static void reset_non_control_endpoints(){}
static void dcd_rp2040_irq(){}
static int user_irq_claim_unused(bool required){require(required,"original required IRQ claim");++task_claims;return 31;}
static void irq_set_exclusive_handler(unsigned irq,void(*)()){require(irq==USB_TASK_IRQ,"task IRQ exact");++task_registrations;}
static void irq_set_enabled(unsigned,bool){}
static void irq_set_pending(unsigned){}
static void irq_add_shared_handler(unsigned,void(*handler)(),unsigned order){if(order==255){require(handler==dcd_rp2040_irq,"DCD callback exact");++dcd_registrations;}else ++trigger_registrations;}
'''
  port_body=function(port,'void TinyUSB_Port_InitDevice(uint8_t rhport)').replace('void TinyUSB_Port_InitDevice(uint8_t rhport)','void GlyphRealPortInit(uint8_t rhport)').replace('{','{\n++port_calls;port_initialized=true;\nrequire(recovery_configurator || !GlyphColdRecoveryBoot(),"cold backend exists before hardware attach");\nif(GlyphColdRecoveryBoot()){require(cold_readonly_ready,\"read-only backend policy before attach\");const uint8_t*d=tud_descriptor_device_cb();require(d[8]==0x8a&&d[9]==0x2e&&d[10]==0x92&&d[11]==0x10,"final recovery identity before port init");}\n',1)
  dcd_body=function(dcd,'void dcd_init (uint8_t rhport)')
  wrap=function(diag,'void GlyphWrapPortInit(uint8_t port)')
  (t/'cold_port_dcd.inc').write_text(prefix+function(port,'static void usb_task_irq(void)')+'\n'+function(port,'static void usb_task_trigger_irq(void)')+'\nextern "C" {\n'+dcd_body+'\n}\n'+port_body+'\n'+wrap)
  binary=t/'cold';run(['c++','-std=c++17',*san,*defs,*inc,COLD/'cold_startup.cpp',*objects,'-o',binary])
  results=[]
  for mode in ['ordinary','random','mode-marker','diag-marker','wrong-reason','bad-selectors','arm','cold','prepare-failure','start-failure']:
   result=run([binary,fixture,mode]);results.append({'case':mode,'output':result.strip()});print(result,end='')
  negatives=[]
  original_cold=cold.read_text();original_port=(t/'cold_port_dcd.inc').read_text();original_intent=(ROOT/'include/core/ColdRecoveryIntent.hpp').read_text()
  cold_obj=t/'ColdRecoveryBoot.o';unchanged=[o for o in objects if o!=cold_obj]
  def mutate_usb(name,*,cs=None,route=None,port_text=None,intent_text=None):
   m=t/('mutant-'+name);(m/'core').mkdir(parents=True)
   source=m/'cold.cpp';source.write_text(original_cold if cs is None else cs)
   if intent_text is not None:(m/'core/ColdRecoveryIntent.hpp').write_text(intent_text)
   mo=m/'cold.o';run(['c++','-std=c++17',*san,*defs,'-I',m,*inc,'-c',source,'-o',mo])
   (t/'recovery_route.inc').write_text(rec if route is None else route);(t/'cold_port_dcd.inc').write_text(original_port if port_text is None else port_text)
   exe=m/'run';run(['c++','-std=c++17',*san,*defs,*inc,COLD/'cold_startup.cpp',*unchanged,mo,'-o',exe])
   failure=run([exe,fixture,'cold'],expected=1);assert 'FAIL:' in failure,name+' did not fail a runtime invariant'
   negatives.append({'name':name,'kind':'production-runtime-mutation','diagnostic':failure.strip()});(out/(name+'.txt')).write_text(failure)
  def changed(text,old,new):
   assert old in text,old
   return text.replace(old,new,1)
  mutate_usb('marker-only-after-early-init',cs=changed(original_cold,'if (ColdRecoveryIntent::Consume(', 'if (false && ColdRecoveryIntent::Consume('))
  mutate_usb('ordinary-hardware-on-boot-B',cs='extern void GlyphRealPortInit(unsigned char);\n'+changed(original_cold,'cold_boot.store(1, std::memory_order_release);','cold_boot.store(1, std::memory_order_release); GlyphRealPortInit(rhport);'))
  mutate_usb('duplicate-port-start',cs=changed(original_cold,'TinyUSB_Port_InitDevice(saved_port);','TinyUSB_Port_InitDevice(saved_port); TinyUSB_Port_InitDevice(saved_port);'))
  final='recovery_configurator->SetRecoveryState(recovery.config_invalid, recovery.storage_available);'
  mutate_usb('descriptor-clear-after-identity',route=changed(rec,final,final+' TinyUSBDevice.clearConfiguration();'))
  mutate_usb('pullup-before-final-identity',cs='extern void GlyphRealPortInit(unsigned char);\n'+changed(original_cold,'phase.store(Prepared, std::memory_order_release);','GlyphRealPortInit(saved_port); phase.store(Prepared, std::memory_order_release);'))
  mutate_usb('duplicate-task-irq-claim',port_text=changed(original_port,'USB_TASK_IRQ = user_irq_claim_unused(true);','USB_TASK_IRQ = user_irq_claim_unused(true); user_irq_claim_unused(true);'))
  reg='irq_add_shared_handler(USBCTRL_IRQ, dcd_rp2040_irq, PICO_SHARED_IRQ_HANDLER_HIGHEST_ORDER_PRIORITY);'
  mutate_usb('duplicate-dcd-handler',port_text=changed(original_port,reg,reg+reg))
  mutate_usb('same-boot-warm-reset',route=changed(rec,'    if (cold_recovery) {','    GlyphRecoveryUsbReinitialize();\n    if (cold_recovery) {'))
  mutate_usb('marker-not-one-shot',intent_text=changed(original_intent,'scratch[2] = 0;','/* removed clear */'))
  mutate_usb('mode-marker-collision',intent_text=changed(original_intent,'0x43525432u','0x4d445354u'))
  try:boot_io_gate(original_cold+'\nvoid persist_intent(){LittleFS.open("intent");}\n')
  except AssertionError:negatives.append({'name':'persistent-boot-intent','kind':'persistent-dependency-source-gate','detected':True})
  else:raise AssertionError('persistent boot intent accepted')
  (t/'recovery_route.inc').write_text(rec);(t/'cold_port_dcd.inc').write_text(original_port)
  # Actual setup routes, with dependencies stubbed as in the retained focused
  # regression. These mutations alter the extracted production setup body.
  setup=function(app,'void setup()');whole_loop=function(app,'void loop()');route_fixture=ROOT/'tools/fixtures/profile_store_selection_recovery_host/setup_routes.cpp'
  def route_case(name,setup_source,mode,expected=0):
   m=t/('route-'+name);m.mkdir();(m/'extracted_setup.inc').write_text(rec.replace(' USBColdReadOnlyReady();','')+'\n'+setup_source+'\n'+whole_loop)
   exe=m/'run';run(['c++','-std=c++17',*san,'-fshort-enums','-DGLYPH_RT2_COLD_RECOVERY_CANDIDATE=1','-I',m,'-I',gen,'-I',NANOPB,'-I',ROOT/'include',route_fixture,'-o',exe])
   result=run([exe,mode],expected=expected)
   if expected:negatives.append({'name':name,'kind':'actual-setup-runtime-mutation','diagnostic':result.strip()})
   else:results.append({'case':'actual-setup-'+mode,'output':result.strip()})
  for mode in ['manual','automatic','filesystem','mb1','cold','cold-mb1','arm-conflict','reboot-return','prepare-failure','start-failure']:route_case(mode,setup,mode)
  route_case('automatic-recovery-arms-cold',changed(setup,'if (load_result != Persistence::LoadResult::Loaded) {','if (load_result != Persistence::LoadResult::Loaded) { GlyphColdRecoveryArm(); reboot_firmware();'), 'automatic',1)
  route_case('MB1-priority-lost',changed(setup,'if (inputs.rt2 && !inputs.mb1)', 'if (inputs.rt2)'), 'mb1',1)
  assert len(negatives)==13
  for name in ['recovery_route.inc','cold_port_dcd.inc','retained_startup.cpp','Adafruit_USBD_Device.cpp']:(out/name).write_bytes((t/name).read_bytes())
 assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'input drift'
 report={'status':'PASS','intent':intent_result.strip(),'usb_cases':results,'required_negative_controls':negatives,'positive_cases':21+len(results),'required_owner_matrix':{'boot_control':['ordinary original-point init exactly once','Boot A marker and one reboot before storage','MB1+RT2 bootloader priority','exact marker consume once','marker clear before Boot B route','Boot B no reboot','later unmarked reset ordinary','random scratch rejected','mode namespace disjoint','diagnostic namespace disjoint','scratch4-7 untouched'],'USB_lifecycle':['ordinary actual begin/port once','Boot B early port/tud/attach absent','actual descriptor/CDC prepare once','actual VID/PID final before port','port hardware once','global USB mutex once','actual USBD queue once','queue critical section once','task IRQ claim once','DCD handler once','task-trigger handler once','attach after identity and read-only backend','no warm reset','no detach/attach retry','files unchanged'],'recovery_application':['Boot B before matrix/display','actual inspection-only initializer','actual Configurator before attach','read-only flags call before attach and actual STATUS','actual bounded CDC protocol including GET_CONFIG','no gameplay constructors','actual CDC-only configuration','Config/store mutation refusals and file bytes unchanged','prepare/start failure refused no retry/fallback'],'coverage':'assertions overlap across21 actual intent +10 actual strong-init/USB cases +10 actual setup cases; no35 independent-case claim'},'sanitizers':['ASan','UBSan'],'source_hashes':before,'limits':['Actual strong C shim and cold-control TU execute with real Adafruit descriptor builder/CDC/USBD/backend/ProfileStore.','Exact pinned port init and DCD init bodies execute with endpoint/MMIO/NVIC/SDK boundary doubles. Hardware constants here select source branches; no register electrical behavior is inferred.','Readonly-ready/descriptor begin/clear and port-entry counters are observation-only host adaptations; actual code bodies/policy execute. One persistent-intent negative is an explicit source dependency gate; remaining12 are executable production mutations.','Optional weak callback boundaries use null/no-op defaults; target XInput app-driver/BOS/vendor overrides are omitted from this pure-CDC host closure. Final target source/ELF proof remains separate.','No physical USB recognition, watchdog reset/ROM timing or whole-device acceptance.']}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('glyph_rt2_cold_recovery=PASS');return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:print('glyph_rt2_cold_recovery=FAIL: '+str(e));raise SystemExit(1)
