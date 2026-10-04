"""Finite adopted GP-VAL-043/044 proofs with separate processor and source phases."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
import glyph_campaign_transition as original
from glyph_hardware_correspondence import CorrespondenceError, classify_path, verify_correspondence

C_R = '3138ade526cabde23a0abedcb94acae8512579d1'
B_R = '0f7fe50b3b5f385397a9737bc4c0a50ddda683c8'
TREE_R = '67a4edd29bcd4c0adfd3ea52790d9a31293f6036'
HANDOFF_R = 'c7bc3364b51959a47d1fa0ba7b11df2db2c46770'
PACKET = '76cb953cd6bfe5398db11669f3d195175361700c'
RECEIPT = '5a82aa06e116cb8c8580cee87a55f1ea98f406cb'
PACKET_BASE = '38017600deb243b5e281edec6d0d378b997d9e40'
FAILED_F = '0a5dd751c391198140ed146853a69fc825d902c7'
RAW_R = 'e3fcf78810c251f1d72f61bcb736075593b489293edd5d42b7c84c4eb1c81864'
MAPPING = 'docs/runtime_config/fixtures/gp_val043_c020_abi_repair.json'
TRANSITIONS = 'docs/runtime_config/fixtures/gp_val043_accepted_transitions.json'
PROOF_PATHS = frozenset(('tools/fixtures/gp_config020_button_validation/abi_probe.cpp',
 'docs/runtime_config/gp_config020_abi_repair.md',
 'docs/runtime_config/fixtures/gp_config020_abi_repair.json'))
NEW_PATHS = frozenset(('tools/glyph_c020_abi_repair_transition.py', MAPPING, TRANSITIONS))
GOVERNANCE_PATHS = original.GOVERNANCE_PATHS | NEW_PATHS | PROOF_PATHS
ROOTS = original.ROOTS | frozenset((C_R, B_R, HANDOFF_R, PACKET, RECEIPT, PACKET_BASE, FAILED_F))
CRITICAL = original.CRITICAL
HOSTS = original.HOSTS
PROTOCOL = original.PROTOCOL
EVIDENCE = original.EVIDENCE
require = original.require
unique = original.unique
ancestor = original.ancestor
critical_tree = original.critical_tree
raw_bytes = original.raw_bytes
current_bytes = original.current_bytes
item = original.item
queue = original.queue
_tree = original._tree
_git = original._git
validate_build_review = original.validate_build_review
accepted_scope_metadata = original.accepted_scope_metadata
MAPPING_SHA256 = '384ee809533060731f57843095b9642c1286a24f1afcce71d54f786b9eda8f8a'
AUTHORITY_BLOBS = {'76cb953cd6bfe5398db11669f3d195175361700c': {'path': 'docs/planning/portfolio_20261003_1256.md', 'sha256': '7f82758bdf36f461e3ed2c43f3a089782f8fac40ef7b80158145b14a3ffadb93'}, '5a82aa06e116cb8c8580cee87a55f1ea98f406cb': {'path': 'docs/project/ACTIVE_AGENT_QUEUE.md', 'sha256': 'e106153598a1357b28204f07068dbdfe94398400c5f488dd6a65417388571a0a'}, '0f7fe50b3b5f385397a9737bc4c0a50ddda683c8': {'path': 'docs/project/ACTIVE_AGENT_QUEUE.md', 'sha256': '5daec97e7ba3abfa35d189ba672d05ff29a2043a0b28c57ba93ff26ea0905ff5'}, 'c7bc3364b51959a47d1fa0ba7b11df2db2c46770': {'path': 'docs/project/ACTIVE_AGENT_QUEUE.md', 'sha256': 'e8e4370cb555c359c5955035eeee220a4f1fb326ab11e4f5ad9248ea36b8c797'}}

PROCESSOR_RECEIPT = 'd9d1e72bb18a5e1dbdf05c829a1d11362893933f'
PROCESSOR_ADOPTION = 'd2f78cd3a3fa38c60d04dab54236ee630ead379e'
PROCESSOR_AUTHORITY = {
    PROCESSOR_RECEIPT: '2660d3c629f16ea77b9872dba67bff40af57deddba49e1a7996fede7ffd0ae20',
    PROCESSOR_ADOPTION: '262f93a44bd48553c002f9542d2bdd2e1476b51adf0da2d27507f6e327e27a97',
}
RESULT = 'docs/calibration/gp_config_020_hardware_result.md'
PROCESSOR_PINS = dict(
    review_commit='040735f6916c7a77924ef53f1b4a873281f2cb7f',
    build='7db4f447d5e796367071b7143fa6c9274c70ae5e',
    parent='de36d24422a67e8be7992217856c76e8420a71f6',
    tree='4b5b63ce56219a508e2b71745438a609dd5661c3',
    artifact_sha256='7743fcbe3d71ec4159e6da5026a1b4560cbbef4d1654cb80b8907fcce344b500',
    artifact_size=796160,
    protocol_sha256='ca6914ea8526e871760c7033a0b3df5aa1e07ba7e4c266cfbaa0aae5193a3421',
    review_queue_sha256='2702f7a177a474fc9501cd930dd1deacfae51e3e9127f6c1a9d29d34ea5abac6',
    evidence_sha256='39a3977fbbc0b4d2db4f1187eba7d233de5056faceae47b734b2068f26051d42',
    result_sha256='9e69b3fc87366b9c61174df4a8c9865603ce95b295cbeaefcc9cbd81bf1f15d5',
    authority_commit=PROCESSOR_RECEIPT, authority_adoption=PROCESSOR_ADOPTION)
# Public roots remain finite literal identities, including off-ancestry build F.
ROOTS |= frozenset((PROCESSOR_RECEIPT, PROCESSOR_ADOPTION,
                   PROCESSOR_PINS['review_commit'], PROCESSOR_PINS['build'],
                   PROCESSOR_PINS['parent']))
PROCESSOR_R = PROCESSOR_PINS['review_commit']
BUILT_F = PROCESSOR_PINS['build']

# Direct owner Revision-3 is a single reviewed committed document, not a
# general documentation/prefix exception or an evidence/catalog exemption.
OWNER_DIRECTION = 'docs/agent_framework/USER_DIRECTION.md'
OWNER_DIRECTION_AUTHORITY = '0efef62a9d4a6254466325eeb0e33184a4848fab'
OWNER_DIRECTION_SHA256 = '4fd9bec943f3c24427e5db5e87c093f8002f5715bdccdc4ef0acd27633fbd8a7'


def _owner_direction_scope(root, head, delta):
    if OWNER_DIRECTION not in delta:
        return frozenset()
    require(ancestor(root, OWNER_DIRECTION_AUTHORITY, head),
            'owner direction lacks exact adopted authority ancestry')
    require(_git(root, 'rev-list', '--parents', '-n', '1', OWNER_DIRECTION_AUTHORITY)
            .decode().split() == [OWNER_DIRECTION_AUTHORITY, PROCESSOR_ADOPTION],
            'owner direction authority parent mismatch')
    require(_git(root, 'diff', '--name-only', PROCESSOR_ADOPTION,
                 OWNER_DIRECTION_AUTHORITY).decode().splitlines() == [OWNER_DIRECTION],
            'owner direction authority changed another path')
    authoritative = raw_bytes(root, OWNER_DIRECTION_AUTHORITY, OWNER_DIRECTION)
    require(_sha(authoritative) == OWNER_DIRECTION_SHA256
            and raw_bytes(root, head, OWNER_DIRECTION) == authoritative
            and current_bytes(root, OWNER_DIRECTION) == authoritative
            and _git(root, 'show', ':' + OWNER_DIRECTION) == authoritative,
            'owner direction immutable committed/live/index substitution')
    return frozenset((OWNER_DIRECTION,))


@dataclass(frozen=True)
class ProcessorRoots:
    repository: str
    pins: tuple
    source_trees: tuple = ()

    def values(self):
        return dict(self.pins)

def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


# These are exactly the existing immutable source/authority consumers. No
# directory-prefix or whole-tree blob prefetch is authorized.
_DECODER_PATHS = tuple('tools/fixtures/gp_config012_button_host/' + path for path in (
    'generated/config.pb.c', 'generated/config.pb.h', 'nanopb/pb.h',
    'nanopb/pb_common.c', 'nanopb/pb_common.h', 'nanopb/pb_decode.c',
    'nanopb/pb_decode.h', 'schema/config.options', 'schema/config.proto'))
_STATUS_PATHS = ('docs/AGENT_CONTEXT.md', 'docs/CURRENT_STATE.md',
                 'docs/ROADMAP.md', original.QUEUE)
_OLD_BASELINE_EVIDENCE = 'docs/calibration/fixtures/gp_config_010_integration_hardware_evidence_2026-09-23.json'
_PREFETCH_PATHS = (CRITICAL | HOSTS | PROOF_PATHS | frozenset(_DECODER_PATHS)
    | frozenset(_STATUS_PATHS) | frozenset(original.FROZEN)
    | frozenset(original.RECEIPTS.values())
    | frozenset(('docs/planning/portfolio_20261003_1256.md',
                 _OLD_BASELINE_EVIDENCE, TRANSITIONS, original.TRANSITIONS)))
_PREFETCH_PATHS |= frozenset((PROTOCOL, EVIDENCE, RESULT))


def _parse_blob_batch(raw, identities):
    """Validate the complete ordered reply before publishing any cached bytes."""
    require(type(raw) is bytes and type(identities) is tuple
            and len(identities) == len(set(identities))
            and all(isinstance(oid, str) and re.fullmatch('[0-9a-f]{40}', oid)
                    for oid in identities), 'invalid immutable blob batch identities')
    result = {}
    offset = 0
    for oid in identities:
        end = raw.find(b'\n', offset)
        require(end >= offset, 'truncated immutable blob batch header')
        header = re.fullmatch(rb'([0-9a-f]{40}) blob (0|[1-9][0-9]*)', raw[offset:end])
        require(header is not None and header.group(1).decode() == oid,
                'immutable blob batch hash/type substitution')
        size = int(header.group(2))
        start = end + 1
        require(size <= len(raw) - start - 1 and raw[start + size:start + size + 1] == b'\n',
                'truncated immutable blob batch payload/trailer')
        data = raw[start:start + size]
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(actual == oid, 'immutable blob batch content/size hash substitution')
        result[oid] = data
        offset = start + size + 1
    require(offset == len(raw), 'extra/duplicate immutable blob batch output')
    return result


def _prefetch_blobs(root, requests):
    """One process, finite literal paths, atomic invocation-only raw blob cache."""
    cache = original._blob_bytes_cache.get()
    require(cache is not None, 'blob prefetch outside proof invocation')
    root = Path(root).resolve()
    root_key = str(root)
    identities = set()
    # Repeated paths/refs and shared blobs deduplicate explicitly. Per-ref modes
    # are checked here and still checked by every later raw_bytes consumer.
    for ref, path in dict.fromkeys(requests):
        require(isinstance(ref, str) and re.fullmatch('[0-9a-f]{40}', ref)
                and path in _PREFETCH_PATHS, 'unadopted immutable blob prefetch input')
        entry = _tree(root, ref).get(path)
        require(entry is not None and entry[:2] == ('100644', 'blob')
                and re.fullmatch('[0-9a-f]{40}', entry[2]),
                'nonregular immutable blob prefetch source: ' + path)
        if (root_key, entry[2]) not in cache:
            identities.add(entry[2])
    if not identities:
        return
    ordered = tuple(sorted(identities))
    execution = subprocess.run(['git', 'cat-file', '--batch'], cwd=root,
        input=('\n'.join(ordered) + '\n').encode(), capture_output=True, check=False)
    require(execution.returncode == 0, 'immutable blob prefetch execution failure')
    # A malformed/missing/substituted reply leaves the existing cache unchanged.
    staged = _parse_blob_batch(execution.stdout, ordered)
    cache.update({(root_key, oid): data for oid, data in staged.items()})


def _source_prefetch_requests():
    requests = [(original.C, path) for path in CRITICAL | HOSTS]
    requests += [(C_R, path) for path in CRITICAL | HOSTS | PROOF_PATHS]
    requests += [(FAILED_F, path) for path in CRITICAL | HOSTS]
    requests += [(original.B, path) for path in (*original.FROZEN, *_DECODER_PATHS,
                  'HAL/pico/src/comms/ConfiguratorBackend.cpp')]
    requests += [(ref, path) for ref, path in original.RECEIPTS.items()]
    requests += [(original.ADOPTION, path) for path in original.RECEIPTS.values()]
    requests += [(ref, path) for ref in (original.ARGUMENT_OPENING, original.ADOPTION)
                 for path in _STATUS_PATHS]
    requests += [(original.HANDOFF, original.QUEUE),
                 ('60614dae8150338160b3440aef6b275bf073fecf', _OLD_BASELINE_EVIDENCE)]
    requests += [(ref, pin['path']) for ref, pin in AUTHORITY_BLOBS.items()]
    return tuple(requests)


def _catalog(raw):
    value = json.loads(raw, object_pairs_hook=unique)
    require(type(value) is dict and set(value) == {'schema_version', 'accepted_transitions'}
            and type(value['schema_version']) is int and value['schema_version'] == 1,
            'transition catalog schema drift')
    records = value['accepted_transitions']
    require(type(records) is list and len(records) <= 1, 'unadopted accepted transition extension')
    return records


@original._proof_invocation
def source_contract(root):
    """Authenticate original C first, then the independent exact repaired roots."""
    root = Path(root).resolve()
    _prefetch_blobs(root, _source_prefetch_requests())
    before, old_after = original.source_contract(root)
    for revision, pin in AUTHORITY_BLOBS.items():
        require(_sha(raw_bytes(root, revision, pin['path'])) == pin['sha256'],
                'immutable repaired authority substitution: ' + revision)
    for revision, parent in ((PACKET, PACKET_BASE), (RECEIPT, PACKET_BASE),
                             (B_R, RECEIPT), (C_R, B_R), (HANDOFF_R, B_R)):
        require(_git(root, 'rev-list', '--parents', '-n', '1', revision).decode().split()
                == [revision, parent], 'repaired authority/candidate direct parent mismatch')
    require(_git(root, 'rev-parse', C_R + '^{tree}').decode().strip() == TREE_R,
            'repaired C020 tree mismatch')
    require(_sha(_git(root, 'diff-tree', '-r', '--no-renames', '--raw', '-z', B_R, C_R))
            == RAW_R, 'repaired C020 raw11 inventory mismatch')
    mapping_raw = current_bytes(root, MAPPING)
    require(_sha(mapping_raw) == MAPPING_SHA256, 'literal repaired mapping substitution')
    mapping = json.loads(mapping_raw, object_pairs_hook=unique)
    head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    if MAPPING in _tree(root, head):
        require(raw_bytes(root, head, MAPPING) == mapping_raw, 'uncommitted repaired mapping')
    for field, identity in (('candidate', C_R), ('parent', B_R), ('tree', TREE_R),
                            ('raw_inventory_sha256', RAW_R)):
        require(mapping['candidate'][field] == identity, 'repaired mapping identity mismatch')
    paths = set(filter(None, _git(root, 'diff', '--no-renames', '--name-only', '-z', B_R, C_R).decode().split('\0')))
    require(paths == CRITICAL | HOSTS | PROOF_PATHS, 'repaired exact eleven-path membership mismatch')
    candidate_tree, base_tree = _tree(root, C_R), _tree(root, B_R)
    entries = mapping['candidate']['entries']
    require(len(entries) == 11 and {x['path'] for x in entries} == paths,
            'repaired inventory duplicates/omissions')
    for entry in entries:
        path = entry['path']
        raw = raw_bytes(root, C_R, path)
        new_entry = ' '.join(candidate_tree[path]) + '\t' + path
        old_entry = (' '.join(base_tree[path]) + '\t' + path) if path in base_tree else None
        require(entry['new_tree_entry'] == new_entry and entry['old_tree_entry'] == old_entry
                and entry['sha256'] == _sha(raw), 'repaired candidate blob/mode substitution: ' + path)
    require(critical_tree(root, B_R) == before == critical_tree(root, PACKET_BASE)
            == critical_tree(root, HANDOFF_R), 'repaired source-free baseline critical union mismatch')
    after = critical_tree(root, C_R)
    require({p for p in before.keys() | after.keys() if before.get(p) != after.get(p)} == CRITICAL,
            'repaired critical union outside three authorized paths')
    for path in ('HAL/pico/src/comms/ConfiguratorBackend.cpp',
                 'include/core/config_button_validation.hpp',
                 'tools/fixtures/gp_config020_button_validation/include/Adafruit_TinyUSB.h'):
        require(raw_bytes(root, C_R, path) == raw_bytes(root, original.C, path),
                'repaired original handler/header/stub substitution: ' + path)
    for path in CRITICAL | HOSTS:
        require(raw_bytes(root, FAILED_F, path) == raw_bytes(root, original.C, path),
                'failed original F preservation mismatch')
    authority = item(root, B_R, 'GP-VAL-043')
    require(authority['status'] == 'PREAUTHORIZED' and authority['activation_state'] == 'WAITING'
            and all(str(n) + '. ' in authority['scope'] for n in range(1, 9)),
            'missing adopted eight-step repair authority')
    handoff_item = item(root, HANDOFF_R, 'GP-CONFIG-020')
    require(handoff_item['candidate_git_sha'] == C_R
            and handoff_item['candidate_base_configurator_sha'] == B_R
            and handoff_item['hardware_result'] is None, 'repaired source-free handoff mismatch')
    text = raw_bytes(root, HANDOFF_R, original.QUEUE).decode()
    records = [json.loads(match, object_pairs_hook=unique)
               for match in re.findall(r'```json\n(.*?)\n```', text, re.S)
               if '"schema_name": "glyph_c020_abi_repair_candidate_handoff"' in match]
    require(len(records) == 1, 'missing/duplicate immutable ABI execution handoff')
    handoff = records[0]
    require(handoff['candidate'] == mapping['candidate'], 'source-free candidate inventory mismatch')
    for key in ('target_object_execution_sha256', 'target_proof_script_sha256',
                'host_execution_sha256', 'independent_review_sha256'):
        require(handoff[key] == mapping[key], 'immutable ABI execution digest mismatch')
    target = handoff['target_object_execution']
    require(target['status'] == 'PASS_OBJECT_ONLY' and target['candidate_sha'] == C_R
            and target['candidate_tree'] == TREE_R and target['layout_tuple_count'] == 82
            and len(target['c_cpp_layout_tuple']) == 82
            and target['c_cpp_layout_tuple'][:4] == [1, 1, 26792, 4]
            and target['compiler_version'] == 'arm-none-eabi-g++ (GCC) 12.3.0',
            'forged target compiler/ABI/layout proof')
    require(_sha(handoff['independent_review'].encode()) == mapping['independent_review_sha256']
            and 'Status: PASS' in handoff['independent_review'], 'independent repair review substitution')
    require(item(root, B_R, 'GP-VAL-037') == item(root, HANDOFF_R, 'GP-VAL-037')
            and item(root, HANDOFF_R, 'GP-VAL-037')['status'] == 'DONE', 'strict037 DONE changed')
    return before, old_after, after


F010 = original.F010
B010 = original.B010


@original._proof_invocation
def processor_authority(root):
    """Authenticate the immutable review and complete descendant READY order."""
    _prefetch_blobs(root, [(ref, original.QUEUE) for ref in PROCESSOR_AUTHORITY])
    for ref, digest in PROCESSOR_AUTHORITY.items():
        require(_sha(raw_bytes(root, ref, original.QUEUE)) == digest,
                'processor authority substitution: ' + ref)
    require(_git(root, 'rev-list', '--parents', '-n', '1', PROCESSOR_RECEIPT).decode().split()
            == [PROCESSOR_RECEIPT, PROCESSOR_PINS['review_commit']],
            'processor receipt direct review parent mismatch')
    require(ancestor(root, PROCESSOR_RECEIPT, PROCESSOR_ADOPTION),
            'processor adoption lacks independent receipt')
    text = raw_bytes(root, PROCESSOR_RECEIPT, original.QUEUE).decode()
    start, end = '<!-- c020-processor-curation:start -->', '<!-- c020-processor-curation:end -->'
    require(text.count(start) == text.count(end) == 1, 'processor authority marker drift')
    block = text.split(start)[1].split(end)[0].strip()
    require(block.startswith('```json\n') and block.endswith('\n```'), 'processor receipt fence drift')
    receipt = json.loads(block[8:-4], object_pairs_hook=unique)
    order = item(root, PROCESSOR_ADOPTION, 'GP-VAL-044')
    require(receipt['schema_name'] == 'glyph_c020_processor_phase_authorization_review'
            and type(receipt['schema_version']) is int and receipt['schema_version'] == 1
            and receipt['subject_id'] == order['id'] == 'GP-VAL-044'
            and receipt['disposition'] == order['status'] == 'READY'
            and receipt['canonical_base'] == PROCESSOR_PINS['review_commit']
            and receipt['tested_F'] == PROCESSOR_PINS['build']
            and receipt['artifact_sha256'] == PROCESSOR_PINS['artifact_sha256']
            and receipt['scope_sha256'] == _sha(order['scope'].encode()),
            'processor authority/work-order coupling mismatch')
    from check_glyph_agent_framework_docs import validate_work_order
    validate_work_order(order, evidence_repo_root=Path(root))
    prior = {x['id']: x for x in queue(root, PROCESSOR_RECEIPT)['items']}
    adopted = {x['id']: x for x in queue(root, PROCESSOR_ADOPTION)['items']}
    require(len(prior) == 96 and set(adopted) == set(prior) | {'GP-VAL-044'}
            and all(adopted[key] == value for key, value in prior.items()),
            'processor adoption changed prior work orders')
    return frozenset(PROCESSOR_AUTHORITY)


@original._proof_invocation
def authenticate_processor_roots(root, pins=None):
    """Structural proof accepts explicit immutable pins; production uses literals.

    Explicit pins are a bounded test API. They do not enter authenticate(), the
    campaign dispatcher, real catalogs, or the production object-root export.
    """
    root = Path(root).resolve()
    return _authenticate_processor_roots(root, pins, source_contract(root))


def _authenticate_processor_roots(root, pins, source_trees):
    """Private continuation after the caller's complete source proof."""
    pins = dict(PROCESSOR_PINS if pins is None else pins)
    require(set(pins) == set(PROCESSOR_PINS), 'processor pin fields mismatch')
    for key in ('review_commit', 'build', 'parent', 'tree', 'authority_commit', 'authority_adoption'):
        require(isinstance(pins[key], str) and re.fullmatch('[0-9a-f]{40}', pins[key]),
                'nonimmutable processor root: ' + key)
    for key in ('artifact_sha256', 'protocol_sha256', 'review_queue_sha256',
                'evidence_sha256', 'result_sha256'):
        require(isinstance(pins[key], str) and re.fullmatch('[0-9a-f]{64}', pins[key]),
                'malformed processor digest: ' + key)
    require(type(pins['artifact_size']) is int and pins['artifact_size'] > 0,
            'invalid processor artifact size')
    require(pins['authority_commit'] == PROCESSOR_RECEIPT
            and pins['authority_adoption'] == PROCESSOR_ADOPTION,
            'unadopted processor authority roots')
    processor_authority(root)
    R, F, parent = (pins[key] for key in ('review_commit', 'build', 'parent'))
    # The actual review predates044; explicit structural review fixtures must
    # retain the actual adopted authority in their disposable history.
    require(R == PROCESSOR_PINS['review_commit'] or ancestor(root, PROCESSOR_ADOPTION, R),
            'structural review lacks separately adopted authority')
    require(_sha(raw_bytes(root, R, original.QUEUE)) == pins['review_queue_sha256'],
            'processor reviewed queue substitution')
    require(_git(root, 'rev-list', '--parents', '-n', '1', F).decode().split() == [F, parent],
            'processor F direct parent mismatch')
    require(_git(root, 'rev-parse', F + '^{tree}').decode().strip() == pins['tree'],
            'processor F tree mismatch')
    require(ancestor(root, C_R, F) and ancestor(root, B_R, F),
            'processor F lacks repaired candidate/governance ancestry')
    verify_correspondence(root, C_R, B_R, target=F, integrated=True, check_worktree=False)
    for path in HOSTS | PROOF_PATHS:
        require(raw_bytes(root, F, path) == raw_bytes(root, C_R, path),
                'processor F candidate host/proof substitution: ' + path)
    require(not ancestor(root, F, R)
            and critical_tree(root, R) == source_trees[0],
            'processor review contains candidate source')
    verify_correspondence(root, F010, B010, target=R, integrated=True, check_worktree=False)
    require(_sha(raw_bytes(root, R, PROTOCOL)) == pins['protocol_sha256'],
            'processor protocol substitution')
    review = item(root, R, 'GP-CONFIG-020')
    require(review['status'] in {'REVIEW', 'HARDWARE_TEST_REQUIRED'}
            and review['hardware_result'] is None
            and review['candidate_git_sha'] == F
            and review['candidate_base_configurator_sha'] == parent
            and review['firmware_artifact_sha256'] == pins['artifact_sha256']
            and review['manual_acceptance_protocol_reference'] == PROTOCOL,
            'processor review identity/phase mismatch')
    locator = f"local_backups/hardware-artifacts/{F}/{pins['artifact_sha256']}/firmware.uf2"
    require(review['preserved_firmware_artifact_locator'] == locator,
            'processor reviewed locator mismatch')
    validate_build_review(raw_bytes(root, R, PROTOCOL).decode(), pins,
                          pins['artifact_sha256'], locator)
    size = re.findall(r'^- UF2 size: `([0-9]+)` bytes\s*$',
                      raw_bytes(root, R, PROTOCOL).decode(), re.MULTILINE)
    require(size == [str(pins['artifact_size'])], 'processor reviewed artifact size mismatch')
    return ProcessorRoots(str(root), tuple(sorted(pins.items())),
                          tuple(tuple(sorted(tree.items())) for tree in source_trees))


