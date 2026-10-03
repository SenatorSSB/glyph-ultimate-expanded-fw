#!/usr/bin/env python3
"""Isolated positive and negative checks for GP-CONFIG-010 proof applicability."""
from __future__ import annotations

import os
import copy
import json
import hashlib
import re
import sys
from unittest.mock import patch
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = "2fd9a827b90b2079f981d75e836833dc99ec7b10"
CANDIDATE = "1c0ff22646729d26d45eacb4b8322c5baea7de48"
CHECKER = "tools/check_glyph_config_010_integration_semantic_correspondence.py"
CLASSIFIER = "tools/glyph_hardware_correspondence.py"
CAMPAIGN = "tools/glyph_campaign_transition.py"
SELF_HEAD = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def run(root: Path, *command: str, expected: int = 0) -> str:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True)
    if result.returncode != expected:
        raise AssertionError(f"{command!r}: expected {expected}, got {result.returncode}\n{result.stdout}{result.stderr}")
    return result.stdout


def commit_change(root: Path, path: str, text: str, branch: str) -> None:
    run(root, "git", "switch", "--detach", SELF_HEAD)
    run(root, "git", "switch", "-c", branch)
    location = root / path
    location.parent.mkdir(parents=True, exist_ok=True)
    location.write_text(location.read_text() + text if location.exists() else text)
    run(root, "git", "add", "--", path)
    run(root, "git", "commit", "-m", branch)


def rejected(call, label: str) -> None:
    try:
        call()
    except (ValueError, AssertionError, OSError):
        return
    raise AssertionError("negative accepted: " + label)


def stable_historical_tests(root: Path) -> None:
    import check_glyph_config_010_integration_semantic_correspondence as checker
    value = json.loads(checker.FIXTURE.read_text())
    with patch.object(checker, "ROOT", root):
        results = []
        for abbreviation in (7, 12, 40):
            run(root, "git", "config", "core.abbrev", str(abbreviation))
            result = checker.verify_historical_patch(value)
            assert result in {"LEGACY_EXACT", "STABLE_FULL_INDEX_EXACT"}
            results.append(result)
        assert "STABLE_FULL_INDEX_EXACT" in results
        run(root, "git", "config", "--unset", "core.abbrev")
        actual = checker.git
        def changed_body(*args, **kwargs):
            data = actual(*args, **kwargs)
            return data + b"\n+invented source body\n" if args[0] == "diff" else data
        with patch.object(checker, "git", side_effect=changed_body):
            rejected(lambda: checker.verify_historical_patch(value), "historical patch body substitution")
        def changed_mode(*args, **kwargs):
            data = actual(*args, **kwargs)
            return data.replace(b"100644", b"100755", 1) if args[0] == "ls-tree" else data
        with patch.object(checker, "git", side_effect=changed_mode):
            rejected(lambda: checker.verify_historical_patch(value), "historical source mode substitution")


def campaign_contract_tests(directory: Path) -> None:
    """Real scratch-tree negatives plus explicitly synthetic acceptance controls."""
    import glyph_campaign_transition as campaign
    import check_glyph_agent_framework_docs as framework
    root = directory / "campaign-contract"
    run(ROOT, "git", "clone", "--quiet", "--no-local", str(ROOT), str(root))
    run(root, "git", "switch", "--detach", "caf0718472c7752c78838be6f1d48b56932d90b9")
    # Read-only contract authentication exercises the actual immutable objects.
    before, after = campaign.source_contract(root)
    assert before != after and set(after) - set(before) == campaign.CRITICAL - {
        "HAL/pico/src/comms/ConfiguratorBackend.cpp"}
    campaign.authenticate(root)
    stable_historical_tests(root)
    for path in campaign.FROZEN:
        file = root / path
        original = file.read_bytes()
        try:
            file.write_bytes(original + b"\n")
            rejected(lambda: campaign.authenticate(root), "frozen fixture " + path)
        finally:
            file.write_bytes(original)
    for path in ("src/core/mode_selection.cpp", "platformio.ini",
                 "HAL/pico/src/comms/ConfiguratorBackend.cpp"):
        file = root / path
        original = file.read_bytes()
        try:
            file.write_bytes(original + b"\n// invalid source substitution\n")
            rejected(lambda: campaign.authenticate(root), "source substitution " + path)
        finally:
            file.write_bytes(original)
    staged = root / "src/core/mode_selection.cpp"
    original = staged.read_bytes()
    try:
        staged.write_bytes(original + b"\n// staged source substitution\n")
        run(root, "git", "add", "src/core/mode_selection.cpp")
        rejected(lambda: campaign.authenticate(root), "staged critical source")
    finally:
        staged.write_bytes(original)
        run(root, "git", "add", "src/core/mode_selection.cpp")
    ignored = root / "src/core/.gp_val037_ignored.cpp"
    exclude = root / ".git/info/exclude"
    original_exclude = exclude.read_bytes()
    try:
        exclude.write_bytes(original_exclude + b"\nsrc/core/.gp_val037_ignored.cpp\n")
        ignored.write_text("// ignored critical source\n")
        rejected(lambda: campaign.authenticate(root), "ignored critical source")
    finally:
        ignored.unlink()
        exclude.write_bytes(original_exclude)
    for path in ("docs/unknown_gp_val037.md", "tools/glyph_campaign_transition.py.bak",
                 "include/core/config_button_validation.hpp.bak",
                 "include/core/Config_button_validation.hpp"):
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        try:
            file.write_text("unknown adjacent or aliased input\n")
            rejected(lambda: campaign.authenticate(root), "unknown path " + path)
        finally:
            file.unlink()
    file = root / "HAL/pico/src/comms/ConfiguratorBackend.cpp"
    original = file.read_bytes()
    mode = file.stat().st_mode
    try:
        file.chmod(mode | 0o111)
        rejected(lambda: campaign.authenticate(root), "executable critical input")
        file.chmod(mode)
        file.unlink()
        file.symlink_to("backend_init.cpp")
        rejected(lambda: campaign.authenticate(root), "symlink critical input")
    finally:
        file.unlink()
        file.write_bytes(original)
        file.chmod(mode)
    # Source-contract substitutions are injected at the object read boundary;
    # they cannot write Git objects or mutate the immutable candidate.
    actual_git = campaign._git
    for label, command, replacement in (
        ("wrong parent", ("rev-list", "--parents", "-n", "1", campaign.C),
         (campaign.C + " " + "0" * 40).encode()),
        ("wrong tree", ("rev-parse", campaign.C + "^{tree}"), b"0" * 40),
        ("raw inventory substitution", ("diff-tree", "-r", "--no-renames", "--raw", "-z", campaign.B, campaign.C), b"substituted"),
    ):
        def changed_git(where, *args):
            return replacement if args == command else actual_git(where, *args)
        with patch.object(campaign, "_git", side_effect=changed_git):
            rejected(lambda: campaign.source_contract(root), label)
    actual_bytes = campaign.raw_bytes
    for label, transform in (
        ("omitted validator", lambda b: b.replace(campaign.INSERT_BODY, b"")),
        ("duplicated validator", lambda b: b.replace(campaign.INSERT_BODY, campaign.INSERT_BODY * 2)),
        ("changed publication", lambda b: b.replace(b"_config = candidate;", b"_config = Config_init_zero;")),
    ):
        def changed_bytes(where, ref, path):
            data = actual_bytes(where, ref, path)
            return transform(data) if ref == campaign.C and path == "HAL/pico/src/comms/ConfiguratorBackend.cpp" else data
        with patch.object(campaign, "raw_bytes", side_effect=changed_bytes):
            rejected(lambda: campaign.source_contract(root), label)

    accepted_contract_tests(directory)
    print("GP-VAL-037 real Git phase and contract negatives PASS; synthetic records stay in disposable clones")


def write_queue_item(root: Path, value: dict) -> None:
    import glyph_campaign_transition as campaign
    state=campaign.queue(root,'HEAD')
    state['items']=[value if x['id']=='GP-CONFIG-020' else x for x in state['items']]
    path=root/campaign.QUEUE
    text=path.read_text()
    prefix,tail=text.split('<!-- queue-state:start -->')
    _,suffix=tail.split('<!-- queue-state:end -->')
    path.write_text(prefix+'<!-- queue-state:start -->\n```json\n'+json.dumps(state,indent=2)+'\n```\n<!-- queue-state:end -->'+suffix)


def fixture_commit(root: Path, message: str) -> str:
    run(root,'git','add','--all')
    run(root,'git','commit','--allow-empty','-m','SYNTHETIC TEST ONLY: '+message)
    return run(root,'git','rev-parse','HEAD').strip()


