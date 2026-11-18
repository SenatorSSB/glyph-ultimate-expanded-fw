# Source Lineage

Source commit, source tree, build evidence, firmware bytes, acceptance publication
and later canonical documentation are different identities. Later documentation
descendants are not the tested source. Build proof is not hardware acceptance;
a CI rebuild does not inherit hardware acceptance of the retained artifact.

## Current first-beta lineage

| Role | Identity |
| --- | --- |
| Tested source | `dcf6e29589f558a95c021bef491578f87e41750f` |
| Tested source tree | `a7731388430ea70dbe666298953795f4018069b0` |
| Build-evidence commit | `ebde1447f5cf348b3af82240ebd95445b44cb888` |
| Retained tested UF2 SHA-256 | `2c77e2b7e50af2fd3b516d1ee7d0b8a67bcf992d6fcf0e3109a837422740cd42` |
| Retained tested UF2 size | 1,325,568 bytes |
| Source-free acceptance record | `2d64e75a1f020d1f7564d3a15db63cb7fcffe96a` |
| Acceptance review / canonical integration-preparation descendant | `9f6e0d0e0bea0e5dcd9292d55cc2c4e2d8af8c62` |
| Canonical documentation baseline after Batch D | `935f08f72dc52476dfbdd2e0059467c13ac5cd9d` |

Git object inspection proves `dcf6e295^{tree}` equals the tested tree above.
`git rev-list --parents` and `git merge-base --is-ancestor` prove the three solid
parent edges below and the ancestry edge to Batch D. The dotted edge spans
intermediate commits rather than asserting direct parentage.

```mermaid
flowchart LR
    S[dcf6e295: tested production source] --> B[ebde1447: build evidence]
    B --> E[2d64e75a: acceptance record]
    E --> I[9f6e0d0e: review and integration preparation]
    I -. ancestry through documentation and host-tool commits .-> D[935f08f7: Batch D canonical baseline]
```

[Hardware acceptance](HARDWARE_ACCEPTANCE.md) owns physical scope. The retained
original packet review binds the source-free acceptance publication above. Its
pending-integration wording describes that time. [CURRENT_STATE](../CURRENT_STATE.md)
records later completed canonical
integration. The baseline was live-verified on `configurator` at Stage E intake;
it is not the UF2 build source, an activated freeze or a release.

The UF2 hash/size come from the accepted retained-artifact records, not Git tree
identity or a rebuild. No private retained artifact was read by this extraction.
See [hardware acceptance](HARDWARE_ACCEPTANCE.md) for installation-attestation limits.

## Build-input equivalence

The original source-equivalence record establishes complete mode/type/blob/path
equality of 1,254 non-documentation paths for
build-evidence and acceptance descendants at its recorded scope. That complete
non-doc equality must not be extended to later documentation work by assumption.

Stage E mechanically compared `git ls-tree -r -z` inventories for the tested
source and all 18 descendant commits through Batch D. Every path
in the retained 329-path production-input inventory
is identical in mode/type/blob/path across those commits. The repository's
[critical-path helper](../../tools/glyph_tracked_worktree_integrity.py) selects 327
critical entries; these and all five schema entries also remain identical.
These are finite tracked-input comparisons, not a claim about external dependency
cache identity, arbitrary untracked files or reproducible UF2 bytes.

Batch D differs from tested source in ten non-doc paths: root README, profile
README/seed and host audit/validation tools/tests. The Git trees therefore differ,
and later checker/tooling changes are real changes even when firmware inputs
remain equal. Stage E adds only the allowlisted history/navigation/checker/census
paths; it preserves the same firmware/build/schema inventories. Its eventual
commit remains a documentation/checker descendant, never a new physical test.

To verify without a build: resolve the tested tree with `git rev-parse`, check
ancestry with `git merge-base --is-ancestor`, enumerate each side with
`git ls-tree -r -z`, and compare mode/type/blob/path entries for the original production
inventory and critical/schema sets. Exact replay of that historical comparison
requires the privately preserved inventory named in Historical source provenance;
the critical/schema sets remain inspectable in current source. Compare the full
inventories separately to
avoid mistaking scoped equivalence for identical Git trees. No classifier
exemptions or historical correspondence rules are changed here.

## Major profile lineage

The Kazuya source tree retains v1→v5 sources and their frozen checks, with
[canonical JSON](../../profiles/kazuya/Kazuya.profile.json) pointing to v5. Git object checks confirm the historical v1 blob
`542ef2607457b42f324d4962ed2bb543f317cd21`, v4 blob
`50741602af1b8e5bf70bdc745416ca9a794ee3c7` and v5 blob
`64c2825605082701b9252832149535c82ebb7fc5` remain unchanged at Batch D.
Canonical `Kazuya.profile.json` equals v5 byte-for-byte. V4 remains the accepted
rollback reference; v1–v3 evidence is retained, not replayed against a substituted
canonical source. Wrapper identities and acceptance limits belong in
[hardware acceptance](HARDWARE_ACCEPTANCE.md), with detailed authoring lineage
remaining under `profiles/kazuya/`.

## Future clean release repository

The reviewed release preparation calls for:

```text
original tested history/evidence
  → reviewed content snapshot with explicit correspondence
  → fresh clean public Git history
```

A fresh public repository commit will not become the physically tested source
commit. It must retain explicit correspondence to the original source/tree and
retained tested artifact evidence. Preserve upstream copyright/license attribution;
review export contents and recoverable private preservation before publication.
Stage E creates no release repository, export, freeze, release or Senscope repin.

## Historical source provenance

The following original development-fork records supplied the selected facts
above at snapshot `5c54d0dcca304f476720655c96f315bac5ed2f6b`. These are provenance
identifiers, not supported public navigation. Preserve the originals privately
when preparing an export; their omission does not broaden any acceptance.

```text
docs/planning/final-usb-gamepad/acceptance/PACKET_REVIEW.json
docs/planning/final-usb-gamepad/acceptance/README.md
docs/planning/final-usb-gamepad/acceptance/SOURCE_EQUIVALENCE.json
docs/planning/final-usb-gamepad/production-inputs.json
```
