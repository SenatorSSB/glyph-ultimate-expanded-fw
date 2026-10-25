#!/usr/bin/env python3
"""Owner v2 requirements through actual C++ preprocessing/SOCD/native output.

Only finite expected rows and comparison assertions live in Python. Production
C++ is the implementation under test. v1 source/tests/evidence remain immutable.
"""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import jsonschema
import glyph_native_profile_json as codec
import test_kazuya_profile as v1
from check_glyph_profile_native_ultimate import compile_runner

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'profiles/kazuya/v2/KazuyaV2.profile.json'
FIX=ROOT/'tools/fixtures/kazuya/v2'
SEED=v1.SEED
SHIELD=16|64|128
DEFAULT=v1.DEFAULT
LOW=v1.LOW[:6]+[[128,205]]*3
# Bit order RF5, RF6, RF7, RF8. Exact owner graph, independent of JSON gates.
MATRIX=[('Default',0),('Default',1),('Default',32),('Default',1),
 ('RF7ReleaseNeutral',0),('SpringloadUp',0),('Default',0),('SpringloadUp',0),
 ('ForcedDown',0),('DownDiagonal',1),('DownDiagonal',32),('DownDiagonal',1),
 ('CDArmed',0),('CDArmed',0),('CDCNeutral',0),('CDCNeutral',0)]
COMMAND_POINTS={
 'ForcedDown':[[128,51]]*9,
 'DownDiagonal':[[61,51],[128,128],[195,51]]*3,
 'CDCNeutral':[[128,128]]*9,
 'CDArmed':[[128,128]]*3+[[61,51],[128,51],[195,51]]+[[128,128]]*3,
 'RF7ReleaseNeutral':DEFAULT[:3]+[[128,128]]*3+DEFAULT[6:],
 'SpringloadUp':DEFAULT[:4]+[[128,205]]+DEFAULT[5:]}

def names_for(rf,x=0,y=0,extra=()):
 n=v1.inputs(rf)|set(extra)
 if x:n.add('LF3' if x<0 else 'LF1')
 if y:n.add('LF5' if y<0 else 'LF2')
 return n

def expected(rf,x=0,y=0,extra=()):
 """Finite requirements oracle for uncomplicated inputs; complex layers use
 actual v1/archival differentials instead of reimplementing their conditions.
 """
 n=names_for(rf,x,y,extra);table,digital=MATRIX[rf];command=bool(rf&12)
 up=y==1 or (rf&1 and not command)
 down=y==-1 and not(rf&1 and not command)
 resolved_y=-1 if down else 1 if up else 0
 if command:ls=COMMAND_POINTS.get(table,DEFAULT)[(y+1)*3+x+1]
 elif rf&1:ls=[128,205]
 elif rf&2:ls=LOW[(resolved_y+1)*3+x+1]
 else:ls=DEFAULT[(resolved_y+1)*3+x+1]
 for name,value in [('RF1',1),('RF2',2),('RF3',4),('RF10',8),('LT1',80),
  ('RF16',128),('LT6',1),('MB7',256),('MB6',512),('MB5',1024),('MB4',2048)]:
  if name in n:digital|=value
 # Only LT2's own contribution is gated. RF5 A is executable iff RF7 absent.
 release='RF3' in n or bool(rf&1 and not rf&4) or (y==1 and bool(n&{'RF1','RF2'}))
 if 'LT2' in n and not release:digital|=SHIELD
 cx=-1 if 'RT3' in n else 1 if 'RT4' in n else 0
 cy=-1 if 'RT2' in n else 1 if 'RT5' in n else 0
 rs=(v1.DIAG_C if cx and cy else v1.BASE_C)[(cy+1)*3+cx+1]
 if 'RF3' in n and cy and x and not cx:rs=[95 if x<0 else 161,91 if cy<0 else 165]
 dpad='RF13' in n and not command
 if dpad:
  ls=[128,128]
  digital|=(1<<14 if x<0 else 1<<15 if x>0 else 0)|(1<<13 if down else 0)|(1<<12 if up else 0)
 else:digital|=(1<<18 if x<0 else 1<<19 if x>0 else 0)|(1<<21 if down else 0)|(1<<20 if up else 0)
 for name,bit in [('RT3',22),('RT4',23),('RT2',25),('RT5',24)]:
  if name in n:digital|=1<<bit
 if 'RF9' in n and 'RF3' not in n:
  if not command:ls=[128,128]
  rs=[128,128]
 if 'LT6' in n:ls=[128,128]
 return table,[SEED|digital,*ls,*rs,140 if digital&64 else 0,140 if digital&128 else 0]

