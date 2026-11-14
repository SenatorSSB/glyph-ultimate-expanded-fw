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
import glyph_switch_recovery as op


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
                      mutation_feasible=True, store_generation=234, store_incarnation=1,
                      transaction_token_high_water=17293822569102712138,
                      config_generation=zlib.crc32(self.owner.current))
            if self.owner.mode == 'incarnation': result.store_incarnation = 2
            if self.owner.mode == 'generation': result.store_generation = 235
            if self.owner.mode == 'highwater': result.transaction_token_high_water += 1
            if self.owner.mode == 'recovery': result.recovery_flags = 1 << 19
            if self.owner.mode == 'fenced': result.recovery_flags = 1 << 21
            if self.owner.mode == 'unresolved': result.recovery_flags = 1 << 30
            if self.owner.mode == 'admission': result.mutation_feasible = False
            if self.owner.mode == 'status-token': result.request_token += 1
            if req.operation == self.owner.pb.PROFILE_STORE_LIST:
                entries = self.owner.baseline_entries[req.page_cursor:req.page_cursor+req.page_size]
                result.next_page_cursor = req.page_cursor + len(entries) if req.page_cursor + len(entries) < 27 else 0
                for e in entries:
                    item = result.entries.add(profile_id=e['id'], revision=int(e['revision']), name=e['name'],
                                              display_rank=e['rank'], payload_version=e['directorySchema'])
                if self.owner.mode == 'directory' or (self.owner.mode == 'post-directory' and self.owner.sets):
                    result.entries[0].name += 'changed'
                if self.owner.mode == 'pagination': result.next_page_cursor = 0
            if req.operation == self.owner.pb.PROFILE_STORE_READ:
                e = next(e for e in self.owner.baseline_entries if e['id'] == req.profile_id)
                result.profile_id = e['id']; result.profile_revision = int(e['revision']); result.profile_health = 0
                result.profile.ParseFromString(self.owner.wrappers[e['id']])
                if self.owner.mode == 'wrapper' or (self.owner.mode == 'post-wrapper' and self.owner.sets):
                    result.profile.schema_version += 1
                if self.owner.mode == 'read-health': result.profile_health = 2
                if self.owner.mode == 'read-id': result.profile_id += 100
            if self.owner.mode == 'recorded' and req.operation in (2, 3):
                key = (req.operation, req.page_cursor if req.operation == 2 else req.profile_id)
                result.ParseFromString(self.owner.recorded[key])
                result.request_token = req.request_token
                result.config_generation = zlib.crc32(self.owner.current)
            if req.protocol_version == 4:
                _, response_type = op.load_package_schema()
                package = response_type(protocol_version=4, request_token=result.request_token, status=result.status,
                    store_generation=result.store_generation, store_incarnation=result.store_incarnation,
                    transaction_token_high_water=result.transaction_token_high_water, config_generation=result.config_generation,
                    storage_floor=2)
                if self.owner.mode == 'package-fenced': package.write_fenced = True
                if self.owner.mode == 'package-floor': package.storage_floor = 3
                if self.owner.mode == 'package-unresolved': package.logical = 4
                if self.owner.mode == 'package-incomplete': package.logical = 2
                if self.owner.mode == 'package-unknown': package.logical = 99
                if self.owner.mode == 'package-floor-zero': package.storage_floor = 0
                if self.owner.mode == 'recorded':
                    package.ParseFromString(self.owner.recorded_status)
                    package.request_token = req.request_token
                    package.config_generation = zlib.crc32(self.owner.current)
                result = package
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
        self.root = Path(self.tmp.name).resolve()
        self.snapshot = self.root/'snapshot'
        shutil.copytree(ARGS.snapshot, self.snapshot)
        self.ledger = self.root/'ledger'
        self.ledger.mkdir()
        self.pb = PB
        cfg = PB.Config.FromString((self.snapshot/'config.pb').read_bytes())
        self.target = cfg.SerializeToString(deterministic=True)
        cfg.default_usb_backend_config = 4
        self.current = self.original_current = cfg.SerializeToString(deterministic=True)
        (self.snapshot/'config.pb').write_bytes(self.current)
        saved = op.read_json(self.snapshot/'snapshot.json')
        saved.update(source=op.SOURCE, uf2=op.UF2, observation='complete read-only candidate capture', selector=4, observedAtUtc=op.timestamp())
        saved['store'].update(configSha=op.CURRENT, configCrc=zlib.crc32(self.current))
        (self.snapshot/'snapshot.json').write_bytes(op.json_bytes(saved))
        self.baseline_entries = saved['entries']
        self.wrappers = {e['id']:(self.snapshot/e['wrapperFile']).read_bytes() for e in self.baseline_entries}
        # Test-only ledger substitute; production path/hashes remain hard pinned.
        self.historical = self.ledger/'historical.claim'
        self.historical.write_bytes(b'prior claim preserved')
        pins = dict(op.PINS, ledger=str(self.ledger), ledgerFiles={'historical.claim':op.sha(self.historical.read_bytes())})
        self.pin_patch = patch.object(op, 'PINS', pins); self.pin_patch.start(); self.addCleanup(self.pin_patch.stop)
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
        self.recorded = {}
        for response in self.snapshot.glob('*.response'):
            request = response.with_suffix('.request')
            if not request.exists(): continue
            query = op.config_tool.cobs_decode(request.read_bytes())
            if query[0] != 9: continue
            req = PB.ProfileStoreRequest.FromString(query[1:])
            if req.protocol_version == 4 and req.operation == 1:
                self.recorded_status = op.config_tool.cobs_decode(response.read_bytes())[1:]
            if req.operation in (2, 3):
                key = (req.operation, req.page_cursor if req.operation == 2 else req.profile_id)
                reply = op.config_tool.cobs_decode(response.read_bytes())
                self.recorded[key] = reply[1:]

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
        self.tick += 0.001
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
        self.assertEqual(self.commands.count(4), 1)
        self.assertEqual(self.commands.count(9), 78)
        self.assertEqual(self.historical.read_bytes(), b'prior claim preserved')
        self.assertEqual(self.constructor, dict(port=None, baudrate=115200, timeout=0.05, write_timeout=1, exclusive=True))
        self.assertEqual(self.lines, (True, False, self.plan['port']))
        self.assertFalse(self.serial.is_open)
        self.assertEqual(len(list((self.out/'execution').glob('*.request'))), len(self.commands))

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


    def run_observe(self, selector=4):
        now = dt.datetime.now(dt.timezone.utc)
        read_approval = self.root/'read-approval.json'
        read_approval.write_bytes(op.json_bytes(dict(approved=True, scope='read-only', source=op.SOURCE, uf2=op.UF2,
            port=self.plan['port'], usbSerial=self.plan['usbSerial'], ownerReference='OFFLINE FAKE READ ONLY',
            approvedAtUtc=now.isoformat(), expiresAtUtc=(now+dt.timedelta(minutes=10)).isoformat())))
        endpoint = types.SimpleNamespace(vid=0x2e8a, pid=10, device=self.plan['port'], serial_number=self.plan['usbSerial'])
        with patch('serial.Serial', lambda **kw: FakeSerial(self, **kw)), patch('serial.tools.list_ports.comports', return_value=[endpoint]), patch.object(op.time, 'monotonic', self.clock):
            return op.observe(ARGS.snapshot, read_approval, ARGS.uf2, self.root/'observed', selector, PB)

    def test_observe_switch_then_prepare_actual_snapshot(self):
        self.mode = 'recorded'
        snap = self.run_observe()
        self.assertEqual(snap['store']['configSha'], op.CURRENT)
        self.assertEqual(self.sets, 0)
        op.prepare(self.root/'observed', ARGS.xinput_baseline, self.ledger, self.root/'new-plan', PB)
        self.assertEqual(len(list(self.ledger.iterdir())), 1)

    def test_observe_xinput(self):
        self.current = self.target
        self.mode = 'recorded'
        self.assertEqual(self.run_observe(1)['store']['configSha'], op.TARGET)
        self.assertEqual(self.sets, 0)

    def test_observe_unexpected_config_refuses_snapshot(self):
        self.current += b'\x00'
        with self.assertRaises(ValueError): self.run_observe()
        self.assertFalse((self.root/'observed/snapshot.json').exists())
        self.assertEqual(self.sets, 0)

    def test_approval_expiry_during_full_preflight(self):
        real = dt.datetime
        initial = real.now(dt.timezone.utc)
        expired = real.fromisoformat(op.read_json(self.approval)['expiresAtUtc']) + dt.timedelta(seconds=1)
        with patch.object(op.dt, 'datetime', wraps=real) as clock:
            clock.now.side_effect = lambda tz: expired if self.gets else initial
            self.rejected()
        self.assertEqual(self.sets, 0)
        self.assertTrue((self.out/'execution/terminal.json').exists())

    def test_predicted_snapshot_cannot_prepare(self):
        saved = op.read_json(self.snapshot/'snapshot.json'); saved.pop('observation')
        (self.snapshot/'snapshot.json').write_bytes(op.json_bytes(saved))
        with self.assertRaisesRegex(ValueError, 'actual Switch'): op.prepare(self.snapshot, ARGS.xinput_baseline, self.ledger, self.root/'prediction', PB)

    def test_retained_actual_list_read_envelopes(self):
        self.assertEqual(len(self.recorded), 31)
        self.mode = 'recorded'
        self.assertEqual(self.run_operator()['profilesVerified'], 27)

    def test_wrong_artifact(self):
        wrong = self.root/'wrong.uf2'; wrong.write_bytes(b'wrong firmware')
        with patch.object(ARGS, 'uf2', wrong): self.rejected()
        self.assertEqual(self.opens, 0)

    def test_historical_ledger_change(self):
        self.historical.write_bytes(b'changed')
        self.rejected()
        self.assertEqual(self.opens, 0)

    def test_new_ledger_refused(self):
        other = self.root/'empty-ledger'; other.mkdir()
        self.change_plan(lambda p:p.update(ledger=str(other)))
        self.rejected()
        self.assertEqual(self.opens, 0)

    def test_baseline_manifest_tamper(self):
        self.change_plan(lambda p:p['entries'][0].update(name='changed'))
        self.rejected()

    def test_duplicate_raw_wrapper(self):
        raw = b'\x4a\x01x\x4a\x01y'
        with self.assertRaisesRegex(ValueError, 'duplicate'): op.nested_wrapper(raw)



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


