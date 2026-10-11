# Runtime-Loaded Ultimate Profiles Chapter Ledger

Status: `HARDWARE_GATE_A_REQUIRED`.

## Authority and scope

- Authority: direct owner chapter, “Runtime-Loaded Ultimate Profiles — Persisted
  Coordinates, Routing, Sublayers, Priorities, and Bounded Output Effects”,
  supplied 2026-10-11.
- Canonical base: live `origin/configurator`
  `28ba39da5f517baa40f3dee8d868c9bb583dde4a`, verified 2026-10-11.
- Isolated branch/worktree: managed worktree
  `runtime-loaded-ultimate-profiles`, based on that exact commit.
- This chapter does not use the private friend-firmware package as a baseline
  or source authority.

## Fixed chapter decisions

- Store versioned Ultimate runtime profiles additively in persisted `Config`.
- Bind an Ultimate `GameModeConfig` to a runtime profile by an explicit
  persisted reference, never by display name.
- An absent reference retains the source-owned legacy Ultimate behavior.
- An explicit but invalid or unsupported runtime extension is rejected; it
  never silently falls back to unrelated source-owned modifier values.
- Stage A owns only persisted, validated 9-way coordinate tables while legacy
  role/routing remains in firmware. Stages B and C are gated on Stage-A human
  hardware evidence.
- The runtime vocabulary is finite and declarative: no scripts, macros, turbo,
  timing, loops, or arbitrary expressions.

## Exclusions and safety boundaries

- No Senscope game-semantics ownership, browser UI, official configurator
  compatibility, WebSerial, automatic device writes, or automatic flashing.
- The daemon never writes Config to or flashes a physical controller.
- No active `RuntimeConfigView` replacement, candidate-view publication,
  generated wrapper publication, or RAM-backed active-table publication.
- Nunchuk remains `NOT_TESTED` unless the owner reports a test.

## Stage state

| Stage | State | Evidence / next permissible action |
| --- | --- | --- |
| 0 — schema, resource, source authority | source design complete; build pending | Tracked schema source and bounded Stage-A representation are in place. Canonical build/codegen proof remains pending. |
| A — persisted coordinates | `HARDWARE_GATE_A_REQUIRED` | Source, host proof, fresh reviews, build and custody are complete. Await the owner's bounded write/reboot observation before any Stage-B routing work. |
| B — roles, sublayers, priorities | blocked on Gate A PASS | No implementation before exact Stage-A owner hardware PASS. |
| C — bounded output effects | blocked on Gate A PASS | No implementation before Stage-A proof and Stage-B source/host proof. |

## Controls and measurements

- Preserve exact source, build and artifact identities for every hardware-facing
  candidate; no merge to `configurator` before the required human PASS.
- Required resource report: `sizeof(Config)`, static/global RAM, stack
  warnings, flash use, and encoded Config sizes for legacy, one, two and
  maximum profiles.
- Chapter worker model/effort and review identities will be recorded when a
  worker is dispatched or a candidate is produced.

## Known starting facts

- The live remote verification required network-enabled execution and matched
  the owner launch observation.
- The original checkout had unrelated dirty changes; this isolated worktree is
  clean and those files are not part of this chapter.
- The current firmware persists its one `Config` protobuf via LittleFS and
  validates decoded candidates before publication. The current source-owned
  Ultimate runtime tables are legacy behavior, not runtime-loaded profiles.
- The selected dependency schema was cached at HayBox-proto
  `db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8`; it is now vendored under
  `schema/haybox/` so Nanopb code generation has tracked, reproducible inputs.
- Stage-A schema uses `Config.ultimate_profiles` (tag 201; capacity two), a
  one-based `GameModeConfig.ultimate_profile_config` reference (tag 203), and
  profiles made of 28 explicitly identified tables with exactly nine `Coords`
  each. Validation and firmware consumption have not yet been added.
- Existing target-ABI evidence measured `sizeof(Config)` at 26,912 bytes.
  The Stage-A schema is estimated to add roughly 1.3 KiB per fixed Config
  instance; final acceptance requires target-generated measurements.

## Current stop condition

Stage A is waiting for owner hardware evidence. Do not start Stage B or C until
the exact Gate-A candidate passes its bounded physical matrix. A concrete
schema reproducibility, resource, source-authority, or architecture
contradiction must be recorded here before requesting an owner decision.

## Stage-A candidate and proof

- Firmware candidate source: `45e0b89dea86fefba631350bc80afae7b28af645`
- Candidate tree: `c2c6dfaa8b99efa99f037733de55656d4247e106`
- Mk6 UF2: 805,888 bytes, SHA-256
  `b13ad448fe989f84265e97babc5b650968eb75d787fc58791d814f478ea8bcf1`
- Custody path:
  `local_backups/hardware-artifacts/45e0b89dea86fefba631350bc80afae7b28af645/b13ad448fe989f84265e97babc5b650968eb75d787fc58791d814f478ea8bcf1/firmware.uf2`
- Build: `./scripts/build-glyph-mk6-quiet.sh` — PASS; RAM 109,520 / 262,144
  bytes (41.8%), flash 390,752 / 1,568,768 bytes (24.9%).
- Host proof: `python3 tools/test_ultimate_profile_host.py` — PASS (504
  profile table/direction lookups plus validation negatives).
- Artifact proof:
  `python3 tools/check_glyph_stage_a_ultimate_profiles_dry_run.py` — PASS;
  profiles 2, table count 28, coordinate count 9, explicit refs `0,1,2`, no
  serial port opened. The exact writer-produced protobuf is regenerated from
  the tracked schema/options, decoded by Nanopb, and accepted by the complete
  production `validate_glyph_config` chain; six semantic and one overlong-name
  decoder negative also reject. Artifact
  `tools/fixtures/stage_a_ultimate_profiles_dry_run.json` SHA-256:
  `fc86614108390f46ede813d5655a73aca34ed9a193258126c9fb6e593b353143`.
  Its encoded payload is 4,064 bytes, SHA-256
  `5ce69327af7039db5c3f203bba29d66ab80c653f01bee47f8ddba0baa7b737d2`.
- Fresh reviews: production implementation APPROVED; final artifact/adapter
  review APPROVED after the non-Ultimate-reference and row-cardinality guards.

## Workers

| Task | Context | Requested | Observed |
| --- | --- | --- | --- |
| Schema research | inherited; read-only | Terra / medium | model UNKNOWN; effort UNKNOWN |
| Schema implementation | inherited; sole schema writer | Terra / medium | model UNKNOWN; effort UNKNOWN |
| Stage-A firmware | fresh; sole production writer | Terra / medium | model UNKNOWN; effort UNKNOWN |
| Stage-A production review | fresh | Luna / medium | model UNKNOWN; effort UNKNOWN |
| Stage-A host proof | fresh; sole tooling writer | Luna / medium | model UNKNOWN; effort UNKNOWN |
| Stage-A artifact adapter | fresh; sole artifact/tool writer | Terra / medium | model UNKNOWN; effort UNKNOWN |
| Artifact review and re-review | fresh | Luna / medium | model UNKNOWN; effort UNKNOWN |
| Artifact admission diagnosis | fresh; sole artifact-admission writer | Sol / medium | model UNKNOWN; effort UNKNOWN |
| Artifact admission review | fresh; independent review | Luna / medium | model UNKNOWN; effort UNKNOWN |
