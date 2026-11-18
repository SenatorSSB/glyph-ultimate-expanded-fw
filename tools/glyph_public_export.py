#!/usr/bin/env python3
"""Deterministic tracked-tree export; never publishes or imports development Git history.

Use --report outside --output for the private, complete inventory. Normal export
fails on REVIEW_REQUIRED or unresolved licenses. --diagnostic-stage produces only
cleared files for fresh-root experiments, retaining those blockers in the report.
No tests, builds, Git initialization or device operations are run by this tool.
"""
from __future__ import annotations
import argparse
import collections
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import tempfile
from urllib.parse import unquote
import zlib

ROOT = Path(__file__).resolve().parents[1]
POLICY = 'tools/fixtures/glyph_public_export_policy.v1.json'
CLASSES = {'PUBLIC_INCLUDE', 'PUBLIC_INCLUDE_TRANSFORMED',
           'PUBLIC_EXCLUDE_HISTORICAL', 'PRIVATE_ARCHIVE_ONLY', 'REVIEW_REQUIRED'}
PUBLIC = {'PUBLIC_INCLUDE', 'PUBLIC_INCLUDE_TRANSFORMED'}
HISTORICAL = ('docs/agent_framework/', 'docs/project/', 'docs/planning/',
              'docs/calibration/', 'docs/archive/', 'docs/maintenance/', 'docs/sources/raw/')
JOURNALS = {'docs/CURRENT_STATE.md': 'current-state-v1',
            'docs/ROADMAP.md': 'current-roadmap-v1'}
FORBIDDEN_COMPONENTS = {'.git', '.pio', '.platformio', '.platformio-home', '.venv',
                        '__pycache__', 'node_modules', '.pytest_cache', 'local_backups'}
BINARY_EXTENSIONS = {'.gz', '.pb', '.bin', '.body', '.cobs', '.png', '.uf2', '.elf', '.zip', '.a', '.o'}
PATTERNS = {
    'absolute_path': r'(?:(?<![A-Za-z0-9_])/(?:Users|home|root|Volumes|mnt|private|tmp|run/user|var/tmp|var/folders)/|\b[A-Za-z]:[\\/]|file://)',
    'contact': r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
    'backup_locator': r'local_backups[/\\][^\s`"\']*',
    'private_capture': r'private[-_ ](?:capture|artifact)[-_ ](?:path|locator|location)',
    'owner_local': r'rasmus' + r'\.pekkarinen|' + 'Personal' + r' code',
}

class ExportError(ValueError):
    pass

def fail(message):
    raise ExportError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            fail('duplicate JSON key: ' + key)
        result[key] = value
    return result

def path_ok(path):
    if (not isinstance(path, str) or not path or '\\' in path or '\x00' in path
            or PurePosixPath(path).is_absolute() or any(p in ('', '.', '..') for p in path.split('/'))
            or ':' in path or any(p.lower() in FORBIDDEN_COMPONENTS for p in path.split('/'))):
        fail('unsafe/cache/output path: ' + str(path))
    return path

def load_policy(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs)
    if value.get('schema') != 'glyph_public_export_policy.v1':
        fail('unknown policy schema')
    for rule in value['rules']:
        if set(rule) != {'prefix', 'classification', 'purpose'} or rule['classification'] not in CLASSES:
            fail('invalid prefix rule')
        path_ok(rule['prefix'].rstrip('/'))
    prefixes = [r['prefix'] for r in value['rules']]
    if len(prefixes) != len(set(prefixes)):
        fail('duplicate prefix rule')
    # Prefix classes must be disjoint. Only exact, documented exceptions override.
    if any(a != b and b.startswith(a) for a in prefixes for b in prefixes):
        fail('overlapping prefix rules')
    for path, record in value['exceptions'].items():
        path_ok(path)
        if record['classification'] not in CLASSES or not record.get('purpose'):
            fail('invalid exact exception: ' + path)
    return value

def classify(path, data, policy):
    path_ok(path)
    exact = policy['exceptions'].get(path)
    if exact:
        result = exact['classification']
    else:
        matches = [r for r in policy['rules'] if path.startswith(r['prefix'])]
        if len(matches) != 1:
            fail('unclassified or ambiguous tracked path: ' + path)
        result = matches[0]['classification']
        if path.startswith(('docs/agent_framework/', 'docs/project/')) or path in ('docs/AGENT_CONTEXT.md', 'docs/WORKFLOW.md'):
            result = 'PRIVATE_ARCHIVE_ONLY'
        # All compressed/binary material defaults to deny, including new fixtures.
        if Path(path).suffix.lower() in BINARY_EXTENSIONS or not is_text(data):
            result = 'PUBLIC_EXCLUDE_HISTORICAL'
    if result in PUBLIC:
        if path.startswith(HISTORICAL) and not (exact and exact.get('historical_exception')):
            fail('historical family leak: ' + path)
        if path in ('docs/AGENT_CONTEXT.md', 'docs/WORKFLOW.md'):
            fail('private workflow leak: ' + path)
        if binary(path, data) and path not in policy['binary_records']:
            fail('binary inclusion without exact record: ' + path)
    return result

