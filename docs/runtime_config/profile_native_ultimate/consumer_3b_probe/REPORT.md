# GP-NATIVE-001 affected-consumer recheck at3b

Exact frozen source: `3b792fd7e38e6eda9b93d6cdec0a452b1c607817`; tree `9ae1a60516c2aad0f02f20779e5ceba2937e76bf`. Root advanced the idle dedicated probe before this resumed finite task. This report preserves and supersedes no6e evidence; prior results remain in `/private/tmp/glyph-native-consumer-probe-results/`. Requested model/effort gpt-6.1-sol/medium; actual runtime UNKNOWN/UNKNOWN.

**27 checker invocations:19 PASS,8 FAIL,0 TIMEOUT.** Every permitted required host consumer was invoked, plus all4named historical mode/cache/button/capacity scripts. Native default-enum proof was executed at root request; writer-reported short proof was not duplicated or claimed as fresh worker evidence. Five target/build/resource commands were deferred explicitly. No full required-suite PASS, final-source review, target resource acceptance or hardware acceptance is claimed.

## Host matrix

Every row has complete original command/stdout/stderr/exit/timeout in its JSON `.log`; `statuses.json` records the matrix and exact snapshot/source hashes. All commands used PYTHONDONTWRITEBYTECODE=1,120seconds outer timeout, existing dependency runtime and stock script logic. Output flags point only into this new result directory. No scripts were patched or assertions bypassed by this worker.

| Actual script/arguments | State | Seconds | Cluster |
|---|---|---|---|
| `tools/check_glyph_stage_a_ultimate_profiles_dry_run.py` | PASS | 1.6 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_stage_b_ultimate_profiles.py` | PASS | 1.52 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_stage_c_ultimate_profiles.py` | PASS | 5.91 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_gp_bind_003_runtime_identity.py` | PASS | 38.58 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_production.py` | PASS | 0.06 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_production_tool.py` | PASS | 0.27 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_candidate_tool.py` | PASS | 0.21 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_strict_host.py` | PASS | 4.39 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_strict_protocol.py` | FAIL | 0.44 | MALFORMED_SOURCE_TUPLE |
| `tools/check_glyph_profile_store_request_identity.py` | PASS | 0.74 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_selection_recovery.py` | PASS | 4.42 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_config_persistence.py` | PASS | 2.84 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_migration_lifecycle.py` | FAIL | 0.46 | MALFORMED_STR_SOURCE_ARGUMENT |
| `tools/check_glyph_profile_store_atomic_commit.py` | PASS | 0.61 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_littlefs_host.py` | PASS | 1.0 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_read_storage.py --output-dir /private/tmp/glyph-native-consumer-probe-results-3b/read-storage` | FAIL | 12.79 | CURRENT_INSTRUMENTATION_ANCHOR |
| `tools/check_glyph_profile_store_directory_decoder.py` | PASS | 1.75 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_rx_host.py --output-dir /private/tmp/glyph-native-consumer-probe-results-3b/check_glyph_profile_store_rx_host` | PASS | 0.41 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_cdc_progress.py --output-dir /private/tmp/glyph-native-consumer-probe-results-3b/check_glyph_profile_store_cdc_progress` | PASS | 2.72 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_cdc_rx_progress.py --output-dir /private/tmp/glyph-native-consumer-probe-results-3b/check_glyph_profile_store_cdc_rx_progress` | PASS | 3.97 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_store_timeout_resynchronization.py` | FAIL | 0.46 | MALFORMED_SOURCE_TUPLE |
| `tools/check_glyph_stage_c_ultimate_profiles.py --default-enum` | PASS | 5.71 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_profile_native_ultimate.py --default-enum` | PASS | 24.79 | PASS_BOUNDED_HOST_SCOPE |
| `tools/check_glyph_config_010_mode_activation_capacity.py` | FAIL | 0.09 | BASELINE_REPRODUCED_SELECTOR_DEBT |
| `tools/check_glyph_custom_modifier_cache_characterization.py` | FAIL | 2.41 | BASELINE_REPRODUCED_C024_CONTEXT_DEBT |
| `tools/check_glyph_gp_config012_button_mask_characterization.py` | FAIL | 2.37 | BASELINE_REPRODUCED_C024_CONTEXT_DEBT |
| `tools/check_glyph_gp_config014_modifier_capacity.py` | FAIL | 2.36 | BASELINE_REPRODUCED_C024_CONTEXT_DEBT |

