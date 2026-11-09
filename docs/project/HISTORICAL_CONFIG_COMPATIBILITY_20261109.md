# Historical Config retained-input compatibility

Owner authority: Senscope Goal FULLPKG-B2-HISTORICAL-CONFIG-COMPATIBILITY,
original attachment 8a821285-e7e7-4213-81b3-7af7e3cad191/goal-objective.md
SHA256 41102f48286d40a3081bc84623f48f18e1c3d669c3d054ec4a65389b76ca2e49.
Candidate-only software; no merge, accepted-source promotion or physical operation.

## Exact source proof

Supported family: exact precompact descriptor/options at
6b73a7c507f35c111745c6bdd341618b490cbdcd, schema introduced at
e086b72a4eaa2e8585a81375a0866ac05fe78d66. Transition
af69dd91e629db852f1d2371e8d8c2d6b624fc54 adds top-level202-210 and switches
the writer from config.bin to config-v2.bin in the same commit. Native extension
28cd6f91acec8a9b9dbcaa7e26ae66302dc8d66e and package extension
35a0b263eb1ebda78f2be5ade6a3578799f5459b are later, unsupported historical data.

The complete historical schema/options and regenerated nanopb0.4.9.2 descriptor
are retained in tools/fixtures/glyph_package_v1/historical_config/. Exact hashes:

| File | SHA256 |
|---|---|
| config.proto | 9a6e157b831d6152e2a9bf3e0582cd6dff2429270a24e808b30338e8b327f773 |
| config.options | 379a564b40819f9524f7ed5218ab66976c59bb034d05ad4cfcb55b66907a4566 |
| config.pb.h | ae093641e3cf592337dcf54880878225b1f509e545b5b1960b6d0f970f0755a3 |
| config.pb.c | 063092571a3cbb7cae5b0099bbd4e3c32f540ee7b3b4cfb4de6758102361948e |
| minimal.pb | 191856fe3a60529575e2305f839327d6186e909f35b2acfa52b794132b077de2 |
| minimal-config.bin | fc3d2b3c8651dd9ad4e1f3df04e96ef84ec1aed44ed02c05ec493794dd2473df |

Historical Persistence.cpp hash07589fff75f0663465bfa6b8bf5d268591934c785cc18956d06d209ddf40f23f;
header hash eb842dd491ccb8620e76a90d664e296824b84a6294927fc87b136916fc8070e8.
The RP2040 file wrapper is LE32 length + LE32 CRC32. Old SaveConfig uses pb_encode
with the generated descriptor. It has no explicit65536 writer ceiling; this
observer retains65536 as a conservative acceptance ceiling. No unknown fields
are emitted; the old decoder skipping unknown fields does not justify accepting
them as writer output. No secondary-backend encoder callback was installed by
the old normal writer; callback wire presence remains rejected.

Historical Config permits1-10,200,201; GameModeConfig permits1-8,200-203;
UltimateProfile permits1-7. The retained schema provides every nested field,
wire type, enumeration and bound. All other nested descriptors/options match
current source. Ordered fields, minimal varints, omitted scalar/string defaults,
one packed numeric field and bounded repeated submessages follow nanopb encoding.
Duplicate/nonminimal/unknown/future fields, invalid types/counts/nested messages,
callbacks and all compact/native/reference/package ownership fields reject.
Fields205/209 are fixed-length32-byte protobuf bytes (wire type2), not the
protobuf fixed32 scalar type (wire type5). Only embedded profile schema1/2/3 with complete existing structural/semantic
rules is valid. Current source validators retain the profile rules. The historical path also
rejects every BTN_UNSPECIFIED RGB target: the old Glyph adapter rejected even
zero-color no-op mappings, while the successor permits those for format0. That
later relaxation is excluded only from historical recognition. All later fields
remain forbidden. The historical observer initializes
current scratch at generated defaults and never publishes it. Nested new scalars
are zero and callbacks cleared, so old child sizing is identical; comparison
skips only post201 root fields, including always-encoded fixed-length byte fields205/209.
Independent old-descriptor roundtrip tests prove positive fixture representation.

## Authority and preservation

Current Config observation runs first. Only rejected exact /config.bin can use
the historical predicate, after independent current config-v2.bin canonical and
semantic validity. The predicate returns recognition only. It produces no Config
facts, selection, fallback, generation, managed marker, package sequence or receipt.
Normal LoadConfigChecked and current canonical validation are unchanged. All
remaining classifier phases run normally, including sticky uncertainty handling.
The original Config scratch/phase workspace is reused; no second Config is added.

Migration kind2 still hashes exact /ultimate-migration.src against its recorded
source digest and verifies receipt correspondence. Kind3 retains legacy-root
provenance. Historical config.bin recognition supplies neither and substitutes
nothing. Any other failing predicate retains its fence and actual diagnostic.

The280-byte G6/HW5 witness SHA804c2f86b78a70c5b25ce4eb5c8c301e8cd867d64a15dd023c9e75d98913363d
contains202-210 and row engine205. It is compact/reference-era transport evidence,
not a positive witness for this precompact path family. It remains unchanged and
is not used to construct a supposed physical config.bin.

**Historical witness != physical filesystem attestation.** Current physical bytes
remain unknown. Software fixtures prove only modeled exact source-supported
states. Future packet must test current untouched controller storage once.
