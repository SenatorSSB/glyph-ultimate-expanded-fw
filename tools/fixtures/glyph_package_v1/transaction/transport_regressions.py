"""Exercise real package-enabled backend routing and durable Config refresh."""
from pathlib import Path
import json, os, struct, subprocess


def transport_regressions(binary, repo, corpus, out, base, model, fixtures, package_pb, strict_response):
    # Caller already configured model's immutable source validators, exactly as
    # the existing transaction regressions main does. No new oracle framework.
    from run import dump_namespace, load_namespace
    import config_pb2 as config_pb
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, 'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1',
           'ASAN_OPTIONS': 'detect_leaks=0'}
    results = []

    def var(value):
        raw = bytearray()
        while value > 127:
            raw.append((value & 127) | 128)
            value >>= 7
        raw.append(value)
        return bytes(raw)

    def invoke(*args):
        command = [str(binary), *map(str, args)]
        process = subprocess.run(command, capture_output=True, text=True, env=env)
        if process.returncode:
            raise RuntimeError(' '.join(command) + '\n' + process.stdout + process.stderr)

    def status(token):
        return package_pb.PackageEnvelope(protocol_version=3, request_token=token,
                                          operation=1).SerializeToString(deterministic=True)

    def query(token, digest, incarnation=42):
        return package_pb.PackageEnvelope(protocol_version=3, request_token=token,
            operation=16, expected_store_incarnation=incarnation,
            expected_digest=digest).SerializeToString(deterministic=True)

    def cobs_frames(raw):
        """Independent bounded decode of actual transport output, retaining frame extents."""
        assert not raw or raw[-1] == 0, 'unterminated actual response'
        decoded = []
        for encoded in raw.split(b'\0')[:-1]:
            # No response TX fault is injected in these cases. Extra delimiter
            # packets or an empty frame therefore indicate an integration bug.
            assert encoded, 'unexpected empty actual frame'
            at = 0
            data = bytearray()
            while at < len(encoded):
                code = encoded[at]
                at += 1
                assert code and at + code - 1 <= len(encoded), 'invalid COBS extent'
                data += encoded[at:at + code - 1]
                at += code - 1
                if code != 255 and at < len(encoded):
                    data.append(0)
            assert data and data[0] == 9, 'actual response command must be9'
            decoded.append((bytes(data[1:]), len(encoded) + 1))
        return decoded

    def receipt_absent(response):
        assert not (response.profile_id or response.profile_revision or
            response.transaction_operation or response.HasField('row_index') or
            response.rgb_index or response.HasField('semantic_digest') or
            response.HasField('config_sha') or response.HasField('record_sha') or
            response.record_publication_generation), 'refusal must omit complete receipt'

    def case(name, requests, expected, disk=None, wanted_disk=None,
             package=True, zero_write=True):
        # expected rows: (token, operation, expected status). None status means
        # only closed shape+identity are known, never an implicit success claim.
        work = out / name
        work.mkdir(exist_ok=False)
        disk = base if disk is None else disk
        wanted_disk = disk if wanted_disk is None else wanted_disk
        dump_namespace(disk, work / 'seed.namespace')
        invoke('seed', work / 'seed.namespace', work / 'seed.nor')
        packed = bytearray(struct.pack('<I', len(requests)))
        for request in requests:
            packed += struct.pack('<I', len(request)) + request
        (work / 'requests.bin').write_bytes(packed)
        invoke('transport', work / 'seed.nor', work / 'requests.bin', work)
        frames = cobs_frames((work / 'responses.cobs').read_bytes())
        assert len(frames) == len(expected), (name, 'actual response count', len(frames), len(expected))
        responses = []
        for (raw, framed_bytes), (token, operation, expected_status) in zip(frames, expected):
            if package:
                response = strict_response(raw, operation)
                assert framed_bytes <= (102 if operation == 1 else 231), 'actual response frame bound'
            else:
                response = config_pb.ProfileStoreResponse.FromString(raw)
                assert response.protocol_version == 2, 'eligible legacy protocol preserved'
            assert response.request_token == token, (name, 'correlation token')
            if expected_status is not None:
                assert response.status == expected_status, (name, response.status, expected_status)
            responses.append(response)
        observed = load_namespace(work / 'namespace.bin')
        assert observed == wanted_disk, (name, 'complete final namespace')
        # Encoding the backend saved snapshot must match the exact current
        # durable body, not merely its CRC/generation or selected field subset.
        assert (work / 'saved-config.pb').read_bytes() == observed['/config-v2.bin'][8:], (name, 'saved Config refresh')
        summary = json.loads((work / 'transport.json').read_text())
        assert summary['active_unchanged'] and summary['no_handles'], (name, summary)
        if zero_write:
            assert summary['programs'] == summary['erases'] == 0 and summary['unchanged'], (name, summary)
            assert (work / 'after.nor').read_bytes() == (work / 'seed.nor').read_bytes(), (name, 'NOR unchanged')
        results.append({'name': 'transport-' + name, 'responses': len(responses),
            'closed_package_responses': package, 'zero_nor_writes': zero_write,
            'exact_namespace': True, 'saved_Config_equals_durable_body': True,
            'active_unchanged': True, 'no_handles': True})
        return responses, work

    states, plan = fixtures.package_plan(base, True, 100)
    template = package_pb.PackageEnvelope.FromString(plan['request'])
    # Group1: actual protocol3 STATUS/unknown QUERY, no package/writer side effect.
    responses, _ = case('status-query', [status(900), query(101, bytes(32)), status(901)],
                        [(900, 1, 1), (101, 16, 4), (901, 1, 1)])
    for response in responses:
        receipt_absent(response)
        assert not response.write_fenced and response.storage_floor == 1
        assert response.transaction_token_high_water == 0

    # Group2: trustworthy outer correlation, invalid payload. Keep exact valid
    # baseline guards so source-invalid bodies do not stop first on guard drift.
    malformed = {}
    for label, payload in [
        ('unknown-nested-package', template.package_body + var(7 << 3) + var(1)),
        ('duplicate-nested-version', b'\x08\x01' + template.package_body),
    ]:
        request = package_pb.PackageEnvelope()
        request.CopyFrom(template)
        request.package_body = payload
        malformed[label] = request.SerializeToString(deterministic=True)
    request = package_pb.PackageEnvelope()
    request.CopyFrom(template)
    request.expected_config_sha256 = b'X' * 31
    malformed['sha31'] = request.SerializeToString(deterministic=True)
    # Rebind ONLY guards/token to the actual baseline while preserving the
    # exact frozen semantic-invalid PackageBody bytes. This prevents a stale
    # maximum-width guard from returning CONFLICT before source validation.
    frozen_negatives = json.loads((Path(corpus) / 'wire/negative-vectors.json').read_text())
    for name in ['invalid GNP5', 'native context mismatch']:
        frozen = next(row for row in frozen_negatives['cases'] if row['name'] == name)
        source_request = package_pb.PackageEnvelope.FromString(bytes.fromhex(frozen['request']))
        request = package_pb.PackageEnvelope()
        request.CopyFrom(template)
        request.package_body = source_request.package_body
        malformed['frozen-source-' + name.replace(' ', '-')] = request.SerializeToString(deterministic=True)
    for label, raw in malformed.items():
        responses, _ = case(label, [raw, status(901)], [(100, 15, 2), (901, 1, 1)])
        for response in responses:
            receipt_absent(response)
            assert response.transaction_token_high_water == 0
        assert responses[0].logical == 0 and not responses[0].write_fenced

    # Group3: no trustworthy canonical outer header => drop. Next frame's sole
    # response proves packet ownership did not discard following input.
    raw = plan['request']
    token = b'\x10' + var(100)
    assert raw.startswith(b'\x08\x03' + token)
    untrusted = {
        'unknown-outer': raw + var(27 << 3) + var(1),
        'duplicate-token': raw[:2] + token + raw[2:],
        'nonminimal-key': b'\x88\x00' + raw[1:],
        'truncated-outer': raw[:-1],
        'missing-token': raw[:2] + raw[2 + len(token):],
    }
    for label, bad in untrusted.items():
        responses, _ = case(label, [bad, status(901)], [(901, 1, 1)])
        receipt_absent(responses[0])
        assert responses[0].transaction_token_high_water == 0

    # Group4: any v3 occurrence prevents legacy fallback, including a v2 final
    # occurrence that ordinary legacy protobuf last-value decoding would retain.
    native = package_pb.PackageBody.FromString(template.package_body).native_body
    legacy = config_pb.ProfileStoreRequest(protocol_version=2, request_token=200,
        operation=4, expected_store_generation=7, expected_store_incarnation=42,
        name='Legacy candidate')
    legacy.profile.schema_version = 5
    legacy.profile.native_payload = native
    legacy_bytes = legacy.SerializeToString(deterministic=True)
    assert legacy_bytes.startswith(b'\x08\x02')
    for label, mixed in {
        'v3-before-v2': b'\x08\x03' + legacy_bytes,
        'v3-after-v2': legacy_bytes[:2] + b'\x08\x03' + legacy_bytes[2:],
        'nonminimal-v3-before-v2': b'\x08\x83\x00' + legacy_bytes,
    }.items():
        responses, _ = case(label, [mixed, status(901)], [(901, 1, 1)])
        assert responses[0].transaction_token_high_water == 0
    # Eligible legacy read-only request still uses the actual same backend.
    legacy_status = config_pb.ProfileStoreRequest(protocol_version=2, request_token=902, operation=1)
    case('eligible-legacy-status', [legacy_status.SerializeToString(deterministic=True)],
         [(902, 1, 1)], package=False)

    # Group5: real CREATE + QUERY + STATUS concatenated; installation bytes are
    # identical to frozen complete model, and saved snapshot refreshes exactly.
    responses, _ = case('create-query-status', [status(900), plan['request'],
        query(100, plan['intent']['digest']), status(901)],
        [(900, 1, 1), (100, 15, 1), (100, 16, 1), (901, 1, 1)],
        wanted_disk=states['COMMITTED'], zero_write=False)
    for response in responses[1:3]:
        assert response.logical == 3 and not response.write_fenced and response.storage_floor == 2
        assert response.profile_id == plan['intent']['id'] and response.profile_revision == 1
        assert response.row_index == plan['intent']['row'] and response.HasField('row_index')
        assert response.rgb_index == plan['intent']['rgb'] and response.record_publication_generation == plan['intent']['publication_generation']
        assert response.semantic_digest == plan['intent']['digest']
        assert response.record_sha == model.sha(plan['record'])
        assert response.config_sha == model.sha(states['COMMITTED']['/config-v2.bin'][8:])
    receipt_absent(responses[-1])
    assert responses[-1].transaction_token_high_water == 100

    # Group6: immutable exact source-valid framing witness. Its deliberately
    # maximum guards conflict with this small baseline; allocation success is
    # neither expected nor needed to establish routing and actual COBS framing.
    maximum = json.loads((Path(corpus) / 'wire/max-frame-vector.json').read_text())
    maximum_request = bytes.fromhex(maximum['request'])
    maximum_token = package_pb.PackageEnvelope.FromString(maximum_request).request_token
    _, work = case('maximum-source-witness', [maximum_request, status(901)],
                   [(maximum_token, 15, 6), (901, 1, 1)])
    actual_requests = (work / 'requests.cobs').read_bytes()
    frozen_frame = bytes.fromhex(maximum['frame'])
    assert len(frozen_frame) == maximum['framed_bytes'] == 4580
    assert actual_requests.startswith(frozen_frame), 'real PacketIO exact maximum witness'
    assert actual_requests[:actual_requests.index(b'\0') + 1] == frozen_frame
    results[-1]['exact_max_request_COBS_bytes'] = 4580
    (out / 'transport-results.json').write_text(json.dumps(results, indent=2) + '\n')
    return results
