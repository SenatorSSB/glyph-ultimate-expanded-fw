#!/usr/bin/env python3
"""Fail-closed host operator for GP-CONFIG-010 13-mode recovery acceptance.

Uses only the existing ConfiguratorBackend commands. It never flashes firmware.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

try:
    from glyph_serial_config_tool import (
        CMD_ERROR,
        CMD_GET_CONFIG,
        CMD_SET_CONFIG,
        CMD_SUCCESS,
        PosixSerialPort,
        ToolError,
        decode_error_payload,
        load_runtime_proto_modules,
    )
except ModuleNotFoundError:  # Supports `python -m unittest` from the repository root.
    from tools.glyph_serial_config_tool import (
        CMD_ERROR,
        CMD_GET_CONFIG,
        CMD_SET_CONFIG,
        CMD_SUCCESS,
        PosixSerialPort,
        ToolError,
        decode_error_payload,
        load_runtime_proto_modules,
    )


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_VERSION = "GP_CONFIG_010_HW_RECOVERY_V1"
CANDIDATE_SHA = "f4771e17430fd1ea3f1e3e5339a83dfe648290a3"
CANDIDATE_ARTIFACT_SHA = "9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a"
ROLLBACK_SHA = "f657715b26d26587a931074ce7dd12c698785290"
ROLLBACK_ARTIFACT_SHA = "00dc75b65a080830131c3c260558d4daeff45bb528e43d196b8ad94fcd06f451"
CMD_GET_DEVICE_INFO = 1
CMD_SET_DEVICE_INFO = 2

STAGES = (
    "prewrite_read_attempted",
    "prewrite_read_completed",
    "prewrite_baseline_matched",
    "write_attempted",
    "full_host_write_completed",
    "awaiting_response",
    "response_received",
    "response_decoded",
    "followup_read_attempted",
    "followup_read_completed",
)

# Source names and positions come from glyph_mk6 matrix_definition.hpp,
# button_positions.hpp, and the repository physical/logical layout map.
BINDINGS = (
    ("BTN_LF6", "Far-right isolated button near center", 2, 3, 55, 25),
    ("BTN_LF7", "Far-upper-right button", 1, 3, 46, 19),
    ("BTN_LF8", "Upper-right button", 1, 2, 35, 17),
    ("BTN_RF9", "Bottom-left button in the center/right cluster", 0, 8, 101, 34),
    ("BTN_RF10", "Left-lower button in the center cluster", 2, 4, 64, 30),
    ("BTN_RF11", "Center-left middle button", 2, 5, 74, 25),
    ("BTN_RF12", "Center-right middle button", 2, 6, 84, 25),
    ("BTN_RF13", "Left-middle button in the upper center cluster", 1, 4, 64, 20),
    ("BTN_RF14", "Upper-left button in the center cluster", 1, 5, 74, 15),
    ("BTN_RF15", "Upper-right button in the center cluster", 1, 6, 84, 15),
    ("BTN_RF16", "Lower-center button", 0, 7, 72, 35),
    ("BTN_LT3", "Right button in the left-thumb diamond", 3, 3, 46, 46),
    ("BTN_LT4", "Upper button in the left-thumb diamond", 3, 1, 38, 40),
)


class TransactionStop(RuntimeError):
    """Expected fail-closed transaction stop whose evidence must be preserved."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_bytes(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ToolError(f"required regular non-symlink file missing: {path}")
    return path.read_bytes()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ToolError(f"required regular non-symlink JSON file missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ToolError(f"invalid JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ToolError(f"JSON root must be an object: {path}")
    return value


def decode_config(payload: bytes, config_pb2: Any) -> Any:
    message = config_pb2.Config()
    try:
        message.ParseFromString(payload)
    except Exception as exc:
        raise ToolError(f"payload is not a valid Config protobuf: {exc}") from exc
    return message


def deterministic(message: Any) -> bytes:
    return message.SerializeToString(deterministic=True)


def request_config(port: PosixSerialPort) -> bytes:
    command, payload = port.transact(CMD_GET_CONFIG, b"")
    if command == CMD_ERROR:
        raise ToolError(f"GET_CONFIG error: {decode_error_payload(payload)}")
    if command != CMD_SET_CONFIG:
        raise ToolError(f"GET_CONFIG unexpected response command: {command}")
    return payload


def request_device_info(port: PosixSerialPort, config_pb2: Any) -> dict[str, Any]:
    command, payload = port.transact(CMD_GET_DEVICE_INFO, b"")
    if command == CMD_ERROR:
        raise ToolError(f"GET_DEVICE_INFO error: {decode_error_payload(payload)}")
    if command != CMD_SET_DEVICE_INFO:
        raise ToolError(f"GET_DEVICE_INFO unexpected response command: {command}")
    message = config_pb2.DeviceInfo()
    message.ParseFromString(payload)
    return {
        "firmware_name": message.firmware_name,
        "firmware_version": message.firmware_version,
        "device_name": message.device_name,
        "raw_payload_length": len(payload),
        "raw_payload_sha256": sha256(payload),
    }


def open_port(path: str, timeout: float) -> PosixSerialPort:
    port = PosixSerialPort(path, 115200, timeout)
    port.open()
    return port


def capture(args: argparse.Namespace, config_pb2: Any, json_format: Any) -> None:
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    port = open_port(args.port, args.timeout_sec)
    try:
        device_info = request_device_info(port, config_pb2)
        payload = request_config(port)
    finally:
        port.close()
    message = decode_config(payload, config_pb2)
    reencoded = deterministic(message)
    if reencoded != payload:
        raise ToolError(
            "captured protobuf did not deterministically re-encode byte-for-byte; stop before mutation"
        )
    config_dict = json_format.MessageToDict(
        message, preserving_proto_field_name=True, use_integers_for_enums=False
    )
    (output / "owner-original-config.bin").write_bytes(payload)
    (output / "owner-original-config.base64").write_text(
        base64.b64encode(payload).decode("ascii") + "\n", encoding="ascii"
    )
    dump_json(output / "owner-original-config.json", config_dict)
    identity = {
        "schema_name": "gp_config_010_recovery_capture",
        "schema_version": 1,
        "protocol_version": PROTOCOL_VERSION,
        "captured_at_utc": utc_now(),
        "selected_port": args.port,
        "device_info": device_info,
        "raw_config_payload_definition": "protobuf Config message bytes excluding command byte and COBS framing",
        "raw_config_payload_length": len(payload),
        "raw_config_payload_sha256": sha256(payload),
        "raw_config_payload_base64": base64.b64encode(payload).decode("ascii"),
        "deterministic_reencode_equal": True,
        "candidate_expected_after_test_flash": CANDIDATE_SHA,
        "candidate_artifact_sha256": CANDIDATE_ARTIFACT_SHA,
        "rollback_candidate": ROLLBACK_SHA,
        "rollback_artifact_sha256": ROLLBACK_ARTIFACT_SHA,
        "nonclaim": "GET_CONFIG reads persisted config.bin; this does not prove live-RAM identity.",
    }
    dump_json(output / "identity-status-snapshot.json", identity)
    dump_json(output / "operator-log.json", {"events": [{"at_utc": utc_now(), "event": "owner_original_config_captured_and_reencode_verified"}]})
    print(json.dumps(identity, indent=2, sort_keys=True))


def snapshot(args: argparse.Namespace, config_pb2: Any, json_format: Any) -> None:
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    port = open_port(args.port, args.timeout_sec)
    try:
        device_info = request_device_info(port, config_pb2)
        payload = request_config(port)
    finally:
        port.close()
    message = decode_config(payload, config_pb2)
    if deterministic(message) != payload:
        raise ToolError("current-state protobuf did not deterministically re-encode byte-for-byte")
    (output / "current-config.bin").write_bytes(payload)
    dump_json(
        output / "current-config.json",
        json_format.MessageToDict(
            message, preserving_proto_field_name=True, use_integers_for_enums=False
        ),
    )
    metadata = {
        "schema_name": "gp_config_010_recovery_current_state",
        "schema_version": 1,
        "protocol_version": PROTOCOL_VERSION,
        "captured_at_utc": utc_now(),
        "label": args.label,
        "selected_port": args.port,
        "device_info": device_info,
        "raw_config_payload_length": len(payload),
        "raw_config_payload_sha256": sha256(payload),
        "deterministic_reencode_equal": True,
    }
    dump_json(output / "current-state-metadata.json", metadata)
    print(json.dumps(metadata, indent=2, sort_keys=True))


def validate_binding_set(config: Any, config_pb2: Any) -> list[dict[str, Any]]:
    matrix_path = ROOT / "config/glyph/glyph_mk6/include/matrix_definition.hpp"
    positions_path = ROOT / "config/glyph/glyph_mk6/include/button_positions.hpp"
    selection_path = ROOT / "src/core/mode_selection.cpp"
    matrix_text = matrix_path.read_text(encoding="utf-8")
    positions_text = re.sub(r"\s+", "", positions_path.read_text(encoding="utf-8"))
    selection_text = selection_path.read_text(encoding="utf-8")
    matrix_match = re.search(
        r"const Button matrix\[num_rows\]\[num_cols\] = \{(.*?)\n\};",
        matrix_text,
        flags=re.DOTALL,
    )
    if matrix_match is None:
        raise ToolError("could not parse authoritative glyph_mk6 matrix")
    matrix_rows = [
        [token.strip() for token in row.split(",")]
        for row in re.findall(r"\{([^{}]+)\}", matrix_match.group(1))
    ]
    if len(matrix_rows) != 4 or any(len(row) != 11 for row in matrix_rows):
        raise ToolError("authoritative glyph_mk6 matrix shape changed")
    debug_chord = {"BTN_LT1", "BTN_LT2", "BTN_MB1", "BTN_MB2"}
    if "inputs.lt1 && inputs.lt2 && inputs.mb1 && inputs.mb2" not in selection_text:
        raise ToolError("manual debug chord source changed; binding exclusions require review")
    backend_buttons = {
        int(button)
        for backend in config.communication_backend_configs
        for button in backend.activation_binding
    }
    rows: list[dict[str, Any]] = []
    masks: list[int] = []
    for index, (name, location, row, col, x, y) in enumerate(BINDINGS):
        if name.startswith("BTN_MB") or name in debug_chord:
            raise ToolError(f"binding {name} is a forbidden menu/update/debug control")
        if matrix_rows[row][col] != name:
            raise ToolError(f"binding {name} no longer matches authoritative matrix row={row}, col={col}")
        if f"{{{name},{x},{y}," not in positions_text:
            raise ToolError(f"binding {name} no longer matches authoritative display position ({x},{y})")
        button = int(getattr(config_pb2, name))
        if button <= 0 or button > 64:
            raise ToolError(f"binding {name} is not representable by the production 64-bit mask")
        if button in backend_buttons:
            raise ToolError(f"binding {name} conflicts with a captured communication-backend activation binding")
        mask = 1 << (button - 1)
        masks.append(mask)
        rows.append(
            {
                "profile": f"Ult{index + 1:02d}",
                "config_index": index,
                "button_id": name,
                "physical_location": location,
                "matrix_row": row,
                "matrix_col": col,
                "miniscreen_x": x,
                "miniscreen_y": y,
                "activation_mask_hex": f"0x{mask:016x}",
                "former_overflow_boundary": index >= 10,
            }
        )
    if len(set(masks)) != 13 or any(mask == 0 for mask in masks):
        raise ToolError("bindings are empty or not pairwise unique")
    for left_index, left in enumerate(masks):
        for right_index, right in enumerate(masks):
            if left_index != right_index and (left & right) in {left, right}:
                raise ToolError("binding set is not a pairwise antichain")
    return rows


def make_plan(args: argparse.Namespace, config_pb2: Any, json_format: Any) -> None:
    original_payload = load_bytes(args.original_payload.resolve())
    original = decode_config(original_payload, config_pb2)
    if deterministic(original) != original_payload:
        raise ToolError("owner-original payload no longer re-encodes byte-for-byte")
    ultimate = [mode for mode in original.game_mode_configs if mode.mode_id == config_pb2.MODE_ULTIMATE]
    if len(ultimate) != 1:
        raise ToolError(f"expected exactly one unambiguous owner Ultimate entry, found {len(ultimate)}")
    source = config_pb2.GameModeConfig()
    source.CopyFrom(ultimate[0])
    rows = validate_binding_set(original, config_pb2)
    temporary = config_pb2.Config()
    temporary.CopyFrom(original)
    del temporary.game_mode_configs[:]
    for row in rows:
        clone = temporary.game_mode_configs.add()
        clone.CopyFrom(source)
        clone.name = row["profile"]
        del clone.activation_binding[:]
        clone.activation_binding.append(getattr(config_pb2, row["button_id"]))
        del clone.applicable_backends[:]
        clone.applicable_backends.append(config_pb2.COMMS_BACKEND_GAMECUBE)

    if len(temporary.game_mode_configs) != 13:
        raise ToolError("temporary config does not have exactly 13 game mode configs")
    # Prove unrelated top-level fields by restoring the original repeated field.
    top_level_probe = config_pb2.Config()
    top_level_probe.CopyFrom(temporary)
    del top_level_probe.game_mode_configs[:]
    for mode in original.game_mode_configs:
        top_level_probe.game_mode_configs.add().CopyFrom(mode)
    if top_level_probe != original:
        raise ToolError("temporary config contains unrelated top-level field drift")
    for index, clone in enumerate(temporary.game_mode_configs):
        probe = config_pb2.GameModeConfig()
        probe.CopyFrom(clone)
        probe.name = source.name
        del probe.activation_binding[:]
        probe.activation_binding.extend(source.activation_binding)
        del probe.applicable_backends[:]
        probe.applicable_backends.extend(source.applicable_backends)
        if probe != source:
            raise ToolError(f"clone {index} differs outside permitted fields")

    payload = deterministic(temporary)
    if deterministic(decode_config(payload, config_pb2)) != payload:
        raise ToolError("temporary payload does not deterministically round-trip")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "temporary-13-ultimate-config.bin").write_bytes(payload)
    dump_json(
        output / "temporary-13-ultimate-config.json",
        json_format.MessageToDict(
            temporary, preserving_proto_field_name=True, use_integers_for_enums=False
        ),
    )
    plan = {
        "schema_name": "gp_config_010_temporary_13_ultimate_plan",
        "schema_version": 1,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at_utc": utc_now(),
        "owner_original_payload_length": len(original_payload),
        "owner_original_payload_sha256": sha256(original_payload),
        "temporary_payload_length": len(payload),
        "temporary_payload_sha256": sha256(payload),
        "game_mode_configs_count": 13,
        "profiles": rows,
        "allowed_differences": [
            "game_mode_configs replaced by 13 clones of the sole captured MODE_ULTIMATE entry",
            "clone name set to Ult01..Ult13",
            "clone activation_binding set to the matching singleton",
            "clone applicable_backends set to COMMS_BACKEND_GAMECUBE only",
        ],
        "proofs": {
            "indices_0_through_12": True,
            "all_mode_ultimate": True,
            "names_exact": True,
            "all_gamecube_applicable": True,
            "bindings_nonempty_unique": True,
            "bindings_pairwise_antichain": True,
            "clone_fields_equal_outside_allowed": True,
            "unrelated_top_level_fields_equal": True,
            "deterministic_roundtrip_equal": True,
        },
    }
    dump_json(output / "temporary-13-ultimate-plan.json", plan)
    lines = [
        "# GP-CONFIG-010 temporary 13-Ultimate plan",
        "",
        f"Owner-original payload: {len(original_payload)} bytes, SHA-256 `{sha256(original_payload)}`",
        f"Temporary payload: {len(payload)} bytes, SHA-256 `{sha256(payload)}`",
        "",
        "| Profile | Config index | Button ID | Physical location |",
        "| --- | ---: | --- | --- |",
    ]
    lines.extend(
        f"| {row['profile']} | {row['config_index']} | {row['button_id'].removeprefix('BTN_')} | {row['physical_location']} |"
        for row in rows
    )
    lines.extend(["", "Only name, activation binding, backend applicability, and the required 13-entry replacement differ.", ""])
    (output / "temporary-13-ultimate-summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(plan, indent=2, sort_keys=True))


def transaction(args: argparse.Namespace, config_pb2: Any) -> None:
    baseline = load_bytes(args.expected_current.resolve())
    intended = load_bytes(args.intended_payload.resolve())
    capture_metadata = load_json(args.capture_metadata.resolve())
    current_state_metadata = load_json(args.current_state_metadata.resolve())
    plan = load_json(args.plan.resolve())
    decode_config(baseline, config_pb2)
    decode_config(intended, config_pb2)
    original_hash = capture_metadata.get("raw_config_payload_sha256")
    if (
        capture_metadata.get("schema_name") != "gp_config_010_recovery_capture"
        or capture_metadata.get("protocol_version") != PROTOCOL_VERSION
        or not isinstance(original_hash, str)
    ):
        raise ToolError("capture metadata identity is invalid")
    if plan.get("schema_name") != "gp_config_010_temporary_13_ultimate_plan" or plan.get("protocol_version") != PROTOCOL_VERSION:
        raise ToolError("temporary plan identity is invalid")
    temporary_hash = plan.get("temporary_payload_sha256")
    if plan.get("owner_original_payload_sha256") != original_hash or not isinstance(temporary_hash, str):
        raise ToolError("capture and temporary plan are not bound to the same owner-original payload")
    if (
        current_state_metadata.get("protocol_version") != PROTOCOL_VERSION
        or current_state_metadata.get("raw_config_payload_sha256") != sha256(baseline)
        or current_state_metadata.get("schema_name")
        not in {"gp_config_010_recovery_capture", "gp_config_010_recovery_current_state"}
    ):
        raise ToolError("expected-current file is not bound to the supplied fresh state metadata")
    if args.operation == "write":
        if (
            current_state_metadata.get("schema_name") != "gp_config_010_recovery_capture"
            or sha256(baseline) != original_hash
            or sha256(intended) != temporary_hash
        ):
            raise ToolError("write files do not match the captured original and validated temporary plan")
    elif args.operation == "restore":
        if (
            current_state_metadata.get("schema_name") != "gp_config_010_recovery_current_state"
            or sha256(intended) != original_hash
        ):
            raise ToolError("restore is not bound to a fresh current-state capture and exact owner original")
    else:
        raise ToolError(f"unsupported transaction operation: {args.operation}")
    result: dict[str, Any] = {
        "schema_name": "gp_config_010_recovery_transaction",
        "schema_version": 2,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at_utc": utc_now(),
        "operation": args.operation,
        "selected_port": args.port,
        "capture_metadata_path": str(args.capture_metadata.resolve()),
        "current_state_metadata_path": str(args.current_state_metadata.resolve()),
        "plan_path": str(args.plan.resolve()),
        "expected_current_sha256": sha256(baseline),
        "intended_payload_sha256": sha256(intended),
        "transaction_stage": "not_started",
        "transaction_stages": [],
        **{stage: False for stage in STAGES},
        "sent": False,
        "partial_write_ambiguous": False,
        "device_state_ambiguous": False,
        "response_command": None,
        "readback_sha256": None,
        "exact_readback_match": False,
        "outcome": "NOT_STARTED",
        "error": None,
    }

    def stage(name: str) -> None:
        if name not in STAGES or result[name]:
            raise ToolError(f"invalid or duplicate transaction stage: {name}")
        result[name] = True
        result["transaction_stage"] = name
        result["transaction_stages"].append({"stage": name, "at_utc": utc_now()})
        if name == "write_attempted":
            result["partial_write_ambiguous"] = True
        if name == "full_host_write_completed":
            result["sent"] = True
            result["partial_write_ambiguous"] = False

    port = open_port(args.port, args.timeout_sec)
    try:
        device_info = request_device_info(port, config_pb2)
        result["device_info"] = device_info
        captured_device = capture_metadata.get("device_info")
        if not isinstance(captured_device, dict) or device_info.get("device_name") != captured_device.get("device_name"):
            result["outcome"] = "DEVICE_IDENTITY_MISMATCH_STOP"
            result["error"] = "current device name differs from the owner-original capture"
            raise TransactionStop(result["outcome"])
        if device_info.get("firmware_version") != CANDIDATE_SHA[:7]:
            result["outcome"] = "DEVICE_FIRMWARE_IDENTITY_MISMATCH_STOP"
            result["error"] = "mutation requires the GP-CONFIG-010 candidate short firmware identity"
            raise TransactionStop(result["outcome"])
        stage("prewrite_read_attempted")
        current = request_config(port)
        stage("prewrite_read_completed")
        if current != baseline:
            result["outcome"] = "BASELINE_DRIFT_STOP"
            result["error"] = "current persisted payload differs from expected baseline"
            raise TransactionStop(result["outcome"])
        stage("prewrite_baseline_matched")
        command, response = port.transact(CMD_SET_CONFIG, intended, stage_callback=stage)
        result["response_command"] = command
        result["response_payload_sha256"] = sha256(response)
        stage("response_decoded")
        if command != CMD_SUCCESS:
            result["outcome"] = "UNEXPECTED_RESPONSE_STOP"
            result["error"] = decode_error_payload(response) if command == CMD_ERROR else f"unexpected response {command}"
            raise TransactionStop(result["outcome"])
        stage("followup_read_attempted")
        readback = request_config(port)
        stage("followup_read_completed")
        result["readback_sha256"] = sha256(readback)
        result["exact_readback_match"] = readback == intended
        if readback != intended:
            result["outcome"] = "READBACK_MISMATCH_STOP"
            result["error"] = "follow-up GET_CONFIG differs from intended payload"
            raise TransactionStop(result["outcome"])
        result["outcome"] = "SUCCESS_RESPONSE_AND_EXACT_READBACK"
    except TransactionStop:
        pass
    except Exception as exc:
        result["outcome"] = "TRANSPORT_OR_FOLLOWUP_ERROR_STOP"
        result["error"] = str(exc)
    finally:
        port.close()
        result["device_state_ambiguous"] = bool(
            result["write_attempted"] and not result["exact_readback_match"]
        )
        dump_json(args.result_out.resolve(), result)
        print(json.dumps(result, indent=2, sort_keys=True))
    if result["outcome"] != "SUCCESS_RESPONSE_AND_EXACT_READBACK":
        raise ToolError(result["outcome"])


def verify(args: argparse.Namespace, config_pb2: Any) -> None:
    expected = load_bytes(args.expected_payload.resolve())
    decode_config(expected, config_pb2)
    port = open_port(args.port, args.timeout_sec)
    try:
        info = request_device_info(port, config_pb2)
        observed = request_config(port)
    finally:
        port.close()
    result = {
        "schema_name": "gp_config_010_recovery_readback",
        "schema_version": 1,
        "protocol_version": PROTOCOL_VERSION,
        "observed_at_utc": utc_now(),
        "label": args.label,
        "selected_port": args.port,
        "device_info": info,
        "expected_length": len(expected),
        "expected_sha256": sha256(expected),
        "observed_length": len(observed),
        "observed_sha256": sha256(observed),
        "exact_match": observed == expected,
    }
    dump_json(args.result_out.resolve(), result)
    print(json.dumps(result, indent=2, sort_keys=True))
    if observed != expected:
        raise ToolError("readback mismatch")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    capture_parser = sub.add_parser("capture")
    capture_parser.add_argument("--port", required=True)
    capture_parser.add_argument("--output-dir", type=Path, required=True)
    capture_parser.add_argument("--timeout-sec", type=float, default=5.0)
    snapshot_parser = sub.add_parser("snapshot")
    snapshot_parser.add_argument("--port", required=True)
    snapshot_parser.add_argument("--output-dir", type=Path, required=True)
    snapshot_parser.add_argument("--label", required=True)
    snapshot_parser.add_argument("--timeout-sec", type=float, default=5.0)
    plan_parser = sub.add_parser("plan")
    plan_parser.add_argument("--original-payload", type=Path, required=True)
    plan_parser.add_argument("--output-dir", type=Path, required=True)
    for name in ("write", "restore"):
        tx = sub.add_parser(name)
        tx.add_argument("--port", required=True)
        tx.add_argument("--expected-current", type=Path, required=True)
        tx.add_argument("--intended-payload", type=Path, required=True)
        tx.add_argument("--capture-metadata", type=Path, required=True)
        tx.add_argument("--current-state-metadata", type=Path, required=True)
        tx.add_argument("--plan", type=Path, required=True)
        tx.add_argument("--result-out", type=Path, required=True)
        tx.add_argument("--timeout-sec", type=float, default=5.0)
        tx.set_defaults(operation=name)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--port", required=True)
    verify_parser.add_argument("--expected-payload", type=Path, required=True)
    verify_parser.add_argument("--result-out", type=Path, required=True)
    verify_parser.add_argument("--label", required=True)
    verify_parser.add_argument("--timeout-sec", type=float, default=5.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config_pb2, json_format, _ = load_runtime_proto_modules(ROOT)
        if args.command == "capture":
            capture(args, config_pb2, json_format)
        elif args.command == "snapshot":
            snapshot(args, config_pb2, json_format)
        elif args.command == "plan":
            make_plan(args, config_pb2, json_format)
        elif args.command in {"write", "restore"}:
            transaction(args, config_pb2)
        else:
            verify(args, config_pb2)
        return 0
    except (ToolError, OSError, ValueError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
