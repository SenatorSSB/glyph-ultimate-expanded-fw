#!/usr/bin/env python3
"""Read-only deterministic aggregate runner for current runtime-config checks."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
REQUIRED = {"id", "path", "command", "category", "applicability", "branch_policy", "required_arguments", "mutation_risk", "source_dependencies", "load_bearing", "historical", "reason"}


def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load() -> tuple[list[dict[str, object]], set[str]]:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    if value.get("schema_version") != 2 or not isinstance(value.get("categories"), list) or not isinstance(value.get("entries"), list):
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
        if entry["applicability"] == "current" and (entry["historical"] or not entry["load_bearing"] or entry["required_arguments"] or entry["mutation_risk"] not in {"none", "temporary_file_only", "temporary_repository_only"}):
            raise ValueError(f"unsafe current aggregate entry: {checker_id}")
        if entry["historical"] and entry["applicability"] != "historical_only":
            raise ValueError(f"historical checker incorrectly current: {checker_id}")
        entries.append(entry)
    return entries, categories


def context() -> dict[str, object]:
    branch = subprocess.run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.strip()
    return {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "branch": branch or None, "detached": not bool(branch), "base": subprocess.run(["git", "merge-base", "HEAD", "origin/configurator"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.strip() or None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", action="append")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    try:
        entries, categories = load()
        if args.category and any(category not in categories for category in args.category):
            raise ValueError("unknown category: " + ", ".join(sorted(set(args.category) - categories)))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"glyph_runtime_config_validation_manifest: FAIL: {exc}")
        return 1
    if args.check_manifest:
        print(f"glyph_runtime_config_validation_manifest: PASS; entries={len(entries)}")
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
    output = {"status": "PASS" if passed else "FAIL", "context": context(), "results": results, "excluded": [{"id": entry["id"], "applicability": entry["applicability"], "reason": entry["reason"]} for entry in entries if entry["applicability"] != "current"]}
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
