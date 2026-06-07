#!/usr/bin/env python3
"""Offline runtime-config binary representation helpers for a deterministic preview artifact."""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

try:
    from extract_glyph_identity_runtime_tables import (
        CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT,
        CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT,
        DEFAULT_SOURCE_PATH,
        load_source_tables,
        runtime_table_id_names,
        normalized_table_names,
    )
except ModuleNotFoundError:
    from tools.extract_glyph_identity_runtime_tables import (
        CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT,
        CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT,
        DEFAULT_SOURCE_PATH,
        load_source_tables,
        runtime_table_id_names,
        normalized_table_names,
    )


DEFAULT_MODE_SCOPE = "MODE_ULTIMATE"
BINARY_SCHEMA_NAME = "glyph_runtime_config_binary_preview"
BINARY_SCHEMA_VERSION = 1
BINARY_MAGIC = b"GCFG"
BINARY_FORMAT_VERSION = 1
BINARY_HEADER_FORMAT = "<4s B I B B B B"
BINARY_HEADER_LENGTH = struct.calcsize(BINARY_HEADER_FORMAT)
CRC_SIZE = 4

REQUIRED_TABLE_NAMES = tuple(normalized_table_names())


@dataclass(frozen=True)
class BinaryIssue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class RuntimeConfigBinary:
    schema_name: str
    schema_version: int
    mode_scope: str
    table_count: int
    point_count_per_table: int
    table_order: list[str]
    tables: dict[str, list[tuple[int, int]]]


def _mode_id_hash(mode_scope: str) -> int:
    return zlib.crc32(mode_scope.encode("utf-8")) & 0xFFFFFFFF


def _ordered_table_points_from_source(source_path: Path = DEFAULT_SOURCE_PATH) -> dict[str, list[tuple[int, int]]]:
    raw_tables = load_source_tables(source_path)
    return {name: list(points) for name, points in raw_tables.items()}


def load_binary_file(path: Path) -> bytes:
    return path.read_bytes()


def build_runtime_config_binary(
    tables: dict[str, list[tuple[int, int]]],
    *,
    mode_scope: str = DEFAULT_MODE_SCOPE,
) -> bytes:
    """Serialize in a deterministic, offline-only binary container."""

    issues = validate_runtime_tables_payload(tables)
    if issues:
        raise ValueError("Cannot encode invalid payload: " + ", ".join(issue.code for issue in issues))

    table_order = list(REQUIRED_TABLE_NAMES)
    table_points = [tables[name] for name in table_order]
    point_count = len(table_points[0])
    table_count = len(table_order)

    header = struct.pack(
        BINARY_HEADER_FORMAT,
        BINARY_MAGIC,
        BINARY_FORMAT_VERSION,
        _mode_id_hash(mode_scope),
        table_count,
        point_count,
        0,
        table_count,
    )
    order_bytes = bytes(index for index, _ in enumerate(table_order))
    payload = bytearray(order_bytes)
    for points in table_points:
        for x, y in points:
            payload.append(int(x))
            payload.append(int(y))

    base_payload = header + payload
    crc = zlib.crc32(base_payload) & 0xFFFFFFFF
    return base_payload + struct.pack("<I", crc)


