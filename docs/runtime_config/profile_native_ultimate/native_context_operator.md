# Native context and restoration operator

Offline preparation only; these commands do not grant device-write or hardware acceptance authority. Final source/artifact review and the exact approved device packet remain required. All `<...>` values below must come from that session's actual fresh observations. The legacy artifact CLI and its fixture-specific binding policy are unchanged.

`glyph_serial_config_tool.py --native-packet` accepts a compact format-v2 raw GET_CONFIG backup, exact raw SHA-256, one existing Ultimate row, the packet's preprocessing context and matching validated schema5 profile. It changes only that row's remaps/SOCD pairs. It preserves its current ID/engine; the checked reference operation follows the context write. The native body must contain the exact context digest. A native context with no remaps/SOCD is admitted without pretending it satisfies the historical Stage-A fixture policy.

Prepare a new immutable receipt and journal without opening a port:

```sh
python3 tools/glyph_serial_config_tool.py --native-packet \
  --expected-current-backup '<fresh-backup.json>' --expected-current-sha256 '<raw-config-sha256>' \
  --session '<approved-session-id>' --mode-index '<existing-Ultimate-row>' \
  --context-json 'docs/runtime_config/profile_native_ultimate/candidate_fixture_packet/forced_wins/context.json' \
  --native-profile-json 'docs/runtime_config/profile_native_ultimate/candidate_fixture_packet/forced_wins/profile.json' \
  --receipt-out '<new-dry-context-receipt.json>' --journal-out '<new-dry-context-journal.jsonl>'
```

Execution additionally requires `--execute --exclusive-configurator-session --port '<approved-port>'` and new receipt/journal paths. It performs production STATUS admission, checks the exact fresh GET_CONFIG against the explicit backup, fsyncs the immutable request receipt and its directory, sends existing SET_CONFIG command4 exactly once, and verifies canonical GET_CONFIG readback. There is no atomic generation comparison in legacy SET_CONFIG; the owner-exclusive host session is necessary. A malformed/lost response or readback mismatch stops with no retry.

After the context write succeeds, use existing checked reference command10 with freshly observed Config CRC/store generation/incarnation/token:

```sh
python3 tools/glyph_profile_store_production_tool.py --port '<approved-port>' \
  --journal-out '<new-ref-journal.jsonl>' set-reference --profile-id '<owned-test-id>' \
  --mode-index '<existing-Ultimate-row>' --config-generation '<fresh-config-crc>' \
  --incarnation '<fresh-incarnation>' --store-generation '<fresh-store-generation>' \
  --token '<fresh-unused-token>' --request-out '<new-ref-receipt.json>'
```

The checked reference sets ID and expected engine in the durable Config; it does not apply preprocessing. The live Config can retain its older reference until reinitialization. Do not follow checked reference with a whole-Config write derived from pre-reinitialization live bytes: that could overwrite the durable reference. Follow the approved packet's manual reboot/reinitialization and capture a fresh backup before any subsequent Config edit.

Restoration uses the exact original raw backup and its SHA, plus a separately captured fresh current backup/SHA. It restores original user fields/references while preserving current firmware-owned transaction/root/migration receipt fields, as SET_CONFIG itself requires. It rejects another store incarnation. Prepare without opening a port:

```sh
python3 tools/glyph_serial_config_tool.py --native-packet \
  --expected-current-backup '<fresh-current-backup.json>' --expected-current-sha256 '<current-raw-sha256>' \
  --restore-original-backup '<original-backup.json>' --original-sha256 '<original-raw-sha256>' \
  --session '<approved-restoration-session-id>' \
  --receipt-out '<new-dry-restore-receipt.json>' --journal-out '<new-dry-restore-journal.jsonl>'
```

The same explicit execution flags and fresh custody paths apply only after device packet approval. Restore original Config/references, reinitialize, and verify ordinary behavior before deleting either disposable test ID. Cleanup uses existing command9, an explicit ID and fresh store/incarnation/token fences:

```sh
python3 tools/glyph_profile_store_production_tool.py --port '<approved-port>' \
  --journal-out '<new-delete-journal.jsonl>' delete --profile-id '<owned-test-id>' \
  --incarnation '<fresh-incarnation>' --store-generation '<fresh-store-generation>' \
  --token '<fresh-unused-token>' --request-out '<new-delete-receipt.json>'
```

Only two distinct disposable native test IDs are needed: update their own revisions across the thirteen complete offline packages, retaining the two-profile selection/latched-identity cases. Original IDs/payloads remain part of the exact backup/restoration comparison. Metadata such as high-water IDs, tokens, generations and retained revisions is monotonic and is not falsely called restored. Twenty-profile capacity remains an actual host LittleFS proof.

Offline checks cover positive and rejected native context preparation, forbidden row-field changes, invalid remap IDs/context mismatch, native empty context, restoration receipt preservation/incarnation refusal, stale backup, exclusive-session guard, receipt-before-one-send, lost acknowledgement/no retry, and checked reference/delete fences. All serial objects in these checks are mocks. The strict candidate tool's production refusal remains asserted.

The owner reports tentative Mk6, USB XInput/Switch, and a Gamecube adapter to Switch; adapter model and exact host details remain unknown. B0XXInputViewer reports physical inputs and cannot establish the full native output/backend report. Switch/Gamecube raw report observability remains unverified. Host output catalogs and backend assignment checks are not physical acceptance or timing/stack observations.
