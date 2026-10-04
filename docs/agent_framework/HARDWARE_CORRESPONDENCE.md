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

Current Revision 3 GLYPH-UD-027 uses Tier-1/Tier-2 relevant correspondence,
negative controls and mutation/isolation proof; global aggregate/topology
FAIL/incomplete is framework debt unless a concrete safety contradiction
exists. No failure is relabelled PASS. R -> E -> I remains exact: source-free
processor E must not require I's catalog; accepted source I still requires
the same immutable E, genuine committed catalog and tested source ancestry.

The bounded post-C020 owner pass additionally classifies only the exact existing
AGENTS.md, authorization/runway, supervisor, scheduled-task, cycle-state,
prompt-template, judge/watchdog, runner-boundary and work-order-template paths
listed literally in glyph_hardware_correspondence.py, and their exact existing
check_glyph_agent_framework_docs.py consumer in the repaired campaign scope.
They are agent policy
inputs, not firmware/compiler/build inputs under the source filters below.
Repaired campaign use is authenticated by the exact separately committed
GLYPH-UD-028 owner document, ancestry and regular committed/live/index bytes.
The old GLYPH-UD-027 identity remains valid for historical heads. No prefix or
adjacent alias is exempt; source, protocol, artifact, evidence, catalog and
history predicates remain unchanged. Classification never grants action
authority; actual affected docs/framework consumers and focused negatives apply.

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

GP-CONFIG-010 final integration adds exactly three later source-free evidence
paths to that finite inventory:
`docs/agent_framework/GP_CONFIG_010_INTEGRATION_HARDWARE_PROTOCOL.md`,
`docs/agent_framework/GP_CONFIG_010_INTEGRATION_HARDWARE_RESULT_20260923.md`,
and
`docs/calibration/fixtures/gp_config_010_integration_hardware_evidence_2026-09-23.json`.
This narrow completion-control consequence does not add a pattern exemption:
critical precedence and rejection of every unknown path remain unchanged.

GP-PROV-014 adds five exact host-only paths: the runtime-config index, its
decoder closure report and fixture, and the report checker and focused tests.
The index and report are documentation; the fixture is read only by its host
checker; that checker and its tests run only during repository validation.
The firmware source filters and include roots below do not select these paths.
Critical precedence and rejection of other paths remain unchanged.

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

## GP-VAL-032 exact host runner path

The isolated runtime-config aggregate entrypoint
`tools/run_glyph_runtime_config_validation.py` reads the current checker
manifest and runs host validation in a disposable local Git repository. The
reviewed PlatformIO source filters and build controls do not select this file
as firmware or a build input. GP-VAL-032 therefore adds only this exact path
to the finite `NON_BEHAVIORAL` inventory so the unchanged GP-CONFIG-010
semantic checker can evaluate a reviewed runner change. Its local historical
object transfer remains subject to the aggregate's own isolation, timeout,
mutation, clean-state, and final fingerprint checks.

Critical-path precedence, unknown-path rejection, and regular non-executable
`100644` entry requirements still apply. Adjacent names and aliases gain no
classification, and ordinary checker, census, health, and framework gates
remain independent. This classification makes no firmware, build-package,
device, or historical artifact claim and does not reopen the rest of
GP-VAL-011.

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

## GP-X1-002 finite host-path extension

GP-VAL-027 adds only the following ten exact paths to the finite
`NON_BEHAVIORAL` inventory after review of the GP-X1-002 candidate, its later
hardware-evidence publication, and the current PlatformIO dependency boundary:

- `docs/agent_framework/GP_X1_002_HARDWARE_PROTOCOL.md`
- `docs/agent_framework/SUBAGENT_CONTRACTS.md`
- `docs/calibration/fixtures/gp_x1_002_hardware_evidence_2026-09-21.json`
- `docs/runtime_config/intakes/x1_normal_restoration_overlay_hardware_candidate.intake.json`
- `docs/runtime_config/source_authority_intake_workflow.md`
- `tools/check_glyph_gp_x1_002_candidate.py`
- `tools/check_glyph_runtime_config_source_sync.py`
- `tools/check_glyph_runtime_config_validation_health.py`
- `tools/check_glyph_source_owned_source_authority_intake.py`
- `tools/source_owned_source_authority_intake.py`

The first GP-X1-002 delta contains nine of these host paths together with the
active generated baseline. The tenth path is the later immutable hardware
evidence record. These files are protocol, authority-intake, evidence, and
host-validation inputs; none is selected by the reviewed Glyph PlatformIO
source filters or build controls. Their classification does not relax their
ordinary content, evidence, source-authority, or governance validators.

`src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`
remains `CRITICAL` and byte/mode exact. Exact membership remains mandatory:
adjacent names, case variants, aliases, extensions, prefixes, nonregular Git
entries, executable metadata, and every other unknown path fail closed.

## GP-CONFIG-012 exact host-path extension

