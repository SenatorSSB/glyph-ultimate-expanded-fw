# Source-Owned Literal Table Replacement Contract

Status: SUPERSEDED / HISTORICAL DOCS-TOOLS CONTRACT.

This packet preserves the former 27-table literal-body replacement contract as
historical evidence. It is not a current production contract, does not
authorize a table set, and does not establish hardware validity.

## What Was Superseded

The prior generator modeled exactly 27 literal table bodies: `constexpr
StickPoint ...[9]` definitions in `src/modes/UltimateIdentityRuntimeTables.hpp`.
It emitted a
separate patched-header fixture. That representation is no longer current.

The active source now includes
`GeneratedRuntimeConfigBaseline.current.hpp` and declares 28 macro-backed
source-owned tables. Canonical table values and order are extracted through
`parse_source_owned_baseline_contract`; the final current table is
`kLt1LowMagnitudeTable`. Direct literal-body replacement is not the current
production path.

## Historical Evidence Retained

These files remain in place as historical evidence only:

- `fixtures/source_owned_table_replacement_generator_contract.json`
- `fixtures/source_owned_table_replacement_input.example.json`
- `fixtures/generated_outputs/UltimateIdentityRuntimeTables.replacement.example.hpp`

They preserve the old 27-table input/output model and are not valid current
generator inputs. They must not be compared byte-for-byte with the active
macro-backed source and must not be interpreted as authority, a candidate, or
a hardware-valid artifact.

`tools/generate_source_owned_table_replacement.py` is retained only as a
fail-closed compatibility entry point. It exits nonzero before reading the
historical input, patching active source, or writing output, and directs
callers to the current supported contracts.

## Current Supported Offline Path

The authoritative current workflow is:

```text
approved source-authority intake
-> generator-input v2
-> current generator modes
-> complete 28-table artifact and manifest
-> separately gated preparation/install
-> active-source candidate
-> build
-> hardware gate
```

Current contract pointers:

- `generated_source_owned_generator_modes.md`
- `source_authority_intake_workflow.md`
- `tools/source_owned_generator_modes.py`
- `tools/manage_source_owned_source_authority_intake.py`
- current baseline extraction through `parse_source_owned_baseline_contract`

No production table ownership has been approved by this supersession cleanup.
Any future active table change still requires explicit source authority,
candidate isolation, build, and HARDWARE_PASS before merge. Runtime-loaded
config, persistent storage, WebSerial/device write, protobuf binary write, and
flashing automation remain unimplemented. Nunchuk remains `NOT_TESTED`; root
cause remains unproven.
