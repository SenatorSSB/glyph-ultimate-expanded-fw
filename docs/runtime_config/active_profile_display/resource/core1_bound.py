import json,re
from pathlib import Path
import argparse
p=argparse.ArgumentParser();p.add_argument('--output-dir',required=True);a=p.parse_args();O=Path(a.output_dir)
F=json.load(open(O/'functions.json'));V=json.load(open(O/'vtables.json'))
D={};notes={};special={};exclude={};edges={}
def find(s):
 names=[n for n in F if n.startswith(s)]
 if len(names)!=1:raise KeyError((s,names))
 return names[0]
def leaf(n,b,why):special[n]=b;notes[n]=why
# Integer/float wrapper and veneer bound64 includes all relevant branch/state-save/B0 dispatch alternatives.
for n in F:
 if n.startswith(('__wrap___aeabi_','____wrap___aeabi_')) and not any(t in n for t in ['mem','dadd','dsub','dmul','ddiv','dcmp','d2','i2d','ui2d','ul2d','l2d','double']):leaf(n,64,'Conservative actual integer/single-float child64; numeric CFG+ROM table proof.')
for n,b in [('__wrap_memset',8),('__wrap___aeabi_memcpy',12),('__aeabi_llsr',0),('____aeabi_llsr_veneer',4),('sleep_us',512),('sleep_until',496),('sleep_ms',520),('best_effort_wfe_or_timeout',512)]:
 if n in F:leaf(n,b,'ROM memory or fixed16-node time helper bound; conservative retained alternatives.')
# SDK no-RTOS route, excludes allocation backedge in unreachable FreeRTOS lock branch.
for n in ['__retarget_lock_acquire','__retarget_lock_acquire_recursive','__retarget_lock_release','__retarget_lock_release_recursive']:
 leaf(n,24,'__freeRTOSinitted false; own8 + veneer4 + mutex maximum12, conservatively additive.')
leaf('reboot_bootloader()',32,'own8+max(lookup8, ROM reset16), rounded32.')
# Function pointers/virtual slots; actual object class set pinned by source and exact vtable words.
GFXS=[x['name'] for x in V['vtable for Adafruit_SSD1306'] if x['offset_from_vptr']>=0 and x['name']]
START='Adafruit_GFX::startWrite()'
PIX=find('Adafruit_SSD1306::drawPixel(');VERT=find('Adafruit_SSD1306::drawFastVLine(');HORIZ=find('Adafruit_SSD1306::drawFastHLine(')
WP=find('Adafruit_GFX::writePixel(');WV=find('Adafruit_GFX::writeFastVLine(');WH=find('Adafruit_GFX::writeFastHLine(');WL=find('Adafruit_GFX::writeLine(');WF=find('Adafruit_GFX::writeFillRect(');FR=find('Adafruit_GFX::fillRect(')
for p,targets in [('writePixel(',[PIX]),('writeFastVLine(',[VERT]),('writeFastHLine(',[HORIZ]),('writeLine(',[WP]),('writeFillRect(',[FR]),('fillRect(',[START,WV]),('drawRect(',[START,WV,WH]),('fillScreen(',[FR]),('drawLine(',[START,WV,WH,WL]),('drawCircle(',[START,WP]),('fillCircle(',[START,WV]),('drawBitmap(',[START,WP]),('drawChar(',[START,WP,WF])]:
 D[find('Adafruit_GFX::'+p)]=targets
D['arduino::Print::write(unsigned char const*, unsigned int)']=['Adafruit_GFX::write(unsigned char)']
for n in F:
 if n.startswith('arduino::Print::') and F[n]['indirect'] and n not in D:
  D[n]=['arduino::Print::write(unsigned char const*, unsigned int)','Adafruit_GFX::write(unsigned char)']
