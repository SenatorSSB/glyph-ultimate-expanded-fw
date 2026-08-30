# Glyph declared non-selector configuration census

Status: current declared literal census only; it does not resolve PlatformIO,
the compiler, dependencies, runtime interpolation, or configuration effects.

The fixture records the finite source-declared inheritance order for
`glyph_mk6`, selected scalar values, ordered flag literals, and the one
non-path nanopb option. `${PIOENV}` and `${platformio.name}` remain unresolved
source tokens. Raw lines and source identities are retained for correspondence;
no macro, board, compiler, protocol, frequency, filesystem, or behavior meaning
is asserted.

Validation is offline and uses only Python standard-library parsing plus
tracked Git/source identity checks:

```bash
python3 tools/check_glyph_build_input_non_selector_configuration.py
```
