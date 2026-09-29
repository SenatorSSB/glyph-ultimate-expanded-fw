# GP-CONFIG-010 mode-activation capacity

This integration candidate repairs the source-proven mismatch between the
Glyph default configuration's 13 mode entries and the prior 10-entry
activation-mask cache. The cache is a named fixed 30-entry array, with a
compile-time equality proof against the generated `Config.game_mode_configs`
extent and a fit proof for the current 13-entry default. Setup and selection
return before indexing when a count exceeds 30.

The exact-production host harness runs under AddressSanitizer and Undefined
BehaviorSanitizer for counts 0, 10, 11, 13, 30, and 31, plus each valid default
selection index 0 through 12. It is characterization of the committed
integration source; it makes no controller, display, cross-core, persistence,
Nunchuk, or root-cause claim. Physical acceptance remains required for this H3
candidate.

The current clean-checkout checker uses the tracked GP-VAL-028 Nanopb 0.4.9.2
generated header at `tools/fixtures/mode_selection_host/generated/config.pb.h`.
It verifies the exact `bdd72a22…` SHA-256, 73,915-byte size, generator banner,
30-entry `Config.game_mode_configs` extent, source proto/options, upstream
generator and package metadata, license, and declared selectors. The separate
handwritten host compile double must have the same extent but cannot satisfy
the generated-header proof. The earlier original candidate used a distinct
`532f7ac3…` generated-header digest from the 0.4.9.1 host closure; this
current fixture does not establish the package used for the historical tested
GP-CONFIG-010 firmware artifact. Its package identity remains UNKNOWN. No
firmware input or active source changed for GP-VAL-028.
