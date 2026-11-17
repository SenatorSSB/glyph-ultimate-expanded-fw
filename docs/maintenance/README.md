# Documentation consolidation: Batch A audit

Audit baseline: `9f6e0d0e0bea0e5dcd9292d55cc2c4e2d8af8c62` on
`configurator`, live-verified on 2026-11-17. This is a bounded owner-authorized
inventory and migration proposal, not a new authority layer or deletion approval.
Only this summary and two optional audit tools are added. Existing tracked files,
firmware, defaults, schemas, CI, evidence and queue outcomes are unchanged.
No freeze, release, export, device operation or hardware qualification occurs.

## Reproduction and coverage

Run from a checkout containing the pinned commit, with Python 3 and Git:

```sh
python3 tools/test_glyph_documentation_audit.py
python3 tools/audit_glyph_documentation.py --baseline 9f6e0d0e0bea0e5dcd9292d55cc2c4e2d8af8c62 --output /absolute/owner-only/new-audit-directory
python3 tools/audit_glyph_documentation.py --baseline 9f6e0d0e0bea0e5dcd9292d55cc2c4e2d8af8c62 --validate /absolute/owner-only/new-audit-directory/inventory.json
```

Choose an owner-controlled directory outside every public checkout/export/cloud
publication path. A directory name alone does not establish privacy. The tool
creates a new directory with mode 700 and report files with mode 600; it refuses
existing output directories and output within its checkout. It never executes
or imports discovered artifacts. Exhaustive outputs must remain private.

The immutable tree contains **7,980 paths: 7,486 blobs and 494 subtrees**, with
148,301,585 blob bytes counted per path. Every path appears once in bytewise
order, including directory objects. Each has mode, type, object ID and applicable
size, plus separate content, relevance, machine role, provenance protection,
privacy, destination, extraction and review dimensions. Default UNREVIEWED
classifications deliberately confer no retention/deletion judgment.

Inventory validation compares every identity against Git. Missing, duplicate,
reordered or changed identities fail. JSON parsing rejects duplicate keys and
non-finite constants. Synthetic tests cover these controls, dirty-checkout
independence, duplicate-object retention, deterministic scans, private permissions,
fixed stdout and bounded compressed input. Outputs contain no timestamps.

Automated coverage is not semantic coverage. The private section index contains
6,368 Markdown sections; the tool marks all UNREVIEWED. The human coverage ledger
records targeted sections/queries in **46 distinct baseline paths**, with PARTIAL
bounds and specialist coverage reports. It is not 46 complete file reviews.
Source, native compiler/schema/defaults, startup/menu/identity, acceptance,
CI/census/manifest and representative historical proof chains were inspected.
Full queue chronology, every checker body, historical packets, dormant engines,
all boards and complete transactional paths remain PARTIAL or UNREVIEWED.

The scan records 211,219 dependency candidates, not a complete dependency graph.
It scans UTF-8 blobs up to 8 MiB, Python import/constructed-expression candidates,
Markdown links/anchors, prose paths, Git locators, external URLs and private
locators. Anchors are recorded, not validated. C++/shell dataflow, escaped or
reference-style links, dynamically constructed paths and transitive execution
are incomplete. Confirmed active edges are a separate human-reviewed register;
resolved strings alone prove no active dependency.

Of 3,750 gzip paths, 1,106 received bounded expansion scans; 2,644 remain
unreviewed after the conservative 256 MiB expansion budget. No archive was
extracted or executed. Binary/media metadata, oversized text and unsupported
formats remain explicitly unreviewed. Two baseline JSON texts failed strict
parsing; their locations/dispositions remain private, without fixture changes.
Unresolved dependencies block their affected migration, not unrelated extraction.

## Contradictions and proposed ownership

[Root README](../../README.md) and [framework overview](../agent_framework/README.md)
contain broad legacy non-claims that conflict with the implemented native lane
recognized by the [boundary](../runtime_config/IMPLEMENTATION_BOUNDARY.md).
[Navigation checks](../../tools/check_glyph_docs_navigation.py) enforce some of
that old wording. Later native exceptions must become a clear scope matrix;
retaining a literal phrase is not evidence that the broad statement is current.
The retired official configurator website and Configurator transport are distinct.

The leading current-state/acceptance prose still says canonical integration is
pending. Live canonical is the pinned preparation descendant, and its non-doc
tracked inputs equal the tested production source. Preserve both the publication
fact and historical decision wording; do not infer a freeze or release decision.

Source finding requiring separate bounded review: Smash64 declares
`socd_pairs_count = 2` while four `SocdPair` initializer entries are visibly
present in that initializer block
([defaults](../../config/glyph/common/include/glyph_overrides.hpp), lines 256–264).
The intended interpretation and any physical or runtime significance are
unverified; this audit does not establish a user-visible defect. No firmware
repair is authorized by Batch A.

Proposed destinations below require subsequent approved edits and consumer review:

