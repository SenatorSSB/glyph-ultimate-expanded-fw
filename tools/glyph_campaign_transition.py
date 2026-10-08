"""Finite GP-VAL-037 source proofs; candidate validation is never hardware PASS."""
from __future__ import annotations
import hashlib
import json
import re
import stat
from pathlib import Path
from contextvars import ContextVar
from functools import wraps
from glyph_hardware_correspondence import CorrespondenceError, classify_path, verify_correspondence, _git, _immutable_query_cache, _tree as _uncached_tree

C = '256bf44cea71f6d5c87aa1675c8dac9f6b79259f'
B = '3dac79dac4eefcf832510817e8cb5ecd6a27f219'
C_TREE = '45831eeb88ece9c8b293e2e819ee5ecb362b64ec'
PRIOR_ADOPTION = 'a8e249eb210b7cd1e010e27dee8f4c61f8fcb537'
ARGUMENT_OPENING = '32280bc9eadfcd7fbcc19bd8df60576e3b0a49eb'
ADOPTION = '93b3c9ee8f702886f731714281ce143428724a17'
HANDOFF = '41ba14202450860340e07bea161f7910c3af922c'
F010 = '1c0ff22646729d26d45eacb4b8322c5baea7de48'
B010 = '22c639c31ea7006c18a29ec2693c8b18ff688ed4'
RECEIPTS = {
 '6cb59e97ddfdb96830432923ac588a76383153b7': 'docs/agent_framework/curation_receipts/gp_val037_current_arguments_20261003.json',
 '9c40e734c4e78f9a00e9bd423cfe3021e0f5a5e0': 'docs/agent_framework/curation_receipts/gp_val037_predecessor_20261003.json',
 '85c1ec43abffb737d080f19190b393c591b862ef': 'docs/agent_framework/curation_receipts/gp_val037_guard_applicability_20261003.json',
}
ROOTS = frozenset((C, B, PRIOR_ADOPTION, ARGUMENT_OPENING, ADOPTION, HANDOFF, F010, B010, *RECEIPTS,
 '3c1ad47cb5e7e268a8a5fd6852135649c8b60f0a', '49528e32849069e87f2729c24be35a21b002b6df',
 '3194fd86c5391f19e598acae7879d6898e3e2072','60614dae8150338160b3440aef6b275bf073fecf'))
CRITICAL = frozenset(('HAL/pico/src/comms/ConfiguratorBackend.cpp',
 'include/core/config_button_validation.hpp', 'src/core/config_button_validation.cpp'))
HOSTS = frozenset(('tools/check_glyph_gp_config020_button_validation.py',
 'tools/fixtures/gp_config020_button_validation/decoder_harness.cpp',
 'tools/fixtures/gp_config020_button_validation/include/Adafruit_TinyUSB.h',
 'tools/fixtures/gp_config020_button_validation/setconfig_harness.cpp',
 'tools/fixtures/gp_config020_button_validation/validation_harness.cpp'))
FROZEN = tuple('docs/runtime_config/fixtures/'+name+'.json' for name in (
 'config_menu_invalid_state_characterization','configurator_setconfig_transaction',
 'current_config_persistence_recovery_research','getconfig_raw_load_characterization',
 'gp_config012_button_mask_characterization','gp_config013_usb_default_characterization',
 'setconfig_runtime_rebinding_characterization'))