# SSD1306 constructed with non-null Wire1; SPI branch unreachable. Conservatively union all used I2C slots.
WIRE=[find('TwoWire::setClock('),find('TwoWire::beginTransmission('),'TwoWire::write(unsigned char)','TwoWire::write(unsigned char const*, unsigned int)','TwoWire::endTransmission()','TwoWire::endTransmission(bool)']
for n in F:
 if n.startswith('Adafruit_SSD1306::') and F[n]['indirect']:D[n]=WIRE
D['TwoWire::write(unsigned char const*, unsigned int)']=['TwoWire::write(unsigned char)']
D['TwoWire::endTransmission()']=['TwoWire::endTransmission(bool)']
D['TwoWire::_handleTimeout(bool)']=['TwoWire::end()','TwoWire::begin()','TwoWire::setClock(unsigned long)']
D['i2c_write_blocking_internal']=['check_single_timeout_us'];D['i2c_read_blocking_internal']=['check_single_timeout_us']
# Concrete NEOPIXEL<11> table plus only installed power callback.
LED=[x['name'] for x in V['vtable for NEOPIXEL<(unsigned char)11>'] if x['name'] and x['offset_from_vptr']>=0]
INIT=find('ClocklessController<') if False else next(n for n in LED if n.endswith('::init()'))
SHOWPIX=next(n for n in LED if '::showPixels(' in n)
CSHOW=next(n for n in LED if '::show(CRGB' in n);CCOLOR=next(n for n in LED if '::showColor(' in n)
D['CFastLED::addLeds(CLEDController*, CRGB*, int, int)']=[INIT,next(n for n in LED if 'getMaxRefreshRate' in n)]
D['CFastLED::show(unsigned char)']=[CSHOW,'calculate_max_brightness_for_power_mW(unsigned char, unsigned long)']
D['CFastLED::showColor(CRGB const&, unsigned char)']=[CCOLOR,'calculate_max_brightness_for_power_mW(unsigned char, unsigned long)']
D['calculate_max_brightness_for_power_mW(unsigned char, unsigned long)']=['CLEDController::size()']
for n in [CSHOW,CCOLOR,'CLEDController::clearLeds(int)']:
 D[n]=[SHOWPIX] if 'clearLeds' not in n else [CCOLOR,SHOWPIX]
# Backend accessors have zero allocation, regardless currently chosen backend.
ACCESS=['CommunicationBackend::SetGameMode(InputMode*)','CommunicationBackend::CurrentGameMode()','InputMode::GetConfig()','CommunicationBackend::BackendId()']
DISP_UP=[n for n in F if re.match(r'(ConfigMenu|InputDisplay|RemapMenu|RgbBrightnessMenu|AboutMenu|MenuButtonHints|OopsieMenu)::UpdateDisplay\(',n)]
DISP_CTRL=[n for n in F if re.match(r'(ConfigMenu|DefaultConfigMenu|InputDisplay|RemapMenu|RgbBrightnessMenu|AboutMenu|MenuButtonHints|OopsieMenu)::HandleControls\(',n)]
ACTIONS=[n for n in F if n.startswith('DefaultConfigMenu::') and ('lambda' in n or '::Set' in n)]+[n for n in F if n.startswith('GlyphConfigMenu::Set')]
LAMBDAS=[n for n in F if n.startswith('setup1::{lambda')]
D['IntegratedDisplay::SendReport()']=DISP_UP+LAMBDAS+['DisplayMode::GetId()'] if 'DisplayMode::GetId()' in F else DISP_UP+LAMBDAS
D['IntegratedDisplay::HandleControls(DisplayMode*)']=DISP_CTRL
D['IntegratedDisplay::Clear()']=[find('Adafruit_SSD1306::clearDisplay(')]+LAMBDAS
D['IntegratedDisplay::UpdateDisplay()']=[find('Adafruit_SSD1306::display(')]+LAMBDAS
# Source virtual callback families are intentionally over-approximated with actual concrete graph leaves only.
for n in F:
 if n in DISP_UP:D[n]=GFXS+ACCESS
 elif n in DISP_CTRL:D[n]=ACTIONS+ACCESS+['GlyphConfigMenu::ReturnToDashboard(IntegratedDisplay*)'] if n.startswith('ConfigMenu::') else ACCESS
 elif n in ACTIONS and F[n]['indirect']:D[n]=GFXS+ACCESS
 elif n.startswith(('MenuButtonHints::MenuButtonHints(','MenuButtonHints::UpdateButtonHints(','DefaultConfigMenu::DefaultConfigMenu(','GlyphConfigMenu::GlyphConfigMenu(')) and F[n]['indirect'] and n not in D:D[n]=ACCESS