def make_synthetic_accepted_fixture(directory: Path, *, repaired: bool = False) -> tuple[Path, dict]:
    """Disposable real Git evidence chronology; never physical acceptance.

    Call only with a fresh temp directory. Returned repository can run actual
    consumers/aggregates after their normal deterministic manifest/census update.
    This function performs no firmware build, artifact creation, or publication.
    """
    import glyph_campaign_transition as campaign
    import glyph_c020_abi_repair_transition as repair
    candidate = repair.C_R if repaired else campaign.C
    catalog_path = repair.TRANSITIONS if repaired else campaign.TRANSITIONS
    root=directory.resolve()/('repaired-accepted-contract' if repaired else 'accepted-contract')
    run(ROOT,'git','clone','--quiet','--no-local',str(ROOT),str(root))
    # Nested disposable clones need immutable off-head roots that may be present
    # only as the caller's remote refs. Fetch exact objects locally without refs.
    roots = repair.ROOTS if repaired else campaign.ROOTS
    run(root, 'git', 'fetch', '--quiet', '--no-tags', '--no-write-fetch-head',
        str(ROOT), *sorted(roots))
    run(root,'git','config','user.name','Synthetic GP-VAL-037 tests')
    run(root,'git','config','user.email','synthetic@example.invalid')
    source_free_base = repair.B_R if repaired else 'caf0718472c7752c78838be6f1d48b56932d90b9'
    run(root, 'git', 'switch', '--detach', source_free_base)
    if repaired:
        # Copy only adopted H1 governance literals from the current worktree.
        # ROOT may itself be a composed candidate; critical source is never copied.
        status_paths = {'docs/AGENT_CONTEXT.md', 'docs/CURRENT_STATE.md',
                        'docs/ROADMAP.md', campaign.QUEUE}
        accepted_metadata = {repair.PROTOCOL, repair.EVIDENCE,
                             'docs/calibration/gp_config_020_hardware_result.md'}
        excluded = repair.PROOF_PATHS | status_paths | accepted_metadata | {
            campaign.TRANSITIONS, repair.TRANSITIONS}
        for path in sorted(repair.GOVERNANCE_PATHS - excluded):
            source = ROOT / path
            if source.is_file():
                destination = root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
        # Accepted caller catalogs, queue and protocol are never a fixture base.
        # Reconstruct source-free status mirrors from the authenticated handoff.
        for path in sorted(status_paths):
            (root / path).write_bytes(campaign.raw_bytes(root, repair.HANDOFF_R, path))
        for path in (campaign.TRANSITIONS, repair.TRANSITIONS):
            (root / path).write_text('{"schema_version":1,"accepted_transitions":[]}\n')
        G = fixture_commit(root, 'source-free repaired governance on explicit B_R')
        assert campaign.critical_tree(root, G) == campaign.critical_tree(root, repair.B_R)
        assert campaign.authenticate(root)['phase'] == 'BASELINE'
    else:
        G=run(root,'git','rev-parse','HEAD').strip()
        assert campaign.critical_tree(root, G) == campaign.critical_tree(root, campaign.B)
    private_suffix = hashlib.sha256(str(root).encode()).hexdigest()[:12]
    run(root,'git','switch','-c','synthetic-candidate-' + private_suffix)
    run(root,'git','merge','--no-ff','--no-edit',candidate)
    P=run(root,'git','rev-parse','HEAD').strip()
    F=fixture_commit(root,'unbuilt candidate identity; no artifact exists')
    T=run(root,'git','rev-parse',F+'^{tree}').strip()
    if repaired:
        proof = campaign.authenticate(root)
        assert proof['phase'] == 'CANDIDATE_VALIDATION_ONLY' and proof['candidate'] == repair.C_R
    run(root,'git','switch','--detach',G)
    run(root,'git','switch','-c','synthetic-evidence-' + private_suffix)
    review=campaign.item(root,G,'GP-CONFIG-020')
    digest='a'*64
    locator=f'local_backups/hardware-artifacts/{F}/{digest}/firmware.uf2'
    review.update(status='HARDWARE_TEST_REQUIRED',candidate_git_sha=F,candidate_base_configurator_sha=P,
        firmware_artifact_build_path='.pio/build/glyph_mk6/firmware.uf2',firmware_artifact_sha256=digest,
        preserved_firmware_artifact_locator=locator,hardware_result=None,hardware_evidence_gaps=[],
        hardware_evidence_dependency_satisfied=False,manual_acceptance_protocol_reference=campaign.PROTOCOL,
        manual_acceptance_protocol_version='GP_CONFIG_020_HW_V1',
        done_evidence='Synthetic disposable test: no actual build, artifact, review, or hardware result.')
    protocol=(f'# SYNTHETIC TEST ONLY: GP-CONFIG-020 protocol\n\n'
        f'- Candidate Git SHA: `{F}`\n- Candidate tree: `{T}`\n'
        f'- Sole parent / authorized canonical base: `{P}`\n'
        f'- UF2 SHA-256: `{digest}`\n- Preserved locator: `{locator}`\n'
        '- Fresh independent postimplementation review: PASS with no findings for the\n'
        '  exact candidate, build output, custody bytes, correspondence, and protocol.\n')
    (root/campaign.PROTOCOL).write_text(protocol)
    write_queue_item(root,review)
    R=fixture_commit(root,'source-free synthetic review handoff')
    template=json.loads((root/'docs/calibration/fixtures/gp_config_010_integration_hardware_evidence_2026-09-23.json').read_text())
    for key in ('candidate_git_sha','candidate_base_configurator_sha','firmware_artifact_build_path',
                'firmware_artifact_sha256','preserved_firmware_artifact_locator'):
        template[key]=review[key]
    template.update(work_order_id='GP-CONFIG-020',candidate_branch=review['branch'],
        candidate_protocol_reference=campaign.PROTOCOL,candidate_protocol_version=review['manual_acceptance_protocol_version'],
        tester='SYNTHETIC TEST ONLY; no real controller observation',
        preconditions=['Synthetic test of validation; no actual build or hardware acceptance.'],
        steps=[dict(id='SYNTHETIC',instruction='Test validation only',expected='Synthetic record',observed='Synthetic PASS')],
        negative_regression_checks=[],power_cycle_reconnect_checks=[],anomalies=[],
        rollback_recovery='Synthetic test only',firmware_profile_state='Synthetic test only',
        controller_model_revision='Synthetic test only',host_platform_adapter='Synthetic test only',
        update_method='No update performed',result='PASS',evidence_gaps=[])
    (root/campaign.EVIDENCE).write_text(json.dumps(template,indent=2)+'\n')
    (root/'docs/calibration/gp_config_020_hardware_result.md').write_text(
        '# SYNTHETIC TEST ONLY\nNo actual controller result; disposable validation fixture.\n')
    payload=fixture_commit(root,'synthetic evidence object after review')
    accepted=dict(review,status='HARDWARE_VALIDATED',hardware_result='PASS',hardware_evidence_dependency_satisfied=True,
        hardware_evidence_record='git-json:'+payload+':'+campaign.EVIDENCE)
    write_queue_item(root,accepted)
    E=fixture_commit(root,'source-free synthetic processor acceptance')
    run(root,'git','merge','--no-ff','--no-edit',F)
    I=run(root,'git','rev-parse','HEAD').strip()
    record=dict(work_order='GP-CONFIG-020',candidate=candidate,build=F,parent=P,tree=T,
                review_commit=R,evidence_commit=E,integration=I)
    (root/catalog_path).write_text(json.dumps(dict(schema_version=1,accepted_transitions=[record]),indent=2)+'\n')
    fixture_commit(root,'synthetic accepted transition catalog')
    return root,record


def accepted_live_input_tests(root: Path) -> None:
    """Every call rechecks live inputs after a successful accepted proof."""
    import glyph_campaign_transition as campaign
    assert campaign.authenticate(root)['phase']=='ACCEPTED_TRANSITION'
    source=root/'src/core/config_button_validation.cpp'
    original=source.read_bytes()
    mode=source.stat().st_mode
    try:
        source.write_bytes(original+b'\n// rejected dirty source\n')
        with patch.object(campaign,'source_contract',wraps=campaign.source_contract) as source_proof:
            rejected(lambda:campaign.authenticate(root),'fresh accepted dirty source')
            assert not source_proof.called
        run(root,'git','add','--','src/core/config_button_validation.cpp')
        source.write_bytes(original)
        rejected(lambda:campaign.authenticate(root),'fresh accepted staged source')
    finally:
        source.write_bytes(original)
        run(root,'git','add','--','src/core/config_button_validation.cpp')
    try:
        source.chmod(mode|0o111)
        rejected(lambda:campaign.authenticate(root),'fresh accepted executable mode')
    finally:
        source.chmod(mode)
    ignored=root/'src/core/.gp_val037_ignored.cpp'
    exclude=root/'.git/info/exclude'
    previous_exclude=exclude.read_bytes()
    try:
        exclude.write_bytes(previous_exclude+b'\nsrc/core/.gp_val037_ignored.cpp\n')
        ignored.write_text('// rejected ignored critical source\n')
        rejected(lambda:campaign.authenticate(root),'fresh accepted ignored critical source')
    finally:
        ignored.unlink()
        exclude.write_bytes(previous_exclude)
    frozen=root/campaign.FROZEN[0]
    prior=frozen.read_bytes()
    try:
        frozen.write_bytes(prior+b'\n')
        rejected(lambda:campaign.authenticate(root),'fresh accepted historical fixture substitution')
    finally:
        frozen.write_bytes(prior)
    assert campaign.authenticate(root)['phase']=='ACCEPTED_TRANSITION'
    governance=root/'docs/ROADMAP.md'
    original_governance=governance.read_bytes()
    try:
        governance.write_bytes(original_governance+b'\nSynthetic allowed governance test.\n')
        with patch.object(campaign,'source_contract',wraps=campaign.source_contract) as source_proof:
            assert campaign.authenticate(root)['phase']=='ACCEPTED_TRANSITION'
            assert source_proof.called
    finally:
        governance.write_bytes(original_governance)


