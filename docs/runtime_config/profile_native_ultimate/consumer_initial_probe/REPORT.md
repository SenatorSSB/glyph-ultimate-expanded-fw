# GP-NATIVE-001 finite affected-consumer probe

Snapshot: `6e6ea894abdf699ea5761cbf5d3a62c072db8dfa`, tree `15152fd22b0ac4484cd60d7b5c96bda18afbd250`. This is the root-frozen intermediate source, not the final candidate. Initial28cd inspection produced no checker execution; root explicitly moved the dedicated checkout before all checks. Requested gpt-6.1-sol/medium; runtime observed UNKNOWN/UNKNOWN.

No source, test, checker, schema, docs, queue, dependency runtime, device, account or remote edits/actions were performed by this probe. Stock host checker scratch outputs used their own temporary directories; retained output is under this report directory. `PYTHONDONTWRITEBYTECODE=1` throughout checker invocations. Tracked tree remains clean. Initial/final status is only root-created `?? .platformio-home`; its existing link was preserved. No firmware build was invoked.

## Actual results

21 stock checker commands ran: 9 PASS, 12 FAIL, zero timeout. These are bounded host results. Native implementation, full required suite, build/resource acceptance and hardware are not established. Exact per-command arguments, exit codes, complete raw stdout/stderr, timeouts, source hashes and dependency links are in statuses.json and individual command logs. The `production` PASS is only PASS_SOURCE_COMPOSITION (no ELF or compile database supplied).

| Checker | Result | Cluster | Seconds |
|---|---|---|---|
| check_glyph_stage_a_ultimate_profiles_dry_run.py | FAIL | MISSING_NATIVE_PROFILE_TU | 1.23 |
| check_glyph_stage_b_ultimate_profiles.py | FAIL | MISSING_NATIVE_PROFILE_TU | 0.87 |
| check_glyph_stage_c_ultimate_profiles.py | FAIL | FROZEN_SHARED_SOURCE_PIN_ADAPTER | 0.24 |
| check_glyph_gp_bind_003_runtime_identity.py | FAIL | REMOVED_GENERATED_SIZE_MACRO | 4.12 |
| check_glyph_profile_store_production.py | PASS | PASS_BOUNDED_HOST_SCOPE | 0.07 |
| check_glyph_profile_store_config_persistence.py | FAIL | MISSING_NATIVE_PROFILE_TU | 2.33 |
| check_glyph_profile_store_read_storage.py | FAIL | REMOVED_GENERATED_SIZE_MACRO | 3.05 |
| check_glyph_config_010_mode_activation_capacity.py | FAIL | OLD_SELECTOR_CONTEXT | 0.1 |
| check_glyph_custom_modifier_cache_characterization.py | FAIL | OLD_C024_APPLICABILITY_CONTEXT | 2.49 |
| check_glyph_gp_config012_button_mask_characterization.py | FAIL | OLD_C024_APPLICABILITY_CONTEXT | 2.73 |
| check_glyph_gp_config014_modifier_capacity.py | FAIL | OLD_C024_APPLICABILITY_CONTEXT | 2.46 |
| check_glyph_profile_store_production_tool.py | PASS | PASS_BOUNDED_HOST_SCOPE | 0.64 |
| check_glyph_profile_store_candidate_tool.py | PASS | PASS_BOUNDED_HOST_SCOPE | 0.21 |
| check_glyph_profile_store_strict_protocol.py | FAIL | MISSING_NATIVE_PROFILE_TU | 4.96 |
| check_glyph_profile_store_request_identity.py | PASS | PASS_BOUNDED_HOST_SCOPE | 0.83 |
| check_glyph_profile_store_selection_recovery.py | FAIL | HOST_DOUBLE_INTERFACE_ADAPTER | 0.53 |
| check_glyph_profile_store_atomic_commit.py | PASS | PASS_BOUNDED_HOST_SCOPE | 0.58 |
| check_glyph_profile_store_littlefs_host.py | PASS | PASS_BOUNDED_HOST_SCOPE | 1.6 |
| check_glyph_profile_store_rx_host.py | PASS | PASS_BOUNDED_HOST_SCOPE | 0.75 |
| check_glyph_profile_store_cdc_progress.py | PASS | PASS_BOUNDED_HOST_SCOPE | 2.58 |
| check_glyph_profile_store_cdc_rx_progress.py | PASS | PASS_BOUNDED_HOST_SCOPE | 3.58 |

