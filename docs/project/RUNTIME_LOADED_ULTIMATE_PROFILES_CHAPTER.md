# Runtime-Loaded Ultimate Profiles Chapter Ledger

Status: `FINAL_HARDWARE_GATE_REQUIRED`.

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
  role/routing remains in firmware. Stage A is hardware-validated; Stage B is
  active and Stage C may activate after its required Stage-B proof.
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
| 0 — schema, resource, source authority | complete | Tracked schema, reproducible code generation, target build, and measured resource report are complete. |
| A — persisted coordinates | `HARDWARE_PASS` | Exact owner H1–H15 evidence passed for the candidate/artifact/fixture tuple. |
| B — roles, sublayers, priorities | source/host proof PASS | Version-2 bounded roles, routed input slots, and explicit numeric-priority table rules passed production admission and fresh review. |
| C — bounded output effects | source/host proof PASS | Bounded v3 typed effects, two complete profiles, production admission, fresh review, exact build, and custody pass. Await remote publication verification and the grouped final owner gate. |

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
  each. Extent/semantic validation and firmware consumption are implemented
  for Stage A only.
- The generated host ABI measurement is `sizeof(Config) = 28,160` bytes,
  versus the 26,912-byte baseline: +1,248 bytes per fixed Config instance.
- Stage-B generated host ABI measurement is `sizeof(Config) = 34,544` bytes,
  +6,384 bytes from Stage A. The finite current-selector profile uses 22
  roles, 15 required routed source inputs, and 19 table rules; the 32,768
  combinations of those source inputs match the frozen legacy table selector.
- Stage-C measurement: short-enum `sizeof(Config) = 31,224` bytes and
  `sizeof(UltimateProfile) = 2,152` bytes; default-enum host ABI is 56,056
  and 2,344 bytes respectively. Production-path host correspondence passed
  1,222,420 complete final-output comparisons per ABI plus 50 strict decoder/
  semantic negatives. Encoded Config sizes are legacy 130, one v3 profile
  3,182, and two/max profiles 6,233 bytes. The two-profile fixture SHA-256 is
  `2a8ef6929956ec983938aad734a2a9e66fa8532e04ae2287c20d07e51f3fa2ec`;
  its writer payload SHA-256 is
  `d8f248b1a89099ea2a610697308ea299f9345bf7dd9b4627856014683e51eb8c`.

## Current stop condition

Stage B is active under the direct owner authorization. Do not request an
intermediate hardware test between B and C unless a concrete hardware-only
uncertainty makes it unsafe to continue. The next owner gate is the grouped
final B+C candidate; no canonical integration occurs before that exact PASS.

Stage B and C source/host validation and fresh independent reviews now pass.
The exact final source/artifact tuple is built and under local custody. Publish
and live-verify the feature branch before the grouped owner hardware gate. No
canonical integration occurs before that exact PASS.

## Final B+C candidate and custody

- Firmware source candidate: `16fb02a5eaaa95e63870d14593376c9d1f15aed2`
- Candidate tree: `13ad3a19e4cb1ae19fd866ad48cb55a96897e630`
- Build: `./scripts/build-glyph-mk6-quiet.sh` — PASS.
- Mk6 UF2: 832,000 bytes, SHA-256
  `c178cc2e39a6d2eceee27c16b9aae1364a04d628f1ca20bd28fc78a798c04830`
- Custody path:
  `local_backups/hardware-artifacts/16fb02a5eaaa95e63870d14593376c9d1f15aed2/c178cc2e39a6d2eceee27c16b9aae1364a04d628f1ca20bd28fc78a798c04830/firmware.uf2`
- Target build resource report: RAM 118,744 / 262,144 bytes (45.3%); flash
  403,968 / 1,568,768 bytes (25.8%). The known existing build warnings are
  unused historical runtime-config helpers and a 1,240-byte Senscope prototype
  self-test stack warning; no new Stage-C warning was reported.
- Final runtime-profile fixture:
  `tools/fixtures/stage_c_ultimate_profiles_dry_run.json`, SHA-256
  `2a8ef6929956ec983938aad734a2a9e66fa8532e04ae2287c20d07e51f3fa2ec`;
  encoded writer payload 6,233 bytes, SHA-256
  `d8f248b1a89099ea2a610697308ea299f9345bf7dd9b4627856014683e51eb8c`.
- The tracked serial adapter accepts only the same bounded v1/v2/v3 structural
  shapes required by production validation. The final v3 dry run passes with
  no serial port opened; malformed role, route, rule, effect, gate, and
  non-Ultimate-reference cases reject before serial access.

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
- Source-free human evidence: `repo-json:docs/calibration/fixtures/runtime_loaded_ultimate_profiles_stage_a_hardware_evidence_2026-10-11.json`.
  The owner reported complete H1–H15 PASS, exact A/B/A coordinate isolation,
  duplicate-name row selection, reboot/power-cycle persistence, and no
  evidence gaps for the recorded candidate/artifact/fixture tuple.

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
| Stage-B behavior inventory | fresh; read-only | Sol / medium | model UNKNOWN; effort UNKNOWN |
| Stage-B/C schema design | fresh; read-only | Sol / high | model UNKNOWN; effort UNKNOWN |
| Stage-B implementation | fresh, then resumed; sole schema/runtime writer | Terra / medium | model UNKNOWN; effort UNKNOWN |
| Stage-B independent review | fresh | Terra / medium | model UNKNOWN; effort UNKNOWN |
| Stage-C effect inventory | fresh; read-only | Sol / medium | model UNKNOWN; effort UNKNOWN |
| Stage-C initial implementation | fresh, then resumed; superseded partial implementation | Terra / medium | model UNKNOWN; effort UNKNOWN |
| Stage-C full integration | fresh; sole accepted Stage-C writer | Sol / high | model UNKNOWN; effort UNKNOWN |
| Final B+C independent review | fresh | Luna / medium | model UNKNOWN; effort UNKNOWN |
| Stage-C artifact adapter | fresh, then resumed; sole adapter writer | Terra / medium | model UNKNOWN; effort UNKNOWN |
| Stage-C adapter review | fresh, then fresh repair re-review | Luna / medium | model UNKNOWN; effort UNKNOWN |
