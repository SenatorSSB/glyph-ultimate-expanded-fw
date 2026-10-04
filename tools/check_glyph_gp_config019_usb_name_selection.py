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

if __name__ == '__main__':
    raise SystemExit(main())
