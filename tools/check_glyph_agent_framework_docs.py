#!/usr/bin/env python3
"""Validate Glyph agent framework documentation surface."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = (
    "AGENTS.md",
    "docs/agent_framework/README.md",
    "docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md",
    "docs/agent_framework/WORK_ORDER_TEMPLATE.md",
    "docs/agent_framework/HARDWARE_EVIDENCE.md",
    "docs/agent_framework/USER_DIRECTION.md",
    "docs/agent_framework/SCHEDULED_TASKS.md",
    "docs/agent_framework/MODEL_ROUTING.md",
    "docs/agent_framework/SUPERVISOR_CONTRACT.md",
    "docs/agent_framework/SUBAGENT_CONTRACTS.md",
    "docs/agent_framework/CYCLE_STATE_MACHINE.md",
    "docs/agent_framework/JUDGE_WATCHDOG_CONTRACT.md",
    "docs/agent_framework/VALIDATION_AND_GATES.md",
    "docs/agent_framework/STATUS_DOC_CONTRACT.md",
    "docs/agent_framework/PROMPT_TEMPLATES.md",
    "docs/agent_framework/RUNNER_BOUNDARY.md",
    "docs/agent_framework/model_routing.v0.json",
    "docs/agent_framework/examples/example_supervisor_cycle_request.md",
    "docs/agent_framework/examples/example_subagent_handoff.md",
    "docs/agent_framework/examples/example_cycle_report.md",
    "docs/project/ACTIVE_AGENT_QUEUE.md",
    "docs/project/AGENTS.md",
    "docs/project/AGENT_OPERATING_CONTRACT.md",
    "docs/project/AGENT_PROMPT_TEMPLATES.md",
    "docs/project/CODEX_CLOUD_WORKFLOW.md",
    "docs/project/CODEX_WORKFLOW.md",
)

REQUIRED_SCHEMAS = (
    "docs/agent_framework/schemas/branch_contract.schema.json",
    "docs/agent_framework/schemas/subagent_handoff.schema.json",
    "docs/agent_framework/schemas/cycle_report.schema.json",
    "docs/agent_framework/schemas/model_routing.schema.json",
)

REQUIRED_ROLES = (
    "supervisor",
    "planner",
    "curator",
    "architecture_specialist",
    "implementer",
    "validator_reviewer",
    "hardware_evidence_processor",
    "docs_status_clerk",
    "judge_watchdog",
)

MODEL_ROUTING_FIELDS = (
    "role",
    "default_model",
    "default_reasoning_effort",
    "escalation_model",
    "escalation_reasoning_effort",
    "escalation_triggers",
    "deescalation_triggers",
    "output_contract",
    "tool_permission_posture",
)

BRANCH_CLASSIFICATIONS = (
    "DOCS_CHECKER_ONLY",
    "INACTIVE_GENERATOR_OR_FIXTURE",
    "FIRMWARE_SOURCE_NON_ACTIVE",
    "FIRMWARE_SOURCE_ACTIVE_BEHAVIOR",
    "FORBIDDEN_OR_UNSAFE",
)

JUDGE_VERDICTS = (
    "DONE",
    "CONTINUE",
    "BLOCKED",
    "NEEDS_HARDWARE",
    "UNSAFE",
    "LOOPING",
)

NON_CODEX_TERMS = (
    "CLAUDE.md",
    ".claude",
    "Claude Code",
    "Claude",
    "Anthropic",
    "Opus",
    "Sonnet",
    "Haiku",
)

BAD_ACTIVE_CLAIMS = (
    "candidate.view is active",
    "active_storage.view is active",
    "generated active runtimeconfigview wrapper is active",
    "ram-backed active table publication is used",
    "runtime-loaded config is implemented",
    "runtime-loaded profiles are implemented",
    "webserial/device write is implemented",
    "protobuf binary write is implemented",
    "backend config.pb write is implemented",
    "persistent runtime-config storage is implemented",
    "flashing automation is implemented",
    "nunchuk was tested",
    "nunchuk is tested",
    "root cause is proven",
)

SAFE_NEGATION_MARKERS = (
    "do not",
    "does not",
    "not ",
    "no ",
    "without",
    "unless",
    "forbidden",
    "stop",
    "would claim",
    "remains unproven",
    "remains not_tested",
    "is not implemented",
)

QUEUE_START = "<!-- queue-state:start -->"
QUEUE_END = "<!-- queue-state:end -->"

QUEUE_STATUSES = {
    "READY",
    "PREAUTHORIZED",
    "IN_PROGRESS",
    "REVIEW",
    "HARDWARE_TEST_REQUIRED",
    "LOCAL_ACCEPTANCE_PENDING",
    "HARDWARE_VALIDATED",
    "HARDWARE_FAILED",
    "BLOCKED_EXTERNAL",
    "DONE",
    "INVALIDATED_PREAUTHORIZED",
}

WORK_ORDER_FIELDS = (
    "id",
    "title",
    "status",
    "branch",
    "objective",
    "why_this_matters",
    "hardware_risk",
    "behavioral_claim",
    "scope",
    "explicit_excluded_scope",
    "touched_planes",
    "source_authority",
    "dependencies_prerequisites",
    "substantive_authorization_rationale",
    "mechanical_activation_conditions",
    "invalidation_conditions",
    "authorization_snapshot_provenance",
    "automated_validation",
    "canonical_build",
    "expected_artifact",
    "manual_acceptance",
    "manual_acceptance_protocol_reference",
    "rollback_recovery",
    "status_documentation_updates",
    "done_evidence",
    "stop_conditions",
    "activation_state",
    "activation_requires_new_judgment",
    "hardware_evidence_dependency_satisfied",
    "candidate_git_sha",
    "candidate_base_configurator_sha",
    "firmware_artifact_build_path",
    "preserved_firmware_artifact_locator",
    "firmware_artifact_sha256",
    "hardware_evidence_record",
    "hardware_result",
    "hardware_evidence_gaps",
)

RUNWAY_FIELDS = (
    "immediate_ready",
    "recorded_preauthorized",
    "mechanically_activatable_preauthorized",
    "invalidated_preauthorized",
    "hardware_pending",
    "effective_authorized_runway",
    "target_effective_authorized_runway",
    "target_provenance",
)

PRIMARY_LIVENESS_SIGNALS = {
    "RUNWAY_OK",
    "RUNWAY_LOW",
    "PLANNING_REQUIRED",
    "CURATION_REQUIRED",
    "GLOBAL_EVIDENCE_WAIT_SUPPORTED",
}

SUPPORTING_SIGNALS = {
    "RUNWAY_SHORTFALL_CANDIDATE_SUPPLY",
    "RUNWAY_SHORTFALL_EVIDENCE_GATED",
    "RUNWAY_SHORTFALL_USER_DECISION_GATED",
    "RUNWAY_SHORTFALL_SUBSTANTIVE_DEPENDENCY",
    "RUNWAY_SHORTFALL_RESEARCH_GATED",
    "PLANNER_REFRESH_REQUIRED",
    "HARDWARE_TEST_REQUIRED",
    "REPAIR_REQUIRED",
}


class FrameworkDocsError(AssertionError):
    """Raised when framework docs drift from the contract."""


def fail(message: str) -> None:
    raise FrameworkDocsError(message)


def pass_line(message: str) -> None:
    print(f"PASS: {message}")


def read_required(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        fail(f"missing required path: {rel_path}")
    return path.read_text(encoding="utf-8")


def load_json(rel_path: str) -> object:
    try:
        return json.loads(read_required(rel_path))
    except json.JSONDecodeError as exc:
        fail(f"{rel_path} is not valid JSON: {exc}")


def normalize(text: str) -> str:
    return " ".join(text.replace("`", "").split()).lower()


def load_queue_state() -> dict[str, object]:
    text = read_required("docs/project/ACTIVE_AGENT_QUEUE.md")
    if text.count(QUEUE_START) != 1 or text.count(QUEUE_END) != 1:
        fail("ACTIVE_AGENT_QUEUE.md must contain exactly one machine-readable state block")
    block = text.split(QUEUE_START, 1)[1].split(QUEUE_END, 1)[0].strip()
    if not block.startswith("```json") or not block.endswith("```"):
        fail("ACTIVE_AGENT_QUEUE.md state block must be fenced JSON")
    raw_json = block[len("```json") : -len("```")].strip()
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        fail(f"ACTIVE_AGENT_QUEUE.md state block is not valid JSON: {exc}")
    if not isinstance(payload, dict):
        fail("ACTIVE_AGENT_QUEUE.md state block must be a JSON object")
    return payload


def require_nonempty_string(value: object, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"queue work order field {field} must be a non-empty string")


def validate_work_order(item: object) -> dict[str, object]:
    if not isinstance(item, dict):
        fail("queue items must be JSON objects")
    missing = [field for field in WORK_ORDER_FIELDS if field not in item]
    if missing:
        fail("queue work order missing fields: " + ", ".join(missing))

    for field in (
        "id",
        "title",
        "branch",
        "objective",
        "why_this_matters",
        "behavioral_claim",
        "scope",
        "explicit_excluded_scope",
        "source_authority",
        "substantive_authorization_rationale",
        "authorization_snapshot_provenance",
        "canonical_build",
        "expected_artifact",
        "manual_acceptance_protocol_reference",
        "rollback_recovery",
        "status_documentation_updates",
        "done_evidence",
    ):
        require_nonempty_string(item[field], field)

    status = item["status"]
    if status not in QUEUE_STATUSES:
        fail(f"queue work order has invalid status: {status!r}")
    if item["hardware_risk"] not in {"H0", "H1", "H2", "H3"}:
        fail("queue work order hardware_risk must be H0, H1, H2, or H3")
    if item["manual_acceptance"] not in {"NOT_REQUIRED", "REQUIRED"}:
        fail("queue work order manual_acceptance must be NOT_REQUIRED or REQUIRED")

    for field in (
        "touched_planes",
        "dependencies_prerequisites",
        "mechanical_activation_conditions",
        "invalidation_conditions",
        "automated_validation",
        "stop_conditions",
    ):
        value = item[field]
        if not isinstance(value, list) or not all(
            isinstance(entry, str) and entry.strip() for entry in value
        ):
            fail(f"queue work order field {field} must be a string list")

    evidence_gaps = item["hardware_evidence_gaps"]
    if not isinstance(evidence_gaps, list) or not all(
        isinstance(entry, str) and entry.strip() for entry in evidence_gaps
    ):
        fail("queue work order hardware_evidence_gaps must be a non-blank string list")
    for field in (
        "candidate_git_sha",
        "candidate_base_configurator_sha",
        "firmware_artifact_build_path",
        "preserved_firmware_artifact_locator",
        "firmware_artifact_sha256",
        "hardware_evidence_record",
        "hardware_result",
    ):
        if item[field] is not None and (
            not isinstance(item[field], str) or not item[field].strip()
        ):
            fail(f"queue work order field {field} must be null or a non-empty string")
    if item["hardware_result"] not in {None, "PASS", "FAIL", "PARTIAL", "INCONCLUSIVE"}:
        fail("queue work order hardware_result is invalid")

    if status in {"READY", "PREAUTHORIZED"}:
        for field in ("touched_planes", "automated_validation", "stop_conditions"):
            if not item[field]:
                fail(f"{status} work requires non-empty {field}")

    activation_state = item["activation_state"]
    if activation_state not in {
        "NOT_APPLICABLE",
        "WAITING",
        "ACTIVATABLE",
        "HARDWARE_PENDING",
        "INVALIDATED",
    }:
        fail(f"queue work order has invalid activation_state: {activation_state!r}")
    if not isinstance(item["activation_requires_new_judgment"], bool):
        fail("activation_requires_new_judgment must be boolean")
    hardware_dependency = item["hardware_evidence_dependency_satisfied"]
    if hardware_dependency is not None and not isinstance(hardware_dependency, bool):
        fail("hardware_evidence_dependency_satisfied must be true, false, or null")

    if status == "PREAUTHORIZED":
        if not item["mechanical_activation_conditions"]:
            fail("Preauthorized work requires mechanical activation conditions")
        if not item["invalidation_conditions"]:
            fail("Preauthorized work requires invalidation conditions")
        if activation_state not in {"WAITING", "ACTIVATABLE", "HARDWARE_PENDING"}:
            fail("Preauthorized work requires WAITING, ACTIVATABLE, or HARDWARE_PENDING")
        if activation_state == "ACTIVATABLE" and (
            item["activation_requires_new_judgment"] is not False
            or hardware_dependency is False
        ):
            fail("ACTIVATABLE Preauthorization cannot require judgment or missing evidence")
        if activation_state == "HARDWARE_PENDING" and hardware_dependency is not False:
            fail("HARDWARE_PENDING Preauthorization requires unsatisfied hardware evidence")
    elif status == "READY":
        if activation_state != "NOT_APPLICABLE":
            fail("READY requires activation_state NOT_APPLICABLE")
        if item["activation_requires_new_judgment"] is not False:
            fail("READY cannot require new judgment")
        if hardware_dependency is False:
            fail("READY cannot have an unsatisfied hardware evidence dependency")
        if item["mechanical_activation_conditions"]:
            fail("READY must not carry Preauthorization activation conditions")
    elif status == "INVALIDATED_PREAUTHORIZED":
        if activation_state != "INVALIDATED":
            fail("INVALIDATED_PREAUTHORIZED requires activation_state INVALIDATED")
        if item["activation_requires_new_judgment"] is not True:
            fail("INVALIDATED_PREAUTHORIZED requires new substantive judgment")

    identity_statuses = {
        "HARDWARE_TEST_REQUIRED",
        "LOCAL_ACCEPTANCE_PENDING",
        "HARDWARE_VALIDATED",
        "HARDWARE_FAILED",
    }
    if status in identity_statuses:
        if item["hardware_risk"] not in {"H2", "H3"}:
            fail(f"{status} is reserved for H2/H3 work")
        for field in ("candidate_git_sha", "candidate_base_configurator_sha"):
            value = item[field]
            if not isinstance(value, str) or len(value) != 40 or any(
                char not in "0123456789abcdef" for char in value
            ):
                fail(f"{status} requires full lowercase {field}")
        artifact_hash = item["firmware_artifact_sha256"]
        if not isinstance(artifact_hash, str) or len(artifact_hash) != 64 or any(
            char not in "0123456789abcdef" for char in artifact_hash
        ):
            fail(f"{status} requires a full lowercase firmware artifact SHA-256")
        for field in (
            "firmware_artifact_build_path",
            "preserved_firmware_artifact_locator",
        ):
            require_nonempty_string(item[field], field)
        locator = item["preserved_firmware_artifact_locator"]
        build_path = item["firmware_artifact_build_path"]
        if locator == build_path or locator.startswith(".pio/") or "/.pio/" in locator:
            fail(f"{status} preserved artifact locator cannot be mutable .pio output")
        if item["candidate_git_sha"] not in locator or artifact_hash not in locator:
            fail(
                f"{status} preserved artifact locator must be addressed by candidate and artifact SHA"
            )
        if item["hardware_evidence_dependency_satisfied"] is not False and status in {
            "HARDWARE_TEST_REQUIRED",
            "LOCAL_ACCEPTANCE_PENDING",
            "HARDWARE_FAILED",
        }:
            fail(f"{status} requires unsatisfied hardware evidence dependency")
    if status == "HARDWARE_VALIDATED":
        if item["hardware_result"] != "PASS":
            fail("HARDWARE_VALIDATED requires hardware_result PASS")
        if item["hardware_evidence_dependency_satisfied"] is not True:
            fail("HARDWARE_VALIDATED requires satisfied hardware evidence dependency")
        require_nonempty_string(item["hardware_evidence_record"], "hardware_evidence_record")
        if evidence_gaps:
            fail("HARDWARE_VALIDATED cannot retain hardware evidence gaps")
    elif status == "HARDWARE_FAILED":
        if item["hardware_result"] != "FAIL":
            fail("HARDWARE_FAILED requires hardware_result FAIL")
        require_nonempty_string(item["hardware_evidence_record"], "hardware_evidence_record")
    elif status == "LOCAL_ACCEPTANCE_PENDING":
        if item["hardware_result"] not in {None, "PARTIAL", "INCONCLUSIVE"}:
            fail("LOCAL_ACCEPTANCE_PENDING result must be null, PARTIAL, or INCONCLUSIVE")
        if item["hardware_result"] is not None:
            require_nonempty_string(
                item["hardware_evidence_record"], "hardware_evidence_record"
            )
            if not evidence_gaps:
                fail("PARTIAL/INCONCLUSIVE hardware result requires exact evidence gaps")
    elif status == "HARDWARE_TEST_REQUIRED" and item["hardware_result"] is not None:
        fail("HARDWARE_TEST_REQUIRED requires hardware_result null before testing")

    if item["hardware_risk"] in {"H2", "H3"} and item["manual_acceptance"] != "REQUIRED":
        fail("H2/H3 work orders require manual acceptance")
    return item


def is_activatable_preauthorized(item: dict[str, object]) -> bool:
    return (
        item["status"] == "PREAUTHORIZED"
        and item["activation_state"] == "ACTIVATABLE"
        and item["activation_requires_new_judgment"] is False
        and (
            item["hardware_evidence_dependency_satisfied"] is True
            or item["hardware_evidence_dependency_satisfied"] is None
        )
        and bool(item["mechanical_activation_conditions"])
        and bool(item["invalidation_conditions"])
        and all(
            isinstance(entry, str) and entry.strip()
            for entry in item["mechanical_activation_conditions"]
        )
        and all(
            isinstance(entry, str) and entry.strip()
            for entry in item["invalidation_conditions"]
        )
    )


def derive_liveness(
    *,
    effective_runway: int,
    target_runway: int,
    packet_state: str,
    substantive_candidate_exists: bool,
    invalidated_authorization_exists: bool,
    failed_hardware_exists: bool,
    curator_review_required: bool,
    global_wait_supported: bool,
) -> str:
    if global_wait_supported:
        return "GLOBAL_EVIDENCE_WAIT_SUPPORTED"
    if effective_runway > 0:
        return "RUNWAY_LOW" if effective_runway < target_runway else "RUNWAY_OK"
    if invalidated_authorization_exists or failed_hardware_exists or curator_review_required:
        return "CURATION_REQUIRED"
    if packet_state in {"ABSENT", "STALE", "CONSUMED"}:
        return "PLANNING_REQUIRED"
    if substantive_candidate_exists:
        return "CURATION_REQUIRED"
    return "PLANNING_REQUIRED"


def require_phrase(rel_path: str, phrase: str) -> None:
    text = read_required(rel_path)
    if normalize(phrase) not in normalize(text):
        fail(f"{rel_path} missing required phrase: {phrase}")


def framework_paths() -> list[Path]:
    return [
        path
        for path in (REPO_ROOT / "docs/agent_framework").rglob("*")
        if path.is_file() and path.suffix in {".md", ".json"}
    ]


def active_framework_text() -> str:
    parts = [path.read_text(encoding="utf-8") for path in framework_paths()]
    parts.append(read_required("AGENTS.md"))
    return "\n".join(parts)


def check_required_paths() -> None:
    for rel_path in REQUIRED_DOCS:
        read_required(rel_path)
    for rel_path in REQUIRED_SCHEMAS:
        load_json(rel_path)
    pass_line("required docs and JSON schemas exist and parse")


def check_codex_only_surface() -> None:
    if (REPO_ROOT / "CLAUDE.md").exists():
        fail("CLAUDE.md must not exist for current Codex/OpenAI-only workflow")
    if (REPO_ROOT / ".claude" / "agents").exists():
        fail(".claude/agents must not exist for current Codex/OpenAI-only workflow")
    bad: list[str] = []
    for path in framework_paths() + [REPO_ROOT / "AGENTS.md"]:
        text = path.read_text(encoding="utf-8")
        for term in NON_CODEX_TERMS:
            if term in text:
                bad.append(f"{path.relative_to(REPO_ROOT)} contains {term}")
    if bad:
        fail("non-Codex active workflow references found: " + "; ".join(bad))
    pass_line("current framework surface is Codex/OpenAI-only")


def check_model_routing() -> None:
    routing = load_json("docs/agent_framework/model_routing.v0.json")
    if not isinstance(routing, dict):
        fail("model_routing.v0.json must be an object")
    roles = routing.get("roles")
    if not isinstance(roles, dict):
        fail("model_routing.v0.json must contain roles object")
    missing = [role for role in REQUIRED_ROLES if role not in roles]
    if missing:
        fail("model_routing.v0.json missing roles: " + ", ".join(missing))
    for role in REQUIRED_ROLES:
        role_entry = roles[role]
        if not isinstance(role_entry, dict):
            fail(f"model_routing role {role} must be an object")
        missing_fields = [field for field in MODEL_ROUTING_FIELDS if field not in role_entry]
        if missing_fields:
            fail(f"model_routing role {role} missing fields: {', '.join(missing_fields)}")
        if role_entry.get("role") != role:
            fail(f"model_routing role field mismatch for {role}")
        for forbidden_field in ("claude_default", "claude_effort", "anthropic_default"):
            if forbidden_field in role_entry:
                fail(f"model_routing role {role} contains non-Codex field: {forbidden_field}")
    pass_line("model routing includes all required Codex/OpenAI roles and fields")


def check_queue_contract() -> None:
    payload = load_queue_state()
    if payload.get("schema_version") != 2:
        fail("queue schema_version must be 2")
    if payload.get("canonical_branch") != "configurator":
        fail("queue canonical_branch must be configurator")
    require_nonempty_string(payload.get("audit_base_sha"), "audit_base_sha")
    audit_base_sha = payload["audit_base_sha"]
    if len(audit_base_sha) != 40 or any(char not in "0123456789abcdef" for char in audit_base_sha):
        fail("queue audit_base_sha must be a full lowercase Git SHA")
    require_nonempty_string(payload.get("operating_mode"), "operating_mode")

    planner_packet = payload.get("planner_packet")
    if not isinstance(planner_packet, dict):
        fail("queue planner_packet must be an object")
    packet_state = planner_packet.get("state")
    if packet_state not in {"ABSENT", "FRESH", "PARTIALLY_CONSUMED", "STALE", "CONSUMED"}:
        fail(f"queue planner packet has invalid state: {packet_state!r}")
    candidate_count = planner_packet.get("candidate_count")
    if not isinstance(candidate_count, int) or candidate_count < 0:
        fail("queue planner_packet.candidate_count must be a non-negative integer")
    events = planner_packet.get("material_events_since_packet")
    if not isinstance(events, list) or not all(
        isinstance(event, str) and event.strip() for event in events
    ):
        fail("queue planner packet material events must be a string list")
    curator_review_required = planner_packet.get("curator_review_required")
    global_wait_proposed = planner_packet.get("global_wait_proposed")
    if not isinstance(curator_review_required, bool):
        fail("queue planner_packet.curator_review_required must be boolean")
    if not isinstance(global_wait_proposed, bool):
        fail("queue planner_packet.global_wait_proposed must be boolean")
    packet_branch = planner_packet.get("branch")
    packet_base_sha = planner_packet.get("base_configurator_sha")
    if packet_state == "ABSENT":
        if (
            packet_branch is not None
            or packet_base_sha is not None
            or candidate_count != 0
            or events
            or curator_review_required
            or global_wait_proposed
        ):
            fail("ABSENT Planner packet must have null/zero/false packet state")
    else:
        if not isinstance(packet_branch, str) or not packet_branch.startswith("planning/portfolio-"):
            fail("recorded Planner packet branch must use planning/portfolio-* convention")
        if (
            not isinstance(packet_base_sha, str)
            or len(packet_base_sha) != 40
            or any(char not in "0123456789abcdef" for char in packet_base_sha)
        ):
            fail("recorded Planner packet requires a full lowercase base configurator SHA")
    if packet_state == "FRESH" and events:
        fail("FRESH Planner packet cannot record material events since publication")
    if packet_state in {"PARTIALLY_CONSUMED", "STALE", "CONSUMED"} and not events:
        fail("consumed/stale Planner packet state requires a material event")
    if packet_state == "PARTIALLY_CONSUMED" and candidate_count == 0:
        fail("PARTIALLY_CONSUMED Planner packet requires surviving candidates")
    if packet_state in {"STALE", "CONSUMED"} and (
        curator_review_required or global_wait_proposed
    ):
        fail("stale/consumed Planner packet cannot await Curator or propose global wait")
    if global_wait_proposed and packet_state not in {"FRESH", "PARTIALLY_CONSUMED"}:
        fail("global wait proposal requires a current useful Planner packet")

    items_raw = payload.get("items")
    if not isinstance(items_raw, list):
        fail("queue items must be a list")
    items = [validate_work_order(item) for item in items_raw]
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        fail("queue work-order IDs must be unique")

    computed = {
        "immediate_ready": sum(item["status"] == "READY" for item in items),
        "recorded_preauthorized": sum(item["status"] == "PREAUTHORIZED" for item in items),
        "mechanically_activatable_preauthorized": sum(
            is_activatable_preauthorized(item) for item in items
        ),
        "invalidated_preauthorized": sum(
            item["status"] == "INVALIDATED_PREAUTHORIZED"
            or (item["status"] == "PREAUTHORIZED" and item["activation_state"] == "INVALIDATED")
            for item in items
        ),
        "hardware_pending": sum(
            item["status"] in {"HARDWARE_TEST_REQUIRED", "LOCAL_ACCEPTANCE_PENDING"}
            or (item["status"] == "PREAUTHORIZED" and item["activation_state"] == "HARDWARE_PENDING")
            for item in items
        ),
        "hardware_failed": sum(item["status"] == "HARDWARE_FAILED" for item in items),
    }
    computed["effective_authorized_runway"] = (
        computed["immediate_ready"] + computed["mechanically_activatable_preauthorized"]
    )

    runway = payload.get("runway")
    if not isinstance(runway, dict):
        fail("queue runway must be an object")
    missing_runway = [field for field in RUNWAY_FIELDS if field not in runway]
    if missing_runway:
        fail("queue runway missing fields: " + ", ".join(missing_runway))
    for field, expected in computed.items():
        if field == "hardware_failed":
            continue
        if runway.get(field) != expected:
            fail(f"queue runway {field} must be {expected}, found {runway.get(field)!r}")
    target_runway = runway.get("target_effective_authorized_runway")
    if not isinstance(target_runway, int) or isinstance(target_runway, bool) or target_runway < 1:
        fail("queue runway target_effective_authorized_runway must be a positive integer")
    require_nonempty_string(runway.get("target_provenance"), "target_provenance")

    signals = payload.get("signals")
    if not isinstance(signals, list) or not all(isinstance(signal, str) for signal in signals):
        fail("queue signals must be a string list")
    if len(signals) != len(set(signals)):
        fail("queue signals must not contain duplicates")
    unknown_signals = set(signals) - PRIMARY_LIVENESS_SIGNALS - SUPPORTING_SIGNALS
    if unknown_signals:
        fail("queue contains unknown signals: " + ", ".join(sorted(unknown_signals)))
    global_wait = payload.get("global_evidence_wait")
    if not isinstance(global_wait, dict) or not isinstance(global_wait.get("supported"), bool):
        fail("queue global_evidence_wait must contain boolean supported")
    if global_wait["supported"]:
        if packet_state != "FRESH":
            fail("global evidence wait requires a fresh broad Planner packet")
        if computed["effective_authorized_runway"] != 0:
            fail("global evidence wait requires zero effective authorized runway")
        if computed["invalidated_preauthorized"] or computed["hardware_failed"]:
            fail("global evidence wait cannot bypass invalidated or failed work")
        if not global_wait_proposed or curator_review_required:
            fail("global evidence wait requires a proposed packet accepted by Curator")
        for field in (
            "planner_broad_audit_provenance",
            "curator_acceptance_provenance",
            "required_external_evidence",
            "resume_event",
        ):
            require_nonempty_string(global_wait.get(field), field)
        if "GLOBAL_EVIDENCE_WAIT_SUPPORTED" not in signals:
            fail("accepted global evidence wait must be reported in queue signals")
    else:
        for field in (
            "planner_broad_audit_provenance",
            "curator_acceptance_provenance",
            "required_external_evidence",
            "resume_event",
        ):
            if global_wait.get(field) is not None:
                fail("unsupported global evidence wait must have null provenance")
        if packet_state == "FRESH" and not curator_review_required:
            fail("unaccepted FRESH Planner packet must require Curator review")

    expected_liveness = derive_liveness(
        effective_runway=computed["effective_authorized_runway"],
        target_runway=target_runway,
        packet_state=packet_state,
        substantive_candidate_exists=bool(candidate_count),
        invalidated_authorization_exists=bool(computed["invalidated_preauthorized"]),
        failed_hardware_exists=bool(computed["hardware_failed"]),
        curator_review_required=curator_review_required,
        global_wait_supported=global_wait["supported"],
    )
    actual_primary = set(signals) & PRIMARY_LIVENESS_SIGNALS
    if actual_primary != {expected_liveness}:
        fail(
            "queue must contain exactly derived primary liveness "
            f"{expected_liveness}; found {sorted(actual_primary)}"
        )
    if expected_liveness == "PLANNING_REQUIRED" and packet_state in {"ABSENT", "STALE", "CONSUMED"}:
        if "PLANNER_REFRESH_REQUIRED" not in signals:
            fail("zero runway plus absent/stale/consumed packet requires PLANNER_REFRESH_REQUIRED")
    if computed["hardware_pending"] and "HARDWARE_TEST_REQUIRED" not in signals:
        fail("hardware-pending work requires HARDWARE_TEST_REQUIRED supporting signal")
    if computed["hardware_failed"] and "REPAIR_REQUIRED" not in signals:
        fail("HARDWARE_FAILED work requires REPAIR_REQUIRED supporting signal")

    adversarial_cases = (
        (0, 4, "CONSUMED", True, False, False, False, False, "PLANNING_REQUIRED"),
        (0, 4, "FRESH", True, False, False, True, False, "CURATION_REQUIRED"),
        (0, 4, "FRESH", False, False, False, False, True, "GLOBAL_EVIDENCE_WAIT_SUPPORTED"),
        (0, 4, "ABSENT", False, True, False, False, False, "CURATION_REQUIRED"),
        (0, 4, "ABSENT", False, False, True, False, False, "CURATION_REQUIRED"),
        (1, 4, "CONSUMED", False, False, False, False, False, "RUNWAY_LOW"),
        (4, 4, "CONSUMED", False, False, False, False, False, "RUNWAY_OK"),
    )
    for effective, target, state, candidate, invalidated, failed, review, wait, expected in adversarial_cases:
        actual = derive_liveness(
            effective_runway=effective,
            target_runway=target,
            packet_state=state,
            substantive_candidate_exists=candidate,
            invalidated_authorization_exists=invalidated,
            failed_hardware_exists=failed,
            curator_review_required=review,
            global_wait_supported=wait,
        )
        if actual != expected:
            fail(f"liveness derivation returned {actual}, expected {expected}")

    activatable_example: dict[str, object] = {
        "status": "PREAUTHORIZED",
        "activation_state": "ACTIVATABLE",
        "activation_requires_new_judgment": False,
        "hardware_evidence_dependency_satisfied": None,
        "mechanical_activation_conditions": ["named prerequisite exists"],
        "invalidation_conditions": ["semantic invariant changed"],
    }
    if not is_activatable_preauthorized(activatable_example):
        fail("valid mechanical Preauthorization must count as activatable")
    blank_condition = dict(activatable_example)
    blank_condition["mechanical_activation_conditions"] = [""]
    if is_activatable_preauthorized(blank_condition):
        fail("blank Preauthorization condition must not count as activatable")
    for field, value in (
        ("activation_state", "HARDWARE_PENDING"),
        ("activation_state", "INVALIDATED"),
        ("activation_requires_new_judgment", True),
        ("hardware_evidence_dependency_satisfied", False),
    ):
        variant = dict(activatable_example)
        variant[field] = value
        if is_activatable_preauthorized(variant):
            fail(f"Preauthorization with {field}={value!r} must not be activatable")

    ready_example: dict[str, object] = {
        "id": "TEST-READY",
        "title": "checker adversarial fixture",
        "status": "READY",
        "branch": "test/ready",
        "objective": "exercise the queue validator",
        "why_this_matters": "prevent fail-open runway",
        "hardware_risk": "H0",
        "behavioral_claim": "none",
        "scope": "checker fixture",
        "explicit_excluded_scope": "product code",
        "touched_planes": ["docs/checkers"],
        "source_authority": "this checker contract",
        "dependencies_prerequisites": [],
        "substantive_authorization_rationale": "adversarial self-test",
        "mechanical_activation_conditions": [],
        "invalidation_conditions": [],
        "authorization_snapshot_provenance": "internal checker fixture",
        "automated_validation": ["this checker"],
        "canonical_build": "NOT_APPLICABLE",
        "expected_artifact": "NOT_APPLICABLE",
        "manual_acceptance": "NOT_REQUIRED",
        "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
        "rollback_recovery": "discard fixture",
        "status_documentation_updates": "none",
        "done_evidence": "validator accepts valid shape",
        "stop_conditions": ["unexpected acceptance"],
        "activation_state": "NOT_APPLICABLE",
        "activation_requires_new_judgment": False,
        "hardware_evidence_dependency_satisfied": None,
        "candidate_git_sha": None,
        "candidate_base_configurator_sha": None,
        "firmware_artifact_build_path": None,
        "preserved_firmware_artifact_locator": None,
        "firmware_artifact_sha256": None,
        "hardware_evidence_record": None,
        "hardware_result": None,
        "hardware_evidence_gaps": [],
    }
    validate_work_order(ready_example)
    for field, value in (
        ("activation_state", "INVALIDATED"),
        ("activation_requires_new_judgment", True),
        ("hardware_evidence_dependency_satisfied", False),
        ("automated_validation", []),
        ("stop_conditions", []),
    ):
        variant = dict(ready_example)
        variant[field] = value
        try:
            validate_work_order(variant)
        except FrameworkDocsError:
            pass
        else:
            fail(f"contradictory READY fixture accepted {field}={value!r}")
    invalid_preauthorized = dict(ready_example)
    invalid_preauthorized.update(
        {
            "status": "PREAUTHORIZED",
            "activation_state": "ACTIVATABLE",
            "mechanical_activation_conditions": [""],
            "invalidation_conditions": ["source authority changed"],
        }
    )
    try:
        validate_work_order(invalid_preauthorized)
    except FrameworkDocsError:
        pass
    else:
        fail("blank-condition PREAUTHORIZED fixture passed full validation")

    validated_hardware = dict(ready_example)
    validated_hardware.update(
        {
            "status": "HARDWARE_VALIDATED",
            "hardware_risk": "H2",
            "manual_acceptance": "REQUIRED",
            "candidate_git_sha": "a" * 40,
            "candidate_base_configurator_sha": "b" * 40,
            "firmware_artifact_build_path": ".pio/build/glyph_mk6/firmware.uf2",
            "preserved_firmware_artifact_locator": (
                "artifact://" + "a" * 40 + "/" + "c" * 64 + "/firmware.uf2"
            ),
            "firmware_artifact_sha256": "c" * 64,
            "hardware_evidence_record": "docs/evidence/test.md",
            "hardware_result": "PASS",
            "hardware_evidence_dependency_satisfied": True,
        }
    )
    validate_work_order(validated_hardware)
    partial_hardware = dict(validated_hardware)
    partial_hardware.update(
        {
            "status": "LOCAL_ACCEPTANCE_PENDING",
            "hardware_result": "PARTIAL",
            "hardware_evidence_dependency_satisfied": False,
            "hardware_evidence_gaps": ["repeat reconnect step"],
        }
    )
    validate_work_order(partial_hardware)
    partial_without_gaps = dict(partial_hardware)
    partial_without_gaps["hardware_evidence_gaps"] = []
    try:
        validate_work_order(partial_without_gaps)
    except FrameworkDocsError:
        pass
    else:
        fail("PARTIAL hardware fixture without exact gaps passed validation")
    pretest_hardware = dict(partial_hardware)
    pretest_hardware.update(
        {
            "status": "HARDWARE_TEST_REQUIRED",
            "hardware_result": None,
            "hardware_evidence_record": None,
            "hardware_evidence_gaps": [],
        }
    )
    validate_work_order(pretest_hardware)
    pretest_with_result = dict(pretest_hardware)
    pretest_with_result["hardware_result"] = "PASS"
    try:
        validate_work_order(pretest_with_result)
    except FrameworkDocsError:
        pass
    else:
        fail("HARDWARE_TEST_REQUIRED fixture with a result passed validation")
    mutable_locator = dict(pretest_hardware)
    mutable_locator["preserved_firmware_artifact_locator"] = mutable_locator[
        "firmware_artifact_build_path"
    ]
    try:
        validate_work_order(mutable_locator)
    except FrameworkDocsError:
        pass
    else:
        fail("mutable .pio hardware artifact locator passed validation")
    incomplete_locator = dict(pretest_hardware)
    incomplete_locator["preserved_firmware_artifact_locator"] = (
        "artifact://" + "a" * 40 + "/firmware.uf2"
    )
    try:
        validate_work_order(incomplete_locator)
    except FrameworkDocsError:
        pass
    else:
        fail("preserved artifact locator without artifact SHA passed validation")
    pass_line("canonical queue, runway counts, and zero-runway liveness validate")


def check_revision_two_surface() -> None:
    for phrase in (
        "READY is immediately executable",
        "Planner cannot mark work Ready or Preauthorized",
        "Invalidated Preauthorization and hardware-pending Preauthorization are never effective runway",
        "Time passage, an unrelated docs commit, or a SHA change alone does not make a packet stale",
        "use PLANNING_REQUIRED",
        "use CURATION_REQUIRED",
        "GLOBAL_EVIDENCE_WAIT_SUPPORTED requires a fresh broad",
        "Schedules are heartbeats, never quotas",
        "Canonical intended control-plane state changed from X to Y",
        "Curator may not edit firmware/configurator product code",
        "ordinary Curator test-edit surface is exactly",
        "planning/portfolio-*",
        "IMPLEMENTATION_DEFERRED_CONCURRENT_WRITER",
        "CURATION_DEFERRED_CONCURRENT_WRITER",
    ):
        require_phrase("docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md", phrase)

    for phrase in (
        "Work-order ID:",
        "Hardware risk:",
        "H0 | H1 | H2 | H3",
        "Behavioral claim:",
        "Explicit excluded scope:",
        "Touched planes:",
        "Source authority:",
        "Substantive authorization rationale:",
        "Mechanical activation conditions:",
        "Invalidation conditions:",
        "Authorization snapshot / provenance:",
        "Canonical build:",
        "Expected artifact:",
        "Manual acceptance protocol reference:",
        "Rollback / recovery:",
        "Done evidence:",
        "Stop conditions:",
        "Candidate Git SHA:",
        "Preserved firmware artifact locator:",
        "Firmware artifact SHA-256:",
        "Hardware evidence record:",
        "Hardware evidence gaps:",
    ):
        require_phrase("docs/agent_framework/WORK_ORDER_TEMPLATE.md", phrase)

    for phrase in (
        "Candidate Git SHA:",
        "Base/configurator SHA:",
        "Firmware artifact SHA-256:",
        "Controller model/revision:",
        "Protocol version:",
        "Expected result for every step:",
        "Observed result for every step:",
        "Negative/regression checks:",
        "Power-cycle/reconnect checks where relevant:",
        "PASS | FAIL | PARTIAL | INCONCLUSIVE",
        "HARDWARE_EVIDENCE_MISMATCH",
        "A failed candidate must not enter configurator",
        "at most one dependent H2/H3 candidate",
        "immutable candidate-SHA/artifact-SHA-addressed locator",
        "never substitute a rebuild",
        "Canonical Queue Result Mapping",
        "Legacy Evidence Boundary",
    ):
        require_phrase("docs/agent_framework/HARDWARE_EVIDENCE.md", phrase)

    for phrase in (
        "Directive",
        "Decision",
        "Priority",
        "Preference",
        "Observation",
        "Hypothesis",
        "Agents must not invent entries",
    ):
        require_phrase("docs/agent_framework/USER_DIRECTION.md", phrase)
    pass_line("Revision 2 authorization, evidence, and user-direction surfaces validate")


def check_legacy_control_plane_supersession() -> None:
    for rel_path in (
        "docs/project/AGENT_OPERATING_CONTRACT.md",
        "docs/project/AGENT_PROMPT_TEMPLATES.md",
        "docs/project/CODEX_CLOUD_WORKFLOW.md",
        "docs/project/CODEX_WORKFLOW.md",
    ):
        require_phrase(rel_path, "SUPERSEDED_BY_AGENT_FRAMEWORK")
        require_phrase(rel_path, "docs/agent_framework/")
    require_phrase("docs/project/AGENTS.md", "adds no alternative authority")
    require_phrase("docs/project/AGENTS.md", "SUPERSEDED_BY_AGENT_FRAMEWORK")
    pass_line("legacy project-local control plane is explicitly superseded")


def check_task_configurations() -> None:
    text = read_required("docs/agent_framework/SCHEDULED_TASKS.md")
    role_requirements = {
        "Glyph Implementation Supervisor": (
            "ACTIVE_SCHEDULE",
            "READY is the only immediately executable state",
            "Complete at most one new work order",
            "fresh independent post-implementation reviewer",
            "preserve the exact UF2",
            "HARDWARE_VALIDATED item is a publication cycle",
            "GLOBAL_EVIDENCE_WAIT_SUPPORTED",
            "Mechanically activatable Preauthorized runway",
            "HARDWARE_TEST_REQUIRED and REPAIR_REQUIRED are supporting signals",
            "invalidation takes precedence",
        ),
        "Glyph Work-Order Curator": (
            "OPTIONAL_SCHEDULE",
            "Planner proposes; Curator judges and authorizes",
            "You may authorize zero",
            "target and its provenance",
            "curator_review_required: true",
            "global_wait_proposed",
            "Canonical intended control-plane state changed from X to Y",
            "ordinary test-edit surface is exactly",
            "runtime product code changed: NO",
            "invalidation takes precedence over Planner refresh",
        ),
        "Glyph Portfolio Planner": (
            "MANUAL",
            "broad, read-heavy, and non-authoritative",
            "curator_review_required: true",
            "global_wait_proposed",
            "candidate_count is zero",
            "Never merge planning output to configurator",
            "configurator changed: NO",
        ),
        "Glyph Hardware Evidence Processor": (
            "MANUAL_ONLY",
            "human-supplied observations/results",
            "preserved artifact locator",
            "with no rebuild substitution",
            "HARDWARE_EVIDENCE_MISMATCH",
            "LOCAL_ACCEPTANCE_PENDING",
            "always add supporting REPAIR_REQUIRED",
            "primary state is CURATION_REQUIRED",
            "separate source-free docs/control-plane snapshot",
            "no runtime source editing",
        ),
    }
    headings = list(role_requirements)
    sections: dict[str, str] = {}
    for index, heading in enumerate(headings):
        marker = f"## {heading}"
        if text.count(marker) != 1:
            fail(f"SCHEDULED_TASKS.md must contain exactly one {heading} section")
        start = text.index(marker)
        end = text.index(f"## {headings[index + 1]}") if index + 1 < len(headings) else len(text)
        sections[heading] = text[start:end]

    if text.count("Exact copy-paste task prompt:") != len(role_requirements):
        fail("SCHEDULED_TASKS.md must contain exactly four full task prompts")
    for heading, phrases in role_requirements.items():
        section = sections[heading]
        for common in (
            "Task name:",
            "Recommended model/capability tier:",
            "Recommended reasoning:",
            "Recommended schedule state:",
            "Recommended cadence if scheduled:",
            "Reason for cadence:",
            "Exact copy-paste task prompt:",
            "Expected no-op/stop states:",
        ):
            if normalize(common) not in normalize(section):
                fail(f"{heading} configuration missing field: {common}")
        for phrase in phrases:
            if normalize(phrase) not in normalize(section):
                fail(f"{heading} prompt missing required contract: {phrase}")
    pass_line("four exact scheduled/manual task configurations validate")


def check_contract_phrases() -> None:
    framework_text = normalize(active_framework_text())
    missing_classifications = [
        classification
        for classification in BRANCH_CLASSIFICATIONS
        if normalize(classification) not in framework_text
    ]
    if missing_classifications:
        fail("missing branch classifications: " + ", ".join(missing_classifications))
    missing_verdicts = [
        verdict for verdict in JUDGE_VERDICTS if normalize(verdict) not in framework_text
    ]
    if missing_verdicts:
        fail("missing judge verdicts: " + ", ".join(missing_verdicts))
    pass_line("branch classifications and judge verdicts are documented")


def check_navigation_pointers() -> None:
    require_phrase("AGENTS.md", "docs/AGENT_CONTEXT.md")
    require_phrase("AGENTS.md", "docs/agent_framework/README.md")
    require_phrase("AGENTS.md", "docs/project/ACTIVE_AGENT_QUEUE.md")
    require_phrase("AGENTS.md", "docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md")
    pass_line("AGENTS.md points to framework entrypoints")


def check_forbidden_claims() -> None:
    bad: list[str] = []
    for raw_line in active_framework_text().splitlines():
        line = normalize(raw_line)
        for claim in BAD_ACTIVE_CLAIMS:
            if claim not in line:
                continue
            if any(marker in line for marker in SAFE_NEGATION_MARKERS):
                continue
            bad.append(f"{claim} [{raw_line.strip()}]")
    if bad:
        fail("forbidden active/supported claims found: " + ", ".join(bad))
    framework_text = normalize(active_framework_text())
    for phrase in (
        "nunchuk remains not_tested",
        "root cause remains unproven",
        "runtime-loaded config is not implemented",
    ):
        if phrase not in framework_text:
            fail(f"framework docs must preserve phrase: {phrase}")
    pass_line("forbidden active claims absent and required non-claims preserved")


def check_runner_boundary() -> None:
    runner_prompt_files = [
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "docs/agent_framework").rglob("*")
        if path.is_file() and "runner_prompt" in path.name.lower()
    ]
    if runner_prompt_files:
        fail("runner prompt files are not allowed: " + ", ".join(runner_prompt_files))
    if (REPO_ROOT / "scripts/agent_runner.py").exists():
        fail("scripts/agent_runner.py must not be added by this framework branch")
    pass_line("runner prompt and scripts/agent_runner.py are absent")


def main() -> int:
    try:
        check_required_paths()
        check_codex_only_surface()
        check_model_routing()
        check_queue_contract()
        check_revision_two_surface()
        check_legacy_control_plane_supersession()
        check_task_configurations()
        check_contract_phrases()
        check_navigation_pointers()
        check_forbidden_claims()
        check_runner_boundary()
    except FrameworkDocsError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("glyph_agent_framework_docs: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
