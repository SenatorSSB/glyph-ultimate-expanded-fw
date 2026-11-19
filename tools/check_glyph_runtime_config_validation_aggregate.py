#!/usr/bin/env python3
"""Focused adversarial tests for the read-only runtime-config aggregate runner.

The tests use an isolated temporary Git repository and replace only the
runner's module-local root and manifest paths.  They never execute a checker
from this repository or alter the committed manifest.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from unittest import mock
from pathlib import Path
from typing import Any


RUNNER_PATH = Path(__file__).with_name("run_glyph_runtime_config_validation.py")
GENERATOR_PATH = Path(__file__).with_name("generate_glyph_checker_census.py")
REQUIRED = {
    "id",
    "path",
    "command",
    "category",
    "applicability",
    "branch_policy",
    "required_arguments",
    "mutation_risk",
    "source_dependencies",
    "load_bearing",
    "historical",
    "reason",
}


def run_git(root: Path, *args: str) -> None:
    completed = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")


def fresh_root(parent: Path) -> Path:
    root = parent.resolve() / "repo"
    root.mkdir()
    run_git(root, "init", "-b", "configurator")
    run_git(root, "config", "user.name", "aggregate adversarial test")
    run_git(root, "config", "user.email", "aggregate@example.invalid")
    (root / "docs/runtime_config/fixtures").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "README.md").write_text("test\n", encoding="utf-8")
    run_git(root, "add", "README.md")
    run_git(root, "commit", "-m", "baseline")
    run_git(root, "update-ref", "refs/remotes/origin/configurator", "HEAD")
    return root


def entry(
    checker_id: str,
    *,
    category: str = "baseline",
    applicability: str = "current",
    historical: bool = False,
    load_bearing: bool = True,
    mutation_risk: str = "none",
) -> dict[str, Any]:
    return {
        "id": checker_id,
        "path": f"tools/check_glyph_{checker_id}.py",
        "command": ["python3", f"tools/check_glyph_{checker_id}.py"],
        "category": category,
        "applicability": applicability,
        "branch_policy": "content_only",
        "required_arguments": [],
        "mutation_risk": mutation_risk,
        "source_dependencies": [],
        "load_bearing": load_bearing,
        "historical": historical,
        "reason": "temporary adversarial checker",
    }


def assert_manifest_failure(module: Any, root: Path, manifest: Path, needle: str) -> None:
    result, text = invoke(module, root, manifest, "--check-manifest")
    if result != 1 or needle not in text:
        raise AssertionError(f"manifest accepted invalid command contract: {needle}")


def write_checker(root: Path, checker: dict[str, Any], exit_code: int) -> None:
    path = root / checker["path"]
    path.write_text(f"raise SystemExit({exit_code})\n", encoding="utf-8")
    run_git(root, "add", checker["path"])


def refresh_census(root: Path) -> None:
    spec = importlib.util.spec_from_file_location("glyph_census_adversarial", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load census generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (root / "docs/runtime_config/fixtures/glyph_checker_census.json").write_text(
        module.rendered(module.generate(root)), encoding="utf-8"
    )


def write_manifest(root: Path, entries: list[dict[str, Any]], categories: list[str]) -> Path:
    manifest = root / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 4,
                "categories": categories,
                "entries": entries,
                "strong_signal_exclusions": [],
            }
        ),
        encoding="utf-8",
    )
    refresh_census(root)
    run_git(root, "add", "docs/runtime_config/fixtures/runtime_config_validation_manifest.json", "docs/runtime_config/fixtures/glyph_checker_census.json")
    run_git(root, "commit", "-m", "refresh manifest fixture")
    return manifest


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("glyph_aggregate_runner_adversarial", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load aggregate runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def invoke(module: Any, root: Path, manifest: Path, *arguments: str, census_path: Path | None = None) -> tuple[int, str]:
    original_root, original_manifest, original_census, original_argv = (
        module.ROOT,
        module.MANIFEST,
        module.CENSUS,
        sys.argv,
    )
    captured = io.StringIO()
    try:
        module.ROOT, module.MANIFEST = root, manifest
        module.CENSUS = census_path or root / "docs/runtime_config/fixtures/glyph_checker_census.json"
        sys.argv = [str(RUNNER_PATH), *arguments]
        with contextlib.redirect_stdout(captured):
            result = module.main()
    finally:
        module.ROOT, module.MANIFEST, module.CENSUS, sys.argv = (
            original_root,
            original_manifest,
            original_census,
            original_argv,
        )
    return result, captured.getvalue()


def payload(text: str) -> dict[str, Any]:
    return json.loads(text)



def isolation_contract_cases(module: Any) -> list[str]:
    """Behavioral probes use only disposable Git histories and short injected clocks."""
    passed = []
    with tempfile.TemporaryDirectory(prefix="glyph-isolation-contract-") as directory:
        parent = Path(directory)
        root = fresh_root(parent)
        module.ROOT = root
        probe = entry("isolation_probe")

        def install(source: str, entries=None) -> Path:
            write_checker(root, probe, 0)
            (root / probe["path"]).write_text(source, encoding="utf-8")
            run_git(root, "add", probe["path"])
            return write_manifest(root, entries or [probe], ["baseline"])

        def execute(manifest: Path, *args: str) -> dict[str, Any]:
            before = module.canonical_fingerprint(root)
            code, text = invoke(module, root, manifest, "--json", *args)
            report = payload(text)
            if before != module.canonical_fingerprint(root):
                raise AssertionError("aggregate changed disposable caller state")
            if report["canonical_proof"] != "MATCH" and report["failure_kind"] != "AGGREGATE_TIMEOUT":
                raise AssertionError(f"final canonical proof missing: {report}")
            if (code == 0) != (report["status"] == "PASS"):
                raise AssertionError("exit/status mismatch")
            return report

        manifest = install("raise SystemExit(0)\n")
        initial = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        # Non-clean caller rejection happens without cloning or checker execution.
        original_clone = module.clone_snapshot
        def forbidden_clone(*args):
            raise AssertionError("dirty caller reached cloning")
        module.clone_snapshot = forbidden_clone
        try:
            for kind in ("unstaged", "staged", "untracked"):
                path = root / ("untracked.txt" if kind == "untracked" else "README.md")
                original = path.read_bytes() if path.exists() else None
                path.write_text("dirty\n", encoding="utf-8")
                if kind == "staged":
                    run_git(root, "add", "README.md")
                report = execute(manifest)
                if report["status"] != "FAIL" or "source worktree must be clean" not in report["message"]:
                    raise AssertionError(f"dirty {kind} accepted")
                if original is None:
                    path.unlink()
                else:
                    path.write_bytes(original)
                if kind == "staged":
                    run_git(root, "add", "README.md")
        finally:
            module.clone_snapshot = original_clone
        for flag in ("assume-unchanged", "skip-worktree"):
            run_git(root, "update-index", "--" + flag, "README.md")
            original = (root / "README.md").read_bytes()
            (root / "README.md").write_text("hidden dirty bytes", encoding="utf-8")
            try:
                for arguments in ((), ("--check-manifest",)):
                    report = execute(manifest, *arguments)
                    if report["status"] != "FAIL" or "source worktree must be clean" not in report["message"]:
                        raise AssertionError("index flags hid dirty source on aggregate or manifest check")
            finally:
                (root / "README.md").write_bytes(original)
                run_git(root, "update-index", "--no-" + flag, "README.md")
        run_git(root, "config", "core.filemode", "false")
        (root / "README.md").chmod(0o755)
        try:
            report = execute(manifest)
            if report["status"] != "FAIL": raise AssertionError("core.filemode hid changed executable mode")
        finally:
            (root / "README.md").chmod(0o644)
            run_git(root, "config", "core.filemode", "true")
        passed.append("ISO-01-staged-unstaged-untracked-hidden-dirty-refused-with-final-proof")

        (root / ".gitignore").write_text("ignored-one\nignored-dir/\n", encoding="utf-8")
        (root / "link").symlink_to("README.md")
        run_git(root, "add", ".gitignore", "link")
        (root / "ignored-one").write_text("caller secret one\n", encoding="utf-8")
        (root / "ignored-dir").mkdir()
        (root / "ignored-dir/two").write_text("caller secret two\n", encoding="utf-8")
        # Leading whitespace and newline file names must not be stripped by NUL probes.
        (root / " ignored-name").write_text("first ignored bytes", encoding="utf-8")
        (root / ".gitignore").write_text((root / ".gitignore").read_text() + " ignored-name\n", encoding="utf-8")
        (root / " tracked-name\nline").write_text("tracked bytes", encoding="utf-8")
        run_git(root, "add", ".gitignore", " tracked-name\nline")
        expected_keys = sorted({"PATH", "HOME", "TMPDIR", "TMP", "TEMP", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "PYTHONPYCACHEPREFIX",
                               "PYTHONHASHSEED", "PYTHONNOUSERSITE", "LC_ALL", "LANG", "TZ", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_OPTIONAL_LOCKS",
                               "GLYPH_CHECKER_BASE", "GLYPH_CHECKER_EXPECTED_MERGE_BASE"})
        manifest = install("import os, json, subprocess, sys\nfrom pathlib import Path\n"
            + f"assert sorted(set(os.environ) - ({{'__CF_USER_TEXT_ENCODING'}} if sys.platform == 'darwin' else set())) == {expected_keys!r}\n"
            + f"assert Path.cwd() != Path({str(root)!r})\n"
            + "assert not Path('ignored-one').exists() and not Path('ignored-dir').exists()\n"
            + "assert not Path('.git/objects/info/alternates').exists()\n"
            + "assert os.environ['PYTHONHASHSEED'] == '0' and os.environ['PYTHONNOUSERSITE'] == '1'\n"
            + "assert os.environ['GIT_OPTIONAL_LOCKS'] == '0' and os.environ['GIT_CONFIG_GLOBAL'] == os.devnull\n"
            + "assert os.environ['LC_ALL'] == 'C' and os.environ['LANG'] == 'C' and os.environ['TZ'] == 'UTC'\n"
            + "assert all(Path(os.environ[k]).is_dir() and not Path(os.environ[k]).is_relative_to(Path.cwd()) for k in ('HOME','TMPDIR','TMP','TEMP','XDG_CONFIG_HOME','XDG_CACHE_HOME','PYTHONPYCACHEPREFIX'))\n"
            + "assert not subprocess.check_output(['git','remote'], text=True).strip()\n"
            + "print(json.dumps({'head': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(), 'refs': subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)'],text=True).splitlines()}))\n")
        run_git(root, "tag", "unrelated-tag")
        run_git(root, "branch", "unrelated-branch")
        run_git(root, "tag", "configurator")
        direct_env = module.isolated_environment(parent / "environment-contract", {"base": initial, "expected_merge_base": initial})
        if sorted(direct_env) != expected_keys:
            raise AssertionError("constructed launch environment has an unauthorized key")
        old_values = {key: os.environ.get(key) for key in ("GLYPH_HOSTILE", "PYTHONPATH", "GIT_DIR", "GIT_CONFIG_COUNT")}
        os.environ.update({"GLYPH_HOSTILE": "do-not-inherit", "PYTHONPATH": "/do-not-inherit", "GIT_DIR": "/absent", "GIT_CONFIG_COUNT": "99"})
        # Fingerprint only through runner's closed Git environment while hostile values exist.
        try:
            report = execute(manifest)
        finally:
            for key, value in old_values.items():
                if value is None: os.environ.pop(key, None)
                else: os.environ[key] = value
        if report["status"] != "PASS":
            raise AssertionError(f"closed environment/ignored independence failed: {report}")
        observation = json.loads(report["results"][0]["stdout_summary"][0])
        if observation["head"] != report["context"]["head"] or {line.split()[0] for line in observation["refs"]} != {"refs/heads/configurator", "refs/remotes/origin/configurator"}:
            raise AssertionError("clone head/ref set differs")
        run_git(root, "tag", "-d", "configurator")
        passed.append("ISO-02-exact-environment-ignored-exclusion-closed-refs-tag-ambiguity")

        # Every persistent isolated mutation stops before the following checker.
        next_checker = entry("must_not_run")
        write_checker(root, next_checker, 0)
        mutations = {
            "tracked-bytes": "Path('README.md').write_text('changed')",
            "tracked-mode": "Path('README.md').chmod(0o755)",
            "tracked-symlink": "Path('link').unlink(); Path('link').symlink_to('.gitignore')",
            "index": "subprocess.run(['git','update-index','--assume-unchanged','README.md'],check=True)",
            "head": "subprocess.run(['git','checkout','--detach'],check=True)",
            "ref": "subprocess.run(['git','update-ref','refs/tags/new','HEAD'],check=True)",
            "config": "subprocess.run(['git','config','validation.mutated','true'],check=True)",
            "staged": "Path('README.md').write_text('staged'); subprocess.run(['git','add','README.md'],check=True)",
            "untracked": "Path('new-file').write_text('new')",
            "ignored": "Path('ignored-one').write_text('new ignored')",
        }
        for label, action in mutations.items():
            manifest = install("from pathlib import Path\nimport subprocess\n" + action + "\n", [probe, next_checker])
            report = execute(manifest)
            if report["failure_kind"] != "ISOLATED_REPOSITORY_MUTATION" or len(report["results"]) != 1 or report["results"][0]["isolated_proof"] != "MISMATCH":
                raise AssertionError(f"isolated {label} mutation accepted or continued: {report}")
        if not {"tracked-bytes", "tracked-mode", "tracked-symlink", "index", "head", "ref", "config", "staged", "untracked", "ignored"}.issubset(mutations):
            raise AssertionError("byte-integrity mutation coverage was removed")
        passed.extend(["ISO-03-all-isolated-mutation-dimensions-stop",
                       "BYTE-06-tracked-mode-symlink-index-HEAD-ref-config-staged-untracked-ignored-mutations"])


        manifest = install("raise SystemExit(0)\n")
        for branch in ("feature-context", None, "configurator"):
            if branch == "feature-context": run_git(root, "switch", "-c", branch)
            elif branch is None: run_git(root, "checkout", "--detach")
            else: run_git(root, "switch", branch)
            report = execute(manifest)
            if report["status"] != "PASS" or report["context"]["branch"] != branch or report["context"]["detached"] != (branch is None):
                raise AssertionError("feature/configurator/detached identity not preserved")
        passed.append("ISO-04-feature-configurator-detached-context")

        # Remote-only commit is deliberately unreachable from local heads at clone time.
        run_git(root, "switch", "-c", "temporary-remote-tip")
        (root / "remote-only.txt").write_text("remote-only object\n", encoding="utf-8")
        run_git(root, "add", "remote-only.txt")
        run_git(root, "commit", "-m", "remote-only object")
        remote_tip = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        run_git(root, "switch", "configurator")
        run_git(root, "update-ref", "refs/remotes/origin/configurator", remote_tip)
        run_git(root, "branch", "-D", "temporary-remote-tip")
        os.environ["GLYPH_CHECKER_BASE"] = initial
        os.environ["GLYPH_CHECKER_EXPECTED_MERGE_BASE"] = initial
        try:
            report = execute(manifest)
            if report["status"] != "PASS" or report["context"]["comparison_ref"] != remote_tip or report["context"]["base"] != initial:
                raise AssertionError(f"local-only immutable transport/comparison override failed: {report}")
            os.environ["GLYPH_CHECKER_EXPECTED_MERGE_BASE"] = "HEAD"
            report = execute(manifest)
            if report["status"] != "FAIL" or "unexpected feature merge base" not in report["message"]:
                raise AssertionError("mismatched expected base accepted")
            os.environ["GLYPH_CHECKER_BASE"] = "0" * 40
            report = execute(manifest)
            if report["status"] != "FAIL": raise AssertionError("unavailable explicit base accepted")
        finally:
            os.environ.pop("GLYPH_CHECKER_BASE", None)
            os.environ.pop("GLYPH_CHECKER_EXPECTED_MERGE_BASE", None)
        report = execute(manifest)
        if report["status"] != "FAIL" or "not an ancestor" not in report["message"]:
            raise AssertionError("non-ancestor comparison base accepted")
        run_git(root, "update-ref", "refs/remotes/origin/configurator", initial)
        passed.append("ISO-05-local-object-transport-real-ref-and-expected-base")

        for checker_id, command in module.SELF_TEST_COMMANDS.items():
            for exact_pair in (True, False):
                self_test = entry(checker_id if exact_pair else "near_" + checker_id)
                self_test["path"], self_test["command"] = command[1], command
                write_checker(root, self_test, 0)
                (root / command[1]).write_text("import os\n" + ("assert 'GLYPH_CHECKER_BASE' not in os.environ and 'GLYPH_CHECKER_EXPECTED_MERGE_BASE' not in os.environ\n" if exact_pair else "assert os.environ['GLYPH_CHECKER_BASE'] and os.environ['GLYPH_CHECKER_EXPECTED_MERGE_BASE']\n"), encoding="utf-8")
                run_git(root, "add", command[1])
                test_manifest = write_manifest(root, [self_test], ["baseline"])
                # These inert self-test scripts prove environment dispatch only;
                # the real adopted campaign catalog is exercised separately.
                import glyph_campaign_transition as campaign
                with mock.patch.object(campaign, "ROOTS", frozenset()), mock.patch.object(
                        campaign, "authenticate", return_value={"test_only_self_test_dispatch": True}):
                    report = execute(test_manifest)
                if report["status"] != "PASS": raise AssertionError("self-test environment exception is not exact: " + str(report))
        passed.append("ISO-06-exact-self-test-id-command-pairs")

        x1_entry = entry("current_x1_regression_subset")
        x1_entry["path"], x1_entry["command"] = module.X1_COMMAND[1], module.X1_COMMAND
        write_checker(root, x1_entry, 0)
        manifest = write_manifest(root, [x1_entry], ["baseline"])
        original_candidate, original_objects = module.X1_CANDIDATE, module.X1_OBJECTS
        module.X1_CANDIDATE, module.X1_OBJECTS = initial, (initial,)
        try:
            report = execute(manifest)
            if report["status"] != "FAIL": raise AssertionError("missing required local historical ref accepted")
            run_git(root, "update-ref", module.X1_REF, "HEAD")
            report = execute(manifest)
            if report["status"] != "FAIL": raise AssertionError("wrong historical ref identity accepted")
            run_git(root, "update-ref", module.X1_REF, initial)
            report = execute(manifest)
            if report["status"] != "PASS": raise AssertionError(f"exact historical ref not reproduced: {report}")
            module.X1_OBJECTS = (initial, "0" * 40)
            report = execute(manifest)
            if report["status"] != "FAIL": raise AssertionError("missing required historical object accepted")
        finally:
            module.X1_CANDIDATE, module.X1_OBJECTS = original_candidate, original_objects
        passed.append("ISO-07-closed-historical-ref-and-object-failures")

        # Dispatch failures are tested at the actual selected checker boundary;
        # repository setup/fingerprints retain their ordinary operational budget.
        import signal
        sentinel = parent / "late-sentinel"
        source = "from pathlib import Path;Path(" + repr(str(sentinel)) + ").touch()\n"
        manifest = install(source, [probe, next_checker])
        old_budgets = module.CHECKER_TIMEOUT_SECONDS, module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS
        original_run, original_exec = module.run_checker, module.child_exec
        module.TERM_GRACE_SECONDS = .03
        def delayed_exec(command, cwd, env):
            if len(command) > 1 and command[1] == probe["path"]:
                time.sleep(30)
            original_exec(command, cwd, env)
        def selected_timeout(command, *args, **kwargs):
            if len(command) > 1 and command[1] == probe["path"]:
                # This deliberately stalled acquisition must be interrupted.
                return original_run(command, *args[:2], .2, **kwargs)
            return original_run(command, *args, **kwargs)
        try:
            module.child_exec, module.run_checker = delayed_exec, selected_timeout
            report = execute(manifest)
            if report["failure_kind"] != "CHILD_SETUP_TIMEOUT" or len(report["results"]) != 1 or sentinel.exists():
                raise AssertionError("acquisition timeout did not stop later checkers")
            def selected_launch_error(command, cwd, env):
                if len(command) > 1 and command[1] == probe["path"]:
                    raise PermissionError(1, "injected checker exec EPERM " + "🧪" * 1000)
                original_exec(command, cwd, env)
            module.child_exec, module.run_checker = selected_launch_error, original_run
            report = execute(manifest)
            if report["failure_kind"] != "CHILD_SETUP_FAILURE" or len(report["results"]) != 1 or sentinel.exists():
                raise AssertionError("launch failure did not stop later checkers")
            # Arm the aggregate clock at the selected launch, not a few hundred
            # milliseconds before a complete Git snapshot must have finished.
            def selected_deadline(command, *args, **kwargs):
                if len(command) > 1 and command[1] == probe["path"]:
                    module.DEADLINE = module.monotonic() + 1.
                    signal.setitimer(signal.ITIMER_REAL, 1.)
                return original_run(command, *args, **kwargs)
            module.child_exec, module.run_checker = delayed_exec, selected_deadline
            report = execute(manifest)
            if (report["failure_kind"] != "AGGREGATE_TIMEOUT" or report["canonical_proof"] != "UNAVAILABLE"
                    or len(report["results"]) != 1 or sentinel.exists()):
                raise AssertionError(f"whole deadline at launch not enforced: {report}")
            module.run_checker, module.child_exec = original_run, original_exec
            # Exhaust the actual absolute budget at the exact preflight entry.
            # The removed 1 ms alarm tested scheduler coincidence, not semantics.
            def exhausted_preflight(*args):
                module.DEADLINE = module.monotonic() - 1
                module.require_budget("deterministic preflight exhaustion")
            with mock.patch.object(module, "preflight_repository_safety", exhausted_preflight):
                code, text = invoke(module, root, manifest, "--json")
                report = payload(text)
            if (report["failure_kind"] != "AGGREGATE_TIMEOUT" or report["status"] != "FAIL"
                    or report["canonical_proof"] != "UNAVAILABLE" or report["results"] or sentinel.exists()):
                raise AssertionError("preflight deadline accepted or unproved state mislabeled")
            # Inject delivery at timer cancellation: the historical escaping
            # callback must instead produce a structured timeout and no dispatch.
            real_timer = signal.setitimer
            injected = []
            def retirement_alarm(which, seconds, interval=0):
                if seconds == 0 and not injected:
                    injected.append(True)
                    os.kill(os.getpid(), signal.SIGALRM)
                return real_timer(which, seconds, interval)
            with mock.patch.object(module, "preflight_repository_safety", exhausted_preflight), \
                    mock.patch.object(module.signal, "setitimer", retirement_alarm):
                code, text = invoke(module, root, manifest, "--json")
                report = payload(text)
            if not injected or report["failure_kind"] != "AGGREGATE_TIMEOUT" or report["status"] != "FAIL" or report["results"]:
                raise AssertionError("timer retirement escaped structured timeout")
        finally:
            module.run_checker, module.child_exec = original_run, original_exec
            module.CHECKER_TIMEOUT_SECONDS, module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS = old_budgets
        passed.append("ISO-08-launch-failure-timeout-whole-and-preflight-deadlines-stop-dispatch")

        manifest = install("raise SystemExit(0)\n")
        original_clone = module.clone_snapshot
        def setup_failure(*args): raise ValueError("injected setup failure")
        module.clone_snapshot = setup_failure
        try:
            report = execute(manifest)
            if report["census_freshness"]["status"] != "PASS" or report["failure_kind"] != "SETUP_FAILURE":
                raise AssertionError("structured setup failure lost truthful census result")
        finally: module.clone_snapshot = original_clone
        # The final proof detects caller writes even though absolute host writes are not prevented.
        def caller_mutation(*args):
            (root / "ignored-one").write_text("altered caller\n", encoding="utf-8")
            raise ValueError("injected setup failure after caller mutation")
        module.clone_snapshot = caller_mutation
        try:
            code, text = invoke(module, root, manifest, "--json")
            report = payload(text)
            if code != 1 or report["failure_kind"] != "CANONICAL_REPOSITORY_MUTATION" or report["canonical_proof"] != "MISMATCH":
                raise AssertionError("setup failure bypassed canonical ignored-byte mutation proof")
        finally: module.clone_snapshot = original_clone
        passed.append("ISO-09-setup-failure-census-and-canonical-mutation-proof")
        # Prove the real-time deadline interrupts work already stalled inside phases.
        old_census, old_fingerprint, old_clone = module.census_freshness, module.canonical_fingerprint, module.clone_snapshot
        old_budget, old_grace = module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS
        try:
            module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS = 30., .03
            for stalled_phase in ("census", "setup", "final_proof"):
                calls = [0]
                entered = []
                def enter_stall():
                    entered.append(stalled_phase)
                    module.DEADLINE = module.monotonic() + 1.
                    signal.setitimer(signal.ITIMER_REAL, 1.)
                def stalled_census():
                    enter_stall()
                    time.sleep(30)
                    return old_census()
                def stalled_fingerprint(*args):
                    calls[0] += 1
                    if calls[0] == 2:
                        enter_stall()
                        time.sleep(30)
                    return old_fingerprint(*args)
                def stalled_setup(*args):
                    enter_stall()
                    result = module.run_checker([sys.executable, "-c", "import time; time.sleep(30)"], root,
                        module.EXECUTION_ENV, module.require_budget("injected setup"))
                    if result[3]: raise module.AggregateTimeout("injected setup command timeout")
                    raise AssertionError("stalled setup did not time out")
                module.census_freshness = stalled_census if stalled_phase == "census" else old_census
                module.canonical_fingerprint = stalled_fingerprint if stalled_phase == "final_proof" else old_fingerprint
                module.clone_snapshot = stalled_setup if stalled_phase == "setup" else old_clone
                started = time.monotonic()
                code, text = invoke(module, root, manifest, "--json", *( ["--check-manifest"] if stalled_phase == "final_proof" else []))
                report = payload(text)
                if (code != 1 or report["failure_kind"] != "AGGREGATE_TIMEOUT"
                        or entered != [stalled_phase] or time.monotonic() - started > 15):
                    raise AssertionError(f"stalled {stalled_phase} was not interrupted boundedly: {report}")
                if report["canonical_proof"] != "UNAVAILABLE":
                    raise AssertionError("deadline exhaustion claimed complete final proof")
        finally:
            module.census_freshness, module.canonical_fingerprint, module.clone_snapshot = old_census, old_fingerprint, old_clone
            module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS = old_budget, old_grace
        passed.append("ISO-10-stalled-census-setup-final-proof-interrupted")
        before = module.canonical_fingerprint(root)
        (root / " ignored-name").write_text("changed ignored bytes", encoding="utf-8")
        if module.canonical_fingerprint(root) == before:
            raise AssertionError("leading whitespace ignored filename bytes were omitted")
        passed.append("ISO-11-whitespace-newline-file-name-fingerprints")

        # A hostile PATH must not replace the interpreter that launched the
        # aggregate.  The manifest command remains portable and is only
        # rewritten at the execution boundary.
        fake_python = parent / "fake-bin" / "python3"
        fake_python.parent.mkdir()
        fake_invocation = fake_python.with_name("invoked")
        fake_python.write_text(
            "#!/bin/sh\nprintf invoked > " + shlex.quote(str(fake_invocation)) + "\nprintf forged-output\nexit 0\n",
            encoding="utf-8",
        )
        fake_python.chmod(0o755)
        interpreter_probe = install(
            "import json,sys\nprint(json.dumps({'executable': sys.executable}))\n"
        )
        old_path = os.environ.get("PATH")
        os.environ["PATH"] = str(fake_python.parent) + os.pathsep + (old_path or "")
        try:
            report = execute(interpreter_probe)
        finally:
            if old_path is None:
                os.environ.pop("PATH", None)
            else:
                os.environ["PATH"] = old_path
        if report["status"] != "PASS":
            raise AssertionError(f"ambient python3 substituted for invoking interpreter: {report}")
        observed = json.loads(report["results"][0]["stdout_summary"][0])["executable"]
        if observed != module.sys.executable or fake_invocation.exists():
            raise AssertionError("checker did not run under the invoking interpreter")

        fake_python.write_text(
            "#!/bin/sh\nprintf invoked > " + shlex.quote(str(fake_invocation)) + "\nexit 91\n",
            encoding="utf-8",
        )
        report = execute(interpreter_probe)
        if report["status"] != "PASS" or fake_invocation.exists():
            raise AssertionError("failing PATH substitute was reached or changed real-checker behavior")

        original_executable = module.sys.executable
        unusable = ["", "relative-invoking-python", str(parent / "missing-invoking-python")]
        non_executable = parent / "non-executable-invoking-python"
        non_executable.write_text("placeholder\n", encoding="utf-8")
        non_executable.chmod(0o644)
        unusable.append(str(non_executable))
        try:
            for candidate in unusable:
                module.sys.executable = candidate
                report = execute(interpreter_probe)
                if report["status"] != "FAIL" or report["failure_kind"] != "SETUP_FAILURE" or "invoking Python executable" not in report["message"]:
                    raise AssertionError(f"unusable invoking interpreter was not rejected: {candidate!r}: {report}")
        finally:
            module.sys.executable = original_executable
        passed.append("ISO-12-invoking-python-binding-and-unusable-identity-failure")
    return passed


def process_control_cases(module: Any) -> list[str]:
    """Real children plus deterministic faults, independent of host startup speed."""
    import errno
    import signal
    passed = []
    with tempfile.TemporaryDirectory(prefix="glyph-process-contract-") as directory:
        root = Path(directory)
        sentinel = root / "executed"
        command = [sys.executable, "-c", "from pathlib import Path;Path(" + repr(str(sentinel)) + ").touch()"]
        old_grace = module.TERM_GRACE_SECONDS
        module.TERM_GRACE_SECONDS = .03
        def run(cmd=command, timeout=20.):
            return module.run_checker(cmd, root, module.base_environment(), timeout)
        def reject(expected, result):
            if result[3] != expected or sentinel.exists():
                raise AssertionError(f"setup/cleanup false success or wrong classification: {result}")
        try:
            result = run([sys.executable, "-c", "import os,json;print(json.dumps([os.getpid(),os.getpgrp(),os.getsid(0)]))"])
            identity = json.loads(result[1])
            if result[0] or result[3] or len(set(identity)) != 1:
                raise AssertionError(f"session acquisition failed: {result}")
            passed.append("PROC-01-session-handshake-success")

            def setup_error(): raise PermissionError(errno.EPERM, "injected setsid denial")
            with mock.patch.object(module.os, "setsid", setup_error):
                result = run()
            reject("CHILD_SETUP_FAILURE", result)
            record = next(json.loads(line) for line in result[2].splitlines() if json.loads(line)["kind"] == "CHILD_SETUP_FAILURE")
            if record["phase"] != "child:setsid" or record["reported_errno"] != errno.EPERM:
                raise AssertionError("child setup syscall/errno lost")
            def exec_error(*args): raise OSError(errno.EIO, "injected before exec")
            with mock.patch.object(module, "child_exec", exec_error):
                reject("CHILD_SETUP_FAILURE", run())
            def unicode_exec_error(*args): raise OSError(errno.ENOENT, "injected launch " + "🧪" * 1000)
            with mock.patch.object(module, "child_exec", unicode_exec_error):
                reject("CHILD_SETUP_FAILURE", run())
            passed.append("PROC-02-pre-exec-setsid-EPERM-and-bounded-Unicode-errors")

            original_status = module.child_setup_status
            def malformed(fd, message):
                if message["status"] == "READY": os.write(fd, b"not-json\n")
                else: original_status(fd, message)
            def premature_eof(fd, message): os._exit(0)
            for writer in (malformed, premature_eof):
                with mock.patch.object(module, "child_setup_status", writer):
                    reject("CHILD_SETUP_PROTOCOL_FAILURE", run())
            def lost_error(fd, message):
                if message["status"] == "ERROR": raise OSError(errno.EIO, "injected lost error report")
                original_status(fd, message)
            with mock.patch.object(module, "child_setup_status", lost_error), mock.patch.object(module, "child_exec", exec_error):
                reject("UNREPORTED_LAUNCH_OR_EXIT_127", run())
            passed.append("PROC-03-malformed-EOF-and-lost-error-handshake-refusal")

            original_setsid = module.os.setsid
            def delayed_session():
                time.sleep(30)
                original_setsid()
            start = time.monotonic()
            with mock.patch.object(module.os, "setsid", delayed_session), mock.patch.object(module, "CHILD_SETUP_TIMEOUT_SECONDS", .2):
                reject("CHILD_SETUP_TIMEOUT", run())
            if time.monotonic() - start > 5:
                raise AssertionError("acquisition cleanup exceeded bound")
            passed.append("PROC-04-delayed-session-acquisition-bounded")

            # Prove actual child AND descendant readiness before arming the real
            # aggregate alarm. Startup has 20s; the deliberate stall is 30s.
            ready = root / "tree-ready"
            child = ("import os,signal,time;from pathlib import Path;"
                     "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                     "Path(" + repr(str(ready)) + ").write_text(str(os.getpid()));time.sleep(30)")
            source = ("import subprocess,sys,signal,time\n"
                      "signal.signal(signal.SIGTERM,signal.SIG_IGN)\n"
                      "subprocess.Popen([sys.executable,'-c'," + repr(child) + "])\n"
                      "time.sleep(30)\n")
            real_clock = module.monotonic
            armed = []
            old_deadline = module.DEADLINE
            def arm_when_ready():
                now = real_clock()
                if not armed and ready.exists():
                    armed.append(now)
                    module.DEADLINE = now + .2
                    signal.setitimer(signal.ITIMER_REAL, .2)
                return now
            def alarm(*args): raise module.AggregateTimeout("real ready-tree deadline")
            old_handler = signal.signal(signal.SIGALRM, alarm)
            old_timer = signal.setitimer(signal.ITIMER_REAL, 0)
            signals = []
            real_killpg = module.os.killpg
            def record_signals(pid, signum):
                if signum: signals.append((pid, signum))
                return real_killpg(pid, signum)
            try:
                with mock.patch.object(module, "monotonic", arm_when_ready), mock.patch.object(module.os, "killpg", record_signals):
                    result = run([sys.executable, "-c", source])
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old_handler)
                module.DEADLINE = old_deadline
                if old_timer[0]: signal.setitimer(signal.ITIMER_REAL, *old_timer)
            if not armed or result[3] != "AGGREGATE_TIMEOUT" or result[0] != -signal.SIGKILL or not any(s == signal.SIGKILL for _, s in signals):
                raise AssertionError(f"ready TERM-resistant tree not killed: {result}; signals={signals}")
            for pgid, _ in signals:
                if module.group_exists(pgid):
                    raise AssertionError("managed descendant group survived KILL")
            if real_clock() - armed[0] > 5:
                raise AssertionError("real tree cleanup exceeded bound")
            passed.append("PROC-05-ready-TERM-resistant-child-and-descendant-real-KILL")

            # Deterministically cross the checker clock only after Python has
            # entered the checker. No assumption that startup fits in .1s.
            ready.unlink()
            def checker_clock(): return real_clock() + (25 if ready.exists() else 0)
            with mock.patch.object(module, "monotonic", checker_clock):
                result = run([sys.executable, "-c", "from pathlib import Path;import time;Path(" + repr(str(ready)) + ").touch();time.sleep(30)"])
            if not ready.exists() or result[3] != "CHECKER_TIMEOUT":
                raise AssertionError("entered checker timeout was not enforced")
            passed.append("PROC-06-checker-timeout-after-proven-entry")

            # EPERM is not an automatic success. A transient group denial may
            # resolve only with a reaped leader AND proven absent group.
            def deny_term(pid, signum):
                if signum == signal.SIGTERM: raise PermissionError(errno.EPERM, "injected group TERM denial")
                return real_killpg(pid, signum)
            with mock.patch.object(module.os, "killpg", deny_term), mock.patch.object(module, "child_exec", exec_error):
                result = run()
            reject("CHILD_SETUP_FAILURE", result)
            if "GROUP_ABSENT_AFTER_REAP" not in result[2]:
                raise AssertionError("denied group operation not resolved by absence proof")
            passed.append("PROC-07-group-EPERM-requires-reap-and-absence-proof")

            real_fork, real_waitpid = module.os.fork, module.os.waitpid
            owned = []
            def record_fork():
                pid = real_fork()
                if pid: owned.append(pid)
                return pid
            def broken_wait(*args): raise OSError(errno.EIO, "injected waitpid failure")
            def deny_group(pid, signum): raise PermissionError(errno.EPERM, "injected persistent group denial")
            for target, replacement in (("waitpid", broken_wait), ("killpg", deny_group)):
                owned.clear()
                try:
                    with mock.patch.object(module.os, "fork", record_fork), mock.patch.object(module.os, target, replacement), mock.patch.object(module, "child_exec", exec_error), mock.patch.object(module, "CLEANUP_REAP_SECONDS", .1):
                        result = run()
                    reject("PROCESS_CLEANUP_FAILURE", result)
                    if "cleanup.proof" not in result[2] or result[4] > 5:
                        raise AssertionError("unproved KILL/reap was hidden or unbounded")
                finally:
                    for pid in owned:
                        try: os.killpg(pid, signal.SIGKILL)
                        except (ProcessLookupError, PermissionError): pass
                        try:
                            found, _ = real_waitpid(pid, os.WNOHANG)
                            if not found:
                                os.kill(pid, signal.SIGKILL)
                                real_waitpid(pid, 0)
                        except (ChildProcessError, ProcessLookupError): pass
            passed.append("PROC-08-KILL-reap-and-permission-proof-failures")

            # Review regressions: a timer at cleanup entry must not discard
            # ownership, and a failed reap must never suppress group KILL.
            for defect in ("alarm_at_cleanup_entry", "reap_failure_with_descendant"):
                if ready.exists(): ready.unlink()
                owned.clear()
                signals.clear()
                alarm_sent = []
                real_timer = signal.setitimer
                real_clock = module.monotonic
                def entered_clock(): return real_clock() + (25 if ready.exists() else 0)
                def entry_alarm(which, value, interval=0):
                    if value == 0 and not alarm_sent:
                        alarm_sent.append(True)
                        os.kill(os.getpid(), signal.SIGALRM)
                    return real_timer(which, value, interval)
                def late_reap_error(*args):
                    if ready.exists(): raise OSError(errno.EIO, "injected reap failure after descendant readiness")
                    return real_waitpid(*args)
                old_handler = signal.signal(signal.SIGALRM, alarm)
                try:
                    with mock.patch.object(module.os, "fork", record_fork), mock.patch.object(module, "monotonic", entered_clock), mock.patch.object(module.os, "killpg", record_signals), mock.patch.object(module, "CLEANUP_REAP_SECONDS", .1):
                        if defect == "alarm_at_cleanup_entry":
                            with mock.patch.object(module.signal, "setitimer", entry_alarm):
                                result = run([sys.executable, "-c", source])
                        else:
                            with mock.patch.object(module.os, "waitpid", late_reap_error):
                                result = run([sys.executable, "-c", source])
                    expected = "AGGREGATE_TIMEOUT" if alarm_sent else "PROCESS_CLEANUP_FAILURE"
                    if result[3] != expected or not ready.exists() or not any(sig == signal.SIGKILL for _, sig in signals):
                        raise AssertionError(f"review cleanup regression {defect}: {result}; signals={signals}")
                    if defect == "alarm_at_cleanup_entry":
                        try: real_waitpid(owned[0], os.WNOHANG)
                        except ChildProcessError: pass
                        else: raise AssertionError("cleanup-entry alarm left owned leader unreaped")
                    else:
                        # Only the injected waitpid prevented proof. Restore it
                        # and verify that group KILL actually happened anyway.
                        found, _ = real_waitpid(owned[0], os.WNOHANG)
                        if found != owned[0]: raise AssertionError("failed reap also suppressed leader KILL")
                    end = time.monotonic() + 2
                    while module.group_exists(owned[0]) and time.monotonic() < end:
                        time.sleep(.01)
                    if module.group_exists(owned[0]):
                        raise AssertionError("review regression left descendant group alive")
                finally:
                    real_timer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, old_handler)
                    for pid in owned:
                        try: os.killpg(pid, signal.SIGKILL)
                        except (ProcessLookupError, PermissionError): pass
                        try:
                            found, _ = real_waitpid(pid, os.WNOHANG)
                            if not found:
                                os.killpg(pid, signal.SIGKILL)
                                os.kill(pid, signal.SIGKILL)
                                real_waitpid(pid, 0)
                        except (ChildProcessError, ProcessLookupError): pass
            passed.append("PROC-09-cleanup-entry-alarm-retains-ownership")
            passed.append("PROC-10-reap-error-cannot-suppress-descendant-KILL")
        finally:
            module.TERM_GRACE_SECONDS = old_grace
    return passed


def byte_integrity_cases(module: Any) -> list[str]:
    """Separate raw repository evidence from strict checker text contracts."""
    import errno
    passed = []
    with tempfile.TemporaryDirectory(prefix="glyph-byte-contract-") as directory:
        parent = Path(directory)
        root = fresh_root(parent)
        original_root = module.ROOT
        module.ROOT = root
        try:
            result = module.run_process([sys.executable, "-c", "import os;os.write(1,b'\\xff');os.write(2,b'\\xfe')"],
                root, module.base_environment(), 20.)
            if result[:4] != (0, b"\xff", b"\xfe", None):
                raise AssertionError(f"raw process evidence changed bytes: {result!r}")
            passed.append("BYTE-01-distinct-malformed-bytes-preserved-by-real-process")

            # Hold every filesystem byte fixed; vary only malformed raw Git
            # metadata so a different digest cannot be credited to file changes.
            original_git = module.git_bytes
            def altered_metadata(raw, stream):
                def probe(*args, **kwargs):
                    result = original_git(*args, **kwargs)
                    if args == ("for-each-ref", "--format=%(refname) %(objectname)"):
                        return subprocess.CompletedProcess(result.args, result.returncode,
                            raw if stream == "stdout" else result.stdout,
                            raw if stream == "stderr" else result.stderr)
                    return result
                return probe
            for stream in ("stdout", "stderr"):
                fingerprints = []
                for raw in (b"ref-\xff\n", b"ref-\xfe\n"):
                    with mock.patch.object(module, "git_bytes", altered_metadata(raw, stream)):
                        fingerprints.append(module.canonical_fingerprint(root))
                if fingerprints[0] == fingerprints[1]:
                    raise AssertionError("malformed Git metadata admitted a byte collision")
            passed.append("BYTE-02-raw-Git-stdout-and-stderr-affect-fingerprint")

            names = [b" leading", b"line\nbreak", "unicode-λ".encode("utf-8"), b"raw-\xff", b"raw-\xfe"]
            enumeration = b"\0".join(reversed(names)) + b"\0"
            if module.nul_paths(enumeration) != sorted(names):
                raise AssertionError("raw NUL path identity/order changed")
            for raw in names:
                path = module.repository_path(root, raw)
                if not isinstance(path, bytes) or os.fsencode(os.fsdecode(path)) != path or not path.endswith(b"/" + raw):
                    raise AssertionError("filesystem path conversion is not reversible")
            for malformed in (b"missing-NUL", b"one\0\0two\0"):
                try: module.nul_paths(malformed)
                except ValueError: pass
                else: raise AssertionError("malformed path framing accepted")
            native_nontext = True
            for raw in names:
                path = module.repository_path(root, raw)
                try:
                    with open(path, "wb") as stream: stream.write(b"before")
                except OSError as exc:
                    if sys.platform != "darwin" or exc.errno not in (errno.EILSEQ, errno.EPERM) or raw not in names[-2:]:
                        raise
                    native_nontext = False
                    continue  # APFS/host permission layer refuses these names; raw roundtrip is tested.
                before = module.canonical_fingerprint(root)
                with open(path, "wb") as stream: stream.write(b"after")
                if module.canonical_fingerprint(root) == before:
                    raise AssertionError(f"path bytes omitted from actual file mutation: {raw!r}")
            passed.append("BYTE-03-raw-NUL-paths-roundtrip-and-" + ("native-nontext-files" if native_nontext else "macOS-nontext-name-refusal-with-raw-roundtrip"))

            link = module.repository_path(root, b"byte-link")
            fingerprints = []
            native_targets = True
            for target in (b"README.md", b"other-target", b"\xff", b"\xfe"):
                try: os.unlink(link)
                except FileNotFoundError: pass
                try: os.symlink(target, link)
                except OSError as exc:
                    if sys.platform != "darwin" or exc.errno not in (errno.EILSEQ, errno.EPERM) or target not in (b"\xff", b"\xfe"):
                        raise
                    native_targets = False
                    break
                if os.readlink(link) != target:
                    raise AssertionError("symlink bytes changed in filesystem transport")
                fingerprints.append(module.canonical_fingerprint(root))
            if len(set(fingerprints)) != len(fingerprints):
                raise AssertionError("different symlink targets collapsed")
            if not native_targets:
                os.symlink(b"README.md", link)
                original_readlink = module.os.readlink
                def changed_target(raw):
                    return lambda path, *args, **kwargs: raw if path == link else original_readlink(path, *args, **kwargs)
                fingerprints = []
                for raw in (b"\xff", b"\xfe"):
                    with mock.patch.object(module.os, "readlink", changed_target(raw)):
                        fingerprints.append(module.canonical_fingerprint(root))
                if fingerprints[0] == fingerprints[1]:
                    raise AssertionError("raw symlink target evidence collapsed")
            passed.append("BYTE-04-byte-symlink-targets-affect-fingerprint")

            # A true text checker emits invalid stdout/stderr, exits zero, and
            # must still stop dispatch before its successor in the real aggregate.
            text_parent = parent / "text"
            text_parent.mkdir()
            text_root = fresh_root(text_parent)
            probe, next_checker = entry("bad_text"), entry("must_not_run_after_bad_text")
            write_checker(text_root, next_checker, 0)
            for descriptor in (1, 2):
                write_checker(text_root, probe, 0)
                (text_root / probe["path"]).write_text(f"import os\nos.write({descriptor},b'\\xff')\n", encoding="utf-8")
                run_git(text_root, "add", probe["path"])
                manifest = write_manifest(text_root, [probe, next_checker], ["baseline"])
                before = module.canonical_fingerprint(text_root)
                code, text = invoke(module, text_root, manifest, "--json")
                report = payload(text)
                if (code != 1 or report["failure_kind"] != "MALFORMED_TEXT_OUTPUT" or len(report["results"]) != 1
                        or report["results"][0]["exit_code"] != 0 or report["canonical_proof"] != "MATCH"
                        or module.canonical_fingerprint(text_root) != before):
                    raise AssertionError(f"malformed text passed or continued dispatch: {report}")
            with mock.patch.object(module, "git_bytes", return_value=subprocess.CompletedProcess(["git"], 0, b"\xff", b"")):
                try: module.git("text-probe")
                except ValueError as exc:
                    if "MALFORMED_GIT_TEXT_OUTPUT" not in str(exc): raise
                else: raise AssertionError("strict Git text boundary accepted malformed UTF-8")
            passed.append("BYTE-05-malformed-checker-text-fails-and-stops-dispatch")
        finally:
            module.ROOT = original_root
    return passed


def pre_git_metadata_cases(module: Any) -> list[str]:
    """Prove unsafe fixed objects never reach even the first Git wrapper call."""
    passed = []
    with tempfile.TemporaryDirectory(prefix="glyph-pre-git-contract-") as directory:
        parent = Path(directory).resolve()
        def refused(root, needle):
            with mock.patch.object(module, "git_bytes", side_effect=AssertionError("Git invoked before admission")) as git_probe:
                for operation in (lambda: module.preflight_repository_safety(root),
                                  lambda: module.canonical_fingerprint(root)):
                    try: operation()
                    except ValueError as exc:
                        if needle not in str(exc): raise
                    else: raise AssertionError("unsafe fixed metadata admitted")
                code, text = invoke(module, root, root / "unused-manifest", "--json")
                report = payload(text)
                if code != 1 or report["failure_kind"] != "SETUP_FAILURE" or needle not in report["message"]:
                    raise AssertionError(f"unsafe main startup classification: {report}")
                if git_probe.call_count: raise AssertionError("Git called on unsafe metadata")
        cases = [("PREMETA-01-config-FIFO", "config", "fifo"),
                 ("PREMETA-02-HEAD-FIFO", "HEAD", "fifo"),
                 ("PREMETA-03-config-directory", "config", "directory"),
                 ("PREMETA-04-config-equal-byte-symlink", "config", "symlink"),
                 ("PREMETA-05-config-broken-symlink", "config", "broken"),
                 ("PREMETA-06-commondir-FIFO", "commondir", "fifo")]
        for label, name, kind in cases:
            fixture = parent / label
            fixture.mkdir()
            root = fresh_root(fixture)
            path = root / ".git" / name
            target = fixture / "equal-bytes"
            if path.is_file():
                target.write_bytes(path.read_bytes())
                path.unlink()
            if kind == "fifo": os.mkfifo(path)
            elif kind == "directory": path.mkdir()
            else: path.symlink_to(target if kind == "symlink" else fixture / "missing")
            refused(root, "UNSAFE_GIT_CONTROL")
            passed.append(label + "-no-Git")
        fixture = parent / "gitfile-refusals"
        fixture.mkdir()
        root = fresh_root(fixture)
        (root / ".git").rename(root / "metadata")
        for raw in (b"wrong locator", b"gitdir: ", b"gitdir: metadata\0", b"gitdir: metadata\nsecond\n",
                    b"gitdir: " + b"x" * (module.LOCATOR_LIMIT + 1)):
            (root / ".git").write_bytes(raw)
            refused(root, "GIT")
        passed.append("PREMETA-07-malformed-NUL-multirecord-oversized-gitfile-no-Git")
        (root / ".git").unlink()
        os.mkfifo(root / ".git")
        refused(root, "UNSAFE_DOT_GIT")
        passed.append("PREMETA-08-dot-git-FIFO-no-read-no-Git")
        (root / ".git").unlink()
        (root / "metadata").rename(root / ".git")
        admitted = module.preflight_repository_safety(root)
        if admitted["kind"] != b"DIRECTORY": raise AssertionError("ordinary layout refused")
        module.canonical_fingerprint(root)
        passed.append("PREMETA-09-ordinary-directory-admitted-and-crosschecked")
        linked = fixture / "linked"
        run_git(root, "worktree", "add", "--detach", str(linked), "HEAD")
        layout = module.preflight_repository_safety(linked)
        if layout["kind"] != b"GITFILE" or layout["git_dir"] == layout["common_dir"]:
            raise AssertionError("linked-worktree common layout not discovered")
        original = module.canonical_fingerprint(linked)
        # Both relative and absolute gitfile forms must agree with Git discovery.
        relative = os.path.relpath(layout["git_dir"], os.fsencode(linked))
        (linked / ".git").write_bytes(b"gitdir: " + relative + b"\n")
        if module.canonical_fingerprint(linked) == original:
            raise AssertionError("raw gitfile locator spelling was not fingerprinted")
        passed.append("PREMETA-10-relative-absolute-gitfile-and-commondir-crosschecked")
        # Actual arbitrary checker mutations: intercept the Git wrapper if it
        # ever sees the unsafe post-state, rather than relying on a short clock.
        normal = parent / "post-state"
        normal.mkdir()
        root = fresh_root(normal)
        probe, successor = entry("unsafe_metadata_post"), entry("after_unsafe_metadata")
        write_checker(root, successor, 0)
        for kind in ("fifo", "symlink"):
            write_checker(root, probe, 0)
            action = "os.mkfifo(p)" if kind == "fifo" else "p.symlink_to('config-copy')"
            (root / probe["path"]).write_text(
                "import os\nfrom pathlib import Path\np=Path('.git/config')\n"
                "Path('.git/config-copy').write_bytes(p.read_bytes())\np.unlink()\n" + action + "\n", encoding="utf-8")
            run_git(root, "add", probe["path"])
            manifest = write_manifest(root, [probe, successor], ["baseline"])
            before = module.canonical_fingerprint(root)
            old_git = module.git_bytes
            def guarded_git(*args, **kwargs):
                active = kwargs.get("cwd") or module.ROOT
                # A Git wrapper call on a mutated config is itself a failure.
                try: module.preflight_repository_safety(active)
                except ValueError as exc:
                    raise AssertionError("Git wrapper reached unsafe post-state") from exc
                return old_git(*args, **kwargs)
            with mock.patch.object(module, "git_bytes", side_effect=guarded_git):
                code, text = invoke(module, root, manifest, "--json")
            report = payload(text)
            if (code != 1 or report["failure_kind"] != "ISOLATED_PROOF_FAILURE" or len(report["results"]) != 1
                    or report["results"][0]["isolated_proof"] == "MATCH"
                    or "UNSAFE_GIT_CONTROL" not in report["results"][0].get("proof_error", "")
                    or report["canonical_proof"] != "MATCH" or module.canonical_fingerprint(root) != before):
                raise AssertionError(f"unsafe post-check metadata accepted: {report}")
        passed.append("PREMETA-11-post-check-FIFO-and-symlink-proof-refusal-stops-next")
    return passed


def locator_traversal_cases(module: Any) -> list[str]:
    """Descriptor traversal regressions, never accepting timeout as admission."""
    import shutil
    passed = []
    with tempfile.TemporaryDirectory(prefix="glyph-descriptor-contract-") as directory:
        parent = Path(directory).resolve()
        root = fresh_root(parent)
        original = root / ".git"
        safe = root / "safe"
        original.rename(safe)
        attacker = parent / "attacker"
        (attacker / "intermediate").mkdir(parents=True)
        shutil.copytree(safe, attacker / "safe")
        (attacker / "safe/config").unlink()
        os.mkfifo(attacker / "safe/config")
        (root / "link").symlink_to(attacker / "intermediate", target_is_directory=True)
        original.write_bytes(b"gitdir: link/../safe\n")
        def refused():
            with mock.patch.object(module, "git_bytes", side_effect=AssertionError("Git reached unsafe locator")) as git_probe:
                try: module.canonical_fingerprint(root)
                except ValueError as exc:
                    if "UNSAFE_LOCATOR_TOPOLOGY" not in str(exc): raise
                else: raise AssertionError("symlink locator admitted")
                if git_probe.call_count: raise AssertionError("unsafe locator invoked Git")
        refused()
        passed.append("PREMETA-12-link-dotdot-FIFO-bypass-refused-at-component-no-Git")
        (root / "link").unlink()
        (root / "real/subdir").mkdir(parents=True)
        target = root / "real/gitdir"
        safe.rename(target)
        original.write_bytes(b"gitdir: real/subdir/../gitdir\n")
        layout = module.preflight_repository_safety(root)
        if layout["git_dir"] != os.fsencode(target): raise AssertionError("physical dotdot target differs")
        module.canonical_fingerprint(root)
        # Dot is an explicit no-op, including raw-byte distinction in the proof.
        before = module.canonical_fingerprint(root)
        original.write_bytes(b"gitdir: ./real/subdir/../gitdir\n")
        if module.canonical_fingerprint(root) == before: raise AssertionError("raw dot locator spelling omitted")
        passed.append("PREMETA-13-real-directory-dotdot-and-explicit-dot-admitted")
        linked = parent / "linked"
        run_git(root, "worktree", "add", "--detach", str(linked), "HEAD")
        linked_layout = module.preflight_repository_safety(linked)
        if linked_layout["commondir_raw"] != b"../..\n" or linked_layout["common_dir"] != os.fsencode(target):
            raise AssertionError("linked-worktree parent traversal differs")
        module.canonical_fingerprint(linked)
        passed.append("PREMETA-14-commondir-dotdot-dotdot-physical-parent-admitted")
        # Symlink components before AND after dotdot in a commondir locator.
        common_record = target / "commondir"
        (target / "link").symlink_to(attacker / "intermediate", target_is_directory=True)
        common_record.write_bytes(b"link/../safe\n")
        refused()
        passed.append("PREMETA-15-commondir-symlink-before-dotdot-no-Git")
        (root / "real/link").symlink_to(attacker / "safe", target_is_directory=True)
        common_record.write_bytes(b"../link\n")
        refused()
        passed.append("PREMETA-16-commondir-symlink-after-dotdot-no-Git")
        common_record.unlink()
        original.write_bytes(b"gitdir: " + os.fsencode(target) + b"\n")
        module.canonical_fingerprint(root)
        passed.append("PREMETA-17-absolute-no-symlink-locator-admitted")
        (root / "alias").symlink_to(root / "real", target_is_directory=True)
        original.write_bytes(b"gitdir: " + os.fsencode(root / "alias/gitdir") + b"\n")
        refused()
        passed.append("PREMETA-18-absolute-symlink-locator-no-Git")
        original.write_bytes(b"gitdir: real/gitdir\n")
        old_object = module.metadata_object
        changed = False
        def replace_locator(path):
            nonlocal changed
            result = old_object(path)
            if path == os.fsencode(original) and not changed:
                changed = True
                original.write_bytes(b"gitdir: ./real/gitdir\n")
            return result
        with mock.patch.object(module, "metadata_object", side_effect=replace_locator), mock.patch.object(
                module, "git_bytes", side_effect=AssertionError("Git used stale locator admission")):
            try: module.canonical_fingerprint(root)
            except ValueError as exc:
                if "GIT_LAYOUT_CHANGED_BEFORE_PROBE" not in str(exc): raise
            else: raise AssertionError("changed raw locator reused stale admission")
        if not changed: raise AssertionError("locator mutation did not execute")
        # Replace the admitted directory itself between traversal and probe.
        changed = False
        def replace_directory(path):
            nonlocal changed
            result = old_object(path)
            if path == os.fsencode(original) and not changed:
                changed = True
                target.rename(target.with_name("saved-gitdir"))
                shutil.copytree(target.with_name("saved-gitdir"), target)
            return result
        with mock.patch.object(module, "metadata_object", side_effect=replace_directory), mock.patch.object(
                module, "git_bytes", side_effect=AssertionError("Git used stale directory admission")):
            try: module.canonical_fingerprint(root)
            except ValueError as exc:
                if "GIT_LAYOUT_CHANGED_BEFORE_PROBE" not in str(exc): raise
            else: raise AssertionError("changed directory reused stale admission")
        passed.append("PREMETA-19-locator-and-directory-replacement-refuse-before-Git")
        for malformed in (b"real//gitdir", b"real/gitdir/"):
            original.write_bytes(b"gitdir: " + malformed + b"\n")
            with mock.patch.object(module, "git_bytes", side_effect=AssertionError("Git used malformed component")):
                try: module.canonical_fingerprint(root)
                except ValueError as exc:
                    if "MALFORMED_LOCATOR_TOPOLOGY" not in str(exc): raise
                else: raise AssertionError("empty locator component admitted")
    return passed


def metadata_object_cases(module: Any) -> list[str]:
    """Object identity controls share the serializer used by every metadata role."""
    import hashlib
    passed = []
    with tempfile.TemporaryDirectory(prefix="glyph-metadata-contract-") as directory:
        parent = Path(directory)
        path = os.fsencode(parent / "metadata")
        target_a, target_b = os.fsencode(parent / "target-a"), os.fsencode(parent / "target-b")
        for target in (target_a, target_b):
            with open(target, "wb") as stream: stream.write(b"same bytes")
        def evidence():
            digest = hashlib.sha256()
            for value in module.metadata_object(path):
                digest.update(len(value).to_bytes(8, "big"))
                digest.update(value)
            return digest.digest()
        absent = evidence()
        os.symlink(b"missing-target", path)
        broken = evidence()
        if broken == absent: raise AssertionError("ABSENT collided with broken metadata symlink")
        os.unlink(path)
        with open(path, "wb") as stream: stream.write(b"same bytes")
        regular = evidence()
        original_mode = os.lstat(path).st_mode
        os.chmod(path, 0o700)
        if evidence() == regular: raise AssertionError("metadata permission mutation invisible")
        os.chmod(path, original_mode)
        with open(path, "wb") as stream: stream.write(b"changed bytes")
        if evidence() == regular: raise AssertionError("metadata regular bytes invisible")
        os.unlink(path)
        os.symlink(target_a, path)
        link_a = evidence()
        if link_a == regular: raise AssertionError("metadata regular/symlink collision")
        os.unlink(path)
        os.symlink(target_b, path)
        if evidence() == link_a: raise AssertionError("equal-content symlink targets collided")
        os.unlink(path)
        os.symlink(b"raw-\xff", path)
        raw_a = evidence()
        os.unlink(path)
        os.symlink(b"raw-\xfe", path)
        if evidence() == raw_a: raise AssertionError("raw metadata link targets collided")
        os.unlink(path)
        passed.extend(["META-01-absent-versus-broken-symlink", "META-02-regular-mode-and-byte-mutations",
                       "META-03-regular-versus-symlink-and-equal-content-targets", "META-04-raw-symlink-target-bytes"])
        for kind in ("directory", "FIFO"):
            if kind == "directory": os.mkdir(path)
            else: os.mkfifo(path)
            # Any attempt to open an unsupported object is itself a test failure;
            # the FIFO control cannot hang even if the implementation regresses.
            with mock.patch.object(module.os, "open", side_effect=AssertionError("unsupported metadata object opened")):
                try: module.metadata_object(path)
                except ValueError as exc:
                    if "UNSUPPORTED_METADATA_OBJECT" not in str(exc): raise
                else: raise AssertionError(f"unsupported metadata {kind} accepted")
            if kind == "directory": os.rmdir(path)
            else: os.unlink(path)
        passed.append("META-05-directory-and-FIFO-refused-before-open")

        # Discovery can resolve an identical-content directory through a new
        # symlink. Its lexical locator must retain that substitution evidence.
        location = parent / "locator"
        destination = parent / "directory"
        location.mkdir()
        before_topology = module.metadata_topology(os.fsencode(location))
        location.rename(destination)
        location.symlink_to(destination, target_is_directory=True)
        if module.metadata_topology(os.fsencode(location)) == before_topology:
            raise AssertionError("metadata directory/symlink topology substitution invisible")
        passed.append("META-06-directory-locator-symlink-topology")

        root = fresh_root(parent)
        original_root = module.ROOT
        module.ROOT = root
        try:
            probe, successor = entry("metadata_object_mutation"), entry("after_metadata_must_not_run")
            write_checker(root, successor, 0)
            write_checker(root, probe, 0)
            (root / probe["path"]).write_text(
                "from pathlib import Path\np=Path('.git/config')\n"
                "target=Path('.git/config-copy')\ntarget.write_bytes(p.read_bytes())\n"
                "p.unlink()\np.symlink_to('config-copy')\n", encoding="utf-8")
            run_git(root, "add", probe["path"])
            manifest = write_manifest(root, [probe, successor], ["baseline"])
            before = module.canonical_fingerprint(root)
            code, text = invoke(module, root, manifest, "--json")
            report = payload(text)
            if (code != 1 or report["failure_kind"] != "ISOLATED_PROOF_FAILURE"
                    or len(report["results"]) != 1 or report["results"][0]["isolated_proof"] == "MATCH"
                    or "UNSAFE_GIT_CONTROL" not in report["results"][0].get("proof_error", "")
                    or report["canonical_proof"] != "MATCH" or module.canonical_fingerprint(root) != before):
                raise AssertionError(f"equal-byte config symlink mutation accepted or continued: {report}")
            config = root / ".git/config"
            contents = config.read_bytes()
            copy = parent / "config-copy"
            copy.write_bytes(contents)
            config.unlink()
            config.symlink_to(copy)
            try: module.canonical_fingerprint(root)
            except ValueError as exc:
                if "UNSAFE_GIT_CONTROL" not in str(exc): raise
            else: raise AssertionError("config symlink passed fresh safety admission")
            passed.append("META-07-config-equal-byte-symlink-fingerprint-and-aggregate-stop")
        finally:
            module.ROOT = original_root
    return passed


def topology_catalog_cases(module: Any) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="glyph-catalog-contract-") as directory:
        root = fresh_root(Path(directory))
        module.ROOT = root
        initial = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        baseline = entry("generated_baseline_artifact")
        baseline["path"] = "tools/check_glyph_generated_source_owned_baseline_artifact.py"
        baseline["command"] = ["python3", baseline["path"]]
        run_git(root, "switch", "-c", "catalog-feature")
        (root / "feature.md").write_text("different feature", encoding="utf-8")
        run_git(root, "add", "feature.md"); run_git(root, "commit", "-m", "feature")
        feature = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        run_git(root, "update-ref", "refs/remotes/origin/configurator", feature)
        refs, roots = module.required_catalog([baseline])
        if refs != {"refs/heads/configurator": initial} or roots != {initial}:
            raise AssertionError("local configurator was aliased to source HEAD or origin")
        run_git(root, "update-ref", "-d", "refs/heads/configurator")
        try: module.required_catalog([baseline])
        except ValueError: pass
        else: raise AssertionError("missing source local configurator was synthesized")
        run_git(root, "update-ref", "refs/heads/configurator", initial)
        observations = entry("build_input_resolution_observations")
        observations["path"] = "tools/check_glyph_build_input_resolution_observations.py"
        observations["command"] = ["python3", observations["path"]]
        nuker = entry("nuker_source_lineage")
        nuker["path"] = "tools/check_glyph_nuker_source_lineage.py"; nuker["command"] = ["python3", nuker["path"]]
        refs, roots = module.required_catalog([observations, nuker])
        if refs or roots != {"8c04262c66613d46b933b1b739c01c575cb0c580", "ffc007552abc848051841362b0b0ac4c1a7d087b", "a747dd54b02b207483142331d8b5be1113fc951e", "d5050847d3f850951b3f47865dc8a91aedea0834"}:
            raise AssertionError("fixed current-source roots differ")
    return ["ISO-12-exact-local-configurator-ref-and-missing-ref-failure",
            "ISO-14-fixed-build-resolution-and-nuker-source-roots"]


def historical_policy_dependency_cases(module: Any) -> list[str]:
    """Current dependencies exclude personal workflow; historical evidence remains admissible."""
    actual_root = RUNNER_PATH.resolve().parents[1]
    relative = "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
    actual = json.loads((actual_root / relative).read_text())
    baseline = json.loads(subprocess.check_output([
        "git", "show", "11e7d4e4f8f7d3a9ddf35cb9bb5097ae5e70dc25:" + relative,
    ], cwd=actual_root))
    # Dependency migration must not change any command or classification field.
    without_dependencies = lambda rows: [
        {key: value for key, value in row.items() if key != "source_dependencies"}
        for row in rows
    ]
    if without_dependencies(actual["entries"]) != without_dependencies(baseline["entries"]):
        raise AssertionError("F3 changed manifest commands/classifications")
    current = [row for row in actual["entries"] if row["applicability"] == "current"]
    if len(current) != 23 or not all(row["load_bearing"] and not row["historical"] for row in current):
        raise AssertionError("F3 current classification count drift")
    legacy = ("docs/WORKFLOW.md", "docs/AGENT_CONTEXT.md")
    for row in current:
        for path in legacy:
            if path in row["source_dependencies"]:
                raise AssertionError(f"current legacy policy dependency: {row['id']}: {path}")
    legacy_hardware = (
        "docs/agent_framework/HARDWARE_ARTIFACT_CUSTODY.md",
        "docs/agent_framework/HARDWARE_EVIDENCE.md",
    )
    retained = (
        "docs/project/ACTIVE_AGENT_QUEUE.md",
        "docs/agent_framework/curation_receipts/gp_val037_current_arguments_20261003.json",
        "docs/agent_framework/GP_VAL_041_FINITE_SCOPE_CURATOR_20261004.md",
        "docs/agent_framework/other.md",
    )
    allowed_current = (
        "docs/evidence/HARDWARE_EVIDENCE.md",
        "docs/runtime_config/fixtures/source_owned_x1_authority_receipt.json",
        "docs/DEVELOPMENT.md",
    )
    legacy_authority = ("docs/agent_framework/USER_DIRECTION.md",)
    for row in current:
        for path in legacy_authority:
            if path in row["source_dependencies"]:
                raise AssertionError(f"current legacy authority dependency: {row['id']}: {path}")
    f3 = json.loads(subprocess.check_output([
        "git", "show", "f6a4c68e0b7db689e6126343d48d60f0336e7694:" + relative,
    ], cwd=actual_root))
    expected = json.loads(json.dumps(f3))
    authority = next(row for row in expected["entries"] if row["id"] == "source_authority_intake")
    authority["source_dependencies"] = [
        "docs/runtime_config/fixtures/source_owned_x1_authority_receipt.json"
        if path == legacy_authority[0] else path for path in authority["source_dependencies"]
    ] + ["docs/runtime_config/fixtures/source_owned_source_authority_intake.json"]
    f4 = json.loads(subprocess.check_output([
        "git", "show", "367785cfe02d883c185327cfface06c37307f2b3:" + relative,
    ], cwd=actual_root))
    if f4 != expected:
        raise AssertionError("F4 source-authority migration drift")
    expected = json.loads(json.dumps(f4))
    hardware = next(row for row in expected["entries"] if row["id"] == "hardware_artifact_custody")
    if hardware["source_dependencies"][2:4] != list(legacy_hardware):
        raise AssertionError("F5 unexpected starting hardware dependencies")
    hardware["source_dependencies"][2:4] = ["docs/evidence/HARDWARE_EVIDENCE.md"]
    f5 = json.loads(subprocess.check_output([
        "git", "show", "f5ffb297bf74d5f41cca206d20dfa794139bea74:" + relative,
    ], cwd=actual_root))
    if f5 != expected:
        raise AssertionError("F5 manifest changed beyond hardware dependency migration")
    expected = json.loads(json.dumps(f5))
    removals = {
        "checker_context": (
            "docs/agent_framework/GP_VAL_041_FINITE_SCOPE_CURATOR_20261004.md",
            "docs/agent_framework/curation_receipts/gp_val037_current_arguments_20261003.json",
            "docs/agent_framework/curation_receipts/gp_val037_guard_applicability_20261003.json",
            "docs/agent_framework/curation_receipts/gp_val037_predecessor_20261003.json",
            "docs/agent_framework/curation_receipts/gp_val041_finite_scope_20261004.json",
            "docs/project/ACTIVE_AGENT_QUEUE.md",
        ),
        "validation_aggregate_adversarial": (
            "docs/agent_framework/curation_receipts/gp_val037_current_arguments_20261003.json",
            "docs/agent_framework/curation_receipts/gp_val037_guard_applicability_20261003.json",
            "docs/agent_framework/curation_receipts/gp_val037_predecessor_20261003.json",
            "docs/project/ACTIVE_AGENT_QUEUE.md",
        ),
    }
    for row in expected["entries"]:
        if row["id"] in removals:
            paths = removals[row["id"]]
            if any(row["source_dependencies"].count(path) != 1 for path in paths):
                raise AssertionError("F6 unexpected starting dependencies: " + row["id"])
            row["source_dependencies"] = [path for path in row["source_dependencies"] if path not in paths]
    if actual != expected:
        raise AssertionError("F6 manifest changed beyond exact 6+4 dependency removal")
    c023 = lambda manifest: next(row for row in manifest["entries"]
                               if row["id"] == "gp_config023_usb_index_validation")
    if c023(actual) != c023(f5):
        raise AssertionError("F6 changed the C023 entry/dependencies")
    for row in current:
        for path in row["source_dependencies"]:
            if path.startswith("docs/agent_framework/") or path == "docs/project/ACTIVE_AGENT_QUEUE.md":
                raise AssertionError(f"current internal workflow dependency: {row['id']}: {path}")
    if hardware["applicability"] != "current" or hardware["load_bearing"] is not True:
        raise AssertionError("F5 custody must remain current/load-bearing")
    for row in current:
        for path in legacy_hardware:
            if path in row["source_dependencies"]:
                raise AssertionError(f"current legacy hardware dependency: {row['id']}: {path}")
    if authority["applicability"] != "current" or authority["load_bearing"] is not True:
        raise AssertionError("F4 source authority is no longer current/load-bearing")
    with tempfile.TemporaryDirectory(prefix="glyph-current-policy-dependencies-") as directory:
        root = fresh_root(Path(directory))
        module.ROOT = root
        for path in (*legacy, *legacy_authority, *legacy_hardware, *retained, *allowed_current):
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("retained synthetic evidence\n", encoding="utf-8")
            run_git(root, "add", path)
        probe = entry("current_policy_probe")
        write_checker(root, probe, 0)
        for path in legacy:
            probe["source_dependencies"] = [path]
            manifest = write_manifest(root, [probe], ["baseline"])
            assert_manifest_failure(module, root, manifest,
                                    f"legacy current policy dependency: {probe['id']}: {path}")
        for path in legacy_authority:
            probe["source_dependencies"] = [path]
            manifest = write_manifest(root, [probe], ["baseline"])
            assert_manifest_failure(module, root, manifest,
                                    f"legacy current authority dependency: {probe['id']}: {path}")
        for path in legacy_hardware:
            probe["source_dependencies"] = [path]
            manifest = write_manifest(root, [probe], ["baseline"])
            assert_manifest_failure(module, root, manifest,
                                    f"legacy current hardware contract dependency: {probe['id']}: {path}")
        for path in retained:
            probe["source_dependencies"] = [path]
            manifest = write_manifest(root, [probe], ["baseline"])
            assert_manifest_failure(module, root, manifest,
                                    f"legacy current internal workflow dependency: {probe['id']}: {path}")
        historical = entry("historical_policy_probe", applicability="historical_only",
                           historical=True, load_bearing=False)
        historical["branch_policy"] = "named_evidence_branch"
        historical["source_dependencies"] = list((*legacy, *legacy_authority, *legacy_hardware, *retained))
        write_checker(root, historical, 9)
        for path in allowed_current:
            probe["source_dependencies"] = [path]
            manifest = write_manifest(root, [probe, historical], ["baseline"])
            code, text = invoke(module, root, manifest, "--check-manifest")
            if code or "glyph_runtime_config_validation_manifest: PASS; entries=2;" not in text:
                raise AssertionError("current public contract or historical workflow rejected: " + text)
    return ["F6-exact-F5-manifest-delta-only-6-plus-4-removals-C023-unchanged",
            "F6-current-manifest-personal-orchestration-dependencies-zero",
            "F6-current-internal-workflow-rejected-with-checker-and-path",
            "F6-historical-workflow-and-current-public-contracts-allowed",
            "F5-current-hardware-legacy-rejected-with-identity-historical-allowed",
            "F5-only-custody-dependencies-migrated-23-classifications-unchanged",
            "F3-current-manifest-no-legacy-policy-dependencies",
            "F3-current-workflow-and-agent-context-rejected-with-identity",
            "F3-historical-policy-and-current-public-contracts-allowed",
            "F4-current-no-legacy-authority-dependency-rejected-with-identity",
            "F4-historical-authority-and-current-public-contracts-allowed",
            "F4-only-source-authority-dependencies-migrated-current-load-bearing",
            "F3-all-23-current-classifications-and-all-commands-unchanged"]


def current_policy_dependency_cases(module: Any) -> list[str]:
    """Current public boundary probes; migration correspondence is historical."""
    actual_root = RUNNER_PATH.resolve().parents[1]
    actual = json.loads((actual_root / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json").read_text())
    module.package_scope.public_contract(actual_root)
    module.package_scope.verify_manifest_coverage(actual_root, actual["entries"])
    current = [row for row in actual["entries"] if row["applicability"] == "current"]
    if not current or not all(row["load_bearing"] and not row["historical"] for row in current):
        raise AssertionError("current load-bearing classification drift")
    legacy = ("docs/WORKFLOW.md", "docs/AGENT_CONTEXT.md")
    legacy_hardware = ("docs/agent_framework/HARDWARE_ARTIFACT_CUSTODY.md",
                       "docs/agent_framework/HARDWARE_EVIDENCE.md")
    legacy_authority = ("docs/agent_framework/USER_DIRECTION.md",)
    retained = ("docs/project/ACTIVE_AGENT_QUEUE.md",
                "docs/agent_framework/curation_receipts/gp_val037_current_arguments_20261003.json",
                "docs/agent_framework/GP_VAL_041_FINITE_SCOPE_CURATOR_20261004.md",
                "docs/agent_framework/other.md")
    allowed_current = ("docs/evidence/HARDWARE_EVIDENCE.md",
                       "docs/runtime_config/fixtures/source_owned_x1_authority_receipt.json",
                       "docs/DEVELOPMENT.md")
    for row in current:
        for path in row["source_dependencies"]:
            if (path in (*legacy, *legacy_hardware, *legacy_authority) or
                    path.startswith(("docs/agent_framework/", "docs/project/"))):
                raise AssertionError(f"current internal dependency: {row['id']}: {path}")
    with tempfile.TemporaryDirectory(prefix="glyph-current-policy-dependencies-") as directory:
        root = fresh_root(Path(directory))
        module.ROOT = root
        for path in (*legacy, *legacy_authority, *legacy_hardware, *retained, *allowed_current):
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("retained synthetic evidence\n", encoding="utf-8")
            run_git(root, "add", path)
        probe = entry("current_policy_probe")
        write_checker(root, probe, 0)
        for path in legacy:
            probe["source_dependencies"] = [path]
            manifest = write_manifest(root, [probe], ["baseline"])
            assert_manifest_failure(module, root, manifest,
                                    f"legacy current policy dependency: {probe['id']}: {path}")
        for path in legacy_authority:
            probe["source_dependencies"] = [path]
            manifest = write_manifest(root, [probe], ["baseline"])
            assert_manifest_failure(module, root, manifest,
                                    f"legacy current authority dependency: {probe['id']}: {path}")
        for path in legacy_hardware:
            probe["source_dependencies"] = [path]
            manifest = write_manifest(root, [probe], ["baseline"])
            assert_manifest_failure(module, root, manifest,
                                    f"legacy current hardware contract dependency: {probe['id']}: {path}")
        for path in retained:
            probe["source_dependencies"] = [path]
            manifest = write_manifest(root, [probe], ["baseline"])
            assert_manifest_failure(module, root, manifest,
                                    f"legacy current internal workflow dependency: {probe['id']}: {path}")
        historical = entry("historical_policy_probe", applicability="historical_only",
                           historical=True, load_bearing=False)
        historical["branch_policy"] = "named_evidence_branch"
        historical["source_dependencies"] = list((*legacy, *legacy_authority, *legacy_hardware, *retained))
        write_checker(root, historical, 9)
        for path in allowed_current:
            probe["source_dependencies"] = [path]
            manifest = write_manifest(root, [probe, historical], ["baseline"])
            code, text = invoke(module, root, manifest, "--check-manifest")
            if code or "glyph_runtime_config_validation_manifest: PASS; entries=2;" not in text:
                raise AssertionError("current public contract or historical workflow rejected: " + text)
    return ["G2B-current-manifest-exact-sealed-contract",
            "G2B-current-public-dependency-boundaries-and-negatives",
            "G2B-historical-evidence-admissible-without-current-authority"]



def historical_orchestration_retirement_cases(module: Any) -> list[str]:
    """Retained protocols neither execute nor supply roots to current validation."""
    actual_root = RUNNER_PATH.resolve().parents[1]
    entries = json.loads((actual_root / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json").read_text())["entries"]
    by_id = {row["id"]: row for row in entries}
    retired = []
    for identity, filename in (
        ("agent_framework", "check_glyph_agent_framework_docs.py"),
        ("agentic_sequence", "check_glyph_agentic_sequence_protocol.py"),
    ):
        row = by_id[identity]
        if (row["applicability"] != "historical_only" or row["branch_policy"] != "named_evidence_branch"
                or row["load_bearing"] is not False or row["historical"] is not True
                or row["command"] != ["python3", "tools/" + filename]):
            raise AssertionError("retained orchestration classification/command drift: " + identity)
        retired.append(row.copy())
    for identity in ("hardware_artifact_custody", "checker_context", "validation_aggregate_adversarial",
                     "source_authority_intake", "build_input_provenance_inventory", "prebuild_git_identity",
                     "gp_config023_usb_index_validation", "docs_navigation"):
        row = by_id[identity]
        if row["applicability"] != "current" or row["load_bearing"] is not True or row["historical"] is not False:
            raise AssertionError("required current safety classification drift: " + identity)
    # The current package C023 replay still receives exactly its authenticated
    # finite roots plus the retained milestone and GP-VAL roots. Retired entries
    # cannot add queue-derived roots to that selection.
    import glyph_campaign_transition as campaign
    if module.package_scope.package_lineage(actual_root):
        finite = frozenset({"a" * 40, "b" * 40})
        proof = {"contract": "c023_usb_index", "object_roots": finite}
        with mock.patch.object(module, "ROOT", actual_root), mock.patch.object(
                module.package_scope, "original_proof", return_value=proof) as authenticated, mock.patch.object(
                campaign, "authenticate", side_effect=AssertionError("current C023 used predecessor proof")):
            for selected in ([by_id["gp_config023_usb_index_validation"]],
                             [by_id["gp_config023_usb_index_validation"], *retired]):
                if module.required_catalog(selected) != ({}, set(campaign.ROOTS) | set(finite) | {module.package_scope.C023_DONE}):
                    raise AssertionError("current authenticated package replay roots changed")
            if authenticated.call_count != 2 or any(call.args[0] != actual_root for call in authenticated.call_args_list):
                raise AssertionError("current package replay did not authenticate its exact source")
            for selected in ([by_id["checker_context"]], [by_id["checker_context"], *retired]):
                if module.required_catalog(selected) != ({}, set()):
                    raise AssertionError("current package context acquired campaign/orchestration roots")
            if authenticated.call_count != 2:
                raise AssertionError("current package context invoked C023 authentication")
            authenticated.side_effect = ValueError("package replay authority unavailable")
            try:
                module.required_catalog([by_id["gp_config023_usb_index_validation"], *retired])
            except ValueError:
                pass
            else:
                raise AssertionError("current package replay authentication failed open")
    with tempfile.TemporaryDirectory(prefix="glyph-orchestration-retirement-") as directory:
        root = fresh_root(Path(directory))
        module.ROOT = root
        # No queue exists here. Catalog selection must not even attempt a Git
        # read for either retained protocol, individually or together.
        with mock.patch.object(module, "git", side_effect=AssertionError("historical catalog read Git")), mock.patch.object(
                module, "git_value", side_effect=AssertionError("historical catalog read a queue/root")):
            for selected in ([retired[0]], [retired[1]], retired):
                if module.required_catalog(selected) != ({}, set()):
                    raise AssertionError("historical orchestration contributed catalog roots")
        current = entry("current_retirement_sentinel")
        write_checker(root, current, 0)
        for row in retired:
            write_checker(root, row, 9)
        manifest = write_manifest(root, [current, *retired], ["baseline", "agent_framework"])
        code, text = invoke(module, root, manifest, "--json")
        report = payload(text)
        if (code or report["status"] != "PASS" or report["canonical_proof"] != "MATCH"
                or [row["id"] for row in report["results"]] != [current["id"]]):
            raise AssertionError("normal aggregate selected/executed retained orchestration: " + text)
    return ["F2-historical-framework-and-sequence-not-selected-or-executed",
            "F2-historical-orchestration-contributes-no-catalog-roots",
            "F2-current-package-replay-exact-authenticated-roots-and-fail-closed",
            "F2-current-custody-authority-context-replay-and-public-docs-classifications"]


def orchestration_retirement_cases(module: Any) -> list[str]:
    """Retained protocols neither execute nor supply roots to current validation."""
    actual_root = RUNNER_PATH.resolve().parents[1]
    entries = json.loads((actual_root / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json").read_text())["entries"]
    by_id = {row["id"]: row for row in entries}
    retired = []
    for identity, filename in (
        ("agent_framework", "check_glyph_agent_framework_docs.py"),
        ("agentic_sequence", "check_glyph_agentic_sequence_protocol.py"),
    ):
        row = by_id[identity]
        if (row["applicability"] != "historical_only" or row["branch_policy"] != "named_evidence_branch"
                or row["load_bearing"] is not False or row["historical"] is not True
                or row["command"] != ["python3", "tools/" + filename]):
            raise AssertionError("retained orchestration classification/command drift: " + identity)
        retired.append(row.copy())
    for identity in ("hardware_artifact_custody", "checker_context", "validation_aggregate_adversarial",
                     "source_authority_intake", "build_input_provenance_inventory", "prebuild_git_identity",
                     "gp_config023_usb_index_validation", "docs_navigation"):
        row = by_id[identity]
        if row["applicability"] != "current" or row["load_bearing"] is not True or row["historical"] is not False:
            raise AssertionError("required current safety classification drift: " + identity)
    # The source-bound current C023 replacement and context guard require no
    # development roots; retained protocols must not add any. Authenticate the
    # positive contract first, and make any historical replay call fatal here.
    module.package_scope.public_contract(actual_root)
    with mock.patch.object(module, "ROOT", actual_root), mock.patch.object(
            module.package_scope, "original_proof", side_effect=AssertionError("current invoked historical C023")):
        for selected in ([by_id["gp_config023_usb_index_validation"]],
                         [by_id["gp_config023_usb_index_validation"], *retired],
                         [by_id["checker_context"]], [by_id["checker_context"], *retired]):
            if module.required_catalog(selected) != ({}, set()):
                raise AssertionError("current public proof acquired development history roots")
    with tempfile.TemporaryDirectory(prefix="glyph-orchestration-retirement-") as directory:
        root = fresh_root(Path(directory))
        module.ROOT = root
        # No queue exists here. Catalog selection must not even attempt a Git
        # read for either retained protocol, individually or together.
        with mock.patch.object(module, "git", side_effect=AssertionError("historical catalog read Git")), mock.patch.object(
                module, "git_value", side_effect=AssertionError("historical catalog read a queue/root")):
            for selected in ([retired[0]], [retired[1]], retired):
                if module.required_catalog(selected) != ({}, set()):
                    raise AssertionError("historical orchestration contributed catalog roots")
        current = entry("current_retirement_sentinel")
        write_checker(root, current, 0)
        for row in retired:
            write_checker(root, row, 9)
        manifest = write_manifest(root, [current, *retired], ["baseline", "agent_framework"])
        code, text = invoke(module, root, manifest, "--json")
        report = payload(text)
        if (code or report["status"] != "PASS" or report["canonical_proof"] != "MATCH"
                or [row["id"] for row in report["results"]] != [current["id"]]):
            raise AssertionError("normal aggregate selected/executed retained orchestration: " + text)
    return ["F2-historical-framework-and-sequence-not-selected-or-executed",
            "F2-historical-orchestration-contributes-no-catalog-roots",
            "G2B-current-C023-and-context-select-no-development-roots",
            "G2B-current-safety-classifications-retained"]



def gp_config_010_historical_object_cases(module: Any) -> list[str]:
    """The exact selected checker alone receives its locally complete historical commit."""
    with tempfile.TemporaryDirectory(prefix="glyph-config-010-object-contract-") as directory:
        parent = Path(directory)
        root = fresh_root(parent)
        module.ROOT = root
        initial = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

        def off_head_commit(branch: str, filename: str) -> str:
            run_git(root, "switch", "-c", branch)
            (root / filename).write_text(branch + "\n", encoding="utf-8")
            run_git(root, "add", filename)
            run_git(root, "commit", "-m", branch)
            identity = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            run_git(root, "switch", "configurator")
            run_git(root, "branch", "-D", branch)
            return identity

        historical = off_head_commit("historical-candidate", "historical.txt")
        substitute = off_head_commit("substitute-candidate", "substitute.txt")
        semantic = entry("gp_config_010_integration_semantic_correspondence")
        semantic["path"] = module.GP_CONFIG_010_SEMANTIC_COMMAND[1]
        semantic["command"] = module.GP_CONFIG_010_SEMANTIC_COMMAND[:]
        unrelated = entry("unrelated")
        wrong_id = entry("near_semantic")
        wrong_id["path"], wrong_id["command"] = semantic["path"], semantic["command"][:]
        wrong_command = dict(semantic)
        wrong_command["command"] = ["python3", "tools/check_glyph_other.py"]
        original_candidate = module.GP_CONFIG_010_HISTORICAL_CANDIDATE
        original_env = module.EXECUTION_ENV
        try:
            module.GP_CONFIG_010_HISTORICAL_CANDIDATE = historical
            refs, roots = module.required_catalog([semantic])
            if refs or roots != {historical}:
                raise AssertionError("exact GP-CONFIG-010 checker did not select only its historical root")
            for selected in ([unrelated], [wrong_id], [wrong_command]):
                refs, roots = module.required_catalog(selected)
                if refs or roots:
                    raise AssertionError("unrelated or altered checker received historical root/ref")
            module.GP_CONFIG_010_HISTORICAL_CANDIDATE = "0" * 40
            try:
                module.immutable_source_context([semantic])
            except ValueError as exc:
                if "0000000000000000000000000000000000000000^{commit}" not in str(exc):
                    raise
            else:
                raise AssertionError("missing local historical commit was accepted")
            module.GP_CONFIG_010_HISTORICAL_CANDIDATE = historical
            context = module.immutable_source_context([semantic])
            if historical not in context["object_roots"] or context["required_refs"]:
                raise AssertionError("historical root/ref context differs")

            def isolated_clone(label: str, roots: list[str]) -> Path:
                location = parent / label
                location.mkdir()
                module.EXECUTION_ENV = module.isolated_environment(location)
                altered = dict(context)
                altered["object_roots"] = roots
                return module.clone_snapshot(altered, location)

            without = isolated_clone("without", [root_id for root_id in context["object_roots"] if root_id != historical])
            replaced = isolated_clone("replaced", [root_id for root_id in context["object_roots"] if root_id != historical] + [substitute])
            with_historical = isolated_clone("with", context["object_roots"])
            for clone in (without, replaced):
                if module.git("cat-file", "-e", f"{historical}^{{commit}}", cwd=clone).returncode == 0:
                    raise AssertionError("omitted/substituted transfer satisfied exact historical identity")
            if module.git_value("cat-file", "-t", historical, cwd=with_historical) != "commit":
                raise AssertionError("exact historical commit was not imported")
            if any(line.startswith("?") for line in module.git_value(
                    "rev-list", "--objects", "--missing=print", historical, cwd=with_historical).splitlines()):
                raise AssertionError("historical closure incomplete")
            expected_refs = {"refs/heads/configurator": initial, "refs/remotes/origin/configurator": initial}
            for clone in (without, replaced, with_historical):
                observed = dict(line.split(" ", 1) for line in module.git_value(
                    "for-each-ref", "--format=%(refname) %(objectname)", cwd=clone).splitlines())
                if observed != expected_refs:
                    raise AssertionError("historical transfer introduced or changed a ref")
            def object_ids(clone: Path) -> set[str]:
                return set(module.git_value("cat-file", "--batch-all-objects", "--batch-check=%(objectname)", cwd=clone).splitlines())
            added = object_ids(with_historical) - object_ids(without)
            closure = {line.split(" ", 1)[0] for line in module.git_value(
                "rev-list", "--objects", historical, "--not", initial).splitlines()}
            if added != closure:
                raise AssertionError(f"historical transfer object delta exceeds exact required closure: {added ^ closure}")
        finally:
            module.GP_CONFIG_010_HISTORICAL_CANDIDATE = original_candidate
            module.EXECUTION_ENV = original_env
    return ["ISO-15-exact-config-010-selection-and-local-failure",
            "ISO-16-config-010-omission-substitution-bounded-closure-and-no-ref"]

def gp_val037_campaign_catalog_cases(module: Any) -> list[str]:
    """Actual adopted authority selects finite roots without the framework checker."""
    import glyph_campaign_transition as campaign
    from glyph_hardware_correspondence import CorrespondenceError

    original_root, original_env = module.ROOT, module.EXECUTION_ENV
    module.ROOT = RUNNER_PATH.resolve().parent.parent
    consumers = {
        "gp_config_012_button_mask_characterization": "check_glyph_gp_config012_button_mask_characterization.py",
        "gp_config_013_usb_default_characterization": "check_glyph_gp_config013_usb_default_characterization.py",
        "gp_config_010_integration_semantic_correspondence": "check_glyph_config_010_integration_semantic_correspondence.py",
        "configurator_setconfig_transaction": "check_glyph_configurator_setconfig_transaction.py",
        "current_config_persistence_recovery_research": "check_glyph_current_config_persistence_recovery_research.py",
        "getconfig_raw_load_characterization": "check_glyph_getconfig_raw_load_characterization.py",
        "setconfig_runtime_rebinding_characterization": "check_glyph_setconfig_runtime_rebinding_characterization.py",
        "config_menu_invalid_state_characterization": "check_glyph_config_menu_invalid_state_characterization.py",
        "checker_context": "check_glyph_checker_context.py",
        "generated_source_contract": "check_glyph_generated_source_owned_generator_contract.py",
        "generated_baseline_artifact": "check_glyph_generated_source_owned_baseline_artifact.py",
        "artifact_install": "check_glyph_generated_source_owned_artifact_install.py",
        "coordinate_native_contract": "check_glyph_coordinate_native_runtime_profile_contract.py",
        "docs_agent_surface": "check_glyph_docs_agent_surface.py",
        "campaign_webserial_source_authority": "check_glyph_runtime_config_webserial_device_write_source_authority.py",
        "custom_modifier_cache_characterization": "check_glyph_custom_modifier_cache_characterization.py",
        "gp_config014_modifier_capacity": "check_glyph_gp_config014_modifier_capacity.py",
        "gp_val034_c014_transition": "test_glyph_c014_campaign_transition.py",
    }
    expected = set(campaign.ROOTS)
    current_argument_authority = {
        "32280bc9eadfcd7fbcc19bd8df60576e3b0a49eb",
        "6cb59e97ddfdb96830432923ac588a76383153b7",
        "93b3c9ee8f702886f731714281ce143428724a17",
    }
    if not current_argument_authority <= expected:
        raise AssertionError("campaign catalog omitted exact current-argument opening/receipt/adoption")
    # The combined selection calls the actual phase authenticator once. The
    # per-consumer tests below isolate selection wiring using that exact proof,
    # guarded by the same complete repository fingerprint throughout.
    selected_entries = []
    for checker_id, filename in consumers.items():
        selected = entry(checker_id)
        selected["path"] = "tools/" + filename
        selected["command"] = ["python3", selected["path"]]
        if checker_id == "campaign_webserial_source_authority":
            selected["command"].append("--campaign-transition")
        selected_entries.append(selected)
    before = module.canonical_fingerprint()
    actual_authenticate = campaign.authenticate
    authenticated_proofs = []
    def authenticate_phase(root):
        proof = actual_authenticate(root)
        authenticated_proofs.append(proof)
        return proof
    try:
        with mock.patch.object(campaign, "authenticate", side_effect=authenticate_phase) as authenticated:
            combined_refs, combined_roots = module.required_catalog(selected_entries)
            authenticated.assert_called_once_with(module.ROOT)
        if len(authenticated_proofs) != 1 or module.canonical_fingerprint() != before:
            raise AssertionError("actual catalog phase authentication changed repository")
        proof = authenticated_proofs[0]
        if proof.get('contract') in {'c020_abi_repair', 'c014_capacity'}:
            expected.update(proof['object_roots'])
        else:
            catalog_path = module.ROOT / campaign.TRANSITIONS
            if catalog_path.exists():
                for record in json.loads(catalog_path.read_text())["accepted_transitions"]:
                    expected.update(record[key] for key in ("build", "parent", "review_commit", "evidence_commit", "integration"))
        configurator = module.git_value("rev-parse", "--verify", "refs/heads/configurator^{commit}")
        if (combined_roots != expected | {configurator, module.GP_CONFIG_010_HISTORICAL_CANDIDATE}
                or combined_refs != {"refs/heads/configurator": configurator}):
            raise AssertionError("actual combined catalog selection differs")
        def unchanged_phase_proof(root):
            if root != module.ROOT:
                raise AssertionError("selection attempted to reuse proof for another repository")
            return authenticated_proofs[0]
        for selected in selected_entries:
            checker_id = selected["id"]
            with mock.patch.object(campaign, "authenticate", side_effect=unchanged_phase_proof) as authenticated:
                refs, roots = module.required_catalog([selected])
                authenticated.assert_called_once_with(module.ROOT)
            wanted = expected.copy()
            wanted_refs = {}
            if checker_id == "gp_config_010_integration_semantic_correspondence":
                wanted.add(module.GP_CONFIG_010_HISTORICAL_CANDIDATE)
            if checker_id == "generated_baseline_artifact":
                identity = module.git_value("rev-parse", "--verify", "refs/heads/configurator^{commit}")
                wanted.add(identity)
                wanted_refs["refs/heads/configurator"] = identity
            if roots != wanted or refs != wanted_refs:
                raise AssertionError("campaign consumer finite catalog differs: " + checker_id)
            for altered in ({**selected, "id": checker_id + "_lookalike"},
                            {**selected, "command": selected["command"] + ["--unexpected"]}):
                with mock.patch.object(campaign, "authenticate", side_effect=AssertionError("near-match authenticated")):
                    if module.required_catalog([altered]) != ({}, set()):
                        raise AssertionError("near-match consumer received catalog roots")
        if module.canonical_fingerprint() != before:
            raise AssertionError("per-consumer selection changed authenticated repository")
        guard = selected_entries[-1]
        with mock.patch.object(campaign, "authenticate", side_effect=CorrespondenceError("authority deliberately unavailable")):
            try:
                module.required_catalog([guard])
            except CorrespondenceError:
                pass
            else:
                raise AssertionError("campaign authentication failure became empty/accepted catalog")
        with tempfile.TemporaryDirectory(prefix="glyph-val037-catalog-closure-") as directory:
            parent = Path(directory)
            closure = {line.split(" ", 1)[0] for line in module.git_value(
                "rev-list", "--objects", *sorted(expected)).splitlines()}
            # Pack only selected immutable closures, never all refs or alternates.
            # Accepted-phase roots can also descend from C. Remove every root
            # that carries C for the omission control, retaining all other roots.
            candidate = proof['candidate']
            candidate_base = proof['base']
            # Test preparation uses the same finite authenticated roots. Read
            # their complete parent graph once; each disposable import and its
            # actual object-presence/closure assertions below still run anew.
            parents = {}
            for line in module.git_value("rev-list", "--parents", *sorted(expected)).splitlines():
                identities = line.split()
                if (not identities or any(len(identity) != 40
                        or any(char not in '0123456789abcdef' for char in identity)
                        for identity in identities) or identities[0] in parents):
                    raise AssertionError("invalid finite catalog parent graph")
                parents[identities[0]] = tuple(identities[1:])
            if (not expected <= parents.keys()
                    or any(parent not in parents for edges in parents.values() for parent in edges)):
                raise AssertionError("incomplete finite catalog parent graph")
            ancestors = {}
            for identity in expected:
                visited, pending = set(), [identity]
                while pending:
                    revision = pending.pop()
                    if revision not in visited:
                        visited.add(revision)
                        pending.extend(parents[revision])
                ancestors[identity] = visited
            def carriers(missing):
                if missing not in parents:
                    raise AssertionError("missing finite catalog ancestry identity")
                return {identity for identity in expected if missing in ancestors[identity]}
            carrying_candidate = carriers(candidate)
            without_candidate = expected - carrying_candidate
            scenarios = [("complete", expected, candidate, True),
                         ("omitted", without_candidate, candidate, False),
                         ("substituted", without_candidate | {candidate_base}, candidate, False)]
            if proof.get('contract') == 'c020_abi_repair':
                from glyph_c020_abi_repair_transition import B_R, PACKET
                # Remove every selected descendant as well as the root itself:
                # retaining C_R would otherwise still carry B_R by ancestry.
                for label, missing in (("omitted-repaired-base", B_R),
                                       ("omitted-repaired-packet", PACKET)):
                    carrying = carriers(missing)
                    scenarios.append((label, expected - carrying, missing, False))
                # At E, F is deliberately off-head. Processor and immutable
                # payload roots still belong to every finite consumer's closed
                # catalog, independent of framework selection. Remove every
                # carrier so incidental ancestry cannot hide a missing root.
                from glyph_c020_abi_repair_transition import PROCESSOR_R, BUILT_F
                processor_roots = [('F', BUILT_F), ('R', PROCESSOR_R)]
                for key in ('evidence_commit', 'evidence_root'):
                    identity = proof.get(key)
                    if identity is not None:
                        processor_roots.append((key, identity))
                for label, missing in processor_roots:
                    if missing not in expected:
                        raise AssertionError('authenticated processor root omitted: ' + label)
                    carrying = carriers(missing)
                    reduced = expected - carrying
                    scenarios.append(('omitted-processor-' + label, reduced, missing, False))
                    scenarios.append(('substituted-processor-' + label,
                                      reduced | {candidate_base}, missing, False))
            # Identical finite root sets have identical immutable pack inputs.
            # Reuse only raw bytes locally; every scenario imports into its own
            # repository and independently proves presence/absence and refs.
            packs = {}
            for label, roots, checked_identity, should_exist in scenarios:
                clone = parent / label
                clone.mkdir()
                run_git(clone, "init", "-b", "catalog-test")
                packing_roots = tuple(sorted(roots))
                if packing_roots not in packs:
                    packed = subprocess.run(["git", "pack-objects", "--revs", "--stdout"],
                        cwd=module.ROOT, input=("\n".join(packing_roots) + "\n").encode(),
                        capture_output=True, check=True)
                    packs[packing_roots] = packed.stdout
                subprocess.run(["git", "index-pack", "--stdin"], cwd=clone,
                    input=packs[packing_roots], capture_output=True, check=True)
                if module.git_value("for-each-ref", "--format=%(refname)", cwd=clone):
                    raise AssertionError("campaign closure imported a ref")
                found = module.git("cat-file", "-e", checked_identity + "^{commit}", cwd=clone).returncode == 0
                if found != should_exist:
                    raise AssertionError("campaign omission/substitution root identity failure: " + label)
                if label == "complete":
                    objects = set(module.git_value("cat-file", "--batch-all-objects", "--batch-check=%(objectname)", cwd=clone).splitlines())
                    if objects != closure:
                        raise AssertionError("campaign transfer exceeded or missed exact selected closure")
                    for identity in expected:
                        if module.git_value("rev-parse", identity + "^{commit}", cwd=clone) != identity:
                            raise AssertionError("campaign exact root absent in reduced repository")
                    if any(line.startswith("?") for line in module.git_value(
                            "rev-list", "--objects", "--missing=print", *sorted(expected), cwd=clone).splitlines()):
                        raise AssertionError("campaign reduced closure missing an object")
        if module.canonical_fingerprint() != before:
            raise AssertionError("campaign catalog tests changed authenticated repository")
    finally:
        module.ROOT, module.EXECUTION_ENV = original_root, original_env
    return ["ISO-17-campaign-exact-consumer-before-framework-selection",
            "ISO-18-campaign-authority-failure-and-near-match-rejection",
            "ISO-19-campaign-reduced-closure-omission-substitution-no-ref",
            "ISO-24-repaired-base-and-immutable-packet-closure-omission"]


def gp_val043_runner_proof_cases(module: Any) -> list[str]:
    """Finite repaired proof wiring; mocked identities never establish acceptance."""
    import glyph_campaign_transition as campaign
    from glyph_hardware_correspondence import CorrespondenceError

    with tempfile.TemporaryDirectory(prefix="glyph-val043-runner-proof-") as directory:
        root = fresh_root(Path(directory))
        guard = entry("campaign_webserial_source_authority", category="candidate_safety")
        guard.update(path="tools/check_glyph_runtime_config_webserial_device_write_source_authority.py",
                     required_arguments=["--campaign-transition"], branch_policy="content_and_scope")
        guard["command"] = ["python3", guard["path"], *guard["required_arguments"]]
        write_checker(root, guard, 0)
        (root / guard["path"]).write_text(
            "import sys\nassert sys.argv[1:] == ['--campaign-transition'], sys.argv\n"
            "print('SYNTHETIC TEST ONLY: repaired proof exact argv PASS')\n")
        run_git(root, "add", guard["path"])
        manifest = write_manifest(root, [guard], ["baseline", "candidate_safety", "historical_evidence"])
        head = module.git_value("rev-parse", "HEAD", cwd=root)
        finite_roots = frozenset({head})
        proof = {"contract": "c020_abi_repair", "object_roots": finite_roots,
                 "test_only_inert_probe": True}
        with mock.patch.object(module, "ROOT", root), mock.patch.object(campaign, "ROOTS", frozenset()):
            with mock.patch.object(campaign, "authenticate", return_value=proof) as authenticated:
                if module.required_catalog([guard]) != ({}, set(finite_roots)):
                    raise AssertionError("repaired selected proof roots differ")
                authenticated.assert_called_once_with(root)
            for malformed in (None, set(finite_roots), [], frozenset(), frozenset({"0" * 39}),
                              frozenset({"A" * 40}), frozenset({1})):
                with mock.patch.object(campaign, "authenticate", return_value=dict(proof, object_roots=malformed)):
                    try:
                        module.required_catalog([guard])
                    except ValueError:
                        pass
                    else:
                        raise AssertionError("malformed repaired proof roots accepted: " + repr(malformed))
            # A mutable catalog on its own never gives this runner roots. The
            # actual helper owns catalog validation before exporting its proof.
            (root / "docs/runtime_config/fixtures/gp_val043_accepted_transitions.json").write_text(
                '{"schema_version":1,"accepted_transitions":[{"build":"' + 'b' * 40 + '"}]}\n')
            with mock.patch.object(campaign, "authenticate", return_value=proof):
                if module.required_catalog([guard]) != ({}, set(finite_roots)):
                    raise AssertionError("unauthenticated repaired catalog supplied roots")
            (root / "docs/runtime_config/fixtures/gp_val043_accepted_transitions.json").unlink()
            with mock.patch.object(campaign, "authenticate", return_value=proof):
                code, text = invoke(module, root, manifest, "--json")
            report = payload(text)
            if (code or report["canonical_proof"] != "MATCH" or len(report["results"]) != 1
                    or report["results"][0]["command"] != guard["command"]
                    or report["results"][0]["isolated_proof"] != "MATCH"
                    or report["results"][0]["status"] != "PASS"):
                raise AssertionError("repaired proof actual argv dispatch failed: " + text)
            with mock.patch.object(campaign, "authenticate", side_effect=CorrespondenceError("repaired authority unavailable")):
                code, text = invoke(module, root, manifest, "--json")
            report = payload(text)
            if (code != 1 or report["failure_kind"] != "SETUP_FAILURE"
                    or report["canonical_proof"] != "MATCH" or report["results"]):
                raise AssertionError("repaired authentication failure bypassed setup: " + text)
    return ["ISO-21-repaired-authenticated-proof-roots-and-malformed-rejection",
            "ISO-22-repaired-catalog-not-root-authority",
            "ISO-23-repaired-exact-argv-and-authentication-setup-failure"]

def gp_val034_catalog_cases(module: Any) -> list[str]:
    """New consumers select only immutable proof roots, never catalog values."""
    import glyph_campaign_transition as campaign
    with tempfile.TemporaryDirectory(prefix='glyph-val034-catalog-') as directory:
        root = fresh_root(Path(directory))
        identity = module.git_value('rev-parse', 'HEAD', cwd=root)
        proof = dict(contract='c014_capacity', object_roots=frozenset({identity}))
        consumers = (
            ('custom_modifier_cache_characterization', 'check_glyph_custom_modifier_cache_characterization.py'),
            ('gp_config014_modifier_capacity', 'check_glyph_gp_config014_modifier_capacity.py'),
            ('gp_val034_c014_transition', 'test_glyph_c014_campaign_transition.py'),
        )
        catalog = root / 'docs/runtime_config/fixtures/gp_val034_accepted_transitions.json'
        catalog.write_text('{"accepted_transitions":[{"build":"' + 'b' * 40 + '"}]}\n')
        with mock.patch.object(module, 'ROOT', root), mock.patch.object(campaign, 'ROOTS', frozenset()):
            for checker_id, filename in consumers:
                selected = entry(checker_id)
                selected.update(path='tools/' + filename, command=['python3', 'tools/' + filename])
                with mock.patch.object(campaign, 'authenticate', return_value=proof) as actual:
                    if module.required_catalog([selected]) != ({}, {identity}):
                        raise AssertionError('014 finite consumer roots differ')
                    actual.assert_called_once_with(root)
                for bad in (None, {identity}, frozenset(), frozenset({'A' * 40}), frozenset({'0' * 39})):
                    with mock.patch.object(campaign, 'authenticate', return_value=dict(proof, object_roots=bad)):
                        try:
                            module.required_catalog([selected])
                        except ValueError:
                            pass
                        else:
                            raise AssertionError('malformed014 proof roots accepted')
                for near in ({**selected, 'id': checker_id + '_alias'},
                             {**selected, 'command': selected['command'] + ['--unexpected']},
                             {**selected, 'applicability': 'historical_only'}):
                    with mock.patch.object(campaign, 'authenticate', side_effect=AssertionError('near014 selection')):
                        if module.required_catalog([near]) != ({}, set()):
                            raise AssertionError('near014 consumer granted roots')
    return ['ISO-24-014-exact-current-consumers-and-authenticated-roots',
            'ISO-25-014-malformed-roots-and-catalog-self-authority-rejected']


def gp_val037_current_argument_cases(module: Any) -> list[str]:
    """Exercise the actual load/preflight and argv path in disposable repositories.

    The inert dispatch fixture mocks only campaign authority/catalog selection;
    it is runner schema/argv compatibility proof, never a real current campaign/
    source-authority PASS. Canonical queue/curation bytes are not fixture inputs.
    """
    from copy import deepcopy
    import glyph_campaign_transition as campaign

    with tempfile.TemporaryDirectory(prefix="glyph-current-arguments-") as directory:
        root = fresh_root(Path(directory))
        guard = entry("campaign_webserial_source_authority", category="candidate_safety")
        guard.update({
            "path": "tools/check_glyph_runtime_config_webserial_device_write_source_authority.py",
            "required_arguments": ["--campaign-transition"],
            "branch_policy": "content_and_scope",
        })
        guard["command"] = ["python3", guard["path"], *guard["required_arguments"]]
        ordinary = entry("ordinary")
        write_checker(root, guard, 0)
        write_checker(root, ordinary, 0)
        categories = ["baseline", "candidate_safety", "historical_evidence"]
        manifest = write_manifest(root, [guard, ordinary], categories)

        def check_load(accepted: bool, label: str) -> None:
            with mock.patch.object(module, "ROOT", root), mock.patch.object(module, "MANIFEST", manifest), mock.patch.object(
                    module, "CENSUS", root / "docs/runtime_config/fixtures/glyph_checker_census.json"):
                try:
                    module.load()
                except ValueError:
                    if accepted:
                        raise
                else:
                    if not accepted:
                        raise AssertionError("actual load accepted " + label)

        def check_preflight(accepted: bool, label: str) -> None:
            code, text = invoke(module, root, manifest, "--check-manifest", "--json")
            report = payload(text)
            if ((code == 0) != accepted or report["results"]
                    or report["canonical_proof"] != ("UNAVAILABLE" if label == "directory" else "MATCH")
                    or (not accepted and (report["status"] != "FAIL" or report["failure_kind"] != "SETUP_FAILURE"))):
                raise AssertionError("actual preflight result differs for " + label + ": " + text)

        check_load(True, "exact guard and ordinary empty arguments")
        check_preflight(True, "exact guard and ordinary empty arguments")
        mutations = []
        for key, values in {
            "id": ["renamed_guard", 1],
            "path": [ordinary["path"], "tools/./check_glyph_runtime_config_webserial_device_write_source_authority.py", None],
            "category": ["baseline", [], None],
            "branch_policy": ["content_only", "named_evidence_branch", None],
            "applicability": ["historical_only", "unsafe_or_mutating", None],
            "load_bearing": [False, 1, "true", None],
            "historical": [True, 0, "false", None],
            "mutation_risk": ["temporary_file_only", "temporary_repository_only", "mutating", None],
            "required_arguments": [[], ["--campaign-transition", "--extra"],
                ["--campaign-transition", "--campaign-transition"], ["--extra", "--campaign-transition"],
                ["--campaign", "transition"], "--campaign-transition", [1], None],
            "command": [["python", guard["path"], "--campaign-transition"],
                ["sh", guard["path"], "--campaign-transition"], ["python3", guard["path"]],
                ["python3", guard["path"], "--campaign-transition", "--extra"],
                ["python3", "--campaign-transition", guard["path"]],
                "python3 " + guard["path"] + " --campaign-transition", [1], None],
        }.items():
            for value in values:
                mutations.append((key + "=" + repr(value), {**deepcopy(guard), key: value}))
        # Nonempty declarations remain forbidden even when generic command
        # equality holds, and an empty reserved variant cannot use that rule.
        mutations.extend([
            ("empty reserved variant", {**guard, "command": ["python3", guard["path"]], "required_arguments": []}),
            ("arbitrary matching declaration", {**ordinary, "command": ["python3", ordinary["path"], "--campaign-transition"], "required_arguments": ["--campaign-transition"]}),
            ("paired wrong path", {**guard, "path": ordinary["path"], "command": ["python3", ordinary["path"], "--campaign-transition"]}),
        ])
        for label, bad in mutations:
            manifest = write_manifest(root, [bad], categories)
            check_load(False, label)
            check_preflight(False, label)
        for label, entries in (
            ("duplicate ID", [guard, deepcopy(guard)]),
            ("reserved path collision", [guard, {**guard, "id": "alias"}]),
            ("reserved ID collision", [guard, {**ordinary, "id": guard["id"]}]),
        ):
            manifest = write_manifest(root, entries, categories)
            check_load(False, label)
            check_preflight(False, label)

        guard_path = root / guard["path"]
        for label in ("executable", "worktree-executable", "symlink", "directory", "untracked", "nonzero-stage", "parent-symlink"):
            # Restore via an ordinary write/add; no destructive Git operation.
            guard_path.write_text("# " + label + "\nraise SystemExit(0)\n")
            guard_path.chmod(0o644)
            run_git(root, "add", guard["path"])
            manifest = write_manifest(root, [guard], categories)
            if label == "executable":
                guard_path.chmod(0o755)
                run_git(root, "add", guard["path"])
            elif label == "worktree-executable":
                guard_path.chmod(0o755)
            elif label == "parent-symlink":
                (root / "tools").rename(root / "tool-alias-target")
                (root / "tools").symlink_to("tool-alias-target", target_is_directory=True)
            elif label == "symlink":
                guard_path.unlink()
                guard_path.symlink_to(Path(ordinary["path"]).name)
                run_git(root, "add", guard["path"])
            elif label == "directory":
                guard_path.unlink()
                guard_path.mkdir()
            elif label == "untracked":
                run_git(root, "update-index", "--force-remove", guard["path"])
            else:
                blob = subprocess.check_output(["git", "rev-parse", "HEAD:" + guard["path"]], cwd=root, text=True).strip()
                run_git(root, "update-index", "--force-remove", guard["path"])
                subprocess.run(["git", "update-index", "--index-info"], cwd=root, text=True,
                    input=f"100644 {blob} 1\t{guard['path']}\n", check=True, capture_output=True)
            if label != "directory":
                refresh_census(root)
            check_load(False, label)
            check_preflight(False, label)
            if label == "parent-symlink":
                (root / "tools").unlink()
                (root / "tool-alias-target").rename(root / "tools")
            if guard_path.is_symlink():
                guard_path.unlink()
            elif guard_path.is_dir():
                guard_path.rmdir()
        guard_path.write_text("import glyph_argument_helper\nraise SystemExit(0)\n")
        helper = root / "tools/glyph_argument_helper.py"
        helper.write_text("# inert dependency fixture\n")
        run_git(root, "add", guard["path"], "tools/glyph_argument_helper.py")
        manifest = write_manifest(root, [guard], categories)
        check_load(False, "missing declared direct helper")
        check_preflight(False, "missing declared direct helper")
        guard["source_dependencies"] = ["tools/glyph_argument_helper.py"]
        manifest = write_manifest(root, [guard], categories)
        check_load(True, "declared direct helper")
        check_preflight(True, "declared direct helper")

        # Keep the actual command and checker execution path. Only immutable
        # campaign authority is outside this deliberately inert fixture.
        probe = ("import os, sys, subprocess\n"
                 "assert sys.argv[1:] == ['--campaign-transition'], sys.argv\n"
                 "assert os.environ['GLYPH_CHECKER_BASE']\n"
                 "assert os.environ['GLYPH_CHECKER_EXPECTED_MERGE_BASE']\n"
                 "assert os.environ['PYTHONHASHSEED'] == '0'\n"
                 "assert os.environ['GIT_CONFIG_NOSYSTEM'] == '1'\n"
                 "assert 'GLYPH_ARGUMENT_POISON' not in os.environ\n"
                 "print('inert exact singleton argv/context probe: PASS')\n")
        guard_path.write_text(probe)
        run_git(root, "add", guard["path"])
        manifest = write_manifest(root, [guard], categories)
        with mock.patch.object(campaign, "ROOTS", frozenset()), mock.patch.object(
                campaign, "authenticate", return_value={"test_only_inert_probe": True}), mock.patch.dict(
                os.environ, {"GLYPH_ARGUMENT_POISON": "ambient must not forward"}):
            code, text = invoke(module, root, manifest, "--json")
            report = payload(text)
            if (code or report["canonical_proof"] != "MATCH" or len(report["results"]) != 1
                    or report["results"][0]["command"] != guard["command"]
                    or report["results"][0]["isolated_proof"] != "MATCH"
                    or report["results"][0]["status"] != "PASS"):
                raise AssertionError("isolated exact argv dispatch failed: " + text)
            for suffix, expected_kind in (
                ("raise SystemExit(7)\n", None),
                ("assert sys.argv[1:] == []\n", None),
                ("open('README.md', 'a').write('changed')\n", "ISOLATED_REPOSITORY_MUTATION"),
            ):
                guard_path.write_text(probe + suffix)
                run_git(root, "add", guard["path"])
                manifest = write_manifest(root, [guard], categories)
                code, text = invoke(module, root, manifest, "--json")
                report = payload(text)
                if code != 1 or report["status"] != "FAIL" or report["results"][0]["status"] != "FAIL":
                    raise AssertionError("failed/changed inert dispatch became PASS: " + text)
                if expected_kind == "ISOLATED_REPOSITORY_MUTATION" and report["failure_kind"] != expected_kind:
                    raise AssertionError("isolated mutation was not detected")
            guard_path.write_text(probe)
            run_git(root, "add", guard["path"])
            manifest = write_manifest(root, [guard], categories)
            original_clone = module.clone_snapshot
            def mutate_canonical(context_data, parent):
                clone = original_clone(context_data, parent)
                (root / "README.md").write_text("deliberate canonical mutation\n")
                return clone
            with mock.patch.object(module, "clone_snapshot", side_effect=mutate_canonical):
                code, text = invoke(module, root, manifest, "--json")
            report = payload(text)
            if (code != 1 or report["status"] != "FAIL" or report["canonical_proof"] != "MISMATCH"
                    or report["failure_kind"] != "CANONICAL_REPOSITORY_MUTATION"):
                raise AssertionError("changed canonical fingerprint became PASS: " + text)
            (root / "README.md").write_text("test\n")
        guard_path.write_text(probe + "# restored before dirty-source case\n")
        run_git(root, "add", guard["path"])
        manifest = write_manifest(root, [guard], categories)
        guard_path.write_text(probe + "# dirty checker\n")
        check_preflight(False, "dirty guard source")
    return ["AGG-23-reserved-current-tuple-load-and-preflight-negatives",
            "AGG-24-reserved-mode-stage-dependency-and-dirty-negatives",
            "ISO-20-exact-current-argument-dispatch-and-failure-proofs"]

def gp_val039_runner_cases(module: Any) -> list[str]:
    """Inert039 command/catalog probes; these never establish C022 acceptance."""
    from copy import deepcopy
    import glyph_campaign_transition as campaign
    import glyph_c022_campaign_transition as rgb_targets
    from glyph_hardware_correspondence import CorrespondenceError
    with tempfile.TemporaryDirectory(prefix='glyph-val039-runner-') as directory:
        root = fresh_root(Path(directory))
        selected = entry('gp_config022_rgb_target_validation', category='candidate_safety',
                         mutation_risk='temporary_file_only')
        path = 'tools/check_glyph_c022_proof_replay.py'
        selected.update(path=path, command=['python3', path], branch_policy='content_and_scope')
        write_checker(root, selected, 0)
        (root / path).write_text("print('SYNTHETIC039 ONLY: inert command dispatch')\n")
        run_git(root, 'add', path)
        manifest = write_manifest(root, [selected], ['baseline', 'candidate_safety', 'historical_evidence'])
        identity = module.git_value('rev-parse', 'HEAD', cwd=root)
        proof = dict(contract='c022_rgb_targets', object_roots=frozenset({identity}),
                     synthetic_runner_probe=True)
        with mock.patch.object(module, 'ROOT', root), mock.patch.object(campaign, 'ROOTS', frozenset()), mock.patch.object(rgb_targets, 'replay_covered_checker_paths', return_value=frozenset()):
            if not module.c022_replay_arguments(selected):
                raise AssertionError('exact039 default command was not admitted')
            for key, values in {
                'id': ['unknown039', 1],
                'path': ['tools/./check_glyph_c022_proof_replay.py', 'tools/check_glyph_c022_proof_replay_alias.py'],
                'command': [['python3', path, '--extra'], ['python', path], ['python3', path, '--consumer', 'recovery021']],
                'required_arguments': [['--extra'], ['--consumer', 'recovery021'], None],
                'category': ['baseline', None],
                'applicability': ['historical_only', None],
                'branch_policy': ['content_only', None],
                'load_bearing': [False, 1, None],
                'historical': [True, 0, None],
                'mutation_risk': ['none', 'temporary_repository_only', None],
            }.items():
                for value in values:
                    bad = {**deepcopy(selected), key: value}
                    try:
                        admitted = module.c022_replay_arguments(bad)
                    except (ValueError, TypeError):
                        continue
                    if admitted:
                        raise AssertionError('039 command tuple mutation accepted: ' + key + '=' + repr(value))
            for executable in (True, False):
                (root / path).chmod(0o755 if executable else 0o644)
                if executable:
                    try: module.c022_replay_arguments(selected)
                    except ValueError: pass
                    else: raise AssertionError('039 executable metadata accepted')
                else:
                    if not module.c022_replay_arguments(selected):
                        raise AssertionError('restored039 mode rejected')
            with mock.patch.object(campaign, 'authenticate', return_value=proof) as actual:
                if module.required_catalog([selected]) != ({}, {identity}):
                    raise AssertionError('039 selected roots differ from authenticated proof')
                actual.assert_called_once_with(root)
            consumers = {
                'current_config_persistence_recovery_research': 'persistence',
                'getconfig_raw_load_characterization': 'raw_get',
                'configurator_setconfig_transaction': 'transaction005',
                'setconfig_runtime_rebinding_characterization': 'rebind008',
                'config_menu_invalid_state_characterization': 'menu009',
                'gp_config_012_button_mask_characterization': 'button012',
                'gp_config_013_usb_default_characterization': 'usb013',
                'gp_config020_button_validation': 'button020',
                'gp_kbd_001_keyboard_pipeline': 'kbd001',
                'gp_config019_usb_name_selection': 'usb019',
                'neopixel_null_sendreport_characterization': 'neopixel016_017',
                'gp_config017_neopixel_repaired_current': 'neopixel016_017',
                'custom_modifier_cache_characterization': 'modifier011',
                'gp_config014_modifier_capacity': 'modifier014',
                'gp_val035_c017_transition': 'transition035',
                'gp_config021_persisted_recovery': 'recovery021',
                'gp_val038_c021_transition': 'transition038',
            }
            commands = [(key, ['python3', path, '--consumer', lane]) for key, lane in consumers.items()]
            commands.append(('gp_val039_c022_transition', ['python3', 'tools/test_glyph_c022_campaign_transition.py']))
            for key, command in commands:
                probe = {**selected, 'id': key, 'path': command[1], 'command': command}
                with mock.patch.object(campaign, 'authenticate', return_value=proof) as actual:
                    if module.required_catalog([probe]) != ({}, {identity}):
                        raise AssertionError('039 exact consumer root selection: ' + key)
                    actual.assert_called_once_with(root)
                for near in ({**probe, 'id': key + '_alias'},
                             {**probe, 'command': command + ['--extra']},
                             {**probe, 'applicability': 'historical_only'}):
                    with mock.patch.object(campaign, 'authenticate', side_effect=AssertionError('near039 selection')):
                        if module.required_catalog([near]) != ({}, set()):
                            raise AssertionError('039 near consumer granted roots')
            for bad in (None, {identity}, frozenset(), frozenset({'A' * 40}), frozenset({'0' * 39}), frozenset({1})):
                with mock.patch.object(campaign, 'authenticate', return_value=dict(proof, object_roots=bad)):
                    try: module.required_catalog([selected])
                    except ValueError: pass
                    else: raise AssertionError('039 malformed authenticated roots accepted')
            catalog = root / 'docs/runtime_config/fixtures/gp_val039_accepted_transitions.json'
            catalog.write_text('{"accepted_transitions":[{"build":"' + 'b' * 40 + '"}]}\n')
            with mock.patch.object(campaign, 'authenticate', return_value=proof):
                if module.required_catalog([selected]) != ({}, {identity}):
                    raise AssertionError('mutable039 catalog granted runner authority')
            catalog.unlink()
            with mock.patch.object(campaign, 'authenticate', return_value=proof):
                code, text = invoke(module, root, manifest, '--json')
            report = payload(text)
            if (code or report['canonical_proof'] != 'MATCH' or len(report['results']) != 1
                    or report['results'][0]['command'] != selected['command']
                    or report['results'][0]['isolated_proof'] != 'MATCH'
                    or report['results'][0]['status'] != 'PASS'):
                raise AssertionError('039 inert exact dispatch failed: ' + text)
            with mock.patch.object(campaign, 'authenticate', side_effect=CorrespondenceError('039 authority unavailable')):
                code, text = invoke(module, root, manifest, '--json')
            report = payload(text)
            if code != 1 or report['failure_kind'] != 'SETUP_FAILURE' or report['results']:
                raise AssertionError('039 authentication failure bypassed setup')
    return ['AGG-25-039-exact-command-typed-tuple-and-mode-controls',
            'ISO-26-039-all-exact-consumer-roots-and-near-miss-rejection',
            'ISO-27-039-malformed-roots-catalog-self-authority-and-inert-dispatch']


def deadline_control_cases(module: Any) -> list[str]:
    """Deterministic deadline dataflow; real process clocks live in ISO/PROC."""
    import signal
    root = RUNNER_PATH.parents[1]
    manifest = root / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
    def exhausted(*args):
        module.DEADLINE = module.monotonic() - 1
        module.require_budget("deterministic preflight exhaustion")
    for kind in ("before_stop_entry", "pending_at_stop", "pending_at_start"):
        original_stop = module.DeadlineAlarm.stop
        original_timer = signal.setitimer
        injected = []
        def stop(alarm):
            if kind == "before_stop_entry" and not injected:
                injected.append(True)
                alarm.handler(signal.SIGALRM, None)
            return original_stop(alarm)
        def timer(which, seconds, interval=0):
            if ((kind == "pending_at_stop" and seconds == 0
                    or kind == "pending_at_start" and seconds > 0) and not injected):
                injected.append(True)
                os.kill(os.getpid(), signal.SIGALRM)
            return original_timer(which, seconds, interval)
        with mock.patch.object(module, "preflight_repository_safety", exhausted), \
                mock.patch.object(module.DeadlineAlarm, "stop", stop), \
                mock.patch.object(module.signal, "setitimer", timer):
            code, text = invoke(module, root, manifest, "--json")
        report = payload(text)
        if (not injected or code != 1 or report["status"] != "FAIL"
                or report["failure_kind"] != "AGGREGATE_TIMEOUT"
                or report["canonical_proof"] != "UNAVAILABLE" or report["results"]):
            raise AssertionError("timer transition escaped or accepted: " + kind + ": " + text)
    # An inherited alarm loses elapsed cleanup time too, even without a global
    # aggregate deadline. An expired clock is reported, never re-armed afresh.
    for deadline in (None, 15.):
        for now, expected in ((12., 3.), (16., None)):
            with mock.patch.object(module, "DEADLINE", deadline), \
                    mock.patch.object(module, "monotonic", return_value=now), \
                    mock.patch.object(module.signal, "setitimer") as timer:
                expired = module.restore_operational_alarm((5., 0.), 10.)
            if expired != (expected is None):
                raise AssertionError("suspended alarm expiration lost")
            if expected is None:
                timer.assert_not_called()
            else:
                timer.assert_called_once_with(signal.ITIMER_REAL, expected, 0.)
    return ["TIMER-01-start-stop-pending-and-entry-delivery-structured-timeout",
            "TIMER-02-suspended-alarm-accounts-elapsed-time-and-expiration"]


def cleanup_proof_control_cases(module: Any) -> list[str]:
    """No repository MATCH or further work after uncertain lifecycle cleanup."""
    import signal
    with tempfile.TemporaryDirectory(prefix="glyph-cleanup-proof-controls-") as directory:
        root = fresh_root(Path(directory))
        first, later = entry("cleanup_probe"), entry("later_probe")
        write_checker(root, first, 0)
        write_checker(root, later, 0)
        manifest = write_manifest(root, [first, later], ["baseline"])
        before = module.canonical_fingerprint(root)
        for defect in ("checker", "scratch", "Git", "final_Git_alarm"):
            injected, later_calls, post_proofs, scratch_calls = [], [], [], []
            caller_proofs, final_stage, alarm_sent = [], [], []
            context = module._CLEANUP_UNPROVEN
            class LifecycleContext:
                def get(self):
                    value = context.get()
                    if defect == "final_Git_alarm" and value and injected and not alarm_sent:
                        alarm_sent.append(True)
                        os.kill(os.getpid(), signal.SIGALRM)
                    return value
                def set(self, value): return context.set(value)
                def reset(self, token): return context.reset(token)
            original_run, original_raw = module.run_checker, module.run_process
            original_fingerprint = module.canonical_fingerprint
            def run(command, *args, **kwargs):
                if len(command) > 1 and command[1] == later["path"]:
                    later_calls.append(command)
                if command[:2] == ["rm", "-rf"]:
                    scratch_calls.append(command)
                if (defect == "checker" and len(command) > 1 and command[1] == first["path"]
                        or defect == "scratch" and command[:2] == ["rm", "-rf"]):
                    injected.append(command)
                    return None, "", "injected lifecycle uncertainty", "PROCESS_CLEANUP_FAILURE", 0.
                return original_run(command, *args, **kwargs)
            def raw(command, *args, **kwargs):
                if (defect == "Git" or defect == "final_Git_alarm" and final_stage) and command[0] == "git" and not injected:
                    injected.append(command)
                    return None, b"", b"injected Git lifecycle uncertainty", "PROCESS_CLEANUP_FAILURE", 0.
                if injected:
                    raise AssertionError("new process dispatched after cleanup uncertainty")
                return original_raw(command, *args, **kwargs)
            def fingerprint(*args):
                if not args:
                    caller_proofs.append(True)
                    if len(caller_proofs) == 2: final_stage.append(True)
                if injected:
                    post_proofs.append(args)
                return original_fingerprint(*args)
            with mock.patch.object(module, "run_checker", run), \
                    mock.patch.object(module, "run_process", raw), \
                    mock.patch.object(module, "canonical_fingerprint", fingerprint), \
                    mock.patch.object(module, "_CLEANUP_UNPROVEN", LifecycleContext()):
                code, text = invoke(module, root, manifest, "--json")
            report = payload(text)
            if (code != 1 or report["status"] != "FAIL" or report["failure_kind"] != "PROCESS_CLEANUP_FAILURE"
                    or report["canonical_proof"] != "UNAVAILABLE" or not injected or post_proofs
                    or any(row["isolated_proof"] == "MATCH" for row in report["results"])):
                raise AssertionError("cleanup uncertainty accepted proof: " + defect + ": " + text)
            if defect == "final_Git_alarm" and not alarm_sent:
                raise AssertionError("final cleanup classification boundary not exercised")
            if defect in ("checker", "Git") and (later_calls or scratch_calls):
                raise AssertionError("unclosed lifecycle permitted later checker or scratch deletion")
            if before != module.canonical_fingerprint(root):
                raise AssertionError("cleanup uncertainty control changed caller")
        token = module._CLEANUP_UNPROVEN.set(True)
        try:
            with mock.patch.object(module.os, "fork", side_effect=AssertionError("unclosed dispatch")):
                result = module.run_checker([sys.executable, "-c", "pass"], root, module.base_environment(), 10.)
                if result[3] != "PROCESS_CLEANUP_FAILURE":
                    raise AssertionError("lower process layer accepted unclosed scope")
                try:
                    module.canonical_fingerprint(root)
                except ValueError as exc:
                    if "PROCESS_CLEANUP_FAILURE" not in str(exc): raise
                else:
                    raise AssertionError("unclosed scope permitted repository proof")
        finally:
            module._CLEANUP_UNPROVEN.reset(token)
    return ["PROC-11-checker-Git-and-scratch-cleanup-uncertainty-never-MATCH",
            "PROC-12-unclosed-lifecycle-suppresses-proof-dispatch-and-deletion"]


def selftest_budget_contract_cases(module: Any) -> list[str]:
    # The expanded suite gets margin, never a larger budget for other commands.
    selected = entry("validation_aggregate_adversarial")
    selected["path"] = "tools/check_glyph_runtime_config_validation_aggregate.py"
    selected["command"] = ["python3", selected["path"]]
    if module.checker_time_budget(selected) != 210. or module.CHECKER_TIMEOUT_SECONDS != 140.:
        raise AssertionError("self-test allowance or ordinary default drifted")
    for key, value in (("id", "other_checker"), ("path", "tools/other.py"),
                       ("command", ["python3", selected["path"], "--other"])):
        near_miss = dict(selected)
        near_miss[key] = value
        if module.checker_time_budget(near_miss) != 140.:
            raise AssertionError("self-test allowance broadened: " + key)
    # Aggregate remaining time always dominates the suite allowance. Exercise
    # actual main dispatch below a mocked remaining budget without wall races.
    with tempfile.TemporaryDirectory(prefix="glyph-selftest-budget-control-") as directory:
        root = fresh_root(Path(directory))
        write_checker(root, selected, 0)
        manifest = write_manifest(root, [selected], ["baseline"])
        original_run, original_budget = module.run_checker, module.require_budget
        observed = []
        def remaining(label):
            return 3. if label == "checker:" + selected["id"] else original_budget(label)
        def dispatch(command, cwd, env, timeout, **kwargs):
            if len(command) > 1 and command[1] == selected["path"]:
                observed.append(timeout)
                return None, "", "injected remaining-budget exhaustion", "CHECKER_TIMEOUT", 0.
            return original_run(command, cwd, env, timeout, **kwargs)
        with mock.patch.object(module, "require_budget", remaining), mock.patch.object(module, "run_checker", dispatch):
            code, text = invoke(module, root, manifest, "--json")
        report = payload(text)
        if (code != 1 or observed != [3.] or report["status"] != "FAIL"
                or report["failure_kind"] != "AGGREGATE_TIMEOUT" or len(report["results"]) != 1):
            raise AssertionError("self-test allowance escaped aggregate remaining budget: " + text)
    return ["AGG-26-exact-selftest-allowance-and-aggregate-budget-clipping"]


def main() -> int:
    module = load_runner()
    passed: list[str] = deadline_control_cases(module) + cleanup_proof_control_cases(module) + selftest_budget_contract_cases(module)
    actual_root = RUNNER_PATH.parents[1]
    module.ROOT = actual_root
    probe = entry("probe")
    probe["path"] = "tools/check_glyph_runtime_config_validation_aggregate.py"
    probe["command"][1] = probe["path"]
    for bad in ("/absolute", "", ".", "../escape", "tools\\bad.py", "tools/check_glyph_runtime_config_validation_aggregate.py"):
        probe["source_dependencies"] = [bad]
        try:
            module.validate_dependencies(probe)
        except ValueError:
            continue
        raise AssertionError(f"malformed dependency path was accepted: {bad!r}")
    policy_probe = entry("policy_probe")
    policy_probe["applicability"] = "historical_only"
    policy_probe["branch_policy"] = "content_only"
    try:
        module.validate_branch_policy(policy_probe)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid applicability/policy pair was accepted")
    passed.append("AGG-13-dependency-path-and-policy-boundaries")
    with tempfile.TemporaryDirectory(prefix="glyph-aggregate-adversarial-") as directory:
        root = fresh_root(Path(directory))
        module.ROOT = root

        (root / "tools/helper.py").write_text("VALUE = 1\n", encoding="utf-8")
        import_probe = entry("import_probe")
        write_checker(root, import_probe, 0)
        (root / import_probe["path"]).write_text("from helper import VALUE\nraise SystemExit(0)\n", encoding="utf-8")
        run_git(root, "add", "tools/helper.py", import_probe["path"])
        run_git(root, "commit", "-m", "add import probe")
        manifest = write_manifest(root, [import_probe], ["baseline"])
        result, text = invoke(module, root, manifest, "--check-manifest")
        if result != 1 or "missing direct helper dependencies" not in text:
            raise AssertionError("missing direct helper import was accepted")
        passed.append("AGG-14-direct-helper-import-required")
        (root / "tools/link.py").symlink_to("helper.py")
        run_git(root, "add", "tools/link.py")
        run_git(root, "commit", "-m", "add symlink probe")
        for bad in ("tools/untracked.py", "tools", "tools/link.py"):
            import_probe["source_dependencies"] = [bad]
            manifest = write_manifest(root, [import_probe], ["baseline"])
            result, text = invoke(module, root, manifest, "--check-manifest")
            if result != 1 or "invalid source dependency path" not in text:
                raise AssertionError(f"invalid dependency target was accepted: {bad}")
        import_probe["source_dependencies"] = ["README.md", "README.md"]
        manifest = write_manifest(root, [import_probe], ["baseline"])
        result, text = invoke(module, root, manifest, "--check-manifest")
        if result != 1 or "duplicate source dependency" not in text:
            raise AssertionError("duplicate dependency was accepted")
        passed.append("AGG-15-untracked-directory-symlink-duplicate-rejected")

        entries = [entry("pass_one"), entry("fail_two"), entry("pass_three")]
        for checker, code in zip(entries, (0, 7, 0), strict=True):
            write_checker(root, checker, code)
        manifest = write_manifest(root, entries, ["baseline"])
        result, text = invoke(module, root, manifest, "--json")
        report = payload(text)
        if result != 1 or report["census_freshness"]["status"] != "PASS" or [item["id"] for item in report["results"]] != ["pass_one", "fail_two", "pass_three"]:
            raise AssertionError("full aggregate did not record all load-bearing checks")
        passed.extend(["AGG-01-failing-load-bearing-fails", "AGG-02-full-records-all"])

        result, text = invoke(module, root, manifest, "--json", "--fail-fast")
        report = payload(text)
        if result != 1 or [item["id"] for item in report["results"]] != ["pass_one", "fail_two"]:
            raise AssertionError("fail-fast did not stop at first failure")
        passed.append("AGG-03-fail-fast-first-failure")

        mutation = entry("mutation_probe")
        write_checker(root, mutation, 0)
        (root / mutation["path"]).write_text(
            "from pathlib import Path\nPath('README.md').write_text('mutated\\n')\n",
            encoding="utf-8",
        )
        run_git(root, "add", mutation["path"])
        manifest = write_manifest(root, [mutation], ["baseline"])
        result, text = invoke(module, root, manifest, "--json")
        report = payload(text)
        if result != 1 or report["results"][0]["failure_kind"] != "ISOLATED_REPOSITORY_MUTATION":
            raise AssertionError("isolated repository mutation was accepted")
        passed.append("AGG-18-isolated-mutation-rejected")

        timeout_probe = entry("timeout_probe")
        write_checker(root, timeout_probe, 0)
        (root / timeout_probe["path"]).write_text("import time\ntime.sleep(10)\n", encoding="utf-8")
        run_git(root, "add", timeout_probe["path"])
        manifest = write_manifest(root, [timeout_probe], ["baseline"])
        original_budgets = (module.CHECKER_TIMEOUT_SECONDS, module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS)
        module.CHECKER_TIMEOUT_SECONDS = 0.05
        module.AGGREGATE_TIMEOUT_SECONDS = 10.0
        module.TERM_GRACE_SECONDS = 0.05
        try:
            result, text = invoke(module, root, manifest, "--json")
        finally:
            module.CHECKER_TIMEOUT_SECONDS, module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS = original_budgets
        report = payload(text)
        if result != 1 or report["results"][0]["failure_kind"] != "CHECKER_TIMEOUT":
            raise AssertionError("checker timeout was not fail-closed")
        passed.append("AGG-19-process-timeout-fails-closed")

        environment_probe = entry("environment_probe")
        write_checker(root, environment_probe, 0)
        (root / environment_probe["path"]).write_text(
            "import os\nfrom pathlib import Path\nassert Path.cwd() != Path(os.environ.get('GLYPH_CANONICAL_ROOT', ''))\nassert (Path.cwd() / '.git').exists()\nassert os.environ['GIT_CONFIG_GLOBAL'] == os.devnull\nassert os.environ['LC_ALL'] == 'C'\n",
            encoding="utf-8",
        )
        run_git(root, "add", environment_probe["path"])
        manifest = write_manifest(root, [environment_probe], ["baseline"])
        original_env = os.environ.pop("GLYPH_CHECKER_BASE", None)
        try:
            result, text = invoke(module, root, manifest, "--json")
        finally:
            if original_env is not None:
                os.environ["GLYPH_CHECKER_BASE"] = original_env
        report = payload(text)
        if result != 0 or report["context"]["branch"] != "configurator":
            raise AssertionError("constructed environment or branch context was not preserved")
        passed.append("AGG-20-environment-and-branch-isolation")

        run_git(root, "update-ref", "-d", "refs/remotes/origin/configurator")
        os.environ["GLYPH_CHECKER_BASE"] = "HEAD"
        try:
            result, text = invoke(module, root, manifest, "--json")
        finally:
            os.environ.pop("GLYPH_CHECKER_BASE", None)
        if result != 0:
            raise AssertionError("explicit base override did not work without origin/configurator")
        run_git(root, "update-ref", "refs/remotes/origin/configurator", "HEAD")
        passed.append("AGG-21-explicit-base-override")

        category_entries = [entry("baseline_pass"), entry("docs_pass", category="docs")]
        for checker in category_entries:
            write_checker(root, checker, 0)
        historical_category_entry = entry(
            "historical_evidence_probe",
            category="historical_evidence",
            applicability="historical_only",
            historical=True,
            load_bearing=False,
        )
        historical_category_entry["branch_policy"] = "named_evidence_branch"
        write_checker(root, historical_category_entry, 0)
        category_entries.append(historical_category_entry)
        manifest = write_manifest(root, category_entries, ["baseline", "docs", "historical_evidence"])
        result, text = invoke(module, root, manifest, "--json", "--category", "docs")
        report = payload(text)
        if result != 0 or [item["id"] for item in report["results"]] != ["docs_pass"]:
            raise AssertionError("category filter did not select exactly one category")
        passed.append("AGG-04-category-filter-exact")

        result, text = invoke(module, root, manifest, "--category", "unknown")
        if result != 1 or "unknown category" not in text:
            raise AssertionError("unknown category was accepted")
        passed.append("AGG-05-unknown-category-rejected")

        for arguments, label in (
            (("historical_evidence",), "historical-only"),
            (("docs", "historical_evidence"), "mixed"),
            (("historical_evidence", "historical_evidence"), "duplicate"),
        ):
            result, text = invoke(module, root, manifest, "--category", arguments[0], *sum((["--category", category] for category in arguments[1:]), []))
            if result != 1 or "requested category selects zero current checks: historical_evidence" not in text:
                raise AssertionError(f"{label} zero-result category was accepted")
        passed.append("AGG-17-zero-result-category-rejected")

        command_probe = entry("command_probe")
        write_checker(root, command_probe, 0)
        run_git(root, "commit", "-m", "add command probe")
        command_cases = [
            (["python", command_probe["path"]], [], "command does not match"),
            (["python3", command_probe["path"], "--extra"], [], "command does not match"),
            (["python3", command_probe["path"]], ["--required"], "command does not match"),
            (["python3"], [], "command does not match"),
            (["python3", "tools/other.py"], [], "command does not match"),
        ]
        for command, required_arguments, needle in command_cases:
            command_probe["command"] = command
            command_probe["required_arguments"] = required_arguments
            manifest = write_manifest(root, [command_probe], ["baseline"])
            assert_manifest_failure(module, root, manifest, needle)
        command_probe["command"] = ["python3", command_probe["path"], "--required"]
        command_probe["required_arguments"] = [1]
        manifest = write_manifest(root, [command_probe], ["baseline"])
        assert_manifest_failure(module, root, manifest, "invalid required_arguments")
        command_probe["required_arguments"] = []
        command_probe["command"] = ["python3", command_probe["path"]]
        manifest = write_manifest(root, [command_probe], ["baseline"])
        result, text = invoke(module, root, manifest, "--check-manifest")
        if result != 0 or "entries=1" not in text:
            raise AssertionError(f"valid command contract was rejected: {text}")
        executable_probe = entry("executable_probe")
        write_checker(root, executable_probe, 0)
        os.chmod(root / executable_probe["path"], 0o755)
        run_git(root, "add", executable_probe["path"])
        manifest = write_manifest(root, [executable_probe], ["baseline"])
        result, text = invoke(module, root, manifest, "--check-manifest")
        if result != 0 or "entries=1" not in text:
            raise AssertionError("tracked executable-mode Python checker was rejected")
        for bad_path in ("tools", "tools/link.py", "/absolute.py", "../escape.py", "tools/./bad.py", "tools\\bad.py"):
            command_probe["path"] = bad_path
            command_probe["command"] = ["python3", bad_path]
            command_probe["required_arguments"] = []
            manifest = write_manifest(root, [command_probe], ["baseline"])
            assert_manifest_failure(module, root, manifest, "invalid checker path")
        command_probe["path"] = "tools/untracked.py"
        command_probe["command"] = ["python3", command_probe["path"]]
        command_probe["required_arguments"] = []
        manifest = write_manifest(root, [command_probe], ["baseline"])
        assert_manifest_failure(module, root, manifest, "invalid checker path")
        passed.append("AGG-16-command-interpreter-path-arguments-and-target-contract")

        mismatch = [entry("unexpected_exit")]
        write_checker(root, mismatch[0], 9)
        manifest = write_manifest(root, mismatch, ["baseline"])
        result, text = invoke(module, root, manifest, "--json")
        if result != 1 or payload(text)["results"][0]["status"] != "FAIL":
            raise AssertionError("unexpected nonzero checker exit was accepted")
        passed.append("AGG-06-unexpected-success-exit-mismatch-fails")

        unsafe = [entry("unsafe_never_run", applicability="unsafe_or_mutating", load_bearing=False, mutation_risk="candidate_preparation")]
        unsafe[0]["branch_policy"] = "not_run"
        write_checker(root, unsafe[0], 9)
        manifest = write_manifest(root, unsafe, ["baseline"])
        result, text = invoke(module, root, manifest, "--json")
        if result != 0 or payload(text)["results"]:
            raise AssertionError("unsafe checker was selected for execution")
        passed.append("AGG-07-unsafe-not-executed")

        missing = [entry("missing_checker")]
        manifest = write_manifest(root, missing, ["baseline"])
        result, text = invoke(module, root, manifest)
        if result != 1 or "invalid checker path" not in text:
            raise AssertionError("missing checker was not rejected before execution")
        passed.append("AGG-08-missing-checker-rejected")

        duplicate = [entry("duplicate"), entry("duplicate")]
        for checker in duplicate:
            write_checker(root, checker, 0)
        manifest = write_manifest(root, duplicate, ["baseline"])
        result, text = invoke(module, root, manifest)
        if result != 1 or "duplicate checker ID" not in text:
            raise AssertionError("duplicate manifest ID was accepted")
        passed.append("AGG-09-duplicate-id-rejected")

        historical = [entry("historical_marked_current", historical=True)]
        write_checker(root, historical[0], 0)
        manifest = write_manifest(root, historical, ["baseline"])
        result, text = invoke(module, root, manifest)
        if result != 1 or "unsafe current aggregate entry" not in text:
            raise AssertionError("historical checker marked current was accepted")
        passed.append("AGG-10-historical-current-rejected")

        actual_manifest = json.loads(
            (actual_root / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        exclusions = actual_manifest.get("strong_signal_exclusions")
        if not isinstance(exclusions, list) or not exclusions:
            raise AssertionError("committed manifest has no strong-signal exclusion to probe")
        census_value = json.loads(
            (actual_root / "docs/runtime_config/fixtures/glyph_checker_census.json").read_text(encoding="utf-8")
        )
        strong_paths = {
            item["path"] for item in census_value["entries"] if item["runtime_config_relevance_signals"]
        }
        omitted = next((item for item in exclusions if item["path"] in strong_paths), None)
        if omitted is None:
            raise AssertionError("committed manifest has no exclusion with a census signal to probe")
        exclusions.remove(omitted)
        probe = root / "omitted-strong-signal-exclusion.json"
        probe.write_text(json.dumps(actual_manifest), encoding="utf-8")
        # The canonical checkout carries the documented pre-existing ignored
        # .pio/libdeps setup entry that blocks aggregate preflight.  This
        # probe targets manifest classification only, so bypass that unrelated
        # preflight gate while retaining the runner's actual load() checks.
        original_reject_partial_repository = module.reject_partial_repository
        original_canonical_fingerprint = module.canonical_fingerprint
        original_census_freshness = module.census_freshness
        module.reject_partial_repository = lambda: None
        module.canonical_fingerprint = lambda *args, **kwargs: "classification-probe"
        module.census_freshness = lambda: {"status": "PASS"}
        try:
            result, text = invoke(
                module,
                actual_root,
                probe,
                "--check-manifest",
                census_path=actual_root / "docs/runtime_config/fixtures/glyph_checker_census.json",
            )
        finally:
            module.reject_partial_repository = original_reject_partial_repository
            module.canonical_fingerprint = original_canonical_fingerprint
            module.census_freshness = original_census_freshness
        needle = f"unclassified strong-signal checker: {omitted['path']}"
        if result != 1 or needle not in text:
            raise AssertionError("strong-signal omission probe did not reach expected rejection: " + text)
        exclusions.append(omitted)
        probe.write_text(json.dumps(actual_manifest), encoding="utf-8")
        # Use a disposable minimal manifest for the synthetic probes; the
        # canonical manifest names repository files that are intentionally not
        # present in this tiny adversarial repository.
        manifest = write_manifest(root, [], ["baseline"])
        passed.append("AGG-11-unclassified-strong-signal-rejected")

        # Each safety-control signal class must participate in the same
        # manifest-or-exclusion classification boundary as runtime-config
        # signals.  The probes are synthetic and are never executed.
        safety_signal_cases = {
            "ci-workflow": ".github/workflows/build.yml",
            "build-hook": "builder_scripts/arduino_pico.py",
            "artifact-custody": "tools/glyph_hardware_artifact_custody.py",
            "hardware-evidence": "HARDWARE_EVIDENCE",
        }
        for label, signal in safety_signal_cases.items():
            synthetic = root / f"tools/check_glyph_synthetic_{label}.py"
            synthetic.write_text(f"# static reference: {signal}\nraise SystemExit(0)\n", encoding="utf-8")
            refresh_census(root)
            result, text = invoke(module, root, manifest, "--check-manifest")
            expected = f"unclassified strong-signal checker: tools/check_glyph_synthetic_{label}.py"
            if result != 1 or expected not in text:
                raise AssertionError(f"{label} safety signal escaped classification")
            synthetic.unlink()
            refresh_census(root)
            near_misses = [f"x{signal}"]
            if label == "ci-workflow":
                near_misses.append("xconfig/glyph/.github/workflows/build.yml")
            if label == "hardware-evidence":
                near_misses.append("xdocs/agent_framework/xHARDWARE_EVIDENCE.md")
            for index, near_signal in enumerate(near_misses):
                near_miss = root / f"tools/check_glyph_synthetic_near_{label}_{index}.py"
                near_miss.write_text(f"# static near miss: {near_signal}\nraise SystemExit(0)\n", encoding="utf-8")
                refresh_census(root)
                original_require_clean_source = module.require_clean_source
                module.require_clean_source = lambda: None
                try:
                    result, text = invoke(module, root, manifest, "--check-manifest")
                finally:
                    module.require_clean_source = original_require_clean_source
                if result != 0 or "glyph_runtime_config_validation_manifest: PASS" not in text:
                    raise AssertionError(f"{label} near-miss prefix became a safety signal")
                near_miss.unlink()
                refresh_census(root)
        passed.append("AGG-22-safety-signal-classes-require-classification")
        probe.unlink()

        drift = [entry("stable")]
        write_checker(root, drift[0], 0)
        manifest = write_manifest(root, drift, ["baseline"])
        result, text = invoke(module, root, manifest, "--json")
        if result != 0 or payload(text)["census_freshness"]["status"] != "PASS":
            raise AssertionError("fresh census was not accepted")
        drift_path = root / drift[0]["path"]
        drift_path.write_text(drift_path.read_text(encoding="utf-8") + "# byte drift\n", encoding="utf-8")
        result, text = invoke(module, root, manifest, "--json")
        if result != 1 or "checker census is stale" not in text:
            raise AssertionError("byte-changed checker was accepted without census regeneration")
        refresh_census(root)
        (root / "tools/check_glyph_extra.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
        refresh_census(root)
        (root / "tools/check_glyph_extra.py").rename(root / "tools/check_glyph_renamed.py")
        result, text = invoke(module, root, manifest, "--json")
        if result != 1 or "checker census is stale" not in text:
            raise AssertionError("renamed checker was accepted without census regeneration")
        refresh_census(root)
        (root / "tools/check_glyph_added.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
        result, text = invoke(module, root, manifest, "--json")
        if result != 1 or "checker census is stale" not in text:
            raise AssertionError("added checker was accepted without census regeneration")
        refresh_census(root)
        (root / "tools/check_glyph_added.py").unlink()
        result, text = invoke(module, root, manifest, "--json")
        if result != 1 or "checker census is stale" not in text:
            raise AssertionError("removed checker was accepted without census regeneration")
        refresh_census(root)
        run_git(root, "add", "-A")
        run_git(root, "commit", "-m", "commit census drift repair")
        result, text = invoke(module, root, manifest, "--json")
        if result != 0 or payload(text)["census_freshness"]["status"] != "PASS":
            raise AssertionError("regenerated census was not accepted after drift repair")
        passed.append("AGG-12-census-freshness-added-removed-renamed-byte-drift")

    passed.extend(current_policy_dependency_cases(module))
    passed.extend(orchestration_retirement_cases(module))
    passed.extend(gp_val037_current_argument_cases(module))
    passed.extend(gp_val043_runner_proof_cases(module))
    passed.extend(gp_val034_catalog_cases(module))
    passed.extend(gp_val039_runner_cases(module))
    passed.extend(isolation_contract_cases(module))
    passed.extend(process_control_cases(module))
    passed.extend(byte_integrity_cases(module))
    passed.extend(metadata_object_cases(module))
    passed.extend(pre_git_metadata_cases(module))
    passed.extend(locator_traversal_cases(module))
    # The old synthetic repositories exercise only the pre-campaign catalog.
    # They contain no adopted campaign authority and must not impersonate it.
    import glyph_campaign_transition as campaign
    with mock.patch.object(campaign, "ROOTS", frozenset()), mock.patch.object(
            campaign, "authenticate", side_effect=lambda root: {"test_only_legacy_catalog": str(root)}):
        passed.extend(topology_catalog_cases(module))
        passed.extend(gp_config_010_historical_object_cases(module))
    actual_root = RUNNER_PATH.resolve().parents[1]
    if module.package_scope.package_lineage(actual_root):
        import copy
        scope = module.package_scope
        entries = json.loads((actual_root / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json").read_text())["entries"]
        scope.verify_manifest_coverage(actual_root, entries)
        # The positively authenticated receipt closes the exact manifest.
        # Git history is provenance, not an input to current coverage tests.
        scope.public_contract(actual_root)
        required_ids = {row["id"] for row in entries}
        controls = [("retire", row["id"]) for row in entries
                    if row["id"] in required_ids and row["applicability"] == "current"]
        controls += [("remove", "validation_publication_workflow"),
                     ("substitute", "gp_config022_rgb_target_validation")]
        for identity in ("agent_framework", "agentic_sequence"):
            controls.extend((change, identity) for change in (
                "substitute", "restore-current", "restore-current-substitute"))
        for change, name in controls:
            alternate = copy.deepcopy(entries)
            row = next(r for r in alternate if r["id"] == name)
            if change == "remove":
                alternate.remove(row)
            elif change.startswith("restore-current"):
                row.update(applicability="current", branch_policy="content_only", load_bearing=True, historical=False)
                if change == "restore-current-substitute":
                    row["command"] = ["python3", "tools/unknown.py"]
            elif change == "substitute":
                row["command"] = ["python3", "tools/unknown.py"]
            else:
                row.update(applicability="historical_only", branch_policy="named_evidence_branch", load_bearing=False, historical=True)
            try:
                scope.verify_manifest_coverage(actual_root, alternate)
            except ValueError:
                pass
            else:
                raise AssertionError("current package manifest accepted " + change + " for " + name)
        passed.extend(["current-package-required-command-and-classification-negatives",
                       "F2-package-all-still-current-required-commands-reject-retirement",
                       "F2-package-retired-command-substitution-and-reactivation-rejected"])
    else:
        raise AssertionError("current aggregate requires positive package contract; historical campaign suite is --historical-maintenance")

    if set(REQUIRED) != set(entry("schema_probe")):
        raise AssertionError("adversarial manifest entry no longer matches the runner schema")
    print("glyph_runtime_config_validation_aggregate: PASS; cases=" + ",".join(passed))
    return 0


def historical_maintenance() -> int:
    """Execute the unchanged pre-G2B migration suite at its exact snapshot.

    This opt-in requires development Git objects. Object absence fails, and
    never authorizes the current validation path or substitutes a PASS.
    """
    from glyph_ci_package_scope import materialize
    snapshot = "6714aca212ba8dd5bb1c655b344c80f35a582630"
    with tempfile.TemporaryDirectory(prefix="glyph-historical-maintenance-") as directory:
        root = materialize(RUNNER_PATH.resolve().parents[1], snapshot, Path(directory))
        return subprocess.run([sys.executable, "-I", "-B", str(root / "tools/check_glyph_runtime_config_validation_aggregate.py")], cwd=root).returncode


if __name__ == "__main__":
    if sys.argv[1:] == ["--historical-maintenance"]:
        raise SystemExit(historical_maintenance())
    if sys.argv[1:]:
        raise SystemExit("expected no arguments or --historical-maintenance")
    raise SystemExit(main())