def is_text(data):
    try:
        data.decode('utf-8')
        return b'\0' not in data
    except UnicodeError:
        return False

def binary(path, data):
    return Path(path).suffix.lower() in BINARY_EXTENSIONS or not is_text(data)

def transform(path, data):
    if path not in JOURNALS:
        fail('unapproved transform: ' + path)
    text = data.decode('utf-8')
    name = JOURNALS[path]
    start, end = f'<!-- {name}:start -->', f'<!-- {name}:end -->'
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) >= text.index(end):
        fail('missing/duplicate/misordered bounded section: ' + path)
    title, rest = text.split(start)
    if not re.fullmatch(r'# [^\n]+\s*', title):
        fail('unexpected preamble: ' + path)
    body = rest.split(end)[0]
    if 'legacy-' in body or 'Legacy chronological journal' in body or 'Legacy roadmap journal' in body:
        fail('legacy journal inside current section: ' + path)
    # Retain current boundaries so standalone navigation can verify this form.
    return (title.rstrip() + '\n\n' + start + body + end + '\n').encode('utf-8')

def privacy_hits(data):
    # Normalize encoded text as data, never evaluate Python/source code. Keep
    # every intermediate view, so decoding cannot hide a raw match. A bounded
    # fixed point also catches nested percent/JSON/hex escapes; excess encoding
    # depth fails closed instead of silently leaving an encoded locator.
    value = data.decode('utf-8', errors='replace')
    views = [value]
    def character(match):
        codepoint = int(match.group(1), 16)
        if codepoint > 0x10ffff: fail('invalid encoded codepoint')
        return chr(codepoint)
    for _ in range(8):
        decoded = unquote(value).replace('\\/', '/')
        decoded = re.sub(r'\\u([0-9a-fA-F]{4})', character, decoded)
        decoded = re.sub(r'\\U([0-9a-fA-F]{8})', character, decoded)
        decoded = re.sub(r'\\x([0-9a-fA-F]{2})', character, decoded)
        if decoded == value: break
        views.append(decoded); value = decoded
    else:
        fail('privacy normalization exceeds encoding-depth bound')
    text = '\n'.join(views)
    return sorted({(kind, m.group()) for kind, pattern in PATTERNS.items()
                   for m in re.finditer(pattern, text, re.I)})

def scan(path, data, policy):
    hits = privacy_hits(data)
    record = policy.get('privacy_exceptions', {}).get(path)
    if record:
        if digest(data) != record['sha256'] or not record.get('purpose'):
            fail('privacy exception fingerprint drift: ' + path)
        allowed = set(record['match_sha256'])
    else:
        allowed = set()
    # Owner-specific identifiers can never be excepted.
    unresolved = [h for h in hits if h[0] == 'owner_local' or digest((h[0] + ':' + h[1]).encode()) not in allowed]
    if unresolved:
        fail('privacy review required: ' + path + ': ' + ', '.join(sorted({h[0] for h in unresolved})))
    return {'result': 'PASS', 'reviewed_literal_matches': len(hits)}

def png_info(data):
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        fail('invalid PNG')
    pos, chunks, metadata = 8, [], []
    width = height = None
    while pos < len(data):
        if pos + 12 > len(data): fail('truncated PNG')
        size, = struct.unpack('>I', data[pos:pos+4])
        if size > 8 * 1024 * 1024 or pos + 12 + size > len(data): fail('oversize PNG chunk')
        kind = data[pos+4:pos+8]; payload = data[pos+8:pos+8+size]
        if zlib.crc32(kind + payload) & 0xffffffff != int.from_bytes(data[pos+8+size:pos+12+size], 'big'):
            fail('PNG CRC mismatch')
        chunks.append(kind.decode('ascii'))
        if kind == b'IHDR': width, height = struct.unpack('>II', payload[:8])
        if kind in (b'tEXt', b'iTXt', b'zTXt', b'iCCP', b'eXIf'):
            # New metadata formats are never silently cleared.
            if kind != b'tEXt': fail('unreviewed PNG metadata format')
            metadata.append(payload.replace(b'\0', b'=').decode('utf-8'))
        pos += 12 + size
        if kind == b'IEND': break
    if pos != len(data) or not chunks or chunks[-1] != 'IEND' or not width or not height:
        fail('invalid PNG termination/dimensions')
    return {'type': 'PNG', 'width': width, 'height': height, 'chunks': chunks, 'metadata': metadata}

