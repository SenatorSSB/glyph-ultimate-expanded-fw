#!/usr/bin/env python3
"""Parse and inspect the small, reviewed GitHub Actions workflow subset."""
from __future__ import annotations

from dataclasses import dataclass, field
import re


class WorkflowStepError(ValueError):
    pass


@dataclass
class Step:
    name: str | None = None
    run: str | None = None
    uses: str | None = None
    condition: str | None = None
    fields: set[str] = field(default_factory=set)


@dataclass
class Job:
    name: str
    needs: str | None = None
    continue_on_error: str | None = None
    steps: list[Step] = field(default_factory=list)


_KEY = re.compile(r"(?P<indent> *)(?P<key>[A-Za-z0-9_-]+):(?:[ ](?P<value>.*))?$")


def _scalar(value: str | None, label: str) -> str:
    if value is None or not value.strip() or value.strip() in {"|", ">", "|-", ">-", "|+", ">+"}:
        raise WorkflowStepError(f"unsupported scalar shape: {label}")
    value = value.strip()
    if value[0] in "[{" or value.endswith(("}", "]")):
        raise WorkflowStepError(f"unsupported scalar shape: {label}")
    return value


def parse_jobs(text: str) -> dict[str, Job]:
    """Parse jobs, needs, failure policy, and step run/uses fields only."""
    lines = text.splitlines()
    if any("\t" in line for line in lines):
        raise WorkflowStepError("tabs are unsupported")
    if any(re.match(r"^\s*#", line) or re.search(r"(^|\s)#", line) for line in lines):
        raise WorkflowStepError("comments are unsupported in the reviewed subset")
    jobs_at = next((i for i, line in enumerate(lines) if line == "jobs:"), None)
    if jobs_at is None:
        raise WorkflowStepError("jobs mapping missing")
    jobs: dict[str, Job] = {}
    current: Job | None = None
    current_step: Step | None = None
    i = jobs_at + 1
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        match = _KEY.match(line)
        if match and len(match.group("indent")) == 2:
            key, value = match.group("key"), match.group("value")
            if key in jobs:
                raise WorkflowStepError(f"duplicate job: {key}")
            current = Job(key)
            jobs[key] = current
            current_step = None
            if value is not None:
                raise WorkflowStepError("job must be a mapping")
            i += 1
            continue
        if current is None:
            raise WorkflowStepError("content outside job")
        if re.match(r"^    steps:\s*$", line):
            i += 1
            while i < len(lines):
                candidate = lines[i]
                if not candidate.strip():
                    i += 1
                    continue
                if re.match(r"^  [A-Za-z0-9_-]+:", candidate):
                    break
                if not candidate.startswith("    - "):
                    raise WorkflowStepError("unsupported step shape")
                item = candidate[6:]
                step = Step()
                current.steps.append(step)
                current_step = step
                if item.startswith("name:"):
                    step.name = _scalar(item[5:].lstrip(), "step name")
                else:
                    raise WorkflowStepError("step must begin with name")
                i += 1
                while i < len(lines):
                    detail = lines[i]
                    if not detail.strip():
                        i += 1
                        continue
                    if detail.startswith("    - ") or re.match(r"^  [A-Za-z0-9_-]+:", detail):
                        break
                    detail_match = _KEY.match(detail)
                    if not detail_match or len(detail_match.group("indent")) != 6:
                        # Nested 'with' values are deliberately outside this parser.
                        if detail.startswith("      ") and current_step.fields and "with" in current_step.fields:
                            i += 1
                            continue
                        raise WorkflowStepError("unsupported step field shape")
                    key, value = detail_match.group("key"), detail_match.group("value")
                    if key in step.fields:
                        raise WorkflowStepError(f"duplicate step field: {key}")
                    step.fields.add(key)
                    if key == "run":
                        if value not in {"|", "|-", "|+"}:
                            step.run = _scalar(value, "run")
                        else:
                            block: list[str] = []
                            i += 1
                            while i < len(lines) and (not lines[i].strip() or lines[i].startswith("      ")):
                                block.append(lines[i][6:] if lines[i].startswith("      ") else "")
                                i += 1
                            step.run = "\n".join(block)
                            continue
                    elif key == "uses":
                        step.uses = _scalar(value, "uses")
                    elif key == "with":
                        if value is not None:
                            raise WorkflowStepError("with must be a mapping")
                    elif key in {"name", "if", "env", "shell", "working-directory"}:
                        scalar = _scalar(value, key)
                        if key == "if":
                            step.condition = scalar
                    else:
                        raise WorkflowStepError(f"unsupported step field: {key}")
                    i += 1
            continue
        mapping = _KEY.match(line)
        if not mapping or len(mapping.group("indent")) != 4:
            raise WorkflowStepError("unsupported job field shape")
        key, value = mapping.group("key"), mapping.group("value")
        if key == "needs":
            if current.needs is not None:
                raise WorkflowStepError("duplicate needs")
            current.needs = _scalar(value, "needs")
        elif key == "continue-on-error":
            if current.continue_on_error is not None:
                raise WorkflowStepError("duplicate continue-on-error")
            current.continue_on_error = _scalar(value, "continue-on-error")
        elif key in {"runs-on", "env", "strategy", "permissions"}:
            # These mappings are outside the contract; reject scalar shorthand.
            if value is not None and key in {"env", "strategy", "permissions"}:
                raise WorkflowStepError(f"unsupported {key} shape")
            if value is None and key in {"env", "strategy", "permissions"}:
                i += 1
                while i < len(lines) and (
                    not lines[i].strip()
                    or (len(lines[i]) > 4 and not re.match(r"^  [A-Za-z0-9_-]+:", lines[i]) and lines[i] != "    steps:")
                ):
                    i += 1
                continue
        else:
            raise WorkflowStepError(f"unsupported job field: {key}")
        i += 1
    if not jobs:
        raise WorkflowStepError("no jobs")
    return jobs


def executable_lines(run: str | None) -> list[str]:
    if run is None:
        return []
    return [line.strip() for line in run.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def validate_current_workflow(text: str, *, validation_job: str, aggregate: str, publication_tokens: list[str]) -> None:
    jobs = parse_jobs(text)
    if validation_job not in jobs:
        raise WorkflowStepError("validation job missing")
    validation = jobs[validation_job]
    matches = [
        step for step in validation.steps
        if aggregate in executable_lines(step.run)
        and step.condition not in {"false", "False", "FALSE", "${{ false }}"}
    ]
    if len(matches) != 1:
        raise WorkflowStepError("aggregate is not exactly one executable validation step")
    for job in jobs.values():
        if job.continue_on_error is not None:
            raise WorkflowStepError(f"permissive failure policy in {job.name}")
        if any(step.condition is not None for step in job.steps):
            raise WorkflowStepError(f"conditional workflow step in {job.name}")
        local_publication = any(
            any(token in line for token in publication_tokens)
            for step in job.steps for line in executable_lines(step.run)
        ) or any(
            step.uses and any(token in step.uses for token in publication_tokens)
            for step in job.steps
        )
        if local_publication and job.needs != validation_job:
            raise WorkflowStepError(f"publication job {job.name} is not dominated by validation")
