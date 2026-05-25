#!/usr/bin/env python3
"""Read-only consistency checks for Glyph Ultimate Tilt prehardware docs."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

PORTABLE_CONFLICT_COMMAND = (
    "grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL "
    "--exclude-dir=.git --exclude-dir=.venv || true"
)
LEGACY_CONFLICT_COMMAND = 'rg -n "^(<<<<<<<|=======|>>>>>>>)" docs tools config include src HAL || true'

REQUIRED_FILES = (
    "tools/run_glyph_ultimate_tilt_prehardware_checks.py",
    "docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md",
    "docs/calibration/glyph_ultimate_tilt_prehardware_polish_handoff.md",
    "docs/calibration/glyph_ultimate_tilt_hardware_test_package_2026-05-24.md",
    "docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md",
    "docs/calibration/glyph_ultimate_tilt_hardware_test_result_TEMPLATE.md",
    "docs/calibration/glyph_ultimate_tilt_rc_manifest.md",
)

REQUIRED_REFERENCES: dict[str, tuple[str, ...]] = {
    "docs/calibration/glyph_ultimate_tilt_hardware_test_package_2026-05-24.md": (
        "tools/run_glyph_ultimate_tilt_prehardware_checks.py",
        "docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md",
    ),
    "docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md": (
        "docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md",
    ),
    "docs/calibration/glyph_ultimate_tilt_hardware_test_result_TEMPLATE.md": (
        "docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md",
        "tools/run_glyph_ultimate_tilt_prehardware_checks.py",
    ),
    "docs/calibration/glyph_ultimate_tilt_rc_manifest.md": (
        "tools/run_glyph_ultimate_tilt_prehardware_checks.py",
        "docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md",
        PORTABLE_CONFLICT_COMMAND,
    ),
    "docs/calibration/glyph_ultimate_tilt_prehardware_polish_handoff.md": (
        "tools/run_glyph_ultimate_tilt_prehardware_checks.py",
        "docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md",
    ),
}

CALIBRATION_DOCS_DIR = REPO_ROOT / "docs" / "calibration"


def _fail(errors: list[str]) -> None:
    detail = "\n".join(f"- {entry}" for entry in errors)
    raise AssertionError(detail)


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def run() -> None:
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing required file: {relative_path}")

    for relative_path, required_tokens in REQUIRED_REFERENCES.items():
        file_path = REPO_ROOT / relative_path
        if not file_path.exists():
            continue
        text = file_path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                errors.append(f"missing reference '{token}' in {relative_path}")

    for path in sorted(CALIBRATION_DOCS_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        display = path.relative_to(REPO_ROOT).as_posix()
        if LEGACY_CONFLICT_COMMAND in text:
            errors.append(f"legacy rg conflict command found in {display}")
        if "rg conflict marker check" in text:
            errors.append(f"legacy rg conflict check label found in {display}")

    if errors:
        _fail(errors)


def main() -> None:
    try:
        run()
    except AssertionError as exc:
        print(f"glyph_ultimate_tilt_docs_consistency: FAIL\n{exc}")
        raise SystemExit(1)

    print("glyph_ultimate_tilt_docs_consistency: PASS")


if __name__ == "__main__":
    main()
