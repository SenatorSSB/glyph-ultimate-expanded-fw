#!/usr/bin/env python3
"""Load-bearing stdlib-only contract check for GP-CONFIG-007."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPERATOR = ROOT / "tools/gp_config_005_hw_test.py"
SERIAL = ROOT / "tools/glyph_serial_config_tool.py"
TESTS = ROOT / "tools/test_gp_config_005_hw_test.py"
DOC = ROOT / "docs/runtime_config/gp_config_007_transaction_stage_schema.md"

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
BOOLEANS = set(STAGES) | {"sent", "partial_write_ambiguous"}


def fail(message: str) -> None:
    raise AssertionError(message)


def cobs_encode(payload: bytes) -> bytes:
    out = bytearray([0])
    code_index = 0
    code = 1
    for value in payload:
        if value == 0:
            out[code_index] = code
            code_index = len(out)
            out.append(0)
            code = 1
        else:
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


def valid_result(prefix_len: int = 0) -> dict[str, object]:
    names = list(STAGES[:prefix_len])
    complete = "full_host_write_completed" in names
    return {
        "schema_name": "gp_config_005_operator_result",
        "schema_version": 2,
        "protocol_version": "GP_CONFIG_005_HW_V1",
        "candidate_git_sha": "437f87e8086a50f0dfbd834176b80d245c1ed307",
        "artifact_sha256": "650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44",
        "hardware_evidence_generated": False,
        "tests": [],
        "valid_update": {
            "transaction_stage": names[-1] if names else "not_started",
            "transaction_stages": [{"stage": name, "at_utc": "2026-01-01T00:00:00+00:00"} for name in names],
            **{name: name in names for name in STAGES},
            "sent": complete,
            "partial_write_ambiguous": "write_attempted" in names and not complete,
            "mechanical_outcome": "SUCCESS_RESPONSE_AND_RESPONSIVE" if prefix_len == len(STAGES) else "NOT_RUN",
            "followup_responsive": prefix_len == len(STAGES),
            "response": {"command": "CMD_SUCCESS"} if prefix_len == len(STAGES) else None,
            "followup": {"response": {"command": "CMD_GET_CONFIG"}} if prefix_len == len(STAGES) else None,
            "unexpected_error": False,
            "post_update_get_config_matches_sent_payload": prefix_len == len(STAGES),
            "human_reboot_observation": None,
            "human_controller_display_smoke": None,
        },
    }


def validate_contract(value: dict[str, object]) -> None:
    if value.get("schema_version") != 2:
        fail("new results must use schema_version 2")
    update = value.get("valid_update")
    if not isinstance(update, dict):
        fail("valid_update must be an object")
    stages = update.get("transaction_stages")
    if not isinstance(stages, list):
        fail("transaction_stages must be a list")
    names: list[str] = []
    for item in stages:
        if not isinstance(item, dict) or set(item) != {"stage", "at_utc"}:
            fail("stage records must have exactly stage and at_utc")
        name = item["stage"]
        stamp = item["at_utc"]
        if not isinstance(name, str) or name in names or name not in STAGES:
            fail("stage list contains an unknown or duplicate stage")
        if not isinstance(stamp, str):
            fail("stage timestamp must be a string")
        try:
            parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise AssertionError("stage timestamp is not ISO-8601") from exc
        if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
            fail("stage timestamp must be UTC")
        names.append(name)
    if names != list(STAGES[: len(names)]):
        fail("stage list must be an exact prefix")
    if update.get("transaction_stage") != (names[-1] if names else "not_started"):
        fail("transaction_stage mismatch")
    for name in STAGES:
        if update.get(name) is not (name in names):
            fail(f"boolean mismatch for {name}")
    if update.get("sent") is not update.get("full_host_write_completed"):
        fail("sent/full_host_write_completed mismatch")
    if update.get("partial_write_ambiguous") is not (
        "write_attempted" in names and "full_host_write_completed" not in names
    ):
        fail("partial-write ambiguity mismatch")
    outcome = update.get("mechanical_outcome")
    if not names:
        if outcome != "NOT_RUN" and not (isinstance(outcome, str) and outcome.startswith("NOT_SENT_")):
            fail("empty transaction outcome mismatch")
    elif len(names) == 2:
        if outcome != "BASELINE_DRIFT_STOP":
            fail("baseline-drift outcome mismatch")
    elif len(names) == 8:
        if outcome != "UNEXPECTED_VALID_UPDATE_RESPONSE_STOP":
            fail("unexpected-response outcome mismatch")
    elif len(names) == len(STAGES):
        if outcome not in {"SUCCESS_RESPONSE_AND_RESPONSIVE", "POST_UPDATE_PERSISTED_READBACK_MISMATCH_STOP"}:
            fail("complete transaction outcome mismatch")
    elif outcome != "TRANSPORT_OR_FOLLOWUP_ERROR_STOP":
        fail("incomplete transaction outcome mismatch")
    response = update.get("response")
    followup = update.get("followup")
    unexpected_error = update.get("unexpected_error")
    followup_responsive = update.get("followup_responsive")
    readback_matches = update.get("post_update_get_config_matches_sent_payload")
    has_error = "error" in update
    if len(names) in {0, 1, 2, 3, 4, 5, 6, 7} and response is not None:
        fail("response present before decode")
    if outcome == "NOT_RUN" or (isinstance(outcome, str) and outcome.startswith("NOT_SENT_")):
        if response is not None or followup is not None or unexpected_error is not False or followup_responsive is not False or readback_matches is not False or has_error:
            fail("not-run fields mismatch")
    if outcome == "BASELINE_DRIFT_STOP":
        if not has_error or response is not None or followup is not None or unexpected_error is not False or followup_responsive is not False or readback_matches is not False:
            fail("baseline-drift fields mismatch")
    if outcome == "TRANSPORT_OR_FOLLOWUP_ERROR_STOP":
        if not has_error or unexpected_error is not False or followup is not None or followup_responsive is not False or readback_matches is not False:
            fail("transport fields mismatch")
    if len(names) == 8:
        if not isinstance(response, dict) or response.get("command") == "CMD_SUCCESS":
            fail("unexpected response shape")
        if update.get("unexpected_error") is not (response.get("command") == "CMD_ERROR"):
            fail("unexpected response error flag mismatch")
        if followup is not None or followup_responsive is not False or readback_matches is not False or has_error:
            fail("unexpected response has follow-up")
    if len(names) == 9:
        if not isinstance(response, dict) or response.get("command") != "CMD_SUCCESS":
            fail("follow-up timeout response mismatch")
        if followup is not None or followup_responsive is not False or readback_matches is not False or not has_error:
            fail("follow-up timeout has follow-up")
    if len(names) == len(STAGES):
        if not isinstance(response, dict) or response.get("command") != "CMD_SUCCESS":
            fail("complete response mismatch")
        if not isinstance(followup, dict) or followup_responsive is not True:
            fail("complete follow-up mismatch")
    if outcome == "SUCCESS_RESPONSE_AND_RESPONSIVE":
        if (
            names != list(STAGES)
            or followup_responsive is not True
            or readback_matches is not True
            or has_error
            or unexpected_error is not False
        ):
            fail("success outcome is not a complete transaction")
    if outcome == "POST_UPDATE_PERSISTED_READBACK_MISMATCH_STOP" and (readback_matches is not False or not has_error or unexpected_error is not False):
        fail("readback mismatch outcome requires a mismatching persisted readback")


def check_source_contract() -> None:
    operator = OPERATOR.read_text(encoding="utf-8")
    serial = SERIAL.read_text(encoding="utf-8")
    tests = TESTS.read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    required_operator = [
        "RESULT_SCHEMA_VERSION = 2",
        "TRANSACTION_STAGE_ORDER = (",
        "result valid_update.transaction_stages must be an exact ordered prefix",
        "result valid_update.sent must match full_host_write_completed",
        "result valid_update.partial_write_ambiguous is inconsistent with write stages",
        "datetime.fromisoformat",
    ]
    required_serial = [
        "raw_packet = bytes([command_id]) + payload",
        "encoded = cobs_encode(raw_packet)",
        'stage_callback("write_attempted")',
        'stage_callback("full_host_write_completed")',
        'stage_callback("awaiting_response")',
        'stage_callback("response_received")',
    ]
    required_tests = [
        "test_serial_transport_stage_callback_boundaries",
        "test_serial_transport_write_failure_does_not_claim_full_write",
        "test_serial_transport_decode_failure_records_received_not_decoded",
    ]
    for fragment in required_operator:
        if fragment not in operator:
            fail(f"operator source contract missing: {fragment}")
    for fragment in required_serial:
        if fragment not in serial:
            fail(f"serial boundary contract missing: {fragment}")
    for fragment in required_tests:
        if fragment not in tests:
            fail(f"focused test seam missing: {fragment}")
    for fragment in ("schema version 2", "historical GP-CONFIG-005", "COBS bytes", "persistence guarantees"):
        if fragment not in doc:
            fail(f"current host schema contract missing: {fragment}")
    if cobs_encode(bytes([4, 0])).hex() != "02040100":
        fail("CMD_SET_CONFIG COBS request vector changed")
    if "bytes([command_id]) + payload" not in serial:
        fail("transport request byte construction changed")


def adversarial_tests() -> None:
    baseline = valid_result(len(STAGES))
    validate_contract(baseline)
    mutations: list[tuple[str, dict[str, object]]] = []
    for index in range(1, len(STAGES)):
        candidate = valid_result(index)
        candidate["valid_update"]["mechanical_outcome"] = "NOT_RUN"  # type: ignore[index]
        mutations.append((f"prefix-{index}-wrong-outcome", candidate))
    bad = copy.deepcopy(baseline)
    bad["schema_version"] = 1
    mutations.append(("historical-v1", bad))
    bad = copy.deepcopy(baseline)
    bad["valid_update"]["transaction_stages"] = list(reversed(bad["valid_update"]["transaction_stages"]))  # type: ignore[index]
    mutations.append(("reversed-stages", bad))
    bad = copy.deepcopy(baseline)
    bad["valid_update"]["transaction_stages"].append({"stage": STAGES[-1], "at_utc": "2026-01-01T00:00:00+00:00"})  # type: ignore[index]
    mutations.append(("duplicate-stage", bad))
    bad = copy.deepcopy(baseline)
    bad["valid_update"]["response_received"] = False  # type: ignore[index]
    mutations.append(("boolean-mismatch", bad))
    bad = copy.deepcopy(baseline)
    bad["valid_update"]["sent"] = False  # type: ignore[index]
    mutations.append(("sent-mismatch", bad))
    bad = copy.deepcopy(baseline)
    bad["valid_update"]["post_update_get_config_matches_sent_payload"] = False  # type: ignore[index]
    mutations.append(("success-readback-mismatch", bad))
    bad = copy.deepcopy(baseline)
    bad["valid_update"]["mechanical_outcome"] = "POST_UPDATE_PERSISTED_READBACK_MISMATCH_STOP"  # type: ignore[index]
    mutations.append(("mismatch-outcome-with-match", bad))
    bad = copy.deepcopy(baseline)
    bad["valid_update"]["response"] = {"command": "CMD_ERROR"}  # type: ignore[index]
    mutations.append(("success-with-error-response", bad))
    bad = copy.deepcopy(baseline)
    bad["valid_update"]["transaction_stages"][0]["at_utc"] = "2026-01-01T00:00:00"  # type: ignore[index]
    mutations.append(("non-utc-timestamp", bad))
    for label, candidate in mutations:
        if label == "complete":
            validate_contract(candidate)
            continue
        try:
            validate_contract(candidate)
        except AssertionError:
            continue
        fail(f"adversarial mutation accepted: {label}")


def main() -> int:
    try:
        check_source_contract()
        adversarial_tests()
    except (AssertionError, OSError, UnicodeError) as exc:
        print(f"glyph_gp_config_007_transaction_stage_schema: FAIL: {exc}")
        return 1
    print("glyph_gp_config_007_transaction_stage_schema: PASS; schema=v2 stages=10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
