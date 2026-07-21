# Runtime-config validation health

This inventory records the controlled baseline run at
`116d34322837fe1f6f724c820b49ccb0d24d6787`. Its machine-readable companion is
`fixtures/runtime_config_validation_health.json`.

The current source-owned contract is 28 ordered tables ending in
`kLt1LowMagnitudeTable`, with semantic digest
`9ea314bd17680d8353198ac174e59faf84c419fcd95a4ef3db24b3bd7e0f2970`.

The two load-bearing baseline failures were
`check_glyph_identity_runtime_table_source_sync.py` and
`check_glyph_runtime_config_semantics_evaluator_bridge.py`. Both read the
stale 27-table `current_baseline_runtime_config_semantics_bridge.json` and are
classified `PRE_EXISTING_FIXTURE_DRIFT`, never PASS. The 27-table generated
prototype is preserved as historical evaluator evidence, not relabelled as a
current baseline.

Commands that can prepare, install, or emit a candidate are classified unsafe
for this offline validation lane. Historical and hardware-result checkers are
explicit inventory entries; they are not counted as current aggregate passes.
