# GP-CONFIG-005 integration result — 2026-09-19

## 1. Overall disposition

DONE_PUBLISHED when this separately reviewed completion commit is canonically
published. The exact hardware-tested candidate is already integrated at
`4e50be81716117022318d8dcdc7aa60c4390b605`; this descendant publishes strict DONE
correspondence. Its containing Git commit is the completion identity, avoiding a
self-SHA cycle. The supervisor's final live verification reports that full SHA.

## 2. Live canonical starting state

Live `origin/configurator` was `2f8e93cfe1430a33ef082829d6c9e0340fd66fbf`.
GP-VAL-014 was DONE; GP-CONFIG-005 was HARDWARE_VALIDATED/PASS, not integrated.
Ordinary restricted DNS failures were retried successfully using permitted network
access. No authentication mutation occurred. Local diagnostic merge `8220bc4` was
preserved and never reused or included in final ancestry.

## 3. Root cause

GP-VAL-014 introduced whole-candidate-path `ls-tree` equality in both host gates.
That condition conflated hardware-critical inputs with independently validated
repository metadata. Its sole then-observed mismatch was a regenerated checker
census; source and build inputs remained exact. This was a host correspondence
model defect, not a newly proven firmware or persistence root cause. GP-VAL-015
retains the useful exact ancestry and protected-source protections and replaces
arbitrary historical blob equality with complete critical-input equality.

## 4. Every candidate-changed path

One of the 23 paths is critical; 22 are non-behavioral. PlatformIO's inherited
source/include filters compile src, Pico HAL and Glyph config inputs. Host harness
stubs are supplied only to the host checker's explicit C++ command. Production
never includes that harness. The full dependency argument is in
[Hardware correspondence](HARDWARE_CORRESPONDENCE.md).

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


## 5. Census fixture determination

The census generator statically reads/hashes checker scripts. Its consumers are
host census, manifest, health and aggregate validators. No firmware source,
include, build hook or selected build configuration consumes its bytes. It can
gate whether validation permits a build, but supplies no compiled firmware data.
Its normal freshness/schema checks remain mandatory and passed after integration.

## 6. Curator action and role transitions

Independent Curator authorized complete H1 READY GP-VAL-015 at
`06903092e086e65904be1ae09e6f377fac50728e`, following separate dependency audit
and independent curation review. Only then did Implementation Supervisor execute
that order. The Curator did not implement it. H1 excludes active source/build
inputs, artifact/evidence mutation, GP-VAL-011, transaction tooling `8b2c893`, and
GP-CONFIG-005 integration within its scope. Integration began as a separate
recovery phase only after H1 DONE was live.

## 7. H1 implementation

The eleven-path cumulative repair adds `tools/glyph_hardware_correspondence.py`,
its 33-test suite and the dependency contract; wires operator and agent-surface
callers; updates their tests, framework README/gate wording, checker census and
the manifest's direct helper dependency. Exact finite metadata inventory replaces
blanket docs/tools trust. Critical categories conservatively cover source,
configuration, build hooks, dependency controls, workflows and generated active
source. Both the complete candidate delta and complete tested-snapshot-to-target
delta are classified. Pre-integration compares the tested base; post-integration
compares the exact candidate. Metadata validators and ordinary scope checks are
not skipped.

## 8. Fail-closed properties

Unknown paths, malformed aliases, candidate/ref/tree/parent mismatch, absent
candidate ancestry, wrong artifact or immutable PASS identity, unrelated critical
input changes, critical additions/deletions/modes, active generated-table changes,
dirty/untracked/ignored critical input, unsafe metadata modes and symlinks fail.
Critical classification precedes metadata membership. Every indexed critical
working file's bytes/mode are read back independently of Git diff, rejecting
assume-unchanged, skip-worktree, restored-stat and disabled-filemode bypasses.

## 9. Required test matrix

All 70 tests pass: 33 shared model, 25 operator and 12 portable real-Git surface
integration tests. Expected negative results below mean the unsafe case was
rejected, not that the test suite failed.

