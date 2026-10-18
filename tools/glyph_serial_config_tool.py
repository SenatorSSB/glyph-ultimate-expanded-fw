#!/usr/bin/env python3
"""Guarded repo-local serial config tool for Glyph configurator protocol."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass, field
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import termios
import time
from types import ModuleType
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[1]
BLOCKER_CODE = "HOST_SERIAL_CONFIG_WRITER_BLOCKED_BY_DEPENDENCY_OR_PROTOCOL"

CMD_GET_CONFIG = 3
CMD_SET_CONFIG = 4
CMD_ERROR = 5
CMD_SUCCESS = 6

EXPECTED_COMMAND_IDS = {
    "CMD_GET_CONFIG": CMD_GET_CONFIG,
    "CMD_SET_CONFIG": CMD_SET_CONFIG,
    "CMD_ERROR": CMD_ERROR,
    "CMD_SUCCESS": CMD_SUCCESS,
}

_V2_REQUIRED_ROUTING_SLOTS = {
    4, 18, 19, 20, 24, 25, 34, 35, 36, 37, 41, 42, 43, 44, 45,
}
_V3_REQUIRED_ROUTING_SLOTS = {
    1, 2, 3, 4, 5, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 29,
    32, 33, 34, 35, 36, 37, 38, 41, 42, 43, 44, 45, 52, 53, 54, 55,
}


class ToolError(RuntimeError):
    """Known tool failure with optional blocker classification."""

    def __init__(self, message: str, *, blocker: bool = False) -> None:
        super().__init__(message)
        self.blocker = blocker


@dataclass
class RunState:
    """Mutable execution status for final status-line reporting."""

    mode: str
    artifact_validated: bool = False
    live_device_access: bool = False
    active_device_profile_updated: bool = False
    readback_verified: bool = False
    failures: list[str] = field(default_factory=list)
    blocker: bool = False


class PosixSerialPort:
    """Small stdlib-only serial transport for USB CDC ports on POSIX."""

    def __init__(self, path: str, baudrate: int, timeout_sec: float) -> None:
        self.path = path
        self.baudrate = baudrate
        self.timeout_sec = timeout_sec
        self.fd: int | None = None
        self._rx_buffer = bytearray()

    def open(self) -> None:
        flags = os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK
        try:
            self.fd = os.open(self.path, flags)
        except OSError as exc:
            raise ToolError(f"failed to open serial port {self.path}: {exc}") from exc
        try:
            self._configure()
            self.flush_input()
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        self._rx_buffer.clear()

    def _configure(self) -> None:
        assert self.fd is not None
        attrs = termios.tcgetattr(self.fd)
        attrs[0] = 0
        attrs[1] = 0
        attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        attrs[3] = 0
        attrs[6][termios.VMIN] = 0
        attrs[6][termios.VTIME] = 0

        speed = getattr(termios, f"B{self.baudrate}", None)
        if speed is None:
            raise ToolError(
                f"unsupported baudrate={self.baudrate}; choose a POSIX-supported baud value"
            )
        attrs[4] = speed
        attrs[5] = speed
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
        termios.tcflush(self.fd, termios.TCIOFLUSH)

    def flush_input(self) -> None:
        assert self.fd is not None
        self._rx_buffer.clear()
        while True:
            ready, _, _ = select.select([self.fd], [], [], 0)
            if not ready:
                break
            chunk = os.read(self.fd, 4096)
            if not chunk:
                break

    def write_all(self, data: bytes) -> None:
        assert self.fd is not None
        total = 0
        while total < len(data):
            _, ready, _ = select.select([], [self.fd], [], self.timeout_sec)
            if not ready:
                raise ToolError("timed out waiting for serial port write availability")
            written = os.write(self.fd, data[total:])
            if written <= 0:
                raise ToolError("serial write returned no progress")
            total += written

    def read_packet(self) -> bytes:
        assert self.fd is not None
        deadline = time.monotonic() + self.timeout_sec
        while True:
            eop_index = self._rx_buffer.find(b"\x00")
            if eop_index >= 0:
                packet = bytes(self._rx_buffer[: eop_index + 1])
                del self._rx_buffer[: eop_index + 1]
                return packet
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ToolError("timed out waiting for serial response packet")
            ready, _, _ = select.select([self.fd], [], [], remaining)
            if not ready:
                continue
            chunk = os.read(self.fd, 4096)
            if not chunk:
                continue
            self._rx_buffer.extend(chunk)

    def transact(
        self,
        command_id: int,
        payload: bytes,
        *,
        stage_callback: Callable[[str], None] | None = None,
    ) -> tuple[int, bytes]:
        raw_packet = bytes([command_id]) + payload
        encoded = cobs_encode(raw_packet)
        if stage_callback is not None:
            stage_callback("write_attempted")
        self.write_all(encoded)
        if stage_callback is not None:
            stage_callback("full_host_write_completed")
            stage_callback("awaiting_response")
        response_packet = self.read_packet()
        if stage_callback is not None:
            stage_callback("response_received")
        decoded = cobs_decode(response_packet)
        if not decoded:
            raise ToolError("received empty decoded packet")
        return decoded[0], decoded[1:]


def cobs_encode(payload: bytes) -> bytes:
    out = bytearray()
    code_index = 0
    out.append(0)
    code = 1
    for value in payload:
        if value == 0:
            out[code_index] = code
            code_index = len(out)
            out.append(0)
            code = 1
            continue
        out.append(value)
        code += 1
        if code == 0xFF:
            out[code_index] = code
            code_index = len(out)
            out.append(0)
            code = 1
    out[code_index] = code
    out.append(0)
    return bytes(out)


def cobs_decode(packet: bytes) -> bytes:
    if not packet or packet[-1] != 0:
        raise ToolError("invalid COBS packet: missing null terminator")
    end = len(packet) - 1
    index = 0
    out = bytearray()
    while index < end:
        code = packet[index]
        if code == 0:
            raise ToolError("invalid COBS packet: zero code encountered")
        index += 1
        next_index = index + code - 1
        if next_index > end:
            raise ToolError("invalid COBS packet: overrun while decoding")
        out.extend(packet[index:next_index])
        index = next_index
        if code != 0xFF and index < end:
            out.append(0)
    if index != end:
        raise ToolError("invalid COBS packet: trailing undecoded bytes")
    return bytes(out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Guarded serial config tool for Glyph configurator protocol. "
            "Never flashes firmware and never writes config without --write."
        )
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--dry-run", action="store_true", help="Validate and encode artifact only.")
    mode_group.add_argument("--read", action="store_true", help="Read active config from device.")
    mode_group.add_argument("--write", action="store_true", help="Write artifact config to device.")
    parser.add_argument("--artifact", help="Path to config/profile JSON artifact for dry-run or write.")
    parser.add_argument("--port", help="Serial device path, e.g. /dev/cu.usbmodem2101.")
    parser.add_argument("--backup-out", help="Write JSON backup only when explicitly provided.")
    parser.add_argument(
        "--baudrate",
        type=int,
        default=115200,
        help="Serial baudrate (default: 115200). USB CDC may ignore this setting.",
    )
    parser.add_argument(
        "--timeout-sec",
        type=float,
        default=5.0,
        help="Packet response timeout in seconds (default: 5.0).",
    )
    args = parser.parse_args()
    if not args.dry_run and not args.read and not args.write:
        args.dry_run = True
    return args


def mode_from_args(args: argparse.Namespace) -> str:
    if args.write:
        return "write"
    if args.read:
        return "read"
    return "dry_run"


def require_cli_guards(args: argparse.Namespace, mode: str) -> None:
    if mode in {"dry_run", "write"} and not args.artifact:
        raise ToolError(f"mode={mode} requires --artifact <path>")
    if mode in {"read", "write"} and not args.port:
        raise ToolError(f"mode={mode} requires --port /dev/cu.usbmodem...")


def ensure_dependency(module_name: str, blocker_hint: str) -> None:
    if importlib.util.find_spec(module_name) is None:
        raise ToolError(
            f"missing dependency: {module_name}. {blocker_hint}",
            blocker=True,
        )


def find_config_proto(repo_root: Path) -> Path:
    """Return the reviewed, tracked schema; never derive wire shape from .pio cache."""
    candidate = repo_root / "schema" / "haybox" / "config.proto"
    if candidate.is_file():
        return candidate
    raise ToolError(
        "could not locate tracked schema/haybox/config.proto; refusing mutable .pio cache schema",
        blocker=True,
    )


def load_runtime_proto_modules(repo_root: Path) -> tuple[ModuleType, ModuleType, Path]:
    ensure_dependency(
        "grpc_tools.protoc",
        "protobuf Python code generation is required for artifact encode/decode.",
    )
    ensure_dependency(
        "google.protobuf.json_format",
        "protobuf JSON conversion is required for artifact encode/decode.",
    )

    from google.protobuf import json_format  # type: ignore

    proto_path = find_config_proto(repo_root)
    with tempfile.TemporaryDirectory(prefix="glyph_config_pb2_") as temp_dir:
        command = [
            sys.executable,
            "-m",
            "grpc_tools.protoc",
            f"--proto_path={proto_path.parent}",
            f"--python_out={temp_dir}",
            str(proto_path),
        ]
        completed = subprocess.run(
            command,
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise ToolError(
                "failed to generate Python protobuf bindings from config.proto: "
                f"{completed.stderr.strip() or completed.stdout.strip()}",
                blocker=True,
            )
        module_path = Path(temp_dir) / "config_pb2.py"
        if not module_path.exists():
            raise ToolError(
                "grpc_tools.protoc completed but config_pb2.py was not generated",
                blocker=True,
            )
        spec = importlib.util.spec_from_file_location("glyph_config_pb2_runtime", module_path)
        if spec is None or spec.loader is None:
            raise ToolError(
                "failed to load generated config_pb2.py module",
                blocker=True,
            )
        config_pb2 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_pb2)

    for command_name, expected_value in EXPECTED_COMMAND_IDS.items():
        actual_value = getattr(config_pb2, command_name, None)
        if actual_value != expected_value:
            raise ToolError(
                "command ID mismatch for "
                f"{command_name}: expected={expected_value}, actual={actual_value}",
                blocker=True,
            )

    return config_pb2, json_format, proto_path


def load_artifact_json(artifact_path: Path) -> dict[str, Any]:
    if not artifact_path.exists():
        raise ToolError(f"artifact path does not exist: {artifact_path}")
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ToolError(f"artifact JSON parse failure: {exc}") from exc
    if not isinstance(payload, dict):
        raise ToolError("artifact root JSON value must be an object")
    return payload


def decode_config_payload(payload: bytes, config_pb2: ModuleType) -> Any:
    message = config_pb2.Config()
    try:
        message.ParseFromString(payload)
    except Exception as exc:  # pragma: no cover - protobuf exception types are runtime-provided.
        raise ToolError(f"failed to decode protobuf config payload: {exc}") from exc
    return message


def encode_artifact_payload(
    artifact_data: dict[str, Any],
    config_pb2: ModuleType,
    json_format: ModuleType,
) -> tuple[Any, bytes]:
    config_message = config_pb2.Config()
    try:
        json_format.ParseDict(artifact_data, config_message, ignore_unknown_fields=False)
    except Exception as exc:  # pragma: no cover - protobuf exception types are runtime-provided.
        raise ToolError(f"failed to parse artifact into protobuf Config: {exc}") from exc
    payload = config_message.SerializeToString()
    if not payload:
        raise ToolError("artifact encoded to empty protobuf payload")
    return config_message, payload


def verify_ultimate_mode_bindings(ultimate_mode: Any, config_pb2: ModuleType, label: str) -> list[str]:
    failures: list[str] = []
    remaps = list(ultimate_mode.button_remapping)

    rf3_entries = [
        remap for remap in remaps if remap.physical_button == config_pb2.BTN_RF3
    ]
    rf4_entries = [
        remap for remap in remaps if remap.physical_button == config_pb2.BTN_RF4
    ]
    rf3_to_lt1 = [
        remap
        for remap in remaps
        if remap.physical_button == config_pb2.BTN_RF3 and remap.activates == config_pb2.BTN_LT1
    ]
    rf4_to_lt2 = [
        remap
        for remap in remaps
        if remap.physical_button == config_pb2.BTN_RF4 and remap.activates == config_pb2.BTN_LT2
    ]
    lt3_entries = [remap for remap in remaps if remap.physical_button == config_pb2.BTN_LT3]
    lt3_to_lt3 = [remap for remap in lt3_entries if remap.activates == config_pb2.BTN_LT3]
    lt3_to_lf4 = [remap for remap in lt3_entries if remap.activates == config_pb2.BTN_LF4]
    physical_buttons = [remap.physical_button for remap in remaps]
    duplicates = sorted(
        {
            button
            for button in physical_buttons
            if physical_buttons.count(button) > 1
        }
    )
    semantic_remap_count = sum(
        1
        for remap in remaps
        if remap.activates not in (config_pb2.BTN_UNSPECIFIED, remap.physical_button)
    )
    omitted_activates_count = sum(
        1 for remap in remaps if remap.activates == config_pb2.BTN_UNSPECIFIED
    )
    explicit_self_activates_count = sum(
        1 for remap in remaps if remap.activates == remap.physical_button
    )
    identity_mode = (
        omitted_activates_count == 0
        and semantic_remap_count == 0
        and explicit_self_activates_count == len(remaps)
    )
    historical_mode = (
        len(rf3_to_lt1) == 1 and len(rf4_to_lt2) == 1 and len(lt3_to_lt3) == 1
    )

    if duplicates:
        failures.append(
            f"duplicate physical remap entries in {label}: "
            + ", ".join(str(button) for button in duplicates)
        )

    if len(rf3_entries) != 1:
        failures.append(
            f"expected exactly one BTN_RF3 physical remap entry in {label}, "
            f"found {len(rf3_entries)}"
        )
    if len(rf4_entries) != 1:
        failures.append(
            f"expected exactly one BTN_RF4 physical remap entry in {label}, "
            f"found {len(rf4_entries)}"
        )
    if len(lt3_entries) != 1:
        failures.append(
            f"expected exactly one BTN_LT3 physical remap entry in {label}, "
            f"found {len(lt3_entries)}"
        )
    if lt3_to_lf4:
        failures.append(f"unexpected BTN_LT3 -> BTN_LF4 mapping present in {label}")

    if not historical_mode and not identity_mode:
        failures.append(
            "expected either historical LT3 remap bindings "
            "(RF3->LT1, RF4->LT2, LT3->LT3) or explicit self-activates identity-baseline remap representation"
        )
    if historical_mode and identity_mode:
        failures.append("ambiguous mode: both historical and identity conditions matched")
    if not historical_mode and omitted_activates_count > 0:
        failures.append(
            "identity baseline requires explicit activates; "
            f"found {omitted_activates_count} omitted activates entries"
        )

    if historical_mode and len(rf3_to_lt1) != 1:
        failures.append(
            "expected exactly one BTN_RF3 -> BTN_LT1 mapping, "
            f"found {len(rf3_to_lt1)}"
        )
    if historical_mode and len(rf4_to_lt2) != 1:
        failures.append(
            "expected exactly one BTN_RF4 -> BTN_LT2 mapping, "
            f"found {len(rf4_to_lt2)}"
        )
    if historical_mode and len(lt3_to_lt3) != 1:
        failures.append(
            "expected exactly one BTN_LT3 -> BTN_LT3 mapping, "
            f"found {len(lt3_to_lt3)}"
        )

    return failures


def verify_ultimate_profiles(config_message: Any, config_pb2: ModuleType) -> list[str]:
    """Validate the bounded schema-backed Ultimate profile wire shape.

    This mirrors the finite versioned admission checks in production
    validation. It does not claim that firmware has consumed a runtime-loaded
    profile or that any device write is safe.
    """
    def invalid_condition(condition: Any, roles: set[int], routed: set[int], maximum_role_id: int,
                          allow_function: bool = False, physical_only: bool = False) -> bool:
        if not condition:
            return True
        seen: set[int] = set()
        for tokens in (condition.all_tokens, condition.any_tokens, condition.none_tokens):
            for token in tokens:
                if token in seen or not (1 <= token <= 60 or 65 <= token <= 96 or
                                         (allow_function and token == 97)):
                    return True
                seen.add(token)
                if token <= 60:
                    if not physical_only and token not in routed:
                        return True
                elif token != 97 and (physical_only or token - 64 > maximum_role_id or token - 64 not in roles):
                    return True
        return False

    def effect_key(effect: Any) -> int | None:
        pairs = {
            (config_pb2.ULTIMATE_OUTPUT_PHASE_DIGITAL, config_pb2.ULTIMATE_OUTPUT_TARGET_DIGITAL): 0,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_BASE_TABLE, config_pb2.ULTIMATE_OUTPUT_TARGET_LEFT_STICK): 1,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_BASE_TABLE, config_pb2.ULTIMATE_OUTPUT_TARGET_RIGHT_STICK): 2,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_DIRECTION_A, config_pb2.ULTIMATE_OUTPUT_TARGET_LEFT_STICK): 3,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_RF6, config_pb2.ULTIMATE_OUTPUT_TARGET_LEFT_STICK): 4,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_RF7, config_pb2.ULTIMATE_OUTPUT_TARGET_LEFT_STICK): 5,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_RS_DIAGONAL, config_pb2.ULTIMATE_OUTPUT_TARGET_RIGHT_STICK): 6,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_RF3_VERTICAL, config_pb2.ULTIMATE_OUTPUT_TARGET_RIGHT_STICK): 7,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_NULL, config_pb2.ULTIMATE_OUTPUT_TARGET_ANALOGUE_NULL): 8,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_TRIGGERS, config_pb2.ULTIMATE_OUTPUT_TARGET_TRIGGER_L): 9,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_TRIGGERS, config_pb2.ULTIMATE_OUTPUT_TARGET_TRIGGER_R): 10,
            (config_pb2.ULTIMATE_OUTPUT_PHASE_DPAD, config_pb2.ULTIMATE_OUTPUT_TARGET_DPAD_LEFT_STICK): 11,
        }
        return pairs.get((effect.phase, effect.target))

    def invalid_effect_shape(effect: Any, key: int) -> bool:
        if key in (0, 9, 10):
            shared = (
                effect.direction_source != 0 or effect.coordinate_mode != 0 or
                effect.table_id != 0 or effect.mode_table_id != 0 or
                effect.fixed_x != 0 or effect.fixed_y != 0 or effect.coordinates
            )
            if shared:
                return True
            if key == 0:
                return (
                    effect.value != 0 or effect.suppress or
                    ((effect.digital_set_mask | effect.digital_clear_mask) & ~0xFFF) != 0 or
                    (effect.digital_set_mask & effect.digital_clear_mask) != 0
                )
            return effect.digital_set_mask != 0 or effect.digital_clear_mask != 0

        if effect.digital_set_mask or effect.digital_clear_mask:
            return True
        if (key == 11 and effect.value > 7) or (key != 11 and effect.value != 0):
            return True
        if not 1 <= effect.direction_source <= 4:
            return True
        if key == 11 and effect.direction_source != config_pb2.ULTIMATE_DIRECTION_SOURCE_CENTER:
            return True
        if effect.coordinate_mode == config_pb2.ULTIMATE_COORDINATE_SELECTED_TABLE:
            return not (key == 1 and effect.table_id == 0 and effect.mode_table_id == 0 and
                        not effect.coordinates and effect.fixed_x == 0 and effect.fixed_y == 0)
        if effect.coordinate_mode == config_pb2.ULTIMATE_COORDINATE_TABLE:
            return not (effect.table_id < 28 and effect.mode_table_id < 28 and
                        not effect.coordinates and effect.fixed_x == 0 and effect.fixed_y == 0)
        if effect.coordinate_mode == config_pb2.ULTIMATE_COORDINATE_FIXED:
            return not (effect.table_id == 0 and effect.mode_table_id == 0 and not effect.coordinates)
        if effect.coordinate_mode == config_pb2.ULTIMATE_COORDINATE_INLINE:
            return not (effect.table_id == 0 and effect.mode_table_id == 0 and
                        len(effect.coordinates) == 18 and effect.fixed_x == 0 and effect.fixed_y == 0)
        return True

    failures: list[str] = []
    profiles = list(config_message.ultimate_profiles)
    if len(profiles) > 2:
        failures.append(f"Stage-A supports at most two ultimate_profiles, found {len(profiles)}")

    for profile_index, profile in enumerate(profiles, start=1):
        label = f"ultimate_profiles[{profile_index}]"
        if profile.schema_version not in (1, 2, 3, 4):
            failures.append(
                f"{label}.schema_version must be one of [1, 2, 3, 4], got {profile.schema_version}"
            )
        if len(profile.tables) != 28:
            failures.append(f"{label}.tables must contain 28 entries, found {len(profile.tables)}")
        else:
            seen_table_ids: set[int] = set()
            for table_index, table in enumerate(profile.tables):
                table_label = f"{label}.tables[{table_index}]"
                if table.table_id >= 28:
                    failures.append(f"{table_label}.table_id must be in [0,27], got {table.table_id}")
                elif table.table_id in seen_table_ids:
                    failures.append(f"{label} has duplicate table_id {table.table_id}")
                else:
                    seen_table_ids.add(table.table_id)
                if len(table.coordinates) != 9:
                    failures.append(f"{table_label}.coordinates must contain 9 entries, found {len(table.coordinates)}")
            missing_table_ids = sorted(set(range(28)) - seen_table_ids)
            if missing_table_ids:
                failures.append(f"{label} is missing table IDs: {missing_table_ids}")

        has_output_program = profile.HasField("output_program")
        if profile.schema_version == 1:
            if (profile.roles or profile.routing_slots or profile.default_table_id != 0 or
                    profile.table_rules or has_output_program or profile.function_bindings):
                failures.append(f"{label} adds fields to schema version 1")
            continue

        if (has_output_program or profile.function_bindings) and profile.schema_version == 2:
            failures.append(f"{label} adds an output program to schema version 2")
        if profile.schema_version == 3 and profile.function_bindings:
            failures.append(f"{label} adds bindings to schema version 3")
        if (not profile.roles or len(profile.routing_slots) < 15 or
                not profile.table_rules or profile.default_table_id >= 28):
            failures.append(f"{label} has an incomplete version 2 shape")
        roles = [role.role_id for role in profile.roles]
        role_ids = set(roles)
        if any(role_id < 1 or role_id > 32 for role_id in roles) or len(role_ids) != len(roles):
            failures.append(f"{label} has an invalid role")
        if profile.schema_version == 4 and (len(roles) != 21 or 2 in role_ids):
            failures.append(f"{label} has an invalid version 4 role inventory")

        routing_slots = [slot.slot_id for slot in profile.routing_slots]
        routing_inputs = [slot.input_token for slot in profile.routing_slots]
        if (any(slot < 1 or slot > 60 for slot in routing_slots) or
                any(token < 1 or token > 60 for token in routing_inputs) or
                len(set(routing_slots)) != len(routing_slots) or
                len(set(routing_inputs)) != len(routing_inputs)):
            failures.append(f"{label} has an invalid routing slot")
        elif not _V2_REQUIRED_ROUTING_SLOTS.issubset(routing_slots):
            failures.append(f"{label} is missing a required routing slot")

        routed_slot_ids = set(routing_slots)
        for role in profile.roles:
            if (not role.HasField("condition") or
                    invalid_condition(role.condition, role_ids, routed_slot_ids, role.role_id - 1) or
                    (profile.schema_version == 4 and 66 in (list(role.condition.all_tokens) + list(role.condition.any_tokens) + list(role.condition.none_tokens)))):
                failures.append(f"{label} has an invalid role condition")
                break

        priorities: set[int] = set()
        for rule in profile.table_rules:
            if (rule.priority == 0 or rule.priority > 255 or rule.table_id >= 28 or
                    rule.priority in priorities):
                failures.append(f"{label} has an invalid table priority")
                break
            priorities.add(rule.priority)
            if (not rule.HasField("condition") or
                    invalid_condition(rule.condition, role_ids, routed_slot_ids, 32, profile.schema_version == 4) or
                    (profile.schema_version == 4 and 66 in (list(rule.condition.all_tokens) + list(rule.condition.any_tokens) + list(rule.condition.none_tokens)))):
                failures.append(f"{label} has an invalid table-rule condition")
                break
        if profile.schema_version in (3, 4):
            if not has_output_program or not profile.output_program.enabled:
                failures.append(f"{label} has an incomplete version 3 output program")
            elif len(profile.output_program.effects) != 12:
                failures.append(
                    f"{label}.output_program.effects must contain 12 entries, "
                    f"found {len(profile.output_program.effects)}"
                )
            if len(profile.routing_slots) != 32:
                failures.append(
                    f"{label}.routing_slots must contain 32 entries for schema version {profile.schema_version}, "
                    f"found {len(profile.routing_slots)}"
                )
            elif set(routing_slots) != _V3_REQUIRED_ROUTING_SLOTS:
                failures.append(f"{label} is missing an output input slot")
            effect_keys: set[int] = set()
            for effect in profile.output_program.effects:
                key = effect_key(effect)
                if key is None or key in effect_keys or invalid_effect_shape(effect, key):
                    failures.append(f"{label} has an invalid output effect")
                    break
                effect_keys.add(key)
                token = effect.gate_token
                if ((token == 0 and effect.gate_inverted) or
                        (token != 0 and not ((1 <= token <= 60 and token in routed_slot_ids) or
                                             (65 <= token <= 96 and token - 64 in role_ids)))):
                    failures.append(f"{label} has an invalid output gate")
                    break
            if len(effect_keys) != 12:
                failures.append(f"{label} is missing an output phase")
        if profile.schema_version == 4:
            if len(profile.function_bindings) != 1:
                failures.append(f"{label} must contain exactly one X1 function binding")
            else:
                binding = profile.function_bindings[0]
                if (binding.function_class != config_pb2.ULTIMATE_CONTROLLER_FUNCTION_STICK_TABLE_MODIFIER or
                        binding.function_instance != config_pb2.ULTIMATE_CONTROLLER_FUNCTION_INSTANCE_X1 or
                        binding.base_table_id >= 28 or binding.mode_table_id >= 28 or
                        binding.base_priority == 0 or binding.mode_priority == 0 or
                        binding.base_priority == binding.mode_priority or
                        binding.base_priority in priorities or binding.mode_priority in priorities or
                        not binding.HasField("activation_condition") or
                        (not binding.activation_condition.all_tokens and not binding.activation_condition.any_tokens) or
                        invalid_condition(binding.activation_condition, role_ids, routed_slot_ids, 0,
                                          False, True)):
                    failures.append(f"{label} has an invalid X1 function binding")
    return failures


def verify_required_bindings(config_message: Any, config_pb2: ModuleType) -> list[str]:
    failures: list[str] = []
    ultimate_modes = [
        mode for mode in config_message.game_mode_configs if mode.mode_id == config_pb2.MODE_ULTIMATE
    ]
    for mode_index, mode in enumerate(config_message.game_mode_configs, start=1):
        if mode.mode_id != config_pb2.MODE_ULTIMATE and mode.ultimate_profile_config != 0:
            failures.append(
                f"game_mode_configs[{mode_index}].ultimate_profile_config is set for a non-Ultimate mode"
            )

    profiles = list(config_message.ultimate_profiles)
    if profiles:
        if len(ultimate_modes) != 3:
            failures.append(
                "Stage-A artifact with runtime profiles requires exactly three MODE_ULTIMATE "
                "rows (legacy, profile 1, profile 2)"
            )
        elif sorted(mode.ultimate_profile_config for mode in ultimate_modes) != [0, 1, 2]:
            failures.append(
                "Stage-A artifact requires explicit MODE_ULTIMATE profile references [0, 1, 2]"
            )
    elif len(ultimate_modes) != 1:
        failures.append(
            f"legacy artifact requires exactly one MODE_ULTIMATE game mode config, found {len(ultimate_modes)}"
        )

    for mode_index, ultimate_mode in enumerate(ultimate_modes, start=1):
        label = f"MODE_ULTIMATE[{mode_index}]"
        failures.extend(verify_ultimate_mode_bindings(ultimate_mode, config_pb2, label))
        if ultimate_mode.ultimate_profile_config > len(config_message.ultimate_profiles):
            failures.append(
                f"{label}.ultimate_profile_config={ultimate_mode.ultimate_profile_config} "
                f"exceeds ultimate_profiles count {len(config_message.ultimate_profiles)}"
            )
    failures.extend(verify_ultimate_profiles(config_message, config_pb2))
    return failures


def decode_error_payload(payload: bytes) -> str:
    if not payload:
        return "device returned CMD_ERROR with empty payload"
    message = payload.decode("utf-8", errors="replace")
    return message.rstrip("\x00")


def request_get_config(serial_port: PosixSerialPort) -> bytes:
    response_command, response_payload = serial_port.transact(CMD_GET_CONFIG, b"")
    if response_command == CMD_ERROR:
        raise ToolError(f"device error during GET_CONFIG: {decode_error_payload(response_payload)}")
    if response_command != CMD_SET_CONFIG:
        raise ToolError(
            "unexpected response command for GET_CONFIG: "
            f"expected={CMD_SET_CONFIG}, actual={response_command}"
        )
    return response_payload


def request_set_config(serial_port: PosixSerialPort, payload: bytes) -> None:
    response_command, response_payload = serial_port.transact(CMD_SET_CONFIG, payload)
    if response_command == CMD_ERROR:
        raise ToolError(f"device error during SET_CONFIG: {decode_error_payload(response_payload)}")
    if response_command != CMD_SUCCESS:
        raise ToolError(
            "unexpected response command for SET_CONFIG: "
            f"expected={CMD_SUCCESS}, actual={response_command}"
        )


def write_backup_json(
    backup_path: Path,
    config_message: Any,
    raw_payload: bytes,
    json_format: ModuleType,
) -> None:
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_json = {
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "rawConfigPayloadBase64": base64.b64encode(raw_payload).decode("ascii"),
        "config": json_format.MessageToDict(
            config_message,
            preserving_proto_field_name=False,
            use_integers_for_enums=False,
        ),
    }
    backup_path.write_text(json.dumps(backup_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_status(state: RunState) -> None:
    status = "PASS" if not state.failures else "FAIL"
    print(f"status={status}")
    print(f"mode={state.mode}")
    print(f"artifact_validated={'true' if state.artifact_validated else 'false'}")
    print(f"live_device_access={'true' if state.live_device_access else 'false'}")
    print(
        "active_device_profile_updated="
        f"{'true' if state.active_device_profile_updated else 'false'}"
    )
    print(f"readback_verified={'true' if state.readback_verified else 'false'}")
    print("firmware_flashing=false")
    if state.blocker:
        print(f"blocker={BLOCKER_CODE}")
    for failure in state.failures:
        print(f"failure={failure}")


def main() -> int:
    args = parse_args()
    mode = mode_from_args(args)
    state = RunState(mode=mode)

    try:
        require_cli_guards(args, mode)
        config_pb2, json_format, proto_path = load_runtime_proto_modules(REPO_ROOT)
        print(f"proto_source={proto_path}")
        print("protocol_source_confirmed=true")

        artifact_message = None
        artifact_payload = b""
        if mode in {"dry_run", "write"}:
            artifact_path = Path(args.artifact).resolve()
            artifact_data = load_artifact_json(artifact_path)
            artifact_message, artifact_payload = encode_artifact_payload(
                artifact_data, config_pb2, json_format
            )
            artifact_failures = verify_required_bindings(artifact_message, config_pb2)
            if artifact_failures:
                raise ToolError(
                    "artifact validation failed: " + "; ".join(artifact_failures)
                )
            state.artifact_validated = True
            print(f"artifact_path={artifact_path}")
            print(f"artifact_payload_bytes={len(artifact_payload)}")

        if mode == "dry_run":
            print("dry_run_serial_opened=false")
            print_status(state)
            return 0

        serial_port = PosixSerialPort(args.port, args.baudrate, args.timeout_sec)
        serial_port.open()
        state.live_device_access = True

        try:
            if mode == "read":
                current_payload = request_get_config(serial_port)
                current_config = decode_config_payload(current_payload, config_pb2)
                print(f"read_payload_bytes={len(current_payload)}")
                if args.backup_out:
                    backup_path = Path(args.backup_out).resolve()
                    write_backup_json(backup_path, current_config, current_payload, json_format)
                    print(f"backup_written={backup_path}")
                else:
                    print("backup_written=false")

                print_status(state)
                return 0

            # mode == "write"
            prewrite_payload = request_get_config(serial_port)
            prewrite_config = decode_config_payload(prewrite_payload, config_pb2)
            print(f"prewrite_payload_bytes={len(prewrite_payload)}")
            if args.backup_out:
                backup_path = Path(args.backup_out).resolve()
                write_backup_json(backup_path, prewrite_config, prewrite_payload, json_format)
                print(f"backup_written={backup_path}")
            else:
                print("backup_written=false")

            request_set_config(serial_port, artifact_payload)
            readback_payload = request_get_config(serial_port)
            readback_config = decode_config_payload(readback_payload, config_pb2)
            readback_failures = verify_required_bindings(readback_config, config_pb2)
            if readback_failures:
                raise ToolError("readback verification failed: " + "; ".join(readback_failures))
            state.readback_verified = True
            state.active_device_profile_updated = True
            print(f"readback_payload_bytes={len(readback_payload)}")
            print_status(state)
            return 0
        finally:
            serial_port.close()

    except ToolError as exc:
        state.failures.append(str(exc))
        state.blocker = state.blocker or exc.blocker
        print_status(state)
        return 1
    except Exception as exc:  # pragma: no cover - hard safety net.
        state.failures.append(f"unexpected error: {exc}")
        print_status(state)
        return 1


if __name__ == "__main__":
    sys.exit(main())