_PROCESSOR_IDENTITIES = (
    'branch', 'candidate_git_sha', 'candidate_base_configurator_sha', 'firmware_artifact_sha256',
    'preserved_firmware_artifact_locator', 'firmware_artifact_build_path',
    'manual_acceptance_protocol_reference', 'manual_acceptance_protocol_version',
    'hardware_evidence_contract_reference', 'hardware_evidence_contract_version')


def _live_processor_item(raw):
    text = raw.decode()
    start, end = '<!-- queue-state:start -->', '<!-- queue-state:end -->'
    require(text.count(start) == text.count(end) == 1, 'live processor queue marker drift')
    block = text.split(start)[1].split(end)[0].strip()
    require(block.startswith('```json') and block.endswith('```'), 'live processor queue fence drift')
    states = json.loads(block[7:-3], object_pairs_hook=unique)['items']
    states = [state for state in states if state['id'] == 'GP-CONFIG-020']
    require(len(states) == 1, 'live processor queue order missing/duplicate')
    return states[0]


@original._proof_invocation
def validate_processor_transition(root, record, target, *, structural_roots=None):
    """Prove E using immutable native payloads before any source integration."""
    root = Path(root).resolve()
    proof = authenticate_processor_roots(root) if structural_roots is None else structural_roots
    require(type(proof) is ProcessorRoots and proof.repository == str(root),
            'processor roots belong to another repository')
    pins = proof.values()
    if structural_roots is not None:
        # Public callers cannot reuse a certificate from a previous invocation.
        require(authenticate_processor_roots(root, pins) == proof, 'processor roots substitution')
    evidence = _validate_processor_evidence(root, record, proof)
    return _validate_processor_target(root, evidence, target)


