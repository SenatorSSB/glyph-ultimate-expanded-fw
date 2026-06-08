#!/usr/bin/env python3
"""Validate future manual official-configurator capture scaffolding.

This checker is read-only and stdlib-only. It validates required docs/templates,
baseline capture prerequisites, and optional dated capture folders when present.
"""

from __future__ import annotations

import hashlib
import json
import re
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
    if template_payload.get("contract_version") != 1:
        fail(f"{display(MANUAL_CAPTURE_METADATA_TEMPLATE)} contract_version must be 1")
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
    if not isinstance(payload.get("schema_name"), str) or payload["schema_name"] != "official_configurator_manual_capture_metadata":
        fail(f"{display(capture_dir)} metadata payload schema_name must be official_configurator_manual_capture_metadata")
    if not status_is_reviewed(payload.get("status")):
        fail(f"{display(capture_dir)} metadata payload status must indicate reviewed result state")
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
    if not isinstance(comparison, dict):
        fail(f"{display(capture_dir)} metadata comparison missing")
    comparison_tool = comparison.get("comparison_tool")
    if comparison_tool != "tools/check_glyph_official_configurator_export_candidate_diff.py":
        fail(f"{display(capture_dir)} comparison_tool must be export candidate diff checker")
    if not status_is_reviewed(comparison.get("checker_output_status")):
        fail(f"{display(capture_dir)} comparison.checker_output_status must be reviewed")

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
        if status_value.startswith("UNKNOWN"):
            fail(f"{display(capture_dir)} result row {row_id} status must be reviewed")
        if status_value not in REVIEWED_STATUSES:
            fail(f"{display(capture_dir)} result row {row_id} status must be a reviewed status")
        if not isinstance(passed, bool):
            fail(f"{display(capture_dir)} result row {row_id} pass must be boolean")
        observed.add(row_id)
    missing = REQUIRED_MARKER_ROW_IDS - observed
    if missing:
        fail(f"{display(capture_dir)} result_rows missing required markers: {', '.join(sorted(missing))}")

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


def validate_result_doc(folder: Path, capture_id: str) -> None:
    result_doc = folder / "result.md"
    if not result_doc.exists():
        fail(f"{display(folder)} missing required result markdown {result_doc.name}")
    text = read_text(result_doc)
    status_match = re.search(r"(?im)^\s*status\s*[:=]\s*`?([A-Za-z0-9_ -]+)`?", text)
    if not status_match:
        fail(f"{display(folder)} result markdown must include a Status marker")
    status = status_match.group(1).strip().upper().replace(" ", "_")
    if status in PLAN_ONLY_STATUSES or status.startswith("UNKNOWN"):
        fail(f"{display(folder)} result markdown status must be reviewed")
    no_positive_claim(text, where=f"result doc {display(result_doc)}")


def resolve_and_validate_artifact(path_value: str, *, expected: Path, label: str, where: str) -> Path:
    if not isinstance(path_value, str):
        fail(f"{where} artifacts.{label} must be a path string")
    resolved = resolve_path(path_value)
    if resolved != expected:
        fail(f"{where} artifacts.{label} must be {expected.name}")
    if not resolved.exists():
        fail(f"{where} artifacts.{label} missing: {display(resolved)}")
    return resolved


def validate_file_set(capture_dir: Path, capture_id: str, payload: dict[str, Any]) -> None:
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict):
        fail(f"{display(capture_dir)} artifacts section missing")

    expected_input = capture_dir / "input_candidate.json"
    expected_output = capture_dir / "output_export.json"
    expected_rejection = capture_dir / "rejection_note.md"
    expected_hashes = capture_dir / "hashes.txt"
    expected_metadata = capture_dir / "metadata.json"
    expected_notes = capture_dir / "notes.md"

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
    )
    output_path: Path | None = None
    if has_output:
        output_path = resolve_and_validate_artifact(
            artifacts.get("output_artifact_path") or payload.get("output_export_path"),
            expected=expected_output,
            label="output_artifact_path",
            where=display(capture_dir),
        )

    metadata_path = artifacts.get("metadata_path")
    if is_unknown(metadata_path) or not isinstance(metadata_path, str):
        fail(f"{display(capture_dir)} artifacts.metadata_path must be filled in reviewed packets")
    resolved_metadata = resolve_path(metadata_path)
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
        metadata_path = resolve_path(metadata_path)
        no_positive_claim(read_text(metadata_path), where=f"metadata {display(metadata_path)}")

    if metadata.get("comparison", {}).get("checker_output_status") not in REVIEWED_STATUSES:
        fail(f"{display(capture_dir)} comparison checker output status must be reviewed")


def list_dated_capture_folders() -> list[Path]:
    if not MANUAL_CAPTURE_DIR.exists():
        fail(f"manual capture directory missing: {display(MANUAL_CAPTURE_DIR)}")
    if not MANUAL_CAPTURE_README.exists():
        fail(f"missing required manual capture README: {display(MANUAL_CAPTURE_README)}")
    capture_folders: list[Path] = []
    allowed_files = {"README.md", ".gitkeep"}
    for entry in sorted(MANUAL_CAPTURE_DIR.iterdir()):
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


def main() -> int:
    print("glyph_official_configurator_manual_capture_result")
    try:
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
