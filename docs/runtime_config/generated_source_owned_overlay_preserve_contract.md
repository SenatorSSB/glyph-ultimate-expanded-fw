# Source-Owned Overlay/Preserve Contract

Status label: CURRENT.

Candidate generation has three explicit modes:

- `full_replacement` requires all 28 active tables and emits every table as
  `replace_explicit_owned`.
- `overlay_preserve` requires an exact current source-owned baseline identity,
  an explicit `owned_tables` list, and table data for every owned slot. Every
  other slot is copied semantically from that baseline.
- `reject_partial` refuses partial input before generation.

The overlay generator is `tools/generate_glyph_source_owned_overlay_preserve.py`.
Its independent comparison path is
`tools/compare_glyph_source_owned_overlay_preserve.py`; the checker and
negative corpus are in `tools/check_glyph_source_owned_overlay_preserve.py`.

Every successful artifact contains 28 tables and a deterministic manifest. A
manifest row identifies the table symbol, ownership source, per-table baseline
and candidate semantic digests, changed status, action, and reason. An
unowned changed table, missing owned input, unknown symbol, duplicate ownership
entry, baseline identity mismatch, wrong shape, or incomplete manifest is a
hard failure.

Production preparation/install rejects example, demonstration, and fixture
provenance. Test-only provenance overrides exist only for checker/test paths;
they are not accepted by production installation.

An overlay whose owned values equal the baseline is `NO_OP` and is not a
hardware candidate. A non-empty authorized difference is classified
`EXPLICIT_OWNED_TABLE_CHANGESET`, but remains separate from active source
installation and requires its own build and hardware gate. The previous
canonical-grid failure was possible because a complete example artifact could
replace unspecified tables with canonical defaults; explicit ownership and
semantic preservation now prevent that recurrence.

This is offline tooling only. It does not implement runtime-loaded config,
storage, WebSerial/device write, protobuf binary write, or flashing.
