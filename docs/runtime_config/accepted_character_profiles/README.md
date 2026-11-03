# Accepted character profiles — Kazuya v5

The canonical [Kazuya source](../../../profiles/kazuya/Kazuya.profile.json) is
the exact reviewed v5 source at
`profiles/kazuya/v5/KazuyaV5.profile.json`: Git blob
`64c2825605082701b9252832149535c82ebb7fc5`. Its required native identities are
wrapper `72c1d401f65c1884ca5bd37f6114727a196fddd8082298c9c95dd39d4ecfae87`,
body `30bd0b711e3973527e1d48b59af08aa5c71b6ef8f2dc5b9d932932420d9c0f6f`,
production protobuf JSON
`54821170ddf4916f310e254c09a06f78d6ece8e8304f030761c3d03d5c6a8828`, and
preprocessing `3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f`.

The owner reports that KazTest5 at ProfileStore ID53 is
**DEVICE_CREATED_AND_READBACK_VERIFIED** and **GAMEPLAY_ACCEPTED**. Local private
installation/readback receipts are unavailable in this checkout, so this chapter
records those two statuses as owner-reported rather than recreating receipts.
The source identities and native-host validation are independently reproducible.

[Accepted identity](ACCEPTED_KAZUYA.json) is the current authority. The accepted
v4 KazTest4/ID51 identity remains an immutable gameplay-accepted historical
milestone and rollback reference; it is not a failed profile. V1-v4 sources and
the archival Ultimate/Pikachu source remain byte-preserved. The historical
accepted-profile aggregate's interrupted execution remains incomplete and is not
relabeled PASS.

The [fresh v5 independent review](INDEPENDENT_REVIEW.json) is APPROVED; the
[v4 review](INDEPENDENT_REVIEW_V4_HISTORICAL.json) remains preserved history.

Run the source-only verification:

```sh
python3 tools/glyph_native_profile_json.py validate profiles/kazuya/Kazuya.profile.json
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/Kazuya.profile.json --output /tmp/Kazuya.accepted.pb
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/Kazuya.profile.json --format protobuf-json --output /tmp/Kazuya.accepted.protobuf.json
python3 tools/check_glyph_accepted_character_profiles.py --report /tmp/Kazuya.accepted.validation.json
```

The verifier replays immutable v1-v4 snapshots, runs authoring 17/23, and runs
the canonical v5 profile through the current native C++ evaluator. This promotion
does not modify firmware, the native evaluator, controller state, generated
payloads, or runtime configuration.
