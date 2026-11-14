#!/usr/bin/env python3
"""Exact post-Stage-H 0b9ef3af campaign USB selector 4 -> 1 restoration only.

prepare is offline. execute requires a separate exact owner approval and a
durable controller-scoped one-shot claim. Never flashes, reboots or retries.
Offline preparation only until supervisory acceptance and fresh owner approval.
Legacy SET_CONFIG has no atomic CAS or token; exclusive sequential session required.
"""
from __future__ import annotations
import argparse
import base64
import datetime as dt
import hashlib
from functools import lru_cache
import subprocess
import tempfile
import json
import os
from pathlib import Path
import secrets
import sys
import time
import zlib

import glyph_serial_config_tool as config_tool
import glyph_profile_store_production_tool as production

ROOT = Path(__file__).resolve().parents[1]
PINS_PATH = ROOT / 'docs/runtime_config/switch_recovery_20261114/pins.json'
PINS = json.loads(PINS_PATH.read_text())
SOURCE, UF2 = PINS['source'], PINS['uf2']
CURRENT, TARGET = PINS['currentSha256'], PINS['targetSha256']
DEVICE_INFO = bytes.fromhex('0a06486179426f78120830623965663361661a09676c7970685f6d6b36')
OPERATION = 'switch-liveness-stage-h-0b9ef3af-usb-4-to-1'
DEPENDENCIES = ('tools/glyph_switch_recovery.py', 'tools/glyph_serial_config_tool.py',
                'tools/glyph_profile_store_production_tool.py',
                'tools/glyph_profile_store_candidate_tool.py', 'schema/haybox/config.proto', 'schema/haybox/package.proto',
                'docs/runtime_config/switch_recovery_20261114/pins.json')


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def read_json(path):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique)


def durable(path, raw):
    path = Path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
    with os.fdopen(fd, 'wb') as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def tooling():
    return {name: sha((ROOT / name).read_bytes()) for name in DEPENDENCIES}


def exact_payload(current, original, pb):
    require(sha(current) == CURRENT and sha(original) == TARGET, 'unexpected Config hash')
    cfg = pb.Config()
    cfg.ParseFromString(current)
    require(cfg.SerializeToString(deterministic=True) == current, 'noncanonical current Config')
    require((cfg.ultimate_profile_store_format, cfg.ultimate_profile_root_format,
             cfg.managed_format, cfg.managed_sequence) == (1, 3, 1, 6), 'unexpected managed root metadata')
    require(cfg.ultimate_profile_store_incarnation == 1 and not cfg.ultimate_profiles,
            'unexpected store incarnation or embedded profiles')
    require(cfg.default_usb_backend_config == 4 and cfg.default_backend_config == 2,
            'unexpected selector indices')
    require([b.backend_id for b in cfg.communication_backend_configs] == [2, 3, 8, 7],
            'backend indices do not identify XInput/GameCube/Configurator/Switch')
    require([b.default_mode_config for b in cfg.communication_backend_configs] == [3, 3, 1, 3],
            'backend defaults differ')
    require(len(cfg.game_mode_configs) == 4 and cfg.game_mode_configs[2].ultimate_profile_id == 53,
            'GameCube destination or row extent differs')
    cfg.default_usb_backend_config = 1
    payload = cfg.SerializeToString(deterministic=True)
    require(payload == original and sha(payload) == TARGET, 'non-selector difference from original baseline')
    return payload


def verify_entries(entries):
    digest = sha(json.dumps(entries, sort_keys=True, separators=(',', ':')).encode())
    require(digest == PINS['entriesSha256'], 'original directory baseline differs')


def verify_ledger(ledger):
    require(str(ledger) == PINS['ledger'] and ledger.resolve(strict=True) == ledger and
            ledger.is_dir() and not ledger.is_symlink(), 'must use existing controller-specific ledger')
    for name, digest in PINS['ledgerFiles'].items():
        path = ledger / name
        require(path.resolve(strict=True) == path and not path.is_symlink() and
                sha(path.read_bytes()) == digest, 'historical ledger changed')


