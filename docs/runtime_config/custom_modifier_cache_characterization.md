# GP-CONFIG-011 custom-modifier cache characterization

This H1 packet records an exact-production host sanitizer characterization of
the current `CustomControllerMode` modifier-mask cache. The production class
declares `_modifier_button_masks[10]`, while the build-resolved
`CustomModeConfig.modifiers` schema permits 20 entries. The harness exercises
constructor mask writes and processing reads separately at counts 0, 10, 11,
and 20.

The packet is characterization only. It does not select a cache or schema
repair, change modifier semantics, claim physical reachability, claim device
or firmware behavior, establish hardware acceptance, or prove root cause.
Any repair requires a separate H2/H3 work order, source authority, build, and
exact-snapshot hardware gate.

Run `python3 tools/check_glyph_custom_modifier_cache_characterization.py` to
compile the exact production bodies against the local build-resolved generated
schema and execute the eight isolated cases under AddressSanitizer and
UndefinedBehaviorSanitizer.
