#!/usr/bin/env python3
"""Kazuya v4 requirements through the unchanged production C++ native path.

Finite expected matrices are assertion data; no Python evaluator replaces C++.
The frozen v2 harness is loaded in isolation; historical suites stay unchanged.
"""
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import unittest
import glyph_native_profile_json as codec
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'profiles/kazuya/v4/KazuyaV4.profile.json'
FIX=ROOT/'tools/fixtures/kazuya/v4'
spec=importlib.util.spec_from_file_location('_kazuya_v4_native_base',ROOT/'tools/test_kazuya_profile_v2.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
base.SOURCE=SOURCE;base.FIX=FIX
DEFAULT=base.DEFAULT;SEED=base.SEED;SHIELD=base.SHIELD
MATRIX=[('Default',0),('Default',1),('Default',32),('Default',1),
 ('RF7ReleaseNeutral',0),('SpringloadUp',0),('Default',0),('SpringloadUp',0),
 ('ForcedDown',0),('DownDiagonal',1),('DownDiagonal',32),('DownDiagonal',1),
 ('CDArmed',0),('CDCNeutral',0),('CDCNeutral',0),('CDCNeutral',0)]
POINTS={'ForcedDown':[[128,51]]*9,'DownDiagonal':[[61,51],[128,128],[195,51]]*3,
 'CDCNeutral':[[128,128]]*9,'CDArmed':[[61,51],[128,51],[195,51]]*3,
 'RF7ReleaseNeutral':[[128,128]]*9,'SpringloadUp':[[128,205]]*9,
 'LT2DefensiveDownBack':[[61,51],[128,51],[195,51],[195,51],[128,51],[61,51],[61,205],[128,205],[195,205]]}

def expected(rf,x=0,y=0,extra=()):
 """Owner matrix for simple input combinations; complex retained layers are
 checked differentially against the actual v3 native output, not reimplemented.
 """
 n=base.names_for(rf,x,y,extra);table,digital=MATRIX[rf];command=bool(rf&12)
 up=y==1 or (rf&1 and not command);down=y==-1 and not(rf&1 and not command)
 resolved_y=-1 if down else 1 if up else 0
 release='RF3' in n or bool(rf&1 and not rf&4) or (y==1 and bool(n&{'RF1','RF2'}))
 shield='LT2' in n and not release
 if rf==12 and shield:table='CDCNeutral'
 if rf==4 and shield:table='LT2DefensiveDownBack'
 if command:ls=POINTS.get(table,DEFAULT)[(y+1)*3+x+1]
 elif rf&1:ls=[128,205]
 elif rf&2:ls=base.LOW[(resolved_y+1)*3+x+1]
 else:ls=DEFAULT[(resolved_y+1)*3+x+1]
 for name,value in [('RF1',1),('RF2',2),('RF3',4),('RF10',8),('LT1',80),('RF16',128),('LT6',1),('RF12',1),('MB7',256),('MB6',512),('MB5',1024),('MB4',2048)]:
  if name in n:digital|=value
 if shield:digital|=SHIELD
 cx=-1 if 'RT3' in n else 1 if 'RT4' in n else 0
 cy=-1 if 'RT2' in n else 1 if 'RT5' in n else 0
 rs=(base.v1.DIAG_C if cx and cy else base.v1.BASE_C)[(cy+1)*3+cx+1]
 if 'RF3' in n and cy and x and not cx:rs=[95 if x<0 else 161,91 if cy<0 else 165]
 dpad='RF13' in n and not command
 if dpad:
  ls=[128,128];digital|=(1<<14 if x<0 else 1<<15 if x>0 else 0)|(1<<13 if down else 0)|(1<<12 if up else 0)
 else:digital|=(1<<18 if x<0 else 1<<19 if x>0 else 0)|(1<<21 if down else 0)|(1<<20 if up else 0)
 for name,bit in [('RT3',22),('RT4',23),('RT2',25),('RT5',24)]:
  if name in n:digital|=1<<bit
 if 'RF9' in n and 'RF3' not in n:
  if not command:ls=[128,128]
  rs=[128,128]
 if 'LT6' in n:ls=[128,51]
 if 'RF12' in n:ls=[128,128]
 return table,[SEED|digital,*ls,*rs,140 if digital&64 else 0,140 if digital&128 else 0]

base.MATRIX=MATRIX;base.COMMAND_POINTS=POINTS;base.expected=expected

class KazuyaV4Tests(base.KazuyaV2Tests):
 observations={}
 @classmethod
 def setUpClass(cls):
  super().setUpClass()
  cls.previous=codec.load_json(ROOT/'profiles/kazuya/v3/KazuyaV3.profile.json')
  cls.previous_wire=cls.save('exact-v3',cls.previous)
 def test_lt6_absolute_neutral_all_commands_and_retained_modifiers(self):
  # Override the v2-named historical test with v4's explicit Down / neutral policy.
  extras=[(),('RF9',),('RF13',),('LT2',),('RF1','RF2'),('RF16','LT1'),('RT3','RT5'),('LT3',),('LT4',),('LT5',),('RF4',),('RT1','RF4'),('LT3','RF3','RF2'),('LF4','RF3')]
  frames=[base.names_for(rf,x,y,e) for rf,x,y,e in itertools.product(range(16),[-1,0,1],[-1,0,1],extras)]
  ordinary=self.independent(frames)
  for modifier,point,index in [('LT6',[128,51],12),('RF12',[128,128],13)]:
   got=self.independent([n|{modifier} for n in frames]);tags=self.independent([n|{modifier} for n in frames],self.effects)
   for n,b,a,t in zip(frames,ordinary,got,tags):
    self.assertEqual(a,[b[0]|1,*point,*b[3:]],str(sorted(n|{modifier})))
    self.assertEqual(t[1:3],[50+index]*2)
   self.observations[modifier.lower()+'_fixed_override_cases']=len(frames)
  both=self.independent([n|{'LT6','RF12'} for n in frames])
  for n,b,a in zip(frames,ordinary,both):self.assertEqual(a,[b[0]|1,128,128,*b[3:]],str(sorted(n)))
  self.observations['rf12_over_lt6_cases']=len(frames)
 def test_defensive_shield_release_sequences_all_directions(self):
  sequences=[[12,12,4,0],[12,13,5,1],[12,14,6,2],[12,15,7,3],
   [12,8,0],[12,0],[13,9,1],[14,10,2],[15,11,3],[13,1],[14,2],[15,3],[5,7,5],[4,0],[6,2]]
  count=0;trace=[]
  for states,x,y in itertools.product(sequences,[-1,0,1],[-1,0,1]):
   # First frame of plain CD is unshielded; later LT2 frames show press/release.
   extras=[() if i==0 and states[:2]==[12,12] else ('LT2',) for i in range(len(states))]
   frames=[base.names_for(r,x,y,e) for r,e in zip(states,extras)]
   got=self.run_frames([set()]+frames)[1:]
   self.assertEqual(got,[expected(r,x,y,e)[1] for r,e in zip(states,extras)])
   count+=len(states)
   trace.append({'rf_masks':states,'physical_fgc':(y+1)*3+x+2,'lt2_held':[bool(e) for e in extras],'native_output_rows':got})
  self.observations['defensive_and_specialized_release_frames']=count
  self.observations['release_trace_sequences']=len(trace)
  type(self).transition_trace=trace
 def test_defensive_socd_and_semantic_shield_gate(self):
  count=0
  for rf,extra in itertools.product([4,12],[('LT2',),('LT2','RF1'),('LT2','RF2'),('LT2','RF3'),('LT2','LT1','RF16')]):
   fixed=base.names_for(rf,extra=extra)
   for first,second,axis,sign in [('LF1','LF3','x',-1),('LF3','LF1','x',1),('LF2','LF5','y',-1),('LF5','LF2','y',1)]:
    frames=[set(),fixed|{first},fixed|{first,second},fixed|{first},fixed]
    got=self.run_frames(frames)
    for at,value in [(2,sign),(3,-sign),(4,0)]:
     self.assertEqual(got[at],expected(rf,value if axis=='x' else 0,value if axis=='y' else 0,extra)[1]);count+=1
   for opponents in [('LF1','LF3'),('LF2','LF5'),('LF1','LF3','LF2','LF5')]:
    self.assertEqual(self.run_frames([set(),fixed|set(opponents)])[-1],expected(rf,extra=extra)[1]);count+=1
  # RF12 intentionally does not release LT2's own contribution.
  cases=[(rf,x,y,('LT2','RF12')) for rf,x,y in itertools.product(range(16),[-1,0,1],[-1,0,1])]
  for c,got in zip(cases,self.independent([base.names_for(*c) for c in cases])):self.assertEqual(got,expected(*c)[1])
  self.observations['defensive_socd_assertions']=count
  self.observations['rf12_lt2_composition_cases']=len(cases)
 def test_rf12_sequence_and_all_cstick_geometry(self):
  count=0
  for x in [-1,0,1]:
   fixed=base.names_for(0,x)
   frames=[fixed|{'RF1'},fixed|{'RF1','RF8'},fixed|{'RF8'},fixed|{'RF8','RF12'}]
   got=self.run_frames([set()]+frames)[1:]
   self.assertEqual(got,[expected(0,x,extra=('RF1',))[1],expected(8,x,extra=('RF1',))[1],expected(8,x)[1],expected(8,x,extra=('RF12',))[1]])
   count+=len(frames)
  frames=[]
  for rf,x,y,c,jump,lt6 in itertools.product(range(16),[-1,0,1],[-1,0,1],range(16),[False,True],[False,True]):
   extra={n for i,n in enumerate(['RT2','RT3','RT4','RT5']) if c&(1<<i)}
   if jump:extra.add('RF3')
   if lt6:extra.add('LT6')
   frames.append(base.names_for(rf,x,y,extra))
  before=self.independent(frames);after=self.independent([n|{'RF12'} for n in frames])
  for n,a,b in zip(frames,after,before):self.assertEqual(a,[b[0]|1,128,128,*b[3:]],str(sorted(n)))
  self.observations['rf12_player_sequence_frames']=count
  self.observations['rf12_all_cstick_composition_cases']=len(frames)
 def test_retained_v1_and_archival_differential(self):
  # Complete retained selectors with every RF state: compare actual v3, allowing
  # only the named raw-LS changes for subsets4,12,13. Other fields remain exact.
  selectors=['LT3','LT4','LT5','RF3','RF4','RF9','RT1','LF4','RF2']
  frames=[];cases=[]
  for bits in range(1<<len(selectors)):
   extra={n for i,n in enumerate(selectors) if bits&(1<<i)}
   for rf,x,y in itertools.product(range(16),[-1,0,1],[-1,0,1]):
    frames.append(base.names_for(rf,x,y,extra));cases.append((rf,x,y))
  current=self.independent(frames);old=self.independent(frames,self.previous_wire)
  for n,(rf,x,y),a,b in zip(frames,cases,current,old):
   if rf in [4,12,13]:
    want=POINTS[MATRIX[rf][0]][(y+1)*3+x+1]
    self.assertEqual(a,[b[0],*want,*b[3:]],str(sorted(n)))
   else:self.assertEqual(a,b,str(sorted(n)))
  self.observations['v3_exact_retained_selector_and_rf_cases']=len(frames)
  self.observations['v3_complete_rf6_subset_cases']=sum(bool(rf&2) for rf,x,y in cases)
  # Each ordinary input and every C-stick subset is fully unchanged except the
  # two explicitly reassigned physical inputs. Include LF geometry and RF3 C transform.
  frames=[{n} for n in codec.INPUTS if n not in ['RF7','RF8','LT6','RF12']]
  frames += [base.names_for(0,x,y,e) for x,y,bits,jump in itertools.product([-1,0,1],[-1,0,1],range(16),[False,True]) for e in [tuple(n for i,n in enumerate(['RT2','RT3','RT4','RT5']) if bits&(1<<i))+ (('RF3',) if jump else ())]]
  for n,a,b in zip(frames,self.independent(frames),self.independent(frames,self.previous_wire)):self.assertEqual(a,b,str(sorted(n)))
  self.observations['v3_ordinary_and_all_cstick_subset_cases']=len(frames)
 def test_schema_resources_coordinates_and_frozen_inputs(self):
  super().test_schema_resources_coordinates_and_frozen_inputs()
  p=self.profile;old=self.previous;body=codec.unwrap_profile(codec.compile_profile(p));report=codec.compile_report(p)
  self.assertEqual(p['directionSources'],old['directionSources'])
  self.assertEqual(p['preprocessing'],old['preprocessing'])
  self.assertEqual(p['tables']['SpringloadUp'],old['tables']['SpringloadUp'])
  self.assertEqual(p['tables']['RF6LowMagnitude'],old['tables']['RF6LowMagnitude'])
  for name,t in old['tables'].items():
   if name not in ['CDArmed','RF7ReleaseNeutral']:self.assertEqual(p['tables'][name],t)
  oldconds={c['name']:c for c in old['conditions']};newconds={c['name']:c for c in p['conditions']}
  for name,c in oldconds.items():
   if name not in ['cdcNeutral','cdArmed']:self.assertEqual(newconds[name],c)
  self.assertEqual(set(newconds)-set(oldconds),{'lt2DefensivePrepare','lt2DefensiveDownBack','neutralCommand'})
  self.assertEqual(p['digitalBindings'][:-1],old['digitalBindings'])
  self.assertEqual(p['digitalBindings'][-1],{'when':'postSocd:RF12','outputs':['buttonA'],'winnerTable':'any'})
  self.assertEqual(p['analogEffects'][:12],old['analogEffects'][:12])
  self.assertEqual(p['digitalPostMask'],old['digitalPostMask'])
  for slot in report['neutral_filled_slots']:self.assertEqual(body[96+slot*18:114+slot*18],bytes([128])*18)
  self.assertEqual(len(body[96:600]),28*9*2)
  self.assertEqual(p['analogEffects'][12]['coordinates'],{'mode':'fixed','point':[128,51]})
  self.assertEqual(p['analogEffects'][13]['coordinates'],{'mode':'fixed','point':[128,128]})
  self.assertEqual([p['analogEffects'][i]['priority'] for i in [13,12,0]],[1,2,5])
  semantic={k:v for k,v in p.items() if k not in ['name','metadata','provenance']}
  digest=hashlib.sha256(b'Glyph.Native.Authoring.v1\0'+json.dumps(semantic,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).digest()
  self.assertEqual(body[60:92],digest)
 def test_negative_mutants(self):
  mutations=[]
  def condition(p,name):return next(c for c in p['conditions'] if c['name']==name)
  def add(label,edit,n,tag=None):
   control=copy.deepcopy(self.profile)
   if tag:tag(control)
   p=copy.deepcopy(control);edit(p);mutations.append((label,p,n,control))
  add('old vertical-neutral CD restored',lambda p:p['tables']['CDArmed'].update(directions=self.previous['tables']['CDArmed']['directions']),{'RF8','RF7','LF1','LF2'})
  add('RF7 loses all-direction neutral',lambda p:p['tables']['RF7ReleaseNeutral'].update(directions=self.previous['tables']['RF7ReleaseNeutral']['directions']),{'RF7','LF2','LF3'})
  add('manual Down incorrectly flipped',lambda p:p['tables']['LT2DefensiveDownBack']['directions'].update({'1':[195,51]}),{'RF7','LT2','LF3','LF5'})
  add('LT2 prepare gated by raw physical LT2',lambda p:condition(p,'lt2DefensivePrepare').update(all=['condition:cdcPair','postSocd:LT2']),{'RF8','RF7','LT2','RF3','LF1'})
  add('LT2 defensive gate ignores Shield suppression',lambda p:condition(p,'lt2DefensiveDownBack').update(all=['postSocd:RF7','postSocd:LT2']),{'RF7','LT2','LF2','RF1'})
  add('LT2 displaces RF5 spring Up',lambda p:condition(p,'lt2DefensiveDownBack')['none'].remove('postSocd:RF5'),{'RF7','RF5','LT2','LF1'})
  add('LT2 displaces RF6 spring Default',lambda p:condition(p,'lt2DefensiveDownBack')['none'].remove('postSocd:RF6'),{'RF7','RF6','LT2','LF1'})
  add('pair RF5 fails neutral preparation',lambda p:condition(p,'cdcNeutral').update(any=['postSocd:RF6']),{'RF8','RF7','RF5','LF1'})
  add('v3 spring Up regresses to horizontal',lambda p:p['tables']['SpringloadUp']['directions'].update({'6':[195,128]}),{'RF7','RF5','LF1'})
  add('RF12 loses to LT6',lambda p:p['analogEffects'][13].update(priority=3),{'RF12','LT6','LF1'})
  add('RF12 loses to command',lambda p:p['analogEffects'][13].update(priority=6),{'RF12','RF8'})
  add('RF12 loses to null',lambda p:p['analogEffects'][13].update(priority=11),{'RF12','RF9'},tag=lambda p:p['analogEffects'][7].update(coordinates={'mode':'fixed','point':[99,99]}))
  add('RF12 loses to Dpad effect',lambda p:p['analogEffects'][13].update(priority=21),{'RF12','RF13'},tag=lambda p:p['analogEffects'][10].update(coordinates={'mode':'fixed','point':[99,99]}))
  add('LT6 old neutral remains',lambda p:p['analogEffects'][12].update(coordinates={'mode':'fixed','point':[128,128]}),{'LT6'})
  add('LT6 loses to spring command',lambda p:p['analogEffects'][12].update(priority=6),{'LT6','RF7','RF5'})
  add('RF12 silently releases LT2 Shield',lambda p:condition(p,'lt2Shield')['none'].append('postSocd:RF12'),{'LT2','RF12'})
  add('RF6 strong physical Up lost',lambda p:p['tables']['RF6LowMagnitude']['directions'].update({'7':[89,167]}),{'RF6','LF2','LF3'})
  add('RF5 RF6 Z exclusivity lost',lambda p:condition(p,'rf6Grab')['none'].remove('postSocd:RF5'),{'RF5','RF6'})
  add('RF5 RF6 analogue exclusivity lost',lambda p:condition(p,'rf6OrdinaryAnalog')['none'].remove('postSocd:RF5'),{'RF5','RF6'})
  add('spring RF5 leaks A',lambda p:condition(p,'rf5Attack').update(none=[]),{'RF7','RF5'})
  add('spring RF6 leaks Z',lambda p:condition(p,'rf6Grab')['none'].remove('postSocd:RF7'),{'RF7','RF6'})
  add('residual analogue after LT2 suppression',lambda p:p['analogEffects'][8].update(activation='postSocd:LT2'),{'LT2','RF3'})
  add('RF12 wrongly adds B',lambda p:p['digitalBindings'][-1]['outputs'].append('buttonB'),{'RF12'})
  add('RF12 wrongly adds Z',lambda p:p['digitalBindings'][-1]['outputs'].append('buttonR'),{'RF12'})
  for label,p,n,control in mutations:
   actual=self.independent([n],self.save('mutant',p))[0];want=self.independent([n],self.save('control',control))[0]
   self.assertNotEqual(actual,want,label)
  self.observations['negative_mutants_detected']=[x[0] for x in mutations]

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);parser.add_argument('-v',action='store_true');args=parser.parse_args()
 result=unittest.TextTestRunner(verbosity=2 if args.v else 1).run(unittest.defaultTestLoader.loadTestsFromTestCase(KazuyaV4Tests))
 if args.report:
  paths=['profiles/kazuya/v4/KazuyaV4.profile.json','tools/test_kazuya_profile_v4.py','tools/test_kazuya_profile_v2.py','tools/glyph_native_profile_json.py','src/modes/Ultimate.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp','schema/haybox/config.proto','HAL/pico/src/comms/GamecubeBackend.cpp','tools/fixtures/profile_native_ultimate/native_runner.cpp']
  args.report.write_text(json.dumps({'status':'PASS' if result.wasSuccessful() else 'FAIL','behavioral_baseline':'b2d72b1367ea6c350574727168cdc8b5c2ce3f1d','tests_run':result.testsRun,'observations':KazuyaV4Tests.observations,'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},'compile_report':codec.compile_report(codec.load_json(SOURCE)),'gameplay':'NOT_TESTED','nunchuk':'NOT_TESTED','device':'NOT_ATTEMPTED; fresh preflight and reviewed identity required'},indent=2)+'\n')
  if hasattr(KazuyaV4Tests,'transition_trace'):args.report.with_name(args.report.stem+'.transitions.json').write_text(json.dumps({'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'unowned_runner_sentinel':hex(SEED),'row_format':['digital_uint32','LSx','LSy','RSx','RSy','Lanalog','Ranalog'],'sequences':KazuyaV4Tests.transition_trace},indent=2)+'\n')
 raise SystemExit(0 if result.wasSuccessful() else 1)
