#!/usr/bin/env python3
"""Finite GP-VAL-034 proof tests. All new evidence below is synthetic test data.

No build, device, network, firmware custody or physical acceptance occurs here.
Disposable native Git repositories exercise actual object/index/worktree seams.
"""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import time
import glyph_c014_campaign_transition as proof

ROOT = Path(__file__).resolve().parents[1]

def git(root, *args, check=True):
    p = subprocess.run(['git', '-C', str(root), '-c', 'core.hooksPath=/dev/null', *args],
                       capture_output=True, check=check)
    return p.stdout.decode().strip()

def write(root, path, raw):
    f = root / path; f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(raw if isinstance(raw, bytes) else raw.encode()); f.chmod(0o644)

def commit(root, label, empty=False):
    git(root, 'add', '--all')
    args = ['commit', '-q', '-m', 'SYNTHETIC PROOF TEST: ' + label]
    if empty: args.append('--allow-empty')
    git(root, *args)
    return git(root, 'rev-parse', 'HEAD')

def checkout(root, ref):
    git(root, 'checkout', '--detach', '--quiet', ref)

def alter_queue(root, order, **values):
    raw = (root / proof.QUEUE).read_text(); begin = '<!-- queue-state:start -->'; end = '<!-- queue-state:end -->'
    left, tail = raw.split(begin, 1); body, right = tail.split(end, 1)
    data = proof.parsed_queue(raw.encode())
    found = [x for x in data['items'] if x['id'] == order]
    assert len(found) == 1
    found[0].update(values)
    write(root, proof.QUEUE, left + begin + '\n```json\n' + json.dumps(data, indent=2) + '\n```\n' + end + right)

def reject(call, label):
    try: call()
    except Exception as error:
        print('PASS rejected', label, ':', str(error).splitlines()[0])
        return
    raise AssertionError('false acceptance: ' + label)

def new_repository(directory):
    root = Path(directory).resolve()
    subprocess.run(['git', '-c', 'init.templateDir=', 'init', '-q', str(root)], check=True)
    objects = Path(git(ROOT, 'rev-parse', '--git-path', 'objects'))
    if not objects.is_absolute(): objects = ROOT / objects
    (root / '.git/info').mkdir(exist_ok=True)
    (root / '.git/objects/info/alternates').write_text(str(objects.resolve()) + '\n')
    git(root, 'config', 'user.name', 'Synthetic proof test')
    git(root, 'config', 'user.email', 'synthetic-proof@example.invalid')
    checkout(root, proof.READY)
    # A finite draft composition. Never copies caches, objects, ignored files or
    # arbitrary current repository contents. A checker substitution is rejected
    # below against independent literal pins, even when freshly committed.
    paths = set(git(ROOT, 'diff', '--name-only', proof.READY).splitlines())
    paths |= set(git(ROOT, 'ls-files', '--others', '--exclude-standard').splitlines())
    assert paths <= proof.GOVERNANCE_PATHS
    for path in paths:
        assert (ROOT / path).is_file() and not (ROOT / path).is_symlink(), path
        write(root, path, (ROOT / path).read_bytes())
    return root, commit(root, 'bounded034 implementation')

def composition(root, base, candidate):
    checkout(root, base)
    git(root, 'merge', '--no-commit', '--no-ff', candidate, check=False)
    conflicts = git(root, 'diff', '--name-only', '--diff-filter=U').splitlines()
    assert set(conflicts) <= proof.GOVERNANCE_PATHS
    # Every governance path uses the bounded source-free implementation. The
    # two critical production entries are taken only from immutable candidate.
    for path in proof.GOVERNANCE_PATHS:
        if path in proof._tree(root, base):
            write(root, path, proof.raw_bytes(root, base, path))
    return commit(root, 'exact candidate composition')

