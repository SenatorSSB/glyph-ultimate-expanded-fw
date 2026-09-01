#!/usr/bin/env python3
"""Verify the bounded observed-only sidecar ordering in build.yml."""

from __future__ import annotations

from pathlib import Path

from glyph_workflow_step_contract import WorkflowStepError, executable_lines, parse_jobs


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/build.yml"


class WorkflowError(ValueError):
    pass


def validate(text: str) -> None:
    required = (
        "fetch-depth: 0",
        "python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-checkout",
        "--candidate-sha \"$GITHUB_SHA\"",
        "--write-sidecar",
        "--verify-sidecar",
        "--artifact \"$ARTIFACT_PATH\"",
        "--sidecar \"$SIDECAR_PATH\"",
        'test "$SIDECAR_PATH" = "$PIO_ENV/${ARTIFACT_NAME}.provenance.json"',
        "path: ${{ env.PIO_ENV }}",
        "actions/upload-artifact@v4",
    )
    for token in required:
        if token not in text:
            raise WorkflowError(f"missing workflow token: {token}")
    try:
        jobs = parse_jobs(text)
    except WorkflowStepError as exc:
        raise WorkflowError(str(exc)) from exc
    build_job = jobs.get("build")
    if build_job is None:
        raise WorkflowError("build job missing")
    steps = build_job.steps
    checkout = [
        step for step in steps
        if any("--verify-checkout" in line for line in executable_lines(step.run))
    ]
    build = [
        step for step in steps
        if any("pio run -e" in line for line in executable_lines(step.run))
    ]
    postprocess = [
        step for step in steps
        if any("ls *.uf2 | xargs ./glyph_nuker" in line for line in executable_lines(step.run))
    ]
    write = [
        step for step in steps
        if any("--write-sidecar" in line for line in executable_lines(step.run))
    ]
    verify = [
        step for step in steps
        if any("--verify-sidecar" in line for line in executable_lines(step.run))
    ]
    upload = [step for step in steps if step.uses == "actions/upload-artifact@v4"]
    if not len(checkout) == len(build) == len(postprocess) == len(write) == len(verify) == len(upload) == 1:
        raise WorkflowError("identity, build, postprocessing, sidecar, and upload steps are not unique")
    positions = [steps.index(step) for step in (checkout[0], build[0], postprocess[0], write[0], verify[0], upload[0])]
    if not positions[0] < positions[1] < positions[2] < positions[3] <= positions[4] < positions[5]:
        raise WorkflowError("identity, postprocessing, sidecar, and upload ordering drifted")
    sidecar_lines = executable_lines(write[0].run)
    if not any("--write-sidecar" in line for line in sidecar_lines):
        raise WorkflowError("sidecar write command is not executable")
    if not any("--verify-sidecar" in line for line in sidecar_lines):
        raise WorkflowError("sidecar verification command is not executable")
    if next(i for i, line in enumerate(sidecar_lines) if "--write-sidecar" in line) >= next(
        i for i, line in enumerate(sidecar_lines) if "--verify-sidecar" in line
    ):
        raise WorkflowError("sidecar verification precedes sidecar write")
    if "build-device-config.yml" in text:
        raise WorkflowError("unresolved external workflow was touched")


def main() -> int:
    try:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        validate(workflow)
        mutations = {
            "remove_checkout_gate": workflow.replace(
                "python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-checkout --candidate-sha \"$GITHUB_SHA\"", "", 1
            ),
            "remove_upload_dependency": workflow.replace(
                "python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-sidecar --candidate-sha \"$GITHUB_SHA\" --artifact \"$ARTIFACT_PATH\" --sidecar \"$SIDECAR_PATH\"",
                "", 1,
            ),
            "remove_sidecar": workflow.replace(
                "python3 tools/check_glyph_artifact_postprocessor_provenance.py --write-sidecar", "", 1
            ),
            "sidecar_outside_upload_directory": workflow.replace(
                'test "$SIDECAR_PATH" = "$PIO_ENV/${ARTIFACT_NAME}.provenance.json"',
                'test "$SIDECAR_PATH" = "$ARTIFACT_NAME.provenance.json"', 1,
            ),
            "upload_outside_sidecar_directory": workflow.replace(
                "path: ${{ env.PIO_ENV }}",
                "path: ${{ env.ARTIFACT_NAME }}", 1,
            ),
            "comment_only_verify": workflow.replace(
                "python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-sidecar",
                "# python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-sidecar", 1,
            ),
        }
        for case, mutated in mutations.items():
            try:
                validate(mutated)
            except (ValueError, WorkflowError):
                continue
            raise WorkflowError(f"adversarial case accepted: {case}")
    except (OSError, ValueError, WorkflowError) as exc:
        print(f"glyph_artifact_postprocessor_workflow: FAIL: {exc}")
        return 1
    print("glyph_artifact_postprocessor_workflow: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