| Requirement | Result and evidence |
| --- | --- |
| 1 Exact integrated critical inputs | PASS: helper exact/real-merge and surface authorized-integration tests. |
| 2 One-byte handler drift | Rejected: surface critical-input loop and helper handler drift. |
| 3 Other later firmware/build input | Rejected: generated baseline, platformio/config, additions/deletions/modes. |
| 4 Recreated candidate | Rejected: real cherry-pick test and helper ancestry test. |
| 5 Candidate ref moved | Rejected: operator and real-Git surface ref tests. |
| 6 Tested parent/base differs | Rejected: operator, surface and helper identity tests. |
| 7 Artifact hash differs | Rejected: operator artifact mismatch test; real preserved bytes also verified. |
| 8 PASS belongs to another pair | Rejected: surface candidate/artifact evidence substitutions. |
| 9 Regenerated candidate census | PASS: real merge + actual integrated census freshness validation. |
| 10 Superseded docs/governance | PASS: helper and surface metadata evolution tests. |
| 11 Invalid exempt metadata | Rejected by real census validator; helper does not suppress it. |
| 12 Exact authorized protected source | PASS: canonical authorization + immutable evidence + exact merge. |
| 13 Exact candidate plus unrelated source | Rejected: real-Git extra-source/build/generated delta tests. |
| 14 Dirty protected source | Rejected: staged, unstaged, untracked, ignored and hidden-index tests. |
| 15 Missing canonical validated PASS | Rejected: surface READY/FAIL/gaps substitutions. |
| 16 Stale authorization | Rejected: candidate/base/artifact/evidence substitutions. |
| 17 Ordinary H0/H1 HAL edit | Rejected: ordinary unauthorized HAL surface test. |
| 18 Metadata absent build dependencies | Audited explicit PlatformIO/include/hook/host graph; frozen critical inputs. |
| 19 Unknown candidate path | Rejected even when its candidate blob remains exact in target. |
| 20 Generated active runtime source | Rejected on drift; active include chain remains protected. |

## 10. Independent review

Separate source-authority specialist, Work-Order Curator, curation reviewer and
fresh implementation reviewer were used through native internal delegation.
Reviewer found a real hidden dirty-source hole; direct byte/mode readback and
regressions closed it and independent reproductions then rejected it. A tracked
helper manifest dependency was subsequently detected by isolated aggregate
validation, declared, independently reviewed and retested. No findings remained.
Independent integration review approved `4e50be8` after exact source, PASS,
custody, historical evidence, build and focused-gate inspection.

## 11. H1 publication

- Authorization: `06903092e086e65904be1ae09e6f377fac50728e`.
- Model implementation: `bf861b05bf272eaa4729b3057cb7a8c0217bc4fa`.
- Final reviewed implementation with declared helper dependency:
  `50a7a2c9ab0cfe5d32eea2f3d86146afa6a5c144` (includes dependency
  correction `91998ee`; final net manifest edit is one dependency).
- Strict H1 DONE: `79608f5e4ceb91209ffe5d5581b985bb5fe7c347`.
- Superseded local completion `372ea85` remained unpublished and is not final
  ancestry. No force-push or destructive history rewrite was used.

## 12. Fresh exact integration

Branch: `codex/gp-config-005-exact-integration-20260919`.
Merge: `4e50be81716117022318d8dcdc7aa60c4390b605`.
Parents, in order:
`79608f5e4ceb91209ffe5d5581b985bb5fe7c347` and
`437f87e8086a50f0dfbd834176b80d245c1ed307`.
Normal `--no-ff` merge was conflict-free; no firmware conflict resolution or
candidate recreation occurred. The exact merge was reviewed, pushed and
live-verified on canonical before this DONE publication.

## 13. Exact H2 correspondence

| Identity | Exact value |
| --- | --- |
| Candidate | `437f87e8086a50f0dfbd834176b80d245c1ed307` |
| Candidate tree | `4b9e2f1eb56add78ff880321730eb15ed22ce72f` |
| Direct tested parent | `9550a1bf1309383e351f4f9e66663562fc9f13ac` |
| Original UF2 SHA-256 | `650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44` |
| Critical changed handler blob | `3e934f2f5aae13a36310a35d273727da60723abe` |
| Canonical hardware PASS publication | `0fd9e30f158fa41b06ea193c32a854a36e8cab31` |
| Immutable evidence object | `0bb9e29a2ba8f92483c8a0177997efe32d400030:docs/calibration/fixtures/gp_config_005_hardware_evidence_2026-09-17.json` |
| Hardware result / gaps | `PASS` / `[]` |

Custody remains the original 792064-byte regular read-only
`local_backups/hardware-artifacts/437f87e8086a50f0dfbd834176b80d245c1ed307/650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44/firmware.uf2`.
It was rehashed before integration and after the build. Every critical input,
including ones untouched by the candidate, remains exact.

## 14. Non-behavioral supersession

Exactly two of the candidate's 23 paths differ; the other 21 retain exact entries.

