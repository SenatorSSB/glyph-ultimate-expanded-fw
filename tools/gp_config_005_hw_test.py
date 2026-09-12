#!/usr/bin/env python3
"""Bounded host operator utility for GP-CONFIG-005 physical acceptance.

This tool talks only to the existing Glyph/HayBox configurator backend.  It
does not flash firmware, add commands, manipulate storage, or create hardware
evidence.  Its JSON output is input for a human operator and the separate
Hardware Evidence Processor.
"""

from __future__ import annotations

import argparse
import base64
import copy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import glob
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Protocol

from glyph_serial_config_tool import (  # Existing custom-backend host transport.
    CMD_ERROR,
    CMD_GET_CONFIG,
    CMD_SET_CONFIG,
    CMD_SUCCESS,
    PosixSerialPort,
    ToolError,
    cobs_decode,
    cobs_encode,
    decode_error_payload,
    find_config_proto,
    load_runtime_proto_modules,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_VERSION = "GP_CONFIG_005_HW_V1"
CANDIDATE_BRANCH = "glyph/gp-config-005-transactional-setconfig"
CANDIDATE_GIT_SHA = "437f87e8086a50f0dfbd834176b80d245c1ed307"
CANDIDATE_BASE_SHA = "9550a1bf1309383e351f4f9e66663562fc9f13ac"
ARTIFACT_SHA256 = "650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44"
CONFIG_PROTO_SHA256 = "2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b"
CONFIG_PROTO_REVISION = "db4e2f6"
EXPECTED_DEVICE_FIRMWARE_VERSION = CANDIDATE_GIT_SHA[:7]
REJECTION_OBSERVATION_ACK_TOKEN = "ACK_REJECTIONS_OBSERVED_NO_ANOMALY"
ARTIFACT_RELATIVE_PATH = Path(
    "local_backups/hardware-artifacts"
) / CANDIDATE_GIT_SHA / ARTIFACT_SHA256 / "firmware.uf2"
PROTOCOL_RELATIVE_PATH = Path("docs/agent_framework/GP_CONFIG_005_HARDWARE_PROTOCOL.md")
CANDIDATE_HANDLER_PATH = "HAL/pico/src/comms/ConfiguratorBackend.cpp"

CMD_GET_DEVICE_INFO = 1
CMD_SET_DEVICE_INFO = 2

COMMAND_NAMES = {
    CMD_GET_DEVICE_INFO: "CMD_GET_DEVICE_INFO",
    CMD_SET_DEVICE_INFO: "CMD_SET_DEVICE_INFO",
    CMD_GET_CONFIG: "CMD_GET_CONFIG",
    CMD_SET_CONFIG: "CMD_SET_CONFIG",
    CMD_ERROR: "CMD_ERROR",
    CMD_SUCCESS: "CMD_SUCCESS",
}

CAPTURE_SCHEMA = "gp_config_005_host_config_capture"
CAPTURE_SCHEMA_VERSION = 1
RESULT_SCHEMA = "gp_config_005_operator_result"
RESULT_SCHEMA_VERSION = 1
PLAN_SCHEMA = "gp_config_005_payload_plan"
PLAN_SCHEMA_VERSION = 1

CAPTURE_NONCLAIMS = [
    "This is a host-side captured config from the existing CMD_GET_CONFIG path.",
    "This capture is not firmware source authority.",
    "This capture is not proof of live RAM byte identity; current CMD_GET_CONFIG reads config.bin.",
    "This capture is for valid-update derivation and rollback/reference only.",
]

RESULT_NONCLAIMS = [
    "This file is operator evidence input, not canonical Revision-2 hardware evidence.",
    "Mechanical responses do not replace required human controller/display observations.",
    "GET_CONFIG reads persisted config.bin and does not prove live RAM byte identity.",
    "A valid update plus reboot does not prove atomic persistence or power-loss safety.",
]


class Transport(Protocol):
    """Small interface shared by the serial transport and test doubles."""

    def transact(self, command_id: int, payload: bytes) -> tuple[int, bytes]: ...


@dataclass
class MutationCase:
    id: str
    target_validation_branch: str
    mutation: str
    changed_fields: list[dict[str, Any]]
    payload: bytes
    expected_response_command: str
    expected_error_text: str
    error_match: str = "exact"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def json_dump(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def run_git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ToolError(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout.strip()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_repository_identity(
    repo_root: Path = REPO_ROOT,
    *,
    require_artifact: bool = True,
) -> dict[str, Any]:
    """Fail closed unless protocol, candidate, schema, and artifact identity match."""

    protocol_path = repo_root / PROTOCOL_RELATIVE_PATH
    if not protocol_path.is_file() or protocol_path.is_symlink():
        raise ToolError(f"required regular protocol file missing: {protocol_path}")
    protocol_text = protocol_path.read_text(encoding="utf-8")
    required_protocol_fragments = [
        f"Protocol version: `{PROTOCOL_VERSION}`.",
        f"Candidate branch: `{CANDIDATE_BRANCH}`",
        f"Candidate Git SHA: `{CANDIDATE_GIT_SHA}`",
        f"Base `configurator` SHA: `{CANDIDATE_BASE_SHA}`",
        f"Artifact SHA-256: `{ARTIFACT_SHA256}`",
        f"Preserved locator: `{ARTIFACT_RELATIVE_PATH.as_posix()}`",
    ]
    missing = [fragment for fragment in required_protocol_fragments if fragment not in protocol_text]
    if missing:
        raise ToolError(
            "protocol identity mismatch; missing exact fragment(s): " + "; ".join(missing)
        )

    resolved_refs: dict[str, str] = {}
    for ref in (
        f"refs/heads/{CANDIDATE_BRANCH}",
        f"refs/remotes/origin/{CANDIDATE_BRANCH}",
    ):
        completed = subprocess.run(
            ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0:
            resolved_refs[ref] = completed.stdout.strip()
    if not resolved_refs:
        raise ToolError(
            "candidate branch identity unavailable; fetch the exact candidate ref before operating"
        )
    mismatches = {ref: sha for ref, sha in resolved_refs.items() if sha != CANDIDATE_GIT_SHA}
    if mismatches:
        raise ToolError(f"candidate branch identity mismatch: {mismatches}")

    run_git(repo_root, "cat-file", "-e", f"{CANDIDATE_GIT_SHA}^{{commit}}")
    merge_base = run_git(repo_root, "merge-base", CANDIDATE_GIT_SHA, "HEAD")
    if merge_base != CANDIDATE_BASE_SHA:
        raise ToolError(
            "candidate/protocol base mismatch: "
            f"expected={CANDIDATE_BASE_SHA}, actual_merge_base={merge_base}"
        )

    candidate_handler = run_git(
        repo_root, "show", f"{CANDIDATE_GIT_SHA}:{CANDIDATE_HANDLER_PATH}"
    )
    required_handler_fragments = [
        "static Config candidate;",
        "pb_decode(&istream, Config_fields, &candidate)",
        "if (!persistence.SaveConfig(candidate))",
        "_config = candidate;",
        "Default backend ID is %d but only %d backend configs are defined",
        "Default mode ID is %d for backend %d but only %d modes are defined",
        "keyboard_mode_id is set for game mode %d but mode_id is not MODE_KEYBOARD",
        "custom_mode_id is set for game mode %d but mode_id is not MODE_CUSTOM",
        "Keyboard mode ID %d is for game mode %d but only %d keyboard modes are defined",
        "Custom mode ID %d is for game mode config %d but only %d custom modes are defined",
    ]
    missing_handler = [
        fragment for fragment in required_handler_fragments if fragment not in candidate_handler
    ]
    if missing_handler:
        raise ToolError(
            "candidate handler no longer matches GP_CONFIG_005_HW_V1: "
            + "; ".join(missing_handler)
        )

    proto_path = find_config_proto(repo_root)
    proto_sha = file_sha256(proto_path)
    if proto_sha != CONFIG_PROTO_SHA256:
        raise ToolError(
            "config.proto identity mismatch: "
            f"expected={CONFIG_PROTO_SHA256}, actual={proto_sha}, path={proto_path}"
        )
    glyph_env_path = repo_root / "config/glyph/env.ini"
    if not glyph_env_path.is_file() or (
        f"https://github.com/GregTurbo/HayBox-proto#{CONFIG_PROTO_REVISION}"
        not in glyph_env_path.read_text(encoding="utf-8")
    ):
        raise ToolError(
            "Glyph HayBox-proto dependency identity mismatch in config/glyph/env.ini"
        )
    artifact_path = repo_root / ARTIFACT_RELATIVE_PATH
    artifact_status: dict[str, Any] = {
        "path": str(artifact_path),
        "required": require_artifact,
        "present": artifact_path.is_file(),
        "sha256": None,
        "matches_expected": None,
    }
    if require_artifact:
        if not artifact_path.is_file() or artifact_path.is_symlink():
            raise ToolError(f"preserved firmware artifact missing or not regular: {artifact_path}")
        actual_artifact_sha = file_sha256(artifact_path)
        artifact_status.update(
            {"sha256": actual_artifact_sha, "matches_expected": actual_artifact_sha == ARTIFACT_SHA256}
        )
        if actual_artifact_sha != ARTIFACT_SHA256:
            raise ToolError(
                "preserved artifact SHA-256 mismatch: "
                f"expected={ARTIFACT_SHA256}, actual={actual_artifact_sha}"
            )

    return {
        "protocol_version": PROTOCOL_VERSION,
        "protocol_path": str(protocol_path),
        "candidate_branch": CANDIDATE_BRANCH,
        "candidate_git_sha": CANDIDATE_GIT_SHA,
        "candidate_base_sha": CANDIDATE_BASE_SHA,
        "resolved_candidate_refs": resolved_refs,
        "config_proto_path": str(proto_path),
        "config_proto_sha256": proto_sha,
        "config_proto_revision": CONFIG_PROTO_REVISION,
        "artifact": artifact_status,
        "verified": True,
    }


def discover_serial_devices() -> list[dict[str, str]]:
    """List plausible serial paths without opening any device."""

    patterns = [
        "/dev/cu.usbmodem*",
        "/dev/tty.usbmodem*",
        "/dev/ttyACM*",
        "/dev/serial/by-id/*",
    ]
    paths: set[str] = set()
    for pattern in patterns:
        paths.update(glob.glob(pattern))
    return [
        {
            "path": path,
            "selection": "Pass this exact path with --port; the utility never auto-selects.",
        }
        for path in sorted(paths)
    ]


def command_name(command_id: int) -> str:
    return COMMAND_NAMES.get(command_id, f"UNKNOWN_COMMAND_{command_id}")


def response_record(command_id: int, payload: bytes) -> dict[str, Any]:
    return {
        "command_id": command_id,
        "command": command_name(command_id),
        "payload_length": len(payload),
        "payload_sha256": sha256_bytes(payload),
        "payload_hex": payload.hex(),
        "payload_base64": base64.b64encode(payload).decode("ascii"),
        "text": decode_error_payload(payload) if command_id == CMD_ERROR else None,
    }


def parse_framed_response(packet: bytes, expected_commands: Iterable[int]) -> dict[str, Any]:
    """Parse one complete PacketIO COBS response and classify its command."""

    decoded = cobs_decode(packet)
    if not decoded:
        raise ToolError("truncated response: decoded packet has no command byte")
    record = response_record(decoded[0], decoded[1:])
    expected = list(expected_commands)
    record["expected_commands"] = [command_name(item) for item in expected]
    record["unexpected_command"] = decoded[0] not in expected
    return record


def transport_is_open(transport: Transport) -> bool:
    if hasattr(transport, "is_open"):
        value = getattr(transport, "is_open")
        return bool(value() if callable(value) else value)
    if hasattr(transport, "fd"):
        return getattr(transport, "fd") is not None
    return True


def deterministic_payload(message: Any) -> bytes:
    return message.SerializeToString(deterministic=True)


def field_value(field: Any, value: Any) -> Any:
    if field.cpp_type == field.CPPTYPE_ENUM:
        descriptor = field.enum_type.values_by_number.get(int(value))
        return descriptor.name if descriptor is not None else int(value)
    if field.type == field.TYPE_BYTES:
        return base64.b64encode(value).decode("ascii")
    return value


def diff_messages(before: Any, after: Any, prefix: str = "") -> list[dict[str, Any]]:
    """Return deterministic leaf-field changes between same-type protobuf messages."""

    if before.DESCRIPTOR.full_name != after.DESCRIPTOR.full_name:
        raise ToolError("cannot diff protobuf messages with different types")
    changes: list[dict[str, Any]] = []
    for field in before.DESCRIPTOR.fields:
        path = f"{prefix}.{field.name}" if prefix else field.name
        before_value = getattr(before, field.name)
        after_value = getattr(after, field.name)
        if field.is_repeated:
            if field.cpp_type == field.CPPTYPE_MESSAGE:
                if len(before_value) != len(after_value):
                    changes.append(
                        {"path": path, "before_count": len(before_value), "after_count": len(after_value)}
                    )
                    continue
                for index, (before_item, after_item) in enumerate(zip(before_value, after_value)):
                    changes.extend(diff_messages(before_item, after_item, f"{path}[{index}]"))
            elif list(before_value) != list(after_value):
                changes.append(
                    {
                        "path": path,
                        "before": [field_value(field, item) for item in before_value],
                        "after": [field_value(field, item) for item in after_value],
                    }
                )
            continue
        if field.cpp_type == field.CPPTYPE_MESSAGE:
            before_has = before.HasField(field.name)
            after_has = after.HasField(field.name)
            if before_has != after_has:
                changes.append({"path": path, "before_present": before_has, "after_present": after_has})
            elif before_has:
                changes.extend(diff_messages(before_value, after_value, path))
            continue
        if before_value != after_value:
            changes.append(
                {
                    "path": path,
                    "before": field_value(field, before_value),
                    "after": field_value(field, after_value),
                }
            )
    return changes


def clone_config(config: Any, config_pb2: Any) -> Any:
    candidate = config_pb2.Config()
    candidate.CopyFrom(config)
    return candidate


def choose_non_type_mode(config: Any, forbidden_mode: int, reference_field: str) -> int:
    for index, mode in enumerate(config.game_mode_configs):
        if mode.mode_id != forbidden_mode and getattr(mode, reference_field) == 0:
            return index
    raise ToolError(
        f"captured config has no game mode suitable for minimal {reference_field} type mutation"
    )


def choose_bound_mode(config: Any, required_mode: int, reference_field: str) -> tuple[int, bool]:
    for index, mode in enumerate(config.game_mode_configs):
        if mode.mode_id == required_mode:
            return index, False
    for index, mode in enumerate(config.game_mode_configs):
        if mode.keyboard_mode_config == 0 and mode.custom_mode_config == 0:
            return index, True
    raise ToolError(
        f"captured config has no game mode suitable for deterministic {reference_field} bound mutation"
    )


def config_case(
    case_id: str,
    target: str,
    mutation: str,
    baseline: Any,
    candidate: Any,
    expected_error: str,
) -> MutationCase:
    changed = diff_messages(baseline, candidate)
    if not changed:
        raise ToolError(f"mutation case {case_id} made no field change")
    return MutationCase(
        id=case_id,
        target_validation_branch=target,
        mutation=mutation,
        changed_fields=changed,
        payload=deterministic_payload(candidate),
        expected_response_command="CMD_ERROR",
        expected_error_text=expected_error,
    )


def first_validation_failure(config: Any, config_pb2: Any) -> tuple[str, str] | None:
    """Mirror the candidate's six bounded checks, in exact production order."""

    backend_count = len(config.communication_backend_configs)
    mode_count = len(config.game_mode_configs)
    keyboard_count = len(config.keyboard_modes)
    custom_count = len(config.custom_modes)
    if config.default_backend_config > backend_count:
        return (
            "default_backend_config > communication_backend_configs_count",
            f"Default backend ID is {config.default_backend_config} but only {backend_count} backend configs are defined",
        )
    for index, backend in enumerate(config.communication_backend_configs):
        if backend.default_mode_config > mode_count:
            return (
                "communication_backend_configs[i].default_mode_config > game_mode_configs_count",
                f"Default mode ID is {backend.default_mode_config} for backend {index + 1} but only {mode_count} modes are defined",
            )
    for index, mode in enumerate(config.game_mode_configs):
        if mode.keyboard_mode_config > 0 and mode.mode_id != config_pb2.MODE_KEYBOARD:
            return (
                "keyboard_mode_config > 0 while mode_id != MODE_KEYBOARD",
                f"keyboard_mode_id is set for game mode {index + 1} but mode_id is not MODE_KEYBOARD",
            )
        if mode.custom_mode_config > 0 and mode.mode_id != config_pb2.MODE_CUSTOM:
            return (
                "custom_mode_config > 0 while mode_id != MODE_CUSTOM",
                f"custom_mode_id is set for game mode {index + 1} but mode_id is not MODE_CUSTOM",
            )
        if mode.keyboard_mode_config > keyboard_count:
            return (
                "keyboard_mode_config > keyboard_modes_count after keyboard type check",
                f"Keyboard mode ID {mode.keyboard_mode_config} is for game mode {index + 1} but only {keyboard_count} keyboard modes are defined",
            )
        if mode.custom_mode_config > custom_count:
            return (
                "custom_mode_config > custom_modes_count after custom type check",
                f"Custom mode ID {mode.custom_mode_config} is for game mode config {index + 1} but only {custom_count} custom modes are defined",
            )
    return None


def build_rejection_cases(baseline: Any, config_pb2: Any) -> list[MutationCase]:
    """Build malformed plus the six production validation rejection families."""

    baseline_failure = first_validation_failure(baseline, config_pb2)
    if baseline_failure is not None:
        raise ToolError(
            "captured persisted Config already fails the candidate validation order: "
            f"branch={baseline_failure[0]!r}, error={baseline_failure[1]!r}"
        )
    if not baseline.communication_backend_configs:
        raise ToolError("captured config has no communication backend config to mutate")
    if not baseline.game_mode_configs:
        raise ToolError("captured config has no game mode config to mutate")

    cases: list[MutationCase] = [
        MutationCase(
            id="malformed_decode",
            target_validation_branch="pb_decode(Config_fields) failure",
            mutation=(
                "Send protobuf byte 00 (illegal protobuf zero tag). COBS framing and "
                "CMD_SET_CONFIG remain valid."
            ),
            changed_fields=[],
            payload=bytes.fromhex("00"),
            expected_response_command="CMD_ERROR",
            expected_error_text="Failed to decode config: zero tag",
            error_match="exact",
        )
    ]

    backend_count = len(baseline.communication_backend_configs)
    mode_count = len(baseline.game_mode_configs)
    keyboard_count = len(baseline.keyboard_modes)
    custom_count = len(baseline.custom_modes)

    candidate = clone_config(baseline, config_pb2)
    candidate.default_backend_config = backend_count + 1
    cases.append(
        config_case(
            "invalid_default_backend_index",
            "default_backend_config > communication_backend_configs_count",
            f"default_backend_config: {baseline.default_backend_config} -> {backend_count + 1}",
            baseline,
            candidate,
            f"Default backend ID is {backend_count + 1} but only {backend_count} backend configs are defined",
        )
    )

    candidate = clone_config(baseline, config_pb2)
    before_mode_ref = candidate.communication_backend_configs[0].default_mode_config
    candidate.communication_backend_configs[0].default_mode_config = mode_count + 1
    cases.append(
        config_case(
            "invalid_backend_default_mode_reference",
            "communication_backend_configs[i].default_mode_config > game_mode_configs_count",
            (
                "communication_backend_configs[0].default_mode_config: "
                f"{before_mode_ref} -> {mode_count + 1}"
            ),
            baseline,
            candidate,
            f"Default mode ID is {mode_count + 1} for backend 1 but only {mode_count} modes are defined",
        )
    )

    keyboard_type_index = choose_non_type_mode(
        baseline, config_pb2.MODE_KEYBOARD, "keyboard_mode_config"
    )
    candidate = clone_config(baseline, config_pb2)
    candidate.game_mode_configs[keyboard_type_index].keyboard_mode_config = 1
    cases.append(
        config_case(
            "invalid_keyboard_reference_type",
            "keyboard_mode_config > 0 while mode_id != MODE_KEYBOARD",
            f"game_mode_configs[{keyboard_type_index}].keyboard_mode_config: 0 -> 1",
            baseline,
            candidate,
            (
                "keyboard_mode_id is set for game mode "
                f"{keyboard_type_index + 1} but mode_id is not MODE_KEYBOARD"
            ),
        )
    )

    custom_type_index = choose_non_type_mode(
        baseline, config_pb2.MODE_CUSTOM, "custom_mode_config"
    )
    candidate = clone_config(baseline, config_pb2)
    candidate.game_mode_configs[custom_type_index].custom_mode_config = 1
    cases.append(
        config_case(
            "invalid_custom_reference_type",
            "custom_mode_config > 0 while mode_id != MODE_CUSTOM",
            f"game_mode_configs[{custom_type_index}].custom_mode_config: 0 -> 1",
            baseline,
            candidate,
            (
                "custom_mode_id is set for game mode "
                f"{custom_type_index + 1} but mode_id is not MODE_CUSTOM"
            ),
        )
    )

    keyboard_bound_index, keyboard_type_change = choose_bound_mode(
        baseline, config_pb2.MODE_KEYBOARD, "keyboard_mode_config"
    )
    candidate = clone_config(baseline, config_pb2)
    if keyboard_type_change:
        candidate.game_mode_configs[keyboard_bound_index].mode_id = config_pb2.MODE_KEYBOARD
    candidate.game_mode_configs[keyboard_bound_index].keyboard_mode_config = keyboard_count + 1
    keyboard_change_note = (
        f"game_mode_configs[{keyboard_bound_index}].keyboard_mode_config: "
        f"{baseline.game_mode_configs[keyboard_bound_index].keyboard_mode_config} -> {keyboard_count + 1}"
    )
    if keyboard_type_change:
        keyboard_change_note += (
            f"; mode_id: {config_pb2.GameModeId.Name(baseline.game_mode_configs[keyboard_bound_index].mode_id)} "
            "-> MODE_KEYBOARD (required to pass the earlier type check)"
        )
    cases.append(
        config_case(
            "keyboard_index_out_of_range",
            "keyboard_mode_config > keyboard_modes_count after keyboard type check",
            keyboard_change_note,
            baseline,
            candidate,
            (
                f"Keyboard mode ID {keyboard_count + 1} is for game mode {keyboard_bound_index + 1} "
                f"but only {keyboard_count} keyboard modes are defined"
            ),
        )
    )

    custom_bound_index, custom_type_change = choose_bound_mode(
        baseline, config_pb2.MODE_CUSTOM, "custom_mode_config"
    )
    candidate = clone_config(baseline, config_pb2)
    if custom_type_change:
        candidate.game_mode_configs[custom_bound_index].mode_id = config_pb2.MODE_CUSTOM
    candidate.game_mode_configs[custom_bound_index].custom_mode_config = custom_count + 1
    custom_change_note = (
        f"game_mode_configs[{custom_bound_index}].custom_mode_config: "
        f"{baseline.game_mode_configs[custom_bound_index].custom_mode_config} -> {custom_count + 1}"
    )
    if custom_type_change:
        custom_change_note += (
            f"; mode_id: {config_pb2.GameModeId.Name(baseline.game_mode_configs[custom_bound_index].mode_id)} "
            "-> MODE_CUSTOM (required to pass the earlier type check)"
        )
    cases.append(
        config_case(
            "custom_index_out_of_range",
            "custom_mode_config > custom_modes_count after custom type check",
            custom_change_note,
            baseline,
            candidate,
            (
                f"Custom mode ID {custom_count + 1} is for game mode config {custom_bound_index + 1} "
                f"but only {custom_count} custom modes are defined"
            ),
        )
    )

    for case in cases[1:]:
        decoded = config_pb2.Config()
        decoded.ParseFromString(case.payload)
        failure = first_validation_failure(decoded, config_pb2)
        expected = (case.target_validation_branch, case.expected_error_text)
        if failure != expected:
            raise ToolError(
                f"case {case.id} does not first reach its declared validation branch: "
                f"expected={expected!r}, actual={failure!r}"
            )
    return cases


def build_valid_update(baseline: Any, config_pb2: Any) -> tuple[Any, dict[str, Any]]:
    """Change only RGB brightness, the schema's non-game-semantic lighting modifier."""

    before = int(baseline.rgb_brightness)
    if not 0 <= before <= 255:
        raise ToolError(f"captured rgb_brightness is outside firmware uint8 range: {before}")
    # Use values produced by the existing Glyph brightness menu, rather than
    # assuming every uint8 value is an operator-supported UI setting.
    after = 30 if before == 20 else 20
    candidate = clone_config(baseline, config_pb2)
    candidate.rgb_brightness = after
    changes = diff_messages(baseline, candidate)
    expected = [{"path": "rgb_brightness", "before": before, "after": after}]
    if changes != expected:
        raise ToolError(f"valid update was not an exact one-field brightness change: {changes}")
    confirmation_token = f"SET_RGB_BRIGHTNESS_{before}_TO_{after}"
    return candidate, {
        "field": "rgb_brightness",
        "before": before,
        "after": after,
        "changed_fields": changes,
        "source_support": (
            "config.proto defines Config.rgb_brightness as the overall RGB brightness modifier "
            "for RgbConfig lighting; Glyph RgbBrightnessMenu reads/writes this field."
        ),
        "game_semantics": "No game-mode, mapping, backend, or controller-output field changes.",
        "confirmation_token": confirmation_token,
    }


def payload_record(command_id: int, payload: bytes) -> dict[str, Any]:
    framed = cobs_encode(bytes([command_id]) + payload)
    return {
        "command_id": command_id,
        "command": command_name(command_id),
        "protobuf_payload_length": len(payload),
        "protobuf_payload_sha256": sha256_bytes(payload),
        "protobuf_payload_hex": payload.hex(),
        "protobuf_payload_base64": base64.b64encode(payload).decode("ascii"),
        "cobs_framed_packet_length": len(framed),
        "cobs_framed_packet_hex": framed.hex(),
    }


def build_payload_plan(baseline: Any, baseline_payload: bytes, config_pb2: Any) -> dict[str, Any]:
    cases = build_rejection_cases(baseline, config_pb2)
    valid_message, valid_metadata = build_valid_update(baseline, config_pb2)
    return {
        "schema_name": PLAN_SCHEMA,
        "schema_version": PLAN_SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "candidate_git_sha": CANDIDATE_GIT_SHA,
        "artifact_sha256": ARTIFACT_SHA256,
        "dry_run": True,
        "device_access": False,
        "baseline": {
            "source": "host-side captured CMD_GET_CONFIG payload (persisted config.bin path)",
            "payload_length": len(baseline_payload),
            "payload_sha256": sha256_bytes(baseline_payload),
            "not_live_ram_identity_proof": True,
        },
        "rejection_cases": [
            {
                "id": case.id,
                "target_validation_branch": case.target_validation_branch,
                "mutation": case.mutation,
                "changed_fields": case.changed_fields,
                "expected_response_command": case.expected_response_command,
                "expected_error_text": case.expected_error_text,
                "error_match": case.error_match,
                "payload": payload_record(CMD_SET_CONFIG, case.payload),
                "followup": "CMD_GET_DEVICE_INFO; expect CMD_SET_DEVICE_INFO and continued response",
            }
            for case in cases
        ],
        "valid_update": {
            **valid_metadata,
            "payload": payload_record(CMD_SET_CONFIG, deterministic_payload(valid_message)),
            "will_send": False,
            "explicit_confirmation_required": True,
        },
        "nonclaims": RESULT_NONCLAIMS,
    }


def config_to_dict(message: Any, json_format: Any) -> dict[str, Any]:
    return json_format.MessageToDict(
        message,
        preserving_proto_field_name=True,
        use_integers_for_enums=False,
    )


def make_capture(
    payload: bytes,
    config_message: Any,
    json_format: Any,
    *,
    port: str,
    device_info: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "schema_name": CAPTURE_SCHEMA,
        "schema_version": CAPTURE_SCHEMA_VERSION,
        "captured_at_utc": utc_now(),
        "protocol_version": PROTOCOL_VERSION,
        "candidate_git_sha": CANDIDATE_GIT_SHA,
        "artifact_sha256": ARTIFACT_SHA256,
        "label": "HOST-SIDE CAPTURED CONFIG — NON-AUTHORITATIVE",
        "source_command": "CMD_GET_CONFIG",
        "source_behavior": "Firmware returns the protobuf body read from persisted config.bin.",
        "device_context": {"selected_port": port, "device_info": device_info},
        "raw_config_payload_length": len(payload),
        "raw_config_payload_sha256": sha256_bytes(payload),
        "raw_config_payload_base64": base64.b64encode(payload).decode("ascii"),
        "config": config_to_dict(config_message, json_format),
        "nonclaims": CAPTURE_NONCLAIMS,
    }


def validate_capture(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ToolError("capture root must be a JSON object")
    required_exact = {
        "schema_name": CAPTURE_SCHEMA,
        "schema_version": CAPTURE_SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "candidate_git_sha": CANDIDATE_GIT_SHA,
        "artifact_sha256": ARTIFACT_SHA256,
    }
    for key, expected in required_exact.items():
        if value.get(key) != expected:
            raise ToolError(f"capture {key} mismatch: expected={expected!r}, actual={value.get(key)!r}")
    encoded = value.get("raw_config_payload_base64")
    if not isinstance(encoded, str):
        raise ToolError("capture raw_config_payload_base64 must be a string")
    try:
        payload = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise ToolError(f"capture payload base64 is invalid: {exc}") from exc
    if value.get("raw_config_payload_length") != len(payload):
        raise ToolError("capture payload length mismatch")
    if value.get("raw_config_payload_sha256") != sha256_bytes(payload):
        raise ToolError("capture payload SHA-256 mismatch")
    return value


def load_capture(path: Path, config_pb2: Any, json_format: Any) -> tuple[dict[str, Any], Any, bytes]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ToolError(f"failed to read capture {path}: {exc}") from exc
    capture = validate_capture(value)
    payload = base64.b64decode(capture["raw_config_payload_base64"], validate=True)
    message = config_pb2.Config()
    try:
        message.ParseFromString(payload)
    except Exception as exc:
        raise ToolError(f"capture protobuf payload is not a Config: {exc}") from exc
    captured_dict = capture.get("config")
    if captured_dict != config_to_dict(message, json_format):
        raise ToolError("capture JSON config does not correspond to its raw protobuf payload")
    return capture, message, payload


def request_device_info(transport: Transport, config_pb2: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    command_id, payload = transport.transact(CMD_GET_DEVICE_INFO, b"")
    response = response_record(command_id, payload)
    if command_id == CMD_ERROR:
        raise ToolError(f"device error during GET_DEVICE_INFO: {response['text']}")
    if command_id != CMD_SET_DEVICE_INFO:
        raise ToolError(
            "unexpected response command for GET_DEVICE_INFO: "
            f"expected=CMD_SET_DEVICE_INFO, actual={command_name(command_id)}"
        )
    message = config_pb2.DeviceInfo()
    try:
        message.ParseFromString(payload)
    except Exception as exc:
        raise ToolError(f"failed to decode DeviceInfo protobuf: {exc}") from exc
    if message.firmware_version != EXPECTED_DEVICE_FIRMWARE_VERSION:
        raise ToolError(
            "device firmware short identity mismatch: "
            f"expected={EXPECTED_DEVICE_FIRMWARE_VERSION!r}, actual={message.firmware_version!r}. "
            "The short value is supportive only; the preserved UF2 hash remains the exact identity."
        )
    return (
        {
            "firmware_name": message.firmware_name,
            "firmware_version": message.firmware_version,
            "device_name": message.device_name,
            "candidate_short_identity_matches": True,
            "identity_nonclaim": (
                "The embedded short Git version supports selection but does not prove the full "
                "candidate SHA or exact flashed UF2 bytes."
            ),
        },
        response,
    )


def request_device_info_response(transport: Transport, config_pb2: Any) -> dict[str, Any]:
    """Use existing device info as a harmless same-transport responsiveness check."""

    device_info, response = request_device_info(transport, config_pb2)
    return {"response": response, "decoded_device_info": device_info}


def request_config(transport: Transport) -> tuple[bytes, dict[str, Any]]:
    command_id, payload = transport.transact(CMD_GET_CONFIG, b"")
    response = response_record(command_id, payload)
    if command_id == CMD_ERROR:
        raise ToolError(f"device error during GET_CONFIG: {response['text']}")
    if command_id != CMD_SET_CONFIG:
        raise ToolError(
            "unexpected response command for GET_CONFIG: "
            f"expected=CMD_SET_CONFIG, actual={command_name(command_id)}"
        )
    return payload, response


def decode_config(payload: bytes, config_pb2: Any) -> Any:
    message = config_pb2.Config()
    try:
        message.ParseFromString(payload)
    except Exception as exc:
        raise ToolError(f"GET_CONFIG payload is not a valid Config protobuf: {exc}") from exc
    return message


def expected_error_matches(case: MutationCase, actual_text: str | None) -> bool:
    if actual_text is None:
        return False
    if case.error_match == "prefix":
        return actual_text.startswith(case.expected_error_text)
    return actual_text == case.expected_error_text


def execute_rejection_case(
    transport: Transport,
    case: MutationCase,
    baseline_payload: bytes,
    config_pb2: Any,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": case.id,
        "target_validation_branch": case.target_validation_branch,
        "mutation": case.mutation,
        "changed_fields": case.changed_fields,
        "source_baseline_payload_sha256": sha256_bytes(baseline_payload),
        "request": payload_record(CMD_SET_CONFIG, case.payload),
        "expected": {
            "response_command": case.expected_response_command,
            "error_text": case.expected_error_text,
            "error_match": case.error_match,
            "unexpected_success": False,
            "followup": "CMD_GET_DEVICE_INFO returns CMD_SET_DEVICE_INFO",
        },
        "response": None,
        "response_matches_expected": False,
        "unexpected_success": False,
        "connected_after": False,
        "followup": None,
        "followup_responsive": False,
        "mechanical_outcome": "NOT_RUN",
        "human_observation": None,
    }
    try:
        command_id, response_payload = transport.transact(CMD_SET_CONFIG, case.payload)
        result["response"] = response_record(command_id, response_payload)
        result["unexpected_success"] = command_id == CMD_SUCCESS
        result["connected_after"] = transport_is_open(transport)
        result["response_matches_expected"] = (
            command_id == CMD_ERROR
            and expected_error_matches(case, result["response"]["text"])
        )
        if not result["response_matches_expected"]:
            result["mechanical_outcome"] = "UNEXPECTED_RESPONSE_STOP"
            return result

        followup_response = request_device_info_response(transport, config_pb2)
        result["connected_after"] = transport_is_open(transport)
        result["followup"] = {
            "request_command": "CMD_GET_DEVICE_INFO",
            **followup_response,
            "purpose": "Harmless same-backend responsiveness check; not a config equality claim.",
        }
        result["followup_responsive"] = True
        result["mechanical_outcome"] = "EXPECTED_REJECTION_AND_RESPONSIVE"
        return result
    except Exception as exc:
        result["connected_after"] = False
        result["mechanical_outcome"] = "TRANSPORT_OR_FOLLOWUP_ERROR_STOP"
        result["error"] = str(exc)
        return result


def execute_rejection_suite(
    transport: Transport,
    cases: list[MutationCase],
    baseline_payload: bytes,
    config_pb2: Any,
) -> tuple[list[dict[str, Any]], bool]:
    results: list[dict[str, Any]] = []
    for case in cases:
        record = execute_rejection_case(transport, case, baseline_payload, config_pb2)
        results.append(record)
        if record["mechanical_outcome"] != "EXPECTED_REJECTION_AND_RESPONSIVE":
            return results, False
    return results, True


def execute_valid_update(
    transport: Transport,
    baseline: Any,
    baseline_payload: bytes,
    config_pb2: Any,
    *,
    confirmation_token: str | None,
    rejection_observations_acknowledged: bool,
) -> dict[str, Any]:
    candidate, metadata = build_valid_update(baseline, config_pb2)
    payload = deterministic_payload(candidate)
    result: dict[str, Any] = {
        **metadata,
        "request": payload_record(CMD_SET_CONFIG, payload),
        "confirmation_required": True,
        "confirmation_received": confirmation_token == metadata["confirmation_token"],
        "rejection_observation_acknowledgement_required": True,
        "rejection_observation_acknowledged": rejection_observations_acknowledged,
        "acknowledgement_nonclaim": (
            "Acknowledgement permits the next operation; it does not auto-populate a hardware PASS."
        ),
        "sent": False,
        "response": None,
        "unexpected_error": False,
        "connected_after": False,
        "followup_responsive": False,
        "post_update_get_config_matches_sent_payload": False,
        "mechanical_outcome": "NOT_SENT_NO_CONFIRMATION",
        "human_reboot_observation": None,
        "human_controller_display_smoke": None,
    }
    if not rejection_observations_acknowledged:
        result["mechanical_outcome"] = "NOT_SENT_NO_REJECTION_OBSERVATION_ACKNOWLEDGEMENT"
        return result
    if confirmation_token != metadata["confirmation_token"]:
        return result

    try:
        current_payload, _ = request_config(transport)
        if current_payload != baseline_payload:
            result["mechanical_outcome"] = "BASELINE_DRIFT_STOP"
            result["error"] = (
                "current persisted GET_CONFIG payload differs from the captured baseline; "
                "recapture and review before any valid write"
            )
            result["connected_after"] = transport_is_open(transport)
            return result
        command_id, response_payload = transport.transact(CMD_SET_CONFIG, payload)
        result["sent"] = True
        result["response"] = response_record(command_id, response_payload)
        result["unexpected_error"] = command_id == CMD_ERROR
        result["connected_after"] = transport_is_open(transport)
        if command_id != CMD_SUCCESS:
            result["mechanical_outcome"] = "UNEXPECTED_VALID_UPDATE_RESPONSE_STOP"
            return result
        followup_payload, followup_response = request_config(transport)
        result["followup"] = {
            "request_command": "CMD_GET_CONFIG",
            "response": followup_response,
            "payload_match_nonclaim": "Persisted payload comparison is not atomic-persistence proof.",
        }
        result["followup_responsive"] = True
        result["post_update_get_config_matches_sent_payload"] = followup_payload == payload
        result["connected_after"] = transport_is_open(transport)
        result["mechanical_outcome"] = "SUCCESS_RESPONSE_AND_RESPONSIVE"
        return result
    except Exception as exc:
        result["connected_after"] = False
        result["mechanical_outcome"] = "TRANSPORT_OR_FOLLOWUP_ERROR_STOP"
        result["error"] = str(exc)
        return result


def empty_result(device_context: dict[str, Any], capture: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "schema_name": RESULT_SCHEMA,
        "schema_version": RESULT_SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "candidate_git_sha": CANDIDATE_GIT_SHA,
        "artifact_sha256": ARTIFACT_SHA256,
        "generated_at_utc": utc_now(),
        "device_context": device_context,
        "baseline_capture": None
        if capture is None
        else {
            "label": capture["label"],
            "captured_at_utc": capture["captured_at_utc"],
            "raw_config_payload_sha256": capture["raw_config_payload_sha256"],
            "not_live_ram_identity_proof": True,
        },
        "tests": [],
        "valid_update": {
            "sent": False,
            "mechanical_outcome": "NOT_RUN",
            "human_reboot_observation": None,
            "human_controller_display_smoke": None,
        },
        "ordinary_controller_display_smoke": None,
        "rejected_values_operationally_visible": None,
        "operator_assessment": None,
        "operator_notes": "",
        "hardware_evidence_generated": False,
        "nonclaims": RESULT_NONCLAIMS,
    }


def validate_result_schema(value: Any) -> None:
    if not isinstance(value, dict):
        raise ToolError("result root must be an object")
    exact = {
        "schema_name": RESULT_SCHEMA,
        "schema_version": RESULT_SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "candidate_git_sha": CANDIDATE_GIT_SHA,
        "artifact_sha256": ARTIFACT_SHA256,
        "hardware_evidence_generated": False,
    }
    for key, expected in exact.items():
        if value.get(key) != expected:
            raise ToolError(f"result {key} mismatch: expected={expected!r}, actual={value.get(key)!r}")
    if not isinstance(value.get("tests"), list):
        raise ToolError("result tests must be a list")
    if not isinstance(value.get("valid_update"), dict):
        raise ToolError("result valid_update must be an object")
    if value.get("operator_assessment") is not None:
        raise ToolError("new mechanical result must leave operator_assessment null")
    for record in value["tests"]:
        if not isinstance(record, dict) or "id" not in record:
            raise ToolError("each test result must be an object with id")
        if "human_observation" not in record or record["human_observation"] is not None:
            raise ToolError("mechanical rejection records must leave human_observation null")


def load_completed_rejection_result(path: Path, capture: dict[str, Any]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ToolError(f"failed to read rejection result {path}: {exc}") from exc
    validate_result_schema(value)
    if value.get("suite_mechanically_complete") is not True:
        raise ToolError("valid update requires suite_mechanically_complete=true")
    baseline = value.get("baseline_capture")
    if not isinstance(baseline, dict) or (
        baseline.get("raw_config_payload_sha256")
        != capture["raw_config_payload_sha256"]
    ):
        raise ToolError("rejection result baseline does not match the selected capture")
    expected_ids = [
        "malformed_decode",
        "invalid_default_backend_index",
        "invalid_backend_default_mode_reference",
        "invalid_keyboard_reference_type",
        "invalid_custom_reference_type",
        "keyboard_index_out_of_range",
        "custom_index_out_of_range",
    ]
    if [record.get("id") for record in value["tests"]] != expected_ids:
        raise ToolError("rejection result does not contain the exact ordered seven-case suite")
    for record in value["tests"]:
        response = record.get("response")
        followup = record.get("followup")
        if not (
            record.get("mechanical_outcome") == "EXPECTED_REJECTION_AND_RESPONSIVE"
            and record.get("response_matches_expected") is True
            and record.get("unexpected_success") is False
            and record.get("connected_after") is True
            and record.get("followup_responsive") is True
            and isinstance(response, dict)
            and response.get("command") == "CMD_ERROR"
            and isinstance(followup, dict)
            and followup.get("request_command") == "CMD_GET_DEVICE_INFO"
            and isinstance(followup.get("response"), dict)
            and followup["response"].get("command") == "CMD_SET_DEVICE_INFO"
        ):
            raise ToolError(f"rejection result case is not mechanically complete: {record.get('id')}")
    if value["valid_update"].get("sent") is not False:
        raise ToolError("rejection prerequisite result must not already contain a valid update")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_dump(value), encoding="utf-8")


def open_transport(args: argparse.Namespace) -> PosixSerialPort:
    transport = PosixSerialPort(args.port, args.baudrate, args.timeout_sec)
    transport.open()
    return transport


def load_modules() -> tuple[Any, Any, Path]:
    return load_runtime_proto_modules(REPO_ROOT)


def default_output_dir() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "local_backups" / "gp-config-005-operator" / stamp


def add_serial_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--port", required=True, help="Exact serial path selected from the list command.")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--timeout-sec", type=float, default=5.0)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List plausible serial paths without opening them.")
    subparsers.add_parser("identity", help="Verify protocol, candidate, and preserved UF2 identity.")

    capture = subparsers.add_parser("capture-current", help="Capture persisted config via CMD_GET_CONFIG.")
    add_serial_args(capture)
    capture.add_argument("--capture-out", type=Path, required=True)

    dry_run = subparsers.add_parser("dry-run", help="Generate exact payload plan without device access.")
    dry_run.add_argument("--baseline", type=Path, required=True, help="Host capture JSON.")
    dry_run.add_argument("--plan-out", type=Path)

    rejection = subparsers.add_parser("rejection-suite", help="Run malformed and bounded-invalid cases.")
    add_serial_args(rejection)
    rejection.add_argument("--baseline", type=Path, required=True)
    rejection.add_argument("--result-out", type=Path, required=True)

    valid = subparsers.add_parser("valid-update", help="Send the one-field RGB brightness update.")
    add_serial_args(valid)
    valid.add_argument("--baseline", type=Path, required=True)
    valid.add_argument(
        "--rejection-result",
        type=Path,
        required=True,
        help="Completed seven-case result tied to the same captured baseline.",
    )
    valid.add_argument("--result-out", type=Path, required=True)
    valid.add_argument(
        "--confirm-token",
        help="Exact token printed by dry-run; omission always prevents SET_CONFIG.",
    )
    valid.add_argument(
        "--rejection-observation-ack-token",
        help=(
            "Exact operator acknowledgement required after checking that rejected values are not "
            "operationally visible; this is not an automatic PASS."
        ),
    )

    status = subparsers.add_parser("status", help="Read device info and persisted config without mutation.")
    add_serial_args(status)

    run = subparsers.add_parser("run", help="Capture, run all rejections, then confirm one valid update.")
    add_serial_args(run)
    run.add_argument("--output-dir", type=Path)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "list":
        devices = discover_serial_devices()
        print(json_dump({"devices": devices, "auto_selected": False}), end="")
        return 0

    try:
        identity = verify_repository_identity(require_artifact=True)
        if args.command == "identity":
            print(json_dump(identity), end="")
            return 0

        config_pb2, json_format, proto_path = load_modules()
        identity["config_proto_path"] = str(proto_path)

        if args.command == "dry-run":
            _, baseline, baseline_payload = load_capture(args.baseline, config_pb2, json_format)
            plan = build_payload_plan(baseline, baseline_payload, config_pb2)
            if args.plan_out:
                write_json(args.plan_out, plan)
            print(json_dump(plan), end="")
            return 0

        loaded_capture: tuple[dict[str, Any], Any, bytes] | None = None
        completed_rejection_result: dict[str, Any] | None = None
        if args.command in {"rejection-suite", "valid-update"}:
            loaded_capture = load_capture(args.baseline, config_pb2, json_format)

        if args.command == "valid-update" and loaded_capture is not None:
            capture, baseline, baseline_payload = loaded_capture
            _, metadata = build_valid_update(baseline, config_pb2)
            acknowledged = (
                args.rejection_observation_ack_token == REJECTION_OBSERVATION_ACK_TOKEN
            )
            if args.confirm_token != metadata["confirmation_token"] or not acknowledged:
                result = empty_result({"selected_port": args.port}, capture)
                result["valid_update"] = execute_valid_update(
                    object(),  # The no-confirmation branch performs no transport call.
                    baseline,
                    baseline_payload,
                    config_pb2,
                    confirmation_token=args.confirm_token,
                    rejection_observations_acknowledged=acknowledged,
                )
                validate_result_schema(result)
                write_json(args.result_out, result)
                print(json_dump(result), end="")
                print(
                    "STOP: exact update confirmation and rejection-observation acknowledgement "
                    "are both required; serial device was not opened.",
                    file=sys.stderr,
                )
                return 1
            completed_rejection_result = load_completed_rejection_result(
                args.rejection_result, capture
            )
            print("Confirmed prerequisite: exact seven-case rejection result is mechanically complete.")
            print("Review the valid-update diff immediately before device access:")
            print(json_dump(metadata), end="", flush=True)

        transport = open_transport(args)
        try:
            if args.command == "status":
                device_info, device_response = request_device_info(transport, config_pb2)
                current_payload, config_response = request_config(transport)
                decode_config(current_payload, config_pb2)
                print(
                    json_dump(
                        {
                            "identity": identity,
                            "selected_port": args.port,
                            "device_info": device_info,
                            "responses": [device_response, config_response],
                            "config_payload_sha256": sha256_bytes(current_payload),
                            "connected": transport_is_open(transport),
                            "nonclaim": "GET_CONFIG reads persisted config.bin, not proven live RAM bytes.",
                        }
                    ),
                    end="",
                )
                return 0

            if args.command == "capture-current":
                device_info, _ = request_device_info(transport, config_pb2)
                payload, _ = request_config(transport)
                message = decode_config(payload, config_pb2)
                capture = make_capture(
                    payload, message, json_format, port=args.port, device_info=device_info
                )
                write_json(args.capture_out, capture)
                print(json_dump(capture), end="")
                print(f"capture_written={args.capture_out.resolve()}")
                return 0

            capture, baseline, baseline_payload = (
                loaded_capture if loaded_capture is not None else (None, None, None)
            )

            if args.command == "rejection-suite":
                result = empty_result({"selected_port": args.port}, capture)
                current_payload, preflight_response = request_config(transport)
                result["baseline_preflight"] = {
                    "request_command": "CMD_GET_CONFIG",
                    "response": preflight_response,
                    "matches_captured_persisted_payload": current_payload == baseline_payload,
                    "nonclaim": "This comparison does not prove live-RAM byte identity.",
                }
                if current_payload != baseline_payload:
                    result["suite_mechanically_complete"] = False
                    result["suite_stop_reason"] = (
                        "Current persisted payload differs from capture; recapture before mutation."
                    )
                    validate_result_schema(result)
                    write_json(args.result_out, result)
                    print(json_dump(result), end="")
                    return 1
                result["tests"], complete = execute_rejection_suite(
                    transport,
                    build_rejection_cases(baseline, config_pb2),
                    baseline_payload,
                    config_pb2,
                )
                result["suite_mechanically_complete"] = complete
                validate_result_schema(result)
                write_json(args.result_out, result)
                print(json_dump(result), end="")
                return 0 if complete else 1

            if args.command == "valid-update":
                result = empty_result({"selected_port": args.port}, capture)
                result["rejection_prerequisite"] = {
                    "path": str(args.rejection_result.resolve()),
                    "file_sha256": file_sha256(args.rejection_result),
                    "suite_mechanically_complete": completed_rejection_result[
                        "suite_mechanically_complete"
                    ],
                    "operator_assessment": completed_rejection_result[
                        "operator_assessment"
                    ],
                }
                result["valid_update"] = execute_valid_update(
                    transport,
                    baseline,
                    baseline_payload,
                    config_pb2,
                    confirmation_token=args.confirm_token,
                    rejection_observations_acknowledged=True,
                )
                validate_result_schema(result)
                write_json(args.result_out, result)
                print(json_dump(result), end="")
                return 0 if result["valid_update"]["mechanical_outcome"] == "SUCCESS_RESPONSE_AND_RESPONSIVE" else 1

            if args.command == "run":
                output_dir = (args.output_dir or default_output_dir()).resolve()
                capture_path = output_dir / "captured-config.json"
                result_path = output_dir / "operator-result.json"
                plan_path = output_dir / "payload-plan.json"
                device_info, device_response = request_device_info(transport, config_pb2)
                baseline_payload, config_response = request_config(transport)
                baseline = decode_config(baseline_payload, config_pb2)
                capture = make_capture(
                    baseline_payload,
                    baseline,
                    json_format,
                    port=args.port,
                    device_info=device_info,
                )
                write_json(capture_path, capture)
                plan = build_payload_plan(baseline, baseline_payload, config_pb2)
                write_json(plan_path, plan)
                result = empty_result(
                    {
                        "selected_port": args.port,
                        "device_info": device_info,
                        "initial_responses": [device_response, config_response],
                    },
                    capture,
                )
                result["tests"], complete = execute_rejection_suite(
                    transport,
                    build_rejection_cases(baseline, config_pb2),
                    baseline_payload,
                    config_pb2,
                )
                result["suite_mechanically_complete"] = complete
                if not complete:
                    validate_result_schema(result)
                    write_json(result_path, result)
                    print(json_dump(result), end="")
                    print(f"STOP: rejection anomaly; result_written={result_path}")
                    return 1

                print(
                    "Before any valid update, observe the ordinary controller/display path and check "
                    "that no rejected value is operationally visible. Stop on any anomaly."
                )
                print(f"To continue, type exactly: {REJECTION_OBSERVATION_ACK_TOKEN}")
                rejection_ack = input("rejection_observation_ack_token> ").strip()
                acknowledged = rejection_ack == REJECTION_OBSERVATION_ACK_TOKEN
                result["pre_valid_operator_acknowledgement"] = {
                    "token_required": REJECTION_OBSERVATION_ACK_TOKEN,
                    "received": acknowledged,
                    "hardware_pass_auto_populated": False,
                }
                if not acknowledged:
                    validate_result_schema(result)
                    write_json(result_path, result)
                    print(f"STOP: acknowledgement not received; result_written={result_path}")
                    return 1

                _, valid_metadata = build_valid_update(baseline, config_pb2)
                print("All rejection responses and GET_DEVICE_INFO follow-ups matched mechanically.")
                print("Review the one-field valid update:")
                print(json_dump(valid_metadata), end="")
                print("Type the exact confirmation token shown above, or press Enter to stop without writing.")
                entered = input("confirmation_token> ").strip()
                result["valid_update"] = execute_valid_update(
                    transport,
                    baseline,
                    baseline_payload,
                    config_pb2,
                    confirmation_token=entered or None,
                    rejection_observations_acknowledged=acknowledged,
                )
                validate_result_schema(result)
                write_json(result_path, result)
                print(json_dump(result), end="")
                print(f"capture_written={capture_path}")
                print(f"plan_written={plan_path}")
                print(f"result_written={result_path}")
                if result["valid_update"]["mechanical_outcome"] != "SUCCESS_RESPONSE_AND_RESPONSIVE":
                    print("No completed valid update. Stop and inspect the result before continuing.")
                    return 1
                print(
                    "NEXT HUMAN STEP: reboot the controller once, run the status command, then perform "
                    "the ordinary controller/display smoke check. Record observations separately."
                )
                return 0

            raise ToolError(f"unsupported command: {args.command}")
        finally:
            transport.close()
    except (ToolError, OSError, EOFError, KeyboardInterrupt) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