def protobuf_wire(data):
    """Bounded generic wire inspection, including all length-delimited bytes.

    This does not substitute for a schema-specific decode; the exact schema and
    separately verified structural decoder are recorded in binary_records.
    """
    def varint(offset):
        value = 0
        for shift in range(0, 70, 7):
            if offset >= len(data): fail('truncated protobuf varint')
            byte = data[offset]; offset += 1; value |= (byte & 127) << shift
            if byte < 128: return value, offset
        fail('oversize protobuf varint')
    pos, fields = 0, []
    while pos < len(data):
        tag, pos = varint(pos); number, wire = tag >> 3, tag & 7
        if not number or number > 536870911: fail('invalid protobuf field')
        if wire == 0: _, pos = varint(pos)
        elif wire in (1, 5): pos += 8 if wire == 1 else 4
        elif wire == 2:
            size, pos = varint(pos); pos += size
        else: fail('unsupported protobuf wire type')
        if pos > len(data): fail('truncated protobuf field')
        fields.append([number, wire])
    return fields

def inspect_binary(path, data, policy):
    record = policy['binary_records'].get(path)
    if not record or record.get('sha256') != digest(data) or not record.get('consumer') or not record.get('purpose'):
        fail('missing/drifted binary evidence: ' + path)
    if len(data) > record.get('max_bytes', 8 * 1024 * 1024): fail('binary exceeds bound: ' + path)
    info = {'sha256': digest(data), 'consumer': record['consumer'], 'purpose': record['purpose']}
    suffix = Path(path).suffix.lower()
    if suffix == '.gz':
        # Read bytes only; gzip cannot choose any output filesystem path.
        limit = record['max_decompressed_bytes']
        if type(limit) is not int or not 0 < limit <= 8 * 1024 * 1024:
            fail('unsafe gzip expansion bound')
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
            unpacked = stream.read(limit + 1)
        if len(unpacked) > limit: fail('gzip expansion exceeds bound')
        if digest(unpacked) != record['decompressed_sha256']: fail('gzip expanded digest drift')
        scan(path, unpacked, policy)
        info['decompressed_sha256'] = digest(unpacked)
    elif suffix == '.png':
        info.update(png_info(data)); scan(path, '\n'.join(info['metadata']).encode(), policy)
    elif suffix == '.pb':
        if not record.get('schema') or not record.get('decoder'): fail('protobuf schema/decoder missing')
        info['wire_fields'] = protobuf_wire(data)
        scan(path, data, policy)
    else:
        if not record.get('format') or not record.get('decoder'): fail('binary format/decoder missing')
        scan(path, data, policy)
    return info

def tracked_tree(root, revision):
    listing = subprocess.check_output(['git', 'ls-tree', '-r', '-z', revision], cwd=root)
    entries = []
    for line in listing.split(b'\0'):
        if not line: continue
        head, rawpath = line.split(b'\t', 1); mode, kind, oid = head.decode().split()
        if kind != 'blob' or mode not in ('100644', '100755'): fail('non-regular tracked entry')
        entries.append((rawpath.decode('utf-8'), mode, oid))
    reader = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for path, mode, oid in sorted(entries):
            reader.stdin.write((oid + '\n').encode()); reader.stdin.flush()
            header = reader.stdout.readline().decode().split()
            if len(header) != 3 or header[:2] != [oid, 'blob']: fail('unreadable Git blob')
            data = reader.stdout.read(int(header[2])); reader.stdout.read(1)
            yield path, mode, data
    finally:
        reader.stdin.close(); reader.stdout.close(); reader.wait()

