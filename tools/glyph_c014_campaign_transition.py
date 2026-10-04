"""Exact GP-VAL-034 C014 proof. Candidate validation never implies hardware PASS."""
from __future__ import annotations
import hashlib
import json
import re
import stat
from pathlib import Path
import glyph_campaign_transition as original
import glyph_c020_abi_repair_transition as predecessor
from glyph_hardware_correspondence import CorrespondenceError, classify_path, verify_correspondence
from glyph_tracked_worktree_integrity import IGNORED_ALLOWED_ROOTS

C = 'a3664be5354ec4253122eb2e738e70e5dfdb9ccc'
B = '8b8e45b17a5670bbf983360faf87bdf9d6b50ce2'
TREE = '287732689ce5ef069db72148a78926f4f5376ea0'
HANDOFF = '5205ba518d1d5fa19e7584d6c6d5210932091b3e'
READY = '7911692afed3e68becefd8e3c90413d4e230ea82'
MAPPING = 'docs/runtime_config/fixtures/gp_val034_c014_transition.json'
TRANSITIONS = 'docs/runtime_config/fixtures/gp_val034_accepted_transitions.json'
MAPPING_SHA256 = 'b391107e4ae7d69f716b6ed1f37857af9fba522508638badb42e4710a427b847'
RAW = 'c40d8aadf736832b52a746455d940b29296522c281f49b3ab314e3d22c1d11aa'
QUEUE = original.QUEUE
PROTOCOL = 'docs/agent_framework/GP_CONFIG_014_HARDWARE_PROTOCOL.md'
EVIDENCE = 'docs/calibration/fixtures/gp_config_014_hardware_evidence.json'
RESULT = 'docs/calibration/gp_config_014_hardware_result.md'
CRITICAL = frozenset(('include/modes/CustomControllerMode.hpp', 'src/modes/CustomControllerMode.cpp'))
HOSTS = frozenset(('tools/check_glyph_gp_config014_modifier_capacity.py',
 'tools/fixtures/gp_config014_modifier_capacity/modifier_capacity_harness.cpp',
 'docs/runtime_config/gp_config014_modifier_capacity.md',
 'docs/runtime_config/fixtures/gp_config014_modifier_capacity.json'))
HOST_OVERLAYS = frozenset(('tools/check_glyph_custom_modifier_cache_characterization.py',
 'tools/check_glyph_gp_config012_button_mask_characterization.py',
 'tools/check_glyph_setconfig_runtime_rebinding_characterization.py',
 'tools/check_glyph_gp_config014_modifier_capacity.py'))
HOST_OVERLAY_BLOBS = {'tools/check_glyph_custom_modifier_cache_characterization.py': {'blob': 'd5d71dc0ab97a525585cb0b2f21296c81ea1a5a2', 'sha256': 'fcc0a671a6ac5a1262f125567e84f2ffe0c56ee12c9533ad994ebd0b45701935', 'mode': '100644'}, 'tools/check_glyph_gp_config012_button_mask_characterization.py': {'blob': 'bc03ec9b0beac7c96876022d37673746052ab4d8', 'sha256': 'f515c1c806494acaf60d38dc2d92aaef10e1d292998abe322161fda6ea0cfcd1', 'mode': '100644'}, 'tools/check_glyph_setconfig_runtime_rebinding_characterization.py': {'blob': '4d5fbc036c1d68105d86a2cdf09002b63a388271', 'sha256': '54e93cb3a9c4d757eb2517772ddf86b44d03c6f55bfc1c032eede30381a6a437', 'mode': '100644'}, 'tools/check_glyph_gp_config014_modifier_capacity.py': {'blob': '7e91f2c1415b6de55766d8cf6c694a93ed36a50d', 'sha256': 'b9296f5b33d73e7946e415645535e07ad364b5211803dfecfef2a6e764f85c46', 'mode': '100644'}}