def tree_inventory_cache_tests(root: Path) -> None:
    """Only full immutable inventory reads are reused, within one invocation."""
    import glyph_campaign_transition as campaign
    native=campaign._uncached_tree
    calls=[]
    def counted(where,ref):
        calls.append((str(Path(where).resolve()),ref))
        return native(where,ref)
    with patch.object(campaign,'_uncached_tree',side_effect=counted):
        campaign.source_contract(root)
        assert calls.count((str(root.resolve()),campaign.B))==1
        campaign.source_contract(root)
        assert calls.count((str(root.resolve()),campaign.B))==2
    assert campaign._tree_inventory_cache.get() is None
    @campaign._proof_invocation
    def symbolic_and_immutable():
        value=campaign._tree(root,campaign.B)
        value.clear()
        assert campaign._tree(root,campaign.B)
        campaign._tree(root,'HEAD')
        campaign._tree(root,'HEAD')
    calls.clear()
    with patch.object(campaign,'_uncached_tree',side_effect=counted):
        symbolic_and_immutable()
    assert calls.count((str(root.resolve()),campaign.B))==1
    assert calls.count((str(root.resolve()),'HEAD'))==2
    @campaign._proof_invocation
    def failed():
        campaign._tree(root,campaign.B)
        raise ValueError('synthetic invocation failure')
    rejected(failed,'cache reset on failure')
    assert campaign._tree_inventory_cache.get() is None
    assert campaign._blob_bytes_cache.get() is None
    # Distinct immutable refs with one blob share bytes, while symbolic HEAD
    # reads and decoded queue dictionaries remain fresh.
    actual_git=campaign._git
    shows=[]
    def observed_git(where,*args):
        if args[0]=='show': shows.append(args[1])
        return actual_git(where,*args)
    path='src/core/mode_selection.cpp'
    @campaign._proof_invocation
    def blobs():
        assert campaign.raw_bytes(root,campaign.B,path)==campaign.raw_bytes(root,campaign.F010,path)
        campaign.raw_bytes(root,'HEAD',path)
        campaign.raw_bytes(root,'HEAD',path)
        first=campaign.queue(root,campaign.ADOPTION)
        first['items'].clear()
        assert campaign.queue(root,campaign.ADOPTION)['items']
    with patch.object(campaign,'_git',side_effect=observed_git):
        blobs()
        blobs()
    assert shows.count(campaign.B+':'+path)==2
    assert shows.count(campaign.F010+':'+path)==0
    assert shows.count('HEAD:'+path)==4
    assert shows.count(campaign.ADOPTION+':'+campaign.QUEUE)==2
    assert campaign._blob_bytes_cache.get() is None
    # The lower correspondence layer shares only exact immutable query bytes.
    import glyph_hardware_correspondence as hardware
    native_run = hardware.subprocess.run
    invocations = []
    def observed_run(command, *args, **kwargs):
        invocations.append(tuple(command[1:]))
        return native_run(command, *args, **kwargs)
    immutable = ('rev-parse', campaign.B + '^{tree}')
    live = ('rev-parse', 'HEAD')
    dirty = ('diff', '--name-only', '-z')
    absent = ('ls-tree', '-r', '-z', '0' * 40)
    @campaign._proof_invocation
    def query_reads():
        for command in (immutable, immutable, live, live, dirty, dirty):
            hardware._git(root, *command)
        for _ in range(2):
            rejected(lambda: hardware._git(root, *absent), 'failed immutable query must rerun')
    with patch.object(hardware.subprocess, 'run', side_effect=observed_run):
        query_reads()
        query_reads()
    assert invocations.count(immutable) == 2
    assert invocations.count(live) == 4 and invocations.count(dirty) == 4
    assert invocations.count(absent) == 4
    for args in (('ls-tree', '-r', '-z', 'HEAD'), ('merge-base', campaign.B, 'HEAD'),
                 ('rev-list', '--reverse', '--topo-order', campaign.B + '..HEAD'),
                 ('diff', '--cached', '--name-only', '-z'), ('ls-files', '--stage'),
                 ('ls-tree', '-r', '-z', campaign.B.upper())):
        assert not hardware._immutable_query(args)
    rejected(failed, 'all immutable caches reset on failure')
    assert hardware._immutable_query_cache.get() is None
    native_tree=campaign._tree
    def executable(where,ref):
        value=native_tree(where,ref)
        if ref==campaign.F010:
            entry=value[path]
            value[path]=('100755',*entry[1:])
        return value
    @campaign._proof_invocation
    def mode_still_checked():
        campaign.raw_bytes(root,campaign.B,path)
        with patch.object(campaign,'_tree',side_effect=executable):
            rejected(lambda:campaign.raw_bytes(root,campaign.F010,path),'cached blob still requires regular mode')
    mode_still_checked()
    assert campaign._blob_bytes_cache.get() is None


def accepted_contract_tests(directory: Path) -> None:
    import glyph_campaign_transition as campaign
    root,record=make_synthetic_accepted_fixture(directory)
    target=run(root,'git','rev-parse','HEAD').strip()
    with patch.object(campaign,'verify_correspondence',wraps=campaign.verify_correspondence) as live_proofs:
        assert campaign.authenticate(root)['phase']=='ACCEPTED_TRANSITION'
        calls=live_proofs.call_args_list
        assert any(call.args[1]==campaign.C and call.kwargs.get('target')==target
                   and call.kwargs['check_worktree'] is False for call in calls)
        assert any(call.args[1]==record['build'] and call.kwargs.get('target')==target
                   and call.kwargs['check_worktree'] is True for call in calls)
    assert campaign.validate_accepted_transition(root,record,target)==record['build']
    accepted_live_input_tests(root)
    tree_inventory_cache_tests(root)
    # Missing/empty catalogs are tested against actual accepted source + queue.
    catalog=root/campaign.TRANSITIONS
    original=catalog.read_bytes()
    evidence=root/campaign.EVIDENCE
    evidence_bytes=evidence.read_bytes()
    try:
        evidence.write_bytes(evidence_bytes+b'\n')
        rejected(lambda:campaign.validate_accepted_transition(root,record,target),'current evidence substitution')
    finally:
        evidence.write_bytes(evidence_bytes)
    try:
        catalog.unlink()
        rejected(lambda:campaign.authenticate(root),'missing accepted catalog')
        catalog.write_text('{"schema_version":1,"accepted_transitions":[]}\n')
        rejected(lambda:campaign.authenticate(root),'empty accepted catalog')
    finally:
        catalog.write_bytes(original)
    for key,value in (('work_order','GP-CONFIG-014'),('work_order','GP-CONFIG-017'),
                      ('work_order','GP-CONFIG-021'),('candidate','0'*40),('build','HEAD'),
                      ('parent',campaign.B),('tree','0'*40),
                      ('review_commit',record['evidence_commit']),
                      ('evidence_commit',record['integration']),
                      ('integration',record['review_commit'])):
        rejected(lambda:campaign.validate_accepted_transition(root,dict(record,**{key:value}),target),
                 'accepted identity/chronology '+key)
    rejected(lambda:campaign.validate_accepted_transition(root,dict(record,bypass=True),target),'extra accepted field')
    protocol=campaign.raw_bytes(root,record['review_commit'],campaign.PROTOCOL).decode()
    digest='a'*64
    locator=f'local_backups/hardware-artifacts/{record["build"]}/{digest}/firmware.uf2'
    campaign.validate_build_review(protocol,record,digest,locator)
    for label,bad in (
        ('review failure',protocol.replace('PASS with no findings','FAIL with findings')),
        ('pending review',protocol.replace('PASS with no findings','PENDING')),
        ('loose prose','independent review '+record['build']),
        ('duplicate block',protocol+protocol),
        ('wrong tree',protocol.replace(record['tree'],'0'*40)),
        ('wrong artifact',protocol.replace(digest,'b'*64)),
        ('wrong locator',protocol.replace(locator,'.pio/firmware.uf2')),
        ('contradictory review',protocol+'\n- Review: FAIL\n'),
    ):
        rejected(lambda:campaign.validate_build_review(bad,record,digest,locator),label)
    # Committed tip rewrites cannot erase accepted history, even when both the
    # queue and catalog are changed together to claim a candidate-only phase.
    run(root,'git','switch','-c','synthetic-downgrade',target)
    downgraded=campaign.item(root,target,'GP-CONFIG-020')
    downgraded.update(status='REVIEW',hardware_result=None,hardware_evidence_record=None,
                      hardware_evidence_dependency_satisfied=None)
    write_queue_item(root,downgraded)
    catalog.write_text('{"schema_version":1,"accepted_transitions":[]}\n')
    fixture_commit(root,'attempt to erase accepted queue and catalog')
    rejected(lambda:campaign.authenticate(root),'committed queue/catalog accepted downgrade')
    run(root,'git','switch','--detach',target)
    # Even before the first catalog publication, processor PASS in integrated
    # ancestry cannot be hidden by replacing only the current queue.
    run(root,'git','switch','-c','synthetic-pre-catalog-downgrade',record['integration'])
    write_queue_item(root,downgraded)
    fixture_commit(root,'attempt to erase processor PASS before catalog')
    rejected(lambda:campaign.authenticate(root),'committed pre-catalog processor downgrade')
    run(root,'git','switch','--detach',target)
    # An ours merge can retain candidate-only bytes while adding accepted
    # ancestry through the second parent. A path-limited rev-list may simplify
    # away that parent; complete commit ancestry must still reject the downgrade.
    run(root,'git','switch','-c','synthetic-ours-merge-downgrade',record['build'])
    run(root,'git','merge','--no-ff','-s','ours','--no-edit',target)
    rejected(lambda:campaign.authenticate(root),'ours merge hides accepted second-parent history')
    run(root,'git','switch','--detach',target)
    # Boundary injection retains all real commits/objects, changing one input at
    # a time. No all-ancestor or processor-validation mocks can create a PASS.
    native_item=campaign.item
    for which,key,value in (
        (record['review_commit'],'status','READY'),
        (record['review_commit'],'candidate_git_sha','0'*40),
        (record['review_commit'],'firmware_artifact_sha256','b'*64),
        (record['review_commit'],'preserved_firmware_artifact_locator','.pio/firmware.uf2'),
        (record['evidence_commit'],'hardware_result','FAIL'),
        (record['evidence_commit'],'hardware_evidence_gaps',['missing test']),
        (record['evidence_commit'],'hardware_evidence_record','git-json:'+campaign.C+':'+campaign.EVIDENCE),
        (target,'status','REVIEW'),
    ):
        def altered_item(where,ref,order):
            value_item=native_item(where,ref,order)
            return dict(value_item,**{key:value}) if ref==which else value_item
        with patch.object(campaign,'item',side_effect=altered_item):
            rejected(lambda:campaign.validate_accepted_transition(root,record,target),'accepted '+key)



