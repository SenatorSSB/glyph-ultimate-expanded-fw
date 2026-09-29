# GP-VAL-028 current capacity header

This is a host-only generated fixture for the current GP-CONFIG-010 capacity
checker. `config.pb.h` is the exact 73,915-byte output of Nanopb 0.4.9.2
(tag `0.4.9.2`, commit `160d4f09e5fabb2b66aa2dea32d4f38ace2c4b3f`)
for the tracked GP-VAL-026 `config.proto` and `config.options` bytes. Its SHA-256
is `bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323`.
The independent host compile double in `../include/config.pb.h` has the same
30-entry extent but does not serve as generated-source evidence.

The exact upstream generator blob is
`096d5c3b96b8a2712b087fc91e9cf74c2cd989ab` (SHA-256
`67d3c5e6de1e5dbd9f45bb4e5b7055d888d1afd6d6e1690791ab8607b6c6b738`).
Scratch regeneration used Python with protobuf 6.33.6 and grpcio-tools 1.80.0:

```text
python -B <nanopb-0.4.9.2>/generator/nanopb_generator.py \
  --output-dir <temporary-output> --error-on-unmatched \
  --proto-path <temporary-proto-directory> config.proto
```

The tracked `nanopb.library.json` is the upstream 0.4.9.2 host package
metadata, whose version field is `0.4.92`; `LICENSE.nanopb.txt` retains its
license notice. `provenance.json` records exact inputs and hashes. Normal
validation checks those bytes and the current declared selectors without
regenerating or downloading. `nanopb/Nanopb@^0.4.8` is a movable range, not a
permanent resolved-version pin. This correspondence does not identify the
Nanopb package used for the historical GP-CONFIG-010 tested firmware artifact.
The earlier GP-VAL-026 0.4.9.1 fixture and GP-CONFIG-010 completion evidence
remain separate.