def _validate_processor_evidence(root, record, proof):
    """Certify immutable E once in the current private call graph."""
    pins = proof.values()
    fields = {'work_order', 'candidate', 'build', 'parent', 'tree', 'review_commit', 'evidence_commit'}
    require(type(record) is dict and set(record) == fields
            and record['work_order'] == 'GP-CONFIG-020' and record['candidate'] == C_R,
            'processor transition fields/candidate mismatch')
    for key in fields - {'work_order', 'candidate'}:
        require(isinstance(record[key], str) and re.fullmatch('[0-9a-f]{40}', record[key]),
                'nonimmutable processor transition: ' + key)
    require(all(record[key] == pins[key] for key in ('build', 'parent', 'tree', 'review_commit')),
            'processor transition differs from authenticated roots')
    R, E, F = record['review_commit'], record['evidence_commit'], record['build']
    require(R != E and ancestor(root, R, E), 'processor review/E chronology mismatch')
    require(ancestor(root, PROCESSOR_ADOPTION, E), 'processor E lacks adopted044 repair authority')
    require(not ancestor(root, F, E) and critical_tree(root, E) == dict(proof.source_trees[0]),
            'processor E integrated candidate source')
    verify_correspondence(root, F010, B010, target=E, integrated=True, check_worktree=False)
    for catalog in (original.TRANSITIONS, TRANSITIONS):
        for snapshot in (R, E):
            if catalog in _tree(root, snapshot):
                require(_catalog(raw_bytes(root, snapshot, catalog)) == [],
                        'processor review/E contains accepted integration catalog')
    review, accepted = item(root, R, 'GP-CONFIG-020'), item(root, E, 'GP-CONFIG-020')
    require(accepted['status'] == 'HARDWARE_VALIDATED' and accepted['hardware_result'] == 'PASS'
            and accepted['hardware_evidence_gaps'] == []
            and accepted['hardware_evidence_dependency_satisfied'] is True,
            'processor E lacks complete native PASS')
    for key in _PROCESSOR_IDENTITIES:
        require(review[key] == accepted[key], 'processor review/E identity drift: ' + key)
    reference = accepted['hardware_evidence_record']
    if reference == 'repo-json:' + EVIDENCE:
        evidence_root = E
    else:
        match = re.fullmatch(r'git-json:([0-9a-f]{40}):' + re.escape(EVIDENCE), str(reference))
        require(match is not None, 'unsupported processor evidence reference')
        evidence_root = match.group(1)
        require(ancestor(root, R, evidence_root) and ancestor(root, evidence_root, E),
                'processor payload outside review/E ancestry')
    payload = raw_bytes(root, evidence_root, EVIDENCE)
    require(_sha(payload) == pins['evidence_sha256']
            and raw_bytes(root, E, EVIDENCE) == payload,
            'processor immutable evidence substitution')
    from check_glyph_agent_framework_docs import validate_work_order
    immutable = dict(accepted, hardware_evidence_record='git-json:' + evidence_root + ':' + EVIDENCE)
    # HARDWARE_VALIDATED work-order validation invokes native evidence validation.
    validate_work_order(immutable, evidence_repo_root=root)
    evidence = json.loads(payload, object_pairs_hook=unique)
    rows = [row['id'] for row in evidence['steps']]
    require(len(rows) == 11 and set(rows) == {'Baseline', *(f'H{x}' for x in range(1, 11))},
            'processor evidence required rows missing/duplicate')
    require(raw_bytes(root, R, PROTOCOL) == raw_bytes(root, E, PROTOCOL),
            'processor protocol changed after review')
    result = raw_bytes(root, E, RESULT)
    require(_sha(result) == pins['result_sha256'], 'processor immutable result substitution')
    text = result.decode()
    require(all(value in text for value in (
        F, pins['tree'], pins['parent'], R, pins['artifact_sha256'], pins['protocol_sha256'],
        review['preserved_firmware_artifact_locator'], 'HARDWARE_VALIDATED', 'PASS')),
        'processor native result/tuple coupling mismatch')
    return dict(record=dict(record), accepted=accepted, evidence_root=evidence_root,
                payload=payload, result=result, protocol=raw_bytes(root, R, PROTOCOL),
                roots=proof, native_item_bytes=json.dumps(immutable, sort_keys=True,
                    separators=(',', ':'), allow_nan=False).encode())


