#!/usr/bin/env python3
"""Read-only checks for Glyph profile/config export corpus capture structure.

This checker validates:
- the template manifest JSON shape;
- real corpus manifests (if present) and listed fixture file existence;
- semantic signal summaries from listed JSON fixture files via the existing
  repo-local profile/config semantics analyzer.

It never mutates files.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import check_glyph_profile_config_semantics as fixture_semantics


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE_PATH = (
    REPO_ROOT / "docs" / "calibration" / "glyph_profile_config_export_corpus_manifest_TEMPLATE.json"
)
DEFAULT_CORPUS_ROOT = REPO_ROOT / "docs" / "calibration" / "export_corpus"
REQUIRED_MANIFEST_FIELDS = [
    "corpus_id",
    "captured_at",
    "captured_by",
    "glyph_repo_commit",
    "firmware_source_commit",
    "configurator_source_reference",
    "configurator_version_label",
    "device_model",
    "hardware_required",
    "source_kind",
    "fixture_files",
    "expected_semantic_features",
    "known_unknowns",
    "notes",
]


@dataclass
class CheckResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class FixtureSemanticSignal:
    path: Path
    omitted_activates: int
    explicit_btn_unspecified: int
    duplicate_physical_modes: int
    many_to_one_modes: int
    omitted_default_mode_backend_count: int
    socd_pairs_without_type: int
    warnings: list[str]
    errors: list[str]


@dataclass
class ManifestCheckResult(CheckResult):
    path: Path | None = None
    fixture_signals: list[FixtureSemanticSignal] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Glyph export-corpus manifest/template structure and summarize "
            "fixture semantic signals without mutating files."
        ),
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE_PATH,
        help="Path to export-corpus manifest template JSON.",
    )
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=DEFAULT_CORPUS_ROOT,
        help="Root directory containing real corpus capture directories.",
    )
    return parser.parse_args()


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"root must be object: {path}")
    return payload


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _validate_required_fields(payload: dict[str, Any], result: CheckResult, label: str) -> None:
    missing = [field for field in REQUIRED_MANIFEST_FIELDS if field not in payload]
    if missing:
        result.errors.append(f"{label}: missing required fields: {', '.join(missing)}")


def _validate_template_types(payload: dict[str, Any], result: CheckResult) -> None:
    list_fields = ["fixture_files", "expected_semantic_features", "known_unknowns"]
    for field_name in list_fields:
        value = payload.get(field_name)
        if value is None:
            result.warnings.append(f"template field '{field_name}' is null; expected list in real manifest")
            continue
        if not isinstance(value, list):
            result.errors.append(f"template field '{field_name}' must be a list")


def validate_template(template_path: Path) -> tuple[CheckResult, dict[str, Any] | None]:
    result = CheckResult()
    if not template_path.exists():
        result.errors.append(f"missing template file: {_display_path(template_path)}")
        return result, None

    try:
        payload = load_json_object(template_path)
    except Exception as exc:  # pragma: no cover - defensive parse guard
        result.errors.append(f"failed to parse template JSON: {exc}")
        return result, None

    _validate_required_fields(payload, result, "template")
    _validate_template_types(payload, result)
    return result, payload


def discover_real_manifests(corpus_root: Path) -> list[Path]:
    if not corpus_root.exists() or not corpus_root.is_dir():
        return []
    return sorted(path for path in corpus_root.rglob("manifest.json") if path.is_file())


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_real_manifest_schema(payload: dict[str, Any], result: ManifestCheckResult) -> None:
    _validate_required_fields(payload, result, "manifest")

    required_non_empty_string_fields = [
        "corpus_id",
        "captured_at",
        "captured_by",
        "glyph_repo_commit",
        "firmware_source_commit",
        "configurator_source_reference",
        "configurator_version_label",
        "device_model",
        "source_kind",
    ]
    for field_name in required_non_empty_string_fields:
        if not _non_empty_string(payload.get(field_name)):
            result.errors.append(f"manifest field '{field_name}' must be a non-empty string")

    hardware_required = payload.get("hardware_required")
    if not isinstance(hardware_required, bool):
        result.errors.append("manifest field 'hardware_required' must be a boolean")

    list_fields = ["fixture_files", "expected_semantic_features", "known_unknowns"]
    for field_name in list_fields:
        value = payload.get(field_name)
        if not isinstance(value, list):
            result.errors.append(f"manifest field '{field_name}' must be a list")
            continue
        if field_name == "fixture_files" and len(value) == 0:
            result.errors.append("manifest field 'fixture_files' must list at least one fixture")
        for item_index, item in enumerate(value):
            if not _non_empty_string(item):
                result.errors.append(
                    f"manifest field '{field_name}[{item_index}]' must be a non-empty string",
                )

    notes = payload.get("notes")
    if notes is not None and not isinstance(notes, str):
        result.errors.append("manifest field 'notes' must be a string or null")


def _summarize_fixture_signal(path: Path) -> FixtureSemanticSignal:
    summary = fixture_semantics.analyze_fixture(path)
    duplicate_mode_count = len([mode for mode in summary.mode_remap_summaries if mode.duplicate_physical])
    alias_mode_count = len([mode for mode in summary.mode_remap_summaries if mode.many_to_one_targets])
    return FixtureSemanticSignal(
        path=summary.path,
        omitted_activates=summary.remaps_omitted_activates,
        explicit_btn_unspecified=summary.remaps_explicit_unspecified,
        duplicate_physical_modes=duplicate_mode_count,
        many_to_one_modes=alias_mode_count,
        omitted_default_mode_backend_count=len(summary.backend_default_mode_omitted),
        socd_pairs_without_type=summary.socd_pairs_without_type,
        warnings=summary.warnings,
        errors=summary.errors,
    )


def validate_real_manifest(manifest_path: Path) -> ManifestCheckResult:
    result = ManifestCheckResult(path=manifest_path)

    try:
        payload = load_json_object(manifest_path)
    except Exception as exc:  # pragma: no cover - defensive parse guard
        result.errors.append(f"failed to parse manifest JSON: {exc}")
        return result

    _validate_real_manifest_schema(payload, result)

    fixture_files = payload.get("fixture_files")
    if not isinstance(fixture_files, list):
        return result

    manifest_dir = manifest_path.parent
    for index, relative_path in enumerate(fixture_files):
        if not isinstance(relative_path, str) or not relative_path.strip():
            continue
        candidate = (manifest_dir / relative_path).resolve()
        if not candidate.exists() or not candidate.is_file():
            result.errors.append(
                "fixture_files"
                f"[{index}] missing file: {relative_path} (resolved {_display_path(candidate)})",
            )
            continue
        if candidate.suffix.lower() != ".json":
            result.warnings.append(
                f"fixture_files[{index}] is not .json; semantic checks skipped: {relative_path}",
            )
            continue

        signal = _summarize_fixture_signal(candidate)
        result.fixture_signals.append(signal)

    return result


def print_template_result(template_path: Path, result: CheckResult) -> None:
    print(f"[template] {_display_path(template_path)}")
    if result.warnings:
        print("- warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    if result.errors:
        print("- errors:")
        for error in result.errors:
            print(f"  - {error}")
    if not result.warnings and not result.errors:
        print("- status: OK")
    print()


def print_manifest_result(result: ManifestCheckResult) -> None:
    assert result.path is not None
    print(f"[manifest] {_display_path(result.path)}")

    if result.fixture_signals:
        print("- fixture_semantic_signals:")
        for signal in result.fixture_signals:
            print(f"  - fixture={_display_path(signal.path)}")
            print(
                "    omitted_activates="
                f"{signal.omitted_activates}, explicit_btn_unspecified={signal.explicit_btn_unspecified}",
            )
            print(
                "    many_to_one_modes="
                f"{signal.many_to_one_modes}, duplicate_physical_modes={signal.duplicate_physical_modes}",
            )
            print(
                "    omitted_defaultModeConfig_backends="
                f"{signal.omitted_default_mode_backend_count}, socd_pairs_without_socdType={signal.socd_pairs_without_type}",
            )
            if signal.warnings:
                print("    warnings:")
                for warning in signal.warnings:
                    print(f"      - {warning}")
            if signal.errors:
                print("    errors:")
                for error in signal.errors:
                    print(f"      - {error}")
    else:
        print("- fixture_semantic_signals: none")

    if result.warnings:
        print("- warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    if result.errors:
        print("- errors:")
        for error in result.errors:
            print(f"  - {error}")

    if not result.errors:
        print("- status: OK")
    print()


def main() -> int:
    args = parse_args()

    template_path = args.template if args.template.is_absolute() else REPO_ROOT / args.template
    corpus_root = args.corpus_root if args.corpus_root.is_absolute() else REPO_ROOT / args.corpus_root

    template_result, _template_payload = validate_template(template_path)
    print_template_result(template_path, template_result)

    manifest_paths = discover_real_manifests(corpus_root)
    has_errors = bool(template_result.errors)

    if not manifest_paths:
        print(
            "no_real_corpus_present=true "
            f"(searched under {_display_path(corpus_root)}; template-only state accepted)",
        )
        print("result=PASS" if not has_errors else "result=FAIL")
        return 0 if not has_errors else 1

    print(f"real_corpus_manifests_found={len(manifest_paths)}")
    print()

    for manifest_path in manifest_paths:
        manifest_result = validate_real_manifest(manifest_path)
        print_manifest_result(manifest_result)
        if manifest_result.errors:
            has_errors = True

    print("result=PASS" if not has_errors else "result=FAIL")
    return 0 if not has_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
