#!/usr/bin/env python3
"""Fixture-backed CLI and contract regression matrix for intake v1."""
from __future__ import annotations

import copy
import io
import json
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

import manage_source_owned_source_authority_intake as intake_cli
import source_owned_source_authority_intake as intake_module
from source_owned_generator_modes import GeneratorModesError, _baseline_tables
from source_owned_source_authority_intake import (
    EXIT_CODES,
    PLACEHOLDER,
    IntakeError,
    assert_safe_offline_output_path,
    create_template,
    emit_generator_input,
    inspect_baseline,
    review_intake,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs/runtime_config/fixtures/source_owned_source_authority_intake.json"
MANAGE = ROOT / "tools/manage_source_owned_source_authority_intake.py"
PRECEDENCE_CASE_IDS = ["baseline_over_authority_and_ownership"]
PROTECTED_PATH_CASE_IDS = [
    "component_src", "component_SRC", "component_Src", "component_include", "component_INCLUDE",
    "component_lib", "component_LIB", "component_backend", "component_BACKEND", "component_HAL",
    "component_hal", "component_dot_git", "component_dot_GIT", "publication_candidate",
    "publication_CANDIDATE", "publication_active_storage", "publication_ACTIVE_STORAGE",
    "publication_runtime_config", "publication_RUNTIME_CONFIG",
]
GENERATOR_ERROR_CASE_IDS = [
    "inspect_baseline_generator_error", "create_template_generator_error",
    "review_generator_error", "emission_generator_error",
]
POSITIVE = 0
NEGATIVE = 0


def make_packet(mode: str = "overlay_preserve", operation: str = "production_changeset", owned_count: int = 1) -> dict:
    baseline = inspect_baseline()
    symbols = baseline["table_order"][:owned_count if mode == "overlay_preserve" else 28]
    tables = {table["table_symbol"]: table for table in _baseline_tables()}
    replacements, declarations = [], []
    for symbol in symbols:
        points = [{"direction_key": i + 1, "x": point["x"], "y": point["y"]} for i, point in enumerate(tables[symbol]["points"])]
        if operation == "production_changeset":
            points[4]["x"] = 127 if points[4]["x"] != 127 else 126
        replacements.append({"table_symbol": symbol, "points": points, "rationale": "human-approved table replacement", "source_reference": "user-source-authority-reference"})
        declarations.append({"table_symbol": symbol, "rationale": "human approved ownership", "authorization_reference": "user-source-authority-reference"})
    return {
        "schema_version": 1, "intake_id": "fixture-intake", "profile_id": "fixture-profile", "profile_name": "fixture-profile",
        "purpose": "fixture only; does not imply hardware validity", "author": "fixture-author", "notes": "synthetic checker fixture",
        "authority": {"status": "approved", "basis": "human source authority record", "approver": "fixture-reviewer", "statement": "approved for offline generator-input validation only", "approval_reference": "fixture-approval"},
        "intent": {"provenance_class": "production_authorized" if operation == "production_changeset" else "source_baseline_derived", "generation_mode": mode, "requested_operation": operation, "controller_scope": "Glyph Mk6", "source_owned_runtime_tables": True},
        "baseline": baseline,
        "ownership": {"owned_tables": symbols, "declarations": declarations, "unlisted_tables_are_unowned": True},
        "replacements": replacements,
        "review": {"unresolved_questions": [], "acknowledges_build_not_hardware_proof": True, "acknowledges_separate_hardware_gate": True},
    }


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(MANAGE), *arguments], cwd=ROOT, text=True, capture_output=True, check=False)


def assert_review_case(case: dict, mutation) -> None:
    global NEGATIVE
    packet = make_packet()
    mutation(packet)
    report = review_intake(packet)
    actual_codes = {blocker["code"] for blocker in report["blockers"]}
    actual_categories = {blocker["category"] for blocker in report["blockers"]}
    assert not report["production_emission_allowed"] and not report["source_equivalence_emission_allowed"], case["case_id"]
    assert set(case["expected_blocker_codes"]).issubset(actual_codes), (case["case_id"], case["expected_blocker_codes"], actual_codes)
    assert set(case.get("expected_blocker_categories", [])).issubset(actual_categories), (case["case_id"], case.get("expected_blocker_categories"), actual_categories)
    NEGATIVE += 1


