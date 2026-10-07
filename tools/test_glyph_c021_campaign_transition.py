#!/usr/bin/env python3
"""Actual finite038 admission, index/live/history and catalog rejectors.

Disposable Git snapshots are synthetic validation inputs, never hardware evidence.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import time
import glyph_c021_campaign_transition as proof
from glyph_hardware_correspondence import CorrespondenceError, classify_path

ROOT = Path(__file__).resolve().parents[1]


def git(root, *args, data=None, env=None):
    done = subprocess.run(['git', *args], cwd=root, input=data, capture_output=True, timeout=90, env=env)
    if done.returncode:
        raise AssertionError(done.stderr.decode(errors='replace'))
    return done.stdout


def rejected(fn, label, observations):
    try:
        fn()
    except (CorrespondenceError, ValueError, TypeError, KeyError, AssertionError) as exc:
        observations.append({'label': label, 'status': 'REJECTED', 'exception': str(exc)})
        return
    raise AssertionError('038 accepted invalid input: ' + label)


def snapshot(parent, pack, head):
    root = parent / 'repository'; root.mkdir()
    git(root, 'init', '-q')
    git(root, 'index-pack', '--stdin', data=pack)
    git(root, 'update-ref', 'refs/heads/synthetic038', head)
    git(root, 'symbolic-ref', 'HEAD', 'refs/heads/synthetic038')
    git(root, 'checkout', '-q', 'synthetic038')
    git(root, 'config', 'user.name', 'Synthetic validation')
    git(root, 'config', 'user.email', 'synthetic-validation@invalid')
    git(root, 'config', 'core.autocrlf', 'false')
    git(root, 'update-ref', 'refs/heads/configurator', proof.READY)
    return root


def commit(root, message):
    git(root, 'add', '-A')
    return git(root, 'commit', '-q', '-m', message)


def rewrite_queue(root, order, updates):
    file = root / proof.QUEUE
    text = file.read_text()
    marker, end = '<!-- queue-state:start -->', '<!-- queue-state:end -->'
    document = proof.stateutil.parsed_queue(text.encode())
    row = next(item for item in document['items'] if item['id'] == order)
    row.update(updates)
    prefix, rest = text.split(marker)
    _, suffix = rest.split(end)
    file.write_text(prefix + marker + '\n```json\n' + json.dumps(document, indent=2) + '\n```\n' + end + suffix)
    return row


def phase_controls(root, head, before, after, observations):
    """Build a disposable graph with synthetic-only rows; never build firmware."""
    changed = sorted(git(root, 'diff', '--name-only', proof.READY, head).decode().splitlines())
    evidence = {
        'schema_name':'glyph_done_completion_evidence', 'schema_version':1,
        'mode':'DIRECT_ANCESTRY', 'implementation_base_sha':proof.READY,
        'reviewed_implementation_sha':head, 'prior_canonical_integration_sha':head,
        'reviewed_changed_paths':changed,
        'independent_review_provenance':'SYNTHETIC VALIDATION INPUT ONLY; no actual review or acceptance.',
        'validation_provenance':'SYNTHETIC VALIDATION INPUT ONLY; no build or hardware test.'}
    rewrite_queue(root, 'GP-VAL-038', {'status':'DONE', 'done_evidence':evidence})
    commit(root, 'Synthetic-only strict governance completion')
    D = git(root, 'rev-parse', 'HEAD').decode().strip()
    assert proof.authenticate(root)['phase'] == 'BASELINE'
    for path in proof.CRITICAL:
        mode, _, identity = after[path]
        file = root / path; file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(proof.raw_bytes(root, proof.C, path)); file.chmod(0o644)
        git(root, 'update-index', '--add', '--cacheinfo', mode, identity, path)
    tree = git(root, 'write-tree').decode().strip()
    M = git(root, 'commit-tree', tree, '-p', D, '-p', proof.C, '-m', 'Synthetic-only candidate composition').decode().strip()
    F = git(root, 'commit-tree', tree, '-p', M, '-m', 'Synthetic-only empty F; no firmware built').decode().strip()
    git(root, 'update-ref', 'refs/heads/synthetic021F', F)
    git(root, 'checkout', '-q', 'synthetic021F')
    assert proof.authenticate(root)['phase'] == 'CANDIDATE_VALIDATION_ONLY'
    git(root, 'checkout', '-q', 'synthetic038')
    digest = 'a' * 64
    locator = f'local_backups/hardware-artifacts/{F}/{digest}/firmware.uf2'
    state = rewrite_queue(root, 'GP-CONFIG-021', {
        'candidate_git_sha':F, 'candidate_base_configurator_sha':M,
        'firmware_artifact_sha256':digest,
        'firmware_artifact_build_path':'.pio/build/glyph_mk6/firmware.uf2',
        'preserved_firmware_artifact_locator':locator,
        'manual_acceptance_protocol_reference':proof.PROTOCOL,
        'manual_acceptance_protocol_version':'GP_CONFIG_021_HW_V1'})
    # Exact native field parser is exercised with an explicit synthetic scope.
    protocol = ('SYNTHETIC GOVERNANCE VALIDATION ONLY. No firmware/artifact or human observations exist.\n'
        f'- Candidate Git SHA: `{F}`\n- Candidate tree: `{tree}`\n'
        f'- Sole parent / authorized canonical base: `{M}`\n'
        f'- UF2 SHA-256: `{digest}`\n- Preserved locator: `{locator}`\n'
        '- Fresh independent postimplementation review: PASS with no findings for the exact candidate, build output, custody bytes, correspondence, and protocol.\n'
        + '\n'.join(proof.REQUIRED_ROWS) + '\n').encode()
    (root / proof.PROTOCOL).write_bytes(protocol)
    commit(root, 'Synthetic-only pending reviewed snapshot')
    R = git(root, 'rev-parse', 'HEAD').decode().strip()
    assert proof._reviewed_build(root, state, before, after, protocol) == (F,M,tree)
    pending = proof.authenticate(root)
    assert pending['phase'] == 'BASELINE' and {F,M} <= pending['object_roots']
    pending_pack=git(root,'-c','protocol.allow=never','pack-objects','--revs','--stdout',
                     data=('\n'.join(sorted(set(pending['object_roots'])|{R}))+'\n').encode())
    pending_parent=root.parent/'pending-closed'; pending_parent.mkdir()
    pending_root=snapshot(pending_parent,pending_pack,R)
    assert git(pending_root,'for-each-ref','--format=%(refname)').decode().splitlines() == [
        'refs/heads/configurator','refs/heads/synthetic038']
    assert proof.authenticate(pending_root)['phase']=='BASELINE'
    for key, value in (
        ('firmware_artifact_sha256', 'b'*64),
        ('preserved_firmware_artifact_locator', 'local_backups/unreviewed/firmware.uf2'),
        ('manual_acceptance_protocol_version', 'GP_CONFIG_017_HW_V1'),
        ('candidate_git_sha', M)):
        bad = dict(state); bad[key] = value
        rejected(lambda bad=bad: proof._reviewed_build(root,bad,before,after,protocol),
                 'reviewed pending build tuple substitution '+key, observations)
    rejected(lambda: proof._reviewed_build(root,state,before,after,protocol+b'\n- UF2 SHA-256: `'+digest.encode()+b'`\n'),
             'duplicate pending protocol identity', observations)
    file=root/proof.PROTOCOL; file.write_bytes(protocol+b'\n')
    rejected(lambda: proof.authenticate(root), 'pending protocol live byte substitution', observations)
    file.write_bytes(protocol)
    for flag, undo in (('--assume-unchanged','--no-assume-unchanged'),('--skip-worktree','--no-skip-worktree')):
        git(root,'update-index',flag,proof.PROTOCOL)
        rejected(lambda: proof.authenticate(root),'pending protocol index '+flag,observations)
        git(root,'update-index',undo,proof.PROTOCOL)
    # Mutate native queue snapshots and exercise the actual outer pending gate.
    for key,value in (('firmware_artifact_sha256','b'*64),
                       ('candidate_base_configurator_sha',proof.B)):
        rewrite_queue(root,'GP-CONFIG-021',{key:value})
        commit(root,'Synthetic invalid pending queue '+key)
        rejected(lambda:proof.authenticate(root),'committed pending queue '+key,observations)
        rewrite_queue(root,'GP-CONFIG-021',{key:state[key]})
        commit(root,'Restore synthetic pending queue '+key)
    state=rewrite_queue(root,'GP-CONFIG-021',{'status':'HARDWARE_TEST_REQUIRED',
        'hardware_evidence_dependency_satisfied':False})
    commit(root,'Synthetic native HARDWARE_TEST_REQUIRED snapshot')
    assert proof.authenticate(root)['phase']=='BASELINE'
    # Native hardware schema receives only unmistakably synthetic observations.
    payload = json.loads(proof.raw_bytes(root,proof.B,proof.previous.EVIDENCE))
    synthetic_text = 'SYNTHETIC VALIDATION INPUT ONLY; no human test or physical acceptance.'
    for key, value in list(payload.items()):
        if isinstance(value,str): payload[key]=synthetic_text
    payload.update(schema_name='glyph_hardware_evidence_record',schema_version=2,
        work_order_id='GP-CONFIG-021',candidate_branch=state['branch'],
        candidate_git_sha=F,candidate_base_configurator_sha=M,
        firmware_artifact_filename='firmware.uf2',
        firmware_artifact_build_path=state['firmware_artifact_build_path'],
        firmware_artifact_sha256=digest,preserved_firmware_artifact_locator=locator,
        evidence_contract_reference=state['hardware_evidence_contract_reference'],
        evidence_contract_version=state['hardware_evidence_contract_version'],
        candidate_protocol_reference=proof.PROTOCOL,candidate_protocol_version='GP_CONFIG_021_HW_V1',
        tested_at='2000-01-01T00:00:00Z',result='PASS',anomalies=[],evidence_gaps=[],
        preconditions=[synthetic_text],negative_regression_checks=[synthetic_text],
        power_cycle_reconnect_checks=[synthetic_text],
        steps=[{'id':key,'instruction':synthetic_text,'expected':synthetic_text,
                'observed':'PASS '+synthetic_text} for key in proof.REQUIRED_ROWS])
    file=root/proof.EVIDENCE;file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(payload,indent=2)+'\n')
    (root/proof.RESULT).write_text(synthetic_text+'\n')
    state=rewrite_queue(root,'GP-CONFIG-021',{'status':'HARDWARE_VALIDATED',
        'hardware_result':'PASS','hardware_evidence_gaps':[],
        'hardware_evidence_dependency_satisfied':True,
        'hardware_evidence_record':'repo-json:'+proof.EVIDENCE})
    commit(root,'Synthetic-only native E schema input; never human evidence')
    E=git(root,'rev-parse','HEAD').decode().strip()
    processor=proof._processor(root,E,state,before,after)
    assert processor['review_commit']==R and processor['evidence_commit']==E
    assert proof.authenticate(root)['phase']=='SOURCE_FREE_PROCESSOR'
    # Earliest exact-tuple R must be regular, even if a child restores its mode.
    with tempfile.TemporaryDirectory(prefix='synthetic038-index-') as index_dir:
        environment=dict(os.environ,GIT_INDEX_FILE=str(Path(index_dir)/'index'))
        git(root,'read-tree',R,env=environment)
        git(root,'update-index','--cacheinfo','100755',git(root,'rev-parse',R+':'+proof.PROTOCOL).decode().strip(),proof.PROTOCOL,env=environment)
        exec_tree=git(root,'write-tree',env=environment).decode().strip()
    badR=git(root,'commit-tree',exec_tree,'-p',D,'-m','Synthetic earliest R executable protocol').decode().strip()
    restoredR=git(root,'commit-tree',git(root,'rev-parse',R+'^{tree}').decode().strip(),'-p',badR,'-m','Synthetic pre-E R mode restoration').decode().strip()
    badE=git(root,'commit-tree',git(root,'rev-parse',E+'^{tree}').decode().strip(),'-p',restoredR,'-m','Synthetic E after historical R mode mutation').decode().strip()
    rejected(lambda:proof._processor(root,badE,state,before,after),
             'earliest R executable mode restored before E',observations)
    for path in proof.CRITICAL:
        mode,_,identity=after[path];file=root/path;file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(proof.raw_bytes(root,proof.C,path));file.chmod(0o644)
        git(root,'update-index','--add','--cacheinfo',mode,identity,path)
    treeI=git(root,'write-tree').decode().strip()
    I=git(root,'commit-tree',treeI,'-p',E,'-p',F,'-m','Synthetic-only source integration after E').decode().strip()
    git(root,'update-ref','refs/heads/synthetic021I',I);git(root,'checkout','-q','synthetic021I')
    record={'work_order':'GP-CONFIG-021','candidate':proof.C,
        **{k:processor[k] for k in ('build','parent','tree','review_commit','evidence_commit')},
        'integration':I}
    (root/proof.TRANSITIONS).write_text(json.dumps({'schema_version':1,'accepted_transitions':[record]},indent=2)+'\n')
    commit(root,'Synthetic-only accepted transition catalog')
    catalog_head=git(root,'rev-parse','HEAD').decode().strip()
    assert proof.authenticate(root)['phase']=='ACCEPTED_TRANSITION'
    completion=dict(evidence,implementation_base_sha=E,reviewed_implementation_sha=I,
        prior_canonical_integration_sha=I,
        reviewed_changed_paths=sorted(proof.CRITICAL))
    rewrite_queue(root,'GP-CONFIG-021',{'status':'DONE','done_evidence':completion})
    commit(root,'Synthetic-only strict product completion')
    assert proof.authenticate(root)['phase']=='ACCEPTED_TRANSITION'
    # A later restoration cannot erase mutations of accepted immutable metadata.
    file=root/proof.PROTOCOL;file.write_bytes(protocol+b'\n')
    commit(root,'Synthetic accepted protocol mutation')
    file.write_bytes(protocol);commit(root,'Synthetic accepted protocol restoration')
    rejected(lambda:proof.authenticate(root),'E descendant protocol mutate then restore',observations)
    return {'synthetic038DONE':D,'syntheticM':M,'syntheticF':F,'syntheticR':R,
            'syntheticE':E,'syntheticI':I,'syntheticCatalog':catalog_head,
            'physical_acceptance':'NOT_CLAIMED','firmware_build':'NOT_RUN'}


def main():
    begun = time.monotonic(); observations = []
    current = proof.authenticate(ROOT)
    before, after = proof.source_contract(ROOT)
    assert len(before) == 236 and len(after) == 238
    assert current['contract'] == 'c021_persisted_recovery'
    assert current['phase'] in {'BASELINE', 'CANDIDATE_VALIDATION_ONLY', 'SOURCE_FREE_PROCESSOR', 'ACCEPTED_TRANSITION'}
    assert current['predecessor_phase'] == 'ACCEPTED_TRANSITION'
    assert {proof.C, proof.B, proof.READY} <= current['object_roots']
    assert current['source_candidates']['HAL/pico/include/comms/NeoPixelBackend.hpp'] == proof.previous.C
    for raw, label in [
        (b'{}', 'catalog fields omitted'),
        (b'{"schema_version":true,"accepted_transitions":[]}', 'boolean catalog version'),
        (b'{"schema_version":1,"schema_version":1,"accepted_transitions":[]}', 'duplicate catalog field'),
        (b'{"schema_version":1,"accepted_transitions":[{},{}]}', 'extra catalog transition'),
        (b'{"schema_version":1,"accepted_transitions":[{"work_order":"GP-CONFIG-022"}]}', 'foreign hardware acceptance')]:
        rejected(lambda raw=raw: proof._catalog(raw), label, observations)
    for path in sorted(proof.HOSTS | proof.NEW_PATHS | proof.CONSUMER_PATHS):
        assert classify_path(path) == 'NON_BEHAVIORAL'
        for alias in (path + '.unreviewed', '/' + path, path.replace('/', '//', 1), path.replace('/', '/./', 1)):
            rejected(lambda alias=alias: classify_path(alias), 'host path alias ' + alias, observations)
    for path in proof.CRITICAL:
        assert classify_path(path) == 'CRITICAL'
    for path in ('HAL/unreviewed_write.cpp', 'builder_scripts/new.py', 'platformio.ini'):
        assert classify_path(path) == 'CRITICAL'
    head = git(ROOT, 'rev-parse', 'HEAD').decode().strip()
    roots = sorted(set(current['object_roots']) | {head})
    pack = git(ROOT, '-c', 'protocol.allow=never', 'pack-objects', '--revs', '--stdout', data=('\n'.join(roots) + '\n').encode())
    with tempfile.TemporaryDirectory(prefix='glyph038-adversarial-') as temp:
        base = Path(temp)
        root = snapshot(base, pack, head)
        expected = proof.critical_tree(root, head)
        assert proof._current_integrity(root, head, expected) == set()
        path = 'HAL/pico/src/comms/ConfiguratorBackend.cpp'
        file = root / path; original = file.read_bytes(); mode = file.stat().st_mode
        file.write_bytes(original + b'\n// synthetic mutation\n')
        rejected(lambda: proof._current_integrity(root, head, expected), 'unstaged critical bytes', observations)
        git(root, 'add', path)
        rejected(lambda: proof._current_integrity(root, head, expected), 'staged critical bytes', observations)
        file.write_bytes(original)
        old_mode, _, blob = expected[path]
        git(root, 'update-index', '--cacheinfo', old_mode, blob, path)
        for flag, undo in (('--assume-unchanged', '--no-assume-unchanged'), ('--skip-worktree', '--no-skip-worktree')):
            git(root, 'update-index', flag, path)
            rejected(lambda: proof._current_integrity(root, head, expected), 'critical index ' + flag, observations)
            git(root, 'update-index', undo, path)
        file.chmod(mode | stat.S_IXUSR)
        rejected(lambda: proof._current_integrity(root, head, expected), 'critical live executable mode', observations)
        file.chmod(mode)
        sibling = root / 'include/core/unreviewed038.hpp'; sibling.write_text('synthetic\n')
        rejected(lambda: proof._current_integrity(root, head, expected), 'untracked critical sibling', observations)
        sibling.unlink()
        ignored = root / 'include/core/.DS_Store'; ignored.write_text('synthetic\n')
        rejected(lambda: proof._current_integrity(root, head, expected), 'ignored critical sibling', observations)
        ignored.unlink()
        unknown = root / 'docs/unreviewed038_metadata.md'; unknown.write_text('synthetic\n')
        rejected(lambda: proof._current_integrity(root, head, expected), 'unknown metadata literal', observations)
        unknown.unlink()
        # A symlink in a declared host input cannot pass the native host reader.
        path = proof.CHECKER; file = root / path; original = file.read_bytes()
        file.unlink(); file.symlink_to(base / 'outside-input')
        rejected(lambda: proof.current_bytes(root, path), 'symlink host input', observations)
        file.unlink(); file.write_bytes(original); file.chmod(0o644)
        for path in (proof.CONSUMER_FIXTURE, proof.CONSUMER_WRAPPER):
            file = root / path; original = file.read_bytes()
            file.write_bytes(original + b'\n')
            rejected(lambda: proof._consumer_contract(root, head), 'one-byte replay input mutation ' + path, observations)
            file.write_bytes(original)
        fixture = json.loads((root / proof.CONSUMER_FIXTURE).read_text())
        path = next(iter(fixture['consumer_lanes'].values()))['original_path']
        file = root / path; original = file.read_bytes()
        file.write_bytes(original + b'\n')
        rejected(lambda: proof._preserve_original_current_inputs(root, head), 'one-byte original main mutation', observations)
        file.write_bytes(original)
        file.chmod(0o755)
        rejected(lambda: proof._preserve_original_current_inputs(root, head), 'original main executable mode', observations)
        file.chmod(0o644)
        for flag, undo in (('--assume-unchanged', '--no-assume-unchanged'), ('--skip-worktree', '--no-skip-worktree')):
            git(root, 'update-index', flag, path)
            rejected(lambda: proof._preserve_original_current_inputs(root, head), 'original main index ' + flag, observations)
            git(root, 'update-index', undo, path)
        # Every manifest mutation is committed in this disposable repo, so the
        # semantic gate, rather than dirty-index rejection, must detect it.
        path = 'docs/runtime_config/fixtures/runtime_config_validation_manifest.json'
        baseline = json.loads((root / path).read_text())
        mutations = []
        def mutate(label, fn):
            doc = json.loads(json.dumps(baseline)); fn(doc); mutations.append((label, doc))
        mutate('manifest required C lane deleted', lambda d: d['entries'].__setitem__(slice(None), [e for e in d['entries'] if e['id'] != 'gp_config021_persisted_recovery']))
        mutate('manifest current C lane demoted', lambda d: next(e for e in d['entries'] if e['id'] == 'gp_config021_persisted_recovery').update(load_bearing=False))
        mutate('manifest required C lane renamed', lambda d: next(e for e in d['entries'] if e['id'] == 'gp_config021_persisted_recovery').update(id='unserved038'))
        mutate('manifest C load-bearing bool replaced with integer', lambda d: next(e for e in d['entries'] if e['id'] == 'gp_config021_persisted_recovery').update(load_bearing=1))
        mutate('manifest extra checker path', lambda d: next(e for e in d['entries'] if e['id'] == 'gp_config021_persisted_recovery').update(path='tools/unreviewed038.py'))
        mutate('manifest C lane historical relabel', lambda d: next(e for e in d['entries'] if e['id'] == 'gp_config021_persisted_recovery').update(historical=True))
        mutate('manifest C command substituted', lambda d: next(e for e in d['entries'] if e['id'] == 'gp_config021_persisted_recovery').update(command=['python3', proof.CHECKER]))
        mutate('manifest helper dependency omitted', lambda d: next(e for e in d['entries'] if e['id'] == 'gp_config021_persisted_recovery')['source_dependencies'].remove('tools/glyph_c021_campaign_transition.py'))
        mutate('manifest existing proof excluded', lambda d: d['strong_signal_exclusions'].append({'path':'tools/check_glyph_configurator_setconfig_transaction.py','reason':'synthetic'}))
        for label, document in mutations:
            (root / path).write_text(json.dumps(document, indent=2) + '\n'); commit(root, label)
            target = git(root, 'rev-parse', 'HEAD').decode().strip()
            rejected(lambda target=target: proof._manifest_contract(root, target), label, observations)
        (root / path).write_text(json.dumps(baseline, indent=2) + '\n'); commit(root, 'Restore synthetic manifest input')
        phase_parent=base/'phases'; phase_parent.mkdir()
        phase_root=snapshot(phase_parent,pack,head)
        phases=phase_controls(phase_root,head,before,after,observations)
        # Immutable predecessor metadata may not change mode and later return.
        path = proof.previous.PROTOCOL; file = root / path; file.chmod(0o755)
        commit(root, 'Synthetic accepted metadata mode mutation')
        file.chmod(0o644); commit(root, 'Synthetic accepted metadata mode restoration')
        target = git(root, 'rev-parse', 'HEAD').decode().strip()
        rejected(lambda: proof._preserve_accepted_predecessors(root, target), 'historical accepted metadata chmod then restore', observations)
        # Wrong pending build identities cannot inherit predecessor acceptance.
        state = proof.item(ROOT, head, 'GP-CONFIG-021')
        for parent, label in ((None, 'pending F parent missing'), (proof.B, 'pending F parent is baseline'),
                              (proof.previous.C, 'pending F parent is predecessor candidate')):
            bad = dict(state, candidate_git_sha=proof.previous.C, candidate_base_configurator_sha=parent)
            rejected(lambda bad=bad: proof._reviewed_build(ROOT, bad, before, after, b''), label, observations)
    assert git(ROOT, 'rev-parse', 'HEAD').decode().strip() == head
    print(json.dumps({'classification':'SYNTHETIC_GOVERNANCE_VALIDATION_ONLY', 'status':'PASS',
        'head':head, 'phase':current['phase'], 'actual_negative_count':len(observations),
        'negative_controls':observations, 'synthetic_phase_graph':phases, 'elapsed_seconds':round(time.monotonic()-begun,3),
        'hardware_acceptance':'NOT_CLAIMED', 'target_build':'NOT_RUN'}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
