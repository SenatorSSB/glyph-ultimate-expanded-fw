#!/usr/bin/env python3
"""Validate Glyph agent framework documentation surface."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
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
    "manual_acceptance_protocol_version",
    "hardware_evidence_contract_reference",
    "hardware_evidence_contract_version",
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

EVIDENCE_RECORD_FIELDS = {
    "schema_name",
    "schema_version",
    "work_order_id",
    "candidate_branch",
    "candidate_git_sha",
    "candidate_base_configurator_sha",
    "firmware_artifact_filename",
    "firmware_artifact_build_path",
    "firmware_artifact_sha256",
    "preserved_firmware_artifact_locator",
    "pre_update_sha256_verified",
    "controller_model_revision",
    "firmware_profile_state",
    "update_method",
    "host_platform_adapter",
    "evidence_contract_reference",
    "evidence_contract_version",
    "candidate_protocol_reference",
    "candidate_protocol_version",
    "preconditions",
    "steps",
    "negative_regression_checks",
    "power_cycle_reconnect_checks",
    "result",
    "anomalies",
    "rollback_recovery",
    "tester",
    "tested_at",
    "evidence_gaps",
}
EVIDENCE_REF_RE = re.compile(
    r"^(?:repo-json:(?P<repo>docs/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*\.json)|"
    r"git-json:(?P<sha>[0-9a-f]{40}):(?P<git>docs/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*\.json))$"
)
EVIDENCE_CONTRACT_REFERENCE = "docs/agent_framework/HARDWARE_EVIDENCE.md"
EVIDENCE_CONTRACT_VERSION = "GLYPH_HARDWARE_EVIDENCE_V2"
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
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

CURRENT_RUNWAY_MARKER_START = "<!-- current-runway:start -->"
CURRENT_RUNWAY_MARKER_END = "<!-- current-runway:end -->"
CURRENT_RUNWAY_MARKER_FIELDS = (
    "ready_ids",
    "immediate_ready",
    "recorded_preauthorized",
    "mechanically_activatable_preauthorized",
    "invalidated_preauthorized",
    "hardware_pending",
    "effective_authorized_runway",
    "target_effective_authorized_runway",
    "primary_liveness",
    "global_evidence_wait_supported",
)
CURRENT_RUNWAY_MIRRORS = (
    "docs/project/ACTIVE_AGENT_QUEUE.md",
    "docs/AGENT_CONTEXT.md",
    "docs/CURRENT_STATE.md",
    "docs/ROADMAP.md",
)

CURRENT_RUNWAY_SUMMARY_START = "<!-- current-runway-summary:start -->"
CURRENT_RUNWAY_SUMMARY_END = "<!-- current-runway-summary:end -->"
CURRENT_RUNWAY_SUMMARY_FIELDS = (
    "Ready IDs",
    "Immediate Ready",
    "Recorded Preauthorized",
    "Mechanically activatable Preauthorized",
    "Invalidated Preauthorized",
    "Hardware-pending",
    "Effective authorized runway",
    "Target effective authorized runway",
    "Primary liveness",
)

CURRENT_PROSE_MIRROR_PATTERNS = (
    re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:Ready IDs|Immediate Ready|Recorded Preauthorized|"
               r"Mechanically activatable Preauthorized|Invalidated Preauthorized|"
               r"Hardware-pending|Effective authorized runway|Target effective authorized runway|"
               r"Primary liveness):"),
    re.compile(r"(?im)\b(?:current|canonical|effective|actual)\s+(?:executable\s+)?"
               r"(?:runway|liveness)\s*(?:is|=|of|:)\s*(?:\d+|RUNWAY_[A-Z_]+|"
               r"PLANNING_REQUIRED|CURATION_REQUIRED)\b"),
    re.compile(r"(?im)\b\d+\s+(?:current\s+)?(?:load-bearing\s+)?"
               r"(?:validation\s+)?(?:checks?|entries?)\b"),
    re.compile(r"(?im)^\s*[-*]\s*`?[A-Z][A-Z0-9-]+`?\s*:\s*`?READY\b|"
               r"\bGP-[A-Z0-9-]+\s+(?:is|remains|currently)\s+READY\b|"
               r"\bCurrent\s+(?:status|state|Ready ID)\s*:\s*(?:GP-[A-Z0-9-]+|READY)\b"),
    re.compile(r"(?im)\b(?:current|executable|selected|next|highest)\s+"
               r"(?:work-order\s+)?priority(?:\s+order)?\b"),
)


def current_prose_without_authoritative_blocks(text: str) -> str:
    text = re.sub(
        r"<!-- current-runway:start -->.*?<!-- current-runway:end -->",
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<!-- current-runway-summary:start -->.*?<!-- current-runway-summary:end -->",
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<!-- queue-state:start -->.*?<!-- queue-state:end -->",
        "",
        text,
        flags=re.DOTALL,
    )
    return text


def check_current_prose_mirrors() -> None:
    for rel_path in CURRENT_RUNWAY_MIRRORS:
        prose = current_prose_without_authoritative_blocks(read_required(rel_path))
        for pattern in CURRENT_PROSE_MIRROR_PATTERNS:
            match = pattern.search(prose)
            if match:
                fail(
                    f"{rel_path} contains an unguarded current runway/prose claim: "
                    f"{match.group(0).strip()}"
                )

    fixtures = (
        "- GP-SYNTHETIC: READY stale current claim",
        "GP-SYNTHETIC is READY.",
        "Current status: READY.",
        "Current Ready ID: GP-SYNTHETIC.",
        "Current executable runway is 2.",
        "Primary liveness: RUNWAY_LOW",
        "The current validation has 31 checks.",
        "The current executable priority is GP-SYNTHETIC.",
    )
    for rel_path in CURRENT_RUNWAY_MIRRORS:
        base = current_prose_without_authoritative_blocks(read_required(rel_path))
        for fixture in fixtures:
            mutated = base + "\n" + fixture + "\n"
            if not any(pattern.search(mutated) for pattern in CURRENT_PROSE_MIRROR_PATTERNS):
                fail(f"current-prose adversarial fixture was accepted for {rel_path}: {fixture}")
    pass_line("current prose contains no duplicated unguarded runway claims")

COMPLETION_POLICY_FIELDS = ("migration_base_configurator_sha", "legacy_done_ids")
COMPLETION_EVIDENCE_FIELDS = {
    "schema_name",
    "schema_version",
    "mode",
    "implementation_base_sha",
    "reviewed_implementation_sha",
    "prior_canonical_integration_sha",
    "reviewed_changed_paths",
    "independent_review_provenance",
    "validation_provenance",
}
COMPLETION_EVIDENCE_NAME = "glyph_done_completion_evidence"
COMPLETION_EVIDENCE_VERSION = 1
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

PLANNER_PACKET_FIELDS = {
    "state",
    "branch",
    "base_configurator_sha",
    "packet_id",
    "packet_path",
    "planning_commit",
    "curation_commit",
    "candidate_count",
    "survivors",
    "curator_review_required",
    "global_wait_proposed",
    "material_events_since_packet",
    "curator_review_provenance",
}
CURATOR_PROVENANCE_FIELDS = {
    "planning_branch",
    "planning_commit",
    "packet_id",
    "packet_base_configurator_sha",
    "curation_branch",
    "curation_commit",
    "review_date",
    "initial_reviewed_dispositions",
}
PLANNER_DISPOSITIONS = {
    "READY",
    "PREAUTHORIZED",
    "SUBSTANTIVE_DEPENDENCY_GATED",
    "EVIDENCE_GATED",
    "RESEARCH_GATED",
    "USER_DECISION_GATED",
    "REPAIR_REAUTHORIZATION",
}
PLANNER_PACKET_ID_RE = re.compile(r"^glyph-portfolio-[0-9]{8}-[0-9]{4}$")
PLANNER_BRANCH_RE = re.compile(r"^planning/portfolio-[0-9]{8}-[0-9]{4}$")

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


TASK_HEADINGS = (
    "Glyph Implementation Supervisor",
    "Glyph Work-Order Curator",
    "Glyph Portfolio Planner",
    "Glyph Hardware Evidence Processor",
)


def extract_task_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    for index, heading in enumerate(TASK_HEADINGS):
        marker = f"## {heading}"
        if text.count(marker) != 1:
            fail(f"SCHEDULED_TASKS.md must contain exactly one {heading} section")
        start = text.index(marker)
        end = text.index(f"## {TASK_HEADINGS[index + 1]}") if index + 1 < len(TASK_HEADINGS) else len(text)
        sections[heading] = text[start:end]
    return sections


def require_concept(label: str, text: str, concept: str, groups: tuple[tuple[str, ...], ...]) -> None:
    normalized = normalize(text)
    missing = ["/".join(group) for group in groups if not any(normalize(term) in normalized for term in group)]
    if missing:
        fail(f"{label} missing {concept}: " + ", ".join(missing))


def validate_no_subagent_reason(reason: str) -> None:
    normalized = normalize(reason).strip(" .\"")
    if "no tools were visible initially" in normalized:
        fail("initial tool visibility is not a valid no-subagent reason")
    accepted = (
        "true no-op",
        "trivial mechanical",
        "complete capability discovery confirming no native",
        "runtime failure after attempted discovery",
        "runtime failure after attempted child creation",
        "concurrency stop",
        "safety stop",
    )
    if not any(marker in normalized for marker in accepted):
        fail("no-subagent reason is not an explicit permitted exception")


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


def _queue_block_from_text(raw: str, label: str) -> dict[str, object]:
    if raw.count(QUEUE_START) != 1 or raw.count(QUEUE_END) != 1:
        fail(f"{label} must contain exactly one queue-state marker pair")
    block = raw.split(QUEUE_START, 1)[1].split(QUEUE_END, 1)[0].strip()
    if not block.startswith("```json") or not block.endswith("```"):
        fail(f"{label} queue-state block must be fenced JSON")
    try:
        payload = json.loads(block[len("```json") : -len("```")].strip())
    except json.JSONDecodeError as exc:
        fail(f"{label} queue-state block is not valid JSON: {exc}")
    if not isinstance(payload, dict):
        fail(f"{label} queue-state block must be an object")
    return payload


def _git_tree_entry(commit: str, path: str, label: str, repo_root: Path = REPO_ROOT) -> tuple[str, str, str]:
    entries = [line for line in _git(repo_root, "ls-tree", commit, "--", path).splitlines() if line]
    if len(entries) != 1:
        fail(f"{label} must resolve to exactly one Git tree entry")
    header, found_path = entries[0].split("\t", 1)
    mode, kind, oid = header.split(" ")
    if found_path != path or mode != "100644" or kind != "blob":
        fail(f"{label} must be a regular non-executable 100644 blob")
    return mode, kind, oid


def _planner_packet_correspondence(
    planner_packet: dict[str, object], packet_state: str, items_raw: object,
    repo_root: Path = REPO_ROOT,
) -> int:
    if packet_state == "ABSENT":
        expected = {
            "state", "branch", "base_configurator_sha", "candidate_count",
            "curator_review_required", "global_wait_proposed",
            "material_events_since_packet",
        }
        if set(planner_packet) != expected or planner_packet["candidate_count"] != 0:
            fail("ABSENT Planner packet must not carry packet/object correspondence")
        return 0
    if set(planner_packet) != PLANNER_PACKET_FIELDS:
        fail("recorded Planner packet fields do not match the object-correspondence contract")
    packet_id = planner_packet["packet_id"]
    packet_path = planner_packet["packet_path"]
    planning_commit = planner_packet["planning_commit"]
    curation_commit = planner_packet["curation_commit"]
    base_sha = planner_packet["base_configurator_sha"]
    if not isinstance(packet_id, str) or not PLANNER_PACKET_ID_RE.fullmatch(packet_id):
        fail("recorded Planner packet requires a canonical packet_id")
    packet_filename = packet_id.removeprefix("glyph-").replace("-", "_") + ".md"
    if not isinstance(packet_path, str) or packet_path != f"docs/planning/{packet_filename}":
        fail("Planner packet_path must be the canonical packet document path")
    if not isinstance(planner_packet["branch"], str) or not PLANNER_BRANCH_RE.fullmatch(planner_packet["branch"]):
        fail("recorded Planner packet branch must use the packet identity")
    for value, field in ((base_sha, "base_configurator_sha"), (planning_commit, "planning_commit"), (curation_commit, "curation_commit")):
        if not isinstance(value, str) or not SHA_RE.fullmatch(value):
            fail(f"{field} must be a full lowercase Git SHA")
        _require_commit_sha(value, field, repo_root)
    if _git(repo_root, "rev-list", "--parents", "-n", "1", planning_commit).split()[1:] != [base_sha]:
        fail("planning_commit must be a direct child of packet_base_configurator_sha")
    if _git(repo_root, "rev-list", "--parents", "-n", "1", curation_commit).split()[1:] != [base_sha]:
        fail("curation_commit must be a direct child of packet_base_configurator_sha")
    _is_ancestor(repo_root, curation_commit, _git(repo_root, "rev-parse", "HEAD").strip(), "curation_commit")
    _git_tree_entry(planning_commit, packet_path, "Planner packet document", repo_root)
    _git_tree_entry(curation_commit, "docs/project/ACTIVE_AGENT_QUEUE.md", "Curator queue snapshot", repo_root)

    packet_text = _git(repo_root, "show", f"{planning_commit}:{packet_path}")
    if packet_text.count("```yaml") != 1:
        fail("Planner packet must contain exactly one YAML frontmatter block")
    frontmatter_text = packet_text.split("```yaml", 1)[1].split("```", 1)[0]
    frontmatter: dict[str, str] = {}
    for line in frontmatter_text.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([a-z][a-z0-9_]*):[ \t]*(.+)", line)
        if not match or match.group(1) in frontmatter:
            fail("Planner packet frontmatter must use unique anchored key/value lines")
        frontmatter[match.group(1)] = match.group(2).strip()
    required_frontmatter = {
        "packet_id": packet_id,
        "packet_state": "FRESH",
        "planning_branch": planner_packet["branch"],
        "base_configurator_sha": base_sha,
        "candidate_count": "13",
        "curator_review_required": "true",
        "global_wait_proposed": "false",
    }
    if any(frontmatter.get(key) != value for key, value in required_frontmatter.items()):
        fail("Planner packet frontmatter does not match the exact queue correspondence")
    candidate_ids = re.findall(r"^###? +(GP-[A-Z0-9-]+)(?:\s|$)", packet_text, re.MULTILINE)
    if len(candidate_ids) != len(set(candidate_ids)) or len(candidate_ids) != 13:
        fail("Planner packet candidate headings must contain exactly thirteen unique candidates")
    candidate_set = set(candidate_ids)

    provenance = planner_packet["curator_review_provenance"]
    if not isinstance(provenance, dict) or set(provenance) != CURATOR_PROVENANCE_FIELDS:
        fail("curator_review_provenance fields do not match the object-correspondence contract")
    for key, expected in (
        ("planning_branch", planner_packet["branch"]),
        ("planning_commit", planning_commit),
        ("packet_id", packet_id),
        ("packet_base_configurator_sha", base_sha),
        ("curation_commit", curation_commit),
    ):
        if provenance.get(key) != expected:
            fail(f"curator_review_provenance.{key} disagrees with packet identity")
    if not isinstance(provenance.get("curation_branch"), str) or not provenance["curation_branch"].startswith("curation/"):
        fail("curator_review_provenance.curation_branch must identify a curation branch")
    initial = provenance["initial_reviewed_dispositions"]
    if not isinstance(initial, list) or len(initial) != len(candidate_ids):
        fail("initial reviewed dispositions must cover every Planner candidate")
    seen_initial: set[str] = set()
    for entry in initial:
        if not isinstance(entry, dict) or set(entry) != {"candidate_id", "disposition"}:
            fail("initial reviewed dispositions must use candidate_id/disposition pairs")
        candidate_id = entry["candidate_id"]
        if candidate_id not in candidate_set or candidate_id in seen_initial:
            fail("initial reviewed dispositions must be unique members of the packet")
        if entry["disposition"] not in PLANNER_DISPOSITIONS:
            fail("initial reviewed disposition is outside the closed disposition set")
        seen_initial.add(candidate_id)
    if seen_initial != candidate_set:
        fail("initial reviewed dispositions must cover the exact packet inventory")

    survivors = planner_packet["survivors"]
    if not isinstance(survivors, list) or planner_packet["candidate_count"] != len(survivors):
        fail("Planner candidate_count must be derived from survivors")
    if not isinstance(items_raw, list):
        fail("queue items must be a list before survivor correspondence")
    current_ids = {item.get("id") for item in items_raw if isinstance(item, dict)}
    seen_survivors: set[str] = set()
    for entry in survivors:
        if not isinstance(entry, dict) or set(entry) != {"candidate_id", "disposition"}:
            fail("survivors must use candidate_id/disposition pairs")
        candidate_id = entry["candidate_id"]
        if candidate_id not in candidate_set or candidate_id in seen_survivors:
            fail("survivors must be unique members of the original packet")
        if entry["disposition"] not in PLANNER_DISPOSITIONS:
            fail("survivor disposition is outside the closed disposition set")
        if candidate_id in current_ids:
            fail("survivors may not be authorized or represented by a current queue item")
        seen_survivors.add(candidate_id)
    return len(survivors)


def check_planner_packet_correspondence_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="glyph-planner-packet-") as temp:
        repo = Path(temp)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "checker@example.invalid"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Glyph checker"], cwd=repo, check=True)
        (repo / "docs/planning").mkdir(parents=True)
        (repo / "docs/project").mkdir(parents=True)
        (repo / "README").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
        base = _git(repo, "rev-parse", "HEAD").strip()
        packet_id = "glyph-portfolio-20260901-0909"
        packet_path = "docs/planning/portfolio_20260901_0909.md"
        candidates = [
            "GP-SRC-006", "GP-VAL-002", "GP-PROV-002", "GP-VAL-012", "GP-PROV-003",
            "GP-VAL-011", "GP-CTL-003", "GP-BUILD-001", "GP-VAL-008", "GP-CONFIG-005",
            "GP-PERSIST-001", "GP-ART-001", "GP-X1-001",
        ]
        packet = "```yaml\n" + "\n".join((
            f"packet_id: {packet_id}",
            "packet_state: FRESH",
            "planning_branch: planning/portfolio-20260901-0909",
            f"base_configurator_sha: {base}",
            "candidate_count: 13",
            "curator_review_required: true",
            "global_wait_proposed: false",
        )) + "\n```\n\n" + "\n".join(f"### {candidate} — fixture" for candidate in candidates) + "\n"
        (repo / packet_path).write_text(packet, encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "planning"], cwd=repo, check=True)
        planning = _git(repo, "rev-parse", "HEAD").strip()
        subprocess.run(["git", "checkout", "-qb", "curation", base], cwd=repo, check=True)
        (repo / "docs/project/ACTIVE_AGENT_QUEUE.md").write_text("queue\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "curation"], cwd=repo, check=True)
        curation = _git(repo, "rev-parse", "HEAD").strip()
        planner_packet: dict[str, object] = {
            "state": "PARTIALLY_CONSUMED",
            "branch": "planning/portfolio-20260901-0909",
            "base_configurator_sha": base,
            "packet_id": packet_id,
            "packet_path": packet_path,
            "planning_commit": planning,
            "curation_commit": curation,
            "candidate_count": 2,
            "survivors": [
                {"candidate_id": "GP-VAL-011", "disposition": "SUBSTANTIVE_DEPENDENCY_GATED"},
                {"candidate_id": "GP-ART-001", "disposition": "USER_DECISION_GATED"},
            ],
            "curator_review_required": False,
            "global_wait_proposed": False,
            "material_events_since_packet": ["fixture event"],
            "curator_review_provenance": {
                "planning_branch": "planning/portfolio-20260901-0909",
                "planning_commit": planning,
                "packet_id": packet_id,
                "packet_base_configurator_sha": base,
                "curation_branch": "curation/fixture",
                "curation_commit": curation,
                "review_date": "2026-09-01",
                "initial_reviewed_dispositions": [
                    {"candidate_id": candidate, "disposition": "USER_DECISION_GATED"}
                    for candidate in candidates
                ],
            },
        }
        items = [{"id": "GP-CTL-003"}, {"id": "GP-VAL-008"}]
        if _planner_packet_correspondence(planner_packet, "PARTIALLY_CONSUMED", items, repo) != 2:
            fail("valid synthetic Planner packet correspondence returned the wrong survivor count")
        subprocess.run(["git", "checkout", "-qb", "bad-frontmatter", base], cwd=repo, check=True)
        bad_packet = packet.replace("packet_id: glyph-portfolio-20260901-0909", "not_packet_id: glyph-portfolio-20260901-0909")
        (repo / "docs/planning").mkdir(parents=True, exist_ok=True)
        (repo / packet_path).write_text(bad_packet, encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "bad frontmatter"], cwd=repo, check=True)
        bad_planning = _git(repo, "rev-parse", "HEAD").strip()
        subprocess.run(["git", "checkout", "-q", "curation"], cwd=repo, check=True)
        malformed = json.loads(json.dumps(planner_packet))
        malformed["planning_commit"] = bad_planning
        try:
            _planner_packet_correspondence(malformed, "PARTIALLY_CONSUMED", items, repo)
        except FrameworkDocsError:
            pass
        else:
            fail("prefixed synthetic Planner frontmatter key was accepted")
        duplicate = json.loads(json.dumps(planner_packet))
        duplicate["survivors"][1] = duplicate["survivors"][0]
        try:
            _planner_packet_correspondence(duplicate, "PARTIALLY_CONSUMED", items, repo)
        except FrameworkDocsError:
            pass
        else:
            fail("duplicate synthetic Planner survivor was accepted")
        missing_blob = json.loads(json.dumps(planner_packet))
        missing_blob["packet_path"] = "docs/planning/missing.md"
        try:
            _planner_packet_correspondence(missing_blob, "PARTIALLY_CONSUMED", items, repo)
        except FrameworkDocsError:
            pass
        else:
            fail("missing synthetic Planner packet blob was accepted")
        for label, mutation in (
            ("count mismatch", lambda value: value.update(candidate_count=3)),
            ("unknown disposition", lambda value: value["survivors"][0].update(disposition="UNKNOWN")),
            ("current survivor", lambda value: value["survivors"][0].update(candidate_id="GP-CTL-003")),
            ("absent survivor", lambda value: value["survivors"][0].update(candidate_id="GP-NOT-IN-PACKET")),
        ):
            variant = json.loads(json.dumps(planner_packet))
            mutation(variant)
            try:
                _planner_packet_correspondence(variant, "PARTIALLY_CONSUMED", items, repo)
            except FrameworkDocsError:
                pass
            else:
                fail(f"{label} synthetic Planner packet was accepted")
    pass_line("Planner/Curator packet object and survivor adversarial cases validate")


def require_nonempty_string(value: object, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"queue work order field {field} must be a non-empty string")


def _git(repo_root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        fail(f"unable to resolve hardware evidence Git object: {exc}")
    return result.stdout


def _require_commit_sha(value: object, field: str, repo_root: Path = REPO_ROOT) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        fail(f"{field} must be a full lowercase Git SHA")
    if _git(repo_root, "cat-file", "-t", f"{value}^{{commit}}").strip() != "commit":
        fail(f"{field} must resolve to a Git commit")
    return value


def _is_ancestor(repo_root: Path, ancestor: str, descendant: str, field: str) -> None:
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=repo_root, check=True, capture_output=True, text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        fail(f"{field} must be an ancestor of the completion publication")


def _queue_from_commit(commit: str, repo_root: Path = REPO_ROOT) -> dict[str, object]:
    raw = _git(repo_root, "show", f"{commit}:docs/project/ACTIVE_AGENT_QUEUE.md")
    if raw.count(QUEUE_START) != 1 or raw.count(QUEUE_END) != 1:
        fail("migration-base queue state must contain exactly one marker pair")
    block = raw.split(QUEUE_START, 1)[1].split(QUEUE_END, 1)[0].strip()
    if not block.startswith("```json") or not block.endswith("```"):
        fail("migration-base queue state must be fenced JSON")
    try:
        payload = json.loads(block[len("```json") : -len("```")].strip())
    except (IndexError, json.JSONDecodeError) as exc:
        fail(f"migration-base queue state is invalid: {exc}")
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        fail("migration-base queue state must contain an items list")
    return payload


def _changed_paths(repo_root: Path, base: str, tip: str) -> list[str]:
    return sorted(
        path for path in _git(repo_root, "diff", "--name-only", base, tip).splitlines()
        if path
    )


def _tree_entry(repo_root: Path, commit: str, path: str) -> tuple[str, str, str] | None:
    entries = [line for line in _git(repo_root, "ls-tree", commit, "--", path).splitlines() if line]
    if not entries:
        return None
    header, found_path = entries[0].split("\t", 1)
    mode, kind, oid = header.split(" ")
    if found_path != path:
        fail("completion evidence tree path resolution is ambiguous")
    return mode, kind, oid


def _validate_exact_path_tree(repo_root: Path, base: str, tip: str, integration: str, paths: list[str]) -> None:
    parents = _git(repo_root, "rev-list", "--parents", "-n", "1", integration).split()
    if len(parents) != 2:
        fail("EXACT_PATH_TREE integration must be a dedicated single-parent commit")
    if _changed_paths(repo_root, base, tip) != paths:
        fail("completion evidence reviewed_changed_paths do not match implementation diff")
    if _changed_paths(repo_root, parents[1], integration) != paths:
        fail("exact replay changed paths do not match reviewed implementation paths")
    for path in paths:
        if _tree_entry(repo_root, tip, path) != _tree_entry(repo_root, integration, path):
            fail("exact replay Git modes or blob identities differ from reviewed implementation")


def validate_completion_evidence(
    item: dict[str, object], evidence: object, *, policy: dict[str, object],
    publication_sha: str, repo_root: Path = REPO_ROOT,
) -> None:
    if not isinstance(evidence, dict) or set(evidence) != COMPLETION_EVIDENCE_FIELDS:
        fail(f"{item['id']} Done evidence must use the strict structured completion schema")
    if evidence["schema_name"] != COMPLETION_EVIDENCE_NAME or type(evidence["schema_version"]) is not int or evidence["schema_version"] != COMPLETION_EVIDENCE_VERSION:
        fail("completion evidence schema identity is invalid")
    mode = evidence["mode"]
    if mode not in {"DIRECT_ANCESTRY", "EXACT_PATH_TREE"}:
        fail("completion evidence mode is invalid")
    for field in ("independent_review_provenance", "validation_provenance"):
        require_nonempty_string(evidence[field], f"completion evidence {field}")
    base = _require_commit_sha(evidence["implementation_base_sha"], "implementation_base_sha", repo_root)
    tip = _require_commit_sha(evidence["reviewed_implementation_sha"], "reviewed_implementation_sha", repo_root)
    integration = _require_commit_sha(evidence["prior_canonical_integration_sha"], "prior_canonical_integration_sha", repo_root)
    paths = evidence["reviewed_changed_paths"]
    if not isinstance(paths, list) or not all(isinstance(path, str) and path for path in paths):
        fail("completion evidence reviewed_changed_paths must be a string list")
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        fail("completion evidence reviewed_changed_paths must be sorted unique strings")
    _is_ancestor(repo_root, base, tip, "implementation base")
    _is_ancestor(repo_root, base, integration, "canonical integration")
    _is_ancestor(repo_root, integration, publication_sha, "canonical integration")
    if integration == publication_sha:
        fail("completion integration must precede status publication")
    if mode == "DIRECT_ANCESTRY":
        _is_ancestor(repo_root, tip, integration, "reviewed implementation")
        if _changed_paths(repo_root, base, tip) != paths:
            fail("completion evidence reviewed_changed_paths do not match implementation diff")
    else:
        _validate_exact_path_tree(repo_root, base, tip, integration, paths)


def check_completion_correspondence(payload: dict[str, object], items: list[dict[str, object]]) -> None:
    policy = payload.get("completion_correspondence")
    if not isinstance(policy, dict) or set(policy) != set(COMPLETION_POLICY_FIELDS):
        fail("queue completion_correspondence policy has invalid fields")
    migration = _require_commit_sha(policy.get("migration_base_configurator_sha"), "migration_base_configurator_sha")
    current_publication = _git(REPO_ROOT, "rev-parse", "HEAD").strip()
    _is_ancestor(REPO_ROOT, migration, current_publication, "migration base")
    legacy_payload = _queue_from_commit(migration)
    legacy = sorted(item["id"] for item in legacy_payload["items"] if isinstance(item, dict) and item.get("status") == "DONE")
    if policy.get("legacy_done_ids") != legacy:
        fail("queue legacy_done_ids do not match the migration-base Done set")
    for item in items:
        if item["status"] == "DONE" and item["id"] not in legacy:
            validate_completion_evidence(item, item["done_evidence"], policy=policy, publication_sha=current_publication)


def check_completion_correspondence_self_test() -> None:
    def run(repo: Path, *args: str) -> str:
        result = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)
        return result.stdout.strip()

    def commit(repo: Path, message: str) -> str:
        run(repo, "add", ".")
        run(repo, "commit", "-qm", message)
        return run(repo, "rev-parse", "HEAD")

    def evidence(base: str, tip: str, integration: str, publication: str, mode: str, paths: list[str]) -> dict[str, object]:
        return {
            "schema_name": COMPLETION_EVIDENCE_NAME,
            "schema_version": COMPLETION_EVIDENCE_VERSION,
            "mode": mode,
            "implementation_base_sha": base,
            "reviewed_implementation_sha": tip,
            "prior_canonical_integration_sha": integration,
            "reviewed_changed_paths": paths,
            "independent_review_provenance": "synthetic independent review",
            "validation_provenance": "synthetic validation",
        }

    with tempfile.TemporaryDirectory(prefix="glyph-completion-") as raw_root:
        repo = Path(raw_root)
        run(repo, "init", "-q")
        run(repo, "config", "user.email", "checker@example.invalid")
        run(repo, "config", "user.name", "checker")
        (repo / "docs").mkdir()
        (repo / "docs" / "reviewed.txt").write_text("before\n", encoding="utf-8")
        base = commit(repo, "base")
        (repo / "docs" / "reviewed.txt").write_text("after\n", encoding="utf-8")
        tip = commit(repo, "reviewed implementation")
        (repo / "docs" / "publication.txt").write_text("published\n", encoding="utf-8")
        publication = commit(repo, "completion publication")
        direct = evidence(base, tip, tip, publication, "DIRECT_ANCESTRY", ["docs/reviewed.txt"])
        validate_completion_evidence({}, direct, policy={}, publication_sha=publication, repo_root=repo)

        replay_root = Path(raw_root) / "replay"
        replay_root.mkdir()
        run(replay_root, "init", "-q")
        run(replay_root, "config", "user.email", "checker@example.invalid")
        run(replay_root, "config", "user.name", "checker")
        (replay_root / "docs").mkdir()
        (replay_root / "docs" / "reviewed.txt").write_text("before\n", encoding="utf-8")
        replay_base = commit(replay_root, "base")
        (replay_root / "docs" / "reviewed.txt").write_text("after\n", encoding="utf-8")
        replay_tip = commit(replay_root, "reviewed implementation")
        run(replay_root, "checkout", "-q", replay_base)
        (replay_root / "docs" / "reviewed.txt").write_text("after\n", encoding="utf-8")
        replay_integration = commit(replay_root, "dedicated replay")
        (replay_root / "docs" / "publication.txt").write_text("published\n", encoding="utf-8")
        replay_publication = commit(replay_root, "completion publication")
        replay = evidence(replay_base, replay_tip, replay_integration, replay_publication, "EXACT_PATH_TREE", ["docs/reviewed.txt"])
        validate_completion_evidence({}, replay, policy={}, publication_sha=replay_publication, repo_root=replay_root)
        for bad_paths in (["docs/extra.txt", "docs/reviewed.txt"], ["docs/reviewed.txt", "docs/reviewed.txt"]):
            invalid_replay = dict(replay)
            invalid_replay["reviewed_changed_paths"] = bad_paths
            try:
                validate_completion_evidence({}, invalid_replay, policy={}, publication_sha=replay_publication, repo_root=replay_root)
            except FrameworkDocsError:
                pass
            else:
                fail("invalid exact replay path set passed completion correspondence")

        invalid = dict(direct)
        invalid["reviewed_implementation_sha"] = base
        try:
            validate_completion_evidence({}, invalid, policy={}, publication_sha=publication, repo_root=repo)
        except FrameworkDocsError:
            pass
        else:
            fail("unintegrated reviewed implementation passed completion correspondence")
        malformed = dict(direct)
        malformed["reviewed_changed_paths"] = [None, "docs/reviewed.txt"]
        try:
            validate_completion_evidence({}, malformed, policy={}, publication_sha=publication, repo_root=repo)
        except FrameworkDocsError:
            pass
        else:
            fail("malformed reviewed path list passed completion correspondence")
        for field, value in (("implementation_base_sha", "refs/heads/main"), ("prior_canonical_integration_sha", "HEAD")):
            invalid_ref = dict(direct)
            invalid_ref[field] = value
            try:
                validate_completion_evidence({}, invalid_ref, policy={}, publication_sha=publication, repo_root=repo)
            except FrameworkDocsError:
                pass
            else:
                fail("mutable completion Git reference passed correspondence")
        invalid_order = dict(direct)
        invalid_order["prior_canonical_integration_sha"] = publication
        try:
            validate_completion_evidence({}, invalid_order, policy={}, publication_sha=publication, repo_root=repo)
        except FrameworkDocsError:
            pass
        else:
            fail("completion integration equal to publication passed correspondence")
        wrong_base = dict(direct)
        wrong_base["implementation_base_sha"] = tip
        try:
            validate_completion_evidence({}, wrong_base, policy={}, publication_sha=publication, repo_root=repo)
        except FrameworkDocsError:
            pass
        else:
            fail("wrong implementation base passed completion correspondence")
    pass_line("completion correspondence direct/replay and negative Git corpus validate")


def _load_evidence_record(reference: object, repo_root: Path = REPO_ROOT) -> dict[str, object]:
    if not isinstance(reference, str):
        fail("hardware_evidence_record must be a supported repo-json or git-json reference")
    match = EVIDENCE_REF_RE.fullmatch(reference)
    if not match:
        fail("hardware_evidence_record must use repo-json:<docs/*.json> or git-json:<sha>:<docs/*.json>")
    commit = "HEAD" if match.group("repo") else match.group("sha")
    rel_path = match.group("repo") or match.group("git")
    if any(segment in {".", ".."} for segment in rel_path.split("/")):
        fail("hardware evidence record path must be normalized and cannot contain dot segments")
    if _git(repo_root, "cat-file", "-t", f"{commit}^{{commit}}").strip() != "commit":
        fail("hardware evidence Git reference must resolve to a commit")
    entries = _git(repo_root, "ls-tree", "-z", commit, "--", rel_path).split("\0")
    entries = [entry for entry in entries if entry]
    if len(entries) != 1:
        fail("hardware evidence record path must resolve to exactly one Git tree entry")
    header, path = entries[0].split("\t", 1)
    mode, kind, blob = header.split(" ")
    if path != rel_path or mode != "100644" or kind != "blob" or not re.fullmatch(r"[0-9a-f]{40}", blob):
        fail("hardware evidence record must be a regular non-executable 100644 JSON blob")
    try:
        raw = _git(repo_root, "show", f"{commit}:{rel_path}")
        def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
            result: dict[str, object] = {}
            for key, value in pairs:
                if key in result:
                    fail("hardware evidence record contains duplicate JSON keys")
                result[key] = value
            return result

        record = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        fail(f"hardware evidence record is not valid JSON: {exc}")
    if not isinstance(record, dict):
        fail("hardware evidence record must be a flat JSON object")
    if set(record) != EVIDENCE_RECORD_FIELDS:
        fail("hardware evidence record has unexpected, missing, or duplicate-schema fields")
    return record


def validate_evidence_record(item: dict[str, object], evidence_repo_root: Path = REPO_ROOT) -> None:
    record = _load_evidence_record(item["hardware_evidence_record"], evidence_repo_root)
    if (
        record["schema_name"] != "glyph_hardware_evidence_record"
        or type(record["schema_version"]) is not int
        or record["schema_version"] != 2
    ):
        fail("hardware evidence record schema identity is invalid")
    string_fields = {
        "work_order_id", "candidate_branch", "candidate_git_sha", "candidate_base_configurator_sha",
        "firmware_artifact_filename", "firmware_artifact_build_path", "firmware_artifact_sha256",
        "preserved_firmware_artifact_locator", "controller_model_revision", "firmware_profile_state",
        "update_method", "host_platform_adapter", "evidence_contract_reference",
        "evidence_contract_version", "candidate_protocol_reference", "candidate_protocol_version",
        "result", "rollback_recovery", "tester", "tested_at",
    }
    for field in string_fields:
        require_nonempty_string(record[field], f"hardware evidence record {field}")
    if record["pre_update_sha256_verified"] is not True:
        fail("hardware evidence record requires pre_update_sha256_verified true")
    if record["result"] not in {"PASS", "FAIL", "PARTIAL", "INCONCLUSIVE"}:
        fail("hardware evidence record result is invalid")
    if not RFC3339_RE.fullmatch(str(record["tested_at"])):
        fail("hardware evidence record tested_at must be RFC3339")
    for field in (
        "preconditions", "negative_regression_checks", "power_cycle_reconnect_checks",
        "anomalies", "evidence_gaps",
    ):
        value = record[field]
        if not isinstance(value, list) or not all(isinstance(entry, str) and entry.strip() for entry in value):
            fail(f"hardware evidence record {field} must be a list of nonblank strings")
    if not record["preconditions"] or not record["steps"]:
        fail("hardware evidence record requires nonempty preconditions and steps")
    for step in record["steps"]:
        if not isinstance(step, dict) or set(step) != {"id", "instruction", "expected", "observed"}:
            fail("hardware evidence record steps must have exact id/instruction/expected/observed fields")
        for field in ("id", "instruction", "expected", "observed"):
            require_nonempty_string(step[field], f"hardware evidence step {field}")
    expected = {
        "work_order_id": item["id"], "candidate_branch": item["branch"],
        "candidate_git_sha": item["candidate_git_sha"],
        "candidate_base_configurator_sha": item["candidate_base_configurator_sha"],
        "firmware_artifact_filename": Path(str(item["firmware_artifact_build_path"])).name,
        "firmware_artifact_build_path": item["firmware_artifact_build_path"],
        "firmware_artifact_sha256": item["firmware_artifact_sha256"],
        "preserved_firmware_artifact_locator": item["preserved_firmware_artifact_locator"],
        "evidence_contract_reference": item["hardware_evidence_contract_reference"],
        "evidence_contract_version": item["hardware_evidence_contract_version"],
        "candidate_protocol_reference": item["manual_acceptance_protocol_reference"],
        "candidate_protocol_version": item["manual_acceptance_protocol_version"],
        "result": item["hardware_result"], "evidence_gaps": item["hardware_evidence_gaps"],
    }
    for field, value in expected.items():
        if record[field] != value:
            fail(f"hardware evidence record field {field} does not match queue")
    if record["evidence_contract_reference"] != EVIDENCE_CONTRACT_REFERENCE or record["evidence_contract_version"] != EVIDENCE_CONTRACT_VERSION:
        fail("hardware evidence record uses the wrong generic evidence contract")
    if record["result"] == "PASS" and record["evidence_gaps"]:
        fail("PASS hardware evidence cannot contain evidence gaps")
    if record["result"] in {"PARTIAL", "INCONCLUSIVE"} and not record["evidence_gaps"]:
        fail("PARTIAL/INCONCLUSIVE hardware evidence requires evidence gaps")


def validate_work_order(item: object, evidence_repo_root: Path = REPO_ROOT) -> dict[str, object]:
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
    ):
        require_nonempty_string(item[field], field)

    if item["status"] == "DONE":
        if not isinstance(item["done_evidence"], (str, dict)):
            fail("DONE work order done_evidence must be a string or structured object")
        if isinstance(item["done_evidence"], str) and not item["done_evidence"].strip():
            fail("DONE work order done_evidence must not be blank")
    else:
        require_nonempty_string(item["done_evidence"], "done_evidence")

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
    if item["hardware_risk"] in {"H0", "H1"}:
        for field in (
            "manual_acceptance_protocol_version",
            "hardware_evidence_contract_reference",
            "hardware_evidence_contract_version",
        ):
            if item[field] != "NOT_APPLICABLE":
                fail(f"{field} must be NOT_APPLICABLE for H0/H1 work")
    else:
        if item["manual_acceptance_protocol_reference"] == "NOT_APPLICABLE":
            fail("H2/H3 work must use a candidate-local manual acceptance protocol reference")
        if item["hardware_evidence_contract_reference"] != EVIDENCE_CONTRACT_REFERENCE:
            fail("H2/H3 work must use the generic hardware evidence contract reference")
        if item["hardware_evidence_contract_version"] != EVIDENCE_CONTRACT_VERSION:
            fail("H2/H3 work must use the generic hardware evidence contract version")
        if item["manual_acceptance_protocol_version"] == "NOT_APPLICABLE":
            fail("H2/H3 work must use a candidate-local manual acceptance protocol version")
        require_nonempty_string(item["manual_acceptance_protocol_version"], "manual_acceptance_protocol_version")

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
        validate_evidence_record(item, evidence_repo_root)
        if evidence_gaps:
            fail("HARDWARE_VALIDATED cannot retain hardware evidence gaps")
    elif status == "HARDWARE_FAILED":
        if item["hardware_result"] != "FAIL":
            fail("HARDWARE_FAILED requires hardware_result FAIL")
        require_nonempty_string(item["hardware_evidence_record"], "hardware_evidence_record")
        validate_evidence_record(item, evidence_repo_root)
    elif status == "LOCAL_ACCEPTANCE_PENDING":
        if item["hardware_result"] not in {None, "PARTIAL", "INCONCLUSIVE"}:
            fail("LOCAL_ACCEPTANCE_PENDING result must be null, PARTIAL, or INCONCLUSIVE")
        if item["hardware_result"] is not None:
            require_nonempty_string(
                item["hardware_evidence_record"], "hardware_evidence_record"
            )
            if not evidence_gaps:
                fail("PARTIAL/INCONCLUSIVE hardware result requires exact evidence gaps")
            validate_evidence_record(item, evidence_repo_root)
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


def parse_current_runway_marker(text: str, rel_path: str) -> dict[str, object]:
    start = text.count(CURRENT_RUNWAY_MARKER_START)
    end = text.count(CURRENT_RUNWAY_MARKER_END)
    if start != 1 or end != 1:
        fail(
            f"{rel_path} must contain exactly one current-runway marker pair; "
            f"found {start} start and {end} end markers"
        )
    marker_start = text.index(CURRENT_RUNWAY_MARKER_START) + len(CURRENT_RUNWAY_MARKER_START)
    marker_end = text.index(CURRENT_RUNWAY_MARKER_END, marker_start)
    raw = text[marker_start:marker_end].strip()
    try:
        marker = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"{rel_path} current-runway marker is not JSON: {exc.msg}")
    if not isinstance(marker, dict):
        fail(f"{rel_path} current-runway marker must be an object")
    if set(marker) != set(CURRENT_RUNWAY_MARKER_FIELDS):
        fail(f"{rel_path} current-runway marker fields do not match the contract")
    return marker


def require_current_runway_match(
    actual: dict[str, object], expected: dict[str, object], rel_path: str
) -> None:
    if actual != expected or any(
        type(actual[field]) is not type(expected[field])
        for field in expected
    ):
        fail(
            f"{rel_path} current-runway marker disagrees with canonical queue: "
            f"expected {json.dumps(expected, sort_keys=True)}, "
            f"found {json.dumps(actual, sort_keys=True)}"
        )


def check_current_runway_mirrors(
    *,
    items: list[dict[str, object]],
    runway: dict[str, object],
    expected_liveness: str,
    global_wait_supported: bool,
) -> None:
    expected: dict[str, object] = {
        "ready_ids": [item["id"] for item in items if item["status"] == "READY"],
        "immediate_ready": runway["immediate_ready"],
        "recorded_preauthorized": runway["recorded_preauthorized"],
        "mechanically_activatable_preauthorized": runway[
            "mechanically_activatable_preauthorized"
        ],
        "invalidated_preauthorized": runway["invalidated_preauthorized"],
        "hardware_pending": runway["hardware_pending"],
        "effective_authorized_runway": runway["effective_authorized_runway"],
        "target_effective_authorized_runway": runway[
            "target_effective_authorized_runway"
        ],
        "primary_liveness": expected_liveness,
        "global_evidence_wait_supported": global_wait_supported,
    }
    def validate_mirror_text(text: str, rel_path: str) -> None:
        actual = parse_current_runway_marker(text, rel_path)
        require_current_runway_match(actual, expected, rel_path)

    for rel_path in CURRENT_RUNWAY_MIRRORS:
        validate_mirror_text(read_required(rel_path), rel_path)
    mirror_path = CURRENT_RUNWAY_MIRRORS[0]
    immediate_ready_literal = f'"immediate_ready":{expected["immediate_ready"]}'
    stale_text = read_required(mirror_path).replace(
        immediate_ready_literal,
        f'"immediate_ready":{int(expected["immediate_ready"]) + 1}',
        1,
    )
    if stale_text == read_required(mirror_path):
        fail("current-runway adversarial fixture did not drift")
    try:
        validate_mirror_text(stale_text, "synthetic current-runway mirror")
    except FrameworkDocsError:
        pass
    else:
        fail("stale current-runway marker fixture was accepted")
    pass_line("current queue/status mirrors match machine-derived runway state")


def parse_current_runway_summary(text: str, rel_path: str) -> dict[str, object]:
    if text.count(CURRENT_RUNWAY_SUMMARY_START) != 1 or text.count(CURRENT_RUNWAY_SUMMARY_END) != 1:
        fail(f"{rel_path} must contain exactly one current-runway summary block")
    start = text.index(CURRENT_RUNWAY_SUMMARY_START) + len(CURRENT_RUNWAY_SUMMARY_START)
    end = text.find(CURRENT_RUNWAY_SUMMARY_END)
    if end < start:
        fail(f"{rel_path} current-runway summary markers are out of order")
    raw_lines = [line.strip() for line in text[start:end].splitlines() if line.strip()]
    lines = raw_lines if len(raw_lines) != 1 else [part.strip() for part in raw_lines[0].split("; ")]
    if len(lines) != len(CURRENT_RUNWAY_SUMMARY_FIELDS):
        fail(f"{rel_path} current-runway summary must contain exactly nine fields")
    values: dict[str, object] = {}
    for line, field in zip(lines, CURRENT_RUNWAY_SUMMARY_FIELDS):
        prefix = field + ": "
        if not line.startswith(prefix) or line.count(": ") != 1:
            fail(f"{rel_path} current-runway summary has malformed {field} field")
        value = line[len(prefix):]
        if not value:
            fail(f"{rel_path} current-runway summary has blank {field} field")
        if field == "Ready IDs":
            values[field] = [] if value == "(none)" else value.split(", ")
        elif field in {
            "Immediate Ready",
            "Recorded Preauthorized",
            "Mechanically activatable Preauthorized",
            "Invalidated Preauthorized",
            "Hardware-pending",
            "Effective authorized runway",
            "Target effective authorized runway",
        }:
            if not value.isdigit():
                fail(f"{rel_path} current-runway summary {field} must be an integer")
            values[field] = int(value)
        else:
            values[field] = value
    return values


def check_current_runway_summaries(
    *,
    items: list[dict[str, object]],
    runway: dict[str, object],
    expected_liveness: str,
) -> None:
    expected = {
        "Ready IDs": [item["id"] for item in items if item["status"] == "READY"],
        "Immediate Ready": runway["immediate_ready"],
        "Recorded Preauthorized": runway["recorded_preauthorized"],
        "Mechanically activatable Preauthorized": runway[
            "mechanically_activatable_preauthorized"
        ],
        "Invalidated Preauthorized": runway["invalidated_preauthorized"],
        "Hardware-pending": runway["hardware_pending"],
        "Effective authorized runway": runway["effective_authorized_runway"],
        "Target effective authorized runway": runway[
            "target_effective_authorized_runway"
        ],
        "Primary liveness": expected_liveness,
    }

    def require_summary_match(actual: dict[str, object], rel_path: str) -> None:
        if actual != expected:
            fail(
                f"{rel_path} current-runway summary disagrees with canonical queue: "
                f"expected {json.dumps(expected, sort_keys=True)}, "
                f"found {json.dumps(actual, sort_keys=True)}"
            )

    for rel_path in CURRENT_RUNWAY_MIRRORS:
        actual = parse_current_runway_summary(read_required(rel_path), rel_path)
        require_summary_match(actual, rel_path)
    stale_text = read_required(CURRENT_RUNWAY_MIRRORS[0]).replace(
        "Immediate Ready: " + str(expected["Immediate Ready"]),
        "Immediate Ready: " + str(int(expected["Immediate Ready"]) + 1),
        1,
    )
    try:
        actual = parse_current_runway_summary(stale_text, "synthetic current-runway summary")
        require_summary_match(actual, "synthetic current-runway summary")
    except FrameworkDocsError:
        pass
    else:
        fail("stale current-runway summary fixture was accepted")
    reversed_text = (
        CURRENT_RUNWAY_SUMMARY_END
        + "\n"
        + CURRENT_RUNWAY_SUMMARY_START
        + "\n"
        + "Ready IDs: TEST"
    )
    try:
        parse_current_runway_summary(reversed_text, "synthetic reversed current-runway summary")
    except FrameworkDocsError:
        pass
    else:
        fail("reversed current-runway summary markers were accepted")
    pass_line("current human-readable runway summaries match machine state")


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
    items_raw = payload.get("items")
    candidate_count = _planner_packet_correspondence(planner_packet, packet_state, items_raw)
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

    if not isinstance(items_raw, list):
        fail("queue items must be a list")
    items = [validate_work_order(item) for item in items_raw]
    check_completion_correspondence(payload, items)
    check_planner_packet_correspondence_self_test()
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

    check_current_runway_mirrors(
        items=items,
        runway=runway,
        expected_liveness=expected_liveness,
        global_wait_supported=global_wait["supported"],
    )
    check_current_runway_summaries(
        items=items,
        runway=runway,
        expected_liveness=expected_liveness,
    )
    check_current_prose_mirrors()

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
        "manual_acceptance_protocol_version": "NOT_APPLICABLE",
        "hardware_evidence_contract_reference": "NOT_APPLICABLE",
        "hardware_evidence_contract_version": "NOT_APPLICABLE",
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
            "manual_acceptance_protocol_reference": "docs/test_protocol.md",
            "manual_acceptance_protocol_version": "TEST_PROTOCOL_V1",
            "hardware_evidence_contract_reference": EVIDENCE_CONTRACT_REFERENCE,
            "hardware_evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
        }
    )
    temp_context = tempfile.TemporaryDirectory(prefix="glyph-hardware-record-")
    if temp_context:
        temp_dir = temp_context.name
        evidence_root = Path(temp_dir)
        subprocess.run(["git", "init", "-q"], cwd=evidence_root, check=True)
        subprocess.run(["git", "config", "user.email", "checker@example.invalid"], cwd=evidence_root, check=True)
        subprocess.run(["git", "config", "user.name", "Glyph checker"], cwd=evidence_root, check=True)
        record = {
            "schema_name": "glyph_hardware_evidence_record", "schema_version": 2,
            "work_order_id": validated_hardware["id"], "candidate_branch": validated_hardware["branch"],
            "candidate_git_sha": validated_hardware["candidate_git_sha"],
            "candidate_base_configurator_sha": validated_hardware["candidate_base_configurator_sha"],
            "firmware_artifact_filename": "firmware.uf2",
            "firmware_artifact_build_path": validated_hardware["firmware_artifact_build_path"],
            "firmware_artifact_sha256": validated_hardware["firmware_artifact_sha256"],
            "preserved_firmware_artifact_locator": validated_hardware["preserved_firmware_artifact_locator"],
            "pre_update_sha256_verified": True, "controller_model_revision": "synthetic",
            "firmware_profile_state": "synthetic", "update_method": "synthetic",
            "host_platform_adapter": "synthetic", "evidence_contract_reference": EVIDENCE_CONTRACT_REFERENCE,
            "evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
            "candidate_protocol_reference": validated_hardware["manual_acceptance_protocol_reference"],
            "candidate_protocol_version": validated_hardware["manual_acceptance_protocol_version"],
            "preconditions": ["synthetic record"],
            "steps": [{"id": "S1", "instruction": "observe", "expected": "pass", "observed": "pass"}],
            "negative_regression_checks": [], "power_cycle_reconnect_checks": [], "result": "PASS",
            "anomalies": [], "rollback_recovery": "none", "tester": "checker",
            "tested_at": "2026-01-01T00:00:00Z", "evidence_gaps": [],
        }
        record_path = evidence_root / "docs" / "evidence.json"
        record_path.parent.mkdir(parents=True)
        record_path.write_text(json.dumps(record), encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=evidence_root, check=True)
        subprocess.run(["git", "commit", "-qm", "record"], cwd=evidence_root, check=True)
        validated_hardware["hardware_evidence_record"] = "repo-json:docs/evidence.json"
        validate_work_order(validated_hardware, evidence_root)
        for schema_version in (2.0, "2", True):
            typed_variant = dict(record)
            typed_variant["schema_version"] = schema_version
            record_path.write_text(json.dumps(typed_variant), encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=evidence_root, check=True)
            subprocess.run(["git", "commit", "-qm", "schema type"], cwd=evidence_root, check=True)
            typed_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=evidence_root, check=True,
                capture_output=True, text=True,
            ).stdout.strip()
            expect_reference = f"git-json:{typed_sha}:docs/evidence.json"
            variant = dict(validated_hardware)
            variant["hardware_evidence_record"] = expect_reference
            try:
                validate_work_order(variant, evidence_root)
            except FrameworkDocsError:
                pass
            else:
                fail(f"non-integer hardware evidence schema_version passed: {schema_version!r}")
            record_path.write_text(json.dumps(record), encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=evidence_root, check=True)
            subprocess.run(["git", "commit", "-qm", "restore schema"], cwd=evidence_root, check=True)
        initial_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=evidence_root, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        validated_hardware["hardware_evidence_record"] = f"git-json:{initial_sha}:docs/evidence.json"
        validate_work_order(validated_hardware, evidence_root)

        def expect_evidence_rejection(reference: str) -> None:
            variant = dict(validated_hardware)
            variant["hardware_evidence_record"] = reference
            try:
                validate_work_order(variant, evidence_root)
            except FrameworkDocsError:
                return
            fail(f"invalid hardware evidence reference passed: {reference}")

        for reference in (
            "https://example.invalid/evidence.json",
            "repo-json:/absolute/evidence.json",
            "repo-json:docs/../evidence.json",
            "git-json:refs/heads/configurator:docs/evidence.json",
        ):
            expect_evidence_rejection(reference)
        duplicate_text = record_path.read_text(encoding="utf-8").replace(
            '"schema_version": 2,', '"schema_version": 2, "schema_version": 2,', 1
        )
        record_path.write_text(duplicate_text, encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=evidence_root, check=True)
        subprocess.run(["git", "commit", "-qm", "duplicate"], cwd=evidence_root, check=True)
        duplicate_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=evidence_root, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        expect_evidence_rejection(f"git-json:{duplicate_sha}:docs/evidence.json")
        record_path.write_text(json.dumps(record), encoding="utf-8")
        executable_path = evidence_root / "docs" / "executable.json"
        executable_path.write_text(json.dumps(record), encoding="utf-8")
        executable_path.chmod(0o755)
        subprocess.run(["git", "add", "."], cwd=evidence_root, check=True)
        subprocess.run(["git", "commit", "-qm", "executable"], cwd=evidence_root, check=True)
        executable_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=evidence_root, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        expect_evidence_rejection(f"git-json:{executable_sha}:docs/executable.json")
        symlink_path = evidence_root / "docs" / "symlink.json"
        symlink_path.symlink_to("evidence.json")
        subprocess.run(["git", "add", "."], cwd=evidence_root, check=True)
        subprocess.run(["git", "commit", "-qm", "symlink"], cwd=evidence_root, check=True)
        symlink_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=evidence_root, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        expect_evidence_rejection(f"git-json:{symlink_sha}:docs/symlink.json")
        validated_hardware["hardware_evidence_record"] = "repo-json:docs/evidence.json"
    partial_hardware = dict(validated_hardware)
    partial_hardware.update(
        {
            "status": "LOCAL_ACCEPTANCE_PENDING",
            "hardware_result": "PARTIAL",
            "hardware_evidence_dependency_satisfied": False,
            "hardware_evidence_gaps": ["repeat reconnect step"],
        }
    )
    partial_hardware["hardware_evidence_record"] = validated_hardware["hardware_evidence_record"]
    partial_record = dict(record)
    partial_record["result"] = "PARTIAL"
    partial_record["evidence_gaps"] = ["repeat reconnect step"]
    record_path.write_text(json.dumps(partial_record), encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=evidence_root, check=True)
    subprocess.run(["git", "commit", "-qm", "partial"], cwd=evidence_root, check=True)
    validate_work_order(partial_hardware, evidence_root)
    partial_without_gaps = dict(partial_hardware)
    partial_without_gaps["hardware_evidence_gaps"] = []
    try:
        validate_work_order(partial_without_gaps, evidence_root)
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
    validate_work_order(pretest_hardware, evidence_root)
    pretest_with_result = dict(pretest_hardware)
    pretest_with_result["hardware_result"] = "PASS"
    try:
        validate_work_order(pretest_with_result, evidence_root)
    except FrameworkDocsError:
        pass
    else:
        fail("HARDWARE_TEST_REQUIRED fixture with a result passed validation")
    mutable_locator = dict(pretest_hardware)
    mutable_locator["preserved_firmware_artifact_locator"] = mutable_locator[
        "firmware_artifact_build_path"
    ]
    try:
        validate_work_order(mutable_locator, evidence_root)
    except FrameworkDocsError:
        pass
    else:
        fail("mutable .pio hardware artifact locator passed validation")
    incomplete_locator = dict(pretest_hardware)
    incomplete_locator["preserved_firmware_artifact_locator"] = (
        "artifact://" + "a" * 40 + "/firmware.uf2"
    )
    try:
        validate_work_order(incomplete_locator, evidence_root)
    except FrameworkDocsError:
        pass
    else:
        fail("preserved artifact locator without artifact SHA passed validation")
    temp_context.cleanup()
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
        "No fresh human approval is required solely because the authorized work changes active firmware behavior",
        "Implementation autonomy is not merge autonomy",
        "USER_DECISION_GATED",
        "EVIDENCE_GATED",
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
        "Substantive Authority Invariant",
        "no redundant blanket human-approval field is required",
        "Hardware risk alone does not require fresh human approval before candidate implementation",
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
        "current user-directed governance correction supplied 2026-08-23",
        "Authorized, source-grounded firmware behavior work may be implemented autonomously through the candidate stage",
    ):
        require_phrase("docs/agent_framework/USER_DIRECTION.md", phrase)
    pass_line("Revision 2 authorization, evidence, and user-direction surfaces validate")


def check_firmware_implementation_authority() -> None:
    required = {
        "AGENTS.md": (
            "A complete READY H2/H3 work order with resolved substantive authority may be implemented",
            "must never merge before its required exact-snapshot hardware PASS",
            "Do not use H2/H3 authorization to bypass those boundaries",
        ),
        "docs/WORKFLOW.md": (
            "A complete READY work order may authorize source-grounded firmware/runtime behavior implementation without a fresh user approval solely because",
            "User/domain input is required before implementation when the proposed runtime behavior still contains an unresolved",
            "Curator may not infer user intent or invent undocumented Glyph behavior",
            "implementation autonomy is not merge autonomy",
        ),
        "docs/AGENT_CONTEXT.md": (
            "A complete READY H2/H3 work order inside the approved current path may be implemented as a candidate",
            "exact-snapshot hardware PASS before merge",
            "Unresolved behavior decisions and forbidden active-publication paths still stop before implementation",
        ),
        "docs/agent_framework/SUPERVISOR_CONTRACT.md": (
            "Do not refuse a complete READY H2/H3 item solely because it changes active firmware",
            "If behavior, product/domain intent, source authority, architecture, scope, or validation still requires substantive judgment, do not implement",
            "Never merge H2/H3 before the exact candidate/artifact pair has physical PASS",
        ),
    }
    for rel_path, phrases in required.items():
        for phrase in phrases:
            require_phrase(rel_path, phrase)

    stale_blanket_rules = {
        "AGENTS.md": "Stop before implementing if the task requires firmware behavior changes",
        "docs/WORKFLOW.md": "User product approval is required before firmware behavior implementation",
    }
    for rel_path, stale_phrase in stale_blanket_rules.items():
        if normalize(stale_phrase) in normalize(read_required(rel_path)):
            fail(f"{rel_path} retains contradictory blanket firmware stop: {stale_phrase}")
    pass_line("firmware implementation authority and hardware merge gate are reconciled")


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


def validate_delegation_sections(sections: dict[str, str]) -> None:
    report_fields = (
        "Delegation:",
        "guidance applicable:",
        "capability discovery:",
        "native capability available:",
        "specialists used:",
        "reviewer used:",
        "if none, reason:",
    )
    for heading, section in sections.items():
        require_concept(
            heading,
            section,
            "complete runtime capability discovery",
            (("complete available runtime", "complete runtime"),
             ("capability/tool catalog", "capability catalog", "tool catalog"),
             ("discovery", "discover")),
        )
        require_concept(
            heading,
            section,
            "initial manifest non-exhaustiveness",
            (("initial visible",), ("manifest", "tool list"),
             ("insufficient", "not exhaustive", "non-exhaustive")),
        )
        require_concept(
            heading,
            section,
            "native delegation versus user-owned jobs",
            (("native internal subagent", "native internal child"),
             ("user-owned",), ("task",), ("thread",),
             ("distinct", "not equivalent", "not a substitute")),
        )
        for field in report_fields:
            if normalize(field) not in normalize(section):
                fail(f"{heading} missing delegation report field: {field}")
        normalized = normalize(section)
        if re.search(
            r"initial (?:visible )?(?:tool )?(?:manifest|list).{0,100}"
            r"(?:is |as )?(?:exhaustive|complete) (?:evidence|proof)",
            normalized,
        ):
            fail(f"{heading} treats initial tool visibility as exhaustive")
        if re.search(
            r"user-owned (?:task|thread|conversation|automation|job).{0,80}"
            r"(?:equivalent to|serves as|constitutes|counts as|"
            r"is (?:the )?(?:only )?) native internal (?:subagent|delegation)",
            normalized,
        ):
            fail(f"{heading} conflates user-owned tasks with native delegation")

    implementation = sections["Glyph Implementation Supervisor"]
    require_concept(
        "Glyph Implementation Supervisor",
        implementation,
        "mandatory fresh reviewer for mutation",
        (("normal implementation cycle",), ("mutates repository state",)),
    )
    normalized_implementation = normalize(implementation)
    if not re.search(
        r"fresh independent post-implementation reviewer (?:is )?required "
        r"when native capability is available",
        normalized_implementation,
    ):
        fail(
            "Glyph Implementation Supervisor missing coupled mandatory fresh "
            "reviewer requirement for available native capability"
        )
    require_concept(
        "Glyph Implementation Supervisor",
        implementation,
        "reviewer evidence and defect scope",
        (("objective/scope/exclusions",), ("diff or changed-area",),
         ("evidence/contracts",), ("validation results",),
         ("correctness",), ("safety",), ("authority",), ("scope",),
         ("publication",), ("regression",)),
    )
    require_concept(
        "Glyph Implementation Supervisor",
        implementation,
        "materially separable specialist",
        (("at least one additional bounded specialist",),
         ("materially separable investigation",), ("quota",)),
    )
    require_concept(
        "Glyph Implementation Supervisor",
        implementation,
        "H2/H3 specialist and separate reviewer",
        (("H2/H3",), ("source-authority", "firmware-safety"),
         ("separate fresh independent reviewer",), ("no new user-approval gate", "no new user approval gate")),
    )
    require_concept(
        "Glyph Implementation Supervisor",
        implementation,
        "root retained authority",
        (("root retains", "root owns"), ("mutation",), ("validation",),
         ("Git",), ("publication",), ("final authority",)),
    )
    for reason in (
        "true no-op cycle",
        "trivial mechanical task",
        "complete capability discovery confirming no native facility",
        "runtime failure after attempted discovery or child creation",
        "concurrency/safety stop",
    ):
        if normalize(reason) not in normalize(implementation):
            fail(f"Implementation prompt missing no-use exception: {reason}")

    planner = sections["Glyph Portfolio Planner"]
    require_concept(
        "Glyph Portfolio Planner",
        planner,
        "partitioned parallel read-heavy specialists",
        (("parallel read-heavy specialists",), ("cleanly partitioned",),
         ("candidate surface is tiny",), ("non-authoritative",)),
    )
    curator = sections["Glyph Work-Order Curator"]
    require_concept(
        "Glyph Work-Order Curator",
        curator,
        "bounded verification with retained judgment",
        (("bounded verification specialists",), ("materially separable",),
         ("retains the final substantive authorization judgment",)),
    )
    evidence = sections["Glyph Hardware Evidence Processor"]
    require_concept(
        "Glyph Hardware Evidence Processor",
        evidence,
        "fresh evidence-mutation reviewer",
        (("result-bearing evidence mutation",), ("fresh reviewer",),
         ("native capability exists",), ("identity",), ("correspondence",),
         ("schema",), ("must not invent physical observations",)),
    )


def check_delegation_contract_self_test(sections: dict[str, str]) -> None:
    validate_delegation_sections(sections)

    def expect_rejection(label: str, mutated: dict[str, str]) -> None:
        try:
            validate_delegation_sections(mutated)
        except FrameworkDocsError:
            return
        fail(f"delegation adversarial self-test passed unexpectedly: {label}")

    implementation = sections["Glyph Implementation Supervisor"]
    mutations = (
        (
            "capability discovery removed",
            re.sub(r"\bcomplete\b", "partial", implementation, flags=re.IGNORECASE),
        ),
        (
            "initial visibility made exhaustive",
            implementation
            + "\nThe initial tool list is exhaustive proof that subagents are unavailable.\n",
        ),
        (
            "user task conflated with native delegation",
            implementation
            + "\nUser-owned thread creation is equivalent to native internal delegation.\n",
        ),
        (
            "user task serves as native delegation",
            implementation
            + "\nA user-owned task serves as native internal delegation.\n",
        ),
        (
            "mandatory reviewer removed",
            re.sub(
                r"(fresh\s+independent\s+post-implementation\s+reviewer\s+is\s+)REQUIRED",
                r"\1OPTIONAL",
                implementation,
                count=1,
                flags=re.IGNORECASE,
            ),
        ),
    )
    for label, changed in mutations:
        if changed == implementation:
            fail(f"delegation self-test mutation did not alter fixture: {label}")
        mutated_sections = dict(sections)
        mutated_sections["Glyph Implementation Supervisor"] = changed
        expect_rejection(label, mutated_sections)

    validate_no_subagent_reason("true no-op cycle")
    try:
        validate_no_subagent_reason("no tools were visible initially")
    except FrameworkDocsError:
        pass
    else:
        fail("initial-visibility no-use reason passed adversarial validation")
    pass_line("delegation discovery and accountability adversarial self-tests validate")


def check_native_delegation_contract() -> None:
    canonical = read_required("docs/agent_framework/SUBAGENT_CONTRACTS.md")
    for phrase in (
        "Native Delegation Discovery And Accountability",
        "complete available runtime capability/tool catalog",
        "initial manifest must not be treated as exhaustive",
        "distinct from and not equivalent to native internal subagent delegation",
        "without hardcoding one runtime-specific tool name",
        "root retains integrated mutation, authoritative validation, Git",
        "a fresh independent post-implementation reviewer is required",
        "Do not create specialist work merely to satisfy a quota",
        "a complete `READY` H2/H3 contract remains executable",
        "Curator retains the final substantive authorization judgment",
        "must not invent physical observations",
    ):
        if normalize(phrase) not in normalize(canonical):
            fail(f"canonical delegation contract missing: {phrase}")

    supervisor = read_required("docs/agent_framework/SUPERVISOR_CONTRACT.md")
    require_concept(
        "Supervisor contract",
        supervisor,
        "delegation discovery and review gate",
        (("delegation preflight",), ("complete runtime capability discovery",),
         ("initial visible tool manifest is not exhaustive evidence",),
         ("user-owned task/thread creation is not native internal delegation",),
         ("fresh independent post-implementation reviewer",),
         ("materially separable investigation",), ("H2/H3",)),
    )

    scheduled = read_required("docs/agent_framework/SCHEDULED_TASKS.md")
    sections = extract_task_sections(scheduled)
    check_delegation_contract_self_test(sections)

    templates = read_required("docs/agent_framework/PROMPT_TEMPLATES.md")
    for heading in (
        "## Supervisor Cycle Prompt",
        "## Planner Handoff",
        "## Curator Handoff",
        "## Hardware Evidence Processor Handoff",
    ):
        if heading not in templates:
            fail(f"PROMPT_TEMPLATES.md missing delegation-aware template: {heading}")
    for phrase in (
        "complete available runtime capability/tool catalog",
        "initial visible manifest",
        "Native internal subagents are distinct from user-owned",
        "Delegation:",
        "capability discovery:",
        "native capability available:",
        "if none, reason:",
    ):
        if normalize(phrase) not in normalize(templates):
            fail(f"prompt templates missing delegation concept: {phrase}")
    pass_line("native delegation discovery, role boundaries, and reporting validate")


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
            "Do not refuse an otherwise complete READY H2/H3 item solely because it changes active firmware",
            "No fresh human approval is required solely because the authorized candidate is H2/H3",
            "return CURATION_REQUIRED and name the exact user/evidence decision gate",
            "Implementation autonomy is not merge autonomy",
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
            "You may authorize source-grounded H2/H3 implementation",
            "Do not require a fresh user approval solely because the authorized work changes active firmware",
            "do not infer user intent or invent undocumented Glyph behavior",
            "USER_DECISION_GATED, EVIDENCE_GATED",
            "physical exact-snapshot PASS remains mandatory before merge",
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
        for phrase in (
            "Attempt live Git verification normally",
            "treat the result as inconclusive",
            "permitted network-enabled/escalated execution mechanism",
            "not authentication evidence",
            "Authentication may be diagnosed only after connectivity is established and GitHub actually rejects authentication",
            "Never automatically run gh auth login/logout",
            "rewrite tokens, delete credentials, change credential helpers, replace SSH keys, switch accounts, or request re-login",
            "account-level changes are user-owned unless separately requested",
            "Do not use stale local remote-tracking refs as a substitute",
            "all permitted network-capable retries failed",
        ):
            if normalize(phrase) not in normalize(section):
                fail(f"{heading} prompt missing live-remote retry contract: {phrase}")
    pass_line("four exact scheduled/manual task configurations validate")


def check_live_remote_retry_contract() -> None:
    required = {
        "AGENTS.md": (
            "ordinary/default minimal read-only verification",
            "result is inconclusive",
            "permitted network-enabled/escalated execution mechanism",
            "not authentication evidence",
            "Never automatically run `gh auth login` or `gh auth logout`",
            "Stale local remote-tracking refs never substitute",
            "all permitted network-capable retries failed",
        ),
        "docs/WORKFLOW.md": (
            "ordinary/default minimal read-only live-remote operation",
            "sandboxed `gh auth status` is not a reliable authentication oracle",
            "Account-level mutation is user-owned",
            "Stale local remote-tracking refs never substitute",
        ),
        "docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md": (
            "ordinary/default minimal read-only attempt",
            "first DNS/network failure is inconclusive",
            "Authentication may be diagnosed only after GitHub connectivity is established",
            "all permitted network-capable retries failed",
        ),
        "docs/agent_framework/VALIDATION_AND_GATES.md": (
            "attempt ordinary/default read-only verification",
            "return `BLOCKED_EXTERNAL` until all permitted network-capable retries fail",
        ),
    }
    for rel_path, phrases in required.items():
        for phrase in phrases:
            require_phrase(rel_path, phrase)
    prompt_templates = read_required("docs/agent_framework/PROMPT_TEMPLATES.md")
    template_headings = (
        "## Supervisor Cycle Prompt",
        "## Planner Handoff",
        "## Curator Handoff",
        "## Hardware Evidence Processor Handoff",
        "## Architecture Specialist Handoff",
    )
    for index, heading in enumerate(template_headings[:-1]):
        start = prompt_templates.index(heading)
        end = prompt_templates.index(template_headings[index + 1], start)
        section = normalize(prompt_templates[start:end])
        for phrase in (
            "Live Git verification: attempt it normally",
            "restricted-sandbox GitHub/DNS/network failure is inconclusive",
            "permitted network-enabled/escalated mechanism",
            "not authentication evidence or sufficient for BLOCKED_EXTERNAL",
            "Authentication may be diagnosed only after connectivity is established and GitHub rejects authentication",
            "Never automatically mutate credentials or request re-login",
            "account-level changes are user-owned unless separately requested",
            "Do not substitute stale tracking refs",
            "all permitted network-capable retries fail or are unavailable",
        ):
            if normalize(phrase) not in section:
                fail(f"{heading} missing live-remote retry contract: {phrase}")
    pass_line("sandbox network/live-remote retry and authentication safety validate")


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
        check_completion_correspondence_self_test()
        check_revision_two_surface()
        check_firmware_implementation_authority()
        check_legacy_control_plane_supersession()
        check_native_delegation_contract()
        check_task_configurations()
        check_live_remote_retry_contract()
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
