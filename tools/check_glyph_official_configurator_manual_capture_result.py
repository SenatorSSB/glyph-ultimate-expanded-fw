#!/usr/bin/env python3
"""Validate future manual official-configurator capture scaffolding.

This checker is read-only and stdlib-only. It validates required docs/templates,
baseline capture prerequisites, and optional dated capture folders when present.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

MANUAL_CAPTURE_DIR = REPO_ROOT / "docs" / "export" / "manual_captures"
MANUAL_CAPTURE_README = MANUAL_CAPTURE_DIR / "README.md"
MANUAL_CAPTURE_LAYOUT_DOC = REPO_ROOT / "docs" / "export" / "official_configurator_manual_capture_artifact_layout.md"
CAPTURE_INSTRUCTIONS_DOC = REPO_ROOT / "docs" / "export" / "official_configurator_manual_capture_instructions.md"
RESULT_TEMPLATE_DOC = REPO_ROOT / "docs" / "export" / "official_configurator_manual_import_export_result_TEMPLATE.md"
PLAN_DOC = REPO_ROOT / "docs" / "export" / "official_configurator_manual_import_export_test_plan.md"
PLAN_FIXTURE = REPO_ROOT / "docs" / "export" / "fixtures" / "official_configurator_manual_import_export_test_plan.json"
MANUAL_CAPTURE_METADATA_TEMPLATE = (
    REPO_ROOT / "docs" / "export" / "fixtures" / "official_configurator_manual_capture_metadata_TEMPLATE.json"
)

BASELINE_MANIFEST_PATH = (
    REPO_ROOT / "docs" / "calibration" / "export_corpus" / "official_glyph_configurator_2026-06-06" / "manifest.json"
)
BASELINE_DEFAULT_FIXTURE = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "export_corpus"
    / "official_glyph_configurator_2026-06-06"
    / "fixtures"
    / "glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json"
)
BASELINE_BACK_AND_FORTH_FIXTURE = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "export_corpus"
    / "official_glyph_configurator_2026-06-06"
    / "fixtures"
    / "glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json"
)
BASELINE_PREVIEW_ARTIFACT = REPO_ROOT / "docs" / "export" / "fixtures" / "generated_official_configurator_candidate_preview.json"

DATE_FOLDER_RE = re.compile(r"^\d{8}_official_configurator_[A-Za-z0-9._-]+$")
REQUIRED_MARKER_ROW_IDS = {
    "official_configurator_import_route",
    "official_configurator_export_route",
    "post_capture_json_diff_review",
}
REQUIRED_METADATA_NON_CLAIMS = {
    "production_export_not_claimed": True,
    "official_configurator_compatibility_not_claimed": True,
    "device_write_not_claimed": True,
    "webserial_not_claimed": True,
    "runtime_loaded_config_not_claimed": True,
    "firmware_flashing_automation_not_claimed": True,
    "hardware_behavior_validation_not_claimed": True,
    "nunchuk_validation_not_claimed": True,
    "no_store_imported_external_assertions": True,
}
REQUIRED_METADATA_TEMPLATE_FIELDS = (
    "schema_name",
    "status",
    "official_configurator_app_version",
    "operating_system",
    "operator",
    "capture_datetime",
    "input_candidate_path",
    "input_candidate_sha256",
    "output_export_path",
    "output_export_sha256",
    "app_acceptance_status",
    "import_route",
    "export_route",
    "result_status",
)
REQUIRED_NON_CLAIMS_LIST = {
    "no_device_write",
    "no_webserial",
    "no_runtime_loaded_config",
    "no_firmware_flashing_automation",
    "no_hardware_behavior_validation",
    "no_official_compatibility_claim_until_reviewed",
    "no_nunchuk_validation",
}
FORBIDDEN_CLAIM_PHRASES = (
    "official configurator compatibility",
    "production export",
    "device write",
    "webserial",
    "runtime-loaded config",
    "firmware flashing automation",
    "hardware behavior validation",
    "nunchuk validation",
)
REVIEWED_STATUSES = {"PASS", "FAIL", "NOT_TESTED", "INCONCLUSIVE", "USER_ACCEPTED_RISK"}
PLAN_ONLY_STATUSES = {
    "TEMPLATE_ONLY_NOT_A_RESULT",
    "PLAN_ONLY_TEMPLATE",
    "PLAN_ONLY_NOT_A_RESULT",
    "MANUAL_TEST_PLAN_ONLY_NOT_A_RESULT",
}
IGNORED_HOST_METADATA_BASENAME = ".DS_Store"
CAPTURE_FOLDER_ALLOWED_FILES = {
    "input_candidate.json",
    "output_export.json",
    "rejection_note.md",
    "metadata.json",
    "hashes.txt",
    "notes.md",
    "result.md",
    "optional_screenshot_or_log_notes.md",
    "comparison.json",
    IGNORED_HOST_METADATA_BASENAME,
}

REVIEWED_METADATA_KEYS = {
    "schema_name", "contract_version", "status", "packet_type",
    "official_configurator_app_version", "operating_system", "operator",
    "capture_datetime", "input_candidate_path", "input_candidate_sha256",
    "output_export_path", "output_export_sha256", "app_acceptance_status",
    "import_route", "export_route", "result_status", "capture_performed",
    "result_recorded", "preconditions", "operator_fields", "routes",
    "artifacts", "comparison", "result_rows", "gaps", "non_claims",
    "non_claims_list",
}
REQUIRED_ROW_IDS = frozenset(REQUIRED_MARKER_ROW_IDS)
ROW_STATUSES = {"PASS", "FAIL", "NOT_TESTED", "INCONCLUSIVE"}
OVERALL_STATUSES = {"PASS", "FAIL", "PARTIAL", "INCONCLUSIVE"}
COMPARISON_KEYS = {"comparison_tool", "checker_output_status", "comparison_path"}
ARTIFACT_KEYS = {
    "input_artifact_path", "input_artifact_sha256", "output_artifact_path",
    "output_artifact_sha256", "metadata_path", "notes_path",
    "checker_output_path", "comparison_path", "rejection_note_path",
}
COMPARISON_FILE_KEYS = {
    "schema_name", "schema_version", "capture_id", "input_artifact_sha256",
    "output_artifact_sha256", "checker_identity", "checker_version",
    "structural_diff", "status",
}


class ManualCaptureResultError(ValueError):
    """Raised when manual capture result checker validation fails."""


def fail(message: str) -> None:
    raise ManualCaptureResultError(message)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def normalize(text: str) -> str:
    text = re.sub(r"[-\u2010-\u2015]", " ", text.lower())
    return re.sub(r"\s+", " ", text)


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {display(path)}")
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"failed reading {display(path)}: {exc}")


def read_json_object(path: Path) -> dict[str, Any]:
    text = read_text(path)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {display(path)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{display(path)} must be a JSON object")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def resolve_capture_path(path_value: str, capture_dir: Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute() and len(path.parts) == 1:
        return capture_dir / path
    return resolve_path(path_value)


def require_phrase(text: str, phrase: str, *, where: str) -> None:
    if phrase.lower() not in text.lower():
        fail(f"{where} missing required phrase: {phrase}")


def require_text(text: str, phrases: tuple[str, ...], *, where: str) -> None:
    lowered = normalize(text)
    missing = [phrase for phrase in phrases if phrase.lower() not in lowered]
    if missing:
        fail(f"{where} missing required phrase(s): " + ", ".join(missing))


def is_unknown(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower()
    return normalized in {
        "unknown_to_be_filled_by_operator",
        "unknown_to_be_filled_by_operator_after_capture",
        "unknown_to_be_filled_by_reviewer",
        "unknown_to_be_filled_after_operator_selects_artifact",
        "unknown_not_executed",
        "unknown_not_recorded",
        "unknown",
        "n/a",
        "",
    }


def status_is_reviewed(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    status = value.strip().upper()
    if not status:
        return False
    if status in PLAN_ONLY_STATUSES:
        return False
    if status.startswith("UNKNOWN"):
        return False
    return True


def no_positive_claim(text: str, where: str) -> None:
    lowered = normalize(text)
    negated = re.compile(r"\b(no|not|cannot|does not|do not|did not|without)\b")
    for phrase in FORBIDDEN_CLAIM_PHRASES:
        escaped = re.escape(phrase)
        for match in re.finditer(rf"\b{escaped}\b", lowered):
            context_start = lowered.rfind(".", 0, match.start())
            if context_start == -1:
                context = lowered[: match.start()]
            else:
                context = lowered[context_start + 1 : match.start()]
            if negated.search(context):
                continue
            if "\n" in context:
                line_context = context.splitlines()[-1]
            else:
                line_context = context
            if negated.search(line_context):
                continue
            fail(f"{where} contains unsupported claim phrase: {phrase}")


def check_required_json_file_exists(path: Path, *, what: str) -> None:
    if not path.exists():
        fail(f"missing required {what}: {display(path)}")


def validate_required_docs_and_templates() -> None:
    require_text(
        read_text(MANUAL_CAPTURE_README),
        ("plan_only_directory_index", "No official configurator manual capture has been executed in this branch"),
        where=display(MANUAL_CAPTURE_README),
    )
    require_text(
        read_text(MANUAL_CAPTURE_LAYOUT_DOC),
        ("template_only_not_a_result", "Template used for each capture row"),
        where=display(MANUAL_CAPTURE_LAYOUT_DOC),
    )
    require_text(
        read_text(CAPTURE_INSTRUCTIONS_DOC),
        ("manual_capture_instructions_only_not_a_result", "this branch does not perform capture"),
        where=display(CAPTURE_INSTRUCTIONS_DOC),
    )
    require_text(
        read_text(RESULT_TEMPLATE_DOC),
        ("template_only_not_a_result", "no production export"),
        where=display(RESULT_TEMPLATE_DOC),
    )
    require_text(
        read_text(PLAN_DOC),
        ("manual_test_plan_only_not_a_result", "This packet explicitly does not record a result"),
        where=display(PLAN_DOC),
    )

    for path in (
        BASELINE_MANIFEST_PATH,
        BASELINE_DEFAULT_FIXTURE,
        BASELINE_BACK_AND_FORTH_FIXTURE,
        BASELINE_PREVIEW_ARTIFACT,
    ):
        check_required_json_file_exists(path, what="baseline artifact")

    plan_payload = read_json_object(PLAN_FIXTURE)
    if plan_payload.get("status") != "MANUAL_TEST_PLAN_ONLY_NOT_A_RESULT":
        fail(f"{display(PLAN_FIXTURE)} must remain plan-only and not a result")
    if plan_payload.get("candidate_preview_artifact") != display(BASELINE_PREVIEW_ARTIFACT):
        fail(f"{display(PLAN_FIXTURE)} candidate_preview_artifact mismatch")
    if plan_payload.get("comparison_tool_after_capture") != "tools/check_glyph_official_configurator_export_candidate_diff.py":
        fail(f"{display(PLAN_FIXTURE)} comparison_tool_after_capture must be the export candidate diff checker")
    plan_rows = plan_payload.get("future_result_rows")
    if not isinstance(plan_rows, list) or not plan_rows:
        fail(f"{display(PLAN_FIXTURE)} future_result_rows missing")
    for row in plan_rows:
        if not isinstance(row, dict):
            fail(f"{display(PLAN_FIXTURE)} future result row must be objects")
        if row.get("status") != "UNKNOWN_NOT_EXECUTED":
            fail(f"{display(PLAN_FIXTURE)} future result rows must remain unknown/not executed")
        if row.get("pass") is not False:
            fail(f"{display(PLAN_FIXTURE)} future result rows must be unexecuted")

    template_payload = read_json_object(MANUAL_CAPTURE_METADATA_TEMPLATE)
    if template_payload.get("status") != "TEMPLATE_ONLY_NOT_A_RESULT":
        fail(f"{display(MANUAL_CAPTURE_METADATA_TEMPLATE)} must remain template-only")
    for key in REQUIRED_METADATA_TEMPLATE_FIELDS:
        if key not in template_payload:
            fail(f"{display(MANUAL_CAPTURE_METADATA_TEMPLATE)} missing required field: {key}")
    if template_payload.get("schema_name") != "official_configurator_manual_capture_metadata":
        fail(f"{display(MANUAL_CAPTURE_METADATA_TEMPLATE)} schema_name must be official_configurator_manual_capture_metadata")
    if template_payload.get("contract_version") != 2:
        fail(f"{display(MANUAL_CAPTURE_METADATA_TEMPLATE)} contract_version must be 2")
    if template_payload.get("packet_type") != "official_configurator_manual_capture":
        fail(f"{display(MANUAL_CAPTURE_METADATA_TEMPLATE)} packet_type must be official_configurator_manual_capture")
    if template_payload.get("capture_performed") is not False or template_payload.get("result_recorded") is not False:
        fail(f"{display(MANUAL_CAPTURE_METADATA_TEMPLATE)} must remain capture/result unknown placeholders")
    if template_payload.get("official_configurator_app_version") != "UNKNOWN_TO_BE_FILLED_BY_OPERATOR":
        fail(f"{display(MANUAL_CAPTURE_METADATA_TEMPLATE)} official_configurator_app_version must be an operator placeholder")
    non_claims_list = template_payload.get("non_claims_list")
    if not isinstance(non_claims_list, list) or set(non_claims_list) != REQUIRED_NON_CLAIMS_LIST:
        fail(f"{display(MANUAL_CAPTURE_METADATA_TEMPLATE)} non_claims_list mismatch")

    no_positive_claim(read_text(PLAN_DOC), where=display(PLAN_DOC))
    no_positive_claim(read_text(PLAN_FIXTURE), where=display(PLAN_FIXTURE))
    no_positive_claim(read_text(RESULT_TEMPLATE_DOC), where=display(RESULT_TEMPLATE_DOC))
    no_positive_claim(read_text(CAPTURE_INSTRUCTIONS_DOC), where=display(CAPTURE_INSTRUCTIONS_DOC))


def validate_metadata_payload(payload: dict[str, Any], capture_dir: Path) -> None:
    if payload.get("contract_version") != 2:
        fail(f"{display(capture_dir)} metadata contract_version must be 2")
    if set(payload) != REVIEWED_METADATA_KEYS:
        fail(f"{display(capture_dir)} metadata keys must match strict schema v2")
    if not isinstance(payload.get("schema_name"), str) or payload["schema_name"] != "official_configurator_manual_capture_metadata":
        fail(f"{display(capture_dir)} metadata payload schema_name must be official_configurator_manual_capture_metadata")
    overall = str(payload.get("status", "")).strip().upper()
    if overall not in OVERALL_STATUSES:
        fail(f"{display(capture_dir)} metadata status must be PASS, FAIL, PARTIAL, or INCONCLUSIVE")
    if str(payload.get("result_status", "")).strip().upper() != overall:
        fail(f"{display(capture_dir)} result_status must equal status")
    if payload.get("packet_type") != "official_configurator_manual_capture":
        fail(f"{display(capture_dir)} metadata payload packet_type must be official_configurator_manual_capture")
    if payload.get("capture_performed") is not True:
        fail(f"{display(capture_dir)} metadata must set capture_performed=True after review")
    if payload.get("result_recorded") is not True:
        fail(f"{display(capture_dir)} metadata must set result_recorded=True after review")
    for key in REQUIRED_METADATA_TEMPLATE_FIELDS:
        value = payload.get(key)
        if is_unknown(value):
            fail(f"{display(capture_dir)} metadata field {key} must be filled in reviewed packets")
    acceptance = str(payload.get("app_acceptance_status", "")).strip().upper()
    if acceptance not in {"ACCEPTED", "REJECTED", "INCONCLUSIVE"}:
        fail(f"{display(capture_dir)} app_acceptance_status must be ACCEPTED, REJECTED, or INCONCLUSIVE")

    preconditions = payload.get("preconditions")
    if not isinstance(preconditions, dict):
        fail(f"{display(capture_dir)} metadata preconditions missing")
    for key in (
        "official_corpus_manifest_path",
        "official_corpus_default_profiles_path",
        "official_corpus_back_and_forth_path",
        "candidate_preview_artifact",
    ):
        value = preconditions.get(key)
        if is_unknown(value):
            fail(f"{display(capture_dir)} precondition {key} must be filled in reviewed packets")
        if not isinstance(value, str) or not resolve_path(value).exists():
            fail(f"{display(capture_dir)} precondition path missing or invalid: {key}")

    operator_fields = payload.get("operator_fields")
    if not isinstance(operator_fields, dict):
        fail(f"{display(capture_dir)} metadata operator_fields missing")
    for key, value in operator_fields.items():
        if is_unknown(value):
            fail(f"{display(capture_dir)} operator field {key} must be reviewed")

    routes = payload.get("routes")
    if not isinstance(routes, dict):
        fail(f"{display(capture_dir)} metadata routes missing")
    for key, value in routes.items():
        if is_unknown(value):
            fail(f"{display(capture_dir)} route {key} must be reviewed")

    comparison = payload.get("comparison")
    if comparison is not None and (not isinstance(comparison, dict) or set(comparison) != COMPARISON_KEYS):
        fail(f"{display(capture_dir)} metadata comparison must be null or strict schema v2 object")
    if isinstance(comparison, dict):
        if comparison.get("comparison_tool") != "tools/check_glyph_official_configurator_export_candidate_diff.py":
            fail(f"{display(capture_dir)} comparison_tool must be export candidate diff checker")
        if comparison.get("checker_output_status") not in ROW_STATUSES:
            fail(f"{display(capture_dir)} comparison.checker_output_status must be a row status")
        if comparison.get("comparison_path") != "comparison.json":
            fail(f"{display(capture_dir)} comparison_path must be comparison.json")

    result_rows = payload.get("result_rows")
    if not isinstance(result_rows, list) or not result_rows:
        fail(f"{display(capture_dir)} metadata result_rows missing")
    observed: set[str] = set()
    for row in result_rows:
        if not isinstance(row, dict):
            fail(f"{display(capture_dir)} result_rows entries must be objects")
        row_id = row.get("row_id")
        status = row.get("status")
        passed = row.get("pass")
        if not isinstance(row_id, str) or not row_id:
            fail(f"{display(capture_dir)} result row_id must be a non-empty string")
        if not isinstance(status, str):
            fail(f"{display(capture_dir)} result row {row_id} status must be a string")
        status_value = status.strip().upper()
        if status_value not in ROW_STATUSES:
            fail(f"{display(capture_dir)} result row {row_id} status must be PASS, FAIL, NOT_TESTED, or INCONCLUSIVE")
        if not isinstance(passed, bool):
            fail(f"{display(capture_dir)} result row {row_id} pass must be boolean")
        if passed is not (status_value == "PASS"):
            fail(f"{display(capture_dir)} result row {row_id} pass must be true exactly for PASS")
        if row_id in observed:
            fail(f"{display(capture_dir)} duplicate result row {row_id}")
        observed.add(row_id)
    if observed != REQUIRED_ROW_IDS:
        missing = REQUIRED_ROW_IDS - observed
        extra = observed - REQUIRED_ROW_IDS
        fail(f"{display(capture_dir)} result_rows must be exactly required rows; missing={sorted(missing)} extra={sorted(extra)}")

    non_claims = payload.get("non_claims")
    if not isinstance(non_claims, dict):
        fail(f"{display(capture_dir)} metadata non_claims missing")
    for key, expected in REQUIRED_METADATA_NON_CLAIMS.items():
        actual = non_claims.get(key)
        if actual is not expected:
            fail(f"{display(capture_dir)} metadata non_claims.{key} must be {expected}")
    non_claims_list = payload.get("non_claims_list", [])
    if non_claims_list and (not isinstance(non_claims_list, list) or not REQUIRED_NON_CLAIMS_LIST.issubset(set(non_claims_list))):
        fail(f"{display(capture_dir)} metadata non_claims_list is missing required values")

    gaps = payload.get("gaps")
    if not isinstance(gaps, list) or any(not isinstance(item, str) or not item.strip() for item in gaps):
        fail(f"{display(capture_dir)} gaps must be a list of non-empty strings")
    rows = {row["row_id"]: row for row in payload["result_rows"]}
    executed = [row for row in rows.values() if row["status"] in {"PASS", "FAIL"}]
    if overall == "PASS":
        if acceptance != "ACCEPTED" or not executed or any(row["status"] != "PASS" for row in rows.values()) or comparison is None or gaps:
            fail(f"{display(capture_dir)} PASS matrix is not satisfied")
    elif overall == "FAIL":
        rejected_shape = acceptance == "REJECTED" and rows["official_configurator_import_route"]["status"] == "FAIL" and all(
            rows[row_id]["status"] == "NOT_TESTED" for row_id in ("official_configurator_export_route", "post_capture_json_diff_review")
        ) and comparison is None and not gaps
        accepted_shape = acceptance == "ACCEPTED" and all(row["status"] in {"PASS", "FAIL"} for row in rows.values()) and any(row["status"] == "FAIL" for row in rows.values()) and comparison is not None and not gaps
        if not (rejected_shape or accepted_shape):
            fail(f"{display(capture_dir)} FAIL matrix is not satisfied")
    elif overall == "PARTIAL":
        if acceptance != "ACCEPTED" or not executed or not any(row["status"] == "NOT_TESTED" for row in rows.values()) or any(row["status"] == "INCONCLUSIVE" for row in rows.values()) or not gaps:
            fail(f"{display(capture_dir)} PARTIAL matrix is not satisfied")
        if rows["post_capture_json_diff_review"]["status"] in {"PASS", "FAIL"} and comparison is None:
            fail(f"{display(capture_dir)} executed diff row requires comparison")
        if rows["post_capture_json_diff_review"]["status"] == "NOT_TESTED" and comparison is not None:
            fail(f"{display(capture_dir)} unexecuted diff row forbids comparison")
    elif acceptance != "INCONCLUSIVE" or not any(row["status"] == "INCONCLUSIVE" for row in rows.values()) or not gaps or (comparison is not None and rows["post_capture_json_diff_review"]["status"] == "NOT_TESTED"):
        fail(f"{display(capture_dir)} INCONCLUSIVE matrix is not satisfied")


def validate_result_doc(folder: Path, capture_id: str) -> None:
    result_doc = folder / "result.md"
    if not result_doc.exists():
        fail(f"{display(folder)} missing required result markdown {result_doc.name}")
    text = read_text(result_doc)
    status_match = re.search(r"(?im)^\s*status\s*[:=]\s*`?([A-Za-z0-9_ -]+?)`?\s*$", text)
    if not status_match:
        fail(f"{display(folder)} result markdown must include a Status marker")
    status = status_match.group(1).strip().upper().replace(" ", "_")
    if status not in OVERALL_STATUSES:
        fail(f"{display(folder)} result markdown status must be an overall v2 status")
    no_positive_claim(text, where=f"result doc {display(result_doc)}")


def resolve_and_validate_artifact(path_value: str, *, expected: Path, label: str, where: str, capture_dir: Path) -> Path:
    if not isinstance(path_value, str):
        fail(f"{where} artifacts.{label} must be a path string")
    resolved = resolve_capture_path(path_value, capture_dir)
    if resolved != expected:
        fail(f"{where} artifacts.{label} must be {expected.name}")
    if not resolved.exists():
        fail(f"{where} artifacts.{label} missing: {display(resolved)}")
    return resolved


def validate_file_set(capture_dir: Path, capture_id: str, payload: dict[str, Any]) -> None:
    validate_capture_folder_entries(capture_dir)
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != ARTIFACT_KEYS:
        fail(f"{display(capture_dir)} artifacts must match strict schema v2 keys")
    for key in ("input_artifact_path", "input_artifact_sha256", "metadata_path", "notes_path"):
        if not isinstance(artifacts.get(key), str) or is_unknown(artifacts[key]):
            fail(f"{display(capture_dir)} artifacts.{key} must be a filled string")
    for key in ("output_artifact_path", "output_artifact_sha256", "checker_output_path", "comparison_path", "rejection_note_path"):
        value = artifacts.get(key)
        if value is not None and (not isinstance(value, str) or is_unknown(value)):
            fail(f"{display(capture_dir)} artifacts.{key} must be a string or null")
    if not isinstance(artifacts, dict):
        fail(f"{display(capture_dir)} artifacts section missing")

    expected_input = capture_dir / "input_candidate.json"
    expected_output = capture_dir / "output_export.json"
    expected_rejection = capture_dir / "rejection_note.md"
    expected_hashes = capture_dir / "hashes.txt"
    expected_metadata = capture_dir / "metadata.json"
    expected_notes = capture_dir / "notes.md"
    expected_comparison = capture_dir / "comparison.json"

    if not expected_notes.exists():
        fail(f"{display(capture_dir)} missing required notes file {expected_notes.name}")
    if not expected_hashes.exists():
        fail(f"{display(capture_dir)} missing required hashes file {expected_hashes.name}")
    if not expected_metadata.exists():
        fail(f"{display(capture_dir)} missing required metadata file {expected_metadata.name}")

    for file_path in (expected_input, expected_metadata):
        if not file_path.exists():
            fail(f"{display(capture_dir)} missing required capture file {file_path.name}")
        if not isinstance(read_json_object(file_path), dict):
            fail(f"{display(file_path)} must contain a JSON object")
    has_output = expected_output.exists()
    has_rejection = expected_rejection.exists()
    if has_output == has_rejection:
        fail(f"{display(capture_dir)} must contain exactly one of output_export.json or rejection_note.md")
    if has_output and not isinstance(read_json_object(expected_output), dict):
        fail(f"{display(expected_output)} must contain a JSON object")

    input_path = resolve_and_validate_artifact(
        artifacts.get("input_artifact_path") or payload.get("input_candidate_path"),
        expected=expected_input,
        label="input_artifact_path",
        where=display(capture_dir),
        capture_dir=capture_dir,
    )
    output_path: Path | None = None
    if has_output:
        output_path = resolve_and_validate_artifact(
            artifacts.get("output_artifact_path") or payload.get("output_export_path"),
            expected=expected_output,
            label="output_artifact_path",
            where=display(capture_dir),
            capture_dir=capture_dir,
        )

    metadata_path = artifacts.get("metadata_path")
    if is_unknown(metadata_path) or not isinstance(metadata_path, str):
        fail(f"{display(capture_dir)} artifacts.metadata_path must be filled in reviewed packets")
    resolved_metadata = resolve_capture_path(metadata_path, capture_dir)
    if resolved_metadata != expected_metadata:
        fail(f"{display(capture_dir)} artifacts.metadata_path must be metadata.json")

    expected_notes_text = read_text(expected_notes)
    no_positive_claim(expected_notes_text, where=f"notes {display(expected_notes)}")
    hashes_text = read_text(expected_hashes)
    no_positive_claim(hashes_text, where=f"hashes {display(expected_hashes)}")

    expected_input_hash = artifacts.get("input_artifact_sha256") or payload.get("input_candidate_sha256")
    if expected_input_hash != sha256_file(input_path):
        fail(f"{display(capture_dir)} input_artifact_sha256 mismatch")
    if output_path is not None:
        expected_output_hash = artifacts.get("output_artifact_sha256") or payload.get("output_export_sha256")
        if expected_output_hash != sha256_file(output_path):
            fail(f"{display(capture_dir)} output_artifact_sha256 mismatch")
    elif "rejection_note.md" not in hashes_text:
        fail(f"{display(capture_dir)} hashes.txt must record rejection_note.md hash when no output export exists")

    comparison = payload.get("comparison")
    if comparison is not None:
        if not expected_output.exists():
            fail(f"{display(capture_dir)} comparison is forbidden without output_export.json")
        if not expected_comparison.exists() or expected_comparison.is_symlink():
            fail(f"{display(capture_dir)} comparison.json is required for an executed diff")
        comparison_payload = read_json_object(expected_comparison)
        if set(comparison_payload) != COMPARISON_FILE_KEYS:
            fail(f"{display(expected_comparison)} keys must match strict comparison schema")
        if comparison_payload.get("schema_name") != "official_configurator_capture_comparison" or comparison_payload.get("schema_version") != 2:
            fail(f"{display(expected_comparison)} schema identity mismatch")
        if comparison_payload.get("capture_id") != capture_id:
            fail(f"{display(expected_comparison)} capture_id mismatch")
        if comparison_payload.get("input_artifact_sha256") != sha256_file(input_path) or comparison_payload.get("output_artifact_sha256") != sha256_file(output_path):
            fail(f"{display(expected_comparison)} input/output hash binding mismatch")
        if not isinstance(comparison_payload.get("checker_identity"), str) or not comparison_payload["checker_identity"].strip() or not isinstance(comparison_payload.get("checker_version"), str) or not comparison_payload["checker_version"].strip():
            fail(f"{display(expected_comparison)} checker identity/version must be non-empty")
        if not isinstance(comparison_payload.get("structural_diff"), dict):
            fail(f"{display(expected_comparison)} structural_diff must be an object")
        if comparison_payload.get("status") != comparison.get("checker_output_status"):
            fail(f"{display(expected_comparison)} status must match metadata diff row")
    elif expected_comparison.exists():
        fail(f"{display(capture_dir)} comparison.json requires a comparison object")

    expected_files = {path.name for path in capture_dir.iterdir() if _is_regular_non_symlink_file(path) and path.name != IGNORED_HOST_METADATA_BASENAME and path.name != "hashes.txt"}
    listed: dict[str, str] = {}
    for line in hashes_text.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-fA-F]{64})  (.+)", line)
        if not match or match.group(2) in listed or match.group(2) == "hashes.txt":
            fail(f"{display(expected_hashes)} must contain unique '<sha256>  <filename>' rows")
        listed[match.group(2)] = match.group(1).lower()
    if set(listed) != expected_files:
        fail(f"{display(expected_hashes)} must enumerate exactly every regular evidence file")
    for name, digest in listed.items():
        if digest != sha256_file(capture_dir / name):
            fail(f"{display(expected_hashes)} hash mismatch for {name}")


def find_reviewed_capture_metadata(capture_dir: Path) -> dict[str, Any]:
    metadata_path = capture_dir / "metadata.json"
    if not metadata_path.exists():
        fail(f"{display(capture_dir)} has no metadata.json")
    payload = read_json_object(metadata_path)
    if payload.get("schema_name") != "official_configurator_manual_capture_metadata":
        fail(f"{display(metadata_path)} schema_name must be official_configurator_manual_capture_metadata")
    return payload


def validate_single_capture_folder(capture_dir: Path) -> None:
    if not capture_dir.is_dir():
        return
    capture_id = capture_dir.name
    metadata = find_reviewed_capture_metadata(capture_dir)
    validate_metadata_payload(metadata, capture_dir)
    validate_file_set(capture_dir, capture_id, metadata)
    validate_result_doc(capture_dir, capture_id)

    metadata_path = metadata.get("artifacts", {}).get("metadata_path")
    if isinstance(metadata_path, str):
        metadata_path = resolve_capture_path(metadata_path, capture_dir)
        no_positive_claim(read_text(metadata_path), where=f"metadata {display(metadata_path)}")

    if metadata.get("comparison") is not None and metadata["comparison"].get("checker_output_status") not in ROW_STATUSES:
        fail(f"{display(capture_dir)} comparison checker output status must be reviewed")


def _is_regular_non_symlink_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def _is_ignored_host_metadata(path: Path) -> bool:
    return path.name == IGNORED_HOST_METADATA_BASENAME and _is_regular_non_symlink_file(path)


def validate_capture_folder_entries(capture_dir: Path) -> None:
    for entry in sorted(capture_dir.iterdir()):
        if _is_ignored_host_metadata(entry):
            continue
        if entry.is_symlink():
            fail(f"unexpected symlink in capture folder {display(entry)}")
        if not _is_regular_non_symlink_file(entry) or entry.name not in CAPTURE_FOLDER_ALLOWED_FILES:
            fail(
                f"unexpected capture folder entry {display(entry)}; "
                "only documented capture files and regular .DS_Store host metadata are allowed"
            )


def validate_manual_capture_root_entries(root: Path) -> list[Path]:
    capture_folders: list[Path] = []
    allowed_files = {"README.md", ".gitkeep", IGNORED_HOST_METADATA_BASENAME}
    for entry in sorted(root.iterdir()):
        if _is_ignored_host_metadata(entry):
            continue
        if entry.is_symlink():
            fail(f"unexpected symlink in manual capture directory {display(entry)}")
        if entry.is_file() and entry.name in allowed_files:
            continue
        if entry.is_dir() and DATE_FOLDER_RE.fullmatch(entry.name):
            capture_folders.append(entry)
            continue
        fail(
            f"unexpected manual capture directory entry {display(entry)}; "
            "future capture folders must match YYYYMMDD_official_configurator_<app-version-or-unknown>"
        )
    return capture_folders


def run_adversarial_tests() -> None:
    with tempfile.TemporaryDirectory(prefix="glyph-manual-capture-adversarial-") as directory:
        root = Path(directory)
        (root / "README.md").write_text("index", encoding="utf-8")
        (root / ".gitkeep").write_text("", encoding="utf-8")
        (root / IGNORED_HOST_METADATA_BASENAME).write_bytes(b"host metadata")
        (root / "20260823_official_configurator_unknown").mkdir()
        assert len(validate_manual_capture_root_entries(root)) == 1

        (root / "unknown.txt").write_text("evidence", encoding="utf-8")
        try:
            validate_manual_capture_root_entries(root)
        except ManualCaptureResultError:
            pass
        else:
            raise AssertionError("unknown root file must be rejected")
        (root / "unknown.txt").unlink()

        (root / IGNORED_HOST_METADATA_BASENAME).unlink()
        (root / IGNORED_HOST_METADATA_BASENAME).mkdir()
        try:
            validate_manual_capture_root_entries(root)
        except ManualCaptureResultError:
            pass
        else:
            raise AssertionError("root .DS_Store directory must be rejected")
        (root / IGNORED_HOST_METADATA_BASENAME).rmdir()

        (root / IGNORED_HOST_METADATA_BASENAME).symlink_to(root / "README.md")
        try:
            validate_manual_capture_root_entries(root)
        except ManualCaptureResultError:
            pass
        else:
            raise AssertionError("root .DS_Store symlink must be rejected")
        (root / IGNORED_HOST_METADATA_BASENAME).unlink()
        (root / IGNORED_HOST_METADATA_BASENAME).write_bytes(b"host metadata")

        capture = root / "20260823_official_configurator_unknown"
        for name in CAPTURE_FOLDER_ALLOWED_FILES - {IGNORED_HOST_METADATA_BASENAME}:
            (capture / name).write_text("fixture", encoding="utf-8")
        (capture / IGNORED_HOST_METADATA_BASENAME).write_bytes(b"host metadata")
        validate_capture_folder_entries(capture)

        (capture / "unknown.log").write_text("evidence", encoding="utf-8")
        try:
            validate_capture_folder_entries(capture)
        except ManualCaptureResultError:
            pass
        else:
            raise AssertionError("unknown capture file must be rejected")
        (capture / "unknown.log").unlink()

        (capture / IGNORED_HOST_METADATA_BASENAME).unlink()
        (capture / IGNORED_HOST_METADATA_BASENAME).mkdir()
        try:
            validate_capture_folder_entries(capture)
        except ManualCaptureResultError:
            pass
        else:
            raise AssertionError(".DS_Store directory must be rejected")
        (capture / IGNORED_HOST_METADATA_BASENAME).rmdir()

        (capture / IGNORED_HOST_METADATA_BASENAME).symlink_to(capture / "notes.md")
        try:
            validate_capture_folder_entries(capture)
        except ManualCaptureResultError:
            pass
        else:
            raise AssertionError(".DS_Store symlink must be rejected")

        def write_synthetic_packet(folder: Path, *, status: str, acceptance: str, row_statuses: dict[str, str], gaps: list[str], rejected: bool = False) -> None:
            folder.mkdir()
            input_path = folder / "input_candidate.json"
            input_path.write_text('{"candidate": "synthetic"}\n', encoding="utf-8")
            output_path = folder / "output_export.json"
            rejection_path = folder / "rejection_note.md"
            if rejected:
                rejection_path.write_text("The app rejected this synthetic packet.\n", encoding="utf-8")
            else:
                output_path.write_text('{"export": "synthetic"}\n', encoding="utf-8")
            (folder / "notes.md").write_text("Synthetic checker fixture; no operator evidence.\n", encoding="utf-8")
            comparison = None
            if not rejected and row_statuses["post_capture_json_diff_review"] in {"PASS", "FAIL"}:
                comparison = {
                    "comparison_tool": "tools/check_glyph_official_configurator_export_candidate_diff.py",
                    "checker_output_status": row_statuses["post_capture_json_diff_review"],
                    "comparison_path": "comparison.json",
                }
                (folder / "comparison.json").write_text(json.dumps({
                    "schema_name": "official_configurator_capture_comparison",
                    "schema_version": 2,
                    "capture_id": folder.name,
                    "input_artifact_sha256": sha256_file(input_path),
                    "output_artifact_sha256": sha256_file(output_path),
                    "checker_identity": "synthetic-checker",
                    "checker_version": "2",
                    "structural_diff": {},
                    "status": row_statuses["post_capture_json_diff_review"],
                }, sort_keys=True) + "\n", encoding="utf-8")
            metadata = {
                "schema_name": "official_configurator_manual_capture_metadata", "contract_version": 2,
                "status": status, "packet_type": "official_configurator_manual_capture",
                "official_configurator_app_version": "synthetic", "operating_system": "synthetic",
                "operator": "synthetic", "capture_datetime": "2026-08-24T00:00:00Z",
                "input_candidate_path": "input_candidate.json", "input_candidate_sha256": sha256_file(input_path),
                "output_export_path": None if rejected else "output_export.json",
                "output_export_sha256": None if rejected else sha256_file(output_path),
                "app_acceptance_status": acceptance, "import_route": "synthetic", "export_route": "synthetic",
                "result_status": status, "capture_performed": True, "result_recorded": True,
                "preconditions": {"official_corpus_manifest_path": display(BASELINE_MANIFEST_PATH), "official_corpus_default_profiles_path": display(BASELINE_DEFAULT_FIXTURE), "official_corpus_back_and_forth_path": display(BASELINE_BACK_AND_FORTH_FIXTURE), "candidate_preview_artifact": display(BASELINE_PREVIEW_ARTIFACT)},
                "operator_fields": {"operator": "synthetic"}, "routes": {"import_route": "synthetic", "export_route": "synthetic"},
                "artifacts": {"input_artifact_path": "input_candidate.json", "input_artifact_sha256": sha256_file(input_path), "output_artifact_path": None if rejected else "output_export.json", "output_artifact_sha256": None if rejected else sha256_file(output_path), "metadata_path": "metadata.json", "notes_path": "notes.md", "checker_output_path": None if rejected else "comparison.json", "comparison_path": None if rejected else "comparison.json", "rejection_note_path": "rejection_note.md" if rejected else None},
                "comparison": comparison,
                "result_rows": [{"row_id": row_id, "status": row_statuses[row_id], "pass": row_statuses[row_id] == "PASS"} for row_id in REQUIRED_ROW_IDS],
                "gaps": gaps, "non_claims": dict(REQUIRED_METADATA_NON_CLAIMS), "non_claims_list": sorted(REQUIRED_NON_CLAIMS_LIST),
            }
            (folder / "metadata.json").write_text(json.dumps(metadata, sort_keys=True) + "\n", encoding="utf-8")
            (folder / "result.md").write_text(f"# Synthetic result\n\nStatus: `{status}`\n", encoding="utf-8")
            evidence_files = sorted(path for path in folder.iterdir() if path.name != "hashes.txt" and path.name != IGNORED_HOST_METADATA_BASENAME)
            (folder / "hashes.txt").write_text("".join(f"{sha256_file(path)}  {path.name}\n" for path in evidence_files), encoding="utf-8")
            validate_single_capture_folder(folder)

        synthetic_root = root / "synthetic"
        synthetic_root.mkdir()
        write_synthetic_packet(synthetic_root / "20260824_official_configurator_pass", status="PASS", acceptance="ACCEPTED", row_statuses={row_id: "PASS" for row_id in REQUIRED_ROW_IDS}, gaps=[])
        write_synthetic_packet(synthetic_root / "20260824_official_configurator_fail", status="FAIL", acceptance="ACCEPTED", row_statuses={"official_configurator_import_route": "PASS", "official_configurator_export_route": "FAIL", "post_capture_json_diff_review": "PASS"}, gaps=[])
        write_synthetic_packet(synthetic_root / "20260824_official_configurator_partial", status="PARTIAL", acceptance="ACCEPTED", row_statuses={"official_configurator_import_route": "PASS", "official_configurator_export_route": "NOT_TESTED", "post_capture_json_diff_review": "NOT_TESTED"}, gaps=["export not executed", "diff not executed"])
        write_synthetic_packet(synthetic_root / "20260824_official_configurator_inconclusive", status="INCONCLUSIVE", acceptance="INCONCLUSIVE", row_statuses={"official_configurator_import_route": "INCONCLUSIVE", "official_configurator_export_route": "NOT_TESTED", "post_capture_json_diff_review": "NOT_TESTED"}, gaps=["operator result unresolved"])
        write_synthetic_packet(synthetic_root / "20260824_official_configurator_rejected", status="FAIL", acceptance="REJECTED", row_statuses={"official_configurator_import_route": "FAIL", "official_configurator_export_route": "NOT_TESTED", "post_capture_json_diff_review": "NOT_TESTED"}, gaps=[], rejected=True)

        tamper = synthetic_root / "20260824_official_configurator_tamper"
        write_synthetic_packet(tamper, status="PASS", acceptance="ACCEPTED", row_statuses={row_id: "PASS" for row_id in REQUIRED_ROW_IDS}, gaps=[])
        tampered_comparison = read_json_object(tamper / "comparison.json")
        tampered_comparison["input_artifact_sha256"] = "0" * 64
        (tamper / "comparison.json").write_text(json.dumps(tampered_comparison) + "\n", encoding="utf-8")
        try:
            validate_file_set(tamper, tamper.name, read_json_object(tamper / "metadata.json"))
        except ManualCaptureResultError:
            pass
        else:
            raise AssertionError("tampered comparison binding must be rejected")


def list_dated_capture_folders() -> list[Path]:
    if not MANUAL_CAPTURE_DIR.exists():
        fail(f"manual capture directory missing: {display(MANUAL_CAPTURE_DIR)}")
    if not MANUAL_CAPTURE_README.exists():
        fail(f"missing required manual capture README: {display(MANUAL_CAPTURE_README)}")
    return validate_manual_capture_root_entries(MANUAL_CAPTURE_DIR)


def main() -> int:
    print("glyph_official_configurator_manual_capture_result")
    try:
        if "--adversarial-test" in sys.argv[1:]:
            run_adversarial_tests()
            print("status=PASS")
            print("adversarial_host_metadata_rules_valid=True")
            return 0
        validate_required_docs_and_templates()
        capture_folders = list_dated_capture_folders()
        print(f"manual_capture_folder_count={len(capture_folders)}")
        for folder in capture_folders:
            validate_single_capture_folder(folder)
            print(f"manual_capture_folder_ok={display(folder)}")
    except (OSError, ManualCaptureResultError) as exc:
        print("status=FAIL")
        print("manual_capture_scaffold_valid=False")
        print(f"error={exc}")
        return 1
    print("status=PASS")
    print("manual_capture_scaffold_valid=True")
    print("forbidden_claims_blocked=True")
    print("reviewed_capture_result_packet_found=True" if capture_folders else "reviewed_capture_result_packet_found=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