# Existing immutable KBD characterization: exact H1 coexistence only. No019
# future inventory or source-route hash refresh is authorized by these pins.
KBD_C = '4fb7c1e9507547774ff9f55cd7788355648d5d1e'
KBD_B = '328c6a1bfb09eb035c2065d0de080283307f34d6'
KBD_AUTHORITY = 'd9ad6132ca0912398839673cc0da24e54a924210'
KBD_TREE = 'a847f1dab9e7918ec49d5dd887b009adf087c87f'
KBD_RAW = 'f8cc5721ad63f142d535aae73087c9466d1891e3010ea241fd03688aa81f6ad5'
KBD_HOST_PINS = {'docs/calibration/fixtures/gp_kbd_001_keyboard_pipeline_characterization.json': {'mode': '100644', 'blob': 'ea61079fcbb3962b1da9c301de7c3d3867ee4db3', 'sha256': 'ce03196f7fd8f2c779b5ac8a563b9f6f0017dbf4a5bc4e80e99bce01b3a0f455'}, 'docs/calibration/gp_kbd_001_keyboard_pipeline_characterization.md': {'mode': '100644', 'blob': '66592c2bb5a9c4860d4a72accdab52e72080b8fc', 'sha256': 'cec227bda66d072c756686b40100fef19fc768bdcb5038040dced1ea720a4d0d'}, 'tools/check_glyph_gp_kbd_001_keyboard_pipeline.py': {'mode': '100644', 'blob': 'fad8c930329b3317ddf7c07bfec725ac1a7f457f', 'sha256': 'c15ccd4ddc7ae3a88913934afb574fbf647777dd53ceb6060695b938dafacdc8'}, 'tools/fixtures/gp_kbd_001_keyboard_pipeline/include/TUKeyboard.hpp': {'mode': '100644', 'blob': '4bd11a0168f8f0f2308aefd6f7b2942156c9ba9c', 'sha256': '6c6701107f94b540a3819de3f5207f37b7bb5f26cb95ebcb92381f1056c1b0b7'}, 'tools/fixtures/gp_kbd_001_keyboard_pipeline/main.cpp': {'mode': '100644', 'blob': 'd9bbaf7cccd5b35f65b6bd8b0462d78c9bf4fd63', 'sha256': 'c3423bb79fec9dc1b5a221e74e44ce04488fb7aceff86360e2aa4f302f36e9cf'}}
KBD_DEPENDENCY_PINS = {'HAL/pico/src/core/KeyboardMode.cpp': {'mode': '100644', 'blob': 'a14f01d030dad62305fc0accdc07d224c61eefcf', 'sha256': 'a4396ef241cde82c7296ee01aad6b7907e6c7579aa4349c5366621c73c59791d'}, 'src/modes/CustomKeyboardMode.cpp': {'mode': '100644', 'blob': '60c7c69ad77e6c3acf931fdd3ccf1d448701c7f8', 'sha256': '90db32b605383adda19c9f00ad69daf538a766d801415483915ea8d6429a9def'}, 'src/core/InputMode.cpp': {'mode': '100644', 'blob': 'f1388a1948fc73f7525463db219a53f5af1e6b7b', 'sha256': '080bcc65bb83b1b896a2b4efa6ea9e9d304071ee30f279fe3386ff2c29cc85c7'}, 'src/core/socd.cpp': {'mode': '100644', 'blob': '81a0d53fae96305c07d5943f4785b33b02ca1949', 'sha256': '5a2bb8e776873d149559e914b07cc4224853e3e3593a46760c38d23ff4d38bb3'}, 'HAL/pico/include/core/KeyboardMode.hpp': {'mode': '100644', 'blob': '81ad10d78f86da84fd8b1e51fb3857a463014f1e', 'sha256': '6bc35650a119ec942e26015dcb36361ffb284e0f8221134ccd5776ebdfb7a7b5'}, 'include/modes/CustomKeyboardMode.hpp': {'mode': '100644', 'blob': '79a2725ca7703dfdabbd1c186d197e2250122c86', 'sha256': 'c907de266f4ebeea8518511cf725c57bf52c85c0c9827f25cc2a7d20381f9464'}, 'include/core/InputMode.hpp': {'mode': '100644', 'blob': '02f3cfd54c47cf2b8f4587a2d519d0682240eec4', 'sha256': 'dc382c38eb2c30cf7f94727670ae5530a682daf6555db65ea5d5b5f0dc2f23ee'}, 'include/core/socd.hpp': {'mode': '100644', 'blob': '5d912b274ba54fde5e07a575cf9bec84da07c9bb', 'sha256': '88ff9be552e89f0c92a1548662fc4bf9b6fd4408b242f6f42bec8ecf70e6fc91'}, 'include/core/state.hpp': {'mode': '100644', 'blob': 'ff3aa94df61fd6a41448799fa1d6f508c41ecd0f', 'sha256': 'c46eb5347843ac4574dcffb28faeace608f029c27b94690c02ce06981cc4e6a3'}, 'HAL/pico/include/util/state_util.hpp': {'mode': '100644', 'blob': '40b8aeb9c4db3268696c49f20b3278efabc7688c', 'sha256': 'db4b4ee7dcfe462dd00097a5109e028787e11d7868b012f447c9fee84e68ea81'}, 'HAL/pico/include/stdlib.hpp': {'mode': '100644', 'blob': '6bc7bc5ee7f56de07116608399af228314dab004', 'sha256': '676ecc6f5a9b333bf2c55a9df11ddf037a83fe217788c17f887fae4851ea90bc'}, 'config/glyph/common/include/glyph_overrides.hpp': {'mode': '100644', 'blob': '90cc393759e91c8acacd6edef9ecb05b86d7fdc8', 'sha256': 'ab4074ed3cd6988abadaf9a79343be8fdd9751c3fb24ebc2d25f3111857cae1d'}, 'config/glyph/common/src/display/GlyphConfigMenu.cpp': {'mode': '100644', 'blob': '819549dfdf2de34d5ceebed58fa30d278da4f4cb', 'sha256': '4ef795f0d34a745cf2d96f52be2493808452e2998a371ee5a96747a08207fcf0'}, 'HAL/pico/src/display/DefaultConfigMenu.cpp': {'mode': '100644', 'blob': 'bf855a584b3e859083d98a1aa49a38daee9204f5', 'sha256': '279b44fb4e55f73178591908f843f51a086c4e1c3c26d537aac18a26eae95b20'}, 'HAL/pico/src/comms/backend_init.cpp': {'mode': '100644', 'blob': 'f7726a0063dd05409d7464d947a47efc675bdbef', 'sha256': '8cbd355e6323a775ab88aacef2ca07d2cad88232790f9d8b8d3f2f686875e2ea'}, 'src/core/mode_selection.cpp': {'mode': '100644', 'blob': '7d659d3133271c2ed956a16d8f5e3eda73040f81', 'sha256': '8df6ddf1ca626f7d840e68ea700654bcbc30f6473fe7383abc4bf6e99fc4fd44'}, 'config/glyph/common/src/config.cpp': {'mode': '100644', 'blob': '701e4ac8c0a635b77ef4282f29109f7bb0bea726', 'sha256': 'bde443c7eceb417494ae71191a2076c0ab251e987706f30a757b14aaf16ad0e5'}, 'platformio.ini': {'mode': '100644', 'blob': '4d56f8630c1b12e84cd12f40ce05a4dc71b9362e', 'sha256': '99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9'}, 'config/glyph/env.ini': {'mode': '100644', 'blob': 'fac4e20461ad632ca1d65826241a4a9c73630f04', 'sha256': 'c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf'}, 'builder_scripts/arduino_pico.py': {'mode': '100644', 'blob': '35381a91ad5aa4ffdbcd362365c1bf9fbd13136e', 'sha256': '676b20e42500cb0b5f671892250a2c063e21a31459ed542ad48a9481a7fce0af'}, 'tools/glyph_tracked_worktree_integrity.py': {'mode': '100644', 'blob': 'f653b4619ee0ce8a8c35d972fa591545522c0be7', 'sha256': '604bea90c4b3cb2cbb0fdf023918da7ba45d1be7d128c2b40050e09e5a220fc7'}, 'tools/fixtures/gp_config012_button_host/generated/config.pb.h': {'mode': '100644', 'blob': '01d0dda2ae768dd0f18c0f338a74c55e613bb199', 'sha256': 'bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323'}, 'tools/fixtures/gp_config012_button_host/nanopb/pb.h': {'mode': '100644', 'blob': '3f181d873a81d82c27c56874f6a63328f38eaaf3', 'sha256': 'e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2'}, 'tools/fixtures/gp_config012_button_host/schema/config.proto': {'mode': '100644', 'blob': 'a58a2bf4dd827ad92482f1ac30c3d56bbea93c05', 'sha256': '2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b'}, 'tools/fixtures/gp_config012_button_host/schema/config.options': {'mode': '100644', 'blob': '7175d8463ade5b0cd45f1a5f8f99be44f5719c3c', 'sha256': '6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805'}, 'tools/fixtures/gp_config012_button_host/include/Arduino.h': {'mode': '100644', 'blob': '7a3d1de2a3400cb7ee45750c25491e9b434f2608', 'sha256': '70de967f79f47db90cb5864847e129e4d6c322dcfa08338cd31ddf601354dc20'}, 'tools/fixtures/gp_config012_button_host/include/pico/stdlib.h': {'mode': '100644', 'blob': '9bf1084ddd04162e6b0fe39f56f52b6d46cbd1c9', 'sha256': '0990f6f853b296816a654c1a4d4ccd8593bc819a1d591af8f01ab238926c41d4'}, 'docs/runtime_config/fixtures/gp_prov_014_decoder_closure.json': {'mode': '100644', 'blob': '25d32a1fc1cc9c39626eadd4dca4835103579d80', 'sha256': 'a0f017c36ce0354f91d1a62210756c0464c6db9b5183ba6592ce69d32da1e13f'}}
KBD_HOSTS = frozenset(KBD_HOST_PINS)
NEW_PATHS = frozenset((MAPPING, TRANSITIONS, 'tools/glyph_c014_campaign_transition.py',
 'tools/test_glyph_c014_campaign_transition.py'))