def nested_wrapper(raw):
    # Inspect wire bytes, not reserialized semantic values. Reject duplicate field9.
    at, wrappers = 0, []
    def varint():
        nonlocal at
        value = 0
        for shift in range(0, 70, 7):
            require(at < len(raw), 'truncated protobuf')
            byte = raw[at]; at += 1; value |= (byte & 127) << shift
            if byte < 128: return value
        raise ValueError('oversized varint')
    while at < len(raw):
        tag = varint(); number, kind = tag >> 3, tag & 7
        require(number > 0, 'invalid protobuf field')
        if kind == 0: varint()
        elif kind == 1: at += 8
        elif kind == 5: at += 4
        elif kind == 2:
            length = varint(); end = at + length
            require(end <= len(raw), 'truncated protobuf field')
            if number == 9: wrappers.append(raw[at:end])
            at = end
        else: raise ValueError('unsupported protobuf wire type')
        require(at <= len(raw), 'truncated fixed field')
    require(len(wrappers) == 1, 'missing/duplicate raw wrapper')
    return wrappers[0]


def preservation(connection, pb, plan, config_raw):
    def query(operation, **kwargs):
        token = secrets.randbits(64) or 1
        req = pb.ProfileStoreRequest(protocol_version=2, request_token=token, operation=operation, **kwargs)
        raw = connection.exchange(9, req.SerializeToString(deterministic=True), 9)
        r = pb.ProfileStoreResponse.FromString(raw)
        require(r.protocol_version == 2 and r.request_token == token and r.status == pb.PROFILE_STORE_OK,
                'uncorrelated/failed preservation read')
        require(r.store_incarnation == plan['store']['incarnation'] and
                r.store_generation == plan['store']['generation'] and
                r.config_generation == zlib.crc32(config_raw) and not r.recovery_flags and not r.diagnostic,
                'preservation guard/health mismatch')
        return r, raw
    def directory():
        actual = []
        for cursor in (0, 8, 16, 24):
            r, _ = query(pb.PROFILE_STORE_LIST, page_cursor=cursor, page_size=8)
            expected = plan['entries'][cursor:cursor+8]
            require(len(r.entries) == len(expected) and r.next_page_cursor == (cursor+8 if cursor < 24 else 0),
                    'directory count/pagination differs')
            for entry, saved in zip(r.entries, expected):
                actual.append((entry.profile_id, entry.revision, entry.name, entry.display_rank, entry.payload_version))
                require(actual[-1] == (saved['id'], int(saved['revision']), saved['name'], saved['rank'], saved['directorySchema'])
                        and not entry.health, 'directory metadata differs')
        return actual
    before = directory()
    wrappers = {}
    for entry in plan['entries']:
        r, raw = query(pb.PROFILE_STORE_READ, profile_id=entry['id'])
        require(r.profile_id == entry['id'] and r.profile_revision == int(entry['revision']) and
                r.HasField('profile') and r.profile.schema_version == entry['wrapperSchema'] and
                r.profile_health == 0, 'profile identity/health differs')
        wrapper = nested_wrapper(raw)
        require(len(wrapper) == entry['wrapperBytes'] and sha(wrapper) == entry['wrapperSha256'],
                'original wrapper bytes differ')
        wrappers[entry['id']] = wrapper
    require(directory() == before, 'directory changed during audit')
    require(connection.exchange(3, b'', 4) == config_raw, 'Config changed during preservation audit')
    status(connection, pb, plan, 2, config_raw)
    status(connection, pb, plan, 4, config_raw)
    return wrappers


