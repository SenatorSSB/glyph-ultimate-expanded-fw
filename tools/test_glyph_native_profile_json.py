#!/usr/bin/env python3
"""Offline JSON codec tests, including independently packed finite ABI fixtures."""
from __future__ import annotations
import base64
import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest
import glyph_native_profile_json as codec
from convert_glyph_native_ultimate_profile import preprocessing_bytes, validate_native_body
ROOT = Path(__file__).resolve().parents[1]
CONTEXT = {'modeId': 'MODE_ULTIMATE'}


def preprocessing_digest():
    context = SimpleNamespace(mode_id=3, button_remapping=[], socd_pairs=[])
    return hashlib.sha256(preprocessing_bytes(context, SimpleNamespace(MODE_ULTIMATE=3))).digest()


def wrapper(body):
    length = len(body)
    encoded = bytearray()
    while length > 127:
        encoded.append((length & 127) | 128)
        length >>= 7
    return b'\x08\x05\x42' + bytes(encoded) + bytes([length]) + bytes(body)


def synthetic(*, boundary=False, dpad=7):
    """Exercise literal asymmetric tables; direction 5 intentionally is not centered."""
    count, early = (96, 95) if boundary else (3, 2)
    header = bytearray(96)
    header[:4] = b'GNP5'
    struct.pack_into('<HH', header, 4, 1, 1)
    nr, nb, ne = (32, 32, 16) if boundary else (2, 2, 7)
    header[10:20] = bytes([count, early, 8, nr, nb, ne, 27, 1, 2, dpad])
    struct.pack_into('<HHHH', header, 20, 0x3002, 0xffff, 0, 0x4008)
    header[28:60] = preprocessing_digest()
    header[60:92] = bytes(range(32))
    tables = bytes((t * 19 + d * 7 + a * 101) % 256
                   for t in range(28) for d in range(9) for a in range(2))
    conditions, tokens = bytearray(), []
    for ident in range(1, count + 1):
        if boundary:
            all_, any_, none = [1, 0x1001], [0x2001, 60, 0x103c, 0x203c], [0, 65535]
        elif ident == 1:
            all_, any_, none = [1, 0x103c], [0x2001, 0x203c, 0, 65535], [60]
        elif ident == 2:
            all_, any_, none = [0x3001], [], []
        else:
            all_, any_, none = [0x3002], [0x4001, 0x4008], []
        conditions += struct.pack('<BH', ident, len(all_) | len(any_) << 2 | len(none) << 5)
        tokens.extend(all_ + any_ + none)
    struct.pack_into('<H', header, 92, len(tokens))
    sources = b''.join(struct.pack('<BHHHH', i, 0x3001, 0x3002, 0x2001,
                                   0x3002 if i < 3 else 0x3000 + count) for i in range(1, 9))
    rules = b''.join(struct.pack('<BBH', i + 1, i % 28, 0x4001 if i % 2 else 65535) for i in range(nr))
    bindings = b''.join(struct.pack('<HHBB', 0x3000 + count, 4095 if i % 2 else 0,
                                    27 if i % 2 else 255, 0) for i in range(nb))
    effects = bytearray()
    for i in range(ne):
        target = (1, 2, 1, 2, 5, 3, 4)[i % 7]
        mode = (1, 2, 3, 4, 3, 0, 0)[i % 7]
        data = bytes([0, 255]) + bytes(16) if mode == 3 else bytes(range(18)) if mode == 4 else bytes(18)
        if target in (3, 4):
            data = bytes([255]) + bytes(17)
        effects += struct.pack('<BBHHBBBB18sBBH', target, i + 1,
                               0x500c if target in (3, 4) else 0x3000 + count,
                               0x5001 if target in (3, 4) else 0x4008,
                               0 if target in (3, 4) else 8, mode,
                               27 if mode == 2 else 0, 1 if mode == 2 else 0,
                               data, 27 if i % 2 else 255, 1 if target in (3, 4) else 3, 0)
    body = header + tables + conditions + b''.join(struct.pack('<H', t) for t in tokens) + sources + rules + bindings + effects + struct.pack('<HHHH', 0x4001, 0x555, 0xaaa, 1)
    struct.pack_into('<H', body, 8, len(body))
    validate_native_body(bytes(body))
    return bytes(body)


