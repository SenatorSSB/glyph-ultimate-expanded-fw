# GP-BIND-003 implementation validation

Classification: FIRMWARE_SOURCE_ACTIVE_BEHAVIOR / H3. This is implementation
evidence, not an independent review, target build, hardware result or DONE.
Base: `bd548dacf453c932b1a88a0684e6e1155080a309`.
Branch: `codex/gp-bind-003-runtime-attestation`.
Wire/digest/lifetime contract was committed first as
`21f3e383` in [the wire contract](gp_bind_003_wire.md), before handlers.
The enclosing implementation commit supplies the exact source/tree identity;
it is deliberately not self-referenced here. No canonical merge is authorized.

## Implemented surface

Const accessors expose the already-selected Ultimate profile, actual mode Config
pointer and ProfileStore's latched active revision. `RuntimeIdentity.hpp` compares
the actual current primary mode with the actual Ultimate instance, proves Config
row membership separately, and compares the evaluator's profile pointer with
the store's active copy. Its digest streams that active payload through the
complete generated Nanopb descriptor. It never reads a file or selects, reloads,
reconciles or activates anything. Configurator command 10 is neutral in that
current context, with an explicit recovery status when applicable.

`RuntimeIdentityService.hpp` is the single finite RX reader in primary XInput,
called on core0 after all complete backend/viewer reports. It accepts only the
16-byte identity request, consumes at most 32 bytes per loop, handles at most
one accepted request and admits the complete 72-byte response plus a 32-byte
viewer reserve before hashing/transmitting. No generic dispatcher, allocation,
wait, retry queue, flush, USB descriptor or scheduling change was introduced.
Existing XInput and B0XX viewer source, viewer payload/clock, selection,
activation, persistence and Ultimate evaluator code remain byte-exact to base.

The host tool is read-only identity capture/strict decoding. Its explicit
`--context xinput` uses fixed records; `--context configurator` wraps only
identity command 10 in COBS. It exposes no generic command argument. Configurator
decoding admits only a complete command-10 neutral Configurator/recovery response,
never a gameplay attestation. It requires an explicit port or retained capture
and an external session label, and rejects partial, ambiguous, unknown, oversized,
duplicate, wrong-context and wrong-token data. CLI round trips/negative controls
and every COBS frame split are tested. The host decoder also consumes the actual
production Configurator COBS response from each ABI harness. No device was opened.
Historical H4 remains UNKNOWN.

Independent review caught the initial host-only `dtr=False` open defect. The
descendant correction asserts DTR before its single 115200-baud open and leaves
RTS deasserted. Pinned Adafruit CDC writes loop only while TinyUSB reports
connected; its connected predicate requires DTR bit 0. The pinned DFU callback
requires falling DTR at 1200 baud, which this observation path never selects.
The source-backed regression executes the exact pinned connected/write/line-state
function bodies with hardware seams: DTR false sends zero bytes, DTR true sends
the complete 72-byte response, and 115200 open/close does not enter DFU; a 1200
negative control proves the DFU seam is live. It also executes the actual CLI
live-open branch for XInput/Configurator through an in-memory serial seam and
requires DTR asserted before one open, identity-only write and one close. This
is host/source proof, not a physical connection or general no-reset claim.

## Actual checks

Commands below ran in the candidate worktree using the existing local Nanopb,
PacketIO and nanopb-arduino dependencies through ignored disposable links. No
download, target build or device access occurred. Sanitized host proof is not
controller acceptance. Final replay is required if any tested source changes.

| Command (`python3 tools/…`) | Observation |
| --- | --- |
| `check_glyph_gp_bind_003_runtime_identity.py` | PASS: actual selection, ProfileStore, Ultimate, communication state, B0XX viewer and finite service; both default and short enum ABIs, ASan/UBSan. |
| `check_glyph_profile_store_selection_recovery.py` | PASS, including old-selection/retired-recovery negative controls. Its extracted-startup fixture gained only a no-op identity-service seam; the new proof exercises the actual service. |
| `check_glyph_profile_store_production.py` | PASS_SOURCE_COMPOSITION, four retirement negative controls; no ELF/build claim. |
| `check_glyph_profile_store_strict_protocol.py` | PASS, including production and candidate diagnostic harnesses, 128 updates, 1,024 arm-loss cycles and 7,680 mixed frames. Diagnostic controls remain disabled in production. |
| `check_glyph_profile_store_config_persistence.py` | PASS, 37 current-source cases; target filesystem power loss NOT_EMULATED. |
| `check_glyph_stage_b_ultimate_profiles.py` | PASS: actual V1–V3 decode/admission/evaluator; ten negatives; Config 31,432 bytes. |
| `check_glyph_stage_c_ultimate_profiles.py` | PASS: 1,222,420 final-output comparisons against frozen legacy; fifty production decode negatives, eleven decoder refusals; profile 2,152 bytes under short-enum ABI. Host Nunchuk invariants do not constitute a Nunchuk test. |
| `check_glyph_build_input_resolution_observations.py` | PASS, 44 historical source-bound observations. |
| `check_glyph_setconfig_runtime_rebinding_characterization.py` | FAIL: `C024 post-integration change outside validation/evidence paths`, in historical source correspondence before its behavior harness. Preserved unchanged; no PASS substituted. |
| `check_glyph_build_input_non_selector_configuration.py` | FAIL: `source identity mismatch: platformio.ini`. Current file is byte-exact to base; historical pin expects earlier source. |
| `check_glyph_build_input_provenance_inventory.py` | FAIL: `declaration byte drift: config/glyph/env.ini`. Current file is byte-exact to base; historical census has not admitted later production changes. |
| `git diff --check` | PASS. |

