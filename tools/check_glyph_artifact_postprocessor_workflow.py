#!/usr/bin/env python3
"""Verify the bounded observed-only sidecar ordering in build.yml."""

from __future__ import annotations

from pathlib import Path

from glyph_workflow_step_contract import WorkflowStepError, executable_lines, parse_jobs


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/build.yml"


class WorkflowError(ValueError):
    pass


PROTECTED_COMMANDS = (
    'python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-checkout --candidate-sha "$GITHUB_SHA"',
    "python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-worktree --phase pre-build",
    "python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-worktree --phase post-build",
    "ls *.uf2 | xargs ./glyph_nuker",
    'python3 tools/check_glyph_artifact_postprocessor_provenance.py --write-sidecar --candidate-sha "$GITHUB_SHA" --artifact "$ARTIFACT_PATH" --sidecar "$SIDECAR_PATH"',
    'python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-sidecar --candidate-sha "$GITHUB_SHA" --artifact "$ARTIFACT_PATH" --sidecar "$SIDECAR_PATH"',
)
PROTECTED_FAMILY_MARKERS = (
    "--verify-checkout",
    "--verify-worktree",
    "ls *.uf2 | xargs ./glyph_nuker",
    "--write-sidecar",
    "--verify-sidecar",
)

EXACT_BUILD_LINES = [
    'pio run -e "$PIO_ENV"',
    'mkdir -p "$PIO_ENV"',
    'cp ".pio/build/${PIO_ENV}/firmware.${BIN_EXT}" "$ARTIFACT_PATH"',
]
EXACT_CHECKOUT_LINES = [PROTECTED_COMMANDS[0]]
EXACT_PRE_BUILD_LINES = [PROTECTED_COMMANDS[1]]
EXACT_NUKE_LINES = [
    "mv glyph_nuker $PIO_ENV/glyph_nuker",
    "cd $PIO_ENV",
    "ls *.uf2 | xargs ./glyph_nuker",
    "rm glyph_nuker",
]
EXACT_POST_BUILD_LINES = [PROTECTED_COMMANDS[2]]
EXACT_SIDECAR_LINES = [
    'export SIDECAR_PATH="$PIO_ENV/${ARTIFACT_NAME}.provenance.json"',
    'test "$SIDECAR_PATH" = "$PIO_ENV/${ARTIFACT_NAME}.provenance.json"',
    'python3 tools/check_glyph_artifact_postprocessor_provenance.py --write-sidecar --candidate-sha "$GITHUB_SHA" --artifact "$ARTIFACT_PATH" --sidecar "$SIDECAR_PATH"',
    'python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-sidecar --candidate-sha "$GITHUB_SHA" --artifact "$ARTIFACT_PATH" --sidecar "$SIDECAR_PATH"',
]
EXACT_UPLOAD_FIELDS = {"name": "Glyph_FW", "path": "${{ env.PIO_ENV }}"}


def reject_decoys_and_conditions(steps: list[object]) -> None:
    exact_blocks = (EXACT_CHECKOUT_LINES, EXACT_PRE_BUILD_LINES, EXACT_BUILD_LINES, EXACT_POST_BUILD_LINES, EXACT_NUKE_LINES, EXACT_SIDECAR_LINES)
    markers = PROTECTED_FAMILY_MARKERS + ("pio run -e", 'mkdir -p "$PIO_ENV"', 'cp ".pio/build/')
    for step in steps:
        if getattr(step, "condition", None) is not None:
            raise WorkflowError("conditional workflow step is not failure-bearing")
        lines = executable_lines(getattr(step, "run", None))
        if any(marker in line for line in lines for marker in markers) and lines not in exact_blocks:
            raise WorkflowError("protected operation has a decoy, masked, or mutated step")


def require_exact_protected_commands(steps: list[object]) -> None:
    """Require each reviewed provenance operation as one failure-bearing line."""
    executable: list[str] = []
    for step in steps:
        lines = executable_lines(getattr(step, "run", None))
        for line in lines:
            if any(marker in line for marker in PROTECTED_FAMILY_MARKERS) and line not in PROTECTED_COMMANDS:
                raise WorkflowError("protected command has non-exact or masked variant")
        if any(command in lines for command in PROTECTED_COMMANDS):
            controls = (
                "if ", "then", "fi", "else", "elif ", "while ", "until ", "do", "done",
                "function ", "(", ")", "{", "}", "<<", "\\", "set ", "trap ",
            )
            if any("<<" in line for line in lines) or any(
                line == token or line.startswith(token) or line.endswith(token)
                for line in lines for token in controls
            ):
                raise WorkflowError("protected command is wrapped in shell control flow")
        if getattr(step, "fields", set()) == {"run"}:
            executable.extend(lines)
    for command in PROTECTED_COMMANDS:
        if executable.count(command) != 1:
            raise WorkflowError(
                f"protected command must appear exactly once as an executable line: {command}"
            )


