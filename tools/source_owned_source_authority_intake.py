#!/usr/bin/env python3
"""Offline source-authority intake records for source-owned generator v2.

This module records human assertions; it never creates authority, prepares an
artifact, installs source, selects a runtime view, or writes under ``src``.
"""
from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from source_owned_generator_modes import (
    EXIT_CODES as GENERATOR_EXIT_CODES,
    GeneratorModesError,
    _baseline_tables,
    baseline_identity,
    canonical_json,
    digest,
    generate,
    production_gate,
    table_digest,
    validate_input,
    validate_manifest,
)

SCHEMA_VERSION = 1
REPORT_SCHEMA_VERSION = 1
TABLE_COUNT = 28
POINTS_PER_TABLE = 9
EXIT_CODES = dict(GENERATOR_EXIT_CODES)
PLACEHOLDER = "__REQUIRED_HUMAN_VALUE__"
STATUSES = {"draft", "submitted_for_review", "approved", "rejected", "superseded"}
PROVENANCE = {"production_authorized", "source_baseline_derived", "synthetic_test", "example_only", "migrated_legacy", "unknown"}
MODES = {"full_replacement", "overlay_preserve", "reject_partial"}
OPERATIONS = {"production_changeset", "source_equivalence_proof"}

# A review can contain several blocker classes.  Validation must select one
# stable machine exit category without hiding the complete review report.
VALIDATION_CATEGORY_PRECEDENCE = (
    "baseline_mismatch",
    "authority",
    "ownership",
    "candidate_ineligible",
    "integrity",
    "invalid_input",
    "invariant",
)
BLOCKER_CATEGORY_TO_EXIT_CATEGORY = {
    "authority": "source_authority",
    "ownership": "unsafe_unowned_change",
}


class IntakeError(ValueError):
    def __init__(self, message: str, category: str = "invalid_input") -> None:
        super().__init__(message)
        self.category = category


def _fail(message: str, category: str = "invalid_input") -> None:
    raise IntakeError(message, category)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"duplicate JSON key: {key}", "integrity")
        result[key] = value
    return result


def _constant(value: str) -> None:
    _fail(f"non-finite JSON constant is forbidden: {value}", "integrity")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
    except (OSError, json.JSONDecodeError, IntakeError) as exc:
        if isinstance(exc, IntakeError):
            raise
        _fail(f"cannot read JSON {path}: {exc}", "integrity")
    if not isinstance(value, dict):
        _fail("JSON root must be an object")
    return value


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and PLACEHOLDER not in value


def inspect_baseline() -> dict[str, Any]:
    identity = copy.deepcopy(baseline_identity())
    tables = _baseline_tables()
    identity["table_order_digest"] = digest(identity["table_order"])
    identity["table_inventory"] = [
        {"table_id": table["table_id"], "table_symbol": table["table_symbol"], "table_digest": table_digest(table)}
        for table in tables
    ]
    return identity


def create_template() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "intake_id": PLACEHOLDER,
        "profile_id": PLACEHOLDER,
        "profile_name": PLACEHOLDER,
        "purpose": PLACEHOLDER,
        "author": PLACEHOLDER,
        "notes": "Draft only; baseline inventory is reference data, not authorization.",
        "authority": {"status": "draft", "basis": PLACEHOLDER, "approver": PLACEHOLDER, "statement": PLACEHOLDER, "approval_reference": PLACEHOLDER},
        "intent": {"provenance_class": "unknown", "generation_mode": None, "requested_operation": "production_changeset", "controller_scope": "Glyph Mk6", "source_owned_runtime_tables": True},
        "baseline": inspect_baseline(),
        "ownership": {"owned_tables": [], "declarations": [], "unlisted_tables_are_unowned": True},
        "replacements": [],
        "review": {"unresolved_questions": [], "acknowledges_build_not_hardware_proof": False, "acknowledges_separate_hardware_gate": False},
    }


def _block(blockers: list[dict[str, str]], code: str, category: str, path: str, message: str) -> None:
    blockers.append({"code": code, "category": category, "path": path, "message": message})


def select_validation_failure_category(report: dict[str, Any]) -> str | None:
    """Return the stable validation category for a completed review report.

    The order is an explicit CLI contract, rather than an accident of the
    human-oriented deterministic blocker ordering used in the report.
    """
    categories = {blocker.get("category") for blocker in report.get("blockers", [])}
    for category in VALIDATION_CATEGORY_PRECEDENCE:
        if category in categories:
            return BLOCKER_CATEGORY_TO_EXIT_CATEGORY.get(category, category)
    # A completed report with an unknown category is an internal contract
    # violation.  It must never accidentally turn a blocked validation into
    # success merely because a new category was not added to the precedence.
    return "invariant" if categories else None


