#!/usr/bin/env python3
"""Install or preview generated source-owned runtime config alias artifacts.

This is an offline source-file workflow only. It can either:

- regenerate the generated source-owned baseline text from a validated
  layout-spec packet, or
- ingest already-generated C++ output text,

and then either dry-run the install to stdout or write only to the inert
source-owned alias path under ``src/modes/runtime_config/generated_source_owned``.

It does not touch device state, firmware flashing, runtime-loaded config, or
any active RuntimeConfigView publication path.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from generate_source_owned_runtime_config import (
    GeneratorContractError,
    assert_inert_source_install_path,
    generate_from_layout_spec,
)
from glyph_source_owned_overlay import OverlayContractError, generate_overlay_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INSTALL_PATH = REPO_ROOT / "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
FORBIDDEN_OUTPUT_TOKENS = (
    "GetActiveRuntimeConfigState",
    "ResolveActiveRuntimeConfig",
    "UpdateAnalogOutputs",
    "active_view =",
    "candidate.view",
    "active_storage.view",
    "RuntimeConfigStorage",
    "WebSerial",
    "config.pb",
    "flash",
    "flashing",
)


class GeneratedSourceOwnedRuntimeConfigInstallError(RuntimeError):
    """Raised when the offline install workflow rejects an input or path."""


def fail(message: str) -> None:
    raise GeneratedSourceOwnedRuntimeConfigInstallError(message)


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required input: {path}")
    return path.read_text(encoding="utf-8")


def validate_generated_output_text(text: str) -> None:
    if "generated source-owned runtime config artifact" not in text:
        fail("generated output is missing the required source-owned marker")
    if "inert generated-table placeholder" not in text:
        fail("generated output is missing the inert-table marker")
    if "not wired into runtime selection" not in text:
        fail("generated output is missing the non-active marker")
    for token in FORBIDDEN_OUTPUT_TOKENS:
        if token in text:
            fail(f"generated output contains forbidden active-path token: {token}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--from-layout-spec",
        type=Path,
        help="layout-spec JSON packet to regenerate the source-owned baseline text",
    )
    input_group.add_argument(
        "--from-generated-output",
        type=Path,
        help="already-generated C++ artifact text to install or preview",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_INSTALL_PATH,
        help="inert source-owned alias path to write; ignored in dry-run mode",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the would-be installed text to stdout without writing files",
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="apply production provenance and explicit overlay/full-replacement gates",
    )
    return parser


def generate_install_text(args: argparse.Namespace) -> str:
    if args.from_layout_spec is not None:
        try:
            if args.production:
                import json
                payload = json.loads(args.from_layout_spec.read_text(encoding="utf-8"))
                generate_overlay_payload(payload, production=True)
            return generate_from_layout_spec(args.from_layout_spec)
        except (GeneratorContractError, OverlayContractError, OSError, ValueError) as exc:
            fail(str(exc))
    assert args.from_generated_output is not None
    return read_required(args.from_generated_output)


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        install_text = generate_install_text(args)
        validate_generated_output_text(install_text)
        if args.dry_run:
            sys.stdout.write(install_text)
            return 0
        assert_inert_source_install_path(args.output)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(install_text, encoding="utf-8")
    except (GeneratedSourceOwnedRuntimeConfigInstallError, GeneratorContractError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