class NativeProfileJsonTests(unittest.TestCase):
    def decode(self, body=None):
        return codec.decode_profile(wrapper(synthetic() if body is None else body), CONTEXT, name='Synthetic')

    def assert_rejected(self, profile):
        with self.assertRaises((ValueError, TypeError)):
            codec.validate_profile(profile)
        with self.assertRaises((ValueError, TypeError)):
            codec.compile_profile(profile)

    def test_all_domains_modes_stages_and_raw_tables_roundtrip(self):
        for dpad in range(8):
            with self.subTest(dpad=dpad):
                body = synthetic(dpad=dpad)
                profile = self.decode(body)
                self.assertEqual(codec.compile_profile(profile), wrapper(body))
                self.assertIsInstance(codec.validate_profile(profile), dict)
                self.assertEqual(profile['formatVersion'], 0)
                self.assertEqual(len(profile['tables']), 28)
                for table in profile['tables'].values():
                    self.assertEqual(set(table['directions']), set('123456789'))
                self.assertTrue(any(t['directions']['5'] != [128, 128] for t in profile['tables'].values()))

    def test_exact_3336_byte_boundary(self):
        body = synthetic(boundary=True)
        self.assertEqual(len(body), 3336)
        self.assertEqual(codec.compile_profile(self.decode(body)), wrapper(body))
        oversized = bytearray(body + b'\0')
        struct.pack_into('<H', oversized, 8, len(oversized))
        with self.assertRaises(ValueError):
            self.decode(oversized)

    def test_explicit_token_pool_and_local_condition_limits(self):
        boundary = self.decode(synthetic(boundary=True))
        boundary['conditions'][0]['none'].append('original:LF1')
        with self.assertRaisesRegex(ValueError, 'token.*768'):
            codec.compile_profile(boundary)
        valid = self.decode()
        valid['conditions'][0]['none'] = ['postSocd:LF1'] * 9
        wire = codec.compile_profile(valid)
        self.assertEqual(codec.compile_profile(codec.decode_profile(wire, CONTEXT)), wire)
        # Priority 255 is admitted production data, even where its strict less-than
        # comparison makes it inert. Do not normalize or reject it in authoring.
        valid['tableRules'][0]['priority'] = 255
        valid['analogEffects'][0]['priority'] = 255
        wire = codec.compile_profile(valid)
        self.assertEqual(codec.compile_profile(codec.decode_profile(wire, CONTEXT)), wire)
        missing = self.decode()
        del missing['tables'][next(iter(missing['tables']))]
        self.assert_rejected(missing)
        bad_domain = self.decode()
        bad_domain['conditions'][0]['all'] = ['gameplay:LF1']
        self.assert_rejected(bad_domain)

    def test_unknown_wrapper_or_wrong_schema_rejected(self):
        good = wrapper(synthetic())
        for raw in (good + b'\x48\x00', b'\x08\x05' + good, b'\x08\x03' + good[2:], b'', b'\x08\x05\x42\x80'):
            with self.subTest(raw=raw[:8]), self.assertRaises(ValueError):
                codec.decode_profile(raw, CONTEXT)

    def test_reserved_counts_references_and_unused_unions_rejected(self):
        body = synthetic()
        source_start = 600 + body[10] * 3 + struct.unpack_from('<H', body, 92)[0] * 2
        binding_start = source_start + body[12] * 9 + body[13] * 4
        effect_start = binding_start + body[14] * 6
        changes = [(94, 1), (95, 1), (10, 97), (11, body[10] + 1), (12, 9),
                   (13, 33), (14, 33), (15, 17), (16, 28), (17, 0), (18, 9), (19, 8),
                   (600, 2), (602, 128), (source_start, 2),
                   (binding_start + 4, 28), (binding_start + 5, 1),
                   (effect_start + 7, 5), (effect_start + 8, 1),
                   (effect_start + 28, 28), (effect_start + 29, 4),
                   (effect_start + 30, 1), (effect_start + 31, 1)]
        for offset, value in changes:
            with self.subTest(offset=offset):
                broken = bytearray(body)
                broken[offset] = value
                with self.assertRaises(ValueError):
                    self.decode(broken)

    def test_unknown_semantics_and_boolean_integer_rejected(self):
        profile = self.decode()
        for key, value in [('unknownSemantic', 'invented'), ('formatVersion', True), ('formatVersion', 1)]:
            broken = copy.deepcopy(profile)
            broken[key] = value
            self.assert_rejected(broken)
        name = next(iter(profile['tables']))
        for coordinate in ([256, 0], [-1, 0], [True, 0], [0.5, 0], [0], [0, 0, 0]):
            broken = copy.deepcopy(profile)
            broken['tables'][name]['directions']['5'] = coordinate
            self.assert_rejected(broken)
        broken = copy.deepcopy(profile)
        del broken['tables'][name]['directions']['9']
        self.assert_rejected(broken)
        broken = copy.deepcopy(profile)
        del broken['tables'][name]['id']
        self.assert_rejected(broken)
        broken = copy.deepcopy(profile)
        names = list(broken['tables'])
        broken['tables'][names[1]]['id'] = broken['tables'][names[0]]['id']
        self.assert_rejected(broken)

    def test_malformed_preprocessing_rejected(self):
        for context in ({}, {'modeId': 'MODE_MELEE'}, {'modeId': 'MODE_ULTIMATE', 'surprise': 1},
                        {'modeId': 'MODE_ULTIMATE', 'buttonRemapping': [{'physicalButton': 'BTN_INVALID'}]},
                        {'modeId': 'MODE_ULTIMATE', 'socdPairs': [{'buttonDir1': 'BTN_LF1', 'buttonDir2': 'BTN_LF2', 'socdType': 'BAD'}]}):
            with self.subTest(context=context), self.assertRaises(ValueError):
                codec.decode_profile(wrapper(synthetic()), context)

    def test_exact_owner_fixture_and_committed_human_profile(self):
        fixture = ROOT / 'tools/fixtures/native_profile_json/Ultimate.pb'
        raw = fixture.read_bytes()
        self.assertEqual(len(raw), 1985)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '30d43278fee3a835ca006f4b5df67963c8e9b11ef059ab3b49329b65c7934c6b')
        from convert_glyph_native_ultimate_profile import raw_fields
        body = next(value for tag, wire, value in raw_fields(raw) if tag == 8)
        self.assertEqual(len(body), 1980)
        self.assertEqual(hashlib.sha256(body).hexdigest(),
                         'ca9985997471f247d2f44ba1290e95197393a6c6bdf80a5e59a357f2d6c3e5ee')
        self.assertEqual(body[28:60].hex(),
                         '3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f')
        context = codec.load_json(fixture.with_name('preprocessing-context.json'))
        decoded = codec.decode_profile(raw, context)
        self.assertEqual(codec.compile_profile(decoded), raw)
        human = codec.load_json(ROOT / 'profiles/ultimate/Ultimate.profile.json')
        self.assertEqual(codec.compile_profile(human), raw)
        self.assertIsInstance(codec.validate_profile(human), dict)

    def test_human_references_priorities_modes_and_capacities_rejected(self):
        original = self.decode()
        mutations = [
            lambda p: p.update(defaultTable='missing'),
            lambda p: p.update(leftStickSource='missing'),
            lambda p: p['gates'].update(mode='finalDigital:buttonA'),
            lambda p: p['conditions'][0].update(all=['condition:' + p['conditions'][0]['name']]),
            lambda p: p['conditions'][0].update(all=['condition:' + p['conditions'][-1]['name']]),
            lambda p: p['conditions'][0].update(all=['direction:leftStickLeft']),
            lambda p: p['conditions'][0].update(any=['original:LF1'] * 5),
            lambda p: p['conditions'][0].update(none=['original:LF1'] * 10),
            lambda p: p['conditions'][0].update(all=['original:LF1'] * 3),
            lambda p: p['tableRules'][1].update(priority=p['tableRules'][0]['priority']),
            lambda p: p['tableRules'][0].update(when='condition:missing'),
            lambda p: p['digitalBindings'][0].update(winnerTable='missing'),
            lambda p: p['digitalBindings'][0].update(outputs=['unknown']),
            lambda p: p['digitalBindings'][0].update(when='finalDigital:buttonA'),
            lambda p: p['analogEffects'][1].update(target=p['analogEffects'][0]['target'], priority=p['analogEffects'][0]['priority']),
            lambda p: p['analogEffects'][0].update(winnerTable='missing'),
            lambda p: p['analogEffects'][0]['coordinates'].update(mode='unknown'),
            lambda p: p['analogEffects'][0].update(target='triggerL'),
            lambda p: p['digitalPostMask'].update(set=['buttonA'], clear=['buttonA']),
            lambda p: p['preprocessing'].update(mode='MODE_MELEE'),
            lambda p: p['preprocessing'].update(remaps=[{'physical': 'LF1', 'activates': 'bad'}]),
            lambda p: p['directionSources'].extend([copy.deepcopy(p['directionSources'][0])]),
            lambda p: p['conditions'].extend([copy.deepcopy(p['conditions'][0])] * 94),
            lambda p: p['tableRules'].extend([copy.deepcopy(p['tableRules'][0])] * 31),
            lambda p: p['digitalBindings'].extend([copy.deepcopy(p['digitalBindings'][0])] * 31),
            lambda p: p['analogEffects'].extend([copy.deepcopy(p['analogEffects'][0])] * 10),
        ]
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index):
                profile = copy.deepcopy(original)
                mutation(profile)
                self.assert_rejected(profile)

    def test_standard_json_schema_validation(self):
        import jsonschema
        schema = codec.load_json(ROOT / 'profiles/ultimate/Ultimate.profile.schema.json')
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema)
        for profile in (self.decode(), self.decode(synthetic(boundary=True)),
                        codec.load_json(ROOT / 'profiles/ultimate/Ultimate.profile.json')):
            validator.validate(profile)
        invalid = self.decode()
        invalid['tables'][next(iter(invalid['tables']))]['directions']['5'] = [256, 0]
        self.assertTrue(list(validator.iter_errors(invalid)))

    def test_protobuf_json_transport_roundtrip_and_unknown_fields(self):
        body = synthetic()
        data = {'schemaVersion': 5, 'nativePayload': base64.b64encode(body).decode()}
        self.assertEqual(codec.compile_profile(codec.decode_profile(data, CONTEXT)), wrapper(body))
        for bad in (dict(data, unknown=True), dict(data, schemaVersion=True),
                    dict(data, nativePayload='invalid base64'), dict(data, nativePayload=data['nativePayload'] + '=')):
            with self.subTest(bad=tuple(bad)), self.assertRaises(ValueError):
                codec.decode_profile(bad, CONTEXT)

    def test_preprocessing_order_all_policies_and_digest_binding(self):
        human = {'mode': 'MODE_ULTIMATE',
                 'remaps': [{'physical': 'LF1', 'activates': 'none'},
                            {'physical': 'RF16', 'activates': 'MB12'}],
                 'socd': [{'first': 'LF3', 'second': 'LF1', 'policy': policy} for policy in
                          ('unspecified', 'neutral', 'secondInputPriority',
                           'secondInputPriorityNoReactivation', 'firstPriority', 'secondPriority')]}
        remaps = [SimpleNamespace(physical_button=1, activates=0), SimpleNamespace(physical_button=32, activates=60)]
        pairs = [SimpleNamespace(button_dir1=3, button_dir2=1, socd_type=i) for i in range(6)]
        canonical = preprocessing_bytes(SimpleNamespace(mode_id=3, button_remapping=remaps, socd_pairs=pairs),
                                        SimpleNamespace(MODE_ULTIMATE=3))
        body = bytearray(synthetic())
        body[28:60] = hashlib.sha256(canonical).digest()
        decoded = codec.decode_profile(wrapper(body), human)
        self.assertEqual(decoded['preprocessing'], human)
        self.assertEqual(codec.compile_profile(decoded), wrapper(body))
        reordered = copy.deepcopy(human)
        reordered['remaps'].reverse()
        with self.assertRaises(ValueError):
            codec.decode_profile(wrapper(body), reordered)
        reordered = copy.deepcopy(human)
        reordered['socd'].reverse()
        with self.assertRaises(ValueError):
            codec.decode_profile(wrapper(body), reordered)

    def test_minimal_finite_program_roundtrip(self):
        original = synthetic()
        header = bytearray(original[:96])
        header[10:20] = bytes([0, 0, 1, 0, 0, 0, 0, 1, 1, 0])
        struct.pack_into('<HHHH', header, 20, 0, 65535, 65535, 0)
        struct.pack_into('<H', header, 92, 0)
        body = header + original[96:600] + struct.pack('<BHHHH', 1, 0, 0, 0, 0) + struct.pack('<HHHH', 65535, 0, 0, 0)
        struct.pack_into('<H', body, 8, len(body))
        self.assertEqual(len(body), 617)
        validate_native_body(bytes(body))
        self.assertEqual(codec.compile_profile(self.decode(body)), wrapper(body))

    def test_profile_name_is_nonsemantic(self):
        profile = self.decode()
        raw = codec.compile_profile(profile)
        profile['name'] = 'Renamed profile'
        self.assertEqual(codec.compile_profile(profile), raw)

    def test_read_export_snake_and_camel_envelopes_are_offline_only(self):
        body = synthetic()
        payload = base64.b64encode(body).decode()
        snake = {'schema_version': 5, 'native_payload': payload}
        camel = {'schemaVersion': 5, 'nativePayload': payload}
        response = {'protocol_version': 1, 'request_token': '9007199254740993',
                    'status': 'PROFILE_STORE_OK', 'store_generation': '18446744073709551615',
                    'profile_id': 27, 'profile_revision': '2', 'profile': snake,
                    'config_generation': '3', 'mutation_protocol_version': 1,
                    'store_incarnation': 9, 'diagnostic': ''}
        for data in (snake, {'profile': snake}, {'response': response},
                     {'response': {'status': 1, 'requestToken': '42', 'profileId': 27, 'profile': camel}}):
            with self.subTest(envelope=tuple(data)):
                decoded = codec.decode_profile(data, CONTEXT)
                self.assertEqual(codec.compile_profile(decoded), wrapper(body))
                self.assertNotIn('request_token', decoded)
                self.assertNotIn('profile_id', decoded)
        bad_exports = [
            {'profile': snake, 'unknown': 1},
            {'response': response, 'unknown': 1},
            {'response': dict(response, unknown=1)},
            {'response': dict(response, status='PROFILE_STORE_NOT_FOUND')},
            {'response': dict(response, status=True)},
            {'response': dict(response, request_token='18446744073709551616')},
            {'response': dict(response, request_token='01')},
            {'response': dict(response, profile_id=True)},
            {'response': dict(response, requestToken='42')},
            dict(snake, schemaVersion=5),
            dict(snake, nativePayload=payload),
        ]
        for index, data in enumerate(bad_exports):
            with self.subTest(invalid=index), self.assertRaises(ValueError):
                codec.decode_profile(data, CONTEXT)

    def test_optional_metadata_edits_preserve_exact_bytes_and_closed_fields(self):
        original = self.decode()
        raw = codec.compile_profile(original)
        for metadata in ({}, {'description': 'Arbitrary human explanation'},
                         {'notes': ['First note', 'Second note']}, {'character': None},
                         {'description': 'Edited description', 'notes': ['A note'], 'character': 'Example character'}):
            with self.subTest(metadata=metadata):
                profile = copy.deepcopy(original)
                profile['metadata'] = metadata
                self.assertEqual(codec.compile_profile(profile), raw)
                self.assertIsInstance(codec.validate_profile(profile), dict)
                import jsonschema
                jsonschema.Draft202012Validator(codec.load_json(codec.SCHEMA_PATH)).validate(profile)
        for metadata in ({'unknown': 'unrecognized'}, {'description': 1},
                         {'notes': ['valid', 2]}, {'character': False}):
            with self.subTest(invalid_metadata=metadata):
                profile = copy.deepcopy(original)
                profile['metadata'] = metadata
                self.assert_rejected(profile)
        for section in ('preprocessing', 'gates', 'dpad', 'digitalPostMask'):
            with self.subTest(unknown_field_section=section):
                profile = copy.deepcopy(original)
                profile[section]['unknown'] = 'unrecognized'
                self.assert_rejected(profile)

    def test_json_loader_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory(prefix='glyph-json-test-') as directory:
            path = Path(directory) / 'duplicate.json'
            path.write_text('{"formatVersion":0,"formatVersion":0}')
            with self.assertRaises(ValueError):
                codec.load_json(path)


if __name__ == '__main__':
    unittest.main()
