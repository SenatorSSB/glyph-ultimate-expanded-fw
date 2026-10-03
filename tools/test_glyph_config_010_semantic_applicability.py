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

    # Pure consumer unit controls: all records remain in memory. These mocks
    # test acceptance plumbing, never hardware evidence or aggregate acceptance.
    F, P, T, R, E, I, H = (character * 40 for character in "abcdef1")
    record = dict(work_order="GP-CONFIG-020", candidate=campaign.C, build=F,
                  parent=P, tree=T, review_commit=R, evidence_commit=E, integration=I)
    review = dict(candidate_git_sha=F, candidate_base_configurator_sha=P,
                  done_evidence="independent review of " + F)
    accepted = dict(review, status="HARDWARE_VALIDATED", hardware_result="PASS", hardware_evidence_gaps=[])
    def synthetic_git(where, *args):
        if args == ("rev-list", "--parents", "-n", "1", F):
            return (F + " " + P).encode()
        if args == ("rev-parse", F + "^{tree}"):
            return T.encode()
        raise AssertionError("unexpected synthetic Git query: " + repr(args))
    def synthetic_item(where, ref, order):
        assert order == "GP-CONFIG-020"
        return review if ref == R else accepted
    with patch.object(campaign, "_git", side_effect=synthetic_git), \
         patch.object(campaign, "ancestor", return_value=True), \
         patch.object(campaign, "verify_correspondence") as correspondence, \
         patch.object(campaign, "item", side_effect=synthetic_item), \
         patch.object(framework, "validate_work_order") as work_order, \
         patch.object(framework, "validate_evidence_record") as evidence:
        assert campaign.validate_accepted_transition(root, record, H) == F
        assert correspondence.call_count == 2 and work_order.call_count == evidence.call_count == 1
        for key, value in (("work_order", "GP-CONFIG-021"), ("work_order", "GP-CONFIG-014"),
                           ("work_order", "GP-CONFIG-017"), ("candidate", "0" * 40),
                           ("parent", "0" * 40), ("tree", "0" * 40), ("build", "HEAD")):
            altered = dict(record, **{key: value})
            rejected(lambda: campaign.validate_accepted_transition(root, altered, H), "accepted " + key + "=" + value)
        rejected(lambda: campaign.validate_accepted_transition(root, dict(record, bypass=True), H), "extra record field")
        for target, key, value in ((review, "done_evidence", "no review identity"),
                                   (review, "candidate_git_sha", "0" * 40),
                                   (accepted, "hardware_result", "FAIL"),
                                   (accepted, "hardware_evidence_gaps", ["missing test"]),
                                   (accepted, "candidate_git_sha", "0" * 40),
                                   (accepted, "status", "REVIEW")):
            saved = copy.deepcopy(target[key])
            try:
                target[key] = value
                rejected(lambda: campaign.validate_accepted_transition(root, record, H), "accepted " + key)
            finally:
                target[key] = saved
        with patch.object(campaign, "ancestor", return_value=False):
            rejected(lambda: campaign.validate_accepted_transition(root, record, H), "missing accepted ancestry")
        with patch.object(framework, "validate_evidence_record", side_effect=ValueError("invalid exact evidence")):
            rejected(lambda: campaign.validate_accepted_transition(root, record, H), "processor validation rejection")
    print("GP-VAL-037 contract negatives PASS; accepted positive is synthetic unit coverage only")


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
