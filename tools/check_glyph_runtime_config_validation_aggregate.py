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
import subprocess
import sys
import tempfile
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


def write_checker(root: Path, checker: dict[str, Any], exit_code: int) -> None:
    path = root / checker["path"]
    path.write_text(f"raise SystemExit({exit_code})\n", encoding="utf-8")


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

        category_entries = [entry("baseline_pass"), entry("docs_pass", category="docs")]
        for checker in category_entries:
            write_checker(root, checker, 0)
        manifest = write_manifest(root, category_entries, ["baseline", "docs"])
        result, text = invoke(module, root, manifest, "--json", "--category", "docs")
        report = payload(text)
        if result != 0 or [item["id"] for item in report["results"]] != ["docs_pass"]:
            raise AssertionError("category filter did not select exactly one category")
        passed.append("AGG-04-category-filter-exact")

        result, text = invoke(module, root, manifest, "--category", "unknown")
        if result != 1 or "unknown category" not in text:
            raise AssertionError("unknown category was accepted")
        passed.append("AGG-05-unknown-category-rejected")

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
        if result != 1 or "missing checker file" not in text:
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
        result, text = invoke(module, root, manifest, "--json")
        if result != 0 or payload(text)["census_freshness"]["status"] != "PASS":
            raise AssertionError("regenerated census was not accepted after drift repair")
        passed.append("AGG-12-census-freshness-added-removed-renamed-byte-drift")

    if set(REQUIRED) != set(entry("schema_probe")):
        raise AssertionError("adversarial manifest entry no longer matches the runner schema")
    print("glyph_runtime_config_validation_aggregate: PASS; cases=" + ",".join(passed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
