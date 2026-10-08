#!/usr/bin/env python3
"""Prepare the owner-approved block-11 repair offline. No device transport."""
from __future__ import annotations

import argparse
import base64
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'tools/fixtures/gp_config012_button_host/schema/config.proto'
SCHEMA_SHA256 = '2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b'
TARGETS = (1, 2, 3, 33, 17, 18, 21, 22, 41, 49, 5)
RGB_ERROR = 'Config contains an invalid RGB target'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(path):
    path = Path(path)
    require(not path.is_symlink() and stat.S_ISREG(path.stat().st_mode),
            'Expected a regular nonsymlink file: ' + str(path))
    return path.read_bytes()


def git(*args):
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=False)
    require(result.returncode == 0, 'Git verification failed: ' + result.stderr.decode())
    return result.stdout


def load_codec():
    """Use the existing protobuf Python generator, with the authenticated schema."""
    schema = ROOT / SCHEMA
    require(digest(regular(schema)) == SCHEMA_SHA256, 'Schema identity mismatch')
    from google.protobuf import json_format
    import google.protobuf
    with tempfile.TemporaryDirectory(prefix='glyph-c022-codec-') as temporary:
        result = subprocess.run(
            [sys.executable, '-m', 'grpc_tools.protoc', '--proto_path=' + str(schema.parent),
             '--python_out=' + temporary, str(schema)], capture_output=True, check=False)
        require(result.returncode == 0 and not result.stderr,
                'Existing protobuf generation failed: ' + result.stderr.decode())
        spec = importlib.util.spec_from_file_location('glyph_c022_config_pb2',
                                                     Path(temporary) / 'config_pb2.py')
        require(spec is not None and spec.loader is not None, 'Generated module unavailable')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module, json_format, google.protobuf.__version__


def artifact_for(message, json_format):
    return json_format.MessageToDict(message, preserving_proto_field_name=False,
                                    use_integers_for_enums=False)


def encode_artifact(artifact, module, json_format):
    message = module.Config()
    json_format.ParseDict(artifact, message, ignore_unknown_fields=False)
    return message.SerializeToString(deterministic=True)


def correct_legacy_block11(message, module):
    """Accept only the identified 11-target block plus nine empty tail records."""
    require(len(message.rgb_configs) >= 11, 'RGB block 11 is absent')
    block = message.rgb_configs[10]
    require(len(block.button_colors) == 20, 'Expected the identified 20-record block 11')
    require(tuple(int(row.button) for row in block.button_colors[:11]) == TARGETS,
            'The eleven retained target identities/order differ from the approved block')
    require(all(int(row.button) == 0 and row.color == 0 for row in block.button_colors[11:]),
            'The nine trailing records are not empty zero/zero records')
    corrected = module.Config()
    corrected.CopyFrom(message)
    del corrected.rgb_configs[10].button_colors[11:]
    corrected.rgb_configs[10].button_colors[0].color = 0
    restored = module.Config()
    restored.CopyFrom(corrected)
    restored.rgb_configs[10].CopyFrom(message.rgb_configs[10])
    require(restored == message, 'An unrelated Config field changed')
    require(all(a == b for a, b in zip(block.button_colors[1:11],
                                      corrected.rgb_configs[10].button_colors[1:])),
            'Another retained mapping changed')
    table = []
    for index, row in enumerate(block.button_colors[:11]):
        table.append({'record': index + 1,
                      'target': module.Button.Name(int(row.button)),
                      'before_stored_color': int(row.color),
                      'before_effective_source_inferred_color': 0 if index == 0 else int(row.color),
                      'after_color': int(corrected.rgb_configs[10].button_colors[index].color),
                      'physical_observation': 'NOT_TESTED'})
    for index in range(11, 20):
        table.append({'record': index + 1, 'target': 0, 'before_color': 0,
                      'after': 'STRUCTURALLY_ABSENT'})
    return corrected, table