GOVERNANCE_PATHS = (predecessor.GOVERNANCE_PATHS | predecessor.REVISION_THREE_PATHS |
 predecessor.PERSISTENT_BATCH_PATHS | HOSTS | HOST_OVERLAYS | NEW_PATHS | KBD_HOSTS |
 frozenset((PROTOCOL, EVIDENCE, RESULT, predecessor.OWNER_DIRECTION,
            'tools/check_glyph_custom_modifier_cache_characterization.py')))
ROOTS = predecessor.ROOTS | frozenset((C, B, HANDOFF, READY, KBD_C, KBD_B, KBD_AUTHORITY,
 predecessor.PERSISTENT_BATCH_AUTHORITY, predecessor.REVISION_THREE_AUTHORITY,
 predecessor.OWNER_DIRECTION_AUTHORITY))
AUTHORITY_SHA256 = {
 B: 'a7006b98a6f7da16cddc17bc249861d613464010c30c5f458515e65a92a84dec',
 HANDOFF: 'b4897410c2922eed071cb8a8895f29724b26cfe0ff9b44af2791ace2f56f86cd',
 READY: '15216484e2fcebc992d3a78d5c8e67ed9890f820e0cd476e1261f763bc8fb7c1'}
REQUIRED_ROWS = ('modifier_0', 'modifier_10', 'modifier_11', 'modifier_20',
                 'combos_modifiers', 'ultimate_x1', 'reconnect_reboot', 'owner_config_restoration')
IDENTITIES = ('candidate_git_sha', 'candidate_base_configurator_sha',
 'firmware_artifact_sha256', 'firmware_artifact_build_path', 'preserved_firmware_artifact_locator',
 'manual_acceptance_protocol_reference', 'manual_acceptance_protocol_version',
 'hardware_evidence_contract_reference', 'hardware_evidence_contract_version')
require = original.require
unique = original.unique
_git = original._git
_tree = original._tree
raw_bytes = original.raw_bytes
current_bytes = original.current_bytes
critical_tree = original.critical_tree
ancestor = original.ancestor
item = original.item
queue = original.queue

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def immutable(identity):
    require(isinstance(identity, str) and re.fullmatch('[0-9a-f]{40}', identity),
            'nonimmutable C014 identity')
    return identity

def parsed_queue(raw):
    text = raw.decode()
    start, end = '<!-- queue-state:start -->', '<!-- queue-state:end -->'
    require(text.count(start) == text.count(end) == 1, 'queue marker mismatch')
    block = text.split(start)[1].split(end)[0].strip()
    require(block.startswith('```json') and block.endswith('```'), 'queue fence mismatch')
    return json.loads(block[7:-3], object_pairs_hook=unique)

def state_from(raw, order):
    found = [x for x in parsed_queue(raw)['items'] if x['id'] == order]
    require(len(found) == 1, 'missing/duplicate order')
    return found[0]