D['setup1']=[INIT,'IntegratedDisplay::SendReport()']+ACCESS
D['loop1']=['IntegratedDisplay::SendReport()',find('NeoPixelBackend<(unsigned char)11, 76>::SetGameMode('),find('NeoPixelBackend<(unsigned char)11, 76>::SendReport(')]+ACCESS
# New source-owned virtual resolvers and native request action.
RESOLVE=[n for n in F if n.startswith(('ConfigMenu::ResolveItem(', 'DefaultConfigMenu::ResolveItem('))]
for n in DISP_UP+DISP_CTRL:
 if n.startswith('ConfigMenu::'):D[n]+=RESOLVE
# Remove source-infeasible alternate hardware/fault/RTOS calls; no arbitrary-corruption support.
faults={'panic','hard_assertion_failure','__hard_assertion_failure_veneer','assert_failed','__assert_func'}
unknown=[];reachable=set();stack=[];memo={};paths={}
addr_to_name={int(x['address'],16):n for n,x in F.items()}
def calc(n):
 if n in special:return special[n],[n]
 if n in memo:return memo[n],paths[n]
 if n in stack:raise RuntimeError('cycle '+repr(stack[stack.index(n):]+[n]))
 if n not in F:unknown.append(('missing',n));return 0,[n]
 stack.append(n);reachable.add(n);x=F[n];es=[]
 for e in x['calls']+x['tail']:
  if e['name'] not in faults:es.append(e['name'])
  else:exclude.setdefault(n,[]).append(e['name'])
 if x['indirect']:
  if n not in D:unknown.append(('indirect',n,x['indirect']))
  else:es+=D[n]
 # veneers release transient r0 before tail BX; retaining it conservatively is safe.
 if n.endswith('_veneer') and not es:
  a=int(x['address'],16);text=(O/'disassembly.txt').read_text();m=re.search(r'^'+format(a+12,'x')+r':.*?\.word\s+0x([\da-f]+)',text,re.M)
  if m:
   dst=int(m[1],16)&~1
   if dst in addr_to_name:es.append(addr_to_name[dst])
   else:unknown.append(('veneer',n,hex(dst)))
  else:unknown.append(('veneer_no_literal',n))
 edges[n]=sorted(set(es));best=(0,[])
 for to in edges[n]:
  b,p=calc(to)
  if b>best[0]:best=(b,p)
 b=x['resolved_frame_bytes']+best[0];memo[n]=b;paths[n]=[n]+best[1];stack.pop();return b,paths[n]
out={}
for n in ['setup1','loop1','IntegratedDisplay::SendReport()',*DISP_UP,*DISP_CTRL,'CFastLED::show(unsigned char)',INIT,CSHOW,CCOLOR,SHOWPIX,'__wrap_malloc','__wrap_calloc','TwoWire::endTransmission()',find('Adafruit_SSD1306::display(')]:
 try:b,p=calc(n);out[n]={'bound':b,'max_path':p}
 except RuntimeError as e:print('ERROR',e);raise
print(json.dumps({'bounds':out,'unknown':unknown,'excluded_precondition_faults':exclude,'reachable_count':len(reachable)},indent=2))
(O/'core1-bound-graph.json').write_text(json.dumps({'bounds':out,'unknown':unknown,'reachable_count':len(reachable),'reachable':sorted(reachable),'edges':edges,'special_bounds':special,'special_notes':notes,'excluded_precondition_faults':exclude,'dynamic_targets':D,'max_paths':paths,'all_function_bounds':memo},indent=2)+'\n')
