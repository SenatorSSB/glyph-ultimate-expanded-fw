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
import subprocess
import sys
import tempfile
import time
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
    root = parent / "repo"
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
        passed.append("ISO-03-all-isolated-mutation-dimensions-stop")

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
                report = execute(test_manifest)
                if report["status"] != "PASS": raise AssertionError("self-test environment exception is not exact")
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

        sentinel = parent / "late-sentinel"
        child = "import signal,time; from pathlib import Path; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(0.5); Path(" + repr(str(sentinel)) + ").write_text('escaped')"
        source = "import subprocess,sys,time,signal\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\nsubprocess.Popen([sys.executable,'-c'," + repr(child) + "])\ntime.sleep(5)\n"
        manifest = install(source, [probe, next_checker])
        old_budgets = module.CHECKER_TIMEOUT_SECONDS, module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS
        module.CHECKER_TIMEOUT_SECONDS, module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS = .1, 10., .05
        try:
            report = execute(manifest)
            if report["failure_kind"] != "CHECKER_TIMEOUT" or len(report["results"]) != 1:
                raise AssertionError("process-tree timeout did not stop later checkers")
            time.sleep(.55)
            if sentinel.exists(): raise AssertionError("TERM-resistant child survived timeout KILL")
            module.CHECKER_TIMEOUT_SECONDS = 10.
            module.AGGREGATE_TIMEOUT_SECONDS = .7
            report = execute(manifest)
            if report["failure_kind"] != "AGGREGATE_TIMEOUT" or report["canonical_proof"] != "UNAVAILABLE":
                raise AssertionError(f"whole deadline claimed complete proof: {report}")
            time.sleep(.55)
            if sentinel.exists(): raise AssertionError("whole deadline left a child alive")
            module.AGGREGATE_TIMEOUT_SECONDS = .001
            report = execute(manifest)
            if report["failure_kind"] != "AGGREGATE_TIMEOUT" or report["status"] != "FAIL":
                raise AssertionError("preflight deadline accepted")
        finally:
            module.CHECKER_TIMEOUT_SECONDS, module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS = old_budgets
        # A real child delayed before exec is already owned and remains killable.
        original_exec = module.child_exec
        def delayed_exec(command, cwd, env):
            time.sleep(2)
            sentinel.write_text("unowned launch child survived", encoding="utf-8")
            original_exec(command, cwd, env)
        module.child_exec = delayed_exec
        try:
            code, _, _, failure, elapsed = module.run_checker(["python3", "-c", "print(0)"], root, module.base_environment(), .05)
            if failure != "CHECKER_TIMEOUT" or elapsed > 1.0:
                raise AssertionError("delayed child setup escaped acquisition timeout")
        finally:
            module.child_exec = original_exec
        time.sleep(.05)
        if sentinel.exists(): raise AssertionError("delayed child setup survived termination")
        passed.append("ISO-08-child-kill-whole-preflight-deadline-and-owned-acquisition")

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
            module.AGGREGATE_TIMEOUT_SECONDS, module.TERM_GRACE_SECONDS = .5, .03
            for stalled_phase in ("census", "setup", "final_proof"):
                calls = [0]
                def stalled_census():
                    time.sleep(2)
                    return old_census()
                def stalled_fingerprint(*args):
                    calls[0] += 1
                    if calls[0] == 2: time.sleep(2)
                    return old_fingerprint(*args)
                def stalled_setup(*args):
                    result = module.run_checker([sys.executable, "-c", "import time; time.sleep(2)"], root,
                        module.EXECUTION_ENV, module.require_budget("injected setup"))
                    if result[3]: raise module.AggregateTimeout("injected setup command timeout")
                    raise AssertionError("stalled setup did not time out")
                module.census_freshness = stalled_census if stalled_phase == "census" else old_census
                module.canonical_fingerprint = stalled_fingerprint if stalled_phase == "final_proof" else old_fingerprint
                module.clone_snapshot = stalled_setup if stalled_phase == "setup" else old_clone
                started = time.monotonic()
                code, text = invoke(module, root, manifest, "--json", *( ["--check-manifest"] if stalled_phase == "final_proof" else []))
                report = payload(text)
                if code != 1 or report["failure_kind"] != "AGGREGATE_TIMEOUT" or time.monotonic() - started > 1.2:
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
        framework = entry("agent_framework")
        framework["path"] = "tools/check_glyph_agent_framework_docs.py"
        framework["command"] = ["python3", framework["path"]]
        # An off-head object is carried only by a caller remote-tracking ref.
        run_git(root, "switch", "-c", "unadvertised-provenance")
        (root / "provenance.md").write_text("provenance", encoding="utf-8")
        run_git(root, "add", "provenance.md"); run_git(root, "commit", "-m", "provenance")
        off_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        run_git(root, "switch", "catalog-feature")
        run_git(root, "update-ref", "refs/remotes/provenance/packet", off_head)
        run_git(root, "update-ref", "-d", "refs/heads/unadvertised-provenance")
        queue = {
            "planner_packet": {"state": "FRESH", "base_configurator_sha": initial, "planning_commit": off_head, "curation_commit": feature},
            "completion_correspondence": {"migration_base_configurator_sha": initial, "legacy_done_ids": ["LEGACY"]},
            "items": [
                {"id": "DIRECT", "status": "DONE", "done_evidence": {"implementation_base_sha": initial, "reviewed_implementation_sha": off_head, "prior_canonical_integration_sha": feature}},
                {"id": "EXACT_PATH", "status": "DONE", "done_evidence": {"implementation_base_sha": initial, "reviewed_implementation_sha": off_head, "prior_canonical_integration_sha": feature}},
                {"id": "LEGACY", "status": "DONE", "done_evidence": "legacy free text " + "e" * 40},
                {"id": "HW", "status": "HARDWARE_VALIDATED", "hardware_result": "PASS", "hardware_evidence_record": "git-json:" + off_head + ":docs/evidence.json"},
                {"id": "HW_PENDING", "status": "LOCAL_ACCEPTANCE_PENDING", "hardware_result": None, "hardware_evidence_record": "git-json:" + "d" * 40 + ":docs/evidence.json"},
            ],
            "unrelated_prose": "a" * 40, "foreign_upstream": "b" * 40, "firmware_artifact_sha256": "c" * 64,
        }
        path = root / "docs/project/ACTIVE_AGENT_QUEUE.md"
        path.parent.mkdir(parents=True)
        def publish(value):
            text = value if isinstance(value, str) else json.dumps(value)
            path.write_text("<!-- queue-state:start -->\n```json\n" + text + "\n```\n<!-- queue-state:end -->\n", encoding="utf-8")
            run_git(root, "add", "docs/project/ACTIVE_AGENT_QUEUE.md")
            run_git(root, "commit", "-m", "queue fixture")
        publish(queue)
        refs, roots = module.required_catalog([framework])
        if refs or roots != {initial, feature, off_head}:
            raise AssertionError("framework object root catalog scanned unrelated fields or missed consumed identities")
        context = module.immutable_source_context([framework])
        with tempfile.TemporaryDirectory(prefix="glyph-catalog-clone-") as clone_directory:
            original_env = module.EXECUTION_ENV
            module.EXECUTION_ENV = module.isolated_environment(Path(clone_directory))
            try:
                clone = module.clone_snapshot(context, Path(clone_directory))
                if module.git_value("cat-file", "-t", off_head, cwd=clone) != "commit":
                    raise AssertionError("off-head provenance object was not locally transferred")
                clone_refs = module.git_value("for-each-ref", "--format=%(refname)", cwd=clone).splitlines()
                if clone_refs != ["refs/heads/catalog-feature", "refs/remotes/origin/configurator"]:
                    raise AssertionError("framework provenance imported an unrelated ref")
            finally: module.EXECUTION_ENV = original_env
        malformed = json.loads(json.dumps(queue)); malformed["planner_packet"]["planning_commit"] = "HEAD"; publish(malformed)
        try: module.required_catalog([framework])
        except ValueError: pass
        else: raise AssertionError("nonimmutable queue field accepted")
        malformed["planner_packet"]["planning_commit"] = "f" * 40; publish(malformed)
        try: module.immutable_source_context([framework])
        except ValueError: pass
        else: raise AssertionError("missing queue object accepted")
        publish(json.dumps(queue).replace('"state": "FRESH"', '"state": "FRESH", "state": "FRESH"'))
        try: module.required_catalog([framework])
        except ValueError: pass
        else: raise AssertionError("duplicate queue keys accepted")
        observations = entry("build_input_resolution_observations")
        observations["path"] = "tools/check_glyph_build_input_resolution_observations.py"
        observations["command"] = ["python3", observations["path"]]
        nuker = entry("nuker_source_lineage")
        nuker["path"] = "tools/check_glyph_nuker_source_lineage.py"; nuker["command"] = ["python3", nuker["path"]]
        refs, roots = module.required_catalog([observations, nuker])
        if refs or roots != {"8c04262c66613d46b933b1b739c01c575cb0c580", "ffc007552abc848051841362b0b0ac4c1a7d087b", "a747dd54b02b207483142331d8b5be1113fc951e", "d5050847d3f850951b3f47865dc8a91aedea0834"}:
            raise AssertionError("fixed current-source roots differ")
    return ["ISO-12-exact-local-configurator-ref", "ISO-13-source-enumerated-queue-roots-and-off-head-transfer", "ISO-14-catalog-schema-identity-and-local-object-failures"]

def main() -> int:
    module = load_runner()
    passed: list[str] = []
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
        module.AGGREGATE_TIMEOUT_SECONDS = 1.0
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
        result, text = invoke(
            module,
            actual_root,
            probe,
            "--check-manifest",
            census_path=actual_root / "docs/runtime_config/fixtures/glyph_checker_census.json",
        )
        needle = f"unclassified strong-signal checker: {omitted['path']}"
        if result != 1 or needle not in text:
            raise AssertionError("strong-signal checker absent from manifest/exclusions was accepted")
        probe.unlink()
        passed.append("AGG-11-unclassified-strong-signal-rejected")

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

    passed.extend(isolation_contract_cases(module))
    passed.extend(topology_catalog_cases(module))

    if set(REQUIRED) != set(entry("schema_probe")):
        raise AssertionError("adversarial manifest entry no longer matches the runner schema")
    print("glyph_runtime_config_validation_aggregate: PASS; cases=" + ",".join(passed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