def _validate_processor_target(root, evidence, target):
    """Every immutable historical target and every live input is checked anew."""
    record, accepted = evidence['record'], evidence['accepted']
    R, E, F = record['review_commit'], record['evidence_commit'], record['build']
    pins = evidence['roots'].values()
    evidence_root, payload, result = (evidence[key] for key in ('evidence_root', 'payload', 'result'))
    require(ancestor(root, E, target), 'processor E/target chronology mismatch')
    current = item(root, target, 'GP-CONFIG-020')
    require(current['status'] in {'HARDWARE_VALIDATED', 'DONE'} and current['hardware_result'] == 'PASS'
            and current['hardware_evidence_gaps'] == []
            and current['hardware_evidence_dependency_satisfied'] is True,
            'processor PASS downgraded at target')
    for key in (*_PROCESSOR_IDENTITIES, 'hardware_evidence_record'):
        require(current[key] == accepted[key], 'processor accepted tuple drift: ' + key)
    from check_glyph_agent_framework_docs import validate_work_order, validate_evidence_record
    native = dict(current, hardware_evidence_record='git-json:' + evidence_root + ':' + EVIDENCE)
    # Reuse only the local immutable native-schema certificate. Complete JSON
    # equality preserves types (False differs from 0); every changed item and
    # every DONE publication still receives its own full native validation.
    require(evidence['roots'].repository == str(root), 'native schema certificate repository mismatch')
    native_bytes = json.dumps(native, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    if native['status'] != 'HARDWARE_VALIDATED' or native_bytes != evidence['native_item_bytes']:
        validate_work_order(native, evidence_repo_root=root)
    if native['status'] == 'DONE':
        validate_evidence_record(native, evidence_repo_root=root)
        from check_glyph_agent_framework_docs import validate_completion_evidence
        validate_completion_evidence(native, native['done_evidence'],
            policy=queue(root, target)['completion_correspondence'],
            publication_sha=target, repo_root=root)
    live_keys = (*_PROCESSOR_IDENTITIES, 'hardware_evidence_record', 'status', 'hardware_result',
                 'hardware_evidence_gaps', 'hardware_evidence_dependency_satisfied')
    # Queue docs may be edited, but live/index physical identity and acceptance
    # never inherit authority from a different committed item.
    head_state = item(root, _git(root, 'rev-parse', 'HEAD').decode().strip(), 'GP-CONFIG-020')
    for raw in (current_bytes(root, original.QUEUE), _git(root, 'show', ':' + original.QUEUE)):
        live = _live_processor_item(raw)
        require(all(live[key] == head_state[key] for key in live_keys),
                'live/index processor tuple or acceptance substitution')
    for path, data in ((EVIDENCE, payload), (RESULT, result),
                       (PROTOCOL, evidence['protocol'])):
        require(raw_bytes(root, target, path) == data and current_bytes(root, path) == data,
                'processor current metadata substitution: ' + path)
    return dict(evidence_commit=E, evidence_root=evidence_root,
                accepted_metadata_paths=frozenset((EVIDENCE, RESULT)),
                object_roots=frozenset((R, F, pins['parent'], E, evidence_root,
                                       PROCESSOR_RECEIPT, PROCESSOR_ADOPTION)))

@original._proof_invocation
def validate_accepted_transition(root, record, target):
    """Closed consumer: later014/017 need separately adopted literal contracts."""
    return _validate_accepted_transition(Path(root).resolve(), record, target)


def _validate_accepted_transition(root, record, target, observations=None):
    root=Path(root).resolve()
    fields={'work_order','candidate','build','parent','tree','review_commit','evidence_commit','integration'}
    require(type(record) is dict and set(record)==fields,'accepted transition fields mismatch')
    require(record['work_order'] in {'GP-CONFIG-020','GP-CONFIG-014','GP-CONFIG-017'},'unknown campaign order')
    require(record['work_order']=='GP-CONFIG-020' and record['candidate']==C_R,'campaign order has no adopted literal candidate contract')
    F=record['build']; parent=record['parent']
    for key in fields-{'work_order'}:
        value=record[key]; require(isinstance(value,str) and len(value)==40 and all(c in '0123456789abcdef' for c in value),'nonimmutable transition identity: '+key)
    if ancestor(root, PROCESSOR_ADOPTION, target):
        require(all(record[key] == PROCESSOR_PINS[key]
                    for key in ('build', 'parent', 'tree', 'review_commit')),
                'accepted transition differs from actual processor pins')
        require(_catalog(raw_bytes(root, target, TRANSITIONS)) == [record]
                and current_bytes(root, TRANSITIONS) == raw_bytes(root, target, TRANSITIONS),
                'accepted transition lacks genuine committed catalog')
        if observations is None:
            observations = processor_history(root, target, [], [record])
        require(observations['processor'] is not None
                and record['evidence_commit'] == observations['processor']['evidence_commit'],
                'accepted transition replaced earliest processor E')
        # The full root/E/history proof above includes the native reviewed
        # build, source-free R/E, schema and payload checks. Prove the remaining
        # integration and live-source correspondence here without repeating it.
        R, E, I = record['review_commit'], record['evidence_commit'], record['integration']
        require(R != E and E != I and ancestor(root, R, E) and ancestor(root, E, I)
                and ancestor(root, F, I) and ancestor(root, I, target),
                'review/PASS/integration chronology mismatch')
        verify_correspondence(root, F, parent, target=target, integrated=True, check_worktree=True)
        return F
    require(_git(root,'rev-list','--parents','-n','1',F).decode().split()==[F,parent],'built F direct parent mismatch')
    require(_git(root,'rev-parse',F+'^{tree}').decode().strip()==record['tree'],'built F tree mismatch')
    require(ancestor(root,C_R,F) and ancestor(root,B_R,F),'built F omitted candidate/governance authority')
    verify_correspondence(root,C_R,B_R,target=F,integrated=True,check_worktree=False)
    require(ancestor(root,F,record['integration']) and ancestor(root,record['integration'],target),'reviewed integration ancestry mismatch')
    R,E,I=record['review_commit'],record['evidence_commit'],record['integration']
    require(R!=E and E!=I and ancestor(root,B_R,R) and ancestor(root,R,E)
            and ancestor(root,E,I), 'review/PASS/integration chronology mismatch')
    # Review and evidence are source-free canonical snapshots referencing unmerged F.
    require(not ancestor(root,F,R) and not ancestor(root,F,E), 'firmware integrated before review/PASS')
    require(critical_tree(root,R)==critical_tree(root,B_R)==critical_tree(root,E),
            'review/PASS snapshots must precede firmware integration')
    for snapshot in (R,E):
        verify_correspondence(root,F010,B010,target=snapshot,integrated=True,check_worktree=False)
    review=item(root,R,'GP-CONFIG-020')
    accepted=item(root,E,'GP-CONFIG-020')
    require(review['status'] in {'REVIEW','HARDWARE_TEST_REQUIRED'} and review['hardware_result'] is None,
            'review is not a pre-hardware handoff')
    require(accepted['status'] in {'HARDWARE_VALIDATED','DONE'} and accepted['hardware_result']=='PASS'
            and accepted['hardware_evidence_gaps']==[], 'missing exact processor PASS')
    for state in (review,accepted):
        require(state['candidate_git_sha']==F and state['candidate_base_configurator_sha']==parent,
                'review/processor built snapshot mismatch')
        require(state['manual_acceptance_protocol_reference']==PROTOCOL, 'unexpected campaign protocol')
    for key in ('firmware_artifact_sha256','preserved_firmware_artifact_locator','firmware_artifact_build_path',
                'manual_acceptance_protocol_version','hardware_evidence_contract_reference','hardware_evidence_contract_version'):
        require(review[key]==accepted[key], 'review/processor identity mismatch: '+key)
    digest=review['firmware_artifact_sha256']
    require(isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest) is not None,'invalid reviewed artifact SHA')
    locator=f'local_backups/hardware-artifacts/{F}/{digest}/firmware.uf2'
    require(review['preserved_firmware_artifact_locator']==locator,'reviewed artifact locator mismatch')
    validate_build_review(raw_bytes(root,R,PROTOCOL).decode(),record,digest,locator)
    # Both native reference forms are immutable at the processor snapshot. A
    # git-json object must itself follow review and be present before processing.
    reference=accepted['hardware_evidence_record']
    if reference=='repo-json:'+EVIDENCE:
        evidence_root=E
    else:
        match=re.fullmatch(r'git-json:([0-9a-f]{40}):'+re.escape(EVIDENCE),str(reference))
        require(match is not None,'unsupported accepted evidence reference')
        evidence_root=match.group(1)
        require(ancestor(root,R,evidence_root) and ancestor(root,evidence_root,E),
                'hardware evidence object outside review/processor ancestry')
    require(current_bytes(root,EVIDENCE)==raw_bytes(root,evidence_root,EVIDENCE), 'current accepted evidence substitution')
    from check_glyph_agent_framework_docs import validate_work_order, validate_evidence_record
    immutable_accepted=dict(accepted,hardware_evidence_record='git-json:'+evidence_root+':'+EVIDENCE)
    validate_work_order(immutable_accepted,evidence_repo_root=root)
    validate_evidence_record(immutable_accepted,evidence_repo_root=root)
    current=item(root,target,'GP-CONFIG-020')
    require(current['status'] in {'HARDWARE_VALIDATED','DONE'} and current['hardware_result']=='PASS'
            and current['hardware_evidence_gaps']==[], 'accepted catalog/current phase mismatch')
    for key in ('candidate_git_sha','candidate_base_configurator_sha','firmware_artifact_sha256',
                'preserved_firmware_artifact_locator','firmware_artifact_build_path','hardware_evidence_record'):
        require(current[key]==accepted[key], 'current accepted identity drift: '+key)
    verify_correspondence(root,F,parent,target=target,integrated=True,check_worktree=True)
    return F