def validate(text: str) -> None:
    required = (
        "fetch-depth: 0",
        "python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-checkout",
        "python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-worktree --phase pre-build",
        "python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-worktree --phase post-build",
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
    if build_job.continue_on_error is not None:
        raise WorkflowError("build job uses a permissive failure policy")
    steps = build_job.steps
    reject_decoys_and_conditions(steps)
    require_exact_protected_commands(steps)
    checkout = [
        step for step in steps
        if any("--verify-checkout" in line for line in executable_lines(step.run))
    ]
    pre_build = [
        step for step in steps
        if any("--verify-worktree --phase pre-build" in line for line in executable_lines(step.run))
    ]
    build = [
        step for step in steps
        if any("pio run -e" in line for line in executable_lines(step.run))
    ]
    post_build = [
        step for step in steps
        if any("--verify-worktree --phase post-build" in line for line in executable_lines(step.run))
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
    if not len(checkout) == len(pre_build) == len(build) == len(post_build) == len(postprocess) == len(write) == len(verify) == len(upload) == 1:
        raise WorkflowError("identity, worktree, build, postprocessing, sidecar, and upload steps are not unique")
    positions = [steps.index(step) for step in (checkout[0], pre_build[0], build[0], post_build[0], postprocess[0], write[0], verify[0], upload[0])]
    if not positions[0] < positions[1] < positions[2] < positions[3] < positions[4] < positions[5] <= positions[6] < positions[7]:
        raise WorkflowError("identity, postprocessing, sidecar, and upload ordering drifted")
    if positions[6] + 1 != positions[7]:
        raise WorkflowError("sidecar verification must immediately precede upload")
    if executable_lines(pre_build[0].run) != EXACT_PRE_BUILD_LINES:
        raise WorkflowError("pre-build worktree gate drifted")
    if executable_lines(post_build[0].run) != EXACT_POST_BUILD_LINES:
        raise WorkflowError("post-build worktree gate drifted")
    if executable_lines(build[0].run) != EXACT_BUILD_LINES:
        raise WorkflowError("build step command block drifted")
    if executable_lines(postprocess[0].run) != EXACT_NUKE_LINES:
        raise WorkflowError("nuke step command block drifted")
    if executable_lines(write[0].run) != EXACT_SIDECAR_LINES:
        raise WorkflowError("sidecar step command block drifted")
    if getattr(upload[0], "fields", set()) != {"uses", "with"} or upload[0].with_fields != EXACT_UPLOAD_FIELDS:
        raise WorkflowError("upload step fields drifted")
    if sum(1 for step in steps if step.uses and "upload-artifact" in step.uses) != 1:
        raise WorkflowError("alternate upload action is present")
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
            "masked_build": workflow.replace('pio run -e "$PIO_ENV"', 'pio run -e "$PIO_ENV" || true', 1),
            "decoy_copy": workflow.replace(
                'cp ".pio/build/${PIO_ENV}/firmware.${BIN_EXT}" "$ARTIFACT_PATH"',
                'cp ".pio/build/wrong/firmware.uf2" "$ARTIFACT_PATH"', 1,
            ),
            "post_verify_mutation": workflow.replace(
                PROTECTED_COMMANDS[5], f"{PROTECTED_COMMANDS[5]}\n        echo mutation", 1
            ),
            "intervening_mutation": workflow.replace(
                "    - name: Publish ${{ matrix.env }} artifacts",
                "    - name: Intervening mutation\n      run: echo mutation\n\n    - name: Publish ${{ matrix.env }} artifacts", 1,
            ),
            "extra_upload_field": workflow.replace(
                "        path: ${{ env.PIO_ENV }}",
                "        path: ${{ env.PIO_ENV }}\n        retention-days: 1", 1,
            ),
            "alternate_upload": workflow.replace(
                "actions/upload-artifact@v4", "actions/upload-artifact@v3", 1
            ),
            "job_continue_on_error": workflow.replace(
                "  build:\n", "  build:\n    continue-on-error: true\n", 1
            ),
        }
        for index, command in enumerate(PROTECTED_COMMANDS):
            mutations[f"masked_{index}"] = workflow.replace(command, f"{command} || true", 1)
            mutations[f"trailing_{index}"] = workflow.replace(command, f"{command}; true", 1)
            mutations[f"duplicate_{index}"] = workflow.replace(
                command, f"{command}\n        {command}", 1
            )
            mutations[f"conditional_{index}"] = workflow.replace(
                command, f"if true; then\n        {command}\n        fi", 1
            )
            mutations[f"subshell_{index}"] = workflow.replace(
                command, f"(\n        {command}\n        )", 1
            )
            mutations[f"function_{index}"] = workflow.replace(
                command, f"run_protected() {{\n        {command}\n        }}\n        run_protected", 1
            )
            mutations[f"while_{index}"] = workflow.replace(
                command, f"while true; do\n        {command}\n        done", 1
            )
            mutations[f"set_errexit_{index}"] = workflow.replace(
                command, f"set +e\n        {command}", 1
            )
            mutations[f"set_pipefail_{index}"] = workflow.replace(
                command, f"set +o pipefail\n        {command}", 1
            )
            mutations[f"masked_duplicate_{index}"] = workflow.replace(
                command, f"{command}\n        {command} || true", 1
            )
            mutations[f"heredoc_{index}"] = workflow.replace(
                command, f"cat <<EOF\n        {command}\n        EOF", 1
            )
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
