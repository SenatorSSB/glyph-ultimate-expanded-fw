#!/usr/bin/env python3
"""Validate Glyph documentation navigation and current roadmap entrypoints."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class DocsNavigationError(AssertionError):
    """Raised when docs navigation guardrails drift."""


def fail(message: str) -> None:
    raise DocsNavigationError(message)


def read_required(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        fail(f"missing required path: {rel_path}")
    return path.read_text(encoding="utf-8")


def normalize(text: str) -> str:
    return " ".join(text.replace("`", "").split()).lower()


def require_phrases(rel_path: str, phrases: tuple[str, ...]) -> None:
    text = read_required(rel_path)
    normalized = normalize(text)
    missing = [phrase for phrase in phrases if normalize(phrase) not in normalized]
    if missing:
        fail(f"{rel_path} missing required phrases: " + ", ".join(missing))


def main() -> int:
    required_paths = (
        "README.md",
        "AGENTS.md",
        "docs/AGENT_CONTEXT.md",
        "docs/CURRENT_STATE.md",
        "docs/ROADMAP.md",
        "docs/WORKFLOW.md",
        "docs/archive/README.md",
        "docs/calibration/README.md",
        "docs/calibration/INDEX.md",
        "docs/calibration/archive_policy.md",
        "docs/export/README.md",
        "docs/runtime_config/README.md",
        "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md",
        "docs/runtime_config/coordinate_native_runtime_profile_contract.md",
        "docs/runtime_config/runtime_config_activation_alternatives_a_f.md",
        "docs/runtime_config/fixtures/coordinate_native_runtime_profile_contract.json",
        "docs/agent_framework/README.md",
        "docs/agent_framework/MODEL_ROUTING.md",
        "docs/agent_framework/SUPERVISOR_CONTRACT.md",
        "docs/agent_framework/SUBAGENT_CONTRACTS.md",
        "docs/agent_framework/VALIDATION_AND_GATES.md",
    )
    for rel_path in required_paths:
        read_required(rel_path)

    require_phrases(
        "README.md",
        (
            "docs/CURRENT_STATE.md",
            "docs/ROADMAP.md",
            "docs/WORKFLOW.md",
            "AGENTS.md",
            "docs/calibration/README.md",
            "docs/export/README.md",
        ),
    )
    require_phrases(
        "AGENTS.md",
        (
            "docs/AGENT_CONTEXT.md",
            "docs/CURRENT_STATE.md",
            "docs/ROADMAP.md",
            "docs/WORKFLOW.md",
            "docs/agent_framework/README.md",
        ),
    )

    require_phrases(
        "docs/AGENT_CONTEXT.md",
        (
            "current known-good branch state",
            "latest Y2 layout source-owned port",
            "source-owned table/routing source",
            "Active RuntimeConfigView selection is unchanged",
            "candidate.view is not active",
            "RAM-backed active table publication is not used",
            "coordinate-native runtime profile",
            "Nunchuk remains NOT_TESTED",
            "root cause remains unproven",
            "docs/agent_framework/README.md",
        ),
    )

    require_phrases(
        "docs/agent_framework/README.md",
        (
            "supervisor",
            "subagents",
            "DOCS_CHECKER_ONLY",
            "FIRMWARE_SOURCE_ACTIVE_BEHAVIOR",
            "FORBIDDEN_OR_UNSAFE",
            "runtime-loaded config is not implemented",
            "Nunchuk remains NOT_TESTED",
            "Root cause remains unproven",
        ),
    )

    require_phrases(
        "docs/CURRENT_STATE.md",
        (
            "docs/AGENT_CONTEXT.md",
            "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md",
            "source-owned Y2 layout HARDWARE_PASS",
            "Active RuntimeConfigView selection remains unchanged",
            "Runtime-loaded config is not implemented",
            "WebSerial/device write is not implemented",
            "Protobuf binary write is not implemented",
            "Firmware flashing automation is not implemented",
            "No nunchuk validation is claimed",
            "No root-cause claim is made",
            "coordinate-native runtime profile contract scaffolding",
            "coordinate_native_runtime_profile_contract.json",
            "offline dry-run evaluator",
        ),
    )

    require_phrases(
        "docs/ROADMAP.md",
        (
            "Phase 0 - Preserve Current Source-Owned Firmware Baseline",
            "Phase 1 - Source-Owned Realization Generator",
            "Phase 2 - Coordinate-Native Runtime Profile Contract Scaffolding",
            "Phase 3 - Future Browser/Protobuf/Persistence Backend",
            "source-owned realization generator",
            "coordinate-native runtime profile contract scaffolding",
            "browser/protobuf/persistence",
            "generated active wrapper",
            "runtime-config-latest-y2-layout-source-owned-port-hardware-result",
            "offline dry-run evaluator",
        ),
    )

    require_phrases(
        "docs/runtime_config/README.md",
        (
            "Current Known-Good State",
            "Safe Source-Owned Realization Path",
            "Forbidden Active Publication Paths",
            "Coordinate-Native Runtime Profile Contract",
            "Archived Diagnostics",
            "coordinate_native_runtime_profile_contract.md",
            "coordinate_native_runtime_profile_contract.json",
            "python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py",
            "python3 tools/dry_run_coordinate_native_runtime_profile.py --profile",
            "RuntimeConfigView replacement is not used",
            "candidate.view is not active",
            "RAM-backed active table publication is not used",
            "offline dry-run evaluator",
        ),
    )

    require_phrases(
        "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md",
        (
            "candidate.view active publication is forbidden",
            "active_storage.view active publication is forbidden",
            "Generated active RuntimeConfigView wrapper publication is forbidden",
            "RuntimeConfigView replacement as the customization mechanism is forbidden",
            "Runtime-loaded profile claims are forbidden",
            "design-only and inactive",
            "browser/protobuf/persistence work may be future infrastructure",
        ),
    )

    require_phrases(
        "docs/archive/README.md",
        (
            "historical diagnostics",
            "Do not delete historical failure evidence",
            "Do not present archived failed implementation branches as current work",
            "Do not claim the root cause is proven",
            "Do not claim nunchuk was tested",
        ),
    )

    correction_packet = REPO_ROOT / "docs/calibration/glyph_external_remapper_misattribution_correction_2026-06-06.md"
    if correction_packet.exists():
        for rel_path in (
            "AGENTS.md",
            "docs/calibration/README.md",
            "docs/calibration/INDEX.md",
            "docs/calibration/archive_policy.md",
        ):
            require_phrases(rel_path, ("quarantined",))
        require_phrases("AGENTS.md", ("Official Glyph configurator corpus is the primary corpus",))

    print("glyph_docs_navigation: PASS")
    for rel_path in required_paths:
        print(f"- {rel_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