def _history(root, head, old_records, repaired_records):
    """Check both catalogs over full original topology; no second parent is hidden."""
    accepted = False
    introductions = {}
    revisions = _git(root, 'rev-list', '--reverse', '--topo-order',
                     original.ADOPTION + '..' + head).decode().split()
    requests = []
    for revision in revisions:
        inventory = _tree(root, revision)
        requests.append((revision, original.QUEUE))
        for path in (original.TRANSITIONS, TRANSITIONS):
            if path in inventory:
                requests.append((revision, path))
    _prefetch_blobs(root, requests)
    for revision in revisions:
        state = item(root, revision, 'GP-CONFIG-020')
        accepted |= state['status'] in {'HARDWARE_VALIDATED', 'DONE'} or state['hardware_result'] == 'PASS'
        inventory = _tree(root, revision)
        for catalog_path, records, candidate in (
                (original.TRANSITIONS, old_records, original.C),
                (TRANSITIONS, repaired_records, C_R)):
            if catalog_path in inventory:
                previous = _catalog(raw_bytes(root, revision, catalog_path))
                if previous:
                    require(previous == records and previous[0].get('candidate') == candidate,
                            'accepted transition history erased or substituted')
                    accepted = True
                    if not any(ancestor(root, prior, revision)
                               for prior in introductions.get(catalog_path, ())):
                        introductions.setdefault(catalog_path, []).append(revision)
            else:
                previous = []
            if any(ancestor(root, prior, revision) for prior in introductions.get(catalog_path, ())):
                require(previous == records, 'accepted transition catalog deleted in history')
    return accepted