## Concrete compatibility findings and minimal bounded mappings

1. **Production native-profile translation unit omitted.** Stage A/B link the current `src/core/config_validation.cpp` but omit `src/modes/UltimateNativeProfile.cpp`, yielding undefined `ultimate_native::ValidProfile`. Config persistence additionally lacks `RejectPayload`, `RejectEmbedded` and `ClearEmbeddedCallbacks`. `strict_protocol` fails in imported `timeout_resynchronization.build_and_run`, with DecodeProfile/PrepareRequest/Bind/BindOwned/PreserveProfile/ContextMatches etc. Production validator/ProfileStore/Configurator consumers need the actual native-profile TU added to their approved launcher source lists. Stage A/B/C also omit `pb_encode.c`; the native-profile TU's Encode uses pb_encode_tag_for_field/pb_encode_string so add the actual Nanopb encode C object. No stub validation or linker allowance is justified. Launchers compiling Ultimate additionally require `src/modes/UltimateNativeEvaluator.cpp`, because current Ultimate references Neutral/Evaluate. Keep both enum variants and existing assertions.

   Actual missing-TU representatives are Stage A/B, config_persistence and strict_protocol. Static same-family mapping: strict_host, migration_lifecycle, read_storage current/frozen-validator source lists, directory_decoder, and GPBIND003 observer/dispatch source lists. `directory_decoder` uses section garbage collection; unused native references might be discarded, so this report does not claim it fails. `timeout_resynchronization` shares the exact helper concretely exercised by strict_protocol; no repeated full invocation was needed.

2. **Callback schema removed generated size macros.** GPBIND003 `tools/fixtures/gp_bind_003_runtime_identity/observer.cpp:150` cannot compile `UltimateProfile_size`. Read storage's `tools/fixtures/profile_store_read_storage/read_observer.inc:12,27` cannot compile `ProfileStoreResponse_size`/`UltimateProfile_size`. Both named observer files are explicitly allowed. Use explicit admitted-profile/frame bounds derived from current production constraints plus real `pb_get_encoded_size` and actual encoding assertions; preserve all fixture roundtrips, counts and failures. Do not substitute `3341` as a maximum for all legacy profile shapes: that constant is the native-only wrapper bound. The actual admitted standalone wire cap is4096; response capacity8192 must still cover envelope and other bounded fields, and diagnostics must truthfully describe admitted bounds rather than a generated schema maximum. Current RuntimeProfileDigest already uses4096. Do not invent enclosing protobuf maxima or increase buffers/limits.

3. **Stage C current shared-source pin intentionally fails.** The unconditional shared-source dictionary expects ControllerMode.cpp SHA1278a7e...; actual default-preserving-hook source SHA is `5a8615740951ad8ab5b07104b38d5842d3a91537e4c1690d47a416f554dcd524`. Stock Stage C stops before compilation, in either enum ABI. A launcher-only exact native-source compatibility verification must preserve historical frozen oracle bytes/hashes and independently verify the hook's preserved legacy path, then compile the actual current profile/evaluator and pb_encode dependencies. Do not change frozen oracle source/header/fixtures or erase the shared-source assertion without equivalent scoped integrity proof. All1,222,420 full-output comparisons remain required in final validation.

4. **Mode-selection fixture lacks the actual new method.** `selection_recovery` compiles mode_selection.cpp against a ProfileStore host double lacking `ActiveNativeView`; failure at mode_selection.cpp:133. Its fixture header is outside closed allowed_test_paths. An approved launcher may generate an exact scratch compatibility header from the immutable fixture, with only the absent native-view method/type declaration and preserving the original Activate double and all existing assertions; otherwise return for separate path authority. The fixture's Ultimate double must also accept the native-view third SetConfig parameter, if its existing variadic API does not already do so. This is an interface recommendation, not a source implementation or adapter proof.

5. **Historical current-applicability gates stop the named cache/button/capacity checks.** cache011, button012 and capacity014 fail `C024 post-integration change outside validation/evidence paths` before host compilation. mode010 fails `HayBox selector drift` in the historical `validate_inputs` selector hash before its seven cases. These are exact observed old-context failures, not a demonstrated native gameplay regression; they still leave directly affected proof incomplete. No relevant CLI base/context override exists in these scripts. Their authorized launcher adapters need separate immutable historical replay and exact current native-interface applicability, retaining fixtures/pins/cases/negative assertions. Do not modify global campaign/context helpers or broaden their allowances. mode010 also checks historical source hashes after selectors; later direct mode source includes the new native view parameter, so mere selector bypass cannot produce valid current proof. Runtime context/authentication redesign is outside scope.

