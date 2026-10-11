# Vendored HayBox schema

`config.proto` and `config.options` were copied from the original checkout's
PlatformIO dependency cache at
`.pio/libdeps/glyph_mk6/HayBox-proto`, pinned at upstream commit
`db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8`.

The files retain the upstream schema semantics and contain only the additive
Stage-A Ultimate profile fields required by this repository. PlatformIO's
Nanopb generation reads this tracked pair rather than the dependency cache.
