# Runtime-Loaded Ultimate Profiles Chapter Ledger

Status: `FINAL_BC_PRE_STAGE_C_BOOT_FAILED` — exact source/artifact preserved; bounded cross-version recovery bridge in preparation.

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
| C — bounded output effects | source/host proof PASS; final boot hardware FAIL | Bounded v3 proof remains valid, but the exact final candidate rejected the Clean-generated persisted Config before any Stage-C write. A reviewed cross-version bridge is the next bounded hardware step. |

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
  3,182, and two/max profiles 6,242 bytes after the explicit recovery envelope.
  The two-profile final-gate fixture SHA-256 is
  `c91f2bb04a1ec70fe68acf8e54be8ed7687a4dd427823a1f943780d13bd786d3`;
  its writer payload SHA-256 is
  `898f0efd71282862e8e567b6bd9633e6577c05cca5cd65bc562ca83256386b6a`.

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
- Final runtime-profile fixture (corrected full-Config envelope):
  `tools/fixtures/stage_c_ultimate_profiles_dry_run.json`, SHA-256
  `c91f2bb04a1ec70fe68acf8e54be8ed7687a4dd427823a1f943780d13bd786d3`;
  encoded writer payload 6,242 bytes, SHA-256
  `898f0efd71282862e8e567b6bd9633e6577c05cca5cd65bc562ca83256386b6a`.
- The tracked serial adapter accepts only the same bounded v1/v2/v3 structural
  shapes required by production validation. The final v3 dry run passes with
  no serial port opened; malformed role, route, rule, effect, gate, and
  non-Ultimate-reference cases reject before serial access.

## Proven Config-envelope replacement defect and repair

- Classification: `PROVEN_CONFIG_ENVELOPE_REPLACEMENT_DEFECT`. This is an
  artifact/envelope defect, not a firmware, USB, or runtime-profile
  architecture failure.
- Source proof: `HAL/pico/src/comms/ConfiguratorBackend.cpp` initializes a
  `Config_init_default` candidate, decodes the submitted complete Config into
  it, validates it, and saves/publishes it; the Configurator SET path is full
  replacement rather than a merge. `HAL/pico/src/display/DefaultConfigMenu.cpp`
  enters Configurator only after finding `COMMS_BACKEND_CONFIGURATOR` in the
  persisted backend rows. `HAL/pico/include/config_defaults.hpp` provides that
  row with `BTN_RT2` activation in the canonical default Config.
- The old Stage-A and Stage-C hardware fixtures supplied only
  `COMMS_BACKEND_XINPUT`. After the Stage-A Config replacement, the menu had no
  Configurator row to select and RT2 had no Configurator activation binding.
- The source-free Stage-A record now preserves the original H1-H15 result and
  explicitly records `POST_STAGE_A_CONFIG_CONFIGURATOR_ACCESS: FAIL` and
  `POST_STAGE_A_CONFIG_RT2_CONFIGURATOR_ACTIVATION: FAIL`. H2's original PASS
  applies after firmware flashing and before the Stage-A Config replacement;
  Stage-A coordinate loading, explicit row/reference selection, duplicate-name
  independence, A/B/A isolation, reboot, and power-cycle persistence remain
  physically proven.
- Final-gate artifact rule: `FINAL_GATE_CONFIGURATOR_RECOVERY_REQUIRED = true`.
  This applies only to this hardware fixture/handoff, not generic Config
  validity. The fixture explicitly supplies XInput plus exactly one
  Configurator backend with `activationBinding: BTN_RT2`; its backend/default
  mode references are checked against its three actual game-mode rows.
- Future runtime-profile exporters must explicitly supply or preserve the
  ordinary complete Config envelope they intend to retain. They must not
  silently emit an XInput-only full Config merely because their owned data is
  Ultimate-specific. Intentionally Configurator-less Configs remain permitted
  by generic Config validation.
- Focused repair proof: JSON/protobuf exact round-trip, Nanopb production
  decode, production `validate_glyph_config`, serial-free tool dry-run,
  Configurator/RT2 presence checks, and invalid backend/default-reference
  negatives pass under both host enum ABIs. The direct Stage-C correspondence
  proof also passes. Fresh independent artifact review: APPROVED.