@original._proof_invocation
def source_contract(root):
    root = Path(root).resolve()
    for revision, digest in AUTHORITY_SHA256.items():
        require(sha(raw_bytes(root, revision, QUEUE)) == digest, 'C014 immutable authority substitution')
    require(_git(root, 'rev-list', '--parents', '-n', '1', C).decode().split() == [C, B],
            'C014 candidate direct parent mismatch')
    require(_git(root, 'rev-parse', C + '^{tree}').decode().strip() == TREE, 'C014 tree mismatch')
    require(sha(_git(root, 'diff-tree', '-r', '--no-renames', '--raw', '-z', B, C)) == RAW,
            'C014 raw inventory mismatch')
    mapping_raw = current_bytes(root, MAPPING)
    require(sha(mapping_raw) == MAPPING_SHA256, 'C014 mapping substitution')
    mapping = json.loads(mapping_raw, object_pairs_hook=unique)
    require(set(mapping) == {'schema_name', 'schema_version', 'work_order', 'candidate', 'base',
                            'tree', 'raw_inventory_sha256', 'entries', 'handoff', 'ready',
                            'review_sha256', 'validation_sha256'}, 'C014 mapping field mismatch')
    require(mapping['schema_name'] == 'glyph_gp_val034_c014_transition'
            and type(mapping['schema_version']) is int and mapping['schema_version'] == 1
            and mapping['work_order'] == 'GP-VAL-034'
            and (mapping['candidate'], mapping['base'], mapping['tree'], mapping['raw_inventory_sha256'],
                 mapping['handoff'], mapping['ready']) == (C, B, TREE, RAW, HANDOFF, READY),
            'C014 literal mapping identity mismatch')
    bt, ct = _tree(root, B), _tree(root, C)
    paths = {p for p in bt.keys() | ct.keys() if bt.get(p) != ct.get(p)}
    metadata = frozenset(('docs/runtime_config/fixtures/runtime_config_validation_manifest.json',
                         'docs/runtime_config/fixtures/glyph_checker_census.json',
                         'docs/runtime_config/fixtures/runtime_config_validation_health.json',
                         'docs/runtime_config/runtime_config_validation_health.md'))
    require(paths == CRITICAL | HOSTS | metadata and len(mapping['entries']) == 10,
            'C014 finite ten-path membership mismatch')
    require({x['path'] for x in mapping['entries']} == paths, 'C014 duplicate/omitted inventory path')
    for entry in mapping['entries']:
        require(set(entry) == {'path', 'old_mode', 'new_mode', 'old_blob', 'new_blob', 'status'},
                'C014 inventory fields mismatch')
        p = entry['path']; old = bt.get(p)
        require(ct[p][:2] == ('100644', 'blob') and entry['new_mode'] == '100644'
                and entry['new_blob'] == ct[p][2]
                and (entry['old_mode'], entry['old_blob'], entry['status']) ==
                    ((old[0], old[2], 'M') if old else ('000000', '0' * 40, 'A')),
                'C014 inventory blob/mode/status substitution: ' + p)
    before, after = critical_tree(root, B), critical_tree(root, C)
    require(len(before) == len(after) == 236
            and {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)} == CRITICAL,
            'C014 critical union outside two entries')
    require(after['include/modes/CustomControllerMode.hpp'][2] == '9658f5e15f50887caaaf5a71efc0096e9677d144'
            and after['src/modes/CustomControllerMode.cpp'][2] == '8cb336f31acd4c324b3ae1f8ef0827c14f15ee85',
            'C014 repaired source not adopted exact blobs')
    require(critical_tree(root, HANDOFF) == before == critical_tree(root, READY)
            and ancestor(root, B, HANDOFF) and ancestor(root, HANDOFF, READY)
            and not ancestor(root, C, HANDOFF), 'C014 handoff/READY contains source or wrong ancestry')
    ready = item(root, READY, 'GP-VAL-034')
    require(ready['status'] == 'READY' and ready['activation_state'] == 'NOT_APPLICABLE'
            and item(root, READY, 'GP-VAL-037')['status'] == 'DONE', '034 readiness/predecessor mismatch')
    text = raw_bytes(root, HANDOFF, QUEUE).decode()
    match = re.findall(r'<!-- gp-config014-handoff:start -->\s*```json\s*(.*?)\s*```\s*<!-- gp-config014-handoff:end -->', text, re.S)
    require(len(match) == 1, 'missing/duplicate C014 handoff')
    handoff = json.loads(match[0], object_pairs_hook=unique)
    require(handoff['candidate'] == C and handoff['base'] == B and handoff['candidate_tree'] == TREE
            and handoff['inventory'] == mapping['entries'] and handoff['raw_inventory_sha256'] == RAW
            and handoff['candidate_published_live_verified'] is True
            and handoff['candidate_firmware_integrated'] is False and handoff['gate_waivers'] is False,
            'C014 source-free handoff substitution')
    for filename, key in (('candidate-review.json', 'review_sha256'),
                          ('candidate-validation.json', 'validation_sha256')):
        record = handoff['reports'][filename]
        require(record['sha256'] == mapping[key]
                and sha((json.dumps(record['report'], indent=2) + '\n').encode()) == mapping[key],
                'C014 immutable execution receipt digest mismatch')
    review = handoff['reports']['candidate-review.json']['report']
    require(review['reviewed_sha'] == C and review['blocking_findings_for_bounded_candidate_handoff'] == []
            and review['verdict'] == 'APPROVED_FOR_EXACT_CANDIDATE_PUBLICATION_AND_SOURCE_FREE_HANDOFF_ONLY'
            and review['gate_waivers'] is False and review['hardware_acceptance'] is False,
            'C014 independent conformance receipt mismatch')
    authenticate_kbd_contract(root)
    return before, after

