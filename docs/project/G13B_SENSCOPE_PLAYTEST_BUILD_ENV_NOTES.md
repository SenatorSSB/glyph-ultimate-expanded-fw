# G13b Senscope Playtest Build Environment Notes

Status: source-backed build-path notes for experimental playtest environment.

## Build Flag

- Name: `SENSCOPE_PROTOTYPE_ENABLE_MANUAL_SELECTION`
- Default value: `0` (disabled) when not explicitly defined.
- Header: `include/prototypes/senscope/SenscopePrototypeBuildFlags.hpp`
- Compile-visible gate consumed at: `src/core/mode_selection.cpp`

Gate interpretation:

- `0` means manual/debug `SenscopePrototype` selection remains disabled.
- Non-zero means manual/debug `SenscopePrototype` selection is compile-enabled.

## Experimental Environment

- Environment name: `glyph_mk6_senscope_playtest`
- Defined in: `config/glyph/env.ini`
- Explicit macro define:
  - `-D SENSCOPE_PROTOTYPE_ENABLE_MANUAL_SELECTION=1`
- Not default:
  - `platformio.ini` still has `default_envs = glyph_mk6`

## Build Commands

Exact direct command:

```bash
./scripts/pio-local.sh run -e glyph_mk6_senscope_playtest
```

Optional quiet wrapper command:

```bash
./scripts/build-glyph-mk6-senscope-playtest-quiet.sh
```

Both commands are build-only. They do not upload, flash, or copy artifacts to mounted devices.

## Source Files Changed For G13 Build Path

- `include/prototypes/senscope/SenscopePrototypeBuildFlags.hpp`
- `src/core/mode_selection.cpp`
- `config/glyph/env.ini`
- `scripts/build-glyph-mk6-senscope-playtest-quiet.sh`

No protobuf, default config activation, or mode-id wiring was added.

