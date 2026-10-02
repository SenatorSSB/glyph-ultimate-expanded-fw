#!/usr/bin/env python3
"""GP-KBD-001: literal source keyboard pipeline, bounded host observations only."""
from __future__ import annotations
import copy
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '328c6a1bfb09eb035c2065d0de080283307f34d6'
AUTHORITY = 'd9ad6132ca0912398839673cc0da24e54a924210'
HOST = 'tools/fixtures/gp_kbd_001_keyboard_pipeline'
GP012 = 'tools/fixtures/gp_config012_button_host'
FIXTURE = 'docs/calibration/fixtures/gp_kbd_001_keyboard_pipeline_characterization.json'
SOURCES = (
    'HAL/pico/src/core/KeyboardMode.cpp', 'src/modes/CustomKeyboardMode.cpp',
    'src/core/InputMode.cpp', 'src/core/socd.cpp',
    'HAL/pico/include/core/KeyboardMode.hpp', 'include/modes/CustomKeyboardMode.hpp',
    'include/core/InputMode.hpp', 'include/core/socd.hpp', 'include/core/state.hpp',
    'HAL/pico/include/util/state_util.hpp', 'HAL/pico/include/stdlib.hpp',
    'config/glyph/common/include/glyph_overrides.hpp',
    'config/glyph/common/src/display/GlyphConfigMenu.cpp',
    'HAL/pico/src/display/DefaultConfigMenu.cpp',
    'HAL/pico/src/comms/backend_init.cpp', 'src/core/mode_selection.cpp',
    'config/glyph/common/src/config.cpp', 'platformio.ini', 'config/glyph/env.ini',
    'builder_scripts/arduino_pico.py', 'tools/glyph_tracked_worktree_integrity.py',
    f'{GP012}/generated/config.pb.h', f'{GP012}/nanopb/pb.h',
    f'{GP012}/schema/config.proto', f'{GP012}/schema/config.options',
    f'{GP012}/include/Arduino.h', f'{GP012}/include/pico/stdlib.h',
    'docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json',
)
HOST_PATHS = (f'{HOST}/main.cpp', f'{HOST}/include/TUKeyboard.hpp')

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, f'duplicate key {key}')
        result[key] = value
    return result

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])

def digest(data):
    return hashlib.sha256(data).hexdigest()

def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def regular(root, path):
    target = root / path
    require(target.is_file(), f'missing file {path}')
    for part in (target, *target.parents):
        if part == root: break
        require(not part.is_symlink(), f'symlink {path}')
    require(target.stat().st_mode & 0o111 == 0, f'executable mode {path}')
    return target.read_bytes()

def identities():
    records = {}
    for path in SOURCES:
        entry = git('ls-tree', BASE, '--', path).decode().strip().split()
        require(len(entry) == 4 and entry[0] == '100644', f'base mode {path}')
        data = git('show', f'{BASE}:{path}')
        require(git('show', f'{AUTHORITY}:{path}') == data, f'authorization source drift {path}')
        records[path] = {'git_blob': entry[2], 'sha256': digest(data), 'mode': '100644'}
    return records

def authenticate(root, value, expected):
    require(set(value) == {'schema_name','schema_version','base','authority','sources','host_assets','observations','limitations'}, 'fixture fields')
    require(value['schema_name'] == 'glyph_gp_kbd_001_keyboard_pipeline' and value['schema_version'] == 1, 'fixture identity')
    require(value['base'] == BASE and value['authority'] == AUTHORITY, 'base identity')
    require(value['sources'] == expected, 'closed source identity mismatch')
    require(set(value['host_assets']) == set(HOST_PATHS), 'closed host asset inventory')
    for path, record in expected.items():
        data = regular(root, path)
        require(blob(data) == record['git_blob'] and digest(data) == record['sha256'], f'source bytes {path}')
    for path in HOST_PATHS:
        require(digest(regular(root, path)) == value['host_assets'][path], f'host asset {path}')

def initializer(source, start):
    begin = source.index(start)
    brace = source.index('{', begin)
    depth = 1
    end = brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[begin:end]

def defaults(root):
    source = (root / 'config/glyph/common/include/glyph_overrides.hpp').read_text()
    section = source[source.index('.game_mode_configs = {'):source.index('    // 1  - Melee')]
    profiles = re.findall(r'GameModeConfig\s*\{', section)
    require(len(profiles) == 13, 'default profile census')
    begin = section.rfind('GameModeConfig {')
    profile = initializer(section[begin:], 'GameModeConfig {')
    require('.mode_id = MODE_KEYBOARD,' in profile, 'keyboard profile index')
    keys = initializer(source[source.index('.keyboard_modes = {'):], 'KeyboardModeConfig {')
    tokens = list(dict.fromkeys(re.findall(r'HID_KEY_[A-Z0-9_]+', keys)))
    require(len(tokens) == 35, 'default key token census')
    # Symbolic host IDs, NOT Pico TinyUSB numeric HID encodings.
    defines = '\n'.join(f'#define {token} {i+1}' for i, token in enumerate(tokens))
    return defines + '\nconst GameModeConfig source_profile = ' + profile + ';\nconst KeyboardModeConfig source_keys = ' + keys + ';\n'

