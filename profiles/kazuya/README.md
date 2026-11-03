# Kazuya v5 canonical gameplay baseline

`Kazuya.profile.json` is byte-identical to
[`v5/KazuyaV5.profile.json`](v5/KazuyaV5.profile.json), the reviewed gameplay-
accepted v5 source. Its Git blob is `64c2825605082701b9252832149535c82ebb7fc5`.
The compiled wrapper/body/protobuf JSON identities are respectively
`72c1d401f65c1884ca5bd37f6114727a196fddd8082298c9c95dd39d4ecfae87`,
`30bd0b711e3973527e1d48b59af08aa5c71b6ef8f2dc5b9d932932420d9c0f6f`, and
`54821170ddf4916f310e254c09a06f78d6ece8e8304f030761c3d03d5c6a8828`.

The owner reports installed **KazTest5**, ProfileStore **ID53**, as readback
verified and gameplay accepted. Private controller receipts are not available in
this checkout; no controller operation occurred as part of canonical promotion.

## Historical sources

[v1](v1/README.md), [v2](v2/README.md), [v3](v3/README.md), and
[v4](v4/README.md) are preserved immutable historical sources/evidence. In
particular v4/KazTest4 (historical ID51) remains a gameplay-accepted rollback
reference, not an invalid profile. The Ultimate/Pikachu archival source is also
preserved. Do not change historical hashes or replay their root-pinned tests
against the new canonical file; use the accepted-profile snapshot verifier.

## Reproduction

```sh
python3 tools/glyph_native_profile_json.py validate profiles/kazuya/Kazuya.profile.json
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/Kazuya.profile.json --output /tmp/KazuyaV5.pb
python3 tools/test_kazuya_profile_v5.py -v
python3 tools/check_glyph_accepted_character_profiles.py --report /tmp/KazuyaV5.accepted.json
```

The promotion leaves firmware, native evaluator behavior, SOCD configuration,
runtime configuration, device records and generated tracked payloads unchanged.
Nunchuk remains NOT_TESTED; no new gameplay semantics are claimed beyond the
owner's acceptance report.
