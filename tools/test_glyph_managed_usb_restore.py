#!/usr/bin/env python3
"""Offline tests of the actual bounded operator using external private evidence.

No private controller payloads are committed. Every serial open is replaced;
tests exercise the real Connection constructor, framing and decoder.
"""
import argparse
import base64
import copy
import datetime as dt
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import glyph_managed_usb_restore as op


class FakeSerial:
    def __init__(self, owner, **kwargs):
        self.owner = owner
        owner.constructor = kwargs
        self.queue = bytearray()
        self.is_open = False

    def open(self):
        self.is_open = True
        self.owner.opens += 1
        self.owner.lines = (self.dtr, self.rts, self.port)

    def close(self):
        self.is_open = False

    @property
    def in_waiting(self):
        return len(self.queue)

    def write(self, frame):
        raw = op.config_tool.cobs_decode(frame)
        self.owner.commands.append(raw[0])
        command, body = raw[0], raw[1:]
        if command == 1:
            reply = b'\x02' + (b'wrong-build' if self.owner.mode == 'firmware' else op.DEVICE_INFO)
        elif command == 9:
            req = self.owner.pb.ProfileStoreRequest()
            req.ParseFromString(body)
            result = self.owner.pb.ProfileStoreResponse(protocol_version=req.protocol_version, request_token=req.request_token,
                      status=self.owner.pb.PROFILE_STORE_OK, mutation_protocol_version=2,
                      mutation_feasible=True, store_generation=230, store_incarnation=1,
                      transaction_token_high_water=17293822569102712134,
                      config_generation=zlib.crc32(self.owner.current))
            if self.owner.mode == 'incarnation': result.store_incarnation = 2
            if self.owner.mode == 'generation': result.store_generation = 231
            if self.owner.mode == 'highwater': result.transaction_token_high_water += 1
            if self.owner.mode == 'recovery': result.recovery_flags = 1 << 19
            if self.owner.mode == 'fenced': result.recovery_flags = 1 << 21
            if self.owner.mode == 'unresolved': result.recovery_flags = 1 << 30
            if self.owner.mode == 'admission': result.mutation_feasible = False
            if self.owner.mode == 'status-token': result.request_token += 1
            reply = b'\x09' + result.SerializeToString(deterministic=True)
        elif command == 3:
            self.owner.gets += 1
            payload = self.owner.current
            if self.owner.mode == 'stale-config' and self.owner.gets == 1: payload += b'\x00'
            if self.owner.mode == 'readback' and self.owner.sets: payload = self.owner.original_current
            reply = b'\x04' + payload
        elif command == 4:
            self.owner.sets += 1
            assert self.owner.sets == 1, 'second mutation is forbidden'
            assert body == self.owner.target
            self.owner.current = body
            if self.owner.mode == 'partial-write': return len(frame)-1
            if self.owner.mode == 'missing-ack': return len(frame)
            if self.owner.mode == 'partial-ack':
                self.queue.extend(b'\x02\x06')
                return len(frame)
            if self.owner.mode == 'error-ack': reply = b'\x05save failed'
            elif self.owner.mode == 'ack-payload': reply = b'\x06unexpected'
            elif self.owner.mode == 'double-ack':
                self.queue.extend(op.config_tool.cobs_encode(b'\x06')*2)
                return len(frame)
            else: reply = b'\x06'
        else:
            raise AssertionError('unapproved command')
        self.queue.extend(op.config_tool.cobs_encode(reply))
        return len(frame)

    def read(self, count):
        count = min(count, len(self.queue), 13)  # fragmented real decoder path
        data = bytes(self.queue[:count])
        del self.queue[:count]
        return data


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='glyph-usb-restore-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.snapshot = self.root/'snapshot'
        shutil.copytree(ARGS.snapshot, self.snapshot)
        self.ledger = self.root/'ledger'
        self.ledger.mkdir()
        self.pb = PB
        self.current = self.original_current = (self.snapshot/'config.pb').read_bytes()
        self.target = ARGS.xinput_baseline.read_bytes()
        self.out = self.root/'episode'
        self.plan = op.prepare(self.snapshot, ARGS.xinput_baseline, self.ledger, self.out, PB)
        self.path = self.out/'plan.json'
        self.approval = self.root/'approval.json'
        self.mode = 'success'
        self.opens = self.gets = self.sets = 0
        self.commands = []
        self.serial = None
        self.approve()
        self.tick = 0.0

    def approve(self, **changes):
        now = dt.datetime.now(dt.timezone.utc)
        value = dict(approved=True, planSha256=op.sha(self.path.read_bytes()), frameSha256=self.plan['frameSha256'],
                     port=self.plan['port'], usbSerial=self.plan['usbSerial'], approvedAtUtc=now.isoformat(),
                     expiresAtUtc=(now+dt.timedelta(minutes=10)).isoformat(), exclusiveConfiguratorSession=True,
                     ownerReference='OFFLINE FAKE SERIAL TEST ONLY')
        value.update(changes)
        self.approval.write_bytes(op.json_bytes(value))

    def change_plan(self, edit):
        value = op.read_json(self.path)
        edit(value)
        self.path.chmod(0o600)
        self.path.write_bytes(op.json_bytes(value))
        self.plan = value
        self.approve()

    def clock(self):
        self.tick += 0.1
        return self.tick

    def run_operator(self, endpoint=None):
        endpoint = endpoint or types.SimpleNamespace(vid=0x2e8a, pid=10, device=self.plan['port'], serial_number=self.plan['usbSerial'])
        def factory(**kwargs):
            self.serial = FakeSerial(self, **kwargs)
            return self.serial
        with patch('serial.Serial', factory), patch('serial.tools.list_ports.comports', return_value=[endpoint]), patch.object(op.time, 'monotonic', self.clock):
            return op.execute(self.path, self.approval, ARGS.uf2, True, PB)

    def rejected(self, expected_sets=0):
        with self.assertRaises((ValueError, FileExistsError, TimeoutError, op.config_tool.ToolError)):
            self.run_operator()
        self.assertEqual(self.sets, expected_sets)
        if self.serial: self.assertFalse(self.serial.is_open)

    def test_exact_pair_and_success(self):
        result = self.run_operator()
        self.assertEqual(result['configSha256'], op.TARGET)
        self.assertEqual(self.current, self.target)
        self.assertEqual(self.sets, 1)
        self.assertEqual(self.commands, [1, 9, 9, 3, 4, 3, 9, 9])
        self.assertEqual(self.constructor, dict(port=None, baudrate=115200, timeout=0.05, write_timeout=1, exclusive=True))
        self.assertEqual(self.lines, (True, False, self.plan['port']))
        self.assertFalse(self.serial.is_open)
        self.assertEqual(len(list((self.out/'execution').glob('*.request'))), 8)

    def test_current_hash(self):
        self.change_plan(lambda p: p.update(currentSha256='0'*64))
        self.rejected()

    def test_unexpected_root(self):
        cfg = PB.Config(); cfg.ParseFromString(self.original_current); cfg.ultimate_profile_root_format = 2
        raw = cfg.SerializeToString(deterministic=True)
        with patch.object(op, 'CURRENT', op.sha(raw)):
            with self.assertRaisesRegex(ValueError, 'managed root'):
                op.exact_payload(raw, self.target, PB)

    def test_wrong_backend_index(self):
        cfg = PB.Config(); cfg.ParseFromString(self.original_current); cfg.default_usb_backend_config = 3
        raw = cfg.SerializeToString(deterministic=True)
        with patch.object(op, 'CURRENT', op.sha(raw)):
            with self.assertRaisesRegex(ValueError, 'selector indices'):
                op.exact_payload(raw, self.target, PB)

    def test_wrong_backend_identity(self):
        cfg = PB.Config(); cfg.ParseFromString(self.original_current); cfg.communication_backend_configs[3].backend_id = 4
        raw = cfg.SerializeToString(deterministic=True)
        with patch.object(op, 'CURRENT', op.sha(raw)):
            with self.assertRaisesRegex(ValueError, 'backend indices'):
                op.exact_payload(raw, self.target, PB)

    def test_nonselector_difference(self):
        cfg = PB.Config(); cfg.ParseFromString(self.target); cfg.rgb_brightness ^= 1
        raw = cfg.SerializeToString(deterministic=True)
        with patch.object(op, 'TARGET', op.sha(raw)):
            with self.assertRaisesRegex(ValueError, 'non-selector'):
                op.exact_payload(self.original_current, raw, PB)

    def test_wrong_firmware_plan(self):
        self.change_plan(lambda p: p.update(source='wrong'))
        self.rejected()

    def test_wrong_controller(self):
        endpoint = types.SimpleNamespace(vid=0x2e8a, pid=10, device=self.plan['port'], serial_number='other')
        with self.assertRaisesRegex(ValueError, 'controller'):
            self.run_operator(endpoint)
        self.assertEqual(self.opens, 0)

    def test_wrong_port(self):
        endpoint = types.SimpleNamespace(vid=0x2e8a, pid=10, device='/dev/cu.other', serial_number=self.plan['usbSerial'])
        with self.assertRaisesRegex(ValueError, 'endpoint'):
            self.run_operator(endpoint)
        self.assertEqual(self.opens, 0)

    def test_stale_approval(self):
        self.approve(planSha256='0'*64)
        self.rejected()

    def test_expired_approval(self):
        now=dt.datetime.now(dt.timezone.utc)
        self.approve(approvedAtUtc=(now-dt.timedelta(minutes=15)).isoformat(), expiresAtUtc=(now-dt.timedelta(minutes=1)).isoformat())
        self.rejected()

    def test_tooling_drift(self):
        self.change_plan(lambda p: p['tooling'].update({'schema/haybox/config.proto': '0'*64}))
        self.rejected()

    def test_duplicate_after_success(self):
        self.run_operator()
        before=self.opens
        self.rejected(expected_sets=1)
        self.assertEqual(self.opens,before)

    def test_claim_survives_new_episode_and_approval(self):
        self.mode='missing-ack';self.rejected(expected_sets=1)
        new=self.root/'new-episode'
        self.plan=op.prepare(self.snapshot, ARGS.xinput_baseline, self.ledger, new, PB)
        self.out=new;self.path=new/'plan.json';self.approve()
        before=self.opens;self.rejected(expected_sets=1);self.assertEqual(self.opens,before)



