# Runtime attestation — independent Curator decision

Date: 2026-10-19. Classification: `DOCS_CHECKER_ONLY`; this decision implements
no firmware, device request, build or hardware test. New product order
**GP-BIND-003 is READY**, H3 / `FIRMWARE_SOURCE_ACTIVE_BEHAVIOR`, only after
the descendant queue adoption is integrated. The immutable receipt alone does
not activate implementation. No global wait is accepted.

## Independently verified authority

The original owner attachment is
`/Users/rasmus.pekkarinen/.codex/attachments/b012f2b7-9d61-4161-9bd3-70368eac2329/goal-objective.md`,
SHA-256 `57683824763eebf0939bea1c19fdfec1ce2065649d5632bd90ffa86ede775eec`.
I read its original text and recomputed its digest. The owner explicitly selects
bounded read-only runtime attestation and requires normal READY and exact
hardware acceptance. The attachment has no embedded timestamp/message ID;
2026-10-19 is its observed/daemon-supplied date, not an invented original ID.

Ordinary live Git verification failed DNS and was inconclusive. The permitted
network-enabled retry independently returned canonical
`941affbdbb7e54563e4c58a3830c49f39ea0f449` and Planner
`9af3ce8b6c6076ca96cc8c7ee60850537c8ddfad`; the Planner was fetched and read.
It is a direct child of that base. The new append-only receipt is also a direct
child of the same base, with the previous queue preserved. Its later adoption
records the immutable receipt SHA. Network escalation conferred no broader
mutation authority. Retain `live_github_requires_network_enabled: true`.

The [Planner packet](../planning/portfolio_20261019_0200.md) is adopted only
within this decision and the complete queue order. Its
[capability input](../planning/runtime_attestation_capability_20261019_0200.json)
is PARTIAL: repository/tool access works; no matching serial/filtered USB device
or worktree-local build runtime was observed. That is neither authentication
failure nor proof of all possible device capabilities. Reuse it until a material
environment change; probe only the unavailable operation, without writes/resets.

## Source judgment and exact authorized surface

Independently inspected at the base: `ProfileStore::Activate` copies the loaded
object into `_active_profile` and latches `_active_revision` (including recovered
previous revision). A failed nonzero activation may preserve older ActiveId.
`src/core/mode_selection.cpp` passes null to `Ultimate::SetConfig` on a failed
selected record; `Ultimate::_profile` is the object used in actual output paths.
Thus Config reference/readback, store ActiveId and `current_mode_index` alone
cannot prove runtime evaluation. Requested row is context only.

`backend_init.cpp` constructs the primary XInput backend plus B0XX viewer;
`B0XXInputViewer::SendReport` writes complete 25-byte records with its existing
pacing. XInput starts Serial but has no Configurator dispatcher. Configurator
is a different session/context and cannot attest an earlier XInput run. The
historical H4 runtime identity remains UNKNOWN and is not reconstructed.

Authorize one const observer of the **current primary backend** and actual
Ultimate object, internally verifying pointer correspondence with the active
store object. No pointer/address leaves firmware. A versioned response may
include protocol version/token/status, primary backend ID, a proven current
Config-member row/requested reference as separately labeled context, and only
on proven persisted evaluation: store incarnation, active ID, latched revision,
schema version and exact SHA-256 of deterministic Nanopb encoding of that actual
active payload with a pinned descriptor/domain/version. Digest/snapshot failure,
legacy embedded/source fallback/non-Ultimate/no mode/recovery/mismatch must yield
explicit neutral/unavailable statuses with no persistent-identity claim.

ID/revision alone cannot challenge wrong-object/payload correspondence. Hash
the actual active object, not Config, directory revision, raw readback headers,
native padding or unknown protobuf fields. Preserve raw readback hashes separately.
Use bounded streaming hashing on the existing core0 service path outside output
generation; prove stable ownership/snapshot and bounded stack/loop cost. No
duplicate selection latch, reload, periodic storage reads or inferred identity.

