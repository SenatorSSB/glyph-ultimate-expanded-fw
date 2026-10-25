# Accepted Kazuya v4 gameplay baseline

The canonical [Kazuya.profile.json](Kazuya.profile.json) is the exact owner-accepted
v4 source: **HOST_VERIFIED**, **DEVICE_CREATED_AND_READBACK_VERIFIED** and
**GAMEPLAY_ACCEPTED (owner-reported)** for stored ID51/revision1/nameKazTest4.
Its source bytes, compiled wrapper/body, preprocessing and authored provenance
are unchanged from accepted commit5e30341ee06761e20e864ccc013ca6658e42b5ca.

[Accepted identity and correspondence](../../docs/runtime_config/accepted_character_profiles/ACCEPTED_KAZUYA.json)
and [chapter evidence/operation packet](../../docs/runtime_config/accepted_character_profiles/README.md)
record exact source→binary→ID51 readback→gameplay linkage. The human source name
KazTest4 remains intentionally exact. A future metadata-only store rename to
Kazuya preserves stableID51 and payload; the firmware's existing RENAME operation
also preserves payload revision. No controller rename/cleanup is performed here.

Validate/compile/report using the unchanged authoring compiler:

```sh
python3 tools/glyph_native_profile_json.py validate profiles/kazuya/Kazuya.profile.json
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/Kazuya.profile.json --output /tmp/Kazuya.accepted.pb
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/Kazuya.profile.json --format protobuf-json --output /tmp/Kazuya.accepted.protobuf.json
python3 tools/glyph_native_profile_json.py report profiles/kazuya/Kazuya.profile.json --output /tmp/Kazuya.accepted.report.json
python3 tools/check_glyph_accepted_character_profiles.py --report /tmp/Kazuya.accepted.validation.json
```

## History and test entrypoints

The old root v1 source and README are byte-preserved under [v1/](v1/README.md).
[V2](v2/README.md), [v3](v3/README.md) and [v4](v4/README.md) are immutable historical
candidate/evidence chapters; their original status text describes their publication
time, not the accepted current baseline. All old tests/manifests/results remain
unchanged. They pinned the former root source and README, so run them via the
accepted-character snapshot verifier above, which replays immutable5e source,
checks current production/harness correspondence, then runs its native v4 suite
against this canonical source. Do not rewrite frozen historical pins to match
this later source promotion. Direct old test commands require the historical checkout.

## Remaining scope

V4 remains the rollback/reference for future experiments. Crouch Jab loop design
is deferred; no additional loop, timers, history or macros are implemented.
Unapproved Kazuya optimizations/sublayers and functionality outside the owner report
remain unaccepted. Nunchuk remains NOT_TESTED. Glyph describes deterministic raw
outputs; game command history and timing are not inferred from host tests.