def verify_observation(saved):
    require(saved.get('observation') == 'complete read-only candidate capture' and saved.get('selector') == 4,
            'fresh actual Switch observation required; offline prediction is insufficient')
    at = dt.datetime.fromisoformat(saved['observedAtUtc'])
    require(at.tzinfo is not None and 0 <= (dt.datetime.now(dt.timezone.utc)-at).total_seconds() <= 900,
            'Switch observation is stale/future')


def prepare(snapshot, original, ledger, output, pb):
    snapshot, ledger, output = Path(snapshot).resolve(), Path(ledger).resolve(strict=True), Path(output)
    verify_ledger(ledger)
    saved = read_json(snapshot / 'snapshot.json')
    verify_observation(saved)
    current, target = (snapshot / 'config.pb').read_bytes(), Path(original).read_bytes()
    payload = exact_payload(current, target, pb)
    require(saved['source'] == SOURCE and saved['uf2'] == UF2, 'wrong firmware snapshot')
    entries = saved['entries']
    verify_entries(entries)
    require(sha(saved['usbSerial'].encode()) == PINS['usbSerialSha256'], 'wrong physical controller')
    require(len(entries) == 27 and len({e['id'] for e in entries}) == 27, 'incomplete directory')
    for entry in entries:
        name = entry['wrapperFile']
        require(Path(name).name == name, 'invalid wrapper path')
        raw = (snapshot / name).read_bytes()
        require(sha(raw) == entry['wrapperSha256'] and len(raw) == entry['wrapperBytes'], 'wrapper identity differs')
    store = saved['store']
    require(store['incarnation'] == 1 and store['generation'] == 234 and
            store['configSha'] == CURRENT and store['configCrc'] == zlib.crc32(current) and
            store['token'] == '17293822569102712139', 'unexpected store guards')
    require(saved['usbSerial'] and saved['port'].startswith('/dev/cu.'), 'explicit controller/port required')
    output.mkdir()  # exclusive new episode; never overwrite old evidence
    plan = dict(format=1, operation=OPERATION, source=SOURCE, uf2=UF2,
                deviceInfoHex=DEVICE_INFO.hex(), port=saved['port'], usbSerial=saved['usbSerial'],
                currentSha256=CURRENT, targetSha256=TARGET,
                currentBase64=base64.b64encode(current).decode(), targetBase64=base64.b64encode(payload).decode(),
                frameSha256=sha(config_tool.cobs_encode(b'\x04' + payload)),
                store=store, entries=entries, snapshot=str(snapshot), snapshotSha256=sha((snapshot/'snapshot.json').read_bytes()),
                ledger=str(ledger), tooling=tooling(), createdAtUtc=timestamp())
    durable(output / 'current.pb', current)
    durable(output / 'payload.pb', payload)
    durable(output / 'plan.json', json_bytes(plan))
    return plan


