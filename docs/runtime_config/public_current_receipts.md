# Current semantic and observation receipts

The G2B receipts make current validation independent of development Git objects.
Provenance commit IDs are inert metadata. Missing history never enables a weaker
proof. Receipt SHA-256 identities are pinned in their current checkers.

`fixtures/source_owned_x1_pre_f4_semantic_reference.v1.json` captures the exact
pre-F4 intake, its stale-baseline and current-baseline review results and emitted
input/artifact/manifest semantics. Only authority metadata and its two derived
semantic digests are normalized; the existing X1 authority receipt, exact nine
coordinates, sole `kX1Table` ownership and all other tables remain protected.
The original implementation replay remains available explicitly with
`python3 tools/check_glyph_source_owned_source_authority_intake.py --historical-f4`.

`fixtures/build_input_observation_receipt.v1.json` seals the original declaration
snapshots and timestamped observation bytes. The ordinary checker also validates
current source declaration contexts and wrapper-chain invariants. Historical
observations do not establish current dependency resolution or reproducible
builds. The additional original Git-object proof remains available explicitly:
`python3 tools/check_glyph_build_input_resolution_observations.py --historical`.

The existing `fixtures/glyph_nuker_source_lineage.json` remains a sealed bounded
search receipt with UNKNOWN claims. Ordinary validation checks that receipt and
the current invocation. Explicit historical object authentication remains:
`python3 tools/check_glyph_nuker_source_lineage.py --historical`.
An omitted executable requires the authenticated public package contract's exact
`OMIT_AND_BLOCK_PUBLICATION` record. Receipt validation PASS is neither source
lineage nor license, firmware equivalence, redistribution or hardware acceptance.
The public exporter must independently block publication of the workflow that
requires the omitted executable.

The READ-storage checker already uses the checked-in response fixtures; its
unused owner-local constant was removed. Real-predecessor replay requires an
explicit `GLYPH_REAL_PREDECESSOR_BACKUP` input and still demands exactly 4,201
bytes with SHA-256 `f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480`.
No private backup was copied, no evidence byte fabricated and no device accessed.
