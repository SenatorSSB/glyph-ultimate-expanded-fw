"""Finite GP-VAL-035 proof for the exact C017 NeoPixel candidate.

Candidate validation is a source proof. Only a later exact F017/UF2/HEP record
can turn it into an accepted hardware transition.
"""
from __future__ import annotations

import hashlib
import json
import re
import stat
from pathlib import Path

import glyph_c014_campaign_transition as previous
from glyph_hardware_correspondence import CorrespondenceError, classify_path, verify_correspondence
from glyph_tracked_worktree_integrity import IGNORED_ALLOWED_ROOTS

C = '478f438804275f3e0c23e6f36bfd26e34aa343bf'
B = 'a6b7750e271324972c51915563fe0dc22f941f95'
TREE = 'd7bd33ae51c5984090c9a1b0af863aa0957d0840'
RAW = '4a5674c786726f30a98067560807e4739ba6c2c644b706425f03c552171792d2'
HANDOFF = '0eb7f23b9f6b765e717d5e7455faa615695f0ebb'
READY = '9ce55e71eff2be6fee366b52434042985de263e6'
MAPPING = 'docs/runtime_config/fixtures/gp_val035_c017_transition.json'
TRANSITIONS = 'docs/runtime_config/fixtures/gp_val035_accepted_transitions.json'
MAPPING_SHA256 = 'd4937c33a9086585f3d1743ea853cebd246cd5b5bb740a31ea08cc546c5fa5b0'
QUEUE = previous.QUEUE
PROTOCOL = 'docs/agent_framework/GP_CONFIG_017_HARDWARE_PROTOCOL.md'
EVIDENCE = 'docs/calibration/fixtures/gp_config_017_hardware_evidence.json'
RESULT = 'docs/calibration/gp_config_017_hardware_result.md'
SOURCE = 'HAL/pico/include/comms/NeoPixelBackend.hpp'
OLD_SOURCE_BLOB = '843eb9b937ccebc616679b0ced24b805d8a6290d'
NEW_SOURCE_BLOB = '4724544d5989fdf403c5e6e0accab721371bc9d3'
ORIGINAL_016_BASE = '0da68bdab9bf0fed4ed595538bea9aba7d2f49f3'
CONFIG019_CHECKER_BLOB = 'd291ba978816d9ea0caea3eefeb798ad8e5ebbe6'
CONFIG019_CHECKER_SHA256 = '27b0e5afa9cf1637a71dc00a60fd6702382d364824eedecebe09923e3e558d42'
HISTORICAL_WRAPPER = 'tools/check_glyph_neopixel_historical_replay.py'
HISTORICAL_WRAPPER_BLOB = 'b8f5ba1dd5574b5c5801ad38ac08081c62cb3c43'
HISTORICAL_WRAPPER_SHA256 = '2a9d3c8eef434d890dc1cf9eeec8fe3ca5f37235de68417a6146dcd6d621c9da'
CRITICAL = frozenset((SOURCE,))
HOSTS = frozenset((
    PROTOCOL,
    'docs/runtime_config/fixtures/gp_config_017_neopixel_repaired_current.json',
    'docs/runtime_config/gp_config_017_neopixel_repaired_current.md',
    'tools/check_glyph_gp_config_017_neopixel_repaired_current.py',
    'tools/fixtures/gp_config017_neopixel_repaired_current/include/FastLED.h',
    'tools/fixtures/gp_config017_neopixel_repaired_current/neo_harness.cpp',
))
METADATA = frozenset((
    'docs/runtime_config/fixtures/glyph_checker_census.json',
    'docs/runtime_config/fixtures/runtime_config_validation_manifest.json',
    'docs/runtime_config/fixtures/runtime_config_validation_health.json',
    'docs/runtime_config/runtime_config_validation_health.md',
))
NEW_PATHS = frozenset((MAPPING, TRANSITIONS,
    'tools/glyph_c017_campaign_transition.py',
    'tools/test_glyph_c017_campaign_transition.py'))
# These are exact existing/new host inputs. Classification remains separately
# fail-closed in glyph_hardware_correspondence; this set never makes HAL metadata.
GOVERNANCE_PATHS = (previous.GOVERNANCE_PATHS | HOSTS | METADATA | NEW_PATHS |
    frozenset((EVIDENCE, RESULT,
        'docs/agent_framework/PORTFOLIO_20261005_0028_CURATOR.md',
        'tools/check_glyph_gp_config019_usb_name_selection.py',
        HISTORICAL_WRAPPER)))
