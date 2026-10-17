#!/usr/bin/env python3
"""Execute exact generated warm-reset bodies and pinned class/control reset code.
Host MMIO/NVIC/SDK scheduling are explicit models; no electrical enumeration proof.
"""
import argparse,hashlib,json,os,re,subprocess,sys,tempfile
from pathlib import Path
import rt2_recovery_reinit as gen
from check_glyph_rt2_usb_startup import function
ROOT=Path(__file__).resolve().parents[1]
FRAMEWORK=Path.home()/'.platformio/packages/framework-arduinopico'
USB=FRAMEWORK/'libraries/Adafruit_TinyUSB_Arduino/src'
FIX=ROOT/'tools/fixtures/rt2_recovery_reinit_host'

def run(args):
 p=subprocess.run([str(x) for x in args],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(p.stdout+'\n'+repr([str(x) for x in args]))
 return p.stdout

def source_gates(port,usbd,dcd,app):
 required=['save_and_disable_interrupts()', 'mutex_try_enter(&__usb_mutex, NULL)', 'glyph_recovery_usb_consumed = true;', 'irq_set_enabled(USBCTRL_IRQ, false);','irq_set_enabled(USB_TASK_IRQ, false);','dcd_disconnect(0);','GlyphRecoveryDcdReset();','GlyphRecoveryUsbdReset();','irq_set_enabled(USB_TASK_IRQ, true);','irq_set_enabled(USBCTRL_IRQ, true);','dcd_connect(0);']
 body=function(port,'extern "C" bool GlyphRecoveryUsbReinitialize(')
 offsets=[body.index(x) for x in required];assert offsets==sorted(offsets)
 assert body.count('irq_clear(USBCTRL_IRQ);')==2 and body.count('irq_clear(USB_TASK_IRQ);')==2
 preflight=['get_core_num() != 0','__get_current_exception() != 0','glyph_recovery_primask() != 0','glyph_recovery_usb_consumed','!tud_inited()','!irq_is_enabled(USBCTRL_IRQ)','!irq_is_enabled(USB_TASK_IRQ)','irq_get_exclusive_handler(USB_TASK_IRQ) != usb_task_irq','!irq_has_shared_handler(USBCTRL_IRQ)','!glyph_recovery_cdc_descriptor()','!GlyphRecoveryUsbdPreflight()']
 for s in preflight:assert s in body
 assert body.count('GlyphRecoveryUsbdPreflight()')==2
 for forbidden in ['Persistence','profile_store','SaveConfig','CheckedRemove','format(', 'delay(', 'sleep', 'irq_set_pending(', 'while (','user_irq_claim','irq_add_shared_handler','mutex_init(','tud_init(','osal_queue_create','dcd_init(']:assert forbidden not in body
 assert 'usbd_reset(0);' in usbd and 'tu_fifo_clear(&_usbd_qdef.ff)' in usbd
 assert 'irq_add_shared_handler' not in dcd and 'dcd_connect(' not in dcd and '_sof_enable = false;' in dcd
 for statement in ['rp2040_usb_init();','_sof_enable = false;','tu_memclr(hw_endpoints[0], 2*sizeof(hw_endpoint_t));','hw_endpoint_init(0x0, 64, TUSB_XFER_CONTROL);','hw_endpoint_init(0x80, 64, TUSB_XFER_CONTROL);','reset_non_control_endpoints();']:assert statement in dcd
 route=function(app,'void enter_recovery_configurator(')
 assert route.index('SetRecoveryState(')<route.index('GlyphRecoveryUsbReinitialize()')<route.index('HandOffIndicator()')
 assert 'manual_rt2 && !GlyphRecoveryUsbReinitialize()' in route or 'manual_rt2&&!GlyphRecoveryUsbReinitialize()' in route
 setup=function(app,'void setup()');assert setup.count('enter_recovery_configurator(true);')==1
 assert re.search(r'if \(inputs.rt2 && !inputs.mb1\)\s*\{\s*enter_recovery_configurator\(true\);',setup)
 assert 'bool manual_rt2 = false' in app or 'bool manual_rt2=false' in app
 return required+preflight

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path);a=ap.parse_args()
 out=a.output_dir or ROOT/'local_backups/reinit/host';out.mkdir(parents=True,exist_ok=True)
 records=gen.prepare(ROOT,FRAMEWORK);generated={k:Path(v['generated']).read_text() for k,v in records.items()}
 app=(ROOT/'config/glyph/common/src/config.cpp').read_text();required=source_gates(gen.PORT_HELPER,gen.USBD_HELPER,gen._dcd_helper((ROOT/gen.PINS['dcd']['pristine']).read_bytes()),app)
 # Every required warm-reset step and preflight discriminator must matter.
 mutations=[]
 for x in required+['irq_clear(USBCTRL_IRQ);','irq_clear(USB_TASK_IRQ);']:
  bad=gen.PORT_HELPER.replace(x,'false' if x in ['get_core_num() != 0','__get_current_exception() != 0','glyph_recovery_primask() != 0','glyph_recovery_usb_consumed','!tud_inited()','!irq_is_enabled(USBCTRL_IRQ)','!irq_is_enabled(USB_TASK_IRQ)','irq_get_exclusive_handler(USB_TASK_IRQ) != usb_task_irq','!irq_has_shared_handler(USBCTRL_IRQ)','!glyph_recovery_cdc_descriptor()','!GlyphRecoveryUsbdPreflight()'] else '/* removed */')
  try:source_gates(bad,gen.USBD_HELPER,gen._dcd_helper((ROOT/gen.PINS['dcd']['pristine']).read_bytes()),app)
  except (AssertionError,ValueError):mutations.append(x)
  else:raise AssertionError('source gate accepted omitted '+x)
 for part in ['usbd_reset(0);','tu_fifo_clear(&_usbd_qdef.ff)']:
  try:source_gates(gen.PORT_HELPER,gen.USBD_HELPER.replace(part,'REMOVED'),gen._dcd_helper((ROOT/gen.PINS['dcd']['pristine']).read_bytes()),app)
  except (AssertionError,ValueError):mutations.append(part)
  else:raise AssertionError('USBD omission accepted')
 dcd_helper=gen._dcd_helper((ROOT/gen.PINS['dcd']['pristine']).read_bytes())
 for step in ['rp2040_usb_init();','_sof_enable = false;','tu_memclr(hw_endpoints[0], 2*sizeof(hw_endpoint_t));','hw_endpoint_init(0x0, 64, TUSB_XFER_CONTROL);','hw_endpoint_init(0x80, 64, TUSB_XFER_CONTROL);','reset_non_control_endpoints();']:
  try:source_gates(gen.PORT_HELPER,gen.USBD_HELPER,dcd_helper.replace(step,'/* omitted DCD reset step */'),app)
  except (AssertionError,ValueError):mutations.append('dcd:'+step)
  else:raise AssertionError('DCD omission accepted: '+step)
 for key,pin in gen.PINS.items():
  original=(ROOT/pin['pristine']).read_bytes();gen.verify_pin(original,key,'positive '+key)
  altered=bytes([original[0]^1])+original[1:]
  try:gen.verify_pin(altered,key,'negative '+key)
  except ValueError:mutations.append('altered-pinned-source:'+key)
  else:raise AssertionError('altered pinned source accepted: '+key)
 routing={key:{'object':str((out/('routing-'+key+'.o')).resolve())} for key in gen.PINS}
 counts={key:1 for key in gen.PINS};linked={key:[record['object']] for key,record in routing.items()}
 gen.validate_routing(routing,counts,linked)
 for key in gen.PINS:
  for mode in ('omitted','duplicate','original-object'):
   badcounts=dict(counts);badlinked={k:list(v) for k,v in linked.items()}
   if mode=='omitted':badcounts[key]=0;badlinked[key]=[]
   elif mode=='duplicate':badcounts[key]=2
   else:badlinked[key].append(str((out/('original-'+key+'.o')).resolve()))
   try:gen.validate_routing(routing,badcounts,badlinked)
   except ValueError:mutations.append('routing:'+key+':'+mode)
   else:raise AssertionError('invalid routing accepted: '+key+':'+mode)
 baseline=run(['git','-C',ROOT,'show','60313cde63c7161921fdef7b2c3ebaddcb15173c:config/glyph/common/src/config.cpp'])
 assert function(app,'void setup()').replace('enter_recovery_configurator(true);','enter_recovery_configurator();')==function(baseline,'void setup()'),'ordinary setup changed'
 assert function(app,'void loop()')==function(baseline,'void loop()'),'normal loop changed'
 inputs=[Path(__file__),*FIX.rglob('*'),ROOT/'tools/rt2_recovery_reinit.py',ROOT/'config/glyph/common/src/config.cpp',ROOT/'include/core/RecoveryUsbReinitialization.h']
 inputs += [p for p in USB.rglob('*') if p.suffix in ('.c','.h')]
 inputs += [ROOT/v['pristine'] for v in gen.PINS.values()]
 inputs += [p for p in (ROOT/'tools/fixtures/profile_store_cdc_progress/include').rglob('*') if p.is_file()]
 inputs += [p for p in (ROOT/'tools/fixtures/rt2_usb_startup/include').rglob('*') if p.is_file()]
 inputs += [ROOT/'tools/check_glyph_rt2_usb_startup.py']
 for key,v in records.items():
  pristine=(ROOT/gen.PINS[key]['pristine']).read_bytes();original=gen.rt2_private_dcd.patch_source(pristine) if key=='dcd' else pristine
  helper=gen._dcd_helper(pristine) if key=='dcd' else gen.USBD_HELPER if key=='usbd' else gen.PORT_HELPER
  patched=Path(v['generated']).read_bytes()
  assert patched==gen._insert(original,helper),'normal source bytes changed'
  nl=b'\r\n' if b'\r\n' in original else b'\n'
  addition=nl+helper.replace('\r\n','\n').replace('\n',nl.decode()).encode()+nl
  assert patched.count(addition)==1 and patched.replace(addition,b'',1)==original,'helper removal must recover exact normal TU'
 inputs=[p for p in inputs if p.is_file()];before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
 with tempfile.TemporaryDirectory(prefix='glyph-reinit-') as name:
  t=Path(name);inc=[FIX/'include',FIX,ROOT/'tools/fixtures/rt2_usb_startup/include',ROOT/'tools/fixtures/profile_store_cdc_progress/include',USB,USB/'arduino',*[USB/f'class/{x}' for x in ['cdc','msc','hid','midi']],ROOT/'include']
  flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-ffunction-sections','-fdata-sections','-DCFG_TUSB_CONFIG_FILE="fixture_tusb_config.h"']+[x for p in inc for x in ('-I',p)]
  objects=[]
  for stem in ['cdc','msc','hid','midi']:
   src=USB/f'class/{stem}/{stem}_device.c';text=src.read_text()
   sig=f'void {stem}d_reset(';fn=function(text,sig);text=text.replace(fn,fn.replace('{','{\n  ++class_resets['+str(['cdc','msc','hid','midi'].index(stem))+'];',1))
   text='extern unsigned class_resets[4];\n'+text
   if stem=='cdc':text+='\nvoid host_cdc_seed(void){_cdcd_itf[0].line_state=3;_cdcd_itf[0].ep_in=0x82;_cdcd_itf[0].line_coding.bit_rate=57600;_cdcd_itf[0].wanted_char=42;tu_fifo_write(&_cdcd_itf[0].rx_ff,"x");tu_fifo_write(&_cdcd_itf[0].tx_ff,"y");}\nbool host_cdc_reset_ok(void){return !_cdcd_itf[0].line_state&&!_cdcd_itf[0].ep_in&&_cdcd_itf[0].line_coding.bit_rate==57600&&_cdcd_itf[0].wanted_char==42&&tu_fifo_empty(&_cdcd_itf[0].rx_ff)&&tu_fifo_empty(&_cdcd_itf[0].tx_ff);}\n'
   if stem in ('msc','hid'):
    state='_mscd_itf' if stem=='msc' else '_hidd_itf'
    text+=f'\nvoid host_{stem}_seed(void){{memset(&{state},0x55,sizeof({state}));}}\nbool host_{stem}_reset_ok(void){{const uint8_t*p=(const uint8_t*)&{state};for(unsigned i=0;i<sizeof({state});i++)if(p[i])return false;return true;}}\n'
   if stem=='midi':
    text+='\nvoid host_midi_seed(void){memset(&_midid_itf[0],0x55,ITF_MEM_RESET_SIZE);tu_fifo_write(&_midid_itf[0].rx_ff,"x");tu_fifo_write(&_midid_itf[0].tx_ff,"y");}\nbool host_midi_reset_ok(void){const uint8_t*p=(const uint8_t*)&_midid_itf[0];for(unsigned i=0;i<ITF_MEM_RESET_SIZE;i++)if(p[i])return false;return tu_fifo_empty(&_midid_itf[0].rx_ff)&&tu_fifo_empty(&_midid_itf[0].tx_ff);}\n'
   src=t/f'{stem}.c';src.write_text(text);obj=t/f'{stem}.o';run(['cc','-std=c11',*flags,'-c',src,'-o',obj]);objects.append(obj)
  obj=t/'fifo.o';run(['cc','-std=c11',*flags,'-c',USB/'common/tusb_fifo.c','-o',obj]);objects.append(obj)
  usbd=(USB/'device/usbd.c').read_text();ctrl=(USB/'device/usbd_control.c').read_text()
  # Actual private USBD layout and reset dispatcher; host driver registry keeps
  # real reset/init pointers and uses null unused open/xfer callbacks.
  typ=usbd[usbd.index('typedef struct\n{'):usbd.index('tu_static usbd_device_t _usbd_dev;')]
  ctrltyp=ctrl[ctrl.index('typedef struct\n{'):ctrl.index('tu_static usbd_control_xfer_t _ctrl_xfer;')]
  pieces=['#include "tusb.h"\n#include "device/usbd_pvt.h"\n#include "core/RecoveryUsbReinitialization.h"\n',typ,ctrltyp,(FIX/'state.inc').read_text(),function(ctrl,'void usbd_control_reset(void)'),function(usbd,'static void configuration_reset('),function(usbd,'static void usbd_reset('),gen.USBD_HELPER]
  (t/'usbd.inc').write_text('\n'.join(pieces))
  port=gen.PORT_HELPER;dcd=gen._dcd_helper((ROOT/gen.PINS['dcd']['pristine']).read_bytes())
  port=port.replace(function(port,'static uint32_t glyph_recovery_primask('),'static uint32_t glyph_recovery_primask(void){return primask;}')
  (t/'port.inc').write_text(port);(t/'dcd.inc').write_text(dcd)
  (t/'noncontrol.inc').write_text(function((ROOT/gen.PINS['dcd']['pristine']).read_text(),'static void __tusb_irq_path_func(reset_non_control_endpoints)'))
  source=(FIX/'harness.cpp').read_text();(t/'harness.cpp').write_text(source)
  (t/'application_route.inc').write_text(function(app,'void enter_recovery_configurator('))
  binary=t/'test';run(['c++','-std=c++17','-Wno-c++11-narrowing',*flags,'-I',t,t/'harness.cpp',*objects,'-Wl,-dead_strip','-o',binary]);result=run([binary]);(out/'stdout.txt').write_text(result)
  for x in ['usbd.inc','port.inc','dcd.inc','harness.cpp']:(out/x).write_bytes((t/x).read_bytes())
 assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'input drift'
 report={'status':'PASS','host_sanitizers':['ASan','UBSan'],'runtime_cases':int(re.search(r'host_cases=(\d+)',result)[1]),'repeated_fresh_constructions':64,'normal_setup_loop_source_unchanged':True,'routing_positive':True,'routing_negative_controls':9,'pinned_source_negative_controls':3,'dcd_step_negative_controls':6,'generated_normal_bytes_inverse':True,'source_negative_controls':len(mutations),'removed_step_controls':mutations,'stdout':result,'inputs':before,'generated':records,'limits':['SDK MMIO/NVIC/mutex/peripheral-reset/EP0-register addressing are modeled; exact generated DCD helper and original noncontrol reset body execute.','Actual four class C reset/FIFO and USBD/control reset bodies execute; driver registry reset/init pointers mirror source mapping.','Application route body executes with persistence/Serial/backend dependencies stubbed; no standalone end-to-end persistent-safety proof.','CDC positive descriptor bytes use actual TUD_CDC_DESCRIPTOR macro and documented Adafruit assignment; full production descriptor builder is not executed in this harness.','No electrical detach/attach, host USB timing or physical enumeration acceptance.']}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('inputs','generated','stdout')},indent=2));print(result)
if __name__=='__main__':main()
