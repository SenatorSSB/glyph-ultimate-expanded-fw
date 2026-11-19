# `glyph_nuker` Source Lineage

## Current G2F reconciliation — 2026-11-19

Exact corresponding source is identified and reproduced. The current release
requirement is **`GLYPH_NUKER_CORRESPONDING_SOURCE_PACKAGING_REQUIRED`**,
using the existing **`REVIEW_REQUIRED`** export classification while packaging is
incomplete. **Public export remains BLOCKED; the repository is not release-ready.**
`GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED` is retired as a current missing-source
blocker. Its appearances in sealed receipts and historical sections describe
the conclusions at those checkpoints.

The [G2F reconciliation receipt](fixtures/glyph_nuker_release_rights_g2f.v1.json)
separates these propositions:

| Proposition | Current evidence / assessment |
| --- | --- |
| A. Official binary origin | YES: tracked bytes equal official LimitLabs/FW-Glyph at `9a78c7eeec87527b68644573e4c29fbdfb543239`; 23,336 bytes, SHA-256 `8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae`, blob `d0524944a90503a8881281b6673b1f46e36f9383`. |
| B. Project GPLv3 declaration | YES: [official README line 15](https://github.com/LimitLabs/FW-Glyph/blob/9a78c7eeec87527b68644573e4c29fbdfb543239/README.md#L15) declares the project GPL Version 3 and links the root [GPLv3 LICENSE](https://github.com/LimitLabs/FW-Glyph/blob/9a78c7eeec87527b68644573e4c29fbdfb543239/LICENSE). Exact blobs are recorded in G2F. This is project distribution evidence, not a blanket license claim about unrelated works. |
| C. Source correspondence | YES: unmodified GregTurbo/glyph-nuker root `b583d53ea71347f2721d40bf3b55933190bdc87a` reproduces the exact executable under the G2D recipe. |
| D. Authorship/provenance linkage | GitHub associates both the official binary introduction `cc57c4fc…` (Git name `stephen`) and matching source commit (Git name `Stephen`) with `GregTurbo`, whose account owns the source repository. The exact source/binary relationship is proved by reproduction, not account association alone. |
| E. Standalone source license | ABSENT in both inspected revisions: no separate LICENSE or explicit source-license declaration. This documentation fact alone does not establish that no applicable license exists. |
| F. Release obligation | Provide the matching Corresponding Source and recipe, retain GPLv3 project licensing and applicable upstream notices/attribution, and verify packaging before distributing the executable. |
| Direct fork | GitHub identifies this repository as a direct fork of LimitLabs/FW-Glyph (parent and source), reverified for G2F. |

The owner states that GregTurbo is one of the founders/owners of Limit Labs.
This is **OWNER_SUPPLIED** provenance. Independent public corroboration is not
recorded; it is not presented as independently verified public fact.

The engineering policy assesses the combined chain: author-associated source →
exact binary correspondence → official FW-Glyph distribution and project-level
GPLv3 declaration → direct fork. The standalone declaration's absence is retained
as a provenance caveat rather than an unresolved-source blocker. An explicit
component license clarification remains an optional improvement. This is the
owner-directed release-policy treatment, not a final legal opinion. It supersedes
the earlier mandatory upstream-contact proposal; no external contact is authorized
or performed.

### Corresponding Source packaging for H stage

The preferred engineering direction is to include the exact pinned source tree
under `third_party/glyph-nuker/`, preserve upstream attribution and applicable
notices, and retain this receipt and build instructions in a self-contained clean
source snapshot where practical. Required recipe: **Zig 0.15.2**, target
**x86_64-linux**, **ReleaseSmall**, **x86-64 baseline CPU**:

```sh
zig build -Dtarget=x86_64-linux -Doptimize=ReleaseSmall
```

The G2D receipt preserves full output/cache/verbosity arguments and the original
evidence. This is a reproduced recipe, **not historical maintainer build-command
attestation**. It grants no executable replacement, execution-safety or hardware
acceptance. Nunchuk remains NOT_TESTED; root cause remains unproven.

Actual source incorporation and packaging verification are deferred to H-stage
release staging. Another durable GPL-compliant source-delivery arrangement would
require a separate staging decision; the current exporter admits only exact
included source bytes, recipe/provenance and notices, not a source URL alone.
Normal export remains refused while packaging is incomplete. Diagnostic
validation omits the executable and reports the new packaging blocker for the
retained workflow. Including the executable without the required obligation or
complete matching source/provenance/notices is rejected even in diagnostic mode.
No firmware, workflow, executable, tested UF2 identity, qualification, freeze or
release state changes in G2F. Other campaign gates remain independent.

### Evidence progression

- G2B: bounded search did not find source at that time.
- G2C: author-owned candidate found; tested macOS environment produced no target.
- G2D: exact source/build correspondence established on Linux.
- G2E: evidence preserved and reviewed; licensing/export conservatively blocked.
- G2F: combined provenance reconciled; missing-source blocker retired, with
  Corresponding Source and notice packaging still required.

All following sections retain historical knowledge and policy at their own dates.
Their unresolved-source/contact requirements do not override current G2F policy.

## Historical G2D finding and G2E preservation — 2026-11-18

Stage result: `SOURCE_REPRODUCED_LICENSE_UNRESOLVED`.
Engineering export gate: **`REVIEW_REQUIRED` / PUBLIC EXPORT BLOCKED**.

The [G2D reproduction receipt](fixtures/glyph_nuker_source_reproduction_g2d.v1.json)
supersedes G2C's earlier **current-state** conclusion about source-build
correspondence at that checkpoint. G2F above supersedes its licensing/export policy.
G2C and the sealed August/G2B evidence remain unchanged historical
observations: the earlier macOS host-runner link failures produced no target
executable and do not contradict the later Linux result.

### Exact source-build correspondence

Unmodified [GregTurbo/glyph-nuker root revision](https://github.com/GregTurbo/glyph-nuker/tree/b583d53ea71347f2721d40bf3b55933190bdc87a)
`b583d53ea71347f2721d40bf3b55933190bdc87a`, built with verified official
**Zig 0.15.2** in disposable Debian 12 amd64 Linux containers, reproduces the
tracked executable byte-for-byte:

```sh
zig build -Dtarget=x86_64-linux -Doptimize=ReleaseSmall
```

The compiler log records **x86-64 baseline CPU**. There were no additional
strip/libc/linker flags; the fixture records the full common output/cache/verbosity
arguments. Linux x86-64 execution used architecture translation/emulation on a
macOS arm64 host; the exact translation backend is unknown. Source archives were
bound to pinned commit metadata by recomputing all Git blobs and recursive trees.
The official Zig archive was checked against its saved official release index
before extraction/execution. Their exact identities are in the receipt.

Matching output: **23,336 bytes**, stripped statically linked x86-64 Linux ELF;
SHA-256 `8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae`;
tracked Git blob `d0524944a90503a8881281b6673b1f46e36f9383`, mode `100755`.
Official binary origin remains the separately verified LimitLabs/FW-Glyph
provenance recorded in G2C below.

All eight bounded builds succeeded with fresh caches, each attempted once:

| Immutable source revision | Debug (default) | ReleaseSafe | ReleaseFast | ReleaseSmall |
| --- | --- | --- | --- | --- |
| `b583d53ea71347f2721d40bf3b55933190bdc87a` | DIFFERENT | DIFFERENT | DIFFERENT | **EXACT** |
| `5c544caa61fe378eb44be4edf74993b7841bf907` | DIFFERENT | DIFFERENT | DIFFERENT | DIFFERENT |

Every output's size/hash and comparison results are recorded in the fixture.
`cmp -s`, SHA-256 and Python direct byte equality agree. Synthetic identical-copy,
modified-byte and truncated-file controls respectively accepted/rejected/rejected.
A fresh G2D reviewer inspected the retained bytes, inputs, commands and raw logs
and found no material contradiction; it did not rerun builds. G2E inspected that
complete packet and rechecked identities, retained comparisons and controls.
Detailed logs and original reports are preserved privately outside the repository
and export tree; public report digests bind this summary to those records.

G2D executed no nuker and processed no firmware. This conclusion rests on the
recorded commands, inspected build graph and isolated mounts, without a
kernel-level execution audit. Exact byte correspondence establishes reproducibility
for this revision/configuration. It does **not** attest that the historical author
used this precise command or environment; historical maintainer attestation is
still absent. The seven different outputs establish only their bounded results.
No replacement, execution-safety or hardware qualification is granted.

### Licensing and public export remain unresolved

Keep these evidence domains separate:

1. **Binary origin:** verified official LimitLabs/FW-Glyph bytes (G2C).
2. **Source-build correspondence:** exact byte-identical reproduction (G2D).
3. **Historical original procedure:** not independently attested by the maintainer.
4. **Licensing:** source, executable and intended Corresponding Source distribution
   terms remain unresolved. Neither inspected GregTurbo source revision contains
   an explicit license declaration. Official FW-Glyph's repository-wide GPLv3
   statement does not establish its applicability to that separate source or
   clear the executable's historical distribution terms.
5. **Public export:** still blocked, with no release input cleared.

The narrowed private **UNSENT** request asks the author/authorized maintainer for
applicable licenses for the matching source and existing executable, permission
and completeness requirements for distributing the source as Corresponding Source
with firmware under the intended release arrangement, required notices/attribution,
and a clear source-repository license declaration. Historical source/build
confirmation is requested if available; another reproduction experiment is not
required. No upstream contact is authorized or performed.

`GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED` remains the release blocker. Normal export
refuses `glyph_nuker`; diagnostic staging omits the executable and retains its
workflow publication blocker. The owner-approved exact G2D receipt exception
includes evidence only and grants no executable/source redistribution clearance.
No firmware/build inputs, executable, workflow invocation or retained firmware
artifact changed; no hardware acceptance transfers.

## Historical G2C finding — 2026-11-18

The following section records G2C knowledge at that time; its current-state
conclusion is superseded by G2D above.

Stage result: `SOURCE_FOUND_BINARY_NOT_REPRODUCED`.
Engineering export gate: **`REVIEW_REQUIRED` / PUBLIC EXPORT BLOCKED**.

The exact canonical starting commit is
`07edd5a58964226e01c851f62ca3d2582b619ed6`. The
[G2C discovery follow-up](fixtures/glyph_nuker_source_discovery_g2b.v1.json)
records the current evidence separately from its retained G2B findings.
The [sealed August fixture](fixtures/glyph_nuker_source_lineage.json) below
remains historical evidence, not the current discovery result.

### Verified binary provenance

The public official [LimitLabs/FW-Glyph repository](https://github.com/LimitLabs/FW-Glyph/tree/9a78c7eeec87527b68644573e4c29fbdfb543239)
has one observed branch, `configurator`, at
`9a78c7eeec87527b68644573e4c29fbdfb543239`. Its `glyph_nuker` is mode
`100755`, 23,336 bytes, Git blob
`d0524944a90503a8881281b6673b1f46e36f9383`, SHA-256
`8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae`.
Direct byte comparison with this fork is exact.

The [upstream invocation](https://github.com/LimitLabs/FW-Glyph/blob/9a78c7eeec87527b68644573e4c29fbdfb543239/.github/workflows/build.yml)
moves the executable beside the UF2, enters that directory, invokes
`ls *.uf2 | xargs ./glyph_nuker`, then removes the executable. These four
commands match the canonical invocation block exactly; the complete workflows
are not claimed identical. The binary and invocation first appear together in
[big squash](https://github.com/LimitLabs/FW-Glyph/commit/cc57c4fcbcf25c5e33fab21fd5b8312e0543c8dd),
`cc57c4fcbcf25c5e33fab21fd5b8312e0543c8dd`, parent
`b38e53a64349bb2263096249813ae14f5ef1a304`. GitHub associates the author
with `GregTurbo`; the recorded Git author name is `stephen`, dated
2026-04-09T04:02:25Z.

The pinned upstream README states repository-wide GPL Version 3 licensing
and links its root GPLv3 LICENSE. This is supporting repository context only:
it does not establish the opaque tool's corresponding source, the candidate
source's license, or an exact build relationship. No legal conclusion is made.

### Author-owned source candidate; correspondence remains unknown

[GregTurbo/glyph-nuker](https://github.com/GregTurbo/glyph-nuker/tree/5c544caa61fe378eb44be4edf74993b7841bf907)
is a public author-owned source candidate. Its observed `master` is
`5c544caa61fe378eb44be4edf74993b7841bf907`; its sole parent/root is
`b583d53ea71347f2721d40bf3b55933190bdc87a`. Both trees contain exactly
`.gitignore`, `build.zig`, `build.zig.zon`, `src/main.zig`, and `src/root.zig`.
Neither has a LICENSE, README, or source license declaration; repository
metadata reports no license. **Candidate source license: `UNKNOWN`.**

The build entrypoint is source-evident as `zig build`. The package declares
minimum Zig 0.15.2 and no dependencies. The original compiler version, target,
optimization/link/strip options, and which revision produced the tracked binary
are undocumented. The newer revision changes the source's overlap calculation;
neither revision can be assumed to correspond to the binary.

Candidate source reads UF2 and writes a separate `_with_config_reset.uf2`
with zero-payload blocks over its declared filesystem interval. This describes
only the pinned source; it does not establish the tracked executable's purpose
or transformation. No source was copied into the public tree.

A bounded clean build used the official SHA-256-verified Zig 0.15.2
`aarch64-macos` toolchain and source-evident `-Dtarget=x86_64-linux`
(the tracked file is an x86-64 Linux ELF). Debug was the source default, not a
claimed original setting. Both attempts used empty local/global caches; the
second supplied the installed macOS SDK with permitted filesystem access.
Both exited 2 while linking Zig's host build runner, with unresolved macOS
symbols including `__availability_version_check` and `_abort`. No target
executable was produced; hash, size, type, and exact-byte comparison are
therefore **NOT POSSIBLE**, rather than a mismatch or equivalence finding.
This host/toolchain limitation does not prove the source cannot build elsewhere.
Neither tracked nor source-built nuker was executed during these source-discovery
probes. The separately authorized unchanged hosted firmware build may execute
the tracked tool; that does not establish source correspondence. The detailed classification
is `SOURCE_FOUND_BUILD_RECIPE_INCOMPLETE`; the stage disposition records that
source was found but the binary was not reproduced.

### Bounded coverage and external requirement

The discovery fixture enumerates every searched surface and limitation:
all advertised official FW-Glyph refs (one branch, two tags, and advertised PR
refs), 480 reachable commits / 1,653 unique blobs / 1,649 UTF-8 text blobs;
complete introduction and parent inventories; both official release source
archives; official LimitLabs repository inventory and scoped exact name/hash/
postprocessing searches; both HayBox-proto branch heads; official Glyph resource,
configurator and download locators; the unavailable historical HayBox-Glyph
locator; both candidate source commits; and bounded web discovery. Only the
workflow invocation matched within FW-Glyph text. Third-party PRs, mirrors and
random forks are not source authority. No global absence is claimed.

For the **exact tracked binary**, corresponding source/source lineage, purpose,
byte transformation, build recipe, reproducibility and applicable license remain
`UNKNOWN`. Binary origin is now verified; source/build clearance is not.
An upstream maintainer must identify the corresponding revision/paths, applicable
source license, original compiler and target/build options, and an exact binary
recipe or explicit source/binary relationship. A private unsent request packet
is prepared outside the export tree. No upstream contact occurred.

No firmware/controller source, workflow, executable bytes, invocation, ordering,
or retained UF2 changed. No new artifact inherits hardware acceptance.
Normal export continues to refuse the one unresolved path/dependency,
`glyph_nuker`; diagnostic staging omits it and retains the explicit workflow
publication blocker `GLYPH_NUKER_EXTERNAL_SOURCE_REQUIRED`.

The offline checker seals the new discovery receipt and rejects unsupported
promotion of canonical claims, candidate licensing/correspondence, or export
clearance. It still validates the preserved historical receipt independently.

## Historical bounded search — 2026-08-29

The following original report is retained as historical evidence. Its not-found
status describes that search, not the later author-owned candidate discovery.

Status: `BOUNDED_SOURCE_LINEAGE_NOT_FOUND`.

This packet records a bounded, read-only search performed on 2026-08-29 for
authoritative source, purpose, byte transformation, and build recipe for the
tracked `glyph_nuker` executable. The search covered the exact repository
history and live SenatorSSB repository refs/tags/releases, plus the
source-named `GregTurbo/HayBox-Glyph` repository. No authoritative source or
recipe was found. This is not a claim of global absence.

The current tracked file is mode `100755`, Git blob
`d0524944a90503a8881281b6673b1f46e36f9383`, and SHA-256
`8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae`. Local
full-history inspection reaches only its binary introduction in squash commit
`cc57c4fcbcf25c5e33fab21fd5b8312e0543c8dd` (tag `1.0.6`). The current workflow
invokes it as `ls *.uf2 | xargs ./glyph_nuker` after moving it beside the UF2.

The packet does not execute, disassemble, rebuild, replace, or compare any
artifact. Therefore purpose, byte transformation, source lineage, build
recipe, reproducibility, safety, artifact acceptance, and hardware evidence
remain `UNKNOWN`.

The deterministic offline checker is:

```text
python3 tools/check_glyph_nuker_source_lineage.py
```

It validates only checked-in facts and the recorded bounded-search shape; it
performs no network access and no binary or artifact execution.