| Destination | Owns |
| --- | --- |
| README.md | Player introduction, examples, availability and routes |
| AGENTS.md | Concise public contributor/agent rules and safety boundaries |
| docs/README.md | Audience navigation and compact glossary |
| docs/CURRENT_STATE.md | Current facts, scoped qualification, exact artifact reference |
| docs/CAPABILITIES.md | Implementation/workflow/package/Senscope/hardware views |
| docs/USAGE.md | Supported workflows, recovery and limitations |
| docs/PROFILE_SYSTEM.md | Ownership, preprocessing, evaluation, subsystems and limits |
| profiles/README.md | Existing authored format/compiler/templates/LLM authoring rules |
| docs/ARCHITECTURE.md | Current source/storage/protocol/activation/write boundaries |
| docs/DEVELOPMENT.md | Public build/test/compatibility/review and engineering lessons |
| docs/ROADMAP.md | Future work, dependencies and explicit deferrals |
| docs/history/{HISTORY,DECISIONS,HARDWARE_ACCEPTANCE,SOURCE_LINEAGE}.md | Selected chronology, decisions, exact scoped evidence and lineage |
| docs/evidence/README.md | Logical index of selected evidence, not a mass-copy archive |

Historical Markdown and identical copies may be immutable machine/review inputs.
Extract product decisions and facts with exact source objects before proposing
retirement; preserve tested bytes and historical outcomes. Personal Planner,
Curator, Runner, roster, transport and telemetry mechanics belong in an owner-held
private playbook or retirement plan after consumers are resolved. Public builds
and tests should eventually require only declared public dependencies.

## Checker disposition proposals

The static census discovers 264 checkers. The validation manifest has 64 entries:
25 current/load-bearing and 39 historical/non-load-bearing. These labels do not
prove all transitive historical dependencies have gone away.

| Family | Proposal and obligation before migration |
| --- | --- |
| Current firmware/package host regressions | Keep current behavior, both enum ABIs, bounds, recovery, preservation and transactional failure controls. A fixture's age is irrelevant. |
| Build/publication/provenance/custody | Keep; reject dirty/wrong/missing source, unsafe mode/type, bypassed upload guards and mismatched artifact identities. Successful build is not acceptance. |
| Native/offline authoring and source-owned tools | Keep supported current contracts; preserve exact coordinates, deterministic compile, explicit overlay/reject and unsupported conversion negatives. |
| Schema/staging/storage fallback | Keep or replace only with equivalent current-source rejection/no-mutation/recovery tests; do not assume package smoke covers every old invariant. |
| Census/health/runner isolation | Keep properties; simplify machinery only with missing/duplicate commands, bad bases, mode swaps, dirty inputs, timeout and isolation negatives. |
| Navigation/framework/sequence | Replace stale phrase/personal-process assertions with scoped claims, public navigation and required contributor rules. Exact historical contracts become optional replay only after consumer migration. |
| C023/C020 and historical correspondence chains | Preserve exact replay inputs now; replace current obligations with current-source regressions before making historical replay optional. Never repin old evidence to new firmware. |
| Orphaned campaign/process checks | Retirement candidates, not approved deletions; trace direct/transitive/frozen consumers and capture product lessons first. |

CI explicitly fetches failed-build object
`0a5dd751c391198140ed146853a69fc825d902c7`
([workflow](../../.github/workflows/build.yml)). C023's authenticated original
classifier traverses C022/C021/C017/C014/C020 roots; C020 compares preserved failed
source/host inputs through ABI repair. The object is evidence, not current firmware.
Keep the fetch until current classification/regression obligations are replaced.
Options: retain mandatory replay; split a documented optional replay lane; or
review a minimal content-addressed fixture retaining original identity/authority.
Missing/wrong objects, modified failed-source bytes, omitted roots, wrong modes,
substituted receipts and wrong-ABI expectations must fail the replay. Current
USB index tests need equivalent exhaustive/bounds negatives before substitution.

The new audit tool is opt-in. Its only direct new consumer is its test module;
the census discovers `check_glyph_*.py`, so these additions do not change it.
The existing CI classifier treats Python additions as build-requiring. Hosted CI
must run normally; its artifacts cannot replace the exact tested UF2.

## Player README foundation and storyboards

Lead with Glyph as customizable controller firmware for Smash Ultimate players,
then give a short honest availability notice and technical navigation. Explain
engine, stock label, backend, physical plate, stored record and complete package
separately: 13 stock rows use eight engine IDs; dispatch supports nine engine IDs.
Pico constructors cover XInput, DInput, Switch USB, GameCube, N64, NES, SNES and
Configurator. PS4/PS5 enum presence alone does not implement those backends.
Optional input classes/prototypes are not Mk6 wiring or qualification claims.

The [schema](../../schema/haybox/config.options) caps total rows at 30, including
retained other modes. Row SOCD/remaps and stored native rules/values are profile
owned; backend destinations, overall brightness and some mode options are global.
The [native evaluator](../../src/modes/UltimateNativeEvaluator.cpp) supports
independent nine-way entries, including nonneutral output at no-direction key 5.
One native input may drive digital bindings, a modifier condition and subsystem
effects; ordinary remapping itself forbids duplicate physical-input fanout.