def run_host(root, sanitize=False):
    compiler = shutil.which('clang++') or shutil.which('g++')
    require(compiler is not None, 'host C++ compiler unavailable')
    (root / 'source_defaults.hpp').write_text(defaults(root))
    command = [compiler, '-std=c++20', '-Wno-missing-field-initializers', '-Wno-reorder-init-list',
               '-include', 'cstdint', '-include', 'cstddef']
    for path in (HOST + '/include', GP012 + '/generated', GP012 + '/nanopb', GP012 + '/include', 'HAL/pico/include', 'include', '.'):
        command += ['-I', str(root / path)]
    if sanitize:
        command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    command += [str(root / path) for path in (*SOURCES[:4], HOST + '/main.cpp')]
    command += ['-o', str(root / 'keyboard-host')]
    subprocess.run(command, check=True, capture_output=True, text=True)
    return subprocess.check_output([str(root / 'keyboard-host')], text=True, stderr=subprocess.PIPE).splitlines()

def negatives(root, value, expected):
    count = 0
    def reject(candidate):
        nonlocal count
        try: authenticate(root, candidate, expected)
        except (AssertionError, FileNotFoundError): count += 1
        else: raise AssertionError('negative accepted')
    for path in SOURCES:
        altered = copy.deepcopy(value); del altered['sources'][path]; reject(altered)
        target = root / path; original = target.read_bytes()
        target.unlink(); reject(value); target.write_bytes(original)
        target.write_bytes(bytes([original[0] ^ 1]) + original[1:]); reject(value); target.write_bytes(original)
        target.chmod(0o755); reject(value); target.chmod(0o644)
    altered = copy.deepcopy(value); altered['sources']['unknown.cpp'] = {}; reject(altered)
    path = SOURCES[0]; target = root / path; original = target.read_bytes()
    changed = bytes([original[0] ^ 1]) + original[1:]; target.write_bytes(changed)
    altered = copy.deepcopy(value)
    altered['sources'][path]['git_blob'] = blob(changed)
    altered['sources'][path]['sha256'] = digest(changed)
    reject(altered); target.write_bytes(original)
    for path in HOST_PATHS:
        altered = copy.deepcopy(value); del altered['host_assets'][path]; reject(altered)
        target = root / path; original = target.read_bytes()
        target.write_bytes(bytes([original[0] ^ 1]) + original[1:]); reject(value); target.write_bytes(original)
    return count

def behavioral_negatives(root):
    # Explicit negative experiments only, AFTER authenticating the positive snapshot.
    # Mutants never authenticate as accepted source and never leave the temp directory.
    target = root / SOURCES[0]; original = target.read_text()
    mutations = (
        ('original-to-copy', 'UpdateKeys(inputs);', 'UpdateKeys(remapped_inputs);'),
        ('omit-remap', '    HandleRemap(inputs, remapped_inputs);', ''),
        ('omit-socd', '    HandleSocd(remapped_inputs);', ''),
        ('omit-releaseAll', '    _keyboard->releaseAll();', ''),
        ('omit-destructor-send', '    _keyboard->sendState();', ''),
    )
    for label, before, after in mutations:
        require(before in original, f'mutation anchor {label}')
        target.write_text(original.replace(before, after, 1))
        try:
            run_host(root)
        except subprocess.CalledProcessError as error:
            # A compiler error is NOT a passing behavioral negative.
            require(error.cmd == [str(root / 'keyboard-host')], f'mutant compile failed {label}')
        else:
            raise AssertionError(f'behavioral mutant accepted {label}')
        finally:
            target.write_text(original)
    return len(mutations)

def main():
    value = json.loads((ROOT / FIXTURE).read_text(), object_pairs_hook=pairs)
    expected = identities()
    authenticate(ROOT, value, expected)
    with tempfile.TemporaryDirectory(prefix='glyph-kbd-host-') as directory:
        root = Path(directory)
        for path in (*SOURCES, *HOST_PATHS):
            target = root / path; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(regular(ROOT, path))
        authenticate(root, value, expected)
        actual = run_host(root)
        require(actual == value['observations'], 'host observation fixture mismatch')
        require(run_host(root, sanitize=True) == actual, 'sanitizer observation mismatch')
        count = negatives(root, value, expected)
        behavioral_count = behavioral_negatives(root)
        authenticate(root, value, expected)
    print(f'PASS GP-KBD-001: {len(actual)-1} input observations; lifecycle; {count} identity negatives; {behavioral_count} executable mutants rejected; ASan/UBSan; literal source host only')

if __name__ == '__main__':
    try: main()
    except (AssertionError, subprocess.CalledProcessError, OSError, ValueError) as error:
        if isinstance(error, subprocess.CalledProcessError): print(error.stderr)
        raise SystemExit(f'FAIL GP-KBD-001: {error}')