GP-VAL-033 adds exactly sixteen `100644` host/documentation paths used by the
GP-CONFIG-012 button-mask characterization: its report and fixture, explicit
host checker, copied schema and Nanopb decoder inputs, platform stubs, and
host harness. The candidate checker loads the production source bodies it
characterizes, then compiles the copied decoder and harness in a temporary
host directory using only the fixture include roots. The firmware source
filters and include roots in `platformio.ini` and `config/glyph/env.ini` do not
select these documentation, checker, or fixture paths; no production source or
build hook consumes them. Their exact membership only permits source-free
candidate metadata to pass this correspondence layer; the normal content,
semantic, census, health, and aggregate validators still apply.

The finite additions are:

- `docs/runtime_config/fixtures/gp_config012_button_mask_characterization.json`
- `docs/runtime_config/gp_config_012_button_mask_characterization.md`
- `tools/check_glyph_gp_config012_button_mask_characterization.py`
- `tools/fixtures/gp_config012_button_host/LICENSE.nanopb.txt`
- `tools/fixtures/gp_config012_button_host/button_harness.cpp`
- `tools/fixtures/gp_config012_button_host/generated/config.pb.c`
- `tools/fixtures/gp_config012_button_host/generated/config.pb.h`
- `tools/fixtures/gp_config012_button_host/include/Arduino.h`
- `tools/fixtures/gp_config012_button_host/include/pico/stdlib.h`
- `tools/fixtures/gp_config012_button_host/nanopb/pb.h`
- `tools/fixtures/gp_config012_button_host/nanopb/pb_common.c`
- `tools/fixtures/gp_config012_button_host/nanopb/pb_common.h`
- `tools/fixtures/gp_config012_button_host/nanopb/pb_decode.c`
- `tools/fixtures/gp_config012_button_host/nanopb/pb_decode.h`
- `tools/fixtures/gp_config012_button_host/schema/config.options`
- `tools/fixtures/gp_config012_button_host/schema/config.proto`

This is a finite exact-path addition. Critical firmware/build inputs retain
precedence, and aliases, unknown paths, symlinks, gitlinks, executable files,
and unsupported modes remain rejected. The GP-CONFIG-010 semantic checker,
fixture, tested-source fingerprint, and hardware evidence are unchanged.

## GP-CONFIG-013 exact host-path extension

GP-VAL-036 classifies only four newly inventoried paths from the clean,
committed GP-CONFIG-013 candidate
`fc5ef65027ee18c21cbdb9e3b347e70a16c7eb3f`. Its direct parent is
`7a2dba85332c90fa2bcc6c06e1205c4745facb92` and its tree is
`a97dbb89bece05d3c31e0cc30baf10659a4bf800`. The complete raw diff has
eight regular `100644` changes: these four paths plus the already classified
checker census, validation manifest, validation health fixture, and validation
health document. Independent source/build-role conformance found no production
or build-input delta; unchanged PlatformIO filters, include roots and extra
script do not select these host inputs. All 25 pinned source, default, schema,
decoder, and build dependencies match the candidate and its parent.

- `docs/runtime_config/fixtures/gp_config013_usb_default_characterization.json`
- `docs/runtime_config/gp_config013_usb_default_characterization.md`
- `tools/check_glyph_gp_config013_usb_default_characterization.py`
- `tools/fixtures/gp_config013_usb_host/usb_harness.cpp`

Only these literal paths receive `NON_BEHAVIORAL` classification. The
characterization remains `CANDIDATE_VALIDATION_ONLY` until its separate
candidate-resume cycle. This finite classification preserves critical input
precedence, exact-path matching, unknown-path rejection, and regular
non-executable `100644` mode restrictions. It does not select a USB fallback,
repair firmware, or establish physical controller behavior.

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

## GP-VAL-037 finite C020 campaign

`glyph_campaign_transition.authenticate` is a separate semantic proof. The legacy
`verify_correspondence` API remains strict: new critical source never inherits
GP-CONFIG-010 hardware acceptance. The immutable 0118/0151 adoption, exact C020
handoff, accepted-baseline, guard-applicability and exact current-argument receipts bind this lane. The last receipt is the regular non-executable literal
`docs/agent_framework/curation_receipts/gp_val037_current_arguments_20261003.json`
at `6cb59e97ddfdb96830432923ac588a76383153b7`, adopted at
`93b3c9ee8f702886f731714281ce143428724a17`.
The candidate, direct parent, tree and complete recursive raw inventory are
literal identities. The only production delta is the reviewed validator header,
implementation and exact Configurator insertion; all other critical entries,
28-table/X1 source and frozen decoder/schema remain unchanged.

The proof reports `BASELINE`, `CANDIDATE_VALIDATION_ONLY`, or
`ACCEPTED_TRANSITION`. Candidate compositions retain C020 as an ancestor and use
exact candidate host bytes. Only authenticated critical entries are removed from
scope checking; unknown paths, modes, aliases and dirty critical inputs fail.
The explicit WebSerial `--campaign-transition` main checks the full unfiltered
inventory for capability/flashing markers. Legacy Step15 remains separate.

