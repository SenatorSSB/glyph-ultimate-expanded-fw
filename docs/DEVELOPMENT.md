# Development

## Supported public development path

This repository implements Glyph controller firmware, backends and storage on
HayBox foundations. Senscope is a separate browser product. Start with
[architecture](ARCHITECTURE.md), [current state](CURRENT_STATE.md) and the
[profile system](PROFILE_SYSTEM.md) to understand the relevant boundary.

Branch from the current live `origin/configurator`, make a bounded change, run
its affected checks, obtain independent reviewer inspection, and merge only
validated work. Keep changes and review evidence easy to compare with that base.
The normal public contributor path uses this guide and does not require an agent
queue or personal orchestration roles. [AGENTS.md](../AGENTS.md) is the normal
coding-agent contract and routes agents to this guide. Maintainer
approval remains necessary for substantive compatibility and device-operation
changes; this guide supplies no device-operation authority.

## Environment and build

Use Python 3, Git and PlatformIO for the Mk6 firmware build. Run from the
repository root, with intended source committed and the worktree clean:

```sh
pio run -e glyph_mk6
```

The repository's quieter fallback is:

```sh
./scripts/build-glyph-mk6-quiet.sh
```

The [fallback script](../scripts/build-glyph-mk6-quiet.sh) uses
[scripts/pio-local.sh](../scripts/pio-local.sh), writes logs and reports its
bounded timeout; it does not flash a device. PlatformIO resolves the framework,
compiler and libraries declared in [platformio.ini](../platformio.ini) and
[Glyph environments](../config/glyph/env.ini). See
[build architecture](ARCHITECTURE.md#build-architecture) for generated inputs and
clean-source checks. Network access is needed to resolve missing packages.
A build does not imply reproducibility across every dependency cache.

Many Python checks use only the standard library. Install optional dependencies
for the checks you actually run: `jsonschema` is required by the legacy v0
authoring test suite and enables independent optional v1 schema checks; `grpcio-tools` supplies `grpc_tools.protoc` for protobuf-generating host
fixtures. Hosted package tests also use C/C++ compilers, sanitizers, Nanopb and a
resolved Arduino-Pico framework; see [CI](../.github/workflows/build.yml). These
host fixture requirements are not prerequisites for every standalone Python check.

## CI model

The [hosted workflow](../.github/workflows/build.yml) runs `current_host`, then
`validation`, then a conditional `build` matrix containing `glyph_mk6`/UF2.
Validation always runs regardless of the build classifier's decision, after its
`current_host` prerequisite succeeds. It is not bypassed for documentation-only
changes, and a failed prerequisite is not a validation PASS.

The [build classifier](../tools/glyph_ci_build_inputs.py) exempts only ordinary
regular Markdown under the repository root or `docs/`, with ordinary Git modes.
Python, JSON, checker, profile-directory and unknown/special-mode changes can
legitimately trigger a firmware build. A new branch's all-zero previous ref uses
the merge base with canonical. Hosted build provenance checks surround the build
and artifact-copy block; the workflow uses the existing postprocessor and an
observed-only provenance sidecar. Its unknown transformation is not documented
as understood or reproducible. A CI build is not physical hardware acceptance.

## Change classification and required evidence

| Change | Focused tests / inspection | Aggregate and CI | Firmware build | Hardware and separate authority |
| --- | --- | --- | --- | --- |
| A. Docs prose only | Navigation, links, source-backed claims, review | Current validation and hosted gates | When classified | None if active behavior/build inputs unchanged; evidence claims need provenance |
| B. Checker/test/tooling only | Positive/negative controls and affected consumers; regenerate checker census | Current aggregate, census/health, hosted gates | When classified; required for actual build-input changes | None when active behavior/build inputs unchanged; no weakening safety gates |
| C. Profile authoring/example only | Authoring/schema/native admission; exact binary compatibility when promised; design review | Affected contracts, current validation, CI | If compiled into active firmware or classified | Offline validity needs no device test; installed execution/gameplay claims need separate exact evidence/authority |
| D. Build/toolchain/configuration | Input identity, generated outputs, affected contracts | Current validation and CI | Required | Exact hardware PASS before merge for active behavior changes; resolve/test uncertain runtime effects |
| E. Schema/protocol/persistent format | Positive/negative decoding, old/new compatibility, storage/recovery/fault tests | Affected contracts, current validation, CI | Required for firmware inputs | Separate design/source approval; exact hardware PASS before merging changed active firmware behavior |
| F. Active firmware behavior | Runtime/compatibility tests and independent source review | Current validation and CI | Required from exact committed candidate | Exact candidate + exact artifact + scoped hardware PASS before merge |
| G. Hardware-result/evidence publication | Human report, scope, source/artifact correspondence, provenance | Relevant evidence/aggregate checks and CI | No substitute rebuild to manufacture acceptance | Only actual reported results; separate correspondence review; no inferred new qualification |
| H. Device-operation workflow | Admission/refusal, custody, recovery, permission boundaries | Affected contracts, current validation, CI | If firmware inputs change | Separate explicit device-operation approval; documentation never authorizes flashing, writes or recovery |

Historical unrelated failures need evidence and explicit disposition; never silently
waive them or relabel them PASS. An active source change cannot merge on build
proof alone. For source touched without an active behavior change, build proof is
still required; unresolved runtime uncertainty needs resolution or hardware proof.

## Testing strategy

Run focused/unit checks first, then affected contracts, the current aggregate,
hosted CI and the classified build. Use hardware where the change or claim
requires it. Representative commands, rather than the historical checker catalog:

```sh
python3 tools/test_glyph_docs_navigation.py
python3 tools/check_glyph_docs_navigation.py
python3 tools/test_glyph_native_profile_json.py -v
python3 tools/test_glyph_native_profile_json_v1.py -v
python3 tools/glyph_ci_current_package_tests.py
python3 tools/generate_glyph_checker_census.py --check
python3 tools/check_glyph_checker_census.py
python3 tools/check_glyph_runtime_config_validation_health.py
python3 tools/check_glyph_prebuild_git_identity.py
python3 tools/test_glyph_ci_build_inputs.py
python3 tools/run_glyph_runtime_config_validation.py --json
pio run -e glyph_mk6
git diff --check
```

After checker-body edits, run `python3 tools/generate_glyph_checker_census.py`
first and review the generated diff. The
[manifest](runtime_config/fixtures/runtime_config_validation_manifest.json)
curates current checks and applicability; the
[census](runtime_config/fixtures/glyph_checker_census.json) inventories checker
bodies/dependencies. [Health checks](../tools/check_glyph_runtime_config_validation_health.py)
protect their relationship. Do not rewrite applicability or historical authority
just to turn a run green.

Report PASS, FAIL, TIMEOUT and SKIPPED separately. TIMEOUT is not PASS; SKIPPED is
not PASS. An unavailable dependency or incomplete aggregate is not successful
coverage. Retain JSON, exit status and failed check names, distinguishing current
regressions from evidenced historical failures. An optional independent schema
test may skip without invalidating mandatory compiler checks; the skip still
supplies no schema-test proof. A focused/category PASS is not full aggregate PASS.

## Git/source identity

Build and hardware evidence need a clean committed worktree, exact commit
identity and a known build-input identity. The
[prebuild identity check](../tools/check_glyph_prebuild_git_identity.py),
[tracked integrity helper](../tools/glyph_tracked_worktree_integrity.py) and
[native build script](../builder_scripts/native_target_metrics.py) address
complementary identity checks. Production inputs include HAL, config, schemas,
libraries and builder code beyond `src/**`. Dirty files, generated changes,
index/worktree divergence or a stale commit label can make artifact correspondence
ambiguous. A clean Git tree alone does not identify every resolved external
package or prove reproducibility.

Use ordinary reviewed commits and normal pushes. Do not force-push or use
destructive Git operations in a reviewed workflow unless explicitly intended and
authorized. Never discard unrelated local edits to obtain a clean build.

## Firmware artifact and hardware evidence

See the [current hardware evidence contract](evidence/HARDWARE_EVIDENCE.md) for
artifact custody and acceptance requirements.

**Build proof:** firmware compiled from known source. **Hardware acceptance:**
the exact candidate source plus exact tested artifact SHA-256 and recorded human
test scope passed. These are different claims. Preserve the retained UF2 and its
hash; a later CI build or local rebuild is not that accepted artifact. Matching
source behavior does not transfer acceptance to an arbitrary rebuild.

[Current state](CURRENT_STATE.md) routes to accepted identities and scoped
evidence. Documentation/checker-only changes need no hardware when active
firmware behavior and build inputs remain unchanged. A classifier-triggered build
for those changes supplies compilation evidence, not a new controller result.

## Compatibility and versioning

Do not silently change existing persistent formats or protocols. Use additive or
explicitly versioned evolution where appropriate, with compatibility and refusal
tests for supported old/new states. Authoring-format version, native schema and
package protocol are independent domains; see
[version contracts](PROFILE_SYSTEM.md#version-contracts). Protect current supported
compatibility fixtures even if their motivating incident is historical.

Historical campaign replay may eventually become optional only after current
regression coverage protects the relevant invariants. Evidence preservation does
not require every old campaign checker to remain on the normal path forever.
This guide retires no checker and changes no current applicability.

## Adding or changing a feature safely

1. Identify the owner and source authority for the behavior.
2. Define current behavior and the intended bounded change.
3. Identify compatibility, storage, protocol and backend impact.
4. Implement the smallest bounded change.
5. Add positive and negative tests, including refusal/preservation cases.
6. Run affected contracts and current validation; retain actual outcomes.
7. Build when inputs or classification require it.
8. Obtain exact hardware acceptance before merging active behavior changes.
9. Update the canonical current documentation owner.
10. Preserve detailed evidence without copying it into introductory current prose.

## Documentation maintenance policy

| Canonical owner | Responsibility |
| --- | --- |
| [README](../README.md) | Player introduction and reader routes |
| [Docs index](README.md) | Navigation and glossary |
| [CURRENT_STATE](CURRENT_STATE.md) | Current status and qualification only |
| [CAPABILITIES](CAPABILITIES.md) | Capability, exposure and qualification distinctions |
| [USAGE](USAGE.md) | Current user workflows |
| [PROFILE_SYSTEM](PROFILE_SYSTEM.md) | Native profile concepts and semantics |
| [ARCHITECTURE](ARCHITECTURE.md) | Repository/system relationships |
| DEVELOPMENT | Build, test and contribution rules |
| [ROADMAP](ROADMAP.md) | Future intent |
| [profiles/README](../profiles/README.md) | Exact v1 authoring contract |
| [history](history/HISTORY.md) / [decisions](history/DECISIONS.md) | Selected milestones and durable rationale |
| [hardware acceptance](history/HARDWARE_ACCEPTANCE.md) / [source lineage](history/SOURCE_LINEAGE.md) | Physical scope and source/artifact relationships |
| [evidence](evidence/README.md) | Logical index linking preserved evidence |

Replace/edit current summaries instead of prepending another dated status report.
Completed work leaves ROADMAP. Detailed incident packets belong in evidence or
history, rather than current entry points. Give one fact one canonical current
owner where practical. Validators protect invariants, not obsolete paragraph
wording. Curated history/evidence now has explicit owners; existing packets remain at
their original paths pending separate preservation and consumer review.

## Lessons learned / engineering practices

| Retained lesson | Practical consequence / source |
| --- | --- |
| Source presence is not product exposure; product exposure is not physical qualification | Keep the separate columns in [capabilities](CAPABILITIES.md) |
| Build PASS is not hardware PASS | Keep exact source, retained artifact and human scope in [current state](CURRENT_STATE.md) |
| Stored labels are not executing identity | Require active owned native-view/context correspondence; see [architecture](ARCHITECTURE.md#selection--activation-architecture) |
| API-visible preservation is not raw-flash equality | Preserve the narrow accepted observation in [acceptance](history/HARDWARE_ACCEPTANCE.md) |
| A historical failed regression may still encode a current invariant | Extract durable coverage before retiring replay; keep compatibility/refusal fixtures |
| Mode engine is not profile label or backend | Review dispatch and transport separately in [architecture](ARCHITECTURE.md#mode-architecture) |
| Authoring JSON is not a complete package | Native compilation does not materialize paired Config/storage ownership; see [profile system](PROFILE_SYSTEM.md) |
| Exact source/artifact correspondence matters | Do not transfer physical acceptance to later rebuilds |

Keep observations, proven causes and inference separate. The browser
Gamepad/JoyCheck discrepancy is an observation with root cause UNPROVEN; it does
not establish a transport explanation. Nunchuk remains NOT_TESTED. These scoped
lessons do not broaden any historical acceptance.

## Legacy/internal workflow note

Historical/internal campaign machinery from the development fork is not part of
the supported public workflow. Curated [history](history/HISTORY.md) and
[evidence](evidence/README.md) contain the durable public facts.
[AGENTS.md](../AGENTS.md) is the normal coding-agent contract; this guide is the
public developer entry point. Retained internal contracts and evidence remain
intact pending separate consumer and preservation review.
