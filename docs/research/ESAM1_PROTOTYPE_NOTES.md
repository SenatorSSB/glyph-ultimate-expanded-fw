# ESAM1 Prototype Notes

ESAM1 is an old custom firmware mode / behavioral reference, not a direct modern profile format.

Known takeaway:

- It is useful as evidence for desired controller behavior.
- It should not be directly ported as a modern Glyph profile.
- Any flipper-like behavior should be re-expressed as explicit safe transforms.

Behavioral themes to preserve as reference only:

- exact coordinate modifiers
- multiple modifier layers
- shifted neutral behavior
- C-stick rotation behavior
- D-pad layer behavior
- analog shield behavior

If the raw ESAM1 source files become available later, they should be stored under `docs/sources/raw/` and treated as reference artifacts only.

Raw reference copy:

- `docs/sources/raw/ESAM1.hpp`
- `docs/sources/raw/ESAM1.cpp`