## Four current affected-consumer failures

1. `check_glyph_profile_store_migration_lifecycle.py:55`: `str(ROOT / "src/modes/UltimateNativeProfile.cpp", ROOT / "src/core/config_validation.cpp")` passes a pathlib.Path as the `encoding` argument. Actual error: `str() argument 'encoding' must be str, not pathlib.PosixPath`. Split these into two independent stringified source entries. No C++ lifecycle assertions were reached.
2. `check_glyph_profile_store_timeout_resynchronization.py:59`: the `(name,source)` iteration now has `("validation", nativeProfilePath, configValidationPath)`. Both required strict_protocol and full timeout_resynchronization exit `too many values to unpack (expected2,got3)`. Make two separately named two-element source tuples to link actual native-profile and validator objects. Their runtime strict/transport assertions were not reached in3b.
3. `check_glyph_profile_store_read_storage.py:55`: current instrumentation still requires old exact `if (out.schema_version <1` anchor. Production ReadProfile atline991 now uses `if ((out.schema_version <1 || out.schema_version >3) && out.schema_version != ultimate_native::kSchema)`. The frozen_d596 run completed6000READs and exact encoding/roundtrip fixtures; current candidate never compiled because instrumentation stopped. Add an exact current guard shape while retaining the historical frozen shape and phase2 position after successful decode, before schema validation. Do not mark current READ proof PASS based on the frozen output.

These are3distinct bounded launcher adapter defects affecting4commands. They were sent to writer/root immediately. No source behavior defect is inferred from Python argument/fixture-instrumentation failures; directly affected validation remains incomplete until exact repaired scripts run.

## Historical applicability debt reproduced independently atA

All4named scripts fail at exact current3b before their meaningful host cases. Each was rerun once in existing clean immutable adoption checkout `/private/tmp/glyph-native-curation-20261020`, HEAD`753932c8fbec3e002d455f4cd2b9b1dbc0ed896f`. All4stdout/stderr failures match current3b exactly; baseline remained clean. No global context/campaign helper or allowance was edited.

| Baseline command | Actual result | Identical stdout/stderr to3b |
|---|---|---|
| `tools/check_glyph_config_010_mode_activation_capacity.py` | FAIL | True |
| `tools/check_glyph_custom_modifier_cache_characterization.py` | FAIL | True |
| `tools/check_glyph_gp_config012_button_mask_characterization.py` | FAIL | True |
| `tools/check_glyph_gp_config014_modifier_capacity.py` | FAIL | True |

mode010 fails `HayBox selector drift`. cache011/button012/capacity014 fail `C024 post-integration change outside validation/evidence paths`. These are baseline-reproduced old applicability/selector debt; neither a current regression nor actual host-case PASS was established. If concrete affected-case proof is needed, use only the approved named-launcher adapters with immutable historical replay/current-interface verification; broader global helper changes remain outside scope.

## Actual proof counts and scope

