#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools import gp_config_010_recovery_operator as operator


class FakePort:
    def __init__(
        self,
        baseline: bytes,
        intended: bytes,
        device_info: bytes,
        *,
        fail_write: bool = False,
        fail_after_full_write: bool = False,
        response_command: int = operator.CMD_SUCCESS,
        readback: bytes | None = None,
    ) -> None:
        self.baseline = baseline
        self.intended = intended
        self.fail_write = fail_write
        self.fail_after_full_write = fail_after_full_write
        self.response_command = response_command
        self.readback = intended if readback is None else readback
        self.calls = 0
        self.closed = False
        self.device_info = device_info

    def transact(self, command: int, payload: bytes, *, stage_callback=None):
        self.calls += 1
        if self.calls == 1:
            return operator.CMD_SET_DEVICE_INFO, self.device_info
        if self.calls == 2:
            return operator.CMD_SET_CONFIG, self.baseline
        if self.calls == 3:
            assert command == operator.CMD_SET_CONFIG
            if stage_callback:
                stage_callback("write_attempted")
            if self.fail_write:
                raise operator.ToolError("synthetic write failure")
            for stage in ("full_host_write_completed", "awaiting_response", "response_received"):
                if self.fail_after_full_write and stage == "response_received":
                    raise operator.ToolError("synthetic response timeout")
                if stage_callback:
                    stage_callback(stage)
            return self.response_command, b"synthetic error" if self.response_command == operator.CMD_ERROR else b""
        return operator.CMD_SET_CONFIG, self.readback

    def close(self) -> None:
        self.closed = True


class RecoveryOperatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config_pb2, cls.json_format, _ = operator.load_runtime_proto_modules(operator.ROOT)

    def base_config(self):
        config = self.config_pb2.Config()
        mode = config.game_mode_configs.add()
        mode.mode_id = self.config_pb2.MODE_ULTIMATE
        mode.name = "OwnerUltimate"
        mode.activation_binding.append(self.config_pb2.BTN_RF3)
        mode.applicable_backends.append(self.config_pb2.COMMS_BACKEND_GAMECUBE)
        backend = config.communication_backend_configs.add()
        backend.backend_id = self.config_pb2.COMMS_BACKEND_GAMECUBE
        backend.default_mode_config = 1
        backend.activation_binding.append(self.config_pb2.BTN_RF2)
        config.default_backend_config = 1
        return config

    def device_info(self) -> bytes:
        message = self.config_pb2.DeviceInfo()
        message.firmware_name = "Glyph"
        message.firmware_version = operator.CANDIDATE_SHA[:7]
        message.device_name = "Glyph Mk6"
        return operator.deterministic(message)

    def metadata_and_plan(self, root: Path, baseline: bytes, intended: bytes) -> tuple[Path, Path]:
        metadata = root / "identity-status-snapshot.json"
        plan = root / "temporary-13-ultimate-plan.json"
        operator.dump_json(
            metadata,
            {
                "schema_name": "gp_config_010_recovery_capture",
                "protocol_version": operator.PROTOCOL_VERSION,
                "raw_config_payload_sha256": operator.sha256(baseline),
                "device_info": {"device_name": "Glyph Mk6"},
            },
        )
        operator.dump_json(
            plan,
            {
                "schema_name": "gp_config_010_temporary_13_ultimate_plan",
                "protocol_version": operator.PROTOCOL_VERSION,
                "owner_original_payload_sha256": operator.sha256(baseline),
                "temporary_payload_sha256": operator.sha256(intended),
            },
        )
        return metadata, plan

    def current_state_metadata(self, root: Path, payload: bytes) -> Path:
        path = root / "current-state-metadata.json"
        operator.dump_json(
            path,
            {
                "schema_name": "gp_config_010_recovery_current_state",
                "protocol_version": operator.PROTOCOL_VERSION,
                "raw_config_payload_sha256": operator.sha256(payload),
            },
        )
        return path

    def test_plan_has_exact_thirteen_and_preserves_top_level(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = self.base_config()
            source = root / "original.bin"
            source.write_bytes(operator.deterministic(original))
            args = argparse.Namespace(original_payload=source, output_dir=root / "plan")
            operator.make_plan(args, self.config_pb2, self.json_format)
            plan = json.loads((root / "plan/temporary-13-ultimate-plan.json").read_text())
            self.assertEqual(plan["game_mode_configs_count"], 13)
            self.assertTrue(all(plan["proofs"].values()))
            self.assertEqual([row["config_index"] for row in plan["profiles"]], list(range(13)))

    def test_backend_binding_conflict_stops(self) -> None:
        config = self.base_config()
        config.communication_backend_configs[0].activation_binding.append(self.config_pb2.BTN_LF6)
        with self.assertRaises(operator.ToolError):
            operator.validate_binding_set(config, self.config_pb2)

    def test_transaction_success_records_all_stages(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = operator.deterministic(self.base_config())
            intended_message = self.base_config()
            intended_message.game_mode_configs[0].name = "Changed"
            intended = operator.deterministic(intended_message)
            (root / "baseline.bin").write_bytes(baseline)
            (root / "intended.bin").write_bytes(intended)
            result_path = root / "result.json"
            metadata, plan = self.metadata_and_plan(root, baseline, intended)
            fake = FakePort(baseline, intended, self.device_info())
            args = argparse.Namespace(
                expected_current=root / "baseline.bin",
                intended_payload=root / "intended.bin",
                result_out=result_path,
                operation="write",
                port="/dev/fake",
                timeout_sec=1.0,
                capture_metadata=metadata,
                current_state_metadata=metadata,
                plan=plan,
            )
            with mock.patch.object(operator, "open_port", return_value=fake):
                operator.transaction(args, self.config_pb2)
            result = json.loads(result_path.read_text())
            self.assertEqual(result["outcome"], "SUCCESS_RESPONSE_AND_EXACT_READBACK")
            self.assertEqual([item["stage"] for item in result["transaction_stages"]], list(operator.STAGES))
            self.assertFalse(result["device_state_ambiguous"])
            self.assertTrue(fake.closed)

    def test_write_failure_is_ambiguous_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = operator.deterministic(self.base_config())
            (root / "baseline.bin").write_bytes(payload)
            (root / "intended.bin").write_bytes(payload)
            result_path = root / "result.json"
            metadata, plan = self.metadata_and_plan(root, payload, payload)
            fake = FakePort(payload, payload, self.device_info(), fail_write=True)
            args = argparse.Namespace(
                expected_current=root / "baseline.bin",
                intended_payload=root / "intended.bin",
                result_out=result_path,
                operation="write",
                port="/dev/fake",
                timeout_sec=1.0,
                capture_metadata=metadata,
                current_state_metadata=metadata,
                plan=plan,
            )
            with mock.patch.object(operator, "open_port", return_value=fake):
                with self.assertRaises(operator.ToolError):
                    operator.transaction(args, self.config_pb2)
            result = json.loads(result_path.read_text())
            self.assertEqual(result["outcome"], "TRANSPORT_OR_FOLLOWUP_ERROR_STOP")
            self.assertTrue(result["partial_write_ambiguous"])
            self.assertTrue(result["device_state_ambiguous"])

    def test_restore_is_bound_to_temp_and_exact_original(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = operator.deterministic(self.base_config())
            changed = self.base_config()
            changed.game_mode_configs[0].name = "Temporary"
            temporary = operator.deterministic(changed)
            drifted = self.base_config()
            drifted.game_mode_configs[0].name = "AmbiguousPersistedState"
            current = operator.deterministic(drifted)
            (root / "temporary.bin").write_bytes(current)
            (root / "original.bin").write_bytes(original)
            metadata, plan = self.metadata_and_plan(root, original, temporary)
            current_state = self.current_state_metadata(root, current)
            result_path = root / "restore.json"
            fake = FakePort(current, original, self.device_info())
            args = argparse.Namespace(
                expected_current=root / "temporary.bin",
                intended_payload=root / "original.bin",
                result_out=result_path,
                operation="restore",
                port="/dev/fake",
                timeout_sec=1.0,
                capture_metadata=metadata,
                current_state_metadata=current_state,
                plan=plan,
            )
            with mock.patch.object(operator, "open_port", return_value=fake):
                operator.transaction(args, self.config_pb2)
            self.assertEqual(
                json.loads(result_path.read_text())["outcome"],
                "SUCCESS_RESPONSE_AND_EXACT_READBACK",
            )

    def test_wrong_plan_rejected_before_device_open(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = operator.deterministic(self.base_config())
            temporary = original + b"\x00"
            (root / "original.bin").write_bytes(original)
            (root / "temporary.bin").write_bytes(original)
            metadata, plan = self.metadata_and_plan(root, original, temporary)
            args = argparse.Namespace(
                expected_current=root / "original.bin",
                intended_payload=root / "temporary.bin",
                result_out=root / "result.json",
                operation="write",
                port="/dev/fake",
                timeout_sec=1.0,
                capture_metadata=metadata,
                current_state_metadata=metadata,
                plan=plan,
            )
            with mock.patch.object(operator, "open_port") as open_mock:
                with self.assertRaises(operator.ToolError):
                    operator.transaction(args, self.config_pb2)
                open_mock.assert_not_called()

    def test_full_write_timeout_is_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = operator.deterministic(self.base_config())
            changed = self.base_config()
            changed.game_mode_configs[0].name = "Temporary"
            temporary = operator.deterministic(changed)
            (root / "original.bin").write_bytes(original)
            (root / "temporary.bin").write_bytes(temporary)
            metadata, plan = self.metadata_and_plan(root, original, temporary)
            result_path = root / "result.json"
            fake = FakePort(original, temporary, self.device_info(), fail_after_full_write=True)
            args = argparse.Namespace(
                expected_current=root / "original.bin",
                intended_payload=root / "temporary.bin",
                result_out=result_path,
                operation="write",
                port="/dev/fake",
                timeout_sec=1.0,
                capture_metadata=metadata,
                current_state_metadata=metadata,
                plan=plan,
            )
            with mock.patch.object(operator, "open_port", return_value=fake):
                with self.assertRaises(operator.ToolError):
                    operator.transaction(args, self.config_pb2)
            result = json.loads(result_path.read_text())
            self.assertTrue(result["full_host_write_completed"])
            self.assertTrue(result["device_state_ambiguous"])
            self.assertEqual(result["outcome"], "TRANSPORT_OR_FOLLOWUP_ERROR_STOP")

    def test_readback_mismatch_stops(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = operator.deterministic(self.base_config())
            changed = self.base_config()
            changed.game_mode_configs[0].name = "Temporary"
            temporary = operator.deterministic(changed)
            (root / "original.bin").write_bytes(original)
            (root / "temporary.bin").write_bytes(temporary)
            metadata, plan = self.metadata_and_plan(root, original, temporary)
            result_path = root / "result.json"
            fake = FakePort(original, temporary, self.device_info(), readback=original)
            args = argparse.Namespace(
                expected_current=root / "original.bin",
                intended_payload=root / "temporary.bin",
                result_out=result_path,
                operation="write",
                port="/dev/fake",
                timeout_sec=1.0,
                capture_metadata=metadata,
                current_state_metadata=metadata,
                plan=plan,
            )
            with mock.patch.object(operator, "open_port", return_value=fake):
                with self.assertRaises(operator.ToolError):
                    operator.transaction(args, self.config_pb2)
            result = json.loads(result_path.read_text())
            self.assertEqual(result["outcome"], "READBACK_MISMATCH_STOP")
            self.assertTrue(result["device_state_ambiguous"])


if __name__ == "__main__":
    unittest.main()