# Kept as a readable library alias for callers that use the earlier wording.
validation_failure_category = select_validation_failure_category


def _symbols() -> list[str]:
    return inspect_baseline()["table_order"]


def _baseline_problems(value: Any, blockers: list[dict[str, str]]) -> None:
    actual = inspect_baseline()
    if not isinstance(value, dict):
        _block(blockers, "BASELINE_MISSING", "baseline_mismatch", "baseline", "complete baseline identity is required")
        return
    for key in ("baseline_id", "source_path", "source_interpreter", "semantic_digest", "table_count", "table_order", "table_order_digest", "table_inventory"):
        if value.get(key) != actual.get(key):
            _block(blockers, "BASELINE_MISMATCH", "baseline_mismatch", f"baseline.{key}", "baseline does not match the authoritative current source-owned baseline")


def _replacement_symbols(replacements: Any, blockers: list[dict[str, str]]) -> list[str]:
    if not isinstance(replacements, list):
        _block(blockers, "REPLACEMENTS_INVALID", "invalid_input", "replacements", "replacements must be a list")
        return []
    symbols: list[str] = []
    for i, replacement in enumerate(replacements):
        path = f"replacements[{i}]"
        if not isinstance(replacement, dict) or set(replacement) != {"table_symbol", "points", "rationale", "source_reference"}:
            _block(blockers, "REPLACEMENT_SHAPE", "invalid_input", path, "replacement must contain table_symbol, points, rationale, and source_reference only")
            continue
        symbol = replacement.get("table_symbol")
        if not _nonempty(symbol):
            _block(blockers, "REPLACEMENT_SYMBOL", "invalid_input", path + ".table_symbol", "replacement table symbol is required")
        else:
            symbols.append(symbol)
        if not _nonempty(replacement.get("rationale")) or not _nonempty(replacement.get("source_reference")):
            _block(blockers, "REPLACEMENT_AUTHORITY", "authority", path, "each replacement needs a non-placeholder rationale and source reference")
        points = replacement.get("points")
        if not isinstance(points, list) or len(points) != POINTS_PER_TABLE:
            _block(blockers, "POINT_COUNT", "invalid_input", path + ".points", "replacement requires exactly nine ordered directional points")
            continue
        for key, point in enumerate(points, 1):
            if not isinstance(point, dict) or set(point) != {"direction_key", "x", "y"} or point.get("direction_key") != key:
                _block(blockers, "POINT_ORDER", "invalid_input", f"{path}.points[{key - 1}]", "points must use direction_key 1..9 in stable order")
                continue
            for axis in ("x", "y"):
                coordinate = point.get(axis)
                if not isinstance(coordinate, int) or isinstance(coordinate, bool) or not 0 <= coordinate <= 255:
                    _block(blockers, "POINT_COORDINATE", "invalid_input", f"{path}.points[{key - 1}].{axis}", "coordinate must be an integer in [0, 255]")
    return symbols