def repaired_blob_prefetch_tests(root: Path) -> None:
    """Finite blob batches fail atomically; cached bytes never bypass ref modes."""
    import glyph_campaign_transition as campaign
    import glyph_c020_abi_repair_transition as repair
    def identity(data):
        return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    def reply(oid, data):
        return oid.encode() + b' blob ' + str(len(data)).encode() + b'\n' + data + b'\n'
    payloads = (b'first\n\0payload', b'second payload')
    ids = tuple(identity(data) for data in payloads)
    replies = tuple(reply(oid, data) for oid, data in zip(ids, payloads))
    valid = b''.join(replies)
    assert repair._parse_blob_batch(valid, ids) == dict(zip(ids, payloads))
    assert repair._parse_blob_batch(b'', ()) == {}
    for label, data in (
        ('truncated header', valid[:20]), ('missing reply', replies[0]),
        ('truncated payload', valid[:-3]), ('missing trailer', valid[:-1]),
        ('wrong trailer', valid[:-1] + b'x'), ('extra output', valid + b'x'),
        ('duplicate reply', valid + replies[0]), ('reordered reply', b''.join(reversed(replies))),
        ('wrong type', valid.replace(b' blob ', b' tree ', 1)),
        ('wrong declared size', valid.replace(b' blob 14\n', b' blob 13\n', 1)),
        ('substituted hash', b'0' * 40 + valid[40:]),
        ('substituted payload', valid.replace(b'first', b'forgd', 1)),
        ('missing object', ids[0].encode() + b' missing\n'),
    ):
        rejected(lambda: repair._parse_blob_batch(data, ids), label)
    rejected(lambda: repair._parse_blob_batch(valid, (ids[0], ids[0])), 'duplicate requested identities')
    rejected(lambda: repair._parse_blob_batch(valid, ('HEAD', ids[1])), 'symbolic requested identity')

    paths = ('src/core/config_button_validation.cpp',
             'tools/fixtures/gp_config020_button_validation/abi_probe.cpp')
    requests = tuple((repair.C_R, path) for path in paths)
    native_tree = campaign._tree
    @campaign._proof_invocation
    def exercise():
        inventory = native_tree(root, repair.C_R)
        oids = tuple(sorted({inventory[path][2] for path in paths}))
        bodies = {inventory[path][2]: campaign._git(root, 'show', repair.C_R + ':' + path)
                  for path in paths}
        output = b''.join(reply(oid, bodies[oid]) for oid in oids)
        cache = campaign._blob_bytes_cache.get()
        sentinel = (str(root.resolve()), 'f' * 40)
        cache[sentinel] = b'preexisting immutable bytes'
        for label, response, code in (
            ('partial successful response', output[:-1], 0),
            ('missing response', reply(oids[0], bodies[oids[0]]), 0),
            ('missing object response', oids[0].encode() + b' missing\n', 0),
            ('wrong type response', output.replace(b' blob ', b' tree ', 1), 0),
            ('wrong hash response', b'0' * 40 + output[40:], 0),
            ('wrong payload response', output[:output.find(b'\n') + 1] + b'x'
                + output[output.find(b'\n') + 2:], 0),
            ('extra response', output + reply(oids[0], bodies[oids[0]]), 0),
            ('failed process', output, 1),
        ):
            previous = dict(cache)
            with patch.object(repair.subprocess, 'run', return_value=subprocess.CompletedProcess(
                    ['git', 'cat-file', '--batch'], code, response, b'')):
                rejected(lambda: repair._prefetch_blobs(root, requests), label)
            assert cache == previous, label + ' inserted partial bytes'
        with patch.object(repair.subprocess, 'run', return_value=subprocess.CompletedProcess(
                ['git', 'cat-file', '--batch'], 0, output, b'')) as process:
            repair._prefetch_blobs(root, requests + requests)
            repair._prefetch_blobs(root, requests)
            assert process.call_count == 1
            assert process.call_args.args[0] == ['git', 'cat-file', '--batch']
            assert process.call_args.kwargs['input'] == ('\n'.join(oids) + '\n').encode()
        assert all(cache[(str(root.resolve()), oid)] == bodies[oid] for oid in oids)
        previous = dict(cache)
        for request in (('HEAD', paths[0]), (repair.C_R, 'src/core/')):
            rejected(lambda: repair._prefetch_blobs(root, (request,)), 'unadopted prefetch input')
            assert cache == previous
        def executable(where, ref):
            value = native_tree(where, ref)
            if ref == repair.C_R:
                value[paths[0]] = ('100755', *value[paths[0]][1:])
            return value
        with patch.object(campaign, '_tree', side_effect=executable):
            rejected(lambda: campaign.raw_bytes(root, repair.C_R, paths[0]), 'prefetched mode still checked')
        with patch.object(repair, '_tree', side_effect=executable):
            rejected(lambda: repair._prefetch_blobs(root, requests), 'cached prefetch mode still checked')
        assert cache == previous
        shared = 'include/core/config_button_validation.hpp'
        repair._prefetch_blobs(root, ((repair.C_R, shared),))
        assert native_tree(root, repair.C_R)[shared][2] == native_tree(root, campaign.C)[shared][2]
        def unsafe_second_ref(where, ref):
            value = native_tree(where, ref)
            if ref == campaign.C:
                value[shared] = ('100755', *value[shared][1:])
            return value
        previous = dict(cache)
        with patch.object(campaign, '_tree', side_effect=unsafe_second_ref):
            rejected(lambda: campaign.raw_bytes(root, campaign.C, shared), 'shared blob unsafe second ref')
        with patch.object(repair, '_tree', side_effect=unsafe_second_ref):
            rejected(lambda: repair._prefetch_blobs(root, ((campaign.C, shared),)), 'shared prefetch unsafe second ref')
        assert cache == previous
    exercise()
    assert campaign._blob_bytes_cache.get() is None
    rejected(lambda: repair._prefetch_blobs(root, requests), 'prefetch outside invocation')