def structural_diff(before, after, path=''):
    result = []
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(before.keys() | after.keys()):
            child = path + '/' + key
            if key not in before:
                result.append({'path': child, 'operation': 'add', 'after': after[key]})
            elif key not in after:
                result.append({'path': child, 'operation': 'remove', 'before': before[key]})
            else:
                result.extend(structural_diff(before[key], after[key], child))
    elif isinstance(before, list) and isinstance(after, list):
        for index in range(max(len(before), len(after))):
            child = path + '/' + str(index)
            if index >= len(before):
                result.append({'path': child, 'operation': 'add', 'after': after[index]})
            elif index >= len(after):
                result.append({'path': child, 'operation': 'remove', 'before': before[index]})
            else:
                result.extend(structural_diff(before[index], after[index], child))
    elif before != after:
        result.append({'path': path, 'operation': 'replace', 'before': before, 'after': after})
    return result


def hexdump(raw):
    return [f'{offset:08x}  {raw[offset:offset + 16].hex(" ")}\n'
            for offset in range(0, len(raw), 16)]


def authenticate_validator(proof, candidate):
    require(re.fullmatch('[0-9a-f]{40}', candidate) is not None, 'Full candidate SHA required')
    require(git('rev-parse', 'HEAD').decode().strip() == candidate,
            'Run from the exact candidate checkout')
    record = proof['raw_validator']
    binary = Path(record['path'])
    require(digest(regular(binary)) == record['sha256'], 'Validator binary hash mismatch')
    pins = record['source_pins']
    required = {'src/core/config_rgb_target_validation.cpp',
                'config/glyph/common/src/glyph_config_validation.cpp',
                'src/core/config_validation.cpp', 'src/core/config_button_validation.cpp',
                'config/glyph/common/include/config_rgb_target_domain.hpp',
                'config/glyph/glyph_mk6/include/neopixel_definitions.hpp'}
    require(required <= set(pins), 'Validator provenance omits required source dependencies')
    for path, expected in pins.items():
        require(not Path(path).is_absolute() and '..' not in Path(path).parts,
                'Unsafe provenance path')
        require(digest(regular(ROOT / path)) == expected, 'Live validator source mismatch: ' + path)
        require(digest(git('show', candidate + ':' + path)) == expected,
                'Committed validator source mismatch: ' + path)
        entry = git('ls-tree', candidate, '--', path).decode().split()
        require(entry[:2] == ['100644', 'blob'], 'Nonregular validator source: ' + path)
    return binary, record