GOVERNANCE_PATHS = frozenset(('docs/AGENT_CONTEXT.md', 'docs/CURRENT_STATE.md', 'docs/ROADMAP.md', 'docs/project/ACTIVE_AGENT_QUEUE.md', 'docs/agent_framework/HARDWARE_CORRESPONDENCE.md', 'docs/runtime_config/fixtures/runtime_config_validation_manifest.json', 'docs/runtime_config/fixtures/glyph_checker_census.json', 'docs/runtime_config/fixtures/runtime_config_validation_health.json', 'docs/runtime_config/runtime_config_validation_health.md', 'docs/runtime_config/fixtures/gp_val037_accepted_transitions.json', 'tools/glyph_campaign_transition.py', 'tools/glyph_hardware_correspondence.py', 'tools/glyph_checker_context.py', 'tools/check_glyph_checker_context.py', 'tools/check_glyph_config_010_integration_semantic_correspondence.py', 'tools/test_glyph_config_010_semantic_applicability.py', 'tools/test_glyph_hardware_correspondence.py', 'tools/check_glyph_runtime_config_webserial_device_write_source_authority.py', 'tools/check_glyph_generated_source_owned_generator_contract.py', 'tools/check_glyph_generated_source_owned_artifact_install.py', 'tools/check_glyph_coordinate_native_runtime_profile_contract.py', 'tools/check_glyph_generated_source_owned_baseline_artifact.py', 'tools/check_glyph_docs_agent_surface.py', 'tools/run_glyph_runtime_config_validation.py', 'tools/check_glyph_runtime_config_validation_aggregate.py', 'tools/check_glyph_gp_config012_button_mask_characterization.py', 'tools/check_glyph_gp_config013_usb_default_characterization.py', 'tools/check_glyph_config_menu_invalid_state_characterization.py', 'tools/check_glyph_setconfig_runtime_rebinding_characterization.py', 'tools/check_glyph_current_config_persistence_recovery_research.py', 'tools/check_glyph_configurator_setconfig_transaction.py', 'tools/check_glyph_getconfig_raw_load_characterization.py', 'tools/fixtures/configurator_setconfig_host/handler_harness.cpp', 'tools/fixtures/configurator_setconfig_host/include/host_stubs.hpp', 'docs/agent_framework/GP_CONFIG_020_HARDWARE_PROTOCOL.md', 'docs/calibration/gp_config_020_hardware_result.md', 'docs/calibration/fixtures/gp_config_020_hardware_evidence.json'))
TRANSITIONS = 'docs/runtime_config/fixtures/gp_val037_accepted_transitions.json'
QUEUE = 'docs/project/ACTIVE_AGENT_QUEUE.md'
PROTOCOL = 'docs/agent_framework/GP_CONFIG_020_HARDWARE_PROTOCOL.md'
EVIDENCE = 'docs/calibration/fixtures/gp_config_020_hardware_evidence.json'
INSERT_INCLUDE = b'#include "core/config_button_validation.hpp"\n'
INSERT_BODY = b'''    if (!validate_config_button_bindings(candidate)) {
        char errmsg[] = "Config contains an invalid button binding";
        WritePacket(CMD_ERROR, (uint8_t *)errmsg, sizeof(errmsg));
        return false;
    }

'''

# Memoize immutable inventories/blob bytes only for one proof invocation. No
# worktree bytes, index state, symbolic ref, or successful proof is memoized.
_tree_inventory_cache = ContextVar('campaign_tree_inventory_cache', default=None)
_blob_bytes_cache = ContextVar('campaign_blob_bytes_cache', default=None)


def _proof_invocation(function):
    @wraps(function)
    def invoke(*args, **kwargs):
        if _tree_inventory_cache.get() is not None:
            return function(*args, **kwargs)
        token = _tree_inventory_cache.set({})
        blob_token = _blob_bytes_cache.set({})
        query_token = _immutable_query_cache.set({})
        try:
            return function(*args, **kwargs)
        finally:
            _blob_bytes_cache.reset(blob_token)
            _immutable_query_cache.reset(query_token)
            _tree_inventory_cache.reset(token)
    return invoke


def _tree(root, ref):
    cache = _tree_inventory_cache.get()
    if cache is None or not isinstance(ref,str) or re.fullmatch('[0-9a-f]{40}',ref) is None:
        return _uncached_tree(root,ref)
    key=(str(Path(root).resolve()),ref)
    if key not in cache:
        cache[key]=_uncached_tree(root,ref)
    # Keep callers from changing the memoized immutable inventory.
    return dict(cache[key])


def require(ok, message):
    if not ok: raise CorrespondenceError(message)

def unique(pairs):
    result = {}
    for k,v in pairs:
        require(k not in result, 'duplicate transition JSON key: '+k); result[k]=v
    return result

