"""Offline tests run the actual v2 Runner; no device enumeration/open/write.

Three current READ responses are raw sealed inputs. Historical JSON serialization
is reconstruction, not a raw historical capture. Uncaptured current records are
explicit fixture doubles; native53 uses known equal native54 source bytes. These
fixtures establish host behavior, never current device payload/activation truth.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('display_v2_executor', HERE / 'executor.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
PB, PACKAGE, GENERATED = e.bindings()
ORIGINAL = Path('/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/display-hardware-results/GLYPH-DISPLAY-9E69188D-HW-v1-20261113')
HISTORICAL = Path('/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/active_profile_display_hardware_20261025T172604Z/final-preservation')
PHASEB = Path('/Users/rasmus.pekkarinen/Personal code/senscope-hardware-evidence/FULLPKG-B2-KAZUYA-MANAGED-C439-PHASE-B-CORRECTED-20261112')


def read_current(name):
    # Exact hashes are sealed in test-inputs.json by the preparation step.
    path = ORIGINAL / name
    manifest = json.loads((HERE / 'test-inputs.json').read_text())
    expected = manifest['files'][str(path)]
    data = path.read_bytes()
    assert e.digest(data) == expected['sha256'] and len(data) == expected['bytes']
    return data


CONFIG = read_current('pre_snapshot/Config.body')
PAGES = [read_current(f'pre_snapshot/{n:02d}-LIST-{c}-decoded.bin')[1:]
         for n, c in ((4, 0), (5, 8), (6, 16), (7, 24))]
ENTRIES = [x for raw in PAGES for x in PB.ProfileStoreResponse.FromString(raw).entries]
CAPTURED = {i: read_current(f'pre_snapshot/{n:02d}-READ-{i}-decoded.bin')[1:]
            for n, i in ((8, 1), (9, 3), (10, 4))}
RAW4 = next(v for t, w, v in e.raw_fields(CAPTURED[4]) if t == 9 and w == 2)
STATUS = read_current('pre_snapshot/02-PACKAGE_STATUS-decoded.bin')[1:]


def checked_input(path):
    manifest = json.loads((HERE / 'test-inputs.json').read_text())
    data = path.read_bytes()
    assert e.digest(data) == manifest['files'][str(path)]['sha256']
    return data


NATIVE = PB.ProfileStoreResponse.FromString(e.framing.cobs_decode(
    checked_input(PHASEB / '17-READ-response.cobs'))[1:]).profile.SerializeToString(deterministic=True)
need_native = e.digest(NATIVE) == e.NATIVE53
assert need_native
POLICY = json.loads((HERE / 'packet.json').read_text())


def response_read(entry, token, wrapper):
    r = PB.ProfileStoreResponse(protocol_version=2, request_token=token, status=1,
        store_incarnation=1, store_generation=229, config_generation=1599895773,
        profile_id=entry.profile_id, profile_revision=entry.revision)
    r.profile.ParseFromString(wrapper)
    return r.SerializeToString(deterministic=True)


def identity_wire(token, **changes):
    values = dict(status=0, backend=2, row=3, requested=53, incarnation=1,
                  active=53, revision=1, schema=5,
                  payload=bytes.fromhex(e.digest(e.DOMAIN + NATIVE)))
    values.update(changes)
    return e.identity.MAGIC + struct.pack('<BBHQBBHIIIII', 1, 2, 72, token,
        values['status'], values['backend'], values['row'], values['requested'],
        values['incarnation'], values['active'], values['revision'], values['schema']) + values['payload']


class FakePort:
    def __init__(self, io):
        self.io, self.queue, self.opened = io, bytearray(), False

    @property
    def in_waiting(self):
        return len(self.queue)

    def open(self):
        self.io.opens += 1
        self.opened = True

    def close(self):
        self.io.closes += 1
        self.opened = False
        if self.io.fault == 'close':
            raise OSError('synthetic close error')

    def read(self, n):
        self.io.now += 0.05 if self.queue else 1
        n = min(n, self.io.chunk)
        data = bytes(self.queue[:n])
        del self.queue[:n]
        return data

    def write(self, data):
        self.io.writes.append((self.io.stage, data))
        if self.io.fault == 'cancel':
            raise KeyboardInterrupt('synthetic cancellation')
        if self.io.fault == 'partial_write':
            return len(data) - 1
        if self.io.fault == 'timeout':
            return len(data)
        if 'xinput' in self.io.stage:
            token = int.from_bytes(data[8:16], 'little')
            wire = identity_wire(token)
            if self.io.fault == 'wrong_runtime':
                wire = identity_wire(token, row=1, requested=27, active=27)
            if self.io.fault == 'runtime_digest':
                wire = identity_wire(token, payload=b'x' * 32)
            if self.io.fault == 'identity_token':
                wire = identity_wire(token + 1)
            if self.io.fault == 'duplicate_identity':
                wire += wire
            if self.io.fault == 'bad_viewer':
                wire = b'unknown' + wire
            if self.io.viewer:
                wire = b'0' * 24 + b'\n' + wire + b'1' * 24 + b'\n'
            self.queue.extend(wire)
            return len(data)
        raw = e.framing.cobs_decode(data)
        command, payload = raw[0], raw[1:]
        request = PB.ProfileStoreRequest.FromString(payload) if command == 9 else None
        if command == 10:
            token = int.from_bytes(payload[8:16], 'little')
            reply = bytes([10]) + identity_wire(token, status=2, backend=8, row=0,
                requested=0, incarnation=0, active=0, revision=0, schema=0, payload=bytes(32))
        elif command == 3:
            reply = bytes([4]) + (CONFIG + b'\x80\x08\x01' if self.io.fault == 'Config_change' else CONFIG)
        elif request.protocol_version == 3:
            assert request.operation == 1
            r = PACKAGE.PackageResponse.FromString(STATUS)
            r.request_token = request.request_token
            if self.io.fault == 'recovery':
                r.write_fenced = True
            reply = bytes([9]) + r.SerializeToString(deterministic=True)
        elif request.operation == 2:
            assert request.page_size == 8
            r = PB.ProfileStoreResponse.FromString(PAGES[request.page_cursor // 8])
            r.request_token = request.request_token
            if self.io.fault == 'directory_change' and request.page_cursor == 0:
                r.entries[2].payload_version = 2
            reply = bytes([9]) + r.SerializeToString(deterministic=True)
        else:
            assert request.protocol_version == 2 and request.operation == 3
            entry = next(x for x in ENTRIES if x.profile_id == request.profile_id)
            # Current raw1/3/4; native exact source bytes; other legacy slots are
            # explicit valid legacy doubles, not claimed current device READs.
            wrapper = NATIVE if entry.payload_version == 5 else RAW4
            if entry.profile_id in CAPTURED:
                wrapper = next(v for t, w, v in e.raw_fields(CAPTURED[entry.profile_id]) if t == 9 and w == 2)
            if self.io.stage == 'post_snapshot' and self.io.fault in ('payload_change', 'payload_schema_change') and entry.profile_id == 4:
                p = PB.UltimateProfile.FromString(wrapper)
                c = p.tables[0].coordinates[0]
                c.x = (c.x + 1) % 256
                if self.io.fault == 'payload_schema_change':
                    old = p
                    p = PB.UltimateProfile(schema_version=1); p.tables.extend(old.tables)
                wrapper = p.SerializeToString(deterministic=True)
            if self.io.fault == 'native53_change' and entry.profile_id == 53:
                p = PB.UltimateProfile.FromString(wrapper)
                b = bytearray(p.native_payload); b[100] ^= 1; p.native_payload = bytes(b)
                wrapper = p.SerializeToString(deterministic=True)
            r = PB.ProfileStoreResponse.FromString(response_read(entry, request.request_token, wrapper))
            if entry.profile_id == 4:
                if self.io.fault == 'wrong_id':
                    r.profile_id = 999
                if self.io.fault == 'wrong_revision':
                    r.profile_revision += 1
                if self.io.fault == 'READ_token':
                    r.request_token += 1
                if self.io.fault == 'READ_error':
                    r.status = 8
                if self.io.fault == 'READ_recovery':
                    r.profile_health = 2
                if self.io.fault == 'unsupported':
                    r.profile.schema_version = 4
                if self.io.fault == 'cross_family':
                    r.profile.ParseFromString(NATIVE)
                if self.io.fault == 'bad_legacy':
                    r.profile.ClearField('tables')
            reply = bytes([9]) + r.SerializeToString(deterministic=True)
        if self.io.fault == 'empty_frame':
            self.queue.extend(b'\0')
        elif self.io.fault == 'duplicate_frame':
            b = e.framing.cobs_encode(reply); self.queue.extend(b + b)
        elif self.io.fault == 'malformed_COBS':
            self.queue.extend(b'\x05\x01\0')
        else:
            self.queue.extend(e.framing.cobs_encode(reply))
        return len(data)


class FakeIO:
    def __init__(self):
        self.now, self.nonce, self.opens, self.closes = 0, 100, 0, 0
        self.writes, self.stage, self.fault = [], '', None
        self.chunk, self.viewer = 9000, False
        path = Path(POLICY['target']['private_identity_record'])
        self.serial = json.loads(path.read_text())['serial_number']
        self.bad_unit, self.competitor, self.owned = False, False, False

    def clock(self):
        self.now += 0.001
        return self.now

    def token(self):
        self.nonce += 1
        return self.nonce

    def ports(self):
        xinput = 'xinput' in self.stage
        r = dict(device='/dev/cu.FAKE_NO_DEVICE', vid=0x0738 if xinput else 0x2e8a,
                 pid=0x4726 if xinput else 0x000a, serial='wrong' if self.bad_unit else self.serial)
        return [r, dict(r)] if self.competitor else [r]

    def unowned(self, name):
        return not self.owned

    def port(self, name):
        return FakePort(self)


def owner_event(stage):
    common = {'owner_present': True, 'owner_message_reference': 'SYNTHETIC_TEST_ONLY',
        'ready': True, 'exclusive': True, 'same_unit_no_change': True,
        'prior_firmware_c439_no_change': True,
        'route': 'normal_no_buttons_USB_default' if 'xinput' in stage else 'menu'}
    if stage == 'install':
        common.update(source_sha=POLICY['built_source_sha'], uf2_sha256=POLICY['artifacts']['firmware.uf2']['sha256'],
            uf2_bytes=1296896, manual_install_count=1, one_same_unit_bootloader=True,
            copy_result='confirmed_success', reenumeration='unambiguous', fresh_volume_path='/FAKE/volume')
    common.update(dashboard_name='KazTest5', plate='Unknown Plate', backend='XInput', responsive=True,
                  viewer_name='KazTest5', returned_dashboard=True)
    return common


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='glyph-display-v2-tests-')
        self.c = Path(self.temp.name)
        self.io = FakeIO()
        self.runner = e.Runner(POLICY, self.c, PB, PACKAGE, self.io)
        # Any accidental real IO would fail before enumeration/open.
        self.guard = patch.object(e.LiveIO, 'ports', side_effect=AssertionError('REAL IO FORBIDDEN'))
        self.guard.start()

    def tearDown(self):
        self.guard.stop(); self.temp.cleanup()

    def execute(self, stage):
        self.io.stage = stage
        return self.runner.execute(stage, owner_event(stage))

    def until(self, last):
        answer = None
        for stage in e.STAGES:
            answer = self.execute(stage)
            if stage == last:
                return answer

    def assert_terminal(self, target, fault):
        self.io.fault = fault
        with self.assertRaises(BaseException):
            self.execute(target)
        self.assertTrue((self.c / 'terminal.json').exists())
        self.assertFalse((self.c / target / 'result.json').exists())
        old_writes = len(self.io.writes)
        with self.assertRaises(ValueError):
            self.execute(target)
        self.assertEqual(len(self.io.writes), old_writes)

    def test_historical_reconstruction_matches_current_raw(self):
        from google.protobuf.json_format import ParseDict
        h = json.loads(checked_input(HISTORICAL / 'read-4.json'))
        profile = PB.UltimateProfile(); ParseDict(h['response']['profile'], profile)
        reconstructed = profile.SerializeToString(deterministic=True)
        self.assertEqual(reconstructed, RAW4)
        self.assertEqual(e.digest(RAW4), 'b8583459651f42bfbb108e4558627ce0a192be89bae229cbb5a74fb0e7dcd8d4')
        listings = json.loads(checked_input(HISTORICAL / 'list-0.json'))
        old = next(x for x in listings['response']['entries'] if int(x['profile_id']) == 4)
        self.assertEqual((int(old['revision']), int(old['payload_version'])), (1, 1))

    def test_actual_captured_read4_admitted_without_relabel(self):
        entry = next(x for x in ENTRIES if x.profile_id == 4)
        original = PB.ProfileStoreResponse.FromString(CAPTURED[4])
        wrapper, facts = e.validate_read(PB, entry, CAPTURED[4], original.request_token)
        self.assertEqual(wrapper, RAW4)
        self.assertEqual((facts['directory_payload_version'], facts['payload_schema_version']), (1, 3))

    def test_complete_seventy_request_workflow(self):
        result = self.until('finish')
        self.assertEqual(result['packet_result'], 'PASS_BOUNDED_LEGACY_DISPLAY_AND_PRESERVATION')
        self.assertEqual((len(self.io.writes), self.io.opens, self.io.closes), (70, 4, 4))
        for name in ('pre_snapshot', 'post_snapshot'):
            record = e.load(self.c / name / 'result.json')
            self.assertEqual(len(record['profiles']), 27)
            self.assertEqual((record['profiles']['4']['directory_payload_version'],
                              record['profiles']['4']['payload_schema_version']), (1, 3))
            self.assertTrue((self.c / name / 'profile-54.pb').exists())
        self.assertEqual((self.c / 'pre_snapshot/directory.bin').read_bytes(),
                         (self.c / 'post_snapshot/directory.bin').read_bytes())
        tokens = [e.load(p)['token'] for p in self.c.glob('*/*-transport.json') if e.load(p)['token']]
        self.assertEqual(len(tokens), len(set(tokens)))
        for name in ('pre_snapshot', 'post_snapshot'):
            requests = [b for stage, b in self.io.writes if stage == name]
            self.assertEqual(len(requests), 34)
            parsed = [e.framing.cobs_decode(b) for b in requests]
            self.assertEqual([x[0] for x in parsed[:3]], [10, 9, 3])
            ops = [PB.ProfileStoreRequest.FromString(x[1:]).operation for x in parsed[3:]]
            self.assertEqual(ops, [2]*4 + [3]*27)

    def test_legacy_supported_version_pairs_are_generic(self):
        entry = copy.deepcopy(next(x for x in ENTRIES if x.profile_id == 4))
        # ID42 demonstrates rule is not an ID4 exception.
        entry.profile_id = 42
        for directory in (1, 2, 3):
            entry.payload_version = directory
            _, facts = e.validate_read(PB, entry, response_read(entry, 123, RAW4), 123)
            self.assertEqual(facts['payload_schema_version'], 3)
            self.assertEqual(facts['directory_payload_version'], directory)

    def test_unsupported_and_family_mismatches(self):
        entry = copy.deepcopy(next(x for x in ENTRIES if x.profile_id == 4))
        for version in (0, 4, 6, 999, 5):
            with self.subTest(directory=version):
                entry.payload_version = version
                with self.assertRaises(ValueError):
                    e.validate_read(PB, entry, response_read(entry, 1, RAW4), 1)
        entry.payload_version = 1
        with self.assertRaises(ValueError):
            e.validate_read(PB, entry, response_read(entry, 1, NATIVE), 1)

    def test_snapshot_validation_failures_terminal(self):
        faults = ('wrong_id', 'wrong_revision', 'READ_token', 'READ_error', 'READ_recovery',
                  'unsupported', 'cross_family', 'bad_legacy', 'native53_change',
                  'directory_change', 'Config_change', 'recovery', 'empty_frame',
                  'duplicate_frame', 'malformed_COBS', 'timeout', 'partial_write', 'cancel', 'close')
        for fault in faults:
            with self.subTest(fault=fault), tempfile.TemporaryDirectory(prefix='glyph-display-negative-') as d:
                self.c = Path(d); self.io = FakeIO(); self.runner = e.Runner(POLICY, self.c, PB, PACKAGE, self.io)
                self.assert_terminal('pre_snapshot', fault)
                self.assertLessEqual(len(self.io.writes), 34)
                self.assertEqual(self.io.opens, 1)
                self.assertEqual(self.io.closes, 1)

    def test_post_payload_byte_change_terminal(self):
        self.until('display')
        self.assert_terminal('post_snapshot', 'payload_change')
        self.assertFalse((self.c / 'final_xinput_boot').exists())

    def test_post_metadata_or_payload_schema_change_terminal(self):
        for fault in ('directory_change', 'payload_schema_change'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory(prefix='glyph-preserve-negative-') as d:
                self.c = Path(d); self.io = FakeIO(); self.runner = e.Runner(POLICY, self.c, PB, PACKAGE, self.io)
                self.until('display')
                self.assert_terminal('post_snapshot', fault)
                self.assertFalse((self.c / 'final_xinput_boot').exists())

    def test_fixed_episode_no_alternative_rearm(self):
        self.assertEqual(e.approved_episode_path(POLICY, POLICY['episode_custody']),
                         Path(POLICY['episode_custody']).resolve())
        for other in (str(self.c / 'another'), str(ORIGINAL)):
            with self.assertRaises(ValueError):e.approved_episode_path(POLICY, other)

    def test_xinput_correspondence_failures_terminal(self):
        for fault in ('wrong_runtime', 'runtime_digest', 'identity_token', 'duplicate_identity', 'bad_viewer'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory(prefix='glyph-xinput-negative-') as d:
                self.c = Path(d); self.io = FakeIO(); self.runner = e.Runner(POLICY, self.c, PB, PACKAGE, self.io)
                self.until('install')
                self.assert_terminal('first_xinput_boot', fault)
                self.assertEqual(len([x for x in self.io.writes if x[0] == 'first_xinput_boot']), 1)

    def test_split_complete_viewer_records_retained(self):
        self.until('install'); self.io.viewer = True; self.io.chunk = 7
        self.execute('first_xinput_boot')
        self.assertEqual(e.load(self.c / 'first_xinput_boot/result.json')['identity']['viewer_records'], 2)

    def test_no_real_io_without_approval(self):
        with self.assertRaises(ValueError):
            e.approve(POLICY, {'approved': True, 'packet_id': 'GLYPH-DISPLAY-9E69188D-HW-v1',
                              'owner_message_reference': 'old'})
        self.assertEqual((self.io.opens, len(self.io.writes)), (0, 0))

    def test_no_unsettled_transition(self):
        (self.c / 'pre_snapshot').mkdir()
        e.save(self.c / 'pre_snapshot', 'result.json', {'result': 'PASS'})
        with self.assertRaises((ValueError, FileNotFoundError)):
            self.execute('install')
        self.assertEqual(self.io.opens, 0)

    def test_native53_exactness_and_malformed_payload(self):
        entry = copy.deepcopy(next(x for x in ENTRIES if x.profile_id == 53))
        for data in (b'\x80', PB.UltimateProfile(schema_version=4).SerializeToString(),
                     PB.UltimateProfile(schema_version=5, native_payload=b'bad').SerializeToString()):
            response = PB.ProfileStoreResponse(protocol_version=2, request_token=1, status=1,
                       profile_id=53, profile_revision=1)
            # Exact raw field9, including deliberately malformed standalone bytes.
            wire = response.SerializeToString() + bytes([0x4a, len(data)]) + data
            with self.assertRaises(Exception):e.validate_read(PB, entry, wire, 1)
        entry.name = 'Different'
        with self.assertRaises(ValueError):e.validate_read(PB, entry, response_read(entry, 1, NATIVE), 1)

    def test_live_serial_settings_without_open(self):
        import serial
        with patch.object(serial.Serial, 'open', side_effect=AssertionError('REAL OPEN FORBIDDEN')):
            port = e.LiveIO().port('/dev/cu.FAKE_NO_DEVICE')
            self.assertFalse(port.is_open)
            self.assertEqual((port.baudrate, port.bytesize, port.parity, port.stopbits), (115200, 8, 'N', 1))
            self.assertTrue(port.dtr); self.assertFalse(port.rts)
            with patch.object(serial.Serial, '_reset_input_buffer', side_effect=AssertionError('FLUSH FORBIDDEN')):
                port._reset_input_buffer()  # frozen subclass suppresses only destructive reset

    def test_display_observation_failure_terminal(self):
        self.until('first_xinput_boot')
        event = owner_event('display'); event['plate'] = 'incorrect'
        with self.assertRaises(ValueError):self.runner.execute('display', event)
        self.assertTrue((self.c / 'terminal.json').exists())
        self.assertFalse((self.c / 'post_snapshot').exists())

    def test_supported_schema1_payload_with_legacy_metadata(self):
        profile = PB.UltimateProfile(schema_version=1)
        profile.tables.extend(PB.UltimateProfile.FromString(RAW4).tables)
        entry = copy.deepcopy(next(x for x in ENTRIES if x.profile_id == 4))
        entry.profile_id = 42; entry.payload_version = 3
        wrapper = profile.SerializeToString(deterministic=True)
        _, facts = e.validate_read(PB, entry, response_read(entry, 123, wrapper), 123)
        self.assertEqual((facts['directory_payload_version'], facts['payload_schema_version']), (3, 1))

    def test_operation_limit_and_forbidden_commands(self):
        stage = self.c / 'x'; stage.mkdir(); port = FakePort(self.io)
        for cmd, payload in ((4, b'x'), (9, PB.ProfileStoreRequest(protocol_version=2, request_token=1, operation=1).SerializeToString()),
                             (9, PACKAGE.PackageEnvelope(protocol_version=3, request_token=1, operation=15).SerializeToString())):
            with self.assertRaises(ValueError):self.runner.exchange(port, stage, 'IDENTITY', cmd, payload, 1)
        self.assertEqual(len(self.io.writes), 0)
        self.runner.count = 34
        with self.assertRaises(ValueError):self.runner.exchange(port, stage, 'READ', 9, b'', 1)
        self.runner.count = 1
        with self.assertRaises(ValueError):self.runner.exchange(port, stage, 'IDENTITY', None, e.identity.request(1), 1, xinput=True)

    def test_admission_failures_before_open(self):
        for name in ('bad_unit', 'competitor', 'owned'):
            with self.subTest(name=name), tempfile.TemporaryDirectory(prefix='glyph-admit-negative-') as d:
                self.c = Path(d); self.io = FakeIO(); setattr(self.io, name, True)
                self.runner = e.Runner(POLICY, self.c, PB, PACKAGE, self.io)
                with self.assertRaises(ValueError):self.execute('pre_snapshot')
                self.assertTrue((self.c / 'terminal.json').exists())
                self.assertEqual((self.io.opens, len(self.io.writes)), (0, 0))

    def cli_established(self):
        self.c = self.c.resolve()
        e.save(self.c, 'begin-claim.json', {'packet_id': e.PACKET_ID})
        e.save(self.c, 'episode.json', {'packet_id': e.PACKET_ID})
        approval = self.c / 'external-approval.json'
        approval.write_text('{"approved": true}')
        return ['executor.py', 'install', '--episode', str(self.c), '--approval', str(approval)]

    def test_actual_cli_preparation_or_custody_failure_consumes_episode(self):
        for reason in ('preparation changed: reviewed bytes', 'retained artifact changed', 'cancel'):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory(prefix='glyph-cli-negative-') as d:
                self.c = Path(d).resolve(); argv = self.cli_established()
                error = KeyboardInterrupt('cancel') if reason == 'cancel' else ValueError(reason)
                with patch.object(e, 'EPISODE_PATH', self.c), patch.object(e.sys, 'argv', argv), \
                     patch.object(e, 'verify_preparation', side_effect=error):
                    with self.assertRaises(BaseException):e.main()
                self.assertTrue((self.c / 'terminal.json').exists())
                self.assertFalse((self.c / 'install').exists())
                # Restored valid preflight must never be reached after terminal.
                with patch.object(e, 'EPISODE_PATH', self.c), patch.object(e.sys, 'argv', argv), \
                     patch.object(e, 'verify_preparation', return_value=(POLICY, PB, PACKAGE)) as restored:
                    with self.assertRaises(ValueError):e.main()
                    restored.assert_not_called()

    def test_actual_cli_approval_or_episode_binding_failure_terminal(self):
        for mode in ('approval', 'episode', 'corrupt_approval', 'corrupt_episode'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix='glyph-cli-bind-negative-') as d:
                self.c = Path(d).resolve(); argv = self.cli_established()
                policy = copy.deepcopy(POLICY); policy['episode_custody'] = str(self.c)
                if mode.startswith('corrupt_'):
                    (self.c / ('external-approval.json' if mode == 'corrupt_approval' else 'episode.json')).write_text('{')
                approval_error = ValueError('approval mismatch') if mode == 'approval' else None
                with patch.object(e, 'EPISODE_PATH', self.c), patch.object(e.sys, 'argv', argv), \
                     patch.object(e, 'verify_preparation', return_value=(policy, PB, PACKAGE)), \
                     patch.object(e, 'approve', side_effect=approval_error):
                    with self.assertRaises((ValueError, KeyError)):e.main()
                self.assertTrue((self.c / 'terminal.json').exists())
                self.assertFalse((self.c / 'install').exists())

    def test_actual_cli_check_failure_after_begin_is_terminal(self):
        self.cli_established()
        with patch.object(e, 'EPISODE_PATH', self.c), patch.object(e.sys, 'argv', ['executor.py', 'check']), \
             patch.object(e, 'verify_preparation', side_effect=ValueError('custody unavailable')):
            with self.assertRaises(ValueError):e.main()
        self.assertTrue((self.c / 'terminal.json').exists())

    def test_owner_install_or_visual_uncertainty_terminal(self):
        self.execute('pre_snapshot')
        event = owner_event('install'); event['copy_result'] = 'unknown'
        with self.assertRaises(ValueError):self.runner.execute('install', event)
        self.assertTrue((self.c / 'terminal.json').exists())
        self.assertFalse((self.c / 'first_xinput_boot').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