def current_integrity(root, head, expected):
    """Prove actual critical working bytes, index, modes and ignored input traps."""
    require(critical_tree(root, head) == expected, 'current critical source outside C014 contract')
    tags = _git(root, 'ls-files', '-v', '-z').decode().split('\0')
    for record in filter(None, tags):
        tag, path = record[0], record[2:]
        if path in expected:
            require(not tag.islower() and tag != 'S', 'assume-unchanged/skip-worktree critical trap: ' + path)
    staged = {}
    for record in _git(root, 'ls-files', '--stage', '-z').decode().split('\0'):
        if record:
            meta, path = record.split('\t'); mode, blob, stage = meta.split()
            if path in expected:
                require(stage == '0', 'unmerged critical index')
                staged[path] = (mode, 'blob', blob)
    require(staged == expected, 'critical index differs from committed source')
    for path, entry in expected.items():
        file = root / path
        require(file.is_file() and all(not p.is_symlink() for p in (file, *file.parents)),
                'critical missing/symlink input: ' + path)
        mode = '100755' if file.stat().st_mode & 0o111 else '100644'
        data = file.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require((mode, 'blob', blob) == entry, 'critical worktree bytes/mode mismatch: ' + path)
    dirty = set(); ignored = set(filter(None, _git(root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z").decode().split("\0")))
    for args in (('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z'),
                 ('ls-files', '--others', '--exclude-standard', '-z'),
                 ('ls-files', '--others', '--ignored', '--exclude-standard', '-z')):
        dirty.update(filter(None, _git(root, *args).decode().split('\0')))
    permitted_caches = set()
    for path in dirty:
        try:
            category = classify_path(path)
        except CorrespondenceError:
            category = 'UNKNOWN'
        require(category != 'CRITICAL', 'dirty/staged/untracked/ignored critical input: ' + path)
        cache = (any(path == prefix or path.startswith(prefix + '/') for prefix in IGNORED_ALLOWED_ROOTS)
                 or (path.startswith('tools/__pycache__/') and path.endswith('.pyc')))
        # Existing ignored build/custody/cache bytes never supply proof inputs.
        if path in ignored and cache:
            permitted_caches.add(path)
        else:
            require(path in GOVERNANCE_PATHS, 'dirty path outside finite C014 governance: ' + path)
            if (root / path).exists():
                current_bytes(root, path)
    return dirty - permitted_caches

def catalog(raw):
    value = json.loads(raw, object_pairs_hook=unique)
    require(set(value) == {'schema_version', 'accepted_transitions'}
            and type(value['schema_version']) is int and value['schema_version'] == 1
            and type(value['accepted_transitions']) is list and len(value['accepted_transitions']) <= 1,
            'C014 catalog fields/count mismatch')
    fields = {'work_order', 'candidate', 'build', 'parent', 'tree', 'review_commit', 'evidence_commit', 'integration'}
    for record in value['accepted_transitions']:
        require(type(record) is dict and set(record) == fields and record['work_order'] == 'GP-CONFIG-014'
                and record['candidate'] == C, 'unadopted C014 catalog record')
        for key in fields - {'work_order'}:
            immutable(record[key])
    return value['accepted_transitions']

def same_acceptance(a, b):
    return all(a[k] == b[k] for k in (*IDENTITIES, 'hardware_evidence_record',
                                    'hardware_result', 'hardware_evidence_gaps', 'hardware_evidence_dependency_satisfied'))

@original._proof_invocation
def processor_record(root, E, before, after):
    """Authenticate an actual source-free processor snapshot independently of I."""
    accepted = item(root, E, 'GP-CONFIG-014')
    require(accepted['status'] == 'HARDWARE_VALIDATED' and accepted['hardware_result'] == 'PASS'
            and accepted['hardware_evidence_gaps'] == []
            and accepted['hardware_evidence_dependency_satisfied'] is True, '014 E lacks complete native PASS')
    F, parent = immutable(accepted['candidate_git_sha']), immutable(accepted['candidate_base_configurator_sha'])
    require(_git(root, 'rev-list', '--parents', '-n', '1', F).decode().split() == [F, parent]
            and ancestor(root, C, F) and ancestor(root, READY, F)
            and not ancestor(root, F, E) and critical_tree(root, E) == before
            and critical_tree(root, F) == after, '014 F/source-free E ancestry or source mismatch')
    verify_correspondence(root, C, B, target=F, integrated=True, check_worktree=False)
    require(accepted['manual_acceptance_protocol_reference'] == PROTOCOL
            and accepted['manual_acceptance_protocol_version'] == 'GP_CONFIG_014_HW_V1', '014 protocol mismatch')
    digest = accepted['firmware_artifact_sha256']
    require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest)
            and accepted['preserved_firmware_artifact_locator'] ==
                f'local_backups/hardware-artifacts/{F}/{digest}/firmware.uf2', '014 artifact custody mismatch')
    reference = accepted['hardware_evidence_record']
    if reference == 'repo-json:' + EVIDENCE:
        evidence_root = E
    else:
        m = re.fullmatch(r'git-json:([0-9a-f]{40}):' + re.escape(EVIDENCE), str(reference))
        require(m is not None, '014 unsupported evidence reference')
        evidence_root = m.group(1)
        require(ancestor(root, evidence_root, E), '014 evidence root after processor E')
    payload = raw_bytes(root, evidence_root, EVIDENCE)
    native = dict(accepted, hardware_evidence_record='git-json:' + evidence_root + ':' + EVIDENCE)
    from check_glyph_agent_framework_docs import validate_work_order, validate_evidence_record
    validate_work_order(native, evidence_repo_root=root)
    validate_evidence_record(native, evidence_repo_root=root)
    evidence = json.loads(payload, object_pairs_hook=unique)
    ids = [row['id'] for row in evidence['steps']]
    require(len(ids) == len(set(ids)) and all(row in ids for row in REQUIRED_ROWS),
            '014 evidence required rows missing/duplicate')
    require(evidence['anomalies'] == [] and evidence['evidence_gaps'] == [], '014 acceptance has anomalies/gaps')
    review = None
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', READY + '..' + E).decode().split():
        state = item(root, revision, 'GP-CONFIG-014')
        if state['status'] in {'REVIEW', 'HARDWARE_TEST_REQUIRED'} and state['hardware_result'] is None:
            if all(state[k] == accepted[k] for k in IDENTITIES) and PROTOCOL in _tree(root, revision):
                record = {'build': F, 'tree': _git(root, 'rev-parse', F + '^{tree}').decode().strip(), 'parent': parent}
                original.validate_build_review(raw_bytes(root, revision, PROTOCOL).decode(), record, digest,
                                               accepted['preserved_firmware_artifact_locator'])
                review = revision
                break
    require(review is not None and review != E and ancestor(root, review, E)
            and ancestor(root, review, evidence_root) and not ancestor(root, F, review)
            and critical_tree(root, review) == before, '014 lacks source-free independent reviewed R before E')
    protocol = raw_bytes(root, review, PROTOCOL)
    require(raw_bytes(root, E, PROTOCOL) == protocol, '014 protocol changed between R/E')
    for row in evidence['steps']:
        require(row['id'] in protocol.decode(), '014 evidence row absent from reviewed protocol')
    return dict(work_order='GP-CONFIG-014', candidate=C, build=F, parent=parent,
                tree=_git(root, 'rev-parse', F + '^{tree}').decode().strip(),
                review_commit=review, evidence_commit=E, evidence_root=evidence_root,
                native=accepted, payload=payload, protocol=protocol,
                result=raw_bytes(root, E, RESULT))

@original._proof_invocation
def history(root, head, before, after):
    earliest = None; integrated = None; done = False
    c020 = item(root, B, 'GP-CONFIG-020')
    c020_literals = (predecessor.PROTOCOL, predecessor.EVIDENCE, predecessor.RESULT, predecessor.TRANSITIONS)
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', B + '..' + head).decode().split():
        if revision == KBD_C:
            require(_git(root, 'rev-list', '--parents', '-n', '1', KBD_C).decode().split() == [KBD_C, KBD_B]
                    and ancestor(root, KBD_B, B) and not ancestor(root, B, KBD_C),
                    'KBD historical sidebranch chronology mismatch')
            continue
        old = item(root, revision, 'GP-CONFIG-020')
        require(old['status'] == 'DONE' and same_acceptance(old, c020), '014 history erased/replaced accepted C020')
        for path in c020_literals:
            require(raw_bytes(root, revision, path) == raw_bytes(root, B, path), '014 history changed immutable C020 metadata')
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', READY + '..' + head).decode().split():
        state = item(root, revision, 'GP-CONFIG-014')
        records = catalog(raw_bytes(root, revision, TRANSITIONS)) if TRANSITIONS in _tree(root, revision) else []
        if records:
            require(earliest is not None, '014 integration catalog precedes processor E')
            record = records[0]
            require(all(record[k] == earliest[k] for k in ('candidate', 'build', 'parent', 'tree',
                                                          'review_commit', 'evidence_commit')),
                    '014 accepted catalog replaced earliest processor tuple')
            I = record['integration']
            require(ancestor(root, earliest['evidence_commit'], I) and ancestor(root, record['build'], I)
                    and ancestor(root, I, revision) and critical_tree(root, revision) == after,
                    '014 integration/catalog chronology or critical tree mismatch')
            require(integrated is None or integrated == record, '014 accepted catalog replacement')
            integrated = record
        if integrated is not None and ancestor(root, integrated['integration'], revision):
            require(bool(records), '014 accepted catalog removed after introduction')
        if state['hardware_result'] == 'PASS' or state['status'] in {'HARDWARE_VALIDATED', 'DONE'}:
            require(state['hardware_result'] == 'PASS' and state['status'] in {'HARDWARE_VALIDATED', 'DONE'}, '014 PASS in invalid native status')
            require(not done or state['status'] == 'DONE', '014 DONE status downgraded')
            if earliest is None:
                require(not records, '014 first PASS must be source-free E')
                earliest = processor_record(root, revision, before, after)
            else:
                require(same_acceptance(state, earliest['native']), '014 processor acceptance downgraded/replaced')
            if state['status'] == 'DONE':
                require(bool(records), '014 DONE lacks accepted integration catalog')
                done = True
        elif earliest is not None and ancestor(root, earliest['evidence_commit'], revision):
            require(False, '014 processor PASS erased/downgraded')
    return earliest, integrated

@original._proof_invocation
def authenticate(root):
    root = Path(root).resolve(); head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    require(ancestor(root, READY, head), 'C014 context lacks immutable 034 READY authority')
    before, after = critical_tree(root, B), critical_tree(root, C)
    current = critical_tree(root, head)
    require(current in (before, after), 'current critical tree outside accepted020/C014')
    dirty = current_integrity(root, head, current)
    overlays = authenticate_host_overlays(root, head)
    kbd = authenticate_kbd_coexistence(root, head)
    delta = set(filter(None, _git(root, 'diff', '--no-renames', '--name-only', '-z', B, head).decode().split('\0')))
    require(delta | dirty <= GOVERNANCE_PATHS | CRITICAL, 'unreviewed C014 governance/source delta')
    for path in delta:
        entry = _tree(root, head).get(path)
        require(entry is not None and entry[:2] == ('100644', 'blob'), 'C014 changed path deleted/unsafe mode: ' + path)
    predecessor._owner_direction_scope(root, head, delta | {predecessor.OWNER_DIRECTION})
    c020 = item(root, B, 'GP-CONFIG-020')
    for raw in (raw_bytes(root, head, QUEUE), current_bytes(root, QUEUE), _git(root, 'show', ':' + QUEUE)):
        state = state_from(raw, 'GP-CONFIG-020')
        require(same_acceptance(state, c020) and state['status'] == 'DONE', '014 changed accepted C020 identity/result')
    for path in (predecessor.PROTOCOL, predecessor.EVIDENCE, predecessor.RESULT, predecessor.TRANSITIONS):
        require(raw_bytes(root, head, path) == raw_bytes(root, B, path)
                and current_bytes(root, path) == raw_bytes(root, B, path)
                and _git(root, 'show', ':' + path) == raw_bytes(root, B, path), '014 changed immutable C020 metadata')
    for path in original.FROZEN:
        require(current_bytes(root, path) == raw_bytes(root, original.B, path), '014 changed frozen historical fixture')
    for path in HOSTS - HOST_OVERLAYS:
        if path in _tree(root, head) or (root / path).exists():
            require(current_bytes(root, path) == raw_bytes(root, C, path), '014 frozen candidate host substitution')
    state = item(root, head, 'GP-CONFIG-014')
    require(state['status'] != 'HARDWARE_FAILED' and state['hardware_result'] != 'FAIL', 'failed014 cannot validate')
    source_contract(root)
    prior = predecessor.authenticate_committed_predecessor(root, B)
    require(prior['phase'] == 'ACCEPTED_TRANSITION', 'C014 predecessor not actually accepted')
    records = catalog(current_bytes(root, TRANSITIONS))
    if TRANSITIONS in _tree(root, head):
        require(current_bytes(root, TRANSITIONS) == raw_bytes(root, head, TRANSITIONS), 'uncommitted014 accepted catalog')
    else:
        require(records == [], 'uncommitted014 acceptance')
    processor, accepted = history(root, head, before, after)
    require(records == ([accepted] if accepted else []), '014 current catalog/history mismatch')
    phase = 'BASELINE'; protected = predecessor.CRITICAL
    if current == after:
        require(ancestor(root, C, head), 'C014 source replay without candidate ancestry')
        verify_correspondence(root, C, B, target=head, integrated=True, check_worktree=False)
        phase = 'CANDIDATE_VALIDATION_ONLY'; protected |= CRITICAL
    require(not (state['hardware_result'] == 'PASS' or state['status'] in {'HARDWARE_VALIDATED', 'DONE'})
            or processor is not None, '014 PASS without genuine processor E')
    metadata = frozenset((predecessor.PROTOCOL, predecessor.EVIDENCE, predecessor.RESULT))
    roots = set(ROOTS) | set(prior['object_roots'])
    if processor:
        require(same_acceptance(state, processor['native']), '014 current processor tuple drift')
        for path, expected in ((EVIDENCE, processor['payload']), (PROTOCOL, processor['protocol']),
                               (RESULT, processor['result'])):
            require(current_bytes(root, path) == expected and raw_bytes(root, head, path) == expected
                    and _git(root, 'show', ':' + path) == expected, '014 accepted evidence/protocol/result substitution')
        for raw in (current_bytes(root, QUEUE), _git(root, 'show', ':' + QUEUE)):
            require(same_acceptance(state_from(raw, 'GP-CONFIG-014'), state), '014 live/index PASS tuple drift')
        roots.update(processor[k] for k in ('build', 'parent', 'review_commit', 'evidence_commit', 'evidence_root'))
        metadata |= frozenset((PROTOCOL, EVIDENCE, RESULT))
        if current == before:
            require(not accepted and not ancestor(root, processor['build'], head), 'source-free014 E contains integrated F')
            phase = 'SOURCE_FREE_PROCESSOR'
        else:
            require(accepted is not None, 'integrated014 PASS lacks accepted catalog')
    if accepted:
        require(current == after and processor is not None, '014 accepted catalog on baseline')
        verify_correspondence(root, accepted['build'], accepted['parent'], target=head,
                              integrated=True, check_worktree=False)
        phase = 'ACCEPTED_TRANSITION'; roots.add(accepted['integration'])
    source_candidates = {p: predecessor.C_R for p in predecessor.CRITICAL}
    if current == after:
        source_candidates.update({p: C for p in CRITICAL})
    return dict(phase=phase, contract='c014_capacity', candidate=C, base=B, target=head,
                critical_paths=protected, accepted_metadata_paths=metadata,
                changed_paths=frozenset(delta | dirty), object_roots=frozenset(roots),
                source_candidates=source_candidates, host_overlay_paths=overlays,
                kbd_host_paths=kbd, evidence_commit=processor['evidence_commit'] if processor else None)

def verify_current_source(root, path, historical_sha256=None):
    root = Path(root).resolve(); old = raw_bytes(root, original.B, path)
    if historical_sha256 is not None:
        require(sha(old) == historical_sha256, 'historical source identity mismatch: ' + path)
    current = current_bytes(root, path)
    if current != old:
        proof = authenticate(root)
        owner = proof['source_candidates'].get(path)
        require(owner is not None and current == raw_bytes(root, owner, path), 'unadopted014 source overlay: ' + path)
    return old

@original._proof_invocation
def authenticate_kbd_contract(root):
    """Bind known immutable H1 object closure even before optional publication."""
    require(_git(root, 'rev-list', '--parents', '-n', '1', KBD_C).decode().split() == [KBD_C, KBD_B]
            and _git(root, 'rev-parse', KBD_C + '^{tree}').decode().strip() == KBD_TREE
            and sha(_git(root, 'diff-tree', '-r', '--no-renames', '--raw', '-z', KBD_B, KBD_C)) == KBD_RAW,
            'KBD immutable candidate parent/tree/raw inventory mismatch')
    before, after = _tree(root, KBD_B), _tree(root, KBD_C)
    metadata = frozenset(('docs/runtime_config/fixtures/runtime_config_validation_manifest.json',
                         'docs/runtime_config/fixtures/glyph_checker_census.json',
                         'docs/runtime_config/fixtures/runtime_config_validation_health.json',
                         'docs/runtime_config/runtime_config_validation_health.md'))
    require({p for p in before.keys() | after.keys() if before.get(p) != after.get(p)} == KBD_HOSTS | metadata,
            'KBD immutable nine-path membership mismatch')
    require(len(KBD_HOSTS) == 5 and len(KBD_DEPENDENCY_PINS) == 28
            and critical_tree(root, KBD_B) == critical_tree(root, KBD_C),
            'KBD immutable host/dependency/critical inventory mismatch')
    for path, pin in dict(KBD_DEPENDENCY_PINS, **KBD_HOST_PINS).items():
        expected = (pin['mode'], 'blob', pin['blob'])
        require(expected[:2] == ('100644', 'blob') and after.get(path) == expected
                and sha(raw_bytes(root, KBD_C, path)) == pin['sha256'], 'KBD immutable literal pin mismatch: ' + path)
        if path in KBD_HOSTS:
            require(path not in before, 'KBD host path not an original addition')
        else:
            require(all(_tree(root, revision).get(path) == expected for revision in (KBD_B, KBD_AUTHORITY, B, C)),
                    'KBD original/current literal dependency changed: ' + path)
    for path in metadata:
        require(before[path][:2] == after[path][:2] == ('100644', 'blob'), 'KBD metadata mode mismatch')
    return KBD_HOSTS

@original._proof_invocation
def authenticate_kbd_coexistence(root, head):
    """Only the five immutable Ckbd outputs may accompany unchanged014 inputs."""
    present = KBD_HOSTS & _tree(root, head).keys()
    live = {p for p in KBD_HOSTS if (root / p).exists() or (root / p).is_symlink()}
    indexed = {record.split('\t', 1)[1] for record in
               _git(root, 'ls-files', '--stage', '-z').decode().split('\0')
               if record and record.split('\t', 1)[1] in KBD_HOSTS}
    if not present and not live and not indexed:
        return frozenset()
    require(present == live == indexed == KBD_HOSTS and len(KBD_DEPENDENCY_PINS) == 28,
            'KBD incomplete exact host/dependency inventory')
    require(ancestor(root, KBD_C, head), 'KBD host files lack immutable candidate ancestry')
    pins = dict(KBD_DEPENDENCY_PINS, **KBD_HOST_PINS)
    for path, pin in pins.items():
        expected = (pin['mode'], 'blob', pin['blob'])
        require(pin['mode'] == '100644' and _tree(root, head).get(path) == expected,
                'KBD committed mode/blob substitution: ' + path)
        require(_tree(root, KBD_C).get(path) == expected
                and sha(raw_bytes(root, KBD_C, path)) == pin['sha256'],
                'KBD immutable source/host pin mismatch: ' + path)
        if path in KBD_DEPENDENCY_PINS:
            require(_tree(root, KBD_B).get(path) == expected
                    and _tree(root, KBD_AUTHORITY).get(path) == expected,
                    'KBD historical dependency authority mismatch: ' + path)
        data = current_bytes(root, path)
        require(sha(data) == pin['sha256'] and _git(root, 'show', ':' + path) == data,
                'KBD live/index dependency/host substitution: ' + path)
        require(_git(root, 'ls-files', '--stage', '--', path).decode().split()[:3]
                == [pin['mode'], pin['blob'], '0'], 'KBD index mode/blob substitution: ' + path)
    return KBD_HOSTS

def authenticate_host_overlays(root, head):
    present = HOST_OVERLAYS & _tree(root, head).keys()
    # Old baseline tools are allowed only at their exact immutable B blobs.
    adopted = any(_tree(root, head).get(p) != _tree(root, B).get(p) for p in present)
    if not adopted:
        return frozenset()
    require(set(HOST_OVERLAY_BLOBS) == HOST_OVERLAYS and present == HOST_OVERLAYS, '034 incomplete finite host overlay inventory')
    for path, pin in HOST_OVERLAY_BLOBS.items():
        require(_tree(root, head).get(path) == (pin['mode'], 'blob', pin['blob']), '034 committed host overlay differs from reviewed literal: ' + path)
        require(sha(raw_bytes(root, head, path)) == pin['sha256'] and sha(current_bytes(root, path)) == pin['sha256']
                and _git(root, 'show', ':' + path) == current_bytes(root, path), '034 host overlay live/index substitution: ' + path)
    return frozenset(present)

def verify_historical_dependency(root, path, expected_blob, expected_sha256):
    root = Path(root).resolve(); old = raw_bytes(root, B, path)
    require(_tree(root, B)[path] == ('100644', 'blob', expected_blob)
            and sha(old) == expected_sha256, '014 historical dependency pin mismatch: ' + path)
    proof = authenticate(root)
    require(path in HOST_OVERLAYS and path in proof['host_overlay_paths'], 'unadopted034 host overlay: ' + path)
    current = current_bytes(root, path)
    require(current == raw_bytes(root, proof['target'], path)
            and _git(root, 'show', ':' + path) == current, '034 host overlay is not committed/index/live exact')
    return old
