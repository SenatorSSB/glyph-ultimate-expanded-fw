#!/usr/bin/env python3
"""Validate the offline invalid corpus for the Glyph runtime config candidate validator."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from glyph_runtime_config_candidate_validator import (
    load_json_object,
    validate_runtime_config_candidate,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_candidate_invalid_corpus_2026-06-03.json"
)
BASELINE_FIXTURE_PATH = (
    REPO_ROOT / "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json"
)
DOC_PATH = REPO_ROOT / "docs/calibration/glyph_runtime_config_candidate_invalid_corpus_2026-06-03.md"

REQUIRED_DOC_PHRASES = (
    "docs/tools-only corpus",
    "not firmware",
    "not runtime-loaded config",
    "not serial/device write behavior",
    "not hardware validation",
    "not nunchuk hardware validation",
)


class InvalidCorpusCheckError(ValueError):
    """Raised when the invalid corpus or validator behavior drifts."""


def fail(message: str) -> None:
    raise InvalidCorpusCheckError(message)


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    return value


def load_corpus() -> dict[str, Any]:
    corpus = load_json_object(CORPUS_PATH)
    expected = {
        "schema_name": "glyph_runtime_config_candidate_invalid_corpus",
        "corpus_version": 1,
        "status": "negative_validator_corpus",
        "hardware_status": "not_new_hardware_result",
        "validator_tool": "tools/glyph_runtime_config_candidate_validator.py",
        "baseline_fixture": "docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json",
    }
    for key, value in expected.items():
        if corpus.get(key) != value:
            fail(f"corpus {key} must be {value!r}")
    return corpus


def apply_path(container: Any, path: list[Any], value: Any) -> None:
    if not path:
        fail("mutation path must not be empty")
    current = container
    for segment in path[:-1]:
        if isinstance(current, dict) and isinstance(segment, str):
            if segment not in current:
                fail(f"mutation path missing object key {segment!r}")
            current = current[segment]
        elif isinstance(current, list) and isinstance(segment, int):
            if segment < 0 or segment >= len(current):
                fail(f"mutation path list index out of range: {segment}")
            current = current[segment]
        else:
            fail(f"mutation path segment {segment!r} is incompatible with current container")

    final = path[-1]
    if isinstance(current, dict) and isinstance(final, str):
        current[final] = value
        return
    if isinstance(current, list) and isinstance(final, int):
        if final < 0 or final >= len(current):
            fail(f"mutation path list index out of range: {final}")
        current[final] = value
        return
    fail(f"mutation path final segment {final!r} is incompatible with current container")


def delete_path(container: Any, path: list[Any]) -> None:
    if not path:
        fail("delete path must not be empty")
    current = container
    for segment in path[:-1]:
        if isinstance(current, dict) and isinstance(segment, str):
            if segment not in current:
                fail(f"delete path missing object key {segment!r}")
            current = current[segment]
        elif isinstance(current, list) and isinstance(segment, int):
            if segment < 0 or segment >= len(current):
                fail(f"delete path list index out of range: {segment}")
            current = current[segment]
        else:
            fail(f"delete path segment {segment!r} is incompatible with current container")

    final = path[-1]
    if isinstance(current, dict) and isinstance(final, str):
        if final not in current:
            fail(f"delete path missing object key {final!r}")
        del current[final]
        return
    if isinstance(current, list) and isinstance(final, int):
        if final < 0 or final >= len(current):
            fail(f"delete path list index out of range: {final}")
        del current[final]
        return
    fail(f"delete path final segment {final!r} is incompatible with current container")


def apply_mutation(payload: dict[str, Any], mutation_ops: list[dict[str, Any]]) -> dict[str, Any]:
    mutated = copy.deepcopy(payload)
    for op in mutation_ops:
        action = op.get("op")
        path = require_list(op.get("path"), "mutation path")
        if not all(isinstance(segment, (str, int)) for segment in path):
            fail("mutation path segments must be strings or integers")
        if action == "set":
            apply_path(mutated, path, op.get("value"))
        elif action == "delete":
            delete_path(mutated, path)
        else:
            fail(f"unsupported mutation op: {action!r}")
    return mutated


def validate_doc() -> None:
    lowered = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in lowered:
            fail(f"{DOC_PATH.relative_to(REPO_ROOT)} missing required phrase: {phrase}")


def main() -> int:
    print("glyph_runtime_config_candidate_invalid_corpus")
    try:
        corpus = load_corpus()
        validate_doc()
        baseline = load_json_object(BASELINE_FIXTURE_PATH)
        if validate_runtime_config_candidate(baseline):
            fail("baseline runtime config candidate sample must pass the validator")

        cases = require_list(corpus.get("cases"), "corpus cases")
        if not cases:
            fail("corpus cases must not be empty")

        invalid_cases = 0
        for case in cases:
            case_obj = require_object(case, "corpus case")
            case_id = case_obj.get("case_id")
            mutation = case_obj.get("mutation")
            expected_codes = require_list(case_obj.get("expected_error_codes"), f"{case_id}.expected_error_codes")
            mutation_ops = require_list(case_obj.get("payload"), f"{case_id}.payload")

            if not isinstance(case_id, str) or not case_id:
                fail("each corpus case must have a string case_id")
            if not isinstance(mutation, str) or not mutation:
                fail(f"{case_id} must have a string mutation")
            if not all(isinstance(code, str) for code in expected_codes):
                fail(f"{case_id}.expected_error_codes must be a string list")
            if not all(isinstance(op, dict) for op in mutation_ops):
                fail(f"{case_id}.payload must be a list of mutation objects")

            mutated = apply_mutation(baseline, mutation_ops)
            issues = validate_runtime_config_candidate(mutated)
            if not issues:
                fail(f"{case_id} unexpectedly passed validation")

            actual_codes = {issue.code for issue in issues}
            missing = sorted(set(expected_codes) - actual_codes)
            if missing:
                fail(f"{case_id} missing expected error code(s): {', '.join(missing)}")
            invalid_cases += 1

        print("status=PASS")
        print(f"invalid_cases={invalid_cases}")
        print("hardware_status=not_new_hardware_result")
        return 0
    except (OSError, ValueError, InvalidCorpusCheckError) as exc:
        print("status=FAIL")
        print("invalid_cases=0")
        print("hardware_status=not_new_hardware_result")
        print(f"error={exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
