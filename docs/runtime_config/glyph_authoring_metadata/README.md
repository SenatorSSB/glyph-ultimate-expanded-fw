# Bounded authoring metadata candidate

Controlling specification: Senscope commit
`f772caa106647ea445f96cd15e116efc36d4689b`,
`docs/project/GLYPH_AUTHORING_METADATA_ARCHITECTURE.md`.
Glyph implementation base: `83fdfa763e5504e7ada57bf6f414fb9349590f8f`.

This candidate adds PackageBody2, managed record3 and manifest1. Existing body1
and record2 remain supported with their historical meanings and limits. A rich
profile owns the same single immutable record object and 128-byte header. Its
payload is the schema5 wrapper followed by bounded inert metadata; offset20 is
wrapper length. CRC, full-record SHA and existing transaction/aggregate witnesses
cover all metadata. Maximum record size3840 retains the4096 package charge.

Manifest1 carries the nonzero28-bit declared-slot mask and one exact UTF-8 name
per declared slot, in ascending order. Names are1..64 bytes, duplicates allowed,
without NUL, normalization, trimming or replacement decoding. Total metadata is
at most371 bytes. New body2 writes validate the complete grammar. Stored future
versions remain bounded opaque data for execution, rich read and rename/reorder.
Body1 UPDATE of record3 refuses before durable intent. No migration or sidecar.

Capability3/bit9 advertises body2/record3/rich-read1 together. Protocol3 receipts
remain1, protocol4 receipts remain2. Protocol2 READ field24 explicitly opts into
the strict ordered canonical guarded request; malformed24 cannot fall through.
Success appends typed bounded response fields218–221, without growing generated
response ownership. Record2 returns ABSENT; record3 returns PRESENT and exact
metadata. Both include whole-record SHA and current record format. The same
synchronous native/metadata lease lasts through response transport settlement.

Native schema5, GNP5, evaluator ABI and frame execution are unchanged. Only the
validated wrapper span enters native decoding. Metadata never reaches evaluator
state. No gameplay semantics, label UI, automatic activation or duplication
product feature is added.

Executable proof entry points:

```sh
python3 tools/glyph_ci_current_package_tests.py
python3 tools/fixtures/glyph_authoring_metadata/regressions.py --binary HOST_HARNESS --out EVIDENCE
python3 tools/fixtures/glyph_package_v1/transaction/lifecycle_regressions.py --corpus FROZEN_V1_CORPUS --binary HOST_HARNESS --out EVIDENCE --rich --all-cuts
```

The existing transaction builder regenerates Nanopb from actual schema/options.
Target layout probes and exact committed Mk6 build evidence belong with candidate
handoff. The sealed public source inventory advances with this reviewed candidate;
all exact-source/mode/index/manifest checks and negative controls remain enabled.
Historical evidence stays in Git and is not relabeled as rich acceptance.

Host/source/build proof is not hardware acceptance. No hardware operation is
authorized here, and this branch must not merge into `configurator` before a
separate exact-candidate hardware acceptance packet and actual human result.
