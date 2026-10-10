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
from unittest.mock import patch
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
    # Authenticate the actual current phase before making synthetic fixtures.
    # The real repository's source, index and acceptance metadata remain intact.
    current = proof.authenticate(ROOT)
    current_critical = proof.critical_tree(ROOT, current['target'])
    root = Path(directory).resolve()
    subprocess.run(['git', '-c', 'init.templateDir=', 'init', '-q', str(root)], check=True)
    objects = Path(git(ROOT, 'rev-parse', '--git-path', 'objects'))
    if not objects.is_absolute(): objects = ROOT / objects
    (root / '.git/info').mkdir(exist_ok=True)
    (root / '.git/objects/info/alternates').write_text(str(objects.resolve()) + '\n')
    git(root, 'config', 'user.name', 'Synthetic proof test')
    git(root, 'config', 'user.email', 'synthetic-proof@example.invalid')
    # The041 adoption already has exact KBD ancestry. Keep it when rebuilding
    # a current fixture; never copy immutable hosts onto a root lacking ancestry.
    checkout(root, proof.CONFIG019_ADOPTION)
    if proof.ancestor(ROOT, proof.CONFIG019_C, current['target']):
        composition(root, proof.CONFIG019_ADOPTION, proof.CONFIG019_C)
    # A finite draft composition. Never copies caches, objects, ignored files or
    # arbitrary current repository contents. A checker substitution is rejected
    # below against independent literal pins, even when freshly committed.
    paths = set(git(ROOT, 'diff', '--name-only', proof.READY).splitlines())
    paths |= set(git(ROOT, 'ls-files', '--others', '--exclude-standard').splitlines())
    assert paths <= proof.GOVERNANCE_PATHS | proof.CRITICAL | proof.VAL045_PATHS
    critical = paths & proof.CRITICAL
    if critical:
        assert critical == proof.CRITICAL
        assert current['phase'] in {'CANDIDATE_VALIDATION_ONLY', 'ACCEPTED_TRANSITION'}
        assert current_critical == proof.critical_tree(ROOT, proof.C)
    # Only the authenticated exact014 source is omitted. The synthetic fixture
    # starts at READY's accepted020 source, then composes immutable C itself.
    paths -= proof.CRITICAL | {proof.PROTOCOL, proof.EVIDENCE, proof.RESULT}
    for path in paths:
        assert (ROOT / path).is_file() and not (ROOT / path).is_symlink(), path
        write(root, path, (ROOT / path).read_bytes())
    # Preserve every other current queue item and governance byte. Replace only
    # the014 entry so actual F/PASS data cannot seed a synthetic baseline proof.
    text = (root / proof.QUEUE).read_text()
    begin, end = '<!-- queue-state:start -->', '<!-- queue-state:end -->'
    left, tail = text.split(begin, 1); block, right = tail.split(end, 1)
    data = proof.parsed_queue(text.encode())
    slots = [i for i, value in enumerate(data['items']) if value['id'] == 'GP-CONFIG-014']
    assert len(slots) == 1
    data['items'][slots[0]] = proof.item(ROOT, proof.READY, 'GP-CONFIG-014')
    write(root, proof.QUEUE, left + begin + '\n```json\n' + json.dumps(data, indent=2) + '\n```\n' + end + right)
    write(root, proof.TRANSITIONS, json.dumps(dict(schema_version=1, accepted_transitions=[]), indent=2) + '\n')
    # The adopted root contains the real pending014 protocol. Remove only these
    # synthetic014 evidence slots along with replacing its queue entry above;
    # the actual ROOT and all other evidence remain untouched.
    for path in (proof.PROTOCOL, proof.EVIDENCE, proof.RESULT):
        if (root / path).exists(): (root / path).unlink()
    assert not any((root / path).exists() for path in (proof.PROTOCOL, proof.EVIDENCE, proof.RESULT))
    print('PASS authenticated current', current['phase'], 'before isolated READY reconstruction')
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
    return commit(root, 'exact candidate composition', empty=True)

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