- Production source candidate `16fb02a5eaaa95e63870d14593376c9d1f15aed2`
  and tree `13ad3a19e4cb1ae19fd866ad48cb55a96897e630` are unchanged. The
  exact 832,000-byte UF2 `c178cc2e39a6d2eceee27c16b9aae1364a04d628f1ca20bd28fc78a798c04830`
  remains the valid final firmware artifact; it was not rebuilt.

## Owner-only final recovery and grouped hardware packet

- Current-controller recovery proposal: with explicit owner authorization,
  manually copy the repository-archived user-provided official Fresh Install /
  Clean image to RPI-RP2:
  `docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7-Clean.uf2`.
  Verified identity: 1,818,112 bytes, SHA-256
  `22fd7f8f29fb33d9cb601187e9503411e5330e72c7297fbce0df710eec8ff200`.
  The recorded official procedure says Fresh Install wipes profiles and restores
  factory defaults, so this action is destructive and requires a separate
  explicit owner approval immediately before device action. No device action
  was performed by this chapter.
- After recovery: confirm menu Configurator entry and RT2 Configurator boot;
  flash the unchanged final UF2; confirm Configurator before Config write;
  write this corrected fixture; reboot; then record PASS for
  `POST_WRITE_MENU_CONFIGURATOR_ACCESS`,
  `POST_WRITE_RT2_CONFIGURATOR_ACCESS`, and
  `POST_POWERCYCLE_MENU_CONFIGURATOR_ACCESS`, alongside the grouped B+C
  behavior matrix and persistence check.

## Final B+C pre-Stage-C boot failure and recovery bridge

- Source-free exact hardware record:
  `docs/calibration/fixtures/runtime_loaded_ultimate_profiles_final_bc_pre_stage_c_boot_failure_2026-10-12.json`.
  Physical classification is `FAIL` at `FINAL_BC_PRE_STAGE_C_BOOT`.
  The owner reported that after the approved official Clean recovery passed both
  Configurator checks, the rehashed exact final UF2 re-enumerated and displayed
  `Stored Config rejected / Recovery required / Operation refused`. No
  Stage-C Config write, retry, rollback, source/fixture change, rebuild, or
  later device action occurred. The macOS extended-attribute copy warning is
  recorded but is not classified as root cause because the device re-enumerated
  and displayed the final candidate's exact refusal screen.
- No independent HEP has reinterpreted the physical result: it remains an
  exact human `FAIL`, not `INCONCLUSIVE`.
- Exact source mapping: `config/glyph/common/src/config.cpp` validates
  compiled defaults, calls `Persistence::LoadConfigChecked`, maps only
  `LoadResult::Rejected` to `BootOutcome::StoredConfigRejected`, and renders
  the observed three-line screen. `HAL/pico/src/core/Persistence.cpp` can
  return that result for a short/size-mismatched/CRC-invalid file, malformed
  protobuf decode, or failed production semantic validation. The screen alone
  cannot select among those cases.
- Header compatibility is source-supported but not proven for this controller:
  official 1.0.7 tag `9a78c7eeec87527b68644573e4c29fbdfb543239` and the
  final candidate use the same native `ConfigHeader` shape (size plus CRC) and
  the same write/check order. Exact stored header bytes were not captured, so
  file-integrity rejection remains possible. Protobuf field compatibility is
  source-proven for the bridge's legacy-only fields, but the particular Clean
  factory payload remains unobserved.
- `SUSPECTED_LEGACY_CLEAN_CONFIG_VALIDATION_INCOMPATIBILITY`: C022 gives a
  strong deterministic candidate explanation, not proof of this unit's stored
  payload. The official 1.0.7/pre-C022 Glyph default has RGB block 11 with a
  declared count of 20 and only 11 initialized entries; the nine aggregate
  initialized tail entries are `BTN_UNSPECIFIED`. Current RGB validation
  rejects each populated unspecified/nonphysical target. Existing C022 host
  evidence proves the reconstructed legacy shape rejects and the corrected
  11-entry/black-LF1 shape accepts. It becomes the exact hardware cause only
  if a captured Clean payload or full stored file matches it and reproduces the
  present rejection.