def repaired_contract_tests(directory: Path) -> None:
    """Actual four phases and rejection controls in disposable Git repositories."""
    import glyph_campaign_transition as campaign
    import glyph_c020_abi_repair_transition as repair
    repaired_blob_prefetch_tests(ROOT)
    historical = directory / 'repair-original-historical'
    run(ROOT, 'git', 'clone', '--quiet', '--no-local', str(ROOT), str(historical))
    run(historical, 'git', 'switch', '--detach', 'caf0718472c7752c78838be6f1d48b56932d90b9')
    before, after = campaign.source_contract(historical)
    assert campaign.authenticate(historical)['contract'] == 'original037'
    assert campaign.authenticate_original(historical)['phase'] == 'BASELINE'
    # The generator asserts source-free B_R/G, source-free R/E, repaired candidate
    # and accepted phases before returning its explicitly synthetic accepted tip.
    root, record = make_synthetic_accepted_fixture(directory, repaired=True)
    target = run(root, 'git', 'rev-parse', 'HEAD').strip()
    proof = campaign.authenticate(root)
    assert proof['phase'] == 'ACCEPTED_TRANSITION' and proof['contract'] == 'c020_abi_repair'
    assert proof['candidate'] == repair.C_R and repair.C_R in proof['object_roots']
    assert repair.validate_accepted_transition(root, record, target) == record['build']
    assert campaign.critical_tree(root, record['review_commit']) == before
    assert campaign.critical_tree(root, record['evidence_commit']) == before
    assert not campaign.ancestor(root, record['build'], record['review_commit'])
    assert not campaign.ancestor(root, record['build'], record['evidence_commit'])
    # Host consumer mains share immutable reads, but every later live edit still rejects.
    campaign._proof_invocation(accepted_live_input_tests)(root)
    assert campaign._tree_inventory_cache.get() is None and campaign._blob_bytes_cache.get() is None
    protocol = root / repair.PROTOCOL
    protocol_bytes = protocol.read_bytes()
    try:
        protocol.write_bytes(protocol_bytes + b'\nrejected immutable accepted metadata\n')
        with patch.object(repair, 'source_contract', wraps=repair.source_contract) as source_proof:
            rejected(lambda: campaign.authenticate(root), 'early accepted metadata substitution')
            assert not source_proof.called
    finally:
        protocol.write_bytes(protocol_bytes)
    # A caller already in accepted phase must still produce source-free G/R/E.
    with tempfile.TemporaryDirectory(prefix='gp-val043-accepted-caller-') as nested_dir:
        with patch.object(sys.modules[__name__], 'ROOT', root):
            nested, nested_record = make_synthetic_accepted_fixture(Path(nested_dir), repaired=True)
        assert campaign.critical_tree(nested, nested_record['review_commit']) == before
        assert campaign.critical_tree(nested, nested_record['evidence_commit']) == before
        assert campaign.authenticate(nested)['phase'] == 'ACCEPTED_TRANSITION'
    # Exact tuple/source/ABI/mode/authority substitution must fail at immutable reads.
    native_git = repair._git
    for label, command, replacement in (
        ('CR parent', ('rev-list', '--parents', '-n', '1', repair.C_R), b'0' * 40),
        ('CR tree', ('rev-parse', repair.C_R + '^{tree}'), b'0' * 40),
        ('raw11', ('diff-tree', '-r', '--no-renames', '--raw', '-z', repair.B_R, repair.C_R), b'forged'),
        ('receipt lineage', ('rev-list', '--parents', '-n', '1', repair.RECEIPT), b'0' * 40),
    ):
        def changed_git(where, *args):
            return replacement if args == command else native_git(where, *args)
        with patch.object(repair, '_git', side_effect=changed_git):
            rejected(lambda: repair.source_contract(root), label)
    native_bytes = repair.raw_bytes
    for ref, path in ((repair.C_R, 'src/core/config_button_validation.cpp'),
                      (repair.C_R, 'tools/fixtures/gp_config020_button_validation/abi_probe.cpp'),
                      (repair.HANDOFF_R, campaign.QUEUE),
                      (repair.PACKET, 'docs/planning/portfolio_20261003_1256.md')):
        def changed_bytes(where, revision, name):
            raw = native_bytes(where, revision, name)
            return raw + b'forged' if (revision, name) == (ref, path) else raw
        with patch.object(repair, 'raw_bytes', side_effect=changed_bytes):
            rejected(lambda: repair.source_contract(root), 'immutable blob ' + path)
    native_tree = repair._tree
    def executable_candidate(where, revision):
        value = native_tree(where, revision)
        if revision == repair.C_R:
            path = 'src/core/config_button_validation.cpp'
            value[path] = ('100755', *value[path][1:])
        return value
    with patch.object(repair, '_tree', side_effect=executable_candidate):
        rejected(lambda: repair.source_contract(root), 'repaired candidate mode substitution')
    host = root / 'tools/check_glyph_gp_config020_button_validation.py'
    host_bytes = host.read_bytes()
    try:
        host.write_bytes(host_bytes + b'\n# substituted reviewed host\n')
        rejected(lambda: campaign.authenticate(root), 'reviewed repaired host substitution')
    finally:
        host.write_bytes(host_bytes)
    for path in (repair.MAPPING, repair.TRANSITIONS):
        file = root / path
        original_bytes = file.read_bytes()
        mode = file.stat().st_mode
        try:
            file.write_bytes(original_bytes + b'\n')
            rejected(lambda: campaign.authenticate(root), 'fixture substitution ' + path)
            file.write_bytes(original_bytes)
            file.chmod(mode | 0o111)
            rejected(lambda: campaign.authenticate(root), 'executable fixture ' + path)
        finally:
            file.write_bytes(original_bytes)
            file.chmod(mode)
    mapping = root / repair.MAPPING
    original_bytes = mapping.read_bytes()
    for change in (lambda x: dict(x, bypass=True),
                   lambda x: dict(x, candidate=dict(x['candidate'], candidate='0' * 40)),
                   lambda x: dict(x, authority=dict(x['authority'], adoption='0' * 40)),
                   lambda x: dict(x, host_execution_sha256='0' * 64)):
        try:
            mapping.write_text(json.dumps(change(json.loads(original_bytes))))
            rejected(lambda: campaign.authenticate(root), 'literal mapping identity/ABI substitution')
        finally:
            mapping.write_bytes(original_bytes)
    for key, value in (('candidate', campaign.C), ('parent', repair.B_R), ('tree', '0' * 40),
                       ('review_commit', record['evidence_commit']),
                       ('review_commit', record['build']),
                       ('evidence_commit', record['build']),
                       ('evidence_commit', record['integration']),
                       ('integration', record['review_commit'])):
        rejected(lambda: repair.validate_accepted_transition(root, dict(record, **{key: value}), target), key)
    native_item = repair.item
    for which, key, value in (
        (record['review_commit'], 'status', 'READY'),
        (record['review_commit'], 'candidate_git_sha', '0' * 40),
        (record['review_commit'], 'firmware_artifact_sha256', 'b' * 64),
        (record['evidence_commit'], 'hardware_result', 'FAIL'),
        (record['evidence_commit'], 'hardware_evidence_gaps', ['missing physical row']),
        (record['evidence_commit'], 'hardware_evidence_record', 'git-json:' + campaign.C + ':' + repair.EVIDENCE),
        (target, 'status', 'REVIEW'),
    ):
        def changed_item(where, revision, order):
            value_item = native_item(where, revision, order)
            return dict(value_item, **{key: value}) if revision == which else value_item
        with patch.object(repair, 'item', side_effect=changed_item):
            rejected(lambda: repair.validate_accepted_transition(root, record, target), key)
    catalog = root / repair.TRANSITIONS
    catalog_bytes = catalog.read_bytes()
    try:
        catalog.unlink()
        rejected(lambda: campaign.authenticate(root), 'missing repaired accepted catalog')
        catalog.write_text('{"schema_version":1,"accepted_transitions":[]}\n')
        rejected(lambda: campaign.authenticate(root), 'empty repaired accepted catalog')
    finally:
        catalog.write_bytes(catalog_bytes)
    downgraded = campaign.item(root, target, 'GP-CONFIG-020')
    downgraded.update(status='REVIEW', hardware_result=None, hardware_evidence_record=None,
                      hardware_evidence_dependency_satisfied=None)
    run(root, 'git', 'switch', '-c', 'synthetic-repair-downgrade')
    write_queue_item(root, downgraded)
    catalog.write_text('{"schema_version":1,"accepted_transitions":[]}\n')
    fixture_commit(root, 'erase repaired accepted queue/catalog')
    rejected(lambda: campaign.authenticate(root), 'committed repaired acceptance downgrade')
    run(root, 'git', 'switch', '--detach', target)
    run(root, 'git', 'switch', '-c', 'synthetic-repair-ours', record['build'])
    run(root, 'git', 'merge', '--no-ff', '-s', 'ours', '--no-edit', target)
    rejected(lambda: campaign.authenticate(root), 'second-parent repaired acceptance concealment')
    print('GP-VAL-043 four actual Git phases and mandatory identity/source/ABI/acceptance negatives PASS; SYNTHETIC TEST ONLY')


PRESERVED_E = '84e999693c5ef058c3a116c1632baa818add6ddb'
ACTUAL_R = '040735f6916c7a77924ef53f1b4a873281f2cb7f'
ACTUAL_F = '7db4f447d5e796367071b7143fa6c9274c70ae5e'


