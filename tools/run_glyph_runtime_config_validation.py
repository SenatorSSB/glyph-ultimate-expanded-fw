#!/usr/bin/env python3
"""Read-only deterministic aggregate runner for current runtime-config checks."""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from pathlib import PurePosixPath
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from generate_glyph_checker_census import generate as generate_census, rendered as render_census  # noqa: E402

MANIFEST = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
CENSUS = ROOT / "docs/runtime_config/fixtures/glyph_checker_census.json"
REQUIRED = {"id", "path", "command", "category", "applicability", "branch_policy", "required_arguments", "mutation_risk", "source_dependencies", "load_bearing", "historical", "reason"}
BRANCH_POLICIES = {"content_only", "content_and_scope", "named_evidence_branch", "not_run"}
APPLICABILITIES = {"current", "historical_only", "unsafe_or_mutating"}
EXCLUSION_REQUIRED = {"id", "path", "reason", "detail"}
EXCLUSION_REASONS = {"HISTORICAL_BRANCH_EVIDENCE", "HARDWARE_RESULT_EVIDENCE", "SUPERSEDED_CONTRACT", "REQUIRES_NONCANONICAL_ARGUMENT", "UNSAFE_OR_MUTATING", "DUPLICATE_COVERAGE", "NOT_CURRENT_RUNTIME_CONFIG_LANE"}


def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def tracked_regular_stage_zero(path: str) -> bool:
    if not path or path.startswith("/") or "\\" in path:
        return False
    pure = PurePosixPath(path)
    if pure.as_posix() != path or any(part in {"", ".", ".."} for part in pure.parts):
        return False
    result = subprocess.run(["git", "ls-files", "--stage", "--", path], cwd=ROOT, text=True, capture_output=True, check=False)
    records = [line.split("\t", 1)[0].split() for line in result.stdout.splitlines() if "\t" in line]
    return len(records) == 1 and records[0][0] in {"100644", "100755"} and (ROOT / path).is_file() and not (ROOT / path).is_symlink()


def direct_local_helpers(checker_path: str) -> set[str]:
    source = (ROOT / checker_path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=checker_path)
    found: set[str] = set()
    for node in ast.walk(tree):
        module = None
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("tools.") and alias.name.count(".") == 1:
                    candidate = f"{alias.name.replace('.', '/')}.py"
                    if tracked_regular_stage_zero(candidate):
                        found.add(candidate)
                elif "." not in alias.name and tracked_regular_stage_zero(f"tools/{alias.name}.py"):
                    found.add(f"tools/{alias.name}.py")
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            module = node.module
            if module.startswith("tools.") and module.count(".") == 1:
                candidate = f"{module.replace('.', '/')}.py"
                if tracked_regular_stage_zero(candidate):
                    found.add(candidate)
            elif "." not in module and tracked_regular_stage_zero(f"tools/{module}.py"):
                found.add(f"tools/{module}.py")
    return found


def validate_dependencies(entry: dict[str, object]) -> None:
    dependencies = entry["source_dependencies"]
    if not isinstance(dependencies, list) or not all(isinstance(path, str) for path in dependencies):
        raise ValueError(f"invalid source_dependencies: {entry['id']}")
    if len(dependencies) != len(set(dependencies)):
        raise ValueError(f"duplicate source dependency: {entry['id']}")
    for path in dependencies:
        if path == entry["path"]:
            raise ValueError(f"checker path repeated as source dependency: {entry['id']}")
        if not tracked_regular_stage_zero(path):
            raise ValueError(f"invalid source dependency path: {entry['id']}: {path}")
    required = direct_local_helpers(str(entry["path"]))
    missing = sorted(required - set(dependencies))
    if missing:
        raise ValueError(f"missing direct helper dependencies for {entry['id']}: {', '.join(missing)}")


def validate_branch_policy(entry: dict[str, object]) -> None:
    applicability, policy = entry["applicability"], entry["branch_policy"]
    if applicability not in APPLICABILITIES or policy not in BRANCH_POLICIES:
        raise ValueError(f"invalid applicability/branch_policy: {entry['id']}")
    expected = {"current": {"content_only", "content_and_scope"}, "historical_only": {"named_evidence_branch"}, "unsafe_or_mutating": {"not_run"}}[applicability]
    if policy not in expected:
        raise ValueError(f"invalid applicability/branch_policy pair: {entry['id']}")


