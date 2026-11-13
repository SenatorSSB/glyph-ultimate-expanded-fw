# Supervisor review corrections — 2026-11-13

Owner follow-up explicitly authorizes these three host-tooling/documentation corrections and publication of traceable successors, returning for review. The uncommitted supervisor drafts were treated as unreviewed scratch, independently checked, integrated and tested. No controller access, flash, firmware promotion or release. The combined firmware remains `84556d904f067bda5a101e6297689239ecd04aae`; its retained UF2 remains `6b3fd3e2f71b839e7448ab6b0daa54e5d4f1d6473d0df917849413e3f4227ddb`. All prior acceptance evidence is retained. Hardware acceptance remains pending.

## Implemented scope

- Cache validation includes `ProfileStoreLifecycle.inc` and other `ProfileStore*.inc` dependencies. Old incomplete manifests require rebuilding; verification precedes corpus imports and execution.
- The lifecycle operator derives an independent exact expected-after Config before sending, saves the expected bytes/hash and row/RGB/default maps, and compares the complete observed Config after receipt/hash/CRC verification. UPDATE covers the complete replacement row. Row/RGB/default compaction retains surviving reference meanings. Root fields, unrelated objects/backend definitions and historical receipts stay exact. Committed mismatches remain terminal `receipt-only`, with evidence and the no-resend claim retained.
- The companion Senscope source-authority navigation note distinguishes historical `a6e3bc88`, accepted `f4146bed` and hardware-pending `84556d90`. Frozen contracts and historical pins remain unchanged.

## Host verification

- `test_build_manifest.py`: 5 tests, including actual `run.py --no-build` refusal for an include-only change and an old incomplete manifest.
- Fresh production harness built with ASan/UBSan and boot probe. Fingerprint `dcf4cb9718d848ccdfcc1d87e23fba63336b15e874f48d0e1622e7f41dd11fa2`. Actual cached `run.py` smoke: 6/6 cases, explicitly `complete:false`; not exhaustive interruption coverage.
- Production `regressions.py`: 64 groups. `lifecycle_regressions.py`: 108 cut/restart cases across five operations, including UPDATE RGB remove/add, surviving default reindexing and capacity reuse. `lifecycle_bounds.py`: response241/framed244 and request4580/framed4601.
- `test-config-preservation.py`: 13 complete Config comparisons (7 independent protoc fixtures and6 production-storage outputs, including an additional actual RGB replacement), 3,839 corruption controls (3,791 single-byte flips and48 named field changes). Twenty self-consistent corrupt Config/receipt operator episodes preserve evidence, return `receipt-only` and refuse resend.
- Routine Vitest preservation tests: 4 passed. Original lifecycle operator: four operations,17 failure cases and20 incomplete captures passed. Original CLI with the retained UF2/fake pyserial and Python bridge6 tests passed.
- Candidate verifier: 2,591 UF2 blocks and663,212 binary bytes; ELF/BIN/map hashes verified. Firmware inputs equal84556d90; all retained candidate files unchanged from the handoff parent.
- Semantic promotion gate: passed using the existing Senscope Python environment; 37 sources/212 memberships unchanged.

The full clean-commit `npm run ci` result is recorded in the verification successor before publication. The first attempt stopped at the default Python3.15 missing pytest; the existing Senscope `.venv/bin` supplies it. No dependency or account settings were changed. The frozen corpus's generated Python7.35.1 code did not match the available protobuf6.33.6 runtime. A private temporary corpus copy regenerated only Python adapters from its unchanged schemas using the available grpc_tools; retained fixtures/provenance were not rewritten.

## Reproduction

Use Python with grpc_tools for the harness build, cache tests, lifecycle regressions and bounds. With the fresh lifecycle outputs run:

```sh
python3 -B tools/hardware-acceptance/productization/test-config-preservation.py --glyph /path/to/exact/tooling-successor --production /path/to/fresh/lifecycle --binary /path/to/fresh/build/package-fault-harness
```

Use the repository's existing Senscope Python environment first on PATH for `npm run ci` and `npm run check:semantic-promotion-gate`. All operator tests use fake ports; none opens a controller.

## Delegation and publication boundaries

Native internal delegation was available and used: separate read-only cache and preservation/source reviewers, followed by a fresh independent implementation reviewer. Root owns integrated mutation, validation and Git. Code review: DONE; final verification metadata is reviewed separately. Publish tooling/documentation successors of the existing campaign branches only. Canonical branches and the firmware artifact are not promoted. The untracked Glyph `.pio` dependency symlink is excluded. Senscope uses a non-slash local branch because an existing local codex reflog file blocks a codex/ namespace; no old refs/logs were deleted.

API-visible canonical Config equality does not prove raw NOR identity, installed-build attestation, physical runtime/display/input or board power-loss behavior. Direct GameCube/Switch runtime identity remains unverified. Core1 replay needs no change. Full package-authoring persistence beyond the completed plate work is outside this follow-up.
