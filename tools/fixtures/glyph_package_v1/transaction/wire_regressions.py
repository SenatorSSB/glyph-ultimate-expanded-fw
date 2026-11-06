"""Bind the frozen request corpus to actual production request/body decoders."""
from pathlib import Path
import hashlib, json, os, struct, subprocess


def wire_regressions(binary, corpus, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    wire = Path(corpus) / 'wire'
    vectors = json.loads((wire / 'vectors.json').read_text())
    negatives = json.loads((wire / 'negative-vectors.json').read_text())
    maximum = json.loads((wire / 'max-frame-vector.json').read_text())
    assert len(vectors) == 4 and len(negatives['cases']) == 62
    # The strict retained parser combines wire and source-native/context
    # acceptance. Production wire decode deliberately defers these TWO cases.
    deferred = {'invalid GNP5', 'native context mismatch'}
    assert deferred <= {row['name'] for row in negatives['cases']}
    cases = []
    for row in vectors:
        cases.append({'name': 'positive/' + row['name'],
            'request': row['request'], 'expected_request': True,
            'expected_body': row['name'] != 'query',
            'body_attempted': row['name'] != 'query'})
    cases.append({'name': 'positive/exact-framed-maximum',
        'request': maximum['request'], 'expected_request': True,
        'expected_body': True, 'body_attempted': True})
    for row in negatives['cases']:
        native_deferred = row['name'] in deferred
        cases.append({'name': 'negative/' + row['name'],
            'request': row['request'], 'expected_request': native_deferred,
            'expected_body': native_deferred, 'body_attempted': native_deferred,
            'source_validation_required': native_deferred})
    # negative_vectors.py constructs its retained740 prefixes from
    # envelope(encode(body())): exactly vectors.json's rgb request.
    rgb = next(row for row in vectors if row['name'] == 'rgb')
    request = bytes.fromhex(rgb['request'])
    assert len(request) == negatives['all_prefix_truncations_rejected'] == 740
    for size in range(len(request)):
        cases.append({'name': 'rgb-prefix/' + str(size),
            'request': request[:size].hex(), 'expected_request': False,
            'expected_body': False, 'body_attempted': False})
    assert len(cases) == 807
    packed = bytearray(struct.pack('<I', len(cases)))
    for case in cases:
        raw = bytes.fromhex(case['request'])
        packed += struct.pack('<I', len(raw)) + raw
    (out / 'requests.bin').write_bytes(packed)
    (out / 'inventory.json').write_text(json.dumps(cases, indent=2) + '\n')
    command = [str(binary), 'wire-requests', str(out / 'requests.bin'), str(out / 'actual.json')]
    process = subprocess.run(command, capture_output=True, text=True,
        env={**os.environ, 'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1',
             'ASAN_OPTIONS': 'detect_leaks=0'})
    (out / 'invocation.json').write_text(json.dumps({'argv': command,
        'exit_status': process.returncode, 'stdout': process.stdout,
        'stderr': process.stderr}, indent=2) + '\n')
    if process.returncode:
        raise RuntimeError(' '.join(command) + '\n' + process.stdout + process.stderr)
    actual = json.loads((out / 'actual.json').read_text())
    assert len(actual) == len(cases), ('actual wire inventory', len(actual), len(cases))
    for index, (case, result) in enumerate(zip(cases, actual)):
        assert result['index'] == index
        assert (result['canonical_request'], result['body_attempted'], result['canonical_body']) == (
            case['expected_request'], case['body_attempted'], case['expected_body']), (case['name'], result)
    summary = {'name': 'actual-production-wire-corpus', 'cases': len(cases),
        'frozen_positive_vectors': 4, 'exact_framed_maximum': 1,
        'frozen_negative_vectors': 62, 'retained_rgb_prefixes': 740,
        'wire_accepted': sum(row['canonical_request'] for row in actual),
        'wire_rejected': sum(not row['canonical_request'] for row in actual),
        'native_context_deferred_cases': sorted(deferred),
        'all_pass': True,
        'input_sha256': hashlib.sha256(packed).hexdigest(),
        'actual_sha256': hashlib.sha256((out / 'actual.json').read_bytes()).hexdigest()}
    assert summary['wire_accepted'] == 7 and summary['wire_rejected'] == 800
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return [summary]
