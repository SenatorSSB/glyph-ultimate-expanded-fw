# Glyph Roadmap

Status label: CURRENT.

This is the clean long-term Glyph-side roadmap. Dated calibration packets remain
evidence, but current direction should be read here first.

## Phase 0 - Current Hardcoded Firmware Baseline

Goal: Preserve the current hardcoded Glyph/HayBox firmware behavior and its
recorded hardware scope.

Current status: GFW3 runtime remap is merged/tested/recorded. Preservation
hardware pass is recorded for applicable non-nunchuk scope.

Required evidence: source files, hardware result packets, current checker output,
and recorded artifact/hash data where available.

Stop conditions: unexpected firmware behavior, unclear hardware scope, missing
result provenance, or any attempt to expand nunchuk claims.

Explicit non-goals: no runtime-loaded config, no device write, no external
adapter output, no Senscope game-semantic changes.

## Phase 1 - Senscope Neutral Profile Format

Goal: Keep a neutral Senscope-owned profile concept separate from Glyph firmware
and game semantics.

Current status: Directional profile ideas exist at the integration boundary, but
this repo does not own Senscope schema changes.

Required evidence: explicit user approval for schema changes and Senscope-side
source authority when that workstream is active.

Stop conditions: task requires changing neutral profile schema or coupling
controller constraints into game-semantic solving.

Explicit non-goals: no Glyph firmware edits, no game-semantic source promotion,
and no schema changes from this repo alone.

## Phase 2 - Generated-Config/Evaluator Bridge

Goal: Use source-backed generated config artifacts to drive offline evaluator
checks and compare expected controller/backend behavior.

Current status: Generated-config prototypes, evaluator input, invalid corpus, and
compatibility checkers exist as docs/tools artifacts.

Required evidence: source-parsed tables, role maps, behavior-case fixtures,
deterministic checker output, and explicit non-claims.

Stop conditions: generated data depends on inferred behavior, unsupported roles,
or undocumented backend behavior.

Explicit non-goals: not firmware input, not runtime-loaded config, not hardware
validation, and not device transport.

## Phase 3 - Generated C++ Constants / Firmware Build Path

Goal: Convert reviewed generated constants into a source-backed firmware build
path only when approved.

Current status: Generated C++ review artifacts exist; they are not firmware
source by themselves.

Required evidence: exact source diff, build output, artifact inspection,
behavior-preserving checker coverage, and hardware plan/result for runtime
impact.

Stop conditions: generated constants drift from source, build fails, or the
change would alter behavior without approval and test plan.

Explicit non-goals: no broad refactor, no runtime-loaded config interpreter, no
device write, and no nunchuk validation claim.

## Phase 4 - Offline Official Configurator Export Candidate

Goal: Produce an offline candidate artifact for official-configurator-oriented
comparison after the profile format exists.

Current status: Official configurator corpus is present when the 2026-06-06
manifest exists, but exact app metadata may remain unknown.

Required evidence: official corpus manifest, fixture hashes, source-authority
classification, and candidate validation report.

Stop conditions: vendor format is undecided, official source authority is
insufficient, or compatibility would be claimed from incomplete evidence.

Explicit non-goals: no WebSerial/device write, no protobuf binary write, no
firmware flashing automation, and no universal official compatibility claim.

## Phase 5 - Manual Import/Export And Hardware Validation Loop

Goal: Compare offline candidates through manual official configurator
import/export and separately record any hardware validation.

Current status: Manual comparison is not a device-write workflow and does not
replace source authority.

Required evidence: exact app/version/source reference when available, input and
output hashes, no-device/write caveats, hardware artifact provenance, and result
packet.

Stop conditions: test route requires push-to-device behavior, WebSerial write,
firmware flashing automation, or undocumented compatibility claims.

Explicit non-goals: no automated flashing, no direct device write, no nunchuk
validation unless executed and recorded.

## Phase 6 - Stable Firmware + Bounded Config-Owned Modifier Data

Goal: Define a stable firmware boundary where future config may own bounded
modifier data while firmware owns evaluator semantics.

Current status: Design-only concepts exist in runtime-loaded config design
packets.

Required evidence: source-backed ownership split, bounded schema, validator
contract, fallback policy, and hardware validation plan.

Stop conditions: config attempts to own evaluator phase order, scripts, macros,
turbo, timing automation, or history-dependent logic.

Explicit non-goals: no arbitrary scripting, no hidden transport behavior, no
runtime interpreter implementation without explicit approval.

## Phase 7 - Runtime-Loaded Config Interpreter

Goal: Implement a firmware-owned bounded runtime config interpreter only if
future approval and source authority exist.

Current status: Runtime-loaded config is not implemented. Existing docs are
design/plan packets only.

Required evidence: explicit user approval, storage decision, representation
decision, validator design, fallback policy, build, hardware plan/result, and
rollback plan.

Stop conditions: implementation approval missing, storage/transport source
authority missing, fallback ambiguous, or implementation depends on inferred
behavior.

Explicit non-goals: no device write transport, no schema authority from external
remapper docs, no hardware validation claim without result.

## Phase 8 - WebSerial/Device-Write / Push-To-Device Workflow

Goal: Consider a write-capable workflow only after source authority, policy, and
validation exist.

Current status: WebSerial/device write is not implemented. Protobuf binary write is not implemented. Firmware flashing automation is not implemented.

Required evidence: official transport/schema authority, no-destructive workflow
policy, explicit approval, round-trip validation, hardware safety plan, and
rollback/recovery plan.

Stop conditions: task requires push-to-device behavior without explicit source
support, reverse-engineering private/encrypted formats, or unsafe/destructive
device actions.

Explicit non-goals: no current implementation, no external-remapper adapter
output, no firmware flashing automation, and no user-facing write path.