@original._proof_invocation
def processor_history(root, head, old_records, repaired_records, *, structural_roots=None):
    """Authenticate every claim over full topology and retain the earliest E."""
    root = Path(root).resolve()
    roots = authenticate_processor_roots(root) if structural_roots is None else structural_roots
    require(type(roots) is ProcessorRoots and roots.repository == str(root),
            'history roots belong to another repository')
    if structural_roots is not None:
        require(authenticate_processor_roots(root, roots.values()) == roots,
                'history roots substitution')
    return _processor_history(root, head, old_records, repaired_records, roots)


def _processor_history(root, head, old_records, repaired_records, roots):
    """One immutable certificate chain; each historical SHA is still checked."""
    pins = roots.values()
    baseline, candidate_tree = dict(roots.source_trees[0]), dict(roots.source_trees[2])
    revisions = _git(root, 'rev-list', '--reverse', '--topo-order',
                     original.ADOPTION + '..' + head).decode().split()
    requests = []
    for revision in revisions:
        inventory = _tree(root, revision)
        requests.append((revision, original.QUEUE))
        requests.extend((revision, path) for path in (original.TRANSITIONS, TRANSITIONS)
                        if path in inventory)
    _prefetch_blobs(root, requests)
    earliest, evidence, integrated = None, None, False
    introductions = {}
    for revision in revisions:
        state = item(root, revision, 'GP-CONFIG-020')
        catalogs = {}
        for path, expected, candidate in ((original.TRANSITIONS, old_records, original.C),
                                         (TRANSITIONS, repaired_records, C_R)):
            previous = _catalog(raw_bytes(root, revision, path)) if path in _tree(root, revision) else []
            catalogs[path] = previous
            if previous:
                require(previous == expected and previous[0].get('candidate') == candidate,
                        'accepted transition history erased or substituted')
                integrated = True
                if not any(ancestor(root, prior, revision) for prior in introductions.get(path, ())):
                    introductions.setdefault(path, []).append(revision)
            if any(ancestor(root, prior, revision) for prior in introductions.get(path, ())):
                require(previous == expected, 'accepted transition catalog deleted in history')
        claims = state['status'] in {'HARDWARE_VALIDATED', 'DONE'} or state['hardware_result'] == 'PASS'
        if claims:
            if earliest is None:
                require(not any(catalogs.values()), 'integrated acceptance lacks earlier processor E')
                record = dict(work_order='GP-CONFIG-020', candidate=C_R,
                              **{key: pins[key] for key in ('build', 'parent', 'tree', 'review_commit')},
                              evidence_commit=revision)
                evidence = _validate_processor_evidence(root, record, roots)
            observed = _validate_processor_target(root, evidence, revision)
            if earliest is None:
                earliest = observed
            actual = critical_tree(root, revision)
            if actual == baseline:
                require(state['status'] == 'HARDWARE_VALIDATED' and not any(catalogs.values())
                        and not ancestor(root, pins['build'], revision),
                        'source-free processor claims integrated acceptance')
            else:
                require(actual == candidate_tree and ancestor(root, pins['build'], revision),
                        'processor history source/ancestry mismatch')
        elif earliest is not None and ancestor(root, earliest['evidence_commit'], revision):
            require(False, 'processor history downgraded or erased PASS')
    if earliest is not None:
        _validate_processor_target(root, evidence, head)
    return dict(processor=earliest, integrated=integrated)


