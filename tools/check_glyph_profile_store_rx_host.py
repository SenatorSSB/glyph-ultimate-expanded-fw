#!/usr/bin/env python3
"""Offline retained-RX evidence and actual POSIX writer proof; opens no device."""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import select
import subprocess
import tempfile
from unittest.mock import patch
import glyph_profile_store_candidate_tool as candidate
import glyph_serial_config_tool as transport

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'tools/fixtures/profile_store_rx_host'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    for entry in json.loads((FIX / 'manifest.json').read_text()):
        data = (FIX / entry['file']).read_bytes()
        require(len(data) == entry['bytes'] and sha(data) == entry['sha256'], 'immutable evidence: ' + entry['file'])
    pb, json_format, _ = transport.load_runtime_proto_modules(ROOT)
    receipt = json.loads((FIX / 'receipt.json').read_text())
    payload = bytes.fromhex(receipt['request_hex'])
    request = pb.ProfileStoreRequest.FromString(payload)
    wire = transport.cobs_encode(bytes([9]) + payload)
    require(payload == (FIX / 'physical-update.pb').read_bytes(), 'receipt protobuf bytes')
    require(wire == (FIX / 'physical-update.cobs').read_bytes(), 'receipt COBS bytes')
    require(len(payload) == 3074 and len(wire) == 3089, 'physical sizes')
    require(sha(payload) == receipt['request_sha256'], 'receipt protobuf hash')
    require(json_format.MessageToDict(request, preserving_proto_field_name=True) == receipt['decoded_request'], 'receipt decoded fields')
    require(request.operation == pb.PROFILE_STORE_UPDATE and request.profile_id == 22 and request.fault_ticket == 1 and not request.liveness_trace, 'ticketed untraced physical UPDATE')
    rows = [json.loads(line) for line in (FIX / 'mutation.trace.jsonl').read_text().splitlines()]
    rows = [row for row in rows if row['phase'] == 'update']
    attempt = next(row for row in rows if row['event'] == 'transmit_attempt')
    complete = next(row for row in rows if row['event'] == 'transmitted')
    require(attempt['request_hex'] == payload.hex() and attempt['wire_bytes'] == len(wire) and attempt['wire_sha256'] == sha(wire), 'receipt matches actual host transmit journal')
    chunks = [row for row in rows if row['event'] == 'receive_chunk']
    received = b''.join(bytes.fromhex(row['chunk_hex']) for row in chunks)
    require(len(chunks) == 1 and len(received) == 30 and received.count(b'\0') == 1, 'only complete error frame received')
    require(transport.cobs_decode(received) == bytes([transport.CMD_ERROR]) + b'Profile store frame timeout', 'normal CMD_ERROR')
    require(not any(row['event'] in ('device_stage', 'response') for row in rows), 'no liveness/ProfileStore frames')
    elapsed_ns = chunks[0]['monotonic_ns'] - complete['monotonic_ns']
    require(elapsed_ns == 5000585375, 'physical elapsed time')
    for filename in ('arm.json', 'pending-status.json'):
        response = pb.ProfileStoreResponse()
        json_format.ParseDict(json.loads((FIX / filename).read_text())['response'], response)
        require(response.storage_fault_pending and response.storage_fault_ticket == 1 and not response.storage_fault_armed and not response.storage_fault_triggered, 'pending fault remains inert in retained response')
    # Execute the exact frozen method, then the current method, against an ideal
    # OS sink. Every successful short write must advance by exactly its count.
    namespace = {'os': os, 'select': select, 'ToolError': transport.ToolError}
    exec(compile((FIX / 'write_all_895.py').read_text(), str(FIX / 'write_all_895.py'), 'exec'), namespace)
    variants = {'frozen_895': namespace['write_all'], 'candidate': transport.PosixSerialPort.write_all}
    tests = []
    for label, writer in variants.items():
        for limit in (1, 63, 64, 65, 127, 128, 255, 256, 257, 512, 3089):
            sink = bytearray()
            port = transport.PosixSerialPort('UNOPENED', 115200, 1)
            port.fd = -999
            def write(fd, data):
                require(bytes(data) == wire[len(sink):], 'writer changed or skipped suffix')
                count = min(limit, len(data)); sink.extend(data[:count]); return count
            with patch.object(transport.select, 'select', return_value=([], [-999], [])), patch.object(transport.os, 'write', write):
                writer(port, wire)
            decoded = transport.cobs_decode(bytes(sink))
            require(decoded == bytes([9]) + payload, 'complete exact ideal COBS receiver')
            require(pb.ProfileStoreRequest.FromString(decoded[1:]) == request, 'exact ideal protobuf decode')
            tests.append({'writer': label, 'maximum_os_write': limit, 'accepted': len(sink), 'exact_frame_decode': True})
        # EINTR/EAGAIN are deliberately not claimed to be retried: the frozen
        # method propagates them. Verify no false completion or silent prefix.
        for exception in (InterruptedError, BlockingIOError):
            sink = bytearray(); calls = [0]
            def interrupted(fd, data):
                calls[0] += 1
                if calls[0] == 1:
                    sink.extend(data[:64]); return 64
                raise exception('offline injected write interruption')
            with patch.object(transport.select, 'select', return_value=([], [-999], [])), patch.object(transport.os, 'write', interrupted):
                try:
                    writer(port, wire)
                except exception:
                    pass
                else:
                    raise AssertionError('interrupted write incorrectly reported completion')
            require(bytes(sink) == wire[:64], 'interrupted prefix exact')
        for unavailable, count in ((True, 0), (False, 0), (False, -1)):
            with patch.object(transport.select, 'select', return_value=([], [] if unavailable else [-999], [])), patch.object(transport.os, 'write', return_value=count):
                try:
                    writer(port, wire)
                except transport.ToolError:
                    pass
                else:
                    raise AssertionError('no-progress write incorrectly reported completion')
    # Actual candidate.request delegates framing and transmission to the same
    # writer. Its transmitted event must occur only after all bytes are accepted.
    for exception in (None, InterruptedError, BlockingIOError):
        sink = bytearray(); events = []; calls = [0]
        port = transport.PosixSerialPort('UNOPENED', 115200, 1); port.fd = -999
        response = pb.ProfileStoreResponse(protocol_version=2, request_token=request.request_token, status=pb.PROFILE_STORE_OK)
        reply = transport.cobs_encode(bytes([9]) + response.SerializeToString(deterministic=True))
        def write(fd, data):
            calls[0] += 1
            if exception is not None and calls[0] == 2:
                raise exception('offline injected write interruption')
            count = min(65, len(data)); sink.extend(data[:count]); return count
        def event(phase, state, **fields):
            if state == 'transmitted':
                require(bytes(sink) == wire, 'event emitted before complete OS acceptance')
            events.append(state)
        def ready(readable, writable, errors, timeout):
            return (readable, writable, [])
        with patch.object(candidate, 'event', event), patch.object(transport.select, 'select', ready), patch.object(transport.os, 'write', write), patch.object(transport.os, 'read', return_value=reply), contextlib.redirect_stderr(io.StringIO()):
            try:
                result = candidate.request(port, pb, request, exact_payload=payload, phase='update')
            except (InterruptedError, BlockingIOError):
                require(exception is not None, 'unexpected write interruption')
            else:
                require(exception is None and result == response, 'exact candidate response')
        require(('transmitted' in events) == (exception is None), 'no false transmitted event on exception')
    with tempfile.TemporaryDirectory(prefix='glyph-rx-host-') as directory:
        executable = Path(directory) / 'pending'
        subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation', '-DGLYPH_STRICT_HARDENING_CANDIDATE=1', '-I' + str(ROOT / 'include'), str(FIX / 'fault_pending.cpp'), '-o', str(executable)], check=True)
        subprocess.run([str(executable)], check=True)
    report = {'result': 'PASS', 'physical_boundary': 'LARGE_UPDATE_WIRE_TRANSMITTED_DEVICE_FRAME_READER_TIMED_OUT', 'request_bytes': len(payload), 'wire_bytes': len(wire), 'request_sha256': sha(payload), 'wire_sha256': sha(wire), 'received_bytes': len(received), 'error_wire_sha256': sha(received), 'elapsed_after_os_write_ns': elapsed_ns, 'write_matrix': tests, 'exception_cases': 'EINTR/EAGAIN propagate; no transmitted event; no zero-progress success', 'pending_fault_hook_attempts': 10000, 'device_actions': 'NONE', 'scope': 'Host OS acceptance and ideal exact receiver only; physical USB receipt is not inferred'}
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
