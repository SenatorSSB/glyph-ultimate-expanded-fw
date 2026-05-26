#!/usr/bin/env python3
"""Read-only structural/semantics checks for repo-local Glyph profile fixtures."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURES = [
    REPO_ROOT / "docs" / "sources" / "raw" / "GlyphUserProfiles.json",
    REPO_ROOT / "docs" / "calibration" / "fixtures" / "GlyphUserProfilesUlt-filled.json",
    REPO_ROOT / "docs" / "calibration" / "fixtures" / "GlyphUltFilled2.json",
    REPO_ROOT
    / "docs"
    / "calibration"
    / "fixtures"
    / "tilt_button_id_probe"
    / "GlyphUserProfilesUltimateMVP01.json",
]

# Source reference: src/core/mode_selection.cpp currently stores activation masks in a fixed array.
MODE_ACTIVATION_MASK_CAPACITY = 10


@dataclass
class ModeRemapSummary:
    name: str
    mode_id: str
    remap_count: int = 0
    omitted_activates: int = 0
    explicit_unspecified: int = 0
    duplicate_physical: dict[str, int] = field(default_factory=dict)
    many_to_one_targets: dict[str, int] = field(default_factory=dict)


@dataclass
class FixtureSummary:
    path: Path
    game_modes_count: int = 0
    backend_configs_count: int = 0
    remaps_total: int = 0
    remaps_with_activates: int = 0
    remaps_omitted_activates: int = 0
    remaps_explicit_unspecified: int = 0
    socd_pairs_total: int = 0
    socd_pairs_without_type: int = 0
    modes_without_button_remapping_field: int = 0
    default_backend_config: int | None = None
    default_usb_backend_config: int | None = None
    backend_default_mode_omitted: list[str] = field(default_factory=list)
    mode_remap_summaries: list[ModeRemapSummary] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read repo-local Glyph profile/config fixtures and report omission/default/remap "
            "signals without mutating files."
        ),
    )
    parser.add_argument(
        "--files",
        nargs="*",
        type=Path,
        help="Optional fixture list override. Defaults to known repo-local fixtures.",
    )
    return parser.parse_args()


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"root must be object: {path}")
    return payload


def analyze_fixture(path: Path) -> FixtureSummary:
    summary = FixtureSummary(path=path)
    if not path.exists():
        summary.errors.append(f"missing fixture: {path}")
        return summary

    try:
        payload = load_json_object(path)
    except Exception as exc:  # pragma: no cover - defensive parse guard
        summary.errors.append(f"failed to parse JSON: {exc}")
        return summary

    game_modes = payload.get("gameModeConfigs")
    backend_configs = payload.get("communicationBackendConfigs")

    if not isinstance(game_modes, list):
        summary.errors.append("gameModeConfigs must be a list")
        game_modes = []
    if not isinstance(backend_configs, list):
        summary.errors.append("communicationBackendConfigs must be a list")
        backend_configs = []

    summary.game_modes_count = len(game_modes)
    summary.backend_configs_count = len(backend_configs)

    summary.default_backend_config = _optional_int(payload.get("defaultBackendConfig"))
    if payload.get("defaultBackendConfig") is not None and summary.default_backend_config is None:
        summary.errors.append("defaultBackendConfig must be an integer when present")
    _validate_index(
        label="defaultBackendConfig",
        index_value=summary.default_backend_config,
        upper_bound=summary.backend_configs_count,
        errors=summary.errors,
        allow_zero=True,
    )

    summary.default_usb_backend_config = _optional_int(payload.get("defaultUsbBackendConfig"))
    if payload.get("defaultUsbBackendConfig") is not None and summary.default_usb_backend_config is None:
        summary.errors.append("defaultUsbBackendConfig must be an integer when present")
    _validate_index(
        label="defaultUsbBackendConfig",
        index_value=summary.default_usb_backend_config,
        upper_bound=summary.backend_configs_count,
        errors=summary.errors,
        allow_zero=True,
    )

    if summary.game_modes_count > MODE_ACTIVATION_MASK_CAPACITY:
        summary.warnings.append(
            "gameModeConfigs count exceeds mode_activation_masks capacity "
            f"({summary.game_modes_count} > {MODE_ACTIVATION_MASK_CAPACITY})",
        )

    for backend_index, backend_entry in enumerate(backend_configs):
        if not isinstance(backend_entry, dict):
            summary.errors.append(
                f"communicationBackendConfigs[{backend_index}] must be an object",
            )
            continue
        backend_id = backend_entry.get("backendId")
        backend_label = backend_id if isinstance(backend_id, str) else f"index_{backend_index + 1}"
        default_mode = backend_entry.get("defaultModeConfig")
        if default_mode is None:
            summary.backend_default_mode_omitted.append(backend_label)
            continue
        default_mode_index = _optional_int(default_mode)
        if default_mode_index is None:
            summary.errors.append(
                f"communicationBackendConfigs[{backend_index}].defaultModeConfig must be an integer",
            )
            continue
        _validate_index(
            label=(
                "communicationBackendConfigs"
                f"[{backend_index}].defaultModeConfig({backend_label})"
            ),
            index_value=default_mode_index,
            upper_bound=summary.game_modes_count,
            errors=summary.errors,
            allow_zero=True,
        )

    for mode_index, mode_entry in enumerate(game_modes):
        if not isinstance(mode_entry, dict):
            summary.errors.append(f"gameModeConfigs[{mode_index}] must be an object")
            continue

        mode_name = mode_entry.get("name")
        mode_id = mode_entry.get("modeId")
        mode_label_name = mode_name if isinstance(mode_name, str) and mode_name else f"index_{mode_index}"
        mode_label_id = mode_id if isinstance(mode_id, str) and mode_id else "<missing_mode_id>"
        mode_summary = ModeRemapSummary(name=mode_label_name, mode_id=mode_label_id)

        socd_pairs = mode_entry.get("socdPairs")
        if socd_pairs is None:
            socd_pairs = []
        if not isinstance(socd_pairs, list):
            summary.errors.append(f"gameModeConfigs[{mode_index}].socdPairs must be a list when present")
            socd_pairs = []
        summary.socd_pairs_total += len(socd_pairs)
        summary.socd_pairs_without_type += len(
            [pair for pair in socd_pairs if isinstance(pair, dict) and "socdType" not in pair],
        )

        remaps_raw = mode_entry.get("buttonRemapping")
        if remaps_raw is None:
            summary.modes_without_button_remapping_field += 1
            remaps_raw = []
        if not isinstance(remaps_raw, list):
            summary.errors.append(
                f"gameModeConfigs[{mode_index}].buttonRemapping must be a list when present",
            )
            remaps_raw = []

        mode_summary.remap_count = len(remaps_raw)
        summary.remaps_total += len(remaps_raw)

        physical_counter: Counter[str] = Counter()
        activates_counter: Counter[str] = Counter()

        for remap_index, remap_entry in enumerate(remaps_raw):
            if not isinstance(remap_entry, dict):
                summary.errors.append(
                    f"gameModeConfigs[{mode_index}].buttonRemapping[{remap_index}] must be an object",
                )
                continue

            physical_button = remap_entry.get("physicalButton")
            if not isinstance(physical_button, str) or not physical_button:
                summary.errors.append(
                    "gameModeConfigs"
                    f"[{mode_index}].buttonRemapping[{remap_index}] missing physicalButton",
                )
            else:
                physical_counter[physical_button] += 1

            if "activates" not in remap_entry:
                mode_summary.omitted_activates += 1
                summary.remaps_omitted_activates += 1
                continue

            activates = remap_entry.get("activates")
            if not isinstance(activates, str):
                summary.errors.append(
                    "gameModeConfigs"
                    f"[{mode_index}].buttonRemapping[{remap_index}].activates must be a string when present",
                )
                continue

            summary.remaps_with_activates += 1
            if activates == "BTN_UNSPECIFIED":
                mode_summary.explicit_unspecified += 1
                summary.remaps_explicit_unspecified += 1
            else:
                activates_counter[activates] += 1

        mode_summary.duplicate_physical = {
            button: count for button, count in physical_counter.items() if count > 1
        }
        mode_summary.many_to_one_targets = {
            button: count for button, count in activates_counter.items() if count > 1
        }
        summary.mode_remap_summaries.append(mode_summary)

    return summary


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _validate_index(
    *,
    label: str,
    index_value: int | None,
    upper_bound: int,
    errors: list[str],
    allow_zero: bool,
) -> None:
    if index_value is None:
        return
    if index_value < 0:
        errors.append(f"{label} must be >= 0, got {index_value}")
        return
    if index_value == 0 and not allow_zero:
        errors.append(f"{label} must be >= 1, got 0")
        return
    if index_value > upper_bound:
        errors.append(f"{label}={index_value} exceeds max {upper_bound}")


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def print_summary(summary: FixtureSummary) -> None:
    print(f"[{_display_path(summary.path)}]")
    print(f"- game_modes={summary.game_modes_count}")
    print(f"- communication_backend_configs={summary.backend_configs_count}")
    print(
        "- remaps_total="
        f"{summary.remaps_total}, remaps_with_activates={summary.remaps_with_activates}, "
        f"remaps_omitted_activates={summary.remaps_omitted_activates}, "
        f"remaps_explicit_btn_unspecified={summary.remaps_explicit_unspecified}",
    )
    print(
        "- socd_pairs_total="
        f"{summary.socd_pairs_total}, socd_pairs_without_socdType={summary.socd_pairs_without_type}",
    )
    print(f"- modes_without_buttonRemapping_field={summary.modes_without_button_remapping_field}")
    print(
        "- default_backend_config="
        f"{summary.default_backend_config}, default_usb_backend_config={summary.default_usb_backend_config}",
    )
    if summary.backend_default_mode_omitted:
        omitted = ", ".join(summary.backend_default_mode_omitted)
        print(f"- backend_defaultModeConfig_omitted={omitted}")

    duplicate_lines = [
        (mode.name, mode.mode_id, mode.duplicate_physical)
        for mode in summary.mode_remap_summaries
        if mode.duplicate_physical
    ]
    if duplicate_lines:
        print("- duplicate_physical_button_entries:")
        for name, mode_id, duplicates in duplicate_lines:
            rendered = ", ".join(f"{button}({count})" for button, count in sorted(duplicates.items()))
            print(f"  - {name}/{mode_id}: {rendered}")
    else:
        print("- duplicate_physical_button_entries: none")

    many_to_one_lines = [
        (mode.name, mode.mode_id, mode.many_to_one_targets)
        for mode in summary.mode_remap_summaries
        if mode.many_to_one_targets
    ]
    if many_to_one_lines:
        print("- many_to_one_logical_targets:")
        for name, mode_id, targets in many_to_one_lines:
            rendered = ", ".join(f"{button}({count})" for button, count in sorted(targets.items()))
            print(f"  - {name}/{mode_id}: {rendered}")
    else:
        print("- many_to_one_logical_targets: none")

    if summary.warnings:
        print("- warnings:")
        for warning in summary.warnings:
            print(f"  - {warning}")

    if summary.errors:
        print("- errors:")
        for error in summary.errors:
            print(f"  - {error}")
    print()


def main() -> int:
    args = parse_args()
    fixtures = args.files if args.files else DEFAULT_FIXTURES
    summaries = [analyze_fixture(path if path.is_absolute() else REPO_ROOT / path) for path in fixtures]

    has_errors = False
    for summary in summaries:
        print_summary(summary)
        if summary.errors:
            has_errors = True

    if has_errors:
        print("result=FAIL")
        return 1

    print("result=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
