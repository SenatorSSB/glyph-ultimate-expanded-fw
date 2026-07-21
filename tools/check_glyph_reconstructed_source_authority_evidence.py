#!/usr/bin/env python3
"""Validate and render the reconstructed source-authority evidence packet.

This checker is deliberately not an authority source.  It checks that the
recorded evidence remains deterministic, source-backed, and conservative about
inferred mappings, approval, and failed candidates.  It never prepares,
installs, or writes active source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
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
CONVERTER_PATH = "tools/convert_coordinate_native_profile_to_source_owned_spec.py"
LAYOUT_SPEC_PATH = "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json"
ALLOWED_FEATURE_PATHS = {
    "docs/runtime_config/fixtures/reconstructed_source_authority_evidence.json",
    "docs/runtime_config/reconstructed_source_authority_evidence.md",
    "docs/runtime_config/intakes/current_source_owned_baseline_equivalence.intake.json",
    "tools/check_glyph_reconstructed_source_authority_evidence.py",
}

sys.path.insert(0, str(REPO_ROOT / "tools"))
from extract_glyph_identity_runtime_tables import load_source_tables  # noqa: E402
from source_owned_source_authority_intake import inspect_baseline, review_intake  # noqa: E402


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AssertionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: str | Path) -> dict[str, Any]:
    resolved = REPO_ROOT / path if isinstance(path, str) else path
    value = json.loads(resolved.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return value


def canonical_json(matrix: dict[str, Any]) -> str:
    return json.dumps(matrix, indent=2, sort_keys=True) + "\n"


def semantic_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def contains_value(value: Any, needle: str) -> bool:
    if isinstance(value, dict):
        return any(contains_value(key, needle) or contains_value(item, needle) for key, item in value.items())
    if isinstance(value, list):
        return any(contains_value(item, needle) for item in value)
    return value == needle


def converter_analysis() -> dict[str, Any]:
    """Run the real offline converter in a temporary directory on every check."""
    with tempfile.TemporaryDirectory(prefix="glyph-reconstructed-evidence-") as directory:
        output = Path(directory) / "converted-layout-spec.json"
        command = [sys.executable, CONVERTER_PATH, "--profile", Y2_PROFILE_PATH, "--output", str(output)]
        result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
        accepted = result.returncode == 0 and output.exists()
        if not accepted:
            raise AssertionError(f"converter probe failed: exit={result.returncode}; stderr={result.stderr.strip()}")
        converted = read_json(output)
        checked_in = read_json(LAYOUT_SPEC_PATH)
        output_bytes = output.read_bytes()
        checked_in_bytes = (REPO_ROOT / LAYOUT_SPEC_PATH).read_bytes()
    direct_symbols = any(isinstance(table, dict) and "table_symbol" in table for table in converted.get("tables", []))
    production_claim_keys = {"ownership", "owner", "provenance", "production_authorized", "approval"}
    claims_production_ownership_or_provenance = any(key in converted for key in production_claim_keys)
    return {
        "command": ["python3", CONVERTER_PATH, "--profile", Y2_PROFILE_PATH, "--output", "<temporary-output>"],
        "exit_status": result.returncode,
        "accepted_input": accepted,
        "output_semantic_digest": semantic_digest(converted),
        "output_equals_current_layout_spec": converted == checked_in and output_bytes == checked_in_bytes,
        "abstract_y2_ids_preserved": contains_value(converted, "y2_primary") or contains_value(converted, "y2_tilt"),
        "direct_source_owned_table_symbol_mappings": direct_symbols,
        "creates_production_ownership_or_provenance_claims": claims_production_ownership_or_provenance,
    }


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
            "comparison_status": "COMPLETE_MATCH",
            "differs_from_current_baseline": False,
            "mapping_status": "EXPLICIT",
            "ownership_status": "PARTIAL",
            "approval_status": "PARTIAL",
            "production_intake_eligibility": "SOURCE_EQUIVALENCE_ONLY",
            "blockers": ["the empty source-equivalence proof remains submitted for human approval; it is not approved or emittable"],
        },
        {
            "candidate_id": "coordinate_native_y2_inspired_sketch",
            "candidate_kind": "coordinate_native_fixture",
            "source_paths": [Y2_PROFILE_PATH, "tools/convert_coordinate_native_profile_to_source_owned_spec.py"],
            "hardware_status": "NOT_TESTED",
            "active_status": "inactive_design_only",
            "comparison_status": "SUBSET_MATCH_ONLY",
            "differs_from_current_baseline": None,
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
            "comparison_status": "COMPLETE_MATCH",
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
            "comparison_status": "COMPLETE_DIFFERENCE",
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
            "comparison_status": "NOT_APPLICABLE",
            "differs_from_current_baseline": None,
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
        "converter_analysis": {"fixture": Y2_PROFILE_PATH, "output": LAYOUT_SPEC_PATH, **converter_analysis()},
        "authority_analysis": {
            "hardware_acceptance_record": Y2_RESULT_PATH,
            "merge_approved_recorded": True,
            "approver_identifier_present": False,
            "production_authorized_target_present": False,
            "required_human_action": {
                "decision": "APPROVE_OR_REJECT_SOURCE_EQUIVALENCE_PROOF",
                "fields_if_approved": ["authority.status", "authority.approver", "authority.statement", "authority.approval_reference"],
            },
            "minimal_missing_decision": "A human must explicitly approve or reject the empty source-equivalence proof. Only if approved may authority.status become approved, authority.approver receive the exact human-approved identifier, authority.statement become affirmative, and authority.approval_reference be confirmed or replaced. A production change additionally needs explicit target intent, owned symbols, exact replacements, ownership references, and production-authorized provenance.",
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
        "7. The source-equivalence packet is submitted for review and cannot be emitted. The required action is an explicit human approval-or-rejection decision, not merely supplying an identifier.",
        "8. No production changeset or production generator-input can be emitted.",
        "9. If a human approves the empty equivalence proof, they must set `authority.status` to `approved`, provide the exact approved `authority.approver`, replace `authority.statement` with an affirmative statement, and explicitly confirm or replace `authority.approval_reference`. A production delta additionally needs explicit target intent, owned symbols, exact replacements, ownership references, and production-authorized approval.",
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
        "- This is `SUBSET_MATCH_ONLY`, not a complete no-op. Equality is supporting evidence only. The sketch contains no `table_symbol`; the converter emits the current canonical layout-spec fixture with table symbols, but does not derive a source mapping from those abstract IDs.",
        "- The Y2 hardware result is source-owned firmware evidence; it does not prove the coordinate-native fixture’s identity or authorize a production replacement.",
        "",
        "## Failed-candidate exclusion",
        "",
        f"The canonical-grid candidate at `{FAILED_COMMIT}` remains `FORBIDDEN_FAILED_CANDIDATE` after `HARDWARE_FAIL`. Its canonical 0/128/255 content is not used as ownership, mapping, replacement, or hardware evidence in this packet. No production artifact is emitted.",
        "",
        "## Source-equivalence packet",
        "",
        f"`{rel(INTAKE_PATH)}` is `submitted_for_review`, `overlay_preserve`, `source_equivalence_proof`, `source_baseline_derived`, with empty `owned_tables`, `declarations`, and `replacements`. Validation is blocked by `NOT_APPROVED`: a human must explicitly approve or reject before the approval fields can be updated. No generator-input v2 file is produced.",
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
    return "\n".join(lines).rstrip("\n") + "\n"


def git_output(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.strip()


def referenced_paths(matrix: dict[str, Any]) -> list[str]:
    paths = [path for values in matrix["evidence_inventory"].values() if isinstance(values, list) for path in values if isinstance(path, str) and not len(path) == 40]
    for candidate in matrix["profile_candidates"]:
        if candidate["mapping_status"] == "EXPLICIT" and not candidate["source_paths"]:
            raise AssertionError(f"explicit candidate mapping lacks direct source evidence: {candidate['candidate_id']}")
        paths.extend(candidate["source_paths"])
    for item in matrix["table_evidence"]:
        paths.append(item["exact_points_source"])
        for record in item["mapping_evidence"]:
            paths.append(record["path"])
        for record in item["hardware_evidence"]:
            paths.append(record if isinstance(record, str) else record["path"])
    return paths


def validate_references(matrix: dict[str, Any]) -> None:
    for path in referenced_paths(matrix):
        if not (REPO_ROOT / path).is_file():
            raise AssertionError(f"missing cited repository path: {path}")
    for commit in matrix["evidence_inventory"]["lineage_commits"]:
        if subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=REPO_ROOT).returncode:
            raise AssertionError(f"missing cited lineage commit: {commit}")
    for item in matrix["table_evidence"]:
        for record in item["mapping_evidence"]:
            lines = (REPO_ROOT / record["path"]).read_text(encoding="utf-8").splitlines()
            if not 0 < record["line"] <= len(lines) or record["needle"] not in lines[record["line"] - 1]:
                raise AssertionError(f"stale mapping evidence: {record}")
        for record in item["hardware_evidence"]:
            if isinstance(record, dict) and not record.get("claim"):
                raise AssertionError(f"hardware evidence lacks claim: {item['abstract_table_id']}")
        if item["mapping_status"] == "EXPLICIT" and not item["mapping_evidence"]:
            raise AssertionError(f"explicit mapping lacks direct evidence: {item['abstract_table_id']}")
        if item["abstract_table_id"] in {"y2_primary", "y2_tilt"}:
            if item["mapping_status"] != "INFERRED_ONLY" or item["ownership_status"] != "NONE":
                raise AssertionError("coordinate-native Y2 IDs must remain inferred and unowned")


def changed_paths(args: list[str]) -> set[str]:
    return {path for path in git_output(*args).splitlines() if path}


def validate_branch_safety() -> None:
    branch = git_output("branch", "--show-current")
    protected_prefixes = ("src/", "include/", "HAL/", "hal/", "backend/", "lib/", "active/", "storage/")
    uncommitted = changed_paths(["diff", "--name-only"])
    staged = changed_paths(["diff", "--cached", "--name-only"])
    all_changed = uncommitted | staged
    if any(path.startswith(protected_prefixes) for path in all_changed):
        raise AssertionError(f"protected source/publication path changed in worktree: {sorted(all_changed)}")
    if branch == "runtime-config-reconstruct-source-authority-evidence":
        if subprocess.run(["git", "merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD"], cwd=REPO_ROOT).returncode:
            raise AssertionError("pinned configurator baseline is not an ancestor")
        merge_base = git_output("merge-base", "HEAD", "origin/configurator")
        if merge_base != BASELINE_COMMIT:
            raise AssertionError(f"unexpected feature merge base: {merge_base}")
        committed = changed_paths(["diff", "--name-only", f"{merge_base}..HEAD"])
        if any(path.startswith(protected_prefixes) for path in committed):
            raise AssertionError(f"protected source/publication path committed on feature branch: {sorted(committed)}")
        unexpected = committed - ALLOWED_FEATURE_PATHS
        if unexpected:
            raise AssertionError(f"feature branch changed paths outside explicit allowlist: {sorted(unexpected)}")


def probe_intake_cli() -> None:
    command = [sys.executable, "tools/manage_source_owned_source_authority_intake.py"]
    validate = subprocess.run(command + ["validate", str(INTAKE_PATH)], cwd=REPO_ROOT, text=True, capture_output=True)
    if validate.returncode != 3 or "NOT_APPROVED" not in validate.stdout or "source_equivalence_emission_allowed\": false" not in validate.stdout:
        raise AssertionError(f"intake validate probe drifted: exit={validate.returncode}; output={validate.stdout}{validate.stderr}")
    with tempfile.TemporaryDirectory(prefix="glyph-intake-probe-") as directory:
        output = Path(directory) / "must-not-exist.generator-input.json"
        emit = subprocess.run(command + ["prove-source-equivalence", str(INTAKE_PATH), "--output", str(output)], cwd=REPO_ROOT, text=True, capture_output=True)
        if emit.returncode != 3 or output.exists() or "Traceback" in emit.stdout + emit.stderr:
            raise AssertionError(f"intake emission probe drifted: exit={emit.returncode}; output={emit.stdout}{emit.stderr}")


def validate_matrix(matrix: dict[str, Any]) -> None:
    actual = inspect_baseline()
    current = matrix["current_baseline"]
    for key in ("baseline_id", "semantic_digest", "table_count", "table_order", "table_order_digest", "source_path", "source_interpreter"):
        if current[key] != actual[key]:
            raise AssertionError(f"current baseline mismatch for {key}")
    if current["table_count"] != 28 or len(current["table_order"]) != 28:
        raise AssertionError("current baseline must contain exactly 28 ordered tables")
    validate_references(matrix)
    baseline_candidate = next(item for item in matrix["profile_candidates"] if item["candidate_id"] == "current_source_owned_baseline")
    if baseline_candidate["production_intake_eligibility"] != "SOURCE_EQUIVALENCE_ONLY" or baseline_candidate["comparison_status"] != "COMPLETE_MATCH" or baseline_candidate["differs_from_current_baseline"]:
        raise AssertionError("current baseline is not a production changeset")
    y2 = next(item for item in matrix["profile_candidates"] if item["candidate_id"] == "coordinate_native_y2_inspired_sketch")
    if y2["comparison_status"] != "SUBSET_MATCH_ONLY" or y2["differs_from_current_baseline"] is not None:
        raise AssertionError("incomplete Y2 sketch must not be classified as a complete baseline match")
    converter = matrix["converter_analysis"]
    if converter["exit_status"] != 0 or not converter["accepted_input"] or not converter["output_equals_current_layout_spec"] or converter["abstract_y2_ids_preserved"] or not converter["direct_source_owned_table_symbol_mappings"] or converter["creates_production_ownership_or_provenance_claims"]:
        raise AssertionError("converter evidence drifted")
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
    if matrix["authority_analysis"]["required_human_action"]["decision"] != "APPROVE_OR_REJECT_SOURCE_EQUIVALENCE_PROOF":
        raise AssertionError("approval action must require a human decision")
    if FAILED_COMMIT in json.dumps(intake):
        raise AssertionError("failed candidate provenance leaked into the equivalence intake")
    for generated_path in (REPO_ROOT / "docs/runtime_config/intakes").glob("*.generator-input.json"):
        if FAILED_COMMIT in generated_path.read_text(encoding="utf-8"):
            raise AssertionError(f"failed candidate provenance leaked into generated input: {generated_path}")
    probe_intake_cli()
    validate_branch_safety()
    print("glyph_reconstructed_source_authority_evidence: PASS")
    print(f"baseline_semantic_digest={actual['semantic_digest']}")
    print("production_delta=NONE_AUTHORIZED")
    print("source_equivalence=SUBMITTED_FOR_REVIEW_NOT_EMITTED")


def validate_committed_artifacts(expected: dict[str, Any], matrix_path: Path = MATRIX_PATH, markdown_path: Path = MARKDOWN_PATH) -> None:
    """Require both derived artifacts to be exact deterministic reconstructions."""
    committed = read_json(matrix_path)
    if committed != expected:
        raise AssertionError(f"committed matrix drift: {matrix_path} differs from deterministic reconstruction")
    if matrix_path.read_text(encoding="utf-8") != canonical_json(expected):
        raise AssertionError(f"committed matrix formatting drift: {matrix_path} is not canonical JSON")
    expected_markdown = render_markdown(expected)
    if markdown_path.read_text(encoding="utf-8") != expected_markdown:
        raise AssertionError(f"committed Markdown drift: {markdown_path} differs from deterministic rendering")


def run_drift_self_tests(expected: dict[str, Any]) -> None:
    """Regression tests: copied JSON or Markdown drift must fail validation."""
    with tempfile.TemporaryDirectory(prefix="glyph-evidence-drift-") as directory:
        matrix_copy = Path(directory) / "matrix.json"
        markdown_copy = Path(directory) / "report.md"
        matrix_copy.write_text(canonical_json(expected).replace('"schema_version": 1', '"schema_version": 2', 1), encoding="utf-8")
        markdown_copy.write_text(render_markdown(expected), encoding="utf-8")
        try:
            validate_committed_artifacts(expected, matrix_copy, markdown_copy)
        except AssertionError as exc:
            if "matrix drift" not in str(exc):
                raise
        else:
            raise AssertionError("matrix drift self-test unexpectedly passed")
        matrix_copy.write_text(canonical_json(expected), encoding="utf-8")
        markdown_copy.write_text(render_markdown(expected) + "drift\n", encoding="utf-8")
        try:
            validate_committed_artifacts(expected, matrix_copy, markdown_copy)
        except AssertionError as exc:
            if "Markdown drift" not in str(exc):
                raise
        else:
            raise AssertionError("Markdown drift self-test unexpectedly passed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-artifacts", action="store_true")
    args = parser.parse_args()
    matrix = build_matrix()
    if args.write_artifacts:
        MATRIX_PATH.write_text(canonical_json(matrix), encoding="utf-8")
        MARKDOWN_PATH.write_text(render_markdown(matrix), encoding="utf-8")
        validate_committed_artifacts(matrix)
        print(f"wrote={rel(MATRIX_PATH)}")
        print(f"wrote={rel(MARKDOWN_PATH)}")
    validate_committed_artifacts(matrix)
    run_drift_self_tests(matrix)
    validate_matrix(matrix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