def queue(root, ref):
    raw = raw_bytes(root,ref,QUEUE).decode()
    require(raw.count('<!-- queue-state:start -->')==1 and raw.count('<!-- queue-state:end -->')==1,'queue marker drift')
    raw=raw.split('<!-- queue-state:start -->')[1].split('<!-- queue-state:end -->')[0].strip()
    require(raw.startswith('```json') and raw.endswith('```'),'queue fence drift')
    return json.loads(raw[7:-3],object_pairs_hook=unique)

def item(root, ref, order):
    found=[x for x in queue(root,ref)['items'] if x['id']==order]
    require(len(found)==1,'missing/duplicate campaign work order'); return found[0]

def ancestor(root, older, newer):
    return _git(root,'merge-base',older,newer).decode().strip()==older

def critical_tree(root, ref):
    found={}
    for p,e in _tree(root,ref).items():
        try: category=classify_path(p)
        except CorrespondenceError: continue
        if category=='CRITICAL': found[p]=e
    return found

def raw_bytes(root, ref, path):
    entry=_tree(root,ref).get(path)
    require(entry is not None and entry[:2]==('100644','blob'),'nonregular proof source: '+path)
    cache=_blob_bytes_cache.get()
    if cache is None or not isinstance(ref,str) or re.fullmatch('[0-9a-f]{40}',ref) is None:
        return _git(root,'show',ref+':'+path)
    # Distinct immutable commits may name the same blob. Keep every per-ref
    # mode/type check above and reparse callers' JSON; only bytes are shared.
    key=(str(Path(root).resolve()),entry[2])
    if key not in cache:
        cache[key]=_git(root,'show',ref+':'+path)
    return cache[key]

def current_bytes(root, path):
    p=root/path
    require(all(not x.is_symlink() for x in [p,*list(p.parents)[:-1]]),'symlinked proof input: '+path)
    require(stat.S_ISREG(p.stat().st_mode) and not p.stat().st_mode & 0o111,'nonregular proof input: '+path)
    return p.read_bytes()

