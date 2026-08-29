# `glyph_nuker` Source Lineage

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
