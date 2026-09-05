# Glyph declared build-input provenance inventory

Status: current declared-input inventory only; no dependency resolution or
reproducibility claim.

## Purpose

`docs/runtime_config/fixtures/build_input_provenance_inventory.json` is the
deterministic schema-v2 static inventory of declarations that select the canonical
`glyph_mk6` build boundary. It binds the tracked declaration bytes and records
the PlatformIO/environment, dependency, workflow runner/action, source
selection, source identity, local script, nested reusable-workflow caller, and
`glyph_nuker` selectors that are declared by the repository.

The inventory is intentionally observational. It does not fetch or install a
package, resolve an action or runner image, inspect `.pio` or another local
dependency cache, import workflow code, execute a discovered script, invoke
PlatformIO, execute `glyph_nuker`, build firmware, publish an artifact, or
access a controller.

The local entrypoint contract records the canonical `pio run -e glyph_mk6`
command, the fallback wrapper chain through `scripts/build-glyph-mk6-quiet.sh`
and `scripts/pio-local.sh`, the ordered interpreter alternatives, and the
`PLATFORMIO_CORE_DIR` declaration. It does not resolve which executable or
dependency environment is selected.

## Discovery boundary

The declaration-file set is discovered from tracked repository state:

- `platformio.ini`;
- `config/*/env.ini` and `config/*/meta.yaml`;
- every tracked top-level or nested `.github/workflows/*.yml` or `*.yaml`;
- the local `extra_scripts` target reached by `glyph_mk6`; and
- the tracked `glyph_nuker` postprocessor blob;
- `scripts/build-glyph-mk6-quiet.sh`, the documented fallback entrypoint; and
- `scripts/pio-local.sh`, the documented local interpreter selector.

The inherited canonical PlatformIO chain is `[env]` plus
`arduino_pico_base`, `glyph_base`, and `env:glyph_mk6`. AVR-only inputs such as
`HAL/avr/proto/config.options` are not reached by that chain and are therefore
outside this inventory. The nested device-config workflow and metadata are
included as declared inputs because the tracked Glyph caller reaches them;
their live caller/ownership remains unresolved external evidence.

Each declaration record binds its tracked Git mode and SHA-256. Each selector
record has a stable ID, declaration context, raw declared selector, finite
selector class, and resolution state. The checker requires deterministic
ordering, exact shapes, current tracked bytes, the separately executable mode
of `glyph_nuker`, and presence of every reviewed selector literal.

## Non-claims

Full Git commits and exact registry versions, when present, are only declared
exact selectors whose content was not fetched by this inventory. Abbreviated
commits, tags, compatible ranges, Python version lines, unversioned packages,
major action tags, `ubuntu-latest`, and the `configurator` reusable-workflow
ref remain movable or unresolved. Runtime expressions, source selections, and
the build-time source SHA resolve only during a run.

The exact unresolved-claim list is load-bearing in the fixture. In particular,
this inventory does not establish complete dependency/toolchain resolution,
package or action content identity, runner image identity, reproducible builds,
postprocessor purpose or byte transformation, artifact acceptance, immutable
artifact storage, or live ownership/invocation of `build-device-config`.

## Validation

Run:

```bash
python3 tools/check_glyph_build_input_provenance_inventory.py
```

The checker is a current load-bearing baseline entry in the runtime-config
validation manifest. Its adversarial cases fail closed on malformed schema,
unknown fields/classes/states, duplicate selector IDs, escaping paths,
unexpected executable declarations, symlink/untracked declaration shapes, and
non-integer schema versions. It performs no network or build operation.
