# Generated Source-Owned Runtime Realization Design

Status label: DESIGN / DOCS-TOOLS ONLY.

This packet records the next safe realization strategy after candidate-backed
and RAM-backed active `RuntimeConfigView` publication failed hardware testing.
It is documentation and checker scaffolding only. It does not change active
firmware behavior.

## Accepted Evidence

- Source-owned active-state preselection has a recorded `HARDWARE_PASS` in the
  source-owned preselection result lineage. The source-owned active view
  remains published, and the active-state indirection is safe enough to use as
  the repair-architecture basis for this scope.
- Parsed/candidate machinery can be present while the published active view
  remains source-owned. The parsed-candidate-present/source-owned-published
  diagnostic recorded `HARDWARE_PASS` while forcing active publication to
  `kSourceOwnedCurrentBaselineRuntimeConfig`.
- Candidate-backed active `RuntimeConfigView` publication is unsafe. The parsed
  candidate active diagnostic recorded `HARDWARE_FAIL`, and candidate.view must
  not become active.
- Source-owned-materialized candidate.view active publication is unsafe.
- Dedicated active storage published active is unsafe under the
  `diagnostic_active_storage_published` diagnostic. The active-storage
  `HARDWARE_FAIL` evidence is recorded in
  `docs/runtime_config/diagnostic_active_storage_published_hardware_failure_2026-06-28.md`.
- RAM-backed active runtime table storage appears unsafe as an active
  publication target under the current diagnostics, even when source-owned
  equivalent, validated, equivalence-checked, parser-free, and not
  candidate-owned.
- The low-level failure mechanism remains unproven.
- Nunchuk remains `NOT_TESTED`; this design makes no nunchuk validation claim.

## Design Target

A future generator may take a neutral/profile/config representation and produce
generated C++ source-owned immutable runtime tables. Firmware would build those
generated tables into the binary, and active `RuntimeConfigView` would point to
source-owned generated tables rather than RAM-backed materialized storage.

The active view model is therefore:

```text
neutral/profile/config input
-> offline generator
-> generated C++ source-owned immutable runtime tables
-> firmware build artifact
-> active RuntimeConfigView points at source-owned generated tables
```

The key property is that active runtime table pointers remain source-owned at
publication time. The generated tables are firmware source artifacts, not
runtime-loaded payloads, not persistent storage, and not a device-write result.

## Required Properties

- Active view remains source-owned.
- Generated runtime tables are immutable/source-owned firmware source.
- No parser payload path is introduced.
- No runtime-loaded config is introduced.
- No persistent storage is introduced.
- No WebSerial/device write path is introduced.
- No backend/config.pb write path is introduced.
- No flashing automation is introduced.
- No `candidate.view` active publication is introduced.
- No RAM-backed active table publication is introduced.
- No nunchuk validation is claimed.
- Hardware test is not required before merge for this docs/checker-only branch
  because active behavior is unchanged.

## Future Implementation Gate

This branch is not an approval to implement generated table selection or active
source switching. Future implementation must be hardware-gated if active source
selection behavior changes.

Any future firmware branch that selects generated source-owned tables as the
active source must provide source-backed generated artifacts, build evidence,
and a hardware plan/result before merge. It must still reject parser payload
activation, runtime-loaded config, persistent storage, WebSerial/device write,
backend/config.pb write paths, firmware flashing automation, candidate.view
active publication, and RAM-backed active table publication unless a later
source-backed and hardware-validated model proves otherwise.

## Non-Claims

- This packet does not prove the low-level failure mechanism.
- This packet does not implement a generator.
- This packet does not add or wire generated C++ tables.
- This packet does not implement runtime-loaded config, storage, WebSerial
  device write, backend/config.pb write, or flashing automation.
- This packet does not claim official configurator compatibility.
- This packet does not claim nunchuk validation.
