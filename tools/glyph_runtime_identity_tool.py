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
IDENTITY_COMMAND = 10

def request(token: int) -> bytes:
    if not 0 < token < 2**64:
        raise ValueError('token must be a nonzero uint64')
    return MAGIC + struct.pack('<BBHQ', 1, 1, 16, token)

def cobs_encode(payload: bytes) -> bytes:
    # Only the fixed identity records use this encoder, never arbitrary commands.
    result = bytearray([0]); code_index = 0; code = 1
    for byte in payload:
        if byte == 0:
            result[code_index] = code; code_index = len(result); result.append(0); code = 1
        else:
            result.append(byte); code += 1
            if code == 255:
                result[code_index] = code; code_index = len(result); result.append(0); code = 1
    result[code_index] = code
    return bytes(result) + b'\0'

def cobs_decode(encoded: bytes) -> bytes:
    result = bytearray(); cursor = 0
    if not encoded or len(encoded) > 74: raise ValueError('invalid Configurator frame extent')
    while cursor < len(encoded):
        code = encoded[cursor]; cursor += 1
        if not code or cursor + code - 1 > len(encoded): raise ValueError('invalid COBS block')
        block = encoded[cursor:cursor+code-1]
        if 0 in block: raise ValueError('zero inside COBS block')
        result.extend(block); cursor += code-1
        if code != 255 and cursor < len(encoded): result.append(0)
    return bytes(result)

def wire_request(token: int, context: str) -> bytes:
    payload = request(token)
    if context == 'xinput': return payload
    if context == 'configurator': return cobs_encode(bytes([IDENTITY_COMMAND]) + payload)
    raise ValueError('unknown identity transport context')

def payload_digest(profile) -> str:
    return hashlib.sha256(DOMAIN + profile.SerializeToString(deterministic=True)).hexdigest()

class Decoder:
    def __init__(self, token: int, expected_backend: int | None = None):
        request(token)
        self.token, self.pending = token, bytearray()
        self.expected_backend = expected_backend
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
            if self.expected_backend is not None and backend != self.expected_backend:
                raise ValueError('response primary backend differs from capture context')
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

class ConfiguratorDecoder:
    """One dedicated command response; no viewer or generic packet dispatcher."""
    def __init__(self, token: int):
        self.identity, self.pending = Decoder(token, expected_backend=8), bytearray()

    @property
    def response(self):
        return self.identity.response

    def feed(self, data: bytes) -> None:
        for byte in data:
            if byte:
                self.pending.append(byte)
                if len(self.pending) > 74: raise ValueError('oversized Configurator identity frame')
                continue
            decoded = cobs_decode(bytes(self.pending)); self.pending.clear()
            if len(decoded) != 73 or decoded[0] != IDENTITY_COMMAND:
                raise ValueError('unexpected Configurator command or identity length')
            self.identity.feed(decoded[1:])
            if self.identity.response['status'] not in ('configurator', 'recovery'):
                raise ValueError('Configurator cannot attest gameplay context')
            if self.identity.response['context_row'] or self.identity.response['requested_reference']:
                raise ValueError('Configurator carries unexpected gameplay context')

    def finish(self) -> dict:
        if self.pending: raise ValueError('partial/timeout Configurator frame')
        return self.identity.finish()

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--capture', type=Path, help='decode an already retained raw XInput capture')
    source.add_argument('--port', help='explicit current CDC port in the selected context; identity request only')
    p.add_argument('--context', choices=('xinput','configurator'), default='xinput',
                   help='fixed XInput records or dedicated Configurator command 10 only')
    p.add_argument('--token', type=lambda s: int(s, 0))
    p.add_argument('--session', required=True, help='external boot/session label; never inferred from token')
    p.add_argument('--timeout', type=float, default=2.0)
    a = p.parse_args()
    if not 0 < a.timeout <= 10: p.error('timeout must be in (0,10] seconds')
    if a.capture and a.token is None: p.error('--capture requires its exact --token')
    token = a.token if a.token is not None else secrets.randbits(64) or 1
    decoder = Decoder(token, expected_backend=2) if a.context == 'xinput' else ConfiguratorDecoder(token)
    if a.capture:
        decoder.feed(a.capture.read_bytes())
    else:
        import serial
        # An explicit open with control lines deasserted avoids tool-owned reset
        # or selection behavior. No reconnect, retries or state restoration.
        with serial.Serial(port=None, baudrate=115200, timeout=0.05, write_timeout=0.1) as wire:
            wire.dtr = False; wire.rts = False; wire.port = a.port; wire.open()
            query = wire_request(token, a.context)
            if wire.write(query) != len(query): raise ValueError('partial request write')
            deadline = time.monotonic() + a.timeout
            while time.monotonic() < deadline and decoder.response is None:
                decoder.feed(wire.read(max(1, min(256, wire.in_waiting))))
    print(json.dumps(dict(session=a.session, context=a.context, observation='current_session_only', **decoder.finish()), indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
