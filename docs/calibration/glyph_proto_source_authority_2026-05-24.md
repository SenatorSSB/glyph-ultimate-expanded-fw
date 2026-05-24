# Glyph Proto Source Authority Trace - 2026-05-24

## Scope

This trace records how the current Glyph firmware/configurator repo obtains the HayBox protobuf schema used to generate `config.pb.h`. It is source-trace documentation only. No dependency configuration was changed.

## Discovered Dependency And Source Paths

Tracked build configuration:

- `platformio.ini`
  - `custom_nanopb_protos` points to `.pio/libdeps/${PIOENV}/HayBox-proto/config.proto`.
  - Base `lib_deps` includes `nanopb/Nanopb@^0.4.8`.
  - Base `lib_deps` includes `https://github.com/JonnyHaystack/HayBox-proto#5b2bb5d`.
- `config/glyph/env.ini`
  - `[glyph_base]` extends `arduino_pico_base`.
  - `lib_ignore` includes `https://github.com/JonnyHaystack/HayBox-proto`.
  - Glyph `lib_deps` includes `https://github.com/GregTurbo/HayBox-proto#db4e2f6`.

Local dependency/build cache observed in this workspace:

- `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
- `.pio/libdeps/glyph_mk6/HayBox-proto/config.options`
- `.pio/libdeps/glyph_mk6/HayBox-proto@src-777dd83f5e06d71aba0103adf11d16aa/config.proto`
- `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
- `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.c`

Local cache git revisions observed:

- `.pio/libdeps/glyph_mk6/HayBox-proto`: `db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8`
- `.pio/libdeps/glyph_mk6/HayBox-proto@src-777dd83f5e06d71aba0103adf11d16aa`: `5b2bb5d2c2a212647d5aaef7d5dc794be5197ecb`

No repo-tracked `.gitmodules` file was found by `find . -maxdepth 3 -name .gitmodules -print`.

## Is `config.proto` Tracked In This Repo?

No repo-tracked `config.proto` was found outside `.pio` cache paths. The active schema file used by the observed local `glyph_mk6` build appears to be dependency-provided under `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`.

This means the canonical schema source is not committed as a first-party source file in this repo.

## Is The Dependency Version Explicit?

Partly yes.

- Base `platformio.ini` explicitly names `JonnyHaystack/HayBox-proto#5b2bb5d`.
- Glyph-specific `config/glyph/env.ini` explicitly names `GregTurbo/HayBox-proto#db4e2f6`.
- `custom_nanopb_protos` is generic by env path: `.pio/libdeps/${PIOENV}/HayBox-proto/config.proto`.

For `glyph_mk6`, the Glyph env override is the strongest tracked evidence: `config/glyph/env.ini` ignores the base JonnyHaystack dependency and adds `GregTurbo/HayBox-proto#db4e2f6`. The local `.pio/libdeps/glyph_mk6/HayBox-proto` cache resolves to the full `db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8` commit.

Nanopb itself is semver-ranged in base `platformio.ini` as `nanopb/Nanopb@^0.4.8`, so that dependency is not a single exact version pin in the tracked config.

## Files That Include Or Depend On Generated `config.pb.h`

Tracked source files include `config.pb.h` broadly across core, modes, HAL, and Glyph config code. Notable files for this branch:

- `include/core/state.hpp`
- `include/core/InputMode.hpp`
- `include/core/ControllerMode.hpp`
- `include/core/config_utils.hpp`
- `include/core/mode_selection.hpp`
- `include/core/socd.hpp`
- `src/core/InputMode.cpp`
- `src/core/mode_selection.cpp`
- `src/modes/CustomControllerMode.cpp`
- `include/modes/CustomControllerMode.hpp`
- `src/modes/Ultimate.cpp`
- `config/glyph/common/include/glyph_overrides.hpp`
- `config/glyph/common/src/config.cpp`
- `HAL/pico/include/util/state_util.hpp`
- `HAL/pico/include/config_defaults.hpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `HAL/pico/src/core/Persistence.cpp`

Generated local artifact:

- `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`

The generated header reflects local build output and is useful for current struct names, counts, and integer widths. It is not a repo-tracked schema authority and should not be edited.

## Authority Classification

For current `glyph_mk6` behavior in this workspace:

- `config.proto` canonical source: dependency-pinned through `config/glyph/env.ini`, locally present only in `.pio` cache.
- Repo-tracked schema source: not found.
- Generated header source path: visible locally under `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`.
- Submodule reference: not found.
- Uncertainty: PlatformIO dependency resolution can recreate `.pio` cache. If a future environment resolves differently or the env override changes, generated schema output can differ even though firmware source files are unchanged.

## Risk Assessment For Future Firmware Behavior Edits

Runtime firmware changes that depend on protobuf fields or generated struct layout would be risky until schema authority is made explicit and reviewable:

- The active Glyph schema is not tracked as a first-party source file in this repo.
- Generated `config.pb.h` is a build artifact and should not be treated as source.
- The base and Glyph envs reference two different HayBox-proto repositories/commits, with Glyph overriding the base dependency.
- Nanopb is range-pinned, not exact-pinned, in base config.
- Schema and options cache files can be absent in a clean checkout before dependency installation/build.

## Recommendation Before Runtime Changes

Before implementing custom Ultimate `TILT`/`Tilt2` runtime behavior or adding schema-backed storage changes:

1. Pin and document the intended Glyph HayBox-proto source authority explicitly.
2. Record the full commit SHA used for the active Glyph env, not only the short ref.
3. Decide whether the repo should vendor/reference the exact schema and options in a reviewed source-authority document or a locked dependency manifest.
4. Regenerate `config.pb.h` only through the build system, never by hand.
5. Treat `.pio` cache evidence as local build evidence, not as a durable source contract.