def validate_plan(path, pb):
    plan = read_json(path)
    require(plan['format'] == 1 and plan['operation'] == OPERATION, 'wrong plan operation')
    require(plan['source'] == SOURCE and plan['uf2'] == UF2 and plan['deviceInfoHex'] == DEVICE_INFO.hex(), 'wrong firmware')
    require(plan['currentSha256'] == CURRENT and plan['targetSha256'] == TARGET, 'wrong approved hashes')
    require(plan['tooling'] == tooling(), 'tooling changed since preview')
    current = base64.b64decode(plan['currentBase64'], validate=True)
    payload = base64.b64decode(plan['targetBase64'], validate=True)
    exact_payload(current, payload, pb)
    require(plan['frameSha256'] == sha(config_tool.cobs_encode(b'\x04' + payload)), 'wrong frame hash')
    require(len(plan['entries']) == 27 and len({e['id'] for e in plan['entries']}) == 27, 'wrong directory baseline')
    require(plan['store'] == {'token': '17293822569102712139', 'generation': 234, 'configCrc': zlib.crc32(current),
                              'incarnation': 1, 'configSha': CURRENT}, 'wrong approved store guards')
    ledger = Path(plan['ledger'])
    require(ledger.is_absolute() and str(ledger.resolve(strict=True)) == plan['ledger'] and ledger.is_dir(), 'ledger identity differs')
    require(sha(plan['usbSerial'].encode()) == PINS['usbSerialSha256'] and plan['port'].startswith('/dev/cu.'), 'wrong physical controller/port')
    verify_entries(plan['entries'])
    verify_ledger(ledger)
    snapshot = Path(plan['snapshot'])
    require(sha((snapshot/'snapshot.json').read_bytes()) == plan['snapshotSha256'], 'snapshot changed')
    snap = read_json(snapshot/'snapshot.json')
    verify_observation(snap)
    require(snap['entries'] == plan['entries'] and snap['store'] == plan['store'] and
            snap['usbSerial'] == plan['usbSerial'] and snap['port'] == plan['port'] and
            snap['source'] == SOURCE and snap['uf2'] == UF2 and (snapshot/'config.pb').read_bytes() == current,
            'snapshot differs from plan')
    for entry in plan['entries']:
        require(Path(entry['wrapperFile']).name == entry['wrapperFile'], 'unsafe wrapper path')
        raw = (snapshot/entry['wrapperFile']).read_bytes()
        require(sha(raw) == entry['wrapperSha256'] and len(raw) == entry['wrapperBytes'], 'wrapper baseline changed')
    return plan, current, payload


class Connection:
    """One DTR-enabled 115200 connection, strict real COBS decoder; no retries."""
    def __init__(self, port, evidence):
        import serial
        self.evidence = evidence
        self.sequence = 0
        self.wire = serial.Serial(port=None, baudrate=115200, timeout=0.05, write_timeout=1, exclusive=True)
        self.wire.dtr = True
        self.wire.rts = False
        self.wire.port = port

    def __enter__(self):
        self.wire.open()
        return self

    def __exit__(self, *unused):
        self.wire.close()

    def exchange(self, command, payload, response_command):
        self.sequence += 1
        prefix = self.evidence / f'{self.sequence:02d}-cmd{command}'
        raw = bytes([command]) + payload
        frame = config_tool.cobs_encode(raw)
        durable(prefix.with_suffix('.request'), frame)
        require(not self.wire.in_waiting, 'unexpected queued serial data')
        received = bytearray()
        try:
            require(self.wire.write(frame) == len(frame), 'partial request write; never retry')
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                chunk = self.wire.read(max(1, min(8259, self.wire.in_waiting)))
                received.extend(chunk)
                require(len(received) <= 8267, 'oversized reply')
                initial = len(received) - len(received.lstrip(b'\0'))
                require(initial <= 8, 'too many synchronization delimiters')
                if 0 in received[initial:]:
                    require(received.index(0, initial) == len(received)-1 and not self.wire.in_waiting,
                            'extra or ambiguous reply')
                    decoded = config_tool.cobs_decode(bytes(received[initial:]))
                    require(decoded and decoded[0] == response_command, 'wrong response command')
                    return decoded[1:]
            raise TimeoutError('missing/partial response; never retry')
        finally:
            durable(prefix.with_suffix('.response'), bytes(received))


@lru_cache(maxsize=1)
def load_package_schema():
    # Use the tracked actual package schema; config.proto is already loaded by
    # config_tool. Descriptor loading avoids a second config_pb2 module identity.
    from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
    with tempfile.TemporaryDirectory(prefix='glyph_switch_package_') as directory:
        output = Path(directory)/'package.desc'
        subprocess.run([sys.executable, '-m', 'grpc_tools.protoc', '-I'+str(ROOT/'schema/haybox'),
                        '--descriptor_set_out='+str(output), str(ROOT/'schema/haybox/package.proto')],
                       check=True, capture_output=True)
        files = descriptor_pb2.FileDescriptorSet.FromString(output.read_bytes())
    pool = descriptor_pool.Default()
    for item in files.file: pool.AddSerializedFile(item.SerializeToString())
    return tuple(message_factory.GetMessageClass(pool.FindMessageTypeByName(name))
                 for name in ('PackageEnvelope', 'PackageResponse'))