@_proof_invocation
def source_contract(root):
    require(_git(root,'rev-list','--parents','-n','1',C).decode().split()==[C,B],'C020 direct parent mismatch')
    require(_git(root,'rev-parse',C+'^{tree}').decode().strip()==C_TREE,'C020 tree mismatch')
    raw=_git(root,'diff-tree','-r','--no-renames','--raw','-z',B,C)
    require(hashlib.sha256(raw).hexdigest()=='7197560406157c5a43963157f79a010dec424553db7f14235859fab42278e27c','C020 complete raw inventory mismatch')
    paths=set(_git(root,'diff','--no-renames','--name-only','-z',B,C).decode().strip('\0').split('\0'))
    require(paths==CRITICAL|HOSTS,'C020 inventory membership mismatch')
    for p in paths: raw_bytes(root,C,p)
    old=raw_bytes(root,B,'HAL/pico/src/comms/ConfiguratorBackend.cpp')
    new=raw_bytes(root,C,'HAL/pico/src/comms/ConfiguratorBackend.cpp')
    require(new.count(INSERT_INCLUDE)==1 and new.count(INSERT_BODY)==1,'validator insertion missing/duplicate')
    require(new.replace(INSERT_INCLUDE,b'').replace(INSERT_BODY,b'')==old,'C020 changed more than exact reviewed validator insertion')
    before, after=critical_tree(root,B),critical_tree(root,C)
    require({p for p in before.keys()|after.keys() if before.get(p)!=after.get(p)}==CRITICAL,'extra critical candidate change')
    require(critical_tree(root,F010)==before==critical_tree(root,ADOPTION),'accepted starting critical tree mismatch')
    for ref,path in RECEIPTS.items():
        require(ancestor(root,ref,ADOPTION),'receipt not adopted')
        require(raw_bytes(root,ref,path)==raw_bytes(root,ADOPTION,path),'receipt substitution')
    # This exact source-free three-commit authority progression is closed.
    previous = PRIOR_ADOPTION
    for revision, paths in (
        (ARGUMENT_OPENING, {'docs/AGENT_CONTEXT.md','docs/CURRENT_STATE.md','docs/ROADMAP.md',QUEUE}),
        ('6cb59e97ddfdb96830432923ac588a76383153b7', {RECEIPTS['6cb59e97ddfdb96830432923ac588a76383153b7']}),
        (ADOPTION, {'docs/AGENT_CONTEXT.md','docs/CURRENT_STATE.md','docs/ROADMAP.md',QUEUE}),
    ):
        require(_git(root,'rev-list','--parents','-n','1',revision).decode().split()==[revision,previous], 'authority progression parent mismatch')
        changed=set(filter(None,_git(root,'diff','--no-renames','--name-only','-z',previous,revision).decode().split('\0')))
        require(changed==paths, 'authority progression path mismatch')
        for path in paths: raw_bytes(root,revision,path)
        previous=revision
    authority=item(root,ADOPTION,'GP-VAL-037')
    require(authority['status']=='PREAUTHORIZED' and authority['activation_state']=='ACTIVATABLE','immutable037authority mismatch')
    for token in (C,B,C_TREE,'--campaign-transition','accepted-transition'):
        require(token in authority['scope'],'incomplete immutable037scope')
    handoff=item(root,HANDOFF,'GP-CONFIG-020')
    require(handoff['status']=='REVIEW' and handoff['candidate_git_sha']==C and handoff['candidate_base_configurator_sha']==B,'independent handoff identity mismatch')
    require(handoff['done_evidence'] and handoff['source_authority'],'missing source review handoff')
    # Exact immutable predecessor result, distinct from any new acceptance.
    evidence='docs/calibration/fixtures/gp_config_010_integration_hardware_evidence_2026-09-23.json'
    raw=raw_bytes(root,'60614dae8150338160b3440aef6b275bf073fecf',evidence)
    require(hashlib.sha256(raw).hexdigest()=='5f87066df7a06a44340790237fcf3a1ec0adfc0f9a51cb46edb1c9d6dbc38a54','accepted baseline evidence substitution')
    result=json.loads(raw,object_pairs_hook=unique)
    require(result['candidate_git_sha']==F010 and result['result']=='PASS' and result['evidence_gaps']==[],'accepted baseline result mismatch')
    return before,after

def validate_build_review(text, record, digest, locator):
    """Parse the native exact hardware-protocol handoff bullets, never queue prose."""
    # Wrapped native bullets are folded only within their own item. Require one
    # occurrence of every identity label, rejecting duplicate/contradictory blocks.
    labels = {
        'Candidate Git SHA': '`'+record['build']+'`',
        'Candidate tree': '`'+record['tree']+'`',
        'Sole parent / authorized canonical base': '`'+record['parent']+'`',
        'UF2 SHA-256': '`'+digest+'`',
        'Preserved locator': '`'+locator+'`',
        'Fresh independent postimplementation review':
            'PASS with no findings for the exact candidate, build output, custody bytes, correspondence, and protocol.',
    }
    for label,expected in labels.items():
        pattern=r'^- '+re.escape(label)+r':([^\n]*(?:\n[ \t]+[^\n]+)*)'
        matches=re.findall(pattern,text,re.MULTILINE)
        require(len(matches)==1 and ' '.join(matches[0].split())==expected,
                'missing, duplicate or mismatched build review field: '+label)
        require(text.casefold().count(label.casefold()+':')==1,'duplicate build review label: '+label)
    statuses=re.findall(r'review[^\n:]*:\s*(PASS|FAIL|PENDING|NOT_APPROVED|INCOMPLETE)',text,re.IGNORECASE)
    require([x.upper() for x in statuses]==['PASS'],'contradictory review status')