def review_intake(payload: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    expected = {"schema_version", "intake_id", "profile_id", "profile_name", "purpose", "author", "notes", "authority", "intent", "baseline", "ownership", "replacements", "review"}
    if set(payload) != expected:
        _block(blockers, "TOP_LEVEL_SCHEMA", "invalid_input", "", "intake has missing or unexpected top-level fields")
    if payload.get("schema_version") != SCHEMA_VERSION:
        _block(blockers, "SCHEMA_VERSION", "invalid_input", "schema_version", "unsupported intake schema version")
    for field in ("intake_id", "profile_id", "profile_name", "purpose", "author"):
        if not _nonempty(payload.get(field)):
            _block(blockers, "IDENTITY_REQUIRED", "authority", field, "human-required identity field is missing or placeholder")
    authority = payload.get("authority")
    if not isinstance(authority, dict) or set(authority) != {"status", "basis", "approver", "statement", "approval_reference"}:
        _block(blockers, "AUTHORITY_SHAPE", "invalid_input", "authority", "authority has an invalid shape")
        authority = {}
    status = authority.get("status")
    if status not in STATUSES:
        _block(blockers, "AUTHORITY_STATUS", "authority", "authority.status", "authority status is required and must be explicit")
    if status == "approved":
        for field in ("basis", "approver", "statement", "approval_reference"):
            if not _nonempty(authority.get(field)):
                _block(blockers, "APPROVAL_EVIDENCE", "authority", f"authority.{field}", "approved intake requires non-placeholder approval evidence")
    elif status != "approved":
        _block(blockers, "NOT_APPROVED", "authority", "authority.status", "only an approved packet may emit generator input")
    intent = payload.get("intent")
    if not isinstance(intent, dict) or set(intent) != {"provenance_class", "generation_mode", "requested_operation", "controller_scope", "source_owned_runtime_tables"}:
        _block(blockers, "INTENT_SHAPE", "invalid_input", "intent", "intent has an invalid shape")
        intent = {}
    provenance, mode, operation = intent.get("provenance_class"), intent.get("generation_mode"), intent.get("requested_operation")
    if provenance not in PROVENANCE:
        _block(blockers, "PROVENANCE", "authority", "intent.provenance_class", "provenance class is invalid")
    if mode not in MODES:
        _block(blockers, "GENERATION_MODE", "invalid_input", "intent.generation_mode", "generation mode must be explicit")
    if operation not in OPERATIONS:
        _block(blockers, "OPERATION", "invalid_input", "intent.requested_operation", "requested operation is invalid")
    if intent.get("controller_scope") != "Glyph Mk6" or intent.get("source_owned_runtime_tables") is not True:
        _block(blockers, "SCOPE", "invalid_input", "intent", "intake must explicitly concern Glyph Mk6 source-owned runtime tables")
    _baseline_problems(payload.get("baseline"), blockers)
    ownership = payload.get("ownership")
    if not isinstance(ownership, dict) or set(ownership) != {"owned_tables", "declarations", "unlisted_tables_are_unowned"}:
        _block(blockers, "OWNERSHIP_SHAPE", "invalid_input", "ownership", "ownership has an invalid shape")
        ownership = {}
    owned = ownership.get("owned_tables", [])
    declarations = ownership.get("declarations", [])
    known = _symbols()
    if not isinstance(owned, list) or not all(isinstance(s, str) for s in owned):
        _block(blockers, "OWNERSHIP_LIST", "invalid_input", "ownership.owned_tables", "owned tables must be an explicit list")
        owned = []
    if len(set(owned)) != len(owned): _block(blockers, "DUPLICATE_OWNERSHIP", "ownership", "ownership.owned_tables", "duplicate ownership is forbidden")
    if any(s not in known for s in owned): _block(blockers, "UNKNOWN_OWNERSHIP", "ownership", "ownership.owned_tables", "unknown or wildcard ownership is forbidden")
    if ownership.get("unlisted_tables_are_unowned") is not True:
        _block(blockers, "UNLISTED_NOT_UNOWNED", "ownership", "ownership.unlisted_tables_are_unowned", "unlisted tables must be explicitly unowned")
    declared: list[str] = []
    if not isinstance(declarations, list): _block(blockers, "DECLARATIONS", "invalid_input", "ownership.declarations", "ownership declarations must be a list")
    else:
        for i, item in enumerate(declarations):
            if not isinstance(item, dict) or set(item) != {"table_symbol", "rationale", "authorization_reference"}:
                _block(blockers, "DECLARATION_SHAPE", "invalid_input", f"ownership.declarations[{i}]", "ownership declaration has invalid shape"); continue
            symbol = item.get("table_symbol")
            if isinstance(symbol, str):
                declared.append(symbol)
            if not _nonempty(symbol) or not _nonempty(item.get("rationale")) or not _nonempty(item.get("authorization_reference")):
                _block(blockers, "DECLARATION_EVIDENCE", "authority", f"ownership.declarations[{i}]", "each explicit ownership declaration needs evidence")
    if set(declared) != set(owned) or len(declared) != len(owned): _block(blockers, "DECLARATION_MISMATCH", "ownership", "ownership.declarations", "ownership declarations must match owned tables exactly")
    replacement_symbols = _replacement_symbols(payload.get("replacements"), blockers)
    if len(set(replacement_symbols)) != len(replacement_symbols): _block(blockers, "DUPLICATE_REPLACEMENT", "ownership", "replacements", "duplicate replacement table is forbidden")
    if any(s not in known for s in replacement_symbols): _block(blockers, "UNKNOWN_REPLACEMENT", "ownership", "replacements", "unknown replacement table is forbidden")
    if set(replacement_symbols) != set(owned): _block(blockers, "OWNERSHIP_REPLACEMENT_MISMATCH", "ownership", "replacements", "every owned table must have one replacement and no unowned replacement is allowed")
    review = payload.get("review")
    if not isinstance(review, dict) or set(review) != {"unresolved_questions", "acknowledges_build_not_hardware_proof", "acknowledges_separate_hardware_gate"}:
        _block(blockers, "REVIEW_SHAPE", "invalid_input", "review", "review has invalid shape"); review = {}
    questions = review.get("unresolved_questions", [])
    if not isinstance(questions, list) or any(not isinstance(q, dict) or set(q) != {"question", "blocking"} or not isinstance(q["question"], str) or not isinstance(q["blocking"], bool) for q in questions): _block(blockers, "QUESTIONS", "invalid_input", "review.unresolved_questions", "questions must be {question, blocking: bool} records")
    elif any(q["blocking"] is True for q in questions): _block(blockers, "UNRESOLVED_BLOCKER", "authority", "review.unresolved_questions", "all blocking review questions must be resolved")
    if review.get("acknowledges_build_not_hardware_proof") is not True or review.get("acknowledges_separate_hardware_gate") is not True:
        _block(blockers, "HARDWARE_ACKNOWLEDGEMENT", "authority", "review", "required build/hardware gate acknowledgements are missing")
    if mode == "reject_partial": _block(blockers, "REJECT_PARTIAL", "candidate_ineligible", "intent.generation_mode", "reject_partial cannot emit generator input")
    if operation == "production_changeset":
        if provenance != "production_authorized": _block(blockers, "PRODUCTION_PROVENANCE", "authority", "intent.provenance_class", "production changeset requires production_authorized provenance")
        if mode == "overlay_preserve" and not owned: _block(blockers, "EMPTY_PRODUCTION_CHANGESET", "candidate_ineligible", "ownership", "empty overlay is not a production changeset")
        if mode == "full_replacement" and set(owned) != set(known): _block(blockers, "FULL_REPLACEMENT_OWNERSHIP", "ownership", "ownership", "full replacement requires all 28 explicitly owned tables")
    if operation == "source_equivalence_proof":
        if provenance != "source_baseline_derived" or mode != "overlay_preserve" or owned or replacement_symbols:
            _block(blockers, "EQUIVALENCE_SCOPE", "candidate_ineligible", "intent", "source equivalence is only empty source_baseline_derived overlay")
    if operation == "production_changeset" and isinstance(payload.get("replacements"), list):
        baseline_by_symbol = {table["table_symbol"]: table for table in _baseline_tables()}
        changed = any(
            isinstance(replacement, dict)
            and replacement.get("table_symbol") in baseline_by_symbol
            and isinstance(replacement.get("points"), list)
            and [{"x": point.get("x"), "y": point.get("y")} for point in replacement["points"] if isinstance(point, dict)] != baseline_by_symbol[replacement["table_symbol"]]["points"]
            for replacement in payload["replacements"]
        )
        if not changed:
            _block(blockers, "SEMANTIC_NO_OP", "candidate_ineligible", "replacements", "production changeset must not be a semantic no-op")
    blockers.sort(key=lambda b: (b["category"], b["path"], b["code"]))
    report = {"schema_version": REPORT_SCHEMA_VERSION, "intake_id": payload.get("intake_id"), "authority_status": status, "provenance_class": provenance, "generation_mode": mode, "requested_operation": operation, "baseline_matches_current": not any(b["category"] == "baseline_mismatch" for b in blockers), "owned_table_count": len(owned), "replacement_table_count": len(replacement_symbols), "blockers": blockers}
    report["production_emission_allowed"] = not blockers and operation == "production_changeset"
    report["source_equivalence_emission_allowed"] = not blockers and operation == "source_equivalence_proof"
    report["future_hardware_candidate_after_downstream_gates"] = report["production_emission_allowed"]
    report["semantic_digest"] = digest(report)
    return report


def _require_emit(payload: dict[str, Any], operation: str) -> None:
    report = review_intake(payload)
    permitted = report["production_emission_allowed"] if operation == "production_changeset" else report["source_equivalence_emission_allowed"]
    if not permitted:
        first = report["blockers"][0] if report["blockers"] else {"message": "emission is not allowed", "category": "invalid_input"}
        _fail(first["message"], select_validation_failure_category(report) or "invalid_input")


def emit_generator_input(payload: dict[str, Any], *, operation: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if operation not in OPERATIONS or payload.get("intent", {}).get("requested_operation") != operation:
        _fail("command operation must exactly match intake requested operation", "candidate_ineligible")
    _require_emit(payload, operation)
    intent, baseline = payload["intent"], inspect_baseline()
    known = baseline["table_order"]
    replacements = {r["table_symbol"]: r for r in payload["replacements"]}
    if intent["generation_mode"] == "overlay_preserve":
        tables = [] if operation == "source_equivalence_proof" else [_to_v2(replacements[s], known.index(s)) for s in known if s in replacements]
        # The intake declares ownership explicitly but may be authored in any
        # order.  The v2 wire form is canonicalized solely from that declared
        # set; it never infers additional ownership.
        owned_tables = [symbol for symbol in known if symbol in payload["ownership"]["owned_tables"]]
        value = {"schema_version": 2, "profile_id": payload["profile_id"], "profile_name": payload["profile_name"], "provenance_class": intent["provenance_class"], "generation_mode": "overlay_preserve", "baseline": baseline, "owned_tables": owned_tables, "tables": tables, "metadata": {"intake_id": payload["intake_id"], "authorization_reference": payload["authority"]["approval_reference"]}}
    else:
        value = {"schema_version": 2, "profile_id": payload["profile_id"], "profile_name": payload["profile_name"], "provenance_class": intent["provenance_class"], "generation_mode": "full_replacement", "baseline": baseline, "tables": [_to_v2(replacements[s], known.index(s)) for s in known], "metadata": {"intake_id": payload["intake_id"], "authorization_reference": payload["authority"]["approval_reference"]}}
    normalized = validate_input(value)
    artifact, manifest = generate(normalized)
    validate_manifest(artifact, manifest)
    production_gate(artifact, manifest)
    if operation == "production_changeset" and manifest["classification"] == "NO_OP": _fail("production changeset must not emit a semantic no-op", "candidate_ineligible")
    if operation == "source_equivalence_proof" and manifest["classification"] != "NO_OP": _fail("source equivalence must be a semantic no-op", "candidate_ineligible")
    # Return the authored v2 wire shape.  ``validate_input`` normalizes an
    # omitted full-replacement ownership list to ``[]`` internally, but the
    # emitted JSON deliberately omits it because v2 treats it as implicit.
    return value, artifact, manifest


def _to_v2(replacement: dict[str, Any], table_id: int) -> dict[str, Any]:
    return {"table_id": table_id, "table_symbol": replacement["table_symbol"], "points": [{"x": p["x"], "y": p["y"]} for p in replacement["points"]]}


def assert_safe_offline_output_path(path: Path, *, input_path: Path | None = None) -> Path:
    if not path.is_absolute(): _fail("output path must be absolute", "integrity")
    resolved = path.resolve(strict=False)
    root = Path(__file__).resolve().parents[1]
    try:
        relative_parts = resolved.relative_to(root).parts
    except ValueError:
        relative_parts = ()
    protected_components = {"src", "include", "lib", "hal", "backend", ".git"}
    for component in relative_parts:
        if component.casefold() in protected_components:
            _fail(f"output path under protected {component}/** is forbidden", "source_authority")
    if input_path and resolved == input_path.resolve(strict=False): _fail("output path must not overwrite intake input", "integrity")
    resolved_casefolded = str(resolved).casefold()
    for forbidden in ("candidate.view", "active_storage.view", "runtimeconfigview"):
        if forbidden in resolved_casefolded: _fail("forbidden active publication path", "source_authority")
    return resolved


def write_json(path: Path, value: dict[str, Any], *, input_path: Path | None = None) -> None:
    target = assert_safe_offline_output_path(path, input_path=input_path)
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, target)
    except OSError as exc:
        try: os.unlink(temporary)
        except OSError: pass
        _fail(f"atomic offline write failed: {exc}", "integrity")


def render_review_markdown(report: dict[str, Any]) -> str:
    lines = ["# Source-authority intake review", "", f"- Intake: `{report.get('intake_id')}`", f"- Authority status: `{report.get('authority_status')}`", f"- Production emission allowed: `{report.get('production_emission_allowed')}`", f"- Source-equivalence emission allowed: `{report.get('source_equivalence_emission_allowed')}`", "", "## Blockers", ""]
    lines.extend([f"- `{b['code']}` at `{b['path']}`: {b['message']}" for b in report["blockers"]] or ["- None."])
    return "\n".join(lines) + "\n"