def make_processor_fixture(directory: Path, *, git_reference: bool = False) -> tuple[Path, dict]:
    """Replay preserved native bytes in disposable source-free governance only.

    This checkpoint is deliberately returned BEFORE any candidate integration.
    It preserves the original failed E object and adds no hardware observation.
    """
    import glyph_campaign_transition as campaign
    import glyph_c020_abi_repair_transition as repair
    root = directory.resolve() / 'processor-contract'
    run(ROOT, 'git', 'clone', '--quiet', '--no-local', str(ROOT), str(root))
    run(root, 'git', 'fetch', '--quiet', '--no-tags', '--no-write-fetch-head',
        str(ROOT), *sorted(repair.ROOTS | {PRESERVED_E, ACTUAL_R, ACTUAL_F}))
    run(root, 'git', 'config', 'user.name', 'Disposable GP-VAL-044 validation')
    run(root, 'git', 'config', 'user.email', 'validation@example.invalid')
    # ROOT can be I during a phase aggregate. Its source is never copied into E.
    run(root, 'git', 'switch', '--detach', repair.PROCESSOR_ADOPTION)
    excluded = {campaign.TRANSITIONS, repair.TRANSITIONS, repair.PROTOCOL,
                repair.EVIDENCE, 'docs/calibration/gp_config_020_hardware_result.md',
                campaign.QUEUE, 'docs/AGENT_CONTEXT.md', 'docs/CURRENT_STATE.md', 'docs/ROADMAP.md'}
    for path in sorted(repair.GOVERNANCE_PATHS - repair.PROOF_PATHS - excluded):
        source = ROOT / path
        if source.is_file():
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    G = fixture_commit(root, 'reviewed source-free044 validation overlay')
    assert campaign.critical_tree(root, G) == campaign.critical_tree(root, repair.B_R)
    assert campaign.authenticate(root)['phase'] == 'BASELINE'
    result_path = 'docs/calibration/gp_config_020_hardware_result.md'
    for path, digest in ((repair.EVIDENCE, '39a3977fbbc0b4d2db4f1187eba7d233de5056faceae47b734b2068f26051d42'),
                         (result_path, '9e69b3fc87366b9c61174df4a8c9865603ce95b295cbeaefcc9cbd81bf1f15d5')):
        data = campaign.raw_bytes(root, PRESERVED_E, path)
        assert hashlib.sha256(data).hexdigest() == digest
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(data)
    payload = fixture_commit(root, 'immutable native git-json payload before processor') if git_reference else None
    accepted = campaign.item(root, G, 'GP-CONFIG-020')
    previous = campaign.item(root, PRESERVED_E, 'GP-CONFIG-020')
    for key in ('status', 'hardware_result', 'hardware_evidence_record',
                'hardware_evidence_dependency_satisfied', 'hardware_evidence_gaps'):
        accepted[key] = previous[key]
    if git_reference:
        accepted['hardware_evidence_record'] = 'git-json:' + payload + ':' + repair.EVIDENCE
    write_queue_item(root, accepted)
    # Preserve current queue authority while deriving only the coupled pending
    # count/signal and status mirrors for this private processor checkpoint.
    state = campaign.queue(root, 'HEAD')
    state['items'] = [accepted if x['id'] == 'GP-CONFIG-020' else x for x in state['items']]
    state['runway']['hardware_pending'] = sum(x['status'] == 'HARDWARE_TEST_REQUIRED' for x in state['items'])
    if not state['runway']['hardware_pending']:
        state['signals'] = [x for x in state['signals'] if x != 'HARDWARE_TEST_REQUIRED']
    queue_path = root / campaign.QUEUE
    text = queue_path.read_text()
    text = re.sub(r'(<!-- queue-state:start -->\s*```json\s*).*?(\s*```\s*<!-- queue-state:end -->)',
                  lambda m: m[1] + json.dumps(state, indent=2) + m[2], text, flags=re.S)
    queue_path.write_text(text)
    for path in (campaign.QUEUE, 'docs/AGENT_CONTEXT.md', 'docs/CURRENT_STATE.md', 'docs/ROADMAP.md'):
        file = root / path
        text = file.read_text()
        def marker(match):
            value = json.loads(match[2])
            value['hardware_pending'] = state['runway']['hardware_pending']
            return match[1] + json.dumps(value, separators=(',', ':')) + match[3]
        text = re.sub(r'(<!-- current-runway:start -->\s*)(.*?)(\s*<!-- current-runway:end -->)',
                      marker, text, flags=re.S)
        text = re.sub(r'(Hardware-pending: )\d+', lambda m: m[1] + str(state['runway']['hardware_pending']), text)
        file.write_text(text)
    E = fixture_commit(root, 'preserved native payload source-free processor checkpoint')
    record = dict(work_order='GP-CONFIG-020', candidate=repair.C_R, build=ACTUAL_F,
                  parent='de36d24422a67e8be7992217856c76e8420a71f6',
                  tree='4b5b63ce56219a508e2b71745438a609dd5661c3',
                  review_commit=ACTUAL_R, evidence_commit=E)
    assert not campaign.ancestor(root, ACTUAL_F, E)
    return root, record


def processor_contract_tests(directory: Path) -> None:
    """Actual pinned R/F, standalone E and retained E before source integration."""
    from dataclasses import replace
    import glyph_campaign_transition as campaign
    import glyph_c020_abi_repair_transition as repair
    import glyph_checker_context as context
    root, record = make_processor_fixture(directory)
    E = record['evidence_commit']
    proof = campaign.authenticate(root)
    assert proof['phase'] == 'SOURCE_FREE_PROCESSOR'
    assert proof['critical_paths'] == frozenset()
    metadata = frozenset((repair.EVIDENCE, 'docs/calibration/gp_config_020_hardware_result.md'))
    assert proof['accepted_metadata_paths'] == metadata
    assert {ACTUAL_R, ACTUAL_F, E} <= proof['object_roots']
    processor = repair.validate_processor_transition(root, record, E)
    assert processor['evidence_commit'] == E and processor['evidence_root'] == E
    raw_context = context.collect_checker_context(repo_root=root, base=repair.PROCESSOR_ADOPTION)
    protected = 'HAL/pico/src/comms/ConfiguratorBackend.cpp'
    # A metadata exemption must never remove candidate/protected source from
    # any of the three inventories even when the input context includes it.
    probe = replace(raw_context, committed_paths=raw_context.committed_paths | {protected},
                    staged_paths=frozenset({protected}), unstaged_paths=frozenset({protected}))
    filtered = context.authenticated_campaign_context(probe)
    assert protected in filtered.committed_paths & filtered.staged_paths & filtered.unstaged_paths
    assert not metadata & filtered.changed_paths
    historical = campaign.raw_bytes(root, campaign.B, protected)
    assert campaign.verify_current_source(root, protected, hashlib.sha256(historical).hexdigest()) == historical
    source = root / protected
    original_source = source.read_bytes()
    try:
        source.write_bytes(campaign.raw_bytes(root, repair.C_R, protected))
        rejected(lambda: campaign.verify_current_source(root, protected,
                 hashlib.sha256(historical).hexdigest()), 'processor candidate source overlay')
    finally:
        source.write_bytes(original_source)
    # Native malformed schema, row, dependency and immutable-reference controls
    # use committed source-free snapshots; no helper/schema mock can create PASS.
    baseline_item = campaign.item(root, E, 'GP-CONFIG-020')
    for label, updates in (
        ('processor downgrade', dict(status='HARDWARE_TEST_REQUIRED', hardware_result=None)),
        ('processor dependency', dict(hardware_evidence_dependency_satisfied=False)),
        ('processor gaps', dict(hardware_evidence_gaps=['missing'])),
        ('candidate identity', dict(candidate_git_sha='0' * 40)),
        ('artifact identity', dict(firmware_artifact_sha256='0' * 64)),
        ('evidence reference', dict(hardware_evidence_record='git-json:' + ACTUAL_R + ':' + repair.EVIDENCE)),
    ):
        run(root, 'git', 'switch', '--detach', E)
        write_queue_item(root, dict(baseline_item, **updates))
        fixture_commit(root, label)
        rejected(lambda: campaign.authenticate(root), label)
    run(root, 'git', 'switch', '--detach', E)
    for path in sorted(metadata):
        file = root / path
        original, mode = file.read_bytes(), file.stat().st_mode
        try:
            file.write_bytes(original + b'\nsubstitution\n')
            rejected(lambda: campaign.authenticate(root), 'dirty processor metadata ' + path)
            run(root, 'git', 'add', '--', path)
            file.write_bytes(original)
            rejected(lambda: campaign.authenticate(root), 'staged processor metadata ' + path)
        finally:
            file.write_bytes(original)
            run(root, 'git', 'add', '--', path)
        try:
            file.chmod(mode | 0o111)
            rejected(lambda: campaign.authenticate(root), 'executable processor metadata')
        finally:
            file.chmod(mode)
        try:
            file.unlink()
            file.symlink_to('../GP_CONFIG_020_HARDWARE_PROTOCOL.md')
            rejected(lambda: campaign.authenticate(root), 'symlink processor metadata')
        finally:
            file.unlink()
            file.write_bytes(original)
            file.chmod(mode)
    for path in (repair.EVIDENCE + '.bak', 'docs/calibration/gp_config_020_hardware_result.md.bak'):
        alias = root / path
        try:
            alias.write_text('metadata alias\n')
            rejected(lambda: campaign.authenticate(root), 'processor alias ' + path)
        finally:
            alias.unlink()
    ignored_path = repair.EVIDENCE + '.bak'
    ignored = root / ignored_path
    exclude = root / '.git/info/exclude'
    previous_exclude = exclude.read_bytes()
    try:
        exclude.write_bytes(previous_exclude + ('\n' + ignored_path + '\n').encode())
        ignored.write_text('ignored adjacent processor metadata\n')
        rejected(lambda: campaign.authenticate(root), 'ignored processor metadata')
    finally:
        ignored.unlink()
        exclude.write_bytes(previous_exclude)
    for key, value in (('build', campaign.C), ('parent', repair.B_R), ('tree', '0' * 40),
                       ('review_commit', E), ('evidence_commit', ACTUAL_F)):
        rejected(lambda: repair.validate_processor_transition(root, dict(record, **{key: value}), E), key)
    # Missing schema/required physical rows and evidence erasure cannot be
    # legitimized by changing a digest. The authenticated actual digest stays
    # pinned while each malformed payload is committed in its own descendant.
    evidence = root / repair.EVIDENCE
    original_evidence = evidence.read_bytes()
    for label, change in (
        ('missing evidence schema', lambda x: {k: v for k, v in x.items() if k != 'schema_version'}),
        ('missing hardware row', lambda x: dict(x, steps=x['steps'][:-1])),
        ('empty hardware rows', lambda x: dict(x, steps=[])),
    ):
        run(root, 'git', 'switch', '--detach', E)
        evidence.write_text(json.dumps(change(json.loads(original_evidence)), indent=2) + '\n')
        fixture_commit(root, label)
        rejected(lambda: campaign.authenticate(root), label)
    run(root, 'git', 'switch', '--detach', E)
    evidence.unlink()
    fixture_commit(root, 'delete accepted native evidence')
    rejected(lambda: campaign.authenticate(root), 'committed processor evidence deletion')
    run(root, 'git', 'switch', '--detach', E)
    for catalog in (repair.TRANSITIONS, campaign.TRANSITIONS):
        file = root / catalog
        original = file.read_bytes()
        try:
            file.write_text(json.dumps(dict(schema_version=1, accepted_transitions=[dict(record, integration=E)])))
            rejected(lambda: campaign.authenticate(root), 'catalog supplied on source-free E')
        finally:
            file.write_bytes(original)
    G = run(root, 'git', 'rev-parse', E + '^').strip()
    run(root, 'git', 'switch', '-c', 'synthetic-hidden-invalid-processor', G)
    write_queue_item(root, dict(baseline_item, hardware_evidence_record=None))
    invalid_prior = fixture_commit(root, 'fabricated invalid earlier processor claim')
    run(root, 'git', 'switch', '--detach', E)
    run(root, 'git', 'merge', '--no-ff', '-s', 'ours', '--no-edit', invalid_prior)
    rejected(lambda: campaign.authenticate(root), 'hidden second-parent invalid processor claim')
    run(root, 'git', 'switch', '--detach', E)
    # Every later processor claim needs native work-order validation, even
    # when its exact accepted hardware tuple and immutable payload are intact.
    assert baseline_item['activation_requires_new_judgment'] is False
    assert dict(baseline_item, activation_requires_new_judgment=0) == baseline_item
    for label, updates in (
        ('later processor malformed schema', dict(title=None)),
        ('later processor integer for Boolean schema', dict(activation_requires_new_judgment=0)),
        ('source-free premature DONE', dict(status='DONE', done_evidence='SYNTHETIC prose only')),
    ):
        write_queue_item(root, dict(baseline_item, **updates))
        fixture_commit(root, label)
        rejected(lambda: campaign.authenticate(root), label)
        write_queue_item(root, baseline_item)
        fixture_commit(root, 'restore valid processor state after ' + label)
        rejected(lambda: campaign.authenticate(root), 'historical ' + label + ' after restoration')
        run(root, 'git', 'switch', '--detach', E)
    # A clean source-free descendant retains earliest E, exact evidence and
    # empty protected-source authority. It is still authenticated before I.
    descendant = fixture_commit(root, 'source-free retained processor descendant')
    retained = campaign.authenticate(root)
    assert retained['phase'] == 'SOURCE_FREE_PROCESSOR' and not retained['critical_paths']
    assert retained['evidence_commit'] == E and {ACTUAL_F, ACTUAL_R, E} <= retained['object_roots']
    assert repair.validate_processor_transition(root, record, descendant)['evidence_commit'] == E
    # Preserve the old code's actual mandatory rejection. Its immutable SHA
    # never becomes a label for the repaired overlay tested above.
    run(root, 'git', 'switch', '--detach', PRESERVED_E)
    old = run(root, sys.executable, '-B',
              'tools/check_glyph_runtime_config_webserial_device_write_source_authority.py',
              '--campaign-transition', expected=1)
    assert 'accepted phase lacks mandatory transition record' in old
    run(root, 'git', 'switch', '--detach', descendant)
    assert campaign.authenticate(root)['evidence_commit'] == E
    with tempfile.TemporaryDirectory(prefix='gp-val044-git-json-') as native_dir:
        native, native_record = make_processor_fixture(Path(native_dir), git_reference=True)
        native_proof = campaign.authenticate(native)
        payload = campaign.item(native, native_record['evidence_commit'], 'GP-CONFIG-020')['hardware_evidence_record'].split(':')[1]
        assert native_proof['evidence_root'] == payload != native_proof['evidence_commit']
        assert {payload, native_proof['evidence_commit'], ACTUAL_F, ACTUAL_R} <= native_proof['object_roots']
        assert campaign.ancestor(native, ACTUAL_R, payload)
        assert campaign.ancestor(native, payload, native_proof['evidence_commit'])
    synthetic_processor_tests(directory)
    print('GP-VAL-044 actual pinned standalone E/E descendant native proof and scope/metadata negatives PASS; disposable overlay only')


