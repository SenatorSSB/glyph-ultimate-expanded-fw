#!/usr/bin/env python3
"""Offline v1 contract proof; fixtures are synthetic and assert no gameplay rules."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

import jsonschema
import glyph_native_profile_json as codec
from test_glyph_native_profile_json import synthetic, CONTEXT

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'profiles/examples'
V1_SCHEMA = ROOT / 'profiles/schema/glyph-native-ultimate-profile.v1.schema.json'
DOMAIN = b'Glyph.Native.Authoring.v1\0'


def single():
    return codec.load_json(EXAMPLES / 'SyntheticSingle.v1.profile.json')


def sparse():
    return codec.load_json(EXAMPLES / 'SyntheticSparse.v1.profile.json')


def body(profile):
    return codec.unwrap_profile(codec.compile_profile(profile))


def canonical_digest(profile):
    semantic = {k: v for k, v in profile.items() if k not in ('name', 'metadata', 'provenance')}
    return hashlib.sha256(DOMAIN + json.dumps(semantic, sort_keys=True,
        separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')).digest()


def boundary():
    # Reuse the independent all-domains native fixture, giving every wire slot a
    # generic authoring symbol. No recovered product coordinates are imported.
    profile = codec.decode_profile(codec.wrap_body(synthetic(boundary=True)), CONTEXT, name='Synthetic capacity')
    names = {name: f'Slot{i:02d}' for i, name in enumerate(codec.TABLES)}
    profile['formatVersion'] = 1
    profile['provenance'] = {'kind': 'authoredSourceV1'}
    profile['tables'] = {names[name]: {'slot': t['id'], 'directions': t['directions']}
                         for name, t in profile['tables'].items()}
    profile['defaultTable'] = names[profile['defaultTable']]
    for rule in profile['tableRules']:
        rule['table'] = names[rule['table']]
    for record in profile['digitalBindings'] + profile['analogEffects']:
        if record['winnerTable'] != 'any':
            record['winnerTable'] = names[record['winnerTable']]
    for effect in profile['analogEffects']:
        coords = effect.get('coordinates', {})
        if coords.get('mode') == 'table':
            for key in ('normalTable', 'modeTable'):
                coords[key] = names[coords[key]]
    return profile


def negatives():
    """Named mutations: syntax failures and cross-reference/native failures."""
    cases = []
    def add(label, mutation, source=None):
        p = copy.deepcopy(sparse() if source is None else source)
        mutation(p)
        cases.append((label, p))
    add('duplicate slots', lambda p: p['tables']['ForcedDown'].update(slot=0))
    for slot in (-1, 28, True, 0.5, '1'):
        add(f'invalid slot {slot!r}', lambda p, slot=slot: p['tables']['Default'].update(slot=slot))
    add('missing slot', lambda p: p['tables']['Default'].pop('slot'))
    add('legacy id field', lambda p: p['tables']['Default'].update(id=0))
    add('incomplete directions', lambda p: p['tables']['Default']['directions'].pop('9'))
    add('extra direction', lambda p: p['tables']['Default']['directions'].update({'0': [128, 128]}))
    for point in ([-1, 0], [0, 256], [True, 0], [0.5, 0], [1], [1, 2, 3], '128,128'):
        add(f'invalid coordinate {point!r}', lambda p, point=point: p['tables']['Default']['directions'].update({'5': point}))
    for name in ('', '9StartsWithDigit', 'has space', 'punctuation!', 'é', 'A' * 65, 'any', 'Good\n'):
        add('invalid table symbol ' + repr(name), lambda p, name=name: p['tables'].update({name: p['tables'].pop('Default')}))
    add('empty table inventory', lambda p: p.update(tables={}))
    add('over 28 tables', lambda p: p.update(tables={f'T{i}': {'slot': i % 28, 'directions': copy.deepcopy(p['tables']['Default']['directions'])} for i in range(29)}))
    for ref in ('Absent', 7, 'any'):
        add(f'defaultTable {ref!r}', lambda p, ref=ref: p.update(defaultTable=ref))
        add(f'rule table {ref!r}', lambda p, ref=ref: p['tableRules'][0].update(table=ref))
        for key in ('normalTable', 'modeTable'):
            add(f'coordinate {key} {ref!r}', lambda p, ref=ref, key=key: p['analogEffects'][1]['coordinates'].update({key: ref}))
    for ref in ('Absent', 7):
        add(f'binding winner {ref!r}', lambda p, ref=ref: p['digitalBindings'][0].update(winnerTable=ref))
        add(f'effect winner {ref!r}', lambda p, ref=ref: p['analogEffects'][0].update(winnerTable=ref))
    for version in (2, -1, True, '1', None):
        add(f'unknown version {version!r}', lambda p, version=version: p.update(formatVersion=version))
    add('missing version', lambda p: p.pop('formatVersion'))
    add('unknown root field', lambda p: p.update(macro='unsupported'))
    for section in ('preprocessing', 'gates', 'dpad', 'digitalPostMask', 'provenance'):
        add('unknown ' + section, lambda p, section=section: p[section].update(unknown=1))
    add('unknown table field', lambda p: p['tables']['Default'].update(unknown=1))
    add('unknown condition field', lambda p: p['conditions'][0].update(unknown=1))
    add('unknown rule field', lambda p: p['tableRules'][0].update(unknown=1))
    add('unknown binding field', lambda p: p['digitalBindings'][0].update(unknown=1))
    add('unknown effect field', lambda p: p['analogEffects'][0].update(unknown=1))
    add('unknown coordinate field', lambda p: p['analogEffects'][1]['coordinates'].update(unknown=1))
    add('legacy provenance', lambda p: p.update(provenance={'kind': 'preservedConversionSourceSha256', 'sha256': '0' * 64}))
    add('manual authored digest', lambda p: p['provenance'].update(sha256='0' * 64))
    add('condition self cycle', lambda p: p['conditions'][0].update(all=['condition:forceDown']))
    add('condition forward reference', lambda p: p['conditions'][0].update(all=['condition:resolvedLeft']))
    add('unknown condition reference', lambda p: p['tableRules'][0].update(when='condition:Absent'))
    add('early reads directions', lambda p: p['conditions'][0].update(all=['direction:leftStickLeft']))
    add('base source reads late condition', lambda p: p['directionSources'][0].update(left='condition:resolvedLeft'))
    add('duplicate condition names', lambda p: p['conditions'][1].update(name='forceDown'))
    add('duplicate source names', lambda p: p['directionSources'].append(copy.deepcopy(p['directionSources'][0])))
    add('missing direction source', lambda p: p.update(leftStickSource='Absent'))
    add('final digital before bindings', lambda p: p['digitalBindings'][0].update(when='finalDigital:buttonA'))
    add('final digital mode gate', lambda p: p['gates'].update(mode='finalDigital:buttonA'))
    add('duplicate rule priorities', lambda p: p['tableRules'][1].update(priority=10))
    add('overlapping both-stick priority', lambda p: p['analogEffects'][2].update(priority=10))
    add('post-mask overlap', lambda p: p['digitalPostMask'].update(set=['buttonA'], clear=['buttonA']))
    add('97 conditions', lambda p: p.update(conditions=[{'name': f'C{i}', 'stage': 'early', 'all': [], 'any': [], 'none': []} for i in range(97)]))
    add('9 direction sources', lambda p: p.update(directionSources=[dict(p['directionSources'][0], name=f'S{i}') for i in range(9)]))
    add('no direction sources', lambda p: p.update(directionSources=[]))
    add('33 table rules', lambda p: p.update(tableRules=[dict(p['tableRules'][0], priority=i+1) for i in range(33)]))
    add('33 bindings', lambda p: p.update(digitalBindings=p['digitalBindings'][:1] * 33))
    add('17 effects', lambda p: p.update(analogEffects=p['analogEffects'][:1] * 17))
    add('all local capacity', lambda p: p['conditions'][0].update(all=['true'] * 3))
    add('any local capacity', lambda p: p['conditions'][0].update(any=['true'] * 5))
    add('none local capacity', lambda p: p['conditions'][0].update(none=['false'] * 10))
    add('769 pool tokens', lambda p: p['conditions'][0]['none'].append('false'), boundary())
    return cases


class V1PositiveTests(unittest.TestCase):
    def test_one_table_and_all_neutral_slots(self):
        p = single(); b = body(p)
        self.assertEqual(b[16], 27)
        for slot in range(28):
            actual = b[96 + slot*18:114 + slot*18]
            expected = bytes(v for d in range(1, 10) for v in p['tables']['Only_Table-1']['directions'][str(d)]) if slot == 27 else bytes([128] * 18)
            self.assertEqual(actual, expected, slot)
        self.assertEqual(len(b), 617)

    def test_sparse_nonsequential_slots_and_nonneutral_five(self):
        p = sparse(); b = body(p)
        self.assertEqual(b[:8], b'GNP5\x01\x00\x01\x00')
        occupied = {t['slot'] for t in p['tables'].values()}
        for name, t in p['tables'].items():
            self.assertEqual(b[96 + t['slot']*18:114 + t['slot']*18], bytes(v for d in range(1, 10) for v in t['directions'][str(d)]), name)
        for slot in set(range(28)) - occupied:
            self.assertEqual(b[96 + slot*18:114 + slot*18], bytes([128] * 18))
        self.assertEqual(b[96+7*18+8:96+7*18+10], bytes([128, 51]))
        self.assertNotEqual(p['tables']['Default']['directions']['1'], p['tables']['Default']['directions']['9'])

    def test_references_resolve_to_slots(self):
        b = body(sparse()); n, _, ns, nr, nb, ne = b[10:16]
        rule = 600 + 3*n + 2*struct.unpack_from('<H', b, 92)[0] + 9*ns
        self.assertEqual(b[16], 0)
        self.assertEqual([b[rule + i*4 + 1] for i in range(nr)], [7, 27])
        binding = rule + nr*4
        self.assertEqual([b[binding + i*6 + 4] for i in range(nb)], [7, 255])
        effect = binding + nb*6
        self.assertEqual(b[effect+32+8:effect+32+10], bytes([13, 27]))
        self.assertEqual(b[effect+4*32+28], 7)
        self.assertEqual(ne, 6)

    def test_arbitrary_symbols_and_inventory_order(self):
        p = single(); t = p['tables'].pop('Only_Table-1')
        name = 'A' + 'x' * 63
        p['tables'][name] = t; p['defaultTable'] = name
        self.assertEqual(body(p)[16], 27)
        p = sparse(); original = codec.compile_profile(p)
        p['tables'] = dict(reversed(list(p['tables'].items())))
        self.assertEqual(codec.compile_profile(p), original)

    def test_slot_zero_as_only_table(self):
        p = single(); p['tables']['Only_Table-1']['slot'] = 0
        self.assertEqual(body(p)[16], 0)

    def test_mode_false_and_active_native_tokens(self):
        for token, expected in [('false', 0), ('true', 65535), ('original:RF8', 24), ('condition:alternateInput', 0x3002), ('direction:leftStickUp', 0x4004)]:
            p = sparse(); p['gates']['mode'] = token
            self.assertEqual(struct.unpack_from('<H', body(p), 20)[0], expected)

    def test_native_capacity_boundary(self):
        p = boundary(); b = body(p)
        self.assertEqual(len(b), 3336)
        self.assertEqual(list(b[10:16]), [96, 95, 8, 32, 32, 16])
        self.assertEqual(struct.unpack_from('<H', b, 92)[0], 768)
        broken = bytearray(b + b'\0'); struct.pack_into('<H', broken, 8, len(broken))
        with self.assertRaises(ValueError):
            codec.wrap_body(bytes(broken))

    def test_all_coordinate_modes_targets_and_routing_flags(self):
        for bits in range(8):
            p = sparse()
            p['dpad'] = {k: bool(bits & (1 << i)) for i, k in enumerate(('routeToDpad', 'bypassLeftStick', 'suppressLeftStickDigital'))}
            self.assertEqual(body(p)[19], bits)
        p = sparse()
        self.assertEqual({e['coordinates']['mode'] for e in p['analogEffects'] if 'coordinates' in e}, {'selectedTable', 'table', 'fixed', 'inline'})
        self.assertEqual({e['target'] for e in p['analogEffects']}, set(codec.TARGETS))

    def test_preprocessing_matches_production_ordered_digest(self):
        p = sparse()
        p['preprocessing']['remaps'] = [{'physical': 'LF1', 'activates': 'RF2'}, {'physical': 'RF1', 'activates': 'none'}]
        p['preprocessing']['socd'] = [{'first': 'LF1', 'second': 'LF2', 'policy': policy} for policy in codec.POLICIES]
        self.assertEqual(body(p)[28:60], hashlib.sha256(codec.context_bytes(p['preprocessing'])).digest())
        b = body(p); p['preprocessing']['remaps'].reverse()
        self.assertNotEqual(body(p)[28:60], b[28:60])

    def test_manifest_matches_wire(self):
        for name in ('SyntheticSingle', 'SyntheticSparse'):
            profile = codec.load_json(EXAMPLES / (name + '.v1.profile.json'))
            expected_report = codec.load_json(ROOT / 'tools/fixtures/native_profile_json_v1' / (name + '.compile-report.json'))
            self.assertEqual(codec.compile_report(profile), expected_report)
        p = sparse(); report = codec.compile_report(p); raw = codec.compile_profile(p); b = codec.unwrap_profile(raw)
        expected = {'profile_name': p['name'], 'format_version': 1, 'declared_tables': sorted(p['tables']), 'table_slots': {n: t['slot'] for n, t in p['tables'].items()}, 'neutral_filled_slots': sorted(set(range(28)) - {t['slot'] for t in p['tables'].values()}), 'condition_count': 3, 'token_count': 3, 'direction_source_count': 1, 'table_rule_count': 2, 'digital_binding_count': 2, 'analog_effect_count': 6, 'body_bytes': len(b), 'wrapper_bytes': len(raw), 'preprocessing_sha256': b[28:60].hex(), 'provenance_sha256': b[60:92].hex(), 'provenance_kind': 'authoredSourceV1', 'body_sha256': hashlib.sha256(b).hexdigest(), 'wrapper_sha256': hashlib.sha256(raw).hexdigest()}
        for key, value in expected.items():
            self.assertEqual(report[key], value, key)

    def test_cli_validate_compile_report_and_protobuf_json(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'profile.pb'; report = Path(d) / 'report.json'; proto = Path(d) / 'profile.json'
            def run(*args):
                return subprocess.run([sys.executable, str(ROOT/'tools/glyph_native_profile_json.py'), *map(str, args)], capture_output=True, text=True, check=True)
            src = EXAMPLES/'SyntheticSparse.v1.profile.json'
            run('validate', src); run('compile', src, '--output', out)
            run('compile', src, '--format', 'protobuf-json', '--output', proto)
            run('report', src, '--output', report)
            self.assertEqual(codec.unwrap_profile(codec.load_json(proto)), codec.unwrap_profile(out.read_bytes()))
            self.assertEqual(codec.load_json(report), codec.compile_report(sparse()))
            self.assertEqual(json.loads(run('report', src).stdout), codec.load_json(report))

    def test_binary_decode_retains_only_archival_wire_representation(self):
        p = sparse(); raw = codec.compile_profile(p)
        decoded = codec.decode_profile(raw, p['preprocessing'])
        self.assertEqual(decoded['formatVersion'], 0)
        self.assertEqual(len(decoded['tables']), 28)
        self.assertEqual(codec.compile_profile(decoded), raw)
        self.assertNotIn('ForcedDown', decoded['tables'])


class V1ProvenanceTests(unittest.TestCase):
    def test_exact_independent_canonical_digest(self):
        for p in (single(), sparse(), boundary()):
            self.assertEqual(body(p)[60:92], canonical_digest(p))

    def test_identical_semantics_and_object_key_order(self):
        p = sparse(); raw = codec.compile_profile(p)
        def reverse(value):
            if isinstance(value, dict): return {k: reverse(v) for k, v in reversed(list(value.items()))}
            if isinstance(value, list): return [reverse(v) for v in value]
            return value
        self.assertEqual(codec.compile_profile(reverse(p)), raw)
        self.assertEqual(codec.compile_profile(json.loads(json.dumps(p, indent=4))), raw)

    def test_metadata_and_display_name_are_nonsemantic(self):
        p = sparse(); raw = codec.compile_profile(p)
        p['name'] = 'A changed display name'
        p['metadata'] = {'description': 'Edited', 'notes': ['Unicode: ö'], 'character': None}
        self.assertEqual(codec.compile_profile(p), raw)
        del p['metadata']
        self.assertEqual(codec.compile_profile(p), raw)

    def test_coordinate_and_slot_edits_change_digest(self):
        for change in ('coordinate', 'slot'):
            p = sparse(); before = body(p)[60:92]
            if change == 'coordinate': p['tables']['Default']['directions']['5'][0] += 1
            else: p['tables']['ForcedDown']['slot'] = 8
            self.assertNotEqual(body(p)[60:92], before)

    def test_condition_and_rule_edits_change_digest(self):
        for change in ('condition', 'rule'):
            p = sparse(); before = body(p)[60:92]
            if change == 'condition': p['conditions'][0]['all'] = ['postSocd:RF2']
            else: p['tableRules'][0]['priority'] = 11
            self.assertNotEqual(body(p)[60:92], before)

    def test_symbolic_table_rename_changes_only_provenance(self):
        p = single(); before = body(p)
        p['tables']['Renamed'] = p['tables'].pop('Only_Table-1'); p['defaultTable'] = 'Renamed'
        after = body(p)
        self.assertNotEqual(after[60:92], before[60:92])
        self.assertEqual(after[:60] + after[92:], before[:60] + before[92:])

    def test_condition_and_source_renames_are_semantic_source_identity(self):
        for change in ('condition', 'source'):
            p = sparse(); before = body(p)
            if change == 'condition':
                p['conditions'][1]['name'] = 'RenamedCondition'
            else:
                p['directionSources'][0]['name'] = 'RenamedSource'
                p['leftStickSource'] = p['rightStickSource'] = 'RenamedSource'
                for e in p['analogEffects']:
                    if 'source' in e: e['source'] = 'RenamedSource'
            after = body(p)
            self.assertNotEqual(after[60:92], before[60:92])
            self.assertEqual(after[:60] + after[92:], before[:60] + before[92:])

    def test_array_order_is_preserved(self):
        p = sparse(); before = body(p)[60:92]
        p['digitalBindings'].reverse()
        self.assertNotEqual(body(p)[60:92], before)


class V1NegativeTests(unittest.TestCase):
    def test_all_negative_fixtures_fail_compilation(self):
        for label, p in negatives():
            with self.subTest(case=label), self.assertRaises(ValueError):
                codec.compile_profile(p)

    def test_duplicate_table_names_rejected_at_json_load(self):
        # Duplicate object keys cannot survive a Python dict or JSON Schema.
        p = single(); text = json.dumps(p)
        table = json.dumps(p['tables']['Only_Table-1'])
        text = text.replace('"tables": {', '"tables": {"Only_Table-1": ' + table + ', ', 1)
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / 'duplicate.json'; file.write_text(text)
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                codec.load_json(file)

    def test_builtin_and_standard_schema_agree_on_all_fixtures(self):
        schema = codec.load_json(V1_SCHEMA)
        jsonschema.Draft202012Validator.check_schema(schema)
        standard = jsonschema.Draft202012Validator(schema)
        cases = [('single', single()), ('sparse', sparse()), ('capacity', boundary())] + negatives()
        for label, p in cases:
            builtin_ok = True
            try: codec._schema_check(p, schema)
            except ValueError: builtin_ok = False
            with self.subTest(case=label):
                self.assertEqual(builtin_ok, standard.is_valid(p))
        for p in (single(), sparse(), boundary()):
            standard.validate(p)


if __name__ == '__main__':
    print(f'V1 fixtures: 12 positive test methods; 8 provenance methods; {len(negatives()) + 1} negative cases (including duplicate-key input); independent schema agreement over {len(negatives()) + 3} fixtures.', flush=True)
    unittest.main()