- StageA PASS:6production admission negatives+1decoder negative; source-defined two-profile shape retained. StageB PASS:10negatives; v1/v2/v3 production validation and encoded-size custody.
- StageC PASS **both enumABIs**, each1,222,420complete-output comparisons against frozen legacy oracle, including A/B/A, remap/SOCD, storage order and host Nunchuk invariants. ShortABI50negatives=11decoder+39semantic; defaultABI50=9decoder+41semantic. Frozen StageA/B/C oracle/fixture files were not edited by this worker.
- GPBIND003 PASS both enumABIs, allV1–V3 payload digests, full canonical field omissions, observer mutants, isolated failedV4descriptor and production Configurator dispatch. Runtime observer footprint output24-byte service/56-byte snapshot retained. These host digest timings are raw, not a target timing guarantee.
- strict_host PASS24cases, zero failures,4frozen production negative controls, actual pinned LittleFS existing20admission; config_persistence PASS37cases. selection_recovery and directory_decoder now PASS with existing negative controls.
- Native `--default-enum` PASS:72independent legacy/native full-output corpus rows; native validation/field-order/legacy-duplicate/callback-lease/request-identity/embedded-rejection assertions;6SOCD policies/history;18family witnesses×60carrier rebindings; **1,124,032full-output frozen comparisons for eachV1,V2,V3**(3,372,096total).
- Frozen3b already contains `store_tests` and `native_store.cpp`: actual run passed20distinct independently converted bodies on pinned RAMNOR/LittleFS, revisions/staging/reserve/reboot/read/health/duplicate/cross-kind/context/unavailable assertions. Reported sizeof_store8712, total524288, used212992, free311296, protected241664, staging45056. These are the exact3bfixture assertions; they do not prove later-expanded full native lifecycle/resource requirements, complete target limits or hardware acceptance. No proof transfers to later source.
- Standalone LittleFS host PASS128replacements+128negative validations; RX host exact retained evidence/write-all tests PASS; CDCTX PASS1024repeated reads/147mixed rounds; CDCRX PASS1024mutation receptions/84read requests and retained/current DTR/fragmentation/timeout controls. These remain host evidence, no device equivalence claim.
- Production checker PASS_SOURCE_COMPOSITION only(noELF/compile-db). Production/candidate tool, request identity and atomic commit PASS their bounded tests.

## Explicit non-runs

| Required command | State | Reason |
|---|---|---|
| `python3 tools/check_glyph_profile_store_directory_stack.py` | NOT_RUN_SCOPE | Target ARM production TU compilation; outside host-consumer scope and deferred to exact candidate target resources. |
| `python3 tools/check_glyph_profile_store_create_stack.py` | NOT_RUN_NO_EXACT_BUILD_RESOURCE_INPUT | Needs actual compile_commands.json/build/ELF and recompiles target inputs. No firmware build or shared build output permitted. |
| `python3 tools/check_glyph_profile_store_read_stack.py` | NOT_RUN_NO_EXACT_RESOURCE_JSON | Requires --resources exact candidate resourceJSON --output; production use requires --production. No fabricated/stale resources supplied. |
| `python3 tools/check_glyph_profile_store_rx_stack.py` | NOT_RUN_NO_EXACT_RESOURCE_JSON | Requires --resources exact candidate resourceJSON --output. No fabricated/stale resources supplied. |
| `pio run -e glyph_mk6` | NOT_RUN_SCOPE | Firmware build prohibited for this finite interface/proof worker. |
| `python3 tools/check_glyph_profile_native_ultimate.py` | SHORT_ENUM_NOT_DUPLICATED_BY_PARENT_REQUEST | Writer reported short-enum proof; this worker ran --default-enum at exact3b instead. No fresh short-enum PASS inferred by this worker. |

## Environment, hashes and final state

Nanopb0.4.92; host protobuf7.36.2/grpcio-tools1.84.0; Apple clang21.0.0 arm64-apple-darwin27. `snapshot.json` binds151allowed source/checker/fixture file hashes, compiler/dependency identity and exact links. Fresh generated binding SHA emitted by GPBIND003: config.pb.h`efd4850ee94fe32c52c8cff1a93021ad2a4959d04615a1463c1e54a845b63c4f`; config.pb.c`fce08045cd7da7795357dff85827a634ef6a7f3fb21ec32e89b0e84817c54750`. Actual generator scratch path is preserved in its raw log; TemporaryDirectory cleanup is normal. No shared build outputs were used or modified.

Probe tracked tree remains clean; final status only intentional root-created `?? .platformio-home` dependency symlink. BaselineA tracked tree remains clean. No repository/dependency/Git mutation, network/account operation, device action or firmware build was performed. Source writer owns repair; final exact validation/source review/build/resources/hardware remain separate gates.
