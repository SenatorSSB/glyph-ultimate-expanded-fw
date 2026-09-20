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
compile the exact production bodies against the tracked byte-identical schema
fixture and execute the eight isolated cases under AddressSanitizer and
UndefinedBehaviorSanitizer. Python 3, Git, and a C++17 compiler with
address/undefined/bounds sanitizer support are required; a firmware build,
PlatformIO, network access, and `.pio` state are not required.

GP-VAL-026 closes only the host-check dependency path. Its
[fixture provenance](../../tools/fixtures/custom_modifier_cache_host/schema/README.md)
binds the exact GregTurbo protocol and Nanopb revisions, original bytes,
generated header, source selector and licenses. The original GP-CONFIG-011
fixture, production source, harness and 0/10/11/20 observations are unchanged.
The checker remains current and load-bearing. Expected sanitizer failures at
11/20 remain characterization successes, not a firmware repair or acceptance.

The checker also runs disposable negative controls for missing, altered,
untracked and symlinked dependencies, wrong source identities, coordinated
schema/provenance replacement, changed selector and production-source drift.
No negative control writes to the source checkout. The runtime validation
manifest declares this complete tracked dependency closure, so
`python3 tools/run_glyph_runtime_config_validation.py --category configurator --json`
can execute it in its existing clean isolated snapshot. GP-VAL-011 is unchanged;
configurator-category success is not a claim that every aggregate category
passes in every developer checkout.
