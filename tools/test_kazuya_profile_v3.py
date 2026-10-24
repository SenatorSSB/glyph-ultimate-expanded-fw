#!/usr/bin/env python3
"""RF5 pure-Up cancel revision, reusing the frozen v2 native verification suite.

Load an isolated module copy so running/importing this suite never changes the
v2 suite's original expectations. The implementation under test remains C++.
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
SOURCE=ROOT/'profiles/kazuya/v3/KazuyaV3.profile.json'
FIX=ROOT/'tools/fixtures/kazuya/v3'
spec=importlib.util.spec_from_file_location('_kazuya_up_cancel_verification_base',ROOT/'tools/test_kazuya_profile_v2.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
base.SOURCE=SOURCE;base.FIX=FIX;base.COMMAND_POINTS=copy.deepcopy(base.COMMAND_POINTS)
base.COMMAND_POINTS['SpringloadUp']=[[128,205] for _ in range(9)]

class KazuyaV3Tests(base.KazuyaV2Tests):
 observations={}
 @classmethod
 def setUpClass(cls):
  super().setUpClass()
  cls.previous=codec.load_json(ROOT/'profiles/kazuya/v2/KazuyaV2.profile.json')
  cls.previous_wire=cls.save('installed-v2-baseline',cls.previous)
 def test_first_post_cancel_frame_is_pure_up(self):
  count=0
  # Both physical horizontal sides, verticals and no direction; RF6 optional.
  for rf6,x,y,shield in itertools.product([0,2],[-1,0,1],[-1,0,1],[False,True]):
   states=[13|rf6,5|rf6,1|rf6];extra=('LT2',) if shield else ()
   got=self.run_frames([set()]+[base.names_for(s,x,y,extra) for s in states])[1:]
   self.assertEqual(got,[base.expected(s,x,y,extra)[1] for s in states])
   self.assertEqual(got[1][1:3],[128,205],'first frame after RF8 release')
   self.assertEqual(got[1][0]&(1|2|32),0,'RF5/RF6 attack withheld')
   self.assertEqual(got[2][1:3],[128,205],'RF7 release keeps Up')
   self.assertEqual(got[2][0]&(1|2|32),1,'RF7 release executes only RF5 A')
   count+=3
  self.observations['focused_up_cancel_release_frames']=count
 def test_only_springload_left_coordinates_change_from_v2(self):
  selectors=['LT3','LT4','LT5','RF3','RF4','RF9','RT1','LF4','RF2']
  extras=[{n for i,n in enumerate(selectors) if b&(1<<i)} for b in range(1<<len(selectors))]
  extras += [{'LT6'}, {'LT6','RF9'}, {'LT6','RF13'}, {'LT6','LT2','RF1','RF2'}, {'LT1','RF16','LT2'}, {'RF13'}, {'RT3','RT5'}, {'RF3','RT5'}]
  cases=list(itertools.product(range(16),[-1,0,1],[-1,0,1],extras))
  frames=[base.names_for(*case) for case in cases]
  old=self.independent(frames,self.previous_wire);new=self.independent(frames)
  changed=0
  for (rf,x,y,extra),n,a,b in zip(cases,frames,new,old):
   spring=bool(rf&1 and rf&4 and not rf&8)
   if spring:
    want=[128,128] if 'LT6' in extra else [128,205]
    self.assertEqual(a,[b[0],*want,*b[3:]],str(sorted(n)))
    changed+=a!=b
   else:self.assertEqual(a,b,str(sorted(n)))
  self.observations['exact_v2_differential_cases']=len(cases)
  self.observations['intended_changed_output_cases']=changed
 def test_exact_source_delta_and_forward_reintroduction_mutation(self):
  expected=copy.deepcopy(self.previous)
  expected['name']=self.profile['name'];expected['metadata']=self.profile['metadata']
  expected['tables']['SpringloadUp']['directions']={str(d):[128,205] for d in range(1,10)}
  self.assertEqual(self.profile,expected)
  old_body=codec.unwrap_profile(codec.compile_profile(self.previous))
  new_body=codec.unwrap_profile(codec.compile_profile(self.profile))
  start=96+self.profile['tables']['SpringloadUp']['slot']*18
  allowed=set(range(60,92))|set(range(start,start+18))
  self.assertEqual(len(old_body),len(new_body))
  self.assertTrue(all(i in allowed for i,(a,b) in enumerate(zip(old_body,new_body)) if a!=b))
  mutant=copy.deepcopy(self.profile)
  mutant['tables']['SpringloadUp']['directions']=self.previous['tables']['SpringloadUp']['directions']
  path=self.save('forward-return-mutant',mutant)
  frames=[base.names_for(rf,x) for rf,x in itertools.product([5,7],[-1,1])]
  old=self.independent(frames,path);new=self.independent(frames)
  for a,b in zip(new,old):
   self.assertEqual(a[1:3],[128,205]);self.assertNotEqual(a[1:3],b[1:3])
  self.observations['forward_reintroduction_mutations_detected']=len(frames)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);parser.add_argument('-v',action='store_true');args=parser.parse_args()
 result=unittest.TextTestRunner(verbosity=2 if args.v else 1).run(unittest.defaultTestLoader.loadTestsFromTestCase(KazuyaV3Tests))
 if args.report:
  paths=['profiles/kazuya/v3/KazuyaV3.profile.json','tools/test_kazuya_profile_v3.py','tools/test_kazuya_profile_v2.py','tools/glyph_native_profile_json.py','src/modes/Ultimate.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp','tools/fixtures/profile_native_ultimate/native_runner.cpp']
  args.report.write_text(json.dumps({'status':'PASS' if result.wasSuccessful() else 'FAIL','baseline_commit':'1381193b0101825d2a9afb46cd7a01009da67cdf','tests_run':result.testsRun,'observations':KazuyaV3Tests.observations,'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},'compile_report':codec.compile_report(codec.load_json(SOURCE)),'upload_status':'NOT_ATTEMPTED; owner-authorized single CREATE subject to fresh preflight','gameplay':'NOT_TESTED','nunchuk':'NOT_TESTED'},indent=2)+'\n')
 raise SystemExit(0 if result.wasSuccessful() else 1)
