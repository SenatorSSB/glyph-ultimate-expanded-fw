#!/usr/bin/env python3
"""Generate deterministic Phase 7A offline runtime-config parser fixtures."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path
from typing import Any

try:
    from extract_glyph_identity_runtime_tables import (
        CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT,
        CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT,
        load_source_tables,
        runtime_table_id_names,
    )
    from glyph_runtime_config_binary_roundtrip import (
        BINARY_FORMAT_VERSION,
        BINARY_HEADER_FORMAT,
        BINARY_HEADER_LENGTH,
        BINARY_MAGIC,
        CRC_SIZE,
        DEFAULT_MODE_SCOPE,
        build_runtime_config_binary,
        decode_runtime_config_binary,
    )
    from glyph_runtime_config_parser_oracle import parse_payload
except ModuleNotFoundError:
    from tools.extract_glyph_identity_runtime_tables import (
        CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT,
        CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT,
        load_source_tables,
        runtime_table_id_names,
    )
    from tools.glyph_runtime_config_binary_roundtrip import (
        BINARY_FORMAT_VERSION,
        BINARY_HEADER_FORMAT,
        BINARY_HEADER_LENGTH,
        BINARY_MAGIC,
        CRC_SIZE,
        DEFAULT_MODE_SCOPE,
        build_runtime_config_binary,
        decode_runtime_config_binary,
    )
    from tools.glyph_runtime_config_parser_oracle import parse_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "docs" / "runtime_config" / "fixtures"
BIN_PATH = FIXTURE_DIR / "phase7a_valid_baseline_runtime_config_payload.bin"
JSON_PATH = FIXTURE_DIR / "phase7a_valid_baseline_runtime_config_payload.json"
REPORT_PATH = FIXTURE_DIR / "phase7a_valid_baseline_runtime_config_payload_report.json"
VECTOR_PATH = FIXTURE_DIR / "phase7a_runtime_config_parser_test_vectors.json"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _with_crc(payload_without_crc: bytes) -> bytes:
    return payload_without_crc + struct.pack("<I", zlib.crc32(payload_without_crc) & 0xFFFFFFFF)


def _set_header(payload: bytes, *, magic: bytes | None = None, version: int | None = None,
                mode_hash: int | None = None, table_count: int | None = None,
                point_count: int | None = None, order_count: int | None = None,
                refresh_crc: bool = True) -> bytes:
    values = list(struct.unpack(BINARY_HEADER_FORMAT, payload[:BINARY_HEADER_LENGTH]))
    if magic is not None:
        values[0] = magic
    if version is not None:
        values[1] = version
    if mode_hash is not None:
        values[2] = mode_hash
    if table_count is not None:
        values[3] = table_count
    if point_count is not None:
        values[4] = point_count
    if order_count is not None:
        values[6] = order_count
    body = struct.pack(BINARY_HEADER_FORMAT, *values) + payload[BINARY_HEADER_LENGTH:-CRC_SIZE]
    return _with_crc(body) if refresh_crc else body + payload[-CRC_SIZE:]


def _mutate_order(payload: bytes, order: bytes) -> bytes:
    body = payload[:BINARY_HEADER_LENGTH] + order + payload[BINARY_HEADER_LENGTH + len(order):-CRC_SIZE]
    return _with_crc(body)


def build_valid_payload() -> bytes:
    return build_runtime_config_binary(load_source_tables())


def build_valid_payload_json(payload: bytes) -> dict[str, Any]:
    decoded, issues = decode_runtime_config_binary(payload)
    if issues:
        raise ValueError("valid baseline fixture unexpectedly failed decode")
    return {
        "schema_name": "glyph_phase7a_valid_runtime_config_payload",
        "schema_version": 1,
        "status": "offline_parser_fixture_not_runtime_active",
        "mode_scope": DEFAULT_MODE_SCOPE,
        "magic": BINARY_MAGIC.decode("ascii"),
        "format_version": BINARY_FORMAT_VERSION,
        "table_count": decoded.table_count,
        "point_count_per_table": decoded.point_count_per_table,
        "table_order": decoded.table_order,
        "payload_hex": payload.hex(),
        "payload_sha256": sha256_bytes(payload),
        "caveats": [
            "not_runtime_loaded_config",
            "not_device_write",
            "not_webserial",
            "not_storage_behavior",
            "not_firmware_runtime_activation",
        ],
    }


def _vector(case_id: str, payload: bytes, expected_acceptance: bool, expected_error_code: str,
            expected_error_class: str, description: str, source_hash: str) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "description": description,
        "payload_hex": payload.hex(),
        "payload_sha256": sha256_bytes(payload),
        "source_fixture_hash": source_hash,
        "expected_acceptance": expected_acceptance,
        "expected_fallback_required": not expected_acceptance,
        "expected_error_code": expected_error_code,
        "expected_error_class": expected_error_class,
    }


def build_vectors(valid: bytes) -> dict[str, Any]:
    source_hash = sha256_bytes(valid)
    order = bytes(range(CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT))
    short = valid[:-12]
    extra = _with_crc(valid[:-CRC_SIZE] + b"\x00")
    coord = bytearray(valid)
    coord[BINARY_HEADER_LENGTH + CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT] = 255
    coord[BINARY_HEADER_LENGTH + CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT + 1] = 255
    vectors = [
        _vector("valid_baseline_payload", valid, True, "ok", "ok", "source-owned 27-table baseline", source_hash),
        _vector("wrong_magic", _set_header(valid, magic=b"BAD!", refresh_crc=True), False, "invalid:magic", "magic", "magic is not GCFG", source_hash),
        _vector("wrong_version", _set_header(valid, version=BINARY_FORMAT_VERSION + 1), False, "invalid:version", "version", "unsupported version", source_hash),
        _vector("wrong_mode", _set_header(valid, mode_hash=0), False, "invalid:mode_scope", "mode_scope", "mode hash is not MODE_ULTIMATE", source_hash),
        _vector("wrong_checksum", valid[:-1] + bytes([valid[-1] ^ 0xFF]), False, "invalid:checksum", "checksum", "trailing CRC32 does not match", source_hash),
        _vector("wrong_table_count", _set_header(valid, table_count=26), False, "invalid:table_count", "table_count", "table count is not 27", source_hash),
        _vector("wrong_point_count", _set_header(valid, point_count=8), False, "invalid:point_count", "point_count", "point count is not 9", source_hash),
        _vector("duplicate_table_id", _mutate_order(valid, bytes([0]) + order[1:-1] + bytes([0])), False, "invalid:table_id", "table_id", "table id order duplicates an id", source_hash),
        _vector("missing_table_id", _set_header(_mutate_order(valid, order[:-1]), order_count=26), False, "invalid:order_length", "order_length", "table id order omits a table", source_hash),
        _vector("unknown_table_id", _mutate_order(valid, order[:-1] + bytes([255])), False, "invalid:table_id", "table_id", "table id is outside RuntimeTableId order", source_hash),
        _vector("out_of_range_coordinate", bytes(coord[:-CRC_SIZE]) + valid[-CRC_SIZE:], False, "invalid:checksum", "checksum", "byte-level format cannot exceed 255; mutation is detected by checksum", source_hash),
        _vector("truncated_payload", short, False, "invalid:checksum", "checksum", "payload is truncated", source_hash),
        _vector("extra_bytes", extra, False, "invalid:payload_length", "payload_length", "payload has bytes after declared points", source_hash),
        _vector("forbidden_metadata_marker", _with_crc(valid[:-CRC_SIZE] + b"device_write"), False, "invalid:forbidden_metadata", "forbidden_metadata", "payload embeds a forbidden capability marker", source_hash),
    ]
    return {
        "schema_name": "glyph_phase7a_runtime_config_parser_test_vectors",
        "schema_version": 1,
        "status": "offline_parser_vectors_not_runtime_active",
        "mode_scope": DEFAULT_MODE_SCOPE,
        "table_count": CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT,
        "point_count_per_table": CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT,
        "vectors": vectors,
        "caveats": [
            "not_firmware_behavior",
            "not_runtime_loaded_config",
            "not_storage_behavior",
            "not_device_write",
            "not_webserial",
        ],
    }


def generate(write: bool) -> dict[str, Any]:
    valid = build_valid_payload()
    payload_json = build_valid_payload_json(valid)
    vectors = build_vectors(valid)
    report = {
        "schema_name": "glyph_phase7a_runtime_config_candidate_generation_report",
        "schema_version": 1,
        "status": "offline_parser_foundation_not_runtime_active",
        "payload_path": str(BIN_PATH.relative_to(REPO_ROOT)),
        "payload_json_path": str(JSON_PATH.relative_to(REPO_ROOT)),
        "test_vectors_path": str(VECTOR_PATH.relative_to(REPO_ROOT)),
        "payload_sha256": sha256_bytes(valid),
        "payload_size_bytes": len(valid),
        "table_count": CURRENT_BASELINE_CONFIG_EXPECTED_TABLE_COUNT,
        "point_count_per_table": CURRENT_BASELINE_CONFIG_EXPECTED_POINT_COUNT,
        "mode_scope": DEFAULT_MODE_SCOPE,
        "oracle_accepts_baseline": parse_payload(valid).accepted,
        "runtime_activation": False,
        "storage": False,
        "device_write": False,
        "webserial": False,
        "firmware_flashing": False,
    }
    if write:
        FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
        BIN_PATH.write_bytes(valid)
        JSON_PATH.write_text(json.dumps(payload_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        VECTOR_PATH.write_text(json.dumps(vectors, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-fixtures", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report = generate(args.write_fixtures)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("status=PASS")
        print(f"payload_sha256={report['payload_sha256']}")
        print(f"table_count={report['table_count']}")
        print(f"point_count_per_table={report['point_count_per_table']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
