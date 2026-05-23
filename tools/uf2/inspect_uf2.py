#!/usr/bin/env python3
"""Read-only UF2 inspection tooling.

This script only reads local UF2 files and prints metadata. It is not flashing,
upload, copy-to-device, mounted-device, or firmware-write tooling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any


BLOCK_SIZE = 512
PAYLOAD_OFFSET = 32
MAGIC_START_0 = 0x0A324655
MAGIC_START_1 = 0x9E5D5157
MAGIC_END = 0x0AB16F30
FLAG_FAMILY_ID_PRESENT = 0x00002000

OFFICIAL_UPDATE_APP_START = 0x10000000
OFFICIAL_UPDATE_APP_END = 0x1005DF00
OFFICIAL_CLEAN_HIGH_START = 0x1017F000
OFFICIAL_CLEAN_HIGH_END = 0x101FF000


def hex_range(start: int, end: int) -> str:
    return f"0x{start:08x}..0x{end:08x}"


def overlaps(start: int, end: int, other_start: int, other_end: int) -> bool:
    return start < other_end and other_start < end


def summarize_segments(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(blocks, key=lambda block: (block["target_address"], block["block_number"]))
    segments: list[dict[str, Any]] = []

    current: dict[str, Any] | None = None
    hasher = None
    for block in ordered:
        start = block["target_address"]
        payload = block["payload"]
        end = start + len(payload)

        if current is None or start != current["end_int"]:
            if current is not None:
                current["payload_sha256"] = hasher.hexdigest()
                segments.append(current)
            hasher = hashlib.sha256()
            current = {
                "range": hex_range(start, end),
                "start": f"0x{start:08x}",
                "end": f"0x{end:08x}",
                "start_int": start,
                "end_int": end,
                "payload_bytes": 0,
                "blocks": 0,
                "all_zero": True,
                "overlaps_official_update_app_range": False,
                "overlaps_official_clean_only_high_flash_range": False,
                "writes_outside_local_app_like_range": False,
            }

        assert current is not None
        assert hasher is not None
        current["end"] = f"0x{end:08x}"
        current["end_int"] = end
        current["range"] = hex_range(current["start_int"], end)
        current["payload_bytes"] += len(payload)
        current["blocks"] += 1
        current["all_zero"] = current["all_zero"] and all(byte == 0 for byte in payload)
        current["overlaps_official_update_app_range"] = (
            current["overlaps_official_update_app_range"]
            or overlaps(start, end, OFFICIAL_UPDATE_APP_START, OFFICIAL_UPDATE_APP_END)
        )
        current["overlaps_official_clean_only_high_flash_range"] = (
            current["overlaps_official_clean_only_high_flash_range"]
            or overlaps(start, end, OFFICIAL_CLEAN_HIGH_START, OFFICIAL_CLEAN_HIGH_END)
        )
        current["writes_outside_local_app_like_range"] = (
            current["writes_outside_local_app_like_range"]
            or start < OFFICIAL_UPDATE_APP_START
            or end > OFFICIAL_CLEAN_HIGH_START
        )
        hasher.update(payload)

    if current is not None:
        assert hasher is not None
        current["payload_sha256"] = hasher.hexdigest()
        segments.append(current)

    for segment in segments:
        del segment["start_int"]
        del segment["end_int"]

    return segments


def inspect_uf2(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    whole_sha256 = hashlib.sha256(data).hexdigest()
    result: dict[str, Any] = {
        "path": str(path),
        "size_bytes": len(data),
        "whole_file_sha256": whole_sha256,
        "uf2_magic_valid": False,
        "errors": [],
    }

    if len(data) % BLOCK_SIZE != 0:
        result["errors"].append("file size is not a multiple of 512 bytes")
        return result

    physical_blocks = len(data) // BLOCK_SIZE
    blocks: list[dict[str, Any]] = []
    declared_counts: set[int] = set()
    family_ids: set[int] = set()
    flags_values: set[int] = set()
    payload_sizes: set[int] = set()
    magic_valid_count = 0

    for index in range(physical_blocks):
        block = data[index * BLOCK_SIZE : (index + 1) * BLOCK_SIZE]
        (
            magic0,
            magic1,
            flags,
            target_address,
            payload_size,
            block_number,
            declared_count,
            family_or_file_size,
        ) = struct.unpack_from("<IIIIIIII", block, 0)
        (magic_end,) = struct.unpack_from("<I", block, BLOCK_SIZE - 4)

        if (magic0, magic1, magic_end) == (MAGIC_START_0, MAGIC_START_1, MAGIC_END):
            magic_valid_count += 1
        else:
            result["errors"].append(f"invalid UF2 magic in physical block {index}")

        declared_counts.add(declared_count)
        flags_values.add(flags)
        payload_sizes.add(payload_size)
        if flags & FLAG_FAMILY_ID_PRESENT:
            family_ids.add(family_or_file_size)

        if payload_size > BLOCK_SIZE - PAYLOAD_OFFSET - 4:
            result["errors"].append(f"payload too large in physical block {index}: {payload_size}")
            payload = b""
        else:
            payload = block[PAYLOAD_OFFSET : PAYLOAD_OFFSET + payload_size]

        blocks.append(
            {
                "target_address": target_address,
                "payload": payload,
                "block_number": block_number,
            }
        )

    block_numbers = [block["block_number"] for block in blocks]
    duplicate_block_numbers = sorted(
        number for number in set(block_numbers) if block_numbers.count(number) > 1
    )
    expected_numbers = set(range(physical_blocks))
    observed_numbers = set(block_numbers)
    missing_block_numbers = sorted(expected_numbers - observed_numbers)

    segments = summarize_segments(blocks)
    result.update(
        {
            "uf2_magic_valid": magic_valid_count == physical_blocks and not result["errors"],
            "magic_valid_blocks": magic_valid_count,
            "block_count": physical_blocks,
            "declared_block_count_values": sorted(declared_counts),
            "flags_values": [f"0x{value:08x}" for value in sorted(flags_values)],
            "family_ids": [f"0x{value:08x}" for value in sorted(family_ids)],
            "payload_size_values": sorted(payload_sizes),
            "total_payload_bytes": sum(segment["payload_bytes"] for segment in segments),
            "segments": segments,
            "any_segment_all_zero": any(segment["all_zero"] for segment in segments),
            "overlaps_official_update_app_range": any(
                segment["overlaps_official_update_app_range"] for segment in segments
            ),
            "overlaps_official_clean_only_high_flash_range": any(
                segment["overlaps_official_clean_only_high_flash_range"] for segment in segments
            ),
            "writes_outside_local_app_like_range": any(
                segment["writes_outside_local_app_like_range"] for segment in segments
            ),
            "duplicate_block_numbers": duplicate_block_numbers,
            "missing_block_numbers": missing_block_numbers,
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only UF2 metadata inspection.")
    parser.add_argument("uf2_paths", nargs="+", help="Local UF2 file path(s) to inspect.")
    args = parser.parse_args()

    summaries = [inspect_uf2(Path(path)) for path in args.uf2_paths]
    print(json.dumps(summaries, indent=2, sort_keys=True))
    return 1 if any(summary["errors"] for summary in summaries) else 0


if __name__ == "__main__":
    sys.exit(main())