Authorize a dedicated read command in Configurator and a **finite identity-only
adapter on the existing primary-XInput CDC session**, using the existing
core0 loop/viewer boundary. Freeze bounded framing/version/length/token and
digest meaning before implementing handlers. Preserve complete 25-byte viewer
records/pacing, serialize response writes at record boundaries, have one reader
per stream, and make the host separate viewer from identity records and reject
ambiguous/partial/timeout data. No generic Configurator dispatch in XInput.
If this cannot be achieved within the existing ownership/timing boundary, stop
for owner architecture direction; Configurator-only neutral replies do not
satisfy the current-session objective.

The queue scope permits only const accessor/helper work, additive identity wire
messages/commands, the finite adapter, host reader/capture and focused proofs.
No new USB interface/descriptor, backend selection, scheduler/background worker,
debug memory/RPC, write/control/reboot/recovery dispatcher, Config/ProfileStore
mutation, selection/evaluator/activation repair, schema admission/binding changes,
ProfileStore redesign, RT2 or flashing automation. Additive query schema fields
are not authority to redesign profile schema or persistent storage.

Canonical admits V1–V3; failed GP-BIND-002 V4 source is unmerged. V4 compatibility
must be tested only in an isolated exact-source host fixture, without importing
failed source or claiming V4 production acceptance here. A later V4 candidate
requires real composed production/digest tests and separate bounded adjudication.
The owner authorizes later source diagnosis, but this order does not authorize
an X1 repair or predetermine activation versus carrier-consumption cause.

## Validation, physical and publication gates

The full [queue](../project/ACTIVE_AGENT_QUEUE.md) order and
[hardware protocol](GP_BIND_003_HARDWARE_PROTOCOL.md) bind the implementation.
Required host proof uses actual selection/store/Ultimate/dispatch code, both enum
ABIs and sanitizers where supported. Cover persisted activation; selection and
required reboot/activation; stored r+1 while runtime remains r; invalid/missing
selection with stale store ActiveId; previous recovery revision; V1–V3 and isolated
V4; complete schema/payload digest; zero persistent writes/reconciliation/activation;
same-input output equivalence; bounded malformed/partial/repeated CDC handling,
viewer preservation and TX backpressure. Mutants that substitute requested/stored
identity, ignore object mismatch or omit payload fields must be rejected.

Run all directly affected consumers identified in the packet and descriptor,
size/build-input proof. A fresh independent reviewer must challenge false
stored-but-not-running claims, snapshot lifetime, digest meaning and stream
ownership/output noninterference. Current Revision 3 Tier 1 and affected Tier 2
block; retain unrelated FAIL/incomplete as framework debt, never aggregate PASS.

Build the exact committed candidate using `pio run -e glyph_mk6` (record the
documented fallback if necessary). Review RAM/flash/stack/latency and preserve
the unique UF2 at `local_backups/hardware-artifacts/<candidate SHA>/<artifact SHA>/firmware.uf2`.
Record full candidate/base/tree, artifact bytes/hash and custody/readback; rehash
before any separately approved manual update. Old candidate/build/physical
acceptance does not transfer. Candidate/artifact/result fields stay null now.

Physical PASS must cover exact candidate/artifact, safe original backup/custody,
neutral Configurator/recovery truth, active persisted identity/digest in the
same XInput boot/session, repeated queries with ordinary controls/viewer intact,
and normal manual reboot/reconnect identity. Missing/corrupt/store-update unsafe
cases remain host-only unless separately approved; no fabricated physical PASS.
The query order authorizes no device-state change. Any needed flash, selection,
profile update or physical action requires its concrete approved preparation
packet and safe manual recovery plan before handoff.

After exact human evidence, source-free HEP `E` follows reviewed handoff `R`,
then exact tested-source integration `I` and its genuine catalog/correspondence,
fresh integration review and separate strict DONE. No H3 source merges before
exact human PASS. Any false identity, wider architecture need, output/transport
anomaly, uncertain mutation, Tier-1/affected Tier-2 defect or missing custody
stops the dependent transition. Source-free evidence must not carry failed source.

After trustworthy attestation, renewed X1 diagnosis must bind Config identity,
actual mode/row/requested ID, store ID/revision/raw and canonical payload digests,
runtime ID/revision/digest and firmware/artifact tuple before any future H4.
Unexpected mismatch stops H4. Fresh evidence then returns for bounded repair
adjudication. GP-BIND-001/002 FAIL and the completed diagnostic remain immutable;
root cause remains UNPROVEN and Nunchuk remains NOT_TESTED.
