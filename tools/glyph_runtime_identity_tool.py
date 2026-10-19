#!/usr/bin/env python3
"""Strict decoder/capture for the GP-BIND-003 identity-only CDC protocol.

No device is opened unless --port is supplied. This tool only sends the fixed
identity request; it has no Configurator write/reset or profile operations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import secrets
import struct
import time
from pathlib import Path

MAGIC = b'\xa5GRI'
DOMAIN = b'Glyph.RuntimeIdentity.UltimateProfile.v1\0'
STATUSES = ('persisted', 'no_primary', 'configurator', 'recovery', 'no_mode',
            'non_ultimate', 'source_fallback', 'embedded_legacy', 'store_unavailable',
            'object_mismatch', 'context_unavailable', 'digest_failure', 'snapshot_unavailable')

def request(token: int) -> bytes:
    if not 0 < token < 2**64:
        raise ValueError('token must be a nonzero uint64')
    return MAGIC + struct.pack('<BBHQ', 1, 1, 16, token)

def payload_digest(profile) -> str:
    return hashlib.sha256(DOMAIN + profile.SerializeToString(deterministic=True)).hexdigest()

class Decoder:
    def __init__(self, token: int):
        request(token)
        self.token, self.pending = token, bytearray()
        self.viewer_records, self.response = 0, None

    def feed(self, data: bytes) -> None:
        self.pending.extend(data)
        while self.pending:
            if self.pending[0] in (48, 49):
                if len(self.pending) < 25:
                    return
                frame = self.pending[:25]
                if any(b not in (48, 49) for b in frame[:24]) or frame[24] != 10:
                    raise ValueError('invalid/ambiguous viewer record')
                del self.pending[:25]
                self.viewer_records += 1
                continue
            if self.pending[0] != MAGIC[0]:
                raise ValueError('unknown/ambiguous stream bytes')
            if len(self.pending) < 8:
                return
            if self.pending[:8] != MAGIC + struct.pack('<BBH', 1, 2, 72):
                raise ValueError('invalid identity header/version/kind/length')
            if len(self.pending) < 72:
                return
            frame = bytes(self.pending[:72]); del self.pending[:72]
            token, status, backend, row, requested, incarnation, ident, revision, schema = struct.unpack_from('<QBBHIIIII', frame, 8)
            if token != self.token or self.response is not None or status >= len(STATUSES):
                raise ValueError('wrong token, duplicate response or unknown status')
            if status and any(frame[24:]):
                raise ValueError('neutral status carries persistent identity')
            if status == 0 and (not all((incarnation, ident, revision, schema)) or not any(frame[40:])):
                raise ValueError('incomplete persisted identity')
            self.response = dict(protocol_version=1, token=token, status=STATUSES[status],
                                 primary_backend=backend, context_row=row, requested_reference=requested,
                                 incarnation=incarnation, active_id=ident, active_revision=revision,
                                 schema_version=schema, payload_sha256=frame[40:].hex() if status == 0 else None)

    def finish(self) -> dict:
        if self.pending or self.response is None:
            raise ValueError('partial/timeout/no identity response')
        return dict(self.response, viewer_records=self.viewer_records)

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--capture', type=Path, help='decode an already retained raw XInput capture')
    source.add_argument('--port', help='explicit current XInput CDC port; sends identity request only')
    p.add_argument('--token', type=lambda s: int(s, 0))
    p.add_argument('--session', required=True, help='external boot/session label; never inferred from token')
    p.add_argument('--timeout', type=float, default=2.0)
    a = p.parse_args()
    if not 0 < a.timeout <= 10: p.error('timeout must be in (0,10] seconds')
    if a.capture and a.token is None: p.error('--capture requires its exact --token')
    token = a.token if a.token is not None else secrets.randbits(64) or 1
    decoder = Decoder(token)
    if a.capture:
        decoder.feed(a.capture.read_bytes())
    else:
        import serial
        # An explicit open with control lines deasserted avoids tool-owned reset
        # or selection behavior. No reconnect, retries or state restoration.
        with serial.Serial(port=None, baudrate=115200, timeout=0.05, write_timeout=0.1) as wire:
            wire.dtr = False; wire.rts = False; wire.port = a.port; wire.open()
            if wire.write(request(token)) != 16: raise ValueError('partial request write')
            deadline = time.monotonic() + a.timeout
            while time.monotonic() < deadline and decoder.response is None:
                decoder.feed(wire.read(max(1, min(256, wire.in_waiting))))
    print(json.dumps(dict(session=a.session, observation='current_session_only', **decoder.finish()), indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