## Required checks not executed

Repeated failure families were bounded; no partial native final-suite success is implied.

| Required command | Disposition | Reason |
|---|---|---|
| `python3 tools/check_glyph_profile_store_strict_host.py` | STATIC_MAPPED_NOT_RUN | Links current ProfileStore/config_validation but omits UltimateNativeProfile.cpp; same missing-TU family as strict_protocol. |
| `python3 tools/check_glyph_profile_store_migration_lifecycle.py` | STATIC_MAPPED_NOT_RUN | Links current ProfileStore/config_validation but omits UltimateNativeProfile.cpp; same missing-TU family as strict_protocol. |
| `python3 tools/check_glyph_profile_store_directory_decoder.py` | STATIC_MAPPED_NOT_RUN | Current ProfileStore and validator object lists omit UltimateNativeProfile.cpp. Section garbage collection may discard unused references; no failure or PASS inferred. |
| `python3 tools/check_glyph_profile_store_timeout_resynchronization.py` | STATIC_MAPPED_NOT_RUN | strict_protocol imports and executes its build_and_run; concrete same linker cluster obtained through strict_protocol. |
| `python3 tools/check_glyph_stage_c_ultimate_profiles.py --default-enum` | STATIC_MAPPED_NOT_RUN | Same unconditional shared ControllerMode.cpp hash check before ABI-dependent compilation. |
| `python3 tools/check_glyph_profile_store_directory_stack.py` | DEFERRED_TARGET_RESOURCE_CHECK | Compiles production TU with target ARM compiler; outside finite no-target-build probe. |
| `python3 tools/check_glyph_profile_store_create_stack.py` | DEFERRED_TARGET_RESOURCE_CHECK | Needs actual compile_commands.json/ELF/build and invokes target compilers; do not reuse writer output or stale report. |
| `python3 tools/check_glyph_profile_store_read_stack.py` | DEFERRED_EXACT_RESOURCE_INPUT | Requires --resources exact target resource JSON --output; final production needs --production. No exact resource input generated by this probe. |
| `python3 tools/check_glyph_profile_store_rx_stack.py` | DEFERRED_EXACT_RESOURCE_INPUT | Requires --resources exact target resource JSON --output. No exact resource input generated by this probe. |
| `python3 tools/check_glyph_profile_native_ultimate.py` | OUTSIDE_AFFECTED_LEGACY_PROBE | Native checker owned by writer; independent semantic review/final exact native proof remains required. |
| `pio run -e glyph_mk6` | PROHIBITED_BY_PROBE_SCOPE | No firmware build/device/network actions authorized for this finite probe. |

## Environment and custody

Host compiler: Apple clang21.0.0, arm64-apple-darwin27. Nanopb library0.4.92; pb.h SHAe0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2 and generator SHA67d3c5e6de1e5dbd9f45bb4e5b7055d888d1afd6d6e1690791ab8607b6c6b738. Current host Python distributions are protobuf7.36.2/grpcio-tools1.84.0, distinct from older fixture-recorded6.33.6/1.80.0; no dependency install or version mutation occurred. Pinned actual LittleFS host and CDC TX/RX checks passed using current available Arduino-Pico1.30603.0. The newer host generator versions are environment facts, not the cause of the concrete missing-symbol/macro failures.

Stock production-schema generators wrote fresh config.pb.h/.c into their own logged scratch locations, including StageA `stage-a-admission-oqlfl8ik`, StageB `stage-b-ultimate-oh9gus2i/generated`, GPBIND003 `gp-bind003-proof-zfkebag9/generated`, config persistence `profile-config-persistence-qmjtwqpw/generated`, read storage `glyph-read-storage-x3dq1rhb/generated`. Stock TemporaryDirectory cleanup removed these outputs; no final descriptor hash is claimed. Logs preserve full actual paths. snapshot.json and consumer-source-hashes.json bind production schema/options/native sources and named checkers/observers. Exact final generated bindings must be hashed in final candidate validation.

Findings were sent directly to sole source writer and root as they emerged. All adapters remain writer-owned and require fresh exact-source validation/review. No final hardware/build/native semantic claim follows from this finite intermediate compatibility probe.