ROOTS = (previous.ROOTS | frozenset((C, B, HANDOFF, READY, ORIGINAL_016_BASE)))

require = previous.require
_git = previous._git
_tree = previous._tree
raw_bytes = previous.raw_bytes
current_bytes = previous.current_bytes
critical_tree = previous.critical_tree
ancestor = previous.ancestor
item = previous.item
unique = previous.unique


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def present(root: Path) -> bool:
    root = Path(root).resolve()
    head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    tree = _tree(root, head)
    return any(path in tree or (root / path).exists() or (root / path).is_symlink()
               for path in (MAPPING, TRANSITIONS, 'tools/glyph_c017_campaign_transition.py'))


def _handoff(root: Path) -> dict:
    text = raw_bytes(root, HANDOFF, QUEUE).decode()
    start = '<!-- gp-config017-handoff-val035-activation:start -->'
    end = '<!-- gp-config017-handoff-val035-activation:end -->'
    require(text.count(start) == text.count(end) == 1, '017 handoff marker substitution')
    block = text.split(start)[1].split(end)[0].strip()
    require(block.startswith('```json') and block.endswith('```'), '017 handoff fence substitution')
    value = json.loads(block[7:-3], object_pairs_hook=unique)
    require(value['schema_name'] == 'glyph_gp_config017_candidate_handoff_val035_activation'
            and value['schema_version'] == 1
            and (value['candidate'], value['canonical_base'], value['candidate_tree'],
                 value['candidate_direct_parent']) == (C, B, TREE, B)
            and value['review_sha256'] == '692494a498d88139fc146b4558acb413efe3698e110f4a881a8ad43856354dc6'
            and value['source_proof_sha256'] == 'c91c5ebb25ad5fcc6a85dbe609693fb5dbeed2292029e702a7f06ad6d39a8a28'
            and value['source_free_canonical'] is True and value['gate_waivers'] is False,
            '017 handoff identity/scope substitution')
    for key, digest in (('independent_review', value['review_sha256']),
                        ('source_proof', value['source_proof_sha256'])):
        require(sha((json.dumps(value[key], indent=2) + '\n').encode()) == digest,
                '017 handoff report digest substitution: ' + key)
    review = value['independent_review']
    require(review['reviewed_sha'] == C and review['reviewed_tree'] == TREE
            and review['verdict'] == 'APPROVED' and review['blocking_findings'] == []
            and review['candidate_conformance']['raw_inventory_sha256'] == RAW
            and review['candidate_conformance']['complete_inventory_path_count'] == 11,
            '017 independent conformance receipt substitution')
    return value


