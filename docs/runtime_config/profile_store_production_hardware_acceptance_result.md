# ProfileStore production hardware acceptance — 2026-10-18

Result: **`MULTI_PROFILE_STORE_PRODUCTION_HARDWARE_ACCEPTANCE_PASS`**.
The clean production path is **`MULTI_PROFILE_STORE_PRODUCTION_INTEGRATION_READY`**.
This records only the exact tested firmware candidate, not this documentation
descendant and not a chapter-wide strict-DONE claim.

- Firmware: `af69dd91e629db852f1d2371e8d8c2d6b624fc54`, tree
  `5c3ae998b94e444f7ab890ac51fcce8492944ceb`, base
  `6b73a7c507f35c111745c6bdd341618b490cbdcd`.
- Preserved UF2: 970752 bytes, SHA-256
  `5813756392a669b952982af9468ab3dbb34440bb98e3103ff76fd7faff743c35`.
- Host acceptance tooling: `066149f0f36eea93f9243989101934ad13862df5`.
- Evidence: `/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-tests/multi-profile-store-strict-hardening-20261016/responses/production-acceptance-af69dd91-20261018T000806Z`.

The pre-flash normal-boot read-only gate passed; the sealed UF2 was rehashed
and installed once. Post-flash ordinary read-only verification passed. One
unreferenced CREATE (token `0xf000000000001d01`, request SHA-256
`05e34f0036cb6d05849a268df787507f0d054f7d908ce6de9d570c8358b70b72`)
allocated stable ID24/revision1 at generation167. One UPDATE (token
`0xf000000000001d02`, request SHA-256
`489fb92321d7fa6ad71aef686b52e07eebd04adab95bc5cffcb3275f57b5bf73`)
returned ID24/revision2 at generation168. After the single planned ordinary
reboot, incarnation1/generation168/high-water `0xf000000000001d02` and the
updated ID24 payload were verified. CREATE and UPDATE transfers were 3117/46
and 3090/46 request/response bytes respectively; this is not maximum-frame
coverage.

All pre-existing profiles retained their witnessed stable IDs, metadata,
revisions and normalized payloads. Config remained byte-identical: 252 bytes,
SHA-256 `cbff16ff67c0b0301d188267255322a5abf4453f207858cc716646726dc46dd0`,
with mode1 -> ID3 and mode2 -> ID4. No recovery, uncertainty, unresolved
receipt, or armed/pending fault was observed.

`SHA256SUMS-final` has content SHA-256
`b5421e04477f5b93024628342e2b758fd79b4259d6e215a19d5028fb02e9445e`.
Its self-entry is stale and therefore fails if the manifest is asked to hash
itself; the other 339 recorded entries validate. This custody-format defect is
preserved as a limitation of the evidence manifest, not silently repaired and
not a contradiction of the recorded transaction/configuration witnesses.

## Remaining boundaries

RT2 remains **DEFERRED BY OWNER** and its underlying cause **UNRESOLVED**.
Automatic recovery failure-entry safety, factory recovery, uncontrolled power
cut, reserve refusal, selection-chord physical evidence, Runtime-B observer,
and Nunchuk remain their existing NOT_TESTED dispositions. Production runtime
stack/heap peaks remain NOT_MEASURED. Universal no-brick behavior, blanket
transport reliability, exhaustive interruption safety, whole-program stability,
and public-release readiness are not established. Ordinary UF2 installation
does not prove filesystem erasure; ROM BOOTSEL remains a separately observed
fallback.

The exact-candidate hardware gates in B9 and B10 are satisfied. Their retained
power/reserve evidence debts are nonblocking under the current owner scope.
This does not reopen RT2 or make the whole chapter strict DONE.
