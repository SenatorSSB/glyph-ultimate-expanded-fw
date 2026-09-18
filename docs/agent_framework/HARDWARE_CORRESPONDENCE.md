# Hardware correspondence

Status: current GP-VAL-015 host validation contract. No firmware behavior change.

Hardware acceptance binds the immutable tested candidate commit, tree, direct
parent, preserved artifact SHA-256 and exact hardware PASS evidence. Integration
must contain that same candidate as an ancestor. A recreated, rebased or
reimplemented candidate is not a substitute. Identity and authorization checks
remain in the operator and agent-surface callers.

`tools/glyph_hardware_correspondence.py` independently verifies the candidate's
direct tested parent and phase ancestry, classifies its complete changed-path
set, and compares the complete tested snapshot with the target. After integration
the snapshot is the candidate; before integration it is the tested base. Every
critical difference fails, including a path untouched by the historical candidate,
an addition, deletion, rename, type change or executable-bit change. This preserves
GP-VAL-014's useful ancestry and narrow protected-source applicability checks.

## Classification and scope

`CRITICAL` covers conservative firmware roots (`src`, `include`, `HAL`/`hal`,
`backend`, `lib`, `active`, `storage`, `config`), build hooks/scripts, boards,
variants, patches, protocol inputs and declared build controls. PlatformIO,
workflows, `glyph_nuker`, dependency controls and Git attributes/ignore policy
are protected. Critical classification always takes precedence over metadata.
This intentionally overprotects some inert files within source roots.

`NON_BEHAVIORAL` is a finite exact-path inventory reviewed against the dependency
graph below. Neither a `docs/` or `tools/` prefix, a file extension, the word
`generated`, nor a fixture-like filename grants an exemption. Unknown paths fail
closed, including unchanged-after-integration paths introduced by the candidate.
New inventory entries require source/dependency review and ordinary authorization.
The module does not dynamically trust paths supplied by a changed manifest.

The inventory includes the 22 audited candidate metadata/host paths below;
subsequent exact control-plane, operator, test, hardware-evidence and documentation
paths between that candidate and canonical `06903092e086e65904be1ae09e6f377fac50728e`;
the narrowly related framework/navigation validators and workflow/hardware/gate
documentation; and this repair's helper, tests, contract and integration report.
These host programs run explicitly in validation or operator workflows, not as
PlatformIO inputs. Their classification does not authorize device operations,
evidence rewriting, or governance changes. Those retain their separate gates.

Nonbehavioral files must be ordinary Git `100644` blobs. Symlinks, gitlinks,
executables and malformed/ambiguous paths fail. Git path output uses NUL records
and disables rename folding so both sides of a move are inspected. Staged,
unstaged and untracked critical or unknown paths fail. Ignored untracked paths
within critical roots/build controls also fail: Git ignore policy does not stop
a compiler from reading them. The ignored-file inspection deliberately excludes
the separate `.pio` dependency cache. Disposable caches inside protected roots
must be absent during acceptance verification. Metadata working paths also reject
symlinked directories and nonregular/executable files.
Every indexed critical working file is independently checked by raw Git-blob
SHA-1, executable mode and regular-file/parent-directory inspection. This does not
trust Git's stat cache, assume-unchanged or skip-worktree optimizations to report
dirty source. A missing tracked critical file also fails.

This helper proves input correspondence only. All ordinary source-sync, scope,
census regeneration, fixture, protocol, provenance, queue, evidence and governance
checks still apply. A hardware-correspondence PASS cannot make malformed census
metadata valid. The focused test suite demonstrates this using the real census
validator on both valid regenerated and invalid metadata.

## Source and build dependency evidence

`platformio.ini` supplies `src_dir = ./`, source filter `+<src/>`, include roots
`src/` and `include/`, then Pico source filter `+<HAL/pico/src>` and include root
`HAL/pico/include`. `config/glyph/env.ini` inherits that Pico environment and adds
`config/glyph/common/src`, `config/glyph/${PIOENV}` and their include directories.
The canonical environment is `glyph_mk6`. Neither docs nor host-fixture directories
are selected by those filters/include roots.

The only declared Pico extra script is `builder_scripts/arduino_pico.py`.
PlatformIO's nanopb inputs come from declared `.pio/libdeps/${PIOENV}/HayBox-proto`
dependencies. The host fixture's `config.pb.h` is never the firmware protobuf input.
`check_glyph_configurator_setconfig_transaction.py` explicitly compiles its own
host harness using `-I tools/fixtures/configurator_setconfig_host/include` and
`-I HAL/pico/include`. The harness includes production source/header; production
does not include the harness or stubs.

`Ultimate.cpp` includes `UltimateIdentityRuntimeTables.hpp`, which includes
`src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`.
That generated header supplies active compile-time runtime tables and is critical.
Being generated does not make an artifact inert. The existing source-sync
validators retain their independent semantic and fixture correspondence checks.

`build_input_provenance_inventory.md` and its checker document the declared
PlatformIO/configuration/workflow/local-entrypoint/postprocessor boundary. That
inventory supplies reusable build-control authority, not a complete resolved
dependency or reproducibility proof. The runtime validation manifest's
`source_dependencies` mixes host, docs and firmware dependencies and is therefore
not a firmware-input classifier.