def live_guard_case(mode):
    def test(self):
        self.mode=mode
        self.rejected()
        self.assertEqual(self.opens,1)
        self.assertTrue((self.out/'execution/terminal.json').exists())
    return test


def uncertain_case(mode):
    def test(self):
        self.mode=mode
        self.rejected(expected_sets=1)
        before=self.opens
        self.rejected(expected_sets=1)
        self.assertEqual(self.opens,before)
        terminal=op.read_json(self.out/'execution/terminal.json')
        self.assertTrue(terminal['retryForbidden'])
        self.assertTrue(terminal['setMayHaveBeenAttempted'])
    return test


for mode in ['firmware','incarnation','generation','highwater','recovery','fenced','unresolved','admission','status-token','stale-config']:
    setattr(RestoreTests,'test_live_'+mode.replace('-','_'),live_guard_case(mode))
for mode in ['partial-write','missing-ack','partial-ack','error-ack','ack-payload','double-ack','readback']:
    setattr(RestoreTests,'test_uncertain_'+mode.replace('-','_'),uncertain_case(mode))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',type=Path,required=True)
    parser.add_argument('--xinput-baseline',type=Path,required=True)
    parser.add_argument('--uf2',type=Path,required=True)
    ARGS=parser.parse_args()
    PB,_,_=op.config_tool.load_runtime_proto_modules(op.ROOT)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RestoreTests))
    sys.exit(not result.wasSuccessful())
