# GP-CONFIG-023 hardware protocol

Protocol version: `GP_CONFIG_023_HW_V1`

Status: `HARDWARE_TEST_REQUIRED`. Every physical row is `NOT_TESTED`. The exact candidate has a successful host build and preserved artifact; neither proves controller acceptance. The owner performs any device or Config action manually through an already established route. No executor or reviewer writes to a device.

## Exact handoff identity

- Candidate branch: `codex/gp-config-023-release-safety`
- Candidate Git SHA: `36bf0f314afe19fc8fcbf4caf97b5bf5f83dac39`
- Candidate tree: `45fa24dc7f95a5cd0e796c2c7c3b46f91688b329`
- Sole parent: `03bbf5da14a7d450f2986b12ad69ec6b3f704bad`
- Candidate base Configurator SHA: `b224227a76cb8edb73e5f4b2ad5de874d1e61ad1`
- UF2 SHA-256: `7e8833e5a83d1656e51f9ca258de78e7808eda2a6f3da918759a1553575f1224`
- UF2 size: `803840` bytes
- Preserved locator: `local_backups/hardware-artifacts/36bf0f314afe19fc8fcbf4caf97b5bf5f83dac39/7e8833e5a83d1656e51f9ca258de78e7808eda2a6f3da918759a1553575f1224/firmware.uf2`
- Build output: `.pio/build/glyph_mk6/firmware.uf2`
- Build: PASS using the repository-approved `./scripts/build-glyph-mk6-quiet.sh` fallback; RAM `105784 / 262144` bytes; flash `389816 / 1568768` bytes.
- Build source: exact committed F above, clean tracked checkout, PlatformIO Core 6.1.19 and pinned project-local dependencies. The first-build transcript witness was invalidated because its cited thread/event coordinates did not corroborate the claimed sequence; the invalidation record is `local_backups/gp-config-023-handoff-36bf0f31/prebuild-session-witness.json` (SHA-256 `75867bec0b8d5f302c963b956a7ac6d155fc8487a5fb6d4d7aefbd92bc3a2c7a`) and is not build evidence. To close the exact build-input identity gap, a fresh build was run from F after saving `build-inputs-prebuild.json` (SHA-256 `a2974aa66edc77372438699f9913c114a9b68688d96c367a60bd2eb752fef32a`). That snapshot binds the full F SHA/tree, clean tracked checkout, all 31 pinned file hashes/sizes, all 10 symlink targets, and the unchanged preserved UF2 before compilation. The fresh build result is `reproduction-build-result.json` (SHA-256 `e447783e6cd83a6251ccdd5c1edb6f1cd5652ab8989133ac3e880969af2f347b`); its log SHA-256 is `41e4dd692cb2b0c00880515d8ea24909c02fd879d1b2b387724a30a2c5815cc7`. The exact F build passed, the post-build input and symlink audit still matched, and it produced the same UF2 SHA-256 `7e8833e5a83d1656e51f9ca258de78e7808eda2a6f3da918759a1553575f1224` and size `803840` bytes. The original build's individual pre-build hashes remain unavailable; the identical-byte reproduction establishes that the preserved artifact is produced from exact F and the recorded pinned inputs. Nanopb 0.4.9.2 was used. Generated `config.pb.c` SHA-256 `d7041bfaf221cc747c7f2dc3fa8586352a1b8dc363fbdcfca181774562941626`; `config.pb.h` SHA-256 `bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323`.
- Fresh exact-tip independent handoff/build review: required before canonical publication. The earlier candidate/build review predates the reproduced build and does not substitute for this review.

F is the exact committed candidate after the source-free GP-VAL-042 governance completion. Do not rebuild or substitute candidate or artifact bytes after review. Rehash the preserved candidate and rollback immediately before any owner update. The exact F artifact remains unmerged pending the Hardware Evidence Processor's review of all required physical evidence and an exact-candidate/artifact PASS with no gaps.

## Preconditions and safety

