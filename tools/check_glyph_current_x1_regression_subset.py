#!/usr/bin/env python3
"""Check the narrow current, source-backed X1 regression correspondence."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from extract_glyph_identity_runtime_tables import load_source_tables, load_source_text_with_generated_tables

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/current_x1_regression_subset.json"
EVIDENCE = ROOT / "docs/calibration/fixtures/x1_offset41_hardware_evidence_2026-09-02.json"
RUNTIME = ROOT / "src/modes/Ultimate.cpp"
DOC = ROOT / "docs/runtime_config/current_x1_regression_subset.md"


class CheckError(AssertionError):
    pass


def fail(message: str) -> None:
    raise CheckError(message)


def exact(value: Any, expected: Any, label: str) -> None:
    if value != expected:
        fail(f"{label} mismatch: {value!r} != {expected!r}")


def load_object(path: Path) -> dict[str, Any]:
    seen: list[str] = []

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                seen.append(key)
            result[key] = value
        return result

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON {path}: {exc}")
    if seen:
        fail(f"duplicate JSON keys in {path}: {sorted(set(seen))}")
    if not isinstance(value, dict):
        fail(f"JSON root is not an object: {path}")
    return value


def keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        fail(f"{label} keys mismatch: {sorted(value)}")


def block(text: str, signature: str) -> str:
    source = re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.DOTALL)
    if source.count(signature) != 1:
        fail(f"expected one source definition: {signature}")
    start = source.find(signature)
    opening = source.find("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    fail(f"unterminated source definition: {signature}")


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def source_structure(fixture: dict[str, Any], source_text: str) -> None:
    source = fixture["source"]
    selection = block(source_text, "RuntimeTableId SelectRuntimeTableId(")
    index = block(source_text, "size_t DirectionIndexFromAxes(")
    lookup = block(source_text, "void ApplyTableAnalogOutput(")
    for fragment in source["selection_required_fragments"]:
        if fragment not in selection:
            fail(f"selection fragment missing: {fragment}")
    for fragment in source["index_required_fragments"]:
        if fragment not in index:
            fail(f"index fragment missing: {fragment}")
    for fragment in source["lookup_required_fragments"]:
        if fragment not in lookup:
            fail(f"lookup fragment missing: {fragment}")

    active = compact(block(source_text, "const ActiveRuntimeConfigState& GetActiveRuntimeConfigState()"))
    resolver = compact(block(source_text, "const RuntimeConfigView& ResolveActiveRuntimeConfig()"))
    required = source["publication_required_fragments"]
    for fragment in required[:3]:
        if fragment not in active:
            fail(f"active publication fragment missing: {fragment}")
    if required[3] not in resolver:
        fail("active resolver publication fragment missing")
    if "candidate.view" in active or "active_storage.view" in active or "candidate.view" in resolver or "active_storage.view" in resolver:
        fail("forbidden alternate active publication path detected")


def evidence_correspondence(fixture: dict[str, Any]) -> None:
    evidence = fixture["evidence"]
    keys(evidence, {"user_direction_ids", "user_observation_id", "work_order_id", "candidate_branch", "candidate_git_sha", "candidate_base_configurator_sha", "integration_commit", "evidence_commit", "evidence_path", "evidence_blob_sha256", "artifact_sha256", "evidence_contract_version", "protocol_reference", "protocol_version", "result", "disconnect_observation", "evidence_gaps"}, "evidence")
    exact(evidence["user_direction_ids"], ["GLYPH-UD-010", "GLYPH-UD-011"], "user direction ids")
    exact(evidence["user_observation_id"], "GLYPH-UD-012", "user observation id")
    exact(evidence["result"], "PASS", "evidence.result")
    exact(evidence["disconnect_observation"], "PASS", "evidence.disconnect_observation")
    exact(evidence["evidence_gaps"], [], "evidence.evidence_gaps")
    exact(evidence["evidence_commit"], "6b0061489cb67d345f212f75268455c181ba271f", "evidence commit")
    exact(evidence["evidence_path"], "docs/calibration/fixtures/x1_offset41_hardware_evidence_2026-09-02.json", "evidence path")
    exact(evidence["candidate_git_sha"], "74ae24364b84520d4e0e39240beb9867653cc7b9", "candidate sha")
    exact(evidence["candidate_base_configurator_sha"], "045bca0d1450c261c3c60ccf5ef86f7302bd3dbc", "candidate base sha")
    exact(evidence["integration_commit"], "1597c01b416b6aa697d73efc7d2c2b3695dc3e5c", "integration commit")
    exact(evidence["evidence_blob_sha256"], "d0d00c4bd3d9a6cae355fecd30aa1c72d1f99581fd53a1b96e610339d61c438b", "evidence blob sha")
    exact(evidence["artifact_sha256"], "5fadd3d7e82e629fbccd41fac868312b07b01e39d2ef0a0a98a06d649ae28254", "artifact sha")
    exact(evidence["evidence_contract_version"], "GLYPH_HARDWARE_EVIDENCE_V2", "evidence contract")
    exact(evidence["protocol_reference"], "docs/calibration/x1_offset41_hardware_test_protocol_2026-09-02.md", "protocol reference")
    exact(evidence["protocol_version"], "GLYPH_X1_OFFSET41_MANUAL_PROTOCOL_V1", "protocol version")
    try:
        raw = subprocess.check_output(
            ["git", "show", f"{evidence['evidence_commit']}:{evidence['evidence_path']}"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        fail(f"immutable evidence object unavailable: {exc}")
    exact(hashlib.sha256(raw).hexdigest(), evidence["evidence_blob_sha256"], "evidence blob sha256")
    if EVIDENCE.read_bytes() != raw:
        fail("working evidence bytes do not match the immutable evidence object")
    recorded = load_object(EVIDENCE)
    for field in ("work_order_id", "candidate_branch", "candidate_git_sha", "candidate_base_configurator_sha"):
        exact(recorded[field], evidence[field], f"recorded evidence {field}")
    exact(recorded["candidate_protocol_version"], evidence["protocol_version"], "recorded evidence protocol version")
    exact(recorded["result"], "PASS", "recorded evidence result")
    exact(recorded["evidence_contract_version"], "GLYPH_HARDWARE_EVIDENCE_V2", "evidence contract version")
    exact(recorded["firmware_artifact_sha256"], evidence["artifact_sha256"], "artifact sha256")
    exact(recorded["evidence_gaps"], [], "recorded evidence gaps")
    exact(subprocess.check_output(["git", "rev-parse", evidence["candidate_branch"]], cwd=ROOT, text=True).strip(), evidence["candidate_git_sha"], "candidate ref")
    parents = subprocess.check_output(["git", "show", "-s", "--format=%P", evidence["integration_commit"]], cwd=ROOT, text=True).split()
    if evidence["candidate_git_sha"] not in parents:
        fail("integration commit does not directly contain the candidate parent")


def validate(fixture: dict[str, Any], source_text: str, tables: dict[str, tuple[tuple[int, int], ...]]) -> None:
    keys(fixture, {"schema_name", "schema_version", "work_order_id", "scope", "role_state", "axes_domain", "directions", "evidence", "source", "non_claims"}, "fixture")
    exact(fixture["schema_name"], "glyph_current_x1_regression_subset", "schema_name")
    exact(fixture["schema_version"], 1, "schema_version")
    exact(fixture["work_order_id"], "GP-VAL-008", "work_order_id")
    exact(fixture["scope"], "sole_non_mode_x1_only", "scope")
    exact(fixture["role_state"], {"mode_active":False,"x1_active":True,"x2_active":False,"y1_active":False,"y2_active":False,"layer_normal_x_active":False,"layer_flipper_active":False,"tilt1_effective":False,"tilt2_effective":False,"tilt3_effective":False}, "role_state")
    exact(fixture["axes_domain"], [-1, 0, 1], "axes_domain")
    exact(fixture["non_claims"], ["not_physical_button_binding", "not_mode_x1_or_mx1", "not_other_modifier_or_override", "not_firmware_simulation", "not_gameplay_semantics", "not_new_hardware_result", "nunchuk_not_tested", "root_cause_unproven"], "non_claims")
    directions = fixture["directions"]
    if not isinstance(directions, list) or len(directions) != 9:
        fail("directions must contain exactly nine rows")
    expected_keys = {"label", "x_axis", "y_axis", "index", "raw"}
    expected_labels = ["down_left", "down", "down_right", "left", "neutral", "right", "up_left", "up", "up_right"]
    for expected_index, row in enumerate(directions):
        if not isinstance(row, dict):
            fail("direction row is not an object")
        keys(row, expected_keys, f"direction {expected_index}")
        exact(row["index"], expected_index, f"direction {expected_index} index")
        if row["x_axis"] not in (-1, 0, 1) or row["y_axis"] not in (-1, 0, 1):
            fail("axis outside the bounded domain")
        exact(row["index"], ((row["y_axis"] + 1) * 3) + (row["x_axis"] + 1), f"direction {expected_index} formula")
        keys(row["raw"], {"x", "y"}, f"direction {expected_index} raw")
        exact(row["label"], expected_labels[expected_index], f"direction {expected_index} label")
        exact(row["raw"], dict(zip(("x", "y"), tables["X1"][expected_index])), f"direction {expected_index} current X1")
    if len({row["label"] for row in directions}) != 9:
        fail("direction labels must be unique")
    evidence_correspondence(fixture)
    for relative, expected_hash in fixture["source"]["file_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            fail(f"source identity mismatch: {relative}")
    source_structure(fixture, source_text)
    exact(tables["X1"], tuple((row["raw"]["x"], row["raw"]["y"]) for row in directions), "extracted kX1Table")
    source = fixture["source"]
    keys(source, {"runtime", "interpreter", "tables", "active_baseline", "table_symbol", "file_sha256", "selection_required_fragments", "index_required_fragments", "lookup_required_fragments", "publication_required_fragments"}, "source")
    exact(source["runtime"], "src/modes/Ultimate.cpp", "runtime source path")
    exact(source["interpreter"], "src/modes/UltimateRuntimeConfigInterpreter.hpp", "interpreter source path")
    exact(source["tables"], "src/modes/UltimateIdentityRuntimeTables.hpp", "tables source path")
    exact(source["active_baseline"], "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp", "active baseline path")
    exact(source["table_symbol"], "kX1Table", "table symbol")
    exact(source["file_sha256"], {"src/modes/Ultimate.cpp":"a40d24db990f0f59ab20ba76257596210e9ccca459415e78235374c2996b2dfd", "src/modes/UltimateRuntimeConfigInterpreter.hpp":"8354ab72bd8dd9e5b14cebc6658bd08cd70396382d1b7499cfbb940684b76108", "src/modes/UltimateIdentityRuntimeTables.hpp":"a0563d1c86f48b8e2e4f664b206eee0e11eb330940426998f6ed80d2c5388fdb", "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp":"533b6a278abfbeb158f5ef7290f00ec79953ad1d0ddc56dede639669f1ea4b7e"}, "source file identities")
    exact(source["selection_required_fragments"], ["if (x1_active)", "active_modifier_count++", "single_modifier = EffectiveModifier::X1", "if (active_modifier_count != 1)", "if (!mode_active)", "case EffectiveModifier::X1:", "return RuntimeTableId::X1;"], "selection fragments")
    exact(source["index_required_fragments"], ["if (x < -1)", "if (x > 1)", "if (y < -1)", "if (y > 1)", "const int index = ((y + 1) * 3) + (x + 1);"], "index fragments")
    exact(source["lookup_required_fragments"], ["const size_t direction_index = DirectionIndexFromAxes(x_axis, y_axis);", "const StickPoint *active_table = LookupRuntimeTable(runtime_config, active_table_id);", "outputs.leftStickX = active_table[direction_index].x;", "outputs.leftStickY = active_table[direction_index].y;"], "lookup fragments")
    exact(source["publication_required_fragments"], ["&kSourceOwnedCurrentBaselineRuntimeConfig", "RuntimeConfigSource::SourceOwnedBaseline", "RuntimeConfigActivationStatus::SourceOwnedSelected", "return *GetActiveRuntimeConfigState().active_view;"], "publication fragments")


def adversarial_tests(fixture: dict[str, Any], source_text: str, tables: dict[str, tuple[tuple[int, int], ...]]) -> None:
    mutations: list[tuple[str, Any, str]] = []
    wrong = copy.deepcopy(fixture); wrong["role_state"]["mode_active"] = True; mutations.append(("wrong mode", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["directions"][4]["raw"]["x"] = 127; mutations.append(("wrong coordinate", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["result"] = "PARTIAL"; mutations.append(("wrong evidence result", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["candidate_git_sha"] = "0" * 40; mutations.append(("wrong candidate identity", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["candidate_base_configurator_sha"] = "0" * 40; mutations.append(("wrong candidate base identity", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["integration_commit"] = "0" * 40; mutations.append(("wrong integration identity", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["evidence_commit"] = "0" * 40; mutations.append(("wrong evidence commit", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["evidence_blob_sha256"] = "0" * 64; mutations.append(("wrong evidence blob", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["artifact_sha256"] = "0" * 64; mutations.append(("wrong artifact identity", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["user_direction_ids"] = ["wrong"]; mutations.append(("wrong user direction identity", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["user_observation_id"] = "wrong"; mutations.append(("wrong user observation identity", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["evidence_contract_version"] = "wrong"; mutations.append(("wrong evidence contract", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["protocol_version"] = "wrong"; mutations.append(("wrong protocol identity", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["protocol_reference"] = "wrong"; mutations.append(("wrong protocol reference", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["evidence_path"] = "wrong.json"; mutations.append(("wrong evidence path", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["evidence"]["unexpected"] = True; mutations.append(("nested schema field", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["directions"].append(copy.deepcopy(wrong["directions"][0])); mutations.append(("extra row", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["directions"][1]["label"] = wrong["directions"][0]["label"]; mutations.append(("duplicate row label", wrong, source_text))
    wrong = copy.deepcopy(fixture); wrong["directions"][0], wrong["directions"][1] = wrong["directions"][1], wrong["directions"][0]; mutations.append(("reordered rows", wrong, source_text))
    wrong_source = source_text.replace("return RuntimeTableId::X1;", "return RuntimeTableId::X2;", 1); mutations.append(("source fragment drift", copy.deepcopy(fixture), wrong_source))
    for label, mutated, mutated_source in mutations:
        try:
            validate(mutated, mutated_source, tables)
        except (CheckError, subprocess.CalledProcessError):
            continue
        fail(f"adversarial mutation unexpectedly passed: {label}")


def main() -> int:
    fixture = load_object(FIXTURE)
    source_text = load_source_text_with_generated_tables(RUNTIME)
    tables = load_source_tables(RUNTIME)
    validate(fixture, source_text, tables)
    adversarial_tests(fixture, source_text, tables)
    print("glyph_current_x1_regression_subset: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