def status(connection, pb, plan, version, config_raw):
    token = secrets.randbits(64) or 1
    request_type, response_type = (pb.ProfileStoreRequest, pb.ProfileStoreResponse) if version == 2 else load_package_schema()
    request = request_type(protocol_version=version, operation=1, request_token=token)
    raw = connection.exchange(9, request.SerializeToString(deterministic=True), 9)
    result = response_type()
    result.ParseFromString(raw)
    require(result.request_token == token and result.protocol_version == version and result.status == pb.PROFILE_STORE_OK,
            'uncorrelated or failed STATUS')
    if version == 2:
        production.verify_production_status(type('Admission', (), {'action': 'status'})(), pb, result)
        require(result.mutation_feasible, 'mutation admission unavailable')
        require(not result.recovery_flags and not result.diagnostic, 'recovery/fencing/diagnostic status')
    else:
        require(not result.write_fenced and result.storage_floor == 2 and result.logical == 0,
                'package write-fenced/unresolved/unsupported storage floor')
    require(result.store_incarnation == plan['store']['incarnation'] and result.store_generation == plan['store']['generation'] and
            result.transaction_token_high_water + 1 == int(plan['store']['token']) and
            result.config_generation == zlib.crc32(config_raw), 'stale incarnation/generation/Config/high-water')


def verify_endpoint(plan):
    from serial.tools.list_ports import comports
    ports = [p for p in comports() if p.vid == 0x2e8a]
    require(len(ports) == 1 and ports[0].device == plan['port'] and ports[0].serial_number == plan['usbSerial'] and
            ports[0].pid in (10, 0x1092) and sha(plan['usbSerial'].encode()) == PINS['usbSerialSha256'],
            'wrong/ambiguous controller or endpoint')


def verify_artifact(path):
    require(Path(path).stat().st_size == 1327104 and sha(Path(path).read_bytes()) == UF2, 'wrong candidate artifact')


def observe(baseline, approval_path, uf2_path, output, selector, pb):
    """Future owner-guided read-only capture; never calls SET_CONFIG or claims ledger."""
    baseline, output = Path(baseline), Path(output)
    require(sha((baseline/'snapshot.json').read_bytes()) == PINS['baselineSnapshotSha256'], 'wrong Stage-H snapshot')
    saved = read_json(baseline/'snapshot.json')
    verify_entries(saved['entries'])
    target = (baseline/'config.pb').read_bytes()
    cfg = pb.Config.FromString(target); cfg.default_usb_backend_config = 4
    current = cfg.SerializeToString(deterministic=True)
    exact_payload(current, target, pb)
    require(selector in (1, 4), 'only exact XInput or Switch checkpoint observation supported')
    expected = target if selector == 1 else current
    approval = read_json(approval_path)
    require(set(approval) == {'approved', 'scope', 'source', 'uf2', 'port', 'usbSerial',
                             'ownerReference', 'approvedAtUtc', 'expiresAtUtc'}, 'invalid read approval fields')
    require(approval['approved'] is True and approval['scope'] == 'read-only' and approval['ownerReference'] and
            approval['source'] == SOURCE and approval['uf2'] == UF2, 'missing exact read approval')
    now = dt.datetime.now(dt.timezone.utc)
    approved, expires = (dt.datetime.fromisoformat(approval[k]) for k in ('approvedAtUtc', 'expiresAtUtc'))
    require(approved.tzinfo is not None and expires.tzinfo is not None and approved <= now <= expires and
            0 < (expires-approved).total_seconds() <= 900, 'expired/future read approval')
    plan = dict(store=dict(saved['store'], configSha=sha(expected), configCrc=zlib.crc32(expected)),
                entries=saved['entries'], port=approval['port'], usbSerial=approval['usbSerial'])
    require(plan['port'].startswith('/dev/cu.'), 'wrong port')
    verify_artifact(uf2_path); verify_endpoint(plan)
    output.mkdir()
    evidence = output/'observation'; evidence.mkdir()
    durable(evidence/'approval.json', json_bytes(approval))
    with Connection(plan['port'], evidence) as connection:
        require(connection.exchange(1, b'', 2) == DEVICE_INFO, 'wrong advertised firmware identity')
        status(connection, pb, plan, 2, expected); status(connection, pb, plan, 4, expected)
        observed = connection.exchange(3, b'', 4)
        require(observed == expected, 'observed Config differs; stop without guessing restoration')
        wrappers = preservation(connection, pb, plan, observed)
    for entry in plan['entries']:
        durable(output/entry['wrapperFile'], wrappers[entry['id']])
    durable(output/'config.pb', observed)
    snapshot = dict(source=SOURCE, uf2=UF2, port=plan['port'], usbSerial=plan['usbSerial'],
                    store=plan['store'], entries=plan['entries'], observedAtUtc=timestamp(),
                    observation='complete read-only candidate capture', selector=selector)
    # Publish only a complete closed observation; prepare consumes this snapshot.
    durable(output/'snapshot.json', json_bytes(snapshot))
    return snapshot