1. Before any firmware update, the owner confirms the established manual recovery route and identifies the controller, current firmware, host/adapter, selected profile, and current Config state. Preserve a complete fresh Config read using the owner's existing safe read method. Record the raw byte count and SHA-256. Do not change Config at this step.
2. Rehash the exact F UF2 and preserved rollback immediately before each manual firmware update. The rollback is the previously accepted GP-CONFIG-017 image: F `5994f1657e45e0883c6c75468a19be7e3b49a72c`, UF2 SHA-256 `e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5`, `796672` bytes, at `local_backups/hardware-artifacts/5994f1657e45e0883c6c75468a19be7e3b49a72c/e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5/firmware.uf2`.
3. Do not write a Config or prepare/store an invalid Config without separate explicit owner approval for the named payload and the established manual route. Preserve the complete original bytes so recovery can prove exact retention. Do not assume Configurator access during refusal.
4. Use only the owner's established manual firmware/recovery method. Do not erase all storage, inject faults, add a device writer, use flashing automation, or enter frozen historical hardware environments. Stop if recovery cannot be performed safely or any exact identity/hash differs.
5. Give the owner one manual action at a time and wait for the report. Record failures and anomalies as reported. Do not turn missing observations into PASS or N/A.

## Required physical evidence

For each row, record exact candidate F and UF2 SHA-256, controller/model, backend, host/adapter, Config/profile, stimulus, expected and actual observations, result (`PASS`, `FAIL`, `PARTIAL`, or `NOT_TESTED`), and anomalies. A safely reachable invalid-index scenario must use an already reviewed payload and existing manual route; do not invent a writer or malformed stimulus. Host tests do not replace these physical rows or a safely reachable physical subcase. An unavailable unsafe display-failure stimulus remains NOT_TESTED and cannot be represented as a physical PASS.

| Required ID | Observation |
| --- | --- |
| `valid_stored_startup` | With a valid stored Config, observe normal startup on GC, XInput, DInput, Switch, and Keyboard routes. Record each supported route and actual initialization result separately; do not infer an untested backend. |
| `ordinary_selection_profile_modifier` | Exercise the valid default selection, held-input startup, menu entry, watchdog recovery, ordinary selection, profile, and modifier behavior on existing configurations. Record each route and concrete expected/actual controls. Do not use unsupported hot replacement. |
| `reconnect_reboot` | Reconnect and reboot with valid stored state. Confirm normal startup and clean input release; record unchanged Config bytes where safely readable. |
| `external_invalid_index_rejection` | Only with a safely reachable, independently reviewed omitted/zero/out-of-range candidate and separate owner authorization for any Config write, verify rejection leaves the previously accepted operation and stored bytes unchanged. |
| `invalid_stored_refusal_gc_usb` | Only with a reviewed invalid stored Config and approved manual setup, verify refusal before gameplay on GC and USB. Confirm the refusal message appears when the display works. If display initialization fails, normal operation must still remain blocked; only test that branch through a safely reachable existing route, otherwise record that physical subcase as NOT_TESTED. Confirm the stored file remains byte-identical after recovery. |
| `invalid_stored_refusal_reboot` | Repeat the invalid stored Config refusal after an ordinary reboot. Record no normal gameplay or backend startup during refusal and prove file retention after recovery. |
| `manual_recovery` | Use the already established manual recovery route; report the exact recovery image and observed firmware identity. No new device writer or automated recovery. |
| `restoration` | Restore the owner's original Config through the separately approved existing manual route. Verify exact raw bytes immediately and after reboot, then confirm normal startup and clean release. |
| `rollback` | If recovery requires rollback, use the exact accepted GP-CONFIG-017 artifact above. Rehash immediately before use and record the observed firmware identity and final Config state. |
| `safe_stop_and_anomalies` | Record any route that was unavailable, unexpected result, refusal display, disconnect, stuck input, file mismatch, or recovery anomaly. Keep unsafe/unreachable stimuli `NOT_TESTED`; do not replace them with host PASS. |

## Acceptance gate

All required physical rows must be resolved by the owner and independently reviewed by the Hardware Evidence Processor against `docs/agent_framework/HARDWARE_EVIDENCE.md`. No merge is permitted until the processor accepts exact candidate `36bf0f314afe19fc8fcbf4caf97b5bf5f83dac39`, exact UF2 SHA-256 `7e8833e5a83d1656e51f9ca258de78e7808eda2a6f3da918759a1553575f1224`, all required rows, and an empty evidence-gap list. A successful build or host proof is not hardware acceptance.

Nunchuk remains `NOT_TESTED`; root cause remains unproven; public release remains human-owned.
