#!/usr/bin/env python3
"""Read-only, single-owner GP-BIND-003 A4 capture operator.

It opens the explicitly supplied normal-XInput CDC endpoint once at 115200 with
DTR asserted and RTS deasserted, records every received byte for 90 seconds,
and writes exactly the two fixed identity frames frozen by the companion
gap-completion packet.  It has no Configurator, ProfileStore, reset, flash or
generic-command surface.
"""
from __future__ import annotations

import argparse
import json
import struct
import time
from pathlib import Path

MAGIC = bytes((0xA5, 0x47, 0x52, 0x49))


def request(token: int) -> bytes:
    if token not in TOKENS:
        raise ValueError("packet admits only the two frozen nonzero tokens")
    return MAGIC + struct.pack("<BBHQ", 1, 1, 16, token)

TOKENS = (0x4750423030330101, 0x4750423030330102)
CAPTURE_SECONDS = 90.0
SEND_AT_SECONDS = (10.0, 40.0)
EXPECTED_DIGEST = bytes.fromhex("d12805847da6f8f07096842cb0c7ce275c1606f911a1f5efd188bb9aeaf2b384")


def validate_frame(frame: bytes, expected_token: int | None = None) -> dict:
    if len(frame) != 72 or frame[:8] != MAGIC + bytes((1, 2, 72, 0)):
        raise ValueError("invalid identity response header")
    token, status, backend, row, reference, incarnation, active_id, revision, schema = struct.unpack_from(
        "<QBBHIIIII", frame, 8)
    if token not in TOKENS or (expected_token is not None and token != expected_token):
        raise ValueError("unexpected identity response token")
    if status != 0 or backend != 2:
        raise ValueError("identity response is not persisted XInput")
    if (row, reference, incarnation, active_id, revision, schema) != (3, 4, 1, 4, 1, 3):
        raise ValueError("identity response differs from frozen active identity")
    if frame[40:] != EXPECTED_DIGEST:
        raise ValueError("identity response differs from frozen payload digest")
    return {"token": token, "response_hex": frame.hex()}


class StreamAudit:
    """Strictly consume all bytes before any subsequent request is allowed."""
    def __init__(self) -> None:
        self.pending = bytearray()
        self.viewer_records = 0
        self.identity_responses: list[dict] = []
        self.expected_token: int | None = None

    def allow(self, token: int) -> None:
        if self.expected_token is not None:
            raise ValueError("previous identity response is still pending")
        self.expected_token = token

    def feed(self, data: bytes) -> None:
        self.pending.extend(data)
        while self.pending:
            if self.pending[:4] == MAGIC:
                if len(self.pending) < 72: return
                if self.expected_token is None:
                    raise ValueError("unexpected identity response")
                checked = validate_frame(bytes(self.pending[:72]), self.expected_token)
                self.identity_responses.append(checked)
                self.expected_token = None
                del self.pending[:72]
                continue
            if len(self.pending) < 25: return
            record = self.pending[:25]
            if record[-1:] != b"\n" or any(value not in (48, 49) for value in record[:-1]):
                raise ValueError("unknown or malformed viewer record")
            self.viewer_records += 1
            del self.pending[:25]

    def finish(self) -> dict:
        if self.pending: raise ValueError("partial viewer or identity response in capture")
        if self.expected_token is not None: raise ValueError("missing fixed identity response")
        if {item["token"] for item in self.identity_responses} != set(TOKENS):
            raise ValueError("missing fixed identity response")
        return {"viewer_records": self.viewer_records, "identity_responses": self.identity_responses}


def audit(raw: bytes) -> dict:
    checker = StreamAudit(); checker.feed(raw); return checker.finish()


def pump(wire, raw: bytearray, checker: StreamAudit) -> None:
    data = wire.read(max(1, min(256, wire.in_waiting)))
    raw.extend(data)
    checker.feed(data)


def wait_until(wire, raw: bytearray, checker: StreamAudit, deadline: float) -> None:
    while time.monotonic() < deadline:
        pump(wire, raw, checker)


def require_complete_boundary(wire, raw: bytearray, checker: StreamAudit) -> None:
    """Do not transmit while a received viewer/frame prefix remains unresolved."""
    deadline = time.monotonic() + 0.25
    while checker.pending and time.monotonic() < deadline:
        pump(wire, raw, checker)
    if checker.pending:
        raise ValueError("partial record pending before fixed identity request")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--raw-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    parser.add_argument("--session", required=True)
    args = parser.parse_args()
    if args.raw_out.exists() or args.report_out.exists():
        parser.error("refuse to overwrite evidence output")
    import serial
    raw = bytearray()
    sent: list[dict] = []
    try:
        with serial.Serial(port=None, baudrate=115200, timeout=0.05, write_timeout=0.1) as wire:
            wire.dtr = True
            wire.rts = False
            wire.port = args.port
            wire.open()
            started = time.monotonic()
            checker = StreamAudit()
            wait_until(wire, raw, checker, started + SEND_AT_SECONDS[0])
            require_complete_boundary(wire, raw, checker)
            first = request(TOKENS[0])
            if wire.write(first) != len(first): raise ValueError("partial first fixed identity request write")
            sent.append({"at_seconds": SEND_AT_SECONDS[0], "token": TOKENS[0], "request_hex": first.hex()})
            checker.allow(TOKENS[0])
            wait_until(wire, raw, checker, started + 20.0)
            if checker.expected_token is not None: raise ValueError("missing first fixed identity response")
            wait_until(wire, raw, checker, started + SEND_AT_SECONDS[1])
            require_complete_boundary(wire, raw, checker)
            second = request(TOKENS[1])
            if wire.write(second) != len(second): raise ValueError("partial second fixed identity request write")
            sent.append({"at_seconds": SEND_AT_SECONDS[1], "token": TOKENS[1], "request_hex": second.hex()})
            checker.allow(TOKENS[1])
            wait_until(wire, raw, checker, started + 50.0)
            if checker.expected_token is not None: raise ValueError("missing second fixed identity response")
            wait_until(wire, raw, checker, started + CAPTURE_SECONDS)
    finally:
        args.raw_out.write_bytes(raw)
    result = checker.finish()
    args.report_out.write_text(json.dumps({
        "session": args.session,
        "observation": "current_session_only",
        "capture_seconds": CAPTURE_SECONDS,
        "fixed_requests": sent,
        "raw_bytes": len(raw),
        **result,
    }, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