def plan(entries, policy):
    rows, output, seen = [], {}, set()
    summary = {c: {'files': 0, 'bytes': 0, 'extensions': {}} for c in sorted(CLASSES)}
    for path, mode, data in entries:
        if path in seen: fail('duplicate source path')
        seen.add(path)
        classification = classify(path, data, policy)
        row = {'path': path, 'classification': classification, 'bytes': len(data), 'git_mode': mode, 'sha256': digest(data)}
        group = summary[classification]; group['files'] += 1; group['bytes'] += len(data)
        ext = Path(path).suffix.lower() or '(none)'
        totals = group['extensions'].setdefault(ext, {'files': 0, 'bytes': 0})
        totals['files'] += 1; totals['bytes'] += len(data)
        if classification in PUBLIC:
            body = transform(path, data) if classification == 'PUBLIC_INCLUDE_TRANSFORMED' else data
            if path in JOURNALS and body != transform(path, body): fail('journal export is not bounded/idempotent')
            if binary(path, body): row['binary_inspection'] = inspect_binary(path, body, policy)
            else: row['privacy'] = scan(path, body, policy)
            destination = policy['exceptions'].get(path, {}).get('output', path)
            path_ok(destination)
            if destination.startswith(HISTORICAL) and not (policy['exceptions'].get(path, {}).get('historical_exception') and destination == path):
                fail('historical output relocation: ' + destination)
            if destination in output: fail('output collision: ' + destination)
            if path in JOURNALS and destination != path: fail('journal relocation forbidden')
            output[destination] = (mode, body)
            row.update(output=destination, output_bytes=len(body), output_sha256=digest(body))
        rows.append(row)
    for obligation in policy['notice_obligations']:
        if any(p.startswith(obligation['material_prefix']) for p in output):
            for notice in obligation['notices']:
                if notice not in output: fail('required bundled notice omitted: ' + notice)
                wanted = policy.get('notice_sha256', {}).get(notice)
                if not wanted or digest(output[notice][1]) != wanted:
                    fail('required bundled notice altered: ' + notice)
    for path, required in policy.get('embedded_notices', {}).items():
        if path in output and any(token.encode() not in output[path][1] for token in required):
            fail('embedded notice removed: ' + path)
    return rows, output, summary

def validate_staging(root, expected):
    actual = set()
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            item = Path(base) / name; rel = item.relative_to(root).as_posix(); path_ok(rel)
            if item.is_symlink(): fail('staging symlink: ' + rel)
        for name in files:
            item = Path(base) / name; rel = item.relative_to(root).as_posix(); actual.add(rel)
            if rel not in expected or item.read_bytes() != expected[rel][1]: fail('staging contents drift: ' + rel)
    if actual != set(expected): fail('staging inventory mismatch')

def write_staging(destination, output):
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink(): fail('output must not exist')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='glyph-export-', dir=destination.parent) as temp:
        root = Path(temp) / 'tree'; root.mkdir()
        for path, (mode, body) in sorted(output.items()):
            path_ok(path); target = root / path
            if not target.resolve().is_relative_to(root.resolve()): fail('path escapes output root')
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream: stream.write(body)
            target.chmod(0o755 if mode == '100755' else 0o644)
        validate_staging(root, output)
        os.rename(root, destination)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--revision', default='HEAD')
    parser.add_argument('--policy', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--diagnostic-stage', action='store_true')
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy or args.root / POLICY)
        rows, output, summary = plan(tracked_tree(args.root, args.revision), policy)
        blockers = [r['path'] for r in rows if r['classification'] == 'REVIEW_REQUIRED']
        blockers += ['license:' + r['name'] for r in policy['dependencies'] if r['action'] == 'REVIEW_REQUIRED']
        report = {'schema': 'glyph_public_export_inventory.v1', 'source_commit': subprocess.check_output(
            ['git', 'rev-parse', args.revision + '^{commit}'], cwd=args.root, text=True).strip(),
            'policy_sha256': digest((args.policy or args.root / POLICY).read_bytes()),
            'tracked_blobs': len(rows), 'classification_totals': summary,
            'privacy': 'PASS_FOR_INCLUDED_OUTPUTS', 'blockers': blockers,
            'stage_h_ready': False, 'diagnostic_only': args.diagnostic_stage,
            'output_files': len(output), 'output_bytes': sum(len(b) for _, b in output.values()), 'inventory': rows}
        if args.output and args.report.absolute().is_relative_to(args.output.absolute()): fail('private report inside staging root')
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        if blockers and not args.diagnostic_stage: fail('export blocked; review required: ' + ', '.join(blockers))
        if args.output: write_staging(args.output, output)
        print(json.dumps({k: report[k] for k in ('tracked_blobs', 'output_files', 'output_bytes', 'privacy', 'blockers')}, sort_keys=True))
        return 0
    except (ExportError, OSError, UnicodeError, KeyError, subprocess.CalledProcessError) as exc:
        print('glyph_public_export: FAIL: ' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