@original._proof_invocation
def authenticate(root):
    root = Path(root).resolve()
    head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    dirty = set()
    for args in [('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z'),
                 ('ls-files', '--others', '--exclude-standard', '-z')]:
        dirty.update(filter(None, _git(root, *args).decode().split('\0')))
    # Ignores are not evidence authority. Reject ignored documentation inputs
    # too; local artifact custody/build/cache roots retain their existing seam.
    ignored = set(filter(None, _git(root, 'ls-files', '--others', '--ignored',
                                   '--exclude-standard', '-z').decode().split('\0')))
    dirty.update(path for path in ignored if path.split('/', 1)[0].casefold() == 'docs')
    require(dirty <= GOVERNANCE_PATHS, 'dirty path outside reviewed governance inventory')
    # Accepted metadata is immutable under the existing final correspondence proof.
    # Reject its live substitutions before expensive source validation. A catalog
    # here can only cause rejection; every successful call still authenticates it.
    accepted_literals = frozenset((PROTOCOL, EVIDENCE,
        'docs/calibration/gp_config_020_hardware_result.md', MAPPING))
    committed_state = item(root, head, 'GP-CONFIG-020')
    if (committed_state['status'] in {'HARDWARE_VALIDATED', 'DONE'}
            or committed_state['hardware_result'] == 'PASS'):
        require(not dirty & (accepted_literals | {TRANSITIONS, original.TRANSITIONS}),
                'accepted metadata substitution or nonregular file mode: '
                + repr(sorted(dirty & (accepted_literals | {TRANSITIONS, original.TRANSITIONS}))))
    if dirty & (accepted_literals | {TRANSITIONS, original.TRANSITIONS}):
        inventory = _tree(root, head)
        for catalog in (TRANSITIONS, original.TRANSITIONS):
            protected = accepted_literals | {catalog}
            if dirty & protected and catalog in inventory and _catalog(raw_bytes(root, head, catalog)):
                require(False, 'accepted metadata substitution or nonregular file mode: '
                        + repr(sorted(dirty & protected)))
    if (ancestor(root, PROCESSOR_ADOPTION, head)
            and (committed_state['status'] in {'HARDWARE_VALIDATED', 'DONE'}
                 or committed_state['hardware_result'] == 'PASS')):
        # Cheap rejection checks precede the full authority/source/history
        # proof. These checks cannot return a successful phase on their own.
        require(committed_state['hardware_result'] == 'PASS'
                and committed_state['hardware_evidence_dependency_satisfied'] is True
                and committed_state['hardware_evidence_gaps'] == [],
                'processor current PASS dependency/gaps mismatch')
        reviewed = item(root, PROCESSOR_R, 'GP-CONFIG-020')
        require(all(committed_state[key] == reviewed[key] for key in _PROCESSOR_IDENTITIES),
                'processor current reviewed tuple mismatch')
        live_keys = (*_PROCESSOR_IDENTITIES, 'hardware_evidence_record', 'status', 'hardware_result',
                     'hardware_evidence_gaps', 'hardware_evidence_dependency_satisfied')
        for raw in (current_bytes(root, original.QUEUE), _git(root, 'show', ':' + original.QUEUE)):
            live = _live_processor_item(raw)
            require(all(live[key] == committed_state[key] for key in live_keys),
                    'live/index processor tuple or acceptance substitution')
        for path, digest in ((EVIDENCE, PROCESSOR_PINS['evidence_sha256']),
                             (RESULT, PROCESSOR_PINS['result_sha256']),
                             (PROTOCOL, PROCESSOR_PINS['protocol_sha256'])):
            immutable = raw_bytes(root, head, path)
            require(_sha(immutable) == digest and current_bytes(root, path) == immutable,
                    'processor current immutable metadata substitution: ' + path)
    require(ancestor(root, B_R, head), 'repaired campaign snapshot lacks adopted authority')
    before, old_after, after = source_contract(root)
    # Fixed off-ancestry roots are exported even for historical repaired phases;
    # authenticate them independently of current phase or catalog selection.
    processor_roots = _authenticate_processor_roots(root, None, (before, old_after, after))
    delta = set(filter(None, _git(root, 'diff', '--no-renames', '--name-only', '-z', B_R, head).decode().split('\0')))
    owner_scope = _owner_direction_scope(root, head, delta)
    require(delta <= GOVERNANCE_PATHS | CRITICAL | HOSTS | owner_scope,
            'unreviewed governance/host delta: '
            + repr(sorted(delta - GOVERNANCE_PATHS - CRITICAL - HOSTS - owner_scope)))
    for revision, path in original.RECEIPTS.items():
        require(current_bytes(root, path) == raw_bytes(root, revision, path), 'current authority receipt substitution')
    for path in _tree(root, original.B):
        if path.startswith(('tools/fixtures/gp_config012_button_host/generated/',
                            'tools/fixtures/gp_config012_button_host/schema/',
                            'tools/fixtures/gp_config012_button_host/nanopb/')):
            require(current_bytes(root, path) == raw_bytes(root, original.B, path), 'frozen decoder/schema substitution: ' + path)
    actual = critical_tree(root, head)
    require(actual in (before, old_after, after), 'current critical tree outside exact repaired campaign contract')
    repaired_records = _catalog(current_bytes(root, TRANSITIONS))
    old_records = _catalog(current_bytes(root, original.TRANSITIONS))
    require(not (repaired_records and old_records), 'contradictory original/repaired acceptance')
    candidate, base = (original.C, original.B) if actual == old_after else (C_R, B_R)
    records = old_records if actual == old_after else repaired_records
    catalog_path = original.TRANSITIONS if actual == old_after else TRANSITIONS
    require(not (old_records if actual != old_after else repaired_records), 'catalog source/candidate contradiction')
    phase = 'BASELINE'
    critical = frozenset()
    if actual != before:
        require(ancestor(root, candidate, head), 'candidate source replay without preserved candidate ancestry')
        phase = 'CANDIDATE_VALIDATION_ONLY'
        critical = CRITICAL
        for path in HOSTS | (PROOF_PATHS if candidate == C_R else frozenset()):
            require(current_bytes(root, path) == raw_bytes(root, candidate, path), 'candidate proof host substitution: ' + path)
        verify_correspondence(root, candidate, base, target=head, integrated=True, check_worktree=not bool(records))
    else:
        verify_correspondence(root, F010, B010, target=head, integrated=True, check_worktree=True)
    for path in original.FROZEN:
        require(current_bytes(root, path) == raw_bytes(root, original.B, path), 'historical fixture changed: ' + path)
    changed = set(filter(None, _git(root, 'diff', '--no-renames', '--name-only', '-z', original.B, head).decode().split('\0'))) | dirty
    for path in changed:
        if classify_path(path) == 'CRITICAL':
            require(path in critical, 'unexpected critical scope input: ' + path)
    state = item(root, head, 'GP-CONFIG-020')
    require(state['status'] != 'HARDWARE_FAILED' and state['hardware_result'] != 'FAIL', 'failed candidate cannot enter campaign phase')
    claims = state['status'] in {'HARDWARE_VALIDATED', 'DONE'} or state['hardware_result'] == 'PASS'
    processor = None
    adopted_processor = ancestor(root, PROCESSOR_ADOPTION, head)
    if adopted_processor:
        observations = _processor_history(root, head, old_records, repaired_records, processor_roots)
        processor = observations['processor']
        require(not observations['integrated'] or bool(records),
                'accepted phase lacks mandatory transition record')
        require(not claims or processor is not None, 'processor claim lacks authenticated E')
        require(processor is None or actual == before or bool(records),
                'integrated processor acceptance lacks mandatory transition record')
    else:
        history = _history(root, head, old_records, repaired_records)
        require(not (claims or history) or bool(records), 'accepted phase lacks mandatory transition record')
    accepted_metadata = frozenset()
    roots = set(ROOTS)
    if processor is not None:
        roots.update(processor['object_roots'])
        if actual == before:
            require(not records and state['status'] == 'HARDWARE_VALIDATED'
                    and not ancestor(root, BUILT_F, head),
                    'source-free processor cannot authorize source/catalog/DONE')
            phase = 'SOURCE_FREE_PROCESSOR'
            accepted_metadata = processor['accepted_metadata_paths']
    if records:
        require(current_bytes(root, catalog_path) == raw_bytes(root, head, catalog_path), 'uncommitted accepted transition record')
        require(actual != before, 'accepted record on baseline source')
        validate = validate_accepted_transition if candidate == C_R else original.validate_accepted_transition
        if adopted_processor:
            require(candidate == C_R and processor is not None
                    and records[0]['review_commit'] == PROCESSOR_R
                    and records[0]['evidence_commit'] == processor['evidence_commit']
                    and all(records[0][key] == PROCESSOR_PINS[key]
                            for key in ('build', 'parent', 'tree')),
                    'integrated transition differs from authenticated processor E/tuple')
            require(ancestor(root, processor['evidence_commit'], records[0]['integration']),
                    'integrated transition omitted authenticated processor E')
        if adopted_processor:
            _validate_accepted_transition(root, records[0], head, observations)
        else:
            validate(root, records[0], head)
        accepted_metadata = accepted_scope_metadata(root, records[0])
        phase = 'ACCEPTED_TRANSITION'
        roots.update(v for k, v in records[0].items() if k not in {'work_order', 'tree'})
        evidence_ref = state['hardware_evidence_record']
        match = re.fullmatch(r'git-json:([0-9a-f]{40}):' + re.escape(EVIDENCE), str(evidence_ref))
        if match:
            roots.add(match.group(1))
    proof = {'phase': phase, 'contract': 'c020_abi_repair', 'candidate': candidate, 'base': base,
            'target': head, 'critical_paths': critical, 'accepted_metadata_paths': accepted_metadata,
            'changed_paths': frozenset(changed), 'object_roots': frozenset(roots)}
    if processor is not None:
        proof.update(evidence_commit=processor['evidence_commit'], evidence_root=processor['evidence_root'])
    return proof