def decode_runtime_config_binary(payload: bytes) -> tuple[RuntimeConfigBinary, list[BinaryIssue]]:
    issues: list[BinaryIssue] = []

    if len(payload) < BINARY_HEADER_LENGTH + CRC_SIZE:
        issues.append(BinaryIssue("invalid:truncated_payload", "payload", "binary payload is too short"))
        return RuntimeConfigBinary(
            schema_name=BINARY_SCHEMA_NAME,
            schema_version=BINARY_SCHEMA_VERSION,
            mode_scope=DEFAULT_MODE_SCOPE,
            table_count=0,
            point_count_per_table=0,
            table_order=[],
            tables={},
        ), issues

    header = payload[:BINARY_HEADER_LENGTH]
    (
        magic,
        version,
        mode_hash,
        table_count,
        point_count,
        _reserved,
        table_id_order_count,
    ) = struct.unpack(BINARY_HEADER_FORMAT, header)

    if magic != BINARY_MAGIC:
        issues.append(BinaryIssue("invalid:magic", "header.magic", "container magic must be GCFG"))
    if version != BINARY_FORMAT_VERSION:
        issues.append(BinaryIssue("invalid:version", "header.version", f"unsupported version: {version}"))

    expected_mode_hash = _mode_id_hash(DEFAULT_MODE_SCOPE)
    if mode_hash != expected_mode_hash:
        issues.append(
            BinaryIssue(
                "invalid:mode_scope",
                "header.mode_scope_hash",
                "mode scope hash must be MODE_ULTIMATE",
            )
        )

    if table_count != CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT:
        issues.append(
            BinaryIssue(
                "invalid:table_count",
                "header.table_count",
                f"table_count must be {CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT}",
            )
        )
    if point_count != CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT:
        issues.append(
            BinaryIssue(
                "invalid:point_count",
                "header.point_count",
                f"point_count must be {CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT}",
            )
        )

    if table_id_order_count != table_count:
        issues.append(
            BinaryIssue(
                "invalid:order_length",
                "header.table_id_order_count",
                "table_id_order_count must equal table_count",
            )
        )

    body = payload[BINARY_HEADER_LENGTH : len(payload) - CRC_SIZE]
    crc_stored = struct.unpack("<I", payload[-CRC_SIZE:])[0]
    crc_actual = zlib.crc32(payload[:-CRC_SIZE]) & 0xFFFFFFFF
    if crc_actual != crc_stored:
        issues.append(
            BinaryIssue(
                "invalid:checksum",
                "crc32",
                "crc32 checksum does not match payload",
            )
        )

    if len(body) < table_id_order_count * point_count * 2:
        issues.append(
            BinaryIssue(
                "invalid:payload_length",
                "body",
                "payload does not contain enough table data",
            )
        )

    order_bytes_expected = BINARY_HEADER_LENGTH + table_id_order_count
    if len(payload) < order_bytes_expected + CRC_SIZE:
        issues.append(
            BinaryIssue(
                "invalid:truncated_order",
                "body.table_order",
                "table_order section is truncated",
            )
        )
        table_order = []
    else:
        table_order_indices = payload[BINARY_HEADER_LENGTH : BINARY_HEADER_LENGTH + table_id_order_count]
        table_order = []
        for index in table_order_indices:
            if index < len(REQUIRED_TABLE_NAMES):
                table_order.append(REQUIRED_TABLE_NAMES[index])
            else:
                table_order.append(f"index_{index}")
        missing = len(table_order) != table_id_order_count
        duplicate = len(set(table_order)) != len(table_order)
        out_of_range = any(index >= len(REQUIRED_TABLE_NAMES) for index in table_order_indices)
        if out_of_range:
            issues.append(
                BinaryIssue(
                    "invalid:table_id",
                    "body.table_order",
                    "table id index out of range",
                )
            )
        if duplicate:
            issues.append(
                BinaryIssue(
                    "invalid:table_id",
                    "body.table_order",
                    "table id order contains duplicate ids",
                )
            )
        if missing:
            issues.append(
                BinaryIssue(
                    "invalid:table_id",
                    "body.table_order",
                    "table id order length does not match table_count",
                )
            )

    table_points: dict[str, list[tuple[int, int]]] = {}
    point_bytes = payload[BINARY_HEADER_LENGTH + table_id_order_count : len(payload) - CRC_SIZE]
    expected_point_bytes = table_count * point_count * 2

    if len(point_bytes) != expected_point_bytes:
        issues.append(
            BinaryIssue(
                "invalid:payload_length",
                "body.payload",
                f"payload bytes must be exactly {expected_point_bytes}",
            )
        )
    if expected_point_bytes <= len(point_bytes) and table_order:
        read_offset = 0
        for table_name in table_order:
            points: list[tuple[int, int]] = []
            for _ in range(point_count):
                x = point_bytes[read_offset]
                y = point_bytes[read_offset + 1]
                points.append((x, y))
                read_offset += 2
            table_points[table_name] = points

    trailing_bytes = payload[BINARY_HEADER_LENGTH + table_id_order_count + expected_point_bytes : len(payload) - CRC_SIZE]
    if trailing_bytes:
        issues.append(
            BinaryIssue(
                "invalid:trailing_bytes",
                "payload",
                "payload contains extra bytes after declared points",
            )
        )

    if set(table_order) != set(REQUIRED_TABLE_NAMES) and not issues:
        issues.append(
            BinaryIssue(
                "invalid:table_ids",
                "body.table_order",
                "table_id_order must include every required table once",
            )
        )

    config = RuntimeConfigBinary(
        schema_name=BINARY_SCHEMA_NAME,
        schema_version=BINARY_SCHEMA_VERSION,
        mode_scope=DEFAULT_MODE_SCOPE,
        table_count=len(table_order),
        point_count_per_table=point_count,
        table_order=table_order,
        tables=table_points,
    )
    return config, issues


