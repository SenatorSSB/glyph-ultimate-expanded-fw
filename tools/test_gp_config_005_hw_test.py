#!/usr/bin/env python3
"""Host-only tests for the GP-CONFIG-005 operator utility."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from google.protobuf.message import DecodeError

import gp_config_005_hw_test as operator
from glyph_serial_config_tool import ToolError, cobs_encode


class MockTransport:
    def __init__(self, responses: list[tuple[int, bytes] | Exception]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[int, bytes]] = []
        self.is_open = True

    def transact(self, command_id: int, payload: bytes) -> tuple[int, bytes]:
        self.calls.append((command_id, payload))
        if not self.responses:
            raise AssertionError("mock transport received an unexpected transaction")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            self.is_open = False
            raise response
        return response


class OperatorUtilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config_pb2, cls.json_format, cls.proto_path = operator.load_modules()

    def make_baseline(self):
        config = self.config_pb2.Config()
        mode = config.game_mode_configs.add()
        mode.mode_id = self.config_pb2.MODE_ULTIMATE
        mode.name = "Operator baseline"
        backend = config.communication_backend_configs.add()
        backend.backend_id = self.config_pb2.COMMS_BACKEND_DINPUT
        backend.default_mode_config = 1
        config.default_backend_config = 1
        config.default_usb_backend_config = 1
        config.rgb_brightness = 128
        return config

    def make_capture(self, baseline, payload: bytes) -> dict:
        return operator.make_capture(
            payload,
            baseline,
            self.json_format,
            port="/dev/mock-explicit-selection",
            device_info={
                "firmware_name": "Glyph",
                "firmware_version": "test",
                "device_name": "mock",
            },
        )

    def make_device_info_payload(self) -> bytes:
        info = self.config_pb2.DeviceInfo()
        info.firmware_name = "Glyph"
        info.firmware_version = operator.EXPECTED_DEVICE_FIRMWARE_VERSION
        info.device_name = "glyph_mk6"
        return info.SerializeToString(deterministic=True)

    def test_pinned_protocol_and_artifact_identity(self) -> None:
        self.assertEqual(operator.PROTOCOL_VERSION, "GP_CONFIG_005_HW_V1")
        self.assertEqual(
            operator.CANDIDATE_GIT_SHA,
            "437f87e8086a50f0dfbd834176b80d245c1ed307",
        )
        self.assertEqual(
            operator.ARTIFACT_SHA256,
            "650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44",
        )
        identity = operator.verify_repository_identity(require_artifact=True)
        self.assertTrue(identity["verified"])
        self.assertTrue(identity["artifact"]["matches_expected"])
        self.assertEqual(identity["config_proto_sha256"], operator.CONFIG_PROTO_SHA256)

    def test_identity_verifier_refuses_protocol_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            protocol = root / operator.PROTOCOL_RELATIVE_PATH
            protocol.parent.mkdir(parents=True)
            protocol.write_text("wrong protocol\n", encoding="utf-8")
            with self.assertRaisesRegex(ToolError, "protocol identity mismatch"):
                operator.verify_repository_identity(root, require_artifact=False)

    def test_all_rejection_mutations_are_minimal_deterministic_and_encodable(self) -> None:
        baseline = self.make_baseline()
        cases = operator.build_rejection_cases(baseline, self.config_pb2)
        self.assertEqual(
            [case.id for case in cases],
            [
                "malformed_decode",
                "invalid_default_backend_index",
                "invalid_backend_default_mode_reference",
                "invalid_keyboard_reference_type",
                "invalid_custom_reference_type",
                "keyboard_index_out_of_range",
                "custom_index_out_of_range",
            ],
        )
        expected_paths = {
            "malformed_decode": [],
            "invalid_default_backend_index": ["default_backend_config"],
            "invalid_backend_default_mode_reference": [
                "communication_backend_configs[0].default_mode_config"
            ],
            "invalid_keyboard_reference_type": [
                "game_mode_configs[0].keyboard_mode_config"
            ],
            "invalid_custom_reference_type": [
                "game_mode_configs[0].custom_mode_config"
            ],
            "keyboard_index_out_of_range": [
                "game_mode_configs[0].mode_id",
                "game_mode_configs[0].keyboard_mode_config",
            ],
            "custom_index_out_of_range": [
                "game_mode_configs[0].mode_id",
                "game_mode_configs[0].custom_mode_config",
            ],
        }
        expected_branches = {
            "malformed_decode": "pb_decode(Config_fields) failure",
            "invalid_default_backend_index": (
                "default_backend_config > communication_backend_configs_count"
            ),
            "invalid_backend_default_mode_reference": (
                "communication_backend_configs[i].default_mode_config > game_mode_configs_count"
            ),
            "invalid_keyboard_reference_type": (
                "keyboard_mode_config > 0 while mode_id != MODE_KEYBOARD"
            ),
            "invalid_custom_reference_type": (
                "custom_mode_config > 0 while mode_id != MODE_CUSTOM"
            ),
            "keyboard_index_out_of_range": (
                "keyboard_mode_config > keyboard_modes_count after keyboard type check"
            ),
            "custom_index_out_of_range": (
                "custom_mode_config > custom_modes_count after custom type check"
            ),
        }
        for case in cases:
            with self.subTest(case=case.id):
                self.assertEqual(
                    [change["path"] for change in case.changed_fields],
                    expected_paths[case.id],
                )
                self.assertEqual(case.target_validation_branch, expected_branches[case.id])
                self.assertEqual(case.expected_response_command, "CMD_ERROR")
                if case.id == "malformed_decode":
                    with self.assertRaises(DecodeError):
                        self.config_pb2.Config().ParseFromString(case.payload)
                else:
                    decoded = self.config_pb2.Config()
                    decoded.ParseFromString(case.payload)
                    self.assertEqual(decoded.SerializeToString(deterministic=True), case.payload)
                framed = operator.payload_record(operator.CMD_SET_CONFIG, case.payload)
                self.assertTrue(framed["cobs_framed_packet_hex"].endswith("00"))

        second = operator.build_rejection_cases(baseline, self.config_pb2)
        self.assertEqual([case.payload for case in cases], [case.payload for case in second])

    def test_bound_mutations_use_existing_typed_modes_when_available(self) -> None:
        baseline = self.make_baseline()
        keyboard = baseline.game_mode_configs.add()
        keyboard.mode_id = self.config_pb2.MODE_KEYBOARD
        custom = baseline.game_mode_configs.add()
        custom.mode_id = self.config_pb2.MODE_CUSTOM
        baseline.communication_backend_configs[0].default_mode_config = 1
        cases = {case.id: case for case in operator.build_rejection_cases(baseline, self.config_pb2)}
        self.assertEqual(
            [item["path"] for item in cases["keyboard_index_out_of_range"].changed_fields],
            ["game_mode_configs[1].keyboard_mode_config"],
        )
        self.assertEqual(
            [item["path"] for item in cases["custom_index_out_of_range"].changed_fields],
            ["game_mode_configs[2].custom_mode_config"],
        )

    def test_preexisting_invalid_baseline_is_rejected_before_plan_generation(self) -> None:
        baseline = self.make_baseline()
        baseline.default_backend_config = 2
        with self.assertRaisesRegex(ToolError, "already fails the candidate validation order"):
            operator.build_rejection_cases(baseline, self.config_pb2)

    def test_malformed_payload_reaches_setconfig_with_valid_framing(self) -> None:
        baseline = self.make_baseline()
        malformed = operator.build_rejection_cases(baseline, self.config_pb2)[0]
        framed = cobs_encode(bytes([operator.CMD_SET_CONFIG]) + malformed.payload)
        decoded = operator.cobs_decode(framed)
        self.assertEqual(decoded[0], operator.CMD_SET_CONFIG)
        self.assertEqual(decoded[1:], bytes.fromhex("00"))

    def test_response_parser_error_success_unexpected_and_truncated(self) -> None:
        error = operator.parse_framed_response(
            cobs_encode(bytes([operator.CMD_ERROR]) + b"expected error"),
            [operator.CMD_ERROR],
        )
        self.assertEqual(error["command"], "CMD_ERROR")
        self.assertEqual(error["text"], "expected error")
        self.assertFalse(error["unexpected_command"])

        success = operator.parse_framed_response(
            cobs_encode(bytes([operator.CMD_SUCCESS])),
            [operator.CMD_SUCCESS],
        )
        self.assertEqual(success["command"], "CMD_SUCCESS")
        self.assertFalse(success["unexpected_command"])

        unexpected = operator.parse_framed_response(
            cobs_encode(bytes([operator.CMD_SET_DEVICE_INFO])),
            [operator.CMD_ERROR, operator.CMD_SUCCESS],
        )
        self.assertTrue(unexpected["unexpected_command"])
        self.assertEqual(unexpected["command"], "CMD_SET_DEVICE_INFO")

        with self.assertRaisesRegex(ToolError, "missing null terminator"):
            operator.parse_framed_response(b"\x02\x05", [operator.CMD_ERROR])
        with self.assertRaisesRegex(ToolError, "no command byte"):
            operator.parse_framed_response(cobs_encode(b""), [operator.CMD_ERROR])

    def test_expected_rejection_records_followup_responsiveness(self) -> None:
        baseline = self.make_baseline()
        baseline_payload = operator.deterministic_payload(baseline)
        case = operator.build_rejection_cases(baseline, self.config_pb2)[1]
        transport = MockTransport(
            [
                (operator.CMD_ERROR, case.expected_error_text.encode("utf-8")),
                (operator.CMD_SET_DEVICE_INFO, self.make_device_info_payload()),
            ]
        )
        record = operator.execute_rejection_case(
            transport, case, baseline_payload, self.config_pb2
        )
        self.assertEqual(record["mechanical_outcome"], "EXPECTED_REJECTION_AND_RESPONSIVE")
        self.assertTrue(record["response_matches_expected"])
        self.assertTrue(record["connected_after"])
        self.assertTrue(record["followup_responsive"])
        self.assertEqual(record["followup"]["request_command"], "CMD_GET_DEVICE_INFO")
        self.assertEqual(
            [call[0] for call in transport.calls],
            [operator.CMD_SET_CONFIG, operator.CMD_GET_DEVICE_INFO],
        )
        self.assertTrue(
            record["followup"]["decoded_device_info"]["candidate_short_identity_matches"]
        )

    def test_device_info_requires_candidate_short_identity(self) -> None:
        info = self.config_pb2.DeviceInfo()
        info.firmware_name = "Glyph"
        info.firmware_version = "deadbee"
        info.device_name = "glyph_mk6"
        transport = MockTransport(
            [(operator.CMD_SET_DEVICE_INFO, info.SerializeToString(deterministic=True))]
        )
        with self.assertRaisesRegex(ToolError, "short identity mismatch"):
            operator.request_device_info(transport, self.config_pb2)

    def test_connection_loss_is_recorded_and_stops_suite(self) -> None:
        baseline = self.make_baseline()
        baseline_payload = operator.deterministic_payload(baseline)
        cases = operator.build_rejection_cases(baseline, self.config_pb2)
        transport = MockTransport([ToolError("connection lost")])
        records, complete = operator.execute_rejection_suite(
            transport, cases, baseline_payload, self.config_pb2
        )
        self.assertFalse(complete)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["mechanical_outcome"], "TRANSPORT_OR_FOLLOWUP_ERROR_STOP")
        self.assertFalse(records[0]["connected_after"])
        self.assertFalse(records[0]["followup_responsive"])

    def test_unexpected_success_stops_without_followup(self) -> None:
        baseline = self.make_baseline()
        baseline_payload = operator.deterministic_payload(baseline)
        case = operator.build_rejection_cases(baseline, self.config_pb2)[1]
        transport = MockTransport([(operator.CMD_SUCCESS, b"")])
        record = operator.execute_rejection_case(
            transport, case, baseline_payload, self.config_pb2
        )
        self.assertEqual(record["mechanical_outcome"], "UNEXPECTED_RESPONSE_STOP")
        self.assertTrue(record["unexpected_success"])
        self.assertFalse(record["followup_responsive"])
        self.assertEqual(len(transport.calls), 1)

    def test_valid_update_is_exactly_one_benign_field(self) -> None:
        baseline = self.make_baseline()
        candidate, metadata = operator.build_valid_update(baseline, self.config_pb2)
        self.assertEqual(metadata["field"], "rgb_brightness")
        self.assertEqual(metadata["changed_fields"], [
            {"path": "rgb_brightness", "before": 128, "after": 20}
        ])
        self.assertEqual(baseline.rgb_brightness, 128)
        self.assertEqual(candidate.rgb_brightness, 20)
        self.assertEqual(metadata["confirmation_token"], "SET_RGB_BRIGHTNESS_128_TO_20")

    def test_valid_update_is_never_sent_without_exact_confirmation(self) -> None:
        baseline = self.make_baseline()
        baseline_payload = operator.deterministic_payload(baseline)
        for token in (None, "", "YES", "SET_RGB_BRIGHTNESS_128_TO_30"):
            with self.subTest(token=token):
                transport = MockTransport([])
                record = operator.execute_valid_update(
                    transport,
                    baseline,
                    baseline_payload,
                    self.config_pb2,
                    confirmation_token=token,
                    rejection_observations_acknowledged=True,
                )
                self.assertFalse(record["sent"])
                self.assertEqual(record["mechanical_outcome"], "NOT_SENT_NO_CONFIRMATION")
                self.assertEqual(transport.calls, [])

    def test_valid_update_confirmation_checks_baseline_then_success_and_followup(self) -> None:
        baseline = self.make_baseline()
        baseline_payload = operator.deterministic_payload(baseline)
        candidate, metadata = operator.build_valid_update(baseline, self.config_pb2)
        candidate_payload = operator.deterministic_payload(candidate)
        transport = MockTransport(
            [
                (operator.CMD_SET_CONFIG, baseline_payload),
                (operator.CMD_SUCCESS, b""),
                (operator.CMD_SET_CONFIG, candidate_payload),
            ]
        )
        record = operator.execute_valid_update(
            transport,
            baseline,
            baseline_payload,
            self.config_pb2,
            confirmation_token=metadata["confirmation_token"],
            rejection_observations_acknowledged=True,
        )
        self.assertTrue(record["sent"])
        self.assertTrue(record["followup_responsive"])
        self.assertTrue(record["post_update_get_config_matches_sent_payload"])
        self.assertEqual(record["mechanical_outcome"], "SUCCESS_RESPONSE_AND_RESPONSIVE")
        self.assertEqual(
            [call[0] for call in transport.calls],
            [operator.CMD_GET_CONFIG, operator.CMD_SET_CONFIG, operator.CMD_GET_CONFIG],
        )

    def test_baseline_drift_prevents_valid_setconfig(self) -> None:
        baseline = self.make_baseline()
        baseline_payload = operator.deterministic_payload(baseline)
        _, metadata = operator.build_valid_update(baseline, self.config_pb2)
        transport = MockTransport([(operator.CMD_SET_CONFIG, b"different persisted payload")])
        record = operator.execute_valid_update(
            transport,
            baseline,
            baseline_payload,
            self.config_pb2,
            confirmation_token=metadata["confirmation_token"],
            rejection_observations_acknowledged=True,
        )
        self.assertFalse(record["sent"])
        self.assertEqual(record["mechanical_outcome"], "BASELINE_DRIFT_STOP")
        self.assertEqual([call[0] for call in transport.calls], [operator.CMD_GET_CONFIG])

    def test_post_success_persisted_readback_mismatch_is_a_hard_stop(self) -> None:
        baseline = self.make_baseline()
        baseline_payload = operator.deterministic_payload(baseline)
        _, metadata = operator.build_valid_update(baseline, self.config_pb2)
        transport = MockTransport(
            [
                (operator.CMD_SET_CONFIG, baseline_payload),
                (operator.CMD_SUCCESS, b""),
                (operator.CMD_SET_CONFIG, baseline_payload),
            ]
        )
        record = operator.execute_valid_update(
            transport,
            baseline,
            baseline_payload,
            self.config_pb2,
            confirmation_token=metadata["confirmation_token"],
            rejection_observations_acknowledged=True,
        )
        self.assertTrue(record["sent"])
        self.assertTrue(record["followup_responsive"])
        self.assertFalse(record["post_update_get_config_matches_sent_payload"])
        self.assertEqual(
            record["mechanical_outcome"],
            "POST_UPDATE_PERSISTED_READBACK_MISMATCH_STOP",
        )

    def test_valid_update_is_never_sent_without_rejection_observation_ack(self) -> None:
        baseline = self.make_baseline()
        baseline_payload = operator.deterministic_payload(baseline)
        _, metadata = operator.build_valid_update(baseline, self.config_pb2)
        transport = MockTransport([])
        record = operator.execute_valid_update(
            transport,
            baseline,
            baseline_payload,
            self.config_pb2,
            confirmation_token=metadata["confirmation_token"],
            rejection_observations_acknowledged=False,
        )
        self.assertFalse(record["sent"])
        self.assertEqual(
            record["mechanical_outcome"],
            "NOT_SENT_NO_REJECTION_OBSERVATION_ACKNOWLEDGEMENT",
        )
        self.assertEqual(transport.calls, [])

    def test_dry_run_performs_no_device_access(self) -> None:
        baseline = self.make_baseline()
        payload = operator.deterministic_payload(baseline)
        capture = self.make_capture(baseline, payload)
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_path = Path(temp_dir) / "capture.json"
            plan_path = Path(temp_dir) / "plan.json"
            capture_path.write_text(operator.json_dump(capture), encoding="utf-8")
            stdout = io.StringIO()
            with mock.patch.object(
                operator,
                "verify_repository_identity",
                return_value={"verified": True},
            ), mock.patch.object(
                operator,
                "open_transport",
                side_effect=AssertionError("dry-run attempted device access"),
            ), contextlib.redirect_stdout(stdout):
                status = operator.main(
                    [
                        "dry-run",
                        "--baseline",
                        str(capture_path),
                        "--plan-out",
                        str(plan_path),
                    ]
                )
            self.assertEqual(status, 0)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertTrue(plan["dry_run"])
            self.assertFalse(plan["device_access"])
            self.assertEqual(len(plan["rejection_cases"]), 7)
            self.assertIn("cobs_framed_packet_hex", stdout.getvalue())

    def test_valid_update_cli_without_both_tokens_never_opens_device(self) -> None:
        baseline = self.make_baseline()
        payload = operator.deterministic_payload(baseline)
        capture = self.make_capture(baseline, payload)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            capture_path = root / "capture.json"
            capture_path.write_text(operator.json_dump(capture), encoding="utf-8")
            result_path = root / "result.json"
            with mock.patch.object(
                operator,
                "verify_repository_identity",
                return_value={"verified": True},
            ), mock.patch.object(
                operator,
                "open_transport",
                side_effect=AssertionError("unconfirmed valid update opened a device"),
            ), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                status = operator.main(
                    [
                        "valid-update",
                        "--port",
                        "/dev/must-not-open",
                        "--baseline",
                        str(capture_path),
                        "--rejection-result",
                        str(root / "not-read-without-confirmation.json"),
                        "--result-out",
                        str(result_path),
                    ]
                )
            self.assertEqual(status, 1)
            result = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertFalse(result["valid_update"]["sent"])

    def test_capture_integrity_and_structured_result_schema(self) -> None:
        baseline = self.make_baseline()
        payload = operator.deterministic_payload(baseline)
        capture = self.make_capture(baseline, payload)
        operator.validate_capture(capture)
        result = operator.empty_result(
            {"selected_port": "/dev/mock-explicit-selection"}, capture
        )
        operator.validate_result_schema(result)
        self.assertIsNone(result["operator_assessment"])
        self.assertFalse(result["hardware_evidence_generated"])
        self.assertTrue(result["baseline_capture"]["not_live_ram_identity_proof"])
        broken = copy_result = json.loads(json.dumps(result))
        copy_result["operator_assessment"] = "PASS"
        with self.assertRaisesRegex(ToolError, "operator_assessment null"):
            operator.validate_result_schema(broken)

    def test_standalone_valid_update_requires_complete_matching_rejection_result(self) -> None:
        baseline = self.make_baseline()
        payload = operator.deterministic_payload(baseline)
        capture = self.make_capture(baseline, payload)
        result = operator.empty_result(
            {"selected_port": "/dev/mock-explicit-selection"}, capture
        )
        cases = operator.build_rejection_cases(baseline, self.config_pb2)
        result["tests"] = []
        for case in cases:
            result["tests"].append(
                {
                    "id": case.id,
                    "human_observation": None,
                    "target_validation_branch": case.target_validation_branch,
                    "changed_fields": case.changed_fields,
                    "source_baseline_payload_sha256": operator.sha256_bytes(payload),
                    "request": operator.payload_record(
                        operator.CMD_SET_CONFIG, case.payload
                    ),
                    "mechanical_outcome": "EXPECTED_REJECTION_AND_RESPONSIVE",
                    "response_matches_expected": True,
                    "unexpected_success": False,
                    "connected_after": True,
                    "followup_responsive": True,
                    "response": operator.response_record(
                        operator.CMD_ERROR, case.expected_error_text.encode("utf-8")
                    ),
                    "followup": {
                        "request_command": "CMD_GET_DEVICE_INFO",
                        "response": operator.response_record(
                            operator.CMD_SET_DEVICE_INFO,
                            self.make_device_info_payload(),
                        ),
                        "decoded_device_info": operator.decode_device_info_payload(
                            self.make_device_info_payload(), self.config_pb2
                        ),
                    },
                }
            )
        result["suite_mechanically_complete"] = True
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rejections.json"
            path.write_text(operator.json_dump(result), encoding="utf-8")
            loaded = operator.load_completed_rejection_result(
                path, capture, baseline, self.config_pb2
            )
            self.assertTrue(loaded["suite_mechanically_complete"])
            result["tests"][0]["followup_responsive"] = False
            path.write_text(operator.json_dump(result), encoding="utf-8")
            with self.assertRaisesRegex(ToolError, "not mechanically complete"):
                operator.load_completed_rejection_result(
                    path, capture, baseline, self.config_pb2
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
