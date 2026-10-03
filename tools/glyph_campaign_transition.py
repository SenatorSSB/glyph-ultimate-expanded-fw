"""Finite GP-VAL-037 source proofs; candidate validation is never hardware PASS."""
from __future__ import annotations
import hashlib
import json
import stat
from pathlib import Path
from glyph_hardware_correspondence import CorrespondenceError, classify_path, verify_correspondence, _git, _tree

C = '256bf44cea71f6d5c87aa1675c8dac9f6b79259f'
B = '3dac79dac4eefcf832510817e8cb5ecd6a27f219'
C_TREE = '45831eeb88ece9c8b293e2e819ee5ecb362b64ec'
ADOPTION = 'a8e249eb210b7cd1e010e27dee8f4c61f8fcb537'
HANDOFF = '41ba14202450860340e07bea161f7910c3af922c'
F010 = '1c0ff22646729d26d45eacb4b8322c5baea7de48'
B010 = '22c639c31ea7006c18a29ec2693c8b18ff688ed4'
RECEIPTS = {
 '9c40e734c4e78f9a00e9bd423cfe3021e0f5a5e0': 'docs/agent_framework/curation_receipts/gp_val037_predecessor_20261003.json',
 '85c1ec43abffb737d080f19190b393c591b862ef': 'docs/agent_framework/curation_receipts/gp_val037_guard_applicability_20261003.json',
}
ROOTS = frozenset((C, B, ADOPTION, HANDOFF, F010, B010, *RECEIPTS,
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
INSERT_INCLUDE = b'#include "core/config_button_validation.hpp"\n'
INSERT_BODY = b'''    if (!validate_config_button_bindings(candidate)) {
        char errmsg[] = "Config contains an invalid button binding";
        WritePacket(CMD_ERROR, (uint8_t *)errmsg, sizeof(errmsg));
        return false;
    }

'''

def require(ok, message):
    if not ok: raise CorrespondenceError(message)

def unique(pairs):
    result = {}
    for k,v in pairs:
        require(k not in result, 'duplicate transition JSON key: '+k); result[k]=v
    return result

def queue(root, ref):
    raw = _git(root,'show',ref+':'+QUEUE).decode()
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
    return _git(root,'show',ref+':'+path)

def current_bytes(root, path):
    p=root/path
    require(all(not x.is_symlink() for x in [p,*list(p.parents)[:-1]]),'symlinked proof input: '+path)
    require(stat.S_ISREG(p.stat().st_mode) and not p.stat().st_mode & 0o111,'nonregular proof input: '+path)
    return p.read_bytes()

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

def validate_accepted_transition(root, record, target):
    """Closed consumer: later014/017 need separately adopted literal contracts."""
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
    review=item(root,record['review_commit'],'GP-CONFIG-020')
    require(ancestor(root,F,record['review_commit']) and ancestor(root,record['review_commit'],target),'review receipt ancestry mismatch')
    require(review['candidate_git_sha']==F and review['candidate_base_configurator_sha']==parent,'review built snapshot mismatch')
    provenance=review['done_evidence']
    require(isinstance(provenance,str) and F in provenance and 'independent' in provenance.lower() and 'review' in provenance.lower(),'missing exact independent build review provenance')
    accepted=item(root,record['evidence_commit'],'GP-CONFIG-020')
    require(ancestor(root,record['review_commit'],record['evidence_commit']) and ancestor(root,record['evidence_commit'],target),'processor receipt ancestry mismatch')
    require(accepted['status'] in {'HARDWARE_VALIDATED','DONE'} and accepted['hardware_result']=='PASS' and accepted['hardware_evidence_gaps']==[],'missing exact processor PASS')
    require(accepted['candidate_git_sha']==F and accepted['candidate_base_configurator_sha']==parent,'processor built snapshot mismatch')
    from check_glyph_agent_framework_docs import validate_work_order, validate_evidence_record
    validate_work_order(accepted,evidence_repo_root=root);validate_evidence_record(accepted,evidence_repo_root=root)
    verify_correspondence(root,F,parent,target=target,integrated=True,check_worktree=True)
    return F

def authenticate(root):
    root=Path(root).resolve(); head=_git(root,'rev-parse','HEAD').decode().strip()
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
    phase='BASELINE'; critical=frozenset()
    if actual==after:
        require(ancestor(root,C,head),'candidate source replay without preserved C ancestry')
        phase='CANDIDATE_VALIDATION_ONLY';critical=CRITICAL
        for path in HOSTS:
            require(current_bytes(root,path)==raw_bytes(root,C,path),'candidate proof host substitution: '+path)
        verify_correspondence(root,C,B,target=head,integrated=True,check_worktree=True)
    else:
        verify_correspondence(root,F010,B010,target=head,integrated=True,check_worktree=True)
    # All historical observations remain frozen, even when current source changes.
    for path in FROZEN:
        require(current_bytes(root,path)==raw_bytes(root,B,path),'historical fixture changed: '+path)
    changed=set(_git(root,'diff','--no-renames','--name-only','-z',B,head).decode().strip('\0').split('\0'))-{''}
    for args in [('diff','--no-renames','--name-only','-z'),('diff','--cached','--no-renames','--name-only','-z'),('ls-files','--others','--exclude-standard','-z')]:
        changed.update(x for x in _git(root,*args).decode().split('\0') if x)
    dirty=set()
    for args in [('diff','--name-only','-z'),('diff','--cached','--name-only','-z'),('ls-files','--others','--exclude-standard','-z')]:
        dirty.update(x for x in _git(root,*args).decode().split('\0') if x)
    require(dirty <= GOVERNANCE_PATHS, 'dirty path outside reviewed governance inventory')
    for path in changed:
        category=classify_path(path)
        if category=='CRITICAL':require(path in critical,'unexpected critical scope input: '+path)
    location=root/TRANSITIONS
    if location.exists():
        value=json.loads(current_bytes(root,TRANSITIONS),object_pairs_hook=unique)
        require(type(value) is dict and set(value)=={'schema_version','accepted_transitions'} and type(value['schema_version']) is int and value['schema_version']==1,'transition catalog schema drift')
        records=value['accepted_transitions'];require(type(records) is list and len(records)<=1,'unadopted accepted transition extension')
        if records:
            require(current_bytes(root,TRANSITIONS)==raw_bytes(root,head,TRANSITIONS),'uncommitted accepted transition record')
            require(actual==after,'accepted record on baseline source')
            validate_accepted_transition(root,records[0],head);phase='ACCEPTED_TRANSITION'
    return {'phase':phase,'candidate':C,'base':B,'target':head,'critical_paths':critical,'changed_paths':frozenset(changed)}

def verify_current_source(root, path, historical_sha256):
    """Prove exact B/C first, then expose frozen B bytes for historical assertions."""
    root=Path(root); old=raw_bytes(root,B,path)
    require(hashlib.sha256(old).hexdigest()==historical_sha256,'historical source identity mismatch: '+path)
    actual=current_bytes(root,path)
    if actual!=old:
        proof=authenticate(root)
        require(proof['phase']!='BASELINE' and path in CRITICAL,'unadopted current source overlay: '+path)
        require(actual==raw_bytes(root,C,path),'current source substitution: '+path)
    return old
