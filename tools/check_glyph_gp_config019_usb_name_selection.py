#!/usr/bin/env python3
"""GP-CONFIG-019 exact production host proof; no firmware or naming-policy change."""
from __future__ import annotations
import hashlib
import json
import stat
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "d2f78cd3a3fa38c60d04dab54236ee630ead379e"
FIXTURE = "docs/calibration/fixtures/gp_config_019_usb_name_selection_characterization.json"
REPORT = "docs/calibration/gp_config_019_usb_name_selection_characterization.md"
HOST = "tools/fixtures/gp_config019_usb_name_selection"
DECODER = "tools/fixtures/gp_config012_button_host"
SOURCE_SHA256 = {'HAL/pico/src/display/DefaultConfigMenu.cpp': '279b44fb4e55f73178591908f843f51a086c4e1c3c26d537aac18a26eae95b20', 'HAL/pico/include/display/DefaultConfigMenu.hpp': '94c6404c37fa6de41563ba06fe839a169b2281d990d8bde36d61c6f29238fa7f', 'HAL/pico/src/display/ConfigMenu.cpp': '5772d5accd688ffe176d968146c02c17682512c9551348438d6a7a76e94a57be', 'HAL/pico/include/display/ConfigMenu.hpp': '16c4c1da62c3b0309a51779780727d1191b6c7bb4bff1a6b1bde2c69c68a8088', 'config/glyph/common/src/display/GlyphConfigMenu.cpp': '4ef795f0d34a745cf2d96f52be2493808452e2998a371ee5a96747a08207fcf0', 'config/glyph/common/include/display/GlyphConfigMenu.hpp': '428ad8033d9a03adbf51526a7cb494287da0525e6c493f83f8c19d8d366f64d7', 'config/glyph/common/include/glyph_overrides.hpp': 'ab4074ed3cd6988abadaf9a79343be8fdd9751c3fb24ebc2d25f3111857cae1d', 'config/glyph/common/src/config.cpp': 'bde443c7eceb417494ae71191a2076c0ab251e987706f30a757b14aaf16ad0e5', 'HAL/pico/src/core/Persistence.cpp': '941cc54f0fb762e6067db338601325d33cf7f980148a59caa1d61f226e140955', 'HAL/pico/include/core/Persistence.hpp': '56d8c3281b54a6d8168a7e8d04d31c0c2b20d1c2223b21b77a9a1549460a669d', 'HAL/pico/src/comms/ConfiguratorBackend.cpp': '28ef942416d0ec4b92588304fcf72f219a0c6b1e2a582f20e2dc7e0e07d1b876', 'HAL/pico/src/comms/backend_init.cpp': '8cbd355e6323a775ab88aacef2ca07d2cad88232790f9d8b8d3f2f686875e2ea', 'HAL/pico/include/comms/backend_init.hpp': '3c2e4b29d06e85e17ba0f63ac7160589ec0b5661874406a9e3a576446b2cf227', 'HAL/pico/src/reboot.cpp': 'f89b9199f55e8f116901ca49484f7ef6c3fe51c048dc31a98934d08bf0a5627e', 'include/reboot.hpp': 'bcc6237cd7c3b85e263cdfd2f265aaf257537a75fc6518acb4edf5f0ab14ef6d', 'src/core/mode_selection.cpp': '8df6ddf1ca626f7d840e68ea700654bcbc30f6473fe7383abc4bf6e99fc4fd44', 'src/core/config_utils.cpp': 'b97af928bff72103f90b0155e4e63fd44a3cfcb84e46ac93cf74f6f3227e02ab', 'HAL/pico/include/util/state_util.hpp': 'db4b4ee7dcfe462dd00097a5109e028787e11d7868b012f447c9fee84e68ea81', 'platformio.ini': '99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9', 'config/glyph/env.ini': 'c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf', 'builder_scripts/arduino_pico.py': '676b20e42500cb0b5f671892250a2c063e21a31459ed542ad48a9481a7fce0af', 'docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json': 'a0f017c36ce0354f91d1a62210756c0464c6db9b5183ba6592ce69d32da1e13f', 'tools/fixtures/gp_config012_button_host/schema/config.proto': '2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b', 'tools/fixtures/gp_config012_button_host/schema/config.options': '6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805', 'tools/fixtures/gp_config012_button_host/generated/config.pb.h': 'bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323', 'tools/fixtures/gp_config012_button_host/generated/config.pb.c': 'd7041bfaf221cc747c7f2dc3fa8586352a1b8dc363fbdcfca181774562941626', 'tools/fixtures/gp_config012_button_host/nanopb/pb.h': 'e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2', 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.h': 'fcac5f7680fe6e870157e4bcf34d5162bdd4fff0d7db3cad1122f2ad24a6da87', 'tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c': 'f5b425beaa207251e531c8ce2c86c9b6867e2920ed59cc1b125332af0c147632', 'tools/fixtures/gp_config012_button_host/nanopb/pb_common.h': '6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd', 'tools/fixtures/gp_config012_button_host/nanopb/pb_common.c': '8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516', 'tools/fixtures/gp_config012_button_host/LICENSE.nanopb.txt': 'e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d'}
HOST_SHA256 = {'tools/fixtures/gp_config019_usb_name_selection/main.cpp': 'aedd1cf767dc370451028a8bfc3a0f17e6859cc6c7cb79384874b67da1969d65', 'tools/fixtures/gp_config019_usb_name_selection/include/host_stubs.hpp': '019087c96be2f61b20827771375f656f5e2811e694293cbab6e2592055560ce1'}
FRAGMENT_SHA256 = {'defaults': '6bd7e0f7170aff3608106096b26b0b4e410aa6e0cf4aa43aa00076bb8b66e31f', 'default_copy': 'fb34a4b4eeaf27de120f21e866f4dd6294fec326a9e9b0be9d1f832215fda834', 'sameName': 'b7faa9e5b31de90ac1dfe0254286beb22e68a1d673dab82dd4f9fd1879d179c4', 'selector': '5fcc08ae11cd40795fa5c8c2d4bae1d1c3bdee2f6a660842ccb9ffaf7b179247', 'usb_menu': 'c5f6d0cc98d8c077fd2a914437734ea9f3a47b3e25c62561becebb5caedf1e9d', 'acceptance': '400290a51fb4740cec889bd7c5eecf719a5e80c8145da3589dd5a66a9d991746', 'load': '374511570ccad298cbe6265f0dcffc877ca0d452484369a501dc42fa94fdc770', 'mask_helpers': '1e422153ff64a5991c88b1fc8a0957ac31c65d26e9ba623459025d3a9cf40e15', 'backend_helpers': 'f1d9899958ea5c7372188d349c9aea82e593c8e329c6223a39a6a165d54a0fbc', 'backend_selector': 'de38f52b6d0362985a4107407dc6ed12deb41ac6c5cf522e3ebf38cc43aa322d', 'usb_getter': '807d98db9948beabf51edee14d6cfaa6326ce5f33039dbb458adfd178318311b', 'watchdog_consumer': '158a3d028c42dc87fe236e64f85f9c619dfd6ca1316c30821e75ecba53715b1b'}

class ContractError(AssertionError):
    pass

def require(ok, message):
    if not ok:
        raise ContractError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def unique(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out

def regular(path):
    file = ROOT / path
    for parent in (file, *file.parents):
        if parent == ROOT:
            break
        require(not parent.is_symlink(), "symlink input: " + path)
    require(file.is_file() and stat.S_ISREG(file.stat().st_mode) and not file.stat().st_mode & 0o111,
            "nonregular/executable input: " + path)
    return file

def validate_inventory(records, expected, content):
    require(isinstance(records, list) and len(records) == len(expected), "inventory omission/addition")
    require({r['path'] for r in records} == set(expected), "inventory membership mismatch")
    for record in records:
        path = record['path']
        require(record['mode'] == '100644' and record['sha256'] == expected[path], "inventory hash/mode substitution: " + path)
        require(digest(content(path)) == expected[path], "input byte substitution: " + path)

def load():
    value = json.loads(regular(FIXTURE).read_text(), object_pairs_hook=unique)
    require(value['schema_name'] == 'glyph_gp_config019_usb_name_selection_characterization'
            and value['schema_version'] == 1 and value['work_order'] == 'GP-CONFIG-019', 'fixture identity')
    require(value['base_configurator_sha'] == BASE and value['candidate_successor'] == 'GP-VAL-041'
            and value['canonical_integration'] == 'WAITING_FOR_GP-VAL-041_DONE', 'candidate gate changed')
    require(value['hardware_acceptance'] == 'NOT_CLAIMED' and value['nunchuk'] == 'NOT_TESTED'
            and value['root_cause'] == 'UNPROVEN', 'nonclaims changed')
    validate_inventory(value['production_sources'], SOURCE_SHA256, lambda p: regular(p).read_bytes())
    validate_inventory(value['host_sources'], HOST_SHA256, lambda p: regular(p).read_bytes())
    for record in value['production_sources']:
        entry = subprocess.check_output(['git', 'ls-tree', BASE, '--', record['path']], cwd=ROOT, text=True).strip()
        require(entry.startswith('100644 blob ' + record['blob'] + '\t'), 'source blob/mode mismatch')
        raw = subprocess.check_output(['git', 'show', BASE + ':' + record['path']], cwd=ROOT)
        require(digest(raw) == SOURCE_SHA256[record['path']], 'immutable base source mismatch')
        flags = subprocess.check_output(['git', 'ls-files', '-v', '--', record['path']], cwd=ROOT, text=True)
        require(flags.startswith('H '), 'source index flag trap')
    report = regular(REPORT).read_text()
    for token in ['GP-CONFIG-019', 'GP-VAL-041', 'H1', 'UNKNOWN', 'NOT_TESTED', 'no naming policy']:
        require(token in report, 'report nonclaim/stop token missing: ' + token)
    return value

def fragment(path, start, end):
    source = regular(path).read_text()
    require(source.count(start) == 1, 'missing/duplicate production body start: ' + start)
    begin = source.index(start); finish = source.find(end, begin + len(start))
    require(finish >= 0, 'missing production body end: ' + end)
    return source[begin:finish].rstrip() + '\n'

def fragments():
    menu = 'HAL/pico/src/display/DefaultConfigMenu.cpp'
    backend = 'HAL/pico/src/comms/backend_init.cpp'
    defaults = 'config/glyph/common/include/glyph_overrides.hpp'
    parts = {
        'defaults': fragment(defaults, 'const Config default_config = {', '// clang-format on'),
        'default_copy': fragment(defaults, 'Config glyph_default_config() {', 'size_t init_secondary_backends_glyph('),
        'sameName': fragment(menu, 'bool sameName(char* name1, char* name2) {', 'void DefaultConfigMenu::SetUsbBackend('),
        'selector': fragment(menu, 'void DefaultConfigMenu::SetUsbBackend(', 'void DefaultConfigMenu::SetSocdType('),
        'usb_menu': fragment(menu, '    /* Build default USB backends page */', '    /* Build gamemodes page */'),
        'acceptance': fragment('HAL/pico/src/comms/ConfiguratorBackend.cpp', 'bool ConfiguratorBackend::HandleSetConfig() {', 'bool ConfiguratorBackend::HandleUnknownCommand('),
        'load': fragment('HAL/pico/src/core/Persistence.cpp', 'bool Persistence::LoadConfig(Config &config) {', 'bool Persistence::CheckSavedConfig() {'),
        'mask_helpers': fragment('HAL/pico/include/util/state_util.hpp', 'inline uint64_t make_button_mask(', 'inline bool any_button_held('),
        'backend_helpers': fragment('src/core/config_utils.cpp', 'CommunicationBackendConfig backend_config_from_buttons(', 'uint8_t backend_config_id_from_backend_id('),
        'backend_selector': fragment(backend, 'backend_config_selector_t get_backend_config_default = [](', '/* Default is to get default USB backend from config. */'),
        'usb_getter': fragment(backend, 'usb_backend_getter_t get_usb_backend_config_default = [](', '// clang-format on'),
        'watchdog_consumer': fragment(backend, 'size_t initialize_backends(', 'void init_primary_backend('),
    }
    return parts

def assemble(parts):
    require(set(parts) == set(FRAGMENT_SHA256), 'production fragment omission/addition')
    for key, data in parts.items():
        require(digest(data.encode()) == FRAGMENT_SHA256[key], 'production fragment substitution: ' + key)
    pieces = []
    for key, data in parts.items():
        if key == 'usb_menu':
            data = 'void DefaultConfigMenu::BuildUsbPage(Config &config) {\n' + data + '}\n'
        pieces.append(data)
    return '\n'.join(pieces)

def run(command):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=45)
    require(result.returncode == 0, 'host command failed: ' + ' '.join(map(str, command)) + '\n' + result.stdout + result.stderr)
    return result

def compile_harness(temp, production):
    (temp / 'production_fragments.inc').write_text(production)
    includes = ['-I' + str(ROOT / DECODER / 'nanopb'), '-I' + str(ROOT / DECODER / 'generated'), '-I' + str(temp)]
    flags = ['-O0', '-g', '-fshort-enums', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer']
    objects = []
    for index, path in enumerate(['nanopb/pb_decode.c', 'nanopb/pb_common.c', 'generated/config.pb.c']):
        obj = temp / (str(index) + '.o')
        run(['cc', '-std=c99', *flags, *includes, '-c', str(ROOT / DECODER / path), '-o', str(obj)])
        objects.append(str(obj))
    obj = temp / 'host.o'
    run(['c++', '-std=gnu++20', *flags, *includes, '-c', str(ROOT / HOST / 'main.cpp'), '-o', str(obj)])
    binary = temp / 'usb-name-host'
    run(['c++', *flags, *objects, str(obj), '-o', str(binary)])
    return binary

def negative_controls(value, parts):
    count = 0
    def rejects(callback):
        nonlocal count
        try:
            callback()
        except ContractError:
            count += 1
        else:
            raise ContractError('negative control accepted')
    for category, pins in [('production_sources', SOURCE_SHA256), ('host_sources', HOST_SHA256)]:
        records = value[category]
        for index, record in enumerate(records):
            rejects(lambda index=index: validate_inventory(records[:index] + records[index + 1:], pins, lambda p: regular(p).read_bytes()))
            forged = [dict(r) for r in records]; forged[index]['sha256'] = '0' * 64
            rejects(lambda forged=forged: validate_inventory(forged, pins, lambda p: regular(p).read_bytes()))
            target = record['path']
            rejects(lambda target=target: validate_inventory(records, pins,
                lambda p: ((bytes([regular(p).read_bytes()[0] ^ 1]) + regular(p).read_bytes()[1:]) if p == target else regular(p).read_bytes())))
            forged = [dict(r) for r in records]; forged[index]['mode'] = '100755'
            rejects(lambda forged=forged: validate_inventory(forged, pins, lambda p: regular(p).read_bytes()))
    for key in parts:
        omitted = dict(parts); omitted.pop(key)
        rejects(lambda omitted=omitted: assemble(omitted))
        changed = dict(parts); changed[key] = chr(ord(changed[key][0]) ^ 1) + changed[key][1:]
        rejects(lambda changed=changed: assemble(changed))
    return count

def main():
    try:
        value = load(); parts = fragments(); production = assemble(parts)
        count = negative_controls(value, parts)
        with tempfile.TemporaryDirectory(prefix='glyph-config019-host-') as folder:
            binary = compile_harness(Path(folder), production)
            result = run([str(binary)])
            require(not result.stderr, 'unexpected sanitizer stderr')
            require(result.stdout.splitlines() == value['expected_rows'], 'observation mismatch:\n' + result.stdout)
            print(result.stdout, end='')
        print(f'negative_controls={count} source_files={len(SOURCE_SHA256)} production_fragments={len(parts)} PASS')
        print('gp_config019_usb_name_selection: PASS; exact production H1; integration awaits GP-VAL-041 DONE')
        return 0
    except (OSError, subprocess.SubprocessError, ContractError, KeyError, TypeError, ValueError) as error:
        print('gp_config019_usb_name_selection: FAIL: ' + str(error))
        return 1


CURRENT_FIXTURE = 'docs/runtime_config/fixtures/gp_val041_usb_name_current_acceptance.json'
CURRENT_REPORT = 'docs/runtime_config/gp_val041_usb_name_current_acceptance.md'
CURRENT_HARNESS = 'tools/fixtures/gp_config019_usb_name_selection/current_acceptance.cpp'
CURRENT_FILE_SHA256 = {'tools/fixtures/gp_config019_usb_name_selection/current_acceptance.cpp': 'be0ace2b917ade71cde930e5e3293443bfe26f4713a4d40d82008a22e0615e1b', 'docs/runtime_config/fixtures/gp_val041_usb_name_current_acceptance.json': 'c918594c260e8a4a675d84c0b808be1c87ac876ea8b2ca138316162de2863453', 'docs/runtime_config/gp_val041_usb_name_current_acceptance.md': '9aa78efa0e35eb483281865e2e25f6611c9653beccb4757ba399959a0012eaab'}
VAL045_FIXTURE = 'docs/runtime_config/fixtures/gp_val045_usb_identity_correspondence.json'
VAL045_CURRENT_FRAGMENTS = None
VAL045_SOURCE_CAMPAIGN = None

# GP-VAL-041 separately pinned current overlay. Historical definitions above are retained.
import argparse
import os
import runpy

REPOSITORY_ROOT = ROOT
ORIGINAL_CANDIDATE = 'fe84db39f2fcdd369d0ae26c1cbb80fd5a15d15d'
ORIGINAL_TREE = '240ce04d0fc6c47d4ceb005c2e9dd6b9485a89ac'
ORIGINAL_RAW_SHA256 = 'c6e56845b9c63577c46a11db1660aa5881160ea6022c324e7fac62b14971a711'
ACCEPTED_F020 = '7db4f447d5e796367071b7143fa6c9274c70ae5e'
ORIGINAL_CHECKER = 'tools/check_glyph_gp_config019_usb_name_selection.py'
ORIGINAL_CHECKER_SHA256 = 'f21ec0eecfd4601e91ba5d6b5370f6798952f9d2a3f781bd5b1c3a55a917e540'
ACCEPTED_GUARD = ('    if (!validate_config_button_bindings(candidate)) {\n'
                  '        char errmsg[] = "Config contains an invalid button binding";\n'
                  '        WritePacket(CMD_ERROR, (uint8_t *)errmsg, sizeof(errmsg));\n'
                  '        return false;\n    }\n\n')
ACCEPTED_INCLUDE = '#include "core/config_button_validation.hpp"\n'


def git_read(*args):
    result = subprocess.run(['git', *args], cwd=REPOSITORY_ROOT, capture_output=True, timeout=30)
    require(result.returncode == 0, 'immutable Git read failed: ' + result.stderr.decode(errors='replace'))
    return result.stdout


def object_record(revision, path):
    entries = git_read('ls-tree', '-z', revision, '--', path).split(b'\0')
    require(len(entries) == 2 and not entries[1], 'missing/extra source tree record: ' + path)
    header, name = entries[0].split(b'\t', 1)
    mode, kind, blob = header.decode('ascii').split()
    require(name.decode() == path and mode == '100644' and kind == 'blob', 'source mode/root/type: ' + path)
    raw = git_read('show', revision + ':' + path)
    return {'path': path, 'mode': mode, 'blob': blob, 'sha256': digest(raw)}, raw


def live_file(path, expected):
    global ROOT
    saved = ROOT
    ROOT = REPOSITORY_ROOT
    try:
        raw = regular(path).read_bytes()
    finally:
        ROOT = saved
    require(digest(raw) == expected, 'live input/overlay byte substitution: ' + path)
    return raw


def guard_critical_inputs(head):
    from glyph_hardware_correspondence import _tree, classify_path, CorrespondenceError
    from glyph_tracked_worktree_integrity import (ignored_critical_worktree_paths,
                                                 untracked_critical_worktree_paths,
                                                 tracked_worktree_divergence)
    def critical(path):
        try:
            return classify_path(path) == 'CRITICAL'
        except CorrespondenceError:
            return False
    accepted = {p: entry for p, entry in _tree(REPOSITORY_ROOT, ACCEPTED_F020).items() if critical(p)}
    committed = {p: entry for p, entry in _tree(REPOSITORY_ROOT, head).items() if critical(p)}
    if committed != accepted:
        from glyph_campaign_transition import authenticate
        proof = authenticate(REPOSITORY_ROOT)
        differences = {p for p in committed.keys() | accepted.keys() if committed.get(p) != accepted.get(p)}
        require(differences <= proof['critical_paths'], 'critical drift outside authenticated campaign source')
        phase = (proof['phase'] in {'CANDIDATE_VALIDATION_ONLY', 'ACCEPTED_TRANSITION'} or
                 (proof.get('contract') == 'c024_selector_identity' and
                  proof['phase'] in {'SOURCE_FREE_CANDIDATE', 'SOURCE_FREE_PROCESSOR', 'CANDIDATE_VALIDATION_ONLY'}) or
                 (proof.get('contract') == 'c017_neopixel' and
                  proof['phase'] in {'BASELINE', 'SOURCE_FREE_PROCESSOR'} and
                  proof.get('predecessor_phase') == 'ACCEPTED_TRANSITION'))
        require(proof['target'] == head and phase and
                all(proof['source_candidates'].get(p) is not None and
                    git_read('show', head + ':' + p) ==
                    git_read('show', proof['source_candidates'][p] + ':' + p)
                    for p in differences),
                'current source compatibility lacks exact authenticated campaign ownership')
    require(not ignored_critical_worktree_paths(REPOSITORY_ROOT) and
            not untracked_critical_worktree_paths(REPOSITORY_ROOT), 'ignored/untracked critical input')
    require(not any(critical(p) for p in tracked_worktree_divergence(REPOSITORY_ROOT)),
            'dirty/staged/mode/type critical input')
    for record in git_read('ls-files', '-v', '-z').split(b'\0'):
        if record:
            tag, path = record[:1], record[2:].decode()
            if critical(path):
                require(tag == b'H', 'critical index flag trap: ' + path)


def authenticate_current():
    global VAL045_CURRENT_FRAGMENTS, VAL045_SOURCE_CAMPAIGN
    # Identity-only catalogue authentication never calls this host proof.
    from glyph_c014_campaign_transition import authenticate_config019_coexistence
    head = git_read('rev-parse', 'HEAD').decode().strip()
    campaign = authenticate_config019_coexistence(REPOSITORY_ROOT, head)
    VAL045_SOURCE_CAMPAIGN = campaign
    guard_critical_inputs(head)
    require(Path(git_read('rev-parse', '--show-toplevel').decode().strip()).resolve() == REPOSITORY_ROOT.resolve(),
            'checker repository root mismatch')
    for path, expected in CURRENT_FILE_SHA256.items():
        live_file(path, expected)
    value = json.loads(live_file(CURRENT_FIXTURE, CURRENT_FILE_SHA256[CURRENT_FIXTURE]), object_pairs_hook=unique)
    require((value['schema_name'], value['schema_version'], value['work_order']) ==
            ('glyph_gp_val041_usb_name_current_acceptance', 1, 'GP-VAL-041'), 'current fixture identity')
    require((value['original_candidate'], value['original_base'], value['original_tree'],
             value['original_raw_inventory_sha256'], value['accepted_source_f020']) ==
            (ORIGINAL_CANDIDATE, BASE, ORIGINAL_TREE, ORIGINAL_RAW_SHA256, ACCEPTED_F020), 'current fixture roots')
    require(git_read('show', '-s', '--format=%P', ORIGINAL_CANDIDATE).decode().strip() == BASE,
            'original candidate parent/replay')
    require(git_read('rev-parse', ORIGINAL_CANDIDATE + '^{tree}').decode().strip() == ORIGINAL_TREE,
            'original candidate tree')
    raw_delta = git_read('diff-tree', '--no-commit-id', '--raw', '--no-abbrev', '-r', '-z', BASE, ORIGINAL_CANDIDATE)
    require(digest(raw_delta) == ORIGINAL_RAW_SHA256, 'original candidate raw inventory')
    require(value['historical_fragments'] == FRAGMENT_SHA256 and len(value['historical_sources']) == 32,
            'historical source/fragment reseal')
    require({p['path']: p['sha256'] for p in value['historical_sources']} == SOURCE_SHA256,
            'historical source pin membership')
    require(len(value['original_host_pins']) == 5 and len({p['path'] for p in value['original_host_pins']}) == 5,
            'original host inventory membership')
    historical = {}
    for pin in value['historical_sources'] + value['original_host_pins']:
        record, raw = object_record(ORIGINAL_CANDIDATE, pin['path'])
        require(record == pin, 'immutable original object identity: ' + pin['path'])
        historical[pin['path']] = raw
        if pin in value['historical_sources']:
            base_record, base_raw = object_record(BASE, pin['path'])
            require(base_record == pin and base_raw == raw, 'historical B/C dependency difference')
        elif pin['path'] != ORIGINAL_CHECKER:
            path = REPOSITORY_ROOT / pin['path']
            if path.exists() or path.is_symlink():
                live_file(pin['path'], pin['sha256'])
    require(digest(historical[ORIGINAL_CHECKER]) == ORIGINAL_CHECKER_SHA256, 'historical checker substitution')
    original_fixture = json.loads(historical[FIXTURE], object_pairs_hook=unique)
    require(value['historical_sources'] == original_fixture['production_sources'] and
            value['historical_expected_rows'] == original_fixture['expected_rows'], 'historical evidence reseal')
    require(value['current_harness'] == {'path': CURRENT_HARNESS, 'mode': '100644',
                                        'sha256': CURRENT_FILE_SHA256[CURRENT_HARNESS]}, 'current harness pin')
    require(len(value['current_sources']) == 34 and len({p['path'] for p in value['current_sources']}) == 34,
            'current source inventory omission/addition')
    current = {}
    head = git_read('rev-parse', 'HEAD').decode().strip()
    for pin in value['current_sources']:
        record, raw = object_record(ACCEPTED_F020, pin['path'])
        require(record == pin, 'current source not exact accepted F020: ' + pin['path'])
        live_record, _ = object_record(head, pin['path'])
        if live_record != pin:
            require(campaign.get('contract') == 'c024_selector_identity'
                    and pin['path'] in campaign['authorized_source_paths'],
                    'committed current source drift: ' + pin['path'])
            require(git_read('show', head + ':' + pin['path']) == git_read('show', campaign['target'] + ':' + pin['path']),
                    'accepted C024 current source object mismatch: ' + pin['path'])
        require(git_read('ls-files', '-v', '--', pin['path']) == ('H ' + pin['path'] + '\n').encode(),
                'current source index flag trap: ' + pin['path'])
        index = git_read('ls-files', '--stage', '-z', '--', pin['path'])
        expected_index = live_record['mode'] + ' ' + live_record['blob'] + ' 0\t' + pin['path'] + '\0'
        require(index == expected_index.encode(),
                'staged current source substitution: ' + pin['path'])
        source_bytes = git_read('show', head + ':' + pin['path'])
        require(live_file(pin['path'], digest(source_bytes)) == source_bytes,
                'live current source differs from committed bytes: ' + pin['path'])
        current[pin['path']] = source_bytes
    differences = [p for p in SOURCE_SHA256 if historical[p] != current[p]]
    if campaign.get('contract') == 'c024_selector_identity':
        require(set(differences) <= campaign['authorized_source_paths'],
                'current source differences exceed accepted C024 predecessor lineage')
        phase_record = json.loads(live_file(VAL045_FIXTURE, digest((REPOSITORY_ROOT / VAL045_FIXTURE).read_bytes())), object_pairs_hook=unique)
        actual_fragments = fragments()
        VAL045_CURRENT_FRAGMENTS = (
            phase_record['candidate_current_fragments']
            if campaign['phase'] == 'CANDIDATE_VALIDATION_ONLY'
            else phase_record['base_current_fragments'])
        require({key: digest(value.encode()) for key, value in actual_fragments.items()} == VAL045_CURRENT_FRAGMENTS,
                'current C024 source fragments differ from finite VAL045 pins')
    else:
        require(differences == ['HAL/pico/src/comms/ConfiguratorBackend.cpp'], 'unexpected current source difference')
        old = historical[differences[0]].decode(); new = current[differences[0]].decode()
        require(new.count(ACCEPTED_INCLUDE) == 1 and new.count(ACCEPTED_GUARD) == 1 and
                new.replace(ACCEPTED_INCLUDE, '', 1).replace(ACCEPTED_GUARD, '', 1) == old,
                'current source delta exceeds exact accepted guard')
    return value, historical, current, head, campaign


def write_snapshot(root, files):
    for path, raw in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)


def historical_route(root, value):
    old = runpy.run_path(str(root / ORIGINAL_CHECKER))
    old['fragments'].__globals__['ROOT'] = root
    fixture = json.loads((root / FIXTURE).read_text(), object_pairs_hook=unique)
    old['validate_inventory'](fixture['production_sources'], old['SOURCE_SHA256'], lambda p: (root / p).read_bytes())
    old['validate_inventory'](fixture['host_sources'], old['HOST_SHA256'], lambda p: (root / p).read_bytes())
    parts = old['fragments'](); production = old['assemble'](parts)
    count = old['negative_controls'](fixture, parts)
    require(count == value['historical_identity_negative_controls'] == 160, 'historical identity negatives')
    build = root.parent / 'historical-build'; build.mkdir()
    result = old['run']([str(old['compile_harness'](build, production))])
    require(not result.stderr and result.stdout.splitlines() == value['historical_expected_rows'], 'historical observation/sanitizer mismatch')
    return {'status': 'PASS', 'observations': result.stdout.splitlines(), 'identity_negatives': count,
            'source_files': 32, 'production_fragments': 12, 'sanitizer_stderr': result.stderr}


def current_route(temp, value, current, campaign):
    global ROOT
    saved = ROOT; ROOT = temp / 'current'
    try:
        parts = fragments()
    finally:
        ROOT = saved
    expected_fragments = VAL045_CURRENT_FRAGMENTS if VAL045_CURRENT_FRAGMENTS is not None else value['current_fragments']
    require({k: digest(v.encode()) for k, v in parts.items()} == expected_fragments, 'current fragment substitution')
    if VAL045_CURRENT_FRAGMENTS is None:
        require([k for k in parts if digest(parts[k].encode()) != FRAGMENT_SHA256[k]] == ['acceptance'], 'unexpected current fragment drift')
    if VAL045_CURRENT_FRAGMENTS is None:
        require(parts['acceptance'].replace(ACCEPTED_GUARD, '', 1) ==
                fragment_from_snapshot(temp / 'historical', 'acceptance'), 'acceptance body equivalence exceeds exact guard')
    pieces = [('void DefaultConfigMenu::BuildUsbPage(Config &config) {\n' + body + '}\n')
              if key == 'usb_menu' else body for key, body in parts.items()]
    persistence_source = current['HAL/pico/src/core/Persistence.cpp'].decode()
    reader_start = persistence_source.index('namespace {')
    reader_end = persistence_source.index('Persistence::Persistence()', reader_start)
    reader_helpers = persistence_source[reader_start:reader_end]
    validator_start = persistence_source.index('bool Persistence::SetValidator(')
    validator_end = persistence_source.index('bool Persistence::SaveConfig(', validator_start)
    validator_methods = persistence_source[validator_start:validator_end]
    saved_check_start = persistence_source.index('bool Persistence::CheckSavedConfig(File &config_file')
    saved_check_end = persistence_source.index('\nPersistence persistence;', saved_check_start)
    saved_check = persistence_source[saved_check_start:saved_check_end]
    host_stubs_path = temp / 'historical/tools/fixtures/gp_config019_usb_name_selection/include/host_stubs.hpp'
    original_stubs = host_stubs_path.read_text()
    stub_start = original_stubs.index('struct File {')
    stub_end = original_stubs.index('// HID constants are inert compile placeholders', stub_start)
    compatible_stubs = '''struct HostConfigHeader { size_t config_size = 0; uint32_t config_crc = 0; };
struct File {
    std::vector<uint8_t> bytes; size_t offset = 0; bool valid = true;
    File() = default; explicit File(std::vector<uint8_t> input) : bytes(std::move(input)) {}
    explicit operator bool() const { return valid; }
    size_t size() const { return bytes.size(); }
    size_t position() const { return offset; }
    bool seek(size_t value) { if (value > bytes.size()) return false; offset = value; return true; }
    int read(uint8_t *out, size_t count) {
        if (offset > bytes.size()) return -1;
        const size_t amount = std::min(count, bytes.size() - offset);
        if (amount) std::memcpy(out, bytes.data() + offset, amount);
        offset += amount; return static_cast<int>(amount);
    }
    int read() { return offset < bytes.size() ? bytes[offset++] : -1; }
    void close() {}
};
inline pb_istream_t as_pb_istream(File &file, size_t) {
    return pb_istream_from_buffer(file.bytes.data(), file.bytes.size());
}
inline struct LittleFsStub {
    File open(const char *, const char *) {
        HostConfigHeader header{}; header.config_size = wire.size();
        CRC32 crc; for (uint8_t byte : wire) crc.update(byte); header.config_crc = crc.finalize();
        std::vector<uint8_t> bytes(sizeof(header) + wire.size());
        std::memcpy(bytes.data(), &header, sizeof(header));
        std::copy(wire.begin(), wire.end(), bytes.begin() + sizeof(header));
        return File(std::move(bytes));
    }
} LittleFS;
class Persistence {
  public:
    using ConfigHeader = HostConfigHeader;
    enum class LoadResult { Loaded, Absent, Rejected, StorageFailure };
    unsigned saves = 0; Config saved = Config_init_zero;
    bool available = true; ConfigSemanticValidator _validator = nullptr;
    const char *config_filename = "host-memory-only";
    size_t config_offset = sizeof(ConfigHeader);
    bool IsAvailable() const { return available; }
    bool SetValidator(ConfigSemanticValidator);
    bool ValidateConfig(const Config &, ConfigValidationError &) const;
    bool CheckSavedConfig(File &, LoadResult *failure = nullptr);
    LoadResult LoadConfigChecked(Config &);
    bool LoadConfig(Config &);
    bool SaveConfig(Config &config) { ++saves; saved = config; return true; }
};
inline Persistence persistence;
struct PersistenceValidatorSetup {
    PersistenceValidatorSetup() { persistence.SetValidator(validate_glyph_config); }
};
inline PersistenceValidatorSetup persistence_validator_setup;
'''
    require(original_stubs.count('struct File {') == 1 and
            original_stubs.count('class Persistence {') == 1,
            'immutable C019 host adapter boundaries changed')
    generated_stubs = (original_stubs[:stub_start] +
        '#include <core/config_validation.hpp>\n#include <glyph_config_validation.hpp>\n#include <CRC32.h>\n' +
        compatible_stubs + original_stubs[stub_end:])
    host_stubs_path.write_text(generated_stubs)
    (temp / 'production_fragments.inc').write_text(
        reader_helpers + validator_methods + saved_check + '\n'.join(pieces))

    support_paths = (
        'include/core/config_validation.hpp', 'include/core/config_usb_default_validation.hpp',
        'include/core/config_rgb_target_validation.hpp',
        'config/glyph/common/include/config_rgb_target_domain.hpp',
        'config/glyph/common/include/glyph_config_validation.hpp',
        'config/glyph/glyph_mk6/include/neopixel_definitions.hpp',
        'src/core/config_validation.cpp', 'src/core/config_usb_default_validation.cpp',
        'src/core/config_rgb_target_validation.cpp', 'config/glyph/common/src/glyph_config_validation.cpp')
    for path in support_paths:
        raw = git_read('show', campaign['target'] + ':' + path)
        predecessor = campaign['source_candidates'].get(path)
        if predecessor is not None:
            require(raw == git_read('show', predecessor + ':' + path),
                    'current C019 checked-load support differs from accepted source: ' + path)
        else:
            require(raw == git_read('show', campaign['base'] + ':' + path),
                    'current C019 checked-load support differs from fresh B: ' + path)
        destination = temp / 'current' / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)

    crc_paths = (
        'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.h',
        'tools/fixtures/gp_config021_persisted_recovery/dependencies/CRC32.cpp')
    crc_root = temp / 'c021-crc-host'
    for path in crc_paths:
        raw = git_read('show', '55e2da3d264dcdb89c6d80fae8bab5629a5a662b:' + path)
        live_file(path, digest(raw))
        destination = crc_root / Path(path).name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    (crc_root / 'Arduino.h').write_text('#pragma once\n#include <cstddef>\n#include <cstdint>\n')
    source = temp / 'current_acceptance.cpp'
    source.write_bytes(live_file(CURRENT_HARNESS, CURRENT_FILE_SHA256[CURRENT_HARNESS]))
    decoder = temp / 'current' / DECODER
    includes = ['-I' + str(decoder / 'nanopb'), '-I' + str(decoder / 'generated'),
                '-I' + str(temp / 'current/include'),
                '-I' + str(temp / 'current/config/glyph/common/include'),
                '-I' + str(temp / 'current/config/glyph/glyph_mk6/include'),
                '-I' + str(crc_root),
                '-I' + str(temp)]
    flags = value['compiler_flags']
    require(flags == ['-O0', '-g', '-fshort-enums', '-fsanitize=address,undefined',
                      '-fno-sanitize-recover=all', '-fno-omit-frame-pointer'], 'current compiler protection flags')
    commands = []; objects = []
    def execute(command):
        commands.append(list(map(str, command)))
        result = subprocess.run(command, cwd=temp, capture_output=True, text=True, timeout=45)
        require(result.returncode == 0, 'current host command failed:\n' + result.stdout + result.stderr)
        return result
    for index, path in enumerate(['nanopb/pb_decode.c', 'nanopb/pb_common.c', 'generated/config.pb.c']):
        obj = temp / ('decoder' + str(index) + '.o')
        execute(['cc', '-std=c99', *flags, *includes, '-c', str(decoder / path), '-o', str(obj)])
        objects.append(str(obj))
    current_cpp_sources = [
        temp / 'current/src/core/config_button_validation.cpp',
        temp / 'current/src/core/config_validation.cpp',
        temp / 'current/src/core/config_usb_default_validation.cpp',
        temp / 'current/src/core/config_rgb_target_validation.cpp',
        temp / 'current/config/glyph/common/src/glyph_config_validation.cpp',
        crc_root / 'CRC32.cpp', source]
    for index, path in enumerate(current_cpp_sources):
        name = 'host' if path == source else 'current' + str(index)
        obj = temp / (name + '.o')
        execute(['c++', '-std=gnu++20', *flags, *includes, '-c', str(path), '-o', str(obj)])
        objects.append(str(obj))
    binary = temp / 'current019-host'
    execute(['c++', *flags, *objects, '-o', str(binary)])
    result = execute([str(binary)])
    require(not result.stderr, 'current sanitizer stderr')
    rows = result.stdout.splitlines()
    require(rows == value['historical_expected_rows'] + value['current_expected_rows'], 'current observation/control mismatch:\n' + result.stdout)
    require(sum('CMD_SUCCESS saves=1' in r for r in rows[18:38]) == value['valid_controls'] == 8 and
            sum('CMD_ERROR saves=0 live=BYTE_EXACT saved=BYTE_EXACT' in r for r in rows[18:38]) ==
            value['decoded_invalid_controls'] == 12, 'current false acceptance/control census')
    return {'status': 'PASS', 'original_observations': rows[:18], 'current_controls': rows[18:],
            'valid_controls': 8, 'real_decoded_invalid_controls': 12, 'source_files': 34,
            'checked_load': 'actual accepted C021/C022/C023 methods and validators; exact CRC32 file adapter',
            'acceptance_sha256': value['current_fragments']['acceptance'], 'commands': commands,
            'binary_sha256': digest(binary.read_bytes()), 'sanitizer_stderr': result.stderr}


