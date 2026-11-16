# GOPT canonical integration preparation

**Integration preparation only. Canonical configurator remains unchanged; public beta remains held.**

The candidate branch is `codex/gopt-canonical-integration-prep`.
It preserves the exact tested source, its independent host review and the separate
qualification documentation through genuine merge ancestry. No accepted history
was rewritten, and no unrelated experimental source was imported.

## Proposed source integration

Canonical baseline is `2bcb5104054f64d8b9c1af9dd1be4a974112f8ec`.
The first integration merge preserves host review `399e06f099a96a4e903cb349fcc7ee03e9d749b2`
and its tested-source ancestor `55739675e5706ea8799265c4221724ac4f2dce9b`.
The second merge, `ea74179498d48d87874dfa7f23f8c102ce5b0c6f`, adds qualification
`ae0ab6e071f6259a0ab1149a9874127d360cd91c` as a genuine parent.
Subsequent changes are sanitized documentation and receipts only.

The exact proposed operation is a fast-forward from the baseline to the final
reviewed candidate tip reported in the supervisory delivery. It is conditional
on separate exact owner approval and a fresh unchanged canonical ref. No canonical
operation was performed. Canonical drift requires reassessment, not blind promotion.

All 323 tracked mode/blob/path entries across HAL, src, include, lib, config,
schema, builder_scripts and platformio.ini equal the exact tested source.
The complete non-documentation delta from that source is empty. Relative to
canonical, the only production differences are the accepted saved-Config CRC,
normal report-loop lock and bounded dashboard-label changes. Corresponding tests,
checker census and host review are retained. See [source correspondence](integration/source-correspondence.json)
and [dependency correspondence](integration/dependency-correspondence.json).

## Build, artifacts and resource limits

A clean `pio run -e glyph_mk6` passed at committed integration source
`ea74179498d48d87874dfa7f23f8c102ce5b0c6f`, using the retained pinned toolchain.
All 545 dependency files match the tested-source checkout exactly.
Later candidate commits contain documentation only and were not rebuilt.

The rebuilt BIN is 662,516 bytes, SHA-256
`81a6d001cb46bec09d61caf4b29069f4d0c131e49939f45330673f9e27684242`.
The rebuilt UF2 is 1,325,056 bytes, SHA-256
`a2f59824141979ca4fa01b3646306a91bb81af03c365f7ea739a9ea190814742`.
Independent ELF-to-BIN conversion matches; all 2,588 ordered RP2040 UF2 blocks
reconstruct the rebuilt BIN plus zero padding.

Exactly 34 BIN bytes differ from the physically tested image: the two eight-character
source labels beginning at offsets 582090 and 601744, and the twenty-byte full source
identity at offset 583432. No other BIN byte differs. Both old and new values and
all four rebuilt artifact hashes are in [artifact correspondence](integration/artifact-correspondence.json).
This establishes bounded source/artifact correspondence, not physical testing of
the rebuilt image. The accepted physical UF2 remains exclusively `63cb30b4…` at
source `55739675…`; it was never replaced.

Linked resource replay passes the finite model: flash 650,484 bytes, static RAM
198,888, heap capacity 63,060, two 2,048-byte stack reservations, core0 maximum
2,048/lifecycle 2,044, CRC maximum 1,556 and core1 bound 1,068 within 1,152.
Seven graph mutations were rejected. Inherited legacy/lifecycle margins remain
zero/four bytes; physical high-water remains unqualified.
[Resource receipt](integration/resource-summary.json) · [Negative controls](integration/graph-controls.json)

## Verification and physical disposition

Twenty current-host commands, eight transaction build/regression commands, two
bounds checks and both-ABI dashboard transition/negative controls pass.
Checker census, build-input inventories, navigation, Git whitespace and conflict
checks pass. Initial missing-dependency setup failures and the nested-checkout
aggregate refusal are retained locally; they were not counted as passes.
[Command receipts and log digests](integration/verification.json)

The current-host commands compile or inspect actual working sources and do not
use the ambient comparison ref to select candidate scope. Their results remain
valid. An earlier aggregate diagnostic used a stale local comparison ref and
returned eleven passes followed by its adversarial self-test's 120-second timeout;
that is not an exact-canonical aggregate pass. The separate exact-base result is
recorded in [the exact-base aggregate receipt](integration/local-aggregate-summary.json):
eleven checks PASS, adversarial self-test CHECKER_TIMEOUT at 120.004 seconds,
canonical proof MATCH, census PASS. No full local aggregate PASS is claimed.
The same self-test timed out in the original qualification; this is retained
validation debt, with no concrete production-source contradiction identified.

[Physical closeout](PHYSICAL_CLOSEOUT.md) preserves the owner's accepted partial
scope, all individual timings and uncertainty, precise API-visible preservation,
profile27 hold, identical53/54 limitation, physical ellipsis gap and beta blockers.
Fresh independent physical-evidence and complete integration reviews found no
material discrepancy. Reviewer inspection is not independent physical observation.

## Safe candidate publication

Both workflows were inspected. The ordinary push/PR workflow builds and uploads
firmware when its event diff includes production files or any non-Markdown input.
Initial candidate publication therefore uses `[skip ci]`; no PR, tag, release or
workflow-dispatch operation is authorized here. The separate device-config workflow
is workflow-call only and is not invoked.

A subsequent strictly Markdown-only event diff can run current-host and runtime
validation while the existing classifier returns `firmware=false`. This preserves
normal hosted verification without publishing a rebuilt firmware artifact. It does
not qualify a public beta. The final hosted result and artifact count are recorded
with their exact run/commit identity before supervisory completion.

No controller operation, firmware installation, Config/profile write, new optimization,
protected-profile change, canonical update or release occurred during preparation.
Original private evidence and backups remain locally retained and unmodified.
