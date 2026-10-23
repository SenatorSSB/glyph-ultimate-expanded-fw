# KAZUYA_PROFILE_DESIGN_HANDOFF

- Schema: `profiles/schema/glyph-native-ultimate-profile.v1.schema.json`.
- Documentation: `profiles/README.md`.
- Validate: `python3 tools/glyph_native_profile_json.py validate SOURCE.profile.json`.
- Compile: `python3 tools/glyph_native_profile_json.py compile SOURCE.profile.json --output /tmp/Profile.pb`.
- Compile report: `python3 tools/glyph_native_profile_json.py report SOURCE.profile.json` (optional `--output /tmp/Profile.report.json`).
- Limits: 28 physical table slots; 1..28 declared tables; 32 table rules; 96 conditions; 768 condition tokens, with at most2 `all`,4 `any`,9 `none` per condition; 1..8 direction sources; 32 digital bindings; 16 analogue effects; 3336 native body bytes.
- Sparse tables: profile-defined names map to explicit unique slots0..27. Declare all9 raw `[x,y]` points, including ordinary stored direction5. Every undeclared slot compiles to exactly `[128,128] × 9` and cannot be referenced. References use declared names; `any` is reserved for winner filters.
- Mode: one existing native gate, optional in use; set required `gates.mode` to `"false"` when unused. Table effects retain named `normalTable`/`modeTable`; RF8 has no intrinsic Mode meaning.
- Provenance: use `{"kind":"authoredSourceV1"}`. Compiler derives SHA256 of `b"Glyph.Native.Authoring.v1\0"` plus canonical semantic JSON: sorted keys, compact separators, UTF8, no ASCII escaping/newline, arrays preserved; exclude root `provenance`, `metadata`, `name`. Symbolic semantic names and slot assignments are included. Human JSON remains source-of-truth; binary alone cannot recover v1 names/declaration intent.
