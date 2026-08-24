#!/usr/bin/env python3
"""Verify the bounded observed-only sidecar ordering in build.yml."""

from __future__ import annotations

from pathlib import Path


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
    checkout = text.index("python3 tools/check_glyph_artifact_postprocessor_provenance.py --verify-checkout")
    build = text.index("pio run -e", checkout)
    postprocess = text.index("ls *.uf2 | xargs ./glyph_nuker", build)
    write = text.index("--write-sidecar", postprocess)
    verify = text.index("--verify-sidecar", write)
    upload = text.index("actions/upload-artifact@v4", verify)
    if not checkout < build or not build < postprocess < write < verify < upload:
        raise WorkflowError("identity, postprocessing, sidecar, and upload ordering drifted")
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