def phases(root, A):
    began = time.monotonic(); baseline = proof.authenticate(root)
    assert baseline['phase'] == 'BASELINE' and baseline['critical_paths'] == proof.predecessor.CRITICAL
    assert baseline['host_overlay_paths'] == proof.HOST_OVERLAYS
    print('PASS actual BASELINE, seconds', round(time.monotonic()-began, 3))
    before, after = proof.source_contract(root)
    M = composition(root, A, proof.C)
    F = commit(root, 'synthetic committed build identity only; no actual build', empty=True)
    candidate = proof.authenticate(root)
    assert candidate['phase'] == 'CANDIDATE_VALIDATION_ONLY'
    assert candidate['critical_paths'] == proof.predecessor.CRITICAL | proof.CRITICAL
    print('PASS actual CANDIDATE_VALIDATION_ONLY')
    checkout(root, A)
    digest = 'a' * 64; locator = f'local_backups/hardware-artifacts/{F}/{digest}/firmware.uf2'
    identities = dict(candidate_git_sha=F, candidate_base_configurator_sha=M,
                      firmware_artifact_build_path='.pio/build/glyph_mk6/firmware.uf2',
                      firmware_artifact_sha256=digest, preserved_firmware_artifact_locator=locator)
    alter_queue(root, 'GP-CONFIG-014', **identities, status='HARDWARE_TEST_REQUIRED',
                hardware_evidence_record=None, hardware_result=None, hardware_evidence_gaps=['Synthetic pending physical evidence'])
    protocol = '# SYNTHETIC TEST ONLY: no hardware observation or actual build\n'
    for key, value in (('Candidate Git SHA', F), ('Candidate tree', git(root, 'rev-parse', F+'^{tree}')),
                       ('Sole parent / authorized canonical base', M), ('UF2 SHA-256', digest), ('Preserved locator', locator)):
        protocol += f'- {key}: `{value}`\n'
    protocol += '- Fresh independent postimplementation review: PASS with no findings for the exact candidate, build output, custody bytes, correspondence, and protocol.\n'
    protocol += '\nSynthetic row names: ' + ', '.join(proof.REQUIRED_ROWS) + '\n'
    write(root, proof.PROTOCOL, protocol)
    R = commit(root, 'synthetic source-free R')
    evidence = json.loads(proof.raw_bytes(root, proof.B, proof.predecessor.EVIDENCE))
    state = proof.item(root, R, 'GP-CONFIG-014')
    evidence.update(work_order_id='GP-CONFIG-014', candidate_branch=state['branch'], **identities,
                    candidate_protocol_reference=proof.PROTOCOL, candidate_protocol_version=state['manual_acceptance_protocol_version'],
                    steps=[dict(id=row, instruction='Synthetic fixture instruction', expected='Synthetic fixture expectation',
                                observed='Synthetic fixture observation; no actual human evidence') for row in proof.REQUIRED_ROWS],
                    anomalies=[], evidence_gaps=[], result='PASS', tester='SYNTHETIC TEST ONLY', tested_at='2026-10-04T00:00:00Z')
    write(root, proof.EVIDENCE, json.dumps(evidence, indent=2)+'\n')
    write(root, proof.RESULT, '# SYNTHETIC TEST ONLY: no physical acceptance\n')
    alter_queue(root, 'GP-CONFIG-014', status='HARDWARE_VALIDATED', hardware_result='PASS',
                hardware_evidence_record='repo-json:'+proof.EVIDENCE, hardware_evidence_gaps=[], hardware_evidence_dependency_satisfied=True)
    E = commit(root, 'synthetic source-free E')
    processor = proof.authenticate(root)
    assert processor['phase'] == 'SOURCE_FREE_PROCESSOR' and processor['evidence_commit'] == E
    assert proof.catalog((root/proof.TRANSITIONS).read_bytes()) == []
    print('PASS actual SOURCE_FREE_PROCESSOR independently of integration catalog')
    I = composition(root, E, F)
    record = dict(work_order='GP-CONFIG-014', candidate=proof.C, build=F, parent=M,
                  tree=git(root,'rev-parse',F+'^{tree}'),review_commit=R,evidence_commit=E,integration=I)
    write(root, proof.TRANSITIONS, json.dumps(dict(schema_version=1, accepted_transitions=[record]),indent=2)+'\n')
    alter_queue(root, 'GP-CONFIG-014', status='DONE')
    J = commit(root, 'synthetic accepted catalog after actual integration')
    accepted = proof.authenticate(root)
    assert accepted['phase'] == 'ACCEPTED_TRANSITION'
    assert {F, M, R, E, I} <= accepted['object_roots']
    print('PASS actual ACCEPTED_TRANSITION after E and integration')
    return before, after, M, F, R, E, I, J

