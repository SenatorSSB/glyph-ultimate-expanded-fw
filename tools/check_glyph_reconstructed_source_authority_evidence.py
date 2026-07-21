#!/usr/bin/env python3
"""Validate and render the reconstructed source-authority evidence packet.

This checker is deliberately not an authority source.  It checks that the
recorded evidence remains deterministic, source-backed, and conservative about
inferred mappings, approval, and failed candidates.  It never prepares,
installs, or writes active source.
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "7fde661303dd836918b4c54008a47b89c478fc09"
MATRIX_PATH = REPO_ROOT / "docs/runtime_config/fixtures/reconstructed_source_authority_evidence.json"
MARKDOWN_PATH = REPO_ROOT / "docs/runtime_config/reconstructed_source_authority_evidence.md"
INTAKE_PATH = REPO_ROOT / "docs/runtime_config/intakes/current_source_owned_baseline_equivalence.intake.json"
INTERPRETER_PATH = "src/modes/UltimateRuntimeConfigInterpreter.hpp"
TABLE_SOURCE_PATH = "src/modes/UltimateIdentityRuntimeTables.hpp"
BASELINE_HEADER_PATH = "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
Y2_PROFILE_PATH = "docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json"
Y2_RESULT_PATH = "docs/calibration/latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md"
FAILED_RESULT_PATH = "docs/calibration/generated_canonical_grid_candidate_hardware_result_2026-07-19.md"
FAILED_COMMIT = "e643017c1577c9ca2b94581fa6f18c0dfb1bac9b"

sys.path.insert(0, str(REPO_ROOT / "tools"))
from extract_glyph_identity_runtime_tables import load_source_tables  # noqa: E402
from source_owned_source_authority_intake import inspect_baseline, review_intake  # noqa: E402


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def read_json(path: str | Path) -> dict[str, Any]:
    value = json.loads((REPO_ROOT / path if isinstance(path, str) else path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return value


def line_for(path: str, needle: str) -> int:
    lines = (REPO_ROOT / path).read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, 1):
        if needle in line:
            return number
    raise AssertionError(f"{needle!r} not found in {path}")


def evidence(path: str, needle: str, kind: str) -> dict[str, Any]:
    return {"path": path, "line": line_for(path, needle), "needle": needle, "kind": kind}


def points_for_profile_table(table: dict[str, Any]) -> list[list[int]]:
    return [[point["x"], point["y"]] for point in sorted(table["direction_points"], key=lambda item: item["direction_key"])]


def build_matrix() -> dict[str, Any]:
    baseline = inspect_baseline()
    source_tables = load_source_tables()
    y2_profile = read_json(Y2_PROFILE_PATH)
    y2_matches: dict[str, list[str]] = {}
    for table in y2_profile["modifier_tables"]:
        points = points_for_profile_table(table)
        y2_matches[table["table_id"]] = [name for name, values in source_tables.items() if points == [list(point) for point in values]]

    table_evidence: list[dict[str, Any]] = []
    for item in baseline["table_inventory"]:
        symbol = item["table_symbol"]
        name = symbol.removeprefix("k").removesuffix("Table")
        direct_needle = f'{{RuntimeTableId::{name}, "{symbol}",'
        table_evidence.append(
            {
                "abstract_table_id": f"RuntimeTableId::{name}",
                "source_owned_table_symbol": symbol,
                "mapping_evidence": [evidence(INTERPRETER_PATH, direct_needle, "direct_runtime_table_view_mapping")],
                "mapping_status": "EXPLICIT",
                "exact_points_source": BASELINE_HEADER_PATH,
                "matches_current_baseline": True,
                "hardware_evidence": [Y2_RESULT_PATH] if symbol in {"kY2Table", "kTilt3Table"} else [],
                "ownership_evidence": [],
                "ownership_status": "NONE",
            }
        )

    for abstract_id, symbol in (("y2_primary", None), ("y2_tilt", None)):
        table_evidence.append(
            {
                "abstract_table_id": abstract_id,
                "source_owned_table_symbol": symbol,
                "mapping_evidence": [],
                "mapping_status": "INFERRED_ONLY",
                "exact_points_source": Y2_PROFILE_PATH,
                "matches_current_baseline": True,
                "matching_source_owned_tables": y2_matches[abstract_id],
                "hardware_evidence": [
                    {"path": Y2_RESULT_PATH, "claim": "source-inspired hardware result; not proof of coordinate-native fixture identity"}
                ],
                "ownership_evidence": [],
                "ownership_status": "NONE",
            }
        )

    candidates = [
        {
            "candidate_id": "current_source_owned_baseline",
            "candidate_kind": "current_baseline",
            "source_paths": [TABLE_SOURCE_PATH, INTERPRETER_PATH, BASELINE_HEADER_PATH, Y2_RESULT_PATH],
            "hardware_status": "HARDWARE_PASS",
            "active_status": "current",
            "differs_from_current_baseline": False,
            "mapping_status": "EXPLICIT",
            "ownership_status": "PARTIAL",
            "approval_status": "PARTIAL",
            "production_intake_eligibility": "SOURCE_EQUIVALENCE_ONLY",
            "blockers": ["merge_approved=true is recorded, but no intake-contract approver identifier is recorded"],
        },
        {
            "candidate_id": "coordinate_native_y2_inspired_sketch",
            "candidate_kind": "coordinate_native_fixture",
            "source_paths": [Y2_PROFILE_PATH, "tools/convert_coordinate_native_profile_to_source_owned_spec.py"],
            "hardware_status": "NOT_TESTED",
            "active_status": "inactive_design_only",
            "differs_from_current_baseline": False,
            "mapping_status": "INFERRED_ONLY",
            "ownership_status": "NONE",
            "approval_status": "NONE",
            "production_intake_eligibility": "BLOCKED",
            "blockers": [
                "y2_primary and y2_tilt are illustrative IDs with no direct source-symbol mapping",
                "fixture is design_only_contract=true and inactive",
                "coordinate equality cannot establish ownership or approval",
                "fixture covers two tables, not a complete production target",
            ],
        },
        {
            "candidate_id": "alternative_b_source_aligned_alias",
            "candidate_kind": "historical_candidate",
            "source_paths": ["docs/calibration/alt_b_generated_table_alias_candidate_hardware_result_2026-07-09.md", "docs/runtime_config/source_owned_table_symbol_map.md"],
            "hardware_status": "HARDWARE_PASS",
            "active_status": "historical",
            "differs_from_current_baseline": False,
            "mapping_status": "EXPLICIT",
            "ownership_status": "PARTIAL",
            "approval_status": "PARTIAL",
            "production_intake_eligibility": "SOURCE_EQUIVALENCE_ONLY",
            "blockers": ["historical source-aligned alias evidence is not a distinct production target"],
        },
        {
            "candidate_id": "generated_canonical_grid_candidate",
            "candidate_kind": "failed_candidate",
            "source_paths": ["docs/runtime_config/fixtures/generated_source_owned_layout_spec.json", FAILED_RESULT_PATH, "docs/runtime_config/generated_source_owned_overlay_preserve_proof_2026-07-19.md"],
            "hardware_status": "HARDWARE_FAIL",
            "active_status": "failed_unmerged",
            "differs_from_current_baseline": True,
            "mapping_status": "EXPLICIT",
            "ownership_status": "NONE",
            "approval_status": "NONE",
            "production_intake_eligibility": "BLOCKED",
            "classification": "FORBIDDEN_FAILED_CANDIDATE",
            "blockers": [
                f"hardware failure recorded for commit {FAILED_COMMIT}",
                "26 non-aligned tables are canonical 0/128/255 grids",
                "failed candidate must never be promoted or used as a replacement source",
            ],
        },
        {
            "candidate_id": "coordinate_native_design_fixture_corpus",
            "candidate_kind": "coordinate_native_fixture",
            "source_paths": sorted(str(path.relative_to(REPO_ROOT)) for path in (REPO_ROOT / "docs/runtime_config/fixtures").glob("coordinate_native_runtime_profile*.json")),
            "hardware_status": "NOT_APPLICABLE",
            "active_status": "inactive_design_only",
            "differs_from_current_baseline": False,
            "mapping_status": "NONE",
            "ownership_status": "NONE",
            "approval_status": "NONE",
            "production_intake_eligibility": "BLOCKED",
            "blockers": ["contract, positive, negative, and dry-run fixtures are design/test corpus, not production-authorized targets"],
        },
    ]

    return {
        "schema_version": 1,
        "reconstruction_status": "NO_DISTINCT_AUTHORIZED_PRODUCTION_DELTA_FOUND",
        "current_baseline": {
            "commit": BASELINE_COMMIT,
            "baseline_id": baseline["baseline_id"],
            "semantic_digest": baseline["semantic_digest"],
            "table_count": baseline["table_count"],
            "table_order": baseline["table_order"],
            "table_order_digest": baseline["table_order_digest"],
            "source_path": baseline["source_path"],
            "source_interpreter": baseline["source_interpreter"],
        },
        "profile_candidates": candidates,
        "table_evidence": table_evidence,
        "converter_analysis": {
            "fixture": Y2_PROFILE_PATH,
            "accepted_input": True,
            "output": "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json",
            "output_is_current_layout_spec": True,
            "abstract_y2_ids_preserved": False,
            "production_mapping_provided": False,
        },
        "authority_analysis": {
            "hardware_acceptance_record": Y2_RESULT_PATH,
            "merge_approved_recorded": True,
            "approver_identifier_present": False,
            "production_authorized_target_present": False,
            "minimal_missing_decision": "Provide an intake-contract approver identifier and approval reference for the empty source-equivalence proof; for production change, also provide explicit target intent, owned symbols, exact replacements, ownership references, and production-authorized provenance.",
        },
        "failed_candidate_exclusion": {
            "commit": FAILED_COMMIT,
            "classification": "FORBIDDEN_FAILED_CANDIDATE",
            "hardware_status": "HARDWARE_FAIL",
            "allowed_in_production_artifacts": False,
        },
        "evidence_inventory": {
            "active_source": [TABLE_SOURCE_PATH, INTERPRETER_PATH, BASELINE_HEADER_PATH],
            "canonical_extraction": ["tools/extract_glyph_identity_runtime_tables.py", "tools/generate_source_owned_runtime_config.py", "tools/source_owned_generator_modes.py"],
            "authority_workflow": ["tools/source_owned_source_authority_intake.py", "tools/manage_source_owned_source_authority_intake.py", "tools/check_glyph_source_owned_source_authority_intake.py", "docs/runtime_config/source_authority_intake_workflow.md"],
            "profile_and_bridge": ["docs/runtime_config/coordinate_native_runtime_profile_contract.md", Y2_PROFILE_PATH, "docs/runtime_config/fixtures/coordinate_native_runtime_profile_source_owned_layout_spec_bridge.example.json", "tools/convert_coordinate_native_profile_to_source_owned_spec.py"],
            "generated_and_failed": ["docs/runtime_config/fixtures/generated_source_owned_layout_spec.json", "docs/runtime_config/fixtures/generated_outputs/generated_source_owned_runtime_config.example.hpp", FAILED_RESULT_PATH],
            "hardware_and_lineage": [Y2_RESULT_PATH, "docs/calibration/alt_b_generated_table_alias_candidate_hardware_result_2026-07-09.md", "docs/runtime_config/latest_y2_layout_source_owned_port.md"],
            "current_docs": ["docs/AGENT_CONTEXT.md", "docs/CURRENT_STATE.md", "docs/ROADMAP.md", "docs/runtime_config/README.md", "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md", "docs/runtime_config/source_owned_table_symbol_map.md"],
            "lineage_commits": ["9842724b12b92988acfd7ed870512e055d79e3b5", "2fc0ce3d5149565b3b52202cb234e359e8c84b28", "83c8dba989605f7d0cf591858ffa336ab10dea61", "5d6d0f3ca215584915b93dbf9e8836468cc17b94", "4924f7bd6a946d14ff9a68d5cbdc76a550b7b1e2"],
        },
    }


def render_markdown(matrix: dict[str, Any]) -> str:
    baseline = matrix["current_baseline"]
    lines = [
        "# Reconstructed source-authority evidence",
        "",
        "Status: `NO_DISTINCT_AUTHORIZED_PRODUCTION_DELTA_FOUND`.",
        "",
        "This packet reconstructs repository evidence only. It does not create source authority, prepare or install a candidate, modify active source, build firmware, or claim hardware correctness for an untested delta.",
        "",
        "## Current baseline",
        "",
        f"- Starting configurator commit: `{baseline['commit']}`.",
        f"- Baseline: `{baseline['baseline_id']}`.",
        f"- Semantic digest: `{baseline['semantic_digest']}`.",
        f"- Table count/order: `{baseline['table_count']}` / `{baseline['table_order_digest']}`.",
        f"- Source: `{baseline['source_path']}`; interpreter: `{baseline['source_interpreter']}`.",
        "- Interpretation: the current source-owned 28-table firmware profile, whose Y2/Tilt3 source state is covered by the recorded latest-Y2 HARDWARE_PASS. Hardware acceptance is evidence for the current source state, not automatic authority for future replacements.",
        "",
        "## Direct answers",
        "",
        "1. The current production profile is the source-owned 28-table baseline identified above.",
        "2. Coordinate-native contract, bridge, positive, negative, and dry-run fixtures are inactive design/test artifacts. The Y2-inspired sketch is illustrative only.",
        "3. Firmware `RuntimeTableId::<name>` to `k<Name>Table` mappings are explicit in `src/modes/UltimateRuntimeConfigInterpreter.hpp`; the matrix records direct line evidence for all 28.",
        "4. `y2_primary -> kY2Table` and `y2_tilt -> kTilt3Table` remain inferred-only from coordinate equality and source inspiration. No direct repository record connects those abstract IDs to symbols.",
        "5. No complete repository-resident target with production intent and an authorized semantic delta was found.",
        "6. No distinct target is production-authorized. The recorded `merge_approved: true` applies to the hardware-passed current source-owned port and is not an intake approver identity.",
        "7. A source-equivalence packet can be prepared as submitted-for-review; it cannot be emitted until a human supplies an intake-contract approver identifier.",
        "8. No production changeset or production generator-input can be emitted.",
        "9. Smallest user decision: confirm the approver identifier/approval reference for the empty equivalence proof; a production delta additionally needs explicit target intent, owned symbols, exact replacements, ownership references, and production-authorized approval.",
        "",
        "## Candidate decisions",
        "",
        "| Candidate | Status | Eligibility | Reason |",
        "| --- | --- | --- | --- |",
    ]
    for candidate in matrix["profile_candidates"]:
        lines.append(f"| `{candidate['candidate_id']}` | `{candidate['active_status']}` / `{candidate['hardware_status']}` | `{candidate['production_intake_eligibility']}` | {candidate['blockers'][0]} |")
    lines += [
        "",
        "## Y2 equality and mapping boundary",
        "",
        "- `y2_primary` exactly matches the current `Y2` table points and therefore has one equality match: `Y2` / `kY2Table`.",
        "- `y2_tilt` exactly matches the current `Tilt3` table points and therefore has one equality match: `Tilt3` / `kTilt3Table`.",
        "- Equality is supporting evidence only. The sketch contains no `table_symbol`, and the converter returns the existing layout-spec fixture rather than preserving those abstract IDs as source mappings.",
        "- The Y2 hardware result is source-owned firmware evidence; it does not prove the coordinate-native fixture’s identity or authorize a production replacement.",
        "",
        "## Failed-candidate exclusion",
        "",
        f"The canonical-grid candidate at `{FAILED_COMMIT}` remains `FORBIDDEN_FAILED_CANDIDATE` after `HARDWARE_FAIL`. Its canonical 0/128/255 content is not used as ownership, mapping, replacement, or hardware evidence in this packet. No production artifact is emitted.",
        "",
        "## Source-equivalence packet",
        "",
        f"`{rel(INTAKE_PATH)}` is `submitted_for_review`, `overlay_preserve`, `source_equivalence_proof`, `source_baseline_derived`, with empty `owned_tables`, `declarations`, and `replacements`. Validation is expected to block only approval/emission because `authority.approver` remains intentionally unresolved; no generator-input v2 file is produced.",
        "",
        "## Evidence inventory",
        "",
    ]
    for category, paths in matrix["evidence_inventory"].items():
        lines.append(f"### {category}")
        lines.append("")
        for path in paths:
            lines.append(f"- `{path}`")
        lines.append("")
    return "\n".join(lines)


def validate_matrix(matrix: dict[str, Any]) -> None:
    actual = inspect_baseline()
    current = matrix["current_baseline"]
    for key in ("baseline_id", "semantic_digest", "table_count", "table_order", "table_order_digest", "source_path", "source_interpreter"):
        if current[key] != actual[key]:
            raise AssertionError(f"current baseline mismatch for {key}")
    if current["table_count"] != 28 or len(current["table_order"]) != 28:
        raise AssertionError("current baseline must contain exactly 28 ordered tables")
    for candidate in matrix["profile_candidates"]:
        for path in candidate["source_paths"]:
            if path.startswith("docs/") or path.startswith("src/") or path.startswith("tools/"):
                if not (REPO_ROOT / path).exists():
                    raise AssertionError(f"missing cited repository path: {path}")
    for item in matrix["table_evidence"]:
        for record in item["mapping_evidence"]:
            if record["kind"] == "direct_runtime_table_view_mapping":
                line = (REPO_ROOT / record["path"]).read_text(encoding="utf-8").splitlines()[record["line"] - 1]
                if record["needle"] not in line:
                    raise AssertionError(f"stale direct mapping evidence: {record}")
        if item["mapping_status"] == "EXPLICIT" and not item["mapping_evidence"]:
            raise AssertionError(f"explicit mapping lacks direct evidence: {item['abstract_table_id']}")
        if item["abstract_table_id"] in {"y2_primary", "y2_tilt"} and item["mapping_status"] != "INFERRED_ONLY":
            raise AssertionError("coordinate-native Y2 IDs must not be promoted to explicit mappings")
    baseline_candidate = next(item for item in matrix["profile_candidates"] if item["candidate_id"] == "current_source_owned_baseline")
    if baseline_candidate["production_intake_eligibility"] != "SOURCE_EQUIVALENCE_ONLY" or baseline_candidate["differs_from_current_baseline"]:
        raise AssertionError("current baseline is not a production changeset")
    failed = matrix["failed_candidate_exclusion"]
    if failed["classification"] != "FORBIDDEN_FAILED_CANDIDATE" or failed["allowed_in_production_artifacts"]:
        raise AssertionError("failed canonical-grid candidate was not excluded")
    intake = read_json(INTAKE_PATH)
    if intake["authority"]["status"] != "submitted_for_review":
        raise AssertionError("equivalence intake must remain submitted_for_review")
    if intake["intent"] != {"provenance_class": "source_baseline_derived", "generation_mode": "overlay_preserve", "requested_operation": "source_equivalence_proof", "controller_scope": "Glyph Mk6", "source_owned_runtime_tables": True}:
        raise AssertionError("equivalence intake scope drifted")
    if intake["ownership"]["owned_tables"] or intake["ownership"]["declarations"] or intake["replacements"]:
        raise AssertionError("equivalence intake must be an empty overlay")
    report = review_intake(intake)
    if report["source_equivalence_emission_allowed"] or not any(blocker["code"] == "NOT_APPROVED" for blocker in report["blockers"]):
        raise AssertionError("submitted equivalence intake must not emit")
    if FAILED_COMMIT in json.dumps(intake):
        raise AssertionError("failed candidate provenance leaked into the equivalence intake")
    for generated_path in (REPO_ROOT / "docs/runtime_config/intakes").glob("*.generator-input.json"):
        if FAILED_COMMIT in generated_path.read_text(encoding="utf-8"):
            raise AssertionError(f"failed candidate provenance leaked into generated input: {generated_path}")
    changed = subprocess.run(["git", "diff", "--name-only", "--", "src"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.strip()
    if changed:
        raise AssertionError(f"src changed unexpectedly: {changed}")
    print("glyph_reconstructed_source_authority_evidence: PASS")
    print(f"baseline_semantic_digest={actual['semantic_digest']}")
    print("production_delta=NONE_AUTHORIZED")
    print("source_equivalence=SUBMITTED_FOR_REVIEW_NOT_EMITTED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-artifacts", action="store_true")
    args = parser.parse_args()
    matrix = build_matrix()
    validate_matrix(matrix)
    if args.write_artifacts:
        MATRIX_PATH.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        MARKDOWN_PATH.write_text(render_markdown(matrix), encoding="utf-8")
        print(f"wrote={rel(MATRIX_PATH)}")
        print(f"wrote={rel(MARKDOWN_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