def execute(plan_path, approval_path, uf2_path, exclusive, pb):
    require(exclusive, 'owner-exclusive Configurator session required')
    plan_path = Path(plan_path)
    plan, current, payload = validate_plan(plan_path, pb)
    approval = read_json(approval_path)
    plan_digest, approval_digest = sha(plan_path.read_bytes()), sha(Path(approval_path).read_bytes())
    require(set(approval) == {'approved', 'planSha256', 'frameSha256', 'port', 'usbSerial', 'approvedAtUtc', 'expiresAtUtc', 'exclusiveConfiguratorSession', 'ownerReference'}, 'invalid approval fields')
    require(approval['approved'] is True and approval['exclusiveConfiguratorSession'] is True and approval['ownerReference'], 'missing exact owner approval')
    require(approval['planSha256'] == sha(plan_path.read_bytes()) and approval['frameSha256'] == plan['frameSha256'] and
            approval['port'] == plan['port'] and approval['usbSerial'] == plan['usbSerial'], 'stale or mismatched approval')
    now = dt.datetime.now(dt.timezone.utc)
    approved = dt.datetime.fromisoformat(approval['approvedAtUtc'])
    expires = dt.datetime.fromisoformat(approval['expiresAtUtc'])
    require(approved.tzinfo is not None and expires.tzinfo is not None and
            approved <= now <= expires and 0 < (expires-approved).total_seconds() <= 900, 'expired/future approval')
    verify_artifact(uf2_path)
    verify_endpoint(plan)
    key = sha((SOURCE + ':' + plan['usbSerial'] + ':' + OPERATION).encode())
    claim = Path(plan['ledger']) / ('switch-stage-h-restore-' + key + '.claim')
    # Claim is controller/operation-scoped, independent of approval/episode/token.
    # It is burned before opening a port, including all uncertain/preflight failures.
    durable(claim, json_bytes({'planSha256': sha(plan_path.read_bytes()), 'approvalSha256': sha(Path(approval_path).read_bytes()),
                              'atUtc': timestamp(), 'terminalOnceCreated': True}))
    evidence = plan_path.parent / 'execution'
    evidence.mkdir()
    durable(evidence/'intent.json', json_bytes({'planSha256': sha(plan_path.read_bytes()), 'approval': approval,
                                              'frameSha256': plan['frameSha256'], 'claim': str(claim),
                                              'targetSha256': TARGET, 'legacyAtomicFence': False, 'atUtc': timestamp()}))
    durable(evidence/'payload.pb', payload)
    attempted = False
    try:
        with Connection(plan['port'], evidence) as connection:
            require(connection.exchange(1, b'', 2) == DEVICE_INFO, 'wrong advertised firmware identity')
            status(connection, pb, plan, 2, current)
            status(connection, pb, plan, 4, current)
            preservation(connection, pb, plan, current)
            verify_ledger(Path(plan['ledger']))
            require(connection.exchange(3, b'', 4) == current, 'fresh Config differs; no SET sent')
            # The complete read-heavy audit can outlast a nearly expired approval.
            # Recheck every immutable input and the approval at the actual write boundary.
            require(sha(plan_path.read_bytes()) == plan_digest and sha(Path(approval_path).read_bytes()) == approval_digest,
                    'plan/approval changed during preflight')
            validate_plan(plan_path, pb)
            require(approved <= dt.datetime.now(dt.timezone.utc) <= expires, 'approval expired during preflight')
            durable(evidence/'set-attempt.json', json_bytes({'atUtc': timestamp(), 'frameSha256': plan['frameSha256'], 'maximumRequests': 1}))
            attempted = True
            require(connection.exchange(4, payload, 6) == b'', 'nonempty/ambiguous acknowledgement')
            require(connection.exchange(3, b'', 4) == payload, 'saved Config readback mismatch')
            status(connection, pb, plan, 2, payload)
            status(connection, pb, plan, 4, payload)
            preservation(connection, pb, plan, payload)
            verify_ledger(Path(plan['ledger']))
        result = dict(status='CONFIG RESTORED; COMPLETE 27-PROFILE PRESERVATION VERIFIED',
                      setRequestsAttempted=1, profilesVerified=27, configSha256=TARGET, claim=str(claim), atUtc=timestamp())
        durable(evidence/'result.json', json_bytes(result))
        return result
    except BaseException as error:
        durable(evidence/'terminal.json', json_bytes({'atUtc': timestamp(), 'setMayHaveBeenAttempted': attempted,
                                                     'status': 'OUTCOME UNCERTAIN' if attempted else 'BLOCKED BEFORE SET',
                                                     'error': str(error), 'claim': str(claim), 'retryForbidden': True}))
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    capture = sub.add_parser('observe')
    for name in ('baseline', 'approval', 'uf2', 'out'):
        capture.add_argument('--'+name, type=Path, required=True)
    capture.add_argument('--selector', type=int, choices=(1, 4), required=True)
    preview = sub.add_parser('prepare')
    for name in ('snapshot', 'xinput-baseline', 'ledger', 'out'):
        preview.add_argument('--'+name, type=Path, required=True)
    run = sub.add_parser('execute')
    for name in ('plan', 'approval', 'uf2'):
        run.add_argument('--'+name, type=Path, required=True)
    run.add_argument('--exclusive-configurator-session', action='store_true')
    args = parser.parse_args(argv)
    pb, _, _ = config_tool.load_runtime_proto_modules(ROOT)
    load_package_schema()
    try:
        if args.action == 'observe':
            snapshot = observe(args.baseline, args.approval, args.uf2, args.out, args.selector, pb)
            print(json.dumps({'status': 'READ-ONLY COMPLETE', 'configSha256': snapshot['store']['configSha'], 'profiles': 27}))
        elif args.action == 'prepare':
            plan = prepare(args.snapshot, args.xinput_baseline, args.ledger, args.out, pb)
            print(json.dumps({'status': 'OFFLINE PREVIEW ONLY', 'planSha256': sha((args.out/'plan.json').read_bytes()),
                              'frameSha256': plan['frameSha256'], 'current': CURRENT, 'target': TARGET}))
        else:
            print(json.dumps(execute(args.plan, args.approval, args.uf2, args.exclusive_configurator_session, pb)))
        return 0
    except Exception as error:
        print('managed USB restore: '+str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
