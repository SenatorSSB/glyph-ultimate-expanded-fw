#!/usr/bin/env python3
"""Offline Kazuya requirements against production preprocessing and native evaluator.

Needs the existing Nanopb dependency and jsonschema. No serial/device imports.
The finite expected matrix is hand specified from the owner work order; the
implementation under test is the actual C++ Ultimate native path.
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
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import jsonschema
import glyph_native_profile_json as codec
from check_glyph_profile_native_ultimate import compile_runner

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'tools/fixtures/kazuya'
SOURCE = ROOT / 'profiles/kazuya/Kazuya.profile.json'
SEED = 0xa0030000  # existing native runner's unowned-bit sentinel
SHIELD = (1 << 4) | (1 << 6) | (1 << 7)
# Bit order RF5, RF6, RF7, RF8. Each row is (selected table, A/B/Z mask).
MATRIX = [
    ('Default', 0), ('Default', 1), ('Default', 32), ('Default', 33),
    ('ForcedDown', 0), ('ForcedDown', 1), ('DownDiagonal', 1), ('DownDiagonal', 1),
    ('ForcedDown', 0), ('CDCNeutral', 1), ('DownDiagonal', 32), ('DownDiagonal', 33),
    ('DownDiagonal', 0), ('DownDiagonal', 2), ('CDCNeutral', 0), ('DownBack', 0),
]
# Explicit side values, never geometric mirroring of an expected effective value.
RAW = {
    'ForcedDown': [[128, 51], [128, 51], [128, 51]],
    'DownDiagonal': [[61, 51], [128, 128], [195, 51]],
    'CDCNeutral': [[128, 128], [128, 128], [128, 128]],
    'DownBack': [[195, 51], [128, 128], [61, 51]],
    'DefensiveDownBack': [[179, 98], [128, 128], [77, 98]],
}
SLOTS = {'Default': 0, 'ForcedDown': 1, 'DownDiagonal': 2, 'CDCNeutral': 3,
         'DownBack': 4, 'DefensiveDownBack': 5}
DEFAULT = [[61,51],[128,51],[195,51],[61,128],[128,128],[195,128],
           [61,205],[128,205],[195,205]]
LOW = [[89,89],[128,79],[167,89],[79,128],[128,128],[177,128],
       [89,167],[128,177],[167,167]]
BASE_C = [[28,28],[128,28],[228,28],[28,128],[128,128],[228,128],
          [28,228],[128,228],[228,228]]
DIAG_C = [[86,60],[128,60],[170,60],[86,128],[128,128],[170,128],
          [86,196],[128,196],[170,196]]

def mask(names):
    return sum(1 << codec.INPUTS.index(n) for n in set(names))

def inputs(rf):
    return {f'RF{i+5}' for i in range(4) if rf & (1 << i)}

def expected(rf, side=0, vertical=0, shield=False, extra=()):
    """Requirements oracle for simple ordinary inputs plus the explicit RF matrix.

    Complex retained modifiers are checked differentially against the immutable
    archival profile, not reimplemented here.
    """
    names = inputs(rf) | set(extra)
    command = bool(rf & 12)
    table, digital = MATRIX[rf]
    if shield:
        names.add('LT2'); digital |= SHIELD
        if command: table = 'DefensiveDownBack'
    x = side
    # Preserve native quadrant flags separately from forced raw geometry.
    up = vertical == 1 or (rf & 1 and not command)
    down = vertical == -1 and not (rf & 1 and not command)
    y = -1 if down else 1 if up else 0
    if table in RAW: ls = RAW[table][x+1]
    elif rf & 2: ls = LOW[(y+1)*3+x+1]
    elif rf & 1: ls = [128,205]
    else: ls = DEFAULT[(y+1)*3+x+1]
    for name, value in [('RF1',1),('RF2',2),('RF3',4),('RF10',8),
                        ('LT1',80),('RF16',128),('MB7',256),('MB6',512),
                        ('MB5',1024),('MB4',2048)]:
        if name in names:digital |= value
    cx = -1 if 'RT3' in names else 1 if 'RT4' in names else 0
    cy = -1 if 'RT2' in names else 1 if 'RT5' in names else 0
    rs = (DIAG_C if cx and cy else BASE_C)[(cy+1)*3+cx+1]
    # Retained RF3 + vertical C + LF horizontal transformation.
    if 'RF3' in names and cy and x and not cx:
        rs = [[95,91],[128,91],[161,91],[95,91],[128,91],[161,91],
              [95,165],[128,165],[161,165]][(cy+1)*3+x+1]
    dpad = 'RF13' in names and not command
    if dpad:
        ls = [128,128]
        digital |= (1<<14 if x<0 else 1<<15 if x>0 else 0)
        digital |= (1<<13 if down else 0) | (1<<12 if up else 0)
    else:
        digital |= (1<<18 if x<0 else 1<<19 if x>0 else 0)
        digital |= (1<<21 if down else 0) | (1<<20 if up else 0)
    for name,bit in [('RT3',22),('RT4',23),('RT2',25),('RT5',24)]:
        if name in names:digital |= 1<<bit
    if 'RF9' in names and 'RF3' not in names:
        if not command:ls=[128,128]
        rs=[128,128]
    return table, [digital | SEED, *ls, *rs, 140 if digital&64 else 0,
                    140 if digital&128 else 0]

def context_wire():
    # Exact tracked GameModeConfig protobuf field IDs, schema/haybox/config.proto.
    data = b'\x08\x03'
    for a,b in [(3,1),(5,2)]:data += bytes([26,6,8,a,16,b,24,2])
    for n in ['RF3','RF4','LT3']:
        i=codec.INPUTS.index(n)+1;data += bytes([34,4,8,i,16,i])
    return data

def verify_workbook(path):
    """Check the committed extract against exact cached measurement cells.

    Read-only, standard-library XLSX inspection; no formulas are invented or
    recalculated. This is the dataset's stored Values sheet, not an LS/RS model.
    """
    evidence=codec.load_json(FIX/'coordinate-evidence.json')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==evidence['workbook']['sha256']
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with ZipFile(path) as archive:
        workbook=ET.fromstring(archive.read('xl/workbook.xml'))
        rels=ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        targets={r.get('Id'):r.get('Target') for r in rels}
        sheet=next(s for s in workbook.findall('m:sheets/m:sheet',ns) if s.get('name')=='Values')
        target=targets[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        rows={int(r['range'].split(':')[0][1:]):r for r in evidence['measurements']}
        count=0
        for _,row in ET.iterparse(archive.open(target),events=['end']):
            if row.tag!='{'+ns['m']+'}row':continue
            number=int(row.get('r'))
            if number in rows:
                values={''.join(c for c in cell.get('r') if c.isalpha()):float(cell.find('m:v',ns).text)
                    for cell in row.findall('m:c',ns) if cell.find('m:v',ns) is not None and cell.get('t') not in ['s','inlineStr']}
                assert [values[c] for c in 'ABCD']==rows[number]['raw']+rows[number]['effective']
                count+=1
            row.clear()
        assert count==len(rows)
    return count

class KazuyaTests(unittest.TestCase):
    observations = {}
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='kazuya-native-')
        cls.work = Path(cls.temp.name)
        cls.exe, _, _, _ = compile_runner(cls.work)
        cls.profile = codec.load_json(SOURCE)
        cls.context = cls.work/'context.pb'; cls.context.write_bytes(context_wire())
        cls.wire = cls.work/'Kazuya.pb';cls.wire.write_bytes(codec.compile_profile(cls.profile))
        cls.golden = ROOT/'tools/fixtures/native_profile_json/Ultimate.pb'
        # Diagnostic table-selection probe runs the *same* native conditions,
        # rules, sources and preprocessing. Only coordinates/effects are tagged.
        probe = copy.deepcopy(cls.profile)
        for t in probe['tables'].values():
            t['directions']={str(d):[t['slot']+1,128] for d in range(1,10)}
        probe['analogEffects']=[dict(cls.profile['analogEffects'][1],
            priority=1,skipWhenDpadBypass=False)]
        cls.probe=cls.work/'selection.pb';cls.probe.write_bytes(codec.compile_profile(probe))
        effect_probe=copy.deepcopy(cls.profile)
        for i,effect in enumerate(effect_probe['analogEffects']):
            if effect['target'] not in ['triggerL','triggerR']:
                effect['coordinates']={'mode':'fixed','point':[50+i,50+i]}
        cls.effects_probe=cls.work/'effects.pb'
        cls.effects_probe.write_bytes(codec.compile_profile(effect_probe))

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def run_frames(self, frames, wire=None):
        path=self.work/'frames.txt';path.write_text(''.join(f'{mask(f):x}\n' for f in frames))
        result=subprocess.run([str(self.exe),str(wire or self.wire),'sequence',
            str(self.context),str(path)],capture_output=True,text=True,check=True)
        rows=[]
        for line in result.stdout.splitlines():
            fields=line.split();rows.append([int(fields[0],16),*map(int,fields[1:])])
        self.assertEqual(len(rows),len(frames))
        return rows

    def check_cases(self, label, cases):
        frames=[]
        for names,_,_ in cases:frames.extend([set(),names])
        outputs=self.run_frames(frames)[1::2]
        selected=self.run_frames(frames,self.probe)[1::2]
        effects=self.run_frames(frames,self.effects_probe)[1::2]
        for (names,table,want),got,probe,effect in zip(cases,outputs,selected,effects):
            self.assertEqual(got,want,f'{label}: {sorted(names)}')
            self.assertEqual(probe[1],SLOTS[table]+1,f'{label}: selected table {sorted(names)}')
            if names & {'RF7','RF8'}:winner=0
            elif 'RF9' in names and 'RF3' not in names:winner=7
            elif 'RF13' in names:winner=10
            elif 'RF6' in names:winner=4
            elif 'RF5' in names:winner=3
            else:winner=1
            self.assertEqual(effect[1:3],[50+winner]*2,f'{label}: analogue winner {sorted(names)}')
        self.observations[label]=len(cases)

    def test_command_matrix_and_composition(self):
        cases=[]
        extras=[(),('RF1',),('RF2',),('RF3',),('RF10',),('LT1',),('RF16',),
                ('RF1','RF2','RF3','RF10'),('MB4','MB5','MB6','MB7'),
                ('RT3',),('RT4','RT5'),('RT2',),('RF3','RT5'),('RF9',),('RF13',)]
        extras += [tuple(n for i,n in enumerate(['RT2','RT3','RT4','RT5']) if b&(1<<i)) for b in range(16)]
        for rf,side,vertical,shield,extra in itertools.product(range(16),[-1,0,1],[-1,0,1],[False,True],extras):
            # RF3 alone selects a retained modifier only with RF4, absent here.
            names=inputs(rf)|set(extra)
            if side:names.add('LF3' if side<0 else 'LF1')
            if vertical:names.add('LF5' if vertical<0 else 'LF2')
            if shield:names.add('LT2')
            table,want=expected(rf,side,vertical,shield,extra)
            cases.append((names,table,want))
        self.check_cases('matrix_composition',cases)

    def test_release_addition_and_socd_history(self):
        count=0
        # All single RF-button additions/releases, both LT2 states and both sides.
        for shield,side in itertools.product([False,True],[-1,1]):
            for rf in range(16):
                for bit in [1,2,4,8]:
                    target=rf^bit
                    fixed={'LF3' if side<0 else 'LF1'}|({'LT2'} if shield else set())
                    frames=[set(),fixed|inputs(rf),fixed|inputs(target)]
                    got=self.run_frames(frames)
                    for at,state in [(1,rf),(2,target)]:
                        self.assertEqual(got[at],expected(state,side,shield=shield)[1])
                        count+=1
            # Shield release ordering complete CDC -> either singleton -> none.
            for singleton in [4,8]:
                states=[12,singleton,0]
                fixed={'LT2','LF3' if side<0 else 'LF1'}
                got=self.run_frames([set(),*[fixed|inputs(s) for s in states]])[1:]
                self.assertEqual(got,[expected(s,side,shield=True)[1] for s in states]);count+=3
        # Existing 2IP is history-sensitive preprocessing, not RF timing logic.
        for rf,shield in itertools.product(range(4,16),[False,True]):
            fixed=inputs(rf)|({'LT2'} if shield else set())
            for first,second,sign in [('LF1','LF3',-1),('LF3','LF1',1)]:
                frames=[set(),fixed|{first},fixed|{first,second},fixed|{first},fixed]
                got=self.run_frames(frames)
                self.assertEqual(got[2],expected(rf,sign,shield=shield)[1])
                self.assertEqual(got[3],expected(rf,-sign,shield=shield)[1])
                self.assertEqual(got[4],expected(rf,0,shield=shield)[1]);count+=3
            # Simultaneous physical opponents from reset resolve to neither.
            got=self.run_frames([set(),fixed|{'LF1','LF3'}])[-1]
            self.assertEqual(got,expected(rf,0,shield=shield)[1]);count+=1
        self.observations['release_and_socd']=count

    def test_retained_baseline_differential(self):
        # All physical table-selector overlaps, all LF axis states, representative
        # ordinary buttons and all C-stick states. RF5..8/LT2 are replaced inputs.
        selectors=['LT3','LT4','LT5','RF3','RF4','RF9','RT1','LF4','RF2']
        frames=[]
        for bits in range(1<<len(selectors)):
            base={n for i,n in enumerate(selectors) if bits&(1<<i)}
            for side,vertical,c,rf in itertools.product([-1,0,1],[-1,0,1],[(),('RT2',),('RT3','RT5')],range(4)):
                names=base|set(c)|inputs(rf)
                if side:names.add('LF3' if side<0 else 'LF1')
                if vertical:names.add('LF5' if vertical<0 else 'LF2')
                frames.extend([set(),names])
        for name in codec.INPUTS:
            if name not in ['RF5','RF6','RF7','RF8','LT2']:frames.extend([set(),{name}])
        current=self.run_frames(frames);golden=self.run_frames(frames,self.golden)
        shielded=self.run_frames([names|{'LT2'} for names in frames])
        for i,(a,b) in enumerate(zip(current,golden)):
            self.assertEqual(a,b,f'retained differential: {sorted(frames[i])}')
            self.assertEqual(shielded[i],[b[0]|SHIELD,*b[1:5],140,140],
                f'LT2 unrestricted geometry: {sorted(frames[i])}')
        self.observations['retained_differential_frames']=len(frames)
        self.observations['lt2_retained_overlay_frames']=len(frames)

    def test_schema_resources_provenance_and_golden(self):
        p=self.profile;body=codec.unwrap_profile(codec.compile_profile(p))
        jsonschema.Draft202012Validator(codec.load_json(codec.V1_SCHEMA_PATH)).validate(p)
        report=codec.compile_report(p)
        self.assertEqual(report,codec.load_json(FIX/'compile-report.json'))
        self.assertEqual(p['gates']['mode'],'false')
        self.assertEqual(p['provenance'],{'kind':'authoredSourceV1'})
        self.assertEqual(p['preprocessing'],codec.load_json(ROOT/'profiles/ultimate/Ultimate.profile.json')['preprocessing'])
        self.assertEqual(body[28:60].hex(),'3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f')
        semantic={k:v for k,v in p.items() if k not in ['name','metadata','provenance']}
        digest=hashlib.sha256(b'Glyph.Native.Authoring.v1\0'+json.dumps(semantic,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).digest()
        self.assertEqual(body[60:92],digest)
        for slot in report['neutral_filled_slots']:self.assertEqual(body[96+slot*18:114+slot*18],bytes([128])*18)
        self.assertEqual(len({t['slot'] for t in p['tables'].values()}),len(p['tables']))
        self.assertEqual(len({r['priority'] for r in p['tableRules']}),len(p['tableRules']))
        for key,limit in [('body_bytes',3336),('condition_count',80),('token_count',600),
            ('direction_source_count',8),('table_rule_count',28),('digital_binding_count',30),('analog_effect_count',14)]:self.assertLessEqual(report[key],limit)
        archival=ROOT/'profiles/ultimate/Ultimate.profile.json'
        self.assertEqual(hashlib.sha1(b'blob '+str(len(archival.read_bytes())).encode()+b'\0'+archival.read_bytes()).hexdigest(),'0c25c3d6f85480898f18f6104fa4405ed2e497cb')
        self.assertEqual(codec.compile_profile(codec.load_json(archival)),self.golden.read_bytes())
        # Trigger effects consume final carriers, so a legitimate post-mask clear
        # removes digital and analogue L/R together. No policy is added to source.
        muted=copy.deepcopy(p);muted['digitalPostMask']['clear']=['triggerLDigital','triggerRDigital']
        path=self.work/'suppressed.pb';path.write_bytes(codec.compile_profile(muted))
        got=self.run_frames([{'LT2'}],path)[0]
        self.assertEqual(got,[SEED|16,128,128,128,128,0,0])

    def test_negative_mutants_are_detected(self):
        mutations=[]
        def add(label,fn,rf,side=1,shield=False,extra=()):
            p=copy.deepcopy(self.profile);fn(p);mutations.append((label,p,rf,side,shield,extra))
        def binding(p,input,output):p['digitalBindings'].append(dict(when='postSocd:'+input,outputs=[output],winnerTable='any'))
        add('historical RF7 B',lambda p:binding(p,'RF7','buttonB'),12)
        add('RF6 Z in EWGF',lambda p:binding(p,'RF6','buttonR'),6)
        add('RF6 Z in neutral',lambda p:binding(p,'RF6','buttonR'),14)
        add('RF5 A in Spinning Demon',lambda p:binding(p,'RF5','buttonA'),13)
        add('four-button RF5 A',lambda p:binding(p,'RF5','buttonA'),15)
        add('four-button B leakage',lambda p:binding(p,'RF5','buttonB'),15)
        add('LT2 becomes Z',lambda p:binding(p,'LT2','buttonR'),12,shield=True)
        add('RF8 Mode resurrection',lambda p:p['gates'].update(mode='postSocd:RF8'),12)
        # Mode is inert with equal normal/mode references. Detect it by contract,
        # since pretending a numerical output difference exists would be false.
        for idx,rf in [(3,13),(4,14)]:
            def override(p,idx=idx):p['analogEffects'][idx].update(priority=1,activation='postSocd:RF5' if idx==3 else 'postSocd:RF6')
            add('ordinary analogue override '+str(idx),override,rf)
        def residual(p):
            p['digitalPostMask']['clear']=['triggerLDigital','triggerRDigital']
            for e in p['analogEffects']:
                if e['target'] in ['triggerL','triggerR']:e['activation']='postSocd:LT2'
        add('residual analogue after carrier clear',residual,0,shield=True)
        caught=[]
        for label,p,rf,side,shield,extra in mutations:
            if label=='RF8 Mode resurrection':self.assertNotEqual(p['gates']['mode'],'false');caught.append(label);continue
            path=self.work/'mutant.pb';path.write_bytes(codec.compile_profile(p))
            names=inputs(rf)|set(extra)|{'LF1' if side>0 else 'LF3'}|({'LT2'} if shield else set())
            got=self.run_frames([set(),names],path)[-1]
            want=expected(rf,side,shield=shield,extra=extra)[1]
            if label=='residual analogue after carrier clear':want=[want[0]&~192,*want[1:5],0,0]
            self.assertNotEqual(got,want,label);caught.append(label)
        self.observations['negative_mutants']=caught

    def test_coordinate_evidence_and_retained_inventory(self):
        evidence=codec.load_json(FIX/'coordinate-evidence.json')
        lookup={tuple(row['raw']):row for row in evidence['measurements']}
        self.assertEqual(len(lookup),67)
        for name,table in self.profile['tables'].items():
            self.assertEqual(table['directions'],evidence['tables'][name]['directions'])
            self.assertEqual(table['slot'],evidence['tables'][name]['slot'])
            for point in table['directions'].values():self.assertIn(tuple(point),lookup)
            refs=evidence['tables'][name]['references']
            self.assertTrue(refs,name+' has no reachable table reference')
            archival_name=evidence['tables'][name]['source'].get('table')
            if evidence['tables'][name]['source']['kind']=='archivalTable':
                archived=codec.load_json(ROOT/'profiles/ultimate/Ultimate.profile.json')
                self.assertEqual(table['directions'],archived['tables'][archival_name]['directions'])
        for raw,effective in [((61,51),[-83,-99]),((195,51),[83,-99]),
            ((77,98),[-83,-34]),((179,98),[83,-34]),((128,128),[0,0]),((128,51),[0,-120])]:
            self.assertEqual(lookup[raw]['effective'],effective)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path)
    parser.add_argument('--workbook',type=Path,help='Optional exact GC measurement workbook: verify all extracted cells')
    parser.add_argument('-v',action='store_true');args=parser.parse_args()
    measured=verify_workbook(args.workbook) if args.workbook else None
    result=unittest.TextTestRunner(verbosity=2 if args.v else 1).run(unittest.defaultTestLoader.loadTestsFromTestCase(KazuyaTests))
    if args.report:
        args.report.write_text(json.dumps({'status':'PASS' if result.wasSuccessful() else 'FAIL',
            'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'compile_report':codec.compile_report(codec.load_json(SOURCE)),
            'baseline':'9a2a20730625671f89988e3911242c71e3f3fc5b',
            'measurement_cells_checked':measured,
            'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [
                'src/modes/Ultimate.cpp','src/modes/UltimateNativeProfile.cpp',
                'src/modes/UltimateNativeEvaluator.cpp','src/core/ControllerMode.cpp',
                'src/core/InputMode.cpp','src/core/socd.cpp','include/core/state.hpp',
                'HAL/pico/src/comms/GamecubeBackend.cpp','schema/haybox/config.proto',
                'tools/glyph_native_profile_json.py','tools/test_kazuya_profile.py',
                'tools/fixtures/profile_native_ultimate/native_runner.cpp',
                'tools/fixtures/kazuya/coordinate-evidence.json']},
            'observations':KazuyaTests.observations,'tests_run':result.testsRun,
            'hardware_acceptance':'NOT_TESTED','installed':False},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