def native_integrated_public_api_tests(directory: Path, source_root: Path, record: dict) -> None:
    """External postcheckpoint regression on an already-composed actual I.

    Call only after all fifteen E/E-descendant mains passed before I was made.
    This function integrates no F and publishes no completion or acceptance.
    It validates native strict DONE mechanics only in a disposable descendant.
    """
    import glyph_campaign_transition as campaign
    import glyph_c020_abi_repair_transition as repair
    import check_glyph_agent_framework_docs as framework
    assert record['build'] == ACTUAL_F and record['review_commit'] == ACTUAL_R
    root = directory / 'native-I-public-api'
    run(source_root, 'git', 'clone', '--quiet', '--no-local', str(source_root), str(root))
    run(root, 'git', 'fetch', '--quiet', '--no-tags', '--no-write-fetch-head', str(ROOT),
        *sorted(repair.ROOTS | {PRESERVED_E, ACTUAL_F}))
    run(root, 'git', 'config', 'user.name', 'Disposable GP-VAL-044 native API proof')
    run(root, 'git', 'config', 'user.email', 'native-api@example.invalid')
    target = run(root, 'git', 'rev-parse', 'HEAD').strip()
    assert repair.validate_accepted_transition(root, record, target) == ACTUAL_F
    for key, value in (('build', campaign.C), ('review_commit', record['evidence_commit']),
                       ('evidence_commit', record['integration'])):
        rejected(lambda: repair.validate_accepted_transition(root, dict(record, **{key: value}), target),
                 'direct native accepted API ' + key)
    catalog = root / repair.TRANSITIONS
    original_catalog = catalog.read_bytes()
    try:
        catalog.write_text('{"schema_version":1,"accepted_transitions":[]}\n')
        rejected(lambda: repair.validate_accepted_transition(root, record, target),
                 'direct native accepted API requires genuine catalog')
    finally:
        catalog.write_bytes(original_catalog)
    accepted = campaign.item(root, target, 'GP-CONFIG-020')
    paths = run(root, 'git', 'diff', '--name-only', repair.B_R, repair.C_R).splitlines()
    completion = dict(schema_name=framework.COMPLETION_EVIDENCE_NAME,
                      schema_version=framework.COMPLETION_EVIDENCE_VERSION, mode='DIRECT_ANCESTRY',
                      implementation_base_sha=repair.B_R, reviewed_implementation_sha=repair.C_R,
                      prior_canonical_integration_sha=record['integration'], reviewed_changed_paths=sorted(paths),
                      independent_review_provenance='SYNTHETIC TEST ONLY: native schema mechanics',
                      validation_provenance='SYNTHETIC TEST ONLY: no published C020 completion')
    # Prove a structurally complete native DONE first, so malformed DONE
    # controls cannot pass through an unconditional refusal of every DONE.
    write_queue_item(root, dict(accepted, status='DONE', done_evidence=completion))
    valid_done = fixture_commit(root, 'native strict completion structural positive only')
    assert repair.validate_accepted_transition(root, record, valid_done) == ACTUAL_F
    assert campaign.authenticate(root)['phase'] == 'ACCEPTED_TRANSITION'
    for label, evidence in (
        ('prose DONE completion', 'SYNTHETIC prose-only completion'),
        ('forged DONE completion', dict(completion, implementation_base_sha='0' * 40)),
        ('Boolean DONE schema version', dict(completion, schema_version=True)),
    ):
        run(root, 'git', 'switch', '--detach', valid_done)
        write_queue_item(root, dict(accepted, status='DONE', done_evidence=evidence))
        invalid = fixture_commit(root, label)
        rejected(lambda: repair.validate_accepted_transition(root, record, invalid), label)
        rejected(lambda: campaign.authenticate(root), 'authenticated ' + label)
        write_queue_item(root, dict(accepted, status='DONE', done_evidence=completion))
        restored = fixture_commit(root, 'restore valid completion after ' + label)
        rejected(lambda: repair.validate_accepted_transition(root, record, restored), 'historical ' + label)
        rejected(lambda: campaign.authenticate(root), 'restored historical ' + label)
    print('GP-VAL-044 direct native accepted API and strict later DONE/history regressions PASS; disposable postcheckpoint only')


