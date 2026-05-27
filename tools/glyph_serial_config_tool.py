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
from typing import Any


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

    def transact(self, command_id: int, payload: bytes) -> tuple[int, bytes]:
        raw_packet = bytes([command_id]) + payload
        encoded = cobs_encode(raw_packet)
        self.write_all(encoded)
        response_packet = self.read_packet()
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
    preferred_paths = [
        repo_root / ".pio" / "libdeps" / "glyph_mk6" / "HayBox-proto" / "config.proto",
    ]
    for candidate in preferred_paths:
        if candidate.exists():
            return candidate

    fallback_matches = sorted(repo_root.glob(".pio/libdeps/**/config.proto"))
    haybox_matches = [path for path in fallback_matches if "HayBox-proto" in str(path)]
    if haybox_matches:
        return haybox_matches[0]
    raise ToolError(
        "could not locate source-traceable config.proto under .pio/libdeps/*/HayBox-proto/",
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


def verify_required_bindings(config_message: Any, config_pb2: ModuleType) -> list[str]:
    failures: list[str] = []
    ultimate_modes = [
        mode for mode in config_message.game_mode_configs if mode.mode_id == config_pb2.MODE_ULTIMATE
    ]
    if len(ultimate_modes) != 1:
        failures.append(
            "expected exactly one MODE_ULTIMATE game mode config, "
            f"found {len(ultimate_modes)}"
        )
        return failures

    ultimate_mode = ultimate_modes[0]
    remaps = list(ultimate_mode.button_remapping)

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

    if len(rf3_to_lt1) != 1:
        failures.append(
            "expected exactly one BTN_RF3 -> BTN_LT1 mapping, "
            f"found {len(rf3_to_lt1)}"
        )
    if len(rf4_to_lt2) != 1:
        failures.append(
            "expected exactly one BTN_RF4 -> BTN_LT2 mapping, "
            f"found {len(rf4_to_lt2)}"
        )
    if len(lt3_entries) != 1:
        failures.append(
            "expected exactly one BTN_LT3 physical remap entry, "
            f"found {len(lt3_entries)}"
        )
    if len(lt3_to_lt3) != 1:
        failures.append(
            "expected exactly one BTN_LT3 -> BTN_LT3 mapping, "
            f"found {len(lt3_to_lt3)}"
        )
    if lt3_to_lf4:
        failures.append("unexpected BTN_LT3 -> BTN_LF4 mapping present")

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
