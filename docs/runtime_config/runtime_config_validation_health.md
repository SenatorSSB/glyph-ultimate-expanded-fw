# Runtime-config validation health

This health record has two explicit layers. The repository-wide layer is the
mechanical checker census at `fixtures/glyph_checker_census.json`; it discovers
every `tools/check_glyph_*.py` path without executing or behaviorally auditing
those checkers. Its count is derived from discovery, not treated as a permanent
constant. The curated layer is
`fixtures/runtime_config_validation_manifest.json`, which records only the
current runtime-config dependency graph and its explicit historical,
evidentiary, and unsafe exclusions.

This corrects the earlier single-level inventory scope. The prior records are
preserved as current-result, historical-evidence, and exclusion records below;
they are not evidence that every repository checker received a manual semantic
assessment. The controlled starting baseline remains
`116d34322837fe1f6f724c820b49ccb0d24d6787`.

The current aggregate treats census freshness as a load-bearing baseline gate:
any added, removed, renamed, or byte-changed `tools/check_glyph_*.py` file
fails the aggregate until the static census is deterministically regenerated.
The census generator only performs static inspection and never imports or
executes discovered checkers; the curated manifest remains authoritative for
which checks are current and load-bearing.

The current source-owned contract is 28 ordered tables ending in
`kLt1LowMagnitudeTable`, with semantic digest
`9ea314bd17680d8353198ac174e59faf84c419fcd95a4ef3db24b3bd7e0f2970`.

The two repaired load-bearing baseline failures were
`check_glyph_identity_runtime_table_source_sync.py` and
`check_glyph_runtime_config_semantics_evaluator_bridge.py`. Both read the
stale 27-table `current_baseline_runtime_config_semantics_bridge.json` at the
starting configurator baseline. The first also had the stale 27-table
interpreter bridge fixture; the second had the stale `Ultimate.cpp` SHA and
27-table bridge lineage. Both pass with the repaired current fixture. The
27-table generated-prototype evaluator remains historical evidence, not a
current aggregate PASS.

Commands that can prepare, install, or emit a candidate are classified unsafe
for this offline validation lane. Historical and hardware-result checkers are
explicit curated records; they are not counted as current aggregate passes.

The curated manifest now has 26 explicit entries, including 21 current
load-bearing checks. The prepared-v2 C++ preview checker is current and
load-bearing because it validates the inactive authority-preserving preview
seam; it does not install source, create a candidate, or change firmware
behavior. The added behavior evaluator remains superseded historical evidence
because its May-28 behavior-case dependency is historical; it is not a current
aggregate PASS.