def validate_raw(binary, path):
    result = subprocess.run([str(binary), '--config-raw', str(path)],
                            capture_output=True, text=True, check=False)
    require(not result.stderr, 'Validator emitted diagnostics: ' + result.stderr)
    value = json.loads(result.stdout)
    require(type(value.get('accepted')) is bool and type(value.get('decoded')) is bool,
            'Malformed validator response')
    require(result.returncode == (0 if value['accepted'] else 1 if value['decoded'] else 2),
            'Validator status disagrees with its response')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--candidate-sha', required=True)
    parser.add_argument('--validator-proof', required=True, type=Path)
    parser.add_argument('--sample-kind', required=True, choices=('archived', 'fresh-owner'))
    args = parser.parse_args()
    backup_raw = regular(args.backup)
    backup = json.loads(backup_raw)
    require(isinstance(backup.get('config'), dict), 'Complete existing backup wrapper required')
    raw = base64.b64decode(backup['rawConfigPayloadBase64'], validate=True)
    require(raw, 'Empty original payload')
    module, json_format, version = load_codec()
    original = module.Config()
    original.ParseFromString(raw)
    original_artifact = artifact_for(original, json_format)
    require(original.SerializeToString(deterministic=True) == raw,
            'Original decode/reencode is not byte-exact')
    require(encode_artifact(original_artifact, module, json_format) == raw,
            'Original JSON restoration cannot reproduce every raw byte')
    require(encode_artifact(backup['config'], module, json_format) == raw,
            'Backup decoded Config differs from its raw payload')
    corrected, table = correct_legacy_block11(original, module)
    corrected_artifact = artifact_for(corrected, json_format)
    # Protobuf omits default scalar values on the wire; the artifact explicitly
    # states black so no caller can mistake an omitted color for a cyan policy.
    corrected_artifact['rgbConfigs'][10]['buttonColors'][0]['color'] = 0
    corrected_raw = corrected.SerializeToString(deterministic=True)
    require(encode_artifact(corrected_artifact, module, json_format) == corrected_raw,
            'Corrected artifact/raw roundtrip mismatch')
    proof_raw = regular(args.validator_proof)
    binary, validator = authenticate_validator(json.loads(proof_raw), args.candidate_sha)
    require(not args.output_dir.exists(), 'Output directory must be new; no artifact overwrite')
    args.output_dir.mkdir(parents=True)
    output = args.output_dir.resolve()
    (output / 'original.raw').write_bytes(raw)
    (output / 'corrected.raw').write_bytes(corrected_raw)
    observed_original = validate_raw(binary, output / 'original.raw')
    observed_corrected = validate_raw(binary, output / 'corrected.raw')
    require(observed_original == {'accepted': False, 'decoded': True, 'error': RGB_ERROR},
            'Original does not have only the expected RGB semantic rejection')
    require(observed_corrected['accepted'] and observed_corrected['decoded'],
            'Corrected Config is rejected by exact candidate validation')
    artifacts = {'original.json': original_artifact, 'corrected.json': corrected_artifact,
                 'restoration.json': original_artifact, 'before-after-block11.json': table,
                 'semantic-diff.json': structural_diff(original_artifact, corrected_artifact)}
    for name, value in artifacts.items():
        (output / name).write_text(json.dumps(value, indent=2) + '\n')
    (output / 'raw-diff.txt').write_text(''.join(difflib.unified_diff(
        hexdump(raw), hexdump(corrected_raw), fromfile='original.raw', tofile='corrected.raw',
        n=max(len(raw), len(corrected_raw)))))
    restored_raw = encode_artifact(json.loads((output / 'restoration.json').read_text()),
                                   module, json_format)
    require(restored_raw == raw, 'Restoration artifact is not byte-exact')
    files = {p.name: {'path': str(p), 'size': p.stat().st_size, 'sha256': digest(p.read_bytes())}
             for p in output.iterdir() if p.is_file()}
    packet = {'schema_name': 'glyph_c022_offline_compatibility_packet', 'schema_version': 1,
              'candidate_git_sha': args.candidate_sha, 'sample_kind': args.sample_kind,
              'freshness_requires_owner_provenance_review': True,
              'backup': {'path': str(args.backup.resolve()), 'sha256': digest(backup_raw)},
              'schema_sha256': SCHEMA_SHA256, 'protobuf_version': version,
              'validator_proof_sha256': digest(proof_raw), 'raw_validator': validator,
              'original': files['original.raw'], 'corrected_artifact': files['corrected.json'],
              'corrected_raw': files['corrected.raw'], 'restoration_artifact': files['restoration.json'],
              'expected_restored_raw': {'size': len(raw), 'sha256': digest(raw)},
              'original_decode_reencode_byte_exact': True, 'restoration_byte_exact': True,
              'all_unrelated_fields_semantically_equal': True,
              'original_validation': observed_original, 'corrected_validation': observed_corrected,
              'files': files, 'independent_review': 'REQUIRED_BEFORE_OWNER_USE',
              'device_or_Config_write_authorized': False, 'physical_appearance': 'NOT_TESTED'}
    (output / 'packet.json').write_text(json.dumps(packet, indent=2) + '\n')
    print(json.dumps({'packet': str(output / 'packet.json'),
                      'independent_review': 'REQUIRED_BEFORE_OWNER_USE', 'device_access': False}))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        print('C022 compatibility preparation refused: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
