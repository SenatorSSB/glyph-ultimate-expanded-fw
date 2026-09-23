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