- Other possible `Rejected` classes remain malformed protobuf and current
  semantic checks for extent, populated bindings, USB/default backend and
  default-mode references, custom/keyboard references, RGB targets, and any
  present runtime profile. No source evidence currently identifies one of
  these for the exact Clean-generated bytes.

### Reviewed cross-version bridge artifact

- Tracked bridge: `tools/fixtures/final_bc_cross_version_bridge_config.json`.
  It is not a final runtime-profile Config: it has one `MODE_ULTIMATE`
  row with only the serial-adapter-required identity remaps RF3/RF4/LT3,
  XInput with default mode 1, one Configurator backend with exactly `BTN_RT2`,
  defaults `defaultBackendConfig=1` and
  `defaultUsbBackendConfig=1`, and no RGB, custom, keyboard, or Ultimate
  profile data. It intentionally omits Configurator default mode, matching the
  official default's zero/unspecified form.
- Its encoded protobuf is 39 bytes, SHA-256
  `c7a2cb264ffd37b6ec6a0b0c59853815d507671b2ce1f8208d9dbcd8d0310c74`;
  fixture SHA-256
  `5ef3e66474e37675452bae7fae9ba77c099a153796d03277513f1d4eda8adf8b`.
- Source-level Clean compatibility: official tag `9a78c7ee` pins
  HayBox-proto `5b2bb5d2c2a212647d5aaef7d5dc794be5197ecb`; the bridge uses
  only matching legacy field numbers/types and enum values (Ultimate=3,
  XInput=2, Configurator=8, RT2=42). Its SET path decodes replacement Config,
  validates default/backend-mode references, and permits this shape. This is
  not a claim of observed Clean SET success.
- Current-side proof passes exact JSON/protobuf round-trip, current Nanopb
  decode and production validation, envelope and invalid binding/RGB/backend
  negatives, and serial-free dry run. Fresh independent bridge review:
  APPROVED. No generic writer, production source, schema, or final firmware
  artifact changed.
- The next recovery run must first use Clean Configurator GET_CONFIG to capture
  the raw fresh factory protobuf body, decoded JSON, byte size, and hash before
  bridge SET. It must also preserve the complete stored file/header separately
  if available; ordinary GET does not establish header/CRC compatibility.
  The captured body must be run through the final candidate decoder/validator
  and any validator error recorded before it is overwritten.

### Revised owner-only terminal packet

1. Verify live branch/artifact identities and obtain a **new explicit owner
   approval** for destructive Clean flashing.
2. Flash the exact Clean UF2 with a locally verified byte-copy command that
   suppresses macOS extended attributes (for example the applicable `cp -X`
   form); stop if an unexpected result occurs.
3. Require Clean menu and RT2 Configurator PASS, then GET and preserve the
   fresh factory Config evidence described above.
4. Write the reviewed bridge; require protocol success and exact immediate
   GET_CONFIG readback, then reboot/reconnect Clean and verify bridge
   persistence.
5. Rehash and flash the unchanged final B+C UF2. Require normal boot,
   pre-write menu Configurator PASS, pre-write RT2 Configurator PASS, and
   backup of the bridge Config under final firmware.
6. Write the already-reviewed corrected Stage-C Config, require exact
   readback, post-write menu/RT2 Configurator PASS, the grouped B+C matrix,
   power-cycle persistence, and post-power-cycle menu Configurator PASS.
   Stop at the first unexpected result; no automatic retry or firmware patch.

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
| Final Config-envelope repair | fresh; sole fixture/checker writer | Terra / medium | model UNKNOWN; effort UNKNOWN |
| Final Config-envelope artifact review | fresh; independent review | Luna / medium | model UNKNOWN; effort UNKNOWN |
| Rejection diagnosis | fresh; read-only | Sol / medium | model UNKNOWN; effort UNKNOWN |
| Clean compatibility inventory | fresh; read-only | Luna / medium | model UNKNOWN; effort UNKNOWN |
| Cross-version bridge artifact | fresh; sole fixture/checker writer | Terra / medium | model UNKNOWN; effort UNKNOWN |
| Cross-version bridge review | fresh; independent review | Luna / medium | model UNKNOWN; effort UNKNOWN |
