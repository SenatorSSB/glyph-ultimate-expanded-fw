# GP-CONFIG-012 Button Decoder and Mask Characterization

Status label: CURRENT.

This H1 host characterization executes the accepted Nanopb 0.4.9.2 decoder
closure against the checked-in generated Config C/header and exact extracted
production function bodies. It also asserts the current source inventory,
Pico `-fshort-enums` ABI, decoder descriptor width, upstream closure hashes,
license hash, and GP-PROV-014 provenance. The compatible PlatformIO selector
is not treated as a permanent version pin. The fixture and checker are at
`fixtures/gp_config012_button_mask_characterization.json` and
`../../tools/check_glyph_gp_config012_button_mask_characterization.py`.

## Observed Host Matrix

| Input | Exact decoder observation | Source category |
| --- | --- | --- |
| `BTN_UNSPECIFIED` 0 through named buttons 1..60 | Accepted; generated storage preserves the corresponding raw byte | Schema-supported; 1..60 also includes named Button values |
| 61..65, 127, 255 | Accepted; one-byte generated storage preserves the raw byte | Injected wire values, outside named Button enumerators |
| 256, 300, -1 | Rejected by this exact decoder/vector combination | Injected wire values |
| Four packed or mixed packed/unpacked repeated values | Accepted, count 4 | Valid encoding control |
| Five activation buttons; four modifier buttons | Rejected at fixed-array extent | Over-capacity injected controls; modifiers stay within the separate GP-CONFIG-014 count boundary |
| Truncated and overlong varints | Rejected | Malformed encoding controls |
| Empty Config | Accepted | Negative control only; not a claim about a producer transaction |

The five default activation bindings are source-backed by
`config/glyph/common/include/glyph_overrides.hpp`: `BTN_RF3`, `BTN_RF2`,
`BTN_LT1`, `BTN_LT2`, and `BTN_RT2` (one button in each binding). The default
source is inventory checked; the host decoder payload matrix does not claim to
replay the complete default initialization path.

## Enum Read and Mask Callers

With the exact host compiler's `-fshort-enums` ABI, `sizeof(Button)`, generated
repeated-element storage, and Nanopb descriptor element width are all 1 byte.
The isolated enum-read sanitizer had no diagnostic for raw 61..63, and reported
an invalid Button enum read for 64, 65, 127, and 255. This is a host ABI/sanitizer
observation, not a Pico device result.

The exact production helper computes `1ULL << (button - 1)`. In an isolated
shift-sanitizer process, 0, 65, and 255 diagnosed an invalid shift; `-1` was
narrowed to 255 in the harness and diagnosed the same way. Values 61..64 remain
within the tested 64-bit shift range and produced masks `1ULL << 60` through
`1ULL << 63`. The compiled source fragments exercised all four production
callers: CustomControllerMode modifier, CustomControllerMode button combo,
mode activation binding, and backend activation binding. Raw 61..64 reached all
four. Raw 0 also reached each caller and diagnosed the invalid shift. Named
`BTN_LF1` (1) caller controls completed.

The source inventory also checks the Configurator `HandleSetConfig` and
Persistence `LoadConfig` decode paths, the default config definition, and the
existing menu setup anchor. Those source-path checks are not a replay of the
Configurator transaction or a LittleFS persistence transaction. No physical
input reachability or stored arbitrary payload occurrence is established.

## Limits and Validation

These results apply to the exact hashes recorded in the fixture and the
observed 0.4.9.2 decoder closure only. The tests use manually encoded host
vectors and literal extracted production function bodies. They do not establish
what the currently compatible package range resolves to in a future build,
physical controller behavior, whether an invalid value can be physically
produced or persisted, the cause of any user symptom, or a policy for handling
invalid bindings. Physical behavior and root cause remain UNKNOWN/unproven;
Nunchuk remains NOT_TESTED. No firmware, ABI, schema, persistence, device, or
policy change is made.

Run:

```bash
python3 tools/check_glyph_gp_config012_button_mask_characterization.py
```