The census generator reads/hashes `tools/check_glyph_*.py` and statically extracts
AST/text facts; it never imports or executes discovered checkers. Census consumers
are the census checker, runtime validation health checker, aggregate runner and
their synthetic tests. No inspected firmware/include/build-hook input consumes its
bytes. Census validity gates repository validation but does not provide compiled
firmware data. The census keeps its existing freshness and integrity validators.

## Exact candidate audit

Candidate `437f87e8086a50f0dfbd834176b80d245c1ed307`, direct parent
`9550a1bf1309383e351f4f9e66663562fc9f13ac`, changes exactly these 23 paths.

| Path | Classification and consumer |
| --- | --- |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp` | Critical: Pico firmware source filter. |
| `docs/runtime_config/current_config_persistence_recovery_research.md` | Nonbehavioral: offline research checker input. |
| `docs/runtime_config/fixtures/configurator_setconfig_transaction.json` | Nonbehavioral: host handler-test contract. |
| `docs/runtime_config/fixtures/current_config_persistence_recovery_research.json` | Nonbehavioral: offline research fixture. |
| `docs/runtime_config/fixtures/glyph_checker_census.json` | Nonbehavioral: deterministic host checker census. |
| `docs/runtime_config/fixtures/runtime_config_validation_health.json` | Nonbehavioral: validation health inventory. |
| `docs/runtime_config/fixtures/runtime_config_validation_manifest.json` | Nonbehavioral: host validation commands/dependencies. |
| `docs/runtime_config/runtime_config_validation_health.md` | Nonbehavioral: validation health documentation. |
| `tools/check_glyph_configurator_setconfig_transaction.py` | Nonbehavioral: explicit host compiler/runner. |
| `tools/check_glyph_current_config_persistence_recovery_research.py` | Nonbehavioral: offline research correspondence validator. |
| `tools/fixtures/configurator_setconfig_host/handler_harness.cpp` | Nonbehavioral: host-only translation unit. |
| `tools/fixtures/configurator_setconfig_host/include/arduino/Adafruit_USBD_Device.h` | Nonbehavioral: host USB stub. |
| `tools/fixtures/configurator_setconfig_host/include/cobs/Print.h` | Nonbehavioral: host stream stub. |
| `tools/fixtures/configurator_setconfig_host/include/cobs/Stream.h` | Nonbehavioral: host stream stub. |
| `tools/fixtures/configurator_setconfig_host/include/config.pb.h` | Nonbehavioral: host Config shape substitute. |
| `tools/fixtures/configurator_setconfig_host/include/core/CommunicationBackend.hpp` | Nonbehavioral: host backend stub. |
| `tools/fixtures/configurator_setconfig_host/include/core/InputSource.hpp` | Nonbehavioral: host input stub. |
| `tools/fixtures/configurator_setconfig_host/include/core/Persistence.hpp` | Nonbehavioral: host persistence substitution. |
| `tools/fixtures/configurator_setconfig_host/include/host_stubs.hpp` | Nonbehavioral: host platform definitions. |
| `tools/fixtures/configurator_setconfig_host/include/pb_arduino.h` | Nonbehavioral: host protobuf transport stub. |
| `tools/fixtures/configurator_setconfig_host/include/pb_decode.h` | Nonbehavioral: host decoder stub. |
| `tools/fixtures/configurator_setconfig_host/include/pb_encode.h` | Nonbehavioral: host encoder stub. |
| `tools/fixtures/configurator_setconfig_host/include/reboot.hpp` | Nonbehavioral: host reboot substitution. |

Whole-candidate-path equality was introduced by GP-VAL-014 commit
`0f7f71bfff4b9488d8b148c6eb155ad20cc05589` in both the operator verifier and
agent-surface integration predicate. Git history and the prior versions contain
no earlier whole-candidate-path rule. The unpushed diagnostic merge
`8220bc4c05c5fcb53f0bc5a7a52f0646bea311cd` preserves all critical source/build
inputs; its sole candidate-path mismatch is the legitimately evolved census.
It remains diagnostic evidence only, never the final integration candidate.

The current GP-CONFIG-006 host-only branch additionally changes
`tools/glyph_serial_config_tool.py`. It is audited as `NON_BEHAVIORAL` in the
correspondence checker because it records host transport boundaries without
changing firmware, build inputs, or encoded command bytes; this current-cycle
path is not part of the historical GP-CONFIG-005 candidate inventory above.

## Artifact identity and limitations

`builder_scripts/arduino_pico.py` embeds Git HEAD plus dirty status into
`FIRMWARE_VERSION`. `AboutMenu.cpp` displays it and `ConfiguratorBackend.cpp`
returns it. A new merge build therefore has different version identity and is
not asserted byte-identical to, or physically accepted as, the original UF2.
Exact preserved artifact SHA-256 and original hardware evidence stay authoritative.
Unchanged tracked build declarations also do not establish reproducibility,
complete toolchain/dependency resolution, or a new hardware PASS.

Run the focused model tests with
`python3 tools/test_glyph_hardware_correspondence.py`, together with the operator,
agent-surface and ordinary affected repository validators.