def kbd_coexistence(root, A):
    # Exact known objects come from the finite proof closure and local alternates.
    git(root,'cat-file','-e',proof.KBD_C+'^{commit}')
    K = composition(root,A,proof.KBD_C)
    context = proof.authenticate(root)
    assert context['phase'] == 'BASELINE' and context['kbd_host_paths'] == proof.KBD_HOSTS
    assert {proof.KBD_C,proof.KBD_B,proof.KBD_AUTHORITY} <= context['object_roots']
    print('PASS source-free034 plus exact preserved KBD composition, 28 dependencies unchanged')
    T = composition(root,K,proof.C)
    context = proof.authenticate(root)
    assert context['phase'] == 'CANDIDATE_VALIDATION_ONLY' and context['kbd_host_paths'] == proof.KBD_HOSTS
    assert proof.critical_tree(root,T) == proof.critical_tree(root,proof.C)
    print('PASS exact014 plus preserved KBD composition, complete critical equality')
    path='tools/check_glyph_gp_kbd_001_keyboard_pipeline.py'
    raw=(root/path).read_bytes()
    write(root,path,raw+b'\n')
    reject(lambda:proof.authenticate_kbd_coexistence(root,T),'KBD live host substitution')
    git(root,'add','--',path)
    write(root,path,raw)
    reject(lambda:proof.authenticate_kbd_coexistence(root,T),'KBD index host substitution')
    git(root,'add','--',path)
    write(root,path,raw+b'\n');N=commit(root,'KBD newly committed host alteration')
    reject(lambda:proof.authenticate_kbd_coexistence(root,N),'KBD newly committed/index/live altered host')
    checkout(root,T);(root/path).unlink();N=commit(root,'KBD omitted required host')
    reject(lambda:proof.authenticate_kbd_coexistence(root,N),'KBD missing finite host')
    checkout(root,T);(root/path).chmod(0o755);N=commit(root,'KBD executable host')
    reject(lambda:proof.authenticate_kbd_coexistence(root,N),'KBD100755 host')
    checkout(root,T);(root/path).unlink();(root/path).symlink_to('check_glyph_gp_config014_modifier_capacity.py')
    N=commit(root,'KBD symlink host')
    reject(lambda:proof.authenticate_kbd_coexistence(root,N),'KBD120000 host')
    checkout(root,T);dep='src/core/InputMode.cpp';write(root,dep,(root/dep).read_bytes()+b'\n');N=commit(root,'KBD dependency source alteration')
    reject(lambda:proof.authenticate(root),'KBD source drift retains critical precedence')
    reject(lambda:proof.authenticate_kbd_coexistence(root,N),'KBD literal dependency source alteration')
    checkout(root,T);unknown='tools/fixtures/gp_kbd_001_keyboard_pipeline/include/TUKeyboard.hpp.bak';write(root,unknown,'unknown adjacent host\n')
    N=commit(root,'KBD adjacent unknown host')
    reject(lambda:proof.authenticate(root),'KBD unknown adjacent path')
    checkout(root,proof.KBD_C)
    alter_queue(root,'GP-CONFIG-020',status='REVIEW')
    bad = commit(root,'nonliteral old KBD sidebranch queue alteration')
    N = composition(root,A,bad)
    reject(lambda:proof.authenticate(root),'nonliteral old sidebranch receives no history exemption')
    checkout(root,A)


def main():
    began = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='glyph-c014-transition-tests-') as directory:
        root,A=new_repository(directory)
        before,after,M,F,R,E,I,J=phases(root,A)
        negatives(root,A,before,after,F,E,I,J)
        kbd_coexistence(root,A)
    print('PASS GP-VAL-034 finite native source/phase/history negative corpus; seconds',round(time.monotonic()-began,3))

# The original matrix is retained in the original group below.


def config019_positive(root, A):
    assert proof.authenticate_config019_contract(root) == proof.CONFIG019_HOSTS
    assert proof.authenticate_config019_coexistence(root, A) == frozenset()
    assert not any((root / p).exists() for p in proof.CONFIG019_ORIGINAL_HOSTS)
    K = composition(root, A, proof.CONFIG019_C)
    observed = proof.authenticate(root)
    assert observed['phase'] == 'BASELINE' and observed['config019_host_paths'] == proof.CONFIG019_HOSTS
    assert {proof.CONFIG019_C, proof.CONFIG019_B, proof.CONFIG019_ADOPTION,
            proof.CONFIG019_RECEIPT_COMMIT, proof.CONFIG019_F020} <= observed['object_roots']
    print('PASS exact019 composition, immutable32/12 and independently pinned current34 proof')
    return K


