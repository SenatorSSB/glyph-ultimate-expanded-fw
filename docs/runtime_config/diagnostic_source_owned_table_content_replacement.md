# Diagnostic Source-Owned Table Content Replacement

Status label: HARDWARE-GATED DIAGNOSTIC / NOT MERGE-SAFE WITHOUT PASS.

This packet records a narrow firmware diagnostic for the question:

Can source-owned table-content replacement be safe when the current active
`RuntimeConfigView`, active state, `RuntimeTableView` array identity/path, and
resolver chain are unchanged?

## Diagnostic Scope

This branch changes only numeric `x`/`y` initializer contents inside the
existing source-owned `StickPoint` tables in
`src/modes/UltimateIdentityRuntimeTables.hpp`.

It does not change `src/modes/Ultimate.cpp`,
`src/modes/UltimateRuntimeConfigInterpreter.hpp`, `RuntimeConfigView` symbols,
active state selection, `RuntimeTableView` array identity, resolver chain, or
any generated active wrapper.

The active path remains:

```text
GetActiveRuntimeConfigState().active_view
-> kSourceOwnedCurrentBaselineRuntimeConfig
-> kSourceOwnedCurrentBaselineRuntimeTables
-> existing StickPoint table symbols
```

## Exact Table Change

The source-documented low-risk diagnostic point is the existing
`RT1+RF4` custom modifier center entry. The source comment records that
direction 5 is source-encoded center because table selection requires a
9-point table and the requested neutral behavior is unchanged.

Changed point:

| Table symbol | Point index | Old x | Old y | New x | New y | Expected scope |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `kRT1RF4CustomTable` | 4 | 128 | 128 | 129 | 128 | Existing `RT1+RF4` custom-table direction-5/center entry only. |

`active_behavior_changed` is `true` because this changes a compiled table value
that can be selected through the existing source path.
`hardware_test_required_before_merge` is `true`.

## Accepted Evidence

- Source-owned active-state preselection: `HARDWARE_PASS`.
- Parsed/candidate machinery present while source-owned active view remains
  published: `HARDWARE_PASS`.
- Parsed candidate.view published active: `HARDWARE_FAIL`.
- Source-owned-materialized candidate.view published active: `HARDWARE_FAIL`.
- Dedicated active storage published active: `HARDWARE_FAIL`.
- Generated source-owned baseline-equivalent `RuntimeConfigView` active:
  `HARDWARE_FAIL`.

## Guardrails

- `active_view_selection_changed`: `false`
- `runtime_config_view_replacement`: `false`
- `source_owned_table_content_replacement_wired`: `true`
- `candidate.view` active publication: not implemented
- runtime-loaded config: not implemented
- persistent storage: not implemented
- WebSerial/device write: not implemented
- backend/config.pb write path: not implemented
- flashing automation: not implemented
- root cause proven: `false`
- Nunchuk remains `NOT_TESTED`

## Non-Claims

This packet does not prove source-owned table-content replacement is safe. It
does not prove the low-level failure mechanism. It does not claim nunchuk
validation, runtime-loaded config, persistent storage, WebSerial/device write,
backend/config.pb write paths, or flashing automation.
