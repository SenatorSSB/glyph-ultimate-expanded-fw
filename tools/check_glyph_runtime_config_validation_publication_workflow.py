#!/usr/bin/env python3
"""Statically verify validation-before-publication CI workflow invariants."""
from __future__ import annotations

import json
import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/build.yml"
FIXTURE = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_publication_workflow.json"


class WorkflowError(ValueError):
    pass


def load_fixture() -> dict[str, object]:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 2:
        raise WorkflowError("invalid workflow fixture")
    return value


def tracked_workflows() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        raise WorkflowError("could not discover tracked workflow files")
    return sorted(
        path for path in completed.stdout.splitlines()
        if path.endswith((".yml", ".yaml"))
        and (path.startswith(".github/workflows/") or "/.github/workflows/" in path)
    )


def publication_routes(text: str) -> list[dict[str, str]]:
    routes: list[dict[str, str]] = []
    for job, body in job_blocks(text).items():
        if "pio run -e" in body:
            routes.append({"job": job, "mechanism": "shell", "token": "pio run -e"})
        if "glyph_nuker" in body:
            routes.append({"job": job, "mechanism": "shell", "token": "glyph_nuker"})
        for action in re.findall(r"(?m)^\s*(?:-\s*)?uses:\s*([^\s]+)", body):
            if "/.github/workflows/" in action:
                routes.append({"job": job, "mechanism": "reusable_workflow", "token": action})
            elif "upload-artifact" in action or "action-gh-release" in action:
                routes.append({"job": job, "mechanism": "action", "token": action})
    return sorted(routes, key=lambda item: (item["job"], item["mechanism"], item["token"]))


def validate_route_census(fixture: dict[str, object]) -> None:
    census = fixture.get("workflow_census")
    if not isinstance(census, list) or not census:
        raise WorkflowError("workflow census is empty")
    expected_paths = sorted(str(item["path"]) for item in census)
    if tracked_workflows() != expected_paths:
        raise WorkflowError("tracked workflow inventory differs from census")
    for item in census:
        if not isinstance(item, dict):
            raise WorkflowError("invalid workflow census entry")
        relative = str(item["path"])
        path = ROOT / relative
        if not path.is_file():
            raise WorkflowError(f"missing censused workflow: {relative}")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise WorkflowError(f"workflow hash drift: {relative}")
        text = raw.decode("utf-8")
        events = []
        for event in ("push", "pull_request", "workflow_call"):
            if re.search(rf"(?m)^\s*{event}:\s*$", text) or re.search(
                rf"(?m)^\s*on:\s*\[[^\]]*\b{event}\b[^\]]*\]", text
            ):
                events.append(event)
        if events != item["events"]:
            raise WorkflowError(f"workflow trigger drift: {relative}")
        if publication_routes(text) != item["publication_routes"]:
            raise WorkflowError(f"publication route drift: {relative}")
        if item["classification"] not in {"CURRENT_GATED", "UNRESOLVED_EXTERNAL"}:
            raise WorkflowError(f"invalid workflow classification: {relative}")
        if item["classification"] == "CURRENT_GATED" and item["gate"] != "validation":
            raise WorkflowError("current workflow is not gated by validation")
        if item["classification"] == "UNRESOLVED_EXTERNAL" and item["gate"] is not None:
            raise WorkflowError("unresolved external workflow has a fabricated gate")
    if not any(item["classification"] == "UNRESOLVED_EXTERNAL" for item in census):
        raise WorkflowError("unresolved external route was not retained")
    if fixture.get("all_tracked_routes_gated") is not False:
        raise WorkflowError("all-routes-gated claim must remain false")


def job_blocks(text: str) -> dict[str, str]:
    matches = re.finditer(
        r"(?ms)^  (?P<job>[A-Za-z0-9_-]+):\n(?P<body>(?:(?!^  [A-Za-z0-9_-]+:\n).)*)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        text,
    )
    return {match.group("job"): match.group("body") for match in matches}


def validate(text: str, fixture: dict[str, object]) -> None:
    for event in fixture["required_events"]:
        if not re.search(rf"(?m)^\s*{re.escape(event)}\s*$", text):
            raise WorkflowError(f"missing event: {event}")
    for token in fixture["required_tokens"]:
        if token not in text:
            raise WorkflowError(f"missing required token: {token}")
    if "continue-on-error:" in text or re.search(r"\bif:\s*always\(\)", text):
        raise WorkflowError("publication must fail closed on validation failure")
    jobs = job_blocks(text)
    validation_job = str(fixture["validation_job"])
    publication_job = str(fixture["publication_job"])
    if validation_job not in jobs or publication_job not in jobs:
        raise WorkflowError("validation/publication jobs missing")
    validation = jobs[validation_job]
    if "python3 tools/run_glyph_runtime_config_validation.py --json" not in validation:
        raise WorkflowError("current aggregate is not in validation job")
    if "fetch-depth: 0" not in validation or "git fetch --no-tags origin" not in validation:
        raise WorkflowError("validation job lacks full-history trusted-base setup")
    if "GITHUB_BASE_REF" not in validation or "origin/configurator" not in validation:
        raise WorkflowError("detached CI comparison base is not explicit")
    for job, body in jobs.items():
        if any(token in body for token in fixture["publication_tokens"]):
            if not re.search(r"(?m)^    needs:\s*validation\s*$", body):
                raise WorkflowError(f"publication job {job} is not gated by validation")


def main() -> int:
    try:
        fixture = load_fixture()
        validate_route_census(fixture)
        workflow = WORKFLOW.read_text(encoding="utf-8")
        validate(workflow, fixture)
        cases = []
        for mutation in fixture["negative_mutations"]:
            mutated = workflow.replace(mutation["old"], mutation["new"], 1)
            if mutated == workflow:
                raise WorkflowError(f"mutation did not apply: {mutation['id']}")
            try:
                validate(mutated, fixture)
            except WorkflowError:
                cases.append(mutation["id"])
            else:
                raise WorkflowError(f"adversarial mutation accepted: {mutation['id']}")
    except (OSError, TypeError, KeyError, json.JSONDecodeError, WorkflowError) as exc:
        print(f"glyph_runtime_config_validation_publication_workflow: FAIL: {exc}")
        return 1
    print("glyph_runtime_config_validation_publication_workflow: PASS; cases=" + ",".join(cases))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
