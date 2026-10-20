# Independent native packet host-tool review

**BOUNDED PASS: no concrete safety finding.** Exact commit `3b218857bd026eccc5fe7ca2c80195e0055a3684`, tree `28b4cd03d9e236aa9bf82fe3b946d922c95783aa`.

Read-only offline review of guarded production set-reference/delete, appended native Config context/restoration helper and focused checker. Exact Git archive at `/private/tmp/glyph-native-packet-tool-probe.CI9Q1q`; eleven supporting file hashes match exact Git objects. Requested/observed model and effort UNKNOWN; no runtime attestation. Candidate/canonical source, SDK and ports untouched.

The exact implementation contract names these tools/checker within the native M0-M7 chapter. No new transport command or generic debug/write/reboot bridge is authorized. Physical packet approval and exact HEP/hardware gates remain separate.

## Verification

| Check | Outcome |
| --- | --- |
| python3 tools/check_glyph_profile_store_production_tool.py | PASS, exit 0; mocks only |
| python3 tools/check_glyph_profile_store_candidate_tool.py | PASS, exit 0; mocks only |
| python3 independent_counterexamples.py | PASS, exit 0; mocks only |
| exact Git-object/archive byte comparison plus historical tool prefix comparison | PASS, exit 0 |

The independent harness has ten case groups: receipt/directory/journal sync failure before send; existing receipt preservation; bad candidate/recovery/incarnation/status; fresh backup mismatch; lost ack and mismatched/malformed readback after one send; wrong SHA; stale set-reference/delete fences; exact restoration whitelist; historical binding positive/negative behavior.

## Source-backed conclusions

- **existing command fences — PASS.** Existing ProfileStore command9 carries DELETE9 and SET_MODE_REFERENCE10. Explicit incarnation/store generation and positive unused nonexhausted uint64 token remain required; reference requires explicit mode/Config generation; no profile body for either. Evidence: `schema/haybox/config.proto:30,560-561`, `tools/glyph_profile_store_production_tool.py:35-46,80-101`.
- **fresh backup and context — PASS.** Exact raw SHA and current GET bytes, compact store/root/incarnation/row admission, one existing Ultimate row, validated schema5 and preprocessing digest. Only remap/SOCD arrays replaced; ID/engine preserved. Evidence: `tools/glyph_serial_config_tool.py:893-945,1000-1006`.
- **receipt before one send — PASS.** Exclusive receipt creation, file fsync, parent-directory fsync and journal-event fsync precede one mutation. Lost ack, malformed/mismatched readback or exceptions stop without retry. Evidence: `tools/glyph_serial_config_tool.py:1007-1019`, `tools/glyph_profile_store_production_tool.py:123-134`.
- **whole Config no CAS — EXPLICIT_LIMIT.** SET_CONFIG4 has no atomic generation fence; exclusive-configurator-session is an owner assertion, not a lock. PASS assumes actual approved exclusive session. Evidence: `tools/glyph_serial_config_tool.py:974-977,993-995`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:334-435`.
- **restoration whitelist — PASS.** Restores all original user fields/references and copies exactly seven current firmware-owned root/reference/migration receipt fields, matching firmware SET preservation. Another incarnation refuses. Store IDs/generations/revisions not falsely restored. Evidence: `tools/glyph_serial_config_tool.py:887-890,948-955`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:345-359,389-395`.
- **live versus durable ordering — PASS_WITH_ORDERING_LIMIT.** Checked reference saves durable candidate and engine while _config can remain old until reinitialize. GET_CONFIG reads durable raw; STATUS Config generation comes from _config. Neither proves native activation. Preserve context -> checked reference -> manual reboot/reinitialize -> fresh backup. Never derive follow-up SET from old in-memory/live state. DELETE checks live and durable references. Evidence: `HAL/pico/src/comms/ConfiguratorBackend.cpp:315-330,539,783-827`, `docs/runtime_config/profile_native_ultimate/native_context_operator.md:18-46`.
- **legacy and strict admission — PASS.** Candidate strict production refusal retained. Historical serial tool body before appended native helper byte-identical to parent; historical positive fixture accepted and native empty context still rejected by old binding policy. Evidence: `tools/glyph_profile_store_candidate_tool.py:195-211`, `tools/glyph_serial_config_tool.py:1-882`.

## Limits

- No physical port/device opened or commands sent; no Config/profile mutation, flash, reboot, firmware build, SDK edit, canonical repository edit/publication or hardware acceptance.
- Final firmware source/IRQ/stack/ELF/P1 review is separately assigned and outside this finite host-tool probe.
- Exact local-object offline proof only; live GitHub truth was not requested or established.
- No aggregate PASS claimed; current host, port/controller/adapter and runtime model/effort unknown.
- Actually exclusive session, separate approved candidate device packet, backups, reinitialization ordering and exact HEP/hardware gates remain necessary.

One auxiliary contract-listing read used canonical checkout where candidate-only file was absent (FileNotFoundError); exact contract subsequently read from archive/Git. No mutation/device access; not a checker failure.

## Exact source hashes

| Path | SHA-256 |
| --- | --- |
| `tools/glyph_serial_config_tool.py` | `0b86d82415064023e9fad20ed6a2f526131a87eed16c055f4f7127fe8024ba8c` |
| `tools/glyph_profile_store_production_tool.py` | `4623bc6afd8a2480db80ff9debec0d79b386d891b12c1d2693cc0b844bb786ef` |
| `tools/check_glyph_profile_store_production_tool.py` | `bd01b023c92dab3796c8086959414ca06c82ae024a0cd157c06efd9d2ba1ba9d` |
| `tools/glyph_profile_store_candidate_tool.py` | `33475c736cfee7f6c0df0f0ee2e81b3b4befcb914a6ae9b342a008f1e3cc65e2` |
| `tools/check_glyph_profile_store_candidate_tool.py` | `efb5d2e693d4b2ed7be36dcc9ce5279163842c77d5be410ca20b5182d792a1db` |
| `tools/convert_glyph_native_ultimate_profile.py` | `d6a84657308ee957172185de2393205cf849465416c2f7e250a91e27774d293f` |
| `schema/haybox/config.proto` | `1e65f3f62f8a7f220c480217722f0e96ad2d48f9c274b462e5494a68ef15edec` |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp` | `b36885a26bada2e1ea3d6983ac993f403c9e00dddae0b6ad933e27c879e9b1e1` |
| `HAL/pico/src/core/ProfileStore.cpp` | `03da4b0a7157abc3d4b5a09c8533f238e72358660c0b377d010b352fd803ac42` |
| `docs/runtime_config/profile_native_ultimate/implementation_contract.json` | `eedf88b87dcd3485831bc74ba617d3f9986ef0f871d8dbc532efeb5946d70ee2` |
| `docs/runtime_config/profile_native_ultimate/native_context_operator.md` | `aa82cfd39ef3fe83f106c50e8174b96d475179deb77bf0a02099d46b66db06c6` |

Structured evidence: `/private/tmp/glyph-native-packet-tool-independent-review.json`. Harness/results/sourcepins retained at `/private/tmp/glyph-native-packet-tool-probe.CI9Q1q`.
