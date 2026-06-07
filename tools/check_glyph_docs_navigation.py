#!/usr/bin/env python3
"""Validate Glyph documentation navigation and current roadmap entrypoints."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class DocsNavigationError(AssertionError):
    """Raised when docs navigation guardrails drift."""


def fail(message: str) -> None:
    raise DocsNavigationError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_required(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        fail(f"missing required path: {rel_path}")
    return path.read_text(encoding="utf-8")


def require_phrases(rel_path: str, phrases: tuple[str, ...]) -> None:
    text = read_required(rel_path)
    missing = [phrase for phrase in phrases if phrase not in text]
    if missing:
        fail(f"{rel_path} missing required phrases: " + ", ".join(missing))


def main() -> int:
    required_paths = (
        "README.md",
        "AGENTS.md",
        "docs/CURRENT_STATE.md",
        "docs/ROADMAP.md",
        "docs/WORKFLOW.md",
        "docs/calibration/README.md",
        "docs/calibration/INDEX.md",
        "docs/calibration/archive_policy.md",
    )
    for rel_path in required_paths:
        if not (REPO_ROOT / rel_path).exists():
            fail(f"missing required path: {rel_path}")

    main_docs = (
        "docs/CURRENT_STATE.md",
        "docs/ROADMAP.md",
        "docs/WORKFLOW.md",
        "AGENTS.md",
        "docs/calibration/README.md",
    )
    require_phrases("README.md", main_docs)
    require_phrases("AGENTS.md", ("docs/CURRENT_STATE.md", "docs/ROADMAP.md", "docs/WORKFLOW.md"))

    require_phrases(
        "docs/CURRENT_STATE.md",
        (
            "GFW3 runtime remap work is merged, user hardware-tested, and recorded",
            "Preservation hardware pass is recorded for applicable non-nunchuk scope",
            "Official Glyph configurator corpus is present",
            "Runtime-loaded config is not implemented",
            "WebSerial/device write is not implemented",
            "Protobuf binary write is not implemented",
            "Firmware flashing automation is not implemented",
            "External adapter output is not implemented",
            "Current Readiness Categories",
            "The user is not currently blocking runtime-loaded config",
            "User domain input is required only for product/domain choices",
            "No nunchuk validation is claimed",
            "No universal official configurator compatibility claim is made",
            "No direct device write is implemented or claimed",
        ),
    )

    require_phrases(
        "docs/ROADMAP.md",
        (
            "Phase 0 - Current Hardcoded Firmware Baseline",
            "Phase 1 - Senscope Neutral Profile Format",
            "Phase 2 - Generated-Config/Evaluator Bridge",
            "Phase 3 - Generated C++ Constants / Firmware Build Path",
            "Phase 4 - Offline Official Configurator Export Candidate",
            "Phase 5 - Manual Import/Export And Hardware Validation Loop",
            "Phase 6 - Stable Firmware + Bounded Config-Owned Modifier Data",
            "Phase 7 - Runtime-Loaded Config Interpreter",
            "Phase 8 - WebSerial/Device-Write / Push-To-Device Workflow",
            "Status Taxonomy",
            "READY_FOR_ENGINEERING_DESIGN",
            "READY_FOR_SOURCE_RESEARCH",
            "requires_user_domain_input",
            "requires_user_product_approval",
            "Runtime-loaded config is not implemented",
            "WebSerial/device write is not implemented",
            "Protobuf binary write is not implemented",
        ),
    )

    require_phrases(
        "docs/WORKFLOW.md",
        (
            "Branch Categories",
            "Docs/tools",
            "Corpus/evidence",
            "Firmware behavior",
            "Hardware result",
            "Exporter/adapter",
            "Runtime-loaded config/device write",
            "Inspection Policy",
            "Post-merge inspection is required",
            "Hardware Test Policy",
            "Source Authority Policy",
            "Autonomy And Approval Policy",
            "Docs/tools, source research, and engineering design can proceed autonomously",
            "User product approval is required before",
        ),
    )

    correction_packet = REPO_ROOT / "docs/calibration/glyph_external_remapper_misattribution_correction_2026-06-06.md"
    if correction_packet.exists():
        for rel_path in (
            "AGENTS.md",
            "docs/CURRENT_STATE.md",
            "docs/calibration/README.md",
            "docs/calibration/INDEX.md",
            "docs/calibration/archive_policy.md",
        ):
            require_phrases(rel_path, ("quarantined",))
        require_phrases("AGENTS.md", ("Official Glyph configurator corpus is the primary corpus",))

    for rel_path in ("README.md", "docs/CURRENT_STATE.md", "docs/ROADMAP.md"):
        require_phrases(
            rel_path,
            (
                "Runtime-loaded config",
                "WebSerial/device write",
                "protobuf",
                "device write",
            ),
        )

    print("glyph_docs_navigation: PASS")
    for rel_path in required_paths:
        print(f"- {rel_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