@_proof_invocation
def validate_accepted_transition(root, record, target):
    """Closed consumer: later014/017 need separately adopted literal contracts."""
    root=Path(root).resolve()
    fields={'work_order','candidate','build','parent','tree','review_commit','evidence_commit','integration'}
    require(type(record) is dict and set(record)==fields,'accepted transition fields mismatch')
    require(record['work_order'] in {'GP-CONFIG-020','GP-CONFIG-014','GP-CONFIG-017'},'unknown campaign order')
    require(record['work_order']=='GP-CONFIG-020' and record['candidate']==C,'campaign order has no adopted literal candidate contract')
    F=record['build']; parent=record['parent']
    for key in fields-{'work_order'}:
        value=record[key]; require(isinstance(value,str) and len(value)==40 and all(c in '0123456789abcdef' for c in value),'nonimmutable transition identity: '+key)
    require(_git(root,'rev-list','--parents','-n','1',F).decode().split()==[F,parent],'built F direct parent mismatch')
    require(_git(root,'rev-parse',F+'^{tree}').decode().strip()==record['tree'],'built F tree mismatch')
    require(ancestor(root,C,F) and ancestor(root,ADOPTION,F),'built F omitted candidate/governance authority')
    verify_correspondence(root,C,B,target=F,integrated=True,check_worktree=False)
    require(ancestor(root,F,record['integration']) and ancestor(root,record['integration'],target),'reviewed integration ancestry mismatch')
    R,E,I=record['review_commit'],record['evidence_commit'],record['integration']
    require(R!=E and E!=I and ancestor(root,ADOPTION,R) and ancestor(root,R,E)
            and ancestor(root,E,I), 'review/PASS/integration chronology mismatch')
    # Review and evidence are source-free canonical snapshots referencing unmerged F.
    require(not ancestor(root,F,R) and not ancestor(root,F,E), 'firmware integrated before review/PASS')
    require(critical_tree(root,R)==critical_tree(root,B)==critical_tree(root,E),
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

def accepted_scope_metadata(root, record):
    """Only exact, immutable accepted-result metadata may leave the scope view."""
    review, evidence = record['review_commit'], record['evidence_commit']
    require(raw_bytes(root,review,PROTOCOL)==raw_bytes(root,evidence,PROTOCOL),
            'accepted protocol changed after independent review')
    paths={PROTOCOL,EVIDENCE}
    result='docs/calibration/gp_config_020_hardware_result.md'
    if result in _tree(root,'HEAD') or (root/result).exists():
        paths.add(result)
    for path in paths:
        require(current_bytes(root,path)==raw_bytes(root,evidence,path),
                'accepted scope metadata substitution: '+path)
    return frozenset(paths)


def prior_accepted_phase(root, head, records):
    """Acceptance is monotonic across immutable queue/catalog history.

    Looking only at the current queue would let a later edit erase processor
    PASS and relabel integrated source as an unaccepted candidate.
    """
    accepted=False
    # No pathspec: Git path-history simplification can hide a second parent's
    # accepted state when an ours merge keeps the unaccepted first-parent tree.
    revisions=_git(root,'rev-list','--reverse','--topo-order',ADOPTION+'..'+head).decode().split()
    for revision in revisions:
        state=item(root,revision,'GP-CONFIG-020')
        accepted |= state['status'] in {'HARDWARE_VALIDATED','DONE'} or state['hardware_result']=='PASS'
        if TRANSITIONS not in _tree(root,revision):
            continue
        catalog=json.loads(raw_bytes(root,revision,TRANSITIONS),object_pairs_hook=unique)
        require(type(catalog) is dict and set(catalog)=={'schema_version','accepted_transitions'}
                and type(catalog['schema_version']) is int and catalog['schema_version']==1,
                'historical transition catalog schema drift')
        previous=catalog['accepted_transitions']
        require(type(previous) is list and len(previous)<=1,'historical unadopted transition extension')
        if previous:
            require(previous==records,'accepted transition history erased or substituted')
            accepted=True
    return accepted


@_proof_invocation
def authenticate(root):
    root=Path(root).resolve(); head=_git(root,'rev-parse','HEAD').decode().strip()
    # Reject forbidden live changes before paying for immutable source proofs.
    # Allowed governance inputs still pass every immutable and final live gate.
    dirty=set()
    for args in [('diff','--name-only','-z'),('diff','--cached','--name-only','-z'),('ls-files','--others','--exclude-standard','-z')]:
        dirty.update(x for x in _git(root,*args).decode().split('\0') if x)
    require(dirty <= GOVERNANCE_PATHS, 'dirty path outside reviewed governance inventory')
    before,after=source_contract(root)
    require(ancestor(root,ADOPTION,head),'campaign snapshot lacks adopted authority')
    delta=set(x for x in _git(root,'diff','--no-renames','--name-only','-z',ADOPTION,head).decode().split('\0') if x)
    require(delta <= GOVERNANCE_PATHS | CRITICAL | HOSTS, 'unreviewed governance/host delta: '+repr(sorted(delta-GOVERNANCE_PATHS-CRITICAL-HOSTS)))
    for revision, path in RECEIPTS.items():
        require(current_bytes(root,path)==raw_bytes(root,revision,path),'current authority receipt substitution')
    for path in _tree(root,B):
        if path.startswith(('tools/fixtures/gp_config012_button_host/generated/',
                            'tools/fixtures/gp_config012_button_host/schema/',
                            'tools/fixtures/gp_config012_button_host/nanopb/')):
            require(current_bytes(root,path)==raw_bytes(root,B,path),'frozen decoder/schema substitution: '+path)
    actual=critical_tree(root,head)
    require(actual in (before,after),'current critical tree outside exact campaign contract')
    value=json.loads(current_bytes(root,TRANSITIONS),object_pairs_hook=unique)
    require(type(value) is dict and set(value)=={'schema_version','accepted_transitions'} and type(value['schema_version']) is int and value['schema_version']==1,'transition catalog schema drift')
    records=value['accepted_transitions'];require(type(records) is list and len(records)<=1,'unadopted accepted transition extension')
    phase='BASELINE'; critical=frozenset()
    if actual==after:
        require(ancestor(root,C,head),'candidate source replay without preserved C ancestry')
        phase='CANDIDATE_VALIDATION_ONLY';critical=CRITICAL
        for path in HOSTS:
            require(current_bytes(root,path)==raw_bytes(root,C,path),'candidate proof host substitution: '+path)
        # A nonempty catalog must pass validate_accepted_transition below, whose
        # final F->HEAD proof always checks the live worktree. Avoid scanning it
        # twice; an empty candidate catalog retains its own full live check.
        verify_correspondence(root,C,B,target=head,integrated=True,check_worktree=not bool(records))
    else:
        verify_correspondence(root,F010,B010,target=head,integrated=True,check_worktree=True)
    # All historical observations remain frozen, even when current source changes.
    for path in FROZEN:
        require(current_bytes(root,path)==raw_bytes(root,B,path),'historical fixture changed: '+path)
    changed=set(_git(root,'diff','--no-renames','--name-only','-z',B,head).decode().strip('\0').split('\0'))-{''}
    for args in [('diff','--no-renames','--name-only','-z'),('diff','--cached','--no-renames','--name-only','-z'),('ls-files','--others','--exclude-standard','-z')]:
        changed.update(x for x in _git(root,*args).decode().split('\0') if x)
    for path in changed:
        category=classify_path(path)
        if category=='CRITICAL':require(path in critical,'unexpected critical scope input: '+path)
    state=item(root,head,'GP-CONFIG-020')
    require(state['status']!='HARDWARE_FAILED' and state['hardware_result']!='FAIL', 'failed candidate cannot enter campaign phase')
    claims_acceptance=(state['status'] in {'HARDWARE_VALIDATED','DONE'} or state['hardware_result']=='PASS')
    historical_acceptance=prior_accepted_phase(root,head,records)
    require(actual!=after or not (claims_acceptance or historical_acceptance) or bool(records),
            'accepted phase lacks mandatory transition record')
    accepted_metadata=frozenset()
    if records:
        require(current_bytes(root,TRANSITIONS)==raw_bytes(root,head,TRANSITIONS),'uncommitted accepted transition record')
        require(actual==after,'accepted record on baseline source')
        validate_accepted_transition(root,records[0],head)
        accepted_metadata=accepted_scope_metadata(root,records[0])
        phase='ACCEPTED_TRANSITION'
    return {'phase':phase,'candidate':C,'base':B,'target':head,'critical_paths':critical,'accepted_metadata_paths':accepted_metadata,'changed_paths':frozenset(changed)}

@_proof_invocation
def verify_current_source(root, path, historical_sha256):
    """Prove exact B/C first, then expose frozen B bytes for historical assertions."""
    from glyph_c022_campaign_transition import present as c022_present
    if c022_present(Path(root)):
        from glyph_c022_campaign_transition import verify_current_source as rgb_targets
        return rgb_targets(root, path, historical_sha256)
    from glyph_c021_campaign_transition import present as c021_present
    if c021_present(Path(root)):
        from glyph_c021_campaign_transition import verify_current_source as recovery
        return recovery(root, path, historical_sha256)
    from glyph_c017_campaign_transition import present as c017_present
    if c017_present(Path(root)):
        from glyph_c017_campaign_transition import verify_current_source as neopixel
        return neopixel(root, path, historical_sha256)
    if _c014_present(Path(root)):
        from glyph_c014_campaign_transition import verify_current_source as capacity
        return capacity(root, path, historical_sha256)
    root=Path(root); old=raw_bytes(root,B,path)
    require(hashlib.sha256(old).hexdigest()==historical_sha256,'historical source identity mismatch: '+path)
    actual=current_bytes(root,path)
    if actual!=old:
        proof=authenticate(root)
        require(proof['phase']!='BASELINE' and path in CRITICAL,'unadopted current source overlay: '+path)
        require(actual==raw_bytes(root,proof['candidate'],path),'current source substitution: '+path)
    return old


# Preserve the historical callable and its literal source_contract/constants.
authenticate_original = authenticate


def _c014_present(root):
    """A capacity proof literal selects its complete contract or fails closed."""
    head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    paths = ('docs/runtime_config/fixtures/gp_val034_c014_transition.json',
             'docs/runtime_config/fixtures/gp_val034_accepted_transitions.json',
             'tools/glyph_c014_campaign_transition.py')
    inventory = _tree(root, head)
    return any(path in inventory or (root / path).exists() for path in paths)


@_proof_invocation
def authenticate(root):
    root = Path(root).resolve()
    from glyph_c022_campaign_transition import present as c022_present
    if c022_present(root):
        from glyph_c022_campaign_transition import authenticate as rgb_targets
        return rgb_targets(root)
    from glyph_c021_campaign_transition import present as c021_present
    if c021_present(root):
        from glyph_c021_campaign_transition import authenticate as recovery
        return recovery(root)
    from glyph_c017_campaign_transition import present as c017_present
    if c017_present(root):
        from glyph_c017_campaign_transition import authenticate as neopixel
        return neopixel(root)
    if _c014_present(root):
        from glyph_c014_campaign_transition import authenticate as capacity
        return capacity(root)
    head = _git(root, 'rev-parse', 'HEAD').decode().strip()
    B_R = "0f7fe50b3b5f385397a9737bc4c0a50ddda683c8"
    MAPPING = "docs/runtime_config/fixtures/gp_val043_c020_abi_repair.json"
    REPAIRED_TRANSITIONS = "docs/runtime_config/fixtures/gp_val043_accepted_transitions.json"
    present = any(path in _tree(root, head) or (root / path).exists()
                  for path in (MAPPING, REPAIRED_TRANSITIONS))
    # Missing adopted objects with repaired literals present must never fall back.
    adopted = False
    try:
        adopted = ancestor(root, B_R, head)
    except CorrespondenceError:
        require(not present, 'repaired mapping lacks adopted immutable authority')
    if adopted or present:
        from glyph_c020_abi_repair_transition import authenticate as repaired
        return repaired(root)
    proof = authenticate_original(root)
    return dict(proof, contract='original037', object_roots=ROOTS)