def synthetic_processor_tests(directory: Path) -> None:
    """Separately authenticated structural roots confer no production acceptance."""
    import glyph_campaign_transition as campaign
    import glyph_c020_abi_repair_transition as repair
    parent = directory / 'explicit-synthetic-roots'
    parent.mkdir()
    root, actual_record = make_processor_fixture(parent)
    actual_E = actual_record['evidence_commit']
    G = run(root, 'git', 'rev-parse', actual_E + '^').strip()
    run(root, 'git', 'switch', '--detach', G)
    run(root, 'git', 'merge', '--no-ff', '--no-edit', repair.C_R)
    P = run(root, 'git', 'rev-parse', 'HEAD').strip()
    F = fixture_commit(root, 'unbuilt synthetic F; no artifact or controller test')
    T = run(root, 'git', 'rev-parse', F + '^{tree}').strip()
    run(root, 'git', 'switch', '--detach', G)
    review = campaign.item(root, G, 'GP-CONFIG-020')
    digest = 'a' * 64
    locator = f'local_backups/hardware-artifacts/{F}/{digest}/firmware.uf2'
    review.update(candidate_git_sha=F, candidate_base_configurator_sha=P,
                  firmware_artifact_sha256=digest, preserved_firmware_artifact_locator=locator)
    protocol = (f'# SYNTHETIC TEST ONLY; no actual hardware or build\n\n'
        f'- Candidate Git SHA: `{F}`\n- Candidate tree: `{T}`\n'
        f'- Sole parent / authorized canonical base: `{P}`\n'
        f'- UF2 SHA-256: `{digest}`\n- UF2 size: `796160` bytes\n'
        f'- Preserved locator: `{locator}`\n'
        '- Fresh independent postimplementation review: PASS with no findings for the\n'
        '  exact candidate, build output, custody bytes, correspondence, and protocol.\n')
    (root / repair.PROTOCOL).write_text(protocol)
    write_queue_item(root, review)
    R = fixture_commit(root, 'source-free synthetic immutable review')
    evidence = json.loads(campaign.raw_bytes(root, PRESERVED_E, repair.EVIDENCE))
    for key in ('candidate_git_sha', 'candidate_base_configurator_sha',
                'firmware_artifact_sha256', 'preserved_firmware_artifact_locator'):
        evidence[key] = review[key]
    evidence['tester'] = 'SYNTHETIC TEST ONLY; no controller observations'
    evidence['preconditions'] = ['Synthetic validation only; no artifact or controller test.']
    for step in evidence['steps']:
        step['observed'] = 'SYNTHETIC TEST ONLY; no controller observation'
    evidence_bytes = (json.dumps(evidence, indent=2) + '\n').encode()
    (root / repair.EVIDENCE).write_bytes(evidence_bytes)
    result = (f'SYNTHETIC TEST ONLY; no controller acceptance\nHARDWARE_VALIDATED PASS\n'
              f'{F}\n{T}\n{P}\n{R}\n{digest}\n{locator}\n'
              f'{hashlib.sha256(protocol.encode()).hexdigest()}\n')
    (root / repair.RESULT).write_text(result)
    payload = fixture_commit(root, 'synthetic native payload before processor')
    accepted = dict(review, status='HARDWARE_VALIDATED', hardware_result='PASS',
                    hardware_evidence_dependency_satisfied=True, hardware_evidence_gaps=[],
                    hardware_evidence_record='git-json:' + payload + ':' + repair.EVIDENCE)
    write_queue_item(root, accepted)
    E = fixture_commit(root, 'source-free synthetic processor')
    record = dict(work_order='GP-CONFIG-020', candidate=repair.C_R, build=F, parent=P, tree=T,
                  review_commit=R, evidence_commit=E)
    pins = dict(review_commit=R, build=F, parent=P, tree=T, artifact_sha256=digest,
                artifact_size=796160, protocol_sha256=hashlib.sha256(protocol.encode()).hexdigest(),
                review_queue_sha256=hashlib.sha256(campaign.raw_bytes(root, R, campaign.QUEUE)).hexdigest(),
                evidence_sha256=hashlib.sha256(evidence_bytes).hexdigest(),
                result_sha256=hashlib.sha256(result.encode()).hexdigest(),
                authority_commit=repair.PROCESSOR_RECEIPT, authority_adoption=repair.PROCESSOR_ADOPTION)
    roots = repair.authenticate_processor_roots(root, pins)
    proof = repair.validate_processor_transition(root, record, E, structural_roots=roots)
    assert proof['evidence_root'] == payload and {F, R, E, payload} <= proof['object_roots']
    # Production has no synthetic-root flag: the same real Git graph must fail
    # its exact actual pin check, even though its structural proof is valid.
    rejected(lambda: campaign.authenticate(root), 'synthetic roots in production authenticator')
    for key, value in (('build', ACTUAL_F), ('parent', repair.B_R), ('tree', '0' * 40),
                       ('artifact_size', 796161),
                       ('review_commit', ACTUAL_R), ('protocol_sha256', '0' * 64),
                       ('review_queue_sha256', '0' * 64), ('authority_commit', R),
                       ('evidence_sha256', '0' * 64), ('result_sha256', '0' * 64)):
        def altered_proof():
            changed = repair.authenticate_processor_roots(root, dict(pins, **{key: value}))
            repair.validate_processor_transition(root, record, E, structural_roots=changed)
        rejected(altered_proof, 'synthetic root substitution ' + key)
    rejected(lambda: repair.authenticate_processor_roots(root, dict(pins, bypass=True)), 'extra synthetic-root field')
    rejected(lambda: repair.validate_processor_transition(ROOT, record, E, structural_roots=roots), 'root-bound structural proof')


def legacy_applicability_tests(directory: Path) -> None:
    """Keep legacy positive scope and exact historical identity coverage separate."""
    canonical = Path(directory) / "canonical"
    run(ROOT, "git", "clone", "--quiet", "--no-local", str(ROOT), str(canonical))
    run(canonical, "git", "switch", "--detach", BASE)
    shutil.copyfile(ROOT / CHECKER, canonical / CHECKER)
    shutil.copyfile(ROOT / CLASSIFIER, canonical / CLASSIFIER)
    shutil.copyfile(ROOT / CAMPAIGN, canonical / CAMPAIGN)
    run(canonical, "python3", CHECKER)
    run(canonical, "git", "config", "user.name", "GP-VAL-029 self-test")
    run(canonical, "git", "config", "user.email", "gp-val-029@example.invalid")
    prebuild=canonical / "tools/check_glyph_prebuild_git_identity.py"
    prebuild.write_text(prebuild.read_text()+"\n# isolated legacy H1 validation self-test delta\n")
    run(canonical, "git", "add", "--", "tools/check_glyph_prebuild_git_identity.py")
    run(canonical, "git", "commit", "-m", "legacy prebuild correspondence positive")
    run(canonical, "python3", CHECKER)
    # A separate clone keeps the dirty-source case out of historical proof.
    historical = Path(directory) / "historical"
    run(ROOT, "git", "clone", "--quiet", "--no-local", str(ROOT), str(historical))
    run(historical, "git", "switch", "--detach", CANDIDATE)
    run(historical, "git", "switch", "-c", "glyph/gp-config-010-current-canonical-integration")
    shutil.copyfile(ROOT / CHECKER, historical / CHECKER)
    shutil.copyfile(ROOT / CLASSIFIER, historical / CLASSIFIER)
    shutil.copyfile(ROOT / CAMPAIGN, historical / CAMPAIGN)
    run(historical, "python3", CHECKER, "--historical")
    run(historical, "git", "switch", "-c", "gp-val-029-wrong-branch")
    run(historical, "python3", CHECKER, "--historical", expected=1)
    run(historical, "git", "switch", "glyph/gp-config-010-current-canonical-integration")
    run(historical, "git", "config", "user.name", "GP-VAL-029 self-test")
    run(historical, "git", "config", "user.email", "gp-val-029@example.invalid")
    (historical / "docs/ROADMAP.md").write_text((historical / "docs/ROADMAP.md").read_text() + "\nnegative parent\n")
    run(historical, "git", "add", "docs/ROADMAP.md")
    run(historical, "git", "commit", "-m", "gp-val-029-wrong-parent")
    run(historical, "python3", CHECKER, "--historical", expected=1)
    run(historical, "python3", "-c", "import sys; sys.path.insert(0, 'tools'); import glyph_hardware_correspondence as c; c.NON_BEHAVIORAL_PATHS = c.NON_BEHAVIORAL_PATHS | {'platformio.ini'}; assert c.classify_path('platformio.ini') == 'CRITICAL'")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="gp-val-029-") as directory:
        root = Path(directory) / "repo"
        run(ROOT, "git", "clone", "--quiet", "--no-local", str(ROOT), str(root))
        run(root, "git", "config", "user.name", "GP-VAL-029 self-test")
        run(root, "git", "config", "user.email", "gp-val-029@example.invalid")
        run(root, "python3", CHECKER)
        campaign_contract_tests(Path(directory))
        repaired_contract_tests(Path(directory))
        # Reuse the already audited immutable root/SHA caches only within this
        # test invocation. Every live dirty/index/metadata input is still read
        # anew by each authenticator call and its rejection controls above.
        import glyph_campaign_transition as campaign
        campaign._proof_invocation(processor_contract_tests)(Path(directory))
        assert campaign._tree_inventory_cache.get() is None and campaign._blob_bytes_cache.get() is None
        commit_change(root, "docs/ROADMAP.md", "\nGP-VAL-029 isolated scope control.\n", "gp-val-029-positive")
        run(root, "python3", CHECKER)
        commit_change(root, "tools/check_glyph_prebuild_git_identity.py", "\n# isolated H1 validation self-test delta\n", "gp-val-029-ready-prerequisite")
        # Legacy correspondence permits this path; the adopted campaign has a
        # narrower finite inventory and must continue to reject it.
        result=run(root, "python3", CHECKER, expected=1)
        assert 'unreviewed governance/host delta' in result
        for label, path, data in (
            ("unknown-doc", "docs/unknown_gp_val_029.md", "unknown\n"),
            ("unknown-tool", "tools/unknown_gp_val_029.py", "# unknown\n"),
            ("critical-build", "platformio.ini", "\n; negative\n"),
            ("mode-source", "src/core/mode_selection.cpp", "\n// negative\n"),
            ("table-source", "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp", "\n// negative\n"),
        ):
            commit_change(root, path, data, "gp-val-029-" + label)
            run(root, "python3", CHECKER, expected=1)
        run(root, "git", "switch", "--detach", SELF_HEAD)
        with (root / "src/core/mode_selection.cpp").open("a") as stream:
            stream.write("\n// dirty negative\n")
        run(root, "python3", CHECKER, expected=1)
        legacy_applicability_tests(Path(directory))
    print("gp_val_029_semantic_applicability: PASS; canonical, unrelated descendant, historical identity and negatives")


if __name__ == "__main__":
    main()
