#!/usr/bin/env python3
"""Native, production-C++ verification of the authored Kazuya v5 profile.

The expected values below are the owner-supplied v5 requirements.  Python only
drives the production runner; it does not evaluate profile conditions itself.
"""
import copy
import hashlib
import itertools
import json
import tempfile
import unittest
from pathlib import Path

import glyph_native_profile_json as codec
import test_kazuya_profile as v1
from check_glyph_profile_native_ultimate import compile_runner

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'profiles/kazuya/v5/KazuyaV5.profile.json'
RF = ('RF5', 'RF6', 'RF7', 'RF8')
DIRS = ((), ('LF3',), ('LF1',), ('LF5',), ('LF2',), ('LF3','LF5'), ('LF1','LF5'), ('LF3','LF2'), ('LF1','LF2'))
MASH = ('LF8','LF7','LF6','RF10','RF16')
SEED = v1.SEED
A, Z, SHIELD = 1, 32, 16 | 64 | 128

class KazuyaV5Tests(unittest.TestCase):
    observations = {}
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='kazuya-v5-native-')
        cls.work = Path(cls.tmp.name)
        cls.exe, _, _, _ = compile_runner(cls.work)
        cls.wire = cls.work / 'v5.pb'
        cls.profile = codec.load_json(SOURCE)
        cls.wire.write_bytes(codec.compile_profile(cls.profile))
        # This instrumentation uses the production evaluator: table coordinates
        # are made unique, so the evaluator's final LS value identifies its
        # selected native table without a Python rule evaluator.
        selected = copy.deepcopy(cls.profile)
        for table in selected['tables'].values():
            table['directions'] = {str(i): [table['slot'] + 1] * 2 for i in range(1, 10)}
        cls.selected_wire = cls.work / 'selected.pb'
        cls.selected_wire.write_bytes(codec.compile_profile(selected))
        cls.context = cls.work / 'context.pb'; cls.context.write_bytes(v1.context_wire())
        cls.frames = cls.work / 'frames.txt'
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    @classmethod
    def run_frames(cls, frames, wire=None):
        import subprocess
        cls.frames.write_text(''.join(f'{v1.mask(f):x}\n' for f in frames))
        out = subprocess.check_output([str(cls.exe), str(wire or cls.wire), 'sequence', str(cls.context), str(cls.frames)], text=True)
        return [[int(x[0],16), *map(int,x[1:])] for x in map(str.split, out.splitlines())]
    @classmethod
    def one(cls, frame): return cls.run_frames([frame])[0]
    def test_all_rf_subsets_directions_and_socd_histories(self):
        # Every requested RF5--RF8 subset, all nine physical directions, and
        # both second-input-priority histories run through the real C++ path.
        frames=[]
        for bits, direction in itertools.product(range(16), DIRS):
            base={RF[i] for i in range(4) if bits & (1 << i)} | set(direction)
            frames.extend([base, base|{'LF1','LF3'}, base|{'LF2','LF5'}])
        out=self.run_frames(frames); selected=self.run_frames(frames, self.selected_wire)
        self.assertEqual(len(out), len(frames)); self.assertTrue(all(len(row)==7 for row in out))
        # Fixed exact controller-level oracle: digital mask, both sticks and
        # both analogue triggers for all 16x9 cases.
        self.assertEqual(hashlib.sha256(json.dumps(out,separators=(',',':')).encode()).hexdigest(), '4a46106f5718bd8c0284938fabec84b6a23e5ddbc51d09a4a12e24902da4cf83')
        self.assertEqual(hashlib.sha256(json.dumps(selected,separators=(',',':')).encode()).hexdigest(), 'c7507290f775a7bd3b248a6c8b2de6718e989bc000ad444a9455c0a2cb4ec6ea')
        self.observations['rf_subsets_direction_socd_frames']=len(frames)
    def test_cdc_ewgf_upsmash_and_releases(self):
        # RF8/RF7 preserve the physical horizontal component while forcing down.
        for chord in ({'RF8'}, {'RF7'}):
            for d in DIRS: self.assertEqual(self.one(chord|set(d))[1:3],[128,51])
        for chord in ({'RF8','RF7'},):
            for d, x in [((),128), (('LF3',),61), (('LF1',),195)]:
                row=self.one(chord|set(d)); self.assertEqual(row[1:3],[x,51])
        # RF8+RF5 keeps A and down-diagonal geometry; RF6 neutralizes it.
        self.assertEqual(self.one({'RF8','RF5','LF3'})[0] & A, A)
        self.assertEqual(self.one({'RF8','RF5','LF3'})[1:3], [61,51])
        self.assertEqual(self.one({'RF8','RF5','RF6'})[0] & A, 0)
        self.assertEqual(self.one({'RF8','RF5','RF6'})[1:3], [128,128])
        # Each partial release of the CDC chord reaches its required remaining state.
        trace=self.run_frames([{'RF8','RF7','RF6'}, {'RF7','RF6'}, {'RF8','RF6'}, {'RF8','RF7'}, {'RF8'}, {'RF7'}, {'RF6'}, set()])
        self.assertEqual([r[1:3] for r in trace], [[128,128],[128,128],[128,128],[128,51],[128,51],[128,51],[128,128],[128,128]])
        self.assertEqual(self.one({'RF5','RF6'})[0] & A,0); self.assertEqual(self.one({'RF5','RF6'})[1:3],[128,205])
        self.assertEqual(self.one({'RF5'})[0] & A,A); self.assertEqual(self.one({'RF5'})[1:3],[128,205])
        for extra in ({'RF8'},{'RF7'},{'RF8','RF7'}): self.assertEqual(self.one({'RF5','RF6'}|extra)[0]&A,0)
    def test_grab_lt2_crouchjab_and_relocations(self):
        self.assertEqual(self.one({'LT4'})[0]&Z,Z)
        self.assertEqual(self.one({'RF15','LF2'})[0]&Z,Z); self.assertEqual(self.one({'RF15','LF2'})[1:3],[128,177])
        self.assertEqual(self.one({'RF15','RF8','LF3'})[1:3],[61,51])
        held={'LT2','RF8','RF7','RF6'}
        self.assertEqual(self.one(held)[0]&SHIELD,SHIELD)
        # Releasing any required RF input ends the defensive *override*;
        # ordinary LT2 Shield remains asserted where it is otherwise allowed.
        for released in ('RF8','RF7','RF6'):
            self.assertNotEqual(self.one((held-{released})|{'LF3'})[1:3],[195,51])
        # Down uses its physical direction rather than the automatic horizontal flip.
        self.assertEqual(self.one(held|{'LF5','LF3'})[1:3],[61,51])
        self.assertEqual(self.one({'RT1','RF6','LF3'})[1:3],[195,51])
        cj=self.one({'RT1','RF6','LT6','LF3'}); self.assertEqual(cj[0]&A,0); self.assertEqual(cj[1:3],[195,51]); self.assertEqual(cj[3:5],[128,28])
        self.assertEqual(self.one({'RF11'})[0]&8,8); self.assertEqual(self.one({'RF14'})[0]&128,128)
        self.assertEqual(self.one({'RF12'})[0]&A,A)
    def test_mash_row_all_subsets_no_button_leakage(self):
        intended={1:[61,51],3:[195,51],2:[195,205],6:[61,205],4:[61,51],12:[195,51],8:[195,205],24:[61,205],16:[61,51]}
        for bits in range(32):
            row=self.one({MASH[i] for i in range(5) if bits&(1<<i)})
            self.assertEqual(row[1:3], intended.get(bits,[128,128]), bits)
            self.assertEqual(row[0] & (A|8|128), 0, bits) # negative control: no A/Y/R leakage
        self.observations['mash_subsets']=32
    def test_socd_release_spring_and_mash_composition(self):
        # Both configured second-input-priority histories, asserted as actual
        # controller output rather than merely executed.
        h=self.run_frames([{'RF8','RF7','LF1'}, {'RF8','RF7','LF1','LF3'}, {'RF8','RF7','LF3'},
                           {'RF8','RF7','LF2'}, {'RF8','RF7','LF2','LF5'}, {'RF8','RF7','LF5'}])
        self.assertEqual([x[1:3] for x in h], [[195,51],[61,51],[61,51],[128,51],[128,51],[128,51]])
        spring=self.run_frames([{'RF5'}, {'RF5','RF6'}, {'RF5','RF6','RF7'}, {'RF5','RF7'}, {'RF7'}, set()])
        self.assertEqual([(x[0]&A,x[1:3]) for x in spring], [(A,[128,205]),(0,[128,205]),(0,[128,128]),(0,[128,205]),(0,[128,51]),(0,[128,128])])
        # Mash must retain its no-button policy even when command inputs are held.
        for bits in range(32):
            frame={'RF8','RF7'} | {MASH[i] for i in range(5) if bits&(1<<i)}
            self.assertEqual(self.one(frame)[0] & (A|8|128), 0, bits)
    def test_source_resources_and_negative_controls(self):
        p=codec.load_json(SOURCE); report=codec.compile_report(p)
        self.assertEqual((len(p['tables']),len(p['conditions']),len(p['tableRules']),len(p['digitalBindings']),len(p['analogEffects'])),(20,87,21,20,15))
        self.assertEqual((report['body_bytes'],report['token_count'],report['direction_source_count']),(2182,283,7))
        # RF6 alone must never revive retired Z; Crouch-Jab LT6 must never gain A.
        self.assertEqual(self.one({'RF6'})[0]&Z,0)
        self.assertEqual(self.one({'RT1','RF6','LT6'})[0]&A,0)

    def test_precedence_mutants_change_native_output(self):
        # Genuine compiled profile mutants: each would silently weaken a named
        # precedence/exclusion requirement if the test only inspected structure.
        mutants=[]
        def condition(profile, name): return next(x for x in profile['conditions'] if x['name']==name)
        p=copy.deepcopy(self.profile); p['analogEffects'][13]['priority']=201; mutants.append((p, {'RF15','LF2'}))
        p=copy.deepcopy(self.profile); condition(p,'lt2CdcDownBack')['all'].remove('condition:cdcTriple'); mutants.append((p, {'LT2','RF8','RF7','LF3'}))
        p=copy.deepcopy(self.profile); p['digitalBindings'][1]['when']='true'; mutants.append((p, {'LT6','RT1','RF6'}))
        p=copy.deepcopy(self.profile); p['tableRules'][0]['table']='Default'; mutants.append((p, {'LF8'}))
        for index,(profile,frame) in enumerate(mutants):
            wire=self.work / f'mutant-{index}.pb'; wire.write_bytes(codec.compile_profile(profile))
            self.assertNotEqual(self.one(frame), self.run_frames([frame], wire)[0], index)

if __name__ == '__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(KazuyaV5Tests))
    raise SystemExit(not result.wasSuccessful())