def validate_runtime_tables_payload(tables: dict[str, list[tuple[int, int]]]) -> list[BinaryIssue]:
    issues: list[BinaryIssue] = []

    if set(tables) != set(REQUIRED_TABLE_NAMES):
        missing = sorted(set(REQUIRED_TABLE_NAMES) - set(tables))
        extra = sorted(set(tables) - set(REQUIRED_TABLE_NAMES))
        if missing:
            issues.append(
                BinaryIssue(
                    "invalid:missing_table",
                    "tables",
                    f"missing tables: {', '.join(missing)}",
                )
            )
        if extra:
            issues.append(
                BinaryIssue(
                    "invalid:unexpected_table",
                    "tables",
                    f"unexpected tables: {', '.join(extra)}",
                )
            )
        return issues

    for table_name in REQUIRED_TABLE_NAMES:
        points = tables.get(table_name, [])
        if not isinstance(points, (list, tuple)):
            issues.append(
                BinaryIssue("invalid:table_points", f"tables.{table_name}", "table points must be an array")
            )
            continue
        if len(points) != CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT:
            issues.append(
                BinaryIssue(
                    "invalid:point_count",
                    f"tables.{table_name}",
                    f"{table_name} must have {CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT} points",
                )
            )
            continue
        for point_idx, point in enumerate(points):
            if (
                not isinstance(point, (list, tuple))
                or len(point) != 2
                or not all(isinstance(coord, int) for coord in point)
            ):
                issues.append(
                    BinaryIssue(
                        "invalid:table_points",
                        f"tables.{table_name}[{point_idx}]",
                        "each point must be [x, y]",
                    )
                )
                continue
            x, y = point
            if not 0 <= x <= 255 or not 0 <= y <= 255:
                issues.append(
                    BinaryIssue(
                        "invalid:coordinate",
                        f"tables.{table_name}[{point_idx}]",
                        "coordinates must be in range 0..255",
                    )
                )

    return issues


def build_source_reference_payload() -> dict[str, object]:
    return {
        "schema_name": BINARY_SCHEMA_NAME,
        "schema_version": BINARY_SCHEMA_VERSION,
        "mode_scope": DEFAULT_MODE_SCOPE,
        "table_count": CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT,
        "point_count_per_table": CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT,
        "mode_id_hash_le": _mode_id_hash(DEFAULT_MODE_SCOPE),
        "table_order": list(runtime_table_id_names()),
    }


def command_build_bin(source_path: Path, output: Path) -> None:
    tables = _ordered_table_points_from_source(source_path)
    payload = build_runtime_config_binary(tables)
    output.write_bytes(payload)
    print(f"output={output.as_posix()}")
    print(f"bytes={len(payload)}")


def command_decode(path: Path) -> None:
    payload = path.read_bytes()
    config, issues = decode_runtime_config_binary(payload)
    if issues:
        print("status=FAIL")
        for issue in issues:
            print(f"{issue.code}:{issue.path}={issue.message}")
        raise SystemExit(1)

    print("status=PASS")
    print(f"schema_name={config.schema_name}")
    print(f"schema_version={config.schema_version}")
    print(f"mode_scope={config.mode_scope}")
    print(f"table_count={config.table_count}")
    print(f"point_count_per_table={config.point_count_per_table}")
    print(f"table_order_count={len(config.table_order)}")


def command_roundtrip() -> None:
    tables = _ordered_table_points_from_source()
    payload = build_runtime_config_binary(tables)
    config, issues = decode_runtime_config_binary(payload)
    if issues:
        print("status=FAIL")
        for issue in issues:
            print(f"{issue.code}:{issue.path}={issue.message}")
        raise SystemExit(1)
    if config.table_order != list(REQUIRED_TABLE_NAMES):
        print("status=FAIL")
        print("error=decoded table order mismatch")
        raise SystemExit(1)
    print("status=PASS")
    print(f"bytes={len(payload)}")
    print(f"magic={BINARY_MAGIC.decode('ascii')}")
    print(f"schema={config.schema_name}")
    print(f"schema_version={config.schema_version}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="encode source-backed runtime tables to binary")
    build_parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_PATH)
    build_parser.add_argument("--output", type=Path, required=True)

    decode_parser = subparsers.add_parser("decode", help="decode a runtime-config binary preview")
    decode_parser.add_argument("path", type=Path)

    subparsers.add_parser("roundtrip", help="roundtrip source-backed tables through binary serializer")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.command == "build":
        command_build_bin(args.source, args.output)
        return 0
    if args.command == "decode":
        command_decode(args.path)
        return 0
    if args.command == "roundtrip":
        command_roundtrip()
        return 0
    raise ValueError(f"unsupported command {args.command!r}")


if __name__ == "__main__":
    raise SystemExit(main())
