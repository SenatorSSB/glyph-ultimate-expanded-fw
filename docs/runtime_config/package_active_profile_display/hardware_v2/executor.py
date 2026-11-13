#!/usr/bin/env python3
"""Frozen display v2 operator: four read-only sessions; owner-only physical steps.

No firmware build, flash, profile/reference/default write, query or retry path.
The CLI validates immutable preparation and external owner approval before any
OS enumeration/serial access. Tests inject IO into the same Runner, not a replica.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import glyph_serial_config_tool as framing
import glyph_runtime_identity_tool as identity
import glyph_hardware_artifact_custody as custody
from convert_glyph_native_ultimate_profile import raw_fields, validate_profile_wire

PACKET_ID = 'GLYPH-DISPLAY-9E69188D-HW-v2'
EPISODE_PATH = Path('/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/display-hardware-results/GLYPH-DISPLAY-9E69188D-HW-v2-20261113')
SCHEMAS = frozenset((1, 2, 3, 5))
NATIVE53 = '72c1d401f65c1884ca5bd37f6114727a196fddd8082298c9c95dd39d4ecfae87'
DOMAIN = b'Glyph.RuntimeIdentity.UltimateProfile.v1\0'
STAGES = ('pre_snapshot', 'install', 'first_xinput_boot', 'display',
          'post_snapshot', 'final_xinput_boot', 'finish')


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def save(root, name, value):
    data = value if isinstance(value, bytes) else (json.dumps(value, indent=2) + '\n').encode()
    path = root / name
    with path.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(root, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def bindings():
    """Existing host protobuf generator, only exact pinned schema inputs."""
    with tempfile.TemporaryDirectory(prefix='glyph-display-v2-bindings-') as directory:
        result = subprocess.run([sys.executable, '-m', 'grpc_tools.protoc',
            '-I', str(ROOT / 'schema/haybox'), '--python_out=' + directory,
            str(ROOT / 'schema/haybox/config.proto'), str(ROOT / 'schema/haybox/package.proto')],
            capture_output=True, text=True)
        need(result.returncode == 0, 'pinned host protobuf bindings unavailable')
        sys.path.insert(0, directory)
        try:
            pb = importlib.import_module('config_pb2')
            package = importlib.import_module('package_pb2')
            generated = {p.name: digest(p.read_bytes()) for p in Path(directory).glob('*_pb2.py')}
        finally:
            sys.path.remove(directory)
    return pb, package, generated


def module_dependencies():
    """Only import dependencies; no enumeration or device access."""
    for name in ('serial', 'serial.serialposix', 'serial.serialutil', 'serial.tools.list_ports',
                 'serial.tools.list_ports_osx', 'grpc_tools.protoc', 'google.protobuf',
                 'google.protobuf.json_format', 'google._upb._message'):
        importlib.import_module(name)
    result = {}
    for name, module in list(sys.modules.items()):
        file = getattr(module, '__file__', None)
        if file and name.startswith(('serial', 'google.protobuf', 'google._upb', 'grpc_tools')):
            path = Path(file).resolve()
            if path.is_file() and path.suffix != '.pyc':
                result[str(path)] = digest(path.read_bytes())
    return dict(sorted(result.items()))


def verify_custody(packet):
    for item in packet['artifacts'].values():
        path = Path(item['custody'])
        need(path.is_absolute() and not any(p.is_symlink() for p in (path, *path.parents)),
             'symlinked/nonabsolute artifact custody')
        actual, size = custody._hash_open_regular(path)
        need((actual, size) == (item['sha256'], item['bytes']), 'retained artifact changed')


def verify_preparation():
    packet = load(HERE / 'packet.json')
    manifest = load(HERE / 'PREPARATION_MANIFEST.json')
    need(packet['packet_id'] == PACKET_ID, 'wrong packet')
    for relative, expected in manifest['repository_files'].items():
        path = ROOT / relative
        need(not path.is_symlink() and path.is_file(), 'preparation file unavailable')
        need(digest(path.read_bytes()) == expected, 'preparation changed: ' + relative)
    need(digest((HERE / 'executor.py').read_bytes()) == packet['executor_sha256'], 'executor mismatch')
    pb, package, generated = bindings()
    need(generated == manifest['generated_bindings'], 'generated host bindings changed')
    need(module_dependencies() == manifest['python_modules'], 'Python dependency closure changed')
    need(digest(Path(sys.executable).resolve().read_bytes()) == manifest['python_binary_sha256'],
         'Python interpreter changed')
    verify_custody(packet)
    return packet, pb, package


def approve(packet, approval):
    need(approval.get('approved') is True and approval.get('packet_id') == PACKET_ID
         and bool(approval.get('owner_message_reference')), 'fresh explicit v2 owner approval required')
    expected = {'packet_id': PACKET_ID, 'packet_sha256': digest((HERE / 'packet.json').read_bytes()),
        'preparation_manifest_sha256': digest((HERE / 'PREPARATION_MANIFEST.json').read_bytes()),
        'built_source_sha': packet['built_source_sha'],
        'uf2_sha256': packet['artifacts']['firmware.uf2']['sha256']}
    need(approval.get('approved') is True and bool(approval.get('owner_message_reference')),
         'fresh explicit owner approval required')
    need(all(approval.get(k) == v for k, v in expected.items()), 'approval tuple mismatch')


def approved_episode_path(packet, supplied):
    path = Path(supplied).resolve()
    need(path == EPISODE_PATH.resolve() == Path(packet['episode_custody']).resolve(),
         'only the fixed fresh v2 episode path is allowed')
    need('GLYPH-DISPLAY-9E69188D-HW-v1' not in str(path), 'v1 is immutable/terminal')
    return path


def validate_read(pb, entry, response_wire, token):
    """Store READ/activation contracts: legacy1..3 vs native5, never legacy equality."""
    response = pb.ProfileStoreResponse.FromString(response_wire)
    need(response.protocol_version == 2 and response.request_token == token and response.status == 1,
         'READ response correlation/status')
    need(response.profile_id == entry.profile_id and response.profile_revision == entry.revision,
         'READ requested ID/revision mismatch')
    need(not response.diagnostic and not response.recovery_flags and response.profile_health in (0, 1),
         'READ diagnostic/recovery/error')
    wrappers = [v for t, w, v in raw_fields(response_wire) if t == 9 and w == 2]
    need(len(wrappers) == 1, 'missing/duplicate raw READ profile')
    wrapper = wrappers[0]
    checked = validate_profile_wire(wrapper)
    schemas = [v for t, w, v in raw_fields(wrapper) if t == 1 and w == 0]
    need(len(schemas) == 1, 'missing/duplicate raw profile schema')
    actual = response.profile.schema_version
    need(actual == schemas[0] and actual in SCHEMAS and entry.payload_version in SCHEMAS,
         'unsupported/inconsistent profile schema')
    need((actual == 5) == (entry.payload_version == 5), 'legacy/native family disagreement')
    if actual != 5:
        # Reuse the existing finite host legacy validator, not a new semantic model.
        config = pb.Config()
        config.ultimate_profiles.add().CopyFrom(response.profile)
        need(not framing.verify_ultimate_profiles(config, pb), 'invalid bounded legacy profile')
    if entry.profile_id == 53:
        need(entry.name == 'KazTest5' and entry.revision == 1 and actual == 5
             and entry.payload_version == 5 and digest(wrapper) == NATIVE53,
             'native53 exact identity/header mismatch')
    return wrapper, {'directory_payload_version': entry.payload_version,
        'payload_schema_version': actual, 'revision': response.profile_revision,
        'sha256': digest(wrapper), 'bytes': len(wrapper), 'validation': checked}


class LiveIO:
    """Existing pyserial IO, strict no-flush open, no new wire protocol."""
    def ports(self):
        from serial.tools.list_ports import comports
        return [{'device': p.device, 'vid': p.vid, 'pid': p.pid, 'serial': p.serial_number,
                 'location': p.location, 'hwid': p.hwid} for p in comports()]

    def unowned(self, port):
        p = subprocess.run(['lsof', '-n', '-F', 'pucn', '--', port], capture_output=True, text=True)
        return p.returncode == 1 and not p.stdout and not p.stderr

    def port(self, name):
        import serial
        class PreserveInput(serial.Serial):
            # serial3.5 otherwise destroys queued input during open.
            def _reset_input_buffer(self):
                pass
        p = PreserveInput(port=None, baudrate=115200, bytesize=8, parity='N', stopbits=1,
            timeout=0.05, write_timeout=0.25, xonxoff=False, rtscts=False, dsrdtr=False,
            exclusive=True)
        p.dtr, p.rts, p.port = True, False, name
        return p

    def clock(self):
        return time.monotonic()

    def token(self):
        return secrets.randbits(64)


class Runner:
    def __init__(self, packet, episode, pb, package, io):
        self.p, self.c, self.pb, self.package, self.io = packet, Path(episode), pb, package, io
        self.used = {load(p)['token'] for p in self.c.glob('*/*-transport.json') if load(p).get('token')}
        self.count = 0

    def token(self):
        value = self.io.token()
        while not value or value in self.used:
            value = self.io.token()
        self.used.add(value)
        return value

    def prior(self, stage):
        need(not (self.c / 'terminal.json').exists(), 'episode terminal; no resume/retry')
        need(load(self.c / stage / 'result.json')['result'] == 'PASS', 'prior stage not PASS')
        if stage in ('pre_snapshot', 'first_xinput_boot', 'post_snapshot', 'final_xinput_boot'):
            need(load(self.c / stage / 'settlement.json')['port_closed'], 'prior port not settled')

    def admit(self, stage, context):
        records = self.io.ports()
        save(stage, 'OS-ports-private.json', records)
        target = self.p['target']
        if context == 'configurator':
            allowed = {(0x2e8a, 0x000a), (0x2e8a, 0x1092)}
        else:
            allowed = {(0x0738, 0x4726)}
        candidates = [r for r in records if (r['vid'], r['pid']) in allowed
            or (r['serial'] and digest(r['serial'].encode()) == target['serial_utf8_sha256'])]
        need(len(candidates) == 1, 'not exactly one unit/no competitor')
        r = candidates[0]
        need(r['serial'] and digest(r['serial'].encode()) == target['serial_utf8_sha256']
             and (r['vid'], r['pid']) in allowed and r['device'].startswith('/dev/cu.'),
             'fresh unit/route mismatch')
        need(self.io.unowned(r['device']), 'port already owned/ownership unknown')
        save(stage, 'admission-private.json', {'port': r['device'], 'vid': r['vid'], 'pid': r['pid'],
             'serial_sha256': digest(r['serial'].encode()), 'one_unit': True, 'no_competitor': True})
        return r['device']

    def allowed_request(self, index, command, payload, token, xinput):
        if xinput:
            need(index == 1 and command is None and payload == identity.request(token),
                 'only one fixed XInput identity request allowed')
            return
        if index == 1:
            wanted_command, wanted_payload = 10, identity.request(token)
        elif index == 2:
            wanted_command = 9
            wanted_payload = self.package.PackageEnvelope(protocol_version=3,
                request_token=token, operation=1).SerializeToString(deterministic=True)
        elif index == 3:
            wanted_command, wanted_payload = 3, b''
        elif 4 <= index <= 7:
            wanted_command = 9
            wanted_payload = self.pb.ProfileStoreRequest(protocol_version=2,
                request_token=token, operation=2, page_cursor=(index-4)*8,
                page_size=8).SerializeToString(deterministic=True)
        else:
            need(8 <= index <= 34 and hasattr(self, 'read_ids'), 'READ outside admitted directory')
            wanted_command = 9
            wanted_payload = self.pb.ProfileStoreRequest(protocol_version=2,
                request_token=token, operation=3,
                profile_id=self.read_ids[index-8]).SerializeToString(deterministic=True)
        need((command, payload) == (wanted_command, wanted_payload), 'request outside exact packet table')

    def exchange(self, port, stage, label, command, payload, token, xinput=False):
        limit = 1 if xinput else 34
        need(self.count < limit, 'stage operation limit')
        self.allowed_request(self.count + 1, command, payload, token, xinput)
        self.count += 1
        stem = f'{self.count:02d}-{label}'
        tx = payload if xinput else framing.cobs_encode(bytes([command]) + payload)
        save(stage, stem + '-request.pb', payload)
        save(stage, stem + '-tx.bin', tx)
        deadline = 10 if label == 'IDENTITY' else 30
        meta = {'command': command, 'token': token, 'deadline_ms': deadline * 1000,
                'tx_invoked': False, 'tx_resolved': False, 'response_settled': False}
        save(stage, stem + '-intent.json', dict(meta, tx_sha256=digest(tx)))
        started, raw = self.io.clock(), bytearray()
        rx_hash = hashlib.sha256()
        decoder = identity.Decoder(token, expected_backend=2) if xinput else None
        try:
            # Retain unexpected already-queued bytes and stop before a request;
            # Configurator has no permitted unsolicited stream. XInput does.
            if not xinput and port.in_waiting:
                extra = port.read(port.in_waiting)
                save(stage, stem + '-unsolicited.bin', extra)
                raise ValueError('unsolicited Configurator bytes before send')
            meta['tx_invoked'] = True
            need(port.write(tx) == len(tx), 'partial host write; no resend')
            meta['tx_resolved'] = True
            with (stage / (stem + '-rx.bin')).open('xb') as capture:
                while True:
                    need(self.io.clock() - started < deadline, 'response deadline exceeded')
                    chunk = port.read(max(1, min(4096, port.in_waiting)))
                    if chunk:
                        capture.write(chunk)
                        capture.flush()
                        os.fsync(capture.fileno())
                        rx_hash.update(chunk)
                        if not xinput:
                            raw.extend(chunk)
                            need(len(raw) <= 9000, 'response capture bound')
                        if xinput:
                            decoder.feed(chunk)
                            if decoder.response is not None and not decoder.pending:
                                # One short passive settlement read; never another request.
                                suffix = port.read(max(1, min(4096, port.in_waiting)))
                                if suffix:
                                    capture.write(suffix); capture.flush(); os.fsync(capture.fileno())
                                    rx_hash.update(suffix); decoder.feed(suffix)
                                if not decoder.pending:
                                    answer = decoder.finish()
                                    break
                        elif 0 in raw:
                            need(len(raw) > 1 and raw[-1] == 0 and raw.count(0) == 1,
                                 'empty/extra/ambiguous Configurator frame')
                            suffix = port.read(1)
                            if suffix:
                                capture.write(suffix); capture.flush(); os.fsync(capture.fileno())
                                rx_hash.update(suffix)
                                raise ValueError('trailing Configurator bytes')
                            answer = framing.cobs_decode(bytes(raw))
                            save(stage, stem + '-decoded.bin', answer)
                            break
            need(self.io.clock() - started <= deadline, 'response/settlement deadline exceeded')
            meta['response_settled'] = True
            return answer
        finally:
            meta.update(elapsed_ms=(self.io.clock() - started) * 1000, rx_sha256=rx_hash.hexdigest())
            save(stage, stem + '-transport.json', meta)

    def common(self, response, token):
        need(response.protocol_version == 2 and response.request_token == token and response.status == 1,
             'response correlation/status mismatch')
        need((response.store_incarnation, response.store_generation, response.config_generation) ==
             (1, 229, 1599895773), 'store/saved Config generation drift')
        need(not response.diagnostic and not response.recovery_flags, 'recovery/error response')

    def snapshot(self, stage, port, post):
        pb = self.pb
        token = self.token()
        raw = self.exchange(port, stage, 'IDENTITY', 10, identity.request(token), token)
        d = identity.ConfiguratorDecoder(token)
        d.feed(framing.cobs_encode(raw)); observed = d.finish()
        need(observed['status'] == 'configurator' and observed['primary_backend'] == 8,
             'normal Configurator required')
        save(stage, 'identity.json', observed)
        token = self.token()
        req = self.package.PackageEnvelope(protocol_version=3, request_token=token, operation=1)
        raw = self.exchange(port, stage, 'PACKAGE_STATUS', 9, req.SerializeToString(deterministic=True), token)
        need(raw[0] == 9, 'package response command')
        status = self.package.PackageResponse.FromString(raw[1:])
        need(status.protocol_version == 3 and status.request_token == token and status.status == 1,
             'package response correlation/status')
        need((status.store_incarnation, status.store_generation, status.config_generation,
              status.transaction_token_high_water) == (1, 229, 1599895773, 17293822569102712133),
             'package/saved baseline drift')
        need(status.logical == 0 and not status.write_fenced and status.storage_floor == 2,
             'package uncertainty/fence/floor')
        need((status.capability_version, status.supported_package_format, status.supported_root_format,
             status.supported_record_format, status.supported_receipt_format, status.package_schema_version,
             status.capability_bits) == (1, 1, 3, 2, 1, 1, 31), 'package capabilities')
        raw = self.exchange(port, stage, 'CONFIG', 3, b'', None)
        need(raw[0] == 4, 'GET_CONFIG response command')
        config = raw[1:]
        need(digest(config) == self.p['baseline']['config_sha256'], 'saved raw Config changed')
        save(stage, 'Config.body', config)
        cfg = pb.Config.FromString(config)
        row = cfg.game_mode_configs[2]
        need((cfg.default_usb_backend_config, cfg.communication_backend_configs[0].default_mode_config,
             row.ultimate_profile_id, row.ultimate_profile_engine, row.layout_plate) == (1, 3, 53, 1, 0),
             'saved default/plate changed')
        entries = []
        for cursor, count, next_cursor in ((0, 8, 8), (8, 8, 16), (16, 8, 24), (24, 3, 0)):
            token = self.token()
            req = pb.ProfileStoreRequest(protocol_version=2, request_token=token, operation=2,
                                         page_cursor=cursor, page_size=8)
            raw = self.exchange(port, stage, 'LIST-' + str(cursor), 9,
                                req.SerializeToString(deterministic=True), token)
            need(raw[0] == 9, 'LIST command')
            response = pb.ProfileStoreResponse.FromString(raw[1:]); self.common(response, token)
            need(len(response.entries) == count and response.next_page_cursor == next_cursor,
                 'LIST cursor/count')
            entries.extend(response.entries)
        need(len(entries) == 27 and len({e.profile_id for e in entries}) == 27 and
             all(e.profile_id and e.revision and not e.health for e in entries), 'directory IDs/count/health')
        encoded = [e.SerializeToString(deterministic=True) for e in entries]
        directory = b''.join(len(b).to_bytes(4, 'big') + b for b in encoded)
        directory_sha = digest(b'Glyph.DisplayPacket.Directory.v1\0' + directory)
        need(directory_sha == self.p['baseline']['directory_sha256'], 'directory metadata changed')
        save(stage, 'directory.bin', directory)
        profiles = {}
        self.read_ids = [entry.profile_id for entry in entries]
        for entry in entries:
            token = self.token()
            req = pb.ProfileStoreRequest(protocol_version=2, request_token=token, operation=3,
                                         profile_id=entry.profile_id)
            raw = self.exchange(port, stage, 'READ-' + str(entry.profile_id), 9,
                                req.SerializeToString(deterministic=True), token)
            need(raw[0] == 9, 'READ command')
            self.common(pb.ProfileStoreResponse.FromString(raw[1:]), token)
            wrapper, facts = validate_read(pb, entry, raw[1:], token)
            if post:
                prior = load(self.c / 'pre_snapshot/result.json')['profiles'][str(entry.profile_id)]
                need(wrapper == (self.c / 'pre_snapshot' / f'profile-{entry.profile_id}.pb').read_bytes(),
                     'profile raw-byte preservation failure')
                need(facts == prior, 'profile schema/metadata preservation failure')
            save(stage, f'profile-{entry.profile_id}.pb', wrapper)
            profiles[str(entry.profile_id)] = facts
        need(self.count == 34, 'snapshot request total')
        if post:
            need(config == (self.c / 'pre_snapshot/Config.body').read_bytes(), 'saved Config preservation')
            need(directory == (self.c / 'pre_snapshot/directory.bin').read_bytes(), 'directory preservation')
        return {'result': 'PASS', 'controller_exchanges': self.count, 'profiles': profiles,
                'config_sha256': digest(config), 'directory_sha256': directory_sha,
                'native53_runtime_digest': digest(DOMAIN + (stage / 'profile-53.pb').read_bytes())}

    def xinput(self, stage, port):
        token = self.token()
        answer = self.exchange(port, stage, 'IDENTITY', None, identity.request(token), token, xinput=True)
        need((answer['status'], answer['primary_backend'], answer['context_row'],
              answer['requested_reference'], answer['incarnation'], answer['active_id'],
              answer['active_revision'], answer['schema_version']) ==
             ('persisted', 2, 3, 53, 1, 53, 1, 5), 'default native53 runtime identity')
        expected = load(self.c / 'pre_snapshot/result.json')['native53_runtime_digest']
        need(answer['payload_sha256'] == expected, 'runtime payload digest mismatch')
        return {'result': 'PASS', 'controller_exchanges': self.count, 'identity': answer}

    def execute(self, name, event):
        need(name in STAGES and not (self.c / 'terminal.json').exists(), 'stage/terminal; no resume')
        index = STAGES.index(name)
        if index:
            self.prior(STAGES[index - 1])
        stage = self.c / name
        stage.mkdir(mode=0o700, exist_ok=False)
        self.count = 0
        port, terminal = None, None
        try:
            save(stage, 'claim.json', {'stage': name, 'one_invocation_only': True,
                 'executor_sha256': digest(Path(__file__).read_bytes())})
            save(stage, 'owner-event.json', event)
            need(event.get('owner_present') is True and bool(event.get('owner_message_reference')),
                 'fresh actual owner event required')
            if name in ('pre_snapshot', 'post_snapshot', 'first_xinput_boot', 'final_xinput_boot'):
                need(event.get('ready') is True and event.get('exclusive') is True,
                     'owner readiness/exclusivity not confirmed')
                if name == 'pre_snapshot':
                    need(event.get('prior_firmware_c439_no_change') is True, 'prior firmware custody unknown')
                else:
                    need(event.get('same_unit_no_change') is True, 'candidate/unit continuity unknown')
                context = 'configurator' if 'snapshot' in name else 'xinput'
                need(event.get('route') in (('menu', 'heldRT2') if context == 'configurator'
                     else ('normal_no_buttons_USB_default',)), 'unexpected route')
                device = self.admit(stage, context)
                port = self.io.port(device)
                save(stage, 'open-intent.json', {'115200_DTR_true_RTS_false': True, 'no_flush': True})
                port.open()
                save(stage, 'open-result.json', {'opened': True})
                success = self.snapshot(stage, port, name == 'post_snapshot') if 'snapshot' in name else self.xinput(stage, port)
            elif name == 'install':
                verify_custody(self.p)
                need(event.get('source_sha') == self.p['built_source_sha'] and
                     event.get('uf2_sha256') == self.p['artifacts']['firmware.uf2']['sha256'] and
                     event.get('uf2_bytes') == 1296896, 'owner installation tuple mismatch')
                need(event.get('manual_install_count') == 1 and event.get('one_same_unit_bootloader') is True
                     and event.get('copy_result') == 'confirmed_success' and
                     event.get('reenumeration') == 'unambiguous' and bool(event.get('fresh_volume_path')),
                     'manual install/copy outcome uncertain')
                success = {'result': 'PASS', 'manual_install_count': 1, 'actor': 'owner',
                           'build_attestation': False, 'basis': 'exact custody + owner one-copy continuity'}
            else:
                need(event.get('dashboard_name') == 'KazTest5' and event.get('plate') == 'Unknown Plate'
                     and event.get('backend') == 'XInput' and event.get('responsive') is True,
                     'owner display observation failed/uncertain')
                if name == 'display':
                    need(event.get('viewer_name') == 'KazTest5' and event.get('returned_dashboard') is True,
                         'Input Viewer/return observation failed')
                success = {'result': 'PASS', 'basis': 'attributed owner observation', 'observations': event}
                if name == 'finish':
                    total = sum(load(p).get('controller_exchanges', 0) for p in self.c.glob('*/result.json'))
                    need(total == 70, 'complete packet operation total')
                    success['packet_result'] = 'PASS_BOUNDED_LEGACY_DISPLAY_AND_PRESERVATION'
                    success['controller_exchanges'] = 0
        except BaseException as error:
            terminal = {'result': 'INCONCLUSIVE_TERMINAL_STOP', 'stage': name,
                        'reason': repr(error), 'request_invocations': self.count, 'no_retry': True}
            raise
        finally:
            if port is not None:
                try:
                    port.close()
                    save(stage, 'settlement.json', {'port_closed': True, 'no_retry': True})
                except BaseException as error:
                    terminal = {'result': 'INCONCLUSIVE_TERMINAL_STOP', 'stage': name,
                                'reason': 'close/settlement: ' + repr(error), 'no_retry': True}
                    raise
                finally:
                    if terminal and not (self.c / 'terminal.json').exists():
                        save(self.c, 'terminal.json', terminal)
            elif terminal and not (self.c / 'terminal.json').exists():
                save(self.c, 'terminal.json', terminal)
        need(not (self.c / 'terminal.json').exists(), 'episode terminal after settlement')
        try:
            save(stage, 'result.json', success)
        except BaseException as error:
            if not (self.c / 'terminal.json').exists():
                save(self.c, 'terminal.json', {'result': 'INCONCLUSIVE_TERMINAL_STOP',
                     'stage': name, 'reason': 'result custody: ' + repr(error), 'no_retry': True})
            raise
        return success


def established_episode():
    """Immutable begin-marker presence owns only this fixed v2 namespace.

    Do not parse mutable approval/episode content to decide whether its binding
    failure is terminal: those are precisely the inputs that may be damaged.
    """
    path = EPISODE_PATH
    if not path.is_dir() or any(p.is_symlink() for p in (path, *path.parents)):
        return None
    marker = path / 'begin-claim.json'
    return path if marker.is_file() and not marker.is_symlink() else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('check', 'begin', *STAGES))
    parser.add_argument('--approval', type=Path)
    parser.add_argument('--episode', type=Path)
    parser.add_argument('--owner-event', type=Path)
    args = parser.parse_args()
    # After begin, even offline preflight/binding/custody failures consume the
    # episode. Restoring inputs cannot authorize resumption. Preparation checks
    # before any established episode remain ordinary offline engineering work.
    try:
        established = established_episode()
        if established:
            need(not (established / 'terminal.json').exists(), 'episode terminal; no resume/retry')
        packet, pb, package = verify_preparation()
        if args.stage == 'check':
            print(json.dumps({'result': 'PASS_OFFLINE_PREPARATION', 'packet_id': PACKET_ID,
                              'device_access': False, 'rebuild': False}))
            return
        need(args.approval and args.episode, 'approval and fresh episode path required')
        approval = load(args.approval)
        approve(packet, approval)
        episode = approved_episode_path(packet, args.episode)
        if args.stage == 'begin':
            episode.mkdir(mode=0o700, parents=True, exist_ok=False)
            save(episode, 'begin-claim.json', {'packet_id': PACKET_ID, 'one_episode_only': True})
            save(episode, 'approval.json', approval)
            save(episode, 'episode.json', {'packet_id': PACKET_ID,
                 'packet_sha256': digest((HERE / 'packet.json').read_bytes()),
                 'manifest_sha256': digest((HERE / 'PREPARATION_MANIFEST.json').read_bytes()),
                 'owner_approval': approval, 'one_episode_only': True})
            print('Fresh v2 episode claimed; no device access')
            return
        claimed = load(episode / 'episode.json')
        need(claimed['packet_id'] == PACKET_ID and
             claimed['packet_sha256'] == digest((HERE / 'packet.json').read_bytes()) and
             claimed['manifest_sha256'] == digest((HERE / 'PREPARATION_MANIFEST.json').read_bytes()) and
             claimed['owner_approval'] == approval, 'episode/approval changed')
        need(args.owner_event, 'fresh actual owner event required')
        result = Runner(packet, episode, pb, package, LiveIO()).execute(args.stage, load(args.owner_event))
        print(json.dumps(result, indent=2))
    except BaseException as error:
        owned = established_episode()
        if owned and not (owned / 'terminal.json').exists():
            save(owned, 'terminal.json', {'result': 'INCONCLUSIVE_TERMINAL_STOP',
                 'stage': args.stage, 'reason': repr(error), 'no_retry': True})
        raise

if __name__ == '__main__':
    main()