def run() -> tuple[int, int]:
    global POSITIVE, NEGATIVE
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    cases: list[tuple[str, int, list[str], object]] = []

    def add(case_id: str, exit_code: int, codes: list[str], mutation) -> None:
        cases.append((case_id, exit_code, codes, mutation))

    add("missing_schema_version", 2, ["TOP_LEVEL_SCHEMA"], lambda packet: packet.pop("schema_version"))
    add("unknown_schema_version", 2, ["SCHEMA_VERSION"], lambda packet: packet.__setitem__("schema_version", 99))
    add("missing_authority_status", 3, ["AUTHORITY_SHAPE"], lambda packet: packet["authority"].pop("status"))
    for case_id, status in (("draft_production", "draft"), ("submitted_production", "submitted_for_review"), ("rejected_production", "rejected"), ("superseded_production", "superseded")):
        add(case_id, 3, ["NOT_APPROVED"], lambda packet, value=status: packet["authority"].__setitem__("status", value))
    add("approved_missing_approver", 3, ["APPROVAL_EVIDENCE"], lambda packet: packet["authority"].__setitem__("approver", ""))
    add("approved_missing_basis", 3, ["APPROVAL_EVIDENCE"], lambda packet: packet["authority"].__setitem__("basis", ""))
    add("production_without_approval", 3, ["NOT_APPROVED"], lambda packet: packet["authority"].__setitem__("status", "draft"))
    for case_id, provenance in (("synthetic_production", "synthetic_test"), ("example_production", "example_only"), ("migrated_legacy_production", "migrated_legacy"), ("unknown_provenance", "unknown")):
        add(case_id, 3, ["PRODUCTION_PROVENANCE"], lambda packet, value=provenance: packet["intent"].__setitem__("provenance_class", value))
    add("missing_generation_mode", 2, ["GENERATION_MODE"], lambda packet: packet["intent"].__setitem__("generation_mode", None))
    add("reject_partial", 6, ["REJECT_PARTIAL"], lambda packet: packet["intent"].__setitem__("generation_mode", "reject_partial"))
    add("replacement_without_ownership", 5, ["OWNERSHIP_REPLACEMENT_MISMATCH"], lambda packet: packet["ownership"].__setitem__("owned_tables", []))
    add("ownership_without_replacement", 5, ["OWNERSHIP_REPLACEMENT_MISMATCH"], lambda packet: packet.__setitem__("replacements", []))
    add("unowned_replacement", 5, ["OWNERSHIP_REPLACEMENT_MISMATCH"], lambda packet: packet["ownership"].__setitem__("owned_tables", []))
    add("duplicate_owned", 5, ["DUPLICATE_OWNERSHIP"], lambda packet: packet["ownership"]["owned_tables"].append(packet["ownership"]["owned_tables"][0]))
    add("duplicate_replacement", 5, ["DUPLICATE_REPLACEMENT"], lambda packet: packet["replacements"].append(copy.deepcopy(packet["replacements"][0])))
    add("unknown_table", 5, ["UNKNOWN_OWNERSHIP"], lambda packet: packet["ownership"]["owned_tables"].__setitem__(0, "kUnknownTable"))
    add("empty_production_changeset", 6, ["EMPTY_PRODUCTION_CHANGESET"], lambda packet: (packet["ownership"].__setitem__("owned_tables", []), packet["ownership"].__setitem__("declarations", []), packet.__setitem__("replacements", [])))
    add("full_missing_table", 5, ["FULL_REPLACEMENT_OWNERSHIP"], lambda packet: packet["intent"].__setitem__("generation_mode", "full_replacement"))
    add("full_extra_table", 5, ["UNKNOWN_OWNERSHIP"], lambda packet: (packet["intent"].__setitem__("generation_mode", "full_replacement"), packet["ownership"]["owned_tables"].append("kUnknownTable")))
    add("full_wildcard", 5, ["UNKNOWN_OWNERSHIP"], lambda packet: packet["ownership"]["owned_tables"].__setitem__(0, "*"))
    add("stale_baseline", 4, ["BASELINE_MISMATCH"], lambda packet: packet["baseline"].__setitem__("semantic_digest", "stale"))
    add("wrong_source_path", 4, ["BASELINE_MISMATCH"], lambda packet: packet["baseline"].__setitem__("source_path", "wrong"))
    add("wrong_table_count", 4, ["BASELINE_MISMATCH"], lambda packet: packet["baseline"].__setitem__("table_count", 27))
    add("changed_source_baseline_derived", 3, ["PRODUCTION_PROVENANCE"], lambda packet: packet["intent"].__setitem__("provenance_class", "source_baseline_derived"))
    add("unresolved_question", 3, ["UNRESOLVED_BLOCKER"], lambda packet: packet["review"].__setitem__("unresolved_questions", [{"question": "unknown", "blocking": True}]))
    add("placeholder_approval", 3, ["APPROVAL_EVIDENCE"], lambda packet: packet["authority"].__setitem__("approver", PLACEHOLDER))
    add("placeholder_point", 2, ["POINT_COORDINATE"], lambda packet: packet["replacements"][0]["points"][0].__setitem__("x", PLACEHOLDER))
    add("invalid_coordinate", 2, ["POINT_COORDINATE"], lambda packet: packet["replacements"][0]["points"][0].__setitem__("x", -1))
    add("wrong_point_count", 2, ["POINT_COUNT"], lambda packet: packet["replacements"][0].__setitem__("points", []))
    add("nondeterministic_order", 2, ["POINT_ORDER"], lambda packet: packet["replacements"][0]["points"].__setitem__(0, {"direction_key": 2, "x": 1, "y": 1}))
    add("infer_from_replacement", 5, ["DECLARATION_MISMATCH"], lambda packet: packet["ownership"].__setitem__("declarations", []))
    add("infer_from_difference", 5, ["DECLARATION_MISMATCH"], lambda packet: packet["ownership"].__setitem__("owned_tables", []))
    add("canonical_grid_unspecified", 5, ["OWNERSHIP_REPLACEMENT_MISMATCH"], lambda packet: packet["replacements"].append({"table_symbol": inspect_baseline()["table_order"][1], "points": [{"direction_key": i, "x": 128, "y": 128} for i in range(1, 10)], "rationale": "canonical default", "source_reference": "none"}))

    fixture_cases = policy["negative_cases"]
    assert len(fixture_cases) == len(cases), (len(fixture_cases), len(cases))
    assert [case["case_id"] for case in fixture_cases] == [case_id for case_id, _, _, _ in cases]
    for fixture_case, (_, exit_code, codes, mutation) in zip(fixture_cases, cases):
        assert fixture_case["expected_exit_code"] == exit_code
        assert fixture_case["expected_blocker_codes"] == codes
        assert_review_case(fixture_case, mutation)
    assert [case["case_id"] for case in policy["precedence_cases"]] == PRECEDENCE_CASE_IDS
    assert [case["case_id"] for case in policy["protected_path_cases"]] == PROTECTED_PATH_CASE_IDS
    assert [case["case_id"] for case in policy["generator_error_cases"]] == GENERATOR_ERROR_CASE_IDS

    one = make_packet()
    emitted, artifact, manifest = emit_generator_input(one, operation="production_changeset")
    assert manifest["classification"] == "EXPLICIT_OWNED_TABLE_CHANGESET" and emitted["owned_tables"] == one["ownership"]["owned_tables"]
    POSITIVE += 1
    multi = make_packet(owned_count=2)
    emitted_multi, _, _ = emit_generator_input(multi, operation="production_changeset")
    assert emitted_multi["owned_tables"] == inspect_baseline()["table_order"][:2]
    POSITIVE += 1
    full = make_packet("full_replacement")
    emitted_full, _, manifest = emit_generator_input(full, operation="production_changeset")
    assert "owned_tables" not in emitted_full and manifest["changed_table_count"] == 28
    POSITIVE += 1
    equivalence = make_packet(operation="source_equivalence_proof", owned_count=0)
    _, _, manifest = emit_generator_input(equivalence, operation="source_equivalence_proof")
    assert manifest["classification"] == "NO_OP"
    POSITIVE += 1
    template = create_template()
    assert review_intake(template)["blockers"] and not template["replacements"]
    POSITIVE += 1
    assert json.dumps(review_intake(one), sort_keys=True) == json.dumps(review_intake(copy.deepcopy(one)), sort_keys=True)
    POSITIVE += 1

    permutation = make_packet(owned_count=2)
    permuted = copy.deepcopy(permutation)
    for key in ("owned_tables", "declarations"):
        permuted["ownership"][key].reverse()
    permuted["replacements"].reverse()
    first = emit_generator_input(permutation, operation="production_changeset")
    second = emit_generator_input(permuted, operation="production_changeset")
    assert first == second and json.dumps(first[0], indent=2, sort_keys=True) == json.dumps(second[0], indent=2, sort_keys=True)
    POSITIVE += 1

    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        # Every review-fixture negative also exercises the real validate CLI,
        # rather than treating a direct library report as sufficient coverage.
        for fixture_case, (_, exit_code, _, mutation) in zip(fixture_cases, cases):
            packet = make_packet()
            mutation(packet)
            input_path = temp / f"{fixture_case['case_id']}.json"
            input_path.write_text(json.dumps(packet), encoding="utf-8")
            completed = run_cli("validate", str(input_path))
            assert completed.returncode == exit_code, (fixture_case["case_id"], completed.returncode, completed.stderr)
            NEGATIVE += 1

        precedence = make_packet()
        precedence["baseline"]["semantic_digest"] = "stale"
        precedence["authority"]["status"] = "draft"
        precedence["ownership"]["owned_tables"] = []
        precedence_path = temp / "precedence.json"
        precedence_path.write_text(json.dumps(precedence), encoding="utf-8")
        report = review_intake(precedence)
        assert {"baseline_mismatch", "authority", "ownership"}.issubset({blocker["category"] for blocker in report["blockers"]})
        expected_precedence = policy["precedence_cases"][0]["expected_exit_code"]
        assert run_cli("validate", str(precedence_path)).returncode == expected_precedence
        blocked_output = temp / "precedence-generator-input.json"
        assert run_cli("emit-generator-input", str(precedence_path), "--output", str(blocked_output)).returncode == expected_precedence
        assert not blocked_output.exists()
        NEGATIVE += 1

        valid_path = temp / "valid.json"
        draft_path = temp / "draft.json"
        valid_path.write_text(json.dumps(make_packet()), encoding="utf-8")
        draft = make_packet()
        draft["authority"]["status"] = "draft"
        draft_path.write_text(json.dumps(draft), encoding="utf-8")
        completed = run_cli("validate", str(valid_path))
        assert completed.returncode == 0, (completed.returncode, completed.stderr)
        review_output = temp / "review.json"
        completed = run_cli("review", str(draft_path), "--output", str(review_output))
        assert completed.returncode == 0 and json.loads(review_output.read_text())["production_emission_allowed"] is False
        blocked_output = temp / "blocked-generator-input.json"
        completed = run_cli("emit-generator-input", str(draft_path), "--output", str(blocked_output))
        assert completed.returncode == 3 and not blocked_output.exists()
        emitted_output = temp / "generator-input.json"
        completed = run_cli("emit-generator-input", str(valid_path), "--output", str(emitted_output))
        assert completed.returncode == 0 and json.loads(emitted_output.read_text())["schema_version"] == 2
        POSITIVE += 3
        NEGATIVE += 2

        for case in policy["protected_path_cases"]:
            component = case.get("path_component")
            publication_name = case.get("publication_name")
            target = ROOT / component / "blocked.json" if component else temp / publication_name / "blocked.json"
            try:
                assert_safe_offline_output_path(target)
                raise AssertionError(f"protected path accepted: {case['case_id']}")
            except IntakeError:
                NEGATIVE += 1

        for case in policy["generator_error_cases"]:
            label, attribute, category = case["case_id"], case["attribute"], case["category"]
            command = case["command"]
            if command == "inspect-baseline": arguments = [command]
            elif command == "create-template": arguments = [command, "--output", str(temp / "template.json")]
            elif command == "review": arguments = [command, str(valid_path)]
            else: arguments = [command, str(valid_path), "--output", str(temp / "generator-error.json")]
            stderr = io.StringIO()
            patch_target = intake_cli if case["patch_module"] == "manager" else intake_module
            with patch.object(patch_target, attribute, side_effect=GeneratorModesError(f"{label} generator failure", category)), redirect_stderr(stderr):
                result = intake_cli.main(arguments)
            assert result == case["expected_exit_code"] == EXIT_CODES[category] and f"{label} generator failure" in stderr.getvalue() and "Traceback" not in stderr.getvalue()
            NEGATIVE += 1

    return POSITIVE, NEGATIVE


if __name__ == "__main__":
    try:
        positive, negative = run()
        print(json.dumps({"status": "PASS", "positive_tests": positive, "negative_tests": negative, "active_source_changed": False, "hardware_candidate_created": False}, sort_keys=True))
        raise SystemExit(0)
    except Exception as exc:
        print(f"error: {exc}")
        raise