@previous.original._proof_invocation
def source_contract(root: Path):
    """Authenticate the immutable C017 envelope and the one exact source move."""
    root = Path(root).resolve()
    require(_git(root, 'rev-list', '--parents', '-n', '1', C).decode().split() == [C, B]
            and _git(root, 'rev-parse', C + '^{tree}').decode().strip() == TREE
            and sha(_git(root, 'diff-tree', '-r', '--no-renames', '--raw', '-z', B, C)) == RAW,
            '017 candidate parent/tree/raw inventory substitution')
    require(ancestor(root, READY, _git(root, 'rev-parse', 'HEAD').decode().strip())
            and ancestor(root, B, HANDOFF) and ancestor(root, HANDOFF, READY)
            and not ancestor(root, C, HANDOFF), '017 source-free READY chronology')
    ready = item(root, READY, 'GP-VAL-035')
    require(ready['status'] == 'READY' and item(root, READY, 'GP-CONFIG-017')['status'] == 'REVIEW'
            and item(root, READY, 'GP-VAL-034')['status'] == 'DONE', '017 READY/014 predecessor state')
    mapping_raw = current_bytes(root, MAPPING)
    require(sha(mapping_raw) == MAPPING_SHA256, '017 mapping substitution')
    mapping = json.loads(mapping_raw, object_pairs_hook=unique)
    require(set(mapping) == {'schema_name', 'schema_version', 'work_order', 'candidate', 'base',
                            'tree', 'raw_inventory_sha256', 'entries', 'handoff', 'ready',
                            'review_sha256', 'source_proof_sha256'}
            and mapping['schema_name'] == 'glyph_gp_val035_c017_transition'
            and mapping['schema_version'] == 1 and mapping['work_order'] == 'GP-VAL-035'
            and tuple(mapping[k] for k in ('candidate', 'base', 'tree', 'raw_inventory_sha256',
                                           'handoff', 'ready')) == (C, B, TREE, RAW, HANDOFF, READY),
            '017 mapping identity substitution')
    handoff = _handoff(root)
    require(mapping['review_sha256'] == handoff['review_sha256']
            and mapping['source_proof_sha256'] == handoff['source_proof_sha256'],
            '017 mapping receipt substitution')
    before, after = _tree(root, B), _tree(root, C)
    paths = {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
    require(paths == CRITICAL | HOSTS | METADATA and len(paths) == len(mapping['entries']) == 11,
            '017 finite eleven-path membership mismatch')
    entries = {row['path']: row for row in mapping['entries']}
    require(set(entries) == paths and len(entries) == len(mapping['entries']),
            '017 inventory duplicate/omission')
    for path in paths:
        row = entries[path]; old = before.get(path); new = after.get(path)
        require(set(row) == {'path', 'old_mode', 'new_mode', 'old_blob', 'new_blob',
                            'status', 'sha256', 'firmware_build_input'},
                '017 inventory fields mismatch: ' + path)
        require(new[:2] == ('100644', 'blob') and row['new_mode'] == '100644'
                and row['new_blob'] == new[2] and row['sha256'] == sha(raw_bytes(root, C, path))
                and (row['old_mode'], row['old_blob'], row['status']) ==
                    ((old[0], old[2], 'M') if old else ('000000', '0' * 40, 'A'))
                and row['firmware_build_input'] is (path == SOURCE),
                '017 inventory blob/mode/role substitution: ' + path)
    require(handoff['independent_review']['candidate_conformance']['inventory'] == mapping['entries'],
            '017 reviewed inventory differs from committed mapping')
    bt, ct = critical_tree(root, B), critical_tree(root, C)
    require(len(bt) == len(ct) == 236 and {p for p in bt.keys() | ct.keys()
            if bt.get(p) != ct.get(p)} == CRITICAL
            and bt[SOURCE] == ('100644', 'blob', OLD_SOURCE_BLOB)
            and ct[SOURCE] == ('100644', 'blob', NEW_SOURCE_BLOB),
            '017 critical tree differs outside one HAL source')
    old = raw_bytes(root, B, SOURCE); new = raw_bytes(root, C, SOURCE)
    speed = b'        uint8_t deltaHue = (diff/1000) * (interval * _config->speed);\n\n'
    guard = b'        if(_config == nullptr) {'
    require(old.count(speed) == new.count(speed) == old.count(guard) == new.count(guard) == 1
            and old.replace(speed, b'', 1) == new.replace(speed, b'', 1)
            and old.index(speed) < old.index(guard) < new.index(speed)
            and old.index(b'        prevTime = time;') < old.index(speed)
            and new.index(b'        prevTime = time;') < new.index(guard),
            '017 source change is not sole speed/guard reordering')
    require(_tree(root, B).get('docs/agent_framework/PORTFOLIO_20261005_0028_CURATOR.md')
            == ('100644', 'blob', '0353396a4d17ff4781f90fa1995ff877211ce6f4'),
            '017 predecessor changed immutable 0028 control-plane entry')
    original016_fixture = 'docs/runtime_config/fixtures/neopixel_null_sendreport_characterization.json'
    fixture = json.loads(raw_bytes(root, B, original016_fixture), object_pairs_hook=unique)
    require(fixture['base_configurator_sha'] == ORIGINAL_016_BASE
            and [row['path'] for row in fixture['production_sources']] ==
                [SOURCE, 'config/glyph/common/src/config.cpp']
            and fixture['production_sources'][0]['sha256'] == sha(old)
            and fixture['production_sources'][1]['sha256'] ==
                sha(raw_bytes(root, B, 'config/glyph/common/src/config.cpp'))
            and _tree(root, B)[original016_fixture] == _tree(root, C)[original016_fixture]
            and _tree(root, B)['tools/check_glyph_neopixel_null_sendreport_characterization.py'] ==
                _tree(root, C)['tools/check_glyph_neopixel_null_sendreport_characterization.py'],
            '017 changed immutable 016 source/provenance fixture')
    _git(root, 'cat-file', '-e', ORIGINAL_016_BASE + '^{commit}')
    return bt, ct


@previous.original._proof_invocation
def predecessor_contract(root: Path):
    """Prove accepted 014 at immutable B017 without the old 0028 scope claim."""
    root = Path(root).resolve()
    before, after = previous.source_contract(root)
    require(critical_tree(root, B) == after, '017 base does not retain accepted014 critical tree')
    c020 = previous.predecessor.authenticate_committed_predecessor(root, previous.B)
    require(c020['phase'] == 'ACCEPTED_TRANSITION', '017 lacks accepted020 predecessor')
    processor, accepted = previous.history(root, B, before, after)
    require(processor is not None and accepted is not None
            and previous.catalog(raw_bytes(root, B, previous.TRANSITIONS)) == [accepted]
            and item(root, B, 'GP-CONFIG-014')['status'] == 'DONE'
            and item(root, B, 'GP-CONFIG-014')['hardware_result'] == 'PASS'
            and critical_tree(root, processor['build']) == after
            and ancestor(root, processor['build'], B),
            '017 base lacks authentic 014 processor/catalog/integration')
    previous.authenticate_kbd_contract(root)
    previous.authenticate_config019_contract(root)
    require(ancestor(root, previous.CONFIG019_ADOPTION, B), '017 lacks accepted 019 authority')
    return dict(processor, c020_object_roots=c020['object_roots']), accepted


def _stage_and_live(root: Path, head: str, path: str, expected: tuple[str, str, str]):
    require(expected[:2] == ('100644', 'blob'), 'unsafe017 host mode: ' + path)
    stage = list(filter(None, _git(root, 'ls-files', '--stage', '-z', '--', path)
                        .decode().split('\0')))
    require(stage == [f'{expected[0]} {expected[2]} 0\t{path}'], '017 host index substitution: ' + path)
    flags = _git(root, 'ls-files', '-v', '-z', '--', path).decode().split('\0')
    require(len(flags) == 2 and flags[0] == 'H ' + path, '017 host index flag trap: ' + path)
    data = current_bytes(root, path)
    require(data == raw_bytes(root, head, path), '017 host working bytes substitution: ' + path)


@previous.original._proof_invocation
def verify019_overlay(root: Path, head: str):
    """Preserve original 019 contract; authenticate only its reviewed live overlay."""
    root = Path(root).resolve()
    previous.authenticate_config019_contract(root)
    require(ancestor(root, previous.CONFIG019_ADOPTION, head), '019 overlay lost adoption')
    paths = (previous.CONFIG019_HOSTS | previous.CONFIG019_OVERLAY_PATHS |
             frozenset(previous.CONFIG019_AUTHORITY_PINS) |
             frozenset(previous.CONFIG019_CURRENT_SOURCE_PINS))
    base = _tree(root, B)
    for path in paths:
        expected = base.get(path)
        require(expected is not None and expected[:2] == ('100644', 'blob'),
                '017 019 predecessor pin missing: ' + path)
        if path == previous.CONFIG019_CHECKER:
            require(expected[2] == previous.CONFIG019_OVERLAY_PINS[path]['blob'],
                    '017 changed original 019 checker base pin')
            expected = ('100644', 'blob', CONFIG019_CHECKER_BLOB)
        require(_tree(root, head).get(path) == expected,
                '017 019 overlay differs from predecessor: ' + path)
        _stage_and_live(root, head, path, expected)
    old = raw_bytes(root, B, previous.CONFIG019_CHECKER)
    new = current_bytes(root, previous.CONFIG019_CHECKER)
    old_guard = b'''        from glyph_c014_campaign_transition import authenticate, CRITICAL, C
        differences = {p for p in committed.keys() | accepted.keys() if committed.get(p) != accepted.get(p)}
        require(differences <= CRITICAL, 'critical drift outside existing exact C014 candidate')
        proof = authenticate(REPOSITORY_ROOT)
        require(proof['target'] == head and proof['phase'] in
                {'CANDIDATE_VALIDATION_ONLY', 'ACCEPTED_TRANSITION'} and
                all(proof['source_candidates'].get(p) == C for p in differences),
                'C014 source compatibility lacks existing authenticated phase')
'''
    new_guard = b'''        from glyph_campaign_transition import authenticate
        proof = authenticate(REPOSITORY_ROOT)
        differences = {p for p in committed.keys() | accepted.keys() if committed.get(p) != accepted.get(p)}
        require(differences <= proof['critical_paths'], 'critical drift outside authenticated campaign source')
        phase = (proof['phase'] in {'CANDIDATE_VALIDATION_ONLY', 'ACCEPTED_TRANSITION'} or
                 (proof.get('contract') == 'c017_neopixel' and
                  proof['phase'] in {'BASELINE', 'SOURCE_FREE_PROCESSOR'} and
                  proof.get('predecessor_phase') == 'ACCEPTED_TRANSITION'))
        require(proof['target'] == head and phase and
                all(proof['source_candidates'].get(p) is not None and
                    git_read('show', head + ':' + p) ==
                    git_read('show', proof['source_candidates'][p] + ':' + p)
                    for p in differences),
                'current source compatibility lacks exact authenticated campaign ownership')
'''
    require(old.count(old_guard) == 1 and old.replace(old_guard, new_guard, 1) == new
            and sha(new) == CONFIG019_CHECKER_SHA256,
            '017 019 guard overlay changed outside exact reviewed body')
    # The original 041 manifest entry must survive metadata regeneration.
    manifest = json.loads(current_bytes(root,
        'docs/runtime_config/fixtures/runtime_config_validation_manifest.json'), object_pairs_hook=unique)
    prior = json.loads(raw_bytes(root, B,
        'docs/runtime_config/fixtures/runtime_config_validation_manifest.json'), object_pairs_hook=unique)
    row = lambda x: [e for e in x['entries'] if e['id'] == 'gp_config019_usb_name_selection']
    require(len(row(manifest)) == len(row(prior)) == 1,
            '017 missing/duplicate accepted019 manifest lane')
    old_row, new_row = row(prior)[0], row(manifest)[0]
    expected_row = dict(old_row)
    expected_row['source_dependencies'] = sorted(set(old_row['source_dependencies']) |
                                                {'tools/glyph_campaign_transition.py'})
    require(new_row == expected_row and
            sha(json.dumps(old_row, sort_keys=True, separators=(',', ':')).encode()) ==
            previous.CONFIG019_MANIFEST_ENTRY_SHA256,
            '017 modified accepted019 manifest beyond exact new helper dependency')
    return previous.CONFIG019_HOSTS


def _current_integrity(root: Path, head: str, expected: dict):
    """Check every critical byte and finite dirty host, including ignored inputs."""
    require(critical_tree(root, head) == expected, '017 current critical tree substitution')
    index = {}
    for record in filter(None, _git(root, 'ls-files', '--stage', '-z').decode().split('\0')):
        meta, path = record.split('\t'); mode, blob, stage = meta.split()
        if path in expected:
            require(stage == '0', '017 unmerged critical input: ' + path)
            index[path] = (mode, 'blob', blob)
    require(index == expected, '017 critical index differs from committed tree')
    tags = {r[2:]: r[0] for r in filter(None, _git(root, 'ls-files', '-v', '-z').decode().split('\0'))}
    for path, entry in expected.items():
        require(path in tags and not tags[path].islower() and tags[path] != 'S',
                '017 critical index flag trap: ' + path)
        file = root / path
        require(file.is_file() and not file.is_symlink()
                and all(not p.is_symlink() for p in file.parents if p != root.parent),
                '017 critical missing/symlink input: ' + path)
        mode = '100755' if file.stat().st_mode & 0o111 else '100644'
        data = file.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require((mode, 'blob', blob) == entry, '017 critical live mode/bytes substitution: ' + path)
    ignored = set(filter(None, _git(root, 'ls-files', '--others', '--ignored',
                                    '--exclude-standard', '-z').decode().split('\0')))
    dirty = set()
    for args in (('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z'),
                 ('ls-files', '--others', '--exclude-standard', '-z'),
                 ('ls-files', '--others', '--ignored', '--exclude-standard', '-z')):
        dirty.update(filter(None, _git(root, *args).decode().split('\0')))
    permitted_cache = set()
    for path in dirty:
        try: category = classify_path(path)
        except CorrespondenceError: category = 'UNKNOWN'
        require(category != 'CRITICAL', '017 dirty critical input: ' + path)
        cache = (any(path == prefix or path.startswith(prefix + '/') for prefix in IGNORED_ALLOWED_ROOTS)
                 or (path.startswith('tools/__pycache__/') and path.endswith('.pyc')))
        if path in ignored and cache:
            permitted_cache.add(path)
        else:
            require(path in GOVERNANCE_PATHS, '017 dirty path outside finite governance: ' + path)
            if (root / path).exists():
                current_bytes(root, path)
    return dirty - permitted_cache


def _catalog(raw: bytes):
    value = json.loads(raw, object_pairs_hook=unique)
    require(set(value) == {'schema_version', 'accepted_transitions'} and
            value['schema_version'] == 1 and type(value['accepted_transitions']) is list and
            len(value['accepted_transitions']) <= 1, '017 catalog fields/count substitution')
    fields = {'work_order', 'candidate', 'build', 'parent', 'tree',
              'review_commit', 'evidence_commit', 'integration'}
    for record in value['accepted_transitions']:
        require(type(record) is dict and set(record) == fields and record['work_order'] == 'GP-CONFIG-017'
                and record['candidate'] == C and
                all(re.fullmatch('[0-9a-f]{40}', record[k]) for k in fields - {'work_order'}),
                '017 catalog record substitution')
    return value['accepted_transitions']


@previous.original._proof_invocation
def authenticate(root: Path):
    root = Path(root).resolve()
    head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    before, after = source_contract(root)
    predecessor, old_accepted = predecessor_contract(root)
    current = critical_tree(root, head)
    require(current in (before, after), '017 current source outside B/C critical trees')
    dirty = _current_integrity(root, head, current)
    delta = set(filter(None, _git(root, 'diff', '--no-renames', '--name-only', '-z', B, head)
                       .decode().split('\0')))
    require(delta | dirty <= GOVERNANCE_PATHS | CRITICAL,
            '017 unreviewed governance/source delta')
    tree = _tree(root, head)
    for path in delta:
        require(tree.get(path, ())[:2] == ('100644', 'blob'),
                '017 deleted/nonregular changed path: ' + path)
    for path in HOSTS:
        if path in tree:
            require(tree[path] == _tree(root, C)[path], '017 candidate host substitution: ' + path)
            _stage_and_live(root, head, path, tree[path])
    require(tree.get(HISTORICAL_WRAPPER) == ('100644', 'blob', HISTORICAL_WRAPPER_BLOB)
            and sha(current_bytes(root, HISTORICAL_WRAPPER)) == HISTORICAL_WRAPPER_SHA256,
            '017 historical wrapper substitution')
    _stage_and_live(root, head, HISTORICAL_WRAPPER, tree[HISTORICAL_WRAPPER])
    for path in METADATA:
        require(tree.get(path, ())[:2] == ('100644', 'blob'), '017 metadata mode substitution: ' + path)
    require(current_bytes(root, MAPPING) == raw_bytes(root, head, MAPPING)
            and _git(root, 'show', ':' + MAPPING) == current_bytes(root, MAPPING),
            '017 uncommitted mapping')
    records = _catalog(current_bytes(root, TRANSITIONS))
    require(records == (_catalog(raw_bytes(root, head, TRANSITIONS)) if TRANSITIONS in tree else []),
            '017 uncommitted accepted catalog')
    state = item(root, head, 'GP-CONFIG-017')
    require(state['status'] != 'HARDWARE_FAILED' and state['hardware_result'] != 'FAIL',
            'failed017 cannot validate')
    for path in (previous.PROTOCOL, previous.EVIDENCE, previous.RESULT, previous.TRANSITIONS):
        require(raw_bytes(root, head, path) == raw_bytes(root, B, path)
                and current_bytes(root, path) == raw_bytes(root, B, path),
                '017 replaced accepted014 record: ' + path)
    for path in previous.original.FROZEN:
        require(current_bytes(root, path) == raw_bytes(root, previous.original.B, path),
                '017 changed frozen historical fixture: ' + path)
    kbd = previous.authenticate_kbd_coexistence(root, head)
    overlays = previous.authenticate_host_overlays(root, head)
    config019 = verify019_overlay(root, head)
    # Literal B017 documents a preexisting 0028 applicability failure in old034.
    require(_tree(root, B)['docs/agent_framework/PORTFOLIO_20261005_0028_CURATOR.md']
            == tree['docs/agent_framework/PORTFOLIO_20261005_0028_CURATOR.md'],
            '017 changed immutable 0028 path')
    phase = 'BASELINE'
    protected = previous.predecessor.CRITICAL | previous.CRITICAL
    source_candidates = {p: previous.predecessor.C_R for p in previous.predecessor.CRITICAL}
    source_candidates.update({p: previous.C for p in previous.CRITICAL})
    if current == after:
        require(ancestor(root, C, head), '017 source replay without candidate ancestry')
        phase = 'CANDIDATE_VALIDATION_ONLY'
        protected |= CRITICAL
        source_candidates[SOURCE] = C
    elif ancestor(root, C, head):
        require(False, '017 candidate ancestry with original source')
    processor = None
    # Scan immutable queue history for the first real processor transition.
    # A later DONE row or catalog cannot self-declare an earlier HEP PASS.
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', READY + '..' + head).decode().split():
        row = item(root, revision, 'GP-CONFIG-017')
        if row['hardware_result'] == 'PASS' or row['status'] in {'HARDWARE_VALIDATED', 'DONE'}:
            require(row['hardware_result'] == 'PASS' and
                    row['status'] in {'HARDWARE_VALIDATED', 'DONE'} and
                    row['hardware_evidence_gaps'] == [] and
                    row['hardware_evidence_dependency_satisfied'] is True,
                    '017 PASS in invalid native status')
            if processor is None:
                require(row['status'] == 'HARDWARE_VALIDATED' and
                        critical_tree(root, revision) == before and
                        not ancestor(root, C, revision),
                        '017 first processor PASS must be source-free E')
                processor = _processor(root, revision, row, before, after)
            else:
                require(previous.same_acceptance(row, processor['native']),
                        '017 processor acceptance downgraded/replaced')
        elif processor is not None:
            require(False, '017 processor PASS erased/downgraded')
        if TRANSITIONS in _tree(root, revision):
            introduced = _catalog(raw_bytes(root, revision, TRANSITIONS))
            if introduced:
                require(processor is not None and len(introduced) == 1,
                        '017 catalog precedes processor')
                _accepted(root, revision, introduced[0], processor, after)
    require((state['hardware_result'] == 'PASS' or state['status'] in {'HARDWARE_VALIDATED', 'DONE'})
            == (processor is not None), '017 current processor status/history mismatch')
    if processor:
        current_native = dict(state)
        if (head == processor['evidence_commit'] and
                current_native['hardware_evidence_record'] == 'repo-json:' + EVIDENCE):
            current_native['hardware_evidence_record'] = (
                'git-json:' + processor['evidence_root'] + ':' + EVIDENCE)
        require(previous.same_acceptance(current_native, processor['native']),
                '017 current acceptance tuple differs from first E')
        for path in (PROTOCOL, EVIDENCE, RESULT):
            require(current_bytes(root, path) == raw_bytes(root, head, path)
                    and _git(root, 'show', ':' + path) == current_bytes(root, path),
                    '017 accepted evidence/protocol/result live/index substitution: ' + path)
        if current == before:
            require(not records, 'source-free017 processor has accepted catalog')
            phase = 'SOURCE_FREE_PROCESSOR'
        else:
            require(len(records) == 1, 'integrated017 PASS lacks accepted catalog')
            _accepted(root, head, records[0], processor, after)
            phase = 'ACCEPTED_TRANSITION'
    else:
        require(not records, '017 accepted catalog without HEP PASS')
    metadata = (frozenset((previous.predecessor.PROTOCOL, previous.predecessor.EVIDENCE,
                           previous.predecessor.RESULT, previous.PROTOCOL, previous.EVIDENCE,
                           previous.RESULT)) |
                (frozenset((PROTOCOL, EVIDENCE, RESULT)) if processor else frozenset()))
    roots = set(ROOTS) | set(predecessor['c020_object_roots']) | {old_accepted['integration'],
        predecessor['build'], predecessor['parent'], predecessor['review_commit'],
        predecessor['evidence_commit'], predecessor['evidence_root']}
    if processor:
        roots |= {processor[k] for k in ('build', 'parent', 'review_commit',
                                        'evidence_commit', 'evidence_root')}
    if records:
        roots.add(records[0]['integration'])
    return {'phase': phase, 'contract': 'c017_neopixel', 'candidate': C, 'base': B,
            'predecessor_phase': 'ACCEPTED_TRANSITION',
            'target': head, 'critical_paths': protected,
            'accepted_metadata_paths': metadata, 'changed_paths': frozenset(delta | dirty),
            'object_roots': frozenset(roots), 'source_candidates': source_candidates,
            'host_overlay_paths': overlays, 'kbd_host_paths': kbd,
            'config019_host_paths': config019,
            'evidence_commit': processor['evidence_commit'] if processor else None}


def _processor(root: Path, head: str, state: dict, before: dict, after: dict):
    """Validate actual future E; this path is unreachable from candidate fixtures."""
    F = state['candidate_git_sha']; parent = state['candidate_base_configurator_sha']
    require(all(isinstance(x, str) and re.fullmatch('[0-9a-f]{40}', x) for x in (F, parent))
            and _git(root, 'rev-list', '--parents', '-n', '1', F).decode().split() == [F, parent]
            and ancestor(root, C, F) and critical_tree(root, F) == after,
            '017 build F parent/source mismatch')
    verify_correspondence(root, C, B, target=F, integrated=True, check_worktree=False)
    digest = state['firmware_artifact_sha256']
    require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest)
            and state['preserved_firmware_artifact_locator'] ==
            f'local_backups/hardware-artifacts/{F}/{digest}/firmware.uf2'
            and state['manual_acceptance_protocol_reference'] == PROTOCOL
            and state['manual_acceptance_protocol_version'] == 'GP_CONFIG_017_HW_V1',
            '017 artifact/protocol identity mismatch')
    reference = state['hardware_evidence_record']
    if reference == 'repo-json:' + EVIDENCE:
        evidence_root = head
    else:
        match = re.fullmatch('git-json:([0-9a-f]{40}):' + re.escape(EVIDENCE), str(reference))
        require(match is not None, '017 evidence lacks immutable Git root')
        evidence_root = match.group(1)
    require(ancestor(root, evidence_root, head), '017 evidence root after E')
    payload = raw_bytes(root, evidence_root, EVIDENCE)
    from check_glyph_agent_framework_docs import validate_work_order, validate_evidence_record
    validate_work_order(state, evidence_repo_root=root)
    validate_evidence_record(state, evidence_repo_root=root)
    evidence = json.loads(payload, object_pairs_hook=unique)
    require(evidence['anomalies'] == evidence['evidence_gaps'] == []
            and len({row['id'] for row in evidence['steps']}) == len(evidence['steps']),
            '017 evidence gaps/duplicate rows')
    review = None
    for revision in _git(root, 'rev-list', '--reverse', '--topo-order', READY + '..' + head).decode().split():
        row = item(root, revision, 'GP-CONFIG-017')
        if row['status'] in {'REVIEW', 'HARDWARE_TEST_REQUIRED'} and row['hardware_result'] is None:
            if all(row[k] == state[k] for k in previous.IDENTITIES) and PROTOCOL in _tree(root, revision):
                review = revision; break
    require(review is not None and ancestor(root, review, evidence_root)
            and ancestor(root, review, head) and not ancestor(root, F, review)
            and critical_tree(root, review) == before
            and raw_bytes(root, review, PROTOCOL) == raw_bytes(root, head, PROTOCOL),
            '017 missing reviewed source-free R/protocol')
    return {'build': F, 'parent': parent, 'tree': _git(root, 'rev-parse', F + '^{tree}').decode().strip(),
            'review_commit': review, 'evidence_commit': head, 'evidence_root': evidence_root,
            'payload': payload, 'native': dict(state, hardware_evidence_record=
                'git-json:' + evidence_root + ':' + EVIDENCE)}


def _accepted(root: Path, head: str, record: dict, processor: dict, after: dict):
    require(all(record[k] == processor[k] for k in ('build', 'parent', 'tree',
                                                    'review_commit', 'evidence_commit'))
            and ancestor(root, processor['evidence_commit'], record['integration'])
            and ancestor(root, processor['build'], record['integration'])
            and ancestor(root, record['integration'], head)
            and critical_tree(root, record['integration']) == after,
            '017 accepted catalog chronology/source mismatch')
    verify_correspondence(root, processor['build'], processor['parent'],
                          target=head, integrated=True, check_worktree=False)


def verify_current_source(root: Path, path: str, historical_sha256: str | None = None):
    root = Path(root).resolve()
    old = raw_bytes(root, previous.original.B, path)
    if historical_sha256 is not None:
        require(sha(old) == historical_sha256, 'historical source identity mismatch: ' + path)
    current = current_bytes(root, path)
    if current != old:
        proof = authenticate(root)
        owner = proof['source_candidates'].get(path)
        require(owner is not None and current == raw_bytes(root, owner, path),
                'unadopted017 source overlay: ' + path)
    return old
