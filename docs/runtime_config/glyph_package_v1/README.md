# Paired package firmware candidate

`FULLPKG-B2-CREATE-PACKAGE-FIRMWARE` implements the owner-authorized frozen
`glyph-package-v1` contract as a candidate on its own branch. Canonical Glyph
integration, source acceptance and hardware acceptance are separate actions.

The binding engineering oracle is Senscope's `contracts/glyph-package-v1/` at
published work `cd9b9b387fe64e1d6acb9546b212b045bf158be4` (Git tree
`395a827f5561afa034607fe72095b991babec646`). The implementation base is Glyph
`d31a5edd433beca0354e4595c26d0c4b69c085e8`. Senscope's accepted source pin stays
`a6e3bc885d46e2a7412ec697aa822bcd8c4ce495`; this candidate does not change it.

## Implementation boundaries

Mk6 enables `GLYPH_PACKAGE_V1` and command9/protocol3 STATUS, CREATE_PACKAGE15
and QUERY_PACKAGE16. The strict wire readers reject unknown, noncanonical,
duplicate, malformed and over-bound inputs before admission. Native schema5,
encoding1 and ABI1 body bytes retain their existing source validation.

CREATE appends one Ultimate row, one stable-ID record, and optionally one
exclusive RGB slot. It preserves existing rows, records, backend/default
destinations and complete managed ownership. Config publication is installation.
Publication proceeds through durable PREPARED, record, store, Config and terminal
metadata, with checked staging, sync, close, exact readback and rename. An error
ends that invocation; no automatic retry, continuation, rollback or cleanup is
introduced. QUERY and protocol3 STATUS perform no persistent writes.

Root3, control, intent and managed record2 use the frozen byte layouts. Large
root/control transfers use segmented existing owners. PackageBody and intent
share the initialization owner at separate lifetimes; borrowed request/native
callbacks end before their source is reused. Pending packages stay outside
ordinary read/health/activation/selection paths. The legacy selector cannot
rewrite package-owned rows or reuse managed backing records.

Checked configuration disables LittleFS auto-format before mount. Unclassified,
unsupported, unresolved or unavailable storage denies persistent writers. A
scoped lower guard binds writer kind, token, phase and exact paths, including
already-open writable handles and cleanup. Same-boot uncertainty remains fenced
through later queries. No factory reset, managed migration, updater, host
product integration or device action is part of B2.

## Reproducible checks

Point component checks at the unchanged published Senscope oracle:

```sh
python3 tools/check_glyph_package_components.py --corpus /path/to/senscope/contracts/glyph-package-v1
```

This compiles the repository's actual wire, storage-format, classifier and
checked-storage components. The independent expected data and source validators
remain in the frozen corpus. Outputs default to a temporary directory. Python
protobuf/grpc-tools, a host C/C++ compiler and pinned LittleFS sources are needed;
these tests operate on synthetic data and RAM storage.

The canonical target command remains `pio run -e glyph_mk6`. If `pio` is not on
PATH, the existing `./scripts/build-glyph-mk6-quiet.sh` wrapper is the documented
fallback. Mk6 emits stack-usage files and a link map for exact resource review.
The source-label build hook requires a clean committed source snapshot.

Adafruit GFX is pinned to 1.12.6 so the accepted graphics/core1 source proof is
not transferred across a floating dependency upgrade. Its source SHA-256 values
are `e4ace04cbed4499c0e2a80df33b381c87ce98689d98da82712f0748bf7359171`
(`Adafruit_GFX.h`) and
`5afa8ca16241a9a0cb354012dd00780c6c00620c345b810a9504cb77bfc698d5`
(`Adafruit_GFX.cpp`). Build evidence must record the actual selected dependencies.

## Evidence and acceptance

An exact candidate requires production-source transaction/fault/restart and
legacy regression results, linked Mk6 flash/static/stack/lifetime proofs, exact
ELF/binary/UF2/map identities, strongest technical review and fresh independent
final review. Component passes alone do not establish that result. Senscope's
B2 REVIEW evidence binds the existing final candidate commit and those results;
no commit embeds its own future SHA.

No physical controller operation, flash, port enumeration, gameplay test or
hardware PASS follows from this candidate or these host checks.
