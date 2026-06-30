# Source-Owned Table Replacement Design

Status label: DESIGN / DOCS-CHECKER ONLY.

This packet records the next safe realization strategy after generated
source-owned baseline-equivalent `RuntimeConfigView` active publication failed
hardware testing. It is documentation and checker scaffolding only. It does not
change firmware source or active firmware behavior.

## Accepted Evidence

- Source-owned active-state preselection `HARDWARE_PASS`: the active
  publication path remains source-owned and is the last known passing
  active-runtime boundary.
- Parsed/candidate machinery present with source-owned active view
  `HARDWARE_PASS`: parser/candidate machinery may exist while
  `kSourceOwnedCurrentBaselineRuntimeConfig` remains the published active view.
- Parsed candidate.view published active `HARDWARE_FAIL`.
- Source-owned-materialized candidate.view published active `HARDWARE_FAIL`.
- Dedicated active storage `HARDWARE_FAIL`: the
  `diagnostic_active_storage_published` result shows dedicated active storage
  published as active is unsafe under current diagnostics.
- Generated source-owned baseline active `HARDWARE_FAIL`: the
  `diagnostic_generated_source_owned_baseline_active` result shows generated
  source-owned baseline-equivalent active publication is unsafe under current
  diagnostics.
- RAM-backed active table storage is unsafe under current diagnostics.
- RuntimeConfigView/table-publication-path replacement is unsafe under current
  diagnostics, even with generated source-owned immutable baseline-equivalent
  data.
- The low-level failure mechanism remains unproven.
- Nunchuk remains `NOT_TESTED`.

## Design Target

A future generator should patch or regenerate the existing source-owned
`StickPoint` table definitions already consumed by
`kSourceOwnedCurrentBaselineRuntimeConfig` before firmware build.

The safe target model is:

```text
neutral/profile/config input
-> offline generator
-> replacement contents for existing source-owned StickPoint tables
-> firmware build artifact
-> existing kSourceOwnedCurrentBaselineRuntimeConfig symbol/path remains active
```

Source-owned table replacement does not change RuntimeConfigView selection.
The existing active `RuntimeConfigView` remains unchanged, the existing active
publication path remains unchanged, and the existing `RuntimeTableView` array
identity/shape remains unchanged unless a later source-backed diagnostic is
explicitly hardware-gated before merge.

Customization is realized only by replacing the compile-time contents of the
existing source-owned `StickPoint` tables before firmware build. This branch
does not introduce a new `RuntimeConfigView`, new active state, new active
wrapper, runtime-loaded config, RAM publication, or alternate active view
selection.

## Required Properties

- `active_view_selection_changed: false`
- `runtime_config_view_replacement_allowed: false`
- `source_owned_table_content_replacement_allowed: design-only`
- `candidate_view_published_active: false`
- `ram_backed_active_table_publication_allowed: false`
- `generated_source_owned_baseline_active_publication_allowed: false`
- `runtime_loaded_config_implemented: false`
- `persistent_storage_implemented: false`
- `webserial_device_write_implemented: false`
- `backend_config_pb_write_path_implemented: false`
- `flashing_automation_implemented: false`
- `nunchuk_status: NOT_TESTED`
- `root_cause_proven: false`

## Future Implementation Gate

This packet is not approval to implement generated table-content replacement.
Future implementation changing table contents must be hardware-gated before
merge if active behavior changes.

Any future implementation must preserve the existing active
`RuntimeConfigView` symbol and selection path unless a separate
source-backed, hardware-gated diagnostic proves that a narrower change is safe.
It must not publish `candidate.view`, RAM-backed active storage, dedicated
active storage, generated baseline-active replacement views, runtime-loaded
payloads, persistent storage, WebSerial/device write, backend/config.pb write
paths, or flashing automation under current evidence.

## Non-Claims

- This packet does not prove the low-level failure mechanism.
- This packet does not modify firmware source.
- This packet does not implement a generator.
- This packet does not replace any table contents.
- This packet does not implement runtime-loaded config, persistent storage,
  WebSerial/device write, backend/config.pb write, or flashing automation.
- This packet does not claim official configurator compatibility.
- This packet does not claim nunchuk validation.