No full aggregate PASS is claimed. The three frozen-census/correspondence
failures are retained as validation debt for supervisor/independent review;
they are not findings that the attestation behavior passed or failed. A concrete
Tier-1/directly affected Tier-2 contradiction still blocks its dependent gate.

The new proof covers real persisted activation, stored r+1/runtime r, real
re-activation, missing selection with stale ActiveId/null Ultimate, corrupt newest
record recovering the exact previous latched revision, requested != active,
pointer mismatch, embedded legacy, foreign Config context, no primary/mode,
non-Ultimate, Configurator/recovery and digest failure. It counts every storage
operation around repeated queries and compares Config bytes, files, generation,
transaction token, active pointer and recovery state. Identical-input sequences
match through 512 query interleavings for each V1/V2/V3 and enum ABI. Sixty mixed
query/viewer loops retain ten complete 25-byte viewer records at the existing
five-increment pacing and sixty complete identity records.

The proof rejects eleven actual observer mutants: requested-ID substitution,
stored-revision substitution, ignored object mismatch, stale row, stored readback
hash, and omission of schema/tables/roles/routing/rules/output payload fields.
Mutants run in the default ABI with ASan/UBSan; positive/adversarial production
cases and digest/dispatch proofs run in both ABIs. Python independently hashes
the decoded full payload with the frozen domain and compares exact digest bytes.
Unknown raw protobuf fields alter raw bytes but not the semantic payload digest.
Malformed version/kind/length/token, short/partial/timeout, 8,192 bytes of garbage,
full/unavailable TX and non-XInput primary are explicit tests. Host decoder tests
all frame splits and all incomplete response lengths.

V4 proof is descriptor compatibility only in a disposable host directory. Exact
failed GP-BIND-002 `b3d60feb48d637efa8612515d2351a470fe9df0e` schema/options and
fixture constructors/inputs are read with `git show`, pinned in checker output,
then used to generate an isolated descriptor and a genuine complete V4 fixture.
The production digest helper compiled against that isolated descriptor matches
independent Python encoding, including function bindings, in both ABIs; omitted
fields differ. None of that failed source or V4 admission is imported. A later
V4 candidate still requires its separate composed production proof/adjudication.

## Descriptor pins and remaining gates

The checker prints exact schema/options, generated descriptor and runtime pins.
Current stable values:

- `schema/haybox/config.proto`: `81b0aad7568728ac465981b42c738154af8250e16426734d269e0abe7b9d3f49`.
- `schema/haybox/config.options`: `612d23b268742d0cc8e4b871d33b3ccba7c6f912ca3352364e329b3fef0096c0`.
- Generated `config.pb.h`: `013e43f98c43fa7977dce4b18957d010e83f713037a8f7885ce935bcd16aca64`.
- Generated `config.pb.c`: `e080e0b4feba05473ff5016167a31dbebbaa348ba974096465bc422f4e7641fc`.
- Nanopb `pb.h`: `a2ecdca9fdaeef5f4972ed983540c0d6fb0a5c402a2e0b0349d7e1bc5e188d29`.
- Nanopb `pb_encode.c`: `d8dff2a1acc58683095a41b0dc3103ba46248e4a8d8c4e20f5810be04127b650`.
- Generator: `9e6551f8a5c9332cb16c711364e3de93dd16ae69b4c390547cbdf0b8639710f3`.

Host measurements report a 24-byte service, 56-byte snapshot and a 5,740-byte
generated maximum encoded extent in both ABIs. These are not target memory or
latency measurements. Hashing uses a streaming SHA state and bounded schema recursion.
Host elapsed timings printed by the checker are host observations only, not
target latency bounds. Target RAM/flash/stack, maximum payload cost and timing
remain exact committed Mk6 build/resource and independent review gates. The
core1 display can clear/restore primary mode while active payload ownership stays
on core0; successful identity is point-in-time and mode is checked before/after
hashing, never promised continuously after reply.

Build NOT_RUN; artifact NONE; custody NOT_CREATED; independent review PENDING;
hardware A1–A5 NOT_TESTED. No flash, reset, profile selection/update, device write,
hardware acceptance, source integration or strict DONE is claimed. Controller
capability remains PARTIAL; network-enabled Git verification remains required
and is supervisor-owned. Root cause remains UNPROVEN; Nunchuk NOT_TESTED.