“Subsystem/sublayer” means authored conditions, gates, table selection and target
effects. Smaller numeric priority wins; overlapping equal effect priorities are
rejected; digital bindings OR then apply masks. There is no arbitrary nesting or
persistent toggle implied. Native limits include 96 conditions, eight sources,
32 table rules, 32 digital bindings, 16 effects and 28 table slots, also constrained
by byte/token budgets. These are finite simultaneous mappings, not timed macros,
character awareness, universal gameplay guarantees or tournament approval.

Proposed README sequence: player benefit and availability; small input/output
examples; profile ownership/capacity; supported workflows and limitations;
qualification matrix; links to authoring, usage, architecture and development.
Captions/storyboards, with illustrative coordinates rather than installed claims:

1. Right input → remap/SOCD → winning table → key 6 → raw output. Modifier selects
   an alternate table with key 6 down-left. No direction still selects key 5, which
   may output a nonneutral point. Caption: “The selected entry determines output.”
2. One physical button branches to digital bindings, modifier and subsystem gate.
   Label original/pre/post-SOCD input domains. Caption: “Several coordinated roles
   in one evaluation.” Do not draw a timed input sequence.
3. Same direction/action inputs, subsystem gate off/on: show base versus alternate
   table, winner-filtered bindings and per-target effects, with winning priority.
   Caption: “A finite authored layer changes which rules apply.”

Neutral-B recipe: bind an explicitly chosen input-domain condition to B and a
higher-priority left-stick neutral fixed-point effect; verify competing effects,
masks and optional overrides in the complete profile. While held, this requests
B plus neutral raw LS. It supplies no frame threshold or guaranteed game move.
Offline native authoring is not a complete managed package or finished Senscope
Builder/install workflow. Selection is boot-bound, not arbitrary hot-swap.

## Exact acceptance and lessons to retain

[Committed acceptance](../planning/final-usb-gamepad/acceptance/README.md) reports
tested source `dcf6e29589f558a95c021bef491578f87e41750f`, tree
`a7731388430ea70dbe666298953795f4018069b0`, UF2 SHA-256
`2c77e2b7e50af2fd3b516d1ee7d0b8a67bcf992d6fcf0e3109a837422740cd42`,
1,325,568 bytes. Batch A did not access/rehash those private retained artifacts.
Keep tested source, build-evidence descendant, acceptance descendant and canonical
tip distinct. Windows joy.cpl/XInput, original Switch USB/Ultimate, GameCube-adapter
route and API-visible preservation/reconnect have only their recorded scope.
DInput was N/A; browser Gamepad/JoyCheck NOT_QUALIFIED; Keyboard deferred;
Switch 2 out of scope; Nunchuk NOT_TESTED; Fresh Install remains unqualified.
Managed activation/display and Input Viewer naming retain their separate gaps.

Representative lessons: both ABI layouts matter for host/target proof (C020);
API-visible preservation does not prove raw-flash equality; stored labels do not
prove execution; later physical findings can supersede an earlier source audit.
Put engineering practice in DEVELOPMENT and scoped decisions/incidents in history.
Keep observations, established causes, hypotheses and practices separate. Browser
and historical physical root causes remain unproven; no speculative cause is fact.

## Privacy, custody and bounded B1

Private findings record local-path/contact candidates and publication surfaces;
no raw matches are repeated here. The scan is not a secrets clearance. Existing
owner author/committer identity is accepted for this fork and is nonblocking.
Metadata review covers 1,992 reachable commit records and local refs; hosted
metadata exposed no releases and 12 workflow artifacts at inspection time.
Hosted artifact bytes, issues/PR discussions, remote-only refs, LFS external
payloads, devices and raw private acceptance captures were not privacy-cleared.
Binary/media metadata and remaining compressed inputs need inspection.

Later export should explicitly select reviewed content without `.git`, old refs,
personal reports, patch author headers or unreviewed artifacts. Use approved public
handle/noreply identities for fresh history/trailers/taggers and inspect assets.
Preserve upstream/license notices. Required sensitive attribution/source/tested
bytes need an explicit later resolution, never silent alteration. Do not export,
rewrite history, create/delete repositories or promise erasure in Batch A.

Before eventual fork deletion, verify a private recoverable archive: Git objects,
refs, submodules/LFS if applicable, release/CI assets and provenance, hosted issues,
PRs/discussions/comments, private originals/artifact custody and relevant external
sources. A Git bundle alone is insufficient. No archive migration/deletion occurs.

B1 recommendation: authorize only current public navigation/scoped claim extraction
and replacement navigation tests, using this coverage ledger and representative
facts. Retain original packets, source/defaults/CI/queues and C020 fetch. Prove
new current claims and negative coverage, obtain fresh review, then consider a
separate checker/replay split. Mass retirement waits for dependency closure,
remaining semantic extraction, verified private custody and export/privacy review.
