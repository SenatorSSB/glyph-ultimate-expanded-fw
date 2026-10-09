# GP-CONFIG-024 hardware result

Status: `HARDWARE_TEST_REQUIRED`; all physical rows are `NOT_TESTED`.

The exact C024 candidate `8ab1173b0690f5ed3e994f95af797c9e9a265525` (tree
`15ed2d35d561d6b1709499fe42083ca4d789e920`, base
`b404453ef22cc994eec54338b8a23c3ba61df808`) built successfully for
`glyph_mk6`. RAM use was 105784/262144 bytes; flash use was 389808/1568768
bytes. The 803840-byte UF2 SHA-256 is
`95de108f23b0d7219caa38a1f85c4dec1691f087061b29787d07b83dab0ba0e6`,
preserved at
`local_backups/hardware-artifacts/8ab1173b0690f5ed3e994f95af797c9e9a265525/95de108f23b0d7219caa38a1f85c4dec1691f087061b29787d07b83dab0ba0e6/firmware.uf2`.
The custody tool confirmed existing bytes and passed a pre-handoff rehash.
Fresh independent source/build/artifact review approved the exact candidate
and artifact. These are build and custody results, not controller acceptance.

No physical action was run. The owner has not provided a current raw Config
hash, safe-to-distinguish existing profile pair, or confirmed manual update
and restoration route. No Config write, device write, or flash action was
performed. The protocol remains gated on those setup facts and owner direction.

| Evidence row | Result |
| --- | --- |
| Valid startup | `NOT_TESTED` |
| Duplicate/empty profile selection and row identity | `NOT_TESTED` |
| Keyboard on DInput | `NOT_TESTED / DEFERRED_POST_FIRST_PUBLIC_BETA` (nonblocking; outside the current first-beta physical scope) |
| Reconnect and reboot | `NOT_TESTED` |
| Restoration and rollback | `NOT_TESTED` |
| Safe stop and anomalies | `NOT_TESTED` |

Nunchuk remains `NOT_TESTED`; root cause remains `UNPROVEN`; no hardware PASS
or public release is claimed.

The Keyboard DInput deferral preserves raw Keyboard semantics. It authorizes
no behavior removal, disabling, or output transformation and requests no
Keyboard physical work now.