def config019_hosts(root, A):
    K = config019_positive(root, A)
    for path in sorted(proof.CONFIG019_ORIGINAL_HOSTS):
        checkout(root, K); raw = (root / path).read_bytes()
        write(root, path, raw + b'\n')
        reject(lambda: proof.authenticate_config019_coexistence(root, K), '019 original live substitution ' + path)
        git(root, 'add', '--', path); write(root, path, raw)
        reject(lambda: proof.authenticate_config019_coexistence(root, K), '019 original index substitution ' + path)
        write(root, path, raw + b'\n'); N = commit(root, '019 committed original substitution')
        reject(lambda: proof.authenticate_config019_coexistence(root, N), '019 original committed substitution ' + path)
        checkout(root, K); (root / path).unlink(); N = commit(root, '019 omitted original')
        reject(lambda: proof.authenticate_config019_coexistence(root, N), '019 omitted original ' + path)
    checkout(root, K)
    for path in proof.CONFIG019_ORIGINAL_HOSTS: (root / path).unlink()
    N = commit(root, '019 all original hosts deleted')
    reject(lambda: proof.authenticate_config019_coexistence(root, N), '019 complete deletion cannot erase ancestry obligation')
    checkout(root, A)
    for path in proof.CONFIG019_ORIGINAL_HOSTS: write(root, path, proof.raw_bytes(root, proof.CONFIG019_C, path))
    N = commit(root, '019 copied original hosts without exact candidate ancestry')
    reject(lambda: proof.authenticate_config019_coexistence(root, N), '019 copied hosts are not integration')
    checkout(root, K)
    path = sorted(proof.CONFIG019_ORIGINAL_HOSTS)[0]
    for kind in ('executable', 'symlink', 'gitlink', 'rename'):
        checkout(root, K)
        if kind == 'executable': (root / path).chmod(0o755)
        elif kind == 'symlink': (root / path).unlink(); (root / path).symlink_to('missing-host')
        elif kind == 'rename': (root / path).rename(root / (path + '.bak'))
        else:
            git(root, 'update-index', '--add', '--cacheinfo', '160000,' + proof.CONFIG019_C + ',' + path)
            git(root, 'commit', '-q', '-m', 'SYNTHETIC PROOF TEST:019 gitlink')
        N = git(root, 'rev-parse', 'HEAD') if kind == 'gitlink' else commit(root, '019 unsafe type or rename')
        reject(lambda: proof.authenticate_config019_coexistence(root, N), '019 original ' + kind)
    for path in ('docs/calibration/gp_config_019_usb_name_selection_characterization.md.bak',
                 'docs/calibration/GP_CONFIG_019_usb_name_selection_characterization.md',
                 'tools/fixtures/gp_config019_usb_name_selection/unknown.cpp'):
        checkout(root, K)
        # Removing a duplicate case-alias index entry during checkout can also
        # remove the canonical working file on a case-insensitive filesystem.
        # Restore only these exact known hosts, then prove the baseline before
        # testing the next unknown path; a missing host must not fake rejection.
        for original in proof.CONFIG019_ORIGINAL_HOSTS:
            if (root / original).exists() or (root / original).is_symlink(): (root / original).unlink()
            write(root, original, proof.raw_bytes(root, K, original))
        assert proof.authenticate(root)['config019_host_paths'] == proof.CONFIG019_HOSTS
        if 'GP_CONFIG_019' in path:
            # Construct a real case-alias tree entry even on case-insensitive
            # filesystems; do not merely overwrite the canonical file bytes.
            source = 'docs/calibration/gp_config_019_usb_name_selection_characterization.md'
            blob = proof.CONFIG019_HOST_PINS[source]['blob']
            git(root, 'update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + path)
            git(root, 'commit', '-q', '-m', 'SYNTHETIC PROOF TEST:019 actual case-alias entry')
            N = git(root, 'rev-parse', 'HEAD')
            assert path in proof._tree(root, N)
        else:
            write(root, path, 'unknown finite host lookalike\n'); N = commit(root, '019 unknown adjacent/alias')
        reject(lambda: proof.authenticate(root), '019 unknown/adjacent/case alias ' + path)
    checkout(root, A)


def config019_overlays(root, A):
    for path in sorted(proof.CONFIG019_OVERLAY_PATHS):
        checkout(root, A); raw = (root / path).read_bytes()
        write(root, path, raw + b'\n')
        reject(lambda: proof.authenticate_config019_coexistence(root, A), '041 overlay live substitution ' + path)
        git(root, 'add', '--', path); write(root, path, raw)
        reject(lambda: proof.authenticate_config019_coexistence(root, A), '041 overlay index substitution ' + path)
        write(root, path, raw + b'\n'); N = commit(root, '041 committed overlay substitution')
        reject(lambda: proof.authenticate_config019_coexistence(root, N), '041 newly committed overlay substitution ' + path)
        checkout(root, A); (root / path).unlink(); N = commit(root, '041 omitted overlay')
        reject(lambda: proof.authenticate_config019_coexistence(root, N), '041 omitted overlay ' + path)
    checkout(root, A)
    for path in proof.CONFIG019_OVERLAY_PATHS: (root / path).unlink()
    N = commit(root, '041 complete overlay deletion after introduction')
    reject(lambda: proof.authenticate_config019_coexistence(root, N), '041 total deletion does not revive historical route')
    for kind in ('executable', 'symlink', 'gitlink'):
        checkout(root, A); path = proof.CONFIG019_CHECKER
        if kind == 'executable': (root / path).chmod(0o755)
        elif kind == 'symlink': (root / path).unlink(); (root / path).symlink_to('missing-current-checker')
        else:
            git(root, 'update-index', '--add', '--cacheinfo', '160000,' + proof.CONFIG019_C + ',' + path)
            git(root, 'commit', '-q', '-m', 'SYNTHETIC PROOF TEST:041 overlay gitlink')
        N = git(root, 'rev-parse', 'HEAD') if kind == 'gitlink' else commit(root, '041 unsafe current overlay type')
        reject(lambda: proof.authenticate_config019_coexistence(root, N), '041 current overlay ' + kind)
    checkout(root, A)
    for flag, undo in (('--assume-unchanged', '--no-assume-unchanged'), ('--skip-worktree', '--no-skip-worktree')):
        path = proof.CONFIG019_CHECKER; git(root, 'update-index', flag, path)
        reject(lambda: proof.authenticate_config019_coexistence(root, A), '041 overlay index flag trap ' + flag)
        git(root, 'update-index', undo, path)
    # False current acceptance cannot become an authenticated fixture, even in a
    # clean new commit with a forged PASS row and no other source changes.
    path = 'docs/runtime_config/fixtures/gp_val041_usb_name_current_acceptance.json'
    forged = json.loads((root / path).read_text()); forged['current_fragments']['acceptance'] = '0' * 64
    forged['current_expected_rows'][-1] = 'current_result PASS no controls executed'
    write(root, path, json.dumps(forged, indent=2) + '\n'); N = commit(root, '041 forged current acceptance')
    reject(lambda: proof.authenticate_config019_coexistence(root, N), '041 false acceptance fragment/observations')
    checkout(root, A)


def config019_authority(root, A):
    assert proof.authenticate_config019_coexistence(root, A) == frozenset()
    for path in proof.CONFIG019_AUTHORITY_PINS:
        checkout(root, A); raw = (root / path).read_bytes(); write(root, path, raw + b'\n')
        reject(lambda: proof.authenticate_config019_coexistence(root, A), '041 authorization live substitution ' + path)
        N = commit(root, '041 committed authorization substitution')
        reject(lambda: proof.authenticate_config019_coexistence(root, N), '041 authorization committed substitution ' + path)
    checkout(root, A)
    path = 'docs/runtime_config/fixtures/runtime_config_validation_manifest.json'
    for change in ('omit', 'command', 'source', 'roots'):
        checkout(root, A); manifest = json.loads((root / path).read_text())
        entries = [e for e in manifest['entries'] if e['id'] == 'gp_config019_usb_name_selection']
        assert len(entries) == 1
        if change == 'omit': manifest['entries'].remove(entries[0])
        elif change == 'command': entries[0]['command'] = ['python3', proof.CONFIG019_CHECKER, '--route', 'historical']
        elif change == 'source': entries[0]['source_dependencies'].remove('src/core/config_button_validation.cpp')
        else: entries[0]['path'] = 'tools/fake-config019.py'
        write(root, path, json.dumps(manifest, indent=2) + '\n'); N = commit(root, '041 manifest omission/substitution')
        reject(lambda: proof.authenticate_config019_coexistence(root, N), '041 manifest ' + change)
    checkout(root, A)
    # Mutable tables cannot invent a different original authority/source fact.
    for name, value in (('CONFIG019_C', proof.KBD_C), ('CONFIG019_B', proof.B),
                        ('CONFIG019_TREE', '0' * 40), ('CONFIG019_RAW', '0' * 64),
                        ('CONFIG019_RECEIPT_COMMIT', '0' * 40), ('CONFIG019_ADOPTION', proof.READY),
                        ('CONFIG019_F020', proof.CONFIG019_C)):
        with patch.object(proof, name, value):
            reject(lambda: proof.authenticate_config019_contract(root), '041 wrong/missing literal root ' + name)
    pins = {p: dict(v) for p, v in proof.CONFIG019_HOST_PINS.items()}
    pins[proof.CONFIG019_CHECKER]['sha256'] = '0' * 64
    with patch.object(proof, 'CONFIG019_HOST_PINS', pins):
        reject(lambda: proof.authenticate_config019_contract(root), '019 tampered candidate pin cannot reseal authority')
    pins = {p: dict(v) for p, v in proof.CONFIG019_CURRENT_SOURCE_PINS.items()}
    pins['HAL/pico/src/comms/ConfiguratorBackend.cpp'] = proof.CONFIG019_DEPENDENCY_PINS['HAL/pico/src/comms/ConfiguratorBackend.cpp']
    with patch.object(proof, 'CONFIG019_CURRENT_SOURCE_PINS', pins):
        reject(lambda: proof.authenticate_config019_contract(root), '019 historical acceptance is not current accepted proof')
    with patch.object(proof, 'CONFIG019_FRAGMENT_PINS', dict(proof.CONFIG019_FRAGMENT_PINS, acceptance='0' * 64)):
        reject(lambda: proof.authenticate_config019_contract(root), '019 historical fragment table cannot reseal evidence')
    checkout(root, A)


def config019_history(root, A):
    K = config019_positive(root, A)
    before, after = proof.source_contract(root)
    proof.history(root, K, before, after)
    # Only the actual C gets a historical qualification. A descendant changing
    # accepted020, followed by restoration at merge, must still fail history.
    checkout(root, proof.CONFIG019_C)
    alter_queue(root, 'GP-CONFIG-020', status='REVIEW', hardware_result=None)
    bad = commit(root, 'nonliteral019 historical sidebranch accepted020 mutation')
    N = composition(root, A, bad)
    reject(lambda: proof.history(root, N, before, after), '019 arbitrary old descendant gets no history skip')
    checkout(root, proof.CONFIG019_B)
    for path in proof.CONFIG019_HOSTS: write(root, path, proof.raw_bytes(root, proof.CONFIG019_C, path))
    replay = commit(root, '019 replay of identical host tree with different candidate identity')
    assert replay != proof.CONFIG019_C
    N = composition(root, A, replay)
    reject(lambda: proof.authenticate_config019_coexistence(root, N), '019 replay/rebase is not exact candidate ancestry')
    checkout(root, A)


def config019_critical(root, A):
    for path in ('HAL/pico/src/comms/ConfiguratorBackend.cpp', 'src/core/config_button_validation.cpp'):
        checkout(root, A); raw = (root / path).read_bytes(); write(root, path, raw + b'\n')
        reject(lambda: proof.authenticate_config019_coexistence(root, A), '019 live accepted source substitution ' + path)
        git(root, 'add', '--', path); write(root, path, raw)
        reject(lambda: proof.authenticate_config019_coexistence(root, A), '019 index accepted source substitution ' + path)
        write(root, path, raw + b'\n'); N = commit(root, '019 source substitution')
        reject(lambda: proof.authenticate(root), '019 committed source retains critical precedence ' + path)
    checkout(root, A)
    K = config019_positive(root, A); T = composition(root, K, proof.C)
    observed = proof.authenticate(root)
    assert observed['phase'] == 'CANDIDATE_VALIDATION_ONLY' and observed['config019_host_paths'] == proof.CONFIG019_HOSTS
    checker = root / proof.CONFIG019_CHECKER
    def named_checker():
        result = subprocess.run(['python3', '-B', str(checker), '--route', 'current'], cwd=root,
                                capture_output=True, text=True, timeout=120)
        if result.returncode: raise AssertionError(result.stdout + result.stderr)
        return result.stdout
    print('PASS current019 real decoder/validator/acceptance on exact authenticated014 candidate:', named_checker().splitlines()[-1])
    for path in sorted(proof.CRITICAL | {'src/core/InputMode.cpp'}):
        checkout(root, T); write(root, path, (root / path).read_bytes() + b'\n'); N = commit(root, '019 rejects near014/third-critical source')
        reject(named_checker, '019 current checker rejects one-byte014/third-critical ' + path)
    checkout(root, A)


def original034_historical(root):
    checkout(root, '62b559ae5ee2d6dee0ff54aeb56b2653d86253c6')
    context = proof.authenticate(root)
    assert context['phase'] == 'BASELINE' and context['config019_host_paths'] == frozenset()
    print('PASS original034 historical committed baseline without future019 overlay')


def val045_handoff_state():
    expected_hardware_paths = frozenset((
        'docs/agent_framework/GP_CONFIG_024_HARDWARE_PROTOCOL.md',
        'docs/calibration/gp_config_024_hardware_result.md',
        'docs/calibration/fixtures/gp_config_024_hardware_evidence.json',
    ))
    assert proof.C024_HARDWARE_HANDOFF_PATHS == expected_hardware_paths
    assert proof.C024_HARDWARE_HANDOFF_PATHS.isdisjoint(proof.C024_CANDIDATE_PATHS)
    assert proof.C024_HARDWARE_HANDOFF_PATHS.isdisjoint(proof.VAL045_PATHS)
    candidate = {
        'candidate_git_sha': proof.C024_C,
        'candidate_base_configurator_sha': proof.C024_B,
        'status': 'PREAUTHORIZED',
        'activation_state': 'WAITING',
    }
    waiting = {
        'status': 'PREAUTHORIZED',
        'activation_state': 'ACTIVATABLE',
        'activation_requires_new_judgment': False,
    }
    proof.validate_val045_handoff_state(candidate, waiting)

    def reject(c024, val045, label):
        try:
            proof.validate_val045_handoff_state(c024, val045)
        except Exception:
            return
        raise AssertionError('false acceptance: ' + label)

    prematurely_activated = dict(candidate, activation_state='ACTIVATABLE')
    reject(prematurely_activated, waiting, 'C024 activated before VAL045 DONE')
    completed = dict(waiting, status='DONE', activation_state='NOT_APPLICABLE')
    activated = dict(
        candidate,
        activation_state='ACTIVATABLE',
        hardware_evidence_dependency_satisfied=True,
    )
    proof.validate_val045_handoff_state(activated, completed)
    hardware_wait = dict(
        activated,
        activation_state='HARDWARE_PENDING',
        hardware_evidence_dependency_satisfied=False,
        firmware_artifact_build_path='.pio/build/glyph_mk6/firmware.uf2',
        firmware_artifact_sha256='95de108f23b0d7219caa38a1f85c4dec1691f087061b29787d07b83dab0ba0e6',
        preserved_firmware_artifact_locator=(
            'local_backups/hardware-artifacts/' + proof.C024_C + '/'
            '95de108f23b0d7219caa38a1f85c4dec1691f087061b29787d07b83dab0ba0e6/firmware.uf2'),
        hardware_result=None,
    )
    proof.validate_val045_handoff_state(hardware_wait, completed)
    reject(candidate, completed, 'C024 stayed waiting after strict VAL045 DONE')
    wrong_candidate = dict(activated, candidate_git_sha='0' * 40)
    reject(wrong_candidate, completed, 'candidate identity substituted at resume')
    wrong_artifact = dict(hardware_wait, firmware_artifact_sha256='0' * 64)
    reject(wrong_artifact, completed, 'C024 artifact substituted at hardware wait')
    print('PASS VAL045 strict DONE gates exact preserved C024 activation and hardware wait')


def run_group(group):
    began = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='glyph-c014-transition-tests-') as directory:
        root, A = new_repository(directory)
        if group in ('original', 'original-phases', 'original-negatives', 'original-kbd'):
            original034_historical(root); checkout(root, A)
            if group != 'original-kbd':
                before, after, M, F, R, E, I, J = phases(root, A)
                if group in ('original', 'original-negatives'):
                    negatives(root, A, before, after, F, E, I, J)
            if group in ('original', 'original-kbd'): kbd_coexistence(root, A)
        else:
            globals()['config019_' + group](root, A)
    print('PASS finite native034/041 group', group, 'seconds', round(time.monotonic() - began, 3))