class KazuyaV2Tests(unittest.TestCase):
 observations={}
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(prefix='kazuya-v2-native-');cls.work=Path(cls.temp.name)
  cls.exe,_,_,_=compile_runner(cls.work)
  cls.profile=codec.load_json(SOURCE)
  cls.context=cls.work/'context.pb';cls.context.write_bytes(v1.context_wire())
  cls.wire=cls.save('v2',cls.profile)
  cls.v1wire=cls.save('v1',codec.load_json(v1.SOURCE))
  cls.golden=ROOT/'tools/fixtures/native_profile_json/Ultimate.pb'
  p=copy.deepcopy(cls.profile)
  for t in p['tables'].values():t['directions']={str(i):[t['slot']+1,128] for i in range(1,10)}
  effect=copy.deepcopy(p['analogEffects'][0]);effect.update(activation='true',priority=1)
  p['analogEffects']=[effect];cls.selection=cls.save('selection',p)
  p=copy.deepcopy(cls.profile)
  for i,e in enumerate(p['analogEffects']):
   if e['target'] not in ['triggerL','triggerR']:e['coordinates']={'mode':'fixed','point':[50+i]*2}
  cls.effects=cls.save('effects',p)
 @classmethod
 def save(cls,name,p):
  path=cls.work/(name+'.pb');path.write_bytes(codec.compile_profile(p));return path
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def run_frames(self,frames,wire=None):
  path=self.work/'frames.txt';path.write_text(''.join(f'{v1.mask(n):x}\n' for n in frames))
  result=subprocess.run([str(self.exe),str(wire or self.wire),'sequence',str(self.context),str(path)],capture_output=True,text=True,check=True)
  rows=[[int(a[0],16),*map(int,a[1:])] for a in map(str.split,result.stdout.splitlines())]
  self.assertEqual(len(rows),len(frames));return rows
 def independent(self,frames,wire=None):return self.run_frames([n for frame in frames for n in [set(),frame]],wire)[1::2]
 def test_16_by_9_matrix_digital_cstick_and_winners(self):
  extras=[(),('RF1',),('RF2',),('RF3',),('RF10',),('LT1',),('RF16',),('LT2',),
   ('RF1','RF2','RF3','RF10'),('MB4','MB5','MB6','MB7'),('RF9',),('RF13',),('RF3','RT5')]
  extras += [tuple(n for i,n in enumerate(['RT2','RT3','RT4','RT5']) if b&(1<<i)) for b in range(16)]
  cases=[(rf,x,y,e) for rf,x,y,e in itertools.product(range(16),[-1,0,1],[-1,0,1],extras)]
  frames=[names_for(*c) for c in cases];outputs=self.independent(frames)
  selected=self.independent(frames,self.selection);effects=self.independent(frames,self.effects)
  for c,n,got,tag,eff in zip(cases,frames,outputs,selected,effects):
   table,want=expected(*c);self.assertEqual(got,want,str(sorted(n)))
   self.assertEqual(tag[1],self.profile['tables'][table]['slot']+1,str(sorted(n)))
   rf=c[0]
   winner=0 if rf&12 else 7 if 'RF9' in n and 'RF3' not in n else 10 if 'RF13' in n else 3 if rf&1 else (4 if c[2]==1 else 11) if rf&2 else 1
   self.assertEqual(eff[1:3],[50+winner]*2,str(sorted(n)))
  self.observations['matrix_composition_and_priority_cases']=len(cases)
 def test_lt6_absolute_neutral_all_commands_and_retained_modifiers(self):
  extras=[(),('RF9',),('RF13',),('LT2',),('RF1','RF2'),('RF16','LT1'),('RT3','RT5'),
   ('LT3',),('LT4',),('LT5',),('RF4',),('RT1','RF4'),('LT3','RF3','RF2'),('LF4','RF3')]
  frames=[names_for(rf,x,y,e) for rf,x,y,e in itertools.product(range(16),[-1,0,1],[-1,0,1],extras)]
  base=self.independent(frames);got=self.independent([n|{'LT6'} for n in frames]);tags=self.independent([n|{'LT6'} for n in frames],self.effects)
  for n,b,a,t in zip(frames,base,got,tags):
   self.assertEqual(a,[b[0]|1,128,128,*b[3:]],str(sorted(n)))
   self.assertEqual(t[1:3],[62,62])
  self.observations['lt6_override_cases']=len(frames)
 def test_lt2_release_carriers_and_independent_triggers(self):
  actions=[(),('RF3',),('RF1',),('RF2',),('RF1','RF2'),('RF3','RT5')]
  carriers=[(),('LT1',),('RF16',),('LT1','RF16')]
  cases=[(rf,x,y,('LT2',)+a+c) for rf,x,y,a,c in itertools.product(range(16),[-1,0,1],[-1,0,1],actions,carriers)]
  frames=[names_for(*c) for c in cases]
  for c,got in zip(cases,self.independent(frames)):self.assertEqual(got,expected(*c)[1],str(sorted(names_for(*c))))
  # Physical Jump releases LT2 even when its X output is replaced/suppressed by a sublayer.
  layers=[('LT3','RF3'),('LF4','RF3'),('RF9','RF3'),('LT3','RF3','RF1','RT5')]
  for layer,carriers in itertools.product(layers,carriers):
   base=set(layer)|set(carriers)
   self.assertEqual(self.independent([base|{'LT2'}])[0],self.independent([base])[0])
  # Synthetic RF2 Up must not replace post-SOCD physical Up for LT2 release.
  n={'LT2','LT3','RF3','RF2'} # RF3 itself releases: check the distinct RF4 face sublayer instead.
  n={'LT2','LT3','RF4','RF2'}
  got=self.independent([n])[0];self.assertEqual(got[0]&SHIELD,SHIELD);self.assertEqual(got[-2:],[140,140])
  self.observations['lt2_release_carrier_cases']=len(cases)+len(layers)*4+1
 def test_release_orders_all_directions_and_single_edges(self):
  sequences=[[8,12,4,0],[12,14,6,2],[12,13,5,1],[15,7,3],
   [12,14,10,2],[12,13,9,1],[15,11,3],[12,0],[14,2],[13,1],[15,3]]
  sequences += [[rf,rf^b] for rf in range(16) for b in [1,2,4,8]]
  count=0
  for states,x,y,shield in itertools.product(sequences,[-1,0,1],[-1,0,1],[False,True]):
   extra=('LT2',) if shield else ()
   frames=[names_for(s,x,y,extra) for s in states]
   self.assertEqual(self.run_frames([set()]+frames)[1:],[expected(s,x,y,extra)[1] for s in states],str(states));count+=len(states)
  self.observations['release_frames']=count
 def test_horizontal_vertical_socd_histories_and_simultaneous(self):
  count=0
  for rf,shield in itertools.product(range(16),[False,True]):
   extra=('LT2',) if shield else ();fixed=names_for(rf,extra=extra)
   for first,second,axis,sign in [('LF1','LF3','x',-1),('LF3','LF1','x',1),('LF2','LF5','y',-1),('LF5','LF2','y',1)]:
    frames=[set(),fixed|{first},fixed|{first,second},fixed|{first},fixed]
    got=self.run_frames(frames)
    for at,value in [(2,sign),(3,-sign),(4,0)]:
     x=value if axis=='x' else 0;y=value if axis=='y' else 0
     self.assertEqual(got[at],expected(rf,x,y,extra)[1],str((rf,first,at)));count+=1
   for axes in [('LF1','LF3'),('LF2','LF5'),('LF1','LF3','LF2','LF5')]:
    self.assertEqual(self.run_frames([set(),fixed|set(axes)])[-1],expected(rf,extra=extra)[1]);count+=1
  # LT2 suppression must follow vertical SOCD's winner, not raw original Up.
  for first,second,y in [('LF2','LF5',-1),('LF5','LF2',1)]:
   fixed={'LT2','RF1'}
   got=self.run_frames([set(),fixed|{first},fixed|{first,second}])[-1]
   self.assertEqual(got,expected(0,y=y,extra=('LT2','RF1'))[1]);count+=1
  self.observations['socd_assertions']=count
 def test_retained_v1_and_archival_differential(self):
  selectors=['LT3','LT4','LT5','RF3','RF4','RF9','RT1','LF4','RF2'];frames=[]
  for bits in range(1<<len(selectors)):
   base={n for i,n in enumerate(selectors) if bits&(1<<i)}
   for x,y,c in itertools.product([-1,0,1],[-1,0,1],[(),('RT2',),('RT3','RT5')]):frames.append(base|names_for(0,x,y,c))
  for name in codec.INPUTS:
   if name not in ['RF5','RF6','RF7','RF8','LT2','LT6']:frames.append({name})
  current=self.independent(frames);self.independent_base=current;old=self.independent(frames,self.v1wire);archive=self.independent(frames,self.golden)
  for n,a,b,c in zip(frames,current,old,archive):
   self.assertEqual(a,b,str(sorted(n)));self.assertEqual(a,c,str(sorted(n)))
  # Command-specific differences are exhaustive above. Compare RS and independent
  # face/menu/trigger bits across every RF subset with the retained selector graph.
  ordinary_mask=0xfff & ~(1|2|32) # A/B may arise from physical sublayers; verify below via per-frame v1 deltas.
  complex_frames=[n|v1.inputs(rf) for n in frames[:13824] for rf in range(16)]
  current=self.independent(complex_frames);old=self.independent(complex_frames,self.v1wire)
  for index,(n,a,b) in enumerate(zip(complex_frames,current,old)):
   self.assertEqual(a[3:],b[3:],str(sorted(n)))
   self.assertEqual(a[0]&ordinary_mask,b[0]&ordinary_mask,str(sorted(n)))
   # Native base retains all unrelated binding contributions, including OR
   # overlap with command bits. Assert full low 12-bit digital output.
   base_index=index//16;rf=index%16
   self.assertEqual(a[0]&0xfff,(self.independent_base[base_index][0]&0xfff)|MATRIX[rf][1],str(sorted(n)))
  # RF6 without physical Up retains complete v1 behavior, including synthetic
  # Up from LF4/LT3 sublayers. Physical Up instead must be straight strong Up
  # whenever ordinary RF6 wins (null and D-pad retain their prior precedence).
  weak_frames=[n|{'RF6'} for n in frames if 'LF2' not in n]
  for n,a,b in zip(weak_frames,self.independent(weak_frames),self.independent(weak_frames,self.v1wire)):
   self.assertEqual(a,b,'RF6 synthetic-only preservation '+str(sorted(n)))
  self.observations['rf6_nonphysical_up_v1_differential_cases']=len(weak_frames)
  self.observations['v1_archival_retained_cases']=len(frames)
  self.observations['v1_retained_rs_and_carrier_cases']=len(complex_frames)
 def test_schema_resources_coordinates_and_frozen_inputs(self):
  p=self.profile;jsonschema.Draft202012Validator(codec.load_json(codec.V1_SCHEMA_PATH)).validate(p)
  report=codec.compile_report(p);self.assertEqual(report,codec.load_json(FIX/'compile-report.json'))
  for k,limit in [('body_bytes',3336),('condition_count',96),('token_count',768),('direction_source_count',8),('table_rule_count',32),('digital_binding_count',32),('analog_effect_count',16)]:self.assertLessEqual(report[k],limit)
  self.assertLessEqual(len(p['tables']),28)
  self.assertEqual(p['gates']['mode'],'false');self.assertEqual(p['provenance'],{'kind':'authoredSourceV1'})
  self.assertEqual(p['preprocessing'],codec.load_json(v1.SOURCE)['preprocessing'])
  self.assertEqual(report['preprocessing_sha256'],'3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f')
  self.assertEqual(len({r['priority'] for r in p['tableRules']}),len(p['tableRules']))
  for name in COMMAND_POINTS:self.assertEqual(list(p['tables'][name]['directions'].values()),COMMAND_POINTS[name])
  self.assertEqual(list(p['tables']['RF6LowMagnitude']['directions'].values()),LOW)
  measured={tuple(r['raw']) for r in codec.load_json(v1.FIX/'coordinate-evidence.json')['measurements']}
  for table in p['tables'].values():
   for point in table['directions'].values():self.assertIn(tuple(point),measured)
  archival=codec.load_json(ROOT/'profiles/ultimate/Ultimate.profile.json')
  self.assertEqual(codec.compile_profile(archival),self.golden.read_bytes())
  self.assertEqual(hashlib.sha256(self.golden.read_bytes()).hexdigest(),'30d43278fee3a835ca006f4b5df67963c8e9b11ef059ab3b49329b65c7934c6b')
  # Pin all v1 source + evidence bytes, not just old test results.
  for path,digest in codec.load_json(FIX/'frozen-baselines.json').items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
 def test_negative_mutants(self):
  mutations=[]
  def add(label,edit,n,tag=None):
   control=copy.deepcopy(self.profile)
   if tag:tag(control)
   p=copy.deepcopy(control);edit(p);mutations.append((label,p,n,control))
  def cond(p,name):return next(c for c in p['conditions'] if c['name']==name)
  add('RF6 weak Up',lambda p:p['tables']['RF6LowMagnitude']['directions'].update({'7':[89,167],'8':[128,177],'9':[167,167]}),{'RF6','LF2','LF3'})
  add('LT6 loses to command',lambda p:p['analogEffects'][-1].update(priority=6),{'LT6','RF8'})
  add('LT6 loses to null',lambda p:p['analogEffects'][-1].update(priority=11),{'LT6','RF5','RF9'})
  # Null and LT6 are both neutral; tag null so precedence is observable, never
  # pretend identical neutral bytes establish a numerical winner.
  mutations[-1][1]['analogEffects'][7]['coordinates']['point']=[99,99]
  add('RF5 RF6 Z exclusivity',lambda p:cond(p,'rf6Grab')['none'].remove('postSocd:RF5'),{'RF5','RF6'})
  add('RF5 RF6 analogue exclusivity',lambda p:cond(p,'rf6OrdinaryAnalog')['none'].remove('postSocd:RF5'),{'RF5','RF6'},tag=lambda p:p['analogEffects'][4].update(coordinates={'mode':'fixed','point':[99,99]}))
  add('LT2 treats spring RF5 as executable',lambda p:cond(p,'lt2Shield')['none'].append('postSocd:RF5'),{'LT2','RF7','RF5'})
  add('LT2 fails executable RF5 release',lambda p:cond(p,'lt2Shield')['none'].remove('condition:rf5Attack'),{'LT2','RF5'})
  add('LT2 residual trigger analogue',lambda p:p['analogEffects'][8].update(activation='postSocd:LT2'),{'LT2','RF3'})
  add('Spring RF5 leaks A',lambda p:cond(p,'rf5Attack').update(none=[]),{'RF5','RF7'})
  add('Spring RF6 leaks Z',lambda p:cond(p,'rf6Grab')['none'].remove('postSocd:RF7'),{'RF6','RF7'})
  add('CDArmed uses synthetic LF Up',lambda p:p['analogEffects'][0].update(source='ordinaryLeft'),{'RF8','RF7','RF5','LT3','RF4','RF2'})
  caught=[]
  for label,p,n,control in mutations:
   path=self.save('mutant',p)
   actual=self.independent([n],path)[0];baseline=self.independent([n],self.save('mutant-control',control))[0]
   self.assertNotEqual(actual,baseline,label);caught.append(label)
  self.observations['negative_mutants_detected']=caught

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);parser.add_argument('-v',action='store_true');args=parser.parse_args()
 result=unittest.TextTestRunner(verbosity=2 if args.v else 1).run(unittest.defaultTestLoader.loadTestsFromTestCase(KazuyaV2Tests))
 if args.report:
  paths=['profiles/kazuya/v2/KazuyaV2.profile.json','tools/test_kazuya_profile_v2.py','tools/test_kazuya_profile.py','tools/glyph_native_profile_json.py','src/modes/Ultimate.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp','schema/haybox/config.proto','HAL/pico/src/comms/GamecubeBackend.cpp','tools/fixtures/profile_native_ultimate/native_runner.cpp']
  args.report.write_text(json.dumps(dict(status='PASS' if result.wasSuccessful() else 'FAIL',baseline='bf6f1e2e6814c6b6f1eb710175a488961c8295e7',tests_run=result.testsRun,observations=KazuyaV2Tests.observations,input_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},compile_report=codec.compile_report(codec.load_json(SOURCE)),hardware_acceptance='NOT_TESTED',gameplay='NOT_TESTED'),indent=2)+'\n')
 raise SystemExit(0 if result.wasSuccessful() else 1)
