#!/usr/bin/env python3
"""Read-only checker for Glyph serial active config writer docs/tooling."""

from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
TRACE_DOC = REPO_ROOT / "docs" / "calibration" / "glyph_serial_active_config_writer_trace_2026-05-27.md"
WRITER_TOOL = REPO_ROOT / "tools" / "glyph_serial_config_tool.py"
BLOCKER_CODE = "HOST_SERIAL_CONFIG_WRITER_BLOCKED_BY_DEPENDENCY_OR_PROTOCOL"


def _has(text: str, needle: str) -> bool:
    return needle.lower() in text.lower()


def main() -> int:
    failures: list[str] = []

    writer_implemented = WRITER_TOOL.exists()
    blocked = False

    if not TRACE_DOC.exists():
        failures.append(f"missing trace doc: {TRACE_DOC.relative_to(REPO_ROOT)}")
        trace_text = ""
    else:
        trace_text = TRACE_DOC.read_text(encoding="utf-8")
        blocked = BLOCKER_CODE in trace_text

        if not (
            _has(trace_text, "never flash firmware")
            or _has(trace_text, "no firmware flashing")
            or _has(trace_text, "never flash")
        ):
            failures.append("trace doc must state no firmware flashing behavior")

        if not (
            _has(trace_text, "explicit `--write` required")
            or _has(trace_text, "explicit --write required")
            or _has(trace_text, "requires explicit user action")
        ):
            failures.append("trace doc must state explicit write action is required")

        if not (
            _has(trace_text, "closed-source")
            and _has(trace_text, "lossy")
            and _has(trace_text, "lt3")
        ):
            failures.append(
                "trace doc must state closed-source webapp path was observed lossy/not verified for LT3"
            )

    if writer_implemented:
        tool_text = WRITER_TOOL.read_text(encoding="utf-8")

        if "args.dry_run = True" not in tool_text:
            failures.append("writer tool must default to dry-run when mode flags are omitted")

        if "--write" not in tool_text:
            failures.append("writer tool must expose explicit --write flag")

        if "mode in {\"read\", \"write\"} and not args.port" not in tool_text:
            failures.append("writer tool must require explicit --port for live access")

        if "mode in {\"dry_run\", \"write\"} and not args.artifact" not in tool_text:
            failures.append("writer tool must require explicit --artifact for dry-run/write")

        forbidden_tokens = [
            "uf2",
            "RPI-RP2",
            "rpi-rp2",
            "reboot_bootloader",
            "copyfile(",
            "shutil.copy",
            "dd if=",
        ]
        for token in forbidden_tokens:
            if token in tool_text:
                failures.append(f"writer tool must not include flashing/copy behavior token: {token}")
    else:
        if not blocked:
            failures.append(
                "writer tool missing without blocker declaration in trace doc"
            )

    print(
        "writer_implemented="
        f"{'true' if writer_implemented else 'false'}"
    )
    print(f"blocked={'true' if blocked else 'false'}")
    print("firmware_flashing=false")

    if failures:
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    print("status=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