def fragment_from_snapshot(root, key):
    global ROOT
    saved = ROOT; ROOT = root
    try:
        return fragments()[key]
    finally:
        ROOT = saved


def overlay_main():
    parser = argparse.ArgumentParser(description='GP-VAL-041 authenticated historical/current GP-CONFIG-019 host proof')
    parser.add_argument('--route', choices=['both', 'historical', 'current'], default='both')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    os.environ['GIT_OPTIONAL_LOCKS'] = '0'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    try:
        value, historical, current, head, campaign = authenticate_current()
        if args.report:
            require(args.report.is_absolute() and not args.report.resolve().is_relative_to(REPOSITORY_ROOT.resolve()),
                    'actual execution report must be absolute and outside repository')
        evidence = {'schema_name': 'glyph_gp_val041_usb_name_execution', 'schema_version': 1,
                    'status': 'PASS', 'route': args.route, 'execution_head': head,
                    'original_candidate': ORIGINAL_CANDIDATE, 'accepted_source_f020': ACCEPTED_F020,
                    'historical_sources': value['historical_sources'], 'current_sources': value['current_sources'],
                    'overlay_sha256': CURRENT_FILE_SHA256,
                    'checker_sha256': digest((REPOSITORY_ROOT / ORIGINAL_CHECKER).read_bytes()),
                    'hardware': 'NOT_CLAIMED', 'nunchuk': 'NOT_TESTED', 'root_cause': 'UNPROVEN'}
        with tempfile.TemporaryDirectory(prefix='glyph-config019-current-') as folder:
            temp = Path(folder)
            write_snapshot(temp / 'historical', historical)
            write_snapshot(temp / 'current', current)
            if args.route in {'both', 'historical'}:
                evidence['historical'] = historical_route(temp / 'historical', value)
                print('gp_config019 historical: PASS observations=18 identity_negatives=160 sources=32 fragments=12 ASan_UBSan=PASS')
            if args.route in {'both', 'current'}:
                evidence['current'] = current_route(temp, value, current, campaign)
                print('gp_config019 current: PASS original_observations=18 valid_controls=8 decoded_invalid_controls=12 sources=34 ASan_UBSan=PASS')
        # Recheck live inputs after execution. No proof result is cached.
        authenticate_current()
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(evidence, indent=2) + '\n')
        print('gp_config019_usb_name_selection: PASS; explicit ' + args.route + ' host proof; hardware=NOT_CLAIMED')
        return 0
    except (OSError, subprocess.SubprocessError, ContractError, KeyError, TypeError, ValueError, ImportError, AttributeError) as error:
        print('gp_config019_usb_name_selection: FAIL: ' + str(error))
        return 1


if __name__ == '__main__':
    raise SystemExit(overlay_main())