| Path | Candidate blob | Integrated blob | Reason |
| --- | --- | --- | --- |
| `docs/runtime_config/fixtures/glyph_checker_census.json` | `2bca430c1f883d294bbe752b4c328ccfe3d39802` | `426cb0d485f172a945eb58e8ac39310e52709164` | Later checker inventory/hash metadata. |
| `docs/runtime_config/fixtures/runtime_config_validation_manifest.json` | `b664288a0ca5977062e636013a813b9289ad9f9a` | `ba604e371712ba331e16a448ce266b662315c74e` | Required direct helper dependency plus candidate transaction-checker entry. |

Both are ordinary `100644` blobs, absent from compiled inputs, and pass their
normal validators. This is an application of the general model, not a filename
waiver. Other later control-plane/operator documents are independently governed.

## 15. Post-integration validation

PASS: direct production transaction harness (9 cases), persistence research
correspondence (48 ordered steps, 15 immutable upstream blobs, 56 negatives),
operator identity, preserved artifact custody, all 70 Python tests, protected
surface, framework, sequence, navigation/agent context, checker context, runtime
source-sync and identity-table sync, Ultimate identity profile baseline, declared
build-input inventory, census (199), health (37 manifest entries), manifest
semantic load (37 entries/37 exclusions), Python compilation and diff/source
checks. The H1 isolated aggregate adversarial suite passed after dependency repair.

The full main-workspace aggregate remains unavailable: preflight SETUP_FAILURE
on `.pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/`, canonical proof UNAVAILABLE.
No full aggregate-green claim is made. An extra GFW3 checker
`check_glyph_smashbox_identity_runtime_bindings.py` fails its legacy
`outputs.buttonL = inputs.lt1 || inputs.lt3;` anchor identically on untouched
pre-H1 canonical and integration. It is absent from the current manifest and
checks unchanged Ultimate/calibration inputs, not the GP-CONFIG-005 handler.
Independent review classified it outside this integration's current/affected
scope; its failure is retained, not repaired or relabeled PASS.

## 16. Firmware build

`pio run -e glyph_mk6` was unavailable (`pio` not on PATH).
Approved fallback `.venv/bin/python -m platformio run -e glyph_mk6` succeeded
in 9.83 seconds after permitted access to the existing PlatformIO cache lock.
RAM: **78720 / 262144 bytes (30.0%)**.
Flash: **383792 / 1568768 bytes (24.5%)**.
Build output is build-integrity proof only. Git HEAD/dirty identity is embedded
in FIRMWARE_VERSION, so the rebuild is not claimed byte-identical or physically
accepted. It did not replace the original tested UF2, and no flashing occurred.

## 17. GP-VAL-011

Remains `REVIEW / OWNER_DEFERRED / NONEXECUTABLE`. Its ignored dependency-path
and aggregate/complete-proof issues were not repaired or hidden. No new authority
for its optimization or validation architecture was created.

## 18. GP-CONFIG-005 completion

Strict `glyph_done_completion_evidence` uses DIRECT_ANCESTRY, the tested direct
parent as implementation base, exact candidate as reviewed implementation,
`4e50be8` as prior canonical integration and all 23 reviewed changed paths.
Candidate/artifact/PASS/gaps fields remain unchanged. Status and mirrors become
DONE in this separate descendant after live integration and passing focused gates.
The prior INCONCLUSIVE_PERSISTENCE_EVENT remains untouched historical evidence;
it is neither candidate FAIL nor PASS and its exact failure window remains unknown.

## 19. Canonical after

Canonical integration was live-verified at
`4e50be81716117022318d8dcdc7aa60c4390b605` before creating this completion.
The completion commit containing this report is separately pushed and live-verified;
its exact final SHA is supplied in the supervisor's final report.

## 20. Remaining open items and non-claims

Excluded transaction-stage tooling `8b2c8932304ecf5c56149eb91ec5ddd7511c59e8`
remains separate and is not an ancestor of the integrated result. GP-VAL-011 and
the additional legacy checker issue remain as reported above. Future persistence
durability/recovery policy and modifier intent remain owner-gated.
No atomic persistence, rollback, power-loss-safety or recovery guarantee is added.
GET_CONFIG does not prove live-RAM byte identity. Nunchuk remains NOT_TESTED;
unrelated firmware paths receive no new acceptance. Persistence root cause remains
unproven. There was no device write, firmware flashing or new physical test.

## 21. Single next control-plane action

Run a fresh non-authoritative Planner audit from live canonical. Effective Ready
runway is zero and primary liveness remains PLANNING_REQUIRED; no unrelated feature
work is started by this recovery.
