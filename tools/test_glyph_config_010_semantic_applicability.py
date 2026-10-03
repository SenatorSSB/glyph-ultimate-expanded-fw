#!/usr/bin/env python3
"""Isolated positive and negative checks for GP-CONFIG-010 proof applicability."""
from __future__ import annotations

import os
import copy
import json
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


def make_synthetic_accepted_fixture(directory: Path) -> tuple[Path, dict]:
    """Disposable real Git evidence chronology; never physical acceptance.

    Call only with a fresh temp directory. Returned repository can run actual
    consumers/aggregates after their normal deterministic manifest/census update.
    This function performs no firmware build, artifact creation, or publication.
    """
    import glyph_campaign_transition as campaign
    root=directory.resolve()/'accepted-contract'
    run(ROOT,'git','clone','--quiet','--no-local',str(ROOT),str(root))
    run(root,'git','config','user.name','Synthetic GP-VAL-037 tests')
    run(root,'git','config','user.email','synthetic@example.invalid')
    G=run(root,'git','rev-parse','HEAD').strip()
    run(root,'git','switch','-c','synthetic-candidate')
    run(root,'git','merge','--no-ff','--no-edit',campaign.C)
    P=run(root,'git','rev-parse','HEAD').strip()
    F=fixture_commit(root,'unbuilt candidate identity; no artifact exists')
    T=run(root,'git','rev-parse',F+'^{tree}').strip()
    run(root,'git','switch','--detach',G)
    run(root,'git','switch','-c','synthetic-evidence')
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
    record=dict(work_order='GP-CONFIG-020',candidate=campaign.C,build=F,parent=P,tree=T,
                review_commit=R,evidence_commit=E,integration=I)
    (root/campaign.TRANSITIONS).write_text(json.dumps(dict(schema_version=1,accepted_transitions=[record]),indent=2)+'\n')
    fixture_commit(root,'synthetic accepted transition catalog')
    return root,record


def accepted_contract_tests(directory: Path) -> None:
    import glyph_campaign_transition as campaign
    root,record=make_synthetic_accepted_fixture(directory)
    target=run(root,'git','rev-parse','HEAD').strip()
    assert campaign.authenticate(root)['phase']=='ACCEPTED_TRANSITION'
    assert campaign.validate_accepted_transition(root,record,target)==record['build']
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


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="gp-val-029-") as directory:
        root = Path(directory) / "repo"
        run(ROOT, "git", "clone", "--quiet", "--no-local", str(ROOT), str(root))
        run(root, "git", "config", "user.name", "GP-VAL-029 self-test")
        run(root, "git", "config", "user.email", "gp-val-029@example.invalid")
        run(root, "python3", CHECKER)
        campaign_contract_tests(Path(directory))
        commit_change(root, "docs/ROADMAP.md", "\nGP-VAL-029 isolated scope control.\n", "gp-val-029-positive")
        run(root, "python3", CHECKER)
        commit_change(root, "tools/check_glyph_prebuild_git_identity.py", "\n# isolated H1 validation self-test delta\n", "gp-val-029-ready-prerequisite")
        run(root, "python3", CHECKER)
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
        canonical = Path(directory) / "canonical"
        run(ROOT, "git", "clone", "--quiet", "--no-local", str(ROOT), str(canonical))
        run(canonical, "git", "switch", "--detach", BASE)
        shutil.copyfile(ROOT / CHECKER, canonical / CHECKER)
        shutil.copyfile(ROOT / CLASSIFIER, canonical / CLASSIFIER)
        shutil.copyfile(ROOT / CAMPAIGN, canonical / CAMPAIGN)
        run(canonical, "python3", CHECKER)
        # A separate clone keeps the dirty-source case out of historical proof.
        historical = Path(directory) / "historical"
        run(ROOT, "git", "clone", "--quiet", "--no-local", str(ROOT), str(historical))
        run(historical, "git", "switch", "--detach", CANDIDATE)
        run(historical, "git", "switch", "-c", "glyph/gp-config-010-current-canonical-integration")
        shutil.copyfile(ROOT / CHECKER, historical / CHECKER)
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
    print("gp_val_029_semantic_applicability: PASS; canonical, unrelated descendant, historical identity and negatives")


if __name__ == "__main__":
    main()
