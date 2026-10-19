# GP-BIND-003 frozen identity wire and ownership contract

Frozen before handler implementation. This document defines wire version 1;
it authorizes no device operation or hardware acceptance.

All multibyte integers are unsigned little endian. A request is exactly 16
bytes: magic `a5 47 52 49`, version `01`, kind `01`, length `10 00`, then a
nonzero 64-bit host correlation token. There are no optional fields, commands,
payload, addresses or writable operations. A response is exactly 72 bytes:
the same magic, version `01`, kind `02`, length `48 00`, echoed token,
status u8, primary backend u8, current Config row u16 (zero means unavailable;
otherwise one based), requested persistent reference u32 (context only),
incarnation u32, active ID u32, latched active revision u32, schema u32,
and 32 digest bytes. Only status 0 carries persistent identity; all five
persistent fields and digest are zero for any other status.

Statuses: 0 persisted, 1 no primary, 2 Configurator, 3 recovery, 4 no mode,
5 non-Ultimate, 6 source fallback, 7 embedded legacy, 8 store unavailable,
9 object mismatch, 10 context unavailable, 11 digest failure,
12 snapshot unavailable. Context row/reference are obtained only by equality
with the actual mode Config pointer within the current Config array. They
never select the profile or replace active identity.

Digest domain is ASCII `Glyph.RuntimeIdentity.UltimateProfile.v1` including
its trailing NUL, followed by deterministic Nanopb encoding using the complete
`UltimateProfile_fields` descriptor generated from this candidate's unchanged
UltimateProfile schema and options. Encoding includes every known schema,
table, role, routing, rule and output-program field and presence bit; it excludes
unknown protobuf fields, native padding, record headers, Config and directory
metadata. The candidate build/handoff must pin the exact generated descriptor,
generator/runtime and schema/options hashes. Descriptor-generic isolated V4
proof does not admit V4 into production. Raw readback SHA-256 is separate.

Configurator command 10 wraps exactly this request/response in its existing
COBS packet ownership. It can only report the current Configurator or recovery
context; it cannot attest an earlier gameplay session. XInput uses the fixed
records directly on existing CDC. It has one RX owner, an identity-only parser,
16-byte storage and at most 32 consumed bytes/loop, no waits or generic
Configurator dispatch. An incomplete record expires after 250 ms and enters
resynchronization; a fresh magic starts a new record. Invalid size/version/kind
or zero token produces no response. At most one valid request is handled/loop.
No success is inferred from silence or a partial frame.

Service occurs on core0 after every backend's complete SendReport call. Existing
25-byte viewer bytes and five-increment pacing remain unchanged. A response is
written only when its complete 72 bytes plus the viewer's 32-byte admission
reserve fit the FIFO; otherwise it is dropped. There is no retry queue, wait,
flush or partial response deliberately emitted. Host permits one outstanding
request, separates exact 25-byte viewer records from fixed identity records,
checks complete framing/version/kind/length/token/status, and rejects partial,
ambiguous, duplicate, out-of-token or timeout data. Host reconnect/reboot starts
a new explicitly recorded capture session; the token is correlation, not a
device boot identifier.

ProfileStore Activate/Begin, Ultimate SetConfig and Config replacement execute
before normal XInput core0 service or in its mutually exclusive Configurator
session. Update does not replace the active copy. No query calls any of them.
The active object, latched revision and incarnation therefore remain owned and
stable during streaming encoding. Core1 display menus may temporarily clear or
restore the primary mode, but do not mutate the active payload or Ultimate's
profile pointer. Sample primary mode before and after encoding and return
snapshot unavailable on a change. A successful response is a point-in-time
observation of the sampled current primary evaluator, never a promise that the
mode remains active after the response. No pointers leave the device.

Streaming hashing uses constant stack and no profile-sized temporary or heap.
Nanopb's generated maximum encoded size caps the hashing stream. Full maximum
payload cost and actual target stack/latency remain candidate validation gates;
no bound is inferred merely from a successful compile.
