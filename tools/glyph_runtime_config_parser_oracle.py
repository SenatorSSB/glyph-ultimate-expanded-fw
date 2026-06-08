#!/usr/bin/env python3
"""Host-side oracle for the Phase 7A offline GCFG-like parser corpus.

This is not firmware behavior, not device write, and not runtime-loaded config.
It decodes the existing offline binary preview format and reports whether a
candidate would be accepted by this design-time oracle.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from glyph_runtime_config_binary_roundtrip import (
        BINARY_HEADER_FORMAT,
        BINARY_HEADER_LENGTH,
        BINARY_MAGIC,
        CRC_SIZE,
        decode_runtime_config_binary,
    )
except ModuleNotFoundError:
    from tools.glyph_runtime_config_binary_roundtrip import (
        BINARY_HEADER_FORMAT,
        BINARY_HEADER_LENGTH,
        BINARY_MAGIC,
        CRC_SIZE,
        decode_runtime_config_binary,
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VECTOR_PATH = (
    REPO_ROOT / "docs" / "runtime_config" / "fixtures" / "phase7a_runtime_config_parser_test_vectors.json"
)
FORBIDDEN_MARKERS = (
    b"runtime_loaded_config",
    b"device_write",
    b"webserial",
    b"flash_uf2",
    b"config.bin",
)


@dataclass(frozen=True)
class OracleResult:
    accepted: bool
    fallback_required: bool
    error_code: str
    error_class: str
    table_count: int
    point_count_per_table: int
    runtime_activation_claimed: bool


def _payload_from_vector(vector: dict[str, Any]) -> bytes:
    if "payload_hex" in vector:
        return bytes.fromhex(str(vector["payload_hex"]))
    if "payload_base64" in vector:
        return base64.b64decode(str(vector["payload_base64"]))
    raise ValueError(f"vector {vector.get('case_id', '<unknown>')} has no payload_hex/payload_base64")


def parse_payload(payload: bytes) -> OracleResult:
    runtime_activation_claimed = any(marker in payload.lower() for marker in FORBIDDEN_MARKERS)
    decoded, issues = decode_runtime_config_binary(payload)

    if runtime_activation_claimed:
        return OracleResult(
            accepted=False,
            fallback_required=True,
            error_code="invalid:forbidden_metadata",
            error_class="forbidden_metadata",
            table_count=decoded.table_count,
            point_count_per_table=decoded.point_count_per_table,
            runtime_activation_claimed=True,
        )

    if issues:
        first = issues[0]
        return OracleResult(
            accepted=False,
            fallback_required=True,
            error_code=first.code,
            error_class=first.code.removeprefix("invalid:"),
            table_count=decoded.table_count,
            point_count_per_table=decoded.point_count_per_table,
            runtime_activation_claimed=False,
        )

    return OracleResult(
        accepted=True,
        fallback_required=False,
        error_code="ok",
        error_class="ok",
        table_count=decoded.table_count,
        point_count_per_table=decoded.point_count_per_table,
        runtime_activation_claimed=False,
    )


def validate_vectors(path: Path = DEFAULT_VECTOR_PATH) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    vectors = data.get("vectors")
    if not isinstance(vectors, list):
        raise ValueError("parser test-vector corpus must contain a vectors list")

    results: list[dict[str, Any]] = []
    for vector in vectors:
        if not isinstance(vector, dict):
            raise ValueError("parser vector entries must be objects")
        payload = _payload_from_vector(vector)
        result = parse_payload(payload)
        expected_acceptance = vector.get("expected_acceptance")
        expected_fallback = vector.get("expected_fallback_required")
        expected_error = vector.get("expected_error_code")
        case_id = vector.get("case_id", "<unknown>")

        if result.accepted != expected_acceptance:
            raise ValueError(f"{case_id}: accepted={result.accepted} expected {expected_acceptance}")
        if result.fallback_required != expected_fallback:
            raise ValueError(f"{case_id}: fallback={result.fallback_required} expected {expected_fallback}")
        if expected_error is not None and result.error_code != expected_error:
            raise ValueError(f"{case_id}: error={result.error_code!r} expected {expected_error!r}")
        results.append({"case_id": case_id, **asdict(result)})
    return results


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    decode = subparsers.add_parser("decode", help="decode one payload file")
    decode.add_argument("path", type=Path)

    validate = subparsers.add_parser("validate-vectors", help="validate parser test vectors")
    validate.add_argument("--vectors", type=Path, default=DEFAULT_VECTOR_PATH)
    validate.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.command == "decode":
        print(json.dumps(asdict(parse_payload(args.path.read_bytes())), indent=2, sort_keys=True))
        return 0
    if args.command == "validate-vectors":
        results = validate_vectors(args.vectors)
        if args.json:
            print(json.dumps(results, indent=2, sort_keys=True))
        else:
            print("status=PASS")
            print(f"vectors={len(results)}")
        return 0
    raise ValueError(f"unsupported command {args.command!r}")


if __name__ == "__main__":
    raise SystemExit(main())