def c024_processor_evidence():
    """Real committed E plus isolated malformed descendants; no physical tests."""
    import copy
    import os
    os.environ['GIT_OPTIONAL_LOCKS'] = '0'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    current = proof.authenticate(ROOT)
    assert current['phase'] == 'SOURCE_FREE_PROCESSOR'
    assert current['accepted_metadata_paths'] == frozenset((
        proof.C024_EVIDENCE, proof.C024_RESULT, proof.C024_ARCHIVE))
    assert proof.authenticate_c024_phase(ROOT, proof.C024_R)['accepted_metadata_paths'] == frozenset()
    from glyph_hardware_correspondence import classify_path
    for path in (*proof.C024_HARDWARE_HANDOFF_PATHS, proof.C024_ARCHIVE):
        assert classify_path(path) == 'NON_BEHAVIORAL'
    assert classify_path(proof.C024_MENU) == 'CRITICAL'
    reject(lambda: classify_path('docs/calibration/fixtures/gp_config_024_unreviewed_neighbor.json'),
           'unreviewed neighboring evidence path')
    evidence = json.loads(proof.original.raw_bytes(ROOT, current['target'], proof.C024_EVIDENCE))
    proof.validate_c024_processor_rows(evidence)
    count = 1
    for label, mutate in (
        ('erased freeze', lambda d: d.update(anomalies=[])),
        ('invented freeze fix', lambda d: d.update(anomalies=['fixed'])),
        ('required row omission', lambda d: d['steps'].pop(0)),
        ('failed required row', lambda d: d['steps'][0].update(observed='FAIL')),
        ('invented Keyboard PASS', lambda d: d['steps'][2].update(observed='PASS')),
        ('rollback claimed without test', lambda d: d['steps'][5].update(observed='PASS')),
        ('required evidence gap', lambda d: d.update(evidence_gaps=['missing physical witness'])),
    ):
        malformed = copy.deepcopy(evidence); mutate(malformed)
        reject(lambda: proof.validate_c024_processor_rows(malformed), label); count += 1
    with tempfile.TemporaryDirectory(prefix='glyph-c024-processor-negatives-') as directory:
        root = Path(directory)
        subprocess.run(['git', '-c', 'init.templateDir=', 'init', '-q', str(root)], check=True)
        common = Path(git(ROOT, 'rev-parse', '--git-common-dir'))
        if not common.is_absolute(): common = ROOT / common
        (root / '.git/objects/info/alternates').write_text(str(common.resolve() / 'objects') + '\n')
        git(root, 'config', 'user.name', 'Synthetic evidence test')
        git(root, 'config', 'user.email', 'synthetic-evidence@example.invalid')
        E = current['target']; checkout(root, E)
        write(root,'docs/AGENT_CONTEXT.md',(root/'docs/AGENT_CONTEXT.md').read_bytes()+b'\n')
        commit(root,'source-free evidence descendant')
        descendant = proof.authenticate(root)
        assert descendant['phase'] == 'SOURCE_FREE_PROCESSOR'
        assert descendant['processor_evidence_commit'] == current['processor_evidence_commit']
        checkout(root,E)
        def bad(label, mutate):
            nonlocal count
            checkout(root, E); mutate(); commit(root, label)
            reject(lambda: proof.authenticate(root), label); count += 1
        def edit_json(path, mutate):
            value=json.loads((root/path).read_text());mutate(value)
            write(root,path,json.dumps(value,indent=2)+'\n')
        def edit_order(**values): alter_queue(root, 'GP-CONFIG-024', **values)
        bad('tested UF2 substitution', lambda: edit_order(firmware_artifact_sha256='0'*64))
        bad('candidate substitution', lambda: edit_order(candidate_git_sha='0'*40))
        bad('source-free early DONE', lambda: edit_order(status='DONE'))
        bad('freeze erased in committed evidence', lambda: edit_json(proof.C024_EVIDENCE,lambda d:d.update(anomalies=[])))
        bad('owner/session archive substitution', lambda: write(root,proof.C024_ARCHIVE,(root/proof.C024_ARCHIVE).read_bytes()+b' '))
        bad('original protocol mutation', lambda: write(root,proof.C024_PROTOCOL,(root/proof.C024_PROTOCOL).read_bytes()+b' '))
        bad('candidate source copied at E',lambda:write(root,proof.C024_MENU,proof.original.raw_bytes(ROOT,proof.C024_C,proof.C024_MENU)))
        bad('early I catalog',lambda:write(root,'docs/runtime_config/fixtures/gp_val045_accepted_transitions.json','{}\n'))
        bad('other order mutation',lambda:alter_queue(root,'GP-CONFIG-023',title='substituted'))
        def mode(): (root/proof.C024_ARCHIVE).chmod(0o755)
        bad('executable evidence archive',mode)
        checkout(root,E)
        write(root,proof.C024_EVIDENCE,(root/proof.C024_EVIDENCE).read_bytes()+b' ')
        reject(lambda:proof.authenticate(root),'live evidence divergence');count+=1
        git(root,'add',proof.C024_EVIDENCE)
        write(root,proof.C024_EVIDENCE,proof.original.raw_bytes(ROOT,E,proof.C024_EVIDENCE))
        reject(lambda:proof.authenticate(root),'index-only evidence divergence');count+=1
        git(root,'add',proof.C024_EVIDENCE)
        assert git(root,'status','--porcelain') == ''
        checkout(root,E)
        edit_order(hardware_result='FAIL');invalid=commit(root,'historical invalid acceptance')
        write(root,proof.QUEUE,proof.original.raw_bytes(ROOT,E,proof.QUEUE));commit(root,'later restoration cannot conceal invalid history')
        reject(lambda:proof.authenticate(root),'hidden historical invalid acceptance');count+=1
        checkout(root,E)
        tree=git(root,'write-tree')
        merged=subprocess.run(['git','-C',str(root),'commit-tree',tree,'-p',E,'-p',proof.C024_C],input=b'SYNTHETIC TEST early tested ancestry\n',capture_output=True,check=True).stdout.decode().strip()
        checkout(root,merged)
        reject(lambda:proof.authenticate(root),'tested ancestry hidden behind baseline critical tree');count+=1
    print('PASS C024 processor real E and',count-1,'negative controls; unresolved anomaly retained; no I/DONE')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    groups = ('original', 'hosts', 'overlays', 'authority', 'history', 'critical')
    parser.add_argument('--group', choices=('all', *groups, 'original-phases', 'original-negatives', 'original-kbd', 'val045-handoff-state', 'c024-processor-evidence'), default='all')
    selected = parser.parse_args().group
    if selected == 'c024-processor-evidence':
        c024_processor_evidence()
    elif selected == 'val045-handoff-state':
        val045_handoff_state()
    else:
        for group in groups if selected == 'all' else (selected,): run_group(group)
