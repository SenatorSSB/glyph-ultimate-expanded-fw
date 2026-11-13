# Source-backed v2 READ admission and route correction

Built source9e69188d857138a3884bcbe243f22188815e9355 is unchanged. All cited
firmware/protocol source bytes equal the source candidate3cc98ae4. This is a
host correction only; the original metadata discrepancy's cause is unresolved.

## READ payload and directory metadata are distinct observations

- `HAL/pico/src/core/ProfileStore.cpp:1276–1336` validates standalone record
  framing/CRC, incarnation, requested ID/revision, decoding and profile semantics.
  Supported payload schemas are legacy1,2,3 and native5.
- `:1339–1350` READ uses the directory's current revision. It does not require
  directory payload_version to equal the decoded legacy schema.
- `:1379–1382` activation checks **native versus legacy family** equivalence,
  with native recovery exclusion; it does not compare legacy version numbers.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp:1074–1077` LIST copies directory
  metadata without inspecting payload bodies. `:870–873`, `:1145–1152` and
  `:1190–1207` return the decoded profile and serialize its actual schema.
- `src/core/config_validation.cpp:123–153` and the existing host finite legacy
  validator validate supported profile shape. The existing native wrapper/body
  validator checks schema5/encoding1/ABI1 and finite native sections.

`executor.validate_read` therefore accepts only:

```python
(directory_version in (1, 2, 3) and payload_schema in (1, 2, 3)) or (
    directory_version == payload_schema == 5
)
```

This follows validation of raw field9 wire, supported schemas, parsed/raw schema
consistency, legacy finite semantics or native header/body, requested ID/current
revision, token/protocol/OK response, generation and diagnostic/recovery guards.
Native53 additionally requires exact nameKazTest5/revision1/schema5 and wrapper
SHA72c1d401f65c1884ca5bd37f6114727a196fddd8082298c9c95dd39d4ecfae87.
Unsupported metadata/payload versions and cross-family disagreement stop. No ID4
exception, skip flag, blanket mismatch acceptance or controller record repair exists.

Each snapshot records `directory_payload_version` and `payload_schema_version`
separately. The post-snapshot compares raw wrapper bytes, exact directory entry
bytes and both facts independently. It never relabels payload schema from metadata.
Raw response and field9 wrapper remain separate from decoded/reconstructed JSON.

## Historical regression provenance

HISTORICAL_REVERIFICATION.json binds the October25 decoded read-4.json and
list-0.json and the v1 sealed decoded response. Pinned-schema deterministic
serialization of the historical decoded profile yields3047bytes, SHA
b8583459651f42bfbb108e4558627ce0a192be89bae229cbb5a74fb0e7dcd8d4, byte-equal
to the current captured raw field9. The historical directory value is1 while the
payload schema is3, both revision1. **Historical bytes are reconstructed from
JSON, not an original raw historical wire capture.** No historical authority,
cause, gameplay or physical acceptance is promoted by this regression.

## Normal Configurator menu route: exact saved-state claim

The owner's normal route is Connect to.Configurator in the menu. Its action sets
watchdog scratch0 (`DefaultConfigMenu.cpp:149–156`); boot consumes it and changes
**RAM** default_usb_backend_config (`backend_init.cpp:313–335`). The normal
Configurator destination explicitly skips the Save action (`:137–147`); saving
is only at the Save branch (`:202`). GET_CONFIG reads persisted raw bytes
(`ConfiguratorBackend.cpp:321–335`), and ConfigGeneration reports persisted state
while ignoring its Config argument (`Persistence.cpp:260–262`).

V2 therefore permits that normal menu route, or the already supported heldRT2
alternative without the scratch override. No Profile/USB/default setting or
reference operation is allowed. It verifies saved Config bytes/generation/default
destinations, not unchanged RAM. Unexpected route, recovery or saved-byte drift
stops. This clarification introduces no host request, persistent write or new
firmware capability.
