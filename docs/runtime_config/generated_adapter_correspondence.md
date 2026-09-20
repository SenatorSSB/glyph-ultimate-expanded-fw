# Generated Adapter Correspondence

The current load-bearing source-sync checker parses the active
`SOURCE_OWNED_GENERATED_TABLE` and `SOURCE_OWNED_GENERATED_TABLE_POINT`
macros in `src/modes/UltimateIdentityRuntimeTables.hpp`. It proves the exact
28 symbol/index aliases, point indices `0` through `8`, x-then-y expansion,
and the canonical generated raw-array namespace.

The extractor's existing `TABLE_SYMBOL_TO_NAME` order remains the only table
identity authority. The fixture at
`docs/runtime_config/fixtures/generated_adapter_correspondence.json` records
the bounded grammar contract; it does not define table values, runtime
publication, or firmware behavior.

The historical table-replacement checker reuses this parser. It no longer
maintains a second alias regex or table-order authority.
