"""Finite adopted GP-VAL-043 proof; host/object evidence is never acceptance."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
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
def validate_accepted_transition(root, record, target):
    """Closed consumer: later014/017 need separately adopted literal contracts."""
    root=Path(root).resolve()
    fields={'work_order','candidate','build','parent','tree','review_commit','evidence_commit','integration'}
    require(type(record) is dict and set(record)==fields,'accepted transition fields mismatch')
    require(record['work_order'] in {'GP-CONFIG-020','GP-CONFIG-014','GP-CONFIG-017'},'unknown campaign order')
    require(record['work_order']=='GP-CONFIG-020' and record['candidate']==C_R,'campaign order has no adopted literal candidate contract')
    F=record['build']; parent=record['parent']
    for key in fields-{'work_order'}:
        value=record[key]; require(isinstance(value,str) and len(value)==40 and all(c in '0123456789abcdef' for c in value),'nonimmutable transition identity: '+key)
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
    return accepted


@original._proof_invocation
def authenticate(root):
    root = Path(root).resolve()
    head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    dirty = set()
    for args in [('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z'),
                 ('ls-files', '--others', '--exclude-standard', '-z')]:
        dirty.update(filter(None, _git(root, *args).decode().split('\0')))
    require(dirty <= GOVERNANCE_PATHS, 'dirty path outside reviewed governance inventory')
    # Accepted metadata is immutable under the existing final correspondence proof.
    # Reject its live substitutions before expensive source validation. A catalog
    # here can only cause rejection; every successful call still authenticates it.
    accepted_literals = frozenset((PROTOCOL, EVIDENCE,
        'docs/calibration/gp_config_020_hardware_result.md', MAPPING))
    if dirty & (accepted_literals | {TRANSITIONS, original.TRANSITIONS}):
        inventory = _tree(root, head)
        for catalog in (TRANSITIONS, original.TRANSITIONS):
            protected = accepted_literals | {catalog}
            if dirty & protected and catalog in inventory and _catalog(raw_bytes(root, head, catalog)):
                require(False, 'accepted metadata substitution or nonregular file mode: '
                        + repr(sorted(dirty & protected)))
    require(ancestor(root, B_R, head), 'repaired campaign snapshot lacks adopted authority')
    before, old_after, after = source_contract(root)
    delta = set(filter(None, _git(root, 'diff', '--no-renames', '--name-only', '-z', B_R, head).decode().split('\0')))
    require(delta <= GOVERNANCE_PATHS | CRITICAL | HOSTS,
            'unreviewed governance/host delta: ' + repr(sorted(delta - GOVERNANCE_PATHS - CRITICAL - HOSTS)))
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
    history = _history(root, head, old_records, repaired_records)
    require(not (claims or history) or bool(records), 'accepted phase lacks mandatory transition record')
    accepted_metadata = frozenset()
    roots = set(ROOTS)
    if records:
        require(current_bytes(root, catalog_path) == raw_bytes(root, head, catalog_path), 'uncommitted accepted transition record')
        require(actual != before, 'accepted record on baseline source')
        validate = validate_accepted_transition if candidate == C_R else original.validate_accepted_transition
        validate(root, records[0], head)
        accepted_metadata = accepted_scope_metadata(root, records[0])
        phase = 'ACCEPTED_TRANSITION'
        roots.update(v for k, v in records[0].items() if k not in {'work_order', 'tree'})
        evidence_ref = state['hardware_evidence_record']
        match = re.fullmatch(r'git-json:([0-9a-f]{40}):' + re.escape(EVIDENCE), str(evidence_ref))
        if match:
            roots.add(match.group(1))
    return {'phase': phase, 'contract': 'c020_abi_repair', 'candidate': candidate, 'base': base,
            'target': head, 'critical_paths': critical, 'accepted_metadata_paths': accepted_metadata,
            'changed_paths': frozenset(changed), 'object_roots': frozenset(roots)}
