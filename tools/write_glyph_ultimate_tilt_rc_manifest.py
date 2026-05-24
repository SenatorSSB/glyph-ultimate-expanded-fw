#!/usr/bin/env python3
"""Generate a deterministic markdown RC manifest for Glyph Ultimate Tilt."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_REL = Path("docs/calibration/glyph_ultimate_tilt_rc_manifest.md")
DEFAULT_OUTPUT_PATH = REPO_ROOT / DEFAULT_OUTPUT_REL
BUILD_COMMAND = "./scripts/build-glyph-mk6-quiet.sh"
RUNTIME_SOURCE_REL = Path("src/modes/Ultimate.cpp")
DOMAIN_FIXTURE_REL = Path("docs/calibration/fixtures/glyph_ultimate_tilt_domain_spec.json")
ARTIFACT_ROOT_REL = Path(".pio/build/glyph_mk6")
ARTIFACT_ROOT = REPO_ROOT / ARTIFACT_ROOT_REL
ARTIFACT_SUFFIXES = (".uf2", ".bin", ".elf", ".hex")
FIRMWARE_RELEVANT_PREFIXES = (
    "src/",
    "include/",
    "HAL/",
    "config/",
    "proto/",
    "schema/",
    "configurator/",
    "backend/",
    "persistence/",
)
FIRMWARE_RELEVANT_EXACT = ("platformio.ini",)
FIRMWARE_RELEVANT_SEGMENTS = (
    "/proto/",
    "/schema/",
    "/configurator/",
    "/backend/",
    "/persistence/",
)

VERIFICATION_COMMANDS = (
    ".venv/bin/python tools/check_glyph_calibration_fixtures.py",
    ".venv/bin/python tools/check_glyph_patch_script.py",
    ".venv/bin/python tools/list_glyph_modifier_symbols.py",
    ".venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py",
    ".venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py",
    ".venv/bin/python tools/check_glyph_native_ultimate_snapshot.py",
    ".venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode docs-only",
    ".venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode runtime-implementation",
    ".venv/bin/python tools/check_glyph_ultimate_tilt_domain_spec.py",
    ".venv/bin/python tools/list_glyph_tilt_button_id_candidates.py",
    ".venv/bin/python tools/check_glyph_tilt_button_id_probe.py",
    ".venv/bin/python tools/check_glyph_ultimate_tilt_runtime_source.py",
    ".venv/bin/python tools/inspect_glyph_mk6_build_artifact.py",
    ".venv/bin/python tools/check_glyph_ultimate_tilt_tables.py",
    ".venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py",
    "./scripts/build-glyph-mk6-quiet.sh",
    ".venv/bin/python tools/write_glyph_ultimate_tilt_rc_manifest.py --output docs/calibration/glyph_ultimate_tilt_rc_manifest.md",
    ".venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py",
)


@dataclass(frozen=True)
class Artifact:
    path: str
    size_bytes: int
    sha256: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic Glyph Ultimate Tilt RC manifest markdown.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_REL),
        help=f"manifest output path (default: {DEFAULT_OUTPUT_REL.as_posix()})",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print manifest to stdout only.",
    )
    parser.add_argument(
        "--strict-artifact",
        action="store_true",
        help="Exit nonzero when no primary build artifact candidates are found.",
    )
    return parser.parse_args()


def _git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or "unknown git error"
        raise RuntimeError(f"git {' '.join(args)} failed: {stderr}")
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _scan_artifacts() -> list[Artifact]:
    if not ARTIFACT_ROOT.is_dir():
        return []

    artifacts: list[Artifact] = []
    chosen_paths: set[Path] = set()

    for suffix in ARTIFACT_SUFFIXES:
        exact = ARTIFACT_ROOT / f"firmware{suffix}"
        candidate: Path | None = exact if exact.is_file() else None

        if candidate is None:
            fallback_pool = [
                path
                for path in ARTIFACT_ROOT.glob(f"*{suffix}")
                if path.is_file() and path.stem.lower().startswith("firmware")
            ]
            if fallback_pool:
                candidate = max(
                    fallback_pool,
                    key=lambda path: (path.stat().st_mtime_ns, path.name),
                )

        if candidate is None or candidate in chosen_paths:
            continue
        chosen_paths.add(candidate)
        artifacts.append(
            Artifact(
                path=candidate.relative_to(REPO_ROOT).as_posix(),
                size_bytes=candidate.stat().st_size,
                sha256=_sha256(candidate),
            )
        )

    return artifacts


def _load_tilt_tables() -> tuple[str, dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    fixture_path = REPO_ROOT / DOMAIN_FIXTURE_REL
    if not fixture_path.exists():
        return ("MISSING", {}, {})
    try:
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ("INVALID_JSON", {}, {})

    if not isinstance(payload, dict):
        return ("INVALID_ROOT", {}, {})
    tables = payload.get("tables")
    if not isinstance(tables, dict):
        return ("MISSING_TABLES", {}, {})
    tilt1 = tables.get("tilt1")
    tilt2 = tables.get("tilt2")
    if not isinstance(tilt1, dict) or not isinstance(tilt2, dict):
        return ("MISSING_TILT_TABLES", {}, {})

    normalized_tilt1: dict[str, dict[str, int]] = {}
    normalized_tilt2: dict[str, dict[str, int]] = {}

    for direction in map(str, range(1, 10)):
        point1 = tilt1.get(direction)
        point2 = tilt2.get(direction)
        if (
            not isinstance(point1, dict)
            or not isinstance(point2, dict)
            or not isinstance(point1.get("x"), int)
            or not isinstance(point1.get("y"), int)
            or not isinstance(point2.get("x"), int)
            or not isinstance(point2.get("y"), int)
        ):
            return ("INVALID_TILT_POINTS", {}, {})

        normalized_tilt1[direction] = {"x": point1["x"], "y": point1["y"]}
        normalized_tilt2[direction] = {"x": point2["x"], "y": point2["y"]}

    return ("OK", normalized_tilt1, normalized_tilt2)


def _dirty_summary(status_lines: list[str]) -> tuple[str, int, int, int]:
    if not status_lines:
        return ("CLEAN", 0, 0, 0)

    staged = 0
    unstaged = 0
    untracked = 0
    for line in status_lines:
        code = line[:2]
        if code == "??":
            untracked += 1
            continue
        if len(code) >= 1 and code[0] != " ":
            staged += 1
        if len(code) >= 2 and code[1] != " ":
            unstaged += 1
    return ("DIRTY", staged, unstaged, untracked)


def _decode_status_path_token(token: str) -> str:
    token = token.strip()
    if token.startswith('"') and token.endswith('"'):
        try:
            decoded = ast.literal_eval(token)
        except (SyntaxError, ValueError):
            return token.strip('"')
        if isinstance(decoded, str):
            return decoded
    return token


def _extract_status_paths(status_line: str) -> list[str]:
    payload = status_line[3:].strip() if len(status_line) >= 3 else ""
    if not payload:
        return []
    if " -> " in payload:
        left, right = payload.split(" -> ", 1)
        return [_decode_status_path_token(left), _decode_status_path_token(right)]
    return [_decode_status_path_token(payload)]


def _is_build_script_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    if not normalized.startswith("scripts/"):
        return False
    name = Path(normalized).name.lower()
    if "build" in name:
        return True
    return name == "pio-local.sh" or name.startswith("pio-") or name.startswith("pio_")


def _is_firmware_relevant_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    if normalized in FIRMWARE_RELEVANT_EXACT:
        return True
    if _is_build_script_path(normalized):
        return True
    if any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in FIRMWARE_RELEVANT_PREFIXES
    ):
        return True

    padded = f"/{normalized}/"
    return any(segment in padded for segment in FIRMWARE_RELEVANT_SEGMENTS)


def _split_dirty_entries(status_lines: list[str]) -> tuple[list[str], list[str]]:
    firmware_relevant: list[str] = []
    non_firmware: list[str] = []
    for status_line in status_lines:
        paths = _extract_status_paths(status_line)
        is_relevant = any(_is_firmware_relevant_path(path) for path in paths)
        if is_relevant:
            firmware_relevant.append(status_line)
        else:
            non_firmware.append(status_line)
    return firmware_relevant, non_firmware


def _render_manifest() -> tuple[str, bool]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    firmware_source_commit_sha = _git(["rev-parse", "HEAD"])
    status_short = _git(["status", "--short"])
    status_lines = sorted(line for line in status_short.splitlines() if line.strip())
    dirty_state, staged_count, unstaged_count, untracked_count = _dirty_summary(status_lines)
    firmware_relevant_entries, non_firmware_entries = _split_dirty_entries(status_lines)
    firmware_relevant_dirty_state = "DIRTY" if firmware_relevant_entries else "CLEAN"

    artifacts = _scan_artifacts()
    artifact_status = "FOUND" if artifacts else "MISSING"
    tables_status, tilt1_table, tilt2_table = _load_tilt_tables()

    lines: list[str] = []
    lines.append("# Glyph Ultimate Tilt RC Manifest")
    lines.append("")
    lines.append("## RC Identity")
    lines.append(f"- manifest_generated_from_branch: `{branch}`")
    lines.append(f"- firmware_source_commit_sha: `{firmware_source_commit_sha}`")
    lines.append(
        "- manifest_generation_note: This manifest is generated before the manifest commit exists; it is not self-referential to a final manifest commit SHA."
    )
    lines.append(f"- build_command: `{BUILD_COMMAND}`")
    lines.append(f"- runtime_implementation_source: `{RUNTIME_SOURCE_REL.as_posix()}`")
    lines.append("- hardware_test_status: NOT_TESTED")
    lines.append("- flashing_automation: NOT_INCLUDED")
    lines.append("")
    lines.append("## Git Dirty Summary")
    lines.append(f"- git_dirty_state: {dirty_state}")
    lines.append(f"- firmware_relevant_dirty_state: {firmware_relevant_dirty_state}")
    lines.append(f"- staged_entries: {staged_count}")
    lines.append(f"- unstaged_entries: {unstaged_count}")
    lines.append(f"- untracked_entries: {untracked_count}")
    if firmware_relevant_entries:
        lines.append("- firmware_relevant_dirty_entries:")
        lines.append("```text")
        lines.extend(firmware_relevant_entries)
        lines.append("```")
    else:
        lines.append("- firmware_relevant_dirty_entries: none")
    if non_firmware_entries:
        lines.append("- non_firmware_dirty_entries:")
        lines.append("```text")
        lines.extend(non_firmware_entries)
        lines.append("```")
    else:
        lines.append("- non_firmware_dirty_entries: none")
    if status_lines:
        lines.append("- git_status_short:")
        lines.append("```text")
        lines.extend(status_lines)
        lines.append("```")
    else:
        lines.append("- git_status_short: CLEAN")
    lines.append("")
    lines.append("## Artifact Candidates")
    lines.append(f"- artifact_status: {artifact_status}")
    lines.append(f"- artifact_root: `{ARTIFACT_ROOT_REL.as_posix()}`")
    lines.append(f"- candidate_suffixes: `{', '.join(ARTIFACT_SUFFIXES)}`")
    if artifacts:
        for index, artifact in enumerate(artifacts, start=1):
            lines.append(f"- artifact_{index}_path: `{artifact.path}`")
            lines.append(f"- artifact_{index}_size_bytes: `{artifact.size_bytes}`")
            lines.append(f"- artifact_{index}_sha256: `{artifact.sha256}`")
    else:
        lines.append("- artifact_candidates: none")
    lines.append("")
    lines.append("## Tilt Input Summary")
    lines.append("- tilt1_input: `inputs.lt1` (post-remap logical input)")
    lines.append("- tilt2_input: `inputs.lt2` (post-remap logical input)")
    lines.append("- implementation_scope: left-stick-only override")
    lines.append("- preserved_outputs: right-stick, triggers")
    lines.append("")
    lines.append("## Tilt Table Reference")
    lines.append(f"- domain_spec_fixture: `{DOMAIN_FIXTURE_REL.as_posix()}`")
    lines.append(f"- domain_spec_fixture_status: {tables_status}")
    if tables_status == "OK":
        lines.append("")
        lines.append("| Direction | Tilt1 (x, y) | Tilt2 (x, y) |")
        lines.append("| --- | --- | --- |")
        for direction in map(str, range(1, 10)):
            point1 = tilt1_table[direction]
            point2 = tilt2_table[direction]
            lines.append(
                f"| {direction} | ({point1['x']}, {point1['y']}) | ({point2['x']}, {point2['y']}) |"
            )
    lines.append("")
    lines.append("## Verification Commands")
    lines.append("```bash")
    lines.extend(VERIFICATION_COMMANDS)
    lines.append("```")

    manifest = "\n".join(lines).rstrip() + "\n"
    return manifest, artifact_status == "MISSING"


def _resolve_output(path_str: str) -> Path:
    output_path = Path(path_str)
    if output_path.is_absolute():
        return output_path
    return REPO_ROOT / output_path


def main() -> int:
    args = parse_args()
    try:
        manifest, missing_artifacts = _render_manifest()
    except RuntimeError as exc:
        print(f"write_glyph_ultimate_tilt_rc_manifest: FAIL {exc}")
        return 1

    if args.no_write:
        sys.stdout.write(manifest)
    else:
        output_path = _resolve_output(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(manifest, encoding="utf-8")
        try:
            display_path = output_path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            display_path = str(output_path)
        print(f"write_glyph_ultimate_tilt_rc_manifest: wrote {display_path}")

    if args.strict_artifact and missing_artifacts:
        print("write_glyph_ultimate_tilt_rc_manifest: FAIL artifact_status=MISSING")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
