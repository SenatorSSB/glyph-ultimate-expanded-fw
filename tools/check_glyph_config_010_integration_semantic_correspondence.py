#!/usr/bin/env python3
"""Fail closed on GP-CONFIG-010 integration semantic or X1 source drift."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from glyph_hardware_correspondence import CorrespondenceError, verify_correspondence

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/gp_config_010_integration_semantic_correspondence.json"
ALLOWED = {"EXACT_SOURCE_MATCH", "SEMANTICALLY_IDENTICAL_WITH_CONTEXT_CHANGE", "DIFFERENT"}
EXPECTED_IDS = [
    "type_traits_extent_support",
    "named_capacity_30",
    "generated_extent_equality",
    "default_13_fit",
    "capacity_sized_storage",
    "selection_oversize_guard",
    "setup_oversize_guard",
    "valid_ordering_bindings_applicability_selection_unchanged",
]
EXPECTED_FIELDS = {
    "schema_name", "schema_version", "work_order", "historical_candidate",
    "historical_base", "authorized_integration_base", "candidate_branch",
    "containing_commit_parent", "source_path", "base_source_blob",
    "historical_candidate_source_blob", "integration_candidate_source_blob",
    "exact_source_diff_sha256", "accepted_x1_candidate",
    "generated_baseline_path", "accepted_x1_generated_baseline_blob",
    "integration_generated_baseline_blob", "semantics",
    "behaviorally_relevant_differences",
}
INTEGRATION_CANDIDATE = "1c0ff22646729d26d45eacb4b8322c5baea7de48"
REVIEWED_CANONICAL = "2fd9a827b90b2079f981d75e836833dc99ec7b10"
CURRENT_SOURCE_BLOB = "7d659d3133271c2ed956a16d8f5e3eda73040f81"
CURRENT_BASELINE_BLOB = "40a0b4703b3cbc5800acca5f2fdc3229bd82844a"
REVIEWED_POST_INTEGRATION_PATHS = {
    "docs/AGENT_CONTEXT.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
    "docs/agent_framework/GP_CONFIG_010_INTEGRATION_HARDWARE_PROTOCOL.md",
    "docs/agent_framework/GP_CONFIG_010_INTEGRATION_HARDWARE_RESULT_20260923.md",
    "docs/agent_framework/HARDWARE_CORRESPONDENCE.md",
    "docs/agent_framework/README.md",
    "docs/agent_framework/USER_DIRECTION.md",
    "docs/calibration/fixtures/gp_config_010_integration_hardware_evidence_2026-09-23.json",
    "docs/project/ACTIVE_AGENT_QUEUE.md",
    "docs/project/DEFERRED_CONFIG_WORK_2026-09-21.md",
    "tools/glyph_hardware_correspondence.py",
}


class ContractError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def git(*args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, input=input_bytes, capture_output=True, check=False
    )
    require(result.returncode == 0, f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def object_id(ref: str, path: str) -> str:
    return git("rev-parse", f"{ref}:{path}").decode().strip()


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def current_main() -> int:
    """Prove accepted content and finite scope on a current canonical descendant."""
    try:
        value = json.loads(FIXTURE.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        require(set(value) == EXPECTED_FIELDS, "top-level fields drift")
        require(value["schema_name"] == "glyph_gp_config_010_integration_semantic_correspondence", "schema name")
        require(value["schema_version"] == 1 and value["work_order"] == "GP-CONFIG-010", "schema/work order")
        fixture_path = FIXTURE.relative_to(ROOT).as_posix()
        require(git("hash-object", fixture_path).decode().strip() == object_id("HEAD", fixture_path), "dirty semantic fixture")
        require(value["containing_commit_parent"] == value["authorized_integration_base"], "historical parent fixture drift")
        require(value["integration_candidate_source_blob"] == CURRENT_SOURCE_BLOB, "accepted source fixture drift")
        require(value["historical_candidate_source_blob"] == CURRENT_SOURCE_BLOB, "historical source fixture drift")
        require(value["accepted_x1_generated_baseline_blob"] == CURRENT_BASELINE_BLOB, "accepted table fixture drift")
        require(value["integration_generated_baseline_blob"] == CURRENT_BASELINE_BLOB, "integration table fixture drift")
        source_path = value["source_path"]
        baseline_path = value["generated_baseline_path"]
        require(source_path == "src/core/mode_selection.cpp", "source path drift")
        require(baseline_path == "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp", "table path drift")
        head = git("rev-parse", "HEAD").decode().strip()
        for ancestor in (INTEGRATION_CANDIDATE, REVIEWED_CANONICAL):
            result = subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, head], cwd=ROOT, capture_output=True)
            require(result.returncode == 0, f"current HEAD does not descend from reviewed {ancestor}")
        require(git("rev-list", "--parents", "-n", "1", INTEGRATION_CANDIDATE).decode().split() ==
                [INTEGRATION_CANDIDATE, value["authorized_integration_base"]], "integration candidate parent drift")
        reviewed_paths = set(filter(None, git("diff", "--no-renames", "--name-only", "-z", INTEGRATION_CANDIDATE, REVIEWED_CANONICAL).decode().split("\0")))
        require(reviewed_paths == REVIEWED_POST_INTEGRATION_PATHS, "reviewed 12-path post-integration inventory drift")
        require(object_id(value["historical_base"], source_path) == value["base_source_blob"], "historical base source drift")
        require(object_id(value["historical_candidate"], source_path) == CURRENT_SOURCE_BLOB, "historical candidate source drift")
        require(object_id(INTEGRATION_CANDIDATE, source_path) == CURRENT_SOURCE_BLOB, "integration candidate source drift")
        historical_diff = git("diff", "--no-ext-diff", value["historical_base"], value["historical_candidate"], "--", source_path)
        integration_diff = git("diff", "--no-ext-diff", value["authorized_integration_base"], INTEGRATION_CANDIDATE, "--", source_path)
        require(historical_diff == integration_diff and hashlib.sha256(integration_diff).hexdigest() == value["exact_source_diff_sha256"], "historical production patch drift")
        require(object_id(value["accepted_x1_candidate"], baseline_path) == CURRENT_BASELINE_BLOB, "accepted X1 table drift")
        require(object_id(value["authorized_integration_base"], baseline_path) == CURRENT_BASELINE_BLOB, "integration base table drift")
        for path, expected in ((source_path, CURRENT_SOURCE_BLOB), (baseline_path, CURRENT_BASELINE_BLOB)):
            entry = git("ls-tree", head, "--", path).decode().split()
            require(len(entry) >= 3 and entry[:2] == ["100644", "blob"], f"non-regular current input: {path}")
            require(object_id(head, path) == expected, f"committed current input drift: {path}")
            require(git("hash-object", path).decode().strip() == expected, f"dirty current input: {path}")
        semantics = value["semantics"]
        require([entry["id"] for entry in semantics] == EXPECTED_IDS, "semantic inventory missing, duplicate, or reordered")
        source = (ROOT / source_path).read_text(encoding="utf-8")
        for entry in semantics:
            require(set(entry) == {"id", "classification", "source"}, f"semantic fields: {entry.get('id')}")
            require(entry["classification"] == "EXACT_SOURCE_MATCH" and entry["source"] in source,
                    f"semantic source/classification drift: {entry.get('id')}")
        require(value["behaviorally_relevant_differences"] == [], "behaviorally relevant difference")
        verify_correspondence(ROOT, INTEGRATION_CANDIDATE, value["authorized_integration_base"],
                              target=head, integrated=True, check_worktree=True)
        print("glyph_config_010_integration_semantic_correspondence: PASS (current descendant)")
        print("- production semantics: 8 EXACT_SOURCE_MATCH")
        print("- generated baseline: exact accepted GP-X1-002 28-table blob")
        print("- descendant scope: finite reviewed correspondence inventory")
        return 0
    except (OSError, ValueError, KeyError, TypeError, ContractError, CorrespondenceError) as exc:
        print(f"glyph_config_010_integration_semantic_correspondence: FAIL: {exc}")
        return 1


def main() -> int:
    try:
        require(sys.argv[1:] == ["--historical"], "expected --historical")
        value = json.loads(FIXTURE.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        require(set(value) == EXPECTED_FIELDS, "top-level fields drift")
        require(value["schema_name"] == "glyph_gp_config_010_integration_semantic_correspondence", "schema name")
        require(value["schema_version"] == 1 and value["work_order"] == "GP-CONFIG-010", "schema/work order")
        source_path = value["source_path"]
        baseline_path = value["generated_baseline_path"]
        head = git("rev-parse", "HEAD").decode().strip()
        branch = git("branch", "--show-current").decode().strip()
        parents = git("rev-list", "--parents", "-n", "1", head).decode().split()
        require(branch == value["candidate_branch"], "candidate branch identity drift")
        require(parents == [head, value["containing_commit_parent"]], "candidate must be a direct child of authorized base")
        require(head == INTEGRATION_CANDIDATE, "historical integration candidate identity drift")
        source_entry = git("ls-tree", head, "--", source_path).decode().split()
        require(len(source_entry) >= 3 and source_entry[:2] == ["100644", "blob"], "candidate source must be regular non-executable 100644")
        fixture_rel = FIXTURE.relative_to(ROOT).as_posix()
        fixture_entry = git("ls-tree", head, "--", fixture_rel).decode().split()
        require(len(fixture_entry) >= 3 and fixture_entry[:2] == ["100644", "blob"], "semantic fixture must be regular non-executable 100644")
        require(subprocess.run(["git", "diff", "--quiet", "HEAD", "--", source_path], cwd=ROOT).returncode == 0, "candidate source has unstaged drift")
        require(subprocess.run(["git", "diff", "--cached", "--quiet", "HEAD", "--", source_path], cwd=ROOT).returncode == 0, "candidate source has staged drift")

        historical_base_blob = object_id(value["historical_base"], source_path)
        integration_base_blob = object_id(value["authorized_integration_base"], source_path)
        historical_candidate_blob = object_id(value["historical_candidate"], source_path)
        working_source_blob = git("hash-object", source_path).decode().strip()
        committed_source_blob = object_id(head, source_path)
        require(historical_base_blob == value["base_source_blob"], "historical base source blob drift")
        require(integration_base_blob == value["base_source_blob"], "integration base source context drift")
        require(historical_candidate_blob == value["historical_candidate_source_blob"], "historical candidate source blob drift")
        require(working_source_blob == value["integration_candidate_source_blob"], "integration candidate source blob drift")
        require(committed_source_blob == value["integration_candidate_source_blob"], "committed integration source blob drift")
        require(working_source_blob == historical_candidate_blob, "production source is not an exact source match")

        historical_diff = git("diff", "--no-ext-diff", value["historical_base"], value["historical_candidate"], "--", source_path)
        integration_diff = git("diff", "--no-ext-diff", value["authorized_integration_base"], head, "--", source_path)
        require(historical_diff == integration_diff, "exact production source diff drift")
        require(hashlib.sha256(integration_diff).hexdigest() == value["exact_source_diff_sha256"], "source diff digest drift")

        semantics = value["semantics"]
        require([entry["id"] for entry in semantics] == EXPECTED_IDS, "semantic inventory missing, duplicate, or reordered")
        source = (ROOT / source_path).read_text(encoding="utf-8")
        for entry in semantics:
            require(set(entry) == {"id", "classification", "source"}, f"semantic fields: {entry.get('id')}")
            require(entry["classification"] in ALLOWED, f"invalid classification: {entry['id']}")
            require(entry["classification"] == "EXACT_SOURCE_MATCH", f"behaviorally relevant result is not exact: {entry['id']}")
            require(entry["source"] in source, f"missing exact semantic source: {entry['id']}")
        require(value["behaviorally_relevant_differences"] == [], "behaviorally relevant DIFFERENT result")

        accepted_baseline_blob = object_id(value["accepted_x1_candidate"], baseline_path)
        integration_base_baseline_blob = object_id(value["authorized_integration_base"], baseline_path)
        working_baseline_blob = git("hash-object", baseline_path).decode().strip()
        expected_baseline_blob = value["accepted_x1_generated_baseline_blob"]
        require(accepted_baseline_blob == expected_baseline_blob, "accepted GP-X1-002 baseline blob drift")
        require(integration_base_baseline_blob == expected_baseline_blob, "authorized base does not preserve accepted GP-X1-002 baseline")
        require(working_baseline_blob == value["integration_generated_baseline_blob"], "integration generated baseline drift")
        require(working_baseline_blob == expected_baseline_blob, "integration does not preserve all accepted table bytes")

        print("glyph_config_010_integration_semantic_correspondence: PASS")
        print("- production semantics: 8 EXACT_SOURCE_MATCH")
        print("- behaviorally relevant differences: 0")
        print("- generated baseline: exact accepted GP-X1-002 28-table blob")
        return 0
    except (OSError, ValueError, KeyError, TypeError, ContractError) as exc:
        print(f"glyph_config_010_integration_semantic_correspondence: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    if not sys.argv[1:]:
        raise SystemExit(current_main())
    raise SystemExit(main())