for mode in ['package-fenced','package-floor','package-floor-zero','package-incomplete','package-unknown','package-unresolved','directory','pagination','wrapper','read-health','read-id','firmware','incarnation','generation','highwater','recovery','fenced','unresolved','admission','status-token','stale-config']:
    setattr(RestoreTests,'test_live_'+mode.replace('-','_'),live_guard_case(mode))
for mode in ['post-directory','post-wrapper','partial-write','missing-ack','partial-ack','error-ack','ack-payload','double-ack','readback']:
    setattr(RestoreTests,'test_uncertain_'+mode.replace('-','_'),uncertain_case(mode))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',type=Path,required=True)
    parser.add_argument('--xinput-baseline',type=Path,required=True)
    parser.add_argument('--uf2',type=Path,required=True)
    ARGS=parser.parse_args()
    # Original private inputs are inspected only; every write goes to tempdirs.
    op.require(op.sha((ARGS.snapshot/'snapshot.json').read_bytes()) == op.PINS['baselineSnapshotSha256'],
               'retained Stage-H snapshot changed')
    op.verify_ledger(Path(op.PINS['ledger']))
    PB,_,_=op.config_tool.load_runtime_proto_modules(op.ROOT)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RestoreTests))
    sys.exit(not result.wasSuccessful())
