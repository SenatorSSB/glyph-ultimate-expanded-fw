# NeoPixel Null SendReport Characterization

Status: H1 host characterization for GP-CONFIG-016 only. This is not a
firmware repair, controller symptom report, or hardware result.

## Source correspondence

At base `0da68bdab9bf0fed4ed595538bea9aba7d2f49f3`, the checker binds the
complete `HAL/pico/include/comms/NeoPixelBackend.hpp` blob and the
`config/glyph/common/src/config.cpp` caller blob by SHA-256 and verifies
anchors for `SetGameMode`, the speed read, the null guard, and `loop1`. The
host harness literal-includes the production header. It does not copy the
`SendReport` implementation. Small host doubles provide only the base class,
protobuf value types, FastLED calls, and Pico time functions required to
compile the production template.

`SendReport` evaluates `_config->speed` while calculating `deltaHue` before
checking `_config == nullptr`. The constructor initializes `_config` to null.
`SetGameMode` also clears the pointer for a missing mode/config, RGB index zero
or an out-of-range index, BREATHE/REACTIVE_SIMPLE animation, and the default
unsupported animation branch.

## Cases and results

The focused checker compiles with C++20 and UndefinedBehaviorSanitizer, then
runs each case in a separate process. Each null case must reach the call marker
and emit the sanitizer's null-member-access diagnostic from the production
header. Static and rainbow-shift controls must return from the same production
method and call the FastLED show double.

| Case | Sequence classification | Host result |
| --- | --- | --- |
| startup null | Source-supported initial member state; direct host call | UBSan reports null member access before the guard |
| no mode | Injected direct `SetGameMode(nullptr)` setup | UBSan reports null member access before the guard |
| no config | Injected mode with null config | UBSan reports null member access before the guard |
| RGB index zero | Injected mode/config value | UBSan reports null member access before the guard |
| RGB index out of range | Injected mode/config value | UBSan reports null member access before the guard |
| unsupported animation | Injected BREATHE setup cleared by `SetGameMode` | UBSan reports null member access before the guard |
| unknown animation enum | Injected unknown value reaches the `SetGameMode` default branch | UBSan reports null member access before the guard |
| valid static | Injected valid static config control | Method returns; show double called once |
| valid dynamic | Injected valid rainbow-shift config control | Method returns; show double called once |

`loop1` calls LED `SendReport` only when `led_backend` is non-null, and it
propagates a changed game mode only when `backends[0]` and its current mode are
non-null. The host cases establish source ordering and host sanitizer behavior;
they do not establish that any null setup reaches `SendReport` on a physical
controller. In particular, the direct no-mode, null-config, and malformed
index setups are injected characterization inputs.

## Validation and limits

Run `python3 tools/check_glyph_neopixel_null_sendreport_characterization.py`.
The checker also rejects modified fixture schema/base identity, promoted
physical claims, relabeling an injected case as source-supported, changed
production-source digests, and a copied `SendReport` body. It proves only the
compiled host inputs and exact bound source bytes.

Physical call reachability: UNKNOWN. Physical controller crash: NOT CLAIMED.
Default RGB policy and repair policy: NOT SELECTED. Hardware acceptance and
root cause: NOT ESTABLISHED. No firmware source or active runtime behavior was
changed.
