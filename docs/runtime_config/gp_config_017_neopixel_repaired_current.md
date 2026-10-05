# GP-CONFIG-017 current NeoPixel ordering proof

The candidate moves the existing null guard before the first RGB speed read in
`HAL/pico/include/comms/NeoPixelBackend.hpp`. Time acquisition, difference
calculation and `prevTime` assignment remain before the guard. The existing
blank, brightness-zero, show and return actions remain unchanged. Every
nonnull static and dynamic path retains its original bytes.

The separate current harness includes the production header, Mk6 pixel mapping
and RGB starter locations literally. It observes 76 pixels and 36 target buttons
using the unchanged generated button identities and RGB host schema. Synthetic
FastLED packing records hue changes; it does not model target color conversion.

Both time representations exercise the seven null categories and two valid
categories. Dynamic controls cover SHIFT and XWAVE separately over four updates
with nonzero hue changes. Full traces of static and both dynamic modes must
match the immutable original header. A null-null-valid sequence also verifies
that the earlier null updates preserve time bookkeeping. Source, harness,
schema and omitted-branch substitutions must fail.

The original GP-CONFIG-016 fixture, checker, harness and stubs remain unchanged.
GP-VAL-035 owns separate authenticated historical replay and current aggregate
selection. Host proof does not establish physical null reachability, a physical
crash, target FastLED colors, hardware acceptance, Nunchuk or root cause.

Run `python3 -B tools/check_glyph_gp_config_017_neopixel_repaired_current.py`.
The exact candidate/base/tree and complete path inventory are recorded after
commit and independent conformance review. Firmware build and source integration
wait for GP-VAL-035 DONE; physical acceptance then applies to the exact built
artifact.
