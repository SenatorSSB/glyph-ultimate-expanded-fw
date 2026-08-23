# Prepared v2 C++ preview

`tools/render_source_owned_cpp_preview.py` renders a complete schema-version-1
prepared packet from `tools/source_owned_generator_modes.py` as deterministic,
inactive C++ review text. It reads table symbols, ordered nine-point
coordinates, ownership rows, provenance, and semantic digests already present
in the packet; it infers no mapping, ownership, profile intent, replacement
value, or game semantics.

The renderer revalidates the prepared packet digest, current baseline identity,
artifact shape, canonical table order, manifest rows/counts/digests, explicit
ownership, provenance, and production gate. Synthetic packets require the
explicit `--test-mode` flag. Normal output is stdout; `--output` is restricted
to an absolute isolated temporary/offline path. It rejects repository source,
active-publication-like, and symlinked-parent targets; only the operating
system's canonical temporary-directory aliases are allowed.

The output is labeled inactive review material and is never installed, wired
into `RuntimeConfigView`, treated as production authority, used to prepare a
firmware candidate, built, flashed, or hardware-accepted. The current source-
owned baseline and all runtime/device-write non-claims remain unchanged.

```bash
python3 tools/render_source_owned_cpp_preview.py PACKET.json
python3 tools/render_source_owned_cpp_preview.py PACKET.json --test-mode --output /private/tmp/glyph-preview.hpp
python3 tools/check_glyph_source_owned_cpp_preview.py
```