def negatives(root, A, before, after, F, E, I, J):
    checkout(root, A)
    path = next(iter(proof.CRITICAL)); original = (root/path).read_bytes()
    write(root,path,original+b'\n'); reject(lambda: proof.current_integrity(root,A,before),'critical live byte')
    git(root,'add','--',path); reject(lambda: proof.current_integrity(root,A,before),'critical staged byte')
    write(root,path,original); git(root,'add','--',path)
    (root/path).chmod(0o755); reject(lambda: proof.current_integrity(root,A,before),'critical live mode'); (root/path).chmod(0o644)
    git(root,'update-index','--assume-unchanged',path)
    reject(lambda: proof.current_integrity(root,A,before),'assume-unchanged critical'); git(root,'update-index','--no-assume-unchanged',path)
    git(root,'update-index','--skip-worktree',path)
    reject(lambda: proof.current_integrity(root,A,before),'skip-worktree critical'); git(root,'update-index','--no-skip-worktree',path)
    write(root,'src/synthetic-proof-ignored.cpp','bad\n'); (root/'.git/info/exclude').write_text('src/synthetic-proof-ignored.cpp\n')
    reject(lambda: proof.current_integrity(root,A,before),'ignored critical input'); (root/'src/synthetic-proof-ignored.cpp').unlink()
    for cached in ('.pio/build/glyph_mk6/synthetic-test.uf2','local_backups/synthetic-custody-test.json'):
        write(root,cached,'synthetic cache only; no proof authority\n')
    assert not proof.current_integrity(root,A,before)
    print('PASS existing ignored build/custody roots carry no proof authority')
    path = 'tools/check_glyph_gp_config014_modifier_capacity.py'; data=(root/path).read_bytes()
    write(root,path,data+b'\n'); K=commit(root,'one-byte freshly committed host substitution')
    reject(lambda: proof.authenticate_host_overlays(root,K),'freshly committed/index/live exact unauthorized checker')
    checkout(root,A); (root/path).unlink(); K=commit(root,'omitted host proof')
    reject(lambda: proof.authenticate_host_overlays(root,K),'omitted finite host overlay')
    checkout(root,A)
    raw=(root/proof.QUEUE).read_bytes(); alter_queue(root,'GP-CONFIG-020',hardware_result=None,status='REVIEW')
    commit(root,'erased020'); write(root,proof.QUEUE,raw); K=commit(root,'restored020')
    reject(lambda: proof.history(root,K,before,after),'historical020 erase/restore')
    checkout(root,A)
    data=(root/proof.predecessor.EVIDENCE).read_bytes();write(root,proof.predecessor.EVIDENCE,data+b'\n')
    commit(root,'changed020 evidence');write(root,proof.predecessor.EVIDENCE,data);K=commit(root,'restored020 evidence')
    reject(lambda: proof.history(root,K,before,after),'historical020 evidence substitution/restore')
    for status,result,label in [('REVIEW','PASS','PASS in REVIEW'),('HARDWARE_VALIDATED','PASS','DONE downgraded'),('DONE',None,'erased PASS')]:
        checkout(root,J);alter_queue(root,'GP-CONFIG-014',status=status,hardware_result=result);K=commit(root,label)
        reject(lambda: proof.history(root,K,before,after),label)
    checkout(root,J);write(root,proof.TRANSITIONS,json.dumps(dict(schema_version=1,accepted_transitions=[]))+'\n');K=commit(root,'removedcatalog')
    reject(lambda: proof.history(root,K,before,after),'accepted catalog removal')
    checkout(root,E)
    ev=json.loads((root/proof.EVIDENCE).read_bytes()); ev['steps']=ev['steps'][:-1]
    write(root,proof.EVIDENCE,json.dumps(ev,indent=2)+'\n');K=commit(root,'missingphysicalrow')
    reject(lambda: proof.processor_record(root,K,before,after),'missing required014 physical row')
    checkout(root,A);ev=proof.catalog(proof.raw_bytes(root,J,proof.TRANSITIONS))
    write(root,proof.TRANSITIONS,json.dumps(dict(schema_version=1,accepted_transitions=ev))+'\n');K=commit(root,'prematurecatalog')
    reject(lambda: proof.history(root,K,before,after),'catalog before processor E')
    checkout(root,J);changed=proof.catalog((root/proof.TRANSITIONS).read_bytes());changed[0]['evidence_commit']=I
    write(root,proof.TRANSITIONS,json.dumps(dict(schema_version=1,accepted_transitions=changed))+'\n');K=commit(root,'catalogtuple')
    reject(lambda: proof.history(root,K,before,after),'replaced earliest E tuple')
    checkout(root,J)
    print('PASS historical pin API')
    for p in ('tools/check_glyph_custom_modifier_cache_characterization.py','tools/check_glyph_setconfig_runtime_rebinding_characterization.py'):
        raw=proof.raw_bytes(root,proof.B,p);blob=proof._tree(root,proof.B)[p][2]
        assert proof.verify_historical_dependency(root,p,blob,proof.sha(raw))==raw


def main():
    with tempfile.TemporaryDirectory(prefix='glyph-c014-transition-tests-') as directory:
        root,A=new_repository(directory)
        before,after,M,F,R,E,I,J=phases(root,A)
        negatives(root,A,before,after,F,E,I,J)
    print('PASS GP-VAL-034 finite native source/phase/history negative corpus')

if __name__=='__main__': main()