In the accepted phase, shared scope views may also remove only the exact C020
protocol, evidence and present result file after their regular-file modes and
current bytes match the immutable processor snapshot. The protocol must also
match the independent review snapshot. Candidate and baseline phases receive no
result-file exemption. Content and flashing scans retain the full inventory.

The initially empty `gp_val037_accepted_transitions.json` is not PASS evidence.
A later record contains exactly work_order, candidate, build, parent, tree,
review_commit, evidence_commit and integration. Only the literal adopted C020
contract is implemented. The consumer reserves the closed 020/014/017 order set;
014/017 remain rejected until their separately authorized literal contracts exist.
Each accepted record must prove preserved C ancestry, actual F direct parent/tree,
C-to-F strict critical correspondence, exact independent review bound by the
immutable protocol and queue to F/tree/parent/artifact/locator, and native processor
PASS with empty gaps for the same pair. Source-free review precedes processor
PASS, which precedes integration. Immutable evidence must belong to that chain.
The catalog is mandatory; missing or empty records cannot downgrade accepted
source to candidate validation. The native artifact locator contract remains mandatory;
actual UF2 custody and rehash remain the separate build/operator gate. Synthetic
records used in disposable tests never become repository evidence.

Original seven characterization fixtures remain byte-frozen. Separate current
proofs authenticate the reviewed insertion and unchanged observed bodies. Current
transaction and raw GET translation units compile the actual helper against the
frozen generated Config schema. Historical line coverage and observations remain
separate. GP-CONFIG-010 keeps its legacy patch digest; a pinned full-index digest
and exact blob/mode/patch-body comparison handles only Git abbreviation variance.


## GP-VAL-043 finite C020 ABI repair successor

`tools/glyph_c020_abi_repair_transition.py` authenticates the separately adopted
repair candidate `3138ade526cabde23a0abedcb94acae8512579d1`, its direct base
`0f7fe50b3b5f385397a9737bc4c0a50ddda683c8`, immutable1256 authority and source-free
handoff. The original GP-VAL-037 constants, source proof, catalog and DONE
history remain unchanged. The new closed mapping is
`docs/runtime_config/fixtures/gp_val043_c020_abi_repair.json`; the separate real
`gp_val043_accepted_transitions.json` catalog starts empty.

The finite metadata inventory adds only those three paths and the candidate's
three reviewed proof paths: `tools/fixtures/gp_config020_button_validation/abi_probe.cpp`,
`docs/runtime_config/gp_config020_abi_repair.md`, and
`docs/runtime_config/fixtures/gp_config020_abi_repair.json`. Regular file modes,
critical precedence, full critical-tree equality and unknown-path rejection
remain mandatory. The mapping binds the exact eleven-path raw inventory and
immutable host, independent review and target object evidence.

Current transaction and GET host mirrors compile the exact repaired helper
with consistent short and ordinary enum modes. The transaction decode remains
mocked; actual generated C/Nanopb descriptor proof belongs to the frozen repaired
candidate suite. Historical fixtures and observations are unchanged. Synthetic
acceptance tests reconstruct a source-free adopted base before review and
processor records; they never establish controller acceptance. Actual acceptance
still requires the exact built snapshot, independent review, preserved artifact,
processor-accepted human PASS, empty gaps and reviewed integration chronology.

## GP-VAL-034 capacity transition

The separate finite C014 proof authenticates immutable candidate
`a3664be5354ec4253122eb2e738e70e5dfdb9ccc` and direct base
`8b8e45b17a5670bbf983360faf87bdf9d6b50ce2`. Only its two exact
CustomControllerMode entries may differ in the 236-entry critical inventory.
The accepted C020 predecessor is proved at that immutable base; C014 then
receives its own full current source, index, worktree, mode and ancestry proof.
The five protected scope filters retain their content checks after removing
only entries certified by that proof.

Capacity host tools and the separate mapping/catalog are exact regular 100644
literals in `glyph_hardware_correspondence.py`; this does not classify either
production entry as nonbehavioral. The original C014 host pins and historical
011/012/rebinding evidence remain immutable. Current tool overlays require the
separate reviewed034 inventory. Candidate validation grants no physical
acceptance. Source-free R and E preserve accepted C020 firmware; E precedes I
and requires no I catalog. Actual I requires exact C014 F/build/artifact/review,
complete processor PASS, the genuine ordered catalog and current critical-tree
correspondence. C014 cannot inherit prior010/020 controller acceptance.

The shared034 KBD overlay is limited to the five exact host files from preserved
Ckbd `4fb7c1e9507547774ff9f55cd7788355648d5d1e` and its original unchanged 28
source/dependency entries. The helper authenticates their original identities,
complete committed/index/live bytes and regular100644 modes when present.
These host literals are non-behavioral; production/source-critical precedence
remains unchanged. GP-VAL-040 strict DONE remains a separate prerequisite to
KBD publication. Future019 identities or additional files require the named041
consequence; they receive no authority from this finite set.
