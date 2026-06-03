#!/usr/bin/env python3
"""Validate the Glyph export artifact compatibility index."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_export_artifact_compatibility_index_2026-06-03.json"
)
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_export_artifact_compatibility_index_2026-06-03.md"
GENERATED_CONFIG_EVALUATOR_CHECKER = (
    REPO_ROOT / "tools/check_glyph_identity_runtime_generated_config_evaluator_input.py"
)
GENERATED_CPP_DIFF_CHECKER = REPO_ROOT / "tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py"

SCHEMA_NAME = "glyph_export_artifact_compatibility_index"
INDEX_VERSION = 1
STATUS = "docs_tools_compatibility_index"
HARDWARE_STATUS = "not_new_hardware_result"
NUNCHUK_STATUS = "preserved_but_not_hardware_validated"
ACCEPTED_HARDWARE_CAVEAT_STATUSES = (
    "not_new_hardware_result",
    "cases_derive_from_hardware_verified_role_map_but_are_not_new_hardware_results",
)

REQUIRED_ARTIFACT_NODES = (
    "generated_config_prototype",
    "generated_config_contract",
    "runtime_config_candidate_sample",
    "runtime_config_candidate_validator_contract",
    "senscope_export_package_sample",
    "senscope_export_contract",
    "runtime_config_validation_report",
    "behavior_cases",
    "behavior_evaluator",
    "generated_cpp_review_artifact",
)
REQUIRED_INVARIANTS = (
    "generated-config tables equal runtime-candidate tables",
    "generated-config role bindings equal runtime-candidate role bindings",
    "generated-config hard overrides equal runtime-candidate hard overrides",
    "generated-config priority lists equal runtime-candidate priority references",
    "generated-config suppression rules equal runtime-candidate suppression rules",
    "Senscope export nested generated config equals committed generated-config prototype",
    "validation report summarizes the committed runtime-candidate sample",
    "runtime-candidate validation report table count equals generated-config table count",
    "generated-config-backed evaluator path still validates behavior cases",
    "all artifacts preserve hardware and nunchuk caveats",
)
REQUIRED_DOC_CAVEATS = (
    "not firmware source",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
    "not nunchuk hardware validation",
)


class ExportArtifactCompatibilityIndexError(ValueError):
    """Raised when the compatibility index drifts from committed artifacts."""


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise ExportArtifactCompatibilityIndexError(message)


def load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{display(path)} must contain a JSON object")
    return data


def collect_repo_relative_paths(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str) and (value.startswith("docs/") or value.startswith("tools/")):
        found.append(value)
    elif isinstance(value, dict):
        for child in value.values():
            found.extend(collect_repo_relative_paths(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(collect_repo_relative_paths(child))
    return found


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{key} must be a string list")
    return value


def run_checker(path: Path) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, str(path.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    return completed.returncode, output


def validate_doc(index: dict[str, Any]) -> None:
    caveats = require_string_list(index, "doc_caveats")
    if caveats != list(REQUIRED_DOC_CAVEATS):
        fail("doc_caveats drifted from required compatibility caveats")

    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_CAVEATS:
        if phrase not in lowered:
            fail(f"{display(DOC_PATH)} missing required phrase: {phrase}")


def validate_top_level(index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    expected = {
        "schema_name": SCHEMA_NAME,
        "index_version": INDEX_VERSION,
        "status": STATUS,
        "hardware_status": HARDWARE_STATUS,
        "nunchuk_status": NUNCHUK_STATUS,
    }
    for key, value in expected.items():
        if index.get(key) != value:
            fail(f"{key} must be {value!r}")

    nodes = index.get("artifact_nodes")
    if not isinstance(nodes, dict):
        fail("artifact_nodes must be an object")

    missing = [node for node in REQUIRED_ARTIFACT_NODES if node not in nodes]
    if missing:
        fail("artifact_nodes missing: " + ", ".join(missing))

    invariants = require_string_list(index, "required_invariants")
    missing_invariants = [item for item in REQUIRED_INVARIANTS if item not in invariants]
    if missing_invariants:
        fail("required_invariants missing: " + ", ".join(missing_invariants))

    return nodes


def validate_referenced_paths(index: dict[str, Any], nodes: dict[str, dict[str, Any]]) -> None:
    rel_paths = sorted(set(collect_repo_relative_paths(index)))
    if not rel_paths:
        fail("index must reference committed docs/tools artifacts")

    resolved: dict[str, Path] = {}
    for rel_path in rel_paths:
        path = REPO_ROOT / rel_path
        if not path.exists():
            fail(f"referenced path does not exist: {rel_path}")
        resolved[rel_path] = path

    for name in REQUIRED_ARTIFACT_NODES:
        node = nodes[name]
        if not isinstance(node, dict):
            fail(f"artifact_nodes.{name} must be an object")
        rel_path = node.get("path")
        if not isinstance(rel_path, str):
            fail(f"artifact_nodes.{name}.path must be a string")
        if rel_path not in resolved:
            fail(f"artifact_nodes.{name}.path must be a referenced committed artifact path")


def load_node_json(nodes: dict[str, dict[str, Any]], name: str) -> dict[str, Any]:
    return load_json_object(REPO_ROOT / nodes[name]["path"])


def validate_artifact_invariants(nodes: dict[str, dict[str, Any]]) -> None:
    prototype = load_node_json(nodes, "generated_config_prototype")
    candidate = load_node_json(nodes, "runtime_config_candidate_sample")
    export_package = load_node_json(nodes, "senscope_export_package_sample")
    validation_report = load_node_json(nodes, "runtime_config_validation_report")

    if prototype.get("tables") != candidate.get("tables"):
        fail("generated-config tables do not match runtime-candidate tables")
    if prototype.get("role_bindings") != candidate.get("role_bindings"):
        fail("generated-config role_bindings do not match runtime-candidate role_bindings")
    if prototype.get("hard_overrides") != candidate.get("hard_overrides"):
        fail("generated-config hard_overrides do not match runtime-candidate hard_overrides")

    priority_model = prototype.get("priority_model")
    if not isinstance(priority_model, dict):
        fail("generated_config_prototype.priority_model must be an object")
    expected_priority = {
        "digital": priority_model.get("digital_effective_direction"),
        "analog": priority_model.get("analog"),
    }
    if candidate.get("priority_references") != expected_priority:
        fail("generated-config priority lists do not match runtime-candidate priority references")
    if prototype.get("suppression_rules") != candidate.get("suppression_rules"):
        fail("generated-config suppression rules do not match runtime-candidate suppression rules")

    if export_package.get("glyph_generated_config_prototype") != prototype:
        fail("Senscope export nested generated config does not match the committed generated-config prototype")

    candidate_tables = candidate.get("tables")
    prototype_tables = prototype.get("tables")
    if not isinstance(candidate_tables, dict) or not isinstance(prototype_tables, dict):
        fail("generated-config and runtime-candidate tables must both be objects")

    if validation_report.get("validated_candidate_schema_name") != candidate.get("schema_name"):
        fail("validation report validated_candidate_schema_name does not match the committed runtime-candidate sample")
    if validation_report.get("sample_candidate_validation_status") != "PASS":
        fail("validation report must summarize a PASS committed runtime-candidate sample")

    source_authority = validation_report.get("source_authority")
    if not isinstance(source_authority, dict):
        fail("runtime_config_validation_report.source_authority must be an object")
    if source_authority.get("sample_candidate") != nodes["runtime_config_candidate_sample"]["path"]:
        fail("validation report must cite the committed runtime-candidate sample fixture")

    candidate_non_goals = candidate.get("non_goals")
    report_non_goals = validation_report.get("required_non_goals")
    if not isinstance(candidate_non_goals, list) or not isinstance(report_non_goals, list):
        fail("candidate/report non_goals must be lists")
    if set(report_non_goals) != set(candidate_non_goals):
        fail("validation report required_non_goals must summarize the committed runtime-candidate sample non_goals")

    if validation_report.get("table_count") != len(candidate_tables):
        fail("validation report table_count does not match runtime-candidate table count")
    if validation_report.get("table_count") != len(prototype_tables):
        fail("validation report table_count does not match generated-config table count")


def validate_caveat_preservation(nodes: dict[str, dict[str, Any]]) -> None:
    json_nodes = (
        "generated_config_prototype",
        "generated_config_contract",
        "runtime_config_candidate_sample",
        "runtime_config_candidate_validator_contract",
        "senscope_export_package_sample",
        "senscope_export_contract",
        "runtime_config_validation_report",
        "behavior_cases",
    )
    for name in json_nodes:
        payload = load_node_json(nodes, name)
        if "hardware_status" in payload and payload.get("hardware_status") not in ACCEPTED_HARDWARE_CAVEAT_STATUSES:
            fail(f"{name} hardware_status must preserve a not-new-hardware caveat status")
        if "nunchuk_status" in payload and payload.get("nunchuk_status") != NUNCHUK_STATUS:
            fail(f"{name} nunchuk_status must stay {NUNCHUK_STATUS!r}")

    export_package = load_node_json(nodes, "senscope_export_package_sample")
    if export_package.get("hardware_status_caveat") != "Sample package only; not hardware validation.":
        fail("senscope_export_package_sample must preserve the not-hardware-validation caveat")
    if export_package.get("nunchuk_status_caveat") != (
        "Nunchuk behavior is preserved but not hardware validated by this package."
    ):
        fail("senscope_export_package_sample must preserve the nunchuk non-validation caveat")


def validate_checker_backed_artifacts() -> None:
    evaluator_returncode, evaluator_output = run_checker(GENERATED_CONFIG_EVALUATOR_CHECKER)
    if evaluator_returncode != 0 or "status=PASS" not in evaluator_output:
        fail("generated-config-backed evaluator path no longer validates behavior cases")

    cpp_returncode, cpp_output = run_checker(GENERATED_CPP_DIFF_CHECKER)
    if cpp_returncode != 0 or "status=PASS" not in cpp_output:
        fail("generated C++ review artifact no longer passes its committed checker")


def main() -> int:
    print("glyph_export_artifact_compatibility_index")
    try:
        index = load_json_object(FIXTURE_PATH)
        nodes = validate_top_level(index)
        validate_referenced_paths(index, nodes)
        validate_doc(index)
        validate_artifact_invariants(nodes)
        validate_caveat_preservation(nodes)
        validate_checker_backed_artifacts()
    except (OSError, ValueError, json.JSONDecodeError, ExportArtifactCompatibilityIndexError) as exc:
        print("status=FAIL")
        print("artifact_nodes=0")
        print("required_invariants=0")
        print(f"hardware_status={HARDWARE_STATUS}")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"artifact_nodes={len(index['artifact_nodes'])}")
    print(f"required_invariants={len(index['required_invariants'])}")
    print(f"hardware_status={index['hardware_status']}")
    print(f"fixture={display(FIXTURE_PATH)}")
    print(f"doc={display(DOC_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