def load() -> tuple[list[dict[str, object]], list[dict[str, object]], set[str]]:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    if value.get("schema_version") != 4 or not isinstance(value.get("categories"), list) or not isinstance(value.get("entries"), list) or not isinstance(value.get("strong_signal_exclusions"), list):
        raise ValueError("invalid manifest root")
    categories = set(value["categories"])
    ids: set[str] = set()
    entries: list[dict[str, object]] = []
    for entry in value["entries"]:
        if not isinstance(entry, dict) or set(entry) != REQUIRED:
            raise ValueError(f"invalid checker entry: {entry!r}")
        checker_id = entry["id"]
        if not isinstance(checker_id, str) or checker_id in ids:
            raise ValueError(f"duplicate checker ID: {checker_id}")
        ids.add(checker_id)
        if entry["category"] not in categories:
            raise ValueError(f"invalid category: {entry['category']}")
        if not isinstance(entry["command"], list) or not entry["command"] or not all(isinstance(part, str) for part in entry["command"]):
            raise ValueError(f"invalid command: {checker_id}")
        if entry["path"] != entry["command"][1] or not (ROOT / entry["path"]).is_file():
            raise ValueError(f"missing checker file: {entry['path']}")
        validate_dependencies(entry)
        validate_branch_policy(entry)
        if entry["applicability"] == "current" and (entry["historical"] or not entry["load_bearing"] or entry["required_arguments"] or entry["mutation_risk"] not in {"none", "temporary_file_only", "temporary_repository_only"}):
            raise ValueError(f"unsafe current aggregate entry: {checker_id}")
        if entry["historical"] and entry["applicability"] != "historical_only":
            raise ValueError(f"historical checker incorrectly current: {checker_id}")
        entries.append(entry)
    exclusions: list[dict[str, object]] = []
    exclusion_ids: set[str] = set()
    exclusion_paths: set[str] = set()
    entry_paths = {str(entry["path"]) for entry in entries}
    for exclusion in value["strong_signal_exclusions"]:
        if not isinstance(exclusion, dict) or set(exclusion) != EXCLUSION_REQUIRED:
            raise ValueError(f"invalid strong-signal exclusion: {exclusion!r}")
        exclusion_id, exclusion_path = exclusion["id"], exclusion["path"]
        if not isinstance(exclusion_id, str) or exclusion_id in exclusion_ids:
            raise ValueError(f"duplicate strong-signal exclusion ID: {exclusion_id}")
        if not isinstance(exclusion_path, str) or exclusion_path in exclusion_paths:
            raise ValueError(f"duplicate strong-signal exclusion path: {exclusion_path}")
        if exclusion_path in entry_paths:
            raise ValueError(f"checker appears in manifest and exclusions: {exclusion_path}")
        if exclusion["reason"] not in EXCLUSION_REASONS:
            raise ValueError(f"invalid strong-signal exclusion reason: {exclusion['reason']}")
        if not isinstance(exclusion["detail"], str) or not exclusion["detail"]:
            raise ValueError(f"invalid strong-signal exclusion detail: {exclusion_id}")
        if not exclusion_path.startswith("tools/check_glyph_") or not exclusion_path.endswith(".py") or not (ROOT / exclusion_path).is_file():
            raise ValueError(f"invalid strong-signal exclusion path: {exclusion_path}")
        exclusion_ids.add(exclusion_id)
        exclusion_paths.add(exclusion_path)
        exclusions.append(exclusion)
    census = json.loads(CENSUS.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    census_entries = census.get("entries")
    if not isinstance(census_entries, list):
        raise ValueError("invalid checker census entries")
    strong_paths: set[str] = set()
    for census_entry in census_entries:
        if not isinstance(census_entry, dict) or not isinstance(census_entry.get("path"), str):
            raise ValueError("invalid checker census entry")
        signals = census_entry.get("runtime_config_relevance_signals")
        if not isinstance(signals, list) or not all(isinstance(signal, str) for signal in signals):
            raise ValueError(f"invalid checker census relevance signals: {census_entry['path']}")
        if signals:
            strong_paths.add(census_entry["path"])
    for path in sorted(strong_paths - entry_paths - exclusion_paths):
        raise ValueError(f"unclassified strong-signal checker: {path}")
    for path in sorted(exclusion_paths - strong_paths):
        raise ValueError(f"strong-signal exclusion lacks census signal: {path}")
    return entries, exclusions, categories


def context() -> dict[str, object]:
    branch = subprocess.run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.strip()
    return {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "branch": branch or None, "detached": not bool(branch), "base": subprocess.run(["git", "merge-base", "HEAD", "origin/configurator"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.strip() or None}


def census_freshness() -> dict[str, object]:
    committed = CENSUS.read_text(encoding="utf-8")
    expected = render_census(generate_census(ROOT))
    return {
        "id": "checker_census_freshness",
        "path": "tools/check_glyph_checker_census.py",
        "category": "baseline",
        "applicability": "current",
        "load_bearing": True,
        "status": "PASS" if committed == expected else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", action="append")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    try:
        freshness = census_freshness()
        if freshness["status"] != "PASS":
            raise ValueError("checker census is stale; run tools/generate_glyph_checker_census.py")
        entries, exclusions, categories = load()
        if args.category and any(category not in categories for category in args.category):
            raise ValueError("unknown category: " + ", ".join(sorted(set(args.category) - categories)))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"glyph_runtime_config_validation_manifest: FAIL: {exc}")
        return 1
    if args.check_manifest:
        print(f"glyph_runtime_config_validation_manifest: PASS; entries={len(entries)}; strong_signal_exclusions={len(exclusions)}")
        return 0
    selected = [entry for entry in entries if entry["applicability"] == "current" and (not args.category or entry["category"] in args.category)]
    results = []
    for entry in selected:
        started = monotonic()
        completed = subprocess.run(entry["command"], cwd=ROOT, text=True, capture_output=True, check=False)
        passed = completed.returncode == 0
        results.append({"id": entry["id"], "command": entry["command"], "category": entry["category"], "applicability": entry["applicability"], "exit_code": completed.returncode, "status": "PASS" if passed else "FAIL", "stdout_summary": completed.stdout.strip().splitlines()[-1:] , "stderr_summary": completed.stderr.strip().splitlines()[-1:], "duration_seconds": round(monotonic() - started, 3)})
        if args.fail_fast and not passed:
            break
    passed = all(result["status"] == "PASS" for result in results)
    output = {"status": "PASS" if passed else "FAIL", "context": context(), "census_freshness": freshness, "results": results, "excluded": [{"id": entry["id"], "applicability": entry["applicability"], "reason": entry["reason"]} for entry in entries if entry["applicability"] != "current"] + [{"id": exclusion["id"], "applicability": "excluded", "reason": exclusion["reason"]} for exclusion in exclusions]}
    if args.json:
        print(json.dumps(output, sort_keys=True))
    else:
        print(f"glyph_runtime_config_validation: {output['status']}")
        for result in results:
            print(f"- {result['id']}: {result['status']}")
        print("excluded=" + ",".join(item["id"] for item in output["excluded"]))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
