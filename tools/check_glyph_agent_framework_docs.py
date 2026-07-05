#!/usr/bin/env python3
"""Validate Glyph agent framework documentation surface."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = (
    "AGENTS.md",
    "CLAUDE.md",
    "docs/agent_framework/README.md",
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
    "architecture_specialist",
    "implementer",
    "validator_reviewer",
    "docs_status_clerk",
    "judge_watchdog",
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


def require_phrase(rel_path: str, phrase: str) -> None:
    text = read_required(rel_path)
    if normalize(phrase) not in normalize(text):
        fail(f"{rel_path} missing required phrase: {phrase}")


def all_framework_text() -> str:
    parts: list[str] = []
    for path in (REPO_ROOT / "docs/agent_framework").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json"}:
            parts.append(path.read_text(encoding="utf-8"))
    parts.append(read_required("AGENTS.md"))
    parts.append(read_required("CLAUDE.md"))
    return "\n".join(parts)


def check_required_paths() -> None:
    for rel_path in REQUIRED_DOCS:
        read_required(rel_path)
    for rel_path in REQUIRED_SCHEMAS:
        load_json(rel_path)
    pass_line("required docs and JSON schemas exist and parse")


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
    required_fields = (
        "openai_codex_default",
        "openai_reasoning_effort",
        "claude_default",
        "claude_effort",
        "escalation_trigger",
        "de_escalation_trigger",
        "output_contract",
        "tool_permission_posture",
    )
    for role in REQUIRED_ROLES:
        role_entry = roles[role]
        if not isinstance(role_entry, dict):
            fail(f"model_routing role {role} must be an object")
        missing_fields = [field for field in required_fields if field not in role_entry]
        if missing_fields:
            fail(f"model_routing role {role} missing fields: {', '.join(missing_fields)}")
    pass_line("model routing includes all required roles and fields")


def check_contract_phrases() -> None:
    framework_text = normalize(all_framework_text())
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
    require_phrase("CLAUDE.md", "docs/agent_framework/README.md")
    pass_line("AGENTS.md and CLAUDE.md point to framework entrypoints")


def check_forbidden_claims() -> None:
    bad: list[str] = []
    for raw_line in all_framework_text().splitlines():
        line = normalize(raw_line)
        for claim in BAD_ACTIVE_CLAIMS:
            if claim not in line:
                continue
            if any(marker in line for marker in SAFE_NEGATION_MARKERS):
                continue
            bad.append(f"{claim} [{raw_line.strip()}]")
    if bad:
        fail("forbidden active/supported claims found: " + ", ".join(bad))
    framework_text = normalize(all_framework_text())
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
        check_model_routing()
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
